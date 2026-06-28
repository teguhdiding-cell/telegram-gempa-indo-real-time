from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from geopy.geocoders import Nominatim
from core.geolocation import lokasi_perairan

geolocator = Nominatim(user_agent="gempa-validator")

lat = -1.8500
lon = 122.7500

print("=" * 60)
print("KASUS NO 13")
print("=" * 60)

print("Latitude :", lat)
print("Longitude:", lon)
print()

try:
    location = geolocator.reverse(
        (lat, lon),
        language="id",
        zoom=10
    )

    print("HASIL NOMINATIM")
    print(location.address)
    print()

except Exception as e:
    print("Gagal Reverse Geocoding:", e)

print("HASIL POLYGON")
print(lokasi_perairan(lat, lon))