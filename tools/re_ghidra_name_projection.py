#!/usr/bin/env python3
"""Build or verify the tracked four-column Ghidra name projection.

The full inventory is intentionally kept in ``local-lab``.  This tool emits the
small tracked address/name/body-range view used by documentation checks while
pinning the exact full-inventory bytes that produced it.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path
import re
import sys
import tempfile


REQUIRED_COLUMNS = {"address", "name", "bodyMin", "bodyMax"}
ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]{8}\Z")


class ProjectionError(RuntimeError):
    pass


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def projection_bytes(
    inventory: Path,
    *,
    expected_inventory_sha256: str,
    source_label: str,
    projection_date: str,
    specimen_sha256: str,
) -> bytes:
    raw = inventory.read_bytes()
    actual_sha256 = sha256_bytes(raw)
    if actual_sha256 != expected_inventory_sha256.lower():
        raise ProjectionError(
            "full inventory SHA-256 differs: "
            f"expected={expected_inventory_sha256.lower()} actual={actual_sha256}"
        )

    rows: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    with inventory.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ProjectionError("full inventory lacks required columns")
        for line_number, row in enumerate(reader, start=2):
            address = (row.get("address") or "").lower()
            name = row.get("name") or ""
            body_min = (row.get("bodyMin") or "").lower()
            body_max = (row.get("bodyMax") or "").lower()
            if not all(ADDRESS_RE.fullmatch(value) for value in (address, body_min, body_max)):
                raise ProjectionError(f"malformed address at inventory line {line_number}")
            if address in seen:
                raise ProjectionError(f"duplicate address at inventory line {line_number}: {address}")
            if any(char in name for char in "\t\r\n") or not name:
                raise ProjectionError(f"unsafe/empty name at inventory line {line_number}")
            if int(body_min, 16) > int(address, 16) or int(address, 16) > int(body_max, 16):
                raise ProjectionError(f"entry lies outside body at inventory line {line_number}")
            seen.add(address)
            rows.append((address, name, body_min, body_max))

    if not rows:
        raise ProjectionError("full inventory has no function rows")
    if rows != sorted(rows, key=lambda item: int(item[0], 16)):
        raise ProjectionError("full inventory is not strictly address ordered")

    header = [
        "# Ghidra function-name table -- address -> current saved symbol",
        "# Purpose : tracked resolution authority for address/name documentation checks.",
        "#           It is a name index, not a database, disassembly, or semantic proof.",
        f"# Projection date: {projection_date}",
        f"# Specimen SHA-256: {specimen_sha256.lower()}",
        f"# Source  : {source_label}",
        f"# Source bytes: {len(raw)}",
        f"# Source SHA-256: {actual_sha256}",
        f"# Rows    : {len(rows)} internal functions; this is a discovered census, not a final ceiling.",
        "# Columns : address, name, bodyMin, bodyMax (hex). Non-contiguous bodies are",
        "#           represented by their bounding range, so bodyMin..bodyMax can over-cover.",
        "address\tname\tbodyMin\tbodyMax",
    ]
    lines = header + ["\t".join(row) for row in rows]
    return ("\n".join(lines) + "\n").encode("utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("create", "verify"))
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-inventory-sha256", required=True)
    parser.add_argument("--source-label", required=True)
    parser.add_argument("--projection-date", required=True)
    parser.add_argument("--specimen-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        expected = projection_bytes(
            args.inventory,
            expected_inventory_sha256=args.expected_inventory_sha256,
            source_label=args.source_label,
            projection_date=args.projection_date,
            specimen_sha256=args.specimen_sha256,
        )
        if args.mode == "verify":
            actual = args.output.read_bytes()
            if actual != expected:
                raise ProjectionError(
                    "tracked projection differs: "
                    f"expected={sha256_bytes(expected)} actual={sha256_bytes(actual)}"
                )
        else:
            if args.output.exists():
                raise ProjectionError(f"output already exists: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temp_name = tempfile.mkstemp(
                prefix=f".{args.output.name}.", suffix=".partial", dir=args.output.parent
            )
            temp = Path(temp_name)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(expected)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.link(temp, args.output)
            finally:
                temp.unlink(missing_ok=True)
        projected_rows = sum(
            1 for line in expected.splitlines() if line and not line.startswith(b"#")
        ) - 1
        print(
            f"READY rows={projected_rows} bytes={len(expected)} "
            f"sha256={sha256_bytes(expected)} output={args.output}"
        )
        return 0
    except (OSError, ProjectionError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
