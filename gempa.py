import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://bmkg-content-inatews.storage.googleapis.com/datagempa.json"


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )


try:

    data = requests.get(URL, timeout=30).json()

    info = data["info"]

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

    print("PESAN TERKIRIM")

except Exception as e:
    print("ERROR:", e)
