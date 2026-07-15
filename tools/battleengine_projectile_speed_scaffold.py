#!/usr/bin/env python3
"""Projectile speed scaffold — path speed of a tracked projectile entity."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence


class ProjectileScaffoldError(ValueError):
    pass


@dataclass(frozen=True)
class ProjectileSample:
    tick: int
    position: tuple[float, float, float]


@dataclass(frozen=True)
class ProjectileSpeedMetrics:
    attempt: int
    accepted: bool
    steady_speed: float
    sample_count: int


def path_speeds(samples: Sequence[ProjectileSample], frequency: int) -> list[float]:
    if frequency <= 0:
        raise ProjectileScaffoldError("frequency must be positive")
    if len(samples) < 2:
        raise ProjectileScaffoldError("undersampled")
    out: list[float] = []
    for a, b in zip(samples, samples[1:]):
        dt = (b.tick - a.tick) / frequency
        if dt <= 0:
            raise ProjectileScaffoldError("non-monotonic")
        d = math.sqrt(sum((b.position[i] - a.position[i]) ** 2 for i in range(3)))
        out.append(d / dt)
    return out


def analyze_projectile_speed(
    *,
    attempt: int,
    samples: Sequence[ProjectileSample],
    frequency: int,
) -> ProjectileSpeedMetrics:
    if attempt not in (1, 2):
        raise ProjectileScaffoldError("attempt must be 1 or 2")
    speeds = [s for s in path_speeds(samples, frequency) if s > 0.05]
    if len(speeds) < 5:
        raise ProjectileScaffoldError("too few active projectile edges")
    steady = statistics.median(speeds[-max(5, len(speeds) // 3) :])
    if steady <= 0:
        raise ProjectileScaffoldError("steady speed not positive")
    return ProjectileSpeedMetrics(
        attempt=attempt, accepted=True, steady_speed=steady, sample_count=len(samples)
    )


def synthetic_projectile_series(
    *,
    speed: float = 40.0,
    n: int = 30,
    frequency: int = 10_000_000,
) -> list[ProjectileSample]:
    step = frequency // 100
    z = 0.0
    out: list[ProjectileSample] = []
    for i in range(n):
        out.append(ProjectileSample(tick=i * step, position=(0.0, 0.0, z)))
        z += speed * 0.01
    return out


def materialize_projectile_pair_envelope(
    first: ProjectileSpeedMetrics,
    second: ProjectileSpeedMetrics,
    *,
    relative_spread: float = 0.20,
) -> dict[str, object]:
    if not (first.accepted and second.accepted):
        raise ProjectileScaffoldError("both attempts must be accepted")
    speeds = sorted((first.steady_speed, second.steady_speed))
    mid = (speeds[0] + speeds[1]) / 2.0
    if mid <= 0:
        raise ProjectileScaffoldError("pair mid speed not positive")
    if (speeds[1] - speeds[0]) / mid > relative_spread:
        raise ProjectileScaffoldError("pair projectile speeds not stable")
    pad = max(mid * 0.05, (speeds[1] - speeds[0]) / 2.0)
    return {
        "schemaVersion": "battleengine-projectile-speed-scalar-response.v0-scaffold",
        "envelope": {
            "steadyProjectileSpeed": {
                "lower": speeds[0] - pad,
                "upper": speeds[1] + pad,
            }
        },
        "nonclaims": [
            "Scaffold envelope is not dual-accepted retail authority for Core.",
            "Projectile entity tracking is required before live dual-accept.",
            "Source ProjectileSpeedPerTick is not Core authority from this scaffold alone.",
        ],
    }
