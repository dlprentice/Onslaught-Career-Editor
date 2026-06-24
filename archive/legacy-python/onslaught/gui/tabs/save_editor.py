"""
Onslaught Career Editor - Save Editor Tab
GUI wrapper around patcher.py functionality
"""

import shutil
import struct
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QFileDialog, QMessageBox, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QDoubleValidator, QIntValidator, QRegularExpressionValidator
from typing import Optional

from ...core.constants import (
    RANK_VALUES, KILL_THRESHOLDS, BES_FILE_SIZE, NUM_LEVELS,
    OFFSET_OPTIONS_ENTRIES, OPTIONS_TAIL_SIZE,
)
from ..widgets import SaveSelector


class SaveEditorTab(QWidget):
    """Save file editor tab - patch .bes files to unlock content"""

    gameDirChanged = pyqtSignal(Path)

    def __init__(self, parent=None, configuration_only: bool = False):
        super().__init__(parent)
        self.configuration_only = configuration_only
        self.input_path = None
        self.output_path = None
        self.input_valid = False
        self.is_options_file = False
        self.copy_options_from_path = None
        self._had_copy_options_source = False
        self._keybind_overrides_valid = True
        self._kills_only_restore_captured = False
        self._kills_only_restore_nodes = True
        self._kills_only_restore_links = True
        self._kills_only_restore_goodies = True
        self._kills_only_restore_kills = True
        self._setup_ui()
        self._set_options_file_mode(self.configuration_only)

    def _setup_ui(self):
        """Set up the tab UI"""
        outer_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll)

        content = QWidget()
        layout = QVBoxLayout(content)
        scroll.setWidget(content)

        # Input file selection using SaveSelector
        self.input_selector = SaveSelector(
            label="Input Options File" if self.configuration_only else "Input Save File"
        )
        self.input_selector.fileSelected.connect(self._on_input_selected)
        self.input_selector.selectionCleared.connect(self._on_input_cleared)
        self.input_selector.gameDirChanged.connect(self._on_game_dir_changed)
        layout.addWidget(self.input_selector)

        # Output file selection
        output_group = QGroupBox("Output Options File" if self.configuration_only else "Output File")
        output_layout = QHBoxLayout(output_group)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Output will be auto-generated, or browse to choose...")
        self.output_edit.setReadOnly(True)
        output_layout.addWidget(self.output_edit)

        self.output_btn = QPushButton("Browse...")
        self.output_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(self.output_btn)

        layout.addWidget(output_group)

        # Options row
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)
        options_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Rank options
        rank_group = QGroupBox("Rank")
        rank_layout = QVBoxLayout(rank_group)
        rank_layout.addWidget(QLabel("Default rank for all missions:"))
        self.rank_combo = QComboBox()
        self.rank_combo.addItems(['S', 'A', 'B', 'C', 'D', 'E', 'NONE'])
        self.rank_combo.setToolTip(
            "S = Perfect (1.0)\n"
            "A = 0.8\n"
            "B = 0.6\n"
            "C = 0.35\n"
            "D = 0.15\n"
            "E = 0.0\n"
            "NONE = No Grade (undefined behavior)"
        )
        rank_layout.addWidget(self.rank_combo)
        rank_layout.addStretch()
        options_layout.addWidget(rank_group)

        # Goodie options
        goodie_group = QGroupBox("Goodies")
        goodie_layout = QVBoxLayout(goodie_group)
        self.new_goodies_check = QCheckBox("Mark as NEW (gold badge)")
        self.new_goodies_check.setToolTip(
            "Checked: Goodies show gold 'NEW' badge\n"
            "Unchecked: Goodies show blue 'OLD' badge"
        )
        goodie_layout.addWidget(self.new_goodies_check)
        goodie_layout.addStretch()
        options_layout.addWidget(goodie_group)

        # Kill count options
        kill_group = QGroupBox("Kill Counts")
        kill_layout = QGridLayout(kill_group)

        kill_layout.addWidget(QLabel("Default:"), 0, 0)
        self.kill_spin = QSpinBox()
        self.kill_spin.setRange(0, 65535)
        self.kill_spin.setValue(100)
        self.kill_spin.setToolTip("Kill count for all categories (0-65535)")
        kill_layout.addWidget(self.kill_spin, 0, 1)
        kill_layout.addWidget(QLabel("Overrides in Advanced Options"), 0, 2)

        options_layout.addWidget(kill_group)

        layout.addLayout(options_layout)

        # Selective patching
        selective_group = QGroupBox("Patch Sections")
        selective_layout = QGridLayout(selective_group)

        self.kills_only_check = QCheckBox("Kills Only Mode")
        self.kills_only_check.setToolTip("Only patch kill counts (disable nodes, links, goodies)")
        self.kills_only_check.toggled.connect(self._toggle_kills_only)
        selective_layout.addWidget(self.kills_only_check, 0, 0, 1, 2)

        self.patch_nodes_check = QCheckBox("Missions")
        self.patch_nodes_check.setChecked(False)
        self.patch_nodes_check.setToolTip("Patch mission nodes (unlock levels, set ranks)")
        selective_layout.addWidget(self.patch_nodes_check, 1, 0)

        self.patch_links_check = QCheckBox("Links")
        self.patch_links_check.setChecked(False)
        self.patch_links_check.setToolTip(
            "Complete all used mission links (preserves non-zero types; leaves unused entries unchanged)"
        )
        selective_layout.addWidget(self.patch_links_check, 1, 1)

        self.patch_goodies_check = QCheckBox("Goodies")
        self.patch_goodies_check.setChecked(False)
        self.patch_goodies_check.setToolTip(
            "Unlock all displayable goodies (233). Leaves reserved entries unchanged."
        )
        selective_layout.addWidget(self.patch_goodies_check, 2, 0)

        self.patch_kills_check = QCheckBox("Kills")
        self.patch_kills_check.setChecked(False)
        self.patch_kills_check.setToolTip("Patch kill counts (for kill-based unlocks)")
        selective_layout.addWidget(self.patch_kills_check, 2, 1)

        layout.addWidget(selective_group)

        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QVBoxLayout(advanced_group)
        self.advanced_toggle = QCheckBox("Show advanced overrides")
        self.advanced_toggle.setChecked(False)
        self.advanced_toggle.toggled.connect(self._toggle_advanced)
        advanced_layout.addWidget(self.advanced_toggle)

        self.advanced_content = QWidget()
        advanced_content_layout = QGridLayout(self.advanced_content)

        advanced_content_layout.addWidget(QLabel("Per-Level Rank Overrides (node index 1-43):"), 0, 0)
        self.level_ranks_edit = QLineEdit()
        self.level_ranks_edit.setPlaceholderText("Format: 1:S,2:A,3:B")
        self.level_ranks_edit.setToolTip("Override default rank for specific nodes (node index 1-43). Example: 1:S,2:A,3:B")
        advanced_content_layout.addWidget(self.level_ranks_edit, 0, 1, 1, 3)

        # Per-category overrides (optional)
        advanced_content_layout.addWidget(QLabel("Per-Category Kill Overrides:"), 1, 0, 1, 4)
        kill_override_layout = QGridLayout()
        self.kill_edits = {}
        categories = ['Aircraft', 'Vehicles', 'Emplacements', 'Infantry', 'Mechs']
        thresholds = [
            '25/50/75/100',
            '100/200/300/400',
            '25/50 (75 in combos)',
            '40/80/160',
            '20/40/80 (40 repeats)',
        ]

        for i, (cat, thresh) in enumerate(zip(categories, thresholds)):
            lbl = QLabel(f"{cat}:")
            edit = QLineEdit()
            edit.setPlaceholderText("default")
            edit.setValidator(QIntValidator(0, 0x00FFFFFF, self))
            edit.setToolTip(f"Optional override. Unlock thresholds: {thresh}")
            self.kill_edits[cat.lower()] = edit
            kill_override_layout.addWidget(lbl, i, 0)
            kill_override_layout.addWidget(edit, i, 1)

        advanced_content_layout.addLayout(kill_override_layout, 2, 0, 1, 4)

        # Career settings overrides (optional)
        settings_group = QGroupBox("Career Settings Overrides (optional)")
        settings_layout = QGridLayout(settings_group)

        def _make_vol_edit() -> QLineEdit:
            edit = QLineEdit()
            edit.setPlaceholderText("keep")
            v = QDoubleValidator(0.0, 1.0, 3, self)
            v.setNotation(QDoubleValidator.Notation.StandardNotation)
            edit.setValidator(v)
            return edit

        self.sound_volume_edit = _make_vol_edit()
        self.sound_volume_edit.setToolTip("Override sound volume (0.0-1.0). Leave blank to keep existing save value.")
        self.music_volume_edit = _make_vol_edit()
        self.music_volume_edit.setToolTip("Override music volume (0.0-1.0). Leave blank to keep existing save value.")

        self.invert_y_p1_combo = QComboBox()
        self.invert_y_p1_combo.addItems(["Keep", "On", "Off"])
        self.invert_y_p1_combo.setToolTip(
            "Invert Y (Walker) override for P1. Keep preserves the existing save value. "
            "Steam build stores 0=Off, non-zero=On."
        )
        self.invert_y_p2_combo = QComboBox()
        self.invert_y_p2_combo.addItems(["Keep", "On", "Off"])
        self.invert_y_p2_combo.setToolTip(
            "Invert Y (Walker) override for P2. Keep preserves the existing save value. "
            "Steam build stores 0=Off, non-zero=On."
        )
        self.invert_flight_p1_combo = QComboBox()
        self.invert_flight_p1_combo.addItems(["Keep", "On", "Off"])
        self.invert_flight_p1_combo.setToolTip(
            "Invert Y (Flight/Jet) override for P1. Keep preserves the existing save value. "
            "Steam build stores 0=Off, non-zero=On."
        )
        self.invert_flight_p2_combo = QComboBox()
        self.invert_flight_p2_combo.addItems(["Keep", "On", "Off"])
        self.invert_flight_p2_combo.setToolTip(
            "Invert Y (Flight/Jet) override for P2. Keep preserves the existing save value. "
            "Steam build stores 0=Off, non-zero=On."
        )
        self.vibration_p1_combo = QComboBox()
        self.vibration_p1_combo.addItems(["Keep", "On", "Off"])
        self.vibration_p1_combo.setToolTip(
            "Controller vibration override for P1. Keep preserves the existing save value. "
            "Steam build stores 0=Off, non-zero=On."
        )
        self.vibration_p2_combo = QComboBox()
        self.vibration_p2_combo.addItems(["Keep", "On", "Off"])
        self.vibration_p2_combo.setToolTip(
            "Controller vibration override for P2. Keep preserves the existing save value. "
            "Steam build stores 0=Off, non-zero=On."
        )

        self.controller_cfg_p1_edit = QLineEdit()
        self.controller_cfg_p1_edit.setPlaceholderText("keep")
        self.controller_cfg_p1_edit.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"(0|[1-9][0-9]{0,9})"), self)
        )
        self.controller_cfg_p1_edit.setToolTip("Override controller config index for P1 (uint32). Leave blank to keep.")
        self.controller_cfg_p2_edit = QLineEdit()
        self.controller_cfg_p2_edit.setPlaceholderText("keep")
        self.controller_cfg_p2_edit.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"(0|[1-9][0-9]{0,9})"), self)
        )
        self.controller_cfg_p2_edit.setToolTip("Override controller config index for P2 (uint32). Leave blank to keep.")

        settings_layout.addWidget(QLabel("Sound volume:"), 0, 0)
        settings_layout.addWidget(self.sound_volume_edit, 0, 1)
        settings_layout.addWidget(QLabel("Music volume:"), 0, 2)
        settings_layout.addWidget(self.music_volume_edit, 0, 3)

        settings_layout.addWidget(QLabel("Invert Y (Walker) (P1):"), 1, 0)
        settings_layout.addWidget(self.invert_y_p1_combo, 1, 1)
        settings_layout.addWidget(QLabel("Invert Y (Walker) (P2):"), 1, 2)
        settings_layout.addWidget(self.invert_y_p2_combo, 1, 3)

        settings_layout.addWidget(QLabel("Invert Y (Flight) (P1):"), 2, 0)
        settings_layout.addWidget(self.invert_flight_p1_combo, 2, 1)
        settings_layout.addWidget(QLabel("Invert Y (Flight) (P2):"), 2, 2)
        settings_layout.addWidget(self.invert_flight_p2_combo, 2, 3)

        settings_layout.addWidget(QLabel("Ctrl cfg (P1):"), 3, 0)
        settings_layout.addWidget(self.controller_cfg_p1_edit, 3, 1)
        settings_layout.addWidget(QLabel("Ctrl cfg (P2):"), 3, 2)
        settings_layout.addWidget(self.controller_cfg_p2_edit, 3, 3)

        settings_layout.addWidget(QLabel("Controller Vibration (P1):"), 4, 0)
        settings_layout.addWidget(self.vibration_p1_combo, 4, 1)
        settings_layout.addWidget(QLabel("Controller Vibration (P2):"), 4, 2)
        settings_layout.addWidget(self.vibration_p2_combo, 4, 3)

        advanced_content_layout.addWidget(settings_group, 3, 0, 1, 4)

        # Options entries + tail snapshot copy (raw byte copy)
        options_copy_group = QGroupBox("Copy Controls/Options From File (optional)")
        options_copy_layout = QGridLayout(options_copy_group)

        self.copy_options_from_edit = QLineEdit()
        self.copy_options_from_edit.setPlaceholderText("keep (no copy)")
        self.copy_options_from_edit.setReadOnly(True)
        self.copy_options_from_edit.setToolTip(
            "Optional. Copy persisted control bindings (options entries) and/or the 0x56-byte tail snapshot "
            "from another .bes/.bea file. Useful for syncing keybinds, mouse sensitivity, screen shape, etc."
        )

        browse_copy_btn = QPushButton("Browse...")
        browse_copy_btn.clicked.connect(self._browse_copy_options_from)

        clear_copy_btn = QPushButton("Clear")
        clear_copy_btn.clicked.connect(self._clear_copy_options_from)

        options_copy_layout.addWidget(QLabel("Source file:"), 0, 0)
        options_copy_layout.addWidget(self.copy_options_from_edit, 0, 1, 1, 2)
        options_copy_layout.addWidget(browse_copy_btn, 0, 3)
        options_copy_layout.addWidget(clear_copy_btn, 0, 4)

        self.copy_options_entries_check = QCheckBox("Copy keybind entries (action bindings)")
        self.copy_options_entries_check.setChecked(False)
        self.copy_options_entries_check.setToolTip(
            "Copies action-binding entries (movement, look, zoom, fire, etc.) from the source file."
        )
        self.copy_options_tail_check = QCheckBox("Copy global settings snapshot (mouse/device/screen)")
        self.copy_options_tail_check.setChecked(False)
        self.copy_options_tail_check.setToolTip(
            "Copies global settings snapshot values (mouse sensitivity, screen shape, D3D device index, and related settings)."
        )

        options_copy_layout.addWidget(self.copy_options_entries_check, 1, 0, 1, 3)
        options_copy_layout.addWidget(self.copy_options_tail_check, 1, 3, 1, 2)

        hint = QLabel(
            "Note: Steam build loads these options from defaultoptions.bea at boot. "
            "Copying into a .bes save does not apply immediately; next-boot behavior can come from "
            "load/save sync into defaultoptions.bea or direct defaultoptions patching."
        )
        hint.setStyleSheet("color: #666; font-size: 11px;")
        hint.setWordWrap(True)
        options_copy_layout.addWidget(hint, 2, 0, 1, 5)

        advanced_content_layout.addWidget(options_copy_group, 4, 0, 1, 4)

        # Keybind overrides (options entries)
        # NOTE: Steam build loads bindings from defaultoptions.bea at boot. Patching a .bes may not apply at runtime
        # until restart, but load/save frontend flows can still sync buffers into defaultoptions.bea for next boot.
        keybind_group = QGroupBox("Keybind Overrides (Options Entries)")
        keybind_layout = QGridLayout(keybind_group)

        def _kb_edit() -> QLineEdit:
            e = QLineEdit()
            e.setPlaceholderText("keep")
            e.setToolTip(
                "Leave blank/keep to preserve.\n"
                "Keyboard examples: A, Key A, Num7, Up, Tab, Space, CapsLock, RShift, RControl, Key -, Key =\n"
                "Special: Look rows accept 'Mouse' (mouse axis). Zoom rows accept MouseWheelUp/MouseWheelDown.\n"
                "Mouse buttons: Fire weapon accepts MouseLeft. Select weapon accepts MouseRight."
            )
            e.setProperty("base_tooltip", e.toolTip())
            return e

        load_btn = QPushButton("Load From Main Input")
        load_btn.setToolTip(
            "Populate the fields below from the main Input File (effective P1/P2).\n"
            "Columns map directly as slot0->Player 1 and slot1->Player 2."
        )
        load_btn.clicked.connect(self._load_keybind_overrides_from_input)

        load_copy_btn = QPushButton("Load From Copy Source")
        load_copy_btn.setToolTip(
            "Populate the fields below from the Copy Controls/Options source file (if set).\n"
            "This is useful if you plan to copy options from one file and then tweak a few bindings via overrides."
        )
        load_copy_btn.clicked.connect(self._load_keybind_overrides_from_copy_source)
        self.load_copy_keybinds_btn = load_copy_btn

        clear_btn = QPushButton("Clear Overrides")
        clear_btn.setToolTip("Clear all keybind override fields (leave blank/keep to preserve existing).")
        clear_btn.clicked.connect(self._clear_keybind_overrides)

        btn_row = QHBoxLayout()
        btn_row.addWidget(load_btn)
        btn_row.addWidget(load_copy_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch(1)
        keybind_layout.addLayout(btn_row, 0, 0, 1, 3)

        keybind_layout.addWidget(QLabel("Action"), 1, 0)
        keybind_layout.addWidget(QLabel("P1"), 1, 1)
        keybind_layout.addWidget(QLabel("P2"), 1, 2)

        self.keybind_fields = {}

        def _add_kb_row(row: int, key: str, label: str) -> None:
            p1 = _kb_edit()
            p2 = _kb_edit()
            keybind_layout.addWidget(QLabel(label), row, 0)
            keybind_layout.addWidget(p1, row, 1)
            keybind_layout.addWidget(p2, row, 2)
            self.keybind_fields[key] = (p1, p2)

        r = 2
        _add_kb_row(r, "move_forward", "Movement: Forward"); r += 1
        _add_kb_row(r, "move_backward", "Movement: Backward"); r += 1
        _add_kb_row(r, "move_left", "Movement: Left"); r += 1
        _add_kb_row(r, "move_right", "Movement: Right"); r += 1
        _add_kb_row(r, "look_up", "Look: Up"); r += 1
        _add_kb_row(r, "look_down", "Look: Down"); r += 1
        _add_kb_row(r, "look_left", "Look: Left"); r += 1
        _add_kb_row(r, "look_right", "Look: Right"); r += 1
        _add_kb_row(r, "zoom_in", "Zoom: In"); r += 1
        _add_kb_row(r, "zoom_out", "Zoom: Out"); r += 1
        _add_kb_row(r, "fire_weapon", "Others: Fire weapon"); r += 1
        _add_kb_row(r, "select_weapon", "Others: Select weapon"); r += 1
        _add_kb_row(r, "transform", "Others: Transform"); r += 1
        _add_kb_row(r, "air_brake", "Others: Air brake"); r += 1
        _add_kb_row(r, "special", "Others: Special function"); r += 1

        advanced_content_layout.addWidget(keybind_group, 5, 0, 1, 4)

        # Validate keybind fields live to prevent patching with invalid tokens.
        self._keybind_rules = {
            # Movement
            "move_forward": (0x1F, False, False, False),
            "move_backward": (0x20, False, False, False),
            "move_left": (0x1D, False, False, False),
            "move_right": (0x1E, False, False, False),
            # Look
            "look_up": (0x1A, True, False, False),
            "look_down": (0x1C, True, False, False),
            "look_left": (0x19, True, False, False),
            "look_right": (0x1B, True, False, False),
            # Zoom
            "zoom_in": (0x10, False, True, False),
            "zoom_out": (0x11, False, True, False),
            # Others
            "fire_weapon": (0x12, False, False, True),
            "select_weapon": (0x14, False, False, True),
            "transform": (0x21, False, False, False),
            "air_brake": (0x15, False, False, False),
            "special": (0x3B, False, False, False),
        }

        for action_key, (p1, p2) in self.keybind_fields.items():
            p1.textChanged.connect(lambda _t, k=action_key: self._validate_keybind_overrides(k))
            p2.textChanged.connect(lambda _t, k=action_key: self._validate_keybind_overrides(k))

        self._validate_keybind_overrides()

        # God mode hint (runtime-only)
        self.god_mode_hint = QLabel(
            "God mode is gated by a save-name cheat: B4K42 (internal) / Maladim (PC port). "
            "Retail saves persist god-mode state fields, but invincibility still appears runtime-gated."
        )
        self.god_mode_hint.setStyleSheet("color: #666; font-size: 11px;")
        self.god_mode_hint.setWordWrap(True)
        advanced_content_layout.addWidget(self.god_mode_hint, 6, 0, 1, 4)

        self.advanced_content.setVisible(False)
        advanced_layout.addWidget(self.advanced_content)

        layout.addWidget(advanced_group)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        helper = QLabel("Use Save Analyzer tab to analyze or compare files")
        helper.setStyleSheet("color: #666; font-size: 11px;")
        button_layout.addWidget(helper)
        button_layout.addStretch()

        self.patch_btn = QPushButton("Patch Configuration" if self.configuration_only else "Patch Save")
        self.patch_btn.setEnabled(False)
        self.patch_btn.clicked.connect(self._do_patch)
        self.patch_btn.setMinimumWidth(120)
        button_layout.addWidget(self.patch_btn)

        layout.addLayout(button_layout)

        # Output log
        log_group = QGroupBox("Output")
        log_layout = QVBoxLayout(log_group)
        log_header = QHBoxLayout()
        log_header.addStretch()
        self.copy_output_btn = QPushButton("Copy")
        self.copy_output_btn.clicked.connect(self._copy_output)
        log_header.addWidget(self.copy_output_btn)
        log_layout.addLayout(log_header)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)
        self._refresh_copy_options_controls()

    def _toggle_advanced(self, checked: bool):
        """Show or hide advanced overrides."""
        if hasattr(self, "advanced_content"):
            self.advanced_content.setVisible(checked)

    @staticmethod
    def _is_options_like_path(path: Optional[Path]) -> bool:
        if path is None:
            return False
        name = path.name.lower()
        return path.suffix.lower() == ".bea" or name.startswith("defaultoptions.bea")

    def _refresh_copy_options_controls(self) -> None:
        has_source = self.copy_options_from_path is not None

        if not has_source:
            # Safe baseline when no copy source is selected.
            self.copy_options_entries_check.setChecked(False)
            self.copy_options_tail_check.setChecked(False)
        elif not self._had_copy_options_source:
            # First source selection defaults mirror WPF behavior:
            # - Save mode: both copy sections remain opt-in.
            # - Configuration mode: entries enabled by default, tail remains opt-in.
            self.copy_options_entries_check.setChecked(self.configuration_only)
            self.copy_options_tail_check.setChecked(False)

        self.copy_options_entries_check.setEnabled(has_source)
        self.copy_options_tail_check.setEnabled(has_source)
        if hasattr(self, "load_copy_keybinds_btn"):
            self.load_copy_keybinds_btn.setEnabled(has_source)
        self._had_copy_options_source = has_source

    def _browse_copy_options_from(self) -> None:
        start_dir = str(self.input_path.parent) if self.input_path else ""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Source Save/Options File",
            start_dir,
            "BEA Save/Options Files (*.bes *.bea);;All Files (*)",
        )
        if filename:
            self.copy_options_from_path = Path(filename)
            self.copy_options_from_edit.setText(str(self.copy_options_from_path))
            self._refresh_copy_options_controls()

    def _clear_copy_options_from(self) -> None:
        self.copy_options_from_path = None
        self.copy_options_from_edit.clear()
        self._refresh_copy_options_controls()

    def _set_options_file_mode(self, enabled: bool) -> None:
        """Toggle safety defaults when editing defaultoptions.bea-style files."""
        if self.configuration_only:
            enabled = True
        self.is_options_file = enabled

        # `defaultoptions.bea` is a global options snapshot. It shares the same 10,004-byte layout as .bes,
        # so patching career progress into it can effectively turn it into a "gold save" at boot.
        career_section_widgets = [
            self.kills_only_check,
            self.patch_nodes_check,
            self.patch_links_check,
            self.patch_goodies_check,
            self.patch_kills_check,
        ]
        for w in career_section_widgets:
            w.setEnabled(not enabled)

        if enabled:
            self.kills_only_check.setChecked(False)
            self.patch_nodes_check.setChecked(False)
            self.patch_links_check.setChecked(False)
            self.patch_goodies_check.setChecked(False)
            self.patch_kills_check.setChecked(False)

        # Patch options that only make sense for career patching.
        for w in [self.rank_combo, self.new_goodies_check, self.kill_spin, self.level_ranks_edit]:
            w.setEnabled(not enabled)
        for edit in getattr(self, "kill_edits", {}).values():
            edit.setEnabled(not enabled)

    def _on_input_selected(self, path: Path):
        """Handle input file selection from SaveSelector"""
        is_options_file = self._is_options_like_path(path)
        if self.configuration_only and not is_options_file:
            QMessageBox.warning(
                self,
                "Configuration Editor",
                "Configuration Editor only accepts .bea/defaultoptions files.",
            )
            self.input_path = None
            self.output_path = None
            self.input_valid = False
            self.output_edit.clear()
            self._update_patch_button()
            return
        if not self.configuration_only and is_options_file:
            QMessageBox.warning(
                self,
                "Save Editor",
                "Save Editor expects a .bes career save file.\nUse Configuration Editor for .bea/defaultoptions files.",
            )
            self.input_path = None
            self.output_path = None
            self.input_valid = False
            self.output_edit.clear()
            self._set_options_file_mode(False)
            self._update_patch_button()
            return

        self.input_path = path
        self.input_valid = False
        self._set_options_file_mode(is_options_file)

        # Validate file format (size + version word)
        try:
            size = path.stat().st_size
            version_ok = False
            if size == BES_FILE_SIZE:
                with path.open('rb') as f:
                    header = f.read(2)
                version_ok = len(header) == 2 and int.from_bytes(header, 'little') == 0x4BD1
            if size == BES_FILE_SIZE and version_ok:
                self.input_valid = True
            else:
                self._log(
                    f"Warning: File is not a valid BEA save/options file "
                    f"(size {size} bytes, expected {BES_FILE_SIZE}, version 0x4BD1)."
                )
                QMessageBox.warning(
                    self, "Invalid File",
                    f"File is not a valid BEA save/options file.\n"
                    f"Size: {size} (expected {BES_FILE_SIZE})\n"
                    "Expected version word: 0x4BD1"
                )
        except Exception:
            pass

        # Auto-suggest output filename.
        # Configuration mode defaults to safe in-place flow (with .bak backup during patch).
        if self.configuration_only and is_options_file:
            suggested = path
        else:
            suggested = path.parent / f"{path.stem}_patched{path.suffix}"
        self.output_path = suggested
        self.output_edit.setText(str(suggested))
        if is_options_file:
            self._log("Note: defaultoptions.bea detected. Career patch sections were disabled to avoid corrupting the global options file.")
        self._update_patch_button()

    def _on_input_cleared(self) -> None:
        """Handle input selection clear from SaveSelector placeholder."""
        self.input_path = None
        self.input_valid = False
        self._set_options_file_mode(False)
        self._update_patch_button()

    def _on_game_dir_changed(self, path: Path):
        """Propagate game directory changes to the main window."""
        self.gameDirChanged.emit(path)

    def _browse_output(self):
        """Browse for output .bes file"""
        start_dir = str(self.output_path.parent) if self.output_path else ""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Patched Output File",
            str(self.output_path) if self.output_path else "",
            "BEA Options Files (*.bea);;All Files (*)" if self.configuration_only else "BEA Career Saves (*.bes);;All Files (*)"
        )
        if filename:
            chosen = Path(filename)
            if self.configuration_only and not self._is_options_like_path(chosen):
                QMessageBox.warning(self, "Configuration Editor", "Output path must be a .bea options file in Configuration Editor.")
                return
            if not self.configuration_only and self._is_options_like_path(chosen):
                QMessageBox.warning(self, "Save Editor", "Save Editor output should be a .bes career save file.")
                return
            self.output_path = chosen
            self.output_edit.setText(filename)
            self._update_patch_button()

    def _update_patch_button(self):
        """Enable patch button only when both files are selected"""
        if not hasattr(self, "patch_btn"):
            return
        same_path = False
        if self.input_path is not None and self.output_path is not None:
            try:
                same_path = self.input_path.resolve() == self.output_path.resolve()
            except Exception:
                same_path = False
        mode_path_valid = True
        if self.configuration_only and self.input_path is not None and self.output_path is not None:
            mode_path_valid = (
                self._is_options_like_path(self.input_path) and
                self._is_options_like_path(self.output_path)
            )
        if (not self.configuration_only) and self.input_path is not None and self.output_path is not None:
            mode_path_valid = (
                self.input_path.suffix.lower() == ".bes" and
                self.output_path.suffix.lower() == ".bes"
            )
        same_path_blocked = same_path and (not self.configuration_only)
        self.patch_btn.setEnabled(
            self.input_path is not None and
            self.output_path is not None and
            self.input_valid and
            self._keybind_overrides_valid and
            not same_path_blocked and
            mode_path_valid
        )

    def _validate_keybind_overrides(self, _changed_key: Optional[str] = None) -> None:
        """Validate per-action keybind tokens and mark invalid fields."""
        def _is_keep_or_blank(s: str) -> bool:
            t = (s or "").strip()
            return t == "" or t.lower() in ("keep", "preserve", "unchanged")

        def _is_valid_look_token(t: str) -> bool:
            tl = t.strip().lower()
            if tl in ("mouse", "mousex", "mousey", "mousex+", "mousex-", "mousey+", "mousey-"):
                return True
            if tl.startswith("mouse(") and tl.endswith(")"):
                inner = tl[len("mouse("):-1]
                try:
                    int(inner)
                    return True
                except ValueError:
                    return False
            return False

        def _validate_token(entry_id: int, allow_look_mouse: bool, allow_zoom_wheel: bool, allow_mouse_buttons: bool, raw: str) -> tuple[bool, str]:
            if _is_keep_or_blank(raw):
                return True, ""
            t = raw.strip()
            tl = t.lower()

            if allow_look_mouse and tl.startswith("mouse"):
                if _is_valid_look_token(t):
                    return True, ""
                return False, "Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key."

            if allow_zoom_wheel and tl in ("mousewheelup", "mousewheeldown"):
                return True, ""

            if allow_mouse_buttons and tl in ("mouseleft", "mouseright"):
                if tl == "mouseleft":
                    if entry_id in (0x12, 0x13):
                        return True, ""
                    return False, "MouseLeft is only supported for Others: Fire weapon."
                if tl == "mouseright":
                    if entry_id == 0x14:
                        return True, ""
                    return False, "MouseRight is only supported for Others: Select weapon."
                return False, "Use MouseLeft/MouseRight."

            try:
                from patcher import parse_keyboard_packed_key
                parse_keyboard_packed_key(t)
                return True, ""
            except Exception as e:
                return False, str(e) or "Invalid key token."

        invalid = False
        for action_key, (p1_edit, p2_edit) in self.keybind_fields.items():
            entry_id, allow_look_mouse, allow_zoom_wheel, allow_mouse_buttons = self._keybind_rules.get(action_key, (0, False, False, False))
            for edit in (p1_edit, p2_edit):
                raw = edit.text()
                ok, err = _validate_token(entry_id, allow_look_mouse, allow_zoom_wheel, allow_mouse_buttons, raw)
                base_tt = edit.property("base_tooltip") or edit.toolTip()
                if ok:
                    edit.setStyleSheet("")
                    edit.setToolTip(base_tt)
                else:
                    invalid = True
                    edit.setStyleSheet("border: 2px solid #cc0000; background: #fff0f0;")
                    edit.setToolTip(f"{base_tt}\nInvalid: {err}")

        self._keybind_overrides_valid = not invalid
        self._update_patch_button()

    def _toggle_kills_only(self, enabled: bool):
        """Toggle kills-only mode, mirroring WPF behavior"""
        if enabled:
            self._kills_only_restore_nodes = self.patch_nodes_check.isChecked()
            self._kills_only_restore_links = self.patch_links_check.isChecked()
            self._kills_only_restore_goodies = self.patch_goodies_check.isChecked()
            self._kills_only_restore_kills = self.patch_kills_check.isChecked()
            self._kills_only_restore_captured = True
            self.patch_nodes_check.setChecked(False)
            self.patch_links_check.setChecked(False)
            self.patch_goodies_check.setChecked(False)
            self.patch_kills_check.setChecked(True)
        else:
            self.patch_nodes_check.setChecked(self._kills_only_restore_nodes if self._kills_only_restore_captured else True)
            self.patch_links_check.setChecked(self._kills_only_restore_links if self._kills_only_restore_captured else True)
            self.patch_goodies_check.setChecked(self._kills_only_restore_goodies if self._kills_only_restore_captured else True)
            self.patch_kills_check.setChecked(self._kills_only_restore_kills if self._kills_only_restore_captured else True)

        self.patch_nodes_check.setEnabled(not enabled)
        self.patch_links_check.setEnabled(not enabled)
        self.patch_goodies_check.setEnabled(not enabled)
        self.patch_kills_check.setEnabled(not enabled)

    def _parse_level_ranks(self) -> Optional[dict]:
        """Parse per-level rank overrides (1-43) into a dict."""
        text = self.level_ranks_edit.text().strip()
        if not text:
            return None

        result = {}
        pairs = [p for p in text.replace(';', ',').split(',') if p.strip()]
        for pair in pairs:
            parts = pair.strip().split(':')
            if len(parts) != 2:
                continue
            try:
                level = int(parts[0].strip())
            except ValueError:
                continue
            if level < 1 or level > NUM_LEVELS:
                continue
            rank = parts[1].strip().upper()
            if rank in RANK_VALUES:
                # UI input is 1-based (1..43). patch_file expects zero-based node indexes.
                result[level - 1] = rank

        return result if result else None

    def _clear_keybind_overrides(self) -> None:
        if not hasattr(self, "keybind_fields"):
            return
        for p1, p2 in self.keybind_fields.values():
            p1.clear()
            p2.clear()
        self._log("Cleared keybind override fields.")

    def _load_keybind_overrides_from_input(self) -> None:
        if not self.input_path:
            QMessageBox.warning(self, "No Input File", "Select an input .bes/.bea file first.")
            return
        self._load_keybind_overrides_from_path(self.input_path, "main input")

    def _load_keybind_overrides_from_copy_source(self) -> None:
        if not self.copy_options_from_path:
            QMessageBox.warning(self, "No Copy Source", "Set 'Copy Controls/Options From File' first.")
            return
        self._load_keybind_overrides_from_path(self.copy_options_from_path, "copy source")

    def _load_keybind_overrides_from_path(self, path: Path, label: str) -> None:
        if not path.exists():
            QMessageBox.warning(self, "File Missing", f"{label.capitalize()} file not found: {path}")
            return

        try:
            data = path.read_bytes()
        except Exception as e:
            QMessageBox.warning(self, "Read Failed", f"Failed to read {label} file:\n{e}")
            return

        if len(data) != BES_FILE_SIZE:
            QMessageBox.warning(
                self,
                "Invalid File",
                f"Unexpected file size: {len(data)} bytes (expected {BES_FILE_SIZE}).",
            )
            return
        version = int.from_bytes(data[:2], 'little') if len(data) >= 2 else None
        if version != 0x4BD1:
            QMessageBox.warning(
                self,
                "Invalid File",
                f"Unexpected version word: 0x{(version or 0):04X} (expected 0x4BD1).",
            )
            return

        try:
            bindings = self._decode_effective_bindings_from_bytes(data)
        except Exception as e:
            QMessageBox.warning(self, "Decode Failed", f"Failed to decode bindings:\n{e}")
            return

        if not bindings:
            QMessageBox.information(self, "No Bindings", "No active bindings entries were found in this file.")
            return

        for action_key, (p1_edit, p2_edit) in self.keybind_fields.items():
            b = bindings.get(action_key)
            if b is None:
                continue
            p1_edit.setText(b[0])
            p2_edit.setText(b[1])

        self._log(
            f"Loaded keybind fields from {label} file. "
            "Columns map slot0->Player 1 and slot1->Player 2."
        )

    def _decode_effective_bindings_from_bytes(self, data: bytes) -> dict[str, tuple[str, str]]:
        """
        Decode the options entries block (0x24BE) and normalize to effective P1/P2 columns.

        Steam build nuance:
        - ControlSchemeIndex==0: slot0/slot1 correspond to UI columns (P1/P2).
        - ControlSchemeIndex==1: preset scheme detected; values are still shown as raw slot0/slot1.
        """
        options_start = OFFSET_OPTIONS_ENTRIES
        entry_size = 0x20
        base_size = options_start + OPTIONS_TAIL_SIZE  # 0x2514

        if len(data) < base_size:
            return {}
        extra = len(data) - base_size
        if extra % entry_size != 0:
            return {}
        n = extra // entry_size

        tail_start = options_start + entry_size * n
        scheme_index = struct.unpack_from("<H", data, tail_start + 0x08)[0]

        # entry_id -> (slot0_dev, slot0_key, slot1_dev, slot1_key)
        entries: dict[int, tuple[int, int, int, int]] = {}
        for i in range(n):
            off = options_start + entry_size * i
            active = struct.unpack_from("<I", data, off + 0x00)[0] & 0xFF
            if active == 0:
                continue
            entry_id = struct.unpack_from("<i", data, off + 0x04)[0]
            if entry_id < 0:
                continue
            s0_dev = struct.unpack_from("<I", data, off + 0x0C)[0]
            s0_key = struct.unpack_from("<I", data, off + 0x10)[0]
            s1_dev = struct.unpack_from("<I", data, off + 0x18)[0]
            s1_key = struct.unpack_from("<I", data, off + 0x1C)[0]
            entries[entry_id] = (s0_dev, s0_key, s1_dev, s1_key)

        if not entries:
            return {}

        # Known entry IDs for the UI rows we expose.
        action_to_entry_id = {
            "move_forward": 0x1F,
            "move_backward": 0x20,
            "move_left": 0x1D,
            "move_right": 0x1E,
            "look_up": 0x1A,
            "look_down": 0x1C,
            "look_left": 0x19,
            "look_right": 0x1B,
            "zoom_in": 0x10,
            "zoom_out": 0x11,
            "fire_weapon": 0x12,  # paired with 0x13 in-game; fallback if 0x12 is absent
            "select_weapon": 0x14,
            "transform": 0x21,
            "air_brake": 0x15,
            "special": 0x3B,
        }
        # Reverse maps for nicer tokens that round-trip through patcher.py parsing.
        key_name_map = {
            (0, 0x00C8): "Up",
            (0, 0x00D0): "Down",
            (0, 0x00CB): "Left",
            (0, 0x00CD): "Right",
            (0, 0x000F): "Tab",
            (ord(" "), 0x0039): "Space",
            (0, 0x003A): "CapsLock",
            (0, 0x002A): "LShift",
            (0, 0x0036): "RShift",
            (0, 0x009D): "RControl",
            (0, 0x000C): "Key -",
            (0, 0x000D): "Key =",
        }
        numpad_scan_to_digit = {
            0x0047: "7", 0x0048: "8", 0x0049: "9",
            0x004B: "4", 0x004C: "5", 0x004D: "6",
            0x004F: "1", 0x0050: "2", 0x0051: "3",
            0x0052: "0",
        }

        def fmt_binding(device_code: int, packed_key: int) -> str:
            vk = (packed_key >> 16) & 0xFFFF
            scan = packed_key & 0xFFFF

            # Mouse look axes (explicit tokens match patcher.py parsing)
            if device_code in (11, 12):
                axis = "MouseX" if scan == 0 else ("MouseY" if scan == 1 else "MouseAxis")
                if axis == "MouseAxis":
                    return f"Mouse({scan})"
                return f"{axis}{'+' if device_code == 11 else '-'}"

            # Mouse wheel / RMB (Zoom, Select weapon)
            if device_code == 16:
                if scan == 3:
                    return "MouseWheelUp"
                if scan == 4:
                    return "MouseWheelDown"
                if scan == 2:
                    return "MouseRight"
                return f"Mouse({scan})"

            # Mouse left button (Fire weapon)
            if device_code in (15, 17) and vk == 0 and scan == 0:
                return "MouseLeft"

            if packed_key == 0:
                return "-"

            # Numpad digits: preserve DIK scan-based distinction
            if scan in numpad_scan_to_digit and 0x30 <= vk <= 0x39:
                return f"Num{numpad_scan_to_digit[scan]}"

            # Named special keys (arrows, shift, tab, etc)
            name = key_name_map.get((vk, scan))
            if name is not None:
                return name

            # Printable ASCII (letters/digits/punct)
            if vk != 0 and 0x20 <= vk <= 0x7E:
                return chr(vk)

            return f"vk=0x{vk:04X} scan=0x{scan:04X}"

        out: dict[str, tuple[str, str]] = {}
        for action_key, entry_id in action_to_entry_id.items():
            if action_key == "fire_weapon":
                e = entries.get(0x12) or entries.get(0x13)
            else:
                e = entries.get(entry_id)
            if e is None:
                continue
            s0_dev, s0_key, s1_dev, s1_key = e
            out[action_key] = (fmt_binding(s0_dev, s0_key), fmt_binding(s1_dev, s1_key))

        return out

    def _log(self, message: str):
        """Append message to log"""
        self.log_text.append(message)

    def _copy_output(self):
        text = self.log_text.toPlainText()
        if not text.strip():
            return
        self.log_text.selectAll()
        self.log_text.copy()

    def _do_patch(self):
        """Perform the patch operation"""
        if not self.input_path or not self.output_path:
            return

        if not self.input_path.exists():
            QMessageBox.warning(self, "Error", f"Input file not found: {self.input_path}")
            return

        if self.configuration_only:
            input_options_like = self._is_options_like_path(self.input_path)
            output_options_like = self._is_options_like_path(self.output_path)
            if not input_options_like or not output_options_like:
                QMessageBox.warning(self, "Configuration Editor", "Configuration Editor requires .bea input and output files.")
                return
        else:
            if self._is_options_like_path(self.input_path) or self._is_options_like_path(self.output_path):
                QMessageBox.warning(
                    self,
                    "Save Editor",
                    "Save Editor only patches .bes career files.\nUse Configuration Editor for .bea/defaultoptions files.",
                )
                return

        config_in_place = False
        patch_output_path = self.output_path
        backup_path: Optional[Path] = None
        same_path = False
        try:
            same_path = self.input_path.resolve() == self.output_path.resolve()
        except Exception:
            same_path = False

        if same_path and not self.configuration_only:
            QMessageBox.warning(self, "Invalid Output", "Output file must be different from input file (in-place patching is blocked).")
            return

        if same_path and self.configuration_only:
            answer = QMessageBox.question(
                self,
                "Confirm In-Place Configuration Patch",
                "Configuration Editor is set to patch in place.\n\n"
                "The current options file will be backed up to a timestamped `.bak` file first.\n"
                "Then the patched file will replace the original path.\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self._log("Patch canceled by user: in-place configuration patch not confirmed.")
                return

            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            patch_output_path = self.output_path.with_name(
                f"{self.output_path.stem}.tmp_patch_{stamp}{self.output_path.suffix}"
            )
            i = 0
            while patch_output_path.exists():
                i += 1
                patch_output_path = self.output_path.with_name(
                    f"{self.output_path.stem}.tmp_patch_{stamp}_{i}{self.output_path.suffix}"
                )
            config_in_place = True
        elif self.output_path.exists():
            overwrite = QMessageBox.question(
                self,
                "Confirm Overwrite",
                f"Output file already exists:\n{self.output_path}\n\nOverwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if overwrite != QMessageBox.StandardButton.Yes:
                self._log("Patch canceled by user: overwrite not confirmed.")
                return

        # Import patcher functions
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from patcher import patch_file, KILL_AIRCRAFT, KILL_VEHICLES, KILL_EMPLACEMENTS, KILL_INFANTRY, KILL_MECHS
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Failed to import patcher: {e}")
            return

        # Gather options
        rank = self.rank_combo.currentText()
        new_goodies = self.new_goodies_check.isChecked()
        kill_count = self.kill_spin.value()

        # Per-category kills (optional overrides)
        per_category_kills = {}
        key_map = {
            'aircraft': KILL_AIRCRAFT,
            'vehicles': KILL_VEHICLES,
            'emplacements': KILL_EMPLACEMENTS,
            'infantry': KILL_INFANTRY,
            'mechs': KILL_MECHS,
        }
        for key, const in key_map.items():
            text = self.kill_edits[key].text().strip()
            if text:
                per_category_kills[const] = int(text)
        if not per_category_kills:
            per_category_kills = None

        # Selective patching
        patch_nodes = self.patch_nodes_check.isChecked()
        patch_links = self.patch_links_check.isChecked()
        patch_goodies = self.patch_goodies_check.isChecked()
        patch_kills = self.patch_kills_check.isChecked()

        level_ranks = self._parse_level_ranks()

        def parse_optional_float01(edit: QLineEdit, label: str) -> Optional[float]:
            text = edit.text().strip()
            if not text:
                return None
            try:
                v = float(text)
            except ValueError:
                raise ValueError(f"{label}: expected a number in range 0.0-1.0")
            if v < 0.0 or v > 1.0:
                raise ValueError(f"{label}: expected a number in range 0.0-1.0")
            return v

        def parse_keep_on_off(combo: QComboBox) -> Optional[bool]:
            v = combo.currentText()
            if v == "Keep":
                return None
            if v == "On":
                return True
            if v == "Off":
                return False
            return None

        def parse_optional_uint32(edit: QLineEdit, label: str) -> Optional[int]:
            text = edit.text().strip()
            if not text:
                return None
            v = int(text)
            if v < 0 or v > 0xFFFFFFFF:
                raise ValueError(f"{label}: expected 0..4294967295")
            return v

        try:
            sound_volume = parse_optional_float01(self.sound_volume_edit, "Sound volume")
            music_volume = parse_optional_float01(self.music_volume_edit, "Music volume")
            invert_y_p1 = parse_keep_on_off(self.invert_y_p1_combo)
            invert_y_p2 = parse_keep_on_off(self.invert_y_p2_combo)
            invert_flight_p1 = parse_keep_on_off(self.invert_flight_p1_combo)
            invert_flight_p2 = parse_keep_on_off(self.invert_flight_p2_combo)
            vibration_p1 = parse_keep_on_off(self.vibration_p1_combo)
            vibration_p2 = parse_keep_on_off(self.vibration_p2_combo)
            controller_cfg_p1 = parse_optional_uint32(self.controller_cfg_p1_edit, "Ctrl cfg (P1)")
            controller_cfg_p2 = parse_optional_uint32(self.controller_cfg_p2_edit, "Ctrl cfg (P2)")
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

        copy_options_from = self.copy_options_from_path
        copy_options_entries = self.copy_options_entries_check.isChecked()
        copy_options_tail = self.copy_options_tail_check.isChecked()

        # Keybind overrides (options entries)
        options_entry_overrides = None
        try:
            from patcher import (
                OptionsEntryOverride,
                parse_keyboard_packed_key,
            )

            def _is_empty_kb(s: Optional[str]) -> bool:
                if s is None:
                    return True
                t = s.strip()
                return t == "" or t.lower() in ("keep", "preserve", "unchanged")

            def _set_slot(overrides: dict[int, OptionsEntryOverride], entry_id: int, slot_index: int, device_code: int, packed_key: int) -> None:
                ov = overrides.get(entry_id)
                if ov is None:
                    ov = OptionsEntryOverride()
                    overrides[entry_id] = ov
                slot = ov.slot0 if slot_index == 0 else ov.slot1
                slot.device_code = device_code
                slot.packed_key = packed_key

            def _parse_look_mouse(entry_id: int) -> tuple[int, int]:
                # Steam preset uses:
                # - device 11: positive direction, device 12: negative direction
                # - packed_key scan: 0 => X axis, 1 => Y axis
                return {
                    0x1B: (11, 0),  # Look Right (MouseX+)
                    0x19: (12, 0),  # Look Left  (MouseX-)
                    0x1A: (11, 1),  # Look Up    (MouseY+)
                    0x1C: (12, 1),  # Look Down  (MouseY-)
                }[entry_id]

            def _parse_look_token(entry_id: int, token: str) -> tuple[int, int]:
                # Accept simple "Mouse" and explicit tokens that match analyzer output.
                t = token.strip()
                tl = t.lower()
                if tl in ("mouse", "mousex", "mousey"):
                    return _parse_look_mouse(entry_id)
                if tl.startswith("mousex"):
                    key = 0
                    if tl.endswith("-"):
                        return 12, key
                    if tl.endswith("+"):
                        return 11, key
                    return _parse_look_mouse(entry_id)
                if tl.startswith("mousey"):
                    key = 1
                    if tl.endswith("-"):
                        return 12, key
                    if tl.endswith("+"):
                        return 11, key
                    return _parse_look_mouse(entry_id)
                if tl.startswith("mouse(") and tl.endswith(")"):
                    inner = tl[len("mouse("):-1]
                    try:
                        scan_signed = int(inner, 10)
                    except ValueError:
                        scan_signed = None
                    if scan_signed is not None:
                        dev_default, _ = _parse_look_mouse(entry_id)
                        return dev_default, scan_signed & 0xFFFFFFFF
                raise ValueError(
                    f"Invalid look binding '{token}'. Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key."
                )

            def _parse_zoom_wheel(token: str) -> tuple[int, int]:
                if token.lower() == "mousewheelup":
                    return 16, 3
                if token.lower() == "mousewheeldown":
                    return 16, 4
                raise ValueError(f"Invalid zoom binding '{token}'. Use MouseWheelUp/MouseWheelDown or a keyboard key.")

            def _parse_mouse_button(entry_id: int, token: str) -> tuple[int, int]:
                if token.lower() == "mouseleft":
                    if entry_id == 0x12:
                        return 17, 0
                    if entry_id == 0x13:
                        return 15, 0
                    raise ValueError("MouseLeft is only supported for Fire weapon (entry 0x12/0x13).")
                if token.lower() == "mouseright":
                    if entry_id == 0x14:
                        return 16, 2
                    raise ValueError("MouseRight is only supported for Select weapon (entry 0x14).")
                raise ValueError(f"Invalid mouse binding '{token}'. Use MouseLeft/MouseRight.")

            def _parse_row(
                overrides: dict[int, OptionsEntryOverride],
                entry_id: int,
                keyboard_device_code: int,
                allow_look_mouse: bool,
                allow_zoom_wheel: bool,
                allow_mouse_buttons: bool,
                p1: Optional[str],
                p2: Optional[str],
            ) -> None:
                def _apply(slot_index: int, raw: str) -> None:
                    t = raw.strip()
                    if allow_look_mouse and t.lower().startswith("mouse"):
                        dev, key = _parse_look_token(entry_id, t)
                        _set_slot(overrides, entry_id, slot_index, dev, key)
                        return
                    if allow_zoom_wheel and t.lower() in ("mousewheelup", "mousewheeldown"):
                        dev, key = _parse_zoom_wheel(t)
                        _set_slot(overrides, entry_id, slot_index, dev, key)
                        return
                    if allow_mouse_buttons and t.lower() in ("mouseleft", "mouseright"):
                        dev, key = _parse_mouse_button(entry_id, t)
                        _set_slot(overrides, entry_id, slot_index, dev, key)
                        return
                    dev, key = keyboard_device_code, parse_keyboard_packed_key(t)
                    _set_slot(overrides, entry_id, slot_index, dev, key)

                if not _is_empty_kb(p1):
                    _apply(0, p1 or "")
                if not _is_empty_kb(p2):
                    _apply(1, p2 or "")

            # Map GUI keys -> entry ids (see reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md)
            overrides: dict[int, OptionsEntryOverride] = {}
            kb = self.keybind_fields

            def _get_pair(k: str) -> tuple[Optional[str], Optional[str]]:
                p1, p2 = kb[k]
                return p1.text(), p2.text()

            # Movement (entry_id 0x1D..0x20)
            p1, p2 = _get_pair("move_forward")
            _parse_row(overrides, 0x1F, 9, False, False, False, p1, p2)
            p1, p2 = _get_pair("move_backward")
            _parse_row(overrides, 0x20, 9, False, False, False, p1, p2)
            p1, p2 = _get_pair("move_left")
            _parse_row(overrides, 0x1D, 9, False, False, False, p1, p2)
            p1, p2 = _get_pair("move_right")
            _parse_row(overrides, 0x1E, 9, False, False, False, p1, p2)

            # Look (entry_id 0x19..0x1C). Allow 'Mouse' token.
            p1, p2 = _get_pair("look_up")
            _parse_row(overrides, 0x1A, 9, True, False, False, p1, p2)
            p1, p2 = _get_pair("look_down")
            _parse_row(overrides, 0x1C, 9, True, False, False, p1, p2)
            p1, p2 = _get_pair("look_left")
            _parse_row(overrides, 0x19, 9, True, False, False, p1, p2)
            p1, p2 = _get_pair("look_right")
            _parse_row(overrides, 0x1B, 9, True, False, False, p1, p2)

            # Zoom (entry_id 0x10/0x11). Allow MouseWheelUp/Down tokens.
            p1, p2 = _get_pair("zoom_in")
            _parse_row(overrides, 0x10, 9, False, True, False, p1, p2)
            p1, p2 = _get_pair("zoom_out")
            _parse_row(overrides, 0x11, 9, False, True, False, p1, p2)

            # Others:
            # Fire weapon maps to two entries (0x12/0x13). Update both if either side is overridden.
            p1, p2 = _get_pair("fire_weapon")
            if not _is_empty_kb(p1) or not _is_empty_kb(p2):
                _parse_row(overrides, 0x12, 10, False, False, True, p1, p2)
                _parse_row(overrides, 0x13, 9, False, False, True, p1, p2)

            p1, p2 = _get_pair("select_weapon")
            _parse_row(overrides, 0x14, 10, False, False, True, p1, p2)
            p1, p2 = _get_pair("transform")
            _parse_row(overrides, 0x21, 8, False, False, False, p1, p2)
            p1, p2 = _get_pair("air_brake")
            _parse_row(overrides, 0x15, 9, False, False, False, p1, p2)
            p1, p2 = _get_pair("special")
            _parse_row(overrides, 0x3B, 8, False, False, False, p1, p2)

            if overrides:
                options_entry_overrides = overrides

        except Exception as e:
            QMessageBox.warning(self, "Invalid Keybind Override", str(e))
            return

        patch_any_section = any([patch_nodes, patch_links, patch_goodies, patch_kills])
        patch_any_settings = any([
            sound_volume is not None,
            music_volume is not None,
            invert_y_p1 is not None,
            invert_y_p2 is not None,
            invert_flight_p1 is not None,
            invert_flight_p2 is not None,
            vibration_p1 is not None,
            vibration_p2 is not None,
            controller_cfg_p1 is not None,
            controller_cfg_p2 is not None,
            copy_options_from is not None,
            options_entry_overrides is not None,
        ])

        if not patch_any_section and not patch_any_settings:
            QMessageBox.warning(self, "Warning", "No sections or settings selected for patching!")
            return

        input_options_like = self._is_options_like_path(self.input_path)
        output_options_like = self._is_options_like_path(self.output_path)
        if (input_options_like or output_options_like) and patch_any_section:
            answer = QMessageBox.question(
                self,
                "Confirm Options-File Career Patch",
                "Career sections (missions/links/goodies/kills) are enabled while input or output is .bea/defaultoptions.\n\n"
                "This can push career progression data into global options snapshots.\n\nContinue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self._log("Patch canceled by user: options-file safety confirmation declined.")
                return

        self._log(f"Patching: {self.input_path.name}")

        try:
            patch_file(
                self.input_path,
                patch_output_path,
                new_goodies=new_goodies,
                kill_count=kill_count,
                rank=rank,
                level_ranks=level_ranks,
                per_category_kills=per_category_kills,
                patch_nodes=patch_nodes,
                patch_links=patch_links,
                patch_goodies=patch_goodies,
                patch_kills=patch_kills,
                sound_volume=sound_volume,
                music_volume=music_volume,
                invert_y_p1=invert_y_p1,
                invert_y_p2=invert_y_p2,
                invert_flight_p1=invert_flight_p1,
                invert_flight_p2=invert_flight_p2,
                vibration_p1=vibration_p1,
                vibration_p2=vibration_p2,
                controller_config_p1=controller_cfg_p1,
                controller_config_p2=controller_cfg_p2,
                copy_options_from=copy_options_from,
                copy_options_entries=copy_options_entries,
                copy_options_tail=copy_options_tail,
                options_entry_overrides=options_entry_overrides,
            )

            if config_in_place:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.output_path.with_name(f"{self.output_path.name}.{stamp}.bak")
                shutil.copy2(self.output_path, backup_path)
                patch_output_path.replace(self.output_path)
                self._log(f"In-place configuration patch completed with backup: {backup_path}")

            # Build summary
            sections = []
            if patch_nodes:
                sections.append(f"Missions ({rank}-rank)")
            if patch_links:
                sections.append("Links")
            if patch_goodies:
                sections.append(f"Goodies ({'NEW' if new_goodies else 'OLD'})")
            if patch_kills:
                if per_category_kills:
                    sections.append("Kills (custom)")
                else:
                    sections.append(f"Kills ({kill_count})")

            if any([
                sound_volume is not None,
                music_volume is not None,
                invert_y_p1 is not None,
                invert_y_p2 is not None,
                invert_flight_p1 is not None,
                invert_flight_p2 is not None,
                vibration_p1 is not None,
                vibration_p2 is not None,
                controller_cfg_p1 is not None,
                controller_cfg_p2 is not None,
            ]):
                sections.append("Career settings")

            if copy_options_from is not None:
                parts = []
                if copy_options_entries:
                    parts.append("entries")
                if copy_options_tail:
                    parts.append("tail")
                if parts:
                    sections.append(f"Options copy ({'+'.join(parts)})")

            if options_entry_overrides is not None:
                sections.append("Keybind overrides")

            self._log(f"Success! Patched: {', '.join(sections)}")
            self._log(f"Output: {self.output_path}")

            mode_label = "Configuration file" if self.configuration_only else "Save file"
            QMessageBox.information(
                self, "Success",
                (
                    f"{mode_label} patched successfully!\n\nOutput: {self.output_path}"
                    + (f"\nBackup: {backup_path}" if backup_path is not None else "")
                )
            )

        except Exception as e:
            if config_in_place and patch_output_path is not None and patch_output_path.exists():
                self._log(f"Temporary patched file retained for recovery: {patch_output_path}")
            self._log(f"ERROR: {e}")
            QMessageBox.critical(self, "Error", f"Patch failed: {e}")

    def load_file(self, path: Path):
        """Load a file into the editor (called from main window)"""
        self.input_selector.set_path(path)
