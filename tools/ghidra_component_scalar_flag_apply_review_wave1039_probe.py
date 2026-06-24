#!/usr/bin/env python3
"""Validate Wave1039 component scalar/flag apply-strip review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1039-component-value-scalar-flag-apply-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_component_scalar_flag_apply_review_wave1039_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1039_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-075609_post_wave1039_component_value_scalar_flag_apply_review_verified"

SCALAR_TARGETS = {
    "0x0043ca70": ("CComponentScalarD8__ApplyToComponentByName", "0x005daac4", "0xd8"),
    "0x0043cb40": ("CComponentScalarDC__ApplyToComponentByName", "0x005daab0", "0xdc"),
    "0x0043cbe0": ("CComponentScalarC0__ApplyToComponentByName", "0x005daa9c", "0xc0"),
    "0x0043cc80": ("CComponentScalar158__ApplyToComponentByName", "0x005daa88", "0x158"),
    "0x0043cd20": ("CComponentScalarB8__ApplyToComponentByName", "0x005daa38", "0xb8"),
    "0x0043cdc0": ("CComponentScalarBC__ApplyToComponentByName", "0x005daa10", "0xbc"),
    "0x0043d460": ("CComponentScalar160__ApplyToComponentByName", "0x005da998", "0x160"),
}

FLAG_TARGETS = {
    "0x0043ce60": ("CComponentFlag124__ApplyToComponentByName", "0x005da9e8", "0x124"),
    "0x0043cf20": ("CComponentFlag128__ApplyToComponentByName", "0x005da9d4", "0x128"),
    "0x0043cfe0": ("CComponentFlag12C__ApplyToComponentByName", "0x005da984", "0x12c"),
    "0x0043d0a0": ("CComponentFlag198__ApplyToComponentByName", "0x005da95c", "0x198"),
    "0x0043d160": ("CComponentFlag114__ApplyToComponentByName", "0x005da948", "0x114"),
    "0x0043d220": ("CComponentFlag19C__ApplyToComponentByName", "0x005da934", "0x19c"),
    "0x0043d2e0": ("CComponentFlag134__ApplyToComponentByName", "0x005da920", "0x134"),
    "0x0043d3a0": ("CComponentFlag108__ApplyToComponentByName", "0x005da9ac", "0x108"),
}

TARGETS = {**SCALAR_TARGETS, **FLAG_TARGETS}

DOC_TOKENS = (
    "Wave1039",
    "component-scalar-flag-apply-review-wave1039",
    "0x0043ca70 CComponentScalarD8__ApplyToComponentByName",
    "0x0043d460 CComponentScalar160__ApplyToComponentByName",
    "0x0043ce60 CComponentFlag124__ApplyToComponentByName",
    "0x0043d3a0 CComponentFlag108__ApplyToComponentByName",
    "DAT_00855400",
    "0x005d856c",
    "positive-only wording",
    "711/1408 = 50.50%",
    "940/1493 = 62.96%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "comment/tag correction",
)

OVERCLAIMS = (
    "runtime physicsscript application behavior proven",
    "runtime component behavior proven",
    "mission-script outcomes proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


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


def decompile_path(address: str, name: str, post: bool = True) -> Path:
    root = BASE / ("post-decompile" if post else "decompile")
    return root / f"{address[2:]}_{name}.c"


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "post-metadata.tsv": 15,
        "post-tags.tsv": 15,
        "post-xrefs.tsv": 15,
        "post-instructions.tsv": 1070,
        "post-decompile/index.tsv": 15,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    instructions = read_tsv(BASE / "post-instructions.tsv")

    for address, (name, xref_addr, record_offset) in TARGETS.items():
        signature = f"void __thiscall {name}(void * this, char * componentName)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave1039", "DAT_00855400", "this+0x8", record_offset):
                require(token in comment, f"missing comment token at {address}: {token}", failures)
            if address in FLAG_TARGETS:
                for token in ("0x005d856c", "zero-comparison path", "positive-only wording"):
                    require(token in comment, f"missing flag correction token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            for token in (
                "static-reaudit",
                "component-scalar-flag-apply-review-wave1039",
                "wave1039-readback-verified",
                "physics-script",
                "physics-script-wave343",
                "component-apply",
                "component-value-tranche",
                "comment-hardened",
            ):
                require(token in tag_text, f"missing tag at {address}: {token}", failures)
            if address in SCALAR_TARGETS:
                require("offset-backed-scalar" in tag_text, f"missing scalar tag at {address}", failures)
            else:
                require("offset-backed-flag" in tag_text, f"missing flag tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref at {address}", failures)
        if xref is not None:
            require(normalize_address(xref.get("from_addr", "")) == xref_addr, f"xref mismatch at {address}", failures)
            require(xref.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)

        decompiled = read_text(decompile_path(address, name))
        require("DAT_00855400" in decompiled, f"missing component list token at {address}", failures)
        if address in SCALAR_TARGETS:
            decimal_offset = str(int(record_offset, 16))
            require(
                record_offset in decompiled or f"iVar5 + {decimal_offset}" in decompiled,
                f"missing scalar offset token at {address}: {record_offset}",
                failures,
            )
        else:
            relevant = [
                instr
                for instr in instructions
                if normalize_address(instr.get("target_addr", "")) == address
                and instr.get("mnemonic") in {"FCOMP", "TEST", "MOV"}
            ]
            text = "\n".join(instr.get("operands", "") for instr in relevant)
            require("0x005d856c" in text or "0x005d856c" in decompiled, f"missing zero constant at {address}", failures)
            require(f"[EDI + {record_offset}]" in text, f"missing flag store at {address}: {record_offset}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=15 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=15 tags_added=60 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=15 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=15 tags_added=60 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=15 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=15 found=15 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "post-xrefs.log": "Wrote 15 rows",
        "post-instructions.log": "Wrote 1070 function-body instruction rows",
        "post-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 174001031, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash-diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        PHYSICS_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIMS:
            require(token not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-component-scalar-flag-apply-review-wave1039")
        == r"py -3 tools\ghidra_component_scalar_flag_apply_review_wave1039_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1039-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1039 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1039 component scalar flag apply review" for row in ledger), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1039 component scalar flag apply review" and row.get("attempt_id") == 20621 for row in attempts),
        "missing attempt row",
        failures,
    )


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
        print("Wave1039 component scalar/flag apply review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1039 component scalar/flag apply review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
