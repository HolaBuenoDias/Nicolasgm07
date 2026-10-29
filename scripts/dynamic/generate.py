"""Genera las imágenes dinámicas del perfil en -dark.svg y -light.svg:

    stats      actividad del último año (KPIs + contribuciones por semana)
    langs      lenguajes por bytes en mis repos (sin forks ni el repo del perfil)
    countdown  cuenta atrás para las prácticas + progreso del ciclo DAW

Lo ejecuta cada día .github/workflows/perfil.yml y publica el resultado en la rama "output":

    python3 scripts/dynamic/generate.py --out dist

- Usuario: --user, o la variable de entorno GH_USER (el workflow le pasa github.repository_owner).
- Token: GITHUB_TOKEN (opcional). Sin él, el calendario sale del HTML público de GitHub.
- Pruebas: --today AAAA-MM-DD simula la fecha (fases de la cuenta atrás); --save-data guarda
  los datos descargados y --data los reutiliza (para iterar el diseño sin gastar peticiones).

Si no hay datos fiables termina con código 1: el workflow no publica y se quedan las
imágenes del día anterior. Solo librería estándar.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # scripts/ → brand, content
sys.path.insert(0, HERE)                    # scripts/dynamic/ → ghdata, cards
from brand import OWNER, THEMES  # noqa: E402
import cards  # noqa: E402
import ghdata  # noqa: E402

MAX_BYTES = 60_000   # límite de peso de DESIGN.md para SVG sin imágenes


# ------------------------------------------------------------------------- fecha
def _last_sunday(year: int, month: int) -> dt.date:
    d = dt.date(year, month, 31)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def madrid_now(now: dt.datetime | None = None) -> dt.datetime:
    """Hora de Madrid. Si zoneinfo no tiene tzdata (Windows sin el paquete tzdata), aplica a
    mano la regla de la UE: horario de verano (UTC+2) del último domingo de marzo al último
    domingo de octubre, a las 01:00 UTC; el resto del año, UTC+1."""
    now = now or dt.datetime.now(dt.timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        return now.astimezone(ZoneInfo("Europe/Madrid"))
    except Exception:  # ZoneInfoNotFoundError, ImportError…
        y = now.astimezone(dt.timezone.utc).year
        start = dt.datetime.combine(_last_sunday(y, 3), dt.time(1), dt.timezone.utc)
        end = dt.datetime.combine(_last_sunday(y, 10), dt.time(1), dt.timezone.utc)
        offset = 2 if start <= now < end else 1
        return now.astimezone(dt.timezone(dt.timedelta(hours=offset)))


# ---------------------------------------------------------------------- datos
def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def _check(name: str, svg: str) -> None:
    """Nunca publicar un SVG roto o desmesurado."""
    try:
        ET.fromstring(svg)
    except ET.ParseError as e:
        raise ghdata.DataError(f"{name}: SVG mal formado ({e})") from None
    size = len(svg.encode("utf-8"))
    if size > MAX_BYTES:
        raise ghdata.DataError(f"{name}: {size} bytes (máx. {MAX_BYTES})")


def build_all(data: dict, today: dt.date) -> dict[str, str]:
    stats = ghdata.compute_stats(data)
    out = {}
    for theme, p in THEMES.items():
        out[f"stats-{theme}.svg"] = cards.stats_svg(theme, p, stats, data, today)
        out[f"langs-{theme}.svg"] = cards.langs_svg(theme, p, data)
        out[f"countdown-{theme}.svg"] = cards.countdown_svg(theme, p, today)
    for name, svg in out.items():
        _check(name, svg)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Imágenes dinámicas del perfil de GitHub")
    ap.add_argument("--out", required=True, help="carpeta de salida (p. ej. dist)")
    ap.add_argument("--user", default=os.environ.get("GH_USER") or OWNER,
                    help="usuario de GitHub (por defecto, $GH_USER)")
    ap.add_argument("--today", type=dt.date.fromisoformat, help="fecha simulada AAAA-MM-DD")
    ap.add_argument("--data", help="usar datos guardados (JSON) en vez de descargarlos")
    ap.add_argument("--save-data", help="guardar los datos descargados en este JSON")
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):   # consolas de Windows en cp1252: sin UnicodeEncodeError
        try:
            stream.reconfigure(errors="replace")
        except AttributeError:
            pass

    today = a.today or madrid_now().date()
    token = (os.environ.get("GITHUB_TOKEN") or "").strip() or None
    print(f"Perfil dinámico de @{a.user} · {today:%d/%m/%Y} · "
          f"{'con token' if token else 'sin token (HTML público)'}", flush=True)
    try:
        data = _load(a.data) if a.data else ghdata.fetch_all(a.user, token, today)
        if a.save_data:
            _save(a.save_data, data)
        files = build_all(data, today)
    except ghdata.DataError as e:
        print(f"✖ Sin datos fiables, no se genera nada: {e}", file=sys.stderr)
        return 1

    os.makedirs(a.out, exist_ok=True)
    for name, svg in files.items():
        path = os.path.join(a.out, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(f"  {name:<22} {len(svg.encode('utf-8')) / 1024:5.1f} KB")
    print(f"✔ {len(files)} SVG en {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
