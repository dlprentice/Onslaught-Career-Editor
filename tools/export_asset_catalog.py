#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
Build a deduplicated cross-surface private asset catalog.

This ties together:
- packed AYA reference manifests
- loose texture exports
- loose mesh exports
- embedded packed-mesh exports
- merged language corpus
- loose video manifest

Examples:
    python ./tools/export_asset_catalog.py --self-test
    python ./tools/export_asset_catalog.py --bundle-root <generated-root> --out-dir <generated-root>/asset_catalog ...
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import stat
import tempfile
from collections import Counter
from pathlib import Path

import aya_archive_inventory as aai
from safe_generated_output import SecuredOutputRoot, validate_disjoint_output_root


CATALOG_SCHEMA_VERSION = 3
CATALOG_PATH_CONTRACT = "bundle-root-relative"
CATALOG_EXPORT_CONTRACT = "source-bound-verified-outputs-only"
CATALOG_INSPECTION_SCHEMA = "onslaught.catalog-source-selection.v1"
MAX_INSPECTED_SOURCES = 256
MAX_INSPECTED_SOURCE_BYTES = 256 * 1024 * 1024
MAX_SINGLE_SOURCE_BYTES = 64 * 1024 * 1024


def _identity_hash(domain: str, value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(domain.encode("ascii") + b"\0" + encoded).hexdigest()


class SourceInspectionError(ValueError):
    def __init__(self, status: str, reason: str):
        self.status, self.reason = status, reason
        super().__init__(reason)


class SourceReadBudget:
    """Charge bytes as read, including sources that later fail identity checks."""
    def __init__(self, limit: int):
        self.limit = limit
        self.bytes_read = 0

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.bytes_read)


def _file_fingerprint(value: os.stat_result) -> tuple[int, ...]:
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns, value.st_nlink)


def _read_selected_source(source_root: Path, source_path: Path, budget: SourceReadBudget) -> bytes:
    """Bounded openat read; retain/revalidate every directory and the file handle.

    No discovery, symlink traversal, hardlinked file, or absolute source outside
    the explicit root is admitted. Directory descriptors prevent path races from
    redirecting a selected read; post-read name checks reject moved/replaced inputs.
    """
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise SourceInspectionError("unsupported", "descriptor-safe reads unavailable")
    root = Path(os.path.abspath(source_root))
    path = Path(os.path.abspath(source_path))
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise SourceInspectionError("rejected", "source outside explicit inspection root") from error
    if not relative.parts:
        raise SourceInspectionError("rejected", "source must be a file below the inspection root")
    descriptors: list[int] = []
    links: list[tuple[int, str, os.stat_result]] = []
    try:
        fd = os.open(root.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(fd)
        for component in (*root.parts[1:], *relative.parts[:-1]):
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            descriptors.append(child)
            metadata = os.fstat(child)
            links.append((fd, component, metadata))
            fd = child
        source = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        descriptors.append(source)
        before = os.fstat(source)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SourceInspectionError("rejected", "source must be a regular single-link file")
        if before.st_size > MAX_SINGLE_SOURCE_BYTES:
            raise SourceInspectionError("unsupported", "source exceeds single-source byte limit")
        if before.st_size > budget.remaining:
            raise SourceInspectionError("notAttempted", "selection byte budget exhausted")
        chunks, count = [], 0
        # Read only the size already admitted by the held descriptor. The final metadata checks
        # catch growth without a one-byte EOF probe beyond either byte limit.
        while count < before.st_size:
            requested = min(1024 * 1024, before.st_size - count, budget.remaining)
            if requested <= 0:
                raise SourceInspectionError("notAttempted", "selection byte budget exhausted")
            chunk = os.read(source, requested)
            budget.bytes_read += len(chunk)
            if not chunk:
                break
            count += len(chunk)
            if len(chunk) > requested or count > MAX_SINGLE_SOURCE_BYTES:
                raise SourceInspectionError("rejected", "source read exceeded admitted byte limit")
            chunks.append(chunk)
        if count != before.st_size or _file_fingerprint(os.fstat(source)) != _file_fingerprint(before):
            raise SourceInspectionError("rejected", "source changed during held read")
        after = os.stat(relative.name, dir_fd=fd, follow_symlinks=False)
        if _file_fingerprint(after) != _file_fingerprint(before):
            raise SourceInspectionError("rejected", "source path changed during held read")
        for parent, name, expected in links:
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if (current.st_dev, current.st_ino, current.st_mode) != (expected.st_dev, expected.st_ino, expected.st_mode):
                raise SourceInspectionError("rejected", "source directory changed during held read")
        return b"".join(chunks)
    except OSError as error:
        if error.errno in (errno.ELOOP, errno.ENOTDIR):
            raise SourceInspectionError("rejected", "source path is a link or not a directory/file") from error
        raise SourceInspectionError("unavailable", "source could not be read") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _source_metadata(kind: str, source: bytes, path: Path, logical: str) -> tuple[dict[str, object], dict[str, object] | None]:
    """Use existing bounded parsers; never infer embedded-body framing/offsets."""
    if kind == "texture":
        import dds_census
        envelope = "dds" if path.suffix.lower() == ".dds" else "aya"
        metadata = dds_census.texture_metadata(source, envelope=envelope)
        payload = metadata["dds"]
        if payload is None:
            return {"status": metadata["status"], "measured": metadata}, None
        identity = {"length": payload["size"], "sha256": payload["sha256"]}
        # Source-envelope fields belong to the occurrence, not a shared payload variant.
        measured = {key: value for key, value in metadata.items() if key != "source"}
        return {"status": metadata["status"], "envelope": envelope}, {
            "payload_domain": "dds-stream", "payload_identity": identity,
            "parser": "dds_census.texture_metadata", "measured": measured,
        }
    import cmsh_animation_usage_census as models
    if path.suffix.lower() == ".aya" and kind == "loose_mesh":
        try:
            payload_bytes = models.inflate_aya(source)
        except models.CmshProfileError as error:
            return {"status": "unparsed", "reason": {"category": error.category,
                    "falsifier": "supply a supported bounded AYA/CMSH source"}}, None
        envelope = "aya"
    elif source.startswith(b"CMSH"):
        payload_bytes, envelope = source, "raw-cmsh-stream"
    else:
        return {"status": "unknown", "reason": {
            "category": "raw mesh framing not established",
            "falsifier": "provide an independently located complete CMSH stream"}}, None
    row, _mesh = models.mesh_record_from_stream(
        payload_bytes, source_path=logical, archive_sha256=hashlib.sha256(source).hexdigest())
    metadata = dict(row["modelMetadata"])
    metadata.pop("identity", None)  # Its archive coordinates do not describe a standalone raw file.
    metadata["summary"] = {key: value for key, value in row.items() if key not in ("file", "modelMetadata")}
    return {"status": metadata["status"], "envelope": envelope}, {
        "payload_domain": "cmsh-stream", "payload_identity": {
            "length": len(payload_bytes), "sha256": hashlib.sha256(payload_bytes).hexdigest()},
        "parser": "cmsh_animation_usage_census.mesh_record_from_stream", "measured": metadata,
    }


def inspect_catalog_sources(
    textures: list[dict[str, object]], loose_meshes: list[dict[str, object]],
    embedded_meshes: list[dict[str, object]], *, source_root: Path,
    source_manifests: tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]],
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Join only the explicit catalog selection, never an exhaustive AYA universe.

    Callers must opt in. Source paths are root-relative logical locations; exact
    variants use payload bytes, while occurrence IDs include selection, location
    and the complete held-source identity. Unreadable/rejected rows remain visible.
    """
    root = Path(os.path.abspath(source_root))
    path_base = root if repo_root is None else Path(os.path.abspath(repo_root))
    entries = [*textures, *loose_meshes, *embedded_meshes]
    selected: dict[tuple[str, str], dict[str, object]] = {}
    grouped: dict[tuple[str, str, str | None], list[tuple[str, str]]] = {}
    if len(source_manifests) != 3:
        raise ValueError("inspection needs the original texture/loose/embedded manifest selections")
    for kind, manifest in zip(("texture", "loose_mesh", "embedded_mesh"), source_manifests):
        for declaration in manifest:
            # Do not reconstruct paths from repo_rel() display fields: those
            # legacy fields resolve links and lose the original selected path.
            declared = Path(declaration["input"])
            path = declared
            if not path.is_absolute():
                path = path_base / path
            path = Path(os.path.abspath(path))
            key = (str(kind), str(path))
            selected.setdefault(key, {"kind": kind, "path": path})
            if kind == "texture":
                aliases = texture_aliases_for_catalog(declared.name)
                catalog_id = "texture:" + choose_texture_ref(aliases, declared.stem)
            elif kind == "loose_mesh":
                catalog_id = "mesh:" + choose_mesh_ref(mesh_aliases_from_loose_name(declared.name))
            else:
                catalog_id = f"embedded_mesh:{declared.parent.name}/{declared.stem}"
            provenance = repo_rel(declared, path_base) if kind == "embedded_mesh" else None
            grouped.setdefault((kind, catalog_id, provenance), []).append(key)
    entry_keys = [grouped.get((str(entry["kind"]), str(entry["catalog_id"]),
                              entry.get("source_body_path") if entry["kind"] == "embedded_mesh" else None), [])
                  for entry in entries]
    observed: dict[tuple[str, str], dict[str, object]] = {}
    budget = SourceReadBudget(MAX_INSPECTED_SOURCE_BYTES)
    for index, key in enumerate(sorted(selected)):
        request = selected[key]
        path, kind = request["path"], request["kind"]
        try:
            logical = path.relative_to(root).as_posix()
        except ValueError:
            logical = None
        row: dict[str, object] = {"kind": kind, "logical_source_path": logical,
                                 "source_identity": None, "variant": None}
        try:
            if index >= MAX_INSPECTED_SOURCES:
                raise SourceInspectionError("notAttempted", "selection source-count budget exhausted")
            source = _read_selected_source(root, path, budget)
            row["source_identity"] = {"length": len(source), "sha256": hashlib.sha256(source).hexdigest()}
            status, variant = _source_metadata(str(kind), source, path, str(logical))
            row.update(status)
            row["variant"] = variant
        except SourceInspectionError as error:
            row.update(status=error.status, reason={"category": error.reason,
                       "falsifier": "provide a stable supported regular source under the explicit root"})
        observed[key] = row
    namespace_rows = sorted(
        ({name: value for name, value in row.items() if name != "variant"} for row in observed.values()),
        key=lambda value: json.dumps(value, sort_keys=True))
    namespace = _identity_hash(CATALOG_INSPECTION_SCHEMA, namespace_rows)
    for entry, keys in zip(entries, entry_keys):
        variants: dict[str, dict[str, object]] = {}
        occurrences = []
        for key in sorted(set(keys)):
            record = dict(observed[key])
            variant = record.pop("variant")
            variant_id = None
            if variant is not None:
                variant_id = "asset-variant:" + _identity_hash("onslaught.asset-variant.v1", {
                    "kind": "texture" if record["kind"] == "texture" else "mesh",
                    "domain": variant["payload_domain"], "identity": variant["payload_identity"]})
                variants[variant_id] = {"variant_id": variant_id,
                    "asset_kind": "texture" if record["kind"] == "texture" else "mesh", **variant,
                    "description": None, "description_status": "not-visually-reviewed", "annotations": []}
            record["variant_id"] = variant_id
            record["occurrence_id"] = ("asset-occurrence:" + _identity_hash("onslaught.asset-occurrence.v1", {
                "selection_namespace": namespace, "kind": record["kind"],
                "logical_source_path": record["logical_source_path"], "source_identity": record["source_identity"]})
                if record["source_identity"] is not None else None)
            occurrences.append(record)
        entry["variants"] = [variants[key] for key in sorted(variants)]
        entry["occurrences"] = sorted(occurrences, key=lambda value: json.dumps(value, sort_keys=True))
        entry["exact_variant_count"], entry["occurrence_count"] = len(variants), len(occurrences)
        entry["occurrence_count_scope"] = "declared-source-locations"
        entry["observed_occurrence_count"] = sum(row["source_identity"] is not None for row in occurrences)
    return {"schema": CATALOG_INSPECTION_SCHEMA, "selection_namespace": namespace,
            "scope": "explicit-manifest-source-selection-not-full-aya-universe",
            "source_count": len(observed), "source_bytes_read": budget.bytes_read,
            "source_limit": MAX_INSPECTED_SOURCES, "source_byte_limit": MAX_INSPECTED_SOURCE_BYTES,
            "status_counts": dict(sorted(Counter(row["status"] for row in observed.values()).items())),
            "description_status": "not-visually-reviewed", "export_verification": "not-established"}


def repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("/", "\\")
    except Exception:
        return str(path).replace("/", "\\")


def bundle_rel(path: Path, bundle_root: Path, label: str) -> str:
    try:
        relative = path.resolve().relative_to(bundle_root.resolve())
    except ValueError as exc:
        raise SystemExit(f"{label} is outside --bundle-root: {path}") from exc
    if not relative.parts:
        raise SystemExit(f"{label} must be a file below --bundle-root: {path}")
    return str(relative).replace("/", "\\")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def legacy_export_attempt(row: dict[str, object], bundle_root: Path, kind: str) -> dict[str, object]:
    """Keep a legacy export declaration without promoting it to source-bound output proof.

    The harness's ok/skipped_existing/error rows have no source/output hashes or
    conversion validator. Even an existing file or a supplied 'verified' field
    cannot establish correspondence to these source bytes. Retain failed and
    unverified attempts for callers to inspect; success paths remain empty until
    an actual identity-bound output producer is connected to this catalog.
    """
    status = row.get("status")
    output = row.get("output")
    if output is not None and (not isinstance(output, str) or not output):
        raise ValueError("catalog export output must be a nonempty path or null")
    return {
        "attempt_status": status if status in ("ok", "skipped_existing", "error") else "notReported",
        "verification_status": "failed" if status == "error" else "unverified",
        "output_kind": kind,
        "requested_output_path": bundle_rel(Path(output), bundle_root, "requested export") if output else None,
        "verified_output_path": None,
        "limitation": "Legacy declaration has no source-bound output identity or conversion validation.",
    }


def choose_texture_ref(refs: set[str], fallback_name: str) -> str:
    if not refs:
        return fallback_name.lower()
    return sorted(refs, key=lambda value: (value.startswith("mustbe_"), len(value), value))[0]


def texture_aliases_for_catalog(file_name: str) -> set[str]:
    lower = file_name.lower()
    stem = lower[:-4] if lower.endswith(".aya") else lower
    if "(0)" in stem:
        stem = stem.split("(0)", 1)[0]

    if ".tga" in stem:
        base = stem[: stem.index(".tga") + 4]
    elif ".t" in stem:
        base = f"{stem[: stem.index('.t') + 2]}ga"
    else:
        base = stem

    aliases = {base.replace("%", "\\")}
    for alias in list(aliases):
        if alias.startswith("mustbe_"):
            aliases.add(alias[len("mustbe_") :])
    return aliases


def mesh_aliases_from_loose_name(file_name: str) -> list[str]:
    lower = file_name.lower()
    if not lower.endswith(".aya"):
        return [lower]
    stem = lower[:-4]
    aliases = {stem}
    if stem.startswith("m_"):
        aliases.add(stem[2:])
    return sorted(aliases)


def choose_mesh_ref(aliases: list[str]) -> str:
    return sorted(aliases, key=lambda value: (value.startswith("m_"), len(value), value))[0]


def packed_ref_maps(packed_manifest: dict[str, object], key: str) -> dict[str, dict[str, object]]:
    rows = packed_manifest[key]
    return {
        row["ref"]: {
            "count": row["count"],
            "match_count": row["match_count"],
            "matches": row["matches"],
        }
        for row in rows
    }


def build_texture_catalog(
    texture_manifest: list[dict[str, object]],
    packed_manifest: dict[str, object],
    repo_root: Path,
    bundle_root: Path,
) -> list[dict[str, object]]:
    text_map = packed_ref_maps(packed_manifest, "text_texture_refs")
    gdie_map = packed_ref_maps(packed_manifest, "gdie_texture_refs")
    catalog: dict[str, dict[str, object]] = {}

    for row in texture_manifest:
        input_path = Path(row["input"])
        attempt = legacy_export_attempt(row, bundle_root, "png")
        attempt["source_aya_path"] = repo_rel(input_path, repo_root)
        refs = texture_aliases_for_catalog(input_path.name)
        canonical_ref = choose_texture_ref(refs, input_path.stem)
        entry = catalog.setdefault(
            canonical_ref,
            {
                "catalog_id": f"texture:{canonical_ref}",
                "kind": "texture",
                "canonical_ref": canonical_ref,
                "aliases": sorted(refs) if refs else [canonical_ref],
                "source_aya_paths": [],
                "source_roots": set(),
                "loose_export_pngs": [],
                "export_records": [],
                "packed_text_ref_count": text_map.get(canonical_ref, {}).get("count", 0),
                "gdie_ref_count": gdie_map.get(canonical_ref, {}).get("count", 0),
            },
        )
        entry["aliases"] = sorted(set(entry["aliases"]) | refs)
        entry["source_aya_paths"].append(repo_rel(input_path, repo_root))
        entry["source_roots"].add(input_path.parent.name.lower())
        entry["export_records"].append(attempt)

    out: list[dict[str, object]] = []
    for key in sorted(catalog):
        entry = catalog[key]
        source_paths = sorted(set(entry["source_aya_paths"]))
        export_paths = sorted(set(entry["loose_export_pngs"]))
        packed_text = entry["packed_text_ref_count"]
        gdie = entry["gdie_ref_count"]
        out.append(
            {
                "catalog_id": entry["catalog_id"],
                "kind": entry["kind"],
                "canonical_ref": entry["canonical_ref"],
                "aliases": entry["aliases"],
                "description": None,
                "description_status": "not-visually-reviewed",
                "source_aya_count": len(source_paths),
                "source_aya_paths": source_paths,
                "source_roots": sorted(entry["source_roots"]),
                "export_png_count": len(export_paths),
                "export_png_paths": export_paths,
                "export_records": sorted(entry["export_records"], key=lambda value: json.dumps(value, sort_keys=True)),
                "packed_text_ref_count": packed_text,
                "gdie_ref_count": gdie,
                "total_packed_ref_count": packed_text + gdie,
                "referenced_in_packed": (packed_text + gdie) > 0,
            }
        )
    return out


def build_loose_mesh_catalog(
    mesh_manifest: list[dict[str, object]],
    packed_manifest: dict[str, object],
    repo_root: Path,
    bundle_root: Path,
) -> list[dict[str, object]]:
    reference_map = packed_ref_maps(packed_manifest, "reference_mesh_refs")
    gdie_map = packed_ref_maps(packed_manifest, "gdie_mesh_refs")
    catalog: dict[str, dict[str, object]] = {}

    for row in mesh_manifest:
        input_path = Path(row["input"])
        attempt = legacy_export_attempt(row, bundle_root, "fbx")
        attempt["source_aya_path"] = repo_rel(input_path, repo_root)
        aliases = mesh_aliases_from_loose_name(input_path.name)
        canonical_ref = choose_mesh_ref(aliases)
        entry = catalog.setdefault(
            canonical_ref,
            {
                "catalog_id": f"mesh:{canonical_ref}",
                "kind": "loose_mesh",
                "canonical_ref": canonical_ref,
                "aliases": aliases,
                "source_aya_paths": [],
                "export_fbx_paths": [],
                "export_records": [],
                "packed_reference_count": reference_map.get(canonical_ref, {}).get("count", 0),
                "gdie_ref_count": gdie_map.get(canonical_ref, {}).get("count", 0),
            },
        )
        entry["aliases"] = sorted(set(entry["aliases"]) | set(aliases))
        entry["source_aya_paths"].append(repo_rel(input_path, repo_root))
        entry["export_records"].append(attempt)

    out: list[dict[str, object]] = []
    for key in sorted(catalog):
        entry = catalog[key]
        source_paths = sorted(set(entry["source_aya_paths"]))
        export_paths = sorted(set(entry["export_fbx_paths"]))
        packed_ref = entry["packed_reference_count"]
        gdie = entry["gdie_ref_count"]
        out.append(
            {
                "catalog_id": entry["catalog_id"],
                "kind": entry["kind"],
                "canonical_ref": entry["canonical_ref"],
                "aliases": entry["aliases"],
                "description": None,
                "description_status": "not-visually-reviewed",
                "source_aya_count": len(source_paths),
                "source_aya_paths": source_paths,
                "export_fbx_count": len(export_paths),
                "export_fbx_paths": export_paths,
                "export_records": sorted(entry["export_records"], key=lambda value: json.dumps(value, sort_keys=True)),
                "packed_reference_count": packed_ref,
                "gdie_ref_count": gdie,
                "total_packed_ref_count": packed_ref + gdie,
                "referenced_in_packed": (packed_ref + gdie) > 0,
            }
        )
    return out


def build_embedded_mesh_catalog(
    embedded_manifest: list[dict[str, object]],
    repo_root: Path,
    bundle_root: Path,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in embedded_manifest:
        input_path = Path(row["input"])
        attempt = legacy_export_attempt(row, bundle_root, "fbx")
        attempt["source_body_path"] = repo_rel(input_path, repo_root)
        source_archive = input_path.parent.name
        body_name = input_path.stem
        out.append(
            {
                "catalog_id": f"embedded_mesh:{source_archive}/{body_name}",
                "kind": "embedded_mesh",
                "description": None,
                "description_status": "not-visually-reviewed",
                "source_archive": source_archive,
                "body_name": body_name,
                "source_body_path": repo_rel(input_path, repo_root),
                "export_fbx_path": None,
                "export_records": [attempt],
            }
        )
    id_counts = Counter(item["catalog_id"] for item in out)
    for entry in out:
        # Legacy archive/body names are lookup aliases, not unique content/occurrence identities.
        entry["logical_id_ambiguous"] = id_counts[entry["catalog_id"]] > 1
    return sorted(out, key=lambda item: (item["catalog_id"], item["source_body_path"],
                                        json.dumps(item, sort_keys=True)))


def build_video_catalog(video_manifest: dict[str, object]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in video_manifest["files"]:
        relative_path = row["relative_path"].replace("/", "\\")
        out.append(
            {
                "catalog_id": f"video:{relative_path.lower()}",
                "kind": "video",
                "relative_path": relative_path,
                "family": row["family"],
                "sequence_id": row["sequence_id"],
                "size": row["size"],
                "sha256": row["sha256"],
                "magic": row["magic"],
            }
        )
    return out


def build_language_catalog(language_matrix: dict[str, object]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in language_matrix["rows"]:
        named_text_count = sum(1 for item in row["languages"].values() if item["text"])
        named_audio_count = sum(1 for item in row["languages"].values() if item["audio"])
        out.append(
            {
                "catalog_id": f"language:{row['id']}",
                "kind": "language_row",
                "id": row["id"],
                "hex": row["hex"],
                "name": row["name"],
                "language_count": len(row["languages"]),
                "text_present_count": named_text_count,
                "audio_present_count": named_audio_count,
                "languages": row["languages"],
            }
        )
    return out


def _goodie_index_from_archive(archive_path: str) -> int | None:
    archive_name = Path(archive_path).name.lower()
    prefix = "goodie_"
    suffix = "_res_pc.aya"
    if not archive_name.startswith(prefix) or not archive_name.endswith(suffix):
        return None

    try:
        return int(archive_name[len(prefix) : -len(suffix)])
    except ValueError:
        return None


def _language_text(row: dict[str, object]) -> str:
    languages = row.get("languages", {})
    if not isinstance(languages, dict):
        return ""

    for key in ("english", "american"):
        item = languages.get(key)
        if isinstance(item, dict) and item.get("text"):
            return str(item["text"])

    for item in languages.values():
        if isinstance(item, dict) and item.get("text"):
            return str(item["text"])
    return ""


def _goodie_title_map(language_rows: list[dict[str, object]]) -> dict[int, str]:
    titles: dict[int, str] = {}
    for row in language_rows:
        name = str(row.get("name", ""))
        match = re.fullmatch(r"GOODIE_TEXT_(\d+)_TITLE", name)
        if not match:
            continue

        title = _language_text(row).strip()
        if not title:
            continue

        titles[int(match.group(1)) - 1] = title
    return titles


def _goodie_title_from_ref(index: int, texture_refs: list[str], mesh_refs: list[str], video_sequence_id: str) -> str:
    if video_sequence_id:
        return f"Goodie {index:03d} - Cutscene {video_sequence_id}"

    ref = mesh_refs[0] if mesh_refs else texture_refs[0] if texture_refs else ""
    if not ref:
        return f"Goodie {index:03d}"

    stem = Path(ref.replace("\\", "/")).stem
    for prefix in ("ca_fc_", "ca_fu_", "ca_mu_", "ca_ma_", "ca_fa_", "ca_be_", "ca_boss_", "ca_cl_"):
        if stem.lower().startswith(prefix):
            stem = stem[len(prefix) :]
            break

    label = " ".join(part for part in stem.replace("-", "_").split("_") if part)
    return f"Goodie {index:03d} - {label.title()}" if label else f"Goodie {index:03d}"


def _goodie_source_type(index: int) -> str:
    if index <= 7:
        return "Artwork"
    if index in (12, 13, 24, 33, 34, 35):
        return "Artwork"
    if index <= 57:
        return "Model"
    if index <= 65:
        return "Artwork"
    if index <= 70:
        return "Level"
    if index <= 74:
        return "Artwork"
    if index == 75:
        return "Video"
    if index == 76:
        return "Model"
    if index == 77:
        return "Video"
    if index > 200:
        return "Video"
    return "Artwork"


def _goodie_video(
    index: int,
    video_by_sequence: dict[str, dict[str, object]],
    video_by_relative: dict[str, dict[str, object]],
) -> tuple[str, dict[str, object] | None]:
    if 201 <= index <= 231:
        sequence_id = f"{index - 200:02d}"
        return sequence_id, video_by_sequence.get(sequence_id)
    if index == 232:
        return "33", video_by_sequence.get("33")
    if index == 75:
        return "gill_m_on_a_fork", video_by_relative.get("gill_m_on_a_fork.vid")
    if index == 77:
        return "UsTheMovie", video_by_relative.get("usthemovie.vid")
    return "", None


def build_goodie_catalog(
    packed_manifest: dict[str, object],
    videos: list[dict[str, object]],
    language_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    goodie_titles = _goodie_title_map(language_rows)
    video_by_sequence = {
        item["sequence_id"]: item
        for item in videos
        if item.get("family") == "cutscene_numeric" and item.get("sequence_id")
    }
    video_by_relative = {
        str(item["relative_path"]).replace("\\", "/").lower(): item
        for item in videos
        if item.get("relative_path")
    }
    rows: list[dict[str, object]] = []

    for item in packed_manifest.get("gdie_families", []):
        index = _goodie_index_from_archive(str(item.get("archive", "")))
        if index is None:
            continue

        texture_refs = [str(ref) for ref in item.get("texture_refs", [])]
        mesh_refs = [str(ref) for ref in item.get("mesh_refs", [])]
        video_sequence_id, video = _goodie_video(index, video_by_sequence, video_by_relative)
        source_title = goodie_titles.get(index, "")
        content_kind = _goodie_source_type(index)

        rows.append(
            {
                "catalog_id": f"goodie:{index:03d}",
                "kind": "goodie",
                "index": index,
                "display_name": (
                    f"Goodie {index:03d} - {source_title}"
                    if source_title
                    else _goodie_title_from_ref(index, texture_refs, mesh_refs, video_sequence_id)
                ),
                "content_kind": content_kind,
                "source_title": source_title,
                "source_archive": Path(str(item.get("archive", ""))).name,
                "gdie_family": item.get("family", ""),
                "texture_refs": texture_refs,
                "mesh_refs": mesh_refs,
                "primary_texture_ref": texture_refs[0] if texture_refs else "",
                "primary_mesh_ref": mesh_refs[0] if mesh_refs else "",
                "video_sequence_id": video_sequence_id,
                "video_catalog_id": video.get("catalog_id", "") if video else "",
                "video_relative_path": video.get("relative_path", "") if video else "",
            }
        )

    if "33" in video_by_sequence:
        video = video_by_sequence["33"]
        rows.append(
            {
                "catalog_id": "goodie:232",
                "kind": "goodie",
                "index": 232,
                "display_name": "Goodie 232 - Cutscene 33",
                "content_kind": "Video",
                "source_title": "",
                "source_archive": "",
                "gdie_family": "video_only",
                "texture_refs": [],
                "mesh_refs": [],
                "primary_texture_ref": "",
                "primary_mesh_ref": "",
                "video_sequence_id": "33",
                "video_catalog_id": video.get("catalog_id", ""),
                "video_relative_path": video.get("relative_path", ""),
            }
        )

    return sorted(rows, key=lambda item: item["index"])


def build_summary(
    textures: list[dict[str, object]],
    loose_meshes: list[dict[str, object]],
    embedded_meshes: list[dict[str, object]],
    videos: list[dict[str, object]],
    language_rows: list[dict[str, object]],
    goodies: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "texture_catalog_entries": len(textures),
        "texture_entries_referenced_in_packed": sum(1 for item in textures if item["referenced_in_packed"]),
        "texture_entries_loose_only": sum(1 for item in textures if not item["referenced_in_packed"]),
        "texture_entries_with_multiple_source_variants": sum(1 for item in textures if item["source_aya_count"] > 1),
        "loose_mesh_catalog_entries": len(loose_meshes),
        "loose_mesh_entries_referenced_in_packed": sum(1 for item in loose_meshes if item["referenced_in_packed"]),
        "loose_mesh_entries_loose_only": sum(1 for item in loose_meshes if not item["referenced_in_packed"]),
        "embedded_mesh_catalog_entries": len(embedded_meshes),
        "video_catalog_entries": len(videos),
        "language_catalog_entries": len(language_rows),
        "goodie_catalog_entries": len(goodies),
        "total_catalog_entries": len(textures)
        + len(loose_meshes)
        + len(embedded_meshes)
        + len(videos)
        + len(language_rows)
        + len(goodies),
        "video_family_counts": dict(sorted(Counter(item["family"] for item in videos).items())),
        "goodie_family_counts": dict(sorted(Counter(item["content_kind"] for item in goodies).items())),
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument(
        "--bundle-root",
        type=Path,
        help="Single generated export root that contains every catalog export path",
    )
    ap.add_argument("--packed-manifest", type=Path, default=Path(".artifacts/aya-assets/packed-manifest.json"))
    ap.add_argument("--texture-manifest", type=Path, default=Path(".artifacts/asset-export/loose-textures/manifest.json"))
    ap.add_argument("--loose-mesh-manifest", type=Path, default=Path(".artifacts/asset-export/loose-meshes/manifest.json"))
    ap.add_argument("--embedded-mesh-manifest", type=Path, default=Path(".artifacts/asset-export/embedded-meshes/manifest.json"))
    ap.add_argument("--video-manifest", type=Path, default=Path(".artifacts/video-manifest/manifest.json"))
    ap.add_argument("--language-matrix", type=Path, default=Path(".artifacts/language-export/merged_matrix.json"))
    ap.add_argument("--out-dir", type=Path, default=Path(".artifacts/asset-catalog"))
    ap.add_argument("--self-test", action="store_true", help="Run built-in catalog assembly checks without game assets")
    ap.add_argument("--inspect-source-root", type=Path,
                    help="Opt in to bounded metadata reads of manifest-selected sources below this explicit root; no discovery")
    return ap.parse_args()


def validate_catalog_output_layout(bundle_root: Path, out_dir: Path) -> None:
    expected_catalog_dir = bundle_root / "asset_catalog"
    if out_dir != expected_catalog_dir:
        raise SystemExit("--out-dir must be the asset_catalog child directory of --bundle-root")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp)
        packed_manifest = {
            "text_texture_refs": [
                {"ref": "meshtex\\cloud.tga", "count": 2, "match_count": 1, "matches": ["001_res_PC.aya"]},
            ],
            "gdie_texture_refs": [
                {"ref": "goodie\\icon.tga", "count": 1, "match_count": 1, "matches": ["goodie_08_res_PC.aya"]},
            ],
            "reference_mesh_refs": [
                {"ref": "fighter", "count": 3, "match_count": 1, "matches": ["base_res_PC.aya"]},
            ],
            "gdie_mesh_refs": [
                {"ref": "reward", "count": 1, "match_count": 1, "matches": ["goodie_08_res_PC.aya"]},
            ],
            "gdie_families": [
                {
                    "archive": str(repo_root / "game" / "data" / "resources" / "goodie_08_res_PC.aya"),
                    "family": "texture_mesh",
                    "texture_refs": ["goodie\\icon.tga"],
                    "mesh_refs": ["reward"],
                }
            ],
        }
        texture_manifest = [
            {
                "input": str(repo_root / "textures" / "meshtex%cloud.tga.aya"),
                "output": str(repo_root / "exports" / "cloud.png"),
            },
        ]
        loose_mesh_manifest = [
            {
                "input": str(repo_root / "meshes" / "m_fighter.aya"),
                "output": str(repo_root / "exports" / "fighter.fbx"),
            },
        ]
        embedded_mesh_manifest = [
            {
                "input": str(repo_root / "embedded" / "001_res_PC.aya" / "body00.cmsbody"),
                "output": str(repo_root / "exports" / "body00.fbx"),
            },
        ]
        video_manifest = {
            "files": [
                {
                    "relative_path": "briefings/PC_100_exact.vid",
                    "family": "briefing",
                    "sequence_id": "100",
                    "size": 16,
                    "sha256": "0" * 64,
                    "magic": "BIKi",
                },
                {
                    "relative_path": "cutscenes/33.vid",
                    "family": "cutscene_numeric",
                    "sequence_id": "33",
                    "size": 32,
                    "sha256": "1" * 64,
                    "magic": "BIKi",
                },
            ]
        }
        language_matrix = {
            "rows": [
                {
                    "id": 1,
                    "hex": "0x0001",
                    "name": "Sample",
                    "languages": {
                        "en": {"text": "Hello", "audio": "sample.ogg"},
                        "fr": {"text": "", "audio": ""},
                    },
                },
                {
                    "id": 2,
                    "hex": "0x0002",
                    "name": "GOODIE_TEXT_9_TITLE",
                    "languages": {
                        "english": {"text": "Test Reward", "audio": ""},
                        "american": {"text": "Test Reward", "audio": ""},
                    },
                }
            ]
        }

        textures = build_texture_catalog(texture_manifest, packed_manifest, repo_root, repo_root)
        loose_meshes = build_loose_mesh_catalog(loose_mesh_manifest, packed_manifest, repo_root, repo_root)
        embedded_meshes = build_embedded_mesh_catalog(embedded_mesh_manifest, repo_root, repo_root)
        videos = build_video_catalog(video_manifest)
        language_rows = build_language_catalog(language_matrix)
        goodies = build_goodie_catalog(packed_manifest, videos, language_rows)
        summary = build_summary(textures, loose_meshes, embedded_meshes, videos, language_rows, goodies)

        assert summary["texture_catalog_entries"] == 1
        assert summary["texture_entries_referenced_in_packed"] == 1
        assert summary["loose_mesh_catalog_entries"] == 1
        assert summary["loose_mesh_entries_referenced_in_packed"] == 1
        assert summary["embedded_mesh_catalog_entries"] == 1
        assert summary["video_catalog_entries"] == 2
        assert summary["language_catalog_entries"] == 2
        assert summary["goodie_catalog_entries"] == 2
        assert summary["total_catalog_entries"] == 9
        assert summary["video_family_counts"] == {"briefing": 1, "cutscene_numeric": 1}
        assert summary["goodie_family_counts"] == {"Model": 1, "Video": 1}
        assert textures[0]["canonical_ref"] == "meshtex\\cloud.tga"
        assert textures[0]["export_png_paths"] == []
        assert textures[0]["export_records"][0]["requested_output_path"] == "exports\\cloud.png"
        assert loose_meshes[0]["canonical_ref"] == "fighter"
        assert loose_meshes[0]["export_fbx_paths"] == []
        assert loose_meshes[0]["export_records"][0]["requested_output_path"] == "exports\\fighter.fbx"
        assert embedded_meshes[0]["source_archive"] == "001_res_PC.aya"
        assert embedded_meshes[0]["export_fbx_path"] is None
        assert embedded_meshes[0]["export_records"][0]["requested_output_path"] == "exports\\body00.fbx"
        assert language_rows[0]["text_present_count"] == 1
        assert language_rows[0]["audio_present_count"] == 1
        assert goodies[0]["index"] == 8
        assert goodies[0]["content_kind"] == "Model"
        assert goodies[0]["source_title"] == "Test Reward"
        assert goodies[0]["display_name"] == "Goodie 008 - Test Reward"
        assert goodies[1]["index"] == 232
        assert goodies[1]["video_sequence_id"] == "33"

        validate_catalog_output_layout(repo_root, repo_root / "asset_catalog")
        try:
            validate_catalog_output_layout(repo_root, repo_root)
            raise AssertionError("direct catalog output layout should be rejected")
        except SystemExit as exc:
            assert "asset_catalog child" in str(exc)

    print("export_asset_catalog self-test: PASS")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    args.repo_root = args.repo_root.resolve()
    args.out_dir = args.out_dir.resolve()
    bundle_root = (
        args.bundle_root.resolve()
        if args.bundle_root is not None
        else (args.out_dir.parent if args.out_dir.name.lower() == "asset_catalog" else args.out_dir)
    )
    validate_catalog_output_layout(bundle_root, args.out_dir)

    input_paths = (
        args.packed_manifest.resolve(),
        args.texture_manifest.resolve(),
        args.loose_mesh_manifest.resolve(),
        args.embedded_mesh_manifest.resolve(),
        args.video_manifest.resolve(),
        args.language_matrix.resolve(),
    )
    missing_inputs = [path for path in input_paths if not path.is_file()]
    if missing_inputs:
        raise SystemExit(f"catalog input does not exist: {missing_inputs[0]}")

    with SecuredOutputRoot(args.out_dir, protected_sources=input_paths) as output:
        packed_manifest = read_json(input_paths[0])
        texture_manifest = read_json(input_paths[1])
        loose_mesh_manifest = read_json(input_paths[2])
        embedded_mesh_manifest = read_json(input_paths[3])
        video_manifest = read_json(input_paths[4])
        language_matrix = read_json(input_paths[5])

        if args.inspect_source_root is not None:
            # Inspecting a source never authorizes replacing it with a generated catalog. Protect
            # each declared location, including unavailable/rejected rows, without forbidding a
            # safe sibling output under a broad inspection root. Check before any publication.
            declared_sources = []
            for manifest in (texture_manifest, loose_mesh_manifest, embedded_mesh_manifest):
                for declaration in manifest:
                    declared = Path(declaration["input"])
                    if not declared.is_absolute():
                        declared = args.repo_root / declared
                    declared_sources.append(Path(os.path.abspath(declared)))
            validate_disjoint_output_root(args.out_dir, declared_sources)

        textures = build_texture_catalog(texture_manifest, packed_manifest, args.repo_root, bundle_root)
        loose_meshes = build_loose_mesh_catalog(loose_mesh_manifest, packed_manifest, args.repo_root, bundle_root)
        embedded_meshes = build_embedded_mesh_catalog(embedded_mesh_manifest, args.repo_root, bundle_root)
        videos = build_video_catalog(video_manifest)
        language_rows = build_language_catalog(language_matrix)
        goodies = build_goodie_catalog(packed_manifest, videos, language_rows)
        source_inspection = {"status": "notRequested"}
        if args.inspect_source_root is not None:
            source_inspection = inspect_catalog_sources(
                textures, loose_meshes, embedded_meshes,
                source_root=args.inspect_source_root, repo_root=args.repo_root,
                source_manifests=(texture_manifest, loose_mesh_manifest, embedded_mesh_manifest))
        summary = build_summary(textures, loose_meshes, embedded_meshes, videos, language_rows, goodies)

        catalog = {
            "schema_version": CATALOG_SCHEMA_VERSION,
            "path_contract": CATALOG_PATH_CONTRACT,
            "export_verification_contract": CATALOG_EXPORT_CONTRACT,
            "source_inspection": source_inspection,
            "summary": summary,
            "textures": textures,
            "loose_meshes": loose_meshes,
            "embedded_meshes": embedded_meshes,
            "videos": videos,
            "language_rows": language_rows,
            "goodies": goodies,
        }

        output.atomic_write_json(args.out_dir / "summary.json", summary)
        output.atomic_write_json(args.out_dir / "catalog.json", catalog)
        output.atomic_write_json(args.out_dir / "textures.json", textures)
        output.atomic_write_json(args.out_dir / "loose_meshes.json", loose_meshes)
        output.atomic_write_json(args.out_dir / "embedded_meshes.json", embedded_meshes)
        output.atomic_write_json(args.out_dir / "videos.json", videos)
        output.atomic_write_json(args.out_dir / "language_rows.json", language_rows)
        output.atomic_write_json(args.out_dir / "goodies.json", goodies)

    print(json.dumps({"out_dir": str(args.out_dir), "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
