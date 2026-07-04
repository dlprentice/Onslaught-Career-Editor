#!/usr/bin/env python3
"""Validate Wave983 CChunkReader resource-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave983-cchunkreader-resource-review"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current"
QUEUE_JSON = QUEUE / "static-reaudit-queue.json"
QUEUE_TSV = QUEUE / "functions_quality.tsv"
NOTE = ROOT / "release" / "readiness" / "ghidra_cchunkreader_resource_review_wave983_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CHUNKER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "chunker.cpp" / "_index.md"
MAPTEX_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "maptex.cpp" / "_index.md"
VERTEX_SHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-001624_post_wave983_cchunkreader_resource_review_verified"

TARGETS = {
    "0x004237d0": ("CChunkReader__ctor", "void * __fastcall CChunkReader__ctor(void * this)", 4),
    "0x00423840": ("CChunkReader__dtor_base", "void __fastcall CChunkReader__dtor_base(void * this)", 7),
    "0x00423870": ("CChunkReader__OpenExistingBuffer", "void * __thiscall CChunkReader__OpenExistingBuffer(void * this, void * existingBuffer)", 2),
    "0x004238c0": ("CChunkReader__OpenFile", "void * __thiscall CChunkReader__OpenFile(void * this, char * filename)", 3),
    "0x00423900": ("CChunkReader__Close", "int __fastcall CChunkReader__Close(void * this)", 4),
    "0x00423910": ("CChunkReader__GetNext", "uint __fastcall CChunkReader__GetNext(void * this)", 107),
    "0x00423960": ("CChunkReader__Read", "bool __thiscall CChunkReader__Read(void * this, void * outBuffer, int size, int count)", 164),
    "0x00423990": ("CChunkReader__Skip", "int __fastcall CChunkReader__Skip(void * this)", 8),
}

REQUIRED_TAGS = {
    "static-reaudit",
    "cchunkreader-resource-review-wave983",
    "wave983-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "source-parity-reviewed",
    "chunk-reader",
    "resource-io",
}

COMMENT_TOKENS = {
    "0x004237d0": ("Wave983 CChunkReader resource review", "0x134-byte", "this+0x4"),
    "0x00423840": ("Wave983 CChunkReader resource review", "mOwnFile", "clears File"),
    "0x00423870": ("Wave983 CChunkReader resource review", "Open(CMEMBUFFER*)", "existingBuffer"),
    "0x004238c0": ("Wave983 CChunkReader resource review", "Open(char*)", "CDXMemBuffer__InitFromFile"),
    "0x00423900": ("Wave983 CChunkReader resource review", "normalizes success to 0 or failure to -1"),
    "0x00423910": ("Wave983 CChunkReader resource review", "4-byte chunk id", "not CMeshPart-specific"),
    "0x00423960": ("Wave983 CChunkReader resource review", "size*count", "CDXMemBuffer__Read"),
    "0x00423990": ("Wave983 CChunkReader resource review", "Size-ReadSinceChunk", "CDXMemBuffer__Skip"),
}

DECOMPILE_TOKENS = {
    "004237d0_CChunkReader__ctor.c": ("CDXMemBuffer__ctor",),
    "00423840_CChunkReader__dtor_base.c": ("CDXMemBuffer__dtor_base",),
    "00423870_CChunkReader__OpenExistingBuffer.c": ("existingBuffer",),
    "004238c0_CChunkReader__OpenFile.c": ("CDXMemBuffer__InitFromFile",),
    "00423900_CChunkReader__Close.c": ("CDXMemBuffer__Close",),
    "00423910_CChunkReader__GetNext.c": ("CDXMemBuffer__Read",),
    "00423960_CChunkReader__Read.c": ("CDXMemBuffer__Read",),
    "00423990_CChunkReader__Skip.c": ("CDXMemBuffer__Skip",),
}

DOC_TOKENS = (
    "Wave983",
    "cchunkreader-resource-review-wave983",
    "CChunkReader__GetNext",
    "CChunkReader__Read",
    "CChunkReader__Skip",
    "6222/6222 = 100.00%",
    "384/1408 = 27.27%",
    "443/1478 = 29.97%",
    BACKUP_PATH,
    "Wave900+ recheck",
)

OVERCLAIMS = (
    "runtime archive/resource i/o behavior proven",
    "exact archive schema coverage proven",
    "rebuild parity proven",
    "exact cchunkreader structure layout proven",
)


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


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def check_counts(failures: list[str]) -> None:
    expected = {
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 299,
        "pre-instructions.tsv": 153,
        "pre-decompile/index.tsv": 8,
        "helper-metadata.tsv": 6,
        "helper-decompile/index.tsv": 6,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 299,
        "post-instructions.tsv": 153,
        "post-decompile/index.tsv": 8,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count {actual} != {count}", failures)


def check_logs(failures: list[str]) -> None:
    expected_tokens = {
        "pre-metadata.log": ("targets=8 found=8 missing=0",),
        "pre-tags.log": ("ExportFunctionTagsByAddress complete: rows=8 missing=0",),
        "pre-xrefs.log": ("Wrote 299 rows",),
        "pre-instructions.log": ("Wrote 153 function-body instruction rows", "targets=8 missing=0"),
        "pre-decompile.log": ("targets=8 dumped=8 missing=0 failed=0",),
        "helper-metadata.log": ("targets=6 found=6 missing=0",),
        "helper-decompile.log": ("targets=6 dumped=6 missing=0 failed=0",),
        "apply-dry.log": ("updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 missing=0 bad=0", "REPORT: Save succeeded"),
        "apply.log": ("updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 missing=0 bad=0", "REPORT: Save succeeded"),
        "apply-final-dry.log": ("updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0", "REPORT: Save succeeded"),
        "post-metadata.log": ("targets=8 found=8 missing=0",),
        "post-tags.log": ("ExportFunctionTagsByAddress complete: rows=8 missing=0",),
        "post-xrefs.log": ("Wrote 299 rows",),
        "post-instructions.log": ("Wrote 153 function-body instruction rows", "targets=8 missing=0"),
        "post-decompile.log": ("targets=8 dumped=8 missing=0 failed=0",),
    }
    bad_tokens = ("LockException", "ERROR REPORT SCRIPT ERROR", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "missing=1", "bad=1", "failed=1")
    for relative, tokens in expected_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"{relative} missing token: {token}", failures)
        for bad in bad_tokens:
            require(bad not in text, f"{relative} contains bad token: {bad}", failures)


def check_saved_rows(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    quality = read_tsv(QUEUE_TSV)

    for address, (name, signature, expected_xrefs) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"post metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"comment token missing at {address}: {token}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"post tags missing {address}", failures)
        if tag_row:
            actual = set(tag_row.get("tags", "").split(";"))
            require(REQUIRED_TAGS.issubset(actual), f"tags missing at {address}: {sorted(REQUIRED_TAGS - actual)}", failures)

        quality_row = row_by_address(quality, address)
        require(quality_row is not None, f"quality row missing {address}", failures)
        if quality_row:
            require(quality_row.get("name") == name, f"quality name mismatch at {address}", failures)
            require(quality_row.get("signature") == signature, f"quality signature mismatch at {address}", failures)
            require("Wave983 CChunkReader resource review" in quality_row.get("comment", ""), f"quality comment missing Wave983 at {address}", failures)

        count = sum(1 for xref in read_tsv(BASE / "post-xrefs.tsv") if normalize_address(xref.get("target_addr", "")) == address)
        require(count == expected_xrefs, f"xref count at {address} {count} != {expected_xrefs}", failures)


def check_xrefs_decompile(failures: list[str]) -> None:
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    caller_names = {row.get("from_function", "") for row in xrefs}
    for caller in (
        "CResourceAccumulator__ReadResourceFile",
        "CMesh__Deserialize",
        "CCutscene__Load",
        "CMapTex__Deserialize",
        "CMeshPart__LoadFromStream",
        "CVertexShader__DeserializeAll",
    ):
        require(caller in caller_names, f"missing caller xref: {caller}", failures)

    for filename, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / "post-decompile" / filename)
        for token in tokens:
            require(token in text, f"{filename} missing decompile token: {token}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173837191, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-cchunkreader-resource-review-wave983")
        == r"py -3 tools\ghidra_cchunkreader_resource_review_wave983_probe.py --check",
        "package script mismatch",
        failures,
    )

    docs = [NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, FUNCTION_COVERAGE, CHUNKER_DOC, MAPTEX_DOC, VERTEX_SHADER_DOC, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text or token.replace("\\", "\\\\") in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"{path.relative_to(ROOT)} contains overclaim token: {bad}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave983 CChunkReader resource review" and row.get("status") == "completed" for row in ledger), "missing Wave983 ledger row", failures)
    require(any(row.get("task") == "Wave983 CChunkReader resource review" and row.get("attempt_id") == 20574 for row in attempts), "missing Wave983 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_logs(failures)
    check_saved_rows(failures)
    check_xrefs_decompile(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave983 CChunkReader resource-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave983 CChunkReader resource-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
