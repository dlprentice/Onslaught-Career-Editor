#!/usr/bin/env python3
"""Validate Wave1090 CDebris lifecycle/render read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1090-cdebris-lifecycle-render-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cdebris_lifecycle_render_review_wave1090_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1090_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
DEBRIS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "debris.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-135715_post_wave1090_cdebris_lifecycle_render_review_verified"
WAVE_TAG = "cdebris-lifecycle-render-review-wave1090"

TARGETS = {
    "0x004411a0": (
        "CDebris__Init",
        "void __thiscall CDebris__Init(void * this, void * init)",
        "0x005daf34",
        ("grs_tuft1.MSH", "cg_debrisfadestart", "DAT_0066eb78"),
    ),
    "0x00441320": (
        "CDebris__dtor_base",
        "void __fastcall CDebris__dtor_base(void * this)",
        "0x00441383",
        ("DAT_0066eb78", "this+0x7c", "CComplexThing__dtor_base"),
    ),
    "0x00441360": (
        "CDebris__GetClassName",
        "char * __cdecl CDebris__GetClassName(void)",
        "0x005daf2c",
        ("CDebris", "0x006283e0"),
    ),
    "0x00441370": (
        "CDebris__GetClassId",
        "int __cdecl CDebris__GetClassId(void)",
        "0x005daf30",
        ("0x1f", "class/OID id"),
    ),
    "0x00441380": (
        "CDebris__scalar_deleting_dtor",
        "void * __thiscall CDebris__scalar_deleting_dtor(void * this, int flags)",
        "0x005daf14",
        ("CDebris__dtor_base", "flags bit 0", "OID__FreeObject"),
    ),
    "0x004413a0": (
        "CDebris__Render",
        "void __thiscall CDebris__Render(void * this, int renderFlags)",
        "0x005dafa0",
        ("cg_debrisfadestart", "cg_debrisfadeend", "DAT_0063012c", "render-object flags path"),
    ),
    "0x00441420": (
        "CDebris__RenderImposter",
        "void __fastcall CDebris__RenderImposter(void * this)",
        "0x005dafa4",
        ("cg_debrisfadestart", "cg_debrisfadeend", "DAT_0063012c", "imposter"),
    ),
}

VTABLE_SLOTS = {
    "0": "CDebris__scalar_deleting_dtor",
    "6": "CDebris__GetClassName",
    "7": "CDebris__GetClassId",
    "8": "CDebris__Init",
    "35": "CDebris__Render",
    "36": "CDebris__RenderImposter",
}

DOC_TOKENS = (
    "Wave1090",
    WAVE_TAG,
    "0x004411a0 CDebris__Init",
    "0x00441320 CDebris__dtor_base",
    "0x004413a0 CDebris__Render",
    "0x00441420 CDebris__RenderImposter",
    "0x005daf14",
    "grs_tuft1.MSH",
    "DAT_0066eb78",
    "DAT_0063012c",
    "1534/1560 = 98.33%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime render behavior proven",
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
        "primary-metadata.tsv": 7,
        "primary-tags.tsv": 7,
        "primary-xrefs.tsv": 7,
        "primary-instructions.tsv": 202,
        "primary-decompile/index.tsv": 7,
        "context-metadata.tsv": 11,
        "context-tags.tsv": 11,
        "context-xrefs.tsv": 1263,
        "context-instructions.tsv": 460,
        "context-decompile/index.tsv": 11,
        "vtable-slots.tsv": 48,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {
        normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")
    }
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "primary-xrefs.tsv")}

    for address, (name, signature, xref_addr, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            for token in ("debris", "debris-wave347", "retail-binary-evidence", "static-reaudit"):
                require(token in tag_text, f"missing tag at {address}: {token}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref at {address}", failures)
        if xref is not None:
            require(normalize_address(xref.get("from_addr", "")) == xref_addr, f"xref mismatch at {address}", failures)

    init_body = read_text(BASE / "primary-decompile" / "004411a0_CDebris__Init.c")
    render_body = read_text(BASE / "primary-decompile" / "004413a0_CDebris__Render.c")
    imposter_body = read_text(BASE / "primary-decompile" / "00441420_CDebris__RenderImposter.c")
    for token in ("CResourceDescriptor__ctor", "PCRTID__CreateObject", "CConsole__RegisterVariable", "DAT_0066eb78"):
        require(token in init_body, f"missing init decompile token: {token}", failures)
    for body_name, body in (("render", render_body), ("imposter", imposter_body)):
        for token in ("DAT_0063012c", "_DAT_00628300", "_DAT_00628304", "0xff"):
            require(token in body, f"missing {body_name} decompile token: {token}", failures)

    vtable = read_tsv(BASE / "vtable-slots.tsv")
    require(all(row.get("status") == "OK" for row in vtable), "vtable contains non-OK row", failures)
    by_slot = {row["slot_index"]: row for row in vtable}
    for slot, name in VTABLE_SLOTS.items():
        row = by_slot.get(slot)
        require(row is not None, f"missing vtable slot {slot}", failures)
        if row is not None:
            require(row.get("function_name") == name, f"vtable slot {slot} mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=7 found=7 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "primary-xrefs.log": "Wrote 7 rows",
        "primary-instructions.log": "Wrote 202 function-body instruction rows",
        "primary-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "context-metadata.log": "targets=11 found=11 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "context-xrefs.log": "Wrote 1263 rows",
        "context-instructions.log": "Wrote 460 function-body instruction rows",
        "context-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=48",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["status"] == "PASS", "queue status mismatch", failures)
    require(queue["totalFunctions"] == 6410, "queue total mismatch", failures)
    for key in (
        "commentlessFunctionCount",
        "undefinedSignatureCount",
        "paramSignatureCount",
        "uncertainOwnerNameCount",
        "helperAddressNameCount",
        "wrapperAddressNameCount",
    ):
        require(quality[key] == 0, f"queue quality signal mismatch: {key}", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6410, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV contains commentless row", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175541127 or backup.get("totalBytes") == 175541127.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEBRIS_DOC,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
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
        scripts.get("test:ghidra-cdebris-lifecycle-render-review-wave1090")
        == r"py -3 tools\ghidra_cdebris_lifecycle_render_review_wave1090_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1090-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1090 --check",
        "missing aggregate package script",
        failures,
    )

    progress = read_json(PROGRESS_JSON)
    require(progress.get("latestWave", {}).get("wave") == "Wave1090 CDebris lifecycle/render review", "progress latest wave mismatch", failures)
    require(progress.get("post100Reaudit", {}).get("expandedStaticSurface", {}).get("completed") == 1534, "progress completed mismatch", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1090 CDebris lifecycle/render review" for row in ledger), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1090 CDebris lifecycle/render review" and row.get("attempt_id") == 20670 for row in attempts),
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
        print("Wave1090 CDebris lifecycle/render review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1090 CDebris lifecycle/render review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
