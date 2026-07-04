#!/usr/bin/env python3
"""Validate the MissionScript Level100 tutorial text/speaker resolution proof."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

LEVEL_DIR = ROOT / "game" / "data" / "MissionScripts" / "level100"
SHARED_TEXT_DIR = ROOT / "game" / "data" / "MissionScripts" / "text"

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_text_speaker_resolution_proof_plan_2026-06-08.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"

MSL_DOC = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
LORE_MSL_DOC = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MISSION_INDEX = ROOT / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
LORE_MISSION_INDEX = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
MISSION_EVENTS = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
LORE_MISSION_EVENTS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-events-index.md"
MISSION_MESSAGES = ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
LORE_MISSION_MESSAGES = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
MISSION_MESSAGE_CALLSITES = ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage-callsites-1.md"
LORE_MISSION_MESSAGE_CALLSITES = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-message-usage-callsites-1.md"
MISSION_SPEAKERS = ROOT / "reverse-engineering" / "game-assets" / "mission-speaker-index.md"
LORE_MISSION_SPEAKERS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-speaker-index.md"
MISSION_TEXT = ROOT / "reverse-engineering" / "game-assets" / "mission-text-index.md"
LORE_MISSION_TEXT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-text-index.md"

MISSIONSCRIPT_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
LORE_MISSIONSCRIPT_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
MISSIONSCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_MISSIONSCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PACKED_LOOSE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
LORE_PACKED_LOOSE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
EVENT_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"
LORE_EVENT_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"
WALKTHROUGH_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
LORE_WALKTHROUGH_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"

PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
PROOF_LINK = "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
SCHEMA_LINK = "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
WALKTHROUGH_LINK = "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
NEXT_SLICE = "MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan"
BOUNDARY_SLICE = "Completed MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan"
BOUNDARY_PROOF_LINK = "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md"
BOUNDARY_SCHEMA_LINK = "missionscript-level100-tutorial-runtime-harness-boundary.v1.json"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan"

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime text/audio behavior proven",
    "runtime message display proven",
    "runtime voice/audio playback proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "speaker portrait behavior proven",
    "runtime localized text selection proven",
    "visual qa complete",
    "godot parity proven",
    "bea patching behavior proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def strip_line_comment(line: str) -> str:
    return line.split("//", 1)[0]


def parse_token_blocks(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    tokens: dict[str, str] = {}
    for match in re.finditer(r"^\[([^\]]+)\](?:\s*//\s*(.*))?\s*$", read_text(path), re.MULTILINE):
        tokens[match.group(1)] = (match.group(2) or "").strip()
    return tokens


def parse_stf_defines(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    defines: dict[str, int] = {}
    for line in read_text(path).splitlines():
        match = re.match(r"\s*#define\s+([A-Za-z0-9_]+)\s+(-?\d+)\b", line)
        if match:
            defines[match.group(1)] = int(match.group(2))
    return defines


def parse_level100_references() -> dict[str, Any]:
    message_rows: list[dict[str, str]] = []
    help_rows: list[str] = []
    objective_rows: list[str] = []
    loss_rows: list[str] = []
    speakers: list[str] = []

    for path in sorted(LEVEL_DIR.glob("*.msl")):
        for line_number, line in enumerate(read_text(path).splitlines(), start=1):
            code = strip_line_comment(line)
            for match in re.finditer(r"\b(PlayCharMessageWait|PlayCharMessage)\s*\(\s*([^,]+)\s*,\s*([^,\)]+)", code):
                speaker = match.group(2).strip()
                token = match.group(3).strip()
                speakers.append(speaker)
                message_rows.append({"file": path.name, "line": str(line_number), "call": match.group(1), "speaker": speaker, "token": token})
            for match in re.finditer(r"AddHelpMessage\s*\(\s*([A-Z0-9_]+)\s*\)", code):
                help_rows.append(match.group(1))
            for match in re.finditer(r"\b(PrimaryObjectiveFailed|PrimaryObjectiveComplete)\s*\([^,]+,\s*([A-Z0-9_]+)\s*\)", code):
                objective_rows.append(match.group(2))
            for match in re.finditer(r"LevelLostString\s*\(\s*([A-Z0-9_]+)\s*\)", code):
                loss_rows.append(match.group(1))

    return {
        "messageRows": message_rows,
        "messageTokens": sorted({row["token"] for row in message_rows}),
        "helpRows": help_rows,
        "helpTokens": sorted(set(help_rows)),
        "objectiveRows": objective_rows,
        "objectiveTokens": sorted(set(objective_rows)),
        "lossRows": loss_rows,
        "lossTokens": sorted(set(loss_rows)),
        "speakerRows": speakers,
        "speakerTokens": sorted(set(speakers)),
        "speakerCounts": dict(Counter(speakers)),
    }


def origin_summary(tokens: set[str], stores: dict[str, set[str]]) -> dict[str, Any]:
    unresolved = sorted(token for token in tokens if not any(token in values for values in stores.values()))
    return {
        "count": len(tokens),
        "levelEnglish": sum(token in stores["levelEnglish"] for token in tokens),
        "levelGlobal": sum(token in stores["levelGlobal"] for token in tokens),
        "levelStf": sum(token in stores["levelStf"] for token in tokens),
        "sharedEnglish": sum(token in stores["sharedEnglish"] for token in tokens),
        "sharedGlobal": sum(token in stores["sharedGlobal"] for token in tokens),
        "sharedStf": sum(token in stores["sharedStf"] for token in tokens),
        "unresolved": unresolved,
    }


def build_schema() -> dict[str, Any]:
    refs = parse_level100_references()
    level_english = parse_token_blocks(LEVEL_DIR / "English.txt")
    level_global = parse_token_blocks(LEVEL_DIR / "Global.txt")
    level_stf = parse_stf_defines(LEVEL_DIR / "text.stf")
    shared_english = parse_token_blocks(SHARED_TEXT_DIR / "english.txt")
    shared_global = parse_token_blocks(SHARED_TEXT_DIR / "global.txt")
    shared_stf = parse_stf_defines(SHARED_TEXT_DIR / "text.stf")
    stores = {
        "levelEnglish": set(level_english),
        "levelGlobal": set(level_global),
        "levelStf": set(level_stf),
        "sharedEnglish": set(shared_english),
        "sharedGlobal": set(shared_global),
        "sharedStf": set(shared_stf),
    }

    message_tokens = set(refs["messageTokens"])
    help_tokens = set(refs["helpTokens"])
    objective_tokens = set(refs["objectiveTokens"])
    loss_tokens = set(refs["lossTokens"])
    speaker_tokens = set(refs["speakerTokens"])
    referenced_text_tokens = message_tokens | help_tokens | objective_tokens | loss_tokens
    extra_level_tokens = sorted(set(level_english) - referenced_text_tokens)
    relevant_static_tokens = referenced_text_tokens | speaker_tokens | set(extra_level_tokens)

    generated_only = sorted(
        token
        for token in referenced_text_tokens
        if token not in level_english
        and token not in level_global
        and token not in shared_english
        and token not in shared_global
        and token in shared_stf
    )

    return {
        "schemaVersion": "missionscript-level100-tutorial-text-speaker-resolution.v1",
        "status": "PASS",
        "source": {
            "runtimeExecution": False,
            "ghidraMutation": False,
            "rawDialogueIncluded": False,
            "schemaPurpose": "static Level100 tutorial message-token, speaker-token, text-block, and generated-ID resolution for clean-room planning",
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": BACKUP,
        },
        "textCorpus": {
            "levelEnglishTokenBlocks": len(level_english),
            "levelGlobalTokenBlocks": len(level_global),
            "levelTextStfDefines": len(level_stf),
            "sharedEnglishTokenBlocks": len(shared_english),
            "sharedGlobalTokenBlocks": len(shared_global),
            "sharedTextStfDefines": len(shared_stf),
            "levelGlobalEmpty": len(level_global) == 0,
            "levelTextStfEmpty": len(level_stf) == 0,
            "textListHeaderNotAuthoritativeForLevel100": True,
            "boundary": "token names, aggregate counts, and static ID resolution only; raw dialogue payloads are intentionally excluded",
        },
        "level100References": {
            "messageRows": len(refs["messageRows"]),
            "messageUnique": len(message_tokens),
            "helpRows": len(refs["helpRows"]),
            "helpUnique": len(help_tokens),
            "objectiveRows": len(refs["objectiveRows"]),
            "objectiveUnique": len(objective_tokens),
            "lossRows": len(refs["lossRows"]),
            "lossUnique": len(loss_tokens),
            "speakerRows": len(refs["speakerRows"]),
            "speakerUnique": len(speaker_tokens),
            "speakerCounts": refs["speakerCounts"],
        },
        "resolution": {
            "messages": origin_summary(message_tokens, stores),
            "help": origin_summary(help_tokens, stores),
            "objectives": origin_summary(objective_tokens, stores),
            "loss": origin_summary(loss_tokens, stores),
            "speakers": origin_summary(speaker_tokens, stores),
            "extraLevelEnglish": origin_summary(set(extra_level_tokens), stores),
            "missingReferenceTokens": sorted(
                token for token in referenced_text_tokens | speaker_tokens if not any(token in values for values in stores.values())
            ),
            "relevantStaticTokensWithSharedStfOrSharedEnglish": sum(
                token in shared_stf or token in shared_english for token in relevant_static_tokens
            ),
            "relevantStaticTokenCount": len(relevant_static_tokens),
        },
        "tokenSets": {
            "generatedOnlyReferencedTextTokens": generated_only,
            "generatedOnlyMessageTokens": sorted(token for token in message_tokens if token in generated_only),
            "generatedOnlyHelpTokens": sorted(token for token in help_tokens if token in generated_only),
            "generatedOnlyObjectiveTokens": sorted(token for token in objective_tokens if token in generated_only),
            "levelLocalMessageTokens": sorted(token for token in message_tokens if token in level_english),
            "levelLocalLossTokens": sorted(token for token in loss_tokens if token in level_english),
            "speakerTokens": sorted(speaker_tokens),
            "extraLevelEnglishTokensNotReferencedByWalkthroughCalls": extra_level_tokens,
            "helpTokens": sorted(help_tokens),
            "objectiveTokens": sorted(objective_tokens),
            "lossTokens": sorted(loss_tokens),
        },
        "claims": [
            "Level100 tutorial message/help/objective/loss/speaker token references resolve statically with zero missing tokens across level-local English, shared English, and shared text.stf.",
            "Generated-only Level100 references are separated from level-local text blocks instead of being treated as missing dialogue text.",
            "Speaker-token resolution is static token/label evidence only and is separate from runtime portraits, audio, or message-box behavior.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime text or audio behavior",
            "runtime message display",
            "runtime voice/audio playback",
            "runtime localized text selection",
            "speaker portrait behavior",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "runtime Level100 mission outcome",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
        "nextStaticSlice": FOLLOWUP_SLICE,
    }


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match generated schema", failures)
        require(actual["textCorpus"]["levelEnglishTokenBlocks"] == 52, "level English token count mismatch", failures)
        require(actual["textCorpus"]["levelGlobalTokenBlocks"] == 0, "level Global token count mismatch", failures)
        require(actual["textCorpus"]["levelTextStfDefines"] == 0, "level text.stf count mismatch", failures)
        require(actual["textCorpus"]["sharedEnglishTokenBlocks"] == 241, "shared English token count mismatch", failures)
        require(actual["textCorpus"]["sharedGlobalTokenBlocks"] == 2, "shared Global token count mismatch", failures)
        require(actual["textCorpus"]["sharedTextStfDefines"] == 2571, "shared text.stf define count mismatch", failures)
        require(actual["level100References"]["messageRows"] == 45, "message row count mismatch", failures)
        require(actual["level100References"]["messageUnique"] == 43, "message unique count mismatch", failures)
        require(actual["level100References"]["helpRows"] == 6, "help row count mismatch", failures)
        require(actual["level100References"]["objectiveRows"] == 8, "objective row count mismatch", failures)
        require(actual["level100References"]["lossRows"] == 2, "loss row count mismatch", failures)
        require(actual["level100References"]["speakerRows"] == 45, "speaker row count mismatch", failures)
        require(actual["resolution"]["missingReferenceTokens"] == [], "missing Level100 reference tokens", failures)
        require(actual["resolution"]["relevantStaticTokensWithSharedStfOrSharedEnglish"] == 68, "relevant static token resolved count mismatch", failures)
        require(actual["resolution"]["relevantStaticTokenCount"] == 68, "relevant static token denominator mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore text/speaker proof mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan",
        "Status: static text/speaker resolution proof plan complete, not runtime proof",
        PROOF_LINK,
        SCHEMA_LINK,
        WALKTHROUGH_LINK,
        "level100",
        "English.txt",
        "52",
        "Global.txt",
        "level-local `text.stf`",
        "shared `text/english.txt`",
        "shared `text/text.stf`",
        "2571",
        "45",
        "43",
        "6",
        "8",
        "4",
        "2",
        "1",
        "P_TATIANA",
        "P_KRAMER",
        "P_TECHNICIAN",
        "TUTORIAL_13_MOD",
        "TUTORIAL_DODGE_MOD",
        "TUTORIAL_THROTTLE_MOD",
        "HELP_FIRE",
        "HELP_RETRO",
        "HELP_TRANSFORM",
        "HELP_WEAPON_SELECT",
        "HELP_ZOOM_IN",
        "HELP_ZOOM_OUT",
        "_100_OBJECTIVE_1",
        "_100_OBJECTIVE_4",
        "LOSE_TUTORIAL_BROKE",
        "68/68",
        "0 missing",
        BACKUP,
        NEXT_SLICE,
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    linked_paths = (
        BACKLOG,
        MAPPED,
        BIN_INDEX,
        RE_INDEX,
        MSL_DOC,
        MISSION_INDEX,
        MISSION_EVENTS,
        MISSION_MESSAGES,
        MISSION_MESSAGE_CALLSITES,
        MISSION_SPEAKERS,
        MISSION_TEXT,
        MISSIONSCRIPT_PLAN,
        MISSIONSCRIPT_CONTRACT,
        PACKED_LOOSE,
        EVENT_PROOF,
        WALKTHROUGH_PROOF,
    )
    for path in linked_paths:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Level100 Tutorial Text/Speaker Resolution"):
            require(token in text, f"{path.relative_to(ROOT)} missing text/speaker proof token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (MSL_DOC, LORE_MSL_DOC),
        (MISSION_INDEX, LORE_MISSION_INDEX),
        (MISSION_EVENTS, LORE_MISSION_EVENTS),
        (MISSION_MESSAGES, LORE_MISSION_MESSAGES),
        (MISSION_MESSAGE_CALLSITES, LORE_MISSION_MESSAGE_CALLSITES),
        (MISSION_SPEAKERS, LORE_MISSION_SPEAKERS),
        (MISSION_TEXT, LORE_MISSION_TEXT),
        (MISSIONSCRIPT_PLAN, LORE_MISSIONSCRIPT_PLAN),
        (MISSIONSCRIPT_CONTRACT, LORE_MISSIONSCRIPT_CONTRACT),
        (PACKED_LOOSE, LORE_PACKED_LOOSE),
        (EVENT_PROOF, LORE_EVENT_PROOF),
        (WALKTHROUGH_PROOF, LORE_WALKTHROUGH_PROOF),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require("Completed MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan" in backlog, "backlog missing completed text/speaker slice", failures)
    require(BOUNDARY_SLICE in backlog, "backlog missing completed runtime-harness boundary slice", failures)
    require(BOUNDARY_PROOF_LINK in backlog, "backlog missing runtime-harness boundary proof link", failures)
    require(BOUNDARY_SCHEMA_LINK in backlog, "backlog missing runtime-harness boundary schema link", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog, "backlog missing copied-profile runtime-observation planning slice", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}" not in backlog, "backlog still marks runtime-harness boundary active", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan" not in backlog, "backlog still marks text/speaker slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-text-speaker-resolution")
        == r"py -3 tools\missionscript_level100_tutorial_text_speaker_resolution_probe.py --check",
        "missing package Level100 text/speaker test script",
        failures,
    )


def run_check() -> list[str]:
    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_package(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-schema", action="store_true")
    args = parser.parse_args()

    if args.write_schema:
        schema = build_schema()
        write_json(SCHEMA, schema)
        write_json(LORE_SCHEMA, schema)
        print(f"Wrote {SCHEMA.relative_to(ROOT)}")
        print(f"Wrote {LORE_SCHEMA.relative_to(ROOT)}")

    if args.check or not args.write_schema:
        failures = run_check()
        if failures:
            print("MissionScript Level100 tutorial text/speaker resolution probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Level100 tutorial text/speaker resolution probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
