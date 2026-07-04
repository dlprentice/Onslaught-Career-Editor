#!/usr/bin/env python3
"""Validate the MissionScript message/audio command-effect static proof."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_message_audio_command_effect_static_proof_2026-06-08.md"

DESCRIPTOR_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PROOF_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
LORE_ISCRIPT_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
MESSAGEBOX_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MessageBox.cpp" / "_index.md"
LORE_MESSAGEBOX_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "MessageBox.cpp" / "_index.md"
MESSAGES_DOC = ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
MSL_SCRIPTING = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE584 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave584-iscript-name-audio-00535670"
WAVE1015 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1015-ogg-message-lifecycle-review"
WAVE1074 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1074-script-text-console-boundary"

CALLSITE_DOCS = (
    ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage-callsites-1.md",
    ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage-callsites-2.md",
)

WAVE1219_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
WAVE584_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260519-091559_post_wave584_iscript_object_audio_verified"
WAVE1015_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified"
WAVE1074_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-052830_post_wave1074_script_text_console_boundary_verified"

PROOF_LINK = "missionscript-message-audio-command-effect-static-proof.md"
SCHEMA_LINK = "missionscript-message-audio-command-effect.v1.json"

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
    "runtime messagescript execution proven",
    "runtime messages proven",
    "runtime message display proven",
    "runtime voice playback proven",
    "runtime audio playback proven",
    "runtime hud output proven",
    "runtime queue ordering proven",
    "live loose-msl loading proven",
    "exact command descriptor layout proven",
    "exact cmessage layout proven",
    "exact cmessagebox layout proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)

DESCRIPTOR_COMMANDS = {
    "PlaySample": {"index": 9, "recordAddress": "0x0064d090", "symbol": "s_PlaySample_0064f9b0"},
    "PrintText": {"index": 15, "recordAddress": "0x0064d210", "symbol": "s_PrintText_0064f984"},
    "AddMessage": {"index": 16, "recordAddress": "0x0064d250", "symbol": "s_AddMessage_0064f978"},
    "PlayCharMessage": {"index": 27, "recordAddress": "0x0064d510", "symbol": "s_PlayCharMessage_0064f8ec"},
    "HighlightHudPart": {"index": 33, "recordAddress": "0x0064d690", "symbol": "s_HighlightHudPart_0064f89c"},
    "UnHighlightHudPart": {"index": 34, "recordAddress": "0x0064d6d0", "symbol": "s_UnHighlightHudPart_0064f888"},
    "PlayCharMessageWait": {"index": 35, "recordAddress": "0x0064d710", "symbol": "s_PlayCharMessageWait_0064f874"},
    "PlayPCharMessage": {"index": 89, "recordAddress": "0x0064e490", "symbol": "s_PlayPCharMessage_0064f568"},
    "PlayPCharMessageWait": {"index": 90, "recordAddress": "0x0064e4d0", "symbol": "s_PlayPCharMessageWait_0064f550"},
    "SwitchMessagesOn": {"index": 111, "recordAddress": "0x0064ea10", "symbol": "s_SwitchMessagesOn_0064f404"},
    "SwitchMessagesOff": {"index": 112, "recordAddress": "0x0064ea50", "symbol": "s_SwitchMessagesOff_0064f3f0"},
    "AddHelpMessage": {"index": 117, "recordAddress": "0x0064eb90", "symbol": "s_AddHelpMessage_0064f390"},
}

MESSAGE_QUEUE_HANDLERS: list[dict[str, Any]] = [
    {
        "address": "0x00537410",
        "name": "IScript__PlaySound",
        "summary": "default text id plus float payload enqueue a CMessage when DAT_008a9d84 is present",
        "metadataTokens": ("message/audio request", "DAT_008a9d84", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance"),
        "decompile": "00537410_IScript__PlaySound.c",
        "decompileTokens": ("DAT_008a9d84", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "CMessage__ctor_base"),
    },
    {
        "address": "0x00537500",
        "name": "IScript__PlaySoundWithCallback",
        "summary": "two text ids plus float payload enqueue a CMessage and optionally retain an active-reader target",
        "metadataTokens": ("active-reader target", "CMessage-sized object", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance"),
        "decompile": "00537500_IScript__PlaySoundWithCallback.c",
        "decompileTokens": ("DAT_008a9d84", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "CMessage__ctor_base"),
    },
    {
        "address": "0x005375f0",
        "name": "IScript__PlaySoundWithFade",
        "summary": "fade/tracking object plus event 0x7d1 setup before the same message queue handoff",
        "metadataTokens": ("event 0x7d1", "CScheduledEvent__Set", "enqueues a CMessage"),
        "decompile": "005375f0_IScript__PlaySoundWithFade.c",
        "decompileTokens": ("0x7d1", "CScheduledEvent__Set", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance"),
    },
    {
        "address": "0x005377e0",
        "name": "IScript__PlaySoundWithPriority",
        "summary": "two text ids, float payload, and priority enqueue the message through CMessageBox",
        "metadataTokens": ("priority value", "CMessage-sized object", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance"),
        "decompile": "005377e0_IScript__PlaySoundWithPriority.c",
        "decompileTokens": ("priority", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "CMessage__ctor_base"),
    },
    {
        "address": "0x005378e0",
        "name": "IScript__PlaySoundWithFadeAndPriority",
        "summary": "fade event setup and priority message enqueue combined",
        "metadataTokens": ("fade-event setup", "priority message enqueue", "DAT_008a9d84"),
        "decompile": "005378e0_IScript__PlaySoundWithFadeAndPriority.c",
        "decompileTokens": ("0x7d1", "priority", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance"),
    },
]

MESSAGEBOX_CONTEXT = (
    "CMessage__ctor_base",
    "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
    "CMessageBox__StartVoiceOrFallbackTextReveal",
    "CMessageBox__AdvanceRevealAndScheduleNextTick",
    "CMessageBox__StopVoicePlaybackIfNotInCutscene",
    "CMessageBox__RenderOverlay",
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


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_by_address(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {row[key].lower(): row for row in read_tsv_rows(path)}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def parse_markdown_table(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in read_text(path).splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("|---") or line.startswith("| Level "):
            continue
        cells = [part.strip() for part in line.strip().strip("|").split("|")]
        if cells and cells[0].isdigit():
            rows.append(cells)
    return rows


def mission_message_summary() -> dict[str, Any]:
    rows = parse_markdown_table(MESSAGES_DOC)
    return {
        "source": "reverse-engineering/game-assets/mission-message-usage.md",
        "levelRows": len(rows),
        "playCharMessage": sum(int(row[2]) for row in rows),
        "addHelpMessage": sum(int(row[3]) for row in rows),
        "levelLostFamily": sum(int(row[4]) for row in rows),
        "levelWonFamily": sum(int(row[5]) for row in rows),
        "boundary": "loose MSL message-family counts only; runtime voice/audio/HUD output and mission outcomes remain unproven",
    }


def mission_message_callsites() -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    for path in CALLSITE_DOCS:
        for cells in parse_markdown_table(path):
            rows.append(
                {
                    "level": cells[0],
                    "dir": cells[1],
                    "file": cells[2],
                    "command": cells[3],
                    "speaker": cells[4],
                    "token": cells[5],
                }
            )
    by_command: dict[str, int] = {}
    for row in rows:
        command = row["command"].strip("`")
        by_command[command] = by_command.get(command, 0) + 1
    speakers = {row["speaker"] for row in rows if row["speaker"] != "``"}
    tokens = {row["token"] for row in rows if row["token"] != "``"}
    return {
        "source": [
            "reverse-engineering/game-assets/mission-message-usage-callsites-1.md",
            "reverse-engineering/game-assets/mission-message-usage-callsites-2.md",
        ],
        "detailedRows": len(rows),
        "byCommand": dict(sorted(by_command.items())),
        "speakerCount": len(speakers),
        "uniqueTokenCount": len(tokens),
        "boundary": "callsite inventory only; command execution, text lookup, audio playback, and HUD display remain unproven",
    }


def evidence_counts() -> dict[str, int]:
    return {
        "wave584MetadataRows": len(read_tsv_rows(WAVE584 / "post_metadata.tsv")),
        "wave584TagRows": len(read_tsv_rows(WAVE584 / "post_tags.tsv")),
        "wave584XrefRows": len(read_tsv_rows(WAVE584 / "post_xrefs.tsv")),
        "wave584InstructionRows": len(read_tsv_rows(WAVE584 / "post_instructions.tsv")),
        "wave584DecompileRows": len(read_tsv_rows(WAVE584 / "post_decompile" / "index.tsv")),
        "wave584VtableRows": len(read_tsv_rows(WAVE584 / "post_vtables.tsv")),
        "wave1015MetadataRows": len(read_tsv_rows(WAVE1015 / "metadata.tsv")),
        "wave1015TagRows": len(read_tsv_rows(WAVE1015 / "tags.tsv")),
        "wave1015XrefRows": len(read_tsv_rows(WAVE1015 / "xrefs.tsv")),
        "wave1015InstructionRows": len(read_tsv_rows(WAVE1015 / "instructions.tsv")),
        "wave1015DecompileRows": len(read_tsv_rows(WAVE1015 / "decompile" / "index.tsv")),
        "wave1015ContextMetadataRows": len(read_tsv_rows(WAVE1015 / "context-metadata.tsv")),
        "wave1015ContextXrefRows": len(read_tsv_rows(WAVE1015 / "context-xrefs.tsv")),
        "wave1015ContextInstructionRows": len(read_tsv_rows(WAVE1015 / "context-instructions.tsv")),
        "wave1015ContextDecompileRows": len(read_tsv_rows(WAVE1015 / "context-decompile" / "index.tsv")),
        "wave1074MetadataRows": len(read_tsv_rows(WAVE1074 / "post-metadata.tsv")),
        "wave1074TagRows": len(read_tsv_rows(WAVE1074 / "post-tags.tsv")),
        "wave1074XrefRows": len(read_tsv_rows(WAVE1074 / "post-xrefs.tsv")),
        "wave1074InstructionRows": len(read_tsv_rows(WAVE1074 / "post-body-instructions.tsv")),
        "wave1074DecompileRows": len(read_tsv_rows(WAVE1074 / "post-decompile" / "index.tsv")),
    }


def descriptor_records() -> dict[str, Any]:
    descriptor = read_json(DESCRIPTOR_SCHEMA)
    records = {record["commandName"]: record for record in descriptor["records"] if record.get("commandName")}
    result: dict[str, Any] = {}
    for command, expected in DESCRIPTOR_COMMANDS.items():
        record = records[command]
        raw_entry = next(item["value"] for item in record["rawAssignments"] if item["offset"] == "+0x00")
        result[command] = {
            "index": record["index"],
            "recordAddress": record["recordAddress"],
            "observedNameSymbol": record["observedNameSymbol"],
            "rawEntryValue": raw_entry,
            "nameStatus": record["nameStatus"],
            "expectedSymbol": expected["symbol"],
        }
    return result


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-message-audio-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave584", "Wave903", "Wave1015", "Wave1074"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static message/audio command descriptor, handler-body, queue-context, and loose-corpus bridge mapping for clean-room planning",
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": WAVE1219_BACKUP,
        },
        "evidenceCounts": evidence_counts(),
        "descriptorRecords": descriptor_records(),
        "missionMessageSummary": mission_message_summary(),
        "missionMessageCallsites": mission_message_callsites(),
        "messageQueueHandlers": [
            {key: value for key, value in handler.items() if key not in {"metadataTokens", "decompile", "decompileTokens"}}
            for handler in MESSAGE_QUEUE_HANDLERS
        ],
        "consoleTextHandler": {
            "address": "0x00537c40",
            "name": "IScript__PrintText",
            "descriptorEvidence": "s_PrintText_0064f984 / 0x0064d220 plus Wave1074 boundary recovery around 0x00537c40",
            "bodyEvidence": "reads script_args[0], calls CText__GetStringById, then CConsole__Printf with format 0x0064fda4 \"%w\"",
        },
        "messageBoxContext": list(MESSAGEBOX_CONTEXT),
        "fieldMappingBoundary": "Descriptor names and raw entry values are preserved as static evidence, but this schema does not prove the exact descriptor field layout or one-to-one command-handler mapping for every row.",
        "claims": [
            "The static descriptor table contains the selected message/audio/HUD-adjacent command names and record addresses.",
            "The saved Wave584 IScript__PlaySound* bodies show static message/audio request handoff into CMessage and CMessageBox queue helpers.",
            "Wave1074 recovers the PrintText static console/text boundary.",
            "Wave1015 and MessageBox owner docs preserve the queued CMessage/CMessageBox lifecycle context used by the IScript message/audio bodies.",
            "The loose MSL message corpus gives reproducible PlayCharMessage/AddHelpMessage/LevelLost/LevelWon family counts for clean-room planning.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime message display",
            "runtime voice playback",
            "runtime audio playback",
            "runtime HUD output",
            "runtime queue ordering",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "exact command descriptor layout",
            "exact command arity",
            "exact argument type schema",
            "exact CMessage layout",
            "exact CMessageBox layout",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def require_tokens(label: str, text: str, tokens: tuple[str, ...], failures: list[str]) -> None:
    for token in tokens:
        require(token in text, f"{label} missing token: {token}", failures)


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
        require(actual["missionMessageSummary"]["levelRows"] == 67, "message summary level-row mismatch", failures)
        require(actual["missionMessageSummary"]["playCharMessage"] == 1365, "PlayCharMessage summary count mismatch", failures)
        require(actual["missionMessageSummary"]["addHelpMessage"] == 7, "AddHelpMessage summary count mismatch", failures)
        require(actual["missionMessageSummary"]["levelLostFamily"] == 110, "LevelLost-family summary count mismatch", failures)
        require(actual["missionMessageSummary"]["levelWonFamily"] == 71, "LevelWon-family summary count mismatch", failures)
        require(actual["missionMessageCallsites"]["detailedRows"] == 1553, "message detailed row count mismatch", failures)
        require(actual["missionMessageCallsites"]["byCommand"].get("PlayCharMessage") == 1365, "PlayCharMessage detailed count mismatch", failures)
        require(actual["missionMessageCallsites"]["byCommand"].get("AddHelpMessage") == 7, "AddHelpMessage detailed count mismatch", failures)
        require(actual["missionMessageCallsites"]["speakerCount"] == 11, "speaker count mismatch", failures)
        require(actual["missionMessageCallsites"]["uniqueTokenCount"] == 499, "message token count mismatch", failures)
        for command, expected_slot in DESCRIPTOR_COMMANDS.items():
            record = actual["descriptorRecords"].get(command)
            require(record is not None, f"missing descriptor record for {command}", failures)
            if record is not None:
                require(record["index"] == expected_slot["index"], f"{command} descriptor index mismatch", failures)
                require(record["recordAddress"] == expected_slot["recordAddress"], f"{command} descriptor address mismatch", failures)
                require(record["observedNameSymbol"] == expected_slot["symbol"], f"{command} descriptor symbol mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "wave584MetadataRows": 11,
        "wave584TagRows": 11,
        "wave584XrefRows": 11,
        "wave584InstructionRows": 4059,
        "wave584DecompileRows": 11,
        "wave584VtableRows": 64,
        "wave1015MetadataRows": 7,
        "wave1015TagRows": 7,
        "wave1015XrefRows": 14,
        "wave1015InstructionRows": 195,
        "wave1015DecompileRows": 7,
        "wave1015ContextMetadataRows": 17,
        "wave1015ContextXrefRows": 549,
        "wave1015ContextInstructionRows": 548,
        "wave1015ContextDecompileRows": 17,
        "wave1074MetadataRows": 1,
        "wave1074TagRows": 1,
        "wave1074XrefRows": 1,
        "wave1074InstructionRows": 13,
        "wave1074DecompileRows": 1,
    }
    actual_counts = evidence_counts()
    for key, expected in expected_counts.items():
        require(actual_counts.get(key) == expected, f"{key} mismatch: {actual_counts.get(key)} != {expected}", failures)

    wave584_metadata = tsv_by_address(WAVE584 / "post_metadata.tsv")
    for handler in MESSAGE_QUEUE_HANDLERS:
        row = wave584_metadata.get(handler["address"])
        require(row is not None, f"missing Wave584 metadata row {handler['address']}", failures)
        if row is not None:
            require(row["name"] == handler["name"], f"Wave584 name mismatch at {handler['address']}", failures)
            require_tokens(f"Wave584 comment {handler['address']}", row["comment"], handler["metadataTokens"], failures)
        decompile = read_text(WAVE584 / "post_decompile" / handler["decompile"])
        require_tokens(f"Wave584 decompile {handler['address']}", decompile, handler["decompileTokens"], failures)

    wave1074_metadata = tsv_by_address(WAVE1074 / "post-metadata.tsv")
    print_text = wave1074_metadata.get("0x00537c40")
    require(print_text is not None, "missing Wave1074 PrintText metadata row", failures)
    if print_text is not None:
        require(print_text["name"] == "IScript__PrintText", "Wave1074 PrintText name mismatch", failures)
        require_tokens(
            "Wave1074 PrintText comment",
            print_text["comment"],
            ("s_PrintText_0064f984", "CText__GetStringById", "CConsole__Printf", "%w"),
            failures,
        )
    require_tokens(
        "Wave1074 PrintText decompile",
        read_text(WAVE1074 / "post-decompile" / "00537c40_IScript__PrintText.c"),
        ("CText__GetStringById", "CConsole__Printf", "0064fda4"),
        failures,
    )

    wave1015_metadata = {row["name"]: row for row in read_tsv_rows(WAVE1015 / "metadata.tsv")}
    for name in ("CMessage__ctor_base", "CMessage__scalar_deleting_dtor", "CMessage__dtor_base"):
        require(name in wave1015_metadata, f"missing Wave1015 metadata row {name}", failures)
    require_tokens(
        "Wave1015 CMessage ctor comment",
        wave1015_metadata["CMessage__ctor_base"]["comment"],
        ("queued CMessage", "WcsLen", "queue_sort_key"),
        failures,
    )

    wave584_backup = read_json(WAVE584 / "wave584_backup_summary.json")
    require(wave584_backup.get("destinationRoot") == WAVE584_BACKUP, "Wave584 backup path mismatch", failures)
    require(wave584_backup.get("status") == "PASS", "Wave584 backup status mismatch", failures)
    require(wave584_backup.get("diffCount") == 0, "Wave584 backup diff mismatch", failures)

    wave1015_backup = read_json(WAVE1015 / "backup-summary.json")
    require(wave1015_backup.get("backupPath") == WAVE1015_BACKUP, "Wave1015 backup path mismatch", failures)
    require(wave1015_backup.get("diffCount") == 0, "Wave1015 backup diff mismatch", failures)
    require(wave1015_backup.get("hashDiffCount") == 0, "Wave1015 backup hash diff mismatch", failures)

    wave1074_backup = read_json(WAVE1074 / "backup-summary.json")
    require(wave1074_backup.get("backupPath") == WAVE1074_BACKUP, "Wave1074 backup path mismatch", failures)
    require(wave1074_backup.get("diffCount") == 0, "Wave1074 backup diff mismatch", failures)
    require(wave1074_backup.get("hashDiffCount") == 0, "Wave1074 backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "MissionScript Message/Audio Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static message/audio command-effect schema proof complete, not runtime proof",
        "PlayCharMessage",
        "PlayCharMessageWait",
        "PlayPCharMessage",
        "PlayPCharMessageWait",
        "SwitchMessagesOn",
        "SwitchMessagesOff",
        "AddHelpMessage",
        "PrintText",
        "AddMessage",
        "IScript__PlaySound",
        "IScript__PlaySoundWithCallback",
        "IScript__PlaySoundWithFade",
        "IScript__PlaySoundWithPriority",
        "IScript__PlaySoundWithFadeAndPriority",
        "IScript__PrintText",
        "CMessage__ctor_base",
        "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
        "CMessageBox__StartVoiceOrFallbackTextReveal",
        "1365 PlayCharMessage",
        "7 AddHelpMessage",
        "1553 detailed message rows",
        "11 speakers",
        "499 unique message tokens",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        WAVE1219_BACKUP,
    )
    for path in (PROOF, LORE_PROOF, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    front_door_docs = (
        CONTRACT,
        PROOF_PLAN,
        BACKLOG,
        LORE_BACKLOG,
        MAPPED,
        LORE_MAPPED,
        BIN_INDEX,
        LORE_BIN_INDEX,
        RE_INDEX,
        LORE_RE_INDEX,
        ISCRIPT_DOC,
        LORE_ISCRIPT_DOC,
        MESSAGEBOX_DOC,
        LORE_MESSAGEBOX_DOC,
        MESSAGES_DOC,
        MSL_SCRIPTING,
        MSL_COMMANDS,
    )
    for path in front_door_docs:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Message/Audio Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing message/audio proof token: {token}", failures)
        check_no_bad_tokens(path, failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_message_audio_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-message-audio-command-effect-static")
    require(actual_script == expected_script, "package script mismatch", failures)

    progress = read_json(PROGRESS)
    require(progress["functionQuality"]["commentedFunctions"] == 6411, "static progress commented count mismatch", failures)
    current_risk = progress["post100Reaudit"]["currentRiskRank"]
    require(current_risk["focusedReviewed"] == 1179, "current-risk progress mismatch", failures)
    require(current_risk["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining count mismatch", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_schema(failures)
    check_artifacts(failures)
    check_docs(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate existing artifacts")
    parser.add_argument("--write-schema", action="store_true", help="write generated schema JSON artifacts")
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
            print("MissionScript message/audio command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript message/audio command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
