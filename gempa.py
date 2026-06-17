import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


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


def save_last_id(gempa_id):
    with open("last_id.txt", "w") as f:
        f.write(gempa_id)


try:

    url = "https://bmkg-content-inatews.storage.googleapis.com/datagempa.json"

    data = requests.get(url, timeout=30).json()

    gempa = data["features"][0]

    prop = gempa["properties"]

    gempa_id = prop["id"]

    last_id = read_last_id()

    if gempa_id != last_id:

        mag = prop["mag"]
        lokasi = prop["place"]
        kedalaman = prop["depth"]
        waktu = prop["time"]
        status = prop["status"]

        pesan = f"""
🚨 GEMPA REALTIME InaTEWS

📍 Lokasi
{lokasi}

📏 Magnitudo
M {mag}

📌 Kedalaman
{kedalaman} km

🕒 Waktu
{waktu}

📡 Status
{status}

━━━━━━━━━━━━━━
⚠ Data awal InaTEWS BMKG

Parameter dapat berubah
"""

        send_message(pesan)

        save_last_id(gempa_id)

        print("GEMPA BARU DIKIRIM")

    else:
        print("TIDAK ADA GEMPA BARU")

except Exception as e:
    print("ERROR:", e)
