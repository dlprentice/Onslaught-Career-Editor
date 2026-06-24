"""
Onslaught Career Editor - Main Window
PyQt6-based GUI for Battle Engine Aquila toolkit
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QStatusBar, QMenuBar, QMenu, QFileDialog, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from ..core.constants import APP_NAME, APP_VERSION
from ..core.config import AppConfig
from .tabs.save_editor import SaveEditorTab
from .tabs.save_analyzer import SaveAnalyzerTab
from .tabs.lore_browser import LoreBrowserTab
from .tabs.audio_player import AudioPlayerTab
from .tabs.video_player import VideoPlayerTab
from .tabs.settings import SettingsTab
from .tabs.binary_patches import BinaryPatchesTab
from .theme import ACCENT_COLOR


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(900, 600)

        self.config = AppConfig.load()

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._on_tab_changed(self.tabs.currentIndex())

    def _setup_ui(self):
        """Set up the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        header = QWidget()
        header.setStyleSheet(
            f"background-color: {ACCENT_COLOR}; border-radius: 6px;"
        )
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(12, 10, 12, 10)

        title = QLabel("Onslaught Toolkit")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: 600;")
        subtitle = QLabel("Battle Engine Aquila (2003) - Save Editor, Configuration Editor, Binary Patches, Lore Browser, Media Player")
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 11px;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)

        # Saves (nested tabs)
        self.save_tabs = QTabWidget()
        self.save_editor_tab = SaveEditorTab()
        self.save_editor_tab.gameDirChanged.connect(self._on_game_dir_changed)
        self.save_tabs.addTab(self.save_editor_tab, "Save Editor")

        self.save_analyzer_tab = SaveAnalyzerTab()
        self.save_analyzer_tab.gameDirChanged.connect(self._on_game_dir_changed)
        self.save_tabs.addTab(self.save_analyzer_tab, "Save Analyzer")

        self.config_editor_tab = SaveEditorTab(configuration_only=True)
        self.config_editor_tab.gameDirChanged.connect(self._on_game_dir_changed)
        self.save_tabs.addTab(self.config_editor_tab, "Configuration Editor")

        self.tabs.addTab(self.save_tabs, "Saves")

        # Media (nested tabs)
        self.media_tabs = QTabWidget()
        self.audio_player_tab = AudioPlayerTab()
        self.audio_player_tab.playbackStarted.connect(lambda: self._on_media_playback_started("audio"))
        self.audio_player_tab.gameDirChanged.connect(self._on_game_dir_changed)
        self.media_tabs.addTab(self.audio_player_tab, "Audio Player")

        self.video_player_tab = VideoPlayerTab()
        self.video_player_tab.playbackStarted.connect(lambda: self._on_media_playback_started("video"))
        self.video_player_tab.gameDirChanged.connect(self._on_game_dir_changed)
        self.media_tabs.addTab(self.video_player_tab, "Video Player")

        self.tabs.addTab(self.media_tabs, "Media")

        # Lore tab
        self.lore_browser_tab = LoreBrowserTab()
        self.tabs.addTab(self.lore_browser_tab, "Lore")

        # Binary patches tab
        self.binary_patches_tab = BinaryPatchesTab()
        self.tabs.addTab(self.binary_patches_tab, "Binary Patches")

        # Settings tab
        self.settings_tab = SettingsTab()
        self.settings_tab.gameDirChanged.connect(self._on_game_dir_changed)
        self.tabs.addTab(self.settings_tab, "Settings")

        # Restore window and tab state
        self._restore_window_state()

        # Track tab changes for status + last-tab persistence
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.save_tabs.currentChanged.connect(self._on_tab_changed)
        self.media_tabs.currentChanged.connect(self._on_tab_changed)

    def _setup_menu(self):
        """Set up the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Save/Options File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        analyze_action = QAction("&Analyze Save/Options...", self)
        analyze_action.triggered.connect(self._on_analyze)
        tools_menu.addAction(analyze_action)

        compare_action = QAction("&Compare Files...", self)
        compare_action.triggered.connect(self._on_compare)
        tools_menu.addAction(compare_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self):
        """Set up the status bar"""
        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: white;")
        self.setStatusBar(self.statusbar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: white;")
        self.game_dir_label = QLabel("")
        self.game_dir_label.setStyleSheet("color: white;")
        self.game_dir_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.statusbar.addWidget(self.status_label, 1)
        self.statusbar.addPermanentWidget(self.game_dir_label)
        self._update_footer()

    def _on_open_file(self):
        """Handle File > Open"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Save/Options File",
            "",
            "BEA Save/Options Files (*.bes *.bea);;All Files (*)"
        )
        if filename:
            self.open_path(Path(filename))

    def _on_analyze(self):
        """Handle Tools > Analyze"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Save/Options File to Analyze",
            "",
            "BEA Save/Options Files (*.bes *.bea);;All Files (*)"
        )
        if filename:
            path = Path(filename)
            self.status_label.setText(f"Analyzing: {filename}")
            # Load file into Save Analyzer tab and switch to it
            self.save_analyzer_tab.load_file(path)
            self.tabs.setCurrentWidget(self.save_tabs)
            self.save_tabs.setCurrentWidget(self.save_analyzer_tab)

    def _on_compare(self):
        """Handle Tools > Compare"""
        left_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Base File to Compare",
            "",
            "BEA Save/Options Files (*.bes *.bea);;All Files (*)"
        )
        if not left_name:
            return

        right_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Compare File",
            "",
            "BEA Save/Options Files (*.bes *.bea);;All Files (*)"
        )
        if not right_name:
            return

        self.compare_paths(Path(left_name), Path(right_name))

    def _on_about(self):
        """Handle Help > About"""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version {APP_VERSION}</p>"
            f"<p>A comprehensive toolkit for Battle Engine Aquila (2003)</p>"
            f"<p>Features:</p>"
            f"<ul>"
            f"<li>Save file editing and analysis</li>"
            f"<li>Binary patching for display/windowed behavior</li>"
            f"<li>Lore and documentation browser</li>"
            f"<li>Audio and video playback</li>"
            f"</ul>"
            f"<p>Created by the BEA reverse engineering community</p>"
            f"<p>Source code provided by Stuart Gillam (Lost Toys)</p>"
        )

    def _restore_window_state(self):
        """Restore window size and last selected tab from config."""
        if self.config.window_width > 0 and self.config.window_height > 0:
            self.resize(self.config.window_width, self.config.window_height)

        if 0 <= self.config.last_tab < self.tabs.count():
            self.tabs.setCurrentIndex(self.config.last_tab)

    def _update_footer(self):
        """Refresh footer labels based on config."""
        game_dir = self.config.get_game_dir()
        if game_dir:
            self.game_dir_label.setText(f"Game: {game_dir}")
        else:
            self.game_dir_label.setText("Game directory not set")

    def open_path(self, path: Path) -> bool:
        """Open a save/options file into the correct editor tab."""
        if not path.exists():
            self.status_label.setText(f"Open failed: missing {path.name}")
            return False

        is_options = path.suffix.lower() == ".bea"
        target_tab = self.config_editor_tab if is_options else self.save_editor_tab
        target_tab.load_file(path)
        self.tabs.setCurrentWidget(self.save_tabs)
        self.save_tabs.setCurrentWidget(target_tab)
        self.status_label.setText(f"Opened: {path.name}")
        return True

    def compare_paths(self, left: Path, right: Path) -> bool:
        """Open two files in the analyzer and execute compare immediately."""
        if not left.exists() or not right.exists():
            missing = left if not left.exists() else right
            self.status_label.setText(f"Compare failed: missing {missing.name}")
            return False

        self.tabs.setCurrentWidget(self.save_tabs)
        self.save_tabs.setCurrentWidget(self.save_analyzer_tab)
        self.save_analyzer_tab.compare_files(left, right)
        self.status_label.setText(f"Compared: {left.name} vs {right.name}")
        return True

    def _on_game_dir_changed(self, path: Path):
        """Handle game directory updates from Settings tab."""
        self.config = AppConfig.load()
        self._update_footer()
        # Refresh media tabs if available
        try:
            self.audio_player_tab._load_audio_tree()
        except Exception:
            pass
        try:
            self.video_player_tab._load_video_tree()
        except Exception:
            pass
        try:
            self.binary_patches_tab.refresh_from_config(force=False)
        except Exception:
            pass

    def _on_tab_changed(self, index: int):
        """Update status when tab changes and persist last tab."""
        sender = self.sender()
        if sender == self.tabs:
            if 0 <= index < self.tabs.count():
                tab_text = self.tabs.tabText(index)
                detail_text = tab_text

                current_widget = self.tabs.widget(index)
                if hasattr(current_widget, "ensure_loaded"):
                    current_widget.ensure_loaded()
                if isinstance(current_widget, QTabWidget):
                    sub_index = current_widget.currentIndex()
                    if sub_index >= 0:
                        detail_text = f"{tab_text} → {current_widget.tabText(sub_index)}"
                    selected = current_widget.currentWidget()
                    if hasattr(selected, "ensure_loaded"):
                        selected.ensure_loaded()

                self.status_label.setText(f"{detail_text} tab active")
                self.config.last_tab = index
                self.config.save()
            self._apply_media_policy_for_main_tab()
        else:
            # Nested tab changed; refresh status based on current main tab + sub-tab
            main_index = self.tabs.currentIndex()
            if 0 <= main_index < self.tabs.count():
                tab_text = self.tabs.tabText(main_index)
                detail_text = tab_text
                current_widget = self.tabs.widget(main_index)
                if isinstance(current_widget, QTabWidget):
                    sub_index = current_widget.currentIndex()
                    if sub_index >= 0:
                        detail_text = f"{tab_text} → {current_widget.tabText(sub_index)}"
                self.status_label.setText(f"{detail_text} tab active")
            if isinstance(sender, QTabWidget):
                selected = sender.currentWidget()
                if hasattr(selected, "ensure_loaded"):
                    selected.ensure_loaded()
            if sender == self.media_tabs:
                self._apply_media_policy_for_media_tab()

    def _apply_media_policy_for_main_tab(self):
        config = AppConfig.load()
        current_widget = self.tabs.currentWidget()
        if current_widget is not self.media_tabs:
            if not config.allow_background_audio:
                self.audio_player_tab.stop_playback()
            if not config.allow_background_video:
                self.video_player_tab.stop_playback()

    def _apply_media_policy_for_media_tab(self):
        config = AppConfig.load()
        current_widget = self.media_tabs.currentWidget()
        if current_widget is self.audio_player_tab:
            if not config.allow_background_video:
                self.video_player_tab.stop_playback()
        elif current_widget is self.video_player_tab:
            if not config.allow_background_audio:
                self.audio_player_tab.stop_playback()

    def _on_media_playback_started(self, kind: str):
        config = AppConfig.load()
        if not config.prevent_audio_video_overlap:
            return
        if kind == "audio":
            self.video_player_tab.stop_playback()
        else:
            self.audio_player_tab.stop_playback()

    def apply_media_policy_now(self):
        self._apply_media_policy_for_main_tab()
        self._apply_media_policy_for_media_tab()
        config = AppConfig.load()
        if config.prevent_audio_video_overlap and self.audio_player_tab.is_playing_now() and self.video_player_tab.is_playing_now():
            self.video_player_tab.stop_playback()

    def closeEvent(self, event):
        """Persist window size and last tab on close."""
        self.config.window_width = self.width()
        self.config.window_height = self.height()
        self.config.last_tab = self.tabs.currentIndex()
        self.config.save()
        try:
            self.audio_player_tab.stop_playback()
            self.video_player_tab.stop_playback()
        except Exception:
            pass
        super().closeEvent(event)
