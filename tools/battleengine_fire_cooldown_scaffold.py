#!/usr/bin/env python3
"""Fire / projectile scalar scaffold (M2.1) — analysis only, no Core authority.

Defines the measurement contract shape and pure timing helpers so a live
dual-accept path can plug in later without inventing Core from source defaults.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


class FireScaffoldError(ValueError):
    pass


@dataclass(frozen=True)
class FireEvent:
    """One observed fire edge (tick when projectile spawn or energy drop proved)."""

    tick: int
    label: str


@dataclass(frozen=True)
class FireCooldownMetrics:
    attempt: int
    accepted: bool
    inter_fire_ms: list[float]
    median_cooldown_ms: float
    event_count: int


def inter_fire_intervals_ms(
    events: Sequence[FireEvent],
    frequency: int,
) -> list[float]:
    if frequency <= 0:
        raise FireScaffoldError("frequency must be positive")
    if len(events) < 2:
        raise FireScaffoldError("need at least two fire events")
    ordered = sorted(events, key=lambda e: e.tick)
    out: list[float] = []
    for previous, current in zip(ordered, ordered[1:]):
        if current.tick <= previous.tick:
            raise FireScaffoldError("fire events must be strictly increasing")
        out.append((current.tick - previous.tick) * 1000.0 / frequency)
    return out


def analyze_fire_cooldown(
    *,
    attempt: int,
    events: Sequence[FireEvent],
    frequency: int,
    min_events: int = 3,
) -> FireCooldownMetrics:
    if attempt not in (1, 2):
        raise FireScaffoldError("attempt must be 1 or 2")
    if len(events) < min_events:
        raise FireScaffoldError(f"need at least {min_events} fire events")
    intervals = inter_fire_intervals_ms(events, frequency)
    if any(not math.isfinite(x) or x <= 0 for x in intervals):
        raise FireScaffoldError("intervals must be positive finite ms")
    ordered = sorted(intervals)
    mid = ordered[len(ordered) // 2]
    # Reject absurd cadence (faster than 1 ms or slower than 10 s median).
    if mid < 1.0 or mid > 10_000.0:
        raise FireScaffoldError("median cooldown outside accepted band")
    return FireCooldownMetrics(
        attempt=attempt,
        accepted=True,
        inter_fire_ms=intervals,
        median_cooldown_ms=mid,
        event_count=len(events),
    )


def synthetic_fire_events(
    *,
    count: int = 5,
    cooldown_ms: float = 200.0,
    frequency: int = 10_000_000,
) -> list[FireEvent]:
    step = max(1, int(round(frequency * cooldown_ms / 1000.0)))
    return [FireEvent(tick=i * step, label=f"fire-{i}") for i in range(count)]
