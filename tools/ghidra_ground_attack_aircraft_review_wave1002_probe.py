#!/usr/bin/env python3
"""Validate Wave1002 GroundAttackAircraft read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1002-ground-attack-aircraft-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_ground_attack_aircraft_review_wave1002_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1002_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GROUND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GroundAttackAircraft.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
RECHECK_TOOL = ROOT / "tools" / "ghidra_wave900_plus_through_wave983_recheck.py"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-112128_post_wave1002_ground_attack_aircraft_review_verified"

TARGETS = {
    "0x0047bab0": ("CGroundAttackAI__InitState", "void __fastcall CGroundAttackAI__InitState(void * this)"),
    "0x0047bbf0": ("CGroundAttackAircraft__Init", "void __thiscall CGroundAttackAircraft__Init(void * this, void * init_data)"),
    "0x0047bd70": ("CGroundAttackAI__ScalarDeletingDestructor", "void * __thiscall CGroundAttackAI__ScalarDeletingDestructor(void * this, byte flags)"),
    "0x0047bd90": ("CGroundAttackAI__Destructor", "void __fastcall CGroundAttackAI__Destructor(void * this)"),
    "0x0047be30": ("CGroundAttackGuide__ScalarDeletingDestructor", "void * __thiscall CGroundAttackGuide__ScalarDeletingDestructor(void * this, byte flags)"),
    "0x0047be50": ("CGroundAttackGuide__Destructor", "void __fastcall CGroundAttackGuide__Destructor(void * this)"),
    "0x0047bfa0": ("CGroundAttackAircraft__OpenBay", "void __fastcall CGroundAttackAircraft__OpenBay(void * this)"),
    "0x0047bff0": ("CGroundAttackAircraft__CloseBay", "void __fastcall CGroundAttackAircraft__CloseBay(void * this)"),
    "0x0047c040": ("CGroundAttackAircraft__AdvanceCloseShootAnimationState", "int __fastcall CGroundAttackAircraft__AdvanceCloseShootAnimationState(void * this)"),
    "0x0050ee10": ("CGroundAttackAircraft__scalar_deleting_dtor", "void * __thiscall CGroundAttackAircraft__scalar_deleting_dtor(void * this, byte delete_flags)"),
    "0x0050f130": ("CGroundAttackAircraft__Destructor_VFunc01", "void __fastcall CGroundAttackAircraft__Destructor_VFunc01(void * this)"),
    "0x004964d0": ("CMCGroundAttack__Constructor", "void * __thiscall CMCGroundAttack__Constructor(void * this, void * owner_aircraft)"),
    "0x00496500": ("CMCGroundAttack__ScalarDeletingDestructor", "void * __thiscall CMCGroundAttack__ScalarDeletingDestructor(void * this, byte delete_flags)"),
    "0x00496520": ("CMCGroundAttack__Destructor", "void __fastcall CMCGroundAttack__Destructor(void * this)"),
    "0x00496540": ("CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540", "void __thiscall CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)"),
    "0x004968a0": ("CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0", "bool __fastcall CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0(void * this)"),
}

COMMENT_TOKENS = {
    "0x0047bab0": ("Wave391 RTTI owner correction", "CGroundAttackAircraft__Init", "CGroundAttackAircraft__CloseBay"),
    "0x0047bbf0": ("function table 0x005e2bf0 slot 0", "CAirUnit__Init", "CMCGroundAttack"),
    "0x0047bd70": ("CGroundAttackAI vtable 0x005dbd4c slot 1", "flags bit 0", "older GroundAttackAircraft owner label"),
    "0x0047bd90": ("CUnitAI base vtable 0x005d8d1c", "+0x28", "CMonitor__Shutdown"),
    "0x0047be30": ("CGroundAttackGuide vtable 0x005dbd20 slot 1", "stale GillMHead label", "flags bit 0"),
    "0x0047be50": ("CGroundAttackGuide", "+0x2c", "CMonitor__Shutdown"),
    "0x0047bfa0": ("bay state +0x27c", "open animation token", "model animation database"),
    "0x0047bff0": ("bay state +0x27c", "close animation token", "model animation database"),
    "0x0047c040": ("function table 0x005e2bf0 slot 50", "open, shoot, and close tokens", "older broad CUnitAI label"),
    "0x0050ee10": ("primary vtable slot 1", "0x005e2bd0", "RET 0x4"),
    "0x0050f130": ("this+0x26c", "this+0x25c", "CUnit__dtor_base"),
    "0x004964d0": ("RET 0x4", "owner_aircraft", "vtable 0x005dc330"),
    "0x00496500": ("RET 0x4", "delete-flags", "OID__FreeObject"),
    "0x00496520": ("vtable 0x005dc330", "+0x08", "base motion-controller destructor"),
    "0x00496540": ("vtable 0x005dc330 slot 4", "turret token at 0x0062dd20", "+0x0c/+0x10"),
    "0x004968a0": ("vtable 0x005dc330 slot 8", "+0xe0/+0xe4/+0x284", "this+0x0c/+0x10"),
}

DOC_TOKENS = (
    "Wave1002",
    "ground-attack-aircraft-review-wave1002",
    "0x0047bbf0 CGroundAttackAircraft__Init",
    "0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState",
    "0x004964d0 CMCGroundAttack__Constructor",
    "0x00496540 CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540",
    "0x004968a0 CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0",
    "472/1408 = 33.52%",
    "629/1478 = 42.56%",
    "359/500 = 71.80%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime ground-attack aircraft behavior proven",
    "runtime ground-attack aircraft ai behavior proven",
    "runtime bay animation behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
)


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
    return token.replace("\\\\", "\\") in text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 16,
        "pre-tags.tsv": 16,
        "pre-xrefs.tsv": 18,
        "pre-instructions.tsv": 691,
        "pre-decompile/index.tsv": 16,
        "pre-vtable-slots.tsv": 512,
        "pre-vtable-types.tsv": 4,
        "pre-pointer-table-005e2bf0.tsv": 80,
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
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"comment token missing {address}: {token}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            for tag in ("static-reaudit", "retail-binary-evidence", "comment-hardened"):
                require(tag in actual_tags, f"missing tag {address}: {tag}", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    expected_xrefs = (
        ("0x0047bab0", "0x0047bc92", "UNCONDITIONAL_CALL"),
        ("0x0047bbf0", "0x005e2bf0", "DATA"),
        ("0x0047bd70", "0x005dbd50", "DATA"),
        ("0x0047bd90", "0x0047bd73", "UNCONDITIONAL_CALL"),
        ("0x0047be30", "0x005dbd24", "DATA"),
        ("0x0047be50", "0x0047be33", "UNCONDITIONAL_CALL"),
        ("0x0047bfa0", "0x0047b6c0", "UNCONDITIONAL_CALL"),
        ("0x0047bfa0", "0x0047ba17", "UNCONDITIONAL_CALL"),
        ("0x0047bff0", "0x0047b8e7", "UNCONDITIONAL_CALL"),
        ("0x0047bff0", "0x0047baee", "UNCONDITIONAL_CALL"),
        ("0x0047c040", "0x005e2cb8", "DATA"),
        ("0x0050ee10", "0x005e2bd0", "DATA"),
        ("0x0050f130", "0x0050ee13", "UNCONDITIONAL_CALL"),
        ("0x004964d0", "0x0047bc41", "UNCONDITIONAL_CALL"),
        ("0x00496500", "0x005dc334", "DATA"),
        ("0x00496520", "0x00496503", "UNCONDITIONAL_CALL"),
        ("0x00496540", "0x005dc340", "DATA"),
        ("0x004968a0", "0x005dc350", "DATA"),
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

    vtable_types = read_tsv(BASE / "pre-vtable-types.tsv")
    for vtable, demangled in (
        ("0x005dbd4c", "CGroundAttackAI"),
        ("0x005dbd20", "CGroundAttackGuide"),
        ("0x005dc330", "CMCGroundAttack"),
        ("0x005e2bcc", "CGroundAttackAircraft"),
    ):
        require(
            any(normalize_address(row.get("vtable", "")) == vtable and row.get("demangled_type_name") == demangled for row in vtable_types),
            f"missing vtable type {vtable} -> {demangled}",
            failures,
        )

    vtable_slots = read_tsv(BASE / "pre-vtable-slots.tsv")
    for vtable, slot, slot_addr, pointer, name in (
        ("0x005dbd4c", "1", "0x005dbd50", "0x0047bd70", "CGroundAttackAI__ScalarDeletingDestructor"),
        ("0x005dbd20", "1", "0x005dbd24", "0x0047be30", "CGroundAttackGuide__ScalarDeletingDestructor"),
        ("0x005dc330", "1", "0x005dc334", "0x00496500", "CMCGroundAttack__ScalarDeletingDestructor"),
        ("0x005dc330", "4", "0x005dc340", "0x00496540", "CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540"),
        ("0x005dc330", "8", "0x005dc350", "0x004968a0", "CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0"),
        ("0x005e2bcc", "1", "0x005e2bd0", "0x0050ee10", "CGroundAttackAircraft__scalar_deleting_dtor"),
        ("0x005e2bcc", "2", "0x005e2bd4", "0x00402d30", "CAirUnit__dtor_base"),
    ):
        require(
            any(
                normalize_address(row.get("vtable", "")) == vtable
                and row.get("slot_index") == slot
                and normalize_address(row.get("slot_addr", "")) == slot_addr
                and normalize_address(row.get("pointer_addr", "")) == pointer
                and row.get("function_name") == name
                and row.get("status") == "OK"
                for row in vtable_slots
            ),
            f"missing vtable slot {vtable} {slot} -> {name}",
            failures,
        )

    pointer_table = read_tsv(BASE / "pre-pointer-table-005e2bf0.tsv")
    for slot, pointer, name in (
        ("0", "0x0047bbf0", "CGroundAttackAircraft__Init"),
        ("50", "0x0047c040", "CGroundAttackAircraft__AdvanceCloseShootAnimationState"),
    ):
        require(
            any(
                row.get("slot") == slot
                and normalize_address(row.get("ptr", "")) == pointer
                and row.get("ptr_name") == name
            for row in pointer_table
            ),
            f"missing pointer-table slot {slot} -> {name}",
            failures,
        )


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "pre-metadata.log": ("targets=16 found=16 missing=0", "REPORT: Save succeeded"),
        "pre-tags.log": ("ExportFunctionTagsByAddress complete: rows=16 missing=0", "REPORT: Save succeeded"),
        "pre-xrefs.log": ("Wrote 18 rows", "REPORT: Save succeeded"),
        "pre-instructions.log": ("Wrote 691 function-body instruction rows", "targets=16 missing=0", "REPORT: Save succeeded"),
        "pre-decompile.log": ("targets=16 dumped=16 missing=0 failed=0", "REPORT: Save succeeded"),
        "pre-vtable-slots.log": ("ExportVtableSlots complete: targets=4 rows=512", "REPORT: Save succeeded"),
        "pre-vtable-types.log": ("ResolveVtableTypeNames complete: rows=4", "REPORT: Save succeeded"),
        "pre-pointer-table-005e2bf0.log": ("DumpPointerTable complete: rows=80", "REPORT: Save succeeded"),
    }
    for relative, tokens in expected_log_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
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
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        GROUND_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-ground-attack-aircraft-review-wave1002")
        == r"py -3 tools\ghidra_ground_attack_aircraft_review_wave1002_probe.py --check",
        "missing Wave1002 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1002-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1002 --check",
        "missing Wave1002 recheck package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param mismatch", failures)

    recheck_text = read_text(RECHECK_TOOL)
    require('glob("Apply*Wave*.java")' in recheck_text, "Wave900+ recheck does not scan Wave1000+ apply scripts", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1002 GroundAttackAircraft review" for row in ledger_rows), "missing Wave1002 ledger row", failures)
    require(any(row.get("task") == "Wave1002 GroundAttackAircraft review" and row.get("attempt_id") == 20584 for row in attempts), "missing Wave1002 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1002 GroundAttackAircraft review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1002 GroundAttackAircraft review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
