#!/usr/bin/env python3
"""Validate bounded cloak/stealth retail-candidate evidence.

This probe checks Stuart-source cloak/stealth anchors against a fresh ignored
Ghidra decompile export. The result is deliberately bounded: it records
candidate retail evidence for cloak latch/energy checks, active energy burn,
forced decloak, stealth-style interpolation, and target-range scaling while
keeping exact method identity, weapon-fire reset, and render-flag identity
unproven.
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
SOURCE = ROOT / "references" / "Onslaught" / "BattleEngine.cpp"
DEFAULT_DECOMPILE = ROOT / "subagents" / "battleengine-cloak-stealth-candidate" / "current" / "decompile"
DEFAULT_CONSTANTS = ROOT / "subagents" / "battleengine-cloak-stealth-candidate" / "current" / "constants.json"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-cloak-stealth-candidate" / "current" / "cloak-stealth-candidate.json"

SOURCE_TOKENS = (
    "if (mCloaked)",
    "mEnergy-=mConfiguration->mMaxAirEnergyCost;",
    "if (mEnergy<0)",
    "Decloak();",
    "if (mConfiguration->mStealth>0)",
    "mDesiredStealth=mConfiguration->mStealth;",
    "mCloaked=TRUE;",
    "mDesiredStealth=0;",
    "mCloaked=FALSE;",
    "if (mStealth<mDesiredStealth-STEALTHSPEED)",
    "mStealth+=STEALTHSPEED;",
    "mStealth=mDesiredStealth;",
    "magnitudeSq=weapon->GetLockRange()*(1.0f-unit->GetStealth()/100.0f)",
    "CMeshRenderer::SetRenderAlpha((SINT)(255.0f-(mStealth/100.0f*255.0f)))",
    "flags|=RF_CLOAKED;",
)

CLOAK_HELPER_TOKENS = (
    "if (*(int *)(param_1 + 0x4ac) != 0)",
    "*(undefined4 *)(param_1 + 0x5dc) = 0",
    "*(undefined4 *)(param_1 + 0x4ac) = 0",
    "*(float *)(iVar1 + 0x2c) <= *(float *)(param_1 + 0xfc)",
    "_DAT_005d856c < *(float *)(iVar1 + 0xa0)",
    "*(undefined4 *)(param_1 + 0x4ac) = 1",
    "*(undefined4 *)(param_1 + 0x5dc) = uVar2",
)

C_MONITOR_TOKENS = (
    "if ((*(int *)((int)param_1 + 0x4ac) != 0)",
    "*(float *)((int)param_1 + 0xfc) - *(float *)(*(int *)((int)param_1 + 0x4b0) + 8)",
    "*(undefined4 *)((int)param_1 + 0xfc) = 0",
    "*(undefined4 *)((int)param_1 + 0x5dc) = 0",
    "*(undefined4 *)((int)param_1 + 0x4ac) = 0",
    "*(undefined4 *)((int)param_1 + 0x2d0) = *(undefined4 *)((int)param_1 + 0x2c8)",
    "*(float *)((int)param_1 + 0x2cc) <= *(float *)((int)param_1 + 0x2c8)",
    "*(float *)((int)param_1 + 0x2c8) - _DAT_005d85c0",
    "*(float *)((int)param_1 + 0x2c8) + _DAT_005d85c0",
    "*(undefined4 *)((int)param_1 + 0x2c8) = *(undefined4 *)((int)param_1 + 0x2cc)",
)

TARGETING_TOKENS = (
    "fVar11 = (float10)_DAT_005d85fc",
    "fVar1 = (float10)_DAT_005d8568",
    "CBattleEngine__GetProfileField9CByDistance",
    "dVar13 = dVar13 * (double)(float)(fVar1 - fVar12 * fVar11)",
)

RENDER_CONTEXT_TOKENS = (
    "CMeshRenderer__RenderMesh",
    "0xff008080",
    "0x3dcccccd",
)

EXPECTED_CONSTANTS = {
    "one": ("0x005d8568", 1.0),
    "stealth_lerp_step": ("0x005d85c0", 0.1),
    "inv_100_candidate": ("0x005d85fc", 0.01),
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


def load_constants(path: Path) -> dict[str, dict[str, object]]:
    if not path.is_file():
        return {}
    report = json.loads(path.read_text(encoding="utf-8"))
    return {item["name"]: item for item in report.get("values", [])}


def require_index_rows(index_rows: list[dict[str, str]], required: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for address, name in required.items():
        matches = [
            row
            for row in index_rows
            if row.get("address", "").lower() == address
            and row.get("name") == name
            and row.get("status") == "OK"
        ]
        if not matches:
            failures.append(f"decompile index lacks OK row for {address} {name}")
    return failures


def build_report(decompile_dir: Path, constants_path: Path) -> dict[str, object]:
    cmonitor = decompile_dir / "004081c0_CMonitor__Process.c"
    targeting = decompile_dir / "00406560_CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.c"
    render_mesh = decompile_dir / "004b6350_CMeshRenderer__RenderMesh.c"
    cloak_helper = decompile_dir / "0040d4d0_CGeneralVolume__Update4ACLatchFromHeightAndA0.c"
    index_rows = read_index(decompile_dir)
    constants = load_constants(constants_path)

    source_hits = token_hits(SOURCE, SOURCE_TOKENS, normalize=True)
    cloak_helper_hits = token_hits(cloak_helper, CLOAK_HELPER_TOKENS, normalize=True)
    cmonitor_hits = token_hits(cmonitor, C_MONITOR_TOKENS, normalize=True)
    targeting_hits = token_hits(targeting, TARGETING_TOKENS, normalize=True)
    render_context_hits = token_hits(render_mesh, RENDER_CONTEXT_TOKENS, normalize=True)

    failures: list[str] = []
    if not SOURCE.is_file():
        failures.append(f"missing source file: {relative(SOURCE)}")
    for path in (cmonitor, targeting, render_mesh, cloak_helper):
        if not path.is_file():
            failures.append(f"missing decompile file: {relative(path)}")
    if not index_rows:
        failures.append(f"missing or empty decompile index: {relative(decompile_dir / 'index.tsv')}")
    else:
        failures.extend(
            require_index_rows(
                index_rows,
                {
                    "0x004081c0": "CMonitor__Process",
                    "0x00406560": "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
                    "0x004b6350": "CMeshRenderer__RenderMesh",
                    "0x0040d4d0": "CGeneralVolume__Update4ACLatchFromHeightAndA0",
                },
            )
        )

    failures.extend(f"missing source token: {token}" for token, lines in source_hits.items() if not lines)
    failures.extend(f"missing cloak helper token: {token}" for token, lines in cloak_helper_hits.items() if not lines)
    failures.extend(f"missing CMonitor token: {token}" for token, lines in cmonitor_hits.items() if not lines)
    failures.extend(f"missing targeting token: {token}" for token, lines in targeting_hits.items() if not lines)
    failures.extend(f"missing render context token: {token}" for token, lines in render_context_hits.items() if not lines)

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

    return {
        "schema": "battleengine-cloak-stealth-candidate.v1",
        "status": "pass" if not failures else "blocked",
        "sourceFile": relative(SOURCE),
        "decompileDir": relative(decompile_dir),
        "constantsFile": relative(constants_path),
        "sourceTokenLineHits": source_hits,
        "cloakHelperTokenLineHits": cloak_helper_hits,
        "cmonitorTokenLineHits": cmonitor_hits,
        "targetingTokenLineHits": targeting_hits,
        "renderContextTokenLineHits": render_context_hits,
        "constantChecks": {name: constants.get(name, {}) for name in EXPECTED_CONSTANTS},
        "failures": failures,
        "whatIsProven": [
            "The source still contains cloak/decloak, active cloak energy burn, forced decloak, stealth interpolation, target-range stealth reduction, render alpha, and RF_CLOAKED render flag tokens.",
            "Fresh read-only CGeneralVolume__Update4ACLatchFromHeightAndA0 decompile contains a candidate cloak toggle/latch helper that sets or clears offsets 0x4ac and 0x5dc after energy/config checks.",
            "Fresh read-only CMonitor__Process decompile contains active energy burn and forced-decloak clearing for the 0x4ac/0x5dc latch plus a candidate current/target transition around offsets 0x2c8 and 0x2cc.",
            "Fresh read-only target/fire decompile still contains a stealth-style 0.01 range-scaling factor used in target selection context.",
            "The render mesh context was exported and checked, but only as context; it is not claimed as RF_CLOAKED identity.",
            "Read-only constant checks map _DAT_005d85c0 to 0.1 and _DAT_005d85fc to 0.01.",
        ],
        "notProven": [
            "Exact source-to-retail identity for CBattleEngine::HandleCloak, Cloak, Decloak, Render, or WeaponFired.",
            "Cloak button handling identity in the retail control path.",
            "Retail RF_CLOAKED render-flag identity.",
            "Weapon-fired stealth reset identity.",
            "Runtime cloak, target-lock, render, or weapon behavior.",
            "Ghidra rename-map mutation.",
            "Rebuildable open-source gameplay implementation.",
        ],
        "privacy": "Report stores repo-relative paths, source token names, decompile token names, public addresses, constants, and line numbers only; raw decompile and constant JSON remain ignored under subagents/.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BattleEngine cloak/stealth bounded candidate evidence.")
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
        print("BattleEngine cloak/stealth candidate probe")
        print(f"Status: {report['status']}")
        print(f"Source tokens: {sum(1 for lines in report['sourceTokenLineHits'].values() if lines)}/{len(SOURCE_TOKENS)}")
        print(f"Cloak helper tokens: {sum(1 for lines in report['cloakHelperTokenLineHits'].values() if lines)}/{len(CLOAK_HELPER_TOKENS)}")
        print(f"CMonitor tokens: {sum(1 for lines in report['cmonitorTokenLineHits'].values() if lines)}/{len(C_MONITOR_TOKENS)}")
        print(f"Targeting tokens: {sum(1 for lines in report['targetingTokenLineHits'].values() if lines)}/{len(TARGETING_TOKENS)}")
        print(f"Render context tokens: {sum(1 for lines in report['renderContextTokenLineHits'].values() if lines)}/{len(RENDER_CONTEXT_TOKENS)}")
        if report["failures"]:
            for failure in report["failures"]:
                print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
