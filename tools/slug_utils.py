import re


def slugify(name: str) -> str:
    """
    Mengubah nama menjadi nama file.
    """

    name = name.lower()

    name = name.replace("&", "and")

    name = re.sub(r"[^a-z0-9]+", "_", name)

    name = re.sub(r"_+", "_", name)

    return name.strip("_")