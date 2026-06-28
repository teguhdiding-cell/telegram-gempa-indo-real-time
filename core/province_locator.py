from shapely.geometry import Point

from core.province_loader import build_database

print("=" * 60)
print("MEMUAT DATABASE PROVINSI")
print("=" * 60)

from core.province_loader import load_all

DATABASE = load_all()

print("Jumlah Provinsi :", len(DATABASE))
print()


def find_province(lat, lon):

    point = Point(lon, lat)

    for item in DATABASE:

        minx, miny, maxx, maxy = item["bounds"]

        if not (
            minx <= lon <= maxx
            and
            miny <= lat <= maxy
        ):
            continue

        if item["prepared"].contains(point):
            return item["name"]

    return None