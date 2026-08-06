#!/usr/bin/env python3
"""Build and verify a specimen-bound Battle Engine Aquila string corpus.

The corpus deliberately separates two evidence classes:

* strings defined by the reviewed Ghidra project; and
* raw printable byte candidates found without trusting Ghidra's definitions.

The tracked Markdown is a complete rendering of the first class.  The larger
raw candidate tables remain in ``local-lab`` because executable bytes can look
printable by accident and are not automatically string literals.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import os
import struct
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "bea.re.binary-strings-corpus.v1"
EXPECTED_SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
RAW_HEADER = (
    "file_offset",
    "address",
    "section",
    "encoding",
    "char_count",
    "byte_length",
    "nul_terminated",
    "value_utf8_sha256",
    "value_json",
)
ALL_HEADER = (
    "file_offset",
    "address",
    "section",
    "origin",
    "encoding",
    "char_count",
    "byte_length",
    "nul_terminated",
    "ghidra_defined",
    "data_type",
    "xref_count",
    "code_xref_count",
    "function_entries",
    "value_utf8_sha256",
    "value_json",
)
DISTINCT_HEADER = (
    "value_utf8_sha256",
    "char_count",
    "defined_occurrences",
    "raw_occurrences",
    "terminated_raw_occurrences",
    "xref_count",
    "sections",
    "first_address",
    "value_json",
)


class CorpusError(RuntimeError):
    """Raised when an input or receipt violates the corpus contract."""


@dataclass(frozen=True)
class Section:
    name: str
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int


@dataclass(frozen=True)
class PeImage:
    image_base: int
    size_of_headers: int
    sections: tuple[Section, ...]

    def locate(self, file_offset: int) -> tuple[str, int | None]:
        if 0 <= file_offset < self.size_of_headers:
            return "Headers", self.image_base + file_offset
        for section in self.sections:
            if section.raw_offset <= file_offset < section.raw_offset + section.raw_size:
                delta = file_offset - section.raw_offset
                return section.name, self.image_base + section.virtual_address + delta
        return "Overlay", None


@dataclass(frozen=True)
class RawString:
    file_offset: int
    address: int | None
    section: str
    encoding: str
    value: str
    byte_length: int
    nul_terminated: bool


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name, suffix=".partial", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def parse_pe(data: bytes) -> PeImage:
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise CorpusError("specimen is not a DOS/PE image")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if pe_offset + 24 > len(data) or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise CorpusError("invalid PE signature")
    section_count = struct.unpack_from("<H", data, pe_offset + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    optional_offset = pe_offset + 24
    if optional_offset + optional_size > len(data):
        raise CorpusError("truncated PE optional header")
    magic = struct.unpack_from("<H", data, optional_offset)[0]
    if magic != 0x10B:
        raise CorpusError(f"expected PE32 optional header, got 0x{magic:04x}")
    image_base = struct.unpack_from("<I", data, optional_offset + 28)[0]
    size_of_headers = struct.unpack_from("<I", data, optional_offset + 60)[0]
    section_offset = optional_offset + optional_size
    sections: list[Section] = []
    for index in range(section_count):
        row_offset = section_offset + index * 40
        if row_offset + 40 > len(data):
            raise CorpusError("truncated PE section table")
        raw_name = data[row_offset : row_offset + 8].split(b"\0", 1)[0]
        name = raw_name.decode("ascii", errors="strict")
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
            "<IIII", data, row_offset + 8
        )
        if raw_offset + raw_size > len(data):
            raise CorpusError(f"section {name} exceeds the specimen")
        sections.append(Section(name, virtual_address, virtual_size, raw_offset, raw_size))
    return PeImage(image_base, size_of_headers, tuple(sections))


def ascii_printable(value: int) -> bool:
    return value in (9, 10, 13) or 0x20 <= value <= 0x7E


def wide_printable(value: int) -> bool:
    if value in (9, 10, 13):
        return True
    # The shipped PC localization set is western-European.  Treating every
    # Unicode code unit for which Python says ``isprintable`` as a candidate
    # turns arbitrary x86 byte pairs into hundreds of thousands of fake CJK
    # strings.  These bounded ranges retain ASCII, Latin-1/Extended text and
    # common Unicode punctuation while keeping the raw scan falsifiable.
    return (
        0x20 <= value <= 0x7E
        or 0x00A0 <= value <= 0x024F
        or 0x2000 <= value <= 0x206F
        or value == 0x20AC
    )


def scan_raw_strings(data: bytes, pe: PeImage, minimum: int = 4) -> list[RawString]:
    if minimum < 2:
        raise CorpusError("minimum raw string length must be at least two characters")
    results: list[RawString] = []

    index = 0
    while index < len(data):
        if not ascii_printable(data[index]):
            index += 1
            continue
        start = index
        while index < len(data) and ascii_printable(data[index]):
            index += 1
        if index - start >= minimum:
            value = data[start:index].decode("ascii")
            section, address = pe.locate(start)
            results.append(
                RawString(start, address, section, "ascii", value, index - start,
                          index < len(data) and data[index] == 0)
            )

    for phase in (0, 1):
        index = phase
        while index + 1 < len(data):
            unit = struct.unpack_from("<H", data, index)[0]
            if not wide_printable(unit):
                index += 2
                continue
            start = index
            units: list[int] = []
            while index + 1 < len(data):
                unit = struct.unpack_from("<H", data, index)[0]
                if not wide_printable(unit):
                    break
                units.append(unit)
                index += 2
            if len(units) >= minimum:
                value = "".join(chr(unit) for unit in units)
                section, address = pe.locate(start)
                results.append(
                    RawString(start, address, section, "utf-16le", value, index - start,
                              index + 1 < len(data) and data[index : index + 2] == b"\0\0")
                )
            if index == start:
                index += 2

    unique = {
        (item.file_offset, item.encoding, item.value, item.byte_length): item for item in results
    }
    return sorted(unique.values(), key=lambda item: (item.file_offset, item.encoding, item.value))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exception:
        raise CorpusError(f"cannot read JSON {path}: {exception}") from exception
    if not isinstance(value, dict):
        raise CorpusError(f"JSON root is not an object: {path}")
    return value


def load_defined_strings(tsv_path: Path, ready_path: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    ready = read_json(ready_path)
    if ready.get("schema") != "bea.re.ghidra-defined-strings.v1" or ready.get("status") != "READY":
        raise CorpusError("defined-string receipt has the wrong schema or status")
    if str(ready.get("executableSha256", "")).lower() != EXPECTED_SPECIMEN_SHA256:
        raise CorpusError("defined-string receipt is bound to the wrong specimen")
    output = ready.get("output")
    if not isinstance(output, dict):
        raise CorpusError("defined-string receipt has no output object")
    actual_bytes = tsv_path.read_bytes()
    if len(actual_bytes) != output.get("bytes") or sha256_bytes(actual_bytes) != output.get("sha256"):
        raise CorpusError("defined-string TSV does not match its READY receipt")
    text = actual_bytes.decode("utf-8")
    physical_lines = text.splitlines()
    if not physical_lines:
        raise CorpusError("defined-string TSV is empty")
    fieldnames = physical_lines[0].split("\t")
    rows = []
    for line_number, line in enumerate(physical_lines[1:], 2):
        values = line.split("\t")
        if len(values) != len(fieldnames):
            raise CorpusError(
                f"defined-string TSV row {line_number} has {len(values)} fields; expected {len(fieldnames)}"
            )
        rows.append(dict(zip(fieldnames, values)))
    if len(rows) != ready.get("definedStringRows"):
        raise CorpusError("defined-string row count does not match its READY receipt")
    required = {
        "address", "file_offset", "section", "data_type", "char_count", "byte_length",
        "value_utf8_sha256", "xref_count", "code_xref_count", "function_entries", "value_json",
    }
    if not rows or set(fieldnames) != required:
        raise CorpusError("defined-string TSV header is not the exact expected schema")
    for row in rows:
        value = json.loads(row["value_json"])
        if not isinstance(value, str):
            raise CorpusError("defined-string value_json did not decode to a string")
        if sha256_bytes(value.encode("utf-8")) != row["value_utf8_sha256"]:
            raise CorpusError(f"defined-string value hash mismatch at {row['address']}")
        row["value"] = value
    return rows, ready


def tsv_bytes(header: Iterable[str], rows: Iterable[Iterable[Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(tuple(header))
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def address_text(value: int | None) -> str:
    return "" if value is None else f"0x{value:08x}"


def offset_text(value: int | None) -> str:
    return "" if value is None else f"0x{value:08x}"


def markdown_code(value: str) -> str:
    encoded = json.dumps(value, ensure_ascii=False)
    return "<code>" + html.escape(encoded, quote=False).replace("|", "&#124;") + "</code>"


def build_markdown(
    defined_rows: list[dict[str, str]],
    raw_rows: list[RawString],
    specimen_path: Path,
    artifact_summaries: dict[str, dict[str, Any]],
    corpus_root: Path,
) -> bytes:
    distinct_defined = len({row["value"] for row in defined_rows})
    referenced = sum(1 for row in defined_rows if int(row["xref_count"]) > 0)
    raw_terminated = sum(1 for row in raw_rows if row.nul_terminated)
    sections: dict[str, int] = {}
    for row in defined_rows:
        sections[row["section"]] = sections.get(row["section"], 0) + 1
    repo_root = Path(__file__).resolve().parent.parent
    try:
        corpus_label = corpus_root.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        corpus_label = str(corpus_root.resolve())

    lines = [
        "# Battle Engine Aquila binary strings",
        "",
        "Status: specimen-bound complete Ghidra-defined string inventory plus a separately",
        "verified raw printable-candidate corpus.",
        "",
        "Last updated: 2026-08-03",
        "",
        "Evidence: MEASURED — exact pristine bytes joined to a read-only export from the",
        "verified post-promotion Ghidra project; runtime reachability remains separate.",
        "",
        f"Specimen: `{EXPECTED_SPECIMEN_SHA256}` ({specimen_path.name}, {specimen_path.stat().st_size:,} bytes).",
        "",
        "Summary: complete tracked inventory of Ghidra-defined executable strings, with",
        "the broader raw printable scan retained as graded machine-local evidence.",
        "",
        "This file contains every string data item defined in the verified post-promotion",
        "Ghidra project. It is bound to the repo-designated unpatched retail baseline",
        f"`{EXPECTED_SPECIMEN_SHA256}` ({specimen_path.name}, {specimen_path.stat().st_size:,} bytes).",
        "A definition is static evidence that Ghidra recognizes data as a string; it is not",
        "proof that retail executes, displays, or honors the value.",
        "",
        "A byte-only scan is also retained under",
        f"`{corpus_label}/`. It records every maximal ASCII or",
        "UTF-16LE printable run of at least four characters, including non-NUL-terminated",
        "runs. Those candidates intentionally stay out of the table below because x86",
        "instructions and packed data can look printable by accident. They remain searchable",
        "evidence for strings that Ghidra may not have defined.",
        "",
        "## Exact census",
        "",
        f"- Ghidra-defined string occurrences: **{len(defined_rows):,}**.",
        f"- Distinct Ghidra-defined values: **{distinct_defined:,}**.",
        f"- Defined occurrences with at least one xref to their start: **{referenced:,}**.",
        f"- Raw printable candidates: **{len(raw_rows):,}**, of which **{raw_terminated:,}** are NUL-terminated.",
        "- Defined-string TSV SHA-256: `" + artifact_summaries["defined-strings.tsv"]["sha256"] + "`.",
        "- Raw-candidate TSV SHA-256: `" + artifact_summaries["raw-printable-candidates.tsv"]["sha256"] + "`.",
        "- Joined occurrence TSV SHA-256: `" + artifact_summaries["all-string-occurrences.tsv"]["sha256"] + "`.",
        "- Distinct-value TSV SHA-256: `" + artifact_summaries["distinct-string-values.tsv"]["sha256"] + "`.",
        "",
        "Defined rows by memory block: " + ", ".join(
            f"`{name}` {count:,}" for name, count in sorted(sections.items())
        ) + ".",
        "",
        "## How to use this evidence",
        "",
        "Search the full table by tool name, switch, path, assertion, format string, class",
        "token, resource extension, or output filename. Prefer rows with code xrefs and a",
        "small owning-function set. Then inspect the exact xref and body; do not infer a live",
        "feature from a string alone. Raw-only candidates require an additional definition/xref",
        "or controlled runtime observation before semantic promotion.",
        "",
        "The local joined TSV is the agent/mining surface: it adds raw-only candidates and",
        "machine-friendly xref/function fields without making this tracked document a second",
        "Ghidra database.",
        "",
        "## Complete Ghidra-defined inventory",
        "",
        "| Address | File offset | Block | Data type | Chars | Bytes | Xrefs | Code xrefs | Referencing functions | Value |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in defined_rows:
        functions = row["function_entries"] or "—"
        lines.append(
            "| `0x" + row["address"].lower() + "`"
            + " | `" + (row["file_offset"] or "—") + "`"
            + " | `" + row["section"].replace("|", "\\|") + "`"
            + " | `" + row["data_type"].replace("|", "\\|") + "`"
            + " | " + row["char_count"]
            + " | " + row["byte_length"]
            + " | " + row["xref_count"]
            + " | " + row["code_xref_count"]
            + " | `" + functions.replace("|", "\\|") + "`"
            + " | " + markdown_code(row["value"]) + " |"
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def artifact(path: Path) -> dict[str, Any]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def extract(args: argparse.Namespace) -> int:
    specimen = args.specimen.resolve()
    specimen_bytes = specimen.read_bytes()
    specimen_sha256 = sha256_bytes(specimen_bytes)
    if specimen_sha256 != EXPECTED_SPECIMEN_SHA256:
        raise CorpusError(
            f"specimen SHA-256 mismatch: expected {EXPECTED_SPECIMEN_SHA256}, got {specimen_sha256}"
        )
    pe = parse_pe(specimen_bytes)
    defined_rows, defined_ready = load_defined_strings(
        args.defined_tsv.resolve(), args.defined_ready.resolve()
    )
    raw_rows = scan_raw_strings(specimen_bytes, pe, args.minimum)

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw-printable-candidates.tsv"
    all_path = out_dir / "all-string-occurrences.tsv"
    distinct_path = out_dir / "distinct-string-values.tsv"

    raw_table = tsv_bytes(
        RAW_HEADER,
        (
            (
                offset_text(row.file_offset), address_text(row.address), row.section, row.encoding,
                len(row.value), row.byte_length, str(row.nul_terminated).lower(),
                sha256_bytes(row.value.encode("utf-8")), json.dumps(row.value, ensure_ascii=False),
            )
            for row in raw_rows
        ),
    )
    atomic_write(raw_path, raw_table)

    defined_by_key: dict[tuple[int, str], list[dict[str, str]]] = {}
    for row in defined_rows:
        defined_by_key.setdefault((int(row["address"], 16), row["value"]), []).append(row)

    all_records: list[dict[str, Any]] = []
    matched_defined: set[int] = set()
    for raw in raw_rows:
        matches = [] if raw.address is None else defined_by_key.get((raw.address, raw.value), [])
        if matches:
            for match in matches:
                matched_defined.add(id(match))
            primary = matches[0]
            all_records.append({
                "file_offset": raw.file_offset, "address": raw.address, "section": raw.section,
                "origin": "RAW_AND_GHIDRA_DEFINED", "encoding": raw.encoding,
                "value": raw.value, "byte_length": raw.byte_length,
                "nul_terminated": raw.nul_terminated, "ghidra_defined": True,
                "data_type": primary["data_type"], "xref_count": sum(int(r["xref_count"]) for r in matches),
                "code_xref_count": sum(int(r["code_xref_count"]) for r in matches),
                "function_entries": ",".join(sorted({f for r in matches for f in r["function_entries"].split(",") if f})),
            })
        else:
            all_records.append({
                "file_offset": raw.file_offset, "address": raw.address, "section": raw.section,
                "origin": "RAW_ONLY", "encoding": raw.encoding, "value": raw.value,
                "byte_length": raw.byte_length, "nul_terminated": raw.nul_terminated,
                "ghidra_defined": False, "data_type": "", "xref_count": 0,
                "code_xref_count": 0, "function_entries": "",
            })
    for row in defined_rows:
        if id(row) in matched_defined:
            continue
        file_offset = int(row["file_offset"], 16) if row["file_offset"] else None
        all_records.append({
            "file_offset": file_offset, "address": int(row["address"], 16), "section": row["section"],
            "origin": "GHIDRA_DEFINED_ONLY", "encoding": "ghidra:" + row["data_type"],
            "value": row["value"], "byte_length": int(row["byte_length"]),
            "nul_terminated": False, "ghidra_defined": True, "data_type": row["data_type"],
            "xref_count": int(row["xref_count"]), "code_xref_count": int(row["code_xref_count"]),
            "function_entries": row["function_entries"],
        })
    all_records.sort(key=lambda row: (
        row["file_offset"] is None, row["file_offset"] or 0, row["origin"], row["encoding"], row["value"]
    ))
    all_table = tsv_bytes(
        ALL_HEADER,
        (
            (
                offset_text(row["file_offset"]), address_text(row["address"]), row["section"],
                row["origin"], row["encoding"], len(row["value"]), row["byte_length"],
                str(row["nul_terminated"]).lower(), str(row["ghidra_defined"]).lower(),
                row["data_type"], row["xref_count"], row["code_xref_count"], row["function_entries"],
                sha256_bytes(row["value"].encode("utf-8")), json.dumps(row["value"], ensure_ascii=False),
            )
            for row in all_records
        ),
    )
    atomic_write(all_path, all_table)

    aggregate: dict[str, dict[str, Any]] = {}
    for row in all_records:
        entry = aggregate.setdefault(row["value"], {
            "defined": 0, "raw": 0, "terminated": 0, "xrefs": 0, "sections": set(),
            "addresses": [],
        })
        if row["ghidra_defined"]:
            entry["defined"] += 1
        if row["origin"] != "GHIDRA_DEFINED_ONLY":
            entry["raw"] += 1
            entry["terminated"] += int(row["nul_terminated"])
        entry["xrefs"] += row["xref_count"]
        entry["sections"].add(row["section"])
        if row["address"] is not None:
            entry["addresses"].append(row["address"])
    distinct_table = tsv_bytes(
        DISTINCT_HEADER,
        (
            (
                sha256_bytes(value.encode("utf-8")), len(value), item["defined"], item["raw"],
                item["terminated"], item["xrefs"], ",".join(sorted(item["sections"])),
                address_text(min(item["addresses"])) if item["addresses"] else "",
                json.dumps(value, ensure_ascii=False),
            )
            for value, item in sorted(
                aggregate.items(),
                key=lambda pair: (-pair[1]["defined"], -pair[1]["xrefs"], pair[0].casefold(), pair[0]),
            )
        ),
    )
    atomic_write(distinct_path, distinct_table)

    summaries = {
        "defined-strings.tsv": artifact(args.defined_tsv.resolve()),
        "raw-printable-candidates.tsv": artifact(raw_path),
        "all-string-occurrences.tsv": artifact(all_path),
        "distinct-string-values.tsv": artifact(distinct_path),
    }
    markdown_path = args.markdown.resolve()
    markdown = build_markdown(defined_rows, raw_rows, specimen, summaries, out_dir)
    atomic_write(markdown_path, markdown)
    summaries[markdown_path.name] = artifact(markdown_path)

    ready_path = out_dir / "binary-strings.ready.json"
    ready = {
        "schema": SCHEMA,
        "status": "READY",
        "specimen": {"path": str(specimen), "bytes": len(specimen_bytes), "sha256": specimen_sha256},
        "pe": {
            "imageBase": f"0x{pe.image_base:08x}",
            "sizeOfHeaders": pe.size_of_headers,
            "sections": [section.__dict__ for section in pe.sections],
        },
        "definition": {
            "minimumRawCharacters": args.minimum,
            "rawEncodings": ["ascii", "utf-16le"],
            "rawIncludesNonTerminated": True,
            "trackedMarkdownContains": "all Ghidra-defined string occurrences",
            "rawCandidateClaim": "printable byte candidates, not automatically literals",
        },
        "counts": {
            "ghidraDefinedOccurrences": len(defined_rows),
            "ghidraDistinctValues": len({row["value"] for row in defined_rows}),
            "rawCandidates": len(raw_rows),
            "rawNulTerminated": sum(1 for row in raw_rows if row.nul_terminated),
            "joinedOccurrences": len(all_records),
            "joinedDistinctValues": len(aggregate),
        },
        "inputs": {
            "definedReady": artifact(args.defined_ready.resolve()),
            "definedReadyIdentity": {
                "schema": defined_ready["schema"],
                "rows": defined_ready["definedStringRows"],
                "outputSha256": defined_ready["output"]["sha256"],
            },
            "ghidraExporter": artifact((Path(__file__).resolve().parent / "ExportDefinedStrings.java")),
            "corpusOwner": artifact(Path(__file__).resolve()),
        },
        "outputs": summaries,
        "claimBoundary": [
            "Ghidra-defined rows are static string-data observations, not runtime reachability.",
            "Raw printable candidates may be instruction/data noise and carry no semantic authority alone.",
            "Xrefs to a string start narrow investigation but do not prove a dormant feature is usable.",
        ],
    }
    atomic_write(ready_path, canonical_json(ready))
    print(json.dumps({"status": "READY", "ready": str(ready_path), "counts": ready["counts"]}, indent=2))
    return 0


def verify(args: argparse.Namespace) -> int:
    ready_path = args.ready.resolve()
    ready = read_json(ready_path)
    if ready.get("schema") != SCHEMA or ready.get("status") != "READY":
        raise CorpusError("corpus READY has the wrong schema or status")
    specimen = ready.get("specimen")
    if not isinstance(specimen, dict):
        raise CorpusError("corpus READY has no specimen object")
    specimen_path = Path(str(specimen.get("path", "")))
    if not specimen_path.is_file():
        raise CorpusError("corpus specimen is missing")
    if specimen_path.stat().st_size != specimen.get("bytes") or sha256_file(specimen_path) != specimen.get("sha256"):
        raise CorpusError("corpus specimen no longer matches READY")
    if specimen.get("sha256") != EXPECTED_SPECIMEN_SHA256:
        raise CorpusError("corpus READY is not bound to the designated specimen")
    for group in ("inputs", "outputs"):
        entries = ready.get(group)
        if not isinstance(entries, dict):
            raise CorpusError(f"corpus READY has no {group} object")
        for name, value in entries.items():
            if group == "inputs" and name == "definedReadyIdentity":
                continue
            if not isinstance(value, dict) or not {"path", "bytes", "sha256"} <= set(value):
                raise CorpusError(f"invalid {group} artifact {name}")
            path = Path(str(value["path"]))
            if not path.is_file():
                raise CorpusError(f"missing {group} artifact {name}: {path}")
            if path.stat().st_size != value["bytes"] or sha256_file(path) != value["sha256"]:
                raise CorpusError(f"{group} artifact does not match READY: {name}")
    parse_pe(specimen_path.read_bytes())
    print(json.dumps({"status": "VERIFIED", "ready": str(ready_path), "counts": ready["counts"]}, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    extract_parser = commands.add_parser("extract", help="build the complete string corpus")
    extract_parser.add_argument("--specimen", type=Path, required=True)
    extract_parser.add_argument("--defined-tsv", type=Path, required=True)
    extract_parser.add_argument("--defined-ready", type=Path, required=True)
    extract_parser.add_argument("--out-dir", type=Path, required=True)
    extract_parser.add_argument("--markdown", type=Path, required=True)
    extract_parser.add_argument("--minimum", type=int, default=4)
    extract_parser.set_defaults(handler=extract)
    verify_parser = commands.add_parser("verify", help="rehash and validate a frozen corpus")
    verify_parser.add_argument("--ready", type=Path, required=True)
    verify_parser.set_defaults(handler=verify)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.handler(args)
    except (CorpusError, OSError, ValueError, json.JSONDecodeError) as exception:
        print(f"ERROR: {exception}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
