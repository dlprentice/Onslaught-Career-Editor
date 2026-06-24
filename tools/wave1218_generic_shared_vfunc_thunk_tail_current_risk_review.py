#!/usr/bin/env python3
"""Validate Wave1218 generic/shared vfunc-thunk tail current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1218-generic-shared-vfunc-thunk-tail-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1218-generic-shared-vfunc-thunk-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1218-generic-shared-vfunc-thunk-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEP_COMMON_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPCommon.cpp" / "_index.md"
FEP_MULTI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMultiplayerStart.cpp" / "_index.md"
GROUNDUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GroundUnit.cpp" / "_index.md"
DEBRIS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "debris.cpp" / "_index.md"
RTCUTSCENE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "RTCutscene.cpp" / "_index.md"
SQUAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified"

TARGETS = {
    "0x00405db0": (
        "VFuncSlot_12_00405db0",
        "void __thiscall VFuncSlot_12_00405db0(void * this, void * arg1, void * arg2)",
        ("RET", "0x8", "no observed body-side state change"),
    ),
    "0x00441370": (
        "CDebris__GetClassId",
        "int __cdecl CDebris__GetClassId(void)",
        ("0x1f", "class/OID id"),
    ),
    "0x0044b290": (
        "CFlexArray__Free_thunk",
        "void __fastcall CFlexArray__Free_thunk(void * this)",
        ("thunk", "CFlexArray__Free"),
    ),
    "0x00452da0": (
        "SharedVFunc__NoOp_Ret08",
        "void __stdcall SharedVFunc__NoOp_Ret08(int unused0, int unused1)",
        ("RET", "0x8", "shared vtable target"),
    ),
    "0x00466290": (
        "CWaitingThread__dtor_thunk",
        "void __thiscall CWaitingThread__dtor_thunk(void * this)",
        ("JMP", "0x00528bf0", "CWaitingThread"),
    ),
    "0x0049fc10": (
        "SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10",
        "void __fastcall SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10(void * this)",
        ("vtable-slot-66", "vertical drift", "pickup"),
    ),
    "0x004d6b20": (
        "SharedVFunc__ReturnZero_004d6b20",
        "int __thiscall SharedVFunc__ReturnZero_004d6b20(void * this)",
        ("returns 0", "broad xref set"),
    ),
    "0x004e66d0": (
        "SharedVFunc__ForwardProcessNoOp",
        "void __thiscall SharedVFunc__ForwardProcessNoOp(void * this, void * process_arg)",
        ("stale-owner", "CWaypoint", "process_arg"),
    ),
}

DOC_TOKENS = (
    "Wave1218",
    "wave1218-generic-shared-vfunc-thunk-tail-current-risk-review",
    "8 generic/shared vfunc-thunk tail current-risk rows",
    "1163/1179 = 98.64%",
    "remaining active focused work: 16",
    "1194/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1117",
    "live regenerated current focused candidates: 1117",
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
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "143 xref rows",
    "122 instruction rows",
    "8 decompile rows",
    "VFuncSlot_12_00405db0",
    "CDebris__GetClassId",
    "CFlexArray__Free_thunk",
    "SharedVFunc__NoOp_Ret08",
    "CWaitingThread__dtor_thunk",
    "SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10",
    "SharedVFunc__ReturnZero_004d6b20",
    "SharedVFunc__ForwardProcessNoOp",
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
    FEP_COMMON_DOC: ("Wave1218", "SharedVFunc__NoOp_Ret08", BACKUP),
    FEP_MULTI_DOC: ("Wave1218", "CWaitingThread__dtor_thunk", BACKUP),
    GROUNDUNIT_DOC: ("Wave1218", "SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10", BACKUP),
    DEBRIS_DOC: ("Wave1218", "CDebris__GetClassId", BACKUP),
    RTCUTSCENE_DOC: ("Wave1218", "SharedVFunc__ReturnZero_004d6b20", BACKUP),
    SQUAD_DOC: ("Wave1218", "SharedVFunc__ForwardProcessNoOp", BACKUP),
    FUNCTION_INDEX: ("Wave1218", "VFuncSlot_12_00405db0", "CFlexArray__Free_thunk", BACKUP),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime threading behavior proven",
    "runtime pickup behavior proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 143,
        "pre-instructions.tsv": 122,
        "pre-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    evidence_text = (
        read_text(BASE / "pre-metadata.tsv")
        + read_text(BASE / "pre-tags.tsv")
        + read_text(BASE / "pre-xrefs.tsv")
        + read_text(BASE / "pre-instructions.tsv")
        + "".join(read_text(path) for path in sorted((BASE / "pre-decompile").glob("*.c")))
    )

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("rebuild parity remain" in row.get("comment", ""), f"boundary missing at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        for token in tokens:
            require(contains_token(evidence_text, token), f"missing evidence token for {address}: {token}", failures)

    logs = {
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "rows=8 missing=0",
        "pre-xrefs.log": "Wrote 143 rows",
        "pre-instructions.log": "Wrote 122 function-body instruction rows",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
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
    require(current.get("focusedReviewed") == 1163, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "98.64%", "progress percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 16, "progress remaining mismatch", failures)
    require(current.get("latestReviewTag") == "wave1218-generic-shared-vfunc-thunk-tail-current-risk-review", "latest review tag mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1163, "ledger reviewed mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "98.64%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 16, "ledger remaining mismatch", failures)
    require(ledger.get("latestWaveTag") == "wave1218-generic-shared-vfunc-thunk-tail-current-risk-review", "ledger latest tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        LEDGER,
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
        package.get("scripts", {}).get("test:wave1218-generic-shared-vfunc-thunk-tail-current-risk-review")
        == r"py -3 tools\wave1218_generic_shared_vfunc_thunk_tail_current_risk_review.py --check",
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
        print("Wave1218 generic/shared vfunc-thunk tail current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1218 generic/shared vfunc-thunk tail current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
