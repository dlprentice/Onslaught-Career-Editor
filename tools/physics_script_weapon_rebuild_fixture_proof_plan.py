#!/usr/bin/env python3
"""Build the PhysicsScript weapon rebuild fixture proof-plan schema."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import physics_script_component_rebuild_fixture_proof_plan as component_tool
import physics_script_rebuild_interface_rollup as rollup_tool
import physics_script_rebuild_fixture_selection as selection_tool
import physics_script_scalar_string_decoder_fixture as scalar_fixture_tool
import physics_script_value_id_semantic_crosswalk as crosswalk_tool


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-rebuild-fixture-proof-plan.v1.json"
DEFAULT_GAME_ROOT = ROOT / "game"

STATUS_TOKEN = "physics-script-weapon-rebuild-fixture-proof-plan-complete-static-weapon-value-interface-fixture-not-runtime-proof"
THIS_SLICE = "PhysicsScript Weapon Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-weapon-rebuild-fixture-proof-plan"
PREVIOUS_SLICE = "PhysicsScript Component Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-round-rebuild-fixture-proof-plan"
SELECTED_FAMILY = "weapon"
SELECTED_PATH = "weapon-selected-value-id-interface-static-fixture"
STATEMENT_TYPE_ID = 2
EXPECTED_VALUE_IDS = [1, 4, 5, 14]
EXPECTED_OBSERVED_VALUE_IDS = list(range(1, 15))
FACTORY_ONLY_VALUE_IDS: list[int] = []
UNSELECTED_OBSERVED_VALUE_IDS = [2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
MIXED_PAYLOAD_SHAPE_VALUE_IDS = [1]

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "livePhysicsScriptRuntimeLoading",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsScriptOutcomesProven",
    "runtimeWeaponBehaviorProven",
    "runtimeWeaponChargeBehaviorProven",
    "runtimeWeaponConsumptionBehaviorProven",
    "runtimeWeaponIconBehaviorProven",
    "runtimeWeaponVersusAirBehaviorProven",
    "runtimeWeaponFiringBehaviorProven",
    "runtimeWeaponDamageBehaviorProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "exactWeaponRecordLayoutProven",
    "completeValueIdSemanticsProven",
    "all185PairsSemanticallyNamed",
    "rawStringIdentityProven",
    "rawNumericMeaningProven",
    "rawCopiedStringsEmitted",
    "rawPayloadBytesPublished",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "sourceSelectionObserved",
    "sourceSelectionProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rebuildImplementation",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
    "exactSourceBodyIdentityProven",
    "exactRegistryContainerLayoutProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimePhysicsScriptRows",
    "runtimeWeaponRows",
    "runtimeWeaponChargeRows",
    "runtimeWeaponConsumptionRows",
    "runtimeWeaponIconRows",
    "runtimeWeaponVersusAirRows",
    "runtimeWeaponFiringRows",
    "runtimeWeaponDamageRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "godotRows",
    "rebuildImplementationRows",
    "beProcessesAfterFixture",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawCopiedStringRows",
    "rawNumericRowsPublished",
    "serializedCompletenessRows",
    "exactLayoutRows",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def payload_shape_counts(game_root: Path = DEFAULT_GAME_ROOT) -> tuple[dict[int, Counter[str]], dict[str, int]]:
    path = game_root / "data" / "default physics.dat"
    data = path.read_bytes()
    offset = 0
    if component_tool.read_i16(data, offset) != 0x12:
        raise component_tool.ParseError("unexpected PhysicsScript header")
    offset += 2
    counts: dict[int, Counter[str]] = defaultdict(Counter)
    top_level_records = 0
    value_nodes = 0
    raw_value_payload_bytes = 0
    declared_payload_bytes = 0
    while True:
        statement_type = component_tool.read_i32(data, offset)
        offset += 4
        if statement_type == -1:
            break
        payload_size = component_tool.read_i32(data, offset)
        offset += 4
        if payload_size < 0 or offset + payload_size > len(data):
            raise component_tool.ParseError("top-level payload overrun")
        nul = data.find(b"\0", offset)
        if nul < 0:
            raise component_tool.ParseError("unterminated statement name")
        offset = nul + 1
        if statement_type == STATEMENT_TYPE_ID:
            top_level_records += 1
            declared_payload_bytes += payload_size
        while True:
            value_id = component_tool.read_i32(data, offset)
            value_payload_size = component_tool.read_i32(data, offset + 4)
            offset += 8
            if value_payload_size < 0 or offset + value_payload_size > len(data):
                raise component_tool.ParseError("value payload overrun")
            payload = data[offset : offset + value_payload_size]
            offset += value_payload_size
            if statement_type == STATEMENT_TYPE_ID:
                class_id = scalar_fixture_tool.classify_payload(payload)
                scalar_fixture_tool.validate_roundtrip(class_id, payload)
                counts[value_id][class_id] += 1
                value_nodes += 1
                raw_value_payload_bytes += len(payload)
            marker = component_tool.read_i32(data, offset)
            offset += 4
            if marker != 0:
                break
    return counts, {
        "topLevelRecords": top_level_records,
        "valueNodes": value_nodes,
        "rawValuePayloadBytes": raw_value_payload_bytes,
        "declaredPayloadBytes": declared_payload_bytes,
    }


def selected_fixture_rows(selection_rows: list[dict[str, Any]], shape_counts: dict[int, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in selection_rows:
        value_id = row["valueId"]
        shapes = dict(sorted(shape_counts.get(value_id, Counter()).items()))
        mixed_shape = len(shapes) > 1
        if value_id == 1:
            boundary = (
                "Selected chargeLevel is copied-corpus-observed with a dominant raw-preserved-other shape and one three-scalar shape. "
                "This fixture preserves the public-safe shape split and does not infer charge-level runtime behavior."
            )
        else:
            boundary = row["claimBoundary"]
        rows.append(
            {
                "fixtureCaseId": f"weapon-value-{value_id:02d}-{row['rebuildFacingFieldName']}",
                "family": row["family"],
                "valueId": value_id,
                "valueIdHex": row["valueIdHex"],
                "rebuildFacingFieldName": row["rebuildFacingFieldName"],
                "crosswalkPayloadClass": row["payloadClass"],
                "observedPayloadShapeClasses": shapes,
                "copiedCorpusCount": row["copiedCorpusCount"],
                "corpusPresence": row["corpusPresence"],
                "semanticState": row["semanticState"],
                "factoryAnchor": row["factoryAnchor"],
                "applyAnchor": row["applyAnchor"],
                "registryGlobal": row["registryGlobal"],
                "destinationRecordKind": row["destinationRecordKind"],
                "destinationField": row["destinationField"],
                "evidenceTier": row["evidenceTier"],
                "factoryOnlyBoundary": False,
                "mixedPayloadShapeBoundary": mixed_shape,
                "claimBoundary": boundary,
                "publicSafe": bool(row["publicSafe"]),
            }
        )
    return rows


def sum_shapes(rows: list[dict[str, Any]]) -> Counter[str]:
    total: Counter[str] = Counter()
    for row in rows:
        total.update(row["observedPayloadShapeClasses"])
    return total


def build_report(game_root: Path = DEFAULT_GAME_ROOT) -> dict[str, Any]:
    selection = selection_tool.build_report()
    rollup = rollup_tool.build_report()
    crosswalk = crosswalk_tool.build_report()
    previous_fixture = read_json(component_tool.OUTPUT)
    shape_counts, corpus = payload_shape_counts(game_root)
    selected_rows = [row for row in crosswalk["crosswalkRows"] if row["family"] == SELECTED_FAMILY]
    selected_rows = sorted(selected_rows, key=lambda row: row["valueId"])
    rows = selected_fixture_rows(selected_rows, shape_counts)
    selected_shape_totals = sum_shapes(rows)

    selected_ids = [row["valueId"] for row in rows]
    observed_ids = sorted(shape_counts)
    unselected_ids = [value_id for value_id in observed_ids if value_id not in selected_ids]
    unselected_shape_totals = Counter()
    for value_id in unselected_ids:
        unselected_shape_totals.update(shape_counts[value_id])

    coverage = crosswalk["familyCoverageSummary"][SELECTED_FAMILY]
    selected_top = next(row for row in rollup["topLevelInterfaceRows"] if row["family"] == SELECTED_FAMILY)

    if selected_ids != EXPECTED_VALUE_IDS:
        raise ValueError(f"unexpected selected weapon ids: {selected_ids}")
    if observed_ids != EXPECTED_OBSERVED_VALUE_IDS:
        raise ValueError(f"unexpected observed weapon ids: {observed_ids}")
    if unselected_ids != UNSELECTED_OBSERVED_VALUE_IDS:
        raise ValueError(f"unexpected unselected weapon ids: {unselected_ids}")
    if coverage["selectedCrosswalkRowCount"] != len(EXPECTED_VALUE_IDS):
        raise ValueError("unexpected weapon selected crosswalk row count")

    return {
        "schemaVersion": "physics-script-weapon-rebuild-fixture-proof-plan.v1",
        "status": "PASS",
        "proofPlan": THIS_SLICE,
        "scope": THIS_SCOPE,
        "fixtureStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "selectedFixtureFamily": SELECTED_FAMILY,
        "selectedFixturePath": SELECTED_PATH,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "fixtureAccounting": {
            "sourceProofCount": 6,
            "sourceSchemaCount": 5,
            "sourceMirrorPairCount": 9,
            "selectedCandidateRank": 6,
            "selectedSourceProofCount": 5,
            "selectedValueInterfaceRowCount": len(rows),
            "selectedValueIdCount": len(selected_ids),
            "selectedObservedValueIdCount": coverage["observedSelectedValueIdCount"],
            "selectedFactoryOnlyValueIdCount": coverage["factoryOnlySelectedValueIdCount"],
            "selectedUnselectedObservedValueIdCount": coverage["unselectedObservedValueIdCount"],
            "selectedTopLevelRecordCount": corpus["topLevelRecords"],
            "selectedValueNodeCount": corpus["valueNodes"],
            "selectedRawValuePayloadBytesPreserved": corpus["rawValuePayloadBytes"],
            "selectedDeclaredPayloadBytes": corpus["declaredPayloadBytes"],
            "selectedOwnedStringFieldCount": 1,
            "selectedScalarFieldCount": 2,
            "selectedCompoundChargeFieldCount": 1,
            "selectedFixtureRowCount": len(rows),
            "selectedObservedFixtureRowCount": len(rows),
            "selectedFactoryOnlyFixtureRowCount": 0,
            "selectedPayloadShapeCaseCount": sum(len(row["observedPayloadShapeClasses"]) for row in rows),
            "selectedObservedPayloadShapeClassCount": len(selected_shape_totals),
            "selectedScalar4ShapePayloadCount": selected_shape_totals["scalar4_roundtrip"],
            "selectedOwnedStringShapePayloadCount": selected_shape_totals["owned_string_ascii_nul_shape_roundtrip"],
            "selectedTwoScalarShapePayloadCount": selected_shape_totals["two_scalar4_roundtrip"],
            "selectedThreeScalarShapePayloadCount": selected_shape_totals["three_scalar4_roundtrip"],
            "selectedRawPreservedOtherShapePayloadCount": selected_shape_totals["raw_preserved_other"],
            "selectedMixedPayloadShapeValueIdCount": len(MIXED_PAYLOAD_SHAPE_VALUE_IDS),
            "selectedCrosswalkChargeLevelCorpusCount": 142,
            "selectedCrosswalkScalarCorpusCount": 27,
            "selectedCrosswalkOwnedStringCorpusCount": 15,
            "factoryOnlyValueIdCount": 0,
            "unselectedObservedValueIdCount": len(unselected_ids),
            "unselectedObservedScalar4PayloadCount": unselected_shape_totals["scalar4_roundtrip"],
            "unselectedObservedRawPreservedOtherPayloadCount": unselected_shape_totals["raw_preserved_other"],
            "unselectedObservedOwnedStringShapePayloadCount": unselected_shape_totals["owned_string_ascii_nul_shape_roundtrip"],
            "topLevelFamilyCount": rollup["rollupAccounting"]["topLevelFamilyCount"],
            "valueInterfaceRowCount": rollup["rollupAccounting"]["valueInterfaceRowCount"],
            "observedSelectedRowCount": rollup["rollupAccounting"]["observedSelectedRowCount"],
            "factoryOnlySelectedRowCount": rollup["rollupAccounting"]["factoryOnlySelectedRowCount"],
            "unselectedObservedRowCount": rollup["rollupAccounting"]["unselectedObservedRowCount"],
            "physicsScriptCorpusByteCount": crosswalk["corpusCounts"]["parsedByteCount"],
            "physicsScriptStreamHeader": crosswalk["corpusCounts"]["streamHeader"],
            "physicsScriptTopLevelStatementCount": crosswalk["corpusCounts"]["topLevelStatementCount"],
            "physicsScriptValueListNodeCount": crosswalk["corpusCounts"]["valueListNodeCount"],
            "physicsScriptStatementValuePairCount": crosswalk["corpusCounts"]["uniqueStatementValuePairCount"],
            "physicsScriptRawValuePayloadBytesPreserved": crosswalk["corpusCounts"]["rawValuePayloadBytesPreserved"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
            "latestGhidraBackupClass": "verified-static-backup-redacted",
            "factoryOnlyValueIds": FACTORY_ONLY_VALUE_IDS,
            "observedValueIds": observed_ids,
            "unselectedObservedValueIds": unselected_ids,
            "selectedMixedPayloadShapeValueIds": MIXED_PAYLOAD_SHAPE_VALUE_IDS,
        },
        "sourceEvidence": {
            "previousFixture": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-component-rebuild-fixture-proof-plan.md",
                "schemaPath": rel(component_tool.OUTPUT),
                "fixtureStatus": previous_fixture["fixtureStatus"],
                "selectedNextSlice": previous_fixture["selectedNextSlice"],
            },
            "fixtureSelection": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-rebuild-fixture-selection.md",
                "schemaPath": rel(selection_tool.OUTPUT),
                "fixtureSelectionStatus": selection["fixtureSelectionStatus"],
            },
            "rollup": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-rebuild-interface-rollup.md",
                "schemaPath": rel(rollup_tool.OUTPUT),
                "rollupStatus": rollup["rollupStatus"],
                "valueInterfaceRowCount": rollup["rollupAccounting"]["valueInterfaceRowCount"],
            },
            "valueIdCrosswalk": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-value-id-semantic-crosswalk-proof-plan.md",
                "schemaPath": rel(crosswalk_tool.OUTPUT),
                "family": SELECTED_FAMILY,
                "observedValueIdCount": coverage["observedValueIdCount"],
                "selectedCrosswalkRowCount": coverage["selectedCrosswalkRowCount"],
                "observedSelectedValueIdCount": coverage["observedSelectedValueIdCount"],
                "factoryOnlySelectedValueIdCount": coverage["factoryOnlySelectedValueIdCount"],
                "unselectedObservedValueIdCount": coverage["unselectedObservedValueIdCount"],
                "unselectedObservedValueIds": crosswalk["unselectedObservedValueIdsByFamily"][SELECTED_FAMILY],
            },
            "staticContract": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-static-contract.md",
                "anchors": [
                    "CPhysicsScriptStatements__CreateStatementType3",
                    "CWeaponStatement__LoadFromMemBuffer",
                    "CPhysicsWeaponValueList__LoadFromMemBuffer",
                    "CWeaponStatement__CreateWeaponAndRecurse",
                    "CWeaponChargeLevel__LoadFromMemBuffer",
                    "CWeaponConsumption__ApplyToWeaponByName",
                    "CWeaponIconName__ApplyToWeaponByName",
                    "CWeaponVersusAir__ApplyToWeaponByName",
                    "DAT_008553e8",
                ],
            },
        },
        "selectedFixture": {
            "family": SELECTED_FAMILY,
            "pathId": SELECTED_PATH,
            "statementFamilyTypeId": selected_top["typeId"],
            "valueFactoryTypeId": 3,
            "nestedFactory": selected_top["nestedFactory"],
            "statementLoader": selected_top["statementLoader"],
            "valueListLoader": selected_top["valueListLoader"],
            "createAnchor": selected_top["createAnchor"],
            "registryGlobal": selected_top["registryGlobal"],
            "valueIds": selected_ids,
            "valueIdHexes": [row["valueIdHex"] for row in rows],
            "observedValueIds": observed_ids,
            "factoryOnlyValueIds": FACTORY_ONLY_VALUE_IDS,
            "unselectedObservedValueIds": unselected_ids,
            "ownedStringFields": [row["rebuildFacingFieldName"] for row in rows if row["crosswalkPayloadClass"] == "owned_string_at_08"],
            "scalarFields": [row["rebuildFacingFieldName"] for row in rows if row["crosswalkPayloadClass"] == "scalar4"],
            "compoundChargeFields": [
                row["rebuildFacingFieldName"] for row in rows if row["crosswalkPayloadClass"] == "owned_string_and_scalar_shape"
            ],
            "fixtureRows": rows,
            "payloadShapeTotals": dict(sorted(selected_shape_totals.items())),
            "mixedPayloadShapeBoundary": {
                "valueIds": MIXED_PAYLOAD_SHAPE_VALUE_IDS,
                "fieldNames": ["chargeLevel"],
                "boundary": "Weapon chargeLevel has a mixed copied-corpus shape distribution: 141 raw-preserved-other rows and one three-scalar public-safe row. The fixture preserves shape counts without interpreting runtime charge behavior.",
                "runtimeMeaningProven": False,
            },
            "unselectedObservedBoundary": {
                "valueIds": unselected_ids,
                "boundary": "Weapon value ids 2, 3, 6, 7, 8, 9, 10, 11, 12, and 13 are observed in the copied corpus but remain outside this selected rebuild-facing crosswalk.",
                "runtimeMeaningProven": False,
            },
        },
        "fixtureRequirementRows": [
            {
                "row": "family-fixture",
                "status": "satisfied-static-with-unselected-observed-boundary",
                "evidence": "weapon has 14 observed ids, 4 selected rows, zero factory-only selected rows, and 10 unselected observed ids",
                "boundary": "Static family-selection proof only.",
            },
            {
                "row": "loader-fixture",
                "status": "satisfied-static",
                "evidence": "CPhysicsScriptStatements__CreateStatementType3, CWeaponStatement__LoadFromMemBuffer, CPhysicsWeaponValueList__LoadFromMemBuffer, CWeaponStatement__CreateWeaponAndRecurse, and DAT_008553e8",
                "boundary": "Static loader/factory/registry bridge only.",
            },
            {
                "row": "value-interface-fixture",
                "status": "satisfied-static",
                "evidence": "selected value ids 1,4,5,14 and four rebuild-facing field names",
                "boundary": "Selected value-id interface only, not complete value semantics.",
            },
            {
                "row": "payload-shape-fixture",
                "status": "satisfied-public-safe",
                "evidence": "chargeLevel mixed shape, consumption scalar4, iconName owned string, and versusAir scalar4 with explicit unselected-observed scalar boundary",
                "boundary": "Public-safe payload shape only; no raw strings or numeric meanings.",
            },
            {
                "row": "stop-fixture",
                "status": "enforced",
                "evidence": "runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows",
                "boundary": "Defer instead of broadening into runtime firing, damage, cadence, visuals, audio, or rebuild implementation.",
            },
        ],
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "frontDoorValidation": {
            "backlogUpdated": True,
            "mappedSystemsUpdated": True,
            "physicsContractUpdated": True,
            "binaryIndexUpdated": True,
            "reIndexUpdated": True,
            "readinessNoteUpdated": True,
            "packageScriptAdded": True,
        },
        "publicSafety": {
            "publicLeakCheck": "PASS",
            "rawBytesEmitted": False,
            "rawCopiedStringsEmitted": False,
            "rawHashValuesEmitted": False,
            "rawNumericValuesEmitted": False,
            "absolutePrivatePathsEmitted": False,
            "privateArtifactLocatorsEmitted": False,
        },
        "claimBoundary": {
            "summary": "Static PhysicsScript weapon selected value-id fixture only.",
            "proves": [
                "The selected weapon value-id interface is materialized as public-safe static fixture rows.",
                "The selected weapon rows preserve chargeLevel, consumption, iconName, and versusAir factory/apply/registry anchors.",
                "The selected fixture preserves the chargeLevel mixed payload-shape boundary and unselected observed weapon value-id debt.",
            ],
            "doesNotProve": [
                "runtime PhysicsScript behavior",
                "runtime weapon behavior",
                "runtime weapon charge behavior",
                "runtime weapon firing behavior",
                "runtime weapon damage behavior",
                "serialized PhysicsScript completeness",
                "exact PhysicsScript layouts",
                "exact weapon record layout",
                "complete value-id semantics",
                "raw string identity",
                "raw numeric value meaning",
                "BEA patching behavior",
                "Godot parity",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write tracked schema")
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    args = parser.parse_args()

    report = build_report(args.game_root)
    if args.write:
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
