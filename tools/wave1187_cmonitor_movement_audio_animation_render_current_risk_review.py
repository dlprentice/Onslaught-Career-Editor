#!/usr/bin/env python3
"""Validate Wave1187 CMonitor movement/audio/animation/render current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1187-cmonitor-movement-audio-animation-render-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1187-cmonitor-movement-audio-animation-render-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1187-cmonitor-movement-audio-animation-render-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1187_cmonitor_movement_audio_animation_render_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
APPLY_SCRIPT = ROOT / "tools" / "ApplyCMonitorMovementAudioAnimationRenderCurrentRiskWave1187.java"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-151617_post_wave1187_cmonitor_movement_audio_animation_render_current_risk_review_verified"

TARGETS = {
    "0x00409950": {
        "name": "CMonitor__UpdateSoundEventPlaybackForReader",
        "signature": "void __fastcall CMonitor__UpdateSoundEventPlaybackForReader(void * monitor)",
        "comment_tokens": (
            "Wave1187 static read-back",
            "CMonitor__Process",
            "0x0040963e",
            "CSoundManager",
            "monitor+0x5e8",
            "monitor+0x294",
            "monitor+0x5d0",
            "no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x0040963e", "UNCONDITIONAL_CALL")},
    },
    "0x00411630": {
        "name": "CMonitor__IntegrateMovementAgainstTerrain",
        "signature": "void __thiscall CMonitor__IntegrateMovementAgainstTerrain(void * this)",
        "comment_tokens": (
            "Wave1187 static read-back",
            "CMonitor__UpdateMovementTransitionAndEffects",
            "0x00410e08",
            "static-shadow/terrain height",
            "this+0x18",
            "vfunc +0x74",
            "heightfield-normal",
            "no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x00410e08", "UNCONDITIONAL_CALL")},
    },
    "0x00411aa0": {
        "name": "CMonitor__ComputeTerrainVelocityScalar",
        "signature": "float __thiscall CMonitor__ComputeTerrainVelocityScalar(void * this)",
        "comment_tokens": (
            "Wave1187 static read-back",
            "CMonitor__UpdateMovementTransitionAndEffects",
            "0x00411068",
            "static-shadow/terrain height",
            "DAT_006fbdfc",
            "0x005d8568",
            "0x005d8cc0",
            "vfunc +0x6c",
            "no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x00411068", "UNCONDITIONAL_CALL")},
    },
    "0x0044e2c0": {
        "name": "CMonitor__CheckSVFAnimationAndAdvanceState",
        "signature": "int __fastcall CMonitor__CheckSVFAnimationAndAdvanceState(void * monitor)",
        "comment_tokens": (
            "Wave1187 static read-back",
            "0x005e051c",
            "SVF",
            "CMesh__FindAnimationIndexByName",
            "vfunc +0x58",
            "vfunc byte offset +0x38",
            "no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x005e051c", "DATA")},
    },
    "0x0047d3b0": {
        "name": "CMonitor__TryQueuePrefireAnimation",
        "signature": "int __fastcall CMonitor__TryQueuePrefireAnimation(void * this)",
        "comment_tokens": (
            "Wave1187 static read-back",
            "CGroundVehicle vtable slot 86",
            "0x005e2ad4",
            "CUnit__UpdateDeployStateAndChargeEffects",
            "this+0x164",
            "this+0x164/+0x244",
            "prefire",
            "vfunc byte offset +0xf0",
            "no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x005e2ad4", "DATA")},
    },
    "0x005078f0": {
        "name": "CMonitor__UpdateTrackedRenderPair",
        "signature": "void __thiscall CMonitor__UpdateTrackedRenderPair(void * this, int update_projected_volume)",
        "comment_tokens": (
            "Wave1187 static read-back",
            "0x00410c81",
            "0x004137a6",
            "CBattleEngineWalkerPart__Move",
            "RET 0x4",
            "update_projected_volume",
            "this+0x18",
            "this+0x18/+0x20",
            "vfunc byte offset +300",
            "owner+0xa0",
            "owner+0xa0/+0x5c",
            "no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {
            ("0x00410c81", "UNCONDITIONAL_CALL"),
            ("0x004137a6", "UNCONDITIONAL_CALL"),
        },
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1187-cmonitor-movement-audio-animation-render-current-risk-review",
    "wave1187-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "monitor",
    "source-identity-deferred",
    "exact-layout-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1187",
    "wave1187-cmonitor-movement-audio-animation-render-current-risk-review",
    "793/1179 = 67.26%",
    "6 CMonitor movement/audio/animation/render current-risk rows",
    "current focused candidates: 1173",
    "live regenerated current focused candidates: 1173",
    "remaining active focused work: 386",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=6 skipped=0",
    "comment_only_updated=6",
    "tags_added=79",
    "final dry updated=0 skipped=6",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consult used",
    "no Cursor/Composer",
    "CMonitor__UpdateSoundEventPlaybackForReader",
    "CMonitor__IntegrateMovementAgainstTerrain",
    "CMonitor__ComputeTerrainVelocityScalar",
    "CMonitor__CheckSVFAnimationAndAdvanceState",
    "CMonitor__TryQueuePrefireAnimation",
    "CMonitor__UpdateTrackedRenderPair",
    "CMonitor__Process",
    "CMonitor__UpdateMovementTransitionAndEffects",
    "CBattleEngineWalkerPart__Move",
    "CUnit__UpdateDeployStateAndChargeEffects",
    "CSoundManager",
    "CStaticShadows__SampleShadowHeightBilinear",
    "CMesh__FindAnimationIndexByName",
    "SVF",
    "prefire",
    "update_projected_volume",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "7 xref rows",
    "914 instruction rows",
    "6 decompile rows",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
    "rebuild-grade specification",
)

OVERCLAIMS = (
    "runtime audio/gameplay behavior proven",
    "runtime movement/terrain behavior proven",
    "runtime animation/state behavior proven",
    "runtime firing animation behavior proven",
    "runtime render behavior proven",
    "exact source-body identity proven",
    "concrete monitor layouts proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 7,
        "pre-instructions.tsv": 914,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 7,
        "post-instructions.tsv": 914,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs_by_target: dict[str, set[tuple[str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs_by_target.setdefault(normalize(row["target_addr"]), set()).add((normalize(row["from_addr"]), row.get("ref_type", "")))

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata target {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"metadata name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"metadata signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in expected["comment_tokens"]:
                require(contains_token(comment, token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == expected["name"], f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(xrefs_by_target.get(address, set()) == expected["xref_set"], f"xref set mismatch at {address}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=79 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=79 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "rows=6 missing=0",
        "post-xrefs.log": "Wrote 7 rows",
        "post-instructions.log": "Wrote 914 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1187_queue_probe.log")
    require("Status: PASS" in queue_log, "queue probe did not pass", failures)
    export_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1187.log")
    require("total_functions=6411 commented_functions=6411" in export_log, "quality export count mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless queue mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined queue mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N queue mismatch", failures)

    quality_rows = {normalize(row["address"]): row for row in read_tsv(QUEUE_TSV)}
    for address, expected in TARGETS.items():
        row = quality_rows.get(address)
        require(row is not None, f"target missing from quality TSV {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"quality TSV name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"quality TSV signature mismatch at {address}", failures)
            require("Wave1187 static read-back" in row.get("comment", ""), f"quality TSV missing Wave1187 comment at {address}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176163719, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1187 CMonitor Movement / Audio / Animation / Render Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1187-cmonitor-movement-audio-animation-render-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    artifact_commit = str(latest.get("artifactCommit", ""))
    require(
        artifact_commit == "pending Wave1187 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", artifact_commit)),
        "latest artifact commit mismatch",
        failures,
    )
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 793, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "67.26%", "current focused percent mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1173, "live focused mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 386, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1187-cmonitor-movement-audio-animation-render-current-risk-review", "latest review tag mismatch", failures)
    target = progress.get("staticCompletionDefinition", {}).get("targetOutcome", "")
    require("no noticeable difference from the original game" in target, "static completion target outcome mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        MONITOR_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1187 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1187-cmonitor-movement-audio-animation-render-current-risk-review")
        == r"py -3 tools\wave1187_cmonitor_movement_audio_animation_render_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1187 apply script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1187 CMonitor movement/audio/animation/render current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1187 CMonitor movement/audio/animation/render current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
