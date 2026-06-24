#!/usr/bin/env python3
"""Check the current BattleEngine weapon construction-side projectile candidate.

This is a bounded static RE probe. It consumes ignored read-only Ghidra exports
that connect weapon construction to a stronger projectile-body candidate:

- `CWorldPhysicsManager__CreateWeaponByIndex` allocates the weapon-like object.
- `CEquipment__ctor_like_00505e00` installs vtable pointer `0x005dfc94`.
- vtable slot 0 points at raw code `0x00506930`, which is not currently a
  function in Ghidra.
- the slot-0 body range reaches projectile creation/targeting helper calls.

The probe intentionally does not rename the raw slot or claim exact source
`CWeapon::Fire` / `CBattleEngine::WeaponFired` identity.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "battleengine-weapon-construction-candidates" / "current"
DEFAULT_INDEX = BASE / "decompile" / "index.tsv"
DEFAULT_CREATE_WEAPON = BASE / "decompile" / "0050f6d0_CWorldPhysicsManager__CreateWeaponByIndex.c"
DEFAULT_CTOR = BASE / "decompile" / "00505e00_CEquipment__ctor_like_00505e00.c"
DEFAULT_VTABLE = BASE / "vtable" / "equipment_vtable_005dfc94.tsv"
DEFAULT_SLOT0_BODY = BASE / "vtable" / "slot0_005069f0_body_disasm.tsv"
DEFAULT_OUT = BASE / "weapon-construction-candidate.json"

EXPECTED_CREATE_ADDRESS = "0x0050f6d0"
EXPECTED_CTOR_ADDRESS = "0x00505e00"
EXPECTED_SLOT0_ADDRESS = "0x00506930"
EXPECTED_VTABLE_ADDRESS = "0x005dfc94"
EXPECTED_SLOT1_ADDRESS = "0x00505f70"
EXPECTED_BODY_CALL_TARGETS = {
    "0x0040c2e0": "CEngine__CanSpawnBurstForResolvedEntry",
    "0x0050f7a0": "CWorldPhysicsManager__CreateProjectile",
    "0x004daab0": "CEngine__SetProjectileTargetReader",
    "0x00407060": "CEngine__MoveBurstReaderToCooldownSet",
    "0x0040c340": "CEngine__RandomizeBurstOffsetsAndAccumulateRange",
}
STEALTH_RESET_TOKENS = ("0x4ac", "0x5d4", "0x5d8", "0x5dc", "00406fc0", "00406560")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def index_status(rows: list[dict[str, str]], address: str) -> str:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get("address", "")) == target:
            return row.get("status", "")
    return ""


def extract_call_targets(disasm_text: str) -> list[str]:
    targets: list[str] = []
    for line in disasm_text.splitlines():
        if "\tCALL\t" not in line:
            continue
        match = re.search(r"0x[0-9a-fA-F]{8}", line)
        if match:
            targets.append(normalize_address(match.group(0)))
    return targets


def build_report(
    *,
    index_path: Path = DEFAULT_INDEX,
    create_weapon_path: Path = DEFAULT_CREATE_WEAPON,
    ctor_path: Path = DEFAULT_CTOR,
    vtable_path: Path = DEFAULT_VTABLE,
    slot0_body_path: Path = DEFAULT_SLOT0_BODY,
) -> dict[str, object]:
    index_path = resolve(index_path)
    create_weapon_path = resolve(create_weapon_path)
    ctor_path = resolve(ctor_path)
    vtable_path = resolve(vtable_path)
    slot0_body_path = resolve(slot0_body_path)

    failures: list[str] = []
    for label, path in (
        ("index", index_path),
        ("CreateWeaponByIndex decompile", create_weapon_path),
        ("CEquipment constructor decompile", ctor_path),
        ("equipment vtable dump", vtable_path),
        ("slot0 body disassembly", slot0_body_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    index_rows = read_tsv(index_path)
    create_text = read_text(create_weapon_path)
    ctor_text = read_text(ctor_path)
    vtable_rows = read_tsv(vtable_path)
    slot0_body_text = read_text(slot0_body_path)

    create_status = index_status(index_rows, EXPECTED_CREATE_ADDRESS)
    ctor_status = index_status(index_rows, EXPECTED_CTOR_ADDRESS)
    slot0_status = index_status(index_rows, EXPECTED_SLOT0_ADDRESS)
    if create_status != "OK":
        failures.append(f"CreateWeaponByIndex export status is {create_status or '<missing>'}")
    if ctor_status != "OK":
        failures.append(f"CEquipment constructor export status is {ctor_status or '<missing>'}")
    if slot0_status != "MISSING":
        failures.append(f"slot0 raw code export status should stay MISSING before mutation, got {slot0_status or '<missing>'}")

    if "OID__AllocObject(0xb0" not in create_text:
        failures.append("CreateWeaponByIndex decompile is missing 0xb0 allocation evidence")
    if "CEquipment__ctor_like_00505e00" not in create_text:
        failures.append("CreateWeaponByIndex decompile is missing CEquipment constructor call")
    if "PTR_LAB_005dfc94" not in ctor_text:
        failures.append("CEquipment constructor decompile is missing vtable pointer 0x005dfc94")

    slot0_row = next((row for row in vtable_rows if row.get("slot") == "0"), {})
    slot1_row = next((row for row in vtable_rows if row.get("slot") == "1"), {})
    slot0_ptr = normalize_address(slot0_row.get("ptr", "")) if slot0_row else ""
    slot1_ptr = normalize_address(slot1_row.get("ptr", "")) if slot1_row else ""
    if slot0_ptr != EXPECTED_SLOT0_ADDRESS:
        failures.append(f"equipment vtable slot 0 expected {EXPECTED_SLOT0_ADDRESS}, got {slot0_ptr or '<missing>'}")
    if slot1_ptr != EXPECTED_SLOT1_ADDRESS:
        failures.append(f"equipment vtable slot 1 expected {EXPECTED_SLOT1_ADDRESS}, got {slot1_ptr or '<missing>'}")

    call_targets = sorted(set(extract_call_targets(slot0_body_text)))
    for target, name in EXPECTED_BODY_CALL_TARGETS.items():
        if target not in call_targets:
            failures.append(f"missing slot0 body call target {target} ({name})")

    lower_body = slot0_body_text.lower()
    unexpected_stealth_tokens = [token for token in STEALTH_RESET_TOKENS if token in lower_body]
    if unexpected_stealth_tokens:
        failures.append(f"unexpected stealth/AddProjectile token references in slot0 body: {unexpected_stealth_tokens}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-weapon-construction-candidate.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": (
            "construction-vtable-slot0-projectile-body-candidate"
            if status == "PASS"
            else "blocked-or-unexpected-weapon-construction-candidate"
        ),
        "inputs": {
            "index": relative(index_path),
            "createWeaponByIndex": relative(create_weapon_path),
            "constructor": relative(ctor_path),
            "vtable": relative(vtable_path),
            "slot0Body": relative(slot0_body_path),
        },
        "constructionEvidence": {
            "createWeaponByIndexAddress": EXPECTED_CREATE_ADDRESS,
            "allocationSize": "0xb0",
            "constructorAddress": EXPECTED_CTOR_ADDRESS,
            "vtableAddress": EXPECTED_VTABLE_ADDRESS,
            "slot0RawAddress": EXPECTED_SLOT0_ADDRESS,
            "slot0GhidraFunctionStatus": slot0_status or "<missing>",
        },
        "vtable": {
            "slot0Ptr": slot0_ptr,
            "slot0Name": slot0_row.get("ptr_name", "") if slot0_row else "",
            "slot1Ptr": slot1_ptr,
            "slot1Name": slot1_row.get("ptr_name", "") if slot1_row else "",
        },
        "slot0BodyCallTargets": call_targets,
        "expectedSlot0BodyCallTargets": EXPECTED_BODY_CALL_TARGETS,
        "unexpectedStealthResetTokens": unexpected_stealth_tokens,
        "failures": failures,
        "whatIsProven": [
            "The current read-only construction exports connect CWorldPhysicsManager__CreateWeaponByIndex to CEquipment__ctor_like_00505e00.",
            "The constructor installs vtable pointer 0x005dfc94, whose slot 0 points at raw code 0x00506930 and slot 1 points at the already known destructor-like CWeapon vfunc.",
            "The current raw slot-0 body disassembly reaches projectile creation and projectile-target helper calls.",
            "The current raw slot-0 body range checked by this probe does not contain direct CBattleEngine__AddProjectile/helper addresses or tracked stealth-adjacent offset tokens.",
        ],
        "notProven": [
            "This does not rename 0x00506930 or prove final function boundaries.",
            "This does not prove exact source CWeapon::Fire or CBattleEngine::WeaponFired identity.",
            "This does not prove retail weapon fire never clears stealth.",
            "This does not rule out an indirect, virtual-dispatch, callback, inlined, or runtime-only stealth reset elsewhere.",
            "This does not mutate Ghidra, apply a rename map, patch BEA.exe, launch the game, or prove runtime cloak/fire behavior.",
        ],
        "privacy": "Report stores repo-relative filenames, public addresses, function names, call targets, counts, and proof boundaries only; raw decompile/vtable/disassembly exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--create-weapon", type=Path, default=DEFAULT_CREATE_WEAPON)
    parser.add_argument("--ctor", type=Path, default=DEFAULT_CTOR)
    parser.add_argument("--vtable", type=Path, default=DEFAULT_VTABLE)
    parser.add_argument("--slot0-body", type=Path, default=DEFAULT_SLOT0_BODY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(
        index_path=args.index,
        create_weapon_path=args.create_weapon,
        ctor_path=args.ctor,
        vtable_path=args.vtable,
        slot0_body_path=args.slot0_body,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon construction candidate probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Slot0 raw address: {report['constructionEvidence']['slot0RawAddress']}")
        print(f"Slot0 call targets observed: {len(report['slot0BodyCallTargets'])}")
        print(f"Unexpected stealth/AddProjectile tokens: {len(report['unexpectedStealthResetTokens'])}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
