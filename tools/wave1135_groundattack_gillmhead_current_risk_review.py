#!/usr/bin/env python3
"""Validate Wave1135 GroundAttack/GillMHead current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1135-groundattack-gillmhead-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1135-groundattack-gillmhead-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1135-groundattack-gillmhead-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1135_groundattack_gillmhead_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GILLMHEAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GillMHead.cpp" / "_index.md"
GROUNDATTACK_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GroundAttackAircraft.cpp" / "_index.md"
GUIDE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Guide.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified"

TARGETS = {
    "0x0047a760": (
        "CGillMHead__CreateGillMHeadAIComponent",
        "void __thiscall CGillMHead__CreateGillMHeadAIComponent(void * this, void * init_data)",
        ("CGillMHeadAI", "0x005dbcec", "this+0x13c"),
        (("0x005e43d4", "<no_function>", "DATA"),),
        ("cgillmhead", "cgillmheadai", "gillmhead-ai-wave390", "static-reaudit"),
    ),
    "0x0047a810": (
        "CGillMHeadAI__Destructor",
        "void __fastcall CGillMHeadAI__Destructor(void * this)",
        ("CUnitAI base vtable", "CMonitor__Shutdown", "+0x28"),
        (("0x0047a7f3", "CGillMHeadAI__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),),
        ("cgillmheadai", "destructor", "gillmhead-ai-wave390", "static-reaudit"),
    ),
    "0x0047a8b0": (
        "CGillMHeadAI__TryTransitionIdleToOpen",
        "int __fastcall CGillMHeadAI__TryTransitionIdleToOpen(void * this)",
        ("idle", "open", "CUnit__UpdateDeployStateAndChargeEffects"),
        (("0x005e4350", "<no_function>", "DATA"),),
        ("cgillmheadai", "animation-state", "gillmhead-ai-wave390", "static-reaudit"),
    ),
    "0x0047bab0": (
        "CGroundAttackAI__InitState",
        "void __fastcall CGroundAttackAI__InitState(void * this)",
        ("+0x60", "+0x64", "CGroundAttackAircraft__CloseBay"),
        (("0x0047bc92", "CGroundAttackAircraft__Init", "UNCONDITIONAL_CALL"),),
        ("cgroundattackai", "init-state", "ground-attack-aircraft-wave391", "static-reaudit"),
    ),
    "0x0047bbf0": (
        "CGroundAttackAircraft__Init",
        "void __thiscall CGroundAttackAircraft__Init(void * this, void * init_data)",
        ("CAirUnit__Init", "CMCGroundAttack", "CGroundAttackGuide"),
        (("0x005e2bf0", "<no_function>", "DATA"),),
        ("cgroundattackaircraft", "component-create", "ground-attack-aircraft-wave391", "static-reaudit"),
    ),
    "0x0047bd90": (
        "CGroundAttackAI__Destructor",
        "void __fastcall CGroundAttackAI__Destructor(void * this)",
        ("CUnitAI base vtable", "CMonitor__Shutdown", "+0x24"),
        (("0x0047bd73", "CGroundAttackAI__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),),
        ("cgroundattackai", "destructor", "ground-attack-aircraft-wave391", "static-reaudit"),
    ),
    "0x0047be50": (
        "CGroundAttackGuide__Destructor",
        "void __fastcall CGroundAttackGuide__Destructor(void * this)",
        ("+0x2c", "CMonitor__Shutdown", "stale GillMHead"),
        (("0x0047be33", "CGroundAttackGuide__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),),
        ("cgroundattackguide", "destructor", "ground-attack-aircraft-wave391", "static-reaudit"),
    ),
    "0x0047c040": (
        "CGroundAttackAircraft__AdvanceCloseShootAnimationState",
        "int __fastcall CGroundAttackAircraft__AdvanceCloseShootAnimationState(void * this)",
        ("open", "shoot", "+0x27c"),
        (("0x005e2cb8", "<no_function>", "DATA"),),
        ("cgroundattackaircraft", "animation-state", "ground-attack-aircraft-wave391", "static-reaudit"),
    ),
    "0x0047e290": (
        "CGuide__ctor_base",
        "void * __thiscall CGuide__ctor_base(void * this, void * guideOwner)",
        ("guideOwner", "+0x18", "RET 0x4"),
        (("0x00402172", "CAirGuide__ctor", "UNCONDITIONAL_CALL"),),
        ("guide", "base-ctor", "static-reaudit"),
    ),
    "0x004964d0": (
        "CMCGroundAttack__Constructor",
        "void * __thiscall CMCGroundAttack__Constructor(void * this, void * owner_aircraft)",
        ("0x005dc330", "owner_aircraft", "+0x0c/+0x10"),
        (("0x0047bc41", "CGroundAttackAircraft__Init", "UNCONDITIONAL_CALL"),),
        ("cmcgroundattack", "constructor", "static-reaudit"),
    ),
}

CONTEXT_TARGETS = {
    "0x0047a730": "CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730",
    "0x0047a7f0": "CGillMHeadAI__ScalarDeletingDestructor",
    "0x0047a900": "CGillMHeadAI__AdvanceOpenAttackCloseState",
    "0x0047a9c0": "CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0",
    "0x0047afc0": "CGillMHeadAI__UpdateAimTransformAndTargetReader",
    "0x0047b090": "CGillMHeadAI__UpdateTargetBallisticArcFlags",
    "0x0047bd70": "CGroundAttackAI__ScalarDeletingDestructor",
    "0x0047be30": "CGroundAttackGuide__ScalarDeletingDestructor",
    "0x0047bfa0": "CGroundAttackAircraft__OpenBay",
    "0x0047bff0": "CGroundAttackAircraft__CloseBay",
    "0x00496500": "CMCGroundAttack__ScalarDeletingDestructor",
    "0x00496520": "CMCGroundAttack__Destructor",
    "0x00496540": "CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540",
}

DOC_TOKENS = (
    "Wave1135",
    "wave1135-groundattack-gillmhead-current-risk-review",
    "196/1179 = 16.62%",
    "10 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 983",
    "GroundAttack/GillMHead guide lifecycle cluster",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime groundattack behavior proven",
    "runtime gillmhead behavior proven",
    "runtime guide behavior proven",
    "runtime bay-animation behavior proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
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


def check_logs_and_counts(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=10 found=10 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "pre-xrefs.log": "Wrote 22 rows",
        "pre-instructions.log": "Wrote 443 function-body instruction rows",
        "pre-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "context-metadata.log": "targets=13 found=13 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "context-xrefs.log": "Wrote 15 rows",
        "context-instructions.log": "Wrote 546 function-body instruction rows",
        "context-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    expected_counts = {
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 22,
        "pre-instructions.tsv": 443,
        "pre-decompile/index.tsv": 10,
        "context-metadata.tsv": 13,
        "context-tags.tsv": 13,
        "context-xrefs.tsv": 15,
        "context-instructions.tsv": 546,
        "context-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}

    for address, (name, signature, comment_tokens, xref_specs, tag_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch for {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in tag_tokens:
                require(token in actual, f"missing tag for {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch for {address}", failures)
        require((BASE / "pre-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)

        for from_addr, from_function, ref_type in xref_specs:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                    and row.get("from_function") == from_function
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"missing xref for {address}: {(from_addr, from_function, ref_type)}",
                failures,
            )

    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch for {address}", failures)


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
        GILLMHEAD_DOC,
        GROUNDATTACK_DOC,
        GUIDE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    address_tokens = tuple(f"{address} {target[0]}" for address, target in TARGETS.items())
    context_tokens = tuple(f"context {address} {name}" for address, name in CONTEXT_TARGETS.items())
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS + address_tokens:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    note_text = read_text(NOTE)
    for token in context_tokens:
        require(contains_token(note_text, token), f"missing context token in note: {token}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1135 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)

    for label, data in (("progress", read_json(PROGRESS)), ("progress mirror", read_json(PROGRESS_MIRROR))):
        latest = data["latestWave"]
        current = data["post100Reaudit"]["currentRiskRank"]
        require(latest["wave"] == "Wave1135 GroundAttack/GillMHead current-risk review", f"{label} latest wave mismatch", failures)
        require(latest["tag"] == "wave1135-groundattack-gillmhead-current-risk-review", f"{label} latest tag mismatch", failures)
        require(latest["backup"] == BACKUP, f"{label} backup mismatch", failures)
        artifact_commit = latest.get("artifactCommit")
        require(
            artifact_commit == "pending Wave1135 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", str(artifact_commit or ""))),
            f"{label} artifact commit mismatch",
            failures,
        )
        require(current["focusedReviewed"] == 196, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "16.62%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1135-groundattack-gillmhead-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 983, f"{label} remaining focused count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1135_groundattack_gillmhead_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1135-groundattack-gillmhead-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_logs_and_counts(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1135 GroundAttack/GillMHead current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1135 GroundAttack/GillMHead current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
