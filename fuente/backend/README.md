# Tienda de ABAY — carrito y cobro con el TPV de Cecabank

La web es estática (GitHub Pages). El cobro **no puede** salir de ahí: la clave de
cifrado del TPV firma los importes, y si viajara en el JavaScript cualquiera
podría pagar 1 € por una camiseta. Por eso hay dos funciones de servidor en
Supabase que son las que calculan el precio y firman.

```
Navegador                Supabase                     Cecabank
---------                --------                     --------
carrito  ── POST ──▶ crear-pedido
                     (precio y stock de la BBDD,
                      firma SHA-256)
         ◀── formulario firmado ──┘
   │
   └── POST ───────────────────────────────────────▶ pantalla de pago
                                                      (tarjeta o Bizum)
                     aviso-pago ◀── aviso on-line ───┘
                     (comprueba firma, descuenta
                      stock, marca PAGADO)
                     ── $*$OKY$*$ ──────────────────▶
   ◀── vuelve a /pedido/gracias/ ──────────────────────┘
```

El pedido solo se da por bueno con el **aviso on-line**, nunca con la vuelta del
cliente a la web: la URL_OK solo se llama si el cliente pulsa ACEPTAR.

## Qué hay aquí

| Archivo | Para qué |
|---|---|
| `supabase/migrations/20261105120000_tienda.sql` | tablas, stock, función `confirmar_pedido` y datos de salida |
| `supabase/functions/_compartido/ceca.ts` | firmas SHA-256 del TPV (manual 8.21) |
| `supabase/functions/crear-pedido/index.ts` | valida el carrito, guarda el pedido y firma el formulario |
| `supabase/functions/aviso-pago/index.ts` | recibe el aviso de Cecabank y marca el pedido pagado |
| `prueba-firma.mjs` | comprueba el algoritmo contra el ejemplo del manual |

## Puesta en marcha

### 1. Base de datos

En el proyecto de Supabase → SQL Editor → pegar el contenido de
`supabase/migrations/20261105120000_tienda.sql` y ejecutar.

Las tablas quedan con RLS y **sin ninguna política**: solo las funciones del
servidor (service_role) pueden leerlas. Desde el navegador no se ve nada.

### 2. Secretos

En Supabase → Project Settings → Edge Functions → Secrets. **Estos valores se
meten ahí directamente, no se mandan por chat ni se escriben en ningún archivo.**

| Secreto | De dónde sale |
|---|---|
| `CECA_CLAVE` | consola del TPV: clave de cifrado (una para pruebas y otra para producción) |
| `CECA_MERCHANT_ID` | alta del TPV (9 caracteres) |
| `CECA_ACQUIRER_BIN` | alta del TPV (10 caracteres) |
| `CECA_TERMINAL_ID` | alta del TPV (8 caracteres) |
| `CECA_ENTORNO` | `pruebas` al principio, `produccion` cuando esté probado |
| `WEB_URL` | `https://abayperformance.com` |
| `RESEND_API_KEY` | opcional: para que llegue un email con cada pedido |
| `EMAIL_AVISOS` | opcional: a quién avisar (se pueden poner varios separados por coma) |
| `EMAIL_REMITE` | opcional: remitente verificado en Resend |

`SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` ya existen solas en las funciones.

### 3. Publicar las funciones

```
cd "src/backend/supabase"
supabase login
supabase link --project-ref TU_PROJECT_REF
supabase functions deploy crear-pedido
supabase functions deploy aviso-pago
```

Quedan en:
- `https://TU_PROJECT_REF.supabase.co/functions/v1/crear-pedido`
- `https://TU_PROJECT_REF.supabase.co/functions/v1/aviso-pago`

### 4. Configurar el TPV

En la consola de Cecabank (https://comercios.ceca.es/pruebas primero):

- **Comunicación on-line**: activarla y poner la URL de `aviso-pago`.
- **Respuesta requerida**: SÍ. Así, si nos quedamos sin stock, contestamos
  `$*$NOK$*$` y el cobro se anula solo en vez de tener que devolverlo a mano.
- **Comunicación on-line por email**: activarla también. Es la red de seguridad
  por si la función tarda más de 30 segundos.
- **Bizum**: si no aparece en la pantalla de pago, pedirlo a tpv@cecabank.es.

### 5. Decirle a la web dónde está el servidor

En `src/index.template.html`, dentro de `var TIENDA = {...}`, poner
`api: "https://TU_PROJECT_REF.supabase.co/functions/v1"`. Con eso aparece el
botón de carrito; mientras esté vacío, la web sigue pidiendo por WhatsApp.

Después: `python3 src/build.py` y publicar.

### 6. Probar

Entorno de pruebas, tarjetas del manual (caducidad: diciembre del año en curso,
CVV2 989):

```
5540500001000004    5020470001370055
5020080001000006    4507670001000009
```

Comprobar que el pedido queda en `pagado`, que el stock baja y que llega el
email. Luego cambiar `CECA_ENTORNO` a `produccion`, apuntar la consola de
producción al mismo `aviso-pago` y hacer una compra real de 1 € con una tarjeta
propia, anulándola después desde la consola.

## Cosas que hay que ajustar

- `tienda_ajuste.envio_cent` está **vacío**: mientras lo esté, la web solo
  ofrece recoger en el centro. Para abrir el envío:
  `update tienda_ajuste set valor = '495' where clave = 'envio_cent';`
  (495 = 4,95 €) y poner también `envio_texto`.
- `tienda_stock` para la tote bag está a 50 por poner algo: ajustar.
- Para cerrar la tienda un rato:
  `update tienda_ajuste set valor = 'no' where clave = 'pedidos_abiertos';`

## Devoluciones

Se hacen desde la consola del TPV con la **Referencia** que guarda
`tienda_pedido.ceca_referencia`. No hace falta tocar código.
