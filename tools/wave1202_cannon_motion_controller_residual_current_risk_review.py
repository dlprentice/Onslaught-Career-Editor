#!/usr/bin/env python3
"""Validate Wave1202 cannon/motion-controller residual current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1202-cannon-motion-controller-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1202-cannon-motion-controller-residual-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1202-cannon-motion-controller-residual-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1202_cannon_motion_controller_residual_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-003050_post_wave1202_cannon_motion_controller_residual_current_risk_review_verified"

TARGETS = {
    "0x0041b450": ("CCannon__VFuncSlot_02_RemoveFromWorldAndForward", "void __fastcall CCannon__VFuncSlot_02_RemoveFromWorldAndForward(void * this)"),
    "0x0041b590": ("CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph", "int __fastcall CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph(void * this)"),
    "0x00493020": ("CMCBuggy__CMCBuggy", "void * __thiscall CMCBuggy__CMCBuggy(void * this, void * owner_model)"),
    "0x00495260": ("CMCCannon__ScalarDeletingDestructor", "void * __thiscall CMCCannon__ScalarDeletingDestructor(void * this, uint flags)"),
    "0x00495280": ("CMCCannon__Dtor", "void __thiscall CMCCannon__Dtor(void * this)"),
    "0x00495930": ("CMCComponent__Ctor", "void * __thiscall CMCComponent__Ctor(void * this, void * ownerField8)"),
    "0x00495960": ("CMCComponent__ScalarDeletingDestructor", "void * __thiscall CMCComponent__ScalarDeletingDestructor(void * this, uint flags)"),
    "0x00495980": ("CMCComponent__Dtor", "void __thiscall CMCComponent__Dtor(void * this)"),
    "0x00496090": ("CMCDropship__Ctor", "void * __thiscall CMCDropship__Ctor(void * this, void * ownerField8)"),
    "0x004960c0": ("CMCDropship__ScalarDeletingDestructor", "void * __thiscall CMCDropship__ScalarDeletingDestructor(void * this, uint flags)"),
    "0x004960e0": ("CMCDropship__Dtor", "void __thiscall CMCDropship__Dtor(void * this)"),
    "0x0049cad0": ("CMCTentacle__Constructor", "void * __thiscall CMCTentacle__Constructor(void * this, void * owner_tentacle)"),
    "0x0049ef80": ("CMCWarspiteDome__Constructor", "void * __thiscall CMCWarspiteDome__Constructor(void * this, void * owner_dome)"),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence"}

DOC_TOKENS = (
    "Wave1202",
    "wave1202-cannon-motion-controller-residual-current-risk-review",
    "13 cannon/motion-controller current-risk rows",
    "1055/1179 = 89.48%",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "remaining active focused work: 124",
    "legacy additive counter is deprecated",
    "1086/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no rename",
    "no signature change",
    "no comment change",
    "no tag change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "CCannon__VFuncSlot_02_RemoveFromWorldAndForward",
    "CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph",
    "CMCBuggy__CMCBuggy",
    "CMCCannon__Dtor",
    "CMCComponent__Ctor",
    "CMCDropship__Ctor",
    "CMCTentacle__Constructor",
    "CMCWarspiteDome__Constructor",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "20 xref rows",
    "140 instruction rows",
    "13 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime cannon behavior proven",
    "runtime motion-controller behavior proven",
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
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 20,
        "pre-instructions.tsv": 140,
        "pre-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require(comment.strip(), f"empty comment at {address}", failures)
            require("runtime" in comment.lower() or "rebuild parity" in comment.lower(), f"missing runtime/rebuild boundary at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"tags missing at {address}: {COMMON_TAGS - actual}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_targets = {normalize_address(row["target_addr"]) for row in xrefs}
    for address in TARGETS:
        require(address in xref_targets, f"missing xref coverage for {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=13 found=13 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "pre-xrefs.log": "Wrote 20 rows",
        "pre-instructions.log": "Wrote 140 function-body instruction rows",
        "pre-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

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
    require(current.get("focusedReviewed") == 1055, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "89.48%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 124, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 1086, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1055, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "89.48%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 124, "ledger remaining mismatch", failures)
    require(ledger.get("countedRowsThroughWave1202") == 1081, "ledger counted row mismatch", failures)

    prose_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1202 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1202-cannon-motion-controller-residual-current-risk-review")
        == r"py -3 tools\wave1202_cannon_motion_controller_residual_current_risk_review.py --check",
        "missing package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    task = "Wave1202 cannon motion-controller residual current-risk review"
    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1202 ledger row", failures)
    require(any(row.get("task") == task and row.get("result") == "success" for row in attempt_rows), "missing Wave1202 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1202 cannon/motion-controller residual current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1202 cannon/motion-controller residual current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
