#!/usr/bin/env python3
"""Generate a public-safe material/sidecar ledger from copied-corpus exports."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import model_texture_linkage_probe as linkage  # noqa: E402


DEFAULT_PROOF_ROOT = ROOT / "subagents" / "texture_mesh_asset_bridge_proof_2026-06-08"
DEFAULT_OUT = ROOT / "subagents" / "texture_mesh_material_sidecar_ledger_2026-06-08" / "asset-material-sidecar-ledger.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def file_name(path_text: str) -> str:
    return path_text.replace("\\", "/").rsplit("/", 1)[-1]


def aggregate_tags(rows: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for row in rows:
        tag_counts = row.get("tag_counts", {})
        if not isinstance(tag_counts, dict):
            continue
        for tag, count in tag_counts.items():
            totals[str(tag)] = totals.get(str(tag), 0) + int(count)
    return totals


def lane_export_summary(asset_export_root: Path, lane: str) -> dict[str, int]:
    rows = read_json(asset_export_root / lane / "manifest.json")
    statuses = Counter(row.get("status", "") for row in rows if isinstance(row, dict))
    outputs = [str(row.get("output", "")).replace("\\", "/") for row in rows if isinstance(row, dict)]
    output_counts = Counter(outputs)
    duplicate_groups = {key: value for key, value in output_counts.items() if key and value > 1}
    return {
        "rows": len(rows),
        "succeeded": statuses.get("ok", 0),
        "failed": statuses.get("error", 0),
        "skippedExisting": statuses.get("skipped_existing", 0),
        "uniqueOutputFiles": len([key for key in output_counts if key]),
        "duplicateOutputGroups": len(duplicate_groups),
        "duplicateOutputRows": sum(value - 1 for value in duplicate_groups.values()),
    }


def kind_coverage(catalog: dict[str, Any], catalog_path: Path) -> dict[str, dict[str, int]]:
    texture_stems = linkage.catalog_texture_stems(catalog)
    sidecar_root = linkage.mesh_texture_root_for(catalog_path, None)
    sidecar_names = linkage.sidecar_texture_names(sidecar_root)
    sidecar_stems = {linkage.texture_stem(name) for name in sidecar_names}

    by_kind: dict[str, dict[str, Any]] = {}
    for export in linkage.model_exports(catalog):
        item = by_kind.setdefault(
            export.kind,
            {
                "rows": 0,
                "rowsWithRefs": 0,
                "textureRefInstances": 0,
                "uniqueRefs": set(),
                "exactSidecarRefs": set(),
                "stemOnlySidecarRefs": set(),
                "missingSidecarRefs": set(),
                "catalogMissingRefs": set(),
            },
        )
        item["rows"] += 1
        refs = linkage.extract_fbx_texture_refs(linkage.resolve_repo_path(export.export_path))
        if refs:
            item["rowsWithRefs"] += 1
            item["textureRefInstances"] += len(refs)
            item["uniqueRefs"].update(refs)

        for ref in refs:
            stem = linkage.texture_stem(ref)
            if ref in sidecar_names:
                item["exactSidecarRefs"].add(ref)
            elif stem in sidecar_stems:
                item["stemOnlySidecarRefs"].add(ref)
            else:
                item["missingSidecarRefs"].add(ref)

            compact = linkage.compact_texture_key(ref)
            catalog_hits = {
                hit
                for key in (stem, compact)
                for hit in texture_stems.get(key, [])
            }
            if not catalog_hits:
                item["catalogMissingRefs"].add(ref)

    public: dict[str, dict[str, int]] = {}
    for kind, item in sorted(by_kind.items()):
        public[kind] = {
            "rows": item["rows"],
            "rowsWithRefs": item["rowsWithRefs"],
            "textureRefInstances": item["textureRefInstances"],
            "uniqueTextureRefs": len(item["uniqueRefs"]),
            "uniqueRefsWithExactSidecarName": len(item["exactSidecarRefs"]),
            "uniqueRefsWithSidecarStemOnly": len(item["stemOnlySidecarRefs"]),
            "uniqueRefsMissingSidecar": len(item["missingSidecarRefs"]),
            "uniqueRefsMissingCatalogRows": len(item["catalogMissingRefs"]),
        }
    return public


def build_ledger(proof_root: Path) -> dict[str, Any]:
    proof_root = proof_root.resolve()
    catalog_path = proof_root / "asset_catalog" / "catalog.json"
    catalog_summary_path = proof_root / "asset_catalog" / "summary.json"
    archive_inventory_path = proof_root / "aya_archive_inventory.json"
    packed_manifest_path = proof_root / "aya_asset_manifest.json"
    asset_export_root = proof_root / "asset_export"

    catalog = read_json(catalog_path)
    catalog_summary = read_json(catalog_summary_path)
    archive_rows = read_json(archive_inventory_path)
    packed_manifest = read_json(packed_manifest_path)
    tags = aggregate_tags(archive_rows)
    model_report = linkage.build_report(catalog_path)

    failures: list[str] = []
    if model_report.get("status") != "PASS":
        failures.append("model texture linkage report is not PASS")
    if model_report.get("uniqueTextureRefsMissingSidecar") != 0:
        failures.append("model texture refs missing sidecar coverage")
    if model_report.get("uniqueTextureRefsMissingCatalogRows") != 0:
        failures.append("model texture refs missing catalog rows")

    export_lanes = {
        "looseTextures": lane_export_summary(asset_export_root, "loose_textures"),
        "looseMeshes": lane_export_summary(asset_export_root, "loose_meshes"),
        "embeddedMeshes": lane_export_summary(asset_export_root, "embedded_meshes"),
    }
    for name, lane in export_lanes.items():
        if lane["failed"] != 0:
            failures.append(f"{name} has failed rows")
        if lane["skippedExisting"] != 0:
            failures.append(f"{name} has skipped-existing rows")

    return {
        "schema": "asset-material-sidecar-ledger.v1",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "sourceArtifacts": {
            "proofRoot": relative(proof_root),
            "catalog": relative(catalog_path),
            "archiveInventory": relative(archive_inventory_path),
            "packedManifest": relative(packed_manifest_path),
            "modelTextureLinkageSemantics": "tools/model_texture_linkage_probe.py",
        },
        "countAnchors": {
            "archives": len(archive_rows),
            "goodieArchives": sum(1 for row in archive_rows if file_name(str(row.get("path", ""))).lower().startswith("goodie_")),
            "topLevelChunks": {
                "TEXT": tags.get("TEXT", 0),
                "MESH": tags.get("MESH", 0),
                "GDIE": tags.get("GDIE", 0),
                "LVLR": tags.get("LVLR", 0),
                "TARG": tags.get("TARG", 0),
                "AYAD": tags.get("AYAD", 0),
            },
            "packedRefs": {
                "textTextures": f"{packed_manifest['summary']['text_texture_refs_resolved']}/{packed_manifest['summary']['text_texture_refs']}",
                "referenceMeshes": f"{packed_manifest['summary']['reference_mesh_refs_resolved']}/{packed_manifest['summary']['reference_mesh_refs']}",
                "gdieTextures": f"{packed_manifest['summary']['gdie_texture_refs_resolved']}/{packed_manifest['summary']['gdie_texture_refs']}",
                "gdieMeshes": f"{packed_manifest['summary']['gdie_mesh_refs_resolved']}/{packed_manifest['summary']['gdie_mesh_refs']}",
            },
        },
        "exportLanes": export_lanes,
        "catalogCoverage": {
            "textures": catalog_summary["texture_catalog_entries"],
            "looseMeshes": catalog_summary["loose_mesh_catalog_entries"],
            "embeddedMeshes": catalog_summary["embedded_mesh_catalog_entries"],
            "videos": catalog_summary["video_catalog_entries"],
            "languageRows": catalog_summary["language_catalog_entries"],
            "goodies": catalog_summary["goodie_catalog_entries"],
            "totalRows": catalog_summary["total_catalog_entries"],
        },
        "modelCoverage": {
            "modelRows": model_report["modelRows"],
            "modelRowsWithTextureRefs": model_report["modelRowsWithTextureRefs"],
            "modelTextureReferenceInstances": model_report["modelTextureReferenceInstances"],
            "modelRowsWithAllTextureRefsCatalogMapped": model_report["modelRowsWithAllTextureRefsCatalogMapped"],
            "modelRowsWithAnyCatalogMissingTextureRef": model_report["modelRowsWithAnyCatalogMissingTextureRef"],
            "modelRowsWithAnyMissingSidecarTextureRef": model_report["modelRowsWithAnyMissingSidecarTextureRef"],
            "uniqueModelTextureRefs": model_report["uniqueModelTextureRefs"],
            "sidecarTextureFiles": model_report["sidecarTextureFiles"],
            "uniqueTextureRefsWithExactSidecarName": model_report["uniqueTextureRefsWithExactSidecarName"],
            "uniqueTextureRefsWithSidecarStemOnly": model_report["uniqueTextureRefsWithSidecarStemOnly"],
            "uniqueTextureRefsMissingSidecar": model_report["uniqueTextureRefsMissingSidecar"],
            "uniqueTextureRefsMissingCatalogRows": model_report["uniqueTextureRefsMissingCatalogRows"],
            "uniqueTextureRefsAmbiguousInCatalog": model_report["uniqueTextureRefsAmbiguousInCatalog"],
            "byKind": kind_coverage(catalog, catalog_path),
        },
        "exportUniqueness": {
            "looseMeshes": {
                "rows": export_lanes["looseMeshes"]["rows"],
                "uniqueOutputFiles": export_lanes["looseMeshes"]["uniqueOutputFiles"],
                "duplicateOutputGroups": export_lanes["looseMeshes"]["duplicateOutputGroups"],
                "duplicateOutputRows": export_lanes["looseMeshes"]["duplicateOutputRows"],
            },
            "embeddedMeshes": {
                "rows": export_lanes["embeddedMeshes"]["rows"],
                "uniqueOutputFiles": export_lanes["embeddedMeshes"]["uniqueOutputFiles"],
                "duplicateOutputGroups": export_lanes["embeddedMeshes"]["duplicateOutputGroups"],
                "duplicateOutputRows": export_lanes["embeddedMeshes"]["duplicateOutputRows"],
            },
        },
        "publicSafety": {
            "stripsAbsoluteFbxTexturePaths": True,
            "stripsExportFilePaths": True,
            "embedsPrivateAssets": False,
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
            "commitsRawAssets": False,
        },
        "claims": [
            "Generated copied-corpus model texture references resolve to sidecar files by exact filename or stem.",
            "Generated copied-corpus model texture references are catalog-mapped after placeholder filtering and compact-name matching.",
            "Embedded mesh export rows can share output filenames; this ledger records duplicate-output accounting separately from row coverage.",
        ],
        "notClaimed": [
            "runtime parser behavior",
            "runtime texture pixels",
            "JPEG/inflate decode fidelity",
            "Direct3D or GPU upload behavior",
            "visual QA",
            "native textured 3D rendering",
            "material visual correctness",
            "material/shader parity",
            "animation, lighting, skinning, or collision runtime behavior",
            "BEA patching behavior",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
            "redistribution rights for private assets",
        ],
        "warnings": ["embedded mesh export has duplicate-output rows; row coverage remains distinct from unique output-file count"],
        "failures": failures,
    }


def write_fake_fbx(path: Path, texture_names: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = b"Kaydara FBX Binary  \x00"
    for name in texture_names:
        payload += b"Texture\x00" + name.encode("ascii") + b"\x00"
        payload += b"C:\\private\\MeshTextures\\" + name.encode("ascii") + b"\x00"
    path.write_bytes(payload)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        proof = root / "proof"
        catalog_dir = proof / "asset_catalog"
        catalog = catalog_dir / "catalog.json"
        fbx = proof / "asset_export" / "loose_meshes" / "ship.fbx"
        mesh_textures = proof / "asset_export" / "loose_meshes" / "MeshTextures"
        write_fake_fbx(fbx, ["ship.png"])
        mesh_textures.mkdir(parents=True, exist_ok=True)
        (mesh_textures / "ship.png").write_bytes(b"png")
        catalog_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            catalog,
            {
                "textures": [{"canonical_ref": "meshtex\\ship.tga"}],
                "loose_meshes": [{"canonical_ref": "ship.msh", "export_fbx_paths": [str(fbx)]}],
                "embedded_meshes": [],
            },
        )
        write_json(catalog_dir / "summary.json", {
            "texture_catalog_entries": 1,
            "loose_mesh_catalog_entries": 1,
            "embedded_mesh_catalog_entries": 0,
            "video_catalog_entries": 0,
            "language_catalog_entries": 0,
            "goodie_catalog_entries": 0,
            "total_catalog_entries": 1,
        })
        write_json(proof / "aya_archive_inventory.json", [{"path": "001_res_PC.aya", "tag_counts": {"TEXT": 1, "MESH": 1, "GDIE": 0, "LVLR": 1, "TARG": 1, "AYAD": 1}}])
        write_json(proof / "aya_asset_manifest.json", {"summary": {
            "text_texture_refs": 1,
            "text_texture_refs_resolved": 1,
            "reference_mesh_refs": 1,
            "reference_mesh_refs_resolved": 1,
            "gdie_texture_refs": 0,
            "gdie_texture_refs_resolved": 0,
            "gdie_mesh_refs": 0,
            "gdie_mesh_refs_resolved": 0,
        }})
        for lane in ("loose_textures", "loose_meshes", "embedded_meshes"):
            rows = [{"input": "in", "output": "out", "status": "ok"}] if lane != "embedded_meshes" else []
            write_json(proof / "asset_export" / lane / "manifest.json", rows)
        ledger = build_ledger(proof)
        assert ledger["schema"] == "asset-material-sidecar-ledger.v1"
        assert ledger["status"] == "PASS"
        assert ledger["modelCoverage"]["modelRows"] == 1
        assert ledger["modelCoverage"]["uniqueTextureRefsMissingSidecar"] == 0
        assert "C:\\private" not in json.dumps(ledger)
    print("texture_mesh_material_sidecar_ledger self-test: PASS")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proof-root", type=Path, default=DEFAULT_PROOF_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true", help="fail if generated ledger status is not PASS")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    ledger = build_ledger(args.proof_root)
    write_json(args.out, ledger)
    print(f"{ledger['status']}: wrote {relative(args.out)}")
    print(
        "Material sidecar ledger: "
        f"models={ledger['modelCoverage']['modelRows']} "
        f"withRefs={ledger['modelCoverage']['modelRowsWithTextureRefs']} "
        f"uniqueRefs={ledger['modelCoverage']['uniqueModelTextureRefs']} "
        f"missingSidecars={ledger['modelCoverage']['uniqueTextureRefsMissingSidecar']} "
        f"catalogMissing={ledger['modelCoverage']['uniqueTextureRefsMissingCatalogRows']}"
    )
    if args.check and ledger["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
