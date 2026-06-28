import json
import pickle
from pathlib import Path

from shapely.geometry import shape
from shapely.prepared import prep

BASE = Path(__file__).parent.parent

DATA = BASE / "data"

CACHE_DIR = BASE / "cache"
CACHE_FILE = CACHE_DIR / "polygon_cache.pkl"


def load_category(category):

    folder = DATA / category

    polygons = []

    for file in folder.glob("*.geojson"):

        if file.name == "index.json":
            continue

        with open(file, encoding="utf-8") as f:
            geojson = json.load(f)

        poly = shape(geojson["geometry"])

        polygons.append({
            "name": geojson["properties"]["name"],
            "polygon": poly,
            "prepared": prep(poly),
            "bounds": poly.bounds
        })

    return polygons


def build_database():

    categories = [
        "sea",
        "strait",
        "gulf",
        "bay",
        "channel",
        "bight",
        "sound",
        "passage",
        "ocean",
        "other",
    ]

    database = []

    for category in categories:
        database.extend(load_category(category))

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

        print("[OK] Polygon Cache ditemukan")

        return load_cache()

    print("[INFO] Cache tidak ditemukan, membaca GeoJSON...")

    return build_database()