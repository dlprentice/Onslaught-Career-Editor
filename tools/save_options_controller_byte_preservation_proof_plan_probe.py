#!/usr/bin/env python3
"""Validate the Save / Options controller byte-preservation proof plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "save_options_controller_byte_preservation_proof_plan_2026-06-08.md"
SAVE_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-static-review-2026-05-26.md"
SAVE_INDEX = ROOT / "reverse-engineering" / "save-file" / "_index.md"
LORE_SAVE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "_index.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "save-options-controller-byte-preservation-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "Save / Options Controller Byte-Preservation Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "save-options-controller-byte-preservation-proof-plan",
    "save-options-static-review-wave902",
    "career-controller-residual-review-wave1044",
    "test:ghidra-career-controller-residual-review-wave1044",
    "wave1212-options-detail-tweak-current-risk-review",
    "10004",
    "0x2714",
    "0x4BD1",
    "true-view base `0x0002`",
    "file_offset = 0x0002 + career_offset",
    "0x23F6",
    "0x24BE-0x26BD",
    "0x26BE-0x2713",
    "N=16",
    "flag=0",
    "flag=1",
    "mControllerConfigurationNum[0/1]",
    "1..4",
    "g_ControlSchemeIndex=0",
    "CCareer__Load",
    "CCareer__Save",
    "CCareer__GetSaveSize",
    "OptionsTail_Write",
    "OptionsTail_Read",
    "CFEPOptions__WriteDefaultOptionsFile",
    "CPauseMenu__ResumeGameAndPersistOptions",
    "copied real `.bes` and `defaultoptions.bea`",
    "Never synthesize a save/options buffer from scratch",
    "DiffCount=0",
    "legacy aligned-view offset write",
    "0x23A4",
    "0x22D4",
    "0x240C",
    "Stop on wrong size, wrong version, unexpected diff outside allowlist",
    "not runtime proof",
)

READINESS_TOKENS = (
    "Save / Options Controller Byte-Preservation Proof Plan Readiness Note",
    "proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a screenshot/capture proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a save synthesis workflow",
    "not a rebuild parity claim",
    "No runtime save/load behavior",
    "runtime defaultoptions boot behavior",
    "runtime menu behavior",
    "runtime controller remap/input behavior",
    "runtime Goodies wall behavior",
)

FORBIDDEN_PHRASES = (
    "runtime save/load behavior proven",
    "runtime defaultoptions boot behavior proven",
    "runtime menu behavior proven",
    "runtime controller remap/input behavior proven",
    "runtime goodies wall behavior proven",
    "exact source-layout parity proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "runtime proof complete",
)

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
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
    for token in (*STATIC_TOKENS, *ANCHOR_TOKENS):
        require(token in text, f"plan missing token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"plan overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"plan leaks public-forbidden token: {token}", failures)
    require(read_text(LORE_PLAN) == text, "lore proof-plan mirror mismatch", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    lower = text.lower()
    for token in (*STATIC_TOKENS, *READINESS_TOKENS):
        require(token in text, f"readiness missing token: {token}", failures)
    for token in (
        "save-options-static-review-wave902",
        "career-controller-residual-review-wave1044",
        "wave1212-options-detail-tweak-current-risk-review",
        "0x24BE-0x26BD",
        "0x26BE-0x2713",
        "N=16",
        "flag=0 applies options",
        "flag=1 skips options",
        "mControllerConfigurationNum 1..4",
        "g_ControlSchemeIndex=0",
    ):
        require(token in text, f"readiness missing anchor token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"readiness overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"readiness leaks public-forbidden token: {token}", failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (SAVE_STATIC, SAVE_INDEX, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        for phrase in FORBIDDEN_PHRASES:
            require(phrase not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)

    require(read_text(SAVE_INDEX) == read_text(LORE_SAVE_INDEX), "save index lore mirror mismatch", failures)
    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Save / options controller byte-preservation proof plan" in backlog, "backlog missing save/options active slice", failures)
    require("copied real `.bes` and `defaultoptions.bea`" in backlog, "backlog missing copied save/options baseline guard", failures)
    require("proof plan complete, not runtime proof" in backlog, "backlog missing save/options proof-plan status", failures)
    require("Do not broaden into runtime save/load, defaultoptions boot, menu/controller input, Goodies wall, patching, visual QA, Godot, broad app runtime proof, or rebuild parity." in backlog, "backlog missing save/options broadening boundary", failures)
    require("Completed Weapon / projectile spawn handoff proof-plan slice" in backlog, "backlog missing completed weapon/projectile slice", failures)

    mapped = read_text(MAPPED)
    require(
        "Completed Save / Options Controller Byte-Preservation Copied-File Proof" in mapped,
        "mapped systems missing completed save/options copied-file proof",
        failures,
    )
    require(
        "save-options-controller-byte-preservation-copied-file-proof.md" in mapped,
        "mapped systems missing save/options copied-file proof link",
        failures,
    )
    require("Completed Weapon / projectile spawn handoff proof-plan slice" in mapped, "mapped systems missing completed weapon/projectile slice", failures)
    require("Save / options / controller" in mapped and PLAN_LINK in mapped, "mapped systems missing save/options row link", failures)


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
    expected = r"py -3 tools\save_options_controller_byte_preservation_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:save-options-controller-byte-preservation-proof-plan")
    require(actual == expected, "missing package Save/options controller proof-plan script", failures)


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
        print("Save / Options controller byte-preservation proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Save / Options controller byte-preservation proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
