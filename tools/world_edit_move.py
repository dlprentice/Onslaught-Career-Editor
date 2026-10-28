#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Preview one thing-position edit, then optionally save its reviewed model under local-data/.

    python tools/world_edit_move.py world100.wrd --thing 0 --position 12.5 -40 3
    python tools/world_edit_move.py world100.wrd --thing 0 --position 12.5 -40 3 \\
        --baseline-sha256 BASELINE --model-sha256 MODEL --game DIR \\
        --out edits/world100.json --acknowledge-unvalidated

The first command is read-only. The second re-creates the same candidate, requires both hashes from the
preview, and publishes a new JSON model only below this checkout's ignored local-data/. It never writes a
world body, stages a mod, or launches a game. Output models can contain game data and must remain private.
Coordinates are float32: pass --allow-rounding only after accepting the displayed float32 value. A preview
checks serialized changes, not terrain, runtime slots, scripts, saves, physics, or playability.
"""
from __future__ import annotations

import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True

import argparse
import copy
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import os
from pathlib import Path
import struct

import world_edit_preview as preview
import world_resources_decode as decoder
import world_resources_encode as encoder
from safe_generated_output import UnsafeGeneratedOutputError

ROOT = Path(__file__).resolve().parent.parent
LOCAL_DATA = ROOT / "local-data"
SCHEMA = "onslaught.world-edit-move.v1"


class MoveError(ValueError):
    """An edit cannot be safely represented or its reviewed identity did not match."""


def _coordinates(values, allow_rounding):
    if len(values) != 3:
        raise MoveError("exactly-three-coordinates-required")
    result = []
    details = []
    for value in values:
        if not isinstance(value, str) or len(value) > 128:
            raise MoveError("invalid-coordinate")
        try:
            requested = Decimal(value)
            if not requested.is_finite():
                raise MoveError("coordinates-must-be-finite")
            as_float = float(requested)
            if not math.isfinite(as_float):
                raise MoveError("coordinate-outside-float32-range")
            packed = struct.pack("<f", as_float)
            stored = struct.unpack("<f", packed)[0]
            if not math.isfinite(stored):
                raise MoveError("coordinate-outside-float32-range")
        except (InvalidOperation, OverflowError, ValueError, struct.error) as error:
            if isinstance(error, MoveError):
                raise
            raise MoveError("invalid-or-out-of-range-coordinate") from error
        rounded = Decimal.from_float(stored) != requested
        if rounded and not allow_rounding:
            raise MoveError(f"coordinate-needs-float32-rounding: {value}; stored={stored!r}; use --allow-rounding")
        result.append(stored)
        details.append({"requested": value, "stored": stored, "float32LittleEndianHex": packed.hex(),
                        "rounded": rounded})
    return result, details


def _model_json(model):
    return (json.dumps(model, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n").encode("ascii")


def prepare_move(baseline: bytes, thing: int, coordinates: list[str], *, allow_rounding: bool = False):
    """Return a candidate model and a report, without writing; reject anything outside one position."""
    if type(baseline) is not bytes or not 0 < len(baseline) <= preview.MAX_BODY_BYTES:
        raise MoveError("input-byte-limit")
    if type(thing) is not int or thing < 0:
        raise MoveError("thing-ordinal-invalid")
    position, details = _coordinates(coordinates, allow_rounding)
    try:
        original = encoder.read_world_model(baseline)
        if encoder.write_world_body(original) != baseline:
            raise MoveError("baseline-does-not-round-trip")
        things = original["things"]
        if thing >= len(things):
            raise MoveError("thing-ordinal-out-of-range")
        old = things[thing]["init"]["position"]
        if len(old) != 3 or any(type(v) is not float or not math.isfinite(v) for v in old):
            raise MoveError("existing-position-not-three-finite-float32-values")

        # Locate the selected serialized position through the *same* encoder: inverting all twelve
        # bytes in a separate throwaway model must change exactly one contiguous 12-byte span.
        # This permits a byte-level preservation check without a second world-format parser.
        probe = copy.deepcopy(original)
        original_position_bytes = b"".join(encoder.f32_out(value) for value in old)
        flipped = bytes(value ^ 0xFF for value in original_position_bytes)
        probe["things"][thing]["init"]["position"] = [
            {"f32bits": flipped[i:i + 4].hex()} for i in (0, 4, 8)]
        probe_body = encoder.write_world_body(probe)
        if len(probe_body) != len(baseline):
            raise MoveError("cannot-locate-exact-position-bytes")
        start, count = None, 0
        for index, (before, after) in enumerate(zip(baseline, probe_body)):
            if before != after:
                if start is None:
                    start = index
                if index != start + count or count >= 12:
                    raise MoveError("cannot-locate-exact-position-bytes")
                count += 1
        if count != 12 or start is None:
            raise MoveError("cannot-locate-exact-position-bytes")
        if baseline[start:start + 12] != original_position_bytes or probe_body[start:start + 12] != flipped:
            raise MoveError("position-byte-locator-mismatch")

        candidate = copy.deepcopy(original)
        candidate["things"][thing]["init"]["position"] = position
        candidate_body = encoder.write_world_body(candidate)
        if candidate_body == baseline:
            raise MoveError("position-unchanged")
        if (len(candidate_body) != len(baseline) or candidate_body[:start] != baseline[:start] or
                candidate_body[start + 12:] != baseline[start + 12:] or
                candidate_body[start:start + 12] != b"".join(encoder.f32_out(value) for value in position)):
            raise MoveError("candidate-changes-outside-selected-position")
        raw = _model_json(candidate)
        report = preview.preview_bytes(baseline, raw)
        paths = [entry["path"] for entry in report["changes"]["entries"]]
        expected_prefix = ["things", thing, "init", "position"]
        if (not report["modelRoundTrip"]["representable"] or report["changes"]["truncated"] or
                not paths or any(len(path) != 5 or path[:4] != expected_prefix or path[4] not in (0, 1, 2)
                                 for path in paths) or
                report["opaqueFields"]["changedGroups"] or
                report["scripts"]["baseline"] != report["scripts"]["candidate"] or
                not report["slotReview"]["positionFieldsChanged"] or
                any(report["slotReview"][key] for key in ("thingCountChanged", "exactRecordPermutationObserved",
                    "nonPositionFieldsOrOrderChanged", "targetFieldsChanged", "baseLevelChanged", "mapNumberChanged",
                    "waypointPathsChanged"))):
            raise MoveError("preview-found-an-unsupported-change")
        return raw, {"schema": SCHEMA, "thingOrdinal": thing, "requestedPosition": details,
                     "selectedPositionByteOffset": start, "preview": report,
                     "reviewRequired": True,
                     "scope": "Only the selected serialized position is changed. Placement, runtime identity, "
                              "mission behavior and save compatibility are unvalidated; this is not a visual editor."}
    except MoveError:
        raise
    except (decoder.DecodeError, encoder.EncodeError, preview.PreviewError, KeyError, TypeError, ValueError,
            IndexError, OverflowError, struct.error, RecursionError) as error:
        raise MoveError(f"world-model-cannot-be-edited: {type(error).__name__}") from error


def _output_path(relative: Path) -> Path:
    if (relative.is_absolute() or not relative.parts or ".." in relative.parts or
            relative.suffix.lower() != ".json"):
        raise MoveError("output-must-be-a-relative-json-path-below-local-data")
    return LOCAL_DATA / relative


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("baseline", type=Path, help="selected loose world body; read once, with no symlink traversal")
    ap.add_argument("--thing", type=int, required=True, help="zero-based ordinal in this exact body")
    ap.add_argument("--position", nargs=3, required=True, metavar=("X", "Y", "Z"))
    ap.add_argument("--allow-rounding", action="store_true", help="accept displayed float32 rounding")
    ap.add_argument("--baseline-sha256", help="pin the body used in the preceding preview")
    ap.add_argument("--model-sha256", help="pin the candidate model from the preceding preview")
    ap.add_argument("--game", type=Path, help="selected game folder, protected from output")
    ap.add_argument("--out", type=Path, help="fresh JSON path relative to this checkout's local-data/")
    ap.add_argument("--acknowledge-unvalidated", action="store_true", help="acknowledge placement and gameplay remain unvalidated")
    args = ap.parse_args(argv)
    try:
        if args.out is not None and (args.game is None or not args.baseline_sha256 or not args.model_sha256 or
                                     not args.acknowledge_unvalidated):
            raise MoveError("saving-requires-game-both-preview-hashes-and-acknowledgement")
        if args.out is None and (args.game is not None or args.acknowledge_unvalidated):
            raise MoveError("game-and-acknowledgement-require-output")
        body = preview._read_snapshot(args.baseline, preview.MAX_BODY_BYTES)
        raw, report = prepare_move(body, args.thing, args.position, allow_rounding=args.allow_rounding)
        preview._expect_sha(hashlib.sha256(body).hexdigest(), args.baseline_sha256, "baseline")
        preview._expect_sha(hashlib.sha256(raw).hexdigest(), args.model_sha256, "model")
        if args.out is not None:
            if not args.game.is_dir():
                raise MoveError("selected-game-folder-must-exist")
            out = _output_path(args.out)
            encoder.publish_fresh(out.parent, args.game, [(out, raw)])
            report["publication"] = {"path": str(out), "sha256": hashlib.sha256(raw).hexdigest(),
                                     "status": "new-private-model-not-staged"}
        else:
            report["publication"] = {"status": "preview-only"}
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (MoveError, preview.PreviewError, UnsafeGeneratedOutputError, OSError) as error:
        print(f"world move refused: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
