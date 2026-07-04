#!/usr/bin/env python3
"""Validate Wave1198 CDXMemBuffer current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1198-cdxmembuffer-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1198-cdxmembuffer-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1198-cdxmembuffer-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1198_cdxmembuffer_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXMEMBUFFER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMemBuffer.cpp.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyCDXMemBufferCurrentRiskWave1198.java"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-214911_post_wave1198_cdxmembuffer_current_risk_review_verified"

TARGETS = {
    "0x00547d70": (
        "CDXMemBuffer__ctor",
        "void * __fastcall CDXMemBuffer__ctor(void * this)",
        ("score16 CDXMemBuffer resource-buffer constructor", "stale CChunker-owner direction", "concrete CDXMemBuffer/file/CRC layouts"),
    ),
    "0x00547ec0": (
        "CDXMemBuffer__InitFromFile",
        "bool __thiscall CDXMemBuffer__InitFromFile(void * this, char * filename, int memType, int mungePath, uint startSkip)",
        ("file-open/init helper", "filename/memType/mungePath/startSkip RET 0x10 contract", "frontend/config, texture/resource, particle, mesh"),
    ),
    "0x005482d0": (
        "CDXMemBuffer__Skip",
        "int __thiscall CDXMemBuffer__Skip(void * this, int size)",
        ("skip helper", "RET 0x4 size argument", "skipped byte count"),
    ),
    "0x00548570": (
        "CDXMemBuffer__Read",
        "int __thiscall CDXMemBuffer__Read(void * this, void * data, int size)",
        ("read helper", "data/size RET 0x8 contract", "short-read/EOF behavior"),
    ),
    "0x00548c00": (
        "CDXMemBuffer__Close",
        "bool __fastcall CDXMemBuffer__Close(void * this)",
        ("close helper", "split read/write cleanup contract", "flushes buffered bytes and CRC side data"),
    ),
    "0x004cdb90": (
        "CDXMemBuffer__dtor_base_Thunk",
        "void __fastcall CDXMemBuffer__dtor_base_Thunk(void)",
        ("destructor thunk", "ParticleSet.cpp unwind cleanup", "single-instruction jump thunk"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1198-cdxmembuffer-current-risk-review",
    "wave1198-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "score15-16",
    "cdxmembuffer-resource-buffer",
    "resource-buffer",
    "source-identity-deferred",
    "exact-layout-deferred",
    "runtime-behavior-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "signature-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1198",
    "wave1198-cdxmembuffer-current-risk-review",
    "6 CDXMemBuffer resource-buffer score15-16 current-risk rows",
    "860/1179 = 72.94%",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "remaining active focused work: 319",
    "legacy additive counter is deprecated",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=6 skipped=0",
    "comment_only_updated=6",
    "tags_added=92",
    "final dry updated=0 skipped=6",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "CDXMemBuffer__ctor",
    "CDXMemBuffer__InitFromFile",
    "CDXMemBuffer__Skip",
    "CDXMemBuffer__Read",
    "CDXMemBuffer__Close",
    "CDXMemBuffer__dtor_base_Thunk",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "709 xref rows",
    "919 instruction rows",
    "6 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

ACCOUNTING_TOKENS = (
    "Wave1198",
    "wave1198-cdxmembuffer-current-risk-review",
    "860/1179 = 72.94%",
    "remaining active focused work: 319",
    "legacy additive counter is deprecated",
    "891/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime io behavior proven",
    "exact layout proven",
    "exact source identity proven",
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
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 709,
        "pre-instructions.tsv": 919,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 709,
        "post-instructions.tsv": 919,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in (
                "Wave1198 static current-risk read-back",
                "Static rebuild contract only",
                "clean-room/no-noticeable-difference parity remain separate proof",
            ):
                require(token in comment, f"missing common comment token at {address}: {token}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}: {COMMON_TAGS - actual}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 709 rows",
        "post-instructions.log": "Wrote 919 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_BAD", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176393095 or backup.get("totalBytes") == 176393095.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress_and_docs(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("accountingMode") == "unique-address-ledger", "accounting mode mismatch", failures)
    require(current.get("focusedReviewed") == 860, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "72.94%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 319, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 891, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 860, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "72.94%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 319, "ledger remaining mismatch", failures)
    require(ledger.get("duplicateAddressOvercount") == 26, "ledger duplicate mismatch", failures)
    require(ledger.get("wave1145ArithmeticOvercount") == 5, "ledger Wave1145 mismatch", failures)
    require(ledger.get("countedRowsThroughWave1198") == 886, "ledger counted row mismatch", failures)

    prose_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        DXMEMBUFFER_DOC,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    accounting_docs = [PROGRESS, LEDGER, ACCOUNTING]
    for path in accounting_docs:
        text = read_text(path)
        for token in ACCOUNTING_TOKENS:
            require(contains_token(text, token), f"missing accounting token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1198 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1198-cdxmembuffer-current-risk-review")
        == r"py -3 tools\wave1198_cdxmembuffer_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Ghidra apply script", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == "Wave1198 CDXMemBuffer current-risk review" for row in ledger_rows), "missing Wave1198 ledger row", failures)
    require(any(row.get("task") == "Wave1198 CDXMemBuffer current-risk review" and row.get("result") == "success" for row in attempt_rows), "missing Wave1198 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1198 CDXMemBuffer current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1198 CDXMemBuffer current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
