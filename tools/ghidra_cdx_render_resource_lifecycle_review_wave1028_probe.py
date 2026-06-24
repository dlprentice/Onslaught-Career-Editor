#!/usr/bin/env python3
"""Validate Wave1028 CDX render-resource lifecycle read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1028-cdx-render-resource-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cdx_render_resource_lifecycle_review_wave1028_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1028_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
DXMESHVBB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
DXMEMBUFFER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMemBuffer.cpp.md"
DXSURF_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXSurf.cpp.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-021726_post_wave1028_cdx_render_resource_lifecycle_review_verified"

TARGETS = {
    "0x0054bff0": (
        "CDXMeshVB__scalar_deleting_dtor",
        "void * __thiscall CDXMeshVB__scalar_deleting_dtor(void * this, byte flags)",
        ("CDXMeshVB lifecycle", "CDXMeshVB__dtor_base", "flags&1"),
    ),
    "0x0054c010": (
        "CDXMeshVB__dtor_base",
        "void __thiscall CDXMeshVB__dtor_base(void * this)",
        ("CDXMeshVB lifecycle", "CDXMeshVB__ReleaseResources", "+0x124"),
    ),
    "0x00547d70": (
        "CDXMemBuffer__ctor",
        "void * __fastcall CDXMemBuffer__ctor(void * this)",
        ("CDXMemBuffer constructor", "CChunkReader", "stale CChunker"),
    ),
    "0x004f2790": (
        "CDXSurf__UnlinkNodeFromGlobalList",
        "void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)",
        ("CDXSurf__UnlinkNodeFromGlobalList", "DAT_0083d9b0", "texture_base-0x08"),
    ),
    "0x00527de0": (
        "CWaterRenderSystem__ResetAndMarkSourceFlag",
        "void __fastcall CWaterRenderSystem__ResetAndMarkSourceFlag(void * validation_record)",
        ("Wave861 static read-back", "DAT_00854dd8", "DAT_00854dd9"),
    ),
}

CONTEXT_TARGETS = {
    "0x0054bf80": "CDXMeshVB__ctor",
    "0x0054d3f0": "CDXMeshVB__ReleaseResources",
    "0x00548570": "CDXMemBuffer__Read",
    "0x004f2710": "CTextureBase__Init",
    "0x0053e2e0": "CDXEngine__Render",
}

DOC_TOKENS = (
    "Wave1028",
    "cdx-render-resource-lifecycle-review-wave1028",
    "0x0054bff0 CDXMeshVB__scalar_deleting_dtor",
    "0x0054c010 CDXMeshVB__dtor_base",
    "0x00547d70 CDXMemBuffer__ctor",
    "0x004f2790 CDXSurf__UnlinkNodeFromGlobalList",
    "0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag",
    "605/1408 = 42.97%",
    "834/1493 = 55.86%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    DXMESHVBB_DOC: ("Wave1028", "cdx-render-resource-lifecycle-review-wave1028", "0x0054bff0 CDXMeshVB__scalar_deleting_dtor", "0x0054c010 CDXMeshVB__dtor_base", BACKUP_PATH),
    DXMEMBUFFER_DOC: ("Wave1028", "cdx-render-resource-lifecycle-review-wave1028", "0x00547d70 CDXMemBuffer__ctor", "0x00548570 CDXMemBuffer__Read", BACKUP_PATH),
    DXSURF_DOC: ("Wave1028", "cdx-render-resource-lifecycle-review-wave1028", "0x004f2790 CDXSurf__UnlinkNodeFromGlobalList", "0x004f2710 CTextureBase__Init", BACKUP_PATH),
    PCPLATFORM_DOC: ("Wave1028", "cdx-render-resource-lifecycle-review-wave1028", "0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag", BACKUP_PATH),
    ENGINE_DOC: ("Wave1028", "cdx-render-resource-lifecycle-review-wave1028", "0x0053e2e0 CDXEngine__Render", "0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime d3d/render-resource lifetime behavior proven",
    "visible render output proven",
    "runtime render output proven",
    "exact layout proven",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 28,
        "instructions.tsv": 87,
        "decompile/index.tsv": 5,
        "context-metadata.tsv": 5,
        "context-tags.tsv": 5,
        "context-xrefs.tsv": 648,
        "context-instructions.tsv": 1020,
        "context-decompile/index.tsv": 5,
        "vtable-slots.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row for {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)

    slots = read_tsv(BASE / "vtable-slots.tsv")
    slot_by_index = {row["slot_index"]: row for row in slots}
    require(slot_by_index.get("0", {}).get("pointer_raw") == "0x0054bff0", "vtable slot 0 mismatch", failures)
    require(slot_by_index.get("4", {}).get("pointer_raw") == "0x0054d3f0", "vtable slot 4 mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=5 found=5 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "xrefs.log": "Wrote 28 rows",
        "instructions.log": "Wrote 87 function-body instruction rows",
        "decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=5 found=5 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "context-xrefs.log": "Wrote 648 rows",
        "context-instructions.log": "Wrote 1020 function-body instruction rows",
        "context-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=8",
    }
    bad_tokens = ("LockException", "Traceback", "BADADDR", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1")
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in bad_tokens:
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cdx-render-resource-lifecycle-review-wave1028")
        == r"py -3 tools\ghidra_cdx_render_resource_lifecycle_review_wave1028_probe.py --check",
        "missing Wave1028 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1028-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1028 --check",
        "missing Wave1028 aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1028 CDX render resource lifecycle review" for row in ledger_rows), "missing Wave1028 ledger row", failures)
    require(
        any(row.get("task") == "Wave1028 CDX render resource lifecycle review" and row.get("attempt_id") == 20610 for row in attempts),
        "missing Wave1028 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave1028 CDX render-resource lifecycle probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1028 CDX render-resource lifecycle probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
