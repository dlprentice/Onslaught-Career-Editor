#!/usr/bin/env python3
"""Validate Wave872 engine/viewpoint read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave872-engine-viewpoint"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_engine_viewpoint_wave872_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave872 engine/viewpoint"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-191020_post_wave872_engine_viewpoint_verified"
NEXT_HEAD = "0x00553960 CDXEngine__RenderMultipassLayerA"
STRICT_PROXY = "5857/6106 = 95.92%"

TARGETS = {
    "0x00552410": {
        "name": "CRenderQueue__ResetOrCreateField6C0Resource",
        "signature": "int __fastcall CRenderQueue__ResetOrCreateField6C0Resource(void * this)",
        "tokens": ("0x005e5134", "this+0x6c0", "0x00888a50", "0x40,0x40,0x50", "owner framing to CRenderQueue"),
        "tags": {"boundary-created", "vtable-slot", "field-6c0-resource", "d3d-resource-create", "owner-corrected"},
    },
    "0x00552470": {
        "name": "CRenderQueue__ReleaseField6C0Resource",
        "signature": "int __fastcall CRenderQueue__ReleaseField6C0Resource(void * this)",
        "tokens": ("0x005e5138", "this+0x6c0", "resource cleanup", "owner wording to CRenderQueue"),
        "tags": {"vtable-slot", "field-6c0-resource", "resource-release", "owner-corrected"},
    },
    "0x005524a0": {
        "name": "CRenderQueue__UpdateViewVectorAndMatrix",
        "signature": "void __thiscall CRenderQueue__UpdateViewVectorAndMatrix(void * this, float x, float y, float z, int flags)",
        "tokens": ("CEngine__SetupLights", "0x0044a38e", "0x009c7550", "this+0x594", "this+0x6c4"),
        "tags": {"setup-lights-caller", "view-vector", "matrix-block", "global-render-queue", "owner-corrected"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "engine-viewpoint-wave872",
    "wave872-readback-verified",
    "retail-binary-evidence",
    "function-boundary-created",
    "signature-corrected",
    "comment-hardened",
    "important-renderer-infrastructure",
    "crenderqueue",
    "viewpoint-lighting",
}

CORE_ANCHORS = (
    TASK,
    "engine-viewpoint-wave872",
    "0x00552410 CRenderQueue__ResetOrCreateField6C0Resource",
    "0x00552470 CRenderQueue__ReleaseField6C0Resource",
    "0x005524a0 CRenderQueue__UpdateViewVectorAndMatrix",
    "0x005e5134",
    "0x005e5138",
    "0x009c7550",
    "CEngine__SetupLights",
    "CRenderQueue__scalar_deleting_dtor",
    "high-importance renderer/viewpoint infrastructure, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime render/viewpoint behavior proven",
    "runtime resource cleanup behavior proven",
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


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 2,
        "pre-instructions.tsv": 124,
        "pre-decompile/index.tsv": 2,
        "pre-expanded-metadata.tsv": 3,
        "pre-expanded-tags.tsv": 3,
        "pre-expanded-xrefs.tsv": 3,
        "pre-expanded-instructions.tsv": 156,
        "pre-expanded-decompile/index.tsv": 3,
        "pre-expanded-vtables.tsv": 16,
        "pre-xref-site-instructions.tsv": 61,
        "pre-helper-metadata.tsv": 1,
        "pre-boundary-instructions.tsv": 242,
        "post-metadata.tsv": 3,
        "post-tags.tsv": 3,
        "post-xrefs.tsv": 3,
        "post-instructions.tsv": 156,
        "post-decompile/index.tsv": 3,
        "post-xref-site-instructions.tsv": 61,
        "post-helper-metadata.tsv": 1,
        "post-vtables.tsv": 16,
        "post-boundary-instructions.tsv": 242,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"metadata name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"metadata signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave872 engine/viewpoint static read-back", *expected["tokens"]):
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | set(expected["tags"])
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing post decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}: {dec.get('signature')}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-xrefs.tsv"))
    for token in ("005e5134", "005e5138", "0044a38e", "CEngine__SetupLights", "UNCONDITIONAL_CALL"):
        require(token in xref_text, f"missing xref token: {token}", failures)

    vtable_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-vtables.tsv"))
    for token in ("CRenderQueue__scalar_deleting_dtor", "CRenderQueue__ResetOrCreateField6C0Resource", "CRenderQueue__ReleaseField6C0Resource"):
        require(token in vtable_text, f"missing vtable token: {token}", failures)

    site_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-xref-site-instructions.tsv"))
    require("CALL\t0x005524a0" in site_text, "missing CEngine__SetupLights callsite token", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "create-dry.log": "created=0 would_create=1 already_exists=0 renamed=0 would_rename=0 failed=0",
        "create-apply.log": "created=1 would_create=0 already_exists=0 renamed=1 would_rename=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=3 skipped=0 renamed=3 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=3 found=3 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "post-xrefs.log": "Wrote 3 rows",
        "post-instructions.log": "Wrote 156 function-body instruction rows",
        "post-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-xref-site-instructions.log": "targets=1 missing=0",
        "post-helper-metadata.log": "targets=1 found=1 missing=0",
        "post-vtables.log": "targets=2 rows=16",
        "post-boundary-instructions.log": "targets=2 missing=0",
        "quality-refresh.log": "total_functions=6106 commented_functions=5857",
        "queue-probe.log": "Commentless functions: 249",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave872.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave872_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADNAME:", "READBACK_BAD", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("ApplyEngineViewpointWave872.java> OK:") == 3, "apply readback count mismatch", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing save success token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6106, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 249, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6106, "quality TSV row count mismatch", failures)
    require(commented == 5857, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5857, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00553960", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXEngine__RenderMultipassLayerA", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172460935 or backup.get("totalBytes") == 172460935.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        ENGINE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-engine-viewpoint-wave872") == r"py -3 tools\ghidra_engine_viewpoint_wave872_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave872 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20527 for row in attempts), "missing Wave872 attempt row", failures)


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
        print("Wave872 engine/viewpoint probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave872 engine/viewpoint probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
