"""
Onslaught Career Editor - Core Module
BES file handling, configuration, and shared utilities
"""

from .constants import (
    APP_NAME, APP_VERSION,
    BES_FILE_SIZE, BES_VERSION_WORD, BES_VERSION_STAMP_DWORD_VIEW,
    RANK_VALUES, KILL_THRESHOLDS,
)
from .bes_file import BesFile, CareerNode, CareerLink
from .config import (
    AppConfig, detect_game_directory, find_save_files, get_save_info,
)

__all__ = [
    'APP_NAME', 'APP_VERSION',
    'BES_FILE_SIZE', 'BES_VERSION_WORD', 'BES_VERSION_STAMP_DWORD_VIEW',
    'RANK_VALUES', 'KILL_THRESHOLDS',
    'BesFile', 'CareerNode', 'CareerLink',
    'AppConfig', 'detect_game_directory', 'find_save_files', 'get_save_info',
]
