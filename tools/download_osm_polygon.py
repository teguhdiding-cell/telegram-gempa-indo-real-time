"""
Downloader Polygon Laut Indonesia
Versi : V15.3

Author : Project Gempa Indonesia
"""

from pathlib import Path
import shapefile


def nama_file(nama):
    nama = nama.lower()
    nama = nama.replace(" ", "_")
    nama = nama.replace("/", "_")
    nama = nama.replace("-", "_")
    return nama + ".geojson"


print("=" * 60)
print("DOWNLOADER POLYGON LAUT INDONESIA V15.3")
print("=" * 60)

nama_laut = input("Masukkan nama laut : ").strip()

print()
print("Nama laut :", nama_laut)

# Folder tujuan
OUTPUT_FOLDER = (
    Path(__file__).parent.parent
    / "data"
    / "sea"
)

print("Folder tujuan :", OUTPUT_FOLDER)

file_geojson = nama_file(nama_laut)

print("Nama file :", file_geojson)

path_file = OUTPUT_FOLDER / file_geojson

print("Lokasi file :", path_file)