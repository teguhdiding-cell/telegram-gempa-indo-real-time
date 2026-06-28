import json
from pathlib import Path


def validasi_geojson(path_file):
    try:
        with open(path_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("type") != "FeatureCollection":
            print("❌ Bukan FeatureCollection")
            return False

        print("✅ GeoJSON valid")
        return True

    except Exception as e:
        print("❌ Error :", e)
        return False


if __name__ == "__main__":
    print("Validator Polygon Indonesia")