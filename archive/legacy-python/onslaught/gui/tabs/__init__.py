"""
Onslaught Career Editor - GUI Tabs
Individual tab implementations for the main window
"""

from .save_editor import SaveEditorTab
from .save_analyzer import SaveAnalyzerTab
from .lore_browser import LoreBrowserTab
from .audio_player import AudioPlayerTab
from .video_player import VideoPlayerTab
from .settings import SettingsTab
from .binary_patches import BinaryPatchesTab

__all__ = [
    'SaveEditorTab',
    'SaveAnalyzerTab',
    'LoreBrowserTab',
    'AudioPlayerTab',
    'VideoPlayerTab',
    'SettingsTab',
    'BinaryPatchesTab',
]
