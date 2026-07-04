#!/usr/bin/env python3
"""Validate Wave1208 CBoolDataType current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1208-cbooldatatype-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1208-cbooldatatype-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1208-cbooldatatype-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1208_cbooldatatype_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
DATATYPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DataType.cpp.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
CURRENT_CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified"

TARGETS = {
    "0x0052e420": ("CBoolDataType__Equals", "bool __thiscall CBoolDataType__Equals(void * this, void * rhs)"),
    "0x0052e440": ("CBoolDataType__NotEquals", "bool __thiscall CBoolDataType__NotEquals(void * this, void * rhs)"),
    "0x0052e460": ("CBoolDataType__Assign", "void __thiscall CBoolDataType__Assign(void * this, void * rhs)"),
}

TARGET_XREFS = {
    "0x0052e420": "0x005e4d68",
    "0x0052e440": "0x005e4d6c",
    "0x0052e460": "0x005e4d64",
}

TAG_TOKENS = {
    "bool-datatype",
    "comment-hardened",
    "datatype",
    "mission-script",
    "retail-binary-evidence",
    "script-opcode-bool-head-wave574",
    "semantic-rename",
    "signature-corrected",
    "static-reaudit",
    "vtable-slot",
}

COMMENT_TOKENS = {
    "0x0052e420": ("Wave574 semantic rename", "0x005e4d68", "slot +0x3c", "this+0x04"),
    "0x0052e440": ("Wave574 semantic rename", "0x005e4d6c", "slot +0x3c", "this+0x04"),
    "0x0052e460": ("Wave574 semantic rename", "0x005e4d64", "slot +0x3c", "this+0x04"),
}

DECOMPILE_TOKENS = (
    "CBoolDataType__Equals",
    "CBoolDataType__NotEquals",
    "CBoolDataType__Assign",
    "+ 0x3c",
    "+ 4",
)

DOC_TOKENS = (
    "Wave1208",
    "wave1208-cbooldatatype-current-risk-review",
    "3 CBoolDataType current-risk rows",
    "1092/1179 = 92.62%",
    "remaining active focused work: 87",
    "legacy additive counter is deprecated",
    "1123/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "no rename",
    "no signature change",
    "no comment change",
    "no tag change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "CBoolDataType__Equals",
    "CBoolDataType__NotEquals",
    "CBoolDataType__Assign",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "3 xref rows",
    "99 instruction rows",
    "3 decompile rows",
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
    "runtime script behavior proven",
    "runtime missionscript behavior proven",
    "exact bool abi proven",
    "exact datatype layout proven",
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
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 99,
        "pre-decompile/index.tsv": 3,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "pre-xrefs.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("runtime" in comment.lower() and "rebuild parity" in comment.lower(), f"missing runtime/rebuild boundary at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in TAG_TOKENS:
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
            require(normalize_address(xref.get("from_addr", "")) == TARGET_XREFS[address], f"xref source mismatch at {address}", failures)
            require(xref.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)

    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "pre-decompile").glob("*.c"))
    for token in DECOMPILE_TOKENS:
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=3 found=3 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "pre-xrefs.log": "Wrote 3 rows",
        "pre-instructions.log": "Wrote 99 instruction rows",
        "pre-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 18, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress_and_docs(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1092, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "92.62%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 87, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 1123, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1208 CBoolDataType Current-Risk Review", "latest review wave mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("latestWave") == "Wave1208 CBoolDataType Current-Risk Review", "ledger latest wave mismatch", failures)
    require(ledger.get("correctedUniqueReviewed") == 1092, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "92.62%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 87, "ledger remaining mismatch", failures)
    require(ledger.get("countedRowsThroughWave1208") == 1118, "ledger counted row mismatch", failures)
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
        DATATYPE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        CURRENT_CAPABILITIES,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1208 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1208-cbooldatatype-current-risk-review")
        == r"py -3 tools\wave1208_cbooldatatype_current_risk_review.py --check",
        "missing package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    task = "Wave1208 CBoolDataType current-risk review"
    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1208 ledger row", failures)
    require(any(row.get("task") == task and row.get("result") == "success" for row in attempt_rows), "missing Wave1208 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1208 CBoolDataType current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1208 CBoolDataType current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
