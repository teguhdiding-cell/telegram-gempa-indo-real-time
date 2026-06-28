from category_utils import detect_category

tests = [
    "Java Sea",
    "Makassar Strait",
    "Gulf of Tomini",
    "Indian Ocean",
    "Rio de La Plata"
]

for item in tests:
    print(f"{item} -> {detect_category(item)}")