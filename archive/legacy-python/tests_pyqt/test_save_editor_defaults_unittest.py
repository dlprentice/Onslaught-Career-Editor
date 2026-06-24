import os
import tempfile
import unittest
from pathlib import Path

from tests_shared.fixture_paths import REPO_ROOT, SAVE_FIXTURE

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class SaveEditorDefaultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from PyQt6.QtWidgets import QApplication
        except Exception as exc:
            raise unittest.SkipTest(f"PyQt6 unavailable: {exc}")

        cls._QApplication = QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_save_mode_defaults_are_safe(self):
        from onslaught.gui.tabs.save_editor import SaveEditorTab

        tab = SaveEditorTab(configuration_only=False)
        try:
            self.assertFalse(tab.configuration_only)
            self.assertFalse(tab.kills_only_check.isChecked())
            self.assertFalse(tab.patch_nodes_check.isChecked())
            self.assertFalse(tab.patch_links_check.isChecked())
            self.assertFalse(tab.patch_goodies_check.isChecked())
            self.assertFalse(tab.patch_kills_check.isChecked())

            self.assertFalse(tab.copy_options_entries_check.isChecked())
            self.assertFalse(tab.copy_options_tail_check.isChecked())
            self.assertFalse(tab.copy_options_entries_check.isEnabled())
            self.assertFalse(tab.copy_options_tail_check.isEnabled())
        finally:
            tab.deleteLater()

    def test_configuration_mode_defaults_are_safe(self):
        from onslaught.gui.tabs.save_editor import SaveEditorTab

        tab = SaveEditorTab(configuration_only=True)
        try:
            self.assertTrue(tab.configuration_only)
            self.assertTrue(tab.is_options_file)
            self.assertFalse(tab.kills_only_check.isChecked())
            self.assertFalse(tab.patch_nodes_check.isChecked())
            self.assertFalse(tab.patch_links_check.isChecked())
            self.assertFalse(tab.patch_goodies_check.isChecked())
            self.assertFalse(tab.patch_kills_check.isChecked())
            self.assertFalse(tab.patch_nodes_check.isEnabled())
            self.assertFalse(tab.patch_links_check.isEnabled())
            self.assertFalse(tab.patch_goodies_check.isEnabled())
            self.assertFalse(tab.patch_kills_check.isEnabled())

            self.assertFalse(tab.copy_options_entries_check.isChecked())
            self.assertFalse(tab.copy_options_tail_check.isChecked())
            self.assertFalse(tab.copy_options_entries_check.isEnabled())
            self.assertFalse(tab.copy_options_tail_check.isEnabled())
        finally:
            tab.deleteLater()

    def test_copy_source_first_selection_defaults_save_mode(self):
        from onslaught.gui.tabs.save_editor import SaveEditorTab

        tab = SaveEditorTab(configuration_only=False)
        try:
            tab.copy_options_from_path = Path("tests_shared/fixtures/gold_career_save.bin")
            tab._refresh_copy_options_controls()
            self.assertFalse(tab.copy_options_entries_check.isChecked())
            self.assertFalse(tab.copy_options_tail_check.isChecked())
            self.assertTrue(tab.copy_options_entries_check.isEnabled())
            self.assertTrue(tab.copy_options_tail_check.isEnabled())

            tab.copy_options_from_path = None
            tab._refresh_copy_options_controls()
            self.assertFalse(tab.copy_options_entries_check.isChecked())
            self.assertFalse(tab.copy_options_tail_check.isChecked())
            self.assertFalse(tab.copy_options_entries_check.isEnabled())
            self.assertFalse(tab.copy_options_tail_check.isEnabled())
        finally:
            tab.deleteLater()

    def test_copy_source_first_selection_defaults_configuration_mode(self):
        from onslaught.gui.tabs.save_editor import SaveEditorTab

        tab = SaveEditorTab(configuration_only=True)
        try:
            tab.copy_options_from_path = Path("tests_shared/fixtures/gold_career_save.bin")
            tab._refresh_copy_options_controls()
            self.assertTrue(tab.copy_options_entries_check.isChecked())
            self.assertFalse(tab.copy_options_tail_check.isChecked())
            self.assertTrue(tab.copy_options_entries_check.isEnabled())
            self.assertTrue(tab.copy_options_tail_check.isEnabled())

            tab.copy_options_from_path = None
            tab._refresh_copy_options_controls()
            self.assertFalse(tab.copy_options_entries_check.isChecked())
            self.assertFalse(tab.copy_options_tail_check.isChecked())
            self.assertFalse(tab.copy_options_entries_check.isEnabled())
            self.assertFalse(tab.copy_options_tail_check.isEnabled())
        finally:
            tab.deleteLater()

    def test_configuration_mode_defaults_output_to_input_path(self):
        from onslaught.gui.tabs.save_editor import SaveEditorTab

        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")
        with tempfile.TemporaryDirectory(prefix="onslaught-config-defaults-") as td:
            td_path = Path(td)
            input_bea = td_path / "defaultoptions.bea"
            input_bea.write_bytes(SAVE_FIXTURE.read_bytes())

            tab = SaveEditorTab(configuration_only=True)
            try:
                tab._on_input_selected(input_bea)
                self.assertEqual(tab.output_path, input_bea)
                self.assertTrue(tab.patch_btn.isEnabled())
            finally:
                tab.deleteLater()

    def test_save_mode_same_path_stays_blocked(self):
        from onslaught.gui.tabs.save_editor import SaveEditorTab

        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")
        with tempfile.TemporaryDirectory(prefix="onslaught-save-samepath-") as td:
            td_path = Path(td)
            input_bes = td_path / "sample.bes"
            input_bes.write_bytes(SAVE_FIXTURE.read_bytes())

            tab = SaveEditorTab(configuration_only=False)
            try:
                tab.input_path = input_bes
                tab.output_path = input_bes
                tab.input_valid = True
                tab._update_patch_button()
                self.assertFalse(tab.patch_btn.isEnabled())
            finally:
                tab.deleteLater()


if __name__ == "__main__":
    unittest.main(verbosity=2)
