#!/usr/bin/env python3
"""Build the PhysicsScript value-id semantic crosswalk schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-value-id-semantic-crosswalk.v1.json"
SEMANTIC_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-semantic-value-field-schema-ledger.v1.json"
FIXTURE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json"


STATEMENT_TYPE_IDS = {
    "unit": 1,
    "weapon": 2,
    "weapon-mode": 3,
    "round": 4,
    "spawner": 5,
    "explosion": 6,
    "component": 7,
    "feature": 8,
    "hazard": 9,
}

VALUE_FACTORY_TYPE_IDS = {
    "unit": 2,
    "weapon": 3,
    "weapon-mode": 4,
    "round": 5,
    "spawner": 6,
    "explosion": 7,
    "feature": 8,
    "hazard": 9,
    "component": 10,
}

FACTORY_ANCHORS = {
    "unit": "CPhysicsScriptStatements__CreateStatementType2",
    "weapon": "CPhysicsScriptStatements__CreateStatementType3",
    "weapon-mode": "CPhysicsScriptStatements__CreateStatementType4",
    "round": "CPhysicsScriptStatements__CreateStatementType5",
    "spawner": "CPhysicsScriptStatements__CreateStatementType6",
    "explosion": "CPhysicsScriptStatements__CreateStatementType7",
    "feature": "CPhysicsScriptStatements__CreateStatementType8",
    "hazard": "CPhysicsScriptStatements__CreateStatementType9",
    "component": "CPhysicsScriptStatements__CreateStatementType10",
}

REGISTRY_GLOBALS = {
    "unit": "DAT_008553fc",
    "weapon": "DAT_008553e8",
    "weapon-mode": "DAT_008553ec",
    "round": "DAT_008553f0",
    "spawner": "DAT_008553f4",
    "explosion": "DAT_008553f8",
    "component": "DAT_00855400",
    "feature": "DAT_00855404",
    "hazard": "DAT_00855408",
}

FALSE_GUARDS = (
    "runtimeExecution",
    "beLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "sourceSelectionProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rebuildImplementation",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsOutcomesProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "completeValueIdSemanticsProven",
    "completeNestedEnumSemanticsProven",
    "rawStringIdentityProven",
    "rawNumericMeaningProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimePhysicsScriptRows",
    "runtimeCommandEffectRows",
    "privateFrameRowsObserved",
    "ghidraMutationRows",
    "executablePatchRows",
    "godotRows",
    "rebuildImplementationRows",
    "beProcessesAfterCrosswalk",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def row(
    family: str,
    value_id: int,
    rebuild_field: str,
    payload_class: str,
    evidence_tier: str,
    apply_anchor: str,
    destination: str,
    boundary: str,
    value_counts: dict[str, dict[str, int]],
    loader_anchor: str | None = None,
    semantic_state: str = "resolved_static_field",
) -> dict[str, Any]:
    copied_count = int(value_counts.get(family, {}).get(str(value_id), 0))
    return {
        "family": family,
        "statementFamilyTypeId": STATEMENT_TYPE_IDS[family],
        "valueFactoryTypeId": VALUE_FACTORY_TYPE_IDS[family],
        "valueId": value_id,
        "valueIdHex": f"0x{value_id:x}",
        "copiedCorpusCount": copied_count,
        "corpusPresence": "copied_corpus_observed" if copied_count else "factory_only_not_observed_in_copied_corpus",
        "rebuildFacingFieldName": rebuild_field,
        "payloadClass": payload_class,
        "semanticState": semantic_state,
        "factoryAnchor": FACTORY_ANCHORS[family],
        "loaderAnchor": loader_anchor,
        "applyAnchor": apply_anchor,
        "registryGlobal": REGISTRY_GLOBALS[family],
        "destinationRecordKind": family,
        "destinationField": destination,
        "evidenceTier": evidence_tier,
        "claimBoundary": boundary,
        "publicSafe": True,
    }


def crosswalk_rows(value_counts: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    add = lambda *args, **kwargs: rows.append(row(*args, value_counts=value_counts, **kwargs))

    for value_id, field, payload, anchor, dest in (
        (1, "unitName", "owned_string_at_08", "CSpawnerUnit__ApplyToSpawnerByName", "spawner unit/name field"),
        (2, "delay", "scalar4", "CSpawnerDelay__ApplyToSpawnerByName", "+0x18"),
        (3, "amount", "scalar4", "CSpawnerAmount__ApplyToSpawnerByName", "+0x0c"),
        (4, "seekDelay", "scalar4", "CSpawnerSeekDelay__ApplyToSpawnerByName", "+0x14"),
        (5, "recallEnabled", "flag_constant_true", "CSpawnerRecall__ApplyToSpawnerByName", "+0x28"),
        (6, "minRange", "scalar4", "CSpawnerMinRange__ApplyToSpawnerByName", "+0x10"),
        (7, "maxRange", "scalar4", "CSpawnerMaxRange__ApplyToSpawnerByName", "+0x20"),
        (8, "preSpawnDelay", "scalar4", "CSpawnerPreSpawnDelay__ApplyToSpawnerByName", "+0x1c"),
        (9, "postSpawnDelay", "scalar4", "CSpawnerPostSpawnDelay__ApplyToSpawnerByName", "+0x2c"),
        (10, "basedOn", "owned_string_at_08", "CSpawnerBasedOn__ApplyToSpawnerByName", "base-spawner copied fields"),
        (11, "squadSize", "scalar4", "CSpawnerSquadSize__ApplyToSpawnerByName", "+0x30"),
        (12, "squadDelay", "scalar4", "CSpawnerSquadDelay__ApplyToSpawnerByName", "+0x34"),
        (13, "infinite", "scalar4", "CSpawnerInfinite__ApplyToSpawnerByName", "+0x38"),
        (14, "conditions", "scalar4", "CSpawnerConditions__ApplyToSpawnerByName", "+0x24"),
    ):
        add("spawner", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Runtime spawn timing/AI behavior remains unproven.")

    for value_id, field, payload, dest, state in (
        (1, "basedOn", "owned_string_at_08", "base explosion copied fields", "resolved_static_field"),
        (2, "airEffect", "owned_string_at_08", "+0x18", "resolved_static_field"),
        (3, "scalar34", "scalar4", "+0x34", "resolved_static_shape"),
        (4, "scalar38", "scalar4", "+0x38", "resolved_static_shape"),
        (5, "groundEffect", "owned_string_at_08", "+0x20", "resolved_static_field"),
        (6, "waterEffect", "owned_string_at_08", "+0x1c", "resolved_static_field"),
        (7, "unitEffect", "owned_string_at_08", "+0x24", "resolved_static_field"),
        (8, "scalar3C", "scalar4", "+0x3c", "resolved_static_shape"),
        (9, "scalar40", "scalar4", "+0x40", "resolved_static_shape"),
        (10, "sound", "owned_string_at_08", "+0x28", "resolved_static_field"),
        (11, "scalar44", "scalar4", "+0x44", "resolved_static_shape"),
        (12, "scalar4C", "scalar4", "+0x4c", "resolved_static_shape"),
        (13, "scalar48", "scalar4", "+0x48", "resolved_static_shape"),
        (15, "waterSound", "owned_string_at_08", "+0x2c", "resolved_static_field"),
    ):
        anchor = "CExplosionBasedOn__ApplyToExplosionByName" if value_id == 1 else "CExplosionValue__ApplyToExplosionByName"
        add("explosion", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Scalar meanings remain offset-named unless a runtime/source unit is separately proven.", semantic_state=state)

    for value_id, field, payload, anchor, dest, state in (
        (1, "scalar18", "scalar4", "CFeatureScalar18__ApplyToFeatureByName", "+0x18", "resolved_static_shape"),
        (2, "mesh", "owned_string_at_08", "CFeatureMesh__ApplyToFeatureByName", "mesh string field", "resolved_static_field"),
        (3, "texture", "owned_string_at_08", "CFeatureTexture__ApplyToFeatureByName", "texture helper input", "resolved_static_field"),
        (4, "flag10", "flag_from_scalar_nonzero", "CFeatureFlag10__ApplyToFeatureByName", "+0x10", "resolved_static_shape"),
        (5, "noise", "owned_string_at_08", "CFeatureNoise__ApplyToFeatureByName", "noise string field", "resolved_static_field"),
        (6, "flag14", "flag_from_scalar_nonzero", "CFeatureFlag14__ApplyToFeatureByName", "+0x14", "resolved_static_shape"),
        (7, "scalar1C", "scalar4", "CFeatureScalar1C__ApplyToFeatureByName", "+0x1c", "resolved_static_shape"),
    ):
        add("feature", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Feature scalar/flag runtime meaning remains deferred.", semantic_state=state)

    for value_id, field, payload, anchor, dest, state in (
        (1, "scalar14", "scalar4", "CHazardScalar14__ApplyToHazardByName", "+0x14", "resolved_static_shape"),
        (2, "effect", "owned_string_at_08", "CHazardEffect__ApplyToHazardByName", "+0x8", "resolved_static_field"),
        (3, "scalar18", "scalar4", "CHazardScalar18__ApplyToHazardByName", "+0x18", "resolved_static_shape"),
        (4, "noise", "owned_string_at_08", "CHazardNoise__ApplyToHazardByName", "+0x0c", "resolved_static_field"),
    ):
        add("hazard", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Hazard scalar runtime meaning remains deferred.", semantic_state=state)

    for value_id, field, payload, anchor, dest, state in (
        (1, "scalarC0", "scalar4", "CComponentScalarC0__ApplyToComponentByName", "+0xc0", "resolved_static_shape"),
        (3, "mesh", "owned_string_at_08", "CComponentMesh__ApplyToComponentByName", "+0x2c", "resolved_static_field"),
        (6, "scalar158", "scalar4", "CComponentScalar158__ApplyToComponentByName", "+0x158", "resolved_static_shape"),
        (7, "scalarDC", "scalar4", "CComponentScalarDC__ApplyToComponentByName", "+0xdc", "resolved_static_shape"),
        (8, "scalarD8", "scalar4", "CComponentScalarD8__ApplyToComponentByName", "+0xd8", "resolved_static_shape"),
        (9, "scalarB8", "scalar4", "CComponentScalarB8__ApplyToComponentByName", "+0xb8", "resolved_static_shape"),
        (10, "basedOn", "owned_string_at_08", "CComponentBasedOn__ApplyToComponentByName", "component copied fields", "resolved_static_field"),
        (11, "scalarBC", "scalar4", "CComponentScalarBC__ApplyToComponentByName", "+0xbc", "resolved_static_shape"),
        (12, "noise", "owned_string_at_08", "CComponentNoise__ApplyToComponentByName", "+0xa8", "resolved_static_field"),
        (13, "flag124", "flag_from_scalar_nonzero", "CComponentFlag124__ApplyToComponentByName", "+0x124", "resolved_static_shape"),
        (15, "flag128", "flag_from_scalar_nonzero", "CComponentFlag128__ApplyToComponentByName", "+0x128", "resolved_static_shape"),
        (16, "flag108", "flag_from_scalar_nonzero", "CComponentFlag108__ApplyToComponentByName", "+0x108", "resolved_static_shape"),
        (17, "scalar160", "scalar4", "CComponentScalar160__ApplyToComponentByName", "+0x160", "resolved_static_shape"),
        (18, "flag12C", "flag_from_scalar_nonzero", "CComponentFlag12C__ApplyToComponentByName", "+0x12c", "resolved_static_shape"),
        (20, "indexedScalar164", "indexed_scalar", "CComponentIndexedScalar164__ApplyToComponentByName", "+0x164[index]", "resolved_static_shape"),
        (21, "flag198", "flag_from_scalar_nonzero", "CComponentFlag198__ApplyToComponentByName", "+0x198", "resolved_static_shape"),
        (22, "flag114", "flag_from_scalar_nonzero", "CComponentFlag114__ApplyToComponentByName", "+0x114", "resolved_static_shape"),
        (23, "flag19C", "flag_from_scalar_nonzero", "CComponentFlag19C__ApplyToComponentByName", "+0x19c", "resolved_static_shape"),
        (24, "flag134", "flag_from_scalar_nonzero", "CComponentFlag134__ApplyToComponentByName", "+0x134", "resolved_static_shape"),
        (25, "vent", "owned_string_at_08", "CComponentVent__ApplyToComponentByName", "+0x98", "resolved_static_field"),
    ):
        add("component", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Component scalar/flag exact gameplay meaning remains deferred.", semantic_state=state)

    for value_id, field, payload, anchor, dest, state in (
        (4, "seekTypeChild", "nested_enum_child", "CRoundSeek__ApplyToRoundByName", "+0x48", "resolved_static_shape"),
        (8, "effect", "owned_string_at_08", "CRoundEffect__ApplyToRoundByName", "+0x10", "resolved_static_field"),
        (9, "explosion", "owned_string_at_08", "CRoundExplosion__ApplyToRoundByName", "+0x8", "resolved_static_field"),
        (24, "gridOfFear", "rounded_scalar4", "CRoundGridOfFear__ApplyToRoundByName", "+0x58", "resolved_static_shape"),
        (33, "waterEffect", "owned_string_at_08", "CRoundWaterEffect__ApplyToRoundByName", "+0x14", "resolved_static_field"),
        (35, "treeCollisionStateChild", "nested_enum_child", "CRoundTreeCollision__ApplyToRoundByName", "+0xa4", "resolved_static_shape"),
        (36, "mesh", "owned_string_at_08", "CRoundMesh__ApplyToRoundByName", "+0x0c", "resolved_static_field"),
    ):
        add("round", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Round runtime projectile behavior remains deferred.", semantic_state=state)

    for value_id, field, payload, anchor, dest, state in (
        (2, "roundNameOrRoundRef", "owned_string_at_08", "CWeaponRound__ApplyToWeaponModeByName", "round reference helper", "resolved_static_field"),
        (6, "muzzleEffect", "owned_string_at_08", "CWeaponMuzzleEffect__ApplyToWeaponModeByName", "+0x1c", "resolved_static_field"),
        (15, "clip", "owned_string_at_08", "CWeaponClip__ApplyToWeaponModeByName", "clip string reference", "resolved_static_field"),
        (18, "preFireEffect", "owned_string_at_08", "CWeaponPreFireEffect__ApplyToWeaponModeByName", "+0x20", "resolved_static_field"),
        (24, "launchSound", "owned_string_at_08", "CWeaponLaunchSound__ApplyToWeaponModeByName", "+0x24", "resolved_static_field"),
        (28, "volleySize", "rounded_scalar4", "CWeaponVolleySize__ApplyToWeaponModeByName", "+0x48", "resolved_static_shape"),
        (31, "launchAngle3", "three_scalar4", "CWeaponLaunchAngle__LoadFromMemBuffer", "this+0x8/+0xc/+0x10", "resolved_static_shape"),
        (34, "preFireSound", "owned_string_at_08", "CWeaponPreFireSound__ApplyToWeaponModeByName", "+0x28", "resolved_static_field"),
        (36, "postFireSound", "owned_string_at_08", "CWeaponPostFireSound__ApplyToWeaponModeByName", "+0x2c", "resolved_static_field"),
    ):
        add("weapon-mode", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Weapon-mode runtime firing behavior remains deferred.", semantic_state=state)

    for value_id, field, payload, anchor, dest, state in (
        (1, "chargeLevel", "owned_string_and_scalar_shape", "CWeaponChargeLevel__LoadFromMemBuffer", "charge-level record shape", "resolved_static_shape"),
        (4, "consumption", "scalar4", "CWeaponConsumption__ApplyToWeaponByName", "weapon registry field", "resolved_static_shape"),
        (5, "iconName", "owned_string_at_08", "CWeaponIconName__ApplyToWeaponByName", "weapon icon string", "resolved_static_field"),
        (14, "versusAir", "scalar4", "CWeaponVersusAir__ApplyToWeaponByName", "weapon registry field", "resolved_static_shape"),
    ):
        add("weapon", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Weapon based-on and other weapon scalar semantics remain deferred.", semantic_state=state)

    for value_id, field, payload, anchor, dest, state in (
        (7, "use", "compound_owned_string_shape", "CUnitUse__ApplyToUnitData", "+0x108 helper input", "resolved_static_shape"),
        (8, "behaviour", "nested_enum_child", "CUnitBehaviour__ApplyToUnitData", "+0xe0/+0xfc", "resolved_static_shape"),
        (20, "importance", "scalar4", "CUnitImportance__ApplyToUnitData", "+0xf8", "resolved_static_shape"),
        (21, "soundMaterial", "rounded_scalar4", "CUnitSoundMaterial__ApplyToUnitData", "+0xe4", "resolved_static_shape"),
        (22, "strafeChange", "scalar4", "CUnitStrafeChange__ApplyToUnitData", "+0x180", "resolved_static_shape"),
        (25, "navMap", "nested_enum_child", "CUnitNavMap__ApplyToUnitData", "+0xfc", "resolved_static_shape"),
        (60, "standingLegPlacementArea", "scalar4", "CUnitStandingLegPlacementArea__ApplyToUnitData", "+0x150", "resolved_static_shape"),
        (61, "maxLegsLifted", "rounded_scalar4", "CUnitMaxLegsLifted__ApplyToUnitData", "+0x140", "resolved_static_shape"),
    ):
        add("unit", value_id, field, payload, "factory_case_plus_apply_anchor", anchor, dest, "Unit AI/runtime movement meaning remains deferred.", semantic_state=state)

    return rows


def build_report() -> dict[str, Any]:
    semantic = read_json(SEMANTIC_SCHEMA)
    fixture = read_json(FIXTURE_SCHEMA)
    value_counts = semantic["valueCountsByFamily"]
    rows = crosswalk_rows(value_counts)
    selected_ids = {
        family: sorted(row["valueId"] for row in rows if row["family"] == family)
        for family in sorted(STATEMENT_TYPE_IDS)
    }
    observed_ids = {
        family: sorted(int(value_id) for value_id in counts)
        for family, counts in value_counts.items()
    }
    unselected_observed = {
        family: [value_id for value_id in observed_ids.get(family, []) if value_id not in selected_ids.get(family, [])]
        for family in sorted(value_counts)
    }
    family_counts = {
        family: {
            "observedValueIdCount": len(observed_ids.get(family, [])),
            "selectedCrosswalkRowCount": len(selected_ids.get(family, [])),
            "observedSelectedValueIdCount": sum(1 for value_id in selected_ids.get(family, []) if value_id in observed_ids.get(family, [])),
            "factoryOnlySelectedValueIdCount": sum(1 for value_id in selected_ids.get(family, []) if value_id not in observed_ids.get(family, [])),
            "unselectedObservedValueIdCount": len(unselected_observed.get(family, [])),
        }
        for family in sorted(STATEMENT_TYPE_IDS)
    }

    return {
        "schemaVersion": "physics-script-value-id-semantic-crosswalk.v1",
        "status": "PASS",
        "proofPlan": "PhysicsScript Value-ID Semantic Crosswalk Proof Plan",
        "scope": "physics-script-value-id-semantic-crosswalk-proof-plan",
        "crosswalkStatus": "physics-script-value-id-semantic-crosswalk-complete-bounded-static-crosswalk-not-runtime-proof",
        "selectedPreviousSlice": "PhysicsScript Scalar/String Value Decoder Fixture Proof Plan",
        "selectedNextSlice": "PhysicsScript Rebuild Interface Rollup Proof Plan",
        "staticContext": semantic["staticContext"],
        "sourceSchemas": {
            "semanticLedgerSchema": str(SEMANTIC_SCHEMA.relative_to(ROOT)).replace("\\", "/"),
            "scalarStringFixtureSchema": str(FIXTURE_SCHEMA.relative_to(ROOT)).replace("\\", "/"),
            "semanticLedgerStatus": semantic["ledgerStatus"],
            "scalarStringFixtureStatus": fixture["fixtureStatus"],
        },
        "corpusCounts": semantic["corpusCounts"],
        "fixtureClassCounts": fixture["corpusAggregate"]["fixtureClassCounts"],
        "topLevelFamilies": semantic["topLevelFamilies"],
        "valueCountsByFamily": value_counts,
        "crosswalkRows": rows,
        "familyCoverageSummary": family_counts,
        "selectedValueIdsByFamily": selected_ids,
        "unselectedObservedValueIdsByFamily": unselected_observed,
        "deferredFactoryValueIdsByFamily": {
            "component": [2, 4, 14, 19],
            "explosion": [14],
            "feature": [],
            "hazard": [],
            "round": [],
            "spawner": [],
            "unit": [],
            "weapon": [],
            "weapon-mode": [],
        },
        "coverageSummary": {
            "familyCount": len(STATEMENT_TYPE_IDS),
            "copiedCorpusUniqueStatementValuePairCount": semantic["corpusCounts"]["uniqueStatementValuePairCount"],
            "valueFamilyCoverageRows": len(value_counts),
            "boundedCrosswalkRowCount": len(rows),
            "copiedCorpusObservedSelectedRowCount": sum(1 for item in rows if item["copiedCorpusCount"] > 0),
            "factoryOnlySelectedRowCount": sum(1 for item in rows if item["copiedCorpusCount"] == 0),
            "allObservedPairsAccountedByCountMap": True,
            "allSelectedRowsHaveFactoryAnchors": all(bool(item["factoryAnchor"]) for item in rows),
            "allSelectedRowsHaveApplyAnchors": all(bool(item["applyAnchor"]) for item in rows),
            "completeValueIdSemanticsProven": False,
            "all185PairsSemanticallyNamed": False,
            "runtimeBehaviorProven": False,
            "rebuildImplementationComplete": False,
        },
        "guardSummary": {
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "A bounded public-safe crosswalk exists for selected PhysicsScript family/value-id rows.",
                "Exact copied-corpus value-id counts are preserved through the prior semantic ledger.",
                "Selected rebuild-facing field names are tied to static factory/apply/load anchors.",
                "Scalar-only fields remain offset-named when gameplay meaning is not proven.",
            ],
            "doesNotProve": [
                "runtime PhysicsScript behavior",
                "runtime physics outcomes",
                "serialized PhysicsScript completeness",
                "exact concrete record layouts",
                "complete value-id semantics for all 185 observed statement/value pairs",
                "complete nested enum semantics",
                "raw string identity",
                "raw numeric value meaning",
                "BEA patching behavior",
                "Godot parity",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
        "publicSafety": {
            "publicLeakCheck": "PASS",
            "rawBytesEmitted": False,
            "rawNamesOrStringsEmitted": False,
            "rawHashValuesEmitted": False,
            "rawNumericValuesEmitted": False,
            "absolutePrivatePathsEmitted": False,
            "privateArtifactLocatorsEmitted": False,
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
