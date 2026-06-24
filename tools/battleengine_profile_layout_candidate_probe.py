#!/usr/bin/env python3
"""Validate the source-to-retail CBattleEngineData profile layout candidate.

This probe is a static guard for the cloak state work. It checks Stuart source
field order, the x86 GenericSPtrSet shape used by that source, and existing
read-only retail decompiles that consume the same offsets. It does not launch
BEA, read or patch the installed executable, attach a debugger, or mutate a
Ghidra project.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "references" / "Onslaught" / "BattleEngineDataManager.h"
SPTRSET_HEADER = ROOT / "references" / "Onslaught" / "SPtrSet.h"
TARGET_DECOMPILE = (
    ROOT
    / "subagents"
    / "battleengine-target-profile-ghidra-readback"
    / "current"
    / "decompile"
    / "0040c650_CBattleEngine__ApplyWeaponProfileByIndex.c"
)
CLOAK_HELPER_DECOMPILE = (
    ROOT
    / "subagents"
    / "battleengine-cloak-stealth-candidate"
    / "current"
    / "decompile"
    / "0040d4d0_CGeneralVolume__Update4ACLatchFromHeightAndA0.c"
)
WALKER_DECOMPILE = (
    ROOT
    / "subagents"
    / "battleengine-walker-recharge-candidate"
    / "current"
    / "decompile"
    / "00413760_CMonitor__ProcessTrackingAndSurfaceAlignment.c"
)
SELECTION_DECOMPILE = (
    ROOT
    / "subagents"
    / "battleengine-selection-helper-ghidra-readback"
    / "current"
    / "decompile"
    / "00414630_CBattleEngine__IsResolvedEntryUsable.c"
)
OUT = (
    ROOT
    / "subagents"
    / "battleengine-profile-layout-candidate"
    / "current"
    / "battleengine-profile-layout-candidate.json"
)

SOURCE_LAYOUT_TOKENS = (
    "float\t\t\tmMaxAirVelocity,mMinAirVelocity;",
    "float\t\t\tmMaxAirEnergyCost,mMinAirEnergyCost;",
    "float\t\t\tmGroundVelocity;",
    "float\t\t\tmAirTurnRate,mGroundTurnRate;",
    "float\t\t\tmLife,mEnergy,mShieldEfficiency;",
    "float\t\t\tmGroundEnergyIncrease,mMinTransformEnergy;",
    "float\t\t\tmWalkFriction,mMaxWalkVelocity;",
    "float\t\t\tmRollEnergyCost,mLoopEnergyCost;",
    "SPtrSet<char*>\tmWalkerWeapons;",
    "SPtrSet<char*>\tmJetWeapons;",
    "char\t\t\t*mPrimaryWeapon,*mAugWeapon;",
    "char\t\t\t*mExplosion;",
    "char\t\t\t*mCockpit;",
    "BOOL\t\t\tmStoreHeat[kBattleEngineStores];",
    "float\t\t\tmStoreValue[kBattleEngineStores];",
    "float\t\t\tmStealth;",
    "SINT\t\t\tmLanguageName;",
    "char\t\t\t*mConfigurationName;",
)

SPTRSET_TOKENS = (
    "SPtrSetNode* mFirst;",
    "SPtrSetNode* mLast;",
    "SPtrSetNode* mIterator;",
    "int\t\t\t mSize;",
)

RETAIL_PROFILE_TOKENS = (
    "*(undefined4 *)(param_1 + 0xfc) = *(undefined4 *)(iVar2 + 0x20);",
    "*(undefined4 *)(param_1 + 0xf8) = *(undefined4 *)(iVar2 + 0x1c);",
    "CConsole__Printf(&DAT_0066f580,*(char **)(iVar2 + 0xa8));",
)

RETAIL_CLOAK_TOKENS = (
    "*(float *)(iVar1 + 0x2c) <= *(float *)(param_1 + 0xfc)",
    "_DAT_005d856c < *(float *)(iVar1 + 0xa0)",
    "uVar2 = *(undefined4 *)(iVar1 + 0xa0);",
)

RETAIL_WALKER_TOKENS = (
    "fVar3 = *(float *)(*(int *)(iVar6 + 0x4b0) + 0x28)",
    "*(float *)(*(int *)(iVar6 + 0x4b0) + 0x20) < *(float *)(iVar6 + 0xfc)",
)

RETAIL_SELECTION_TOKENS = (
    "*(float *)(*(int *)(iVar1 + 0x4b0) + 0x88 + iVar2 * 4)",
)

EXPECTED_OFFSETS = {
    "mLife": 0x1C,
    "mEnergy": 0x20,
    "mGroundEnergyIncrease": 0x28,
    "mMinTransformEnergy": 0x2C,
    "mStoreHeat": 0x70,
    "mStoreValue": 0x88,
    "mStealth": 0xA0,
    "mLanguageName": 0xA4,
    "mConfigurationName": 0xA8,
}


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


def calculated_offsets() -> dict[str, int]:
    offset = 0
    offsets: dict[str, int] = {}

    def scalar(name: str, size: int = 4) -> None:
        nonlocal offset
        offsets[name] = offset
        offset += size

    def array(name: str, count: int, size: int = 4) -> None:
        nonlocal offset
        offsets[name] = offset
        offset += count * size

    def sptrset(name: str) -> None:
        # x86 source shape: mFirst, mLast, mIterator, mSize.
        array(name, 4, 4)

    scalar("mMaxAirVelocity")
    scalar("mMinAirVelocity")
    scalar("mMaxAirEnergyCost")
    scalar("mMinAirEnergyCost")
    scalar("mGroundVelocity")
    scalar("mAirTurnRate")
    scalar("mGroundTurnRate")
    scalar("mLife")
    scalar("mEnergy")
    scalar("mShieldEfficiency")
    scalar("mGroundEnergyIncrease")
    scalar("mMinTransformEnergy")
    scalar("mWalkFriction")
    scalar("mMaxWalkVelocity")
    scalar("mRollEnergyCost")
    scalar("mLoopEnergyCost")
    sptrset("mWalkerWeapons")
    sptrset("mJetWeapons")
    scalar("mPrimaryWeapon")
    scalar("mAugWeapon")
    scalar("mExplosion")
    scalar("mCockpit")
    array("mStoreHeat", 6)
    array("mStoreValue", 6)
    scalar("mStealth")
    scalar("mLanguageName")
    scalar("mConfigurationName")
    offsets["sizeofCandidate"] = offset
    return offsets


def build_report() -> dict[str, object]:
    source_hits = token_hits(HEADER, SOURCE_LAYOUT_TOKENS)
    sptrset_hits = token_hits(SPTRSET_HEADER, SPTRSET_TOKENS)
    retail_profile_hits = token_hits(TARGET_DECOMPILE, RETAIL_PROFILE_TOKENS)
    retail_cloak_hits = token_hits(CLOAK_HELPER_DECOMPILE, RETAIL_CLOAK_TOKENS)
    retail_walker_hits = token_hits(WALKER_DECOMPILE, RETAIL_WALKER_TOKENS)
    retail_selection_hits = token_hits(SELECTION_DECOMPILE, RETAIL_SELECTION_TOKENS)
    offsets = calculated_offsets()

    failures: list[str] = []
    for path in (HEADER, SPTRSET_HEADER, TARGET_DECOMPILE, CLOAK_HELPER_DECOMPILE, WALKER_DECOMPILE, SELECTION_DECOMPILE):
        if not path.is_file():
            failures.append(f"missing input file: {relative(path)}")
    require_tokens("source layout", source_hits, failures)
    require_tokens("SPtrSet shape", sptrset_hits, failures)
    require_tokens("retail profile apply", retail_profile_hits, failures)
    require_tokens("retail cloak helper", retail_cloak_hits, failures)
    require_tokens("retail walker profile", retail_walker_hits, failures)
    require_tokens("retail selection profile", retail_selection_hits, failures)
    for field, expected in EXPECTED_OFFSETS.items():
        actual = offsets.get(field)
        if actual != expected:
            failures.append(f"layout mismatch {field}: expected 0x{expected:x}, got {actual!r}")

    return {
        "schema": "battleengine-profile-layout-candidate.v1",
        "status": "pass" if not failures else "blocked",
        "assumptions": {
            "target": "Steam retail x86 process layout",
            "pointerBytes": 4,
            "floatBytes": 4,
            "boolBytes": 4,
            "sintBytes": 4,
            "genericSPtrSetBytes": 16,
        },
        "inputs": {
            "sourceHeader": relative(HEADER),
            "sptrSetHeader": relative(SPTRSET_HEADER),
            "profileApply": relative(TARGET_DECOMPILE),
            "cloakHelper": relative(CLOAK_HELPER_DECOMPILE),
            "walkerRecharge": relative(WALKER_DECOMPILE),
            "selectionHelper": relative(SELECTION_DECOMPILE),
        },
        "calculatedOffsetsHex": {field: f"0x{offset:x}" for field, offset in offsets.items()},
        "expectedOffsetsHex": {field: f"0x{offset:x}" for field, offset in EXPECTED_OFFSETS.items()},
        "sourceLayoutTokenLineHits": source_hits,
        "sptrSetTokenLineHits": sptrset_hits,
        "retailProfileTokenLineHits": retail_profile_hits,
        "retailCloakTokenLineHits": retail_cloak_hits,
        "retailWalkerTokenLineHits": retail_walker_hits,
        "retailSelectionTokenLineHits": retail_selection_hits,
        "failures": failures,
        "whatIsProven": [
            "Stuart source CBattleEngineData field order and x86 GenericSPtrSet shape place mLife at +0x1c, mEnergy at +0x20, mGroundEnergyIncrease at +0x28, mMinTransformEnergy at +0x2c, mStoreValue at +0x88, mStealth at +0xa0, and mConfigurationName at +0xa8.",
            "Existing read-only retail decompile consumes profile +0x1c/+0x20 as life/energy-like state, profile +0x28/+0x20 as recharge/max-energy-like configuration, profile +0x88 as per-slot store values, profile +0xa0 in the cloak helper gate, and profile +0xa8 as the printed configuration name.",
            "Retail profile +0xa0 is therefore a strong source-compatible candidate for CBattleEngineData::mStealth, and the latest copied-profile runtime blocker is consistent with a non-stealth-capable current profile.",
        ],
        "notProven": [
            "Exact values of all loaded retail BattleEngine profiles.",
            "Which profile/configuration the latest copied runtime selected.",
            "A runtime profile with positive mStealth/profile+0xa0.",
            "Runtime cloak activation or fire-while-cloaked behavior.",
            "A Ghidra rename-map mutation.",
            "Rebuildable gameplay implementation parity.",
        ],
        "privacy": "Report contains source-layout field names, public offsets, repo-relative paths, and token line hits only; raw decompile inputs and generated JSON remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
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

    report = build_report()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine profile layout candidate probe")
        print(f"Status: {report['status']}")
        print(f"Source layout tokens: {sum(1 for hits in report['sourceLayoutTokenLineHits'].values() if hits)}/{len(SOURCE_LAYOUT_TOKENS)}")
        print(f"SPtrSet tokens: {sum(1 for hits in report['sptrSetTokenLineHits'].values() if hits)}/{len(SPTRSET_TOKENS)}")
        print(f"Retail profile tokens: {sum(1 for hits in report['retailProfileTokenLineHits'].values() if hits)}/{len(RETAIL_PROFILE_TOKENS)}")
        print(f"Retail cloak tokens: {sum(1 for hits in report['retailCloakTokenLineHits'].values() if hits)}/{len(RETAIL_CLOAK_TOKENS)}")
        print(f"Retail walker tokens: {sum(1 for hits in report['retailWalkerTokenLineHits'].values() if hits)}/{len(RETAIL_WALKER_TOKENS)}")
        print(f"Retail selection tokens: {sum(1 for hits in report['retailSelectionTokenLineHits'].values() if hits)}/{len(RETAIL_SELECTION_TOKENS)}")
        print("Calculated critical offsets:")
        for field in EXPECTED_OFFSETS:
            print(f"- {field}: {report['calculatedOffsetsHex'][field]}")
        for failure in report["failures"]:
            print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
