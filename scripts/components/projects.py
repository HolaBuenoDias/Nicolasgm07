"""Proyectos (sección 05 del README).

  · Destacado (1000 × 448): la aplicación inspirada en League of Legends, full stack en dos repos
    (app-lol: Angular 21 con SSR · league_of_legends: Spring Boot + MongoDB). A la izquierda, texto
    y stack; a la derecha, la arquitectura animada: la app pide GET /api/characters, la API consulta
    MongoDB con findAll() y el JSON vuelve, mientras la app pasa de esqueleto de carga a tarjetas.
  · Dos tarjetas (490 × 256): Api_products y ActBaseDatos, cada una con su esquema relacional real.

Datos comprobados en los repos (octubre de 2026): CharacterController (@RequestMapping api/characters
y sus 7 endpoints), CharacterService.findAll(), colección «characters», puerto 8080 (lo usa el
CharacterService del front), ng serve en localhost:4200, menú de header.ts (Campeones, Tier List,
Builds) y etiquetas «Tanque»/«Multirol» de las páginas de filtros; script_productos.sql
(Producto.categoria_id → Categoria.id, @ManyToOne) y Empresa_informatica.sql
(empleados.departamento_id → departamentos.departamento_id, FOREIGN KEY).
Todo son formas propias: ningún logo ni arte de Riot, Angular, Spring o MongoDB.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import (EASE, TECH, brand_gradient, card, delay, dot_grid, esc, icon, kicker,  # noqa: E402
                   paragraph, picture, rrect, shadow_filter, svg_doc, text_width, window_dots, wrap,
                   write_themed)
import content as C  # noqa: E402

FEAT = C.PROJECTS["featured"]
OTHERS = {o["repo"]: o for o in C.PROJECTS["others"]}

W, H = 1000, 448          # destacado (ancho completo)
SW, SH = 490, 256         # tarjetas pequeñas (dos por fila a width="49%")
COVER = 116               # alto del «escaparate» de las tarjetas pequeñas
T = 8.0                   # ciclo de la animación de datos del destacado (s)
LOOP = 1.9                # el ciclo arranca cuando ya han entrado las piezas
METHOD = {"GET": "num", "POST": "success", "PUT": "warning", "DELETE": "danger"}


# ------------------------------------------------------------------------ helpers
def tech_color(label: str, p: dict) -> str:
    """Color linguist de una tecnología («Angular 21» → Angular); gris si no tiene."""
    return TECH.get(label) or TECH.get(label.rsplit(" ", 1)[0]) or p["subtle"]


def tag(x, y, label, p, dot, size=13, h=26) -> tuple[str, float]:
    """Chip del stack (variante compacta de brand.chip, como en el portfolio)."""
    pad, dw = 10, 13
    w = pad * 2 + dw + text_width(label, size, 500)
    out = rrect(x + .5, y + .5, w - 1, h - 1, (h - 1) / 2, p["raised"], p["border"])
    out += f'<circle cx="{x + pad + 4:g}" cy="{y + h / 2:g}" r="4" fill="{dot}"/>'
    out += (f'<text x="{x + pad + dw:g}" y="{y + h / 2 + size * .36:g}" font-size="{size}" font-weight="500" '
            f'fill="{p["text"]}">{esc(label)}</text>')
    return out, w


def glyph(paths: str, x, y, s, color, sw=1.8, extra="") -> str:
    """Icono propio en rejilla 24 con trazo redondeado (mismo estilo que brand.icon)."""
    k = s / 24
    return (f'<g transform="translate({x:g} {y:g}) scale({k:g})" fill="none" stroke="{color}" '
            f'stroke-width="{sw / k:.3g}" stroke-linecap="round" stroke-linejoin="round" {extra}>{paths}</g>')


REPO = ('<path d="M5 18.5V5.5A2.5 2.5 0 0 1 7.5 3H19v13.5H7.5A2.5 2.5 0 0 0 5 19a2.5 2.5 0 0 0 2.5 2.5H10"/>'
        '<path d="M13 19v3.5l2-1.5 2 1.5V19"/><path d="M19 16.5v5h-.5"/>')
TABLE = '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 9.5h18"/><path d="M9 9.5V20"/>'
KEY = '<circle cx="7.5" cy="15.5" r="4"/><path d="M10.4 12.6 19 4"/><path d="M15.5 7.5l2.5 2.5"/><path d="M13.5 9.5l2 2"/>'
ROUTE = '<circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="6" r="2.5"/><path d="M8.5 18H15a3.5 3.5 0 0 0 0-7H9a3.5 3.5 0 0 1 0-7h6.5"/>'


def method_badge(x, y, m, p, w=46, h=15) -> str:
    c = p[METHOD[m]]
    return (rrect(x, y, w, h, 4, c, None, extra='fill-opacity=".15"')
            + f'<text class="mono" x="{x + w / 2:g}" y="{y + h / 2 + 3.4:g}" font-size="9.5" font-weight="700" '
              f'fill="{c}" text-anchor="middle" letter-spacing=".4">{m}</text>')


def top_bar(x, y, w, bar, r, fill) -> str:
    """Franja superior de una ventana/caja con las esquinas de arriba redondeadas."""
    ri = r - .5
    return (f'<path d="M{x + r:g} {y + .5:g}H{x + w - r:g}A{ri:g} {ri:g} 0 0 1 {x + w - .5:g} {y + r:g}'
            f'V{y + bar:g}H{x + .5:g}V{y + r:g}A{ri:g} {ri:g} 0 0 1 {x + r:g} {y + .5:g}Z" fill="{fill}"/>')


# ================================================================== destacado
CSS_F = f"""
.win{{animation:win .9s {EASE} backwards}}
@keyframes win{{from{{opacity:0;transform:translateY(16px)}}}}
.req{{animation:req {T:g}s ease-in-out {LOOP}s infinite backwards}}
@keyframes req{{0%,3%{{opacity:0;transform:translateY(-22px)}}6%,15%{{opacity:1}}18%,100%{{opacity:0;transform:translateY(22px)}}}}
.db{{animation:db {T:g}s ease-in-out {LOOP}s infinite backwards}}
@keyframes db{{0%,19%{{opacity:0;transform:translateX(-24px)}}21%,33%{{opacity:1}}26.5%{{transform:translateX(24px)}}35%,100%{{opacity:0;transform:translateX(-24px)}}}}
.res{{animation:res {T:g}s ease-in-out {LOOP}s infinite backwards}}
@keyframes res{{0%,36%{{opacity:0;transform:translateY(22px)}}39%,48%{{opacity:1}}51%,100%{{opacity:0;transform:translateY(-22px)}}}}
.skel{{opacity:0;animation:skel {T:g}s ease {LOOP}s infinite backwards}}
@keyframes skel{{0%{{opacity:0}}3%,50%{{opacity:1}}55%,100%{{opacity:0}}}}
"""

CARDS = [  # (color de la paleta, etiqueta del retrato, ancho de la barra del nombre)
    ("brand", "Tanque", 46), ("num", "Multirol", 54), ("fn", None, 40), ("success", "Tanque", 50),
]


def champion_card(x, y, w, h, p, color, badge, name_w, uid) -> str:
    """Tarjeta de personaje genérica: retrato (silueta propia), etiqueta de rol y textos."""
    c = p[color]
    ph = 46
    px, py, pw = x + 4, y + 4, w - 8
    mid = px + pw / 2
    pb = py + ph
    out = [rrect(x + .5, y + .5, w - 1, h - 1, 8, p["surface"], p["border"]),
           f'<clipPath id="{uid}"><rect x="{px:g}" y="{py:g}" width="{pw:g}" height="{ph:g}" rx="5"/></clipPath>',
           f'<g clip-path="url(#{uid})">',
           f'<rect x="{px:g}" y="{py:g}" width="{pw:g}" height="{ph:g}" fill="{c}" fill-opacity=".16"/>',
           f'<circle cx="{px + pw * .82:g}" cy="{py + 6:g}" r="{ph * .62:g}" fill="{c}" fill-opacity=".14"/>',
           f'<circle cx="{mid:g}" cy="{pb - 24:g}" r="7.5" fill="{c}" fill-opacity=".85"/>',
           f'<path d="M{mid - 17:g} {pb + 1:g}C{mid - 17:g} {pb - 10:g} {mid - 9:g} {pb - 14:g} {mid:g} {pb - 14:g}'
           f'C{mid + 9:g} {pb - 14:g} {mid + 17:g} {pb - 10:g} {mid + 17:g} {pb + 1:g}Z" fill="{c}" fill-opacity=".85"/>',
           "</g>"]
    if badge:
        bw = text_width(badge, 9.5, 700) + 12
        out.append(rrect(px + 4, py + 4, bw, 15, 7.5, p["raised"], None, extra='fill-opacity=".92"')
                   + f'<text x="{px + 10:g}" y="{py + 14.6:g}" font-size="9.5" font-weight="700" '
                     f'fill="{p["text"]}">{esc(badge)}</text>')
    out.append(rrect(x + 8, y + ph + 15, name_w, 6, 3, p["text"], None, extra='fill-opacity=".82"'))
    out.append(rrect(x + 8, y + ph + 26, name_w * .62, 4.5, 2.25, p["muted"], None, extra='fill-opacity=".55"'))
    return "".join(out)


def skeleton_card(x, y, w, h, p, name_w) -> str:
    """El mismo hueco mientras «carga» (tapa la tarjeta real por completo)."""
    ph = 46
    return (rrect(x + .5, y + .5, w - 1, h - 1, 8, p["surface"], p["border"])
            + rrect(x + 4, y + 4, w - 8, ph, 5, p["border_soft"], None)
            + rrect(x + 8, y + ph + 15, name_w, 6, 3, p["border_soft"], None)
            + rrect(x + 8, y + ph + 26, name_w * .62, 4.5, 2.25, p["border_soft"], None))


def app_window(x, y, w, h, p) -> str:
    """Ventana con app-lol: barra con localhost:4200, cabecera de la app y tarjetas de personajes."""
    bar = 30
    out = [f'<g filter="url(#sh)">{rrect(x, y, w, h, 12, p["raised"], p["border"])}</g>',
           top_bar(x, y, w, bar, 12, p["surface"]),
           f'<line x1="{x:g}" y1="{y + bar:g}" x2="{x + w:g}" y2="{y + bar:g}" stroke="{p["border_soft"]}"/>',
           window_dots(x + 17, y + bar / 2, r=4.3, gap=14)]
    url = "localhost:4200"
    ux, uw = x + 66, text_width(url, 11.5) + 36
    out.append(rrect(ux, y + 7, uw, bar - 14, (bar - 14) / 2, p["canvas"], p["border_soft"])
               + icon("lock", ux + 8, y + bar / 2 - 5.5, 11, p["muted"], 2.2)
               + f'<text x="{ux + 24:g}" y="{y + bar / 2 + 4:g}" font-size="11.5" fill="{p["muted"]}">{url}</text>')
    # etiqueta «SSR» a la derecha de la barra (la app se renderiza también en servidor)
    sl = "SSR"
    sw_ = text_width(sl, 10, 700, mono=True) + 14
    out.append(rrect(x + w - 12 - sw_, y + 8, sw_, 14, 7, p["brand_soft"], p["brand_line"])
               + f'<text class="mono" x="{x + w - 12 - sw_ / 2:g}" y="{y + 18.3:g}" font-size="10" font-weight="700" '
                 f'fill="{p["brand_text"]}" text-anchor="middle">{sl}</text>')
    # cabecera de la app
    top = y + bar
    hx = x + 14
    out.append(rrect(hx, top + 9, 13, 13, 4, "url(#mk)")
               + f'<text x="{hx + 20:g}" y="{top + 20:g}" font-size="12" font-weight="800" letter-spacing="-.2" '
                 f'fill="{p["text"]}">app-lol</text>')
    nx = x + w - 14
    for i, lab in reversed(list(enumerate(["Campeones", "Tier List", "Builds"]))):
        wt = 650 if i == 0 else 400
        tw = text_width(lab, 11, wt)
        nx -= tw
        out.append(f'<text x="{nx:g}" y="{top + 20:g}" font-size="11" font-weight="{wt}" '
                   f'fill="{p["text"] if i == 0 else p["muted"]}">{lab}</text>')
        if i == 0:
            out.append(rrect(nx, top + 27, tw, 2, 1, p["brand"]))
        nx -= 16
    out.append(f'<line x1="{x + 1:g}" y1="{top + 30.5:g}" x2="{x + w - 1:g}" y2="{top + 30.5:g}" '
               f'stroke="{p["border_soft"]}"/>')
    # tarjetas (con su esqueleto de carga encima, que se desvanece cuando llega el JSON)
    n, gap = len(CARDS), 10
    cw = (w - 28 - gap * (n - 1)) / n
    cy, chh = top + 42, h - bar - 42 - 12
    real, skel = [], []
    for i, (color, badge, name_w) in enumerate(CARDS):
        cx = x + 14 + i * (cw + gap)
        real.append(champion_card(cx, cy, cw, chh, p, color, badge, name_w, f"pc{i}"))
        skel.append(skeleton_card(cx, cy, cw, chh, p, name_w))
    out.append("".join(real))
    out.append(f'<g class="skel">{"".join(skel)}</g>')
    return "".join(out)


def server_box(x, y, w, h, p) -> str:
    """API de Spring Boot: cabecera y lista corta de endpoints reales del CharacterController."""
    head = 32
    out = [f'<g filter="url(#sh)">{rrect(x, y, w, h, 12, p["raised"], p["border"])}</g>',
           top_bar(x, y, w, head, 12, p["surface"]),
           f'<line x1="{x:g}" y1="{y + head:g}" x2="{x + w:g}" y2="{y + head:g}" stroke="{p["border_soft"]}"/>',
           icon("server", x + 12, y + 8, 16, TECH["Spring Boot"], 2),
           f'<text x="{x + 35:g}" y="{y + 21:g}" font-size="12.5" font-weight="700" fill="{p["text"]}">Spring Boot</text>',
           f'<text class="mono" x="{x + w - 12:g}" y="{y + 20.5:g}" font-size="11" fill="{p["muted"]}" '
           f'text-anchor="end">:8080</text>']
    rows = [("GET", "/api/characters"), ("GET", "/api/characters/{id}"), ("POST", "/api/characters"),
            ("GET", "…/filter/multirol"), ("GET", "…/filter/role/tank")]
    ry = y + head + 9
    for i, (m, path) in enumerate(rows):
        yy = ry + i * 21
        if i == 0:
            out.append(rrect(x + 6, yy - 3, w - 12, 21, 6, p["brand_soft"], p["brand_line"]))
        out.append(method_badge(x + 12, yy, m, p))
        out.append(f'<text class="mono" x="{x + 66:g}" y="{yy + 11.4:g}" font-size="11.5" '
                   f'fill="{p["text"] if i == 0 else p["muted"]}">{esc(path)}</text>')
    return "".join(out)


def mongo(x0, x1, y0, y1, p) -> str:
    """Cilindro de base de datos (forma genérica) con la colección «characters»."""
    rx, ry = (x1 - x0) / 2, 10
    cx = (x0 + x1) / 2
    g = TECH["MongoDB"]
    out = [f'<g filter="url(#sh)"><path d="M{x0:g} {y0:g}V{y1:g}A{rx:g} {ry} 0 0 0 {x1:g} {y1:g}V{y0:g}Z" '
           f'fill="{p["raised"]}" stroke="{p["border"]}"/></g>',
           f'<ellipse cx="{cx:g}" cy="{y0:g}" rx="{rx:g}" ry="{ry}" fill="{p["surface"]}" stroke="{p["border"]}"/>',
           f'<ellipse cx="{cx:g}" cy="{y0:g}" rx="{rx - 14:g}" ry="{ry - 4.5:g}" fill="{g}" fill-opacity=".22"/>']
    for k in (1, 2):
        yy = y0 + (y1 - y0) * k / 3 + 6
        out.append(f'<path d="M{x0 + .5:g} {yy:g}A{rx:g} {ry} 0 0 0 {x1 - .5:g} {yy:g}" stroke="{p["border_soft"]}" '
                   f'stroke-width="1.2"/>')
    out.append(f'<text x="{cx:g}" y="{y0 + 34:g}" font-size="12.5" font-weight="700" fill="{p["text"]}" '
               f'text-anchor="middle">MongoDB</text>'
               f'<text class="mono" x="{cx:g}" y="{y0 + 51:g}" font-size="11" fill="{p["muted"]}" '
               f'text-anchor="middle">characters</text>')
    # documentos
    for k in range(3):
        dy = y0 + 72 + k * 10
        out.append(rrect(cx - 26 + k * 4, dy, 44 - k * 8, 5, 2.5, g, None, extra=f'fill-opacity="{.55 - k * .15:.2f}"'))
    return "".join(out)


def lane_pill(x, y, parts, p, h=24) -> tuple[str, float]:
    """Etiqueta de un conector: [(texto, color, peso)] en mono."""
    w = sum(text_width(t, 11.5, mono=True) for t, _, _ in parts) + 20
    spans = "".join(f'<tspan fill="{c}" font-weight="{wt}">{esc(t)}</tspan>' for t, c, wt in parts)
    return (f'<g filter="url(#shs)">{rrect(x, y, w, h, h / 2, p["raised"], p["border"])}</g>'
            f'<text class="mono" x="{x + 10:g}" y="{y + h / 2 + 4:g}" font-size="11.5" xml:space="preserve">'
            f'{spans}</text>'), w


def featured(theme, p):
    dark = theme == "dark"
    defs = (
        f'<clipPath id="cc"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22"/></clipPath>'
        f'<radialGradient id="glow" cx="86%" cy="4%" r="62%"><stop offset="0" stop-color="{p["brand"]}" '
        f'stop-opacity="{.22 if dark else .13}"/><stop offset=".55" stop-color="{p["brand"]}" '
        f'stop-opacity="{.04 if dark else .03}"/><stop offset="1" stop-color="{p["brand"]}" stop-opacity="0"/>'
        f'</radialGradient>'
        f'<radialGradient id="glow2" cx="4%" cy="100%" r="44%"><stop offset="0" stop-color="{p["grad_a"]}" '
        f'stop-opacity=".09"/><stop offset="1" stop-color="{p["grad_a"]}" stop-opacity="0"/></radialGradient>'
        + dot_grid("dots", p["grid"], 22, 1.15, .75 if dark else .9)
        + f'<linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0"><stop offset=".35" stop-color="#fff" '
          f'stop-opacity="0"/><stop offset=".8" stop-color="#fff" stop-opacity="1"/></linearGradient>'
          f'<mask id="gm"><rect width="{W}" height="{H}" fill="url(#fadeL)"/></mask>'
        + brand_gradient("mk", p, "100%", "100%")
        + shadow_filter("sh", p["shadow"], 10, 20)
        + shadow_filter("shs", p["shadow"], 3, 6)
    )
    b = [f'<g clip-path="url(#cc)">{rrect(0, 0, W, H, 22, p["canvas"])}'
         f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#gm)"/>'
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/><rect width="{W}" height="{H}" fill="url(#glow2)"/></g>',
         rrect(.5, .5, W - 1, H - 1, 22, "none", p["border"])]

    # ---- columna izquierda
    x0 = 48
    b.append(f'<g class="fade" {delay(0)}>{icon("star", x0, 52, 15, p["brand_text"], 2)}'
             f'{kicker(x0 + 23, 64, "proyecto destacado · full stack", p)}</g>')
    b.append(f'<text class="rise" {delay(1)} x="{x0 - 1}" y="110" font-size="32" font-weight="800" '
             f'letter-spacing="-.6" fill="{p["text"]}"><tspan x="{x0 - 1}">Aplicación web inspirada</tspan>'
             f'<tspan x="{x0 - 1}" dy="38">en League of Legends</tspan></text>')
    para, last = paragraph(x0, 190, FEAT["text"], p, size=15, max_width=440, lh=23, cls="rise", style=delay(2))
    b.append(para)
    y = last + 46
    for i, (label, repo) in enumerate((("Frontend", FEAT["front"]), ("Backend", FEAT["back"]))):
        g = [f'<g class="rise" {delay(3 + i)}>',
             glyph(REPO, x0, y - 12.5, 15, p["muted"], 2),
             f'<text x="{x0 + 22}" y="{y}" font-size="13.5" font-weight="650" fill="{p["text"]}">{label}'
             f'<tspan fill="{p["subtle"]}" font-weight="400"> · </tspan>'
             f'<tspan class="mono" font-size="13" font-weight="500" fill="{p["brand_text"]}">{esc(repo["repo"])}'
             f'</tspan></text>']
        cx = x0
        for t in repo["stack"]:
            svg, w = tag(cx, y + 11, t, p, tech_color(t, p))
            g.append(svg)
            cx += w + 6
        g.append("</g>")
        b.append("".join(g))
        y += 66

    # ---- ilustración: app (arriba) → API (abajo izquierda) → MongoDB (abajo derecha)
    wx, wy, ww, wh = 544, 40, 416, 162
    sx, sy, sw, sh = 544, 260, 228, 148
    mx0, mx1, my0, my1 = 850, 960, 278, 396
    b.append(f'<g class="win" style="animation-delay:.35s">{app_window(wx, wy, ww, wh, p)}</g>')
    b.append(f'<g class="win" style="animation-delay:.55s">{server_box(sx, sy, sw, sh, p)}</g>')
    b.append(f'<g class="win" style="animation-delay:.7s">{mongo(mx0, mx1, my0, my1, p)}</g>')

    # conectores app ⇄ API (dos carriles) con su etiqueta y el paquete que viaja
    top, bot = wy + wh, sy
    mid = (top + bot) / 2
    lanes = []
    for lx, kind in ((586, "req"), (748, "res")):
        lanes.append(f'<line x1="{lx}" y1="{top + 5}" x2="{lx}" y2="{bot - 5}" stroke="{p["border"]}" '
                     f'stroke-width="1.5" stroke-dasharray="2 4" stroke-linecap="round"/>')
    # flechas: la petición baja, la respuesta sube
    lanes.append(f'<path d="M581.5 {bot - 11}L586 {bot - 6}L590.5 {bot - 11}" stroke="{p["brand_text"]}" '
                 f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    lanes.append(f'<path d="M743.5 {top + 11}L748 {top + 6}L752.5 {top + 11}" stroke="{p["success"]}" '
                 f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    req, _ = lane_pill(598, mid - 12, [("GET", p["brand_text"], 700), (" /api/characters", p["text"], 500)], p)
    res, _ = lane_pill(760, mid - 12, [("200 OK", p["success"], 700), (" · JSON", p["text"], 500)], p)
    lanes.append(req + res)
    b.append(f'<g class="fade" style="animation-delay:.9s">{"".join(lanes)}</g>')
    b.append(f'<g class="req"><circle cx="586" cy="{mid}" r="7" fill="{p["brand"]}" fill-opacity=".22"/>'
             f'<rect x="582.5" y="{mid - 7}" width="7" height="14" rx="3.5" fill="{p["brand"]}"/></g>')
    b.append(f'<g class="res"><circle cx="748" cy="{mid}" r="7" fill="{p["success"]}" fill-opacity=".22"/>'
             f'<rect x="744.5" y="{mid - 7}" width="7" height="14" rx="3.5" fill="{p["success"]}"/></g>')

    # conector API ⇄ MongoDB: findAll()
    dy = sy + sh / 2
    l0, l1 = sx + sw + 6, mx0 - 6
    b.append(f'<g class="fade" style="animation-delay:1s">'
             f'<line x1="{l0}" y1="{dy}" x2="{l1}" y2="{dy}" stroke="{p["border"]}" stroke-width="1.5" '
             f'stroke-dasharray="2 4" stroke-linecap="round"/>'
             f'<text class="mono" x="{(l0 + l1) / 2:g}" y="{dy - 10:g}" font-size="11" fill="{p["muted"]}" '
             f'text-anchor="middle">findAll()</text></g>')
    b.append(f'<g class="db"><circle cx="{(l0 + l1) / 2:g}" cy="{dy}" r="7" fill="{TECH["MongoDB"]}" fill-opacity=".22"/>'
             f'<rect x="{(l0 + l1) / 2 - 7:g}" y="{dy - 3.5:g}" width="14" height="7" rx="3.5" '
             f'fill="{TECH["MongoDB"]}"/></g>')

    title = ("Proyecto destacado: aplicación web inspirada en League of Legends. Frontend en Angular 21 "
             "(app-lol) y API REST propia con Java 21, Spring Boot y MongoDB (league_of_legends).")
    desc = ("Diagrama animado de la arquitectura: la app Angular (localhost:4200) pide GET /api/characters, la API "
            "de Spring Boot (puerto 8080) consulta la colección characters de MongoDB con findAll() y devuelve "
            "200 OK con JSON; mientras tanto la app muestra un esqueleto de carga que se convierte en las tarjetas "
            "de personajes con sus etiquetas de rol (Tanque, Multirol).")
    return svg_doc(W, H, "".join(b), title=title, desc=desc, css=CSS_F, defs=defs)


# ============================================================ tarjetas pequeñas
SCHEMAS = {  # columnas reales (scripts SQL de cada repo); la FK va en 2.ª fila para alinear el conector
    "Api_products": {
        "slug": "api-products",
        "many": ("Producto", [("cod_barras", "pk"), ("categoria_id", "fk"), ("precio", None)]),
        "one": ("Categoria", [("id", "pk"), ("nombre", None)]),
        "rel": "@ManyToOne",
        "base": "/api/productos",
        "desc": "Esquema relacional: muchos productos pertenecen a una categoría (categoria_id → id).",
    },
    "ActBaseDatos": {
        "slug": "act-base-datos",
        "many": ("empleados", [("empleado_id", "pk"), ("departamento_id", "fk"), ("nombre_completo", None)]),
        "one": ("departamentos", [("departamento_id", "pk"), ("nombre_depto", None)]),
        "rel": "FOREIGN KEY",
        "base": "/api/empleados",
        "desc": ("Esquema relacional: muchos empleados pertenecen a un departamento "
                 "(departamento_id → departamento_id)."),
    },
}

CSS_S = f"""
.win{{animation:win .9s {EASE} backwards}}
@keyframes win{{from{{opacity:0;transform:translateY(12px)}}}}
.nudge{{animation:nudge 4.8s ease-in-out 2.4s infinite}}
@keyframes nudge{{0%,72%,100%{{transform:none}}80%{{transform:translate(2px,-2px)}}88%{{transform:none}}}}
.pk{{animation:pk 4.2s ease-in-out 1.6s infinite backwards}}
@keyframes pk{{0%,8%{{opacity:0;transform:translateX(0)}}14%,40%{{opacity:1}}46%,100%{{opacity:0;transform:translateX(var(--d))}}}}
.hl{{opacity:0;animation:hl 4.2s ease-in-out 1.6s infinite backwards}}
@keyframes hl{{0%,6%{{opacity:0}}14%,52%{{opacity:1}}66%,100%{{opacity:0}}}}
"""

ROW, HEAD = 17, 24


def table(x, y, w, name, rows, p, *, link_row) -> tuple[str, float, float]:
    """Tabla del esquema. Devuelve (svg, alto, y del centro de la fila enlazada)."""
    h = HEAD + ROW * len(rows) + 6
    out = [f'<g filter="url(#shs)">{rrect(x, y, w, h, 8, p["raised"], p["border"])}</g>',
           top_bar(x, y, w, HEAD, 8, p["surface"]),
           f'<line x1="{x:g}" y1="{y + HEAD:g}" x2="{x + w:g}" y2="{y + HEAD:g}" stroke="{p["border_soft"]}"/>',
           glyph(TABLE, x + 9, y + 6, 13, p["muted"], 1.9),
           f'<text class="mono" x="{x + 28:g}" y="{y + 16.3:g}" font-size="11.5" font-weight="700" '
           f'fill="{p["text"]}">{esc(name)}</text>']
    link_y = 0
    for i, (field, kind) in enumerate(rows):
        ry = y + HEAD + 3 + i * ROW
        cy = ry + ROW / 2
        if i == link_row:
            link_y = cy
            out.append(f'<g class="hl">{rrect(x + 3, ry, w - 6, ROW, 4, p["brand_soft"], None)}</g>')
        if kind == "pk":
            out.append(glyph(KEY, x + 9, cy - 6, 12, p["brand_text"], 2.1))
        elif kind == "fk":
            out.append(f'<text class="mono" x="{x + 15:g}" y="{cy + 3:g}" font-size="8" font-weight="700" '
                       f'fill="{p["muted"]}" text-anchor="middle">FK</text>')
        out.append(f'<text class="mono" x="{x + 28:g}" y="{cy + 3.8:g}" font-size="11" '
                   f'fill="{p["text"] if kind else p["muted"]}">{esc(field)}</text>')
    return "".join(out), h, link_y


def small_card(repo):
    o, s = OTHERS[repo], SCHEMAS[repo]

    def build(theme, p):
        dark = theme == "dark"
        well = p["canvas"] if dark else p["surface"]
        base = p["surface"] if dark else p["canvas"]
        defs = (f'<clipPath id="cc"><rect x=".5" y=".5" width="{SW - 1}" height="{SH - 1}" rx="18"/></clipPath>'
                + dot_grid("dots", p["grid"], 16, 1, .8 if dark else 1)
                + '<radialGradient id="dfade" cx="50%" cy="50%" r="70%"><stop offset=".2" stop-color="#fff" '
                  'stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></radialGradient>'
                + f'<mask id="dm"><rect width="{SW}" height="{COVER}" fill="url(#dfade)"/></mask>'
                + f'<radialGradient id="glow" cx="92%" cy="0%" r="80%"><stop offset="0" stop-color="{p["brand"]}" '
                  f'stop-opacity="{.18 if dark else .11}"/><stop offset="1" stop-color="{p["brand"]}" '
                  f'stop-opacity="0"/></radialGradient>'
                + shadow_filter("shs", p["shadow"], 4, 8))
        b = [card(0, 0, SW, SH, p, fill=base),
             f'<g clip-path="url(#cc)"><rect width="{SW}" height="{COVER}" fill="{well}"/>'
             f'<rect width="{SW}" height="{COVER}" fill="url(#dots)" mask="url(#dm)"/>'
             f'<rect width="{SW}" height="{COVER}" fill="url(#glow)"/></g>',
             f'<line x1="1" y1="{COVER + .5}" x2="{SW - 1}" y2="{COVER + .5}" stroke="{p["border"]}"/>',
             card(0, 0, SW, SH, p, fill="none")]

        # ---- esquema: tabla «muchos» ⟶ tabla «uno»
        tw, gap = 150, 92
        lx = (SW - (tw * 2 + gap)) / 2
        rx = lx + tw + gap
        ty = 18
        (mname, mrows), (oname, orows) = s["many"], s["one"]
        lsvg, lh, ly = table(lx, ty, tw, mname, mrows, p, link_row=1)
        rsvg, rh, _ = table(rx, ty + ROW, tw, oname, orows, p, link_row=0)
        b.append(f'<g class="win" style="animation-delay:.1s">{lsvg}</g>')
        b.append(f'<g class="win" style="animation-delay:.25s">{rsvg}</g>')
        x1, x2 = lx + tw, rx
        c = p["brand_text"]
        # pata de gallo (muchos) en la tabla izquierda y doble barra (uno) en la derecha
        rel = (f'<line class="draw" pathLength="1" x1="{x1:g}" y1="{ly:g}" x2="{x2:g}" y2="{ly:g}" stroke="{c}" '
               f'stroke-width="1.6" style="animation-delay:.55s"/>'
               f'<g class="fade" style="animation-delay:.9s" stroke="{c}" stroke-width="1.6" stroke-linecap="round">'
               f'<path d="M{x1 + 12:g} {ly:g}L{x1:g} {ly - 6:g}M{x1 + 12:g} {ly:g}L{x1:g} {ly + 6:g}" fill="none"/>'
               f'<path d="M{x2 - 8:g} {ly - 6:g}V{ly + 6:g}M{x2 - 13:g} {ly - 6:g}V{ly + 6:g}"/></g>'
               f'<g class="fade" style="animation-delay:1s">'
               f'<text class="mono" x="{(x1 + x2) / 2:g}" y="{ly - 9:g}" font-size="11" font-weight="700" '
               f'fill="{p["text"]}" text-anchor="middle">N : 1</text>'
               f'<text class="mono" x="{(x1 + x2) / 2:g}" y="{ly + 19:g}" font-size="10" fill="{p["muted"]}" '
               f'text-anchor="middle">{esc(s["rel"])}</text></g>')
        b.append(rel)
        d = x2 - x1 - 34
        b.append(f'<g class="pk" style="--d:{d:g}px"><circle cx="{x1 + 17:g}" cy="{ly:g}" r="6" fill="{p["brand"]}" '
                 f'fill-opacity=".25"/><circle cx="{x1 + 17:g}" cy="{ly:g}" r="3.2" fill="{p["brand"]}"/></g>')

        # ---- ficha
        x0, y0 = 24, COVER + 40
        b.append(f'<g class="rise" {delay(0, base=.35)}><text x="{x0}" y="{y0}" font-size="21" font-weight="800" '
                 f'letter-spacing="-.3" fill="{p["text"]}">{esc(o["title"])}</text>'
                 f'{glyph(REPO, x0, y0 + 11, 15, p["muted"], 2)}'
                 f'<text class="mono" x="{x0 + 22}" y="{y0 + 23.5}" font-size="13.5" fill="{p["brand_text"]}">'
                 f'{esc(o["repo"])}</text></g>')
        lines = wrap(o["text"], 14.5, SW - 2 * x0)
        spans = "".join(f'<tspan x="{x0}" dy="{0 if i == 0 else 21}">{esc(l)}</tspan>' for i, l in enumerate(lines))
        b.append(f'<text class="rise" {delay(1, base=.35)} x="{x0}" y="{y0 + 52}" font-size="14.5" '
                 f'fill="{p["muted"]}">{spans}</text>')
        # lenguajes (puntos tipo GitHub) + ruta base de la API a la derecha
        ly2 = SH - 22
        row, cx = [f'<g class="rise" {delay(2, base=.35)}>'], x0
        for t in o["stack"]:
            row.append(f'<circle cx="{cx + 5:g}" cy="{ly2 - 4.5:g}" r="5" fill="{tech_color(t, p)}"/>'
                       f'<text x="{cx + 15:g}" y="{ly2:g}" font-size="13" fill="{p["muted"]}">{esc(t)}</text>')
            cx += 15 + text_width(t, 13) + 16
        bw = text_width(s["base"], 12.5, mono=True)
        row.append(glyph(ROUTE, SW - x0 - bw - 21, ly2 - 12, 15, p["subtle"], 2)
                   + f'<text class="mono" x="{SW - x0:g}" y="{ly2:g}" font-size="12.5" fill="{p["muted"]}" '
                     f'text-anchor="end">{esc(s["base"])}</text></g>')
        b.append("".join(row))
        # botón ↗ (como en el portfolio)
        bx, by, r = SW - x0 - 20, COVER + 36, 20
        b.append(f'<g class="pop" {delay(3, base=.35)}>'
                 f'<circle cx="{bx}" cy="{by}" r="{r - .5}" fill="{p["brand_soft"]}" stroke="{p["brand_line"]}"/>'
                 f'<g class="nudge">{icon("external", bx - 9, by - 9, 18, p["brand_text"], 2.3)}</g></g>')

        title = f"{o['title']} — {o['repo']}: {o['text']}"
        desc = (f"Tarjeta del repositorio {o['repo']} ({', '.join(o['stack'])}). {s['desc']} "
                f"Ruta base de la API: {s['base']}.")
        return svg_doc(SW, SH, "".join(b), title=title, desc=desc, css=CSS_S, defs=defs)

    return build


# ------------------------------------------------------------------- salida
def main():
    paths = write_themed("projects/lol", featured)
    for repo, sch in SCHEMAS.items():
        paths += write_themed(f"projects/{sch['slug']}", small_card(repo))
    return paths


def snippet() -> str:
    """Fragmento HTML/Markdown para el README."""
    f = FEAT
    out = [
        '<p align="center">\n  '
        + picture("projects/lol", "Proyecto destacado: aplicación web inspirada en League of Legends, con frontend "
                  "en Angular 21 y API REST propia en Spring Boot y MongoDB", width="100%", href=f["front"]["url"])
        + "\n</p>\n",
        f'<p align="center">\n  <b>Frontend</b> → <a href="{f["front"]["url"]}"><code>{f["front"]["repo"]}</code></a>'
        f' &nbsp;·&nbsp; <b>Backend</b> → <a href="{f["back"]["url"]}"><code>{f["back"]["repo"]}</code></a>\n</p>\n',
    ]
    pics = [picture(f"projects/{SCHEMAS[o['repo']]['slug']}", f"{o['title']} ({o['repo']}): {o['text']}",
                    width="49%", href=o["url"], title=f"{o['repo']} en GitHub")
            for o in C.PROJECTS["others"]]
    out.append(f'<p align="center">\n  {pics[0]}\n  {pics[1]}\n</p>\n')
    rows = "\n".join(f"| [{c['repo']}]({C.GITHUB}/{c['repo']}) | {c['text']} |" for c in C.PROJECTS["class"])
    out.append("<details>\n<summary><b>Más prácticas de clase</b></summary>\n<br>\n\n"
               "| Repositorio | Qué es |\n| :-- | :-- |\n" + rows + "\n\n</details>\n")
    return "\n".join(out)


if __name__ == "__main__":
    for path in main():
        print(path, f"{os.path.getsize(path) / 1024:.1f} KB")
