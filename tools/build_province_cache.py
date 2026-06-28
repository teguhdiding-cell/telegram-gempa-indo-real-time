from pathlib import Path
import pickle
import sys
import time

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.province_loader import build_database

CACHE_DIR = ROOT / "cache"
CACHE_FILE = CACHE_DIR / "province_cache.pkl"

print("=" * 60)
print("MEMBANGUN PROVINCE CACHE")
print("=" * 60)

CACHE_DIR.mkdir(exist_ok=True)

start = time.perf_counter()

database = build_database()

cache = []

for item in database:

    cache.append({
        "name": item["name"],
        "polygon": item["polygon"],
        "bounds": item["bounds"]
    })

with open(CACHE_FILE, "wb") as f:
    pickle.dump(cache, f)

elapsed = time.perf_counter() - start

print()
print("Jumlah Provinsi :", len(cache))
print("Cache :", CACHE_FILE)
print(f"Waktu Build : {elapsed:.3f} detik")