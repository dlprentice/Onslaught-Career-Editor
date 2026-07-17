#!/usr/bin/env python3
"""
Run the full local Battle Engine Aquila asset-extraction backend.

This orchestrates the existing private extraction lanes:
- packed AYA inventory + embedded-body preparation
- headless texture/mesh export harness, one lane per process
- language DAT export
- loose video manifest
- cross-surface asset catalog

Example:
    py -3 tools/export_game_assets.py --game-root game
"""

from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Mapping, Sequence

import aya_archive_inventory as aya_observation
from safe_generated_output import SecuredOutputRoot


EXPORT_OUTCOME_SCHEMA = "onslaught.aya-export-outcome.v1"
EXPORT_LANE_MANIFEST_SCHEMA = "onslaught.aya-export-lane-manifest.v1"
CORPUS_RECONCILIATION_SCHEMA = "onslaught.aya-corpus-reconciliation.v1"
EXPORT_LANES = (
    "looseTextures",
    "looseMeshes",
    "embeddedMeshes",
    "language",
    "video",
    "catalog",
)
EXPORT_STATUSES = (
    "exported",
    "knownUnsupported",
    "rejected",
    "notAttempted",
    "notApplicable",
)
DEPENDENCY_STATUSES = frozenset({"resolved", "missing", "ambiguous", "unresolved"})
DEPENDENCY_TYPES = frozenset(
    {"source", "chunk", "texture", "mesh", "language", "video", "catalog"}
)
OUTPUT_KINDS = frozenset(
    {
        "none",
        "png",
        "fbx",
        "obj",
        "materialReport",
        "languageCorpus",
        "videoManifest",
        "assetCatalog",
    }
)
LANE_OUTPUT_KINDS = {
    "looseTextures": frozenset({"none", "png"}),
    "looseMeshes": frozenset({"none", "fbx"}),
    "embeddedMeshes": frozenset({"none", "fbx", "obj", "materialReport"}),
    "language": frozenset({"none", "languageCorpus"}),
    "video": frozenset({"none", "videoManifest"}),
    "catalog": frozenset({"none", "assetCatalog"}),
}
RECONCILIATION_NONCLAIMS = (
    "not-exhaustive-target-matrix",
    "not-format-completeness",
    "not-runtime-or-render-fidelity",
    "not-successful-full-corpus-extraction",
)
STATUS_REASONS = {
    "exported": frozenset({None}),
    "knownUnsupported": frozenset({"unsupportedFeature", "unsupportedOutputKind"}),
    "rejected": frozenset(
        {
            "invalidManifest",
            "exportFailed",
            "dependencyMissing",
            "dependencyAmbiguous",
            "dependencyUnresolved",
            "sourceRejected",
        }
    ),
    "notAttempted": frozenset(
        {"notRequested", "dependencyMissing", "dependencyAmbiguous", "dependencyUnresolved"}
    ),
    "notApplicable": frozenset({"laneNotApplicable", "sourceRejected"}),
}


class ExportOutcomeError(ValueError):
    """A deterministic rejection of malformed or identity-unsafe export evidence."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _valid_length(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_digest_identity(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"length", "sha256"}:
        raise ExportOutcomeError(f"invalid {label}")
    if not _valid_length(value["length"]) or not _valid_digest(value["sha256"]):
        raise ExportOutcomeError(f"invalid {label}")
    return {"length": value["length"], "sha256": value["sha256"]}


def _observation_index(
    observation_report: Mapping[str, object],
) -> tuple[str, dict[str, dict[str, object]]]:
    if not isinstance(observation_report, dict):
        raise ExportOutcomeError("observation report must be an object")
    try:
        aya_observation.render_observation_records(observation_report)
    except (TypeError, ValueError) as error:
        raise ExportOutcomeError("unaccepted AYA observation universe") from error

    universe_id = observation_report["sourceUniverseId"]
    records = observation_report["archiveRecords"]
    return universe_id, {record["archiveOrdinal"]: record for record in records}


def _validate_target(
    value: object,
    sources: Mapping[str, dict[str, object]],
) -> tuple[dict[str, object], dict[str, object], dict[str, object] | None]:
    if not isinstance(value, dict) or set(value) != {
        "sourceOrdinal",
        "sourceIdentity",
        "chunkIdentity",
    }:
        raise ExportOutcomeError("invalid export target")

    source_ordinal = value["sourceOrdinal"]
    if not isinstance(source_ordinal, str) or source_ordinal not in sources:
        raise ExportOutcomeError("foreign source ordinal")
    source = sources[source_ordinal]
    if value["sourceIdentity"] != source["sourceIdentity"]:
        raise ExportOutcomeError("foreign or ambiguous source identity")

    chunk_identity = value["chunkIdentity"]
    chunk: dict[str, object] | None = None
    if chunk_identity is not None:
        if not isinstance(chunk_identity, dict) or set(chunk_identity) != {
            "chunkOrdinal",
            "declaredLength",
            "payloadSha256",
        }:
            raise ExportOutcomeError("invalid chunk identity")
        chunks = {
            item["chunkOrdinal"]: item for item in source["chunkObservations"]
        }
        chunk_ordinal = chunk_identity["chunkOrdinal"]
        if not isinstance(chunk_ordinal, str) or chunk_ordinal not in chunks:
            raise ExportOutcomeError("foreign chunk ordinal")
        chunk = chunks[chunk_ordinal]
        accepted_identity = {
            "chunkOrdinal": chunk["chunkOrdinal"],
            "declaredLength": chunk["declaredLength"],
            "payloadSha256": chunk["payloadSha256"],
        }
        if chunk_identity != accepted_identity:
            raise ExportOutcomeError("foreign or ambiguous chunk identity")

    target = {
        "sourceOrdinal": source_ordinal,
        "sourceIdentity": source["sourceIdentity"],
        "chunkIdentity": chunk_identity,
    }
    return target, source, chunk


def _target_key(value: Mapping[str, object]) -> bytes:
    return _canonical_bytes(
        {
            "sourceOrdinal": value["sourceOrdinal"],
            "sourceIdentity": value["sourceIdentity"],
            "chunkIdentity": value["chunkIdentity"],
        }
    )


def _validate_dependencies(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise ExportOutcomeError("dependencies must be a list")
    dependencies: list[dict[str, object]] = []
    identities: set[bytes] = set()
    for dependency in value:
        if not isinstance(dependency, dict) or set(dependency) != {
            "dependencyType",
            "identity",
            "status",
        }:
            raise ExportOutcomeError("invalid dependency")
        dependency_type = dependency["dependencyType"]
        status = dependency["status"]
        if (
            not isinstance(dependency_type, str)
            or dependency_type not in DEPENDENCY_TYPES
            or not isinstance(status, str)
            or status not in DEPENDENCY_STATUSES
        ):
            raise ExportOutcomeError("unknown dependency type or status")
        identity = _validate_digest_identity(dependency["identity"], "dependency identity")
        identity_key = _canonical_bytes([dependency_type, identity])
        if identity_key in identities:
            raise ExportOutcomeError("duplicate or ambiguous dependency")
        identities.add(identity_key)
        dependencies.append(
            {
                "dependencyType": dependency_type,
                "identity": identity,
                "status": status,
            }
        )
    return sorted(dependencies, key=_canonical_bytes)


def _validate_terminal_record(
    value: object,
    sources: Mapping[str, dict[str, object]],
) -> tuple[dict[str, object], dict[str, object], dict[str, object] | None]:
    if not isinstance(value, dict) or set(value) != {
        "sourceOrdinal",
        "sourceIdentity",
        "chunkIdentity",
        "dependencies",
        "deterministicOutputDigest",
        "deterministicOutputStatus",
        "exportStatus",
        "outputKind",
        "reason",
    }:
        raise ExportOutcomeError("invalid terminal export record")
    target, source, chunk = _validate_target(
        {key: value[key] for key in ("sourceOrdinal", "sourceIdentity", "chunkIdentity")},
        sources,
    )
    status = value["exportStatus"]
    reason = value["reason"]
    output_kind = value["outputKind"]
    digest_status = value["deterministicOutputStatus"]
    digest = value["deterministicOutputDigest"]
    if (
        not isinstance(status, str)
        or status not in EXPORT_STATUSES
        or (reason is not None and not isinstance(reason, str))
        or reason not in STATUS_REASONS.get(status, ())
    ):
        raise ExportOutcomeError("unknown export status or reason")
    if not isinstance(output_kind, str) or output_kind not in OUTPUT_KINDS:
        raise ExportOutcomeError("unknown output kind")
    if not isinstance(digest_status, str) or digest_status not in {
        "verified",
        "unverified",
        "failed",
        "notApplicable",
    }:
        raise ExportOutcomeError("unknown deterministic output status")
    if digest_status in {"verified", "unverified"}:
        if status != "exported" or output_kind == "none" or not _valid_digest(digest):
            raise ExportOutcomeError("invalid deterministic output digest")
    elif digest is not None:
        raise ExportOutcomeError("non-output record carries a deterministic digest")
    if digest_status == "failed" and status != "rejected":
        raise ExportOutcomeError("failed digest status requires rejected export")
    if digest_status == "notApplicable" and status in {"exported", "rejected"}:
        raise ExportOutcomeError("terminal status disagrees with deterministic output status")
    if source["observationStatus"] == "rejected" and (
        status == "exported"
        or output_kind != "none"
        or digest_status in {"verified", "unverified"}
    ):
        raise ExportOutcomeError("rejected source cannot carry output")
    return (
        {
            **target,
            "dependencies": _validate_dependencies(value["dependencies"]),
            "deterministicOutputDigest": digest,
            "deterministicOutputStatus": digest_status,
            "exportStatus": status,
            "outputKind": output_kind,
            "reason": reason,
        },
        source,
        chunk,
    )


def _observed_fields(
    source: Mapping[str, object],
    chunk: Mapping[str, object] | None,
) -> dict[str, object]:
    selected_chunks = source["chunkObservations"] if chunk is None else [chunk]
    flags = {
        "archiveObserved"
        if source["observationStatus"] == "observed"
        else "archiveRejected"
    }
    if chunk is not None:
        flags.add("chunkObserved")
    if any(item["bodyCandidateObservations"] for item in selected_chunks):
        flags.add("meshBodyCandidateObserved")
    return {
        "observedExtensions": [source["extension"]],
        "observedFeatureFlags": sorted(flags),
        "observedTags": [
            {"tagAscii": item["tagAscii"], "tagHex": item["tagHex"]}
            for item in selected_chunks
        ],
    }


def _validate_lane_output_kind(lane: str, record: Mapping[str, object]) -> None:
    if record["outputKind"] not in LANE_OUTPUT_KINDS[lane]:
        raise ExportOutcomeError("lane/output kind mismatch")


def produce_export_outcomes(
    observation_report: Mapping[str, object],
    manifests: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Validate identity-bound lane manifests and return path-free terminal outcomes."""

    universe_id, sources = _observation_index(observation_report)
    output_records: list[dict[str, object]] = []
    global_keys: set[bytes] = set()
    for manifest in manifests:
        if not isinstance(manifest, dict) or set(manifest) != {
            "expectedRecords",
            "lane",
            "records",
            "schemaVersion",
            "sourceUniverseId",
        }:
            raise ExportOutcomeError("invalid lane manifest envelope")
        if manifest["schemaVersion"] != EXPORT_LANE_MANIFEST_SCHEMA:
            raise ExportOutcomeError("unaccepted lane manifest version")
        if manifest["sourceUniverseId"] != universe_id:
            raise ExportOutcomeError("foreign export source universe")
        lane = manifest["lane"]
        if not isinstance(lane, str) or lane not in EXPORT_LANES:
            raise ExportOutcomeError("unknown export lane")
        if not isinstance(manifest["expectedRecords"], list) or not isinstance(
            manifest["records"], list
        ):
            raise ExportOutcomeError("manifest records must be lists")

        expected: dict[bytes, dict[str, object]] = {}
        for raw_target in manifest["expectedRecords"]:
            accepted_target, _, _ = _validate_target(raw_target, sources)
            key = _target_key(accepted_target)
            if key in expected:
                raise ExportOutcomeError("duplicate or ambiguous expected export record")
            expected[key] = accepted_target

        actual: dict[bytes, tuple[dict[str, object], dict[str, object], dict[str, object] | None]] = {}
        for raw_record in manifest["records"]:
            accepted = _validate_terminal_record(raw_record, sources)
            _validate_lane_output_kind(lane, accepted[0])
            key = _target_key(accepted[0])
            if key in actual:
                raise ExportOutcomeError("duplicate or ambiguous terminal export record")
            actual[key] = accepted
        if set(actual) != set(expected):
            raise ExportOutcomeError("missing or unexpected terminal export record")

        for key, (record, source, chunk) in actual.items():
            global_key = _canonical_bytes([lane, json.loads(key.decode("ascii"))])
            if global_key in global_keys:
                raise ExportOutcomeError("duplicate lane target across manifests")
            global_keys.add(global_key)
            output_records.append({"lane": lane, **record, **_observed_fields(source, chunk)})

    output_records.sort(key=_canonical_bytes)
    return {
        "exportRecords": output_records,
        "producer": {"name": "export_game_assets", "producerVersion": 1},
        "schemaVersion": EXPORT_OUTCOME_SCHEMA,
        "sourceObservationSchemaVersion": aya_observation.OBSERVATION_SCHEMA,
        "sourceUniverseId": universe_id,
    }


def render_export_outcomes(report: Mapping[str, object]) -> bytes:
    """Render a producer result as deterministic path-free ASCII JSON."""

    if not isinstance(report, dict) or set(report) != {
        "exportRecords",
        "producer",
        "schemaVersion",
        "sourceObservationSchemaVersion",
        "sourceUniverseId",
    }:
        raise ExportOutcomeError("invalid export outcome envelope")
    if report["schemaVersion"] != EXPORT_OUTCOME_SCHEMA or report["producer"] != {
        "name": "export_game_assets",
        "producerVersion": 1,
    }:
        raise ExportOutcomeError("unaccepted export outcome producer")
    if report["sourceObservationSchemaVersion"] != aya_observation.OBSERVATION_SCHEMA:
        raise ExportOutcomeError("unaccepted source observation version")
    if not _valid_digest(report["sourceUniverseId"]):
        raise ExportOutcomeError("invalid export outcome universe")
    if not isinstance(report["exportRecords"], list):
        raise ExportOutcomeError("invalid export outcome records")
    return _canonical_bytes(report) + b"\n"


def _validated_export_records(
    outcome_report: Mapping[str, object],
    universe_id: str,
    sources: Mapping[str, dict[str, object]],
) -> list[dict[str, object]]:
    if not isinstance(outcome_report, dict) or set(outcome_report) != {
        "exportRecords",
        "producer",
        "schemaVersion",
        "sourceObservationSchemaVersion",
        "sourceUniverseId",
    }:
        raise ExportOutcomeError("invalid export outcome envelope")
    if outcome_report["schemaVersion"] != EXPORT_OUTCOME_SCHEMA or outcome_report[
        "producer"
    ] != {"name": "export_game_assets", "producerVersion": 1}:
        raise ExportOutcomeError("unaccepted export outcome producer")
    if outcome_report["sourceObservationSchemaVersion"] != aya_observation.OBSERVATION_SCHEMA:
        raise ExportOutcomeError("unaccepted source observation version")
    if outcome_report["sourceUniverseId"] != universe_id:
        raise ExportOutcomeError("foreign export source universe")
    raw_records = outcome_report["exportRecords"]
    if not isinstance(raw_records, list):
        raise ExportOutcomeError("invalid export outcome records")

    terminal_keys = {
        "sourceOrdinal",
        "sourceIdentity",
        "chunkIdentity",
        "dependencies",
        "deterministicOutputDigest",
        "deterministicOutputStatus",
        "exportStatus",
        "outputKind",
        "reason",
    }
    observed_keys = {"observedExtensions", "observedFeatureFlags", "observedTags"}
    accepted_records: list[dict[str, object]] = []
    global_keys: set[bytes] = set()
    for raw_record in raw_records:
        if not isinstance(raw_record, dict) or set(raw_record) != {
            "lane",
            *terminal_keys,
            *observed_keys,
        }:
            raise ExportOutcomeError("invalid export outcome record")
        lane = raw_record["lane"]
        if not isinstance(lane, str) or lane not in EXPORT_LANES:
            raise ExportOutcomeError("unknown export lane")
        terminal, source, chunk = _validate_terminal_record(
            {key: raw_record[key] for key in terminal_keys}, sources
        )
        _validate_lane_output_kind(lane, terminal)
        observed = _observed_fields(source, chunk)
        if {key: raw_record[key] for key in observed_keys} != observed:
            raise ExportOutcomeError("export record observation fields disagree with source")
        accepted = {"lane": lane, **terminal, **observed}
        if raw_record != accepted:
            raise ExportOutcomeError("noncanonical export outcome record")
        global_key = _canonical_bytes([lane, json.loads(_target_key(terminal).decode("ascii"))])
        if global_key in global_keys:
            raise ExportOutcomeError("duplicate lane target in export outcomes")
        global_keys.add(global_key)
        accepted_records.append(accepted)

    if accepted_records != sorted(accepted_records, key=_canonical_bytes):
        raise ExportOutcomeError("export outcome records are not in canonical order")
    return accepted_records


def produce_corpus_reconciliation(
    observation_report: Mapping[str, object],
    outcome_report: Mapping[str, object],
) -> dict[str, object]:
    """Reconcile bounded observed surfaces without claiming exhaustive extraction."""

    universe_id, sources = _observation_index(observation_report)
    records = _validated_export_records(outcome_report, universe_id, sources)

    expected_archives = set(sources)
    if not expected_archives:
        raise ExportOutcomeError("empty observation universe cannot be reconciled")
    covered_archives = {record["sourceOrdinal"] for record in records}
    if covered_archives != expected_archives:
        raise ExportOutcomeError("incomplete observed archive coverage")

    expected_extensions = {source["extension"] for source in sources.values()}
    covered_extensions = {
        extension for record in records for extension in record["observedExtensions"]
    }
    if covered_extensions != expected_extensions:
        raise ExportOutcomeError("incomplete observed extension coverage")

    expected_tags = {
        _canonical_bytes({"tagAscii": chunk["tagAscii"], "tagHex": chunk["tagHex"]})
        for source in sources.values()
        for chunk in source["chunkObservations"]
    }
    if not expected_tags:
        raise ExportOutcomeError("observation universe has no tag surfaces")
    covered_tags = {
        _canonical_bytes(tag) for record in records for tag in record["observedTags"]
    }
    if covered_tags != expected_tags:
        raise ExportOutcomeError("incomplete observed tag coverage")

    covered_lanes = {record["lane"] for record in records}
    if covered_lanes != set(EXPORT_LANES):
        raise ExportOutcomeError("incomplete export lane coverage")

    expected_output_kinds = set(OUTPUT_KINDS) - {"none"}
    verified_records = [
        record
        for record in records
        if record["exportStatus"] == "exported"
        and record["deterministicOutputStatus"] == "verified"
        and _valid_digest(record["deterministicOutputDigest"])
    ]
    covered_output_kinds = {
        record["outputKind"] for record in verified_records
    } - {"none"}
    if covered_output_kinds != expected_output_kinds:
        raise ExportOutcomeError("incomplete verified output-family coverage")

    status_counts = {
        status: sum(record["exportStatus"] == status for record in records)
        for status in EXPORT_STATUSES
    }
    return {
        "evidenceScope": "terminal-outcome-surface-reconciliation",
        "nonClaims": list(RECONCILIATION_NONCLAIMS),
        "observedSurfaceCoverageStatus": "complete",
        "coveredLanes": sorted(covered_lanes),
        "coveredOutputKinds": sorted(covered_output_kinds),
        "exportOutcomeSha256": hashlib.sha256(
            render_export_outcomes(outcome_report)
        ).hexdigest(),
        "observedArchiveCount": len(expected_archives),
        "observedExtensions": sorted(expected_extensions),
        "observedTags": [json.loads(tag.decode("ascii")) for tag in sorted(expected_tags)],
        "producer": {"name": "export_game_assets", "producerVersion": 1},
        "schemaVersion": CORPUS_RECONCILIATION_SCHEMA,
        "sourceObservationSha256": hashlib.sha256(
            aya_observation.render_observation_records(observation_report)
        ).hexdigest(),
        "sourceUniverseId": universe_id,
        "terminalOutcomeCount": len(records),
        "terminalStatusCounts": {
            status: count for status, count in status_counts.items() if count
        },
        "verifiedOutputCount": len(verified_records),
    }


def render_corpus_reconciliation(report: Mapping[str, object]) -> bytes:
    """Render a validated reconciliation result as deterministic path-free ASCII JSON."""

    if not isinstance(report, dict) or set(report) != {
        "coveredLanes",
        "coveredOutputKinds",
        "evidenceScope",
        "exportOutcomeSha256",
        "nonClaims",
        "observedArchiveCount",
        "observedExtensions",
        "observedSurfaceCoverageStatus",
        "observedTags",
        "producer",
        "schemaVersion",
        "sourceObservationSha256",
        "sourceUniverseId",
        "terminalOutcomeCount",
        "terminalStatusCounts",
        "verifiedOutputCount",
    }:
        raise ExportOutcomeError("invalid corpus reconciliation envelope")
    if report["schemaVersion"] != CORPUS_RECONCILIATION_SCHEMA or report[
        "producer"
    ] != {"name": "export_game_assets", "producerVersion": 1}:
        raise ExportOutcomeError("unaccepted corpus reconciliation producer")
    if report["evidenceScope"] != "terminal-outcome-surface-reconciliation" or report[
        "nonClaims"
    ] != list(RECONCILIATION_NONCLAIMS):
        raise ExportOutcomeError("invalid corpus reconciliation scope")
    if report["observedSurfaceCoverageStatus"] != "complete":
        raise ExportOutcomeError("incomplete corpus reconciliation")
    if not _valid_digest(report["sourceUniverseId"]) or not _valid_digest(
        report["exportOutcomeSha256"]
    ) or not _valid_digest(
        report["sourceObservationSha256"]
    ):
        raise ExportOutcomeError("invalid corpus reconciliation identity")
    if not _valid_length(report["observedArchiveCount"]) or report[
        "observedArchiveCount"
    ] == 0:
        raise ExportOutcomeError("invalid observed archive count")
    if report["coveredLanes"] != sorted(EXPORT_LANES):
        raise ExportOutcomeError("invalid reconciled export lanes")
    if report["coveredOutputKinds"] != sorted(OUTPUT_KINDS - {"none"}):
        raise ExportOutcomeError("invalid reconciled output kinds")
    extensions = report["observedExtensions"]
    if (
        not isinstance(extensions, list)
        or not extensions
        or any(
            not isinstance(extension, str) or extension not in {".aya", "other"}
            for extension in extensions
        )
        or extensions != sorted(set(extensions))
    ):
        raise ExportOutcomeError("invalid reconciled extensions")
    tags = report["observedTags"]
    if (
        not isinstance(tags, list)
        or not tags
        or any(
            not isinstance(tag, dict)
            or set(tag) != {"tagAscii", "tagHex"}
            or not isinstance(tag["tagAscii"], str)
            or len(tag["tagAscii"]) != 4
            or not isinstance(tag["tagHex"], str)
            or len(tag["tagHex"]) != 8
            or any(character not in "0123456789abcdef" for character in tag["tagHex"])
            or aya_observation._decode_tag(bytes.fromhex(tag["tagHex"]))
            != tag["tagAscii"]
            for tag in tags
        )
        or tags != sorted(tags, key=_canonical_bytes)
        or len({_canonical_bytes(tag) for tag in tags}) != len(tags)
    ):
        raise ExportOutcomeError("invalid reconciled tags")
    if (
        not _valid_length(report["terminalOutcomeCount"])
        or report["terminalOutcomeCount"] == 0
        or report["observedArchiveCount"] > report["terminalOutcomeCount"]
        or not _valid_length(report["verifiedOutputCount"])
        or report["verifiedOutputCount"] < len(OUTPUT_KINDS - {"none"})
        or report["verifiedOutputCount"] > report["terminalOutcomeCount"]
    ):
        raise ExportOutcomeError("invalid reconciliation outcome counts")
    status_counts = report["terminalStatusCounts"]
    if (
        not isinstance(status_counts, dict)
        or not status_counts
        or any(
            status not in EXPORT_STATUSES or not _valid_length(count) or count == 0
            for status, count in status_counts.items()
        )
    ):
        raise ExportOutcomeError("invalid terminal status counts")
    if sum(status_counts.values()) != report["terminalOutcomeCount"]:
        raise ExportOutcomeError("terminal status counts disagree with outcome count")
    if report["verifiedOutputCount"] > status_counts.get("exported", 0):
        raise ExportOutcomeError("verified outputs exceed exported outcomes")
    return _canonical_bytes(report) + b"\n"


def default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def pick_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(output: SecuredOutputRoot, path: Path, payload: object) -> None:
    output.atomic_write_json(path, payload)


def render_cmd(cmd: list[str]) -> str:
    return subprocess.list2cmdline([str(part) for part in cmd])


def require_existing(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(f"{description} does not exist: {path}")


def resolve_executable(command: str, *, label: str) -> Path:
    candidate = Path(command)
    if candidate.is_absolute() or candidate.parent != Path("."):
        resolved = candidate.resolve(strict=True)
    else:
        located = shutil.which(command)
        if located is None:
            raise SystemExit(f"{label} executable was not found on PATH: {command}")
        resolved = Path(located).resolve(strict=True)
    if not resolved.is_file():
        raise SystemExit(f"{label} executable is not a file: {resolved}")
    return resolved


def require_trusted_executables(args: argparse.Namespace) -> None:
    requested_python = resolve_executable(args.python_exe, label="Python")
    running_python = Path(sys.executable).resolve(strict=True)
    if not os.path.samefile(requested_python, running_python):
        raise SystemExit(
            "--python-exe must resolve to the interpreter running export_game_assets.py"
        )

    requested_dotnet = resolve_executable(args.dotnet_exe, label="dotnet")
    trusted_dotnet_path = shutil.which("dotnet")
    if trusted_dotnet_path is None:
        raise SystemExit("dotnet was not found on PATH")
    trusted_dotnet = Path(trusted_dotnet_path).resolve(strict=True)
    if not os.path.samefile(requested_dotnet, trusted_dotnet):
        raise SystemExit("--dotnet-exe must resolve to the dotnet executable on PATH")

    args.python_exe = str(running_python)
    args.dotnet_exe = str(trusted_dotnet)


def run_step(cmd: list[str], *, cwd: Path, log_path: Path, output: SecuredOutputRoot) -> None:
    output.refresh_tree()
    print(f"$ {render_cmd(cmd)}")
    with output.atomic_text_writer(log_path) as log:
        process = subprocess.run(
            [str(part) for part in cmd],
            cwd=str(cwd),
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    output.refresh_tree()
    if process.returncode != 0:
        tail = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
        print("\n".join(tail), file=sys.stderr)
        raise SystemExit(f"step failed with exit code {process.returncode}: {log_path}")
    print(f"[OK] {log_path}")


def build_harness_cmd(args: argparse.Namespace, repo_root: Path, resources_root: Path, embedded_root: Path, asset_export_root: Path, command: str) -> list[str]:
    cmd = [
        args.dotnet_exe,
        "run",
        "--project",
        str(repo_root / "tools" / "BeaAssetExportHarness" / "BeaAssetExportHarness.csproj"),
        "--",
        command,
        "--repo-root",
        str(repo_root),
        "--resources-root",
        str(resources_root),
        "--extractor-runtime-dir",
        str(args.extractor_runtime_dir),
        "--extractor-root",
        str(args.extractor_root),
        "--embedded-root",
        str(embedded_root),
        "--out-dir",
        str(asset_export_root),
        "--progress-every",
        str(args.progress_every),
    ]
    if command == "export-textures" and args.limit_loose_textures is not None:
        cmd.extend(["--limit-loose-textures", str(args.limit_loose_textures)])
    if command == "export-loose-meshes" and args.limit_loose_meshes is not None:
        cmd.extend(["--limit-loose-meshes", str(args.limit_loose_meshes)])
    if command == "export-embedded-meshes" and args.limit_embedded_bodies is not None:
        cmd.extend(["--limit-embedded-bodies", str(args.limit_embedded_bodies)])
    if args.skip_existing:
        cmd.append("--skip-existing")
    return cmd


def lane_result_from_manifest(asset_export_root: Path, lane: str) -> dict[str, object]:
    manifest_path = asset_export_root / lane / "manifest.json"
    rows = read_json(manifest_path)
    if not isinstance(rows, list):
        raise SystemExit(f"unexpected manifest shape: {manifest_path}")
    succeeded = sum(1 for row in rows if isinstance(row, dict) and row.get("status") in ("ok", "skipped_existing"))
    failed = sum(1 for row in rows if isinstance(row, dict) and row.get("status") == "error")
    return {
        "Lane": lane,
        "Attempted": len(rows),
        "Succeeded": succeeded,
        "Failed": failed,
        "ManifestPath": str(manifest_path),
    }


def write_asset_export_summary(output: SecuredOutputRoot, asset_export_root: Path) -> dict[str, object]:
    summary = {
        "command": "export-all",
        "out_dir": str(asset_export_root),
        "process_model": "separate_process_per_lane",
        "results": [
            lane_result_from_manifest(asset_export_root, "loose_textures"),
            lane_result_from_manifest(asset_export_root, "loose_meshes"),
            lane_result_from_manifest(asset_export_root, "embedded_meshes"),
        ],
    }
    write_json(output, asset_export_root / "summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    repo_root = default_repo_root()
    game_root = repo_root / "game"
    default_out = repo_root / ".artifacts" / "asset-export" / date.today().isoformat()

    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=repo_root)
    ap.add_argument("--game-root", type=Path, default=game_root)
    ap.add_argument("--out-root", type=Path, default=default_out)
    ap.add_argument("--python-exe", default=sys.executable)
    ap.add_argument("--dotnet-exe", default="dotnet")
    ap.add_argument(
        "--extractor-runtime-dir",
        type=Path,
        default=repo_root / "references" / "AYAResourceExtractor" / "Code" / "AyaResourceExtractor" / "bin" / "Debug" / "net6.0-windows",
    )
    ap.add_argument(
        "--extractor-root",
        type=Path,
        default=repo_root / "references" / "AYAResourceExtractor",
    )
    ap.add_argument("--archive-glob", default="*_res_PC.aya")
    ap.add_argument("--limit-archives", type=int, default=0)
    ap.add_argument("--limit-loose-textures", type=int)
    ap.add_argument("--limit-loose-meshes", type=int)
    ap.add_argument("--limit-embedded-bodies", type=int)
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--progress-every", type=int, default=25)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    require_trusted_executables(args)
    repo_root = args.repo_root.resolve()
    game_root = args.game_root.resolve()
    out_root = args.out_root.resolve()

    data_root = game_root / "data"
    resources_root = pick_existing(data_root / "resources")
    language_dir = pick_existing(data_root / "LANGUAGE", data_root / "language")
    video_root = pick_existing(data_root / "video")
    stf_path = pick_existing(data_root / "MissionScripts" / "text" / "text.stf")

    require_existing(repo_root / "tools" / "aya_archive_inventory.py", "aya archive inventory tool")
    require_existing(repo_root / "tools" / "export_language_corpus.py", "language export tool")
    require_existing(repo_root / "tools" / "export_video_manifest.py", "video manifest tool")
    require_existing(repo_root / "tools" / "export_asset_catalog.py", "asset catalog tool")
    require_existing(repo_root / "tools" / "BeaAssetExportHarness" / "BeaAssetExportHarness.csproj", "asset export harness project")
    require_existing(game_root, "game root")
    require_existing(resources_root, "resources root")
    require_existing(language_dir, "language dir")
    require_existing(video_root, "video root")
    require_existing(stf_path, "text.stf")
    require_existing(args.extractor_root, "AYAResourceExtractor root")
    require_existing(args.extractor_runtime_dir / "AYAResourceExtractor.dll", "AYAResourceExtractor runtime dll")
    require_existing(args.extractor_runtime_dir / "DDSTextureUncompress.dll", "DDSTextureUncompress runtime dll")

    output = SecuredOutputRoot(
        out_root,
        protected_sources=(
            game_root,
            resources_root,
            language_dir,
            video_root,
            stf_path,
            args.extractor_root.resolve(strict=True),
            args.extractor_runtime_dir.resolve(strict=True),
        ),
    )
    atexit.register(output.close)

    logs_dir = out_root / "logs"
    embedded_root = out_root / "aya_embedded_meshes"
    asset_manifest_path = out_root / "aya_asset_manifest.json"
    asset_export_root = out_root / "asset_export"
    language_out = out_root / "language_export"
    video_out = out_root / "video_manifest"
    catalog_out = out_root / "asset_catalog"

    for directory in (
        logs_dir,
        embedded_root,
        asset_export_root,
        asset_export_root / "loose_textures",
        asset_export_root / "loose_meshes",
        asset_export_root / "embedded_meshes",
        language_out,
        video_out,
        catalog_out,
    ):
        output.ensure_directory(directory)
    output.refresh_tree()

    inventory_cmd = [
        args.python_exe,
        str(repo_root / "tools" / "aya_archive_inventory.py"),
        str(resources_root),
        "--glob",
        args.archive_glob,
        "--resolve-assets",
        "--resource-root",
        str(resources_root),
        "--dump-dir",
        str(embedded_root),
        "--dump-tag",
        "MESH",
        "--extract-embedded-mesh-bodies",
        "--asset-manifest-out",
        str(asset_manifest_path),
    ]
    if args.limit_archives > 0:
        inventory_cmd.extend(["--limit", str(args.limit_archives)])

    harness_steps = [
        ("02a_asset_export_textures.log", build_harness_cmd(args, repo_root, resources_root, embedded_root, asset_export_root, "export-textures")),
        ("02b_asset_export_loose_meshes.log", build_harness_cmd(args, repo_root, resources_root, embedded_root, asset_export_root, "export-loose-meshes")),
        ("02c_asset_export_embedded_meshes.log", build_harness_cmd(args, repo_root, resources_root, embedded_root, asset_export_root, "export-embedded-meshes")),
    ]

    language_cmd = [
        args.python_exe,
        str(repo_root / "tools" / "export_language_corpus.py"),
        "--language-dir",
        str(language_dir),
        "--stf",
        str(stf_path),
        "--out-dir",
        str(language_out),
    ]

    video_cmd = [
        args.python_exe,
        str(repo_root / "tools" / "export_video_manifest.py"),
        "--video-root",
        str(video_root),
        "--out-dir",
        str(video_out),
    ]

    catalog_cmd = [
        args.python_exe,
        str(repo_root / "tools" / "export_asset_catalog.py"),
        "--repo-root",
        str(repo_root),
        "--bundle-root",
        str(out_root),
        "--packed-manifest",
        str(asset_manifest_path),
        "--texture-manifest",
        str(asset_export_root / "loose_textures" / "manifest.json"),
        "--loose-mesh-manifest",
        str(asset_export_root / "loose_meshes" / "manifest.json"),
        "--embedded-mesh-manifest",
        str(asset_export_root / "embedded_meshes" / "manifest.json"),
        "--video-manifest",
        str(video_out / "manifest.json"),
        "--language-matrix",
        str(language_out / "merged_matrix.json"),
        "--out-dir",
        str(catalog_out),
    ]

    run_step(inventory_cmd, cwd=repo_root, log_path=logs_dir / "01_aya_inventory.log", output=output)
    for log_name, harness_cmd in harness_steps:
        run_step(harness_cmd, cwd=repo_root, log_path=logs_dir / log_name, output=output)
    run_step(language_cmd, cwd=repo_root, log_path=logs_dir / "03_language_export.log", output=output)
    run_step(video_cmd, cwd=repo_root, log_path=logs_dir / "04_video_manifest.log", output=output)
    run_step(catalog_cmd, cwd=repo_root, log_path=logs_dir / "05_asset_catalog.log", output=output)

    asset_manifest = read_json(asset_manifest_path)
    asset_export_summary = write_asset_export_summary(output, asset_export_root)
    language_summary = read_json(language_out / "summary.json")
    video_summary = read_json(video_out / "summary.json")
    catalog_summary = read_json(catalog_out / "summary.json")

    summary = {
        "status": "ok",
        "repo_root": str(repo_root),
        "game_root": str(game_root),
        "out_root": str(out_root),
        "notes": [
            "Backend-only extraction workflow intended for WinUI/tooling integration or public BYO-assets packaging.",
            "This pipeline does not ship any copyrighted assets; it operates against a local game install.",
        ],
        "paths": {
            "asset_manifest": str(asset_manifest_path),
            "embedded_root": str(embedded_root),
            "asset_export_root": str(asset_export_root),
            "language_out": str(language_out),
            "video_out": str(video_out),
            "catalog_out": str(catalog_out),
            "logs_dir": str(logs_dir),
        },
        "summaries": {
            "aya_asset_manifest": asset_manifest["summary"],
            "asset_export": asset_export_summary,
            "language_export": language_summary,
            "video_manifest": video_summary,
            "asset_catalog": catalog_summary,
        },
    }
    summary_path = out_root / "extraction_summary.json"
    write_json(output, summary_path, summary)
    print(json.dumps(summary, indent=2))
    print(f"[OK] wrote backend summary: {summary_path}")
    output.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
