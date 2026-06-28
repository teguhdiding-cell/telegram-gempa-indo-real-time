def save_geojson(category, filename, feature):

    folder = (
        BASE
        / "data"
        / category
    )

    folder.mkdir(parents=True, exist_ok=True)

    path = folder / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            feature,
            f,
            ensure_ascii=False,
            indent=2
        )

    return path

import json
import shapefile

from pathlib import Path
from shapely.geometry import shape, mapping

from slug_utils import slugify
from category_utils import detect_category

BASE = Path(__file__).parent.parent

RAW_FILE = (
    BASE
    / "data"
    / "raw"
    / "iho_v3"
    / "World_Seas_IHO_v3"
    / "World_Seas_IHO_v3.shp"
)

sf = shapefile.Reader(str(RAW_FILE))

print("=" * 60)
print("IHO CONVERTER V15.3")
print("=" * 60)

print("Jumlah Record :", len(sf))
print()

for i, record in enumerate(sf.records()):

    name = record["NAME"]

    shape_record = sf.shape(i)

    geo = shape(shape_record.__geo_interface__)

    feature = {
        "type": "Feature",
        "properties": {
            "name": name
        },
        "geometry": mapping(geo)
    }

    category = detect_category(name)

    filename = slugify(name) + ".geojson"

    path = save_geojson(
    category,
    filename,
    feature
    )

    print(
        f"{i+1:03d}",
        "|",
        category.ljust(8),
        "|",
        path.name
    )