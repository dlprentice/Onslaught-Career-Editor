#!/usr/bin/env python3
"""Hash-bound identity checks for retail vtable slot 66 / 0x004d8e40.

Re-verifies against a pristine PE (default: local-lab safe-copy original backup
sha256 74154bfa…). Does not invent Stuart method names; it only checks bytes.

Exit 0 on full pass. Exit 2 on failed assertion. Exit 1 on usage/IO error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

EXPECTED_SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

SLOT = 66
SLOT_BYTE_OFFSET = SLOT * 4  # 0x108

CROUND_VT_BASE = 0x005DE82C
CMISSILE_STYLE_VT_BASE = 0x005E3BA4
CBATTLEENGINE_VT_BASE = 0x005D89C4

ROUND_BODY = 0x004D8E40
BE_MOVE_BODY = 0x004081C0
CACTOR_MOVE_BODY = 0x004015E0
EFFECT_HELPER = 0x004D9F30
CALLSITE = 0x00401AEA
CALLSITE_BYTES = bytes.fromhex("ff9208010000")  # call dword ptr [edx+0x108]
BODY_PROLOGUE = bytes.fromhex("81ec18010000")  # sub esp, 0x118
BODY_SIZE = 0x0AC5  # 0x004d9905 - 0x004d8e40


def parse_pe_sections(data: bytes) -> tuple[int, list[tuple[str, int, int, int, int]]]:
    if data[:2] != b"MZ":
        raise ValueError("not MZ")
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew : e_lfanew + 4] != b"PE\0\0":
        raise ValueError("not PE")
    opt = e_lfanew + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic != 0x10B:
        raise ValueError("PE32 only")
    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_off = e_lfanew + 24 + size_opt
    sections: list[tuple[str, int, int, int, int]] = []
    for i in range(num_sections):
        o = sec_off + i * 40
        name = data[o : o + 8].split(b"\0", 1)[0].decode("ascii", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((name, va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(
    va: int, image_base: int, sections: list[tuple[str, int, int, int, int]]
) -> int:
    rva = va - image_base
    for _name, sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            return rawptr + (rva - sva)
    raise ValueError(f"VA not mapped: 0x{va:X}")


def u32_va(
    data: bytes, va: int, image_base: int, sections: list[tuple[str, int, int, int, int]]
) -> int:
    return struct.unpack_from("<I", data, va_to_off(va, image_base, sections))[0]


def find_direct_calls(
    data: bytes,
    body_va: int,
    body_size: int,
    image_base: int,
    sections: list[tuple[str, int, int, int, int]],
) -> list[tuple[int, int]]:
    off = va_to_off(body_va, image_base, sections)
    body = data[off : off + body_size]
    hits: list[tuple[int, int]] = []
    for i in range(len(body) - 5):
        if body[i] != 0xE8:
            continue
        rel = struct.unpack_from("<i", body, i + 1)[0]
        tgt = body_va + i + 5 + rel
        hits.append((body_va + i, tgt))
    return hits


def analyze(specimen: Path) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    image_base, sections = parse_pe_sections(data)

    checks: list[dict] = []

    def check(name: str, ok: bool, detail: object) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            raise AssertionError(f"{name}: {detail}")

    check("specimen_sha256", sha == EXPECTED_SPECIMEN_SHA256, sha)
    check("image_base", image_base == 0x400000, hex(image_base))
    check("slot_byte_offset", SLOT_BYTE_OFFSET == 0x108, hex(SLOT_BYTE_OFFSET))

    cround_cell = CROUND_VT_BASE + SLOT_BYTE_OFFSET
    missile_cell = CMISSILE_STYLE_VT_BASE + SLOT_BYTE_OFFSET
    cbe_cell = CBATTLEENGINE_VT_BASE + SLOT_BYTE_OFFSET

    cround_tgt = u32_va(data, cround_cell, image_base, sections)
    missile_tgt = u32_va(data, missile_cell, image_base, sections)
    cbe_tgt = u32_va(data, cbe_cell, image_base, sections)

    check("cround_slot66_target", cround_tgt == ROUND_BODY, hex(cround_tgt))
    check("cmissile_slot66_target", missile_tgt == ROUND_BODY, hex(missile_tgt))
    check("cbe_slot66_is_move_body", cbe_tgt == BE_MOVE_BODY, hex(cbe_tgt))

    cs_off = va_to_off(CALLSITE, image_base, sections)
    check(
        "callsite_call_edx_plus_108",
        data[cs_off : cs_off + 6] == CALLSITE_BYTES,
        data[cs_off : cs_off + 6].hex(),
    )

    body_off = va_to_off(ROUND_BODY, image_base, sections)
    check(
        "body_prologue",
        data[body_off : body_off + 6] == BODY_PROLOGUE,
        data[body_off : body_off + 6].hex(),
    )

    calls = find_direct_calls(data, ROUND_BODY, BODY_SIZE, image_base, sections)
    targets = {tgt for _site, tgt in calls}
    check("body_calls_effect_helper_004d9f30", EFFECT_HELPER in targets, sorted(hex(t) for t in targets if t == EFFECT_HELPER))
    check(
        "body_calls_CActor_Move_004015e0",
        CACTOR_MOVE_BODY in targets,
        hex(CACTOR_MOVE_BODY) if CACTOR_MOVE_BODY in targets else "missing",
    )

    rtti = {}
    for name in (
        b".?AVCRound@@",
        b".?AVCMissile@@",
        b".?AVCBattleEngine@@",
        b".?AVCActor@@",
    ):
        idx = data.find(name)
        rtti[name.decode()] = hex(idx) if idx >= 0 else None
        check(f"rtti_present_{name.decode()}", idx >= 0, hex(idx) if idx >= 0 else None)

    return {
        "schema": "bea.re.vfunc66-slot-identity.v1",
        "status": "PASS",
        "specimen": str(specimen),
        "specimen_sha256": sha,
        "slot": SLOT,
        "slot_byte_offset": hex(SLOT_BYTE_OFFSET),
        "cround_vtable_base": hex(CROUND_VT_BASE),
        "cround_slot66_cell": hex(cround_cell),
        "cround_slot66_target": hex(cround_tgt),
        "cmissile_slot66_cell": hex(missile_cell),
        "cmissile_slot66_target": hex(missile_tgt),
        "cbattleengine_slot66_cell": hex(cbe_cell),
        "cbattleengine_slot66_target": hex(cbe_tgt),
        "family_note": (
            "Slot 66 of CBattleEngine vtable is the documented CBattleEngine::Move "
            "body; CRound/CMissile-style share the same ordinal pointing at 0x004d8e40."
        ),
        "source_spelling": {
            "status": "OPEN",
            "bounded_hypothesis": "CRound::Move (actor Move override)",
            "reason": (
                "Pinned GPL has CActor::Move and CBattleEngine::Move correspondence "
                "at slot 66, but no CRound.h/.cpp in references/Onslaught; do not "
                "campaign-promote Stuart spelling without that unit or equivalent map."
            ),
        },
        "rtti_type_names": rtti,
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--specimen",
        type=Path,
        default=Path(
            "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
        ),
        help="Path to pristine PE (sha256 74154bfa…)",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path to write the full result JSON",
    )
    args = parser.parse_args(argv)

    try:
        if not args.specimen.is_file():
            print(f"specimen not found: {args.specimen}", file=sys.stderr)
            return 1
        result = analyze(args.specimen.resolve())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"error: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(result, indent=2)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    print("VFUNC66_SLOT_IDENTITY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
