#!/usr/bin/env python3
"""Validate Wave1166 CMapWho / CHeightField spatial-query read-only evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1166-cmapwho-heightfield-spatial-query-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1166-cmapwho-heightfield-spatial-query-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1166-cmapwho-heightfield-spatial-query-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1166_cmapwho_heightfield_spatial_query_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
HEIGHTFIELD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HeightField.cpp" / "_index.md"
MAPWHO_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mapwho.cpp" / "_index.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-043614_post_wave1166_cmapwho_heightfield_spatial_query_current_risk_review_verified"

TARGETS = {
    "0x00491060": "CHeightField__DeserializeMapAndInitResources",
    "0x00490e30": "CHeightField__BuildCellMinMaxHeightTable",
    "0x00490a40": "CHeightField__TraceLineAgainstHeightfield",
    "0x00491930": "CMapWho__Destroy",
    "0x004919b0": "CMapWho__Init",
    "0x00491c50": "CMapWho__GetLevelForRadius",
    "0x00491cd0": "CMapWho__AddEntry",
    "0x00491d20": "CMapWho__RemoveEntry",
    "0x00491ea0": "CMapWho__GetFirstEntryWithinRadius",
    "0x00492020": "CMapWho__GetNextEntryWithinRadius",
    "0x00492110": "CMapWho__GetFirstEntryWithinLine",
    "0x004922f0": "CMapWho__SetupLineLevel",
    "0x004924b0": "CMapWho__AdvanceLineIterator",
    "0x004925a0": "CMapWho__GetNextEntryWithinLine",
    "0x00492670": "CMapWho__WorldToSector",
    "0x004926e0": "CMapWho__Sort",
    "0x00492ba0": "CMapWhoEntry__SetPosition",
    "0x00492c70": "CMapWhoEntry__RemoveFromMap",
    "0x00492c90": "CMapWhoEntry__GetOwner",
    "0x00492ca0": "CMapWhoEntry__UpdatePosition",
}

SIGNATURE_TOKENS = {
    "0x00491060": "void __thiscall CHeightField__DeserializeMapAndInitResources",
    "0x00490e30": "void __fastcall CHeightField__BuildCellMinMaxHeightTable",
    "0x00490a40": "int __thiscall CHeightField__TraceLineAgainstHeightfield",
    "0x00491ea0": "void * __thiscall CMapWho__GetFirstEntryWithinRadius",
    "0x00492110": "void * __thiscall CMapWho__GetFirstEntryWithinLine",
    "0x00492670": "void * __thiscall CMapWho__WorldToSector",
    "0x00492ba0": "void __thiscall CMapWhoEntry__SetPosition",
    "0x00492c90": "void * __fastcall CMapWhoEntry__GetOwner",
}

TAG_TOKENS = {
    "0x00491060": ("heightfield", "map-resource-wave426", "terrain-heightfield"),
    "0x00490e30": ("heightfield", "map-resource-wave426", "minmax-table"),
    "0x00490a40": ("heightfield", "map-resource-wave426", "line-trace"),
    "0x00491930": ("mapwho-wave428", "spatial-query"),
    "0x004919b0": ("mapwho-wave428", "quadtree-levels"),
    "0x00491ea0": ("mapwho-wave428", "radius-query"),
    "0x00492110": ("mapwho-wave429", "line-query"),
    "0x00492670": ("mapwho-wave429", "sector-conversion"),
    "0x00492ba0": ("mapwho-wave429", "entry-position"),
    "0x00492c90": ("mapwho-wave429", "entry-owner"),
}

COMMENT_TOKENS = {
    "0x00491060": ("Wave426", "MAP.Deserialize"),
    "0x00490e30": ("Wave426", "min/max"),
    "0x00490a40": ("Wave426", "line, hit_out"),
    "0x00491930": ("Wave428", "destroy"),
    "0x004919b0": ("Wave428", "allocates five level arrays"),
    "0x00491ea0": ("Wave428", "radius"),
    "0x00492110": ("Wave429", "line_start"),
    "0x00492670": ("Wave429", "sector_coord"),
    "0x00492ba0": ("Wave429", "position, owner"),
    "0x00492c90": ("Wave429", "entry - 0x0c"),
}

DOC_TOKENS = (
    "Wave1166",
    "wave1166-cmapwho-heightfield-spatial-query-current-risk-review",
    "624/1179 = 52.93%",
    "20 CMapWho / CHeightField spatial-query current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 555",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consult used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "109 xref rows",
    "1651 instruction rows",
    "CHeightField__TraceLineAgainstHeightfield",
    "CMapWho__GetFirstEntryWithinRadius",
    "CMapWho__GetFirstEntryWithinLine",
    "CMapWho__WorldToSector",
    "CMapWhoEntry__SetPosition",
    "CMapWhoEntry__GetOwner",
    "CWorld__FindFirstThingToHitLine",
    "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime spatial-query behavior proven",
    "runtime terrain collision proven",
    "line-of-sight proven",
    "auto-aim proven",
    "hlcollision behavior proven",
    "debug rendering proven",
    "exact cmapwho layout proven",
    "exact cmapwhoentry layout proven",
    "exact cheightfield layout proven",
    "source-body identity proven",
    "rebuild parity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 20,
        "pre-tags.tsv": 20,
        "pre-xrefs.tsv": 109,
        "pre-instructions.tsv": 1651,
        "pre-decompile/index.tsv": 20,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}

    for address, name in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            if address in SIGNATURE_TOKENS:
                require(row.get("signature", "").startswith(SIGNATURE_TOKENS[address]), f"signature mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in COMMENT_TOKENS.get(address, ()):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for tag in ("static-reaudit", "retail-binary-evidence", "comment-hardened"):
                require(tag in actual_tags, f"missing common tag at {address}: {tag}", failures)
            for tag in TAG_TOKENS.get(address, ()):
                require(tag in actual_tags, f"missing tag at {address}: {tag}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row at {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_text = read_text(BASE / "pre-xrefs.tsv")
    for token in (
        "CStaticShadows__BuildShadowMaps",
        "CCarverAI__CheckNearbyEnemies",
        "CWorld__FindFirstThingToHitLine",
        "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
        "CRepairPadAI__VFunc_11_UpdateDockCandidateReader",
        "CRound__FindNearbyHostileWithinProjectileRadius",
        "CSpawnerThng__IsSpawnPositionClear",
    ):
        require(token in xref_text, f"missing xref caller token: {token}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=20 found=20 missing=0",
        "pre-tags.log": "rows=20 missing=0",
        "pre-xrefs.log": "Wrote 109 rows",
        "pre-instructions.log": "Wrote 1651 function-body instruction rows",
        "pre-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 176032647, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1166 CMapWho / CHeightField spatial-query current-risk review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1166-cmapwho-heightfield-spatial-query-current-risk-review", "latest progress tag mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 624, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "52.93%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 555, "remaining focused mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        HEIGHTFIELD_DOC,
        MAPWHO_DOC,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1166 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1166-cmapwho-heightfield-spatial-query-current-risk-review")
        == r"py -3 tools\wave1166_cmapwho_heightfield_spatial_query_current_risk_review.py --check",
        "missing Wave1166 package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_progress(failures)
    check_docs(failures)
    if failures:
        print("Wave1166 CMapWho / CHeightField spatial-query probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1166 CMapWho / CHeightField spatial-query probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
