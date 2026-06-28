from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.sea_loader import load_all

db = load_all()

nama = input("Nama polygon : ").strip().lower()

for item in db:

    if item["name"].lower() == nama:

        poly = item["polygon"]

        print("=" * 60)
        print("NAMA :", item["name"])
        print("=" * 60)

        print("Tipe :", poly.geom_type)
        print("Valid :", poly.is_valid)
        print("Luas :", poly.area)

        print()

        print("Bounding Box")
        print(poly.bounds)

        print()

        c = poly.centroid

        print("Centroid")
        print("LAT :", c.y)
        print("LON :", c.x)

        break

else:
    print("Tidak ditemukan")