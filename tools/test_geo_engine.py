from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.geo_engine import locate

print("=" * 60)
print("TEST GEO ENGINE")
print("=" * 60)

TESTS = [

    ("Bondowoso",
     -7.9136,
     113.8215),

    ("Palu",
     -0.8917,
     119.8707),

    ("Laut Flores",
     -7.5,
     120.8),

    ("Sorong",
     -0.876,
     131.255)

]

for nama, lat, lon in TESTS:

    print()
    print("=" * 60)

    print(nama)

    hasil = locate(lat, lon)

    print("Province :", hasil["province"])
    print("Sea      :", hasil["sea"])