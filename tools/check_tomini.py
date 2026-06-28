from pathlib import Path
import sys
import json

from shapely.geometry import shape, Point

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

# ===========================
# LOAD POLYGON GULF OF TOMINI
# ===========================

FILE = (
    ROOT
    / "data"
    / "gulf"
    / "gulf_of_tomini.geojson"
)

with open(FILE, encoding="utf-8") as f:
    geojson = json.load(f)

polygon = shape(geojson["geometry"])

print("=" * 70)
print("CEK POLYGON GULF OF TOMINI")
print("=" * 70)

# ===========================
# TITIK YANG GAGAL
# ===========================

points = [
    (-1.139675, 120.150703),
    (-1.078868, 120.130478),
    (-1.176129, 120.253716),
    (-1.283927, 120.294075),
    (-1.145353, 120.211754),
    (-1.229850, 120.209915),
    (-1.229467, 120.228355),
    (-1.243615, 120.271049),
    (-1.189365, 120.193924),
    (-1.151275, 120.221352),
]

for i, (lat, lon) in enumerate(points, start=1):

    point = Point(lon, lat)

    inside = polygon.contains(point)

    print(
        f"{i:02d} | "
        f"{lat:.6f}, {lon:.6f} | "
        f"{'INSIDE' if inside else 'OUTSIDE'}"
    )