"""Cabecera principal: nombre, estado de disponibilidad y una mini tienda online animada
(un cursor añade un producto al carrito) junto a un fragmento de PHP para WooCommerce."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import (MONO, brand_gradient, browser_frame, chip, delay, dot_grid, esc, icon,  # noqa: E402
                   rrect, shadow_filter, svg_doc, text_width, write_themed)
import content as C  # noqa: E402

W, H = 1000, 460
ROTATOR = ["PHP + WooCommerce", "Angular + Spring Boot", "Java + MongoDB", "WordPress + PrestaShop"]
CODE = [
    [("com", "<?php // functions.php · tema hijo")],
    [("fn", "add_action"), ("punc", "(")],
    [("punc", "  "), ("str", "'woocommerce_shop_loop_item_title'"), ("punc", ",")],
    [("punc", "  "), ("kw", "function"), ("punc", " () {")],
    [("punc", "    "), ("kw", "global"), ("punc", " "), ("prop", "$product"), ("punc", ";")],
    [("punc", "    "), ("kw", "if"), ("punc", " ("), ("prop", "$product"), ("punc", "->"),
     ("fn", "get_meta"), ("punc", "("), ("str", "'_reacond'"), ("punc", "))")],
    [("punc", "      "), ("kw", "echo"), ("punc", " "), ("str", "'<span class=\"badge\">'")],
    [("punc", "        . "), ("str", "'Reacondicionado</span>'"), ("punc", ";")],
    [("punc", "  });")],
]


def washer(cx, cy, p):
    return (f'<g transform="translate({cx-23} {cy-27})">'
            + rrect(0, 0, 46, 54, 7, p["raised"], p["muted"], 1.4)
            + f'<line x1="0" y1="13" x2="46" y2="13" stroke="{p["muted"]}" stroke-width="1.2"/>'
            + f'<circle cx="8" cy="6.5" r="2" fill="{p["muted"]}"/><circle cx="15" cy="6.5" r="2" fill="{p["muted"]}"/>'
            + f'<rect x="28" y="4.5" width="12" height="4" rx="2" fill="{p["brand"]}"/>'
            + f'<circle cx="23" cy="33" r="14" fill="{p["surface"]}" stroke="{p["muted"]}" stroke-width="1.4"/>'
            + f'<g class="drum"><circle cx="23" cy="33" r="9" fill="{p["brand_soft"]}" stroke="{p["brand"]}" '
              f'stroke-width="1.6" stroke-dasharray="7 4.5"/></g></g>')


def stroller(cx, cy, p):
    m = p["muted"]
    return (f'<g transform="translate({cx-28} {cy-26})" stroke="{m}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M30 6 A20 20 0 0 1 50 26 H30 Z" fill="{p["brand"]}" stroke="{p["brand"]}"/>'
            f'<path d="M8 26 H50 C50 36 42 41 31 41 H22 C14 41 8 35 8 26 Z" fill="{p["raised"]}"/>'
            f'<path d="M8 26 L2 14 H-3"/><circle cx="16" cy="48" r="5" fill="{p["surface"]}"/>'
            f'<circle cx="41" cy="48" r="5" fill="{p["surface"]}"/><path d="M22 41 L18 44 M35 41 L39 44"/></g>')


def fridge(cx, cy, p):
    m = p["muted"]
    return (f'<g transform="translate({cx-17} {cy-30})">'
            + rrect(0, 0, 34, 60, 6, p["raised"], m, 1.4)
            + f'<line x1="0" y1="21" x2="34" y2="21" stroke="{m}" stroke-width="1.2"/>'
            + f'<line x1="27" y1="7" x2="27" y2="15" stroke="{m}" stroke-width="2" stroke-linecap="round"/>'
            + f'<line x1="27" y1="27" x2="27" y2="40" stroke="{m}" stroke-width="2" stroke-linecap="round"/></g>')


def product_card(x, y, p, *, name, price, glyph, badge=None, badge_fill=None, badge_text=None, active=False):
    w, h = 108, 168
    out = [f'<g>', rrect(x, y, w, h, 10, p["raised"], p["border"]),
           rrect(x + 6, y + 6, w - 12, 82, 7, p["surface"], None),
           glyph(x + w / 2, y + 50, p)]
    if badge:
        bw = text_width(badge, 8.2, 700) + 12
        out.append(rrect(x + 10, y + 11, bw, 15, 7.5, badge_fill or p["brand"], None))
        out.append(f'<text x="{x+16}" y="{y+21.3}" font-size="8.2" font-weight="700" fill="{badge_text or "#fff"}" '
                   f'letter-spacing=".3">{esc(badge)}</text>')
    out.append(f'<text x="{x+10}" y="{y+108}" font-size="11.5" font-weight="600" fill="{p["text"]}">{esc(name)}</text>')
    out.append(f'<text x="{x+10}" y="{y+126}" font-size="12.5" font-weight="700" fill="{p["brand_text"]}">{esc(price)}</text>')
    bx, by = x + 10, y + 136
    if active:
        out.append(f'<g class="btn">{rrect(bx, by, 88, 23, 11.5, p["brand"], None)}'
                   f'<g class="btn-done">{rrect(bx, by, 88, 23, 11.5, p["success"], None)}</g></g>'
                   f'<text class="lbl-add" x="{bx+44}" y="{by+15.5}" font-size="11" font-weight="700" fill="#fff" text-anchor="middle">Añadir</text>'
                   f'<text class="lbl-done" x="{bx+44}" y="{by+15.5}" font-size="11" font-weight="700" fill="#fff" text-anchor="middle">✓ Añadido</text>')
    else:
        out.append(rrect(bx, by, 88, 23, 11.5, p["brand"], None))
        out.append(f'<text x="{bx+44}" y="{by+15.5}" font-size="11" font-weight="700" fill="#fff" text-anchor="middle">Añadir</text>')
    out.append("</g>")
    return "".join(out)


def build(theme, p):
    dark = theme == "dark"
    defs = (
        f'<clipPath id="card"><rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="22"/></clipPath>'
        f'<radialGradient id="glow" cx="80%" cy="10%" r="62%"><stop offset="0" stop-color="{p["brand"]}" stop-opacity="{.26 if dark else .16}"/>'
        f'<stop offset=".55" stop-color="{p["brand"]}" stop-opacity="{.05 if dark else .04}"/><stop offset="1" stop-color="{p["brand"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="glow2" cx="8%" cy="100%" r="45%"><stop offset="0" stop-color="{p["grad_a"]}" stop-opacity="{.10 if dark else .10}"/>'
        f'<stop offset="1" stop-color="{p["grad_a"]}" stop-opacity="0"/></radialGradient>'
        + dot_grid("dots", p["grid"], 22, 1.15, .75 if dark else .9)
        + f'<linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0"><stop offset=".25" stop-color="#fff" stop-opacity="0"/>'
          f'<stop offset=".75" stop-color="#fff" stop-opacity="1"/></linearGradient>'
          f'<mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#fadeL)"/></mask>'
        + brand_gradient("name", p)
        + shadow_filter("sh", p["shadow"], 12, 22)
        + shadow_filter("shs", p["shadow"], 4, 8)
        + '<clipPath id="badge"><circle cx="0" cy="0" r="8.5"/></clipPath>'
    )
    css = f"""
    .drum{{animation:spin 3.2s linear infinite;transform-box:fill-box;transform-origin:center}}
    @keyframes spin{{to{{transform:rotate(360deg)}}}}
    .rot{{animation:rot 12s ease infinite backwards}}
    .rot1,.rot2,.rot3{{opacity:0}}
    @keyframes rot{{0%{{opacity:0;transform:translateY(7px)}}3%,22%{{opacity:1;transform:none}}25%,100%{{opacity:0;transform:translateY(-7px)}}}}
    .cursor{{transform:translate(972px,318px);animation:cur 9s 1.8s ease-in-out infinite backwards}}
    @keyframes cur{{0%{{transform:translate(972px,318px);opacity:0}}6%{{opacity:1}}
      30%,33%{{transform:translate(748px,383px)}}35%{{transform:translate(748px,383px) scale(.86)}}
      38%{{transform:translate(748px,383px) scale(1)}}62%{{transform:translate(862px,300px);opacity:1}}
      84%{{transform:translate(972px,318px);opacity:1}}90%,100%{{transform:translate(972px,318px);opacity:0}}}}
    .btn{{animation:press 9s 1.8s infinite backwards;transform-box:fill-box;transform-origin:center}}
    @keyframes press{{0%,34%,38%,100%{{transform:none}}35.5%{{transform:scale(.93)}}}}
    .btn-done,.lbl-done{{opacity:0;animation:done 9s 1.8s infinite backwards}}
    @keyframes done{{0%,35%{{opacity:0}}37%,80%{{opacity:1}}84%,100%{{opacity:0}}}}
    .lbl-add{{animation:undone 9s 1.8s infinite backwards}}
    @keyframes undone{{0%,35%{{opacity:1}}37%,80%{{opacity:0}}84%,100%{{opacity:1}}}}
    .digits{{animation:count 9s 1.8s infinite backwards}}
    @keyframes count{{0%,35.5%{{transform:none}}38%,84%{{transform:translateY(-17px)}}87%,100%{{transform:none}}}}
    .bump{{animation:bump 9s 1.8s infinite backwards;transform-box:fill-box;transform-origin:center}}
    @keyframes bump{{0%,35.5%,44%,100%{{transform:none}}39%{{transform:scale(1.35)}}}}
    .toast{{opacity:0;animation:toast 9s 1.8s infinite backwards}}
    @keyframes toast{{0%,36%{{opacity:0;transform:translateY(-8px)}}40%,70%{{opacity:1;transform:none}}75%,100%{{opacity:0;transform:translateY(-8px)}}}}
    .f1{{animation:float 6s ease-in-out 1.4s infinite}}
    .f2{{animation:float 7s ease-in-out 2.1s infinite}}
    .f3{{animation:float 6.5s ease-in-out 2.8s infinite}}
    .win{{animation:win .9s cubic-bezier(.2,.8,.2,1) backwards}}
    @keyframes win{{from{{opacity:0;transform:translate(22px,10px)}}}}
    """
    b = []
    # Fondo
    b.append(f'<g clip-path="url(#card)">{rrect(0, 0, W, H, 22, p["canvas"])}'
             f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#gridmask)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#glow)"/><rect width="{W}" height="{H}" fill="url(#glow2)"/></g>')
    b.append(rrect(0.5, 0.5, W - 1, H - 1, 22, "none", p["border"]))

    # ---- columna izquierda
    x0 = 56
    status = "Disponible para prácticas · feb – may 2027"
    sw = text_width(status, 14, 600) + 48
    b.append(f'<g class="pop" {delay(0, base=.1)}>'
             + rrect(x0, 48, sw, 34, 17, p["success_soft"], p["success"], 1)
             + f'<circle class="ping" cx="{x0+19}" cy="65" r="4.5" fill="{p["success"]}"/>'
             + f'<circle cx="{x0+19}" cy="65" r="4.5" fill="{p["success"]}"/>'
             + f'<text x="{x0+33}" y="70" font-size="14" font-weight="600" fill="{p["success"]}">{esc(status)}</text></g>')
    b.append(f'<text class="mono fade" {delay(1, base=.15)} x="{x0}" y="124" font-size="15" fill="{p["brand_text"]}" '
             f'letter-spacing=".5">// hola, soy</text>')
    b.append(f'<text class="rise" {delay(2, base=.15)} x="{x0-3}" y="186" font-size="62" font-weight="800" '
             f'letter-spacing="-1.6" fill="{p["text"]}">{esc(C.FIRST_NAME)}</text>')
    b.append(f'<text class="rise" {delay(3, base=.15)} x="{x0-3}" y="252" font-size="62" font-weight="800" '
             f'letter-spacing="-1.6" fill="url(#name)">{esc(C.LAST_NAMES)}</text>')
    b.append(f'<text class="rise" {delay(4, base=.2)} x="{x0}" y="301" font-size="20" font-weight="500" fill="{p["muted"]}">'
             f'Construyo <tspan fill="{p["text"]}" font-weight="650">tiendas online</tspan> y '
             f'<tspan fill="{p["text"]}" font-weight="650">aplicaciones web</tspan>.</text>')
    # rotador
    pre = "~/stack $ "
    px = x0 + text_width(pre, 15, mono=True)
    b.append(f'<g class="rise" {delay(5, base=.2)}><text class="mono" x="{x0}" y="342" font-size="15" fill="{p["subtle"]}">{esc(pre)}</text>')
    for i, word in enumerate(ROTATOR):
        b.append(f'<text class="mono rot rot{i}" style="animation-delay:{i*3}s" x="{px:g}" y="342" font-size="15" '
                 f'font-weight="600" fill="{p["text"]}">{esc(word)}</text>')
    b.append(f'<rect class="blink" x="{px + text_width(max(ROTATOR, key=len), 15, mono=True) + 6:g}" y="329" '
             f'width="8.5" height="17" rx="1.5" fill="{p["brand"]}"/></g>')
    # meta
    meta = [("pin", "El Viso del Alcor, Sevilla"), ("cap", "2.º DAW · IES Los Alcores")]
    mx = x0
    mrow = [f'<g class="rise" {delay(6, base=.2)}>']
    for ic, label in meta:
        mrow.append(icon(ic, mx, 389, 17, p["brand_text"], 1.9))
        mrow.append(f'<text x="{mx+24:g}" y="402.5" font-size="14.5" fill="{p["muted"]}">{esc(label)}</text>')
        mx += 24 + text_width(label, 14.5) + 26
    mrow.append("</g>")
    b.append("".join(mrow))
    b.append(f'<line class="fade" {delay(7, base=.2)} x1="{x0}" y1="368" x2="{x0+36}" y2="368" stroke="{p["brand"]}" '
             f'stroke-width="2.5" stroke-linecap="round"/>')

    # ---- ilustración: editor de código (detrás)
    cx, cy, cw, ch = 626, 40, 334, 214
    code = [f'<g class="win" style="animation-delay:.45s"><g class="f3" style="animation-delay:3.4s"><g filter="url(#sh)">'
            + rrect(cx, cy, cw, ch, 14, p["surface"], p["border"]) + "</g>"
            + f'<path d="M{cx+14} {cy+.5}H{cx+cw-14}A13.5 13.5 0 0 1 {cx+cw-.5} {cy+14}V{cy+32}H{cx+.5}V{cy+14}A13.5 13.5 0 0 1 {cx+14} {cy+.5}Z" fill="{p["raised"]}"/>'
            + f'<line x1="{cx}" y1="{cy+32}" x2="{cx+cw}" y2="{cy+32}" stroke="{p["border_soft"]}"/>'
            + "".join(f'<circle cx="{cx+18+i*15}" cy="{cy+16}" r="4.6" fill="{c}"/>' for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")))
            + f'<text class="mono" x="{cx+cw/2}" y="{cy+20.5}" font-size="12" fill="{p["muted"]}" text-anchor="middle">functions.php</text>']
    ly = cy + 54
    for n, line in enumerate(CODE):
        spans = "".join(f'<tspan fill="{p[k]}">{esc(t)}</tspan>' for k, t in line)
        code.append(f'<g class="fade" {delay(n, .07, .9)}><text class="mono" x="{cx+14}" y="{ly}" font-size="11" fill="{p["subtle"]}">{n+1}</text>'
                    f'<text class="mono" x="{cx+34}" y="{ly}" font-size="11.4" xml:space="preserve">{spans}</text></g>')
        ly += 17.5
    code.append("</g></g>")
    b.append("".join(code))

    # ---- navegador (delante) con la tienda
    bx, by, bw, bh = 556, 152, 376, 268
    frame, (ix, iy, iw, ih) = browser_frame(bx, by, bw, bh, p, url="mi-tienda.es", r=14, bar=38)
    shop = [f'<g class="win" style="animation-delay:.7s"><g filter="url(#sh)">{frame}</g>']
    # cabecera de la tienda
    hy = iy + 10
    shop.append(rrect(ix + 13, hy + 1, 16, 16, 4.5, p["brand"]) +
                f'<text x="{ix+35}" y="{hy+13.5}" font-size="13" font-weight="800" fill="{p["text"]}" letter-spacing="-.2">outlet</text>')
    shop.append(rrect(ix + 96, hy, 172, 19, 9.5, p["surface"], p["border_soft"]) +
                icon("search", ix + 103, hy + 3.5, 12, p["subtle"], 2) +
                f'<text x="{ix+121}" y="{hy+13.5}" font-size="10.5" fill="{p["subtle"]}">Buscar productos…</text>')
    cart_x, cart_y = ix + iw - 38, hy - 1
    shop.append(icon("cart", cart_x, cart_y, 21, p["text"], 1.9))
    shop.append(f'<g transform="translate({cart_x+19} {cart_y+3})"><g class="bump"><circle r="8.5" fill="{p["brand"]}"/>'
                f'<g clip-path="url(#badge)"><g class="digits">'
                f'<text y="4" font-size="11" font-weight="800" fill="#fff" text-anchor="middle">2</text>'
                f'<text y="21" font-size="11" font-weight="800" fill="#fff" text-anchor="middle">3</text></g></g></g></g>')
    shop.append(f'<line x1="{ix}" y1="{hy+29}" x2="{ix+iw}" y2="{hy+29}" stroke="{p["border_soft"]}"/>')
    # productos
    py = hy + 40
    shop.append(product_card(ix + 13, py, p, name="Lavadora 8 kg", price="339,99 €", glyph=washer,
                             badge="REACONDICIONADO"))
    shop.append(product_card(ix + 133, py, p, name="Silla de paseo", price="249,00 €", glyph=stroller, active=True))
    shop.append(product_card(ix + 253, py, p, name="Frigorífico", price="184,95 €", glyph=fridge,
                             badge="TARA ESTÉTICA", badge_fill=p["grad_a"], badge_text="#3b1d00"))
    # toast
    tw = text_width("Añadido al carrito", 11.5, 600) + 40
    tx = ix + iw - tw - 12
    shop.append(f'<g class="toast"><g filter="url(#shs)">{rrect(tx, hy + 34, tw, 26, 13, p["raised"], p["success"])}</g>'
                + icon("check", tx + 9, hy + 40, 14, p["success"], 2.6)
                + f'<text x="{tx+28}" y="{hy+51}" font-size="11.5" font-weight="600" fill="{p["text"]}">Añadido al carrito</text></g>')
    shop.append("</g>")
    b.append("".join(shop))

    # ---- chips flotantes
    def float_chip(x, y, ic, label, cls, d):
        w = text_width(label, 12.5, 600) + 44
        return (f'<g class="pop" style="animation-delay:{d}s"><g class="{cls}"><g filter="url(#shs)">'
                f'{rrect(x, y, w, 30, 15, p["raised"], p["border"])}</g>'
                f'{icon(ic, x + 11, y + 7, 16, p["brand_text"], 2)}'
                f'<text x="{x+33}" y="{y+19.5}" font-size="12.5" font-weight="600" fill="{p["text"]}">{esc(label)}</text></g></g>')

    b.append(float_chip(482, 104, "box", "Google Shopping", "f1", 1.15))
    b.append(float_chip(706, 412, "card", "Bizum · PayPal · Klarna", "f2", 1.3))

    # ---- cursor
    b.append(f'<g class="cursor"><path d="M0 0 L0 17 L4.6 13.2 L7.6 20 L10.6 18.7 L7.7 12 L13.6 12 Z" '
             f'fill="{p["text"]}" stroke="{p["canvas"]}" stroke-width="1.3" stroke-linejoin="round"/></g>')

    title = f"{C.NAME} — desarrollador web y e-commerce. Disponible para prácticas de febrero a mayo de 2027."
    desc = ("Cabecera animada: nombre, estado de disponibilidad, una mini tienda online donde un cursor "
            "añade una silla de paseo al carrito y un fragmento de PHP para WooCommerce.")
    return svg_doc(W, H, "".join(b), title=title, desc=desc, css=css, defs=defs)


def main():
    return write_themed("hero/hero", build)


if __name__ == "__main__":
    for path in main():
        print(path)
