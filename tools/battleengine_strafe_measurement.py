#!/usr/bin/env python3
"""Walker strafe/lateral scalar measurement helpers (rebuild-grade).

Path-speed analysis for Movement/Left (or Right) holds. Live dual-accept is
required before any Core constant.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence


class StrafeError(ValueError):
    pass


@dataclass(frozen=True)
class PathSample:
    tick: int
    phase: str
    position: tuple[float, float, float]


@dataclass(frozen=True)
class StrafeAttemptMetrics:
    attempt: int
    accepted: bool
    steady_lateral_speed: float
    baseline_b95_speed: float
    sample_counts: dict[str, int]
    response_latency_ms: tuple[int, int]
    release_latency_ms: tuple[int, int]
    hold_endpoint_displacement: float


def path_speeds(
    samples: Sequence[PathSample],
    frequency: int,
) -> list[tuple[PathSample, float]]:
    if frequency <= 0:
        raise StrafeError("QPC frequency must be positive")
    if len(samples) < 2:
        raise StrafeError("path phase undersampled")
    out: list[tuple[PathSample, float]] = []
    for previous, current in zip(samples, samples[1:]):
        elapsed = (current.tick - previous.tick) / frequency
        if elapsed <= 0:
            raise StrafeError("sample time must be monotonic")
        disp = math.sqrt(
            sum((current.position[i] - previous.position[i]) ** 2 for i in range(3))
        )
        out.append((current, disp / elapsed))
    return out


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


def _first_three(
    rates: Sequence[tuple[PathSample, float]],
    threshold: float,
    frequency: int,
    *,
    mode: str,
) -> tuple[int, int]:
    """First three *qualifying* samples (zeros between staircase edges allowed)."""

    if not rates:
        raise StrafeError("latency window empty")
    origin = rates[0][0].tick
    count = 0
    first_tick: int | None = None
    for sample, rate in rates:
        ok = rate >= threshold if mode == "above" else rate <= threshold
        if not ok:
            continue
        count += 1
        if count == 1:
            first_tick = sample.tick
        if count >= 3 and first_tick is not None:
            lower = int(math.floor((first_tick - origin) * 1000.0 / frequency / 10) * 10)
            upper = int(math.ceil((sample.tick - origin) * 1000.0 / frequency / 10) * 10)
            return max(0, lower), max(lower, upper)
    raise StrafeError(f"strafe {mode} threshold was not sustained")


def analyze_strafe_attempt(
    *,
    attempt: int,
    baseline: Sequence[PathSample],
    hold: Sequence[PathSample],
    release: Sequence[PathSample],
    frequency: int,
) -> StrafeAttemptMetrics:
    if attempt not in (1, 2):
        raise StrafeError("attempt must be 1 or 2")
    for name, rows in (("baseline", baseline), ("hold", hold), ("release", release)):
        if len(rows) < 8:
            raise StrafeError(f"{name} phase undersampled")
        if any(r.phase != name for r in rows):
            raise StrafeError(f"{name} phase label mismatch")

    baseline_speeds = path_speeds(baseline, frequency)
    hold_speeds = path_speeds(hold, frequency)
    release_speeds = path_speeds(release, frequency)
    # Retail motion is staircase-polled: many adjacent samples have zero
    # displacement. Use active (non-static) edges for steady median, with
    # whole-hold endpoint/time as a corroborating floor.
    hold_elapsed = (hold[-1].tick - hold[0].tick) / frequency
    hold_disp = math.sqrt(
        sum((hold[-1].position[i] - hold[0].position[i]) ** 2 for i in range(3))
    )
    active_hold = [(s, sp) for s, sp in hold_speeds if sp > 0.05]
    endpoint_speed = hold_disp / hold_elapsed if hold_elapsed > 0 else 0.0
    if len(active_hold) >= 8:
        steady = active_hold[-max(8, len(active_hold) // 3) :]
        edge_median = statistics.median(s for _, s in steady)
        # Prefer whole-hold endpoint speed when staircase edges spike above cruise.
        steady_speed = endpoint_speed if endpoint_speed > 0 else edge_median
        if endpoint_speed > 0 and edge_median > 0:
            # Bound edge median into a sensible band around endpoint cruise.
            if 0.5 * endpoint_speed <= edge_median <= 3.0 * endpoint_speed:
                steady_speed = statistics.median([endpoint_speed, edge_median])
    elif endpoint_speed > 0:
        steady_speed = endpoint_speed
    else:
        raise StrafeError("steady strafe window undersampled")
    if steady_speed <= 0:
        raise StrafeError("response steady lateral speed is not positive")
    b95 = _percentile([s for _, s in baseline_speeds], 0.95)
    if steady_speed <= 1.5 * max(b95, 1e-6):
        raise StrafeError("strafe steady speed did not dominate baseline")
    base_disp = math.sqrt(
        sum((baseline[-1].position[i] - baseline[0].position[i]) ** 2 for i in range(3))
    )
    if hold_disp <= 1.5 * max(base_disp, 1e-6):
        raise StrafeError("strafe displacement did not dominate baseline drift")
    threshold = max(0.20 * steady_speed, 1.10 * b95)
    # Latency uses full series so early zeros are skipped until motion edges.
    response = _first_three(hold_speeds, threshold, frequency, mode="above")
    coast = 0.50 * steady_speed
    release_lat = _first_three(release_speeds, coast, frequency, mode="below")
    return StrafeAttemptMetrics(
        attempt=attempt,
        accepted=True,
        steady_lateral_speed=steady_speed,
        baseline_b95_speed=b95,
        sample_counts={
            "baseline": len(baseline),
            "hold": len(hold),
            "release": len(release),
        },
        response_latency_ms=response,
        release_latency_ms=release_lat,
        hold_endpoint_displacement=hold_disp,
    )


def synthetic_strafe_attempt(
    *,
    attempt: int,
    steady_speed: float = 2.5,
    baseline_speed: float = 0.0,
    frequency: int = 10_000_000,
) -> tuple[list[PathSample], list[PathSample], list[PathSample]]:
    step = max(1, round(frequency * 0.01))
    tick = 0
    x = 0.0

    def emit(phase: str, n: int, speed: float, sink: list[PathSample]) -> None:
        nonlocal tick, x
        for _ in range(n):
            sink.append(PathSample(tick=tick, phase=phase, position=(x, 0.0, 0.0)))
            x += speed * 0.01
            tick += step

    baseline: list[PathSample] = []
    hold: list[PathSample] = []
    release: list[PathSample] = []
    emit("baseline", 20, baseline_speed, baseline)
    emit("hold", 5, steady_speed * 0.3, hold)
    emit("hold", 45, steady_speed, hold)
    emit("release", 5, steady_speed * 0.6, release)
    emit("release", 20, 0.0, release)
    return baseline, hold, release
