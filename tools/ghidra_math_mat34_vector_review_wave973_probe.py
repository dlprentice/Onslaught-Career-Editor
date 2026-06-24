#!/usr/bin/env python3
"""Validate Wave973 math/Mat34 vector review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave973-math-mat34-vector-review"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_math_mat34_vector_review_wave973_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-192743_post_wave973_math_mat34_vector_review_verified"

TARGET = {
    "address": "0x0040c990",
    "name": "CBattleEngine__GetLaunchPosition",
    "signature": "void __thiscall CBattleEngine__GetLaunchPosition(void * this, void * inWeapon, int inIndex, void * outPos, void * outOrientation, int inNeedOrientation)",
    "comment_tokens": (
        "Wave973 math/Mat34 vector review boundary recovery",
        "CBattleEngine::GetLaunchPosition",
        "0x0040d0ed",
        "RET 0x14",
        "Vec3__ElevationOrZero",
        "Mat34__SetFromEulerAngles",
        "references/Onslaught/BattleEngine.cpp lines 3000-3069",
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "math-mat34-vector-review-wave973",
    "wave973-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "battleengine",
    "launch-position",
    "mat34",
    "vector-math",
    "source-backed",
    "comment-hardened",
    "signature-hardened",
}

CORE_TOKENS = (
    "Wave973",
    "math-mat34-vector-review-wave973",
    "0x0040c990 CBattleEngine__GetLaunchPosition",
    "0x0040d1a0 Vec3__ElevationOrZero",
    "0x0040d1f0 Mat34__SetFromEulerAngles",
    "0x0040d2c0 Mat34__TransformVec3ByBasisToOut",
    "0x0040d320 Mat34__MultiplyBasisToOut",
    "0x005b86c0 CFastVB__FastAcosApprox_Scalar",
    "350/1408 = 24.86%",
    "408/1466 = 27.83%",
    "6210/6210 = 100.00%",
    BACKUP_PATH,
    "function-boundary recovery",
)

OVERCLAIMS = (
    "runtime launch-position behavior proven",
    "runtime projectile behavior proven",
    "runtime auto-aim behavior proven",
    "rebuild parity proven",
    "fully reverse-engineered",
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
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 152,
        "instructions.tsv": 294,
        "decompile/index.tsv": 5,
        "nofunction-around.tsv": 1050,
        "gap-0040c720-0040d0f0.tsv": 498,
        "create-dry.tsv": 1,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 153,
        "post-instructions.tsv": 777,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} count mismatch: {actual} != {expected}", failures)

    create_rows = read_tsv(BASE / "create-dry.tsv")
    require(create_rows and normalize_address(create_rows[0].get("address", "")) == TARGET["address"], "create dry address mismatch", failures)
    require(create_rows and create_rows[0].get("status") == "would_create", "create dry status mismatch", failures)

    gap_text = read_text(BASE / "gap-0040c720-0040d0f0.tsv")
    for token in ("0040c990", "MOV\tEAX, FS:[0x0]", "0040d090", "0040d0b0", "0040d0ed", "RET\t0x14"):
        require(token in gap_text, f"missing gap token: {token}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = [row for row in read_tsv(BASE / "post-xrefs.tsv") if normalize_address(row.get("target_addr", "")) == TARGET["address"]]

    row = metadata.get(TARGET["address"])
    require(row is not None, "missing recovered target metadata", failures)
    if row is not None:
        require(row.get("name") == TARGET["name"], "recovered target name mismatch", failures)
        require(row.get("signature") == TARGET["signature"], f"recovered target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "recovered target metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in TARGET["comment_tokens"]:
            require(token in comment, f"missing recovered target comment token: {token}", failures)

    tag_row = tags.get(TARGET["address"])
    require(tag_row is not None, "missing recovered target tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)

    dec = decompile.get(TARGET["address"])
    require(dec is not None, "missing recovered target decompile row", failures)
    if dec is not None:
        require(dec.get("signature") == TARGET["signature"], "recovered target decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "recovered target decompile status mismatch", failures)

    require(any(normalize_address(row.get("from_addr", "")) == "0x005d8af0" and row.get("ref_type") == "DATA" for row in xrefs), "missing 0x005d8af0 DATA xref", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "rows=6 missing=0",
        "post-xrefs.log": "Wrote 153 rows",
        "post-instructions.log": "Wrote 777 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "export-functions-quality-wave973.log": "total_functions=6210 commented_functions=6210",
        "wave973_queue_probe.log": "Total functions: 6210",
    }
    aliases = {
        "export-functions-quality-wave973.log": QUEUE / "export-functions-quality-wave973.log",
        "wave973_queue_probe.log": QUEUE / "wave973_queue_probe.log",
    }
    for relative, token in expected_logs.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue = read_json(QUEUE / "static-reaudit-queue.json")
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6210, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain owner count mismatch", failures)
    require(quality["helperAddressNameCount"] == 0, "address helper count mismatch", failures)
    require(quality["wrapperAddressNameCount"] == 0, "address wrapper count mismatch", failures)

    rows = read_tsv(QUEUE / "functions_quality.tsv")
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6210, "quality TSV row count mismatch", failures)
    require(commented == 6210, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6210, "strict clean-signature count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173771655, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, BATTLEENGINE_DOC, MATH_DOC, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-math-mat34-vector-review-wave973")
        == r"py -3 tools\ghidra_math_mat34_vector_review_wave973_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave973 math Mat34 vector review" for row in ledger_rows), "missing Wave973 ledger row", failures)
    require(
        any(row.get("task") == "Wave973 math Mat34 vector review" and row.get("attempt_id") == 20569 for row in attempts),
        "missing Wave973 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave973 math/Mat34 vector review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave973 math/Mat34 vector review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
