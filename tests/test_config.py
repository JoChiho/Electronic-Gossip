"""配置持久化测试。"""

from bagua.config import CONFIG_PATH, load_config, save_config
from bagua.models import UserConfig


def test_user_config_roundtrip(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr("bagua.config.CONFIG_PATH", config_file)
    monkeypatch.setattr("bagua.config.BAGUA_DIR", tmp_path)

    cfg = UserConfig(
        timezone="Asia/Tokyo",
        region_label="日本",
        question="测试问题",
        bazi="甲子",
        birth_datetime="1990-01-01 08:00",
        coin_mode="auto",
    )
    save_config(cfg)

    loaded = load_config()
    assert loaded.timezone == "Asia/Tokyo"
    assert loaded.question == "测试问题"
    assert loaded.coin_mode == "auto"