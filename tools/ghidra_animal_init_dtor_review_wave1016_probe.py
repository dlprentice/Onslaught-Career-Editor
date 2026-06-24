#!/usr/bin/env python3
"""Validate Wave1016 CAnimal init/destructor read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1016-animal-init-dtor-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_animal_init_dtor_review_wave1016_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1016_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
ANIMAL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Animal.cpp" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified"

TARGETS = {
    "0x00403d30": ("CAnimal__Init", "void __thiscall CAnimal__Init(void * this, void * init)"),
    "0x00404010": ("CAnimal__dtor_base", "void __fastcall CAnimal__dtor_base(void * this)"),
    "0x004041f0": ("CAnimal__scalar_deleting_dtor", "void * __thiscall CAnimal__scalar_deleting_dtor(void * this, byte flags)"),
}

CONTEXT_TARGETS = {
    "0x004f33e0": "CThing__ctor_base",
    "0x004f34a0": "CThing__Init",
    "0x004f3600": "CThing__Shutdown",
    "0x004f3640": "CThing__dtor_base",
    "0x004f3f00": "CComplexThing__dtor_base",
    "0x004f3fd0": "CComplexThing__Init",
    "0x004f41b0": "CComplexThing__Shutdown",
    "0x0044c140": "CAnimal__HandleEvent3000Dispatch",
    "0x00403f40": "CResourceDescriptor__ctor",
    "0x00403f80": "CResourceDescriptor__dtor",
    "0x00403ff0": "CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk",
    "0x004011e0": "CActor__Init",
    "0x004013d0": "CActor__dtor_base",
    "0x0044b370": "CEventManager__AddEvent_AtTime",
    "0x00516580": "PCRTID__CreateObject",
    "0x0042b840": "CConsole__AddString",
    "0x004040f0": "CAnimal__GetClassNameString",
    "0x00404100": "CAnimal__GetTypeId1D",
    "0x00404110": "CAnimal__SetThingTypeMask80000001",
    "0x00404120": "CAnimal__CopyVector7CToOut",
    "0x00404150": "CAnimal__SetVector7CFromInput",
    "0x00404170": "CAnimal__AddVectorTo7C",
    "0x004041a0": "CAnimal__CopyVector8CToOut",
    "0x004041d0": "CAnimal__CopyMatrix9CToOut",
    "0x004045d0": "CAnimal__RenderViaCThingRender",
}

EXPECTED_STRINGS = {
    "string-00622d48.tsv": "bird.msh",
    "string-00622d1c.tsv": r"Warning! Unknown animal type %d generated!\x0a",
    "string-00622d70.tsv": "CAnimal",
}

VTABLE_SLOTS = {
    "1": "CAnimal__scalar_deleting_dtor",
    "7": "CAnimal__GetClassNameString",
    "8": "CAnimal__GetTypeId1D",
    "9": "CAnimal__Init",
    "27": "CAnimal__CopyVector7CToOut",
    "30": "CAnimal__CopyVector8CToOut",
    "31": "CAnimal__CopyMatrix9CToOut",
    "36": "CAnimal__RenderViaCThingRender",
    "38": "CAnimal__SetThingTypeMask80000001",
    "67": "CAnimal__SetVector7CFromInput",
    "68": "CAnimal__AddVectorTo7C",
}

DOC_TOKENS = (
    "Wave1016",
    "animal-init-dtor-review-wave1016",
    "0x00403d30 CAnimal__Init",
    "0x00404010 CAnimal__dtor_base",
    "0x004041f0 CAnimal__scalar_deleting_dtor",
    "0x005d8698",
    "0x00622d48 bird.msh",
    "0x00622d1c Warning! Unknown animal type",
    "0x00622d70 CAnimal",
    "513/1408 = 36.43%",
    "739/1493 = 49.50%",
    "439/500 = 87.80%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime animal behavior proven",
    "runtime event scheduling proven",
    "exact source virtual names proven",
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
    if value in {"", "<none>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 3,
        "tags.tsv": 3,
        "xrefs.tsv": 3,
        "instructions.tsv": 195,
        "decompile/index.tsv": 3,
        "context-metadata.tsv": 32,
        "context-xrefs.tsv": 637,
        "context-instructions.tsv": 1292,
        "context-decompile/index.tsv": 32,
        "vtable-005d8698.tsv": 69,
        "data-xrefs.tsv": 14,
        "scalar-references.tsv": 3,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")
    comment_tokens = {
        "0x00403d30": ("CAnimal init correction", "bird_msh", "CComplexThing__Init", "event 3000"),
        "0x00404010": ("CAnimal destructor-base correction", "0x005d8698", "DAT_00660130", "CComplexThing__dtor_base"),
        "0x004041f0": ("CAnimal scalar-deleting destructor", "CAnimal__dtor_base", "flags&1", "optionally frees this"),
    }
    for address, (name, signature) in TARGETS.items():
        key = normalize_address(address)
        row = metadata.get(key)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in comment_tokens[address]:
                require(token in comment, f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(key)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
            require("CAtmospheric__Destructor" not in tag_row.get("tags", ""), f"stale destructor tag {address}", failures)

        dec = decompile.get(key)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    context = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(normalize_address(address))
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    for target, source, function in (
        ("0x00403d30", "0x005d86bc", "<no_function>"),
        ("0x00404010", "0x004041f0", "CAnimal__scalar_deleting_dtor"),
        ("0x004041f0", "0x005d869c", "<no_function>"),
    ):
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_function_addr", "") if function != "<no_function>" else row.get("from_addr", "")) == source
                and row.get("from_function") == function
                for row in xrefs
            ),
            f"missing xref {source} -> {target}",
            failures,
        )

    vtable = read_tsv(BASE / "vtable-005d8698.tsv")
    by_slot = {row.get("slot_index", ""): row for row in vtable}
    for slot, name in VTABLE_SLOTS.items():
        row = by_slot.get(slot)
        require(row is not None, f"missing vtable slot {slot}", failures)
        if row:
            require(row.get("vtable") == "005d8698", f"vtable address mismatch slot {slot}", failures)
            require(row.get("function_name") == name, f"vtable slot {slot} name mismatch: {row.get('function_name')}", failures)
            require(row.get("status") == "OK", f"vtable slot {slot} status mismatch", failures)

    data_xrefs = read_tsv(BASE / "data-xrefs.tsv")
    data_expectations = (
        ("0x00622d48", "CAnimal__Init", "READ"),
        ("0x00622d1c", "CAnimal__Init", "DATA"),
        ("0x00622d70", "CAnimal__GetClassNameString", "DATA"),
        ("0x00660130", "CAnimal__Init", "WRITE"),
        ("0x00660134", "CAnimal__dtor_base", "READ_WRITE"),
    )
    for target, function, ref_type in data_expectations:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and row.get("from_function") == function
                and row.get("ref_type") == ref_type
                for row in data_xrefs
            ),
            f"missing data xref {target} {function} {ref_type}",
            failures,
        )

    scalar_rows = read_tsv(BASE / "scalar-references.tsv")
    for value, function in (("0x622d48", "CAnimal__Init"), ("0x622d1c", "CAnimal__Init"), ("0x622d70", "CAnimal__GetClassNameString")):
        require(any(row.get("value_hex") == value and row.get("function") == function for row in scalar_rows), f"missing scalar {value}", failures)

    for relative, expected in EXPECTED_STRINGS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=3 found=3 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "xrefs.log": "Wrote 3 rows",
        "instructions.log": "Wrote 195 function-body instruction rows",
        "decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "context-metadata.log": "targets=32 found=32 missing=0",
        "context-xrefs.log": "Wrote 637 rows",
        "context-instructions.log": "Wrote 1292 function-body instruction rows",
        "context-decompile.log": "targets=32 dumped=32 missing=0 failed=0",
        "vtable-005d8698.log": "ExportVtableSlots complete: targets=1 rows=69",
        "data-xrefs.log": "Wrote 14 rows",
        "scalar-references.log": "Wrote 3 scalar rows",
        "string-00622d48.log": "text=bird.msh",
        "string-00622d1c.log": "Warning! Unknown animal type",
        "string-00622d70.log": "text=CAnimal",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        ANIMAL_DOC,
        THING_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIMS:
            require(token not in lower, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-animal-init-dtor-review-wave1016")
        == r"py -3 tools\ghidra_animal_init_dtor_review_wave1016_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1016-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1016 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1016 animal init dtor review" for row in ledger_rows), "missing Wave1016 ledger row", failures)
    require(any(row.get("task") == "Wave1016 animal init dtor review" and row.get("attempt_id") == 20598 for row in attempts), "missing Wave1016 attempt row", failures)


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
        print("Wave1016 animal init/dtor review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1016 animal init/dtor review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
