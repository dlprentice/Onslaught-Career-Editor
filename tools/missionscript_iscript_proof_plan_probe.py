#!/usr/bin/env python3
"""Validate the MissionScript / IScript proof plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_iscript_proof_plan_2026-06-08.md"
MISSION_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-static-review-2026-05-26.md"
MSL_DOC = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
MISSION_INDEX = ROOT / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
MISSION_EVENTS = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
MISSION_SLOT = ROOT / "reverse-engineering" / "game-assets" / "mission-slot-usage.md"
MISSION_THING = ROOT / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
MISSION_MESSAGE = ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "missionscript-iscript-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "MissionScript / IScript Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "missionscript-iscript-proof-plan",
    "missionscript-static-review-wave903",
    "wave1189-missionscript-bytecode-iscript-current-risk-review",
    "wave1208-cbooldatatype-current-risk-review",
    "`169` saved Ghidra rows",
    "ScriptCommandRegistry__InitBuiltins",
    "`144` contiguous `0x40`-byte command descriptor records",
    "0x0064ce50",
    "0x0064f210",
    "FollowWaypointWait",
    "IsOverWater",
    "`49` `IScript__*` functions",
    "IScript__ScheduleEvent",
    "IScript__SetSlotSave",
    "IScript__LevelWon",
    "IScript__GetThingRef",
    "IScript__SpawnThing",
    "IScript__SetGoodieState",
    "IScript__GetGoodieState",
    "missionscript-goodie-state-command-effect-static-proof.md",
    "missionscript-goodie-state-command-effect.v1.json",
    "MissionScript Goodie State Command-Effect",
    "g_Career_mGoodies[index-1]",
    "0x00662564",
    "0x1F46",
    "descriptor/name context only",
    "`37` datatype rows",
    "`19` instruction/opcode rows",
    "0x0052e180",
    "0x0052e1d0",
    "0x0052e220",
    "0x0052e270",
    "0x0052e330",
    "CInstructionOP_PLUS__VFunc_00_0052e180",
    "CInstructionOP_MINUS__VFunc_00_0052e1d0",
    "CInstructionOP_MULTIPLY__VFunc_00_0052e220",
    "CInstructionOP_DIVIDE__VFunc_00_0052e270",
    "CInstructionOP_CMP__VFunc_00_0052e330",
    "IScript__Constructor",
    "CMissionScriptObjectCode__ClearFields_Thunk",
    "CAsmInstruction__SpawnFromOpcode",
    "Wave1120",
    "script_state+0x218",
    "script_object_code+0x68",
    "CBoolDataType__Equals",
    "CBoolDataType__NotEquals",
    "CBoolDataType__Assign",
    "`22` `CScriptObjectCode`",
    "`13` `CScriptEventNB`",
    "`7` `CMissionScriptObjectCode`",
    "`5` `CEventFunction`",
    "CScriptObjectCode__Run",
    "CScriptEventNB__PostEvent",
    "CMissionScriptObjectCode__LoadAsync",
    "`95` level rows",
    "`795` loose event-name counts",
    "`115` primary-complete calls",
    "`42` secondary-complete calls",
    "`102` primary-failed calls",
    "`79` level-won calls",
    "`13` level-lost calls",
    "mission-scripts-index.md",
    "mission-events-index.md",
    "mission-slot-usage.md",
    "mission-thing-usage.md",
    "mission-message-usage.md",
    "command descriptor schema design",
    "IScript command-effect design",
    "VM/datatype/opcode behavior design",
    "event/object-code lifecycle design",
    "loose MSL corpus linkage design",
    "mission outcome/event proof design",
    "slot/goodie/career bridge design",
    "thing/spawn/object-reference bridge design",
    "message/objective/HUD command design",
    r"G:\GhidraBackups\BEA_20260526-095411_post_wave903_missionscript_static_review_verified",
    r"G:\GhidraBackups\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified",
    r"G:\GhidraBackups\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified",
)

READINESS_TOKENS = (
    "MissionScript / IScript Proof Plan Readiness Note",
    "proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a mission execution proof",
    "not a live loose-MSL loading proof",
    "not a save/career mutation proof",
    "not a screenshot/capture proof",
    "not a native input proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a rebuild parity claim",
    "No runtime MissionScript execution",
    "runtime command effects",
    "runtime event outcomes",
    "live loose-MSL loading",
)

FORBIDDEN_PHRASES = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime event outcomes proven",
    "runtime mission objectives proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact command descriptor schema proven",
    "exact vm layout proven",
    "exact source-body identity proven",
    "bea patching behavior proven",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "runtime proof complete",
)

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_no_overclaims(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)


def check_plan(failures: list[str]) -> None:
    text = read_text(PLAN)
    for token in (*STATIC_TOKENS, *ANCHOR_TOKENS):
        require(token in text, f"plan missing token: {token}", failures)
    check_no_overclaims(PLAN, failures)
    require(read_text(LORE_PLAN) == text, "lore proof-plan mirror mismatch", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    for token in (*STATIC_TOKENS, *READINESS_TOKENS):
        require(token in text, f"readiness missing token: {token}", failures)
    for token in (
        "missionscript-static-review-wave903",
        "wave1189-missionscript-bytecode-iscript-current-risk-review",
        "wave1208-cbooldatatype-current-risk-review",
        "ScriptCommandRegistry__InitBuiltins",
        "copied-profile, copied-script, copied-resource, copied-file, or app-owned artifact-root work",
        "stop on installed-game mutation need",
    ):
        require(token in text, f"readiness missing anchor token: {token}", failures)
    check_no_overclaims(READINESS, failures)


def check_source_docs(failures: list[str]) -> None:
    for path in (
        MISSION_STATIC,
        MSL_DOC,
        MSL_COMMANDS,
        MISSION_INDEX,
        MISSION_EVENTS,
        MISSION_SLOT,
        MISSION_THING,
        MISSION_MESSAGE,
    ):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        check_no_overclaims(path, failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        require("MissionScript / IScript proof plan" in text or "MissionScript / IScript Proof Plan" in text, f"{path.relative_to(ROOT)} missing MissionScript plan label", failures)
        check_no_overclaims(path, failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Completed MissionScript / IScript proof-plan slice" in backlog, "backlog missing completed MissionScript slice", failures)
    require("The selected active static-to-proof slice is [MissionScript / IScript Proof Plan]" not in backlog, "backlog still marks MissionScript proof plan active", failures)
    require("missionscript-iscript-static-contract.md" in backlog, "backlog missing MissionScript static-contract successor", failures)
    require("Completed Frontend / input / game-loop proof-plan slice" in backlog, "backlog missing completed frontend/input slice", failures)
    require("Do not broaden into live mission execution, broad mission simulation, save/career mutation, native input, audio/message/HUD output, packed-vs-loose resource selection, Godot, patching, broad runtime proof, or rebuild parity." in backlog, "backlog missing MissionScript broadening boundary", failures)

    mapped = read_text(MAPPED)
    require("Completed MissionScript / IScript proof-plan slice" in mapped, "mapped systems missing completed MissionScript slice", failures)
    require("Active MissionScript / IScript proof-plan slice" not in mapped, "mapped systems still marks MissionScript proof plan active", failures)
    require("missionscript-iscript-static-contract.md" in mapped, "mapped systems missing MissionScript static-contract successor", failures)
    require("MissionScript / IScript Core" in mapped and PLAN_LINK in mapped, "mapped systems missing MissionScript row link", failures)


def check_progress_unchanged(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total function mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented function mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)

    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "live focused mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1210, "legacy additive mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)


def check_package(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    scripts = package["scripts"]
    require(
        scripts.get("test:missionscript-iscript-proof-plan") == r"py -3 tools\missionscript_iscript_proof_plan_probe.py --check",
        "missing package MissionScript/IScript proof-plan script",
        failures,
    )
    require(
        scripts.get("test:ghidra-missionscript-static-review-wave903") == r"py -3 tools\ghidra_missionscript_static_review_wave903_probe.py --check",
        "missing package Wave903 MissionScript static review script",
        failures,
    )
    require(
        scripts.get("test:wave1189-missionscript-bytecode-iscript-current-risk-review") == r"py -3 tools\wave1189_missionscript_bytecode_iscript_current_risk_review.py --check",
        "missing package Wave1189 MissionScript bytecode/IScript script",
        failures,
    )
    require(
        scripts.get("test:wave1208-cbooldatatype-current-risk-review") == r"py -3 tools\wave1208_cbooldatatype_current_risk_review.py --check",
        "missing package Wave1208 CBoolDataType script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_plan(failures)
    check_readiness(failures)
    check_source_docs(failures)
    check_front_doors(failures)
    check_progress_unchanged(failures)
    check_package(failures)

    if failures:
        print("MissionScript / IScript proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript / IScript proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
