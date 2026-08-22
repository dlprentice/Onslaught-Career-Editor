#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Mechanical contract-status classifier over the existing RE evidence corpus.

WHAT THIS IS
------------
The overlay scanner described by
``reverse-engineering/contract-schema/SCHEMA.md``. It reads four existing
corpora -- the tracked evidence-register projection
(``reverse-engineering/EVIDENCE-REGISTER.tsv``), the per-function notes under
``reverse-engineering/binary-analysis/functions/**``, and the dated manifest
TSVs beside them, plus schema-valid factory documents under
``reverse-engineering/contracts/**`` -- applies the seven-status decision table
with grep-grade rules only (no LLM calls, no network), and writes one JSON
dashboard:

    reverse-engineering/contract-schema/coverage.json

OVERLAY ONLY. Nothing upstream is rewritten; every input is opened read-only.
The function notes stay canonical regardless of what this file says.

HONESTY CONTRACT (do not weaken)
--------------------------------
1. The denominator is the pinned authority ``developer_state.json`` ->
   ``current_re_authority.counts`` (8,329 functions / 14,365 contracts).
   Older prose counts cannot leak in because they are never read.
2. A function whose evidence carries no markers is SKELETON. The classifier
   never invents progress, and one witness counted twice never fabricates a
   second: witness kinds are distinct by construction.
3. Every row records which notes fired, so any classification can be audited
   by hand against the canonical files.
4. Factory documents join existing inventory rows by normalized VA. They never
   append a row, count as a promotion witness, or establish VERIFIED. A schema-
   valid document reaches the REVIEW_READY floor only when its header carries
   the same exact ``Evidence: MEASURED`` marker used for function notes.
5. Fail closed: missing register, wrong row count, unparsable denominator, an
   invalid/duplicate factory identity, or a factory VA absent from the canonical
   inventory exits 2 and writes nothing. A dashboard that cannot run is not
   published.

USAGE
-----
    py -3 tools/contract_coverage.py [--repo-root DIR] [--out PATH | --stdout]
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

from contract_factory_validate import (
    collect_contract_files,
    normalize_va,
    parse_gitmodules_paths,
    validate_file,
)

SCHEMA_ID = "bea.re.contract-coverage.v1"

STATUSES = (
    "STALE",
    "DISPUTED",
    "BLOCKED",
    "VERIFIED",
    "REVIEW_READY",
    "PROVISIONAL",
    "SKELETON",
)

EVIDENCE_CLASSES = (
    "byte-read",
    "ttd-capture",
    "pinned-source-line",
    "controlled-runtime",
    "ghidra-readback",
    "name-only",
)

WITNESS_KINDS = (
    "NOTE_MEASURED",
    "MANIFEST_WITNESS",
    "REGISTER_CONTROLLED_RUNTIME",
)

DEFAULT_REGISTER = Path("reverse-engineering/EVIDENCE-REGISTER.tsv")
DEFAULT_STATE = Path("developer_state.json")
DEFAULT_NOTES_ROOT = Path("reverse-engineering/binary-analysis/functions")
DEFAULT_MANIFESTS_ROOT = Path("reverse-engineering/binary-analysis")
DEFAULT_CONTRACTS_ROOT = Path("reverse-engineering/contracts")
DEFAULT_PATCH_TSV = Path("patches/patch-surface-rows.tsv")
DEFAULT_OUT = Path("reverse-engineering/contract-schema/coverage.json")

# ---------------------------------------------------------------------------
# register evidence-class families (measured from the live register
# 2026-08-22; distributions are asserted by contract_coverage_tests.py)
# ---------------------------------------------------------------------------

REGISTER_VERIFIED_SUFFIX_RE = re.compile(r"(PROMOTED|SURVIVED|REPLICATED)$")
REGISTER_TTD_RE = re.compile(r"^TTD_")
# Deliberately EXCLUDES bare RUNTIME_BOUNDED: it stamps 4,481 baseline
# ANALYST_METADATA_ONLY rows and carries no runtime observation of its own.
REGISTER_CONTROLLED_RUNTIME_RE = re.compile(r"(REPLICATED$|REFUTER_SURVIVED$)")
REGISTER_BYTE_READ_RE = re.compile(
    r"(CAMPAIGN_C1_OPAQUE_PE(_BATCH)?|CAMPAIGN_C1_STATIC_PROOF|"
    r"STATIC_CONTRACT_PROVED|EXHAUSTIVE_STATIC_CROSSWALK)"
)
REGISTER_SOURCE_LINE_RE = re.compile(r"(SOURCE_CORRELATED|SOURCE_JOIN|SEMANTIC_PROMOTED)")
BASELINE_TRIO = ("BASELINE_STATIC", "ANALYST_METADATA_ONLY", "RUNTIME_BOUNDED")

GRADE_TO_STATUS = {
    "C1_CANDIDATE_PARTIAL": "REVIEW_READY",
    "C2_BOUNDED_RUNTIME": "REVIEW_READY",
}

# ---------------------------------------------------------------------------
# note markers (line-scoped on purpose; see SCHEMA.md "Limits")
# ---------------------------------------------------------------------------

HEADER_GRADE_RE = re.compile(
    r"^\s{0,3}(?:>\s?)*\s*(?:[-*+]\s+)?\*{0,2}Evidence\*{0,2}\s*:\s*([A-Za-z]+)",
    re.I,
)
STALE_STATUS_RE = re.compile(
    r"^\s{0,3}(?:>\s?)*\s*\**Status\*{0,2}:?\*{0,2}\s*:?\s*.*\b(superseded|redirect)\b",
    re.I,
)
SECOND_WITNESS_RE = re.compile(
    r"two.witness|second witness|independen[a-z]* re-?read|"
    r"independen[a-z]* reproduc|cross-build|\btwin\b",
    re.I,
)
DISPUTE_LINE_RE = re.compile(
    r"\bwithdrawn\b|\bsuperseded\b|\brefuted\b|proven false|\bdemoted\b|"
    r"\bdisputed\b|open conflict",
    re.I,
)
# Implementation gates only. Scope discipline ("did not mill FUN_*", "did not
# widen the C2") is NOT a block and must not read as one, so widening/did-not
# phrasing is deliberately absent from this pattern. Subject-note level: a
# note that forbids implementing from itself blocks its own subject.
BLOCK_LINE_RE = re.compile(
    r"do not implement|don't implement|must not implement|never implement|"
    r"remains blocked|blocked pending|is blocked until",
    re.I,
)
READBACK_RE = re.compile(r"Saved/read-back|read-back verified", re.I)

VA_RE = re.compile(r"\b0x0{0,2}[0-9A-Fa-f]{6,8}\b")
IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{7,}\b")
VA_LO, VA_HI = 0x00400000, 0x006FFFFF

# Manifest columns measured across the tracked TSVs on 2026-08-22.
NAME_COLUMN_CANDIDATES = (
    "liveName",
    "currentName",
    "retail_current_name",
    "trackedName",
    "currentGhidraName",
    "postName",
    "preName",
    "name",
)
WITNESS_COLUMN_CANDIDATES = (
    "exactness",
    "confidence",
    "byteProof",
    "verdict",
    "agreesWithNote",
)
WITNESS_STRONG_VALUES = frozenset(
    {"MEASURED", "YES", "PASS", "PROVED", "COMPLETE_ENUMERATION"}
)


class ClassificationError(RuntimeError):
    """Fail-closed condition: the corpus cannot be classified honestly."""


# ---------------------------------------------------------------------------
# keys
# ---------------------------------------------------------------------------


def norm_name(name: str) -> str:
    return name.strip().strip("`*_").strip()


def va_key_set(va: int) -> set[str]:
    return {f"0x{va:08X}", f"0x{va:06X}", f"0x{va:X}", str(va)}


def text_va_keys(text: str) -> set[str]:
    out: set[str] = set()
    for m in VA_RE.finditer(text):
        try:
            va = int(m.group(0), 16)
        except ValueError:
            continue
        if VA_LO <= va <= VA_HI:
            out |= va_key_set(va)
    return out


def name_keys(name: str) -> set[str]:
    return {norm_name(name)} | text_va_keys(name)


def register_keys(row: dict) -> set[str]:
    keys = name_keys(row["name"])
    try:
        va = int(row["entryVa"].strip(), 16)
    except ValueError:
        keys.add(row["entryVa"].strip().upper())
    else:
        keys |= va_key_set(va)
    return keys


# ---------------------------------------------------------------------------
# inputs
# ---------------------------------------------------------------------------


def load_denominator(state_path: Path) -> dict:
    raw = json.loads(state_path.read_text(encoding="utf-8"))
    auth = raw.get("current_re_authority")
    if not isinstance(auth, dict):
        raise ClassificationError(f"{state_path}: current_re_authority missing")
    counts = auth.get("counts")
    if not isinstance(counts, dict):
        raise ClassificationError(f"{state_path}: current_re_authority.counts missing")
    for field in ("functions", "contracts"):
        if field not in counts:
            raise ClassificationError(f"{state_path}: counts.{field} missing")
    return {
        "functions": int(counts["functions"]),
        "contracts": int(counts["contracts"]),
        "generation": auth.get("generation"),
        "lineageId": auth.get("lineageId"),
        "readySha256": auth.get("readySha256"),
    }


def load_register(register_path: Path) -> list[dict]:
    if not register_path.exists():
        raise ClassificationError(f"{register_path}: evidence register not found")
    lines = [
        line
        for line in register_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    required = {"entryVa", "name", "grade", "evidence"}
    if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
        raise ClassificationError(
            f"{register_path}: register columns missing "
            f"{sorted(required - set(reader.fieldnames or []))}"
        )
    rows = list(reader)
    if not rows:
        raise ClassificationError(f"{register_path}: zero data rows")
    return rows


class FactoryContract:
    __slots__ = ("rel", "review_ready_floor")

    def __init__(self, rel: str, review_ready_floor: bool) -> None:
        self.rel = rel
        self.review_ready_floor = review_ready_floor


def _contract_has_measured_header(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_end = min(len(lines), 60)
    for i, line in enumerate(lines[:header_end]):
        if i > 0 and re.match(r"^\s{0,3}#{2,6}\s", line):
            break
        match = HEADER_GRADE_RE.match(line)
        if match and match.group(1).upper() == "MEASURED":
            return True
    return False


def load_factory_contracts(
    repo_root: Path, register_rows: list[dict]
) -> dict[str, FactoryContract]:
    """Validate factory files and key them to existing inventory VAs only."""
    contracts_root = repo_root / DEFAULT_CONTRACTS_ROOT
    if not contracts_root.exists():
        return {}
    files = collect_contract_files([contracts_root])
    if not files:
        return {}

    submodule_prefixes = parse_gitmodules_paths(repo_root)
    reports = [
        validate_file(
            path,
            path.relative_to(contracts_root).as_posix(),
            submodule_prefixes,
            repo_root,
        )
        for path in files
    ]
    diagnostics = [
        f"{report.relative}:{violation.line}: [{violation.code}] {violation.message}"
        for report in reports
        for violation in report.violations
    ]

    va_claims: dict[str, tuple[str, int]] = {}
    name_claims: dict[str, str] = {}
    for report in reports:
        if report.normalized_va is not None:
            prior_va = va_claims.get(report.normalized_va)
            if prior_va is not None:
                diagnostics.append(
                    f"{report.relative}:{max(report.address_line, 1)}: "
                    f"[DUPLICATE_VA] VA {report.normalized_va} already claimed by "
                    f"{prior_va[0]}:{prior_va[1]}"
                )
            else:
                va_claims[report.normalized_va] = (
                    report.relative, max(report.address_line, 1)
                )
        if report.tracked_name is not None:
            name_key = report.tracked_name.casefold()
            prior_name = name_claims.get(name_key)
            if prior_name is not None:
                diagnostics.append(
                    f"{report.relative}:1: [DUPLICATE_NAME] tracked name "
                    f"{report.tracked_name!r} already titled in {prior_name}"
                )
            else:
                name_claims[name_key] = report.relative

    if diagnostics:
        raise ClassificationError(
            "factory contract validation failed:\n" + "\n".join(sorted(diagnostics))
        )

    register_vas = {
        normalized
        for row in register_rows
        if (normalized := normalize_va(row["entryVa"])) is not None
    }
    contracts: dict[str, FactoryContract] = {}
    for report in reports:
        va = report.normalized_va
        if va is None or va not in register_vas:
            raise ClassificationError(
                f"factory contract {report.relative}: VA {va or '<invalid>'} is not "
                "present in the canonical function inventory"
            )
        contracts[va] = FactoryContract(
            (DEFAULT_CONTRACTS_ROOT / report.relative).as_posix(),
            _contract_has_measured_header(report.path),
        )
    return contracts


class Note:
    __slots__ = (
        "rel",
        "subject_stem",
        "stale",
        "measured",
        "second_witness",
        "readback",
        "blocks_subject",
        "dispute_keys",
        "block_keys",
        "mention_keys",
    )

    def __init__(self, rel: str, subject_stem: str) -> None:
        self.rel = rel
        self.subject_stem = subject_stem
        self.stale = False
        self.measured = False
        self.second_witness = False
        self.readback = False
        self.blocks_subject = False
        self.dispute_keys: set[str] = set()
        self.block_keys: set[str] = set()
        self.mention_keys: set[str] = set()


def parse_note(path: Path, rel: str) -> Note:
    """Lift mechanical markers from one note file. Read-only, one pass."""
    note = Note(rel, path.stem)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    # Header block: everything before the first ## heading, capped at 60 lines
    # (the same header convention tools/doc_header_check.py enforces).
    header_end = min(len(lines), 60)
    for i, line in enumerate(lines[:header_end]):
        if i > 0 and re.match(r"^\s{0,3}#{2,6}\s", line):
            header_end = i
            break
        m = HEADER_GRADE_RE.match(line)
        if m and m.group(1).upper() == "MEASURED":
            note.measured = True
        if STALE_STATUS_RE.match(line):
            note.stale = True

    for line in lines:
        low = line.lower()
        if SECOND_WITNESS_RE.search(line):
            note.second_witness = True
        if READBACK_RE.search(line):
            note.readback = True
        blocked_line = bool(BLOCK_LINE_RE.search(low))
        if blocked_line:
            note.blocks_subject = True
        line_keys: set[str] = set(IDENT_RE.findall(line)) | text_va_keys(line)
        note.mention_keys |= line_keys
        if DISPUTE_LINE_RE.search(low):
            note.dispute_keys |= line_keys
        if blocked_line:
            note.block_keys |= line_keys
    return note


def load_manifest_witness_keys(paths: list[Path]) -> tuple[set[str], list[str]]:
    """Keys (names/VAs) carrying a strong witness value in a manifest TSV."""
    keys: set[str] = set()
    files_used: list[str] = []
    for path in paths:
        try:
            lines = [
                ln
                for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()
                if ln.strip() and not ln.startswith("#")
            ]
        except OSError:
            continue
        if len(lines) < 2:
            continue
        header = lines[0].split("\t")
        name_col = next((c for c in NAME_COLUMN_CANDIDATES if c in header), None)
        if name_col is None:
            continue
        witness_col = next((c for c in WITNESS_COLUMN_CANDIDATES if c in header), None)
        name_idx = header.index(name_col)
        w_idx = header.index(witness_col) if witness_col in header else None
        files_used.append(path.as_posix())
        for line in lines[1:]:
            cells = line.split("\t")
            if len(cells) <= name_idx:
                continue
            strong = bool(
                w_idx is not None
                and len(cells) > w_idx
                and cells[w_idx].strip().upper() in WITNESS_STRONG_VALUES
            )
            if not strong:
                continue
            keys |= name_keys(cells[name_idx])
            for cell in cells:
                keys |= text_va_keys(cell)
    return keys, files_used


# ---------------------------------------------------------------------------
# classification
# ---------------------------------------------------------------------------


def classify_row(row: dict, ctx: dict) -> dict:
    name = row["name"].strip()
    grade = row["grade"].strip()
    classes_raw = [c.strip() for c in row.get("evidence", "").split(";") if c.strip()]
    keys = register_keys(row)

    classes: set[str] = set()
    kinds: set[str] = set()
    notes_fired: list[str] = []
    flags: list[str] = []
    contract = ctx["contracts_by_va"].get(normalize_va(row["entryVa"]))

    reg_verified = any(REGISTER_VERIFIED_SUFFIX_RE.search(c) for c in classes_raw)
    reg_controlled = any(REGISTER_CONTROLLED_RUNTIME_RE.search(c) for c in classes_raw)
    reg_ttd = any(REGISTER_TTD_RE.match(c) for c in classes_raw)
    reg_byte_read = any(REGISTER_BYTE_READ_RE.search(c) for c in classes_raw)
    reg_source_line = any(REGISTER_SOURCE_LINE_RE.search(c) for c in classes_raw)
    reg_baseline_only = tuple(classes_raw) == BASELINE_TRIO

    if reg_ttd:
        classes.add("ttd-capture")
    if reg_controlled:
        classes.add("controlled-runtime")
        kinds.add("REGISTER_CONTROLLED_RUNTIME")
    if reg_source_line:
        classes.add("pinned-source-line")
    if reg_byte_read:
        classes.add("byte-read")

    subject_note: Note | None = ctx["subjects"].get(norm_name(name))
    if subject_note is None:
        subject_note = ctx["subjects_by_key"].get(norm_name(name))
        if subject_note is None:
            for k in sorted(keys):
                hit = ctx["subjects_by_key"].get(k)
                if hit is not None:
                    subject_note = hit
                    break

    covering: list[Note] = []
    seen_rels: set[str] = set()
    for k in sorted(keys):
        for note in ctx["key_index"].get(k, ()):
            if note.rel not in seen_rels:
                seen_rels.add(note.rel)
                covering.append(note)

    note_measured = bool(subject_note and subject_note.measured)
    if note_measured:
        classes.add("byte-read")
        kinds.add("NOTE_MEASURED")
    if manifest_hit := any(k in ctx["manifest_keys"] for k in keys):
        kinds.add("MANIFEST_WITNESS")
    if covering or (subject_note and subject_note.readback):
        classes.add("ghidra-readback")
    if contract is not None and contract.review_ready_floor:
        classes.add("byte-read")

    status: str | None = None

    # 1. STALE -- the note ABOUT this function declares itself a redirect.
    if subject_note is not None and subject_note.stale:
        status = "STALE"
        flags.append("note-declares-redirect")
        notes_fired.append(subject_note.rel)

    # 2. DISPUTED -- named on a dispute line.
    if status is None:
        for note in [subject_note, *covering]:
            if note is not None and (keys & note.dispute_keys):
                status = "DISPUTED"
                notes_fired.append(note.rel)
                break

    # 3. BLOCKED -- its own note forbids implementing from it, or it is named
    #    on a block line elsewhere.
    if status is None:
        if subject_note is not None and subject_note.blocks_subject:
            status = "BLOCKED"
            notes_fired.append(subject_note.rel)
        else:
            for note in covering:
                if keys & note.block_keys:
                    status = "BLOCKED"
                    notes_fired.append(note.rel)
                    break

    # 4. VERIFIED -- two DISTINCT witness kinds, or a register
    #    promotion/adjudication/replication receipt.
    if status is None:
        if len(kinds) >= 2 or reg_verified:
            status = "VERIFIED"
            if reg_verified:
                flags.append("register-promotion-or-adjudication")

    # 5. REVIEW_READY -- campaign C1/C2 grade, or a measured note that itself
    #    carries second-witness language.
    if status is None:
        if grade in GRADE_TO_STATUS:
            status = GRADE_TO_STATUS[grade]
        elif note_measured and subject_note.second_witness:
            status = "REVIEW_READY"
            flags.append("note-second-witness-language")
        elif contract is not None and contract.review_ready_floor:
            status = "REVIEW_READY"
            flags.append("factory-contract-review-floor")

    # 6. PROVISIONAL -- a measured byte contract covers this function.
    if status is None and (note_measured or reg_byte_read):
        status = "PROVISIONAL"

    # 7. SKELETON -- honest default.
    if status is None:
        status = "SKELETON"

    if status == "SKELETON":
        classes.add("name-only")
        if reg_baseline_only:
            flags.append("analyst-metadata-only")

    if contract is not None:
        flags.append("factory-contract-joined")

    result = {
        "va": row["entryVa"],
        "name": name,
        "status": status,
        "evidenceClasses": sorted(c for c in classes if c in EVIDENCE_CLASSES),
        "witnessKinds": sorted(kinds),
        "notes": sorted(set(notes_fired))[:8],
        "flags": flags,
    }
    if contract is not None:
        result["contracts"] = [contract.rel]
    return result


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------


def build_coverage(repo_root: Path) -> dict:
    t_start = time.monotonic()
    state = load_denominator(repo_root / DEFAULT_STATE)
    register_rows = load_register(repo_root / DEFAULT_REGISTER)
    if len(register_rows) != state["functions"]:
        raise ClassificationError(
            f"register rows {len(register_rows)} != pinned function denominator "
            f"{state['functions']} -- refusing to publish a partial dashboard"
        )

    contracts_by_va = load_factory_contracts(repo_root, register_rows)

    # --- notes ---------------------------------------------------------------
    notes_root = repo_root / DEFAULT_NOTES_ROOT
    notes: list[Note] = []
    subjects: dict[str, Note] = {}
    subjects_by_key: dict[str, Note] = {}
    for path in sorted(notes_root.rglob("*.md")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        note = parse_note(path, rel)
        notes.append(note)
        subjects.setdefault(note.subject_stem, note)
        subjects_by_key.setdefault(note.subject_stem, note)
        for k in text_va_keys(note.subject_stem):
            subjects_by_key.setdefault(k, note)

    # --- join index ----------------------------------------------------------
    register_key_set: set[str] = set()
    for row in register_rows:
        register_key_set |= register_keys(row)

    key_index: dict[str, list[Note]] = {}
    for note in notes:
        for k in note.mention_keys:
            if k in register_key_set:
                key_index.setdefault(k, []).append(note)

    # --- manifests -----------------------------------------------------------
    manifest_paths = sorted((repo_root / DEFAULT_MANIFESTS_ROOT).glob("*.tsv"))
    patch_tsv = repo_root / DEFAULT_PATCH_TSV
    if patch_tsv.exists():
        manifest_paths.append(patch_tsv)
    manifest_keys, manifest_files = load_manifest_witness_keys(manifest_paths)

    ctx = {
        "subjects": subjects,
        "subjects_by_key": subjects_by_key,
        "key_index": key_index,
        "manifest_keys": manifest_keys,
        "contracts_by_va": contracts_by_va,
    }

    results = [classify_row(row, ctx) for row in register_rows]

    by_status = {s: 0 for s in STATUSES}
    for r in results:
        by_status[r["status"]] += 1
    class_counts = {c: 0 for c in EVIDENCE_CLASSES}
    for r in results:
        for c in r["evidenceClasses"]:
            class_counts[c] += 1

    elapsed = time.monotonic() - t_start
    return {
        "schema": SCHEMA_ID,
        "generatedAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "denominator": state,
        "inputs": {
            "register": DEFAULT_REGISTER.as_posix(),
            "registerRows": len(register_rows),
            "noteFiles": len(notes),
            "manifestFilesWithNamedWitnesses": len(manifest_files),
            "manifestWitnessKeys": len(manifest_keys),
            "contractFiles": len(contracts_by_va),
            "contractRowsJoined": len(contracts_by_va),
        },
        "statusCounts": by_status,
        "evidenceClassCounts": class_counts,
        "elapsedSeconds": round(elapsed, 3),
        "functions": results,
    }


def write_coverage(payload: dict, out_path: Path) -> None:
    to_write = payload
    if out_path.exists():
        try:
            previous = json.loads(out_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = None
        if isinstance(previous, dict):
            stable_previous = {
                key: value for key, value in previous.items()
                if key not in {"generatedAtUtc", "elapsedSeconds"}
            }
            stable_current = {
                key: value for key, value in payload.items()
                if key not in {"generatedAtUtc", "elapsedSeconds"}
            }
            if stable_previous == stable_current:
                to_write = dict(payload)
                for key in ("generatedAtUtc", "elapsedSeconds"):
                    if key in previous:
                        to_write[key] = previous[key]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(to_write, indent=1), encoding="utf-8")
    tmp.replace(out_path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out", type=Path, default=None, help="output path override")
    ap.add_argument("--stdout", action="store_true", help="print distribution, skip write")
    args = ap.parse_args(argv)

    try:
        payload = build_coverage(args.repo_root)
    except ClassificationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    total = sum(payload["statusCounts"].values())
    print(f"{total} functions classified in {payload['elapsedSeconds']}s "
          f"(denominator {payload['denominator']['functions']})")
    for s in STATUSES:
        n = payload["statusCounts"][s]
        pct = (100.0 * n / total) if total else 0.0
        print(f"  {s:<13} {n:>6}  ({pct:5.1f}%)")

    if args.stdout:
        return 0
    out = args.out if args.out is not None else args.repo_root / DEFAULT_OUT
    write_coverage(payload, out)
    print(f"wrote {out.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
