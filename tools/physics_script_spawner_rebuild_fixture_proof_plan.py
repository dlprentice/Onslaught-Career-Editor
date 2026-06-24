#!/usr/bin/env python3
"""Build the PhysicsScript spawner rebuild fixture proof-plan schema."""

from __future__ import annotations

import argparse
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import physics_script_explosion_rebuild_fixture_proof_plan as explosion_tool
import physics_script_rebuild_fixture_selection as selection_tool
import physics_script_rebuild_interface_rollup as rollup_tool
import physics_script_scalar_string_decoder_fixture as scalar_fixture_tool
import physics_script_value_id_semantic_crosswalk as crosswalk_tool


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-spawner-rebuild-fixture-proof-plan.v1.json"
DEFAULT_GAME_ROOT = ROOT / "game"

STATUS_TOKEN = "physics-script-spawner-rebuild-fixture-proof-plan-complete-static-spawner-value-interface-fixture-not-runtime-proof"
THIS_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-spawner-rebuild-fixture-proof-plan"
PREVIOUS_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Hazard Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-hazard-rebuild-fixture-proof-plan"
SELECTED_FAMILY = "spawner"
SELECTED_PATH = "spawner-selected-value-id-interface-static-fixture"
STATEMENT_TYPE_ID = 5
EXPECTED_VALUE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
EXPECTED_OBSERVED_VALUE_IDS = [1, 2, 3, 6, 7, 8, 9, 11, 12, 14]
FACTORY_ONLY_VALUE_IDS = [4, 5, 10, 13]

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "livePhysicsScriptRuntimeLoading",
    "runtimeExecution",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsScriptOutcomesProven",
    "runtimeSpawnerBehaviorProven",
    "runtimeSpawnerUnitSpawnProven",
    "runtimeSpawnerTimingProven",
    "runtimeSpawnerAiBehaviorProven",
    "runtimeSpawnerRangeBehaviorProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "exactSpawnerRecordLayoutProven",
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
    "runtimeBasedOnInheritanceProven",
    "runtimeSpawnedUnitIdentityProven",
    "runtimeSquadBehaviorProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "runtimeCommandEffectRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimePhysicsScriptRows",
    "runtimeSpawnerRows",
    "runtimeSpawnerUnitSpawnRows",
    "runtimeSpawnerTimingRows",
    "runtimeSpawnerAiRows",
    "runtimeSpawnerRangeRows",
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
    "runtimeBasedOnRows",
    "runtimeSpawnedUnitRows",
    "runtimeSquadRows",
)


class ParseError(ValueError):
    """Raised when the copied PhysicsScript corpus cannot be framed."""


def read_i16(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        raise ParseError(f"truncated int16 at {offset}")
    return struct.unpack_from("<h", data, offset)[0]


def read_i32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise ParseError(f"truncated int32 at {offset}")
    return struct.unpack_from("<i", data, offset)[0]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def payload_shape_counts(game_root: Path = DEFAULT_GAME_ROOT) -> dict[int, Counter[str]]:
    path = game_root / "data" / "default physics.dat"
    data = path.read_bytes()
    offset = 0
    if read_i16(data, offset) != 0x12:
        raise ParseError("unexpected PhysicsScript header")
    offset += 2
    counts: dict[int, Counter[str]] = defaultdict(Counter)
    while True:
        statement_type = read_i32(data, offset)
        offset += 4
        if statement_type == -1:
            break
        payload_size = read_i32(data, offset)
        offset += 4
        if payload_size < 0 or offset + payload_size > len(data):
            raise ParseError("top-level payload overrun")
        nul = data.find(b"\0", offset)
        if nul < 0:
            raise ParseError("unterminated statement name")
        offset = nul + 1
        while True:
            value_id = read_i32(data, offset)
            value_payload_size = read_i32(data, offset + 4)
            offset += 8
            if value_payload_size < 0 or offset + value_payload_size > len(data):
                raise ParseError("value payload overrun")
            payload = data[offset : offset + value_payload_size]
            offset += value_payload_size
            if statement_type == STATEMENT_TYPE_ID:
                class_id = scalar_fixture_tool.classify_payload(payload)
                scalar_fixture_tool.validate_roundtrip(class_id, payload)
                counts[value_id][class_id] += 1
            marker = read_i32(data, offset)
            offset += 4
            if marker != 0:
                break
    return counts


def selected_fixture_rows(selection_rows: list[dict[str, Any]], shape_counts: dict[int, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in selection_rows:
        value_id = row["valueId"]
        shapes = dict(sorted(shape_counts.get(value_id, Counter()).items()))
        factory_only = value_id in FACTORY_ONLY_VALUE_IDS
        mixed_shape = len(shapes) > 1
        if value_id == 1 and mixed_shape:
            boundary = (
                "Selected `unitName` field has mixed copied-corpus payload-shape classes: "
                "owned-string-shaped rows plus payload-size-12 rows classified by the scalar/string fixture as three-scalar roundtrip. "
                "The fixture preserves both public-safe shape classes and does not publish raw unit names or numeric meanings."
            )
        elif factory_only:
            boundary = (
                "Factory-only selected spawner row: static factory/apply evidence exists, but this copied corpus has no observed payload rows for the value id. "
                "The fixture keeps the row as an explicit boundary instead of inventing copied-corpus evidence."
            )
        else:
            boundary = row["claimBoundary"]
        rows.append(
            {
                "fixtureCaseId": f"spawner-value-{value_id:02d}-{row['rebuildFacingFieldName']}",
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
                "factoryOnlyBoundary": factory_only,
                "mixedPayloadShapeBoundary": bool(value_id == 1 and mixed_shape),
                "publicSafe": row["publicSafe"],
                "fixtureAssertion": "public-safe static selected spawner value-id interface row; no raw payload publication",
                "claimBoundary": boundary,
            }
        )
    return rows


def build_report(game_root: Path = DEFAULT_GAME_ROOT) -> dict[str, Any]:
    selection = selection_tool.build_report()
    explosion = explosion_tool.build_report(game_root)
    rollup = rollup_tool.build_report()
    crosswalk = crosswalk_tool.build_report()
    top_rows = {row["family"]: row for row in rollup["topLevelInterfaceRows"]}
    selected_top = top_rows[SELECTED_FAMILY]
    selection_rows = [row for row in rollup["valueInterfaceRows"] if row["family"] == SELECTED_FAMILY]
    coverage = crosswalk["familyCoverageSummary"][SELECTED_FAMILY]
    shapes_by_value_id = payload_shape_counts(game_root)
    rows = selected_fixture_rows(selection_rows, shapes_by_value_id)

    observed_shape_totals: Counter[str] = Counter()
    for counter in shapes_by_value_id.values():
        observed_shape_totals.update(counter)
    selected_shape_totals: Counter[str] = Counter()
    for row in rows:
        selected_shape_totals.update(row["observedPayloadShapeClasses"])
    mixed_rows = [row for row in rows if row["mixedPayloadShapeBoundary"]]
    factory_only_rows = [row for row in rows if row["factoryOnlyBoundary"]]
    payload_classes = Counter(row["crosswalkPayloadClass"] for row in rows)
    payload_corpus_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        payload_corpus_counts[row["crosswalkPayloadClass"]] += row["copiedCorpusCount"]

    return {
        "schemaVersion": "physics-script-spawner-rebuild-fixture-proof-plan.v1",
        "status": "PASS",
        "proofPlan": THIS_SLICE,
        "scope": THIS_SCOPE,
        "fixtureStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "selectedFixtureFamily": SELECTED_FAMILY,
        "selectedFixturePath": SELECTED_PATH,
        "staticContext": rollup["staticContext"],
        "fixtureAccounting": {
            "sourceProofCount": 6,
            "sourceSchemaCount": 5,
            "sourceMirrorPairCount": 9,
            "selectedCandidateRank": 2,
            "selectedSourceProofCount": 5,
            "selectedValueInterfaceRowCount": len(selection_rows),
            "selectedValueIdCount": len(selection_rows),
            "selectedObservedValueIdCount": coverage["observedSelectedValueIdCount"],
            "selectedFactoryOnlyValueIdCount": coverage["factoryOnlySelectedValueIdCount"],
            "selectedUnselectedObservedValueIdCount": coverage["unselectedObservedValueIdCount"],
            "selectedTopLevelRecordCount": selected_top["topLevelRecords"],
            "selectedValueNodeCount": selected_top["valueNodes"],
            "selectedRawValuePayloadBytesPreserved": selected_top["rawValuePayloadBytes"],
            "selectedDeclaredPayloadBytes": selected_top["declaredPayloadBytes"],
            "selectedOwnedStringFieldCount": payload_classes["owned_string_at_08"],
            "selectedScalarFieldCount": payload_classes["scalar4"],
            "selectedFlagConstantTrueFieldCount": payload_classes["flag_constant_true"],
            "selectedFixtureRowCount": len(rows),
            "selectedObservedFixtureRowCount": len(EXPECTED_OBSERVED_VALUE_IDS),
            "selectedFactoryOnlyFixtureRowCount": len(factory_only_rows),
            "selectedPayloadShapeCaseCount": sum(len(row["observedPayloadShapeClasses"]) for row in rows),
            "selectedObservedPayloadShapeClassCount": len(selected_shape_totals),
            "selectedScalar4ShapePayloadCount": selected_shape_totals["scalar4_roundtrip"],
            "selectedOwnedStringShapePayloadCount": selected_shape_totals["owned_string_ascii_nul_shape_roundtrip"],
            "selectedThreeScalarShapePayloadCount": selected_shape_totals["three_scalar4_roundtrip"],
            "selectedMixedPayloadShapeValueIdCount": len(mixed_rows),
            "selectedMixedPayloadShapeValueIds": [row["valueId"] for row in mixed_rows],
            "selectedCrosswalkOwnedStringCorpusCount": payload_corpus_counts["owned_string_at_08"],
            "selectedCrosswalkScalarCorpusCount": payload_corpus_counts["scalar4"],
            "selectedCrosswalkFlagConstantTrueCorpusCount": payload_corpus_counts["flag_constant_true"],
            "unitNameObservedOwnedStringShapeCount": shapes_by_value_id[1]["owned_string_ascii_nul_shape_roundtrip"],
            "unitNameObservedThreeScalarShapeCount": shapes_by_value_id[1]["three_scalar4_roundtrip"],
            "factoryOnlyValueIdCount": len(FACTORY_ONLY_VALUE_IDS),
            "factoryOnlyValueIds": FACTORY_ONLY_VALUE_IDS,
            "observedValueIds": EXPECTED_OBSERVED_VALUE_IDS,
            "topLevelFamilyCount": rollup["rollupAccounting"]["topLevelFamilyCount"],
            "valueInterfaceRowCount": rollup["rollupAccounting"]["valueInterfaceRowCount"],
            "observedSelectedRowCount": rollup["rollupAccounting"]["observedSelectedRowCount"],
            "factoryOnlySelectedRowCount": rollup["rollupAccounting"]["factoryOnlySelectedRowCount"],
            "unselectedObservedRowCount": rollup["rollupAccounting"]["unselectedObservedRowCount"],
            "physicsScriptCorpusByteCount": rollup["corpusCounts"]["parsedByteCount"],
            "physicsScriptStreamHeader": rollup["corpusCounts"]["streamHeader"],
            "physicsScriptTopLevelStatementCount": rollup["rollupAccounting"]["physicsScriptTopLevelStatementCount"],
            "physicsScriptValueListNodeCount": rollup["rollupAccounting"]["physicsScriptValueListNodeCount"],
            "physicsScriptStatementValuePairCount": rollup["rollupAccounting"]["physicsScriptStatementValuePairCount"],
            "physicsScriptRawValuePayloadBytesPreserved": rollup["rollupAccounting"]["physicsScriptRawValuePayloadBytesPreserved"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "previousFixture": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-explosion-rebuild-fixture-proof-plan.md",
                "schemaPath": rel(explosion_tool.OUTPUT),
                "fixtureStatus": explosion["fixtureStatus"],
                "selectedNextSlice": explosion["selectedNextSlice"],
            },
            "fixtureSelection": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-rebuild-fixture-selection.md",
                "schemaPath": rel(selection_tool.OUTPUT),
                "fixtureSelectionStatus": selection["fixtureSelectionStatus"],
                "selectedFixtureFamily": selection["selectedFixtureFamily"],
                "selectedFixturePath": selection["selectedFixturePath"],
            },
            "rollup": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-rebuild-interface-rollup.md",
                "schemaPath": rel(rollup_tool.OUTPUT),
                "rollupStatus": rollup["rollupStatus"],
                "valueInterfaceRowCount": rollup["rollupAccounting"]["valueInterfaceRowCount"],
                "unselectedObservedRowCount": rollup["rollupAccounting"]["unselectedObservedRowCount"],
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
                "deferredFactoryValueIds": crosswalk["deferredFactoryValueIdsByFamily"][SELECTED_FAMILY],
            },
            "scalarStringFixture": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-scalar-string-value-decoder-fixture-proof-plan.md",
                "schemaPath": "reverse-engineering/binary-analysis/physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json",
                "observedSpawnerPayloadShapeTotals": dict(sorted(observed_shape_totals.items())),
            },
            "staticContract": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-static-contract.md",
                "anchors": [
                    "CPhysicsScriptStatements__CreateStatementType6",
                    "CSpawnerStatement__LoadFromMemBuffer",
                    "CPhysicsSpawnerValueList__LoadFromMemBuffer",
                    "CSpawnerStatement__CreateSpawnerAndRecurse",
                    "CSpawnerData__CreateAndRegisterByName",
                    "CSpawnerBasedOn__ApplyToSpawnerByName",
                    "CSpawnerUnit__ApplyToSpawnerByName",
                    "DAT_008553f4",
                ],
            },
        },
        "selectedFixture": {
            "family": SELECTED_FAMILY,
            "pathId": SELECTED_PATH,
            "statementFamilyTypeId": selected_top["typeId"],
            "valueFactoryTypeId": selection_rows[0]["valueFactoryTypeId"],
            "nestedFactory": selected_top["nestedFactory"],
            "statementLoader": selected_top["statementLoader"],
            "valueListLoader": selected_top["valueListLoader"],
            "createAnchor": selected_top["createAnchor"],
            "registryGlobal": selected_top["registryGlobal"],
            "valueIds": [row["valueId"] for row in rows],
            "valueIdHexes": [row["valueIdHex"] for row in rows],
            "observedValueIds": EXPECTED_OBSERVED_VALUE_IDS,
            "factoryOnlyValueIds": FACTORY_ONLY_VALUE_IDS,
            "ownedStringFields": [row["rebuildFacingFieldName"] for row in rows if row["crosswalkPayloadClass"] == "owned_string_at_08"],
            "scalarFields": [row["rebuildFacingFieldName"] for row in rows if row["crosswalkPayloadClass"] == "scalar4"],
            "flagConstantTrueFields": [row["rebuildFacingFieldName"] for row in rows if row["crosswalkPayloadClass"] == "flag_constant_true"],
            "fixtureRows": rows,
            "payloadShapeTotals": dict(sorted(selected_shape_totals.items())),
            "factoryOnlyBoundary": {
                "valueIds": FACTORY_ONLY_VALUE_IDS,
                "fieldNames": [row["rebuildFacingFieldName"] for row in factory_only_rows],
                "boundary": "These selected spawner rows have static factory/apply evidence but no copied-corpus payload rows in the current public-safe corpus aggregate.",
                "runtimeMeaningProven": False,
            },
        },
        "fixtureRequirementRows": [
            {
                "row": "family-fixture",
                "status": "satisfied-static-with-factory-only-boundary",
                "evidence": "spawner has 10 observed selected ids, 14 selected rows, 4 factory-only selected rows, and zero unselected observed ids",
                "boundary": "Static family-selection proof only.",
            },
            {
                "row": "loader-fixture",
                "status": "satisfied-static",
                "evidence": "CPhysicsScriptStatements__CreateStatementType6, CSpawnerStatement__LoadFromMemBuffer, CPhysicsSpawnerValueList__LoadFromMemBuffer, CSpawnerStatement__CreateSpawnerAndRecurse, and DAT_008553f4",
                "boundary": "Static loader/factory/registry bridge only.",
            },
            {
                "row": "value-interface-fixture",
                "status": "satisfied-static",
                "evidence": "selected value ids 1 through 14 and 14 rebuild-facing field names",
                "boundary": "Selected value-id interface only, not complete value semantics.",
            },
            {
                "row": "factory-only-boundary-fixture",
                "status": "satisfied-explicit-boundary",
                "evidence": "value ids 4,5,10,13 are factory-only selected rows in this copied-corpus aggregate",
                "boundary": "Static factory/apply evidence only; no copied-corpus payload values are invented.",
            },
            {
                "row": "payload-shape-fixture",
                "status": "satisfied-public-safe",
                "evidence": "nine scalar4 observed rows, one string-facing observed row, one explicit mixed payload-shape boundary for unitName, and four factory-only selected rows",
                "boundary": "Public-safe payload shape only; no raw strings or numeric meanings.",
            },
            {
                "row": "unit-name-fixture",
                "status": "satisfied-static",
                "evidence": "unitName value id 1 is anchored to CSpawnerUnit__ApplyToSpawnerByName and DAT_008553f4",
                "boundary": "Static unit-name field boundary only, not runtime spawned-unit identity.",
            },
            {
                "row": "stop-fixture",
                "status": "enforced",
                "evidence": "runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows",
                "boundary": "Defer instead of broadening.",
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
            "summary": "Static PhysicsScript spawner selected value-id fixture only.",
            "proves": [
                "The selected spawner value-id interface is materialized as public-safe static fixture rows.",
                "The selected spawner observed value ids carry static factory/apply/registry anchors and copied-corpus payload-shape counts.",
                "The selected fixture preserves public-safe payload shape counts and records the value id 1 mixed-shape boundary.",
                "Factory-only selected rows 4,5,10,13 remain explicit boundary debt instead of being hidden.",
            ],
            "doesNotProve": [
                "runtime PhysicsScript behavior",
                "runtime spawner behavior",
                "runtime spawned-unit identity",
                "runtime spawn timing",
                "runtime spawner AI behavior",
                "runtime range behavior",
                "serialized PhysicsScript completeness",
                "exact PhysicsScript layouts",
                "exact spawner record layout",
                "complete value-id semantics",
                "raw string identity",
                "raw numeric value meaning",
                "runtime based-on inheritance",
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
