"""Monograma «NG» en 3D para el visor STL interactivo de GitHub.

    python scripts/extras/logo3d.py > logo.stl

Las letras se componen de prismas convexos (trazos y segmentos de arco) sobre una base
octogonal; el resultado es un STL ASCII compacto que se pega en el README.
"""
import math

DEPTH, BASE_H = 6.0, 3.0


def prism(poly, z0, z1):
    """Extruye un polígono convexo (antihorario) entre z0 y z1. Devuelve triángulos."""
    tris, n = [], len(poly)
    for i in range(1, n - 1):
        a, b, c = poly[0], poly[i], poly[i + 1]
        tris.append(((a[0], a[1], z1), (b[0], b[1], z1), (c[0], c[1], z1)))
        tris.append(((a[0], a[1], z0), (c[0], c[1], z0), (b[0], b[1], z0)))
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        tris.append(((x0, y0, z0), (x1, y1, z0), (x1, y1, z1)))
        tris.append(((x0, y0, z0), (x1, y1, z1), (x0, y0, z1)))
    return tris


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def arc(cx, cy, r0, r1, a0, a1, steps):
    out = []
    for i in range(steps):
        t0 = math.radians(a0 + (a1 - a0) * i / steps)
        t1 = math.radians(a0 + (a1 - a0) * (i + 1) / steps)
        out.append([(cx + r1 * math.cos(t0), cy + r1 * math.sin(t0)),
                    (cx + r1 * math.cos(t1), cy + r1 * math.sin(t1)),
                    (cx + r0 * math.cos(t1), cy + r0 * math.sin(t1)),
                    (cx + r0 * math.cos(t0), cy + r0 * math.sin(t0))][::-1 if a1 > a0 else 1])
    return out


def ccw(poly):
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    return poly if area > 0 else poly[::-1]


def model():
    s = 4.0                                   # grosor del trazo
    parts = [rect(-24, -12, s, 24), rect(-8 - s, -12, s, 24),                 # N: palos
             [(-24 + s, 12), (-24 + s, 12 - 7), (-8 - s, -12), (-8 - s, -12 + 7)]]  # N: diagonal
    parts += arc(12, 0, 12 - s, 12, 40, 320, 14)                              # G: arco
    parts += [rect(12, -2, 12, s * .9), rect(24 - s, -12 + 2.5, s, 10.4)]      # G: barra y cola
    tris = []
    for poly in parts:
        tris += prism(ccw(poly), BASE_H, BASE_H + DEPTH)
    base = [(36 * math.cos(math.radians(22.5 + 45 * i)), 22 * math.sin(math.radians(22.5 + 45 * i)))
            for i in range(8)]
    tris += prism(ccw(base), 0, BASE_H)
    return tris


def normal(a, b, c):
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    m = math.sqrt(sum(x * x for x in n)) or 1
    return tuple(x / m for x in n)


def stl(tris):
    f = lambda v: " ".join(f"{x:.1f}".rstrip("0").rstrip(".") if "." in f"{x:.1f}" else f"{x:.1f}" for x in v)  # noqa: E731
    out = ["solid NG"]
    for t in tris:
        out.append(f"facet normal {' '.join(f'{x:.2f}' for x in normal(*t))}\nouter loop\n"
                   + "\n".join(f"vertex {f(v)}" for v in t) + "\nendloop\nendfacet")
    out.append("endsolid NG")
    return "\n".join(out)


if __name__ == "__main__":
    print(stl(model()))
