#!/usr/bin/env python3
"""Validate a small read-only Ghidra decompile read-back for BattleEngine.

This probe consumes decompile files exported by ``ExportFunctionsByAddressDecompile.java``.
It does not launch Ghidra by itself, read BEA.exe, mutate the game install, or mutate a
Ghidra project. The output stays under ``subagents/`` and records function names,
addresses, token labels, and line numbers only.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECOMPILE_DIR = ROOT / "subagents" / "battleengine-ghidra-readback" / "current" / "decompile"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-ghidra-readback" / "current" / "battleengine-ghidra-readback.json"


@dataclass(frozen=True)
class FunctionExpectation:
    address: str
    name: str
    signature_tokens: tuple[str, ...]
    file_token: str
    required_tokens: tuple[str, ...]
    source_anchor: str
    identity_note: str


EXPECTATIONS: tuple[FunctionExpectation, ...] = (
    FunctionExpectation(
        "0x0040f590",
        "CBattleEngineData__Initialise",
        ("CBattleEngineData__Initialise",),
        "0040f590_CBattleEngineData__Initialise.c",
        (
            "s_C__dev_ONSLAUGHT2_BattleEngineDa_00623674",
            "s_Vulcan_Cannon_1_00623658",
            "s_Pulse_Cannon_Pod_00623644",
            "s_Missile_Pod_00623638",
            "s_cockpit2_msh_00623608",
            "param_1[8] = 0x40200000",
            "param_1[2] = 0x3e99999a",
            "param_1[0xb] = 0x3f800000",
            "param_1[9] = 0x42b40000",
        ),
        "references/Onslaught/BattleEngineDataManager.cpp",
        "Fresh headless decompile read-back confirms the current BattleEngineData initialise function and selected default/loadout tokens.",
    ),
    FunctionExpectation(
        "0x00404dd0",
        "CBattleEngine__Init",
        ("CBattleEngine__Init", "__thiscall"),
        "00404dd0_CBattleEngine__Init.c",
        (
            "s_C__dev_ONSLAUGHT2_BattleEngine_c_006230bc",
            "CBattleEngine__ApplyWeaponProfileByIndex",
            "CBattleEngine__InitDashMoveParams",
            "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
            "CBattleEngine__HandleAutoAim",
        ),
        "references/Onslaught/BattleEngine.cpp",
        "Fresh headless decompile read-back confirms the named BattleEngine init function and selected ownership/call-chain tokens.",
    ),
    FunctionExpectation(
        "0x004d28a0",
        "CPlayer__Init",
        ("CPlayer__Init", "__fastcall"),
        "004d28a0_CPlayer__Init.c",
        ("CPlayer__GotoFPView",),
        "references/Onslaught/Player.cpp",
        "Fresh headless decompile read-back confirms the named Player init function and first-person-view initialization token.",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def line_hits(lines: list[str], tokens: tuple[str, ...]) -> dict[str, list[int]]:
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def parse_index(index_path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    if not index_path.is_file():
        return rows
    for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        cells = line.split("\t")
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


def summarize_expectation(expectation: FunctionExpectation, decompile_dir: Path, index_rows: dict[tuple[str, str], dict[str, str]]) -> dict[str, object]:
    row = index_rows.get((expectation.address.lower(), expectation.name))
    row_failures: list[str] = []
    if row is None:
        row_failures.append("missing index row")
        row = {"address": expectation.address, "name": expectation.name, "signature": "", "status": "MISSING"}
    if row.get("status") != "OK":
        row_failures.append(f"index status is {row.get('status')}")
    signature_hits = {token: token in row.get("signature", "") for token in expectation.signature_tokens}
    missing_signature_tokens = [token for token, present in signature_hits.items() if not present]

    decompile_path = decompile_dir / expectation.file_token
    decompile_failures: list[str] = []
    token_hits: dict[str, list[int]] = {}
    if not decompile_path.is_file():
        decompile_failures.append("missing decompile file")
    else:
        token_hits = line_hits(read_lines(decompile_path), expectation.required_tokens)
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
        "identityNote": expectation.identity_note,
        "indexStatus": row.get("status"),
        "signatureTokenPresence": signature_hits,
        "missingSignatureTokens": missing_signature_tokens,
        "decompileFile": relative(decompile_path),
        "tokenLineHits": token_hits,
        "rowFailures": row_failures,
        "decompileFailures": decompile_failures,
    }


def build_report(decompile_dir: Path) -> dict[str, object]:
    index_path = decompile_dir / "index.tsv"
    index_rows = parse_index(index_path)
    results = [summarize_expectation(expectation, decompile_dir, index_rows) for expectation in EXPECTATIONS]
    failures = [item for item in results if item["status"] != "PASS"]
    return {
        "schema": "battleengine-ghidra-readback.v1",
        "status": "pass" if not failures else "blocked",
        "decompileDir": relative(decompile_dir),
        "indexFile": relative(index_path),
        "functionsChecked": len(results),
        "functionsPassed": sum(1 for item in results if item["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative ignored decompile filenames, function names, addresses, token labels, and line numbers only; it does not include decompiled source excerpts, binaries, private paths, runtime captures, or Ghidra mutation logs.",
        "proven": [
            "Fresh headless Ghidra decompile read-back for three already named retail functions",
            "Selected BattleEngineData config default/loadout tokens in the current decompile output",
            "Selected BattleEngine and Player ownership/call-chain tokens in the current decompile output",
        ],
        "notProven": [
            "Steam retail binary identity for every BattleEngine gameplay source anchor",
            "Runtime gameplay-state interpretation",
            "Ghidra rename-map mutation",
            "Rebuildable open-source gameplay implementation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public-safe BattleEngine Ghidra decompile read-back evidence.")
    parser.add_argument("--check", action="store_true", help="run the read-back probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR, help="ignored decompile export directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    decompile_dir = args.decompile_dir if args.decompile_dir.is_absolute() else ROOT / args.decompile_dir
    out = args.out if args.out.is_absolute() else ROOT / args.out
    for candidate in (decompile_dir, out.parent):
        try:
            candidate.resolve().relative_to((ROOT / "subagents").resolve())
        except ValueError:
            print(f"Refusing to read/write outside subagents/: {candidate}")
            return 1

    report = build_report(decompile_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine Ghidra read-back probe")
        print(f"Status: {report['status']}")
        print(f"Functions: {report['functionsPassed']}/{report['functionsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['address']} {item['name']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
