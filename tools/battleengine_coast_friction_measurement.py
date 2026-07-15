#!/usr/bin/env python3
"""Coast / friction release model scaffold (M1.6).

Analyzes path-speed decay after a control release. Live dual-accept is separate;
synthetic fixtures do not authorize Core friction constants.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence


class CoastFrictionError(ValueError):
    pass


@dataclass(frozen=True)
class CoastSample:
    tick: int
    phase: str
    position: tuple[float, float, float]


@dataclass(frozen=True)
class CoastAttemptMetrics:
    attempt: int
    accepted: bool
    hold_steady_speed: float
    release_half_life_ms: float
    release_terminal_speed: float
    sample_counts: dict[str, int]


def path_speeds(
    samples: Sequence[CoastSample],
    frequency: int,
) -> list[tuple[CoastSample, float]]:
    if frequency <= 0:
        raise CoastFrictionError("frequency must be positive")
    if len(samples) < 2:
        raise CoastFrictionError("undersampled")
    out: list[tuple[CoastSample, float]] = []
    for previous, current in zip(samples, samples[1:]):
        dt = (current.tick - previous.tick) / frequency
        if dt <= 0:
            raise CoastFrictionError("non-monotonic")
        disp = math.sqrt(
            sum((current.position[i] - previous.position[i]) ** 2 for i in range(3))
        )
        out.append((current, disp / dt))
    return out


def analyze_coast_attempt(
    *,
    attempt: int,
    hold: Sequence[CoastSample],
    release: Sequence[CoastSample],
    frequency: int,
) -> CoastAttemptMetrics:
    """Accept when release speed falls below half of hold steady cruise."""

    if attempt not in (1, 2):
        raise CoastFrictionError("attempt must be 1 or 2")
    if len(hold) < 10 or len(release) < 10:
        raise CoastFrictionError("hold/release undersampled")

    hold_speeds = [s for _, s in path_speeds(hold, frequency) if s > 0.05]
    if len(hold_speeds) < 5:
        raise CoastFrictionError("hold has too few active edges")
    steady = statistics.median(hold_speeds[-max(5, len(hold_speeds) // 3) :])
    if steady <= 0:
        raise CoastFrictionError("hold steady speed not positive")

    release_rows = path_speeds(release, frequency)
    origin = release[0].tick
    half = 0.5 * steady
    half_tick: int | None = None
    for sample, speed in release_rows:
        if speed <= half:
            half_tick = sample.tick
            break
    if half_tick is None:
        raise CoastFrictionError("release did not fall to half of hold cruise")

    half_life_ms = (half_tick - origin) * 1000.0 / frequency
    if half_life_ms < 0 or half_life_ms > 30_000:
        raise CoastFrictionError("half-life outside accepted band")
    terminal = statistics.median([s for _, s in release_rows[-max(3, len(release_rows) // 4) :]])
    if not math.isfinite(terminal):
        raise CoastFrictionError("terminal speed not finite")

    return CoastAttemptMetrics(
        attempt=attempt,
        accepted=True,
        hold_steady_speed=steady,
        release_half_life_ms=half_life_ms,
        release_terminal_speed=terminal,
        sample_counts={"hold": len(hold), "release": len(release)},
    )


def materialize_coast_pair_envelope(
    first: CoastAttemptMetrics,
    second: CoastAttemptMetrics,
    *,
    relative_spread: float = 0.35,
) -> dict[str, object]:
    if not (first.accepted and second.accepted):
        raise CoastFrictionError("both attempts must be accepted")
    lives = sorted((first.release_half_life_ms, second.release_half_life_ms))
    mid = (lives[0] + lives[1]) / 2.0
    if mid <= 0:
        raise CoastFrictionError("pair mid half-life not positive")
    if (lives[1] - lives[0]) / mid > relative_spread:
        raise CoastFrictionError("pair half-lives not stable")
    pad = max(mid * 0.05, (lives[1] - lives[0]) / 2.0)
    return {
        "schemaVersion": "battleengine-coast-friction-response.v0-scaffold",
        "envelope": {
            "releaseHalfLifeMs": {
                "lower": lives[0] - pad,
                "upper": lives[1] + pad,
            }
        },
        "nonclaims": [
            "Scaffold envelope is not dual-accepted retail authority for Core.",
            "Source walk friction defaults are not Core authority.",
        ],
    }


def synthetic_coast_attempt(
    *,
    attempt: int,
    hold_speed: float = 3.0,
    half_life_ms: float = 200.0,
    frequency: int = 10_000_000,
) -> tuple[list[CoastSample], list[CoastSample]]:
    step = frequency // 100
    z = 0.0
    hold: list[CoastSample] = []
    for i in range(40):
        hold.append(CoastSample(tick=i * step, phase="hold", position=(0.0, 0.0, z)))
        z += hold_speed * 0.01
    release: list[CoastSample] = []
    speed = hold_speed
    decay = 0.5 ** (10.0 / half_life_ms)  # per 10 ms sample toward half-life
    for i in range(60):
        release.append(
            CoastSample(
                tick=(40 + i) * step,
                phase="release",
                position=(0.0, 0.0, z),
            )
        )
        z += speed * 0.01
        speed *= decay
    return hold, release
