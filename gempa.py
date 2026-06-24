import requests
import os
import time
import json
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://bmkg-content-inatews.storage.googleapis.com/lastQL.json"

last_data = None

last_event_key = None

last_daily_report = None

LAST_ID_FILE = "last_id.txt"

FB_POST_ID_FILE = "facebook_post_id.txt"
FB_POST_TEXT_FILE = "facebook_post_text.txt"

geo_cache = {}


# =====================================
# LAST ID CACHE
# =====================================

def load_last_id():

    try:

        with open(
            LAST_ID_FILE,
            "r"
        ) as f:

            return f.read().strip()

    except:

        return None


def save_last_id(gempa_id):

    try:

        with open(
            LAST_ID_FILE,
            "w"
        ) as f:

            f.write(gempa_id)

    except Exception as e:

        print(
            "SAVE ID ERROR:",
            e
        )


# =====================================
# FACEBOOK POST CACHE
# =====================================

def load_fb_post_id():

    try:

        with open(
            FB_POST_ID_FILE,
            "r"
        ) as f:

            data = f.read().strip()

            if data == "none":
                return None

            return data

    except:

        return None


def save_fb_post_id(post_id):

    try:

        with open(
            FB_POST_ID_FILE,
            "w"
        ) as f:

            f.write(post_id)

    except Exception as e:

        print(
            "SAVE FB POST ID ERROR:",
            e
        )


def load_fb_post_text():

    try:

        with open(
            FB_POST_TEXT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = f.read()

            if data.strip() == "none":
                return ""

            return data

    except:

        return ""


def save_fb_post_text(text):

    try:

        with open(
            FB_POST_TEXT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(text)

    except Exception as e:

        print(
            "SAVE FB TEXT ERROR:",
            e
        )


# =====================================
# DAILY STATS
# =====================================

def load_daily_stats():

    try:

        with open(
            "daily_stats.json",
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {}


def save_daily_stats(data):

    with open(
        "daily_stats.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def get_provinsi_only(lokasi_text):

    if not lokasi_text:
        return "Tidak Diketahui"

    baris = [
        x.strip()
        for x in lokasi_text.split("\n")
        if x.strip()
    ]

    if len(baris) == 0:
        return "Tidak Diketahui"

    return baris[-1]


def update_daily_stats(provinsi):

    hari = datetime.now().strftime(
        "%Y-%m-%d"
    )

    data = load_daily_stats()

    if hari not in data:

        data[hari] = {}

    if provinsi not in data[hari]:

        data[hari][provinsi] = 0

    data[hari][provinsi] += 1

    save_daily_stats(data)

    print(
        "STAT HARIAN:",
        provinsi,
        "=",
        data[hari][provinsi]
    )

    print(
        "TOTAL PROVINSI HARI INI:",
        len(data[hari])
    )

def build_daily_report():

    hari = datetime.now().strftime(
        "%Y-%m-%d"
    )

    data = load_daily_stats()

    if hari not in data:

        return None

    statistik = data[hari]

    total = sum(
        statistik.values()
    )

    ranking = sorted(
        statistik.items(),
        key=lambda x: x[1],
        reverse=True
    )

    teks = (
        "📊 REKAP GEMPA HARIAN\n\n"
        f"{hari}\n\n"
        f"🌍 Total Gempa: {total}\n\n"
    )

    medal = [
        "🥇",
        "🥈",
        "🥉"
    ]

    for i, item in enumerate(
        ranking[:10]
    ):

        provinsi = item[0]
        jumlah = item[1]

        icon = (
            medal[i]
            if i < 3
            else "•"
        )

        teks += (
            f"{icon} "
            f"{provinsi}: "
            f"{jumlah}\n"
        )

    teks += (
        "\n━━━━━━━━━━━━━━\n"
        "🛰 Sumber: InaTEWS BMKG"
    )

    return teks

def test_daily_report():

    report = build_daily_report()

    if report:

        send_message(
            report
        )

        print(
            "TEST REKAP TERKIRIM"
        )


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
# FACEBOOK
# =====================================

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

def post_facebook(message, image_url=None):

    try:

        if not FB_PAGE_ID or not FB_PAGE_TOKEN:
            return

        use_photo = False

        if image_url:

            try:

                cek = requests.head(
                    image_url,
                    timeout=10
                )

                if cek.status_code < 400:
                    use_photo = True

            except:
                pass

        if use_photo:

            url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/photos"

            payload = {
                "url": image_url,
                "caption": message,
                "access_token": FB_PAGE_TOKEN
            }

        else:

            url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/feed"

            payload = {
                "message": message,
                "access_token": FB_PAGE_TOKEN
            }

        r = requests.post(
            url,
            data=payload,
            timeout=30
        )

        print(
            "FACEBOOK:",
            r.status_code
        )

        print(
            "FACEBOOK RESPONSE:",
            r.text
        )

        if r.status_code == 200:

            try:

                data_fb = r.json()

                if "id" in data_fb:

                    save_fb_post_id(
                        data_fb["id"]
                    )

                    save_fb_post_text(
                        message
                    )

                    print(
                        "FB POST ID DISIMPAN:",
                        data_fb["id"]
                    )

            except Exception as e:

                print(
                    "SAVE FB CACHE ERROR:",
                    e
                )

    except Exception as e:

        print(
            "FACEBOOK ERROR:",
            e
        )

def edit_facebook_post(post_id, message):

    try:

        if not post_id:
            return

        url = (
            f"https://graph.facebook.com/v25.0/"
            f"{post_id}"
        )

        payload = {
            "message": message,
            "access_token": FB_PAGE_TOKEN
        }

        r = requests.post(
            url,
            data=payload,
            timeout=30
        )

        print(
            "FACEBOOK EDIT:",
            r.status_code
        )

        print(
            "FACEBOOK EDIT RESPONSE:",
            r.text
        )

        if r.status_code == 200:

            pass

    except Exception as e:

        print(
            "FACEBOOK EDIT ERROR:",
            e
        )


# ==========================
# SHAKEMAP
# ==========================

def get_shakemap_url(gempa_id):

    return (
        "https://bmkg-content-inatews.storage.googleapis.com/"
        f"mt.{gempa_id}.png"
    )


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


print("Bot Gempa V11 berjalan...")

cached_id = load_last_id()

print(
    "LAST ID CACHE:",
    cached_id
)


# =====================================
# LOOP
# =====================================

while True:

    try:

        now = datetime.now()

        jam = now.strftime("%H:%M")

        hari = now.strftime(
        "%Y-%m-%d"
        )

        if jam == "23:21":
        
            if last_daily_report != hari:
        
                test_daily_report()
        
                last_daily_report = hari

        data = requests.get(
            URL,
            timeout=30

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

        event_key = current["id"]

        print(
            "EVENT:",
            event_key,
            "| LAST:",
            last_event_key
        )
        
        if last_data is None:

            if cached_id:

                print(
                    "CACHE FOUND:",
                    cached_id
                )

            else:

                save_last_id(
                    current["id"]
                )

                cached_id = current["id"]

                print(
                    "CACHE INIT:",
                    current["id"]
                )

            last_data = current
            last_event_key = event_key

            print("Data awal dimuat")

        else:

            # =================================
            # GEMPA BARU
            # =================================

            if current["id"] != cached_id:

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

                provinsi = get_provinsi_only(
                    lokasi_pro
                )

                print(
                    "PROVINSI:",
                    provinsi
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

                update_daily_stats(
                    provinsi
                )

                report = build_daily_report()

                if report:
                
                    print(
                        "\n===== REKAP HARIAN =====\n"
                    )
                
                    print(report)
                
                    print(
                        "\n========================\n"
                    )
                
                send_photo(
                    photo_url,
                    caption
                )

                post_facebook(
                    caption,
                    get_shakemap_url(current["id"])
                )

                print("GEMPA BARU DIKIRIM")

                save_last_id(current["id"])
                cached_id = current["id"]

                print(
                    "CACHE DISIMPAN:",
                    current["id"]
                )

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

                    fb_post_id = load_fb_post_id()
                
                    old_text = load_fb_post_text()
                
                    update_number = (
                        old_text.count("🔄 UPDATE #")
                        + 1
                    )

                    new_text = (
                        old_text
                        + "\n\n━━━━━━━━━━━━━━\n\n"
                        + f"🔄 UPDATE #{update_number}\n\n"
                        + pesan
                    )

                    print(
                        "FB TEXT LENGTH:",
                        len(new_text)
                    )
                    
                    edit_facebook_post(
                        fb_post_id,
                        new_text
                    )

                    save_fb_post_text(
                        new_text
                    )
                    
                    print("UPDATE PARAMETER")


            last_data = current
            last_event_key = event_key
    
    except Exception as e:

        print("ERROR:", e)

    time.sleep(10)
