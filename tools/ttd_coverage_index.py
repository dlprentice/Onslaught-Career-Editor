# SPDX-License-Identifier: GPL-3.0-or-later
#
# Canonical offline index + cross-trace query over the retained TTD exec-
# coverage receipts (PROGRAM P5).
#
# WHY THIS EXISTS
# ---------------
# Every retained trace left behind a per-trace coverage receipt
# (`coverage.jsonl`, schema `bea.ttd.exec-coverage.v1`) under G:\\bea-ttd\\,
# but answering "which retained traces ever executed address X?" still meant
# launching a fresh cdb/TTD session or writing another throwaway walk.  This
# tool turns the existing receipts into ONE hashed, validated index and then
# answers unlimited cross-trace questions offline.  It launches nothing: no
# debugger, no trace recording.  The receipts are consumed strictly read-only
# and are hash-bound into every output, so an answer carries the identity of
# the exact inputs that produced it.
#
# FAIL-CLOSED CONTRACT
# --------------------
# An index that silently skips a broken receipt produces confident lies, so
# every defect aborts the build with exit code 2 and names the file and line:
#   - non-JSON, wrong-schema, unknown-kind, missing-field, or blank rows;
#   - missing/duplicate/malformed gap summaries or contradictory accounting;
#   - unreadable receipt subtrees (os.walk errors are never skipped);
#   - duplicate or overlapping range rows inside one receipt;
#   - rows whose VA-RVA width disagrees or whose byte_count contradicts the
#     row's own span;
#   - ranges outside the metadata module's mapped span (out-of-domain);
#   - per-trace covered bytes disagreeing with the receipt's own summary
#     `covered_bytes`;
#   - assertion rows disagreeing with the range data or whose VA/RVA delta is
#     not the metadata module base (an instrument that contradicts its own
#     measurements is broken, not merely mistaken);
#   - summaries outside the two measured terminal classes (run-to-completion
#     Process, or timer-stopped Thread), failed marker assertions, duplicate
#     trace names, or divergent module bases across receipts.
# Counter quarantines are not hidden or rehabilitated: affected trace names and
# flags remain explicit in the index while every range row is independently
# revalidated.
# Readback fails closed too, before any membership answer: every per-trace
# receipt path must be canonical -- relative, forward-slash, fully normalized
# (`<trace>/coverage.jsonl`), never absolute in any host syntax (Windows drive,
# drive-relative colon syntax, UNC, or POSIX-rooted) -- so a tampered index can
# never re-bind a receipt to an attacker-chosen location.
# Queries fail closed too: exit code 2 for structural problems (bad index,
# bad address) and exit code 1 when a declared must-hit/must-miss control is
# violated -- the result JSON still prints either way, because a refuted
# answer is itself an answer.
#
# RECEIPT-SET HASH
# ----------------
# `receipt_set_sha256` is sha256 over the UTF-8 lines
# `<relpath>\n<sha256-of-file>\n` for every consumed receipt in sorted relpath
# order.  Recomputable from the receipts alone.
#
# USAGE
# -----
#   py -3 tools\ttd_coverage_index.py build --root G:\bea-ttd \
#       --out .artifacts\ttd-coverage-index.json
#   py -3 tools\ttd_coverage_index.py query --index .artifacts\ttd-coverage-index.json \
#       --va 0x00407060,0x004f9a90 --expect-hit 0x004f9a90 --expect-miss 0x00672fd0
#
# Addresses may be given as absolute VAs (--va) or as RVAs against the common
# module base (--rva).  Any address list works; nothing here knows about
# FireLock or any other function.

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

SCHEMA_RECEIPT = "bea.ttd.exec-coverage.v1"
SCHEMA_INDEX = "bea.ttd.coverage-index.v1"
SCHEMA_QUERY = "bea.ttd.coverage-query.v1"

RECEIPT_FILENAME = "coverage.jsonl"

REQUIRED_ASSERTION_EXPECTATIONS = ("hit", "miss")
GAP_BUCKET_FIELDS = (
    "kind_no_gap",
    "kind_context_switch",
    "kind_unrecorded",
    "kind_large",
)
GAP_EVENT_FIELDS = (
    "event_SyntheticSequence",
    "event_CodeCacheFlush",
    "event_PreAtomicOperation",
    "event_PotentialAtomicCollision",
    "event_EtwEvent",
    "event_DebugBreak",
    "event_FastFail",
    "event_KernelCall",
    "event_SyntheticFallback",
    "event_ExceptionDispatch",
    "event_UnknownInstruction",
    "event_ThreadSuspended",
    "event_SListRollback",
    "event_SyncPoint",
    "event_PauseEmulation",
    "event_StopEmulation",
    "event_Throttled",
)
GAP_SUMMARY_FIELDS = frozenset(
    ("schema", "kind", "total", *GAP_BUCKET_FIELDS, *GAP_EVENT_FIELDS)
)
MODULE_IDENTITY_FIELDS = (
    "module_requested",
    "module_name",
    "module_base",
    "module_size",
    "module_timestamp",
    "module_checksum",
    "upstream_commit",
    "api_package",
)

# Exit codes (documented in the module docstring).
EXIT_OK = 0
EXIT_CONTROL_FAILURE = 1
EXIT_STRUCTURAL_ERROR = 2


class StructuralError(Exception):
    """A receipt or index is unusable; the message names file and line."""


def _parse_hex(value: object, context: str) -> int:
    if not isinstance(value, str):
        raise StructuralError(f"{context}: expected hex-string, got {value!r}")
    text = value.strip()
    try:
        # Receipts write hex with or without a leading "0x"; a bare "0x540411"
        # is hex, while "540411" alone is ambiguous and is rejected.
        return int(text, 16) if text.lower().startswith("0x") else int(text)
    except ValueError:
        raise StructuralError(f"{context}: not a hex number ({value!r})") from None


def _require(row: dict, key: str, context: str) -> object:
    if key not in row:
        raise StructuralError(f"{context}: missing required key {key!r}")
    return row[key]


def _parse_bool(row: dict, key: str, context: str) -> bool:
    value = _require(row, key, context)
    if not isinstance(value, bool):
        raise StructuralError(f"{context}: {key!r} must be boolean, got {value!r}")
    return value


def _parse_decimal_string(row: dict, key: str, context: str) -> int:
    value = _require(row, key, context)
    if not isinstance(value, str) or not value.isdecimal():
        raise StructuralError(
            f"{context}: {key!r} must be a non-negative decimal string, "
            f"got {value!r}"
        )
    return int(value)


def _validate_sha256(value: object, context: str) -> str:
    if (not isinstance(value, str) or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)):
        raise StructuralError(f"{context}: expected lowercase SHA-256, got {value!r}")
    return value


def _canonical_receipt_path(receipt: object, context: str) -> str:
    """Validate one per-trace receipt path canonically, host-independently.

    A receipt path stored in an index must be exactly what ``build`` emits for
    it: relative to the receipts root, forward-slash separated, fully
    normalized (no empty/`.`/`..` segments, no duplicate separators), never
    absolute in any host syntax (Windows drive ``C:/...``, drive-relative
    ``C:name``, UNC ``//host/share``, POSIX-rooted ``/...``), and always naming
    ``coverage.jsonl``.  Anything else means the index was re-bound after the
    fact -- its hashes were recomputed over a different location than the
    corpus it claims to describe -- so membership built on it would answer
    about bytes the index cannot name; this fails closed instead.
    """
    if not isinstance(receipt, str) or not receipt:
        raise StructuralError(f"{context}: invalid receipt path {receipt!r}")
    # Windows separators are rejected by name (never via os.sep) so the check
    # is identical on every host.
    if "\\" in receipt:
        raise StructuralError(
            f"{context}: noncanonical receipt path {receipt!r}: backslash "
            f"separator (forward slashes only)"
        )
    # A colon anywhere is Windows drive / drive-relative / alternate-stream
    # syntax and can never appear in a build-emitted relpath.
    if ":" in receipt:
        raise StructuralError(
            f"{context}: noncanonical receipt path {receipt!r}: colon "
            f"(drive/drive-relative/alternate-stream syntax)"
        )
    if receipt.startswith("/"):
        raise StructuralError(
            f"{context}: noncanonical receipt path {receipt!r}: rooted path"
        )
    segments = receipt.split("/")
    if any(segment in ("", ".", "..") for segment in segments):
        # Empty segments cover leading/trailing slashes and duplicate
        # separators; ".."/"." cover un-normalized relative escapes.
        raise StructuralError(
            f"{context}: noncanonical receipt path {receipt!r}: empty, '.', "
            f"or '..' segment"
        )
    if segments[-1] != RECEIPT_FILENAME:
        raise StructuralError(
            f"{context}: receipt path {receipt!r} does not name "
            f"{RECEIPT_FILENAME}"
        )
    return receipt


def _merge_intervals(intervals: list[tuple[int, int]]) -> list[list[int]]:
    """Merge touching/overlapping half-open intervals."""
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def _union_bytes(merged: list[list[int]]) -> int:
    return sum(end - start for start, end in merged)


class TraceCoverage:
    """Validated coverage for one trace receipt."""

    def __init__(self, name: str, relpath: str, sha256: str, size_bytes: int,
                 module_base: int, module_size: int, intervals:
                 list[list[int]], summary_covered_bytes: int,
                 counters_quarantined: bool = False,
                 replay_complete: bool = True,
                 stop_reason: str = "Process",
                 module_identity: dict[str, str] | None = None,
                 assertion_controls: tuple[tuple[str, int, bool], ...] = ()) -> None:
        self.name = name
        self.relpath = relpath
        self.sha256 = sha256
        self.size_bytes = size_bytes
        self.module_base = module_base
        self.module_size = module_size
        self.intervals = intervals
        self.summary_covered_bytes = summary_covered_bytes
        self.counters_quarantined = counters_quarantined
        self.replay_complete = replay_complete
        self.stop_reason = stop_reason
        self.module_identity = module_identity or {}
        self.assertion_controls = assertion_controls

    def covered_bytes(self) -> int:
        return sum(end - start for start, end in self.intervals)


def _read_receipt(path: str, relpath: str) -> TraceCoverage:
    """Parse and fully validate one coverage.jsonl.  Raises StructuralError."""
    name = os.path.basename(os.path.dirname(path)) or path
    digest = hashlib.sha256()
    metadata: dict | None = None
    summary: dict | None = None
    raw_intervals: list[tuple[int, int]] = []
    range_base_deltas: list[tuple[int, int]] = []
    seen_rows: set[str] = set()
    assertions: list[tuple[str, int, int, bool]] = []
    gap_summary: dict | None = None

    with open(path, "rb") as handle:
        for offset, raw in enumerate(handle, start=1):
            digest.update(raw)
            line = raw.decode("utf-8").strip()
            context = f"{relpath}:{offset}"
            if not line:
                raise StructuralError(f"{context}: blank line")
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise StructuralError(f"{context}: invalid JSON ({error})") from None
            if not isinstance(row, dict):
                raise StructuralError(f"{context}: row is not an object")
            schema = row.get("schema")
            if schema != SCHEMA_RECEIPT:
                raise StructuralError(
                    f"{context}: schema {schema!r} != {SCHEMA_RECEIPT!r}"
                )
            kind = row.get("kind")

            if kind == "metadata":
                if metadata is not None:
                    raise StructuralError(f"{context}: duplicate metadata row")
                metadata = row
            elif kind == "summary":
                if summary is not None:
                    raise StructuralError(f"{context}: duplicate summary row")
                summary = row
            elif kind == "range":
                index_value = _require(row, "index", context)
                if not isinstance(index_value, int) or isinstance(index_value, bool):
                    raise StructuralError(f"{context}: 'index' must be an integer")
                rva_start = _parse_hex(_require(row, "rva_start", context), context)
                rva_end = _parse_hex(
                    _require(row, "rva_end_exclusive", context), context
                )
                va_start = _parse_hex(_require(row, "va_start", context), context)
                va_end = _parse_hex(_require(row, "va_end_exclusive", context), context)
                if rva_end <= rva_start or va_end <= va_start:
                    raise StructuralError(
                        f"{context}: empty/inverted range [{va_start:#x}, {va_end:#x})"
                    )
                if va_start - rva_start != va_end - rva_end:
                    raise StructuralError(
                        f"{context}: VA/RVA width mismatch "
                        f"({va_start:#x}-{rva_start:#x} vs "
                        f"{va_end:#x}-{rva_end:#x})"
                    )
                byte_count = _require(row, "byte_count", context)
                if not isinstance(byte_count, int) or isinstance(byte_count, bool):
                    raise StructuralError(f"{context}: 'byte_count' must be integer")
                if byte_count != va_end - va_start:
                    raise StructuralError(
                        f"{context}: byte_count {byte_count} != range width "
                        f"{va_end - va_start}"
                    )
                key = json.dumps(row, sort_keys=True)
                if key in seen_rows:
                    raise StructuralError(f"{context}: duplicate range row")
                seen_rows.add(key)
                raw_intervals.append((va_start, va_end))
                range_base_deltas.append((offset, va_start - rva_start))
            elif kind == "assertion":
                expectation = _require(row, "expectation", context)
                if expectation not in ("hit", "miss"):
                    raise StructuralError(
                        f"{context}: unsupported assertion expectation "
                        f"{expectation!r}"
                    )
                va = _parse_hex(_require(row, "va", context), context)
                rva = _parse_hex(_require(row, "rva", context), context)
                observed = _parse_bool(row, "observed", context)
                passed = _parse_bool(row, "pass", context)
                if not passed:
                    raise StructuralError(
                        f"{context}: assertion did not pass (observed={observed})"
                    )
                assertions.append((expectation, va, rva, observed))
            elif kind == "gap-summary":
                if gap_summary is not None:
                    raise StructuralError(f"{context}: duplicate gap-summary row")
                if frozenset(row) != GAP_SUMMARY_FIELDS:
                    missing = sorted(GAP_SUMMARY_FIELDS - frozenset(row))
                    extra = sorted(frozenset(row) - GAP_SUMMARY_FIELDS)
                    raise StructuralError(
                        f"{context}: malformed gap-summary fields "
                        f"missing={missing} extra={extra}"
                    )
                gap_summary = row
            else:
                raise StructuralError(f"{context}: unknown kind {kind!r}")

    if metadata is None:
        raise StructuralError(f"{relpath}: no metadata row")
    if summary is None:
        raise StructuralError(f"{relpath}: no summary row")
    meta_context = f"{relpath}:metadata"
    module_identity: dict[str, str] = {}
    for key in MODULE_IDENTITY_FIELDS:
        value = _require(metadata, key, meta_context)
        if not isinstance(value, str) or not value:
            raise StructuralError(f"{meta_context}: {key!r} must be non-empty text")
        module_identity[key] = value
    base = _parse_hex(module_identity["module_base"], meta_context)
    module_size = _parse_hex(module_identity["module_size"], meta_context)
    if module_size <= 0:
        raise StructuralError(f"{meta_context}: module_size must be positive")
    # Parse the remaining PE/collector identity pins so malformed values do not
    # survive merely because two receipts repeat the same bad string.
    _parse_hex(module_identity["module_timestamp"], meta_context)
    _parse_hex(module_identity["module_checksum"], meta_context)
    if len(module_identity["upstream_commit"]) != 40 or any(
        character not in "0123456789abcdef"
        for character in module_identity["upstream_commit"]
    ):
        raise StructuralError(f"{meta_context}: malformed upstream_commit")
    trace_path = _require(metadata, "trace", meta_context)
    if not isinstance(trace_path, str) or not trace_path:
        raise StructuralError(f"{meta_context}: 'trace' must be non-empty text")
    for offset, delta in range_base_deltas:
        if delta != base:
            raise StructuralError(
                f"{relpath}:{offset}: VA/RVA delta {delta:#x} != metadata "
                f"module base {base:#x}"
            )
    if gap_summary is None:
        raise StructuralError(f"{relpath}: no gap-summary row")
    gap_context = f"{relpath}:gap-summary"
    gap_total = _parse_decimal_string(gap_summary, "total", gap_context)
    bucket_total = sum(
        _parse_decimal_string(gap_summary, field, gap_context)
        for field in GAP_BUCKET_FIELDS
    )
    event_total = sum(
        _parse_decimal_string(gap_summary, field, gap_context)
        for field in GAP_EVENT_FIELDS
    )
    if bucket_total != gap_total or event_total != gap_total:
        raise StructuralError(
            f"{gap_context}: contradictory accounting total={gap_total} "
            f"bucket_sum={bucket_total} event_sum={event_total}"
        )

    sorted_intervals = sorted(raw_intervals)
    for previous, current in zip(sorted_intervals, sorted_intervals[1:]):
        if current[0] < previous[1]:
            raise StructuralError(
                f"{relpath}: overlapping range rows "
                f"[{previous[0]:#x}, {previous[1]:#x}) and "
                f"[{current[0]:#x}, {current[1]:#x})"
            )
    intervals = _merge_intervals(raw_intervals)
    summary_context = f"{relpath}:summary"
    range_count = _require(summary, "range_count", summary_context)
    if not isinstance(range_count, int) or isinstance(range_count, bool):
        raise StructuralError(f"{summary_context}: range_count must be an integer")
    if range_count != len(raw_intervals):
        raise StructuralError(
            f"{summary_context}: range_count {range_count} != parsed range rows "
            f"{len(raw_intervals)}"
        )
    claimed = _parse_hex(
        _require(summary, "covered_bytes", summary_context), summary_context
    )
    actual = sum(end - start for start, end in intervals)
    if claimed != actual:
        raise StructuralError(
            f"{relpath}: summary covered_bytes {claimed} != merged range sum {actual}"
        )

    summary_context = f"{relpath}:summary"
    if not _parse_bool(summary, "marker_assertions_passed", summary_context):
        raise StructuralError(f"{relpath}: summary marker_assertions_passed is false")
    counters_quarantined = _parse_bool(
        summary, "counters_quarantined", summary_context
    )
    if counters_quarantined:
        # The collector refused to trust its step/callback counters (measured
        # cause: TTD replay accounting stopped advancing).  The range rows are
        # still individually validated below and the receipt's own marker
        # assertions still passed, so the receipt is admissible with its
        # quarantine recorded -- never silently rehabilitated.
        pass

    # replay_complete / collector_checks_passed are the collector's terminal
    # expectation: they are true only for run-to-completion traces and false
    # for the timer-stopped level-opening class whose replays end on a Thread
    # event (measured twice on L742; see local-lab/TTD-PILOT-2026-07-31.md and
    # Invoke-TtdExecCoverage.ps1's AliveAtStopExpected adjudication).  The
    # clause that does the real work here is marker_assertions_passed plus the
    # per-row checks above, so these two flags are recorded verbatim rather
    # than enforced -- but a receipt that claims completeness with a non-
    # Process stop is internally inconsistent and is rejected.
    stop_reason = _require(summary, "stop_reason", summary_context)
    if not isinstance(stop_reason, str) or not stop_reason:
        raise StructuralError(f"{relpath}: summary stop_reason must be a string")
    replay_complete = _parse_bool(summary, "replay_complete", summary_context)
    collector_checks_passed = _parse_bool(
        summary, "collector_checks_passed", summary_context
    )
    terminal_class = (replay_complete, collector_checks_passed, stop_reason)
    accepted_terminal_classes = {
        (True, True, "Process"),
        (False, False, "Thread"),
    }
    if terminal_class not in accepted_terminal_classes:
        raise StructuralError(
            f"{relpath}: unsupported terminal class "
            f"(replay_complete={replay_complete}, "
            f"collector_checks_passed={collector_checks_passed}, "
            f"stop_reason={stop_reason!r}); expected complete Process or "
            f"timer-stopped Thread"
        )

    # Domain bound: every covered byte must sit inside the module's mapped span.
    span_lo, span_hi = base, base + module_size
    for start, end in intervals:
        if start < span_lo or end > span_hi:
            raise StructuralError(
                f"{relpath}: range [{start:#x}, {end:#x}) outside module span "
                f"[{span_lo:#x}, {span_hi:#x})"
            )

    # Assertions are the receipt's required positive/negative collector
    # controls; bind the exact set and re-derive each result from the ranges.
    actual_assertions = tuple(
        (expectation, rva, observed)
        for expectation, _va, rva, observed in assertions
    )
    if tuple(control[0] for control in actual_assertions) != (
        REQUIRED_ASSERTION_EXPECTATIONS
    ):
        raise StructuralError(
            f"{relpath}: required assertion controls differ: expected one hit "
            f"then one miss, actual={actual_assertions!r}"
        )
    for expectation, va, rva, observed in assertions:
        if observed != (expectation == "hit"):
            raise StructuralError(
                f"{relpath}: assertion {expectation} observed={observed} "
                f"contradicts its expectation"
            )
        if va - rva != base:
            raise StructuralError(
                f"{relpath}: assertion VA/RVA delta {va - rva:#x} != module base "
                f"{base:#x}"
            )
        if va != base + rva:
            raise StructuralError(
                f"{relpath}: assertion {expectation} VA {va:#x} does not equal "
                f"base+rva {base + rva:#x}"
            )
        covered = any(start <= va < end for start, end in intervals)
        if covered != observed:
            raise StructuralError(
                f"{relpath}: assertion va={va:#x} claims observed={observed} but "
                f"ranges say covered={covered}"
            )

    return TraceCoverage(
        name=name,
        relpath=relpath,
        sha256=digest.hexdigest(),
        size_bytes=os.path.getsize(path),
        module_base=base,
        module_size=module_size,
        intervals=intervals,
        summary_covered_bytes=claimed,
        counters_quarantined=counters_quarantined,
        replay_complete=replay_complete,
        stop_reason=stop_reason,
        module_identity=module_identity,
        assertion_controls=actual_assertions,
    )


def collect_receipt_paths(root: str) -> list[str]:
    if not os.path.isdir(root):
        raise StructuralError(f"{root}: receipt root is not a readable directory")

    def refuse_walk_error(error: OSError) -> None:
        filename = getattr(error, "filename", None) or root
        raise StructuralError(f"{filename}: unreadable receipt subtree ({error})")

    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=refuse_walk_error):
        dirnames.sort()
        for filename in sorted(filenames):
            if filename == RECEIPT_FILENAME:
                found.append(os.path.join(dirpath, filename))
    if not found:
        raise StructuralError(f"{root}: no {RECEIPT_FILENAME} files found")
    return sorted(found)


def _index_content_sha256(payload: dict) -> str:
    """Hash every index field except the hash itself using canonical JSON."""
    bound = dict(payload)
    bound.pop("content_sha256", None)
    encoded = (
        json.dumps(bound, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_index(root: str) -> dict:
    traces = [
        _read_receipt(path, _canonical_receipt_path(
            os.path.relpath(path, root).replace(os.sep, "/"),
            f"{path}:receipt",
        ))
        for path in collect_receipt_paths(root)
    ]

    names = [trace.name for trace in traces]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise StructuralError(f"duplicate trace names under {root}: {duplicates}")
    first_identity = traces[0].module_identity
    divergent_identity_fields = [
        field for field in MODULE_IDENTITY_FIELDS
        if any(trace.module_identity.get(field) != first_identity.get(field)
               for trace in traces[1:])
    ]
    if divergent_identity_fields:
        raise StructuralError(
            f"divergent module identity across receipts: fields="
            f"{divergent_identity_fields}; one shared image/VA space cannot be "
            f"assumed"
        )
    base = _parse_hex(first_identity["module_base"], "module identity")
    first_controls = traces[0].assertion_controls
    if any(trace.assertion_controls != first_controls for trace in traces[1:]):
        raise StructuralError(
            "divergent required assertion controls across receipts"
        )

    receipt_set_sha256 = hashlib.sha256()
    for trace in traces:
        receipt_set_sha256.update(trace.relpath.encode("utf-8"))
        receipt_set_sha256.update(b"\n")
        receipt_set_sha256.update(trace.sha256.encode("ascii"))
        receipt_set_sha256.update(b"\n")

    union = _merge_intervals(
        [(start, end) for trace in traces for start, end in trace.intervals]
    )
    payload = {
        "schema": SCHEMA_INDEX,
        "built_from_root": os.path.abspath(root).replace(os.sep, "/"),
        "receipt_filename": RECEIPT_FILENAME,
        "receipt_count": len(traces),
        "module": first_identity,
        "module_base": hex(base),
        "required_assertions": [
            {"expectation": expectation, "rva": hex(rva),
             "observed": observed}
            for expectation, rva, observed in first_controls
        ],
        "receipt_set_sha256": receipt_set_sha256.hexdigest(),
        "union_covered_bytes": _union_bytes(union),
        "traces_with_quarantined_counters": [
            trace.name for trace in traces if trace.counters_quarantined
        ],
        "traces": [
            {
                "name": trace.name,
                "receipt": trace.relpath,
                "sha256": trace.sha256,
                "size_bytes": trace.size_bytes,
                "range_rows": len(trace.intervals),
                "covered_bytes": trace.covered_bytes(),
                "counters_quarantined": trace.counters_quarantined,
                "replay_complete": trace.replay_complete,
                "stop_reason": trace.stop_reason,
                "intervals": [
                    [hex(start), hex(end)] for start, end in trace.intervals
                ],
            }
            for trace in traces
        ],
    }
    payload["content_sha256"] = _index_content_sha256(payload)
    return payload


def dump_json(payload: dict) -> str:
    return json.dumps(payload, indent=1, sort_keys=True) + "\n"


def load_index(path: str) -> dict:
    """Load and deeply revalidate an index before any membership answer."""
    try:
        with open(path, "rb") as handle:
            payload = json.load(handle)
    except OSError as error:
        raise StructuralError(f"{path}: cannot read index ({error})") from None
    except json.JSONDecodeError as error:
        raise StructuralError(f"{path}: invalid JSON ({error})") from None
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA_INDEX:
        raise StructuralError(f"{path}: not a {SCHEMA_INDEX} document")

    context = f"{path}:index"
    content_hash = _validate_sha256(payload.get("content_sha256"), context)
    recomputed_content_hash = _index_content_sha256(payload)
    if content_hash != recomputed_content_hash:
        raise StructuralError(
            f"{context}: content_sha256 mismatch expected={content_hash} "
            f"actual={recomputed_content_hash}"
        )

    module = payload.get("module")
    if not isinstance(module, dict) or set(module) != set(MODULE_IDENTITY_FIELDS):
        raise StructuralError(f"{context}: malformed module identity object")
    for key in MODULE_IDENTITY_FIELDS:
        if not isinstance(module[key], str) or not module[key]:
            raise StructuralError(f"{context}: module.{key} must be non-empty text")
    module_base = _parse_hex(module["module_base"], f"{context}:module")
    module_size = _parse_hex(module["module_size"], f"{context}:module")
    _parse_hex(module["module_timestamp"], f"{context}:module")
    _parse_hex(module["module_checksum"], f"{context}:module")
    if module_size <= 0:
        raise StructuralError(f"{context}: module_size must be positive")
    if len(module["upstream_commit"]) != 40 or any(
        character not in "0123456789abcdef"
        for character in module["upstream_commit"]
    ):
        raise StructuralError(f"{context}: malformed upstream_commit")
    built_from_root = payload.get("built_from_root")
    if not isinstance(built_from_root, str) or not built_from_root:
        raise StructuralError(f"{context}: built_from_root must be non-empty text")
    if payload.get("module_base") != hex(module_base):
        raise StructuralError(
            f"{context}: module_base mirror disagrees with module identity"
        )

    assertion_rows = payload.get("required_assertions")
    if not isinstance(assertion_rows, list) or len(assertion_rows) != 2:
        raise StructuralError(f"{context}: required assertion controls differ")
    assertion_expectations: list[str] = []
    for assertion_index, assertion in enumerate(assertion_rows):
        assertion_context = f"{context}:required_assertions[{assertion_index}]"
        if not isinstance(assertion, dict) or set(assertion) != {
            "expectation", "rva", "observed"
        }:
            raise StructuralError(f"{assertion_context}: malformed control")
        expectation = assertion["expectation"]
        observed = assertion["observed"]
        if not isinstance(expectation, str) or not isinstance(observed, bool):
            raise StructuralError(f"{assertion_context}: malformed control values")
        _parse_hex(assertion["rva"], assertion_context)
        if observed != (expectation == "hit"):
            raise StructuralError(f"{assertion_context}: expectation/observed differ")
        assertion_expectations.append(expectation)
    if tuple(assertion_expectations) != REQUIRED_ASSERTION_EXPECTATIONS:
        raise StructuralError(f"{context}: required assertion controls differ")
    if payload.get("receipt_filename") != RECEIPT_FILENAME:
        raise StructuralError(f"{context}: unexpected receipt_filename")

    traces = payload.get("traces")
    receipt_count = payload.get("receipt_count")
    if not isinstance(traces, list) or not traces:
        raise StructuralError(f"{context}: index carries no traces")
    if (not isinstance(receipt_count, int) or isinstance(receipt_count, bool)
            or receipt_count != len(traces)):
        raise StructuralError(
            f"{context}: receipt_count {receipt_count!r} != trace rows "
            f"{len(traces)}"
        )

    names: list[str] = []
    receipts: list[str] = []
    quarantined: list[str] = []
    all_intervals: list[tuple[int, int]] = []
    receipt_manifest = hashlib.sha256()
    for trace_index, trace in enumerate(traces):
        trace_context = f"{context}:traces[{trace_index}]"
        if not isinstance(trace, dict):
            raise StructuralError(f"{trace_context}: trace row is not an object")
        name = trace.get("name")
        receipt = _canonical_receipt_path(
            trace.get("receipt"), f"{trace_context}:receipt"
        )
        if not isinstance(name, str) or not name:
            raise StructuralError(f"{trace_context}: invalid trace name")
        names.append(name)
        receipts.append(receipt)
        digest = _validate_sha256(trace.get("sha256"), trace_context)
        receipt_manifest.update(receipt.encode("utf-8"))
        receipt_manifest.update(b"\n")
        receipt_manifest.update(digest.encode("ascii"))
        receipt_manifest.update(b"\n")

        size_bytes = trace.get("size_bytes")
        range_rows = trace.get("range_rows")
        covered_bytes = trace.get("covered_bytes")
        for label, value, minimum in (
            ("size_bytes", size_bytes, 1),
            ("range_rows", range_rows, 0),
            ("covered_bytes", covered_bytes, 0),
        ):
            if (not isinstance(value, int) or isinstance(value, bool)
                    or value < minimum):
                raise StructuralError(
                    f"{trace_context}: {label} must be integer >= {minimum}"
                )
        counters_quarantined = trace.get("counters_quarantined")
        replay_complete = trace.get("replay_complete")
        stop_reason = trace.get("stop_reason")
        if not isinstance(counters_quarantined, bool):
            raise StructuralError(
                f"{trace_context}: counters_quarantined must be boolean"
            )
        if not isinstance(replay_complete, bool):
            raise StructuralError(f"{trace_context}: replay_complete must be boolean")
        if (replay_complete, stop_reason) not in (
            (True, "Process"),
            (False, "Thread"),
        ):
            raise StructuralError(f"{trace_context}: unsupported terminal class")
        if counters_quarantined:
            quarantined.append(name)

        intervals = trace.get("intervals")
        if not isinstance(intervals, list) or len(intervals) != range_rows:
            raise StructuralError(
                f"{trace_context}: range_rows {range_rows} != interval rows "
                f"{len(intervals) if isinstance(intervals, list) else 'non-list'}"
            )
        parsed_intervals: list[tuple[int, int]] = []
        previous_end: int | None = None
        for interval_index, interval in enumerate(intervals):
            interval_context = f"{trace_context}:intervals[{interval_index}]"
            if not isinstance(interval, list) or len(interval) != 2:
                raise StructuralError(f"{interval_context}: expected [start, end]")
            start = _parse_hex(interval[0], interval_context)
            end = _parse_hex(interval[1], interval_context)
            if end <= start:
                raise StructuralError(f"{interval_context}: empty/inverted interval")
            if start < module_base or end > module_base + module_size:
                raise StructuralError(f"{interval_context}: out-of-domain interval")
            if previous_end is not None and start < previous_end:
                raise StructuralError(
                    f"{interval_context}: intervals are unsorted or overlapping"
                )
            previous_end = end
            parsed_intervals.append((start, end))
        parsed_covered_bytes = sum(end - start for start, end in parsed_intervals)
        if parsed_covered_bytes != covered_bytes:
            raise StructuralError(
                f"{trace_context}: covered_bytes {covered_bytes} != interval sum "
                f"{parsed_covered_bytes}"
            )
        all_intervals.extend(parsed_intervals)

    if len(names) != len(set(names)):
        raise StructuralError(f"{context}: duplicate trace names")
    if len(receipts) != len(set(receipts)):
        raise StructuralError(f"{context}: duplicate receipt paths")
    if receipts != sorted(receipts):
        raise StructuralError(f"{context}: receipt rows are not sorted")
    if payload.get("traces_with_quarantined_counters") != quarantined:
        raise StructuralError(f"{context}: quarantine summary disagrees with trace rows")

    expected_receipt_hash = _validate_sha256(
        payload.get("receipt_set_sha256"), context
    )
    actual_receipt_hash = receipt_manifest.hexdigest()
    if expected_receipt_hash != actual_receipt_hash:
        raise StructuralError(
            f"{context}: receipt_set_sha256 mismatch expected="
            f"{expected_receipt_hash} actual={actual_receipt_hash}"
        )
    union_covered_bytes = payload.get("union_covered_bytes")
    actual_union = _union_bytes(_merge_intervals(all_intervals))
    if (not isinstance(union_covered_bytes, int)
            or isinstance(union_covered_bytes, bool)
            or union_covered_bytes != actual_union):
        raise StructuralError(
            f"{context}: union_covered_bytes {union_covered_bytes!r} != "
            f"interval union {actual_union}"
        )
    return payload


def _parse_address(token: str) -> int:
    try:
        return int(token, 16)
    except ValueError:
        raise StructuralError(f"not a hex address: {token!r}") from None


def _split_addresses(text: str | None) -> list[int]:
    return [_parse_address(token) for token in text.split(",") if token]


def membership_for_address(index: dict, address: int) -> list[str]:
    """Sorted names of traces whose coverage contains `address`."""
    members: list[str] = []
    for trace in index["traces"]:
        for start_text, end_text in trace["intervals"]:
            start = _parse_address(start_text)
            end = _parse_address(end_text)
            if start <= address < end:
                members.append(trace["name"])
                break
    members.sort()
    return members


def run_query(index_path: str, addresses: list[str],
              expect_hit: list[str], expect_miss: list[str]) -> dict:
    """Query a built index.  Addresses are hex tokens (e.g. ``0x407060``)."""
    index = load_index(index_path)
    canonical_input = {
        "addresses": addresses,
        "expect_hit": expect_hit,
        "expect_miss": expect_miss,
    }
    input_bytes = (
        json.dumps(canonical_input, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    query_input_sha256 = hashlib.sha256(input_bytes).hexdigest()
    entries = []
    for address in addresses:
        members = membership_for_address(index, _parse_address(address))
        entries.append({
            "address": address,
            "hit_count": len(members),
            "traces": members,
        })
    by_address = {entry["address"]: entry["traces"] for entry in entries}

    def control_entry(address: str) -> tuple[list[str], bool]:
        traces = by_address.get(address)
        if traces is None:
            traces = membership_for_address(index, _parse_address(address))
        return traces, bool(traces)

    controls = []
    ok = True
    for address in expect_hit:
        traces, present = control_entry(address)
        passed = present
        ok = ok and passed
        controls.append({
            "control": "must_hit",
            "address": address,
            "hit_count": len(traces),
            "pass": passed,
        })
    for address in expect_miss:
        traces, present = control_entry(address)
        passed = not present
        ok = ok and passed
        controls.append({
            "control": "must_miss",
            "address": address,
            "hit_count": len(traces),
            "pass": passed,
        })

    return {
        "schema": SCHEMA_QUERY,
        "index": index_path,
        "index_content_sha256": index.get("content_sha256"),
        "index_receipt_set_sha256": index.get("receipt_set_sha256"),
        "index_receipt_count": index.get("receipt_count"),
        "query_input": canonical_input,
        "query_input_sha256": query_input_sha256,
        "addresses": entries,
        "controls": controls,
        "pass": ok,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline index + cross-trace query over TTD exec-coverage "
        "receipts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="build the index")
    build_parser.add_argument("--root", required=True)
    build_parser.add_argument("--out")
    build_parser.add_argument("--stdout", action="store_true",
                              help="print the index instead of writing a file")

    query_parser = subparsers.add_parser("query", help="query the index")
    query_parser.add_argument("--index", required=True)
    query_parser.add_argument("--va", default="",
                              help="comma-separated absolute VAs")
    query_parser.add_argument("--rva", default="",
                              help="comma-separated RVAs against the module base")
    query_parser.add_argument("--expect-hit", default="")
    query_parser.add_argument("--expect-miss", default="")

    arguments = parser.parse_args(argv)

    try:
        if arguments.command == "build":
            payload = build_index(arguments.root)
            text = dump_json(payload)
            if arguments.out:
                parent = os.path.dirname(os.path.abspath(arguments.out))
                os.makedirs(parent, exist_ok=True)
                with open(arguments.out, "w", encoding="utf-8",
                          newline="\n") as handle:
                    handle.write(text)
            if arguments.stdout or not arguments.out:
                sys.stdout.write(text)
            return EXIT_OK

        tokens = [hex(address) for address in _split_addresses(arguments.va)]
        if _split_addresses(arguments.rva):
            base = _parse_address(str(load_index(arguments.index)["module_base"]))
            tokens += [
                hex(address + base) for address in _split_addresses(arguments.rva)
            ]
        payload = run_query(
            arguments.index,
            tokens,
            [hex(address) for address in _split_addresses(arguments.expect_hit)],
            [hex(address) for address in _split_addresses(arguments.expect_miss)],
        )
        sys.stdout.write(dump_json(payload))
        return EXIT_OK if payload["pass"] else EXIT_CONTROL_FAILURE
    except StructuralError as error:
        print(f"FAIL CLOSED: {error}", file=sys.stderr)
        return EXIT_STRUCTURAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
