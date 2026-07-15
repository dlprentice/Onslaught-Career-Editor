#!/usr/bin/env python3
"""Regression checker for landed public scalar motion contracts.

Drives real tracked JSON contracts and fails if missing, schema-broken, or
envelope-incoherent. No live BEA.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MECH = ROOT / "reverse-engineering" / "game-mechanics"
CONTRACTS = (
    MECH / "walker-forward-scalar-response-v2.json",
    MECH / "jet-forward-scalar-response-v1.json",
    MECH / "walker-turn-yaw-scalar-response-v1.json",
    MECH / "walker-strafe-lateral-scalar-response-v1.json",
    MECH / "walker-transform-morph-timing-v1.json",
    MECH / "jet-energy-drain-scalar-response-v1.json",
)


class ContractRegressionError(ValueError):
    pass


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ContractRegressionError(f"{label} must be an object")
    return value


def _require_finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ContractRegressionError(f"{label} must be a finite number")
    return float(value)


def _require_range(value: Any, label: str) -> tuple[float, float]:
    row = _require_mapping(value, label)
    if set(row) != {"lower", "upper"}:
        raise ContractRegressionError(f"{label} must have lower/upper only")
    lower = _require_finite(row["lower"], f"{label}.lower")
    upper = _require_finite(row["upper"], f"{label}.upper")
    if lower > upper:
        raise ContractRegressionError(f"{label} lower exceeds upper")
    return lower, upper


def _steady_key(envelope: Mapping[str, Any], metrics: Mapping[str, Any]) -> tuple[str, str]:
    """Return (envelope_key, metrics_key) for the steady scalar of this contract."""

    if "steadySpeed" in envelope and "steadySpeed" in metrics:
        return "steadySpeed", "steadySpeed"
    if "steadyYawRateRadPerSec" in envelope and "steadyYawRateRadPerSec" in metrics:
        return "steadyYawRateRadPerSec", "steadyYawRateRadPerSec"
    if "steadyLateralSpeed" in envelope and "steadyLateralSpeed" in metrics:
        return "steadyLateralSpeed", "steadyLateralSpeed"
    if "steadyEnergyRatePerSec" in envelope and "steadyEnergyRatePerSec" in metrics:
        return "steadyEnergyRatePerSec", "steadyEnergyRatePerSec"
    raise ContractRegressionError("unsupported steady metric shape")


def _validate_latency_pair_contract(path: Path, root: Mapping[str, Any]) -> dict[str, object]:
    """Transform-style contracts: envelope.morphLatencyMs + attempt morphLatencyMs."""

    envelope = _require_mapping(root["envelope"], "envelope")
    if "morphLatencyMs" not in envelope:
        raise ContractRegressionError(f"{path.name} missing envelope.morphLatencyMs")
    env_lo, env_hi = _require_range(envelope["morphLatencyMs"], "envelope.morphLatencyMs")
    attempts = root["attempts"]
    mids: list[float] = []
    for index, attempt in enumerate(attempts, start=1):
        row = _require_mapping(attempt, f"attempt[{index}]")
        metrics = _require_mapping(row.get("metrics"), f"attempt[{index}].metrics")
        lo, hi = _require_range(metrics.get("morphLatencyMs"), f"attempt[{index}].morphLatencyMs")
        if lo < env_lo * 0.99 or hi > env_hi * 1.01:
            raise ContractRegressionError(
                f"{path.name} attempt latency [{lo},{hi}] outside envelope [{env_lo},{env_hi}]"
            )
        mids.append((lo + hi) / 2.0)
    relative = abs(mids[0] - mids[1]) / min(mids)
    if relative > 0.25:
        raise ContractRegressionError(f"{path.name} morph mid relative delta {relative:.4f} too large")
    nonclaims = root["nonclaims"]
    if not isinstance(nonclaims, list) or not nonclaims:
        raise ContractRegressionError(f"{path.name} nonclaims must be a non-empty list")
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "schemaVersion": root["schemaVersion"],
        "steadyValues": mids,
        "envelope": {"lower": env_lo, "upper": env_hi, "key": "morphLatencyMs"},
        "relativeDelta": relative,
    }


def validate_landed_scalar_contract(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ContractRegressionError(f"missing contract: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    root = _require_mapping(payload, str(path))
    for key in ("schemaVersion", "status", "claim", "attempts", "envelope", "nonclaims"):
        if key not in root:
            raise ContractRegressionError(f"{path.name} missing {key}")
    if root["status"] != "two-accepted-fresh-attempts":
        raise ContractRegressionError(f"{path.name} status is not dual-accept")
    attempts = root["attempts"]
    if not isinstance(attempts, list) or len(attempts) != 2:
        raise ContractRegressionError(f"{path.name} must have exactly two attempts")
    envelope = _require_mapping(root["envelope"], "envelope")
    if "morphLatencyMs" in envelope:
        return _validate_latency_pair_contract(path, root)
    # Probe first metrics for shape.
    first_metrics = _require_mapping(attempts[0].get("metrics"), "attempt[1].metrics")
    env_key, met_key = _steady_key(envelope, first_metrics)
    lower, upper = _require_range(envelope.get(env_key), f"envelope.{env_key}")
    energy_drain = env_key == "steadyEnergyRatePerSec"
    values: list[float] = []
    for index, attempt in enumerate(attempts, start=1):
        row = _require_mapping(attempt, f"attempt[{index}]")
        metrics = _require_mapping(row.get("metrics"), f"attempt[{index}].metrics")
        speed = _require_finite(metrics.get(met_key), f"attempt[{index}].{met_key}")
        if energy_drain:
            if speed >= 0:
                raise ContractRegressionError(
                    f"attempt[{index}] {met_key} must be negative drain"
                )
        elif speed <= 0:
            raise ContractRegressionError(f"attempt[{index}] {met_key} must be positive")
        values.append(speed)
        if speed < lower * 0.99 or speed > upper * 1.01:
            raise ContractRegressionError(
                f"{path.name} attempt {met_key} {speed} outside envelope [{lower}, {upper}]"
            )
        # Latency object if present (forward/jet/strafe/turn all have some form).
        for lat_key in ("responseLatencyMs",):
            if lat_key in metrics:
                _require_range(metrics[lat_key], f"attempt[{index}].{lat_key}")
    magnitudes = [abs(v) for v in values]
    relative = abs(magnitudes[0] - magnitudes[1]) / min(magnitudes)
    if relative > 0.12:
        raise ContractRegressionError(
            f"{path.name} pair relative delta {relative:.4f} too large"
        )
    nonclaims = root["nonclaims"]
    if not isinstance(nonclaims, list) or not nonclaims:
        raise ContractRegressionError(f"{path.name} nonclaims must be a non-empty list")
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "schemaVersion": root["schemaVersion"],
        "steadyValues": values,
        "envelope": {"lower": lower, "upper": upper, "key": env_key},
        "relativeDelta": relative,
    }


def validate_all_landed_contracts(
    paths: Sequence[Path] | None = None,
) -> list[dict[str, object]]:
    selected = list(paths) if paths is not None else list(CONTRACTS)
    return [validate_landed_scalar_contract(path) for path in selected]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--contract", action="append", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        reports = validate_all_landed_contracts(args.contract)
    except ContractRegressionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"passed": True, "contracts": reports}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
