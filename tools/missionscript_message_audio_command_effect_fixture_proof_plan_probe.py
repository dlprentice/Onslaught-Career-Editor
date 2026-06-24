#!/usr/bin/env python3
"""Validate MissionScript message/audio deterministic fixture proof artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-fixture-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_message_audio_command_effect_fixture_proof_plan_2026-06-09.md"

PREVIOUS_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json"
MESSAGE_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect.v1.json"
ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
FIXTURE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
ISCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_ISCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Message/Audio Command-Effect Fixture Proof Plan"
PREVIOUS_SLICE = "MissionScript Objective/Outcome Command-Effect Fixture Proof Plan"
NEXT_SLICE = "MissionScript HUD / Display Command-Effect Fixture Proof Plan"
HUD_DISPLAY_FIXTURE_SLICE = "MissionScript HUD / Display Command-Effect Fixture Proof Plan"
THING_VALUE_FIXTURE_SLICE = "MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan"
PLAYER_STATE_FIXTURE_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-message-audio-command-effect-fixture-proof-plan-complete-static-message-audio-console-effect-table-not-runtime-proof"
PREVIOUS_STATUS = "missionscript-objective-outcome-command-effect-fixture-proof-plan-complete-static-objective-outcome-effect-table-not-runtime-proof"

DESCRIPTOR_ORDER = (
    "PlaySample",
    "PrintText",
    "AddMessage",
    "PlayCharMessage",
    "HighlightHudPart",
    "UnHighlightHudPart",
    "PlayCharMessageWait",
    "PlayPCharMessage",
    "PlayPCharMessageWait",
    "SwitchMessagesOn",
    "SwitchMessagesOff",
    "AddHelpMessage",
)
DESCRIPTOR_INDICES = (9, 15, 16, 27, 33, 34, 35, 89, 90, 111, 112, 117)

MESSAGE_QUEUE_CASE_SEEDS = {
    "IScript__PlaySound": {
        "id": "PlaySound-text-100-duration-1250ms",
        "textIds": [100],
        "floatSeeds": [1.25],
        "prioritySeed": None,
        "callbackContext": False,
        "fadeEvent": False,
    },
    "IScript__PlaySoundWithCallback": {
        "id": "PlaySoundWithCallback-text-101-102-duration-2000ms",
        "textIds": [101, 102],
        "floatSeeds": [2.0],
        "prioritySeed": None,
        "callbackContext": True,
        "fadeEvent": False,
    },
    "IScript__PlaySoundWithFade": {
        "id": "PlaySoundWithFade-text-103-duration-3000ms",
        "textIds": [103],
        "floatSeeds": [3.0],
        "prioritySeed": None,
        "callbackContext": False,
        "fadeEvent": True,
    },
    "IScript__PlaySoundWithPriority": {
        "id": "PlaySoundWithPriority-text-104-105-duration-4000ms-priority-7",
        "textIds": [104, 105],
        "floatSeeds": [4.0],
        "prioritySeed": 7,
        "callbackContext": False,
        "fadeEvent": False,
    },
    "IScript__PlaySoundWithFadeAndPriority": {
        "id": "PlaySoundWithFadeAndPriority-text-106-107-duration-5000ms-priority-8",
        "textIds": [106, 107],
        "floatSeeds": [5.0],
        "prioritySeed": 8,
        "callbackContext": False,
        "fadeEvent": True,
    },
}

CONSOLE_TEXT_CASE = {
    "id": "PrintText-text-300-console-wide-string",
    "command": "PrintText",
    "textIdSeed": 300,
    "expectedLookup": "CText__GetStringById",
    "expectedSink": "CConsole__Printf",
    "expectedFormatToken": "%w",
}

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "originalExecutableMutation",
    "copiedFileMutation",
    "sourceBaselineRead",
    "privateArtifactMaterialized",
    "saveSynthesis",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeMessageDisplayProven",
    "runtimeVoicePlaybackProven",
    "runtimeAudioPlaybackProven",
    "runtimeHudOutputProven",
    "runtimeQueueOrderingProven",
    "runtimeConsoleOutputProven",
    "runtimeTextLookupProven",
    "runtimeSpeakerRoutingProven",
    "runtimeSubtitleTimingProven",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "sourceSelectionObserved",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rebuildImplementation",
    "exactCommandDescriptorLayoutProven",
    "exactCommandArityProven",
    "exactArgumentTypeSchemaProven",
    "exactCMessageLayoutProven",
    "exactCMessageBoxLayoutProven",
    "exactTextCatalogLayoutProven",
    "exactAudioResourceMappingProven",
    "messageQueueCapacityProven",
    "messagePriorityOrderingProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeMessageDisplayRows",
    "runtimeMessageRows",
    "runtimeAudioRows",
    "runtimeVoiceRows",
    "runtimeHudRows",
    "runtimeConsoleRows",
    "runtimeQueueRows",
    "runtimeTextLookupRows",
    "runtimeSpeakerRows",
    "runtimeSubtitleRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "sourceObservedRows",
    "sourceRuntimeObservationRows",
    "sourceRowStatusChangedCount",
    "newLaunchRows",
    "captureRows",
    "ocrRows",
    "rawDialogueRows",
    "visibleTextExcerptRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "copiedFileMutationRows",
    "sourceBaselineReadRows",
    "privateArtifactRows",
    "rebuildImplementationRows",
    "godotProjectRows",
    "beProcessesAfterFixture",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "subagent artifact path"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framesha256|framebytelength"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime message display proven",
    "runtime voice playback proven",
    "runtime audio playback proven",
    "runtime hud output proven",
    "runtime queue ordering proven",
    "runtime console output proven",
    "runtime text lookup proven",
    "runtime speaker routing proven",
    "runtime subtitle timing proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact cmessage layout proven",
    "exact cmessagebox layout proven",
    "exact text catalog layout proven",
    "exact audio resource mapping proven",
    "message queue capacity proven",
    "message priority ordering proven",
    "private-frame review complete",
    "source-selection observation complete",
    "visual qa complete",
    "godot parity proven",
    "ghidra mutation complete",
    "executable patching behavior proven",
    "product ui behavior proven",
    "rebuild implementation complete",
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


def no_bea_process_running() -> bool:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "if (Get-Process -Name BEA -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def message_queue_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    by_name = {row["name"]: row for row in static_schema["messageQueueHandlers"]}
    cases: list[dict[str, Any]] = []
    for name, seed in MESSAGE_QUEUE_CASE_SEEDS.items():
        handler = by_name[name]
        cases.append(
            {
                "id": seed["id"],
                "handlerAnchor": f"{handler['address']} {handler['name']}",
                "handlerSummary": handler["summary"],
                "textIdSeeds": seed["textIds"],
                "floatSeeds": seed["floatSeeds"],
                "prioritySeed": seed["prioritySeed"],
                "callbackContext": seed["callbackContext"],
                "fadeEvent0x7d1": seed["fadeEvent"],
                "expectedObject": "CMessage",
                "expectedQueueSink": "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
                "expectedQueueGlobal": "DAT_008a9d84",
                "finiteFixtureOnly": True,
                "runtimeMessageDisplayProven": False,
                "runtimeVoicePlaybackProven": False,
                "runtimeAudioPlaybackProven": False,
            }
        )
    return cases


def descriptor_context_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    records = static_schema["descriptorRecords"]
    return [
        {
            "command": command,
            "descriptorIndex": records[command]["index"],
            "recordAddress": records[command]["recordAddress"],
            "observedNameSymbol": records[command]["observedNameSymbol"],
            "rawEntryValue": records[command]["rawEntryValue"],
            "descriptorContextOnly": True,
            "exactDescriptorLayoutProven": False,
            "exactCommandArityProven": False,
            "exactArgumentTypeSchemaProven": False,
        }
        for command in DESCRIPTOR_ORDER
    ]


def build_schema() -> dict[str, Any]:
    previous = read_json(PREVIOUS_FIXTURE)
    static_schema = read_json(MESSAGE_STATIC)
    rollup = read_json(ROLLUP)
    fixture_selection = read_json(FIXTURE_SELECTION)
    queue_cases = message_queue_cases(static_schema)
    descriptor_cases = descriptor_context_cases(static_schema)
    console_case = {
        **CONSOLE_TEXT_CASE,
        "handlerAnchor": f"{static_schema['consoleTextHandler']['address']} {static_schema['consoleTextHandler']['name']}",
        "descriptorEvidence": static_schema["consoleTextHandler"]["descriptorEvidence"],
        "bodyEvidence": static_schema["consoleTextHandler"]["bodyEvidence"],
        "finiteFixtureOnly": True,
        "runtimeConsoleOutputProven": False,
        "runtimeTextLookupProven": False,
    }
    return {
        "schemaVersion": "missionscript-message-audio-command-effect-fixture-proof-plan.v1",
        "status": "PASS",
        "missionScriptMessageAudioCommandEffectFixtureProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "message-audio-console",
        "selectedFixturePath": "message-audio-queue-console-effect-table",
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "fixtureAccounting": {
            "sourceSchemaCount": 4,
            "corpusSourceCount": 3,
            "descriptorIndices": list(DESCRIPTOR_INDICES),
            "descriptorRecordCount": len(static_schema["descriptorRecords"]),
            "descriptorContextCaseCount": len(descriptor_cases),
            "messageQueueHandlerCount": len(static_schema["messageQueueHandlers"]),
            "consoleTextHandlerCount": 1,
            "messageBoxContextCount": len(static_schema["messageBoxContext"]),
            "handlerAnchorCount": len(static_schema["messageQueueHandlers"]) + 1,
            "plannedMessageQueueCaseCount": len(queue_cases),
            "plannedConsoleTextCaseCount": 1,
            "deterministicFixtureCaseCount": len(queue_cases) + 1,
            "textIdSeedCount": sum(len(case["textIdSeeds"]) for case in queue_cases) + 1,
            "floatSeedCount": sum(len(case["floatSeeds"]) for case in queue_cases),
            "prioritySeedCount": sum(1 for case in queue_cases if case["prioritySeed"] is not None),
            "fadeEventCaseCount": sum(1 for case in queue_cases if case["fadeEvent0x7d1"]),
            "callbackContextCaseCount": sum(1 for case in queue_cases if case["callbackContext"]),
            "effectAssertionCount": len(queue_cases) * 3 + 2,
            "wave584MetadataRows": static_schema["evidenceCounts"]["wave584MetadataRows"],
            "wave584InstructionRows": static_schema["evidenceCounts"]["wave584InstructionRows"],
            "wave584VtableRows": static_schema["evidenceCounts"]["wave584VtableRows"],
            "wave1015MetadataRows": static_schema["evidenceCounts"]["wave1015MetadataRows"],
            "wave1015ContextXrefRows": static_schema["evidenceCounts"]["wave1015ContextXrefRows"],
            "wave1015ContextInstructionRows": static_schema["evidenceCounts"]["wave1015ContextInstructionRows"],
            "wave1074MetadataRows": static_schema["evidenceCounts"]["wave1074MetadataRows"],
            "wave1074InstructionRows": static_schema["evidenceCounts"]["wave1074InstructionRows"],
            "messageCorpusLevelRows": static_schema["missionMessageSummary"]["levelRows"],
            "messageCorpusPlayCharMessage": static_schema["missionMessageSummary"]["playCharMessage"],
            "messageCorpusAddHelpMessage": static_schema["missionMessageSummary"]["addHelpMessage"],
            "messageCorpusLevelLostFamily": static_schema["missionMessageSummary"]["levelLostFamily"],
            "messageCorpusLevelWonFamily": static_schema["missionMessageSummary"]["levelWonFamily"],
            "messageCallsiteDetailedRows": static_schema["missionMessageCallsites"]["detailedRows"],
            "messageCallsiteSpeakerCount": static_schema["missionMessageCallsites"]["speakerCount"],
            "messageCallsiteUniqueTokenCount": static_schema["missionMessageCallsites"]["uniqueTokenCount"],
            "rollupCommandFamilyCount": rollup["rollupAccounting"]["commandFamilyCount"],
            "fixtureSelectionOriginalRank": next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "message-audio-console"),
            "previousFixtureStatus": previous["missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
        },
        "sourceEvidence": {
            "previousFixture": {
                "schema": "reverse-engineering/binary-analysis/missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json",
                "status": previous["missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus"],
                "selectedNextSlice": previous["selectedNextSlice"],
            },
            "messageAudioStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-message-audio-command-effect.v1.json",
                "status": static_schema["status"],
                "descriptorIndices": list(DESCRIPTOR_INDICES),
                "messageQueueHandlers": [row["name"] for row in static_schema["messageQueueHandlers"]],
                "consoleTextHandler": static_schema["consoleTextHandler"]["name"],
                "messageBoxContext": static_schema["messageBoxContext"],
                "boundary": "static descriptor/body/corpus bridge only; runtime message/audio behavior remains unproven",
            },
            "rollup": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-rebuild-interface-rollup.v1.json",
                "commandFamilyCount": rollup["rollupAccounting"]["commandFamilyCount"],
                "descriptorRecordCount": rollup["rollupAccounting"]["descriptorRecordCount"],
            },
            "fixtureSelection": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-fixture-selection.v1.json",
                "originalRank": next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "message-audio-console"),
                "originalDecision": next(row["decision"] for row in fixture_selection["candidateRanking"] if row["family"] == "message-audio-console"),
            },
        },
        "fixtureModel": {
            "messageQueueEffectModel": "finite text/float/priority seeds map to static CMessage construction and CMessageBox enqueue skeletons",
            "consoleTextEffectModel": "finite text id seed maps to CText lookup and CConsole wide-string sink skeleton",
            "descriptorContextModel": "descriptor names and raw entries remain context-only because exact descriptor layout and handler binding are unproven",
            "selectedRuntimeCommands": [
                "PlayCharMessage",
                "PlayCharMessageWait",
                "PlayPCharMessage",
                "PlayPCharMessageWait",
                "SwitchMessagesOn",
                "SwitchMessagesOff",
                "AddHelpMessage",
                "PrintText",
                "AddMessage",
            ],
            "excludedCases": [
                "runtime voice/audio playback",
                "runtime HUD display",
                "runtime queue ordering",
                "runtime speaker routing",
                "text catalog resolution",
                "audio resource mapping",
                "message timing and queue capacity",
            ],
        },
        "deterministicMessageQueueCases": queue_cases,
        "deterministicConsoleTextCases": [console_case],
        "descriptorContextCases": descriptor_cases,
        "deferredProofGate": {
            "selectedNextSlice": NEXT_SLICE,
            "runtimeExecution": False,
            "beLaunch": False,
            "sourceBaselineRead": False,
            "privateArtifactMaterialized": False,
            "copiedFileMutation": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
            "requiresSeparateProofForRuntimeMessageDisplay": True,
            "requiresSeparateProofForRuntimeVoiceAudio": True,
            "requiresSeparateProofForRuntimeHudOutput": True,
        },
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "five finite message queue fixture cases tied to saved static Wave584 handlers",
                "one finite console text fixture case tied to saved Wave1074 handler evidence",
                "twelve descriptor context rows tied to the message/audio static schema",
                "message corpus and MessageBox lifecycle counts are preserved as static reference counts",
                "the message/audio fixture table is consolidated without runtime, Ghidra, patch, Godot, product UI, or rebuild claims",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime message display",
                "runtime voice playback",
                "runtime audio playback",
                "runtime HUD output",
                "runtime queue ordering",
                "runtime console output",
                "runtime text lookup",
                "runtime speaker routing",
                "runtime subtitle timing",
                "live loose-MSL loading",
                "packed-resource script selection",
                "exact command descriptor layout",
                "exact command arity",
                "exact argument type schema",
                "exact CMessage layout",
                "exact CMessageBox layout",
                "exact text catalog layout",
                "exact audio resource mapping",
                "message queue capacity",
                "message priority ordering",
                "source-selection observation",
                "private-frame review",
                "visual QA",
                "Godot parity",
                "Ghidra mutation",
                "executable patching",
                "product UI behavior",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
    }


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def assert_schema(actual: dict[str, Any], failures: list[str]) -> None:
    expected = build_schema()
    require(actual == expected, "schema is not regenerated from current message/audio fixture evidence", failures)
    accounting = actual["fixtureAccounting"]
    require(accounting["descriptorIndices"] == list(DESCRIPTOR_INDICES), "descriptor index list mismatch", failures)
    require(accounting["descriptorRecordCount"] == 12, "descriptor record count mismatch", failures)
    require(accounting["descriptorContextCaseCount"] == 12, "descriptor context count mismatch", failures)
    require(accounting["messageQueueHandlerCount"] == 5, "message queue handler count mismatch", failures)
    require(accounting["consoleTextHandlerCount"] == 1, "console handler count mismatch", failures)
    require(accounting["messageBoxContextCount"] == 6, "messagebox context count mismatch", failures)
    require(accounting["handlerAnchorCount"] == 6, "handler anchor count mismatch", failures)
    require(accounting["plannedMessageQueueCaseCount"] == 5, "message queue case count mismatch", failures)
    require(accounting["plannedConsoleTextCaseCount"] == 1, "console case count mismatch", failures)
    require(accounting["deterministicFixtureCaseCount"] == 6, "deterministic fixture count mismatch", failures)
    require(accounting["textIdSeedCount"] == 9, "text id seed count mismatch", failures)
    require(accounting["floatSeedCount"] == 5, "float seed count mismatch", failures)
    require(accounting["prioritySeedCount"] == 2, "priority seed count mismatch", failures)
    require(accounting["fadeEventCaseCount"] == 2, "fade event case count mismatch", failures)
    require(accounting["callbackContextCaseCount"] == 1, "callback context case count mismatch", failures)
    require(accounting["effectAssertionCount"] == 17, "effect assertion count mismatch", failures)
    require(accounting["wave584MetadataRows"] == 11, "wave584 metadata rows mismatch", failures)
    require(accounting["wave1015MetadataRows"] == 7, "wave1015 metadata rows mismatch", failures)
    require(accounting["wave1074MetadataRows"] == 1, "wave1074 metadata rows mismatch", failures)
    require(accounting["messageCorpusLevelRows"] == 67, "message corpus level rows mismatch", failures)
    require(accounting["messageCorpusPlayCharMessage"] == 1365, "PlayCharMessage count mismatch", failures)
    require(accounting["messageCorpusAddHelpMessage"] == 7, "AddHelpMessage count mismatch", failures)
    require(accounting["messageCorpusLevelLostFamily"] == 110, "LevelLost family mismatch", failures)
    require(accounting["messageCorpusLevelWonFamily"] == 71, "LevelWon family mismatch", failures)
    require(accounting["messageCallsiteDetailedRows"] == 1553, "message detailed rows mismatch", failures)
    require(accounting["messageCallsiteSpeakerCount"] == 11, "speaker count mismatch", failures)
    require(accounting["messageCallsiteUniqueTokenCount"] == 499, "unique token count mismatch", failures)
    require(accounting["fixtureSelectionOriginalRank"] == 6, "fixture selection original rank mismatch", failures)
    require(accounting["previousFixtureStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    for case in actual["deterministicMessageQueueCases"]:
        require(case["expectedObject"] == "CMessage", f"message object mismatch: {case['id']}", failures)
        require(case["expectedQueueSink"] == "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", f"queue sink mismatch: {case['id']}", failures)
        require(case["expectedQueueGlobal"] == "DAT_008a9d84", f"queue global mismatch: {case['id']}", failures)
        require(case["finiteFixtureOnly"] is True, f"finite guard mismatch: {case['id']}", failures)
        require(case["runtimeMessageDisplayProven"] is False, f"message runtime guard mismatch: {case['id']}", failures)
        require(case["runtimeVoicePlaybackProven"] is False, f"voice runtime guard mismatch: {case['id']}", failures)
        require(case["runtimeAudioPlaybackProven"] is False, f"audio runtime guard mismatch: {case['id']}", failures)
    console = actual["deterministicConsoleTextCases"][0]
    require(console["textIdSeed"] == 300, "console text id seed mismatch", failures)
    require(console["expectedLookup"] == "CText__GetStringById", "console lookup mismatch", failures)
    require(console["expectedSink"] == "CConsole__Printf", "console sink mismatch", failures)
    require(console["expectedFormatToken"] == "%w", "console format mismatch", failures)
    for case in actual["descriptorContextCases"]:
        require(case["descriptorContextOnly"] is True, f"descriptor context guard mismatch: {case['command']}", failures)
        require(case["exactDescriptorLayoutProven"] is False, f"descriptor layout guard mismatch: {case['command']}", failures)

    guards = actual["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    assert_schema(result, failures)
    require(lore == result, "lore schema mirror mismatch", failures)
    check_no_bad_public_content(RESULT, failures)


def check_source_prerequisites(failures: list[str]) -> None:
    previous = read_json(PREVIOUS_FIXTURE)
    static_schema = read_json(MESSAGE_STATIC)
    fixture_selection = read_json(FIXTURE_SELECTION)
    require(previous["missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(previous["selectedNextSlice"] == THIS_SLICE, "previous fixture selected next slice mismatch", failures)
    require(static_schema["status"] == "PASS", "message/audio static schema status mismatch", failures)
    require(tuple(static_schema["descriptorRecords"].keys()) == DESCRIPTOR_ORDER, "descriptor key order mismatch", failures)
    require(tuple(static_schema["descriptorRecords"][key]["index"] for key in static_schema["descriptorRecords"]) == DESCRIPTOR_INDICES, "descriptor index order mismatch", failures)
    require(len(static_schema["messageQueueHandlers"]) == 5, "message queue handler prerequisite mismatch", failures)
    require(static_schema["consoleTextHandler"]["name"] == "IScript__PrintText", "console text handler mismatch", failures)
    require(len(static_schema["messageBoxContext"]) == 6, "messagebox context prerequisite mismatch", failures)
    require(static_schema["missionMessageSummary"]["levelRows"] == 67, "message summary row mismatch", failures)
    require(static_schema["missionMessageCallsites"]["detailedRows"] == 1553, "message detailed row mismatch", failures)
    require(next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "message-audio-console") == 6, "fixture selection rank mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-message-audio-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptMessageAudioCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=message-audio-console",
        "selectedFixturePath=message-audio-queue-console-effect-table",
        "descriptorIndices=9/15/16/27/33/34/35/89/90/111/112/117",
        "descriptorRecordCount=12",
        "descriptorContextCaseCount=12",
        "messageQueueHandlerCount=5",
        "consoleTextHandlerCount=1",
        "messageBoxContextCount=6",
        "handlerAnchorCount=6",
        "plannedMessageQueueCaseCount=5",
        "plannedConsoleTextCaseCount=1",
        "deterministicFixtureCaseCount=6",
        "textIdSeedCount=9",
        "floatSeedCount=5",
        "prioritySeedCount=2",
        "fadeEventCaseCount=2",
        "callbackContextCaseCount=1",
        "effectAssertionCount=17",
        "wave584MetadataRows=11",
        "wave1015MetadataRows=7",
        "wave1074MetadataRows=1",
        "messageCorpusLevelRows=67",
        "messageCorpusPlayCharMessage=1365",
        "messageCorpusAddHelpMessage=7",
        "messageCorpusLevelLostFamily=110",
        "messageCorpusLevelWonFamily=71",
        "messageCallsiteDetailedRows=1553",
        "messageCallsiteSpeakerCount=11",
        "messageCallsiteUniqueTokenCount=499",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "0x00537410 IScript__PlaySound",
        "0x00537500 IScript__PlaySoundWithCallback",
        "0x005375f0 IScript__PlaySoundWithFade",
        "0x005377e0 IScript__PlaySoundWithPriority",
        "0x005378e0 IScript__PlaySoundWithFadeAndPriority",
        "0x00537c40 IScript__PrintText",
        "CMessage__ctor_base",
        "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
        "CMessageBox__StartVoiceOrFallbackTextReveal",
        "CMessageBox__AdvanceRevealAndScheduleNextTick",
        "CMessageBox__StopVoicePlaybackIfNotInCutscene",
        "CMessageBox__RenderOverlay",
        "DAT_008a9d84",
        "CText__GetStringById",
        "CConsole__Printf",
        "runtimeExecution=false",
        "beLaunch=false",
        "sourceBaselineRead=false",
        "privateArtifactMaterialized=false",
        "copiedFileMutation=false",
        "ghidraMutation=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeMessageRows=0",
        "runtimeAudioRows=0",
        "beProcessesAfterFixture=0",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "missionscript-message-audio-command-effect-fixture-proof-plan.md",
        "missionscript-message-audio-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptMessageAudioCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=message-audio-console",
        "selectedNextSlice=MissionScript HUD / Display Command-Effect Fixture Proof Plan",
        "plannedMessageQueueCaseCount=5",
        "plannedConsoleTextCaseCount=1",
        "deterministicFixtureCaseCount=6",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, ISCRIPT_CONTRACT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks message/audio fixture active",
            failures,
        )

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed message/audio fixture lane", failures)
    require(
        f"Completed {HUD_DISPLAY_FIXTURE_SLICE}" in backlog,
        "backlog missing completed HUD/display follow-up lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog,
        "backlog still marks HUD/display follow-up lane active",
        failures,
    )
    require(
        f"Completed {THING_VALUE_FIXTURE_SLICE}" in backlog
        or f"The selected active static-to-proof slice is {THING_VALUE_FIXTURE_SLICE}. Status: selected" in backlog,
        "backlog missing active-or-completed Thing Value / Engine Helper follow-up lane",
        failures,
    )
    require(
        f"Completed {COMPLETION_ROLLUP_SLICE}" in backlog,
        "backlog missing completed fixture-family completion rollup follow-up lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {COMPLETION_ROLLUP_SLICE}. Status: selected" not in backlog,
        "backlog still marks fixture-family completion rollup follow-up lane active",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {POST_ROLLUP_NEXT_SLICE}. Status: selected" in backlog,
        "backlog missing active post-rollup selection refresh lane",
        failures,
    )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (ISCRIPT_CONTRACT, LORE_ISCRIPT_CONTRACT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-message-audio-command-effect-fixture-proof-plan")
        == r"py -3 tools\missionscript_message_audio_command_effect_fixture_proof_plan_probe.py --check",
        "missing package message/audio fixture proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-message-audio-command-effect-static",
        "test:missionscript-objective-outcome-command-effect-fixture-proof-plan",
        "test:static-to-proof-transition-backlog",
    ):
        require(script in scripts, f"missing source package script: {script}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-schema", action="store_true")
    args = parser.parse_args()

    if args.write_schema:
        schema = build_schema()
        write_json(RESULT, schema)
        write_json(LORE_RESULT, schema)
        print(f"Wrote {RESULT.relative_to(ROOT)}")
        print(f"Wrote {LORE_RESULT.relative_to(ROOT)}")

    if args.check or not args.write_schema:
        failures: list[str] = []
        check_source_prerequisites(failures)
        check_result(failures)
        check_docs(failures)
        check_package(failures)
        require(no_bea_process_running(), "BEA.exe process is running after message/audio fixture proof", failures)
        if failures:
            print("MissionScript message/audio command-effect fixture proof-plan probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript message/audio command-effect fixture proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
