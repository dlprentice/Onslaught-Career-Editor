#!/usr/bin/env python3
"""Validate Wave1212 options/detail/tweak current-risk read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1212-options-detail-tweak-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1212-options-detail-tweak-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1212-options-detail-tweak-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1212_options_detail_tweak_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FEP_OPTIONS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPOptions.cpp" / "_index.md"
CLI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CLIParams.cpp" / "_index.md"
DISPLAY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "display-settings.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-065722_post_wave1212_options_detail_tweak_current_risk_review_verified"

TARGETS = {
    "0x004ceef0": ("LandscapeDetail_SetLevel", "void __stdcall LandscapeDetail_SetLevel(int detail_level)", ("0x009c7c54", "0x009c7c56")),
    "0x004cef30": ("LandscapeDetail_GetLevel", "int __cdecl LandscapeDetail_GetLevel(void)", ("0x009c7c54", "0x009c7c56")),
    "0x004cef50": ("CTreeDetail__SetQualityLevel", "void __stdcall CTreeDetail__SetQualityLevel(int quality_level)", ("CRTMesh__SetQualityLevel", "0x004dd6b0")),
    "0x004cf030": ("CMouseSensitivityMenuItem__scalar_deleting_dtor", "void * __thiscall CMouseSensitivityMenuItem__scalar_deleting_dtor(void * this, int flags)", ("CMenuItem__Destructor_Thunk", "CDXMemoryManager__Free")),
    "0x004cf8e0": ("CMultiSample__GetSampleCountLabel", "void * __stdcall CMultiSample__GetSampleCountLabel(int available_sample_ordinal)", ("Localization__GetStringById", "0xd4")),
    "0x00527d00": ("CReconnectInterface__VFunc_07_00527d00", "void __thiscall CReconnectInterface__VFunc_07_00527d00(void * this, float tweak_value)", ("CLIParams__ParseCommandLine", "-landscape")),
    "0x00528690": ("CTweak__ctor_base", "void * __thiscall CTweak__ctor_base(void * this, void * callback_context)", ("DAT_0089c018", "global tweak list")),
    "0x005286b0": ("CTweak__dtor_base", "void __fastcall CTweak__dtor_base(void * this)", ("DAT_0089c018", "global tweak list")),
    "0x004530a0": ("CTweak__dtor_base_thunk_004530a0", "void __fastcall CTweak__dtor_base_thunk_004530a0(void * this)", ("CTweak__dtor_base", "jump thunk")),
}

TARGET_XREFS = {
    "0x004ceef0": ("004cead0", "COMPUTED_CALL"),
    "0x004cef30": ("004ceac6", "COMPUTED_CALL"),
    "0x004cef50": ("004ceb06", "COMPUTED_CALL"),
    "0x004cf030": ("005de6b8", "DATA"),
    "0x004cf8e0": ("005de258", "DATA"),
    "0x00527d00": ("00423f45", "UNCONDITIONAL_CALL"),
    "0x00528690": ("00527c99", "UNCONDITIONAL_CALL"),
    "0x005286b0": ("004530a0", "UNCONDITIONAL_JUMP"),
    "0x004530a0": ("00554f75", "UNCONDITIONAL_CALL"),
}

DOC_TOKENS = (
    "Wave1212",
    "wave1212-options-detail-tweak-current-risk-review",
    "9 options/detail/tweak current-risk rows",
    "1119/1179 = 94.91%",
    "remaining active focused work: 60",
    "1150/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1127",
    "live regenerated current focused candidates: 1127",
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
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "64 xref rows",
    "175 instruction rows",
    "9 decompile rows",
    "869 context xref rows",
    "1887 context instruction rows",
    "7 context decompile rows",
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

OWNER_DOC_TOKENS = {
    FEP_OPTIONS_DOC: ("Wave1212", "LandscapeDetail_SetLevel", "CMultiSample__GetSampleCountLabel", BACKUP),
    CLI_DOC: ("Wave1212", "CReconnectInterface__VFunc_07_00527d00", "CTweak__ctor_base", BACKUP),
    DISPLAY_DOC: ("Wave1212", "LandscapeDetail_GetLevel", "CTreeDetail__SetQualityLevel", BACKUP),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime options behavior proven",
    "runtime device behavior proven",
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
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 64,
        "pre-instructions.tsv": 175,
        "pre-decompile/index.tsv": 9,
        "context-metadata.tsv": 7,
        "context-tags.tsv": 7,
        "context-xrefs.tsv": 869,
        "context-instructions.tsv": 1887,
        "context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    evidence_text = (
        read_text(BASE / "pre-metadata.tsv")
        + read_text(BASE / "pre-instructions.tsv")
        + read_text(BASE / "context-metadata.tsv")
        + read_text(BASE / "context-instructions.tsv")
    )

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Static", "evidence only"):
                require(token in row.get("comment", ""), f"missing bounded comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag at {address}", failures)

        from_addr, ref_type = TARGET_XREFS[address]
        require(
            any(normalize_address(row.get("target_addr", "")) == address and row.get("from_addr") == from_addr and row.get("ref_type") == ref_type for row in xrefs),
            f"missing xref {from_addr} {ref_type} for {address}",
            failures,
        )
        for token in tokens:
            require(contains_token(evidence_text, token), f"missing evidence token for {address}: {token}", failures)

    logs = {
        "pre-metadata.log": "targets=9 found=9 missing=0",
        "pre-tags.log": "rows=9 missing=0",
        "pre-xrefs.log": "Wrote 64 rows",
        "pre-instructions.log": "Wrote 175 function-body instruction rows",
        "pre-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "context-metadata.log": "targets=7 found=7 missing=0",
        "context-tags.log": "rows=7 missing=0",
        "context-xrefs.log": "Wrote 869 rows",
        "context-instructions.log": "Wrote 1887 function-body instruction rows",
        "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING", "FAIL", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_backup_and_progress(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1119, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "94.91%", "progress percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 60, "progress remaining mismatch", failures)
    require(current.get("latestReviewTag") == "wave1212-options-detail-tweak-current-risk-review", "latest review tag mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1119, "ledger reviewed mismatch", failures)
    require(ledger.get("remainingUnique") == 60, "ledger remaining mismatch", failures)
    require(ledger.get("latestWaveTag") == "wave1212-options-detail-tweak-current-risk-review", "ledger latest tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        RANK,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave note mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1212-options-detail-tweak-current-risk-review")
        == r"py -3 tools\wave1212_options_detail_tweak_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_backup_and_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1212 options/detail/tweak current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1212 options/detail/tweak current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
