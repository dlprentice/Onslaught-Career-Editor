"""
Onslaught Career Editor - BES File Parser
Handles reading and writing Battle Engine Aquila save files
"""

import struct
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from .constants import (
    BES_FILE_SIZE, BES_VERSION_WORD,
    OFFSET_VERSION, OFFSET_NODES, OFFSET_LINKS, OFFSET_GOODIES,
    OFFSET_KILLS, OFFSET_SLOTS,
    OFFSET_OPTIONS_ENTRIES, OPTIONS_TAIL_SIZE,
    OFFSET_NEW_GOODIE_COUNT,
    OFFSET_CAREER_IN_PROGRESS, OFFSET_SOUND_VOLUME, OFFSET_MUSIC_VOLUME,
    OFFSET_GOD_MODE_ENABLED,
    OFFSET_INVERT_Y_P1, OFFSET_INVERT_Y_P2,
    OFFSET_INVERT_FLIGHT_P1, OFFSET_INVERT_FLIGHT_P2,
    OFFSET_VIBRATION_P1, OFFSET_VIBRATION_P2,
    OFFSET_CONTROLLER_CONFIG_P1, OFFSET_CONTROLLER_CONFIG_P2,
    OFFSET_MYSTERY_HEADER_START, OFFSET_MYSTERY_HEADER_END,
    NODE_SIZE, LINK_SIZE, GOODIE_SIZE,
    MAX_NODES, MAX_LINKS, MAX_GOODIES, MAX_SLOTS, NUM_KILL_CATEGORIES,
    NUM_LEVELS, RANK_VALUES, KILL_CATEGORIES, KILL_THRESHOLDS,
    GOODIE_UNKNOWN, GOODIE_INSTRUCTIONS_SHOWN, GOODIE_NEW, GOODIE_OLD,
    GOODIE_DISPLAYABLE_COUNT,
)


@dataclass
class CareerNode:
    """Represents a single mission node in the save file"""
    index: int
    state: int = 0
    complete: int = 0
    lower_link: int = 0
    higher_link: int = 0
    world_number: int = 0
    base_things_exists: list = field(default_factory=lambda: [0] * 9)
    num_attempts: int = 0
    ranking: int = 0

    @property
    def is_complete(self) -> bool:
        return self.complete != 0

    @property
    def rank_letter(self) -> str:
        """Decode the ranking float bits to a letter grade (true dword view)."""
        for rank, float_bits in RANK_VALUES.items():
            if self.ranking == float_bits:
                return rank

        float_val = struct.unpack('<f', struct.pack('<I', self.ranking))[0]

        if float_val >= 0.9:
            return f"~S ({float_val:.2f})"
        if float_val >= 0.7:
            return f"~A ({float_val:.2f})"
        if float_val >= 0.5:
            return f"~B ({float_val:.2f})"
        if float_val >= 0.25:
            return f"~C ({float_val:.2f})"
        if float_val >= 0.1:
            return f"~D ({float_val:.2f})"
        if float_val > 0:
            return f"~D ({float_val:.2f})"
        if float_val == 0:
            return "E"
        if float_val < 0:
            return "NONE"
        return f"? ({float_val:.2f})"


@dataclass
class CareerLink:
    """Represents a link between mission nodes"""
    index: int
    to_node: int = 0
    link_type: int = 0

    @property
    def is_complete(self) -> bool:
        return self.to_node != 0xFFFFFFFF and self.link_type != 0


@dataclass
class BesFile:
    """Represents a complete BES save file"""
    path: Optional[Path] = None
    raw_data: bytes = b''

    version: int = 0  # version word (0x4BD1)
    header_dword_view: int = 0
    version_valid: bool = False
    file_size: int = 0

    # CCareer header fields (at start of CCareer dump)
    new_goodie_count_raw: int = 0

    # God mode toggle state (cheat-gated; not sufficient by itself)
    god_mode_enabled_raw: int = 0
    god_mode_enabled: bool = False

    # CCareer tail fields (within the fixed 0x24BC-byte CCareer copy)
    career_in_progress_raw: int = 0
    career_in_progress: bool = False
    sound_volume_bits: int = 0
    sound_volume: float = 0.0
    music_volume_bits: int = 0
    music_volume: float = 0.0
    invert_y_axis_raw: list = field(default_factory=lambda: [0, 0])
    invert_flight_raw: list = field(default_factory=lambda: [0, 0])
    vibration_raw: list = field(default_factory=lambda: [0, 0])
    controller_config_num: list = field(default_factory=lambda: [0, 0])
    options_entry_count: int = 0
    options_tail_start: int = 0
    options_entries_size: int = 0
    options_control_scheme_index: int = 0
    options_mouse_sensitivity_bits: int = 0
    options_mouse_sensitivity: float = 0.0
    options_screen_shape: int = 0
    options_d3d_device_index: int = 0

    nodes: list = field(default_factory=list)
    links: list = field(default_factory=list)
    goodies: list = field(default_factory=list)
    kills: list = field(default_factory=list)
    kills_meta: list = field(default_factory=list)
    slots: list = field(default_factory=list)

    @classmethod
    def load(cls, path: Path, strict_version: bool = True) -> 'BesFile':
        """Load a BES file from disk"""
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        data = path.read_bytes()

        if len(data) != BES_FILE_SIZE:
            raise ValueError(f"Invalid file size: {len(data)} (expected {BES_FILE_SIZE})")

        bes = cls(path=path, raw_data=data, file_size=len(data))
        bes._parse(strict_version=strict_version)
        return bes

    def _parse(self, strict_version: bool = True):
        """Parse the raw data into structured fields"""
        data = self.raw_data

        # Header (version word + dword view for debugging)
        self.version = struct.unpack_from('<H', data, OFFSET_VERSION)[0]
        self.header_dword_view = struct.unpack_from('<I', data, OFFSET_VERSION)[0]
        self.version_valid = (self.version == BES_VERSION_WORD)

        if strict_version and not self.version_valid:
            raise ValueError(
                f"Invalid version word: 0x{self.version:04X} (expected 0x{BES_VERSION_WORD:04X}); "
                f"header dword view=0x{self.header_dword_view:08X}"
            )

        # CCareer header (first dword of the CCareer dump)
        self.new_goodie_count_raw = struct.unpack_from('<I', data, OFFSET_NEW_GOODIE_COUNT)[0]

        # Parse nodes
        self.nodes = []
        for i in range(MAX_NODES):
            offset = OFFSET_NODES + (i * NODE_SIZE)
            node = CareerNode(index=i)
            node.state = struct.unpack_from('<I', data, offset + 0x00)[0]
            node.complete = struct.unpack_from('<I', data, offset + 0x04)[0]
            node.lower_link = struct.unpack_from('<I', data, offset + 0x08)[0]
            node.higher_link = struct.unpack_from('<I', data, offset + 0x0C)[0]
            node.world_number = struct.unpack_from('<I', data, offset + 0x10)[0]
            node.base_things_exists = list(struct.unpack_from('<9I', data, offset + 0x14))
            node.num_attempts = struct.unpack_from('<I', data, offset + 0x38)[0]
            node.ranking = struct.unpack_from('<I', data, offset + 0x3C)[0]
            self.nodes.append(node)

        # Parse links
        self.links = []
        for i in range(MAX_LINKS):
            offset = OFFSET_LINKS + (i * LINK_SIZE)
            link = CareerLink(index=i)
            link.link_type = struct.unpack_from('<I', data, offset + 0x00)[0]
            link.to_node = struct.unpack_from('<I', data, offset + 0x04)[0]
            self.links.append(link)

        # Parse goodies
        self.goodies = []
        for i in range(MAX_GOODIES):
            offset = OFFSET_GOODIES + (i * GOODIE_SIZE)
            state = struct.unpack_from('<I', data, offset)[0]
            self.goodies.append(state)

        # Parse kills
        self.kills = []
        self.kills_meta = []
        for i in range(NUM_KILL_CATEGORIES):
            offset = OFFSET_KILLS + (i * 4)
            raw = struct.unpack_from('<I', data, offset)[0]
            self.kills_meta.append((raw >> 24) & 0xFF)
            self.kills.append(raw & 0x00FFFFFF)

        # Parse slots
        self.slots = []
        for i in range(MAX_SLOTS):
            offset = OFFSET_SLOTS + (i * 4)
            slot = struct.unpack_from('<I', data, offset)[0]
            self.slots.append(slot)

        # CCareer settings at end of fixed CCareer block
        self.career_in_progress_raw = struct.unpack_from('<I', data, OFFSET_CAREER_IN_PROGRESS)[0]
        self.career_in_progress = self.career_in_progress_raw != 0

        self.sound_volume_bits = struct.unpack_from('<I', data, OFFSET_SOUND_VOLUME)[0]
        self.sound_volume = struct.unpack_from('<f', data, OFFSET_SOUND_VOLUME)[0]

        self.music_volume_bits = struct.unpack_from('<I', data, OFFSET_MUSIC_VOLUME)[0]
        self.music_volume = struct.unpack_from('<f', data, OFFSET_MUSIC_VOLUME)[0]

        self.invert_y_axis_raw = [
            struct.unpack_from('<I', data, OFFSET_INVERT_Y_P1)[0],
            struct.unpack_from('<I', data, OFFSET_INVERT_Y_P2)[0],
        ]
        self.invert_flight_raw = [
            struct.unpack_from('<I', data, OFFSET_INVERT_FLIGHT_P1)[0],
            struct.unpack_from('<I', data, OFFSET_INVERT_FLIGHT_P2)[0],
        ]
        self.vibration_raw = [
            struct.unpack_from('<I', data, OFFSET_VIBRATION_P1)[0],
            struct.unpack_from('<I', data, OFFSET_VIBRATION_P2)[0],
        ]
        self.controller_config_num = [
            struct.unpack_from('<I', data, OFFSET_CONTROLLER_CONFIG_P1)[0],
            struct.unpack_from('<I', data, OFFSET_CONTROLLER_CONFIG_P2)[0],
        ]

        # Options entries + fixed tail snapshot layout.
        self.options_tail_start = self.file_size - OPTIONS_TAIL_SIZE
        self.options_entries_size = self.options_tail_start - OFFSET_OPTIONS_ENTRIES
        if self.options_entries_size >= 0 and (self.options_entries_size % 0x20) == 0:
            self.options_entry_count = self.options_entries_size // 0x20
            self.options_mouse_sensitivity_bits = struct.unpack_from('<I', data, self.options_tail_start + 0x04)[0]
            self.options_mouse_sensitivity = struct.unpack_from('<f', data, self.options_tail_start + 0x04)[0]
            self.options_control_scheme_index = struct.unpack_from('<H', data, self.options_tail_start + 0x08)[0]
            self.options_screen_shape = struct.unpack_from('<I', data, self.options_tail_start + 0x20)[0]
            self.options_d3d_device_index = struct.unpack_from('<I', data, self.options_tail_start + 0x28)[0]
        else:
            self.options_entry_count = 0
            self.options_tail_start = 0
            self.options_entries_size = 0

        # God mode toggle state (persisted menu toggle; runtime behavior is cheat-gated)
        self.god_mode_enabled_raw = struct.unpack_from('<I', data, OFFSET_GOD_MODE_ENABLED)[0]
        self.god_mode_enabled = self.god_mode_enabled_raw != 0

    def get_stats(self) -> dict:
        """Get summary statistics about the save file"""
        used_nodes = [n for n in self.nodes if n.world_number != 0]
        completed_nodes = sum(1 for n in used_nodes if n.is_complete)
        partial_nodes = sum(1 for n in used_nodes if not n.is_complete)

        used_links = [l for l in self.links if l.to_node != 0xFFFFFFFF]
        completed_links = sum(1 for l in used_links if l.is_complete)

        # Count goodies by state
        displayable_goodies = self.goodies[:GOODIE_DISPLAYABLE_COUNT]
        goodie_new = sum(1 for g in displayable_goodies if g == GOODIE_NEW)
        goodie_old = sum(1 for g in displayable_goodies if g == GOODIE_OLD)
        goodie_locked = sum(1 for g in displayable_goodies if g == GOODIE_UNKNOWN)
        goodie_instructions = sum(1 for g in displayable_goodies if g == GOODIE_INSTRUCTIONS_SHOWN)
        goodie_other = len(displayable_goodies) - goodie_new - goodie_old - goodie_locked - goodie_instructions
        goodie_reserved = len(self.goodies) - len(displayable_goodies)

        # Rank distribution
        ranks = {}
        for node in used_nodes:
            if node.is_complete:
                rank = node.rank_letter
                if rank.startswith('~'):
                    # Normalize approximate labels ("~S (0.95)") into canonical buckets.
                    rank = rank[1:2] if len(rank) > 1 else '?'
                ranks[rank] = ranks.get(rank, 0) + 1

        # Next unlock thresholds per category
        next_thresholds = []
        for i, cat in enumerate(KILL_CATEGORIES):
            thresholds = KILL_THRESHOLDS.get(cat, [])
            current = self.kills[i]
            next_val = None
            for t in thresholds:
                if current < t:
                    next_val = t
                    break
            next_thresholds.append(next_val)

        # Tech slots
        active_slots = sum(1 for s in self.slots if s != 0)

        # Mystery regions summary
        mystery_regions = []
        regions = [
            ("CCareerHeader", OFFSET_MYSTERY_HEADER_START, OFFSET_MYSTERY_HEADER_END, "CCareer header dword0 (NewGoodieCount; increments when unlocking goodies)"),
        ]
        for name, start, end, desc in regions:
            region_data = self.raw_data[start:end]
            all_zeros = all(b == 0 for b in region_data)
            all_ff = all(b == 0xFF for b in region_data)
            non_zero = sum(1 for b in region_data if b != 0)
            mystery_regions.append({
                'name': name,
                'start': start,
                'end': end,
                'size': end - start,
                'description': desc,
                'all_zeros': all_zeros,
                'all_ff': all_ff,
                'non_zero': non_zero,
            })

        return {
            'file_path': str(self.path) if self.path else None,
            'is_options_file': bool(self.path and (self.path.suffix.lower() == ".bea" or self.path.name.lower().startswith("defaultoptions.bea"))),
            'version_word': f"0x{self.version:04X}",
            'header_dword_view': f"0x{self.header_dword_view:08X}",
            'file_size': self.file_size,
            'version_valid': self.version_valid,
            'new_goodie_count_raw': self.new_goodie_count_raw,
            'career_in_progress': self.career_in_progress,
            'career_in_progress_raw': self.career_in_progress_raw,
            'sound_volume': self.sound_volume,
            'sound_volume_bits': self.sound_volume_bits,
            'music_volume': self.music_volume,
            'music_volume_bits': self.music_volume_bits,
            'invert_y_axis_raw': self.invert_y_axis_raw,
            'invert_flight_raw': self.invert_flight_raw,
            'vibration_raw': self.vibration_raw,
            'controller_config_num': self.controller_config_num,
            'options_entry_count': self.options_entry_count,
            'options_tail_start': self.options_tail_start,
            'options_entries_size': self.options_entries_size,
            'options_control_scheme_index': self.options_control_scheme_index,
            'options_mouse_sensitivity_bits': self.options_mouse_sensitivity_bits,
            'options_mouse_sensitivity': self.options_mouse_sensitivity,
            'options_screen_shape': self.options_screen_shape,
            'options_d3d_device_index': self.options_d3d_device_index,
            'completed_missions': completed_nodes,
            'used_missions': len(used_nodes),
            'total_missions': MAX_NODES,
            'completed_links': completed_links,
            'used_links': len(used_links),
            'partial_nodes': partial_nodes,
            'goodies_new': goodie_new,
            'goodies_old': goodie_old,
            'goodies_instructions': goodie_instructions,
            'goodies_locked': goodie_locked,
            'goodies_other': goodie_other,
            'goodies_reserved': goodie_reserved,
            'kills': dict(zip(KILL_CATEGORIES, self.kills)),
            'total_kills': sum(self.kills),
            'next_unlock_thresholds': next_thresholds,
            'rank_distribution': ranks,
            'god_mode_enabled': self.god_mode_enabled,
            'god_mode_enabled_raw': self.god_mode_enabled_raw,
            'tech_slots_active': active_slots,
            'tech_slots_total': MAX_SLOTS,
            'mystery_regions': mystery_regions,
        }
