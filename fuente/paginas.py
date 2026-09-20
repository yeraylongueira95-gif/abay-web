#!/usr/bin/env python3
"""Páginas secundarias: legales, 404, robots, sitemap y cabeceras de Cloudflare Pages.
Lo llama build.py; los datos entre [corchetes] están pendientes de rellenar."""
import os

DOMINIO = "https://abayperformance.com"
EMPRESA = {
    "razon": "ABAY CENTRO DE ENTRENAMIENTO, S.L.",
    "cif": "B26748228",
    "registro": "[Datos de inscripción en el Registro Mercantil de A Coruña PENDIENTES]",
    "direccion": "C/ Pedro Galán Calvete, 9, 15002 A Coruña",
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
  <span>© 2026 ABAY Performance Center · A Coruña</span>
  <a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a><a href="/cookies/">Cookies</a>
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
<li>Domicilio: {E['direccion']}</li>
<li>Email: {E['email']}</li>
<li>{E['registro']}</li>
</ul>
<h2>Objeto</h2>
<p>La web abayperformance.com informa sobre los servicios de ABAY Performance Center: entrenamiento personal, funcional y de rendimiento deportivo; fisioterapia, rehabilitación y recuperación; nutrición; y demás actividades relacionadas con la salud, el deporte y el bienestar que constan en el objeto social de la sociedad. A través de la web también pueden ofrecerse y contratarse servicios y productos propios; en ese caso se publicarán sus condiciones de contratación.</p>
<h2>Propiedad intelectual</h2>
<p>Los textos, fotografías, logotipos y el diseño de esta web pertenecen a {E['razon']} o a sus autores, y no pueden reproducirse sin autorización.</p>
<h2>Responsabilidad</h2>
<p>El titular no se hace responsable del contenido de las webs externas a las que se enlaza (Google Maps, WhatsApp, Instagram).</p>
<h2>Legislación aplicable</h2>
<p>Esta web se rige por la legislación española.</p>""")

PRIV = P(f"""<p class="k">Información legal</p>
<h1>Política de privacidad</h1>
<h2>Responsable</h2>
<p>{E['razon']} (CIF {E['cif']}), {E['direccion']}. Contacto: {E['email']}.</p>
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
<h2>El mapa de Google</h2>
<p>En la sección «El espacio» hay un mapa que solo se carga si pulsas «Ver mapa». En ese momento Google Maps puede instalar sus propias cookies, según la <a href="https://policies.google.com/technologies/cookies?hl=es" rel="noopener">política de cookies de Google</a>.</p>
<h2>Enlaces externos</h2>
<p>Los botones de WhatsApp, Instagram y Google te llevan a esas plataformas, que tienen sus propias políticas de cookies.</p>""")

NF = """<p class="k">Error 404</p>
<h1>Esta página no existe.</h1>
<p>Puede que el enlace esté mal escrito o que la página se haya movido.</p>
<p style="margin-top:28px"><a href="/" style="display:inline-block;background:#0c0f12;color:#f8f6f1;padding:14px 24px;font-size:12px;letter-spacing:.16em;text-transform:uppercase;text-decoration:none">Ir a la portada</a></p>"""

def generar(out):
    def w(ruta, contenido):
        p = os.path.join(out, ruta)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(contenido)
    w("aviso-legal/index.html", pagina("Aviso legal", "Aviso legal de ABAY Performance Center.", AVISO, "/aviso-legal/"))
    w("privacidad/index.html", pagina("Política de privacidad", "Política de privacidad de ABAY Performance Center.", PRIV, "/privacidad/"))
    w("cookies/index.html", pagina("Política de cookies", "Política de cookies de ABAY Performance Center.", COOK, "/cookies/"))
    w("404.html", pagina("Página no encontrada", "Página no encontrada.", NF, "/404", indexar=False))
    w("site.webmanifest", '{"name":"ABAY Performance Center","short_name":"ABAY","start_url":"/","display":"standalone","background_color":"#050608","theme_color":"#050608","lang":"es","icons":[{"src":"/apple-touch-icon.png","sizes":"180x180","type":"image/png"},{"src":"/favicon.svg","sizes":"any","type":"image/svg+xml"}]}\n')
    w("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n")
    urls = ["/", "/aviso-legal/", "/privacidad/", "/cookies/"]
    w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{DOMINIO}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    # Cloudflare Pages: caché larga para fuentes e imágenes, cabeceras de seguridad
    w("_headers", """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
  X-Frame-Options: SAMEORIGIN
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-src https://maps.google.com https://www.google.com; connect-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/img/*
  Cache-Control: public, max-age=2592000

/og.jpg
  Cache-Control: public, max-age=604800

/favicon.svg
  Cache-Control: public, max-age=604800
""")
