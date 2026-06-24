#!/usr/bin/env python3
"""Validate Wave798 Vec3 negate helper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave798-cthing-negate-vec3"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_vec3_negate_wave798_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-060456_post_wave798_vec3_negate_verified"
TARGET = "0x004404f0"
TARGET_NAME = "Vec3__NegateToOut"
TARGET_SIGNATURE = "void __thiscall Vec3__NegateToOut(void * this, void * outVec)"
NEXT_RAW_HEAD = "0x00441730"

COMMON_TAGS = {
    "static-reaudit",
    "vec3-negate-wave798",
    "wave798-readback-verified",
    "retail-binary-evidence",
    "name-corrected",
    "signature-corrected",
    "comment-hardened",
    "vector-math",
    "owner-neutral",
}

EXPECTED_CALLERS = {
    "CDXEngine__BuildDirectionalSampleRing",
    "CThing__RenderDebugVolumeOverlay",
    "CMCMech__UpdateBone",
    "CMCBuggy__UpdateWheel",
    "CCylinder__ResolveCollisionVFunc02",
    "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    "<no_function>",
}

CORE_ANCHORS = (
    "Wave798 Vec3 negate helper",
    "vec3-negate-wave798",
    "0x004404f0 Vec3__NegateToOut",
    "0x00441730 CLIParams__SetField04",
    "0 exact-undefined signatures",
    "0 param_N signatures",
    "5546/6098 = 90.95%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime math behavior proven",
    "runtime collision behavior proven",
    "runtime render behavior proven",
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
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 11,
        "pre-instructions.tsv": 65,
        "pre-decompile/index.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 11,
        "post-instructions.tsv": 65,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    row = metadata.get(TARGET)
    require(row is not None, "missing post metadata target", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, "target signature mismatch", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in (
            "Wave798 static read-back",
            "owner-neutral Vec3 negate-to-output helper",
            "ECX as the source Vec3",
            "[ESP+4]",
            "RET 0x4",
            "older CThing-specific owner label too narrow",
            "rebuild parity remain unproven",
        ):
            require(token in comment, f"missing comment token: {token}", failures)

    tag_row = tags.get(TARGET)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "target tag status mismatch", failures)

    dec = decompile.get(TARGET)
    require(dec is not None, "missing target decompile index", failures)
    if dec is not None:
        require(dec.get("signature") == TARGET_SIGNATURE, "decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    callers = {row.get("from_function", "") for row in xrefs}
    require(EXPECTED_CALLERS.issubset(callers), f"xref caller set missing: {EXPECTED_CALLERS - callers}", failures)
    require(all(row.get("target_name") == TARGET_NAME for row in xrefs), "xref target name mismatch", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    target_body = [row for row in instructions if row.get("function_name") == TARGET_NAME]
    observed = {(row.get("instruction_addr"), row.get("mnemonic"), row.get("operands")) for row in target_body}
    for expected in (
        ("0x004404f0", "FLD", "float ptr [ECX + 0x8]"),
        ("0x004404f3", "FCHS", ""),
        ("0x004404f5", "FLD", "float ptr [ECX + 0x4]"),
        ("0x004404f8", "MOV", "EAX, dword ptr [ESP + 0x4]"),
        ("0x004404fe", "FLD", "float ptr [ECX]"),
        ("0x00440502", "FSTP", "float ptr [EAX]"),
        ("0x00440504", "FSTP", "float ptr [EAX + 0x4]"),
        ("0x00440507", "FSTP", "float ptr [EAX + 0x8]"),
        ("0x0044050a", "RET", "0x4"),
    ):
        require(expected in observed, f"missing instruction tuple: {expected}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 11 rows",
        "post-instructions.log": "Wrote 65 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5546",
        "queue-probe.log": "Commentless functions: 552",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave798.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave798_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 552, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "commentless high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5546, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5546, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == NEXT_RAW_HEAD, "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CLIParams__SetField04", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 18, "backup file count mismatch", failures)
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
        MATH_DOC,
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

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-vec3-negate-wave798") == r"py -3 tools\ghidra_vec3_negate_wave798_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave798 Vec3 negate helper" for row in read_jsonl(LEDGER)), "missing Wave798 ledger row", failures)
    require(any(row.get("task") == "Wave798 Vec3 negate helper" and row.get("attempt_id") == 20453 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave798 attempt row", failures)


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
        print("Wave798 Vec3-negate probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave798 Vec3-negate probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
