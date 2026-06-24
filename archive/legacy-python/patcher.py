#!/usr/bin/env python3
"""
Onslaught Career Editor - CLI Patcher
Battle Engine Aquila (2003) save file editor

Usage:
    python3 patcher.py input.bes output.bes [options]
    python3 patcher.py defaultoptions.bea output.bea [options]
    python3 patcher.py --analyze input.bes
    python3 patcher.py --analyze defaultoptions.bea
    python3 patcher.py --list-goodies input.bes
    python3 patcher.py --list-goodies input.bes --show-reserved-goodies

Modes:
    Patch Mode (default): Modify a save file
    Analyze Mode (--analyze): Display current save state without modifying
    Goodie List Mode (--list-goodies): Print per-slot goodie states

Patch Options:
    --new           Mark goodies as NEW instead of OLD
    --kills N       Set kill count for all categories (default: 100)
    --rank GRADE    Set rank for all missions (S/A/B/C/D/E, default: S)

Selective Patching:
    --kills-only         Only patch kill counts (preserve nodes, links, goodies)
    --no-nodes           Skip patching mission nodes
    --no-links           Skip patching mission links
    --no-goodies         Skip patching goodies
    --no-kills           Skip patching kill counts

Advanced Options:
    --level-rank N:GRADE  Set specific node index rank (1-43). Can be repeated.
    --aircraft-kills N    Override aircraft kill count
    --vehicle-kills N     Override vehicle kill count
    --emplacement-kills N Override emplacement kill count
    --infantry-kills N    Override infantry kill count
    --mech-kills N        Override mech kill count

Career Settings Overrides (optional; omit to preserve existing save values):
    --sound-volume V                    Set sound volume (0.0-1.0, float)
    --music-volume V                    Set music volume (0.0-1.0, float)
    --invert-walker-p1/--invert-y-p1   Set invert Y (Walker) for player 1
    --invert-walker-p2/--invert-y-p2   Set invert Y (Walker) for player 2
    --invert-flight-p1                  Set invert Y (Flight/Jet) for player 1
    --invert-flight-p2                  Set invert Y (Flight/Jet) for player 2
    --vibration-p1                      Set controller vibration for player 1
    --vibration-p2                      Set controller vibration for player 2
    --controller-config-p1 N            Set controller config index for player 1 (uint32)
    --controller-config-p2 N            Set controller config index for player 2 (uint32)
    --experimental-pending-extra-goodies N  Experimental placeholder (currently ignored)

Options Entries + Tail Snapshot (control bindings, mouse sensitivity, screen shape):
    --copy-options-from FILE         Copy options entries + tail snapshot from another .bes/.bea file
    --no-copy-options-entries        With --copy-options-from: do not copy options entries (`0x20*N`, typically `0x200`)
    --no-copy-options-tail           With --copy-options-from: do not copy the fixed 0x56-byte options tail snapshot
"""

import argparse
import math
import struct
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from onslaught.core.constants import APP_VERSION

# Layout constants
# File format confirmed via Ghidra static analysis of BEA.exe (Feb 2026)
#
# IMPORTANT: "true dword view"
# - CCareer bytes are copied from source+2 (CCareer::Load) and saved to dest+2 (CCareer::Save).
# - That means all CCareer dwords on disk are aligned to offsets where (file_offset % 4 == 2).
# - If you view the file at 4-byte aligned offsets (file_offset % 4 == 0), values *look* like
#   "shift-16", but that is just a misaligned view of the same bytes.
EXPECTED_FILE_SIZE = 10004  # Exact size of valid BEA save/options file (Steam build)

CAREER_BASE = 0x0002  # File offset where the CCareer memory dump begins (after 16-bit version word)

# CCareer offsets (in-memory) from BEA.exe, plus file mapping: file_off = CAREER_BASE + mem_off
CCAREER_NEW_GOODIE_COUNT = 0x0000   # CCareer header dword0 (increments when unlocking goodies)
CCAREER_NODE_BASE = 0x0004          # CCareerNode[100] x 64 bytes
CCAREER_LINK_BASE = 0x1904          # CCareerNodeLink[200] x 8 bytes
CCAREER_GOODIE_BASE = 0x1F44        # CGoodie[300] x 4 bytes
CCAREER_KILLS_BASE = 0x23F4         # Kill counters[5] x 4 bytes
CCAREER_TECH_SLOTS_BASE = 0x2408    # mSlots[32] x 4 bytes
CCAREER_CAREER_IN_PROGRESS = 0x2488
CCAREER_SOUND_VOLUME = 0x248C
CCAREER_MUSIC_VOLUME = 0x2490
CCAREER_GOD_MODE_ENABLED = 0x2494   # God mode toggle state (g_bGodModeEnabled in Ghidra)
# Steam build per-player toggles (verified in BEA.exe Controls UI):
# - Walker mode invert Y axis (action code 0x38): P1=CCareer+0x24A4, P2=CCareer+0x24A8
# - Flight/Jet mode invert Y axis (action code 0x39): P1=CCareer+0x249C, P2=CCareer+0x24A0
# - Controller vibration toggles: P1=CCareer+0x24AC, P2=CCareer+0x24B0
CCAREER_WALKER_INVERT_Y_P1 = 0x24A4
CCAREER_WALKER_INVERT_Y_P2 = 0x24A8
CCAREER_FLIGHT_INVERT_Y_P1 = 0x249C
CCAREER_FLIGHT_INVERT_Y_P2 = 0x24A0
CCAREER_VIBRATION_P1 = 0x24AC
CCAREER_VIBRATION_P2 = 0x24B0
CCAREER_CONTROLLER_CONFIG_P1 = 0x24B4
CCAREER_CONTROLLER_CONFIG_P2 = 0x24B8

NODE_BASE = CAREER_BASE + CCAREER_NODE_BASE
NODE_SIZE = 64
NODE_COUNT = 100
NUM_LEVELS = 43

LINK_BASE = CAREER_BASE + CCAREER_LINK_BASE
LINK_SIZE = 8
LINK_COUNT = 200

GOODIE_BASE = CAREER_BASE + CCAREER_GOODIE_BASE
GOODIE_COUNT = 300
# Retail goodies gallery can surface slot 232 (FMV 33) in addition to 0..231.
GOODIE_DISPLAYABLE_COUNT = 233  # Indices 0-232 map to displayable goodies

KILLS_BASE = CAREER_BASE + CCAREER_KILLS_BASE
KILLS_COUNT = 5

# Kill category offsets (from KILLS_BASE)
# Index: 0=Aircraft, 1=Vehicles, 2=Emplacements, 3=Infantry, 4=Mechs
KILL_AIRCRAFT = 0
KILL_VEHICLES = 1
KILL_EMPLACEMENTS = 2
KILL_INFANTRY = 3
KILL_MECHS = 4

# NOTE (Feb 2026): The legacy 4-byte-aligned view placed "goodie 228" at 0x22D4 and
# "mCareerInProgress" at 0x2488; both are artifacts of misalignment.
# In the true dword view, Goodie 228 is at 0x22D6 and mCareerInProgress is at 0x248A.
# Patch using true view offsets only.

# Tech slots (mSlots[32]) - 128 bytes immediately after kill counters
TECH_SLOTS_BASE = CAREER_BASE + CCAREER_TECH_SLOTS_BASE
TECH_SLOTS_COUNT = 32

# God mode flags (persisted, but retail builds appear to gate god mode via runtime save-name checks)
GOD_MODE_ENABLED_OFFSET = CAREER_BASE + CCAREER_GOD_MODE_ENABLED
INVERT_Y_P1_OFFSET = CAREER_BASE + CCAREER_WALKER_INVERT_Y_P1
INVERT_Y_P2_OFFSET = CAREER_BASE + CCAREER_WALKER_INVERT_Y_P2
INVERT_FLIGHT_P1_OFFSET = CAREER_BASE + CCAREER_FLIGHT_INVERT_Y_P1
INVERT_FLIGHT_P2_OFFSET = CAREER_BASE + CCAREER_FLIGHT_INVERT_Y_P2
VIBRATION_P1_OFFSET = CAREER_BASE + CCAREER_VIBRATION_P1
VIBRATION_P2_OFFSET = CAREER_BASE + CCAREER_VIBRATION_P2
CONTROLLER_CONFIG_P1_OFFSET = CAREER_BASE + CCAREER_CONTROLLER_CONFIG_P1
CONTROLLER_CONFIG_P2_OFFSET = CAREER_BASE + CCAREER_CONTROLLER_CONFIG_P2

SOUND_VOLUME_OFFSET = CAREER_BASE + CCAREER_SOUND_VOLUME
MUSIC_VOLUME_OFFSET = CAREER_BASE + CCAREER_MUSIC_VOLUME

# Version stamp (BEA.exe validates only the low 16-bit word at file offset 0)
VERSION_WORD = 0x4BD1

# Mystery regions - bytes we intentionally do not interpret/modify yet.
# Note: the file tail (options entries + 0x56-byte OptionsTail snapshot) is *not* a mystery region anymore.
# See: reverse-engineering/save-file/save-format.md (Region 3).
MYSTERY_REGIONS = [
    ("CCareerHeader", 0x0002, 0x0006, "CCareer header dword0 (increments when unlocking goodies; see Cutscene_UnlockGoodie_* in BEA.exe)"),
]

# Goodie states (true dword view)
GOODIE_UNKNOWN = 0
GOODIE_INSTRUCTIONS = 1
GOODIE_NEW = 2  # Gold badge
GOODIE_OLD = 3  # Blue badge


def classify_goodie_state(index: int, raw: int) -> str:
    """Classify one goodie slot raw value into a stable state label."""
    if index >= GOODIE_DISPLAYABLE_COUNT:
        return "RESERVED"
    if raw == GOODIE_NEW:
        return "NEW"
    if raw == GOODIE_OLD:
        return "OLD"
    if raw == GOODIE_UNKNOWN:
        return "LOCKED"
    if raw == GOODIE_INSTRUCTIONS:
        return "INSTRUCTIONS"
    return "OTHER"

# Node ranking float bit patterns (true dword view, raw IEEE-754 float at node+0x3C)
RANK_FLOAT_BITS = {
    "S": 0x3F800000,    # 1.0
    "A": 0x3F4CCCCD,    # 0.8
    "B": 0x3F19999A,    # 0.6
    "C": 0x3EB33333,    # 0.35
    "D": 0x3E19999A,    # 0.15
    "E": 0x00000000,    # 0.0
    "NONE": 0xBF800000, # -1.0 (never completed)
}


def write_u32(buf: bytearray, offset: int, value: int) -> None:
    """Write a 32-bit little-endian value."""
    struct.pack_into('<I', buf, offset, value)


def read_u32(buf: bytearray, offset: int) -> int:
    """Read a 32-bit little-endian value."""
    return struct.unpack_from('<I', buf, offset)[0]


def read_u16(buf: bytearray, offset: int) -> int:
    """Read a 16-bit little-endian value."""
    return struct.unpack_from('<H', buf, offset)[0]


def write_f32(buf: bytearray, offset: int, value: float) -> None:
    """Write a 32-bit IEEE-754 float (little-endian)."""
    struct.pack_into('<f', buf, offset, float(value))


def read_f32(buf: bytearray, offset: int) -> float:
    """Read a 32-bit IEEE-754 float (little-endian)."""
    return struct.unpack_from('<f', buf, offset)[0]


def compute_options_layout(file_size: int) -> tuple[int, int, int]:
    """
    Compute (entry_count, tail_start, entries_size) for the options entries + tail snapshot.

    Retail Steam build layout:
    - options entries start at 0x24BE
    - entries are 0x20 bytes each
    - tail is fixed 0x56 bytes at end of file
    - total file size is 0x2514 + 0x20*N
    """
    options_start = 0x24BE
    entry_size = 0x20
    tail_size = 0x56
    base_size = options_start + tail_size  # 0x2514

    if file_size < base_size:
        raise ValueError(f"File too small for options layout: 0x{file_size:X} (< 0x{base_size:X}).")

    extra = file_size - base_size
    if extra % entry_size != 0:
        raise ValueError(
            f"Invalid options layout: file_size=0x{file_size:X} is not 0x{base_size:X} + 0x{entry_size:X}*N."
        )

    n = extra // entry_size
    entries_size = n * entry_size
    tail_start = options_start + entries_size

    # Sanity: tail is last 0x56 bytes.
    if tail_start != file_size - tail_size:
        raise ValueError(
            f"Invalid tail location: computed tail_start=0x{tail_start:X}, expected 0x{(file_size - tail_size):X}."
        )

    return n, tail_start, entries_size


@dataclass
class OptionsEntrySlotOverride:
    device_code: Optional[int] = None
    packed_key: Optional[int] = None


@dataclass
class OptionsEntryOverride:
    slot0: OptionsEntrySlotOverride = field(default_factory=OptionsEntrySlotOverride)
    slot1: OptionsEntrySlotOverride = field(default_factory=OptionsEntrySlotOverride)


# ---- Options entries key parsing (matches BesFilePatcher.TryParseKeyboardPackedKey) ----
# Packed key format: (vk << 16) | scan.
# Notes:
# - scan codes observed are Set-1/DIK-like.
# - Arrow keys appear as scan+0x80 with vk=0 (e.g., Left=0xCB).
KEY_NAME_MAP: dict[str, tuple[int, int]] = {
    "Up": (0, 0x00C8),
    "Down": (0, 0x00D0),
    "Left": (0, 0x00CB),
    "Right": (0, 0x00CD),
    "Tab": (0, 0x000F),
    "Space": (ord(" "), 0x0039),
    "CapsLock": (0, 0x003A),
    "LShift": (0, 0x002A),
    "RShift": (0, 0x0036),
    "RControl": (0, 0x009D),
    "-": (ord("-"), 0x000C),
    "Minus": (ord("-"), 0x000C),
    "=": (ord("="), 0x000D),
    "Equals": (ord("="), 0x000D),
    "+": (ord("+"), 0x000D),  # plus shares '=' physical key; vk differs by shift
}

KEY_NAME_MAP_LOWER: dict[str, tuple[int, int]] = {
    k.lower(): v for k, v in KEY_NAME_MAP.items()
}

LETTER_SCAN: dict[str, int] = {
    "A": 0x001E, "B": 0x0030, "C": 0x002E, "D": 0x0020, "E": 0x0012, "F": 0x0021, "G": 0x0022,
    "H": 0x0023, "I": 0x0017, "J": 0x0024, "K": 0x0025, "L": 0x0026, "M": 0x0032, "N": 0x0031,
    "O": 0x0018, "P": 0x0019, "Q": 0x0010, "R": 0x0013, "S": 0x001F, "T": 0x0014, "U": 0x0016,
    "V": 0x002F, "W": 0x0011, "X": 0x002D, "Y": 0x0015, "Z": 0x002C,
}

DIGIT_SCAN: dict[str, int] = {
    "1": 0x0002, "2": 0x0003, "3": 0x0004, "4": 0x0005, "5": 0x0006, "6": 0x0007, "7": 0x0008,
    "8": 0x0009, "9": 0x000A, "0": 0x000B,
}

NUMPAD_DIGIT_SCAN: dict[str, int] = {
    "7": 0x0047, "8": 0x0048, "9": 0x0049,
    "4": 0x004B, "5": 0x004C, "6": 0x004D,
    "1": 0x004F, "2": 0x0050, "3": 0x0051,
    "0": 0x0052,
}


def parse_keyboard_packed_key(raw: str) -> int:
    """
    Parse a human-friendly key like:
      A, Key A, Num7, Numpad7, Up, Tab, Space, CapsLock, RShift, RControl, -, =
    Returns packed_key (vk<<16)|scan. '-' (dash) returns 0 (unbound).
    """
    if raw is None:
        raise ValueError("empty key")

    t = raw.strip()
    if not t:
        raise ValueError("empty key")

    if t.lower() in ("-", "none"):
        return 0

    # Allow "Key X" prefix (matches in-game UI style).
    if t.lower().startswith("key "):
        t = t[4:].strip()

    # Allow analyzer fallback format for unknown keyboard tokens:
    # "vk=0x0000 scan=0x0052"
    tl = t.lower()
    if tl.startswith("vk=0x"):
        parts = tl.split()
        if len(parts) == 2 and parts[0].startswith("vk=0x") and parts[1].startswith("scan=0x"):
            try:
                vk = int(parts[0][5:], 16) & 0xFFFF
                scan = int(parts[1][7:], 16) & 0xFFFF
                return (vk << 16) | scan
            except ValueError:
                pass

    # Numpad shorthand (Num7 / Num 7 / Numpad7).
    tn = t.replace(" ", "")
    if tn.lower().startswith("num"):
        rest = tn[3:]
        if rest.lower().startswith("pad"):
            rest = rest[3:]
        if len(rest) == 1 and rest in NUMPAD_DIGIT_SCAN:
            vk = ord(rest)
            scan = NUMPAD_DIGIT_SCAN[rest]
            return (vk << 16) | scan

    mapped = KEY_NAME_MAP_LOWER.get(t.lower())
    if mapped is not None:
        vk, scan = mapped
        return (vk << 16) | scan

    # Single printable character.
    if len(t) == 1:
        c = t.upper()
        if c in LETTER_SCAN:
            vk = ord(c)
            scan = LETTER_SCAN[c]
            return (vk << 16) | scan
        if c in DIGIT_SCAN:
            vk = ord(c)
            scan = DIGIT_SCAN[c]
            return (vk << 16) | scan
        # Common punctuation (extend as needed)
        if c == ";":
            return (ord(c) << 16) | 0x0027
        if c == "'":
            return (ord(c) << 16) | 0x0028
        if c == ",":
            return (ord(c) << 16) | 0x0033
        if c == ".":
            return (ord(c) << 16) | 0x0034
        if c == "/":
            return (ord(c) << 16) | 0x0035
        if c == "\\":
            return (ord(c) << 16) | 0x002B
        if c == "`":
            return (ord(c) << 16) | 0x0029

    raise ValueError(
        f"Unrecognized key '{raw}'. Examples: A, Num7, Up, Tab, Space, CapsLock, RShift, RControl, '-', '='."
    )


def _parse_look_mouse(entry_id: int) -> tuple[int, int]:
    # Steam preset uses:
    # - device 11: positive direction, device 12: negative direction
    # - packed_key scan: 0 => X axis, 1 => Y axis
    return {
        0x1B: (11, 0),  # Look Right (MouseX+)
        0x19: (12, 0),  # Look Left  (MouseX-)
        0x1A: (11, 1),  # Look Up    (MouseY+)
        0x1C: (12, 1),  # Look Down  (MouseY-)
    }[entry_id]


def _parse_look_token(entry_id: int, token: str) -> tuple[int, int]:
    """
    Look bindings accept:
    - "Mouse" (simple UI token; row/entry decides axis+dir)
    - "MouseX+/MouseX-/MouseY+/MouseY-" (explicit axis+direction, matches analyzer output)
    """
    t = token.strip()
    tl = t.lower()

    if tl in ("mouse", "mousex", "mousey"):
        return _parse_look_mouse(entry_id)

    if tl.startswith("mousex"):
        # X axis: scan=0
        key = 0
        if tl.endswith("-"):
            return 12, key
        if tl.endswith("+"):
            return 11, key
        return _parse_look_mouse(entry_id)

    if tl.startswith("mousey"):
        # Y axis: scan=1
        key = 1
        if tl.endswith("-"):
            return 12, key
        if tl.endswith("+"):
            return 11, key
        return _parse_look_mouse(entry_id)

    if tl.startswith("mouse(") and tl.endswith(")"):
        inner = tl[len("mouse("):-1]
        try:
            scan_signed = int(inner, 10)
        except ValueError:
            scan_signed = None
        if scan_signed is not None:
            dev_default, _ = _parse_look_mouse(entry_id)
            return dev_default, scan_signed & 0xFFFFFFFF

    raise ValueError(f"Invalid look binding '{token}'. Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key.")


def _parse_zoom_mouse_wheel(token: str) -> tuple[int, int]:
    if token.lower() == "mousewheelup":
        return 16, 3
    if token.lower() == "mousewheeldown":
        return 16, 4
    raise ValueError(f"Invalid zoom binding '{token}'. Use MouseWheelUp/MouseWheelDown or a keyboard key.")


def _parse_mouse_button(entry_id: int, token: str) -> tuple[int, int]:
    if token.lower() == "mouseleft":
        # Steam build uses these device codes for Fire weapon:
        # - entry 0x12: dev 17, key 0
        # - entry 0x13: dev 15, key 0
        if entry_id == 0x12:
            return 17, 0
        if entry_id == 0x13:
            return 15, 0
        raise ValueError("MouseLeft is only supported for Fire weapon (entry 0x12/0x13).")

    if token.lower() == "mouseright":
        # Steam build uses device 16 scan 2 for Select weapon.
        if entry_id == 0x14:
            return 16, 2
        raise ValueError("MouseRight is only supported for Select weapon (entry 0x14).")

    raise ValueError(f"Invalid mouse binding '{token}'. Use MouseLeft/MouseRight.")


def apply_options_entry_overrides(buf: bytearray, overrides: dict[int, OptionsEntryOverride]) -> None:
    """
    Apply keybind edits to the 0x20-byte options entries block and force ControlSchemeIndex=0.
    Mirrors BesFilePatcher.ApplyOptionsEntryOverrides().
    """
    if not overrides:
        return

    n, tail_start, _entries_size = compute_options_layout(len(buf))
    options_start = 0x24BE
    entry_size = 0x20

    entry_offsets: dict[int, int] = {}
    for i in range(n):
        off = options_start + entry_size * i
        entry_id = struct.unpack_from("<i", buf, off + 0x04)[0]
        entry_offsets[entry_id] = off

    scheme_index = read_u16(buf, tail_start + 0x08)

    if scheme_index not in (0, 1):
        raise ValueError(f"Options entry overrides only support ControlSchemeIndex 0 or 1. Found: {scheme_index}.")

    def _apply_one(entry_id: int, ov: OptionsEntryOverride) -> None:
        eoff = entry_offsets.get(entry_id)
        if eoff is None:
            raise ValueError(f"Options entry_id 0x{entry_id:X} not found in file.")

        flags = read_u32(buf, eoff + 0x00)
        flags = (flags & 0xFFFFFF00) | 1
        write_u32(buf, eoff + 0x00, flags)

        if ov.slot0.device_code is not None:
            write_u32(buf, eoff + 0x0C, int(ov.slot0.device_code) & 0xFFFFFFFF)
        if ov.slot0.packed_key is not None:
            write_u32(buf, eoff + 0x10, int(ov.slot0.packed_key) & 0xFFFFFFFF)
        if ov.slot1.device_code is not None:
            write_u32(buf, eoff + 0x18, int(ov.slot1.device_code) & 0xFFFFFFFF)
        if ov.slot1.packed_key is not None:
            write_u32(buf, eoff + 0x1C, int(ov.slot1.packed_key) & 0xFFFFFFFF)

    # Steam build: Fire weapon remaps both entry_id 0x12 and 0x13.
    has12 = 0x12 in overrides
    has13 = 0x13 in overrides

    for entry_id, ov in overrides.items():
        _apply_one(entry_id, ov)
        if entry_id == 0x12 and not has13:
            _apply_one(0x13, ov)
        elif entry_id == 0x13 and not has12:
            _apply_one(0x12, ov)

    # Force "Custom" scheme when patching bindings so the two slots map consistently to P1/P2.
    struct.pack_into("<H", buf, tail_start + 0x08, 0)


def set_slot_bit(buf: bytearray, slot_index: int, bit_index: int, on: bool) -> None:
    """
    Enable/disable a specific bit in a tech slot.

    Args:
        buf: The save file buffer
        slot_index: Tech slot index (0-31)
        bit_index: Bit index within the slot (0-31)
        on: True to set the bit, False to clear it
    """
    if not (0 <= slot_index < TECH_SLOTS_COUNT):
        return
    if not (0 <= bit_index < 32):
        return

    offset = TECH_SLOTS_BASE + slot_index * 4
    current = read_u32(buf, offset)
    mask = 1 << bit_index

    if on:
        new_val = current | mask
    else:
        new_val = current & ~mask

    write_u32(buf, offset, new_val)


def patch_node(buf: bytearray, offset: int, node_index: int, rank: str = 'S') -> None:
    """
    Patch a node to mark it as completed with the specified rank display.

    BEA.exe uses the "true dword view" where the node stores:
    - +0x04 mComplete (raw int 0/1)
    - +0x38 mNumAttempts (raw int)
    - +0x3C mRanking (raw float)

    We intentionally do NOT modify:
    - +0x00 state/flags (island-start/etc; not fully mapped)
    - +0x14..+0x37 mBaseThingsExists[9] (level-specific persistence bits)
    """
    rank_bits = RANK_FLOAT_BITS.get(rank.upper(), RANK_FLOAT_BITS["S"])
    write_u32(buf, offset + 0x04, 1)        # complete
    write_u32(buf, offset + 0x38, 0)        # attempts
    write_u32(buf, offset + 0x3C, rank_bits)  # float bits


def patch_file(input_path: Path, output_path: Path,
		               new_goodies: bool = False,
		               kill_count: int = 100,
		               rank: str = 'S',
		               level_ranks: Optional[dict] = None,
		               per_category_kills: Optional[dict] = None,
		               patch_nodes: bool = True,
		               patch_links: bool = True,
		               patch_goodies: bool = True,
		               patch_kills: bool = True,
		               sound_volume: Optional[float] = None,
		               music_volume: Optional[float] = None,
		               invert_y_p1: Optional[bool] = None,
		               invert_y_p2: Optional[bool] = None,
		               invert_flight_p1: Optional[bool] = None,
		               invert_flight_p2: Optional[bool] = None,
		               vibration_p1: Optional[bool] = None,
		               vibration_p2: Optional[bool] = None,
		               controller_config_p1: Optional[int] = None,
		               controller_config_p2: Optional[int] = None,
		                   copy_options_from: Optional[Path] = None,
		                   copy_options_entries: bool = True,
		                   copy_options_tail: bool = True,
		                   options_entry_overrides: Optional[dict[int, OptionsEntryOverride]] = None) -> None:
    """
    Apply patches to a BES save file. Each section can be toggled independently.

    Args:
        input_path: Path to input .bes file
        output_path: Path to output .bes file
        new_goodies: Mark goodies as NEW (gold) instead of OLD (blue)
        kill_count: Default kill count for all categories
        rank: Default rank for all levels (S/A/B/C/D/E/NONE)
	        level_ranks: Dict mapping zero-based node index -> rank for per-level overrides (from CLI/UI 1-43 input)
        per_category_kills: Dict mapping category index -> kill count for per-category overrides
        patch_nodes: Patch mission nodes (unlock levels, set ranks)
	        patch_links: Patch mission links (unlock paths)
	        patch_goodies: Patch goodies (unlock gallery items)
	        patch_kills: Patch kill counts (for kill-based unlocks)

	        sound_volume: Override sound volume (0.0-1.0). None preserves existing.
	        music_volume: Override music volume (0.0-1.0). None preserves existing.
	        invert_y_p1: Override invert Y (Walker) for P1 (bool). None preserves existing.
	        invert_y_p2: Override invert Y (Walker) for P2 (bool). None preserves existing.
	        invert_flight_p1: Override invert Y (Flight/Jet) for P1 (bool). None preserves existing.
	        invert_flight_p2: Override invert Y (Flight/Jet) for P2 (bool). None preserves existing.
	        vibration_p1: Override controller vibration for P1 (bool). None preserves existing.
	        vibration_p2: Override controller vibration for P2 (bool). None preserves existing.
	        controller_config_p1: Override controller config index for P1 (uint32). None preserves existing.
	        controller_config_p2: Override controller config index for P2 (uint32). None preserves existing.

	        copy_options_from: Copy the options entries + tail snapshot from another file (same size/layout).
        copy_options_entries: When copying, include the full options entries region (0x20*N bytes at 0x24BE).
	        copy_options_tail: When copying, include the fixed 0x56-byte tail snapshot at file_size-0x56.
	        options_entry_overrides: Optional per-entry keybind overrides (options entries). When provided, the patcher
	            normalizes preset schemes (if needed) and forces ControlSchemeIndex=0 for deterministic P1/P2 columns.
	    """

    if input_path.resolve() == output_path.resolve():
        raise ValueError("Refusing to patch in place. Please choose a different output path.")

    # Read input
    buf = bytearray(input_path.read_bytes())

    # Validate file size (strict check)
    if len(buf) != EXPECTED_FILE_SIZE:
        raise ValueError(
            f"Invalid .bes file: expected {EXPECTED_FILE_SIZE} bytes, got {len(buf)}. "
            f"This may not be a valid Battle Engine Aquila career save file."
        )

    version_word = read_u16(buf, 0x0000)
    if version_word != VERSION_WORD:
        raise ValueError(
            f"Invalid .bes version word: expected 0x{VERSION_WORD:04X}, got 0x{version_word:04X}."
        )

    # NOTE: God mode in retail builds is primarily cheat-gated at runtime (save-name substring checks).
    # Persisted per-player flags from Stuart's internal source are not yet mapped reliably for the Steam build.

    # Patch nodes (mark completed + set rank float). Supports per-level rank overrides via level_ranks dict.
    if patch_nodes:
        for n in range(NODE_COUNT):
            offset = NODE_BASE + n * NODE_SIZE
            if offset + NODE_SIZE <= len(buf):
                world = read_u32(buf, offset + 0x10)
                if world == 0:
                    # Unused node slots in retail saves; avoid touching unknown padding.
                    continue
                # Use per-level rank if specified, otherwise default rank
                node_rank = rank
                if level_ranks and n in level_ranks:
                    node_rank = level_ranks[n]
                patch_node(buf, offset, n, node_rank)

    # Mark all links as complete (minimal change).
    # Link layout (true view): [0]=linkState/type, [4]=toNode (0xFFFFFFFF for unused).
    # We avoid clobbering link types (values like 2 appear in real saves).
    if patch_links:
        for link in range(LINK_COUNT):
            offset = LINK_BASE + link * LINK_SIZE
            to_node = read_u32(buf, offset + 4)
            if to_node == 0xFFFFFFFF:
                continue
            current = read_u32(buf, offset)
            if current == 0:
                write_u32(buf, offset, 1)

    # Unlock all goodies (true view: states are raw ints 0/1/2/3).
    if patch_goodies:
        goodie_state = GOODIE_NEW if new_goodies else GOODIE_OLD
        for g in range(GOODIE_DISPLAYABLE_COUNT):
            offset = GOODIE_BASE + g * 4
            write_u32(buf, offset, goodie_state)

    # NOTE (Feb 2026): In true dword view, mCareerInProgress is at 0x248A.
    # The historical 4-byte-aligned view placed "mCareerInProgress" at 0x2488 and "goodie 228" at 0x22D4.
    # Do not write to legacy aligned offsets like 0x22D4; patch using true view offsets only.

    # Set kill counts (per-category if specified, otherwise all same).
    # True view encoding: stored_value = (meta << 24) | (kills & 0x00FFFFFF)
    # Load clamps meta for the first two counters but preserves the lower 24 bits.
    if patch_kills:
        for k in range(KILLS_COUNT):
            # Use per-category override if specified, otherwise default
            kills = kill_count
            if per_category_kills and k in per_category_kills:
                kills = per_category_kills[k]
            if kills < 0:
                kills = 0
            if kills > 0x00FFFFFF:
                kills = 0x00FFFFFF
            offset = KILLS_BASE + k * 4
            current = read_u32(buf, offset)
            meta = current & 0xFF000000
            write_u32(buf, offset, meta | (kills & 0x00FFFFFF))

    # Optional CCareer settings overrides (only written when explicitly set)
    if sound_volume is not None:
        v = float(sound_volume)
        if not math.isfinite(v):
            raise ValueError("Sound volume must be a finite float.")
        v = max(0.0, min(1.0, v))
        write_f32(buf, SOUND_VOLUME_OFFSET, v)

    if music_volume is not None:
        v = float(music_volume)
        if not math.isfinite(v):
            raise ValueError("Music volume must be a finite float.")
        v = max(0.0, min(1.0, v))
        write_f32(buf, MUSIC_VOLUME_OFFSET, v)

    # Steam build stores these toggles as normal booleans: 0=Off, non-zero=On.
    if invert_y_p1 is not None:
        write_u32(buf, INVERT_Y_P1_OFFSET, 1 if invert_y_p1 else 0)
    if invert_y_p2 is not None:
        write_u32(buf, INVERT_Y_P2_OFFSET, 1 if invert_y_p2 else 0)

    if invert_flight_p1 is not None:
        write_u32(buf, INVERT_FLIGHT_P1_OFFSET, 1 if invert_flight_p1 else 0)
    if invert_flight_p2 is not None:
        write_u32(buf, INVERT_FLIGHT_P2_OFFSET, 1 if invert_flight_p2 else 0)

    if vibration_p1 is not None:
        write_u32(buf, VIBRATION_P1_OFFSET, 1 if vibration_p1 else 0)
    if vibration_p2 is not None:
        write_u32(buf, VIBRATION_P2_OFFSET, 1 if vibration_p2 else 0)

    if controller_config_p1 is not None:
        if not (0 <= int(controller_config_p1) <= 0xFFFFFFFF):
            raise ValueError("controller_config_p1 must be in range 0..0xFFFFFFFF.")
        write_u32(buf, CONTROLLER_CONFIG_P1_OFFSET, int(controller_config_p1))

    if controller_config_p2 is not None:
        if not (0 <= int(controller_config_p2) <= 0xFFFFFFFF):
            raise ValueError("controller_config_p2 must be in range 0..0xFFFFFFFF.")
        write_u32(buf, CONTROLLER_CONFIG_P2_OFFSET, int(controller_config_p2))

    # Optional: copy options entries + tail snapshot from another file (raw byte copy).
    if copy_options_from is not None:
        src = bytearray(Path(copy_options_from).read_bytes())
        if len(src) != len(buf):
            raise ValueError(
                f"Options copy requires matching file sizes. Source={len(src):,} bytes, Dest={len(buf):,} bytes."
            )

        n_dest, tail_start_dest, entries_size_dest = compute_options_layout(len(buf))
        n_src, tail_start_src, entries_size_src = compute_options_layout(len(src))
        if (n_src, tail_start_src, entries_size_src) != (n_dest, tail_start_dest, entries_size_dest):
            raise ValueError(
                f"Options copy requires matching options layout. Source entries={n_src}, Dest entries={n_dest}."
            )

        options_start = 0x24BE
        if copy_options_entries:
            buf[options_start:options_start + entries_size_dest] = src[options_start:options_start + entries_size_dest]
        if copy_options_tail:
            buf[tail_start_dest:] = src[tail_start_dest:]

    # Optional: patch keybinds in the options entries block.
    if options_entry_overrides:
        apply_options_entry_overrides(buf, options_entry_overrides)

    # Write output
    output_path.write_bytes(buf)


def parse_level_rank_entries(values: list[str], valid_ranks: set[str]) -> tuple[Optional[dict], list[str]]:
    """Parse level-rank entries like ['1:A','42:S'] into a dict and validation errors."""
    if not values:
        return None, []

    result: dict[int, str] = {}
    errors: list[str] = []

    for entry in values:
        parts = entry.split(':')
        if len(parts) != 2:
            errors.append(
                f"Error: Invalid --level-rank entry '{entry}', expected NODE_INDEX:GRADE (e.g., 1:S)."
            )
            continue
        try:
            level = int(parts[0])
        except ValueError:
            errors.append(
                f"Error: Invalid node index '{parts[0]}' in --level-rank entry '{entry}', expected 1-{NUM_LEVELS}."
            )
            continue
        if level < 1 or level > NUM_LEVELS:
            errors.append(
                f"Error: Node index {level} out of range (1-{NUM_LEVELS}) in --level-rank entry '{entry}'."
            )
            continue
        rank = parts[1].upper()
        if rank not in valid_ranks:
            errors.append(
                f"Error: Invalid rank '{parts[1]}' for node index {level}. Valid values: S, A, B, C, D, E, NONE."
            )
            continue
        # CLI/UI input is 1-based (1..43); patcher internals use zero-based node indexes.
        result[level - 1] = rank

    return (result if result else None), errors


def parse_tri_bool(value: Optional[str], option_name: str) -> Optional[bool]:
    """
    Parse a tri-state boolean option from CLI:
    - None -> None (preserve)
    - keep/preserve/unchanged -> None (preserve)
    - on/true/1/yes -> True
    - off/false/0/no -> False
    """
    if value is None:
        return None
    v = value.strip().lower()
    if v in ("keep", "preserve", "unchanged"):
        return None
    if v in ("on", "true", "1", "yes", "y"):
        return True
    if v in ("off", "false", "0", "no", "n"):
        return False
    raise ValueError(f"{option_name}: expected on/off/true/false/1/0/yes/no/y/n (or omit to preserve).")


def is_options_like_path(path: Path) -> bool:
    name = path.name.lower()
    return path.suffix.lower() == ".bea" or name.startswith("defaultoptions.bea")


def decode_rank(rank_bits: int) -> str:
    """
    Decode a node grade from the raw float bits at node+0x3C (true dword view).
    Returns a grade letter or a best-effort approximation string.
    """
    for grade, bits in RANK_FLOAT_BITS.items():
        if rank_bits == bits:
            return grade

    float_val = struct.unpack('<f', struct.pack('<I', rank_bits & 0xFFFFFFFF))[0]
    if float_val >= 0.9:
        return f"~S ({float_val:.2f})"
    if float_val >= 0.7:
        return f"~A ({float_val:.2f})"
    if float_val >= 0.5:
        return f"~B ({float_val:.2f})"
    if float_val >= 0.25:
        return f"~C ({float_val:.2f})"
    if float_val > 0:
        return f"~D ({float_val:.2f})"
    if float_val == 0:
        return "E"
    if float_val < 0:
        return "NONE"
    return f"? ({float_val:.2f})"


def get_next_unlock_threshold(category: int, current_kills: int) -> Optional[int]:
    """Get the next unlock threshold for a kill category, or None if all unlocked."""
    thresholds = {
        KILL_AIRCRAFT: [25, 50, 75, 100],
        KILL_VEHICLES: [100, 200, 300, 400],
        KILL_EMPLACEMENTS: [25, 50],  # 75 appears only in combined unlocks (handled elsewhere)
        KILL_INFANTRY: [40, 80, 160],
        KILL_MECHS: [20, 40, 80],
    }
    for threshold in thresholds.get(category, []):
        if current_kills < threshold:
            return threshold
    return None


def hex_dump(buf: bytearray, start: int, end: int, bytes_per_line: int = 16) -> str:
    """Generate a hex dump of a buffer region."""
    lines = []
    for offset in range(start, end, bytes_per_line):
        chunk = buf[offset:min(offset + bytes_per_line, end)]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"  {offset:04X}: {hex_part:<{bytes_per_line*3}}  {ascii_part}")
    return '\n'.join(lines)


def analyze_mystery_regions(buf: bytearray, dump_hex: bool = False) -> str:
    """Analyze reserved/unmapped regions (summary + optional hex dump)."""
    lines = []
    total_size = sum(end - start for _name, start, end, _desc in MYSTERY_REGIONS)
    lines.append(f"\nUNMAPPED / RESERVED REGIONS ({total_size} bytes total)")
    lines.append("-" * 60)

    for name, start, end, desc in MYSTERY_REGIONS:
        size = end - start
        lines.append(f"\n  {name}: 0x{start:04X} - 0x{end:04X} ({size} bytes)")
        lines.append(f"  Description: {desc}")
        lines.append("")

        # Check if region is all zeros, all 0xFF, or has data
        region = buf[start:end]
        if all(b == 0 for b in region):
            lines.append("  [All zeros]")
        elif all(b == 0xFF for b in region):
            lines.append("  [All 0xFF]")
        else:
            # Count non-zero bytes
            non_zero = sum(1 for b in region if b != 0)
            lines.append(f"  Non-zero bytes: {non_zero}/{size} ({100*non_zero/size:.1f}%)")
            if dump_hex:
                lines.append("")
                lines.append(hex_dump(buf, start, end))

    return '\n'.join(lines)


def compare_files(file1: Path, file2: Path) -> None:
    """Compare two .bes files and show differences."""
    buf1 = bytearray(file1.read_bytes())
    buf2 = bytearray(file2.read_bytes())

    print(f"\n{'='*70}")
    print(f"  FILE COMPARISON")
    print(f"{'='*70}")
    print(f"\n  File 1: {file1.name} ({len(buf1):,} bytes)")
    print(f"  File 2: {file2.name} ({len(buf2):,} bytes)")

    if len(buf1) != len(buf2):
        print(f"\n  WARNING: Files are different sizes!")
        min_len = min(len(buf1), len(buf2))
    else:
        min_len = len(buf1)
        print(f"\n  Files are same size: {min_len:,} bytes")

    # Find all differences
    diffs = []
    for i in range(min_len):
        if buf1[i] != buf2[i]:
            diffs.append(i)

    print(f"  Total differing bytes: {len(diffs)}")

    if not diffs:
        print("\n  Files are identical!")
        return

    # Group consecutive differences into ranges
    ranges = []
    if diffs:
        start = diffs[0]
        end = diffs[0]
        for offset in diffs[1:]:
            if offset == end + 1:
                end = offset
            else:
                ranges.append((start, end + 1))
                start = offset
                end = offset
        ranges.append((start, end + 1))

    print(f"  Difference ranges: {len(ranges)}")

    def _calc_tail_start(buf_len: int) -> Optional[int]:
        # Total save size is 0x2514 + 0x20*N where:
        # - options entries start at 0x24BE
        # - tail is fixed 0x56 bytes at the end
        base_size = 0x2514
        if buf_len < base_size:
            return None
        extra = buf_len - base_size
        if extra % 0x20 != 0:
            return None
        n = extra // 0x20
        return 0x24BE + 0x20 * n

    tail_start_1 = _calc_tail_start(len(buf1))
    tail_start_2 = _calc_tail_start(len(buf2))
    tail_start = tail_start_1 if tail_start_1 == tail_start_2 else tail_start_1

    # Map offsets to known regions (true dword view)
    def get_region_name(offset: int) -> str:
        if offset < CAREER_BASE:
            return "VersionWord"
        if offset < NODE_BASE:
            return "CCareerHeader"
        if offset < LINK_BASE:
            node = (offset - NODE_BASE) // NODE_SIZE
            field_off = (offset - NODE_BASE) % NODE_SIZE
            return f"Node[{node}]+0x{field_off:02X}"
        if offset < GOODIE_BASE:
            link = (offset - LINK_BASE) // LINK_SIZE
            return f"Link[{link}]"
        if offset < KILLS_BASE:
            goodie = (offset - GOODIE_BASE) // 4
            return f"Goodie[{goodie}]"
        if offset < TECH_SLOTS_BASE:
            kill = (offset - KILLS_BASE) // 4
            cats = ["Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs"]
            return f"Kills[{cats[kill] if kill < 5 else kill}]"
        if offset < CAREER_BASE + CCAREER_CAREER_IN_PROGRESS:
            slot = (offset - TECH_SLOTS_BASE) // 4
            return f"TechSlot[{slot}]"
        # CCareer fixed-block settings near the end
        if offset < CAREER_BASE + 0x2498:
            return "ProgressSettings"
        if offset < 0x24BE:
            return "CareerSettings2"
        else:
            if tail_start is not None and offset >= tail_start:
                if offset < tail_start + 0x56:
                    return "OptionsTail"
                return "AfterTail"
            return "OptionsEntries"

    print(f"\n{'-'*70}")
    print("DIFFERENCES BY REGION:")
    print(f"{'-'*70}")

    # Count diffs per region
    region_counts = {}
    for offset in diffs:
        region = get_region_name(offset)
        # Simplify names for counting
        if region.startswith("Node["):
            region = "Nodes"
        elif region.startswith("Link["):
            region = "Links"
        elif region.startswith("Goodie["):
            region = "Goodies"
        elif region.startswith("Kills["):
            region = "Kills"
        elif region.startswith("TechSlot["):
            region = "TechSlots"
        region_counts[region] = region_counts.get(region, 0) + 1

    for region, count in sorted(region_counts.items(), key=lambda x: -x[1]):
        print(f"  {region:20s}: {count:5} bytes differ")

    # Show detailed diff for mystery regions
    print(f"\n{'-'*70}")
    print("MYSTERY REGION DETAILS:")
    print(f"{'-'*70}")

    for name, start, end, desc in MYSTERY_REGIONS:
        region_diffs = [d for d in diffs if start <= d < end]
        if region_diffs:
            print(f"\n  {name} ({desc}): {len(region_diffs)} bytes differ")
            print()
            # Show side-by-side hex for first 64 bytes of differences
            show_start = region_diffs[0]
            show_end = min(show_start + 64, end)
            print(f"  Offset    File1                               File2")
            print(f"  ------    -----                               -----")
            for off in range(show_start, show_end, 8):
                chunk1 = buf1[off:min(off+8, show_end)]
                chunk2 = buf2[off:min(off+8, show_end)]
                hex1 = ' '.join(f'{b:02X}' for b in chunk1)
                hex2 = ' '.join(f'{b:02X}' for b in chunk2)
                marker = " *" if chunk1 != chunk2 else ""
                print(f"  0x{off:04X}:   {hex1:<24}      {hex2:<24}{marker}")
        else:
            print(f"\n  {name}: No differences")

    print(f"\n{'='*70}")


def analyze_file(input_path: Path, verbose: bool = False, dump_mystery: bool = False) -> bool:
    """
    Analyze a BEA save/options file and display its current state.

    Args:
        input_path: Path to input .bes/.bea file
        verbose: Show completed-node details and reserved/unmapped hex dumps
        dump_mystery: Show reserved/unmapped hex dumps without verbose node details
    """
    buf = bytearray(input_path.read_bytes())
    is_options_file = is_options_like_path(input_path)

    header_line = "=" * 60
    section_line = "-" * 40

    print(header_line)
    print("  SAVE FILE ANALYSIS")
    print(f"  File: {input_path.name}")
    print(header_line)
    print()

    # File validation
    print("FILE VALIDATION")
    print(section_line)
    print(f"  File size: {len(buf):,} bytes", end="")
    if len(buf) == EXPECTED_FILE_SIZE:
        print(" [OK]")
    else:
        print(f" [FAIL] (expected {EXPECTED_FILE_SIZE:,})")
        print(f"  ERROR: Invalid file size (expected {EXPECTED_FILE_SIZE:,})")
        return False

    # Version word (BEA.exe checks only the low 16 bits)
    version_word = read_u16(buf, 0x0000)
    version_dword = read_u32(buf, 0x0000)
    print(f"  Version word: 0x{version_word:04X}", end="")
    if version_word == VERSION_WORD:
        print(" [OK]")
    else:
        print(f" [FAIL] (expected 0x{VERSION_WORD:04X})")
    print(f"  Header dword view @0x0000: 0x{version_dword:08X} (version word + first 2 bytes of CCareer)")

    # CCareer header dword0 (increments when unlocking goodies via cutscenes; typically 0 in many saves)
    new_goodie_count = read_u32(buf, CAREER_BASE + CCAREER_NEW_GOODIE_COUNT)
    print(f"  NewGoodieCount: {new_goodie_count} (raw=0x{new_goodie_count:08X})")

    # God mode toggle state (persisted menu toggle; runtime behavior is cheat-gated)
    god_mode_enabled_raw = read_u32(buf, GOD_MODE_ENABLED_OFFSET)
    god_mode_enabled = god_mode_enabled_raw != 0
    print(f"  GodModeEnabled: 0x{god_mode_enabled_raw:08X} ({'ON' if god_mode_enabled else 'OFF'})")

    # CCareer settings at the end of the fixed 0x24BC-byte block (true dword view).
    career_in_progress_raw = read_u32(buf, CAREER_BASE + CCAREER_CAREER_IN_PROGRESS)
    sound_bits = read_u32(buf, CAREER_BASE + CCAREER_SOUND_VOLUME)
    music_bits = read_u32(buf, CAREER_BASE + CCAREER_MUSIC_VOLUME)
    sound_vol = read_f32(buf, CAREER_BASE + CCAREER_SOUND_VOLUME)
    music_vol = read_f32(buf, CAREER_BASE + CCAREER_MUSIC_VOLUME)

    invert_y_p1 = read_u32(buf, INVERT_Y_P1_OFFSET)
    invert_y_p2 = read_u32(buf, INVERT_Y_P2_OFFSET)
    invert_flight_p1 = read_u32(buf, INVERT_FLIGHT_P1_OFFSET)
    invert_flight_p2 = read_u32(buf, INVERT_FLIGHT_P2_OFFSET)
    vib_p1 = read_u32(buf, VIBRATION_P1_OFFSET)
    vib_p2 = read_u32(buf, VIBRATION_P2_OFFSET)
    cfg_p1 = read_u32(buf, CONTROLLER_CONFIG_P1_OFFSET)
    cfg_p2 = read_u32(buf, CONTROLLER_CONFIG_P2_OFFSET)

    print(f"  CareerInProgress: 0x{career_in_progress_raw:08X} ({'YES' if career_in_progress_raw != 0 else 'NO'})")
    print(f"  SoundVolume: {sound_vol:.3f} (bits=0x{sound_bits:08X})")
    print(f"  MusicVolume: {music_vol:.3f} (bits=0x{music_bits:08X})")
    if is_options_file:
        print("  NOTE: This is a .bea options file (loaded at boot). These volumes should apply globally after restart.")
    else:
        print("  NOTE (Steam build): When loading a .bes save, the game preserves current Sound/Music volumes (from defaultoptions.bea). These values may not apply on load.")
    def _fmt_bool(v: int) -> str:
        return "ON" if v != 0 else "OFF"

    print(f"  InvertY (Walker): P1={_fmt_bool(invert_y_p1)} (raw=0x{invert_y_p1:08X}) P2={_fmt_bool(invert_y_p2)} (raw=0x{invert_y_p2:08X})")
    print(f"  InvertY (Flight): P1={_fmt_bool(invert_flight_p1)} (raw=0x{invert_flight_p1:08X}) P2={_fmt_bool(invert_flight_p2)} (raw=0x{invert_flight_p2:08X})")
    print(f"  Vibration:        P1={_fmt_bool(vib_p1)} (raw=0x{vib_p1:08X}) P2={_fmt_bool(vib_p2)} (raw=0x{vib_p2:08X})")
    print(f"  CtrlConfig:  P1={cfg_p1} P2={cfg_p2}")

    print()

    # Options entries + fixed tail snapshot (OptionsTail)
    # Total size formula from BEA.exe: 0x2514 + 0x20*N, with a fixed 0x56-byte tail at end.
    base_size = 0x2514
    entry_size = 0x20
    tail_size = 0x56
    options_start = 0x24BE
    if len(buf) >= base_size and (len(buf) - base_size) % entry_size == 0:
        n = (len(buf) - base_size) // entry_size
        tail_start = options_start + entry_size * n
        # Sanity: tail is always last 0x56 bytes in retail saves.
        tail_start_expected = len(buf) - tail_size
        if tail_start == tail_start_expected:
            print("OPTIONS (bindings + tail snapshot)")
            print(section_line)
            if is_options_file:
                print("  NOTE: The game loads these entries/tail at boot by loading defaultoptions.bea via CCareer::Load(flag=0).")
            else:
                print("  NOTE (Steam build): CCareer::Load(flag=1) does NOT apply these entries/tail when loading a .bes save.")
                print("        Runtime uses defaultoptions.bea for keybinds and most global options (mouse sensitivity, screen shape, etc).")
                print("        Frontend load/save flows may rewrite defaultoptions.bea from loaded/current buffers for the next boot")
                print("        (load path is conditional on DAT_0082b5b0 == 0), so a patched .bes can affect global options after restart.")
            print(f"  Options entries: {n} (0x20*N = 0x{entry_size*n:X} bytes)")
            print(f"  Tail start: 0x{tail_start:04X} (size=0x{tail_size:X})")

            ms_bits = read_u32(buf, tail_start + 0x04)
            ms = read_f32(buf, tail_start + 0x04)
            scheme_index = read_u16(buf, tail_start + 0x08)
            lang_index = read_u16(buf, tail_start + 0x0A)
            screen_shape = read_u32(buf, tail_start + 0x20)
            d3d_device = read_u32(buf, tail_start + 0x28)

            print(f"  MouseSensitivity: {ms:.3f} (bits=0x{ms_bits:08X})")
            print(f"  ControlSchemeIndex: {scheme_index}")
            print(f"  LanguageIndex: {lang_index}")
            print(f"  ScreenShape: 0x{screen_shape:08X} ({screen_shape}) (0=4:3, 1=16:9, 2=1:1)")
            print(f"  D3DDeviceIndex: 0x{d3d_device:08X} ({d3d_device})")

            if verbose:
                # Options entries: persisted control bindings (two slots per entry_id).
                # See: reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md
                scan_names = {
                    0x000F: "Tab",
                    0x002A: "LShift",
                    0x0036: "RShift",
                    0x0039: "Space",
                    0x003A: "CapsLock",
                    0x009D: "RControl",
                    0x00C8: "Up",
                    0x00CB: "Left",
                    0x00CD: "Right",
                    0x00D0: "Down",
                }
                entry_names = {
                    0x1F: "Movement: Forward",
                    0x20: "Movement: Backward",
                    0x1D: "Movement: Left",
                    0x1E: "Movement: Right",
                    0x1A: "Look: Up",
                    0x1C: "Look: Down",
                    0x19: "Look: Left",
                    0x1B: "Look: Right",
                    0x10: "Zoom: In",
                    0x11: "Zoom: Out",
                    0x12: "Others: Fire weapon (A)",
                    0x13: "Others: Fire weapon (B)",
                    0x14: "Others: Select weapon",
                    0x21: "Others: Transform",
                    0x15: "Others: Air brake",
                    0x3B: "Others: Special function",
                }

                def fmt_binding(dev_code: int, packed_key: int) -> str:
                    vk = (packed_key >> 16) & 0xFFFF
                    scan = packed_key & 0xFFFF
                    # Mouse look axes (Steam preset uses these for Look Up/Down/Left/Right).
                    # NOTE: scan=0 => packed_key==0, so dev_code must be checked before treating packed_key==0 as "unbound".
                    if dev_code in (11, 12):
                        axis = "MouseX" if scan == 0 else ("MouseY" if scan == 1 else "MouseAxis")
                        if axis == "MouseAxis":
                            return f"Mouse({scan})"
                        return f"{axis}{'+' if dev_code == 11 else '-'}"
                    # Mouse wheel appears as device_code=16 with small scan values.
                    if dev_code == 16:
                        if scan == 4:
                            return "MouseWheelDown"
                        if scan == 3:
                            return "MouseWheelUp"
                        if scan == 2:
                            return "MouseRight"
                        return f"Mouse({scan})"
                    # Mouse buttons observed in Steam build:
                    # - dev 17 + packed_key 0 => left mouse button
                    # - dev 15 + packed_key 0 => left mouse button (paired entry)
                    if dev_code in (15, 17) and vk == 0 and scan == 0:
                        return "MouseLeft"
                    if packed_key == 0:
                        return "-"
                    # Numpad digits: preserve DIK scan-based distinction (Num7 != '7')
                    numpad_scan_to_digit = {
                        0x0047: "7", 0x0048: "8", 0x0049: "9",
                        0x004B: "4", 0x004C: "5", 0x004D: "6",
                        0x004F: "1", 0x0050: "2", 0x0051: "3",
                        0x0052: "0",
                    }
                    if scan in numpad_scan_to_digit and 0x30 <= vk <= 0x39:
                        return f"Num{numpad_scan_to_digit[scan]}"
                    if vk == 0 and scan in numpad_scan_to_digit:
                        return f"Num{numpad_scan_to_digit[scan]}"
                    if vk != 0 and 0x20 <= vk <= 0x7E:
                        if scan == 0x000D:
                            return "="
                        if scan == 0x000C:
                            return "-"
                        if scan == 0x0027:
                            return ";"
                        return chr(vk)
                    if scan in scan_names:
                        return scan_names[scan]
                    return f"vk=0x{vk:04X} scan=0x{scan:04X}"

                print("  Bindings (options entries, verbose):")
                if scheme_index == 1:
                    print("  NOTE: ControlSchemeIndex=1 preset detected; retail mapping reads slot0/slot1 as P1/P2.")
                for i in range(n):
                    eoff = options_start + entry_size * i
                    active = read_u32(buf, eoff + 0x00) & 0xFF
                    entry_id = struct.unpack_from("<i", buf, eoff + 0x04)[0] & 0xFFFFFFFF
                    if active == 0:
                        continue
                    s0_dev = read_u32(buf, eoff + 0x0C)
                    s0_key = read_u32(buf, eoff + 0x10)
                    s1_dev = read_u32(buf, eoff + 0x18)
                    s1_key = read_u32(buf, eoff + 0x1C)
                    name = entry_names.get(entry_id, f"entry_id=0x{entry_id:02X}")
                    if scheme_index in (0, 1):
                        p1_dev, p1_key = s0_dev, s0_key
                        p2_dev, p2_key = s1_dev, s1_key
                        print(f"    {name:18s} P1={fmt_binding(p1_dev, p1_key):12s} P2={fmt_binding(p2_dev, p2_key)}")
                    else:
                        print(f"    {name:18s} slot0={fmt_binding(s0_dev, s0_key):12s} slot1={fmt_binding(s1_dev, s1_key)}")

                # Tail snapshot (selected fields) - useful for correlating in-game Video/Sound Options.
                def u32(off: int) -> int:
                    return read_u32(buf, tail_start + off)

                def i32(off: int) -> int:
                    return struct.unpack_from("<i", buf, tail_start + off)[0]

                ld2 = buf[tail_start + 0x54]
                ld1 = buf[tail_start + 0x55]
                effective_ld = 2 if ld2 != 0 else ld1
                print("  Tail snapshot (selected, verbose):")
                print(f"    g_LandscapeLowresGeom:   0x{u32(0x1C):08X}")
                print(f"    g_DisallowMipMapping:    0x{u32(0x24):08X}")
                print(f"    g_TryLockableBackbuffer: 0x{u32(0x2C):08X}")
                print(f"    g_LandscapeMaxLevelsUser:0x{u32(0x30):08X}")
                print(f"    g_UserTextureResLossShift:0x{u32(0x34):08X}")
                print(f"    g_UserTextureAllow32Bit: 0x{u32(0x38):08X}")
                print(f"    g_ProfileMultisampleType:{i32(0x3C)}")
                print(f"    g_SoundEnabledFlag:      0x{u32(0x44):08X}")
                print(f"    g_SoundSampleRateIndex:  0x{u32(0x48):08X}")
                print(f"    g_SoundDeviceIndex:      0x{u32(0x4C):08X}")
                print(f"    g_Sound3DMethod:         0x{u32(0x50):08X}")
                print(f"    g_LandscapeDetailLevel1/2: 0x{ld1:02X} / 0x{ld2:02X} (effective={effective_ld})")

            print()

    # Node analysis
    print("MISSION NODES (100 slots)")
    print(section_line)

    completed_nodes: list[tuple[int, int, str, int]] = []  # (nodeIndex, world, rankStr, rankBits)
    incomplete_nodes: list[tuple[int, int, int, int]] = []  # (nodeIndex, world, complete, rankBits)

    for n in range(NODE_COUNT):
        offset = NODE_BASE + n * NODE_SIZE
        world = read_u32(buf, offset + 0x10)
        if world == 0:
            # Unused slot (common in retail saves).
            continue

        complete = read_u32(buf, offset + 0x04)
        rank_bits = read_u32(buf, offset + 0x3C)

        is_complete = complete != 0
        if is_complete:
            rank = decode_rank(rank_bits)
            completed_nodes.append((n, world, rank, rank_bits))
        else:
            incomplete_nodes.append((n, world, complete, rank_bits))

    used_nodes = len(completed_nodes) + len(incomplete_nodes)
    print(f"  Used:      {used_nodes} nodes (world != 0)")
    print(f"  Completed: {len(completed_nodes)} nodes")
    print(f"  Incomplete:{len(incomplete_nodes)} nodes")
    print(f"  Unused:    {NODE_COUNT - used_nodes} nodes (world == 0)")

    if verbose and completed_nodes:
        print("\n  Completed Nodes:")
        for n, world, rank, rank_bits in completed_nodes:
            f = struct.unpack('<f', struct.pack('<I', rank_bits))[0]
            print(f"    Node {n:2d} (world={world:3d}): {rank:6s} (rankBits=0x{rank_bits:08X}, f={f:.2f})")
    elif completed_nodes:
        # Show rank distribution
        rank_counts = {}
        for _n, _world, rank, _bits in completed_nodes:
            base_rank = rank.split()[0].replace('~', '')  # Get base rank letter
            rank_counts[base_rank] = rank_counts.get(base_rank, 0) + 1
        print("  Rank distribution:", end="")
        for rank in ['S', 'A', 'B', 'C', 'D', 'E', 'NONE']:
            if rank in rank_counts:
                print(f"  {rank}:{rank_counts[rank]}", end="")
        print()

    print()

    # Link analysis
    print("LINKS (200 slots)")
    print(section_line)

    used_links = 0
    completed_links = 0
    for link in range(LINK_COUNT):
        offset = LINK_BASE + link * LINK_SIZE
        link_state = read_u32(buf, offset)
        to_node = read_u32(buf, offset + 4)
        if to_node == 0xFFFFFFFF:
            continue
        used_links += 1
        if link_state != 0:
            completed_links += 1

    print(f"  Used:      {used_links}/{LINK_COUNT}")
    print(f"  Completed: {completed_links}/{used_links if used_links else 0} (state != 0)")

    print()

    # Goodie analysis
    displayable_goodies = GOODIE_DISPLAYABLE_COUNT
    print(f"GOODIES ({displayable_goodies} displayable, {GOODIE_COUNT - displayable_goodies} reserved)")
    print(section_line)

    goodie_states = {'LOCKED': 0, 'INSTRUCTIONS': 0, 'NEW': 0, 'OLD': 0, 'OTHER': 0, 'RESERVED': 0}
    for g in range(GOODIE_COUNT):
        if g >= GOODIE_DISPLAYABLE_COUNT:
            goodie_states['RESERVED'] += 1
            continue
        offset = GOODIE_BASE + g * 4
        val = read_u32(buf, offset)
        if val == GOODIE_UNKNOWN:
            goodie_states['LOCKED'] += 1
        elif val == GOODIE_INSTRUCTIONS:
            goodie_states['INSTRUCTIONS'] += 1
        elif val == GOODIE_NEW:
            goodie_states['NEW'] += 1
        elif val == GOODIE_OLD:
            goodie_states['OLD'] += 1
        else:
            goodie_states['OTHER'] += 1

    unlocked = goodie_states['NEW'] + goodie_states['OLD']
    print(f"  Unlocked:  {unlocked}/{displayable_goodies}")
    print(f"    - NEW (gold): {goodie_states['NEW']}")
    print(f"    - OLD (blue): {goodie_states['OLD']}")
    if goodie_states['INSTRUCTIONS'] > 0:
        print(f"    - Instructions: {goodie_states['INSTRUCTIONS']}")
    if goodie_states['OTHER'] > 0:
        print(f"    - Other:      {goodie_states['OTHER']}")
    print(f"  Locked:    {goodie_states['LOCKED']}")
    if goodie_states['RESERVED'] > 0:
        print(f"  Reserved:  {goodie_states['RESERVED']}")

    print()

    # Kill counts
    print("KILL COUNTS")
    print(section_line)

    categories = ['Aircraft', 'Vehicles', 'Emplacements', 'Infantry', 'Mechs']
    for k in range(KILLS_COUNT):
        offset = KILLS_BASE + k * 4
        raw = read_u32(buf, offset)
        meta = (raw >> 24) & 0xFF
        kills = raw & 0x00FFFFFF
        next_unlock = get_next_unlock_threshold(k, kills)

        progress = ""
        if next_unlock:
            progress = f" (next unlock at {next_unlock})"
        else:
            progress = " (all unlocked)"

        meta_str = f" meta=0x{meta:02X}" if meta != 0 else ""
        print(f"  {categories[k]:13s}: {kills:6d}{meta_str}{progress}")

    print()

    # Tech slots summary
    print("TECH SLOTS (32 slots)")
    print(section_line)

    active_slots = 0
    for slot in range(TECH_SLOTS_COUNT):
        offset = TECH_SLOTS_BASE + slot * 4
        val = read_u32(buf, offset)
        if val != 0:
            active_slots += 1

    print(f"  Active: {active_slots}/{TECH_SLOTS_COUNT}")

    if verbose:
        print("\n  Slot values (bit masks, NOT shift-16):")
        for slot in range(TECH_SLOTS_COUNT):
            offset = TECH_SLOTS_BASE + slot * 4
            val = read_u32(buf, offset)
            if val != 0:
                # Find which bits are set
                set_bits = [i for i in range(32) if val & (1 << i)]
                # Calculate actual slot numbers (slot_index * 32 + bit)
                slot_nums = [slot * 32 + b for b in set_bits]
                bits_str = ','.join(str(b) for b in set_bits[:8])  # Show first 8
                if len(set_bits) > 8:
                    bits_str += f"...+{len(set_bits)-8} more"
                slots_str = ','.join(str(s) for s in slot_nums[:4])
                if len(slot_nums) > 4:
                    slots_str += f"...+{len(slot_nums)-4}"
                print(f"    mSlots[{slot:2d}]: 0x{val:08X} bits=[{bits_str}] -> slots [{slots_str}]")

    # Reserved/unmapped regions summary (always show; hex dump if verbose or --dump-mystery)
    print(analyze_mystery_regions(buf, dump_hex=(verbose or dump_mystery)))

    print()
    print(header_line)
    hints = []
    if not verbose:
        hints.append("--verbose for node details")
    if not dump_mystery and not verbose:
        hints.append("--dump-mystery for raw reserved/unmapped byte dumps")
    if hints:
        print(f"  Analysis complete. Use {', '.join(hints)}.")
    else:
        print("  Analysis complete.")
    print(header_line)
    print()
    return True


def list_goodies(input_path: Path, show_reserved: bool = False) -> bool:
    """
    List per-slot goodie state from a .bes/.bea file.
    Returns True when the file validates and output is emitted.
    """
    buf = bytearray(input_path.read_bytes())

    if len(buf) != EXPECTED_FILE_SIZE:
        print(
            f"ERROR: Invalid file size {len(buf):,} bytes "
            f"(expected {EXPECTED_FILE_SIZE:,}).",
            file=sys.stderr,
        )
        return False

    version_word = read_u16(buf, 0x0000)
    if version_word != VERSION_WORD:
        print(
            f"ERROR: Invalid version word 0x{version_word:04X} "
            f"(expected 0x{VERSION_WORD:04X}).",
            file=sys.stderr,
        )
        return False

    print("Onslaught Career Editor - Goodie List")
    print("=====================================")
    print(f"File: {input_path}")
    print(f"Version: 0x{version_word:04X}")
    print(f"Display mode: {'all 300 slots' if show_reserved else 'displayable slots (0-232)'}")
    print()
    print(f"{'Idx':>4} {'Offset':>8} {'State':<13} {'Raw':<10} {'Scope':<11}")
    print("-" * 52)

    counts = {
        "NEW": 0,
        "OLD": 0,
        "LOCKED": 0,
        "INSTRUCTIONS": 0,
        "OTHER": 0,
        "RESERVED": 0,
    }

    for idx in range(GOODIE_COUNT):
        offset = GOODIE_BASE + idx * 4
        raw = read_u32(buf, offset)
        state = classify_goodie_state(idx, raw)
        scope = "Reserved" if idx >= GOODIE_DISPLAYABLE_COUNT else "Displayable"
        counts[state] += 1

        if not show_reserved and idx >= GOODIE_DISPLAYABLE_COUNT:
            continue

        print(f"{idx:>4} 0x{offset:04X} {state:<13} 0x{raw:08X} {scope:<11}")

    unlocked = counts["NEW"] + counts["OLD"]
    print()
    print("Summary (displayable slots 0-232):")
    print(f"  Unlocked: {unlocked}/{GOODIE_DISPLAYABLE_COUNT} (NEW {counts['NEW']}, OLD {counts['OLD']})")
    print(f"  Locked: {counts['LOCKED']}")
    print(f"  Instructions: {counts['INSTRUCTIONS']}")
    if counts["OTHER"] > 0:
        print(f"  Other: {counts['OTHER']}")
    print(f"  Reserved slots: {counts['RESERVED']}")

    if not show_reserved:
        print("  Note: Reserved rows hidden; use --show-reserved-goodies to include them.")

    return True


def get_cli_version() -> str:
    """Return Python CLI version string with optional git SHA suffix."""
    base = APP_VERSION
    repo_root = Path(__file__).resolve().parent
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
        sha = proc.stdout.strip()
        if len(sha) == 40 and all(c in "0123456789abcdef" for c in sha.lower()):
            return f"{base}+{sha}"
    except Exception:
        pass
    return base


def main():
    parser = argparse.ArgumentParser(
        description='Onslaught Career Editor - Battle Engine Aquila save patcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    %(prog)s --analyze career.bes
    %(prog)s --analyze career.bes --verbose --dump-mystery
    %(prog)s --list-goodies career.bes
    %(prog)s --list-goodies career.bes --show-reserved-goodies
    %(prog)s --compare gold.bes patched.bes
    %(prog)s career.bes career_patched.bes
    %(prog)s career.bes patched.bes --new --kills 500
    %(prog)s career.bes patched.bes --rank A --level-rank 1:S --level-rank 2:S
    %(prog)s career.bes patched.bes --kills-only --kills 400
    %(prog)s career.bes patched.bes --no-goodies --no-kills

Game Directory Management:
    %(prog)s --list-saves              List detected save files
    %(prog)s --set-game-dir "C:\\..."  Set game installation directory
    %(prog)s --show-config             Show current configuration

Kill Category Thresholds (for goodie unlocks):
    Aircraft:     25, 50, 75, 100
    Vehicles:     100, 200, 300, 400
    Emplacements: 25, 50 (75 appears only in combined unlocks)
    Infantry:     40, 80, 160
    Mechs:        20, 40, 80
        '''
    )
    # Analyze mode
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze save file without modifying (only requires input file)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show completed-node details + reserved/unmapped hex dumps (use with --analyze)')
    parser.add_argument('--dump-mystery', action='store_true',
                        help='Show reserved/unmapped hex dumps without verbose node details (use with --analyze)')
    parser.add_argument('--compare', type=Path, metavar='FILE2',
                        help='Compare input file with another .bes/.bea file')
    parser.add_argument('--list-goodies', action='store_true',
                        help='List per-slot goodie states (read-only; requires input file)')
    parser.add_argument('--show-reserved-goodies', action='store_true',
                        help='With --list-goodies: include reserved slots (233-299)')

    # Game directory management (no input file required)
    parser.add_argument('--list-saves', action='store_true',
                        help='List detected save files from game directory')
    parser.add_argument('--set-game-dir', type=Path, metavar='PATH',
                        help='Set the Battle Engine Aquila installation directory')
    parser.add_argument('--show-config', action='store_true',
                        help='Show current configuration')
    parser.add_argument('--version', action='store_true',
                        help='Print CLI version and exit')

    parser.add_argument('input', type=Path, nargs='?', help='Input .bes/.bea file')
    parser.add_argument('output', type=Path, nargs='?', help='Output .bes/.bea file (not needed for read-only modes)')
    parser.add_argument('--new', action='store_true',
                        help='Mark goodies as NEW (gold) instead of OLD (blue)')

    # Selective patching flags
    parser.add_argument('--kills-only', action='store_true',
                        help='Only patch kill counts (preserve nodes, links, goodies)')
    parser.add_argument('--no-nodes', action='store_true',
                        help='Skip patching mission nodes')
    parser.add_argument('--no-links', action='store_true',
                        help='Skip patching mission links')
    parser.add_argument('--no-goodies', action='store_true',
                        help='Skip patching goodies')
    parser.add_argument('--no-kills', action='store_true',
                        help='Skip patching kill counts')
    parser.add_argument('--allow-career-sections-on-options-file', action='store_true',
                        help='Allow missions/links/goodies/kills patching when input/output is .bea/defaultoptions (advanced; off by default).')
    parser.add_argument('--kills', type=int, default=100,
                        help='Kill count for all categories (default: 100)')
    parser.add_argument('--rank', type=str, default='S',
                        help='Rank for all missions (default: S). NONE = unlocked without grade letter.')

    # Per-level rank overrides
    parser.add_argument('--level-rank', type=str, action='extend', nargs='+', dest='level_ranks',
                        metavar='N:GRADE',
                        help='Set specific node index rank (1-43). Example: --level-rank 1:A. Can be repeated.')

    # Per-category kill overrides
    parser.add_argument('--aircraft-kills', type=int, metavar='N',
                        help='Aircraft kill count (unlocks at 25/50/75/100)')
    parser.add_argument('--vehicle-kills', type=int, metavar='N',
                        help='Vehicle kill count (unlocks at 100/200/300/400)')
    parser.add_argument('--emplacement-kills', type=int, metavar='N',
                        help='Emplacement kill count (unlocks at 25/50; 75 appears only in combined unlocks)')
    parser.add_argument('--infantry-kills', type=int, metavar='N',
                        help='Infantry kill count (unlocks at 40/80/160)')
    parser.add_argument('--mech-kills', type=int, metavar='N',
                        help='Mech kill count (unlocks at 20/40/80; 40 unlocks two goodies)')

    # Optional CCareer settings overrides (true dword view; omit to preserve existing save values)
    parser.add_argument('--sound-volume', type=float, metavar='V',
                        help='Override sound volume (0.0-1.0). Omit to preserve.')
    parser.add_argument('--music-volume', type=float, metavar='V',
                        help='Override music volume (0.0-1.0). Omit to preserve.')
    parser.add_argument('--invert-walker-p1', '--invert-y-p1', dest='invert_walker_p1', type=str, metavar='on|off',
                        help='Override invert-Y (Walker mode) for player 1: on/off/true/false/1/0 (omit to preserve).')
    parser.add_argument('--invert-walker-p2', '--invert-y-p2', dest='invert_walker_p2', type=str, metavar='on|off',
                        help='Override invert-Y (Walker mode) for player 2: on/off/true/false/1/0 (omit to preserve).')
    parser.add_argument('--invert-flight-p1', type=str, metavar='on|off',
                        help='Override invert-Y (Flight/Jet mode) for player 1: on/off/true/false/1/0 (omit to preserve).')
    parser.add_argument('--invert-flight-p2', type=str, metavar='on|off',
                        help='Override invert-Y (Flight/Jet mode) for player 2: on/off/true/false/1/0 (omit to preserve).')
    parser.add_argument('--vibration-p1', type=str, metavar='on|off',
                        help='Override controller vibration for player 1: on/off/true/false/1/0 (omit to preserve).')
    parser.add_argument('--vibration-p2', type=str, metavar='on|off',
                        help='Override controller vibration for player 2: on/off/true/false/1/0 (omit to preserve).')
    parser.add_argument('--controller-config-p1', type=int, metavar='N',
                        help='Override controller config index for player 1 (uint32; omit to preserve).')
    parser.add_argument('--controller-config-p2', type=int, metavar='N',
                        help='Override controller config index for player 2 (uint32; omit to preserve).')
    parser.add_argument('--experimental-pending-extra-goodies', type=int, metavar='N',
                        help='Experimental only: pending-extra-goodies override (currently ignored for retail Steam).')

    # Options entries + tail snapshot copy (raw byte copy for keybinds + global options snapshot)
    parser.add_argument('--copy-options-from', type=Path, metavar='FILE',
                        help='Copy the options entries + tail snapshot from another .bes/.bea file (same size/layout).')
    parser.add_argument('--no-copy-options-entries', action='store_true',
                        help='With --copy-options-from: do not copy the options entries region (`0x20*N`, typically `0x200`).')
    parser.add_argument('--no-copy-options-tail', action='store_true',
                        help='With --copy-options-from: do not copy the fixed 0x56-byte options tail snapshot (globals).')

    # Keybind overrides (options entries). Each takes two values: P1 P2.
    # Use "keep" to preserve that side. Examples: A, Num7, Up, Mouse, MouseX+, MouseY-, MouseWheelUp, MouseLeft, MouseRight.
    parser.add_argument('--bind-move-forward', nargs=2, metavar=('P1', 'P2'),
                        help='Override Movement: Forward bindings (P1 P2).')
    parser.add_argument('--bind-move-backward', nargs=2, metavar=('P1', 'P2'),
                        help='Override Movement: Backward bindings (P1 P2).')
    parser.add_argument('--bind-move-left', nargs=2, metavar=('P1', 'P2'),
                        help='Override Movement: Left bindings (P1 P2).')
    parser.add_argument('--bind-move-right', nargs=2, metavar=('P1', 'P2'),
                        help='Override Movement: Right bindings (P1 P2).')

    parser.add_argument('--bind-look-up', nargs=2, metavar=('P1', 'P2'),
                        help='Override Look: Up bindings (P1 P2). Use "Mouse" to bind to mouse axis.')
    parser.add_argument('--bind-look-down', nargs=2, metavar=('P1', 'P2'),
                        help='Override Look: Down bindings (P1 P2). Use "Mouse" to bind to mouse axis.')
    parser.add_argument('--bind-look-left', nargs=2, metavar=('P1', 'P2'),
                        help='Override Look: Left bindings (P1 P2). Use "Mouse" to bind to mouse axis.')
    parser.add_argument('--bind-look-right', nargs=2, metavar=('P1', 'P2'),
                        help='Override Look: Right bindings (P1 P2). Use "Mouse" to bind to mouse axis.')

    parser.add_argument('--bind-zoom-in', nargs=2, metavar=('P1', 'P2'),
                        help='Override Zoom: In bindings (P1 P2). Use MouseWheelUp/MouseWheelDown for wheel.')
    parser.add_argument('--bind-zoom-out', nargs=2, metavar=('P1', 'P2'),
                        help='Override Zoom: Out bindings (P1 P2). Use MouseWheelUp/MouseWheelDown for wheel.')

    parser.add_argument('--bind-fire-weapon', nargs=2, metavar=('P1', 'P2'),
                        help='Override Others: Fire weapon bindings (P1 P2). Use MouseLeft to bind to LMB.')
    parser.add_argument('--bind-select-weapon', nargs=2, metavar=('P1', 'P2'),
                        help='Override Others: Select weapon bindings (P1 P2). Use MouseRight to bind to RMB.')
    parser.add_argument('--bind-transform', nargs=2, metavar=('P1', 'P2'),
                        help='Override Others: Transform bindings (P1 P2).')
    parser.add_argument('--bind-air-brake', nargs=2, metavar=('P1', 'P2'),
                        help='Override Others: Air brake bindings (P1 P2).')
    parser.add_argument('--bind-special', nargs=2, metavar=('P1', 'P2'),
                        help='Override Others: Special function bindings (P1 P2).')

    args = parser.parse_args()

    if args.version:
        print(get_cli_version())
        sys.exit(0)

    # Handle config commands (no input file required)
    if args.list_saves or args.set_game_dir or args.show_config:
        try:
            from onslaught.core.config import (
                AppConfig, detect_game_directory, find_save_files, get_save_info, get_config_path
            )
        except ImportError:
            print("Error: Could not import config module. Run from project root.", file=sys.stderr)
            sys.exit(1)

        config = AppConfig.load()

        # Set game directory
        if args.set_game_dir:
            if args.set_game_dir.exists():
                if not config.set_game_dir(args.set_game_dir):
                    print(f"Error: Failed to persist game directory: {args.set_game_dir}", file=sys.stderr)
                    sys.exit(1)
                print(f"Game directory set to: {args.set_game_dir}")
            else:
                print(f"Error: Directory does not exist: {args.set_game_dir}", file=sys.stderr)
                sys.exit(1)

        # Show configuration
        if args.show_config:
            print("Onslaught Career Editor - Configuration")
            print("=======================================")
            print(f"Config file: {get_config_path()}")
            print()

            game_dir = config.get_game_dir()
            detected = detect_game_directory()

            print(f"Game directory:     {game_dir or '(not set)'}")
            print(f"Auto-detected:      {detected or '(not found)'}")
            print(f"Max recent files:   {config.max_recent_files}")
            print(f"Window size:        {config.window_width}x{config.window_height}")
            print(f"Last tab:           {config.last_tab}")

            if config.recent_files:
                print()
                print(f"Recent files ({len(config.recent_files)}):")
                for f in config.recent_files:
                    exists = Path(f).exists()
                    print(f"  {'[OK]' if exists else '[X]'} {f}")

        # List save files
        if args.list_saves:
            game_dir = config.get_game_dir() or detect_game_directory()

            print("Onslaught Career Editor - Save Files")
            print("====================================")

            if game_dir is None:
                print("Game directory not configured and could not be auto-detected.")
                print("Use --set-game-dir <path> to specify the game installation folder.")
                sys.exit(1)

            print(f"Searching in: {game_dir}")
            print()

            saves = find_save_files(game_dir)

            if not saves:
                print("No .bes/.bea save/options files found.")
                sys.exit(0)

            print(f"Found {len(saves)} save file(s):")
            print()
            print(f"{'Name':<30} {'Size':<12} {'Modified':<20} {'Valid'}")
            print("-" * 70)

            from datetime import datetime
            for save_path in saves:
                info = get_save_info(save_path)
                size_str = "10,004 B" if info['size'] == EXPECTED_FILE_SIZE else f"{info['size']:,} B"
                valid_str = "Yes" if info['valid'] else "No*"
                modified = datetime.fromtimestamp(info['modified'])
                print(f"{info['name']:<30} {size_str:<12} {modified.strftime('%Y-%m-%d %H:%M'):<20} {valid_str}")

            print()
            print("Paths:")
            for save_path in saves:
                print(f"  {save_path}")
            print()
            print(f"* Invalid format: expected {EXPECTED_FILE_SIZE:,} bytes and version word 0x{VERSION_WORD:04X}")

        sys.exit(0)

    # Input file required for remaining commands
    if not args.input:
        print("Error: Input file required. Use -h for help.", file=sys.stderr)
        sys.exit(1)

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.show_reserved_goodies and not args.list_goodies:
        print("Warning: --show-reserved-goodies is only used with --list-goodies.", file=sys.stderr)

    # Handle compare mode
    if args.compare:
        if not args.compare.exists():
            print(f"Error: Comparison file not found: {args.compare}", file=sys.stderr)
            sys.exit(1)
        try:
            compare_files(args.input, args.compare)
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Handle analyze mode
    if args.analyze:
        try:
            ok = analyze_file(args.input, verbose=args.verbose, dump_mystery=args.dump_mystery)
            sys.exit(0 if ok else 1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Handle goodies listing mode
    if args.list_goodies:
        try:
            ok = list_goodies(args.input, show_reserved=args.show_reserved_goodies)
            sys.exit(0 if ok else 1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Patch mode requires output file
    if args.output is None:
        print("Error: Output file required for patch mode (use --analyze for read-only mode)", file=sys.stderr)
        sys.exit(1)

    # Guardrail: block in-place patching before printing patch configuration.
    try:
        if args.input.resolve() == args.output.resolve():
            print("Error: Output file must be different from input file (in-place patching is blocked).", file=sys.stderr)
            sys.exit(1)
    except Exception:
        pass

    # Validate rank (patch mode only)
    valid_ranks = set(RANK_FLOAT_BITS.keys())
    rank = args.rank.upper()
    if rank not in valid_ranks:
        print(f"Error: Invalid rank '{args.rank}'. Valid values: S, A, B, C, D, E, NONE", file=sys.stderr)
        sys.exit(1)

    # Build per-level rank dict from --level-rank arguments (warn and skip invalid entries)
    level_ranks, level_rank_errors = parse_level_rank_entries(args.level_ranks or [], valid_ranks)
    if level_rank_errors:
        for err in level_rank_errors:
            print(err, file=sys.stderr)
        sys.exit(1)

    # Build per-category kills dict from individual arguments
    per_category_kills = {}
    if args.aircraft_kills is not None:
        per_category_kills[KILL_AIRCRAFT] = args.aircraft_kills
    if args.vehicle_kills is not None:
        per_category_kills[KILL_VEHICLES] = args.vehicle_kills
    if args.emplacement_kills is not None:
        per_category_kills[KILL_EMPLACEMENTS] = args.emplacement_kills
    if args.infantry_kills is not None:
        per_category_kills[KILL_INFANTRY] = args.infantry_kills
    if args.mech_kills is not None:
        per_category_kills[KILL_MECHS] = args.mech_kills

    # Determine what to patch based on flags
    # --kills-only is a shortcut for --no-nodes --no-links --no-goodies and forces kills on
    if args.kills_only:
        do_patch_nodes = False
        do_patch_links = False
        do_patch_goodies = False
        do_patch_kills = True
    else:
        do_patch_nodes = not args.no_nodes
        do_patch_links = not args.no_links
        do_patch_goodies = not args.no_goodies
        do_patch_kills = not args.no_kills

    input_options_like = is_options_like_path(args.input)
    output_options_like = is_options_like_path(args.output)
    career_sections_enabled = do_patch_nodes or do_patch_links or do_patch_goodies or do_patch_kills
    if (input_options_like or output_options_like) and career_sections_enabled:
        if not args.allow_career_sections_on_options_file:
            print("Error: Career section patching is blocked for .bea/defaultoptions files by default.", file=sys.stderr)
            print("Use settings-only mode (--no-nodes --no-links --no-goodies --no-kills),", file=sys.stderr)
            print("or pass --allow-career-sections-on-options-file to override intentionally.", file=sys.stderr)
            sys.exit(1)
        print("Warning: Applying career section patching to an options-style file (.bea/defaultoptions).", file=sys.stderr)

    # Parse tri-state overrides (strings -> Optional[bool])
    try:
        invert_y_p1 = parse_tri_bool(args.invert_walker_p1, "--invert-walker-p1")
        invert_y_p2 = parse_tri_bool(args.invert_walker_p2, "--invert-walker-p2")
        invert_flight_p1 = parse_tri_bool(args.invert_flight_p1, "--invert-flight-p1")
        invert_flight_p2 = parse_tri_bool(args.invert_flight_p2, "--invert-flight-p2")
        vibration_p1 = parse_tri_bool(args.vibration_p1, "--vibration-p1")
        vibration_p2 = parse_tri_bool(args.vibration_p2, "--vibration-p2")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Keybind overrides (options entries)
    options_entry_overrides: dict[int, OptionsEntryOverride] = {}

    def _is_keep_token(t: Optional[str]) -> bool:
        return t is None or t.strip() == "" or t.strip().lower() in ("keep", "preserve", "unchanged")

    def _set_slot(entry_id: int, slot_index: int, dev: int, key: int) -> None:
        ov = options_entry_overrides.get(entry_id)
        if ov is None:
            ov = OptionsEntryOverride()
            options_entry_overrides[entry_id] = ov
        slot = ov.slot0 if slot_index == 0 else ov.slot1
        slot.device_code = int(dev)
        slot.packed_key = int(key)

    def _parse_row(
        entry_id: int,
        keyboard_device_code: int,
        allow_look_mouse: bool,
        allow_zoom_wheel: bool,
        allow_mouse_buttons: bool,
        pair: Optional[list[str]],
        label: str,
    ) -> None:
        if pair is None:
            return
        p1, p2 = pair

        if not _is_keep_token(p1):
            t = p1.strip()
            if allow_look_mouse and t.lower().startswith("mouse"):
                dev, key = _parse_look_token(entry_id, t)
            elif allow_zoom_wheel and t.lower() in ("mousewheelup", "mousewheeldown"):
                dev, key = _parse_zoom_mouse_wheel(t)
            elif allow_mouse_buttons and t.lower() in ("mouseleft", "mouseright"):
                dev, key = _parse_mouse_button(entry_id, t)
            else:
                dev, key = keyboard_device_code, parse_keyboard_packed_key(t)
            _set_slot(entry_id, 0, dev, key)

        if not _is_keep_token(p2):
            t = p2.strip()
            if allow_look_mouse and t.lower().startswith("mouse"):
                dev, key = _parse_look_token(entry_id, t)
            elif allow_zoom_wheel and t.lower() in ("mousewheelup", "mousewheeldown"):
                dev, key = _parse_zoom_mouse_wheel(t)
            elif allow_mouse_buttons and t.lower() in ("mouseleft", "mouseright"):
                dev, key = _parse_mouse_button(entry_id, t)
            else:
                dev, key = keyboard_device_code, parse_keyboard_packed_key(t)
            _set_slot(entry_id, 1, dev, key)

    try:
        # Movement (entry_id 0x1D..0x20, keyboard dev 9)
        _parse_row(0x1F, 9, False, False, False, args.bind_move_forward, "Movement: Forward")
        _parse_row(0x20, 9, False, False, False, args.bind_move_backward, "Movement: Backward")
        _parse_row(0x1D, 9, False, False, False, args.bind_move_left, "Movement: Left")
        _parse_row(0x1E, 9, False, False, False, args.bind_move_right, "Movement: Right")

        # Look (entry_id 0x19..0x1C, allow "Mouse" axis)
        _parse_row(0x1A, 9, True, False, False, args.bind_look_up, "Look: Up")
        _parse_row(0x1C, 9, True, False, False, args.bind_look_down, "Look: Down")
        _parse_row(0x19, 9, True, False, False, args.bind_look_left, "Look: Left")
        _parse_row(0x1B, 9, True, False, False, args.bind_look_right, "Look: Right")

        # Zoom (entry_id 0x10/0x11, allow MouseWheelUp/Down)
        _parse_row(0x10, 9, False, True, False, args.bind_zoom_in, "Zoom: In")
        _parse_row(0x11, 9, False, True, False, args.bind_zoom_out, "Zoom: Out")

        # Others
        # Fire weapon maps to both entry_id 0x12 (dev 10) and 0x13 (dev 9), and supports MouseLeft.
        if args.bind_fire_weapon is not None:
            _parse_row(0x12, 10, False, False, True, args.bind_fire_weapon, "Others: Fire weapon")
            _parse_row(0x13, 9, False, False, True, args.bind_fire_weapon, "Others: Fire weapon")

        _parse_row(0x14, 10, False, False, True, args.bind_select_weapon, "Others: Select weapon")
        _parse_row(0x21, 8, False, False, False, args.bind_transform, "Others: Transform")
        _parse_row(0x15, 9, False, False, False, args.bind_air_brake, "Others: Air brake")
        _parse_row(0x3B, 8, False, False, False, args.bind_special, "Others: Special function")
    except ValueError as e:
        print(f"Error: keybind override: {e}", file=sys.stderr)
        sys.exit(1)

    # Show configuration (parity with C#)
    print("Onslaught Career Editor - CLI Mode")
    print("===================================")
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print()
    print("Configuration:")
    print(f"  Rank:           {rank}")
    print(f"  Kill count:     {args.kills}")
    print(f"  Goodies style:  {'NEW (gold)' if args.new else 'OLD (blue)'}")
    print(f"  Patch nodes:    {'Yes' if do_patch_nodes else 'No'}")
    print(f"  Patch links:    {'Yes' if do_patch_links else 'No'}")
    print(f"  Patch goodies:  {'Yes' if do_patch_goodies else 'No'}")
    print(f"  Patch kills:    {'Yes' if do_patch_kills else 'No'}")

    if level_ranks:
        print(f"  Level overrides: {len(level_ranks)} levels")

    if per_category_kills:
        print("  Per-category kills:")
        if KILL_AIRCRAFT in per_category_kills:
            print(f"    Aircraft:     {per_category_kills[KILL_AIRCRAFT]}")
        if KILL_VEHICLES in per_category_kills:
            print(f"    Vehicles:     {per_category_kills[KILL_VEHICLES]}")
        if KILL_EMPLACEMENTS in per_category_kills:
            print(f"    Emplacements: {per_category_kills[KILL_EMPLACEMENTS]}")
        if KILL_INFANTRY in per_category_kills:
            print(f"    Infantry:     {per_category_kills[KILL_INFANTRY]}")
        if KILL_MECHS in per_category_kills:
            print(f"    Mechs:        {per_category_kills[KILL_MECHS]}")

    if args.sound_volume is not None:
        print(f"  Sound volume:   {args.sound_volume:.3f}")
    if args.music_volume is not None:
        print(f"  Music volume:   {args.music_volume:.3f}")
    if invert_y_p1 is not None:
        print(f"  Invert Y (Walker) (P1): {'On' if invert_y_p1 else 'Off'}")
    if invert_y_p2 is not None:
        print(f"  Invert Y (Walker) (P2): {'On' if invert_y_p2 else 'Off'}")
    if invert_flight_p1 is not None:
        print(f"  Invert Y (Flight) (P1): {'On' if invert_flight_p1 else 'Off'}")
    if invert_flight_p2 is not None:
        print(f"  Invert Y (Flight) (P2): {'On' if invert_flight_p2 else 'Off'}")
    if vibration_p1 is not None:
        print(f"  Vibration (P1): {'On' if vibration_p1 else 'Off'}")
    if vibration_p2 is not None:
        print(f"  Vibration (P2): {'On' if vibration_p2 else 'Off'}")
    if args.controller_config_p1 is not None:
        print(f"  Ctrl cfg (P1):  {args.controller_config_p1}")
    if args.controller_config_p2 is not None:
        print(f"  Ctrl cfg (P2):  {args.controller_config_p2}")
    if args.experimental_pending_extra_goodies is not None:
        print("  Experimental pending-extra-goodies: ignored")

    if args.copy_options_from is not None:
        if args.no_copy_options_entries and args.no_copy_options_tail:
            print(
                "Error: --copy-options-from was provided, but both --no-copy-options-entries and --no-copy-options-tail were set (nothing to copy).",
                file=sys.stderr,
            )
            sys.exit(1)
        entries_on = not args.no_copy_options_entries
        tail_on = not args.no_copy_options_tail
        print(f"  Copy options from: {args.copy_options_from}")
        print(f"    - entries: {'Yes' if entries_on else 'No'}")
        print(f"    - tail:    {'Yes' if tail_on else 'No'}")

    if options_entry_overrides:
        print(f"  Keybind overrides: {len(options_entry_overrides)} entries (forces ControlSchemeIndex=0)")

    print()

    if args.experimental_pending_extra_goodies is not None:
        print(
            "Warning: --experimental-pending-extra-goodies is currently ignored for retail Steam until persistence semantics are re-verified.",
            file=sys.stderr
        )

    try:
        patch_file(
            args.input,
            args.output,
            new_goodies=args.new,
            kill_count=args.kills,
            rank=rank,
            level_ranks=level_ranks,
            per_category_kills=per_category_kills if per_category_kills else None,
            patch_nodes=do_patch_nodes,
            patch_links=do_patch_links,
            patch_goodies=do_patch_goodies,
            patch_kills=do_patch_kills,
            sound_volume=args.sound_volume,
            music_volume=args.music_volume,
            invert_y_p1=invert_y_p1,
            invert_y_p2=invert_y_p2,
            invert_flight_p1=invert_flight_p1,
            invert_flight_p2=invert_flight_p2,
            vibration_p1=vibration_p1,
            vibration_p2=vibration_p2,
            controller_config_p1=args.controller_config_p1,
            controller_config_p2=args.controller_config_p2,
            copy_options_from=args.copy_options_from,
            copy_options_entries=not args.no_copy_options_entries,
            copy_options_tail=not args.no_copy_options_tail,
            options_entry_overrides=options_entry_overrides if options_entry_overrides else None,
        )

        # Output summary
        print(f"Patched: {args.output}")

        # Show what was patched
        patched_sections = []

        if do_patch_nodes:
            if level_ranks:
                patched_sections.append(f"Nodes ({rank} + {len(level_ranks)} overrides)")
            else:
                patched_sections.append(f"Nodes ({rank}-rank)")

        if do_patch_links:
            patched_sections.append("Links")

        if do_patch_goodies:
            patched_sections.append(f"Goodies ({'NEW' if args.new else 'OLD'})")

        if do_patch_kills:
            if per_category_kills:
                patched_sections.append(f"Kills (custom per-category)")
            else:
                patched_sections.append(f"Kills ({args.kills} each)")

        has_settings_overrides = (
            args.sound_volume is not None or
            args.music_volume is not None or
            invert_y_p1 is not None or
            invert_y_p2 is not None or
            invert_flight_p1 is not None or
            invert_flight_p2 is not None or
            vibration_p1 is not None or
            vibration_p2 is not None or
            args.controller_config_p1 is not None or
            args.controller_config_p2 is not None
        )
        if has_settings_overrides:
            patched_sections.append("Career settings")

        if args.copy_options_from is not None:
            parts = []
            if not args.no_copy_options_entries:
                parts.append("entries")
            if not args.no_copy_options_tail:
                parts.append("tail")
            if parts:
                patched_sections.append(f"Options copy ({'+'.join(parts)})")

        if options_entry_overrides:
            patched_sections.append(f"Keybind overrides ({len(options_entry_overrides)} entries)")

        if patched_sections:
            print(f"  Patched: {', '.join(patched_sections)}")
        else:
            print("  WARNING: No sections selected for patching!")

        # Show skipped sections
        skipped = []
        if not do_patch_nodes:
            skipped.append("Nodes")
        if not do_patch_links:
            skipped.append("Links")
        if not do_patch_goodies:
            skipped.append("Goodies")
        if not do_patch_kills:
            skipped.append("Kills")
        if skipped:
            print(f"  Skipped: {', '.join(skipped)}")

        # Detailed kill counts if custom
        if do_patch_kills and per_category_kills:
            print(f"  Kill counts (default: {args.kills}):")
            categories = ['Aircraft', 'Vehicles', 'Emplacements', 'Infantry', 'Mechs']
            for i, cat in enumerate(categories):
                count = per_category_kills.get(i, args.kills)
                override = " *" if i in per_category_kills else ""
                print(f"    {cat}: {count}{override}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
