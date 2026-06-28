from pathlib import Path
import pickle
import sys
import time

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.sea_loader import load_all

CACHE_DIR = ROOT / "cache"
CACHE_FILE = CACHE_DIR / "polygon_cache.pkl"

print("=" * 60)
print("MEMBANGUN POLYGON CACHE")
print("=" * 60)

CACHE_DIR.mkdir(exist_ok=True)

start = time.perf_counter()

database = load_all()

elapsed = time.perf_counter() - start

cache = []

for item in database:

    cache.append({
        "name": item["name"],
        "polygon": item["polygon"],
        "bounds": item["bounds"]
    })

with open(CACHE_FILE, "wb") as f:
    pickle.dump(cache, f)

print()
print("Jumlah Polygon :", len(database))
print("Cache :", CACHE_FILE)
print(f"Waktu Build : {elapsed:.3f} detik")