"""地点与经纬度解析测试。"""

from bagua.locations import (
    LOCATION_CUSTOM,
    LOCATION_FOLLOW_TZ,
    coordinates_for_city,
    infer_location_label,
    longitude_for_city,
    resolve_display_coord,
    resolve_longitude,
)


def test_longitude_for_city_beijing():
    assert longitude_for_city("北京") == 116.41


def test_coordinates_for_city_beijing():
    coord = coordinates_for_city("北京")
    assert coord is not None
    assert coord.latitude == 39.90
    assert coord.longitude == 116.41


def test_resolve_follow_timezone_returns_none():
    assert resolve_longitude(LOCATION_FOLLOW_TZ, "", "Asia/Shanghai") is None


def test_resolve_custom_longitude():
    assert resolve_longitude(LOCATION_CUSTOM, "116.4", "Asia/Shanghai") == 116.4


def test_resolve_display_coord_city_updates_both():
    lon, lat = resolve_display_coord("北京", "", "Asia/Shanghai")
    assert lon == 116.41
    assert lat == 39.90


def test_infer_location_label_custom():
    assert infer_location_label(100.5, "Asia/Shanghai") == LOCATION_CUSTOM


def test_infer_location_label_city():
    assert infer_location_label(116.41, "Asia/Shanghai") == "北京"