#!/usr/bin/env python3
"""Validate Wave1210 Waypoint/Wingman lifecycle current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1210-waypoint-wingman-lifecycle-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1210-waypoint-wingman-lifecycle-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1210-waypoint-wingman-lifecycle-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1210_waypoint_wingman_lifecycle_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WAYPOINT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WaypointManager.cpp" / "_index.md"
OIDS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "oids.cpp" / "_index.md"
CURRENT_CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-053028_post_wave1210_waypoint_wingman_lifecycle_current_risk_review_verified"

TARGETS = {
    "0x004bfd60": (
        "CWaypoint__scalar_deleting_dtor",
        "void * __thiscall CWaypoint__scalar_deleting_dtor(void * this, byte flags)",
        ("Wave1210 static correction", "CWaypoint__dtor_base", "0x005dd2f4", "CDXMemoryManager__Free(&DAT_009c3df0, this)"),
    ),
    "0x004bfdc0": (
        "CWingmanStart__scalar_deleting_dtor",
        "void * __thiscall CWingmanStart__scalar_deleting_dtor(void * this, byte flags)",
        ("Wave1210 static correction", "CWingmanStart__dtor_base", "0x005dcb5c", "CDXMemoryManager__Free(&DAT_009c3df0, this)"),
    ),
    "0x004bfe70": (
        "CWaypoint__dtor_base",
        "void __fastcall CWaypoint__dtor_base(void * this)",
        ("Wave1210 static correction", "CThing__dtor_base", "CSPtrSet__Remove", "stale CThing__ctor_like_004f3640"),
    ),
    "0x004bffa0": (
        "CWingmanStart__dtor_base",
        "void __fastcall CWingmanStart__dtor_base(void * this)",
        ("Wave1210 static read-back", "CComplexThing__dtor_base", "CSPtrSet__Remove", "this+0x7c"),
    ),
    "0x00505960": (
        "CWaypoint__Load",
        "void __thiscall CWaypoint__Load(void * this, void * mem_buffer, int load_mode, void * object_table)",
        ("Wave1210 static read-back", "RET 0x0c", "WaypointManager.cpp line 0x1a", "this+0x08"),
    ),
    "0x00505bb0": (
        "CWaypointPath__scalar_deleting_dtor",
        "void * __thiscall CWaypointPath__scalar_deleting_dtor(void * this, byte flags)",
        ("Wave1210 static read-back", "CWaypointPath__dtor_base", "0x005dfc8c", "CDXMemoryManager__Free(&DAT_009c3df0, this)"),
    ),
}

TARGET_XREFS = {
    "0x004bfd60": ("0x005dd2f4", "DATA"),
    "0x004bfdc0": ("0x005dcb5c", "DATA"),
    "0x004bfe70": ("0x004bfd63", "UNCONDITIONAL_CALL"),
    "0x004bffa0": ("0x004bfdc3", "UNCONDITIONAL_CALL"),
    "0x00505960": ("0x00505b64", "UNCONDITIONAL_CALL"),
    "0x00505bb0": ("0x005dfc8c", "DATA"),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1210-waypoint-wingman-lifecycle-current-risk-review",
    "wave1210-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "object-lifecycle",
    "waypoint-lifecycle",
    "rebuild-grade-static-contract",
}

EXTRA_TAGS = {
    "0x004bfd60": {"scalar-deleting-destructor", "destructor", "waypoint", "comment-corrected", "memory-manager-free"},
    "0x004bfdc0": {"scalar-deleting-destructor", "destructor", "wingman-start", "comment-corrected", "memory-manager-free"},
    "0x004bfe70": {"destructor-body", "destructor", "waypoint", "comment-corrected", "owner-link-cleanup"},
    "0x004bffa0": {"destructor-body", "destructor", "wingman-start", "owner-link-cleanup"},
    "0x00505960": {"waypoint", "load", "mem-buffer", "object-link"},
    "0x00505bb0": {"scalar-deleting-destructor", "destructor", "waypoint-path", "memory-manager-free"},
}

DOC_TOKENS = (
    "Wave1210",
    "wave1210-waypoint-wingman-lifecycle-current-risk-review",
    "6 Waypoint/Wingman lifecycle current-risk rows",
    "1102/1179 = 93.47%",
    "remaining active focused work: 77",
    "1133/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1127",
    "live regenerated current focused candidates: 1127",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "CThing__dtor_base",
    "stale CThing__ctor_like_004f3640",
    "tags_removed=1",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consult used",
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "6 xref rows",
    "630 instruction rows",
    "6 decompile rows",
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
    "runtime waypoint behavior proven",
    "runtime wingman-start behavior proven",
    "exact waypoint layout proven",
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
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 630,
        "pre-decompile/index.tsv": 6,
        "context-metadata.tsv": 8,
        "context-tags.tsv": 8,
        "context-xrefs.tsv": 11,
        "context-instructions.tsv": 968,
        "context-decompile/index.tsv": 8,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 6,
        "post-instructions.tsv": 630,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    changed_comments = 0
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            pre_comment = pre_metadata[address].get("comment", "")
            comment = row.get("comment", "")
            changed_comments += int(pre_comment != comment)
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
            if address == "0x00505960":
                require("destructor" not in actual, "CWaypoint__Load must not carry destructor tag", failures)
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

    require(changed_comments == 6, f"expected six pre/post comment changes, got {changed_comments}", failures)

    instructions = read_text(BASE / "post-instructions.tsv")
    for token in ("CWaypoint__dtor_base", "CWingmanStart__dtor_base", "CWaypoint__Load"):
        require(token in instructions, f"missing instruction token: {token}", failures)

    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "post-decompile").glob("*.c"))
    for token in (
        "CThing__dtor_base(this)",
        "CComplexThing__dtor_base(this)",
        "CWaypointPath__dtor_base(this)",
        "CSPtrSet__AddToHead",
        "CSPtrSet__Remove",
        "CDXMemoryManager__Free",
    ):
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-xrefs.log": "Wrote 6 rows",
        "pre-instructions.log": "Wrote 630 instruction rows",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=8 found=8 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "context-xrefs.log": "Wrote 11 rows",
        "context-instructions.log": "Wrote 968 instruction rows",
        "context-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 tags_removed=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 tags_removed=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 tags_removed=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 6 rows",
        "post-instructions.log": "Wrote 630 instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_accounting(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    queue = read_json(QUEUE_JSON)
    ledger = read_json(LEDGER)
    current = progress["post100Reaudit"]["currentRiskRank"]

    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    quality = queue["qualitySignals"]
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    for data, label in ((current, "progress"), (ledger, "ledger")):
        getter = data.get
        require(getter("focusedReviewed", getter("correctedUniqueReviewed")) == 1102, f"{label} reviewed mismatch", failures)
        require(getter("focusedReviewedPercent", getter("correctedUniquePercent")) == "93.47%", f"{label} percent mismatch", failures)
        require(getter("remainingFocusedAfterLatestReview", getter("remainingUnique")) == 77, f"{label} remaining mismatch", failures)
        require(getter("liveFocusedCandidatesAfterLatestReview") == 1127, f"{label} live focused mismatch", failures)

    require(ledger.get("latestWaveTag") == "wave1210-waypoint-wingman-lifecycle-current-risk-review", "ledger latest tag mismatch", failures)
    require(ledger.get("legacyAdditiveThroughWave1210Deprecated") == 1133, "legacy additive mismatch", failures)
    require(ledger.get("countedRowsThroughWave1210") == 1128, "counted rows mismatch", failures)
    require(ledger.get("duplicateAddressOvercount") == 26, "duplicate overcount mismatch", failures)
    require(ledger.get("wave1145ArithmeticOvercount") == 5, "Wave1145 overcount mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_INDEX,
        WAYPOINT_DOC,
        OIDS_DOC,
        CURRENT_CAPABILITIES,
        AGENTS,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1210-waypoint-wingman-lifecycle-current-risk-review")
        == r"py -3 tools\wave1210_waypoint_wingman_lifecycle_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave1210 Waypoint/Wingman lifecycle current-risk review" for row in read_jsonl(LEDGER_JSONL)), "missing Wave1210 ledger row", failures)
    require(any(row.get("task") == "Wave1210 Waypoint/Wingman lifecycle current-risk review" for row in read_jsonl(ATTEMPTS)), "missing Wave1210 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_accounting(failures)
    check_docs(failures)

    if failures:
        print("Wave1210 Waypoint/Wingman lifecycle current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1210 Waypoint/Wingman lifecycle current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
