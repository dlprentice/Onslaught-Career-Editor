#!/usr/bin/env python3
"""Validate a bounded walker recharge retail candidate bridge.

This probe checks Stuart-source walker recharge anchors against a fresh ignored
Ghidra decompile export for the retail surface-alignment helper plus a private
read-only constant scan. The result is intentionally partial: it supports a
retail candidate cluster, not exact source method identity or runtime proof.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references" / "Onslaught" / "BattleEngineWalkerPart.cpp"
DEFAULT_DECOMPILE = ROOT / "subagents" / "battleengine-walker-recharge-candidate" / "current" / "decompile"
DEFAULT_CONSTANTS = ROOT / "subagents" / "battleengine-walker-recharge-candidate" / "current" / "constants.json"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-walker-recharge-candidate" / "current" / "walker-recharge-candidate.json"

SOURCE_TOKENS = (
    "if (EVENT_MANAGER.GetTime()-mMainPart->mLastTimeOnGround<0.3f)",
    "if ((!mMainPart->mInfinateEnergy) && (!mMainPart->mCloaked))",
    "float\trecharge=mMainPart->mConfiguration->mGroundEnergyIncrease;",
    "if (!mShieldsRecharging)",
    "recharge/=2;",
    "mMainPart->mEnergy+=recharge;",
    "if (mMainPart->mEnergy>mMainPart->mConfiguration->mEnergy)",
    "mMainPart->mShields=mMainPart->mEnergy;",
)

DECOMPILE_TOKENS = (
    "DAT_00672fd0 - *(float *)(iVar6 + 0xcc) < _DAT_005d8cb4",
    "*(int *)(iVar6 + 0x160) == 0",
    "*(int *)(iVar6 + 0x4ac) == 0",
    "fVar3 = *(float *)(*(int *)(iVar6 + 0x4b0) + 0x28)",
    "if (*(int *)((int)param_1 + 0x14) == 0)",
    "fVar3 = fVar3 * _DAT_005d85ec",
    "*(float *)(iVar6 + 0xfc) = fVar3 + *(float *)(iVar6 + 0xfc)",
    "*(float *)(*(int *)(iVar6 + 0x4b0) + 0x20) < *(float *)(iVar6 + 0xfc)",
    "*(undefined4 *)(iVar6 + 0xfc) = *(undefined4 *)(*(int *)(iVar6 + 0x4b0) + 0x20)",
    "*(undefined4 *)((int)param_1 + 0x14) = 1",
    "*(undefined4 *)(*(int *)((int)param_1 + 0x20) + 0x100)",
    "*(undefined4 *)(*(int *)((int)param_1 + 0x20) + 0xfc)",
)

EXPECTED_CONSTANTS = {
    "half_recharge_multiplier": ("0x005d85ec", 0.5),
    "ground_recent_window": ("0x005d8cb4", 0.3),
}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalized(text: str) -> str:
    return "".join(text.split())


def token_hits(path: Path, tokens: tuple[str, ...], *, normalize: bool = False) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    hits: dict[str, list[int]] = {}
    if normalize:
        norm_lines = [normalized(line) for line in lines]
        for token in tokens:
            needle = normalized(token)
            hits[token] = [index + 1 for index, line in enumerate(norm_lines) if needle in line]
    else:
        for token in tokens:
            hits[token] = [index + 1 for index, line in enumerate(lines) if token in line]
    return hits


def read_index(decompile_dir: Path) -> list[dict[str, str]]:
    index = decompile_dir / "index.tsv"
    if not index.is_file():
        return []
    with index.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def find_decompile(decompile_dir: Path) -> Path:
    candidates = sorted(decompile_dir.glob("00413760_CMonitor__ProcessTrackingAndSurfaceAlignment.c"))
    return candidates[0] if candidates else decompile_dir / "00413760_CMonitor__ProcessTrackingAndSurfaceAlignment.c"


def load_constants(path: Path) -> dict[str, dict[str, object]]:
    if not path.is_file():
        return {}
    report = json.loads(path.read_text(encoding="utf-8"))
    return {item["name"]: item for item in report.get("values", [])}


def first_hit(hits: dict[str, list[int]], token: str) -> int | None:
    lines = hits.get(token, [])
    return lines[0] if lines else None


def build_report(decompile_dir: Path, constants_path: Path) -> dict[str, object]:
    decompile = find_decompile(decompile_dir)
    index_rows = read_index(decompile_dir)
    source_hits = token_hits(SOURCE, SOURCE_TOKENS, normalize=True)
    decompile_hits = token_hits(decompile, DECOMPILE_TOKENS, normalize=True)
    constants = load_constants(constants_path)

    failures: list[str] = []
    if not SOURCE.is_file():
        failures.append(f"missing source file: {relative(SOURCE)}")
    if not decompile.is_file():
        failures.append(f"missing decompile file: {relative(decompile)}")
    if not index_rows:
        failures.append(f"missing or empty decompile index: {relative(decompile_dir / 'index.tsv')}")
    else:
        ok_rows = [
            row
            for row in index_rows
            if row.get("address", "").lower() == "0x00413760"
            and row.get("name") == "CMonitor__ProcessTrackingAndSurfaceAlignment"
            and row.get("status") == "OK"
        ]
        if not ok_rows:
            failures.append("decompile index lacks OK row for 0x00413760 CMonitor__ProcessTrackingAndSurfaceAlignment")
    failures.extend(f"missing source token: {token}" for token, lines in source_hits.items() if not lines)
    failures.extend(f"missing decompile token: {token}" for token, lines in decompile_hits.items() if not lines)
    for name, (expected_va, expected_float) in EXPECTED_CONSTANTS.items():
        item = constants.get(name)
        if not item:
            failures.append(f"missing constant: {name}")
            continue
        actual_va = str(item.get("va", "")).lower()
        actual_float = float(item.get("float", math.nan))
        if actual_va != expected_va:
            failures.append(f"{name} VA mismatch: expected {expected_va}, got {actual_va}")
        if not math.isfinite(actual_float) or abs(actual_float - expected_float) > 0.00001:
            failures.append(f"{name} float mismatch: expected {expected_float}, got {actual_float}")

    time_gate_line = first_hit(decompile_hits, "DAT_00672fd0 - *(float *)(iVar6 + 0xcc) < _DAT_005d8cb4")
    half_line = first_hit(decompile_hits, "fVar3 = fVar3 * _DAT_005d85ec")
    add_line = first_hit(decompile_hits, "*(float *)(iVar6 + 0xfc) = fVar3 + *(float *)(iVar6 + 0xfc)")
    cap_check_line = first_hit(decompile_hits, "*(float *)(*(int *)(iVar6 + 0x4b0) + 0x20) < *(float *)(iVar6 + 0xfc)")
    cap_write_line = first_hit(decompile_hits, "*(undefined4 *)(iVar6 + 0xfc) = *(undefined4 *)(*(int *)(iVar6 + 0x4b0) + 0x20)")
    mirror_line = first_hit(decompile_hits, "*(undefined4 *)(*(int *)((int)param_1 + 0x20) + 0x100)")

    if time_gate_line and add_line and time_gate_line >= add_line:
        failures.append("time-since-ground gate does not precede energy addition")
    if half_line and add_line and half_line >= add_line:
        failures.append("half-recharge multiplier does not precede energy addition")
    if add_line and cap_check_line and add_line >= cap_check_line:
        failures.append("energy addition does not precede max-energy cap check")
    if cap_check_line and cap_write_line and cap_check_line >= cap_write_line:
        failures.append("max-energy cap check does not precede cap write")
    if cap_write_line and mirror_line and cap_write_line >= mirror_line:
        failures.append("cap write does not precede shield/energy mirror")

    return {
        "schema": "battleengine-walker-recharge-candidate.v1",
        "status": "pass" if not failures else "blocked",
        "sourceFile": relative(SOURCE),
        "decompileDir": relative(decompile_dir),
        "decompileFile": relative(decompile),
        "constantsFile": relative(constants_path),
        "sourceTokenLineHits": source_hits,
        "decompileTokenLineHits": decompile_hits,
        "constantChecks": {
            name: constants.get(name, {})
            for name in EXPECTED_CONSTANTS
        },
        "lineOrder": {
            "timeSinceGroundGate": time_gate_line,
            "halfRechargeMultiplier": half_line,
            "energyAddition": add_line,
            "maxEnergyCapCheck": cap_check_line,
            "maxEnergyCapWrite": cap_write_line,
            "energyShieldMirror": mirror_line,
        },
        "failures": failures,
        "whatIsProven": [
            "Source CBattleEngineWalkerPart::Move() still contains recent-ground recharge, infinite-energy/cloak exclusions, ground-energy-increase addition, half-rate recharge after weapon use, max-energy cap, and shield/energy mirror tokens.",
            "Fresh read-only CMonitor__ProcessTrackingAndSurfaceAlignment decompile contains a source-compatible recent-ground gate, two exclusion flags, config-rate addition, half multiplier, max cap, and shield/energy mirror cluster.",
            "The read-only constant scan maps _DAT_005d8cb4 to 0.3 and _DAT_005d85ec to 0.5 in .rdata.",
        ],
        "notProven": [
            "Exact source-to-retail identity for CBattleEngineWalkerPart::Move().",
            "Exact semantic names for the retail flags at offsets 0x160, 0x4ac, or the state at param_1+0x14.",
            "Runtime walker recharge behavior.",
            "Cloak energy gate, forced decloak, render flag, or weapon-fired stealth reset identity.",
            "Ghidra rename-map mutation.",
            "Rebuildable open-source gameplay implementation.",
        ],
        "privacy": "Report stores repo-relative paths, source token names, decompile token names, public addresses, constants, and line numbers only; raw decompile and constant JSON remain ignored under subagents/.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BattleEngine walker recharge candidate read-back evidence.")
    parser.add_argument("--check", action="store_true", help="run the candidate probe")
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE, help="ignored Ghidra decompile export dir")
    parser.add_argument("--constants", type=Path, default=DEFAULT_CONSTANTS, help="ignored read-only constant JSON")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    decompile_dir = args.decompile_dir if args.decompile_dir.is_absolute() else ROOT / args.decompile_dir
    constants_path = args.constants if args.constants.is_absolute() else ROOT / args.constants
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    report = build_report(decompile_dir, constants_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine walker recharge candidate probe")
        print(f"Status: {report['status']}")
        print(f"Source tokens: {sum(1 for lines in report['sourceTokenLineHits'].values() if lines)}/{len(SOURCE_TOKENS)}")
        print(f"Decompile tokens: {sum(1 for lines in report['decompileTokenLineHits'].values() if lines)}/{len(DECOMPILE_TOKENS)}")
        if report["failures"]:
            for failure in report["failures"]:
                print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
