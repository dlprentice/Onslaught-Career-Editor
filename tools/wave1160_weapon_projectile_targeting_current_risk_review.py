#!/usr/bin/env python3
"""Validate Wave1160 weapon/projectile targeting current-risk review evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1160-weapon-projectile-targeting-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1160-weapon-projectile-targeting-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1160-weapon-projectile-targeting-current-risk-review.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "wave1160_weapon_projectile_targeting_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x00505e00": ("CWeapon__ctor_base", "void * __thiscall CWeapon__ctor_base(void * this, void * weapon_data, int create_context)", ("CWeapon table", "runtime weapon behavior")),
    "0x005061f0": ("CWeapon__DoesTargetMaskMatchDistanceProfile", "bool __thiscall CWeapon__DoesTargetMaskMatchDistanceProfile(void * this, void * target_unit)", ("distance-profile", "target_unit")),
    "0x00506350": ("CWeapon__GetDistanceProfileField90", "int __fastcall CWeapon__GetDistanceProfileField90(void * this)", ("+0x90", "distance-profile")),
    "0x00506440": ("CWeapon__GetDistanceProfileField94", "double __fastcall CWeapon__GetDistanceProfileField94(void * this)", ("+0x94", "projectile")),
    "0x00506530": ("CWeapon__GetDistanceProfileFieldA8", "int __fastcall CWeapon__GetDistanceProfileFieldA8(void * this)", ("+0xa8", "firing-mode")),
    "0x00506620": ("CWeapon__GetDistanceProfileField98", "double __fastcall CWeapon__GetDistanceProfileField98(void * this)", ("+0x98", "targeting")),
    "0x00506710": ("CWeapon__GetDistanceProfileField9C", "double __fastcall CWeapon__GetDistanceProfileField9C(void * this)", ("+0x9c", "target-selection")),
    "0x00506800": ("CWeapon__GetDistanceProfileFieldA0", "double __fastcall CWeapon__GetDistanceProfileFieldA0(void * this)", ("+0xa0", "target-selection")),
    "0x005068f0": ("CWeapon__AdvanceChargeProgressIfAnySlotAssigned", "void __fastcall CWeapon__AdvanceChargeProgressIfAnySlotAssigned(void * weapon)", ("assigned-slot", "stealth behavior")),
    "0x00506010": ("ProjectileBurst__SpawnFromPercentBucketFallback", "int __fastcall ProjectileBurst__SpawnFromPercentBucketFallback(void * burstContext)", ("percent-bucket fallback", "weapon_fire_breaks_stealth")),
    "0x005069f0": ("ProjectileBurst__SpawnFromCurrentPreset", "int __fastcall ProjectileBurst__SpawnFromCurrentPreset(void * burstContext)", ("current-preset", "CBattleEngine::WeaponFired")),
    "0x005078b0": ("ProjectileBurstPreset__GetListEntryIdByIndex", "int __thiscall ProjectileBurstPreset__GetListEntryIdByIndex(void * this, int entry_index)", ("entry_index", "preset/list")),
    "0x004d9ef0": ("CRound__UpdateRoundAndTriggerLaunchEffect", "void __fastcall CRound__UpdateRoundAndTriggerLaunchEffect(void * this)", ("launch", "CRound")),
    "0x004dac90": ("CRound__SelectBestTargetReaderAndSyncAimState", "void __thiscall CRound__SelectBestTargetReaderAndSyncAimState(void * this, void * eventPayload, void * unusedContext)", ("active-reader helper", "aim state")),
    "0x004db150": ("CRound__SpawnConfiguredProjectile", "void __fastcall CRound__SpawnConfiguredProjectile(void * this)", ("creates a projectile", "CRoundInitThing-like")),
    "0x004d9f30": ("CRound__UpdateEffectTransformByMode_004d9f30", "void __thiscall CRound__UpdateEffectTransformByMode_004d9f30(void * this, int effectMode, void * context, void * targetOrOwner)", ("effect transform", "mode")),
    "0x004daab0": ("CRound__SetTargetReaderIfAllowed", "void __thiscall CRound__SetTargetReaderIfAllowed(void * this, void * targetReader, int replaceExisting)", ("targetReader", "replaceExisting")),
    "0x004db090": ("CRound__GetPresetScalarByConfigName", "double __fastcall CRound__GetPresetScalarByConfigName(void * this)", ("preset", "scalar")),
    "0x004db630": ("CRound__ArmProjectileAndSpawnTrailEffect", "void __fastcall CRound__ArmProjectileAndSpawnTrailEffect(void * this)", ("trail effect", "velocity")),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "comment-hardened"}
WAVE_TAG_TARGETS = {
    "0x00506010": {"wave1160-weapon-projectile-targeting-current-risk-review", "wave1160-readback-verified", "projectile-burst", "weapon-projectile-spine"},
    "0x005069f0": {"wave1160-weapon-projectile-targeting-current-risk-review", "wave1160-readback-verified", "projectile-burst", "weapon-projectile-spine"},
}

DOCS = [
    NOTE,
    NOTE_MIRROR,
    CONTRACT,
    CONTRACT_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "README.md",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "AGENTS.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Weapon.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Round.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

DOC_TOKENS = (
    "Wave1160",
    "wave1160-weapon-projectile-targeting-current-risk-review",
    "516/1179 = 43.77%",
    "19 CWeapon/ProjectileBurst/CRound current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 663",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "tag-only normalization",
    "updated=2 skipped=0 renamed=0",
    "tags_added=16",
    "no rename",
    "no signature change",
    "no comment change",
    "Codex read-only consults used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "51 xref rows",
    "3272 instruction rows",
    "CWeapon__DoesTargetMaskMatchDistanceProfile",
    "ProjectileBurst__SpawnFromPercentBucketFallback",
    "ProjectileBurst__SpawnFromCurrentPreset",
    "CRound__SpawnConfiguredProjectile",
    "CRound__ArmProjectileAndSpawnTrailEffect",
    BACKUP,
    "weapon_fire_breaks_stealth",
    "exact CBattleEngine::WeaponFired",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime weapon behavior proven",
    "runtime projectile behavior proven",
    "runtime stealth behavior proven",
    "weapon_fire_breaks_stealth proven",
    "cbattleengine::weaponfired proven",
    "rebuild parity proven",
    "exact layout proven",
    "source identity proven",
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


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


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
        "pre-metadata.tsv": 19,
        "pre-tags.tsv": 19,
        "pre-xrefs.tsv": 51,
        "pre-instructions.tsv": 3272,
        "pre-decompile/index.tsv": 19,
        "post-metadata.tsv": 19,
        "post-tags.tsv": 19,
        "post-xrefs.tsv": 51,
        "post-instructions.tsv": 3272,
        "post-decompile/index.tsv": 19,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(WAVE_TAG_TARGETS.get(address, set()).issubset(actual_tags), f"Wave1160 tags missing at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    actual_ref_types = {row.get("ref_type") for row in xrefs}
    require(actual_ref_types == {"UNCONDITIONAL_CALL", "DATA"}, f"unexpected xref types: {actual_ref_types}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=19 found=19 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=19 missing=0",
        "pre-xrefs.log": "Wrote 51 rows",
        "pre-instructions.log": "Wrote 3272 function-body instruction rows",
        "pre-decompile.log": "targets=19 dumped=19 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=16 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=16 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=19 found=19 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=19 missing=0",
        "post-xrefs.log": "Wrote 51 rows",
        "post-instructions.log": "Wrote 3272 function-body instruction rows",
        "post-decompile.log": "targets=19 dumped=19 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("sourceRoot") == EXPECTED_SOURCE_ROOT, "backup source root mismatch", failures)
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


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(latest.get("wave") == "Wave1160 weapon/projectile targeting current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1160-weapon-projectile-targeting-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 516, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "43.77%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 663, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1160 weapon/projectile targeting current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1160 note mirror mismatch", failures)
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "unit/BattleEngine contract mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    require(
        read_json(PACKAGE_JSON).get("scripts", {}).get("test:wave1160-weapon-projectile-targeting-current-risk-review")
        == r"py -3 tools\wave1160_weapon_projectile_targeting_current_risk_review.py --check",
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
        print("Wave1160 weapon/projectile targeting current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1160 weapon/projectile targeting current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
