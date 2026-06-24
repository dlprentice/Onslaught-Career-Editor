#!/usr/bin/env python3
"""Validate the bounded cloak gate state/config candidate.

This probe ties the latest gate-blocked runtime result back to existing
read-only source and Ghidra evidence. It does not launch BEA, read or patch the
installed executable, attach a debugger, or mutate a Ghidra project. Raw
decompile inputs and generated JSON stay under ignored ``subagents/``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references" / "Onslaught" / "BattleEngine.cpp"
DATA_HEADER = ROOT / "references" / "Onslaught" / "BattleEngineDataManager.h"
DEFAULT_TARGET_DECOMPILE = (
    ROOT / "subagents" / "battleengine-target-profile-ghidra-readback" / "current" / "decompile"
)
DEFAULT_SELECTION_DECOMPILE = (
    ROOT / "subagents" / "battleengine-selection-helper-ghidra-readback" / "current" / "decompile"
)
DEFAULT_CLOAK_DECOMPILE = (
    ROOT / "subagents" / "battleengine-cloak-stealth-candidate" / "current" / "decompile"
)
DEFAULT_WALKER_DECOMPILE = (
    ROOT / "subagents" / "battleengine-walker-recharge-candidate" / "current" / "decompile"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-cloak-gate-state-candidate"
    / "current"
    / "battleengine-cloak-gate-state-candidate.json"
)

SOURCE_TOKENS = (
    "void CBattleEngine::HandleCloak()",
    "else if (mEnergy>=mConfiguration->mMinTransformEnergy)",
    "void CBattleEngine::Cloak()",
    "if (mConfiguration->mStealth>0)",
    "mDesiredStealth=mConfiguration->mStealth;",
    "mCloaked=TRUE;",
    "void CBattleEngine::Decloak()",
    "mDesiredStealth=0;",
    "mCloaked=FALSE;",
)

DATA_TOKENS = (
    "float\t\t\tmMaxAirEnergyCost,mMinAirEnergyCost;",
    "float\t\t\tmLife,mEnergy,mShieldEfficiency;",
    "float\t\t\tmGroundEnergyIncrease,mMinTransformEnergy;",
    "float\t\t\tmStealth;",
)

PROFILE_APPLY_TOKENS = (
    "iVar2 = CBattleEngine__GetWeaponProfileByIndex(*(int *)(param_1 + 0x600));",
    "*(int *)(param_1 + 0x4b0) = iVar2;",
    "*(undefined4 *)(param_1 + 0xfc) = *(undefined4 *)(iVar2 + 0x20);",
    "*(undefined4 *)(param_1 + 0xf8) = *(undefined4 *)(iVar2 + 0x1c);",
    "CConsole__Printf(&DAT_0066f580,*(char **)(iVar2 + 0xa8));",
)

CLOAK_HELPER_TOKENS = (
    "iVar1 = *(int *)(param_1 + 0x4b0);",
    "*(float *)(iVar1 + 0x2c) <= *(float *)(param_1 + 0xfc)",
    "_DAT_005d856c < *(float *)(iVar1 + 0xa0)",
    "uVar2 = *(undefined4 *)(iVar1 + 0xa0);",
    "*(undefined4 *)(param_1 + 0x4ac) = 1;",
    "*(undefined4 *)(param_1 + 0x5dc) = uVar2;",
)

ACTIVE_CLOAK_TOKENS = (
    "if ((*(int *)((int)param_1 + 0x4ac) != 0)",
    "*(float *)((int)param_1 + 0xfc) - *(float *)(*(int *)((int)param_1 + 0x4b0) + 8)",
    "*(undefined4 *)((int)param_1 + 0xfc) = 0",
    "*(undefined4 *)((int)param_1 + 0x5dc) = 0",
    "*(undefined4 *)((int)param_1 + 0x4ac) = 0",
)

WALKER_PROFILE_TOKENS = (
    "fVar3 = *(float *)(*(int *)(iVar6 + 0x4b0) + 0x28)",
    "*(float *)(*(int *)(iVar6 + 0x4b0) + 0x20) < *(float *)(iVar6 + 0xfc)",
    "*(undefined4 *)(iVar6 + 0xfc) = *(undefined4 *)(*(int *)(iVar6 + 0x4b0) + 0x20)",
)

SELECTION_PROFILE_TOKENS = (
    "CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1)",
    "iVar1 = *(int *)((int)param_1 + 0x20);",
    "_DAT_005d856c < *(float *)(iVar1 + 0x52c + iVar2 * 4)",
    "*(float *)(*(int *)(iVar1 + 0x4b0) + 0x88 + iVar2 * 4)",
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalized(text: str) -> str:
    return "".join(text.split())


def token_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    norm_lines = [normalized(line) for line in lines]
    return {
        token: [
            index + 1
            for index, line in enumerate(norm_lines)
            if normalized(token) in line
        ]
        for token in tokens
    }


def require_tokens(label: str, hits: dict[str, list[int]], failures: list[str]) -> None:
    failures.extend(f"missing {label} token: {token}" for token, lines in hits.items() if not lines)


def build_report(
    target_decompile: Path,
    selection_decompile: Path,
    cloak_decompile: Path,
    walker_decompile: Path,
) -> dict[str, object]:
    profile_apply = target_decompile / "0040c650_CBattleEngine__ApplyWeaponProfileByIndex.c"
    resolved_usable = selection_decompile / "00414630_CBattleEngine__IsResolvedEntryUsable.c"
    cloak_helper = cloak_decompile / "0040d4d0_CGeneralVolume__Update4ACLatchFromHeightAndA0.c"
    cmonitor = cloak_decompile / "004081c0_CMonitor__Process.c"
    walker_recharge = walker_decompile / "00413760_CMonitor__ProcessTrackingAndSurfaceAlignment.c"

    source_hits = token_hits(SOURCE, SOURCE_TOKENS)
    data_hits = token_hits(DATA_HEADER, DATA_TOKENS)
    profile_apply_hits = token_hits(profile_apply, PROFILE_APPLY_TOKENS)
    cloak_helper_hits = token_hits(cloak_helper, CLOAK_HELPER_TOKENS)
    active_cloak_hits = token_hits(cmonitor, ACTIVE_CLOAK_TOKENS)
    walker_profile_hits = token_hits(walker_recharge, WALKER_PROFILE_TOKENS)
    selection_profile_hits = token_hits(resolved_usable, SELECTION_PROFILE_TOKENS)

    failures: list[str] = []
    for path in (SOURCE, DATA_HEADER, profile_apply, resolved_usable, cloak_helper, cmonitor, walker_recharge):
        if not path.is_file():
            failures.append(f"missing input file: {relative(path)}")
    require_tokens("source cloak", source_hits, failures)
    require_tokens("source data", data_hits, failures)
    require_tokens("profile apply", profile_apply_hits, failures)
    require_tokens("cloak helper", cloak_helper_hits, failures)
    require_tokens("active cloak", active_cloak_hits, failures)
    require_tokens("walker profile", walker_profile_hits, failures)
    require_tokens("selection profile", selection_profile_hits, failures)

    return {
        "schema": "battleengine-cloak-gate-state-candidate.v1",
        "status": "pass" if not failures else "blocked",
        "inputs": {
            "source": relative(SOURCE),
            "dataHeader": relative(DATA_HEADER),
            "profileApply": relative(profile_apply),
            "resolvedUsable": relative(resolved_usable),
            "cloakHelper": relative(cloak_helper),
            "cmonitor": relative(cmonitor),
            "walkerRecharge": relative(walker_recharge),
        },
        "sourceTokenLineHits": source_hits,
        "dataTokenLineHits": data_hits,
        "profileApplyTokenLineHits": profile_apply_hits,
        "cloakHelperTokenLineHits": cloak_helper_hits,
        "activeCloakTokenLineHits": active_cloak_hits,
        "walkerProfileTokenLineHits": walker_profile_hits,
        "selectionProfileTokenLineHits": selection_profile_hits,
        "failures": failures,
        "whatIsProven": [
            "Source CBattleEngine::HandleCloak routes to Cloak only when energy meets MinTransformEnergy, and source CBattleEngine::Cloak gates activation on mConfiguration->mStealth > 0.",
            "Source CBattleEngineData carries mStealth beside energy, min-transform, max-air-energy-cost, and ground-energy-increase configuration fields.",
            "Read-only retail decompile shows CBattleEngine__ApplyWeaponProfileByIndex writes the current profile pointer to this+0x4b0 and copies profile+0x20/profile+0x1c into current energy/life-like fields.",
            "Read-only retail decompile shows the candidate cloak helper gates activation on linked profile+0x2c <= current energy and profile+0xa0 > zero-threshold, then copies profile+0xa0 into the target scalar.",
            "Read-only retail CMonitor and walker recharge decompiles reuse the same this+0x4b0 profile pointer for active cloak energy burn, max energy, and ground recharge-like configuration values.",
            "Selection helper decompile shows the same profile pointer participates in per-slot usability/readiness gates, reinforcing that this+0x4b0 is a current configuration/profile object rather than an arbitrary runtime input object.",
        ],
        "runtimeInterpretation": [
            "The latest copied-profile gate observer saw helper reachability with linked profile+0xa0 equal to the zero-threshold side, so the tested configuration/state did not satisfy the source-compatible stealth-positive activation gate.",
            "The next runtime wave should identify or select a profile/configuration with a positive profile+0xa0 before sending weapon-fire input.",
        ],
        "notProven": [
            "Exact source-to-retail field layout for every CBattleEngineData member.",
            "Final semantic name for retail profile+0xa0.",
            "Runtime cloak activation.",
            "Fire-while-cloaked behavior.",
            "Retail RF_CLOAKED render-flag identity.",
            "Ghidra rename-map mutation or project semantic promotion.",
            "Rebuildable gameplay implementation parity.",
        ],
        "privacy": "Report stores repo-relative paths, token names, public addresses, and line numbers only; raw decompile inputs and generated JSON remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--target-decompile", type=Path, default=DEFAULT_TARGET_DECOMPILE)
    parser.add_argument("--selection-decompile", type=Path, default=DEFAULT_SELECTION_DECOMPILE)
    parser.add_argument("--cloak-decompile", type=Path, default=DEFAULT_CLOAK_DECOMPILE)
    parser.add_argument("--walker-decompile", type=Path, default=DEFAULT_WALKER_DECOMPILE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    report = build_report(
        args.target_decompile if args.target_decompile.is_absolute() else ROOT / args.target_decompile,
        args.selection_decompile if args.selection_decompile.is_absolute() else ROOT / args.selection_decompile,
        args.cloak_decompile if args.cloak_decompile.is_absolute() else ROOT / args.cloak_decompile,
        args.walker_decompile if args.walker_decompile.is_absolute() else ROOT / args.walker_decompile,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine cloak gate state candidate probe")
        print(f"Status: {report['status']}")
        print(f"Source cloak tokens: {sum(1 for hits in report['sourceTokenLineHits'].values() if hits)}/{len(SOURCE_TOKENS)}")
        print(f"Source data tokens: {sum(1 for hits in report['dataTokenLineHits'].values() if hits)}/{len(DATA_TOKENS)}")
        print(f"Profile apply tokens: {sum(1 for hits in report['profileApplyTokenLineHits'].values() if hits)}/{len(PROFILE_APPLY_TOKENS)}")
        print(f"Cloak helper tokens: {sum(1 for hits in report['cloakHelperTokenLineHits'].values() if hits)}/{len(CLOAK_HELPER_TOKENS)}")
        print(f"Active cloak tokens: {sum(1 for hits in report['activeCloakTokenLineHits'].values() if hits)}/{len(ACTIVE_CLOAK_TOKENS)}")
        print(f"Walker profile tokens: {sum(1 for hits in report['walkerProfileTokenLineHits'].values() if hits)}/{len(WALKER_PROFILE_TOKENS)}")
        print(f"Selection profile tokens: {sum(1 for hits in report['selectionProfileTokenLineHits'].values() if hits)}/{len(SELECTION_PROFILE_TOKENS)}")
        for failure in report["failures"]:
            print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
