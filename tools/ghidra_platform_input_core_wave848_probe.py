#!/usr/bin/env python3
"""Validate Wave848 platform-input/core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave848-platform-input-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_platform_input_core_wave848_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PLATFORM_INPUT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PlatformInput.cpp" / "_index.md"
LTSHELL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ltshell.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-070518_post_wave848_platform_input_core_verified"
NEXT_HEAD = "0x00513640 CEngine__GetConstant32"

TARGETS = {
    "0x00513120": {
        "name": "PlatformInput__InitDirectInput",
        "signature": "int __thiscall PlatformInput__InitDirectInput(void * this, void * window_handle)",
        "tokens": (
            "Wave848 static read-back",
            "PCLTShell::InitDirectInput(HWND)",
            "DirectInput8Create",
            "0x00513178",
            "0x00512ff0",
            "Found %d joypads",
            "runtime device behavior",
        ),
        "tags": {"directinput", "joypad-enumeration", "signature-hardened", "ret-4"},
    },
    "0x00513370": {
        "name": "PlatformInput__PollPadState",
        "signature": "int __thiscall PlatformInput__PollPadState(void * this, int pad_index, bool rotate_buttons)",
        "tokens": (
            "Wave848 static read-back",
            "PCLTShell::UpdateJoystick(int)",
            "0x8007001e",
            "button bytes 0x30-0x33",
            "runtime controller behavior",
        ),
        "tags": {"directinput", "joypad-poll", "ret-8"},
    },
    "0x005134a0": {
        "name": "CEngine__GrabScreenshot",
        "signature": "void __thiscall CEngine__GrabScreenshot(void * this, int screenshot_index)",
        "tokens": (
            "Wave848 static read-back",
            "Failed for %s",
            "0x0062c610",
            "scr%.4d.tga",
            "ImageIO__WriteTGA24",
            "runtime screenshot output behavior",
        ),
        "tags": {"d3d-surface", "screenshot", "signature-hardened", "ret-4"},
    },
    "0x005135f0": {
        "name": "PlatformInput__SetKeySinkCore",
        "signature": "void __thiscall PlatformInput__SetKeySinkCore(void * this, void * key_sink)",
        "tokens": (
            "Wave848 static read-back",
            "PLATFORM__SetKeySink",
            "CFEPVirtualKeyboard",
            "this+0x33458",
            "RET 0x4",
        ),
        "tags": {"key-sink", "virtual-keyboard", "ret-4"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "platform-input-core-wave848",
    "wave848-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "source-reference-ltshell",
}

EXPECTED_XREFS = {
    "0x00513120": {("0x00512942", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x00513370": {("0x0051260d", "PLATFORM__ProcessSystemMessages", "UNCONDITIONAL_CALL")},
    "0x005134a0": {("0x00471584", "CGame__DrawGameStuff", "UNCONDITIONAL_CALL")},
    "0x005135f0": {
        ("0x005159ca", "PLATFORM__SetKeySink", "UNCONDITIONAL_CALL"),
        ("0x0051ffe3", "CFEPVirtualKeyboard__Shutdown", "UNCONDITIONAL_CALL"),
        ("0x00520301", "CFEPVirtualKeyboard__Process", "UNCONDITIONAL_CALL"),
        ("0x0052035c", "CFEPVirtualKeyboard__Process", "UNCONDITIONAL_CALL"),
    },
}

STRING_EXPECTATIONS = {
    "pre-string-0062c610.tsv": r"grabs\scr%.4d.tga",
    "pre-string-0063de2c.tsv": r"Found %d joypads\x0a",
    "pre-string-0063de40.tsv": r"Found no joypads\x0a",
    "pre-string-0063de54.tsv": r"Failed for %s\x0a",
}

CORE_DOC_TOKENS = (
    "Wave848 platform input core",
    "platform-input-core-wave848",
    "0x00513120 PlatformInput__InitDirectInput",
    "0x00513370 PlatformInput__PollPadState",
    "0x005134a0 CEngine__GrabScreenshot",
    "0x005135f0 PlatformInput__SetKeySinkCore",
    "DirectInput8Create",
    "PCLTShell::InitDirectInput(HWND)",
    "PCLTShell::UpdateJoystick(int)",
    "grabs\\scr%.4d.tga",
    "5678/6098 = 93.11%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime controller behavior proven",
    "runtime screenshot output proven",
    "runtime directinput behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact directinput interface layout proven",
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


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 7,
        "pre-instructions.tsv": 396,
        "pre-xref-site-instructions.tsv": 81,
        "pre-context-metadata.tsv": 5,
        "pre-decompile/index.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 7,
        "post-instructions.tsv": 396,
        "post-xref-site-instructions.tsv": 81,
        "post-context-metadata.tsv": 5,
        "post-decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    xrefs: dict[str, set[tuple[str, str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        target = normalize_address(row["target_addr"])
        xrefs.setdefault(target, set()).add(
            (normalize_address(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", ""))
        )

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == spec["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == spec["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in spec["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | set(spec["tags"])
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == spec["name"], f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == spec["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(EXPECTED_XREFS[address].issubset(xrefs.get(address, set())), f"xref set mismatch for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 7 rows",
        "post-instructions.log": "Wrote 396 instruction rows",
        "post-xref-site-instructions.log": "Wrote 81 instruction rows",
        "post-context-metadata.log": "targets=5 found=5 missing=0",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5678",
        "queue-probe.log": "Commentless functions: 420",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave848.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave848_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "READBACK_BAD", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_log = read_text(BASE / "apply.log")
    for address, spec in TARGETS.items():
        require(f"READBACK_OK: {address} {spec['name']} {spec['signature']}" in apply_log, f"missing READBACK_OK for {address}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 420, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5678, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5678, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00513640", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CEngine__GetConstant32", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171871111 or backup.get("totalBytes") == 171871111.0, "backup byte count mismatch", failures)
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
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        PLATFORM_INPUT_DOC: (
            "Wave848 platform input core",
            "platform-input-core-wave848",
            "0x00513120 PlatformInput__InitDirectInput",
            "0x00513370 PlatformInput__PollPadState",
            "0x005135f0 PlatformInput__SetKeySinkCore",
            BACKUP_PATH,
        ),
        LTSHELL_DOC: (
            "Wave848 platform input core",
            "PCLTShell::InitDirectInput(HWND)",
            "PCLTShell::UpdateJoystick(int)",
            "0x005134a0 CEngine__GrabScreenshot",
            BACKUP_PATH,
        ),
        ENGINE_DOC: (
            "Wave848 platform input core",
            "0x005134a0 CEngine__GrabScreenshot",
            "grabs\\scr%.4d.tga",
            BACKUP_PATH,
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-platform-input-core-wave848")
        == r"py -3 tools\ghidra_platform_input_core_wave848_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave848 platform input core" for row in ledger_rows), "missing Wave848 ledger row", failures)
    require(any(row.get("task") == "Wave848 platform input core" and row.get("attempt_id") == 20503 for row in attempts), "missing Wave848 attempt row", failures)


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
        print("Wave848 platform-input/core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave848 platform-input/core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
