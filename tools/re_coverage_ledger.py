# SPDX-License-Identifier: GPL-3.0-or-later
"""Function-granularity coverage / discovery ledger for the BEA.exe `.text` section.

WHAT THIS IS
------------
A re-runnable scoreboard for the reverse-engineering programme. It answers, for
every function in the current Ghidra inventory and for every byte of `.text`:

  OBSERVED   -- bytes proven to have executed, unioned over every TTD coverage
                index handed to it. Positive execution only; a miss is
                NON-OBSERVATION, never absence.
  NAMED      -- does the symbol carry human meaning, or is it `FUN_*`, a vtable
                slot index, or a name that is just a class plus its own address.
  UNDERSTOOD -- is there a behavioural claim behind it: a script-native registry
                binding that also executed, or an exact entry-address citation
                in the tracked evidence corpus.
  DARK       -- zero observed bytes.

Then it ranks the dark regions by size and by adjacency to observed code,
because a dark body called from an observed one is far cheaper to identify than
an island, and it estimates how much of the dark mass is reachable by in-game
probing at all.

HONESTY CONTRACT (do not weaken these)
--------------------------------------
1. Every number is printed with its denominator and the date/hash of the input
   it came from. `build` refuses to run against a specimen whose sha256 is not
   the pristine baseline unless `--allow-specimen-mismatch` is passed.
2. The historical 79.8268% `.text` figure is a DATED 6,411-body measurement.
   This tool never reproduces, rolls forward, or approximates it. When supplied
   an authenticated `ExportParityLabGraph` READY receipt it uses exact fragmented
   bodies and verifies every fragment against the specimen. Without that input,
   it falls back to a 7,555-body *hull* union explicitly labelled an UPPER BOUND.
3. Where a number cannot be computed from the inputs present, the field is the
   string "UNKNOWN". It is never estimated into a plausible-looking value.
4. DARK is exact (a real body is a subset of its hull, so a hull with zero
   observed bytes had a body with zero observed bytes). COVERED is conservative
   (it demands 100% of the hull, which over-covers). Both asymmetries are
   stated in the output.
5. A coverage HIT proves bytes at an address executed. It does not prove the
   name attached to that address is correct. `UNDERSTOOD` is a proxy built from
   citations and registry bindings; citation is not correctness.
6. No step/instruction counter is read from any receipt (TTD engine defect,
   task #149). Byte ranges only.
7. The static call graph is a byte-pattern heuristic (`E8`/`E9` rel32 landing
   exactly on a known entry, plus dword-aligned absolute VAs), not a
   disassembly. It is a superset with a measurable false-positive floor, and
   the report prints that floor.

USAGE
-----
  py -3 tools/re_coverage_ledger.py build  --out DIR [options]
  py -3 tools/re_coverage_ledger.py report --snapshot DIR [--top N]
  py -3 tools/re_coverage_ledger.py delta  --before DIR --after DIR [--top N]

`build` writes a self-describing snapshot directory:
  ledger-summary.json    headline numbers, denominators, input manifest
  ledger-functions.tsv   one row per function in the inventory
  ledger-dark.tsv        dark regions ranked
  ledger-gaps.tsv        executed `.text` bytes claimed by no function
  ledger-native-handlers.tsv  finite 144-row Mission native accounting
  ledger-families.tsv    dark bytes aggregated by class-name family

Re-run `build` after every probe, then `delta` the two snapshots to see what the
probe actually bought.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "bea.re.coverage-ledger.v2"
PARITY_GRAPH_RECEIPT_SCHEMA = "bea-ghidra-parity-graph-receipt.v2"
PARITY_GRAPH_TSV_SCHEMA = "bea-ghidra-parity-graph.v2"
NATIVE_CANARY_SCHEMA = "bea.re.native-execution-canary.v1"
SNAPSHOT_READY_SCHEMA = "bea.re.coverage-ledger-ready.v1"
SNAPSHOT_FILES = (
    "ledger-summary.json",
    "ledger-functions.tsv",
    "ledger-dark.tsv",
    "ledger-gaps.tsv",
    "ledger-unmapped.tsv",
    "ledger-native-handlers.tsv",
    "ledger-families.tsv",
)

REPO = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Defaults. Every one of these is overridable on the command line; they are the
# measured locations as of 2026-08-02 and are recorded into the snapshot.
# ---------------------------------------------------------------------------

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

DEFAULT_SPECIMEN = REPO / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
DEFAULT_NAMES = REPO / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv"
DEFAULT_NATIVES = REPO / "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv"
DEFAULT_PARITY_GRAPH = REPO / "local-lab/parity-lab-static-v5-2026-07-29/parity-graph.ready.json"

DEFAULT_COVERAGE_ROOTS = [
    Path("G:/bea-ttd/q-campaign-coverage-v1"),
    REPO / "local-lab/startup-to-main-menu-20260729-173124-exec-v1",
    REPO / "local-lab/frontend-manual-02-exec-par-v2",
    REPO / "local-lab/options-open-manual-01-exec-v1",
]

DEFAULT_EVIDENCE_ROOTS = [
    REPO / "reverse-engineering",
    REPO / "rebuild",
]

DEFAULT_EVIDENCE_GLOBS = ["*.md"]  # applied at repo root as well

EVIDENCE_SKIP_DIR_PARTS = {".rep", "BEA.rep", "ghidra", "node_modules", ".git"}
EVIDENCE_EXTS = {".md", ".json", ".tsv", ".txt"}
EVIDENCE_MAX_BYTES = 8 * 1024 * 1024

# A file that mentions this many distinct `.text` addresses is an inventory
# dump, not a set of claims. Counting it would make every address look "cited"
# -- the name table alone names all 7,555. Such files are excluded and named in
# the snapshot so the exclusion is auditable rather than silent.
EVIDENCE_INVENTORY_THRESHOLD = 2000

# Bulk review corpora: every function in a sweep gets an entry whether or not
# anyone learned anything about it. Citations from these paths are counted
# separately from targeted ones, because "it was in the 6,411-function fullpass"
# is a much weaker signal than "somebody wrote a claim about this address".
BULK_REVIEW_MARKERS = ("ghidra-fullpass-findings", "ghidra-reviewed-correction-plan", "name-grading-ledger")

# Above this, a bodyMin..bodyMax hull is very unlikely to be one contiguous
# function body and the byte figure should not be trusted as a body size.
HULL_SUSPECT_BYTES = 8192


class LedgerInputError(ValueError):
    """An evidence input failed an identity, shape, or consistency check."""


# ---------------------------------------------------------------------------
# Interval algebra over half-open RVA ranges.
# ---------------------------------------------------------------------------


def merge(ranges):
    """Merge a list of (start, end_exclusive) into sorted disjoint runs."""
    out = []
    for a, b in sorted(ranges):
        if b <= a:
            continue
        if out and a <= out[-1][1]:
            if b > out[-1][1]:
                out[-1][1] = b
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def clip(ranges, lo, hi):
    return [(max(a, lo), min(b, hi)) for a, b in ranges if min(b, hi) > max(a, lo)]


def total(ranges):
    return sum(b - a for a, b in ranges)


def subtract(a_ranges, b_ranges):
    """A minus B. Both must already be merged and sorted."""
    out = []
    j = 0
    for a, b in a_ranges:
        cur = a
        while j > 0 and b_ranges[j - 1][1] > cur:
            j -= 1
        k = j
        while k < len(b_ranges) and b_ranges[k][0] < b:
            ba, bb = b_ranges[k]
            if bb <= cur:
                k += 1
                continue
            if ba > cur:
                out.append((cur, min(ba, b)))
            cur = max(cur, bb)
            if cur >= b:
                break
            k += 1
        j = max(0, k)
        if cur < b:
            out.append((cur, b))
    return [(a, b) for a, b in out if b > a]


class CoverageIndex:
    """Merged coverage runs plus an O(log n) 'how many bytes of [lo,hi) ran' query."""

    def __init__(self, ranges):
        self.runs = merge(ranges)
        self.starts = [a for a, _ in self.runs]
        self.prefix = [0]
        for a, b in self.runs:
            self.prefix.append(self.prefix[-1] + (b - a))

    def total(self):
        return self.prefix[-1]

    def covered_in(self, lo, hi):
        """Bytes of [lo, hi) that appear in the index."""
        if hi <= lo or not self.runs:
            return 0

        def upto(x):
            # bytes covered strictly below x
            i = bisect_right(self.starts, x) - 1
            if i < 0:
                return 0
            acc = self.prefix[i]
            a, b = self.runs[i]
            if x > a:
                acc += min(x, b) - a
            return acc

        return upto(hi) - upto(lo)


# ---------------------------------------------------------------------------
# Inputs.
# ---------------------------------------------------------------------------


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def file_stamp(path: Path) -> dict:
    st = path.stat()
    return {
        "path": str(path),
        "bytes": st.st_size,
        "sha256": sha256_of(path),
        "lastWriteUtc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
    }


def verify_snapshot(snapshot: Path) -> dict:
    """Verify the atomic READY receipt and every published ledger byte."""
    receipt_path = snapshot / "ledger.ready.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerInputError(f"cannot read coverage READY receipt: {exc}") from exc
    if receipt.get("schema") != SNAPSHOT_READY_SCHEMA:
        raise LedgerInputError(
            f"unsupported coverage READY schema: {receipt.get('schema')!r}"
        )
    files = receipt.get("files")
    if not isinstance(files, dict) or set(files) != set(SNAPSHOT_FILES):
        raise LedgerInputError(
            "coverage READY receipt does not name the exact published ledger set"
        )
    for name in SNAPSHOT_FILES:
        path = snapshot / name
        expected = files.get(name)
        if not path.is_file() or not isinstance(expected, dict):
            raise LedgerInputError(f"coverage output missing from disk/receipt: {name}")
        if expected.get("path") != name:
            raise LedgerInputError(
                f"coverage READY receipt contains a non-portable output path: {name}"
            )
        actual = file_stamp(path)
        if (
            actual["bytes"] != expected.get("bytes")
            or actual["sha256"] != expected.get("sha256")
        ):
            raise LedgerInputError(
                f"coverage output disagrees with READY receipt: {name}"
            )
    return receipt


def function_population_date(path: Path) -> str:
    """Return only a date the input itself authorises us to claim.

    Ghidra's full-inventory TSV has no embedded export timestamp.  Filesystem
    mtime is recorded separately by `file_stamp`; it is not silently promoted
    to an evidence date.  The canonical historical table is the one exception:
    its dated filename is its published identity.
    """
    try:
        canonical = path.resolve() == DEFAULT_NAMES.resolve()
    except OSError:
        canonical = False
    if canonical:
        return "2026-07-27 (canonical name-table export date encoded in its filename)"
    return "UNKNOWN (supplied inventory has no embedded export timestamp; lastWriteUtc is filesystem metadata only)"


def _canonical_json_sha256(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def coverage_set_sha256(sources: list[dict]) -> str:
    """Content identity for one complete coverage input set.

    Paths and source labels are deliberately excluded: the same byte-identical
    indexes remain the same evidence set after a move. Duplicate inputs remain
    visible because this hashes a sorted list rather than a set.
    """

    return _canonical_json_sha256(sorted(row["coverageSha256"] for row in sources))


class Specimen:
    """Read-only PE reader over the pristine baseline. Writes nothing, ever."""

    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        if self.data[:2] != b"MZ":
            raise ValueError(f"{path}: not a PE image")
        pe = struct.unpack_from("<I", self.data, 0x3C)[0]
        if self.data[pe : pe + 4] != b"PE\0\0":
            raise ValueError(f"{path}: bad PE signature")
        n_sections = struct.unpack_from("<H", self.data, pe + 6)[0]
        opt_size = struct.unpack_from("<H", self.data, pe + 20)[0]
        self.image_base = struct.unpack_from("<I", self.data, pe + 24 + 28)[0]
        self.timestamp = struct.unpack_from("<I", self.data, pe + 8)[0]
        sec = pe + 24 + opt_size
        self.sections = []
        for i in range(n_sections):
            off = sec + i * 40
            name = self.data[off : off + 8].rstrip(b"\0").decode("ascii", "replace")
            vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", self.data, off + 8)
            self.sections.append(
                {"name": name, "rva": vaddr, "vsize": vsize, "rawptr": rawptr, "rawsize": rawsize}
            )
        text = next(s for s in self.sections if s["name"] == ".text")
        self.text_lo = text["rva"]
        self.text_hi = text["rva"] + text["vsize"]  # half-open RVA
        self.text_vsize = text["vsize"]
        self.text_rawptr = text["rawptr"]
        self.text_rawsize = text["rawsize"]

    def section_of_rva(self, rva):
        for s in self.sections:
            if s["rva"] <= rva < s["rva"] + max(s["vsize"], s["rawsize"]):
                return s["name"]
        return None

    def bytes_at_rva(self, rva: int, size: int) -> bytes:
        """Read initialized image bytes for one range without RVA=file-offset guesses."""

        if size < 0:
            raise LedgerInputError(f"negative specimen read size: {size}")
        for section in self.sections:
            start = section["rva"]
            raw_end = start + section["rawsize"]
            if start <= rva and rva + size <= raw_end:
                offset = section["rawptr"] + (rva - start)
                return self.data[offset : offset + size]
        raise LedgerInputError(
            f"RVA range [0x{rva:x},0x{rva + size:x}) is not wholly backed by one PE section"
        )


def _read_tsv_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            item = line[1:].strip()
            if "=" in item:
                key, value = item.split("=", 1)
                metadata[key.strip()] = value.strip()
    return metadata


def _parse_hex(value: object, label: str) -> int:
    try:
        return int(str(value), 16)
    except (TypeError, ValueError) as exc:
        raise LedgerInputError(f"{label} is not a hexadecimal integer: {value!r}") from exc


def load_exact_body_graph(receipt_path: Path, spec: Specimen, name_rows: list[dict]) -> dict:
    """Load and fully authenticate an ExportParityLabGraph body-fragment export."""

    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerInputError(f"cannot read parity-graph receipt {receipt_path}: {exc}") from exc

    if receipt.get("schemaVersion") != PARITY_GRAPH_RECEIPT_SCHEMA:
        raise LedgerInputError(
            f"unsupported parity-graph receipt schema: {receipt.get('schemaVersion')!r}"
        )

    program = receipt.get("program")
    body_record = receipt.get("bodyRanges")
    if not isinstance(program, dict) or not isinstance(body_record, dict):
        raise LedgerInputError("parity-graph receipt is missing program/bodyRanges objects")

    expected_md5 = str(program.get("executableMd5", "")).lower()
    specimen_md5 = hashlib.md5(spec.data, usedforsecurity=False).hexdigest()
    if expected_md5 != specimen_md5:
        raise LedgerInputError(
            "parity-graph executable MD5 does not match the supplied specimen: "
            f"receipt={expected_md5 or '<missing>'} specimen={specimen_md5}"
        )
    if _parse_hex(program.get("imageBase"), "parity-graph imageBase") != spec.image_base:
        raise LedgerInputError("parity-graph image base does not match the supplied specimen")

    body_name = body_record.get("file")
    if not isinstance(body_name, str) or not body_name or Path(body_name).name != body_name:
        raise LedgerInputError("parity-graph bodyRanges.file must be one sibling filename")
    body_path = receipt_path.parent / body_name
    if not body_path.is_file():
        raise LedgerInputError(f"parity-graph body-range file is missing: {body_path}")
    body_stamp = file_stamp(body_path)
    if body_stamp["bytes"] != body_record.get("bytes"):
        raise LedgerInputError("parity-graph body-range byte count disagrees with its READY receipt")
    if body_stamp["sha256"] != str(body_record.get("sha256", "")).lower():
        raise LedgerInputError("parity-graph body-range SHA-256 disagrees with its READY receipt")

    metadata = _read_tsv_metadata(body_path)
    if metadata.get("schema") != PARITY_GRAPH_TSV_SCHEMA:
        raise LedgerInputError(f"unsupported body-range TSV schema: {metadata.get('schema')!r}")
    if metadata.get("executableMd5", "").lower() != specimen_md5:
        raise LedgerInputError("body-range TSV executable MD5 does not match the supplied specimen")
    if _parse_hex(metadata.get("imageBase"), "body-range imageBase") != spec.image_base:
        raise LedgerInputError("body-range TSV image base does not match the supplied specimen")

    by_entry: dict[int, list[tuple[int, int]]] = defaultdict(list)
    ordinals: dict[int, set[int]] = defaultdict(set)
    export_names: dict[int, str] = {}
    all_ranges: list[tuple[int, int, int]] = []
    row_count = 0
    with open(body_path, encoding="utf-8") as fh:
        header = None
        for raw in fh:
            if raw.startswith("#") or not raw.strip():
                continue
            fields = raw.rstrip("\n").split("\t")
            if header is None:
                header = fields
                required = {
                    "functionAddress", "functionName", "rangeOrdinal", "rangeMin",
                    "rangeMax", "rangeEndExclusive", "rangeBytes", "rangeSha256",
                }
                if not required.issubset(header):
                    raise LedgerInputError("body-range TSV is missing required columns")
                continue
            row_count += 1
            row = dict(zip(header, fields))
            entry = _parse_hex(row.get("functionAddress"), "functionAddress")
            lo_va = _parse_hex(row.get("rangeMin"), "rangeMin")
            max_va = _parse_hex(row.get("rangeMax"), "rangeMax")
            hi_va = _parse_hex(row.get("rangeEndExclusive"), "rangeEndExclusive")
            try:
                size = int(row.get("rangeBytes", ""))
                ordinal = int(row.get("rangeOrdinal", ""))
            except ValueError as exc:
                raise LedgerInputError("body-range ordinal/size is not an integer") from exc
            if size <= 0 or hi_va - lo_va != size or max_va + 1 != hi_va:
                raise LedgerInputError(
                    f"inconsistent body range at 0x{entry:08x}: "
                    f"[0x{lo_va:x},0x{hi_va:x}) size={size} max=0x{max_va:x}"
                )
            if ordinal <= 0 or ordinal in ordinals[entry]:
                raise LedgerInputError(f"duplicate/invalid range ordinal {ordinal} at 0x{entry:08x}")
            ordinals[entry].add(ordinal)

            lo = lo_va - spec.image_base
            hi = hi_va - spec.image_base
            if not (spec.text_lo <= lo < hi <= spec.text_hi):
                raise LedgerInputError(
                    f"body range [0x{lo_va:x},0x{hi_va:x}) is outside the specimen .text section"
                )
            actual_hash = hashlib.sha256(spec.bytes_at_rva(lo, size)).hexdigest()
            if actual_hash != str(row.get("rangeSha256", "")).lower():
                raise LedgerInputError(
                    f"body-range bytes do not match the specimen at [0x{lo_va:x},0x{hi_va:x})"
                )
            by_entry[entry].append((lo, hi))
            export_names[entry] = row.get("functionName", "")
            all_ranges.append((lo, hi, entry))

    expected_rows = body_record.get("rangeCount")
    expected_functions = body_record.get("functionCount")
    if row_count != expected_rows or len(by_entry) != expected_functions:
        raise LedgerInputError(
            "parity-graph row/function counts disagree with its READY receipt: "
            f"rows={row_count}/{expected_rows}, functions={len(by_entry)}/{expected_functions}"
        )

    name_entries = {row["va"] for row in name_rows}
    body_entries = set(by_entry)
    if body_entries != name_entries:
        missing = sorted(name_entries - body_entries)
        extra = sorted(body_entries - name_entries)
        raise LedgerInputError(
            "parity-graph and name-table function populations differ: "
            f"missing={len(missing)} extra={len(extra)}"
        )

    for entry, ranges in by_entry.items():
        expected_ordinals = set(range(1, len(ranges) + 1))
        if ordinals[entry] != expected_ordinals:
            raise LedgerInputError(f"non-contiguous range ordinals at 0x{entry:08x}")
        if not any(lo <= entry - spec.image_base < hi for lo, hi in ranges):
            raise LedgerInputError(f"function entry 0x{entry:08x} is outside its exported body")
        ranges.sort()

    previous = None
    for lo, hi, entry in sorted(all_ranges):
        if previous is not None and lo < previous[1]:
            raise LedgerInputError(
                "overlapping exact function bodies: "
                f"0x{spec.image_base + lo:08x} begins before "
                f"0x{spec.image_base + previous[1]:08x}"
            )
        previous = (lo, hi, entry)

    name_by_entry = {row["va"]: row["name"] for row in name_rows}
    union = merge((lo, hi) for lo, hi, _entry in all_ranges)
    return {
        "byEntryVa": dict(by_entry),
        "union": union,
        "unionBytes": total(union),
        "rangeCount": row_count,
        "functionCount": len(by_entry),
        "nameMismatchCount": sum(
            1 for entry, exported in export_names.items()
            if name_by_entry.get(entry) != exported
        ),
        "receipt": file_stamp(receipt_path),
        "bodyRanges": body_stamp,
        "program": program,
    }


def native_canary_result(
    canary_path: Path | None,
    coverage_digest: str,
    native_stamp: dict | None,
    observed: int,
    observed_uncontradicted: int,
) -> dict:
    """Validate an optional native-hit canary bound to exact input manifests."""

    base = {
        "schema": NATIVE_CANARY_SCHEMA,
        "status": "NOT_CONFIGURED",
        "coverageSetSha256": coverage_digest,
        "note": (
            "No count expectation applies to an arbitrary coverage set. Supply --native-canary "
            "with a manifest bound to this coverage-set and registry SHA-256 to enforce one."
        ),
    }
    if canary_path is None:
        return base
    try:
        canary = json.loads(canary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerInputError(f"cannot read native canary {canary_path}: {exc}") from exc
    if canary.get("schema") != NATIVE_CANARY_SCHEMA:
        raise LedgerInputError(f"unsupported native canary schema: {canary.get('schema')!r}")
    if canary.get("coverageSetSha256") != coverage_digest:
        raise LedgerInputError("native canary is bound to a different coverage input set")
    if native_stamp is None or canary.get("nativeRegistrySha256") != native_stamp.get("sha256"):
        raise LedgerInputError("native canary is bound to a different native registry")
    expected = canary.get("expected")
    if not isinstance(expected, dict):
        raise LedgerInputError("native canary is missing its expected object")
    wanted = {
        "handlerFirstByteObserved": observed,
        "handlerFirstByteObservedExcludingContradicted": observed_uncontradicted,
    }
    mismatches = {
        key: {"expected": expected.get(key), "actual": actual}
        for key, actual in wanted.items()
        if expected.get(key) != actual
    }
    if mismatches:
        raise LedgerInputError(f"native canary failed: {mismatches}")
    return {
        **base,
        "status": "PASS",
        "manifest": file_stamp(canary_path),
        "nativeRegistrySha256": native_stamp["sha256"],
        "expected": expected,
        "note": "Expected native-hit counts matched the exact coverage and registry manifests.",
    }


# --- Ghidra name table ------------------------------------------------------

RE_FUN = re.compile(r"^FUN_[0-9a-fA-F]{8}$")
RE_VFUNCSLOT = re.compile(r"^VFuncSlot_\d+_[0-9a-fA-F]{8}$")
RE_ADDRSUFFIX = re.compile(r"^.*_[0-9a-fA-F]{8}$")
RE_UNWIND = re.compile(r"^Unwind@")
RE_THUNK = re.compile(r"^thunk_|^_?thunk")


def name_class(name: str) -> str:
    """Coarse naming tier. NAMED means a human wrote meaning into the symbol."""
    if RE_UNWIND.match(name):
        return "UNWIND"  # MSVC EH funclet; compiler-generated, not human-namable
    if RE_FUN.match(name):
        return "FUN"  # Ghidra default: no name at all
    if RE_VFUNCSLOT.match(name):
        return "VFUNC_SLOT"  # known to be a vtable slot, nothing more
    if RE_THUNK.match(name):
        return "THUNK"
    if name.startswith("SharedVFunc__"):
        return "SHARED_STUB"
    if RE_ADDRSUFFIX.match(name):
        return "ADDR_SUFFIXED"  # class known, semantics not
    return "NAMED"


HUMAN_NAMED_CLASSES = {"NAMED"}
UNNAMED_CLASSES = {"FUN", "VFUNC_SLOT"}


def evidence_proxy_tier(name_class_value: str, focused_citations: int, citations: int) -> str:
    """Return only the weak evidence grade this ledger can establish.

    Runtime entry coverage and a registry binding are deliberately absent from
    this decision. They establish execution and a candidate identity, not a
    reviewed receiver/input/write/return contract.
    """
    if focused_citations > 0:
        return "U2_ADDRESS_CITED"
    if citations > 0:
        return "U1b_BULK_REVIEWED"
    if name_class_value in HUMAN_NAMED_CLASSES:
        return "U1_NAMED_ONLY"
    return "U0_NONE"


def load_name_table(path: Path):
    rows = []
    header_lines = []
    columns = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                header_lines.append(line.rstrip("\n"))
                continue
            if not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if columns is None:
                columns = {name: index for index, name in enumerate(fields)}
                required = {"address", "name", "bodyMin", "bodyMax"}
                if not required.issubset(columns):
                    raise LedgerInputError(
                        f"name table is missing required columns: {sorted(required - set(columns))}"
                    )
                continue
            if len(fields) <= max(columns[column] for column in required):
                continue
            try:
                addr = int(fields[columns["address"]], 16)
                lo = int(fields[columns["bodyMin"]], 16)
                hi = int(fields[columns["bodyMax"]], 16)
            except ValueError:
                continue
            rows.append(
                {
                    "va": addr,
                    "name": fields[columns["name"]],
                    "hullLoVa": lo,
                    "hullHiVa": hi,
                }
            )
    if columns is None:
        raise LedgerInputError(f"name table has no header: {path}")
    rows.sort(key=lambda r: r["va"])
    return rows, header_lines


# --- MissionScript native registry -----------------------------------------


def load_natives(path: Path):
    """handler VA -> {shippedName, ghidraName, status}. Absent file is tolerated."""
    if not path or not path.exists():
        return {}, None
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) < 6 or f[0] == "index":
                continue
            try:
                index = int(f[0])
                record = int(f[1], 16)
                handler = int(f[2], 16)
            except ValueError:
                continue
            if handler in out:
                raise LedgerInputError(
                    f"native registry aliases handler 0x{handler:08x}; "
                    "aliases must be represented explicitly before they can be classified"
                )
            out[handler] = {
                "index": index,
                "recordVa": record,
                "shippedName": f[3],
                "ghidraName": f[4],
                "registryStatus": f[5],
            }
    return out, file_stamp(path)


# --- TTD coverage indexes ---------------------------------------------------

RE_RANGE = re.compile(r'"rva_start"\s*:\s*"(0x[0-9a-fA-F]+)"\s*,\s*"rva_end_exclusive"\s*:\s*"(0x[0-9a-fA-F]+)"')


def load_coverage_index(path: Path):
    """Parse one coverage.jsonl into raw (start, end_exclusive) RVA ranges.

    Only `kind:"range"` lines contribute. No counter field is read: step and
    instruction counters are quarantined (task #149).
    """
    ranges = []
    meta = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"kind":"range"' in line.replace(" ", ""):
                m = RE_RANGE.search(line)
                if m:
                    ranges.append((int(m.group(1), 16), int(m.group(2), 16)))
                    continue
                obj = json.loads(line)
                ranges.append((int(obj["rva_start"], 16), int(obj["rva_end_exclusive"], 16)))
            elif meta is None and '"kind":"metadata"' in line.replace(" ", ""):
                try:
                    meta = json.loads(line)
                except json.JSONDecodeError:
                    meta = None
    return ranges, meta


def discover_coverage_indexes(roots):
    found = []
    for root in roots:
        # An empty string becomes Path('.') and would walk the entire repository,
        # silently pulling in indexes the caller did not ask for. Refuse it.
        if not str(root).strip():
            print("WARNING: ignoring an empty --coverage-root", file=sys.stderr)
            continue
        root = Path(root)
        if not root.exists():
            print(f"WARNING: coverage root does not exist, skipped: {root}", file=sys.stderr)
            continue
        if root.is_file():
            found.append(root)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            if "coverage.jsonl" in filenames:
                found.append(Path(dirpath) / "coverage.jsonl")
    return sorted(set(found), key=str)


def read_source_receipt(cov_path: Path):
    """Best-effort receipt read. Returns only fields that are safe to trust."""
    rp = cov_path.parent / "receipt.json"
    if not rp.exists():
        return None
    try:
        r = json.loads(rp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    summary = r.get("summary", {}) or {}
    return {
        "generatedAtUtc": r.get("generatedAtUtc"),
        "exitCode": r.get("exitCode"),
        "collectorExitCode": r.get("collectorExitCode"),
        "replayComplete": r.get("replayComplete"),
        "stopReason": (r.get("terminalStop") or {}).get("stopReason"),
        "terminalStopAccepted": (r.get("terminalStop") or {}).get("terminalStopAccepted"),
        "stopReasonAdjudicated": r.get("stopReasonAdjudicated"),
        "countersQuarantined": r.get("countersQuarantined"),
        "traceSha256": (r.get("trace") or {}).get("sha256"),
        "traceBytes": (r.get("trace") or {}).get("bytes"),
        "targetSha256": (r.get("target") or {}).get("sha256"),
        "reportedCoveredBytes": summary.get("covered_bytes"),
        "rangeCount": summary.get("range_count"),
    }


# --- Evidence citation scan -------------------------------------------------

RE_ADDR_TOKEN = re.compile(r"(?<![0-9a-fA-F])(?:0[xX])?([0-9a-fA-F]{8})(?![0-9a-fA-F])")


def scan_evidence(roots, extra_globs_root: Path, text_lo_va, text_hi_va, inventory_threshold):
    """Count exact entry-address citations across the evidence corpus.

    A citation is an 8-hex token, delimited by non-hex characters, whose value
    lands inside `.text`. The delimiter rule is what keeps sha256 fragments out.

    Files that mention more than `inventory_threshold` distinct `.text`
    addresses are treated as INVENTORY DUMPS and excluded: the name table alone
    lists all 7,555 addresses, and counting it would make the citation signal
    meaningless. The excluded list is returned so the exclusion is auditable.

    This measures that somebody wrote the address down in prose. It does NOT
    measure that what they wrote is correct.
    """
    files = []
    for root in roots:
        root = Path(root)
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            parts = set(Path(dirpath).parts)
            if parts & EVIDENCE_SKIP_DIR_PARTS:
                dirnames[:] = []
                continue
            for fn in filenames:
                p = Path(dirpath) / fn
                if p.suffix.lower() in EVIDENCE_EXTS and p.stat().st_size <= EVIDENCE_MAX_BYTES:
                    files.append(p)
    if extra_globs_root:
        for pat in DEFAULT_EVIDENCE_GLOBS:
            files.extend(sorted(extra_globs_root.glob(pat)))

    files = sorted(set(files), key=str)
    counts = Counter()
    focused = Counter()
    docs = defaultdict(set)
    excluded = []
    scanned = 0
    bulk_files = 0
    for p in files:
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(p.relative_to(REPO)) if str(p).startswith(str(REPO)) else str(p)
        hits = Counter()
        for m in RE_ADDR_TOKEN.finditer(txt):
            v = int(m.group(1), 16)
            if text_lo_va <= v < text_hi_va:
                hits[v] += 1
        if len(hits) > inventory_threshold:
            excluded.append({"path": rel, "distinctAddresses": len(hits)})
            continue
        scanned += 1
        is_bulk = any(mark in rel.replace("\\", "/") for mark in BULK_REVIEW_MARKERS)
        if is_bulk:
            bulk_files += 1
        for v, n in hits.items():
            counts[v] += n
            docs[v].add(rel)
            if not is_bulk:
                focused[v] += n
    return counts, focused, docs, scanned, bulk_files, excluded


# --- Static reference scan --------------------------------------------------


def scan_static_refs(spec: Specimen, entry_rvas):
    """Byte-pattern superset of the ways a function entry can be referenced.

    Not a disassembly. Three separate signals, kept separate because they mean
    different things for reachability:

      rel32 edges   `E8`/`E9` inside `.text` whose rel32 lands exactly on a
                    known entry. Direct static call or tail-jump.
      pointer refs  dword-ALIGNED locations in any section whose value equals an
                    entry VA. This is how vtables and EH funcinfo tables reach
                    their targets: virtual dispatch, reachable if the right
                    object type is instantiated.
      immediate refs  4-byte little-endian occurrences at ANY offset in `.text`
                    equal to an entry VA. This is `push offset F` /
                    `mov reg, offset F` -- the form the MissionScript native
                    registry uses, since it is built at runtime by
                    ScriptCommandRegistry__InitBuiltins rather than sitting in
                    static data. Without this pass, every script native looks
                    unreferenced.

    A function with none of the three is a *candidate* for unreachable, never a
    proof of it: computed dispatch and jump-table forms are not modelled here.
    """
    entry_set = set(entry_rvas)
    data = spec.data
    base = spec.text_rawptr
    size = min(spec.text_rawsize, spec.text_vsize)
    text_lo, text_hi = spec.text_lo, spec.text_hi

    edges = []  # (site_rva, target_rva, kind)
    for opcode, kind in ((0xE8, "CALL"), (0xE9, "JMP")):
        needle = bytes([opcode])
        pos = data.find(needle, base, base + size)
        while pos != -1:
            off = pos - base
            if off + 5 <= size:
                rel = struct.unpack_from("<i", data, pos + 1)[0]
                site_rva = text_lo + off
                tgt = site_rva + 5 + rel
                if tgt in entry_set:
                    edges.append((site_rva, tgt, kind))
            pos = data.find(needle, pos + 1, base + size)

    # False-positive floor: probability a random byte-triple decodes to a valid
    # entry. Reported, not hidden.
    e8_sites = data.count(b"\xe8", base, base + size)
    e9_sites = data.count(b"\xe9", base, base + size)

    ptr_refs = Counter()
    ptr_by_section = defaultdict(Counter)
    image_base = spec.image_base
    for sec in spec.sections:
        raw_lo = sec["rawptr"]
        raw_hi = sec["rawptr"] + sec["rawsize"]
        if raw_hi <= raw_lo:
            continue
        chunk = data[raw_lo:raw_hi]
        n = len(chunk) - (len(chunk) % 4)
        for (v,) in struct.iter_unpack("<I", chunk[:n]):
            rva = v - image_base
            if text_lo <= rva < text_hi and rva in entry_set:
                ptr_refs[rva] += 1
                ptr_by_section[rva][sec["name"]] += 1

    # Unaligned immediates inside .text. Four shifted aligned passes cover every
    # byte offset without a per-byte Python loop.
    imm_refs = Counter()
    text_blob = data[base : base + size]
    for shift in range(4):
        tail = text_blob[shift:]
        n = len(tail) - (len(tail) % 4)
        for (v,) in struct.iter_unpack("<I", tail[:n]):
            rva = v - image_base
            if text_lo <= rva < text_hi and rva in entry_set:
                imm_refs[rva] += 1

    return {
        "edges": edges,
        "ptrRefs": ptr_refs,
        "ptrBySection": ptr_by_section,
        "immRefs": imm_refs,
        "e8ByteCount": e8_sites,
        "e9ByteCount": e9_sites,
    }


# ---------------------------------------------------------------------------
# Reachability classification. NAME-BASED HEURISTIC -- inferred, not measured.
# ---------------------------------------------------------------------------

REACH_RULES = [
    # (label, compiled regex over the symbol name, note)
    ("CRT_EH_FUNCLET", re.compile(r"^Unwind@"), "MSVC exception funclet; runs only while unwinding a throw"),
    ("EH_ERROR_PATH", re.compile(r"(?i)(exception|__except|unwind|assert|fatal|panic|onerror|handleerror|_error|errorhandler|throw|hresulttostring|d3derr|dderr|failedcase)"), "error / exception handling"),
    ("MULTIPLAYER", re.compile(r"(?i)(multiplayer|netgame|network|lobby|dplay|directplay|ipx|modem|skirmish|deathmatch|remoteplayer|(^|_)mp[A-Z_])"), "needs a real multiplayer session"),
    ("CRT_RUNTIME", re.compile(r"(?i)(^_+[a-z]|^std__|operator_new|operator_delete|^malloc|^free$|^printf|^sprintf|^memcpy|^memset|^strcmp|crt|^type_info|^__)"), "MSVC C runtime / compiler support"),
    ("EDITOR_DEBUG", re.compile(r"(?i)(editor|devmode|debugdraw|profiler|benchmark|dumpmem|memstats)"), "developer / editor path"),
    ("CONSOLE", re.compile(r"(?i)(cconsole|console__|execscript|cvar)"), "reachable through the proven console command path"),
    ("SCRIPT_VM", re.compile(r"(?i)(iscript|missionscript|scriptcommand|^cscript)"), "script VM; reachable by authoring bytecode"),
    ("COMBAT_AI", re.compile(r"(?i)(weapon|projectile|missile|bullet|damage|destro|explo|turret|squad|hive|boss|guide|ammo|shield|hitpoint|health|kill|die|attack|target)"), "combat / AI; reachable in-game with the right scenario"),
    ("RENDER", re.compile(r"(?i)(render|^cpd|^dx|d3d|shader|texture|mesh|sprite|particle|water|cloud|sky|light|fog|hud|font)"), "render path; reachable but needs the state that triggers it"),
    ("FRONTEND", re.compile(r"(?i)(frontend|menu|goodies|credits|options|career|fmv|cutscene|savegame|slot)"), "frontend page or flow"),
    ("WORLD_SIM", re.compile(r"(?i)(cworld|cthing|cactor|physics|collision|terrain|heightfield|battleengine|mech|vehicle|aircraft|jet|walker)"), "world simulation; reachable in-game"),
]

# Explicit family overrides for the largest families the keyword rules miss.
# Each is a judgement, listed so it can be argued with rather than buried in a
# regex. A family is a naming convention, not a measured module boundary.
FAMILY_REACH_OVERRIDES = {
    "CFastVB": "RENDER",            # D3D vertex-buffer wrapper; no keyword in the name
    "CDXMeshVB": "RENDER",
    "CStaticShadows": "RENDER",
    "CPolyBucket": "RENDER",
    "DXPalletizer": "RENDER",
    "CMCBuggy": "COMBAT_AI",        # a mech chassis like CMCMech
    "CFEPMultiplayerStart": "MULTIPLAYER",  # the MP frontend page: clickable, but it is the MP lane
    "CCutscene": "FRONTEND",
    "CFEPDebriefing": "FRONTEND",
    "CFEPWingmen": "FRONTEND",
    "Math": "MATH_LIB",
    "Mat34": "MATH_LIB",
    "Vec3": "MATH_LIB",
    "CGame": "ENGINE_CORE",
    "CEngine": "ENGINE_CORE",
    "CDXEngine": "ENGINE_CORE",
    "CD3DApplication": "ENGINE_CORE",
    "CController": "INPUT",
    "Controls": "INPUT",
    "CSoundManager": "AUDIO",
}

# Classes an in-game probe cannot light no matter how long you play, or can only
# light by leaving the single-player loop entirely.
REACH_HARD = {"CRT_EH_FUNCLET", "EH_ERROR_PATH", "MULTIPLAYER", "EDITOR_DEBUG", "CRT_RUNTIME"}


def reach_class(name: str) -> str:
    fam = family_of(name)
    if fam in FAMILY_REACH_OVERRIDES:
        return FAMILY_REACH_OVERRIDES[fam]
    for label, rx, _note in REACH_RULES:
        if rx.search(name):
            return label
    return "UNCLASSIFIED"


def family_of(name: str) -> str:
    """Class-name family: the token before `__`, else a coarse bucket."""
    if name.startswith("Unwind@"):
        return "(eh-funclet)"
    if RE_FUN.match(name):
        return "(unnamed FUN_*)"
    if RE_VFUNCSLOT.match(name):
        return "(vtable slot only)"
    if "__" in name:
        return name.split("__", 1)[0]
    if name.startswith("thunk_"):
        return "(thunk)"
    return "(free function)"


# ---------------------------------------------------------------------------
# Build.
# ---------------------------------------------------------------------------


def build(args) -> int:
    destination = Path(args.out)
    if destination.exists():
        print(f"FATAL: refusing existing snapshot destination: {destination}", file=sys.stderr)
        return 2
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    original_out = args.out
    args.out = str(stage)
    try:
        result = _build_into(args)
        if result != 0:
            return result
        missing = [name for name in SNAPSHOT_FILES if not (stage / name).is_file()]
        if missing:
            print(f"FATAL: staged snapshot omitted outputs: {missing}", file=sys.stderr)
            return 2
        ready = {
            "schema": SNAPSHOT_READY_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "files": {
                name: {**file_stamp(stage / name), "path": name}
                for name in SNAPSHOT_FILES
            },
        }
        (stage / "ledger.ready.json").write_text(
            json.dumps(ready, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(stage, destination)
        print(f"READY snapshot published atomically to {destination}", file=sys.stderr)
        return 0
    finally:
        args.out = original_out
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)


def _build_into(args) -> int:
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_path = Path(args.specimen)
    if not spec_path.exists():
        print(f"FATAL: specimen not found: {spec_path}", file=sys.stderr)
        return 2
    spec_stamp = file_stamp(spec_path)
    if spec_stamp["sha256"] != PRISTINE_SHA256 and not args.allow_specimen_mismatch:
        print(
            "FATAL: specimen sha256 is not the pristine baseline.\n"
            f"  expected {PRISTINE_SHA256}\n"
            f"  got      {spec_stamp['sha256']}\n"
            "Byte evidence must come from the pristine specimen. Pass\n"
            "--allow-specimen-mismatch only if you intend a non-baseline reading,\n"
            "and expect every byte number below to be about that other file.",
            file=sys.stderr,
        )
        return 2

    spec = Specimen(spec_path)
    text_lo, text_hi = spec.text_lo, spec.text_hi
    text_size = spec.text_vsize
    text_lo_va = spec.image_base + text_lo
    text_hi_va = spec.image_base + text_hi

    print(f"[1/7] specimen {spec_path.name} sha256 {spec_stamp['sha256'][:8]}…", file=sys.stderr)
    print(f"      .text RVA [0x{text_lo:x}, 0x{text_hi:x}) = {text_size:,} bytes", file=sys.stderr)

    # --- coverage ----------------------------------------------------------
    # Filter blanks BEFORE the Path() conversion: Path("") is Path("."), which
    # would walk the whole repository and silently pull in indexes the caller
    # never asked for.
    raw_roots = args.coverage_root if args.coverage_root is not None else DEFAULT_COVERAGE_ROOTS
    roots = []
    for r in raw_roots:
        if not str(r).strip():
            print("WARNING: ignoring an empty --coverage-root", file=sys.stderr)
            continue
        roots.append(Path(r))
    cov_paths = discover_coverage_indexes(roots)
    if args.coverage_index:
        cov_paths.extend(Path(p) for p in args.coverage_index)
        cov_paths = sorted(set(cov_paths), key=str)
    print(f"[2/7] {len(cov_paths)} coverage index(es) discovered", file=sys.stderr)

    sources = []
    all_ranges = []
    per_source_runs = {}
    for p in cov_paths:
        ranges, meta = load_coverage_index(p)
        runs = merge(clip(merge(ranges), text_lo, text_hi))
        sid = p.parent.name
        per_source_runs[sid] = runs
        rec = {
            "sourceId": sid,
            "coverageIndex": str(p),
            "coverageSha256": sha256_of(p),
            "textBytesObserved": total(runs),
            "rangeCount": len(ranges),
            "receipt": read_source_receipt(p),
            "moduleName": (meta or {}).get("module_name"),
            "trace": (meta or {}).get("trace"),
        }
        sources.append(rec)
        all_ranges.extend(runs)

    union = CoverageIndex(clip(merge(all_ranges), text_lo, text_hi))
    union_runs = union.runs
    observed_bytes = union.total()
    coverage_digest = coverage_set_sha256(sources)
    print(f"      union observed .text = {observed_bytes:,} bytes ({100*observed_bytes/text_size:.4f}%)", file=sys.stderr)

    # --- name table --------------------------------------------------------
    names_path = Path(args.names)
    rows, name_header = load_name_table(names_path)
    names_stamp = file_stamp(names_path)
    population_date = function_population_date(names_path)
    print(f"[3/7] name table: {len(rows):,} functions", file=sys.stderr)

    hulls = []
    overlapping = 0
    prev_hi = None
    outside_text = 0
    for r in rows:
        lo = r["hullLoVa"] - spec.image_base
        hi = r["hullHiVa"] - spec.image_base + 1  # table is inclusive-max
        r["lo"] = lo
        r["hi"] = hi
        r["hullBytes"] = hi - lo
        if not (text_lo <= lo < text_hi):
            outside_text += 1
        hulls.append((lo, hi))
        if prev_hi is not None and lo < prev_hi:
            overlapping += 1
        prev_hi = max(prev_hi or 0, hi)

    hull_union = merge(clip(hulls, text_lo, text_hi))
    hull_union_bytes = total(hull_union)

    exact_graph = None
    graph_value = None if args.no_exact_bodies else args.parity_graph
    if graph_value and str(graph_value).strip():
        graph_path = Path(graph_value)
        if not graph_path.is_file():
            print(f"FATAL: parity-graph receipt not found: {graph_path}", file=sys.stderr)
            return 2
        try:
            exact_graph = load_exact_body_graph(graph_path, spec, rows)
        except LedgerInputError as exc:
            print(f"FATAL: exact body graph rejected: {exc}", file=sys.stderr)
            return 2
        print(
            f"      exact bodies: {exact_graph['rangeCount']:,} fragments / "
            f"{exact_graph['functionCount']:,} functions = {exact_graph['unionBytes']:,} bytes",
            file=sys.stderr,
        )
    else:
        print("      exact bodies: unavailable; retaining conservative hull accounting", file=sys.stderr)

    body_union = exact_graph["union"] if exact_graph else hull_union
    body_union_bytes = total(body_union)
    body_accounting = "EXACT_GHIDRA_FRAGMENTS" if exact_graph else "BODY_MIN_MAX_HULLS"
    unmapped = subtract([(text_lo, text_hi)], body_union)
    unmapped_bytes = total(unmapped)

    # --- natives, evidence, static refs ------------------------------------
    try:
        natives, natives_stamp = load_natives(Path(args.natives) if args.natives else None)
    except LedgerInputError as exc:
        print(f"FATAL: native registry rejected: {exc}", file=sys.stderr)
        return 2
    print(f"[4/7] native registry: {len(natives)} handler bindings", file=sys.stderr)

    # Native execution, tested at the BYTE level and independent of whether
    # Ghidra has a function at the handler address. 86 of the 144 handlers have
    # no function, so a name-table join alone under-counts badly. This doubles
    # as a self-test: the number below should reproduce the independently
    # verified 60-hit / 59-real figure when run over the 66-level campaign.
    natives_observed = {}
    for handler_va, info in natives.items():
        rva = handler_va - spec.image_base
        hit = union.covered_in(rva, rva + 1) > 0 if text_lo <= rva < text_hi else False
        natives_observed[handler_va] = hit
    natives_hit = sum(1 for v in natives_observed.values() if v)
    natives_hit_uncontradicted = sum(
        1 for h, v in natives_observed.items()
        if v and natives[h]["registryStatus"] != "CONTRADICTED"
    )
    try:
        native_canary = native_canary_result(
            Path(args.native_canary) if args.native_canary else None,
            coverage_digest,
            natives_stamp,
            natives_hit,
            natives_hit_uncontradicted,
        )
    except LedgerInputError as exc:
        print(f"FATAL: native execution canary rejected: {exc}", file=sys.stderr)
        return 2

    function_by_va = {row["va"]: row for row in rows}
    native_rows = []
    for handler, info in sorted(natives.items(), key=lambda item: item[1]["index"]):
        function = function_by_va.get(handler)
        observed = natives_observed[handler]
        if info["registryStatus"] == "CONTRADICTED":
            terminal = "WRONG_PRIOR_NAME"
        elif function is None:
            terminal = "BOUNDARY_MISSING"
        elif not observed:
            terminal = "UNREACHED_IN_SCENARIOS"
        elif info["registryStatus"] in ("MATCH", "WEAK"):
            terminal = "ENTRY_CONFIRMED_NAME_WEAK"
        else:
            terminal = "ENTRY_CONFIRMED_BEHAVIOR_UNKNOWN"
        native_rows.append(
            {
                "index": info["index"],
                "recordVa": info["recordVa"],
                "handlerVa": handler,
                "shippedName": info["shippedName"],
                "currentGhidraName": function["name"] if function else "",
                "registryStatus": info["registryStatus"],
                "functionPresent": function is not None,
                "observed": observed,
                "terminalState": terminal,
                "needsBoundaryReview": function is None,
                "needsBehaviorContract": observed,
            }
        )
    native_terminal_counts = Counter(row["terminalState"] for row in native_rows)

    if args.skip_evidence:
        cite_counts, cite_focused, cite_docs, n_evidence_files, n_bulk_files, cite_excluded = (
            Counter(), Counter(), {}, 0, 0, []
        )
    else:
        ev_roots = [Path(r) for r in (args.evidence_root or DEFAULT_EVIDENCE_ROOTS)]
        cite_counts, cite_focused, cite_docs, n_evidence_files, n_bulk_files, cite_excluded = scan_evidence(
            ev_roots, REPO, text_lo_va, text_hi_va, args.inventory_threshold
        )
    print(f"[5/7] evidence corpus: {n_evidence_files} files scanned "
          f"({n_bulk_files} bulk-review, {len(cite_excluded)} inventory dumps excluded), "
          f"{len(cite_counts):,} distinct .text addresses cited "
          f"({len(cite_focused):,} outside the bulk-review corpus)", file=sys.stderr)

    entry_rvas = [r["va"] - spec.image_base for r in rows]
    if args.skip_static_refs:
        refs = {"edges": [], "ptrRefs": Counter(), "ptrBySection": {}, "immRefs": Counter(),
                "e8ByteCount": 0, "e9ByteCount": 0}
    else:
        refs = scan_static_refs(spec, entry_rvas)
    print(f"[6/7] static refs: {len(refs['edges']):,} rel32 edges, "
          f"{sum(refs['ptrRefs'].values()):,} aligned pointer refs, "
          f"{sum(refs['immRefs'].values()):,} in-.text immediates", file=sys.stderr)

    # --- per-function ledger ------------------------------------------------
    by_rva = {r["va"] - spec.image_base: r for r in rows}
    starts = [r["lo"] for r in rows]

    exact_intervals = []
    exact_interval_starts = []
    if exact_graph:
        row_by_va = {r["va"]: r for r in rows}
        exact_intervals = sorted(
            (lo, hi, row_by_va[entry])
            for entry, ranges in exact_graph["byEntryVa"].items()
            for lo, hi in ranges
        )
        exact_interval_starts = [lo for lo, _hi, _row in exact_intervals]

    def containing(rva):
        if exact_graph:
            i = bisect_right(exact_interval_starts, rva) - 1
            if i >= 0:
                lo, hi, row = exact_intervals[i]
                if lo <= rva < hi:
                    return row
            return None
        i = bisect_right(starts, rva) - 1
        while i >= 0:
            r = rows[i]
            if r["lo"] <= rva < r["hi"]:
                return r
            # hulls can nest; walk back a bounded distance
            if r["lo"] + 0x20000 < rva:
                break
            i -= 1
        return None

    in_edges = defaultdict(list)
    for site, tgt, kind in refs["edges"]:
        in_edges[tgt].append((site, kind))

    funcs = []
    for idx, r in enumerate(rows):
        lo, hi = r["lo"], r["hi"]
        hull_obs = union.covered_in(lo, hi) if text_lo <= lo < text_hi else 0
        nc = name_class(r["name"])
        nat = natives.get(r["va"])
        cited = cite_counts.get(r["va"], 0)
        # Tighter of two upper bounds on body size: the bodyMin..bodyMax hull,
        # and the distance to the next function entry. Both over-count (padding,
        # non-contiguity); neither under-counts a contiguous body.
        next_lo = rows[idx + 1]["lo"] if idx + 1 < len(rows) else None
        span_next = (next_lo - lo) if (next_lo is not None and next_lo > lo) else None
        body_est = min(r["hullBytes"], span_next) if span_next else r["hullBytes"]
        exact_ranges = exact_graph["byEntryVa"][r["va"]] if exact_graph else []
        body_ranges = exact_ranges if exact_graph else [(lo, hi)]
        body_exact = sum(b - a for a, b in exact_ranges) if exact_graph else None
        body_bytes = body_exact if body_exact is not None else body_est
        exec_denominator = body_exact if body_exact is not None else r["hullBytes"]
        range_text = ";".join(f"0x{a:x}-0x{b:x}" for a, b in body_ranges)
        range_set_sha256 = _canonical_json_sha256(body_ranges) if exact_graph else "UNKNOWN"
        entity_key = (
            f"CODE:{spec_stamp['sha256']}:VA=0x{r['va']:08x}:RANGES={range_set_sha256}"
            if exact_graph else "UNKNOWN"
        )
        obs = sum(union.covered_in(a, b) for a, b in body_ranges)
        hit_sources = (
            [
                sid for sid, runs in per_source_runs.items()
                if sum(CoverageIndexCacheGet(sid, runs).covered_in(a, b) for a, b in body_ranges) > 0
            ]
            if args.per_source else []
        )
        exec_state = "DARK" if obs == 0 else ("COVERED" if obs >= exec_denominator else "PARTIAL")
        funcs.append(
            {
                "va": r["va"],
                "entryRva": r["va"] - spec.image_base,
                "entityKey": entity_key,
                "name": r["name"],
                "lo": lo,
                "hi": hi,
                "bodyRanges": body_ranges,
                "bodyRangesRva": range_text if exact_graph else "UNKNOWN",
                "bodyRangeSetSha256": range_set_sha256,
                "bodyRangeCount": len(body_ranges) if exact_graph else "UNKNOWN",
                "bodyAccounting": body_accounting,
                "bodyBytes": body_bytes,
                "bodyBytesExact": body_exact if body_exact is not None else "UNKNOWN",
                "hullBytes": r["hullBytes"],
                "spanToNextEntry": span_next if span_next is not None else "",
                "bodyBytesEstimate": body_est,
                "hullSuspect": r["hullBytes"] > HULL_SUSPECT_BYTES,
                "nameClass": nc,
                "observedBytes": obs,
                "observedBytesInHull": hull_obs,
                "observedPctOfBody": (
                    round(100.0 * obs / exec_denominator, 4) if exec_denominator else 0.0
                ),
                "observedPctOfHull": round(100.0 * hull_obs / r["hullBytes"], 4) if r["hullBytes"] else 0.0,
                "execState": exec_state,
                "execStateHull": (
                    "DARK" if hull_obs == 0 else ("COVERED" if hull_obs >= r["hullBytes"] else "PARTIAL")
                ),
                "sourceHits": len(hit_sources),
                "nativeShippedName": (nat or {}).get("shippedName"),
                "nativeRegistryStatus": (nat or {}).get("registryStatus"),
                "citationCount": cited,
                "citationCountFocused": cite_focused.get(r["va"], 0),
                "citingDocs": len(cite_docs.get(r["va"], ())) if cite_docs else 0,
                "inCallSites": len(in_edges.get(lo, [])),
                "ptrRefs": refs["ptrRefs"].get(lo, 0),
                "immRefs": refs["immRefs"].get(lo, 0),
                "family": family_of(r["name"]),
                "reachClass": reach_class(r["name"]),
            }
        )

    # caller-side adjacency: for each edge, was the *calling* body observed?
    exec_state_by_lo = {f["lo"]: f["execState"] for f in funcs}
    name_class_by_lo = {f["lo"]: f["nameClass"] for f in funcs}
    in_callers = defaultdict(set)
    in_callers_observed = defaultdict(set)
    in_callers_named = defaultdict(set)
    unmapped_call_sites = Counter()
    for site, tgt, _kind in refs["edges"]:
        c = containing(site)
        if c is None:
            unmapped_call_sites[tgt] += 1
            continue
        clo = c["lo"]
        in_callers[tgt].add(clo)
        if exec_state_by_lo.get(clo) in ("PARTIAL", "COVERED"):
            in_callers_observed[tgt].add(clo)
        if name_class_by_lo.get(clo) in HUMAN_NAMED_CLASSES:
            in_callers_named[tgt].add(clo)

    for f in funcs:
        lo = f["lo"]
        f["inCallers"] = len(in_callers.get(lo, ()))
        f["inCallersObserved"] = len(in_callers_observed.get(lo, ()))
        f["inCallersNamed"] = len(in_callers_named.get(lo, ()))
        f["inCallSitesUnmapped"] = unmapped_call_sites.get(lo, 0)
        f["staticRefTotal"] = f["inCallSites"] + f["ptrRefs"] + f["immRefs"]
        f["noStaticRef"] = f["staticRefTotal"] == 0
        f["vtableOnly"] = f["inCallSites"] == 0 and f["immRefs"] == 0 and f["ptrRefs"] > 0
        f["understoodTier"] = evidence_proxy_tier(
            f["nameClass"], f["citationCountFocused"], f["citationCount"]
        )
        # cheapness of identifying a dark body from observed neighbours.
        # Components are all present as their own columns; this is a sort key,
        # not a claim.
        f["adjacencyScore"] = f["inCallersObserved"] * 4 + f["inCallersNamed"] * 2 + min(f["ptrRefs"], 8)

    # --- reconcile the dark byte mass ---------------------------------------
    # With an authenticated parity graph these are exact Ghidra fragments. The
    # legacy fallback retains hulls and labels them as such.
    unobserved = subtract([(text_lo, text_hi)], union_runs)
    unobserved_in_bodies = total(
        [(max(a, ba), min(b, bb)) for (ba, bb) in body_union for (a, b) in unobserved
         if min(b, bb) > max(a, ba)]
    )
    unobserved_unmapped = total(unobserved) - unobserved_in_bodies

    # The three-way split the reachability question actually turns on.
    # Dark bytes inside a PARTIALLY observed body are branches not taken in a
    # function the process has already entered -- a different problem entirely
    # from a body that never ran. Exact fragments do not overlap; the fallback
    # merges hulls per class and preserves the earlier overlap attribution.
    dark_body_ranges = merge(clip(
        [item for f in funcs if f["execState"] == "DARK" for item in f["bodyRanges"]],
        text_lo,
        text_hi,
    ))
    partial_body_ranges = merge(clip(
        [item for f in funcs if f["execState"] == "PARTIAL" for item in f["bodyRanges"]],
        text_lo,
        text_hi,
    ))
    dark_in_dark_bodies = total(
        [(max(a, ba), min(b, bb)) for (ba, bb) in dark_body_ranges for (a, b) in unobserved
         if min(b, bb) > max(a, ba)]
    )
    partial_dark_raw = total(
        [(max(a, ba), min(b, bb)) for (ba, bb) in partial_body_ranges for (a, b) in unobserved
         if min(b, bb) > max(a, ba)]
    )
    # A byte can sit in both a dark hull and a partial hull only in fallback
    # mode. Attribute such bytes to the partial side so all parts still sum.
    dark_in_partial_bodies = max(0, unobserved_in_bodies - dark_in_dark_bodies)
    partial_overlap_note = partial_dark_raw - dark_in_partial_bodies

    # --- executed but unmapped ---------------------------------------------
    exec_unmapped = merge(
        [
            (max(a, ua), min(b, ub))
            for (ua, ub) in unmapped
            for (a, b) in union_runs
            if min(b, ub) > max(a, ua)
        ]
    )
    exec_unmapped_bytes = total(exec_unmapped)

    # Padding tally over the unmapped mass, and over the DARK unmapped mass.
    # The second one is the load-bearing number: bytes that are alignment fill
    # or in-.text data can never be "observed executing" no matter how the game
    # is probed, so they cap the achievable coverage ceiling independently of
    # any probe design.
    def pad_tally(ranges):
        n_pad = 0
        for a, b in ranges:
            off = spec.text_rawptr + (a - text_lo)
            n = min(b, text_lo + spec.text_rawsize) - a
            if n <= 0:
                continue
            chunk = spec.data[off : off + n]
            n_pad += chunk.count(0xCC) + chunk.count(0x90) + chunk.count(0x00)
        return n_pad

    pad_bytes = pad_tally(unmapped)
    dark_unmapped = subtract(merge(unmapped), union_runs)
    dark_unmapped_pad = pad_tally(dark_unmapped)

    # Partition every byte not claimed by an exact Ghidra body at coverage
    # boundaries. Executed segments are code candidates; dark segments remain
    # mechanically AMBIGUOUS even when their bytes look like padding. A byte
    # pattern is a useful falsifier hint, never sufficient proof of DATA or
    # PADDING on its own.
    unmapped_rows = []
    for gap_lo, gap_hi in unmapped:
        cuts = {gap_lo, gap_hi}
        for run_lo, run_hi in union_runs:
            if run_hi <= gap_lo:
                continue
            if run_lo >= gap_hi:
                break
            cuts.add(max(gap_lo, run_lo))
            cuts.add(min(gap_hi, run_hi))
        points = sorted(cuts)
        for seg_lo, seg_hi in zip(points, points[1:]):
            if seg_hi <= seg_lo:
                continue
            observed = union.covered_in(seg_lo, seg_hi)
            segment_bytes = seg_hi - seg_lo
            if observed not in (0, segment_bytes):
                raise LedgerInputError("unmapped partition did not split at a coverage boundary")
            raw_off = spec.text_rawptr + (seg_lo - text_lo)
            raw_len = max(0, min(seg_hi, text_lo + spec.text_rawsize) - seg_lo)
            payload = spec.data[raw_off : raw_off + raw_len]
            if raw_len != segment_bytes:
                byte_pattern = "VIRTUAL_TAIL"
            elif payload and all(value in (0x00, 0x90, 0xCC) for value in payload):
                byte_pattern = "PADDING_LIKE_BYTES"
            else:
                byte_pattern = "MIXED_OR_CODE_LIKE_BYTES"
            start_va = spec.image_base + seg_lo
            end_va = spec.image_base + seg_hi
            i = bisect_right(starts, seg_lo) - 1
            j = bisect_left(starts, seg_hi)
            unmapped_rows.append(
                {
                    "entityKey": (
                        f"TEXT_RESIDUAL:{spec_stamp['sha256']}:"
                        f"0x{start_va:08X}-0x{end_va:08X}"
                    ),
                    "startVa": start_va,
                    "endVa": end_va,
                    "bytes": segment_bytes,
                    "observedBytes": observed,
                    "observationState": "EXECUTED" if observed else "DARK",
                    "classification": "CODE_CANDIDATE" if observed else "AMBIGUOUS",
                    "classificationVerdict": "MEASURED_EXECUTION" if observed else "UNSCORED",
                    "terminalState": (
                        "OPEN_CODE_BOUNDARY" if observed else "OPEN_CLASSIFICATION"
                    ),
                    "bytePattern": byte_pattern,
                    "prevFunc": rows[i]["name"] if 0 <= i < len(rows) else "",
                    "nextFunc": rows[j]["name"] if 0 <= j < len(rows) else "",
                }
            )

    unmapped_row_bytes = sum(row["bytes"] for row in unmapped_rows)
    if unmapped_row_bytes != unmapped_bytes:
        raise LedgerInputError(
            "complete residual partition does not reproduce the unmapped-byte denominator"
        )
    if sum(row["observedBytes"] for row in unmapped_rows) != exec_unmapped_bytes:
        raise LedgerInputError(
            "complete residual partition does not reproduce executed-unmapped bytes"
        )

    # --- dark regions -------------------------------------------------------
    regions = []
    cur = None
    for f in sorted(funcs, key=lambda x: x["lo"]):
        if f["execState"] == "DARK":
            if cur and f["lo"] - cur["endRva"] <= args.region_gap:
                cur["endRva"] = max(cur["endRva"], f["hi"])
                cur["funcs"].append(f)
            else:
                if cur:
                    regions.append(cur)
                cur = {"startRva": f["lo"], "endRva": f["hi"], "funcs": [f]}
        else:
            if cur:
                regions.append(cur)
                cur = None
    if cur:
        regions.append(cur)

    region_rows = []
    for reg in regions:
        fs = reg["funcs"]
        fam = Counter(x["family"] for x in fs)
        rc = Counter(x["reachClass"] for x in fs)
        region_rows.append(
            {
                "startVa": spec.image_base + reg["startRva"],
                "endVa": spec.image_base + reg["endRva"],
                "spanBytes": reg["endRva"] - reg["startRva"],
                "darkBytes": sum(x["bodyBytes"] for x in fs),
                "darkHullBytes": sum(x["hullBytes"] for x in fs),
                "funcCount": len(fs),
                "hullSuspectFuncs": sum(1 for x in fs if x["hullSuspect"]),
                "namedCount": sum(1 for x in fs if x["nameClass"] in HUMAN_NAMED_CLASSES),
                "unnamedCount": sum(1 for x in fs if x["nameClass"] in UNNAMED_CLASSES),
                "inCallersObserved": sum(x["inCallersObserved"] for x in fs),
                "inCallersTotal": sum(x["inCallers"] for x in fs),
                "ptrRefs": sum(x["ptrRefs"] for x in fs),
                "immRefs": sum(x["immRefs"] for x in fs),
                "noStaticRefFuncs": sum(1 for x in fs if x["noStaticRef"]),
                "vtableOnlyFuncs": sum(1 for x in fs if x["vtableOnly"]),
                "topFamilies": "; ".join(f"{k}({v})" for k, v in fam.most_common(4)),
                "topReachClass": rc.most_common(1)[0][0] if rc else "UNCLASSIFIED",
                "reachMix": "; ".join(f"{k}({v})" for k, v in rc.most_common(4)),
                "largestFunc": max(fs, key=lambda x: x["bodyBytes"])["name"],
                "largestFuncBytes": max(x["bodyBytes"] for x in fs),
            }
        )
    region_rows.sort(key=lambda x: -x["darkBytes"])

    # --- family rollup (dark mass by class family) --------------------------
    fam_rollup = defaultdict(lambda: {"darkBytes": 0, "darkFuncs": 0, "totalBytes": 0, "totalFuncs": 0,
                                      "observedBytes": 0, "inCallersObserved": 0, "noStaticRef": 0,
                                      "reach": Counter()})
    for f in funcs:
        e = fam_rollup[f["family"]]
        e["totalBytes"] += f["bodyBytes"]
        e["totalFuncs"] += 1
        e["observedBytes"] += f["observedBytes"]
        e["reach"][f["reachClass"]] += 1
        if f["execState"] == "DARK":
            e["darkBytes"] += f["bodyBytes"]
            e["darkFuncs"] += 1
            e["inCallersObserved"] += f["inCallersObserved"]
            if f["noStaticRef"]:
                e["noStaticRef"] += 1

    # --- reachability accounting -------------------------------------------
    dark_funcs = [f for f in funcs if f["execState"] == "DARK"]
    dark_hull_bytes = sum(f["hullBytes"] for f in dark_funcs)
    dark_body_bytes = sum(f["bodyBytes"] for f in dark_funcs)

    reach_buckets = defaultdict(lambda: {"funcs": 0, "darkBytes": 0, "darkHullBytes": 0})
    for f in dark_funcs:
        b = reach_buckets[f["reachClass"]]
        b["funcs"] += 1
        b["darkBytes"] += f["bodyBytes"]
        b["darkHullBytes"] += f["hullBytes"]

    dark_no_ref = [f for f in dark_funcs if f["noStaticRef"]]
    dark_no_ref_bytes = sum(f["bodyBytes"] for f in dark_no_ref)
    dark_reachable_from_observed = [f for f in dark_funcs if f["inCallersObserved"] > 0]
    dark_reachable_bytes = sum(f["bodyBytes"] for f in dark_reachable_from_observed)
    dark_vtable_only = [f for f in dark_funcs if f["vtableOnly"]]
    dark_vtable_only_bytes = sum(f["bodyBytes"] for f in dark_vtable_only)

    hard_bytes = sum(v["darkBytes"] for k, v in reach_buckets.items() if k in REACH_HARD)
    hard_funcs = sum(v["funcs"] for k, v in reach_buckets.items() if k in REACH_HARD)

    # --- headline numbers ---------------------------------------------------
    n_funcs = len(funcs)
    n_unwind = sum(1 for f in funcs if f["nameClass"] == "UNWIND")
    human_denom = n_funcs - n_unwind
    by_exec = Counter(f["execState"] for f in funcs)
    by_name = Counter(f["nameClass"] for f in funcs)
    by_understood = Counter(f["understoodTier"] for f in funcs)
    fully_covered_hull = sum(1 for f in funcs if f["execStateHull"] == "COVERED")

    observed_funcs = [f for f in funcs if f["execState"] != "DARK"]
    observed_named = [f for f in observed_funcs if f["nameClass"] in HUMAN_NAMED_CLASSES]
    observed_unnamed = [f for f in observed_funcs if f["nameClass"] in UNNAMED_CLASSES]

    summary = {
        "schema": SCHEMA,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "toolPath": str(Path(__file__).relative_to(REPO)) if str(Path(__file__)).startswith(str(REPO)) else __file__,
        "readingRules": [
            "A coverage MISS is NON-OBSERVATION across the indexes supplied, never absence from the game.",
            "A coverage HIT proves bytes at that address executed. It does not prove the symbol name is correct.",
            (
                "Function execution states use authenticated exact Ghidra body fragments."
                if exact_graph else
                "Function execution states use bodyMin..bodyMax hulls; DARK is exact and COVERED is conservative."
            ),
            "Hull-union byte totals are UPPER BOUNDS on named-body bytes, not measurements of them.",
            (
                "The exact body export is a dated input, not an assertion about an unexported live Ghidra database."
                if exact_graph else
                "The exact body-byte total is UNKNOWN because no authenticated parity graph was supplied."
            ),
            "The historical 79.8268% .text figure is a DATED 6,411-body measurement and is NOT reproduced here.",
            "No step or instruction counter was read from any receipt (task #149).",
            "The static call graph is a byte-pattern superset, not a disassembly.",
            (
                "UNDERSTOOD tiers are weak citation/name proxies. Runtime entry coverage and registry "
                "bindings never establish a behavior contract."
            ),
        ],
        "denominators": {
            "textVirtualSizeBytes": text_size,
            "textRvaHalfOpen": [f"0x{text_lo:x}", f"0x{text_hi:x}"],
            "textSource": "PE section header of the specimen named in inputs.specimen",
            "functionPopulation": n_funcs,
            "functionPopulationSource": str(names_path),
            "functionPopulationDate": population_date,
            "humanNamableDenominator": human_denom,
            "humanNamableNote": f"{n_funcs} functions minus {n_unwind} MSVC Unwind@ EH funclets",
            "coverageIndexCount": len(sources),
            "coverageSetSha256": coverage_digest,
            "nativeRegistryPopulation": len(natives),
            "bodyAccountingMethod": body_accounting,
            "exactBodyByteTotal": exact_graph["unionBytes"] if exact_graph else "UNKNOWN",
            "exactBodyBytePctOfText": (
                round(100.0 * exact_graph["unionBytes"] / text_size, 6)
                if exact_graph else "UNKNOWN"
            ),
            "exactBodyFunctionCount": exact_graph["functionCount"] if exact_graph else "UNKNOWN",
            "exactBodyRangeCount": exact_graph["rangeCount"] if exact_graph else "UNKNOWN",
            "exactBodyFreshnessNote": (
                "Exact for the supplied, specimen-bound parity-graph export and matching function population; "
                "live Ghidra state after that export is not observed by this tool."
                if exact_graph else
                "UNKNOWN -- supply an authenticated ExportParityLabGraph READY receipt."
            ),
        },
        "inputs": {
            "specimen": spec_stamp,
            "nameTable": names_stamp,
            "parityGraph": (
                {
                    "receipt": exact_graph["receipt"],
                    "bodyRanges": exact_graph["bodyRanges"],
                    "program": exact_graph["program"],
                    "functionCount": exact_graph["functionCount"],
                    "rangeCount": exact_graph["rangeCount"],
                    "nameMismatchCount": exact_graph["nameMismatchCount"],
                }
                if exact_graph else None
            ),
            "nativeRegistry": natives_stamp,
            "evidenceFileCount": n_evidence_files,
            "evidenceInventoryThreshold": args.inventory_threshold,
            "evidenceExcludedAsInventory": cite_excluded,
            "coverageRoots": [str(r) for r in roots],
        },
        "bytes": {
            "textTotal": text_size,
            "observedUnion": observed_bytes,
            "observedUnionPct": round(100.0 * observed_bytes / text_size, 4),
            "darkBytes": text_size - observed_bytes,
            "darkPct": round(100.0 * (text_size - observed_bytes) / text_size, 4),
            "darkBytesInsideKnownBodies": unobserved_in_bodies,
            "knownBodyMethod": body_accounting,
            "darkBytesClaimedByNoFunction": unobserved_unmapped,
            "darkBytesInsideNeverEnteredBodies": dark_in_dark_bodies,
            "darkBytesInsidePartiallyObservedBodies": dark_in_partial_bodies,
            "darkThreeWaySplitNote": (
                "darkBytesInsideNeverEnteredBodies + darkBytesInsidePartiallyObservedBodies + "
                "darkBytesClaimedByNoFunction == darkBytes. The middle term is branches not taken in a "
                "function the process ALREADY entered -- a different and much easier problem than a body "
                "that never ran. "
                + (
                    "Exact Ghidra fragments are non-overlapping."
                    if exact_graph else
                    f"Hull overlap is {partial_overlap_note} bytes and is attributed to the partial side."
                )
            ),
            "darkReconciliationNote": (
                "darkBytesInsideKnownBodies + darkBytesClaimedByNoFunction == darkBytes. "
                + (
                    "Known bodies are authenticated exact fragments."
                    if exact_graph else
                    "Known bodies are legacy bodyMin..bodyMax hulls and therefore an upper-bound mapping."
                )
            ),
            "namedBodyUnion": body_union_bytes,
            "namedBodyUnionPct": round(100.0 * body_union_bytes / text_size, 6),
            "namedBodyUnionMethod": body_accounting,
            "namedHullUnion_UPPER_BOUND": hull_union_bytes,
            "namedHullUnionPct_UPPER_BOUND": round(100.0 * hull_union_bytes / text_size, 4),
            "namedHullUnionCaveat": (
                "UPPER BOUND. bodyMin..bodyMax hulls over-cover 67 non-contiguous bodies and "
                f"{overlapping} spans overlap their predecessor. This is NOT comparable to the "
                "dated 6,411-body 79.8268% figure and must not be presented as its successor."
            ),
            "unmappedByAnyFunction": unmapped_bytes,
            "unmappedByAnyFunctionPct": round(100.0 * unmapped_bytes / text_size, 4),
            "unmappedMethod": body_accounting,
            "unmappedBytesEqualToCC90or00": pad_bytes,
            "unmappedBytesEqualToCC90or00Note": (
                "A byte-value tally over the unmapped runs, not a run-length padding analysis. "
                "Alignment padding dominates it, but a 0x00 inside real data is counted too."
            ),
            "unmappedOtherBytes": unmapped_bytes - pad_bytes,
            "darkUnmappedBytesEqualToCC90or00": dark_unmapped_pad,
            "darkUnmappedCeilingNote": (
                "Bytes in the dark, unmapped mass whose value is CC/90/00. Alignment fill and in-.text "
                "data cannot execute, so they cap the achievable coverage ceiling no matter how the game "
                "is probed. This is a LOWER BOUND on the non-code fraction: jump tables and float "
                "constants living in .text are not counted here."
            ),
            "executedButUnmapped": exec_unmapped_bytes,
            "executedButUnmappedRuns": len(exec_unmapped),
            "allUnmappedSegments": len(unmapped_rows),
            "darkUnmappedSegments": sum(
                1 for row in unmapped_rows if row["observationState"] == "DARK"
            ),
            "executedButUnmappedNote": (
                "Bytes proven to execute that no supplied exact Ghidra body claims. Runs are candidate "
                "boundary fragments: several runs may belong to one function, and one run may include "
                "adjacent code/data. They are not a one-run/one-function count."
                if exact_graph else
                "Bytes proven to execute outside every supplied function hull. Runs are candidate "
                "boundary fragments, not a one-run/one-function count."
            ),
        },
        "functions": {
            "population": n_funcs,
            "observed": len(observed_funcs),
            "observedPct": round(100.0 * len(observed_funcs) / n_funcs, 4),
            "dark": by_exec.get("DARK", 0),
            "darkPct": round(100.0 * by_exec.get("DARK", 0) / n_funcs, 4),
            "fullyCovered": by_exec.get("COVERED", 0),
            "fullyCoveredMethod": body_accounting,
            "fullyCovered_conservativeHull": fully_covered_hull,
            "partial": by_exec.get("PARTIAL", 0),
            "darkBodyBytes": dark_body_bytes,
            "darkHullBytes": dark_hull_bytes,
            "byNameClass": dict(by_name),
            "byUnderstoodTier": dict(by_understood),
            "humanNamed": by_name.get("NAMED", 0),
            "humanNamedPctOfNamableDenom": round(100.0 * by_name.get("NAMED", 0) / human_denom, 4),
            "observedAndNamed": len(observed_named),
            "observedAndUnnamed": len(observed_unnamed),
            "observedAndUnnamedNote": "Executed bytes with no human name. The cheapest naming targets on the board.",
        },
        "understanding": {
            "U3_REVIEWED_RUNTIME_CONTRACT": 0,
            "U3_definition": (
                "Reserved for a reviewed receiver/input/write/return contract. This ledger has no contract "
                "input, so it never awards U3 from coverage, registry strings, names, or function creation."
            ),
            "U2_ADDRESS_CITED": by_understood.get("U2_ADDRESS_CITED", 0),
            "U2_definition": (
                f"entry address cited in a TARGETED evidence document ({n_evidence_files} files scanned, "
                f"{n_bulk_files} of them bulk-review shards counted separately)"
            ),
            "U1b_BULK_REVIEWED": by_understood.get("U1b_BULK_REVIEWED", 0),
            "U1b_definition": "cited only inside a bulk review corpus -- it was in a sweep, not the subject of a claim",
            "U1_NAMED_ONLY": by_understood.get("U1_NAMED_ONLY", 0),
            "U0_NONE": by_understood.get("U0_NONE", 0),
            "caveat": (
                "These are weak evidence proxies, not measurements of semantic understanding. A citation "
                "or name can be wrong; only a separately reviewed contract may earn U3."
            ),
        },
        "nativeCrossCheck": {
            "registryRows": len(natives),
            "handlersAtAGhidraFunctionEntry": sum(1 for h in natives if (h - spec.image_base) in {r["lo"] for r in rows}),
            "handlerFirstByteObserved": natives_hit,
            "handlerFirstByteObservedExcludingContradicted": natives_hit_uncontradicted,
            "terminalStates": dict(native_terminal_counts),
            "coverageSetSha256": coverage_digest,
            "canary": native_canary,
            "note": (
                "Byte-level handler observations are computed independently of Ghidra function creation. "
                "There is deliberately no universal expected count: expectations are valid only when a "
                "native canary is bound to the exact coverage-set and registry hashes."
            ),
        },
        "staticRefs": {
            "rel32EdgesOntoKnownEntries": len(refs["edges"]),
            "pointerRefsOntoKnownEntries": int(sum(refs["ptrRefs"].values())),
            "inTextImmediateRefsOntoKnownEntries": int(sum(refs["immRefs"].values())),
            "e8BytesInText": refs["e8ByteCount"],
            "e9BytesInText": refs["e9ByteCount"],
            "falsePositiveFloorEstimate": round(
                (refs["e8ByteCount"] + refs["e9ByteCount"]) * (n_funcs / text_size), 1
            ),
            "falsePositiveFloorNote": (
                "Expected count of random E8/E9 bytes whose rel32 happens to land on one of the "
                f"{n_funcs} entries, if the operand were uniform over .text. Compare against "
                "rel32EdgesOntoKnownEntries to judge signal."
            ),
            "method": "byte-pattern superset; not a disassembly; verify any single edge by disassembling its site",
        },
        "reachability": {
            "darkFunctionCount": len(dark_funcs),
            "darkBodyBytes": dark_body_bytes,
            "darkBodyBytesMethod": body_accounting,
            "darkBodyBytesEstimate": dark_body_bytes,
            "darkHullBytes": dark_hull_bytes,
            "darkWithObservedCaller": len(dark_reachable_from_observed),
            "darkWithObservedCallerBytes": dark_reachable_bytes,
            "darkVtableOnly": len(dark_vtable_only),
            "darkVtableOnlyBytes": dark_vtable_only_bytes,
            "darkVtableOnlyNote": (
                "Referenced only from an aligned pointer table (vtable / funcinfo). Reachable by "
                "instantiating the right object type, not by finding a call site."
            ),
            "darkWithNoStaticRefAtAll": len(dark_no_ref),
            "darkWithNoStaticRefBytes": dark_no_ref_bytes,
            "darkWithNoStaticRefNote": (
                "Candidate-unreachable: no rel32 edge, no aligned pointer, and no in-.text immediate "
                "anywhere in the image. NOT proof of dead code -- computed/indirect dispatch and jump-table "
                "forms this scan does not model would both look like this."
            ),
            "hardClassFuncs": hard_funcs,
            "hardClassBytes": hard_bytes,
            "hardClasses": sorted(REACH_HARD),
            "byClass": {k: v for k, v in sorted(reach_buckets.items(), key=lambda kv: -kv[1]["darkBytes"])},
            "classMethod": "NAME-BASED HEURISTIC over the symbol string. INFERRED, not measured. A wrong name gives a wrong class.",
        },
        "sources": sources,
    }

    (out_dir / "ledger-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # --- per-function TSV ---------------------------------------------------
    fcols = [
        "va", "entryRva", "entityKey", "name", "nameClass", "execState", "understoodTier", "reachClass", "family",
        "bodyAccounting", "bodyRangeCount", "bodyBytes", "bodyBytesExact",
        "bodyRangesRva", "bodyRangeSetSha256",
        "hullBytes", "bodyBytesEstimate", "spanToNextEntry", "hullSuspect",
        "observedBytes", "observedPctOfBody", "observedBytesInHull", "observedPctOfHull", "execStateHull",
        "sourceHits",
        "citationCount", "citationCountFocused", "citingDocs",
        "nativeShippedName", "nativeRegistryStatus",
        "inCallSites", "inCallers", "inCallersObserved", "inCallersNamed",
        "ptrRefs", "immRefs", "staticRefTotal", "noStaticRef", "vtableOnly", "adjacencyScore",
    ]
    with open(out_dir / "ledger-functions.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " per-function ledger\n")
        fh.write(f"# denominator: {n_funcs} functions from {names_path.name} (as of {population_date})\n")
        fh.write(f"# .text {text_size} bytes; union observed {observed_bytes} bytes over {len(sources)} coverage index(es)\n")
        fh.write(f"# execution state basis: {body_accounting}\n")
        fh.write("# hullBytes remains the bodyMin..bodyMax upper bound for comparison; bodyBytes is the accounting denominator.\n")
        fh.write("\t".join(fcols) + "\n")
        for f in sorted(funcs, key=lambda x: x["va"]):
            fh.write("\t".join(
                (
                    f"0x{f[c]:08x}"
                    if c in ("va", "entryRva") else str(f.get(c, ""))
                )
                for c in fcols
            ) + "\n")

    # --- dark regions TSV ---------------------------------------------------
    rcols = ["startVa", "endVa", "spanBytes", "darkBytes", "darkHullBytes", "funcCount", "hullSuspectFuncs",
             "namedCount", "unnamedCount",
             "inCallersObserved", "inCallersTotal", "ptrRefs", "immRefs", "noStaticRefFuncs", "vtableOnlyFuncs",
             "topReachClass", "reachMix", "topFamilies", "largestFunc", "largestFuncBytes"]
    with open(out_dir / "ledger-dark.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " dark regions, ranked by darkBytes\n")
        fh.write(f"# a region is a run of consecutive DARK functions with gaps <= {args.region_gap} bytes\n")
        fh.write(f"# darkBytes sums bodyBytes using {body_accounting}; darkHullBytes preserves the raw hull comparison\n")
        fh.write("# inCallersObserved is the count of distinct OBSERVED bodies that call into this region: high = cheap to identify\n")
        fh.write("\t".join(rcols) + "\n")
        for r in region_rows:
            fh.write("\t".join(
                (f"0x{r[c]:08x}" if c in ("startVa", "endVa") else str(r.get(c, ""))) for c in rcols
            ) + "\n")

    # --- executed-but-unmapped TSV -----------------------------------------
    with open(out_dir / "ledger-gaps.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " executed .text bytes claimed by NO function in the inventory\n")
        fh.write("# runs are boundary candidates, not a one-run/one-function count; adjacent runs may share an owner\n")
        fh.write("startVa\tendVa\tbytes\tprevFunc\tnextFunc\n")
        for a, b in sorted(exec_unmapped, key=lambda x: -(x[1] - x[0])):
            i = bisect_right(starts, a) - 1
            prev_name = rows[i]["name"] if 0 <= i < len(rows) else ""
            j = bisect_left(starts, b)
            next_name = rows[j]["name"] if 0 <= j < len(rows) else ""
            fh.write(f"0x{spec.image_base+a:08x}\t0x{spec.image_base+b:08x}\t{b-a}\t{prev_name}\t{next_name}\n")

    # --- all unmapped .text segments --------------------------------------
    unmapped_columns = [
        "entityKey", "startVa", "endVa", "bytes", "observedBytes",
        "observationState", "classification", "classificationVerdict",
        "terminalState", "bytePattern", "prevFunc", "nextFunc",
    ]
    with open(out_dir / "ledger-unmapped.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " complete .text residual accounting\n")
        fh.write(
            "# every byte outside authenticated Ghidra body fragments appears exactly once; "
            "dark padding-like bytes remain AMBIGUOUS until independently classified\n"
        )
        fh.write("\t".join(unmapped_columns) + "\n")
        for row in sorted(unmapped_rows, key=lambda item: item["startVa"]):
            fh.write("\t".join(
                f"0x{row[column]:08x}"
                if column in ("startVa", "endVa")
                else str(row.get(column, ""))
                for column in unmapped_columns
            ) + "\n")

    # --- finite Mission-native surface -------------------------------------
    native_columns = [
        "index", "recordVa", "handlerVa", "shippedName", "currentGhidraName",
        "registryStatus", "functionPresent", "observed", "terminalState",
        "needsBoundaryReview", "needsBehaviorContract",
    ]
    with open(out_dir / "ledger-native-handlers.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " MissionScript native handler ledger\n")
        fh.write("# denominator is the supplied registry; execution is bounded to this snapshot's coverage set\n")
        fh.write("# ENTRY_CONFIRMED_AND_SEMANTIC is never inferred from registry+coverage alone; a reviewed contract must earn it\n")
        fh.write("\t".join(native_columns) + "\n")
        for row in native_rows:
            fh.write("\t".join(
                (
                    f"0x{row[column]:08x}"
                    if column in ("recordVa", "handlerVa") else str(row.get(column, ""))
                )
                for column in native_columns
            ) + "\n")

    # --- family rollup TSV --------------------------------------------------
    with open(out_dir / "ledger-families.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " dark mass by class-name family\n")
        fh.write("# family is the token before '__' in the symbol; it is a naming convention, not a measured module boundary\n")
        fh.write("family\ttotalFuncs\ttotalBytes\tobservedBytes\tdarkFuncs\tdarkBytes\tdarkPctOfFamily\tinCallersObserved\tnoStaticRefFuncs\ttopReachClass\n")
        for fam, e in sorted(fam_rollup.items(), key=lambda kv: -kv[1]["darkBytes"]):
            pct = round(100.0 * e["darkBytes"] / e["totalBytes"], 2) if e["totalBytes"] else 0.0
            top = e["reach"].most_common(1)[0][0] if e["reach"] else "UNCLASSIFIED"
            fh.write(f"{fam}\t{e['totalFuncs']}\t{e['totalBytes']}\t{e['observedBytes']}\t{e['darkFuncs']}\t"
                     f"{e['darkBytes']}\t{pct}\t{e['inCallersObserved']}\t{e['noStaticRef']}\t{top}\n")

    print(f"[7/7] snapshot written to {out_dir}", file=sys.stderr)
    render_report(summary, region_rows, funcs, args.top)
    return 0


_cov_cache = {}


def CoverageIndexCacheGet(sid, runs):
    ci = _cov_cache.get(sid)
    if ci is None:
        ci = CoverageIndex(runs)
        _cov_cache[sid] = ci
    return ci


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def _pct(n, d):
    return f"{100.0*n/d:.4f}%" if d else "UNKNOWN"


def render_report(summary, region_rows, funcs, top):
    b = summary["bytes"]
    fx = summary["functions"]
    d = summary["denominators"]
    rr = summary["reachability"]
    body_method = d.get("bodyAccountingMethod", "BODY_MIN_MAX_HULLS")
    body_union = b.get("namedBodyUnion", b.get("namedHullUnion_UPPER_BOUND"))
    body_union_pct = b.get("namedBodyUnionPct", b.get("namedHullUnionPct_UPPER_BOUND"))

    print()
    print("=" * 78)
    print("RE COVERAGE / DISCOVERY LEDGER")
    print("=" * 78)
    print(f"generated       {summary['generatedAtUtc']}")
    print(f"specimen        {Path(summary['inputs']['specimen']['path']).name}  sha256 {summary['inputs']['specimen']['sha256'][:16]}…")
    print(f"name table      {Path(summary['inputs']['nameTable']['path']).name}  ({d['functionPopulation']:,} functions, as of {d['functionPopulationDate']})")
    print(f"coverage        {d['coverageIndexCount']} index(es)")
    print()
    print("-- BYTES ------------------------------------------------------------------")
    print(f"  .text denominator                  {d['textVirtualSizeBytes']:>12,}  (PE section header, virtual size)")
    print(f"  OBSERVED executing (union)         {b['observedUnion']:>12,}  {b['observedUnionPct']:.4f}%")
    print(f"  DARK (never observed)              {b['darkBytes']:>12,}  {b['darkPct']:.4f}%")
    if "darkBytesInsideNeverEnteredBodies" in b:
        print(f"    in bodies NEVER entered          {b['darkBytesInsideNeverEnteredBodies']:>12,}  {_pct(b['darkBytesInsideNeverEnteredBodies'], b['darkBytes'])} of dark")
        print(f"    branches not taken in bodies")
        print(f"      that DID execute               {b['darkBytesInsidePartiallyObservedBodies']:>12,}  {_pct(b['darkBytesInsidePartiallyObservedBodies'], b['darkBytes'])} of dark")
        print(f"    claimed by no function at all    {b['darkBytesClaimedByNoFunction']:>12,}  {_pct(b['darkBytesClaimedByNoFunction'], b['darkBytes'])} of dark")
        print(f"                                                   (these three sum exactly to DARK)")
    elif "darkBytesInsideKnownBodies" in b:
        print(f"    inside supplied function bodies {b['darkBytesInsideKnownBodies']:>12,}")
        print(f"    claimed by no function at all    {b['darkBytesClaimedByNoFunction']:>12,}")
    elif "darkBytesInsideAFunctionHull" in b:
        print(f"    inside a known function hull     {b['darkBytesInsideAFunctionHull']:>12,}")
        print(f"    claimed by no function at all    {b['darkBytesClaimedByNoFunction']:>12,}")
    body_label = "exact Ghidra body fragments" if body_method == "EXACT_GHIDRA_FRAGMENTS" else "function hulls (upper bound)"
    print(f"  claimed by {body_label:<26} {body_union:>12,}  {body_union_pct:.6f}%")
    if body_method == "EXACT_GHIDRA_FRAGMENTS":
        print(f"  hull comparison (upper bound)      {b['namedHullUnion_UPPER_BOUND']:>12,}  {b['namedHullUnionPct_UPPER_BOUND']:.4f}%")
    print(f"  claimed by NO function             {b['unmappedByAnyFunction']:>12,}  {b['unmappedByAnyFunctionPct']:.4f}%")
    print(f"    of which bytes are CC/90/00      {b['unmappedBytesEqualToCC90or00']:>12,}  (byte tally, not a run analysis)")
    print(f"  EXECUTED but unmapped              {b['executedButUnmapped']:>12,}  in {b['executedButUnmappedRuns']} candidate runs")
    exact_total = d.get("exactBodyByteTotal", d.get("exactCurrentBodyByteTotal", "UNKNOWN"))
    if isinstance(exact_total, int):
        print(f"  exact supplied body-byte total     {exact_total:>12,}  (dated export; not unexported live state)")
    else:
        print(f"  exact supplied body-byte total     {'UNKNOWN':>12}  (supply a parity-graph READY receipt)")
    print()
    print("-- FUNCTIONS --------------------------------------------------------------")
    print(f"  population (denominator)           {fx['population']:>12,}")
    print(f"  OBSERVED executing                 {fx['observed']:>12,}  {fx['observedPct']:.4f}%")
    fully_covered = fx.get("fullyCovered", fx.get("fullyCovered_conservative", 0))
    fully_label = "exact fragments" if body_method == "EXACT_GHIDRA_FRAGMENTS" else "conservative hull"
    print(f"    fully covered ({fully_label})    {fully_covered:>12,}")
    if body_method == "EXACT_GHIDRA_FRAGMENTS":
        print(f"    fully covered (whole hull too)   {fx.get('fullyCovered_conservativeHull', 0):>12,}")
    print(f"    partially covered                {fx['partial']:>12,}")
    print(f"  DARK                               {fx['dark']:>12,}  {fx['darkPct']:.4f}%")
    print(f"  dark accounted body bytes          {fx.get('darkBodyBytes', fx['darkHullBytes']):>12,}")
    print(f"  dark hull comparison               {fx['darkHullBytes']:>12,}")
    print()
    print(f"  human-named                        {fx['humanNamed']:>12,}  {fx['humanNamedPctOfNamableDenom']:.4f}% of {d['humanNamableDenominator']:,} namable")
    for k, v in sorted(fx["byNameClass"].items(), key=lambda kv: -kv[1]):
        print(f"    {k:<22}                {v:>10,}")
    print()
    print("-- SEMANTIC EVIDENCE PROXY (coverage is not behavior) ----------------------")
    u = summary["understanding"]
    for k in (
        "U3_REVIEWED_RUNTIME_CONTRACT",
        "U3_RUNTIME_BEHAVIOUR",  # legacy snapshots only
        "U2_ADDRESS_CITED",
        "U1b_BULK_REVIEWED",
        "U1_NAMED_ONLY",
        "U0_NONE",
    ):
        if k in u:
            print(f"  {k:<32}     {u.get(k,0):>10,}")
    print()
    nx = summary.get("nativeCrossCheck")
    if nx:
        print("-- MISSION NATIVE EXECUTION CROSS-CHECK -----------------------------------")
        print(f"  registry rows                      {nx['registryRows']:>12,}")
        print(f"  handler first byte OBSERVED        {nx['handlerFirstByteObserved']:>12,}")
        print(f"  handlers that are Ghidra entries   {nx['handlersAtAGhidraFunctionEntry']:>12,}")
        canary = nx.get("canary")
        if canary:
            print(f"  input-bound canary                 {canary.get('status', 'UNKNOWN'):>12}")
        else:
            print(f"  input-bound canary                 {'LEGACY/NONE':>12}")
        print("  No universal expected hit count is applied to arbitrary augmented inputs.")
        print()
    print("-- OBSERVED BUT UNNAMED (cheapest naming targets) --------------------------")
    print(f"  {fx['observedAndUnnamed']:,} functions executed with no human name")
    cand = sorted(
        (f for f in funcs if f["execState"] != "DARK" and f["nameClass"] in UNNAMED_CLASSES),
        key=lambda f: -f["observedBytes"],
    )[:top]
    for f in cand:
        denominator = f.get("bodyBytes", f["hullBytes"])
        print(f"    0x{f['va']:08x}  {f['observedBytes']:>7,}b obs / {denominator:>7,}b  "
              f"callers-obs={f.get('inCallersObserved',0):<3} ptr={f.get('ptrRefs',0):<3} imm={f.get('immRefs',0):<3} {f['name']}")
    print()
    print("-- DARK REGIONS ranked by size --------------------------------------------")
    print(f"  {'startVa':<12}{'bytes':>9} {'fns':>5} {'obsCallers':>11}  reach / families")
    for r in region_rows[:top]:
        print(f"  0x{r['startVa']:08x}{r['darkBytes']:>11,} {r['funcCount']:>5} {r['inCallersObserved']:>11}  "
              f"{r['topReachClass']}  {r['topFamilies'][:56]}")
    print()
    print("-- DARK REGIONS ranked by adjacency to observed code (cheapest first) ------")
    for r in sorted(region_rows, key=lambda x: (-x["inCallersObserved"], -x["darkBytes"]))[:top]:
        print(f"  0x{r['startVa']:08x}{r['darkBytes']:>11,} {r['funcCount']:>5} obsCallers={r['inCallersObserved']:<5} "
              f"{r['topReachClass']}  {r['topFamilies'][:48]}")
    print()
    print("-- REACHABILITY OF THE DARK MASS (name heuristic; INFERRED) ----------------")
    byte_label = "exact body bytes" if body_method == "EXACT_GHIDRA_FRAGMENTS" else "body bytes (est)"
    print(f"  dark functions                     {rr['darkFunctionCount']:>12,}   {rr.get('darkBodyBytes', rr.get('darkBodyBytesEstimate', rr['darkHullBytes'])):>12,} {byte_label}")
    print(f"  with an OBSERVED caller            {rr['darkWithObservedCaller']:>12,}   {rr['darkWithObservedCallerBytes']:>12,} bytes  << cheap")
    print(f"  reachable only via a vtable        {rr.get('darkVtableOnly',0):>12,}   {rr.get('darkVtableOnlyBytes',0):>12,} bytes  << needs the object type")
    print(f"  with NO static reference at all    {rr['darkWithNoStaticRefAtAll']:>12,}   {rr['darkWithNoStaticRefBytes']:>12,} bytes  << candidate-unreachable")
    print(f"  in a hard class {sorted(REACH_HARD)}")
    print(f"                                     {rr['hardClassFuncs']:>12,}   {rr['hardClassBytes']:>12,} bytes")
    print()
    print(f"  {'class':<20}{'darkFuncs':>10}{'darkBytes':>14}")
    for k, v in list(rr["byClass"].items()):
        print(f"  {k:<20}{v['funcs']:>10,}{v.get('darkBytes', v['darkHullBytes']):>14,}")
    unc = sorted(
        ((f["family"], f) for f in funcs if f["execState"] == "DARK" and f["reachClass"] == "UNCLASSIFIED"),
        key=lambda kv: kv[0],
    )
    if unc:
        agg = Counter()
        for fam, f in unc:
            agg[fam] += int(f.get("bodyBytes") or f.get("bodyBytesEstimate") or f.get("hullBytes") or 0)
        print()
        print("  largest UNCLASSIFIED dark families (the classifier's blind spot -- fix these first):")
        for k, v in agg.most_common(10):
            print(f"    {k:<40}{v:>10,}")
    print()
    print("REMINDERS")
    for line in summary["readingRules"]:
        print(f"  - {line}")
    print("=" * 78)


HEX_COLUMNS = {"va", "entryRva", "startVa", "endVa"}


def _coerce(rec):
    """Convert every column that is plainly numeric.

    Doing this generically rather than from a hand-maintained list: an earlier
    version listed the columns to convert and silently missed `darkBytes`, which
    then crashed the report formatter the moment a snapshot was re-read from
    disk instead of rendered in-process.
    """
    out = {}
    for k, v in rec.items():
        if k in HEX_COLUMNS:
            out[k] = int(v, 16) if v else 0
            continue
        if v in ("True", "False"):
            out[k] = v == "True"
            continue
        try:
            out[k] = int(v)
        except (TypeError, ValueError):
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                out[k] = v
    return out


def _read_tsv(path: Path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        hdr = None
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            if hdr is None:
                hdr = f
                continue
            rows.append(_coerce(dict(zip(hdr, f))))
    return rows


def report(args) -> int:
    snap = Path(args.snapshot)
    try:
        verify_snapshot(snap)
    except LedgerInputError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2
    summary = json.loads((snap / "ledger-summary.json").read_text(encoding="utf-8"))
    funcs = _read_tsv(snap / "ledger-functions.tsv")
    regions = _read_tsv(snap / "ledger-dark.tsv")
    render_report(summary, regions, funcs, args.top)
    return 0


# ---------------------------------------------------------------------------
# Delta: what did a probe actually buy?
# ---------------------------------------------------------------------------


def _load_funcs(snap: Path):
    return {r["va"]: r for r in _read_tsv(snap / "ledger-functions.tsv")}


def delta(args) -> int:
    a_dir, b_dir = Path(args.before), Path(args.after)
    try:
        verify_snapshot(a_dir)
        verify_snapshot(b_dir)
    except LedgerInputError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2
    a = json.loads((a_dir / "ledger-summary.json").read_text(encoding="utf-8"))
    b = json.loads((b_dir / "ledger-summary.json").read_text(encoding="utf-8"))
    af, bf = _load_funcs(a_dir), _load_funcs(b_dir)

    a_src = {s["sourceId"] for s in a["sources"]}
    b_src = {s["sourceId"] for s in b["sources"]}
    added_src = sorted(b_src - a_src)
    removed_src = sorted(a_src - b_src)

    same_pop = a["denominators"]["functionPopulation"] == b["denominators"]["functionPopulation"]
    same_names = a["inputs"]["nameTable"]["sha256"] == b["inputs"]["nameTable"]["sha256"]
    a_graph = ((a.get("inputs", {}).get("parityGraph") or {}).get("bodyRanges") or {}).get("sha256")
    b_graph = ((b.get("inputs", {}).get("parityGraph") or {}).get("bodyRanges") or {}).get("sha256")
    same_bodies = a_graph == b_graph and a["denominators"].get("bodyAccountingMethod") == b["denominators"].get("bodyAccountingMethod")

    d_bytes = b["bytes"]["observedUnion"] - a["bytes"]["observedUnion"]
    d_funcs = b["functions"]["observed"] - a["functions"]["observed"]

    flipped = []
    deepened = []
    for va, bv in bf.items():
        av = af.get(va)
        if av is None:
            continue
        if av["execState"] == "DARK" and bv["execState"] != "DARK":
            flipped.append(bv)
        elif bv["observedBytes"] > av["observedBytes"]:
            deepened.append((bv, bv["observedBytes"] - av["observedBytes"]))
    new_funcs = [bv for va, bv in bf.items() if va not in af]
    gone_funcs = [av for va, av in af.items() if va not in bf]

    new_body_bytes = sum(f.get("bodyBytes", f["hullBytes"]) for f in flipped)
    deeper_bytes = sum(dv for _f, dv in deepened)

    print("=" * 78)
    print("LEDGER DELTA")
    print("=" * 78)
    print(f"  before  {a_dir}   {a['generatedAtUtc']}")
    print(f"  after   {b_dir}   {b['generatedAtUtc']}")
    print()
    if not same_names:
        print("  !! NAME TABLE CHANGED between snapshots. Function-level deltas below mix")
        print("     'the probe found new code' with 'the inventory grew'. Read new/removed")
        print("     function counts before trusting any coverage delta.")
    if not same_pop:
        print(f"  !! population {a['denominators']['functionPopulation']:,} -> {b['denominators']['functionPopulation']:,}")
    if not same_bodies:
        print("  !! BODY ACCOUNTING CHANGED between snapshots. Function-byte deltas are not comparable.")
    print(f"  coverage indexes added   : {', '.join(added_src) if added_src else '(none)'}")
    print(f"  coverage indexes removed : {', '.join(removed_src) if removed_src else '(none)'}")
    print()
    print("-- WHAT THE PROBE BOUGHT ---------------------------------------------------")
    print(f"  observed .text bytes     {a['bytes']['observedUnion']:>12,} -> {b['bytes']['observedUnion']:>12,}   {d_bytes:+,}")
    print(f"  observed .text %         {a['bytes']['observedUnionPct']:>12.4f} -> {b['bytes']['observedUnionPct']:>12.4f}   {b['bytes']['observedUnionPct']-a['bytes']['observedUnionPct']:+.4f} pp")
    print(f"  observed functions       {a['functions']['observed']:>12,} -> {b['functions']['observed']:>12,}   {d_funcs:+,}")
    print(f"  executed-but-unmapped    {a['bytes']['executedButUnmapped']:>12,} -> {b['bytes']['executedButUnmapped']:>12,}   {b['bytes']['executedButUnmapped']-a['bytes']['executedButUnmapped']:+,}")
    print()
    unit = "exact body bytes" if b["denominators"].get("bodyAccountingMethod") == "EXACT_GHIDRA_FRAGMENTS" else "estimated body bytes"
    print(f"  NEW BODIES lit (DARK -> observed) : {len(flipped):,} functions, {new_body_bytes:,} {unit}")
    print(f"  DEEPER penetration of known bodies: {len(deepened):,} functions, {deeper_bytes:,} extra bytes")
    print("  (the first number is the one that matters: it is new territory, not a longer")
    print("   walk through territory you already had)")
    if new_funcs or gone_funcs:
        print(f"  inventory churn: {len(new_funcs):,} functions added, {len(gone_funcs):,} removed")
    print()
    print(f"-- TOP {args.top} NEWLY-LIT BODIES ------------------------------------------------")
    for f in sorted(flipped, key=lambda x: -x.get("bodyBytes", x["hullBytes"]))[: args.top]:
        size = f.get("bodyBytes", f["hullBytes"])
        print(f"  0x{f['va']:08x}  {size:>7,}b  {f['nameClass']:<14} {f['reachClass']:<16} {f['name']}")
    if not flipped:
        print("  (none -- this probe lit no body that was previously dark)")
    print()
    fam = Counter()
    for f in flipped:
        fam[f["family"]] += f.get("bodyBytes", f["hullBytes"])
    if fam:
        print("-- NEWLY-LIT BYTES BY FAMILY ----------------------------------------------")
        for k, v in fam.most_common(args.top):
            print(f"  {k:<40}{v:>10,}")
    print()
    print("READING RULE: a byte that did not appear here is NON-OBSERVED, not absent.")
    print("=" * 78)
    return 0


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="re_coverage_ledger.py",
        description="Function-granularity coverage / discovery ledger for BEA.exe .text",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="compute a ledger snapshot")
    b.add_argument("--out", required=True, help="snapshot output directory")
    b.add_argument("--specimen", default=str(DEFAULT_SPECIMEN))
    b.add_argument("--names", default=str(DEFAULT_NAMES))
    b.add_argument("--natives", default=str(DEFAULT_NATIVES))
    exact = b.add_mutually_exclusive_group()
    exact.add_argument(
        "--parity-graph",
        default=str(DEFAULT_PARITY_GRAPH) if DEFAULT_PARITY_GRAPH.is_file() else None,
        help=(
            "ExportParityLabGraph READY receipt; exact body fragments are hash-checked against "
            "the specimen and must match the name-table population"
        ),
    )
    exact.add_argument(
        "--no-exact-bodies",
        action="store_true",
        help="deliberately fall back to bodyMin..bodyMax hull accounting",
    )
    b.add_argument(
        "--native-canary",
        help=(
            "optional JSON expectation bound to the exact coverage-set and native-registry hashes; "
            "there is no universal expected hit count"
        ),
    )
    b.add_argument("--coverage-root", action="append", help="directory scanned recursively for coverage.jsonl (repeatable)")
    b.add_argument("--coverage-index", action="append", help="a single coverage.jsonl (repeatable)")
    b.add_argument("--evidence-root", action="append", help="directory scanned for entry-address citations (repeatable)")
    b.add_argument("--skip-evidence", action="store_true", help="skip the citation scan (faster; U2 tier becomes 0)")
    b.add_argument("--skip-static-refs", action="store_true", help="skip the static reference scan (adjacency becomes 0)")
    b.add_argument("--per-source", action="store_true", help="record per-function how many indexes hit it (slower)")
    b.add_argument("--region-gap", type=int, default=64, help="merge dark functions separated by <= this many bytes")
    b.add_argument("--inventory-threshold", type=int, default=EVIDENCE_INVENTORY_THRESHOLD,
                   help="an evidence file mentioning more than this many distinct .text addresses is an "
                        "inventory dump and is excluded from citation counting")
    b.add_argument("--top", type=int, default=25)
    b.add_argument("--allow-specimen-mismatch", action="store_true")
    b.set_defaults(func=build)

    r = sub.add_parser("report", help="print the headline report from a snapshot")
    r.add_argument("--snapshot", required=True)
    r.add_argument("--top", type=int, default=25)
    r.set_defaults(func=report)

    dl = sub.add_parser("delta", help="what did a probe buy: compare two snapshots")
    dl.add_argument("--before", required=True)
    dl.add_argument("--after", required=True)
    dl.add_argument("--top", type=int, default=25)
    dl.set_defaults(func=delta)

    v = sub.add_parser("verify", help="verify an atomic READY snapshot")
    v.add_argument("--snapshot", required=True)

    def verify_command(args) -> int:
        try:
            receipt = verify_snapshot(Path(args.snapshot))
        except LedgerInputError as exc:
            print(f"FATAL: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(receipt, indent=2))
        return 0

    v.set_defaults(func=verify_command)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
