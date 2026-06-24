#!/usr/bin/env python3
"""Validate Wave1045 frontend vtable boundary recovery artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1045-frontend-residual-helper-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_vtable_boundary_wave1045_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1045_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GOODIES_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPGoodies.cpp" / "_index.md"
WINGMEN_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPWingmen.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-112809_post_wave1045_frontend_vtable_boundary_verified"

TARGETS = {
    "0x0045c7a0": ("CFEPGoodies__Init", "int __fastcall CFEPGoodies__Init(void * this)", "0x005db998"),
    "0x0045c9e0": ("CFEPGoodies__Shutdown", "void __fastcall CFEPGoodies__Shutdown(void * this)", "0x005db99c"),
    "0x0045e0d0": (
        "CFEPGoodies__Render",
        "void __thiscall CFEPGoodies__Render(void * this, float transition, int dest)",
        "0x005db9ac",
    ),
    "0x0045ffa0": (
        "CFEPGoodies__TransitionNotification",
        "void __thiscall CFEPGoodies__TransitionNotification(void * this, int from_page)",
        "0x005db9b0",
    ),
    "0x005216c0": ("CFEPWingmen__Init", "int __fastcall CFEPWingmen__Init(void * this)", "0x005dba10"),
    "0x00521d20": (
        "CFEPWingmen__ButtonPressed",
        "void __thiscall CFEPWingmen__ButtonPressed(void * this, int button, float val)",
        "0x005dba1c",
    ),
    "0x00522160": (
        "CFEPWingmen__RenderPreCommon",
        "void __stdcall CFEPWingmen__RenderPreCommon(float transition, int dest)",
        "0x005dba20",
    ),
    "0x00522190": (
        "CFEPWingmen__Render",
        "void __thiscall CFEPWingmen__Render(void * this, float transition, int dest)",
        "0x005dba24",
    ),
}

COMMENT_TOKENS = {
    "0x0045c7a0": ("Wave1045", "0x005db998 slot 0", "0x00679870"),
    "0x0045c9e0": ("Wave1045", "0x005db998 slot 1", "CFEPGoodies__FreeUpGoodyResources"),
    "0x0045e0d0": ("Wave1045", "0x005db998 slot 5", "0x0045ff36", "Render(float transition"),
    "0x0045ffa0": ("Wave1045", "0x005db998 slot 6", "PLATFORM__GetSysTimeFloat"),
    "0x005216c0": ("Wave1045", "0x005dba10 slot 0", "FEPWingmen.cpp source is absent"),
    "0x00521d20": ("Wave1045", "0x005dba10 slot 3", "DAT_008a956c"),
    "0x00522160": ("Wave1045", "0x005dba10 slot 4", "RET 0x8"),
    "0x00522190": ("Wave1045", "0x005dba10 slot 5", "0x005230ac", "CFEPWingmen__FindCurrentLevelRecord"),
}

DECOMPILE_TOKENS = {
    "0x0045c7a0": ("PLATFORM__GetSysTimeFloat", "0x13c", "0x1a0"),
    "0x0045c9e0": ("CFEPGoodies__FreeUpGoodyResources(this)",),
    "0x0045e0d0": ("CFrontEnd__RenderOverlayEffects", "CDXSurf__RenderSurface", "PLATFORM__GetSysTimeFloat"),
    "0x0045ffa0": ("PLATFORM__GetSysTimeFloat", "0x00679870", "0x1a0"),
    "0x005216c0": ("CDXMemoryManager__Alloc", "CFEPMultiplayerStart__LoadPreviewMeshFromConfig", "0x14"),
    "0x00521d20": ("CFEPWingmen__FindCurrentLevelRecord", "DAT_008a956c", "CFrontEnd__SetPage"),
    "0x00522160": ("CFrontEnd__RenderPreCommonFade",),
    "0x00522190": ("CFrontEnd__RenderOverlayEffects", "CFEPWingmen__FindCurrentLevelRecord", "CDXSurf__RenderSurface"),
}

COMMON_TAGS = {
    "static-reaudit",
    "frontend-vtable-boundary-wave1045",
    "wave1045-readback-verified",
    "function-boundary-recovered",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "frontend",
    "vtable-slot",
}

DOC_TOKENS = (
    "Wave1045",
    "frontend-vtable-boundary-wave1045",
    "0x0045c7a0 CFEPGoodies__Init",
    "0x0045c9e0 CFEPGoodies__Shutdown",
    "0x0045e0d0 CFEPGoodies__Render",
    "0x0045ffa0 CFEPGoodies__TransitionNotification",
    "0x005216c0 CFEPWingmen__Init",
    "0x00521d20 CFEPWingmen__ButtonPressed",
    "0x00522160 CFEPWingmen__RenderPreCommon",
    "0x00522190 CFEPWingmen__Render",
    "0x005db998",
    "0x005dba10",
    "735/1408 = 52.20%",
    "985/1501 = 65.62%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "function-boundary recovery",
)

OVERCLAIMS = (
    "runtime goodies wall behavior proven",
    "runtime wingmen menu behavior proven",
    "runtime visual behavior proven",
    "exact source-body identity proven",
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


def read_json(path: Path):
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
        "pre-candidate-boundary-metadata.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 3540,
        "post-decompile/index.tsv": 8,
        "post-vtable-slots.tsv": 135,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-candidate-boundary-metadata.tsv")
    require(all(row.get("status") == "MISSING" for row in pre), "pre metadata should show missing boundaries", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, (name, signature, xref_from) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row at {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing common tags at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
        text = read_text(BASE / "post-decompile" / f"{address[2:]}_{name}.c")
        for token in DECOMPILE_TOKENS[address]:
            require(token in text, f"missing decompile token at {address}: {token}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref at {address}", failures)
        if xref is not None:
            require(normalize_address(xref.get("from_addr", "")) == xref_from, f"xref source mismatch at {address}", failures)
            require(xref.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)

    slots = read_tsv(BASE / "post-vtable-slots.tsv")
    by_vtable_pointer = {(normalize_address(row["vtable"]), normalize_address(row["pointer_addr"])): row for row in slots}
    for address, (name, _signature, _xref_from) in TARGETS.items():
        vtable = "0x005db998" if "Goodies" in name else "0x005dba10"
        row = by_vtable_pointer.get((vtable, address))
        require(row is not None, f"missing vtable slot for {address}", failures)
        if row is not None:
            require(row.get("function_name") == name, f"vtable function mismatch at {address}", failures)
            require(row.get("status") == "OK", f"vtable status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-candidate-boundary-metadata.log": "targets=8 found=0 missing=8",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "FAIL: 0x0045e0d0 CFEPGoodies__Render IllegalStateException: createFunction returned null at 0x0045e0d0 (disassemble=true)",
        "apply-recovery-dry.log": "SUMMARY: updated=0 skipped=7 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-recovery.log": "SUMMARY: updated=1 skipped=7 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 3540 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=15 rows=135",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("LockException" not in text, f"LockException in {relative}", failures)
        if relative not in {"pre-candidate-boundary-metadata.log", "apply.log"}:
            for bad in ("MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
                require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    apply_text = read_text(BASE / "apply.log")
    require("SUMMARY: updated=7 skipped=0 created=7" in apply_text and "bad=1" in apply_text, "apply partial-failure summary not preserved", failures)
    require("REPORT: Save succeeded" in apply_text, "apply partial run did not save", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6246, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined signature count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174590855 or backup.get("totalBytes") == 174590855.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        GOODIES_DOC: (
            "Wave1045",
            "frontend-vtable-boundary-wave1045",
            "0x0045c7a0 CFEPGoodies__Init",
            "0x0045c9e0 CFEPGoodies__Shutdown",
            "0x0045e0d0 CFEPGoodies__Render",
            "0x0045ffa0 CFEPGoodies__TransitionNotification",
            "0x005db998",
            "985/1501 = 65.62%",
            BACKUP_PATH,
        ),
        WINGMEN_DOC: (
            "Wave1045",
            "frontend-vtable-boundary-wave1045",
            "0x005216c0 CFEPWingmen__Init",
            "0x00521d20 CFEPWingmen__ButtonPressed",
            "0x00522160 CFEPWingmen__RenderPreCommon",
            "0x00522190 CFEPWingmen__Render",
            "0x005dba10",
            "FEPWingmen.cpp source is absent",
            "985/1501 = 65.62%",
            BACKUP_PATH,
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-frontend-vtable-boundary-wave1045")
        == r"py -3 tools\ghidra_frontend_vtable_boundary_wave1045_probe.py --check",
        "missing Wave1045 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1045-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1045 --check",
        "missing Wave1045 aggregate recheck package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1045 frontend vtable boundary recovery" for row in ledger_rows), "missing Wave1045 ledger row", failures)
    require(
        any(row.get("task") == "Wave1045 frontend vtable boundary recovery" for row in attempt_rows),
        "missing Wave1045 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1045 frontend vtable boundary recovery probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1045 frontend vtable boundary recovery probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
