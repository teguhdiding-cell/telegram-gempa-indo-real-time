from pathlib import Path
import json

ROOT = Path(__file__).parent.parent

FILE = ROOT / "data" / "province" / "indonesia_provinces.geojson"

print("=" * 60)
print("INSPECT PROVINCE DATASET")
print("=" * 60)

with open(FILE, encoding="utf-8") as f:
    geojson = json.load(f)

print()

print("Type :", geojson["type"])
print("Jumlah Feature :", len(geojson["features"]))

print()

feature = geojson["features"][0]

print("Geometry :", feature["geometry"]["type"])

print()

print("Properties")

for key, value in feature["properties"].items():
    print(f"{key} : {value}")