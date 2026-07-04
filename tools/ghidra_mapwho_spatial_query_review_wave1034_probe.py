#!/usr/bin/env python3
"""Validate Wave1034 MapWho spatial-query read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1034-mapwho-spatial-query-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_mapwho_spatial_query_review_wave1034_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1034_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
MAPWHO_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mapwho.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-054844_post_wave1034_mapwho_spatial_query_review_verified"

TARGETS = {
    "0x00491900": ("CMapWhoEntry__Init", "void __fastcall CMapWhoEntry__Init(void * entry)", "mapwho-wave428"),
    "0x00491930": ("CMapWho__Destroy", "void __fastcall CMapWho__Destroy(void * this)", "mapwho-wave428"),
    "0x004919b0": ("CMapWho__Init", "void __fastcall CMapWho__Init(void * this)", "mapwho-wave428"),
    "0x00491c50": ("CMapWho__GetLevelForRadius", "int __thiscall CMapWho__GetLevelForRadius(void * this, float radius)", "mapwho-wave428"),
    "0x00491cd0": ("CMapWho__AddEntry", "void __thiscall CMapWho__AddEntry(void * this, void * entry)", "mapwho-wave428"),
    "0x00491d20": ("CMapWho__RemoveEntry", "void __thiscall CMapWho__RemoveEntry(void * this, void * entry)", "mapwho-wave428"),
    "0x00491d80": ("CMapWho__SetIteratorFromSectorHead", "void * __thiscall CMapWho__SetIteratorFromSectorHead(void * this, void * sector_entry)", "mapwho-wave428"),
    "0x00491d90": ("CMapWho__AdvanceIteratorAndGetCurrent", "void * __fastcall CMapWho__AdvanceIteratorAndGetCurrent(void * this)", "mapwho-wave428"),
    "0x00491da0": ("CMapWho__IsSectorCoordInBounds", "int __stdcall CMapWho__IsSectorCoordInBounds(void * sector_coord)", "mapwho-wave428"),
    "0x00491df0": ("CMapWho__SetupNextRadiusLevel", "int __fastcall CMapWho__SetupNextRadiusLevel(void * this)", "mapwho-wave428"),
    "0x00491ea0": ("CMapWho__GetFirstEntryWithinRadius", "void * __thiscall CMapWho__GetFirstEntryWithinRadius(void * this, float query_x, float query_y, float query_z, float query_w, float radius)", "mapwho-wave428"),
    "0x00492020": ("CMapWho__GetNextEntryWithinRadius", "void * __fastcall CMapWho__GetNextEntryWithinRadius(void * this)", "mapwho-wave428"),
    "0x00492110": ("CMapWho__GetFirstEntryWithinLine", "void * __thiscall CMapWho__GetFirstEntryWithinLine(void * this, float line_start_x, float line_start_y, float line_start_z, float line_start_w, float line_end_x, float line_end_y, float line_end_z, float line_end_w)", "mapwho-wave429"),
    "0x004922f0": ("CMapWho__SetupLineLevel", "int __fastcall CMapWho__SetupLineLevel(void * this)", "mapwho-wave429"),
    "0x004924b0": ("CMapWho__AdvanceLineIterator", "int __fastcall CMapWho__AdvanceLineIterator(void * this)", "mapwho-wave429"),
    "0x004925a0": ("CMapWho__GetNextEntryWithinLine", "void * __fastcall CMapWho__GetNextEntryWithinLine(void * this)", "mapwho-wave429"),
    "0x00492670": ("CMapWho__WorldToSector", "void * __thiscall CMapWho__WorldToSector(void * this, void * sector_coord, void * position, int level)", "mapwho-wave429"),
    "0x004926e0": ("CMapWho__Sort", "void __fastcall CMapWho__Sort(void * this)", "mapwho-wave429"),
    "0x00492860": ("CMapWho__DebugDrawSector", "void __thiscall CMapWho__DebugDrawSector(void * this, int packed_sector_coord, int level)", "mapwho-wave429"),
    "0x00492950": ("CMapWho__DebugDraw", "void __fastcall CMapWho__DebugDraw(void * this)", "mapwho-wave429"),
    "0x00492ba0": ("CMapWhoEntry__SetPosition", "void __thiscall CMapWhoEntry__SetPosition(void * this, void * position, void * owner, float explicit_radius)", "mapwho-wave429"),
    "0x00492c60": ("CMapWhoEntry__Invalidate", "void __fastcall CMapWhoEntry__Invalidate(void * entry)", "mapwho-wave429"),
    "0x00492c70": ("CMapWhoEntry__RemoveFromMap", "void __fastcall CMapWhoEntry__RemoveFromMap(void * entry)", "mapwho-wave429"),
    "0x00492c90": ("CMapWhoEntry__GetOwner", "void * __fastcall CMapWhoEntry__GetOwner(void * entry)", "mapwho-wave429"),
    "0x00492ca0": ("CMapWhoEntry__UpdatePosition", "int __thiscall CMapWhoEntry__UpdatePosition(void * this, void * position)", "mapwho-wave429"),
}

DOC_TOKENS = (
    "Wave1034",
    "mapwho-spatial-query-review-wave1034",
    "0x00491900 CMapWhoEntry__Init",
    "0x00491d80 CMapWho__SetIteratorFromSectorHead",
    "0x00491ea0 CMapWho__GetFirstEntryWithinRadius",
    "0x00492110 CMapWho__GetFirstEntryWithinLine",
    "0x00492670 CMapWho__WorldToSector",
    "0x00492860 CMapWho__DebugDrawSector",
    "0x00492ba0 CMapWhoEntry__SetPosition",
    "0x00492c90 CMapWhoEntry__GetOwner",
    "660/1408 = 46.88%",
    "889/1493 = 59.54%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime spatial-query behavior proven",
    "runtime collision behavior proven",
    "runtime render behavior proven",
    "runtime ai targeting behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 25,
        "tags.tsv": 25,
        "xrefs.tsv": 119,
        "instructions.tsv": 1538,
        "decompile/index.tsv": 25,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}

    for address, (name, signature, wave_tag) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Static retail evidence only" in row.get("comment", ""), f"missing static evidence boundary at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            require("static-reaudit" in tag_text, f"missing static-reaudit tag at {address}", failures)
            require(wave_tag in tag_text, f"missing original MapWho wave tag at {address}: {wave_tag}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = read_text(BASE / "xrefs.tsv")
    for token in (
        "CBattleEngine__HandleAutoAim",
        "CUnitAI__IsCachedAnchorPointValid",
        "CRepairPadAI__VFunc_11_UpdateDockCandidateReader",
        "CWorld__FindFirstThingToHitLine",
        "CDXTrees__BuildTreeGeometry",
        "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
        "CDXEngine__Render",
        "CThing__Init",
        "CActor__Move",
    ):
        require(token in xrefs, f"missing xref caller token: {token}", failures)

    instructions = read_text(BASE / "instructions.tsv")
    for token in ("RET\t0x14", "RET\t0x20", "RET\t0xc", "RET\t0x8", "CMapWhoEntry__GetOwner"):
        require(token in instructions, f"missing instruction token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=25 found=25 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "xrefs.log": "Wrote 119 rows",
        "instructions.log": "Wrote 1538 function-body instruction rows",
        "decompile.log": "targets=25 dumped=25 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "failed=1", "missing=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash-diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        MAPWHO_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIMS:
            require(token not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-mapwho-spatial-query-review-wave1034")
        == r"py -3 tools\ghidra_mapwho_spatial_query_review_wave1034_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1034-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1034 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1034 MapWho spatial query review" for row in ledger), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1034 MapWho spatial query review" and row.get("attempt_id") == 20616 for row in attempts),
        "missing attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1034 MapWho spatial-query review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1034 MapWho spatial-query review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
