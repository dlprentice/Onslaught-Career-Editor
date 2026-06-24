#!/usr/bin/env python3
"""Validate Wave1087 HiveBoss unit vtable-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1087-hiveboss-unit-vtable-tail-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_hiveboss_unit_vtable_tail_review_wave1087_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
HIVEBOSS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HiveBoss.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-141730_post_wave1087_hiveboss_unit_vtable_tail_verified"
TAG = "hiveboss-unit-vtable-tail-review-wave1087"

TARGETS = {
    "0x00480000": (
        "CHiveBossVFunc__CheckField170AndMaybeReturn64_00480000",
        "int __thiscall CHiveBossVFunc__CheckField170AndMaybeReturn64_00480000(void * this, void * arg)",
        ("Slot 26", "0x005e16d0", "0x0062ccb8", "0x64"),
    ),
    "0x0050eb10": (
        "CHiveBossVFunc__GetClassNameString_0050eb10",
        "char * __thiscall CHiveBossVFunc__GetClassNameString_0050eb10(void * this)",
        ("Slot 37", "0x005e16fc", "0x0063d844", "CHiveBoss"),
    ),
    "0x0050eb20": (
        "CHiveBossVFunc__ForwardArgWithFlags40100400_0050eb20",
        "void __thiscall CHiveBossVFunc__ForwardArgWithFlags40100400_0050eb20(void * this, int value)",
        ("Slot 68", "0x005e1778", "0x40100400"),
    ),
    "0x00480050": (
        "CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050",
        "void __thiscall CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050(void * this, void * hitContext, void * sourceThing, void * arg2, void * arg3)",
        ("Slot 70", "0x005e1780", "0x01000000", "CUnit__ApplyDamage"),
    ),
    "0x0050eb40": (
        "CHiveBossVFunc__ReturnFloat005d8580_0050eb40",
        "float __thiscall CHiveBossVFunc__ReturnFloat005d8580_0050eb40(void * this)",
        ("Slot 75", "0x005e1794", "0x005d8580"),
    ),
    "0x004802f0": (
        "CHiveBossVFunc__MaybeScheduleEvent1388ForField74_004802f0",
        "int __thiscall CHiveBossVFunc__MaybeScheduleEvent1388ForField74_004802f0(void * this)",
        ("Slot 80", "0x005e17a8", "0x1388", "0x00672fc8"),
    ),
    "0x00480220": (
        "CHiveBossVFunc__AccumulateMotionOffsetsThenTailJmp4fa8d0_00480220",
        "void __thiscall CHiveBossVFunc__AccumulateMotionOffsetsThenTailJmp4fa8d0_00480220(void * this)",
        ("Slot 96", "0x005e17e8", "this+0x29c", "0x004fa8d0"),
    ),
    "0x00480690": (
        "CHiveBossVFunc__ForwardArgToThingHelper4f3ac0_00480690",
        "void __thiscall CHiveBossVFunc__ForwardArgToThingHelper4f3ac0_00480690(void * this, void * arg)",
        ("Slot 120", "0x005e1848", "0x004f3ac0"),
    ),
    "0x00480340": (
        "CHiveBossVFunc__BuildField164ContextAndDispatch_00480340",
        "void __thiscall CHiveBossVFunc__BuildField164ContextAndDispatch_00480340(void * this)",
        ("Slot 125", "0x005e185c", "this+0x164", "0x008553f8"),
    ),
    "0x00480080": (
        "CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080",
        "void __thiscall CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080(void * this, void * outVector)",
        ("Slot 140", "0x005e1898", "0x008a9d3c", "0x0047eb80"),
    ),
}

TARGET_XREFS = {
    "0x00480000": "0x005e16d0",
    "0x0050eb10": "0x005e16fc",
    "0x0050eb20": "0x005e1778",
    "0x00480050": "0x005e1780",
    "0x0050eb40": "0x005e1794",
    "0x004802f0": "0x005e17a8",
    "0x00480220": "0x005e17e8",
    "0x00480690": "0x005e1848",
    "0x00480340": "0x005e185c",
    "0x00480080": "0x005e1898",
}

STRING_EXPECTATIONS = {
    "string-0063d844.tsv": "CHiveBoss",
    "string-0062ccb8.tsv": "!!all flash!!",
    "string-0062cddc.tsv": "hb_maxvelx",
    "string-0062cdd0.tsv": "hb_maxvely",
    "string-0062cdc4.tsv": "hb_maxvelz",
    "string-0062cdb4.tsv": "hb_rotate_speed",
    "string-0062cd94.tsv": "hb_core_top_inner_rotate_speed",
    "string-0062cd74.tsv": "hb_core_top_outer_rotate_speed",
    "string-0062cd54.tsv": "hb_core_mid_inner_rotate_speed",
    "string-0062cd34.tsv": "hb_core_mid_outer_rotate_speed",
    "string-0062cd14.tsv": "hb_core_bot_inner_rotate_speed",
    "string-0062ccf4.tsv": "hb_core_bot_outer_rotate_speed",
    "string-0062cce4.tsv": "hb_safe_dist",
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave1087-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "function-boundary-recovered",
    "vtable-boundary",
    "hiveboss-vtable",
    "hiveboss-vfunc",
}

DOC_TOKENS = (
    "Wave1087",
    TAG,
    "0x00480000 CHiveBossVFunc__CheckField170AndMaybeReturn64_00480000",
    "0x0050eb10 CHiveBossVFunc__GetClassNameString_0050eb10",
    "0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050",
    "0x00480220 CHiveBossVFunc__AccumulateMotionOffsetsThenTailJmp4fa8d0_00480220",
    "0x00480340 CHiveBossVFunc__BuildField164ContextAndDispatch_00480340",
    "0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080",
    "158",
    "2",
    "1482/1560 = 95.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6365/6365 = 100.00%",
    BACKUP_PATH,
    "boundary recovery",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime proof complete",
    "gameplay outcomes proven",
    "rebuild parity proven",
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


def strict_count(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "candidate-code-targets.txt": 10,
        "candidate-all-targets.txt": 12,
        "vtable-targets.txt": 1,
        "pre-diagnose.tsv": 12,
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 12,
        "pre-instructions-around.tsv": 1052,
        "pre-instructions-wide.tsv": 2570,
        "pre-decompile/index.tsv": 10,
        "pre-vtable-slots.tsv": 160,
        "post-diagnose.tsv": 12,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 328,
        "post-decompile/index.tsv": 10,
        "post-vtable-slots.tsv": 160,
    }
    for relative, expected in expected_counts.items():
        path = BASE / relative
        if relative.endswith(".txt"):
            count = len([line for line in read_text(path).splitlines() if line.strip() and not line.startswith("#")])
        else:
            count = len(read_tsv(path))
        require(count == expected, f"{relative} row/count mismatch: {count} != {expected}", failures)

    pre_diagnose = read_tsv(BASE / "pre-diagnose.tsv")
    require(sum(1 for row in pre_diagnose if row.get("memory_block") == ".text" and row.get("status") == "INSTRUCTION_NO_FUNCTION") == 10, "pre text missing-boundary count mismatch", failures)
    require(sum(1 for row in pre_diagnose if row.get("memory_block") == ".rdata" and row.get("status") == "UNDEFINED") == 2, "pre rdata undefined count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave1087 static read-back", "exact source virtual name", *comment_tokens):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"tags missing at {address}: {COMMON_TAGS - actual}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref_row = xrefs.get(address)
        require(xref_row is not None, f"missing xref at {address}", failures)
        if xref_row is not None:
            require(normalize_address(xref_row.get("from_addr", "")) == TARGET_XREFS[address], f"xref source mismatch at {address}", failures)
            require(xref_row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"string mismatch in {relative}", failures)

    post_slots = read_tsv(BASE / "post-vtable-slots.tsv")
    require(sum(1 for row in post_slots if row.get("status") == "OK") == 158, "post vtable OK mismatch", failures)
    require(sum(1 for row in post_slots if row.get("status") == "NO_FUNCTION_AT_POINTER") == 2, "post vtable NO_FUNCTION mismatch", failures)
    require(all(row.get("pointer_addr") in {"00617f58", "006178c0"} for row in post_slots if row.get("status") == "NO_FUNCTION_AT_POINTER"), "unexpected post vtable unresolved pointer", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 created=10 would_create=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
        "post-instructions.log": "Wrote 328 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=160",
        "quality-refresh.log": "total_functions=6365 commented_functions=6365",
        "queue-probe.log": "Status: PASS",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1087.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1087_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BAD:", "BADADDR", "BADNAME", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6365, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain-owner count mismatch", failures)
    require(quality["helperAddressNameCount"] == 0, "helper-address count mismatch", failures)
    require(quality["wrapperAddressNameCount"] == 0, "wrapper-address count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = strict_count(rows)
    require(len(rows) == 6365, "quality TSV row count mismatch", failures)
    require(commented == 6365, "quality TSV commented mismatch", failures)
    require(strict == 6365, "quality TSV strict clean mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175082375, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    progress = read_json(PROGRESS_JSON)
    require(progress.get("schema") == "bea-static-reaudit-progress.v1", "progress schema mismatch", failures)
    require(progress.get("latestWave", {}).get("tag") == TAG, "progress latest-wave tag mismatch", failures)
    require(progress.get("latestWave", {}).get("backup") == BACKUP_PATH, "progress backup mismatch", failures)
    function_quality = progress.get("functionQuality", {})
    require(function_quality.get("totalFunctions") == 6365, "progress total mismatch", failures)
    require(function_quality.get("commentedFunctions") == 6365, "progress commented mismatch", failures)
    require(function_quality.get("commentlessFunctions") == 0, "progress commentless mismatch", failures)
    require(function_quality.get("undefinedSignatures") == 0, "progress undefined mismatch", failures)
    require(function_quality.get("paramSignatures") == 0, "progress param mismatch", failures)
    require(function_quality.get("strictCleanSignatureProxy") == "6365/6365 = 100.00%", "progress strict proxy mismatch", failures)
    expanded = progress.get("post100Reaudit", {}).get("expandedStaticSurface", {})
    require(expanded.get("completed") == 1482, "progress expanded completed mismatch", failures)
    require(expanded.get("total") == 1560, "progress expanded total mismatch", failures)
    require(expanded.get("percent") == "95.00%", "progress expanded percent mismatch", failures)
    focused = progress.get("post100Reaudit", {}).get("wave911Focused", {})
    require(focused.get("completed") == 812, "progress focused completed mismatch", failures)
    require(focused.get("total") == 1408, "progress focused total mismatch", failures)
    require(focused.get("percent") == "57.67%", "progress focused percent mismatch", failures)
    top500 = progress.get("post100Reaudit", {}).get("wave911Top500RiskRanked", {})
    require(top500.get("completed") == 500, "progress top500 completed mismatch", failures)
    require(top500.get("total") == 500, "progress top500 total mismatch", failures)
    require(top500.get("percent") == "100.00%", "progress top500 percent mismatch", failures)
    latest_sample = progress.get("latestSample", {})
    require(latest_sample.get("ok") == 158, "progress sample OK mismatch", failures)
    require(latest_sample.get("total") == 160, "progress sample total mismatch", failures)
    require(latest_sample.get("percent") == "98.75%", "progress sample percent mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, FUNCTION_COVERAGE, GHIDRA_REFERENCE, CAMPAIGN, HIVEBOSS_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-hiveboss-unit-vtable-tail-review-wave1087")
        == r"py -3 tools\ghidra_hiveboss_unit_vtable_tail_review_wave1087_probe.py --check",
        "missing Wave1087 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1087-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1087 --check",
        "missing Wave1087 aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1087 HiveBoss unit vtable tail review" for row in ledger_rows), "missing Wave1087 ledger row", failures)
    require(any(row.get("task") == "Wave1087 HiveBoss unit vtable tail review" for row in attempt_rows), "missing Wave1087 attempt row", failures)


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
        print("Wave1087 HiveBoss unit vtable-tail review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1087 HiveBoss unit vtable-tail review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
