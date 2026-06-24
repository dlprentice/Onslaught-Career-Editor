#!/usr/bin/env python3
"""Validate Wave1197 FEPBEConfig/frontend residual artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1197-fepbeconfig-frontend-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1197-fepbeconfig-frontend-residual-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1197-fepbeconfig-frontend-residual-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1197_fepbeconfig_frontend_residual_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FEPBECONFIG_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPBEConfig.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyFEPBEConfigFrontendResidualWave1197.java"

BACKUP = r"G:\GhidraBackups\BEA_20260606-211310_post_wave1197_fepbeconfig_frontend_residual_current_risk_review_verified"

TARGETS = {
    "0x0044fa90": (
        "CFEPBEConfig__Init",
        "void __thiscall CFEPBEConfig__Init(void * this)",
        ("data\\\\WorldHeaders.dat", "beconf::init() 0-5", "0x005dba3c", "0x0044fa90", "0x0044fa93"),
    ),
    "0x0044eb30": (
        "CFEPMultiplayerStart__SetConfigDescriptionByIndex",
        "void __cdecl CFEPMultiplayerStart__SetConfigDescriptionByIndex(int config_index)",
        ("Unknown Configuration", "DAT_0089d94c", "DAT_006602a0", "0x0051efa8"),
    ),
    "0x0044f530": (
        "CFEPBEConfig__PlayWeaponSound",
        "void __cdecl CFEPBEConfig__PlayWeaponSound(void * config, int weapon_index)",
        ("Unknown Weapon", "DAT_008553e8", "+0x40/+0x48", "0x00451044"),
    ),
    "0x0044f830": (
        "CFEPBEConfig__PlayWeaponSoundAlt",
        "void __cdecl CFEPBEConfig__PlayWeaponSoundAlt(void * config, int weapon_index)",
        ("Unknown Weapon", "+0x50/+0x58", "DAT_008553e8", "0x0045117f"),
    ),
}

EXPECTED_XREFS = {
    "0x0044fa90": ("0x005dba3c", "DATA"),
    "0x0044eb30": ("0x0051efa8", "UNCONDITIONAL_CALL"),
    "0x0044f530": ("0x00451044", "UNCONDITIONAL_CALL"),
    "0x0044f830": ("0x0045117f", "UNCONDITIONAL_CALL"),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1197-fepbeconfig-frontend-residual-current-risk-review",
    "wave1197-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "score15-16",
    "fepbeconfig-frontend-residual",
    "frontend",
    "source-identity-deferred",
    "exact-layout-deferred",
    "runtime-behavior-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1197",
    "wave1197-fepbeconfig-frontend-residual-current-risk-review",
    "885/1179 = 75.06%",
    "4 FEPBEConfig/frontend residual score15-16 current-risk rows",
    "current focused candidates: 1142",
    "live regenerated current focused candidates: 1142",
    "remaining active focused work: 294",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=4 skipped=0",
    "comment_only_updated=4",
    "tags_added=52",
    "final dry updated=0 skipped=4",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "CFEPBEConfig__Init",
    "CFEPMultiplayerStart__SetConfigDescriptionByIndex",
    "CFEPBEConfig__PlayWeaponSound",
    "CFEPBEConfig__PlayWeaponSoundAlt",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "4 xref rows",
    "860 instruction rows",
    "4 decompile rows",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
    "rebuild-grade specification",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime frontend behavior proven",
    "runtime frontend/config loading behavior proven",
    "runtime frontend audio/text behavior proven",
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
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 4,
        "pre-instructions.tsv": 860,
        "pre-decompile/index.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 4,
        "post-instructions.tsv": 860,
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
            for token in (
                "Wave1197 static current-risk read-back",
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

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref for {address}", failures)
        if xref is not None:
            expected_from, expected_type = EXPECTED_XREFS[address]
            require(normalize_address(xref.get("from_addr", "")) == expected_from, f"xref source mismatch at {address}", failures)
            require(xref.get("ref_type") == expected_type, f"xref type mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 4 rows",
        "post-instructions.log": "Wrote 860 function-body instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "Input file not found", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply save report missing", failures)


def check_progress_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 885, "focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "75.06%", "focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 294, "remaining focused mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1142, "live focused mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "risk candidate mismatch", failures)
    require(progress["latestWave"]["tag"] == "wave1197-fepbeconfig-frontend-residual-current-risk-review", "latest progress wave mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176360327 or backup.get("totalBytes") == 176360327.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1197 note mirror mismatch", failures)
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        GHIDRA_REFERENCE,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BINARY_INDEX,
        RE_INDEX,
        FEPBECONFIG_DOC,
        BACKLOG,
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

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1197-fepbeconfig-frontend-residual-current-risk-review")
        == r"py -3 tools\wave1197_fepbeconfig_frontend_residual_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1197 apply script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == "Wave1197 FEPBEConfig frontend residual current-risk review" for row in ledger_rows), "missing Wave1197 ledger row", failures)
    require(any(row.get("task") == "Wave1197 FEPBEConfig frontend residual current-risk review" and row.get("attempt_id") == 20688 for row in attempt_rows), "missing Wave1197 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_progress_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1197 FEPBEConfig/frontend residual probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1197 FEPBEConfig/frontend residual probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
