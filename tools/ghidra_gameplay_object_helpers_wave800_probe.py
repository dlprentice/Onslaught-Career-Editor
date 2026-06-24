#!/usr/bin/env python3
"""Validate Wave800 gameplay-object helper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave800-gameplay-object-helpers"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_gameplay_object_helpers_wave800_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MCBUGGY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MCBuggy.cpp" / "_index.md"
DIVEBOMBER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DiveBomber.cpp" / "_index.md"
DIVEBOMBER_DETAIL = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DiveBomber.cpp" / "CDiveBomber__SelectTarget.md"
MINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mine.cpp" / "_index.md"
OIDS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "oids.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-070217_post_wave800_gameplay_object_helpers_verified"
NEXT_RAW_HEAD = "0x0044a0c0"

TARGETS = {
    "0x00445010": {
        "name": "CMCBuggy__GetTargetValueOrFallback",
        "signature": "float __thiscall CMCBuggy__GetTargetValueOrFallback(void * this, int target_id)",
        "comment": ("Wave800 static read-back", "RET 0x4", "0x005d856c", "CDestructableSegmentsMotionController__ApplyRumbleTransform"),
        "tags": {"cmcbuggy", "target-value", "signature-corrected", "ret-0x4", "tranche-head"},
    },
    "0x00445070": {
        "name": "CDiveBomber__SelectTarget",
        "signature": "void __thiscall CDiveBomber__SelectTarget(void * this, void * out_target_position)",
        "comment": ("Wave800 static read-back", "CCannon__SelectTarget", "single stack output pointer", "CThing__GetCentrePos"),
        "tags": {"divebomber", "target-selection", "signature-corrected", "out-position"},
    },
    "0x00449560": {
        "name": "Vec3__AssignFromValuePointersAndReturnThis",
        "signature": "void * __thiscall Vec3__AssignFromValuePointersAndReturnThis(void * this, float * x_value, float * y_value, float * z_value)",
        "comment": ("Wave800 static read-back", "owner-neutral Vec3 assignment helper", "CMine__Init", "older CMine-specific owner label was too narrow"),
        "tags": {"vec3", "mine-context", "name-corrected", "signature-corrected", "ret-0xc"},
    },
    "0x00449d40": {
        "name": "OID__FreeObject_Callback",
        "signature": "void __cdecl OID__FreeObject_Callback(void * ptr)",
        "comment": ("Wave800 static read-back", "657 current xrefs", "0x009c3df0", "CDXMemoryManager__Free"),
        "tags": {"oid", "cleanup-callback", "memory-manager-free", "tranche-tail"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "gameplay-object-helpers-wave800",
    "wave800-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
}

EXPECTED_XREF_COUNTS = {
    "0x00445010": 1,
    "0x00445070": 1,
    "0x00449560": 2,
    "0x00449d40": 657,
}

EXPECTED_XREFS = {
    ("0x00445010", "0x00494cfa", "CDestructableSegmentsMotionController__ApplyRumbleTransform"),
    ("0x00445070", "0x004fd4e1", "CCannon__SelectTarget"),
    ("0x00449560", "0x004ba41e", "CMine__Init"),
    ("0x00449560", "0x004494b8", "<no_function>"),
}

EXPECTED_INSTRUCTIONS = {
    ("0x00445010", "0x00445019", "MOV", "EDI, dword ptr [ESP + 0xc]"),
    ("0x00445010", "0x00445047", "FLD", "float ptr [0x005d856c]"),
    ("0x00445070", "0x0044504f", "RET", "0x4"),
    ("0x00445070", "0x004450aa", "MOV", "EAX, dword ptr [EBX + 0x160]"),
    ("0x00445070", "0x004450b7", "MOV", "ECX, dword ptr [EDI + 0x88]"),
    ("0x00449560", "0x00449560", "MOV", "EAX, ECX"),
    ("0x00449560", "0x0044956c", "MOV", "dword ptr [EAX], EDX"),
    ("0x00449560", "0x00449579", "MOV", "dword ptr [EAX + 0x8], EDX"),
    ("0x00449560", "0x0044957c", "RET", "0xc"),
    ("0x00449d40", "0x00449d44", "MOV", "ECX, 0x9c3df0"),
    ("0x00449d40", "0x00449d4a", "CALL", "0x00549220"),
    ("0x00449d40", "0x00449d4f", "RET", ""),
}

CORE_ANCHORS = (
    "Wave800 gameplay object helpers",
    "gameplay-object-helpers-wave800",
    "0x00445010 CMCBuggy__GetTargetValueOrFallback",
    "0x00445070 CDiveBomber__SelectTarget",
    "0x00449560 Vec3__AssignFromValuePointersAndReturnThis",
    "0x00449d40 OID__FreeObject_Callback",
    "0x0044a0c0 CDXMeshVB__GetGlobalZeroDouble",
    "0 exact-undefined signatures",
    "0 param_N signatures",
    "5556/6098 = 91.11%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime targeting behavior proven",
    "runtime mine behavior proven",
    "runtime allocator behavior proven",
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
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 661,
        "pre-instructions.tsv": 148,
        "pre-decompile/index.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 661,
        "post-instructions.tsv": 148,
        "post-decompile/index.tsv": 4,
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

    xref_rows = read_tsv(BASE / "post-xrefs.tsv")
    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row.get("from_function", ""))
        for row in xref_rows
    }
    require(EXPECTED_XREFS.issubset(xrefs), f"xref set missing: {EXPECTED_XREFS - xrefs}", failures)
    for address, expected_count in EXPECTED_XREF_COUNTS.items():
        actual_count = sum(1 for row in xref_rows if normalize_address(row["target_addr"]) == address)
        require(actual_count == expected_count, f"xref count mismatch at {address}: {actual_count}", failures)

    instructions = {
        (normalize_address(row["target_addr"]), normalize_address(row["instruction_addr"]), row.get("mnemonic", ""), row.get("operands", ""))
        for row in read_tsv(BASE / "post-instructions.tsv")
    }
    require(EXPECTED_INSTRUCTIONS.issubset(instructions), f"instruction set missing: {EXPECTED_INSTRUCTIONS - instructions}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=1 signature_updated=3 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=1 would_rename=0 signature_updated=3 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 661 rows",
        "post-instructions.log": "Wrote 148 instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5556",
        "queue-probe.log": "Commentless functions: 542",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave800.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave800_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 542, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "commentless high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5556, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5556, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == NEXT_RAW_HEAD, "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXMeshVB__GetGlobalZeroDouble", "raw commentless head name mismatch", failures)

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
        MCBUGGY_DOC: ("Wave800 gameplay object helpers", "gameplay-object-helpers-wave800", "0x00445010 CMCBuggy__GetTargetValueOrFallback", "RET 0x4", BACKUP_PATH),
        DIVEBOMBER_DOC: ("Wave800 gameplay object helpers", "0x00445070 CDiveBomber__SelectTarget", "out_target_position", "CCannon__SelectTarget", BACKUP_PATH),
        DIVEBOMBER_DETAIL: ("Wave800 gameplay object helpers", "void __thiscall CDiveBomber__SelectTarget(void * this, void * out_target_position)", "older no-argument return-pointer signature was incomplete", BACKUP_PATH),
        MINE_DOC: ("Wave800 gameplay object helpers", "0x00449560 Vec3__AssignFromValuePointersAndReturnThis", "CMine__AssignVec3AndReturnThis", "owner-neutral Vec3", BACKUP_PATH),
        OIDS_DOC: ("Wave800 gameplay object helpers", "0x00449d40 OID__FreeObject_Callback", "CDXMemoryManager__Free", "657 current xrefs", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-gameplay-object-helpers-wave800")
        == r"py -3 tools\ghidra_gameplay_object_helpers_wave800_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave800 gameplay object helpers" for row in read_jsonl(LEDGER)), "missing Wave800 ledger row", failures)
    require(any(row.get("task") == "Wave800 gameplay object helpers" and row.get("attempt_id") == 20455 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave800 attempt row", failures)


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
        print("Wave800 gameplay-object helpers probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave800 gameplay-object helpers probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
