#!/usr/bin/env python3
"""Strict public-safe schema for two accepted walker trajectory attempts."""

from __future__ import annotations

import math
import re
from typing import Any, Mapping


PUBLIC_SCHEMA = "battleengine-walker-forward-scalar-response.v2"
PUBLIC_STATUS = "two-accepted-fresh-attempts"
PUBLIC_CLAIM = "scalar-walker-forward-motion-response"
PUBLIC_METRIC_UNITS = {
    "position": "retail-world-coordinate-unit",
    "speed": "retail-world-coordinate-units-per-second",
    "speedSlope": "retail-world-coordinate-units-per-second-squared",
    "latency": "milliseconds",
    "ratio": "unitless",
}
PUBLIC_NONCLAIMS = (
    "No actor-relative or camera-relative direction is measured.",
    "No grounded, terrain, turning, jet, morph, or parity behavior is claimed.",
    "Timing is bounded to the ten millisecond sampling cadence.",
    "No physical-distance or deterministic-Core coordinate conversion is established.",
    "No scalar, including a unitless ratio, authorizes deterministic-Core behavior.",
    "No conversion from QPC seconds or milliseconds to deterministic-Core ticks is established.",
    "Physics-update period and actor-velocity units are hypothesized from source and static evidence and inferred from position edges; they are not a proven retail tick identity.",
)


class SchemaError(ValueError):
    pass


ROOT_KEYS = {"schemaVersion", "status", "claim", "metricUnits", "sampling", "attempts", "envelope", "nonclaims"}
SAMPLING_KEYS = {"clock", "cadenceMs", "baselineMs", "holdMs", "releaseMs", "timingPrecisionMs"}
ATTEMPT_KEYS = {"attempt", "receiptSha256", "runDigest", "sampleCounts", "metrics", "integrity"}
COUNT_KEYS = {"baseline", "hold", "release"}
METRIC_KEYS = {
    "steadySpeed",
    "baselineB95Speed",
    "baselineEndpointDisplacement",
    "responseThreshold",
    "responseLatencyMs",
    "releaseLatencyMs",
    "steadySlope",
    "normalizedResponse",
    "velocityHoldToBaselineRatio",
}
INTEGRITY_KEYS = {"receiptRevalidated", "foregroundMaintained", "keyUpConfirmed", "cleanupConfirmed"}
ENVELOPE_KEYS = {"steadySpeed", "responseLatencyMs", "releaseLatencyMs", "normalizedResponse", "steadySlope"}
RANGE_KEYS = {"lower", "upper"}
NODE_KEYS = {"100ms", "200ms", "350ms", "500ms"}
FORBIDDEN_KEY_PARTS = (
    "path", "pid", "pointer", "hwnd", "modulebase", "rawsample", "log", "address", "processid"
)
PATH_LIKE = re.compile(r"[\\/]|file:", re.IGNORECASE)


def _exact(value: Any, expected: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise SchemaError(f"{label} must have exact keys {sorted(expected)}; found {actual}")
    return value


def _number(value: Any, label: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise SchemaError(f"{label} must be a finite JSON number")
    result = float(value)
    if minimum is not None and result < minimum:
        raise SchemaError(f"{label} must be at least {minimum}")
    return result


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise SchemaError(f"{label} must be an integer >= {minimum}")
    return value


def _digest(value: Any, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise SchemaError(f"{label} must be a lowercase SHA-256 digest")


def _range(value: Any, label: str, *, minimum: float = 0.0) -> tuple[float, float]:
    row = _exact(value, RANGE_KEYS, label)
    lower = _number(row["lower"], f"{label}.lower", minimum=minimum)
    upper = _number(row["upper"], f"{label}.upper", minimum=minimum)
    if lower > upper:
        raise SchemaError(f"{label} lower exceeds upper")
    return lower, upper


def _timing_range(value: Any, label: str, *, duration_ms: int) -> tuple[int, int]:
    lower, upper = _range(value, label)
    if not lower.is_integer() or not upper.is_integer() or int(lower) % 10 or int(upper) % 10:
        raise SchemaError(f"{label} must use the 10 ms sampling cadence")
    if upper > duration_ms:
        raise SchemaError(f"{label} exceeds the declared phase duration")
    return int(lower), int(upper)


def _require_exact_range(value: Any, expected: tuple[float, float], label: str) -> None:
    actual = _range(value, label, minimum=-math.inf)
    if actual != expected:
        raise SchemaError(f"{label} does not match the exact two-run envelope")


def _reject_private(value: Any, label: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            folded = str(key).replace("_", "").replace("-", "").lower()
            if any(part in folded for part in FORBIDDEN_KEY_PARTS):
                raise SchemaError(f"{label} contains forbidden private key {key!r}")
            _reject_private(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_private(child, f"{label}[{index}]")
    elif isinstance(value, str) and PATH_LIKE.search(value):
        raise SchemaError(f"{label} contains a path-like string")


def validate_public_projection(payload: Any) -> None:
    root = _exact(payload, ROOT_KEYS, "projection")
    if root["schemaVersion"] != PUBLIC_SCHEMA:
        raise SchemaError("projection schemaVersion mismatch")
    if root["status"] != PUBLIC_STATUS:
        raise SchemaError("projection status mismatch")
    if root["claim"] != PUBLIC_CLAIM:
        raise SchemaError("projection claim mismatch")
    if root["metricUnits"] != PUBLIC_METRIC_UNITS:
        raise SchemaError("metric units contract mismatch")

    sampling = _exact(root["sampling"], SAMPLING_KEYS, "sampling")
    expected_sampling = {
        "clock": "query-performance-counter",
        "cadenceMs": 10,
        "baselineMs": 500,
        "holdMs": 2000,
        "releaseMs": 750,
        "timingPrecisionMs": 10,
    }
    if sampling != expected_sampling:
        raise SchemaError("sampling contract mismatch")

    attempts = root["attempts"]
    if not isinstance(attempts, list) or len(attempts) != 2:
        raise SchemaError("projection requires exactly two attempts")
    receipts: set[str] = set()
    runs: set[str] = set()
    attempt_metrics: list[Mapping[str, Any]] = []
    for index, attempt_value in enumerate(attempts, start=1):
        attempt = _exact(attempt_value, ATTEMPT_KEYS, f"attempt[{index}]")
        if attempt["attempt"] != index:
            raise SchemaError("attempt order must be 1 then 2")
        _digest(attempt["receiptSha256"], "receiptSha256")
        _digest(attempt["runDigest"], "runDigest")
        receipts.add(attempt["receiptSha256"])
        runs.add(attempt["runDigest"])
        counts = _exact(attempt["sampleCounts"], COUNT_KEYS, "sampleCounts")
        for phase, minimum, maximum in (
            ("baseline", 48, 50), ("hold", 192, 200), ("release", 72, 75)
        ):
            count = _integer(counts[phase], f"sampleCounts.{phase}", minimum=minimum)
            if count > maximum:
                raise SchemaError(f"sampleCounts.{phase} count exceeds its phase target")
        metrics = _exact(attempt["metrics"], METRIC_KEYS, "metrics")
        for key in (
            "steadySpeed", "baselineB95Speed", "baselineEndpointDisplacement",
            "responseThreshold", "velocityHoldToBaselineRatio",
        ):
            _number(metrics[key], f"metrics.{key}", minimum=0.0)
        steady = _number(metrics["steadySpeed"], "metrics.steadySpeed", minimum=0.0)
        b95 = _number(metrics["baselineB95Speed"], "metrics.baselineB95Speed", minimum=0.0)
        endpoint = _number(
            metrics["baselineEndpointDisplacement"],
            "metrics.baselineEndpointDisplacement",
            minimum=0.0,
        )
        threshold = _number(metrics["responseThreshold"], "metrics.responseThreshold", minimum=0.0)
        slope = _number(metrics["steadySlope"], "metrics.steadySlope")
        ratio = _number(
            metrics["velocityHoldToBaselineRatio"],
            "metrics.velocityHoldToBaselineRatio",
            minimum=0.0,
        )
        if steady <= 0 or b95 > 0.05 * steady or endpoint > 0.025 * steady:
            raise SchemaError("metrics baseline drift contract mismatch")
        if not math.isclose(threshold, max(5 * b95, 0.10 * steady), rel_tol=0.0, abs_tol=1e-12):
            raise SchemaError("metrics response threshold contract mismatch")
        if abs(slope) > 0.10 * steady or ratio <= 5.0:
            raise SchemaError("metrics steady or velocity contract mismatch")
        _timing_range(metrics["responseLatencyMs"], "metrics.responseLatencyMs", duration_ms=750)
        _timing_range(metrics["releaseLatencyMs"], "metrics.releaseLatencyMs", duration_ms=750)
        nodes = _exact(metrics["normalizedResponse"], NODE_KEYS, "metrics.normalizedResponse")
        for key, value in nodes.items():
            _number(value, f"metrics.normalizedResponse.{key}", minimum=0.0)
        integrity = _exact(attempt["integrity"], INTEGRITY_KEYS, "integrity")
        if any(value is not True for value in integrity.values()):
            raise SchemaError("all integrity flags must be true")
        attempt_metrics.append(metrics)
    if len(receipts) != 2 or len(runs) != 2:
        raise SchemaError("attempt identities must be fresh and distinct")

    first, second = attempt_metrics
    first_steady = float(first["steadySpeed"])
    second_steady = float(second["steadySpeed"])
    relative_speed = abs(first_steady - second_steady) / min(first_steady, second_steady)
    first_response = _timing_range(first["responseLatencyMs"], "first response", duration_ms=750)
    second_response = _timing_range(second["responseLatencyMs"], "second response", duration_ms=750)
    first_release = _timing_range(first["releaseLatencyMs"], "first release", duration_ms=750)
    second_release = _timing_range(second["releaseLatencyMs"], "second release", duration_ms=750)
    response_union = max(first_response[1], second_response[1]) - min(first_response[0], second_response[0])
    release_union = max(first_release[1], second_release[1]) - min(first_release[0], second_release[0])
    first_nodes = first["normalizedResponse"]
    second_nodes = second["normalizedResponse"]
    node_delta = max(abs(float(first_nodes[key]) - float(second_nodes[key])) for key in NODE_KEYS)
    if relative_speed > 0.10 or response_union > 30 or release_union > 50 or node_delta > 0.10:
        raise SchemaError("attempts do not satisfy the exact two-run tolerance")

    envelope = _exact(root["envelope"], ENVELOPE_KEYS, "envelope")
    _require_exact_range(
        envelope["steadySpeed"],
        (round(0.95 * min(first_steady, second_steady), 12), round(1.05 * max(first_steady, second_steady), 12)),
        "envelope.steadySpeed",
    )
    _require_exact_range(
        envelope["responseLatencyMs"],
        (min(first_response[0], second_response[0]), max(first_response[1], second_response[1])),
        "envelope.responseLatencyMs",
    )
    _require_exact_range(
        envelope["releaseLatencyMs"],
        (min(first_release[0], second_release[0]), max(first_release[1], second_release[1])),
        "envelope.releaseLatencyMs",
    )
    _require_exact_range(
        envelope["steadySlope"],
        (
            min(float(first["steadySlope"]), float(second["steadySlope"])) - 0.02,
            max(float(first["steadySlope"]), float(second["steadySlope"])) + 0.02,
        ),
        "envelope.steadySlope",
    )
    nodes = _exact(envelope["normalizedResponse"], NODE_KEYS, "envelope.normalizedResponse")
    for key, value in nodes.items():
        _require_exact_range(
            value,
            (
                max(0.0, min(float(first_nodes[key]), float(second_nodes[key])) - 0.05),
                max(float(first_nodes[key]), float(second_nodes[key])) + 0.05,
            ),
            f"envelope.normalizedResponse.{key}",
        )

    _reject_private(root)
    nonclaims = root["nonclaims"]
    if nonclaims != list(PUBLIC_NONCLAIMS):
        raise SchemaError("nonclaims must match the exact bounded canonical list")
