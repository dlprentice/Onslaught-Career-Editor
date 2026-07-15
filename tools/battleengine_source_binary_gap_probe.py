#!/usr/bin/env python3
"""Public-safe BattleEngine source-to-binary gap probe.

This read-only probe compares the BattleEngine source-anchor families tracked by
``battleengine_logic_coverage_probe.py`` with the current binary function
mapping docs. It deliberately reports gaps instead of pretending source anchors
have retail-binary identity before Ghidra/read-back work proves that identity.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS_ROOT = ROOT / "reverse-engineering" / "binary-analysis" / "functions"
LOGIC_PROBE = ROOT / "tools" / "battleengine_logic_coverage_probe.py"
DEFAULT_OUT = ROOT / "local-lab" / "battleengine-source-binary-gap" / "current" / "battleengine-source-binary-gap.json"


@dataclass(frozen=True)
class BinaryFamilyExpectation:
    source_file: str
    minimum_named_functions: int


@dataclass(frozen=True)
class PartialCandidateExpectation:
    key: str
    evidence_file: str
    tokens: tuple[str, ...]
    summary: str
    status: str = "PARTIAL_RETAIL_CANDIDATE_PENDING_EXACT_IDENTITY"


EXPECTED_BINARY_FAMILIES: tuple[BinaryFamilyExpectation, ...] = (
    BinaryFamilyExpectation("BattleEngine.cpp", 3),
    BinaryFamilyExpectation("BattleEngineDataManager.cpp", 3),
    BinaryFamilyExpectation("Player.cpp", 3),
)

SOURCE_ONLY_ANCHOR_KEYS: tuple[str, ...] = (
    "damage_stat_fixed_point",
    "damage_shield_efficiency",
    "damage_walker_energy_tracks_shields",
    "damage_invulnerability_restore",
    "transform_reject_special_moves",
    "transform_morph_method_anchor",
    "transform_jet_to_walker_event",
    "transform_walker_to_jet_energy_gate",
    "jet_energy_cost",
    "jet_stall_forces_morph_to_walker",
    "target_lock_modes_and_stealth_range",
    "augmented_weapon_charge_decay_and_reset",
    "weapon_fire_breaks_stealth",
    "config_defaults",
    "player_god_mode_toggles",
)

PARTIAL_RETAIL_CANDIDATE_ANCHORS: tuple[PartialCandidateExpectation, ...] = (
    PartialCandidateExpectation(
        "damage_stat_fixed_point",
        "release/readiness/battleengine_damage_source_readback_bridge_2026-05-06.md",
        (
            "Source core damage anchors",
            "Fixed-point damage stats",
            "CUnit__ApplyDamage",
            "Exact `CBattleEngine::Damage` to `CUnit__ApplyDamage` control-flow identity",
        ),
        "Damage fixed-point stat accounting has partial source/read-back bridge evidence through CUnit__ApplyDamage, but exact CBattleEngine::Damage control-flow identity remains unresolved.",
    ),
    PartialCandidateExpectation(
        "damage_shield_efficiency",
        "release/readiness/battleengine_damage_source_readback_bridge_2026-05-06.md",
        (
            "Source core damage anchors",
            "shield-efficiency absorption",
            "CUnit__ApplyDamage",
            "Exact `CBattleEngine::Damage` to `CUnit__ApplyDamage` control-flow identity",
        ),
        "Damage shield-efficiency absorption has partial source/read-back bridge evidence through CUnit__ApplyDamage, but exact CBattleEngine::Damage control-flow identity remains unresolved.",
    ),
    PartialCandidateExpectation(
        "damage_walker_energy_tracks_shields",
        "release/readiness/battleengine_damage_source_readback_bridge_2026-05-06.md",
        (
            "Source restore/energy anchors",
            "Walker energy/shield mirroring",
            "CUnit__ApplyDamage",
            "Exact `CBattleEngine::Damage` to `CUnit__ApplyDamage` control-flow identity",
        ),
        "Walker energy/shield mirroring during damage has partial source/read-back bridge evidence, but exact CBattleEngine::Damage control-flow identity remains unresolved.",
    ),
    PartialCandidateExpectation(
        "damage_invulnerability_restore",
        "release/readiness/battleengine_damage_source_readback_bridge_2026-05-06.md",
        (
            "Source restore/energy anchors",
            "vulnerability-restore tokens",
            "CUnit__ApplyDamage",
            "Exact `CBattleEngine::Damage` to `CUnit__ApplyDamage` control-flow identity",
        ),
        "Damage invulnerability restore behavior has partial source/read-back bridge evidence, but exact CBattleEngine::Damage control-flow identity remains unresolved.",
    ),
    PartialCandidateExpectation(
        "transform_reject_special_moves",
        "release/readiness/ghidra_battleengine_walker_dash_gate_review_wave984_2026-05-31.md",
        (
            "`transform_reject_special_moves`",
            "`CBattleEngine__Morph`",
            "`CBattleEngineJetPart__IsStateMachineActive`",
            "`CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove`",
            "runtime transform rejection",
        ),
        "Transform special-move rejection has current static retail evidence through CBattleEngine__Morph and the WalkerPart special-move predicate, but runtime behavior and exact layouts remain unresolved.",
    ),
    PartialCandidateExpectation(
        "transform_morph_method_anchor",
        "release/readiness/ghidra_battleengine_walker_dash_gate_review_wave984_2026-05-31.md",
        (
            "`CBattleEngine__Morph`",
            "`s_flytowalk_006234bc`",
            "`s_walktofly_006234b0`",
            "runtime transform rejection",
        ),
        "The source Morph branch has current static retail bridge evidence through CBattleEngine__Morph, but runtime transform behavior and exact layouts remain unresolved.",
    ),
    PartialCandidateExpectation(
        "transform_jet_to_walker_event",
        "release/readiness/ghidra_battleengine_walker_dash_gate_review_wave984_2026-05-31.md",
        (
            "`0x1771`",
            "`CBattleEngine__Morph`",
            "`s_flytowalk_006234bc`",
            "runtime transform rejection",
        ),
        "Jet-to-walker transform event behavior has current static retail bridge evidence through CBattleEngine__Morph, but runtime transform behavior remains unresolved.",
    ),
    PartialCandidateExpectation(
        "transform_walker_to_jet_energy_gate",
        "release/readiness/ghidra_battleengine_walker_dash_gate_review_wave984_2026-05-31.md",
        (
            "`6000`",
            "`CBattleEngine__Morph`",
            "`s_walktofly_006234b0`",
            "runtime transform rejection",
        ),
        "Walker-to-jet transform/event and energy-gate behavior has current static retail bridge evidence through CBattleEngine__Morph, but runtime transform behavior remains unresolved.",
    ),
    PartialCandidateExpectation(
        "jet_energy_cost",
        "release/readiness/battleengine_jet_stall_candidate_2026-05-07.md",
        (
            "`jet_energy_cost`",
            "energy-like subtract from offset `0x280`",
            "`_DAT_005d8c2c`",
            "exact source-to-retail identity",
        ),
        "Jet energy spend has partial retail candidate evidence through CMonitor__Process energy-offset subtraction and .rdata constant read-back, but exact BattleEngineJetPart method identity remains unresolved.",
    ),
    PartialCandidateExpectation(
        "jet_stall_forces_morph_to_walker",
        "release/readiness/battleengine_jet_stall_candidate_2026-05-07.md",
        (
            "`jet_stall_forces_morph_to_walker`",
            "velocity-threshold path",
            "`0x310`",
            "`0x110`",
            "exact source-to-retail identity",
        ),
        "Jet low-speed stall fallback has partial retail candidate evidence through CMonitor__Process velocity-threshold/counter/vfunc tokens, but exact BattleEngineJetPart method identity remains unresolved.",
    ),
    PartialCandidateExpectation(
        "walker_recharge",
        "release/readiness/battleengine_walker_recharge_candidate_2026-05-07.md",
        (
            "`walker_recharge`",
            "CMonitor__ProcessTrackingAndSurfaceAlignment",
            "recent-ground gate",
            "ground-energy-increase",
            "shield/energy mirror",
            "Exact source-to-retail identity for `CBattleEngineWalkerPart::Move()`",
        ),
        "Walker recharge has partial retail candidate evidence through CMonitor__ProcessTrackingAndSurfaceAlignment recent-ground/config-rate/cap/mirror tokens, but exact BattleEngineWalkerPart method identity remains unresolved.",
    ),
    PartialCandidateExpectation(
        "cloak_energy_gate_burn_and_render",
        "release/readiness/battleengine_cloak_stealth_candidate_2026-05-07.md",
        (
            "CGeneralVolume__Update4ACLatchFromHeightAndA0",
            "CMonitor__Process",
            "cloak toggle/latch helper",
            "active energy burn",
            "forced-decloak clearing",
            "Render context tokens",
            "Weapon-fired stealth reset identity",
        ),
        "Cloak behavior has partial retail candidate evidence through latch/config checks, active energy burn, forced-decloak clearing, interpolation, and target-scaling tokens, but exact source method identity, RF_CLOAKED identity, and runtime behavior remain unresolved.",
    ),
    PartialCandidateExpectation(
        "config_defaults",
        "release/readiness/battleengine_config_defaults_binary_doc_2026-05-06.md",
        (
            "BattleEngine config defaults binary-doc probe",
            "energy default",
            "minimum transform energy default",
            "shield-efficiency default",
            "Exact Steam retail function body identity for each source default field",
        ),
        "Configuration defaults have partial value-level source-to-binary-doc evidence, but exact retail function body identity remains unresolved.",
    ),
    PartialCandidateExpectation(
        "player_god_mode_toggles",
        "release/readiness/battleengine_god_mode_source_bridge_2026-05-07.md",
        (
            "`player_god_mode_toggles`",
            "partial mechanism evidence",
            "exact source-to-retail identity for `CPlayer::SetIsGod`",
            "environmental hazard behavior",
        ),
        "Player god-mode toggles have partial source/binary/runtime-note mechanism evidence, but exact Steam SetIsGod identity and full runtime boundary remain unresolved.",
    ),
    PartialCandidateExpectation(
        "target_lock_modes_and_stealth_range",
        "reverse-engineering/game-mechanics/battleengine-target-acquisition-static-contract-v1.md",
        (
            "accepted static contract; not runtime proof",
            "`0x00406560` | `CBattleEngine__HandleLocks`",
            "`CBattleEngine::GetClosestLockableUnit`",
            "`CBattleEngine::StartLock`",
            "`runtime target choice`",
            "`the retail semantic meaning of the source stealth expression`",
        ),
        "The 0x00406560 CBattleEngine__HandleLocks retail-static root identity is accepted; exact source identities for the two dependent helpers, retail stealth-expression semantics, and runtime target choice remain unresolved.",
        "RETAIL_STATIC_ROOT_IDENTITY_ACCEPTED_DEPENDENT_HYPOTHESES_PENDING",
    ),
    PartialCandidateExpectation(
        "augmented_weapon_charge_decay_and_reset",
        "release/readiness/battleengine_augmented_weapon_candidate_readback_2026-05-07.md",
        (
            "0x0040de40",
            "0x004081c0",
            "activation/depletion",
            "does not prove whether retail code inlined or reorganized",
        ),
        "Augmented-weapon activation/depletion has partial retail candidate evidence, but exact source method boundaries remain unresolved.",
    ),
)


def import_logic_probe():
    spec = importlib.util.spec_from_file_location("battleengine_logic_coverage_probe", LOGIC_PROBE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {LOGIC_PROBE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def parse_function_table(index_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not index_path.is_file():
        return rows
    for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| 0x"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        rows.append({"address": cells[0], "name": cells[1]})
    return rows


def token_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def summarize_binary_family(expectation: BinaryFamilyExpectation) -> dict[str, object]:
    index_path = FUNCTIONS_ROOT / expectation.source_file / "_index.md"
    rows = parse_function_table(index_path)
    named = [
        row
        for row in rows
        if row["name"]
        and not row["name"].startswith("FUN_")
        and not row["name"].startswith("__Unk_")
    ]
    status = "PASS" if len(named) >= expectation.minimum_named_functions else "GAP"
    return {
        "sourceFile": expectation.source_file,
        "binaryDoc": relative(index_path),
        "status": status,
        "namedFunctions": len(named),
        "minimumNamedFunctions": expectation.minimum_named_functions,
        "functions": named,
    }


def summarize_partial_candidate(expectation: PartialCandidateExpectation, tracked_anchor_keys: list[str]) -> dict[str, object]:
    path = ROOT / expectation.evidence_file
    hits = token_hits(path, expectation.tokens)
    missing_tokens = [token for token, lines in hits.items() if not lines]
    failures: list[str] = []
    if expectation.key not in tracked_anchor_keys:
        failures.append("anchor key missing from source coverage report")
    if not path.is_file():
        failures.append(f"missing evidence file: {expectation.evidence_file}")
    failures.extend(f"missing evidence token: {token}" for token in missing_tokens)
    return {
        "key": expectation.key,
        "evidenceFile": expectation.evidence_file,
        "status": expectation.status if not failures else "GAP",
        "summary": expectation.summary,
        "tokenLineHits": hits,
        "failures": failures,
    }


def build_report() -> dict[str, object]:
    logic_probe = import_logic_probe()
    logic_report = logic_probe.build_report()
    binary_families = [summarize_binary_family(item) for item in EXPECTED_BINARY_FAMILIES]
    binary_failures = [item for item in binary_families if item["status"] != "PASS"]
    source_failures = [item for item in logic_report["sourceResults"] if item["status"] != "PASS"]
    tracked_anchor_keys = [item["key"] for item in logic_report["sourceResults"]]
    unexpected_missing = [key for key in SOURCE_ONLY_ANCHOR_KEYS if key not in tracked_anchor_keys]
    partial_retail_candidates = [
        summarize_partial_candidate(item, tracked_anchor_keys)
        for item in PARTIAL_RETAIL_CANDIDATE_ANCHORS
    ]
    partial_failures = [item for item in partial_retail_candidates if item["status"] == "GAP"]
    partial_keys = {item.key for item in PARTIAL_RETAIL_CANDIDATE_ANCHORS}
    source_only_anchors = [
        {
            "key": item["key"],
            "sourceFile": item["file"],
            "status": "SOURCE_ONLY_PENDING_BINARY_IDENTITY",
            "reason": "The source anchor is machine-checked, but this probe has no matching retail-binary function identity/read-back proof for that specific anchor.",
        }
        for item in logic_report["sourceResults"]
        if item["key"] in SOURCE_ONLY_ANCHOR_KEYS and item["key"] not in partial_keys
    ]
    status = "pass" if not binary_failures and not source_failures and not unexpected_missing and not partial_failures else "blocked"
    return {
        "schema": "battleengine-source-binary-gap.v1",
        "status": status,
        "binaryFamiliesChecked": len(binary_families),
        "binaryFamiliesPassed": sum(1 for item in binary_families if item["status"] == "PASS"),
        "sourceAnchorsChecked": logic_report["sourceAnchorsChecked"],
        "sourceAnchorsPassed": logic_report["sourceAnchorsPassed"],
        "binaryFamilies": binary_families,
        "sourceOnlyAnchors": source_only_anchors,
        "partialRetailCandidates": partial_retail_candidates,
        "unexpectedMissingAnchorKeys": unexpected_missing,
        "whatIsMapped": "Current binary docs include named BattleEngine.cpp, BattleEngineDataManager.cpp, and Player.cpp function families.",
        "whatRemainsSourceOnly": "Selected weapon-fired stealth remains source-only until retail-binary/Ghidra read-back identifies its exact function body. Selected damage anchors, transform special-move lockout, Morph event/energy-gate anchors, jet energy/stall anchors, walker recharge, cloak behavior, player god-mode toggles, configuration defaults, and augmented-weapon activation/depletion have partial retail candidate evidence, but exact source method/control-flow/function-body boundaries remain unproven. Target locking now has accepted 0x00406560 CBattleEngine__HandleLocks retail-static root identity while dependent helper source identities, retail stealth-expression semantics, and runtime target choice remain hypotheses or runtime-required.",
        "privacy": "Report stores repo-relative doc/source filenames, function names, addresses already present in public-safe docs, and gap labels only; no binaries, private paths, source excerpts, runtime captures, or Ghidra mutation logs.",
        "notProven": [
            "Steam retail binary identity for every remaining source anchor",
            "Exact source-method boundaries for partial retail candidates",
            "No new Ghidra rename-map mutation or live read-back is performed by this probe",
            "Runtime gameplay-state interpretation",
            "Continuous frame streaming",
            "Rebuildable open-source gameplay implementation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BattleEngine source-to-binary coverage gaps.")
    parser.add_argument("--check", action="store_true", help="run the gap probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "local-lab").resolve())
    except ValueError:
        print(f"Refusing to write report outside local-lab/: {out}")
        return 1
    report = build_report()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine source-to-binary gap probe")
        print(f"Status: {report['status']}")
        print(f"Binary families: {report['binaryFamiliesPassed']}/{report['binaryFamiliesChecked']}")
        print(f"Source anchors: {report['sourceAnchorsPassed']}/{report['sourceAnchorsChecked']}")
        for item in report["binaryFamilies"]:
            print(f"- {item['status']}: {item['sourceFile']}: named functions {item['namedFunctions']}")
        print(f"Source-only anchors pending binary identity: {len(report['sourceOnlyAnchors'])}")
        print(f"Composite partial-retail rows: {len(report['partialRetailCandidates'])}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
