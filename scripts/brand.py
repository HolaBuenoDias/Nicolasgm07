"""Sistema de diseño del perfil: tokens de color, tipografía, movimiento e iconos,
más los helpers que usan todos los generadores de SVG (estáticos y dinámicos).

Todo es librería estándar de Python para que funcione igual en local y en GitHub Actions.
"""
from __future__ import annotations

import os
from xml.sax.saxutils import escape

OWNER = "Nicolasgm07"
REPO = "Nicolasgm07"
BRANCH = "main"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"
RAW_OUTPUT = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/output"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# --------------------------------------------------------------------------- color
# Naranja de marca = el mismo del CV (#F2511B). Neutros = los de GitHub para que los
# SVG se fundan con la página en modo claro y oscuro.
THEMES = {
    "dark": dict(
        canvas="#0d1117", surface="#161b22", raised="#1c2330", inset="#010409",
        border="#30363d", border_soft="#21262d",
        text="#e6edf3", muted="#9198a1", subtle="#6e7681",
        brand="#F2511B", brand_text="#FF7A45", brand_strong="#FF8A57",
        brand_soft="rgba(242,81,27,0.14)", brand_line="rgba(242,81,27,0.45)",
        grad_a="#FFB347", grad_b="#F2511B", on_brand="#ffffff",
        success="#3fb950", success_soft="rgba(63,185,80,0.16)",
        warning="#d29922", danger="#f85149",
        shadow="rgba(1,4,9,0.55)", grid="#30363d",
        # sintaxis (paleta de GitHub)
        kw="#ff7b72", str="#a5d6ff", prop="#ffa657", fn="#d2a8ff", num="#79c0ff", com="#8b949e",
        punc="#e6edf3", tag="#7ee787",
    ),
    "light": dict(
        canvas="#ffffff", surface="#f6f8fa", raised="#ffffff", inset="#eff2f5",
        border="#d0d7de", border_soft="#e6e9ee",
        text="#1f2328", muted="#59636e", subtle="#818b98",
        brand="#F2511B", brand_text="#C2410C", brand_strong="#D9480F",
        brand_soft="rgba(242,81,27,0.09)", brand_line="#FFC4AD",
        grad_a="#FF9F1C", grad_b="#F2511B", on_brand="#ffffff",
        success="#1a7f37", success_soft="#dafbe1",
        warning="#9a6700", danger="#cf222e",
        shadow="rgba(31,35,40,0.12)", grid="#d0d7de",
        kw="#cf222e", str="#0a3069", prop="#953800", fn="#8250df", num="#0550ae", com="#6e7781",
        punc="#1f2328", tag="#116329",
    ),
}

# Colores de lenguajes/tecnologías (puntos tipo GitHub linguist)
TECH = {
    "PHP": "#777bb4", "Java": "#b07219", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "HTML": "#e34c26", "CSS": "#663399", "SQL": "#e38c00", "XML": "#0060ac",
    "Angular": "#dd0031", "Spring Boot": "#6db33f", "Maven": "#c71a36", "MySQL": "#4479a1",
    "MariaDB": "#c0765a", "MongoDB": "#47a248", "WordPress": "#21759b", "WooCommerce": "#7f54b3",
    "PrestaShop": "#df0067", "Divi": "#8a3ffc", "Elementor": "#92003b", "Astra": "#5c2ede",
    "Moodle": "#f98012", "Swagger": "#85ea2d", "Lombok": "#bc2c2c", "Git": "#f05032",
    "Linux": "#fcc624", "Apache": "#d22128", "Cloudflare": "#f38020", "Google": "#4285f4",
}

# ---------------------------------------------------------------------- typography
SANS = ("'Segoe UI Variable Display','Segoe UI',-apple-system,BlinkMacSystemFont,"
        "'Helvetica Neue','Noto Sans',Arial,sans-serif")
MONO = ("ui-monospace,'Cascadia Code','SFMono-Regular','SF Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")

# Anchos aproximados (Helvetica AFM, 1/1000 em) para dimensionar chips y pills.
_W_REG = dict(zip(
    " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
    [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
    [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556,
     833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333,
     556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278,
     556, 500, 722, 500, 500, 500, 334, 260, 334, 584]))
_W_BOLD = dict(zip(
    " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
    [278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
    [333, 333, 584, 584, 584, 611, 975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611,
     833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556, 333,
     556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611, 611, 611, 389, 556, 333,
     611, 556, 778, 556, 556, 500, 389, 280, 389, 584]))
_FOLD = str.maketrans("áéíóúüñÁÉÍÓÚÜÑàèìòùç", "aeiouunAEIOUUNaeiouc")
_EXTRA = {"·": 278, "–": 556, "—": 1000, "«": 556, "»": 556, "€": 556, "º": 365, "ª": 370,
          "✓": 760, "→": 1000, "←": 1000, "●": 600, "•": 350, "…": 1000, "¿": 611, "¡": 333}


def text_width(s: str, size: float, weight: int = 400, mono: bool = False, tracking: float = 0) -> float:
    """Ancho estimado en px (algo generoso: mejor que sobre aire a que se corte)."""
    if mono:
        return len(s) * size * 0.6 + tracking * size * max(len(s) - 1, 0)
    table = _W_BOLD if weight >= 600 else _W_REG
    total = 0
    for ch in s:
        if ch in _EXTRA:
            total += _EXTRA[ch]
        else:
            total += table.get(ch.translate(_FOLD), 1000 if ord(ch) > 0x2000 else 556)
    return total / 1000 * size + tracking * size * max(len(s) - 1, 0)


# ------------------------------------------------------------------------- motion
EASE = "cubic-bezier(.2,.8,.2,1)"
BASE_CSS = f"""
text{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.rise{{animation:rise .75s {EASE} backwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}}}
.fade{{animation:fade .9s ease backwards}}
@keyframes fade{{from{{opacity:0}}}}
.pop{{animation:pop .6s cubic-bezier(.2,1.5,.4,1) backwards;transform-box:fill-box;transform-origin:center}}
@keyframes pop{{from{{opacity:0;transform:scale(.6)}}}}
.slide{{animation:slide .8s {EASE} backwards}}
@keyframes slide{{from{{opacity:0;transform:translateX(-16px)}}}}
.draw{{stroke-dasharray:1;animation:draw 1.4s {EASE} backwards}}
@keyframes draw{{from{{stroke-dashoffset:1}}}}
.pulse{{animation:pulse 2.2s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.35}}}}
.ping{{animation:ping 2.2s cubic-bezier(0,0,.2,1) infinite;transform-box:fill-box;transform-origin:center}}
@keyframes ping{{0%{{opacity:.7;transform:scale(1)}}80%,100%{{opacity:0;transform:scale(2.6)}}}}
.float{{animation:float 6s ease-in-out infinite}}
@keyframes float{{50%{{transform:translateY(-7px)}}}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
"""
# Notas de movimiento:
#  - Las entradas usan fill-mode "backwards": el estado base es el final, así que sin
#    animación (o con reduced-motion) todo se ve completo.
#  - .draw necesita pathLength="1" en el elemento.


def delay(i: float, step: float = 0.09, base: float = 0.1) -> str:
    """style="animation-delay:…" escalonado para listas."""
    return f'style="animation-delay:{base + i * step:.2f}s"'


# ------------------------------------------------------------------------- helpers
def esc(s) -> str:
    return escape(str(s), {'"': "&quot;"})


def svg_doc(w: float, h: float, body: str, *, title: str, desc: str = "", css: str = "",
            defs: str = "") -> str:
    """Documento SVG completo, accesible, con el CSS base del sistema."""
    d = f"<desc>{esc(desc)}</desc>" if desc else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" viewBox="0 0 {w:g} {h:g}" '
        f'role="img" aria-label="{esc(title)}" fill="none">'
        f"<title>{esc(title)}</title>{d}"
        f"<style>{BASE_CSS}{css}</style>"
        f"<defs>{defs}</defs>{body}</svg>\n"
    )


def write(rel_path: str, svg: str) -> str:
    """Escribe un asset (ruta relativa a assets/) en UTF-8 con saltos LF."""
    path = os.path.join(ASSETS, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    return path


def write_themed(rel_base: str, fn) -> list[str]:
    """fn(theme_name, palette) -> svg.  Escribe <rel_base>-dark.svg y <rel_base>-light.svg."""
    return [write(f"{rel_base}-{name}.svg", fn(name, THEMES[name])) for name in ("dark", "light")]


def picture(rel_base: str, alt: str, *, width=None, height=None, href=None, title=None,
            base_url: str = RAW + "/assets", themed: bool = True) -> str:
    """HTML para el README: <picture> claro/oscuro con URLs absolutas (como hace GitHub)."""
    size = (f' width="{width}"' if width else "") + (f' height="{height}"' if height else "")
    t = f' title="{esc(title)}"' if title else ""
    if themed:
        html = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base_url}/{rel_base}-dark.svg">'
                f'<source media="(prefers-color-scheme: light)" srcset="{base_url}/{rel_base}-light.svg">'
                f'<img src="{base_url}/{rel_base}-light.svg" alt="{esc(alt)}"{size}{t}></picture>')
    else:
        html = f'<img src="{base_url}/{rel_base}.svg" alt="{esc(alt)}"{size}{t}>'
    return f'<a href="{href}">{html}</a>' if href else html


def rrect(x, y, w, h, r, fill="none", stroke=None, sw=1, extra="") -> str:
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r:g}" fill="{fill}"{s} {extra}/>'


def dot_grid(pid: str, color: str, gap: float = 22, r: float = 1.1, opacity: float = 0.55) -> str:
    return (f'<pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{gap/2:g}" cy="{gap/2:g}" r="{r}" fill="{color}" fill-opacity="{opacity}"/></pattern>')


def shadow_filter(fid: str, color: str, dy: float = 10, blur: float = 14) -> str:
    return (f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="150%">'
            f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{blur/2:g}" flood-color="{color}"/></filter>')


def brand_gradient(gid: str, p: dict, x2: str = "100%", y2: str = "0%") -> str:
    return (f'<linearGradient id="{gid}" x1="0%" y1="0%" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{p["grad_a"]}"/><stop offset="1" stop-color="{p["grad_b"]}"/></linearGradient>')


def chip(x, y, label, p, *, dot=None, size=13, h=26, mono=False, fill=None, stroke=None,
         color=None, cls="", style="") -> tuple[str, float]:
    """Etiqueta redondeada (opcionalmente con punto de color). Devuelve (svg, ancho)."""
    pad = 11
    dw = 14 if dot else 0
    tw = text_width(label, size, 500, mono=mono)
    w = pad * 2 + dw + tw
    fam = ' class="mono"' if mono else ""
    out = [f'<g class="{cls}" {style}>' if (cls or style) else "<g>",
           rrect(x, y, w, h, h / 2, fill or p["surface"], stroke or p["border"])]
    if dot:
        out.append(f'<circle cx="{x + pad + 4:g}" cy="{y + h/2:g}" r="4.5" fill="{dot}"/>')
    out.append(f'<text x="{x + pad + dw:g}" y="{y + h/2 + size*0.36:g}" font-size="{size}" '
               f'font-weight="500" fill="{color or p["text"]}"{fam}>{esc(label)}</text></g>')
    return "".join(out), w


def wrap(text: str, size: float, max_width: float, weight: int = 400) -> list[str]:
    """Parte un texto en líneas que caben en max_width (estimación con text_width)."""
    lines, cur = [], ""
    for word in text.split():
        cand = f"{cur} {word}".strip()
        if cur and text_width(cand, size, weight) > max_width:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def paragraph(x, y, text, p, *, size=15, max_width=400, lh=None, color=None, weight=400,
              cls="", style="") -> tuple[str, float]:
    """Párrafo multilínea. Devuelve (svg, y de la última línea)."""
    lh = lh or round(size * 1.5)
    lines = wrap(text, size, max_width, weight)
    spans = "".join(f'<tspan x="{x:g}" dy="{0 if i == 0 else lh}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    attrs = (f' class="{cls}"' if cls else "") + (f" {style}" if style else "")
    svg = (f'<text x="{x:g}" y="{y:g}" font-size="{size}" font-weight="{weight}" '
           f'fill="{color or p["muted"]}"{attrs}>{spans}</text>')
    return svg, y + lh * (len(lines) - 1)


def card(x, y, w, h, p, *, r=18, fill=None, stroke=None, extra="") -> str:
    """Tarjeta estándar: superficie + borde (se funde con GitHub claro/oscuro)."""
    return rrect(x + .5, y + .5, w - 1, h - 1, r, fill or p["surface"], stroke or p["border"], 1, extra)


def kicker(x, y, text, p, *, color=None, size=12.5, anchor="start", extra="") -> str:
    """Etiqueta pequeña en mono y mayúsculas (antetítulo)."""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text class="mono" x="{x:g}" y="{y:g}" font-size="{size}" font-weight="600" letter-spacing="1.6" '
            f'fill="{color or p["brand_text"]}"{a} {extra}>{esc(text.upper())}</text>')


ODOMETER_CSS = """
.odo{animation:odo 1.6s cubic-bezier(.2,.8,.2,1) backwards}
@keyframes odo{from{transform:translateY(0)}}
"""


def odometer(x, y, value: str, p, *, uid: str, size=44, weight=800, color=None, start=0.2,
             stagger=0.08) -> tuple[str, float]:
    """Número que «rueda» hasta su valor (estado final = valor real, sin animación también).
    Necesita ODOMETER_CSS en el css del documento. Devuelve (svg, ancho)."""
    color = color or p["text"]
    dw = text_width("0", size, weight)
    lh = size * 1.18
    out, cx, i = [], x, 0
    clip = f'{uid}c'
    out.append(f'<clipPath id="{clip}"><rect x="{x - 2:g}" y="{y - size * 0.98:g}" width="{dw * len(value) + 40:g}" '
               f'height="{size * 1.24:g}"/></clipPath><g clip-path="url(#{clip})">')
    for ch in value:
        if ch.isdigit():
            d = int(ch)
            col = "".join(f'<text x="{cx:g}" y="{y + k * lh:g}" font-size="{size}" font-weight="{weight}" '
                          f'fill="{color}" style="font-variant-numeric:tabular-nums">{k}</text>' for k in range(d + 1))
            out.append(f'<g class="odo" style="transform:translateY({-d * lh:g}px);animation-delay:{start + i * stagger:.2f}s">'
                       f'{col}</g>')
            cx += dw
            i += 1
        else:
            out.append(f'<text x="{cx:g}" y="{y:g}" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ch)}</text>')
            cx += text_width(ch, size, weight)
    out.append("</g>")
    return "".join(out), cx - x


def window_dots(x, y, colors=("#ff5f57", "#febc2e", "#28c840"), r=5.5, gap=17) -> str:
    return "".join(f'<circle cx="{x + i*gap:g}" cy="{y:g}" r="{r}" fill="{c}"/>' for i, c in enumerate(colors))


def browser_frame(x, y, w, h, p, *, url="", r=14, bar=40, fill=None, extra="") -> tuple[str, tuple]:
    """Ventana de navegador. Devuelve (svg, (cx, cy, cw, ch)) con el área de contenido."""
    fill = fill or p["raised"]
    out = [f"<g {extra}>",
           rrect(x, y, w, h, r, fill, p["border"]),
           f'<path d="M{x+r} {y+0.5}H{x+w-r}A{r-0.5} {r-0.5} 0 0 1 {x+w-0.5} {y+r}V{y+bar}H{x+0.5}V{y+r}A{r-0.5} {r-0.5} 0 0 1 {x+r} {y+0.5}Z" fill="{p["surface"]}"/>',
           f'<line x1="{x}" y1="{y+bar}" x2="{x+w}" y2="{y+bar}" stroke="{p["border"]}"/>',
           window_dots(x + 20, y + bar / 2, r=5, gap=16)]
    if url:
        ax, aw = x + 76, min(w - 152, max(160, text_width(url, 12.5) + 52))
        out.append(rrect(ax, y + 9, aw, bar - 18, (bar - 18) / 2, p["canvas"], p["border_soft"]))
        out.append(icon("lock", ax + 9, y + bar / 2 - 6, 12, p["muted"], sw=2.2))
        out.append(f'<text x="{ax+27:g}" y="{y+bar/2+4.3:g}" font-size="12.5" fill="{p["muted"]}">{esc(url)}</text>')
    out.append("</g>")
    return "".join(out), (x + 1, y + bar + 1, w - 2, h - bar - 2)


def phone_frame(x, y, w, h, p, *, r=26) -> tuple[str, tuple]:
    """Marco de móvil. Devuelve (svg, (cx, cy, cw, ch)) con el área de pantalla."""
    b = 7
    out = (rrect(x, y, w, h, r, p["inset"] if p is THEMES["dark"] else "#1f2328", p["border"])
           + rrect(x + w/2 - 18, y + 9, 36, 7, 3.5, "#000000", None))
    return out, (x + b, y + b, w - 2*b, h - 2*b)


# ------------------------------------------------------------------------- iconos
# Iconos de línea propios en rejilla 24×24 (trazo redondeado). Rellenos: github, linkedin.
ICONS = {
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "layers": '<path d="M12 2.5 2 7.5l10 5 10-5-10-5Z"/><path d="M2 12.5l10 5 10-5"/><path d="M2 17.5l10 5 10-5"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5.5A2.5 2.5 0 0 1 11.5 3h1A2.5 2.5 0 0 1 15 5.5V7"/><path d="M3 12.5h18"/>',
    "cart": '<path d="M3 4h2.2l2.3 11a1.6 1.6 0 0 0 1.6 1.3h8.5a1.6 1.6 0 0 0 1.5-1.2L21 8H6.1"/><circle cx="9.5" cy="20" r="1.4"/><circle cx="17" cy="20" r="1.4"/>',
    "code": '<path d="M8 7l-5 5 5 5"/><path d="M16 7l5 5-5 5"/><path d="M13.5 4l-3 16"/>',
    "terminal": '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M7.5 9.5l3 2.5-3 2.5"/><path d="M12.5 15h4"/>',
    "folder": '<path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H9l2 2.2h7.5A2.5 2.5 0 0 1 21 9.7v7.8a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5v-10Z"/>',
    "cap": '<path d="M2 9.5 12 4.5l10 5-10 5-10-5Z"/><path d="M6 11.5v4.8c0 1.5 2.7 3.2 6 3.2s6-1.7 6-3.2v-4.8"/><path d="M22 9.5v6"/>',
    "chart": '<path d="M3 21h18"/><path d="M7 17v-4"/><path d="M12 17V7"/><path d="M17 17v-7"/>',
    "gamepad": '<path d="M7.5 8h9a4.8 4.8 0 0 1 4.6 6.2l-.9 3a2.4 2.4 0 0 1-4.1.9L14.6 16H9.4l-1.5 2.1a2.4 2.4 0 0 1-4.1-.9l-.9-3A4.8 4.8 0 0 1 7.5 8Z"/><path d="M8 10.8v3.6"/><path d="M6.2 12.6h3.6"/><circle cx="15.3" cy="11.6" r=".6" fill="currentColor"/><circle cx="17.3" cy="13.6" r=".6" fill="currentColor"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.8 7l8.2 6 8.2-6"/>',
    "pin": '<path d="M12 21.5s-7-6.3-7-11.8a7 7 0 0 1 14 0c0 5.5-7 11.8-7 11.8Z"/><circle cx="12" cy="9.7" r="2.6"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2.5"/><path d="M3 10h18"/><path d="M8 3v4"/><path d="M16 3v4"/>',
    "star": '<path d="M12 3.2l2.7 5.5 6 .9-4.4 4.2 1.1 6-5.4-2.8-5.4 2.8 1.1-6-4.4-4.2 6-.9L12 3.2Z"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "arrow": '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>',
    "external": '<path d="M7 17 17 7"/><path d="M9 7h8v8"/>',
    "sparkle": '<path d="M12 3c.6 4.4 2.6 6.4 7 7-4.4.6-6.4 2.6-7 7-.6-4.4-2.6-6.4-7-7 4.4-.6 6.4-2.6 7-7Z"/><path d="M19 15.5c.2 1.4.9 2.1 2.3 2.3-1.4.2-2.1.9-2.3 2.3-.2-1.4-.9-2.1-2.3-2.3 1.4-.2 2.1-.9 2.3-2.3Z"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.6-3.4 8.3-8 9-4.6-.7-8-4.4-8-9V6l8-3Z"/><path d="M8.6 12.2l2.4 2.4 4.4-4.8"/>',
    "truck": '<path d="M2.5 6h11.5v10H2.5z"/><path d="M14 10h4.2l3.3 3.4V16H14"/><circle cx="6.5" cy="17.8" r="2"/><circle cx="17.5" cy="17.8" r="2"/>',
    "card": '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19"/><path d="M6.5 15h4"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "server": '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01"/><path d="M7 16.5h.01"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3Z"/>',
    "award": '<circle cx="12" cy="9" r="6"/><path d="M8.6 14.2 7.3 21l4.7-2.7 4.7 2.7-1.3-6.8"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/>',
    "heart": '<path d="M12 20s-7.2-4.5-9.3-9.1A5 5 0 0 1 12 6.3a5 5 0 0 1 9.3 4.6C19.2 15.5 12 20 12 20Z"/>',
    "bolt": '<path d="M13 2.5 4.5 14H11l-1 7.5L18.5 10H12l1-7.5Z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20.5 20.5 16 16"/>',
    "box": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3Z"/><path d="M4 7.5l8 4.5 8-4.5"/><path d="M12 12v9"/>',
    "store": '<path d="M4 9.5 5.6 4h12.8L20 9.5"/><path d="M4 9.5h16v1.2a2.7 2.7 0 0 1-5.3.7 2.7 2.7 0 0 1-5.4 0A2.7 2.7 0 0 1 4 10.7V9.5Z"/><path d="M5.5 13v7h13v-7"/><path d="M10 20v-4.5h4V20"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    "language": '<path d="M4 5h9"/><path d="M8.5 3v2"/><path d="M6.2 5c.6 3 2.4 5.6 5 7"/><path d="M10.8 5c-.6 3.4-2.6 6.2-6.3 8"/><path d="M13 21l4-9 4 9"/><path d="M14.4 18h5.2"/>',
    "car": '<path d="M4.5 16v-3.6L6.6 7h10.8l2.1 5.4V16"/><path d="M3.5 16h17"/><circle cx="7.8" cy="16.5" r="1.8"/><circle cx="16.2" cy="16.5" r="1.8"/>',
    "wrench": '<path d="M14.7 6.3a4.2 4.2 0 0 0-5.5 5.5L3.5 17.5l3 3 5.7-5.7a4.2 4.2 0 0 0 5.5-5.5l-2.7 2.7-2.4-.6-.6-2.4 2.7-2.7Z"/>',
    "home": '<path d="M3 11.2 12 4l9 7.2"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5.5h4V20"/>',
    "map": '<path d="M9 4 3 6.2v13.8l6-2.2 6 2.2 6-2.2V4l-6 2.2L9 4Z"/><path d="M9 4v13.8"/><path d="M15 6.2V20"/>',
    "chat": '<path d="M20.5 12a8.5 8.5 0 0 1-12.3 7.6L3.5 21l1.4-4.5A8.5 8.5 0 1 1 20.5 12Z"/>',
    "cube": '<path d="M12 2.5l8.5 4.8v9.4L12 21.5l-8.5-4.8V7.3L12 2.5Z"/><path d="M12 21.5V12"/><path d="M20.5 7.3 12 12 3.5 7.3"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
    "flag": '<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>',
    "rocket": '<path d="M12.5 3.5c3.6-.8 6.6-.8 8 .1.9 1.4.9 4.4.1 8l-6.6 6.6-4.7-4.7 3.2-10Z" transform="rotate(0)"/><path d="M9.3 13.5 5.5 12l2.8-3.6 4.2-.4"/><path d="M10.5 14.7l1.5 3.8 3.6-2.8.4-4.2"/><path d="M6.6 17.4c-1 .5-2 1.7-2.1 3.6 1.9-.1 3.1-1.1 3.6-2.1"/><circle cx="16" cy="8" r="1.5"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z"/><circle cx="12" cy="12" r="3"/>',
    "github": None, "linkedin": None,
}
_GITHUB = ("M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 "
           "0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 "
           "0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 "
           "1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55"
           "-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 "
           "1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z")


def icon(name: str, x: float, y: float, size: float = 24, color: str = "currentColor",
         sw: float = 1.8, extra: str = "") -> str:
    """Icono en (x, y) con lado `size`."""
    s = size / 24
    if name == "github":
        return (f'<g transform="translate({x:g} {y:g}) scale({size/16:g})" {extra}>'
                f'<path d="{_GITHUB}" fill="{color}"/></g>')
    if name == "linkedin":
        return (f'<g transform="translate({x:g} {y:g}) scale({s:g})" {extra}>'
                f'<rect x="2" y="2" width="20" height="20" rx="4.5" fill="{color}"/>'
                f'<circle cx="7.6" cy="7.6" r="1.55" fill="#fff"/><rect x="6.35" y="10" width="2.5" height="7.6" rx=".4" fill="#fff"/>'
                f'<path d="M10.9 10h2.4v1.1c.55-.85 1.6-1.35 2.8-1.35 2.2 0 3.3 1.4 3.3 3.9v3.95h-2.5v-3.6c0-1.25-.5-1.95-1.5-1.95'
                f'-1.05 0-1.65.75-1.65 1.95v3.6h-2.5V10Z" fill="#fff"/></g>')
    inner = ICONS[name]
    return (f'<g transform="translate({x:g} {y:g}) scale({s:g})" fill="none" stroke="{color}" '
            f'stroke-width="{sw / s:.3g}" stroke-linecap="round" stroke-linejoin="round" '
            f'color="{color}" {extra}>{inner}</g>')
