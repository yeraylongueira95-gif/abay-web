#!/usr/bin/env bash
# =====================================================================
#  Monta la tienda de ABAY: base de datos, funciones y publicación.
#
#  Uso:  bash "src/backend/montar.sh"      (desde la carpeta Web ABAY)
#
#  Las claves del TPV se piden aquí, se mandan directamente a Supabase
#  y no se guardan en ningún archivo ni se ven en pantalla.
# =====================================================================
set -euo pipefail

AZUL=$'\033[1;36m'; VERDE=$'\033[1;32m'; ROJO=$'\033[1;31m'; GRIS=$'\033[0;90m'; FIN=$'\033[0m'
titulo(){ printf '\n%s== %s ==%s\n' "$AZUL" "$1" "$FIN"; }
ok(){ printf '%s  ✓ %s%s\n' "$VERDE" "$1" "$FIN"; }
err(){ printf '%s  ✗ %s%s\n' "$ROJO" "$1" "$FIN"; }
nota(){ printf '%s    %s%s\n' "$GRIS" "$1" "$FIN"; }

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUPA="$RAIZ/src/backend/supabase"
cd "$RAIZ"

# ---------------------------------------------------------------- 0
titulo "Comprobaciones"
for p in node git; do
  command -v "$p" >/dev/null || { err "falta $p"; exit 1; }
done
if ! command -v supabase >/dev/null; then
  nota "instalando la herramienta de Supabase…"
  npm install -g supabase >/dev/null
fi
ok "supabase $(supabase --version | head -1)"
[ -f "$SUPA/config.toml" ] || { err "no encuentro $SUPA/config.toml"; exit 1; }
ok "código del servidor encontrado"

# ---------------------------------------------------------------- 1
titulo "1. Entrar en Supabase"
if supabase projects list >/dev/null 2>&1; then
  ok "ya estabas dentro"
else
  nota "se abrirá el navegador: entra con tu cuenta y acepta"
  supabase login
fi

# ---------------------------------------------------------------- 2
titulo "2. Elegir el proyecto"
supabase projects list || true
echo
read -r -p "Pega el REFERENCE ID del proyecto para la tienda (o escribe NUEVO): " REF

if [ "$REF" = "NUEVO" ] || [ "$REF" = "nuevo" ]; then
  supabase orgs list
  read -r -p "ID de la organización: " ORG
  nota "te pedirá una contraseña para la base de datos: invéntala larga y guárdala"
  nota "en tu gestor de contraseñas; te la volverá a pedir al crear las tablas"
  supabase projects create "ABAY tienda" --org-id "$ORG" --region eu-west-3
  echo
  supabase projects list
  read -r -p "Pega ahora el REFERENCE ID del proyecto recién creado: " REF
fi

[ -n "$REF" ] || { err "sin proyecto no se puede seguir"; exit 1; }

cd "$SUPA"
supabase link --project-ref "$REF" --yes
ok "proyecto enlazado: $REF"

# ---------------------------------------------------------------- 3
titulo "3. Crear las tablas"
if supabase db push --remote --yes; then
  ok "tablas creadas"
else
  err "no se han podido crear desde aquí"
  nota "abre https://supabase.com/dashboard/project/$REF/sql/new"
  nota "y pega el contenido de:"
  nota "$SUPA/migrations/20261105120000_tienda.sql"
  read -r -p "Pulsa Enter cuando lo hayas hecho… " _
fi

# ---------------------------------------------------------------- 4
titulo "4. Claves del TPV de Cecabank"
nota "no se ven al escribirlas y no se guardan en el ordenador"
read -r  -p "  MerchantID (9 caracteres) : " MID
read -r  -p "  AcquirerBIN (10)          : " BIN
read -r  -p "  TerminalID (8)            : " TID
read -rs -p "  Clave de cifrado          : " CLAVE; echo
read -r  -p "  ¿Entorno? [pruebas/produccion] (pruebas): " ENT
ENT="${ENT:-pruebas}"
read -r  -p "  Email para avisos de pedido (Enter para saltar): " MAILAVISO
read -rs -p "  Clave de Resend si quieres emails (Enter para saltar): " RESEND; echo

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ENVF="$TMP/secretos.env"
umask 077
{
  echo "CECA_MERCHANT_ID=$MID"
  echo "CECA_ACQUIRER_BIN=$BIN"
  echo "CECA_TERMINAL_ID=$TID"
  echo "CECA_CLAVE=$CLAVE"
  echo "CECA_ENTORNO=$ENT"
  echo "WEB_URL=https://abayperformance.com"
  [ -n "$RESEND" ] && echo "RESEND_API_KEY=$RESEND"
  [ -n "$MAILAVISO" ] && echo "EMAIL_AVISOS=$MAILAVISO"
  [ -n "$MAILAVISO" ] && echo "EMAIL_REMITE=pedidos@abayperformance.com"
} > "$ENVF"
supabase secrets set --env-file "$ENVF" --yes
rm -f "$ENVF"
unset CLAVE RESEND
ok "claves guardadas en Supabase (y borradas de este ordenador)"

# ---------------------------------------------------------------- 5
titulo "5. Publicar las funciones"
supabase functions deploy crear-pedido
supabase functions deploy aviso-pago
API="https://$REF.supabase.co/functions/v1"
ok "funciones publicadas"

# ---------------------------------------------------------------- 6
titulo "6. Comprobar que responden"
if curl -fsS "$API/crear-pedido" | head -c 120; then
  echo; ok "el catálogo responde"
else
  err "el catálogo no responde: revisa el paso 3"
fi

# ---------------------------------------------------------------- 7
titulo "7. Encender el carrito en la web"
cd "$RAIZ"
node -e '
const fs=require("fs"); const p="src/index.template.html";
let s=fs.readFileSync(p,"utf8");
const api=process.argv[1];
const re=/var TIENDA = \{ api: "[^"]*" \};/;
if(!re.test(s)){ console.error("no encuentro la línea de TIENDA"); process.exit(1); }
fs.writeFileSync(p, s.replace(re, `var TIENDA = { api: "${api}" };`));
' "$API"
python3 src/build.py
cp -R sitio/. repo/
cp -R src/. repo/fuente/
ok "web reconstruida con el carrito encendido"

cd "$RAIZ/repo"
git add -A
git commit -q -m "Enciende el carrito: pagos con el TPV de Cecabank" || true
echo
read -r -p "¿Publico la web ahora? [s/N] " SUBIR
if [ "$SUBIR" = "s" ] || [ "$SUBIR" = "S" ]; then
  git push origin HEAD
  ok "publicada en abayperformance.com"
else
  nota "sin publicar. Cuando quieras: cd repo && git push origin HEAD"
fi

# ---------------------------------------------------------------- 8
titulo "Lo último, en la consola de Cecabank"
cat <<FIN

  Entra en https://comercios.ceca.es/pruebas (o la de producción) y:

  1. Comunicación on-line  ->  activar, con esta URL:

         $API/aviso-pago

  2. Respuesta requerida   ->  SÍ
  3. Comunicación on-line por email -> activar también (red de seguridad)
  4. Si no ves Bizum en la pantalla de pago, pídelo a tpv@cecabank.es

  Y prueba una compra con estas tarjetas del entorno de pruebas
  (caducidad: diciembre de este año, CVV2 989):

         5540500001000004     5020470001370055
         5020080001000006     4507670001000009

  Para abrir el envío a domicilio, en el SQL Editor de Supabase:

         update tienda_ajuste set valor = '495' where clave = 'envio_cent';

FIN
