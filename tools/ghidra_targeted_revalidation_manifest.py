#!/usr/bin/env python3
"""Build the public-safe correction manifest for targeted Ghidra revalidation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


RESEARCH_SCHEMA = "onslaught-ghidra-full-reaudit-research-review.v1"
CRITICAL_SCHEMA = "onslaught-ghidra-critical-review.v1"
CONFLICT_SCHEMA = "onslaught-ghidra-full-reaudit-conflict-review.v1"
OUTPUT_SCHEMA = "onslaught-ghidra-targeted-revalidation-corrections.v2"
ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{8}$")
ABSOLUTE_PATH_PATTERN = re.compile(r"(?i)(?:[a-z]:[\\/]|/(?:home|mnt|tmp|users?)/)")
CONFLICT_DOC_PATH_PATTERN = re.compile(
    r"(?:reverse-engineering|release/readiness)/[A-Za-z0-9_./-]+\.md"
)
PROPOSED_FIELDS = (
    ("proposedName", "name", "correctedName"),
    ("proposedSignature", "signature", "correctedSignature"),
    ("proposedComment", "comment", "correctedComment"),
)


@dataclass(frozen=True)
class Ledger:
    path: Path
    bytes: int
    sha256: str
    rows: tuple[dict, ...]


@dataclass(frozen=True)
class MetadataSnapshot:
    path: Path
    bytes: int
    sha256: str
    rows: dict[str, dict[str, str]]


@dataclass(frozen=True)
class CoveredManifest:
    path: Path
    bytes: int
    sha256: str
    records: dict[str, dict]

    @property
    def addresses(self) -> frozenset[str]:
        return frozenset(self.records)


def load_ledgers(paths: Iterable[Path]) -> list[Ledger]:
    ledgers: list[Ledger] = []
    for path in paths:
        raw = path.read_bytes()
        rows: list[dict] = []
        for line_number, raw_line in enumerate(raw.decode("utf-8").splitlines(), start=1):
            if not raw_line.strip():
                continue
            try:
                row = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL {path.name}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"non-object JSONL row {path.name}:{line_number}")
            rows.append(row)
        ledgers.append(
            Ledger(
                path=path,
                bytes=len(raw),
                sha256=hashlib.sha256(raw).hexdigest(),
                rows=tuple(rows),
            )
        )
    return ledgers


def load_metadata(path: Path) -> MetadataSnapshot:
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter="\t")
    required = {"address", "name", "signature", "prototype_key"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValueError(f"metadata TSV missing required columns: {path.name}")
    rows: dict[str, dict[str, str]] = {}
    for row in reader:
        address = str(row.get("address", "")).lower()
        if not ADDRESS_PATTERN.fullmatch(address):
            raise ValueError(f"metadata TSV has invalid address: {address}")
        if address in rows:
            raise ValueError(f"metadata TSV duplicate address: {address}")
        if not row.get("name") or not row.get("signature"):
            raise ValueError(f"metadata TSV missing name/signature: {address}")
        rows[address] = {key: str(value or "") for key, value in row.items()}
    return MetadataSnapshot(
        path=path,
        bytes=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(),
        rows=rows,
    )


def load_covered_manifest(path: Path) -> CoveredManifest:
    raw = path.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise ValueError(f"covered manifest has no records array: {path.name}")
    by_address: dict[str, dict] = {}
    for record in records:
        address = str(record.get("address", "")).lower() if isinstance(record, dict) else ""
        if not ADDRESS_PATTERN.fullmatch(address):
            raise ValueError(f"covered manifest has invalid address: {address}")
        if address in by_address:
            raise ValueError(f"covered manifest duplicate address: {address}")
        by_address[address] = dict(record)
    return CoveredManifest(
        path=path,
        bytes=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(),
        records=by_address,
    )


def _validate_doc_path(value: object, address: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{address}: empty doc finding")
    normalized = value.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if (
        normalized.startswith("/")
        or re.match(r"^[A-Za-z]:/", normalized)
        or ".." in pure.parts
    ):
        raise ValueError(f"{address}: doc finding must be repo-relative: {value}")
    return normalized


def _public_artifact(path: Path, size: int, sha256: str) -> dict[str, object]:
    return {"file": path.name, "bytes": size, "sha256": sha256}


def _validate_public_row(row: dict, address: str) -> None:
    if ABSOLUTE_PATH_PATTERN.search(json.dumps(row, ensure_ascii=True)):
        raise ValueError(f"{address}: review row contains an absolute path")
    evidence = row.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(
        isinstance(value, str) and value.strip() for value in evidence
    ):
        raise ValueError(f"{address}: evidence must be a non-empty string array")
    rationale = row.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError(f"{address}: rationale must be a non-empty string")
    source_alignment = row.get("sourceAlignment")
    if source_alignment is not None and (
        not isinstance(source_alignment, str) or not source_alignment.strip()
    ):
        raise ValueError(f"{address}: sourceAlignment must be null or a non-empty string")


def _conflict_doc_paths(values: object, address: str) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError(f"{address}: docFindings must be a string array")
    result: list[str] = []
    for value in values:
        matches = CONFLICT_DOC_PATH_PATTERN.findall(value.replace("\\", "/"))
        if not matches and value.strip():
            raise ValueError(f"{address}: conflict doc finding contains no repo path: {value}")
        result.extend(_validate_doc_path(match, address) for match in matches)
    return list(dict.fromkeys(result))


def _signature_shape(signature: str) -> tuple[str, tuple[str, ...]]:
    match = re.fullmatch(r"\s*(.*?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*", signature)
    if not match:
        raise ValueError(f"cannot classify signature shape: {signature}")
    prefix = " ".join(match.group(1).split())
    raw_parameters = match.group(3).strip()
    if not raw_parameters or raw_parameters == "void":
        return prefix, ()
    parameters: list[str] = []
    for parameter in raw_parameters.split(","):
        normalized = " ".join(parameter.strip().split())
        normalized = re.sub(r"\s+[A-Za-z_][A-Za-z0-9_]*$", "", normalized)
        normalized = re.sub(r"\s*\*\s*", " *", normalized).strip()
        parameters.append(normalized)
    return prefix, tuple(parameters)


def _correction_matches_covered(correction: dict, covered_record: dict) -> bool:
    pairs = (
        ("proposedName", "correctedName"),
        ("proposedSignature", "correctedSignature"),
        ("proposedComment", "correctedComment"),
    )
    proposed = [(source, target) for source, target in pairs if correction.get(source)]
    return bool(proposed) and all(
        correction[source] == covered_record.get(target) for source, target in proposed
    )


def _correction_record(
    row: dict, phase: str, metadata_row: dict[str, str] | None
) -> dict:
    address = str(row["address"]).lower()
    correction = row.get("correction")
    if not isinstance(correction, dict):
        raise ValueError(f"{address}: correction-required row has no correction object")
    proposed = [key for key, _, _ in PROPOSED_FIELDS if correction.get(key)]
    if not proposed:
        raise ValueError(f"{address}: correction has no proposed field")
    saved_name = row.get("savedName") or (metadata_row or {}).get("name")
    if not isinstance(saved_name, str) or not saved_name:
        raise ValueError(f"{address}: missing savedName")
    fields: list[str] = []
    record: dict[str, object] = {
        "address": address,
        "phase": phase,
        "confidence": row.get("confidence"),
        "currentName": saved_name,
        "correctedName": correction.get("proposedName") or saved_name,
    }
    if metadata_row:
        record["currentSignature"] = metadata_row["signature"]
        record["currentPrototypeKey"] = metadata_row["prototype_key"]
    for proposed_key, field_name, output_key in PROPOSED_FIELDS:
        value = correction.get(proposed_key)
        if value:
            fields.append(field_name)
            record[output_key] = value
    record["correctedFields"] = fields
    if phase == "recovered-conflicts":
        record["docFindings"] = _conflict_doc_paths(row.get("docFindings"), address)
    else:
        record["docFindings"] = [
            _validate_doc_path(value, address) for value in row.get("docFindings") or ()
        ]
    record["evidence"] = list(row.get("evidence") or ())
    record["rationale"] = row.get("rationale")
    if correction.get("proposedSignature"):
        if not metadata_row:
            raise ValueError(f"{address}: signature correction requires final metadata")
        record["signatureChangeClass"] = (
            "name-and-parameter-rendering-only"
            if _signature_shape(metadata_row["signature"])
            == _signature_shape(str(correction["proposedSignature"]))
            else "structured-prototype-change"
        )
    if phase == "research-findings":
        record["recoveryEvidence"] = row.get("recoveryEvidence")
    elif phase == "recovered-conflicts":
        record["conflictClass"] = row.get("conflictClass")
        record["recoveredVerdicts"] = list(row.get("recoveredVerdicts") or ())
        record["recoveryVariantCount"] = row.get("variantCount")
    else:
        record["sourceAlignment"] = row.get("sourceAlignment")
    return record


def build_manifest(
    ledgers: Iterable[Ledger],
    source_campaign: str,
    *,
    metadata: MetadataSnapshot | None = None,
    covered: CoveredManifest | None = None,
) -> dict:
    records: list[dict] = []
    seen: dict[str, str] = {}
    sources: list[dict] = []
    reviewed = 0
    covered_corrections: list[str] = []
    superseding_overlaps: list[str] = []
    for ledger in ledgers:
        sources.append(
            {
                "file": ledger.path.name,
                "bytes": ledger.bytes,
                "sha256": ledger.sha256,
            }
        )
        for row in ledger.rows:
            schema = row.get("schemaVersion")
            if schema == RESEARCH_SCHEMA:
                phase = "research-findings"
            elif schema == CRITICAL_SCHEMA:
                phase = "runtime-critical"
            elif schema == CONFLICT_SCHEMA:
                phase = "recovered-conflicts"
            else:
                raise ValueError(f"unsupported review schema: {schema}")
            address = str(row.get("address", "")).lower()
            if not ADDRESS_PATTERN.fullmatch(address):
                raise ValueError(f"invalid address: {address}")
            disposition = row.get("disposition")
            if disposition not in {"accepted", "correction-required", "unresolved"}:
                raise ValueError(f"{address}: invalid disposition {disposition}")
            _validate_public_row(row, address)
            if address in seen:
                if seen[address] != "accepted" or disposition != "accepted":
                    raise ValueError(f"duplicate address across ledgers: {address}")
                continue
            seen[address] = disposition
            reviewed += 1
            if disposition == "correction-required":
                if covered and address in covered.addresses:
                    correction = row.get("correction")
                    if isinstance(correction, dict) and _correction_matches_covered(
                        correction, covered.records[address]
                    ):
                        covered_corrections.append(address)
                        continue
                    superseding_overlaps.append(address)
                metadata_row = metadata.rows.get(address) if metadata else None
                record = _correction_record(row, phase, metadata_row)
                if address in superseding_overlaps:
                    record["supersedesCursorDeltaRecord"] = True
                records.append(record)
    records.sort(key=lambda item: item["address"])
    sources.sort(key=lambda item: item["file"])
    payload: dict[str, object] = {
        "prototypeOrBoundaryMutationAuthorized": False,
        "recordCount": len(records),
        "records": records,
        "reviewedAddressCount": reviewed,
        "schemaVersion": OUTPUT_SCHEMA,
        "sourceCampaign": source_campaign,
        "sourceLedgers": sources,
        "coveredByCursorDeltaCount": len(covered_corrections),
        "coveredByCursorDeltaAddresses": sorted(covered_corrections),
        "supersedingCursorDeltaOverlapCount": len(superseding_overlaps),
        "supersedingCursorDeltaOverlapAddresses": sorted(superseding_overlaps),
    }
    if metadata:
        payload["sourceMetadata"] = _public_artifact(
            metadata.path, metadata.bytes, metadata.sha256
        )
    if covered:
        payload["coveredByCursorDeltaSource"] = _public_artifact(
            covered.path, covered.bytes, covered.sha256
        )
    return payload


def write_manifest(path: Path, payload: dict, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"refusing to overwrite existing output: {path}")
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, action="append", required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--covered-manifest", type=Path)
    parser.add_argument("--source-campaign", default="ghidra-full-reaudit-20260712")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        payload = build_manifest(
            load_ledgers(args.ledger),
            args.source_campaign,
            metadata=load_metadata(args.metadata),
            covered=(
                load_covered_manifest(args.covered_manifest)
                if args.covered_manifest
                else None
            ),
        )
        write_manifest(args.output, payload, force=args.force)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"Targeted revalidation manifest: FAIL: {exc}")
        return 1
    print(
        "Targeted revalidation manifest: PASS "
        f"Reviewed={payload['reviewedAddressCount']} Corrections={payload['recordCount']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
