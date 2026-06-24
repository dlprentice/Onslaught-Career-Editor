#!/usr/bin/env python3
"""Validate Wave1014 ParticleSet load/lifecycle read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1014-particle-set-load-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_particle_set_load_lifecycle_review_wave1014_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1014_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PARTICLE_SET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleSet.cpp" / "_index.md"
PARTICLE_MANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified"

TARGETS = {
    "0x004cc020": ("CParticleSet__CreateByType", "void * __thiscall CParticleSet__CreateByType(void * this, char * set_name, int type_id, void * context)"),
    "0x004cc850": ("CParticleSet__Init", "void __fastcall CParticleSet__Init(void * particle_set)"),
    "0x004cc870": ("CParticleSet__dtor_base", "void __fastcall CParticleSet__dtor_base(void * particle_set)"),
    "0x004ccb40": ("CParticleSet__shared_scalar_deleting_dtor", "void * __thiscall CParticleSet__shared_scalar_deleting_dtor(void * this, int flags)"),
    "0x004ccc50": ("CPDSelector__DispatchChildVFunc20", "void __thiscall CPDSelector__DispatchChildVFunc20(void * this, int dispatch_context)"),
    "0x004cd290": ("CParticleSet__InitType11", "void __fastcall CParticleSet__InitType11(void * particle_set)"),
    "0x004cd2d0": ("CParticleSet__InitType12", "void __fastcall CParticleSet__InitType12(void * particle_set)"),
    "0x004cd3c0": ("CParticleSet__InitType13", "void __fastcall CParticleSet__InitType13(void * particle_set)"),
    "0x004cd7a0": ("CParticleSet__FindByNameAndTrackLinkSlot", "void * __thiscall CParticleSet__FindByNameAndTrackLinkSlot(void * this, char * set_name)"),
    "0x004cd7f0": ("CParticleSet__LoadFromArchive", "int __thiscall CParticleSet__LoadFromArchive(void * this, void * archive_source)"),
    "0x004cda60": ("CParticleSet__LoadParticleSetFile", "int __thiscall CParticleSet__LoadParticleSetFile(void * this, int particle_set_mode)"),
    "0x004cdba0": ("CParticleManager__LinkNodeByOffset3C40", "void __thiscall CParticleManager__LinkNodeByOffset3C40(void * this, void * node)"),
    "0x004cdbe0": ("CParticleManager__UnlinkNodeByOffset3C40", "void __thiscall CParticleManager__UnlinkNodeByOffset3C40(void * this, void * node)"),
}

CONTEXT_TARGETS = {
    "0x004c0150": ("CParticle__ApplyParentTransformOrStoreLink", "void __stdcall CParticle__ApplyParentTransformOrStoreLink(void * particle, void * parent_particle, int link_parent_only)"),
    "0x004c0510": ("CParticleManager__AppendNodeToActiveList", "void __thiscall CParticleManager__AppendNodeToActiveList(void * this, void * node, void * unused_context)"),
    "0x004c0560": ("CParticleManager__UnlinkNodeFromActiveList", "void __thiscall CParticleManager__UnlinkNodeFromActiveList(void * this, void * node, void * unused_context)"),
    "0x004cae50": ("CParticle__Destroy", "void __fastcall CParticle__Destroy(void * particle)"),
    "0x004cb0e0": ("CParticleManager__Init", "void * __fastcall CParticleManager__Init(void * manager)"),
    "0x004cb1b0": ("CParticleManager__Shutdown", "void __fastcall CParticleManager__Shutdown(void * manager)"),
    "0x004cb210": ("CParticleManager__Update", "int __thiscall CParticleManager__Update(void * this, float delta_time, int update_context)"),
    "0x004cb5c0": ("CParticleManager__AllocateParticle", "void * __thiscall CParticleManager__AllocateParticle(void * this, void * particle_set, int force_allocate)"),
    "0x004cb920": ("CParticleManager__UpdateParticleAndRecycleIfDead", "void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)"),
    "0x004cbff0": ("CParticleManager__DestroyParticleList", "void __fastcall CParticleManager__DestroyParticleList(void * list_head_ptr)"),
    "0x004c5410": ("CParticleDescriptor__Update", "int __thiscall CParticleDescriptor__Update(void * this, void * particle)"),
    "0x004c5730": ("CParticleDescriptor__Load", "int __thiscall CParticleDescriptor__Load(void * this, void * token_archive)"),
    "0x0048ddd0": ("CDXMemBuffer__OpenReadMode11", "int __thiscall CDXMemBuffer__OpenReadMode11(void * this, char * filename)"),
    "0x0048ddf0": ("CDXMemBuffer__Close_Thunk", "bool __fastcall CDXMemBuffer__Close_Thunk(void * this)"),
    "0x004cdb90": ("CDXMemBuffer__dtor_base_Thunk", "void __fastcall CDXMemBuffer__dtor_base_Thunk(void)"),
    "0x00547d70": ("CDXMemBuffer__ctor", "void * __fastcall CDXMemBuffer__ctor(void * this)"),
}

DOC_TOKENS = (
    "Wave1014",
    "particle-set-load-lifecycle-review-wave1014",
    "0x004cc020 CParticleSet__CreateByType",
    "0x004cc850 CParticleSet__Init",
    "0x004ccb40 CParticleSet__shared_scalar_deleting_dtor",
    "0x004ccc50 CPDSelector__DispatchChildVFunc20",
    "0x004cd290 CParticleSet__InitType11",
    "0x004cd2d0 CParticleSet__InitType12",
    "0x004cd3c0 CParticleSet__InitType13",
    "0x004cd7f0 CParticleSet__LoadFromArchive",
    "0x004cda60 CParticleSet__LoadParticleSetFile",
    "0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40",
    "505/1408 = 35.87%",
    "729/1493 = 48.83%",
    "431/500 = 86.20%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime particle behavior proven",
    "runtime particle loading proven",
    "runtime effect behavior proven",
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
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 79,
        "pre-instructions.tsv": 997,
        "pre-decompile/index.tsv": 13,
        "context-metadata.tsv": 16,
        "context-xrefs.tsv": 54,
        "context-instructions.tsv": 1206,
        "context-decompile/index.tsv": 16,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "pre-metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "pre-tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "pre-decompile" / "index.tsv"), "address")

    for address, (name, signature) in TARGETS.items():
        key = normalize_address(address)
        row = metadata.get(key)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("Static retail" in comment, f"comment boundary missing {address}", failures)

        tag_row = tags.get(key)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(key)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    context = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    context_decompile = rows_by(read_tsv(BASE / "context-decompile" / "index.tsv"), "address")
    for address, (name, signature) in CONTEXT_TARGETS.items():
        key = normalize_address(address)
        row = context.get(key)
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = context_decompile.get(key)
        require(dec is not None, f"missing context decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"context decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    expected_xrefs = {
        ("0x004cc020", "0x004cd7f0", "CParticleSet__LoadFromArchive"),
        ("0x004cc850", "0x004cc020", "CParticleSet__CreateByType"),
        ("0x004cd290", "0x004cc020", "CParticleSet__CreateByType"),
        ("0x004cd2d0", "0x004cc020", "CParticleSet__CreateByType"),
        ("0x004cd3c0", "0x004cc020", "CParticleSet__CreateByType"),
        ("0x004cd7f0", "0x004cda60", "CParticleSet__LoadParticleSetFile"),
        ("0x004cda60", "0x004687e0", "CFrontEnd__LoadSharedResources"),
        ("0x004cda60", "0x0046cd30", "CGame__LoadResources"),
        ("0x004cdba0", "0x004c0510", "CParticleManager__AppendNodeToActiveList"),
        ("0x004cdbe0", "0x004c0560", "CParticleManager__UnlinkNodeFromActiveList"),
    }
    for target, source, function in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == normalize_address(target)
                and normalize_address(row.get("from_function_addr", "")) == normalize_address(source)
                and row.get("from_function") == function
                for row in xrefs
            ),
            f"missing xref {source} -> {target} ({function})",
            failures,
        )


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=13 found=13 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "pre-xrefs.log": "Wrote 79 rows",
        "pre-instructions.log": "Wrote 997 function-body instruction rows",
        "pre-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "context-metadata.log": "targets=16 found=16 missing=0",
        "context-xrefs.log": "Wrote 54 rows",
        "context-instructions.log": "Wrote 1206 function-body instruction rows",
        "context-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
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
    require(backup.get("fileCount") == 18, "backup file count mismatch", failures)
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
        PARTICLE_SET_DOC,
        PARTICLE_MANAGER_DOC,
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
        scripts.get("test:ghidra-particle-set-load-lifecycle-review-wave1014")
        == r"py -3 tools\ghidra_particle_set_load_lifecycle_review_wave1014_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1014-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1014 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1014 particle set load lifecycle review" for row in ledger_rows), "missing Wave1014 ledger row", failures)
    require(any(row.get("task") == "Wave1014 particle set load lifecycle review" and row.get("attempt_id") == 20596 for row in attempts), "missing Wave1014 attempt row", failures)


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
        print("Wave1014 particle-set load/lifecycle probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1014 particle-set load/lifecycle probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
