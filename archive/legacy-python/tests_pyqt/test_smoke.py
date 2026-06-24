import os
import sys
import tempfile
from pathlib import Path

import pytest
from tests_shared.fixture_paths import SAVE_FIXTURE

pytest.importorskip("PyQt6")


def _has_display() -> bool:
    if sys.platform.startswith("win"):
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def test_main_window_tabs(qtbot):
    if not _has_display():
        pytest.skip("No GUI display available for PyQt smoke test.")

    from onslaught.gui.main_window import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    qtbot.waitExposed(window, timeout=2000)

    tab_widget = window.tabs
    top_labels = [tab_widget.tabText(i) for i in range(tab_widget.count())]

    expected_top = {"Saves", "Media", "Lore", "Binary Patches", "Settings"}
    assert expected_top.issubset(set(top_labels))

    nested_labels = set()
    for nested in (window.save_tabs, window.media_tabs):
        nested_labels.update(nested.tabText(i) for i in range(nested.count()))

    expected_nested = {
        "Save Editor",
        "Save Analyzer",
        "Configuration Editor",
        "Audio Player",
        "Video Player",
    }

    assert expected_nested.issubset(nested_labels)


def test_main_window_open_path_routes_bea_to_configuration_editor(qtbot):
    if not _has_display():
        pytest.skip("No GUI display available for PyQt smoke test.")

    from onslaught.gui.main_window import MainWindow

    assert SAVE_FIXTURE.exists()

    with tempfile.TemporaryDirectory(prefix="onslaught-open-path-") as td:
        options_file = Path(td) / "defaultoptions.bea"
        options_file.write_bytes(SAVE_FIXTURE.read_bytes())

        window = MainWindow()
        qtbot.addWidget(window)
        assert window.open_path(options_file)
        assert window.tabs.currentWidget() is window.save_tabs
        assert window.save_tabs.currentWidget() is window.config_editor_tab


def test_main_window_compare_paths_routes_to_analyzer(qtbot):
    if not _has_display():
        pytest.skip("No GUI display available for PyQt smoke test.")

    from onslaught.gui.main_window import MainWindow

    assert SAVE_FIXTURE.exists()

    with tempfile.TemporaryDirectory(prefix="onslaught-compare-paths-") as td:
        left = Path(td) / "left.bes"
        right = Path(td) / "right.bes"
        left.write_bytes(SAVE_FIXTURE.read_bytes())
        right.write_bytes(SAVE_FIXTURE.read_bytes())

        window = MainWindow()
        qtbot.addWidget(window)
        assert window.compare_paths(left, right)
        assert window.tabs.currentWidget() is window.save_tabs
        assert window.save_tabs.currentWidget() is window.save_analyzer_tab
        assert window.save_analyzer_tab.output_title.text() == "File Comparison"
