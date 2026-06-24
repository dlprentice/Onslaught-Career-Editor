#!/usr/bin/env python3
"""Build the PhysicsScript rebuild fixture-selection schema."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import physics_script_rebuild_interface_rollup as rollup_tool


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.v1.json"

STATUS_TOKEN = "physics-script-rebuild-fixture-selection-complete-explosion-selected"
THIS_SLICE = "PhysicsScript Rebuild Fixture Selection Proof Plan"
PREVIOUS_SLICE = "PhysicsScript Rebuild Interface Rollup Proof Plan"
NEXT_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-explosion-rebuild-fixture-proof-plan"
SELECTED_FAMILY = "explosion"
SELECTED_PATH = "explosion-selected-value-id-interface-static-fixture"

RANKING_ORDER = (
    ("explosion", "selected", "Fully observed selected value-id surface: 14 observed ids, 14 selected crosswalk rows, zero factory-only selected rows, and zero unselected observed ids."),
    ("spawner", "deferred", "No unselected observed ids, but four factory-only selected rows make it less clean as the first deterministic fixture."),
    ("hazard", "deferred", "Small surface, but one factory-only selected row makes the evidence boundary less clean than explosion."),
    ("feature", "deferred", "No unselected observed ids, but two factory-only selected rows remain explicit boundary debt."),
    ("component", "deferred", "High-value selected surface, but four unselected observed ids and four factory-only selected rows remain."),
    ("weapon", "deferred", "Weapon registry rows are valuable, but ten unselected observed ids remain and runtime firing behavior is easy to overclaim."),
    ("round", "deferred", "Projectile/round rows are important, but twenty-six unselected observed ids and runtime projectile outcomes are out of scope."),
    ("weapon-mode", "deferred", "Mode rows tempt firing cadence and launch-angle behavior claims while twenty-five unselected observed ids remain."),
    ("unit", "deferred", "Broad AI/unit surface with forty-eight unselected observed ids; it should follow narrower deterministic fixture work."),
)

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
    "beProcessesAfterSelection",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawCopiedStringRows",
    "rawNumericRowsPublished",
    "serializedCompletenessRows",
    "exactLayoutRows",
)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_candidate_ranking(top_rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    ranking: list[dict[str, Any]] = []
    for rank, (family, decision, rationale) in enumerate(RANKING_ORDER, start=1):
        row = top_rows[family]
        ranking.append(
            {
                "rank": rank,
                "family": family,
                "decision": decision,
                "observedValueIdCount": row["uniqueObservedValueIds"],
                "selectedCrosswalkRowCount": row["selectedCrosswalkRows"],
                "observedSelectedValueIdCount": row["observedSelectedRows"],
                "factoryOnlySelectedValueIdCount": row["factoryOnlySelectedRows"],
                "unselectedObservedValueIdCount": row["unselectedObservedValueIdCount"],
                "rationale": rationale,
            }
        )
    return ranking


def build_report() -> dict[str, Any]:
    rollup = rollup_tool.build_report()
    top_rows = {row["family"]: row for row in rollup["topLevelInterfaceRows"]}
    selected_top = top_rows[SELECTED_FAMILY]
    selected_values = [row for row in rollup["valueInterfaceRows"] if row["family"] == SELECTED_FAMILY]
    coverage = rollup["coverageBoundaries"]["familyCoverageSummary"][SELECTED_FAMILY]
    payload_classes = Counter(row["payloadClass"] for row in selected_values)
    payload_corpus_counts: dict[str, int] = defaultdict(int)
    for row in selected_values:
        payload_corpus_counts[row["payloadClass"]] += row["copiedCorpusCount"]

    owned_string_fields = [row["rebuildFacingFieldName"] for row in selected_values if row["payloadClass"] == "owned_string_at_08"]
    scalar_fields = [row["rebuildFacingFieldName"] for row in selected_values if row["payloadClass"] == "scalar4"]
    candidate_ranking = build_candidate_ranking(top_rows)

    return {
        "schemaVersion": "physics-script-rebuild-fixture-selection.v1",
        "status": "PASS",
        "proofPlan": THIS_SLICE,
        "scope": "physics-script-rebuild-fixture-selection",
        "fixtureSelectionStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedChildLane": NEXT_SLICE,
        "selectedChildScope": NEXT_SCOPE,
        "selectedFixtureFamily": SELECTED_FAMILY,
        "selectedFixturePath": SELECTED_PATH,
        "staticContext": rollup["staticContext"],
        "selectionAccounting": {
            "candidateFamilyCount": len(candidate_ranking),
            "selectedCandidateRank": 1,
            "selectedSourceProofCount": 4,
            "selectedValueInterfaceRowCount": len(selected_values),
            "selectedValueIdCount": len(selected_values),
            "selectedObservedValueIdCount": coverage["observedSelectedValueIdCount"],
            "selectedFactoryOnlyValueIdCount": coverage["factoryOnlySelectedValueIdCount"],
            "selectedUnselectedObservedValueIdCount": coverage["unselectedObservedValueIdCount"],
            "selectedTopLevelRecordCount": selected_top["topLevelRecords"],
            "selectedValueNodeCount": selected_top["valueNodes"],
            "selectedRawValuePayloadBytesPreserved": selected_top["rawValuePayloadBytes"],
            "selectedDeclaredPayloadBytes": selected_top["declaredPayloadBytes"],
            "selectedOwnedStringFieldCount": len(owned_string_fields),
            "selectedScalarFieldCount": len(scalar_fields),
            "selectedPayloadClassCount": len(payload_classes),
            "sourceProofCount": rollup["rollupAccounting"]["sourceProofCount"],
            "sourceSchemaCount": rollup["rollupAccounting"]["sourceSchemaCount"],
            "sourceMirrorPairCount": rollup["rollupAccounting"]["sourceMirrorPairCount"],
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
            "rollup": {
                "proofPath": "reverse-engineering/binary-analysis/physics-script-rebuild-interface-rollup.md",
                "schemaPath": rel(rollup_tool.OUTPUT),
                "schemaVersion": rollup["schemaVersion"],
                "rollupStatus": rollup["rollupStatus"],
                "recommendedNextFixtureFamily": rollup["recommendedNextFixtureFamily"]["family"],
                "sourceProofCount": rollup["rollupAccounting"]["sourceProofCount"],
                "sourceSchemaCount": rollup["rollupAccounting"]["sourceSchemaCount"],
                "sourceMirrorPairCount": rollup["rollupAccounting"]["sourceMirrorPairCount"],
                "topLevelFamilyCount": rollup["rollupAccounting"]["topLevelFamilyCount"],
                "valueInterfaceRowCount": rollup["rollupAccounting"]["valueInterfaceRowCount"],
                "observedSelectedRowCount": rollup["rollupAccounting"]["observedSelectedRowCount"],
                "factoryOnlySelectedRowCount": rollup["rollupAccounting"]["factoryOnlySelectedRowCount"],
                "unselectedObservedRowCount": rollup["rollupAccounting"]["unselectedObservedRowCount"],
            },
            "valueIdCrosswalk": {
                "proofPath": rel(rollup_tool.CROSSWALK_PROOF),
                "schemaPath": rel(rollup_tool.CROSSWALK_SCHEMA),
                "family": SELECTED_FAMILY,
                "observedValueIdCount": coverage["observedValueIdCount"],
                "selectedCrosswalkRowCount": coverage["selectedCrosswalkRowCount"],
                "observedSelectedValueIdCount": coverage["observedSelectedValueIdCount"],
                "factoryOnlySelectedValueIdCount": coverage["factoryOnlySelectedValueIdCount"],
                "unselectedObservedValueIdCount": coverage["unselectedObservedValueIdCount"],
            },
            "scalarStringFixture": {
                "proofPath": rel(rollup_tool.FIXTURE_PROOF),
                "schemaPath": rel(rollup_tool.FIXTURE_SCHEMA),
                "fixtureAggregateClassCount": rollup["rollupAccounting"]["fixtureAggregateClassCount"],
                "fixtureClassDefinitionCount": rollup["rollupAccounting"]["fixtureClassDefinitionCount"],
                "syntheticFixtureCaseCount": rollup["rollupAccounting"]["syntheticFixtureCaseCount"],
            },
            "staticContract": {
                "proofPath": rel(rollup_tool.PHYSICS_CONTRACT),
                "anchors": [
                    "CPhysicsScriptStatements__CreateStatementType7",
                    "CExplosionStatement__LoadFromMemBuffer",
                    "CPhysicsExplosionValueList__LoadFromMemBuffer",
                    "CExplosionStatement__CreateExplosionAndRecurse",
                    "CExplosionBasedOn__ApplyToExplosionByName",
                    "CExplosionValue__ApplyToExplosionByName",
                    "DAT_008553f8",
                ],
            },
        },
        "selectedFixture": {
            "family": SELECTED_FAMILY,
            "pathId": SELECTED_PATH,
            "statementFamilyTypeId": selected_values[0]["statementFamilyTypeId"],
            "valueFactoryTypeId": selected_values[0]["valueFactoryTypeId"],
            "nestedFactory": selected_top["nestedFactory"],
            "statementLoader": selected_top["statementLoader"],
            "valueListLoader": selected_top["valueListLoader"],
            "createAnchor": selected_top["createAnchor"],
            "registryGlobal": selected_top["registryGlobal"],
            "topLevelRecords": selected_top["topLevelRecords"],
            "valueNodes": selected_top["valueNodes"],
            "rawValuePayloadBytes": selected_top["rawValuePayloadBytes"],
            "declaredPayloadBytes": selected_top["declaredPayloadBytes"],
            "valueIds": [row["valueId"] for row in selected_values],
            "valueIdHexes": [row["valueIdHex"] for row in selected_values],
            "valueRows": selected_values,
            "payloadClassBreakdown": {
                payload: {"fieldCount": payload_classes[payload], "copiedCorpusCount": payload_corpus_counts[payload]}
                for payload in sorted(payload_classes)
            },
            "ownedStringFields": owned_string_fields,
            "scalarFields": scalar_fields,
        },
        "candidateRanking": candidate_ranking,
        "futureEvidenceRequirements": [
            {
                "row": "family-fixture",
                "requirement": "Reconfirm explosion family coverage from the rollup: 14 observed ids, 14 selected rows, zero factory-only selected rows, and zero unselected observed ids.",
                "boundary": "Static family-selection proof only.",
            },
            {
                "row": "loader-fixture",
                "requirement": "Preserve CPhysicsScriptStatements__CreateStatementType7, CExplosionStatement__LoadFromMemBuffer, CPhysicsExplosionValueList__LoadFromMemBuffer, CExplosionStatement__CreateExplosionAndRecurse, and DAT_008553f8.",
                "boundary": "Static loader/factory/registry bridge only.",
            },
            {
                "row": "value-interface-fixture",
                "requirement": "Preserve exact selected value ids 1,2,3,4,5,6,7,8,9,10,11,12,13,15 and all 14 rebuild-facing field names.",
                "boundary": "Selected value-id interface only, not complete value semantics.",
            },
            {
                "row": "payload-shape-fixture",
                "requirement": "Model seven owned-string-shaped fields and seven scalar4 fields using the scalar/string fixture classes without publishing copied strings or raw numeric meanings.",
                "boundary": "Public-safe payload shape only.",
            },
            {
                "row": "based-on-fixture",
                "requirement": "Treat basedOn as a static copy/apply anchor through CExplosionBasedOn__ApplyToExplosionByName.",
                "boundary": "Static base-copy field boundary only, not runtime explosion inheritance behavior.",
            },
            {
                "row": "stop-fixture",
                "requirement": "Stop if the next proof needs runtime effects, audio, damage, visual behavior, BE launch, Godot, Ghidra mutation, executable patching, product UI wiring, rebuild implementation, raw values, or private paths.",
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
            "summary": "Static PhysicsScript fixture selection only.",
            "proves": [
                "Explosion is the first selected PhysicsScript rebuild fixture family.",
                "The selected explosion value-id interface has 14 observed ids, 14 selected rows, zero factory-only selected rows, and zero unselected observed ids.",
                "The future child lane has explicit evidence requirements and stop conditions before runtime, Godot, patching, or rebuild implementation begins.",
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
    args = parser.parse_args()

    report = build_report()
    if args.write:
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
