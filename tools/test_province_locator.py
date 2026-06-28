from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.province_locator import find_province

print("=" * 60)
print("TEST PROVINCE LOCATOR")
print("=" * 60)

TESTS = [

    ("Bondowoso",
     -7.9136,
     113.8215),

    ("Yogyakarta",
     -7.8014,
     110.3647),

    ("Palu",
     -0.8917,
     119.8707),

    ("Jayapura",
     -2.5916,
     140.6689),

    ("Sorong",
     -0.876,
     131.255)

]

for nama, lat, lon in TESTS:

    print()

    print("=" * 60)

    print(nama)

    print("-" * 60)

    print("HASIL :", find_province(lat, lon))