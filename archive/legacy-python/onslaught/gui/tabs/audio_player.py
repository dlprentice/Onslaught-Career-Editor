"""
Onslaught Career Editor - Audio Player Tab
Play game music and voice files using Qt Multimedia
"""

import os
import struct
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton,
    QSlider, QGroupBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.config import AppConfig, detect_game_directory
from ..widgets.save_selector import GameDirDialog

# Check for PyQt6 multimedia
MULTIMEDIA_AVAILABLE = False
try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    pass


class AudioPlayerTab(QWidget):
    """Audio player tab - play game music and voice files"""
    playbackStarted = pyqtSignal()
    gameDirChanged = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = AppConfig.load()
        self.current_file = None
        self.is_playing = False
        self._slider_being_dragged = False
        self._duration_cache = {}
        self._has_loaded = False
        self._setup_ui()
        # Defer loading until tab is activated

    def _get_game_dir(self) -> Path:
        """Get game directory from config or detect"""
        self.config = AppConfig.load()
        game_dir = self.config.get_game_dir()
        if game_dir and game_dir.exists():
            return game_dir
        detected = detect_game_directory()
        if detected and detected.exists():
            return detected
        # Explicit dev fallback only.
        if os.getenv("ONSLAUGHT_DEV_GAME_FALLBACK", "0") == "1":
            module_dir = Path(__file__).parent.parent.parent.parent
            return module_dir / 'game'
        return Path("__UNSET_GAME_DIR__")

    def _setup_ui(self):
        """Set up the tab UI"""
        layout = QVBoxLayout(self)

        # Status message about audio availability
        if not MULTIMEDIA_AVAILABLE:
            warning = QLabel(
                "Audio playback unavailable. Qt Multimedia not found.\n"
                "Try: pip install PyQt6"
            )
            warning.setStyleSheet("color: red; padding: 10px;")
            layout.addWidget(warning)

        # Game directory controls
        game_layout = QHBoxLayout()
        game_layout.addWidget(QLabel("Game Dir:"))
        self.game_dir_label = QLabel("")
        self.game_dir_label.setStyleSheet("color: #444;")
        self.game_dir_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        game_layout.addWidget(self.game_dir_label, 1)

        self.set_game_btn = QPushButton("Set Game Dir...")
        self.set_game_btn.clicked.connect(self._set_game_dir)
        game_layout.addWidget(self.set_game_btn)

        self.reload_btn = QPushButton("Reload Audio Files")
        self.reload_btn.clicked.connect(self._load_audio_tree)
        game_layout.addWidget(self.reload_btn)

        layout.addLayout(game_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter audio files...")
        self.search_edit.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_edit)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._load_audio_tree)
        search_layout.addWidget(self.refresh_btn)

        layout.addLayout(search_layout)

        # Splitter for tree and controls
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Audio file tree
        tree_group = QGroupBox("Audio Files")
        tree_layout = QVBoxLayout(tree_group)
        self.audio_tree = QTreeWidget()
        self.audio_tree.setHeaderLabels(["File", "Duration"])
        self.audio_tree.setColumnWidth(0, 300)
        self.audio_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.audio_tree.itemClicked.connect(self._on_item_clicked)
        tree_layout.addWidget(self.audio_tree)
        splitter.addWidget(tree_group)

        # Player controls
        controls_group = QGroupBox("Player")
        controls_layout = QVBoxLayout(controls_group)

        # Now playing label
        self.now_playing = QLabel("No track selected")
        self.now_playing.setFont(QFont("Sans", 11, QFont.Weight.Bold))
        self.now_playing.setWordWrap(True)
        controls_layout.addWidget(self.now_playing)

        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setEnabled(False)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self.progress_slider.sliderMoved.connect(self._on_slider_moved)
        controls_layout.addWidget(self.progress_slider)

        # Time labels
        time_layout = QHBoxLayout()
        self.time_current = QLabel("0:00")
        self.time_total = QLabel("0:00")
        time_layout.addWidget(self.time_current)
        time_layout.addStretch()
        time_layout.addWidget(self.time_total)
        controls_layout.addLayout(time_layout)

        # Playback buttons
        btn_layout = QHBoxLayout()

        self.play_btn = QPushButton("Play")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self._play)
        btn_layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._pause_resume)
        btn_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        btn_layout.addWidget(self.stop_btn)

        controls_layout.addLayout(btn_layout)

        # Volume control
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        vol_layout.addWidget(self.volume_slider)
        self.volume_label = QLabel("70%")
        vol_layout.addWidget(self.volume_label)
        controls_layout.addLayout(vol_layout)

        controls_layout.addStretch()

        # File info
        self.file_info = QLabel("")
        self.file_info.setWordWrap(True)
        controls_layout.addWidget(self.file_info)

        splitter.addWidget(controls_group)
        splitter.setSizes([500, 300])

        layout.addWidget(splitter, 1)  # Give splitter all the stretch

        # Compact status bar (footer style)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px;")
        self.status_label.setMaximumHeight(20)
        layout.addWidget(self.status_label)

        # Set up media player
        if MULTIMEDIA_AVAILABLE:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(0.7)  # 70% default

            # Connect signals
            self.media_player.positionChanged.connect(self._on_position_changed)
            self.media_player.durationChanged.connect(self._on_duration_changed)
            self.media_player.playbackStateChanged.connect(self._on_state_changed)
            self.media_player.errorOccurred.connect(self._on_error)
        else:
            self.media_player = None

    def _load_audio_tree(self):
        """Load audio files into the tree"""
        self._has_loaded = True
        self.audio_tree.clear()
        game_dir = self._get_game_dir()
        self.game_dir_label.setText(str(game_dir) if game_dir else "(not set)")

        if not game_dir.exists():
            self.status_label.setText(f"Game directory not found: {game_dir}")
            return

        music_count = 0
        voice_count = 0

        # Music tracks
        music_dir = game_dir / 'data' / 'Music'
        if music_dir.exists():
            music_item = QTreeWidgetItem(["Music"])
            music_item.setData(0, Qt.ItemDataRole.UserRole, None)

            for ogg_file in sorted(music_dir.glob("*.ogg")):
                # Clean up display name
                display_name = ogg_file.stem.replace("(Master)", "").strip()
                duration = self._get_duration_display(ogg_file)
                file_item = QTreeWidgetItem([display_name, duration])
                file_item.setData(0, Qt.ItemDataRole.UserRole, ogg_file)
                file_item.setToolTip(0, str(ogg_file))
                music_item.addChild(file_item)
                music_count += 1

            if music_item.childCount() > 0:
                self.audio_tree.addTopLevelItem(music_item)
                music_item.setExpanded(True)

        # Voice files (English)
        voice_dir = game_dir / 'data' / 'sounds' / 'english' / 'MessageBox'
        if voice_dir.exists():
            voice_item = QTreeWidgetItem(["Voice (English)"])
            voice_item.setData(0, Qt.ItemDataRole.UserRole, None)

            # Group voice files by prefix (mission number)
            groups = {}
            for ogg_file in sorted(voice_dir.glob("*.ogg")):
                name = ogg_file.stem
                # Try to extract prefix (e.g., "110_" -> "Mission 110")
                parts = name.split('_')
                if parts[0].isdigit():
                    prefix = f"Mission {parts[0]}"
                elif name.startswith("TUTORIAL"):
                    prefix = "Tutorial"
                elif name.startswith("RACING"):
                    prefix = "Racing"
                elif any(name.startswith(x) for x in ["HEALTH", "UNDER", "BASE", "NEED"]):
                    prefix = "Status Messages"
                else:
                    prefix = "Other"

                if prefix not in groups:
                    groups[prefix] = []
                groups[prefix].append(ogg_file)
                voice_count += 1

            # Add grouped items
            for group_name in sorted(groups.keys()):
                group_item = QTreeWidgetItem([f"{group_name} ({len(groups[group_name])})"])
                group_item.setData(0, Qt.ItemDataRole.UserRole, None)

                for ogg_file in groups[group_name]:
                    duration = self._get_duration_display(ogg_file)
                    file_item = QTreeWidgetItem([ogg_file.stem, duration])
                    file_item.setData(0, Qt.ItemDataRole.UserRole, ogg_file)
                    file_item.setToolTip(0, str(ogg_file))
                    group_item.addChild(file_item)

                voice_item.addChild(group_item)

            if voice_item.childCount() > 0:
                self.audio_tree.addTopLevelItem(voice_item)

        self.status_label.setText(f"Loaded {music_count} music tracks, {voice_count} voice files")

    def ensure_loaded(self):
        """Load audio tree on first activation to avoid blocking startup."""
        if not self._has_loaded:
            self._load_audio_tree()

    def _set_game_dir(self):
        """Open dialog to set game directory"""
        current = self.config.game_directory or ""
        dialog = GameDirDialog(self, current)
        dialog.open()
        dialog.finished.connect(lambda r: self._on_game_dir_dialog_finished(dialog, r))

    def _on_game_dir_dialog_finished(self, dialog: GameDirDialog, result: int):
        if result == dialog.DialogCode.Accepted.value:
            new_path = dialog.get_path()
            if new_path:
                path = Path(new_path)
                if path.exists():
                    if not self.config.set_game_dir(path):
                        QMessageBox.warning(self, "Save Failed", f"Failed to persist game directory:\n{new_path}")
                        return
                    self._load_audio_tree()
                    self.gameDirChanged.emit(path)
                else:
                    QMessageBox.warning(self, "Invalid Path", f"Directory does not exist:\n{new_path}")

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle single click - select file"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            self.current_file = file_path
            self.now_playing.setText(file_path.stem)
            self.file_info.setText(f"Path: {file_path}")
            self.play_btn.setEnabled(MULTIMEDIA_AVAILABLE)
            self.pause_btn.setEnabled(False)
            self.pause_btn.setText("Pause")
            self.stop_btn.setEnabled(False)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double click - play file"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            self.current_file = file_path
            self._play_file(file_path)

    def _format_time(self, ms: int) -> str:
        """Format milliseconds as M:SS"""
        seconds = ms // 1000
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"

    def _format_duration(self, seconds: float) -> str:
        """Format seconds as M:SS"""
        total = int(round(seconds))
        mins = total // 60
        secs = total % 60
        return f"{mins}:{secs:02d}"

    def _get_duration_display(self, file_path: Path) -> str:
        """Return cached duration string for an audio file."""
        cached = self._duration_cache.get(file_path)
        if cached is not None:
            return cached

        duration = None
        if file_path.suffix.lower() == ".ogg":
            duration = self._get_ogg_duration(file_path)
        elif file_path.suffix.lower() == ".wav":
            duration = self._get_wav_duration(file_path)

        display = self._format_duration(duration) if duration is not None else ""
        self._duration_cache[file_path] = display
        return display

    def _get_wav_duration(self, file_path: Path) -> float | None:
        """Get WAV duration in seconds."""
        try:
            import wave
            with wave.open(str(file_path), "rb") as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                return frames / rate if rate else None
        except Exception:
            return None

    def _get_ogg_duration(self, file_path: Path) -> float | None:
        """Get OGG duration in seconds by parsing Ogg pages."""
        try:
            sample_rate = None
            last_granule = None
            with open(file_path, "rb") as f:
                while True:
                    header = f.read(27)
                    if len(header) < 27:
                        break
                    if header[0:4] != b"OggS":
                        break
                    granule = struct.unpack_from("<Q", header, 6)[0]
                    seg_count = header[26]
                    lacing = f.read(seg_count)
                    if len(lacing) < seg_count:
                        break
                    data_len = sum(lacing)
                    data = f.read(data_len)

                    if sample_rate is None:
                        idx = data.find(b"\x01vorbis")
                        if idx != -1 and len(data) >= idx + 1 + 6 + 4 + 1 + 4:
                            sample_rate = struct.unpack_from("<I", data, idx + 1 + 6 + 4 + 1)[0]

                    if granule != 0xFFFFFFFFFFFFFFFF:
                        last_granule = granule

            if sample_rate and last_granule is not None:
                return last_granule / sample_rate
        except Exception:
            return None

        return None

    def _play_file(self, file_path: Path):
        """Play an audio file"""
        if not MULTIMEDIA_AVAILABLE:
            QMessageBox.warning(self, "Error", "Qt Multimedia not available for audio playback")
            return

        try:
            self.media_player.setSource(QUrl.fromLocalFile(str(file_path)))
            self.audio_output.setVolume(self.volume_slider.value() / 100)
            self.media_player.play()

            self.is_playing = True
            self.play_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.pause_btn.setText("Pause")
            self.stop_btn.setEnabled(True)
            self.progress_slider.setEnabled(True)

            self.now_playing.setText(f"Playing: {file_path.stem}")
            self.playbackStarted.emit()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to play: {e}")

    def _play(self):
        """Start playback for the current file"""
        if not self.media_player:
            return

        if self.current_file:
            self._play_file(self.current_file)

    def _pause_resume(self):
        """Pause or resume playback"""
        if not self.media_player:
            return

        state = self.media_player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.is_playing = False
            self.pause_btn.setText("Resume")
            if self.current_file:
                self.now_playing.setText(f"Paused: {self.current_file.stem}")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.media_player.play()
            self.is_playing = True
            self.pause_btn.setText("Pause")
            if self.current_file:
                self.now_playing.setText(f"Playing: {self.current_file.stem}")
            self.playbackStarted.emit()

    def _stop(self):
        """Stop playback"""
        if self.media_player:
            self.media_player.stop()
        self.is_playing = False
        self.play_btn.setEnabled(self.current_file is not None)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(False)
        self.time_current.setText("0:00")
        if self.current_file:
            self.now_playing.setText(f"Stopped: {self.current_file.stem}")

    def stop_playback(self):
        """Public stop for cross-tab coordination."""
        self._stop()

    def is_playing_now(self) -> bool:
        return bool(self.is_playing)

    def _on_volume_changed(self, value: int):
        """Handle volume slider change"""
        self.volume_label.setText(f"{value}%")
        if self.media_player and hasattr(self, 'audio_output'):
            self.audio_output.setVolume(value / 100)

    def _on_position_changed(self, position: int):
        """Handle playback position change from media player"""
        if not self._slider_being_dragged:
            self.progress_slider.setValue(position)
        self.time_current.setText(self._format_time(position))

    def _on_duration_changed(self, duration: int):
        """Handle duration change from media player"""
        self.progress_slider.setRange(0, duration)
        self.time_total.setText(self._format_time(duration))

    def _on_state_changed(self, state):
        """Handle playback state change"""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self.is_playing:
                # Playback finished naturally
                self.is_playing = False
                self.play_btn.setEnabled(self.current_file is not None)
                self.pause_btn.setEnabled(False)
                self.pause_btn.setText("Pause")
                self.stop_btn.setEnabled(False)
                if self.current_file:
                    self.now_playing.setText(f"Finished: {self.current_file.stem}")

    def _on_error(self, error, message):
        """Handle media player error"""
        self.now_playing.setText(f"Error: {message}")
        QMessageBox.warning(self, "Playback Error", f"Could not play audio:\n{message}")

    def _on_slider_pressed(self):
        """Handle slider press - pause position updates"""
        self._slider_being_dragged = True

    def _on_slider_released(self):
        """Handle slider release - seek to position"""
        self._slider_being_dragged = False
        if self.media_player:
            self.media_player.setPosition(self.progress_slider.value())

    def _on_slider_moved(self, position: int):
        """Handle slider drag - update time display"""
        self.time_current.setText(self._format_time(position))

    def _on_search(self, text: str):
        """Filter audio files by search text"""
        search_lower = text.lower()

        def filter_item(item: QTreeWidgetItem) -> bool:
            """Recursively filter items, returns True if item or any child matches"""
            file_path = item.data(0, Qt.ItemDataRole.UserRole)

            # Check if this item matches
            matches = search_lower in item.text(0).lower()

            # Check children
            child_matches = False
            for i in range(item.childCount()):
                child = item.child(i)
                if filter_item(child):
                    child_matches = True

            # Show if matches or has matching children
            should_show = matches or child_matches or not text
            item.setHidden(not should_show)

            return matches or child_matches

        for i in range(self.audio_tree.topLevelItemCount()):
            filter_item(self.audio_tree.topLevelItem(i))

        if not text:
            # Expand top level when search cleared
            for i in range(self.audio_tree.topLevelItemCount()):
                self.audio_tree.topLevelItem(i).setExpanded(True)
