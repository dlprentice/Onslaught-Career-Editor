#!/usr/bin/env python3
"""Validate Wave1154 UnitAI deploy/target current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1154-unitai-deploy-target-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1154-unitai-deploy-target-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1154-unitai-deploy-target-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1154_unitai_deploy_target_current_risk_review_2026-06-05.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified"

TARGETS = {
    "0x00410c50": (
        "CMonitor__UpdateMovementTransitionAndEffects",
        "void __fastcall CMonitor__UpdateMovementTransitionAndEffects(void * monitor)",
        ("CMonitor__UpdateTrackedRenderPair", "CMonitor__IntegrateMovementAgainstTerrain", "CBattleEngine__GroundParticleEffect"),
    ),
    "0x00414b30": (
        "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
        "int __fastcall TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit(void * target_set)",
        ("CUnit__IsTargetTimeoutBeforeProfileLimit", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "linked"),
    ),
    "0x00415780": (
        "CUnitAI__PlayDeployingAnimationIfState0",
        "void __fastcall CUnitAI__PlayDeployingAnimationIfState0(void * unitAI)",
        ("deploying", "0x260", "0xf0"),
    ),
    "0x004157c0": (
        "CUnitAI__PlayUndeployingAnimation",
        "void __fastcall CUnitAI__PlayUndeployingAnimation(void * unitAI)",
        ("undeploying", "0x1f0", "0xf0"),
    ),
    "0x00415970": (
        "CUnitAI__HandleDeployUndeployAnimationCompletion",
        "int __fastcall CUnitAI__HandleDeployUndeployAnimationCompletion(void * unitAI)",
        ("deployed", "normal", "CUnitAI__HandleDeployAndFireAnimationCompletion"),
    ),
}

EXPECTED_XREFS = {
    ("0x00410c50", "0x00408d61", "CMonitor__Process", "UNCONDITIONAL_CALL"),
    ("0x00414b30", "0x0040657e", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("0x00414b30", "0x0040658b", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("0x00415780", "0x005e23d4", "<no_function>", "DATA"),
    ("0x004157c0", "0x005e23d8", "<no_function>", "DATA"),
    ("0x00415970", "0x005e2378", "<no_function>", "DATA"),
}

DOC_TOKENS = (
    "Wave1154",
    "wave1154-unitai-deploy-target-current-risk-review",
    "378/1179 = 32.06%",
    "5 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 801",
    "current risk candidates: 6166",
    "UnitAI deploy/target transition current-risk review",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consults used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CMonitor__UpdateMovementTransitionAndEffects",
    "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
    "CUnitAI__PlayDeployingAnimationIfState0",
    "CUnitAI__PlayUndeployingAnimation",
    "CUnitAI__HandleDeployUndeployAnimationCompletion",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

STATIC_DONE_TOKENS = (
    "Static Done Definition",
    "Static binary RE is done when every active static lane",
    "no unreviewed active static-risk rows remain",
    "No active static lane is skipped, waived, or deferred merely because it is hard",
    "remaining unknowns must be explicitly outside static-only proof",
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


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 783,
        "pre-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    evidence = "\n".join(row.get("comment", "") for row in metadata.values())
    evidence += "\n" + "\n".join(read_text(path) for path in (BASE / "pre-decompile").glob("*.c"))
    evidence += "\n" + "\n".join(
        f"{row.get('mnemonic','')} {row.get('operands','')}" for row in read_tsv(BASE / "pre-instructions.tsv")
    )
    compact = evidence.lower().replace(" ", "")

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in tokens:
                require(token.lower().replace(" ", "") in compact or token in evidence, f"missing evidence token at {address}: {token}", failures)
        tag = tags.get(address)
        require(tag is not None, f"missing tag row for {address}", failures)
        if tag is not None:
            require(tag.get("status") == "OK", f"tag status mismatch at {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    actual_xrefs = {
        (normalize_address(row.get("target_addr", "")), normalize_address(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", ""))
        for row in read_tsv(BASE / "pre-xrefs.tsv")
    }
    for target, source, source_fn, ref_type in EXPECTED_XREFS:
        require(
            (normalize_address(target), normalize_address(source), source_fn, ref_type) in actual_xrefs,
            f"xref mismatch for {target} from {source}",
            failures,
        )


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 6 rows",
        "pre-instructions.log": "Wrote 783 function-body instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)
    focused_addresses = {normalize_address(row["address"]) for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused_addresses, f"target absent from focused list: {address}", failures)


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    latest = progress["latestWave"]
    require(latest["wave"] == "Wave1154 UnitAI deploy/target current-risk review", "progress latest wave mismatch", failures)
    require(latest["tag"] == "wave1154-unitai-deploy-target-current-risk-review", "progress latest tag mismatch", failures)
    require(latest["backup"] == BACKUP, "progress backup mismatch", failures)
    require(current["focusedReviewed"] == 378, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "32.06%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 801, "progress remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)

    done = progress.get("staticCompletionDefinition", {})
    require(done.get("status") == "active-definition", "static completion definition missing", failures)
    done_text = json.dumps(done, sort_keys=True)
    for token in STATIC_DONE_TOKENS[1:]:
        require(token in done_text, f"missing static completion token in progress: {token}", failures)

    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        ROOT / "README.md",
        ROOT / "CURRENT_CAPABILITIES.md",
        ROOT / "AGENTS.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
        ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
        ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md",
        ROOT / "developer_agent_state.json",
        ROOT / "documentation_agent_state.json",
        ROOT / "re_orchestrator_state.json",
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for token in STATIC_DONE_TOKENS:
            if path.name in {"mapped-systems.md", "static-reaudit-campaign.md"}:
                require(contains_token(text, token), f"missing static done token in {path.relative_to(ROOT)}: {token}", failures)

    owner_docs = {
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md": (
            "Wave1154",
            "wave1154-unitai-deploy-target-current-risk-review",
            "CUnitAI__PlayDeployingAnimationIfState0",
            "CUnitAI__PlayUndeployingAnimation",
            "CUnitAI__HandleDeployUndeployAnimationCompletion",
            BACKUP,
        ),
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md": (
            "Wave1154",
            "wave1154-unitai-deploy-target-current-risk-review",
            "CMonitor__UpdateMovementTransitionAndEffects",
            "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
            BACKUP,
        ),
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md": (
            "Wave1154",
            "wave1154-unitai-deploy-target-current-risk-review",
            "CMonitor__UpdateMovementTransitionAndEffects",
            "CMonitor__Process",
            BACKUP,
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1154 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1154-unitai-deploy-target-current-risk-review")
        == r"py -3 tools\wave1154_unitai_deploy_target_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_docs_progress(failures)
    if failures:
        print("Wave1154 UnitAI deploy/target current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1154 UnitAI deploy/target current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
