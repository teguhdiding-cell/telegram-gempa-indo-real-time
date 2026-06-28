import json
import pickle
from pathlib import Path

from shapely.geometry import shape
from shapely.prepared import prep

BASE = Path(__file__).parent.parent

DATA_FILE = BASE / "data" / "province" / "indonesia_provinces.geojson"

CACHE_DIR = BASE / "cache"
CACHE_FILE = CACHE_DIR / "province_cache.pkl"


def build_database():

    with open(DATA_FILE, encoding="utf-8") as f:
        geojson = json.load(f)

    database = []

    for feature in geojson["features"]:

        poly = shape(feature["geometry"])

        database.append({
            "name": feature["properties"]["PROVINSI"],
            "polygon": poly,
            "prepared": prep(poly),
            "bounds": poly.bounds
        })

    return database


def load_cache():

    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)

    database = []

    for item in cache:

        poly = item["polygon"]

        database.append({
            "name": item["name"],
            "polygon": poly,
            "prepared": prep(poly),
            "bounds": item["bounds"]
        })

    return database


def load_all():

    if CACHE_FILE.exists():

        print("[OK] Province Cache ditemukan")

        return load_cache()

    print("[INFO] Province Cache tidak ditemukan")

    return build_database()