"""Tres en raya comunitario por issues. Lo ejecuta .github/workflows/tres-en-raya.yml.

    python3 scripts/game/ttt.py --event "$GITHUB_EVENT_PATH" --out "$RUNNER_TEMP/ttt"
        Aplica la jugada del issue del evento (y la de cualquier otro issue «ttt|…» que
        siga abierto porque su ejecución se canceló), guarda state.json, reescribe la
        región del README y deja en --out las respuestas (replies.json) y el mensaje del
        commit (commit.txt). No llama a la API para escribir: eso va después del push.
    python3 scripts/game/ttt.py --reply "$RUNNER_TEMP/ttt/replies.json"
        Comenta en cada issue y lo cierra (completed u not_planned).
    python3 scripts/game/ttt.py --apologize "$GITHUB_EVENT_PATH"
        Si algo ha fallado antes: lo explica en el issue y lo cierra sin aplicar nada.

En local:
    python scripts/game/ttt.py --snippet                    # región de una partida nueva
    python scripts/game/ttt.py --render                     # reescribe la región desde state.json
    python scripts/game/ttt.py --play 5 --user prueba       # simula una jugada (--dry-run: sin guardar)

Seguridad: el título, el autor y el resto del issue se leen del JSON del evento o de la
API, nunca de la línea de órdenes. El título solo se acepta si encaja entera con
^ttt\\|(move\\|[1-9]|new)$ y los nombres de usuario se validan antes de escribirlos.
Solo librería estándar.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E  # noqa: E402
import region as R  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STATE_PATH = os.path.join(HERE, "state.json")
README_PATH = os.path.join(ROOT, "README.md")

KEEP_RECENT = 10          # jugadas que se guardan (en el README se ven 5)
KEEP_PROCESSED = 200      # números de issue ya aplicados (para no aplicar dos veces el mismo)
SWEEP_LIMIT = 20          # issues «ttt|» abiertos que se recogen en una ejecución
COMPLETED, NOT_PLANNED = "completed", "not_planned"
LOGIN_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", re.ASCII)
SOURCE_URL = f"https://github.com/{R.REPO}/tree/main/scripts/game"
FOOTER = (f"\n\n<sub>Respuesta automática de GitHub Actions · el código está en "
          f"[scripts/game]({SOURCE_URL})</sub>")


@dataclass
class Reply:
    issue: int
    body: str
    reason: str          # completed | not_planned


# ------------------------------------------------------------------------------ estado
def new_game(number: int) -> dict:
    return {"number": number, "board": ["---", "---", "---"], "status": "playing",
            "line": None, "last": None, "moves": []}


def new_state() -> dict:
    return {
        "about": "Estado del tres en raya del README. Lo actualiza .github/workflows/tres-en-raya.yml; no lo edites a mano.",
        "version": 1,
        "game": new_game(1),
        "stats": {"games": 0, "visitors": 0, "cpu": 0, "draws": 0, "moves": 0},
        "recent": [],
        "players": {},
        "processed": [],
        "updated": None,
    }


def board_of(state: dict) -> str:
    return "".join(state["game"]["board"])


def set_board(game: dict, board: str) -> None:
    game["board"] = [board[0:3], board[3:6], board[6:9]]


def load_state(path: str) -> dict:
    if not os.path.exists(path):
        return new_state()
    with open(path, encoding="utf-8") as f:
        state = json.load(f)
    if state.get("version") != 1 or not E.is_valid_board(board_of(state)):
        raise ValueError(f"{path} no tiene un estado válido")
    return state


def save_state(path: str, state: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def clean_login(login) -> str | None:
    return login if isinstance(login, str) and LOGIN_RE.fullmatch(login) else None


# --------------------------------------------------------------------------- mensajes
def mention(login: str | None) -> str:
    return f"@{login}" if login else "visitante"


def board_text(board: str) -> str:
    rows = ["     A   B   C"]
    for r in range(3):
        cells = [board[r * 3 + c] if board[r * 3 + c] != E.EMPTY else "·" for c in range(3)]
        rows.append(f"  {r + 1}  " + " │ ".join(cells))
        if r < 2:
            rows.append("    ───┼───┼───")
    return "```text\n" + "\n".join(rows) + "\n```"


def line_name(line) -> str:
    return "–".join(E.CELLS[i] for i in line)


def result_text(status: str) -> str:
    return {E.X: "ganaron los visitantes", E.O: "ganó la CPU", "draw": "acabó en empate"}.get(status, "")


def safe_title(title) -> str:
    t = str(title).replace("`", "'").replace("\n", " ").strip()
    return (t[:60] + "…") if len(t) > 60 else (t or "(vacío)")


def msg_move(login, cell, cpu, status, line, board, number) -> str:
    who = mention(login)
    grid = board_text(board)
    if status == E.X:
        return (f"¡Tres en raya, {who}! 🎉 Tu **X** en **{cell}** completa la línea **{line_name(line)}** "
                f"y los visitantes ganan la partida n.º {number}.\n\n{grid}\n\n"
                f"Ya estás en el marcador del perfil. ¿Otra? Pulsa «Nueva partida» en {R.PLAY_URL}")
    if status == E.O:
        return (f"Has puesto una **X** en **{cell}**, {who}, pero la CPU ha respondido en **{cpu}** y ha hecho "
                f"tres en raya (**{line_name(line)}**). Esta vez gana la máquina 🤖\n\n{grid}\n\n"
                f"¡La próxima seguro que cae! Empieza otra con «Nueva partida» en {R.PLAY_URL}")
    if status == "draw":
        reply = f" y la CPU ha respondido en **{cpu}**" if cpu else ""
        return (f"Has puesto una **X** en **{cell}**, {who}{reply}, y el tablero se ha llenado: "
                f"**empate** 🤝 en la partida n.º {number}.\n\n{grid}\n\n"
                f"¿La desempatamos? Pulsa «Nueva partida» en {R.PLAY_URL}")
    return (f"¡Gracias por jugar, {who}! Has puesto una **X** en **{cell}** y la CPU ha respondido con una "
            f"**O** en **{cpu}**.\n\n{grid}\n\n"
            f"La partida n.º {number} sigue abierta: vuelve al perfil y elige otra casilla libre "
            f"(o deja que otro visitante haga la siguiente). 👉 {R.PLAY_URL}")


def msg_new(login, number) -> str:
    return (f"¡Partida nueva lista, {mention(login)}! Es la n.º {number} y el tablero está vacío: "
            f"abre tú con la primera **X**. 👉 {R.PLAY_URL}")


def msg_bad_title(login, title) -> str:
    return (f"Hola, {mention(login)}. No he entendido la jugada: el título tiene que ser exactamente "
            f"`ttt|move|1` … `ttt|move|9` o `ttt|new`, y este issue se titula `{safe_title(title)}`. "
            f"No he cambiado nada.\n\nLo más fácil es pulsar una casilla del tablero: el issue se rellena solo. "
            f"👉 {R.PLAY_URL}")


def msg_occupied(login, cell) -> str:
    return (f"¡Uy, {mention(login)}! La casilla **{cell}** ya está ocupada (alguien se te ha adelantado), así "
            f"que no he cambiado nada. Vuelve al tablero y elige otra casilla libre. 👉 {R.PLAY_URL}")


def msg_game_over(login, number, status) -> str:
    return (f"La partida n.º {number} ya ha terminado ({result_text(status)}), así que no he aplicado tu "
            f"jugada, {mention(login)}. Empieza otra con «Nueva partida» en {R.PLAY_URL} y luego elige tu casilla.")


def msg_new_while_playing(login, number, moves) -> str:
    if not moves:
        return (f"La partida n.º {number} ya está lista y esperando su primera jugada, {mention(login)}: "
                f"no hace falta empezar otra. Elige una casilla en {R.PLAY_URL}")
    return (f"La partida n.º {number} sigue en juego, {mention(login)}, así que no he empezado otra: "
            f"termínala primero. Te toca a ti: elige una casilla libre en {R.PLAY_URL}")


def msg_apology(login) -> str:
    return (f"Lo siento, {mention(login)}: algo ha fallado al guardar el tablero y tu jugada no se ha aplicado "
            f"(no es culpa tuya). Prueba otra vez en un rato desde {R.PLAY_URL}")


# ------------------------------------------------------------------------------ reglas
def apply_issue(state: dict, issue: int, title, login, *, rng: random.Random,
                now: str | None = None, random_rate: float = E.RANDOM_RATE):
    """Aplica un issue al estado.

    Devuelve (estado, Reply | None, resumen | None). Si la jugada no es válida se
    devuelve el MISMO objeto de estado, sin tocar, y un Reply not_planned. Si el issue ya
    se aplicó (reintento), no hay respuesta.
    """
    if issue in state["processed"]:
        return state, None, None
    login = clean_login(login)
    parsed = E.parse_title(title)
    if parsed is None:
        return state, Reply(issue, msg_bad_title(login, title), NOT_PLANNED), None
    kind, cell = parsed
    g = state["game"]

    if kind == "new":
        if g["status"] == "playing":
            return state, Reply(issue, msg_new_while_playing(login, g["number"], g["moves"]), NOT_PLANNED), None
        new = copy.deepcopy(state)
        new["game"] = new_game(g["number"] + 1)
        _bookkeeping(new, issue, now)
        n = new["game"]["number"]
        return new, Reply(issue, msg_new(login, n), COMPLETED), f"partida nueva n.º {n} (#{issue})"

    if g["status"] != "playing":
        return state, Reply(issue, msg_game_over(login, g["number"], g["status"]), NOT_PLANNED), None
    board = board_of(state)
    if board[cell] != E.EMPTY:
        return state, Reply(issue, msg_occupied(login, E.CELLS[cell]), NOT_PLANNED), None

    new = copy.deepcopy(state)
    g = new["game"]
    board = E.play(board, cell, E.X)
    g["moves"].append({"cell": E.CELLS[cell], "by": E.X, "user": login, "issue": issue})
    g["last"] = cell
    cpu = None
    if not E.outcome(board):
        cpu = E.cpu_move(board, E.O, rng, random_rate)
        board = E.play(board, cpu, E.O)
        g["moves"].append({"cell": E.CELLS[cpu], "by": E.O})
        g["last"] = cpu
    set_board(g, board)
    result = E.outcome(board)
    w = E.winner(board)
    g["status"] = result or "playing"
    g["line"] = list(w[1]) if w else None

    st = new["stats"]
    st["moves"] += 1
    if result:
        st["games"] += 1
        st[{E.X: "visitors", E.O: "cpu", "draw": "draws"}[result]] += 1
    if login:
        p = new["players"].setdefault(login, {"moves": 0, "wins": 0})
        p["moves"] += 1
        if result == E.X:
            p["wins"] += 1
    new["recent"].insert(0, {"game": g["number"], "issue": issue, "user": login, "cell": E.CELLS[cell],
                             "cpu": E.CELLS[cpu] if cpu is not None else None, "result": result})
    del new["recent"][KEEP_RECENT:]
    _bookkeeping(new, issue, now)

    cpu_name = E.CELLS[cpu] if cpu is not None else None
    body = msg_move(login, E.CELLS[cell], cpu_name, g["status"], g["line"], board, g["number"])
    summary = f"{mention(login)} juega {E.CELLS[cell]}"
    summary += {E.X: " y ganan los visitantes", E.O: f", la CPU responde {cpu_name} y gana",
                "draw": " y queda en empate"}.get(result, f", la CPU responde {cpu_name}")
    return new, Reply(issue, body, COMPLETED), f"{summary} (#{issue})"


def _bookkeeping(state: dict, issue: int, now: str | None) -> None:
    state["processed"].append(issue)
    del state["processed"][:-KEEP_PROCESSED]
    state["updated"] = now or datetime.now(timezone.utc).isoformat(timespec="seconds")


def commit_message(summaries: list[str]) -> str:
    if not summaries:
        return "Tres en raya: tablero sincronizado"
    if len(summaries) == 1:
        return f"Tres en raya: {summaries[0]}"
    return f"Tres en raya: {len(summaries)} jugadas\n\n" + "\n".join(f"- {s}" for s in summaries)


# --------------------------------------------------------------------------- README
def update_readme(path: str, state: dict) -> bool:
    """Reescribe solo la región del tablero. Devuelve True si el fichero ha cambiado."""
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    new = R.replace_region(text, R.render(state))
    if new == text:
        return False
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    return True


# ------------------------------------------------------------------------- API GitHub
class GitHub:
    """Cliente mínimo de la API REST con urllib (sin dependencias)."""

    def __init__(self, token: str, repo: str, base: str = "https://api.github.com"):
        self.token, self.repo, self.base = token, repo, base

    @classmethod
    def from_env(cls) -> GitHub | None:
        token = os.environ.get("GITHUB_TOKEN")
        return cls(token, os.environ.get("GITHUB_REPOSITORY", R.REPO)) if token else None

    def request(self, method: str, path: str, data: dict | None = None, attempts: int = 3):
        body = json.dumps(data).encode() if data is not None else None
        for i in range(attempts):
            req = urllib.request.Request(self.base + path, data=body, method=method, headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "tres-en-raya-bot",
                **({"Content-Type": "application/json"} if body else {}),
            })
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    raw = r.read()
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as e:
                if e.code < 500 or i == attempts - 1:
                    raise
            except urllib.error.URLError:
                if i == attempts - 1:
                    raise
            time.sleep(2 * (i + 1))

    def issue(self, number: int) -> dict:
        return self.request("GET", f"/repos/{self.repo}/issues/{number}")

    def open_game_issues(self) -> list[dict]:
        items = self.request("GET", f"/repos/{self.repo}/issues?state=open&sort=created&direction=asc&per_page=100")
        return [i for i in items or [] if "pull_request" not in i
                and isinstance(i.get("title"), str) and i["title"][:4].lower() == "ttt|"][:SWEEP_LIMIT]

    def comment(self, number: int, body: str) -> None:
        self.request("POST", f"/repos/{self.repo}/issues/{number}/comments", {"body": body})

    def close(self, number: int, reason: str) -> None:
        self.request("PATCH", f"/repos/{self.repo}/issues/{number}", {"state": "closed", "state_reason": reason})


def warn(msg: str) -> None:
    print(f"::warning::{msg}", flush=True)


# ------------------------------------------------------------------------------ modos
def collect_issues(event: dict, api: GitHub | None) -> dict[int, tuple]:
    """Issues por atender: el del evento + los «ttt|» que sigan abiertos (cuando varias
    ejecuciones coinciden, GitHub cancela las que esperan en la cola de concurrencia)."""
    queue = {}
    issue = event.get("issue") or {}
    number = issue.get("number")
    if isinstance(number, int):
        queue[number] = (issue.get("title"), (issue.get("user") or {}).get("login"))
    if api:
        try:
            if isinstance(number, int) and api.issue(number).get("state") != "open":
                queue.pop(number)        # ya lo atendió otra ejecución
        except Exception as e:  # noqa: BLE001 - la API es opcional aquí
            warn(f"no he podido comprobar el issue #{number}: {e}")
        try:
            for it in api.open_game_issues():
                queue.setdefault(it["number"], (it.get("title"), (it.get("user") or {}).get("login")))
        except Exception as e:  # noqa: BLE001
            warn(f"no he podido buscar otros issues abiertos: {e}")
    return queue


def run_event(event_path: str, out_dir: str, *, state_path: str = STATE_PATH, readme_path: str = README_PATH,
              api: GitHub | None = None, rng: random.Random | None = None) -> list[Reply]:
    with open(event_path, encoding="utf-8") as f:
        event = json.load(f)
    rng = rng or random.Random()
    state = load_state(state_path)
    replies, summaries = [], []
    for number, (title, login) in sorted(collect_issues(event, api).items()):
        state, reply, summary = apply_issue(state, number, title, login, rng=rng)
        if reply:
            replies.append(reply)
        if summary:
            summaries.append(summary)
            print(f"✔ #{number}: {summary}")
        elif reply:
            print(f"✘ #{number}: jugada no válida, el estado no cambia")
    if summaries:
        save_state(state_path, state)
    update_readme(readme_path, state)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "replies.json"), "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in replies], f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "commit.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(commit_message(summaries) + "\n")
    return replies


def send_replies(path: str, api: GitHub) -> int:
    """Comenta y cierra. Un fallo aquí no tumba el job: la jugada ya está guardada."""
    with open(path, encoding="utf-8") as f:
        replies = json.load(f)
    failed = 0
    for r in replies:
        try:
            api.comment(r["issue"], r["body"] + FOOTER)
            api.close(r["issue"], r["reason"])
            print(f"✔ respondido y cerrado #{r['issue']} ({r['reason']})")
        except Exception as e:  # noqa: BLE001
            failed += 1
            warn(f"no he podido responder en #{r['issue']}: {e}")
    return failed


def apologize(event_path: str, api: GitHub) -> None:
    with open(event_path, encoding="utf-8") as f:
        issue = json.load(f).get("issue") or {}
    number = issue.get("number")
    if not isinstance(number, int):
        return
    try:
        if api.issue(number).get("state") != "open":
            return
        api.comment(number, msg_apology(clean_login((issue.get("user") or {}).get("login"))) + FOOTER)
        api.close(number, NOT_PLANNED)
    except Exception as e:  # noqa: BLE001
        warn(f"tampoco he podido avisar en #{number}: {e}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tres en raya comunitario por issues.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--event", metavar="JSON", help="evento de GitHub (GITHUB_EVENT_PATH)")
    mode.add_argument("--reply", metavar="JSON", help="replies.json generado por --event")
    mode.add_argument("--apologize", metavar="JSON", help="avisa en el issue del evento de que algo falló")
    mode.add_argument("--render", action="store_true", help="reescribe la región del README desde el estado")
    mode.add_argument("--snippet", action="store_true", help="imprime la región de una partida nueva")
    mode.add_argument("--play", type=int, metavar="1-9", help="simula una jugada en local")
    ap.add_argument("--out", default=os.path.join(os.environ.get("RUNNER_TEMP", "."), "ttt"))
    ap.add_argument("--state", default=STATE_PATH)
    ap.add_argument("--readme", default=README_PATH)
    ap.add_argument("--user", default="visitante-local")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--dry-run", action="store_true", help="con --play: no guarda nada")
    a = ap.parse_args(argv)
    rng = random.Random(a.seed)

    if a.snippet:
        print(R.render(new_state()))
    elif a.render:
        changed = update_readme(a.readme, load_state(a.state))
        print("README actualizado" if changed else "README ya estaba al día")
    elif a.event:
        run_event(a.event, a.out, state_path=a.state, readme_path=a.readme, api=GitHub.from_env(), rng=rng)
    elif a.reply:
        api = GitHub.from_env()
        if not api:
            print("Falta GITHUB_TOKEN", file=sys.stderr)
            return 1
        send_replies(a.reply, api)
    elif a.apologize:
        api = GitHub.from_env()
        if api:
            apologize(a.apologize, api)
    else:
        state = load_state(a.state)
        issue = max(state["processed"], default=0) + 1
        state, reply, summary = apply_issue(state, issue, f"ttt|move|{a.play}", a.user, rng=rng)
        print(reply.body if reply else "(sin respuesta)")
        if summary and not a.dry_run:
            save_state(a.state, state)
            update_readme(a.readme, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
