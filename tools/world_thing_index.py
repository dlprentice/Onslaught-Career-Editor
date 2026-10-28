#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""List stored thing ordinals and positions for the stream-only world editor.

    python tools/world_thing_index.py WORLD.wrd --stdout
    python tools/world_thing_index.py WORLD.wrd --start 100 --limit 100 --stdout

The selected body is read once through a Linux no-follow file reader; the
report contains metadata and a source hash, not world bytes or script bodies.
The thing ordinal identifies the serialized row in this exact body; it is not
a runtime slot, stable identity or proof that a thing spawns. Position values
are serialized fields, not validated terrain placement. The report cannot
identify the source level, determine gameplay or prove a move is safe.

The CLI writes no report file. Shell redirection and all later file handling
are outside its control; never redirect into a game or user folder. Reports
can contain private game or user-authored names; keep them private. The CLI
requires Linux descriptor-relative O_PATH and /proc/self/fd. A Python caller
can pass already-owned bytes to report_bytes on other platforms.
"""
from __future__ import annotations

import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any

import model_transform_catalog as selected
import world_edit_preview as preview
import world_resources_decode as decoder
import world_resources_encode as encoder

SCHEMA = "onslaught.world-thing-index.v1"
MAX_THINGS = 1000
MAX_PAGE = 128


class WorldIndexError(ValueError):
    """The selected body or requested page cannot be inspected."""


def _coordinate(value: Any) -> dict[str, Any]:
    raw = encoder.f32_out(value)
    number = struct.unpack("<f", raw)[0]
    return {"value": number if math.isfinite(number) else None,
            "float32LittleEndianHex": raw.hex(),
            "finite": math.isfinite(number)}


def report_for(body: bytes, *, start: int = 0, limit: int = 100) -> dict[str, Any]:
    """Index selected bytes without writing; a successful decode must round-trip exactly."""
    if type(body) is not bytes or not 0 < len(body) <= preview.MAX_BODY_BYTES:
        raise WorldIndexError("input-byte-limit")
    if type(start) is not int or start < 0:
        raise WorldIndexError("start-must-be-nonnegative-integer")
    if type(limit) is not int or not 1 <= limit <= MAX_PAGE:
        raise WorldIndexError("page-limit-out-of-range")
    try:
        model = encoder.read_world_model(body)
        things = model["things"]
        if len(things) > MAX_THINGS:
            raise WorldIndexError("thing-count-over-editor-limit")
        if encoder.write_world_body(model) != body:
            raise WorldIndexError("baseline-does-not-round-trip")
        if start > len(things):
            raise WorldIndexError("start-past-thing-count")
        end = min(start + limit, len(things))
        rows = []
        for ordinal in range(start, end):
            thing = things[ordinal]
            init = thing["init"]
            rows.append({"ordinal": ordinal, "objectId": thing["oid"], "serializedKind": thing["kind"],
                         "name": init["name"], "definition": thing.get("definition"),
                         "position": [_coordinate(value) for value in init["position"]]})
        return {
            "schema": SCHEMA,
            "generatedRetailDerived": True,
            "baseline": {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body),
                         "bodyVersion": model["version"], "roundTripExact": True},
            "pagination": {"thingCount": len(things), "startOrdinal": start, "limit": limit,
                           "nextOrdinal": end if end < len(things) else None},
            "things": rows,
            "scope": "Stored rows in one selected world body. Ordinals are not runtime slots or stable identities; "
                     "level ownership, script effects, terrain placement and gameplay are not established.",
            "evidence": ["onslaught-decomp src/world.cpp CWorld::LoadWorld @0x0050b9c0",
                         "tools/world_resources_encode.py:read_world_model and write_world_body"],
        }
    except WorldIndexError:
        raise
    except (decoder.DecodeError, encoder.EncodeError, KeyError, TypeError, ValueError, OverflowError,
            IndexError, struct.error, RecursionError) as error:
        raise WorldIndexError(f"world-body-cannot-be-indexed: {type(error).__name__}") from error


def report_bytes(body: bytes, *, start: int = 0, limit: int = 100) -> bytes:
    """Return deterministic UTF-8 metadata; the caller controls any persistence or disclosure."""
    report = report_for(body, start=start, limit=limit)
    return (json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                 allow_abbrev=False)
    ap.add_argument("baseline", type=Path, help="selected world body; no parent traversal or symlinks")
    ap.add_argument("--start", type=int, default=0, help="first zero-based stored thing ordinal")
    ap.add_argument("--limit", type=int, default=100, help="maximum rows per page, 1..128")
    ap.add_argument("--baseline-sha256", help="require this exact source-body hash")
    ap.add_argument("--stdout", action="store_true", required=True, help="emit private metadata to stdout")
    args = ap.parse_args(argv)
    try:
        path = selected._selected_path(args.baseline)
        body, stamp = selected._read_selected_mesh(path)
        preview._expect_sha(hashlib.sha256(body).hexdigest(), args.baseline_sha256, "baseline")
        payload = report_bytes(body, start=args.start, limit=args.limit)
        selected._check_input_bindings([(path, stamp)])
        output = payload.decode("ascii")
        if sys.stdout.write(output) != len(output):
            raise WorldIndexError("stdout-stream-incomplete")
        sys.stdout.flush()
    except (WorldIndexError, preview.PreviewError, ValueError, OSError, RuntimeError) as error:
        print(f"world thing index refused: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
