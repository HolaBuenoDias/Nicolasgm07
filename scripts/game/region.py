"""Región del README con el tablero, entre <!-- TTT:START --> y <!-- TTT:END -->.

Todo es HTML que GitHub deja pasar (a, picture, source, img, table, p, sub, b, code,
ul/ol): nada de style, class ni script. Las casillas son SVG estáticos de
assets/game/ (los genera scripts/components/game_assets.py); aquí solo se decide qué
casilla va en cada hueco y a dónde enlaza.
"""
from __future__ import annotations

import os
from html import escape
from urllib.parse import quote

import engine as E

START, END = "<!-- TTT:START -->", "<!-- TTT:END -->"

REPO = os.environ.get("TTT_REPO", "Nicolasgm07/Nicolasgm07")
OWNER = REPO.split("/")[0]
RAW = f"https://raw.githubusercontent.com/{REPO}/main/assets/game"
ISSUES_NEW = f"https://github.com/{REPO}/issues/new"
PROFILE = f"https://github.com/{OWNER}"
ANCHOR = "#juega"
PLAY_URL = PROFILE + ANCHOR

TILE = 96            # px de cada casilla en el README (los SVG miden 100×100)
INFO_W = 360         # ancho de la cabecera de estado y de la columna de información

MOVE_BODY = ("Pulsa «Create» / «Submit new issue» sin cambiar nada. Tu jugada se aplicará en unos "
             "segundos y el tablero del perfil se actualizará solo.")
NEW_BODY = ("Pulsa «Create» / «Submit new issue» sin cambiar nada. La partida nueva empezará en unos "
            "segundos y el tablero del perfil se actualizará solo.")

STATUS = {   # estado → (asset, texto alternativo)
    "playing": ("status-turn", "Te toca: elige una casilla"),
    E.X: ("status-win", "¡Has ganado! Los visitantes se llevan la partida"),
    E.O: ("status-lose", "Gana la CPU"),
    "draw": ("status-draw", "Empate"),
}


def esc(s) -> str:
    return escape(str(s), quote=True)


def issue_url(title: str, body: str) -> str:
    return f"{ISSUES_NEW}?title={quote(title, safe='')}&body={quote(body, safe='')}"


def move_url(cell: int) -> str:
    """Enlace que abre un issue ya rellenado con la jugada (cell = índice 0–8)."""
    return issue_url(f"ttt|move|{cell + 1}", MOVE_BODY)


def new_game_url() -> str:
    return issue_url("ttt|new", NEW_BODY)


def picture(name: str, alt: str, *, href: str, width: int, height: int, title: str | None = None,
            align: str | None = None) -> str:
    """<a><picture> con la versión clara y oscura del asset (mismo formato que brand.picture)."""
    dark, light = f"{RAW}/{name}-dark.svg", f"{RAW}/{name}-light.svg"
    extra = (f' title="{esc(title)}"' if title else "") + (f' align="{align}"' if align else "")
    return (f'<a href="{esc(href)}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="{dark}">'
            f'<source media="(prefers-color-scheme: light)" srcset="{light}">'
            f'<img src="{light}" width="{width}" height="{height}" alt="{esc(alt)}"{extra}>'
            f'</picture></a>')


def user_link(login: str) -> str:
    return f'<a href="https://github.com/{esc(login)}">@{esc(login)}</a>'


# ----------------------------------------------------------------------------- tablero
def tile(state: dict, cell: int) -> str:
    g = state["game"]
    board = "".join(g["board"])
    mark, name = board[cell], E.CELLS[cell]
    playing = g["status"] == "playing"
    line = g.get("line") or ()
    if mark == E.EMPTY:
        if playing:
            return picture(f"empty-{name.lower()}", f"{name}: casilla libre", href=move_url(cell),
                           width=TILE, height=TILE, title=f"Jugar en {name}", align="top")
        return picture("blank", f"{name}: libre", href=ANCHOR, width=TILE, height=TILE,
                       title="Partida terminada: empieza una nueva", align="top")
    who = "la CPU" if mark == E.O else next(
        (f"@{m['user']}" for m in reversed(g["moves"]) if m["cell"] == name and m.get("user")), "un visitante")
    if cell in line:
        variant, title = "win", f"{name} · {mark} ganadora de {who}"
    elif cell == g.get("last"):
        variant, title = "last", f"{name} · última jugada, de {who}"
    else:
        variant, title = "", f"{name} · {mark} de {who}"
    asset = mark.lower() + (f"-{variant}" if variant else "")
    return picture(asset, f"{name}: {mark}", href=ANCHOR, width=TILE, height=TILE, title=title, align="top")


def board_html(state: dict) -> str:
    rows = ["".join(tile(state, r * 3 + c) for c in range(3)) for r in range(3)]
    return "<br>\n".join(rows)


# ------------------------------------------------------------------------ información
def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def recent_item(r: dict) -> str:
    who = user_link(r["user"]) if r.get("user") else "Un visitante"
    out = f'{who} juega <code>{esc(r["cell"])}</code>'
    if r.get("result") == E.X:
        return out + " · ¡tres en raya para los visitantes!"
    if r.get("result") == "draw" and not r.get("cpu"):
        return out + " · empate"
    if r.get("cpu"):
        out += f' · la CPU responde <code>{esc(r["cpu"])}</code>'
        if r.get("result") == E.O:
            out += " y gana"
        elif r.get("result") == "draw":
            out += " · empate"
    return out


def top_players(state: dict, n: int = 5) -> list[tuple[str, dict]]:
    players = state.get("players", {})
    return sorted(players.items(), key=lambda kv: (-kv[1]["moves"], -kv[1].get("wins", 0), kv[0].lower()))[:n]


def info_html(state: dict) -> str:
    g, st = state["game"], state["stats"]
    status = g["status"]
    asset, alt = STATUS[status]
    out = [picture(asset, alt, href=ANCHOR, width=INFO_W, height=72)]
    n = len(g["moves"])
    if status == "playing":
        meta = (f"Partida n.º {g['number']} · visitantes (<b>X</b>) contra la CPU (<b>O</b>)"
                if n else f"Partida n.º {g['number']} · el tablero está vacío: ¡abre tú!")
    else:
        meta = f"Partida n.º {g['number']} · terminada en {plural(n, 'movimiento', 'movimientos')}"
    out.append(f"<p><sub>{meta}</sub></p>")
    if status != "playing":
        out.append("<p>" + picture("new-game", "Nueva partida", href=new_game_url(), width=184, height=44,
                                   title="Empezar una partida nueva") + "</p>")

    out.append("<p><sub><b>MARCADOR</b></sub></p>")
    cols = (("Partidas", st["games"]), ("Visitantes", st["visitors"]), ("CPU", st["cpu"]),
            ("Empates", st["draws"]))
    out.append("<table>\n<tr>" + "".join(f"<th>{k}</th>" for k, _ in cols) + "</tr>\n<tr>"
               + "".join(f'<td align="center">{v}</td>' for _, v in cols) + "</tr>\n</table>")

    out.append("<p><sub><b>ÚLTIMAS JUGADAS</b></sub></p>")
    recent = state.get("recent", [])[:5]
    if recent:
        out.append("<ul>\n" + "\n".join(f"<li>{recent_item(r)}</li>" for r in recent) + "\n</ul>")
    else:
        out.append("<p><sub>Todavía no hay jugadas: ¡estrena el tablero!</sub></p>")

    out.append("<p><sub><b>TOP JUGADORES</b></sub></p>")
    top = top_players(state)
    if top:
        items = []
        for login, p in top:
            s = f"{user_link(login)} · {plural(p['moves'], 'jugada', 'jugadas')}"
            if p.get("wins"):
                s += f" · {plural(p['wins'], 'victoria', 'victorias')}"
            items.append(f"<li>{s}</li>")
        out.append("<ol>\n" + "\n".join(items) + "\n</ol>")
    else:
        out.append("<p><sub>Aquí saldrá quien más juegue. ¿Serás tú?</sub></p>")
    return "\n".join(out)


def render(state: dict) -> str:
    """Región completa, marcadores incluidos. Misma entrada → mismo texto (idempotente)."""
    return "\n".join([
        START,
        '<div align="center">',
        "<table>",
        "<tr>",
        f'<td align="center" valign="middle" width="{3 * TILE + 24}">',
        board_html(state),
        "</td>",
        f'<td valign="top" width="{INFO_W + 24}">',
        info_html(state),
        "</td>",
        "</tr>",
        "</table>",
        "</div>",
        END,
    ])


def replace_region(text: str, region: str) -> str:
    """Sustituye lo que hay entre los marcadores (ellos incluidos) y no toca nada más."""
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError(f"el README debe tener exactamente un {START} y un {END}")
    s, e = text.index(START), text.index(END)
    if e < s:
        raise ValueError(f"{END} aparece antes que {START}")
    return text[:s] + region + text[e + len(END):]
