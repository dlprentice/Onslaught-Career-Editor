#!/usr/bin/env python3
"""Validate Wave870 CRenderQueue core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave870-crenderqueue-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crenderqueue_core_wave870_2026-05-25.md"
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

TASK = "Wave870 CRenderQueue core"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-180844_post_wave870_crenderqueue_core_verified"
NEXT_HEAD = "0x00551c90 CScreenFx__InitZoomEffectCvar"
STRICT_PROXY = "5851/6105 = 95.84%"

TARGETS = {
    "0x005515a0": {
        "name": "CDXEngine__InitConsoleVar_UseRenderQueue",
        "signature": "void __fastcall CDXEngine__InitConsoleVar_UseRenderQueue(void * storage)",
        "tokens": ("cg_userenderqueue", "Use the render queue", "CGame__InitRestartLoop"),
        "tags": {"render-queue-cvar", "console-variable", "game-init"},
    },
    "0x005515d0": {
        "name": "CRenderQueueBucket__Reset",
        "signature": "void __fastcall CRenderQueueBucket__Reset(void * bucket)",
        "tokens": ("bucket+4", "CDXEngine__Render"),
        "tags": {"bucket-reset", "cdxengine-render", "tiny-state-helper"},
    },
    "0x005515e0": {
        "name": "CRenderQueueBucket__RenderAndRecycle",
        "signature": "void __thiscall CRenderQueueBucket__RenderAndRecycle(void * this, void * bucket_set, int bucket_index)",
        "tokens": ("CEngine__DrawIndexedPrimitives", "CDXMemoryManager__Free", "CRenderQueue__BeginFrame"),
        "tags": {"bucket-render-recycle", "draw-indexed-primitives", "state-cache", "memory-recycle"},
    },
    "0x00551920": {
        "name": "CRenderQueue__BeginFrame",
        "signature": "void __fastcall CRenderQueue__BeginFrame(void * queue)",
        "tokens": ("CDXEngine__SetWorldMatrixElements", "CRenderQueueBucket__RenderAndRecycle", "CDXEngine__Render"),
        "tags": {"begin-frame", "matrix-defaults", "cdxengine-render", "sampler-state"},
    },
    "0x00551f20": {
        "name": "CRenderQueue__ctor",
        "signature": "void * __fastcall CRenderQueue__ctor(void * this)",
        "tokens": ("this+0x0c", "this+0x10c", "CGenericActiveReader__ctor_Zero", "this+0x704"),
        "tags": {"constructor", "active-reader-array", "deviceobject-subobject", "vtable"},
    },
    "0x00551fb0": {
        "name": "CRenderQueue__scalar_deleting_dtor",
        "signature": "void * __thiscall CRenderQueue__scalar_deleting_dtor(void * this, int free_flag)",
        "tokens": ("CRenderQueue__dtor", "CDXMemoryManager__Free", "0x005e512c"),
        "tags": {"scalar-deleting-dtor", "vtable", "memory-free"},
    },
    "0x00551fd0": {
        "name": "CGenericActiveReader__ctor_Zero",
        "signature": "void __fastcall CGenericActiveReader__ctor_Zero(void * this)",
        "tokens": ("zeroes the first dword", "CRenderQueue__ctor", "OID__CreateObject"),
        "tags": {"active-reader", "shared-helper", "constructor", "crenderqueue-constructor"},
    },
    "0x00551fe0": {
        "name": "CRenderQueue__dtor",
        "signature": "void __fastcall CRenderQueue__dtor(void * this)",
        "tokens": ("CRT__EhVectorDestructorIterator_WithUnwind", "CGenericActiveReader__dtor", "DeviceObject__dtor_body"),
        "tags": {"destructor", "active-reader-array", "deviceobject-subobject"},
    },
    "0x00552660": {
        "name": "CRenderQueue__ResetOrPushSentinel",
        "signature": "void __fastcall CRenderQueue__ResetOrPushSentinel(void * this)",
        "tokens": ("this+0x704", "0x46800000", "-1.0 sentinel", "DAT_0089d680"),
        "tags": {"depth-sentinel", "active-reader", "cdxengine-render", "dat-0089d680-gate"},
    },
    "0x005526c0": {
        "name": "CRenderQueue__InsertSortedByDepth",
        "signature": "void __thiscall CRenderQueue__InsertSortedByDepth(void * this, void * item, float depth)",
        "tokens": ("CVBufTexture__RenderDynamicUnitPass", "CRenderQueue__InsertIfDepthBelowIndexedLimit", "CGenericActiveReader__SetReader"),
        "tags": {"depth-sort", "active-reader", "dynamic-unit-render", "dat-0089d680-gate"},
    },
    "0x00552740": {
        "name": "CRenderQueue__RecycleInactiveItems",
        "signature": "void __fastcall CRenderQueue__RecycleInactiveItems(void * this)",
        "tokens": ("this+0x10c", "this+0x50c", "DAT_00652230", "CRenderQueue__RenderAll"),
        "tags": {"recycle-inactive", "active-reader", "free-list", "frame-delta"},
    },
    "0x00552800": {
        "name": "CRenderQueue__MergePendingItems",
        "signature": "void __fastcall CRenderQueue__MergePendingItems(void * this)",
        "tokens": ("this+0x0c", "this+0x10c", "this+0x50c", "CGenericActiveReader__SetReader"),
        "tags": {"merge-pending", "active-reader", "free-list", "render-all-helper"},
    },
    "0x005528b0": {
        "name": "CRenderQueue__RenderAll",
        "signature": "void __fastcall CRenderQueue__RenderAll(void * this)",
        "tokens": ("PLATFORM__GetSysTimeFloat", "static shadow height", "CFastVB__RenderTriangleStripImmediate", "CDXEngine__SetGlobalTintColorOpaque(0xe7)"),
        "tags": {"render-all", "fast-vb", "static-shadow", "state-restore", "global-tint"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "crenderqueue-core-wave870",
    "wave870-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-reviewed",
    "important-renderer-infrastructure",
    "render-queue",
    "renderer-connective-code",
}

CORE_ANCHORS = (
    TASK,
    "crenderqueue-core-wave870",
    "0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue",
    "0x005515e0 CRenderQueueBucket__RenderAndRecycle",
    "0x00551920 CRenderQueue__BeginFrame",
    "0x00551f20 CRenderQueue__ctor",
    "0x005526c0 CRenderQueue__InsertSortedByDepth",
    "0x005528b0 CRenderQueue__RenderAll",
    "important renderer infrastructure, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime visual behavior proven",
    "runtime queue toggle behavior proven",
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
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 29,
        "pre-instructions.tsv": 1594,
        "pre-decompile/index.tsv": 13,
        "pre-xref-site-instructions.tsv": 757,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 29,
        "post-instructions.tsv": 1594,
        "post-decompile/index.tsv": 13,
        "post-xref-site-instructions.tsv": 757,
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
            for token in ("Wave870 CRenderQueue core static read-back", *expected["tokens"]):
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

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
    for token in (
        "CGame__Init",
        "CDXEngine__Render",
        "CRenderQueue__BeginFrame",
        "CVBufTexture__RenderDynamicUnitPass",
        "CRenderQueue__InsertIfDepthBelowIndexedLimit",
        "CRenderQueue__RenderAll",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)

    site_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-xref-site-instructions.tsv"))
    for token in ("CALL\t0x005515a0", "CALL\t0x005515d0", "CALL\t0x005515e0", "CALL\t0x005526c0", "CALL\t0x005528b0"):
        require(token in site_text, f"missing xref-site token: {token}", failures)
    require("0x005e512c\t0x005e512c\tMISSING" in site_text, "expected vtable data site miss not recorded", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=13 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=13 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=13 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-xrefs.log": "Wrote 29 rows",
        "post-instructions.log": "Wrote 1594 function-body instruction rows",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "pre-xref-site-instructions.log": "targets=29 missing=1",
        "post-xref-site-instructions.log": "targets=29 missing=1",
        "quality-refresh.log": "total_functions=6105 commented_functions=5851",
        "queue-probe.log": "Commentless functions: 254",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave870.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave870_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADNAME:", "READBACK_BAD", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("READBACK_OK:") == 13, "apply readback count mismatch", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing save success token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 254, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5851, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5851, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00551c90", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CScreenFx__InitZoomEffectCvar", "raw commentless head name mismatch", failures)

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
    require(scripts.get("test:ghidra-crenderqueue-core-wave870") == r"py -3 tools\ghidra_crenderqueue_core_wave870_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave870 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20525 for row in attempts), "missing Wave870 attempt row", failures)


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
        print("Wave870 CRenderQueue core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave870 CRenderQueue core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
