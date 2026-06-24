"""
Onslaught Career Editor - Save Analyzer Tab
GUI wrapper around patcher.py --analyze functionality for .bes/.bea files.
"""

import io
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QCheckBox,
    QMessageBox, QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem, QApplication, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.bes_file import BesFile
from ..widgets import SaveSelector


class SaveAnalyzerTab(QWidget):
    """Save/options analyzer tab - inspect .bes/.bea files without modification"""

    gameDirChanged = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.compare_file = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the tab UI"""
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, 1)

        # Left panel (file selection, options, summary)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Primary file selection using SaveSelector
        self.primary_selector = SaveSelector(label="Primary Save/Options File")
        self.primary_selector.fileSelected.connect(self._on_primary_selected)
        self.primary_selector.selectionCleared.connect(self._on_primary_cleared)
        self.primary_selector.gameDirChanged.connect(self._on_game_dir_changed)

        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        file_layout.addWidget(self.primary_selector)

        file_buttons = QHBoxLayout()
        file_buttons.setSpacing(8)
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self._do_analyze)
        self.analyze_btn.setMinimumWidth(110)
        file_buttons.addWidget(self.analyze_btn)

        self.refresh_btn = QPushButton("Re-Analyze")
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.clicked.connect(self._do_analyze)
        self.refresh_btn.setMinimumWidth(110)
        file_buttons.addWidget(self.refresh_btn)
        file_buttons.addStretch()
        file_layout.addLayout(file_buttons)

        left_layout.addWidget(file_group)

        # Display options
        options_group = QGroupBox("Display Options")
        options_layout = QVBoxLayout(options_group)
        self.verbose_check = QCheckBox("Verbose (node details)")
        self.verbose_check.setToolTip("Show detailed per-node information")
        options_layout.addWidget(self.verbose_check)

        self.mystery_check = QCheckBox("Dump Reserved/Unmapped Bytes")
        self.mystery_check.setToolTip("Show hex dump of reserved/unmapped save-file regions")
        options_layout.addWidget(self.mystery_check)
        left_layout.addWidget(options_group)

        # Comparison file selection using SaveSelector
        self.compare_selector = SaveSelector(label="Comparison Save/Options File (Optional)", auto_select_first=False)
        self.compare_selector.fileSelected.connect(self._on_compare_selected)
        self.compare_selector.selectionCleared.connect(self._on_compare_cleared)
        self.compare_selector.gameDirChanged.connect(self._on_game_dir_changed)

        compare_group = QGroupBox("Compare Files")
        compare_layout = QVBoxLayout(compare_group)
        compare_layout.addWidget(self.compare_selector)
        self.compare_action_btn = QPushButton("Compare Files")
        self.compare_action_btn.setEnabled(False)
        self.compare_action_btn.clicked.connect(self._do_compare)
        self.compare_action_btn.setMinimumWidth(120)
        compare_layout.addWidget(self.compare_action_btn)
        left_layout.addWidget(compare_group)

        # Summary tree
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout(summary_group)
        self.summary_tree = QTreeWidget()
        self.summary_tree.setHeaderLabels(["Property", "Value"])
        self.summary_tree.setColumnWidth(0, 180)
        summary_layout.addWidget(self.summary_tree)
        left_layout.addWidget(summary_group, 1)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(left_panel)
        splitter.addWidget(left_scroll)

        # Right panel (output)
        output_group = QGroupBox("Analysis Output")
        output_layout = QVBoxLayout(output_group)

        output_header = QHBoxLayout()
        output_header.setSpacing(8)
        self.output_title = QLabel("Save/Options Analysis")
        self.output_title.setFont(QFont("Sans", 10, QFont.Weight.Bold))
        output_header.addWidget(self.output_title)
        output_header.addStretch()

        self.copy_btn = QPushButton("Copy Output")
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._copy_output)
        output_header.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_output)
        output_header.addWidget(self.clear_btn)

        output_layout.addLayout(output_header)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Monospace", 9))
        output_layout.addWidget(self.output_text)
        splitter.addWidget(output_group)

        splitter.setSizes([320, 640])

    def _on_primary_selected(self, path: Path):
        """Handle primary file selection"""
        self.current_file = path
        self._update_buttons()
        # Auto-analyze on file selection
        self._do_analyze()

    def _on_compare_selected(self, path: Path):
        """Handle comparison file selection"""
        self.compare_file = path
        self._update_buttons()

    def _on_primary_cleared(self) -> None:
        """Handle primary selection clear."""
        self.current_file = None
        self._update_buttons()

    def _on_compare_cleared(self) -> None:
        """Handle comparison selection clear."""
        self.compare_file = None
        self._update_buttons()

    def _on_game_dir_changed(self, path: Path):
        """Propagate game directory changes to the main window."""
        self.gameDirChanged.emit(path)

    def _update_buttons(self):
        """Update button states"""
        self.analyze_btn.setEnabled(self.current_file is not None)
        self.refresh_btn.setEnabled(self.current_file is not None)
        self.compare_action_btn.setEnabled(
            self.current_file is not None and
            self.compare_file is not None
        )
        self.copy_btn.setEnabled(bool(self.output_text.toPlainText().strip()))

    def _clear_output(self):
        """Clear output and reset"""
        self.output_text.clear()
        self.summary_tree.clear()
        self.output_title.setText("Save/Options Analysis")
        self._update_buttons()

    def _copy_output(self):
        """Copy analysis output to clipboard"""
        text = self.output_text.toPlainText()
        if not text.strip():
            return
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Analysis output copied to clipboard.")

    @staticmethod
    def _calculate_diff_summary(left_path: Path, right_path: Path) -> tuple[int, int, bool]:
        left = left_path.read_bytes()
        right = right_path.read_bytes()
        min_len = min(len(left), len(right))

        diff_offsets: list[int] = []
        for idx in range(min_len):
            if left[idx] != right[idx]:
                diff_offsets.append(idx)

        if len(left) != len(right):
            diff_offsets.extend(range(min_len, max(len(left), len(right))))

        if not diff_offsets:
            return 0, 0, len(left) == len(right)

        ranges = 1
        last = diff_offsets[0]
        for offset in diff_offsets[1:]:
            if offset != last + 1:
                ranges += 1
            last = offset

        return len(diff_offsets), ranges, len(left) == len(right)

    def _populate_compare_summary(self, left_path: Path, right_path: Path) -> None:
        diff_bytes, diff_ranges, same_size = self._calculate_diff_summary(left_path, right_path)
        self.summary_tree.clear()

        compare_item = QTreeWidgetItem(["Comparison", ""])
        compare_item.addChild(QTreeWidgetItem(["Left file", left_path.name]))
        compare_item.addChild(QTreeWidgetItem(["Right file", right_path.name]))
        compare_item.addChild(QTreeWidgetItem(["Size match", "Yes" if same_size else "No"]))
        compare_item.addChild(QTreeWidgetItem(["Differing bytes", f"{diff_bytes:,}"]))
        compare_item.addChild(QTreeWidgetItem(["Difference ranges", str(diff_ranges)]))

        try:
            left_stats = BesFile.load(left_path, strict_version=False).get_stats()
            right_stats = BesFile.load(right_path, strict_version=False).get_stats()
            compare_item.addChild(QTreeWidgetItem([
                "Left file kind",
                "defaultoptions.bea" if left_stats.get("is_options_file") else ".bes career save",
            ]))
            compare_item.addChild(QTreeWidgetItem([
                "Right file kind",
                "defaultoptions.bea" if right_stats.get("is_options_file") else ".bes career save",
            ]))
        except Exception:
            pass

        self.summary_tree.addTopLevelItem(compare_item)
        self.summary_tree.expandAll()

    def _populate_summary(self, bes: BesFile):
        """Populate the summary tree with file stats"""
        self.summary_tree.clear()
        stats = bes.get_stats()

        # File info
        file_item = QTreeWidgetItem(["File", ""])
        file_item.addChild(QTreeWidgetItem(["Path", str(stats.get('file_path', 'Unknown'))]))
        file_item.addChild(QTreeWidgetItem(["Version word", stats.get('version_word', 'Unknown')]))
        file_item.addChild(QTreeWidgetItem(["Header dword view", stats.get('header_dword_view', 'Unknown')]))
        file_item.addChild(QTreeWidgetItem(["Size", f"{stats.get('file_size', 0):,} bytes"]))
        version_valid = stats.get('version_valid', False)
        file_item.addChild(QTreeWidgetItem(["Version Valid", "Yes" if version_valid else "NO"]))
        new_goodie_count = int(stats.get('new_goodie_count_raw', 0))
        file_item.addChild(QTreeWidgetItem(["NewGoodieCount", f"{new_goodie_count} (0x{new_goodie_count:08X})"]))
        self.summary_tree.addTopLevelItem(file_item)

        # Options / settings
        options_item = QTreeWidgetItem(["Options", ""])
        file_kind = "defaultoptions.bea (boot/global)" if stats.get("is_options_file") else ".bes (career save)"
        options_item.addChild(QTreeWidgetItem(["File kind", file_kind]))
        options_item.addChild(QTreeWidgetItem([
            "Volumes",
            f"Sound={stats.get('sound_volume', 0.0):0.3f} Music={stats.get('music_volume', 0.0):0.3f}",
        ]))
        invert_walker = stats.get("invert_y_axis_raw", [0, 0])
        invert_flight = stats.get("invert_flight_raw", [0, 0])
        vibration = stats.get("vibration_raw", [0, 0])
        options_item.addChild(QTreeWidgetItem([
            "InvertY Walker",
            f"P1={'ON' if invert_walker[0] != 0 else 'OFF'}, P2={'ON' if invert_walker[1] != 0 else 'OFF'}",
        ]))
        options_item.addChild(QTreeWidgetItem([
            "InvertY Flight",
            f"P1={'ON' if invert_flight[0] != 0 else 'OFF'}, P2={'ON' if invert_flight[1] != 0 else 'OFF'}",
        ]))
        options_item.addChild(QTreeWidgetItem([
            "Vibration",
            f"P1={'ON' if vibration[0] != 0 else 'OFF'}, P2={'ON' if vibration[1] != 0 else 'OFF'}",
        ]))
        options_entry_count = int(stats.get("options_entry_count", 0))
        if options_entry_count > 0:
            options_item.addChild(QTreeWidgetItem([
                "Options entries",
                f"{options_entry_count} (tail @ 0x{int(stats.get('options_tail_start', 0)):04X})",
            ]))
            options_item.addChild(QTreeWidgetItem([
                "ControlSchemeIndex",
                str(int(stats.get("options_control_scheme_index", 0))),
            ]))
            options_item.addChild(QTreeWidgetItem([
                "MouseSensitivity",
                f"{float(stats.get('options_mouse_sensitivity', 0.0)):0.3f}",
            ]))
            options_item.addChild(QTreeWidgetItem([
                "ScreenShape",
                f"{int(stats.get('options_screen_shape', 0))} (0=4:3,1=16:9,2=1:1)",
            ]))
        self.summary_tree.addTopLevelItem(options_item)

        # Missions
        missions_item = QTreeWidgetItem(["Missions", f"{stats['completed_missions']}/{stats['total_missions']}"])
        if stats.get('rank_distribution'):
            for rank, count in sorted(stats['rank_distribution'].items()):
                missions_item.addChild(QTreeWidgetItem([f"Rank {rank}", str(count)]))
        if stats.get('partial_nodes', 0) > 0:
            missions_item.addChild(QTreeWidgetItem(["Partial", str(stats['partial_nodes'])]))
        self.summary_tree.addTopLevelItem(missions_item)

        # Links
        links_item = QTreeWidgetItem(["Links", f"{stats.get('completed_links', 0)}/200"])
        self.summary_tree.addTopLevelItem(links_item)

        # Goodies
        goodies_item = QTreeWidgetItem(["Goodies", ""])
        goodies_item.addChild(QTreeWidgetItem(["NEW (gold)", str(stats.get('goodies_new', 0))]))
        goodies_item.addChild(QTreeWidgetItem(["OLD (blue)", str(stats.get('goodies_old', 0))]))
        goodies_item.addChild(QTreeWidgetItem(["Locked", str(stats.get('goodies_locked', 0))]))
        if stats.get('goodies_other', 0) > 0:
            goodies_item.addChild(QTreeWidgetItem(["Other", str(stats.get('goodies_other', 0))]))
        if stats.get('goodies_reserved', 0) > 0:
            goodies_item.addChild(QTreeWidgetItem(["Reserved", str(stats.get('goodies_reserved', 0))]))
        self.summary_tree.addTopLevelItem(goodies_item)

        # Kills
        total_kills = stats.get('total_kills', 0)
        kills_item = QTreeWidgetItem(["Kills", f"{total_kills:,} total"])
        kills = stats.get('kills', {})
        thresholds = stats.get('next_unlock_thresholds', [])
        for idx, cat in enumerate(kills.keys()):
            count = kills[cat]
            next_thresh = thresholds[idx] if idx < len(thresholds) else None
            suffix = f" (next: {next_thresh})" if next_thresh is not None else " (max)"
            kills_item.addChild(QTreeWidgetItem([cat, f"{count}{suffix}"]))
        self.summary_tree.addTopLevelItem(kills_item)

        # God mode
        god_item = QTreeWidgetItem(["God Mode", ""])
        god_enabled_raw = int(stats.get('god_mode_enabled_raw', 0))
        god_item.addChild(QTreeWidgetItem([
            "Enabled (toggle)",
            f"{'ON' if stats.get('god_mode_enabled') else 'OFF'} (0x{god_enabled_raw:08X})",
        ]))
        self.summary_tree.addTopLevelItem(god_item)

        # Tech slots
        tech_item = QTreeWidgetItem([
            "Tech Slots",
            f"{stats.get('tech_slots_active', 0)}/{stats.get('tech_slots_total', 0)} active"
        ])
        self.summary_tree.addTopLevelItem(tech_item)

        # Reserved/unmapped regions
        mystery = stats.get('mystery_regions', [])
        if mystery:
            total_bytes = sum(r.get('size', 0) for r in mystery)
            mystery_item = QTreeWidgetItem(["Reserved/Unmapped Regions", f"{total_bytes} bytes"])
            for region in mystery:
                if region.get('all_zeros'):
                    status = "[zeros]"
                elif region.get('all_ff'):
                    status = "[0xFF]"
                else:
                    status = f"{region.get('non_zero', 0)} non-zero"
                mystery_item.addChild(QTreeWidgetItem([region.get('name', 'Region'), status]))
            self.summary_tree.addTopLevelItem(mystery_item)

        self.summary_tree.expandAll()

    def _do_analyze(self):
        """Perform analysis on the selected file"""
        if not self.current_file or not self.current_file.exists():
            QMessageBox.warning(self, "Error", "Please select a valid .bes/.bea file")
            return

        self._clear_output()

        try:
            # Use BesFile for summary
            bes = BesFile.load(self.current_file, strict_version=False)
            self._populate_summary(bes)

            # Use patcher.py analyze_file for detailed output
            import sys as _sys
            _sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from patcher import analyze_file

            # Capture stdout
            old_stdout = _sys.stdout
            _sys.stdout = captured = io.StringIO()

            try:
                analyze_file(
                    self.current_file,
                    verbose=self.verbose_check.isChecked(),
                    dump_mystery=self.mystery_check.isChecked()
                )
            finally:
                _sys.stdout = old_stdout

            self.output_text.setPlainText(captured.getvalue())
            self.output_title.setText("Save/Options Analysis")
            self._update_buttons()

        except Exception as e:
            self.output_text.setPlainText(f"Error analyzing file: {e}")
            QMessageBox.critical(self, "Error", f"Analysis failed: {e}")

    def _do_compare(self):
        """Compare two .bes/.bea files"""
        if not self.current_file or not self.compare_file:
            QMessageBox.warning(self, "Error", "Please select two files to compare")
            return

        if not self.current_file.exists():
            QMessageBox.warning(self, "Error", f"File not found: {self.current_file}")
            return

        if not self.compare_file.exists():
            QMessageBox.warning(self, "Error", f"File not found: {self.compare_file}")
            return

        self._clear_output()

        try:
            import sys as _sys
            _sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from patcher import compare_files

            # Capture stdout
            old_stdout = _sys.stdout
            _sys.stdout = captured = io.StringIO()

            try:
                compare_files(self.current_file, self.compare_file)
            finally:
                _sys.stdout = old_stdout

            self._populate_compare_summary(self.current_file, self.compare_file)
            self.output_text.setPlainText(captured.getvalue())
            self.output_title.setText("File Comparison")
            self._update_buttons()

        except Exception as e:
            self.output_text.setPlainText(f"Error comparing files: {e}")
            QMessageBox.critical(self, "Error", f"Comparison failed: {e}")

    def load_file(self, path: Path):
        """Load a file into the analyzer (called from main window)"""
        self.primary_selector.set_path(path)

    def set_compare_file(self, path: Path) -> None:
        """Load a compare file into the analyzer selector."""
        self.compare_selector.set_path(path)

    def compare_files(self, left: Path, right: Path) -> None:
        """Load two files and run compare immediately."""
        self.load_file(left)
        self.set_compare_file(right)
        self._do_compare()
