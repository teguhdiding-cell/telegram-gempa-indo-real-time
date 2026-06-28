from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.sea_locator import find_sea

print("=" * 60)
print("TEST SEA LOCATOR")
print("=" * 60)

tests = [
    (-6.5, 110.5),      # Laut Jawa
    (-3.0, 125.0),      # Laut Maluku
    (-9.5, 118.0),      # Samudra Hindia
]

for lat, lon in tests:

    print()
    print(f"LAT : {lat}")
    print(f"LON : {lon}")

    hasil = find_sea(lat, lon)

    print("HASIL :", hasil)