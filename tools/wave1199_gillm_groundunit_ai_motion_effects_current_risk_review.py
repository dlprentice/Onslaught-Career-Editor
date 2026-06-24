#!/usr/bin/env python3
"""Validate Wave1199 GillM/GroundUnit AI-motion-effects current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1199_gillm_groundunit_ai_motion_effects_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GILLM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GillM.cpp" / "_index.md"
GILLMHEAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GillMHead.cpp" / "_index.md"
GROUNDUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GroundUnit.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyGillMGroundUnitAIMotionEffectsCurrentRiskWave1199.java"

BACKUP = r"G:\GhidraBackups\BEA_20260606-225205_post_wave1199_gillm_groundunit_ai_motion_effects_current_risk_review_verified"

TARGETS = {
    "0x0049fdb0": (
        "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0",
        "void __fastcall SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0(void * this)",
        ("score19 shared ground-unit", "0x005e3190", "CMCMech__BuildInterpolatedPoseAndAnchor"),
    ),
    "0x0047a900": (
        "CGillMHeadAI__AdvanceOpenAttackCloseState",
        "int __fastcall CGillMHeadAI__AdvanceOpenAttackCloseState(void * this)",
        ("score18 GillMHeadAI", "0x005e42e4", "CUnit__HasAnyLinkedUnitBeforeTargetTimeout"),
    ),
    "0x0047a730": (
        "CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730",
        "void __thiscall CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730(void * this, void * arg)",
        ("score17 GillMHeadAI-adjacent", "0x005e421c", "0x0062ca48"),
    ),
    "0x0047a9c0": (
        "CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0",
        "void __thiscall CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0(void * this, int mode)",
        ("score17 GillMHeadAI-adjacent", "0x005e42d0", "CUnit__SetEngagementModeAndMaybeClearTargetReader"),
    ),
    "0x00479b60": (
        "CGillM__InitGillMAIComponent",
        "void __thiscall CGillM__InitGillMAIComponent(void * this, void * init_data)",
        ("score16 CGillM", "0x005e0d08", "0x005dbcb4", "this+0x13c"),
    ),
    "0x00479bf0": (
        "CGillMAI__ScalarDeletingDestructor",
        "void * __thiscall CGillMAI__ScalarDeletingDestructor(void * this, byte flags)",
        ("score16 CGillMAI", "0x005dbcb8", "flags bit 0"),
    ),
    "0x00479cb0": (
        "CGillM__InitTerrainGuideComponent",
        "void __fastcall CGillM__InitTerrainGuideComponent(void * this)",
        ("score16 CGillM", "0x005e0d0c", "CTerrainGuide__ctor", "this+0x208"),
    ),
    "0x00479d10": (
        "CGillM__UpdateGroundedVerticalDrift",
        "void __fastcall CGillM__UpdateGroundedVerticalDrift(void * this)",
        ("score16 CGillM", "0x005e0c38", "+0x274", "+0x244"),
    ),
    "0x00479db0": (
        "CGillM__TriggerRandomArmHitAnimationIfReady",
        "void __fastcall CGillM__TriggerRandomArmHitAnimationIfReady(void * this)",
        ("score16 CGillM", "0x0047a392", "Gill_M_Left_Arm", "Gill_M_Right_Arm"),
    ),
    "0x0047a160": (
        "CGillM__StartState1WithStoredMotionVector",
        "void __thiscall CGillM__StartState1WithStoredMotionVector(void * this)",
        ("score16 CGillM", "0x005e0cc0", "+0x278", "vtable +0xf4"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review",
    "wave1199-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "score16-19",
    "gillm-groundunit-ai-motion-effects",
    "source-identity-deferred",
    "exact-layout-deferred",
    "runtime-behavior-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "signature-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1199",
    "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review",
    "10 GillM/GillMHead/shared ground-unit AI/motion/effects score16-19 current-risk rows",
    "870/1179 = 73.79%",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "remaining active focused work: 309",
    "legacy additive counter is deprecated",
    "901/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=10 skipped=0",
    "comment_only_updated=10",
    "tags_added=129",
    "final dry updated=0 skipped=10",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0",
    "CGillMHeadAI__AdvanceOpenAttackCloseState",
    "CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730",
    "CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0",
    "CGillM__InitGillMAIComponent",
    "CGillMAI__ScalarDeletingDestructor",
    "CGillM__InitTerrainGuideComponent",
    "CGillM__UpdateGroundedVerticalDrift",
    "CGillM__TriggerRandomArmHitAnimationIfReady",
    "CGillM__StartState1WithStoredMotionVector",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "13 xref rows",
    "540 instruction rows",
    "10 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

ACCOUNTING_TOKENS = (
    "Wave1199",
    "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review",
    "870/1179 = 73.79%",
    "remaining active focused work: 309",
    "legacy additive counter is deprecated",
    "901/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime animation behavior proven",
    "runtime movement behavior proven",
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 13,
        "pre-instructions.tsv": 540,
        "pre-decompile/index.tsv": 10,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 13,
        "post-instructions.tsv": 540,
        "post-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in (
                "Wave1199 static current-risk read-back",
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


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 tags_added=129 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 tags_added=129 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 13 rows",
        "post-instructions.log": "Wrote 540 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_BAD", "FAIL:", "missing=1", "bad=1", "failed=1"):
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
    require(current.get("accountingMode") == "unique-address-ledger", "accounting mode mismatch", failures)
    require(current.get("focusedReviewed") == 870, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "73.79%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 309, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 901, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 870, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "73.79%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 309, "ledger remaining mismatch", failures)
    require(ledger.get("duplicateAddressOvercount") == 26, "ledger duplicate mismatch", failures)
    require(ledger.get("wave1145ArithmeticOvercount") == 5, "ledger Wave1145 mismatch", failures)
    require(ledger.get("countedRowsThroughWave1199") == 896, "ledger counted row mismatch", failures)

    prose_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        GILLM_DOC: (
            "Wave1199",
            "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review",
            "CGillM__InitGillMAIComponent",
            "CGillMAI__ScalarDeletingDestructor",
            "CGillM__InitTerrainGuideComponent",
            "CGillM__UpdateGroundedVerticalDrift",
            "CGillM__TriggerRandomArmHitAnimationIfReady",
            "CGillM__StartState1WithStoredMotionVector",
            "870/1179 = 73.79%",
            "remaining active focused work: 309",
            "13 xref rows",
            "540 instruction rows",
            "10 decompile rows",
            BACKUP,
        ),
        GILLMHEAD_DOC: (
            "Wave1199",
            "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review",
            "CGillMHeadAI__AdvanceOpenAttackCloseState",
            "CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730",
            "CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0",
            "870/1179 = 73.79%",
            "remaining active focused work: 309",
            "0x005e42e4",
            "0x005e421c",
            "0x005e42d0",
            BACKUP,
        ),
        GROUNDUNIT_DOC: (
            "Wave1199",
            "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review",
            "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0",
            "870/1179 = 73.79%",
            "remaining active focused work: 309",
            "0x005e3190",
            "0x005e10fc",
            "0x005e0c4c",
            "0x005e07a0",
            BACKUP,
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    accounting_docs = [PROGRESS, LEDGER, ACCOUNTING]
    for path in accounting_docs:
        text = read_text(path)
        for token in ACCOUNTING_TOKENS:
            require(contains_token(text, token), f"missing accounting token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1199 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1199-gillm-groundunit-ai-motion-effects-current-risk-review")
        == r"py -3 tools\wave1199_gillm_groundunit_ai_motion_effects_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Ghidra apply script", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == "Wave1199 GillM/GroundUnit AI-motion-effects current-risk review" for row in ledger_rows), "missing Wave1199 ledger row", failures)
    require(any(row.get("task") == "Wave1199 GillM/GroundUnit AI-motion-effects current-risk review" and row.get("result") == "success" for row in attempt_rows), "missing Wave1199 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1199 GillM/GroundUnit AI-motion-effects current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1199 GillM/GroundUnit AI-motion-effects current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
