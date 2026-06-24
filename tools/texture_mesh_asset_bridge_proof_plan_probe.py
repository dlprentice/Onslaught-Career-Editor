#!/usr/bin/env python3
"""Validate the texture/mesh asset bridge proof plan and claim boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"
COPIED_CORPUS_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
LORE_COPIED_CORPUS_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"

PLAN_LINK = "texture-mesh-asset-bridge-proof-plan.md"
RESULT_LINK = "texture-mesh-asset-bridge-copied-corpus-proof.md"

REQUIRED_PLAN_TOKENS = (
    "Texture/Mesh Asset Bridge Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "texture/resource/decode plus mesh asset bridge",
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`",
    "Wave1163 texture/decode current-risk evidence: `17` rows, `68` xref rows, `2779` instruction rows, and `17` decompile rows",
    "JPEG Huffman separate from inflate Huffman",
    "`301` PC resource archives",
    "`232` goodie archives",
    "`TEXT 18857`",
    "`MESH 3492`",
    "`GDIE 232`",
    "`847/847` loose textures",
    "`213/213` loose meshes",
    "`139/139` embedded packed mesh bodies",
    "`4050` catalog rows",
    "`TEXT 601/601`",
    "reference `MESH 209/209`",
    "`GDIE` textures `206/206`",
    "`GDIE` meshes `42/42`",
    "`352/352` model material/texture-binding metadata rows",
    "`213/213` unique model texture sidecar references",
    "copied/app-owned",
    "deterministic manifest and copied-output inventory plan",
    "py -3 tools\\export_asset_catalog.py --self-test",
    "No runtime pixel, GPU upload, visual QA, or parity claim.",
    "texture-mesh-asset-bridge-copied-corpus-proof.md",
    "copied-corpus inventory/export proof only",
)

FORBIDDEN_PHRASES = (
    "runtime texture pixels proven",
    "gpu upload parity proven",
    "visual qa complete",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "exact layouts proven",
    "asset bridge counts prove runtime render correctness",
    "godot is the active product lane",
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
    require(read_text(LORE_COPIED_CORPUS_RESULT) == read_text(COPIED_CORPUS_RESULT), "lore copied-corpus result mirror mismatch", failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (BACKLOG, MAPPED, GAME_ASSETS_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        require(RESULT_LINK in text, f"{path.relative_to(ROOT)} missing copied-corpus result link", failures)
        for phrase in FORBIDDEN_PHRASES:
            require(phrase not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)

    backlog = read_text(BACKLOG)
    require("Active Proof Slice" in backlog, "backlog missing active proof slice section", failures)
    require("copied-corpus inventory/export proof complete, not runtime proof" in backlog, "backlog missing copied-corpus completion boundary", failures)
    require("No runtime pixel, GPU upload, visual QA, or parity claim." in backlog, "backlog missing runtime/visual boundary", failures)

    mapped = read_text(MAPPED)
    require("Completed first proof-planning slice" in mapped, "mapped systems missing completed-slice wording", failures)
    require("not runtime render correctness" in mapped.lower(), "mapped systems missing extraction/runtime boundary", failures)


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
    expected = r"py -3 tools\texture_mesh_asset_bridge_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:texture-mesh-asset-bridge-proof-plan")
    require(actual == expected, "missing package proof-plan script", failures)
    copied_expected = r"py -3 tools\texture_mesh_asset_bridge_copied_corpus_probe.py --check"
    copied_actual = package["scripts"].get("test:texture-mesh-asset-bridge-copied-corpus")
    require(copied_actual == copied_expected, "missing package copied-corpus script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_plan(failures)
    check_front_doors(failures)
    check_progress_unchanged(failures)
    check_package(failures)

    if failures:
        print("Texture/mesh asset bridge proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh asset bridge proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
