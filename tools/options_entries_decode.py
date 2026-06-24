#!/usr/bin/env python3
"""
Decode the 0x20-byte "options entries" block inside BEA .bes saves and defaultoptions.bea.

These entries are persisted control bindings: two binding slots per action/entry_id.

Steam build nuance (verified in BEA.exe):
- `CCareer__Load` @ 0x00421200 loads `defaultoptions.bea` with `flag=0`, which applies these entries + the 0x56-byte tail snapshot.
- Loading a `.bes` career save uses `CCareer::Load(flag=1)`, which does NOT apply the options entries/tail (global options persist).

See: reverse-engineering/save-file/save-format.md (Region 3: Options Block + Tail)
"""

from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass
from pathlib import Path


OPTIONS_START = 0x24BE
TAIL_SIZE = 0x56
ENTRY_SIZE = 0x20
BASE_SIZE = OPTIONS_START + TAIL_SIZE  # 0x2514

# Entry ID -> semantic action name (retail Steam BEA.exe, Feb 2026).
# Source-of-truth: reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md
ENTRY_NAMES: dict[int, str] = {
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

# Retail renderer mapping note:
# ControlsUI__RenderBindingsList (0x00455010) indexes binding slot as (param_2 / 2)
# with no branch on g_ControlSchemeIndex. In practice this means slot0/slot1 map
# directly to the on-screen left/right columns (Player 1 / Player 2 labels) for both
# custom and preset schemes. Presets rewrite values, not column orientation.

# Minimal scan-name map for nicer prints (extended arrows use scan|0x80).
SCAN_NAMES: dict[int, str] = {
    0x000F: "Tab",
    0x002A: "LShift",
    0x0036: "RShift",
    0x0039: "Space",
    0x003A: "CapsLock",
    0x0027: "Key ;",
    0x009D: "RControl",
    0x00C8: "Up",
    0x00CB: "Left",
    0x00CD: "Right",
    0x00D0: "Down",
}

NUMPAD_SCAN_TO_NAME: dict[int, str] = {
    0x0047: "Num 7",
    0x0048: "Num 8",
    0x0049: "Num 9",
    0x004B: "Num 4",
    0x004C: "Num 5",
    0x004D: "Num 6",
    0x004F: "Num 1",
    0x0050: "Num 2",
    0x0051: "Num 3",
    0x0052: "Num 0",
}


def _u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def _u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def _i32(data: bytes, off: int) -> int:
    return struct.unpack_from("<i", data, off)[0]


def _f32(data: bytes, off: int) -> float:
    return struct.unpack_from("<f", data, off)[0]


def _u8(data: bytes, off: int) -> int:
    return data[off]


def _fmt_u32(v: int) -> str:
    return f"0x{v:08X} ({v})"


def _fmt_i32(v: int) -> str:
    return f"{v} (0x{v & 0xFFFFFFFF:08X})"


def _fmt_vk(vk: int) -> str:
    if vk == 0:
        return "0x0000"
    if 0x20 <= vk <= 0x7E:
        return f"'{chr(vk)}' (0x{vk:02X})"
    return f"0x{vk:04X}"


def _fmt_scan(scan: int) -> str:
    return f"0x{scan:04X}"

def _fmt_binding(device_code: int, packed_key: int) -> str:
    vk = (packed_key >> 16) & 0xFFFF
    scan = packed_key & 0xFFFF

    # Mouse look axes (Steam preset uses these for Look entries).
    # NOTE: scan=0 => packed_key==0, so device_code must be checked before treating packed_key==0 as unbound.
    if device_code in (11, 12):
        axis = "MouseX" if scan == 0 else ("MouseY" if scan == 1 else "MouseAxis")
        if axis == "MouseAxis":
            return f"Mouse({scan})"
        return f"{axis}{'+' if device_code == 11 else '-'}"

    # Mouse wheel / RMB (observed in Steam build for Zoom / Select weapon)
    if device_code == 16:
        if scan == 4:
            return "MouseWheelDown"
        if scan == 3:
            return "MouseWheelUp"
        if scan == 2:
            return "MouseRight"
        return f"Mouse({scan})"

    # Mouse left button (observed in Steam build for Fire weapon)
    if device_code in (15, 17) and vk == 0 and scan == 0:
        return "MouseLeft"

    if packed_key == 0:
        return "-"

    if vk != 0 and 0x20 <= vk <= 0x7E:
        return chr(vk)

    if scan in SCAN_NAMES:
        return SCAN_NAMES[scan]

    if vk == 0 and scan in NUMPAD_SCAN_TO_NAME:
        return NUMPAD_SCAN_TO_NAME[scan]

    return f"vk=0x{vk:04X} scan=0x{scan:04X}"


def _print_named_summary(entries: list[OptionsEntry], scheme_index: int) -> None:
    entries_by_id: dict[int, OptionsEntry] = {e.entry_id & 0xFFFFFFFF: e for e in entries if e.active != 0}
    if not entries_by_id:
        return

    print("bindings_summary:")
    if scheme_index == 1:
        print("  NOTE: ControlSchemeIndex=1 preset detected; retail mapping reads slot0/slot1 as P1/P2.")
    elif scheme_index != 0:
        print("  NOTE: ControlSchemeIndex!=0 is an unknown/preset scheme; output uses raw slot0/slot1 columns.")

    for entry_id in (
        0x1F, 0x20, 0x1D, 0x1E,
        0x1A, 0x1C, 0x19, 0x1B,
        0x10, 0x11,
        0x12, 0x13, 0x14, 0x21, 0x15, 0x3B,
    ):
        e = entries_by_id.get(entry_id)
        if e is None:
            continue
        name = ENTRY_NAMES.get(entry_id, f"entry_id=0x{entry_id:02X}")

        if scheme_index in (0, 1):
            print(f"  {name:24s} P1={_fmt_binding(e.slot0.device_code, e.slot0.packed_key):12s} P2={_fmt_binding(e.slot1.device_code, e.slot1.packed_key)}")
        else:
            print(f"  {name:24s} slot0={_fmt_binding(e.slot0.device_code, e.slot0.packed_key):12s} slot1={_fmt_binding(e.slot1.device_code, e.slot1.packed_key)}")

    print("")


@dataclass(frozen=True)
class BindingSlot:
    field0: int
    device_code: int
    packed_key: int

    @property
    def vk(self) -> int:
        return (self.packed_key >> 16) & 0xFFFF

    @property
    def scan(self) -> int:
        return self.packed_key & 0xFFFF


@dataclass(frozen=True)
class OptionsEntry:
    active: int
    entry_id: int
    slot0: BindingSlot
    slot1: BindingSlot


def parse_options_entries(data: bytes) -> tuple[list[OptionsEntry], int, int, int]:
    if len(data) < BASE_SIZE:
        raise ValueError(f"File too small: 0x{len(data):X} bytes (< 0x{BASE_SIZE:X})")

    extra = len(data) - BASE_SIZE
    if extra % ENTRY_SIZE != 0:
        raise ValueError(
            f"Size mismatch: len=0x{len(data):X} does not match 0x{BASE_SIZE:X} + 0x{ENTRY_SIZE:X}*N"
        )

    n = extra // ENTRY_SIZE
    entries: list[OptionsEntry] = []
    off = OPTIONS_START
    for _ in range(n):
        d0 = _u32(data, off + 0x00)
        entry_id = struct.unpack_from("<i", data, off + 0x04)[0]
        slot0 = BindingSlot(
            field0=_u32(data, off + 0x08),
            device_code=_u32(data, off + 0x0C),
            packed_key=_u32(data, off + 0x10),
        )
        slot1 = BindingSlot(
            field0=_u32(data, off + 0x14),
            device_code=_u32(data, off + 0x18),
            packed_key=_u32(data, off + 0x1C),
        )
        entries.append(OptionsEntry(active=d0 & 0xFF, entry_id=entry_id, slot0=slot0, slot1=slot1))
        off += ENTRY_SIZE

    tail_start = OPTIONS_START + ENTRY_SIZE * n
    scheme_index = _u16(data, tail_start + 0x08)
    language_index = _u16(data, tail_start + 0x0A)
    return entries, n, scheme_index, language_index


def parse_options_tail(data: bytes, tail_start: int) -> dict[str, object]:
    """Parse the fixed 0x56-byte OptionsTail snapshot (see save-format.md)."""
    if tail_start < 0 or tail_start + TAIL_SIZE > len(data):
        raise ValueError(f"Tail out of range: start=0x{tail_start:X} size=0x{TAIL_SIZE:X}")

    # Floats are stored as raw IEEE-754 bits in the tail.
    def f(off: int) -> tuple[float, int]:
        bits = _u32(data, tail_start + off)
        return _f32(data, tail_start + off), bits

    out: dict[str, object] = {}
    out["g_Options_UnknownFloat0"] = f(0x00)
    out["g_MouseSensitivity"] = f(0x04)
    out["g_ControlSchemeIndex"] = _u16(data, tail_start + 0x08)
    out["g_LanguageIndex"] = _u16(data, tail_start + 0x0A)
    out["g_MeshQualityDistance"] = f(0x0C)
    out["g_MeshLodBias"] = f(0x10)
    out["g_MeshQualityScaleFactor"] = f(0x14)

    # 0x18 is treated as a dword in OptionsTail_Write/Read (not a float in all code paths).
    out["g_MeshQualityLodTable"] = _u32(data, tail_start + 0x18)

    out["g_LandscapeLowresGeom"] = _u32(data, tail_start + 0x1C)
    out["g_ScreenShape"] = _u32(data, tail_start + 0x20)
    out["g_DisallowMipMapping"] = _u32(data, tail_start + 0x24)
    out["g_D3DDeviceIndex"] = _u32(data, tail_start + 0x28)
    out["g_TryLockableBackbuffer"] = _u32(data, tail_start + 0x2C)
    out["g_LandscapeMaxLevelsUser"] = _u32(data, tail_start + 0x30)
    out["g_UserTextureResLossShift"] = _u32(data, tail_start + 0x34)
    out["g_UserTextureAllow32Bit"] = _u32(data, tail_start + 0x38)

    out["g_ProfileMultisampleType"] = _i32(data, tail_start + 0x3C)
    out["g_InvertXAxisFlag"] = _u32(data, tail_start + 0x40)
    out["g_SoundEnabledFlag"] = _u32(data, tail_start + 0x44)
    out["g_SoundSampleRateIndex"] = _u32(data, tail_start + 0x48)
    out["g_SoundDeviceIndex"] = _u32(data, tail_start + 0x4C)
    out["g_Sound3DMethod"] = _u32(data, tail_start + 0x50)

    out["g_LandscapeDetailLevel2"] = _u8(data, tail_start + 0x54)
    out["g_LandscapeDetailLevel1"] = _u8(data, tail_start + 0x55)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path, help="Path to .bes or defaultoptions.bea")
    ap.add_argument("--only-active", action="store_true", help="Only show active entries (active!=0)")
    ap.add_argument("--tail-only", action="store_true", help="Only show tail snapshot (skip options entries)")
    ap.add_argument("--no-tail", action="store_true", help="Do not print tail snapshot fields")
    ap.add_argument("--no-summary", action="store_true", help="Do not print the named bindings summary")
    args = ap.parse_args(argv)

    data = args.path.read_bytes()
    entries, n, scheme_index, language_index = parse_options_entries(data)

    print(f"path: {args.path}")
    print(f"size: 0x{len(data):X} ({len(data)} bytes)")
    print(f"options_entries: start=0x{OPTIONS_START:X} count={n} (0x20*N = 0x{ENTRY_SIZE*n:X} bytes)")
    tail_start = OPTIONS_START + ENTRY_SIZE * n
    print(f"tail: start=0x{tail_start:X} size=0x{TAIL_SIZE:X}")
    print(f"g_ControlSchemeIndex: {scheme_index}")
    print(f"g_LanguageIndex: {language_index}")
    print("")

    if not args.no_tail:
        tail = parse_options_tail(data, tail_start)
        print("tail_snapshot:")
        u0, u0_bits = tail["g_Options_UnknownFloat0"]  # type: ignore[assignment]
        ms, ms_bits = tail["g_MouseSensitivity"]  # type: ignore[assignment]
        mqd, mqd_bits = tail["g_MeshQualityDistance"]  # type: ignore[assignment]
        mlb, mlb_bits = tail["g_MeshLodBias"]  # type: ignore[assignment]
        mqsf, mqsf_bits = tail["g_MeshQualityScaleFactor"]  # type: ignore[assignment]

        print(f"  +0x00 g_Options_UnknownFloat0: {u0:.3f} (bits=0x{u0_bits:08X})")
        print(f"  +0x04 g_MouseSensitivity:      {ms:.3f} (bits=0x{ms_bits:08X})")
        print(f"  +0x08 g_ControlSchemeIndex:    {tail['g_ControlSchemeIndex']}")
        print(f"  +0x0A g_LanguageIndex:         {tail['g_LanguageIndex']}")
        print(f"  +0x0C g_MeshQualityDistance:   {mqd:.3f} (bits=0x{mqd_bits:08X})")
        print(f"  +0x10 g_MeshLodBias:           {mlb:.3f} (bits=0x{mlb_bits:08X})")
        print(f"  +0x14 g_MeshQualityScaleFactor:{mqsf:.3f} (bits=0x{mqsf_bits:08X})")
        lod_table = int(tail["g_MeshQualityLodTable"])
        lod_table_f = struct.unpack("<f", struct.pack("<I", lod_table))[0]
        print(f"  +0x18 g_MeshQualityLodTable:   0x{lod_table:08X} (f={lod_table_f:.3f})")
        print(f"  +0x1C g_LandscapeLowresGeom:   {_fmt_u32(int(tail['g_LandscapeLowresGeom']))}")
        print(f"  +0x20 g_ScreenShape:           {_fmt_u32(int(tail['g_ScreenShape']))} (0=4:3, 1=16:9, 2=1:1)")
        print(f"  +0x24 g_DisallowMipMapping:    {_fmt_u32(int(tail['g_DisallowMipMapping']))}")
        print(f"  +0x28 g_D3DDeviceIndex:        {_fmt_u32(int(tail['g_D3DDeviceIndex']))}")
        print(f"  +0x2C g_TryLockableBackbuffer: {_fmt_u32(int(tail['g_TryLockableBackbuffer']))}")
        print(f"  +0x30 g_LandscapeMaxLevelsUser:{_fmt_u32(int(tail['g_LandscapeMaxLevelsUser']))}")
        print(f"  +0x34 g_UserTextureResLossShift:{_fmt_u32(int(tail['g_UserTextureResLossShift']))}")
        print(f"  +0x38 g_UserTextureAllow32Bit: {_fmt_u32(int(tail['g_UserTextureAllow32Bit']))}")
        print(f"  +0x3C g_ProfileMultisampleType:{_fmt_i32(int(tail['g_ProfileMultisampleType']))}")
        print(f"  +0x40 g_InvertXAxisFlag:       {_fmt_u32(int(tail['g_InvertXAxisFlag']))}")
        print(f"  +0x44 g_SoundEnabledFlag:      {_fmt_u32(int(tail['g_SoundEnabledFlag']))}")
        print(f"  +0x48 g_SoundSampleRateIndex:  {_fmt_u32(int(tail['g_SoundSampleRateIndex']))}")
        print(f"  +0x4C g_SoundDeviceIndex:      {_fmt_u32(int(tail['g_SoundDeviceIndex']))}")
        print(f"  +0x50 g_Sound3DMethod:         {_fmt_u32(int(tail['g_Sound3DMethod']))}")
        ld2 = tail["g_LandscapeDetailLevel2"]
        ld1 = tail["g_LandscapeDetailLevel1"]
        level = 2 if ld2 != 0 else ld1
        print(f"  +0x54 g_LandscapeDetailLevel2: 0x{ld2:02X}")
        print(f"  +0x55 g_LandscapeDetailLevel1: 0x{ld1:02X} (effective={level})")
        print("")

    if args.tail_only:
        return 0

    for e in entries:
        if args.only_active and e.active == 0:
            continue
        s0 = e.slot0
        s1 = e.slot1
        print(
            "entry_id=0x{eid:02X} active={act} | "
            "slot0: dev={d0:2d} field0=0x{f0:08X} key=0x{p0:08X} (vk={vk0}, scan={sc0}) | "
            "slot1: dev={d1:2d} field0=0x{f1:08X} key=0x{p1:08X} (vk={vk1}, scan={sc1})".format(
                eid=e.entry_id & 0xFFFFFFFF,
                act=e.active,
                d0=s0.device_code,
                f0=s0.field0,
                p0=s0.packed_key,
                vk0=_fmt_vk(s0.vk),
                sc0=_fmt_scan(s0.scan),
                d1=s1.device_code,
                f1=s1.field0,
                p1=s1.packed_key,
                vk1=_fmt_vk(s1.vk),
                sc1=_fmt_scan(s1.scan),
            )
        )

    if not args.no_summary:
        _print_named_summary(entries, scheme_index)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
