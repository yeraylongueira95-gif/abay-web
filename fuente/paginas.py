#!/usr/bin/env python3
"""Páginas secundarias: legales, 404, robots, sitemap y cabeceras de Cloudflare Pages.
Lo llama build.py; los datos entre [corchetes] están pendientes de rellenar."""
import os

DOMINIO = "https://abayperformance.com"
EMPRESA = {
    "razon": "ABAY CENTRO DE ENTRENAMIENTO, S.L.",
    "domicilio": "C/ Cuento, 14, 2.º, 15002 A Coruña",
    "cif": "B26748228",
    "registro": "Inscrita en el Registro Mercantil de A Coruña, hoja C-67639, inscripción 1.ª, de 18 de febrero de 2026",
    "direccion": "C/ Pedro Galán Calvete, 9, 15002 A Coruña",  # el centro
    "email": "info@abay.es",
}

CSS = """
@font-face{font-family:'Space Grotesk';src:url(/assets/fonts/SpaceGrotesk-latin.woff2) format('woff2');font-weight:300 500;font-display:swap}
@font-face{font-family:'Space Mono';src:url(/assets/fonts/SpaceMono-latin.woff2) format('woff2');font-weight:400;font-display:swap}
*{margin:0;padding:0;box-sizing:border-box}
html{background:#f8f6f1}
body{font-family:'Space Grotesk',system-ui,sans-serif;color:#0c0f12;-webkit-font-smoothing:antialiased;line-height:1.7}
a{color:inherit}
header{display:flex;align-items:center;justify-content:space-between;padding:18px clamp(20px,5vw,84px);background:#050608}
header a{display:flex;align-items:center;gap:12px;color:#9aa1a6;font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.24em;text-transform:uppercase;text-decoration:none}
header a:hover{color:#f3efe7}
header svg{width:36px;height:20px;fill:#f3efe7}
main{max-width:760px;margin:0 auto;padding:clamp(50px,9vh,100px) clamp(20px,5vw,40px) 80px}
.k{font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.38em;text-transform:uppercase;color:#a8874f}
h1{font-weight:300;font-size:clamp(36px,6vw,64px);line-height:1.05;letter-spacing:-.015em;margin:18px 0 36px}
h2{font-weight:400;font-size:20px;margin:38px 0 10px}
p,li{color:#3d4247;font-size:16px;margin-bottom:12px}
ul{padding-left:20px}
.pend{background:#f3e3c3;padding:0 4px}
footer{border-top:1px solid rgba(12,15,18,.1);padding:28px clamp(20px,5vw,84px);font-family:'Space Mono',monospace;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:#8b9197;display:flex;gap:10px 26px;flex-wrap:wrap}
footer a{text-decoration:none}
footer a:hover{color:#0c0f12}
"""

def pagina(titulo, desc, cuerpo, ruta, indexar=True):
    spark = open(os.path.join(os.path.dirname(__file__), "..", "sitio", "favicon.svg")).read()
    d = spark.split('<path d="')[1].split('"')[0]
    robots = "" if indexar else '<meta name="robots" content="noindex">\n'
    canon = f'<link rel="canonical" href="{DOMINIO}{ruta}">\n' if indexar else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} · ABAY Performance Center</title>
<meta name="description" content="{desc}">
{robots}{canon}<meta name="theme-color" content="#050608">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>{CSS}</style>
</head>
<body>
<header>
  <a href="/" aria-label="Volver a la web de ABAY"><svg viewBox="0 0 1113 619" aria-hidden="true"><g transform="translate(0,619) scale(0.1,-0.1)"><path d="{d}"/></g></svg>Volver</a>
</header>
<main>
{cuerpo}
</main>
<footer>
  <span>© 2026 ABAY Centro de Entrenamiento, S.L. · A Coruña</span>
  <a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a><a href="/cookies/">Cookies</a><a href="/condiciones/">Condiciones de compra</a>
</footer>
</body>
</html>
"""

def P(texto):
    """Marca en color los datos pendientes para que se vean al revisar."""
    import re
    return re.sub(r"\[([^\]]+)\]", r'<span class="pend">[\1]</span>', texto)

E = EMPRESA
AVISO = P(f"""<p class="k">Información legal</p>
<h1>Aviso legal</h1>
<h2>Titular de la web</h2>
<p>En cumplimiento del artículo 10 de la Ley 34/2002, de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), se informa de que esta web es titularidad de:</p>
<ul>
<li>Razón social: {E['razon']}</li>
<li>CIF: {E['cif']}</li>
<li>Domicilio social: {E['domicilio']}</li>
<li>Centro: {E['direccion']}</li>
<li>Email: {E['email']}</li>
<li>{E['registro']}</li>
</ul>
<h2>Objeto</h2>
<p>La web abayperformance.com informa sobre los servicios de ABAY Performance Center y permite ponerse en contacto con el centro. A través de la web también pueden ofrecerse y contratarse servicios y productos propios; en ese caso se publicarán sus condiciones de contratación.</p>
<h2>Objeto social</h2>
<p>Según sus estatutos, la sociedad tiene por objeto social (CNAE 8551) las actividades de formación, en forma de entrenamientos personales y colectivos, sesiones grupales de entrenamiento de fuerza y acondicionamiento, clases dirigidas, running, entrenamiento funcional, asesoramiento y entrenamiento online, pilates y cualquier actividad relacionada con la salud postural. Asimismo desarrolla, entre otras:</p>
<ul>
<li>Desarrollo de centros de entrenamiento, salud, bienestar y actividades deportivas (CNAE 9313).</li>
<li>Venta y comercialización, al por menor y/o al por mayor, de material y artículos deportivos, ropa y complementos deportivos (CNAE 4764).</li>
<li>Actividades de recuperación físico-deportiva mediante técnicas no sanitarias deportivas y rehabilitación, mejora del rendimiento deportivo y tecnificación, y asesoramiento nutricional y dietético.</li>
<li>Asesoramiento afectivo-motivacional y gestión emocional en el ámbito deportivo.</li>
<li>Asesoramiento sobre cuidado y prevención de lesiones en el complejo pie-tobillo en el ámbito deportivo.</li>
<li>Asesoramiento técnico en el ámbito deportivo.</li>
<li>Alquiler de bienes inmobiliarios por cuenta propia (CNAE 6820).</li>
<li>Desarrollo de actividades y eventos de carácter formativo en el ámbito deportivo, así como colaboraciones con entidades públicas y/o privadas.</li>
</ul>
<h2>Propiedad intelectual</h2>
<p>Los textos, fotografías, logotipos y el diseño de esta web pertenecen a {E['razon']} o a sus autores, y no pueden reproducirse sin autorización.</p>
<h2>Responsabilidad</h2>
<p>El titular no se hace responsable del contenido de las webs externas a las que se enlaza (Google Maps, WhatsApp, Instagram).</p>
<h2>Legislación aplicable</h2>
<p>Esta web se rige por la legislación española.</p>""")

PRIV = P(f"""<p class="k">Información legal</p>
<h1>Política de privacidad</h1>
<h2>Responsable</h2>
<p>{E['razon']} (CIF {E['cif']}), con domicilio social en {E['domicilio']} y centro en {E['direccion']}. Contacto: {E['email']}.</p>
<h2>Qué datos tratamos</h2>
<p>Tratamos los datos que nos facilitas cuando nos escribes por WhatsApp, email o Instagram: tu nombre, tu forma de contacto y lo que nos cuentes en el mensaje. Si rellenas un formulario de contacto o de reserva en esta web, tratamos además los datos que indiques en él. Solo pedimos lo necesario para atenderte.</p>
<h2>Para qué</h2>
<p>Para responder a tu consulta, organizar tu primera sesión y, si te haces cliente, gestionar tus sesiones, tratamientos y servicios, así como la facturación.</p>
<h2>Formularios y reservas</h2>
<p>Cuando la web incorpore formularios (contacto, reserva de sesión o alta como cliente), se indicará en cada uno qué datos son obligatorios y para qué se usan, y será necesario aceptar esta política antes de enviarlos.</p>
<h2>Base legal</h2>
<p>Tu consentimiento al escribirnos y, si contratas un servicio, la ejecución de ese contrato (art. 6.1.a y 6.1.b del RGPD). Los datos de salud que nos facilites para recibir cualquiera de nuestros servicios (entrenamiento, fisioterapia, rehabilitación, recuperación o nutrición) se tratan con las garantías del art. 9.2.h del RGPD y solo por los profesionales que te atienden, sujetos a secreto profesional.</p>
<h2>Cuánto tiempo</h2>
<p>El necesario para atender tu consulta o mientras seas cliente, y después durante los plazos legales obligatorios.</p>
<h2>Con quién se comparten</h2>
<p>No cedemos tus datos a terceros salvo obligación legal. Los servicios de mensajería que elijas para escribirnos (WhatsApp, Instagram, email) tratan los datos según sus propias políticas.</p>
<h2>Tus derechos</h2>
<p>Puedes pedir el acceso, la rectificación, la supresión, la oposición, la limitación o la portabilidad de tus datos escribiendo a {E['email']}. Si no quedas satisfecho, puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).</p>""")

COOK = P("""<p class="k">Información legal</p>
<h1>Política de cookies</h1>
<h2>Esta web no usa cookies</h2>
<p>abayperformance.com no instala cookies propias ni de terceros, ni usa herramientas de analítica o publicidad. Las fuentes y las imágenes se sirven desde nuestro propio dominio. Por eso no verás ningún aviso de cookies.</p>
<h2>El mapa</h2>
<p>El plano de la sección «El espacio» es una imagen alojada en nuestro propio servidor, hecha con datos de <a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a> (© colaboradores de OpenStreetMap). No se carga nada desde Google ni desde ningún otro servidor: al verlo no se envía tu dirección IP a terceros ni se instala ninguna cookie. Solo si pulsas el plano se abre Google Maps, ya fuera de esta web.</p>
<h2>Enlaces externos</h2>
<p>Los botones de WhatsApp, Instagram y Google te llevan a esas plataformas, que tienen sus propias políticas de cookies.</p>""")

CONTRA = P(f"""<p class="k">Tienda</p>
<h1>Condiciones de contratación</h1>
<p>Estas condiciones regulan la venta de productos y bonos de ABAY Performance Center a distancia, es decir, cuando el pedido se hace por WhatsApp, por email o a través de esta web, sin estar presente en el centro. Al hacer un pedido aceptas lo que viene a continuación. Te recomendamos guardar una copia.</p>

<h2>1. Quién vende</h2>
<ul>
<li>Razón social: {E['razon']}</li>
<li>CIF: {E['cif']}</li>
<li>Domicilio social: {E['domicilio']}</li>
<li>Centro y dirección a efectos de devoluciones: {E['direccion']}</li>
<li>Email: {E['email']} · WhatsApp: +34 624 852 324</li>
</ul>

<h2>2. Productos y precios</h2>
<p>Los precios que ves en la tienda están <strong>en euros y con el IVA incluido</strong>. No incluyen los gastos de envío, que se indican aparte y se te confirman antes de que pagues. Antes de cerrar el pedido siempre sabrás el total exacto: producto, talla, envío e importe final.</p>
<p>Las fotografías son orientativas. El tono de la prenda puede variar ligeramente según la pantalla.</p>
<p>Las camisetas se venden en tallas XS a XXL y las unidades son limitadas. Si una talla se agota después de que hagas el pedido te avisamos y puedes elegir otra talla o que te devolvamos el dinero.</p>

<h2>3. Cómo se hace un pedido</h2>
<p>Hoy los pedidos se cierran por WhatsApp: nos dices el producto y la talla, te confirmamos disponibilidad, el total con envío y la forma de pago. El contrato queda formalizado cuando confirmamos el pedido y se completa el pago.</p>
<p>Cuando la web tenga pago en línea, el proceso será el mismo pero automático, con la confirmación por email.</p>

<h2>4. Formas de pago</h2>
<p>Admitimos pago en el centro, transferencia bancaria, Bizum y tarjeta. Los pagos con tarjeta y Bizum a distancia se procesan a través de la pasarela de pago segura de nuestra entidad bancaria: los datos de tu tarjeta se introducen directamente en el entorno del banco y <strong>ABAY no los ve ni los almacena en ningún momento</strong>.</p>

<h2>5. Envíos y entrega</h2>
<p><strong>Recogida en el centro:</strong> gratuita. Te avisamos cuando esté listo y lo recoges en C/ Pedro Galán Calvete, 9.</p>
<p><strong>Envío a domicilio:</strong> [zonas de envío] por [importe de los gastos de envío]. Plazo estimado de entrega: [plazo] días laborables desde que se confirma el pago.</p>
<p>Si el pedido se retrasa por encima de ese plazo te informamos y puedes cancelarlo y recuperar el dinero. Revisa el paquete al recibirlo: si llega dañado, dínoslo lo antes posible y nos encargamos.</p>

<h2>6. Derecho de desistimiento</h2>
<p>Si eres consumidor, tienes <strong>14 días naturales</strong> para devolver el producto sin dar ninguna explicación. El plazo cuenta desde el día en que recibes el pedido.</p>
<p>Para ejercerlo basta con decírnoslo por email a {E['email']} o por WhatsApp antes de que acaben esos 14 días. Puedes usar el <a href="/desistimiento/">formulario de desistimiento</a>, aunque no es obligatorio. Te confirmaremos la recepción.</p>
<p>Después tienes 14 días más para devolvernos el producto. Te <strong>devolvemos todo lo que pagaste, incluidos los gastos de envío estándar</strong>, en un plazo máximo de 14 días desde que nos comunicas el desistimiento, por el mismo medio con el que pagaste. Podemos esperar a haber recibido el producto antes de hacer la devolución.</p>
<p><strong>El coste de devolverlo lo pagas tú</strong>, salvo que el producto llegara defectuoso o equivocado, en cuyo caso lo pagamos nosotros.</p>
<p>El producto debe volver completo, sin usar más de lo necesario para probarlo y con sus etiquetas. No hay derecho de desistimiento en los servicios ya prestados en su totalidad con tu consentimiento previo expreso (por ejemplo, una sesión de entrenamiento o de fisioterapia ya realizada), tal y como prevé el artículo 103 del texto refundido de la Ley General para la Defensa de los Consumidores y Usuarios.</p>

<h2>7. Cambios de talla</h2>
<p>Si la talla no te va, escríbenos dentro de los 14 días y te la cambiamos por otra si hay stock. El cambio en el centro es gratuito; si hay que enviarlo, se aplican los gastos de envío del nuevo pedido.</p>

<h2>8. Garantía</h2>
<p>Los productos tienen la garantía legal de <strong>tres años</strong> por falta de conformidad prevista en el artículo 120 del texto refundido de la Ley General para la Defensa de los Consumidores y Usuarios. Si el producto sale defectuoso, escríbenos y lo reparamos, lo sustituimos o te devolvemos el dinero, según corresponda. No cubre el desgaste normal por el uso ni los daños por un lavado distinto al indicado en la etiqueta.</p>

<h2>9. Tarjeta regalo y bonos</h2>
<p>La tarjeta regalo es un bono de sesiones de entrenamiento o de fisioterapia. Una vez emitida:</p>
<ul>
<li>Es <strong>transferible</strong>: la puede usar la persona a la que se la regales, aunque no sea quien la compró.</li>
<li><strong>No es canjeable por dinero</strong> ni reembolsable una vez que se ha empezado a usar.</li>
<li>Tiene una validez de [validez de la tarjeta regalo] desde la fecha de compra. Las sesiones no utilizadas en ese plazo se pierden.</li>
<li>Las sesiones se reservan con cita previa y están sujetas a disponibilidad de horario.</li>
<li>Si se compra a distancia y no se ha usado ninguna sesión, se le aplica el derecho de desistimiento de 14 días del punto 6.</li>
</ul>

<h2>10. Reclamaciones</h2>
<p>Si algo no ha salido como esperabas, escríbenos a {E['email']} y te respondemos. En el centro hay hojas de reclamaciones oficiales a tu disposición.</p>
<p>Como consumidor también puedes dirigirte al Instituto Galego do Consumo e da Competencia de la Xunta de Galicia o a la oficina municipal de información al consumidor de tu ayuntamiento. ABAY no está adherida, por el momento, a ninguna junta arbitral de consumo.</p>

<h2>11. Ley aplicable</h2>
<p>Estas condiciones se rigen por la legislación española. Si eres consumidor, cualquier discrepancia se resolverá ante los juzgados de tu lugar de residencia.</p>

<h2>12. Cambios en estas condiciones</h2>
<p>Podemos actualizar estas condiciones. A tu pedido se le aplican siempre las que estaban publicadas en el momento en que lo hiciste.</p>
<p style="margin-top:30px;font-size:13px;color:#8b9197">Última actualización: noviembre de 2026.</p>""")

DESIST = P(f"""<p class="k">Tienda</p>
<h1>Formulario de desistimiento</h1>
<p>Si has comprado a distancia y quieres devolver el producto, tienes <strong>14 días naturales</strong> desde que lo recibiste y no hace falta que des ninguna explicación. Puedes usar este modelo, pero no es obligatorio: basta con que nos lo digas de forma clara por email a {E['email']} o por WhatsApp al +34 624 852 324.</p>
<p>Lee antes el punto 6 de las <a href="/condiciones/">condiciones de contratación</a>, donde se explican los plazos y quién paga el envío de vuelta.</p>

<h2>Modelo</h2>
<p>Copia este texto, rellena tus datos y envíanoslo:</p>
<div style="background:#fff;border:1px solid rgba(12,15,18,.14);padding:26px 24px;margin:18px 0 26px;font-size:15px;line-height:1.85">
<p>A la atención de {E['razon']}, {E['direccion']}, {E['email']}:</p>
<p>Por la presente le comunico que desisto de mi contrato de venta del siguiente producto:</p>
<p>Producto y talla: ...........................................................<br>
Número o fecha del pedido: ...........................................<br>
Fecha en que lo recibí: ...................................................</p>
<p>Nombre y apellidos: ......................................................<br>
Domicilio: ......................................................................<br>
Email o teléfono de contacto: ........................................</p>
<p>Fecha: ............................................</p>
<p>Firma (solo si envías este formulario en papel): ............................................</p>
</div>

<h2>Qué pasa después</h2>
<ul>
<li>Te confirmamos que hemos recibido tu comunicación.</li>
<li>Tienes 14 días para devolvernos el producto a C/ Pedro Galán Calvete, 9, 15002 A Coruña, o para dejarlo en el centro.</li>
<li>Te devolvemos el importe íntegro, incluidos los gastos de envío estándar, en un máximo de 14 días y por el mismo medio de pago que usaste.</li>
<li>El coste de devolver el producto corre por tu cuenta, salvo que llegara defectuoso o equivocado.</li>
</ul>""")

NF = P("""<p class="k">Error 404</p>
<h1>Esta página no existe.</h1>
<p>Puede que el enlace esté mal escrito o que la página se haya movido.</p>
<p style="margin-top:28px"><a href="/" style="display:inline-block;background:#0c0f12;color:#f8f6f1;padding:14px 24px;font-size:12px;letter-spacing:.16em;text-transform:uppercase;text-decoration:none">Ir a la portada</a></p>""")

def generar(out):
    def w(ruta, contenido):
        p = os.path.join(out, ruta)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(contenido)
    w("aviso-legal/index.html", pagina("Aviso legal", "Aviso legal de ABAY Performance Center.", AVISO, "/aviso-legal/"))
    w("privacidad/index.html", pagina("Política de privacidad", "Política de privacidad de ABAY Performance Center.", PRIV, "/privacidad/"))
    w("cookies/index.html", pagina("Política de cookies", "Política de cookies de ABAY Performance Center.", COOK, "/cookies/"))
    w("condiciones/index.html", pagina("Condiciones de contratación", "Condiciones de compra de la tienda de ABAY Performance Center: precios, envíos, desistimiento de 14 días, devoluciones, garantía y tarjeta regalo.", CONTRA, "/condiciones/"))
    w("desistimiento/index.html", pagina("Formulario de desistimiento", "Modelo de formulario para devolver un producto comprado a distancia en ABAY Performance Center dentro de los 14 días.", DESIST, "/desistimiento/"))
    w("404.html", pagina("Página no encontrada", "Página no encontrada.", NF, "/404", indexar=False))
    w("site.webmanifest", '{"name":"ABAY Performance Center","short_name":"ABAY","start_url":"/","display":"standalone","background_color":"#050608","theme_color":"#050608","lang":"es","icons":[{"src":"/apple-touch-icon.png","sizes":"180x180","type":"image/png"},{"src":"/favicon.svg","sizes":"any","type":"image/svg+xml"}]}\n')
    w("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n")
    urls = ["/", "/aviso-legal/", "/privacidad/", "/cookies/", "/condiciones/", "/desistimiento/"]
    w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{DOMINIO}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    # Cloudflare Pages: caché larga para fuentes e imágenes, cabeceras de seguridad
    w("_headers", """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
  X-Frame-Options: SAMEORIGIN
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-src 'none'; connect-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/img/*
  Cache-Control: public, max-age=2592000

/og.jpg
  Cache-Control: public, max-age=604800

/favicon.svg
  Cache-Control: public, max-age=604800
""")
