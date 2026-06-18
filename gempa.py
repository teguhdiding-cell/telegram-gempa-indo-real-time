import requests
import os
import time
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://bmkg-content-inatews.storage.googleapis.com/lastQL.json"

last_data = None


# =====================================
# TELEGRAM
# =====================================

def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "disable_web_page_preview": True
            },
            timeout=30
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

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "photo": photo_url,
                    "caption": caption
                },
                timeout=30
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


print("Bot Gempa V7 berjalan...")


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

        if last_data is None:

            last_data = current

            print("Data awal dimuat")

        else:

            # =================================
            # GEMPA BARU
            # =================================

            if current["id"] != last_data["id"]:

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

                caption = f"""
🚨 GEMPA REALTIME InaTEWS

📍 Lokasi
{current['place']}

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
#GempaRealtime
"""

                send_photo(photo_url, caption)

                print("GEMPA BARU DIKIRIM")

                if float(current["mag"]) >= 6.0:

                    send_message(
f"""
🚨 GEMPA KUAT

Magnitudo M{round(float(current['mag']),1)}

📍 {current['place']}

⚠ Periksa informasi resmi BMKG untuk pembaruan selanjutnya.

#GempaKuat
"""
                    )

            # =================================
            # UPDATE PARAMETER
            # =================================

            else:

                perubahan = []

                if current["mag"] != last_data["mag"]:

                    perubahan.append(
                        f"📏 Magnitudo\n"
                        f"{last_data['mag']} → {current['mag']}"
                    )

                if current["depth"] != last_data["depth"]:

                    perubahan.append(
                        f"📌 Kedalaman\n"
                        f"{last_data['depth']} Km → "
                        f"{current['depth']} Km"
                    )

                koordinat_berubah = (

                    abs(current["lat"] - last_data["lat"]) >= 0.01

                    or

                    abs(current["lon"] - last_data["lon"]) >= 0.01

                )

                if koordinat_berubah:

                    perubahan.append(
                        "🌐 Lokasi episenter diperbarui"
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

    except Exception as e:

        print("ERROR:", e)

    time.sleep(5)
