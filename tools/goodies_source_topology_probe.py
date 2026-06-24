#!/usr/bin/env python3
"""Map source-level Goodies topology around hidden/non-grid rows.

This probe reads Stuart's source tree only. It does not launch the game, read or
write BEA.exe, mutate Ghidra, patch saves, or touch runtime artifacts.

The goal is narrower than the source access probe: record whether Goodies 71-73
are present in data/resource helper topology while still absent from the normal
frontend coordinate mapper.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "references" / "Onslaught"
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-source-topology"
    / "current"
    / "goodies-source-topology.json"
)

TARGET_GOODIES = (71, 72, 73)
EXPECTED_GOODIE_SOURCE_FILES = {
    "references/Onslaught/Career.cpp",
    "references/Onslaught/Career.h",
    "references/Onslaught/CLIParams.cpp",
    "references/Onslaught/CLIParams.h",
    "references/Onslaught/FEPGoodies.cpp",
    "references/Onslaught/FEPGoodies.h",
    "references/Onslaught/FEPSaveGame.cpp",
    "references/Onslaught/FrontEnd.cpp",
    "references/Onslaught/Frontend.h",
    "references/Onslaught/game.cpp",
    "references/Onslaught/ResourceAccumulator.cpp",
}


@dataclass(frozen=True)
class SourceHit:
    path: Path
    line: int
    text: str

    def to_json(self) -> dict[str, object]:
        return {
            "file": relative(self.path),
            "line": self.line,
            "text": self.text,
        }


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def iter_source_files(source_root: Path) -> list[Path]:
    extensions = {".c", ".cpp", ".h", ".hpp", ".inl", ".txt"}
    files: list[Path] = []
    for path in source_root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file() and path.suffix.lower() in extensions:
            files.append(path)
    return sorted(files)


def line_hits(path: Path, pattern: re.Pattern[str]) -> list[SourceHit]:
    hits: list[SourceHit] = []
    for index, line in enumerate(read_text(path).splitlines(), start=1):
        if pattern.search(line):
            hits.append(SourceHit(path, index, line.strip()))
    return hits


def collect_hits(paths: list[Path], pattern: re.Pattern[str]) -> list[SourceHit]:
    hits: list[SourceHit] = []
    for path in paths:
        hits.extend(line_hits(path, pattern))
    return hits


def function_slice(text: str, marker: str) -> str:
    start = text.find(marker)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return text[start:]


def target_case_hits(path: Path, function_name: str) -> dict[str, object]:
    text = read_text(path)
    body = function_slice(text, function_name)
    case_hits: dict[str, bool] = {}
    for goodie in TARGET_GOODIES:
        case_hits[str(goodie)] = bool(re.search(rf"\bcase\s+{goodie}\s*:", body))
    return {
        "function": function_name,
        "hasFunctionBody": bool(body),
        "targetCases": case_hits,
    }


def build_report(source_root: Path) -> dict[str, object]:
    failures: list[str] = []
    all_source_files = iter_source_files(source_root)
    goodie_token_pattern = re.compile(r"goodie", re.IGNORECASE)
    goodie_hits = collect_hits(all_source_files, goodie_token_pattern)
    goodie_source_files = sorted({relative(hit.path) for hit in goodie_hits})

    fep = source_root / "FEPGoodies.cpp"
    career = source_root / "Career.cpp"
    fepsave = source_root / "FEPSaveGame.cpp"

    for required in (fep, career, fepsave):
        if not required.is_file():
            failures.append(f"missing source file: {relative(required)}")

    all_paths = all_source_files
    target_number_group = "|".join(str(value) for value in TARGET_GOODIES)
    direct_state_hits = collect_hits(
        all_paths,
        re.compile(
            rf"\b(?:CAREER\.)?(?:GetGoodieState|SetGoodieState)\s*\(\s*(?:{target_number_group})\b"
        ),
    )
    direct_array_hits = collect_hits(
        all_paths,
        re.compile(rf"\bmGoodies\s*\[\s*(?:{target_number_group})\s*\]"),
    )

    fep_text = read_text(fep) if fep.is_file() else ""
    career_text = read_text(career) if career.is_file() else ""
    fepsave_text = read_text(fepsave) if fepsave.is_file() else ""
    mapper_body = function_slice(fep_text, "static SINT get_goodie_number")

    mapper_direct_returns = {
        str(goodie): bool(re.search(rf"return\s*\(\s*{goodie}\s*\)", mapper_body))
        for goodie in TARGET_GOODIES
    }
    data_table_entries = {
        str(goodie): bool(re.search(rf"\bCGoodieData\s*\(\s*GOODIES_{goodie}\b", fep_text))
        for goodie in TARGET_GOODIES
    }
    career_unlock_entries = {
        str(goodie): bool(re.search(rf"\bSET_GOODIE_NEW\s*\(\s*{goodie}\s*\)", career_text))
        for goodie in TARGET_GOODIES
    }
    career_instruction_entries = {
        str(goodie): bool(
            re.search(rf"\bSET_GOODIE_INSTRUCTION\s*\(\s*{goodie}\s*\)", career_text)
        )
        for goodie in TARGET_GOODIES
    }

    texture_topology = target_case_hits(fep, "static CTEXTURE *get_goodie_texture_hack")
    mesh_topology = target_case_hits(fep, "static CMESH *get_goodie_mesh_hack")
    background_topology = target_case_hits(
        fep, "static CTEXTURE *get_goodie_background_hack"
    )

    selection_loader_tokens = {
        "StartLoadingGoodyUsesMapper": "int goodie_number = get_goodie_number(mCX, mCY);"
        in fep_text,
        "StartLoadingGoodyLoadsResourceByMappedNumber": "-1000 - goodie_number" in fep_text,
        "LoadingGoodyPollUsesMapper": "CResourceAccumulator::ReadResources(-1000 - goodie_number"
        in fep_text,
    }
    cheat_override_tokens = {
        "SaveNameCheatStringPresent": "105770Y2" in fepsave_text,
        "GoodiesPageChecksUnlockAllCheat": "IsCheatActive(0)" in fep_text,
        "CheatSetsDisplayStateOld": "if (ischeatactive)\n\t\treturn(GS_OLD);" in fep_text
        or "if (ischeatactive)\r\n\t\treturn(GS_OLD);" in fep_text,
        "CheatStillUsesCoordinateMapper": "static EGoodieState\tget_goodie_state" in fep_text
        and "int num=get_goodie_number(x, y);" in fep_text,
    }

    unexpected_goodie_source_files = sorted(
        set(goodie_source_files) - EXPECTED_GOODIE_SOURCE_FILES
    )
    missing_expected_goodie_source_files = sorted(
        EXPECTED_GOODIE_SOURCE_FILES - set(goodie_source_files)
    )

    if unexpected_goodie_source_files:
        failures.append("unexpected Goodies source files found")
    if missing_expected_goodie_source_files:
        failures.append("expected Goodies source files are missing")
    if direct_state_hits:
        failures.append("direct source Goodie API calls target 71-73")
    if direct_array_hits:
        failures.append("direct source mGoodies[71..73] array hits were found")
    if any(mapper_direct_returns.values()):
        failures.append("frontend coordinate mapper directly returns 71-73")
    if not all(data_table_entries.values()):
        failures.append("FEPGoodies data table no longer contains all 71-73 entries")
    if not all(career_unlock_entries.values()):
        failures.append("Career unlock logic no longer contains all 71-73 entries")
    if not all(career_instruction_entries.values()):
        failures.append("Career instruction logic no longer contains all 71-73 entries")
    if not all(texture_topology["targetCases"].values()):
        failures.append("texture helper no longer contains all 71-73 cases")
    if any(mesh_topology["targetCases"].values()):
        failures.append("mesh helper unexpectedly contains 71-73 cases")
    if not all(selection_loader_tokens.values()):
        failures.append("selected Goodie load path no longer proves mapper-based loading")
    if not all(cheat_override_tokens.values()):
        failures.append("unlock-all cheat topology tokens changed")

    return {
        "schema": "goodies-source-topology.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "sourceRoot": relative(source_root),
        "sourceFileCount": len(all_source_files),
        "goodieTokenLineCount": len(goodie_hits),
        "goodieSourceFiles": goodie_source_files,
        "unexpectedGoodieSourceFiles": unexpected_goodie_source_files,
        "missingExpectedGoodieSourceFiles": missing_expected_goodie_source_files,
        "directStateTargetHits": [hit.to_json() for hit in direct_state_hits],
        "directArrayTargetHits": [hit.to_json() for hit in direct_array_hits],
        "mapperDirectReturns": mapper_direct_returns,
        "dataTableEntries": data_table_entries,
        "careerUnlockEntries": career_unlock_entries,
        "careerInstructionEntries": career_instruction_entries,
        "textureTopology": texture_topology,
        "meshTopology": mesh_topology,
        "backgroundTopology": background_topology,
        "selectionLoaderTokens": selection_loader_tokens,
        "cheatOverrideTokens": cheat_override_tokens,
        "currentClaims": [
            "Source topology contains data-table, texture-helper, unlock, and instruction support for Goodies 71-73.",
            "The normal selected-load path still derives the Goodie number from get_goodie_number(mCX, mCY).",
            "The unlock-all save-name cheat is a display-state override after coordinate mapping, not proof that skipped indices have visible wall coordinates.",
            "No source-level direct GetGoodieState/SetGoodieState or mGoodies[71..73] access path was found outside the known unlock/instruction topology.",
        ],
        "notClaimed": [
            "This probe does not prove Steam retail runtime behavior.",
            "This probe does not inspect packed/runtime script divergence.",
            "This probe does not rule out indirect binary-only or developer/debug direct-selection paths.",
            "This probe does not launch BEA.exe or mutate any executable, save, or Ghidra project.",
        ],
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the source topology no longer matches current expectations.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.source_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "source topology: "
        f"goodieFiles={len(report['goodieSourceFiles'])} "
        f"directState71to73={len(report['directStateTargetHits'])} "
        f"directArray71to73={len(report['directArrayTargetHits'])} "
        f"mapperReturns71to73={sum(report['mapperDirectReturns'].values())}"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
