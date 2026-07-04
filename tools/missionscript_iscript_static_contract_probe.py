#!/usr/bin/env python3
"""Validate the MissionScript / IScript static contract extraction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_iscript_static_contract_2026-06-08.md"
PROOF_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
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

CONTRACT_LINK = "missionscript-iscript-static-contract.md"
PROOF_PLAN_LINK = "missionscript-iscript-proof-plan.md"
WORLD_PLAN_LINK = "world-thing-spawn-object-reference-proof-plan.md"
SCHEMA_PLAN_LINK = "world-thing-spawn-copied-corpus-schema-proof-plan.md"
VM_SCHEMA_PROOF_LINK = "missionscript-vm-datatype-opcode-schema-proof.md"
VM_SCHEMA_JSON_LINK = "missionscript-vm-datatype-opcode-schema.v1.json"
EVENT_OBJECT_CODE_PROOF_LINK = "missionscript-event-object-code-lifecycle-proof.md"
EVENT_OBJECT_CODE_SCHEMA_LINK = "missionscript-event-object-code-lifecycle.v1.json"
SLOT_COMMAND_PROOF_LINK = "missionscript-slot-command-effect-static-proof.md"
SLOT_COMMAND_SCHEMA_LINK = "missionscript-slot-command-effect.v1.json"
OBJECTIVE_OUTCOME_PROOF_LINK = "missionscript-objective-outcome-command-effect-static-proof.md"
OBJECTIVE_OUTCOME_SCHEMA_LINK = "missionscript-objective-outcome-command-effect.v1.json"
MESSAGE_AUDIO_PROOF_LINK = "missionscript-message-audio-command-effect-static-proof.md"
MESSAGE_AUDIO_SCHEMA_LINK = "missionscript-message-audio-command-effect.v1.json"
GOODIE_STATE_PROOF_LINK = "missionscript-goodie-state-command-effect-static-proof.md"
GOODIE_STATE_SCHEMA_LINK = "missionscript-goodie-state-command-effect.v1.json"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

CONTRACT_TOKENS = (
    "MissionScript / IScript Static Contract",
    "Status: static contract extraction complete, not runtime proof",
    "missionscript-iscript-static-contract",
    "missionscript-iscript-proof-plan.md",
    "missionscript-static-review-wave903",
    "wave1189-missionscript-bytecode-iscript-current-risk-review",
    "wave1208-cbooldatatype-current-risk-review",
    "`169` selected MissionScript family rows",
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
    "CAsmInstruction__SpawnFromOpcode",
    "CInstructionOP_PLUS__VFunc_00_0052e180",
    "CInstructionOP_MINUS__VFunc_00_0052e1d0",
    "CInstructionOP_MULTIPLY__VFunc_00_0052e220",
    "CInstructionOP_DIVIDE__VFunc_00_0052e270",
    "CInstructionOP_CMP__VFunc_00_0052e330",
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
    "CMissionScriptObjectCode__ClearFields_Thunk",
    "`57` level rows",
    "`418` `GetThingRef`",
    "`18` `SpawnThing`",
    "`436` total thing/spawn refs",
    "`95` level rows",
    "`795` loose event-name counts",
    "World/thing/spawn bridge",
    "world-thing-spawn-object-reference-proof-plan.md",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified",
)

READINESS_TOKENS = (
    "MissionScript / IScript Static Contract Readiness Note",
    "static contract extraction complete, not runtime proof",
    "not a new static re-audit wave",
    "not a Ghidra mutation",
    "not a runtime test",
    "not a mission execution proof",
    "not a live loose-MSL loading proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a rebuild parity claim",
    "World / Thing / Spawn / Object-Reference Bridge Proof Plan",
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


def check_contract(failures: list[str]) -> None:
    text = read_text(CONTRACT)
    for token in (*STATIC_TOKENS, *CONTRACT_TOKENS):
        require(token in text, f"contract missing token: {token}", failures)
    check_no_overclaims(CONTRACT, failures)
    require(read_text(LORE_CONTRACT) == text, "lore static-contract mirror mismatch", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    for token in (*STATIC_TOKENS, *READINESS_TOKENS, *CONTRACT_TOKENS[2:30]):
        require(token in text, f"readiness missing token: {token}", failures)
    check_no_overclaims(READINESS, failures)


def check_source_docs(failures: list[str]) -> None:
    for path in (
        PROOF_PLAN,
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
        require(CONTRACT_LINK in text, f"{path.relative_to(ROOT)} missing static-contract link", failures)
        if path != PROOF_PLAN:
            require(PROOF_PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        check_no_overclaims(path, failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(CONTRACT_LINK in text, f"{path.relative_to(ROOT)} missing static-contract link", failures)
        require(PROOF_PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        require("MissionScript / IScript Static Contract" in text, f"{path.relative_to(ROOT)} missing static-contract label", failures)
        check_no_overclaims(path, failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Completed World / Thing / Spawn / Object-Reference Bridge Proof Plan" in backlog, "backlog missing completed world/thing/spawn bridge slice", failures)
    require("Completed MissionScript Goodie State Command-Effect static proof" in backlog, "backlog missing completed MissionScript Goodie-state command-effect slice", failures)
    require("MissionScript Goodie State Command-Effect" in backlog, "backlog missing MissionScript Goodie-state command-effect label", failures)
    require(GOODIE_STATE_PROOF_LINK in backlog, "backlog missing MissionScript Goodie-state command-effect proof link", failures)
    require(GOODIE_STATE_SCHEMA_LINK in backlog, "backlog missing MissionScript Goodie-state command-effect schema link", failures)
    require("MissionScript Message/Audio Command-Effect" in backlog, "backlog missing MissionScript message/audio command-effect label", failures)
    require(MESSAGE_AUDIO_PROOF_LINK in backlog, "backlog missing MissionScript message/audio command-effect proof link", failures)
    require(MESSAGE_AUDIO_SCHEMA_LINK in backlog, "backlog missing MissionScript message/audio command-effect schema link", failures)
    require("MissionScript Objective/Outcome Command-Effect" in backlog, "backlog missing MissionScript objective/outcome command-effect label", failures)
    require(OBJECTIVE_OUTCOME_PROOF_LINK in backlog, "backlog missing MissionScript objective/outcome command-effect proof link", failures)
    require(OBJECTIVE_OUTCOME_SCHEMA_LINK in backlog, "backlog missing MissionScript objective/outcome command-effect schema link", failures)
    require("MissionScript Slot Command-Effect" in backlog, "backlog missing MissionScript slot command-effect label", failures)
    require(SLOT_COMMAND_PROOF_LINK in backlog, "backlog missing MissionScript slot command-effect proof link", failures)
    require(SLOT_COMMAND_SCHEMA_LINK in backlog, "backlog missing MissionScript slot command-effect schema link", failures)
    require("Completed MissionScript VM/datatype/opcode schema proof" in backlog, "backlog missing completed MissionScript VM/datatype/opcode schema proof", failures)
    require(VM_SCHEMA_PROOF_LINK in backlog, "backlog missing MissionScript VM/datatype/opcode proof link", failures)
    require(VM_SCHEMA_JSON_LINK in backlog, "backlog missing MissionScript VM/datatype/opcode schema link", failures)
    require("Completed MissionScript event/object-code lifecycle schema proof" in backlog, "backlog missing completed MissionScript event/object-code lifecycle schema proof", failures)
    require(EVENT_OBJECT_CODE_PROOF_LINK in backlog, "backlog missing MissionScript event/object-code lifecycle proof link", failures)
    require(EVENT_OBJECT_CODE_SCHEMA_LINK in backlog, "backlog missing MissionScript event/object-code lifecycle schema link", failures)
    require("Completed MissionScript / IScript static-contract extraction slice" in backlog, "backlog missing completed static-contract slice", failures)
    require("Completed MissionScript / IScript proof-plan slice" in backlog, "backlog missing completed proof-plan slice", failures)
    require(WORLD_PLAN_LINK in backlog, "backlog missing world/thing/spawn bridge link", failures)
    require(SCHEMA_PLAN_LINK in backlog, "backlog missing copied-corpus schema link", failures)
    require("The selected active static-to-proof slice is [MissionScript / IScript Static Contract]" not in backlog, "backlog still has stale active static-contract slice", failures)

    mapped = read_text(MAPPED)
    require("Completed MissionScript / IScript static-contract extraction slice" in mapped, "mapped systems missing completed static-contract slice", failures)
    require("Completed World / Thing / Spawn / Object-Reference Bridge Proof Plan" in mapped, "mapped systems missing completed world/thing/spawn bridge slice", failures)
    require("Completed MissionScript VM/datatype/opcode schema result" in mapped, "mapped systems missing completed MissionScript VM/datatype/opcode schema result", failures)
    require(VM_SCHEMA_PROOF_LINK in mapped, "mapped systems missing MissionScript VM/datatype/opcode proof link", failures)
    require(VM_SCHEMA_JSON_LINK in mapped, "mapped systems missing MissionScript VM/datatype/opcode schema link", failures)
    require("Completed MissionScript event/object-code lifecycle schema result" in mapped, "mapped systems missing completed MissionScript event/object-code lifecycle schema result", failures)
    require(EVENT_OBJECT_CODE_PROOF_LINK in mapped, "mapped systems missing MissionScript event/object-code lifecycle proof link", failures)
    require(EVENT_OBJECT_CODE_SCHEMA_LINK in mapped, "mapped systems missing MissionScript event/object-code lifecycle schema link", failures)
    require("Completed MissionScript Slot Command-Effect static proof" in mapped, "mapped systems missing completed MissionScript slot command-effect result", failures)
    require(SLOT_COMMAND_PROOF_LINK in mapped, "mapped systems missing MissionScript slot command-effect proof link", failures)
    require(SLOT_COMMAND_SCHEMA_LINK in mapped, "mapped systems missing MissionScript slot command-effect schema link", failures)
    require("Completed MissionScript Objective/Outcome Command-Effect static proof" in mapped, "mapped systems missing completed MissionScript objective/outcome command-effect result", failures)
    require(OBJECTIVE_OUTCOME_PROOF_LINK in mapped, "mapped systems missing MissionScript objective/outcome command-effect proof link", failures)
    require(OBJECTIVE_OUTCOME_SCHEMA_LINK in mapped, "mapped systems missing MissionScript objective/outcome command-effect schema link", failures)
    require("MissionScript Goodie State Command-Effect" in mapped, "mapped systems missing MissionScript Goodie-state command-effect result", failures)
    require(GOODIE_STATE_PROOF_LINK in mapped, "mapped systems missing MissionScript Goodie-state command-effect proof link", failures)
    require(GOODIE_STATE_SCHEMA_LINK in mapped, "mapped systems missing MissionScript Goodie-state command-effect schema link", failures)
    require("Completed MissionScript / IScript proof-plan slice" in mapped, "mapped systems missing completed MissionScript proof-plan slice", failures)
    require(WORLD_PLAN_LINK in mapped, "mapped systems missing world/thing/spawn bridge link", failures)
    require(SCHEMA_PLAN_LINK in mapped, "mapped systems missing copied-corpus schema link", failures)
    require("Active MissionScript / IScript static-contract extraction slice" not in mapped, "mapped systems still has stale active static-contract slice", failures)


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
    scripts = read_json(PACKAGE_JSON)["scripts"]
    require(
        scripts.get("test:missionscript-iscript-static-contract") == r"py -3 tools\missionscript_iscript_static_contract_probe.py --check",
        "missing package MissionScript/IScript static-contract script",
        failures,
    )
    require(
        scripts.get("test:missionscript-iscript-proof-plan") == r"py -3 tools\missionscript_iscript_proof_plan_probe.py --check",
        "missing package MissionScript/IScript proof-plan script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_contract(failures)
    check_readiness(failures)
    check_source_docs(failures)
    check_front_doors(failures)
    check_progress_unchanged(failures)
    check_package(failures)

    if failures:
        print("MissionScript / IScript static-contract probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript / IScript static-contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
