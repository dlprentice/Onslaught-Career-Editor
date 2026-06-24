"""
Onslaught Career Editor - Settings Tab
Configure game directory and view save file info
"""

from pathlib import Path
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QLineEdit, QFileDialog, QCheckBox
)

from ...core.config import AppConfig, detect_game_directory, find_save_files, get_config_path


class SettingsTab(QWidget):
    """Settings tab - configures game directory and app preferences"""

    gameDirChanged = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = AppConfig.load()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Game directory group
        game_group = QGroupBox("Game Directory")
        game_layout = QVBoxLayout(game_group)

        game_desc = QLabel(
            "Set the Battle Engine Aquila installation directory. This is used by the "
            "Audio Player, Video Player, and Save tools to locate game files."
        )
        game_desc.setStyleSheet("color: #666;")
        game_desc.setWordWrap(True)
        game_layout.addWidget(game_desc)

        game_path_layout = QHBoxLayout()
        self.game_dir_edit = QLineEdit()
        self.game_dir_edit.setReadOnly(True)
        self.game_dir_edit.setPlaceholderText("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Battle Engine Aquila")
        game_path_layout.addWidget(self.game_dir_edit, 1)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_game_dir)
        game_path_layout.addWidget(browse_btn)

        detect_btn = QPushButton("Auto-Detect")
        detect_btn.clicked.connect(self._auto_detect_game_dir)
        game_path_layout.addWidget(detect_btn)

        game_layout.addLayout(game_path_layout)

        self.game_dir_status = QLabel("")
        self.game_dir_status.setStyleSheet("color: #666;")
        self.game_dir_status.setWordWrap(True)
        game_layout.addWidget(self.game_dir_status)

        layout.addWidget(game_group)

        # Save files group
        save_group = QGroupBox("Save Files")
        save_layout = QVBoxLayout(save_group)

        save_desc = QLabel(
            "Save files are typically located in the game's save directory. "
            "The editor will scan this location for .bes/.bea files (including defaultoptions.bea)."
        )
        save_desc.setStyleSheet("color: #666;")
        save_desc.setWordWrap(True)
        save_layout.addWidget(save_desc)

        self.save_dir_label = QLabel("")
        self.save_dir_label.setStyleSheet("font-weight: 600;")
        save_layout.addWidget(self.save_dir_label)

        self.save_file_count = QLabel("")
        self.save_file_count.setStyleSheet("color: #666;")
        save_layout.addWidget(self.save_file_count)

        layout.addWidget(save_group)

        # Media playback group
        media_group = QGroupBox("Media Playback")
        media_layout = QVBoxLayout(media_group)

        media_desc = QLabel(
            "Control whether audio or video continues playing when you switch tabs."
        )
        media_desc.setStyleSheet("color: #666;")
        media_desc.setWordWrap(True)
        media_layout.addWidget(media_desc)

        self.allow_background_audio = QCheckBox("Allow audio to keep playing when switching tabs")
        self.allow_background_audio.stateChanged.connect(self._on_media_prefs_changed)
        media_layout.addWidget(self.allow_background_audio)

        self.allow_background_video = QCheckBox("Allow video to keep playing when switching tabs")
        self.allow_background_video.stateChanged.connect(self._on_media_prefs_changed)
        media_layout.addWidget(self.allow_background_video)

        self.prevent_media_overlap = QCheckBox("Prevent audio and video from playing at the same time")
        self.prevent_media_overlap.stateChanged.connect(self._on_media_prefs_changed)
        media_layout.addWidget(self.prevent_media_overlap)

        layout.addWidget(media_group)

        # About group
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout(about_group)

        about_layout.addWidget(QLabel("Onslaught Toolkit"))
        about_desc = QLabel("Save editor and media browser for Battle Engine Aquila (2003)")
        about_desc.setStyleSheet("color: #444;")
        about_layout.addWidget(about_desc)

        thanks = QLabel(
            "Created for the Battle Engine Aquila preservation community.\n"
            "Special thanks to Stuart Gillam for providing source code reference."
        )
        thanks.setStyleSheet("color: #666; font-size: 11px;")
        thanks.setWordWrap(True)
        about_layout.addWidget(thanks)

        config_path = get_config_path()
        config_label = QLabel(f"Config file: {config_path}")
        config_label.setStyleSheet("color: #666; font-size: 11px;")
        config_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        about_layout.addWidget(config_label)

        layout.addWidget(about_group)
        layout.addStretch()

    def _load_settings(self):
        self.config = AppConfig.load()
        game_dir = self.config.get_game_dir()
        self._loading = True

        if game_dir:
            self.game_dir_edit.setText(str(game_dir))
            self._validate_game_dir(game_dir)
        else:
            self.game_dir_status.setText("No game directory set. Click Browse or Auto-Detect.")
            self.game_dir_status.setStyleSheet("color: #666;")

        self._update_save_info()
        self.allow_background_audio.setChecked(self.config.allow_background_audio)
        self.allow_background_video.setChecked(self.config.allow_background_video)
        self.prevent_media_overlap.setChecked(self.config.prevent_audio_video_overlap)
        self._loading = False

    def _browse_game_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Battle Engine Aquila Directory"
        )
        if folder:
            self._set_game_dir(Path(folder))

    def _auto_detect_game_dir(self):
        detected = detect_game_directory()
        if detected:
            self._set_game_dir(detected)
        else:
            self.game_dir_status.setText(
                "Could not auto-detect game directory. Please browse manually."
            )
            self.game_dir_status.setStyleSheet("color: #b36b00;")

    def _set_game_dir(self, path: Path):
        self.config = AppConfig.load()
        if not path.exists():
            self._validate_game_dir(path)
            return
        if not self.config.set_game_dir(path):
            self.game_dir_status.setText("Failed to save game directory setting")
            self.game_dir_status.setStyleSheet("color: #b00020;")
            return
        self.game_dir_edit.setText(str(path))
        self._validate_game_dir(path)
        self._update_save_info()
        self.gameDirChanged.emit(path)

    def _validate_game_dir(self, path: Path):
        if not path.exists():
            self.game_dir_status.setText("Directory does not exist")
            self.game_dir_status.setStyleSheet("color: #b00020;")
            return

        has_data = (path / 'data').exists()
        has_video = (path / 'data' / 'video').exists()
        has_music = (path / 'data' / 'Music').exists()
        has_exe = (path / 'BEA.exe').exists() or (path / 'bea.exe').exists()

        if has_data and (has_video or has_music):
            msg = "Valid game directory detected"
            if has_exe:
                msg += " (with executable)"
            self.game_dir_status.setText(msg)
            self.game_dir_status.setStyleSheet("color: #2e7d32;")
        else:
            self.game_dir_status.setText(
                "Warning: This doesn't look like a BEA installation (missing data folder)"
            )
            self.game_dir_status.setStyleSheet("color: #b36b00;")

    def _update_save_info(self):
        self.config = AppConfig.load()
        game_dir = self.config.get_game_dir()

        if not game_dir:
            self.save_dir_label.setText("Game directory not configured")
            self.save_file_count.setText("")
            return

        saves = find_save_files(game_dir)
        if saves:
            first_dir = saves[0].parent
            self.save_dir_label.setText(str(first_dir))
            self.save_file_count.setText(f"Found {len(saves)} save file(s)")
        else:
            self.save_dir_label.setText("No save files found")
            self.save_file_count.setText("Create a save in-game first, or check game directory")

    def _on_media_prefs_changed(self):
        if getattr(self, "_loading", False):
            return
        self.config = AppConfig.load()
        self.config.allow_background_audio = self.allow_background_audio.isChecked()
        self.config.allow_background_video = self.allow_background_video.isChecked()
        self.config.prevent_audio_video_overlap = self.prevent_media_overlap.isChecked()
        self.config.save()
        window = self.window()
        if hasattr(window, "apply_media_policy_now"):
            window.apply_media_policy_now()
