from pathlib import Path
import sys
import random
import time

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.sea_locator import find_sea

print("=" * 60)
print("BENCHMARK SEA LOCATOR")
print("=" * 60)

TOTAL = 10000

# Koordinat acak di sekitar Indonesia
points = [
    (
        random.uniform(-12, 8),
        random.uniform(94, 142)
    )
    for _ in range(TOTAL)
]

start = time.perf_counter()

found = 0

for lat, lon in points:

    hasil = find_sea(lat, lon)

    if hasil:
        found += 1

elapsed = time.perf_counter() - start

print()
print("Jumlah Test :", TOTAL)
print("Ditemukan   :", found)
print(f"Waktu       : {elapsed:.3f} detik")
print(f"Rata-rata   : {elapsed / TOTAL * 1000:.3f} ms/pencarian")