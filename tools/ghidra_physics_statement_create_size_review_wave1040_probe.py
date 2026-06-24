#!/usr/bin/env python3
"""Validate Wave1040 PhysicsScript statement create/size review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1040-physics-statement-create-size-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_statement_create_size_review_wave1040_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1040_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-082926_post_wave1040_physics_statement_create_size_review_verified"

TARGETS = {
    "0x0042ede0": ("CUnitStatement__CreateUnitAndRecurse", "void __fastcall CUnitStatement__CreateUnitAndRecurse(void * this)"),
    "0x0042f230": ("CUnitStatement__GetSerializedSize", "int __fastcall CUnitStatement__GetSerializedSize(void * this)"),
    "0x0042f280": ("CPhysicsUnitValueList__GetSerializedSize", "int __fastcall CPhysicsUnitValueList__GetSerializedSize(void * this)"),
    "0x0042f4b0": ("CPhysicsUnitValueList__scalar_deleting_dtor", "void * __thiscall CPhysicsUnitValueList__scalar_deleting_dtor(void * this, int flags)"),
    "0x0042f5b0": ("CWeaponStatement__CreateWeaponAndRecurse", "void __fastcall CWeaponStatement__CreateWeaponAndRecurse(void * this)"),
    "0x0042f700": ("CWeaponStatement__GetSerializedSize", "int __fastcall CWeaponStatement__GetSerializedSize(void * this)"),
    "0x0042f750": ("CPhysicsWeaponValueList__GetSerializedSize", "int __fastcall CPhysicsWeaponValueList__GetSerializedSize(void * this)"),
    "0x0042f980": ("CPhysicsWeaponValueList__scalar_deleting_dtor", "void * __thiscall CPhysicsWeaponValueList__scalar_deleting_dtor(void * this, int flags)"),
    "0x0042fa40": ("CWeaponModeStatement__CreateWeaponModeAndRecurse", "void __fastcall CWeaponModeStatement__CreateWeaponModeAndRecurse(void * this)"),
    "0x0042fc20": ("CWeaponModeStatement__GetSerializedSize", "int __fastcall CWeaponModeStatement__GetSerializedSize(void * this)"),
    "0x0042fc70": ("CPhysicsWeaponModeValueList__GetSerializedSize", "int __fastcall CPhysicsWeaponModeValueList__GetSerializedSize(void * this)"),
    "0x0042fea0": ("CPhysicsWeaponModeValueList__scalar_deleting_dtor", "void * __thiscall CPhysicsWeaponModeValueList__scalar_deleting_dtor(void * this, int flags)"),
    "0x0042ff60": ("CRoundStatement__CreateRoundAndRecurse", "void __fastcall CRoundStatement__CreateRoundAndRecurse(void * this)"),
    "0x00430190": ("CRoundStatement__GetSerializedSize", "int __fastcall CRoundStatement__GetSerializedSize(void * this)"),
    "0x004301e0": ("CPhysicsRoundValueList__GetSerializedSize", "int __fastcall CPhysicsRoundValueList__GetSerializedSize(void * this)"),
    "0x00430410": ("CPhysicsRoundValueList__scalar_deleting_dtor", "void * __thiscall CPhysicsRoundValueList__scalar_deleting_dtor(void * this, int flags)"),
}

DTORS = {
    "0x0042f4b0": "0x005d988c",
    "0x0042f980": "0x005d98a8",
    "0x0042fea0": "0x005d98b0",
    "0x00430410": "0x005d98b8",
}

DATA_XREFS = {
    "0x0042ede0": "0x005d987c",
    "0x0042f230": "0x005d9880",
    "0x0042f4b0": "0x005d988c",
    "0x0042f5b0": "0x005d9854",
    "0x0042f700": "0x005d9858",
    "0x0042f980": "0x005d98a8",
    "0x0042fa40": "0x005d9868",
    "0x0042fc20": "0x005d986c",
    "0x0042fea0": "0x005d98b0",
    "0x0042ff60": "0x005d9840",
    "0x00430190": "0x005d9844",
    "0x00430410": "0x005d98b8",
}

DOC_TOKENS = (
    "Wave1040",
    "physics-statement-create-size-review-wave1040",
    "0x0042ede0 CUnitStatement__CreateUnitAndRecurse",
    "0x0042f4b0 CPhysicsUnitValueList__scalar_deleting_dtor",
    "0x0042f980 CPhysicsWeaponValueList__scalar_deleting_dtor",
    "0x0042fea0 CPhysicsWeaponModeValueList__scalar_deleting_dtor",
    "0x00430410 CPhysicsRoundValueList__scalar_deleting_dtor",
    "CDXMemoryManager__Free",
    "0x00549220",
    "DAT_009c3df0",
    "727/1408 = 51.63%",
    "956/1493 = 64.03%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "comment/tag correction",
)

OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime lifetime behavior proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 16,
        "tags.tsv": 16,
        "xrefs.tsv": 20,
        "instructions.tsv": 442,
        "decompile/index.tsv": 16,
        "context-metadata.tsv": 1,
        "context-decompile/index.tsv": 1,
        "post-metadata.tsv": 16,
        "post-tags.tsv": 16,
        "post-xrefs.tsv": 20,
        "post-instructions.tsv": 442,
        "post-decompile/index.tsv": 16,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    instructions = read_tsv(BASE / "post-instructions.tsv")
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    xref_pairs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row.get("ref_type", ""))
        for row in xrefs
    }

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            for token in (
                "static-reaudit",
                "physics-statement-create-size-review-wave1040",
                "wave1040-readback-verified",
                "physics-script",
                "statement-create-size",
            ):
                require(token in tag_text, f"missing tag at {address}: {token}", failures)
            if address in DTORS:
                for token in ("comment-corrected", "memory-manager-free", "destructor", "value-list"):
                    require(token in tag_text, f"missing dtor tag at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for address, from_addr in DATA_XREFS.items():
        require((address, from_addr, "DATA") in xref_pairs, f"missing DATA xref {from_addr} -> {address}", failures)

    for address, vtable in DTORS.items():
        row = metadata[address]
        comment = row.get("comment", "")
        for token in (
            "Wave1040 static re-audit correction",
            vtable,
            "CDXMemoryManager__Free",
            "0x00549220",
            "DAT_009c3df0",
            "not OID__FreeObject",
        ):
            require(token in comment, f"missing dtor comment token at {address}: {token}", failures)
        require("optionally calls OID__FreeObject" not in comment, f"stale OID wording remains at {address}", failures)

        instr_text = "\n".join(
            f"{row.get('mnemonic')} {row.get('operands')}"
            for row in instructions
            if normalize_address(row.get("target_addr", "")) == address
        )
        require("MOV ECX, 0x9c3df0" in instr_text, f"missing memory-manager ECX load at {address}", failures)
        require("CALL 0x00549220" in instr_text, f"missing CDXMemoryManager__Free call at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    helper = context.get("0x00549220")
    require(helper is not None, "missing CDXMemoryManager__Free context metadata", failures)
    if helper is not None:
        require(helper.get("name") == "CDXMemoryManager__Free", "context helper name mismatch", failures)
        require("not OID object freeing" in helper.get("comment", ""), "context helper comment missing OID boundary", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=16 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=16 found=16 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "post-xrefs.log": "Wrote 20 rows",
        "post-instructions.log": "Wrote 442 function-body instruction rows",
        "post-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "context-metadata.log": "targets=1 found=1 missing=0",
        "context-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
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
        BACKLOG,
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
        scripts.get("test:ghidra-physics-statement-create-size-review-wave1040")
        == r"py -3 tools\ghidra_physics_statement_create_size_review_wave1040_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1040-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1040 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1040 physics statement create size review" for row in ledger), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1040 physics statement create size review" and row.get("attempt_id") == 20622 for row in attempts),
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
        print("Wave1040 PhysicsScript statement create/size review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1040 PhysicsScript statement create/size review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
