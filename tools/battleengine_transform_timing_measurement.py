#!/usr/bin/env python3
"""Transform morph timing harness (walker state → jet state).

Offline-analyzable latency from a sequence of state samples. Live dual-accept
is separate; this module is the durable analysis entry point.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence

WALKER_STATE = 2
JET_STATE = 3
TRANSFORMING_STATE = 1  # observed mid-morph in jet path


class TransformTimingError(ValueError):
    pass


@dataclass(frozen=True)
class StateSample:
    tick: int
    state_raw: int


@dataclass(frozen=True)
class TransformTimingMetrics:
    attempt: int
    accepted: bool
    morph_latency_ms: tuple[int, int]
    jet_settle_sample_count: int
    states_seen: list[int]


def analyze_transform_timing(
    *,
    attempt: int,
    samples: Sequence[StateSample],
    frequency: int,
    morph_request_tick: int,
) -> TransformTimingMetrics:
    """Accept when jet state is sustained after a morph request tick."""

    if attempt not in (1, 2):
        raise TransformTimingError("attempt must be 1 or 2")
    if frequency <= 0:
        raise TransformTimingError("frequency must be positive")
    if len(samples) < 5:
        raise TransformTimingError("state series undersampled")
    if any(samples[i].tick > samples[i + 1].tick for i in range(len(samples) - 1)):
        raise TransformTimingError("sample time must be monotonic")

    seen = sorted({int(s.state_raw) for s in samples})
    consecutive = 0
    first_jet_tick: int | None = None
    settle_count = 0
    for sample in samples:
        if sample.tick < morph_request_tick:
            continue
        if sample.state_raw == JET_STATE:
            consecutive += 1
            if consecutive == 1:
                first_jet_tick = sample.tick
            if consecutive >= 5:
                settle_count = consecutive
                break
        else:
            consecutive = 0
            first_jet_tick = None
    if first_jet_tick is None or settle_count < 5:
        raise TransformTimingError("jet state was not sustained after morph request")

    lower = int(
        math.floor((first_jet_tick - morph_request_tick) * 1000.0 / frequency / 10) * 10
    )
    # Upper bound: tick when 5th consecutive jet sample was observed.
    fifth_tick = first_jet_tick
    count = 0
    for sample in samples:
        if sample.tick < first_jet_tick:
            continue
        if sample.state_raw == JET_STATE:
            count += 1
            if count >= 5:
                fifth_tick = sample.tick
                break
    upper = int(math.ceil((fifth_tick - morph_request_tick) * 1000.0 / frequency / 10) * 10)
    lower = max(0, lower)
    upper = max(lower, upper)
    if upper > 30_000:
        raise TransformTimingError("morph latency exceeds 30 s bound")
    return TransformTimingMetrics(
        attempt=attempt,
        accepted=True,
        morph_latency_ms=(lower, upper),
        jet_settle_sample_count=settle_count,
        states_seen=seen,
    )


def synthetic_transform_series(
    *,
    frequency: int = 10_000_000,
    morph_delay_ms: int = 200,
) -> tuple[list[StateSample], int]:
    step = max(1, round(frequency * 0.01))
    request = 100 * step
    samples: list[StateSample] = []
    # Pre-morph walker
    for i in range(20):
        samples.append(StateSample(tick=i * step, state_raw=WALKER_STATE))
    # Transition
    delay_steps = max(1, morph_delay_ms // 10)
    for i in range(delay_steps):
        samples.append(
            StateSample(tick=request + i * step, state_raw=TRANSFORMING_STATE)
        )
    for i in range(30):
        samples.append(
            StateSample(
                tick=request + (delay_steps + i) * step,
                state_raw=JET_STATE,
            )
        )
    return samples, request
