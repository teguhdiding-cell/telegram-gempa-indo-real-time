import requests
import os
import time
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://bmkg-content-inatews.storage.googleapis.com/lastQL.json"

last_data = None


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
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "photo": photo_url,
                "caption": caption
            },
            timeout=30
        )

        if not r.ok:
            send_message(caption)

    except Exception:
        send_message(caption)


def format_wib(time_string):
    try:
        utc_time = datetime.strptime(
            time_string.split(".")[0],
            "%Y-%m-%d %H:%M:%S"
        )

        wib_time = utc_time + timedelta(hours=7)

        bulan = {
            1: "Januari",
            2: "Februari",
            3: "Maret",
            4: "April",
            5: "Mei",
            6: "Juni",
            7: "Juli",
            8: "Agustus",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember"
        }

        return (
            f"{wib_time.day} "
            f"{bulan[wib_time.month]} "
            f"{wib_time.year}\n"
            f"{wib_time.strftime('%H:%M:%S')} WIB"
        )

    except:
        return time_string


def status_magnitudo(mag):

    if mag < 3:
        return "🟢 Minor"

    elif mag < 5:
        return "🟡 Ringan"

    elif mag < 6:
        return "🟠 Sedang"

    elif mag < 7:
        return "🔴 Kuat"

    return "⚫ Besar"


print("Bot Gempa Profesional V4 berjalan...")


while True:

    try:

        data = requests.get(URL, timeout=30).json()

        gempa = data["features"][0]

        p = gempa["properties"]
        g = gempa["geometry"]

        current = {
            "id": p["id"],
            "mag": float(p["mag"]),
            "fase": str(p["fase"]),
            "depth": float(p["depth"]),
            "place": p["place"],
            "time": format_wib(p["time"]),
            "lat": float(g["coordinates"][1]),
            "lon": float(g["coordinates"][0])
        }

        if last_data is None:

            last_data = current

            print("Data awal dimuat")

        else:

            # GEMPA BARU
            if current["id"] != last_data["id"]:

                lat = round(current["lat"], 4)
                lon = round(current["lon"], 4)

                maps = (
                    f"https://maps.google.com/?q="
                    f"{lat},{lon}"
                )

                photo_url = (
                    "https://bmkg-content-inatews.storage.googleapis.com/"
                    f"mt.{current['id']}.png"
                )

                caption = (
                    "🚨 GEMPA REALTIME InaTEWS\n\n"

                    f"📍 Lokasi\n"
                    f"{current['place']}\n\n"

                    f"📏 Magnitudo\n"
                    f"M {current['mag']:.1f}\n"
                    f"{status_magnitudo(current['mag'])}\n\n"

                    f"📌 Kedalaman\n"
                    f"{current['depth']:.1f} Km\n\n"

                    f"⚡ Fase Analisis\n"
                    f"{current['fase']}\n\n"

                    f"🌐 Koordinat\n"
                    f"{lat}, {lon}\n\n"

                    f"🗺 Google Maps\n"
                    f"{maps}\n\n"

                    f"🕒 Waktu Kejadian\n"
                    f"{current['time']}\n\n"

                    "━━━━━━━━━━━━━━\n"
                    "📡 Sumber: InaTEWS BMKG\n"
                    "#GempaRealtime"
                )

                send_photo(photo_url, caption)

                print("GEMPA BARU DIKIRIM")

            else:

                perubahan = []

                # filter perubahan penting saja

                if abs(current["mag"] - last_data["mag"]) >= 0.1:
                    perubahan.append(
                        f"📏 Magnitudo\n"
                        f"{last_data['mag']:.2f} → {current['mag']:.2f}"
                    )

                if abs(current["depth"] - last_data["depth"]) >= 1:
                    perubahan.append(
                        f"📌 Kedalaman\n"
                        f"{last_data['depth']:.1f} Km → "
                        f"{current['depth']:.1f} Km"
                    )

                if current["fase"] != last_data["fase"]:
                    perubahan.append(
                        f"⚡ Fase Analisis\n"
                        f"{last_data['fase']} → {current['fase']}"
                    )

                lat_changed = (
                    abs(current["lat"] - last_data["lat"])
                    >= 0.01
                )

                lon_changed = (
                    abs(current["lon"] - last_data["lon"])
                    >= 0.01
                )

                if lat_changed or lon_changed:
                    perubahan.append(
                        "🌐 Lokasi episenter diperbarui"
                    )

                if perubahan:

                    pesan = (
                        "🔄 UPDATE PARAMETER GEMPA\n\n"
                        + "\n\n".join(perubahan)
                        + "\n\n━━━━━━━━━━━━━━\n"
                        + "📡 Sumber: InaTEWS BMKG"
                    )

                    send_message(pesan)

                    print("UPDATE PARAMETER")

            last_data = current

    except Exception as e:

        print("ERROR:", e)

    time.sleep(5)
