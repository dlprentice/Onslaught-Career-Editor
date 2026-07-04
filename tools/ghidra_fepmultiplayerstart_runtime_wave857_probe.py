#!/usr/bin/env python3
"""Validate Wave857 FEPMultiplayerStart runtime-helper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave857-fepmultiplayerstart-runtime"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepmultiplayerstart_runtime_wave857_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMultiplayerStart.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave857 FEPMultiplayerStart runtime"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-121518_post_wave857_fepmultiplayerstart_runtime_verified"
NEXT_HEAD = "0x0051f370 CFEPOptions__GetState"

TARGET_SIGNATURES = {
    "0x0051b600": ("CFEPMultiplayerStart__SubObj4034__ctor", "void __fastcall CFEPMultiplayerStart__SubObj4034__ctor(void * this)"),
    "0x0051b610": ("CFEPMultiplayerStart__SubObj4034__ResetFlags", "void __fastcall CFEPMultiplayerStart__SubObj4034__ResetFlags(void * this)"),
    "0x0051b640": ("CFEPMultiplayerStart__SubObj4034__Init", "int __fastcall CFEPMultiplayerStart__SubObj4034__Init(void * this)"),
    "0x0051b660": ("CFEPMultiplayerStart__SubObj4034__ButtonPressed", "void __thiscall CFEPMultiplayerStart__SubObj4034__ButtonPressed(void * this, int button, float val)"),
    "0x0051b6b0": ("CFEPMultiplayerStart__SubObj4034__Process", "void __thiscall CFEPMultiplayerStart__SubObj4034__Process(void * this, int state)"),
    "0x0051be70": ("CFEPMultiplayerStart__SubObj4034__InitRuntimeState", "void __fastcall CFEPMultiplayerStart__SubObj4034__InitRuntimeState(void * this)"),
    "0x0051da60": ("CFEPMultiplayerStart__InitSelection", "void __thiscall CFEPMultiplayerStart__InitSelection(void * this, int mode)"),
    "0x0051ddd0": ("CFEPMultiplayerStart__HandleInput", "void __thiscall CFEPMultiplayerStart__HandleInput(void * this, int button, int player_index)"),
}

COMMENT_TOKENS = {
    "0x0051b600": ("Wave857 static read-back", "owner+0x4034", "0x005e49b4"),
    "0x0051b610": ("Wave857 static read-back", "DAT_00677614", "0x0051b64e", "0x0051b6cf"),
    "0x0051b640": ("function-create", "vtable 0x005e49b4 slot 0", "returns 1"),
    "0x0051b660": ("function-create", "vtable 0x005e49b4 slot 3", "button 0x2c", "CFrontEnd__SetPage"),
    "0x0051b6b0": ("function-create", "vtable 0x005e49b4 slot 2", "dev-mode timeout", "CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture"),
    "0x0051be70": ("Wave857 static read-back", "0x005e49cc", "PLATFORM__GetSysTimeFloat", "CFEPMultiplayerStart__SetCurrentSelection"),
    "0x0051da60": ("Wave857 static read-back", "0x005db910", "0x005d8ba0"),
    "0x0051ddd0": ("Wave857 static read-back", "0x0051ee7b", "0x0051ef9e", "CFEPMultiplayerStart__GetConfigCount"),
}

COMMON_TAGS = {
    "static-reaudit",
    "fepmultiplayerstart-runtime-wave857",
    "wave857-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "frontend",
    "fepmultiplayerstart",
    "multiplayer-start",
    "subobj4034",
}

EXPECTED_XREFS = {
    ("0x0051b600", "0x00466049", "UNCONDITIONAL_CALL"),
    ("0x0051b610", "0x0051b64e", "UNCONDITIONAL_CALL"),
    ("0x0051b610", "0x0051b6cf", "UNCONDITIONAL_CALL"),
    ("0x0051b640", "0x005e49b4", "DATA"),
    ("0x0051b660", "0x005e49c0", "DATA"),
    ("0x0051b6b0", "0x005e49bc", "DATA"),
    ("0x0051be70", "0x005e49cc", "DATA"),
    ("0x0051da60", "0x005db910", "DATA"),
    ("0x0051ddd0", "0x0051ee7b", "UNCONDITIONAL_CALL"),
    ("0x0051ddd0", "0x0051ef9e", "UNCONDITIONAL_CALL"),
}

CORE_ANCHORS = (
    TASK,
    "fepmultiplayerstart-runtime-wave857",
    "0x0051b600 CFEPMultiplayerStart__SubObj4034__ctor",
    "0x0051b640 CFEPMultiplayerStart__SubObj4034__Init",
    "0x0051b660 CFEPMultiplayerStart__SubObj4034__ButtonPressed",
    "0x0051b6b0 CFEPMultiplayerStart__SubObj4034__Process",
    "0x0051be70 CFEPMultiplayerStart__SubObj4034__InitRuntimeState",
    "0x0051da60 CFEPMultiplayerStart__InitSelection",
    "0x0051ddd0 CFEPMultiplayerStart__HandleInput",
    "[maintainer-local-source-export-root]\\FEPMultiplayerStart.cpp",
    NEXT_HEAD,
    "5770/6101 = 94.57%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime multiplayer-start behavior proven",
    "runtime frontend transition behavior proven",
    "exact subobj4034 layout proven",
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
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 7,
        "pre-instructions.tsv": 185,
        "pre-decompile/index.tsv": 5,
        "pre-nofunction-instructions.tsv": 111,
        "pre-context-metadata.tsv": 18,
        "pre-context-decompile/index.tsv": 18,
        "pre-vtable.tsv": 12,
        "post-create-metadata.tsv": 8,
        "post-create-tags.tsv": 8,
        "post-create-xrefs.tsv": 10,
        "post-create-instructions.tsv": 296,
        "post-create-decompile/index.tsv": 8,
        "post-create-vtable.tsv": 12,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 10,
        "post-instructions.tsv": 296,
        "post-decompile/index.tsv": 8,
        "post-context-metadata.tsv": 18,
        "post-context-decompile/index.tsv": 18,
        "post-vtable.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    created = read_tsv(BASE / "create-apply.tsv")
    require({normalize_address(row["address"]) for row in created} == {"0x0051b640", "0x0051b660", "0x0051b6b0"}, "created address set mismatch", failures)
    require(all(row.get("status") == "created" for row in created), "created status mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    for address, (name, signature) in TARGET_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)

    actual_xrefs = {
        (normalize_address(row.get("target_addr", "")), normalize_address(row.get("from_addr", "")), row.get("ref_type", ""))
        for row in read_tsv(BASE / "post-xrefs.tsv")
    }
    require(EXPECTED_XREFS.issubset(actual_xrefs), f"xrefs missing: {EXPECTED_XREFS - actual_xrefs}", failures)

    vtable = read_tsv(BASE / "post-vtable.tsv")
    subobj_slots = {
        int(row["slot_index"]): row["function_name"]
        for row in vtable
        if normalize_address(row.get("vtable", "")) == "0x005e49b4" and row.get("slot_index", "").isdigit()
    }
    for slot, name in {
        0: "CFEPMultiplayerStart__SubObj4034__Init",
        1: "DebugTrace",
        2: "CFEPMultiplayerStart__SubObj4034__Process",
        3: "CFEPMultiplayerStart__SubObj4034__ButtonPressed",
    }.items():
        require(subobj_slots.get(slot) == name, f"SubObj4034 vtable slot {slot} mismatch", failures)

    string_rows = read_tsv(BASE / "post-string-0063fc24.tsv")
    require(string_rows and string_rows[0].get("cstring") == r"[maintainer-local-source-export-root]\FEPMultiplayerStart.cpp", "FEPMultiplayerStart.cpp string mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "create-dry.log": "CreateFunctionsFromAddressList complete: mode=dry targets=3 created=0 would_create=3 already_exists=0 renamed=0 would_rename=0 failed=0",
        "create-apply.log": "CreateFunctionsFromAddressList complete: mode=apply targets=3 created=3 would_create=0 already_exists=0 renamed=3 would_rename=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=5 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=5 missing=0 bad=1",
        "apply-redry-after-badsig.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-fix-signature.log": "SUMMARY: updated=1 skipped=7 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 10 rows",
        "post-instructions.log": "Wrote 296 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-context-metadata.log": "targets=18 found=18 missing=0",
        "post-context-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
        "post-vtable.log": "ExportVtableSlots complete: targets=3 rows=12",
        "post-string-0063fc24.log": r"DumpCStringAtAddress complete: input=0063fc24 target=0063fc24 text=[maintainer-local-source-export-root]\FEPMultiplayerStart.cpp",
        "quality-refresh.log": "total_functions=6101 commented_functions=5770",
        "queue-probe.log": "Commentless functions: 331",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave857.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave857_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        disallowed = ("LockException", "MISSING:", "BADNAME:", "BADCOMMENT:", "BADTAGS:", "missing=1", "failed=1")
        for bad in disallowed:
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        if relative != "apply.log":
            require("BADSIG:" not in text and "bad=1" not in text, f"unexpected bad signature token in {relative}", failures)
    require("BADSIG: 0x0051b640" in read_text(BASE / "apply.log"), "expected corrective BADSIG evidence missing", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6101, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 331, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6101, "quality TSV row count mismatch", failures)
    require(commented == 5770, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5770, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0051f370", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFEPOptions__GetState", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (172198791, 172198791.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, FUNCTION_INDEX, FEP_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-fepmultiplayerstart-runtime-wave857")
        == r"py -3 tools\ghidra_fepmultiplayerstart_runtime_wave857_probe.py --check",
        "missing package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger), "missing Wave857 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20512 for row in attempts), "missing Wave857 attempt row", failures)


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
        print("Wave857 FEPMultiplayerStart runtime probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave857 FEPMultiplayerStart runtime probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
