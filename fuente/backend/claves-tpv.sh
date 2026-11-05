#!/bin/bash
# ---------------------------------------------------------------------------
#  Mete las claves del TPV de Cecabank en Supabase y enciende el carrito.
#
#  Las claves NO se guardan en ningún archivo del proyecto, NO se suben a
#  GitHub y la clave de cifrado no se ve al escribirla. Van directas a los
#  secretos de Supabase y el archivo temporal se borra al terminar.
#
#  Uso:  cd ~/Desktop/"Web ABAY" && bash src/backend/claves-tpv.sh
# ---------------------------------------------------------------------------
set -uo pipefail

REF="gqwacqkyvecuojkfgxiq"
WEB="/Users/yeraylongueira/Desktop/Web ABAY"
API="https://$REF.supabase.co/functions/v1"

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
mal()  { printf '  \033[31m✗\033[0m %s\n' "$1"; }
tit()  { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

cd "$WEB/src/backend" || { mal "no encuentro $WEB/src/backend"; exit 1; }

tit "Claves del TPV de Cecabank"
echo "  Están en el correo o el panel que te dio el banco."
echo "  La clave de cifrado no se verá mientras la escribes: es normal."
echo
read -r  -p "  MerchantID  : " MID
read -r  -p "  AcquirerBIN : " BIN
read -r  -p "  TerminalID  : " TID
read -rs -p "  Clave de cifrado : " CLAVE; echo
read -r  -p "  Entorno [pruebas/produccion] (pruebas): " ENT
ENT="${ENT:-pruebas}"

if [ -z "$MID" ] || [ -z "$BIN" ] || [ -z "$TID" ] || [ -z "$CLAVE" ]; then
  mal "falta algún dato; no he cambiado nada"
  exit 1
fi
if [ "$ENT" != "pruebas" ] && [ "$ENT" != "produccion" ]; then
  mal "el entorno tiene que ser 'pruebas' o 'produccion'"
  exit 1
fi

tit "Guardando en Supabase"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ENVF="$TMP/env"
(
  umask 077
  {
    echo "CECA_MERCHANT_ID=$MID"
    echo "CECA_ACQUIRER_BIN=$BIN"
    echo "CECA_TERMINAL_ID=$TID"
    echo "CECA_CLAVE=$CLAVE"
    echo "CECA_ENTORNO=$ENT"
    echo "WEB_URL=https://abayperformance.com"
  } > "$ENVF"
)
unset MID BIN TID CLAVE

if ! supabase secrets set --env-file "$ENVF" --yes >/dev/null 2>&1; then
  mal "Supabase no ha aceptado los secretos. ¿Estás dentro? Prueba: supabase login"
  rm -f "$ENVF"
  exit 1
fi
rm -f "$ENVF"
ok "claves guardadas (entorno: $ENT)"

tit "Prueba: un pedido de mentira"
RES=$(curl -s -X POST "$API/crear-pedido" \
  -H 'content-type: application/json' \
  -H 'origin: https://abayperformance.com' \
  -d '{"lineas":[{"producto":"camiseta-negra","talla":"M","unidades":1}],
       "cliente":{"nombre":"Prueba montaje","email":"prueba@abay.es","telefono":"624852324"},
       "entrega":"recogida","metodo":"tarjeta","acepta":true}')

if printf '%s' "$RES" | grep -q '"campos"'; then
  ok "el servidor firma el pago correctamente"
  printf '%s' "$RES" | grep -o '"action":"[^"]*"' | head -1 | sed 's/^/     /'
else
  mal "el servidor ha contestado esto:"
  printf '     %s\n' "$RES"
  echo
  echo "  Repasa las claves y vuelve a lanzar este script. La web sigue"
  echo "  pidiendo por WhatsApp, así que no hay nada roto de cara al público."
  exit 1
fi

tit "Encendiendo el carrito en la web"
node -e '
const fs=require("fs");
const p=process.argv[1], api=process.argv[2];
let s=fs.readFileSync(p,"utf8");
const re=/var TIENDA = \{ api: "[^"]*" \};/;
if(!re.test(s)){ console.error("no encuentro la línea de TIENDA"); process.exit(1); }
fs.writeFileSync(p, s.replace(re, `var TIENDA = { api: "${api}" };`));
' "$WEB/src/index.template.html" "$API" || { mal "no he podido tocar la plantilla"; exit 1; }
ok "plantilla actualizada"

cd "$WEB" || exit 1
python3 src/build.py >/dev/null && ok "web reconstruida" || { mal "falló build.py"; exit 1; }
cp -R sitio/. repo/
cp -R src/. repo/fuente/
ok "archivos copiados al repositorio"

cd "$WEB/repo" || exit 1
git add -A
git commit -q -m "Enciende el carrito: pagos con el TPV de Cecabank" || true
echo
read -r -p "¿Publico la web ahora? [s/N] " SUBIR
if [ "$SUBIR" = "s" ] || [ "$SUBIR" = "S" ]; then
  git push origin HEAD && ok "publicada; en 1-2 minutos estará viva"
else
  echo "  Sin publicar. Cuando quieras:  cd ~/Desktop/\"Web ABAY\"/repo && git push origin HEAD"
fi

tit "Lo último: la consola de Cecabank"
cat <<FIN
  Entra en la consola del TPV y configura:

  1. Comunicación on-line  →  SÍ
     URL:  $API/aviso-pago
  2. Respuesta requerida   →  SÍ
  3. Email de respaldo     →  abay@abay.es
  4. Bizum                 →  pide que lo activen a tpv@cecabank.es

  Tarjetas de prueba y resto de detalles: src/backend/README.md
FIN
echo
