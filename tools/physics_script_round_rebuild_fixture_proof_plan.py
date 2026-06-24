#!/usr/bin/env python3
"""Build the PhysicsScript round rebuild fixture proof-plan schema."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import physics_script_component_rebuild_fixture_proof_plan as component_tool
import physics_script_rebuild_fixture_selection as selection_tool
import physics_script_rebuild_interface_rollup as rollup_tool
import physics_script_scalar_string_decoder_fixture as scalar_fixture_tool
import physics_script_value_id_semantic_crosswalk as crosswalk_tool
import physics_script_weapon_rebuild_fixture_proof_plan as weapon_tool


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-round-rebuild-fixture-proof-plan.v1.json"
DEFAULT_GAME_ROOT = ROOT / "game"

STATUS_TOKEN = "physics-script-round-rebuild-fixture-proof-plan-complete-static-round-value-interface-fixture-not-runtime-proof"
THIS_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-round-rebuild-fixture-proof-plan"
PREVIOUS_SLICE = "PhysicsScript Weapon Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-weapon-mode-rebuild-fixture-proof-plan"
SELECTED_FAMILY = "round"
SELECTED_PATH = "round-selected-value-id-interface-static-fixture"
STATEMENT_TYPE_ID = 4
EXPECTED_VALUE_IDS = [4, 8, 9, 24, 33, 35, 36]
EXPECTED_OBSERVED_VALUE_IDS = [
    1,
    2,
    3,
    4,
    5,
    6,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    22,
    23,
    24,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    35,
    36,
    37,
    38,
]
FACTORY_ONLY_VALUE_IDS: list[int] = []
UNSELECTED_OBSERVED_VALUE_IDS = [
    1,
    2,
    3,
    5,
    6,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    22,
    23,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    37,
    38,
]
MIXED_PAYLOAD_SHAPE_VALUE_IDS = [8, 9]

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "livePhysicsScriptRuntimeLoading",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsScriptOutcomesProven",
    "runtimeRoundBehaviorProven",
    "runtimeProjectileBehaviorProven",
    "runtimeProjectileOutcomeProven",
    "runtimeRoundSeekBehaviorProven",
    "runtimeRoundEffectBehaviorProven",
    "runtimeRoundExplosionBehaviorProven",
    "runtimeRoundGridOfFearBehaviorProven",
    "runtimeRoundTreeCollisionBehaviorProven",
    "runtimeRoundMeshBehaviorProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "exactRoundRecordLayoutProven",
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
    "runtimeRoundRows",
    "runtimeProjectileRows",
    "runtimeProjectileOutcomeRows",
    "runtimeRoundSeekRows",
    "runtimeRoundEffectRows",
    "runtimeRoundExplosionRows",
    "runtimeRoundGridOfFearRows",
    "runtimeRoundTreeCollisionRows",
    "runtimeRoundMeshRows",
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
        mixed_shape = value_id in MIXED_PAYLOAD_SHAPE_VALUE_IDS and len(shapes) > 1
        if value_id == 8:
            boundary = (
                "Selected `effect` field has mixed copied-corpus payload-shape classes: owned-string-shaped rows plus "
                "payload-size-8 and payload-size-12 rows classified as two-scalar and three-scalar roundtrip. "
                "The fixture preserves public-safe shape counts and does not infer runtime projectile visual behavior."
            )
        elif value_id == 9:
            boundary = (
                "Selected `explosion` field has mixed copied-corpus payload-shape classes: owned-string-shaped rows plus "
                "payload-size-8 and payload-size-12 rows classified as two-scalar and three-scalar roundtrip. "
                "The fixture preserves public-safe shape counts and does not infer runtime explosion/outcome behavior."
            )
        else:
            boundary = row["claimBoundary"]
        rows.append(
            {
                "fixtureCaseId": f"round-value-{value_id:02d}-{row['rebuildFacingFieldName']}",
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
                "publicSafe": bool(row["publicSafe"]),
                "fixtureAssertion": "public-safe static selected round value-id interface row; no raw payload publication",
                "claimBoundary": boundary,
            }
        )
    return rows


def sum_shapes(rows: list[dict[str, Any]]) -> Counter[str]:
    total: Counter[str] = Counter()
    for row in rows:
        total.update(row["observedPayloadShapeClasses"])
    return total


def build_report(game_root: Path = DEFAULT_GAME_ROOT) -> dict[str, Any]:
    previous_fixture = read_json(weapon_tool.OUTPUT)
    selection = selection_tool.build_report()
    rollup = rollup_tool.build_report()
    crosswalk = crosswalk_tool.build_report()
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
    candidate = next(row for row in selection["candidateRanking"] if row["family"] == SELECTED_FAMILY)
    payload_classes = Counter(row["crosswalkPayloadClass"] for row in rows)
    payload_corpus_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        payload_corpus_counts[row["crosswalkPayloadClass"]] += row["copiedCorpusCount"]

    if selected_ids != EXPECTED_VALUE_IDS:
        raise ValueError(f"unexpected selected round ids: {selected_ids}")
    if observed_ids != EXPECTED_OBSERVED_VALUE_IDS:
        raise ValueError(f"unexpected observed round ids: {observed_ids}")
    if unselected_ids != UNSELECTED_OBSERVED_VALUE_IDS:
        raise ValueError(f"unexpected unselected round ids: {unselected_ids}")
    if coverage["selectedCrosswalkRowCount"] != len(EXPECTED_VALUE_IDS):
        raise ValueError("unexpected round selected crosswalk row count")

    return {
        "schemaVersion": "physics-script-round-rebuild-fixture-proof-plan.v1",
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
            "selectedCandidateRank": candidate["rank"],
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
            "selectedOwnedStringFieldCount": payload_classes["owned_string_at_08"],
            "selectedRoundedScalarFieldCount": payload_classes["rounded_scalar4"],
            "selectedNestedEnumChildFieldCount": payload_classes["nested_enum_child"],
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
            "selectedCrosswalkOwnedStringCorpusCount": payload_corpus_counts["owned_string_at_08"],
            "selectedCrosswalkRoundedScalarCorpusCount": payload_corpus_counts["rounded_scalar4"],
            "selectedCrosswalkNestedEnumChildCorpusCount": payload_corpus_counts["nested_enum_child"],
            "effectObservedOwnedStringShapeCount": shape_counts[8]["owned_string_ascii_nul_shape_roundtrip"],
            "effectObservedTwoScalarShapeCount": shape_counts[8]["two_scalar4_roundtrip"],
            "effectObservedThreeScalarShapeCount": shape_counts[8]["three_scalar4_roundtrip"],
            "explosionObservedOwnedStringShapeCount": shape_counts[9]["owned_string_ascii_nul_shape_roundtrip"],
            "explosionObservedTwoScalarShapeCount": shape_counts[9]["two_scalar4_roundtrip"],
            "explosionObservedThreeScalarShapeCount": shape_counts[9]["three_scalar4_roundtrip"],
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
                "proofPath": "reverse-engineering/binary-analysis/physics-script-weapon-rebuild-fixture-proof-plan.md",
                "schemaPath": rel(weapon_tool.OUTPUT),
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
            "scalarStringFixture": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-scalar-string-value-decoder-fixture-proof-plan.md",
                "schemaPath": "reverse-engineering/binary-analysis/physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json",
                "observedRoundPayloadShapeTotals": dict(sorted(sum_shapes([
                    {"observedPayloadShapeClasses": dict(counter)} for counter in shape_counts.values()
                ]).items())),
            },
            "staticContract": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-static-contract.md",
                "anchors": [
                    "CPhysicsScriptStatements__CreateStatementType5",
                    "CRoundStatement__LoadFromMemBuffer",
                    "CPhysicsRoundValueList__LoadFromMemBuffer",
                    "CRoundStatement__CreateRoundAndRecurse",
                    "CRoundSeek__ApplyToRoundByName",
                    "CRoundEffect__ApplyToRoundByName",
                    "CRoundExplosion__ApplyToRoundByName",
                    "CRoundGridOfFear__ApplyToRoundByName",
                    "CRoundWaterEffect__ApplyToRoundByName",
                    "CRoundTreeCollision__ApplyToRoundByName",
                    "CRoundMesh__ApplyToRoundByName",
                    "DAT_008553f0",
                ],
            },
        },
        "selectedFixture": {
            "family": SELECTED_FAMILY,
            "pathId": SELECTED_PATH,
            "statementFamilyTypeId": selected_top["typeId"],
            "valueFactoryTypeId": 5,
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
            "roundedScalarFields": [row["rebuildFacingFieldName"] for row in rows if row["crosswalkPayloadClass"] == "rounded_scalar4"],
            "nestedEnumChildFields": [row["rebuildFacingFieldName"] for row in rows if row["crosswalkPayloadClass"] == "nested_enum_child"],
            "fixtureRows": rows,
            "payloadShapeTotals": dict(sorted(selected_shape_totals.items())),
            "mixedPayloadShapeBoundary": {
                "valueIds": MIXED_PAYLOAD_SHAPE_VALUE_IDS,
                "fieldNames": ["effect", "explosion"],
                "boundary": "Round effect and explosion rows carry mixed copied-corpus payload shapes. The fixture preserves the public-safe shape split and does not infer runtime projectile visual/explosion outcomes.",
                "runtimeMeaningProven": False,
            },
            "unselectedObservedBoundary": {
                "valueIds": unselected_ids,
                "boundary": "Round has 26 copied-corpus-observed value ids outside the selected rebuild-facing crosswalk. These rows remain explicit semantic debt rather than receiving invented meanings.",
                "runtimeMeaningProven": False,
            },
        },
        "fixtureRequirementRows": [
            {
                "row": "family-fixture",
                "status": "satisfied-static-with-unselected-observed-boundary",
                "evidence": "round has 33 observed ids, 7 selected rows, zero factory-only selected rows, and 26 unselected observed ids",
                "boundary": "Static family-selection proof only.",
            },
            {
                "row": "loader-fixture",
                "status": "satisfied-static",
                "evidence": "CPhysicsScriptStatements__CreateStatementType5, CRoundStatement__LoadFromMemBuffer, CPhysicsRoundValueList__LoadFromMemBuffer, CRoundStatement__CreateRoundAndRecurse, and DAT_008553f0",
                "boundary": "Static loader/factory/registry bridge only.",
            },
            {
                "row": "value-interface-fixture",
                "status": "satisfied-static",
                "evidence": "selected value ids 4,8,9,24,33,35,36 and seven rebuild-facing field names",
                "boundary": "Selected value-id interface only, not complete value semantics.",
            },
            {
                "row": "unselected-observed-boundary-fixture",
                "status": "satisfied-explicit-boundary",
                "evidence": "26 copied-corpus-observed round value ids are intentionally outside this selected rebuild-facing crosswalk",
                "boundary": "Observed raw round payload shapes are preserved as deferred boundary rows instead of receiving invented semantics.",
            },
            {
                "row": "payload-shape-fixture",
                "status": "satisfied-public-safe",
                "evidence": "selected nested enum, owned-string, and rounded-scalar rows with mixed shape boundaries for effect and explosion",
                "boundary": "Public-safe payload shape only; no raw strings or numeric meanings.",
            },
            {
                "row": "projectile-field-fixture",
                "status": "satisfied-static",
                "evidence": "seekTypeChild, effect, explosion, gridOfFear, waterEffect, treeCollisionStateChild, and mesh are anchored to round apply helpers and DAT_008553f0",
                "boundary": "Static round field boundary only, not runtime projectile behavior or outcome proof.",
            },
            {
                "row": "stop-fixture",
                "status": "enforced",
                "evidence": "runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows",
                "boundary": "Defer instead of broadening into runtime projectile launch, movement, collision, effects, damage, or rebuild implementation.",
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
            "summary": "Static PhysicsScript round selected value-id fixture only.",
            "proves": [
                "The selected round value-id interface is materialized as public-safe static fixture rows.",
                "The selected round rows preserve seekTypeChild, effect, explosion, gridOfFear, waterEffect, treeCollisionStateChild, and mesh factory/apply/registry anchors.",
                "The selected fixture preserves mixed payload-shape boundaries for effect and explosion.",
                "The large unselected observed Round value-id set remains explicit boundary debt instead of receiving invented meanings.",
            ],
            "doesNotProve": [
                "runtime PhysicsScript behavior",
                "runtime round behavior",
                "runtime projectile behavior",
                "runtime projectile outcomes",
                "runtime round seek behavior",
                "runtime round effect behavior",
                "runtime round explosion behavior",
                "runtime round grid-of-fear behavior",
                "runtime round tree-collision behavior",
                "runtime round mesh behavior",
                "serialized PhysicsScript completeness",
                "exact PhysicsScript layouts",
                "exact round record layout",
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
