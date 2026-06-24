#!/usr/bin/env python3
"""Validate read-only Ghidra decompile read-back for transition/HUD helper functions.

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
DEFAULT_DECOMPILE_DIR = ROOT / "subagents" / "transition-hud-helper-ghidra-readback" / "current" / "decompile"
DEFAULT_OUT = ROOT / "subagents" / "transition-hud-helper-ghidra-readback" / "current" / "transition-hud-helper-ghidra-readback.json"


@dataclass(frozen=True)
class FunctionExpectation:
    address: str
    name: str
    signature_tokens: tuple[str, ...]
    file_token: str
    required_tokens: tuple[str, ...]
    note: str


EXPECTATIONS: tuple[FunctionExpectation, ...] = (
    FunctionExpectation(
        "0x00424920",
        "CGeneralVolume__BeginFlyToWalkTransition",
        ("CGeneralVolume__BeginFlyToWalkTransition", "__fastcall"),
        "00424920_CGeneralVolume__BeginFlyToWalkTransition.c",
        (
            "s_flytowalk_006234bc",
            "FindAnimationIndex",
            "(int)this + 0x11c",
            "(int)this + 0x114) = 1",
        ),
        "Fresh read-back confirms the named fly-to-walk transition helper and selected animation-state tokens.",
    ),
    FunctionExpectation(
        "0x00424990",
        "CGeneralVolume__BeginWalkToFlyTransition",
        ("CGeneralVolume__BeginWalkToFlyTransition", "__fastcall"),
        "00424990_CGeneralVolume__BeginWalkToFlyTransition.c",
        (
            "s_walktofly_006234b0",
            "FindAnimationIndex",
            "(int)this + 0x11c",
            "(int)this + 0x114) = 2",
        ),
        "Fresh read-back confirms the named walk-to-fly transition helper and selected animation-state tokens.",
    ),
    FunctionExpectation(
        "0x0040eeb0",
        "CBattleEngine__FinishedPlayingCurrentAnimation",
        ("CBattleEngine__FinishedPlayingCurrentAnimation", "__thiscall"),
        "0040eeb0_CBattleEngine__FinishedPlayingCurrentAnimation.c",
        (
            "s_flytowalk_006234bc",
            "s_walktofly_006234b0",
            "FindAnimationIndex",
            "SharedUnitAnimation__PlayAnimationByNameIfPresent",
        ),
        "Fresh read-back confirms the named BattleEngine current-animation completion helper checks both transition animation strings.",
    ),
    FunctionExpectation(
        "0x0040a580",
        "CBattleEngine__Morph",
        ("CBattleEngine__Morph", "__fastcall"),
        "0040a580_CBattleEngine__Morph.c",
        (
            "CGeneralVolume__BeginFlyToWalkTransition",
            "CGeneralVolume__BeginWalkToFlyTransition",
            "SharedUnitAnimation__PlayAnimationByNameIfPresent",
            "s_flytowalk_006234bc",
            "s_walktofly_006234b0",
            "EVENT_MANAGER",
            "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
        ),
        "Fresh read-back confirms the named BattleEngine morph helper calls both transition helpers and animation strings.",
    ),
    FunctionExpectation(
        "0x004081c0",
        "CMonitor__Process",
        ("CMonitor__Process", "__fastcall"),
        "004081c0_CMonitor__Process.c",
        (
            "CBattleEngine__Morph",
            "s_hud__s_00623314",
            "CMonitor__PlayRandomSampleFromChain",
            "CMonitor__UpdateMovementTransitionAndEffects",
            "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
        ),
        "Fresh read-back confirms the named monitor process body calls the morph helper and selected HUD/sound/movement helpers.",
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
        "schema": "transition-hud-helper-ghidra-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "decompileDir": relative(decompile_dir),
        "mutation": False,
        "functionsChecked": len(results),
        "functionsPassed": sum(1 for item in results if item["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative ignored decompile filenames, function names, addresses, token labels, and line numbers only; it does not include decompiled source excerpts, binaries, private paths, runtime captures, or Ghidra mutation logs.",
        "proves": [
            "Fresh headless Ghidra decompile read-back for five transition/HUD helper functions reached from transform/HUD string xrefs",
            "Selected transition animation, BattleEngine morph, HUD-format, sound, and movement-helper tokens in the current decompile output",
        ],
        "doesNotProve": [
            "Exact source-to-retail identity for source CBattleEngine::Morph / the transform-morph flow",
            "Runtime transform or HUD-warning behavior",
            "Ghidra rename-map mutation",
            "Rebuildable open-source gameplay implementation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public-safe transition/HUD helper Ghidra read-back evidence.")
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
        print("Transition/HUD helper Ghidra read-back probe")
        print(f"Output: {relative(args.out)}")
        print(f"Functions: {report['functionsPassed']}/{report['functionsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['address']} {item['name']}")

    return 0 if not args.check or report["functionsPassed"] == report["functionsChecked"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
