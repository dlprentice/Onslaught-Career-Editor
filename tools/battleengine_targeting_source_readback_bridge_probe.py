#!/usr/bin/env python3
"""Validate the public-safe BattleEngine target-acquisition static bridge.

The probe binds pinned-source vocabulary to the reviewed retail correction and
the address-bound helper notes without promoting source-only helper names or
runtime behavior into accepted retail claims.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import battleengine_target_acquisition_static_contract as static_contract

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = (
    ROOT
    / "local-lab"
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
        "reviewed_handle_locks_correction",
        "reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json",
        (
            '"address": "0x00406560"',
            '"classification": "confirmed-apply"',
            '"correctedName": "CBattleEngine__HandleLocks"',
            '"correctedSignature": "void __fastcall CBattleEngine__HandleLocks(void * this)"',
        ),
        "The reviewed correction plan establishes the current 0x00406560 retail-static identity.",
    ),
    Check(
        "handle_locks_function_note",
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.md",
        (
            "CBattleEngine__HandleLocks",
            "lock-entry creation",
            "0x00406da0",
            "0x00406fc0",
            "hypothesis-only",
        ),
        "The retained legacy-path note documents current HandleLocks structure and dependent-helper boundaries.",
    ),
    Check(
        "forward_candidate_function_note",
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__SelectNearestForwardTargetFromGlobalSet.md",
        (
            "CBattleEngine::GetClosestLockableUnit",
            "hypothesis-only",
            "global candidate set",
            "nearest retained candidate",
            "forward-deflection",
        ),
        "The forward-candidate note preserves retail structure while keeping the stronger source name hypothetical.",
    ),
    Check(
        "lock_entry_function_note",
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__AddProjectile.md",
        (
            "Saved Ghidra name",
            "lock-entry creation",
            "CBattleEngine::StartLock",
            "hypothesis-only",
        ),
        "The dependent-helper note records lock-entry structure without accepting its source name or old projectile semantics.",
    ),
    Check(
        "target_acquisition_static_contract",
        "reverse-engineering/game-mechanics/battleengine-target-acquisition-static-contract-v1.md",
        (
            "battleengine-target-acquisition-static-contract.v1",
            "reviewed-retail-static",
            "saved-retail-structure",
            "pinned-source-hypothesis",
            "runtime-required",
            "CBattleEngine__HandleLocks",
            "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
            "CBattleEngine__AddProjectile",
            "runtime target choice",
            "Core behavior",
        ),
        "The accepted static contract records evidence classes, current address anchors, and explicit runtime/Core non-claims.",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def text_hits(text: str, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    lines = text.splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def line_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    return text_hits(path.read_text(encoding="utf-8", errors="replace"), tokens)


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

    if check.key == "source_target_lock_anchor":
        try:
            revision = static_contract._source_revision(path.parent)
            if revision != static_contract.SOURCE_PIN:
                raise static_contract.ContractError(
                    f"source revision mismatch: expected {static_contract.SOURCE_PIN}, got {revision}"
                )
            source_text = static_contract._source_text_at_revision(
                path.parent, static_contract.SOURCE_PIN, "BattleEngine.cpp"
            )
        except static_contract.ContractError as exc:
            return {
                "key": check.key,
                "status": "FAIL",
                "file": relative(path),
                "summary": f"{check.summary} Pinned source check failed: {exc}",
                "tokenLineHits": {token: [] for token in check.tokens},
                "missingTokens": list(check.tokens),
            }
        hits = text_hits(source_text, check.tokens)
    else:
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
        "privacy": "Report stores repo-relative filenames, selected public source-anchor expressions, token names, and line numbers only; no bulk source excerpts, binaries, private paths, runtime captures, screenshots, or Ghidra mutation logs.",
        "whatIsProven": [
            "Selected Stuart source target-lock anchors are present.",
            "The reviewed correction establishes CBattleEngine__HandleLocks at 0x00406560.",
            "The address-bound candidate and lock-entry helper roles and ordering are documented.",
            "The stronger helper source names remain pinned-source hypotheses.",
        ],
        "notProven": [
            "Runtime target choice, lock timing, or gameplay outcomes.",
            "Exact source identity for the helpers at 0x00406da0 and 0x00406fc0.",
            "Ghidra rename-map mutation or read-back.",
            "Core or Godot gameplay implementation.",
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
        out.resolve().relative_to((ROOT / "local-lab").resolve())
    except ValueError:
        print(f"Refusing to write report outside local-lab/: {out}")
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
