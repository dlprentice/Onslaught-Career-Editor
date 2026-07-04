#!/usr/bin/env python3
"""Validate Wave1031 particle/CPDSimpleSprite runtime-transform review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1031-particle-cpdsimplesprite-runtime-transform-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_particle_cpdsimplesprite_runtime_transform_review_wave1031_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1031_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
TOKEN_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "TokenArchive.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified"

TARGETS = {
    "0x004c0150": (
        "CParticle__ApplyParentTransformOrStoreLink",
        "void __stdcall CParticle__ApplyParentTransformOrStoreLink(void * particle, void * parent_particle, int link_parent_only)",
        ("parent_particle", "link_parent_only", "particle +0x58"),
    ),
    "0x004c0940": (
        "CPDSimpleSprite__SetUVFromTileIndex",
        "void __thiscall CPDSimpleSprite__SetUVFromTileIndex(void * this, int tile_index, uint tile_grid_selector, int unused_context)",
        ("atlas UV", "+0xb8", "+0xc4"),
    ),
    "0x004c5280": (
        "CPDSimpleSprite__CopyTransformMatrix",
        "void __thiscall CPDSimpleSprite__CopyTransformMatrix(void * this, void * out_matrix, void * unused_context)",
        ("matrix", "output block", "decompiler artifacts"),
    ),
    "0x004f5b70": (
        "CTokenArchive__BindIndexedFieldPointer",
        "void __thiscall CTokenArchive__BindIndexedFieldPointer(void * this, int slot_index, void * field_ptr)",
        ("TokenArchive indexed field-pointer binder", "0x004c57d4", "0x004f5b80"),
    ),
    "0x004c5410": (
        "CParticleDescriptor__Update",
        "int __thiscall CParticleDescriptor__Update(void * this, void * particle)",
        ("CParticleDescriptor update", "CParticleManager__CreateEffect", "CParticleManager__AllocateParticle"),
    ),
}

CONTEXT_TARGETS = {
    "0x004c5730": "CParticleDescriptor__Load",
    "0x004c0c70": "CPDSimpleSprite__EvalExpressionNode",
    "0x004c07f0": "CPDSimpleSprite__WriteTokenFields",
    "0x004cc870": "CParticleSet__dtor_base",
    "0x004cdba0": "CParticleManager__LinkNodeByOffset3C40",
    "0x004cdbe0": "CParticleManager__UnlinkNodeByOffset3C40",
}

TOKENARCHIVE_CONTEXT = {
    "0x004f5b80": "CTokenArchive__RegisterReferenceFixup",
    "0x004f5ba0": "CTokenArchive__ResolveReferences",
}

DOC_TOKENS = (
    "Wave1031",
    "particle-cpdsimplesprite-runtime-transform-review-wave1031",
    "0x004f5b70 CTokenArchive__BindIndexedFieldPointer",
    "0x004c0150 CParticle__ApplyParentTransformOrStoreLink",
    "0x004c0940 CPDSimpleSprite__SetUVFromTileIndex",
    "0x004c5280 CPDSimpleSprite__CopyTransformMatrix",
    "0x004c5410 CParticleDescriptor__Update",
    "0x004f5b80 CTokenArchive__RegisterReferenceFixup",
    "626/1408 = 44.46%",
    "855/1493 = 57.27%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "one rename/signature/comment correction",
)

OVERCLAIMS = (
    "runtime particle parsing proven",
    "runtime particle rendering proven",
    "runtime transform behavior proven",
    "exact token-slot semantics proven",
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
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 19,
        "instructions.tsv": 539,
        "decompile/index.tsv": 5,
        "context-metadata.tsv": 6,
        "context-tags.tsv": 6,
        "context-xrefs.tsv": 21,
        "context-instructions.tsv": 667,
        "context-decompile/index.tsv": 6,
        "setter-xref-windows.tsv": 255,
        "tokenarchive-context-metadata.tsv": 2,
        "tokenarchive-context-instructions.tsv": 83,
        "tokenarchive-context-decompile/index.tsv": 2,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 19,
        "post-instructions.tsv": 539,
        "post-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            require("static-reaudit" in tag_row.get("tags", ""), f"missing static-reaudit tag at {address}", failures)
            if address == "0x004f5b70":
                for token in ("name-corrected", "signature-hardened", "tokenarchive-indexed-field-pointer", "wave1031-readback-verified"):
                    require(token in tag_row.get("tags", ""), f"missing Wave1031 tag at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing post decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    context_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context_metadata.get(address)
        require(row is not None, f"missing context metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context metadata status mismatch at {address}", failures)

    token_context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tokenarchive-context-metadata.tsv")}
    for address, name in TOKENARCHIVE_CONTEXT.items():
        row = token_context.get(address)
        require(row is not None, f"missing TokenArchive context metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"TokenArchive context name mismatch at {address}", failures)

    setter_windows = read_text(BASE / "setter-xref-windows.tsv")
    for token in ("0x004c57d4", "0x004c57e9", "MOV\tECX, EDI", "CALL\t0x004f5b70"):
        require(token in setter_windows, f"missing setter xref-window token: {token}", failures)

    post_decompile = read_text(BASE / "post-decompile" / "004f5b70_CTokenArchive__BindIndexedFieldPointer.c")
    for token in ("CTokenArchive__BindIndexedFieldPointer", "slot_index", "field_ptr", "slot_index * 4 + 0xc"):
        require(token in post_decompile, f"missing post decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=5 found=5 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "xrefs.log": "Wrote 19 rows",
        "instructions.log": "Wrote 539 function-body instruction rows",
        "decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=6 found=6 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "context-xrefs.log": "Wrote 21 rows",
        "context-instructions.log": "Wrote 667 function-body instruction rows",
        "context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "setter-xref-windows.log": "targets=15 missing=0",
        "tokenarchive-context-metadata.log": "targets=2 found=2 missing=0",
        "tokenarchive-context-instructions.log": "Wrote 83 function-body instruction rows",
        "tokenarchive-context-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 19 rows",
        "post-instructions.log": "Wrote 539 function-body instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_expectations = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 tags_added=7 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 tags_added=7 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
    }
    for relative, token in apply_expectations.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing apply summary in {relative}", failures)
        require("REPORT: Save succeeded" in text, f"missing save success in {relative}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected apply failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_docs_and_state(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "queue commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "queue undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "queue param_N mismatch", failures)
    require(quality["legacyWeakNameCount"] == 0, "queue weak-name mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-particle-cpdsimplesprite-runtime-transform-review-wave1031")
        == r"py -3 tools\ghidra_particle_cpdsimplesprite_runtime_transform_review_wave1031_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1031-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1031 --check",
        "missing aggregate package script",
        failures,
    )

    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        PARTICLE_DOC,
        TOKEN_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1031 particle CPDSimpleSprite runtime transform review" for row in ledger_rows), "missing Wave1031 ledger row", failures)
    require(
        any(row.get("task") == "Wave1031 particle CPDSimpleSprite runtime transform review" and row.get("attempt_id") == 20613 for row in attempt_rows),
        "missing Wave1031 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_docs_and_state(failures)

    if failures:
        print("Wave1031 particle CPDSimpleSprite runtime-transform probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1031 particle CPDSimpleSprite runtime-transform probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
