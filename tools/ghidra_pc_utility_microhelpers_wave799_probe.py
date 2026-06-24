#!/usr/bin/env python3
"""Validate Wave799 PC utility microhelper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave799-pc-utility-microhelpers"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_pc_utility_microhelpers_wave799_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
CLIPARAMS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CLIParams.cpp" / "_index.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
PLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Platform.cpp" / "_index.md"
DXVIDEO_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFrontEndVideo.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-063302_post_wave799_pc_utility_microhelpers_verified"
NEXT_RAW_HEAD = "0x00445010"

TARGETS = {
    "0x00441730": {
        "name": "CLIParams__SetField04",
        "signature": "void __thiscall CLIParams__SetField04(void * this, int field04_value)",
        "comment": ("Wave799 static read-back", "RET 0x4", "unused_flags parameter was a phantom", "mNoStaticShadows"),
        "tags": {"cli-params", "signature-corrected", "ret-0x4"},
    },
    "0x00441b10": {
        "name": "CGame__SetGlobalSelectionSnapshot",
        "signature": "void __cdecl CGame__SetGlobalSelectionSnapshot(void * selection_vec4, int selection_mode)",
        "comment": ("Wave799 static read-back", "0x0066eb80", "0x0066ff74", "0x0066ff75"),
        "tags": {"game-screenshot", "selection-snapshot", "global-state"},
    },
    "0x00441b80": {
        "name": "Platform__ProcessPendingScreenDump",
        "signature": "void Platform__ProcessPendingScreenDump(void)",
        "comment": ("Wave799 static read-back", "PCPlatform__DeviceFlip", "0x0066ff78", "Direct3D surface"),
        "tags": {"platform", "screen-dump", "device-flip"},
    },
    "0x00441e20": {
        "name": "CDXFrontEndVideo__ClearByteFlag",
        "signature": "void __thiscall CDXFrontEndVideo__ClearByteFlag(void * this)",
        "comment": ("Wave799 static read-back", "byte-flag clear", "CDXFrontEndVideo__Render", "owning field offset is not proven"),
        "tags": {"frontend-video", "byte-flag", "render-helper"},
    },
    "0x00441e30": {
        "name": "CDXFrontEndVideo__SetByteFlagAndReturnOld",
        "signature": "int __thiscall CDXFrontEndVideo__SetByteFlagAndReturnOld(void * this)",
        "comment": ("Wave799 static read-back", "old byte in AL", "upper EAX bits are not semantically proven"),
        "tags": {"frontend-video", "byte-flag", "render-helper"},
    },
    "0x00441e40": {
        "name": "CGame__ClearDwordValue",
        "signature": "void __thiscall CGame__ClearDwordValue(void * this)",
        "comment": ("Wave799 static read-back", "CGame__InitRestartLoop", "dword pointed to by ECX", "owning CGame field identity"),
        "tags": {"game", "restart-loop", "dword-clear", "tranche-tail"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "pc-utility-microhelpers-wave799",
    "wave799-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "pc-utility-microhelper",
}

EXPECTED_XREFS = {
    ("0x00441730", "0x004240a0", "CLIParams__ParseCommandLine"),
    ("0x00441b10", "0x004684b6", "CFrontEnd__Render"),
    ("0x00441b10", "0x0046e961", "CGame__Update"),
    ("0x00441b10", "0x0046e9df", "CGame__Update"),
    ("0x00441b10", "0x0047159f", "CGame__DrawGameStuff"),
    ("0x00441b80", "0x005158fb", "PCPlatform__DeviceFlip"),
    ("0x00441e20", "0x005418f2", "CDXFrontEndVideo__Render"),
    ("0x00441e30", "0x00541909", "CDXFrontEndVideo__Render"),
    ("0x00441e40", "0x0046c57d", "CGame__InitRestartLoop"),
}

EXPECTED_INSTRUCTIONS = {
    ("0x00441730", "0x00441730", "MOV", "EAX, dword ptr [ESP + 0x4]"),
    ("0x00441730", "0x00441734", "MOV", "dword ptr [ECX + 0x4], EAX"),
    ("0x00441730", "0x00441737", "RET", "0x4"),
    ("0x00441b10", "0x00441b1a", "MOV", "dword ptr [0x0066eb80], ECX"),
    ("0x00441b10", "0x00441b3f", "MOV", "byte ptr [0x0066ff74], 0x1"),
    ("0x00441b10", "0x00441b50", "MOV", "dword ptr [0x0066eb84], 0xffffffff"),
    ("0x00441b80", "0x00441b80", "MOV", "AL, [0x0066ff74]"),
    ("0x00441b80", "0x00441b94", "MOV", "EAX, [0x0066ff78]"),
    ("0x00441e20", "0x00441e22", "MOV", "byte ptr [EAX], 0x0"),
    ("0x00441e30", "0x00441e30", "MOV", "AL, byte ptr [ECX]"),
    ("0x00441e30", "0x00441e32", "MOV", "byte ptr [ECX], 0x1"),
    ("0x00441e40", "0x00441e40", "MOV", "dword ptr [ECX], 0x0"),
}

CORE_ANCHORS = (
    "Wave799 PC utility microhelpers",
    "pc-utility-microhelpers-wave799",
    "0x00441730 CLIParams__SetField04",
    "0x00441b10 CGame__SetGlobalSelectionSnapshot",
    "0x00441b80 Platform__ProcessPendingScreenDump",
    "0x00441e20 CDXFrontEndVideo__ClearByteFlag",
    "0x00441e30 CDXFrontEndVideo__SetByteFlagAndReturnOld",
    "0x00441e40 CGame__ClearDwordValue",
    "0x00445010 CMCBuggy__GetTargetValueOrFallback",
    "0 exact-undefined signatures",
    "0 param_N signatures",
    "5552/6098 = 91.05%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime screenshot behavior proven",
    "runtime command-line behavior proven",
    "runtime bink behavior proven",
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
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 9,
        "pre-instructions.tsv": 222,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 9,
        "post-instructions.tsv": 222,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata row: {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["comment"]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags row: {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | set(expected["tags"])
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row: {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row.get("from_function", ""))
        for row in read_tsv(BASE / "post-xrefs.tsv")
    }
    require(EXPECTED_XREFS.issubset(xrefs), f"xref set missing: {EXPECTED_XREFS - xrefs}", failures)

    instructions = {
        (normalize_address(row["target_addr"]), normalize_address(row["instruction_addr"]), row.get("mnemonic", ""), row.get("operands", ""))
        for row in read_tsv(BASE / "post-instructions.tsv")
    }
    require(EXPECTED_INSTRUCTIONS.issubset(instructions), f"instruction set missing: {EXPECTED_INSTRUCTIONS - instructions}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=5 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=5 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
        "post-instructions.log": "Wrote 222 instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5552",
        "queue-probe.log": "Commentless functions: 546",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave799.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave799_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "Script not found", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 546, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "commentless high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5552, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5552, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == NEXT_RAW_HEAD, "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CMCBuggy__GetTargetValueOrFallback", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 171314055, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    broad_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in broad_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    function_docs = {
        CLIPARAMS_DOC: ("Wave799 PC utility microhelpers", "pc-utility-microhelpers-wave799", "0x00441730 CLIParams__SetField04", "unused_flags", "mNoStaticShadows", BACKUP_PATH),
        GAME_DOC: ("Wave799 PC utility microhelpers", "0x00441b10 CGame__SetGlobalSelectionSnapshot", "0x00441e40 CGame__ClearDwordValue", "0x00445010 CMCBuggy__GetTargetValueOrFallback", BACKUP_PATH),
        PLATFORM_DOC: ("Wave799 PC utility microhelpers", "0x00441b80 Platform__ProcessPendingScreenDump", "PCPlatform__DeviceFlip", "0x0066ff78", BACKUP_PATH),
        DXVIDEO_DOC: ("Wave799 PC utility microhelpers", "0x00441e20 CDXFrontEndVideo__ClearByteFlag", "0x00441e30 CDXFrontEndVideo__SetByteFlagAndReturnOld", "CDXFrontEndVideo__Render", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-pc-utility-microhelpers-wave799")
        == r"py -3 tools\ghidra_pc_utility_microhelpers_wave799_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave799 PC utility microhelpers" for row in read_jsonl(LEDGER)), "missing Wave799 ledger row", failures)
    require(any(row.get("task") == "Wave799 PC utility microhelpers" and row.get("attempt_id") == 20454 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave799 attempt row", failures)


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
        print("Wave799 PC utility microhelpers probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave799 PC utility microhelpers probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
