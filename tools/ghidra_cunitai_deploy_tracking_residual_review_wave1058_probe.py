#!/usr/bin/env python3
"""Validate Wave1058 CUnitAI deploy-tracking residual review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1058-cunitai-deploy-tracking-residual-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cunitai_deploy_tracking_residual_review_wave1058_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1058_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GENERAL_VOLUME_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md"
UNIT_AI_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
BATTLE_ENGINE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
COCKPIT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Cockpit.cpp" / "_index.md"
MATH_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-192010_post_wave1058_cunitai_deploy_tracking_residual_review_verified"

TARGETS = {
    "0x004247a0": ("CGeneralVolume__InitRandomizedVelocityOffsets", "void __thiscall CGeneralVolume__InitRandomizedVelocityOffsets(void * this, int randomRange)"),
    "0x00424a20": ("CUnitAI__UpdateDeployAimAndScheduleEvent", "void __fastcall CUnitAI__UpdateDeployAimAndScheduleEvent(void * this)"),
    "0x00424be0": ("CUnitAI__AdvanceDeployAnimationPhase", "void __fastcall CUnitAI__AdvanceDeployAnimationPhase(void * this)"),
    "0x00424ca0": ("CUnitAI__UpdateDeployTrackingTransformTowardTarget", "void __fastcall CUnitAI__UpdateDeployTrackingTransformTowardTarget(void * this)"),
    "0x004250f0": ("CUnitAI__DecayDeployTrackingTransformToNeutral", "void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(void * this)"),
}

CONTEXT_TAGGED = {
    "0x004244b0": ("CCockpit__ctor", "void * __thiscall CCockpit__ctor(void * this, void * battleEngine)"),
    "0x00424920": ("CGeneralVolume__BeginFlyToWalkTransition", "void __fastcall CGeneralVolume__BeginFlyToWalkTransition(void * this)"),
    "0x00424990": ("CGeneralVolume__BeginWalkToFlyTransition", "void __fastcall CGeneralVolume__BeginWalkToFlyTransition(void * this)"),
    "0x0040a580": ("CBattleEngine__Morph", "void __fastcall CBattleEngine__Morph(void * battleEngine)"),
    "0x0040eeb0": ("CBattleEngine__FinishedPlayingCurrentAnimation", "int __thiscall CBattleEngine__FinishedPlayingCurrentAnimation(void * this)"),
    "0x00425760": ("Mat34__OrthonormalizeAxes", "void __fastcall Mat34__OrthonormalizeAxes(void * mat34)"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cunitai-deploy-tracking-residual-review-wave1058",
    "wave1058-readback-verified",
    "retail-binary-evidence",
    "tag-normalized",
    "comment-hardened",
}

EXTRA_TAGS = {
    "0x004247a0": {"generalvolume", "randomized-offsets", "deploy-tracking-context"},
    "0x00424a20": {"unit-ai", "deploy-tracking", "deploy-animation", "event-scheduler"},
    "0x00424be0": {"unit-ai", "deploy-tracking", "deploy-animation", "phase-advance"},
    "0x00424ca0": {"unit-ai", "deploy-tracking", "target-tracking", "transform-update"},
    "0x004250f0": {"unit-ai", "deploy-tracking", "neutral-decay", "transform-update"},
    "0x004244b0": {"cockpit", "constructor", "battleengine-init-context"},
    "0x00424920": {"generalvolume", "morph-transition", "flytowalk"},
    "0x00424990": {"generalvolume", "morph-transition", "walktofly"},
    "0x0040a580": {"battleengine", "morph-transition", "source-shape-evidence"},
    "0x0040eeb0": {"battleengine", "animation-transition", "source-shape-evidence"},
    "0x00425760": {"math", "mat34", "owner-neutral"},
}

DOC_TOKENS = (
    "Wave1058",
    "cunitai-deploy-tracking-residual-review-wave1058",
    "0x004247a0 CGeneralVolume__InitRandomizedVelocityOffsets",
    "0x00424a20 CUnitAI__UpdateDeployAimAndScheduleEvent",
    "0x00424be0 CUnitAI__AdvanceDeployAnimationPhase",
    "0x00424ca0 CUnitAI__UpdateDeployTrackingTransformTowardTarget",
    "0x004250f0 CUnitAI__DecayDeployTrackingTransformToNeutral",
    "0x004244b0 CCockpit__ctor",
    "0x00424920 CGeneralVolume__BeginFlyToWalkTransition",
    "0x00424990 CGeneralVolume__BeginWalkToFlyTransition",
    "0x0040a580 CBattleEngine__Morph",
    "0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation",
    "0x00425760 Mat34__OrthonormalizeAxes",
    "804/1408 = 57.10%",
    "1132/1509 = 75.02%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "tag normalization",
)

OVERCLAIM_TOKENS = (
    "runtime deploy behavior proven",
    "runtime morph behavior proven",
    "fully reverse-engineered runtime",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def rows_by_address(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row[key]): row for row in read_tsv(path)}


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 5,
        "instructions.tsv": 802,
        "decompile/index.tsv": 5,
        "context-metadata.tsv": 10,
        "context-tags.tsv": 10,
        "context-xrefs.tsv": 53,
        "context-instructions.tsv": 915,
        "context-decompile/index.tsv": 10,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 5,
        "post-instructions.tsv": 802,
        "post-decompile/index.tsv": 5,
        "post-context-metadata.tsv": 10,
        "post-context-tags.tsv": 10,
        "post-context-xrefs.tsv": 53,
        "post-context-instructions.tsv": 915,
        "post-context-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = rows_by_address(BASE / "post-metadata.tsv")
    context_metadata = rows_by_address(BASE / "post-context-metadata.tsv")
    tags = rows_by_address(BASE / "post-tags.tsv")
    context_tags = rows_by_address(BASE / "post-context-tags.tsv")

    for address, (name, signature) in {**TARGETS, **CONTEXT_TAGGED}.items():
        row = metadata.get(address) or context_metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)

        tag_row = tags.get(address) or context_tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            expected = COMMON_TAGS | EXTRA_TAGS[address]
            require(expected.issubset(actual), f"missing tags at {address}: {sorted(expected - actual)}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 tags_added=103 missing=0 bad=0",
        "apply-first-explicit-save-error.log": "SUMMARY: updated=11 skipped=0 tags_added=103 missing=0 bad=0",
        "apply-clean-noop.log": "SUMMARY: updated=0 skipped=11 tags_added=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 5 rows",
        "post-instructions.log": "Wrote 802 function-body instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-context-xrefs.log": "Wrote 53 rows",
        "post-context-instructions.log": "Wrote 915 function-body instruction rows",
        "post-context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative == "apply-first-explicit-save-error.log":
            require("Unable to lock due to active transaction" in text, "missing expected first-apply save-call error", failures)
            continue
        for bad in ("LockException", "SCRIPT ERROR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "VERIFY_MISSING", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6246, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless row", failures)
    require(not any(row.get("signature", "").startswith("undefined ") for row in rows), "quality TSV has undefined signature", failures)
    require(not any(re.search(r"\bparam_\d+\b", row.get("signature", "")) for row in rows), "quality TSV has param_N signature", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174656391 or backup.get("totalBytes") == 174656391.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        BACKLOG,
        TRACKING_STATE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        GENERAL_VOLUME_INDEX: (
            "Wave1058",
            "cunitai-deploy-tracking-residual-review-wave1058",
            "0x004247a0 CGeneralVolume__InitRandomizedVelocityOffsets",
            "0x00424920 CGeneralVolume__BeginFlyToWalkTransition",
            "0x00424990 CGeneralVolume__BeginWalkToFlyTransition",
            BACKUP_PATH,
            "tag normalization",
        ),
        UNIT_AI_INDEX: (
            "Wave1058",
            "cunitai-deploy-tracking-residual-review-wave1058",
            "0x00424a20 CUnitAI__UpdateDeployAimAndScheduleEvent",
            "0x00424be0 CUnitAI__AdvanceDeployAnimationPhase",
            "0x00424ca0 CUnitAI__UpdateDeployTrackingTransformTowardTarget",
            "0x004250f0 CUnitAI__DecayDeployTrackingTransformToNeutral",
            BACKUP_PATH,
            "tag normalization",
        ),
        BATTLE_ENGINE_INDEX: (
            "Wave1058",
            "cunitai-deploy-tracking-residual-review-wave1058",
            "0x0040a580 CBattleEngine__Morph",
            "0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation",
            BACKUP_PATH,
            "tag normalization",
        ),
        COCKPIT_INDEX: (
            "Wave1058",
            "cunitai-deploy-tracking-residual-review-wave1058",
            "0x004244b0 CCockpit__ctor",
            BACKUP_PATH,
            "tag normalization",
        ),
        MATH_INDEX: (
            "Wave1058",
            "cunitai-deploy-tracking-residual-review-wave1058",
            "0x00425760 Mat34__OrthonormalizeAxes",
            BACKUP_PATH,
            "tag normalization",
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cunitai-deploy-tracking-residual-review-wave1058")
        == r"py -3 tools\ghidra_cunitai_deploy_tracking_residual_review_wave1058_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1058-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1058 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1058 cunitai deploy tracking residual review" for row in ledger_rows), "missing Wave1058 ledger row", failures)
    require(
        any(row.get("task") == "Wave1058 cunitai deploy tracking residual review" and row.get("attempt_id") == 20640 for row in attempts),
        "missing Wave1058 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1058 CUnitAI deploy-tracking residual probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1058 CUnitAI deploy-tracking residual probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
