"""
Onslaught Career Editor - Video Player Tab
Play game cutscenes and briefings (Bink .vid format)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton,
    QSlider, QGroupBox, QLineEdit, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QUrl, QProcess, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.config import AppConfig, detect_game_directory
from ..widgets.save_selector import GameDirDialog

def _ffmpeg_install_hint() -> str:
    return "Install ffmpeg and add it to PATH (https://ffmpeg.org/download.html)."


# Check for ffmpeg availability
FFMPEG_AVAILABLE = shutil.which('ffmpeg') is not None

# Check for PyQt6 multimedia
MULTIMEDIA_AVAILABLE = False
try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PyQt6.QtMultimediaWidgets import QVideoWidget
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    pass


class VideoPlayerTab(QWidget):
    """Video player tab - play game cutscenes and briefings"""
    playbackStarted = pyqtSignal()
    gameDirChanged = pyqtSignal(Path)

    # Video metadata for enhanced display
    CUTSCENE_NAMES = {
        '01': 'Opening - Battle Engine Introduction',
        '02': 'Mospherus Island - Arrival',
        '03': 'First Victory',
        '04': 'Enemy Advances',
        '05': 'Mospherus Defense',
        '06': 'Island Evacuation',
        '07': 'New Theater',
        '08': 'Evo Reveal',
        '09': 'Short Transition',
        '10': 'Major Battle',
        '11': 'Turning Point',
        '12': 'Brief Scene',
        '13': 'Quick Cut',
        '14': 'Plot Development',
        '15': 'Action Sequence',
        '16': 'Short Scene',
        '17': 'Battle Continuation',
        '18': 'Climax Building',
        '19': 'Transition',
        '20': 'Scene',
        '21': 'Major Event',
        '22': 'Story Beat',
        '23': 'Continuation',
        '24': 'Development',
        '25': 'Brief',
        '26': 'Scene',
        '27': 'Transition',
        '28': 'Brief',
        '29': 'Major',
        '30': 'Climax',
        '31': 'Short',
        '33': 'Ending',  # Note: 32 is missing
    }

    MAIN_VIDEOS = {
        'OpeningFMV': 'Opening Movie (Full)',
        'LTLogo': 'Lost Toys Logo',
        'FEBack128': 'Menu Background',
        'TWIMTBP_GefFX_640x480_Audio': 'NVIDIA Intro',
        'UsTheMovie': 'Us The Movie (Developer)',
        'gill_m_on_a_fork': 'Easter Egg - Gill on a Fork!',
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = AppConfig.load()
        self.current_file = None
        self.is_playing = False
        self.conversion_process = None
        self._pending_file = None
        self._direct_playback_attempted = False
        self._has_loaded = False
        self._setup_ui()
        # Defer loading until tab is activated

        # Timer for updating playback position
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_position)

    def _get_game_dir(self) -> Path:
        """Get game directory from config or detect"""
        self.config = AppConfig.load()
        game_dir = self.config.get_game_dir()
        if game_dir and game_dir.exists():
            return game_dir
        detected = detect_game_directory()
        if detected and detected.exists():
            return detected
        if os.getenv("ONSLAUGHT_DEV_GAME_FALLBACK", "0") == "1":
            module_dir = Path(__file__).parent.parent.parent.parent
            return module_dir / 'game'
        return Path("__UNSET_GAME_DIR__")

    def _get_cache_dir(self) -> Path:
        """Get video cache directory for converted files"""
        cache_dir = Path.home() / '.cache' / 'onslaught-career-editor' / 'videos'
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def _setup_ui(self):
        """Set up the tab UI"""
        layout = QVBoxLayout(self)

        # Status messages
        if not MULTIMEDIA_AVAILABLE:
            warning = QLabel(
                "Video playback unavailable. Install PyQt6-Multimedia:\n"
                "  pip install PyQt6-Multimedia"
            )
            warning.setStyleSheet("color: red; padding: 10px;")
            layout.addWidget(warning)
        elif not FFMPEG_AVAILABLE:
            warning = QLabel(
                "FFmpeg not found. Bink video conversion unavailable.\n"
                f"{_ffmpeg_install_hint()}"
            )
            warning.setStyleSheet("color: orange; padding: 10px;")
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

        self.reload_btn = QPushButton("Reload Videos")
        self.reload_btn.clicked.connect(self._load_video_tree)
        game_layout.addWidget(self.reload_btn)

        layout.addLayout(game_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter videos...")
        self.search_edit.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_edit)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._load_video_tree)
        search_layout.addWidget(self.refresh_btn)

        layout.addLayout(search_layout)

        # Splitter for tree and player
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Video file tree
        tree_group = QGroupBox("Video Files")
        tree_layout = QVBoxLayout(tree_group)
        self.video_tree = QTreeWidget()
        self.video_tree.setHeaderLabels(["Video", "Size"])
        self.video_tree.setColumnWidth(0, 300)
        self.video_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.video_tree.itemClicked.connect(self._on_item_clicked)
        tree_layout.addWidget(self.video_tree)
        splitter.addWidget(tree_group)

        # Player panel
        player_group = QGroupBox("Player")
        player_layout = QVBoxLayout(player_group)

        # Video display area
        if MULTIMEDIA_AVAILABLE:
            self.video_widget = QVideoWidget()
            self.video_widget.setMinimumSize(480, 270)
            player_layout.addWidget(self.video_widget, 1)

            # Set up media player
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)
            self.media_player.setVideoOutput(self.video_widget)
            self.media_player.positionChanged.connect(self._on_position_changed)
            self.media_player.durationChanged.connect(self._on_duration_changed)
            self.media_player.playbackStateChanged.connect(self._on_state_changed)
            self.media_player.errorOccurred.connect(self._on_error)
        else:
            placeholder = QLabel("Video player not available")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setMinimumSize(480, 270)
            placeholder.setStyleSheet("background: #f3f5f7; color: #666;")
            player_layout.addWidget(placeholder, 1)
            self.media_player = None

        # Now playing label
        self.now_playing = QLabel("No video selected")
        self.now_playing.setFont(QFont("Sans", 10, QFont.Weight.Bold))
        self.now_playing.setWordWrap(True)
        player_layout.addWidget(self.now_playing)

        # Conversion progress bar (hidden by default)
        self.conversion_progress = QProgressBar()
        self.conversion_progress.setVisible(False)
        self.conversion_progress.setTextVisible(True)
        self.conversion_progress.setFormat("Converting: %p%")
        player_layout.addWidget(self.conversion_progress)

        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setEnabled(False)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self.progress_slider.sliderMoved.connect(self._on_slider_moved)
        player_layout.addWidget(self.progress_slider)

        # Time labels
        time_layout = QHBoxLayout()
        self.time_current = QLabel("0:00")
        self.time_total = QLabel("0:00")
        time_layout.addWidget(self.time_current)
        time_layout.addStretch()
        time_layout.addWidget(self.time_total)
        player_layout.addLayout(time_layout)

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

        player_layout.addLayout(btn_layout)

        # Volume control
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        vol_layout.addWidget(self.volume_slider)
        player_layout.addLayout(vol_layout)

        # File info
        self.file_info = QLabel("")
        self.file_info.setWordWrap(True)
        player_layout.addWidget(self.file_info)

        splitter.addWidget(player_group)
        splitter.setSizes([350, 550])

        layout.addWidget(splitter, 1)  # Give splitter all the stretch

        # Compact status bar (footer style)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px;")
        self.status_label.setMaximumHeight(20)
        layout.addWidget(self.status_label)

    def _format_size(self, size_bytes: int) -> str:
        """Format file size for display"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _load_video_tree(self):
        """Load video files into the tree"""
        self._has_loaded = True
        self.video_tree.clear()
        game_dir = self._get_game_dir()
        self.game_dir_label.setText(str(game_dir) if game_dir else "(not set)")

        if not game_dir.exists():
            self.status_label.setText(f"Game directory not found: {game_dir}")
            return

        video_dir = game_dir / 'data' / 'video'
        if not video_dir.exists():
            self.status_label.setText(f"Video directory not found: {video_dir}")
            return

        added_paths = set()
        total_count = 0

        # === Main Videos (root, excluding numbered cutscenes/briefings) ===
        main_item = QTreeWidgetItem(["Main Videos"])
        main_item.setData(0, Qt.ItemDataRole.UserRole, None)

        for vid_file in sorted(video_dir.glob("*.vid")):
            base = vid_file.stem
            if len(base) == 2 and base.isdigit():
                continue
            if base.startswith("PC_") and base.endswith("_exact"):
                continue
            key = str(vid_file).lower()
            if key in added_paths:
                continue
            added_paths.add(key)
            display_name = self.MAIN_VIDEOS.get(base, base)
            size = self._format_size(vid_file.stat().st_size)
            file_item = QTreeWidgetItem([display_name, size])
            file_item.setData(0, Qt.ItemDataRole.UserRole, vid_file)
            file_item.setToolTip(0, str(vid_file))
            main_item.addChild(file_item)
            total_count += 1

        if main_item.childCount() > 0:
            self.video_tree.addTopLevelItem(main_item)
            main_item.setExpanded(True)

        # === Cutscenes (cutscenes/ dir + root numbered fallback) ===
        cutscene_item = QTreeWidgetItem(["Cutscenes"])
        cutscene_item.setData(0, Qt.ItemDataRole.UserRole, None)

        cutscene_dir = video_dir / "cutscenes"
        if cutscene_dir.exists():
            for vid_file in sorted(cutscene_dir.glob("*.vid"), key=lambda p: int(p.stem) if p.stem.isdigit() else 999):
                key = str(vid_file).lower()
                if key in added_paths:
                    continue
                added_paths.add(key)
                num = vid_file.stem
                display_name = self.CUTSCENE_NAMES.get(num, f"Cutscene {num}")
                size = self._format_size(vid_file.stat().st_size)
                file_item = QTreeWidgetItem([f"{num} - {display_name}", size])
                file_item.setData(0, Qt.ItemDataRole.UserRole, vid_file)
                file_item.setToolTip(0, str(vid_file))
                cutscene_item.addChild(file_item)
                total_count += 1

        for vid_file in sorted(video_dir.glob("*.vid"), key=lambda p: int(p.stem) if p.stem.isdigit() else 999):
            if not (vid_file.stem.isdigit() and len(vid_file.stem) == 2):
                continue
            key = str(vid_file).lower()
            if key in added_paths:
                continue
            added_paths.add(key)
            num = vid_file.stem
            display_name = self.CUTSCENE_NAMES.get(num, f"Cutscene {num}")
            size = self._format_size(vid_file.stat().st_size)
            file_item = QTreeWidgetItem([f"{num} - {display_name}", size])
            file_item.setData(0, Qt.ItemDataRole.UserRole, vid_file)
            file_item.setToolTip(0, str(vid_file))
            cutscene_item.addChild(file_item)
            total_count += 1

        if cutscene_item.childCount() > 0:
            self.video_tree.addTopLevelItem(cutscene_item)

        # === Briefings (briefings/ dir + root fallback) ===
        briefing_item = QTreeWidgetItem(["Mission Briefings"])
        briefing_item.setData(0, Qt.ItemDataRole.UserRole, None)
        briefings_by_episode = {}

        def process_briefing_files(files):
            for vid_file in files:
                key = str(vid_file).lower()
                if key in added_paths:
                    continue
                base = vid_file.stem
                if not (base.startswith("PC_") and base.endswith("_exact")):
                    continue
                added_paths.add(key)
                mission_num = base.replace("PC_", "").replace("_exact", "")
                episode = mission_num[0] if mission_num else "?"
                briefings_by_episode.setdefault(episode, []).append((mission_num, vid_file))

        briefing_dir = video_dir / "briefings"
        if briefing_dir.exists():
            process_briefing_files(list(briefing_dir.glob("*.vid")))
        process_briefing_files(list(video_dir.glob("PC_*_exact.vid")))

        for episode in sorted(briefings_by_episode.keys()):
            episode_item = QTreeWidgetItem([f"Episode {episode}"])
            episode_item.setData(0, Qt.ItemDataRole.UserRole, None)
            for mission_num, vid_file in sorted(briefings_by_episode[episode], key=lambda x: x[0]):
                size = self._format_size(vid_file.stat().st_size)
                file_item = QTreeWidgetItem([f"Mission {mission_num}", size])
                file_item.setData(0, Qt.ItemDataRole.UserRole, vid_file)
                file_item.setToolTip(0, str(vid_file))
                episode_item.addChild(file_item)
                total_count += 1
            briefing_item.addChild(episode_item)

        if briefing_item.childCount() > 0:
            self.video_tree.addTopLevelItem(briefing_item)

        self.status_label.setText(f"Loaded {total_count} videos")

    def ensure_loaded(self):
        """Load video tree on first activation to avoid blocking startup."""
        if not self._has_loaded:
            self._load_video_tree()

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
                    self._load_video_tree()
                    self.gameDirChanged.emit(path)
                else:
                    QMessageBox.warning(self, "Invalid Path", f"Directory does not exist:\n{new_path}")

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle single click - select file"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            self.current_file = file_path
            self.now_playing.setText(f"Selected: {item.text(0)}")
            size_info = self._format_size(file_path.stat().st_size)
            self.file_info.setText(f"Path: {file_path}\nSize: {size_info}")
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

    def _get_converted_path(self, original_path: Path) -> Path:
        """Get path for converted video file"""
        cache_dir = self._get_cache_dir()
        return cache_dir / f"{original_path.stem}.mp4"

    def _play_file(self, file_path: Path):
        """Play a video file - try direct playback first, convert if needed"""
        if not MULTIMEDIA_AVAILABLE:
            QMessageBox.warning(self, "Error", "PyQt6-Multimedia not available")
            return

        # FFmpeg has native Bink decoders - try direct playback first
        # This avoids conversion and preserves original audio quality
        self._try_direct_playback(file_path)

    def _try_direct_playback(self, file_path: Path):
        """Attempt to play file directly without conversion"""
        self.media_player.setSource(QUrl.fromLocalFile(str(file_path)))
        self.audio_output.setVolume(self.volume_slider.value() / 100)

        # Store path for fallback conversion if direct playback fails
        self._pending_file = file_path
        self._direct_playback_attempted = True

        self.media_player.play()

        self.is_playing = True
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("Pause")
        self.stop_btn.setEnabled(True)
        self.progress_slider.setEnabled(True)
        self.now_playing.setText(f"Playing: {file_path.stem}")
        self.playbackStarted.emit()

    def _convert_video(self, vid_path: Path):
        """Convert Bink video to MP4 using ffmpeg"""
        output_path = self._get_converted_path(vid_path)

        self.conversion_progress.setVisible(True)
        self.conversion_progress.setValue(0)
        self.now_playing.setText(f"Converting: {vid_path.stem}...")
        self.play_btn.setEnabled(False)

        # Use QProcess for async conversion
        self.conversion_process = QProcess()
        self.conversion_process.finished.connect(
            lambda code, status: self._on_conversion_finished(code, vid_path, output_path)
        )
        self.conversion_process.readyReadStandardError.connect(self._on_conversion_progress)

        # ffmpeg command for Bink to MP4
        args = [
            '-i', str(vid_path),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',  # Overwrite
            '-progress', 'pipe:2',  # Progress to stderr
            str(output_path)
        ]

        self.conversion_process.start('ffmpeg', args)

    def _on_conversion_progress(self):
        """Update conversion progress"""
        if self.conversion_process:
            # Read stderr for progress info
            data = self.conversion_process.readAllStandardError().data().decode()
            # ffmpeg outputs frame= and time= info we could parse
            # For now, just pulse the progress bar
            current = self.conversion_progress.value()
            if current < 95:
                self.conversion_progress.setValue(current + 5)

    def _on_conversion_finished(self, exit_code: int, original: Path, converted: Path):
        """Handle conversion completion"""
        self.conversion_progress.setVisible(False)
        self.conversion_process = None

        if exit_code == 0 and converted.exists():
            self._play_converted(converted, original.stem)
        else:
            self.now_playing.setText(f"Conversion failed: {original.stem}")
            QMessageBox.critical(
                self, "Conversion Error",
                f"Failed to convert {original.name}\n\n"
                "The video format may not be supported by your ffmpeg installation."
            )
            self.play_btn.setEnabled(True)

    def _play_converted(self, file_path: Path, display_name: str):
        """Play a converted (or directly playable) video file"""
        self.media_player.setSource(QUrl.fromLocalFile(str(file_path)))
        self.audio_output.setVolume(self.volume_slider.value() / 100)
        self.media_player.play()

        self.is_playing = True
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("Pause")
        self.stop_btn.setEnabled(True)
        self.progress_slider.setEnabled(True)
        self.now_playing.setText(f"Playing: {display_name}")
        self.playbackStarted.emit()

    def _play(self):
        """Start playback for the selected file."""
        if not self.media_player:
            return
        if self.current_file:
            self._play_file(self.current_file)

    def _pause_resume(self):
        """Pause or resume playback."""
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
        self._stop_conversion()

    def is_playing_now(self) -> bool:
        return bool(self.is_playing)

    def _stop_conversion(self):
        if self.conversion_process and self.conversion_process.state() != QProcess.ProcessState.NotRunning:
            self.conversion_process.kill()
            self.conversion_process = None
        if hasattr(self, "conversion_progress"):
            self.conversion_progress.setVisible(False)
            self.conversion_progress.setValue(0)

    def _on_volume_changed(self, value: int):
        """Handle volume slider change"""
        if self.media_player and hasattr(self, 'audio_output'):
            self.audio_output.setVolume(value / 100)

    def _format_time(self, ms: int) -> str:
        """Format milliseconds as M:SS"""
        seconds = ms // 1000
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"

    def _on_position_changed(self, position: int):
        """Handle playback position change"""
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
        self.time_current.setText(self._format_time(position))

    def _on_duration_changed(self, duration: int):
        """Handle duration change"""
        self.progress_slider.setRange(0, duration)
        self.time_total.setText(self._format_time(duration))

    def _on_state_changed(self, state):
        """Handle playback state change"""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self.is_playing:
                # Video finished
                self._stop()

    def _on_error(self, error, message):
        """Handle media player error - fallback to conversion if direct playback fails"""
        # If direct playback failed and we have a pending file, try conversion
        if self._direct_playback_attempted and self._pending_file:
            self._direct_playback_attempted = False
            vid_path = self._pending_file
            self._pending_file = None

            # Check if we have a cached conversion
            converted = self._get_converted_path(vid_path)
            if converted.exists():
                self._play_converted(converted, vid_path.stem)
            elif FFMPEG_AVAILABLE:
                self.now_playing.setText(f"Direct playback failed, converting...")
                self._convert_video(vid_path)
            else:
                self.now_playing.setText(f"Playback failed: {message}")
                QMessageBox.warning(
                    self, "Playback Failed",
                    f"Could not play {vid_path.name} directly.\n\n"
                    "Install ffmpeg for conversion fallback:\n"
                    f"  {_ffmpeg_install_hint()}"
                )
        else:
            self.now_playing.setText(f"Error: {message}")

    def _update_position(self):
        """Update playback position (timer callback, unused with QMediaPlayer signals)"""
        pass

    def _on_slider_pressed(self):
        """Handle slider press"""
        pass  # Position updates handled by signals

    def _on_slider_released(self):
        """Handle slider release - seek to position"""
        if self.media_player:
            self.media_player.setPosition(self.progress_slider.value())

    def _on_slider_moved(self, position: int):
        """Handle slider move - update time display"""
        self.time_current.setText(self._format_time(position))

    def _on_search(self, text: str):
        """Filter videos by search text"""
        search_lower = text.lower()

        def filter_item(item: QTreeWidgetItem) -> bool:
            """Recursively filter items"""
            matches = search_lower in item.text(0).lower()

            child_matches = False
            for i in range(item.childCount()):
                child = item.child(i)
                if filter_item(child):
                    child_matches = True

            should_show = matches or child_matches or not text
            item.setHidden(not should_show)

            return matches or child_matches

        for i in range(self.video_tree.topLevelItemCount()):
            filter_item(self.video_tree.topLevelItem(i))

        if not text:
            for i in range(self.video_tree.topLevelItemCount()):
                self.video_tree.topLevelItem(i).setExpanded(True)
