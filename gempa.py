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


def read_last_id():
    if not os.path.exists("last_id.txt"):
        return ""

    with open("last_id.txt", "r") as f:
        return f.read().strip()


def save_last_id(event_id):
    with open("last_id.txt", "w") as f:
        f.write(event_id)


try:

    data = requests.get(URL, timeout=30).json()

    info = data["info"]

    event_id = info["eventid"]

    last_id = read_last_id()

    if event_id != last_id:

        pesan = f"""
🚨 GEMPA REALTIME InaTEWS

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

        save_last_id(event_id)

        print("GEMPA BARU DIKIRIM")

    else:
        print("TIDAK ADA GEMPA BARU")

except Exception as e:
    print("ERROR:", e)
