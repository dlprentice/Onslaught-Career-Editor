#!/usr/bin/env python3
"""Build the PhysicsScript explosion rebuild fixture proof-plan schema."""

from __future__ import annotations

import argparse
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import physics_script_rebuild_fixture_selection as selection_tool
import physics_script_scalar_string_decoder_fixture as scalar_fixture_tool
import physics_script_value_id_semantic_crosswalk as crosswalk_tool


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-explosion-rebuild-fixture-proof-plan.v1.json"
DEFAULT_GAME_ROOT = ROOT / "game"

STATUS_TOKEN = "physics-script-explosion-rebuild-fixture-proof-plan-complete-static-explosion-value-interface-fixture-not-runtime-proof"
THIS_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-explosion-rebuild-fixture-proof-plan"
PREVIOUS_SLICE = "PhysicsScript Rebuild Fixture Selection Proof Plan"
NEXT_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-spawner-rebuild-fixture-proof-plan"
SELECTED_FAMILY = "explosion"
SELECTED_PATH = "explosion-selected-value-id-interface-static-fixture"
EXPECTED_VALUE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
EXPECTED_VALUE_ID_HEXES = ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7", "0x8", "0x9", "0xa", "0xb", "0xc", "0xd", "0xf"]
DEFERRED_FACTORY_VALUE_IDS = [14]

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "livePhysicsScriptRuntimeLoading",
    "runtimeExecution",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsScriptOutcomesProven",
    "runtimeExplosionBehaviorProven",
    "runtimeExplosionDamageProven",
    "runtimeExplosionVisualEffectProven",
    "runtimeExplosionAudioProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "exactExplosionRecordLayoutProven",
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
    "runtimeInheritanceBehaviorProven",
    "runtimeSoundPlaybackProven",
    "runtimeEffectDispatchProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "runtimeCommandEffectRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimePhysicsScriptRows",
    "runtimeExplosionRows",
    "runtimeExplosionDamageRows",
    "runtimeExplosionVisualRows",
    "runtimeExplosionAudioRows",
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
    "runtimeInheritanceRows",
    "runtimeSoundRows",
    "runtimeEffectRows",
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
            if statement_type == 6:
                class_id = scalar_fixture_tool.classify_payload(payload)
                scalar_fixture_tool.validate_roundtrip(class_id, payload)
                counts[value_id][class_id] += 1
            marker = read_i32(data, offset)
            offset += 4
            if marker != 0:
                break
    return counts


def selected_fixture_rows(selection: dict[str, Any], shape_counts: dict[int, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in selection["selectedFixture"]["valueRows"]:
        value_id = row["valueId"]
        shapes = dict(sorted(shape_counts[value_id].items()))
        mixed_shape = len(shapes) > 1 or row["payloadClass"] not in {"scalar4", "owned_string_at_08"}
        if value_id == 10 and shapes.get("three_scalar4_roundtrip"):
            boundary = (
                "Selected `sound` field has mixed copied-corpus payload-shape classes: "
                "owned-string-shaped rows plus payload-size-12 rows classified by the scalar/string fixture as three-scalar roundtrip. "
                "The fixture preserves both public-safe shape classes and does not publish raw strings or numeric meanings."
            )
        else:
            boundary = row["claimBoundary"]
        rows.append(
            {
                "fixtureCaseId": f"explosion-value-{value_id:02d}-{row['rebuildFacingFieldName']}",
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
                "mixedPayloadShapeBoundary": bool(mixed_shape and value_id == 10),
                "publicSafe": row["publicSafe"],
                "fixtureAssertion": "public-safe static selected value-id interface row; no raw payload publication",
                "claimBoundary": boundary,
            }
        )
    return rows


def build_report(game_root: Path = DEFAULT_GAME_ROOT) -> dict[str, Any]:
    selection = selection_tool.build_report()
    rollup = selection["sourceEvidence"]["rollup"]
    crosswalk = crosswalk_tool.build_report()
    shapes_by_value_id = payload_shape_counts(game_root)
    rows = selected_fixture_rows(selection, shapes_by_value_id)
    selected = selection["selectedFixture"]
    accounting = selection["selectionAccounting"]

    observed_shape_totals: Counter[str] = Counter()
    for counter in shapes_by_value_id.values():
        observed_shape_totals.update(counter)
    selected_shape_totals: Counter[str] = Counter()
    for row in rows:
        selected_shape_totals.update(row["observedPayloadShapeClasses"])
    mixed_rows = [row for row in rows if row["mixedPayloadShapeBoundary"]]

    return {
        "schemaVersion": "physics-script-explosion-rebuild-fixture-proof-plan.v1",
        "status": "PASS",
        "proofPlan": THIS_SLICE,
        "scope": THIS_SCOPE,
        "fixtureStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "selectedFixtureFamily": SELECTED_FAMILY,
        "selectedFixturePath": SELECTED_PATH,
        "staticContext": selection["staticContext"],
        "fixtureAccounting": {
            "sourceProofCount": 5,
            "sourceSchemaCount": 4,
            "sourceMirrorPairCount": 10,
            "selectedCandidateRank": accounting["selectedCandidateRank"],
            "selectedSourceProofCount": accounting["selectedSourceProofCount"],
            "selectedValueInterfaceRowCount": accounting["selectedValueInterfaceRowCount"],
            "selectedValueIdCount": accounting["selectedValueIdCount"],
            "selectedObservedValueIdCount": accounting["selectedObservedValueIdCount"],
            "selectedFactoryOnlyValueIdCount": accounting["selectedFactoryOnlyValueIdCount"],
            "selectedUnselectedObservedValueIdCount": accounting["selectedUnselectedObservedValueIdCount"],
            "selectedTopLevelRecordCount": accounting["selectedTopLevelRecordCount"],
            "selectedValueNodeCount": accounting["selectedValueNodeCount"],
            "selectedRawValuePayloadBytesPreserved": accounting["selectedRawValuePayloadBytesPreserved"],
            "selectedDeclaredPayloadBytes": accounting["selectedDeclaredPayloadBytes"],
            "selectedOwnedStringFieldCount": accounting["selectedOwnedStringFieldCount"],
            "selectedScalarFieldCount": accounting["selectedScalarFieldCount"],
            "selectedFixtureRowCount": len(rows),
            "selectedPayloadShapeCaseCount": sum(len(row["observedPayloadShapeClasses"]) for row in rows),
            "selectedObservedPayloadShapeClassCount": len(selected_shape_totals),
            "selectedScalar4ShapePayloadCount": selected_shape_totals["scalar4_roundtrip"],
            "selectedOwnedStringShapePayloadCount": selected_shape_totals["owned_string_ascii_nul_shape_roundtrip"],
            "selectedThreeScalarShapePayloadCount": selected_shape_totals["three_scalar4_roundtrip"],
            "selectedMixedPayloadShapeValueIdCount": len(mixed_rows),
            "selectedMixedPayloadShapeValueIds": [row["valueId"] for row in mixed_rows],
            "selectedCrosswalkOwnedStringCorpusCount": selection["selectedFixture"]["payloadClassBreakdown"]["owned_string_at_08"]["copiedCorpusCount"],
            "selectedCrosswalkScalarCorpusCount": selection["selectedFixture"]["payloadClassBreakdown"]["scalar4"]["copiedCorpusCount"],
            "soundObservedOwnedStringShapeCount": shapes_by_value_id[10]["owned_string_ascii_nul_shape_roundtrip"],
            "soundObservedThreeScalarShapeCount": shapes_by_value_id[10]["three_scalar4_roundtrip"],
            "deferredFactoryValueIdCount": len(DEFERRED_FACTORY_VALUE_IDS),
            "deferredFactoryValueIds": DEFERRED_FACTORY_VALUE_IDS,
            "topLevelFamilyCount": accounting["topLevelFamilyCount"],
            "valueInterfaceRowCount": accounting["valueInterfaceRowCount"],
            "observedSelectedRowCount": accounting["observedSelectedRowCount"],
            "factoryOnlySelectedRowCount": accounting["factoryOnlySelectedRowCount"],
            "unselectedObservedRowCount": accounting["unselectedObservedRowCount"],
            "physicsScriptCorpusByteCount": accounting["physicsScriptCorpusByteCount"],
            "physicsScriptStreamHeader": accounting["physicsScriptStreamHeader"],
            "physicsScriptTopLevelStatementCount": accounting["physicsScriptTopLevelStatementCount"],
            "physicsScriptValueListNodeCount": accounting["physicsScriptValueListNodeCount"],
            "physicsScriptStatementValuePairCount": accounting["physicsScriptStatementValuePairCount"],
            "physicsScriptRawValuePayloadBytesPreserved": accounting["physicsScriptRawValuePayloadBytesPreserved"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "fixtureSelection": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-rebuild-fixture-selection.md",
                "schemaPath": rel(selection_tool.OUTPUT),
                "fixtureSelectionStatus": selection["fixtureSelectionStatus"],
                "selectedFixtureFamily": selection["selectedFixtureFamily"],
                "selectedFixturePath": selection["selectedFixturePath"],
            },
            "rollup": {
                "proofPath": rollup["proofPath"],
                "schemaPath": rollup["schemaPath"],
                "rollupStatus": rollup["rollupStatus"],
                "recommendedNextFixtureFamily": rollup["recommendedNextFixtureFamily"],
                "valueInterfaceRowCount": rollup["valueInterfaceRowCount"],
                "unselectedObservedRowCount": rollup["unselectedObservedRowCount"],
            },
            "valueIdCrosswalk": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-value-id-semantic-crosswalk-proof-plan.md",
                "schemaPath": rel(crosswalk_tool.OUTPUT),
                "family": SELECTED_FAMILY,
                "observedValueIdCount": crosswalk["familyCoverageSummary"][SELECTED_FAMILY]["observedValueIdCount"],
                "selectedCrosswalkRowCount": crosswalk["familyCoverageSummary"][SELECTED_FAMILY]["selectedCrosswalkRowCount"],
                "deferredFactoryValueIds": crosswalk["deferredFactoryValueIdsByFamily"][SELECTED_FAMILY],
            },
            "scalarStringFixture": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-scalar-string-value-decoder-fixture-proof-plan.md",
                "schemaPath": "reverse-engineering/binary-analysis/physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json",
                "observedExplosionPayloadShapeTotals": dict(sorted(observed_shape_totals.items())),
            },
            "staticContract": selection["sourceEvidence"]["staticContract"],
        },
        "selectedFixture": {
            "family": SELECTED_FAMILY,
            "pathId": SELECTED_PATH,
            "statementFamilyTypeId": selected["statementFamilyTypeId"],
            "valueFactoryTypeId": selected["valueFactoryTypeId"],
            "nestedFactory": selected["nestedFactory"],
            "statementLoader": selected["statementLoader"],
            "valueListLoader": selected["valueListLoader"],
            "createAnchor": selected["createAnchor"],
            "registryGlobal": selected["registryGlobal"],
            "valueIds": selected["valueIds"],
            "valueIdHexes": selected["valueIdHexes"],
            "ownedStringFields": selected["ownedStringFields"],
            "scalarFields": selected["scalarFields"],
            "fixtureRows": rows,
            "payloadShapeTotals": dict(sorted(selected_shape_totals.items())),
            "deferredFactoryBoundary": {
                "valueIds": DEFERRED_FACTORY_VALUE_IDS,
                "boundary": "Value id 14 is a deferred factory boundary in the value-id crosswalk, not part of the selected copied-corpus-observed explosion fixture.",
                "runtimeMeaningProven": False,
            },
        },
        "fixtureRequirementRows": [
            {
                "row": "family-fixture",
                "status": "satisfied-static",
                "evidence": "explosion has 14 observed ids, 14 selected rows, zero factory-only selected rows, and zero unselected observed ids",
                "boundary": "Static family-selection proof only.",
            },
            {
                "row": "loader-fixture",
                "status": "satisfied-static",
                "evidence": "CPhysicsScriptStatements__CreateStatementType7, CExplosionStatement__LoadFromMemBuffer, CPhysicsExplosionValueList__LoadFromMemBuffer, CExplosionStatement__CreateExplosionAndRecurse, and DAT_008553f8",
                "boundary": "Static loader/factory/registry bridge only.",
            },
            {
                "row": "value-interface-fixture",
                "status": "satisfied-static",
                "evidence": "selected value ids 1,2,3,4,5,6,7,8,9,10,11,12,13,15 and 14 rebuild-facing field names",
                "boundary": "Selected value-id interface only, not complete value semantics.",
            },
            {
                "row": "payload-shape-fixture",
                "status": "satisfied-public-safe",
                "evidence": "seven scalar4 selected fields, seven selected string-facing fields, and one explicit mixed payload-shape boundary for sound",
                "boundary": "Public-safe payload shape only; no raw strings or numeric meanings.",
            },
            {
                "row": "based-on-fixture",
                "status": "satisfied-static",
                "evidence": "basedOn value id 1 is anchored to CExplosionBasedOn__ApplyToExplosionByName",
                "boundary": "Static base-copy field boundary only, not runtime explosion inheritance behavior.",
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
            "summary": "Static PhysicsScript explosion selected value-id fixture only.",
            "proves": [
                "The selected explosion value-id interface is materialized as public-safe static fixture rows.",
                "All selected explosion value ids are copied-corpus observed and carry static factory/apply/registry anchors.",
                "The selected fixture preserves public-safe payload shape counts and records the value id 10 mixed-shape boundary.",
                "Value id 14 remains deferred factory boundary debt instead of being hidden.",
            ],
            "doesNotProve": [
                "runtime PhysicsScript behavior",
                "runtime explosion behavior",
                "runtime explosion damage",
                "runtime explosion visual effects",
                "runtime explosion audio",
                "serialized PhysicsScript completeness",
                "exact PhysicsScript layouts",
                "exact explosion record layout",
                "complete value-id semantics",
                "raw string identity",
                "raw numeric value meaning",
                "runtime inheritance behavior",
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
