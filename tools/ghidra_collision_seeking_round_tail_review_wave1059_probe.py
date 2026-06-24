#!/usr/bin/env python3
"""Validate Wave1059 collision-seeking round tail review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1059-collision-seeking-round-tail-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_collision_seeking_round_tail_review_wave1059_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1059_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
COLLISION_ROUND_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CollisionSeekingRound.cpp" / "_index.md"
COLLISION_THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "collisionseekingthing.cpp.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified"

TARGETS = {
    "0x00425b50": ("CCollisionSeekingRound__InitCollisionLineAndSound", "void __thiscall CCollisionSeekingRound__InitCollisionLineAndSound(void * this, void * roundConfig)"),
    "0x00425e30": ("CCollisionSeekingRound__UpdatePrimarySeekerLeadVector", "void * __fastcall CCollisionSeekingRound__UpdatePrimarySeekerLeadVector(void * this)"),
    "0x00426300": ("CMeshCollisionVolume__ScalarDeletingDestructor_00426300", "void * __thiscall CMeshCollisionVolume__ScalarDeletingDestructor_00426300(void * this, int deleteFlags)"),
    "0x00426370": ("CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset", "void __thiscall CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset(void * this, void * newSeeker)"),
    "0x004263f0": ("CCollisionSeekingRound__Destructor", "void __fastcall CCollisionSeekingRound__Destructor(void * this)"),
    "0x00426460": ("CCollisionSeekingRound__ScalarDeletingDestructor", "void * __thiscall CCollisionSeekingRound__ScalarDeletingDestructor(void * this, int deleteFlags)"),
    "0x00426480": ("CCollisionSeekingRound__SetCollisionMask", "void __thiscall CCollisionSeekingRound__SetCollisionMask(void * this, int collisionMask)"),
    "0x004264a0": ("CCollisionSeekingRound__ResolveRoundCollisionResponse", "void __thiscall CCollisionSeekingRound__ResolveRoundCollisionResponse(void * this, void * otherRound)"),
}

CONTEXT_TARGETS = {
    "0x00425a10": ("CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags", "bool __thiscall CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags(void * this, void * candidateRound)"),
    "0x00425c60": ("CCollisionSeekingRound__FilterCollisionCandidateByTrajectory", "bool __thiscall CCollisionSeekingRound__FilterCollisionCandidateByTrajectory(void * this, void * candidateRound)"),
    "0x00426900": ("CCollisionSeekingRound__CheckCollisionFlags", "bool __thiscall CCollisionSeekingRound__CheckCollisionFlags(void * this, void * candidateRound)"),
    "0x00426920": ("CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance", "int __thiscall CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance(void * this, void * packedCell)"),
    "0x00426a00": ("CCollisionSeekingRound__ProcessMapWhoCollisionSweep", "void __thiscall CCollisionSeekingRound__ProcessMapWhoCollisionSweep(void * this, void * startOrContext, void * endOrContext)"),
    "0x00426a20": ("CCollisionSeekingRound__MarkDelayedCollisionReady", "void __thiscall CCollisionSeekingRound__MarkDelayedCollisionReady(void * this, void * event)"),
}

COMMON_TAGS = {
    "static-reaudit",
    "collision-seeking-round-tail-review-wave1059",
    "wave1059-readback-verified",
    "retail-binary-evidence",
    "tag-normalized",
    "comment-hardened",
}

EXTRA_TAGS = {
    "0x00425b50": {"collision-seeking-round", "line-helper", "init-with-sound", "vtable-slot"},
    "0x00425e30": {"collision-seeking-round", "primary-seeker", "lead-vector", "vtable-slot"},
    "0x00426300": {"mesh-collision-volume", "scalar-deleting-destructor", "collision-helper"},
    "0x00426370": {"collision-seeking-round", "primary-seeker", "helper-replacement", "owner-relative-offset"},
    "0x004263f0": {"collision-seeking-round", "destructor", "monitor-shutdown"},
    "0x00426460": {"collision-seeking-round", "scalar-deleting-destructor", "destructor-wrapper"},
    "0x00426480": {"collision-seeking-round", "collision-mask", "explicit-mask-flag"},
    "0x004264a0": {"collision-seeking-round", "collision-response", "delayed-ready-flag", "peer-collision"},
    "0x00425a10": {"infantry-bloke", "collision-filter", "mount-state", "collision-seeking-context"},
    "0x00425c60": {"collision-seeking-round", "trajectory-filter", "collision-filter"},
    "0x00426900": {"collision-seeking-round", "collision-mask", "flag-filter"},
    "0x00426920": {"collision-seeking-round", "mapwho-distance", "chebyshev-distance"},
    "0x00426a00": {"collision-seeking-round", "mapwho-sweep", "hlcollisiondetector-bridge"},
    "0x00426a20": {"collision-seeking-round", "delayed-ready-flag", "event-callback"},
}

DOC_TOKENS = (
    "Wave1059",
    "collision-seeking-round-tail-review-wave1059",
    "0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound",
    "0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector",
    "0x00426300 CMeshCollisionVolume__ScalarDeletingDestructor_00426300",
    "0x00426370 CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset",
    "0x004263f0 CCollisionSeekingRound__Destructor",
    "0x00426480 CCollisionSeekingRound__SetCollisionMask",
    "0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse",
    "0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady",
    "812/1408 = 57.67%",
    "1140/1509 = 75.55%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "tag normalization",
)

OVERCLAIM_TOKENS = (
    "runtime projectile behavior proven",
    "runtime collision behavior proven",
    "fully reverse-engineered runtime",
    "rebuild parity proven",
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


def rows_by_address(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row[key]): row for row in read_tsv(path)}


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 26,
        "instructions.tsv": 665,
        "decompile/index.tsv": 8,
        "context-metadata.tsv": 6,
        "context-tags.tsv": 6,
        "context-xrefs.tsv": 18,
        "context-instructions.tsv": 257,
        "context-decompile/index.tsv": 6,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 26,
        "post-instructions.tsv": 665,
        "post-decompile/index.tsv": 8,
        "post-context-metadata.tsv": 6,
        "post-context-tags.tsv": 6,
        "post-context-xrefs.tsv": 18,
        "post-context-instructions.tsv": 257,
        "post-context-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = rows_by_address(BASE / "post-metadata.tsv")
    context_metadata = rows_by_address(BASE / "post-context-metadata.tsv")
    tags = rows_by_address(BASE / "post-tags.tsv")
    context_tags = rows_by_address(BASE / "post-context-tags.tsv")

    for address, (name, signature) in {**TARGETS, **CONTEXT_TARGETS}.items():
        row = metadata.get(address) or context_metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)

        tag_row = tags.get(address) or context_tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            expected = COMMON_TAGS | EXTRA_TAGS[address]
            require(expected.issubset(actual), f"missing tags at {address}: {sorted(expected - actual)}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 tags_added=131 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=14 skipped=0 tags_added=131 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=14 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 26 rows",
        "post-instructions.log": "Wrote 665 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-context-metadata.log": "targets=6 found=6 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-context-xrefs.log": "Wrote 18 rows",
        "post-context-instructions.log": "Wrote 257 function-body instruction rows",
        "post-context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "VERIFY_MISSING", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6246, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless row", failures)
    require(not any(row.get("signature", "").startswith("undefined ") for row in rows), "quality TSV has undefined signature", failures)
    require(not any(re.search(r"\bparam_\d+\b", row.get("signature", "")) for row in rows), "quality TSV has param_N signature", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174689159 or backup.get("totalBytes") == 174689159.0, "backup byte count mismatch", failures)
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
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        COLLISION_ROUND_INDEX: (
            "Wave1059",
            "collision-seeking-round-tail-review-wave1059",
            "0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound",
            "0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector",
            "0x004263f0 CCollisionSeekingRound__Destructor",
            "0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse",
            BACKUP_PATH,
            "tag normalization",
        ),
        COLLISION_THING_DOC: (
            "Wave1059",
            "collision-seeking-round-tail-review-wave1059",
            "0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags",
            "0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory",
            "0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady",
            BACKUP_PATH,
            "tag normalization",
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-collision-seeking-round-tail-review-wave1059")
        == r"py -3 tools\ghidra_collision_seeking_round_tail_review_wave1059_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1059-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1059 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1059 collision seeking round tail review" for row in ledger_rows), "missing Wave1059 ledger row", failures)
    require(
        any(row.get("task") == "Wave1059 collision seeking round tail review" and row.get("attempt_id") == 20641 for row in attempts),
        "missing Wave1059 attempt row",
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
        print("Wave1059 collision-seeking round tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1059 collision-seeking round tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
