#!/usr/bin/env python3
"""Public-safe config-defaults support probe for BattleEngine docs.

This read-only probe checks one narrow source-to-binary bridge: the source
default configuration values and the existing binary documentation for
``CBattleEngineData__Initialise`` both carry the expected value tokens. It does
not read BEA.exe, launch the game, or mutate Ghidra.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "references" / "Onslaught" / "BattleEngineDataManager.cpp"
BINARY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineDataManager.cpp" / "_index.md"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-config-defaults-binary-doc" / "current" / "battleengine-config-defaults-binary-doc.json"


@dataclass(frozen=True)
class ValueAnchor:
    key: str
    source_tokens: tuple[str, ...]
    binary_tokens: tuple[str, ...]
    note: str


ANCHORS: tuple[ValueAnchor, ...] = (
    ValueAnchor(
        "energy_default",
        ("mEnergy=2.5f",),
        ("0x40200000", "2.5f"),
        "Source energy default and binary-doc float token are both present.",
    ),
    ValueAnchor(
        "max_air_energy_cost_default",
        ("mMaxAirEnergyCost=0.3f",),
        ("0x3e99999a", "0.3f"),
        "Source max air-energy cost default and binary-doc float token are both present.",
    ),
    ValueAnchor(
        "min_transform_energy_default",
        ("mMinTransformEnergy=1.0f",),
        ("0x3f800000", "1.0f"),
        "Source minimum-transform-energy default and binary-doc float token are both present.",
    ),
    ValueAnchor(
        "shield_efficiency_default",
        ("mShieldEfficiency=90.0f",),
        ("0x42b40000", "90.0f"),
        "Source shield-efficiency default and binary-doc float token are both present.",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def text_for(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def line_hits(text: str, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    lines = text.splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def summarize_anchor(anchor: ValueAnchor, source_text: str, binary_text: str) -> dict[str, object]:
    source_hits = line_hits(source_text, anchor.source_tokens)
    binary_hits = line_hits(binary_text, anchor.binary_tokens)
    missing_source = [token for token, hits in source_hits.items() if not hits]
    missing_binary = [token for token, hits in binary_hits.items() if not hits]
    status = "PASS" if not missing_source and not missing_binary else "FAIL"
    return {
        "key": anchor.key,
        "status": status,
        "sourceFile": relative(SOURCE_FILE),
        "binaryDoc": relative(BINARY_DOC),
        "sourceTokens": list(anchor.source_tokens),
        "binaryTokens": list(anchor.binary_tokens),
        "sourceLineHits": source_hits,
        "binaryDocLineHits": binary_hits,
        "missingSourceTokens": missing_source,
        "missingBinaryDocTokens": missing_binary,
        "note": anchor.note,
    }


def build_report() -> dict[str, object]:
    source_text = text_for(SOURCE_FILE) if SOURCE_FILE.is_file() else ""
    binary_text = text_for(BINARY_DOC) if BINARY_DOC.is_file() else ""
    results = [summarize_anchor(anchor, source_text, binary_text) for anchor in ANCHORS]
    if not SOURCE_FILE.is_file():
        results.append(
            {
                "key": "source_file_exists",
                "status": "FAIL",
                "sourceFile": relative(SOURCE_FILE),
                "missing": True,
            }
        )
    if not BINARY_DOC.is_file():
        results.append(
            {
                "key": "binary_doc_exists",
                "status": "FAIL",
                "binaryDoc": relative(BINARY_DOC),
                "missing": True,
            }
        )
    failures = [item for item in results if item["status"] != "PASS"]
    return {
        "schema": "battleengine-config-defaults-binary-doc.v1",
        "status": "pass" if not failures else "blocked",
        "sourceFile": relative(SOURCE_FILE),
        "binaryDoc": relative(BINARY_DOC),
        "anchorsChecked": len(ANCHORS),
        "anchorsPassed": sum(1 for item in results if item["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative source/doc filenames, token names, and line numbers only; no source excerpts, binaries, private paths, runtime captures, or Ghidra mutation logs.",
        "notProven": [
            "Exact Steam retail function body identity for each source default field",
            "Fresh Ghidra decompile/read-back for these constants",
            "Runtime gameplay-state interpretation",
            "Rebuildable implementation parity",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BattleEngine config defaults against existing binary docs.")
    parser.add_argument("--check", action="store_true", help="run the config-defaults support probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1
    report = build_report()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine config defaults binary-doc probe")
        print(f"Status: {report['status']}")
        print(f"Anchors: {report['anchorsPassed']}/{report['anchorsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['key']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
