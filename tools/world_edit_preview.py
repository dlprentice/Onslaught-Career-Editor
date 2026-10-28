#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Compare an editable world model with one selected original body, without writing or running anything.

    python tools/world_edit_preview.py world100.wrd world100.json
    python tools/world_edit_preview.py world100.wrd world100.json --baseline-sha256 SHA --model-sha256 SHA

Both paths are explicit, bounded inputs. Output contains hashes, field paths, changed-byte counts when the lengths
match, opaque-region changes and structural mission-script findings, never the world or script payloads. A preview
is not tied automatically to a later encode/stage command: compare the two input identities before using that command.
It does not check placement against terrain, resolve runtime slots/physics, run scripts or prove a level playable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import sys

import mission_script_inspect as mission
import world_resources_decode as decoder
import world_resources_encode as encoder

SCHEMA = "onslaught.world-edit-preview.v1"
MAX_BODY_BYTES = 32 * 1024 * 1024
MAX_MODEL_BYTES = 64 * 1024 * 1024
MAX_CHANGES = 512
MAX_SCRIPTS = 512
SHA = re.compile(r"[0-9a-f]{64}\Z")


class PreviewError(ValueError):
    """A selected input or its model could not be inspected safely."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _expect_sha(actual: str, expected: str | None, label: str) -> None:
    if expected is not None and (not isinstance(expected, str) or not SHA.fullmatch(expected) or actual != expected):
        raise PreviewError(f"{label}-identity-mismatch")


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise PreviewError("duplicate-model-key")
        if len(key) > 256:
            raise PreviewError("model-key-too-long")
        obj[key] = value
    return obj


def _reject_constant(_):
    raise PreviewError("non-finite-json-number-use-f32bits")


def _check_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise PreviewError("non-finite-json-number-use-f32bits")
    if isinstance(value, dict):
        for item in value.values():
            _check_finite(item)
    elif isinstance(value, list):
        for item in value:
            _check_finite(item)


def _load_model(raw: bytes):
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_reject_constant)
        _check_finite(value)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, PreviewError):
            raise
        raise PreviewError("invalid-model-json") from error
    if not isinstance(value, dict):
        raise PreviewError("model-must-be-object")
    return value


def _json_identity(value) -> str:
    data = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    return _sha(data)


def _same_scalar(a, b) -> bool:
    if type(a) is bool or type(b) is bool:
        return type(a) is type(b) and a == b
    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
        if a == b == 0 and (isinstance(a, float) or isinstance(b, float)):
            return math.copysign(1., a) == math.copysign(1., b)
        return a == b
    return type(a) is type(b) and a == b


def _changes(before, after, limit=MAX_CHANGES):
    """Return bounded changed paths and hashes, not values; list indexes are positional, not runtime slots."""
    out = []
    truncated = False

    def add(path, old, new, kind):
        nonlocal truncated
        if len(out) >= limit:
            truncated = True
            return
        row = {"path": path, "kind": kind}
        if old is not _MISSING:
            row["beforeSha256"] = _json_identity(old)
        if new is not _MISSING:
            row["afterSha256"] = _json_identity(new)
        out.append(row)

    def visit(a, b, path):
        nonlocal truncated
        if truncated:
            return
        if isinstance(a, dict) and isinstance(b, dict):
            # f32bits is an exact byte representation; upper/lowercase hex has the same bytes.
            if set(a) == set(b) == {"f32bits"} and isinstance(a["f32bits"], str) and isinstance(b["f32bits"], str):
                if a["f32bits"].lower() != b["f32bits"].lower():
                    add(path, a, b, "changed")
                return
            for key in sorted(a.keys() | b.keys()):
                if truncated:
                    return
                if key not in a:
                    add(path + [key], _MISSING, b[key], "added")
                elif key not in b:
                    add(path + [key], a[key], _MISSING, "removed")
                else:
                    visit(a[key], b[key], path + [key])
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                add(path + ["length"], len(a), len(b), "length-changed")
            for i in range(max(len(a), len(b))):
                if truncated:
                    return
                if i >= len(a):
                    add(path + [i], _MISSING, b[i], "added")
                elif i >= len(b):
                    add(path + [i], a[i], _MISSING, "removed")
                else:
                    visit(a[i], b[i], path + [i])
        elif not _same_scalar(a, b):
            add(path, a, b, "changed")

    visit(before, after, [])
    return {"entries": out, "truncated": truncated}


_MISSING = object()


def _opaque_identities(model):
    """Keep uninterpreted fields separate from the general change list, even if that list is truncated."""
    float_bits = []

    def collect(value, path):
        if isinstance(value, dict):
            if set(value) == {"f32bits"}:
                float_bits.append([path, value["f32bits"].lower()])
            else:
                for key in sorted(value):
                    collect(value[key], path + [key])
        elif isinstance(value, list):
            for index, item in enumerate(value):
                collect(item, path + [index])

    collect(model, [])
    return {
        "header-unused": _json_identity([model["header"].get("unused"), model["header"].get("v2Words")]),
        "influence-map": _json_identity(model.get("influenceMap")),
        "occupancy-grids": _json_identity([model.get("occupancyGrids"), model.get("legacyGridWords")]),
        "script-opaque-fields": _json_identity([
            [script.get("trailer"), script["code"].get("tail"),
             [symbol.get("flag") for symbol in script["code"].get("symbols", [])]]
            for script in model["scripts"]
        ]),
        "compiled-script-code": _json_identity([script["code"] for script in model["scripts"]]),
        "non-finite-float-bits": _json_identity(float_bits),
    }


def _script_report(model):
    rows = []
    for index, script in enumerate(model["scripts"][:MAX_SCRIPTS]):
        output = encoder.Writer()
        encoder.write_code(output, script["code"])
        raw = output.bytes()
        digest = _sha(raw)
        try:
            report = mission.inspect_script(raw, source_sha256=digest, record_sha256=digest)
            rows.append({"ordinal": index, "sha256": digest, "status": report["status"],
                         "findingCount": len(report["findings"]),
                         "findingCodes": sorted({finding["code"] for finding in report["findings"]})})
        except mission.InspectionError:
            rows.append({"ordinal": index, "sha256": digest, "status": "unsupported",
                         "findingCodes": ["inspection-profile-limit"]})
    return {"total": len(model["scripts"]), "inspected": len(rows), "truncated": len(model["scripts"]) > len(rows),
            "records": rows}


def preview_bytes(baseline: bytes, model_json: bytes, *, baseline_sha256=None, model_sha256=None) -> dict:
    """Pure preview of two immutable snapshots. Returned hashes identify exactly what was inspected."""
    if type(baseline) is not bytes or type(model_json) is not bytes:
        raise TypeError("baseline and model must be immutable bytes")
    if not 0 < len(baseline) <= MAX_BODY_BYTES or not 0 < len(model_json) <= MAX_MODEL_BYTES:
        raise PreviewError("input-byte-limit")
    baseline_digest, model_digest = _sha(baseline), _sha(model_json)
    _expect_sha(baseline_digest, baseline_sha256, "baseline")
    _expect_sha(model_digest, model_sha256, "model")
    model = _load_model(model_json)
    try:
        original = encoder.read_world_model(baseline)
        if encoder.write_world_body(original) != baseline:
            raise PreviewError("baseline-does-not-round-trip")
        candidate_body = encoder.write_world_body(model)
        if len(candidate_body) > MAX_BODY_BYTES:
            raise PreviewError("candidate-body-byte-limit")
        candidate = encoder.read_world_model(candidate_body)
        ignored = _changes(model, candidate)
        changes = _changes(original, candidate)
        old_opaque, new_opaque = _opaque_identities(original), _opaque_identities(candidate)
        old_scripts, new_scripts = _script_report(original), _script_report(candidate)
    except PreviewError:
        raise
    except (decoder.DecodeError, encoder.EncodeError, KeyError, TypeError, ValueError, IndexError, OverflowError,
            struct.error, RecursionError) as error:
        raise PreviewError(f"world-model-cannot-be-encoded-or-read: {type(error).__name__}") from error
    same_length = len(baseline) == len(candidate_body)
    first = next((i for i, (a, b) in enumerate(zip(baseline, candidate_body)) if a != b), None)
    if first is None and not same_length:
        first = min(len(baseline), len(candidate_body))
    opaque_changed = [key for key in old_opaque if old_opaque[key] != new_opaque[key]]
    things_changed = _json_identity(original["things"]) != _json_identity(candidate["things"])
    script_review = new_scripts["truncated"] or any(row["status"] != "complete" or row.get("findingCount", 0)
                                                     for row in new_scripts["records"])
    review = []
    if ignored["entries"] or ignored["truncated"]:
        review.append("model-fields-not-representable")
    if changes["truncated"]:
        review.append("change-list-truncated")
    if opaque_changed:
        review.append("opaque-or-compiled-data-changed")
    if script_review:
        review.append("script-inspection-findings-or-limits")
    return {
        "schema": SCHEMA,
        "baseline": {"bytes": len(baseline), "sha256": baseline_digest},
        "model": {"bytes": len(model_json), "sha256": model_digest},
        "candidateBody": {"bytes": len(candidate_body), "sha256": _sha(candidate_body),
                          "identicalToBaseline": candidate_body == baseline,
                          "firstDifferentOffset": first,
                          "changedBytePositions": sum(a != b for a, b in zip(baseline, candidate_body)) if same_length else None},
        "modelRoundTrip": {"representable": not ignored["entries"] and not ignored["truncated"], "differences": ignored},
        "changes": changes,
        "opaqueFields": {"changedGroups": opaque_changed, "baselineSha256": old_opaque, "candidateSha256": new_opaque},
        "slotReview": {"thingsChanged": things_changed,
                       "thingCountChanged": len(original["things"]) != len(candidate["things"]),
                       "baseLevelChanged": original["baseLevel"] != candidate["baseLevel"],
                       "waypointPathsChanged": _json_identity(original["waypointPaths"]) != _json_identity(candidate["waypointPaths"])},
        "scripts": {"baseline": old_scripts, "candidate": new_scripts, "structuralReviewRequired": script_review},
        "structuralReviewReasons": review,
        "limits": {"bodyBytes": MAX_BODY_BYTES, "modelBytes": MAX_MODEL_BYTES, "reportedChanges": MAX_CHANGES,
                   "scriptsPerSide": MAX_SCRIPTS},
        "scope": "Read-only structural comparison; not a terrain, runtime-slot, mission execution, career safety or gameplay validation. "
                 "Later encoding/staging must use the same two input identities. No visual editor or game launch is provided.",
    }


def _read_snapshot(path: Path, limit: int) -> bytes:
    """Read a regular file once, without following any path symlink; detect changes and replacement while reading."""
    if not all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_DIRECTORY", "O_CLOEXEC", "O_NONBLOCK")):
        raise PreviewError("descriptor-safe-file-reading-unavailable; use preview_bytes")
    path = Path(os.path.abspath(path))
    stamp = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_nlink)
    fd = mission._open_nofollow(path)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise PreviewError("input-type-or-byte-limit")
        chunks, total = [], 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, limit - total + 1))
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise PreviewError("input-grew-past-byte-limit")
            chunks.append(chunk)
        if total != before.st_size or stamp(before) != stamp(os.fstat(fd)):
            raise PreviewError("input-changed-during-read")
        check = mission._open_nofollow(path)
        try:
            if stamp(before) != stamp(os.fstat(check)):
                raise PreviewError("input-path-replaced-during-read")
        finally:
            os.close(check)
        return b"".join(chunks)
    finally:
        os.close(fd)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("baseline", type=Path, help="the selected original loose world body (.wrd)")
    ap.add_argument("model", type=Path, help="its edited JSON model")
    ap.add_argument("--baseline-sha256", help="refuse if the selected body differs from this SHA-256")
    ap.add_argument("--model-sha256", help="refuse if the selected model differs from this SHA-256")
    args = ap.parse_args(argv)
    try:
        report = preview_bytes(_read_snapshot(args.baseline, MAX_BODY_BYTES), _read_snapshot(args.model, MAX_MODEL_BYTES),
                               baseline_sha256=args.baseline_sha256, model_sha256=args.model_sha256)
    except (PreviewError, OSError) as error:
        print(f"world edit preview refused: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not report["structuralReviewReasons"] else 1


if __name__ == "__main__":
    sys.exit(main())
