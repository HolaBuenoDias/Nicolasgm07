"""Tarjetas SVG dinámicas (estadísticas, lenguajes y cuenta atrás) con el sistema de diseño
de brand.py. Cada función recibe (tema, paleta, …) y devuelve el documento SVG completo.

Medidas: stats a ancho completo (viewBox 1000) y langs + countdown a medio ancho (490), las
dos con la misma altura para ir lado a lado con width="49%". Los márgenes (40) y las líneas
base de cabecera (41) y pie (232) coinciden entre tarjetas para que el bloque se lea como uno.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import (ODOMETER_CSS, TECH, brand_gradient, dot_grid, esc, icon,  # noqa: E402
                   kicker, rrect, shadow_filter, svg_doc, text_width)
import content as C  # noqa: E402

# ------------------------------------------------------------------- formato es-ES
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
MES_ABR = ["ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sep.", "oct.", "nov.", "dic."]
MES_EJE = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

# Ciclo DAW (curso escolar en Andalucía) y prácticas de empresa (content.py).
DAW_START = dt.date(2025, 9, 15)
DAW_END = dt.date(2027, 6, 23)
PRACT_START = dt.date.fromisoformat(C.AVAILABILITY["start"])
PRACT_END = dt.date.fromisoformat(C.AVAILABILITY["end"])

# Colores de linguist para lenguajes que no están en brand.TECH.
LINGUIST = {
    "SCSS": "#c6538c", "Sass": "#a53b70", "Less": "#1d365d", "Vue": "#41b883", "Svelte": "#ff3e00",
    "Python": "#3572a5", "Kotlin": "#a97bff", "C#": "#178600", "C++": "#f34b7d", "C": "#555555",
    "Go": "#00add8", "Rust": "#dea584", "Ruby": "#701516", "Dart": "#00b4ab", "Swift": "#f05138",
    "Blade": "#f7523f", "Twig": "#c1d026", "Smarty": "#f0c040", "Hack": "#878787", "TSQL": "#e38c00",
    "PLpgSQL": "#336790", "PLSQL": "#dad8d8", "Jupyter Notebook": "#da5b0b", "Markdown": "#083fa1",
    "Shell": "#89e051", "Batchfile": "#c1f12e", "PowerShell": "#012456", "Dockerfile": "#384d54",
    "EJS": "#a91e50", "Handlebars": "#f7931e", "Pug": "#a86454", "MDX": "#fcb32c", "Astro": "#ff5a03",
    "Groovy": "#4298b8", "Scala": "#c22d40", "Lua": "#000080", "R": "#198ce7", "Perl": "#0298c3",
    "Objective-C": "#438eff", "Assembly": "#6e4c13", "Makefile": "#427819", "JSON": "#292929",
}

W_HALF, H_HALF = 490, 264        # tarjetas a medio ancho
TILE_W, TILE_H = 52, 68          # fichas de la cuenta atrás
PAD = 40                         # margen lateral común
HEAD_Y, FOOT_Y = 41, 236         # líneas base de cabecera y pie


def lang_color(name: str) -> str:
    return TECH.get(name) or LINGUIST.get(name) or "#8b949e"


def num(n: int) -> str:
    """1234 → 1234 · 12345 → 12.345 (en español no se separan los números de 4 cifras)."""
    return f"{n:,}".replace(",", ".") if n >= 10000 else str(n)


def pct(v: float) -> str:
    """Porcentaje a la española: 55,0 % (con espacio fino irrompible)."""
    if 0 < v < 0.05:
        return "<0,1 %"
    return f"{v:.1f}".replace(".", ",") + " %"


def dias(n: int) -> str:
    return "día" if n == 1 else "días"


def fecha_corta(d: dt.date, ref_year: int | None = None) -> str:
    s = f"{d.day} {MES_ABR[d.month - 1]}"
    return s if d.year == ref_year else f"{s} {d.year}"


def rango(a: dt.date, b: dt.date, ref_year: int) -> str:
    year = "" if a.year == b.year == ref_year else f" {b.year}"
    if a == b:
        return fecha_corta(a, ref_year)
    if (a.year, a.month) == (b.year, b.month):
        return f"{a.day}–{b.day} {MES_ABR[a.month - 1]}{year}"
    if a.year == b.year:
        return f"{a.day} {MES_ABR[a.month - 1]} – {b.day} {MES_ABR[b.month - 1]}{year}"
    return f"{fecha_corta(a)} – {fecha_corta(b)}"


def fit(s: str, size: float, max_w: float, weight: int = 400, mono: bool = False) -> str:
    """Recorta con «…» si no cabe."""
    if text_width(s, size, weight, mono) <= max_w:
        return s
    while s and text_width(s + "…", size, weight, mono) > max_w:
        s = s[:-1]
    return s.rstrip() + "…"


# ----------------------------------------------------------------------- piezas
def frame(w, h, r, p, dark, *, glow=("88%", "0%"), glow_r="70%", dots_at=("100%", "0%")):
    """Fondo de tarjeta (canvas + rejilla de puntos que se desvanece + brillo de marca + borde)."""
    defs = (f'<clipPath id="card"><rect x=".5" y=".5" width="{w-1:g}" height="{h-1:g}" rx="{r}"/></clipPath>'
            f'<radialGradient id="glow" cx="{glow[0]}" cy="{glow[1]}" r="{glow_r}">'
            f'<stop offset="0" stop-color="{p["brand"]}" stop-opacity="{.20 if dark else .12}"/>'
            f'<stop offset=".6" stop-color="{p["brand"]}" stop-opacity="{.035 if dark else .025}"/>'
            f'<stop offset="1" stop-color="{p["brand"]}" stop-opacity="0"/></radialGradient>'
            + dot_grid("dots", p["grid"], 22, 1.1, .7 if dark else .85)
            + f'<radialGradient id="dotfade" cx="{dots_at[0]}" cy="{dots_at[1]}" r="75%">'
              f'<stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
              f'</radialGradient><mask id="dotmask"><rect width="{w}" height="{h}" fill="url(#dotfade)"/></mask>')
    body = (f'<g clip-path="url(#card)">{rrect(0, 0, w, h, r, p["canvas"])}'
            f'<rect width="{w}" height="{h}" fill="url(#dots)" mask="url(#dotmask)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#glow)"/></g>'
            + rrect(.5, .5, w - 1, h - 1, r, "none", p["border"]))
    return defs, body


def header(x, y, ic, label, p, *, right: str = "", right_x: float | None = None) -> str:
    """Icono + antetítulo en mono mayúsculas (+ texto opcional alineado a la derecha)."""
    ico = ic(x, y - 14, 18, p["brand_text"], 2.1) if callable(ic) else icon(ic, x, y - 14, 18, p["brand_text"], 2.1)
    out = f'<g class="fade">{ico}{kicker(x + 26, y, label, p, size=13)}'
    if right:
        out += right if right.startswith("<") else (
            f'<text x="{right_x:g}" y="{y}" font-size="13" fill="{p["muted"]}" text-anchor="end">{esc(right)}</text>')
    return out + "</g>"


def head_chip(x1, y, label, p) -> str:
    """Pastilla discreta alineada a la derecha de la cabecera."""
    cw = text_width(label, 13, 500) + 22
    return (rrect(x1 - cw, y - 18, cw, 24, 12, p["surface"], p["border"])
            + f'<text x="{x1 - cw / 2:g}" y="{y - 1.5}" font-size="13" font-weight="500" '
              f'fill="{p["muted"]}" text-anchor="middle">{esc(label)}</text>')


def flame(x, y, size, color, sw=1.9):
    s = size / 24
    return (f'<g transform="translate({x:g} {y:g}) scale({s:g})" fill="none" stroke="{color}" '
            f'stroke-width="{sw / s:.3g}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M12 21.5c-3.9 0-7-2.9-7-6.8 0-2.7 1.5-4.6 3-6 .3 1.9 1.4 2.9 2.4 3.2-.5-3.4 1.2-6.6 '
            f'4.4-8.9.2 2.9 1.6 4.7 3 6.3 1.2 1.3 1.7 2.9 1.7 4.7 0 4.2-3.3 7.5-7.5 7.5Z"/>'
            f'<path d="M12 21.5c-1.7 0-3-1.3-3-3 0-1.5 1-2.4 2-3.3.2 1 .8 1.6 1.5 1.8.4-1 .9-1.8 1.6-2.4.5 1 1 1.9 1 3.4 '
            f'0 1.9-1.4 3.5-3.1 3.5Z"/></g>')


def commit_icon(x, y, size, color, sw=1.9):
    s = size / 24
    return (f'<g transform="translate({x:g} {y:g}) scale({s:g})" fill="none" stroke="{color}" '
            f'stroke-width="{sw / s:.3g}" stroke-linecap="round">'
            f'<circle cx="12" cy="12" r="4"/><path d="M2.5 12H8"/><path d="M16 12h5.5"/></g>')


def hourglass(x, y, size, color, sw=1.9):
    """Reloj de arena (mismo estilo de línea que brand.ICONS)."""
    s = size / 24
    return (f'<g transform="translate({x:g} {y:g}) scale({s:g})" fill="none" stroke="{color}" '
            f'stroke-width="{sw / s:.3g}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M6 3h12"/><path d="M6 21h12"/>'
            f'<path d="M7.5 3v2.6c0 1.6.8 3 2.1 3.9L12 11l2.4-1.5a4.6 4.6 0 0 0 2.1-3.9V3"/>'
            f'<path d="M7.5 21v-2.6c0-1.6.8-3 2.1-3.9L12 13l2.4 1.5a4.6 4.6 0 0 1 2.1 3.9V21"/></g>')


def roll(x, y, value: str, *, uid: str, size: float, fill: str, weight: int = 800,
         start: float = .2, stagger: float = .08) -> tuple[str, float]:
    """Como brand.odometer, pero con la ventana ajustada a la altura de las cifras y más
    separación entre ellas: mientras ruedan no asoman por encima ni por debajo."""
    dw = text_width("0", size, weight)
    lh = size * 1.25
    total = sum(dw if ch.isdigit() else text_width(ch, size, weight) for ch in value)
    out = [f'<clipPath id="{uid}"><rect x="{x - 4:g}" y="{y - size * .84:g}" width="{total + 8:g}" '
           f'height="{size * 1.02:g}"/></clipPath><g clip-path="url(#{uid})">']
    cx, i = x, 0
    for ch in value:
        if ch.isdigit():
            d = int(ch)
            col = "".join(f'<text x="{cx:g}" y="{y + k * lh:g}" font-size="{size}" font-weight="{weight}" '
                          f'fill="{fill}">{k}</text>' for k in range(d + 1))
            out.append(f'<g class="odo" style="transform:translateY({-d * lh:g}px);'
                       f'animation-delay:{start + i * stagger:.2f}s">{col}</g>')
            cx += dw
            i += 1
        else:
            out.append(f'<text x="{cx:g}" y="{y:g}" font-size="{size}" font-weight="{weight}" fill="{fill}">{esc(ch)}</text>')
            cx += text_width(ch, size, weight)
    out.append("</g>")
    return "".join(out), total


# -------------------------------------------------------------------- curvas
def _sign(v):
    return (v > 0) - (v < 0)


def monotone_path(pts) -> str:
    """Curva cúbica monótona (método de Steffen, como d3.curveMonotoneX): no se sale por debajo
    de cero ni inventa picos que no existen."""
    n = len(pts)
    if n == 1:
        return f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    sec = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [0.0] * n
    for i in range(1, n - 1):
        h0, h1 = xs[i] - xs[i - 1], xs[i + 1] - xs[i]
        s0, s1 = sec[i - 1], sec[i]
        pp = (s0 * h1 + s1 * h0) / (h0 + h1)
        m[i] = (_sign(s0) + _sign(s1)) * min(abs(s0), abs(s1), 0.5 * abs(pp))
    for i, j in ((0, 1), (n - 1, n - 2)):
        s = sec[min(i, j)]
        t = (3 * s - m[j]) / 2
        m[i] = 0 if _sign(t) != _sign(s) else (3 * s if abs(t) > 3 * abs(s) else t)
    d = [f"M{xs[0]:.1f} {ys[0]:.1f}"]
    for i in range(n - 1):
        h = (xs[i + 1] - xs[i]) / 3
        d.append(f"C{xs[i] + h:.1f} {ys[i] + m[i] * h:.1f} {xs[i + 1] - h:.1f} {ys[i + 1] - m[i + 1] * h:.1f} "
                 f"{xs[i + 1]:.1f} {ys[i + 1]:.1f}")
    return "".join(d)


# ================================================================== estadísticas
def stats_svg(theme: str, p: dict, stats: dict, data: dict, today: dt.date) -> str:
    dark = theme == "dark"
    W, H = 1000, 308
    X0, X1 = PAD, 1000 - PAD
    fdefs, fbody = frame(W, H, 22, p, dark, glow=("92%", "-10%"), glow_r="60%", dots_at=("100%", "0%"))
    defs = [fdefs, brand_gradient("bg", p),
            f'<linearGradient id="area" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="{.62 if dark else .5}"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
            shadow_filter("shs", p["shadow"], 4, 10)]
    css = ODOMETER_CSS + f"""
    .wipe{{animation:wipe 1.6s cubic-bezier(.45,.05,.25,1) .55s backwards;transform-origin:{X0}px 0}}
    @keyframes wipe{{from{{transform:scaleX(0)}}}}
    """
    b = [fbody]

    # ---- cabecera
    user = f'@{data["user"]}'
    ux = X0 + 26 + text_width("ACTIVIDAD EN GITHUB", 13, mono=True, tracking=1.6 / 13) + 14
    upd = f"Actualizado el {today:%d/%m/%Y}"
    uw = text_width(upd, 13)
    b.append(header(X0, HEAD_Y, commit_icon, "Actividad en GitHub", p,
                    right=f'<text class="mono" x="{ux:g}" y="{HEAD_Y}" font-size="13" fill="{p["muted"]}">{esc(user)}</text>'
                          f'<circle class="ping" cx="{X1 - uw - 14:g}" cy="{HEAD_Y - 4.5}" r="4" fill="{p["success"]}"/>'
                          f'<circle cx="{X1 - uw - 14:g}" cy="{HEAD_Y - 4.5}" r="4" fill="{p["success"]}"/>'
                          f'<text x="{X1}" y="{HEAD_Y}" font-size="13" fill="{p["muted"]}" text-anchor="end">{esc(upd)}</text>'))

    # ---- KPIs
    end = stats["end"]
    cur, best = stats["current"], stats["longest"]
    if cur["days"]:
        if cur["start"] == end:
            cur_sub = "con actividad hoy"
        elif cur["start"] == end - dt.timedelta(days=1):
            cur_sub = "desde ayer"
        else:
            cur_sub = f"desde el {fecha_corta(cur['start'], end.year)}"
    elif stats["last_active"]:
        cur_sub = f"último día activo: {fecha_corta(stats['last_active'], end.year)}"
    else:
        cur_sub = "aún sin actividad"
    best_sub = rango(best["start"], best["end"], end.year) if best["days"] else "aún sin rachas"
    kpis = [
        (commit_icon, "Contribuciones", num(stats["total"]), "", "en el último año"),
        (flame, "Racha actual", str(cur["days"]), dias(cur["days"]), cur_sub),
        ("award", "Racha máxima", str(best["days"]), dias(best["days"]), best_sub),
        ("folder", "Repos públicos", num(data["public_repos"]), "", None),
    ]
    TW, TH, TY, GAP = 218, 100, 62, 16
    for i, (ic, label, value, unit, sub) in enumerate(kpis):
        x = X0 + i * (TW + GAP)
        g = [f'<g class="rise" style="animation-delay:{.12 + i * .08:.2f}s">',
             rrect(x + .5, TY + .5, TW - 1, TH - 1, 14, p["surface"], p["border_soft"])]
        ix, iy = x + TW - 40, TY + 14
        g.append(rrect(ix, iy, 26, 26, 8, p["brand_soft"]))
        g.append(ic(ix + 5, iy + 5, 16, p["brand_text"], 2) if callable(ic) else icon(ic, ix + 5, iy + 5, 16, p["brand_text"], 2))
        g.append(f'<text x="{x + 18}" y="{TY + 31}" font-size="14" font-weight="600" fill="{p["muted"]}">{esc(label)}</text>')
        ov, vw = roll(x + 17, TY + 70, value, uid=f"k{i}", size=38, fill=p["text"], start=.35 + i * .1)
        g.append(ov)
        if unit:
            g.append(f'<text x="{x + 17 + vw + 7:g}" y="{TY + 70}" font-size="17" font-weight="600" fill="{p["muted"]}">{unit}</text>')
        if sub is None:  # repos: último push
            pre = "último push: "
            pw = text_width(pre, 13)
            repo = fit(data.get("last_push") or "—", 13, TW - 36 - pw, mono=True)
            g.append(f'<text x="{x + 18}" y="{TY + 89}" font-size="13" fill="{p["subtle"]}">{pre}'
                     f'<tspan class="mono" fill="{p["muted"]}">{esc(repo)}</tspan></text>')
        else:
            g.append(f'<text x="{x + 18}" y="{TY + 89}" font-size="13" fill="{p["subtle"]}">{esc(fit(sub, 13, TW - 36))}</text>')
        g.append("</g>")
        b.append("".join(g))

    # ---- gráfico de área: contribuciones por semana
    weekly = stats["weekly"]
    vals = [w_["total"] for w_ in weekly]
    top, base = 196, 262
    vmax = max(vals) or 1
    n = len(vals)
    step = (X1 - X0) / max(n - 1, 1)
    pts = [(X0 + i * step, base - (v / vmax) * (base - top)) for i, v in enumerate(vals)]
    line = monotone_path(pts)
    area = f"{line}L{pts[-1][0]:.1f} {base}L{pts[0][0]:.1f} {base}Z"
    defs.append(f'<mask id="areamask"><path d="{area}" fill="url(#area)"/></mask>'
                f'<clipPath id="reveal"><rect class="wipe" x="{X0 - 8}" y="{top - 24}" width="{X1 - X0 + 16}" height="{base - top + 30}"/></clipPath>')
    # rejilla: mitad + máximo
    for frac in (0.5, 1.0):
        y = base - frac * (base - top)
        b.append(f'<line x1="{X0}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" stroke="{p["border"]}" stroke-dasharray="2 5" '
                 f'stroke-opacity=".8"/>')
    b.append(f'<line x1="{X0}" y1="{base + .5}" x2="{X1}" y2="{base + .5}" stroke="{p["border"]}"/>')
    b.append(f'<g clip-path="url(#reveal)"><rect x="{X0}" y="{top - 10}" width="{X1 - X0}" height="{base - top + 10}" '
             f'fill="url(#bg)" mask="url(#areamask)"/>'
             f'<path d="{line}" stroke="url(#bg)" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/></g>')
    # puntos en las semanas con actividad (aparecen al paso del barrido)
    imax = max(range(n), key=lambda i: (vals[i], i))
    dots = []
    for i, (x, y) in enumerate(pts):
        if vals[i] and i not in (imax, n - 1):
            d = .55 + 1.6 * (x - X0) / (X1 - X0) * .8
            dots.append(f'<circle class="pop" style="animation-delay:{d:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="3" '
                        f'fill="{p["canvas"]}" stroke="{p["brand"]}" stroke-width="1.8"/>')
    b.append("".join(dots))
    # última semana: punto vivo
    lx, ly = pts[-1]
    b.append(f'<g class="pop" style="animation-delay:2.1s"><circle class="ping" cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{p["brand"]}"/>'
             f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{p["brand"]}" stroke="{p["canvas"]}" stroke-width="2"/></g>')
    # pico anotado
    if vals[imax] > 0:
        px, py = pts[imax]
        wk = weekly[imax]["start"]
        label = f"{vals[imax]} en la semana del {fecha_corta(wk, end.year)}"
        lw = text_width(label, 13, 600) + 24
        right = px + 14 + lw <= X1
        bx = px + 14 if right else px - 14 - lw
        by = max(py - 13, top - 18)
        b.append(f'<g class="pop" style="animation-delay:2.2s">'
                 f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{p["brand"]}" stroke="{p["canvas"]}" stroke-width="2"/>'
                 f'<g filter="url(#shs)">{rrect(bx, by, lw, 26, 13, p["raised"], p["border"])}</g>'
                 f'<text x="{bx + 12:.1f}" y="{by + 17.5:.1f}" font-size="13" font-weight="600" fill="{p["text"]}">'
                 f'<tspan fill="{p["brand_text"]}" font-weight="800">{vals[imax]}</tspan>{esc(label[len(str(vals[imax])):])}</text></g>')
    # meses: en la semana que contiene el día 1 (como el calendario de GitHub)
    last_x = -1e9
    for i, w_ in enumerate(weekly):
        span = (w_["end"] - w_["start"]).days + 1
        d1 = next((w_["start"] + dt.timedelta(days=k) for k in range(span)
                   if (w_["start"] + dt.timedelta(days=k)).day == 1), None)
        if d1 is None:
            continue
        x = X0 + i * step
        yr = f" {d1.year}" if d1.month == 1 else ""
        if x - last_x < 44 or x + text_width(MES_EJE[d1.month - 1] + yr, 13, 600) > X1 + 4:
            continue
        b.append(f'<line x1="{x:.1f}" y1="{base + 1}" x2="{x:.1f}" y2="{base + 6}" stroke="{p["border"]}"/>'
                 f'<text x="{x:.1f}" y="{base + 24}" font-size="13" fill="{p["subtle"]}">{MES_EJE[d1.month - 1]}'
                 + (f'<tspan fill="{p["muted"]}" font-weight="600">{yr}</tspan>' if yr else "") + "</text>")
        last_x = x

    title = f"Actividad de {C.FIRST_NAME} en GitHub: {stats['total']} contribuciones en el último año"
    desc = (f"Contribuciones en el último año: {stats['total']}, repartidas en {stats['active_days']} "
            f"{dias(stats['active_days'])}. Racha actual: {cur['days']} {dias(cur['days'])}. "
            f"Racha máxima: {best['days']} {dias(best['days'])}"
            + (f" ({rango(best['start'], best['end'], end.year)})" if best['days'] else "")
            + f". Repositorios públicos: {data['public_repos']}. Gráfico de área con las contribuciones de cada una "
              f"de las últimas {n} semanas; el máximo es de {vals[imax]} en una semana. {upd}.")
    return svg_doc(W, H, "".join(b), title=title, desc=desc, css=css, defs="".join(defs))


# ===================================================================== lenguajes
MAX_LANGS = 6


def lang_rows(languages: dict[str, int]) -> list[tuple[str, float, str]]:
    """[(nombre, %, color)] ordenados; a partir del 6.º se agrupan en «Otros»."""
    total = sum(languages.values())
    if not total:
        return []
    items = sorted(languages.items(), key=lambda kv: -kv[1])
    if len(items) > MAX_LANGS:
        items = items[:MAX_LANGS - 1] + [("Otros", sum(v for _, v in items[MAX_LANGS - 1:]))]
    return [(k, v * 100 / total, lang_color(k) if k != "Otros" else "#8b949e") for k, v in items]


def _segment_widths(shares: list[float], avail: float, min_w: float = 5) -> list[float]:
    raw = [s / 100 * avail for s in shares]
    small = [r < min_w for r in raw]
    if all(small):
        return [avail / len(raw)] * len(raw)
    scale = (avail - min_w * sum(small)) / sum(r for r, s in zip(raw, small) if not s)
    return [min_w if s else r * scale for r, s in zip(raw, small)]


def langs_svg(theme: str, p: dict, data: dict) -> str:
    dark = theme == "dark"
    W, H = W_HALF, H_HALF
    X0, X1 = PAD, W - PAD
    rows = lang_rows(data.get("languages") or {})
    repos = len(data.get("lang_repos") or [])
    fdefs, fbody = frame(W, H, 22, p, dark, glow=("4%", "-12%"), glow_r="72%", dots_at=("0%", "0%"))
    css = f"""
    .grow{{animation:grow 1.3s cubic-bezier(.65,.05,.25,1) .35s backwards;transform-origin:{X0}px 0}}
    @keyframes grow{{from{{transform:scaleX(0)}}}}
    """
    defs = [fdefs]
    b = [fbody]
    b.append(header(X0, HEAD_Y, "code", "Lenguajes", p, right=head_chip(X1, HEAD_Y, f"{repos} repos", p)))

    # ---- barra apilada
    BY, BH, GAPW = 68, 14, 2
    bw = X1 - X0
    defs.append(f'<clipPath id="bar"><rect x="{X0}" y="{BY}" width="{bw}" height="{BH}" rx="{BH / 2}"/></clipPath>')
    seg = [f'<g clip-path="url(#bar)">{rrect(X0, BY, bw, BH, BH / 2, p["inset"])}<g class="grow">']
    if rows:
        widths = _segment_widths([r[1] for r in rows], bw - GAPW * (len(rows) - 1))
        x = X0
        for (name, _, color), w in zip(rows, widths):
            seg.append(f'<rect x="{x:.2f}" y="{BY}" width="{w:.2f}" height="{BH}" fill="{color}"/>')
            x += w + GAPW
    seg.append("</g></g>")
    b.append("".join(seg))

    # ---- leyenda (2 columnas, por orden: 1-3 a la izquierda, 4-6 a la derecha)
    col_w = (bw - 24) / 2
    RY, RH = 120, 33
    per_col = 3
    if not rows:
        b.append(f'<text class="fade" x="{X0}" y="{RY}" font-size="14" fill="{p["muted"]}">'
                 f'Todavía no hay código en repos públicos.</text>')
    for i, (name, share, color) in enumerate(rows):
        col, row = divmod(i, per_col)
        cx = X0 + col * (col_w + 24)
        y = RY + row * RH
        ptxt = pct(share)
        pw = text_width(ptxt, 13.5, 500, mono=True)
        label = fit(name, 14.5, col_w - 20 - pw - 12, 600)
        b.append(f'<g class="rise" style="animation-delay:{.55 + i * .07:.2f}s">'
                 f'<circle cx="{cx + 5:g}" cy="{y - 5:g}" r="5" fill="{color}"/>'
                 f'<text x="{cx + 18:g}" y="{y}" font-size="14.5" font-weight="600" fill="{p["text"]}">{esc(label)}</text>'
                 f'<text class="mono" x="{cx + col_w:g}" y="{y}" font-size="13.5" font-weight="500" fill="{p["muted"]}" '
                 f'text-anchor="end">{esc(ptxt)}</text></g>')
        if row < per_col - 1 and i + 1 < len(rows):     # separador con el siguiente de la columna
            b.append(f'<line class="fade" style="animation-delay:{.6 + i * .07:.2f}s" x1="{cx:g}" y1="{y + 14:g}" '
                     f'x2="{cx + col_w:g}" y2="{y + 14:g}" stroke="{p["border_soft"]}" stroke-dasharray="2 4"/>')

    # ---- pie
    foot = "Por bytes de código · repos propios, sin forks"
    b.append(f'<g class="fade" style="animation-delay:.9s">'
             f'<line x1="{X0}" y1="{FOOT_Y - 26}" x2="{X1}" y2="{FOOT_Y - 26}" stroke="{p["border_soft"]}"/>'
             f'<text x="{X0}" y="{FOOT_Y}" font-size="13" fill="{p["subtle"]}">{esc(foot)}</text></g>')

    summary = ", ".join(f"{n} {pct(s)}" for n, s, _ in rows) or "sin datos"
    title = f"Lenguajes en mis repositorios: {summary}"
    desc = (f"Barra apilada con el porcentaje de bytes de código de cada lenguaje en {repos} repositorios "
            f"propios de GitHub (sin forks ni el repositorio del perfil): {summary}.")
    return svg_doc(W, H, "".join(b), title=title, desc=desc, css=css, defs="".join(defs))


# ================================================================== cuenta atrás
def phase(today: dt.date) -> tuple[str, int]:
    """('antes', días que faltan) · ('durante', semana) · ('despues', 0)."""
    if today < PRACT_START:
        return "antes", (PRACT_START - today).days
    if today <= PRACT_END:
        return "durante", (today - PRACT_START).days // 7 + 1
    return "despues", 0


def daw_progress(today: dt.date) -> float:
    total = (DAW_END - DAW_START).days
    return min(max((today - DAW_START).days / total, 0.0), 1.0)


def flip_tiles(x, y, value: str, p, dark: bool, *, tw=TILE_W, th=TILE_H, gap=8, size=46,
               start=.3) -> tuple[str, str, float]:
    """Cifras en «fichas» de marcador (estilo flip) que ruedan hasta su valor.
    Devuelve (defs, svg, ancho)."""
    digits = [int(c) for c in value]
    lh = th                              # una cifra por ficha en reposo
    base = y + th / 2 + size * .36       # línea base para centrar la cifra (altura de mayúscula ≈ .72 em)
    clip = "".join(f'<rect x="{x + i * (tw + gap):g}" y="{y}" width="{tw}" height="{th}" rx="12"/>'
                   for i in range(len(digits)))
    defs = f'<clipPath id="tiles">{clip}</clipPath>'
    out = []
    for i in range(len(digits)):
        tx = x + i * (tw + gap)
        # media ficha sombreada: la de arriba más clara en oscuro, la de abajo más oscura en claro
        hy, col, op = (y, "#ffffff", .045) if dark else (y + th / 2, "#000000", .035)
        out.append(f'<g class="pop" style="animation-delay:{start - .15 + i * .07:.2f}s">'
                   f'<g filter="url(#shs)">{rrect(tx, y, tw, th, 12, p["raised"], p["border"])}</g>'
                   f'<rect x="{tx:g}" y="{hy:g}" width="{tw}" height="{th / 2:g}" fill="{col}" fill-opacity="{op}" '
                   f'clip-path="url(#tiles)"/></g>')
    cols = []
    for i, d in enumerate(digits):
        cx = x + i * (tw + gap) + tw / 2
        col = "".join(f'<text x="{cx:g}" y="{base + k * lh:g}" font-size="{size}" font-weight="800" '
                      f'text-anchor="middle" fill="url(#digit)">{k}</text>' for k in range(d + 1))
        cols.append(f'<g class="odo" style="transform:translateY({-d * lh:g}px);'
                    f'animation-delay:{start + i * .12:.2f}s">{col}</g>')
    out.append(f'<g class="fade" style="animation-delay:{start - .15:.2f}s"><g clip-path="url(#tiles)">{"".join(cols)}</g></g>')
    # bisagra central del marcador, por encima de las cifras
    for i in range(len(digits)):
        tx = x + i * (tw + gap)
        out.append(f'<g class="pop" style="animation-delay:{start - .15 + i * .07:.2f}s">'
                   f'<line x1="{tx + 1:g}" y1="{y + th / 2:g}" x2="{tx + tw - 1:g}" y2="{y + th / 2:g}" '
                   f'stroke="{p["canvas"]}" stroke-width="1.6" stroke-opacity=".9"/>'
                   f'<circle cx="{tx + 1:g}" cy="{y + th / 2:g}" r="2.6" fill="{p["canvas"]}"/>'
                   f'<circle cx="{tx + tw - 1:g}" cy="{y + th / 2:g}" r="2.6" fill="{p["canvas"]}"/></g>')
    return defs, "".join(out), len(digits) * tw + (len(digits) - 1) * gap


def countdown_svg(theme: str, p: dict, today: dt.date) -> str:
    dark = theme == "dark"
    W, H = W_HALF, H_HALF
    X0, X1 = PAD, W - PAD
    fase, n = phase(today)
    prog = daw_progress(today)
    fdefs, fbody = frame(W, H, 22, p, dark, glow=("96%", "-12%"), glow_r="72%", dots_at=("100%", "0%"))
    defs = [fdefs, brand_gradient("bg", p), shadow_filter("shs", p["shadow"], 3, 8),
            # cifras: degradado vertical de marca (en claro, más oscuro para mantener el contraste)
            f'<linearGradient id="digit" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{p["grad_a"] if dark else p["brand"]}"/>'
            f'<stop offset="1" stop-color="{p["grad_b"] if dark else p["brand_text"]}"/></linearGradient>',
            f'<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="6" height="6" fill="{p["brand"]}" fill-opacity="{.10 if dark else .08}"/>'
            f'<line x1="0" y1="0" x2="0" y2="6" stroke="{p["brand"]}" stroke-width="2.2" stroke-opacity="{.45 if dark else .35}"/>'
            f'</pattern>']
    css = ODOMETER_CSS + f"""
    .fill{{animation:fill 1.5s cubic-bezier(.65,.05,.25,1) .7s backwards;transform-origin:{X0}px 0}}
    @keyframes fill{{from{{transform:scaleX(0)}}}}
    .knob{{animation:knob 1.5s cubic-bezier(.65,.05,.25,1) .7s backwards}}
    """
    b = [fbody]
    period = f"{MESES[PRACT_START.month - 1]} – {MESES[PRACT_END.month - 1]} {PRACT_END.year}"

    # ---- cabecera
    b.append(header(X0, HEAD_Y, hourglass if fase == "antes" else "briefcase", "Prácticas de empresa", p,
                    right=head_chip(X1, HEAD_Y, "2.º DAW", p)))

    # ---- bloque principal
    TY = 58
    if fase in ("antes", "durante"):
        if fase == "antes":
            pre, post = ("Falta" if n == 1 else "Faltan"), dias(n)
            line2 = [("para mis prácticas", p["text"], 600), (f" · {period}", p["muted"], 400)]
        else:
            pre, post = "Semana", ""
            line2 = [("En prácticas", p["text"], 600), (f" · {period}", p["muted"], 400)]
        pw = text_width(pre, 24, 700)
        tx = X0 + pw + 14
        tdefs, tiles, tw = flip_tiles(tx, TY, str(n), p, dark)
        defs.append(tdefs)
        base = TY + TILE_H / 2 + 24 * .36
        b.append(f'<text class="rise" style="animation-delay:.1s" x="{X0}" y="{base:g}" font-size="24" '
                 f'font-weight="700" fill="{p["text"]}">{esc(pre)}</text>')
        b.append(tiles)
        if post:
            b.append(f'<text class="rise" style="animation-delay:.35s" x="{tx + tw + 14:g}" y="{base:g}" font-size="24" '
                     f'font-weight="700" fill="{p["text"]}">{esc(post)}</text>')
        y2 = TY + TILE_H + 32
        spans = "".join(f'<tspan fill="{c}" font-weight="{wt}">{esc(t)}</tspan>' for t, c, wt in line2)
        dot = ""
        lx = X0
        if fase == "durante":
            dot = (f'<circle class="ping" cx="{X0 + 5}" cy="{y2 - 5}" r="4.5" fill="{p["success"]}"/>'
                   f'<circle cx="{X0 + 5}" cy="{y2 - 5}" r="4.5" fill="{p["success"]}"/>')
            lx = X0 + 18
        b.append(f'<g class="rise" style="animation-delay:.45s">{dot}<text x="{lx}" y="{y2}" font-size="16">{spans}</text></g>')
    else:
        # prácticas completadas: insignia con check
        cx, cy, r = X0 + 34, TY + TILE_H / 2, 34
        b.append(f'<g class="pop" style="animation-delay:.2s"><circle cx="{cx}" cy="{cy}" r="{r}" fill="{p["success_soft"]}" '
                 f'stroke="{p["success"]}" stroke-width="1.5"/>'
                 f'<path class="draw" pathLength="1" style="animation-delay:.5s" d="M{cx - 13} {cy + 1}l9 9 18-19" '
                 f'stroke="{p["success"]}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></g>')
        b.append(f'<text class="rise" style="animation-delay:.3s" x="{X0 + 86}" y="{TY + 32}" font-size="26" '
                 f'font-weight="800" letter-spacing="-.4" fill="{p["text"]}">Prácticas completadas</text>')
        b.append(f'<text class="rise" style="animation-delay:.4s" x="{X0 + 86}" y="{TY + 58}" font-size="16" '
                 f'fill="{p["muted"]}">{esc(period)} · 2.º DAW</text>')

    # ---- progreso del ciclo DAW
    LY, BY, BH = 192, 203, 12
    bw = X1 - X0
    fill_w = bw * prog
    label = "Progreso del ciclo DAW"
    lw = text_width(label, 14, 600)
    b.append(f'<g class="fade" style="animation-delay:.6s"><text x="{X0}" y="{LY}" font-size="14" font-weight="600" '
             f'fill="{p["text"]}">{label}<tspan fill="{p["subtle"]}" font-weight="400"> · </tspan>'
             f'<tspan fill="{p["brand_text"]}" font-weight="800">{esc(pct(prog * 100))}</tspan></text></g>')
    # tramo de prácticas dentro del ciclo (cota con etiqueta)
    total = (DAW_END - DAW_START).days
    sx0 = X0 + bw * (PRACT_START - DAW_START).days / total
    sx1 = X0 + bw * ((PRACT_END - DAW_START).days + 1) / total
    smid = (sx0 + sx1) / 2
    b.append(f'<g class="fade" style="animation-delay:.9s">'
             f'<path d="M{sx0 + .5:.1f} {BY - 4}V{BY - 7}H{sx1 - .5:.1f}V{BY - 4}" stroke="{p["brand_line"]}" stroke-width="1.2"/>'
             f'<text x="{smid:.1f}" y="{LY}" font-size="13" font-weight="600" fill="{p["brand_text"]}" '
             f'text-anchor="middle">prácticas</text></g>')
    defs.append(f'<clipPath id="track"><rect x="{X0}" y="{BY}" width="{bw}" height="{BH}" rx="{BH / 2}"/></clipPath>')
    b.append(f'<g clip-path="url(#track)">{rrect(X0, BY, bw, BH, BH / 2, p["inset"])}'
             f'<rect x="{sx0:.1f}" y="{BY}" width="{sx1 - sx0:.1f}" height="{BH}" fill="url(#hatch)"/>'
             f'<rect class="fill" x="{X0}" y="{BY}" width="{fill_w:.1f}" height="{BH}" fill="url(#bg)"/></g>'
             + rrect(X0 + .5, BY + .5, bw - 1, BH - 1, (BH - 1) / 2, "none", p["border_soft"]))
    if 0 < prog < 1:
        kx = X0 + fill_w
        css += f"@keyframes knob{{from{{transform:translateX({-fill_w:.1f}px)}}}}"
        b.append(f'<g class="knob"><circle class="ping" cx="{kx:.1f}" cy="{BY + BH / 2}" r="7" fill="{p["brand"]}" '
                 f'fill-opacity=".5"/><circle cx="{kx:.1f}" cy="{BY + BH / 2}" r="7.5" fill="{p["raised"]}" '
                 f'stroke="{p["brand"]}" stroke-width="2.5"/></g>')
    # extremos del ciclo
    b.append(f'<g class="fade" style="animation-delay:.8s">'
             f'<text x="{X0}" y="{FOOT_Y}" font-size="13" fill="{p["subtle"]}">{MES_ABR[DAW_START.month - 1]} {DAW_START.year}</text>'
             f'<text x="{X1}" y="{FOOT_Y}" font-size="13" fill="{p["subtle"]}" text-anchor="end">'
             f'{MES_ABR[DAW_END.month - 1]} {DAW_END.year}</text></g>')

    prog_txt = f"Progreso del ciclo DAW (sep. 2025 – jun. 2027): {pct(prog * 100)}."
    if fase == "antes":
        title = f"{'Falta' if n == 1 else 'Faltan'} {n} {dias(n)} para mis prácticas ({period})"
        desc = f"Cuenta atrás para las prácticas de empresa de 2.º DAW, de {period}. {prog_txt}"
    elif fase == "durante":
        title = f"En prácticas · semana {n} ({period})"
        desc = f"Prácticas de empresa de 2.º DAW en curso, de {period}: semana {n}. {prog_txt}"
    else:
        title = f"Prácticas completadas ({period})"
        desc = f"Prácticas de empresa de 2.º DAW completadas ({period}). {prog_txt}"
    return svg_doc(W, H, "".join(b), title=title, desc=desc, css=css, defs="".join(defs))
