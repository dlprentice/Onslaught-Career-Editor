#!/usr/bin/env python3
"""Validate Wave804 CVBufTexture render-helper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave804-cvbuftexture-render-helpers"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvbuftexture_render_helpers_wave804_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-091718_post_wave804_cvbuftexture_render_helpers_verified"
SCRIPT_NAME = "ApplyCVBufTextureRenderHelpersWave804.java"

TARGETS = {
    "0x00472e50": {
        "name": "CVBufTexture__DrawSpriteWithDefaultTextureFallback",
        "signature": "int __thiscall CVBufTexture__DrawSpriteWithDefaultTextureFallback(void * this, float screen_x, float screen_y, float draw_width, float draw_height, float argb_tint_bits)",
        "xref_from": "0x00527ba7",
        "xref_function": "CGame__DrawLocalCoopControllerPrompt",
        "comment": (
            "Wave804 static read-back",
            "s_meshtex_default_tga_00625498",
            "CTexture__FindTexture",
            "DAT_0089ce84",
            "CVBufTexture__DrawSpriteEx",
            "RET 0x14",
        ),
        "tags": {
            "static-reaudit",
            "cvbuftexture-render-helpers-wave804",
            "wave804-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "cvbuftexture",
            "sprite-wrapper",
            "fallback-texture",
            "signature-hardened",
            "tranche-head",
        },
    },
    "0x00476fe0": {
        "name": "CVBufTexture__RenderDynamicUnitPass",
        "signature": "void CVBufTexture__RenderDynamicUnitPass(void)",
        "xref_from": "0x0050ab91",
        "xref_function": "CVBufTexture__RenderAndRestoreStateFlag4",
        "comment": (
            "Wave804 static read-back",
            "DAT_00855170",
            "DAT_00855178",
            "CDXEngine__BuildProjectedSprites",
            "CMapWhoEntry__GetOwner",
            "CRenderQueue__InsertSortedByDepth",
            "g_MeshQualityDistance",
            "g_MeshQualityLodTable",
        ),
        "tags": {
            "static-reaudit",
            "cvbuftexture-render-helpers-wave804",
            "wave804-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "cvbuftexture",
            "dynamic-unit-render",
            "render-queue",
            "lod-gate",
            "signature-retained",
            "tranche-tail",
        },
    },
}

CORE_ANCHORS = (
    "Wave804 CVBufTexture render helpers",
    "cvbuftexture-render-helpers-wave804",
    "0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback",
    "0x00476fe0 CVBufTexture__RenderDynamicUnitPass",
    "0x00488f60 CInfantryUnit__VFunc_02_00488f60",
    "5576/6098 = 91.44%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime rendering behavior proven",
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
        "pre-instructions.tsv": 338,
        "pre-decompile/index.tsv": 2,
        "pre-context-metadata.tsv": 7,
        "pre-context-decompile/index.tsv": 7,
        "pre-context-instructions.tsv": 595,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 2,
        "post-instructions.tsv": 338,
        "post-decompile/index.tsv": 2,
        "post-context-metadata.tsv": 7,
        "post-context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    decompile_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in (BASE / "post-decompile").glob("*.c"))

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in expected["comment"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected["tags"].issubset(actual_tags), f"tags missing at {address}: {expected['tags'] - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref row for {address}", failures)
        if xref is not None:
            require(normalize_address(xref.get("from_addr", "")) == expected["xref_from"], f"xref source mismatch at {address}", failures)
            require(xref.get("from_function") == expected["xref_function"], f"xref function mismatch at {address}", failures)
            require(xref.get("ref_type") == "UNCONDITIONAL_CALL", f"xref type mismatch at {address}", failures)

    for token in (
        "s_meshtex_default_tga_00625498",
        "CTexture__FindTexture",
        "CVBufTexture__DrawSpriteEx",
        "DAT_00855178",
        "CDXEngine__BuildProjectedSprites",
        "CMapWhoEntry__GetOwner",
        "CRenderQueue__InsertSortedByDepth",
        "g_MeshQualityDistance",
        "g_MeshQualityLodTable",
    ):
        require(token in decompile_text, f"missing post-decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 2 rows",
        "post-instructions.log": "Wrote 338 instruction rows",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5576",
        "queue-probe.log": "Commentless functions: 522",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave804.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave804_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 522, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue expected empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5576, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5576, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00488f60", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CInfantryUnit__VFunc_02_00488f60", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (171314055, 171314055.0), "backup byte count mismatch", failures)
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
        VBUFTEXTURE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cvbuftexture-render-helpers-wave804")
        == r"py -3 tools\ghidra_cvbuftexture_render_helpers_wave804_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave804 CVBufTexture render helpers" for row in ledger_rows), "missing Wave804 ledger row", failures)
    require(
        any(row.get("task") == "Wave804 CVBufTexture render helpers" and row.get("attempt_id") == 20459 for row in attempts),
        "missing Wave804 attempt row",
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
        print("Wave804 CVBufTexture render-helpers probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave804 CVBufTexture render-helpers probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
