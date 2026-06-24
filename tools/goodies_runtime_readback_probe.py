#!/usr/bin/env python3
"""Public-safe read-back probe for Goodies runtime/static RE coverage.

This probe records token presence and line numbers across Stuart's source
anchors and existing retail-binary function documentation. It does not launch
the game, read or write BEA.exe directly, mutate a Ghidra project, or apply a
rename map.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-runtime-readback"
    / "current"
    / "goodies-runtime-readback.json"
)


@dataclass(frozen=True)
class TokenGroup:
    key: str
    file: Path
    tokens: tuple[str, ...]
    summary: str


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def line_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def summarize_group(group: TokenGroup) -> dict[str, object]:
    if not group.file.is_file():
        return {
            "key": group.key,
            "status": "FAIL",
            "file": relative(group.file),
            "summary": f"Missing file: {relative(group.file)}",
            "tokens": list(group.tokens),
            "lineHits": {},
            "missingTokens": list(group.tokens),
        }

    hits = line_hits(group.file, group.tokens)
    missing = [token for token, lines in hits.items() if not lines]
    return {
        "key": group.key,
        "status": "PASS" if not missing else "FAIL",
        "file": relative(group.file),
        "summary": group.summary,
        "tokens": list(group.tokens),
        "lineHits": hits,
        "missingTokens": missing,
    }


def build_report() -> dict[str, object]:
    groups = (
        TokenGroup(
            "source_update_goodie_states",
            ROOT / "references" / "Onslaught" / "Career.cpp",
            (
                "void CCareer::UpdateGoodieStates()",
                "TOTAL_C_GRADES(66)",
                "SET_GOODIE_NEW(66)",
                "SET_GOODIE_NEW(71)",
                "SET_GOODIE_NEW(72)",
                "SET_GOODIE_NEW(73)",
                "SET_GOODIE_NEW(78)",
                "mPendingExtraGoodies",
                "SET_GOODIE_INSTRUCTION(0)",
                "SET_GOODIE_INSTRUCTION(71)",
                "SET_GOODIE_INSTRUCTION(72)",
                "SET_GOODIE_INSTRUCTION(73)",
            ),
            "Source anchor for grade, kill, concept-art, 71-73 unlock/instruction, and pending-new Goodie recomputation.",
        ),
        TokenGroup(
            "source_goodie_grid_and_state_helpers",
            ROOT / "references" / "Onslaught" / "FEPGoodies.cpp",
            (
                "static SINT\tget_goodie_number",
                "return((x-8)+66);",
                "return(x+201);",
                "return(x+78);",
                "return CAREER.GetGoodieState(num);",
                "CAREER.SetGoodieState(get_goodie_number(x, y), s);",
            ),
            "Source anchor for the Goodies wall row/column mapping and frontend state get/set helpers.",
        ),
        TokenGroup(
            "source_goodies_71_73_reachability",
            ROOT / "references" / "Onslaught" / "FEPGoodies.cpp",
            (
                "CGoodieData(GOODIES_71),",
                "CGoodieData(GOODIES_72),",
                "CGoodieData(GOODIES_73),",
                "case 71:\treturn CTEXTURE::GetTextureByName",
                "else if (goodie_num<=73)",
                "int goodie_number = get_goodie_number(mCX, mCY);",
                "if (goodienum == -1)",
                "//#define STRESS_TEST_GOODIES",
            ),
            "Source anchor showing 71-73 have data/type/texture support while the ordinary frontend path still selects coordinates through get_goodie_number.",
        ),
        TokenGroup(
            "source_fmv_unlock_path",
            ROOT / "references" / "Onslaught" / "Game.cpp",
            (
                "void\tCGame::RunIntroFMV()",
                "void\tCGame::RunOutroFMV()",
                "int fmvgn=fmv+200;",
                "if (fmv==33)",
                "CAREER.SetGoodieState(fmvgn,GS_NEW);",
                "CAREER.mPendingExtraGoodies ++;",
                "FMV.PlayFullscreen(foo, FALSE, localise);",
            ),
            "Source anchor for intro/outro FMV playback unlocking Goodies 201-232.",
        ),
        TokenGroup(
            "retail_update_goodie_states_doc",
            ROOT
            / "reverse-engineering"
            / "binary-analysis"
            / "functions"
            / "Career.cpp"
            / "CCareer__UpdateGoodieStates.md",
            (
                "0x0041c470",
                "Verified vs Source:** Yes",
                "TOTAL_S_GRADES",
                "[CCareer__GetAndResetGoodieNewCount]",
                "& 0x00FFFFFF",
            ),
            "Retail function doc anchor for Goodies recomputation and kill-counter masking.",
        ),
        TokenGroup(
            "retail_fmv_unlock_docs",
            ROOT
            / "reverse-engineering"
            / "binary-analysis"
            / "functions"
            / "game.cpp"
            / "CGame__RunIntroFMV.md",
            (
                "0x0046d890",
                "Renamed, signature set, commented in Ghidra",
                "Unlocks associated cutscene goodie",
                "GS_NEW",
            ),
            "Retail intro-FMV Goodie unlock doc anchor.",
        ),
        TokenGroup(
            "retail_outro_unlock_docs",
            ROOT
            / "reverse-engineering"
            / "binary-analysis"
            / "functions"
            / "game.cpp"
            / "CGame__RunOutroFMV.md",
            (
                "0x0046d9f0",
                "Renamed, signature set, commented in Ghidra",
                "unlocks corresponding goodie state",
                "CGame__RollCredits",
            ),
            "Retail outro-FMV Goodie unlock doc anchor.",
        ),
        TokenGroup(
            "retail_script_goodie_docs",
            ROOT
            / "reverse-engineering"
            / "binary-analysis"
            / "functions"
            / "IScript.cpp.md",
            (
                "0x00533a70",
                "IScript__SetGoodieState",
                "0x00533aa0",
                "IScript__GetGoodieState",
                "index-1",
            ),
            "Retail mission-script Goodie get/set doc anchor.",
        ),
        TokenGroup(
            "retail_frontend_goodies_process_doc",
            ROOT
            / "reverse-engineering"
            / "binary-analysis"
            / "functions"
            / "FEPGoodies.cpp"
            / "CFEPGoodies__Process.md",
            (
                "0x0045d7e0",
                "IsCheatActive(0)",
                "IsCheatActive(5)",
                "0x006798b0",
                "0x006798b4",
                "0x00662564",
                "Partial Field / Branch Read-Back",
                "this + 0x13C",
                "mCurrentGoodyType",
                "mDisplayGoody",
                "Bucket value",
            ),
            "Retail frontend Goodies cheat/display override doc anchor.",
        ),
        TokenGroup(
            "retail_frontend_goodie_loader_docs",
            ROOT
            / "reverse-engineering"
            / "binary-analysis"
            / "functions"
            / "FEPGoodies.cpp"
            / "CFEPGoodies__StartLoadingGoody.md",
            (
                "0x0045c9f0",
                "get_goodie_number(this->mCX, this->mCY)",
                "Computes goody content type bucket",
                "starts async mission-script resource load",
            ),
            "Retail frontend Goodie selection/load doc anchor.",
        ),
        TokenGroup(
            "winui_unlock_requirement_service",
            ROOT
            / "OnslaughtCareerEditor.AppCore"
            / "GoodieUnlockRequirementService.cs",
            (
                "GoodieUnlockRequirementService",
                "ExplicitRules",
                "Earn C or better on 26 campaign missions.",
                "CGame cutscene handlers",
                "GradeRequirement",
            ),
            "WinUI/AppCore service anchor translating current RE unlock knowledge into product-facing copy.",
        ),
        TokenGroup(
            "real_asset_extraction_smoke",
            ROOT
            / "release"
            / "readiness"
            / "real_asset_extraction_smoke_2026-05-07.md",
            (
                "PC resource archives scanned",
                "Goodie resource archives",
                "GDIE",
                "loose textures",
                "loose meshes",
                "Bink",
            ),
            "Read-only real-install asset extraction evidence anchor.",
        ),
        TokenGroup(
            "quick_reference_displayable_ranges",
            ROOT
            / "reverse-engineering"
            / "quick-reference"
            / "save-goodies.md",
            (
                "233 total displayable, indices 0-232",
                "71-73 | Intended source-level image Goodies with shipped texture-only archives (`ca_be_final01`, `ca_be_final02`, `ca_bea_battle_pic`), unlock/instruction hooks, and no known wall coordinate",
                "201-232 | FMV Cutscenes | 32",
                "FMV 232 maps to cutscene file 33",
            ),
            "Quick-reference anchor for corrected displayable range and the 71-73 static classification.",
        ),
        TokenGroup(
            "goodies_asset_matrix_71_73",
            ROOT
            / "release"
            / "readiness"
            / "goodies_asset_matrix_2026-05-07.md",
            (
                "Goodie resources 71-73",
                "3 texture-only",
                "resolved texture-only entries",
                "runtime/non-grid investigation",
            ),
            "Readiness evidence anchor for shipped-but-not-wall-visible Goodies 71-73.",
        ),
        TokenGroup(
            "goodies_wall_visibility_71_73",
            ROOT
            / "release"
            / "readiness"
            / "winui_goodies_wall_visibility_2026-05-07.md",
            (
                "Goodie archives `71-73` exist",
                "resolved texture-only entries",
                "runtime/non-grid path",
                "not look like ordinary visible wall entries",
            ),
            "WinUI/AppCore visibility evidence anchor for Goodies 71-73.",
        ),
    )

    group_reports = [summarize_group(group) for group in groups]
    missing_groups = [group["key"] for group in group_reports if group["status"] != "PASS"]
    return {
        "schema": "goodies-runtime-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "repoRoot": relative(ROOT),
        "status": "PASS" if not missing_groups else "FAIL",
        "summary": {
            "groupCount": len(group_reports),
            "passedGroups": len(group_reports) - len(missing_groups),
            "failedGroups": len(missing_groups),
            "missingGroups": missing_groups,
        },
        "safety": {
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
            "mutatesGhidraProject": False,
            "appliesRenameMap": False,
            "writesPrivateAssetOutputs": False,
        },
        "currentClaims": [
            "Goodie save-state encoding and displayable range are documented.",
            "Default Goodie recomputation has source and retail function-doc anchors.",
            "FMV Goodie unlocks have source and retail function-doc anchors.",
            "Mission-script Goodie get/set has retail function-doc anchors.",
            "Frontend Goodies grid/display/cheat override has source and retail function-doc anchors.",
            "Goodies 71-73 have source/resource/type support but no normal source coordinate reachability.",
            "Actual PC install asset inventory/extraction has bounded read-only evidence.",
        ],
        "notClaimed": [
            "No runtime process was launched in this probe.",
            "No live save recomputation was observed inside a running BEA process in this probe.",
            "No Ghidra names or signatures were changed in this probe.",
            "No hidden/direct runtime selection path for Goodies 71-73 is proven by this probe.",
            "No exhaustive model viewer/runtime Goodies wall replay was performed in this probe.",
        ],
        "groups": group_reports,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when any token group fails.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "groups: "
        f"{report['summary']['passedGroups']}/{report['summary']['groupCount']} passing"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
