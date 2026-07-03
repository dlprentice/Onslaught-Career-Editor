#!/usr/bin/env python3
"""Validate public-safe Wave1200 residual compiler-unwind accounting support."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1200-residual-unwind-current-risk-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1200-residual-unwind-current-risk-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1200_residual_unwind_current_risk_supersession_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-231915_post_wave1200_residual_unwind_current_risk_verified"

DETAILED_SAMPLE_TARGETS = {
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

TARGETS = (
    "0x005d1115",
    "0x005d1be0",
    "0x005d2540",
    "0x005d2560",
    "0x005d2680",
    "0x005d26e0",
    "0x005d27f0",
    "0x005d2930",
    "0x005d29d0",
    "0x005d2a60",
    "0x005d2ad0",
    "0x005d2b2c",
    "0x005d2b60",
    "0x005d2b90",
    "0x005d2c40",
    "0x005d2c53",
    "0x005d2c90",
    "0x005d2e70",
    "0x005d2ec0",
    "0x005d2ed3",
    "0x005d2f00",
    "0x005d2f08",
    "0x005d3140",
    "0x005d3160",
    "0x005d3440",
    "0x005d3460",
    "0x005d3480",
    "0x005d34b0",
    "0x005d34c3",
    "0x005d34f0",
    "0x005d34f8",
    "0x005d3540",
    "0x005d3560",
    "0x005d3b30",
    "0x005d3b50",
    "0x005d3b70",
    "0x005d3b90",
    "0x005d3bd0",
    "0x005d3bf0",
    "0x005d3cc6",
    "0x005d3d5a",
    "0x005d3eeb",
    "0x005d3fe8",
    "0x005d4184",
    "0x005d4250",
    "0x005d45a0",
    "0x005d45dc",
    "0x005d4640",
    "0x005d46c0",
    "0x005d46f0",
    "0x005d4710",
    "0x005d4880",
    "0x005d4948",
    "0x005d4ae0",
    "0x005d4b10",
    "0x005d4ba0",
    "0x005d4c70",
    "0x005d4c90",
    "0x005d4cb0",
    "0x005d4ed0",
    "0x005d5000",
    "0x005d5030",
    "0x005d50b0",
    "0x005d50e0",
    "0x005d5170",
    "0x005d5190",
    "0x005d51d0",
    "0x005d51f8",
    "0x005d5388",
    "0x005d55f0",
    "0x005d5790",
    "0x005d5810",
    "0x005d58a0",
    "0x005d58a8",
    "0x005d58e0",
    "0x005d58e8",
    "0x005d5910",
    "0x005d5c09",
    "0x005d5c30",
    "0x005d5c7c",
    "0x005d5d8e",
    "0x005d5f50",
    "0x005d5f58",
    "0x005d5f80",
    "0x005d5f88",
    "0x005d5fb0",
    "0x005d5fb8",
    "0x005d5fe0",
    "0x005d5fe8",
    "0x005d6010",
    "0x005d6018",
    "0x005d6040",
    "0x005d6048",
    "0x005d6070",
    "0x005d6090",
    "0x005d6098",
    "0x005d60c0",
    "0x005d60c8",
    "0x005d60f0",
    "0x005d60f8",
    "0x005d6120",
    "0x005d6128",
    "0x005d6150",
    "0x005d6158",
    "0x005d6180",
    "0x005d6188",
    "0x005d6298",
    "0x005d6309",
    "0x005d6311",
    "0x005d6346",
    "0x005d634e",
    "0x005d6383",
    "0x005d63a0",
    "0x005d63a8",
    "0x005d63c0",
    "0x005d63c8",
    "0x005d63e0",
    "0x005d63e8",
    "0x005d6c50",
    "0x005d6c70",
    "0x005d6ca6",
    "0x005d6cc0",
    "0x005d6ce0",
    "0x005d7020",
    "0x005d73d9",
    "0x005d73f0",
    "0x005d77c0",
    "0x005d77e0",
    "0x005d7860",
    "0x005d7a80",
    "0x005d7ac0",
    "0x005d7b60",
    "0x005d7e70",
    "0x005d7e78",
    "0x005d7e80",
    "0x005d7e88",
    "0x005d7e90",
    "0x005d7ec0",
    "0x005d7ec8",
    "0x005d7ed0",
    "0x005d7ed8",
    "0x005d7ef0",
    "0x005d7f10",
    "0x005d7f18",
    "0x005d7f20",
    "0x005d7f40",
    "0x005d7f53",
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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def ledger_row_addresses(row: dict) -> tuple[str, ...]:
    return tuple(normalize_address(value) for value in row.get("address", "").split(",") if value.strip())


def check_progress_and_docs(failures: list[str]) -> None:
    require(len(TARGETS) == 147, "embedded Wave1200 target list count mismatch", failures)
    require(len(set(TARGETS)) == 147, "embedded Wave1200 target list contains duplicates", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("accountingMode") == "unique-address-ledger", "accounting mode mismatch", failures)
    require(current.get("currentRiskLedger") == "reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json", "ledger pointer mismatch", failures)
    require(current.get("legacyAdditiveThroughWave1200Deprecated") == 1048, "Wave1200 legacy additive mismatch", failures)
    require(current.get("countedRowsThroughWave1200") == 1043, "Wave1200 counted-row mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)
    require(
        current.get("completionTarget") == "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence",
        "completion target mismatch",
        failures,
    )

    ledger = read_json(LEDGER)
    require(ledger.get("legacyAdditiveThroughWave1200Deprecated") == 1048, "ledger Wave1200 legacy additive mismatch", failures)
    require(ledger.get("duplicateAddressOvercount") == 26, "ledger duplicate overcount mismatch", failures)
    wave1200 = next((row for row in ledger.get("perWave", []) if row.get("wave") == 1200), None)
    require(wave1200 is not None, "ledger missing Wave1200 per-wave row", failures)
    if wave1200 is not None:
        require(wave1200.get("script") == "tools/wave1200_residual_unwind_current_risk_supersession.py", "ledger Wave1200 script mismatch", failures)
        require(wave1200.get("countedRows") == 147, "ledger Wave1200 counted rows mismatch", failures)
        require(wave1200.get("newUniqueRows") == 147, "ledger Wave1200 unique rows mismatch", failures)
        require(wave1200.get("duplicateRows") == 0, "ledger Wave1200 duplicate rows mismatch", failures)
        require(wave1200.get("duplicateAddresses") == [], "ledger Wave1200 duplicate address list mismatch", failures)

    prose_docs = [NOTE, NOTE_MIRROR, READINESS]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1200 note mirror mismatch", failures)
    backlog_text = read_text(BACKLOG)
    for token in ("Wave1200", "function_mutation_ledger.jsonl", "function_mutation_attempt_log.jsonl", "147 residual `Unwind@...` rows"):
        require(contains_token(backlog_text, token), f"missing Wave1200 backlog token: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1200-residual-unwind-current-risk-supersession")
        == r"py -3 tools\wave1200_residual_unwind_current_risk_supersession.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    task = "Wave1200 residual compiler-unwind current-risk supersession"
    ledger_row = next((row for row in ledger_rows if row.get("task") == task), None)
    attempt_row = next((row for row in attempt_rows if row.get("task") == task and row.get("result") == "success"), None)
    require(ledger_row is not None, "missing Wave1200 ledger row", failures)
    require(attempt_row is not None, "missing Wave1200 attempt row", failures)
    if ledger_row is not None:
        require(ledger_row_addresses(ledger_row) == TARGETS, "Wave1200 ledger address list mismatch", failures)
    if attempt_row is not None:
        require(ledger_row_addresses(attempt_row) == TARGETS, "Wave1200 attempt address list mismatch", failures)
        require(attempt_row.get("mode") == "read-only-supersession", "Wave1200 attempt mode mismatch", failures)
        require(attempt_row.get("updated") == 0, "Wave1200 attempt updated count mismatch", failures)
        require(attempt_row.get("skipped") == 147, "Wave1200 attempt skipped count mismatch", failures)
        require(attempt_row.get("missing") == 0, "Wave1200 attempt missing count mismatch", failures)
        require(attempt_row.get("bad") == 0, "Wave1200 attempt bad count mismatch", failures)
        require(attempt_row.get("backup") == BACKUP, "Wave1200 attempt backup mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_progress_and_docs(failures)

    if failures:
        print("Wave1200 residual compiler-unwind public accounting support probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1200 residual compiler-unwind public accounting support probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
