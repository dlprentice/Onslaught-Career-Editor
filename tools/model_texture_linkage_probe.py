#!/usr/bin/env python3
"""Summarize model FBX texture linkage from the generated asset export.

The probe reads the public-safe asset catalog plus ignored exported FBX files
and reports whether model texture references have local sidecar texture files.
It strips absolute paths and records catalog linkage separately from sidecar
coverage because some FBX texture names are mesh-export sidecars rather than
rows in the texture catalog.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = (
    ROOT
    / "subagents"
    / "asset-full-install-2026-05-07"
    / "full-export"
    / "asset_catalog"
    / "catalog.json"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "model-texture-linkage"
    / "current"
    / "model-texture-linkage.json"
)
PRINTABLE_RE = re.compile(rb"[ -~]{4,}")
TEXTURE_FILE_RE = re.compile(r"\.(png|tga)$", re.IGNORECASE)
DEFAULT_TEXTURE_RE = re.compile(r"default\d+$", re.IGNORECASE)


@dataclass(frozen=True)
class ModelExport:
    kind: str
    label: str
    export_path: Path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_path_fragment(value: object) -> str:
    return str(value).replace("\\", "/")


def texture_stem(filename: str) -> str:
    return Path(filename.replace("\\", "/")).stem.lower()


def compact_texture_key(filename: str) -> str:
    return "".join(ch for ch in texture_stem(filename) if ch.isalnum())


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (ROOT / path).resolve()


def load_catalog(catalog_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    catalog_path = resolve_repo_path(catalog_path)
    if not catalog_path.is_file():
        return None, [f"missing catalog: {relative(catalog_path)}"]
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"catalog JSON decode failed: {exc}"]
    if not isinstance(data, dict):
        return None, ["catalog root is not an object"]
    return data, []


def catalog_texture_stems(catalog: dict[str, Any]) -> dict[str, list[str]]:
    stems: dict[str, list[str]] = {}
    for row in catalog.get("textures", []) or []:
        if not isinstance(row, dict):
            continue
        for field in ("canonical_ref", "export_file_name"):
            value = normalize_path_fragment(row.get(field, ""))
            if not value:
                continue
            stem = texture_stem(value)
            compact = compact_texture_key(value)
            stems.setdefault(stem, []).append(value)
            if compact and compact != stem:
                stems.setdefault(compact, []).append(value)
    return stems


def model_exports(catalog: dict[str, Any]) -> list[ModelExport]:
    exports: list[ModelExport] = []
    for row in catalog.get("loose_meshes", []) or []:
        if not isinstance(row, dict):
            continue
        label = str(row.get("canonical_ref") or row.get("catalog_id") or "loose_mesh")
        for raw_path in row.get("export_fbx_paths", []) or []:
            exports.append(ModelExport("loose", label, Path(str(raw_path))))

    for row in catalog.get("embedded_meshes", []) or []:
        if not isinstance(row, dict):
            continue
        raw_path = row.get("export_fbx_path")
        if not raw_path:
            continue
        label = str(row.get("body_name") or row.get("catalog_id") or "embedded_mesh")
        exports.append(ModelExport("embedded", label, Path(str(raw_path))))
    return exports


def mesh_texture_root_for(catalog_path: Path, explicit_root: Path | None) -> Path:
    if explicit_root is not None:
        return resolve_repo_path(explicit_root)
    catalog_path = resolve_repo_path(catalog_path)
    full_export_root = catalog_path.parents[1]
    return full_export_root / "asset_export" / "loose_meshes" / "MeshTextures"


def sidecar_texture_names(mesh_texture_root: Path) -> set[str]:
    if not mesh_texture_root.is_dir():
        return set()
    return {
        child.name.lower()
        for child in mesh_texture_root.iterdir()
        if child.is_file() and TEXTURE_FILE_RE.search(child.name)
    }


def is_template_texture(filename: str) -> bool:
    stem = texture_stem(filename)
    return bool(DEFAULT_TEXTURE_RE.fullmatch(stem)) or stem == "base_color_texture"


def extract_fbx_texture_refs(path: Path) -> set[str]:
    data = path.read_bytes()
    refs: set[str] = set()
    for match in PRINTABLE_RE.finditer(data):
        value = match.group().decode("latin1", errors="ignore")
        filename = normalize_path_fragment(value).split("/")[-1].lower()
        if not TEXTURE_FILE_RE.search(filename):
            continue
        if is_template_texture(filename):
            continue
        refs.add(filename)
    return refs


def build_report(
    catalog_path: Path,
    *,
    mesh_texture_root: Path | None = None,
) -> dict[str, Any]:
    catalog_path = resolve_repo_path(catalog_path)
    catalog, failures = load_catalog(catalog_path)
    if catalog is None:
        return {
            "schema": "model-texture-linkage.v1",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "status": "FAIL",
            "catalog": relative(catalog_path),
            "failures": failures,
        }

    texture_stems = catalog_texture_stems(catalog)
    exports = model_exports(catalog)
    sidecar_root = mesh_texture_root_for(catalog_path, mesh_texture_root)
    sidecar_names = sidecar_texture_names(sidecar_root)
    sidecar_stems = {texture_stem(name) for name in sidecar_names}

    missing_exports: list[str] = []
    missing_sidecar_refs: set[str] = set()
    catalog_missing_refs: set[str] = set()
    ambiguous_catalog_refs: set[str] = set()
    exact_sidecar_refs: set[str] = set()
    stem_sidecar_refs: set[str] = set()
    all_texture_refs: set[str] = set()
    row_family_counts: Counter[str] = Counter()
    model_rows_with_refs = 0
    model_ref_instances = 0
    model_rows_with_all_refs_catalog_mapped = 0
    model_rows_with_any_catalog_missing_ref = 0
    model_rows_with_any_missing_sidecar_ref = 0
    sample_models: list[dict[str, Any]] = []
    all_catalog_mapped_model_samples: list[dict[str, Any]] = []
    sidecar_needed_model_samples: list[dict[str, Any]] = []

    for export in exports:
        export_path = resolve_repo_path(export.export_path)
        if not export_path.is_file():
            missing_exports.append(export.label)
            continue
        refs = extract_fbx_texture_refs(export_path)
        if refs:
            model_rows_with_refs += 1
            model_ref_instances += len(refs)
            all_texture_refs.update(refs)
            row_family_counts[export.kind] += 1
        if refs and len(sample_models) < 8:
            sample_models.append(
                {
                    "kind": export.kind,
                    "label": export.label,
                    "textureRefSample": sorted(refs)[:8],
                }
            )
        row_has_catalog_missing_ref = False
        row_has_missing_sidecar_ref = False
        row_catalog_missing_refs: set[str] = set()
        for ref in refs:
            stem = texture_stem(ref)
            if ref in sidecar_names:
                exact_sidecar_refs.add(ref)
            elif stem in sidecar_stems:
                stem_sidecar_refs.add(ref)
            else:
                missing_sidecar_refs.add(ref)
                row_has_missing_sidecar_ref = True

            compact = compact_texture_key(ref)
            catalog_hits = list(
                {
                    hit
                    for key in (stem, compact)
                    for hit in texture_stems.get(key, [])
                }
            )
            if not catalog_hits:
                catalog_missing_refs.add(ref)
                row_catalog_missing_refs.add(ref)
                row_has_catalog_missing_ref = True
            elif len(catalog_hits) > 1:
                ambiguous_catalog_refs.add(ref)
        if refs:
            if row_has_catalog_missing_ref:
                model_rows_with_any_catalog_missing_ref += 1
            else:
                model_rows_with_all_refs_catalog_mapped += 1
            if row_has_missing_sidecar_ref:
                model_rows_with_any_missing_sidecar_ref += 1
            if not row_has_catalog_missing_ref and len(all_catalog_mapped_model_samples) < 8:
                all_catalog_mapped_model_samples.append(model_sample(export, refs))
            if row_has_catalog_missing_ref and len(sidecar_needed_model_samples) < 8:
                sidecar_sample = model_sample(export, refs)
                sidecar_sample["catalogMissingRefSample"] = sorted(row_catalog_missing_refs)[:8]
                sidecar_needed_model_samples.append(sidecar_sample)

    if not exports:
        failures.append("no model export rows found in catalog")
    if missing_exports:
        failures.append(f"missing FBX exports: {len(missing_exports)}")
    if missing_sidecar_refs:
        failures.append(f"missing sidecar texture refs: {len(missing_sidecar_refs)}")

    return {
        "schema": "model-texture-linkage.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "catalog": relative(catalog_path),
        "modelRows": len(exports),
        "modelRowsWithTextureRefs": model_rows_with_refs,
        "modelTextureReferenceInstances": model_ref_instances,
        "modelRowsWithAllTextureRefsCatalogMapped": model_rows_with_all_refs_catalog_mapped,
        "modelRowsWithAnyCatalogMissingTextureRef": model_rows_with_any_catalog_missing_ref,
        "modelRowsWithAnyMissingSidecarTextureRef": model_rows_with_any_missing_sidecar_ref,
        "uniqueModelTextureRefs": len(all_texture_refs),
        "sidecarTextureFiles": len(sidecar_names),
        "uniqueTextureRefsWithExactSidecarName": len(exact_sidecar_refs),
        "uniqueTextureRefsWithSidecarStemOnly": len(stem_sidecar_refs),
        "uniqueTextureRefsMissingSidecar": len(missing_sidecar_refs),
        "uniqueTextureRefsMissingCatalogRows": len(catalog_missing_refs),
        "uniqueTextureRefsAmbiguousInCatalog": len(ambiguous_catalog_refs),
        "modelRowsWithTextureRefsByKind": dict(sorted(row_family_counts.items())),
        "sampleModels": sample_models,
        "allCatalogMappedModelSamples": all_catalog_mapped_model_samples,
        "sidecarNeededModelSamples": sidecar_needed_model_samples,
        "catalogMissingRefSamples": sorted(catalog_missing_refs)[:20],
        "ambiguousCatalogRefSamples": sorted(ambiguous_catalog_refs)[:20],
        "missingSidecarRefSamples": sorted(missing_sidecar_refs)[:20],
        "publicSafety": {
            "stripsAbsoluteFbxTexturePaths": True,
            "stripsExportFilePaths": True,
            "embedsPrivateAssets": False,
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
        },
        "currentClaims": [
            "Every checked model texture reference must resolve to a local mesh-texture sidecar by exact filename or stem.",
            "Texture catalog linkage is reported separately because some model sidecars are not represented as direct texture catalog rows.",
            "Template default texture slots from the FBX export are excluded from linkage counts.",
        ],
        "notClaimed": [
            "This does not render textured models in WinUI.",
            "This does not prove material/shader parity with the retail renderer.",
            "This does not prove runtime in-game model-viewer playback.",
            "This does not make any redistribution claim for private game textures.",
        ],
        "failures": failures,
    }


def model_sample(export: ModelExport, refs: set[str]) -> dict[str, Any]:
    return {
        "kind": export.kind,
        "label": export.label,
        "textureRefSample": sorted(refs)[:8],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mesh-texture-root", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if model exports or sidecar texture coverage are missing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.catalog, mesh_texture_root=args.mesh_texture_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "Model texture linkage: "
        f"models={report.get('modelRows', 0)} "
        f"withRefs={report.get('modelRowsWithTextureRefs', 0)} "
        f"uniqueRefs={report.get('uniqueModelTextureRefs', 0)} "
        f"missingSidecars={report.get('uniqueTextureRefsMissingSidecar', 0)} "
        f"catalogMissing={report.get('uniqueTextureRefsMissingCatalogRows', 0)}"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
