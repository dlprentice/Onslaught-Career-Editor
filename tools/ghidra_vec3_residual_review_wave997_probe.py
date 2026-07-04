#!/usr/bin/env python3
"""Validate Wave997 Vec3 residual read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave997-vec3-residual-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_vec3_residual_review_wave997_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-083022_post_wave997_vec3_residual_review_verified"

TARGETS = {
    "0x0041ad10": ("Vec3__AddInPlace", "void __thiscall Vec3__AddInPlace(void * this, void * add_vec3)"),
    "0x00490900": ("Vec3__SubtractInPlace", "void __thiscall Vec3__SubtractInPlace(void * this, void * rhs_vector)"),
    "0x004404f0": ("Vec3__NegateToOut", "void __thiscall Vec3__NegateToOut(void * this, void * outVec)"),
    "0x004c7d90": ("Vec3__CopyXYZ", "void * __thiscall Vec3__CopyXYZ(void * this, void * src_vec3)"),
    "0x004c7900": ("Vec3__NormalizeInPlace", "void __thiscall Vec3__NormalizeInPlace(void * this)"),
}

COMMENT_TOKENS = {
    "0x0041ad10": ("owner-neutral Vec3", "RET 0x4", "CMCTentacle-only owner label too narrow"),
    "0x00490900": ("RET 0x4", "subtracts rhs_vector"),
    "0x004404f0": ("FCHS", "RET 0x4", "Vec3 negate-to-output"),
    "0x004c7d90": ("three-dword copy", "RET 0x4", "EAX returns the destination pointer"),
    "0x004c7900": ("squared magnitude", "DAT_005d856c", "sqrt(length_sq)"),
}

DOC_TOKENS = (
    "Wave997",
    "vec3-residual-review-wave997",
    "0x0041ad10 Vec3__AddInPlace",
    "0x00490900 Vec3__SubtractInPlace",
    "0x004404f0 Vec3__NegateToOut",
    "0x004c7d90 Vec3__CopyXYZ",
    "0x004c7900 Vec3__NormalizeInPlace",
    "465/1408 = 33.03%",
    "581/1478 = 39.31%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime math behavior proven",
    "runtime render behavior proven",
    "runtime collision behavior proven",
    "exact vec3 layout proven",
    "source identity proven",
    "rebuild parity proven",
)

EXPECTED_LOG_TOKENS = {
    "pre-metadata.log": ("targets=5 found=5 missing=0", "REPORT: Save succeeded"),
    "pre-tags.log": ("ExportFunctionTagsByAddress complete: rows=5 missing=0", "REPORT: Save succeeded"),
    "pre-xrefs.log": ("Wrote 45 rows", "REPORT: Save succeeded"),
    "pre-instructions.log": ("Wrote 73 function-body instruction rows", "targets=5 missing=0", "REPORT: Save succeeded"),
    "pre-decompile.log": ("targets=5 dumped=5 missing=0 failed=0", "REPORT: Save succeeded"),
}


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    if token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text:
        return True

    def collapse_backslashes(value: str) -> str:
        previous = None
        current = value
        while previous != current:
            previous = current
            current = current.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
        return current

    return collapse_backslashes(token) in collapse_backslashes(text)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 45,
        "pre-instructions.tsv": 73,
        "pre-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "pre-metadata.tsv")
    tags = read_tsv(BASE / "pre-tags.tsv")
    decompile_index = read_tsv(BASE / "pre-decompile" / "index.tsv")

    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            require(comment.strip() != "", f"metadata comment missing {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"comment token missing {address}: {token}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag {address}", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    expected_xrefs = (
        ("0x0041ad10", "0x004b57dc", "UNCONDITIONAL_CALL"),
        ("0x0041ad10", "0x004940d7", "UNCONDITIONAL_CALL"),
        ("0x004404f0", "0x00542dd7", "UNCONDITIONAL_CALL"),
        ("0x004404f0", "0x0053dd08", "UNCONDITIONAL_CALL"),
        ("0x00490900", "0x004c512d", "UNCONDITIONAL_CALL"),
        ("0x004c7900", "0x004c749e", "UNCONDITIONAL_CALL"),
        ("0x004c7d90", "0x0053ddb4", "UNCONDITIONAL_CALL"),
        ("0x004c7d90", "0x00543275", "UNCONDITIONAL_CALL"),
    )
    for target, source, ref_type in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == source
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {source} -> {target} {ref_type}",
            failures,
        )

    instructions = read_tsv(BASE / "pre-instructions.tsv")
    instruction_checks = (
        ("0x0041ad10", "0x0041ad2c", "RET", "0x4"),
        ("0x00490900", "0x0049091c", "RET", "0x4"),
        ("0x004404f0", "0x0044050a", "RET", "0x4"),
        ("0x004c7d90", "0x004c7da6", "RET", "0x4"),
        ("0x004c7900", "0x004c792b", "FSQRT", ""),
        ("0x004c7900", "0x004c7947", "RET", ""),
    )
    for target, instr_addr, mnemonic, operand in instruction_checks:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and row.get("instruction_addr") == instr_addr
                and row.get("mnemonic") == mnemonic
                and row.get("operands") == operand
                for row in instructions
            ),
            f"missing instruction {target} {instr_addr} {mnemonic} {operand}",
            failures,
        )


def check_logs_and_backup(failures: list[str]) -> None:
    for relative, tokens in EXPECTED_LOG_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (NOTE, GHIDRA_REFERENCE, CAMPAIGN, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE)
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token {path.relative_to(ROOT)}: {bad}", failures)

    targeted_docs = {
        FUNCTION_INDEX: ("Wave997", "Math.cpp", "Vec3 residual"),
        FUNCTION_COVERAGE: ("Wave997", "vec3-residual-review-wave997", "0x0041ad10", "0x004c7900", BACKUP_PATH),
        MATH_DOC: (
            "Wave997",
            "vec3-residual-review-wave997",
            "0x0041ad10 Vec3__AddInPlace",
            "0x00490900 Vec3__SubtractInPlace",
            "0x004404f0 Vec3__NegateToOut",
            "0x004c7d90 Vec3__CopyXYZ",
            "0x004c7900 Vec3__NormalizeInPlace",
            "581/1478 = 39.31%",
            BACKUP_PATH,
        ),
    }
    for path, tokens in targeted_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing doc token {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-vec3-residual-review-wave997")
        == r"py -3 tools\ghidra_vec3_residual_review_wave997_probe.py --check",
        "missing package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave997 Vec3 residual review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave997 Vec3 residual review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
