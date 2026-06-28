import shapefile
from pathlib import Path

FILE = (
    Path(__file__).parent.parent
    / "data"
    / "raw"
    / "iho_v3"
    / "World_Seas_IHO_v3"
    / "World_Seas_IHO_v3.shp"
)

sf = shapefile.Reader(str(FILE))

print("=" * 60)
print("JUMLAH POLYGON :", len(sf))
print("=" * 60)

print("\nFIELD DATA")
print("=" * 60)

for field in sf.fields:
    print(field)

    print()
print("=" * 60)
print("DAFTAR NAMA LAUT")
print("=" * 60)

for record in sf.records():
    print(record["NAME"])