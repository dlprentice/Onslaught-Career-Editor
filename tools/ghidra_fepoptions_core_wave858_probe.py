#!/usr/bin/env python3
"""Validate Wave858 FEPOptions core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave858-fepoptions-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepoptions_core_wave858_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPOptions.cpp" / "_index.md"
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

TASK = "Wave858 FEPOptions core"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-124939_post_wave858_fepoptions_core_verified"
NEXT_HEAD = "0x0051f9f0 CFEPScreenPos__Init"
STRICT_PROXY = "5779/6105 = 94.66%"

TARGET_SIGNATURES = {
    "0x0051f370": ("CFEPOptions__GetState", "int __fastcall CFEPOptions__GetState(void * this)"),
    "0x0051f4b0": ("CFEPOptions__Init", "int __fastcall CFEPOptions__Init(void * this)"),
    "0x0051f4c0": ("CFEPOptions__Shutdown", "void __fastcall CFEPOptions__Shutdown(void * this)"),
    "0x0051f4e0": ("CFEPOptions__ButtonPressed", "void __thiscall CFEPOptions__ButtonPressed(void * this, int button, float val)"),
    "0x0051f500": ("CFEPOptions__SaveDefaultOptions", "void __cdecl CFEPOptions__SaveDefaultOptions(int return_flag)"),
    "0x0051f600": ("CFEPOptions__ProcessInput", "void __thiscall CFEPOptions__ProcessInput(void * this, int state)"),
    "0x0051f6d0": ("CFEPOptions__RenderPreCommon", "void __stdcall CFEPOptions__RenderPreCommon(float transition, int dest)"),
    "0x0051f700": ("CFEPOptions__Update", "void __stdcall CFEPOptions__Update(void * this, float transition, int dest)"),
    "0x0051f8e0": ("CFEPOptions__Cleanup", "void CFEPOptions__Cleanup(void)"),
}

CREATED = {"0x0051f4b0", "0x0051f4c0", "0x0051f4e0", "0x0051f6d0"}

COMMENT_TOKENS = {
    "0x0051f370": ("Wave858 static read-back", "CFrontEnd__Process", "this+0x05"),
    "0x0051f4b0": ("function-create", "vtable 0x005db8a8 slot 0", "returns 1"),
    "0x0051f4c0": ("function-create", "g_pOptionsContext", "0x0089bc30"),
    "0x0051f4e0": ("function-create", "vtable slot +0x0c", "RET 0x8"),
    "0x0051f500": ("defaultoptions.bea", "CCareer__Save", "Couldn't write defaultoptions"),
    "0x0051f600": ("process/state-machine", "0x005db8b0", "CFEPOptions__SaveDefaultOptions(1)"),
    "0x0051f6d0": ("function-create", "0x005db8a8 slot 4", "CFrontEnd__RenderPreCommonFade"),
    "0x0051f700": ("render/update", "CPauseMenu__Render", "0x265233"),
    "0x0051f8e0": ("cleanup helper", "CFrontEnd__SetLanguage", "0x0089bc30"),
}

COMMON_TAGS = {
    "static-reaudit",
    "fepoptions-core-wave858",
    "wave858-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "frontend",
    "fepoptions",
    "options-page",
}

EXPECTED_XREFS = {
    ("0x0051f370", "0x00466c8d", "UNCONDITIONAL_CALL"),
    ("0x0051f370", "0x0046cf49", "UNCONDITIONAL_CALL"),
    ("0x0051f4b0", "0x005db8a8", "DATA"),
    ("0x0051f4c0", "0x005db8ac", "DATA"),
    ("0x0051f4e0", "0x005db8b4", "DATA"),
    ("0x0051f500", "0x0051f65d", "UNCONDITIONAL_CALL"),
    ("0x0051f500", "0x0045d0f4", "UNCONDITIONAL_CALL"),
    ("0x0051f600", "0x005db8b0", "DATA"),
    ("0x0051f6d0", "0x005db8b8", "DATA"),
    ("0x0051f700", "0x005db8bc", "DATA"),
    ("0x0051f8e0", "0x00466ab3", "UNCONDITIONAL_CALL"),
}

CORE_ANCHORS = (
    TASK,
    "fepoptions-core-wave858",
    "0x0051f370 CFEPOptions__GetState",
    "0x0051f4b0 CFEPOptions__Init",
    "0x0051f4c0 CFEPOptions__Shutdown",
    "0x0051f4e0 CFEPOptions__ButtonPressed",
    "0x0051f500 CFEPOptions__SaveDefaultOptions",
    "0x0051f600 CFEPOptions__ProcessInput",
    "0x0051f6d0 CFEPOptions__RenderPreCommon",
    "0x0051f700 CFEPOptions__Update",
    "0x0051f8e0 CFEPOptions__Cleanup",
    "[maintainer-local-source-export-root]\\FEPOptions.cpp",
    "defaultoptions.bea",
    "important frontend/options connective",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime options menu behavior proven",
    "runtime filesystem behavior proven",
    "exact options-context layout proven",
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
        "pre-nofunction-instructions.tsv": 148,
        "pre-context-metadata.tsv": 15,
        "pre-context-decompile/index.tsv": 15,
        "pre-vtable.tsv": 18,
        "post-create-metadata.tsv": 9,
        "post-create-tags.tsv": 9,
        "post-create-xrefs.tsv": 11,
        "post-create-instructions.tsv": 333,
        "post-create-decompile/index.tsv": 9,
        "post-create-vtable.tsv": 18,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 11,
        "post-instructions.tsv": 333,
        "post-decompile/index.tsv": 9,
        "post-context-metadata.tsv": 15,
        "post-context-decompile/index.tsv": 15,
        "post-vtable.tsv": 18,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    created = read_tsv(BASE / "create-apply.tsv")
    require({normalize_address(row["address"]) for row in created} == CREATED, "created address set mismatch", failures)
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
    fep_slots = {
        int(row["slot_index"]): row["function_name"]
        for row in vtable
        if normalize_address(row.get("vtable", "")) == "0x005db8a8" and row.get("slot_index", "").isdigit()
    }
    for slot, name in {
        0: "CFEPOptions__Init",
        1: "CFEPOptions__Shutdown",
        2: "CFEPOptions__ProcessInput",
        3: "CFEPOptions__ButtonPressed",
        4: "CFEPOptions__RenderPreCommon",
        5: "CFEPOptions__Update",
        6: "CFEPOptions__EnsureOptionsContext",
        7: "SharedVFunc__NoOpOneArg_004014c0",
        8: "CFrontEndPage__DeActiveNotification",
    }.items():
        require(fep_slots.get(slot) == name, f"CFEPOptions vtable slot {slot} mismatch", failures)

    screen_slots = {
        int(row["slot_index"]): row["function_name"]
        for row in vtable
        if normalize_address(row.get("vtable", "")) == "0x005db858" and row.get("slot_index", "").isdigit()
    }
    require(screen_slots.get(0) == "CFEPScreenPos__Init", "CFEPScreenPos context slot 0 mismatch", failures)

    strings = {
        "post-string-0063fc54.tsv": "Couldn't write defaultoptions",
        "post-string-0063fc74.tsv": "defaultoptions.bea",
        "post-string-0063fc88.tsv": r"[maintainer-local-source-export-root]\FEPOptions.cpp",
    }
    for relative, expected in strings.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "create-dry.log": "CreateFunctionsFromAddressList complete: mode=dry targets=4 created=0 would_create=4 already_exists=0 renamed=0 would_rename=0 failed=0",
        "create-apply.log": "CreateFunctionsFromAddressList complete: mode=apply targets=4 created=4 would_create=0 already_exists=0 renamed=4 would_rename=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=5 missing=0 bad=0",
        "apply-redry-after-signature-string.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 11 rows",
        "post-instructions.log": "Wrote 333 instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-context-metadata.log": "targets=15 found=15 missing=0",
        "post-context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "post-vtable.log": "ExportVtableSlots complete: targets=2 rows=18",
        "post-string-0063fc88.log": r"DumpCStringAtAddress complete: input=0063fc88 target=0063fc88 text=[maintainer-local-source-export-root]\FEPOptions.cpp",
        "quality-refresh.log": "total_functions=6105 commented_functions=5779",
        "queue-probe.log": "Commentless functions: 326",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave858.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave858_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADCOMMENT:", "BADTAGS:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        require("BADSIG:" not in text and "bad=1" not in text and "READBACK_BAD" not in text, f"unexpected bad token in {relative}", failures)

    first_dry = read_text(BASE / "apply-dry-badsig-existing-signature-string.log")
    require("BADSIG: 0x0051f370" in first_dry and "bad=4" in first_dry, "preserved first dry BADSIG evidence missing", failures)
    first_apply = read_text(BASE / "apply-initial-signature-string-bad.log")
    require("READBACK_BAD: 0x0051f4b0" in first_apply and "READBACK_BAD: 0x0051f6d0" in first_apply and "bad=4" in first_apply, "preserved initial apply readback mismatch evidence missing", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 326, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5779, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5779, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0051f9f0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFEPScreenPos__Init", "raw commentless head name mismatch", failures)

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
        package.get("scripts", {}).get("test:ghidra-fepoptions-core-wave858")
        == r"py -3 tools\ghidra_fepoptions_core_wave858_probe.py --check",
        "missing package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger), "missing Wave858 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20513 for row in attempts), "missing Wave858 attempt row", failures)


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
        print("Wave858 FEPOptions core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave858 FEPOptions core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
