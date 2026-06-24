#!/usr/bin/env python3
"""Guard active static re-audit accounting against stale additive progress."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
LEDGER_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
CAMPAIGN_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MEASUREMENT_REGISTER_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
ACCOUNTING_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
ACCOUNTING_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
READINESS = ROOT / "release" / "readiness" / "wave1219_final_score16_current_risk_review_2026-06-07.md"
PACKAGE_JSON = ROOT / "package.json"
README = ROOT / "README.MD"
AGENTS = ROOT / "AGENTS.md"

WAVE911_FOCUSED = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-focused-correction-candidates.tsv"
WAVE911_RISK = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-risk-ranked-functions.tsv"
WAVE1108_BROAD = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.tsv"
WAVE1108_FOCUSED = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"

DENOMINATOR = 1179
WAVE_START = 1109
LATEST_WAVE = 1219
LEGACY_ADDITIVE_THROUGH_WAVE1197 = 885
LEGACY_ADDITIVE_THROUGH_WAVE1198 = 891
LEGACY_ADDITIVE_THROUGH_WAVE1199 = 901
LEGACY_ADDITIVE_THROUGH_WAVE1200 = 1048
LEGACY_ADDITIVE_THROUGH_WAVE1201 = 1073
LEGACY_ADDITIVE_THROUGH_WAVE1202 = 1086
LEGACY_ADDITIVE_THROUGH_WAVE1203 = 1093
LEGACY_ADDITIVE_THROUGH_WAVE1204 = 1102
LEGACY_ADDITIVE_THROUGH_WAVE1205 = 1107
LEGACY_ADDITIVE_THROUGH_WAVE1206 = 1114
LEGACY_ADDITIVE_THROUGH_WAVE1207 = 1120
LEGACY_ADDITIVE_THROUGH_WAVE1208 = 1123
LEGACY_ADDITIVE_THROUGH_WAVE1209 = 1127
LEGACY_ADDITIVE_THROUGH_WAVE1210 = 1133
LEGACY_ADDITIVE_THROUGH_WAVE1211 = 1141
LEGACY_ADDITIVE_THROUGH_WAVE1212 = 1150
LEGACY_ADDITIVE_THROUGH_WAVE1213 = 1156
LEGACY_ADDITIVE_THROUGH_WAVE1214 = 1164
LEGACY_ADDITIVE_THROUGH_WAVE1215 = 1169
LEGACY_ADDITIVE_THROUGH_WAVE1216 = 1176
LEGACY_ADDITIVE_THROUGH_WAVE1217 = 1186
LEGACY_ADDITIVE_THROUGH_WAVE1218 = 1194
LEGACY_ADDITIVE_THROUGH_WAVE1219 = 1210
EXPECTED_UNIQUE_REVIEWED = 1179
EXPECTED_REMAINING = 0
EXPECTED_PERCENT = "100.00%"
EXPECTED_DUPLICATE_OVERCOUNT = 26
EXPECTED_WAVE1145_ARITHMETIC_OVERCOUNT = 5
EXPECTED_COUNTED_ROWS = 1205
EXPECTED_LIVE_FOCUSED = 1117
EXPECTED_LATEST_WAVE_STATUS = "complete static current-risk final score16 tag-only read-back; validation passed"
EXPECTED_ARTIFACT_COMMIT = "99abee208c86fe87b38aa37c00948df23c256f60"
EXPECTED_CLOSEOUT_COMMIT = "831a6984ca9c5b473b3b6fc8a605db3101d83d35"
NON_COUNTING_TARGETS = {
    1139: {
        "0x004074d0",  # CBattleEngine__Gravity: Wave1139 function-boundary recovery, not denominator row.
    },
    1192: {
        "0x004daff0",  # FearGridTrackedObject context row explicitly re-read but not counted.
    },
}

DOC_TOKENS = (
    "static-reaudit-current-risk-ledger.json",
    "unique-address accounting",
    "1179/1179 = 100.00%",
    "remaining active focused work: 0",
    "legacy additive counter is deprecated",
    "1210/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1117",
    "not Wave911 reconstruction",
    "Wave911 is historical-retired/non-reconstructable",
    "812/1408 = 57.67%",
    "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence",
    "16 final score16 current-risk rows",
    "tag-only normalization",
    "updated=16 skipped=0",
    "tags_added=84",
    "final dry updated=0 skipped=16",
    "no rename",
    "no signature change",
    "no comment change",
    "CLine__ctor_copy",
    "CBoat__Init",
    "CBoatGuide__ctor",
    "CFrameTimer__ctor",
    "CDebugMarker__ctor",
    "CEndLevelData__IsAllSecondaryObjectivesComplete",
    "CCollisionSeekingThing__ctor_base",
    "CHLCollisionDetector__ctor_base",
    "COggLoader__readerSubobject_dtor_body",
    "COggLoader__ctor_base",
    "CPlane__Hit_CheckFatalDamageAndDie",
    "CSentinel__Init",
    "SharedUnitAnimation__FindAnimationIndexOrZero",
    "SharedUnitAnimation__PlayAnimationByNameIfPresent",
    "PCLTShell__ctor",
    "COggFileRead__scalar_deleting_dtor",
    "44 xref rows",
    "539 instruction rows",
    "16 decompile rows",
)

REGISTER_TOKENS = (
    "static-reaudit-measurement-register",
    "Metric Authorities",
    "Wave Update Checklist",
    "Anti-Churn Rules",
    "Do not use README prose, old wave paragraphs, scratch files, or subagent reports as active percentages.",
    "Handoff state",
)

STALE_TOKENS = (
    "Current accounting authority: The counters live in `static-reaudit-progress.json`; scratch/subagent artifacts can be partial or stale. Wave1181",
    "Wave1181 is the current accounting authority",
    "latest_airunit_init_current_risk_review",
    "latest_wave\": \"Wave1185 AirUnit Init Current-Risk Review",
    "current_focused_completed\": 783",
    "current_remaining_focused\": 396",
    "8e08e7920a090dd43502dec25e819e0c3d0ee7a7",
    "0b9c173db15aff65f65c514bb690848d0d60e26b",
    "validates Wave1218 artifact/status/pending markers",
    "validates Wave1216 artifact/state/push/no-pending markers",
    "Probe token anchor: Wave1215;",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if not re.fullmatch(r"[0-9a-f]+", value):
        return ""
    return "0x" + value.zfill(8)


def is_address(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"0x[0-9a-fA-F]{6,8}", value.strip()) is not None


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def read_tsv_addresses(path: Path) -> set[str]:
    lines = read_text(path).splitlines()
    if not lines:
        return set()
    header = lines[0].split("\t")
    try:
        idx = header.index("address")
    except ValueError:
        return set()
    addresses: set[str] = set()
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if idx < len(parts):
            address = normalize_address(parts[idx])
            if address:
                addresses.add(address)
    return addresses


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def import_wave_module(path: Path):
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def target_from_row(row: Any) -> str | None:
    if is_address(row):
        return normalize_address(row)
    if isinstance(row, dict):
        for key in ("address", "target", "addr"):
            if is_address(row.get(key)):
                return normalize_address(row[key])
        return None
    if isinstance(row, (list, tuple)):
        for item in row[:2]:
            if is_address(item):
                return normalize_address(item)
    return None


def extract_targets(module: Any) -> list[str]:
    addresses: list[str] = []
    for name in ("TARGETS", "TOP15", "REMAINDER"):
        if not hasattr(module, name):
            continue
        value = getattr(module, name)
        if isinstance(value, dict):
            rows = value.keys()
        else:
            rows = value
        for row in rows:
            address = target_from_row(row)
            if address:
                addresses.append(address)
    for name in ("ADDRESS", "TARGET"):
        if hasattr(module, name) and is_address(getattr(module, name)):
            addresses.append(normalize_address(getattr(module, name)))
    return addresses


def wave_script_paths() -> list[Path]:
    paths: list[Path] = []
    for path in TOOLS.glob("wave*.py"):
        match = re.match(r"wave(\d+)_", path.name)
        if not match:
            continue
        wave = int(match.group(1))
        if WAVE_START <= wave <= LATEST_WAVE:
            paths.append(path)
    return sorted(paths, key=lambda p: int(re.match(r"wave(\d+)_", p.name).group(1)))


def build_ledger() -> dict[str, Any]:
    seen: dict[str, int] = {}
    duplicate_addresses: dict[str, list[int]] = defaultdict(list)
    per_wave: list[dict[str, Any]] = []
    total_counted = 0

    for path in wave_script_paths():
        wave = int(re.match(r"wave(\d+)_", path.name).group(1))
        module = import_wave_module(path)
        addresses = [
            address
            for address in extract_targets(module)
            if address not in NON_COUNTING_TARGETS.get(wave, set())
        ]
        unique_in_wave = list(dict.fromkeys(addresses))
        total_counted += len(unique_in_wave)

        new_addresses = []
        duplicates = []
        for address in unique_in_wave:
            if address in seen:
                duplicates.append(address)
                duplicate_addresses[address].append(wave)
            else:
                seen[address] = wave
                new_addresses.append(address)

        per_wave.append(
            {
                "wave": wave,
                "script": str(path.relative_to(ROOT)).replace("\\", "/"),
                "countedRows": len(unique_in_wave),
                "newUniqueRows": len(new_addresses),
                "duplicateRows": len(duplicates),
                "duplicateAddresses": duplicates,
            }
        )

    duplicate_detail = [
        {
            "address": address,
            "firstWave": seen[address],
            "duplicateWaves": waves,
        }
        for address, waves in sorted(duplicate_addresses.items())
    ]
    unique_reviewed = len(seen)
    remaining = DENOMINATOR - unique_reviewed
    probe_anchor = (
        "Probe token anchor: Wave1219; wave1219-final-score16-current-risk-review; "
        "1179/1179 = 100.00%; 16 final score16 current-risk rows; "
        "CLine__ctor_copy; CBoat__Init; CBoatGuide__ctor; CFrameTimer__ctor; CDebugMarker__ctor; "
        "CEndLevelData__IsAllSecondaryObjectivesComplete; CCollisionSeekingThing__ctor_base; "
        "CHLCollisionDetector__ctor_base; COggLoader__readerSubobject_dtor_body; COggLoader__ctor_base; "
        "CPlane__Hit_CheckFatalDamageAndDie; CSentinel__Init; "
        "SharedUnitAnimation__FindAnimationIndexOrZero; SharedUnitAnimation__PlayAnimationByNameIfPresent; "
        "PCLTShell__ctor; COggFileRead__scalar_deleting_dtor; "
        "6411/6411 = 100.00%; 0 / 0 / 0; 44 xref rows; 539 instruction rows; "
        "16 decompile rows; current focused candidates: 1117; live regenerated current focused candidates: 1117; "
        "remaining active focused work: 0; current risk candidates: 6166; fresh Ghidra export; "
        "tag-only normalization; updated=16 skipped=0; tags_added=84; final dry updated=0 skipped=16; "
        "no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; "
        "unique-address accounting; Codex read-only consults used; no Cursor/Composer; "
        "legacy additive counter is deprecated (`1210/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; "
        "Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; "
        "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; "
        "static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; "
        "continuity denominator; "
        r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified; "
        "wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; "
        "not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference."
    )
    return {
        "schema": "bea-static-current-risk-ledger.v1",
        "lastUpdated": "2026-06-07",
        "authority": "Unique normalized function address, not additive wave prose.",
        "activeDenominator": DENOMINATOR,
        "latestWave": "Wave1219 Final Score16 Current-Risk Review",
        "latestWaveTag": "wave1219-final-score16-current-risk-review",
        "correctedUniqueReviewed": unique_reviewed,
        "correctedUniquePercent": f"{(unique_reviewed / DENOMINATOR) * 100:.2f}%",
        "remainingUnique": remaining,
        "countedRowsThroughWave1219": total_counted,
        "duplicateAddressOvercount": total_counted - unique_reviewed,
        "wave1145ArithmeticOvercount": EXPECTED_WAVE1145_ARITHMETIC_OVERCOUNT,
        "legacyAdditiveThroughWave1197Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1197,
        "legacyAdditiveThroughWave1198Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1198,
        "legacyAdditiveThroughWave1199Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1199,
        "legacyAdditiveThroughWave1200Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1200,
        "legacyAdditiveThroughWave1201Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1201,
        "legacyAdditiveThroughWave1202Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1202,
        "legacyAdditiveThroughWave1203Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1203,
        "legacyAdditiveThroughWave1204Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1204,
        "legacyAdditiveThroughWave1205Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1205,
        "legacyAdditiveThroughWave1206Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1206,
        "legacyAdditiveThroughWave1207Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1207,
        "legacyAdditiveThroughWave1208Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1208,
        "legacyAdditiveThroughWave1209Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1209,
        "legacyAdditiveThroughWave1210Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1210,
        "legacyAdditiveThroughWave1211Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1211,
        "legacyAdditiveThroughWave1212Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1212,
        "legacyAdditiveThroughWave1213Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1213,
        "legacyAdditiveThroughWave1214Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1214,
        "legacyAdditiveThroughWave1215Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1215,
        "legacyAdditiveThroughWave1216Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1216,
        "legacyAdditiveThroughWave1217Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1217,
        "legacyAdditiveThroughWave1218Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1218,
        "legacyAdditiveThroughWave1219Deprecated": LEGACY_ADDITIVE_THROUGH_WAVE1219,
        "liveFocusedCandidatesAfterLatestReview": EXPECTED_LIVE_FOCUSED,
        "nonCountingTargets": {
            str(wave): sorted(addresses)
            for wave, addresses in NON_COUNTING_TARGETS.items()
        },
        "wave911FocusedHistorical": "812/1408 = 57.67%",
        "wave911Status": "historical-retired/non-reconstructable",
        "completionTarget": "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence",
        "probeAnchor": probe_anchor,
        "centralFiles": {
            "progress": "reverse-engineering/binary-analysis/static-reaudit-progress.json",
            "ledger": "reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json",
            "accountingGuard": "reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md",
            "measurementRegister": "reverse-engineering/binary-analysis/static-reaudit-measurement-register.md",
            "systemMap": "reverse-engineering/binary-analysis/mapped-systems.md",
            "campaign": "reverse-engineering/binary-analysis/static-reaudit-campaign.md",
            "riskRank": "reverse-engineering/binary-analysis/wave1108-current-risk-rank.md",
        },
        "perWave": per_wave,
        "duplicateAddresses": duplicate_detail,
    }


def write_ledger() -> None:
    ledger = build_ledger()
    text = json.dumps(ledger, indent=2, sort_keys=False) + "\n"
    LEDGER.write_text(text, encoding="utf-8")
    LEDGER_MIRROR.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_MIRROR.write_text(text, encoding="utf-8")
    print(f"Wrote {LEDGER.relative_to(ROOT)}")
    print(f"Wrote {LEDGER_MIRROR.relative_to(ROOT)}")


def git_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def check_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1219 Final Score16 Current-Risk Review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1219-final-score16-current-risk-review", "latest wave tag mismatch", failures)
    require(latest.get("status") == EXPECTED_LATEST_WAVE_STATUS, "latest wave status mismatch", failures)
    require(latest.get("artifactCommit") == EXPECTED_ARTIFACT_COMMIT, "latest wave artifact commit mismatch", failures)
    expected_commit_fields = {
        "artifactCommit": EXPECTED_ARTIFACT_COMMIT,
        "stateCloseoutCommit": EXPECTED_CLOSEOUT_COMMIT,
    }
    for key, expected in expected_commit_fields.items():
        if not expected.startswith("pending "):
            require("pending" not in str(latest.get(key, "")).lower(), f"latest wave {key} is still pending", failures)
    quality = progress.get("functionQuality", {})
    require(quality.get("totalFunctions") == 6411, "function total mismatch", failures)
    require(quality.get("commentedFunctions") == 6411, "commented total mismatch", failures)
    require(quality.get("commentlessFunctions") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatures") == 0, "undefined signature count mismatch", failures)
    require(quality.get("paramSignatures") == 0, "param_N count mismatch", failures)

    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("accountingMode") == "unique-address-ledger", "accounting mode mismatch", failures)
    require(current.get("currentRiskLedger") == "reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json", "ledger pointer mismatch", failures)
    require(current.get("focusedReviewed") == EXPECTED_UNIQUE_REVIEWED, "corrected focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == EXPECTED_PERCENT, "corrected percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == EXPECTED_REMAINING, "corrected remaining mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == LEGACY_ADDITIVE_THROUGH_WAVE1219, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == EXPECTED_DUPLICATE_OVERCOUNT, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == EXPECTED_WAVE1145_ARITHMETIC_OVERCOUNT, "Wave1145 arithmetic overcount mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == EXPECTED_LIVE_FOCUSED, "live focused count mismatch", failures)
    require(current.get("focusedReviewed") + current.get("remainingFocusedAfterLatestReview") == DENOMINATOR, "reviewed+remaining mismatch", failures)
    require(current.get("isWave911Reconstruction") is False, "Wave1108 reconstruction flag mismatch", failures)
    require(current.get("completionTarget") == "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence", "completion target mismatch", failures)

    wave911 = progress.get("post100Reaudit", {}).get("wave911Focused", {})
    require(wave911.get("status") == "historical-retired/non-reconstructable", "Wave911 status mismatch", failures)
    require(wave911.get("active") is False, "Wave911 active flag mismatch", failures)
    require(wave911.get("completed") == 812, "Wave911 completed mismatch", failures)
    require(wave911.get("total") == 1408, "Wave911 total mismatch", failures)
    require(wave911.get("percent") == "57.67%", "Wave911 percent mismatch", failures)


def check_ledger(failures: list[str]) -> None:
    expected = build_ledger()
    actual = read_json(LEDGER)
    require(actual == expected, "current-risk ledger is not freshly generated from wave probes", failures)
    require(read_text(LEDGER) == read_text(LEDGER_MIRROR), "ledger mirror mismatch", failures)
    require(actual.get("correctedUniqueReviewed") == EXPECTED_UNIQUE_REVIEWED, "ledger unique count mismatch", failures)
    require(actual.get("correctedUniquePercent") == EXPECTED_PERCENT, "ledger percent mismatch", failures)
    require(actual.get("remainingUnique") == EXPECTED_REMAINING, "ledger remaining mismatch", failures)
    require(actual.get("duplicateAddressOvercount") == EXPECTED_DUPLICATE_OVERCOUNT, "ledger duplicate overcount mismatch", failures)
    require(actual.get("wave1145ArithmeticOvercount") == EXPECTED_WAVE1145_ARITHMETIC_OVERCOUNT, "ledger Wave1145 overcount mismatch", failures)
    require(actual.get("countedRowsThroughWave1219") == EXPECTED_COUNTED_ROWS, "ledger counted-row mismatch", failures)


def check_wave911_materialization(failures: list[str]) -> None:
    wave911_focused = read_tsv_addresses(WAVE911_FOCUSED)
    wave911_risk = read_tsv_addresses(WAVE911_RISK)
    wave1108_broad = read_tsv_addresses(WAVE1108_BROAD)
    wave1108_focused = read_tsv_addresses(WAVE1108_FOCUSED)
    require(len(wave911_focused) == 300, "Wave911 focused materialized row count mismatch", failures)
    require(len(wave911_risk) == 500, "Wave911 broad materialized row count mismatch", failures)
    require(len(wave1108_broad) == 6166, "Wave1108 broad row count mismatch", failures)
    require(len(wave1108_focused) == EXPECTED_LIVE_FOCUSED, "Wave1108 focused live row count mismatch", failures)
    require(len(wave911_focused & wave1108_broad) == 300, "Wave911 focused vs Wave1108 broad overlap mismatch", failures)
    require(len(wave911_risk & wave1108_broad) == 500, "Wave911 broad vs Wave1108 broad overlap mismatch", failures)


def check_no_tracked_duplicate_wave1153(failures: list[str]) -> None:
    forbidden = (
        "wave1153-cfastvb-transform-batch-current-risk-review",
        "wave1153_cfastvb_transform_batch_current_risk_review",
        "cfastvb-transform-batch-current-risk-review",
    )
    matches = [path for path in git_files() if any(token in path for token in forbidden)]
    require(not matches, "tracked duplicate Wave1153 CFastVB artifacts exist: " + ", ".join(matches), failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "static-reaudit-accounting-guard.md": read_text(ACCOUNTING_NOTE),
        "wave1219_final_score16_current_risk_review_2026-06-07.md": read_text(READINESS),
        "static-reaudit-campaign.md": read_text(CAMPAIGN),
        "mapped-systems.md": read_text(MAPPED_SYSTEMS),
        "static-reaudit-measurement-register.md": read_text(MEASUREMENT_REGISTER),
        "static-reaudit-progress.json": read_text(PROGRESS),
        "AGENTS.md": read_text(AGENTS),
    }
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        if name == "static-reaudit-measurement-register.md":
            for token in REGISTER_TOKENS:
                require(contains_token(text, token), f"missing register token in {name}: {token}", failures)
            for token in (EXPECTED_ARTIFACT_COMMIT, EXPECTED_CLOSEOUT_COMMIT, "Wave1219 artifact/status/pending markers"):
                require(contains_token(text, token), f"missing register closeout token in {name}: {token}", failures)
        for token in STALE_TOKENS:
            require(token not in text, f"stale accounting token in {name}: {token}", failures)
        require("runtime behavior proven" not in text.lower(), f"overclaim in {name}: runtime behavior proven", failures)
        require("rebuild parity proven" not in text.lower(), f"overclaim in {name}: rebuild parity proven", failures)

    require(
        "static-reaudit-measurement-register.md" in read_text(MAPPED_SYSTEMS),
        "mapped systems missing measurement-register pointer",
        failures,
    )
    require(
        "static-reaudit-measurement-register.md" in read_text(ACCOUNTING_NOTE),
        "accounting guard missing measurement-register pointer",
        failures,
    )
    readme_text = read_text(README)
    require(
        "static-reaudit-measurement-register.md" in readme_text,
        "README missing measurement-register pointer",
        failures,
    )
    for token in ("Current static snapshot after Wave", "Latest completed backup:", "/1179"):
        require(token not in readme_text, f"README duplicates active static metric token: {token}", failures)

    require(read_text(ACCOUNTING_NOTE) == read_text(ACCOUNTING_MIRROR), "accounting guard mirror mismatch", failures)
    require(read_text(CAMPAIGN) == read_text(CAMPAIGN_MIRROR), "campaign mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped systems mirror mismatch", failures)
    require(read_text(MEASUREMENT_REGISTER) == read_text(MEASUREMENT_REGISTER_MIRROR), "measurement register mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:static-reaudit-accounting-guard")
        == r"py -3 tools\static_reaudit_accounting_guard.py --check",
        "missing package script",
        failures,
    )
    require(
        package.get("scripts", {}).get("test:ghidra-static-reaudit-progress")
        == r"py -3 tools\static_reaudit_accounting_guard.py --check",
        "progress probe must delegate to accounting guard",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.add_argument("--write-ledger", action="store_true", help="regenerate unique-address ledger")
    args = parser.parse_args()

    if args.write_ledger:
        write_ledger()
        return 0

    failures: list[str] = []
    check_progress(failures)
    check_ledger(failures)
    check_wave911_materialization(failures)
    check_no_tracked_duplicate_wave1153(failures)
    check_docs(failures)

    if failures:
        print("Static re-audit accounting guard: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Static re-audit accounting guard: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
