#!/usr/bin/env python3
"""Build and verify a fail-closed Ghidra reviewed-correction apply plan."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


CLASSIFICATIONS = (
    "confirmed-apply",
    "already-correct/no-op",
    "disputed-needs-research",
    "rejected-manifest-error",
)
ALLOWED_FIELDS = {"name", "signature", "comment"}
LEASED_STRUCTURED_PROTOTYPE_ADDRESS = "0x0050b9c0"
REJECTED_MANIFEST_ADDRESS = "0x004dac90"
CURSOR_MANIFEST_SCHEMA = "onslaught-ghidra-full-reaudit-corrections.v1"
TARGETED_MANIFEST_SCHEMA = "onslaught-ghidra-targeted-revalidation-corrections.v2"
REVIEWED_PLAN_SCHEMA = "onslaught-ghidra-reviewed-correction-plan.v1"
EXPECTED_REVIEWED_PLAN_SHA256 = "312ee274791c4d9a0167305846f482a12cd8f153adc44ee7f7f27279cc48c8ce"
EXPECTED_REVIEWED_ADDRESS_COUNT = 92
EXPECTED_APPLY_RECORD_COUNT = 91
EXPECTED_POST_SNAPSHOT_COUNT = 6411
APPLY_PLAN_FIELDS = (
    "address",
    "classification",
    "fields",
    "expected_name",
    "expected_signature",
    "expected_comment",
    "expected_prototype_key",
    "corrected_name",
    "corrected_signature",
    "corrected_comment",
    "signature_change_class",
    "expected_corrected_prototype_key",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_address(value: str) -> str:
    text = str(value).strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or any(ch not in "0123456789abcdef" for ch in text) or len(text) > 8:
        raise ValueError(f"invalid address: {value!r}")
    return "0x" + text.zfill(8)


def unescape(value: str | None) -> str:
    if value is None:
        return ""
    result: list[str] = []
    index = 0
    escapes = {"\\": "\\", "t": "\t", "r": "\r", "n": "\n"}
    while index < len(value):
        current = value[index]
        if current != "\\":
            result.append(current)
            index += 1
            continue
        index += 1
        if index >= len(value):
            raise ValueError("trailing backslash in plan field")
        escaped = value[index]
        if escaped not in escapes:
            raise ValueError(f"unknown plan escape: \\{escaped}")
        result.append(escapes[escaped])
        index += 1
    return "".join(result)


def escape(value: str | None) -> str:
    if value is None:
        return ""
    return (
        value.replace("\\", "\\\\")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def load_manifest(path: Path, expected_schema: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != expected_schema:
        raise ValueError(
            f"unexpected manifest schema at {path}: {data.get('schemaVersion')!r}; "
            f"expected {expected_schema!r}"
        )
    if data.get("prototypeOrBoundaryMutationAuthorized") is not False:
        raise ValueError(
            f"source manifest must not authorize prototype or boundary mutation: {path}"
        )
    records = data.get("records")
    if not isinstance(records, list) or data.get("recordCount") != len(records):
        raise ValueError(f"manifest recordCount mismatch: {path}")
    return data


def resolved_records(cursor_path: Path, targeted_path: Path) -> dict[str, dict]:
    cursor = load_manifest(cursor_path, CURSOR_MANIFEST_SCHEMA)
    targeted = load_manifest(targeted_path, TARGETED_MANIFEST_SCHEMA)
    result: dict[str, dict] = {}
    for index, record in enumerate(cursor["records"]):
        address = normalize_address(record.get("address", ""))
        if address in result:
            raise ValueError(f"duplicate correction address in cursor manifest: {address}")
        result[address] = {
            "sourceManifest": "cursor",
            "sourceRecordIndex": index,
            "record": record,
        }

    declared = {
        normalize_address(address)
        for address in targeted.get("supersedingCursorDeltaOverlapAddresses", [])
    }
    flagged: set[str] = set()
    for index, record in enumerate(targeted["records"]):
        address = normalize_address(record.get("address", ""))
        if address in result:
            if record.get("supersedesCursorDeltaRecord") is not True or address not in declared:
                raise ValueError(f"duplicate correction address without explicit superseder: {address}")
            flagged.add(address)
        result[address] = {
            "sourceManifest": "targeted",
            "sourceRecordIndex": index,
            "record": record,
        }
    if flagged != declared:
        raise ValueError(
            "targeted superseding address declaration mismatch: "
            f"declared={sorted(declared)} flagged={sorted(flagged)}"
        )
    if targeted.get("supersedingCursorDeltaOverlapCount", len(declared)) != len(declared):
        raise ValueError("targeted superseding overlap count mismatch")
    return result


def load_decisions(path: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        address = normalize_address(row.get("address", ""))
        if address in result:
            raise ValueError(f"duplicate decision address at line {line_number}: {address}")
        classification = row.get("classification")
        if classification not in CLASSIFICATIONS:
            raise ValueError(f"invalid classification at {address}: {classification!r}")
        if not str(row.get("rationale", "")).strip():
            raise ValueError(f"missing decision rationale at {address}")
        evidence = row.get("freshEvidence")
        if not isinstance(evidence, list) or not evidence or not all(str(item).strip() for item in evidence):
            raise ValueError(f"missing freshEvidence at {address}")
        result[address] = row
    return result


def load_snapshot(path: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"address", "name", "signature", "comment", "status", "prototype_key"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"snapshot missing required columns: {path}")
        for row in reader:
            address = normalize_address(row["address"])
            if address in result:
                raise ValueError(f"duplicate snapshot address: {address}")
            if row["status"] != "OK":
                raise ValueError(f"snapshot status is not OK at {address}: {row['status']}")
            result[address] = {
                "name": unescape(row["name"]),
                "signature": unescape(row["signature"]),
                "comment": unescape(row["comment"]),
                "prototypeKey": unescape(row["prototype_key"]),
            }
    return result


def derived_corrected_signature(record: dict, live: dict[str, str], fields: list[str]) -> str:
    if "signature" in fields:
        corrected = record.get("correctedSignature")
        if not isinstance(corrected, str) or not corrected:
            raise ValueError(f"signature correction missing correctedSignature at {record.get('address')}")
        return corrected
    if "name" in fields:
        current_name = record.get("currentName")
        corrected_name = record.get("correctedName")
        if not isinstance(current_name, str) or not isinstance(corrected_name, str):
            raise ValueError(f"name correction missing names at {record.get('address')}")
        if current_name not in live["signature"]:
            raise ValueError(f"current name not rendered in signature at {record.get('address')}")
        return live["signature"].replace(current_name, corrected_name, 1)
    return live["signature"]


def validate_live_preconditions(address: str, record: dict, live: dict[str, str]) -> None:
    checks: list[tuple[str, str, str]] = []
    if "currentName" in record:
        checks.append(("name", str(record["currentName"]), live["name"]))
    if "currentSignature" in record:
        checks.append(("signature", str(record["currentSignature"]), live["signature"]))
    if "currentPrototypeKey" in record:
        checks.append(("prototype_key", str(record["currentPrototypeKey"]), live["prototypeKey"]))
    if "currentComment" in record:
        checks.append(("comment", str(record["currentComment"]), live["comment"]))
    for field, expected, actual in checks:
        if expected != actual:
            raise ValueError(
                f"live precondition mismatch at {address} field {field}: "
                f"expected {expected!r}, actual {actual!r}"
            )


def build_record(address: str, source: dict, decision: dict, live: dict[str, str]) -> dict:
    record = source["record"]
    fields = record.get("correctedFields")
    if not isinstance(fields, list) or not fields or len(fields) != len(set(fields)):
        raise ValueError(f"invalid correctedFields at {address}")
    if not set(fields).issubset(ALLOWED_FIELDS):
        raise ValueError(f"unknown correctedFields at {address}: {fields}")
    validate_live_preconditions(address, record, live)

    corrected_name = record.get("correctedName", live["name"])
    corrected_signature = derived_corrected_signature(record, live, fields)
    corrected_comment = record.get("correctedComment", live["comment"])
    signature_class = record.get("signatureChangeClass")
    corrected_prototype_key = live["prototypeKey"]
    if "signature" in fields:
        if signature_class not in {
            "name-and-parameter-rendering-only",
            "structured-prototype-change",
        }:
            raise ValueError(f"invalid signatureChangeClass at {address}: {signature_class!r}")
        if signature_class == "structured-prototype-change":
            if address != LEASED_STRUCTURED_PROTOTYPE_ADDRESS:
                raise ValueError(
                    f"structured signature address is not leased: {address}; "
                    f"expected {LEASED_STRUCTURED_PROTOTYPE_ADDRESS}"
                )
            corrected_prototype_key = decision.get("expectedCorrectedPrototypeKey")
            if decision["classification"] == "confirmed-apply" and not corrected_prototype_key:
                raise ValueError(
                    f"confirmed structured signature at {address} requires expectedCorrectedPrototypeKey"
                )
            if (
                decision["classification"] == "confirmed-apply"
                and corrected_prototype_key == live["prototypeKey"]
            ):
                raise ValueError(
                    f"confirmed structured signature at {address} must change prototype key"
                )
            corrected_prototype_key = corrected_prototype_key or live["prototypeKey"]

    return {
        "address": address,
        "sourceManifest": source["sourceManifest"],
        "sourceRecordIndex": source["sourceRecordIndex"],
        "classification": decision["classification"],
        "reviewRationale": str(decision["rationale"]),
        "freshEvidence": list(decision["freshEvidence"]),
        "correctedFields": fields,
        "signatureChangeClass": signature_class,
        "currentName": live["name"],
        "currentSignature": live["signature"],
        "currentComment": live["comment"],
        "currentPrototypeKey": live["prototypeKey"],
        "correctedName": corrected_name,
        "correctedSignature": corrected_signature,
        "correctedComment": corrected_comment,
        "expectedCorrectedPrototypeKey": corrected_prototype_key,
    }


def write_apply_plan(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\t".join(APPLY_PLAN_FIELDS) + "\n")
        for record in records:
            values = [
                record["address"],
                record["classification"],
                ",".join(record["correctedFields"]),
                record["currentName"],
                record["currentSignature"],
                record["currentComment"],
                record["currentPrototypeKey"],
                record["correctedName"],
                record["correctedSignature"],
                record["correctedComment"],
                record["signatureChangeClass"] or "",
                record["expectedCorrectedPrototypeKey"],
            ]
            handle.write("\t".join(escape(str(value)) for value in values) + "\n")


def validate_apply_plan(
    path: Path,
    *,
    expected_sha256: str,
    expected_count: int,
) -> list[dict[str, str]]:
    if re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise ValueError("expected apply-plan SHA-256 must be 64 lowercase hex characters")
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"apply-plan SHA-256 mismatch: expected={expected_sha256} actual={actual_sha256}"
        )
    if expected_count <= 0:
        raise ValueError("expected apply-plan count must be positive")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "\t".join(APPLY_PLAN_FIELDS):
        raise ValueError("apply-plan header mismatch")
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(lines[1:], start=2):
        if not line:
            raise ValueError(f"blank apply-plan row at line {line_number}")
        raw = line.split("\t")
        if len(raw) != len(APPLY_PLAN_FIELDS):
            raise ValueError(
                f"apply-plan column count mismatch at line {line_number}: {len(raw)}"
            )
        values = [unescape(value) for value in raw]
        row = dict(zip(APPLY_PLAN_FIELDS, values, strict=True))
        address = normalize_address(row["address"])
        if row["address"] != address:
            raise ValueError(f"apply-plan address is not canonical: {row['address']!r}")
        if address == REJECTED_MANIFEST_ADDRESS:
            raise ValueError(f"rejected manifest address is forbidden in apply plan: {address}")
        if address in seen:
            raise ValueError(f"duplicate apply-plan address: {address}")
        seen.add(address)
        if row["classification"] != "confirmed-apply":
            raise ValueError(f"non-confirmed apply-plan row at {address}")
        fields = row["fields"].split(",")
        if (
            not fields
            or len(fields) != len(set(fields))
            or not set(fields).issubset(ALLOWED_FIELDS)
        ):
            raise ValueError(f"invalid apply-plan fields at {address}: {row['fields']!r}")
        signature_class = row["signature_change_class"]
        if "signature" in fields:
            if signature_class == "structured-prototype-change":
                if address != LEASED_STRUCTURED_PROTOTYPE_ADDRESS:
                    raise ValueError(f"structured apply-plan address is not leased: {address}")
            elif signature_class == "name-and-parameter-rendering-only":
                if row["expected_prototype_key"] != row["expected_corrected_prototype_key"]:
                    raise ValueError(f"rendering-only apply-plan row changes prototype key: {address}")
            else:
                raise ValueError(f"invalid apply-plan signature class at {address}: {signature_class!r}")
        elif signature_class:
            raise ValueError(f"apply-plan signature class without signature field at {address}")
        rows.append(row)
    if len(rows) != expected_count:
        raise ValueError(
            f"apply-plan row count mismatch: expected={expected_count} actual={len(rows)}"
        )
    return rows


def build_plan(
    cursor_manifest: Path,
    targeted_manifest: Path,
    decisions_path: Path,
    live_snapshot_path: Path,
    output_manifest_path: Path,
    output_apply_plan_path: Path,
) -> dict:
    resolved = resolved_records(cursor_manifest, targeted_manifest)
    decisions = load_decisions(decisions_path)
    if set(decisions) != set(resolved):
        raise ValueError(
            "decision addresses must exactly match correction addresses: "
            f"missing={sorted(set(resolved) - set(decisions))} "
            f"extra={sorted(set(decisions) - set(resolved))}"
        )
    live_snapshot = load_snapshot(live_snapshot_path)
    missing_live = sorted(set(resolved) - set(live_snapshot))
    if missing_live:
        raise ValueError(f"live snapshot missing correction addresses: {missing_live}")

    records = [
        build_record(address, resolved[address], decisions[address], live_snapshot[address])
        for address in sorted(resolved)
    ]
    apply_records = [record for record in records if record["classification"] == "confirmed-apply"]
    write_apply_plan(output_apply_plan_path, apply_records)
    apply_plan_sha256 = sha256_file(output_apply_plan_path)
    validate_apply_plan(
        output_apply_plan_path,
        expected_sha256=apply_plan_sha256,
        expected_count=len(apply_records),
    )
    counts = Counter(record["classification"] for record in records)
    result = {
        "schemaVersion": REVIEWED_PLAN_SCHEMA,
        "sourceManifestSha256": {
            "cursor": sha256_file(cursor_manifest),
            "targeted": sha256_file(targeted_manifest),
        },
        "liveSnapshotSha256": sha256_file(live_snapshot_path),
        "reviewedAddressCount": len(records),
        "classificationCounts": {
            classification: counts[classification]
            for classification in CLASSIFICATIONS
            if counts[classification]
        },
        "applyRecordCount": len(apply_records),
        "applyPlanSha256": apply_plan_sha256,
        "records": records,
    }
    output_manifest_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def validate_reviewed_plan_manifest(manifest: dict) -> list[dict]:
    if not isinstance(manifest, dict) or manifest.get("schemaVersion") != REVIEWED_PLAN_SCHEMA:
        raise ValueError("unsupported reviewed-correction plan schema")
    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("reviewed-correction plan must contain a non-empty records array")
    if manifest.get("reviewedAddressCount") != len(records):
        raise ValueError(
            "reviewedAddressCount mismatch: "
            f"declared={manifest.get('reviewedAddressCount')!r} actual={len(records)}"
        )

    seen: set[str] = set()
    counts: Counter[str] = Counter()
    required_strings = (
        "currentName",
        "currentSignature",
        "currentComment",
        "currentPrototypeKey",
        "correctedName",
        "correctedSignature",
        "correctedComment",
        "expectedCorrectedPrototypeKey",
    )
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("reviewed-correction plan contains a non-object record")
        address = normalize_address(record.get("address", ""))
        if record.get("address") != address:
            raise ValueError(f"reviewed address is not canonical: {record.get('address')!r}")
        if address in seen:
            raise ValueError(f"duplicate reviewed address: {address}")
        seen.add(address)
        classification = record.get("classification")
        if classification not in CLASSIFICATIONS:
            raise ValueError(f"invalid classification at {address}: {classification!r}")
        counts[classification] += 1
        fields = record.get("correctedFields")
        if (
            not isinstance(fields, list)
            or not fields
            or len(fields) != len(set(fields))
            or not set(fields).issubset(ALLOWED_FIELDS)
        ):
            raise ValueError(f"invalid correctedFields at {address}: {fields!r}")
        for key in required_strings:
            if not isinstance(record.get(key), str):
                raise ValueError(f"reviewed record {address} has invalid {key}")
        signature_class = record.get("signatureChangeClass")
        if "signature" in fields:
            if signature_class == "structured-prototype-change":
                if address != LEASED_STRUCTURED_PROTOTYPE_ADDRESS:
                    raise ValueError(f"structured signature address is not leased: {address}")
                if record["expectedCorrectedPrototypeKey"] == record["currentPrototypeKey"]:
                    raise ValueError(f"structured signature does not change prototype key at {address}")
            elif signature_class == "name-and-parameter-rendering-only":
                if record["expectedCorrectedPrototypeKey"] != record["currentPrototypeKey"]:
                    raise ValueError(f"rendering-only signature changes prototype key at {address}")
            else:
                raise ValueError(f"invalid signatureChangeClass at {address}: {signature_class!r}")
        elif signature_class is not None:
            raise ValueError(f"signatureChangeClass without signature field at {address}")

    expected_counts = {
        classification: counts[classification]
        for classification in CLASSIFICATIONS
        if counts[classification]
    }
    if manifest.get("classificationCounts") != expected_counts:
        raise ValueError(
            "classificationCounts mismatch: "
            f"declared={manifest.get('classificationCounts')!r} actual={expected_counts!r}"
        )
    if manifest.get("applyRecordCount") != counts["confirmed-apply"]:
        raise ValueError(
            "applyRecordCount mismatch: "
            f"declared={manifest.get('applyRecordCount')!r} "
            f"actual={counts['confirmed-apply']}"
        )
    for key in ("liveSnapshotSha256", "applyPlanSha256"):
        value = manifest.get(key)
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(f"invalid {key}")
    source_hashes = manifest.get("sourceManifestSha256")
    if not isinstance(source_hashes, dict) or set(source_hashes) != {"cursor", "targeted"}:
        raise ValueError("invalid sourceManifestSha256")
    for key, value in source_hashes.items():
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(f"invalid sourceManifestSha256.{key}")
    return records


def _verify_post_state_data(
    manifest: dict,
    snapshot: dict[str, dict[str, str]],
    *,
    expected_snapshot_count: int,
) -> dict:
    records = validate_reviewed_plan_manifest(manifest)
    if expected_snapshot_count <= 0:
        raise ValueError("expected snapshot count must be positive")
    if len(snapshot) != expected_snapshot_count:
        raise ValueError(
            "snapshot address count mismatch: "
            f"expected={expected_snapshot_count} actual={len(snapshot)}"
        )
    mismatches: list[dict] = []
    confirmed = 0
    unchanged = 0
    for record in records:
        address = normalize_address(record.get("address", ""))
        actual = snapshot.get(address)
        if actual is None:
            mismatches.append({"address": address, "field": "address", "expected": "present", "actual": "missing"})
            continue
        is_confirmed = record["classification"] == "confirmed-apply"
        if is_confirmed:
            confirmed += 1
            expected = {
                "name": record["correctedName"],
                "signature": record["correctedSignature"],
                "comment": record["correctedComment"],
                "prototypeKey": record["expectedCorrectedPrototypeKey"],
            }
        else:
            unchanged += 1
            expected = {
                "name": record["currentName"],
                "signature": record["currentSignature"],
                "comment": record["currentComment"],
                "prototypeKey": record["currentPrototypeKey"],
            }
        for field, expected_value in expected.items():
            if actual[field] != expected_value:
                mismatches.append(
                    {
                        "address": address,
                        "field": field,
                        "expected": expected_value,
                        "actual": actual[field],
                    }
                )
    return {
        "snapshotAddressCount": len(snapshot),
        "verifiedAddressCount": len(records),
        "confirmedAppliedCount": confirmed,
        "nonAppliedUnchangedCount": unchanged,
        "mismatches": mismatches,
    }


def verify_post_state(public_manifest_path: Path, post_snapshot_path: Path) -> dict:
    actual_manifest_sha256 = sha256_file(public_manifest_path)
    if actual_manifest_sha256 != EXPECTED_REVIEWED_PLAN_SHA256:
        raise ValueError(
            "reviewed plan SHA-256 mismatch: "
            f"expected={EXPECTED_REVIEWED_PLAN_SHA256} actual={actual_manifest_sha256}"
        )
    manifest = json.loads(public_manifest_path.read_text(encoding="utf-8"))
    if manifest.get("reviewedAddressCount") != EXPECTED_REVIEWED_ADDRESS_COUNT:
        raise ValueError("reviewed plan is not the exact accepted 92-address set")
    if manifest.get("classificationCounts") != {
        "confirmed-apply": EXPECTED_APPLY_RECORD_COUNT,
        "rejected-manifest-error": 1,
    }:
        raise ValueError("reviewed plan does not have the exact accepted 91/1 classification counts")
    if manifest.get("applyRecordCount") != EXPECTED_APPLY_RECORD_COUNT:
        raise ValueError("reviewed plan does not have exactly 91 apply records")
    rejected = [
        record.get("address")
        for record in manifest.get("records") or ()
        if record.get("classification") == "rejected-manifest-error"
    ]
    if rejected != [REJECTED_MANIFEST_ADDRESS]:
        raise ValueError("reviewed plan does not retain the exact rejected manifest address")
    snapshot = load_snapshot(post_snapshot_path)
    return _verify_post_state_data(
        manifest,
        snapshot,
        expected_snapshot_count=EXPECTED_POST_SNAPSHOT_COUNT,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--cursor-manifest", type=Path, required=True)
    build.add_argument("--targeted-manifest", type=Path, required=True)
    build.add_argument("--decisions", type=Path, required=True)
    build.add_argument("--live-snapshot", type=Path, required=True)
    build.add_argument("--output-manifest", type=Path, required=True)
    build.add_argument("--output-apply-plan", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "build":
        result = build_plan(
            args.cursor_manifest,
            args.targeted_manifest,
            args.decisions,
            args.live_snapshot,
            args.output_manifest,
            args.output_apply_plan,
        )
        print(json.dumps({key: value for key, value in result.items() if key != "records"}, indent=2))
        return 0
    result = verify_post_state(args.manifest, args.snapshot)
    print(json.dumps(result, indent=2))
    return 0 if not result["mismatches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
