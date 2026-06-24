#!/usr/bin/env python3
"""Validate Wave1200 residual compiler-unwind current-risk supersession artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1200-residual-unwind-current-risk-supersession"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1200-residual-unwind-current-risk-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1200-residual-unwind-current-risk-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1200_residual_unwind_current_risk_supersession_2026-06-06.md"
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
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-231915_post_wave1200_residual_unwind_current_risk_verified"

TARGETS = {
    "0x005d1115": ("Unwind@005d1115", "0x00619f7c", "Wave741", ("BattleEngine.cpp", "CMonitor__Shutdown_Thunk")),
    "0x005d1be0": ("Unwind@005d1be0", "0x0061aa4c", "Wave746", ("CPhysicsScript.cpp", "OID__FreeObject_Callback")),
    "0x005d2540": ("Unwind@005d2540", "0x0061b39c", "Wave750", ("eventmanager.cpp", "CParticleManager__RemoveFromGlobalList_Thunk")),
    "0x005d2560": ("Unwind@005d2560", "0x0061b3c4", "Wave750", ("eventmanager.cpp", "CMonitor__Shutdown")),
    "0x005d2680": ("Unwind@005d2680", "0x0061b504", "Wave750", ("FrontEnd.cpp", "CMonitor__Shutdown_Thunk")),
    "0x005d26e0": ("Unwind@005d26e0", "0x0061b55c", "Wave750", ("FrontEnd.cpp", "CMonitor__Shutdown_Thunk")),
    "0x005d27f0": ("Unwind@005d27f0", "0x0061b65c", "Wave751", ("game.cpp", "CMonitor__Shutdown_Thunk")),
    "0x005d2930": ("Unwind@005d2930", "0x0061b71c", "Wave751", ("game.cpp", "CMonitor__Shutdown_Thunk")),
    "0x005d29d0": ("Unwind@005d29d0", "0x0061b7bc", "Wave751", ("game.cpp", "CMonitor__Shutdown_Thunk")),
    "0x005d2a60": ("Unwind@005d2a60", "0x0061b844", "Wave752", ("GillM.cpp", "CMonitor__Shutdown")),
    "0x005d2ad0": ("Unwind@005d2ad0", "0x0061b8cc", "Wave752", ("GillMHead.cpp", "CMonitor__Shutdown")),
    "0x005d2b2c": ("Unwind@005d2b2c", "0x0061b914", "Wave752", ("GroundAttackAircraft.cpp", "CDXLandscape__FreeObjectCallback")),
    "0x005d2b60": ("Unwind@005d2b60", "0x0061b944", "Wave752", ("GroundAttackAircraft.cpp", "CMonitor__Shutdown")),
    "0x005d2b90": ("Unwind@005d2b90", "0x0061b97c", "Wave752", ("GroundAttackAircraft.cpp", "CMonitor__Shutdown_Thunk")),
    "0x005d2c40": ("Unwind@005d2c40", "0x0061ba0c", "Wave752", ("GroundVehicle.cpp", "CMonitor__Shutdown_Thunk")),
    "0x005d2c53": ("Unwind@005d2c53", "0x0061ba1c", "Wave753", ("post-GroundVehicle", "CUnitAI__FreeOwnedObjects_10_18")),
    "0x005d2c90": ("Unwind@005d2c90", "0x0061ba6c", "Wave753", ("post-GroundVehicle", "CMonitor__Shutdown_Thunk")),
    "0x005d2e70": ("Unwind@005d2e70", "0x0061bc2c", "Wave753", ("Infantry.cpp", "CMonitor__Shutdown")),
    "0x005d2ec0": ("Unwind@005d2ec0", "0x0061bc8c", "Wave754", ("monitor cleanup", "CMonitor__Shutdown_Thunk")),
    "0x005d2ed3": ("Unwind@005d2ed3", "0x0061bc9c", "Wave754", ("UnitAI cleanup", "CUnitAI__FreeOwnedObjects_10_18")),
    "0x005d2f00": ("Unwind@005d2f00", "0x0061bccc", "Wave754", ("monitor cleanup", "CMonitor__Shutdown_Thunk")),
    "0x005d2f08": ("Unwind@005d2f08", "0x0061bcd4", "Wave754", ("UnitAI cleanup", "CUnitAI__FreeOwnedObjects_10_18")),
    "0x005d3140": ("Unwind@005d3140", "0x0061be54", "Wave755", ("monitor cleanup", "CMonitor__Shutdown_Thunk")),
    "0x005d3160": ("Unwind@005d3160", "0x0061be7c", "Wave755", ("monitor cleanup", "CMonitor__Shutdown_Thunk")),
    "0x005d3440": ("Unwind@005d3440", "0x0061c174", "Wave756", ("particle-manager", "CParticleManager__RemoveFromGlobalList_Thunk")),
}
DETAILED_SAMPLE_TARGETS = TARGETS
TARGETS = tuple(
    line.strip().lower()
    for line in (BASE / "targets.txt").read_text(encoding="ascii").splitlines()
    if line.strip()
)

DOC_TOKENS = (
    "Wave1200",
    "wave1200-residual-unwind-current-risk-supersession",
    "147 residual compiler-unwind current-risk rows",
    "1017/1179 = 86.26%",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "remaining active focused work: 162",
    "legacy additive counter is deprecated",
    "1048/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only supersession",
    "no rename",
    "no signature change",
    "no comment change",
    "no tag change",
    "no function-boundary change",
    "no executable-byte change",
    "0x005d1115 Unwind@005d1115",
    "0x005d3440 Unwind@005d3440",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "147 xref rows",
    "348 instruction rows",
    "147 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime cleanup behavior proven",
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
        "pre-metadata.tsv": 147,
        "pre-tags.tsv": 147,
        "pre-xrefs.tsv": 147,
        "pre-instructions.tsv": 348,
        "pre-decompile/index.tsv": 147,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "pre-xrefs.tsv")}

    require(len(TARGETS) == 147, "target list count mismatch", failures)
    for address in TARGETS:
        name = f"Unwind@{address[2:]}"
        signature = f"void __cdecl {name}(void)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Static retail Ghidra metadata/decompile/xref evidence only", "remain unproven"):
                require(token in comment, f"missing common comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in ("static-reaudit", "compiler-unwind", "scope-table", "comment-hardened", "signature-hardened", "retail-binary-evidence"):
                require(token in actual, f"missing tag at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref row for {address}", failures)
        if xref is not None:
            require(xref.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=147 found=147 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=147 missing=0",
        "pre-xrefs.log": "Wrote 147 rows",
        "pre-instructions.log": "Wrote 348 function-body instruction rows",
        "pre-decompile.log": "targets=147 dumped=147 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
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
    require(current.get("focusedReviewed") == 1017, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "86.26%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 162, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 1048, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1017, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "86.26%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 162, "ledger remaining mismatch", failures)
    require(ledger.get("countedRowsThroughWave1200") == 1043, "ledger counted row mismatch", failures)

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
        PROGRESS,
        LEDGER,
        ACCOUNTING,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1200 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1200-residual-unwind-current-risk-supersession")
        == r"py -3 tools\wave1200_residual_unwind_current_risk_supersession.py --check",
        "missing package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    task = "Wave1200 residual compiler-unwind current-risk supersession"
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1200 ledger row", failures)
    require(any(row.get("task") == task and row.get("result") == "success" for row in attempt_rows), "missing Wave1200 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1200 residual compiler-unwind current-risk supersession probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1200 residual compiler-unwind current-risk supersession probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
