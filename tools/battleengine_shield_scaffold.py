#!/usr/bin/env python3
"""Shield regen/drain scalar scaffold — pure analysis only."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence


class ShieldScaffoldError(ValueError):
    pass


@dataclass(frozen=True)
class ShieldSample:
    tick: int
    shield: float


@dataclass(frozen=True)
class ShieldRateMetrics:
    attempt: int
    accepted: bool
    steady_rate_per_sec: float
    sample_count: int


def shield_rates(samples: Sequence[ShieldSample], frequency: int) -> list[float]:
    if frequency <= 0:
        raise ShieldScaffoldError("frequency must be positive")
    if len(samples) < 2:
        raise ShieldScaffoldError("undersampled")
    rates: list[float] = []
    for a, b in zip(samples, samples[1:]):
        dt = (b.tick - a.tick) / frequency
        if dt <= 0:
            raise ShieldScaffoldError("non-monotonic")
        rates.append((b.shield - a.shield) / dt)
    return rates


def analyze_shield_rate(
    *,
    attempt: int,
    samples: Sequence[ShieldSample],
    frequency: int,
    expect_positive: bool = True,
) -> ShieldRateMetrics:
    if attempt not in (1, 2):
        raise ShieldScaffoldError("attempt must be 1 or 2")
    rates = [r for r in shield_rates(samples, frequency) if abs(r) > 1e-6]
    if len(rates) < 5:
        raise ShieldScaffoldError("too few active shield edges")
    steady = statistics.median(rates[-max(5, len(rates) // 3) :])
    if expect_positive and steady <= 0:
        raise ShieldScaffoldError("expected positive regen rate")
    if not expect_positive and steady >= 0:
        raise ShieldScaffoldError("expected negative drain rate")
    if not math.isfinite(steady):
        raise ShieldScaffoldError("non-finite rate")
    return ShieldRateMetrics(
        attempt=attempt,
        accepted=True,
        steady_rate_per_sec=steady,
        sample_count=len(samples),
    )


def synthetic_shield_series(
    *,
    start: float = 50.0,
    rate_per_sec: float = 2.0,
    n: int = 40,
    frequency: int = 10_000_000,
) -> list[ShieldSample]:
    step = frequency // 100
    s = start
    out: list[ShieldSample] = []
    for i in range(n):
        out.append(ShieldSample(tick=i * step, shield=s))
        s += rate_per_sec * 0.01
    return out
