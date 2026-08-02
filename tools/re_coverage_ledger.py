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
   This tool never reproduces, rolls forward, or approximates it. What it emits
   instead is a 7,555-body *hull* union explicitly labelled an UPPER BOUND,
   because the name table carries bodyMin/bodyMax hulls and 67 bodies are
   non-contiguous. The exact current body-byte total is UNKNOWN until a fresh
   per-instruction interval export exists.
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
import struct
import sys
from bisect import bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "bea.re.coverage-ledger.v1"

REPO = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Defaults. Every one of these is overridable on the command line; they are the
# measured locations as of 2026-08-02 and are recorded into the snapshot.
# ---------------------------------------------------------------------------

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

DEFAULT_SPECIMEN = REPO / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
DEFAULT_NAMES = REPO / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv"
DEFAULT_NATIVES = REPO / "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv"

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


def load_name_table(path: Path):
    rows = []
    header_lines = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                header_lines.append(line.rstrip("\n"))
                continue
            if line.startswith("address\t"):
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) < 4:
                continue
            try:
                addr = int(f[0], 16)
                lo = int(f[2], 16)
                hi = int(f[3], 16)
            except ValueError:
                continue
            rows.append({"va": addr, "name": f[1], "hullLoVa": lo, "hullHiVa": hi})
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
                handler = int(f[2], 16)
            except ValueError:
                continue
            out[handler] = {
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
    print(f"      union observed .text = {observed_bytes:,} bytes ({100*observed_bytes/text_size:.4f}%)", file=sys.stderr)

    # --- name table --------------------------------------------------------
    names_path = Path(args.names)
    rows, name_header = load_name_table(names_path)
    names_stamp = file_stamp(names_path)
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
    unmapped = subtract([(text_lo, text_hi)], hull_union)
    unmapped_bytes = total(unmapped)

    # --- natives, evidence, static refs ------------------------------------
    natives, natives_stamp = load_natives(Path(args.natives) if args.natives else None)
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

    def containing(rva):
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
        obs = union.covered_in(lo, hi) if text_lo <= lo < text_hi else 0
        nc = name_class(r["name"])
        nat = natives.get(r["va"])
        cited = cite_counts.get(r["va"], 0)
        hit_sources = [sid for sid, runs in per_source_runs.items()
                       if CoverageIndexCacheGet(sid, runs).covered_in(lo, hi) > 0] if args.per_source else []
        # Tighter of two upper bounds on body size: the bodyMin..bodyMax hull,
        # and the distance to the next function entry. Both over-count (padding,
        # non-contiguity); neither under-counts a contiguous body.
        next_lo = rows[idx + 1]["lo"] if idx + 1 < len(rows) else None
        span_next = (next_lo - lo) if (next_lo is not None and next_lo > lo) else None
        body_est = min(r["hullBytes"], span_next) if span_next else r["hullBytes"]
        funcs.append(
            {
                "va": r["va"],
                "name": r["name"],
                "lo": lo,
                "hi": hi,
                "hullBytes": r["hullBytes"],
                "spanToNextEntry": span_next if span_next is not None else "",
                "bodyBytesEstimate": body_est,
                "hullSuspect": r["hullBytes"] > HULL_SUSPECT_BYTES,
                "nameClass": nc,
                "observedBytes": obs,
                "observedPctOfHull": round(100.0 * obs / r["hullBytes"], 4) if r["hullBytes"] else 0.0,
                "execState": "DARK" if obs == 0 else ("COVERED" if obs >= r["hullBytes"] else "PARTIAL"),
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
        # understanding tier
        if f["nativeShippedName"] and f["nativeRegistryStatus"] != "CONTRADICTED" and f["observedBytes"] > 0:
            f["understoodTier"] = "U3_RUNTIME_BEHAVIOUR"
        elif f["citationCountFocused"] > 0:
            f["understoodTier"] = "U2_ADDRESS_CITED"
        elif f["citationCount"] > 0:
            f["understoodTier"] = "U1b_BULK_REVIEWED"
        elif f["nameClass"] in HUMAN_NAMED_CLASSES:
            f["understoodTier"] = "U1_NAMED_ONLY"
        else:
            f["understoodTier"] = "U0_NONE"
        # cheapness of identifying a dark body from observed neighbours.
        # Components are all present as their own columns; this is a sort key,
        # not a claim.
        f["adjacencyScore"] = f["inCallersObserved"] * 4 + f["inCallersNamed"] * 2 + min(f["ptrRefs"], 8)

    # --- reconcile the dark byte mass ---------------------------------------
    # These two DO sum exactly to the dark byte total, unlike the dark-function
    # hull sum, which double-counts overlapping hulls and over-counts
    # non-contiguous bodies. Printing the reconciliation stops a reader
    # equating "dark function bytes" with "dark .text bytes".
    unobserved = subtract([(text_lo, text_hi)], union_runs)
    unobserved_in_hulls = total(
        [(max(a, ha), min(b, hb)) for (ha, hb) in hull_union for (a, b) in unobserved
         if min(b, hb) > max(a, ha)]
    )
    unobserved_unmapped = total(unobserved) - unobserved_in_hulls

    # The three-way split the reachability question actually turns on.
    # Dark bytes inside a PARTIALLY observed body are branches not taken in a
    # function the process has already entered -- a different problem entirely
    # from a body that never ran. Computed against merged hulls per class so
    # overlapping hulls cannot double-count.
    dark_hulls = merge(clip([(f["lo"], f["hi"]) for f in funcs if f["execState"] == "DARK"], text_lo, text_hi))
    partial_hulls = merge(clip([(f["lo"], f["hi"]) for f in funcs if f["execState"] == "PARTIAL"], text_lo, text_hi))
    dark_in_dark_bodies = total(
        [(max(a, ha), min(b, hb)) for (ha, hb) in dark_hulls for (a, b) in unobserved
         if min(b, hb) > max(a, ha)]
    )
    partial_dark_raw = total(
        [(max(a, ha), min(b, hb)) for (ha, hb) in partial_hulls for (a, b) in unobserved
         if min(b, hb) > max(a, ha)]
    )
    # A byte can sit in both a dark hull and a partial hull where hulls overlap.
    # Attribute such bytes to the partial side only, so the three parts sum.
    dark_in_partial_bodies = max(0, unobserved_in_hulls - dark_in_dark_bodies)
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
                "darkBytes": sum(x["bodyBytesEstimate"] for x in fs),
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
                "largestFunc": max(fs, key=lambda x: x["bodyBytesEstimate"])["name"],
                "largestFuncBytes": max(x["bodyBytesEstimate"] for x in fs),
            }
        )
    region_rows.sort(key=lambda x: -x["darkBytes"])

    # --- family rollup (dark mass by class family) --------------------------
    fam_rollup = defaultdict(lambda: {"darkBytes": 0, "darkFuncs": 0, "totalBytes": 0, "totalFuncs": 0,
                                      "observedBytes": 0, "inCallersObserved": 0, "noStaticRef": 0,
                                      "reach": Counter()})
    for f in funcs:
        e = fam_rollup[f["family"]]
        e["totalBytes"] += f["hullBytes"]
        e["totalFuncs"] += 1
        e["observedBytes"] += f["observedBytes"]
        e["reach"][f["reachClass"]] += 1
        if f["execState"] == "DARK":
            e["darkBytes"] += f["hullBytes"]
            e["darkFuncs"] += 1
            e["inCallersObserved"] += f["inCallersObserved"]
            if f["noStaticRef"]:
                e["noStaticRef"] += 1

    # --- reachability accounting -------------------------------------------
    dark_funcs = [f for f in funcs if f["execState"] == "DARK"]
    dark_hull_bytes = sum(f["hullBytes"] for f in dark_funcs)
    dark_body_bytes = sum(f["bodyBytesEstimate"] for f in dark_funcs)

    reach_buckets = defaultdict(lambda: {"funcs": 0, "darkBytes": 0, "darkHullBytes": 0})
    for f in dark_funcs:
        b = reach_buckets[f["reachClass"]]
        b["funcs"] += 1
        b["darkBytes"] += f["bodyBytesEstimate"]
        b["darkHullBytes"] += f["hullBytes"]

    dark_no_ref = [f for f in dark_funcs if f["noStaticRef"]]
    dark_no_ref_bytes = sum(f["bodyBytesEstimate"] for f in dark_no_ref)
    dark_reachable_from_observed = [f for f in dark_funcs if f["inCallersObserved"] > 0]
    dark_reachable_bytes = sum(f["bodyBytesEstimate"] for f in dark_reachable_from_observed)
    dark_vtable_only = [f for f in dark_funcs if f["vtableOnly"]]
    dark_vtable_only_bytes = sum(f["bodyBytesEstimate"] for f in dark_vtable_only)

    hard_bytes = sum(v["darkBytes"] for k, v in reach_buckets.items() if k in REACH_HARD)
    hard_funcs = sum(v["funcs"] for k, v in reach_buckets.items() if k in REACH_HARD)

    # --- headline numbers ---------------------------------------------------
    n_funcs = len(funcs)
    n_unwind = sum(1 for f in funcs if f["nameClass"] == "UNWIND")
    human_denom = n_funcs - n_unwind
    by_exec = Counter(f["execState"] for f in funcs)
    by_name = Counter(f["nameClass"] for f in funcs)
    by_understood = Counter(f["understoodTier"] for f in funcs)

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
            "DARK is exact: a real body is a subset of its hull, so a hull with zero observed bytes had a body with zero observed bytes.",
            "COVERED is conservative: it requires 100% of the bodyMin..bodyMax hull, which over-covers 67 non-contiguous bodies.",
            "Hull-union byte totals are UPPER BOUNDS on named-body bytes, not measurements of them.",
            "The historical 79.8268% .text figure is a DATED 6,411-body measurement and is NOT reproduced here.",
            "No step or instruction counter was read from any receipt (task #149).",
            "The static call graph is a byte-pattern superset, not a disassembly.",
            "UNDERSTOOD tiers are citation/registry proxies. Citation is not correctness.",
        ],
        "denominators": {
            "textVirtualSizeBytes": text_size,
            "textRvaHalfOpen": [f"0x{text_lo:x}", f"0x{text_hi:x}"],
            "textSource": "PE section header of the specimen named in inputs.specimen",
            "functionPopulation": n_funcs,
            "functionPopulationSource": str(names_path),
            "functionPopulationDate": "2026-07-27 (name table export date; do not treat as today's live DB)",
            "humanNamableDenominator": human_denom,
            "humanNamableNote": f"{n_funcs} functions minus {n_unwind} MSVC Unwind@ EH funclets",
            "coverageIndexCount": len(sources),
            "nativeRegistryPopulation": len(natives),
            "exactCurrentBodyByteTotal": "UNKNOWN -- requires a fresh per-instruction interval export of the live inventory",
        },
        "inputs": {
            "specimen": spec_stamp,
            "nameTable": names_stamp,
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
            "darkBytesInsideAFunctionHull": unobserved_in_hulls,
            "darkBytesClaimedByNoFunction": unobserved_unmapped,
            "darkBytesInsideNeverEnteredBodies": dark_in_dark_bodies,
            "darkBytesInsidePartiallyObservedBodies": dark_in_partial_bodies,
            "darkThreeWaySplitNote": (
                "darkBytesInsideNeverEnteredBodies + darkBytesInsidePartiallyObservedBodies + "
                "darkBytesClaimedByNoFunction == darkBytes. The middle term is branches not taken in a "
                "function the process ALREADY entered -- a different and much easier problem than a body "
                "that never ran. Bytes lying in both a dark and a partial hull (hull overlap, "
                f"{partial_overlap_note} bytes) are attributed to the partial side so the parts sum."
            ),
            "darkReconciliationNote": (
                "darkBytesInsideAFunctionHull + darkBytesClaimedByNoFunction == darkBytes. The dark-FUNCTION "
                "hull sum in functions.darkHullBytes does not, because hulls overlap and over-cover; do not "
                "equate the two."
            ),
            "namedHullUnion_UPPER_BOUND": hull_union_bytes,
            "namedHullUnionPct_UPPER_BOUND": round(100.0 * hull_union_bytes / text_size, 4),
            "namedHullUnionCaveat": (
                "UPPER BOUND. bodyMin..bodyMax hulls over-cover 67 non-contiguous bodies and "
                f"{overlapping} spans overlap their predecessor. This is NOT comparable to the "
                "dated 6,411-body 79.8268% figure and must not be presented as its successor."
            ),
            "unmappedByAnyFunction": unmapped_bytes,
            "unmappedByAnyFunctionPct": round(100.0 * unmapped_bytes / text_size, 4),
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
            "executedButUnmappedNote": "Bytes proven to execute that no current Ghidra function claims. Each run is a missing function.",
        },
        "functions": {
            "population": n_funcs,
            "observed": len(observed_funcs),
            "observedPct": round(100.0 * len(observed_funcs) / n_funcs, 4),
            "dark": by_exec.get("DARK", 0),
            "darkPct": round(100.0 * by_exec.get("DARK", 0) / n_funcs, 4),
            "fullyCovered_conservative": by_exec.get("COVERED", 0),
            "partial": by_exec.get("PARTIAL", 0),
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
            "U3_RUNTIME_BEHAVIOUR": by_understood.get("U3_RUNTIME_BEHAVIOUR", 0),
            "U3_definition": "script-native registry binding (not CONTRADICTED) whose bytes also executed",
            "U3_blockedByMissingGhidraFunction": natives_hit - sum(
                1 for h, v in natives_observed.items()
                if v and (h - spec.image_base) in {r["lo"] for r in rows}
            ),
            "U3_blockedNote": (
                "Handlers observed executing that Ghidra has no function for, so they cannot appear in "
                "the per-function table at all. Creating those bodies converts them to U3 for free."
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
            "caveat": "These are proxies for understanding, not measurements of it. A citation can be wrong.",
        },
        "nativeCrossCheck": {
            "registryRows": len(natives),
            "handlersAtAGhidraFunctionEntry": sum(1 for h in natives if (h - spec.image_base) in {r["lo"] for r in rows}),
            "handlerFirstByteObserved": natives_hit,
            "handlerFirstByteObservedExcludingContradicted": natives_hit_uncontradicted,
            "note": (
                "Byte-level test at the handler VA, independent of whether Ghidra has a function there. "
                "Over the 66-level campaign this should reproduce the independently verified 60-hit / "
                "59-real figure from local-lab/TTD-CORPUS-ANALYSIS-2026-07-31.md. A disagreement means "
                "this tool is wrong or the input set changed -- investigate before trusting anything above."
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
        "va", "name", "nameClass", "execState", "understoodTier", "reachClass", "family",
        "hullBytes", "bodyBytesEstimate", "spanToNextEntry", "hullSuspect",
        "observedBytes", "observedPctOfHull", "citationCount", "citationCountFocused", "citingDocs",
        "nativeShippedName", "nativeRegistryStatus",
        "inCallSites", "inCallers", "inCallersObserved", "inCallersNamed",
        "ptrRefs", "immRefs", "staticRefTotal", "noStaticRef", "vtableOnly", "adjacencyScore",
    ]
    with open(out_dir / "ledger-functions.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " per-function ledger\n")
        fh.write(f"# denominator: {n_funcs} functions from {names_path.name} (export date 2026-07-27)\n")
        fh.write(f"# .text {text_size} bytes; union observed {observed_bytes} bytes over {len(sources)} coverage index(es)\n")
        fh.write("# hullBytes is bodyMin..bodyMax and OVER-COVERS non-contiguous bodies. DARK is exact; COVERED is conservative.\n")
        fh.write("\t".join(fcols) + "\n")
        for f in sorted(funcs, key=lambda x: x["va"]):
            fh.write("\t".join(
                (f"0x{f['va']:08x}" if c == "va" else str(f.get(c, ""))) for c in fcols
            ) + "\n")

    # --- dark regions TSV ---------------------------------------------------
    rcols = ["startVa", "endVa", "spanBytes", "darkBytes", "darkHullBytes", "funcCount", "hullSuspectFuncs",
             "namedCount", "unnamedCount",
             "inCallersObserved", "inCallersTotal", "ptrRefs", "immRefs", "noStaticRefFuncs", "vtableOnlyFuncs",
             "topReachClass", "reachMix", "topFamilies", "largestFunc", "largestFuncBytes"]
    with open(out_dir / "ledger-dark.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " dark regions, ranked by darkBytes\n")
        fh.write(f"# a region is a run of consecutive DARK functions with gaps <= {args.region_gap} bytes\n")
        fh.write("# darkBytes sums bodyBytesEstimate = min(hull, distance-to-next-entry); darkHullBytes sums the raw hulls\n")
        fh.write("# inCallersObserved is the count of distinct OBSERVED bodies that call into this region: high = cheap to identify\n")
        fh.write("\t".join(rcols) + "\n")
        for r in region_rows:
            fh.write("\t".join(
                (f"0x{r[c]:08x}" if c in ("startVa", "endVa") else str(r.get(c, ""))) for c in rcols
            ) + "\n")

    # --- executed-but-unmapped TSV -----------------------------------------
    with open(out_dir / "ledger-gaps.tsv", "w", encoding="utf-8", newline="") as fh:
        fh.write("# " + SCHEMA + " executed .text bytes claimed by NO function in the inventory\n")
        fh.write("# each run is a missing function: bytes proven to run that Ghidra has no body for\n")
        fh.write("startVa\tendVa\tbytes\tprevFunc\tnextFunc\n")
        for a, b in sorted(exec_unmapped, key=lambda x: -(x[1] - x[0])):
            i = bisect_right(starts, a) - 1
            prev_name = rows[i]["name"] if 0 <= i < len(rows) else ""
            j = bisect_right(starts, b)
            next_name = rows[j]["name"] if 0 <= j < len(rows) else ""
            fh.write(f"0x{spec.image_base+a:08x}\t0x{spec.image_base+b:08x}\t{b-a}\t{prev_name}\t{next_name}\n")

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

    print()
    print("=" * 78)
    print("RE COVERAGE / DISCOVERY LEDGER")
    print("=" * 78)
    print(f"generated       {summary['generatedAtUtc']}")
    print(f"specimen        {Path(summary['inputs']['specimen']['path']).name}  sha256 {summary['inputs']['specimen']['sha256'][:16]}…")
    print(f"name table      {Path(summary['inputs']['nameTable']['path']).name}  ({d['functionPopulation']:,} functions, export {d['functionPopulationDate']})")
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
    elif "darkBytesInsideAFunctionHull" in b:
        print(f"    inside a known function hull     {b['darkBytesInsideAFunctionHull']:>12,}")
        print(f"    claimed by no function at all    {b['darkBytesClaimedByNoFunction']:>12,}")
    print(f"  claimed by a function hull         {b['namedHullUnion_UPPER_BOUND']:>12,}  {b['namedHullUnionPct_UPPER_BOUND']:.4f}%   << UPPER BOUND")
    print(f"  claimed by NO function             {b['unmappedByAnyFunction']:>12,}  {b['unmappedByAnyFunctionPct']:.4f}%")
    print(f"    of which bytes are CC/90/00      {b['unmappedBytesEqualToCC90or00']:>12,}  (byte tally, not a run analysis)")
    print(f"  EXECUTED but unmapped              {b['executedButUnmapped']:>12,}  in {b['executedButUnmappedRuns']} runs  << missing functions")
    print(f"  exact current body-byte total      {'UNKNOWN':>12}  (needs a fresh interval export)")
    print()
    print("-- FUNCTIONS --------------------------------------------------------------")
    print(f"  population (denominator)           {fx['population']:>12,}")
    print(f"  OBSERVED executing                 {fx['observed']:>12,}  {fx['observedPct']:.4f}%")
    print(f"    fully covered (conservative)     {fx['fullyCovered_conservative']:>12,}")
    print(f"    partially covered                {fx['partial']:>12,}")
    print(f"  DARK                               {fx['dark']:>12,}  {fx['darkPct']:.4f}%")
    print(f"  dark hull bytes                    {fx['darkHullBytes']:>12,}")
    print()
    print(f"  human-named                        {fx['humanNamed']:>12,}  {fx['humanNamedPctOfNamableDenom']:.4f}% of {d['humanNamableDenominator']:,} namable")
    for k, v in sorted(fx["byNameClass"].items(), key=lambda kv: -kv[1]):
        print(f"    {k:<22}                {v:>10,}")
    print()
    print("-- UNDERSTOOD (proxy tiers; citation is not correctness) -------------------")
    u = summary["understanding"]
    for k in ("U3_RUNTIME_BEHAVIOUR", "U2_ADDRESS_CITED", "U1b_BULK_REVIEWED", "U1_NAMED_ONLY", "U0_NONE"):
        print(f"  {k:<24}             {u.get(k,0):>10,}")
    if u.get("U3_blockedByMissingGhidraFunction"):
        print(f"  (+{u['U3_blockedByMissingGhidraFunction']} handlers observed executing that Ghidra has no function for --")
        print("   they cannot enter the table at all until those bodies are created)")
    print()
    nx = summary.get("nativeCrossCheck")
    if nx:
        print("-- SELF-TEST: MissionScript native execution -------------------------------")
        print(f"  registry rows                      {nx['registryRows']:>12,}")
        print(f"  handler first byte OBSERVED        {nx['handlerFirstByteObserved']:>12,}")
        print(f"  handlers that are Ghidra entries   {nx['handlersAtAGhidraFunctionEntry']:>12,}")
        print("  EXPECTED 60 over the 66-level campaign, of which 59 are real: the verified")
        print("  analysis strikes SetSpeed@0x00453AC0, a shared 3-byte ret-stub whose hits")
        print("  belong to any caller of the stub. If this reads anything but 60, either the")
        print("  tool is wrong or the coverage set changed -- do not trust the numbers above.")
        print()
    print("-- OBSERVED BUT UNNAMED (cheapest naming targets) --------------------------")
    print(f"  {fx['observedAndUnnamed']:,} functions executed with no human name")
    cand = sorted(
        (f for f in funcs if f["execState"] != "DARK" and f["nameClass"] in UNNAMED_CLASSES),
        key=lambda f: -f["observedBytes"],
    )[:top]
    for f in cand:
        print(f"    0x{f['va']:08x}  {f['observedBytes']:>7,}b obs / {f['hullBytes']:>7,}b  "
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
    print(f"  dark functions                     {rr['darkFunctionCount']:>12,}   {rr.get('darkBodyBytesEstimate', rr['darkHullBytes']):>12,} body bytes (est)")
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
            agg[fam] += int(f.get("bodyBytesEstimate") or f.get("hullBytes") or 0)
        print()
        print("  largest UNCLASSIFIED dark families (the classifier's blind spot -- fix these first):")
        for k, v in agg.most_common(10):
            print(f"    {k:<40}{v:>10,}")
    print()
    print("REMINDERS")
    for line in summary["readingRules"]:
        print(f"  - {line}")
    print("=" * 78)


HEX_COLUMNS = {"va", "startVa", "endVa"}


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
    a = json.loads((a_dir / "ledger-summary.json").read_text(encoding="utf-8"))
    b = json.loads((b_dir / "ledger-summary.json").read_text(encoding="utf-8"))
    af, bf = _load_funcs(a_dir), _load_funcs(b_dir)

    a_src = {s["sourceId"] for s in a["sources"]}
    b_src = {s["sourceId"] for s in b["sources"]}
    added_src = sorted(b_src - a_src)
    removed_src = sorted(a_src - b_src)

    same_pop = a["denominators"]["functionPopulation"] == b["denominators"]["functionPopulation"]
    same_names = a["inputs"]["nameTable"]["sha256"] == b["inputs"]["nameTable"]["sha256"]

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

    new_body_bytes = sum(f["hullBytes"] for f in flipped)
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
    print(f"  coverage indexes added   : {', '.join(added_src) if added_src else '(none)'}")
    print(f"  coverage indexes removed : {', '.join(removed_src) if removed_src else '(none)'}")
    print()
    print("-- WHAT THE PROBE BOUGHT ---------------------------------------------------")
    print(f"  observed .text bytes     {a['bytes']['observedUnion']:>12,} -> {b['bytes']['observedUnion']:>12,}   {d_bytes:+,}")
    print(f"  observed .text %         {a['bytes']['observedUnionPct']:>12.4f} -> {b['bytes']['observedUnionPct']:>12.4f}   {b['bytes']['observedUnionPct']-a['bytes']['observedUnionPct']:+.4f} pp")
    print(f"  observed functions       {a['functions']['observed']:>12,} -> {b['functions']['observed']:>12,}   {d_funcs:+,}")
    print(f"  executed-but-unmapped    {a['bytes']['executedButUnmapped']:>12,} -> {b['bytes']['executedButUnmapped']:>12,}   {b['bytes']['executedButUnmapped']-a['bytes']['executedButUnmapped']:+,}")
    print()
    print(f"  NEW BODIES lit (DARK -> observed) : {len(flipped):,} functions, {new_body_bytes:,} hull bytes")
    print(f"  DEEPER penetration of known bodies: {len(deepened):,} functions, {deeper_bytes:,} extra bytes")
    print("  (the first number is the one that matters: it is new territory, not a longer")
    print("   walk through territory you already had)")
    if new_funcs or gone_funcs:
        print(f"  inventory churn: {len(new_funcs):,} functions added, {len(gone_funcs):,} removed")
    print()
    print(f"-- TOP {args.top} NEWLY-LIT BODIES ------------------------------------------------")
    for f in sorted(flipped, key=lambda x: -x["hullBytes"])[: args.top]:
        print(f"  0x{f['va']:08x}  {f['hullBytes']:>7,}b  {f['nameClass']:<14} {f['reachClass']:<16} {f['name']}")
    if not flipped:
        print("  (none -- this probe lit no body that was previously dark)")
    print()
    fam = Counter()
    for f in flipped:
        fam[f["family"]] += f["hullBytes"]
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

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
