#!/usr/bin/env python3
"""Validate MissionScript thing-value/engine-helper deterministic fixture proof artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_thing_value_engine_helper_command_effect_fixture_proof_plan_2026-06-09.md"

PREVIOUS_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-fixture-proof-plan.v1.json"
THING_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect.v1.json"
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

THIS_SLICE = "MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan"
PREVIOUS_SLICE = "MissionScript HUD / Display Command-Effect Fixture Proof Plan"
NEXT_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan-complete-static-thing-engine-dispatch-table-not-runtime-proof"
PREVIOUS_STATUS = "missionscript-hud-display-command-effect-fixture-proof-plan-complete-static-hud-variable-display-effect-table-not-runtime-proof"

DESCRIPTOR_ORDER = (
    "SetWindVector",
    "DisableWeapon",
    "EnableFlightMode",
    "TeleportOrientation",
    "DisableSpawner",
    "SetName",
)
DESCRIPTOR_INDICES = (41, 98, 99, 138, 140, 141)
EXPECTED_DIRECT_COUNTS = {
    "SetWindVector": 0,
    "DisableWeapon": 15,
    "EnableFlightMode": 1,
    "TeleportOrientation": 5,
    "DisableSpawner": 2,
    "SetName": 4,
}
DISPATCH_CASES = {
    "SetWindVector": {
        "handlerAddress": "0x00535560",
        "handlerName": "IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
        "argumentGetterSlot": "+0x30",
        "dispatchKind": "unit-helper",
        "dispatchTarget": "CUnit__SetFactionForHierarchy",
    },
    "DisableWeapon": {
        "handlerAddress": "0x00534fb0",
        "handlerName": "IScript__SetThingValueViaVFunc198_FromArg",
        "argumentGetterSlot": "+0x38",
        "dispatchKind": "thing-vfunc-slot",
        "dispatchTarget": "+0x198",
    },
    "EnableFlightMode": {
        "handlerAddress": "0x00534fe0",
        "handlerName": "IScript__SetThingValueViaVFunc19C_FromArg",
        "argumentGetterSlot": "+0x38",
        "dispatchKind": "thing-vfunc-slot",
        "dispatchTarget": "+0x19c",
    },
    "TeleportOrientation": {
        "handlerAddress": "0x00535530",
        "handlerName": "IScript__SetThingFloatViaVFunc1C8_FromArg",
        "argumentGetterSlot": "+0x34",
        "dispatchKind": "thing-vfunc-slot",
        "dispatchTarget": "+0x1c8",
    },
    "DisableSpawner": {
        "handlerAddress": "0x00535010",
        "handlerName": "IScript__SetThingValueViaEngineHelper4FE390_FromArg",
        "argumentGetterSlot": "+0x38",
        "dispatchKind": "engine-helper",
        "dispatchTarget": "CEngine__EnableThingByNameFlag",
    },
    "SetName": {
        "handlerAddress": "0x00535040",
        "handlerName": "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg",
        "argumentGetterSlot": "+0x38",
        "dispatchKind": "engine-helper",
        "dispatchTarget": "CEngine__DisableThingByNameFlag",
    },
}

FALSE_GUARDS = (
    "programFilesInputUsed",
    "sourcePathsPublic",
    "rawMslRowsPublic",
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
    "runtimeThingValueEngineHelperBehaviorProven",
    "runtimeThingBehaviorProven",
    "runtimeDisableWeaponBehaviorProven",
    "runtimeEnableFlightModeBehaviorProven",
    "runtimeDisableSpawnerBehaviorProven",
    "runtimeSetNameBehaviorProven",
    "runtimeTeleportOrientationBehaviorProven",
    "runtimeSetWindVectorBehaviorProven",
    "runtimeObjectIdentityProven",
    "runtimeObjectLookupByNameProven",
    "runtimeThingStateMutationProven",
    "runtimeWeaponStateProven",
    "runtimeFlightModeProven",
    "runtimeSpawnerBehaviorProven",
    "runtimeThingNameMutationProven",
    "runtimeThingOrientationProven",
    "runtimeWindVectorBehaviorProven",
    "runtimeUnitFactionBehaviorProven",
    "runtimeNameLookupSideEffectsProven",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
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
    "exactThingLayoutProven",
    "exactThingVfuncSemanticsProven",
    "exactUnitFactionEnumProven",
    "exactSourceBodyIdentityProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeThingBehaviorRows",
    "runtimeDisableWeaponRows",
    "runtimeEnableFlightModeRows",
    "runtimeDisableSpawnerRows",
    "runtimeSetNameRows",
    "runtimeTeleportOrientationRows",
    "runtimeSetWindVectorRows",
    "runtimeObjectIdentityRows",
    "runtimeObjectLookupRows",
    "runtimeWeaponStateRows",
    "runtimeFlightModeRows",
    "runtimeSpawnerRows",
    "runtimeThingNameRows",
    "runtimeThingOrientationRows",
    "runtimeWindVectorRows",
    "runtimeUnitFactionRows",
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
    (re.compile(r"(?i)game[\\/]+data[\\/]+missionscripts"), "private loose MSL row path"),
    (re.compile(r"(?i)sampleRows"), "raw private sample row field"),
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
    "runtime thing behavior proven",
    "runtime disableweapon behavior proven",
    "runtime enableflightmode behavior proven",
    "runtime disablespawner behavior proven",
    "runtime setname behavior proven",
    "runtime teleportorientation behavior proven",
    "runtime setwindvector behavior proven",
    "runtime object identity proven",
    "runtime object lookup proven",
    "runtime thing-state mutation proven",
    "runtime weapon state proven",
    "runtime flight mode proven",
    "runtime spawner behavior proven",
    "runtime thing name mutation proven",
    "runtime thing orientation proven",
    "runtime wind vector proven",
    "runtime unit faction proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact thing layout proven",
    "exact thing vfunc semantics proven",
    "exact unit faction enum proven",
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


def fixture_selection_row(fixture_selection: dict[str, Any]) -> dict[str, Any]:
    return next(row for row in fixture_selection["candidateRanking"] if row["family"] == "thing-value-engine-helper")


def descriptor_context_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    records = static_schema["descriptorRecords"]
    return [
        {
            "command": command,
            "descriptorIndex": records[command]["index"],
            "recordAddress": records[command]["recordAddress"],
            "observedNameSymbol": records[command]["observedNameSymbol"],
            "rawEntryValue": records[command]["rawEntryValue"],
            "postWave582HandlerName": records[command]["postWave582HandlerName"],
            "rawShapeValues": records[command]["rawShapeValues"],
            "descriptorContextOnly": True,
            "runtimeCommandEffectProven": False,
            "exactDescriptorLayoutProven": False,
            "exactCommandArityProven": False,
        }
        for command in DESCRIPTOR_ORDER
    ]


def deterministic_dispatch_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    records = static_schema["descriptorRecords"]
    usage = static_schema["looseMslUsage"]["directNonCommentCounts"]
    cases: list[dict[str, Any]] = []
    for command in DESCRIPTOR_ORDER:
        dispatch = DISPATCH_CASES[command]
        record = records[command]
        cases.append(
            {
                "id": f"{command}-{dispatch['dispatchKind']}-{dispatch['dispatchTarget']}-static-dispatch",
                "command": command,
                "descriptorIndex": record["index"],
                "handlerAddress": dispatch["handlerAddress"],
                "handlerName": dispatch["handlerName"],
                "argumentGetterSlot": dispatch["argumentGetterSlot"],
                "dispatchKind": dispatch["dispatchKind"],
                "dispatchTarget": dispatch["dispatchTarget"],
                "guard": static_schema["dispatchContext"]["guard"],
                "directNonCommentLooseMslRows": usage[command],
                "staticDispatchOnly": True,
                "runtimeCommandEffectProven": False,
                "runtimeObjectIdentityProven": False,
                "exactThingVfuncSemanticsProven": False,
                "exactThingLayoutProven": False,
            }
        )
    return cases


def build_schema() -> dict[str, Any]:
    previous = read_json(PREVIOUS_FIXTURE)
    static_schema = read_json(THING_STATIC)
    fixture_selection = read_json(FIXTURE_SELECTION)
    selection = fixture_selection_row(fixture_selection)
    descriptor_cases = descriptor_context_cases(static_schema)
    dispatch_cases = deterministic_dispatch_cases(static_schema)
    usage = static_schema["looseMslUsage"]["directNonCommentCounts"]
    evidence = static_schema["evidenceCounts"]
    return {
        "schemaVersion": "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1",
        "status": "PASS",
        "missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "thing-value-engine-helper",
        "selectedFixturePath": "thing-vfunc-engine-unit-helper-dispatch-table",
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "fixtureAccounting": {
            "sourceSchemaCount": 3,
            "descriptorIndices": list(DESCRIPTOR_INDICES),
            "descriptorRecordCount": len(static_schema["descriptorRecords"]),
            "descriptorContextCaseCount": len(descriptor_cases),
            "handlerDispatchCaseCount": len(dispatch_cases),
            "thingVfuncDispatchCaseCount": sum(1 for row in dispatch_cases if row["dispatchKind"] == "thing-vfunc-slot"),
            "engineHelperDispatchCaseCount": sum(1 for row in dispatch_cases if row["dispatchKind"] == "engine-helper"),
            "unitHelperDispatchCaseCount": sum(1 for row in dispatch_cases if row["dispatchKind"] == "unit-helper"),
            "getterSlotCount": len(static_schema["dispatchContext"]["argumentGetterSlots"]),
            "thingVfuncSlotCount": len(static_schema["dispatchContext"]["thingVfuncSlots"]),
            "engineHelperCount": len(static_schema["dispatchContext"]["engineHelpers"]),
            "unitHelperCount": 1,
            "dispatchTargetCount": len(dispatch_cases),
            "deterministicFixtureCaseCount": len(dispatch_cases),
            "totalStaticCommandStepCount": len(dispatch_cases),
            "guardAssertionCount": len(dispatch_cases),
            "getterSlotAssertionCount": len(dispatch_cases),
            "dispatchTargetAssertionCount": len(dispatch_cases),
            "effectAssertionCount": len(dispatch_cases) * 3,
            "directNonCommentLooseMslRows": sum(usage.values()),
            "commandWithCorpusRows": sum(1 for count in usage.values() if count > 0),
            "zeroCorpusCommandCount": sum(1 for count in usage.values() if count == 0),
            "disableWeaponCallRows": usage["DisableWeapon"],
            "enableFlightModeCallRows": usage["EnableFlightMode"],
            "disableSpawnerCallRows": usage["DisableSpawner"],
            "setNameCallRows": usage["SetName"],
            "teleportOrientationCallRows": usage["TeleportOrientation"],
            "setWindVectorCallRows": usage["SetWindVector"],
            "wave582MetadataRows": evidence["wave582MetadataRows"],
            "wave582TagRows": evidence["wave582TagRows"],
            "wave582XrefRows": evidence["wave582XrefRows"],
            "wave582InstructionRows": evidence["wave582InstructionRows"],
            "wave582DecompileRows": evidence["wave582DecompileRows"],
            "wave582VtableRows": evidence["wave582VtableRows"],
            "fixtureSelectionOriginalRank": selection["rank"],
            "fixtureSelectionOriginalDecision": selection["decision"],
            "previousFixtureStatus": previous["missionScriptHudDisplayCommandEffectFixtureProofPlanStatus"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
        },
        "sourceEvidence": {
            "previousFixture": {
                "schema": "reverse-engineering/binary-analysis/missionscript-hud-display-command-effect-fixture-proof-plan.v1.json",
                "status": previous["missionScriptHudDisplayCommandEffectFixtureProofPlanStatus"],
                "selectedNextSlice": previous["selectedNextSlice"],
            },
            "thingValueEngineHelperStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-thing-value-engine-helper-command-effect.v1.json",
                "status": static_schema["status"],
                "descriptorIndices": list(DESCRIPTOR_INDICES),
                "handlers": [
                    {
                        "address": row["address"],
                        "name": row["name"],
                    }
                    for row in static_schema["handlers"]
                ],
                "dispatchContext": {
                    "guard": static_schema["dispatchContext"]["guard"],
                    "argumentGetterSlots": static_schema["dispatchContext"]["argumentGetterSlots"],
                    "thingVfuncSlots": static_schema["dispatchContext"]["thingVfuncSlots"],
                    "engineHelpers": static_schema["dispatchContext"]["engineHelpers"],
                    "unitHelper": static_schema["dispatchContext"]["unitHelper"],
                },
                "looseMslUsageAggregate": {command: usage[command] for command in DESCRIPTOR_ORDER},
                "boundary": "static descriptor/handler/dispatch/corpus bridge only; runtime thing/object/helper behavior remains unproven",
            },
            "fixtureSelection": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-fixture-selection.v1.json",
                "originalRank": selection["rank"],
                "originalDecision": selection["decision"],
            },
        },
        "fixtureModel": {
            "thingDispatchModel": "finite descriptor commands map to static thing-vfunc, engine-helper, or unit-helper dispatch cases",
            "descriptorContextModel": "raw descriptor records remain context-only because exact descriptor layout and runtime effects are unproven",
            "selectedRuntimeCommands": list(DESCRIPTOR_ORDER),
            "excludedCases": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime object identity",
                "runtime object lookup by name",
                "runtime thing-state mutation",
                "live loose-MSL loading",
                "packed-resource script selection",
                "exact thing vfunc semantics",
            ],
        },
        "deterministicDispatchCases": dispatch_cases,
        "descriptorContextCases": descriptor_cases,
        "deferredProofGate": {
            "selectedNextSlice": NEXT_SLICE,
            "runtimeExecution": False,
            "beLaunch": False,
            "sourcePathsPublic": False,
            "rawMslRowsPublic": False,
            "liveLooseMslLoading": False,
            "packedResourceScriptSelectionProven": False,
            "sourceBaselineRead": False,
            "privateArtifactMaterialized": False,
            "copiedFileMutation": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
            "requiresSeparateProofForRuntimeObjectIdentity": True,
            "requiresSeparateProofForRuntimeCommandEffects": True,
            "requiresSeparateProofForExactThingVfuncSemantics": True,
        },
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "six finite static thing-value/engine-helper dispatch fixture cases tied to saved descriptor rows",
                "three thing-vfunc dispatch cases, two engine-helper dispatch cases, and one unit-helper dispatch case",
                "six descriptor context rows tied to the Thing Value / Engine Helper static schema",
                "aggregate command-token counts are preserved without publishing raw loose-MSL sample rows",
                "the fixture table is consolidated without runtime, Ghidra, patch, Godot, product UI, or rebuild claims",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime thing behavior",
                "runtime DisableWeapon behavior",
                "runtime EnableFlightMode behavior",
                "runtime DisableSpawner behavior",
                "runtime SetName behavior",
                "runtime TeleportOrientation behavior",
                "runtime SetWindVector behavior",
                "runtime object identity",
                "runtime object lookup by name",
                "runtime thing-state mutation",
                "live loose-MSL loading",
                "packed-resource script selection",
                "exact command descriptor layout",
                "exact command arity",
                "exact argument type schema",
                "exact thing layout",
                "exact thing vfunc semantics",
                "exact unit faction enum",
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
    require(actual == expected, "schema is not regenerated from current thing-value fixture evidence", failures)
    accounting = actual["fixtureAccounting"]
    require(accounting["descriptorIndices"] == list(DESCRIPTOR_INDICES), "descriptor index list mismatch", failures)
    require(accounting["descriptorRecordCount"] == 6, "descriptor record count mismatch", failures)
    require(accounting["descriptorContextCaseCount"] == 6, "descriptor context count mismatch", failures)
    require(accounting["handlerDispatchCaseCount"] == 6, "handler dispatch count mismatch", failures)
    require(accounting["thingVfuncDispatchCaseCount"] == 3, "thing vfunc dispatch count mismatch", failures)
    require(accounting["engineHelperDispatchCaseCount"] == 2, "engine helper count mismatch", failures)
    require(accounting["unitHelperDispatchCaseCount"] == 1, "unit helper count mismatch", failures)
    require(accounting["getterSlotCount"] == 3, "getter slot count mismatch", failures)
    require(accounting["dispatchTargetCount"] == 6, "dispatch target count mismatch", failures)
    require(accounting["deterministicFixtureCaseCount"] == 6, "deterministic fixture count mismatch", failures)
    require(accounting["totalStaticCommandStepCount"] == 6, "static command step count mismatch", failures)
    require(accounting["effectAssertionCount"] == 18, "effect assertion count mismatch", failures)
    require(accounting["directNonCommentLooseMslRows"] == 27, "loose MSL aggregate count mismatch", failures)
    require(accounting["commandWithCorpusRows"] == 5, "command-with-corpus count mismatch", failures)
    require(accounting["zeroCorpusCommandCount"] == 1, "zero-corpus command count mismatch", failures)
    require(accounting["disableWeaponCallRows"] == 15, "DisableWeapon row count mismatch", failures)
    require(accounting["enableFlightModeCallRows"] == 1, "EnableFlightMode row count mismatch", failures)
    require(accounting["disableSpawnerCallRows"] == 2, "DisableSpawner row count mismatch", failures)
    require(accounting["setNameCallRows"] == 4, "SetName row count mismatch", failures)
    require(accounting["teleportOrientationCallRows"] == 5, "TeleportOrientation row count mismatch", failures)
    require(accounting["setWindVectorCallRows"] == 0, "SetWindVector row count mismatch", failures)
    require(accounting["wave582MetadataRows"] == 6, "Wave582 metadata count mismatch", failures)
    require(accounting["wave582InstructionRows"] == 534, "Wave582 instruction count mismatch", failures)
    require(accounting["wave582VtableRows"] == 32, "Wave582 vtable count mismatch", failures)
    require(accounting["fixtureSelectionOriginalRank"] == 8, "fixture selection rank mismatch", failures)
    require(accounting["fixtureSelectionOriginalDecision"] == "deferred", "fixture selection decision mismatch", failures)
    require(accounting["previousFixtureStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    for case in actual["deterministicDispatchCases"]:
        expected_case = DISPATCH_CASES[case["command"]]
        require(case["handlerAddress"] == expected_case["handlerAddress"], f"handler address mismatch: {case['command']}", failures)
        require(case["handlerName"] == expected_case["handlerName"], f"handler name mismatch: {case['command']}", failures)
        require(case["argumentGetterSlot"] == expected_case["argumentGetterSlot"], f"getter slot mismatch: {case['command']}", failures)
        require(case["dispatchKind"] == expected_case["dispatchKind"], f"dispatch kind mismatch: {case['command']}", failures)
        require(case["dispatchTarget"] == expected_case["dispatchTarget"], f"dispatch target mismatch: {case['command']}", failures)
        require(case["directNonCommentLooseMslRows"] == EXPECTED_DIRECT_COUNTS[case["command"]], f"loose MSL count mismatch: {case['command']}", failures)
        require(case["staticDispatchOnly"] is True, f"static-dispatch guard mismatch: {case['command']}", failures)
        require(case["runtimeCommandEffectProven"] is False, f"runtime effect guard mismatch: {case['command']}", failures)
        require(case["runtimeObjectIdentityProven"] is False, f"object identity guard mismatch: {case['command']}", failures)
        require(case["exactThingVfuncSemanticsProven"] is False, f"vfunc semantics guard mismatch: {case['command']}", failures)
    for case in actual["descriptorContextCases"]:
        require(case["descriptorContextOnly"] is True, f"descriptor context guard mismatch: {case['command']}", failures)
        require(case["runtimeCommandEffectProven"] is False, f"descriptor runtime guard mismatch: {case['command']}", failures)

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
    static_schema = read_json(THING_STATIC)
    fixture_selection = read_json(FIXTURE_SELECTION)
    require(previous["missionScriptHudDisplayCommandEffectFixtureProofPlanStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(previous["selectedNextSlice"] == THIS_SLICE, "previous fixture selected next slice mismatch", failures)
    require(static_schema["status"] == "PASS", "Thing Value static schema status mismatch", failures)
    require(tuple(static_schema["descriptorRecords"].keys()) == DESCRIPTOR_ORDER, "descriptor key order mismatch", failures)
    require(tuple(static_schema["descriptorRecords"][key]["index"] for key in static_schema["descriptorRecords"]) == DESCRIPTOR_INDICES, "descriptor index order mismatch", failures)
    for command, expected in EXPECTED_DIRECT_COUNTS.items():
        require(static_schema["looseMslUsage"]["directNonCommentCounts"][command] == expected, f"{command} direct count mismatch", failures)
    require(sum(static_schema["looseMslUsage"]["directNonCommentCounts"].values()) == 27, "loose MSL total mismatch", failures)
    selection = fixture_selection_row(fixture_selection)
    require(selection["rank"] == 8, "fixture selection rank mismatch", failures)
    require(selection["decision"] == "deferred", "fixture selection decision mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=thing-value-engine-helper",
        "selectedFixturePath=thing-vfunc-engine-unit-helper-dispatch-table",
        "descriptorIndices=41/98/99/138/140/141",
        "descriptorRecordCount=6",
        "descriptorContextCaseCount=6",
        "handlerDispatchCaseCount=6",
        "thingVfuncDispatchCaseCount=3",
        "engineHelperDispatchCaseCount=2",
        "unitHelperDispatchCaseCount=1",
        "getterSlotCount=3",
        "dispatchTargetCount=6",
        "deterministicFixtureCaseCount=6",
        "totalStaticCommandStepCount=6",
        "effectAssertionCount=18",
        "directNonCommentLooseMslRows=27",
        "commandWithCorpusRows=5",
        "zeroCorpusCommandCount=1",
        "disableWeaponCallRows=15",
        "enableFlightModeCallRows=1",
        "disableSpawnerCallRows=2",
        "setNameCallRows=4",
        "teleportOrientationCallRows=5",
        "setWindVectorCallRows=0",
        "wave582InstructionRows=534",
        "wave582VtableRows=32",
        "fixtureSelectionOriginalRank=8",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "IScript__SetThingValueViaVFunc198_FromArg",
        "IScript__SetThingValueViaVFunc19C_FromArg",
        "IScript__SetThingValueViaEngineHelper4FE390_FromArg",
        "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg",
        "IScript__SetThingFloatViaVFunc1C8_FromArg",
        "IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
        "0x00534fb0",
        "0x00534fe0",
        "0x00535010",
        "0x00535040",
        "0x00535530",
        "0x00535560",
        "+0x38",
        "+0x34",
        "+0x30",
        "+0x198",
        "+0x19c",
        "+0x1c8",
        "CEngine__EnableThingByNameFlag",
        "CEngine__DisableThingByNameFlag",
        "CUnit__SetFactionForHierarchy",
        "DisableWeapon",
        "EnableFlightMode",
        "DisableSpawner",
        "SetName",
        "TeleportOrientation",
        "SetWindVector",
        "runtimeExecution=false",
        "beLaunch=false",
        "sourcePathsPublic=false",
        "rawMslRowsPublic=false",
        "liveLooseMslLoading=false",
        "packedResourceScriptSelectionProven=false",
        "privateFrameReviewPerformed=false",
        "ghidraMutation=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeThingBehaviorRows=0",
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
        "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.md",
        "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=thing-value-engine-helper",
        "selectedNextSlice=MissionScript Player-State / Score Command-Effect Fixture Proof Plan",
        "handlerDispatchCaseCount=6",
        "thingVfuncDispatchCaseCount=3",
        "engineHelperDispatchCaseCount=2",
        "unitHelperDispatchCaseCount=1",
        "directNonCommentLooseMslRows=27",
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
            f"{path.relative_to(ROOT)} still marks Thing Value fixture active",
            failures,
        )

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed Thing Value fixture lane", failures)
    require(
        f"Completed {NEXT_SLICE}" in backlog
        or f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in backlog,
        "backlog missing active-or-completed Player-State / Score follow-up lane",
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
        scripts.get("test:missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan")
        == r"py -3 tools\missionscript_thing_value_engine_helper_command_effect_fixture_proof_plan_probe.py --check",
        "missing package Thing Value fixture proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-thing-value-engine-helper-command-effect-static",
        "test:missionscript-hud-display-command-effect-fixture-proof-plan",
        "test:missionscript-command-effect-fixture-selection",
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
        require(no_bea_process_running(), "BEA.exe process is running after Thing Value fixture proof", failures)
        if failures:
            print("MissionScript Thing Value / Engine Helper fixture proof-plan probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Thing Value / Engine Helper fixture proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
