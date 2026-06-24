"""
Onslaught Career Editor - Save File Selector Widget
Reusable widget for selecting .bes/.bea files with auto-detection
"""

from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QPushButton, QLabel, QFileDialog,
    QDialog, QLineEdit, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from ...core.config import (
    AppConfig, find_save_files, get_save_info, detect_game_directory
)


class GameDirDialog(QDialog):
    """Dialog for setting the game directory"""

    def __init__(self, parent=None, current_dir: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Set Game Directory")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Instructions
        layout.addWidget(QLabel(
            "Set the Battle Engine Aquila installation directory.\n"
            "Save/options files (.bes/.bea) will be detected from this location."
        ))

        # Path input
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(current_dir)
        self.path_edit.setPlaceholderText("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Battle Engine Aquila")
        path_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)
        path_layout.addWidget(browse_btn)

        layout.addLayout(path_layout)

        # Auto-detect button
        detect_btn = QPushButton("Auto-Detect")
        detect_btn.clicked.connect(self._auto_detect)
        layout.addWidget(detect_btn)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse(self):
        """Browse for game directory"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Battle Engine Aquila Directory"
        )
        if folder:
            self.path_edit.setText(folder)

    def _auto_detect(self):
        """Try to auto-detect game directory"""
        detected = detect_game_directory()
        if detected:
            self.path_edit.setText(str(detected))
            QMessageBox.information(self, "Found", f"Detected game at:\n{detected}")
        else:
            QMessageBox.warning(
                self, "Not Found",
                "Could not auto-detect Battle Engine Aquila.\n"
                "Please browse to the installation folder manually."
            )

    def get_path(self) -> str:
        """Get the entered path"""
        return self.path_edit.text()


class SaveSelector(QWidget):
    """Widget for selecting .bes/.bea files with auto-detection"""

    # Signal emitted when a save file is selected
    fileSelected = pyqtSignal(Path)
    # Signal emitted when file selection is cleared (placeholder selected)
    selectionCleared = pyqtSignal()
    # Signal emitted when game directory changes
    gameDirChanged = pyqtSignal(Path)

    def __init__(self, parent=None, label: str = "Save File", auto_select_first: bool = True):
        super().__init__(parent)
        self.config = AppConfig.load()
        self.current_path: Path | None = None
        self.label_text = label
        self.auto_select_first = auto_select_first
        self._setup_ui()
        self._refresh_saves()

    def _setup_ui(self):
        """Set up the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main group
        group = QGroupBox(self.label_text)
        group_layout = QVBoxLayout(group)

        # Combo box for detected saves
        combo_layout = QHBoxLayout()

        self.save_combo = QComboBox()
        self.save_combo.setMinimumWidth(300)
        self.save_combo.currentIndexChanged.connect(self._on_selection_changed)
        combo_layout.addWidget(self.save_combo, 1)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip("Refresh list of detected save/options files")
        refresh_btn.clicked.connect(self._refresh_saves)
        combo_layout.addWidget(refresh_btn)

        group_layout.addLayout(combo_layout)

        # Action buttons row
        btn_layout = QHBoxLayout()

        browse_btn = QPushButton("Browse...")
        browse_btn.setToolTip("Browse for a save/options file anywhere on your system")
        browse_btn.clicked.connect(self._browse_file)
        btn_layout.addWidget(browse_btn)

        settings_btn = QPushButton("Set Game Dir...")
        settings_btn.setToolTip("Set the Battle Engine Aquila installation directory")
        settings_btn.clicked.connect(self._set_game_dir)
        btn_layout.addWidget(settings_btn)

        btn_layout.addStretch()

        # Status label
        self.status_label = QLabel("")
        btn_layout.addWidget(self.status_label)

        group_layout.addLayout(btn_layout)

        layout.addWidget(group)

    def _refresh_saves(self):
        """Refresh the list of detected saves"""
        self.current_path = None
        self.save_combo.clear()
        self.save_combo.addItem("-- Select a save/options file --", None)

        # Reload config to get any changes
        self.config = AppConfig.load()
        game_dir = self.config.get_game_dir()

        saves = find_save_files(game_dir)

        if saves:
            for save_path in saves:
                info = get_save_info(save_path)
                # Format: "filename.ext (modified date)"
                modified = datetime.fromtimestamp(info['modified'])
                display = f"{save_path.name} ({modified.strftime('%Y-%m-%d %H:%M')})"
                if not info['valid']:
                    display += " [INVALID]"
                self.save_combo.addItem(display, save_path)

            self.status_label.setText(f"{len(saves)} files found")
        else:
            if game_dir:
                self.status_label.setText("No save/options files in game directory")
            else:
                self.status_label.setText("Game directory not set")

        # Also add recent files that aren't in the detected list
        recent = self.config.recent_files
        if recent:
            self.save_combo.insertSeparator(self.save_combo.count())
            for path_str in recent[:5]:
                path = Path(path_str)
                if path.exists() and path not in saves:
                    self.save_combo.addItem(f"[Recent] {path.name}", path)

        if self.auto_select_first and saves:
            # Index 0 is the placeholder; auto-select the first detected save
            self.save_combo.setCurrentIndex(1)

    def _on_selection_changed(self, index: int):
        """Handle combo box selection change"""
        path = self.save_combo.itemData(index)
        if path:
            self.current_path = path
            self.config.add_recent_file(path)
            self.fileSelected.emit(path)
        else:
            self.current_path = None
            self.selectionCleared.emit()

    def _browse_file(self):
        """Browse for a save/options file"""
        start_dir = ""
        game_dir = self.config.get_game_dir()
        if game_dir:
            start_dir = str(game_dir)

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Save/Options File",
            start_dir,
            "BEA Save/Options Files (*.bes *.bea);;All Files (*)"
        )
        if filename:
            path = Path(filename)
            self.current_path = path
            self.config.add_recent_file(path)

            # Add to combo if not already there
            found = False
            for i in range(self.save_combo.count()):
                if self.save_combo.itemData(i) == path:
                    self.save_combo.setCurrentIndex(i)
                    found = True
                    break

            if not found:
                self.save_combo.addItem(f"[Browsed] {path.name}", path)
                self.save_combo.setCurrentIndex(self.save_combo.count() - 1)

    def _set_game_dir(self):
        """Open dialog to set game directory"""
        current = self.config.game_directory or ""
        dialog = GameDirDialog(self, current)
        result = dialog.exec()
        if result != int(QDialog.DialogCode.Accepted):
            return

        new_path = dialog.get_path()
        if new_path:
            path = Path(new_path)
            if path.exists():
                if not self.config.set_game_dir(path):
                    QMessageBox.warning(
                        self, "Save Failed",
                        f"Failed to persist game directory:\n{new_path}"
                    )
                    return
                self._refresh_saves()
                self.gameDirChanged.emit(path)
            else:
                QMessageBox.warning(
                    self, "Invalid Path",
                    f"Directory does not exist:\n{new_path}"
                )

    def get_selected_path(self) -> Path | None:
        """Get the currently selected path"""
        return self.current_path

    def set_path(self, path: Path):
        """Programmatically set the selected path"""
        self.current_path = path
        # Try to find in combo
        for i in range(self.save_combo.count()):
            if self.save_combo.itemData(i) == path:
                self.save_combo.setCurrentIndex(i)
                return
        # Add if not found
        self.save_combo.addItem(f"[Selected] {path.name}", path)
        self.save_combo.setCurrentIndex(self.save_combo.count() - 1)
