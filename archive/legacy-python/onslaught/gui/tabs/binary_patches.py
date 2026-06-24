"""
Onslaught Career Editor - Binary Patches Tab
Byte-verified BEA.exe patching (verify/apply/restore).
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QCheckBox,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...core.binary_patches import (
    PATCH_SPECS,
    PATCH_CATALOG_STATUS,
    PatchSpec,
    apply_patches_to_file,
    build_backup_path,
    get_patch_spec,
    render_state_report,
    restore_from_backup,
    verify_patch_specs,
)
from ...core.config import AppConfig

class BinaryPatchesTab(QWidget):
    """GUI surface for BEA.exe byte-verified catalog patches."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resolution_spec = self._get_spec("resolution_gate", fallback_index=0)
        self.force_windowed_spec = self._get_spec("force_windowed", fallback_index=1)
        self.extra_graphics_default_on_spec = self._get_spec("extra_graphics_default_on", fallback_index=2)
        self.ignore_cardid_overrides_spec = self._get_spec("ignore_cardid_tweak_overrides", fallback_index=3)
        self.version_pointer_spec = self._get_spec("version_overlay_use_patched_format_pointer", fallback_index=4)
        self.version_cave_string_spec = self._get_spec("version_overlay_patched_format_cave_string", fallback_index=5)
        self.skip_auto_toggle_spec = self._get_spec("skip_auto_toggle", fallback_index=6)
        self._verified_signature: tuple[str, tuple[str, ...]] | None = None
        self._setup_ui()
        self.refresh_from_config(force=False)
        self._update_button_state()
        self.output_text.setPlainText(
            "Select BEA.exe, choose patches, then run Verify Selected before applying.\n"
            f"Catalog: {PATCH_CATALOG_STATUS}"
        )

    @staticmethod
    def _get_spec(key: str, fallback_index: int) -> PatchSpec:
        direct = get_patch_spec(key)
        if direct is not None:
            return direct
        if 0 <= fallback_index < len(PATCH_SPECS):
            return PATCH_SPECS[fallback_index]
        return PATCH_SPECS[0]

    @staticmethod
    def _format_patch_label(spec: PatchSpec) -> str:
        track = "Stable" if spec.track.lower() == "stable" else "Experimental"
        if spec.optional:
            return f"{track} (optional): {spec.display_name.lower()}"
        return f"{track}: {spec.display_name.lower()}"

    @staticmethod
    def _format_patch_tooltip(spec: PatchSpec) -> str:
        original = spec.original.hex(" ").upper()
        patched = spec.patched.hex(" ").upper()
        return (
            f"{spec.display_name}\n"
            f"Patch key: {spec.key}\n"
            f"Offset: 0x{spec.file_offset:X}\n"
            f"Bytes: {original} -> {patched}"
        )

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        target_group = QGroupBox("Target Executable")
        target_layout = QHBoxLayout(target_group)
        self.exe_path_edit = QLineEdit()
        self.exe_path_edit.setReadOnly(True)
        self.exe_path_edit.textChanged.connect(self._on_selection_changed)
        target_layout.addWidget(self.exe_path_edit, 1)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse_exe)
        target_layout.addWidget(browse_btn)

        use_game_dir_btn = QPushButton("Use Game Dir")
        use_game_dir_btn.clicked.connect(lambda: self.refresh_from_config(force=True))
        target_layout.addWidget(use_game_dir_btn)
        layout.addWidget(target_group)

        patches_group = QGroupBox("Display / Windowed Patches (Stable + Experimental)")
        patches_layout = QVBoxLayout(patches_group)
        patches_layout.addWidget(QLabel(
            "Stable track patches are the default and byte-verified. The app only writes when bytes match expected original/patched values."
        ))
        patches_layout.addWidget(QLabel(
            "Experimental patches are opt-in and should be used only when stable patches are insufficient on your setup."
        ))
        patches_layout.addWidget(QLabel(
            "Version watermark note: applying any selected patch also applies an internal version-overlay tag so the game shows V1.00 - PATCHED."
        ))

        self.resolution_gate_check = QCheckBox(self._format_patch_label(self.resolution_spec))
        self.resolution_gate_check.setChecked(True)
        self.resolution_gate_check.setToolTip(self._format_patch_tooltip(self.resolution_spec))
        self.resolution_gate_check.toggled.connect(self._on_selection_changed)
        patches_layout.addWidget(self.resolution_gate_check)

        self.force_windowed_check = QCheckBox(self._format_patch_label(self.force_windowed_spec))
        self.force_windowed_check.setChecked(True)
        self.force_windowed_check.setToolTip(self._format_patch_tooltip(self.force_windowed_spec))
        self.force_windowed_check.toggled.connect(self._on_selection_changed)
        patches_layout.addWidget(self.force_windowed_check)

        self.extra_graphics_default_on_check = QCheckBox(self._format_patch_label(self.extra_graphics_default_on_spec))
        self.extra_graphics_default_on_check.setChecked(True)
        self.extra_graphics_default_on_check.setToolTip(self._format_patch_tooltip(self.extra_graphics_default_on_spec))
        self.extra_graphics_default_on_check.toggled.connect(self._on_selection_changed)
        patches_layout.addWidget(self.extra_graphics_default_on_check)

        self.ignore_cardid_overrides_check = QCheckBox(self._format_patch_label(self.ignore_cardid_overrides_spec))
        self.ignore_cardid_overrides_check.setChecked(True)
        self.ignore_cardid_overrides_check.setToolTip(self._format_patch_tooltip(self.ignore_cardid_overrides_spec))
        self.ignore_cardid_overrides_check.toggled.connect(self._on_selection_changed)
        patches_layout.addWidget(self.ignore_cardid_overrides_check)

        self.skip_auto_toggle_check = QCheckBox(self._format_patch_label(self.skip_auto_toggle_spec))
        self.skip_auto_toggle_check.setToolTip(self._format_patch_tooltip(self.skip_auto_toggle_spec))
        self.skip_auto_toggle_check.toggled.connect(self._on_selection_changed)
        patches_layout.addWidget(self.skip_auto_toggle_check)

        patches_layout.addWidget(QLabel(
            "Experimental patch 5 is only for setups where startup still flips mode after the stable patches; it is not a universal fix."
        ))
        layout.addWidget(patches_group)

        action_row = QHBoxLayout()
        self.verify_btn = QPushButton("Verify Selected")
        self.verify_btn.clicked.connect(self._on_verify_selected)
        action_row.addWidget(self.verify_btn)

        self.apply_btn = QPushButton("Apply Selected")
        self.apply_btn.clicked.connect(self._on_apply_selected)
        action_row.addWidget(self.apply_btn)

        self.restore_btn = QPushButton("Restore Backup")
        self.restore_btn.clicked.connect(self._on_restore_backup)
        action_row.addWidget(self.restore_btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        output_group = QGroupBox("Patch Output")
        output_layout = QVBoxLayout(output_group)
        output_layout.addWidget(QLabel(
            "Recommended flow: Verify Selected -> Apply Selected. "
            "In-place writes create backup file: BEA.exe.original.backup"
        ))

        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))
        output_layout.addWidget(self.output_text, 1)
        layout.addWidget(output_group, 1)

    def refresh_from_config(self, force: bool) -> None:
        config = AppConfig.load()
        game_dir = config.get_game_dir()
        if game_dir is None:
            self._update_button_state()
            return

        exe_candidate = game_dir / "BEA.exe"

        if exe_candidate.exists():
            current = self.exe_path_edit.text().strip()
            if force or not current or not Path(current).exists():
                self.exe_path_edit.setText(str(exe_candidate))
                self.output_text.setPlainText(f"Using BEA.exe from configured game directory:\n{exe_candidate}")

        self._update_button_state()

    def _visible_selected_specs(self) -> list[PatchSpec]:
        selected: list[PatchSpec] = []
        if self.resolution_gate_check.isChecked():
            selected.append(self.resolution_spec)
        if self.force_windowed_check.isChecked():
            selected.append(self.force_windowed_spec)
        if self.extra_graphics_default_on_check.isChecked():
            selected.append(self.extra_graphics_default_on_spec)
        if self.ignore_cardid_overrides_check.isChecked():
            selected.append(self.ignore_cardid_overrides_spec)
        if self.skip_auto_toggle_check.isChecked():
            selected.append(self.skip_auto_toggle_spec)
        return selected

    def _selected_specs(self) -> list[PatchSpec]:
        selected = self._visible_selected_specs()
        if selected:
            if all(spec.key != self.version_pointer_spec.key for spec in selected):
                selected.append(self.version_pointer_spec)
            if all(spec.key != self.version_cave_string_spec.key for spec in selected):
                selected.append(self.version_cave_string_spec)
        return selected

    def _selection_signature(self) -> tuple[str, tuple[str, ...]] | None:
        raw = self.exe_path_edit.text().strip()
        if not raw:
            return None
        visible = self._visible_selected_specs()
        if not visible:
            return None
        return (str(Path(raw)), tuple(spec.key for spec in visible))

    def _on_selection_changed(self) -> None:
        self._verified_signature = None
        self._update_button_state()

    def _validate_selection(self) -> str | None:
        visible = self._visible_selected_specs()
        if not visible:
            return "Select at least one patch first."
        has_experimental = any(spec.track.lower() == "experimental" for spec in visible)
        has_stable = any(spec.track.lower() == "stable" for spec in visible)
        if has_experimental and not has_stable:
            return "Experimental startup patch should be layered on top of the stable patch set, not applied by itself."
        return None

    def _update_button_state(self) -> None:
        raw = self.exe_path_edit.text().strip()
        exe_ok = bool(raw) and Path(raw).exists()
        selected = len(self._visible_selected_specs()) > 0
        current_signature = self._selection_signature()
        verified_current = current_signature is not None and current_signature == self._verified_signature
        self.verify_btn.setEnabled(exe_ok and selected)
        self.apply_btn.setEnabled(exe_ok and selected and verified_current)
        self.restore_btn.setEnabled(bool(raw) and build_backup_path(Path(raw)).exists())

    def _get_target_exe(self, allow_missing: bool = False) -> Path | None:
        raw = self.exe_path_edit.text().strip()
        if not raw:
            self.output_text.setPlainText("Select a valid BEA.exe path first.")
            self._update_button_state()
            return None

        exe_path = Path(raw)
        if not allow_missing and not exe_path.exists():
            self.output_text.setPlainText("Select a valid BEA.exe path first.")
            self._update_button_state()
            return None

        return exe_path

    def _on_browse_exe(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select BEA.exe",
            "",
            "BEA executable (BEA.exe);;Executable files (*.exe);;All files (*)",
        )
        if not filename:
            return
        self.exe_path_edit.setText(filename)
        self._update_button_state()

    def _on_verify_selected(self) -> None:
        exe_path = self._get_target_exe()
        if exe_path is None:
            return

        validation_error = self._validate_selection()
        if validation_error:
            self.output_text.setPlainText(validation_error)
            self._update_button_state()
            return

        specs = self._selected_specs()
        data = exe_path.read_bytes()
        all_known, all_patched, rows = verify_patch_specs(data, specs)
        if not all_known:
            summary = "Verification failed: at least one patch location is in an unexpected state."
        elif all_patched:
            summary = "All selected patches are already applied."
        else:
            summary = "All selected patches are in known original/patched states and safe to apply."

        self.output_text.setPlainText(render_state_report(exe_path, rows, summary))
        self._verified_signature = self._selection_signature() if all_known else None
        self._update_button_state()

    def _on_apply_selected(self) -> None:
        exe_path = self._get_target_exe()
        if exe_path is None:
            return

        current_signature = self._selection_signature()
        if current_signature is None or current_signature != self._verified_signature:
            self.output_text.setPlainText(
                "Verify Selected after your latest path/selection change before applying patches."
            )
            self._update_button_state()
            return

        specs = self._selected_specs()
        result = QMessageBox.question(
            self,
            "Confirm Apply Patches",
            "Apply the selected byte-verified patches to BEA.exe?\n\n"
            "Notes:\n"
            "- Restore uses the first full-file backup snapshot.\n"
            "- Companion version watermark writes are added automatically.\n"
            "- Verify Selected should be rerun after any later selection change.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            self.output_text.setPlainText("Apply canceled by user.")
            self._update_button_state()
            return

        ok, message = apply_patches_to_file(exe_path, specs)
        self.output_text.setPlainText(message)
        if not ok:
            QMessageBox.warning(self, "Binary Patches", "Apply did not complete.\nSee Patch Output for details.")
        self._verified_signature = None
        self._update_button_state()

    def _on_restore_backup(self) -> None:
        exe_path = self._get_target_exe(allow_missing=True)
        if exe_path is None:
            return

        backup_path = build_backup_path(exe_path)
        if not backup_path.exists():
            self.output_text.setPlainText(f"Backup file not found: {backup_path}")
            self._update_button_state()
            return

        result = QMessageBox.question(
            self,
            "Confirm Restore Backup",
            f"Restore {exe_path} from backup?\n\nBackup:\n{backup_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            self.output_text.setPlainText("Restore canceled by user.")
            self._update_button_state()
            return

        ok, message = restore_from_backup(exe_path)
        self.output_text.setPlainText(message)
        if not ok:
            QMessageBox.warning(self, "Binary Patches", message)
        self._verified_signature = None
        self._update_button_state()
