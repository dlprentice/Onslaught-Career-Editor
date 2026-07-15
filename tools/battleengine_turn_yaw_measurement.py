#!/usr/bin/env python3
"""Turn/yaw scalar measurement helpers (rebuild-grade scaffold).

Pure analysis for copied-runtime turn/yaw samples. Live dual-accept is not
claimed here: this module is the durable harness entry point that unit tests
drive, and that a future live observer can call once orientation/yaw samples
are collected receipt-bound.

Evidence classes:
- Steam static hypothesis: GeneralVolume yaw-axis field near BattleEngine+0x278
  (see GHIDRA ApplyYawInputByWeaponClass notes); jet Turn writes yaw/roll
  velocity near main-part +0x278/+0x27c.
- Source hypothesis: mGroundTurnRate / mAirTurnRate config defaults (not Core).
- Copied-runtime: required for Core constant authority; not established by
  synthetic fixtures alone.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence

# Steam-static hypothesis only — not a layout completeness claim.
BATTLE_ENGINE_YAW_AXIS_OFFSET = 0x278
# Source-config defaults (quick-reference); not dual-accepted retail truth.
SOURCE_GROUND_TURN_RATE_HYPOTHESIS = 1.5
SOURCE_AIR_TURN_RATE_HYPOTHESIS = 2.0

CADENCE_MS = 10
PHYSICS_TICK_SECONDS = 0.05


class TurnYawError(ValueError):
    """Turn/yaw analysis or fixture failure."""


@dataclass(frozen=True)
class YawSample:
    """One poll of heading and optional yaw-axis store."""

    tick: int
    phase: str
    heading_rad: float
    yaw_axis: float | None = None


@dataclass(frozen=True)
class TurnAttemptMetrics:
    attempt: int
    accepted: bool
    steady_yaw_rate_rad_s: float
    baseline_b95_yaw_rate_rad_s: float
    sample_counts: dict[str, int]
    response_latency_ms: tuple[int, int]
    release_latency_ms: tuple[int, int]


def heading_from_velocity_xz(vx: float, vz: float) -> float:
    """Horizontal heading in radians from velocity (atan2(vx, vz))."""

    if not (math.isfinite(vx) and math.isfinite(vz)):
        raise TurnYawError("velocity components must be finite")
    if abs(vx) < 1e-12 and abs(vz) < 1e-12:
        raise TurnYawError("velocity heading is undefined at near-zero speed")
    return math.atan2(vx, vz)


def unwrap_delta(previous: float, current: float) -> float:
    """Shortest signed angle from previous to current heading."""

    delta = current - previous
    while delta > math.pi:
        delta -= 2.0 * math.pi
    while delta < -math.pi:
        delta += 2.0 * math.pi
    return delta


def phase_yaw_rates(
    samples: Sequence[YawSample],
    frequency: int,
) -> list[tuple[YawSample, float]]:
    """Wall-clock |yaw rate| between consecutive samples (rad/s)."""

    if frequency <= 0:
        raise TurnYawError("QPC frequency must be positive")
    if len(samples) < 2:
        raise TurnYawError("yaw phase undersampled")
    rates: list[tuple[YawSample, float]] = []
    for previous, current in zip(samples, samples[1:]):
        elapsed = (current.tick - previous.tick) / frequency
        if elapsed <= 0:
            raise TurnYawError("sample time must be monotonic")
        delta = unwrap_delta(previous.heading_rad, current.heading_rad)
        rates.append((current, abs(delta) / elapsed))
    return rates


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


def phase_yaw_axis_store_rates(
    samples: Sequence[YawSample],
) -> list[tuple[YawSample, float]]:
    """Treat |yaw_axis| store as instantaneous yaw rate (live turn-p01 shape).

    When Look/Left write a near-steady float into BE+0x278, differentiating it
    as a heading yields ~0. Use the store magnitude as rad/s directly.
    """

    if len(samples) < 2:
        raise TurnYawError("yaw phase undersampled")
    return [(row, abs(float(row.yaw_axis or 0.0))) for row in samples[1:]]


def analyze_turn_attempt(
    *,
    attempt: int,
    baseline: Sequence[YawSample],
    hold: Sequence[YawSample],
    release: Sequence[YawSample],
    frequency: int,
    rate_source: str = "heading",
) -> TurnAttemptMetrics:
    """Accept a turn attempt when hold yaw rate dominates baseline and settles.

    rate_source:
      - "heading": differentiate heading_rad (path/velocity heading series)
      - "yaw_axis_store": use |yaw_axis| as instantaneous rate (live BE+0x278)
    """

    if attempt not in (1, 2):
        raise TurnYawError("attempt must be 1 or 2")
    if rate_source not in ("heading", "yaw_axis_store"):
        raise TurnYawError("rate_source must be heading or yaw_axis_store")
    for phase_name, rows in (("baseline", baseline), ("hold", hold), ("release", release)):
        if len(rows) < 8:
            raise TurnYawError(f"{phase_name} phase undersampled")
        if any(row.phase != phase_name for row in rows):
            raise TurnYawError(f"{phase_name} sample phase label mismatch")

    if rate_source == "yaw_axis_store":
        baseline_rates = phase_yaw_axis_store_rates(baseline)
        hold_rates = phase_yaw_axis_store_rates(hold)
        release_rates = phase_yaw_axis_store_rates(release)
    else:
        baseline_rates = phase_yaw_rates(baseline, frequency)
        hold_rates = phase_yaw_rates(hold, frequency)
        release_rates = phase_yaw_rates(release, frequency)

    steady = hold_rates[-max(8, len(hold_rates) // 3) :]
    if len(steady) < 8:
        raise TurnYawError("steady yaw window undersampled")
    steady_rate = statistics.median(rate for _, rate in steady)
    if steady_rate <= 0:
        raise TurnYawError("response steady yaw rate is not positive")

    b95 = _percentile([rate for _, rate in baseline_rates], 0.95)
    if steady_rate <= 1.5 * max(b95, 1e-6):
        raise TurnYawError("turn steady yaw rate did not dominate baseline")

    # Response: first three consecutive samples at/above 20% of steady.
    threshold = max(0.20 * steady_rate, 1.10 * b95)
    response_latency = _first_three_latency(hold_rates, threshold, frequency, mode="above")
    # Release: decay below 50% of steady (coast/stop turning).
    coast = 0.50 * steady_rate
    release_latency = _first_three_latency(release_rates, coast, frequency, mode="below")

    return TurnAttemptMetrics(
        attempt=attempt,
        accepted=True,
        steady_yaw_rate_rad_s=steady_rate,
        baseline_b95_yaw_rate_rad_s=b95,
        sample_counts={
            "baseline": len(baseline),
            "hold": len(hold),
            "release": len(release),
        },
        response_latency_ms=response_latency,
        release_latency_ms=release_latency,
    )


def _first_three_latency(
    rates: Sequence[tuple[YawSample, float]],
    threshold: float,
    frequency: int,
    *,
    mode: str,
) -> tuple[int, int]:
    if not rates:
        raise TurnYawError("latency window empty")
    origin = rates[0][0].tick
    consecutive = 0
    first_tick: int | None = None
    for sample, rate in rates:
        ok = rate >= threshold if mode == "above" else rate <= threshold
        if ok:
            consecutive += 1
            if consecutive == 1:
                first_tick = sample.tick
            if consecutive >= 3 and first_tick is not None:
                lower = int(math.floor((first_tick - origin) * 1000.0 / frequency / CADENCE_MS) * CADENCE_MS)
                upper = int(math.ceil((sample.tick - origin) * 1000.0 / frequency / CADENCE_MS) * CADENCE_MS)
                return max(0, lower), max(lower, upper)
        else:
            consecutive = 0
            first_tick = None
    raise TurnYawError(f"yaw {mode} threshold was not sustained")


def materialize_turn_pair_envelope(
    first: TurnAttemptMetrics,
    second: TurnAttemptMetrics,
) -> dict[str, object]:
    """Build a public-safe envelope from two accepted attempts (retail units)."""

    if not (first.accepted and second.accepted):
        raise TurnYawError("two accepted attempts are required")
    if (first.attempt, second.attempt) != (1, 2):
        raise TurnYawError("attempt order must be 1 then 2")
    relative = abs(first.steady_yaw_rate_rad_s - second.steady_yaw_rate_rad_s) / min(
        first.steady_yaw_rate_rad_s, second.steady_yaw_rate_rad_s
    )
    if relative > 0.15:
        raise TurnYawError("two-run turn pair is not stable enough for an envelope")

    lo = 0.90 * min(first.steady_yaw_rate_rad_s, second.steady_yaw_rate_rad_s)
    hi = 1.10 * max(first.steady_yaw_rate_rad_s, second.steady_yaw_rate_rad_s)
    return {
        "schemaVersion": "battleengine-walker-turn-yaw-scalar-response.v0-scaffold",
        "status": "two-accepted-fresh-attempts",
        "claim": "scalar-walker-turn-yaw-rate-response",
        "metricUnits": {
            "yawRate": "radians-per-second",
            "latency": "milliseconds",
        },
        "envelope": {
            "steadyYawRateRadPerSec": {"lower": lo, "upper": hi},
            "responseLatencyMs": {
                "lower": min(first.response_latency_ms[0], second.response_latency_ms[0]),
                "upper": max(first.response_latency_ms[1], second.response_latency_ms[1]),
            },
            "releaseLatencyMs": {
                "lower": min(first.release_latency_ms[0], second.release_latency_ms[0]),
                "upper": max(first.release_latency_ms[1], second.release_latency_ms[1]),
            },
        },
        "nonclaims": [
            "Scaffold schema v0 is not a dual-accepted live retail contract.",
            "Source mGroundTurnRate/mAirTurnRate defaults are hypotheses only.",
            "BattleEngine+0x278 yaw-axis offset is a Steam-static hypothesis.",
            "No deterministic Core TurnRate constant is authorized by this scaffold alone.",
        ],
        "sourceHypotheses": {
            "mGroundTurnRate": SOURCE_GROUND_TURN_RATE_HYPOTHESIS,
            "mAirTurnRate": SOURCE_AIR_TURN_RATE_HYPOTHESIS,
            "yawAxisOffset": BATTLE_ENGINE_YAW_AXIS_OFFSET,
        },
    }


def synthetic_turn_attempt(
    *,
    attempt: int,
    steady_rate: float = 1.45,
    baseline_rate: float = 0.02,
    frequency: int = 10_000_000,
) -> tuple[list[YawSample], list[YawSample], list[YawSample]]:
    """Build a source-shaped synthetic yaw ramp for offline harness tests."""

    step = max(1, round(frequency * CADENCE_MS / 1000))
    heading = 0.0
    baseline: list[YawSample] = []
    hold: list[YawSample] = []
    release: list[YawSample] = []
    tick = 0

    def emit(phase: str, count: int, rate: float, sink: list[YawSample]) -> None:
        nonlocal heading, tick
        for _ in range(count):
            heading += rate * (CADENCE_MS / 1000.0)
            sink.append(YawSample(tick=tick, phase=phase, heading_rad=heading, yaw_axis=rate))
            tick += step

    emit("baseline", 20, baseline_rate, baseline)
    # Ramp into steady turn.
    emit("hold", 5, steady_rate * 0.4, hold)
    emit("hold", 40, steady_rate, hold)
    emit("release", 5, steady_rate * 0.7, release)
    emit("release", 20, baseline_rate, release)
    return baseline, hold, release
