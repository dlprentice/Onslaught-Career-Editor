#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build and verify a specimen-bound census of BEA's shipped ``__FILE__`` plates.

The census is deliberately narrower than a source-file assignment.  It records
the exact embedded path push, adjacent decoded line value, allocation/free call
family, and exact campaign function or residual that owns each site.  Only a
primary allocation plate carrying a CPP path is a translation-unit anchor;
closed spans and neighboring anchors remain order priors, never names.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import ntpath
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from typing import Any, Iterable

import capstone
from capstone import Cs, CS_ARCH_X86, CS_MODE_32


SCHEMA = "bea.re.source-unit-census.v1"
CAMPAIGN_SCHEMA = "bea.re.campaign.v5"
REDUCER_SCHEMA = "bea.re.campaign-reducer.v1"
STATUS = "READY"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SPECIMEN_BYTES = 2_506_752
SPECIMEN_MD5 = "3b456964020070efe696d2cc09464a55"
IMAGE_BASE = 0x00400000
CAPSTONE_VERSION = "5.0.7"
EXPECTED_CAMPAIGN_READY_SHA256 = "5bddceb51c131d9c3a1ac634fd0672d0e9999b7ccab3f65dd2b33b4a68947cde"
EXPECTED_REDUCER_ID = "384c325149a4244a5eb48fa70d01bff541584d7b3c5b90b69e4658eed96852d6"
EXPECTED_BODY_RANGES_SHA256 = "ece12c7ce659aa23f8e8fa36b694ef7b2425212ff4ffd4b233535c4a51d00ad5"
EXPECTED_PARITY_READY_SHA256 = "4e4dd5cb1262cbb4f3e616aa02619beee1aa7373629737f58a7cb1f577dab310"
MAX_FORWARD_BYTES = 256

PRIMARY_TARGETS = frozenset((0x005490E0, 0x004A1810))
FREE_TARGET = 0x00449D40
KNOWN_TARGETS = PRIMARY_TARGETS | {FREE_TARGET}

OUTPUTS = (
    "source-unit-owner.py",
    "source-path-strings.tsv",
    "source-sites.tsv",
    "function-source-evidence.tsv",
    "source-units.tsv",
    "function-unit-priors.tsv",
)
CAMPAIGN_OUTPUTS = (
    "campaign-functions.tsv",
    "campaign-residuals.tsv",
    "campaign-questions.tsv",
    "campaign-scenarios.tsv",
    "campaign-levers.tsv",
    "campaign-contracts.tsv",
    "campaign-adjudications.tsv",
    "campaign-supersessions.tsv",
)

FUNCTION_COLUMNS = (
    "entityKey", "entryVa", "entryRva", "currentName", "nativeShippedName",
    "nativeRegistryStatus", "bodyRangesRva", "bodyRangeSetSha256", "bodyBytes",
    "executionState", "observedBytes", "nameClass", "understoodTier", "reachClass",
    "evidenceStates", "resolutionState", "semanticGrade", "campaignState", "lever",
    "leverConfidence", "requiresElevation", "cheapestFalsifier", "lastMeasurementDate",
)
RESIDUAL_COLUMNS = (
    "entityKey", "startVa", "endVa", "bytes", "observedBytes", "observationState",
    "classification", "classificationVerdict", "terminalState", "bytePattern", "prevFunc",
    "nextFunc", "campaignState", "lever", "requiresElevation", "cheapestFalsifier",
    "questionIds", "lastMeasurementDate",
)
PATH_COLUMNS = (
    "pathStringKey", "stringVa", "stringRva", "fileOffset", "sectionName", "rawPath",
    "canonicalPathKey", "canonicalWindowsPath", "canonicalRelativePath", "pathKind",
    "extension", "canonicalAliasCount", "pushSiteCount", "primaryPlateSiteCount",
    "unwindFreePlateSiteCount", "mappedFunctionSiteCount", "residualSiteCount",
)
SITE_COLUMNS = (
    "siteKey", "siteVa", "siteRva", "fileOffset", "pathStringKey", "canonicalPathKey",
    "canonicalRelativePath", "pathKind", "pathPushBytes", "instructionVerdict",
    "lineInstructionVa", "lineEncoding", "lineValue", "lineVerdict", "firstDirectCallVa",
    "firstDirectCallTargetVa", "callOffsetBytes", "plateClass", "plateStartVa",
    "plateEndExclusiveVa", "plateBytesSha256", "pathOwnerKind", "pathOwnerEntityKey",
    "pathOwnerIntervalStartVa", "pathOwnerIntervalEndVa", "pathFunctionEntryVa",
    "pathFunctionName", "pathFunctionBodyRangeSetSha256", "pathResidualObservationState",
    "pathResidualClassification", "callOwnerKind", "callOwnerEntityKey",
    "callOwnerIntervalStartVa", "callOwnerIntervalEndVa", "ownerBoundaryCrossing",
    "evidenceGrade",
)
FUNCTION_EVIDENCE_COLUMNS = (
    "functionEntityKey", "entryVa", "currentName", "bodyRangeSetSha256", "canonicalPathKey",
    "canonicalRelativePath", "pathKind", "siteCount", "lineSiteCount",
    "primaryAllocatorSiteCount", "unwindFreeSiteCount", "firstSiteVa", "lastSiteVa",
    "ownerBoundaryCrossingSiteCount", "evidenceGrade",
)
UNIT_COLUMNS = (
    "unitKey", "canonicalPathKey", "canonicalWindowsPath", "canonicalRelativePath", "basename",
    "rawStringCount", "allSiteCount", "primarySiteCount", "unwindFreeSiteCount",
    "mappedPrimarySiteCount", "residualPrimarySiteCount", "primaryFirstSiteVa",
    "primaryLastSiteVa", "directFunctionCount", "directFunctionFirstEntryVa",
    "directFunctionLastEntryVa", "anchorStatus", "lineSiteCount", "lineMin", "lineMax",
    "lineAdjacentPairCount", "lineInversionCount", "linePriorEligible", "linkOrderOrdinal",
    "lexicalResetBefore", "linkRunPrior", "priorGrade",
)
PRIOR_COLUMNS = (
    "functionEntityKey", "entryVa", "currentName", "bodyRangeSetSha256", "directCppUnitKey",
    "directCppSiteCount", "directHeaderPathKeys", "directHeaderSiteCount", "closedSpanUnitKey",
    "previousUnitKey", "nextUnitKey", "candidateUnitKeys", "priorDisposition", "evidenceGrade",
)

PATH_REGEX = re.compile(
    rb"c:\\dev\\onslaught2\\[^\x00\r\n]{1,260}\.(?:cpp|c|h|hpp)\x00",
    re.IGNORECASE,
)
ROOT_PATH = ntpath.normpath(r"c:\dev\onslaught2").casefold()

PATH_POLICY = {
    "regex": r"(?i)c:\dev\onslaught2\[^\x00\r\n]{1,260}\.(?:cpp|c|h|hpp)\x00",
    "encoding": "strict-ascii-printable",
    "normalization": "ntpath.normpath(rawPath.replace('/', '\\\\')).casefold()",
    "root": ROOT_PATH,
    "headersOwnTranslationUnits": False,
}
PLATE_POLICY = {
    "candidateBytes": "68 <raw-path-string-va-u32-le>",
    "candidateScan": "overlapping-exact-five-byte",
    "line": "immediately-previous-contiguous-decoded-push",
    "primaryTargets": ["0x004a1810", "0x005490e0"],
    "unwindFreeTarget": "0x00449d40",
    "maxForwardBytes": MAX_FORWARD_BYTES,
}
JOIN_POLICY = {
    "ownerIntervals": "exact-generation-5-function-fragments-or-residuals",
    "functionHullsAllowed": False,
    "pathAndCallOwnersPreservedSeparately": True,
    "currentNameAffectsDerivation": False,
}
UNIT_PRIOR_POLICY = {
    "anchor": "PRIMARY_ALLOC_SOURCE_PLATE+CPP+exact-function-owner",
    "directWins": True,
    "closedAnchorSpan": "min/max-direct-function-entry-within-one-unit",
    "betweenSpanOwnerForced": False,
    "linkRunsAreOrderPriorOnly": True,
}
CLAIM_BOUNDARY = [
    "A direct fact is an embedded path push plus decoded memory plate and exact specimen owner address; it does not prove every surrounding function came from that translation unit.",
    "CPP direct evidence is stronger than a span prior; header paths are context only.",
    "Closed spans, link runs, and gap neighbors are hypotheses, never names, Ghidra mutation authority, or rebuild-ready contracts.",
    "currentName is navigation only and never influences any count, tag, or prior.",
    "Absence of plates does not classify library or authored code, and the empty middle band is not an authorship boundary.",
    "The 0x00437a3a owner crossing is an OPEN boundary question, not merge authority.",
    "This tool mutates neither specimen nor Ghidra and authorizes no semantic promotion.",
]


class CensusError(ValueError):
    """An input, derived invariant, or frozen census failed closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CensusError(message)


def va(value: int) -> str:
    return f"0x{value:08x}"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stamp(path: Path, root: Path | None = None) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"artifact is not one plain file: {path}")
    resolved = path.resolve()
    label = resolved.relative_to(root.resolve()).as_posix() if root is not None else str(resolved)
    return {"path": label, "bytes": resolved.stat().st_size, "sha256": sha256_file(resolved)}


def validate_stamp(path: Path, expected: object, label: str) -> dict[str, Any]:
    require(isinstance(expected, dict), f"{label} has no stamp")
    actual = stamp(path)
    require(
        set(expected) >= {"path", "bytes", "sha256"}
        and actual["bytes"] == expected.get("bytes")
        and actual["sha256"] == expected.get("sha256"),
        f"{label} stamp drift",
    )
    return actual


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CensusError(f"cannot read {label}: {path}: {exc}") from exc
    require(isinstance(value, dict), f"{label} is not an object")
    return value


def render_tsv(columns: tuple[str, ...], rows: Iterable[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=list(columns), delimiter="\t", lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        require(set(row) == set(columns), f"TSV row columns drift: {sorted(set(row) ^ set(columns))}")
        values = {column: str(row[column]) for column in columns}
        require(
            not any("\t" in value or "\r" in value or "\n" in value for value in values.values()),
            "TSV value contains a control separator",
        )
        writer.writerow(values)
    return stream.getvalue().encode("utf-8")


def read_exact_tsv(
    path: Path,
    columns: tuple[str, ...],
    label: str,
    *,
    leading_comment: str | None = None,
) -> list[dict[str, str]]:
    try:
        content = path.read_bytes()
        require(not content.startswith(b"\xef\xbb\xbf"), f"{label} has a BOM")
        require(content.endswith(b"\n") and not content.endswith(b"\n\n"), f"{label} final LF drift")
        text = content.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise CensusError(f"cannot read {label}: {path}: {exc}") from exc
    lines = text.splitlines(keepends=True)
    if leading_comment is not None:
        require(bool(lines) and lines[0] == leading_comment + "\n", f"{label} schema comment drift")
        lines = lines[1:]
    require(bool(lines), f"{label} is empty")
    require(lines[0] == "\t".join(columns) + "\n", f"{label} header/column order drift")
    require(not any(line.startswith("#") for line in lines[1:]), f"{label} unexpected comment row")
    try:
        reader = csv.DictReader(lines, delimiter="\t")
        rows = list(reader)
    except csv.Error as exc:
        raise CensusError(f"cannot parse {label}: {exc}") from exc
    require(reader.fieldnames == list(columns), f"{label} header drift")
    require(all(None not in row and set(row) == set(columns) for row in rows), f"{label} malformed row")
    require(render_tsv(columns, rows) == "".join(lines).encode("utf-8"), f"{label} noncanonical bytes")
    return rows


def _u16(data: bytes, offset: int, label: str) -> int:
    require(0 <= offset <= len(data) - 2, f"truncated {label}")
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int, label: str) -> int:
    require(0 <= offset <= len(data) - 4, f"truncated {label}")
    return struct.unpack_from("<I", data, offset)[0]


def parse_pe(data: bytes) -> dict[str, Any]:
    require(len(data) >= 0x40 and data[:2] == b"MZ", "invalid/truncated DOS header")
    pe = _u32(data, 0x3C, "PE offset")
    require(pe <= len(data) - 24 and data[pe : pe + 4] == b"PE\0\0", "invalid/truncated PE signature")
    require(_u16(data, pe + 4, "machine") == 0x014C, "PE is not i386")
    section_count = _u16(data, pe + 6, "section count")
    optional_size = _u16(data, pe + 20, "optional header size")
    require(section_count == 4, "PE section count drift")
    require(optional_size == 224, "PE optional-header size drift")
    optional = pe + 24
    require(optional + optional_size <= len(data), "truncated PE optional header")
    require(_u16(data, optional, "optional magic") == 0x010B, "PE is not PE32")
    require(_u32(data, optional + 28, "image base") == IMAGE_BASE, "PE image-base drift")
    table = optional + optional_size
    require(table + section_count * 40 <= len(data), "truncated section table")
    sections: list[dict[str, Any]] = []
    names: set[str] = set()
    for index in range(section_count):
        offset = table + index * 40
        raw_name = data[offset : offset + 8].split(b"\0", 1)[0]
        try:
            name = raw_name.decode("ascii")
        except UnicodeDecodeError as exc:
            raise CensusError("non-ASCII section name") from exc
        require(name and name not in names, f"duplicate/empty section name: {name!r}")
        names.add(name)
        virtual_size = _u32(data, offset + 8, "section virtual size")
        rva = _u32(data, offset + 12, "section RVA")
        raw_size = _u32(data, offset + 16, "section raw size")
        raw_pointer = _u32(data, offset + 20, "section raw pointer")
        require(raw_pointer + raw_size >= raw_pointer and raw_pointer + raw_size <= len(data), f"section raw range escapes file: {name}")
        sections.append({
            "name": name, "rva": rva, "virtualSize": virtual_size,
            "rawSize": raw_size, "rawPointer": raw_pointer,
        })
    require({".text", ".data"} <= names, "required .text/.data section missing")
    raw_intervals = sorted((s["rawPointer"], s["rawPointer"] + s["rawSize"], s["name"]) for s in sections if s["rawSize"])
    for prior, current in zip(raw_intervals, raw_intervals[1:]):
        require(prior[1] <= current[0], f"overlapping/ambiguous raw sections: {prior[2]} {current[2]}")
    by_name = {s["name"]: s for s in sections}
    text = by_name[".text"]
    data_section = by_name[".data"]
    require(
        (text["rva"], text["rawPointer"], text["virtualSize"], text["rawSize"])
        == (0x1000, 0x1000, 0x1D6F9D, 0x1D7000),
        ".text layout drift",
    )
    require(
        (data_section["rva"], data_section["rawPointer"], data_section["virtualSize"], data_section["rawSize"])
        == (0x222000, 0x222000, 0x3B2614, 0x3F000),
        ".data layout drift",
    )
    return {"imageBase": IMAGE_BASE, "sections": sections, "text": text, "data": data_section}


def offset_mapping(pe: dict[str, Any], offset: int) -> tuple[dict[str, Any], int]:
    matches = []
    for section in pe["sections"]:
        delta = offset - section["rawPointer"]
        if 0 <= delta < section["rawSize"] and delta < section["virtualSize"]:
            matches.append((section, IMAGE_BASE + section["rva"] + delta))
    require(len(matches) == 1, f"file offset has ambiguous/uninitialized mapping: {offset:#x}")
    return matches[0]


def va_to_offset(pe: dict[str, Any], address: int, size: int = 1) -> int:
    require(size >= 0 and address + size >= address, "invalid VA span")
    matches = []
    for section in pe["sections"]:
        delta = address - (IMAGE_BASE + section["rva"])
        initialized = min(section["virtualSize"], section["rawSize"])
        if 0 <= delta and delta + size <= initialized:
            matches.append(section["rawPointer"] + delta)
    require(len(matches) == 1, f"VA span has ambiguous/uninitialized mapping: {address:#x}+{size}")
    return matches[0]


def _campaign_repo_root(campaign: Path) -> Path:
    for candidate in (campaign, *campaign.parents):
        if (candidate / "README.MD").is_file() and (candidate / "local-lab").is_dir():
            return candidate
    raise CensusError("campaign path is not beneath a repository local-lab owner")


def _validate_external_repo_path(root: Path, value: object, label: str) -> Path:
    require(isinstance(value, str) and bool(value), f"{label} path missing")
    raw = Path(value)
    path = raw if raw.is_absolute() else root / raw
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise CensusError(f"{label} path escapes repository") from exc
    return resolved


def validate_campaign(campaign_ready: Path, expected_ready_sha256: str, specimen: Path) -> dict[str, Any]:
    require(re.fullmatch(r"[0-9a-f]{64}", expected_ready_sha256) is not None, "expected campaign READY hash is not canonical")
    require(expected_ready_sha256 == EXPECTED_CAMPAIGN_READY_SHA256, "source census campaign boundary hash drift")
    require(campaign_ready.name == "campaign.ready.json" and campaign_ready.is_file() and not campaign_ready.is_symlink(), "campaign READY path is invalid")
    require(sha256_file(campaign_ready) == expected_ready_sha256, "campaign READY hash drift")
    campaign = campaign_ready.parent.resolve()
    repo = _campaign_repo_root(campaign)
    ready = read_json(campaign_ready, "campaign READY")
    require(ready.get("schema") == CAMPAIGN_SCHEMA, "campaign schema drift")
    require(ready.get("generation") == 5, "campaign generation drift")
    reducer = ready.get("reducer")
    require(isinstance(reducer, dict) and reducer.get("schema") == REDUCER_SCHEMA, "campaign reducer schema drift")
    require(reducer.get("id") == EXPECTED_REDUCER_ID, "campaign reducer ID drift")
    files = reducer.get("files")
    require(isinstance(files, list) and files, "campaign reducer manifest missing")
    reducer_paths: set[str] = set()
    for row in files:
        require(isinstance(row, dict) and set(row) == {"role", "path", "bytes", "sha256"}, "campaign reducer row malformed")
        relative = str(row["path"])
        require(relative.startswith("_reducer/") and relative not in reducer_paths and ".." not in Path(relative).parts, "unsafe/duplicate reducer path")
        reducer_paths.add(relative)
        validate_stamp(campaign / Path(relative), row, f"campaign reducer {relative}")
    actual_reducer = {
        path.relative_to(campaign).as_posix()
        for path in (campaign / "_reducer").rglob("*") if path.is_file()
    }
    require(actual_reducer == reducer_paths, "campaign reducer contains unmanifested/missing files")
    outputs = ready.get("outputs")
    require(isinstance(outputs, dict) and set(outputs) == set(CAMPAIGN_OUTPUTS), "campaign output manifest drift")
    for name in CAMPAIGN_OUTPUTS:
        validate_stamp(campaign / name, outputs[name], f"campaign output {name}")
    counts = ready.get("counts")
    require(isinstance(counts, dict) and counts.get("functions") == 7595 and counts.get("residuals") == 6618, "campaign counts drift")
    snapshot = ready.get("sourceSnapshot")
    require(isinstance(snapshot, dict), "campaign source snapshot missing")
    snap_specimen = snapshot.get("specimen")
    require(isinstance(snap_specimen, dict), "campaign snapshot specimen missing")
    require(
        snap_specimen.get("bytes") == SPECIMEN_BYTES
        and snap_specimen.get("sha256") == SPECIMEN_SHA256
        and stamp(specimen)["bytes"] == snap_specimen.get("bytes")
        and stamp(specimen)["sha256"] == snap_specimen.get("sha256"),
        "campaign/direct specimen mismatch",
    )
    graph = snapshot.get("parityGraph")
    require(isinstance(graph, dict), "campaign parity graph missing")
    program = graph.get("program")
    require(
        isinstance(program, dict)
        and program.get("executableMd5") == SPECIMEN_MD5
        and program.get("imageBase") == va(IMAGE_BASE)
        and program.get("language") == "x86:LE:32:default"
        and program.get("compilerSpec") == "windows",
        "campaign source program drift",
    )
    require(graph.get("functionCount") == 7595 and graph.get("rangeCount") == 7712, "campaign source range counts drift")
    body = graph.get("bodyRanges")
    parity_receipt = graph.get("receipt")
    require(isinstance(body, dict) and body.get("sha256") == EXPECTED_BODY_RANGES_SHA256, "transitive body-range owner drift")
    require(isinstance(parity_receipt, dict) and parity_receipt.get("sha256") == EXPECTED_PARITY_READY_SHA256, "transitive parity READY drift")
    validate_stamp(_validate_external_repo_path(repo, body.get("path"), "body ranges"), body, "transitive body ranges")
    validate_stamp(_validate_external_repo_path(repo, parity_receipt.get("path"), "parity READY"), parity_receipt, "transitive parity READY")
    frozen_entry = campaign / str(reducer.get("entry", ""))
    require(frozen_entry.is_file(), "frozen campaign verifier missing")
    environment = dict(os.environ)
    environment["BEA_REPO_ROOT"] = str(repo)
    bootstrap = (
        "import runpy,sys;from pathlib import Path;"
        "p=Path(sys.argv[1]).resolve();sys.path.insert(0,str(p.parent));"
        "sys.argv=[str(p),*sys.argv[2:]];runpy.run_path(str(p),run_name='__main__')"
    )
    completed = subprocess.run(
        [
            sys.executable, "-I", "-B", "-c", bootstrap, str(frozen_entry),
            "verify", "--campaign", str(campaign),
        ],
        cwd=campaign, env=environment, capture_output=True, text=True, timeout=900, check=False,
    )
    require(completed.returncode == 0 and "CAMPAIGN_VERIFIED" in completed.stdout, f"frozen campaign replay failed: {completed.stderr or completed.stdout}")
    return {"dir": campaign, "repo": repo, "ready": ready, "program": program}


def _parse_address(value: str, label: str) -> int:
    require(re.fullmatch(r"0x[0-9a-f]{8}", value) is not None, f"{label} is not canonical VA")
    return int(value, 16)


def _parse_rva(value: str, label: str) -> int:
    require(re.fullmatch(r"0x[0-9a-f]+", value) is not None, f"{label} is not canonical RVA")
    return int(value, 16)


def _range_digest(ranges: list[list[int]]) -> str:
    return sha256_bytes(json.dumps(ranges, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def load_owner_intervals(campaign: Path) -> dict[str, Any]:
    functions = read_exact_tsv(
        campaign / "campaign-functions.tsv", FUNCTION_COLUMNS, "campaign functions",
        leading_comment="# bea.re.campaign.v5",
    )
    residuals = read_exact_tsv(
        campaign / "campaign-residuals.tsv", RESIDUAL_COLUMNS, "campaign residuals",
        leading_comment="# bea.re.campaign.v5",
    )
    require(len(functions) == 7595 and len(residuals) == 6618, "campaign row counts drift")
    fragments: list[dict[str, Any]] = []
    function_by_key: dict[str, dict[str, Any]] = {}
    function_by_entry: dict[int, dict[str, Any]] = {}
    for row in functions:
        entry = _parse_address(row["entryVa"], "function entry")
        entry_rva = _parse_rva(row["entryRva"], "function entry RVA")
        require(entry_rva == entry - IMAGE_BASE, "function entry VA/RVA drift")
        ranges: list[list[int]] = []
        for item in row["bodyRangesRva"].split(";"):
            match = re.fullmatch(r"(0x[0-9a-f]+)-(0x[0-9a-f]+)", item)
            require(match is not None, "function body range syntax drift")
            lo, hi = int(match.group(1), 16), int(match.group(2), 16)
            require(lo < hi and (not ranges or ranges[-1][1] <= lo), "function ranges unsorted/overlap/empty")
            ranges.append([lo, hi])
        digest = _range_digest(ranges)
        require(digest == row["bodyRangeSetSha256"], "function body range digest drift")
        require(sum(hi - lo for lo, hi in ranges) == int(row["bodyBytes"]), "function body byte count drift")
        require(any(lo <= entry_rva < hi for lo, hi in ranges), "function entry outside exact body")
        expected_key = f"CODE:{SPECIMEN_SHA256}:VA={va(entry)}:RANGES={digest}"
        require(row["entityKey"] == expected_key, "function entity key drift")
        require(row["entityKey"] not in function_by_key and entry not in function_by_entry, "duplicate function identity")
        cooked = dict(row)
        cooked.update({"entry": entry, "ranges": ranges})
        function_by_key[row["entityKey"]] = cooked
        function_by_entry[entry] = cooked
        for lo, hi in ranges:
            fragments.append({
                "lo": IMAGE_BASE + lo, "hi": IMAGE_BASE + hi, "kind": "FUNCTION",
                "entity": row["entityKey"], "row": cooked,
            })
    require(len(fragments) == 7712, "function fragment count drift")
    fragments.sort(key=lambda item: (item["lo"], item["hi"], item["entity"]))
    _require_no_overlap(fragments, "function fragments")
    residual_intervals: list[dict[str, Any]] = []
    residual_by_key: dict[str, dict[str, Any]] = {}
    for row in residuals:
        lo = _parse_address(row["startVa"], "residual start")
        hi = _parse_address(row["endVa"], "residual end")
        require(lo < hi and hi - lo == int(row["bytes"]), "residual interval/byte count drift")
        expected_entity = (
            f"TEXT_RESIDUAL:{SPECIMEN_SHA256}:"
            f"0x{lo:08X}-0x{hi:08X}"
        )
        require(row["entityKey"] == expected_entity, "residual entity key drift")
        require(row["entityKey"] not in residual_by_key, "duplicate residual entity")
        cooked = dict(row)
        cooked.update({"lo": lo, "hi": hi})
        residual_by_key[row["entityKey"]] = cooked
        residual_intervals.append({"lo": lo, "hi": hi, "kind": "RESIDUAL", "entity": row["entityKey"], "row": cooked})
    residual_intervals.sort(key=lambda item: (item["lo"], item["hi"], item["entity"]))
    _require_no_overlap(residual_intervals, "residual intervals")
    all_intervals = sorted(fragments + residual_intervals, key=lambda item: (item["lo"], item["hi"], item["kind"]))
    _require_no_overlap(all_intervals, "combined function/residual intervals")
    return {
        "functions": list(function_by_key.values()), "functionByKey": function_by_key,
        "functionByEntry": function_by_entry, "fragments": fragments,
        "residuals": list(residual_by_key.values()), "residualByKey": residual_by_key,
        "residualIntervals": residual_intervals, "allIntervals": all_intervals,
        "starts": [item["lo"] for item in all_intervals],
    }


def _require_no_overlap(intervals: list[dict[str, Any]], label: str) -> None:
    for prior, current in zip(intervals, intervals[1:]):
        require(prior["hi"] <= current["lo"], f"{label} overlap")


def owner_at(owners: dict[str, Any], address: int) -> dict[str, Any]:
    index = bisect_right(owners["starts"], address) - 1
    require(index >= 0 and owners["allIntervals"][index]["lo"] <= address < owners["allIntervals"][index]["hi"], f"address has neither exact function fragment nor residual owner: {address:#x}")
    return owners["allIntervals"][index]


def scan_paths(data: bytes, pe: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for match in PATH_REGEX.finditer(data):
        content = match.group()[:-1]
        require(content and all(0x20 <= byte <= 0x7E for byte in content), "source path contains non-printable bytes")
        try:
            raw = content.decode("ascii")
        except UnicodeDecodeError as exc:
            raise CensusError("source path is not strict ASCII") from exc
        section, address = offset_mapping(pe, match.start())
        require(section["name"] == ".data", "source path is outside initialized .data")
        canonical, relative, extension, kind = canonicalize_source_path(raw)
        digest = sha256_bytes(canonical.encode("utf-8"))
        rows.append({
            "offset": match.start(), "address": address, "raw": raw, "canonical": canonical,
            "relative": relative, "extension": extension, "kind": kind,
            "pathStringKey": f"PATH_STRING:{SPECIMEN_SHA256}:VA={va(address)}",
            "canonicalPathKey": f"SOURCE_PATH:{SPECIMEN_SHA256}:PATHSHA={digest}",
            "unitKey": f"SOURCE_UNIT:{SPECIMEN_SHA256}:PATHSHA={digest}",
        })
    require(len(rows) == 166, "raw source path count drift")
    require(len({row["raw"].casefold() for row in rows}) == 163, "raw casefold path count drift")
    require(len({row["canonical"] for row in rows}) == 162, "canonical path count drift")
    require(Counter(row["kind"] for row in rows) == Counter({"CPP": 151, "HEADER": 15}), "raw path-kind count drift")
    require(Counter({row["canonical"]: row["kind"] for row in rows}.values()) == Counter({"CPP": 151, "HEADER": 11}), "canonical path-kind count drift")
    require(len({row["address"] for row in rows}) == len(rows), "duplicate source string VA")
    return rows


def canonicalize_source_path(raw: str) -> tuple[str, str, str, str]:
    """Return the frozen Windows spelling and conservative CPP/header class."""
    require(raw and all(0x20 <= ord(character) <= 0x7E for character in raw), "source path contains invalid ASCII/control bytes")
    canonical = ntpath.normpath(raw.replace("/", "\\")).casefold()
    require(canonical == ROOT_PATH or canonical.startswith(ROOT_PATH + "\\"), "source path escapes canonical root")
    relative = ntpath.relpath(canonical, ROOT_PATH).replace("\\", "/")
    require(relative not in ("", ".") and not relative.startswith("../"), "source path has invalid relative name")
    extension = ntpath.splitext(canonical)[1]
    require(extension in (".cpp", ".c", ".h", ".hpp"), "source path extension drift")
    kind = "CPP" if extension in (".cpp", ".c") else "HEADER"
    return canonical, relative, extension, kind


def scan_candidates(data: bytes, pe: dict[str, Any], paths: list[dict[str, Any]]) -> list[dict[str, Any]]:
    text = pe["text"]
    text_bytes = data[text["rawPointer"] : text["rawPointer"] + text["virtualSize"]]
    rows = []
    seen_sites: set[int] = set()
    for path in paths:
        hits = exact_push_offsets(text_bytes, path["address"])
        count = len(hits)
        for hit in hits:
            site = IMAGE_BASE + text["rva"] + hit
            require(site not in seen_sites, "candidate site aliases two raw path strings")
            seen_sites.add(site)
            rows.append({"site": site, "fileOffset": text["rawPointer"] + hit, "path": path})
        require(count > 0, f"source string has no exact push site: {path['raw']}")
    rows.sort(key=lambda row: (row["site"], row["path"]["pathStringKey"]))
    require(len(rows) == 1870 and len(seen_sites) == 1870, "raw source plate candidate count drift")
    return rows


def exact_push_offsets(blob: bytes, string_va: int) -> list[int]:
    """Find overlapping exact ``PUSH imm32`` byte candidates, not bare pointers."""
    require(0 <= string_va <= 0xFFFFFFFF, "source string VA is not u32")
    needle = b"\x68" + struct.pack("<I", string_va)
    offsets = []
    position = 0
    while True:
        hit = blob.find(needle, position)
        if hit < 0:
            return offsets
        offsets.append(hit)
        position = hit + 1


def _interval_instruction_map(data: bytes, pe: dict[str, Any], interval: dict[str, Any]) -> tuple[list[Any], dict[int, int]]:
    offset = va_to_offset(pe, interval["lo"], interval["hi"] - interval["lo"])
    blob = data[offset : offset + interval["hi"] - interval["lo"]]
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.skipdata = True
    instructions = list(decoder.disasm(blob, interval["lo"]))
    require(instructions and instructions[0].address == interval["lo"], "exact owner interval decode failed at start")
    cursor = interval["lo"]
    for instruction in instructions:
        require(instruction.address == cursor and instruction.size > 0, "exact owner interval decode gap")
        cursor += instruction.size
    require(cursor == interval["hi"], "exact owner interval decode incomplete")
    return instructions, {instruction.address: index for index, instruction in enumerate(instructions)}


def decoded_line(instructions: list[Any], indices: dict[int, int], site: int) -> tuple[str, str, str, str]:
    require(site in indices, "path push is not an instruction start in exact owner interval")
    instruction = instructions[indices[site]]
    require(instruction.bytes[:1] == b"\x68" and instruction.size == 5, "path candidate is not exact PUSH imm32 instruction")
    index = indices[site]
    if index == 0:
        return "", "NONE", "", "NO_ADJACENT_DECODED_LINE_PUSH"
    previous = instructions[index - 1]
    if previous.address + previous.size != site or previous.mnemonic != "push":
        return "", "NONE", "", "NO_ADJACENT_DECODED_LINE_PUSH"
    raw = bytes(previous.bytes)
    if len(raw) == 2 and raw[0] == 0x6A:
        value = raw[1]
        require(value <= 127, "high-bit PUSH imm8 violates canonical line encoding")
        return va(previous.address), "PUSH_IMM8", str(value), "ADJACENT_DECODED_LINE_PUSH"
    if len(raw) == 5 and raw[0] == 0x68:
        value = struct.unpack_from("<I", raw, 1)[0]
        require(value >= 128, "PUSH imm32 below 128 violates canonical line encoding")
        return va(previous.address), "PUSH_IMM32", str(value), "ADJACENT_DECODED_LINE_PUSH"
    return "", "NONE", "", "NO_ADJACENT_DECODED_LINE_PUSH"


def first_direct_call(data: bytes, pe: dict[str, Any], site: int) -> tuple[int, int]:
    offset = va_to_offset(pe, site, MAX_FORWARD_BYTES)
    blob = data[offset : offset + MAX_FORWARD_BYTES]
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    instructions = list(decoder.disasm(blob, site))
    cursor = site
    for instruction in instructions:
        require(instruction.address == cursor, "forward plate decode gap")
        cursor += instruction.size
        raw = bytes(instruction.bytes)
        if instruction.address == site:
            require(raw[:1] == b"\x68" and instruction.size == 5, "forward decode did not begin at path push")
        if raw[:1] == b"\xe8" and instruction.size == 5:
            displacement = struct.unpack_from("<i", raw, 1)[0]
            target = instruction.address + 5 + displacement
            require(target in KNOWN_TARGETS, f"unknown first direct source-plate call target: {target:#x}")
            return instruction.address, target
        mnemonic = instruction.mnemonic.lower()
        require(mnemonic not in ("ret", "retf", "jmp"), f"{mnemonic.upper()} before first direct source-plate call")
    raise CensusError("no direct E8 source-plate call within 256 bytes")


def derive(data: bytes, pe: dict[str, Any], paths: list[dict[str, Any]], candidates: list[dict[str, Any]], owners: dict[str, Any]) -> dict[str, Any]:
    interval_cache: dict[tuple[int, int, str], tuple[list[Any], dict[int, int]]] = {}
    sites: list[dict[str, Any]] = []
    for candidate in candidates:
        site = candidate["site"]
        path = candidate["path"]
        path_owner = owner_at(owners, site)
        cache_key = (path_owner["lo"], path_owner["hi"], path_owner["entity"])
        decoded = interval_cache.get(cache_key)
        if decoded is None:
            decoded = _interval_instruction_map(data, pe, path_owner)
            interval_cache[cache_key] = decoded
        instructions, indices = decoded
        line_va, line_encoding, line_value, line_verdict = decoded_line(instructions, indices, site)
        instruction = instructions[indices[site]]
        require(bytes(instruction.bytes) == data[candidate["fileOffset"] : candidate["fileOffset"] + 5], "decoded path push bytes disagree with specimen")
        call, target = first_direct_call(data, pe, site)
        require(7 <= call - site <= 124, "first direct call offset drift")
        call_owner = owner_at(owners, call)
        plate_class = "PRIMARY_ALLOC_SOURCE_PLATE" if target in PRIMARY_TARGETS else "UNWIND_FREE_SOURCE_PLATE"
        plate_start = int(line_va, 16) if line_va else site
        plate_end = call + 5
        plate_offset = va_to_offset(pe, plate_start, plate_end - plate_start)
        plate_hash = sha256_bytes(data[plate_offset : plate_offset + plate_end - plate_start])
        crossing = (
            path_owner["kind"], path_owner["entity"], path_owner["lo"], path_owner["hi"]
        ) != (
            call_owner["kind"], call_owner["entity"], call_owner["lo"], call_owner["hi"]
        )
        evidence_grade = "DIRECT_DECODED_FILE_LINE_PLATE" if line_encoding != "NONE" else "DIRECT_DECODED_FILE_PATH_PLATE"

        function = path_owner["row"] if path_owner["kind"] == "FUNCTION" else None
        residual = path_owner["row"] if path_owner["kind"] == "RESIDUAL" else None
        row = {
            "siteKey": f"FILE_PLATE:{SPECIMEN_SHA256}:VA={va(site)}:PATHVA={va(path['address'])}",
            "siteVa": va(site), "siteRva": va(site - IMAGE_BASE), "fileOffset": va(candidate["fileOffset"]),
            "pathStringKey": path["pathStringKey"], "canonicalPathKey": path["canonicalPathKey"],
            "canonicalRelativePath": path["relative"], "pathKind": path["kind"],
            "pathPushBytes": bytes(instruction.bytes).hex(), "instructionVerdict": "EXACT_INTERVAL_LINEAR_DECODED_PUSH_IMM32",
            "lineInstructionVa": line_va, "lineEncoding": line_encoding, "lineValue": line_value,
            "lineVerdict": line_verdict, "firstDirectCallVa": va(call), "firstDirectCallTargetVa": va(target),
            "callOffsetBytes": str(call - site), "plateClass": plate_class, "plateStartVa": va(plate_start),
            "plateEndExclusiveVa": va(plate_end), "plateBytesSha256": plate_hash,
            "pathOwnerKind": path_owner["kind"], "pathOwnerEntityKey": path_owner["entity"],
            "pathOwnerIntervalStartVa": va(path_owner["lo"]), "pathOwnerIntervalEndVa": va(path_owner["hi"]),
            "pathFunctionEntryVa": function["entryVa"] if function else "",
            "pathFunctionName": function["currentName"] if function else "",
            "pathFunctionBodyRangeSetSha256": function["bodyRangeSetSha256"] if function else "",
            "pathResidualObservationState": residual["observationState"] if residual else "",
            "pathResidualClassification": residual["classification"] if residual else "",
            "callOwnerKind": call_owner["kind"], "callOwnerEntityKey": call_owner["entity"],
            "callOwnerIntervalStartVa": va(call_owner["lo"]), "callOwnerIntervalEndVa": va(call_owner["hi"]),
            "ownerBoundaryCrossing": str(crossing), "evidenceGrade": evidence_grade,
        }
        sites.append(row)

    path_by_key = {path["pathStringKey"]: path for path in paths}
    canonical_aliases = Counter(path["canonical"] for path in paths)
    sites_by_string: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for site in sites:
        sites_by_string[site["pathStringKey"]].append(site)
    path_rows = []
    for path in sorted(paths, key=lambda item: item["address"]):
        related = sites_by_string[path["pathStringKey"]]
        path_rows.append({
            "pathStringKey": path["pathStringKey"], "stringVa": va(path["address"]),
            "stringRva": va(path["address"] - IMAGE_BASE), "fileOffset": va(path["offset"]),
            "sectionName": ".data", "rawPath": path["raw"], "canonicalPathKey": path["canonicalPathKey"],
            "canonicalWindowsPath": path["canonical"], "canonicalRelativePath": path["relative"],
            "pathKind": path["kind"], "extension": path["extension"],
            "canonicalAliasCount": str(canonical_aliases[path["canonical"]]),
            "pushSiteCount": str(len(related)),
            "primaryPlateSiteCount": str(sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" for row in related)),
            "unwindFreePlateSiteCount": str(sum(row["plateClass"] == "UNWIND_FREE_SOURCE_PLATE" for row in related)),
            "mappedFunctionSiteCount": str(sum(row["pathOwnerKind"] == "FUNCTION" for row in related)),
            "residualSiteCount": str(sum(row["pathOwnerKind"] == "RESIDUAL" for row in related)),
        })

    function_relation_sites: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for site in sites:
        if site["pathOwnerKind"] == "FUNCTION":
            function_relation_sites[(site["pathOwnerEntityKey"], site["canonicalPathKey"])].append(site)
    function_rows = []
    for (entity, path_key), related in function_relation_sites.items():
        function = owners["functionByKey"][entity]
        path = path_by_key[related[0]["pathStringKey"]]
        function_rows.append({
            "functionEntityKey": entity, "entryVa": function["entryVa"], "currentName": function["currentName"],
            "bodyRangeSetSha256": function["bodyRangeSetSha256"], "canonicalPathKey": path_key,
            "canonicalRelativePath": related[0]["canonicalRelativePath"], "pathKind": related[0]["pathKind"],
            "siteCount": str(len(related)), "lineSiteCount": str(sum(row["lineEncoding"] != "NONE" for row in related)),
            "primaryAllocatorSiteCount": str(sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" for row in related)),
            "unwindFreeSiteCount": str(sum(row["plateClass"] == "UNWIND_FREE_SOURCE_PLATE" for row in related)),
            "firstSiteVa": min(row["siteVa"] for row in related), "lastSiteVa": max(row["siteVa"] for row in related),
            "ownerBoundaryCrossingSiteCount": str(sum(row["ownerBoundaryCrossing"] == "True" for row in related)),
            "evidenceGrade": "EXACT_FUNCTION_FRAGMENT_PATH_PUSH",
        })
    function_rows.sort(key=lambda row: (int(row["entryVa"], 16), row["canonicalRelativePath"]))

    canonical_paths: dict[str, dict[str, Any]] = {}
    for path in paths:
        canonical_paths.setdefault(path["canonicalPathKey"], path)
    canonical_sites: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for site in sites:
        canonical_sites[site["canonicalPathKey"]].append(site)
    cpp_paths = [path for path in canonical_paths.values() if path["kind"] == "CPP"]
    unit_material = []
    direct_by_unit: dict[str, set[str]] = defaultdict(set)
    direct_sites_by_unit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for site in sites:
        if site["pathKind"] == "CPP" and site["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE":
            direct_sites_by_unit[site["canonicalPathKey"]].append(site)
            if site["pathOwnerKind"] == "FUNCTION":
                direct_by_unit[site["canonicalPathKey"]].add(site["pathOwnerEntityKey"])
    for path in cpp_paths:
        all_sites = canonical_sites[path["canonicalPathKey"]]
        primary = [site for site in all_sites if site["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE"]
        require(primary, f"CPP unit has no primary source plate: {path['relative']}")
        functions = sorted(direct_by_unit[path["canonicalPathKey"]], key=lambda entity: owners["functionByKey"][entity]["entry"])
        line_sites = sorted(
            (int(site["siteVa"], 16), int(site["lineValue"])) for site in primary if site["lineEncoding"] != "NONE"
        )
        eligible = len(line_sites) >= 5
        inversions = sum(left[1] > right[1] for left, right in zip(line_sites, line_sites[1:])) if eligible else 0
        unit_material.append({
            "path": path, "all": all_sites, "primary": primary, "functions": functions,
            "lineSites": line_sites, "eligible": eligible, "inversions": inversions,
            "first": min(int(site["siteVa"], 16) for site in primary),
            "last": max(int(site["siteVa"], 16) for site in primary),
        })
    unit_material.sort(key=lambda item: (item["first"], item["path"]["relative"]))
    for prior, current in zip(unit_material, unit_material[1:]):
        require(prior["last"] < current["first"], "primary source-unit spans overlap")
    run = 1
    unit_rows = []
    for ordinal, item in enumerate(unit_material, start=1):
        path = item["path"]
        lexical_reset = ordinal > 1 and path["relative"] < unit_material[ordinal - 2]["path"]["relative"]
        if lexical_reset:
            run += 1
        functions = item["functions"]
        raw_count = sum(candidate["canonicalPathKey"] == path["canonicalPathKey"] for candidate in paths)
        line_sites = item["lineSites"]
        unit_rows.append({
            "unitKey": path["unitKey"], "canonicalPathKey": path["canonicalPathKey"],
            "canonicalWindowsPath": path["canonical"], "canonicalRelativePath": path["relative"],
            "basename": ntpath.basename(path["canonical"]), "rawStringCount": str(raw_count),
            "allSiteCount": str(len(item["all"])), "primarySiteCount": str(len(item["primary"])),
            "unwindFreeSiteCount": str(len(item["all"]) - len(item["primary"])),
            "mappedPrimarySiteCount": str(sum(site["pathOwnerKind"] == "FUNCTION" for site in item["primary"])),
            "residualPrimarySiteCount": str(sum(site["pathOwnerKind"] == "RESIDUAL" for site in item["primary"])),
            "primaryFirstSiteVa": va(item["first"]), "primaryLastSiteVa": va(item["last"]),
            "directFunctionCount": str(len(functions)),
            "directFunctionFirstEntryVa": owners["functionByKey"][functions[0]]["entryVa"] if functions else "",
            "directFunctionLastEntryVa": owners["functionByKey"][functions[-1]]["entryVa"] if functions else "",
            "anchorStatus": "ANCHORED" if functions else "RESIDUAL_ONLY",
            "lineSiteCount": str(len(line_sites)), "lineMin": str(min((line for _, line in line_sites), default="")),
            "lineMax": str(max((line for _, line in line_sites), default="")),
            "lineAdjacentPairCount": str(len(line_sites) - 1 if item["eligible"] else 0),
            "lineInversionCount": str(item["inversions"]), "linePriorEligible": str(item["eligible"]),
            "linkOrderOrdinal": str(ordinal), "lexicalResetBefore": str(lexical_reset),
            "linkRunPrior": str(run), "priorGrade": "ORDER_PRIOR_NOT_AUTHORSHIP",
        })

    unit_by_path = {row["canonicalPathKey"]: row for row in unit_rows}
    direct_cpp_by_function: dict[str, list[dict[str, Any]]] = defaultdict(list)
    header_by_function: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for site in sites:
        if site["pathOwnerKind"] != "FUNCTION":
            continue
        if site["pathKind"] == "CPP" and site["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE":
            direct_cpp_by_function[site["pathOwnerEntityKey"]].append(site)
        elif (
            site["pathKind"] == "HEADER"
            and site["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE"
        ):
            header_by_function[site["pathOwnerEntityKey"]].append(site)
    require(all(len({site["canonicalPathKey"] for site in related}) == 1 for related in direct_cpp_by_function.values()), "direct function anchors multiple CPP units")
    anchor_spans = []
    for row in unit_rows:
        if row["anchorStatus"] != "ANCHORED":
            continue
        anchor_spans.append({
            "lo": int(row["directFunctionFirstEntryVa"], 16),
            "hi": int(row["directFunctionLastEntryVa"], 16),
            "unit": row["unitKey"],
        })
    anchor_spans.sort(key=lambda item: item["lo"])
    for prior, current in zip(anchor_spans, anchor_spans[1:]):
        require(prior["hi"] < current["lo"], "closed source-unit anchor spans overlap")
    span_starts = [span["lo"] for span in anchor_spans]
    prior_rows = []
    for function in sorted(owners["functions"], key=lambda row: row["entry"]):
        entity = function["entityKey"]
        entry = function["entry"]
        direct_sites = direct_cpp_by_function.get(entity, [])
        header_sites = header_by_function.get(entity, [])
        header_keys = sorted({site["canonicalPathKey"] for site in header_sites})
        direct_unit = ""
        closed_unit = ""
        previous_unit = ""
        next_unit = ""
        candidate_units: list[str] = []
        if direct_sites:
            direct_path_key = direct_sites[0]["canonicalPathKey"]
            direct_unit = unit_by_path[direct_path_key]["unitKey"]
            disposition = "DIRECT_CPP"
            grade = "DIRECT_STATIC_CPP_PLATE"
            candidate_units = [direct_unit]
        else:
            index = bisect_right(span_starts, entry) - 1
            if index >= 0 and entry <= anchor_spans[index]["hi"]:
                closed_unit = anchor_spans[index]["unit"]
                disposition = "CLOSED_SPAN_SINGLE_CANDIDATE"
                grade = "CLOSED_SPAN_ORDER_PRIOR"
                candidate_units = [closed_unit]
                previous_unit = closed_unit
                next_unit = closed_unit
            elif index < 0:
                disposition = "BEFORE_FIRST_ANCHOR"
                grade = "NO_BOUNDED_PRIOR"
                next_unit = anchor_spans[0]["unit"]
            elif index == len(anchor_spans) - 1:
                disposition = "AFTER_LAST_ANCHOR"
                grade = "NO_BOUNDED_PRIOR"
                previous_unit = anchor_spans[-1]["unit"]
            else:
                previous_unit = anchor_spans[index]["unit"]
                next_unit = anchor_spans[index + 1]["unit"]
                disposition = "BETWEEN_SPANS_AMBIGUOUS"
                grade = "AMBIGUOUS_ORDER_GAP"
                candidate_units = sorted((previous_unit, next_unit))
        prior_rows.append({
            "functionEntityKey": entity, "entryVa": function["entryVa"], "currentName": function["currentName"],
            "bodyRangeSetSha256": function["bodyRangeSetSha256"], "directCppUnitKey": direct_unit,
            "directCppSiteCount": str(len(direct_sites)), "directHeaderPathKeys": ";".join(header_keys),
            "directHeaderSiteCount": str(len(header_sites)), "closedSpanUnitKey": closed_unit,
            "previousUnitKey": previous_unit, "nextUnitKey": next_unit,
            "candidateUnitKeys": ";".join(candidate_units), "priorDisposition": disposition,
            "evidenceGrade": grade,
        })

    secondary = _secondary_function_min(sites, owners)
    result = {
        "pathRows": path_rows, "siteRows": sites, "functionRows": function_rows,
        "unitRows": unit_rows, "priorRows": prior_rows, "secondary": secondary,
    }
    result["counts"] = validate_current_counts(result)
    return result


def _secondary_function_min(sites: list[dict[str, Any]], owners: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    relative_by_path: dict[str, str] = {}
    for site in sites:
        if (
            site["pathKind"] == "CPP"
            and site["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE"
            and site["pathOwnerKind"] == "FUNCTION"
            and site["lineEncoding"] != "NONE"
        ):
            grouped[(site["canonicalPathKey"], site["pathOwnerEntityKey"])].append(int(site["lineValue"]))
            relative_by_path[site["canonicalPathKey"]] = site["canonicalRelativePath"]
    per_unit: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for (path_key, function_key), values in grouped.items():
        per_unit[path_key].append((owners["functionByKey"][function_key]["entry"], min(values)))
    eligible = []
    for path_key, values in per_unit.items():
        values.sort()
        if len(values) >= 5:
            inversions = sum(left[1] > right[1] for left, right in zip(values, values[1:]))
            eligible.append({
                "canonicalRelativePath": relative_by_path[path_key], "functions": len(values),
                "pairs": len(values) - 1, "inversions": inversions,
            })
    eligible.sort(key=lambda row: row["canonicalRelativePath"])
    return {
        "eligibleUnits": len(eligible), "selectedFunctions": sum(row["functions"] for row in eligible),
        "adjacentPairs": sum(row["pairs"] for row in eligible),
        "inversions": sum(row["inversions"] for row in eligible), "units": eligible,
    }


def validate_current_counts(result: dict[str, Any]) -> dict[str, Any]:
    paths = result["pathRows"]
    sites = result["siteRows"]
    functions = result["functionRows"]
    units = result["unitRows"]
    priors = result["priorRows"]
    path_residual_entities = {row["pathOwnerEntityKey"] for row in sites if row["pathOwnerKind"] == "RESIDUAL"}
    call_residual_entities = {row["callOwnerEntityKey"] for row in sites if row["callOwnerKind"] == "RESIDUAL"}
    dispositions = Counter(row["priorDisposition"] for row in priors)
    target_counts = Counter(row["firstDirectCallTargetVa"] for row in sites)
    line_encodings = Counter(row["lineEncoding"] for row in sites)
    line_imm8 = [int(row["lineValue"]) for row in sites if row["lineEncoding"] == "PUSH_IMM8"]
    line_imm32 = [int(row["lineValue"]) for row in sites if row["lineEncoding"] == "PUSH_IMM32"]
    relation_counts = Counter(row["pathKind"] for row in functions)
    function_site_kind_counts = Counter(
        row["pathKind"] for row in sites if row["pathOwnerKind"] == "FUNCTION"
    )
    relation_multiplicity = Counter(row["functionEntityKey"] for row in functions)
    path_site_counts = [int(row["pushSiteCount"]) for row in paths]
    unit_site_totals = {
        "all": sum(int(row["allSiteCount"]) for row in units),
        "primary": sum(int(row["primarySiteCount"]) for row in units),
        "unwindFree": sum(int(row["unwindFreeSiteCount"]) for row in units),
        "mappedPrimary": sum(int(row["mappedPrimarySiteCount"]) for row in units),
        "residualPrimary": sum(int(row["residualPrimarySiteCount"]) for row in units),
        "primaryLineSites": sum(int(row["lineSiteCount"]) for row in units),
    }
    all_cpp_sites: dict[str, list[int]] = defaultdict(list)
    for row in sites:
        if row["pathKind"] == "CPP":
            all_cpp_sites[row["canonicalPathKey"]].append(int(row["siteVa"], 16))
    all_spans = sorted((min(values), max(values)) for values in all_cpp_sites.values())
    all_span_adjacent_overlaps = sum(
        left[1] >= right[0] for left, right in zip(all_spans, all_spans[1:])
    )
    reset_transitions = []
    for previous, current in zip(units, units[1:]):
        if current["lexicalResetBefore"] == "True":
            reset_transitions.append(
                f"{previous['canonicalRelativePath']}->{current['canonicalRelativePath']}"
            )
    header_prior_functions = [row for row in priors if int(row["directHeaderSiteCount"]) > 0]
    anchored_unit_rows = [row for row in units if row["anchorStatus"] == "ANCHORED"]
    function_aggregate = {
        "relations": len(functions),
        "functions": len(relation_multiplicity),
        "multiPathFunctions": sum(count > 1 for count in relation_multiplicity.values()),
        "maxPathsPerFunction": max(relation_multiplicity.values()),
        "relationsByKind": dict(sorted(relation_counts.items())),
        "sites": sum(int(row["siteCount"]) for row in functions),
        "sitesByKind": dict(sorted(function_site_kind_counts.items())),
        "decodedLineSites": sum(int(row["lineSiteCount"]) for row in functions),
        "primarySites": sum(int(row["primaryAllocatorSiteCount"]) for row in functions),
        "unwindFreeSites": sum(int(row["unwindFreeSiteCount"]) for row in functions),
        "crossingSites": sum(int(row["ownerBoundaryCrossingSiteCount"]) for row in functions),
    }
    secondary = result["secondary"]
    counts = {
        "rawPathStrings": len(paths),
        "rawCasefoldIdentities": len({row["rawPath"].casefold() for row in paths}),
        "canonicalPaths": len({row["canonicalPathKey"] for row in paths}),
        "canonicalCppPaths": len(units),
        "canonicalHeaderPaths": len({row["canonicalPathKey"] for row in paths if row["pathKind"] == "HEADER"}),
        "rawPathKinds": dict(sorted(Counter(row["pathKind"] for row in paths).items())),
        "canonicalPathKinds": dict(
            sorted(
                Counter(
                    {row["canonicalPathKey"]: row["pathKind"] for row in paths}.values()
                ).items()
            )
        ),
        "pathStringPushSites": {
            "sum": sum(path_site_counts), "min": min(path_site_counts), "max": max(path_site_counts),
            "zero": sum(count == 0 for count in path_site_counts),
        },
        "decodedCandidates": len(sites),
        "adjacentLineSites": sum(row["lineEncoding"] != "NONE" for row in sites),
        "unresolvedLineSites": sum(row["lineEncoding"] == "NONE" for row in sites),
        "lineEncodings": dict(sorted(line_encodings.items())),
        "lineValueRanges": {
            "PUSH_IMM8": {"min": min(line_imm8), "max": max(line_imm8)},
            "PUSH_IMM32": {"min": min(line_imm32), "max": max(line_imm32)},
        },
        "firstDirectCallTargets": dict(sorted(target_counts.items())),
        "primaryPlateSites": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" for row in sites),
        "unwindFreePlateSites": sum(row["plateClass"] == "UNWIND_FREE_SOURCE_PLATE" for row in sites),
        "pathFunctionSites": sum(row["pathOwnerKind"] == "FUNCTION" for row in sites),
        "pathResidualSites": sum(row["pathOwnerKind"] == "RESIDUAL" for row in sites),
        "pathTouchedResidualEntities": len(path_residual_entities),
        "pathResidualSiteStates": dict(
            sorted(Counter(row["pathResidualObservationState"] for row in sites if row["pathOwnerKind"] == "RESIDUAL").items())
        ),
        "pathResidualEntityStates": dict(
            sorted(
                Counter(
                    {
                        row["pathOwnerEntityKey"]: row["pathResidualObservationState"]
                        for row in sites if row["pathOwnerKind"] == "RESIDUAL"
                    }.values()
                ).items()
            )
        ),
        "pathResidualSiteKinds": dict(
            sorted(Counter(row["pathKind"] for row in sites if row["pathOwnerKind"] == "RESIDUAL").items())
        ),
        "pathResidualClassifications": dict(
            sorted(Counter(row["pathResidualClassification"] for row in sites if row["pathOwnerKind"] == "RESIDUAL").items())
        ),
        "callFunctionSites": sum(row["callOwnerKind"] == "FUNCTION" for row in sites),
        "callResidualSites": sum(row["callOwnerKind"] == "RESIDUAL" for row in sites),
        "callTouchedResidualEntities": len(call_residual_entities),
        "ownerBoundaryCrossings": sum(row["ownerBoundaryCrossing"] == "True" for row in sites),
        "samePathAndCallOwnerSites": sum(row["ownerBoundaryCrossing"] == "False" for row in sites),
        "primaryAddressDistribution": {
            "below0x00570000": sum(
                row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" and int(row["siteVa"], 16) < 0x00570000
                for row in sites
            ),
            "middle0x00570000To0x005c8000": sum(
                row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE"
                and 0x00570000 <= int(row["siteVa"], 16) < 0x005C8000
                for row in sites
            ),
            "unwindFreeAtOrAbove0x005c8000": sum(
                row["plateClass"] == "UNWIND_FREE_SOURCE_PLATE" and int(row["siteVa"], 16) >= 0x005C8000
                for row in sites
            ),
        },
        "functionPathRelations": len(functions),
        "functionsWithPathEvidence": len({row["functionEntityKey"] for row in functions}),
        "functionEvidence": function_aggregate,
        "sourceUnits": len(units),
        "anchoredUnits": sum(row["anchorStatus"] == "ANCHORED" for row in units),
        "residualOnlyUnits": sum(row["anchorStatus"] == "RESIDUAL_ONLY" for row in units),
        "directCppFunctions": dispositions["DIRECT_CPP"],
        "sourceUnitSites": unit_site_totals,
        "sourceUnitAllSpanAdjacentOverlaps": all_span_adjacent_overlaps,
        "sourceUnitDirectFunctionSum": sum(int(row["directFunctionCount"]) for row in units),
        "anchorBounds": {
            "firstUnit": anchored_unit_rows[0]["canonicalRelativePath"],
            "firstEntryVa": anchored_unit_rows[0]["directFunctionFirstEntryVa"],
            "lastUnit": anchored_unit_rows[-1]["canonicalRelativePath"],
            "lastEntryVa": anchored_unit_rows[-1]["directFunctionLastEntryVa"],
        },
        "linkOrder": {
            "lexicalResets": sum(row["lexicalResetBefore"] == "True" for row in units),
            "runs": len({row["linkRunPrior"] for row in units}),
            "resetTransitions": reset_transitions,
        },
        "directHeaderEvidence": {
            "functions": len(header_prior_functions),
            "headerOnlyFunctions": sum(not row["directCppUnitKey"] for row in header_prior_functions),
            "cppAndHeaderFunctions": sum(bool(row["directCppUnitKey"]) for row in header_prior_functions),
            "sites": sum(int(row["directHeaderSiteCount"]) for row in header_prior_functions),
        },
        "functionPriors": len(priors),
        "closedAnchorFunctions": dispositions["DIRECT_CPP"] + dispositions["CLOSED_SPAN_SINGLE_CANDIDATE"],
        "priorDispositions": dict(sorted(dispositions.items())),
        "primaryLinePrior": {
            "eligibleUnits": sum(row["linePriorEligible"] == "True" for row in units),
            "adjacentPairs": sum(int(row["lineAdjacentPairCount"]) for row in units),
            "inversions": sum(int(row["lineInversionCount"]) for row in units),
        },
        "secondaryFunctionMinLinePrior": secondary,
    }
    expected = {
        "rawPathStrings": 166, "rawCasefoldIdentities": 163, "canonicalPaths": 162,
        "canonicalCppPaths": 151, "canonicalHeaderPaths": 11, "decodedCandidates": 1870,
        "rawPathKinds": {"CPP": 151, "HEADER": 15},
        "canonicalPathKinds": {"CPP": 151, "HEADER": 11},
        "pathStringPushSites": {"sum": 1870, "min": 1, "max": 269, "zero": 0},
        "adjacentLineSites": 1601, "unresolvedLineSites": 269,
        "lineEncodings": {"NONE": 269, "PUSH_IMM32": 962, "PUSH_IMM8": 639},
        "lineValueRanges": {
            "PUSH_IMM8": {"min": 7, "max": 127},
            "PUSH_IMM32": {"min": 128, "max": 4543},
        },
        "firstDirectCallTargets": {"0x00449d40": 493, "0x004a1810": 2, "0x005490e0": 1375},
        "primaryPlateSites": 1377, "unwindFreePlateSites": 493,
        "pathFunctionSites": 1845, "pathResidualSites": 25, "pathTouchedResidualEntities": 20,
        "pathResidualSiteStates": {"DARK": 18, "EXECUTED": 7},
        "pathResidualEntityStates": {"DARK": 13, "EXECUTED": 7},
        "pathResidualSiteKinds": {"CPP": 24, "HEADER": 1},
        "pathResidualClassifications": {"AMBIGUOUS": 18, "CODE_CANDIDATE": 7},
        "callFunctionSites": 1844, "callResidualSites": 26, "callTouchedResidualEntities": 21,
        "ownerBoundaryCrossings": 1, "samePathAndCallOwnerSites": 1869,
        "primaryAddressDistribution": {
            "below0x00570000": 1377, "middle0x00570000To0x005c8000": 0,
            "unwindFreeAtOrAbove0x005c8000": 493,
        },
        "functionPathRelations": 1007,
        "functionsWithPathEvidence": 987, "sourceUnits": 151, "anchoredUnits": 148,
        "residualOnlyUnits": 3, "directCppFunctions": 368, "functionPriors": 7595,
        "functionEvidence": {
            "relations": 1007, "functions": 987, "multiPathFunctions": 20,
            "maxPathsPerFunction": 2, "relationsByKind": {"CPP": 818, "HEADER": 189},
            "sites": 1845, "sitesByKind": {"CPP": 1605, "HEADER": 240},
            "decodedLineSites": 1577, "primarySites": 1352, "unwindFreeSites": 493,
            "crossingSites": 1,
        },
        "sourceUnitSites": {
            "all": 1629, "primary": 1179, "unwindFree": 450,
            "mappedPrimary": 1155, "residualPrimary": 24, "primaryLineSites": 1022,
        },
        "sourceUnitAllSpanAdjacentOverlaps": 109,
        "sourceUnitDirectFunctionSum": 368,
        "anchorBounds": {
            "firstUnit": "airunit.cpp", "firstEntryVa": "0x00402ad0",
            "lastUnit": "dxtrees.cpp", "lastEntryVa": "0x0055a420",
        },
        "linkOrder": {
            "lexicalResets": 4, "runs": 5,
            "resetTransitions": [
                "worldphysicsmanager.cpp->ltshell.cpp",
                "pcsoundmanager.cpp->fastvb.cpp",
                "mixermap.cpp->missionscript/asminstruction.cpp",
                "xboxasynccache.cpp->dxbattleline.cpp",
            ],
        },
        "directHeaderEvidence": {
            "functions": 145, "headerOnlyFunctions": 126, "cppAndHeaderFunctions": 19,
            "sites": 197,
        },
        "closedAnchorFunctions": 1833,
        "priorDispositions": {
            "AFTER_LAST_ANCHOR": 2744, "BEFORE_FIRST_ANCHOR": 56,
            "BETWEEN_SPANS_AMBIGUOUS": 2962, "CLOSED_SPAN_SINGLE_CANDIDATE": 1465,
            "DIRECT_CPP": 368,
        },
        "primaryLinePrior": {"eligibleUnits": 33, "adjacentPairs": 795, "inversions": 12},
    }
    for key, value in expected.items():
        require(counts.get(key) == value, f"current census count drift: {key}: {counts.get(key)!r} != {value!r}")
    expected_secondary = {
        "eligibleUnits": 8, "selectedFunctions": 111, "adjacentPairs": 103, "inversions": 0,
        "units": [
            {"canonicalRelativePath": "cphysicsscriptstatements.cpp", "functions": 15, "pairs": 14, "inversions": 0},
            {"canonicalRelativePath": "game.cpp", "functions": 6, "pairs": 5, "inversions": 0},
            {"canonicalRelativePath": "mesh.cpp", "functions": 5, "pairs": 4, "inversions": 0},
            {"canonicalRelativePath": "meshpart.cpp", "functions": 11, "pairs": 10, "inversions": 0},
            {"canonicalRelativePath": "missionscript/asminstruction.cpp", "functions": 12, "pairs": 11, "inversions": 0},
            {"canonicalRelativePath": "missionscript/datatype.cpp", "functions": 5, "pairs": 4, "inversions": 0},
            {"canonicalRelativePath": "missionscript/iscript.cpp", "functions": 47, "pairs": 46, "inversions": 0},
            {"canonicalRelativePath": "worldphysicsmanager.cpp", "functions": 10, "pairs": 9, "inversions": 0},
        ],
    }
    require(secondary == expected_secondary, f"secondary function-min line prior drift: {secondary!r}")
    crossing = [row for row in sites if row["ownerBoundaryCrossing"] == "True"]
    require(
        len(crossing) == 1
        and crossing[0]["lineInstructionVa"] == "0x00437a27"
        and crossing[0]["lineValue"] == "212"
        and crossing[0]["siteVa"] == "0x00437a2c"
        and crossing[0]["firstDirectCallVa"] == "0x00437a3a"
        and crossing[0]["firstDirectCallTargetVa"] == "0x005490e0"
        and crossing[0]["canonicalRelativePath"] == "cphysicsscriptstatements.cpp"
        and crossing[0]["pathOwnerEntityKey"]
        == f"CODE:{SPECIMEN_SHA256}:VA=0x00437490:RANGES=0eaddd1099b6a7d16e64fe31014f8d219e0b8a80ea33ed805b597b9e1419e4f6"
        and crossing[0]["pathOwnerIntervalEndVa"] == "0x00437a3a"
        and crossing[0]["pathFunctionEntryVa"] == "0x00437490"
        and crossing[0]["pathFunctionName"] == "CPhysicsScriptStatements__CreateStatementType5"
        and crossing[0]["pathFunctionBodyRangeSetSha256"]
        == "0eaddd1099b6a7d16e64fe31014f8d219e0b8a80ea33ed805b597b9e1419e4f6"
        and crossing[0]["callOwnerKind"] == "RESIDUAL"
        and crossing[0]["callOwnerEntityKey"]
        == f"TEXT_RESIDUAL:{SPECIMEN_SHA256}:0x00437A3A-0x00437A5C"
        and crossing[0]["callOwnerIntervalStartVa"] == "0x00437a3a"
        and crossing[0]["callOwnerIntervalEndVa"] == "0x00437a5c",
        "required 0x00437a3a owner crossing drift",
    )
    residual_only = sorted(row["canonicalRelativePath"] for row in units if row["anchorStatus"] == "RESIDUAL_ONLY")
    require(residual_only == ["bomber.cpp", "carver.cpp", "fepmain.cpp"], "residual-only unit set drift")
    residual_primary_sites: dict[str, list[str]] = defaultdict(list)
    for row in sites:
        if (
            row["pathKind"] == "CPP"
            and row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE"
            and row["pathOwnerKind"] == "RESIDUAL"
            and row["canonicalRelativePath"] in residual_only
        ):
            residual_primary_sites[row["canonicalRelativePath"]].append(row["siteVa"])
    require(
        {key: sorted(value) for key, value in residual_primary_sites.items()}
        == {
            "bomber.cpp": ["0x004160e4", "0x0041611d"],
            "carver.cpp": ["0x00422471", "0x004224aa"],
            "fepmain.cpp": ["0x00462879"],
        },
        "residual-only unit site set drift",
    )
    return counts


def _rows_by_output(result: dict[str, Any]) -> dict[str, tuple[tuple[str, ...], list[dict[str, Any]]]]:
    return {
        "source-path-strings.tsv": (PATH_COLUMNS, result["pathRows"]),
        "source-sites.tsv": (SITE_COLUMNS, result["siteRows"]),
        "function-source-evidence.tsv": (FUNCTION_EVIDENCE_COLUMNS, result["functionRows"]),
        "source-units.tsv": (UNIT_COLUMNS, result["unitRows"]),
        "function-unit-priors.tsv": (PRIOR_COLUMNS, result["priorRows"]),
    }


def _derive_from_inputs(specimen: Path, campaign_ready: Path, expected_campaign_hash: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    require(specimen.is_file() and not specimen.is_symlink(), "specimen is not a plain file")
    require(specimen.stat().st_size == SPECIMEN_BYTES and sha256_file(specimen) == SPECIMEN_SHA256, "not the pristine specimen")
    data = specimen.read_bytes()
    pe = parse_pe(data)
    campaign = validate_campaign(campaign_ready, expected_campaign_hash, specimen)
    owners = load_owner_intervals(campaign["dir"])
    paths = scan_paths(data, pe)
    candidates = scan_candidates(data, pe, paths)
    result = derive(data, pe, paths, candidates, owners)
    return result, campaign, pe


def _campaign_envelope(campaign: dict[str, Any], repo: Path) -> dict[str, Any]:
    ready = campaign["ready"]
    directory = campaign["dir"]
    def frozen_stamp(value: object, label: str) -> dict[str, Any]:
        require(isinstance(value, dict), f"campaign {label} stamp missing")
        require(set(value) >= {"path", "bytes", "sha256"}, f"campaign {label} stamp malformed")
        return {"path": value["path"], "bytes": value["bytes"], "sha256": value["sha256"]}

    return {
        "path": directory.resolve().relative_to(repo.resolve()).as_posix(),
        "ready": stamp(directory / "campaign.ready.json", directory),
        "generation": ready["generation"],
        "reducerId": ready["reducer"]["id"],
        "outputs": {name: stamp(directory / name, directory) for name in CAMPAIGN_OUTPUTS},
        "sourceSnapshot": {
            "specimen": frozen_stamp(ready["sourceSnapshot"]["specimen"], "snapshot specimen"),
            "program": ready["sourceSnapshot"]["parityGraph"]["program"],
            "functionCount": ready["sourceSnapshot"]["parityGraph"]["functionCount"],
            "rangeCount": ready["sourceSnapshot"]["parityGraph"]["rangeCount"],
            "bodyRanges": frozen_stamp(ready["sourceSnapshot"]["parityGraph"]["bodyRanges"], "body ranges"),
            "parityReady": frozen_stamp(ready["sourceSnapshot"]["parityGraph"]["receipt"], "parity READY"),
        },
    }


def write_bundle(specimen: Path, campaign_ready: Path, expected_campaign_hash: str, out: Path) -> dict[str, Any]:
    require(not out.exists() and not out.is_symlink(), f"destination already exists: {out}")
    result, campaign, pe = _derive_from_inputs(specimen.resolve(), campaign_ready.resolve(), expected_campaign_hash)
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.stage-", dir=out.parent))
    try:
        owner_destination = stage / "source-unit-owner.py"
        shutil.copyfile(Path(__file__).resolve(), owner_destination)
        for name, (columns, rows) in _rows_by_output(result).items():
            (stage / name).write_bytes(render_tsv(columns, rows))
        repo = campaign["repo"]
        text = pe["text"]
        data_section = pe["data"]
        ready = {
            "schema": SCHEMA,
            "status": STATUS,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "tool": stamp(owner_destination, stage),
            "decoder": {"name": "capstone", "version": CAPSTONE_VERSION, "arch": "x86", "mode": 32, "maxForwardBytes": MAX_FORWARD_BYTES},
            "specimen": stamp(specimen.resolve()),
            "campaign": _campaign_envelope(campaign, repo),
            "pe": {
                "machine": "0x014c", "sectionCount": 4, "optionalMagic": "0x010b", "optionalHeaderBytes": 224,
                "imageBase": va(IMAGE_BASE),
                "text": {"rva": va(text["rva"]), "rawPointer": va(text["rawPointer"]), "virtualBytes": text["virtualSize"], "rawBytes": text["rawSize"], "startVa": va(IMAGE_BASE + text["rva"]), "endExclusiveVa": va(IMAGE_BASE + text["rva"] + text["virtualSize"])},
                "data": {"rva": va(data_section["rva"]), "rawPointer": va(data_section["rawPointer"]), "virtualBytes": data_section["virtualSize"], "rawBytes": data_section["rawSize"]},
            },
            "pathPolicy": PATH_POLICY,
            "platePolicy": PLATE_POLICY,
            "joinPolicy": JOIN_POLICY,
            "unitPriorPolicy": UNIT_PRIOR_POLICY,
            "counts": result["counts"],
            "outputs": {name: stamp(stage / name, stage) for name in OUTPUTS},
            "claimBoundary": CLAIM_BOUNDARY,
        }
        (stage / "source-unit-census.ready.json").write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8", newline="")
        verify_bundle(stage)
        os.replace(stage, out)
        return read_json(out / "source-unit-census.ready.json", "published READY")
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _resolve_campaign_from_ready(ready: dict[str, Any], specimen: Path) -> tuple[Path, str]:
    campaign = ready.get("campaign")
    require(isinstance(campaign, dict), "READY campaign envelope missing")
    campaign_path = str(campaign.get("path", ""))
    # The specimen is repository-local for the current evidence owner. Resolve the
    # recorded local-lab path only beneath that owning repository.
    repo = None
    for candidate in (specimen.parent, *specimen.parents):
        if (candidate / "README.MD").is_file() and (candidate / "local-lab").is_dir():
            repo = candidate
            break
    require(repo is not None, "cannot locate repository for frozen campaign input")
    campaign_dir = _validate_external_repo_path(repo, campaign_path, "READY campaign")
    campaign_ready = campaign_dir / "campaign.ready.json"
    expected = campaign.get("ready")
    require(isinstance(expected, dict) and expected.get("sha256"), "READY campaign stamp missing")
    return campaign_ready, str(expected["sha256"])


def verify_bundle(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    ready_path = bundle / "source-unit-census.ready.json"
    ready = read_json(ready_path, "source-unit census READY")
    require(set(ready) == {"schema", "status", "generatedAtUtc", "tool", "decoder", "specimen", "campaign", "pe", "pathPolicy", "platePolicy", "joinPolicy", "unitPriorPolicy", "counts", "outputs", "claimBoundary"}, "READY top-level field drift")
    require(ready.get("schema") == SCHEMA and ready.get("status") == STATUS, "READY schema/status drift")
    try:
        generated = datetime.fromisoformat(str(ready["generatedAtUtc"]))
    except ValueError as exc:
        raise CensusError("READY timestamp is invalid") from exc
    require(generated.tzinfo is not None, "READY timestamp is not timezone-aware")
    require(ready.get("decoder") == {"name": "capstone", "version": CAPSTONE_VERSION, "arch": "x86", "mode": 32, "maxForwardBytes": MAX_FORWARD_BYTES}, "decoder policy drift")
    require(capstone.__version__ == CAPSTONE_VERSION, "runtime Capstone version drift")
    require(ready.get("pathPolicy") == PATH_POLICY and ready.get("platePolicy") == PLATE_POLICY, "path/plate policy drift")
    require(ready.get("joinPolicy") == JOIN_POLICY and ready.get("unitPriorPolicy") == UNIT_PRIOR_POLICY, "join/unit prior policy drift")
    require(ready.get("claimBoundary") == CLAIM_BOUNDARY, "claim boundary drift")
    outputs = ready.get("outputs")
    require(isinstance(outputs, dict) and set(outputs) == set(OUTPUTS), "output manifest drift")
    entries = list(bundle.rglob("*"))
    require(not any(path.is_symlink() for path in entries), "bundle contains a symlink")
    require(all(path.is_file() for path in entries), "bundle contains an unmanifested directory or special entry")
    actual_tree = {path.relative_to(bundle).as_posix() for path in entries}
    require(actual_tree == set(OUTPUTS) | {"source-unit-census.ready.json"}, "bundle contains unmanifested/missing files")
    for name in OUTPUTS:
        validate_stamp(bundle / name, outputs[name], f"bundle output {name}")
    owner = bundle / "source-unit-owner.py"
    require(sha256_file(Path(__file__).resolve()) == sha256_file(owner), "running tool differs from frozen owner")
    specimen_stamp = ready.get("specimen")
    require(isinstance(specimen_stamp, dict), "READY specimen stamp missing")
    specimen = Path(str(specimen_stamp.get("path", ""))).resolve()
    validate_stamp(specimen, specimen_stamp, "READY specimen")
    campaign_ready, campaign_hash = _resolve_campaign_from_ready(ready, specimen)
    result, campaign, pe = _derive_from_inputs(specimen, campaign_ready, campaign_hash)
    require(ready.get("campaign") == _campaign_envelope(campaign, campaign["repo"]), "campaign envelope drift")
    text = pe["text"]
    data_section = pe["data"]
    expected_pe = {
        "machine": "0x014c", "sectionCount": 4, "optionalMagic": "0x010b", "optionalHeaderBytes": 224,
        "imageBase": va(IMAGE_BASE),
        "text": {"rva": va(text["rva"]), "rawPointer": va(text["rawPointer"]), "virtualBytes": text["virtualSize"], "rawBytes": text["rawSize"], "startVa": va(IMAGE_BASE + text["rva"]), "endExclusiveVa": va(IMAGE_BASE + text["rva"] + text["virtualSize"])},
        "data": {"rva": va(data_section["rva"]), "rawPointer": va(data_section["rawPointer"]), "virtualBytes": data_section["virtualSize"], "rawBytes": data_section["rawSize"]},
    }
    require(ready.get("pe") == expected_pe, "PE envelope drift")
    require(ready.get("counts") == result["counts"], "READY counts/state drift")
    for name, (columns, rows) in _rows_by_output(result).items():
        actual_rows = read_exact_tsv(bundle / name, columns, name)
        expected_bytes = render_tsv(columns, rows)
        require((bundle / name).read_bytes() == expected_bytes, f"{name} does not rederive byte-exactly")
        require(len(actual_rows) == len(rows), f"{name} row-count drift")
    return ready


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    writer = commands.add_parser("write", help="derive one immutable source-unit census")
    writer.add_argument("--specimen", type=Path, required=True)
    writer.add_argument("--campaign-ready", type=Path, required=True)
    writer.add_argument("--expected-campaign-ready-sha256", required=True)
    writer.add_argument("--out", type=Path, required=True)
    verifier = commands.add_parser("verify", help="rederive and verify a frozen census")
    verifier.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "write":
            receipt = write_bundle(args.specimen, args.campaign_ready, args.expected_campaign_ready_sha256, args.out)
            print(f"SOURCE_UNIT_CENSUS_READY sites={receipt['counts']['decodedCandidates']} units={receipt['counts']['sourceUnits']} out={args.out}")
        else:
            receipt = verify_bundle(args.bundle)
            print(f"SOURCE_UNIT_CENSUS_VERIFIED sites={receipt['counts']['decodedCandidates']} units={receipt['counts']['sourceUnits']} bundle={args.bundle}")
        return 0
    except (CensusError, OSError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
