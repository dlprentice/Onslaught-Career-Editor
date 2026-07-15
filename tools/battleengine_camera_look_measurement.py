#!/usr/bin/env python3
"""Camera / body look-rate measurement harness (M3.1 scaffold).

Pure analysis for ordered yaw/pitch look samples. Live dual-accept is separate;
free-camera patch Q-yaw proofs are canaries only and must not authorize Core
look constants.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence

# Steam-static body yaw hypothesis reused from turn measurement (not camera).
BATTLE_ENGINE_YAW_AXIS_OFFSET = 0x278
# Free-camera patch canaries are not rebuild Core authority.
FREE_CAMERA_PATCH_CANARY_NONCLAIM = (
    "Free-camera Q-yaw/pitch patch proofs are control canaries only; they do "
    "not authorize Core walker or chase-camera look rates."
)


class CameraLookError(ValueError):
    pass


@dataclass(frozen=True)
class LookSample:
    """One poll of look orientation (radians) and optional body yaw-axis store."""

    tick: int
    phase: str
    yaw_rad: float
    pitch_rad: float = 0.0
    yaw_axis: float | None = None


@dataclass(frozen=True)
class CameraLookAttemptMetrics:
    attempt: int
    accepted: bool
    steady_yaw_rate_rad_s: float
    steady_pitch_rate_rad_s: float
    baseline_b95_yaw_rate_rad_s: float
    sample_counts: dict[str, int]
    response_latency_ms: tuple[int, int]
    release_latency_ms: tuple[int, int]


def unwrap_delta(previous: float, current: float) -> float:
    delta = current - previous
    while delta > math.pi:
        delta -= 2.0 * math.pi
    while delta < -math.pi:
        delta += 2.0 * math.pi
    return delta


def phase_angular_rates(
    samples: Sequence[LookSample],
    frequency: int,
    *,
    axis: str,
) -> list[tuple[LookSample, float]]:
    """Wall-clock absolute angular rate between consecutive samples (rad/s)."""

    if frequency <= 0:
        raise CameraLookError("QPC frequency must be positive")
    if axis not in ("yaw", "pitch"):
        raise CameraLookError("axis must be yaw or pitch")
    if len(samples) < 2:
        raise CameraLookError("look phase undersampled")
    rates: list[tuple[LookSample, float]] = []
    for previous, current in zip(samples, samples[1:]):
        elapsed = (current.tick - previous.tick) / frequency
        if elapsed <= 0:
            raise CameraLookError("sample time must be monotonic")
        if axis == "yaw":
            delta = unwrap_delta(previous.yaw_rad, current.yaw_rad)
        else:
            delta = current.pitch_rad - previous.pitch_rad
        rates.append((current, abs(delta) / elapsed))
    return rates


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


def _first_three(
    rates: Sequence[tuple[LookSample, float]],
    threshold: float,
    frequency: int,
) -> tuple[int, int]:
    if not rates:
        raise CameraLookError("latency window empty")
    origin = rates[0][0].tick
    count = 0
    first_tick: int | None = None
    third_tick: int | None = None
    for sample, rate in rates:
        if rate < threshold:
            continue
        count += 1
        if count == 1:
            first_tick = sample.tick
        if count >= 3:
            third_tick = sample.tick
            break
    if first_tick is None or third_tick is None:
        raise CameraLookError("look rate did not sustain three edges above threshold")
    lower = int(math.floor((first_tick - origin) * 1000.0 / frequency / 10) * 10)
    upper = int(math.ceil((third_tick - origin) * 1000.0 / frequency / 10) * 10)
    return max(0, lower), max(lower, upper)


def analyze_camera_look_attempt(
    *,
    attempt: int,
    baseline: Sequence[LookSample],
    hold: Sequence[LookSample],
    release: Sequence[LookSample],
    frequency: int,
    rate_source: str = "orientation",
    min_hold_ratio: float = 3.0,
) -> CameraLookAttemptMetrics:
    """Accept when hold yaw rate dominates baseline and is stable."""

    if attempt not in (1, 2):
        raise CameraLookError("attempt must be 1 or 2")
    if rate_source not in ("orientation", "yaw_axis_store"):
        raise CameraLookError("rate_source must be orientation or yaw_axis_store")

    if rate_source == "yaw_axis_store":
        def store_rates(samples: Sequence[LookSample]) -> list[float]:
            values = [s.yaw_axis for s in samples if s.yaw_axis is not None]
            if len(values) < 5:
                raise CameraLookError("yaw_axis_store undersampled")
            return [abs(v) for v in values if math.isfinite(v)]

        baseline_rates = store_rates(baseline)
        hold_rates = store_rates(hold)
        release_rates = store_rates(release)
        # Fabricate rate rows for latency from hold samples using store magnitude.
        hold_rate_rows = [
            (s, abs(s.yaw_axis or 0.0))
            for s in hold
            if s.yaw_axis is not None and math.isfinite(s.yaw_axis)
        ]
        release_rate_rows = [
            (s, abs(s.yaw_axis or 0.0))
            for s in release
            if s.yaw_axis is not None and math.isfinite(s.yaw_axis)
        ]
        pitch_hold = 0.0
    else:
        baseline_rows = phase_angular_rates(baseline, frequency, axis="yaw")
        hold_rows = phase_angular_rates(hold, frequency, axis="yaw")
        release_rows = phase_angular_rates(release, frequency, axis="yaw")
        pitch_rows = phase_angular_rates(hold, frequency, axis="pitch")
        baseline_rates = [r for _, r in baseline_rows]
        hold_rates = [r for _, r in hold_rows]
        release_rates = [r for _, r in release_rows]
        hold_rate_rows = hold_rows
        release_rate_rows = release_rows
        pitch_active = [r for r in (x for _, x in pitch_rows) if r > 1e-6]
        pitch_hold = statistics.median(pitch_active) if pitch_active else 0.0

    if len(hold_rates) < 5:
        raise CameraLookError("too few hold look rates")
    baseline_b95 = _percentile(baseline_rates, 0.95) if baseline_rates else 0.0
    steady = statistics.median(hold_rates[-max(5, len(hold_rates) // 3) :])
    if not math.isfinite(steady) or steady <= 0:
        raise CameraLookError("steady look yaw rate not positive")
    if steady < max(1e-4, baseline_b95 * min_hold_ratio):
        raise CameraLookError("hold look rate must dominate baseline")

    threshold = max(steady * 0.35, baseline_b95 * 1.5, 1e-4)
    response = _first_three(hold_rate_rows, threshold, frequency)
    # Release latency: first three samples below threshold after hold.
    quiet: list[tuple[LookSample, float]] = []
    for sample, rate in release_rate_rows:
        if rate <= threshold:
            quiet.append((sample, rate))
        elif quiet:
            quiet.clear()
    if len(quiet) < 3:
        # Soft: measure from release start to last sample if quiet never sustained.
        if not release_rate_rows:
            raise CameraLookError("release phase empty")
        origin = release_rate_rows[0][0].tick
        end = release_rate_rows[-1][0].tick
        release_latency = (
            0,
            max(0, int(math.ceil((end - origin) * 1000.0 / frequency / 10) * 10)),
        )
    else:
        origin = release_rate_rows[0][0].tick
        first = quiet[0][0].tick
        third = quiet[2][0].tick
        release_latency = (
            max(0, int(math.floor((first - origin) * 1000.0 / frequency / 10) * 10)),
            max(0, int(math.ceil((third - origin) * 1000.0 / frequency / 10) * 10)),
        )

    return CameraLookAttemptMetrics(
        attempt=attempt,
        accepted=True,
        steady_yaw_rate_rad_s=steady,
        steady_pitch_rate_rad_s=pitch_hold,
        baseline_b95_yaw_rate_rad_s=baseline_b95,
        sample_counts={
            "baseline": len(baseline),
            "hold": len(hold),
            "release": len(release),
        },
        response_latency_ms=response,
        release_latency_ms=release_latency,
    )


def materialize_camera_look_pair_envelope(
    first: CameraLookAttemptMetrics,
    second: CameraLookAttemptMetrics,
    *,
    relative_spread: float = 0.20,
) -> dict[str, object]:
    if not (first.accepted and second.accepted):
        raise CameraLookError("both attempts must be accepted")
    rates = sorted((first.steady_yaw_rate_rad_s, second.steady_yaw_rate_rad_s))
    mid = (rates[0] + rates[1]) / 2.0
    if mid <= 0:
        raise CameraLookError("pair mid rate not positive")
    if (rates[1] - rates[0]) / mid > relative_spread:
        raise CameraLookError("pair look rates not stable")
    pad = max(mid * 0.05, (rates[1] - rates[0]) / 2.0)
    return {
        "schemaVersion": "battleengine-camera-look-rate-scalar-response.v0-scaffold",
        "envelope": {
            "steadyYawRateRadPerSec": {
                "lower": rates[0] - pad,
                "upper": rates[1] + pad,
            }
        },
        "nonclaims": [
            FREE_CAMERA_PATCH_CANARY_NONCLAIM,
            "Scaffold envelope is not dual-accepted retail authority for Core.",
            "No deterministic Core constant is authorized by synthetic fixtures alone.",
        ],
    }


def synthetic_camera_look_attempt(
    *,
    attempt: int,
    steady_rate: float = 0.09,
    baseline_rate: float = 0.0,
    frequency: int = 10_000_000,
) -> tuple[list[LookSample], list[LookSample], list[LookSample]]:
    step = frequency // 100

    def series(phase: str, n: int, rate: float, start: float = 0.0) -> list[LookSample]:
        out: list[LookSample] = []
        yaw = start
        for i in range(n):
            out.append(
                LookSample(
                    tick=i * step,
                    phase=phase,
                    yaw_rad=yaw,
                    pitch_rad=0.0,
                    yaw_axis=rate if rate > 0 else 0.0,
                )
            )
            yaw += rate * 0.01
        return out

    baseline = series("baseline", 20, baseline_rate)
    hold = series("hold", 50, steady_rate)
    release = series("release", 25, 0.0, start=hold[-1].yaw_rad)
    return baseline, hold, release
