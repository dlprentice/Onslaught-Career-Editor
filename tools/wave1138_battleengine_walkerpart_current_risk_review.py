#!/usr/bin/env python3
"""Validate Wave1138 BattleEngine WalkerPart current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1138-battleengine-walkerpart-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1138-battleengine-walkerpart-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1138-battleengine-walkerpart-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1138_battleengine_walkerpart_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
UNIT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-130856_post_wave1138_battleengine_walkerpart_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-122130_post_wave1137_physics_script_weapon_bridge_review_verified"

TARGETS = {
    "0x00412cf0": (
        "CBattleEngineWalkerPart__dtor_base",
        "void __thiscall CBattleEngineWalkerPart__dtor_base(void * this)",
        ("drains owned weapon entries", "clears the weapon set", "destructor completeness"),
        ("0x00405bbc", "CBattleEngine__dtor_base", "UNCONDITIONAL_CALL"),
    ),
    "0x00414410": (
        "CBattleEngineWalkerPart__GetWeaponAmmoPercentage",
        "float __thiscall CBattleEngineWalkerPart__GetWeaponAmmoPercentage(void * this)",
        ("+0x52c", "+0x4b0/+0x88", "clamped to 1.0"),
        ("0x0040c43f", "CBattleEngine__GetWeaponAmmoPercentage", "UNCONDITIONAL_CALL"),
    ),
    "0x00414470": (
        "CBattleEngineWalkerPart__GetWeaponAmmoCount",
        "int __thiscall CBattleEngineWalkerPart__GetWeaponAmmoCount(void * this)",
        ("rounded +0x52c", "non-heat stores", "runtime HUD behavior"),
        ("0x0040c46f", "CBattleEngine__GetWeaponAmmoCount", "UNCONDITIONAL_CALL"),
    ),
    "0x004144c0": (
        "CBattleEngineWalkerPart__IsEnergyWeapon",
        "int __thiscall CBattleEngineWalkerPart__IsEnergyWeapon(void * this)",
        ("+0x55c", "heat flag", "runtime HUD behavior"),
        ("0x0040c48f", "CBattleEngine__IsEnergyWeapon", "UNCONDITIONAL_CALL"),
    ),
    "0x004144f0": (
        "CBattleEngineWalkerPart__IsWeaponOverheated",
        "int __thiscall CBattleEngineWalkerPart__IsWeaponOverheated(void * this)",
        ("+0x544", "overheat flag", "runtime HUD behavior"),
        ("0x0040c3af", "CBattleEngine__IsWeaponOverheated", "UNCONDITIONAL_CALL"),
    ),
}

DOC_TOKENS = (
    "Wave1138",
    "wave1138-battleengine-walkerpart-current-risk-review",
    "219/1179 = 18.58%",
    "5 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 960",
    "BattleEngine WalkerPart weapon/ammo/heat current-risk cluster",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime walkerpart weapon behavior proven",
    "runtime hud ammo behavior proven",
    "runtime heat/overheat behavior proven",
    "weapon_fire_breaks_stealth proven",
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
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 5 rows",
        "pre-instructions.log": "Wrote 125 function-body instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "ERROR Abort", "MISSING:", "BADADDR", "FAIL:", "bad=1", "failed=1", "missing=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    expected_counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 5,
        "pre-instructions.tsv": 125,
        "pre-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    instructions = read_text(BASE / "pre-instructions.tsv")
    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "pre-decompile").glob("*.c"))

    for address, (name, signature, comment_tokens, xref_spec) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch for {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag row mismatch for {address}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch for {address}", failures)
        require((BASE / "pre-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)

        from_addr, from_function, ref_type = xref_spec
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref for {address}: {xref_spec}",
            failures,
        )
        require(address in instructions, f"missing instruction address token for {address}", failures)
        require(name in decompile_text, f"missing decompile name token for {name}", failures)

    for token in ("CSPtrSet__Clear", "0x52c", "0x4b0", "0x88", "0x55c", "0x544"):
        require(token in decompile_text or token in instructions, f"missing body evidence token: {token}", failures)


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
        UNIT_CONTRACT,
        BATTLEENGINE_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1138 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)

    for label, data in (("progress", read_json(PROGRESS)), ("progress mirror", read_json(PROGRESS_MIRROR))):
        latest = data["latestWave"]
        current = data["post100Reaudit"]["currentRiskRank"]
        sample = data["latestSample"]
        require(latest["wave"] == "Wave1138 BattleEngine WalkerPart current-risk review", f"{label} latest wave mismatch", failures)
        require(latest["tag"] == "wave1138-battleengine-walkerpart-current-risk-review", f"{label} latest tag mismatch", failures)
        require(latest["backup"] == BACKUP, f"{label} backup mismatch", failures)
        artifact_commit = latest.get("artifactCommit")
        require(
            artifact_commit == "pending Wave1138 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", str(artifact_commit or ""))),
            f"{label} artifact commit mismatch",
            failures,
        )
        require(current["focusedReviewed"] == 219, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "18.58%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1138-battleengine-walkerpart-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 960, f"{label} remaining focused count mismatch", failures)
        require(sample.get("wave") == "Wave1138" and sample.get("ok") == 5 and sample.get("total") == 5, f"{label} sample mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1138_battleengine_walkerpart_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1138-battleengine-walkerpart-current-risk-review") == expected_script, "missing package script", failures)


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
        print("Wave1138 BattleEngine WalkerPart current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1138 BattleEngine WalkerPart current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
