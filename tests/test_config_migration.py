"""配置迁移与双时区测试。"""

from bagua.config import load_config, normalize_config_data, save_config
from bagua.models import UserConfig


def test_legacy_longitude_migrates_to_divination(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr("bagua.config.CONFIG_PATH", config_file)
    monkeypatch.setattr("bagua.config.BAGUA_DIR", tmp_path)

    config_file.write_text(
        '{"timezone":"Asia/Shanghai","longitude":121.5,"use_true_solar":true}',
        encoding="utf-8",
    )
    cfg = load_config()
    assert cfg.divination_longitude == 121.5
    assert cfg.use_true_solar_divination is True
    assert cfg.use_true_solar_birth is True


def test_normalize_fills_divination_timezone():
    data = normalize_config_data({"timezone": "Asia/Tokyo", "region_label": "日本"})
    assert data["divination_timezone"] == "Asia/Tokyo"


def test_save_persists_split_timezones(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr("bagua.config.CONFIG_PATH", config_file)
    monkeypatch.setattr("bagua.config.BAGUA_DIR", tmp_path)

    cfg = UserConfig(
        timezone="Asia/Shanghai",
        region_label="中国",
        divination_timezone="Asia/Tokyo",
        divination_region_label="日本",
        birth_longitude=121.47,
        divination_longitude=139.69,
    )
    save_config(cfg)
    loaded = load_config()
    assert loaded.timezone == "Asia/Shanghai"
    assert loaded.divination_timezone == "Asia/Tokyo"
    assert loaded.birth_longitude == 121.47
    assert loaded.divination_longitude == 139.69