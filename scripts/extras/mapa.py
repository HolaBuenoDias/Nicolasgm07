"""Mapa GeoJSON (GitHub lo muestra como mapa interactivo). Puntos a nivel de municipio.

    python scripts/extras/mapa.py
"""
import json
import math

PLACES = [  # (lon, lat, título, descripción)
    (-5.7208, 37.3896, "El Viso del Alcor", "Aquí vivo."),
    (-5.7480, 37.3729, "Mairena del Alcor · IES Los Alcores", "Aquí estudio 2.º de DAW (antes, SMR)."),
    (-5.9845, 37.3891, "Sevilla", "Sevilla capital."),
]


def km(a, b):
    (lo1, la1), (lo2, la2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def geojson():
    d = km(PLACES[0][:2], PLACES[2][:2])
    feats = []
    for i, (lon, lat, title, desc) in enumerate(PLACES):
        if i == 2:
            desc += f" A unos {d:.0f} km en línea recta de El Viso del Alcor."
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
                      "properties": {"title": title, "description": desc, "marker-color": "#F2511B",
                                     "marker-symbol": ["home", "college", "city"][i]}})
    feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": [p[:2] for p in PLACES]},
                  "properties": {"title": "Los Alcores → Sevilla", "stroke": "#F2511B", "stroke-width": 3}})
    return json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    print(geojson())
