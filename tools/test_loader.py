from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent

sys.path.append(str(ROOT))

from core.sea_loader import load_all

db = load_all()

print("=" * 60)
print("JUMLAH POLYGON :", len(db))
print("=" * 60)

print()

print(db[0]["name"])
print(db[1]["name"])
print(db[2]["name"])
print(db[3]["name"])
print(db[4]["name"])