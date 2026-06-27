from geopy.geocoders import Nominatim
from sea_database import SEA_DATABASE

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


# =====================================
# DATABASE PERAIRAN INDONESIA V1
# =====================================

def lokasi_perairan(lat, lon):

    wilayah = SEA_DATABASE

    cocok = []

    for laut in wilayah:
    
        if (
            laut["lat_min"] <= lat <= laut["lat_max"]
            and
            laut["lon_min"] <= lon <= laut["lon_max"]
        ):
    
            luas = (
                (laut["lat_max"] - laut["lat_min"])
                *
                (laut["lon_max"] - laut["lon_min"])
            )
    
            cocok.append(
                (
                    luas,
                    laut["nama"]
                )
            )
    
    if cocok:
    
        cocok.sort(key=lambda x: x[0])
    
        return cocok[0][1]
    
    return "🌊 Perairan Indonesia"
