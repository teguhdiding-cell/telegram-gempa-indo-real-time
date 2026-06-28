def detect_category(name: str) -> str:
    """
    Menentukan kategori berdasarkan nama IHO.
    """

    name = name.lower()

    rules = [
        ("strait", "strait"),
        ("channel", "channel"),
        ("gulf", "gulf"),
        ("bay", "bay"),
        ("bight", "bight"),
        ("sound", "sound"),
        ("passage", "passage"),
        ("ocean", "ocean"),
        ("sea", "sea"),
    ]

    for keyword, category in rules:
        if keyword in name:
            return category

    return "other"