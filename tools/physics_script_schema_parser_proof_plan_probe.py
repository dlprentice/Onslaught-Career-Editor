#!/usr/bin/env python3
"""Validate the PhysicsScript schema/parser proof plan and claim boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-schema-parser-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-schema-parser-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "physics_script_schema_parser_proof_plan_2026-06-08.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
LORE_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "physics-script-schema-parser-proof-plan.md"

REQUIRED_PLAN_TOKENS = (
    "PhysicsScript Schema/Parser Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "Schema/parser proof checklist and corpus requirement list",
    "physics-script-static-contract.md",
    "physics-script-static-contract-wave1103",
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "CPhysicsScript__Load",
    "CPhysicsScript__CreateStatement",
    "statement type ids `1..9`",
    "CPhysicsScriptStatements__CreateStatementType2",
    "CPhysicsScriptStatements__CreateStatementType10",
    "CUnitStatement__LoadFromMemBuffer",
    "CPhysicsHazardValueList__LoadFromMemBuffer",
    "CStatementChain__InvokeVFunc04OnNodes",
    "DAT_008553f4",
    "DAT_008553f8",
    "DAT_00855400",
    "DAT_00855404",
    "DAT_00855408",
    "DAT_008553fc",
    "copied/app-owned script/resource evidence",
    "data/default physics.dat",
    "175603",
    "MissionScripts/*.msl",
    "No mission outcome or serialized completeness claim until corpus proof exists.",
    "No runtime PhysicsScript behavior, exact layouts, mission/resource-script outcomes, BEA patching behavior, rebuild parity, or no-noticeable-difference parity claim.",
)

REQUIRED_READINESS_TOKENS = (
    "PhysicsScript Schema/Parser Proof Plan Readiness Note",
    "schema/parser proof checklist complete, not runtime proof",
    "not a new static re-audit wave",
    "0x0042e950 CPhysicsScript__Load",
    "0x0042eb90 CPhysicsScript__CreateStatement",
    "G:\\GhidraBackups\\BEA_20260607-005927_post_wave1203_physics_script_registry_apply_residual_current_risk_review_verified",
    "copied/app-owned script/resource evidence only",
    "MissionScripts/*.msl",
    "No mission outcome or serialized completeness claim until corpus proof exists.",
)

FORBIDDEN_PHRASES = (
    "runtime physicsscript behavior proven",
    "serialized physics-script file-format completeness proven",
    "mission outcomes proven",
    "resource-script outcomes proven",
    "exact layouts proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "parser corpus complete",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_plan(failures: list[str]) -> None:
    text = read_text(PLAN)
    lower = text.lower()
    for token in REQUIRED_PLAN_TOKENS:
        require(token in text, f"plan missing token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"plan overclaims: {phrase}", failures)
    require(read_text(LORE_PLAN) == text, "lore proof-plan mirror mismatch", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    lower = text.lower()
    for token in REQUIRED_READINESS_TOKENS:
        require(token in text, f"readiness missing token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"readiness overclaims: {phrase}", failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (CONTRACT, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        for phrase in FORBIDDEN_PHRASES:
            require(phrase not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)

    require(read_text(CONTRACT) == read_text(LORE_CONTRACT), "PhysicsScript contract lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Active Proof Slice" in backlog, "backlog missing active proof slice section", failures)
    require("PhysicsScript schema/parser" in backlog, "backlog missing PhysicsScript slice", failures)
    require("Schema/parser proof checklist and corpus requirement list" in backlog, "backlog missing schema/parser artifact", failures)
    require("No mission outcome or serialized completeness claim until corpus proof exists." in backlog, "backlog missing mission/completeness boundary", failures)
    require("texture-mesh-material-sidecar-ledger-proof.md" in backlog, "backlog dropped texture/mesh material ledger result", failures)

    mapped = read_text(MAPPED)
    require("Post-Wave1220 Transition Candidates" in mapped, "mapped systems missing transition candidates", failures)
    require("copied-corpus parser/spec slice" in mapped, "mapped systems missing parser/spec wording", failures)


def check_progress_unchanged(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total function mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented function mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)

    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "live focused mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1210, "legacy additive mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)


def check_package(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    expected = r"py -3 tools\physics_script_schema_parser_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:physics-script-schema-parser-proof-plan")
    require(actual == expected, "missing package PhysicsScript schema/parser proof-plan script", failures)
    contract_expected = r"py -3 tools\physics_script_static_contract_probe.py --check"
    contract_actual = package["scripts"].get("test:physics-script-static-contract")
    require(contract_actual == contract_expected, "missing package PhysicsScript static-contract script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_plan(failures)
    check_readiness(failures)
    check_front_doors(failures)
    check_progress_unchanged(failures)
    check_package(failures)

    if failures:
        print("PhysicsScript schema/parser proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript schema/parser proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
