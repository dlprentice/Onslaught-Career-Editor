#!/usr/bin/env python3
"""Validate Wave1184 AirUnit/Plane residual current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1184-airunit-plane-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1184-airunit-plane-residual-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1184-airunit-plane-residual-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1184_airunit_plane_residual_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
AIRUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "_index.md"
PLANE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Plane.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-131434_post_wave1184_airunit_plane_residual_current_risk_review_verified"

TARGETS = {
    "0x00403730": (
        "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
        "void __thiscall CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport(void * this)",
        {
            ("0x004d20a3", "UNCONDITIONAL_CALL"),
            ("0x005e2148", "DATA"),
            ("0x005e0e9c", "DATA"),
            ("0x005e0540", "DATA"),
            ("0x005e3634", "DATA"),
            ("0x005e3888", "DATA"),
        },
    ),
    "0x00403a50": (
        "CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear",
        "int __thiscall CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear(void * this)",
        {
            ("0x005e2ff4", "DATA"),
            ("0x005e2da0", "DATA"),
            ("0x005e220c", "DATA"),
            ("0x005e1b04", "DATA"),
            ("0x005e1410", "DATA"),
            ("0x005e0f60", "DATA"),
            ("0x005e0604", "DATA"),
            ("0x005e36f8", "DATA"),
            ("0x005e394c", "DATA"),
            ("0x0044814a", "UNCONDITIONAL_CALL"),
        },
    ),
    "0x004d20a0": (
        "CPlane__VFunc_68_CrashIfNoAirSupport",
        "void __thiscall CPlane__VFunc_68_CrashIfNoAirSupport(void * this)",
        {
            ("0x005e2f30", "DATA"),
            ("0x005e2cdc", "DATA"),
            ("0x005e1a40", "DATA"),
            ("0x005e134c", "DATA"),
        },
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "retail-binary-evidence",
    "air-unit-crash-support-vfunc-review-wave1006",
    "wave1006-readback-verified",
    "comment-normalized",
    "tag-normalized",
    "vtable-slot-evidence",
}

DOC_TOKENS = (
    "Wave1184",
    "wave1184-airunit-plane-residual-current-risk-review",
    "782/1179 = 66.33%",
    "3 AirUnit/Plane support-gate residual current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 397",
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
    "both consults converged on exact three-row AirUnit/Plane residual slice",
    "root rejected duplicate Wave1123 slot-69 rows",
    "CAirUnit__Init deferred to separate lifecycle/init residual pass",
    "no Cursor/Composer",
    "Wave1006 provenance",
    "air-unit support gate",
    "plane-family slot 68",
    "shared slot 117 predicate",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "20 xref rows",
    "51 instruction rows",
    "3 decompile rows",
    "0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
    "0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear",
    "0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime aircraft crash behavior proven",
    "runtime support-gate behavior proven",
    "runtime position-delta behavior proven",
    "exact source virtual names proven",
    "concrete cunit/airunit/cplane layouts proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "post-metadata.tsv": 3,
        "post-tags.tsv": 3,
        "post-xrefs.tsv": 20,
        "post-instructions.tsv": 51,
        "post-decompile/index.tsv": 3,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs_by_target: dict[str, set[tuple[str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs_by_target.setdefault(normalize(row["target_addr"]), set()).add((normalize(row["from_addr"]), row.get("ref_type", "")))

    for address, (name, signature, expected_xrefs) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave1006 static re-audit metadata normalization", "Static retail Ghidra metadata/xref/decompile/vtable evidence only"):
                require(token in comment, f"missing comment token {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        normalized_expected = {(normalize(addr), typ) for addr, typ in expected_xrefs}
        require(xrefs_by_target.get(address, set()) == normalized_expected, f"xref set mismatch {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "post-metadata.log": "targets=3 found=3 missing=0",
        "post-tags.log": "rows=3 missing=0",
        "post-xrefs.log": "Wrote 20 rows",
        "post-instructions.log": "Wrote 51 function-body instruction rows",
        "post-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176098183, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1184 AirUnit/Plane Residual Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1184-airunit-plane-residual-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    artifact_commit = str(latest.get("artifactCommit", ""))
    require(artifact_commit == "pending Wave1184 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", artifact_commit)), "latest artifact commit mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 782, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "66.33%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 397, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1184-airunit-plane-residual-current-risk-review", "latest review tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        AIRUNIT_DOC,
        PLANE_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1184 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1184-airunit-plane-residual-current-risk-review")
        == r"py -3 tools\wave1184_airunit_plane_residual_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1184 AirUnit/Plane residual current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1184 AirUnit/Plane residual current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
