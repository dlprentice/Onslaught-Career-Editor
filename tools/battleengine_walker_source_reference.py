#!/usr/bin/env python3
"""Deterministic, source-led BattleEngine walker reference model.

This is a symbolic control-flow fixture generator, not a retail behavior
implementation.  Numeric retail comparisons and constants remain unresolved
until accepted copied-runtime measurements exist.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping

import onslaught_source_steam_crosswalk as crosswalk_validator
import battleengine_walker_trajectory_schema as trajectory_schema


SCHEMA = "onslaught.battleengine-walker-source-reference.v1"
SOURCE_REVISION = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"
SOURCE_CROSSWALK = Path("reverse-engineering/source-code/onslaught-source-steam-crosswalk.v1.json")
SOURCE_FILE = Path("references/Onslaught/BattleEngineWalkerPart.cpp")
PLAYER_SOURCE_FILE = Path("references/Onslaught/Player.cpp")
BATTLEENGINE_SOURCE_FILE = Path("references/Onslaught/BattleEngine.cpp")
FUTURE_CORE_CONSUMER = "deterministic-core-walker-forward"

def _canonical_future_core_targets() -> dict[str, Any]:
    return {
        "contractFile": "rebuild/OnslaughtRebuild.Core/WalkerForwardResponseContract.cs",
    "contractType": "WalkerForwardResponseContract",
    "integrationFile": "rebuild/OnslaughtRebuild.Core/Simulation.cs",
    "integrationType": "Simulation",
    "contractTests": "rebuild/OnslaughtRebuild.Core.Tests/WalkerForwardResponseContractTests.cs",
    "integrationTests": "rebuild/OnslaughtRebuild.Core.Tests/SimulationTests.cs",
    "contractTestCases": [
        "AcceptsTwoAttemptEnvelope",
        "RejectsMissingOrOutOfRangeEnvelope",
    ],
    "integrationTestCases": [
        "WalkerForward_UsesAcceptedResponseContractDeterministically",
        "WalkerForward_ReplayHashIsStable",
    ],
    "constantsFile": "rebuild/OnslaughtRebuild.Core/SimulationConstants.cs",
    "constantsType": "SimulationConstants",
    "candidateConstantsMember": "WalkerSpeedPerTick",
    "translationContract": {
        "status": "blocked-until-coordinate-scale-tick-and-quantization-policy-accepted",
        "measurementUnit": "retail-world-coordinate-units-per-second",
        "coreUnit": "integer-core-units-per-tick",
        "coreTickRateMember": "SimulationConstants.TicksPerSecond",
        "requiredFields": [
            "coreUnitsPerRetailWorldCoordinateUnit",
            "speedEnvelopeSelectionRule",
            "responseCurveToTickRule",
            "releaseLatencyToTickRule",
            "roundingMode",
            "maximumQuantizationErrorCoreUnits",
            "overflowBounds",
        ],
        "satisfied": False,
    },
    "replayTests": "rebuild/OnslaughtRebuild.Core.Tests/ReplayTests.cs",
    "replayTestCase": "FirstFlightReplay_IsDeterministicAndMatchesGoldenHash",
    "scenarioFile": "rebuild/scenarios/first-flight.v1.json",
    "headlessFile": "rebuild/OnslaughtRebuild.Headless/HeadlessApplication.cs",
    "headlessType": "HeadlessApplication",
    "headlessTests": "rebuild/OnslaughtRebuild.Core.Tests/HeadlessApplicationTests.cs",
    "headlessTestCase": "TapeGolden_IsCheckedAndVerified",
        "targetSetStatus": "open-blocked-translation-contract-incomplete",
    }


SCALAR_MEASURABLE_FIELDS = (
    "steadySpeed",
    "baselineB95Speed",
    "baselineEndpointDisplacement",
    "responseThreshold",
    "responseLatencyMs",
    "releaseLatencyMs",
    "steadySlope",
    "normalizedResponse",
    "velocityHoldToBaselineRatio",
)

FUTURE_PROBE_FIELDS = (
    "actorBasis",
    "actorRelativeDirection",
    "groundedState",
    "terrainState",
    "dashState",
    "walkCycle",
    "energy",
    "shield",
)

SOURCE_SHAPED_FIXTURE_INPUTS = (
    "battleEngineState",
    "normalizedInput",
    "groundedAtForward",
    "dashCount",
    "slowMovement",
    "forward.crossesDashStart",
    "forward.crossesDashEnd",
    "forward.reverseStartWithinWindow",
    "move.currentWeaponPresent",
    "move.playerPresent",
    "move.recentGround",
    "move.energyLimited",
    "move.cloaked",
    "move.shieldsRechargingBeforeMove",
    "move.rechargeExceedsCapacity",
    "move.goingIntoWaterChecks",
    "move.shouldSlide",
    "move.onGround",
    "move.horizontalSpeedExceedsMax",
    "move.dashBelowFrictionThreshold",
    "move.walking",
    "walkCycle.present",
    "walkCycle.localXMagnitudeGreater",
    "walkCycle.exceedsPositivePi",
    "walkCycle.belowNegativePiAfterUpperCheck",
)

REQUIRED_ROWS = {
    "player_forward_route": ("BATTLE_ENGINE_STATE_WALKER", "BUTTON_MECH_FORWARD", "GetWalkerPart()->Forward(val)"),
    "walker_forward": ("IsOnGround", "mDoingDashCount", "mMainPart->AddVelocity(move)"),
    "walker_move": ("mGroundEnergyIncrease", "mWalkFriction", "mMaxWalkVelocity", "UpdateWalkCycle"),
    "walker_walk_cycle": ("ori.TransposeInPlace", "rel_vel.X*2.5f", "rel_vel.Y*3.0f", "PI_M2"),
}

SOURCE_ORDER_CONTRACTS = {
    SOURCE_FILE: (
        "if (GoingIntoWater())",
        "else if (ShouldSlide())",
        "if (!GoingIntoWater() )",
        "mMainPart->IsOnGround() || mDoingDashCount != 0",
        "if (m>mv && mDoingDashCount < mDashFriction)",
    ),
}

SOURCE_TOKEN_CONTRACTS = {
    PLAYER_SOURCE_FILE: REQUIRED_ROWS["player_forward_route"],
    SOURCE_FILE: (
        tuple(token for row in ("walker_forward", "walker_move", "walker_walk_cycle") for token in REQUIRED_ROWS[row])
        + SOURCE_ORDER_CONTRACTS[SOURCE_FILE]
    ),
    BATTLEENGINE_SOURCE_FILE: ("void CBattleEngine::Move", "mWalkerPart->Move();"),
}

STEAM_ROW_CONTRACTS = {
    "walker_forward": ("accepted-bounded-static", "0x00412d80", "CBattleEngineWalkerPart__Forward"),
    "walker_move": ("accepted-bounded-static", "0x00413760", "CBattleEngineWalkerPart__Move"),
    "walker_walk_cycle": ("accepted-bounded-static", "0x00412ad0", "CBattleEngineWalkerPart__UpdateWalkCycle"),
}

STEAM_EVIDENCE_TOKEN_CONTRACTS = {
    Path("reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Move.md"): (
        "0x004081c0",
        "CBattleEngine__Move",
        "Copied-runtime behavior proof: pending",
    ),
    Path("reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md"): (
        "0x00412ad0 CBattleEngineWalkerPart__UpdateWalkCycle",
        "larger-magnitude X/Y component",
        "runtime pending",
    ),
}

UNRESOLVED_CONSTANTS = (
    "forwardAccelerationFromGroundVelocity",
    "dashStartThreshold",
    "dashEndThreshold",
    "dashTimeWindow",
    "dashVelocityMultiplier",
    "dashLength",
    "slowMovementFactor",
    "recentGroundWindow",
    "groundEnergyIncrease",
    "shieldRechargeDivisor",
    "energyMaximum",
    "walkFriction",
    "maximumWalkVelocity",
    "dashFrictionThreshold",
    "walkCycleLocalXMultiplier",
    "walkCycleLocalYMultiplier",
    "walkCyclePiBoundary",
    "walkCycleTwoPiSpan",
)

BRANCH_IDS = frozenset(
    {
        "forward.airborne_return",
        "forward.dash_active_return",
        "forward.record_hard_forward",
        "forward.trigger_dash",
        "forward.no_dash",
        "forward.slow_scale",
        "forward.normal_scale",
        "move.weapon_missing",
        "move.weapon_present",
        "move.player_stat",
        "move.no_player_stat",
        "move.recharge",
        "move.no_recharge",
        "move.recharge_halved",
        "move.recharge_full",
        "move.energy_capped",
        "move.energy_not_capped",
        "move.water",
        "move.slide",
        "move.clear_slide",
        "move.friction",
        "move.no_friction",
        "move.speed_exceeds_max",
        "move.speed_within_max",
        "move.dash_clamp_gate_open",
        "move.dash_clamp_gate_closed",
        "move.speed_clamp",
        "move.no_speed_clamp",
        "move.dash_decrement",
        "move.no_dash_decrement",
        "move.walk_cycle",
        "move.no_walk_cycle",
        "walk.x_axis",
        "walk.y_axis",
        "walk.upper_wrap",
        "walk.no_upper_wrap",
        "walk.lower_wrap",
        "walk.no_lower_wrap",
    }
)


class ModelError(ValueError):
    """Raised when evidence or a branch fixture cannot be accepted."""


@dataclass(frozen=True)
class ForwardBranches:
    crosses_dash_start: bool = False
    crosses_dash_end: bool = False
    reverse_start_within_window: bool = False


@dataclass(frozen=True)
class MoveBranches:
    current_weapon_present: bool
    player_present: bool
    recent_ground: bool
    energy_limited: bool
    cloaked: bool
    shields_recharging_before_move: bool
    recharge_exceeds_capacity: bool
    going_into_water_checks: tuple[bool, bool]
    should_slide: bool
    on_ground: bool
    horizontal_speed_exceeds_max: bool
    dash_below_friction_threshold: bool | None
    walking: bool


@dataclass(frozen=True)
class WalkCycleBranches:
    local_x_magnitude_greater: bool
    exceeds_positive_pi: bool
    below_negative_pi_after_upper_check: bool


@dataclass(frozen=True)
class WalkerFixture:
    fixture_id: str
    normalized_input: tuple[float, float]
    grounded_at_forward: bool
    dash_count: int
    slow_movement: bool
    forward: ForwardBranches
    move: MoveBranches
    walk_cycle: WalkCycleBranches | None
    battleengine_state: str = "walker"


@dataclass
class SymbolicState:
    dash_count: str
    last_move_y: str = "initialLastMoveY"
    velocity: str = "initialVelocity"
    energy: str = "initialEnergy"
    shields: str = "initialShields"
    flags: str = "initialFlags"
    walk_cycle: str = "initialWalkCycle"
    old_walk_cycle: str = "initialOldWalkCycle"
    current_weapon_slot: str = "initialCurrentWeaponSlot"
    engine_state: str = "initialEngineState"
    shields_recharging: bool = False


def evidence_manifest() -> dict[str, list[dict[str, Any]]]:
    """Return the immutable evidence split accepted by this model."""
    return {
        "steamStatic": [
            {
                "status": "accepted-bounded-static",
                "address": "0x004081c0",
                "symbol": "CBattleEngine__Move",
                "claim": "walker-part dispatch exists in the non-jet source-compatible movement path",
            },
            {
                "status": "accepted-bounded-static",
                "address": "0x00412ad0",
                "symbol": "CBattleEngineWalkerPart__UpdateWalkCycle",
                "claim": "local-velocity axis selection, cycle update, and ordered wrap checks",
            },
            {
                "status": "accepted-bounded-static",
                "address": "0x00412d80",
                "symbol": "CBattleEngineWalkerPart__Forward",
                "claim": "retail address/symbol identity under BattleEngineWalkerPart",
            },
            {
                "status": "accepted-bounded-static",
                "address": "0x00413760",
                "symbol": "CBattleEngineWalkerPart__Move",
                "claim": "retail address/symbol identity under BattleEngineWalkerPart",
            },
        ],
        "sourceHypothesis": [
            {"symbol": "CPlayer::ReceiveButtonAction", "claim": "walker forward input route"},
            {"symbol": "CBattleEngineWalkerPart::Forward", "claim": "forward gates and symbolic velocity side effects"},
            {"symbol": "CBattleEngineWalkerPart::Move", "claim": "energy, water, slide, friction, clamp, dash, and walk-cycle branches"},
        ],
        "archiveObservation": [
            {
                "status": "not-applicable-to-control-flow",
                "claim": "AYA archive observations do not establish walker movement behavior",
            }
        ],
        "unresolvedDifferences": [
            {
                "addresses": ["0x00412d80", "0x00413760"],
                "status": "accepted-bounded-static-identity-control-flow-values-runtime-unresolved",
                "retailControlFlowShapeEstablished": False,
                "retailNamedConfigBindingsEstablished": False,
                "retailConstantsEstablished": False,
                "runtimeBehaviorEstablished": False,
            },
            {"constants": list(UNRESOLVED_CONSTANTS), "values": None},
        ],
        "copiedRuntimeMeasurement": [
            {
                "status": "required-not-measured",
                "measurementFieldPartition": {
                    "scalarMeasurableNow": list(SCALAR_MEASURABLE_FIELDS),
                    "requiresFutureProbe": list(FUTURE_PROBE_FIELDS),
                    "sourceShapedFixtureInputs": list(SOURCE_SHAPED_FIXTURE_INPUTS),
                },
                "requiredFutureAcceptanceGate": {
                    "satisfied": False,
                    "publicationAuthorized": False,
                    "schemaVersion": trajectory_schema.PUBLIC_SCHEMA,
                    "requiredStatus": trajectory_schema.PUBLIC_STATUS,
                    "attemptCount": 2,
                    "attemptOrder": [1, 2],
                    "thirdAttemptForbidden": True,
                    "distinctIdentityFields": ["receiptSha256", "runDigest"],
                    "requiredIntegrity": [
                        "receiptRevalidated",
                        "foregroundMaintained",
                        "keyUpConfirmed",
                        "cleanupConfirmed",
                    ],
                    "sampling": {
                        "cadenceMs": 10,
                        "baselineMs": 500,
                        "holdMs": 2000,
                        "releaseMs": 750,
                    },
                    "maximumPairDeltas": {
                        "relativeSteadySpeed": 0.10,
                        "responseLatencyUnionMs": 30,
                        "releaseLatencyUnionMs": 50,
                        "normalizedResponseNode": 0.10,
                    },
                },
            }
        ],
        "rebuildContract": [
            {
                "status": "blocked-until-runtime-accepted",
                "futureConsumer": FUTURE_CORE_CONSUMER,
                "authorizedBehaviorChange": False,
            }
        ],
    }


def validate_evidence_manifest(candidate: Mapping[str, Any]) -> None:
    expected = evidence_manifest()
    if candidate != expected:
        raise ModelError("evidence promotion or mutation rejected")
    if candidate["copiedRuntimeMeasurement"][0]["status"] != "required-not-measured":
        raise ModelError("copied-runtime evidence promotion rejected")
    if candidate["rebuildContract"][0]["authorizedBehaviorChange"]:
        raise ModelError("rebuild behavior authorization rejected")


def validate_future_core_targets(candidate: Mapping[str, Any]) -> None:
    if candidate != _canonical_future_core_targets():
        raise ModelError("future Core target or translation contract mutation rejected")
    translation = candidate.get("translationContract")
    if not isinstance(translation, Mapping) or translation.get("satisfied") is not False:
        raise ModelError("future Core translation contract promotion rejected")
    if candidate.get("targetSetStatus") != "open-blocked-translation-contract-incomplete":
        raise ModelError("future Core target set closure rejected")


def _read_text(path: Path, role: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ModelError(f"missing or unreadable {role}") from error


def validate_repository_evidence(repo_root: Path) -> dict[str, Any]:
    """Validate the exact source pin, crosswalk rows, and required source tokens."""
    repo_root = Path(repo_root).resolve()
    try:
        crosswalk = json.loads(_read_text(repo_root / SOURCE_CROSSWALK, "source crosswalk"))
    except json.JSONDecodeError as error:
        raise ModelError("invalid source crosswalk") from error
    try:
        crosswalk_validator.validate_document(crosswalk, repo_root)
    except crosswalk_validator.CrosswalkValidationError as error:
        raise ModelError("hardened crosswalk validation failed") from error
    if crosswalk.get("sourceRevision") != SOURCE_REVISION:
        raise ModelError("crosswalk source pin mismatch")
    rows = {row.get("id"): row for row in crosswalk.get("rows", []) if isinstance(row, dict)}
    for row_id, required_tokens in REQUIRED_ROWS.items():
        row = rows.get(row_id)
        if not row:
            raise ModelError(f"missing crosswalk row: {row_id}")
        source = row.get("sourceHypothesis", {})
        declared = tuple(source.get("requiredTokens", ()))
        if declared != required_tokens:
            raise ModelError(f"missing or promoted crosswalk tokens: {row_id}")
        if source.get("status") != "hypothesis-only":
            raise ModelError(f"source evidence promotion rejected: {row_id}")
        expected_runtime_status = (
            "accepted-input-state-handoff-only"
            if row_id == "player_forward_route"
            else "required-not-measured"
        )
        if row.get("copiedRuntimeMeasurement", {}).get("status") != expected_runtime_status:
            raise ModelError(f"copied-runtime runtime status mismatch: {row_id}")
        if row.get("rebuildContract", {}).get("status") != "blocked-until-runtime-accepted":
            raise ModelError(f"rebuild contract promotion rejected: {row_id}")
        if row_id in STEAM_ROW_CONTRACTS:
            expected_status, expected_address, expected_symbol = STEAM_ROW_CONTRACTS[row_id]
            steam = row.get("steamStatic", {})
            if (steam.get("status"), steam.get("address"), steam.get("symbol")) != (
                expected_status,
                expected_address,
                expected_symbol,
            ):
                raise ModelError(f"missing or promoted Steam static row: {row_id}")
    for relative_path, tokens in SOURCE_TOKEN_CONTRACTS.items():
        text = _read_text(repo_root / relative_path, "pinned source")
        missing = [token for token in tokens if token not in text]
        if missing:
            raise ModelError(f"missing pinned source tokens: {relative_path.name}")
    for relative_path, tokens in SOURCE_ORDER_CONTRACTS.items():
        text = _read_text(repo_root / relative_path, "pinned source")
        positions = [text.find(token) for token in tokens]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            raise ModelError(f"source control-flow order mismatch: {relative_path.name}")
    for relative_path, tokens in STEAM_EVIDENCE_TOKEN_CONTRACTS.items():
        text = _read_text(repo_root / relative_path, "tracked Steam evidence")
        if any(token not in text for token in tokens):
            raise ModelError(f"missing tracked Steam evidence tokens: {relative_path.name}")
    manifest = evidence_manifest()
    validate_evidence_manifest(manifest)
    return manifest


def generated_fixtures() -> tuple[WalkerFixture, ...]:
    """Generate a deterministic branch-covering fixture catalog."""
    base_move = MoveBranches(
        current_weapon_present=True,
        player_present=True,
        recent_ground=True,
        energy_limited=True,
        cloaked=False,
        shields_recharging_before_move=True,
        recharge_exceeds_capacity=False,
        going_into_water_checks=(False, False),
        should_slide=False,
        on_ground=True,
        horizontal_speed_exceeds_max=False,
        dash_below_friction_threshold=None,
        walking=True,
    )
    no_wrap_x = WalkCycleBranches(True, False, False)
    return (
        WalkerFixture("grounded-forward-x", (0.0, -0.5), True, 0, False, ForwardBranches(), base_move, no_wrap_x),
        WalkerFixture(
            "airborne-water-idle",
            (0.0, -1.0),
            False,
            0,
            False,
            ForwardBranches(),
            replace(
                base_move,
                current_weapon_present=False,
                player_present=False,
                recent_ground=False,
                energy_limited=False,
                shields_recharging_before_move=False,
                going_into_water_checks=(True, True),
                on_ground=False,
                horizontal_speed_exceeds_max=False,
                walking=False,
            ),
            None,
        ),
        WalkerFixture(
            "dash-active-slide",
            (0.0, -1.0),
            True,
            3,
            False,
            ForwardBranches(),
            replace(base_move, recent_ground=False, should_slide=True, on_ground=False, walking=False),
            None,
        ),
        WalkerFixture(
            "dash-trigger-slow-y-upper",
            (0.0, -1.0),
            True,
            0,
            True,
            ForwardBranches(True, True, True),
            replace(
                base_move,
                shields_recharging_before_move=False,
                recharge_exceeds_capacity=True,
                horizontal_speed_exceeds_max=True,
                dash_below_friction_threshold=True,
            ),
            WalkCycleBranches(False, True, False),
        ),
        WalkerFixture(
            "dash-window-miss-lower-wrap",
            (0.0, -0.9),
            True,
            0,
            False,
            ForwardBranches(False, True, False),
            replace(base_move, energy_limited=False, cloaked=True, on_ground=False),
            WalkCycleBranches(True, False, True),
        ),
        WalkerFixture(
            "grounded-no-friction-idle",
            (0.0, -0.25),
            True,
            0,
            False,
            ForwardBranches(True, False, False),
            replace(base_move, recent_ground=False, on_ground=False, walking=False),
            None,
        ),
        WalkerFixture(
            "speed-over-max-dash-gate-closed",
            (0.0, -0.4),
            True,
            0,
            False,
            ForwardBranches(),
            replace(base_move, horizontal_speed_exceeds_max=True, dash_below_friction_threshold=False),
            no_wrap_x,
        ),
    )


def _validate_identifier(value: str, role: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", value):
        raise ModelError(f"private path or invalid {role}")


def _validate_fixture(fixture: WalkerFixture) -> None:
    _validate_identifier(fixture.fixture_id, "fixture id")
    if len(fixture.normalized_input) != 2 or not all(math.isfinite(value) and -1.0 <= value <= 1.0 for value in fixture.normalized_input):
        raise ModelError("invalid normalized input")
    if fixture.dash_count < 0:
        raise ModelError("invalid dash count")
    if fixture.battleengine_state != "walker":
        raise ModelError("invalid walker-path state fixture")
    if (
        len(fixture.move.going_into_water_checks) != 2
        or any(type(value) is not bool for value in fixture.move.going_into_water_checks)
    ):
        raise ModelError("water checks must be exactly two booleans")
    if not fixture.grounded_at_forward or fixture.dash_count > 0:
        if fixture.forward != ForwardBranches():
            raise ModelError("unreachable Forward branch fixture")
    if fixture.forward.reverse_start_within_window and not fixture.forward.crosses_dash_end:
        raise ModelError("invalid dash-window branch fixture")
    if fixture.move.going_into_water_checks[0] and fixture.move.should_slide:
        raise ModelError("unreachable slide branch fixture")
    move_dash_active = fixture.dash_count > 0 or fixture.forward.reverse_start_within_window
    if fixture.move.horizontal_speed_exceeds_max:
        if any(fixture.move.going_into_water_checks) or not (fixture.move.on_ground or move_dash_active):
            raise ModelError("unreachable speed-clamp comparison fixture")
        if type(fixture.move.dash_below_friction_threshold) is not bool:
            raise ModelError("missing dash-friction threshold fixture")
    elif fixture.move.dash_below_friction_threshold is not None:
        raise ModelError("dead dash-friction threshold fixture")
    recharge = fixture.move.recent_ground and fixture.move.energy_limited and not fixture.move.cloaked
    if fixture.move.recharge_exceeds_capacity and not recharge:
        raise ModelError("unreachable energy-cap branch fixture")
    if fixture.move.walking != (fixture.walk_cycle is not None):
        raise ModelError("walk-cycle branch fixture mismatch")
    if (
        fixture.walk_cycle is not None
        and fixture.walk_cycle.exceeds_positive_pi
        and fixture.walk_cycle.below_negative_pi_after_upper_check
    ):
        raise ModelError("impossible walk-cycle wrap fixture")


def _event(events: list[dict[str, Any]], branches: set[str], call: str, action: str, evidence: str, **details: Any) -> None:
    branch = details.pop("branch", None)
    if branch:
        branches.add(branch)
    events.append({"sequence": len(events), "call": call, "action": action, "evidence": evidence, "details": details})


def _serialized_fixture_inputs(fixture: WalkerFixture) -> dict[str, Any]:
    walk = fixture.walk_cycle
    return {
        "battleEngineState": fixture.battleengine_state,
        "normalizedInput": list(fixture.normalized_input),
        "groundedAtForward": fixture.grounded_at_forward,
        "dashCount": fixture.dash_count,
        "slowMovement": fixture.slow_movement,
        "forward": {
            "crossesDashStart": fixture.forward.crosses_dash_start,
            "crossesDashEnd": fixture.forward.crosses_dash_end,
            "reverseStartWithinWindow": fixture.forward.reverse_start_within_window,
        },
        "move": {
            "currentWeaponPresent": fixture.move.current_weapon_present,
            "playerPresent": fixture.move.player_present,
            "recentGround": fixture.move.recent_ground,
            "energyLimited": fixture.move.energy_limited,
            "cloaked": fixture.move.cloaked,
            "shieldsRechargingBeforeMove": fixture.move.shields_recharging_before_move,
            "rechargeExceedsCapacity": fixture.move.recharge_exceeds_capacity,
            "goingIntoWaterChecks": list(fixture.move.going_into_water_checks),
            "shouldSlide": fixture.move.should_slide,
            "onGround": fixture.move.on_ground,
            "horizontalSpeedExceedsMax": fixture.move.horizontal_speed_exceeds_max,
            "dashBelowFrictionThreshold": fixture.move.dash_below_friction_threshold,
            "walking": fixture.move.walking,
        },
        "walkCycle": {
            "present": walk is not None,
            "localXMagnitudeGreater": None if walk is None else walk.local_x_magnitude_greater,
            "exceedsPositivePi": None if walk is None else walk.exceeds_positive_pi,
            "belowNegativePiAfterUpperCheck": None if walk is None else walk.below_negative_pi_after_upper_check,
        },
    }


def execute_fixture(fixture: WalkerFixture, *, manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Execute one fixture as ordered symbolic source control flow."""
    validate_evidence_manifest(evidence_manifest() if manifest is None else manifest)
    _validate_fixture(fixture)
    state = SymbolicState(dash_count=str(fixture.dash_count))
    dash_active = fixture.dash_count > 0
    dash_triggered = False
    events: list[dict[str, Any]] = []
    branches: set[str] = set()

    _event(events, branches, "CPlayer::ReceiveButtonAction", "dispatch-forward", "sourceHypothesis", normalizedInput=list(fixture.normalized_input))
    _event(events, branches, "CBattleEngineWalkerPart::Forward", "enter", "sourceHypothesis")
    if not fixture.grounded_at_forward:
        _event(events, branches, "CBattleEngineWalkerPart::Forward", "return-airborne", "sourceHypothesis", branch="forward.airborne_return")
    elif dash_active:
        _event(events, branches, "CBattleEngineWalkerPart::Forward", "return-dash-active", "sourceHypothesis", branch="forward.dash_active_return")
    else:
        if fixture.forward.crosses_dash_start:
            _event(events, branches, "CBattleEngineWalkerPart::Forward", "record-hard-forward-time", "sourceHypothesis", branch="forward.record_hard_forward", value="eventTime")
        _event(
            events,
            branches,
            "CBattleEngineWalkerPart::Forward",
            "evaluate-dash-end-crossing",
            "sourceHypothesis",
            result=fixture.forward.crosses_dash_end,
        )
        if fixture.forward.crosses_dash_end:
            _event(
                events,
                branches,
                "CBattleEngineWalkerPart::Forward",
                "evaluate-reverse-start-window",
                "sourceHypothesis",
                result=fixture.forward.reverse_start_within_window,
            )
        if fixture.forward.crosses_dash_end and fixture.forward.reverse_start_within_window:
            state.dash_count = "unresolvedDashLength"
            dash_active = True
            dash_triggered = True
            _event(events, branches, "CBattleEngineWalkerPart::Forward", "dash-side-effects", "sourceHypothesis", branch="forward.trigger_dash", effects=["playStrafeSound", "loseWeaponCharge", "zoomOutTime=zero", "dashCount=unresolvedDashLength"])
        else:
            _event(events, branches, "CBattleEngineWalkerPart::Forward", "no-dash", "sourceHypothesis", branch="forward.no_dash")
        state.last_move_y = "normalizedInputY"
        scale_branch = "forward.slow_scale" if fixture.slow_movement else "forward.normal_scale"
        forward_delta = "-inputY*unresolvedAcceleration"
        if dash_triggered:
            forward_delta += "*unresolvedDashVelocityMultiplier"
        state.velocity = f"initialVelocity + yawTransform(0,{forward_delta},0)"
        if fixture.slow_movement:
            state.velocity += "/unresolvedSlowMovementFactor"
        _event(events, branches, "CBattleEngineWalkerPart::Forward", "add-symbolic-velocity", "sourceHypothesis", branch=scale_branch, velocity=state.velocity)

    _event(events, branches, "CBattleEngine::Move", "dispatch-walker-part", "steamStatic", address="0x004081c0")
    _event(events, branches, "CBattleEngineWalkerPart::Move", "enter", "sourceHypothesis")
    state.engine_state = "enginesOff"
    _event(events, branches, "CBattleEngineWalkerPart::Move", "set-engine-state", "sourceHypothesis", value=state.engine_state)
    if fixture.move.current_weapon_present:
        branches.add("move.weapon_present")
    else:
        branches.add("move.weapon_missing")
        state.current_weapon_slot = "zero"
        _event(events, branches, "CBattleEngineWalkerPart::Move", "select-primary-weapon-slot", "sourceHypothesis")
    stat_branch = "move.player_stat" if fixture.move.player_present else "move.no_player_stat"
    branches.add(stat_branch)
    if fixture.move.player_present:
        _event(events, branches, "CBattleEngineWalkerPart::Move", "increment-time-as-walker", "sourceHypothesis")
    _event(events, branches, "CBattleEngineWalkerPart::Move", "move-all-weapon-emitters", "sourceHypothesis", enabled=False)

    recharge = fixture.move.recent_ground and fixture.move.energy_limited and not fixture.move.cloaked
    if recharge:
        branches.add("move.recharge")
        half = not fixture.move.shields_recharging_before_move
        branches.add("move.recharge_halved" if half else "move.recharge_full")
        state.energy = "initialEnergy + unresolvedGroundEnergyIncrease"
        if half:
            state.energy += "/unresolvedShieldRechargeDivisor"
        if fixture.move.recharge_exceeds_capacity:
            state.energy = "unresolvedEnergyMaximum"
        branches.add("move.energy_capped" if fixture.move.recharge_exceeds_capacity else "move.energy_not_capped")
        _event(events, branches, "CBattleEngineWalkerPart::Move", "recharge-energy-symbolically", "sourceHypothesis", energy=state.energy)
    else:
        branches.add("move.no_recharge")
    state.shields_recharging = True
    state.shields = state.energy
    _event(events, branches, "CBattleEngineWalkerPart::Move", "copy-energy-to-shields", "sourceHypothesis", shields=state.shields)

    first_water_result = fixture.move.going_into_water_checks[0]
    _event(events, branches, "CBattleEngineWalkerPart::Move", "evaluate-going-into-water", "sourceHypothesis", occurrence=1, result=first_water_result)
    if first_water_result:
        branches.add("move.water")
        state.velocity = "vector(0,0,currentVelocityZ)"
        _event(events, branches, "CBattleEngineWalkerPart::Move", "zero-horizontal-velocity", "sourceHypothesis")
    elif fixture.move.should_slide:
        _event(events, branches, "CBattleEngineWalkerPart::Move", "evaluate-should-slide", "sourceHypothesis", result=True)
        branches.add("move.slide")
        state.flags = "initialFlags | slideFlag"
        _event(events, branches, "CBattleEngineWalkerPart::Move", "set-slide-and-call-slide", "sourceHypothesis")
    else:
        _event(events, branches, "CBattleEngineWalkerPart::Move", "evaluate-should-slide", "sourceHypothesis", result=False)
        branches.add("move.clear_slide")
        state.flags = "initialFlags & ~slideFlag"
        _event(events, branches, "CBattleEngineWalkerPart::Move", "clear-slide", "sourceHypothesis")

    second_water_result = fixture.move.going_into_water_checks[1]
    _event(events, branches, "CBattleEngineWalkerPart::Move", "evaluate-going-into-water", "sourceHypothesis", occurrence=2, result=second_water_result)
    friction = not second_water_result and (fixture.move.on_ground or dash_active)
    if friction:
        branches.add("move.friction")
        state.velocity = f"({state.velocity})*unresolvedWalkFriction"
        _event(events, branches, "CBattleEngineWalkerPart::Move", "apply-symbolic-friction", "sourceHypothesis", velocity=state.velocity)
        branches.add("move.speed_exceeds_max" if fixture.move.horizontal_speed_exceeds_max else "move.speed_within_max")
        _event(
            events,
            branches,
            "CBattleEngineWalkerPart::Move",
            "evaluate-horizontal-speed",
            "sourceHypothesis",
            horizontalSpeedExceedsUnresolvedMaximum=fixture.move.horizontal_speed_exceeds_max,
            result=fixture.move.horizontal_speed_exceeds_max,
        )
        clamp = False
        if fixture.move.horizontal_speed_exceeds_max:
            branches.add("move.dash_clamp_gate_open" if fixture.move.dash_below_friction_threshold else "move.dash_clamp_gate_closed")
            clamp = fixture.move.dash_below_friction_threshold
            _event(
                events,
                branches,
                "CBattleEngineWalkerPart::Move",
                "evaluate-dash-friction-threshold",
                "sourceHypothesis",
                dashCountBelowUnresolvedFrictionThreshold=fixture.move.dash_below_friction_threshold,
                result=clamp,
            )
        branches.add("move.speed_clamp" if clamp else "move.no_speed_clamp")
        if clamp:
            state.velocity = "clampHorizontalToUnresolvedMaximumPreserveZ"
            _event(events, branches, "CBattleEngineWalkerPart::Move", "clamp-symbolic-horizontal-speed", "sourceHypothesis", velocity=state.velocity)
    else:
        branches.add("move.no_friction")

    if dash_active:
        state.dash_count = f"({state.dash_count})-1"
        branches.add("move.dash_decrement")
        _event(events, branches, "CBattleEngineWalkerPart::Move", "decrement-dash-count", "sourceHypothesis", remaining=state.dash_count)
    else:
        branches.add("move.no_dash_decrement")

    if fixture.move.walking:
        branches.add("move.walk_cycle")
        walk = fixture.walk_cycle
        assert walk is not None
        _event(events, branches, "CBattleEngineWalkerPart::UpdateWalkCycle", "enter", "steamStatic", address="0x00412ad0")
        state.old_walk_cycle = state.walk_cycle
        _event(events, branches, "CBattleEngineWalkerPart::UpdateWalkCycle", "transpose-orientation-and-project-velocity", "steamStatic", result="symbolicLocalVelocity")
        axis = "localX" if walk.local_x_magnitude_greater else "localY"
        multiplier = "unresolvedLocalXMultiplier" if walk.local_x_magnitude_greater else "unresolvedLocalYMultiplier"
        branches.add("walk.x_axis" if walk.local_x_magnitude_greater else "walk.y_axis")
        state.walk_cycle = f"initialWalkCycle + {axis}*{multiplier}"
        _event(events, branches, "CBattleEngineWalkerPart::UpdateWalkCycle", "advance-symbolic-cycle", "steamStatic", axis=axis, cycle=state.walk_cycle)
        branches.add("walk.upper_wrap" if walk.exceeds_positive_pi else "walk.no_upper_wrap")
        _event(events, branches, "CBattleEngineWalkerPart::UpdateWalkCycle", "evaluate-upper-wrap", "steamStatic", result=walk.exceeds_positive_pi)
        if walk.exceeds_positive_pi:
            state.walk_cycle += " - unresolvedTwoPiSpan"
            _event(events, branches, "CBattleEngineWalkerPart::UpdateWalkCycle", "upper-wrap", "steamStatic")
        branches.add("walk.lower_wrap" if walk.below_negative_pi_after_upper_check else "walk.no_lower_wrap")
        _event(events, branches, "CBattleEngineWalkerPart::UpdateWalkCycle", "evaluate-lower-wrap-after-upper-check", "steamStatic", result=walk.below_negative_pi_after_upper_check)
        if walk.below_negative_pi_after_upper_check:
            state.walk_cycle += " + unresolvedTwoPiSpan"
            _event(events, branches, "CBattleEngineWalkerPart::UpdateWalkCycle", "lower-wrap", "steamStatic")
    else:
        branches.add("move.no_walk_cycle")

    future_core_targets = _canonical_future_core_targets()
    validate_future_core_targets(future_core_targets)
    report = {
        "schema": SCHEMA,
        "fixtureId": fixture.fixture_id,
        "sourceRevision": SOURCE_REVISION,
        "evidence": evidence_manifest(),
        "measurementFieldPartition": {
            "scalarMeasurableNow": list(SCALAR_MEASURABLE_FIELDS),
            "requiresFutureProbe": list(FUTURE_PROBE_FIELDS),
            "sourceShapedFixtureInputs": list(SOURCE_SHAPED_FIXTURE_INPUTS),
        },
        "initialInputsAndState": _serialized_fixture_inputs(fixture),
        "calls": [event["call"] for event in events if event["action"] in {"dispatch-forward", "enter", "dispatch-walker-part"}],
        "events": events,
        "branches": sorted(branches),
        "finalSymbolicState": asdict(state),
        "retailValuesResolved": False,
        "futureConsumer": FUTURE_CORE_CONSUMER,
        "futureCoreTargets": future_core_targets,
    }
    _reject_private_paths(report)
    return report


def execute_catalog(fixtures: Iterable[WalkerFixture] | None = None) -> dict[str, Any]:
    selected = tuple(generated_fixtures() if fixtures is None else fixtures)
    reports = []
    for fixture in selected:
        first = execute_fixture(fixture)
        if first != execute_fixture(fixture):
            raise ModelError(f"nondeterministic fixture rejected: {fixture.fixture_id}")
        reports.append(first)
    coverage = sorted({branch for report in reports for branch in report["branches"]})
    missing = sorted(BRANCH_IDS - set(coverage))
    if missing:
        raise ModelError("generated fixture branch coverage incomplete: " + ", ".join(missing))
    future_core_targets = _canonical_future_core_targets()
    validate_future_core_targets(future_core_targets)
    result = {
        "schema": SCHEMA,
        "sourceRevision": SOURCE_REVISION,
        "evidence": evidence_manifest(),
        "measurementFieldPartition": {
            "scalarMeasurableNow": list(SCALAR_MEASURABLE_FIELDS),
            "requiresFutureProbe": list(FUTURE_PROBE_FIELDS),
            "sourceShapedFixtureInputs": list(SOURCE_SHAPED_FIXTURE_INPUTS),
        },
        "branchCoverage": coverage,
        "fixtures": reports,
        "retailValuesResolved": False,
        "futureConsumer": FUTURE_CORE_CONSUMER,
        "futureCoreTargets": future_core_targets,
    }
    _reject_private_paths(result)
    return result


def _reject_private_paths(value: Any) -> None:
    for text in _all_strings(value):
        if re.match(r"^(?:\\\\|/|file:)", text, re.IGNORECASE) or re.search(
            r"(?:[A-Za-z]:[\\/]|/(?:Users|home|private|tmp|dev|proc|sys)/|\\Users\\)",
            text,
            re.IGNORECASE,
        ):
            raise ModelError("private path rejected")


def _all_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from _all_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _all_strings(item)


def _validate_report_contracts(report: Mapping[str, Any]) -> None:
    try:
        validate_evidence_manifest(report["evidence"])
        validate_future_core_targets(report["futureCoreTargets"])
    except (KeyError, TypeError) as error:
        raise ModelError("report contract missing or malformed") from error
    if report.get("retailValuesResolved") is not False:
        raise ModelError("retail value resolution promotion rejected")
    if report.get("futureConsumer") != FUTURE_CORE_CONSUMER:
        raise ModelError("future Core consumer mutation rejected")

    fixtures = report.get("fixtures")
    if fixtures is None:
        return
    if not isinstance(fixtures, list):
        raise ModelError("catalog fixtures malformed")
    for fixture_report in fixtures:
        if not isinstance(fixture_report, Mapping):
            raise ModelError("catalog fixture report malformed")
        _validate_report_contracts(fixture_report)


def _validate_canonical_render_report(report: Mapping[str, Any]) -> None:
    if "fixtures" in report:
        expected = execute_catalog()
    else:
        fixture_id = report.get("fixtureId")
        matches = [fixture for fixture in generated_fixtures() if fixture.fixture_id == fixture_id]
        if len(matches) != 1:
            raise ModelError("noncanonical fixture report rejected")
        expected = execute_fixture(matches[0])
    if report != expected:
        raise ModelError("canonical report mutation rejected")


def render_report(report: Mapping[str, Any]) -> bytes:
    _reject_private_paths(report)
    _validate_report_contracts(report)
    _validate_canonical_render_report(report)
    return (json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def _default_repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "goal.policy.md").is_file() and (candidate / "package.json").is_file():
            return candidate
    raise ModelError("repository root not found")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=_default_repo_root())
    parser.add_argument("--fixture-id")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        validate_repository_evidence(args.repo_root)
        fixtures = generated_fixtures()
        if args.fixture_id:
            matches = [fixture for fixture in fixtures if fixture.fixture_id == args.fixture_id]
            if len(matches) != 1:
                raise ModelError("unknown fixture id")
            report = execute_fixture(matches[0])
        else:
            report = execute_catalog(fixtures)
    except ModelError as error:
        print(f"reference model rejected: {error}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(render_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
