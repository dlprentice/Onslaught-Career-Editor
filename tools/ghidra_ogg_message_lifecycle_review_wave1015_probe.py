#!/usr/bin/env python3
"""Validate Wave1015 Ogg/message lifecycle read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1015-ogg-message-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_ogg_message_lifecycle_review_wave1015_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1015_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
OGG_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "OggLoader.cpp" / "_index.md"
MESSAGE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MessageBox.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified"

TARGETS = {
    "0x004b6cd0": ("COggLoader__readerSubobject_dtor_body", "void __fastcall COggLoader__readerSubobject_dtor_body(void * reader_subobject)"),
    "0x004b6d30": ("COggLoader__ctor_base", "void * __fastcall COggLoader__ctor_base(void * this)"),
    "0x004b6d90": ("COggLoader__ThreadProc_ReadPathIntoBuffer", "void __fastcall COggLoader__ThreadProc_ReadPathIntoBuffer(void * this)"),
    "0x004b6df0": ("COggLoader__readerSubobject_scalar_deleting_dtor", "void * __thiscall COggLoader__readerSubobject_scalar_deleting_dtor(void * this, byte flags)"),
    "0x004b6e50": ("CMessage__ctor_base", "void * __thiscall CMessage__ctor_base(void * this, int payload0, short * message_text, int payload2, int payload3, void * active_reader_target, int payload5, int queue_sort_key)"),
    "0x004b6f10": ("CMessage__scalar_deleting_dtor", "void * __thiscall CMessage__scalar_deleting_dtor(void * this, byte flags)"),
    "0x004b7160": ("CMessage__dtor_base", "void __fastcall CMessage__dtor_base(void * this)"),
}

CONTEXT_TARGETS = {
    "0x00528bc0": ("CWaitingThread__ctor_base", "void * __thiscall CWaitingThread__ctor_base(void * this)"),
    "0x00528bf0": ("CWaitingThread__dtor_body", "void __thiscall CWaitingThread__dtor_body(void * this)"),
    "0x005245a0": ("COggFileRead__ctor_base", "void * __thiscall COggFileRead__ctor_base(void * this)"),
    "0x005245e0": ("COggFileRead__scalar_deleting_dtor", "void * __thiscall COggFileRead__scalar_deleting_dtor(void * this, byte flags)"),
    "0x00524600": ("COggFileRead__dtor_body", "void __thiscall COggFileRead__dtor_body(void * this)"),
    "0x005246a0": ("COggFileRead__OpenFileAndPrimeDecoder", "int __thiscall COggFileRead__OpenFileAndPrimeDecoder(void * this, char * file_path)"),
    "0x00524710": ("COggFileRead__ReadDecodedPcm", "int __thiscall COggFileRead__ReadDecodedPcm(void * this, uint requested_byte_count, void * out_pcm_bytes, int * out_bytes_read)"),
    "0x00524770": ("COggFileRead__CloseAndReset", "int __thiscall COggFileRead__CloseAndReset(void * this)"),
    "0x00524800": ("COggFileRead__IsOpen", "int __thiscall COggFileRead__IsOpen(void * this)"),
    "0x00524810": ("COggFileRead__GetSampleRate", "int __thiscall COggFileRead__GetSampleRate(void * this)"),
    "0x00524820": ("COggFileRead__GetChannelCount", "int __thiscall COggFileRead__GetChannelCount(void * this)"),
    "0x004b7ca0": ("CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "void __thiscall CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance(void * this, void * queued_message)"),
    "0x004b7ea0": ("CMessageBox__StartVoiceOrFallbackTextReveal", "void __fastcall CMessageBox__StartVoiceOrFallbackTextReveal(void * this)"),
    "0x004b8800": ("CMessageBox__StopVoicePlaybackIfNotInCutscene", "void __fastcall CMessageBox__StopVoicePlaybackIfNotInCutscene(void * this)"),
    "0x00401000": ("CGenericActiveReader__SetReader", "void __thiscall CGenericActiveReader__SetReader(void * this, void * readerCell)"),
    "0x004e5bd0": ("CSPtrSet__Remove", "void __thiscall CSPtrSet__Remove(void * this, void * value)"),
    "0x004bac40": ("CMonitor__Shutdown", "void __fastcall CMonitor__Shutdown(void * this)"),
}

DOC_TOKENS = (
    "Wave1015",
    "ogg-message-lifecycle-review-wave1015",
    "0x004b6cd0 COggLoader__readerSubobject_dtor_body",
    "0x004b6d30 COggLoader__ctor_base",
    "0x004b6d90 COggLoader__ThreadProc_ReadPathIntoBuffer",
    "0x004b6df0 COggLoader__readerSubobject_scalar_deleting_dtor",
    "0x004b6e50 CMessage__ctor_base",
    "0x004b6f10 CMessage__scalar_deleting_dtor",
    "0x004b7160 CMessage__dtor_base",
    "511/1408 = 36.29%",
    "736/1493 = 49.30%",
    "437/500 = 87.40%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime ogg streaming proven",
    "runtime audio playback proven",
    "runtime message display proven",
    "runtime voice playback proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
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
    if value in {"", "<none>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 7,
        "tags.tsv": 7,
        "xrefs.tsv": 14,
        "instructions.tsv": 195,
        "decompile/index.tsv": 7,
        "context-metadata.tsv": 17,
        "context-xrefs.tsv": 549,
        "context-instructions.tsv": 548,
        "context-decompile/index.tsv": 17,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")

    comment_tokens = {
        "0x004b6cd0": ("COggFileRead cleanup", "CWaitingThread cleanup"),
        "0x004b6d30": ("CWaitingThread construction", "COggFileRead-style reader"),
        "0x004b6d90": ("+0x102310", "+0x2310", "+0x102414"),
        "0x004b6df0": ("ret 0x4", "flags"),
        "0x004b6e50": ("Ret 0x1c", "WcsLen", "queue_sort_key"),
        "0x004b6f10": ("ret 0x4", "CMessage__dtor_base"),
        "0x004b7160": ("active reader cell", "CMonitor__Shutdown"),
    }
    for address, (name, signature) in TARGETS.items():
        key = normalize_address(address)
        row = metadata.get(key)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("Static retail" in comment, f"comment boundary missing {address}", failures)
            for token in comment_tokens[address]:
                require(token in comment, f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(key)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(key)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    context = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    context_decompile = rows_by(read_tsv(BASE / "context-decompile" / "index.tsv"), "address")
    for address, (name, signature) in CONTEXT_TARGETS.items():
        key = normalize_address(address)
        row = context.get(key)
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = context_decompile.get(key)
        require(dec is not None, f"missing context decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"context decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    expected_xrefs = {
        ("0x004b6cd0", "0x004b6df0", "COggLoader__readerSubobject_scalar_deleting_dtor", "from_function_addr"),
        ("0x004b6d90", "0x005dc688", "<no_function>", "from_addr"),
        ("0x004b6df0", "0x005dc690", "<no_function>", "from_addr"),
        ("0x004b6e50", "0x004f9a90", "CUnit__ApplyDamage", "from_function_addr"),
        ("0x004b6e50", "0x004fe030", "CUnit__TriggerEffect", "from_function_addr"),
        ("0x004b6e50", "0x00537410", "IScript__PlaySound", "from_function_addr"),
        ("0x004b6f10", "0x005dc6b8", "<no_function>", "from_addr"),
        ("0x004b7160", "0x004b6f10", "CMessage__scalar_deleting_dtor", "from_function_addr"),
    }
    for target, source, function, source_field in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == normalize_address(target)
                and normalize_address(row.get(source_field, "")) == normalize_address(source)
                and row.get("from_function") == function
                for row in xrefs
            ),
            f"missing xref {source} -> {target} ({function})",
            failures,
        )


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=7 found=7 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "xrefs.log": "Wrote 14 rows",
        "instructions.log": "Wrote 195 function-body instruction rows",
        "decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "context-metadata.log": "targets=17 found=17 missing=0",
        "context-xrefs.log": "Wrote 549 rows",
        "context-instructions.log": "Wrote 548 function-body instruction rows",
        "context-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 18, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        OGG_DOC,
        MESSAGE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIMS:
            require(token not in lower, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-ogg-message-lifecycle-review-wave1015")
        == r"py -3 tools\ghidra_ogg_message_lifecycle_review_wave1015_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1015-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1015 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1015 ogg message lifecycle review" for row in ledger_rows), "missing Wave1015 ledger row", failures)
    require(any(row.get("task") == "Wave1015 ogg message lifecycle review" and row.get("attempt_id") == 20597 for row in attempts), "missing Wave1015 attempt row", failures)


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
        print("Wave1015 Ogg/message lifecycle probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1015 Ogg/message lifecycle probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
