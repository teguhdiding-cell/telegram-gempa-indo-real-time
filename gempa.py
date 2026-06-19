import requests
import os
import time
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://bmkg-content-inatews.storage.googleapis.com/lastQL.json"

last_data = None

last_event_key = None

geo_cache = {}


# =====================================
# TELEGRAM
# =====================================

def send_message(text):
    try:

        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "disable_web_page_preview": True
            },
            timeout=30
        )

        print(
            "TELEGRAM MESSAGE:",
            r.status_code
        )

    except Exception as e:
        print("SEND MESSAGE ERROR:", e)


def send_photo(photo_url, caption):

    try:

        cek = requests.head(
            photo_url,
            timeout=10
        )

        if cek.status_code == 200:

            r = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "photo": photo_url,
                    "caption": caption
                },
                timeout=30
            )

            print(
                "TELEGRAM PHOTO:",
                r.status_code
            )

        else:

            send_message(caption)

    except Exception as e:

        print("SEND PHOTO ERROR:", e)

        send_message(caption)


# =====================================
# WIB
# =====================================

def waktu_wib(time_str):

    try:

        dt = datetime.fromisoformat(
            time_str.replace(" ", "T")
        )

        dt += timedelta(hours=7)

        bulan = [
            "Januari","Februari","Maret",
            "April","Mei","Juni",
            "Juli","Agustus","September",
            "Oktober","November","Desember"
        ]

        return (
            f"{dt.day} "
            f"{bulan[dt.month-1]} "
            f"{dt.year}\n"
            f"{dt.strftime('%H:%M:%S')} WIB"
        )

    except:

        return time_str


# =====================================
# KATEGORI MAGNITUDO
# =====================================

def kategori_mag(mag):

    mag = float(mag)

    if mag < 2:
        return "⚪ Mikro"

    elif mag < 4:
        return "🟢 Minor"

    elif mag < 5:
        return "🟡 Ringan"

    elif mag < 6:
        return "🟠 Sedang"

    elif mag < 7:
        return "🔴 Kuat"

    elif mag < 8:
        return "🟣 Mayor"

    return "⚫ Great Earthquake"


# =====================================
# KEDALAMAN
# =====================================

def kategori_depth(depth):

    depth = float(depth)

    if depth < 70:
        return "🔹 Gempa Dangkal"

    elif depth < 300:
        return "🔷 Gempa Menengah"

    return "🔶 Gempa Dalam"


# =====================================
# ENERGI
# =====================================

def energi_tnt(mag):

    mag = float(mag)

    joule = 10 ** (1.5 * mag + 4.8)

    tnt = joule / 4.184e9

    if tnt < 1:

        return f"≈ {tnt*1000:.0f} kg TNT"

    elif tnt < 1000:

        return f"≈ {tnt:.1f} ton TNT"

    else:

        return f"≈ {tnt/1000:.1f} kiloton TNT"


# =====================================
# KOORDINAT
# =====================================

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
# GEOLOKASI V9
# =====================================

geolocator = Nominatim(
    user_agent="gempa-realtime-v9"
)

def lokasi_detail(lat, lon):

    key = (
        round(lat, 2),
        round(lon, 2)
    )

    if key in geo_cache:
        return geo_cache[key]
        
    try:

        lokasi = geolocator.reverse(
            f"{lat},{lon}",
            language="id",
            timeout=10
        )

        if not lokasi:
            return "Indonesia"

        alamat = lokasi.raw["address"]

        kabupaten = (
            alamat.get("county")
            or alamat.get("city")
            or alamat.get("municipality")
            or alamat.get("state_district")
            or ""
        )

        provinsi = alamat.get("state", "")

        hasil = []

        if kabupaten:
            hasil.append(kabupaten)

        if provinsi:
            hasil.append(provinsi)

        if hasil:
            hasil_text = "\n".join(hasil)
            geo_cache[key] = hasil_text
            return hasil_text

        return lokasi.address

    except Exception as e:

        print("GEO ERROR:", e)

        return "Indonesia"


print("Bot Gempa V9 berjalan...")


# =====================================
# LOOP
# =====================================

while True:

    try:

        data = requests.get(URL, timeout=30).json()

        gempa = data["features"][0]

        p = gempa["properties"]
        g = gempa["geometry"]

        current = {

            "id": p["id"],
            "mag": p["mag"],
            "fase": p["fase"],
            "depth": p["depth"],
            "place": p["place"],
            "time": p["time"],

            "lat": float(g["coordinates"][1]),
            "lon": float(g["coordinates"][0])

        }

        event_key = current["time"]
        
        if last_data is None:

            last_data = current
            last_event_key = event_key

            print("Data awal dimuat")

        else:

            # =================================
            # GEMPA BARU
            # =================================

            if event_key != last_event_key:

                print(
                    "ID BARU:",
                    last_data["id"],
                    "->",
                    current["id"]
                )
                
                lat_txt, lon_txt = format_koordinat(
                    current["lat"],
                    current["lon"]
                )

                maps = (
                    f"https://maps.google.com/?q="
                    f"{current['lat']},{current['lon']}"
                )

                photo_url = (
                    "https://bmkg-content-inatews.storage.googleapis.com/"
                    f"mt.{current['id']}.png"
                )

                lokasi_pro = lokasi_detail(
                    current["lat"],
                    current["lon"]
                )

                caption = f"""
🚨 GEMPA REALTIME InaTEWS

📍 Lokasi
{lokasi_pro}

📏 Magnitudo
M {round(float(current['mag']),1)}

{kategori_mag(current['mag'])}

📌 Kedalaman
{round(float(current['depth']),1)} Km

{kategori_depth(current['depth'])}

⚡ Energi Relatif
{energi_tnt(current['mag'])}

⚡ Status Analisis
Fase ke-{current['fase']}

🌐 Koordinat

{lat_txt}
{lon_txt}

🗺 Lihat Lokasi
{maps}

🕒 Waktu Kejadian
{waktu_wib(current['time'])}

━━━━━━━━━━━━━━
🛰 Sumber: InaTEWS BMKG
#GEMPAdanCUACA
"""

                send_message(caption)

                print("GEMPA BARU DIKIRIM")

                if float(current["mag"]) >= 5.0:

                    send_message(
f"""
🚨 GEMPA KUAT

Magnitudo M{round(float(current['mag']),1)}

📍 {lokasi_pro}

⚠ Periksa informasi resmi BMKG untuk pembaruan selanjutnya.

#GempaKuat
"""
                    )

            # =================================
            # UPDATE PARAMETER
            # =================================

            else:

                perubahan = []

                if abs(
                    float(current["mag"])
                    -
                    float(last_data["mag"])
                ) >= 0.1:

                    perubahan.append(
                        f"📏 Magnitudo\n"
                        f"M{round(float(last_data['mag']),1)} → "
                        f"M{round(float(current['mag']),1)}"
                    )

                if abs(
                    float(current["depth"])
                    -
                    float(last_data["depth"])
                ) >= 1:

                    perubahan.append(
                        f"📌 Kedalaman\n"
                        f"{round(float(last_data['depth']),1)} Km → "
                        f"{round(float(current['depth']),1)} Km"
                    )

                koordinat_berubah = (

                    abs(current["lat"] - last_data["lat"]) >= 0.001

                    or

                    abs(current["lon"] - last_data["lon"]) >= 0.001

                )

                if koordinat_berubah:

                    lokasi_baru = lokasi_detail(
                        current["lat"],
                        current["lon"]
                    )

                    perubahan.append(
                        f"🌐 Lokasi Episenter\n"
                        f"{lokasi_baru}\n\n"
                        f"{current['lat']:.4f}, {current['lon']:.4f}"
                    )

                if perubahan:

                    maps = (
                        f"https://maps.google.com/?q="
                        f"{current['lat']},{current['lon']}"
                    )

                    pesan = (
                        "🔄 UPDATE PARAMETER GEMPA\n\n"
                        + "\n\n".join(perubahan)
                        + "\n\n🗺 Google Maps"
                        + f"\n{maps}"
                        + "\n\n🕒 Waktu Analisis"
                        + f"\n{waktu_wib(current['time'])}"
                        + "\n\n━━━━━━━━━━━━━━"
                        + "\n🛰 Sumber: InaTEWS BMKG"
                    )

                    send_message(pesan)

                    print("UPDATE PARAMETER")


            last_data = current
            last_event_key = event_key

            print(
                "CACHE UPDATED:",
                current["id"]
            )
    
    except Exception as e:

        print("ERROR:", e)

    time.sleep(5)
