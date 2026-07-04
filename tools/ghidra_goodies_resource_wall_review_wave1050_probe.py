#!/usr/bin/env python3
"""Validate Wave1050 Goodies resource-wall review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1050-goodies-resource-wall-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_goodies_resource_wall_review_wave1050_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1050_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GOODIES_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPGoodies.cpp" / "_index.md"
GOODIES_PROCESS = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPGoodies.cpp" / "CFEPGoodies__Process.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-143021_post_wave1050_goodies_resource_wall_review_verified"

PRIMARY_SIGNATURES = {
    "0x0045ac30": ("CFEPGoodies__BuildStaticGoodieDataTable", "void CFEPGoodies__BuildStaticGoodieDataTable(void)"),
    "0x0045c770": (
        "CGoodieData__ctor",
        "void __thiscall CGoodieData__ctor(void * this, int method, int method2, int number, int number2, int t1, int t2)",
    ),
    "0x0045c7a0": ("CFEPGoodies__Init", "int __fastcall CFEPGoodies__Init(void * this)"),
    "0x0045c870": ("CFEPGoodies__Deserialise", "void __thiscall CFEPGoodies__Deserialise(void * this, void * chunk_reader)"),
    "0x0045c9e0": ("CFEPGoodies__Shutdown", "void __fastcall CFEPGoodies__Shutdown(void * this)"),
    "0x0045c9f0": ("CFEPGoodies__StartLoadingGoody", "void __fastcall CFEPGoodies__StartLoadingGoody(void * this)"),
    "0x0045cb80": ("get_goodie_number", "int __cdecl get_goodie_number(int x, int y)"),
    "0x0045cc10": ("CFEPGoodies__LoadingGoodyPoll", "void __fastcall CFEPGoodies__LoadingGoodyPoll(void * this)"),
    "0x0045cd10": ("CFEPGoodies__FreeUpGoodyResources", "void __fastcall CFEPGoodies__FreeUpGoodyResources(void * this)"),
    "0x0045cde0": ("CFEPGoodies__ButtonPressed", "void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)"),
    "0x0045d7e0": ("CFEPGoodies__Process", "void __thiscall CFEPGoodies__Process(void * this, int state)"),
    "0x0045e0d0": ("CFEPGoodies__Render", "void __thiscall CFEPGoodies__Render(void * this, float transition, int dest)"),
    "0x0045ffa0": ("CFEPGoodies__TransitionNotification", "void __thiscall CFEPGoodies__TransitionNotification(void * this, int from_page)"),
}

PROCESS_COMMENT_TOKENS = (
    "Wave1050 Goodies resource-wall correction",
    "broader than the older cheat-flag-only comment",
    "g_Cheat_MALLOY",
    "g_Cheat_LATETE",
    "IsCheatActive(0/5)",
    "CFEPGoodies__FreeUpGoodyResources",
    "CFEPGoodies__LoadingGoodyPoll",
    "get_goodie_number",
    "CFMV__PlayFullscreenWithLoadingGate",
    "CFEPCommon video",
)

PROCESS_TAGS = {
    "static-reaudit",
    "goodies-resource-wall-review-wave1050",
    "wave1050-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "frontend-goodies",
    "goodies-process",
    "goodie-resource-wall",
    "goodie-cheat-flags",
    "fmv-goodie-path",
    "source-shape-evidence",
}

VTABLE_SLOTS = {
    "0": "CFEPGoodies__Init",
    "1": "CFEPGoodies__Shutdown",
    "2": "CFEPGoodies__Process",
    "3": "CFEPGoodies__ButtonPressed",
    "4": "CFEPLanguageTest__RenderPreCommon",
    "5": "CFEPGoodies__Render",
    "6": "CFEPGoodies__TransitionNotification",
    "7": "SharedVFunc__NoOpOneArg_004014c0",
    "8": "CFrontEndPage__DeActiveNotification",
}

DOC_TOKENS = (
    "Wave1050",
    "goodies-resource-wall-review-wave1050",
    "0x0045d7e0 CFEPGoodies__Process",
    "IsCheatActive(0/5)",
    "CFEPGoodies__FreeUpGoodyResources",
    "CFEPGoodies__LoadingGoodyPoll",
    "get_goodie_number",
    "CFEPCommon__StopVideo",
    "CFMV__PlayFullscreenWithLoadingGate",
    "CFEPCommon__StartVideo",
    "0x005db998 CFEPGoodies_vtable",
    "744/1408 = 52.84%",
    "1021/1509 = 67.66%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "comment/tag correction",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 132,
        "pre-instructions.tsv": 5274,
        "pre-decompile/index.tsv": 13,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 132,
        "post-instructions.tsv": 5274,
        "post-decompile/index.tsv": 13,
        "context-metadata.tsv": 15,
        "context-tags.tsv": 15,
        "context-xrefs.tsv": 462,
        "context-instructions.tsv": 7241,
        "context-decompile/index.tsv": 15,
        "post-context-metadata.tsv": 15,
        "post-context-tags.tsv": 15,
        "post-context-xrefs.tsv": 462,
        "post-context-instructions.tsv": 7241,
        "post-context-decompile/index.tsv": 15,
        "post-render-context-metadata.tsv": 3,
        "post-render-context-tags.tsv": 3,
        "post-render-context-xrefs.tsv": 17,
        "post-render-context-instructions.tsv": 132,
        "post-render-context-decompile/index.tsv": 3,
        "post-vtable-slots.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    for address, (name, signature) in PRIMARY_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    process = metadata.get("0x0045d7e0", {})
    comment = process.get("comment", "")
    for token in PROCESS_COMMENT_TOKENS:
        require(token in comment, f"missing process comment token: {token}", failures)

    tag_rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    process_tags = set(tag_rows.get("0x0045d7e0", {}).get("tags", "").split(";"))
    require(PROCESS_TAGS.issubset(process_tags), f"missing process tags: {PROCESS_TAGS - process_tags}", failures)

    vtable_rows = read_tsv(BASE / "post-vtable-slots.tsv")
    for slot, expected_name in VTABLE_SLOTS.items():
        row = next((item for item in vtable_rows if item.get("slot_index") == slot), None)
        require(row is not None, f"missing vtable slot {slot}", failures)
        if row is not None:
            require(row.get("function_name") == expected_name, f"vtable slot {slot} mismatch", failures)
            require(row.get("status") == "OK", f"vtable slot {slot} status mismatch", failures)

    decompile_tokens = {
        "post-decompile/0045d7e0_CFEPGoodies__Process.c": (
            "IsCheatActive",
            "g_Cheat_MALLOY",
            "g_Cheat_LATETE",
            "CFEPGoodies__FreeUpGoodyResources",
            "CFEPGoodies__LoadingGoodyPoll",
            "get_goodie_number",
            "CFEPCommon__StopVideo",
            "CFMV__PlayFullscreenWithLoadingGate",
            "CFEPCommon__StartVideo",
        ),
        "post-decompile/0045cde0_CFEPGoodies__ButtonPressed.c": ("get_goodie_number", "CFEPGoodies__StartLoadingGoody"),
        "post-render-context-decompile/004679e0_CFrontEnd__RenderPreCommonFade.c": ("CFrontEnd__RenderPreCommonFade",),
        "post-render-context-decompile/00452ce0_CFrontEnd__RenderVideoQuadScaledToWindow.c": ("CFrontEnd__RenderVideoQuadScaledToWindow",),
    }
    for relative, tokens in decompile_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token in {relative}: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=1 tags_added=11 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 comment_only_updated=1 tags_added=11 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-xrefs.log": "Wrote 132 rows",
        "post-instructions.log": "Wrote 5274 function-body instruction rows",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-context-metadata.log": "targets=15 found=15 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "post-context-xrefs.log": "Wrote 462 rows",
        "post-context-instructions.log": "Wrote 7241 function-body instruction rows",
        "post-context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "post-render-context-metadata.log": "targets=3 found=3 missing=0",
        "post-render-context-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "post-render-context-xrefs.log": "Wrote 17 rows",
        "post-render-context-instructions.log": "Wrote 132 function-body instruction rows",
        "post-render-context-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=9",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        require("REPORT: Save succeeded" in text, f"missing save success in {relative}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174590855, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        GOODIES_INDEX,
        GOODIES_PROCESS,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-goodies-resource-wall-review-wave1050")
        == r"py -3 tools\ghidra_goodies_resource_wall_review_wave1050_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1050-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1050 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1050 goodies resource wall review" for row in ledger_rows), "missing Wave1050 ledger row", failures)
    require(
        any(row.get("task") == "Wave1050 goodies resource wall review" and row.get("attempt_id") == 20632 for row in attempts),
        "missing Wave1050 attempt row",
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
        print("Wave1050 Goodies resource-wall probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1050 Goodies resource-wall probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
