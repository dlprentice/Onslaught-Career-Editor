#!/usr/bin/env python3
"""Validate Wave1112 CAnimal current-risk supersession evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
WAVE1108_DIR = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank"
FOCUSED_TSV = WAVE1108_DIR / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
WAVE1016_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1016-animal-init-dtor-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1112-animal-wave1016-current-risk-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1112-animal-wave1016-current-risk-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1112_animal_wave1016_current_risk_supersession_2026-06-04.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
ANIMAL_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Animal.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE1016_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified"
LATEST_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

TARGETS = {
    "0x00403d30": {
        "name": "CAnimal__Init",
        "signature": "void __thiscall CAnimal__Init(void * this, void * init)",
        "score": "27",
        "signals": ("stale_or_corrected", "provisional_or_candidate", "exact_layout_deferred", "source_identity_deferred"),
        "comment_tokens": ("CAnimal init correction", "bird_msh", "CComplexThing__Init", "event 3000"),
    },
    "0x00404010": {
        "name": "CAnimal__dtor_base",
        "signature": "void __fastcall CAnimal__dtor_base(void * this)",
        "score": "23",
        "signals": ("stale_or_corrected", "provisional_or_candidate", "exact_layout_deferred", "runtime_or_rebuild_deferred"),
        "comment_tokens": ("CAnimal destructor-base correction", "0x005d8698", "DAT_00660130", "CComplexThing__dtor_base"),
    },
    "0x004041f0": {
        "name": "CAnimal__scalar_deleting_dtor",
        "signature": "void * __thiscall CAnimal__scalar_deleting_dtor(void * this, byte flags)",
        "score": "15",
        "signals": ("stale_or_corrected", "provisional_or_candidate"),
        "comment_tokens": ("CAnimal scalar-deleting destructor", "CAnimal__dtor_base", "flags&1", "optionally frees this"),
    },
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
    "Wave1112",
    "wave1112-animal-wave1016-current-risk-supersession",
    "28/1179 = 2.37%",
    "3 rows",
    "current focused candidates: 1179",
    "Wave1016",
    "animal-init-dtor-review-wave1016",
    "0x00403d30 CAnimal__Init",
    "0x00404010 CAnimal__dtor_base",
    "0x004041f0 CAnimal__scalar_deleting_dtor",
    "0x005d8698",
    "0x00622d48 bird.msh",
    "0x00622d1c Warning! Unknown animal type",
    "0x00622d70 CAnimal",
    WAVE1016_BACKUP,
    LATEST_BACKUP,
    "no new Ghidra export",
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime animal behavior proven",
    "runtime event scheduling proven",
    "exact source virtual names proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
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


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value in {"", "<none>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def check_wave1108_membership(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    focused = row_map(FOCUSED_TSV)
    require(len(focused) == 1179, "Wave1108 focused row count mismatch", failures)
    for address, expected in TARGETS.items():
        row = focused.get(address)
        require(row is not None, f"Wave1108 focused row missing: {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"Wave1108 name mismatch: {address}", failures)
        require(row.get("score") == expected["score"], f"Wave1108 score mismatch: {address}", failures)
        for signal in expected["signals"]:
            require(signal in row.get("signals", ""), f"Wave1108 missing signal {address}: {signal}", failures)


def check_current_queue(failures: list[str]) -> None:
    queue = row_map(QUEUE_TSV)
    for address, expected in TARGETS.items():
        row = queue.get(address)
        require(row is not None, f"current queue row missing: {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"current queue name mismatch: {address}", failures)
        require(row.get("signature") == expected["signature"], f"current queue signature mismatch: {address}", failures)
        require(row.get("status") == "OK", f"current queue status mismatch: {address}", failures)
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            require(token in comment, f"current queue missing comment token {address}: {token}", failures)


def check_wave1016_artifacts(failures: list[str]) -> None:
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
        actual = len(read_tsv(WAVE1016_BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = row_map(WAVE1016_BASE / "metadata.tsv")
    tags = row_map(WAVE1016_BASE / "tags.tsv")
    decompile = row_map(WAVE1016_BASE / "decompile" / "index.tsv")
    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"Wave1016 metadata missing: {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"Wave1016 metadata name mismatch: {address}", failures)
            require(row.get("signature") == expected["signature"], f"Wave1016 metadata signature mismatch: {address}", failures)
            require(row.get("status") == "OK", f"Wave1016 metadata status mismatch: {address}", failures)
            for token in expected["comment_tokens"]:
                require(token in row.get("comment", ""), f"Wave1016 metadata missing token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"Wave1016 tags missing: {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"Wave1016 tag status mismatch: {address}", failures)
            require("CAtmospheric__Destructor" not in tag_row.get("tags", ""), f"stale destructor tag: {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"Wave1016 decompile missing: {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"Wave1016 decompile signature mismatch: {address}", failures)
            require(dec.get("status") == "OK", f"Wave1016 decompile status mismatch: {address}", failures)

    xrefs = read_tsv(WAVE1016_BASE / "xrefs.tsv")
    xref_expectations = (
        ("0x00403d30", "0x005d86bc", "<no_function>", "DATA"),
        ("0x00404010", "0x004041f3", "CAnimal__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("0x004041f0", "0x005d869c", "<no_function>", "DATA"),
    )
    for target, from_addr, from_function, ref_type in xref_expectations:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == from_addr
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing Wave1016 xref {from_addr} -> {target}",
            failures,
        )

    vtable = {row.get("slot_index", ""): row for row in read_tsv(WAVE1016_BASE / "vtable-005d8698.tsv")}
    for slot, name in VTABLE_SLOTS.items():
        row = vtable.get(slot)
        require(row is not None, f"missing Wave1016 vtable slot {slot}", failures)
        if row is not None:
            require(row.get("vtable") == "005d8698", f"Wave1016 vtable mismatch slot {slot}", failures)
            require(row.get("function_name") == name, f"Wave1016 vtable name mismatch slot {slot}: {row.get('function_name')}", failures)
            require(row.get("status") == "OK", f"Wave1016 vtable status mismatch slot {slot}", failures)

    data_xrefs = read_tsv(WAVE1016_BASE / "data-xrefs.tsv")
    for target, function, ref_type in (
        ("0x00622d48", "CAnimal__Init", "READ"),
        ("0x00622d1c", "CAnimal__Init", "DATA"),
        ("0x00622d70", "CAnimal__GetClassNameString", "DATA"),
        ("0x00660130", "CAnimal__Init", "WRITE"),
        ("0x00660134", "CAnimal__dtor_base", "READ_WRITE"),
    ):
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and row.get("from_function") == function
                and row.get("ref_type") == ref_type
                for row in data_xrefs
            ),
            f"missing Wave1016 data xref {target} {function} {ref_type}",
            failures,
        )

    scalar_rows = read_tsv(WAVE1016_BASE / "scalar-references.tsv")
    for value, function in (("0x622d48", "CAnimal__Init"), ("0x622d1c", "CAnimal__Init"), ("0x622d70", "CAnimal__GetClassNameString")):
        require(any(row.get("value_hex") == value and row.get("function") == function for row in scalar_rows), f"missing Wave1016 scalar {value}", failures)

    for relative, expected in EXPECTED_STRINGS.items():
        rows = read_tsv(WAVE1016_BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    decompile_text = read_text(WAVE1016_BASE / "decompile" / "00403d30_CAnimal__Init.c")
    for token in ("CResourceDescriptor__ctor", "s_bird_msh_00622d48", "PCRTID__CreateObject", "CComplexThing__Init", "CEventManager__AddEvent_AtTime"):
        require(token in decompile_text, f"CAnimal__Init decompile missing token: {token}", failures)

    logs = {
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
    }
    for relative, token in logs.items():
        text = read_text(WAVE1016_BASE / relative)
        require(token in text, f"Wave1016 log missing token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"Wave1016 log failure token in {relative}: {bad}", failures)

    backup = read_json(WAVE1016_BASE / "backup-summary.json")
    require(backup.get("backupPath") == WAVE1016_BACKUP, "Wave1016 backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "Wave1016 backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173968263, "Wave1016 backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "Wave1016 backup diff mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "Wave1016 backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "wave1112 note": read_text(NOTE),
        "wave1112 readiness": read_text(READINESS),
        "mapped systems": read_text(MAPPED_SYSTEMS),
        "campaign": read_text(CAMPAIGN),
        "binary index": read_text(BINARY_INDEX),
        "RE index": read_text(RE_INDEX),
        "progress": read_text(PROGRESS),
        "Animal index": read_text(ANIMAL_INDEX),
        "developer state": read_text(DEVELOPER_STATE),
        "documentation state": read_text(DOCUMENTATION_STATE),
        "re state": read_text(RE_STATE),
    }
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {name}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1112 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "static progress mirror mismatch", failures)
    current = read_json(PROGRESS).get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 28, "progress focusedReviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "2.37%", "progress focusedReviewedPercent mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1112-animal-wave1016-current-risk-supersession")
        == r"py -3 tools\wave1112_animal_wave1016_current_risk_supersession.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_membership(failures)
    check_current_queue(failures)
    check_wave1016_artifacts(failures)
    check_docs(failures)

    if failures:
        print("Wave1112 CAnimal current-risk supersession probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1112 CAnimal current-risk supersession probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
