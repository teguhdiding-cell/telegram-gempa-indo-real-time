from pathlib import Path
import sys
import requests

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from core.geolocation import lokasi_perairan

URL = "https://bmkg-content-inatews.storage.googleapis.com/lastQL.json"

print("=" * 70)
print("VALIDASI GEMPA TERBARU (InaTEWS)")
print("=" * 70)

data = requests.get(URL, timeout=30).json()

gempa = data["features"][0]

p = gempa["properties"]
g = gempa["geometry"]

lat = float(g["coordinates"][1])
lon = float(g["coordinates"][0])

hasil = lokasi_perairan(lat, lon)

print()
print("ID          :", p["id"])
print("Magnitudo   :", p["mag"])
print("Kedalaman   :", p["depth"], "Km")
print("Koordinat   :", lat, ",", lon)
print("Place BMKG  :", p["place"])
print()
print("Engine Laut :", hasil)

print()
print("=" * 70)