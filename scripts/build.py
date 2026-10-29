"""Regenera todos los SVG estáticos de assets/ a partir de scripts/components/*.py.

    python scripts/build.py              # todo
    python scripts/build.py hero about   # solo esos componentes
"""
import importlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "components"))


def main(argv):
    names = sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "components"))
                   if f.endswith(".py") and not f.startswith("_"))
    if argv:
        names = [n for n in names if n in argv]
    total = 0
    for name in names:
        t = time.time()
        files = importlib.import_module(name).main() or []
        total += len(files)
        print(f"  {name:<14} {len(files):>3} archivos  {time.time() - t:.2f}s")
    print(f"{total} SVG generados")


if __name__ == "__main__":
    main(sys.argv[1:])
