"""
Onslaught Career Editor - Configuration Management
Handles game directory detection and user settings
"""

import json
import platform
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field, fields

from .constants import BES_FILE_SIZE, BES_VERSION_WORD


# Default Steam installation paths by platform
DEFAULT_STEAM_PATHS = {
    'Windows': [
        Path(r'C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila'),
        Path(r'C:\Program Files\Steam\steamapps\common\Battle Engine Aquila'),
        Path(r'D:\Steam\steamapps\common\Battle Engine Aquila'),
        Path(r'D:\SteamLibrary\steamapps\common\Battle Engine Aquila'),
        Path(r'E:\Steam\steamapps\common\Battle Engine Aquila'),
        Path(r'E:\SteamLibrary\steamapps\common\Battle Engine Aquila'),
    ],
    'Linux': [
        Path.home() / '.steam/steam/steamapps/common/Battle Engine Aquila',
        Path.home() / '.local/share/Steam/steamapps/common/Battle Engine Aquila',
    ],
}

# Save file locations relative to game directory
SAVE_SUBDIRS = [
    '',           # Root of game folder
    'saves',      # Common save folder
    'Save',       # Alternative
    'savegames',  # Steam/retail save directory
]

# Config file location
def _get_config_dirs() -> tuple[Path, Path]:
    """Return (primary, legacy) config directories."""
    if platform.system() == 'Windows':
        base = Path.home() / 'AppData' / 'Roaming'
    else:
        base = Path.home() / '.config'

    primary = base / 'OnslaughtCareerEditor'
    legacy = base / 'onslaught-career-editor'
    return primary, legacy


def get_config_dir() -> Path:
    """Get the config directory for this application"""
    config_dir, _legacy = _get_config_dirs()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Get the path to the config file"""
    return get_config_dir() / 'config.json'


def get_legacy_config_path() -> Path:
    """Get the legacy config path (pre-parity naming)."""
    _primary, legacy = _get_config_dirs()
    return legacy / 'config.json'

_CAMEL_TO_SNAKE = {
    'gameDirectory': 'game_directory',
    'recentFiles': 'recent_files',
    'maxRecentFiles': 'max_recent_files',
    'windowWidth': 'window_width',
    'windowHeight': 'window_height',
    'lastTab': 'last_tab',
    'allowBackgroundAudio': 'allow_background_audio',
    'allowBackgroundVideo': 'allow_background_video',
    'preventAudioVideoOverlap': 'prevent_audio_video_overlap',
}


def _normalize_config_data(data: dict, config_cls: type) -> dict:
    """Normalize config keys to snake_case and drop unknown fields."""
    if not isinstance(data, dict):
        return {}

    normalized = {}
    for key, value in data.items():
        normalized[_CAMEL_TO_SNAKE.get(key, key)] = value

    allowed = {f.name for f in fields(config_cls)}
    return {k: normalized[k] for k in allowed if k in normalized}


@dataclass
class AppConfig:
    """Application configuration"""
    game_directory: Optional[str] = None
    recent_files: List[str] = field(default_factory=list)
    max_recent_files: int = 10

    # Window state
    window_width: int = 900
    window_height: int = 600
    last_tab: int = 0

    allow_background_audio: bool = True
    allow_background_video: bool = False
    prevent_audio_video_overlap: bool = True

    def save(self) -> bool:
        """Save config to disk."""
        config_path = get_config_path()
        try:
            with open(config_path, 'w') as f:
                json.dump(self.to_json_dict(), f, indent=2)
            return True
        except OSError:
            return False

    def to_json_dict(self) -> dict:
        """Serialize to JSON using the C#-compatible camelCase schema."""
        return {
            'gameDirectory': self.game_directory,
            'recentFiles': self.recent_files,
            'maxRecentFiles': self.max_recent_files,
            'windowWidth': self.window_width,
            'windowHeight': self.window_height,
            'lastTab': self.last_tab,
            'allowBackgroundAudio': self.allow_background_audio,
            'allowBackgroundVideo': self.allow_background_video,
            'preventAudioVideoOverlap': self.prevent_audio_video_overlap,
        }

    @classmethod
    def load(cls) -> 'AppConfig':
        """Load config from disk, or create default"""
        primary_path = get_config_path()
        legacy_path = get_legacy_config_path()

        for path in (primary_path, legacy_path):
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                    normalized = _normalize_config_data(data, cls)
                    config = cls(**normalized)
                    # Migrate legacy config to primary path for parity with C# app
                    if path == legacy_path and not primary_path.exists():
                        config.save()
                    return config
                except (json.JSONDecodeError, TypeError, OSError):
                    pass
        return cls()

    def add_recent_file(self, path: Path):
        """Add a file to recent files list"""
        path_str = str(path)
        if path_str in self.recent_files:
            self.recent_files.remove(path_str)
        self.recent_files.insert(0, path_str)
        self.recent_files = self.recent_files[:self.max_recent_files]
        self.save()

    def get_game_dir(self) -> Optional[Path]:
        """Get configured game directory as Path"""
        if self.game_directory:
            path = Path(self.game_directory)
            if path.exists() and path.is_dir():
                return path
        return None

    def set_game_dir(self, path: Path) -> bool:
        """Set and persist game directory."""
        if not path.exists() or not path.is_dir():
            return False
        self.game_directory = str(path)
        return self.save()


def detect_game_directory() -> Optional[Path]:
    """Auto-detect Battle Engine Aquila installation"""
    system = platform.system()
    paths = DEFAULT_STEAM_PATHS.get(system, [])

    for path in paths:
        if path.exists() and path.is_dir():
            # Verify it's actually BEA by checking for known files
            if (path / 'BEA.exe').exists() or (path / 'data').exists():
                return path

    return None


def find_save_files(game_dir: Optional[Path] = None) -> List[Path]:
    """Find .bes/.bea save/options files in the game directory and common locations."""
    saves: List[Path] = []
    dirs_to_search: List[Path] = []

    if game_dir is None:
        config = AppConfig.load()
        game_dir = config.get_game_dir()

    if game_dir is None:
        game_dir = detect_game_directory()

    if game_dir is not None and game_dir.exists():
        for subdir in SAVE_SUBDIRS:
            dirs_to_search.append(game_dir / subdir if subdir else game_dir)

    # Also search Documents and LocalAppData on Windows for parity with C#
    if platform.system() == 'Windows':
        dirs_to_search.extend([
            Path.home() / 'Documents' / 'Battle Engine Aquila',
            Path.home() / 'AppData' / 'Local' / 'Battle Engine Aquila',
        ])

    for search_dir in dirs_to_search:
        try:
            if search_dir.exists():
                saves.extend(search_dir.glob('*.bes'))
                saves.extend(search_dir.glob('*.bea'))
        except (OSError, PermissionError):
            continue

    # Remove duplicates and sort by modification time (newest first)
    seen = set()
    unique_saves = []
    for save in saves:
        try:
            key = str(save.resolve())
        except OSError:
            key = str(save)
        if platform.system() == 'Windows':
            key = key.lower()
        if key not in seen:
            seen.add(key)
            unique_saves.append(save)

    def _safe_mtime(path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    return sorted(unique_saves, key=_safe_mtime, reverse=True)


def get_save_info(path: Path) -> dict:
    """Get basic info about a save file without full parsing"""
    stat = path.stat()
    is_valid = False
    if stat.st_size == BES_FILE_SIZE:
        try:
            with path.open('rb') as f:
                header = f.read(2)
            is_valid = len(header) == 2 and int.from_bytes(header, 'little') == BES_VERSION_WORD
        except OSError:
            is_valid = False

    return {
        'path': path,
        'name': path.stem,
        'size': stat.st_size,
        'modified': stat.st_mtime,
        'valid': is_valid,
    }
