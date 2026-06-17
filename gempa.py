import requests
import os
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://bmkg-content-inatews.storage.googleapis.com/datagempa.json"

last_time = ""

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

        info = data["info"]

        gempa_id = f"{info['date']}_{info['time']}"

        if gempa_id != last_time:

            pesan = f"""🚨 GEMPA REALTIME InaTEWS

📍 Lokasi
{info['area']}

📏 Magnitudo
M {info['magnitude']}

📌 Kedalaman
{info['depth']}

🕒 Waktu
{info['date']} | {info['time']}

📢 Dirasakan
{info.get('felt', '-')}

⚠ Potensi
{info.get('potential', '-')}

━━━━━━━━━━━━━━
Sumber: InaTEWS BMKG
#GempaRealtime
"""

            send_message(pesan)

            print("GEMPA BARU DIKIRIM")

            last_time = gempa_id

        else:
            print("Tidak ada gempa baru")

    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)
