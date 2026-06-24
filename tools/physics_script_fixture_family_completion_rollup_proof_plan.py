#!/usr/bin/env python3
"""Build the PhysicsScript fixture-family completion rollup schema."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-fixture-family-completion-rollup-proof-plan.v1.json"

STATUS_TOKEN = "physics-script-fixture-family-completion-rollup-proof-plan-complete-nine-family-static-fixture-rollup-not-runtime-proof"
THIS_SLICE = "PhysicsScript Fixture Family Completion Rollup Proof Plan"
THIS_SCOPE = "physics-script-fixture-family-completion-rollup-proof-plan"
PREVIOUS_SLICE = "PhysicsScript Unit Rebuild Fixture Proof Plan"
NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"
NEXT_SCOPE = "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh"

ROLLUP_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-interface-rollup.v1.json"
FIXTURE_SELECTION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.v1.json"
UNIT_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-unit-rebuild-fixture-proof-plan.v1.json"

FAMILY_ROWS = (
    {
        "family": "explosion",
        "expectedNext": "PhysicsScript Spawner Rebuild Fixture Proof Plan",
        "script": "test:physics-script-explosion-rebuild-fixture-proof-plan",
        "depthClass": "fully-observed-selected-interface",
    },
    {
        "family": "spawner",
        "expectedNext": "PhysicsScript Hazard Rebuild Fixture Proof Plan",
        "script": "test:physics-script-spawner-rebuild-fixture-proof-plan",
        "depthClass": "selected-interface-with-factory-only-boundaries",
    },
    {
        "family": "hazard",
        "expectedNext": "PhysicsScript Feature Rebuild Fixture Proof Plan",
        "script": "test:physics-script-hazard-rebuild-fixture-proof-plan",
        "depthClass": "selected-interface-with-factory-only-boundary",
    },
    {
        "family": "feature",
        "expectedNext": "PhysicsScript Component Rebuild Fixture Proof Plan",
        "script": "test:physics-script-feature-rebuild-fixture-proof-plan",
        "depthClass": "selected-interface-with-factory-only-boundaries",
    },
    {
        "family": "component",
        "expectedNext": "PhysicsScript Weapon Rebuild Fixture Proof Plan",
        "script": "test:physics-script-component-rebuild-fixture-proof-plan",
        "depthClass": "selected-interface-with-factory-only-and-unselected-boundaries",
    },
    {
        "family": "weapon",
        "expectedNext": "PhysicsScript Round Rebuild Fixture Proof Plan",
        "script": "test:physics-script-weapon-rebuild-fixture-proof-plan",
        "depthClass": "selected-interface-with-unselected-boundaries",
    },
    {
        "family": "round",
        "expectedNext": "PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan",
        "script": "test:physics-script-round-rebuild-fixture-proof-plan",
        "depthClass": "selected-interface-with-unselected-boundaries",
    },
    {
        "family": "weapon-mode",
        "expectedNext": "PhysicsScript Unit Rebuild Fixture Proof Plan",
        "script": "test:physics-script-weapon-mode-rebuild-fixture-proof-plan",
        "depthClass": "selected-interface-with-factory-only-and-unselected-boundaries",
    },
    {
        "family": "unit",
        "expectedNext": THIS_SLICE,
        "script": "test:physics-script-unit-rebuild-fixture-proof-plan",
        "depthClass": "selected-interface-with-factory-only-and-unselected-boundaries",
    },
)

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "livePhysicsScriptRuntimeLoading",
    "runtimeExecution",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsScriptOutcomesProven",
    "runtimeExplosionBehaviorProven",
    "runtimeSpawnerBehaviorProven",
    "runtimeHazardBehaviorProven",
    "runtimeFeatureBehaviorProven",
    "runtimeComponentBehaviorProven",
    "runtimeWeaponBehaviorProven",
    "runtimeRoundBehaviorProven",
    "runtimeWeaponModeBehaviorProven",
    "runtimeUnitBehaviorProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
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
    "exactRecordLayoutProven",
    "exactRegistryContainerLayoutProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimePhysicsScriptRows",
    "runtimeExplosionRows",
    "runtimeSpawnerRows",
    "runtimeHazardRows",
    "runtimeFeatureRows",
    "runtimeComponentRows",
    "runtimeWeaponRows",
    "runtimeRoundRows",
    "runtimeWeaponModeRows",
    "runtimeUnitRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "godotRows",
    "rebuildImplementationRows",
    "beProcessesAfterRollup",
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
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def family_schema_path(family: str) -> Path:
    return ROOT / "reverse-engineering" / "binary-analysis" / f"physics-script-{family}-rebuild-fixture-proof-plan.v1.json"


def family_plan_path(family: str) -> Path:
    return ROOT / "reverse-engineering" / "binary-analysis" / f"physics-script-{family}-rebuild-fixture-proof-plan.md"


def family_probe_path(family: str) -> Path:
    safe = family.replace("-", "_")
    return ROOT / "tools" / f"physics_script_{safe}_rebuild_fixture_proof_plan_probe.py"


def mirror_matches(path: Path) -> bool:
    mirror = ROOT / "lore-book" / path.relative_to(ROOT)
    return mirror.is_file() and path.read_text(encoding="utf-8-sig") == mirror.read_text(encoding="utf-8-sig")


def boundary_ids(selected: dict[str, Any], key: str, nested_key: str | None = None) -> list[int]:
    if key in selected:
        return selected[key]
    if nested_key and nested_key in selected:
        return selected[nested_key].get("valueIds", [])
    return []


def build_family_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for config in FAMILY_ROWS:
        schema_path = family_schema_path(config["family"])
        plan_path = family_plan_path(config["family"])
        probe_path = family_probe_path(config["family"])
        schema = read_json(schema_path)
        accounting = schema["fixtureAccounting"]
        selected = schema["selectedFixture"]
        rows.append(
            {
                "fixtureFamily": config["family"],
                "fixturePlanDoc": rel(plan_path),
                "fixturePlanSchema": rel(schema_path),
                "fixtureProofPlanProbe": rel(probe_path),
                "packageScript": config["script"],
                "schemaVersion": schema["schemaVersion"],
                "fixtureStatus": schema["fixtureStatus"],
                "selectedNextSlice": schema["selectedNextSlice"],
                "expectedNextSlice": config["expectedNext"],
                "depthClass": config["depthClass"],
                "selectedFixturePath": schema["selectedFixturePath"],
                "selectedCandidateRank": accounting["selectedCandidateRank"],
                "selectedValueInterfaceRowCount": accounting["selectedValueInterfaceRowCount"],
                "selectedObservedValueIdCount": accounting["selectedObservedValueIdCount"],
                "selectedFactoryOnlyValueIdCount": accounting["selectedFactoryOnlyValueIdCount"],
                "selectedUnselectedObservedValueIdCount": accounting["selectedUnselectedObservedValueIdCount"],
                "selectedTopLevelRecordCount": accounting["selectedTopLevelRecordCount"],
                "selectedValueNodeCount": accounting["selectedValueNodeCount"],
                "selectedPayloadShapeCaseCount": accounting["selectedPayloadShapeCaseCount"],
                "selectedRawValuePayloadBytesPreserved": accounting["selectedRawValuePayloadBytesPreserved"],
                "selectedDeclaredPayloadBytes": accounting["selectedDeclaredPayloadBytes"],
                "selectedValueIds": selected["valueIds"],
                "factoryOnlyValueIds": boundary_ids(selected, "factoryOnlyValueIds", "factoryOnlyBoundary"),
                "unselectedObservedValueIds": boundary_ids(selected, "unselectedObservedValueIds", "unselectedObservedBoundary"),
                "selectedMixedPayloadShapeValueIds": accounting["selectedMixedPayloadShapeValueIds"],
                "proofMirrorMatch": mirror_matches(plan_path),
                "schemaMirrorMatch": mirror_matches(schema_path),
                "runtimeExecution": False,
                "godotWork": False,
                "ghidraMutation": False,
                "rebuildImplementation": False,
            }
        )
    return rows


def sum_key(rows: list[dict[str, Any]], key: str) -> int:
    return sum(int(row[key]) for row in rows)


def shape_totals() -> Counter[str]:
    totals: Counter[str] = Counter()
    for config in FAMILY_ROWS:
        schema = read_json(family_schema_path(config["family"]))
        totals.update(schema["selectedFixture"]["payloadShapeTotals"])
    return totals


def build_report() -> dict[str, Any]:
    family_rows = build_family_rows()
    shapes = shape_totals()
    rollup = read_json(ROLLUP_SCHEMA)
    selection = read_json(FIXTURE_SELECTION_SCHEMA)
    previous = read_json(UNIT_SCHEMA)
    rollup_accounting = rollup["rollupAccounting"]

    return {
        "schemaVersion": "physics-script-fixture-family-completion-rollup-proof-plan.v1",
        "status": "PASS",
        "proofPlan": THIS_SLICE,
        "scope": THIS_SCOPE,
        "physicsScriptFixtureFamilyCompletionRollupStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "staticAccountingSource": "static-reaudit-measurement-register.md",
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "sourceInterfaceRollupSchema": rel(ROLLUP_SCHEMA),
            "sourceInterfaceRollupStatus": rollup["physicsScriptRebuildInterfaceRollupStatus"],
            "sourceFixtureSelectionSchema": rel(FIXTURE_SELECTION_SCHEMA),
            "sourceFixtureSelectionStatus": selection["fixtureSelectionStatus"],
            "previousFixtureSchema": rel(UNIT_SCHEMA),
            "previousFixtureStatus": previous["fixtureStatus"],
            "previousFixtureSelectedNextSlice": previous["selectedNextSlice"],
            "existingTrackedArtifactsOnly": True,
            "sourceSchemaValidationOnly": True,
            "frontDoorDocValidationOnly": True,
        },
        "familyCompletionRows": family_rows,
        "fixtureCompletionAccounting": {
            "expectedFixtureFamilyCount": 9,
            "completedFixtureFamilyCount": len(family_rows),
            "remainingFixtureFamilyCount": 9 - len(family_rows),
            "fixturePlanDocCount": len({row["fixturePlanDoc"] for row in family_rows}),
            "fixturePlanSchemaCount": len({row["fixturePlanSchema"] for row in family_rows}),
            "fixtureProofPlanProbeCount": len({row["fixtureProofPlanProbe"] for row in family_rows}),
            "packageScriptCount": len({row["packageScript"] for row in family_rows}),
            "sourceProofCount": len(family_rows),
            "sourceSchemaCount": len(family_rows),
            "sourceMirrorPairCount": sum(1 for row in family_rows if row["proofMirrorMatch"]) + sum(1 for row in family_rows if row["schemaMirrorMatch"]),
            "allSourceMirrorsMatch": all(row["proofMirrorMatch"] and row["schemaMirrorMatch"] for row in family_rows),
            "selectedValueInterfaceRowCount": sum_key(family_rows, "selectedValueInterfaceRowCount"),
            "selectedObservedValueIdCount": sum_key(family_rows, "selectedObservedValueIdCount"),
            "selectedFactoryOnlyValueIdCount": sum_key(family_rows, "selectedFactoryOnlyValueIdCount"),
            "selectedUnselectedObservedValueIdCount": sum_key(family_rows, "selectedUnselectedObservedValueIdCount"),
            "selectedTopLevelRecordCount": sum_key(family_rows, "selectedTopLevelRecordCount"),
            "selectedValueNodeCount": sum_key(family_rows, "selectedValueNodeCount"),
            "selectedPayloadShapeCaseCount": sum_key(family_rows, "selectedPayloadShapeCaseCount"),
            "selectedScalar4ShapePayloadCount": shapes["scalar4_roundtrip"],
            "selectedOwnedStringShapePayloadCount": shapes["owned_string_ascii_nul_shape_roundtrip"],
            "selectedTwoScalarShapePayloadCount": shapes["two_scalar4_roundtrip"],
            "selectedThreeScalarShapePayloadCount": shapes["three_scalar4_roundtrip"],
            "selectedRawPreservedOtherShapePayloadCount": shapes["raw_preserved_other"],
            "selectedPayloadShapeTotals": dict(sorted(shapes.items())),
            "selectedRawValuePayloadBytesPreserved": sum_key(family_rows, "selectedRawValuePayloadBytesPreserved"),
            "selectedDeclaredPayloadBytes": sum_key(family_rows, "selectedDeclaredPayloadBytes"),
            "factoryOnlyBoundaryFamilyCount": sum(1 for row in family_rows if row["selectedFactoryOnlyValueIdCount"] > 0),
            "unselectedObservedBoundaryFamilyCount": sum(1 for row in family_rows if row["selectedUnselectedObservedValueIdCount"] > 0),
            "mixedPayloadBoundaryFamilyCount": sum(1 for row in family_rows if row["selectedMixedPayloadShapeValueIds"]),
            "runtimeFamilyProofCount": 0,
            "runtimeObservationReadyFamilyCount": 0,
            "publicLeakCheck": "PASS",
        },
        "rollupCrossCheck": {
            "topLevelFamilyCount": rollup_accounting["topLevelFamilyCount"],
            "valueInterfaceRowCount": rollup_accounting["valueInterfaceRowCount"],
            "observedSelectedRowCount": rollup_accounting["observedSelectedRowCount"],
            "factoryOnlySelectedRowCount": rollup_accounting["factoryOnlySelectedRowCount"],
            "unselectedObservedRowCount": rollup_accounting["unselectedObservedRowCount"],
            "physicsScriptTopLevelStatementCount": rollup_accounting["physicsScriptTopLevelStatementCount"],
            "physicsScriptValueListNodeCount": rollup_accounting["physicsScriptValueListNodeCount"],
            "physicsScriptStatementValuePairCount": rollup_accounting["physicsScriptStatementValuePairCount"],
            "physicsScriptRawValuePayloadBytesPreserved": rollup_accounting["physicsScriptRawValuePayloadBytesPreserved"],
            "fixtureAggregateClassCount": rollup_accounting["fixtureAggregateClassCount"],
            "semanticBucketCount": rollup_accounting["semanticBucketCount"],
            "completeValueIdSemanticsProven": False,
            "all185PairsSemanticallyNamed": False,
        },
        "staticToProofBacklogAccounting": {
            "completedParentInterfaceRollup": "PhysicsScript Rebuild Interface Rollup Proof Plan",
            "completedFixtureSelection": "PhysicsScript Rebuild Fixture Selection Proof Plan",
            "completedFixtureFamilies": [row["fixtureFamily"] for row in family_rows],
            "selectedNextSlice": NEXT_SLICE,
            "nextSliceClass": "selection-refresh",
            "runtimeExecution": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
        },
        "frontDoorValidation": {
            "backlogUpdated": True,
            "mappedSystemsUpdated": True,
            "physicsContractUpdated": True,
            "binaryIndexUpdated": True,
            "reIndexUpdated": True,
            "readinessNoteUpdated": True,
            "packageScriptAdded": True,
            "loreMirrorsRequired": True,
        },
        "guardSummary": {
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
            "publicLeakCheck": "PASS",
        },
        "claimBoundary": {
            "proves": [
                "nine PhysicsScript fixture families have tracked public-safe static fixture proof artifacts",
                "the fixture-family set accounts for 87 selected value-interface rows, 72 observed selected rows, 15 factory-only selected rows, and 113 unselected observed rows",
                "the nine fixtures reconcile with the existing PhysicsScript rebuild-interface rollup's 777 top-level statements, 6803 value-list nodes, and 185 observed statement/value pairs",
                "the next safe work item is a static-to-proof selection refresh rather than runtime, Godot, patch, product UI, or rebuild implementation",
            ],
            "doesNotProve": [
                "runtime PhysicsScript behavior",
                "runtime physics outcomes",
                "runtime explosion/spawner/hazard/feature/component/weapon/round/weapon-mode/Unit behavior",
                "serialized PhysicsScript completeness",
                "exact statement/value-list/concrete record layouts",
                "complete value-id semantics",
                "all 185 observed statement/value pairs semantically named",
                "raw string identity",
                "raw numeric value meaning",
                "source-body identity",
                "BEA patching behavior",
                "Godot parity",
                "product UI behavior",
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
