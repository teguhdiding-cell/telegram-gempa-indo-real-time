import shapefile
from pathlib import Path
from shapely.geometry import shape
from shapely.geometry import mapping

BASE = Path(__file__).parent.parent

SHP = (
    BASE
    / "data"
    / "raw"
    / "iho_v3"
    / "World_Seas_IHO_v3"
    / "World_Seas_IHO_v3.shp"
)

sf = shapefile.Reader(str(SHP))

geo = shape(sf.shape(13).__geo_interface__)

print("=" * 60)
print("TEST SHAPELY")
print("=" * 60)

print("Geometry Type :", geo.geom_type)
print("Is Valid      :", geo.is_valid)
print("Area          :", geo.area)

geojson = mapping(geo)

print()
print("GeoJSON Type :", geojson["type"])

import json

print()
print("=" * 60)
print("5 KUNCI GEOMETRY")
print("=" * 60)

print(geojson.keys())

print()
print(json.dumps(geojson, indent=2)[:1000])