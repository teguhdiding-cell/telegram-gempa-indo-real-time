import requests
import os
import time
import json
import sqlite3
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from supabase import create_client

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =====================================
# SUPABASE GENERIC STATE
# =====================================

def load_state(key):

    try:

        response = (
            supabase
            .table("bot_state")
            .select("value")
            .eq("key", key)
            .execute()
        )

        if response.data:

            return response.data[0]["value"]

        return None

    except Exception as e:

        print(
            "SUPABASE LOAD STATE ERROR:",
            e
        )

        return None


def save_state(key, value):

    try:

        supabase.table("bot_state").upsert(
            {
                "key": key,
                "value": value
            }
        ).execute()

    except Exception as e:

        print(
            "SUPABASE SAVE STATE ERROR:",
            e
        )


# =====================================
# EARTHQUAKE LOG
# =====================================

def save_earthquake_log(data, kabupaten, provinsi):

    try:

        supabase.table("earthquake_log").upsert(
            {
                "id": data["id"],
                "waktu": data["time"],
                "magnitudo": float(data["mag"]),
                "kedalaman": float(data["depth"]),
                "fase": int(data["fase"]),
                "kabupaten": kabupaten,
                "provinsi": provinsi,
                "latitude": float(data["lat"]),
                "longitude": float(data["lon"])
            }
        ).execute()

        print(
            "EARTHQUAKE LOG SAVED:",
            data["id"]
        )

    except Exception as e:

        print(
            "EARTHQUAKE LOG ERROR:",
            e
        )
        
URL = "https://bmkg-content-inatews.storage.googleapis.com/lastQL.json"

last_data = None

last_event_key = None

last_daily_report = None

geo_cache = {}

DB_FILE = "gempa.db"


# =====================================
# WAKTU WIB
# =====================================

from datetime import datetime, timedelta, UTC

def now_wib():
    return datetime.now(UTC) + timedelta(hours=7)
    

# =====================================
# SQLITE
# =====================================

def init_db():

    conn = sqlite3.connect(DB_FILE)

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_stats (
        tanggal TEXT,
        provinsi TEXT,
        jumlah INTEGER,
        PRIMARY KEY (tanggal, provinsi)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_report_status (
        tanggal TEXT PRIMARY KEY,
        sent INTEGER DEFAULT 0
    )
    """)

    conn.commit()

    # BARU CEK
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )

    print("DATABASE:", DB_FILE)
    print("TABLE:", cur.fetchall())

    conn.close()

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


def update_daily_stats(kabupaten):

    hari = now_wib().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_FILE)

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO daily_stats
        (tanggal, provinsi, jumlah)

        VALUES (?, ?, 1)

        ON CONFLICT(tanggal, provinsi)

        DO UPDATE SET

        jumlah = jumlah + 1
        """,
        (
            hari,
            kabupaten
        )
    )

    conn.commit()

    cur.execute("""
    SELECT COUNT(*)
    FROM daily_stats
    """)

    print(
        "JUMLAH DATA DATABASE:",
        cur.fetchone()[0]
    )

    cur.execute(
        "SELECT * FROM daily_stats"
    )

    print(
        "ISI DATABASE:",
        cur.fetchall()
    )

    cur.execute(
        """
        SELECT jumlah
        FROM daily_stats
        WHERE tanggal=?
        AND provinsi=?
        """,
        (
            hari,
            kabupaten
        )
    )

    total = cur.fetchone()[0]

    conn.close()

    print(
        "STAT HARIAN:",
        kabupaten,
        "=",
        total
    )

def build_daily_report():

    hari = now_wib().strftime(
        "%Y-%m-%d"
    )

    conn = sqlite3.connect(DB_FILE)

    cur = conn.cursor()

    cur.execute("SELECT * FROM daily_stats")

    print(
        "SEMUA DATA:",
        cur.fetchall()
    )

    cur.execute(
        """
        SELECT provinsi, jumlah
        FROM daily_stats
        WHERE tanggal=?
        ORDER BY jumlah DESC
        """,
        (hari,)
    )

    ranking = cur.fetchall()

    conn.close()

    print("HASIL QUERY:", ranking)

    if not ranking:

        return None

    total = sum(
        row[1]
        for row in ranking
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

    for i, row in enumerate(
        ranking[:10]
    ):

        provinsi = row[0]
        jumlah = row[1]

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

    print("REKAP BERHASIL DIBUAT")

    return teks


# =====================================
# DAILY REPORT SUPABASE
# =====================================

def build_daily_report_supabase():

    try:

        hari = now_wib().strftime("%Y-%m-%d")

        response = (
            supabase
            .table("earthquake_log")
            .select("kabupaten")
            .gte("waktu", f"{hari}T00:00:00+07:00")
            .lt("waktu", f"{hari}T23:59:59+07:00")
            .execute()
        )

        data = response.data

        if not data:
            return None

        statistik = {}

        for row in data:

            kabupaten = row["kabupaten"] or "Tidak Diketahui"

            statistik[kabupaten] = (
                statistik.get(kabupaten, 0) + 1
            )

        ranking = sorted(
            statistik.items(),
            key=lambda x: x[1],
            reverse=True
        )

        total = len(data)

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

        for i, (kabupaten, jumlah) in enumerate(ranking[:10]):

            icon = medal[i] if i < 3 else "•"

            teks += (
                f"{icon} "
                f"{kabupaten}: "
                f"{jumlah}\n"
            )

        teks += (
            "\n━━━━━━━━━━━━━━\n"
            "🛰 Sumber: Database Gempa Indonesia"
        )

        return teks

    except Exception as e:

        print(
            "SUPABASE REPORT ERROR:",
            e
        )

        return None
        
def test_daily_report():

    report = build_daily_report_supabase()

    print(report)

    if report:

        send_message(report)

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

                    save_state("fb_post_id", data_fb["id"])
                    
                    save_state(
                        "fb_post_text",
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
# GEOLOKASI V12
# =====================================

geolocator = Nominatim(
    user_agent="gempa-realtime-v12"
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

            hasil = {
                "kabupaten": "Indonesia",
                "provinsi": "Tidak Diketahui",
                "display": "Indonesia"
            }

            geo_cache[key] = hasil

            return hasil

        alamat = lokasi.raw.get("address", {})

        print("=" * 60)
        print("RAW ADDRESS NOMINATIM")
        print(json.dumps(alamat, indent=2, ensure_ascii=False))
        print("=" * 60)

        kabupaten = (
            alamat.get("regency")
            or alamat.get("county")
            or alamat.get("city")
            or alamat.get("municipality")
            or alamat.get("state_district")
            or alamat.get("village")
            or alamat.get("town")
            or alamat.get("hamlet")
            or "Tidak Diketahui"
        )

        provinsi = (
            alamat.get("state")
            or "Tidak Diketahui"
        )

        # ==========================
        # FORMAT DISPLAY
        # ==========================

        if kabupaten != "Tidak Diketahui":

            display = kabupaten

            if provinsi != "Tidak Diketahui":
                display += "\n" + provinsi

        else:

            if provinsi != "Tidak Diketahui":

                kabupaten = f"Perairan {provinsi}"
                display = kabupaten

            else:

                kabupaten = "Indonesia"
                display = "Indonesia"

        hasil = {
            "kabupaten": kabupaten,
            "provinsi": provinsi,
            "display": display
        }

        geo_cache[key] = hasil

        return hasil

    except Exception as e:

        print(
            "GEO ERROR:",
            e
        )

        hasil = {
            "kabupaten": "Indonesia",
            "provinsi": "Tidak Diketahui",
            "display": "Indonesia"
        }

        return hasil


# =====================================
# TEST NOMINATIM
# =====================================

def test_nominatim(lat, lon):

    print("\n")
    print("=" * 70)
    print("TEST NOMINATIM")
    print(f"LAT : {lat}")
    print(f"LON : {lon}")
    print("=" * 70)

    try:

        lokasi = geolocator.reverse(
            f"{lat},{lon}",
            language="id",
            timeout=10
        )

        if lokasi is None:

            print("HASIL : TIDAK ADA")
            return

        print("\nRAW DATA")

        print(
            json.dumps(
                lokasi.raw,
                indent=4,
                ensure_ascii=False
            )
        )

        print("\nADDRESS")

        print(
            json.dumps(
                lokasi.raw.get("address", {}),
                indent=4,
                ensure_ascii=False
            )
        )

    except Exception as e:

        print("ERROR :", e)

    print("=" * 70)
    print("\n")
    

init_db()

try:

    result = (
        supabase
        .table("bot_state")
        .select("*")
        .limit(1)
        .execute()
    )

    print("SUPABASE CONNECTED")

except Exception as e:

    print("SUPABASE ERROR:", e)

print("Bot Gempa V11 berjalan...")

cached_id = load_state("last_id")

print(
    "LAST ID CACHE:",
    cached_id
)

# =====================================
# TEST KOORDINAT
# =====================================

test_nominatim(-8.7528, 117.2396)


# =====================================
# LOOP
# =====================================

while True:

    try:

        now = now_wib()

        jam = now.strftime("%H:%M")

        print(
            "JAM PYTHON:",
            jam
        )

        hari = now.strftime(
        "%Y-%m-%d"
        )

        data = requests.get(
            URL,
            timeout=30
        ).json()

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

                save_state(
                    "last_id",
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

                lokasi = lokasi_detail(
                    current["lat"],
                    current["lon"]
                )
                
                lokasi_pro = lokasi["display"]
                
                kabupaten = lokasi["kabupaten"]
                
                provinsi = lokasi["provinsi"]
                
                print(
                    "KABUPATEN:",
                    kabupaten
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
                    kabupaten
                )
                
                save_earthquake_log(
                    current,
                    kabupaten,
                    provinsi
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

                save_state(
                    "last_id",
                    current["id"]
                )
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
                    )["display"]

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

                    fb_post_id = load_state("fb_post_id")
                
                    old_text = load_state("fb_post_text")

                    if old_text is None:
                        old_text = ""
                
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

                    save_state(
                        "fb_post_text",
                        new_text
                    )
                    
                    print("UPDATE PARAMETER")


            last_data = current
            last_event_key = event_key

            # ==========================
            # REKAP HARIAN
            # ==========================
            
            if jam == "19:33":
            
                if last_daily_report != hari:
            
                    print("JAM COCOK")
            
                    test_daily_report()
            
                    last_daily_report = hari
    
    except Exception as e:

        print("ERROR:", e)

    time.sleep(10)
