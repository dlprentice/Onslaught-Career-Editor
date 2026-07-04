#!/usr/bin/env python3
"""Validate Wave1030 frontend init/video/fade read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1030-frontend-init-video-fade-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_init_video_fade_review_wave1030_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1030_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
FEPCOMMON_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPCommon.cpp" / "_index.md"
FEPMULTI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMultiplayerStart.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified"

TARGETS = {
    "0x004662a0": (
        "CFrontEnd__Init",
        "int __thiscall CFrontEnd__Init(void * this, int entry, int in_loaded_system)",
        ("CFrontEnd startup initializer", "shared frontend resources", "page table wiring"),
    ),
    "0x004679e0": (
        "CFrontEnd__RenderPreCommonFade",
        "void __stdcall CFrontEnd__RenderPreCommonFade(float transition, uint argb, int destination_page)",
        ("Frontend/page pre-common fade helper", "renders a full-window/video quad", "clamps"),
    ),
    "0x00452ce0": (
        "CFrontEnd__RenderVideoQuadScaledToWindow",
        "void __stdcall CFrontEnd__RenderVideoQuadScaledToWindow(float scale, int argb, float center_x, float center_y)",
        ("frontend video-quad render helper", "PLATFORM window dimensions", "CDXFrontEndVideo__Render"),
    ),
}

CONTEXT_TARGETS = {
    "0x00452b00": "CFEPCommon__Init",
    "0x00452b30": "CFEPCommon__Shutdown",
    "0x00452b60": "CFrontEndPage__Process_NoOp",
    "0x00452da0": "SharedVFunc__NoOp_Ret08",
    "0x00466ae0": "CFrontEnd__SetPage",
    "0x00468770": "CFrontEnd__PlaySound",
    "0x00462b70": "CFEPMain__RenderPreCommon",
    "0x00459e50": "CFEPMultiplayerStart__SubObj8848__RenderPreCommon",
    "0x00441e20": "CDXFrontEndVideo__ClearByteFlag",
    "0x00441e30": "CDXFrontEndVideo__SetByteFlagAndReturnOld",
}

DOC_TOKENS = (
    "Wave1030",
    "frontend-init-video-fade-review-wave1030",
    "0x004662a0 CFrontEnd__Init",
    "0x004679e0 CFrontEnd__RenderPreCommonFade",
    "0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow",
    "621/1408 = 44.11%",
    "850/1493 = 56.93%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime frontend behavior proven",
    "runtime video behavior proven",
    "runtime transition visuals proven",
    "exact layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
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
        "metadata.tsv": 3,
        "tags.tsv": 3,
        "xrefs.tsv": 9,
        "instructions.tsv": 481,
        "decompile/index.tsv": 3,
        "context-metadata.tsv": 10,
        "context-tags.tsv": 10,
        "context-xrefs.tsv": 354,
        "context-instructions.tsv": 221,
        "context-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            require("static-reaudit" in tag_row.get("tags", ""), f"missing static-reaudit tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    context_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    context_decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-decompile" / "index.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context_metadata.get(address)
        require(row is not None, f"missing context metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context metadata status mismatch at {address}", failures)
        dec = context_decompile.get(address)
        require(dec is not None and dec.get("status") == "OK", f"context decompile mismatch at {address}", failures)

    xrefs_text = read_text(BASE / "xrefs.tsv")
    for token in (
        "CFrontEnd__Run",
        "CFEPDebriefing__RenderPreCommon",
        "CFEPCredits__RenderPreCommon",
        "CFEPLanguageTest__RenderPreCommon",
        "CFEPOptions__RenderPreCommon",
        "CFEPScreenPos__RenderPreCommon",
        "CFEPMain__RenderPreCommon",
        "CFEPMultiplayerStart__SubObj8848__RenderPreCommon",
    ):
        require(token in xrefs_text, f"missing xref token: {token}", failures)

    primary_decomp = "\n".join(read_text(path) for path in (BASE / "decompile").glob("*.c"))
    for token in (
        "CFrontEnd__LoadSharedResources",
        "CDXFrontEndVideo__SetDefaultSize",
        "CFrontEnd__SetPage",
        "CFrontEnd__RenderVideoQuadScaledToWindow",
        "PLATFORM__GetWindowWidth",
        "CDXFrontEndVideo__Render",
    ):
        require(token in primary_decomp, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=3 found=3 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "xrefs.log": "Wrote 9 rows",
        "instructions.log": "Wrote 481 function-body instruction rows",
        "decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "context-metadata.log": "targets=10 found=10 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "context-xrefs.log": "Wrote 354 rows",
        "context-instructions.log": "Wrote 221 function-body instruction rows",
        "context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        FRONTEND_DOC,
        FEPCOMMON_DOC,
        FEPMULTI_DOC,
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

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-frontend-init-video-fade-review-wave1030")
        == r"py -3 tools\ghidra_frontend_init_video_fade_review_wave1030_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1030-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1030 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1030 frontend init/video/fade review" for row in ledger), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1030 frontend init/video/fade review" and row.get("attempt_id") == 20612 for row in attempts),
        "missing attempt row",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6238, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave1030 frontend init/video/fade review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1030 frontend init/video/fade review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
