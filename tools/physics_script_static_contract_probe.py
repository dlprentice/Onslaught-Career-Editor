#!/usr/bin/env python3
"""Validate the PhysicsScript static contract surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "physics_script_static_contract_wave1103_2026-06-04.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
CPHYSICS = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScript.cpp.md"
STATEMENTS = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
PACKAGE_JSON = ROOT / "package.json"


CONTRACT_TOKENS = (
    "PhysicsScript Static Contract",
    "physics-script-static-contract-wave1103",
    "0x0042e880 CPhysicsScript__Create",
    "0x0042e950 CPhysicsScript__Load",
    "0x0042eb90 CPhysicsScript__CreateStatement",
    "0x0066e99c g_pPhysicsScript",
    "0x0062568c",
    "0x00625818",
    "0x0042f2b0 CUnitStatement__LoadFromMemBuffer",
    "0x00431a10 CPhysicsHazardValueList__LoadFromMemBuffer",
    "CPhysicsScriptStatements__CreateStatementType2",
    "CPhysicsScriptStatements__CreateStatementType10",
    "0x0042ede0 CUnitStatement__CreateUnitAndRecurse",
    "CStatementChain__InvokeVFunc04OnNodes",
    "DAT_008553fc",
    "DAT_008553f4",
    "DAT_008553f8",
    "DAT_00855400",
    "DAT_00855404",
    "DAT_00855408",
    "CDXMemoryManager__Free",
    "DAT_009c3df0",
    "0x00549220",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260531-211749_post_wave1019_physics_script_manager_lifecycle_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260601-100128_post_wave1043_physics_statement_load_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260601-124915_post_wave1047_physics_statement_create_recurse_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260607-005927_post_wave1203_physics_script_registry_apply_residual_current_risk_review_verified",
    "6411/6411 = 100.00%",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "physics-script-schema-parser-proof-plan.md",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "Runtime PhysicsScript behavior",
    "Serialized physics-script file-format completeness",
    "rebuild parity",
)

OVERCLAIM_TOKENS = (
    "runtime physicsscript behavior proven",
    "serialized physics-script file-format completeness proven",
    "rebuild parity proven",
    "exact layouts proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_contract(failures: list[str]) -> None:
    text = read_text(CONTRACT)
    for token in CONTRACT_TOKENS:
        require(contains_token(text, token), f"contract missing token: {token}", failures)
    for bad in OVERCLAIM_TOKENS:
        require(bad not in text.lower(), f"contract overclaim token present: {bad}", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    for token in (
        "PhysicsScript Static Contract Wave1103 Readiness Note",
        "physics-script-static-contract-wave1103",
        "no Ghidra mutation",
        "no executable-byte change",
        "0x0042e880 CPhysicsScript__Create",
        "0x00431a10 CPhysicsHazardValueList__LoadFromMemBuffer",
        "DAT_008553fc",
        "DAT_008553f4",
        "6410/6410 = 100.00%",
        "1560/1560 = 100.00%",
        "Runtime PhysicsScript behavior",
        "Serialized physics-script file-format completeness",
        "Rebuild parity",
    ):
        require(contains_token(text, token), f"readiness missing token: {token}", failures)
    require("6411/6411 = 100.00%" not in text, "historical Wave1103 readiness should not be rewritten to current counters", failures)


def check_navigation(failures: list[str]) -> None:
    docs = {
        "mapped-systems.md": read_text(MAPPED_SYSTEMS),
        "_index.md": read_text(INDEX),
        "RE-INDEX.md": read_text(RE_INDEX),
        "static-reaudit-campaign.md": read_text(CAMPAIGN),
        "CPhysicsScript.cpp.md": read_text(CPHYSICS),
        "CPhysicsScriptStatements.cpp.md": read_text(STATEMENTS),
    }
    for name, text in docs.items():
        require("physics-script-static-contract.md" in text, f"{name} missing contract link token", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"{name} overclaim token present: {bad}", failures)

    mapped = docs["mapped-systems.md"]
    require(
        "Latest static contract consolidation: Wave1103" in mapped
        or "Current static contract consolidation: Wave1103" in mapped
        or "Prior static contract consolidation: Wave1103" in mapped,
        "mapped systems missing Wave1103 consolidation note",
        failures,
    )
    require("CPhysicsScript__Create" in mapped, "mapped systems missing manager anchor", failures)
    require("runtime PhysicsScript behavior" in mapped, "mapped systems missing runtime boundary", failures)
    require("serialized file-format completeness" in mapped, "mapped systems missing file-format boundary", failures)

    index = docs["_index.md"]
    require("Wave1103 consolidated static contract" in index, "binary index missing Wave1103 contract description", failures)

    re_index = docs["RE-INDEX.md"]
    require("Wave1103 consolidated static PhysicsScript contract" in re_index, "RE index missing Wave1103 contract description", failures)

    campaign = docs["static-reaudit-campaign.md"]
    require(
        "Current continuation: Wave1103" in campaign or "Prior continuation: Wave1103" in campaign,
        "campaign missing Wave1103 current/prior continuation anchor",
        failures,
    )
    require("Prior continuation: Wave1100" in campaign, "campaign missing Wave1100 demotion", failures)
    for token in (
        "CUnitStatement__LoadFromMemBuffer",
        "CPhysicsHazardValueList__LoadFromMemBuffer",
        "DAT_008553fc",
        "DAT_008553f4",
    ):
        require(contains_token(campaign, token), f"campaign missing deep anchor: {token}", failures)

    statements = docs["CPhysicsScriptStatements.cpp.md"]
    require("the adjacent `CCutscene` cluster around `0x0043e8e0`" not in statements, "stale PhysicsScriptStatements remaining-work queue head remains", failures)


def check_mirror(failures: list[str]) -> None:
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "PhysicsScript contract lore mirror mismatch", failures)


def check_package_script(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    expected = r"py -3 tools\physics_script_static_contract_probe.py --check"
    require(scripts.get("test:physics-script-static-contract") == expected, "missing package physics contract script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_contract(failures)
    check_readiness(failures)
    check_navigation(failures)
    check_mirror(failures)
    check_package_script(failures)

    if failures:
        print("PhysicsScript static contract probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript static contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
