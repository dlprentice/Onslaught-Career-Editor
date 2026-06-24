#!/usr/bin/env python3
"""Validate Wave871 CScreenFx zoom read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave871-cscreenfx-zoom"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cscreenfx_zoom_wave871_2026-05-25.md"
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

TASK = "Wave871 CScreenFx zoom"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-183506_post_wave871_cscreenfx_zoom_verified"
NEXT_HEAD = "0x00552470 CEngine__ReleaseField6C0"
STRICT_PROXY = "5854/6105 = 95.89%"

TARGETS = {
    "0x00551c90": {
        "name": "CScreenFx__InitZoomEffectCvar",
        "signature": "void __fastcall CScreenFx__InitZoomEffectCvar(void * state)",
        "tokens": ("cg_zoomeffectenabled", "Is the visual effect for zooming enabled?", "CEngine__Init", "state+0x10"),
        "tags": {"console-variable", "zoom-effect-cvar", "engine-init"},
    },
    "0x00551cc0": {
        "name": "CScreenFx__LoadZoomTextures",
        "signature": "void __fastcall CScreenFx__LoadZoomTextures(void * state)",
        "tokens": ("screenfx\\zoomlines.tga", "screenfx\\reticle.tga", "CScreenFx__FindTexture", "CVBufTexture__SetVBFormat", "CVBufTexture__SetIBFormat"),
        "tags": {"texture-load", "zoomlines-texture", "reticle-texture", "vbuftexture-format", "engine-initresources"},
    },
    "0x00551d40": {
        "name": "CScreenFx__ReleaseZoomTextures",
        "signature": "void __fastcall CScreenFx__ReleaseZoomTextures(void * state)",
        "tokens": ("CEngine__Shutdown", "CDXEngine__DecrementResourceRefCount", "state+4", "CScreenFx__LoadZoomTextures"),
        "tags": {"texture-release", "resource-refcount", "engine-shutdown", "zoom-effect-lifecycle"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "cscreenfx-zoom-wave871",
    "wave871-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-reviewed",
    "important-renderer-infrastructure",
    "screenfx",
    "zoom-effect",
    "renderer-connective-code",
}

HELPERS = {
    "CVBufTexture__SetVBFormat",
    "CVBufTexture__SetIBFormat",
    "CDXEngine__DecrementResourceRefCount",
    "CScreenFx__FindTexture",
}

STRING_EXPECTATIONS = {
    "string-006521bc.tsv": "cg_zoomeffectenabled",
    "string-006521d4.tsv": "Is the visual effect for zooming enabled?",
    "string-00652218.tsv": r"screenfx\zoomlines.tga",
    "string-00652200.tsv": r"screenfx\reticle.tga",
}

CORE_ANCHORS = (
    TASK,
    "cscreenfx-zoom-wave871",
    "0x00551c90 CScreenFx__InitZoomEffectCvar",
    "0x00551cc0 CScreenFx__LoadZoomTextures",
    "0x00551d40 CScreenFx__ReleaseZoomTextures",
    "cg_zoomeffectenabled",
    r"screenfx\zoomlines.tga",
    r"screenfx\reticle.tga",
    "important screen-effect renderer infrastructure, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime zoom-line/reticle rendering behavior proven",
    "runtime cvar toggling behavior proven",
    "runtime cleanup behavior proven",
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
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 67,
        "pre-decompile/index.tsv": 3,
        "pre-xref-site-instructions.tsv": 69,
        "pre-helper-metadata.tsv": 4,
        "post-metadata.tsv": 3,
        "post-tags.tsv": 3,
        "post-xrefs.tsv": 3,
        "post-instructions.tsv": 67,
        "post-decompile/index.tsv": 3,
        "post-xref-site-instructions.tsv": 69,
        "post-helper-metadata.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    require(HELPERS.issubset(helper_names), f"missing helper metadata rows: {HELPERS - helper_names}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

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
            for token in ("Wave871 CScreenFx zoom static read-back", *expected["tokens"]):
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
    for token in ("CEngine__Init", "CEngine__InitResources", "CEngine__Shutdown"):
        require(token in xref_text, f"missing xref token: {token}", failures)

    site_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-xref-site-instructions.tsv"))
    for token in ("CALL\t0x00551c90", "CALL\t0x00551cc0", "CALL\t0x00551d40"):
        require(token in site_text, f"missing xref-site token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=3 found=3 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "post-xrefs.log": "Wrote 3 rows",
        "post-instructions.log": "Wrote 67 function-body instruction rows",
        "post-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-xref-site-instructions.log": "targets=3 missing=0",
        "post-helper-metadata.log": "targets=4 found=4 missing=0",
        "quality-refresh.log": "total_functions=6105 commented_functions=5854",
        "queue-probe.log": "Commentless functions: 251",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave871.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave871_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADNAME:", "READBACK_BAD", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("READBACK_OK:") == 3, "apply readback count mismatch", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing save success token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 251, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5854, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5854, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00552470", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CEngine__ReleaseField6C0", "raw commentless head name mismatch", failures)

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
    require(scripts.get("test:ghidra-cscreenfx-zoom-wave871") == r"py -3 tools\ghidra_cscreenfx_zoom_wave871_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave871 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20526 for row in attempts), "missing Wave871 attempt row", failures)


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
        print("Wave871 CScreenFx zoom probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave871 CScreenFx zoom probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
