#!/usr/bin/env python3
"""Validate read-only Ghidra decompile read-back for BattleEngine helper functions.

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
DEFAULT_DECOMPILE_DIR = ROOT / "subagents" / "battleengine-helper-ghidra-readback" / "current" / "decompile"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-helper-ghidra-readback" / "current" / "battleengine-helper-ghidra-readback.json"


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
        "0x00406460",
        "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
        ("CBattleEngine__SwapPrimarySecondaryPartReadersForState", "__fastcall"),
        "00406460_CBattleEngine__SwapPrimarySecondaryPartReadersForState.c",
        (
            "param_1 + 0x260",
            "param_1 + 0x5f0",
            "param_1 + 0x5ec",
            "CMCMech__Reset",
            "CInfluenceMap__SetTrackedThingAndClearCachedObject",
        ),
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/_index.md",
        "Fresh headless decompile read-back confirms the named state-gated reader swap helper and selected transform/reader tokens.",
    ),
    FunctionExpectation(
        "0x00406560",
        "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
        ("CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "__fastcall"),
        "00406560_CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.c",
        (
            "CBattleEngine__GetIndexedEntry",
            "CBattleEngine__IsIndexedEntryUsable",
            "CGeneralVolume__ResolveCurrentOrFallbackEntry",
            "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
            "CBattleEngine__AddProjectile",
            "CSPtrSet__Remove",
        ),
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/_index.md",
        "Fresh headless decompile read-back confirms the named auto-target/projectile helper and selected target/fire call-chain tokens.",
    ),
    FunctionExpectation(
        "0x00406da0",
        "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
        ("CBattleEngine__SelectNearestForwardTargetFromGlobalSet",),
        "00406da0_CBattleEngine__SelectNearestForwardTargetFromGlobalSet.c",
        (
            "CBattleEngine__IsWeaponModeCompatibleWithMountState",
            "CBattleEngine__DoesTargetMaskMatchProfileByDistance",
            "CBattleEngine__GetProfileField98ByDistance",
            "CSPtrSet__First",
            "CSPtrSet__Next",
        ),
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/_index.md",
        "Fresh headless decompile read-back confirms the named forward-target selection helper and selected profile/list traversal tokens.",
    ),
    FunctionExpectation(
        "0x00407310",
        "CBattleEngine__IsCurrentResolvedEntry",
        ("CBattleEngine__IsCurrentResolvedEntry", "__thiscall"),
        "00407310_CBattleEngine__IsCurrentResolvedEntry.c",
        (
            "CBattleEngine__GetIndexedEntry",
            "CGeneralVolume__ResolveCurrentOrFallbackEntry",
        ),
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/_index.md",
        "Fresh headless decompile read-back confirms the named current/resolved-entry comparator and selected entry-resolution tokens.",
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
        "schema": "battleengine-helper-ghidra-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "decompileDir": relative(decompile_dir),
        "mutation": False,
        "functionsChecked": len(results),
        "functionsPassed": sum(1 for item in results if item["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative ignored decompile filenames, function names, addresses, token labels, and line numbers only; it does not include decompiled source excerpts, binaries, private paths, runtime captures, or Ghidra mutation logs.",
        "proves": [
            "Fresh headless Ghidra decompile read-back for four already named BattleEngine helper functions",
            "Selected transform-state, reader-swap, target-selection, and projectile call-chain tokens in the current decompile output",
        ],
        "doesNotProve": [
            "Exact Steam retail identity for every BattleEngine source mechanic",
            "Runtime gameplay-state interpretation",
            "Ghidra rename-map mutation",
            "Rebuildable open-source gameplay implementation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public-safe BattleEngine helper Ghidra read-back evidence.")
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
        print("BattleEngine helper Ghidra read-back probe")
        print(f"Output: {relative(args.out)}")
        print(f"Functions: {report['functionsPassed']}/{report['functionsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['address']} {item['name']}")

    return 0 if not args.check or report["functionsPassed"] == report["functionsChecked"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
