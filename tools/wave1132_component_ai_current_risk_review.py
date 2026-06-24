#!/usr/bin/env python3
"""Validate Wave1132 component/UnitAI current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1132-component-ai-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUALITY_LOG = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1132.log"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1132-component-ai-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1132-component-ai-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1132_component_ai_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
COMPONENT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Component.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
UNITAI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified"

TARGETS = {
    "0x00427b80": (
        "CComponent__VFunc_09_00427b80",
        "void __thiscall CComponent__VFunc_09_00427b80(void * this, void * init)",
        ("Thunderhead Main Gun", "Normal", "Activated"),
        ("0x005e3d64", "<no_function>", "DATA"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-21-current-risk", "component-init"),
    ),
    "0x00427f90": (
        "CComponentBomberAI__scalar_deleting_dtor",
        "void * __thiscall CComponentBomberAI__scalar_deleting_dtor(void * this, byte flags)",
        ("CComponentBomberAI", "OID__FreeObject", "scalar-delete"),
        ("0x005d96b8", "<no_function>", "DATA"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-16-current-risk", "ccomponent-bomber-ai"),
    ),
    "0x00427fb0": (
        "CComponentBomberAI__dtor_base",
        "void __fastcall CComponentBomberAI__dtor_base(void * this)",
        ("CComponentBomberAI", "CSPtrSet__Remove", "CMonitor__Shutdown"),
        ("0x00427f93", "CComponentBomberAI__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-20-current-risk", "monitored-set-cleanup"),
    ),
    "0x00428050": (
        "CFenrirMainGunAI__scalar_deleting_dtor",
        "void * __thiscall CFenrirMainGunAI__scalar_deleting_dtor(void * this, byte flags)",
        ("CFenrirMainGunAI", "OID__FreeObject", "scalar-delete"),
        ("0x005d9684", "<no_function>", "DATA"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-16-current-risk", "cfenrir-main-gun-ai"),
    ),
    "0x00428070": (
        "CFenrirMainGunAI__dtor_base",
        "void __fastcall CFenrirMainGunAI__dtor_base(void * this)",
        ("CFenrirMainGunAI", "CSPtrSet__Remove", "CMonitor__Shutdown"),
        ("0x00428053", "CFenrirMainGunAI__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-20-current-risk", "monitored-set-cleanup"),
    ),
    "0x00428710": (
        "CUnitAI__GetRenderPosFromActorOrCache",
        "void * __thiscall CUnitAI__GetRenderPosFromActorOrCache(void * this, void * outRenderPos, void * unused)",
        ("CActor__GetRenderPos", "refreshing/copying", "cached component position"),
        ("0x005e4180", "<no_function>", "DATA"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-20-current-risk", "render-cache"),
    ),
    "0x00428770": (
        "CUnitAI__GetRenderOrientationFromActorOrCache",
        "void * __thiscall CUnitAI__GetRenderOrientationFromActorOrCache(void * this, void * outRenderOrientation, void * unused)",
        ("CActor__GetRenderOrientation", "refreshing/copying", "cached orientation matrix"),
        ("0x005e4184", "<no_function>", "DATA"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-20-current-risk", "render-cache"),
    ),
    "0x00428c70": (
        "CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action",
        "void __fastcall CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action(void * this)",
        ("resets field D0", "flag bit 4", "vtable slot 0x38"),
        ("0x005e430c", "<no_function>", "DATA"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-20-current-risk", "flag4-dispatch"),
    ),
    "0x00428d50": (
        "CUnitAI__PlayActivateAnimationOrFinalizeActivated",
        "void __fastcall CUnitAI__PlayActivateAnimationOrFinalizeActivated(void * this)",
        ("Activate", "finalizes activation", "vtable slot 0xf0"),
        ("0x005e4250", "<no_function>", "DATA"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-20-current-risk", "activation-animation"),
    ),
    "0x00428e80": (
        "CComponentAI__ClearReaderIfTargetDestroyedThenForward",
        "void __fastcall CComponentAI__ClearReaderIfTargetDestroyedThenForward(void * this)",
        ("CComponentBomberAI", "CFenrirMainGunAI", "vtable slot 0x2c"),
        ("0x005d96c4", "<no_function>", "DATA"),
        ("wave1132-component-ai-current-risk-review", "wave1132-readback-verified", "score-22-current-risk", "component-ai-reader-clear"),
    ),
}

DOC_TOKENS = (
    "Wave1132",
    "wave1132-component-ai-current-risk-review",
    "178/1179 = 15.10%",
    "10 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 1001",
    "component/active-reader UnitAI residual cluster",
    "fresh Ghidra export",
    "tag-only normalization",
    "91 tags",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime component behavior proven",
    "runtime unitai behavior proven",
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=91 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=91 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 21 rows",
        "post-instructions.log": "Wrote 326 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "context-metadata.log": "targets=10 found=10 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "context-xrefs.log": "Wrote 16 rows",
        "context-instructions.log": "Wrote 1173 function-body instruction rows",
        "context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 21,
        "pre-instructions.tsv": 326,
        "pre-decompile/index.tsv": 10,
        "context-metadata.tsv": 10,
        "context-tags.tsv": 10,
        "context-xrefs.tsv": 16,
        "context-instructions.tsv": 1173,
        "context-decompile/index.tsv": 10,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 21,
        "post-instructions.tsv": 326,
        "post-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for stem in ("metadata", "xrefs", "instructions"):
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
            comment = row.get("comment", "").lower()
            for token in comment_tokens:
                require(token.lower() in comment, f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in tag_tokens + ("current-risk-review", "component-ai-current-risk-review", "retail-binary-evidence"):
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


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


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
        COMPONENT_DOC,
        UNIT_DOC,
        UNITAI_DOC,
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
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1132 Component/UnitAI current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1132-component-ai-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(current["focusedReviewed"] == 178, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "15.10%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1132-component-ai-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 1001, f"{label} remaining focused count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1132_component_ai_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1132-component-ai-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_logs(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1132 component/UnitAI current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1132 component/UnitAI current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
