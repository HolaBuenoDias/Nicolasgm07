"""Sobre mí en formato «bento»: ocho teselas que resumen a Nicolás de un vistazo (historia,
cifras, formación, certificaciones, idiomas, stack y la llamada a la acción).

    python scripts/build.py about   →  assets/about/bento-{dark,light}.svg

Rejilla de 4 columnas × 3 filas sin marco exterior; cada tesela es brand.card() (r = 18) y
la separación es de 12 px. Las dos teselas grandes (historia y llamada) mandan y quedan en
diagonal para equilibrar el peso:

    ┌───────────────┬───────┬───────┐
    │               │ T2  6 │ T3 16 │
    │  T1 historia  ├───────┼───────┤
    │               │ T4 DAW│ T5 cer│
    ├───────┬───────┼───────┴───────┤
    │ T7 id │ T8 st │  T6 llamada   │
    └───────┴───────┴───────────────┘
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import (ODOMETER_CSS, TECH, THEMES, brand_gradient, card, dot_grid, esc, icon,  # noqa: E402
                   kicker, odometer, rrect, svg_doc, text_width, write_themed)
import content as C  # noqa: E402

W = 1000
COLS, ROWS, GAP = 4, 3, 12
COL_W = (W - GAP * (COLS - 1)) / COLS          # 241
ROW_H = 164
H = ROWS * ROW_H + (ROWS - 1) * GAP            # 516
PAD = 20                                       # margen interior de las teselas pequeñas
CAP1, CAP2 = 44, 22                            # líneas base de rótulo y subrótulo (desde abajo)

NBSP = " "                                # une palabras que no deben separarse
DEEP = THEMES["light"]["brand_text"]           # naranja profundo (#C2410C): fondo de la llamada bajo el texto blanco

ODO_EASE, ODO_DUR = (.2, .8, .2, 1), 1.6       # misma curva y duración que brand.ODOMETER_CSS
T0, STEP = .08, .08                            # entrada en ola diagonal: T0 + STEP · (columna + fila)

STORY = [  # (texto, destacado) — sacado del CV
    ("Fue en", False), ("Bastilipo:", True), ("durante", False),
    (NBSP.join("1 año y 4 meses".split()), True),
    ("desarrollé y mantuve tiendas online con", False),
    ("WordPress, WooCommerce y" + NBSP + "PrestaShop,", True),
    ("y lo compaginé con " + NBSP.join("1.º de DAW.".split()) + " Ahora curso " + NBSP.join("2.º en".split())
     + " el IES Los" + NBSP + "Alcores.", False),
]
STACK = ["PHP", "Java", "Angular", "Spring Boot", "WordPress"]


# --------------------------------------------------------------------------- helpers
def cell(col, row, cs=1, rs=1):
    """Rectángulo (x, y, w, h) de una tesela que ocupa cs columnas y rs filas."""
    return (col * (COL_W + GAP), row * (ROW_H + GAP),
            cs * COL_W + (cs - 1) * GAP, rs * ROW_H + (rs - 1) * GAP)


def wave(col, row):
    return T0 + STEP * (col + row)


def anim(cls, d):
    return f'class="{cls}" style="animation-delay:{d:.2f}s"'


def tw(s, size, weight=400, mono=False):
    return text_width(s.replace(NBSP, " "), size, weight, mono=mono)


def txt(x, y, s, size, fill, weight=400, *, mono=False, anchor=None, extra=""):
    cls = ' class="mono"' if mono else ""
    a = f' text-anchor="{anchor}"' if anchor else ""
    ex = f" {extra}" if extra else ""
    return (f'<text{cls} x="{x:g}" y="{y:g}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}"{a}{ex}>{esc(s)}</text>')


def bezier_time(progress, curve=ODO_EASE):
    """Fracción de tiempo en la que una cubic-bezier alcanza `progress` (bisección)."""
    x1, y1, x2, y2 = curve
    lo, hi = 0.0, 1.0
    for _ in range(40):
        s = (lo + hi) / 2
        y = 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s ** 2 * y2 + s ** 3
        lo, hi = (s, hi) if y < progress else (lo, s)
    s = (lo + hi) / 2
    return 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s ** 2 * x2 + s ** 3


def odo_at(start, frac):
    """Instante (s) en que el odómetro pasa por la fracción `frac` de su recorrido."""
    return start + ODO_DUR * bezier_time(frac)


def months(start, end):
    y, m = map(int, start.split("-"))
    y2, m2 = map(int, end.split("-"))
    out = []
    while (y, m) <= (y2, m2):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def rich_lines(segments, size, max_w, strong_w=650):
    """Parte un texto con tramos destacados en líneas (voraz y sin huérfanas)."""
    words = [(w, strong) for text, strong in segments for w in text.split(" ") if w]
    space = tw(" ", size)

    def width(ws):
        return sum(tw(w, size, strong_w if s else 400) for w, s in ws) + space * (len(ws) - 1)

    def layout(limit):
        lines, cur = [], []
        for item in words:
            if cur and width(cur + [item]) > limit:
                lines.append(cur)
                cur = [item]
            else:
                cur.append(item)
        return lines + [cur] if cur else lines

    lines = layout(max_w)
    if len(lines) > 1 and len(lines[-1]) < 2:          # evita una palabra sola en la última línea
        lim = max_w
        while lim > max_w * .75:
            lim -= 4
            cand = layout(lim)
            if len(cand) != len(lines):
                break
            if len(cand[-1]) >= 2:
                lines = cand
                break
    assert all(width(l) <= max_w for l in lines), "párrafo desbordado"
    return lines


def rich_text(x, y, lines, p, *, size, lh, strong_w=650, extra=""):
    out = [f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{p["muted"]}" {extra}>']
    for i, line in enumerate(lines):
        runs = []
        for w, s in line:
            if runs and runs[-1][1] == s:
                runs[-1][0].append(w)
            else:
                runs.append(([w], s))
        parts = []
        for j, (ws, s) in enumerate(runs):
            t = esc((" " if j else "") + " ".join(ws))
            parts.append(f'<tspan fill="{p["text"]}" font-weight="{strong_w}">{t}</tspan>' if s else f"<tspan>{t}</tspan>")
        out.append(f'<tspan x="{x:g}" dy="{0 if i == 0 else lh}">{"".join(parts)}</tspan>')
    out.append("</text>")
    return "".join(out)


def captions(x, y, h, p, label, sub=None):
    """Rótulo (y subrótulo mono) alineados abajo: misma línea base en todas las teselas."""
    if sub:
        return (txt(x + PAD, y + h - CAP1, label, 15, p["text"], 600)
                + txt(x + PAD, y + h - CAP2, sub, 13, p["muted"], 500, mono=True))
    return txt(x + PAD, y + h - CAP2, label, 15, p["text"], 600)


def arc(cx, cy, r, a0, a1):
    """Arco en sentido horario; ángulos en grados desde las 12 en punto."""
    def pt(a):
        t = math.radians(a - 90)
        return cx + r * math.cos(t), cy + r * math.sin(t)
    (xa, ya), (xb, yb) = pt(a0), pt(a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{xa:.2f} {ya:.2f}A{r:g} {r:g} 0 {large} 1 {xb:.2f} {yb:.2f}"


# --------------------------------------------------------------------------- teselas
def t1_story(p, x, y, w, h, d):
    """Historia: antetítulo, titular en dos líneas, párrafo y ubicación."""
    px, maxw = x + 32, w - 64
    out = [card(x, y, w, h, p),
           f'<g clip-path="url(#abt1c)"><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#abdots)" '
           f'mask="url(#abt1m)"/><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#abglow)"/></g>']
    out.append(f'<g {anim("fade", d + .12)}>{kicker(px, y + 54, "sobre mí", p, size=13)}</g>')
    t1, t2 = "Empecé en prácticas", "y me quedé contratado."
    assert tw(t2, 36, 800) - 21 * .9 < maxw and tw(t1, 36, 800) < maxw, "titular demasiado ancho"
    out.append(f'<text {anim("rise", d + .18)} x="{px - 2:g}" y="{y + 104:g}" font-size="36" font-weight="800" '
               f'letter-spacing="-.9" fill="{p["text"]}">{esc(t1)}</text>')
    out.append(f'<text {anim("rise", d + .26)} x="{px - 2:g}" y="{y + 148:g}" font-size="36" font-weight="800" '
               f'letter-spacing="-.9" fill="url(#abgrad)">{esc(t2)}</text>')
    lines = rich_lines(STORY, 16, maxw)
    out.append(f'<g {anim("rise", d + .34)}>{rich_text(px, y + 194, lines, p, size=16, lh=25)}</g>')
    last = y + 194 + 25 * (len(lines) - 1)
    fy = y + h - 30
    assert fy - last > 30, "el párrafo choca con el pie"
    out.append(f'<g {anim("fade", d + .42)}>'
               f'<line x1="{px:g}" y1="{fy - 30:g}" x2="{x + w - 32:g}" y2="{fy - 30:g}" stroke="{p["border_soft"] if dark_of(p) else p["border"]}"/>'
               f'{icon("pin", px - 1, fy - 14, 18, p["brand_text"], 1.9)}'
               f'{txt(px + 25, fy, "El Viso del Alcor, Sevilla", 15, p["muted"], 500)}</g>')
    return "".join(out)


def dark_of(p):
    return p is THEMES["dark"]


def t2_sites(p, x, y, w, h, d):
    """6 tiendas y webs: odómetro + seis ventanitas apiladas que caen al ritmo del contador."""
    start = d + .32
    num, nw = odometer(x + PAD - 2, y + 62, "6", p, uid="abo6", size=58, start=start)
    out = [card(x, y, w, h, p), num]
    # cascada: de atrás (arriba a la derecha) a delante (abajo a la izquierda)
    n, ww, wh, dx, dy = 6, 100, 60, 8.6, 5.4
    fx, fy = x + w - PAD - ww - (n - 1) * dx, y + PAD - 2 + (n - 1) * dy
    assert fx > x + PAD + nw + 14, "la cascada choca con el número"
    for j in range(n):
        k = n - 1 - j                                     # 0 = delante
        wx, wy = fx + k * dx, fy - k * dy
        front = k == 0
        t = odo_at(start, (j + 1) / n) - .12
        win = [rrect(wx, wy, ww, wh, 7, p["raised"], p["border"])]
        if front:
            win.append(f'<line x1="{wx:g}" y1="{wy + 13:g}" x2="{wx + ww:g}" y2="{wy + 13:g}" stroke="{p["border"]}"/>')
            win.extend(f'<circle cx="{wx + 9 + i * 7:g}" cy="{wy + 6.8:g}" r="2.2" fill="{c}"/>'
                       for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")))
            win.append(rrect(wx + 34, wy + 4, 52, 6, 3, p["surface"], p["border_soft"]))
            # mini tienda: banner + tres productos
            win.append(rrect(wx + 8, wy + 19, ww - 16, 11, 3, p["brand_soft"]))
            win.append(rrect(wx + 12, wy + 23, 30, 3, 1.5, p["brand"]))
            for i in range(3):
                bx = wx + 8 + i * 29
                win.append(rrect(bx, wy + 35, 26, 17, 3, p["surface"], p["border_soft"]))
                win.append(rrect(bx + 4, wy + 46, 12, 3, 1.5, p["brand"] if i == 1 else p["border"]))
        else:
            win.extend(f'<circle cx="{wx + 8 + i * 6:g}" cy="{wy + 5.5:g}" r="1.8" fill="{p["border"]}"/>'
                       for i in range(3))
        out.append(f'<g {anim("win", t)}>{"".join(win)}</g>')
    out.append(captions(x, y, h, p, "tiendas y webs corporativas", "con WordPress y PrestaShop"))
    return "".join(out)


def t3_months(p, x, y, w, h, d):
    """16 meses en Bastilipo: odómetro + calendario 2025/2026 que se rellena mes a mes."""
    E = C.EXPERIENCE
    ms = months(E["start"], E["end"])
    assert len(ms) == 16
    start = d + .32
    num, nw = odometer(x + PAD - 2, y + 62, str(len(ms)), p, uid="abo16", size=58, start=start)
    out = [card(x, y, w, h, p), num]
    years = sorted({yy for yy, _ in ms})
    cols, g = 12, 3
    cw = (w - 2 * PAD - g * (cols - 1)) / cols
    gy = y + 76
    for r, yr in enumerate(years):
        for c in range(cols):
            out.append(rrect(x + PAD + c * (cw + g), gy + r * (cw + g), cw, cw, 3, p["border_soft"]))
    for i, (yr, m) in enumerate(ms):
        cx_, cy_ = x + PAD + (m - 1) * (cw + g), gy + years.index(yr) * (cw + g)
        out.append(f'<rect {anim("cellpop", odo_at(start, (i + 1) / len(ms)) - .1)} x="{cx_:g}" y="{cy_:g}" '
                   f'width="{cw:g}" height="{cw:g}" rx="3" fill="url(#abmonth)"/>')
    out.append(captions(x, y, h, p, "meses en Bastilipo", E["period"]))
    return "".join(out)


def t4_daw(p, x, y, w, h, d):
    """2.º DAW: titular + anillo decorativo de dos tramos (1.º hecho, 2.º en curso)."""
    out = [card(x, y, w, h, p)]
    out.append(f'<text x="{x + PAD - 1:g}" y="{y + 52:g}" font-size="31" font-weight="800" letter-spacing="-.6" '
               f'fill="{p["text"]}">2.º DAW</text>')
    out.append(txt(x + PAD, y + 76, "Desarrollo de", 14, p["muted"], 500))
    out.append(txt(x + PAD, y + 94, "Aplicaciones Web", 14, p["muted"], 500))
    r, sw = 27, 7
    cx, cy = x + w - PAD - r - sw / 2, y + PAD + r + sw / 2
    assert cx - r - sw / 2 - (x + PAD + tw("2.º DAW", 31, 800)) > 10, "el anillo choca con el texto"
    gap = 13
    out.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r}" stroke="{p["border_soft"]}" stroke-width="{sw}"/>')
    out.append(f'<path {anim("arc", d + .5)} pathLength="1" d="{arc(cx, cy, r, gap, 180 - gap)}" '
               f'stroke="url(#abring)" stroke-width="{sw}" stroke-linecap="round"/>')
    out.append(f'<path {anim("arc", d + 1.15)} pathLength="1" d="{arc(cx, cy, r, 180 + gap, 360 - gap)}" '
               f'stroke="{p["brand_line"]}" stroke-width="{sw}" stroke-linecap="round"/>')
    out.append(f'<g {anim("pop", d + .7)}>{icon("cap", cx - 11, cy - 11, 22, p["brand_text"], 1.9)}</g>')
    out.append(captions(x, y, h, p, "IES Los Alcores", "promoción 2027"))
    return "".join(out)


def t5_certs(p, x, y, w, h, d):
    """Certificaciones: dos insignias (Analytics y Ads)."""
    out = [card(x, y, w, h, p)]
    pw, ph = w - 2 * PAD, 34
    for i, c in enumerate(C.CERTS):
        py = y + PAD + i * (ph + 10)
        out.append(f'<g {anim("pop", d + .35 + i * .1)}>'
                   f'{rrect(x + PAD, py, pw, ph, ph / 2, p["brand_soft"], p["brand_line"])}'
                   f'{icon("award", x + PAD + 9, py + 7, 20, p["brand_text"], 1.9)}'
                   f'{txt(x + PAD + 36, py + 22, c["name"], 15, p["text"], 650)}'
                   f'{icon("check", x + PAD + pw - 28, py + 9, 16, p["brand_text"], 2.4)}</g>')
    out.append(captions(x, y, h, p, "Certificaciones de Google", "verificables en LinkedIn"))
    return "".join(out)


def t7_langs(p, x, y, w, h, d):
    """Idiomas: teclas ES / EN con nivel."""
    out = [card(x, y, w, h, p)]
    rows = [("ES", "Español", "nativo"), ("EN", "Inglés", "lectura técnica fluida")]
    for i, (code, name, level) in enumerate(rows):
        ry = y + PAD + i * 48
        kx = x + PAD
        out.append(f'<g {anim("rise", d + .3 + i * .08)}>'
                   f'{rrect(kx, ry, 36, 36, 9, p["raised"], p["border"])}'
                   f'{rrect(kx + 3, ry + 31, 30, 2, 1, p["border_soft"])}'
                   f'{txt(kx + 18, ry + 22.5, code, 13, p["brand_text"], 700, mono=True, anchor="middle")}'
                   f'{txt(kx + 50, ry + 15, name, 16, p["text"], 700)}'
                   f'{txt(kx + 50, ry + 34, level, 14, p["muted"], 400)}</g>')
        assert kx + 50 + tw(level, 14) < x + w - PAD
    out.append(captions(x, y, h, p, "Idiomas"))
    return "".join(out)


def t8_stack(p, x, y, w, h, d):
    """Stack principal: mini-chips con los puntos de color de GitHub."""
    out = [card(x, y, w, h, p)]
    cx, cy, ch, gx, gy = x + PAD, y + PAD - 4, 25, 6, 6
    i = 0
    for name in STACK:
        cw = 10 + 13 + tw(name, 12.5, 600) + 10
        if cx + cw > x + w - PAD:
            cx, cy = x + PAD, cy + ch + gy
        out.append(f'<g {anim("pop", d + .3 + i * .06)}>'
                   f'{rrect(cx, cy, cw, ch, ch / 2, p["raised"], p["border"])}'
                   f'<circle cx="{cx + 13:g}" cy="{cy + ch / 2:g}" r="4" fill="{TECH[name]}"/>'
                   f'{txt(cx + 22, cy + ch / 2 + 4.5, name, 12.5, p["text"], 600)}</g>')
        cx += cw + gx
        i += 1
    assert cy + ch < y + h - CAP2 - 26, "los chips chocan con el rótulo"
    out.append(captions(x, y, h, p, "Stack principal"))
    return "".join(out)


def t6_cta(p, x, y, w, h, d):
    """Llamada a la acción: degradado de marca, texto blanco, punto que late y flecha."""
    wh = p["on_brand"]
    out = [f'<g filter="url(#abctash)">{rrect(x, y, w, h, 18, "url(#abcta)")}</g>',
           f'<g clip-path="url(#abctac)">'
           f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#abctaglow)"/>'
           f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#abctadots)" mask="url(#abctam)"/>']
    bx, by, br = x + w - 32 - 28, y + h / 2, 28
    for i, rr in enumerate((48, 72, 98)):
        out.append(f'<circle cx="{bx:g}" cy="{by:g}" r="{rr}" stroke="{wh}" stroke-opacity="{(.26, .17, .1)[i]}" '
                   f'stroke-width="1.2"/>')
    out.append(f'<path class="shine" d="M{x - 140:g} {y:g}h70l-50 {h:g}h-70Z" fill="url(#abshine)"/></g>')
    out.append(rrect(x + .5, y + .5, w - 1, h - 1, 17.5, "none", wh, 1, 'stroke-opacity=".18"'))
    # texto
    tx = x + 30
    pill = "DISPONIBLE"
    pwid = 30 + tw(pill, 13, mono=True) + 13 * .12 * (len(pill) - 1) + 12
    out.append(f'<g {anim("fade", d + .3)}>{rrect(tx, y + 26, pwid, 26, 13, DEEP, wh, 1, "stroke-opacity=\".3\"")}'
               f'<circle class="ping" style="animation-delay:{d + 1:.2f}s" cx="{tx + 15:g}" cy="{y + 39:g}" r="4" fill="{wh}"/>'
               f'<circle cx="{tx + 15:g}" cy="{y + 39:g}" r="4" fill="{wh}"/>'
               f'<text class="mono" x="{tx + 27:g}" y="{y + 43.5:g}" font-size="13" font-weight="700" letter-spacing="1.6" '
               f'fill="{wh}">{pill}</text></g>')
    out.append(f'<text {anim("rise", d + .36)} x="{tx - 2:g}" y="{y + 98:g}" font-size="38" font-weight="800" '
               f'letter-spacing="-1" fill="{wh}">Busco prácticas</text>')
    sub = "De febrero a mayo de 2027 · 2.º DAW"
    assert tx + tw(sub, 16, 600) < bx - br - 20, "el subtítulo choca con la flecha"
    out.append(f'<text {anim("rise", d + .44)} x="{tx:g}" y="{y + 130:g}" font-size="16" font-weight="600" '
               f'fill="{wh}">{esc(sub)}</text>')
    # botón con flecha
    out.append(f'<g {anim("pop", d + .55)}><circle cx="{bx:g}" cy="{by:g}" r="{br}" fill="{wh}"/>'
               f'<g class="nudge" style="animation-delay:{d + 2.2:.2f}s">'
               f'{icon("arrow", bx - 12, by - 12, 24, DEEP, 2.4)}</g></g>')
    return "".join(out)


# --------------------------------------------------------------------------- documento
def build(theme, p):
    dark = theme == "dark"
    t1 = cell(0, 0, 2, 2)
    t6 = cell(2, 2, 2, 1)
    x1, y1, w1, h1 = t1
    x6, y6, w6, h6 = t6
    msx = cell(3, 0)[0] + PAD
    defs = [
        f'<clipPath id="abt1c"><rect x="{x1 + .5:g}" y="{y1 + .5:g}" width="{w1 - 1:g}" height="{h1 - 1:g}" rx="18"/></clipPath>',
        dot_grid("abdots", p["grid"], 22, 1.1, .8 if dark else .95),
        f'<radialGradient id="abt1g" cx="100%" cy="0%" r="70%">'
        f'<stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<mask id="abt1m"><rect x="{x1:g}" y="{y1:g}" width="{w1:g}" height="{h1:g}" fill="url(#abt1g)"/></mask>',
        f'<radialGradient id="abglow" cx="96%" cy="0%" r="75%">'
        f'<stop offset="0" stop-color="{p["brand"]}" stop-opacity="{.2 if dark else .11}"/>'
        f'<stop offset=".6" stop-color="{p["brand"]}" stop-opacity="{.04 if dark else .025}"/>'
        f'<stop offset="1" stop-color="{p["brand"]}" stop-opacity="0"/></radialGradient>',
        brand_gradient("abgrad", p),
        brand_gradient("abring", p, x2="0%", y2="100%"),
        f'<linearGradient id="abmonth" gradientUnits="userSpaceOnUse" x1="{msx:g}" y1="0" x2="{msx + COL_W - 2 * PAD:g}" y2="0">'
        f'<stop offset="0" stop-color="{p["grad_a"]}"/><stop offset="1" stop-color="{p["grad_b"]}"/></linearGradient>',
        # llamada: naranja profundo bajo el texto, ámbar solo en la esquina de la flecha
        f'<linearGradient id="abcta" x1="0" y1="1" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{DEEP}"/><stop offset="1" stop-color="{p["brand"]}"/></linearGradient>',
        f'<radialGradient id="abctaglow" cx="92%" cy="10%" r="62%">'
        f'<stop offset="0" stop-color="{p["grad_a"]}" stop-opacity=".95"/>'
        f'<stop offset=".55" stop-color="{p["grad_a"]}" stop-opacity=".25"/>'
        f'<stop offset="1" stop-color="{p["grad_a"]}" stop-opacity="0"/></radialGradient>',
        f'<clipPath id="abctac"><rect x="{x6:g}" y="{y6:g}" width="{w6:g}" height="{h6:g}" rx="18"/></clipPath>',
        dot_grid("abctadots", p["on_brand"], 18, 1.1, .32),
        f'<radialGradient id="abctamg" cx="100%" cy="50%" r="70%">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<mask id="abctam"><rect x="{x6:g}" y="{y6:g}" width="{w6:g}" height="{h6:g}" fill="url(#abctamg)"/></mask>',
        f'<linearGradient id="abshine" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<filter id="abctash" x="-10%" y="-20%" width="120%" height="150%">'
        f'<feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="{p["brand"]}" flood-opacity="{.32 if dark else .26}"/></filter>',
    ]
    css = ODOMETER_CSS + f"""
    .win{{animation:win .55s cubic-bezier(.2,.9,.3,1.15) backwards}}
    @keyframes win{{from{{opacity:0;transform:translate(9px,-9px)}}}}
    .cellpop{{animation:cellpop .38s cubic-bezier(.2,1.4,.4,1) backwards;transform-box:fill-box;transform-origin:center}}
    @keyframes cellpop{{from{{opacity:0;transform:scale(.3)}}}}
    .arc{{stroke-dasharray:1;animation:draw .85s cubic-bezier(.55,0,.3,1) backwards}}
    .nudge{{animation:nudge 2.6s ease-in-out infinite}}
    @keyframes nudge{{0%,55%,100%{{transform:none}}25%{{transform:translateX(4px)}}}}
    .shine{{animation:shine 7s 2.4s cubic-bezier(.45,0,.3,1) infinite backwards}}
    @keyframes shine{{0%{{transform:translateX(0)}}22%,100%{{transform:translateX({w6 + 260:g}px)}}}}
    """
    tiles = [
        ((0, 0), t1_story, t1),
        ((2, 0), t2_sites, cell(2, 0)),
        ((3, 0), t3_months, cell(3, 0)),
        ((2, 1), t4_daw, cell(2, 1)),
        ((3, 1), t5_certs, cell(3, 1)),
        ((0, 2), t7_langs, cell(0, 2)),
        ((1, 2), t8_stack, cell(1, 2)),
        ((2, 2), t6_cta, t6),
    ]
    body = []
    for (c, r), fn, rect in tiles:
        d = wave(c, r)
        body.append(f'<g {anim("rise", d)}>{fn(p, *rect, d)}</g>')

    E = C.EXPERIENCE
    title = (f"Sobre mí: {C.NAME}, desarrollador web y e-commerce de {C.LOCATION}. "
             "Busco prácticas de febrero a mayo de 2027.")
    desc = ("Resumen en ocho teselas. Empecé en prácticas y me quedé contratado: en Bastilipo desarrollé y "
            "mantuve tiendas online con WordPress, WooCommerce y PrestaShop durante 1 año y 4 meses y lo "
            "compaginé con 1.º de DAW. 6 tiendas y webs corporativas. "
            f"{len(months(E['start'], E['end']))} meses en Bastilipo ({E['period']}). "
            "2.º de DAW en el IES Los Alcores, promoción 2027. Certificaciones de Google: Google Analytics y "
            "Google Ads. Idiomas: español nativo; inglés con lectura técnica fluida. Stack principal: "
            + ", ".join(STACK[:-1]) + f" y {STACK[-1]}. Busco prácticas de febrero a mayo de 2027 (2.º DAW). "
            "Vivo en El Viso del Alcor (Sevilla).")
    return svg_doc(W, H, "".join(body), title=title, desc=desc, css=css, defs="".join(defs))


def main():
    return write_themed("about/bento", build)


if __name__ == "__main__":
    for path in main():
        print(path)
