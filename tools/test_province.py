from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.province_loader import build_database

print("=" * 60)
print("MEMUAT DATABASE PROVINSI")
print("=" * 60)

db = build_database()

print()

print("Jumlah Provinsi :", len(db))

print()

for item in db[:10]:
    print(item["name"])