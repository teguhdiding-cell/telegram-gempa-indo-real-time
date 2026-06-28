def point_in_polygon(lat, lon, polygon):
    """
    Mengecek apakah titik (lat, lon)
    berada di dalam polygon.

    polygon:
    [
        (lat, lon),
        (lat, lon),
        ...
    ]
    """

    inside = False

    j = len(polygon) - 1

    for i in range(len(polygon)):

        lat_i, lon_i = polygon[i]
        lat_j, lon_j = polygon[j]

        if (
            (lon_i > lon) != (lon_j > lon)
            and
            lat < (
                (lat_j - lat_i)
                * (lon - lon_i)
                / (lon_j - lon_i)
                + lat_i
            )
        ):
            inside = not inside

        j = i

    return inside
