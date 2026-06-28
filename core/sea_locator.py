from shapely.geometry import Point

from core.sea_loader import load_all


print("=" * 60)
print("MEMUAT DATABASE POLYGON LAUT")
print("=" * 60)

DATABASE = load_all()

print("Jumlah Polygon :", len(DATABASE))
print()


def find_sea(lat, lon):
    """
    Mengembalikan nama laut berdasarkan koordinat.
    """

    point = Point(lon, lat)

    for item in DATABASE:

        # Ambil Bounding Box polygon
        minx, miny, maxx, maxy = item["bounds"]

        # Filter cepat
        if not (
            minx <= lon <= maxx
            and
            miny <= lat <= maxy
        ):
            continue

        # Cek polygon yang lolos Bounding Box
        if item["prepared"].contains(point):
            return item["name"]

    return None