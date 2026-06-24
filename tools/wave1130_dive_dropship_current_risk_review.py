#!/usr/bin/env python3
"""Validate Wave1130 DiveBomber/Dropship current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1130-dive-dropship-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUALITY_LOG = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1130.log"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1130-dive-dropship-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1130-dive-dropship-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1130_dive_dropship_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DIVE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DiveBomber.cpp" / "_index.md"
DROPSHIP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Dropship.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified"

TARGETS = {
    "0x00445380": (
        "CDiveBomberAI__scalar_deleting_dtor",
        "void * __thiscall CDiveBomberAI__scalar_deleting_dtor(void * this, int flags)",
        ("CDiveBomberAI__dtor_base", "OID__FreeObject", "runtime AI behavior"),
        ("0x005db1b0", "<no_function>", "DATA"),
        ("divebomber-ai", "wave1130-dive-dropship-current-risk-review", "wave1130-readback-verified", "vtable"),
    ),
    "0x00445440": (
        "CDiveBomberGuide__scalar_deleting_dtor",
        "void * __thiscall CDiveBomberGuide__scalar_deleting_dtor(void * this, int flags)",
        ("CDiveBomberGuide__dtor_base", "OID__FreeObject", "runtime guide behavior"),
        ("0x005db184", "<no_function>", "DATA"),
        ("divebomber-guide", "wave1130-dive-dropship-current-risk-review", "wave1130-readback-verified", "vtable"),
    ),
    "0x00446d70": (
        "CDropship__Init",
        "void __thiscall CDropship__Init(void * this, void * initThing)",
        ("CAirUnit", "wingflat", "doorclosed", "Thruster Dust Effect"),
        ("0x005e1dfc", "<no_function>", "DATA"),
        ("dropship", "init", "component-init", "wave1130-dive-dropship-current-risk-review", "wave1130-readback-verified"),
    ),
    "0x00447040": (
        "CDropshipAI__scalar_deleting_dtor",
        "void * __thiscall CDropshipAI__scalar_deleting_dtor(void * this, int flags)",
        ("CDropshipAI__dtor_base", "OID__FreeObject", "runtime AI behavior"),
        ("0x005db1f8", "<no_function>", "DATA"),
        ("dropship-ai", "wave1130-dive-dropship-current-risk-review", "wave1130-readback-verified", "vtable"),
    ),
    "0x00447120": (
        "CDropship__ProcessDoorThrustersAndChildUnits",
        "void __fastcall CDropship__ProcessDoorThrustersAndChildUnits(void * this)",
        ("dooropening", "doorclosing", "child-unit", "thruster"),
        ("0x005e1ee0", "<no_function>", "DATA"),
        ("door-state", "child-units", "wave1130-dive-dropship-current-risk-review", "wave1130-readback-verified", "vtable"),
    ),
    "0x00448170": (
        "CDropship__TraceGroundAndSpawnThrusterDust",
        "void __stdcall CDropship__TraceGroundAndSpawnThrusterDust(void * effectPoint, void * transformMatrix)",
        ("CLine", "heightfield", "thruster dust"),
        ("0x004472b2", "CDropship__ProcessDoorThrustersAndChildUnits", "UNCONDITIONAL_CALL"),
        ("heightfield", "particle-effect", "stdcall-helper", "wave1130-dive-dropship-current-risk-review", "wave1130-readback-verified"),
    ),
}

DOC_TOKENS = (
    "Wave1130",
    "wave1130-dive-dropship-current-risk-review",
    "161/1179 = 13.66%",
    "6 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 1018",
    "score-22 DiveBomber/Dropship aircraft current-risk cluster",
    "fresh Ghidra export",
    "tag-only normalization",
    "42 tags",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime dropship behavior proven",
    "runtime dive-bomber behavior proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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


def check_wave1108_accounting(failures: list[str]) -> None:
    counts = wave1108_current_risk_rank.generate()
    require(counts["total"] == 6410, "Wave1108 total mismatch", failures)
    require(counts["risk"] == 6165, "Wave1108 risk mismatch", failures)
    require(counts["focused"] == 1178, "Wave1108 focused mismatch", failures)
    focused = {normalize_address(row["address"]): row for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused, f"target missing from current focused TSV: {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=42 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=42 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 7 rows",
        "post-instructions.log": "Wrote 1049 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=4 rows=512",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality = read_text(QUALITY_LOG)
    require("total_functions=6410 commented_functions=6410" in quality, "quality refresh mismatch", failures)


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 7,
        "pre-instructions.tsv": 1049,
        "pre-decompile/index.tsv": 6,
        "pre-vtable-slots.tsv": 512,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 7,
        "post-instructions.tsv": 1049,
        "post-decompile/index.tsv": 6,
        "post-vtable-slots.tsv": 512,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for stem in ("metadata", "xrefs", "instructions", "vtable-slots"):
        require(read_text(BASE / f"pre-{stem}.tsv") == read_text(BASE / f"post-{stem}.tsv"), f"pre/post {stem} drift", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, comment_tokens, xref, tag_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch for {address}", failures)
            for token in comment_tokens:
                require(token.lower() in row.get("comment", "").lower(), f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in tag_tokens + ("current-risk-review", "score-22-current-risk", "aircraft-current-risk-review"):
                require(token in actual, f"missing tag for {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch for {address}", failures)

        from_addr, from_function, ref_type = xref
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref for {address}: {xref}",
            failures,
        )

    require(
        any(
            normalize_address(row.get("target_addr", "")) == "0x00448170"
            and normalize_address(row.get("from_addr", "")) == "0x004473f9"
            and row.get("from_function") == "CDropship__ProcessDoorThrustersAndChildUnits"
            for row in xrefs
        ),
        "missing second dropship dust helper call xref",
        failures,
    )


def check_vtables_and_backup(failures: list[str]) -> None:
    slots = read_tsv(BASE / "post-vtable-slots.tsv")
    expected_slots = (
        ("0x005db180", "1", "0x005db184", "0x00445440", "CDiveBomberGuide__scalar_deleting_dtor"),
        ("0x005db1ac", "1", "0x005db1b0", "0x00445380", "CDiveBomberAI__scalar_deleting_dtor"),
        ("0x005db1f4", "1", "0x005db1f8", "0x00447040", "CDropshipAI__scalar_deleting_dtor"),
        ("0x005e1dfc", "0", "0x005e1dfc", "0x00446d70", "CDropship__Init"),
        ("0x005e1dfc", "57", "0x005e1ee0", "0x00447120", "CDropship__ProcessDoorThrustersAndChildUnits"),
    )
    for vtable, slot, slot_addr, pointer, name in expected_slots:
        require(
            any(
                normalize_address(row.get("vtable", "")) == vtable
                and row.get("slot_index") == slot
                and normalize_address(row.get("slot_addr", "")) == slot_addr
                and normalize_address(row.get("pointer_addr", "")) == pointer
                and row.get("function_name") == name
                and row.get("status") == "OK"
                for row in slots
            ),
            f"missing vtable slot: {vtable}[{slot}] -> {name}",
            failures,
        )

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        DIVE_DOC,
        DROPSHIP_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    address_tokens = tuple(f"{address} {target[0]}" for address, target in TARGETS.items())
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS + address_tokens:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    commit_pattern = re.compile(r"^(pending Wave1130 artifact commit|[0-9a-f]{40})$")
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1130 Dive/Dropship current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1130-dive-dropship-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(bool(commit_pattern.match(data["latestWave"].get("artifactCommit", ""))), f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 161, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "13.66%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1130-dive-dropship-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 1018, f"{label} remaining focused count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1130_dive_dropship_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1130-dive-dropship-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_logs(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_vtables_and_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1130 Dive/Dropship current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1130 Dive/Dropship current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
