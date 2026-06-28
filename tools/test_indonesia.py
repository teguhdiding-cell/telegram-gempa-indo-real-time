from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.sea_locator import find_sea

tests = [

    # Laut
    (-6.5,110.5,"Java Sea"),
    (-3.0,125.0,"Banda Sea"),
    (-9.5,118.0,"Indian Ocean"),
    (-3.8,135.5,"Arafura Sea"),
    (-2.5,121.5,"Gulf of Tomini"),

]

print("="*70)
print("VALIDASI POLYGON INDONESIA")
print("="*70)

pass_test = 0
fail_test = 0

for lat,lon,expected in tests:

    hasil = find_sea(lat,lon)

    status = "PASS" if hasil == expected else "FAIL"

    print(
        f"{status:5} | "
        f"Expected : {expected:20} | "
        f"Hasil : {str(hasil):20}"
    )

    if status=="PASS":
        pass_test +=1
    else:
        fail_test +=1

print()
print("="*70)
print("PASS :",pass_test)
print("FAIL :",fail_test)