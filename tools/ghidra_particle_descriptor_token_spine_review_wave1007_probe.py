#!/usr/bin/env python3
"""Validate Wave1007 particle descriptor token-spine review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1007-particle-descriptor-token-spine-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_particle_descriptor_token_spine_review_wave1007_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1007_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-143106_post_wave1007_particle_descriptor_token_spine_review_verified"

TARGETS = {
    "0x004c07f0": ("CPDSimpleSprite__WriteTokenFields", "void __fastcall CPDSimpleSprite__WriteTokenFields(void * this)"),
    "0x004c1970": ("CPDEmitter__WriteTokenFields", "void __fastcall CPDEmitter__WriteTokenFields(void * this)"),
    "0x004c2220": ("CPDSelector__WriteTokenFields", "void __fastcall CPDSelector__WriteTokenFields(void * this)"),
    "0x004c2400": ("CPDColourRange__WriteTokenFields", "void __fastcall CPDColourRange__WriteTokenFields(void * this)"),
    "0x004c2ca0": ("CPDShape__WriteTokenFields", "void __fastcall CPDShape__WriteTokenFields(void * this)"),
    "0x004c3440": ("CPDTrail__WriteTokenFields", "void __fastcall CPDTrail__WriteTokenFields(void * this)"),
    "0x004c4920": ("CPDFunction__WriteTokenFields", "void __fastcall CPDFunction__WriteTokenFields(void * this)"),
    "0x004c49b0": ("CPDMesh__dtor_base", "void __fastcall CPDMesh__dtor_base(void * this)"),
    "0x004c4ae0": ("CPDMesh__scalar_deleting_dtor", "void * __thiscall CPDMesh__scalar_deleting_dtor(void * this, byte flags)"),
    "0x004c4c70": ("CPDMesh__WriteTokenFields", "void __fastcall CPDMesh__WriteTokenFields(void * this)"),
    "0x004c53b0": ("CPDFoR__WriteTokenFields", "void __fastcall CPDFoR__WriteTokenFields(void * this)"),
    "0x004c5410": ("CParticleDescriptor__Update", "int __thiscall CParticleDescriptor__Update(void * this, void * particle)"),
    "0x004c5730": ("CParticleDescriptor__Load", "int __thiscall CParticleDescriptor__Load(void * this, void * token_archive)"),
    "0x004c59e0": ("CPDPMesh__WriteTokenFields", "void __fastcall CPDPMesh__WriteTokenFields(void * this)"),
}

CONTEXT_TARGETS = {
    "0x004c0370": "CParticleDescriptor__PushCurrentToHistoryAndSetNow",
    "0x004c0450": "CParticleDescriptor__Load12DwordsAndMarkDirty",
    "0x004c5c50": "CPDSimpleSprite__BuildUvAtlasBuckets",
    "0x004c5d50": "CPDSimpleSprite__ProcessAndRenderSpriteList",
    "0x004cb3d0": "CParticleManager__CreateEffect",
    "0x004cb5c0": "CParticleManager__AllocateParticle",
    "0x004f5b70": "CParticleDescriptor__SetIndexedParam",
}

EXPECTED_VTABLE_TYPES = {
    "005ddb3c": "CPDMesh",
    "005ddbb8": "CPDFunction",
    "005ddc88": "CPDTrail",
    "005ddcf0": "CPDShape",
    "005dddc0": "CPDColourRange",
    "005dde28": "CPDSelector",
    "005ddef8": "CPDEmitter",
    "005ddf60": "CPDSimpleSprite",
    "005ddfc8": "CPDFoR",
    "005de030": "CPDPMesh",
}

EXPECTED_SLOT_ROWS = {
    ("005ddb3c", "0", "004c4ae0"),
    ("005ddb3c", "7", "004c4c70"),
    ("005ddbb8", "7", "004c4920"),
    ("005ddc88", "7", "004c3440"),
    ("005ddcf0", "7", "004c2ca0"),
    ("005dddc0", "7", "004c2400"),
    ("005dde28", "7", "004c2220"),
    ("005ddef8", "7", "004c1970"),
    ("005ddf60", "7", "004c07f0"),
    ("005ddfc8", "7", "004c53b0"),
    ("005ddfc8", "10", "004c5410"),
    ("005ddfc8", "32", "004c5730"),
    ("005de030", "7", "004c59e0"),
}

DOC_TOKENS = (
    "Wave1007",
    "particle-descriptor-token-spine-review-wave1007",
    "0x004c07f0 CPDSimpleSprite__WriteTokenFields",
    "0x004c1970 CPDEmitter__WriteTokenFields",
    "0x004c2220 CPDSelector__WriteTokenFields",
    "0x004c2400 CPDColourRange__WriteTokenFields",
    "0x004c2ca0 CPDShape__WriteTokenFields",
    "0x004c3440 CPDTrail__WriteTokenFields",
    "0x004c4920 CPDFunction__WriteTokenFields",
    "0x004c49b0 CPDMesh__dtor_base",
    "0x004c5410 CParticleDescriptor__Update",
    "0x004c5730 CParticleDescriptor__Load",
    "0x004c59e0 CPDPMesh__WriteTokenFields",
    "499/1408 = 35.44%",
    "676/1478 = 45.74%",
    "398/500 = 79.60%",
    "6223/6223 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime particle behavior proven",
    "runtime particle loading proven",
    "runtime particle rendering proven",
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
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def contains_token(text: str, token: str) -> bool:
    return (
        token in text
        or token.replace("\\", "\\\\") in text
        or token.replace("\\", "\\\\\\\\") in text
        or token.replace("\\\\", "\\") in text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    )


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 14,
        "pre-tags.tsv": 14,
        "pre-xrefs.tsv": 14,
        "pre-instructions.tsv": 1133,
        "pre-decompile/index.tsv": 14,
        "context-metadata.tsv": 7,
        "context-instructions.tsv": 2370,
        "context-decompile/index.tsv": 7,
        "vtable-slots.tsv": 480,
        "vtable-types.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "pre-metadata.tsv")
    tags = read_tsv(BASE / "pre-tags.tsv")
    decompile_index = read_tsv(BASE / "pre-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
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
            for tag in ("static-reaudit", "retail-binary-evidence", "comment-hardened", "particle-descriptor-wave461"):
                require(tag in actual_tags, f"missing tag {address}: {tag}", failures)

        require(
            any(normalize_address(row.get("target_addr", "")) == address for row in xrefs),
            f"xref missing {address}",
            failures,
        )

    context = read_tsv(BASE / "context-metadata.tsv")
    context_index = read_tsv(BASE / "context-decompile" / "index.tsv")
    for address, name in CONTEXT_TARGETS.items():
        row = row_by_address(context, address)
        require(row is not None, f"context metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = row_by_address(context_index, address)
        require(dec is not None, f"context decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"context decompile name mismatch {address}", failures)
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    types = read_tsv(BASE / "vtable-types.tsv")
    for vtable, type_name in EXPECTED_VTABLE_TYPES.items():
        row = row_by_address(types, "0x" + vtable, "vtable")
        require(row is not None, f"missing vtable type {vtable}", failures)
        if row:
            require(row.get("demangled_type_name") == type_name, f"vtable type mismatch {vtable}", failures)

    slots = read_tsv(BASE / "vtable-slots.tsv")
    for vtable, slot, pointer in EXPECTED_SLOT_ROWS:
        require(
            any(
                normalize_address(row.get("vtable", "")) == "0x" + vtable
                and row.get("slot_index") == slot
                and normalize_address(row.get("pointer_addr", "")) == "0x" + pointer
                and row.get("status") == "OK"
                for row in slots
            ),
            f"missing vtable slot {vtable}[{slot}] -> {pointer}",
            failures,
        )

    update_text = read_text(BASE / "pre-decompile" / "004c5410_CParticleDescriptor__Update.c")
    for token in ("CParticleManager__CreateEffect", "CParticleManager__AllocateParticle"):
        require(token in update_text, f"update decompile missing {token}", failures)

    load_text = read_text(BASE / "pre-decompile" / "004c5730_CParticleDescriptor__Load.c")
    for token in ("CTokenArchive__ReadNextToken", "CParticleDescriptor__SetIndexedParam", "CTokenArchive__RegisterReferenceFixup"):
        require(token in load_text, f"load decompile missing {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "pre-metadata.log": "targets=14 found=14 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "pre-xrefs.log": "Wrote 14 rows",
        "pre-instructions.log": "Wrote 1133 function-body instruction rows",
        "pre-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
        "context-metadata.log": "targets=7 found=7 missing=0",
        "context-instructions.log": "Wrote 2370 function-body instruction rows",
        "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "vtable-slots.log": "targets=10 rows=480",
        "vtable-types.log": "ResolveVtableTypeNames complete: rows=10",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        PARTICLE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-particle-descriptor-token-spine-review-wave1007")
        == r"py -3 tools\ghidra_particle_descriptor_token_spine_review_wave1007_probe.py --check",
        "missing Wave1007 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1007-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1007 --check",
        "missing Wave1007 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1007 particle descriptor token spine review" for row in ledger_rows), "missing Wave1007 ledger row", failures)
    require(
        any(row.get("task") == "Wave1007 particle descriptor token spine review" and row.get("attempt_id") == 20589 for row in attempts),
        "missing Wave1007 attempt row",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6223, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)
    if failures:
        print("Wave1007 particle descriptor token spine review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1007 particle descriptor token spine review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
