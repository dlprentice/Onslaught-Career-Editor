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
    energy: float


@dataclass(frozen=True)
class ShieldRateMetrics:
    attempt: int
    accepted: bool
    steady_rate_per_sec: float
    steady_energy_rate_per_sec: float
    paired_active_edge_fraction: float
    relative_rate_delta: float
    sample_count: int


def _paired_rates(
    samples: Sequence[ShieldSample], frequency: int
) -> list[tuple[float, float]]:
    if frequency <= 0:
        raise ShieldScaffoldError("frequency must be positive")
    if len(samples) < 2:
        raise ShieldScaffoldError("undersampled")
    if any(
        not math.isfinite(float(value))
        for sample in samples
        for value in (sample.shield, sample.energy)
    ):
        raise ShieldScaffoldError("shield and energy samples must be finite")
    rates: list[tuple[float, float]] = []
    for a, b in zip(samples, samples[1:]):
        dt = (b.tick - a.tick) / frequency
        if dt <= 0:
            raise ShieldScaffoldError("non-monotonic")
        rates.append(
            (
                (b.shield - a.shield) / dt,
                (b.energy - a.energy) / dt,
            )
        )
    return rates


def shield_rates(samples: Sequence[ShieldSample], frequency: int) -> list[float]:
    return [shield_rate for shield_rate, _energy_rate in _paired_rates(samples, frequency)]


def analyze_shield_rate(
    *,
    attempt: int,
    samples: Sequence[ShieldSample],
    frequency: int,
    expect_positive: bool = True,
) -> ShieldRateMetrics:
    if attempt not in (1, 2):
        raise ShieldScaffoldError("attempt must be 1 or 2")
    active = [pair for pair in _paired_rates(samples, frequency) if abs(pair[0]) > 1e-6]
    if len(active) < 5:
        raise ShieldScaffoldError("too few active shield edges")
    steady = statistics.median(
        pair[0] for pair in active[-max(5, len(active) // 3) :]
    )
    if expect_positive and steady <= 0:
        raise ShieldScaffoldError("expected positive regen rate")
    if not expect_positive and steady >= 0:
        raise ShieldScaffoldError("expected negative drain rate")
    opposite = [pair for pair in active if pair[0] * pair[1] < 0]
    if len(opposite) / len(active) > 0.20:
        raise ShieldScaffoldError("energy moved in the opposite direction from shields")
    paired = [
        pair
        for pair in active
        if (pair[1] > 1e-6 if expect_positive else pair[1] < -1e-6)
    ]
    paired_fraction = len(paired) / len(active)
    if paired_fraction < 0.80:
        raise ShieldScaffoldError("energy did not track enough active shield edges")
    steady_pairs = paired[-max(5, len(paired) // 3) :]
    steady_energy = statistics.median(pair[1] for pair in steady_pairs)
    if not math.isfinite(steady):
        raise ShieldScaffoldError("non-finite rate")
    rate_mid = (abs(steady) + abs(steady_energy)) / 2.0
    relative_rate_delta = abs(steady - steady_energy) / max(rate_mid, 1e-12)
    if relative_rate_delta > 0.25:
        raise ShieldScaffoldError("energy/shield steady-rate correlation exceeded tolerance")
    return ShieldRateMetrics(
        attempt=attempt,
        accepted=True,
        steady_rate_per_sec=steady,
        steady_energy_rate_per_sec=steady_energy,
        paired_active_edge_fraction=paired_fraction,
        relative_rate_delta=relative_rate_delta,
        sample_count=len(samples),
    )


def synthetic_shield_series(
    *,
    start: float = 50.0,
    rate_per_sec: float = 2.0,
    energy_start: float | None = None,
    energy_rate_per_sec: float | None = None,
    n: int = 40,
    frequency: int = 10_000_000,
) -> list[ShieldSample]:
    step = frequency // 100
    s = start
    e = start if energy_start is None else energy_start
    e_rate = rate_per_sec if energy_rate_per_sec is None else energy_rate_per_sec
    out: list[ShieldSample] = []
    for i in range(n):
        out.append(ShieldSample(tick=i * step, shield=s, energy=e))
        s += rate_per_sec * 0.01
        e += e_rate * 0.01
    return out


# Steam-static hypothesis (paired with energy scaffold).
BATTLE_ENGINE_SHIELDS_OFFSET = 0x100
BATTLE_ENGINE_ENERGY_OFFSET = 0xFC


def materialize_shield_pair_envelope(
    first: ShieldRateMetrics,
    second: ShieldRateMetrics,
    *,
    relative_spread: float = 0.25,
) -> dict[str, object]:
    if not (first.accepted and second.accepted):
        raise ShieldScaffoldError("both attempts must be accepted")
    rates = sorted((first.steady_rate_per_sec, second.steady_rate_per_sec))
    mid = (rates[0] + rates[1]) / 2.0
    if mid == 0:
        raise ShieldScaffoldError("pair mid rate is zero")
    if abs(rates[1] - rates[0]) / abs(mid) > relative_spread:
        raise ShieldScaffoldError("pair shield rates not stable")
    pad = max(abs(mid) * 0.05, abs(rates[1] - rates[0]) / 2.0)
    energy_rates = sorted(
        (first.steady_energy_rate_per_sec, second.steady_energy_rate_per_sec)
    )
    energy_mid = (energy_rates[0] + energy_rates[1]) / 2.0
    if energy_mid == 0:
        raise ShieldScaffoldError("pair energy mid rate is zero")
    if abs(energy_rates[1] - energy_rates[0]) / abs(energy_mid) > relative_spread:
        raise ShieldScaffoldError("pair energy rates not stable")
    energy_pad = max(
        abs(energy_mid) * 0.05,
        abs(energy_rates[1] - energy_rates[0]) / 2.0,
    )
    return {
        "schemaVersion": "battleengine-shield-rate-scalar-response.v0-scaffold",
        "envelope": {
            "steadyShieldRatePerSec": {
                "lower": rates[0] - pad,
                "upper": rates[1] + pad,
            },
            "steadyEnergyRatePerSec": {
                "lower": energy_rates[0] - energy_pad,
                "upper": energy_rates[1] + energy_pad,
            },
            "pairedActiveEdgeFraction": {
                "lower": min(
                    first.paired_active_edge_fraction,
                    second.paired_active_edge_fraction,
                ),
                "upper": 1.0,
            },
            "rateRelativeDelta": {
                "lower": 0.0,
                "upper": max(first.relative_rate_delta, second.relative_rate_delta),
            },
        },
        "offsetHypothesis": {
            "battleEngineShields": hex(BATTLE_ENGINE_SHIELDS_OFFSET),
            "battleEngineEnergy": hex(BATTLE_ENGINE_ENERGY_OFFSET),
        },
        "nonclaims": [
            "Scaffold envelope is not dual-accepted retail authority for Core.",
            "Offsets are steam-static hypotheses until live dual-accept.",
        ],
    }
