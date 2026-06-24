#!/usr/bin/env python3
"""Validate Wave1060 DXCompass lifecycle review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1060-dxcompass-lifecycle-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dxcompass_lifecycle_review_wave1060_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1060_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXCOMPASS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXCompass.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-205027_post_wave1060_dxcompass_lifecycle_review_verified"

TARGETS = {
    "0x00406040": ("CDXCompass__GetTrackedPositionX", "double __fastcall CDXCompass__GetTrackedPositionX(void * context)"),
    "0x0040c630": ("CDXCompass__GetTrackedPositionY", "double __fastcall CDXCompass__GetTrackedPositionY(void * context)"),
    "0x004270e0": ("CDXCompass__InitMarkerArrays", "void __fastcall CDXCompass__InitMarkerArrays(void * this)"),
    "0x00427110": ("CDXCompass__LoadTextures", "void __fastcall CDXCompass__LoadTextures(void * this)"),
    "0x00427190": ("CDXCompass__DestroyTextures", "void __fastcall CDXCompass__DestroyTextures(void * this)"),
    "0x00427200": ("CDXCompass__Reset", "void __fastcall CDXCompass__Reset(void * this)"),
    "0x00427210": ("CDXCompass__Render", "void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)"),
    "0x0053be40": ("CDXCompass__Init", "void __fastcall CDXCompass__Init(void * this)"),
    "0x0053c1d0": (
        "CDXCompass__BuildRingGeometry",
        "void __cdecl CDXCompass__BuildRingGeometry(void * vertices, int textureWidth, int textureHeight, int segmentCount, int thicknessPercent, float uvScale)",
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "dxcompass-lifecycle-review-wave1060",
    "wave1060-readback-verified",
    "retail-binary-evidence",
    "tag-normalized",
    "comment-hardened",
    "signature-corrected",
    "dxcompass",
    "hud-render",
}

EXTRA_TAGS = {
    "0x00406040": {"tracked-position", "fpu-return", "context-0x4b0"},
    "0x0040c630": {"tracked-position", "fpu-return", "context-0x4b0"},
    "0x004270e0": {"marker-array", "init", "chud-owned"},
    "0x00427110": {"texture-load", "threat-flash", "damage-flash", "objective-marker"},
    "0x00427190": {"texture-release", "resource-lifetime", "chud-shutdown"},
    "0x00427200": {"reset", "state-flag", "chud-owned"},
    "0x00427210": {"compass-render", "battle-engine-context", "sprite-render"},
    "0x0053be40": {"resource-init", "ring-texture", "byte-sprite", "cvbuffer"},
    "0x0053c1d0": {"ring-geometry", "plain-helper", "vertex-strip"},
}

COMMENT_TOKENS = {
    "0x00406040": ("tracked-position X", "context +0x4b0", "+0x1c"),
    "0x0040c630": ("tracked-position Y", "context +0x4b0", "+0x20"),
    "0x004270e0": ("30-slot compass marker arrays", "this+0x3c24", "CDXCompass__Init"),
    "0x00427110": ("ThreatFlash", "DamageFlash", "CompassObjectiveMarker"),
    "0x00427190": ("four compass texture references", "texture+8", "CHud__ShutDown"),
    "0x00427200": ("compass render/state flag", "this+0x3c10"),
    "0x00427210": ("main compass render path", "CDXCompass__RenderWorldSpaceOverlay", "CFastVB"),
    "0x0053be40": ("compass render resources", "CByteSprite", "CVBuffers"),
    "0x0053c1d0": ("compass ring vertex strip", "sin/cos", "close the ring"),
}

DOC_TOKENS = (
    "Wave1060",
    "dxcompass-lifecycle-review-wave1060",
    "0x00406040 CDXCompass__GetTrackedPositionX",
    "0x0040c630 CDXCompass__GetTrackedPositionY",
    "0x004270e0 CDXCompass__InitMarkerArrays",
    "0x00427110 CDXCompass__LoadTextures",
    "0x00427190 CDXCompass__DestroyTextures",
    "0x00427200 CDXCompass__Reset",
    "0x00427210 CDXCompass__Render",
    "0x0053be40 CDXCompass__Init",
    "0x0053c1d0 CDXCompass__BuildRingGeometry",
    "812/1408 = 57.67%",
    "1148/1509 = 76.08%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "tag normalization",
)

OVERCLAIM_TOKENS = (
    "runtime compass behavior proven",
    "runtime hud rendering behavior proven",
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


def check_counts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 7,
        "primary-tags.tsv": 7,
        "primary-xrefs.tsv": 12,
        "primary-instructions.tsv": 731,
        "primary-decompile/index.tsv": 7,
        "context-metadata.tsv": 13,
        "context-tags.tsv": 13,
        "context-xrefs.tsv": 14,
        "context-instructions.tsv": 2339,
        "context-decompile/index.tsv": 13,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 15,
        "post-instructions.tsv": 1081,
        "post-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=7 found=7 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "primary-xrefs.log": "Wrote 12 rows",
        "primary-instructions.log": "Wrote 731 function-body instruction rows",
        "primary-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "context-metadata.log": "targets=13 found=13 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "context-xrefs.log": "Wrote 14 rows",
        "context-instructions.log": "Wrote 2339 function-body instruction rows",
        "context-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 15 rows",
        "post-instructions.log": "Wrote 1081 function-body instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 tags_added=110 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=9 skipped=0 tags_added=110 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 tags_added=0 missing=0 bad=0",
        "comment-fix-dry.log": "SUMMARY: updated=0 skipped=8 tags_added=0 comment_updated=1 missing=0 bad=0",
        "comment-fix.log": "SUMMARY: updated=1 skipped=8 tags_added=0 comment_updated=1 missing=0 bad=0",
        "comment-fix-final-dry.log": "SUMMARY: updated=0 skipped=9 tags_added=0 comment_updated=0 missing=0 bad=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "VERIFY_TAGS_FAIL", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_saved_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | EXTRA_TAGS[address]
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (174721927, 174721927.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    bad_undefined = sum(1 for row in rows if row.get("signature", "").startswith("undefined "))
    bad_param = sum(1 for row in rows if re.search(r"\bparam_\d+\b", row.get("signature", "")))
    require(len(rows) == 6246, "quality TSV row count mismatch", failures)
    require(commented == 6246, "quality TSV commented count mismatch", failures)
    require(bad_undefined == 0, "undefined signature count mismatch", failures)
    require(bad_param == 0, "param_N signature count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        DXCOMPASS_DOC,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-dxcompass-lifecycle-review-wave1060")
        == r"py -3 tools\ghidra_dxcompass_lifecycle_review_wave1060_probe.py --check",
        "missing Wave1060 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1060-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1060 --check",
        "missing Wave1060 aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1060 DXCompass lifecycle review" for row in ledger_rows), "missing Wave1060 ledger row", failures)
    require(any(row.get("task") == "Wave1060 DXCompass lifecycle review" for row in attempts), "missing Wave1060 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_logs(failures)
    check_saved_metadata(failures)
    check_backup_and_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1060 DXCompass lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1060 DXCompass lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
