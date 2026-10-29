"""Datos de GitHub para las tarjetas dinámicas. Solo librería estándar.

- Calendario de contribuciones: GraphQL (con token) y, si no hay token o falla, el HTML
  público de https://github.com/users/<usuario>/contributions.
- Repositorios y lenguajes: API REST (con token si lo hay; sin él, 60 peticiones/hora).

Cualquier fallo sin datos fiables lanza DataError: el script termina con código ≠ 0 y el
workflow no publica (se quedan las imágenes del día anterior).
"""
from __future__ import annotations

import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
WEB = "https://github.com"
UA = "Nicolasgm07-perfil (+https://github.com/Nicolasgm07/Nicolasgm07)"
USER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
MAX_YEARS = 12          # años de historial que se consultan para la racha máxima
# Lenguajes que en estos repos solo vienen de envoltorios y scripts generados
# (mvnw, mvnw.cmd de Maven…): no reflejan código escrito a mano.
IGNORED_LANGS = {"Batchfile", "Shell", "PowerShell", "Dockerfile", "Makefile", "Procfile"}


class DataError(RuntimeError):
    """No hay datos fiables con los que generar las tarjetas."""


def log(msg: str) -> None:
    print(f"  · {msg}", flush=True)


# ----------------------------------------------------------------------------- HTTP
def _request(url: str, *, token: str | None = None, payload: dict | None = None,
             accept: str = "application/vnd.github+json", retries: int = 3, timeout: float = 25) -> str:
    headers = {"User-Agent": UA, "Accept": accept}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    last = "sin respuesta"
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            # 4xx definitivos (salvo límites de uso): no tiene sentido reintentar
            if 400 <= e.code < 500 and e.code not in (403, 429):
                break
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last = type(e).__name__
        if attempt < retries - 1:
            time.sleep(2 * 2 ** attempt)
    # Nunca se incluye el token en los mensajes; la URL solo lleva el usuario.
    raise DataError(f"{url.split('?')[0]} → {last}")


def _get_json(url: str, token: str | None):
    try:
        return json.loads(_request(url, token=token))
    except DataError:
        if not token:
            raise
        log("la petición con token ha fallado; reintento sin token")
        return json.loads(_request(url))


# ------------------------------------------------------------------- calendario
_GQL_LAST_YEAR = """
query($login: String!) {
  user(login: $login) {
    createdAt
    contributionsCollection {
      contributionYears
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def _gql(query: str, variables: dict, token: str) -> dict:
    res = json.loads(_request(f"{API}/graphql", token=token, payload={"query": query, "variables": variables}))
    if res.get("errors") or not (res.get("data") or {}).get("user"):
        msg = "; ".join(e.get("message", "?") for e in res.get("errors") or []) or "usuario no encontrado"
        raise DataError(f"GraphQL: {msg}")
    return res["data"]["user"]


def _weeks_to_days(weeks: list) -> list[tuple[str, int]]:
    return [(d["date"], int(d["contributionCount"])) for w in weeks for d in w["contributionDays"]]


def calendar_graphql(user: str, token: str) -> dict:
    u = _gql(_GQL_LAST_YEAR, {"login": user}, token)
    cc = u["contributionsCollection"]
    days = _weeks_to_days(cc["contributionCalendar"]["weeks"])
    history = dict(days)
    years = sorted({int(y) for y in cc.get("contributionYears") or []})[-MAX_YEARS:]
    if years:
        # Un alias por año (máx. un año por consulta); los años son enteros validados.
        parts = "".join(
            f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") '
            f"{{ contributionCalendar {{ weeks {{ contributionDays {{ date contributionCount }} }} }} }}\n"
            for y in years)
        try:
            uy = _gql(f"query($login: String!) {{ user(login: $login) {{ {parts} }} }}", {"login": user}, token)
            for y in years:
                for d, n in _weeks_to_days(uy[f"y{y}"]["contributionCalendar"]["weeks"]):
                    history.setdefault(d, n)
        except (DataError, KeyError, TypeError) as e:
            log(f"historial por años no disponible ({e}); la racha máxima usa solo el último año")
    return {"source": "graphql", "days": days, "history": history,
            "total": int(cc["contributionCalendar"]["totalContributions"]), "created_at": u.get("createdAt")}


_TD = re.compile(r"<td\b[^>]*>")
_TIP = re.compile(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>')
_N = re.compile(r"^\s*([\d,.]+)\s+contributions?\b", re.I)


def parse_calendar_html(html: str) -> list[tuple[str, int]]:
    """[(fecha, contribuciones)] a partir del HTML público del calendario."""
    ids = {}
    for m in _TD.finditer(html):
        tag = m.group(0)
        d = re.search(r'\bdata-date="(\d{4}-\d{2}-\d{2})"', tag)
        i = re.search(r'\bid="([^"]+)"', tag)
        if d and i:
            ids[i.group(1)] = d.group(1)
    counts = {}
    for m in _TIP.finditer(html):
        date = ids.get(m.group(1))
        if not date:
            continue
        text = m.group(2).strip()
        n = _N.match(text)
        if n:
            counts[date] = int(re.sub(r"[,.]", "", n.group(1)))
        elif text.lower().startswith("no contributions"):
            counts[date] = 0
    if not ids or len(counts) < 0.95 * len(ids):
        raise DataError(f"HTML del calendario irreconocible ({len(counts)}/{len(ids)} días con dato)")
    return sorted(counts.items())


def calendar_html(user: str, created_year: int | None, today: dt.date) -> dict:
    base = f"{WEB}/users/{urllib.parse.quote(user)}/contributions"
    html = _request(base, accept="text/html")
    days = parse_calendar_html(html)
    if len(days) < 360:
        raise DataError(f"calendario incompleto: {len(days)} días")
    # Total oficial («N contributions in the last year»); si no aparece, la suma de los días.
    m = re.search(r'js-contribution-activity-description[^>]*>\s*([\d,.]+)\s+contribution', html)
    total = sum(n for _, n in days)
    if m:
        header_total = int(re.sub(r"[,.]", "", m.group(1)))
        if header_total != total:
            log(f"aviso: el total del encabezado ({header_total}) no cuadra con la suma ({total}); uso el del encabezado")
        total = header_total
    history = dict(days)
    first_year = max(created_year or today.year, today.year - MAX_YEARS + 1)
    for y in range(first_year, today.year + 1):
        try:
            for d, n in parse_calendar_html(_request(f"{base}?from={y}-01-01&to={y}-12-31", accept="text/html")):
                history.setdefault(d, n)
        except DataError as e:
            log(f"año {y} no disponible ({e}); la racha máxima puede quedarse corta")
    return {"source": "html", "days": days, "history": history, "total": total, "created_at": None}


# ------------------------------------------------------------- repos y lenguajes
def repos_and_languages(user: str, token: str | None) -> dict:
    q = urllib.parse.quote(user)
    profile = _get_json(f"{API}/users/{q}", token)
    repos, page = [], 1
    while page <= 10:
        batch = _get_json(f"{API}/users/{q}/repos?per_page=100&type=owner&sort=pushed&page={page}", token)
        if not isinstance(batch, list):
            raise DataError("respuesta inesperada al listar repositorios")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r.get("fork") and r.get("name", "").lower() != user.lower()]
    langs: dict[str, int] = {}
    counted = []
    for r in own:
        # Repo vacío: ni tamaño ni lenguaje. (Solo con size == 0 no basta: la API redondea a KB
        # y un repo pequeño con HTML puede tener size 0.)
        if not r.get("size") and not r.get("language"):
            continue
        data = _get_json(f"{API}/repos/{q}/{urllib.parse.quote(r['name'])}/languages", token)
        mine = {k: int(v) for k, v in data.items() if k not in IGNORED_LANGS}
        if mine:
            counted.append(r["name"])
        for k, v in mine.items():
            langs[k] = langs.get(k, 0) + v
    last = max(repos, key=lambda r: r.get("pushed_at") or "", default=None)
    last_own = max(own, key=lambda r: r.get("pushed_at") or "", default=None)
    return {
        "public_repos": int(profile.get("public_repos", len(repos))),
        "created_at": profile.get("created_at"),
        "own_repos": len(own),
        "lang_repos": counted,
        "languages": dict(sorted(langs.items(), key=lambda kv: -kv[1])),
        "last_push": (last_own or last or {}).get("name"),
    }


# ------------------------------------------------------------------- todo junto
def fetch_all(user: str, token: str | None, today: dt.date) -> dict:
    if not USER_RE.match(user or ""):
        raise DataError("nombre de usuario de GitHub no válido")
    rl = repos_and_languages(user, token)
    log(f"{rl['public_repos']} repos públicos, {len(rl['languages'])} lenguajes en {len(rl['lang_repos'])} repos")
    cal = None
    if token:
        try:
            cal = calendar_graphql(user, token)
        except (DataError, KeyError, TypeError, ValueError) as e:
            log(f"GraphQL no disponible ({e}); uso el HTML público")
    if cal is None:
        created_year = int(rl["created_at"][:4]) if rl.get("created_at") else None
        cal = calendar_html(user, created_year, today)
    log(f"calendario vía {cal['source']}: {len(cal['days'])} días, {cal['total']} contribuciones, "
        f"{len(cal['history'])} días de historial")
    return {
        "user": user,
        "source": cal["source"],
        "days": cal["days"],
        "history": sorted(cal["history"].items()),
        "total": cal["total"],
        **{k: rl[k] for k in ("public_repos", "own_repos", "lang_repos", "languages", "last_push")},
    }


# ---------------------------------------------------------------- estadísticas
def _streak_runs(counts: dict[dt.date, int]) -> list[tuple[dt.date, dt.date]]:
    runs, start, prev = [], None, None
    for d in sorted(counts):
        if counts[d] > 0:
            if start is None or prev is None or (d - prev).days != 1:
                if start is not None:
                    runs.append((start, prev))
                start = d
            prev = d
        elif start is not None:
            runs.append((start, prev))
            start = prev = None
    if start is not None:
        runs.append((start, prev))
    return runs


def compute_stats(data: dict) -> dict:
    days = [(dt.date.fromisoformat(d), int(n)) for d, n in data["days"]]
    if not days:
        raise DataError("calendario vacío")
    history = {dt.date.fromisoformat(d): int(n) for d, n in data["history"]}
    history.update(dict(days))
    end = days[-1][0]

    # Racha actual: si hoy aún no hay contribuciones, no se rompe (el día no ha terminado).
    d = end if history.get(end, 0) > 0 else end - dt.timedelta(days=1)
    cur_end = d
    n = 0
    while history.get(d, 0) > 0:
        n += 1
        d -= dt.timedelta(days=1)
    current = {"days": n, "start": d + dt.timedelta(days=1) if n else None, "end": cur_end if n else None}
    last_active = max((k for k, v in history.items() if v > 0 and k <= end), default=None)

    runs = _streak_runs(history)
    best = max(runs, key=lambda r: ((r[1] - r[0]).days, r[1]), default=None)  # empate → la más reciente
    longest = {"days": (best[1] - best[0]).days + 1 if best else 0,
               "start": best[0] if best else None, "end": best[1] if best else None}

    # Semanas como las columnas del calendario de GitHub (de domingo a sábado); las 52 últimas.
    weeks: list[list[tuple[dt.date, int]]] = []
    for day, cnt in days:
        if not weeks or day.weekday() == 6:       # domingo → nueva columna
            weeks.append([])
        weeks[-1].append((day, cnt))
    weeks = weeks[-52:]
    weekly = [{"start": w[0][0], "end": w[-1][0], "total": sum(c for _, c in w)} for w in weeks]
    total = data.get("total")
    return {
        # el número que enseña GitHub en el perfil; si faltara, la suma del calendario
        "total": int(total) if isinstance(total, int) and total >= 0 else sum(c for _, c in days),
        "end": end,
        "current": current,
        "longest": longest,
        "last_active": last_active,
        "weekly": weekly,
        "active_days": sum(1 for _, c in days if c > 0),
    }
