"""配置持久化测试。"""

from bagua.config import load_config, save_config
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
        last_method="time",
        use_current_time=False,
        time_input="2026-06-24 14:30",
        coin_tosses=[["1", "2", "1"], ["2", "2", "2"], ["1", "1", "1"], ["1", "2", "2"], ["2", "1", "1"], ["1", "1", "2"]],
    )
    save_config(cfg)

    loaded = load_config()
    assert loaded.timezone == "Asia/Tokyo"
    assert loaded.question == "测试问题"
    assert loaded.coin_mode == "auto"
    assert loaded.last_method == "time"
    assert loaded.use_current_time is False
    assert loaded.time_input == "2026-06-24 14:30"
    assert loaded.coin_tosses[0] == ["1", "2", "1"]