#!/usr/bin/env python3
"""Validate Wave948 BattleEngine transition/effects read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave948-battleengine-transition-effects-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_transition_effects_review_wave948_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
JETPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineJetPart.cpp" / "_index.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260528-073152_post_wave948_battleengine_transition_effects_review_verified"
SCRIPT_NAME = "test:ghidra-battleengine-transition-effects-review-wave948"
SCRIPT_VALUE = r"py -3 tools\ghidra_battleengine_transition_effects_review_wave948_probe.py --check"

TARGETS = {
    "0x0040eeb0": (
        "CBattleEngine__FinishedPlayingCurrentAnimation",
        "int __thiscall CBattleEngine__FinishedPlayingCurrentAnimation(void * this)",
        ("flytowalk", "walktofly", "CUnit owner"),
    ),
    "0x0040ef20": (
        "CBattleEngine__GroundParticleEffect",
        "void __thiscall CBattleEngine__GroundParticleEffect(void * this)",
        ("water/terrain", "this+0x1c..0x28", "CMonitor"),
    ),
    "0x00410c50": (
        "CMonitor__UpdateMovementTransitionAndEffects",
        "void __fastcall CMonitor__UpdateMovementTransitionAndEffects(void * monitor)",
        ("CMonitor__Process", "CMonitor__UpdateTrackedRenderPair", "CMonitor__SpawnGroundOrAirImpactEffect"),
    ),
    "0x004124d0": (
        "CBattleEngineJetPart__GetCurrentWeaponNameField04",
        "char * __thiscall CBattleEngineJetPart__GetCurrentWeaponNameField04(void * this)",
        ("CBattleEngine__ChangeWeapon", "+0x57c", "field +0x04"),
    ),
}

CONTEXT = {
    "0x004081c0": ("CMonitor__Process", "void __fastcall CMonitor__Process(void * monitor)"),
    "0x00409f70": ("CBattleEngine__ChangeWeapon", "void __fastcall CBattleEngine__ChangeWeapon(void * battleEngine)"),
    "0x0040a580": ("CBattleEngine__Morph", "void __fastcall CBattleEngine__Morph(void * battleEngine)"),
    "0x0040dcc0": ("CBattleEngine__ClearFlag58CAndMorphIfState3", "void __thiscall CBattleEngine__ClearFlag58CAndMorphIfState3(void * this)"),
    "0x0040de40": ("CBattleEngine__AugmentWeapon", "void __thiscall CBattleEngine__AugmentWeapon(void * this)"),
    "0x00411b70": ("CBattleEngineJetPart__IsStateMachineActive", "int __thiscall CBattleEngineJetPart__IsStateMachineActive(void * this)"),
    "0x00411e70": ("CBattleEngineJetPart__ChangeWeapon", "void __thiscall CBattleEngineJetPart__ChangeWeapon(void * this)"),
    "0x00412520": ("CBattleEngineJetPart__GetWeaponIconName", "char * __thiscall CBattleEngineJetPart__GetWeaponIconName(void * this)"),
    "0x00412570": ("CBattleEngineJetPart__CanWeaponFire", "int __thiscall CBattleEngineJetPart__CanWeaponFire(void * this)"),
    "0x00412610": ("CBattleEngineJetPart__GetCurrentWeapon", "void * __thiscall CBattleEngineJetPart__GetCurrentWeapon(void * this)"),
    "0x00424920": ("CGeneralVolume__BeginFlyToWalkTransition", "void __fastcall CGeneralVolume__BeginFlyToWalkTransition(void * this)"),
    "0x00424990": ("CGeneralVolume__BeginWalkToFlyTransition", "void __fastcall CGeneralVolume__BeginWalkToFlyTransition(void * this)"),
    "0x005078f0": ("CMonitor__UpdateTrackedRenderPair", "void __thiscall CMonitor__UpdateTrackedRenderPair(void * this, int update_projected_volume)"),
}

EXPECTED_XREFS = {
    ("0x0040eeb0", "0x005d8ab0", "<no_function>", "DATA"),
    ("0x0040ef20", "0x0040971e", "CMonitor__Process", "UNCONDITIONAL_CALL"),
    ("0x0040ef20", "0x004114b6", "CMonitor__UpdateMovementTransitionAndEffects", "UNCONDITIONAL_CALL"),
    ("0x00410c50", "0x00408d61", "CMonitor__Process", "UNCONDITIONAL_CALL"),
    ("0x004124d0", "0x0040a001", "CBattleEngine__ChangeWeapon", "UNCONDITIONAL_CALL"),
}

EXPECTED_CONTEXT_XREFS = {
    ("0x0040a580", "0x00408d70", "CMonitor__Process", "UNCONDITIONAL_CALL"),
    ("0x0040a580", "0x00410df9", "CMonitor__UpdateMovementTransitionAndEffects", "UNCONDITIONAL_CALL"),
    ("0x0040a580", "0x00411228", "CMonitor__UpdateMovementTransitionAndEffects", "UNCONDITIONAL_CALL"),
    ("0x0040de40", "0x00408582", "CMonitor__Process", "UNCONDITIONAL_CALL"),
    ("0x00411b70", "0x0040a5bf", "CBattleEngine__Morph", "UNCONDITIONAL_CALL"),
    ("0x00411e70", "0x00409fd3", "CBattleEngine__ChangeWeapon", "UNCONDITIONAL_CALL"),
    ("0x00412520", "0x0040c5aa", "CBattleEngine__GetWeaponIconName", "UNCONDITIONAL_CALL"),
    ("0x00412610", "0x004065ac", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("0x00424920", "0x0040a663", "CBattleEngine__Morph", "UNCONDITIONAL_CALL"),
    ("0x00424990", "0x0040a74c", "CBattleEngine__Morph", "UNCONDITIONAL_CALL"),
    ("0x005078f0", "0x00410c81", "CMonitor__UpdateMovementTransitionAndEffects", "UNCONDITIONAL_CALL"),
}

DECOMPILE_TOKENS = {
    "decompile/0040eeb0_CBattleEngine__FinishedPlayingCurrentAnimation.c": ("flytowalk", "walktofly", "CMesh__FindAnimationIndexByName"),
    "decompile/0040ef20_CBattleEngine__GroundParticleEffect.c": ("CStaticShadows__SampleShadowHeightBilinear", "CParticleManager__CreateEffect", "0x1c", "0x24", "0x28"),
    "decompile/00410c50_CMonitor__UpdateMovementTransitionAndEffects.c": ("CMonitor__UpdateTrackedRenderPair", "CBattleEngine__Morph", "CMonitor__IntegrateMovementAgainstTerrain", "CBattleEngine__GroundParticleEffect"),
    "decompile/004124d0_CBattleEngineJetPart__GetCurrentWeaponNameField04.c": ("0xa4", "return *(char **)(*(int *)(iVar2 + 0xa4) + 4)", "0x10"),
    "context-decompile/00409f70_CBattleEngine__ChangeWeapon.c": ("CBattleEngineJetPart__GetCurrentWeaponNameField04", "0x57c", "s_hud__s_00623314"),
    "context-decompile/0040a580_CBattleEngine__Morph.c": ("CBattleEngineJetPart__IsStateMachineActive", "CGeneralVolume__BeginFlyToWalkTransition", "CGeneralVolume__BeginWalkToFlyTransition"),
}

CORE_TOKENS = (
    "Wave948",
    "battleengine-transition-effects-review-wave948",
    "0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation",
    "0x0040ef20 CBattleEngine__GroundParticleEffect",
    "0x00410c50 CMonitor__UpdateMovementTransitionAndEffects",
    "0x004124d0 CBattleEngineJetPart__GetCurrentWeaponNameField04",
    "0x00409f70 CBattleEngine__ChangeWeapon",
    "0x0040a580 CBattleEngine__Morph",
    "0x00411e70 CBattleEngineJetPart__ChangeWeapon",
    "0x005078f0 CMonitor__UpdateTrackedRenderPair",
    "247/1408 = 17.54%",
    "6150/6150 = 100.00%",
    BACKUP,
    "no mutation",
)

OVERCLAIMS = (
    "runtime morph behavior proven",
    "runtime particle behavior proven",
    "runtime weapon switching proven",
    "runtime hud audio behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalized(addr: str) -> str:
    value = (addr or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    if token in text or token.replace("\\", "\\\\") in text:
        return True
    lower = text.lower()
    return token.lower() in lower or token.replace("\\", "\\\\").lower() in lower


def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str]:
    want = normalized(addr)
    for row in rows:
        got = row.get("address") or row.get("target_addr") or row.get("function_entry") or ""
        if normalized(got) == want:
            return row
    return {}


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 4,
        "tags.tsv": 4,
        "xrefs.tsv": 5,
        "instructions.tsv": 860,
        "decompile/index.tsv": 4,
        "context-metadata.tsv": 13,
        "context-tags.tsv": 13,
        "context-xrefs.tsv": 21,
        "context-instructions.tsv": 2818,
        "context-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=4 found=4 missing=0",
        "tags.log": "rows=4 missing=0",
        "xrefs.log": "Wrote 5 rows",
        "instructions.log": "Wrote 860 function-body instruction rows",
        "decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "context-metadata.log": "targets=13 found=13 missing=0",
        "context-tags.log": "rows=13 missing=0",
        "context-xrefs.log": "Wrote 21 rows",
        "context-instructions.log": "Wrote 2818 function-body instruction rows",
        "context-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR:", "MISSING:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    decomp = read_tsv(BASE / "decompile" / "index.tsv")
    context_metadata = read_tsv(BASE / "context-metadata.tsv")
    context_tags = read_tsv(BASE / "context-tags.tsv")
    context_decomp = read_tsv(BASE / "context-decompile" / "index.tsv")

    for addr, (name, signature, comment_tokens) in TARGETS.items():
        row = row_by_addr(metadata, addr)
        require(row.get("name") == name, f"metadata name mismatch for {addr}", failures)
        require(row.get("signature") == signature, f"metadata signature mismatch for {addr}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch for {addr}", failures)
        for token in comment_tokens:
            require(token in row.get("comment", ""), f"missing comment token for {addr}: {token}", failures)
        require(row_by_addr(tags, addr).get("status") == "OK", f"tag status mismatch for {addr}", failures)
        drow = row_by_addr(decomp, addr)
        require(drow.get("name") == name, f"decompile name mismatch for {addr}", failures)
        require(drow.get("signature") == signature, f"decompile signature mismatch for {addr}", failures)
        require(drow.get("status") == "OK", f"decompile status mismatch for {addr}", failures)

    for addr, (name, signature) in CONTEXT.items():
        row = row_by_addr(context_metadata, addr)
        require(row.get("name") == name, f"context name mismatch for {addr}", failures)
        require(row.get("signature") == signature, f"context signature mismatch for {addr}", failures)
        require(row.get("status") == "OK", f"context metadata status mismatch for {addr}", failures)
        require(row_by_addr(context_tags, addr).get("status") == "OK", f"context tag status mismatch for {addr}", failures)
        drow = row_by_addr(context_decomp, addr)
        require(drow.get("name") == name, f"context decompile name mismatch for {addr}", failures)
        require(drow.get("signature") == signature, f"context decompile signature mismatch for {addr}", failures)
        require(drow.get("status") == "OK", f"context decompile status mismatch for {addr}", failures)


def check_xrefs(failures: list[str]) -> None:
    actual = {
        (normalized(row.get("target_addr", "")), normalized(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", ""))
        for row in read_tsv(BASE / "xrefs.tsv")
    }
    for target, source, source_fn, ref_type in EXPECTED_XREFS:
        require((normalized(target), normalized(source), source_fn, ref_type) in actual, f"xref mismatch for {target} from {source}", failures)

    context_actual = {
        (normalized(row.get("target_addr", "")), normalized(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", ""))
        for row in read_tsv(BASE / "context-xrefs.tsv")
    }
    for target, source, source_fn, ref_type in EXPECTED_CONTEXT_XREFS:
        require((normalized(target), normalized(source), source_fn, ref_type) in context_actual, f"context xref mismatch for {target} from {source}", failures)


def check_decompile_tokens(failures: list[str]) -> None:
    for relative, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token in {relative}: {token}", failures)


def check_docs_and_summary(failures: list[str]) -> None:
    summary = json.loads(read_text(BASE / "wave948-battleengine-transition-effects-review.json") or "{}")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")

    require(summary.get("selectedTargets") == 4, "summary selected target mismatch", failures)
    require(summary.get("contextTargets") == 13, "summary context target mismatch", failures)
    require(summary.get("mutatedTargets") == 0, "summary mutation mismatch", failures)
    require(summary.get("focusedReauditProgressAfter") == "247/1408 = 17.54%", "summary progress mismatch", failures)
    require(summary.get("staticExportContractClosure") == "6150/6150 = 100.00%", "summary closure mismatch", failures)
    require(summary.get("backup") == BACKUP, "summary backup mismatch", failures)

    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    broad_docs = [NOTE, CAMPAIGN, BATTLEENGINE_DOC, *STATE_FILES]
    for path in broad_docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scoped_docs = {
        JETPART_DOC: (
            "Wave948",
            "battleengine-transition-effects-review-wave948",
            "0x004124d0 CBattleEngineJetPart__GetCurrentWeaponNameField04",
            "0x00409f70 CBattleEngine__ChangeWeapon",
            "0x00411e70 CBattleEngineJetPart__ChangeWeapon",
            "247/1408 = 17.54%",
            "6150/6150 = 100.00%",
            BACKUP,
            "no mutation",
        ),
        MONITOR_DOC: (
            "Wave948",
            "battleengine-transition-effects-review-wave948",
            "0x00410c50 CMonitor__UpdateMovementTransitionAndEffects",
            "0x004081c0 CMonitor__Process",
            "0x0040a580 CBattleEngine__Morph",
            "0x0040ef20 CBattleEngine__GroundParticleEffect",
            "0x005078f0 CMonitor__UpdateTrackedRenderPair",
            "247/1408 = 17.54%",
            "6150/6150 = 100.00%",
            BACKUP,
            "no mutation",
        ),
    }
    for path, tokens in scoped_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = json.loads(read_text(PACKAGE_JSON) or "{}")
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "package script mismatch", failures)


def build_report() -> dict[str, object]:
    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata(failures)
    check_xrefs(failures)
    check_decompile_tokens(failures)
    check_docs_and_summary(failures)
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "counts": {
            "metadata": len(read_tsv(BASE / "metadata.tsv")),
            "xrefs": len(read_tsv(BASE / "xrefs.tsv")),
            "instructions": len(read_tsv(BASE / "instructions.tsv")),
            "decompile": len(read_tsv(BASE / "decompile" / "index.tsv")),
            "contextMetadata": len(read_tsv(BASE / "context-metadata.tsv")),
            "contextInstructions": len(read_tsv(BASE / "context-instructions.tsv")),
            "contextDecompile": len(read_tsv(BASE / "context-decompile" / "index.tsv")),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    report = build_report()
    report_path = BASE / "wave948-probe-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Ghidra Wave948 BattleEngine transition/effects review probe")
    print(f"Status: {report['status']}")
    print(f"Output: {report_path.relative_to(ROOT)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
