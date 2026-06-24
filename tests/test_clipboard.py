"""剪贴板工具测试。"""

from bagua import clipboard


def test_copy_empty_returns_false():
    assert clipboard.copy_to_clipboard("") is False


def test_copy_fallback_chain(monkeypatch):
    monkeypatch.setattr(clipboard, "_copy_via_win32", lambda _t: False)
    monkeypatch.setattr(clipboard, "_copy_via_windows_clip", lambda _t: False)
    monkeypatch.setattr(clipboard, "_copy_via_tkinter", lambda _t: True)
    assert clipboard.copy_to_clipboard("hello") is True