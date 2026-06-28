from core.sea_locator import find_sea
from core.province_locator import find_province


def locate(lat, lon):

    hasil = {}

    hasil["sea"] = find_sea(lat, lon)

    hasil["province"] = find_province(lat, lon)

    return hasil