#!/usr/bin/env python3
"""Validate Wave1185 AirUnit init current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1185-airunit-init-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1185-airunit-init-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1185-airunit-init-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1185_airunit_init_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
AIRUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "_index.md"
AIRUNIT_INIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "CAirUnit__Init.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
APPLY_SCRIPT = ROOT / "tools" / "ApplyAirUnitInitCurrentRiskWave1185.java"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-134914_post_wave1185_airunit_init_current_risk_review_verified"
TARGET = "0x00402ad0"
TARGET_NAME = "CAirUnit__Init"
TARGET_SIGNATURE = "void __thiscall CAirUnit__Init(void * this, void * init)"

EXPECTED_TAGS = {
    "static-reaudit",
    "wave1185-airunit-init-current-risk-review",
    "wave1185-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "air-unit",
    "lifecycle-init",
    "particle-effect-links",
    "source-identity-deferred",
    "exact-layout-deferred",
    "rebuild-grade-static-contract",
    "comment-hardened",
    "tag-normalized",
}

EXPECTED_XREFS = {
    ("0x00446dbd", "UNCONDITIONAL_CALL"),
    ("0x004d19fd", "UNCONDITIONAL_CALL"),
    ("0x005e3548", "DATA"),
    ("0x005e379c", "DATA"),
    ("0x00421ab9", "UNCONDITIONAL_CALL"),
    ("0x0042246a", "UNCONDITIONAL_CALL"),
    ("0x00445270", "UNCONDITIONAL_CALL"),
    ("0x0047bc0f", "UNCONDITIONAL_CALL"),
}

DOC_TOKENS = (
    "Wave1185",
    "wave1185-airunit-init-current-risk-review",
    "783/1179 = 66.41%",
    "1 AirUnit init lifecycle current-risk row",
    "current focused candidates: 1177",
    "live regenerated current focused candidates: 1177",
    "remaining active focused work: 396",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=1 skipped=0",
    "comment_only_updated=1",
    "tags_added=13",
    "final dry updated=0 skipped=1",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consult used",
    "no Cursor/Composer",
    "CAirUnit__Init",
    "CUnit__Init",
    "CCarrier__Init",
    "CDropship__Init",
    "CPlane__Init",
    "CGroundAttackAircraft__Init",
    "aircraft vtable DATA refs 0x005e3548/0x005e379c",
    "Trail",
    "Engine",
    "0x00622d14",
    "0x00622cec",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "8 xref rows",
    "165 instruction rows",
    "1 decompile row",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime flight/effect behavior proven",
    "runtime aircraft behavior proven",
    "concrete cunit/cairunit/init/profile/particle-node layouts proven",
    "exact source-body identity proven",
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
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 165,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {(normalize(row["from_addr"]), row.get("ref_type", "")) for row in read_tsv(BASE / "post-xrefs.tsv")}

    row = metadata.get(TARGET)
    require(row is not None, "missing metadata target", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "metadata name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, "metadata signature mismatch", failures)
        require(row.get("status") == "OK", "metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in (
            "Wave1185 static read-back",
            "CCarrier__Init",
            "CDropship__Init",
            "CPlane__Init",
            "CGroundAttackAircraft__Init",
            "0x005e3548/0x005e379c",
            "CUnit__Init",
            "+0x3bc",
            "Trail/Engine",
            "0x00622d14/0x00622cec",
            "CSPtrSet",
            "no-noticeable-difference parity remain separate proof",
        ):
            require(token in comment, f"missing comment token: {token}", failures)

    tag_row = tags.get(TARGET)
    require(tag_row is not None, "missing tag row", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(EXPECTED_TAGS.issubset(actual_tags), f"tags missing: {EXPECTED_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "tag status mismatch", failures)

    dec = decompile.get(TARGET)
    require(dec is not None, "missing decompile row", failures)
    if dec is not None:
        require(dec.get("name") == TARGET_NAME, "decompile name mismatch", failures)
        require(dec.get("signature") == TARGET_SIGNATURE, "decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    require(xrefs == EXPECTED_XREFS, f"xref set mismatch: {xrefs}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=13 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=13 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "rows=1 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 165 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1185_queue_probe.log")
    require("Status: PASS" in queue_log, "queue probe did not pass", failures)
    export_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1185.log")
    require("total_functions=6411 commented_functions=6411" in export_log, "quality export count mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless queue mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined queue mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N queue mismatch", failures)

    quality_rows = {normalize(row["address"]): row for row in read_tsv(QUEUE_TSV)}
    target = quality_rows.get(TARGET)
    require(target is not None, "target missing from quality TSV", failures)
    if target is not None:
        require(target.get("name") == TARGET_NAME, "quality TSV name mismatch", failures)
        require(target.get("signature") == TARGET_SIGNATURE, "quality TSV signature mismatch", failures)
        require("Wave1185 static read-back" in target.get("comment", ""), "quality TSV missing Wave1185 comment", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176098183, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1185 AirUnit Init Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1185-airunit-init-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    artifact_commit = str(latest.get("artifactCommit", ""))
    require(
        artifact_commit == "pending Wave1185 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", artifact_commit)),
        "latest artifact commit mismatch",
        failures,
    )
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 783, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "66.41%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 396, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1185-airunit-init-current-risk-review", "latest review tag mismatch", failures)


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
        AIRUNIT_INIT_DOC,
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

    require("void __thiscall CAirUnit__Init(void * this, void * init)" in read_text(AIRUNIT_INIT_DOC), "AirUnit init doc missing current signature", failures)
    require("int param_1" not in read_text(AIRUNIT_INIT_DOC), "AirUnit init doc still has stale param_1 signature", failures)
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1185 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1185-airunit-init-current-risk-review")
        == r"py -3 tools\wave1185_airunit_init_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1185 apply script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1185 AirUnit init current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1185 AirUnit init current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
