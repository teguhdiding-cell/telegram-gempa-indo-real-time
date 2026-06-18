import requests
import os
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://bmkg-content-inatews.storage.googleapis.com/lastQL.json"

last_data = None


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )


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
            "lat": g["coordinates"][1],
            "lon": g["coordinates"][0],
            "place": p["place"],
            "time": p["time"]
        }

        if last_data is None:
            last_data = current
            print("Data awal dimuat")

        else:

            # GEMPA BARU
            if current["id"] != last_data["id"]:

                pesan = f"""🚨 GEMPA BARU InaTEWS

🆔 {current['id']}

📍 {current['place']}

📏 M {round(float(current['mag']),1)}

📌 Kedalaman {round(float(current['depth']),1)} Km

⚡ Fase {current['fase']}

🕒 {current['time']}

#GempaRealtime
"""

                send_message(pesan)

                print("GEMPA BARU DIKIRIM")

            # UPDATE PARAMETER
            else:

                perubahan = []

                if current["mag"] != last_data["mag"]:
                    perubahan.append(
                        f"Magnitudo: {last_data['mag']} → {current['mag']}"
                    )

                if current["fase"] != last_data["fase"]:
                    perubahan.append(
                        f"Fase: {last_data['fase']} → {current['fase']}"
                    )

                if current["depth"] != last_data["depth"]:
                    perubahan.append(
                        f"Kedalaman: {last_data['depth']} → {current['depth']}"
                    )

                if (
                    current["lat"] != last_data["lat"]
                    or
                    current["lon"] != last_data["lon"]
                ):
                    perubahan.append(
                        "Koordinat diperbarui"
                    )

                if perubahan:

                    pesan = (
                        f"🔄 UPDATE PARAMETER\n\n"
                        f"ID: {current['id']}\n\n"
                        + "\n".join(perubahan)
                    )

                    send_message(pesan)

                    print("UPDATE PARAMETER")

            last_data = current

    except Exception as e:
        print("ERROR:", e)

    time.sleep(5)
