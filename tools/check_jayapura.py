from pathlib import Path
import sys

from shapely.geometry import Point

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.province_loader import build_database

db = build_database()

lat = -2.53
lon = 140.71

point = Point(lon, lat)

print("=" * 60)
print("CEK JAYAPURA")
print("=" * 60)

for item in db:

    minx, miny, maxx, maxy = item["bounds"]

    if (
        minx <= lon <= maxx
        and
        miny <= lat <= maxy
    ):

        print()
        print(item["name"])
        print("Bounds :", item["bounds"])
        print("Contains :", item["prepared"].contains(point))