#!/usr/bin/env python3
"""Validate Wave852 PC platform/resource tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave852-pc-platform-resource-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_pc_platform_resource_tail_wave852_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
RESOURCE_ACCUMULATOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ResourceAccumulator.cpp" / "_index.md"
LTSHELL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ltshell.cpp" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
CONSOLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "console.cpp" / "_index.md"
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

TASK = "Wave852 PC platform/resource tail"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-093157_post_wave852_pc_platform_resource_tail_verified"
NEXT_HEAD = "0x005168d0 CPCSoundManager__dtor"

COMMON_TAGS = {
    "static-reaudit",
    "pc-platform-resource-tail-wave852",
    "wave852-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
}

TARGETS = {
    "0x00515ab0": {
        "name": "D3DDevice__SetViewport",
        "signature": "void __stdcall D3DDevice__SetViewport(void * viewport)",
        "tokens": ("Wave852 static read-back", "D3DVIEWPORT", "DAT_00888a50", "vtable slot 0xbc"),
        "tags": {"pc-platform", "d3d-viewport", "render-connector"},
    },
    "0x00515b10": {
        "name": "PCPlatform__DeserializeFontsAndAssets",
        "signature": "void __thiscall PCPlatform__DeserializeFontsAndAssets(void * this, int chunk_reader)",
        "tokens": ("Wave852 static read-back", "Warning : deserializing font twice!", "CDXBitmapFont__Deserialize", "this+0x18"),
        "tags": {"pc-platform", "font-resources", "resource-deserialize"},
    },
    "0x00515db0": {
        "name": "Registry__SetStringValue_HKCU",
        "signature": "void __stdcall Registry__SetStringValue_HKCU(char * value_name, uchar * value_text)",
        "tokens": ("Wave852 static read-back", r"Software\\Lost Toys\\Battle Engine Aquila", "RegSetValueExA", "HKEY_CURRENT_USER"),
        "tags": {"pc-platform", "registry", "console"},
    },
    "0x00515f60": {
        "name": "CResourceDescriptorTable__ctor",
        "signature": "void * __fastcall CResourceDescriptorTable__ctor(void * this)",
        "tokens": ("Wave852 static read-back", "0x41c-byte", "this+0x424", "DATA xref 0x00515f35"),
        "tags": {"resource-descriptor", "constructor", "global-table"},
    },
    "0x00515fb0": {
        "name": "CResourceDescriptorTable__InitDefaultMeshNames",
        "signature": "void CResourceDescriptorTable__InitDefaultMeshNames(void)",
        "tokens": ("Wave852 static read-back", "0x428-byte-stride", "default.msh", "DAT_00896488"),
        "tags": {"resource-descriptor", "default-mesh", "global-table"},
    },
    "0x00516450": {
        "name": "CResourceDescriptorTable__FreeAllEntries",
        "signature": "void CResourceDescriptorTable__FreeAllEntries(void)",
        "tokens": ("Wave852 static read-back", "DAT_0088a510", "0x428-byte strides", "CDXMemoryManager__Free"),
        "tags": {"resource-descriptor", "resource-lifetime", "shutdown"},
    },
    "0x005164b0": {
        "name": "CResourceDescriptorTable__InstantiateChain",
        "signature": "void * __cdecl CResourceDescriptorTable__InstantiateChain(void * descriptor_table, int owner_tag)",
        "tokens": ("Wave852 static read-back", "PCRTID__CreateObject", "owner_tag", "CThing__InitRenderThing"),
        "tags": {"resource-descriptor", "render-thing", "pcrtid"},
    },
}

STRING_EXPECTATIONS = {
    "string-0063e1ac.tsv": "Warning : deserializing font twice!\\x0a",
    "string-0063e1d4.tsv": r"Software\Lost Toys\Battle Engine Aquila",
    "string-0063e1fc.tsv": "REG_SZ",
    "string-00632b30.tsv": "default.msh",
    "string-0063e26c.tsv": "cannon1.msh",
    "string-0063e260.tsv": "radar1.msh",
    "string-0063e254.tsv": "plane1.msh",
    "string-0063e248.tsv": "tree2.msh",
    "string-0063e238.tsv": "Enemymech.msh",
    "string-0063e22c.tsv": "bloke.msh",
    "string-0063e21c.tsv": "EnemyT~1.msh",
    "string-0063e210.tsv": "shell.msh",
    "string-00623608.tsv": "cockpit2.msh",
    "string-0063e204.tsv": "carrier.msh",
    "string-0063e278.tsv": "tank1.msh",
}

CORE_DOC_TOKENS = (
    TASK,
    "pc-platform-resource-tail-wave852",
    "0x00515ab0 D3DDevice__SetViewport",
    "0x00515b10 PCPlatform__DeserializeFontsAndAssets",
    "0x00515db0 Registry__SetStringValue_HKCU",
    "0x00515f60 CResourceDescriptorTable__ctor",
    "0x00515fb0 CResourceDescriptorTable__InitDefaultMeshNames",
    "0x00516450 CResourceDescriptorTable__FreeAllEntries",
    "0x005164b0 CResourceDescriptorTable__InstantiateChain",
    "5736/6098 = 94.06%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime d3d viewport behavior proven",
    "runtime font/resource loading proven",
    "runtime registry side effects proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
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
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 14,
        "pre-instructions.tsv": 2107,
        "pre-decompile/index.tsv": 7,
        "pre-context-metadata.tsv": 9,
        "pre-context-decompile/index.tsv": 9,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 14,
        "post-instructions.tsv": 2107,
        "post-decompile/index.tsv": 7,
        "post-context-metadata.tsv": 9,
        "post-context-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"common tags missing at {address}", failures)
            require(set(expected["tags"]).issubset(actual_tags), f"specific tags missing at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    source = read_text(BASE / "source-context.txt")
    for token in ("PCPlatform.cpp", "CPCPlatform::SetViewport", "LT.D3D_SetViewport", "RegSetValueEx", "ResourceAccumulator", "CThing::AccumulateResources"):
        require(token in source, f"missing source context token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 14 rows",
        "post-instructions.log": "Wrote 2107 instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-context-metadata.log": "targets=9 found=9 missing=0",
        "post-context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5736",
        "queue-probe.log": "Commentless functions: 362",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave852.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave852_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 362, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5736, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5736, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005168d0", "raw head address mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CPCSoundManager__dtor", "raw head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 172034951, "backup byte count mismatch", failures)
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
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    common_owner_tokens = (TASK, "pc-platform-resource-tail-wave852", "5736/6098 = 94.06%", NEXT_HEAD, BACKUP_PATH)
    owner_docs = {
        PCPLATFORM_DOC: (
            "0x00515ab0 D3DDevice__SetViewport",
            "0x00515b10 PCPlatform__DeserializeFontsAndAssets",
            "0x00515db0 Registry__SetStringValue_HKCU",
            "Warning : deserializing font twice!",
        ),
        RESOURCE_ACCUMULATOR_DOC: (
            "0x00515b10 PCPlatform__DeserializeFontsAndAssets",
            "CResourceAccumulator__ReadResourceFile",
            "CDXBitmapFont__Deserialize",
        ),
        LTSHELL_DOC: (
            "0x00515fb0 CResourceDescriptorTable__InitDefaultMeshNames",
            "0x00516450 CResourceDescriptorTable__FreeAllEntries",
            "default.msh",
        ),
        THING_DOC: (
            "0x005164b0 CResourceDescriptorTable__InstantiateChain",
            "CThing__InitRenderThing",
            "PCRTID__CreateObject",
        ),
        CONSOLE_DOC: (
            "0x00515db0 Registry__SetStringValue_HKCU",
            "Software\\Lost Toys\\Battle Engine Aquila",
            "RegSetValueExA",
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in common_owner_tokens + tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-pc-platform-resource-tail-wave852")
        == r"py -3 tools\ghidra_pc_platform_resource_tail_wave852_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave852 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20507 for row in attempts), "missing Wave852 attempt row", failures)


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
        print("Wave852 PC platform/resource tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave852 PC platform/resource tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
