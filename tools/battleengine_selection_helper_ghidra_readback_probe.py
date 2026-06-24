#!/usr/bin/env python3
"""Validate read-only Ghidra read-back for BattleEngine selection helpers.

This probe consumes decompile files exported by ExportFunctionsByAddressDecompile.java.
It does not launch the game, read BEA.exe directly, mutate BEA.exe, or mutate a Ghidra
project. Output stays under subagents/ and records function names, addresses, token
labels, and line numbers only.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECOMPILE_DIR = (
    ROOT
    / "subagents"
    / "battleengine-selection-helper-ghidra-readback"
    / "current"
    / "decompile"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-selection-helper-ghidra-readback"
    / "current"
    / "battleengine-selection-helper-ghidra-readback.json"
)


@dataclass(frozen=True)
class FunctionExpectation:
    address: str
    name: str
    signature_tokens: tuple[str, ...]
    file_name: str
    required_tokens: tuple[str, ...]
    note: str


EXPECTATIONS: tuple[FunctionExpectation, ...] = (
    FunctionExpectation(
        "0x00411e70",
        "CCockpit__CycleToNextUsableWeapon",
        ("CCockpit__CycleToNextUsableWeapon", "__fastcall"),
        "00411e70_CCockpit__CycleToNextUsableWeapon.c",
        (
            "CSPtrSet__First(param_1)",
            "CSPtrSet__Next(param_1)",
            "*(int *)((int)param_1 + 0x10) + 1",
            "+ 0x55c + iVar6 * 4",
            "+ 0x52c + iVar6 * 4",
            "*(undefined4 *)((int)pvVar4 + 0x60) = 0",
            "CGeneralVolume__SetParam2CC_ToOne",
        ),
        "Fresh headless read-back confirms the named cycle helper and selected traversal, ammo/energy gate, active flag, and selection-change tokens.",
    ),
    FunctionExpectation(
        "0x004124d0",
        "CGeneralVolume__GetSelectedWeaponDef",
        ("CGeneralVolume__GetSelectedWeaponDef", "__fastcall"),
        "004124d0_CGeneralVolume__GetSelectedWeaponDef.c",
        (
            "if (iVar3 == *(int *)((int)param_1 + 0x10))",
            "return *(int *)(*(int *)(iVar2 + 0xa4) + 4)",
            "return 0",
        ),
        "Fresh headless read-back confirms the selected-weapon-definition lookup path through indexed set entry data.",
    ),
    FunctionExpectation(
        "0x004145f0",
        "CGeneralVolume__GetSelectedWeaponDef_CachedPath",
        ("CGeneralVolume__GetSelectedWeaponDef_CachedPath", "__fastcall"),
        "004145f0_CGeneralVolume__GetSelectedWeaponDef_CachedPath.c",
        (
            "CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1)",
            "return *(int *)(*(int *)(iVar1 + 0xa4) + 4)",
            "return 0",
        ),
        "Fresh headless read-back confirms the cached selected-weapon-definition lookup path.",
    ),
    FunctionExpectation(
        "0x00412cf0",
        "CCockpit__DestroyWeaponSetAndOwnedNodes",
        ("CCockpit__DestroyWeaponSetAndOwnedNodes", "__fastcall"),
        "00412cf0_CCockpit__DestroyWeaponSetAndOwnedNodes.c",
        (
            "CSPtrSet__Remove(param_1,value)",
            "(**(code **)(**(int **)((int)param_1 + 0x18) + 4))(1)",
            "(**(code **)(**(int **)((int)param_1 + 0x1c) + 4))(1)",
            "CSPtrSet__Clear(param_1)",
        ),
        "Fresh headless read-back confirms the named weapon-set cleanup helper and selected owned-node destroy/clear tokens.",
    ),
    FunctionExpectation(
        "0x00412610",
        "CBattleEngine__GetIndexedEntry",
        ("CBattleEngine__GetIndexedEntry", "__fastcall"),
        "00412610_CBattleEngine__GetIndexedEntry.c",
        (
            "if (iVar3 == *(int *)((int)param_1 + 0x10))",
            "return iVar2",
            "return 0",
        ),
        "Fresh headless read-back confirms the indexed-entry lookup helper and selected list-index match tokens.",
    ),
    FunctionExpectation(
        "0x00412570",
        "CBattleEngine__IsIndexedEntryUsable",
        ("CBattleEngine__IsIndexedEntryUsable", "__fastcall"),
        "00412570_CBattleEngine__IsIndexedEntryUsable.c",
        (
            "+ 0x55c + iVar2 * 4",
            "_DAT_005d856c",
            "+ 0x52c + iVar2 * 4",
            "+ 0x544 + iVar2 * 4",
            "return 1",
        ),
        "Fresh headless read-back confirms indexed-entry usability checks for selected readiness, energy/ammo, and cooldown-like gates.",
    ),
    FunctionExpectation(
        "0x00414630",
        "CBattleEngine__IsResolvedEntryUsable",
        ("CBattleEngine__IsResolvedEntryUsable", "__fastcall"),
        "00414630_CBattleEngine__IsResolvedEntryUsable.c",
        (
            "CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1)",
            "+ 0x55c + iVar2 * 4",
            "_DAT_005d856c",
            "+ 0x544 + iVar2 * 4",
            "return 1",
        ),
        "Fresh headless read-back confirms resolved-entry usability checks after current/fallback resolution.",
    ),
    FunctionExpectation(
        "0x004102a0",
        "CBattleEngine__DestroySPtrSetElementsAndClear",
        ("CBattleEngine__DestroySPtrSetElementsAndClear", "__fastcall"),
        "004102a0_CBattleEngine__DestroySPtrSetElementsAndClear.c",
        (
            "CSPtrSet__Remove(param_1,value)",
            "CSPtrSet__Clear(param_1)",
            "return",
        ),
        "Fresh headless read-back confirms the generic SPtrSet element remove-and-clear helper.",
    ),
    FunctionExpectation(
        "0x00407310",
        "CBattleEngine__IsCurrentResolvedEntry",
        ("CBattleEngine__IsCurrentResolvedEntry", "__thiscall"),
        "00407310_CBattleEngine__IsCurrentResolvedEntry.c",
        (
            "CBattleEngine__GetIndexedEntry",
            "CGeneralVolume__ResolveCurrentOrFallbackEntry",
            "iVar1 == param_1",
            "return 1",
            "return 0",
        ),
        "Fresh headless read-back confirms current/resolved entry comparison across indexed and fallback selection paths.",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def token_line_hits(lines: list[str], tokens: tuple[str, ...]) -> dict[str, list[int]]:
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def parse_index(index_path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not index_path.is_file():
        return {}

    rows: dict[tuple[str, str], dict[str, str]] = {}
    with index_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        next(reader, None)
        for cells in reader:
            if len(cells) < 4:
                continue
            address, name, signature, status = cells[:4]
            rows[(address.lower(), name)] = {
                "address": address,
                "name": name,
                "signature": signature,
                "status": status,
            }
    return rows


def summarize(
    expectation: FunctionExpectation,
    decompile_dir: Path,
    index_rows: dict[tuple[str, str], dict[str, str]],
) -> dict[str, object]:
    row = index_rows.get((expectation.address.lower(), expectation.name))
    failures: list[str] = []
    if row is None:
        row = {"address": expectation.address, "name": expectation.name, "signature": "", "status": "MISSING"}
        failures.append("function row missing from index.tsv")
    elif row.get("status") != "OK":
        failures.append(f"index.tsv status is {row.get('status')}")

    signature_hits = {token: token in row.get("signature", "") for token in expectation.signature_tokens}
    missing_signature_tokens = [token for token, present in signature_hits.items() if not present]
    failures.extend(f"missing signature token: {token}" for token in missing_signature_tokens)

    decompile_path = decompile_dir / expectation.file_name
    token_hits: dict[str, list[int]] = {}
    if not decompile_path.is_file():
        failures.append(f"missing decompile file: {expectation.file_name}")
    else:
        token_hits = token_line_hits(read_lines(decompile_path), expectation.required_tokens)
        failures.extend(f"missing token: {token}" for token, hits in token_hits.items() if not hits)

    return {
        "address": expectation.address,
        "name": expectation.name,
        "status": "PASS" if not failures else "FAIL",
        "note": expectation.note,
        "indexStatus": row.get("status"),
        "signatureTokenPresence": signature_hits,
        "missingSignatureTokens": missing_signature_tokens,
        "decompileFile": relative(decompile_path),
        "tokenLineHits": token_hits,
        "failures": failures,
    }


def build_report(decompile_dir: Path) -> dict[str, object]:
    index_rows = parse_index(decompile_dir / "index.tsv")
    results = [summarize(expectation, decompile_dir, index_rows) for expectation in EXPECTATIONS]
    failures = [item for item in results if item["status"] != "PASS"]
    return {
        "schema": "battleengine-selection-helper-ghidra-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not failures else "blocked",
        "decompileDir": relative(decompile_dir),
        "mutation": False,
        "functionsChecked": len(results),
        "functionsPassed": len(results) - len(failures),
        "results": results,
        "privacy": "Report stores repo-relative ignored decompile filenames, function names, addresses, token labels, and line numbers only; it does not include decompiled source excerpts, binaries, private paths, runtime captures, screenshots, or Ghidra mutation logs.",
        "proves": [
            "Fresh headless Ghidra decompile read-back for nine already named BattleEngine selection and weapon-entry helpers.",
            "Selected entry traversal, current/fallback resolution, selected weapon definition, usability gate, cycle, and cleanup tokens in current decompile output.",
        ],
        "doesNotProve": [
            "Exact Steam retail binary identity for every source weapon-change or selection behavior anchor.",
            "Runtime weapon cycling, firing readiness, selected weapon behavior, or gameplay-state interpretation.",
            "Ghidra rename-map mutation or project write intent.",
            "Rebuildable open-source gameplay implementation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public-safe BattleEngine selection-helper Ghidra read-back evidence.")
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    report = build_report(args.decompile_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine selection-helper Ghidra read-back probe")
        print(f"Output: {relative(out)}")
        print(f"Status: {report['status']}")
        print(f"Functions: {report['functionsPassed']}/{report['functionsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['address']} {item['name']}")

    return 0 if report["status"] == "pass" or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
