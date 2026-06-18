import requests
import os
import time

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
        print("ERROR SEND MESSAGE:", e)


def send_photo(photo_url, caption):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "photo": photo_url,
                "caption": caption
            },
            timeout=30
        )
    except Exception as e:
        print("ERROR SEND PHOTO:", e)


print("Bot berjalan...")

while True:

    try:

        data = requests.get(URL, timeout=30).json()

        gempa = data["features"][0]

        p = gempa["properties"]
        g = gempa["geometry"]

        current = {
            "id": p["id"],
            "mag": float(p["mag"]),
            "fase": p["fase"],
            "depth": float(p["depth"]),
            "place": p["place"],
            "time": p["time"],
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

                photo_url = (
                    f"https://bmkg-content-inatews.storage.googleapis.com/"
                    f"mt.{current['id']}.png"
                )

                maps = f"https://maps.google.com/?q={lat},{lon}"

                caption = (
                    f"🚨 GEMPA REALTIME InaTEWS\n\n"
                    f"🆔 ID\n{current['id']}\n\n"
                    f"📍 Lokasi\n{current['place']}\n\n"
                    f"📏 Magnitudo\nM {current['mag']:.1f}\n\n"
                    f"📌 Kedalaman\n{current['depth']:.1f} Km\n\n"
                    f"⚡ Fase\n{current['fase']}\n\n"
                    f"🌐 Koordinat\n{lat}, {lon}\n\n"
                    f"🗺 Google Maps\n{maps}\n\n"
                    f"🕒 Waktu\n{current['time']}\n\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"Sumber: InaTEWS BMKG\n"
                    f"#GempaRealtime"
                )

                send_photo(photo_url, caption)

                print("GEMPA BARU DIKIRIM")

            # UPDATE PARAMETER
            else:

                perubahan = []

                if current["mag"] != last_data["mag"]:
                    perubahan.append(
                        f"📏 Magnitudo: {last_data['mag']:.2f} → {current['mag']:.2f}"
                    )

                if current["fase"] != last_data["fase"]:
                    perubahan.append(
                        f"⚡ Fase: {last_data['fase']} → {current['fase']}"
                    )

                if current["depth"] != last_data["depth"]:
                    perubahan.append(
                        f"📌 Kedalaman: {last_data['depth']:.2f} → {current['depth']:.2f} Km"
                    )

                if (
                    current["lat"] != last_data["lat"]
                    or
                    current["lon"] != last_data["lon"]
                ):
                    perubahan.append(
                        f"🌐 Koordinat diperbarui"
                    )

                if perubahan:

                    pesan = (
                        f"🔄 UPDATE PARAMETER\n\n"
                        f"🆔 ID\n{current['id']}\n\n"
                        + "\n".join(perubahan)
                    )

                    send_message(pesan)

                    print("UPDATE PARAMETER")

            last_data = current

    except Exception as e:

        print("ERROR:", e)

    time.sleep(5)
