"""Kit de interfaz del perfil: pills de navegación, cabeceras de sección, matriz de stack,
botones de contacto y pie con el monograma «NG».

    python scripts/build.py ui_kit                 →  assets/nav/, assets/sections/, assets/stack/,
                                                      assets/contact/ y assets/footer/
    python scripts/components/ui_kit.py --snippet  →  imprime el HTML que se pega en el README
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import (EASE, TECH, THEMES, brand_gradient, chip, dot_grid, esc, icon,  # noqa: E402
                   picture, rrect, svg_doc, text_width, write_themed)
import content as C  # noqa: E402

# --------------------------------------------------------------------------- contenido
NAV = [  # (ancla, texto, icono)
    ("sobre-mi", "Sobre mí", "user"),
    ("stack", "Stack", "layers"),
    ("experiencia", "Experiencia", "briefcase"),
    ("portfolio", "Portfolio", "store"),
    ("proyectos", "Proyectos", "code"),
    ("formacion", "Formación", "cap"),
    ("actividad", "Actividad", "chart"),
    ("juega", "Juega", "gamepad"),
    ("contacto", "Contacto", "mail"),
]
CTA_SLUG = "contacto"
NAV_BREAK = 5            # en el README: 5 pills arriba y 4 abajo (dos filas equilibradas)

SECTIONS = [  # (número, ancla, título, subtítulo, icono)
    ("01", "sobre-mi", "Sobre mí", "Quién soy, de dónde vengo y qué busco", "user"),
    ("02", "stack", "Stack", "Las herramientas con las que trabajo", "layers"),
    ("03", "experiencia", "Experiencia", f"{C.EXPERIENCE['duration']} haciendo e-commerce real", "briefcase"),
    ("04", "portfolio", "Portfolio", "Webs y tiendas online en las que he trabajado", "store"),
    ("05", "proyectos", "Proyectos", "Lo que construyo en el ciclo de DAW", "code"),
    ("06", "formacion", "Formación", "De SMR a DAW, con certificaciones de Google", "cap"),
    ("07", "actividad", "Actividad", "Mis números en GitHub, actualizados cada día", "chart"),
    ("08", "juega", "Juega", "Tres en raya, un monograma en 3D y alguna sorpresa", "gamepad"),
    ("09", "contacto", "Contacto", "¿Hablamos? Te respondo rápido", "mail"),
]

# Lo que rodea al código (los lenguajes y frameworks principales van como iconos encima).
STACK_GROUPS = [
    ("E-commerce y CMS", "store", ["WordPress", "WooCommerce", "PrestaShop 1.7", "Divi", "Elementor", "Astra",
                                   "WoodMart", "WPBakery", "FiboSearch", "Moodle"]),
    ("Pagos y envíos", "card", ["Redsys · Bizum", "PayPal", "Klarna", "Sendcloud", "GLS"]),
    ("Marketing y marketplaces", "trend", ["Google Merchant Center", "Google Ads", "Google Analytics",
                                           "Tag Manager", "Channable", "SEO / SEM", "Google Shopping",
                                           "TikTok Shop", "eBay", "Amazon"]),
    ("Hosting y seguridad", "shield", ["IONOS", "Cloudflare", "DNS", "Apache2", "OPcache", "Wordfence",
                                       "UpdraftPlus"]),
    ("Sistemas y redes", "server", ["Ubuntu Server", "Debian", "Windows Server", "Active Directory",
                                    "DNS y DHCP", "VirtualBox", "XAMPP"]),
    ("Herramientas", "wrench", ["Git", "GitHub", "IntelliJ IDEA", "Eclipse", "NetBeans", "Maven", "Swagger",
                                "Lombok", "IA (Claude, ChatGPT)"]),
]
# Color del punto: el de brand.TECH (directo o por familia); el resto, un neutro de la paleta.
DOT_ALIAS = {"PrestaShop 1.7": "PrestaShop", "Apache2": "Apache", "OPcache": "PHP",
             "Ubuntu Server": "Linux", "Debian": "Linux", "Tag Manager": "Google"}

CONTACT = [  # (id, título, detalle, enlace)
    ("email", "Escríbeme", C.EMAIL, f"mailto:{C.EMAIL}"),
    ("linkedin", "LinkedIn", C.NAME, C.LINKEDIN),
    ("github", "GitHub", f"@{C.GITHUB_USER}", C.GITHUB),
]

FOOT_TITLE = "Gracias por pasarte por mi perfil"
FOOT_SUB = ("Hecho con SVG, Python y GitHub Actions", "El Viso del Alcor, Sevilla")

# Holgura para fuentes más anchas que la estimación (Noto Sans mide hasta un ~6 % más).
SAFE = 1.06


# --------------------------------------------------------------------------- color
def _rgb(h: str) -> tuple[int, ...]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(_rgb(a), _rgb(b)))


def contrast(a: str, b: str) -> float:
    def lum(h):
        ch = [c / 255 for c in _rgb(h)]
        ch = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
        return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# Superficies con texto blanco: variante profunda del naranja de marca. Los dos extremos son
# tokens de la paleta (brand_strong → brand_text del tema claro) y el degradado arranca antes
# del borde (CTA_X1 < 0) para que el texto blanco supere 4.5:1 en todo su recorrido.
CTA_A, CTA_B = THEMES["light"]["brand_strong"], THEMES["light"]["brand_text"]
CTA_X1 = -0.3


def cta_color(t: float) -> str:
    """Color del degradado CTA en la fracción horizontal t (0 = borde izquierdo)."""
    return mix(CTA_A, CTA_B, min(1.0, max(0.0, (t - CTA_X1) / (1 - CTA_X1))))


def check_white_text(x0: float, box_x: float, box_w: float, what: str) -> None:
    c = contrast("#ffffff", cta_color((x0 - box_x) / box_w))
    assert c >= 4.5, f"{what}: el texto blanco solo tiene {c:.2f}:1"


def cta_defs(uid: str, x: float, y: float, w: float, h: float, r: float) -> str:
    """Degradado CTA + brillo superior + resplandor ámbar + barrido de luz, recortados a la forma."""
    return (f'<linearGradient id="{uid}g" x1="{CTA_X1}" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{CTA_A}"/><stop offset="1" stop-color="{CTA_B}"/></linearGradient>'
            f'<linearGradient id="{uid}hl" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#ffffff" stop-opacity=".22"/>'
            f'<stop offset=".48" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="{uid}am" cx="0" cy="0" r=".42">'
            f'<stop offset="0" stop-color="{THEMES["dark"]["grad_a"]}" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="{THEMES["dark"]["grad_a"]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{uid}sh" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#ffffff" stop-opacity=".34"/>'
            f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="{uid}c">{rrect(x, y, w, h, r)}</clipPath>')


def cta_body(uid: str, x: float, y: float, w: float, h: float, r: float) -> str:
    """Relleno CTA con su brillo; el barrido (clase .sheen) parte fuera de la forma."""
    band = 46
    return (rrect(x, y, w, h, r, f"url(#{uid}g)")
            + f'<g clip-path="url(#{uid}c)">'
            + f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#{uid}am)"/>'
            + f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#{uid}hl)"/>'
            + f'<path class="sheen" d="M{x - band - h * .35:g} {y + h:g}l{h * .35:g} {-h:g}h{band:g}l{-h * .35:g} {h:g}Z" '
              f'fill="url(#{uid}sh)"/></g>'
            + rrect(x + .5, y + .5, w - 1, h - 1, r - .5, "none", "#ffffff", 1, 'stroke-opacity=".2"'))


def sheen_css(travel: float, delay: float, period: float = 6.5) -> str:
    move = 1.1 / period * 100
    return (f".sheen{{animation:sheen {period}s {delay}s cubic-bezier(.45,0,.3,1) infinite backwards}}"
            f"@keyframes sheen{{0%{{transform:translateX(0)}}{move:.1f}%,100%{{transform:translateX({travel:g}px)}}}}")


# --------------------------------------------------------------------------- 1) pills
NAV_H, PILL_H, NAV_M = 44, 40, 2


def nav_pill(i: int, slug: str, label: str, ic: str):
    """Pill de navegación. Devuelve fn(theme, p) para write_themed."""
    cta = slug == CTA_SLUG
    fs, isz, gap, pad = 15, 18, 8, 16
    tw = text_width(label, fs, 600)
    pw = math.ceil(pad + isz + gap + tw + pad)
    W = pw + 2 * NAV_M
    x0, y0 = NAV_M, (NAV_H - PILL_H) / 2
    ix, iy = x0 + pad, y0 + (PILL_H - isz) / 2
    tx = ix + isz + gap
    ty = y0 + PILL_H / 2 + fs * .355
    if cta:
        check_white_text(tx, x0, pw, f"pill {label}")

    def build(theme, p):
        css = (f".nin{{animation:nin .6s {EASE} backwards}}"
               f"@keyframes nin{{from{{opacity:0;transform:translateY(5px)}}}}")
        d = f'style="animation-delay:{.05 + i * .05:.2f}s"'
        defs = ""
        if cta:
            uid = "k"
            defs = cta_defs(uid, x0, y0, pw, PILL_H, PILL_H / 2)
            css += sheen_css(pw + 120, 1.4)
            shape = cta_body(uid, x0, y0, pw, PILL_H, PILL_H / 2)
            ink, txt = "#ffffff", "#ffffff"
        else:
            shape = rrect(x0 + .5, y0 + .5, pw - 1, PILL_H - 1, (PILL_H - 1) / 2, p["surface"], p["border"])
            ink, txt = p["brand_text"], p["text"]
        body = (f'<g class="nin" {d}>{shape}{icon(ic, ix, iy, isz, ink, 2)}'
                f'<text x="{tx:g}" y="{ty:.1f}" font-size="{fs}" font-weight="600" fill="{txt}">{esc(label)}</text></g>')
        desc = ("Botón principal: ir a la sección de contacto del perfil." if cta
                else f"Botón de navegación: ir a la sección «{label}» del perfil.")
        return svg_doc(W, NAV_H, body, title=f"Ir a {label}", desc=desc, css=css, defs=defs)

    return build


# --------------------------------------------------------------------------- 2) cabeceras
SEC_W, SEC_H = 1000, 128


def section_header(k: int, nn: str, slug: str, title: str, sub: str, ic: str):
    """Cabecera de sección: insignia con el número, título, subtítulo y una línea que viaja
    desde el final del título hasta el icono de la sección."""
    bx, by, bs = 4, 36, 56                       # insignia
    tx = bx + bs + 22                            # columna de texto
    ty, sy = 62, 91                              # líneas base: título / subtítulo
    ls = -0.9                                    # letter-spacing del título
    tw = text_width(title, 34, 800) + ls * (len(title) - 1)
    sw = text_width(sub, 16)
    cr = 24                                      # círculo del icono
    cx, cy = SEC_W - 4 - cr, 50                  # alineado con el título
    lx0 = tx + tw * SAFE + 18                    # la línea arranca tras el título
    lx1 = cx - cr - 12
    assert lx1 - lx0 > 200, f"{title}: no queda sitio para la línea"
    assert tx + sw * SAFE < SEC_W - 12, f"{sub}: el subtítulo no cabe"
    spark_w = 110
    travel = lx1 - lx0 + spark_w
    # Cada cabecera arranca su bucle con un pequeño desfase para que no vayan todas a la vez.
    loop_d = 2.6 + (k % 3) * .6

    def build(theme, p):
        dark = theme == "dark"
        defs = (f'<linearGradient id="ln" gradientUnits="userSpaceOnUse" x1="{lx0:g}" y1="0" x2="{lx1:g}" y2="0">'
                f'<stop offset="0" stop-color="{p["brand"]}" stop-opacity=".95"/>'
                f'<stop offset=".55" stop-color="{p["brand"]}" stop-opacity="{.42 if dark else .38}"/>'
                f'<stop offset="1" stop-color="{p["border"]}"/></linearGradient>'
                f'<linearGradient id="sp" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0" stop-color="{p["grad_a"]}" stop-opacity="0"/>'
                f'<stop offset=".7" stop-color="{p["grad_a"] if dark else p["brand"]}"/>'
                f'<stop offset="1" stop-color="{p["grad_a"] if dark else p["brand"]}" stop-opacity="0"/></linearGradient>'
                f'<clipPath id="lc"><rect x="{lx0:g}" y="{cy - 4}" width="{lx1 - lx0:g}" height="8"/></clipPath>')
        css = (f".spark{{animation:spark 8s {loop_d:.1f}s cubic-bezier(.45,0,.25,1) infinite backwards}}"
               f"@keyframes spark{{0%{{transform:translateX(0)}}21%,100%{{transform:translateX({travel:g}px)}}}}"
               f".ring{{opacity:0;animation:ring 8s {loop_d:.1f}s ease-out infinite backwards;"
               f"transform-box:fill-box;transform-origin:center}}"
               f"@keyframes ring{{0%,17%{{opacity:0;transform:scale(1)}}20%{{opacity:.75;transform:scale(1)}}"
               f"38%,100%{{opacity:0;transform:scale(1.5)}}}}")
        b = []
        # insignia con el número
        b.append(f'<g class="pop" style="animation-delay:.05s">'
                 + rrect(bx + .5, by + .5, bs - 1, bs - 1, 16, p["brand_soft"], p["brand_line"])
                 + f'<text class="mono" x="{bx + bs / 2:g}" y="{by + bs / 2 + 7:g}" font-size="20" font-weight="700" '
                   f'fill="{p["brand_text"]}" text-anchor="middle" letter-spacing=".5">{esc(nn)}</text></g>')
        # título y subtítulo
        b.append(f'<text class="rise" style="animation-delay:.12s" x="{tx}" y="{ty}" font-size="34" font-weight="800" '
                 f'letter-spacing="{ls}" fill="{p["text"]}">{esc(title)}</text>')
        b.append(f'<text class="fade" style="animation-delay:.3s" x="{tx}" y="{sy}" font-size="16" '
                 f'fill="{p["muted"]}">{esc(sub)}</text>')
        # línea que se dibuja + chispa que la recorre
        b.append(f'<circle class="pop" style="animation-delay:.42s" cx="{lx0:g}" cy="{cy}" r="3.2" fill="{p["brand"]}"/>')
        b.append(f'<line class="draw" style="animation-delay:.5s;animation-duration:1.15s" pathLength="1" '
                 f'x1="{lx0:g}" y1="{cy}" x2="{lx1:g}" y2="{cy}" stroke="url(#ln)" stroke-width="1.5" '
                 f'stroke-linecap="round"/>')
        b.append(f'<g clip-path="url(#lc)"><rect class="spark" x="{lx0 - spark_w:g}" y="{cy - 1.5}" '
                 f'width="{spark_w}" height="3" rx="1.5" fill="url(#sp)"/></g>')
        # círculo con el icono (se «enciende» cuando llega la chispa)
        b.append(f'<circle class="ring" cx="{cx}" cy="{cy}" r="{cr - .5}" stroke="{p["brand"]}" stroke-width="1.5"/>')
        b.append(f'<g class="pop" style="animation-delay:1.3s">'
                 f'<circle cx="{cx}" cy="{cy}" r="{cr - .5}" fill="{p["surface"]}" stroke="{p["brand_line"]}"/>'
                 f'{icon(ic, cx - 11, cy - 11, 22, p["brand_text"], 1.9)}</g>')
        return svg_doc(SEC_W, SEC_H, "".join(b), title=f"{nn} · {title}",
                       desc=f"Cabecera de la sección {int(nn)}: {title}. {sub}.", css=css, defs=defs)

    return build


# --------------------------------------------------------------------------- 3) matriz
MX0, MX1 = 40, 960            # columna de contenido
M_LABEL_TILE = 36
M_CHIP_X = 316                # inicio de los chips (columna de grupos ≈ 230 px + aire)
M_CHIP_H, M_CHIP_FS = 30, 14
M_GAP_X, M_GAP_Y = 8, 10
M_PAD_Y = 24                  # aire arriba/abajo de cada fila


def chip_width(label: str) -> float:
    # misma fórmula que brand.chip (relleno 11 + punto 14 + texto)
    return 22 + 14 + text_width(label, M_CHIP_FS, 500)


def pack(labels: list[str], width: float) -> list[list[tuple[str, float]]]:
    lines, cur, used = [], [], 0.0
    for lab in labels:
        w = chip_width(lab)
        need = w if not cur else used + M_GAP_X + w
        if cur and need > width:
            lines.append(cur)
            cur, used = [], 0.0
            need = w
        cur.append((lab, w))
        used = need
    if cur:
        lines.append(cur)
    return lines


def matrix_layout():
    width = MX1 - M_CHIP_X
    rows, y = [], M_PAD_Y + 6
    for name, ic, labels in STACK_GROUPS:
        lines = pack(labels, width)
        block = len(lines) * M_CHIP_H + (len(lines) - 1) * M_GAP_Y
        h = max(M_LABEL_TILE, block + 3)
        rows.append(dict(name=name, icon=ic, lines=lines, y=y, h=h))
        y += h + 2 * M_PAD_Y
    return rows, y - M_PAD_Y + 6


def dot_for(label: str, p: dict) -> str:
    return TECH.get(DOT_ALIAS.get(label, label)) or (TECH["Google"] if label.startswith("Google") else p["subtle"])


def stack_matrix(theme, p):
    dark = theme == "dark"
    rows, H = matrix_layout()
    W = 1000
    lbl_x = MX0 + M_LABEL_TILE + 14
    for r in rows:
        assert lbl_x + text_width(r["name"], 16, 700) * SAFE < M_CHIP_X - 14, f"{r['name']} invade los chips"
    chip_fill = p["raised"]
    defs = (f'<clipPath id="mc"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18"/></clipPath>'
            + dot_grid("md", p["grid"], 22, 1.1, .8 if dark else .95)
            + f'<radialGradient id="mdm" cx="100%" cy="0%" r="55%"><stop offset="0" stop-color="#fff" stop-opacity=".85"/>'
              f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
              f'<mask id="mdk"><rect width="{W}" height="{H}" fill="url(#mdm)"/></mask>'
              f'<radialGradient id="mg" cx="96%" cy="0%" r="48%">'
              f'<stop offset="0" stop-color="{p["brand"]}" stop-opacity="{.13 if dark else .08}"/>'
              f'<stop offset="1" stop-color="{p["brand"]}" stop-opacity="0"/></radialGradient>')
    css = (f".cin{{animation:cin .5s {EASE} backwards;transform-box:fill-box;transform-origin:center}}"
           f"@keyframes cin{{from{{opacity:0;transform:translateY(6px) scale(.94)}}}}")
    b = [rrect(.5, .5, W - 1, H - 1, 18, p["surface"], p["border"]),
         f'<g clip-path="url(#mc)"><rect width="{W}" height="{H}" fill="url(#md)" mask="url(#mdk)"/>'
         f'<rect width="{W}" height="{H}" fill="url(#mg)"/></g>']
    n = 0
    for ri, r in enumerate(rows):
        y = r["y"]
        t0 = .1 + ri * .14
        # separador sobre la fila (menos en la primera)
        if ri:
            sep_y = y - M_PAD_Y - .5
            b.append(f'<line class="draw" style="animation-delay:{t0:.2f}s;animation-duration:1s" pathLength="1" '
                     f'x1="{MX0}" y1="{sep_y:g}" x2="{MX1}" y2="{sep_y:g}" '
                     f'stroke="{p["border_soft"] if dark else p["border"]}" stroke-opacity="{1 if dark else .75}"/>')
        # etiqueta del grupo
        ty = y + M_LABEL_TILE / 2 + 16 * .35
        b.append(f'<g class="slide" style="animation-delay:{t0:.2f}s">'
                 + rrect(MX0 + .5, y + .5, M_LABEL_TILE - 1, M_LABEL_TILE - 1, 10, p["brand_soft"], p["brand_line"])
                 + icon(r["icon"], MX0 + 8, y + 8, 20, p["brand_text"], 1.9)
                 + f'<text x="{lbl_x}" y="{ty:.1f}" font-size="16" font-weight="700" letter-spacing="-.1" '
                   f'fill="{p["text"]}">{esc(r["name"])}</text></g>')
        # chips
        cy = y + 3
        for line in r["lines"]:
            cx = M_CHIP_X
            for lab, w in line:
                dot = dot_for(lab, p)
                svg, cw = chip(cx, cy, lab, p, dot=dot, size=M_CHIP_FS, h=M_CHIP_H, fill=chip_fill)
                ring = ""
                if contrast(dot, chip_fill) < 1.9:      # puntos claros sobre claro / oscuros sobre oscuro
                    ring = (f'<circle cx="{cx + 15:g}" cy="{cy + M_CHIP_H / 2:g}" r="4.5" fill="none" '
                            f'stroke="{p["text"]}" stroke-opacity=".28"/>')
                b.append(f'<g class="cin" style="animation-delay:{t0 + .12 + n * .022:.3f}s">{svg}{ring}</g>')
                assert abs(cw - w) < .01 and cx + cw <= MX1 + .01
                cx += w + M_GAP_X
                n += 1
            cy += M_CHIP_H + M_GAP_Y
    groups = "; ".join(f"{name}: {', '.join(labels)}" for name, _, labels in STACK_GROUPS)
    return svg_doc(W, H, "".join(b), title="Herramientas y servicios con los que trabajo",
                   desc=f"Matriz de stack por grupos. {groups}.", css=css, defs=defs)


# --------------------------------------------------------------------------- 4) contacto
CB_W, CB_H, CB_R = 288, 68, 18
CB_TILE, CB_TX = 40, 14


def contact_button(i: int, kind: str, title: str, detail: str, href: str):
    primary = kind == "email"
    tile_y = (CB_H - CB_TILE) / 2
    lx = CB_TX + CB_TILE + 12                    # columna de texto
    ax = CB_W - 12 - 14                          # flecha
    room = ax - 8 - lx
    assert text_width(detail, 13) * SAFE <= room, f"{detail} no cabe ({room}px)"
    assert text_width(title, 16, 700) * SAFE <= room
    if primary:
        check_white_text(lx, 0, CB_W, f"botón {kind}")

    def build(theme, p):
        x, y, w, h = 1, 1, CB_W - 2, CB_H - 2
        css = (f".cin{{animation:cin .7s {EASE} backwards}}"
               f"@keyframes cin{{from{{opacity:0;transform:translateY(8px)}}}}")
        defs = ""
        b = [f'<g class="cin" style="animation-delay:{.05 + i * .1:.2f}s">']
        if primary:
            defs = cta_defs("e", x, y, w, h, CB_R)
            css += sheen_css(CB_W + 160, 1.8, 7)
            css += (".nudge{animation:nudge 7s 1.8s ease-in-out infinite}"
                    "@keyframes nudge{0%,12%,24%,100%{transform:none}18%{transform:translateX(3px)}}")
            b.append(cta_body("e", x, y, w, h, CB_R))
            b.append(rrect(CB_TX + .5, tile_y + .5, CB_TILE - 1, CB_TILE - 1, 10, "#ffffff", "#ffffff", 1,
                           'fill-opacity=".16" stroke-opacity=".3"'))
            b.append(icon("mail", CB_TX + 9, tile_y + 9, 22, "#ffffff", 2))
            t_col = d_col = arr = "#ffffff"
        else:
            b.append(rrect(x + .5, y + .5, w - 1, h - 1, CB_R - .5, p["surface"], p["border"]))
            if kind == "linkedin":
                # El logo de brand.icon ya es un cuadrado redondeado: se escala para que sea la propia baldosa.
                s = CB_TILE * 24 / 20
                b.append(icon("linkedin", CB_TX - s / 12, tile_y - s / 12, s, "#0a66c2"))
            else:
                b.append(rrect(CB_TX, tile_y, CB_TILE, CB_TILE, 9, p["text"]))
                b.append(icon("github", CB_TX + 8, tile_y + 8, 24, p["canvas"]))
            t_col, d_col, arr = p["text"], p["muted"], p["muted"]
        b.append(f'<text x="{lx}" y="30" font-size="16" font-weight="700" fill="{t_col}">{esc(title)}</text>')
        b.append(f'<text x="{lx}" y="49" font-size="13" fill="{d_col}">{esc(detail)}</text>')
        arrow = icon("arrow" if primary else "external", ax, CB_H / 2 - 7, 14, arr, 2.2)
        b.append(f'<g class="nudge">{arrow}</g>' if primary else arrow)
        b.append("</g>")
        names = {"email": "correo electrónico", "linkedin": "LinkedIn", "github": "GitHub"}
        return svg_doc(CB_W, CB_H, "".join(b), title=f"{title}: {detail}",
                       desc=f"Botón de contacto por {names[kind]}.", css=css, defs=defs)

    return build


# --------------------------------------------------------------------------- 5) pie
FT_W, FT_H = 1000, 180
NG_A = "M22 72V28L46 72H67a12 12 0 0 0 12-12V52H63"      # N + panza y travesaño de la G
NG_B = "M79 28H56a10 10 0 0 0-10 10V72"                    # brazo superior de la G + asta compartida


def monogram(x: float, y: float, s: float, color: str, sw: float = 7.5, delay: float = .5) -> str:
    """Monograma «NG» de un solo trazo: la segunda asta de la N es también el lomo de la G.
    Dibujado en una caja de 100×100 escalada a s."""
    k = s / 100
    return (f'<g transform="translate({x:g} {y:g}) scale({k:g})" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path class="draw" style="animation-delay:{delay:.2f}s;animation-duration:1.3s" pathLength="1" d="{NG_A}"/>'
            f'<path class="draw" style="animation-delay:{delay + .75:.2f}s;animation-duration:.9s" pathLength="1" d="{NG_B}"/>'
            f'</g>')


def footer(theme, p):
    dark = theme == "dark"
    W, H = FT_W, FT_H
    S = 64
    tx, ty = W / 2 - S / 2, 16
    ly = ty + S / 2
    gap = 22
    l0, l1 = 150, tx - gap                   # línea izquierda
    r0, r1 = tx + S + gap, W - 150           # línea derecha
    glint = 90
    title_y, sub_y = 128, 157
    assert text_width(FOOT_TITLE, 26, 800) * SAFE < W - 48
    defs = (brand_gradient("ft", p, x2="100%", y2="100%")
            + f'<filter id="fg" x="-40%" y="-40%" width="180%" height="190%">'
              f'<feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="{p["brand"]}" flood-opacity="{.4 if dark else .28}"/></filter>'
            + f'<linearGradient id="la" gradientUnits="userSpaceOnUse" x1="{l0}" y1="0" x2="{l1:g}" y2="0">'
              f'<stop offset="0" stop-color="{p["grad_a"]}" stop-opacity="0"/>'
              f'<stop offset="1" stop-color="{p["grad_b"]}"/></linearGradient>'
            + f'<linearGradient id="lb" gradientUnits="userSpaceOnUse" x1="{r0:g}" y1="0" x2="{r1}" y2="0">'
              f'<stop offset="0" stop-color="{p["grad_b"]}"/>'
              f'<stop offset="1" stop-color="{p["grad_a"]}" stop-opacity="0"/></linearGradient>'
            + f'<linearGradient id="gl" x1="0" y1="0" x2="1" y2="0">'
              f'<stop offset="0" stop-color="{p["grad_a"]}" stop-opacity="0"/>'
              f'<stop offset=".5" stop-color="{"#ffffff" if dark else p["grad_a"]}"/>'
              f'<stop offset="1" stop-color="{p["grad_a"]}" stop-opacity="0"/></linearGradient>'
            + f'<clipPath id="ca"><rect x="{l0}" y="{ly - 3}" width="{l1 - l0:g}" height="6"/></clipPath>'
            + f'<clipPath id="cb"><rect x="{r0:g}" y="{ly - 3}" width="{r1 - r0:g}" height="6"/></clipPath>'
            + f'<clipPath id="ct">{rrect(tx, ty, S, S, 19)}</clipPath>'
            + f'<linearGradient id="ts" x1="0" y1="0" x2="1" y2="0">'
              f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".38"/>'
              f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    span = l1 - l0 + glint
    css = (f".gla{{animation:gla 7s 2.4s cubic-bezier(.45,0,.3,1) infinite backwards}}"
           f"@keyframes gla{{0%{{transform:translateX(0)}}30%,100%{{transform:translateX({-span:g}px)}}}}"
           f".glb{{animation:glb 7s 2.4s cubic-bezier(.45,0,.3,1) infinite backwards}}"
           f"@keyframes glb{{0%{{transform:translateX(0)}}30%,100%{{transform:translateX({span:g}px)}}}}"
           f".tsh{{animation:tsh 7s 2.1s cubic-bezier(.45,0,.3,1) infinite backwards}}"
           f"@keyframes tsh{{0%{{transform:translateX(0)}}14%,100%{{transform:translateX({S + 80}px)}}}}")
    b = []
    # líneas que nacen del monograma
    b.append(f'<path class="draw" style="animation-delay:.35s;animation-duration:1.3s" pathLength="1" '
             f'd="M{l1:g} {ly:g}H{l0}" stroke="url(#la)" stroke-width="2" stroke-linecap="round"/>')
    b.append(f'<path class="draw" style="animation-delay:.35s;animation-duration:1.3s" pathLength="1" '
             f'd="M{r0:g} {ly:g}H{r1}" stroke="url(#lb)" stroke-width="2" stroke-linecap="round"/>')
    b.append(f'<g clip-path="url(#ca)"><rect class="gla" x="{l1:g}" y="{ly - 1.5:g}" width="{glint}" height="3" rx="1.5" fill="url(#gl)"/></g>')
    b.append(f'<g clip-path="url(#cb)"><rect class="glb" x="{r0 - glint:g}" y="{ly - 1.5:g}" width="{glint}" height="3" rx="1.5" fill="url(#gl)"/></g>')
    # baldosa con el monograma
    b.append(f'<g class="pop" style="animation-delay:.05s"><g filter="url(#fg)">{rrect(tx, ty, S, S, 19, "url(#ft)")}</g>'
             f'<g clip-path="url(#ct)"><path class="tsh" d="M{tx - 60:g} {ty + S:g}l22 {-S}h30l-22 {S}Z" fill="url(#ts)"/></g>'
             f'{rrect(tx + .5, ty + .5, S - 1, S - 1, 18.5, "none", "#ffffff", 1, "stroke-opacity=\".25\"")}'
             f'{monogram(tx + S * .06, ty + S * .06, S * .88, "#ffffff", 8, .45)}</g>')
    # textos
    b.append(f'<text class="rise" style="animation-delay:.25s" x="{W / 2:g}" y="{title_y}" font-size="26" font-weight="800" '
             f'letter-spacing="-.5" fill="{p["text"]}" text-anchor="middle">{esc(FOOT_TITLE)}</text>')
    b.append(f'<text class="fade" style="animation-delay:.45s" x="{W / 2:g}" y="{sub_y}" font-size="14" '
             f'fill="{p["muted"]}" text-anchor="middle" xml:space="preserve">{esc(FOOT_SUB[0])}'
             f'<tspan fill="{p["brand_text"]}" font-weight="700">  ·  </tspan>{esc(FOOT_SUB[1])}</text>')
    return svg_doc(W, H, "".join(b), title=FOOT_TITLE,
                   desc=f"Pie del perfil con el monograma NG. {FOOT_SUB[0]} · {FOOT_SUB[1]}.", css=css, defs=defs)


# --------------------------------------------------------------------------- README
def snippet() -> str:
    """HTML listo para pegar en el README (URLs absolutas, como las sirve GitHub)."""
    out = ["<!-- NAV: pills de navegación (5 + 4 en dos filas) -->", '<p align="center">']
    for j, (slug, label, _) in enumerate(NAV):
        if j == NAV_BREAK:
            out.append("  <br>")
        tip = "Escríbeme: correo, LinkedIn y GitHub" if slug == CTA_SLUG else f"Ir a {label}"
        out.append("  " + picture(f"nav/{slug}", label, height="38", href=f"#{slug}", title=tip))
    out.append("</p>")
    for nn, slug, title, sub, _ in SECTIONS:
        out += ["", f"<!-- SECTION:{slug} -->", f'<a name="{slug}"></a>', "",
                f'<p align="center">{picture(f"sections/{nn}-{slug}", f"{nn} · {title} — {sub}", width="100%")}</p>']
    groups = "; ".join(f"{name}: {', '.join(labels)}" for name, _, labels in STACK_GROUPS)
    out += ["", "<!-- STACK_MATRIX -->",
            f'<p align="center">{picture("stack/matrix", f"Herramientas y servicios por grupos. {groups}", width="100%")}</p>']
    out += ["", "<!-- CONTACT: botones (se muestran en fila con height=64) -->", '<p align="center">']
    alts = {"email": f"Escríbeme: {C.EMAIL}", "linkedin": f"LinkedIn: {C.NAME}", "github": f"GitHub: @{C.GITHUB_USER}"}
    tips = {"email": "Escríbeme un correo", "linkedin": "Mi perfil de LinkedIn", "github": "Mis repositorios en GitHub"}
    for kind, _, _, href in CONTACT:
        out.append("  " + picture(f"contact/{kind}", alts[kind], height="64", href=href, title=tips[kind]))
    out.append("</p>")
    out += ["", "<!-- FOOTER -->",
            f'<p align="center">{picture("footer/footer", f"{FOOT_TITLE}. {FOOT_SUB[0]} · {FOOT_SUB[1]}", width="100%")}</p>']
    return "\n".join(out) + "\n"


def main():
    files = []
    for i, (slug, label, ic) in enumerate(NAV):
        files += write_themed(f"nav/{slug}", nav_pill(i, slug, label, ic))
    for k, s in enumerate(SECTIONS):
        files += write_themed(f"sections/{s[0]}-{s[1]}", section_header(k, *s))
    files += write_themed("stack/matrix", stack_matrix)
    for i, c in enumerate(CONTACT):
        files += write_themed(f"contact/{c[0]}", contact_button(i, *c))
    files += write_themed("footer/footer", footer)
    return files


if __name__ == "__main__":
    if "--snippet" in sys.argv:
        sys.stdout.reconfigure(encoding="utf-8")
        print(snippet(), end="")
    else:
        for path in main():
            print(path)
