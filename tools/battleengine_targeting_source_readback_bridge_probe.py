#!/usr/bin/env python3
"""Validate a public-safe bridge between BattleEngine targeting source anchors and retail helper read-back.

This probe checks selected Stuart source targeting/stealth-lock anchors and the
existing retail helper read-back/function notes. It deliberately keeps the claim
bounded: related target-selection and projectile helper evidence exists, but
exact source-to-retail control-flow identity and runtime target choice remain
unproven.
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
    / "battleengine-targeting-source-readback-bridge"
    / "current"
    / "battleengine-targeting-source-readback-bridge.json"
)


@dataclass(frozen=True)
class Check:
    key: str
    file: str
    tokens: tuple[str, ...]
    summary: str


CHECKS: tuple[Check, ...] = (
    Check(
        "source_target_lock_anchor",
        "references/Onslaught/BattleEngine.cpp",
        (
            "void    CBattleEngine::HandleLocks()",
            "weapon->ReadyToFire()",
            "case kDirectLockMode",
            "case kProximityLockMode",
            "case kSequenceLockMode",
            "CountLocks()>=weapon->GetMaxLocks()",
            "magnitudeSq=weapon->GetLockRange()*(1.0f-unit->GetStealth()/100.0f)",
            "StartLock(unit,weapon->GetLockTime(),TRUE)",
        ),
        "Stuart source target-lock logic checks readiness, lock caps, lock modes, stealth-adjusted range, and direct-lock starts.",
    ),
    Check(
        "source_coverage_and_gap_evidence",
        "release/readiness/battleengine_locking_source_anchor_2026-05-07.md",
        (
            "target_lock_modes_and_stealth_range",
            "partial retail candidate pending exact identity",
            "source anchors `17/17`",
            "source-only pending binary identity `15`",
        ),
        "Source-anchor evidence records target locking as a partial retail candidate while keeping exact identity unresolved.",
    ),
    Check(
        "helper_readback_evidence",
        "release/readiness/battleengine_helper_ghidra_readback_2026-05-06.md",
        (
            "`CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`",
            "`CBattleEngine__SelectNearestForwardTargetFromGlobalSet`",
            "target-resolution and projectile emission call-chain",
            "profile/list traversal and target-mask tokens",
        ),
        "Fresh helper read-back evidence records target/projectile and forward-target helper tokens.",
    ),
    Check(
        "auto_target_function_note",
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.md",
        (
            "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
            "CBattleEngine__AddProjectile",
            "target-selection state",
            "projectile emission",
            "does not prove the full runtime firing model",
        ),
        "Function note documents the auto-target/projectile helper without overclaiming runtime firing behavior.",
    ),
    Check(
        "forward_target_function_note",
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__SelectNearestForwardTargetFromGlobalSet.md",
        (
            "Target-selection helper",
            "profile/mode/mask checks",
            "CSPtrSet__First",
            "CSPtrSet__Next",
            "runtime target-choice behavior remains unproven",
        ),
        "Function note documents the forward-target helper while keeping runtime semantic target choice unproven.",
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
    failures = [item for item in results if item["status"] != "PASS"]
    return {
        "schema": "battleengine-targeting-source-readback-bridge.v1",
        "status": "pass" if not failures else "blocked",
        "checksPassed": len(results) - len(failures),
        "checksTotal": len(results),
        "results": results,
        "privacy": "Report stores repo-relative filenames, token names, and line numbers only; no source excerpts, binaries, private paths, runtime captures, screenshots, or Ghidra mutation logs.",
        "whatIsProven": [
            "Selected Stuart source target-lock anchors are present.",
            "Public source-anchor evidence records target locking as source-only pending binary identity.",
            "Existing retail helper read-back evidence records selected target/projectile helper tokens.",
            "The current function notes document related target/projectile helpers without claiming runtime target choice.",
        ],
        "notProven": [
            "Exact `CBattleEngine::HandleLocks` to retail helper control-flow identity.",
            "Target choice, lock acquisition, or projectile behavior in a running copied-profile mission.",
            "Runtime gameplay-state interpretation.",
            "Ghidra rename-map mutation or read-back.",
            "Rebuildable open-source gameplay implementation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public-safe BattleEngine targeting source/read-back bridge.")
    parser.add_argument("--check", action="store_true", help="run the bridge probe")
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
        print("BattleEngine targeting source/read-back bridge probe")
        print(f"Status: {report['status']}")
        print(f"Checks: {report['checksPassed']}/{report['checksTotal']}")
        for result in report["results"]:
            print(f"- {result['status']}: {result['key']}: {result['file']}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
