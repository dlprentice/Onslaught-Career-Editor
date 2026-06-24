#!/usr/bin/env python3
"""Validate Wave1122 HLCollisionDetector current-risk review."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from pathlib import Path

import wave1108_current_risk_rank
import wave1121_mixed_score24_current_risk_review as wave1121


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1122-hlcollisiondetector-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1122-hlcollisiondetector-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1122-hlcollisiondetector-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1122_hlcollisiondetector_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

HLCOLLISION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HLCollisionDetector.cpp" / "_index.md"
HLCOLLISION_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "HLCollisionDetector.cpp" / "_index.md"

BACKUP = r"G:\GhidraBackups\BEA_20260605-043957_post_wave1122_hlcollisiondetector_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified"

TARGETS = {
    "0x00480a30": (
        "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
        "void __thiscall CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions(void * this, void * collision_component)",
        ("Wave398", "MapWho", "dispatches collision pairs", "runtime collision behavior"),
        ("0x004269ec", "CCollisionSeekingRound__InitWithSound", "UNCONDITIONAL_CALL"),
        ("CMapWho__WorldToSector", "CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions", "CHLCollisionDetector__DispatchCollisionEventForPair"),
    ),
    "0x00480c90": (
        "CHLCollisionDetector__HandleCollisionEnter",
        "void __thiscall CHLCollisionDetector__HandleCollisionEnter(void * this, void * candidate_component)",
        ("Wave398", "enter-event", "0x100", "scheduled collision"),
        ("0x004812ec", "CHLCollisionDetector__HandleScheduledCollisionEvent", "UNCONDITIONAL_CALL"),
        ("0x100", "CHLCollisionDetector__DispatchCollisionEventForPair"),
    ),
    "0x00480db0": (
        "CHLCollisionDetector__HandleCollisionExit",
        "void __thiscall CHLCollisionDetector__HandleCollisionExit(void * this, void * candidate_component)",
        ("Wave398", "exit-event", "collision-changed flag", "flag"),
        ("0x004811d2", "CHLCollisionDetector__ProcessMapWhoCollisionSweep", "UNCONDITIONAL_CALL"),
        ("CConsole__Printf", "CHLCollisionDetector__DispatchCollisionEventForPair"),
    ),
    "0x00480e10": (
        "CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions",
        "void __thiscall CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions(void * this, void * mapwho_entry_or_quad_node)",
        ("Wave398", "quad", "MapWho", "mutual filters"),
        ("0x00480b30", "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions", "UNCONDITIONAL_CALL"),
        ("CMapWhoEntry__GetOwner", "CThing__GetPersistentCollisionSeekingThing", "CHLCollisionDetector__DispatchCollisionEventForPair"),
    ),
    "0x00480ed0": (
        "CHLCollisionDetector__DispatchCollisionEventForPair",
        "void __thiscall CHLCollisionDetector__DispatchCollisionEventForPair(void * this, void * candidate_component)",
        ("Wave398", "event 2000", "DAT_00672fd0", "EVENT_MANAGER"),
        ("0x00480d94", "CHLCollisionDetector__HandleCollisionEnter", "UNCONDITIONAL_CALL"),
        ("DAT_00672fd0", "CEventManager__AddEvent_AtTime", "2000"),
    ),
    "0x00481060": (
        "CHLCollisionDetector__ProcessMapWhoCollisionSweep",
        "void __thiscall CHLCollisionDetector__ProcessMapWhoCollisionSweep(void * this, void * previous_sector, void * current_sector)",
        ("Wave398", "map/who sweep", "exit callbacks", "newly entered cells"),
        ("0x00426a0d", "CCollisionSeekingRound__ProcessMapWhoCollisionSweep", "UNCONDITIONAL_CALL"),
        ("CHLCollisionDetector__HandleCollisionExit", "CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions"),
    ),
    "0x004812d0": (
        "CHLCollisionDetector__HandleScheduledCollisionEvent",
        "void __thiscall CHLCollisionDetector__HandleScheduledCollisionEvent(void * this, void * event)",
        ("Wave398", "event number 2000", "HandleCollisionEnter", "+0xc"),
        ("0x005dbf78", "<no_function>", "DATA"),
        ("2000", "CHLCollisionDetector__HandleCollisionEnter", "+ 0xc"),
    ),
}

DOC_TOKENS = (
    "Wave1122",
    "wave1122-hlcollisiondetector-current-risk-review",
    "129/1179 = 10.94%",
    "7 rows",
    "current focused candidates: 1179",
    "score-23 HLCollisionDetector cluster",
    "fresh read-only Ghidra export",
    "no mutation",
    "0 / 0 / 0",
    "Wave398",
    "Wave916",
    "Wave1018",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime collision behavior proven",
    "event timing behavior proven",
    "exact detector layout proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def import_probe(path: Path):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_probe_addresses(module) -> set[str]:
    addresses: set[str] = set()
    for attr in ("TOP15", "REMAINDER", "TARGETS"):
        if not hasattr(module, attr):
            continue
        value = getattr(module, attr)
        if isinstance(value, dict):
            addresses.update(normalize_address(address) for address in value)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                if isinstance(item, str):
                    addresses.add(normalize_address(item))
                elif isinstance(item, (list, tuple)) and item and isinstance(item[0], str):
                    addresses.add(normalize_address(item[0]))
    if hasattr(module, "ADDRESS"):
        addresses.add(normalize_address(getattr(module, "ADDRESS")))
    return addresses


def prior_accounted_addresses() -> set[str]:
    accounted = set(wave1121.prior_accounted_addresses())
    accounted.update(wave1121.TARGETS)
    return accounted


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    rows = read_tsv(FOCUSED_TSV)
    accounted = prior_accounted_addresses()
    remaining = [row for row in rows if normalize_address(row.get("address", "")) not in accounted]
    require(len(rows) == 1179, "Wave1108 focused row count mismatch", failures)
    require(len(accounted) == 122, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1057, f"remaining focused count mismatch: {len(remaining)}", failures)
    expected = list(TARGETS)
    window = [normalize_address(row.get("address", "")) for row in remaining[:18]]
    require(all(address in window for address in expected), "Wave1122 targets are not in the next score-23 Wave1108 focused window", failures)
    for row in remaining[:18]:
        require(row.get("score") == "23", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 24,
        "pre-instructions.tsv": 752,
        "pre-decompile/index.tsv": 7,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)
    log_tokens = {
        "pre-metadata.log": "targets=7 found=7 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "pre-xrefs.log": "Wrote 24 rows",
        "pre-instructions.log": "targets=7 missing=0",
        "pre-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING\t", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "pre-metadata.tsv")
    tags = row_map(BASE / "pre-tags.tsv")
    decompile = row_map(BASE / "pre-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    queue = row_map(QUEUE_TSV)

    for address, expected in TARGETS.items():
        name, signature, comment_tokens, xref, decompile_tokens = expected
        for label, rows in (("metadata", metadata), ("current queue", queue)):
            row = rows.get(address)
            require(row is not None, f"{label} missing: {address}", failures)
            if row is not None:
                comment = unescape_tsv(row.get("comment", ""))
                require(row.get("name") == name, f"{label} name mismatch at {address}", failures)
                require(row.get("signature") == signature, f"{label} signature mismatch at {address}", failures)
                require(row.get("status") == "OK", f"{label} status mismatch at {address}", failures)
                for token in comment_tokens:
                    require(token in comment, f"{label} missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("name") == name, f"tag name mismatch at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            for token in ("collision-hl-wave398", "hlcollision", "static-reaudit"):
                require(token in tag_row.get("tags", ""), f"missing tag token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            dec_text = read_text(BASE / "pre-decompile" / f"{address[2:]}_{name}.c")
            for token in decompile_tokens:
                require(token in dec_text, f"missing decompile token at {address}: {token}", failures)

        xref_from, xref_function, xref_type = xref
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(xref_from)
                and row.get("from_function") == xref_function
                and row.get("ref_type") == xref_type
                for row in xrefs
            ),
            f"missing expected xref for {address}",
            failures,
        )


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175672199, "backup byte count mismatch", failures)
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

    for path in (HLCOLLISION_DOC, HLCOLLISION_DOC_MIRROR):
        text = read_text(path)
        for token in ("Wave1122", "0x00480a30 CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions", "0x004812d0 CHLCollisionDetector__HandleScheduledCollisionEvent", BACKUP):
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    commit_pattern = re.compile(r"^(pending Wave1122 artifact commit|[0-9a-f]{40})$")
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1122 HLCollisionDetector current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1122-hlcollisiondetector-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(bool(commit_pattern.match(data["latestWave"].get("artifactCommit", ""))), f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 129, f"{label} focused reviewed mismatch", failures)
        require(current["focusedReviewedPercent"] == "10.94%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1122-hlcollisiondetector-current-risk-review", f"{label} review tag mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1122_hlcollisiondetector_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1122-hlcollisiondetector-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_head(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1122 HLCollisionDetector current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1122 HLCollisionDetector current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
