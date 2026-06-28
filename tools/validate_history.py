import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent

load_dotenv(ROOT / ".env")

import sys
sys.path.append(str(ROOT))

from supabase import create_client
from core.geolocation import lokasi_perairan

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("=" * 80)
print("VALIDASI RIWAYAT GEMPA")
print("=" * 80)

response = (
    supabase
    .table("earthquake_log")
    .select("*")
    .order("waktu", desc=True)
    .limit(100)
    .execute()
)

rows = response.data

print("Jumlah Data :", len(rows))
print()

statistik = {}

none_count = 0
darat_count = 0
bug_count = 0

for i, row in enumerate(rows, start=1):

    lat = row["latitude"]
    lon = row["longitude"]

    laut = lokasi_perairan(lat, lon)

    if laut == "🌊 Perairan Indonesia":

        none_count += 1

        kabupaten = row["kabupaten"].lower()

        kata_laut = [
            "perairan",
            "laut",
            "samudra",
            "selat",
            "ocean",
            "sea",
            "teluk",
            "gulf"
        ]

        if any(k in kabupaten for k in kata_laut):

            bug_count += 1
            status = "BUG POLYGON"

            print()
            print("=" * 80)
            print("BUG POLYGON")
            print("=" * 80)
            print("No        :", i)
            print("Kabupaten :", row["kabupaten"])
            print("Provinsi  :", row["provinsi"])
            print("Lat       :", lat)
            print("Lon       :", lon)
            print("=" * 80)

        else:

            darat_count += 1
            status = "DARAT"

        print()
        print("=" * 80)
        print(status)
        print("=" * 80)

        print("No        :", i)
        print("Kabupaten :", row["kabupaten"])
        print("Provinsi  :", row["provinsi"])
        print("Lat       :", lat)
        print("Lon       :", lon)

        print("=" * 80)
        print()

    statistik[laut] = statistik.get(laut, 0) + 1

    print(
        f"{i:03d} | "
        f"M{row['magnitudo']:.1f} | "
        f"{row['kabupaten']} | "
        f"{lat:.3f},{lon:.3f} | "
        f"{laut}"
    )

print()
print("=" * 80)
print("STATISTIK")
print("=" * 80)

ranking = sorted(
    statistik.items(),
    key=lambda x: x[1],
    reverse=True
)

for nama, jumlah in ranking:
    print(f"{jumlah:3d} | {nama}")

print()
print("=" * 80)
print("RINGKASAN")
print("=" * 80)

print("Total Gempa        :", len(rows))
print("Tidak Teridentifikasi :", none_count)
print("Gempa Darat        :", darat_count)
print("Bug Polygon        :", bug_count)

akurasi = (
    (len(rows) - none_count)
    / len(rows)
    * 100
)

print(f"Akurasi : {akurasi:.2f}%")