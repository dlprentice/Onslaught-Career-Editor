#!/usr/bin/env python3
"""Validate read-only Ghidra decompile read-back for BattleEngine target/profile helpers.

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
    / "battleengine-target-profile-ghidra-readback"
    / "current"
    / "decompile"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-target-profile-ghidra-readback"
    / "current"
    / "battleengine-target-profile-ghidra-readback.json"
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
        "0x0040acc0",
        "CBattleEngine__CalcUnitOverCrossHair",
        ("CBattleEngine__CalcUnitOverCrossHair", "__thiscall"),
        "0040acc0_CBattleEngine__CalcUnitOverCrossHair.c",
        (
            "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
            "CPlayer__GetCurrentViewPoint",
            "CPlayer__GetCurrentViewOrientation",
            "OID__TraceLineAndSelectBestTargetHit",
            "CGenericActiveReader__SetReader((void *)((int)this + 0x4cc)",
            "CEventManager__AddEvent_AtTime",
        ),
        "Fresh headless read-back confirms the named CalcUnitOverCrossHair source bridge and selected view, trace, reader, metric, and event tokens.",
    ),
    FunctionExpectation(
        "0x0040b6d0",
        "CBattleEngine__HandleAutoAim",
        ("CBattleEngine__HandleAutoAim", "__thiscall"),
        "0040b6d0_CBattleEngine__HandleAutoAim.c",
        (
            "CUnit__ComputeMinBallisticTravelDistance",
            "CUnit__ComputeMaxBallisticTravelDistance",
            "CMapWho__GetFirstEntryWithinRadius",
            "CBattleEngine__IsWeaponModeCompatibleWithMountState",
            "CGenericActiveReader__SetReader((void *)((int)this + 0x4e0)",
            "OID__TraceLineAndSelectBestTargetHit",
            "CEventManager__AddEvent_AtTime(&EVENT_MANAGER,0x1773",
        ),
        "Fresh headless read-back confirms the named HandleAutoAim source bridge and selected range, candidate, reader, trace, and event tokens.",
    ),
    FunctionExpectation(
        "0x0040c650",
        "CBattleEngine__ApplyWeaponProfileByIndex",
        ("CBattleEngine__ApplyWeaponProfileByIndex", "__fastcall"),
        "0040c650_CBattleEngine__ApplyWeaponProfileByIndex.c",
        (
            "CBattleEngine__GetWeaponProfileByIndex(*(int *)(param_1 + 0x600))",
            "param_1 + 0x4b0",
            "CBattleEngineJetPart__ResetConfiguration",
            "CBattleEngineWalkerPart__ResetConfiguration",
            "iVar4 = 6",
            "CConsole__Printf(&DAT_0066f580",
        ),
        "Fresh headless read-back confirms the named weapon-profile apply helper and selected profile, reader-reset, slot-loop, and console tokens.",
    ),
    FunctionExpectation(
        "0x0040f2f0",
        "CBattleEngine__GetWeaponProfileByIndex",
        ("CBattleEngine__GetWeaponProfileByIndex", "__cdecl"),
        "0040f2f0_CBattleEngine__GetWeaponProfileByIndex.c",
        (
            "if ((param_1 < 0) || (DAT_00660250 <= param_1))",
            "piVar2 = DAT_006602a0",
            "pbVar6 = (byte *)(&DAT_00660200)[param_1]",
            "_DAT_006602a8 = DAT_006602a0",
            "return iVar5",
        ),
        "Fresh headless read-back confirms the named weapon-profile lookup helper and selected bounds, name-table, traversal, and return tokens.",
    ),
    FunctionExpectation(
        "0x005061f0",
        "CBattleEngine__DoesTargetMaskMatchProfileByDistance",
        ("CBattleEngine__DoesTargetMaskMatchProfileByDistance", "__thiscall"),
        "005061f0_CBattleEngine__DoesTargetMaskMatchProfileByDistance.c",
        (
            "if (*(int *)(param_1 + 0x214) == 0)",
            "*(int *)(param_1 + 0x228) != 0",
            "if (*(int *)(param_1 + 0x22c) != 0)",
            "ROUND(*(float *)((int)this + 0x60))",
            "DAT_008553ec[2] = (int)piVar2",
            "return (*(uint *)(iVar3 + 0xa4) & *(uint *)(param_1 + 0x34)) != 0",
        ),
        "Fresh headless read-back confirms the named target-mask helper and selected profile-gate, distance-bucket, set-walk, and mask tokens.",
    ),
    FunctionExpectation(
        "0x00509c80",
        "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
        ("CBattleEngine__ComputeProjectileMetricFromTargetProfile", "__thiscall"),
        "00509c80_CBattleEngine__ComputeProjectileMetricFromTargetProfile.c",
        (
            "CUnit__ComputeMaxBallisticTravelDistance",
            "ROUND(*(float *)((int)this + 0x60))",
            "pvVar3 = CSPtrSet__First(DAT_008553ec)",
            "pvVar3 = CSPtrSet__Next(DAT_008553ec)",
            "CBattleEngine__GetTargetSetEntryByIndex",
            "return (double)(*(float *)(iVar7 + 0x2c) * *(float *)(iVar7 + 0x24))",
        ),
        "Fresh headless read-back confirms the named projectile metric helper and selected ballistic fallback, target-set, and metric tokens.",
    ),
    FunctionExpectation(
        "0x00509e40",
        "CBattleEngine__GetTargetSetEntryByIndex",
        ("CBattleEngine__GetTargetSetEntryByIndex", "__cdecl"),
        "00509e40_CBattleEngine__GetTargetSetEntryByIndex.c",
        (
            "int __cdecl CBattleEngine__GetTargetSetEntryByIndex(int param_1)",
            "piVar1 = (int *)*DAT_008553ec",
            "DAT_008553ec[2] = (int)piVar1",
            "if (iVar3 == param_1) break",
            "return iVar2",
        ),
        "Fresh headless read-back confirms the named target-set lookup helper and selected list-walk/index tokens.",
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
        "schema": "battleengine-target-profile-ghidra-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not failures else "blocked",
        "decompileDir": relative(decompile_dir),
        "mutation": False,
        "functionsChecked": len(results),
        "functionsPassed": len(results) - len(failures),
        "results": results,
        "privacy": "Report stores repo-relative ignored decompile filenames, function names, addresses, token labels, and line numbers only; it does not include decompiled source excerpts, binaries, private paths, runtime captures, screenshots, or Ghidra mutation logs.",
        "proves": [
            "Fresh headless Ghidra decompile read-back for seven already named BattleEngine target/profile helper functions.",
            "Selected aim-target, ballistic acquisition, profile lookup, target-mask, projectile metric, and target-set lookup tokens in current decompile output.",
        ],
        "doesNotProve": [
            "Exact Steam retail binary identity for every source target-lock or weapon behavior anchor.",
            "Runtime target choice, aim correctness, projectile behavior, lock acquisition, stealth behavior, or gameplay-state interpretation.",
            "Ghidra rename-map mutation or project write intent.",
            "Rebuildable open-source gameplay implementation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public-safe BattleEngine target/profile Ghidra read-back evidence.")
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
        print("BattleEngine target/profile Ghidra read-back probe")
        print(f"Output: {relative(out)}")
        print(f"Status: {report['status']}")
        print(f"Functions: {report['functionsPassed']}/{report['functionsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['address']} {item['name']}")

    return 0 if report["status"] == "pass" or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
