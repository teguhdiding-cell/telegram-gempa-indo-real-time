from pathlib import Path
import sys

from shapely.geometry import Point

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.sea_loader import load_all

print("=" * 60)
print("MEMUAT DATABASE")
print("=" * 60)

database = load_all()

print("Jumlah Polygon :", len(database))
print()

# ===========================
# TEST KOORDINAT
# ===========================

lat = -10.518417192356152
lon = 136.95566140056167

point = Point(lon, lat)

print("TEST KOORDINAT")
print("LAT :", lat)
print("LON :", lon)
print()

found = False

for item in database:

    if item["polygon"].contains(point):

        print("DITEMUKAN")
        print("Nama :", item["name"])

        found = True
        break

if not found:
    print("Tidak ditemukan")