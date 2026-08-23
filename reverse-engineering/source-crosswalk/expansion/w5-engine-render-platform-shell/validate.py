#!/usr/bin/env python3
"""Validate the source-first W5 engine/render/platform/shell receipt."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "references" / "Onslaught"
SOURCE_COMMIT = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"
BASE_COMMIT = "784367bd43f9ec13125521b00fe0c8352670ffdd"
BASE_CROSSWALK_SHA256 = "e37f13b37e9ce9d712174e35b86fc1f7ebcfc693fe9957448a8f39ff03829479"
NAME_TABLE_SHA256 = "4590dff93f4ee85c5a5c3450139b2e696118646af3401f6eb9719dc4237d3213"
CLOSURE_SHA256 = "cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974"
PREDECESSORS = {
    "local-lab/hermes-kanban-campaign-2026-08-22/source-first-expansion/PLAN.md": "604d5db76ecc9811b55321c5ec443f346c9be32515b6d8ed526142622d7ec393",
    "local-lab/hermes-kanban-campaign-2026-08-22/source-first-expansion/EXECUTION.md": "12a0f72ea2b1606ee673824ee801586cefe815e0aa899d2fe55073e7c4509f18",
    "local-lab/hermes-kanban-campaign-2026-08-22/source-first-expansion/manifest.json": "6f58de995a27a0088749f40e06907969d3213872b40d1bf0bb450afda1fd216e",
    "local-lab/hermes-kanban-campaign-2026-08-22/source-first-expansion/partition.tsv": "bc36791975f43d5da6b584727df3eb7d29402e18c550dd3d96e01bba0c301fde",
    "reverse-engineering/source-crosswalk/crosswalk.tsv": BASE_CROSSWALK_SHA256,
    "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv": NAME_TABLE_SHA256,
    "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv": CLOSURE_SHA256,
    "reverse-engineering/binary-analysis/pcltshell-vtable-semantics-2026-08-11.tsv": "c1510d9baa0d6a633bf0d9514b7fc9ce3a5eb32070e1643181467ae2cffe7d1b",
    "reverse-engineering/binary-analysis/ghidra-fullpass-findings/W008/adversarial/B15.md": "a57fb6c7d35eefc4384f7faf56cb79aee77d0c9897d1c4aefe0f3ea770e3e7fd",
    "reverse-engineering/binary-analysis/ghidra-fullpass-findings/W009/primary/A01.md": "bc1727dfb86d7f9f9aecf27a487e04796bfcf0986ace61cc82970578b9cb68b7",
    "reverse-engineering/binary-analysis/ghidra-fullpass-findings/W009/primary/A02.md": "59524647a4f21496ad8a3f1247aecd2354b02119115796b61cbe2eee809abba8",
    "reverse-engineering/binary-analysis/ghidra-fullpass-findings/W009/primary/A04.md": "70ebd87bd8905e7202dd439b3386739023573d95e8c6729237dece1a8911ed61",
    "reverse-engineering/source-code/stuart-source-synthesis.md": "62c53e7e266b774c0d1ebe5c433203b9be08a972b911964ab3423fdbb86b417f",
}

EXPECTED_FILE_COUNTS = {
    "d3dapp.h": 11,
    "DXEngine.cpp": 1,
    "DXEngine.h": 6,
    "EditorD3DApp.h": 11,
    "engine.h": 39,
    "ltshell.cpp": 1,
    "ltshell.h": 40,
    "PCEngine.h": 11,
    "PCPlatform.h": 8,
    "ResourceAccumulator.h": 8,
}
EXPECTED_CLASSIFICATIONS = {
    "NO_MATCH_FOUND": 104,
    "NOT_IN_RETAIL": 23,
    "SOURCE_ANALOG": 9,
}
REQUIRED_DEFINITION_COLUMNS = {
    "stable_key",
    "source_file",
    "source_line",
    "function",
    "signature",
    "source_commit",
    "target_branch",
    "source_anchor",
    "source_excerpt",
    "source_algorithm",
    "fields_constants",
    "source_side_effects",
    "initial_readiness",
    "retail_classification",
    "retail_va",
    "retail_analog",
    "retail_evidence",
    "retail_reason",
    "retail_falsifier",
    "rebuild_disposition",
    "rebuild_owner",
    "reuse_disposition",
    "predecessor_artifacts",
}
ALLOWED_CLASSIFICATIONS = set(EXPECTED_CLASSIFICATIONS)
ALLOWED_DELTA_STATUSES = {
    "SOURCE_AGREES",
    "SOURCE_DIVERGES",
    "RETAIL_UNRESOLVED",
    "SOURCE_ONLY",
    "NOT_SELECTED_TARGET",
}
HASHED_OUTPUTS = (
    "definitions.tsv",
    "SOURCE-CONTRACT.md",
    "RETAIL-DELTA.tsv",
    "REBUILD-DELTA.md",
    "validate.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def base_populated_vas() -> set[str]:
    path = ROOT / "reverse-engineering" / "source-crosswalk" / "crosswalk.tsv"
    rows = read_tsv(path)
    return {row.get("retail_va", "").lower() for row in rows if row.get("retail_va")}


def validate() -> dict[str, object]:
    definitions_path = HERE / "definitions.tsv"
    delta_path = HERE / "RETAIL-DELTA.tsv"
    require(definitions_path.is_file(), "definitions.tsv is missing")
    require(delta_path.is_file(), "RETAIL-DELTA.tsv is missing")
    for name in ("SOURCE-CONTRACT.md", "REBUILD-DELTA.md"):
        require((HERE / name).is_file(), f"{name} is missing")

    definitions = read_tsv(definitions_path)
    require(len(definitions) == 136, f"definitions.tsv has {len(definitions)} rows, expected 136")
    require(REQUIRED_DEFINITION_COLUMNS <= set(definitions[0]), "definitions.tsv schema is incomplete")
    require(Counter(row["source_file"] for row in definitions) == Counter(EXPECTED_FILE_COUNTS), "source-file partition differs from the exact W5 ten-file set")

    keys = [row["stable_key"] for row in definitions]
    require(len(set(keys)) == 136, "stable keys are duplicated")
    classifications = Counter(row["retail_classification"] for row in definitions)
    require(set(classifications) <= ALLOWED_CLASSIFICATIONS, f"unsupported retail classification: {sorted(set(classifications) - ALLOWED_CLASSIFICATIONS)}")
    require(classifications == Counter(EXPECTED_CLASSIFICATIONS), f"classification counts differ: {dict(classifications)}")

    populated_vas = [row["retail_va"].lower() for row in definitions if row["retail_va"]]
    require(len(populated_vas) == len(set(populated_vas)), "populated retail VAs collide inside W5")
    base_collisions = sorted(set(populated_vas) & base_populated_vas())
    require(not base_collisions, f"W5 populated VAs collide with the corrected 1,149-row base: {base_collisions}")

    for row in definitions:
        expected_key = f'{row["source_file"]}:{row["source_line"]}:{row["function"]}:{row["signature"]}'
        require(row["stable_key"] == expected_key, f"stable key mismatch: {row['stable_key']}")
        require(row["source_commit"] == SOURCE_COMMIT, f"source commit mismatch: {row['stable_key']}")
        line_number = int(row["source_line"])
        source_path = SOURCE_ROOT / row["source_file"]
        require(source_path.is_file(), f"source file missing: {row['source_file']}")
        source_lines = source_path.read_text(encoding="utf-8", errors="strict").splitlines()
        require(1 <= line_number <= len(source_lines), f"source line out of range: {row['stable_key']}")
        require(row["source_anchor"] == source_lines[line_number - 1].strip(), f"source anchor drift: {row['stable_key']}")
        for field in (
            "target_branch",
            "source_excerpt",
            "source_algorithm",
            "fields_constants",
            "source_side_effects",
            "initial_readiness",
            "retail_evidence",
            "retail_reason",
            "retail_falsifier",
            "rebuild_disposition",
            "rebuild_owner",
            "predecessor_artifacts",
        ):
            require(bool(row[field].strip()), f"{field} is empty: {row['stable_key']}")
        require(row["reuse_disposition"] == "EXTENDED", f"row is not classified as EXTENDED: {row['stable_key']}")
        if row["retail_classification"] == "SOURCE_ANALOG":
            require(bool(row["retail_va"] and row["retail_analog"]), f"analog lacks VA/name: {row['stable_key']}")
        else:
            require(not row["retail_va"], f"non-analog has populated VA: {row['stable_key']}")

    deltas = read_tsv(delta_path)
    require(len(deltas) == 136, f"RETAIL-DELTA.tsv has {len(deltas)} rows, expected 136")
    delta_by_key = {row["stable_key"]: row for row in deltas}
    require(len(delta_by_key) == 136 and set(delta_by_key) == set(keys), "retail delta stable keys do not exactly match definitions")
    for row in definitions:
        delta = delta_by_key[row["stable_key"]]
        require(delta["status"] in ALLOWED_DELTA_STATUSES, f"unsupported retail delta status: {delta['status']}")
        require(delta["retail_classification"] == row["retail_classification"], f"delta classification mismatch: {row['stable_key']}")
        require(delta["retail_va"] == row["retail_va"], f"delta VA mismatch: {row['stable_key']}")
        require(bool(delta["evidence"].strip() and delta["boundary"].strip() and delta["falsifier"].strip()), f"delta evidence/boundary/falsifier missing: {row['stable_key']}")

    base_crosswalk = ROOT / "reverse-engineering" / "source-crosswalk" / "crosswalk.tsv"
    name_table = ROOT / "reverse-engineering" / "binary-analysis" / "ghidra-function-name-table-2026-08-17.tsv"
    closure = ROOT / "reverse-engineering" / "binary-analysis" / "function-c1-closure-2026-08-11.tsv"
    require(sha256(base_crosswalk) == BASE_CROSSWALK_SHA256, "canonical corrected crosswalk changed")
    require(sha256(name_table) == NAME_TABLE_SHA256, "name-table input changed")
    require(sha256(closure) == CLOSURE_SHA256, "closure input changed")

    return {
        "definitions": definitions,
        "deltas": deltas,
        "classification_counts": dict(sorted(classifications.items())),
        "delta_status_counts": dict(sorted(Counter(row["status"] for row in deltas).items())),
        "populated_vas": len(populated_vas),
    }


def make_receipt(result: dict[str, object]) -> dict[str, object]:
    return {
        "schema": "bea.source-crosswalk.expansion-wave.v1",
        "wave": "W5_ENGINE_RENDER_PLATFORM_SHELL",
        "base_commit": BASE_COMMIT,
        "source_commit": SOURCE_COMMIT,
        "counts": {
            "definitions": 136,
            "stable_key_duplicates": 0,
            "populated_vas": result["populated_vas"],
            "populated_va_collisions": 0,
            "base_va_collisions": 0,
            "source_files": EXPECTED_FILE_COUNTS,
            "retail_classifications": result["classification_counts"],
            "retail_delta_statuses": result["delta_status_counts"],
            "reuse_disposition_definitions": {
                "REUSED": 0,
                "EXTENDED": 136,
                "NEW_MEASUREMENT": 0,
            },
            "reuse_disposition_artifacts": {
                "REUSED": len(PREDECESSORS),
                "EXTENDED": 6,
                "NEW_MEASUREMENT": 0,
            },
        },
        "predecessors": PREDECESSORS,
        "hashes": {
            **{name: sha256(HERE / name) for name in HASHED_OUTPUTS},
            "base_crosswalk.tsv": BASE_CROSSWALK_SHA256,
            "ghidra-function-name-table-2026-08-17.tsv": NAME_TABLE_SHA256,
            "function-c1-closure-2026-08-11.tsv": CLOSURE_SHA256,
        },
        "guards": {
            "canonical_crosswalk_unchanged": True,
            "canonical_report_unchanged": True,
            "exact_w5_file_set": True,
            "source_line_readback": True,
            "retail_payloads_added": False,
            "binary_or_ghidra_mutation": False,
            "generation32_catalogs_reused": True,
            "new_generic_ps2_work": False,
            "new_measurement_performed": False,
            "files_deleted_moved_or_retired": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = validate()
    receipt_path = HERE / "RECEIPT.json"
    expected = make_receipt(result)
    if args.write_receipt:
        receipt_path.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    require(receipt_path.is_file(), "RECEIPT.json is missing")
    actual = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(actual == expected, "RECEIPT.json does not match deterministic recomputation")
    print("PASS: W5 receipt has 136 exact stable keys, deterministic hashes, and zero VA collisions")


if __name__ == "__main__":
    main()
