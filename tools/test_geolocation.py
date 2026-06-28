from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.geolocation import lokasi_perairan

tests = [
    (-6.5, 110.5),
    (-3.0, 125.0),
    (-10.518417192356152, 136.95566140056167),
]

print("=" * 60)
print("TEST GEOLOCATION")
print("=" * 60)

for lat, lon in tests:

    print()
    print("LAT :", lat)
    print("LON :", lon)

    print("HASIL :", lokasi_perairan(lat, lon))