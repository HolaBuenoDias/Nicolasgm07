"""Formación: línea temporal sep. 2023 → jun. 2027 (formación y trabajo) y certificaciones."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import (brand_gradient, card, delay, dot_grid, esc, icon, kicker, rrect,  # noqa: E402
                   svg_doc, text_width, write_themed)
import content as C  # noqa: E402

W, H = 1000, 340
X0, X1 = 150, 960                      # sep. 2023 … jun. 2027
START = (2023, 9)
MONTHS = (2027 - 2023) * 12 + (6 - 9)  # 45 meses


def mx(ym):
    y, m = map(int, ym.split("-"))
    return X0 + ((y - START[0]) * 12 + m - START[1]) / MONTHS * (X1 - X0)


def bar(x0, x1, y, h, fill, label, sub, p, d, *, dashed=False, txt="#fff", sub_col=None):
    w = x1 - x0
    stroke = f' stroke="{p["brand"]}" stroke-width="1.6" stroke-dasharray="5 4"' if dashed else ""
    out = (f'<g class="grow" style="animation-delay:{d:.2f}s">'
           f'<rect x="{x0:g}" y="{y}" width="{w:g}" height="{h}" rx="{h/2:g}" fill="{fill}"{stroke}/></g>')
    fs = 14 if text_width(label, 14, 700) + 24 < w else 12.5
    out += (f'<g class="fade" style="animation-delay:{d+.45:.2f}s">'
            f'<text x="{x0+14:g}" y="{y+h/2+5:g}" font-size="{fs}" font-weight="700" fill="{txt}">{esc(label)}</text>')
    if sub:
        out += (f'<text x="{x0+14:g}" y="{y+h+18:g}" font-size="13" fill="{sub_col or p["muted"]}">{esc(sub)}</text>')
    return out + "</g>"


def timeline(theme, p):
    css = """.grow{animation:grow 1.1s cubic-bezier(.2,.8,.2,1) backwards;transform-box:fill-box;transform-origin:left center}
    @keyframes grow{from{transform:scaleX(0)}}
    .goal{animation:goal 2.6s ease-in-out 2.4s infinite}
    @keyframes goal{50%{opacity:.55}}"""
    defs = brand_gradient("eg", p) + dot_grid("edots", p["grid"], 22, 1.1, .5)
    b = [card(0, 0, W, H, p), f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="url(#edots)" opacity=".6"/>']
    b.append(kicker(36, 44, "mi recorrido · 2023 → 2027", p))
    # carriles
    lanes = [("Formación", "cap", 92), ("Trabajo", "briefcase", 182)]
    for i, (name, ic, y) in enumerate(lanes):
        b.append(f'<g class="fade" {delay(i)}>{icon(ic, 36, y - 2, 18, p["brand_text"], 2)}'
                 f'<text x="36" y="{y+34}" font-size="12" font-weight="600" fill="{p["subtle"]}" class="mono">{name.upper()}</text></g>')
    # eje de años
    ay = 262
    b.append(f'<line x1="{X0}" y1="{ay}" x2="{X1}" y2="{ay}" stroke="{p["border"]}" stroke-width="1.5"/>')
    for yr in range(2024, 2028):
        x = mx(f"{yr}-01")
        b.append(f'<line x1="{x:g}" y1="{ay-6}" x2="{x:g}" y2="{ay+6}" stroke="{p["border"]}" stroke-width="1.5"/>'
                 f'<text class="mono" x="{x:g}" y="{ay+26}" font-size="13" font-weight="600" fill="{p["muted"]}" text-anchor="middle">{yr}</text>'
                 f'<line x1="{x:g}" y1="70" x2="{x:g}" y2="{ay-8}" stroke="{p["border_soft"]}" stroke-dasharray="2 5"/>')
    # formación
    b.append(bar(mx("2023-09"), mx("2025-06"), 94, 30, p["muted"] if theme == "light" else "#3d444d",
                 "SMR · título obtenido", "Sistemas Microinformáticos y Redes", p, .3))
    b.append(bar(mx("2025-09"), mx("2027-06"), 94, 30, "url(#eg)", "DAW · cursando 2.º",
                 "Desarrollo de Aplicaciones Web · IES Los Alcores", p, .55))
    # trabajo
    b.append(bar(mx("2025-03"), mx("2026-06"), 184, 30, p["brand_text"] if theme == "light" else p["brand"],
                 "Bastilipo", "Web y e-commerce · 1 año y 4 meses", p, .8))
    gx0, gx1 = mx("2027-02"), mx("2027-05") + 14
    b.append(f'<g class="goal">{bar(gx0, gx1, 184, 30, p["brand_soft"], "", "", p, 1.05, dashed=True)}</g>')
    b.append(f'<g class="fade" style="animation-delay:1.4s"><text x="{gx1:g}" y="179" font-size="13" font-weight="700" '
             f'fill="{p["brand_text"]}" text-anchor="end">Prácticas DAW</text>'
             f'<text x="{gx1:g}" y="236" font-size="13" fill="{p["muted"]}" text-anchor="end">feb. – may. 2027</text></g>')
    # hitos en el eje
    for i, (ym, title, _) in enumerate(C.MILESTONES):
        x = mx(ym)
        b.append(f'<circle class="pop" style="animation-delay:{1.2 + i*.1:.2f}s" cx="{x:g}" cy="{ay}" r="5" '
                 f'fill="{p["canvas"]}" stroke="{p["brand"]}" stroke-width="2.4"/>')
    b.append(f'<text x="{X0}" y="{ay+52}" font-size="13" fill="{p["subtle"]}">'
             f'sep. 2023 → SMR · mar. 2025 → Bastilipo · sep. 2025 → DAW · feb. 2027 → prácticas · jun. 2027 → título</text>')
    return svg_doc(W, H + 6, "".join(b), title="Línea temporal: SMR 2023–2025, Bastilipo 2025–2026, DAW 2025–2027 y prácticas de febrero a mayo de 2027",
                   css=css, defs=defs)


def certs(theme, p):
    w, h, gap = 494, 132, 12
    b = []
    for i, cert in enumerate(C.CERTS):
        x = i * (w + gap)
        b.append(f'<g class="rise" {delay(i, .15)}>{card(x, 0, w, h, p)}')
        b.append(rrect(x + 24, 28, 76, 76, 20, "url(#cg)") + icon("award", x + 44, 48, 36, "#fff", 2.2))
        b.append(kicker(x + 124, 46, "certificación de google", p))
        b.append(f'<text x="{x+124}" y="80" font-size="26" font-weight="800" letter-spacing="-.5" fill="{p["text"]}">{esc(cert["name"])}</text>')
        b.append(icon("check", x + 124, 92, 15, p["success"], 2.4) +
                 f'<text x="{x+145}" y="104" font-size="13.5" fill="{p["muted"]}">Verificable en LinkedIn</text>')
        b.append(f'<circle cx="{x+w-36}" cy="36" r="5" fill="{p["brand"]}" class="pulse"/></g>')
    return svg_doc(1000, h, "".join(b), title="Certificaciones de Google: Google Analytics y Google Ads, verificables en LinkedIn",
                   defs=brand_gradient("cg", p, "100%", "100%"))


def main():
    return write_themed("education/timeline", timeline) + write_themed("education/certs", certs)


if __name__ == "__main__":
    for f in main():
        print(f)
