"""Piezas del tres en raya del README (sección 08 · Juega), todas estáticas:

  casillas 100×100 (en el README se ven a 96 px):
    empty-a1 … empty-c3   libre: coordenada tenue y un «+» que respira en ola diagonal
    blank                 libre con la partida terminada (sin invitación)
    x, o                  ficha que se dibuja al cargar (X naranja de marca, O neutra)
    x-last, o-last        la última jugada, con un punto que avisa
    x-win, o-win          casillas de la línea ganadora, con fondo de marca y brillo
  cabeceras de estado 360×80: status-turn, status-win, status-lose, status-draw
  botón 184×44: new-game

El tablero cambia en el README (scripts/game/region.py elige qué pieza va en cada hueco);
estos SVG no cambian nunca, así que la caché de GitHub no retrasa las jugadas.

    python scripts/build.py game_assets   →  assets/game/*-{dark,light}.svg
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "game"))
from brand import EASE, esc, icon, rrect, svg_doc, text_width, write_themed  # noqa: E402
from engine import CELLS  # noqa: E402

T = 100                       # lado de la casilla (viewBox)
M = 4.5                       # margen transparente: hueco de ~8 px entre casillas
R = 16                        # radio de la casilla
C = T / 2

# Iconos propios (rejilla 24, trazo redondeado, mismo estilo que brand.ICONS)
GLYPHS = {
    "trophy": '<path d="M7.5 4h9v5.2a4.5 4.5 0 0 1-9 0V4Z"/><path d="M7.5 6.2H5.2a.7.7 0 0 0-.7.8 3.6 3.6 0 0 0 3.3 3.1"/>'
              '<path d="M16.5 6.2h2.3a.7.7 0 0 1 .7.8 3.6 3.6 0 0 1-3.3 3.1"/><path d="M12 13.7V17"/>'
              '<path d="M8.5 20.2h7"/><path d="M9.6 17h4.8l.6 3.2H9l.6-3.2Z"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="2.2"/><rect x="9.6" y="9.6" width="4.8" height="4.8" rx=".8"/>'
           '<path d="M9.5 2.8V6M14.5 2.8V6M9.5 18v3.2M14.5 18v3.2M2.8 9.5H6M2.8 14.5H6M18 9.5h3.2M18 14.5h3.2"/>',
    "equal": '<circle cx="12" cy="12" r="9"/><path d="M8 10h8"/><path d="M8 14h8"/>',
    "cursor": '<path d="M7 4.2 18.2 13l-5 .9 2.8 5.3-2.3 1.2-2.8-5.4L7 18.4V4.2Z"/>',
    "refresh": '<path d="M19.5 11A7.6 7.6 0 0 0 6.2 6.6L4.5 8.4"/><path d="M4.5 4.2v4.2h4.2"/>'
               '<path d="M4.5 13a7.6 7.6 0 0 0 13.3 4.4l1.7-1.8"/><path d="M19.5 19.8v-4.2h-4.2"/>',
}


def glyph(name, x, y, size, color, sw=2.0):
    s = size / 24
    return (f'<g transform="translate({x:g} {y:g}) scale({s:g})" fill="none" stroke="{color}" '
            f'stroke-width="{sw / s:.3g}" stroke-linecap="round" stroke-linejoin="round">{GLYPHS[name]}</g>')


# ------------------------------------------------------------------------------ casillas
TILE_CSS = f"""
.st{{stroke-dasharray:1;animation:st .42s cubic-bezier(.65,0,.35,1) backwards}}
@keyframes st{{from{{stroke-dashoffset:1;opacity:0}}12%{{opacity:1}}}}
.ring{{stroke-dasharray:1;animation:st .6s cubic-bezier(.65,0,.35,1) backwards}}
.plus{{animation:breathe 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes breathe{{0%,100%{{opacity:.5;transform:scale(.9)}}45%{{opacity:1;transform:scale(1.1)}}}}
.glow{{animation:glow 2.6s ease-in-out infinite}}
@keyframes glow{{0%,100%{{opacity:.35}}50%{{opacity:.85}}}}
.hl{{animation:hl 2.6s ease-in-out infinite}}
@keyframes hl{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}
.dot{{animation:pop .5s cubic-bezier(.2,1.5,.4,1) .55s backwards;transform-box:fill-box;transform-origin:center}}
"""


def tile_base(p, *, fill=None, stroke=None, sw=1.0, extra=""):
    inset = M + sw / 2
    return rrect(inset, inset, T - 2 * inset, T - 2 * inset, R, fill or p["surface"], stroke or p["border"], sw, extra)


def mark_x(p, gid, *, delay=0.0, glow=False):
    a, b = 32, 68
    lines = [(a, a, b, b), (b, a, a, b)]
    out = []
    if glow:
        out.append(f'<g class="glow" filter="url(#{gid}b)">'
                   + "".join(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{p["brand"]}" '
                             f'stroke-width="12" stroke-linecap="round"/>' for x1, y1, x2, y2 in lines) + "</g>")
    for i, (x1, y1, x2, y2) in enumerate(lines):
        out.append(f'<line class="st" style="animation-delay:{delay + i * .26:.2f}s" pathLength="1" x1="{x1}" y1="{y1}" '
                   f'x2="{x2}" y2="{y2}" stroke="url(#{gid})" stroke-width="10" stroke-linecap="round"/>')
    return "".join(out)


def mark_o(p, color, *, delay=0.0, glow=None, gid=""):
    r = 18.5
    d = f"M{C} {C - r} a{r} {r} 0 1 1 0 {2 * r} a{r} {r} 0 1 1 0 {-2 * r}"
    out = []
    if glow:
        out.append(f'<g class="glow" filter="url(#{gid}b)"><path d="{d}" stroke="{glow}" stroke-width="12"/></g>')
    out.append(f'<path class="ring" style="animation-delay:{delay:.2f}s" pathLength="1" d="{d}" stroke="{color}" '
               f'stroke-width="9.5" stroke-linecap="round"/>')
    return "".join(out)


def tile_defs(p, gid):
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="30" y1="30" x2="70" y2="70">'
            f'<stop offset="0" stop-color="{p["grad_a"]}"/><stop offset="1" stop-color="{p["grad_b"]}"/></linearGradient>'
            f'<filter id="{gid}b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>')


def empty_tile(name, idx):
    row, col = divmod(idx, 3)
    wave = (row + col) * 0.22

    def build(theme, p):
        body = [tile_base(p),
                f'<text class="mono" x="{M + 11.5:g}" y="{M + 22:g}" font-size="13.5" font-weight="600" '
                f'letter-spacing=".4" fill="{p["muted"]}">{name}</text>',
                f'<g class="plus" style="animation-delay:{wave:.2f}s"><path d="M{C} {C - 8}V{C + 8}M{C - 8} {C}H{C + 8}" '
                f'stroke="{p["subtle"]}" stroke-width="2.6" stroke-linecap="round"/></g>']
        return svg_doc(T, T, "".join(body), title=f"Casilla {name} libre",
                       desc=f"Casilla {name} del tres en raya, libre: púlsala para jugar ahí.", css=TILE_CSS)
    return build


def blank_tile(theme, p):
    body = tile_base(p, fill=p["canvas"], stroke=p["border_soft"])
    return svg_doc(T, T, body, title="Casilla libre", desc="Casilla libre de una partida ya terminada.", css=TILE_CSS)


def piece_tile(mark, variant):
    def build(theme, p):
        dark = theme == "dark"
        gid = f"g{mark}{variant}"
        defs = tile_defs(p, gid)
        win, last = variant == "win", variant == "last"
        o_color = p["text"]
        if win:
            body = [tile_base(p),
                    f'<g class="hl">{tile_base(p, fill=p["brand_soft"], stroke=p["brand_line"], sw=1.5)}</g>']
        else:
            body = [tile_base(p, stroke=p["muted"] if last else None, sw=1.5 if last else 1.0)]
        if mark == "x":
            body.append(mark_x(p, gid, delay=.05, glow=win))
        else:
            body.append(mark_o(p, o_color, delay=.45 if last else .1,
                               glow=(p["brand"] if win else None), gid=gid))
        if last:
            color = p["brand"] if mark == "x" else p["muted"]
            body.append(f'<circle class="ping" style="animation-delay:.9s" cx="{T - M - 14:g}" cy="{M + 14:g}" r="4" fill="{color}"/>'
                        f'<circle class="dot" cx="{T - M - 14:g}" cy="{M + 14:g}" r="4" fill="{color}"/>')
        who = "X (visitantes)" if mark == "x" else "O (CPU)"
        title = {"win": f"{who} ganadora", "last": f"{who}, última jugada", "": who}[variant]
        desc = (f"Casilla ocupada por una {who}" + {"win": ", parte de la línea ganadora.",
                                                    "last": ": es la última jugada de la partida.", "": "."}[variant])
        _ = dark
        return svg_doc(T, T, "".join(body), title=title, desc=desc, css=TILE_CSS, defs=defs)
    return build


# ------------------------------------------------------------------------ cabeceras
SW, SH = 360, 80
STATUS = {
    "turn": dict(kicker="Partida en juego", title="Te toca", sub="Elige una casilla libre del tablero",
                 glyph="cursor", tone="brand"),
    "win": dict(kicker="Partida terminada", title="¡Has ganado!", sub="Los visitantes se llevan la partida",
                glyph="trophy", tone="solid"),
    "lose": dict(kicker="Partida terminada", title="Gana la CPU", sub="Esta vez no ha podido ser",
                 glyph="cpu", tone="neutral"),
    "draw": dict(kicker="Partida terminada", title="Empate", sub="Nadie cede ni una casilla",
                 glyph="equal", tone="neutral"),
}
STATUS_CSS = f"""
.rise{{animation:rise .7s {EASE} backwards}}
.spark{{animation:spark 2.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes spark{{0%,100%{{opacity:.35;transform:scale(.7)}}50%{{opacity:1;transform:scale(1)}}}}
"""


def status_banner(key):
    s = STATUS[key]

    def build(theme, p):
        defs = (f'<linearGradient id="sg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["grad_a"]}"/>'
                f'<stop offset="1" stop-color="{p["grad_b"]}"/></linearGradient>')
        bx, by, bs = 0.75, 12.75, 54.5
        if s["tone"] == "solid":
            badge = rrect(bx, by, bs, bs, 16, "url(#sg)")
            ic = p["on_brand"]
        elif s["tone"] == "brand":
            badge = rrect(bx, by, bs, bs, 16, p["brand_soft"], p["brand_line"], 1.5)
            ic = p["brand_text"]
        else:
            badge = rrect(bx, by, bs, bs, 16, p["surface"], p["border"], 1.5)
            ic = p["text"]
        body = [f'<g class="pop">{badge}{glyph(s["glyph"], bx + bs / 2 - 14, by + bs / 2 - 14, 28, ic, 2.1)}</g>']
        if key == "win":
            for i, (x, y, sz) in enumerate(((52, 6, 13), (60, 52, 9), (-2, 58, 8))):
                body.append(f'<g class="spark" style="animation-delay:{.6 + i * .5:.2f}s">'
                            + icon("sparkle", x, y, sz, p["grad_a"], 1.6) + "</g>")
        tx = 72
        k = s["kicker"].upper()
        if key == "turn":
            body.append(f'<circle class="ping" cx="{tx + 4.5}" cy="20.5" r="4" fill="{p["success"]}"/>'
                        f'<circle cx="{tx + 4.5}" cy="20.5" r="4" fill="{p["success"]}"/>')
            kx, kc = tx + 15, p["success"]
        else:
            kx, kc = tx, p["muted"]
        body.append(f'<text class="mono fade" style="animation-delay:.15s" x="{kx}" y="25" font-size="12.5" '
                    f'font-weight="600" letter-spacing="1.5" fill="{kc}">{esc(k)}</text>')
        body.append(f'<text class="rise" style="animation-delay:.2s" x="{tx - 1.5}" y="54" font-size="28" '
                    f'font-weight="800" letter-spacing="-.6" fill="{p["text"]}">{esc(s["title"])}</text>')
        body.append(f'<text class="rise" style="animation-delay:.3s" x="{tx}" y="74" font-size="14.5" '
                    f'fill="{p["muted"]}">{esc(s["sub"])}</text>')
        for t, size, w in ((k, 12.5, 600), (s["title"], 28, 800), (s["sub"], 14.5, 400)):
            assert tx + text_width(t, size, w, mono=(t == k), tracking=1.5 / 12.5 if t == k else 0) < SW - 12, t
        alt = {"turn": "Te toca: elige una casilla", "win": "¡Has ganado! Los visitantes se llevan la partida",
               "lose": "Gana la CPU", "draw": "Empate"}[key]
        return svg_doc(SW, SH, "".join(body), title=alt, desc=f"Estado del tres en raya: {s['title']}. {s['sub']}.",
                       css=STATUS_CSS, defs=defs)
    return build


# ------------------------------------------------------------------------------ botón
BW, BH = 184, 44


def new_game_button(theme, p):
    label = "Nueva partida"
    size = 18.5
    tw = text_width(label, size, 700)
    gx = (BW - (20 + 9 + tw)) / 2
    body = [f'<g class="pop">{rrect(0.5, 0.5, BW - 1, BH - 1, (BH - 1) / 2, p["brand"])}</g>',
            glyph("refresh", gx, BH / 2 - 10, 20, p["on_brand"], 2.3),
            f'<text class="fade" x="{gx + 29:g}" y="{BH / 2 + size * .35:g}" font-size="{size}" font-weight="700" '
            f'fill="{p["on_brand"]}">{label}</text>']
    assert gx > 12
    return svg_doc(BW, BH, "".join(body), title="Nueva partida",
                   desc="Botón para empezar una partida nueva del tres en raya.")


# ------------------------------------------------------------------------------- main
def main():
    out = []
    for i, name in enumerate(CELLS):
        out += write_themed(f"game/empty-{name.lower()}", empty_tile(name, i))
    out += write_themed("game/blank", blank_tile)
    for mark in ("x", "o"):
        for variant in ("", "last", "win"):
            out += write_themed(f"game/{mark}" + (f"-{variant}" if variant else ""), piece_tile(mark, variant))
    for key in STATUS:
        out += write_themed(f"game/status-{key}", status_banner(key))
    out += write_themed("game/new-game", new_game_button)
    return out


if __name__ == "__main__":
    for path in main():
        print(path)
