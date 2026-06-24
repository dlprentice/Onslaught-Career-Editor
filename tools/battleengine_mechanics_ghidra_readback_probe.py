#!/usr/bin/env python3
"""Validate read-only Ghidra decompile read-back for Unit/Mech mechanics functions.

This probe consumes decompile files exported by ExportFunctionsByAddressDecompile.java.
It does not launch the game, read BEA.exe directly, mutate BEA.exe, or mutate a Ghidra
project. Output stays under subagents/ and records function names, addresses, token
labels, and line numbers only.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECOMPILE_DIR = ROOT / "subagents" / "battleengine-mechanics-ghidra-readback" / "current" / "decompile"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-mechanics-ghidra-readback" / "current" / "battleengine-mechanics-ghidra-readback.json"


@dataclass(frozen=True)
class FunctionExpectation:
    address: str
    name: str
    signature_tokens: tuple[str, ...]
    file_token: str
    required_tokens: tuple[str, ...]
    source_anchor: str
    note: str


EXPECTATIONS: tuple[FunctionExpectation, ...] = (
    FunctionExpectation(
        "0x004f9a90",
        "CUnit__ApplyDamage",
        ("CUnit__ApplyDamage", "__thiscall", "damageAmount"),
        "004f9a90_CUnit__ApplyDamage.c",
        (
            "CUnit__ResetDamageCooldownTimer",
            "CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold",
            "CParticleManager__CreateEffect",
            "s_weakpoint_00633ae8",
            "s_nexus_00633af4",
        ),
        "reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__ApplyDamage.md",
        "Fresh headless decompile read-back confirms the named Unit damage handler and selected shield/segment/effect/name tokens.",
    ),
    FunctionExpectation(
        "0x004f86d0",
        "CUnit__Init",
        ("CUnit__Init", "__thiscall"),
        "004f86d0_CUnit__Init.c",
        (
            "CWorldPhysicsManager__CreateWeaponByIndex",
            "CSPtrSet__AddToTail",
            "CWorldPhysicsManager__CreateSpawner",
            "CWorldPhysicsManager__CreateCharacter",
            "CGenericActiveReader__SetReader",
            "s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c",
        ),
        "reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__Init.md",
        "Fresh headless decompile read-back confirms the named Unit initialization function and selected weapon/spawner/character setup tokens.",
    ),
    FunctionExpectation(
        "0x004fc4e0",
        "CUnit__UpdateTransform",
        ("CUnit__UpdateTransform",),
        "004fc4e0_CUnit__UpdateTransform.c",
        (
            "CUnit__FindEmitterIndexBySlotTag",
            "CMCBuggy__MultiplyMat34Basis",
            "s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c",
        ),
        "reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__UpdateTransform.md",
        "Fresh headless decompile read-back confirms the named Unit transform function and selected transform/emitter/source ownership tokens.",
    ),
    FunctionExpectation(
        "0x0049fa30",
        "CMech__InitCockpit",
        ("CMech__InitCockpit",),
        "0049fa30_CMech__InitCockpit.c",
        (
            "OID__AllocObject(100",
            "CMechAI__ctor_like_004a02e0",
            "s_C__dev_ONSLAUGHT2_Mech_cpp_0062e0e0",
        ),
        "reverse-engineering/binary-analysis/functions/Mech.cpp/_index.md",
        "Fresh headless decompile read-back confirms the named Mech cockpit setup function and selected object-allocation tokens.",
    ),
    FunctionExpectation(
        "0x0049faa0",
        "CMech__InitTargeting",
        ("CMech__InitTargeting",),
        "0049faa0_CMech__InitTargeting.c",
        (
            "OID__AllocObject(0x48",
            "CMechGuide__ctor_like_004a0a20",
            "s_C__dev_ONSLAUGHT2_Mech_cpp_0062e0e0",
        ),
        "reverse-engineering/binary-analysis/functions/Mech.cpp/_index.md",
        "Fresh headless decompile read-back confirms the named Mech targeting setup function and selected object-allocation tokens.",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
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


def summarize(expectation: FunctionExpectation, decompile_dir: Path, index_rows: dict[tuple[str, str], dict[str, str]]) -> dict[str, object]:
    row = index_rows.get((expectation.address.lower(), expectation.name))
    row_failures: list[str] = []
    if row is None:
        row = {"address": expectation.address, "name": expectation.name, "signature": "", "status": "MISSING"}
        row_failures.append("function row missing from index.tsv")
    elif row.get("status") != "OK":
        row_failures.append(f"index.tsv status is {row.get('status')}")

    signature_hits = {token: token in row.get("signature", "") for token in expectation.signature_tokens}
    missing_signature_tokens = [token for token, present in signature_hits.items() if not present]

    decompile_path = decompile_dir / expectation.file_token
    token_hits: dict[str, list[int]] = {}
    decompile_failures: list[str] = []
    if not decompile_path.is_file():
        decompile_failures.append(f"missing decompile file: {expectation.file_token}")
    else:
        token_hits = token_line_hits(read_lines(decompile_path), expectation.required_tokens)
        decompile_failures.extend(
            f"missing token: {token}"
            for token, hits in token_hits.items()
            if not hits
        )

    status = "PASS" if not row_failures and not missing_signature_tokens and not decompile_failures else "FAIL"
    return {
        "address": expectation.address,
        "name": expectation.name,
        "status": status,
        "sourceAnchor": expectation.source_anchor,
        "note": expectation.note,
        "indexStatus": row.get("status"),
        "signatureTokenPresence": signature_hits,
        "missingSignatureTokens": missing_signature_tokens,
        "decompileFile": relative(decompile_path),
        "tokenLineHits": token_hits,
        "failures": row_failures + decompile_failures,
    }


def build_report(decompile_dir: Path) -> dict[str, object]:
    index_rows = parse_index(decompile_dir / "index.tsv")
    results = [summarize(expectation, decompile_dir, index_rows) for expectation in EXPECTATIONS]
    return {
        "schema": "battleengine-mechanics-ghidra-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "decompileDir": relative(decompile_dir),
        "mutation": False,
        "functionsChecked": len(results),
        "functionsPassed": sum(1 for item in results if item["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative ignored decompile filenames, function names, addresses, token labels, and line numbers only; it does not include decompiled source excerpts, binaries, private paths, runtime captures, or Ghidra mutation logs.",
        "proves": [
            "Fresh headless Ghidra decompile read-back for five already named Unit/Mech mechanics-adjacent retail functions",
            "Selected damage, unit initialization, transform, cockpit, and targeting tokens in the current decompile output",
        ],
        "doesNotProve": [
            "Exact Steam retail identity for every BattleEngine source mechanic",
            "Runtime gameplay-state interpretation",
            "Ghidra rename-map mutation",
            "Rebuildable open-source gameplay implementation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public-safe Unit/Mech Ghidra mechanics read-back evidence.")
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(args.decompile_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine mechanics Ghidra read-back probe")
        print(f"Output: {relative(args.out)}")
        print(f"Functions: {report['functionsPassed']}/{report['functionsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['address']} {item['name']}")

    return 0 if not args.check or report["functionsPassed"] == report["functionsChecked"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
