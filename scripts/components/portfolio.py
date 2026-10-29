"""Portfolio: cuatro tarjetas (rejilla 2×2 a width="49%") con capturas reales de las webs en
las que trabajé en Bastilipo.

Cada tarjeta mide 490 × 500 y tiene dos zonas:
  - «escaparate» (arriba): la captura de escritorio hace scroll sola dentro de una ventana de
    navegador y la versión móvil, en un teléfono superpuesto, hace scroll desfasado.
  - ficha (abajo): nombre, dominio, sector y stack verificado (content.SITES) y un botón ↗.

Las capturas (scripts/screens/*.webp, octubre de 2026) se incrustan tal cual como data: URI
(GitHub no deja cargar recursos externos dentro de un SVG servido como <img>). Con
prefers-reduced-motion todo se queda quieto mostrando la parte superior de cada web.

Los móviles llevan barra de estado del color con el que empieza cada web (muestreado de la
propia captura): la isla queda dentro de esa barra y la página hace scroll por debajo, así
nunca tapa texto de la captura.
"""
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import (EASE, ROOT, TECH, THEMES, browser_frame, card, delay, dot_grid, esc,  # noqa: E402
                   icon, picture, rrect, shadow_filter, svg_doc, text_width, wrap, write_themed)
import content as C  # noqa: E402

W, H = 490, 500          # tarjeta (dos por fila a width="49%")
SH = 328                 # alto del escaparate
PAD = 24                 # margen interior de la ficha
PERIOD = 20.0            # ciclo de scroll (ida y vuelta), en segundos
START = 1.4              # el scroll arranca cuando ya han entrado los marcos
SCREENS = os.path.join(ROOT, "scripts", "screens")
SITES = {s["slug"]: s for s in C.SITES}
DEVICE = THEMES["dark"]  # el móvil es oscuro en los dos temas (como uno de verdad)

# Primera fila de cada captura móvil (color de la barra de estado) y tinta de sus iconos.
TOPBAR = {
    "circuitobebe-mobile.webp": ("#a8d3c7", "#0f2e27"),
    "electro-outlet-mobile.webp": ("#de0f0e", "#ffffff"),
    "urbify-mobile.webp": ("#0a1f45", "#ffffff"),
}


# --------------------------------------------------------------------- capturas
def webp_size(data: bytes) -> tuple[int, int]:
    """Ancho y alto de un WebP leyendo su cabecera (VP8, VP8L o VP8X)."""
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("no es un WebP")
    kind = data[12:16]
    if kind == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    if kind == b"VP8 ":
        return (int.from_bytes(data[26:28], "little") & 0x3FFF,
                int.from_bytes(data[28:30], "little") & 0x3FFF)
    if kind == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    raise ValueError(f"WebP desconocido: {kind!r}")


_SHOTS: dict = {}


def shot(name: str) -> dict:
    """Captura real: {'uri', 'w', 'h', 'bytes'} (se lee una vez y se reutiliza)."""
    if name not in _SHOTS:
        with open(os.path.join(SCREENS, name), "rb") as f:
            data = f.read()
        w, h = webp_size(data)
        _SHOTS[name] = {"uri": "data:image/webp;base64," + base64.b64encode(data).decode("ascii"),
                        "w": w, "h": h, "bytes": len(data)}
    return _SHOTS[name]


class Doc:
    """Acumula defs y css de un SVG; cada captura se incrusta una sola vez (<use> la repite)."""

    def __init__(self):
        self.defs, self.css, self._imgs = [], [], {}

    def image(self, name: str, width: float) -> tuple[str, float]:
        """Devuelve (id, alto) de la captura escalada a `width`, definida una vez en <defs>."""
        s = shot(name)
        key = (name, round(width, 2))
        h = width * s["h"] / s["w"]
        if key not in self._imgs:
            iid = f"img{len(self._imgs)}"
            self._imgs[key] = iid
            self.defs.append(f'<image id="{iid}" href="{s["uri"]}" width="{width:g}" height="{h:.2f}" '
                             f'preserveAspectRatio="none"/>')
        return self._imgs[key], h


# ------------------------------------------------------------------- movimiento
def scroll_css(cls: str, stops: list, *, period=PERIOD, start=START, hold=2.2, end_hold=2.8,
               v=120.0, back_v=300.0, mmin=1.5, mmax=3.6) -> str:
    """Scroll «humano»: pausa, baja por tramos (ease-in-out en cada uno), pausa abajo y vuelve
    arriba de un tirón suave. `stops` son desplazamientos en px; el primero es el de reposo."""
    pts = [(0.0, stops[0]), (hold, stops[0])]
    t = hold
    for i in range(1, len(stops)):
        t += min(mmax, max(mmin, abs(stops[i] - stops[i - 1]) / v))
        pts.append((t, stops[i]))
        t += end_hold if i == len(stops) - 1 else hold
        pts.append((t, stops[i]))
    t += min(4.2, max(2.2, abs(stops[-1] - stops[0]) / back_v))
    pts.append((t, stops[0]))
    limit = period - 0.4
    if t > limit:                      # si no cabe en el ciclo, se comprime todo por igual
        pts = [(a * limit / t, s) for a, s in pts]
    pts.append((period, stops[0]))
    rules, i = [], 0
    while i < len(pts):
        j = i
        while j + 1 < len(pts) and abs(pts[j + 1][1] - pts[i][1]) < 1e-6:
            j += 1
        sel = ",".join(f"{pts[k][0] / period * 100:.2f}".rstrip("0").rstrip(".") + "%"
                       for k in sorted({i, j}))
        rules.append(f"{sel}{{transform:translateY({-pts[i][1]:.1f}px)}}")
        i = j + 1
    return (f".{cls}{{animation:{cls} {period:g}s ease-in-out {start:.2f}s infinite backwards}}"
            f"@keyframes {cls}{{{''.join(rules)}}}")


def offsets(stops_src: list, scale: float, travel: float) -> list:
    """Paradas en px de la captura original → px del SVG (None = final de la página)."""
    return [round(travel if s is None else min(travel, s * scale), 1) for s in stops_src]


CSS = f"""
.win{{animation:win .9s {EASE} backwards}}
@keyframes win{{from{{opacity:0;transform:translateY(18px)}}}}
.dev{{animation:dev 1s {EASE} backwards}}
@keyframes dev{{from{{opacity:0;transform:translateY(30px)}}}}
.nudge{{animation:nudge 4.8s ease-in-out 2.4s infinite}}
@keyframes nudge{{0%,72%,100%{{transform:none}}80%{{transform:translate(2px,-2px)}}88%{{transform:none}}}}
"""


# ---------------------------------------------------------------------- piezas
def rpath(x, y, w, h, rt, rb) -> str:
    """Rectángulo con radios distintos arriba (rt) y abajo (rb), como path."""
    return (f"M{x + rt:g} {y:g}H{x + w - rt:g}" + (f"A{rt:g} {rt:g} 0 0 1 {x + w:g} {y + rt:g}" if rt else "")
            + f"V{y + h - rb:g}" + (f"A{rb:g} {rb:g} 0 0 1 {x + w - rb:g} {y + h:g}" if rb else "")
            + f"H{x + rb:g}" + (f"A{rb:g} {rb:g} 0 0 1 {x:g} {y + h - rb:g}" if rb else "")
            + f"V{y + rt:g}" + (f"A{rt:g} {rt:g} 0 0 1 {x + rt:g} {y:g}" if rt else "") + "Z")


def stage(p, theme) -> tuple[str, str]:
    """Defs y fondo de la tarjeta: escaparate con rejilla de puntos y brillo de marca."""
    dark = theme == "dark"
    well = p["canvas"] if dark else p["surface"]
    base = p["surface"] if dark else p["canvas"]
    defs = (f'<clipPath id="cc"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18"/></clipPath>'
            + dot_grid("dots", p["grid"], 16, 1, .8 if dark else 1)
            + '<radialGradient id="dfade" cx="50%" cy="45%" r="70%"><stop offset=".25" stop-color="#fff" '
              'stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></radialGradient>'
            + f'<mask id="dm"><rect width="{W}" height="{SH}" fill="url(#dfade)"/></mask>'
            + f'<radialGradient id="glow" cx="92%" cy="0%" r="80%"><stop offset="0" stop-color="{p["brand"]}" '
              f'stop-opacity="{.20 if dark else .12}"/><stop offset=".6" stop-color="{p["brand"]}" '
              f'stop-opacity="{.04 if dark else .03}"/><stop offset="1" stop-color="{p["brand"]}" stop-opacity="0"/>'
              f'</radialGradient>'
            + shadow_filter("sh", p["shadow"], 12, 20)
            + shadow_filter("shs", p["shadow"], 4, 8))
    body = (card(0, 0, W, H, p, fill=base)
            + f'<g clip-path="url(#cc)"><rect width="{W}" height="{SH}" fill="{well}"/>'
              f'<rect width="{W}" height="{SH}" fill="url(#dots)" mask="url(#dm)"/>'
              f'<rect width="{W}" height="{SH}" fill="url(#glow)"/></g>'
            + f'<line x1="1" y1="{SH + .5}" x2="{W - 1}" y2="{SH + .5}" stroke="{p["border"]}"/>')
    return defs, body


def frame_border(p) -> str:
    """Borde de la tarjeta, encima de todo (tapa sombras que lleguen al canto)."""
    return card(0, 0, W, H, p, fill="none")


def status_bar(sx, sy, sw, sb, rs, fill, ink) -> str:
    """Barra de estado de iPhone a escala: hora, isla, cobertura y batería."""
    k = sw / 100
    cy = sy + 6.9 * k                       # eje de la isla
    base = cy + 1.9 * k                     # línea base de la hora y de las barras
    out = [f'<path d="{rpath(sx, sy, sw, sb, rs, 0)}" fill="{fill}"/>',
           f'<text x="{sx + 17 * k:.1f}" y="{base:.1f}" font-size="{5.4 * k:.2f}" font-weight="700" '
           f'fill="{ink}" text-anchor="middle" letter-spacing="-.1">9:41</text>',
           rrect(sx + sw / 2 - 15 * k, sy + 2.6 * k, 30 * k, 8.6 * k, 4.3 * k, "#000000")]
    bx = sx + 68.5 * k                      # cobertura: cuatro barras
    for i, bh in enumerate((1.5, 2.2, 2.9, 3.6)):
        out.append(rrect(bx + i * 1.75 * k, base - bh * k, 1.15 * k, bh * k, .3 * k, ink))
    bx = sx + 77.5 * k                      # batería
    out.append(rrect(bx, base - 3.6 * k, 6.6 * k, 3.6 * k, 1.1 * k, "none", ink, .45 * k,
                     'stroke-opacity=".45"'))
    out.append(rrect(bx + .75 * k, base - 2.85 * k, 4.6 * k, 2.1 * k, .5 * k, ink))
    out.append(rrect(bx + 6.95 * k, base - 2.45 * k, .7 * k, 1.3 * k, .3 * k, ink, extra='fill-opacity=".45"'))
    return "".join(out)


def phone(doc: Doc, uid: str, x, y, w, h, shot_name: str, cls: str, base: float = 0) -> tuple[str, dict]:
    """Móvil con la captura `shot_name` haciendo scroll bajo su barra de estado.
    Devuelve (svg, métricas de la ventana de la captura)."""
    d = DEVICE
    r = round(w * .17, 1)
    bz = round(max(5.0, w * .045), 1)
    sx, sy, sw, sh = x + bz, y + bz, w - 2 * bz, h - 2 * bz
    rs = r - bz
    sb = round(sw * .135, 1)                # alto de la barra de estado
    vy, vh = sy + sb, sh - sb               # ventana por la que pasa la web
    iid, ih = doc.image(shot_name, sw)
    fill, ink = TOPBAR[shot_name]
    rest = f' style="transform:translateY({-base:.1f}px)"' if base else ""
    k = sw / 100
    svg = (f'<g filter="url(#sh)">'
           + rrect(x - 1.6, y + h * .19, 3.2, h * .07, 1.6, d["border"])
           + rrect(x - 1.6, y + h * .29, 3.2, h * .11, 1.6, d["border"])
           + rrect(x + w - 1.6, y + h * .25, 3.2, h * .14, 1.6, d["border"])
           + rrect(x, y, w, h, r, d["inset"], d["border"], 1.2) + "</g>"
           + f'<clipPath id="{uid}"><path d="{rpath(sx, vy, sw, vh, 0, rs)}"/></clipPath>'
           + f'<path d="{rpath(sx, vy, sw, vh, 0, rs)}" fill="#ffffff"/>'
           + f'<g clip-path="url(#{uid})"><g class="{cls}"{rest}><use href="#{iid}" x="{sx:g}" y="{vy:g}"/></g></g>'
           + status_bar(sx, sy, sw, sb, rs, fill, ink)
           + rrect(sx + sw / 2 - 17 * k, sy + sh - 2.4 * k - max(1.6, 1.3 * k), 34 * k, max(1.6, 1.3 * k),
                   .8 * k, "#000000", extra='fill-opacity=".55"')
           + rrect(x + 2.2, y + 2.2, w - 4.4, h - 4.4, r - 2.2, "none", "#ffffff", .8, 'stroke-opacity=".08"'))
    s = shot(shot_name)
    scale = sw / s["w"]
    return svg, {"scale": scale, "travel": ih - vh, "view": vh / scale}


def browser(doc: Doc, x, y, w, h, p, *, url: str, shot_name: str, cls: str) -> tuple[str, dict]:
    """Ventana de navegador (brand.browser_frame) con la captura recortada al área de contenido."""
    frame, (cx, cy, cw, ch) = browser_frame(x, y, w, h, p, url=url, r=12, bar=36)
    iid, ih = doc.image(shot_name, cw)
    rr = 11
    svg = (f'<g filter="url(#sh)">{frame}</g>'
           f'<clipPath id="bc"><path d="{rpath(cx, cy, cw, ch, 0, rr)}"/></clipPath>'
           f'<g clip-path="url(#bc)"><rect x="{cx:g}" y="{cy:g}" width="{cw:g}" height="{ch:g}" fill="#ffffff"/>'
           f'<g class="{cls}"><use href="#{iid}" x="{cx:g}" y="{cy:g}"/></g></g>')
    scale = cw / shot(shot_name)["w"]
    return svg, {"scale": scale, "travel": ih - ch, "view": ch / scale}


def tag(x, y, label, p, dot=None, size=13, h=26) -> tuple[str, float]:
    """Chip del stack (variante compacta de brand.chip para que quepan cuatro por fila)."""
    pad, dw = 10, (13 if dot else 0)
    w = pad * 2 + dw + text_width(label, size, 500)
    out = rrect(x + .5, y + .5, w - 1, h - 1, (h - 1) / 2, p["raised"], p["border"])
    if dot:
        out += f'<circle cx="{x + pad + 4:g}" cy="{y + h / 2:g}" r="4" fill="{dot}"/>'
    out += (f'<text x="{x + pad + dw:g}" y="{y + h / 2 + size * .36:g}" font-size="{size}" font-weight="500" '
            f'fill="{p["text"]}">{esc(label)}</text>')
    return out, w


def devices_icon(x, y, s, color) -> str:
    """Icono propio «escritorio + móvil» (rejilla 24, trazo redondeado). La pantalla se corta
    donde empieza el móvil, así no hace falta tapar líneas con un relleno."""
    k = s / 24
    return (f'<g transform="translate({x:g} {y:g}) scale({k:g})" fill="none" stroke="{color}" '
            f'stroke-width="{2 / k:.3g}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M12 15H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v1"/>'
            f'<path d="M9 15v4.5"/><path d="M6 19.5h5"/>'
            f'<rect x="14.5" y="9.5" width="7.5" height="12" rx="1.8"/><path d="M17.6 18.6h1.3"/></g>')


def phone_glyph(x, y, s, color) -> str:
    """Icono propio de móvil (rejilla 24)."""
    k = s / 24
    return (f'<g transform="translate({x:g} {y:g}) scale({k:g})" fill="none" stroke="{color}" '
            f'stroke-width="{2.1 / k:.3g}" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="6" y="2.5" width="12" height="19" rx="2.6"/><path d="M10.5 18.5h3"/></g>')


def float_chip(x, y, glyph, label, p, d=.9) -> tuple[str, float]:
    """Chip flotante con sombra (mismo lenguaje que los del hero). Devuelve (svg, ancho)."""
    w = text_width(label, 13, 600) + 48
    return (f'<g class="pop" style="animation-delay:{d}s"><g filter="url(#shs)">'
            f'{rrect(x, y, w, 32, 16, p["raised"], p["border"])}</g>'
            f'{glyph(x + 13, y + 8, 16, p["brand_text"])}'
            f'<text x="{x + 35}" y="{y + 20.5}" font-size="13" font-weight="600" fill="{p["text"]}">'
            f'{esc(label)}</text></g>'), w


def info(p, *, name, sub, text, tags, button) -> str:
    """Ficha inferior: nombre, dominio (mono), sector, chips y botón arriba a la derecha."""
    x0, y0 = PAD, SH + 46
    out = [f'<g class="rise" {delay(0, base=.45)}><text x="{x0}" y="{y0}" font-size="22" font-weight="800" '
           f'letter-spacing="-.3" fill="{p["text"]}">{esc(name)}</text>'
           f'<text class="mono" x="{x0}" y="{y0 + 24}" font-size="13.5" fill="{p["brand_text"]}">{esc(sub)}</text></g>']
    size = 14.5
    while len(wrap(text, size, W - 2 * PAD)) > 1:    # una sola línea, siempre
        size -= .5
    out.append(f'<text class="rise" {delay(1, base=.45)} x="{x0}" y="{y0 + 52}" font-size="{size:g}" '
               f'fill="{p["muted"]}">{esc(text)}</text>')
    tx, ty, row = x0, H - PAD - 26, [f'<g class="rise" {delay(2, base=.45)}>']
    for label, dot in tags:
        svg, w = tag(tx, ty, label, p, dot)
        row.append(svg)
        tx += w + 8
    assert tx - 8 <= W - PAD, f"los chips no caben: {tags}"
    row.append("</g>")
    out.append("".join(row))
    # botón (↗ abre la web; en la tarjeta «responsive», icono de dispositivos)
    bx, by, r = W - PAD - 20, SH + 40, 20
    btn = [f'<g class="pop" {delay(3, base=.45)}>',
           f'<circle cx="{bx}" cy="{by}" r="{r - .5}" fill="{p["brand_soft"]}" stroke="{p["brand_line"]}"/>']
    if button == "external":
        btn.append(f'<g class="nudge">{icon("external", bx - 9, by - 9, 18, p["brand_text"], 2.3)}</g>')
    else:
        btn.append(devices_icon(bx - 10, by - 10, 20, p["brand_text"]))
    btn.append("</g>")
    out.append("".join(btn))
    return "".join(out)


def stack_tags(stack, p) -> list:
    return [(t, TECH.get(t) or p["subtle"]) for t in stack]


def finish(doc: Doc, p, body: list, sdefs: str, *, title: str, desc: str) -> str:
    body.append(frame_border(p))
    return svg_doc(W, H, "".join(body), title=title, desc=desc, css=CSS + "".join(doc.css),
                   defs=sdefs + "".join(doc.defs))


# --------------------------------------------------------------------- tarjetas
def site_card(slug, desk_name, mob_name, desk_stops, mob_stops):
    """Tarjeta de una web con captura de escritorio (navegador) + móvil superpuesto."""
    site = SITES[slug]

    def build(theme, p):
        doc = Doc()
        sdefs, sbody = stage(p, theme)
        b = [sbody]
        # navegador
        win, m = browser(doc, 24, 24, 372, 272, p, url=site["domain"], shot_name=desk_name, cls="sd")
        b.append(f'<g class="win" style="animation-delay:.1s">{win}</g>')
        doc.css.append(scroll_css("sd", offsets(desk_stops, m["scale"], m["travel"])))
        # móvil superpuesto abajo a la derecha
        pw, ph = 116, 252
        svg, m = phone(doc, "pc", W - 22 - pw, SH - 18 - ph, pw, ph, mob_name, "sm")
        b.append(f'<g class="dev" style="animation-delay:.35s">{svg}</g>')
        doc.css.append(scroll_css("sm", offsets(mob_stops, m["scale"], m["travel"]),
                                  start=START - PERIOD / 2, hold=2.0, end_hold=2.6))
        b.append(info(p, name=site["name"], sub=site["domain"], text=site["sector"],
                      tags=stack_tags(site["stack"], p), button="external"))
        title = f"{site['name']} ({site['domain']}) — {site['sector']}"
        desc = (f"Tarjeta del portfolio con capturas reales de {site['domain']} tomadas en octubre de 2026: "
                f"la versión de escritorio hace scroll dentro de una ventana de navegador y la versión móvil "
                f"en un teléfono. Stack: {', '.join(site['stack'])}.")
        return finish(doc, p, b, sdefs, title=title, desc=desc)
    return build


def mobile_card(slug, mob_name, a_stops, b_stops):
    """Electro-outlet: sin captura de escritorio (su hosting bloquea navegadores automatizados),
    así que la tarjeta es «mobile first»: dos móviles grandes desfasados."""
    site = SITES[slug]

    def build(theme, p):
        doc = Doc()
        sdefs, sbody = stage(p, theme)
        b = [sbody]
        pw, ph, gap = 132, 268, 26
        ax, ay = (W - 2 * pw - gap) / 2, 20
        bx2, by2 = ax + pw + gap, 46
        svg_a, m = phone(doc, "pa", ax, ay, pw, ph, mob_name, "ea")
        a_off = offsets(a_stops, m["scale"], m["travel"])
        b_off = offsets(b_stops, m["scale"], m["travel"])
        svg_b, _ = phone(doc, "pb", bx2, by2, pw, ph, mob_name, "eb", base=b_off[0])
        b.append(f'<g class="dev" style="animation-delay:.1s">{svg_a}</g>')
        b.append(f'<g class="dev" style="animation-delay:.3s">{svg_b}</g>')
        doc.css.append(scroll_css("ea", a_off, hold=2.6, end_hold=3.2))
        doc.css.append(scroll_css("eb", b_off, start=START - PERIOD * .45, hold=1.8, end_hold=2.4))
        # chip flotante «Mobile first»: alineado arriba con el primer móvil y apoyado en el canto
        # superior del segundo (solo pisa el marco, nunca la barra de estado ni la web)
        chip, cw = float_chip(0, 0, phone_glyph, "Mobile first", p)
        b.append(f'<g transform="translate({W - PAD - cw:g} {ay + 2:g})">{chip}</g>')
        b.append(info(p, name=site["name"], sub=site["domain"], text=site["sector"],
                      tags=stack_tags(site["stack"], p), button="external"))
        title = f"{site['name']} ({site['domain']}) — {site['sector']}"
        desc = (f"Tarjeta del portfolio con capturas reales de la versión móvil de {site['domain']} tomadas en "
                f"octubre de 2026: dos móviles hacen scroll desfasado, uno por la cabecera, el buscador y "
                f"las ofertas y otro por el catálogo de productos. Stack: {', '.join(site['stack'])}.")
        return finish(doc, p, b, sdefs, title=title, desc=desc)
    return build


RESPONSIVE = [  # (captura móvil, nombre, paradas en px de la captura original)
    ("circuitobebe-mobile.webp", "Circuito Bebé", [0, 800, None]),
    ("electro-outlet-mobile.webp", "Electro-outlet", [0, 560, 1130, None]),
    ("urbify-mobile.webp", "Urbify", [0, 740, None]),
]


def responsive_card(theme, p):
    """4.ª tarjeta: las tres webs en el móvil, ligeramente escalonadas."""
    doc = Doc()
    sdefs, sbody = stage(p, theme)
    b = [sbody]
    side, mid = (120, 250), (136, 284)
    gap = 14
    x0 = (W - (side[0] * 2 + mid[0] + gap * 2)) / 2
    slots = [(x0, 44, *side), (x0 + side[0] + gap, 16, *mid), (x0 + side[0] + mid[0] + gap * 2, 44, *side)]
    order = [0, 2, 1]  # el central, delante
    phones = {}
    for i, (name, label, stops) in enumerate(RESPONSIVE):
        x, y, w, h = slots[i]
        cls = f"r{i}"
        svg, m = phone(doc, f"pr{i}", x, y, w, h, name, cls)
        doc.css.append(scroll_css(cls, offsets(stops, m["scale"], m["travel"]),
                                  start=START - PERIOD * i / 3, hold=1.8, end_hold=2.4))
        lw = text_width(label, 13, 600) + 26
        pill = (f'<g filter="url(#shs)">{rrect(x + w / 2 - lw / 2, y + h - 13, lw, 26, 13, p["raised"], p["border"])}</g>'
                f'<text x="{x + w / 2:g}" y="{y + h + 4.7:g}" font-size="13" font-weight="600" fill="{p["text"]}" '
                f'text-anchor="middle">{esc(label)}</text>')
        phones[i] = f'<g class="dev" style="animation-delay:{.1 + .15 * i:.2f}s">{svg}{pill}</g>'
    b.extend(phones[i] for i in order)
    tags = [("PHP (hooks)", TECH["PHP"]), ("CSS", TECH["CSS"]), ("JavaScript", TECH["JavaScript"])]
    b.append(info(p, name="Todo responsive", sub="@media (max-width: 768px)",
                  text="Fichas, carrito, buscador y menú móvil pensados para el móvil", tags=tags,
                  button="devices"))
    title = "Todo responsive — las tres webs en el móvil"
    desc = ("Tres móviles con capturas reales (octubre de 2026) de circuitobebe.com, electro-outlet.net y "
            "urbifyrealstate.com haciendo scroll desfasado. Fichas, carrito, buscador y menú móvil pensados "
            "para el móvil, personalizados con PHP (hooks), CSS y JavaScript.")
    return finish(doc, p, b, sdefs, title=title, desc=desc)


# ------------------------------------------------------------------------ build
def main():
    paths = []
    paths += write_themed("portfolio/circuitobebe", site_card(
        "circuitobebe", "circuitobebe-desktop.webp", "circuitobebe-mobile.webp",
        desk_stops=[0, 440, None], mob_stops=[0, 800, None]))
    paths += write_themed("portfolio/electro-outlet", mobile_card(
        "electro-outlet", "electro-outlet-mobile.webp", a_stops=[0, 300], b_stops=[600, 1130, None]))
    paths += write_themed("portfolio/urbify", site_card(
        "urbify", "urbify-desktop.webp", "urbify-mobile.webp",
        desk_stops=[0, 440, 950, None], mob_stops=[0, 740, None]))
    paths += write_themed("portfolio/responsive", responsive_card)
    return paths


CARD_LINKS = [  # (asset, url, alt, title)
    ("circuitobebe", "https://www.circuitobebe.com/",
     "Circuito Bebé — tienda online de puericultura (circuitobebe.com)",
     "Abrir circuitobebe.com · tienda online de puericultura con WordPress y WooCommerce"),
    ("electro-outlet", "https://www.electro-outlet.net/",
     "Electro-outlet — electrodomésticos reacondicionados (electro-outlet.net)",
     "Abrir electro-outlet.net · electrodomésticos reacondicionados con WooCommerce"),
    ("urbify", "https://urbifyrealstate.com/",
     "Urbify — consultora inmobiliaria con identidad visual propia (urbifyrealstate.com)",
     "Abrir urbifyrealstate.com · web de la consultora inmobiliaria Urbify (logo y favicon incluidos)"),
    ("responsive", "#portfolio",
     "Todo responsive — las tres webs en el móvil",
     "Fichas, carrito, buscador y menú móvil pensados para el móvil"),
]


def snippet() -> str:
    """Fragmento HTML para el README (rejilla 2×2, cada tarjeta enlazada a su web)."""
    pics = [picture(f"portfolio/{a}", alt, width="49%", href=url, title=title) for a, url, alt, title in CARD_LINKS]
    return (f'<p align="center">\n  {pics[0]}\n  {pics[1]}\n<br>\n  {pics[2]}\n  {pics[3]}\n</p>\n\n'
            '<p align="center"><sub>Capturas reales de las webs, tomadas en octubre de 2026 · '
            'pulsa una tarjeta para abrirla</sub></p>\n')


if __name__ == "__main__":
    for path in main():
        print(path, f"{os.path.getsize(path) / 1024:.0f} KB")
