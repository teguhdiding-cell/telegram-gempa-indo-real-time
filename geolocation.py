from geopy.geocoders import Nominatim

geolocator = Nominatim(
    user_agent="gempa-realtime-v15"
)

def format_koordinat(lat, lon):

    if lat < 0:
        lat_txt = f"{abs(lat):.4f} LS"
    else:
        lat_txt = f"{lat:.4f} LU"

    if lon < 0:
        lon_txt = f"{abs(lon):.4f} BB"
    else:
        lon_txt = f"{lon:.4f} BT"

    return lat_txt, lon_txt
