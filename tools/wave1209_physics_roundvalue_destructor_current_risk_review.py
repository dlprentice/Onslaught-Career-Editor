#!/usr/bin/env python3
"""Validate Wave1209 PhysicsScript round-value destructor current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1209-physics-roundvalue-destructor-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1209-physics-roundvalue-destructor-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1209-physics-roundvalue-destructor-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1209_physics_roundvalue_destructor_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CURRENT_CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-044807_post_wave1209_physics_roundvalue_destructor_current_risk_review_verified"

TARGETS = {
    "0x004395b0": (
        "CRoundSeek__scalar_deleting_dtor",
        "void * __thiscall CRoundSeek__scalar_deleting_dtor(void * this, int flags)",
        ("Wave1209 static correction", "CDXMemoryManager__Free(&DAT_009c3df0, this)", "0x00549220", "not OID__FreeObject", "0x005da534"),
    ),
    "0x004395d0": (
        "CRoundSeek__dtor_base",
        "void __fastcall CRoundSeek__dtor_base(void * this)",
        ("Wave1209 static read-back", "this+0x8", "0x005da534", "0x005da584", "SEH frame"),
    ),
    "0x00439ad0": (
        "CRoundTreeCollision__scalar_deleting_dtor",
        "void * __thiscall CRoundTreeCollision__scalar_deleting_dtor(void * this, int flags)",
        ("Wave1209 static correction", "CDXMemoryManager__Free(&DAT_009c3df0, this)", "0x00549220", "not OID__FreeObject", "0x005da2dc"),
    ),
    "0x00439af0": (
        "CRoundTreeCollision__dtor_base",
        "void __fastcall CRoundTreeCollision__dtor_base(void * this)",
        ("Wave1209 static read-back", "this+0x8", "0x005da2dc", "0x005da584", "SEH frame"),
    ),
}

TARGET_XREFS = {
    "0x004395b0": ("0x005da534", "DATA"),
    "0x004395d0": ("0x004395b3", "UNCONDITIONAL_CALL"),
    "0x00439ad0": ("0x005da2dc", "DATA"),
    "0x00439af0": ("0x00439ad3", "UNCONDITIONAL_CALL"),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1209-physics-roundvalue-destructor-current-risk-review",
    "wave1209-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "physics-script",
    "round-value-tail",
    "nested-round-value",
    "destructor",
    "rebuild-grade-static-contract",
}

EXTRA_TAGS = {
    "0x004395b0": {"scalar-deleting-destructor", "memory-manager-free", "comment-corrected", "round-seek"},
    "0x004395d0": {"destructor-body", "owned-child-lifetime", "round-seek"},
    "0x00439ad0": {"scalar-deleting-destructor", "memory-manager-free", "comment-corrected", "round-tree-collision"},
    "0x00439af0": {"destructor-body", "owned-child-lifetime", "round-tree-collision"},
}

DOC_TOKENS = (
    "Wave1209",
    "wave1209-physics-roundvalue-destructor-current-risk-review",
    "4 PhysicsScript round-value destructor current-risk rows",
    "1096/1179 = 92.96%",
    "remaining active focused work: 83",
    "legacy additive counter is deprecated",
    "1127/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=4 skipped=0",
    "comment_only_updated=4",
    "tags_added=34",
    "final dry updated=0 skipped=4",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "CDXMemoryManager__Free(&DAT_009c3df0, this)",
    "not OID__FreeObject",
    "CRoundSeek__scalar_deleting_dtor",
    "CRoundSeek__dtor_base",
    "CRoundTreeCollision__scalar_deleting_dtor",
    "CRoundTreeCollision__dtor_base",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "4 xref rows",
    "68 instruction rows",
    "4 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "static-reaudit-measurement-register.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime physics-script behavior proven",
    "runtime projectile collision behavior proven",
    "exact physicscript round-value layouts proven",
    "exact source destructor identity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
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


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 4,
        "pre-instructions.tsv": 68,
        "pre-decompile/index.tsv": 4,
        "context-metadata.tsv": 6,
        "context-tags.tsv": 6,
        "context-xrefs.tsv": 43,
        "context-instructions.tsv": 177,
        "context-decompile/index.tsv": 6,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 4,
        "post-instructions.tsv": 68,
        "post-decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("runtime" in comment.lower() and "rebuild parity" in comment.lower(), f"missing runtime/rebuild boundary at {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in COMMON_TAGS | EXTRA_TAGS[address]:
                require(token in actual, f"missing tag at {address}: {token}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref for {address}", failures)
        if xref is not None:
            expected_from, expected_type = TARGET_XREFS[address]
            require(normalize_address(xref.get("from_addr", "")) == expected_from, f"xref source mismatch at {address}", failures)
            require(xref.get("ref_type") == expected_type, f"xref type mismatch at {address}", failures)

    instructions = read_text(BASE / "post-instructions.tsv")
    for token in ("0x00549220", "0x9c3df0", "CALL\tdword ptr [EAX]"):
        require(token in instructions, f"missing instruction token: {token}", failures)

    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "post-decompile").glob("*.c"))
    for token in ("CDXMemoryManager__Free(&DAT_009c3df0,this)", "CRoundSeek__dtor_base", "CRoundTreeCollision__dtor_base", "0x005da584"):
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=4 found=4 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "pre-xrefs.log": "Wrote 4 rows",
        "pre-instructions.log": "Wrote 68 function-body instruction rows",
        "pre-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "context-metadata.log": "targets=6 found=6 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "context-xrefs.log": "Wrote 43 rows",
        "context-instructions.log": "Wrote 177 function-body instruction rows",
        "context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=34 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=34 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 4 rows",
        "post-instructions.log": "Wrote 68 function-body instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply save marker missing", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress_and_docs(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1096, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "92.96%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 83, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 1127, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1209 PhysicsScript Round-Value Destructor Current-Risk Review", "latest review wave mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("latestWave") == "Wave1209 PhysicsScript Round-Value Destructor Current-Risk Review", "ledger latest wave mismatch", failures)
    require(ledger.get("correctedUniqueReviewed") == 1096, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "92.96%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 83, "ledger remaining mismatch", failures)
    require(ledger.get("countedRowsThroughWave1209") == 1122, "ledger counted row mismatch", failures)
    require(ledger.get("duplicateAddressOvercount") == 26, "ledger duplicate mismatch", failures)

    prose_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        PHYSICS_DOC,
        FUNCTION_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        CURRENT_CAPABILITIES,
        AGENTS,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1209 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1209-physics-roundvalue-destructor-current-risk-review")
        == r"py -3 tools\wave1209_physics_roundvalue_destructor_current_risk_review.py --check",
        "missing package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    task = "Wave1209 PhysicsScript round-value destructor current-risk review"
    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1209 ledger row", failures)
    require(any(row.get("task") == task and row.get("result") == "success" for row in attempt_rows), "missing Wave1209 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1209 PhysicsScript round-value destructor current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1209 PhysicsScript round-value destructor current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
