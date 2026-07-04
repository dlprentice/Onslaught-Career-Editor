#!/usr/bin/env python3
"""Validate Wave989 CarverGuide lifecycle read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave989-carver-guide-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_carver_guide_lifecycle_review_wave989_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CARVER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carver.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-034107_post_wave989_carver_guide_lifecycle_review_verified"

TARGETS = {
    "0x00422440": ("CCarver__Init", "void __thiscall CCarver__Init(void * this, void * init)"),
    "0x00422f90": ("CCarverGuide__ctor", "void * __thiscall CCarverGuide__ctor(void * this, void * guideTarget)"),
    "0x00422fb0": ("CCarverGuide__scalar_deleting_dtor", "void * __thiscall CCarverGuide__scalar_deleting_dtor(void * this, byte flags)"),
    "0x00422fd0": ("CCarverGuide__dtor_base", "void __fastcall CCarverGuide__dtor_base(void * this)"),
    "0x00423490": ("CCarverGuide__HandleEvent", "void __thiscall CCarverGuide__HandleEvent(void * this, void * event)"),
    "0x00423510": ("CCarverGuide__AcquireNearestTargetReader", "void __fastcall CCarverGuide__AcquireNearestTargetReader(void * this)"),
    "0x004bac40": ("CMonitor__Shutdown", "void __fastcall CMonitor__Shutdown(void * this)"),
}

PRIMARY = {
    "0x00422f90",
    "0x00422fb0",
    "0x00422fd0",
    "0x00423490",
    "0x00423510",
}

DOC_TOKENS = (
    "Wave989",
    "carver-guide-lifecycle-review-wave989",
    "0x00422f90 CCarverGuide__ctor",
    "0x00422fb0 CCarverGuide__scalar_deleting_dtor",
    "0x00422fd0 CCarverGuide__dtor_base",
    "0x00423490 CCarverGuide__HandleEvent",
    "0x00423510 CCarverGuide__AcquireNearestTargetReader",
    "438/1408 = 31.11%",
    "509/1478 = 34.44%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime carverguide behavior proven",
    "exact carverguide layout proven",
    "source identity proven",
    "rebuild parity proven",
)

EXPECTED_LOG_TOKENS = {
    "metadata.log": ("targets=7 found=7 missing=0", "REPORT: Save succeeded"),
    "tags.log": ("ExportFunctionTagsByAddress complete: rows=7 missing=0", "REPORT: Save succeeded"),
    "xrefs.log": ("Wrote 121 rows", "REPORT: Save succeeded"),
    "instructions.log": ("targets=7 missing=0", "REPORT: Save succeeded"),
    "decompile.log": ("targets=7 dumped=7 missing=0 failed=0", "REPORT: Save succeeded"),
    "vtable-slots.log": ("ExportVtableSlots complete: targets=2 rows=256", "REPORT: Save succeeded"),
    "vtable-types.log": ("ResolveVtableTypeNames complete: rows=2", "REPORT: Save succeeded"),
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


def contains_path_token(text: str, token: str) -> bool:
    return (
        token in text
        or token.replace("\\", "\\\\") in text
        or token.replace("\\", "\\\\\\\\") in text
    )


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 7,
        "tags.tsv": 7,
        "xrefs.tsv": 121,
        "instructions.tsv": 238,
        "decompile/index.tsv": 7,
        "vtable-slots.tsv": 256,
        "vtable-types.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    decompile_index = read_tsv(BASE / "decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("comment", "").strip() != "", f"metadata comment missing {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)

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
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
            if address in {"0x00422fb0", "0x00422fd0"}:
                require("constructor" not in actual_tags, f"stale constructor tag present at {address}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    expected_xrefs = (
        ("0x00422f90", "0x0042249f", "UNCONDITIONAL_CALL"),
        ("0x00422fb0", "0x005d9480", "DATA"),
        ("0x00422fd0", "0x00422fb3", "UNCONDITIONAL_CALL"),
        ("0x00423490", "0x005d947c", "DATA"),
        ("0x00423510", "0x004234ad", "UNCONDITIONAL_CALL"),
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

    vtable_types = read_tsv(BASE / "vtable-types.tsv")
    guide_row = row_by_address(vtable_types, "0x005d947c", field="vtable")
    require(guide_row is not None, "missing CCarverGuide vtable type row", failures)
    if guide_row:
        require(guide_row.get("demangled_type_name") == "CCarverGuide", "CCarverGuide vtable type mismatch", failures)

    vtable_slots = read_tsv(BASE / "vtable-slots.tsv")
    expected_slots = (
        ("0x005d947c", "0", "CCarverGuide__HandleEvent"),
        ("0x005d947c", "1", "CCarverGuide__scalar_deleting_dtor"),
        ("0x005e0d90", "8", "CCarver__Init"),
    )
    for vtable, slot, name in expected_slots:
        require(
            any(
                normalize_address(row.get("vtable", "")) == vtable
                and row.get("slot_index") == slot
                and row.get("function_name") == name
                for row in vtable_slots
            ),
            f"missing vtable slot {vtable}[{slot}] -> {name}",
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
    require(backup.get("totalBytes") == 173837191 or backup.get("totalBytes") == 173837191.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = (
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        CARVER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_path_token(text, token), f"missing doc token {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIMS:
            require(token not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-carver-guide-lifecycle-review-wave989")
        == r"py -3 tools\ghidra_carver_guide_lifecycle_review_wave989_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_exports(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave989 CarverGuide lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave989 CarverGuide lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
