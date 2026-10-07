# test_config_loader.py
import pytest

from config_loader import get_int, load_settings


def test_value_containing_equals_sign_is_kept_whole(tmp_path):
    cfg = tmp_path / "s.cfg"
    cfg.write_text("report_title = a=b\n", encoding="utf-8")
    assert load_settings(cfg)["report_title"] == "a=b"


def test_unknown_key_warns(tmp_path):
    cfg = tmp_path / "s.cfg"
    cfg.write_text("warn_at_precent = 80\n", encoding="utf-8")
    with pytest.warns(UserWarning, match="warn_at_precent"):
        assert load_settings(cfg) == {}


def test_shipped_settings_hold_the_approved_rules():
    s = load_settings()
    assert get_int(s, "service_interval_km", -1) == 15000
    assert get_int(s, "warn_at_percent", -1) == 80


def test_get_int_falls_back_on_bad_value():
    assert get_int({"x": "abc"}, "x", 7) == 7
    assert get_int({}, "x", 7) == 7
