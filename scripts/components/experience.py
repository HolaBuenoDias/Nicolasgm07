"""Experiencia en Bastilipo: tarjeta con cabecera (empresa, puesto, periodo e insignia),
una mini línea temporal mes a mes (mar. 2025 → jun. 2026) que se rellena con el degradado
de marca, y la rejilla 3×2 con las seis áreas de trabajo.

    python scripts/build.py experience   →  assets/experience/bastilipo-{dark,light}.svg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import (brand_gradient, card, dot_grid, esc, icon, rrect, svg_doc,  # noqa: E402
                   text_width, write_themed)
import content as C  # noqa: E402

E = C.EXPERIENCE
W = 1000
X0, X1 = 40, 960                      # columna de contenido

MESES = ["ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sep.", "oct.", "nov.", "dic."]
INICIALES = "EFMAMJJASOND"

# ---- ritmo vertical (rejilla de 4/8)
Y_HEAD, TILE = 36, 64                 # cabecera: 36 → 100
Y_FLAG = 132                          # banderas de los hitos
Y_DATE, Y_LBL = 145, 166              # líneas base: fecha (mono) y etiqueta
Y_BAR, BAR_H = 182, 10                # barra segmentada (un bloque = un mes)
Y_LET = Y_BAR + BAR_H + 23            # iniciales de los meses
Y_YEAR = Y_LET + 16                   # llaves de año
Y_GRID, CELL_H, GUT = 260, 88, 16     # rejilla de áreas
H = Y_GRID + 2 * CELL_H + 12 + 36

# ---- tiempos de la animación de entrada (s)
T_FILL, D_FILL = .62, 1.55            # la barra se rellena de izquierda a derecha
CURVE = (.45, .05, .25, 1)            # reparto de los bloques en el tiempo (ease in-out)
SEG_DUR = .32

# Frases que nunca se parten entre líneas.
NOBREAK = ("PrestaShop 1.7", "Tag Manager", "Ads Shopping", "Merchant Center", "Google Shopping",
           "TikTok Shop", "1 año", "4 meses")

STAR = "M12 3.2l2.7 5.5 6 .9-4.4 4.2 1.1 6-5.4-2.8-5.4 2.8 1.1-6-4.4-4.2 6-.9L12 3.2Z"


# --------------------------------------------------------------------------- helpers
def months(start: str, end: str) -> list[tuple[int, int]]:
    y, m = map(int, start.split("-"))
    y2, m2 = map(int, end.split("-"))
    out = []
    while (y, m) <= (y2, m2):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def label_month(y: int, m: int) -> str:
    return f"{MESES[m - 1]} {y}"


def bezier_time(progress: float, curve=CURVE) -> float:
    """Fracción de tiempo en la que una cubic-bezier alcanza `progress` (bisección)."""
    x1, y1, x2, y2 = curve
    lo, hi = 0.0, 1.0
    for _ in range(40):
        s = (lo + hi) / 2
        y = 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s ** 2 * y2 + s ** 3
        lo, hi = (s, hi) if y < progress else (lo, s)
    s = (lo + hi) / 2
    return 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s ** 2 * x2 + s ** 3


def seg_time(k: int, n: int) -> float:
    """Instante (s) en que empieza a rellenarse el bloque k de n."""
    return T_FILL + D_FILL * bezier_time(k / n)


def nice_lines(text: str, size: float, max_w: float, weight: int = 400, max_lines: int = 3) -> list[str]:
    """Parte el texto como lo haría un maquetador: el menor número de líneas posible, líneas
    equilibradas, cortes preferidos tras «·» (que desaparece en el salto) o tras coma, y nunca
    dentro de las frases de NOBREAK ni dejando «+» o «y» colgando al final de línea."""
    words = text.split()
    n = len(words)
    bare = [w.rstrip(",.;:") for w in words]
    protected = set()                  # índices i tales que no se puede cortar entre i e i+1
    for phrase in NOBREAK:
        pw = phrase.split()
        for i in range(n - len(pw) + 1):
            if bare[i:i + len(pw)] == pw:
                protected.update(range(i, i + len(pw) - 1))

    def render(chunk):
        if chunk and chunk[-1] == "·":
            chunk = chunk[:-1]
        return " ".join(chunk)

    best = None
    for k in range(1, max_lines + 1):
        def splits(start, left):
            if left == 1:
                yield [words[start:]]
                return
            for cut in range(start + 1, n - left + 2):
                for rest in splits(cut, left - 1):
                    yield [words[start:cut]] + rest

        for parts in splits(0, k):
            if any(not p for p in parts):
                continue
            idx, cost, ok = 0, 0.0, True
            lines = []
            for j, part in enumerate(parts):
                idx += len(part)
                line = render(part)
                if part[0] == "·" or text_width(line, size, weight) > max_w:
                    ok = False
                    break
                lines.append(line)
                if j < len(parts) - 1:
                    last = part[-1]
                    if idx - 1 in protected:
                        cost += 1000
                    if last == "·":
                        cost -= 150
                    elif last.endswith(","):
                        cost -= 12
                    elif last in ("+", "y", "e", "con", "de", "del", "la", "el"):
                        cost += 45
            if not ok:
                continue
            widths = [text_width(l, size, weight) for l in lines]
            cost += max(widths) + (max(widths) - min(widths)) * .35
            if best is None or cost < best[0]:
                best = (cost, lines)
        if best:
            return best[1]
    raise ValueError(f"No cabe: {text!r} en {max_w}px")


def tspans(parts) -> str:
    """[(texto, color, peso[, atributos extra])] → tspans encadenados."""
    out = []
    for t, col, wt, *extra in parts:
        ex = f" {extra[0]}" if extra else ""
        out.append(f'<tspan fill="{col}" font-weight="{wt}"{ex}>{esc(t)}</tspan>')
    return "".join(out)


def parts_width(parts, size) -> float:
    return sum(text_width(t, size, wt) for t, _, wt, *_ in parts)


def anim(cls: str, d: float) -> str:
    return f'class="{cls}" style="animation-delay:{d:.2f}s"'


# --------------------------------------------------------------------------- tarjeta
def build(theme, p):
    dark = theme == "dark"
    ms = months(E["start"], E["end"])
    n = len(ms)
    daw = next(e for e in C.EDUCATION if e["short"] == "DAW")
    k_daw = ms.index(tuple(map(int, daw["start"].split("-"))))
    start_lbl, end_lbl = (s.strip() for s in E["period"].split("–"))
    assert start_lbl == label_month(*ms[0]) and end_lbl == label_month(*ms[-1])

    # Bloques de un mes agrupados por trimestres: hueco fino entre meses, ancho entre trimestres.
    GAP_M, GAP_Q = 3, 10
    gaps = [GAP_Q if ms[k][1] in (1, 4, 7, 10) else GAP_M for k in range(1, n)]
    seg_w = (X1 - X0 - sum(gaps)) / n
    seg_x = [X0]
    for g in gaps:
        seg_x.append(seg_x[-1] + seg_w + g)

    def sx(k):          # x de la frontera antes del mes k (centro del hueco; k = 0 / n → extremos)
        if k == 0:
            return X0
        if k == n:
            return X1
        return seg_x[k] - gaps[k - 1] / 2

    defs = [
        f'<clipPath id="xclip"><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18"/></clipPath>',
        f'<radialGradient id="xglow" cx="92%" cy="0%" r="58%">'
        f'<stop offset="0" stop-color="{p["brand"]}" stop-opacity="{.17 if dark else .10}"/>'
        f'<stop offset=".6" stop-color="{p["brand"]}" stop-opacity="{.03 if dark else .02}"/>'
        f'<stop offset="1" stop-color="{p["brand"]}" stop-opacity="0"/></radialGradient>',
        dot_grid("xdots", p["grid"], 22, 1.1, .8 if dark else .95),
        f'<radialGradient id="xdm" cx="100%" cy="0%" r="62%">'
        f'<stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<mask id="xdmask"><rect width="{W}" height="{H}" fill="url(#xdm)"/></mask>',
        brand_gradient("xtile", p, x2="100%", y2="100%"),
        f'<linearGradient id="xbar" gradientUnits="userSpaceOnUse" x1="{X0}" y1="0" x2="{X1}" y2="0">'
        f'<stop offset="0" stop-color="{p["grad_a"]}"/><stop offset="1" stop-color="{p["grad_b"]}"/></linearGradient>',
        f'<filter id="xtglow" x="-40%" y="-40%" width="180%" height="190%">'
        f'<feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="{p["brand"]}" flood-opacity="{.38 if dark else .28}"/></filter>',
        f'<linearGradient id="xshine" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity="{.22 if dark else .75}"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="xglint" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity="{.55 if dark else .6}"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
    ]

    seg_end = sx(n)
    css = f"""
    .seg{{animation:seg {SEG_DUR}s cubic-bezier(.3,.7,.4,1) backwards;transform-box:fill-box;transform-origin:0 50%}}
    @keyframes seg{{from{{transform:scaleX(0)}}}}
    .lit{{animation:lit .45s ease backwards}}
    @keyframes lit{{from{{opacity:.28}}}}
    .glint{{animation:glint 7s 3.4s cubic-bezier(.45,0,.3,1) infinite backwards}}
    @keyframes glint{{0%{{transform:translateX(0)}}26%,100%{{transform:translateX({seg_end - X0 + 200:g}px)}}}}
    .shine{{animation:shine 7s 2.9s cubic-bezier(.45,0,.3,1) infinite backwards}}
    @keyframes shine{{0%{{transform:translateX(0)}}16%,100%{{transform:translateX(420px)}}}}
    .tw{{animation:tw 7s 2.9s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
    @keyframes tw{{0%,12%,100%{{transform:none}}5%{{transform:scale(1.28) rotate(18deg)}}}}
    """

    b = []
    # ---------------------------------------------------------------- fondo
    b.append(card(0, 0, W, H, p))
    b.append(f'<g clip-path="url(#xclip)"><rect width="{W}" height="{H}" fill="url(#xdots)" mask="url(#xdmask)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#xglow)"/></g>')

    # ---------------------------------------------------------------- cabecera
    tx, ty = X0, Y_HEAD
    b.append(f'<g {anim("pop", .05)}><g filter="url(#xtglow)">{rrect(tx, ty, TILE, TILE, 17, "url(#xtile)")}</g>'
             f'{rrect(tx + .5, ty + .5, TILE - 1, TILE - 1, 16.5, "none", "#ffffff", 1, "stroke-opacity=\".22\"")}'
             f'{icon("briefcase", tx + 16, ty + 16, 32, p["on_brand"], 2)}</g>')
    nx = X0 + TILE + 24
    b.append(f'<text {anim("rise", .12)} x="{nx}" y="{ty + 30}" font-size="30" font-weight="800" letter-spacing="-.6" '
             f'fill="{p["text"]}">{esc(E["company"])}</text>')
    b.append(f'<text {anim("rise", .2)} x="{nx}" y="{ty + 56}" font-size="16" font-weight="500" '
             f'fill="{p["muted"]}">{esc(E["role"])}</text>')

    # chips a la derecha (mismo ancho, apilados)
    chip_h, cs = 28, 13.5
    period = [(E["period"], p["text"], 500), ("  ·  ", p["subtle"], 500), (E["duration"], p["brand_text"], 650)]
    note = [(E["note"], p["brand_text"], 650)]
    cw = max(parts_width(period, cs), parts_width(note, cs)) + 12 + 16 + 9 + 16
    cx = X1 - cw
    y1, y2 = ty, ty + TILE - chip_h
    assert cx - (nx + text_width(E["role"], 16, 500)) > 40, "la cabecera se solapa"
    b.append(f'<g {anim("rise", .28)}>{rrect(cx, y1, cw, chip_h, chip_h / 2, p["raised"], p["border"])}'
             f'{icon("calendar", cx + 12, y1 + 6, 16, p["muted"], 2)}'
             f'<text x="{cx + 37:g}" y="{y1 + chip_h / 2 + cs * .36:g}" font-size="{cs}" xml:space="preserve">'
             f'{tspans(period)}</text></g>')
    b.append(f'<clipPath id="xbadge">{rrect(cx, y2, cw, chip_h, chip_h / 2)}</clipPath>')
    b.append(f'<g {anim("rise", .36)}>{rrect(cx, y2, cw, chip_h, chip_h / 2, p["brand_soft"], p["brand_line"])}'
             f'<g clip-path="url(#xbadge)"><path class="shine" d="M{cx - 70:g} {y2}h44l-16 {chip_h}h-44Z" fill="url(#xshine)"/></g>'
             f'<g transform="translate({cx + 12:g} {y2 + 6:g}) scale({16 / 24:g})"><path class="tw" d="{STAR}" '
             f'fill="{p["brand_text"]}" stroke="{p["brand_text"]}" stroke-width="1.6" stroke-linejoin="round"/></g>'
             f'<text x="{cx + 37:g}" y="{y2 + chip_h / 2 + cs * .36:g}" font-size="{cs}">{tspans(note)}</text></g>')

    # ---------------------------------------------------------------- línea temporal
    # base vacía + bloques que se rellenan (un bloque = un mes)
    segs, base, clip = [], [], []
    r = 3
    for k in range(n):
        a = seg_x[k]
        base.append(rrect(a, Y_BAR, seg_w, BAR_H, r, p["border_soft"]))
        clip.append(f'<rect x="{a:g}" y="{Y_BAR}" width="{seg_w:g}" height="{BAR_H}" rx="{r}"/>')
        segs.append(f'<rect {anim("seg", seg_time(k, n))} x="{a:g}" y="{Y_BAR}" width="{seg_w:g}" height="{BAR_H}" '
                    f'rx="{r}" fill="url(#xbar)"/>')
    defs.append(f'<clipPath id="xsegs">{"".join(clip)}</clipPath>')
    b.append("".join(base) + "".join(segs))
    b.append(f'<g clip-path="url(#xsegs)"><rect class="glint" x="{X0 - 170}" y="{Y_BAR - 2}" width="150" '
             f'height="{BAR_H + 4}" fill="url(#xglint)"/></g>')

    # iniciales de los meses (se «encienden» al pasar el relleno)
    key = {0, k_daw, n - 1}
    for k, (y, m) in enumerate(ms):
        col = p["text"] if k in key else p["muted"]
        wt = 700 if k in key else 500
        b.append(f'<text {anim("mono lit", seg_time(k, n) + .12)} x="{seg_x[k] + seg_w / 2:g}" y="{Y_LET}" font-size="13" '
                 f'font-weight="{wt}" fill="{col}" text-anchor="middle">{INICIALES[m - 1]}</text>')

    # llaves de año
    years = []
    k = 0
    while k < n:
        yr = ms[k][0]
        k2 = k
        while k2 < n and ms[k2][0] == yr:
            k2 += 1
        a, z = seg_x[k] + 4, seg_x[k2 - 1] + seg_w - 4
        mid, half = (a + z) / 2, text_width(str(yr), 13, mono=True) / 2 + 9
        hook = 5
        years.append(f'<g {anim("fade", seg_time(k, n) + .1)}>'
                     f'<path d="M{a:g} {Y_YEAR - hook}V{Y_YEAR}H{mid - half:g}M{mid + half:g} {Y_YEAR}H{z:g}V{Y_YEAR - hook}" '
                     f'stroke="{p["border"]}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>'
                     f'<text class="mono" x="{mid:g}" y="{Y_YEAR + 4.5}" font-size="13" font-weight="600" fill="{p["muted"]}" '
                     f'text-anchor="middle">{yr}</text></g>')
        k = k2
    b.append("".join(years))

    # banderas de los hitos
    def flag(x, side, date, label_parts, d, strong=True):
        lx = x + 11 if side == "r" else x - 11
        anchor = "" if side == "r" else ' text-anchor="end"'
        line_col = p["brand"] if strong else p["border"]
        dot = (f'<circle cx="{x:g}" cy="{Y_FLAG + 2}" r="3.2" fill="{p["brand"] if strong else p["surface"]}" '
               f'stroke="{p["brand"] if strong else p["subtle"]}" stroke-width="1.5"/>')
        return (f'<g {anim("fade", d)}>'
                f'<line x1="{x:g}" y1="{Y_FLAG + 2}" x2="{x:g}" y2="{Y_BAR - 1}" stroke="{line_col}" stroke-width="1.5" '
                f'stroke-opacity="{.55 if strong else 1}"/>{dot}'
                f'<text class="mono" x="{lx:g}" y="{Y_DATE}" font-size="13" font-weight="600" letter-spacing=".3" '
                f'fill="{p["brand_text"] if strong else p["muted"]}"{anchor}>{esc(date)}</text>'
                f'<text x="{lx:g}" y="{Y_LBL}" font-size="14.5"{anchor}>{tspans(label_parts)}</text></g>')

    smr = [("Prácticas del SMR", p["text"], 650), (" → ", p["brand_text"], 700, 'font-size="17"'),
           ("contrato", p["text"], 650)]
    mid = [("Empiezo DAW en paralelo", p["muted"], 500)]
    fin = [("Cierro etapa", p["text"], 650)]
    x_mid = sx(k_daw)
    # comprobación de holguras entre etiquetas
    w_smr = max(parts_width(smr, 14.5), text_width(start_lbl, 13, mono=True))
    w_mid = max(parts_width(mid, 14.5), text_width(label_month(*ms[k_daw]), 13, mono=True))
    w_fin = max(parts_width(fin, 14.5), text_width(end_lbl, 13, mono=True))
    assert X0 + 1 + 11 + w_smr + 24 < x_mid, "hito inicial y DAW se solapan"
    assert x_mid + 11 + w_mid + 24 < X1 - 1 - 11 - w_fin, "hito DAW y final se solapan"
    b.append(flag(X0 + 1, "r", start_lbl, smr, T_FILL - .2))
    b.append(flag(x_mid, "r", label_month(*ms[k_daw]), mid, seg_time(k_daw, n) + .05, strong=False))
    b.append(flag(X1 - 1, "l", end_lbl, fin, seg_time(n - 1, n) + SEG_DUR))

    # ---------------------------------------------------------------- áreas (3 × 2)
    cols = 3
    cw_ = (X1 - X0 - GUT * (cols - 1)) / cols
    text_x, text_w = 64, cw_ - 64 - 14
    for i, area in enumerate(E["areas"]):
        r_, c_ = divmod(i, cols)
        x = X0 + c_ * (cw_ + GUT)
        y = Y_GRID + r_ * (CELL_H + 12)
        lines = nice_lines(area["summary"], 14, text_w)
        assert len(lines) <= 2, (area["key"], lines)
        assert text_width(area["title"], 15.5, 700) <= text_w, area["title"]
        spans = "".join(f'<tspan x="{x + text_x:g}" dy="{0 if j == 0 else 19}">{esc(l)}</tspan>'
                        for j, l in enumerate(lines))
        b.append(f'<g {anim("rise", .7 + i * .07)}>'
                 f'{rrect(x + .5, y + .5, cw_ - 1, CELL_H - 1, 14, p["raised"], p["border_soft" if not dark else "border"])}'
                 f'{rrect(x + 16, y + 16, 36, 36, 10, p["brand_soft"])}'
                 f'{icon(area["icon"], x + 24, y + 24, 20, p["brand_text"], 1.9)}'
                 f'<text x="{x + text_x:g}" y="{y + 32}" font-size="15.5" font-weight="700" fill="{p["text"]}">{esc(area["title"])}</text>'
                 f'<text x="{x + text_x:g}" y="{y + 54}" font-size="14" fill="{p["muted"]}">{spans}</text></g>')

    title = (f"Experiencia: {E['role']} en {E['company']}, {E['period']} ({E['duration']}). "
             f"{E['note']}.")
    desc = ("Tarjeta con la línea temporal mes a mes desde las prácticas del SMR, que acabaron en contrato, "
            "hasta junio de 2026 (con el inicio de DAW en paralelo en septiembre de 2025), y las seis áreas "
            "de trabajo: " + "; ".join(f'{a["title"]}: {a["summary"]}' for a in E["areas"]) + ".")
    return svg_doc(W, H, "".join(b), title=title, desc=desc, css=css, defs="".join(defs))


def main():
    return write_themed("experience/bastilipo", build)


if __name__ == "__main__":
    for path in main():
        print(path)
