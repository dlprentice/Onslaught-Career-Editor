#!/usr/bin/env python3
"""Energy drain/regen scalar scaffold — pure analysis only."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence

# Steam-static hypothesis (see energy-rate-scalar-measurement-plan.md).
BATTLE_ENGINE_ENERGY_OFFSET = 0xFC
BATTLE_ENGINE_SHIELDS_OFFSET = 0x100


class EnergyScaffoldError(ValueError):
    pass


@dataclass(frozen=True)
class EnergySample:
    tick: int
    energy: float


@dataclass(frozen=True)
class EnergyRateMetrics:
    attempt: int
    accepted: bool
    steady_rate_per_sec: float
    sample_count: int


def energy_rates(samples: Sequence[EnergySample], frequency: int) -> list[float]:
    if frequency <= 0:
        raise EnergyScaffoldError("frequency must be positive")
    if len(samples) < 2:
        raise EnergyScaffoldError("undersampled")
    rates: list[float] = []
    for a, b in zip(samples, samples[1:]):
        dt = (b.tick - a.tick) / frequency
        if dt <= 0:
            raise EnergyScaffoldError("non-monotonic")
        rates.append((b.energy - a.energy) / dt)
    return rates


def analyze_energy_rate(
    *,
    attempt: int,
    samples: Sequence[EnergySample],
    frequency: int,
    expect_negative: bool,
) -> EnergyRateMetrics:
    if attempt not in (1, 2):
        raise EnergyScaffoldError("attempt must be 1 or 2")
    rates = energy_rates(samples, frequency)
    active = [r for r in rates if abs(r) > 1e-6]
    if len(active) < 5:
        raise EnergyScaffoldError("too few active energy edges")
    steady = statistics.median(active[-max(5, len(active) // 3) :])
    if expect_negative and steady >= 0:
        raise EnergyScaffoldError("expected drain (negative rate)")
    if not expect_negative and steady <= 0:
        raise EnergyScaffoldError("expected regen (positive rate)")
    if not math.isfinite(steady):
        raise EnergyScaffoldError("non-finite rate")
    return EnergyRateMetrics(
        attempt=attempt,
        accepted=True,
        steady_rate_per_sec=steady,
        sample_count=len(samples),
    )


def synthetic_energy_series(
    *,
    start: float = 100.0,
    rate_per_sec: float = -3.0,
    n: int = 40,
    frequency: int = 10_000_000,
) -> list[EnergySample]:
    step = frequency // 100
    out: list[EnergySample] = []
    e = start
    for i in range(n):
        out.append(EnergySample(tick=i * step, energy=e))
        e += rate_per_sec * 0.01
    return out


def materialize_energy_pair_envelope(
    first: EnergyRateMetrics,
    second: EnergyRateMetrics,
    *,
    relative_spread: float = 0.20,
) -> dict[str, object]:
    """Build a provisional public envelope from two accepted attempts."""

    if not (first.accepted and second.accepted):
        raise EnergyScaffoldError("both attempts must be accepted")
    rates = sorted((first.steady_rate_per_sec, second.steady_rate_per_sec))
    mid = (rates[0] + rates[1]) / 2.0
    if mid == 0:
        raise EnergyScaffoldError("pair mid rate is zero")
    if abs(rates[1] - rates[0]) / abs(mid) > relative_spread:
        raise EnergyScaffoldError("pair energy rates not stable")
    pad = max(abs(mid) * 0.05, abs(rates[1] - rates[0]) / 2.0)
    lower, upper = rates[0] - pad, rates[1] + pad
    if lower > upper:
        lower, upper = upper, lower
    return {
        "schemaVersion": "battleengine-energy-rate-scalar-response.v0-scaffold",
        "envelope": {
            "steadyEnergyRatePerSec": {
                "lower": lower,
                "upper": upper,
            }
        },
        "offsetHypothesis": {
            "battleEngineEnergy": hex(BATTLE_ENGINE_ENERGY_OFFSET),
            "battleEngineShields": hex(BATTLE_ENGINE_SHIELDS_OFFSET),
        },
        "nonclaims": [
            "Scaffold envelope is not dual-accepted retail authority for Core.",
            "Offsets are steam-static hypotheses until live dual-accept.",
            "Source energy defaults are not Core authority.",
        ],
    }
