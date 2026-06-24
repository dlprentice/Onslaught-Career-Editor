#!/usr/bin/env python3
"""Check source Goodies model-viewer rules against installed GDIE metadata.

This is a static provenance/alignment probe. It reads Stuart's source and the
local read-only Goodies resource archives, then proves the source `GT_MESH`
Goodie set matches the installed `GDAT` model/gallery kind set. It does not
extract assets, launch the game, patch saves, touch BEA.exe, or mutate Ghidra.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "references" / "Onslaught" / "FEPGoodies.cpp"
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-model-viewer-alignment"
    / "current"
    / "goodies-model-viewer-alignment.json"
)

EXPECTED_IMAGE_EXCEPTIONS_BEFORE_58 = {12, 13, 24, 33, 34, 35}
EXPECTED_SOURCE_MODEL_INDICES = [
    *[index for index in range(8, 58) if index not in EXPECTED_IMAGE_EXCEPTIONS_BEFORE_58],
    76,
]

SOURCE_TOKENS = {
    "typeHackFunction": "static EGoodieType get_goodie_type_hack(SINT goodie_num)",
    "meshRange": "else if (goodie_num<=57)\n\t\treturn(GT_MESH);",
    "developerModel": "else if (goodie_num==76)\n\t\treturn(GT_MESH);",
    "meshLoader": "CMESH *mesh=get_goodie_mesh_hack(number);",
    "meshDeserialize": "mCurrentGoodyMesh=CMESH::Deserialize(c);",
    "meshInteraction": "else if (mCurrentGoodyType == GT_MESH)",
    "meshRender": "CMESHRENDERER::RenderMesh(pos,ori,mCurrentGoodyMesh,NULL,NULL,0,FALSE,0);",
    "manualControlToggle": "case BUTTON_START:\t\t\t\t\tmManualControl=!mManualControl; break;",
    "distanceClamp": "Clamp(mMeshDistance, mCurrentGoodyMesh->mBoundingBox->mRadius, mCurrentGoodyMesh->mBoundingBox->mRadius*3.0f);",
}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_census(resource_root: Path | None) -> dict[str, object]:
    sys.path.insert(0, str((ROOT / "tools").resolve()))
    from goodies_resource_archive_census_probe import DEFAULT_RESOURCE_ROOT, build_report

    return build_report(resource_root or DEFAULT_RESOURCE_ROOT)


def optional_catalog_model_indices(catalog_path: Path) -> list[int] | None:
    if not catalog_path.exists():
        return None
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    return sorted(
        int(row.get("index", -1))
        for row in catalog.get("goodies", [])
        if str(row.get("content_kind", "")).strip().lower() == "model"
    )


def build_report(resource_root: Path | None, catalog_path: Path | None) -> dict[str, object]:
    failures: list[str] = []
    source_text = SOURCE_FILE.read_text(encoding="utf-8", errors="replace")
    source_token_status = {
        key: token in source_text for key, token in SOURCE_TOKENS.items()
    }
    missing_source_tokens = [
        key for key, present in source_token_status.items() if not present
    ]
    if missing_source_tokens:
        failures.append("source model-viewer tokens missing")

    census = load_census(resource_root)
    gdat_model_indices = [
        int(value)
        for value in census["summary"]["indicesByContentKind"].get("1", [])
    ]
    source_model_indices = list(EXPECTED_SOURCE_MODEL_INDICES)
    if source_model_indices != gdat_model_indices:
        failures.append("source GT_MESH indices differ from installed GDAT kind-1 indices")

    catalog_indices: list[int] | None = None
    if catalog_path is not None:
        catalog_indices = optional_catalog_model_indices(catalog_path)
        if catalog_indices is not None and catalog_indices != gdat_model_indices:
            failures.append("catalog Model Goodies differ from installed GDAT kind-1 indices")

    expected_conditions = {
        "sourceTokensPresent": not missing_source_tokens,
        "sourceModelCountIs45": len(source_model_indices) == 45,
        "gdatModelCountIs45": len(gdat_model_indices) == 45,
        "sourceMatchesGdatKind1": source_model_indices == gdat_model_indices,
        "catalogIfPresentMatchesGdatKind1": catalog_indices is None
        or catalog_indices == gdat_model_indices,
    }

    return {
        "schema": "goodies-model-viewer-alignment.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "sourceFile": relative(SOURCE_FILE),
        "sourceTokenStatus": source_token_status,
        "missingSourceTokens": missing_source_tokens,
        "summary": {
            "sourceModelGoodieCount": len(source_model_indices),
            "installedGdatModelGoodieCount": len(gdat_model_indices),
            "catalogModelGoodieCount": None if catalog_indices is None else len(catalog_indices),
            "sourceModelIndices": source_model_indices,
            "installedGdatModelIndices": gdat_model_indices,
            "catalogModelIndices": catalog_indices,
            "expectedConditions": expected_conditions,
        },
        "failures": failures,
        "safety": {
            "stripsAbsolutePaths": True,
            "stripsRawAssetNames": True,
            "extractsAssets": False,
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
            "mutatesInstalledGame": False,
            "mutatesGhidraProject": False,
        },
        "notes": [
            "Source GT_MESH rules are modelled from get_goodie_type_hack and guarded by exact source tokens.",
            "Installed GDAT kind 1 is treated as the model/gallery content family from the Goodies archive census.",
            "This proves static source/resource alignment for model Goodies, not runtime model-viewer behavior or final WinUI textured rendering.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource-root", type=Path)
    parser.add_argument(
        "--catalog",
        type=Path,
        default=ROOT
        / "subagents"
        / "goodie_catalog_probe_2026-05-07"
        / "asset_catalog"
        / "catalog.json",
        help="Optional generated catalog used only if present.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.resource_root, args.catalog)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary = report["summary"]
    print(f"{report['status']}: wrote {args.out.relative_to(ROOT).as_posix()}")
    print(
        "Goodies model alignment: "
        f"source {summary['sourceModelGoodieCount']}, "
        f"installed GDAT {summary['installedGdatModelGoodieCount']}, "
        f"catalog {summary['catalogModelGoodieCount']}"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
