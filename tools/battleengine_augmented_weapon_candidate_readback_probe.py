#!/usr/bin/env python3
"""Validate a public-safe AugmentWeapon candidate read-back.

This probe checks source augmented-weapon anchors plus ignored read-only
Ghidra evidence for the `hud_weapon_augmented` string xref and the current
decompile of the candidate function. The claim is intentionally bounded:
0x0040de40 is a strong augmented-weapon activation candidate, but this script
does not rename the function, mutate Ghidra, run the game, or prove runtime
weapon behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-weapon-identity-candidates"
    / "current"
    / "augmented-weapon-candidate-readback.json"
)


@dataclass(frozen=True)
class Check:
    key: str
    file: str
    tokens: tuple[str, ...]
    summary: str


CHECKS: tuple[Check, ...] = (
    Check(
        "source_augment_weapon_body",
        "references/Onslaught/BattleEngine.cpp",
        (
            "void CBattleEngine::AugmentWeapon()",
            "mAugActiveTime=EVENT_MANAGER.GetTime()",
            "mAugValue=MAX_AUG_VALUE",
            "mAugActive=TRUE",
            'PlayHudSample("hud_weapon_augmented")',
            "mAugmentedTime = EVENT_MANAGER.GetTime()",
        ),
        "Source AugmentWeapon body records event-time, max meter, active flag, HUD sample, and augmented-time anchors.",
    ),
    Check(
        "source_augment_evidence_note",
        "release/readiness/battleengine_augmented_weapon_source_anchor_2026-05-07.md",
        (
            "augmented_weapon_charge_decay_and_reset",
            "source-only pending retail-binary identity",
            "runtime weapon behavior proof",
        ),
        "Existing public source-anchor evidence keeps augmented weapon behavior source-only pending retail-binary identity.",
    ),
    Check(
        "hud_augmented_string_xref",
        "subagents/battleengine-weapon-identity-candidates/current/hud_augmented_string_xrefs.tsv",
        (
            "00623540",
            "0040def7",
            "0040de40",
            "CMonitor__HandleTargetStateChangeAndHudPrompt",
            "DATA",
        ),
        "Ignored Ghidra xref evidence maps the augmented HUD sample string to one current candidate function.",
    ),
    Check(
        "candidate_decompile_tokens",
        "subagents/battleengine-weapon-identity-candidates/current/decompile/0040de40_CMonitor__HandleTargetStateChangeAndHudPrompt.c",
        (
            "0x41200000",
            "+ 0x2f8) = 0x41200000",
            "+ 0x2fc) = 1",
            "+ 0x300) = DAT_00672fd0",
            "+ 0x30c) = DAT_00672fd0",
            "s_hud__s_00623314",
            "CBattleEngine__FindSoundEventByNameIfEnabled",
            "CMonitor__PlayRandomSampleFromChain",
        ),
        "Candidate decompile includes max-meter, active-flag, event-time, and HUD sample lookup/playback tokens.",
    ),
    Check(
        "candidate_caller_xref",
        "subagents/battleengine-weapon-identity-candidates/current/augment_candidate_function_xrefs.tsv",
        (
            "0040de40",
            "CMonitor__HandleTargetStateChangeAndHudPrompt",
            "00408582",
            "004081c0",
            "CMonitor__Process",
            "UNCONDITIONAL_CALL",
        ),
        "Ignored Ghidra xref evidence records the current known caller path into the candidate function.",
    ),
    Check(
        "candidate_caller_context_tokens",
        "subagents/battleengine-weapon-identity-candidates/current/caller-decompile/004081c0_CMonitor__Process.c",
        (
            "CMonitor__Process",
            "CMonitor__HandleTargetStateChangeAndHudPrompt(param_1);",
            "+ 0x2fc) == 0",
            "+ 0x2f8))",
            "*(float *)((int)param_1 + 0x2f8) - _DAT_005d8574",
            "*(undefined4 *)((int)param_1 + 0x2f8) = 0;",
            "*(undefined4 *)((int)param_1 + 0x2fc) = 0;",
        ),
        "Caller decompile includes source-aligned activation threshold, active-meter decay, and meter/active reset tokens.",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def line_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def summarize(check: Check) -> dict[str, object]:
    path = ROOT / check.file
    if not path.is_file():
        return {
            "key": check.key,
            "status": "FAIL",
            "file": check.file,
            "summary": f"Missing file: {check.file}",
            "tokenLineHits": {},
            "missingTokens": list(check.tokens),
        }

    hits = line_hits(path, check.tokens)
    missing = [token for token, token_hits in hits.items() if not token_hits]
    return {
        "key": check.key,
        "status": "PASS" if not missing else "FAIL",
        "file": relative(path),
        "summary": check.summary,
        "tokenLineHits": hits,
        "missingTokens": missing,
    }


def build_report() -> dict[str, object]:
    results = [summarize(check) for check in CHECKS]
    failures = [result for result in results if result["status"] != "PASS"]
    return {
        "schema": "battleengine-augmented-weapon-candidate-readback.v1",
        "status": "pass" if not failures else "blocked",
        "checksPassed": len(results) - len(failures),
        "checksTotal": len(results),
        "results": results,
        "privacy": "Report stores repo-relative filenames, token names, and line numbers only; no source excerpts, binaries, private paths, runtime captures, screenshots, Ghidra project files, or mutation logs.",
        "whatIsProven": [
            "The selected source AugmentWeapon body anchors are present.",
            "The existing source-anchor evidence still classifies augmented weapon behavior as source-only pending retail-binary identity.",
            "The retail augmented HUD sample string has a current read-only Ghidra xref to 0x0040de40.",
            "The current 0x0040de40 decompile contains max-meter, active-flag, event-time, and HUD sample lookup/playback tokens.",
            "The current known caller xref is from CMonitor__Process, which keeps owner/name inference deliberately cautious.",
            "The caller context contains source-aligned threshold-call, meter-decay, and meter/active-reset tokens.",
        ],
        "notProven": [
            "Final owner/name/signature correctness for 0x0040de40.",
            "Exact full control-flow identity for every source AugmentWeapon statement.",
            "UnaugmentWeapon identity, meter decay, shield-damage meter gain, or weapon-fired stealth reset identity.",
            "Whether the retail compiler inlined or reorganized source AugmentWeapon/UnaugmentWeapon/update-loop methods.",
            "Runtime augmented-weapon behavior, HUD audio playback, projectile behavior, or stealth behavior.",
            "Ghidra rename-map mutation or read-back.",
            "Rebuildable open-source gameplay implementation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public-safe BattleEngine augmented weapon candidate read-back.")
    parser.add_argument("--check", action="store_true", help="run the candidate read-back probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    args = parser.parse_args()
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
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine augmented weapon candidate read-back probe")
        print(f"Status: {report['status']}")
        print(f"Checks: {report['checksPassed']}/{report['checksTotal']}")
        for result in report["results"]:
            print(f"- {result['status']}: {result['key']}: {result['file']}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
