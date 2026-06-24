#!/usr/bin/env python3
"""Validate read-only Ghidra decompile read-back for BattleEngine weapon helpers.

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
    / "battleengine-weapon-helper-ghidra-readback"
    / "current"
    / "decompile"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-weapon-helper-ghidra-readback"
    / "current"
    / "battleengine-weapon-helper-ghidra-readback.json"
)


@dataclass(frozen=True)
class FunctionExpectation:
    address: str
    name: str
    signature_tokens: tuple[str, ...]
    file_name: str
    required_tokens: tuple[str, ...]
    source_anchor: str
    note: str


EXPECTATIONS: tuple[FunctionExpectation, ...] = (
    FunctionExpectation(
        "0x004063b0",
        "CBattleEngine__UpdateWeaponEffect",
        ("CBattleEngine__UpdateWeaponEffect",),
        "004063b0_CBattleEngine__UpdateWeaponEffect.c",
        (
            "void __fastcall CBattleEngine__UpdateWeaponEffect",
            "(**(code **)(*param_1 + 0x40))()",
            "OID__AllocObject(0x20",
            "(**(code **)(*param_1 + 0xc0))()",
            "puVar2[5] = fVar1",
            "puVar2[6] = fVar1 * fVar1",
            "puVar2[7] = (float)(fVar5 * fVar4)",
            "(**(code **)(*(int *)param_1[0xe] + 0x24))(puVar3)",
        ),
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__UpdateWeaponEffect.md",
        "Fresh headless decompile read-back confirms the named weapon-effect helper and selected allocation/life/gravity/container tokens.",
    ),
    FunctionExpectation(
        "0x00406fc0",
        "CBattleEngine__AddProjectile",
        ("CBattleEngine__AddProjectile",),
        "00406fc0_CBattleEngine__AddProjectile.c",
        (
            "CBattleEngine__AddProjectile(int param_1,void *param_2,float param_3,undefined4 param_4)",
            "(*(byte *)((int)param_2 + 0x2c) & 4) == 0",
            "param_1 + 0x294",
            "param_1 + 0x29c",
            "OID__AllocObject(0x14",
            "CGenericActiveReader__SetReader(puVar4,param_2)",
            "DAT_00672fd0",
            "puVar4[4] = param_4",
            "puVar4[2] = fVar1 + param_3",
            "CSPtrSet__AddToTail((void *)(param_1 + 0x294),puVar4)",
        ),
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__AddProjectile.md",
        "Fresh headless decompile read-back confirms the named projectile helper and selected disabled-flag/list/duration/tail-add tokens.",
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
        "sourceAnchor": expectation.source_anchor,
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
        "schema": "battleengine-weapon-helper-ghidra-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not failures else "blocked",
        "decompileDir": relative(decompile_dir),
        "mutation": False,
        "functionsChecked": len(results),
        "functionsPassed": len(results) - len(failures),
        "results": results,
        "privacy": "Report stores repo-relative ignored decompile filenames, function names, addresses, token labels, and line numbers only; it does not include decompiled source excerpts, binaries, private paths, runtime captures, screenshots, or Ghidra mutation logs.",
        "proves": [
            "Fresh headless Ghidra decompile read-back for two already named BattleEngine weapon helper functions.",
            "Selected weapon-effect allocation/life/gravity/container tokens in the current decompile output.",
            "Selected projectile disabled-flag/list/duration/tail-add tokens in the current decompile output.",
        ],
        "doesNotProve": [
            "Exact Steam retail binary identity for every source weapon, augmented-weapon, or stealth anchor.",
            "Runtime weapon firing, projectile behavior, lock behavior, stealth reset, or augmented-weapon behavior.",
            "Ghidra rename-map mutation or project write intent.",
            "Rebuildable open-source gameplay implementation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public-safe BattleEngine weapon helper Ghidra read-back evidence.")
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
        print("BattleEngine weapon helper Ghidra read-back probe")
        print(f"Output: {relative(out)}")
        print(f"Status: {report['status']}")
        print(f"Functions: {report['functionsPassed']}/{report['functionsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['address']} {item['name']}")

    return 0 if report["status"] == "pass" or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
