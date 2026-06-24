#!/usr/bin/env python3
"""Validate Wave569 frontend/reconnect Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave569-frontend-render-tail-00527960"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_reconnect_wave569_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPM_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMultiplayerStart.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x00527960": {
        "raw": "00527960",
        "name": "CFEPMultiplayerStart__SetCurrentSelection",
        "signature": "void __thiscall CFEPMultiplayerStart__SetCurrentSelection(void * this, int selection_state)",
        "tags": {"static-reaudit", "frontend-reconnect-wave569", "retail-binary-evidence", "frontend", "fepmultiplayerstart", "selection-state", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("selection_state", "RET 0x4 confirms", "DAT_0089be50/DAT_0089be5c", "runtime frontend behavior"),
        "decompile_tokens": ("CFEPMultiplayerStart__SetCurrentSelection(void *this,int selection_state)", "this + 8", "selection_state"),
    },
    "0x00527c50": {
        "raw": "00527c50",
        "name": "CFrontEnd__AdvanceStateAndRelinquishControl",
        "signature": "bool __thiscall CFrontEnd__AdvanceStateAndRelinquishControl(void * this, void * controller, int caller_state_token)",
        "tags": {"static-reaudit", "frontend-reconnect-wave569", "retail-binary-evidence", "frontend", "controller-handoff", "reconnect-handoff", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("State 1 becomes 2", "CController__RelinquishControl(controller)", "RET 0x8 confirms", "second consumed but currently unread stack token"),
        "decompile_tokens": ("CFrontEnd__AdvanceStateAndRelinquishControl", "void *controller", "int caller_state_token", "CController__RelinquishControl(controller)"),
    },
    "0x00527c90": {
        "raw": "00527c90",
        "name": "CReconnectInterface__ctor",
        "signature": "void * __thiscall CReconnectInterface__ctor(void * this, void * tweak_name, int default_index_one_based)",
        "tags": {"static-reaudit", "frontend-reconnect-wave569", "retail-binary-evidence", "reconnect-interface", "ctweak", "constructor", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("CTweak__ctor_base(tweak_name)", "vtable 0x005e4a80", "default_index_one_based - 1", "older third param_N"),
        "decompile_tokens": ("CReconnectInterface__ctor(void *this,void *tweak_name,int default_index_one_based)", "CTweak__ctor_base(this,tweak_name)", "return this;"),
    },
    "0x00527d00": {
        "raw": "00527d00",
        "name": "CReconnectInterface__VFunc_07_00527d00",
        "signature": "void __thiscall CReconnectInterface__VFunc_07_00527d00(void * this, float tweak_value)",
        "tags": {"static-reaudit", "frontend-reconnect-wave569", "retail-binary-evidence", "reconnect-interface", "ctweak", "float-setter", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("single float stack argument", "RET 0x4 confirms", "-landscape0/-landscape1/-landscape2", "exact class ownership"),
        "decompile_tokens": ("CReconnectInterface__VFunc_07_00527d00(void *this,float tweak_value)", "ROUND(tweak_value)", "this + 0xc"),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def row_count(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values: dict[str, int] = {}
    for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1)):
        values[key] = int(value)
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def require_doc_tokens(path: Path, tokens: tuple[str, ...], failures: list[str]) -> None:
    try:
        text = read_text(path)
    except FileNotFoundError:
        failures.append(f"missing doc: {path}")
        return
    require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)


def run_check() -> list[str]:
    failures: list[str] = []

    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply.log", {"updated": 4, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_verify_dry.log", {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)

    expected_counts = {
        "post_metadata.tsv": 4,
        "post_tags.tsv": 4,
        "post_decompile/index.tsv": 4,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")

    overclaim_tokens = ("runtime behavior proven", "source identity proven", "rebuild parity proven", "fully RE'ed", "fully REed")
    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} metadata status is {row['status']}")
        if row["name"] != spec["name"]:
            failures.append(f"{address} name mismatch: {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row['signature']} != {spec['signature']}")
        require_tokens(f"{address} comment", row["comment"], spec["comment_tokens"], failures)
        for bad_token in overclaim_tokens:
            if bad_token in row["comment"]:
                failures.append(f"{address} comment overclaims: {bad_token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            present = set(filter(None, tag_row["tags"].split(";")))
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")
            for forbidden in ("source-parity", "runtime-proven", "rebuild-parity"):
                if forbidden in present:
                    failures.append(f"{address} unexpectedly has {forbidden} tag")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile index")
        elif decomp_row["status"] != "OK":
            failures.append(f"{address} decompile status is {decomp_row['status']}")
        else:
            decomp_file = next((BASE / "post_decompile").glob(f"{spec['raw']}_*.c"), None)
            if decomp_file is None:
                failures.append(f"{address} missing decompile file")
            else:
                require_tokens(f"{address} decompile", read_text(decomp_file), spec["decompile_tokens"], failures)

    require_tokens(
        "xrefs",
        xrefs,
        (
            "00527960\tCFEPMultiplayerStart__SetCurrentSelection\t0051be91\t0051be70\tCFEPMultiplayerStart__SubObj4034__InitRuntimeState\tUNCONDITIONAL_CALL",
            "00527c50\tCFrontEnd__AdvanceStateAndRelinquishControl\t00466c67\t00466ba0\tCFrontEnd__Process\tUNCONDITIONAL_CALL",
            "00527c90\tCReconnectInterface__ctor\t0053aa1c\t<none>\t<no_function>\tUNCONDITIONAL_CALL",
            "00527d00\tCReconnectInterface__VFunc_07_00527d00\t00423f45\t00423bc0\tCLIParams__ParseCommandLine\tUNCONDITIONAL_CALL",
            "00527d00\tCReconnectInterface__VFunc_07_00527d00\t005e4a80\t<none>\t<no_function>\tDATA",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x00527960\t0x00527960\tAFTER\t2\t0x00527967\t0x00527960\tCFEPMultiplayerStart__SetCurrentSelection\tRET\t0x4",
            "0x00527c50\t0x00527c50\tAFTER\t13\t0x00527c73\t0x00527c50\tCFrontEnd__AdvanceStateAndRelinquishControl\tRET\t0x8",
            "0x00527c90\t0x00527c90\tAFTER\t15\t0x00527cba\t0x00527c90\tCReconnectInterface__ctor\tRET\t0x8",
            "0x00527d00\t0x00527d00\tAFTER\t7\t0x00527d1c\t0x00527d00\tCReconnectInterface__VFunc_07_00527d00\tRET\t0x4",
        ),
        failures,
    )

    require_doc_tokens(PUBLIC_NOTE, ("Wave569", "CFEPMultiplayerStart__SetCurrentSelection", "CFrontEnd__AdvanceStateAndRelinquishControl", "No runtime behavior was claimed"), failures)
    require_doc_tokens(FUNCTION_INDEX, ("Wave569 frontend/reconnect", "0x00527960", "0x00527d00"), failures)
    require_doc_tokens(FEPM_INDEX, ("Wave569", "SetCurrentSelection", "AdvanceStateAndRelinquishControl"), failures)
    require_doc_tokens(GHIDRA_REFERENCE, ("Wave569 frontend/reconnect", "0x00527c90", "0x00527d00"), failures)
    require_doc_tokens(CAMPAIGN, ("Wave569", "frontend/reconnect", "comment-backed proxy"), failures)
    require_doc_tokens(BACKLOG, ("Wave569", "CReconnectInterface__ctor", "queued next"), failures)

    if not QUEUE_JSON.is_file():
        failures.append("missing current queue JSON")
    else:
        data = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
        if data.get("status") != "PASS":
            failures.append(f"queue status is {data.get('status')}")
        quality = data.get("qualitySignals", {})
        for key in ("commentlessFunctionCount", "undefinedSignatureCount", "paramSignatureCount"):
            if quality.get(key) is None:
                failures.append(f"queue JSON missing qualitySignals.{key}")

    if not LEDGER.is_file():
        failures.append("missing mutation ledger")
    else:
        ledger_text = LEDGER.read_text(encoding="utf-8")
        require_tokens("ledger", ledger_text, ("wave569", "frontend-reconnect-wave569", "0x00527960", "0x00527d00"), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate Wave569 artifacts")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()
    failures = run_check()
    if args.json:
        print(json.dumps({"ok": not failures, "failures": failures}, indent=2))
    else:
        if failures:
            print("FAIL")
            for failure in failures:
                print(f"- {failure}")
        else:
            print("PASS Wave569 frontend/reconnect probe")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
