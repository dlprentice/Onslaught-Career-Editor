#!/usr/bin/env python3
"""Validate Wave994 ParticleManager core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave994-particle-manager-core-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_particle_manager_core_review_wave994_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-070007_post_wave994_particle_manager_core_review_verified"

TARGETS = {
    "0x004cae50": ("CParticle__Destroy", "void __fastcall CParticle__Destroy(void * particle)"),
    "0x004caf60": ("CParticleManager__CleanupHandles", "void __cdecl CParticleManager__CleanupHandles(void)"),
    "0x004cb0b0": ("ParticleEffectLink__SetHandleStateAndClear", "void __thiscall ParticleEffectLink__SetHandleStateAndClear(void * this, int set_state_one)"),
    "0x004cb0e0": ("CParticleManager__Init", "void * __fastcall CParticleManager__Init(void * manager)"),
    "0x004cb1b0": ("CParticleManager__Shutdown", "void __fastcall CParticleManager__Shutdown(void * manager)"),
    "0x004cb210": ("CParticleManager__Update", "int __thiscall CParticleManager__Update(void * this, float delta_time, int update_context)"),
    "0x004cb3d0": ("CParticleManager__CreateEffect", "void __stdcall CParticleManager__CreateEffect(void * manager, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)"),
    "0x004cb5c0": ("CParticleManager__AllocateParticle", "void * __thiscall CParticleManager__AllocateParticle(void * this, void * particle_set, int force_allocate)"),
    "0x004cb920": ("CParticleManager__UpdateParticleAndRecycleIfDead", "void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)"),
    "0x004cba30": ("CParticleManager__ProjectPointToTerrainWithRadiusClamp", "int __stdcall CParticleManager__ProjectPointToTerrainWithRadiusClamp(void * world_pos, float radius, void * out_pos)"),
    "0x004cba90": ("CParticleManager__ComputeMinCameraDistanceSqForParticle", "double __stdcall CParticleManager__ComputeMinCameraDistanceSqForParticle(void * particle)"),
    "0x004cbca0": ("CParticleManager__UpdateParticles", "void __cdecl CParticleManager__UpdateParticles(void * active_head)"),
    "0x004cbe30": ("CParticleManager__PruneDeadParticles", "int __fastcall CParticleManager__PruneDeadParticles(void * manager)"),
    "0x004cbff0": ("CParticleManager__DestroyParticleList", "void __fastcall CParticleManager__DestroyParticleList(void * list_head_ptr)"),
}

WAVE994_TARGET = "0x004cb920"
WAVE994_TAGS = {
    "static-reaudit",
    "particle-manager-core-review-wave994",
    "wave994-readback-verified",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "phantom-param-corrected",
    "particle-manager-wave463",
    "particle-update",
    "particle-recycle",
}

DOC_TOKENS = (
    "Wave994",
    "particle-manager-core-review-wave994",
    "0x004cb920 CParticleManager__UpdateParticleAndRecycleIfDead",
    "void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)",
    "unused_context",
    "0x004cb924",
    "0x004cba27",
    "461/1408 = 32.74%",
    "563/1478 = 38.09%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime particle behavior proven",
    "exact layout proven",
    "source identity proven",
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


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 14,
        "tags.tsv": 14,
        "xrefs.tsv": 120,
        "instructions.tsv": 1130,
        "decompile/index.tsv": 14,
        "post-metadata.tsv": 14,
        "post-tags.tsv": 14,
        "post-xrefs.tsv": 120,
        "post-instructions.tsv": 1130,
        "post-decompile/index.tsv": 14,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)

    target = metadata[WAVE994_TARGET]
    comment = target.get("comment", "")
    for token in (
        "Wave994 signature correction",
        "RET 0x4",
        "0x004cb924",
        "unused_context",
        "one stack argument",
        "particle-set vfunc +0x28",
        "Static retail-binary evidence only",
    ):
        require(token in comment, f"missing target comment token: {token}", failures)
    require("unused_context" not in target.get("signature", ""), "stale unused_context still present in signature", failures)

    tag_row = tags.get(WAVE994_TARGET)
    require(tag_row is not None, "missing Wave994 tag row", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(WAVE994_TAGS.issubset(actual_tags), f"Wave994 tags missing: {WAVE994_TAGS - actual_tags}", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    target_instructions = [row for row in instructions if normalize_address(row.get("target_addr", "")) == WAVE994_TARGET]
    require(any(row.get("instruction_addr") == "0x004cb924" and row.get("mnemonic") == "MOV" and row.get("operands") == "ESI, dword ptr [ESP + 0x18]" for row in target_instructions), "missing 0x004cb924 stack-argument MOV", failures)
    require(any(row.get("instruction_addr") == "0x004cba27" and row.get("mnemonic") == "RET" and row.get("operands") == "0x4" for row in target_instructions), "missing 0x004cba27 RET 0x4", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=14 found=14 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "xrefs.log": "Wrote 120 rows",
        "instructions.log": "Wrote 1130 function-body instruction rows",
        "decompile.log": "targets=14 dumped=14 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 signature_updated=1 comment_only_updated=0 tags_added=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 signature_updated=1 comment_only_updated=0 tags_added=3 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=14 found=14 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "post-xrefs.log": "Wrote 120 rows",
        "post-instructions.log": "Wrote 1130 function-body instruction rows",
        "post-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6222 commented_functions=6222",
        "queue-probe.log": "Status: PASS",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave994.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave994_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        if relative in {"apply-dry.log", "apply.log", "apply-final-dry.log"}:
            require("REPORT: Save succeeded" in text, f"missing save report in {relative}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173869959, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        PARTICLE_DOC,
        BACKLOG,
        TRACKING_STATE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-particle-manager-core-review-wave994")
        == r"py -3 tools\ghidra_particle_manager_core_review_wave994_probe.py --check",
        "missing package Wave994 script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave994-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 994 --check",
        "missing package Wave994 recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave994 particle manager core signature correction" for row in ledger_rows), "missing Wave994 ledger row", failures)
    require(any(row.get("task") == "Wave994 particle manager core signature correction" and row.get("attempt_id") == 20580 for row in attempts), "missing Wave994 attempt row", failures)


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
        print("Wave994 ParticleManager core review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave994 ParticleManager core review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
