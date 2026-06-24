#!/usr/bin/env python3
"""Validate Wave724 texture row edge padding head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave724-texture-row-edge-padding-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_row_edge_padding_head_wave724_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
MESHCOLLISION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

SIGNATURE_TAGS = {
    "static-reaudit",
    "texture-row-edge-padding-head-wave724",
    "wave724-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "texture-row-edge-padding",
}

COMMENT_TAGS = {
    "static-reaudit",
    "texture-row-edge-padding-head-wave724",
    "wave724-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
    "hidden-register-context",
    "texture-row-edge-padding",
}

TARGETS = {
    "0x005ab420": (
        "CTexture__BuildComponentPlaneRowPointers",
        "void CTexture__BuildComponentPlaneRowPointers(void)",
        ("builds component-plane row pointer tables", "hidden ESI context", "current void(void) signature is intentionally retained"),
        COMMENT_TAGS | {"component-plane", "row-pointer-table", "hidden-esi-context", "tranche-head"},
    ),
    "0x005ab4d0": (
        "CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh",
        "void __fastcall CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh(void * texture_context)",
        ("mirrors/copies high-side edge rows", "ECX texture/decode context", "owner/source identity proof"),
        SIGNATURE_TAGS | {"edge-padding", "mirror-high", "fastcall-ecx-context", "current-owner-unproven"},
    ),
    "0x005ab620": (
        "CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth",
        "void CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth(void)",
        ("mirrors/copies both edge sides", "hidden EAX texture/decode context", "current void(void) signature is intentionally retained"),
        COMMENT_TAGS | {"edge-padding", "mirror-both", "hidden-eax-context", "current-owner-unproven"},
    ),
    "0x005ab700": (
        "CMeshCollisionVolume__FinalizeEdgePaddingRows",
        "void CMeshCollisionVolume__FinalizeEdgePaddingRows(void)",
        ("finalizes component-plane edge-padding rows", "row-cache +0x48", "current void(void) signature is intentionally retained"),
        COMMENT_TAGS | {"edge-padding", "finalize-padding", "hidden-eax-context", "current-owner-unproven"},
    ),
    "0x005ab9c0": (
        "CDXTexture__InitComponentPlaneRowCache",
        "void __stdcall CDXTexture__InitComponentPlaneRowCache(void * texture_context)",
        ("initializes the component-plane row cache", "RET 0x4 evidence", "texture_context"),
        SIGNATURE_TAGS | {"row-cache", "component-plane", "allocator", "tranche-tail", "hidden-ebx-diagnostic"},
    ),
}

DOC_TOKENS = (
    "Wave724 texture row edge padding head",
    "texture-row-edge-padding-head-wave724",
    "0x005ab420 CTexture__BuildComponentPlaneRowPointers",
    "0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh",
    "0x005ab620 CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth",
    "0x005ab700 CMeshCollisionVolume__FinalizeEdgePaddingRows",
    "0x005ab9c0 CDXTexture__InitComponentPlaneRowCache",
    "0x005aba90 CDXTexture__SelectNextScanTableForProgress",
    "0x0042f220 CSPtrSet__Clear",
    r"G:\GhidraBackups\BEA_20260522-055657_post_wave724_texture_row_edge_padding_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime texture/decode behavior proven",
    "current owner/source identity proven",
    "fully reverse-engineered",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 5,
        "pre-instructions.tsv": 2405,
        "pre-decompile/index.tsv": 5,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 5,
        "post-instructions.tsv": 2405,
        "post-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave724 static read-back" in comment, f"missing Wave724 comment at {address}", failures)
        require("Static retail Ghidra metadata" in comment, f"missing static-evidence boundary at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "post-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 5 rows",
        "pre-instructions.log": "Wrote 2405 instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 5 rows",
        "post-instructions.log": "Wrote 2405 instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)
        require("BADNAME" not in text, f"unexpected BADNAME in {relative}", failures)
        require("FAIL" not in text, f"unexpected FAIL in {relative}", failures)
        require("Input file not found" not in text, f"stale failed export in {relative}", failures)

    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save evidence", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply-final-dry.log"), "missing final dry save evidence", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1838, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 109, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005aba90", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CDXTexture__SelectNextScanTableForProgress", "high-signal head name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    raw_head = next(row for row in rows if not row.get("comment", "").strip())
    require(commented == 4260, "commented count mismatch", failures)
    require(strict_clean == 4202, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    by_address = {normalize_address(row["address"]): row for row in rows}
    for address in TARGETS:
        row = by_address.get(address)
        require(row is not None, f"missing queue row for {address}", failures)
        if row is None:
            continue
        require(bool(row.get("comment", "").strip()), f"queue row still commentless for {address}", failures)
        if address in {"0x005ab4d0", "0x005ab9c0"}:
            require(re.search(r"\bparam_\d+\b", row.get("signature", "")) is None, f"queue row still has param_N for {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["backup"] == r"G:\GhidraBackups\BEA_20260522-055657_post_wave724_texture_row_edge_padding_head_verified", "backup destination mismatch", failures)
    require(backup["sourceFileCount"] == 19, "backup source file count mismatch", failures)
    require(backup["backupFileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["backupBytes"]) == 166562695, "backup byte count mismatch", failures)
    require(backup["diffCount"] == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        MESHCOLLISION_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            escaped = token.replace("\\", "\\\\")
            require(token in text or escaped in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lower, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    require("test:ghidra-texture-row-edge-padding-head-wave724" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave724 texture row edge padding head" for row in ledgers), "missing Wave724 ledger row", failures)
    require(any(row.get("attempt_id") == 20379 and row.get("task") == "Wave724 texture row edge padding head" for row in attempts), "missing Wave724 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20380, "tracking next_attempt_id mismatch", failures)
    require("Wave724 texture row edge padding head" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return non-zero when validation fails.")
    args = parser.parse_args(argv)

    failures: list[str] = []
    for check in (check_artifacts, check_logs, check_queue_and_backup, check_docs_and_state):
        try:
            check(failures)
        except Exception as exc:  # pragma: no cover - diagnostic path
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("Wave724 texture row edge padding head probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave724 texture row edge padding head probe")
    print("Status: PASS")
    print("Targets: 5")
    print("Queue: 6098 total, 4260 commented, 1838 commentless, 1216 undefined, 109 param_N")
    print(r"Backup: G:\GhidraBackups\BEA_20260522-055657_post_wave724_texture_row_edge_padding_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
