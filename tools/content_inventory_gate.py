#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The retail gate for tools/content_inventory.py: re-derive what only the real install can show, by a path that does
not run through the reader being checked, and fail on any disagreement.

tools/content_inventory_tests.py checks the rules on authored data. This reads a finished run's output and the game
folder it came from, and checks that:

  files      an independent walk of the folder finds exactly the run's files and sizes and no link or special file,
             and each file still has the hash the run recorded
  account    every file's parts and spans sum to its logical size and its classes agree with its bytes
  envelope   every AYA, inflated here member by member with zlib alone, has the logical size the run reports
  chunks     every archive's top-level chunks, walked here, close exactly and reach the end of the stream
  records    every catalogue record placed by offset in an archive's inflated stream hashes, at those coordinates, to
             the SHA-256 the catalogue gave it, and lies on bytes the account does not call unknown
  images     Pillow opens every PNG, JPEG and TGA at the size the walkers report (skipped, and said so, without Pillow)
  decoders   every Ogg and Bink was read by the independent decoder and agreed (a run without one fails here)
  animation  every mesh's cached model-space frames equal its keys composed down the hierarchy
  items      item ids are unique, and every item's file is one of the run's files
  sniffing   every file's own magic agrees with its family
  problems   no reader refused anything

The gate reads and writes nothing else. It prints counts; a failure names a file and what disagreed, never its bytes.
The exit code is 0 only when every check passes.

    python3 tools/content_inventory_gate.py --game GAME [--inventory local-data/content-inventory] [--no-compose]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import stat
import struct
import sys
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

import cmsh_animation_usage_census as meshcensus  # noqa: E402
import cmsh_grammar_walk as grammar  # noqa: E402
import content_inventory as inv  # noqa: E402

try:
    from PIL import Image
except ImportError:  # the check says so; it never passes silently
    Image = None

# The catalogue envelopes whose offset and length are coordinates in the archive's inflated stream. A world body's
# records are placed inside the body instead, so they are not checked this way.
STREAM_ENVELOPE_RE = re.compile(r"^lvlr-chunk\([A-Z0-9]{4}(?:/PMSH/PMS2)?\)$")
IMAGE_SUFFIXES = (".png", ".jpg", ".tga")


def walk_folder(game: Path) -> tuple[dict[str, int], list[str]]:
    """Every regular file below the folder and its size, and every other entry: a link (to a directory too, which
    os.walk lists among the directories and does not enter) or a special file, which no account can hold."""
    found, irregular = {}, []
    for folder, dirs, names in os.walk(game, followlinks=False):
        irregular += [(Path(folder) / name).relative_to(game).as_posix() for name in dirs
                      if (Path(folder) / name).is_symlink()]
        for name in names:
            path = Path(folder) / name
            info = path.lstat()
            if stat.S_ISREG(info.st_mode):
                found[path.relative_to(game).as_posix()] = info.st_size
            else:
                irregular.append(path.relative_to(game).as_posix())
    return found, sorted(irregular)


def inflate_members(data: bytes) -> bytes:
    """AYA's members, with nothing but zlib: u32 stored length, then a complete zlib stream."""
    out, position = [], 0
    while position < len(data):
        if position + 4 > len(data):
            raise ValueError("truncated member length")
        (length,) = struct.unpack_from("<I", data, position)
        position += 4
        inflater = zlib.decompressobj()
        out.append(inflater.decompress(data[position:position + length]))
        if not length or not inflater.eof or inflater.unused_data or position + length > len(data):
            raise ValueError("member does not close")
        position += length
    return b"".join(out)


def walk_chunks(raw: bytes) -> list[tuple[bytes, int, int]]:
    rows, position = [], 0
    while position < len(raw):
        if position + 8 > len(raw):
            raise ValueError("truncated chunk header")
        (size,) = struct.unpack_from("<I", raw, position + 4)
        if position + 8 + size > len(raw):
            raise ValueError("chunk runs past the stream")
        rows.append((raw[position:position + 4], position, size))
        position += 8 + size
    return rows


def spans_cover(spans: list, start: int, end: int) -> bool:
    return any(a < end and start < b for a, b in spans)


def check_files(game: Path, rows: list[dict], report: "Report") -> None:
    found, irregular = walk_folder(game)
    listed = {row["path"]: row["storedBytes"] for row in rows}
    report.count("files walked", len(found))
    for path in irregular:
        report.fail(f"{path}: a link or special file, which no account holds")
    for path in sorted(set(found) ^ set(listed)):
        report.fail(f"{path}: in {'the folder' if path in found else 'the run'} only")
    for path in sorted(set(found) & set(listed)):
        if found[path] != listed[path]:
            report.fail(f"{path}: the run's size differs from the folder's")
    for row in rows:
        path = game / row["path"]
        if path.is_file():
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                report.fail(f"{row['path']}: the file changed after the run")
            yield row, data


def check_account(row: dict, report: "Report") -> None:
    totals = row["bytes"]
    if sum(totals.values()) != row["logicalBytes"]:
        report.fail(f"{row['path']}: classes do not sum to the logical size")
    by_class: collections.Counter = collections.Counter()
    for part in row["parts"]:
        by_class[part["class"]] += part["bytes"]
    if any(by_class[klass] != totals[klass] for klass in inv.BYTE_CLASSES):
        report.fail(f"{row['path']}: parts do not sum to the classes")
    if sum(end - start for start, end, _part in row["unknownSpans"]) != totals[inv.UNKNOWN]:
        report.fail(f"{row['path']}: unknown spans do not sum to the unknown bytes")
    if sum(end - start for start, end in row["referencedSpans"]) != totals[inv.REFERENCED]:
        report.fail(f"{row['path']}: referenced spans do not sum to the referenced bytes")
    if row["class"] != inv.file_class(row["logicalBytes"], totals):
        report.fail(f"{row['path']}: its class disagrees with its bytes")
    report.count("accounts checked")


def stream_records(catalog_records: list[dict]) -> dict[str, list[dict]]:
    """The catalogue records placed in an archive's inflated stream, by folded container path."""
    out: dict[str, list[dict]] = collections.defaultdict(list)
    for record in catalog_records:
        source = record["source"]
        if STREAM_ENVELOPE_RE.match(source["envelope"]) and source["offset"] is not None and source["length"]:
            out[source["container"].casefold()].append(record)
    return out


def check_records(row: dict, raw: bytes, records: list[dict], report: "Report") -> None:
    unknown = [span[:2] for span in row["unknownSpans"]]
    for record in records:
        source = record["source"]
        start, end = source["offset"], source["offset"] + source["length"]
        if end > len(raw):
            report.fail(f"{record['id']}: its coordinates run past its stream")
        elif hashlib.sha256(raw[start:end]).hexdigest() != record["sha256"]:
            report.fail(f"{record['id']}: the bytes at its coordinates do not hash to its SHA-256")
        elif spans_cover(unknown, start, end):
            report.fail(f"{record['id']}: it lies on bytes the account calls unknown")
        else:
            report.count("records whose coordinates hash to their SHA-256")
            if spans_cover(row["referencedSpans"], start, end):
                report.count("records touching referenced bytes")


def check_image(row: dict, data: bytes, report: "Report") -> None:
    if Image is None:
        return
    import io
    try:
        with Image.open(io.BytesIO(data)) as image:
            size = image.size
            image.load()
    except Exception as error:  # Pillow raises many kinds; any of them is this file's failure
        report.fail(f"{row['path']}: Pillow refused it: {type(error).__name__}")
        return
    if size != (row["facts"].get("width"), row["facts"].get("height")):
        report.fail(f"{row['path']}: Pillow's size differs from the walker's")
    report.count("images Pillow read at the walker's size")


def check_compose(data: bytes, totals: collections.Counter, worst: list[float], report: "Report", path: str) -> None:
    try:
        meshes = grammar.walk_stream(data, collections.defaultdict(collections.Counter))
    except (grammar.GrammarError, struct.error) as error:
        report.fail(f"{path}: the grammar walk refused it: {error}")
        return
    grammar.check_caches(meshes, totals, worst)


class Report:
    def __init__(self):
        self.counts: collections.Counter = collections.Counter()
        self.failures: list[str] = []

    def count(self, what: str, by: int = 1) -> None:
        self.counts[what] += by

    def fail(self, line: str) -> None:
        self.failures.append(line)


def run(game: Path, inventory: Path, *, compose: bool = True) -> Report:
    report = Report()
    coverage = json.loads((inventory / "coverage.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in (inventory / "files.jsonl").read_text(encoding="utf-8").splitlines()]
    items = [json.loads(line) for line in (inventory / "items.jsonl").read_text(encoding="utf-8").splitlines()]
    if sum(row["storedBytes"] for row in rows) != coverage["installBytes"] or len(rows) != coverage["installFiles"]:
        report.fail("the run's files do not sum to its install")
    if Image is None:
        report.count("image checks skipped: Pillow is not installed")
    placed = stream_records([json.loads(line) for line in
                             (inventory / "records.jsonl").read_text(encoding="utf-8").splitlines()])
    totals: collections.Counter = collections.Counter()
    worst = [0.0, 0.0]
    for row, data in check_files(game, rows, report):
        check_account(row, report)
        if not inv.sniff_agrees(row["family"], inv.sniff(data)):
            report.fail(f"{row['path']}: its magic disagrees with its family {row['family']}")
        if row["problems"]:
            report.fail(f"{row['path']}: {len(row['problems'])} reader problems")
        if row["stream"] == "inflated":
            try:
                raw = inflate_members(data)
            except (ValueError, zlib.error) as error:
                report.fail(f"{row['path']}: the envelope does not inflate: {error}")
                continue
            if len(raw) != row["logicalBytes"]:
                report.fail(f"{row['path']}: inflated size differs from the run's")
            report.count("envelopes inflated independently")
            check_records(row, raw, placed.pop(row["path"].casefold(), []), report)
            if row["family"] == "lvlr-resource-archive":
                try:
                    report.count("archive chunks walked", len(walk_chunks(raw)))
                except ValueError as error:
                    report.fail(f"{row['path']}: {error}")
                if compose:
                    for chunk_tag, at, size in walk_chunks(raw):
                        if chunk_tag == b"MESH" and b"CMSH" in raw[at + 8:at + 8 + size]:
                            stream, _offset = meshcensus._direct_embedded_cmsh_with_offset(raw[at + 8:at + 8 + size])
                            check_compose(stream, totals, worst, report, row["path"])
            elif row["family"] == "cmsh-mesh" and compose:
                check_compose(raw, totals, worst, report, row["path"])
        if row["family"] in inv.MEDIA_FAMILIES:
            if row["facts"].get("decoder") != "agrees":
                report.fail(f"{row['path']}: the independent decoder did not agree ({row['facts'].get('decoder')})")
            else:
                report.count("media files the independent decoder agreed with")
        if row["path"].casefold().endswith(IMAGE_SUFFIXES):
            check_image(row, data, report)
    for container, left in sorted(placed.items()):
        report.fail(f"{container}: {len(left)} records placed in a stream the gate did not inflate")
    if compose:
        report.count("cached positions equal to composed keys", totals["position frames"])
        report.count("cached orientations equal to composed keys", totals["orientation frames"])
        for kind in ("position mismatches", "orientation mismatches"):
            if totals[kind]:
                report.fail(f"{totals[kind]} {kind}: a cached frame is not its composed keys")
    ids = collections.Counter(item["id"] for item in items)
    for name, count in ids.items():
        if count > 1:
            report.fail(f"item id {name} is used {count} times")
    paths = {row["path"] for row in rows}
    for item in items:
        if item["file"] not in paths:
            report.fail(f"{item['id']}: its file is not one of the run's")
    report.count("items checked", len(items))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--game", required=True, type=Path, help="the installed game folder the run read")
    parser.add_argument("--inventory", type=Path, default=ROOT / "local-data" / "content-inventory")
    parser.add_argument("--no-compose", action="store_true", help="skip the animation composition check")
    args = parser.parse_args(argv)
    report = run(args.game, args.inventory, compose=not args.no_compose)
    for key in sorted(report.counts):
        print(f"{key}: {report.counts[key]}")
    for line in report.failures[:60]:
        print("FAIL", line)
    if len(report.failures) > 60:
        print(f"... and {len(report.failures) - 60} more")
    print("content inventory gate: " + ("failed" if report.failures else "passed") + f" ({len(report.failures)} failures)")
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
