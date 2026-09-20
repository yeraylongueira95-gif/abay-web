#!/usr/bin/env python3
"""Genera sitio/index.html a partir de la plantilla y del faro (hero.html).

Uso:  python3 src/build.py      (desde la carpeta "Web ABAY")
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "sitio")
IMG = os.path.join(OUT, "assets", "img")

hero = open(os.path.join(SRC, "hero.html"), encoding="utf-8").read()
tpl = open(os.path.join(SRC, "index.template.html"), encoding="utf-8").read()

# ---------- vectores (de la propia portada) ----------
spark_d = " ".join(re.search(r'<g id="spark".*?<path d="([^"]+)"', hero, re.S).group(1).split())
wm_ds = re.findall(r'<g class="wmL"[^>]*><path d="([^"]+)"', hero)
assert len(wm_ds) == 4, "no encuentro las 4 letras del logotipo"
wm_d = " ".join(" ".join(d.split()) for d in wm_ds)

# ---------- CSS del faro ----------
css_all = re.search(r"<style>(.*?)</style>", hero, re.S).group(1)
m_scene = re.search(r"(#scene\{.*?)(?=/\* ---------- grain)", css_all, re.S).group(1)
m_replay = re.search(r"(/\* ---------- replay ---------- \*/.*?)(?=@media \(prefers-reduced-motion)", css_all, re.S).group(1)
hero_css = (m_scene + "\n" + m_replay).replace("position:fixed", "position:absolute")
hero_css = ("#hero{position:relative;height:100vh;height:100svh;min-height:560px;overflow:hidden;background:var(--ink)}\n"
            + hero_css)
hero_css = hero_css.replace("#brand{\n  position:absolute", "#brand{\n  z-index:5;\n  position:absolute")

# ---------- HTML del faro ----------
body = re.search(r"<body>(.*?)<script>", hero, re.S).group(1)
canvas = re.search(r'<canvas id="scene"[^>]*></canvas>', body).group(0)
brand = re.search(r'<div id="brand".*?<div id="sub2">.*?</div>\s*</div>', body, re.S).group(0)
replay = re.search(r'<button id="replay".*?</button>', body, re.S).group(0)
hero_html = "  " + canvas + "\n" + brand + "\n" + replay

# ---------- JS del faro (adaptado a vivir dentro de la página) ----------
js = re.search(r"<script>\n(.*)</script>", hero, re.S).group(1)

def swap(old, new):
    global js
    assert old in js, "no encuentro en el faro: " + old[:60]
    js = js.replace(old, new)

swap("W = innerWidth; H = innerHeight;", "W = cv.clientWidth; H = cv.clientHeight;")
swap("""  const r = brand.querySelector('svg').getBoundingClientRect();
  sparkPt = { x: r.left + r.width*(561.5/980), y: r.top + r.height*(113/710) };""",
     """  const r = brand.querySelector('svg').getBoundingClientRect();
  const cr = cv.getBoundingClientRect();
  sparkPt = { x: r.left - cr.left + r.width*(561.5/980), y: r.top - cr.top + r.height*(113/710) };""")
swap("""    replayBtn.classList.add('on');
    if(!window.__fx0){ window.__fx0 = performance.now(); }""",
     """    replayBtn.classList.add('on');
    document.body.classList.add('hero-done');
    if(!window.__fx0){ window.__fx0 = performance.now(); }""")
swap("""  replayBtn.classList.add('on');
  window.__fx0 = performance.now();
}""", """  replayBtn.classList.add('on');
  document.body.classList.add('hero-done');
  window.__fx0 = performance.now();
}""")
# la animación se pausa cuando la portada sale de pantalla (ahorra batería y CPU)
swap("addEventListener('resize', ()=>{resize(); if(REDUCED) finalFrame();});",
     """let heroVisible = true;
new IntersectionObserver(en=>{
  heroVisible = en[0].isIntersecting;
  if(!heroVisible){ paused=true; cancelAnimationFrame(raf); }
  else if(!REDUCED && paused && !document.hidden){
    paused=false;
    t0 = window.__fx0 ? performance.now() - (T.ambient+2)*1000 : performance.now();
    raf=requestAnimationFrame(loop);
  }
},{threshold:0}).observe(cv);

let rzT=0;
addEventListener('resize', ()=>{ clearTimeout(rzT); rzT=setTimeout(()=>{resize(); if(REDUCED||paused) finalFrame();},120); });""")
swap("  else if(!REDUCED){\n    // reanudar", "  else if(!REDUCED && heroVisible){\n    // reanudar")

# si el equipo no puede con la animación, se muestra el fotograma final (nada de pantalla en negro)
swap("""function loop(now){
  if(paused) return;
  const t=(now-t0)/1000;
  draw(t);
  updateBrand(t);
  raf=requestAnimationFrame(loop);
}""", """let frames=0, fpsT0=0;
function loop(now){
  if(paused) return;
  const t=(now-t0)/1000;
  if(!fpsT0) fpsT0 = now;
  frames++;
  if(t < T.sparkIn && now - fpsT0 > 900 && frames / ((now - fpsT0)/1000) < 18){
    finalFrame();            // equipo lento: al final directamente
    return;
  }
  draw(t);
  updateBrand(t);
  raf=requestAnimationFrame(loop);
}""")

swap("  if((e.key==='r'||e.key==='R') && !e.metaKey && !e.ctrlKey) start();",
     "  if((e.key==='r'||e.key==='R') && !e.metaKey && !e.ctrlKey && heroVisible && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) start();")

# ---------- imágenes: <picture> AVIF + JPG con tamaños ----------
def dims(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], capture_output=True, text=True).stdout
    w = int(re.search(r"pixelWidth: (\d+)", out).group(1))
    h = int(re.search(r"pixelHeight: (\d+)", out).group(1))
    return w, h

def pic(m):
    name, alt, sizes = m.group(1), m.group(2), m.group(3)
    widths = sorted(int(f.split("-")[-1].split(".")[0]) for f in os.listdir(IMG)
                    if f.startswith(name + "-") and f.endswith(".jpg"))
    assert widths, "faltan imágenes de " + name
    small = widths[0]
    w, h = dims(os.path.join(IMG, f"{name}-{small}.jpg"))
    avif = ", ".join(f"/assets/img/{name}-{x}.avif {x}w" for x in widths)
    jpg = ", ".join(f"/assets/img/{name}-{x}.jpg {x}w" for x in widths)
    return (f'<picture><source type="image/avif" srcset="{avif}" sizes="{sizes}">'
            f'<img src="/assets/img/{name}-{small}.jpg" srcset="{jpg}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async"></picture>')

html = re.sub(r"\{\{pic:([a-z0-9]+)\|([^|}]+)\|([^}]+)\}\}", pic, tpl)
html = (html.replace("__HEROCSS__", hero_css)
            .replace("__HEROHTML__", hero_html)
            .replace("__HEROJS__", js)
            .replace("__SPARKD__", spark_d)
            .replace("__WMD__", wm_d))
leftover = re.findall(r"__[A-Z]+__|\{\{pic:", html)
assert not leftover, f"tokens sin reemplazar: {leftover}"

open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)

# el vector también sirve de favicon
fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#050608"/>'
       '<g transform="translate(8.5,19) scale(0.0425)"><g transform="translate(0,619) scale(0.1,-0.1)" fill="#f3efe7">'
       f'<path d="{spark_d}"/></g></g></svg>')
open(os.path.join(OUT, "favicon.svg"), "w").write(fav)

import paginas
paginas.generar(OUT)

# icono para la pantalla de inicio del iPhone (180x180 PNG a partir del favicon)
tmp = os.path.join(SRC, ".tmp"); os.makedirs(tmp, exist_ok=True)
subprocess.run(["qlmanage", "-t", "-s", "180", "-o", tmp, os.path.join(OUT, "favicon.svg")], capture_output=True)
png = os.path.join(tmp, "favicon.svg.png")
if os.path.exists(png):
    subprocess.run(["sips", "-z", "180", "180", png, "--out", os.path.join(OUT, "apple-touch-icon.png")], capture_output=True)

print("index.html:", os.path.getsize(os.path.join(OUT, "index.html")) // 1024, "KB")
