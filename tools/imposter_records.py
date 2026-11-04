#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Read imposter identities and view rectangles without guessing the remaining fields.

The caller supplies the payload of a top-level IMPS archive chunk. The nested
IMPS/IMPO/IMPT framing, IMSH resource id and CIMP label are the catalogue's
established CDXImposter::DeserializeAll reading. VIEW consists of six-float
rectangles as read by content_inventory.views_hold and the rebuild materializer.
The number of complete rectangles is not a claim about runtime view selection.

All offsets address the supplied payload. Unknown fields remain named spans;
neither their values nor original payload bytes are returned. This reader does
not read files, write output, decode atlas pixels or claim runtime use.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import struct


class ImposterFormatError(ValueError):
    """The supplied chunk stream cannot establish an unambiguous identity."""


@dataclass(frozen=True)
class Chunk:
    tag: str
    offset: int
    payload: int
    length: int

    @property
    def end(self) -> int:
        return self.payload + self.length


def chunks(data: bytes, start: int, end: int) -> list[Chunk]:
    """Read only length-delimited siblings, never search opaque payload bytes."""
    if not 0 <= start <= end <= len(data):
        raise ImposterFormatError("chunk range is outside its supplied stream")
    out = []
    position = start
    while position < end:
        if end - position < 8:
            raise ImposterFormatError("truncated chunk header")
        tag = data[position:position + 4]
        if len(tag) != 4 or any(c < 32 or c > 126 for c in tag):
            raise ImposterFormatError("chunk tag is not printable ASCII")
        length = struct.unpack_from("<I", data, position + 4)[0]
        body = position + 8
        if length > end - body:
            raise ImposterFormatError("chunk extends past its enclosing stream")
        out.append(Chunk(tag.decode("ascii"), position, body, length))
        position = body + length
    return out


def only(rows: list[Chunk], tag: str, *, required: bool = True) -> Chunk | None:
    found = [row for row in rows if row.tag == tag]
    if len(found) > 1:
        raise ImposterFormatError(f"duplicate {tag} chunk")
    if not found and required:
        raise ImposterFormatError(f"missing {tag} chunk")
    return found[0] if found else None


def span(row: Chunk, label: str) -> dict:
    return {"field": label, "offset": row.payload, "length": row.length}


def view_metadata(data: bytes, row: Chunk | None) -> dict:
    if row is None:
        return {"status": "unparsed", "countByLength": None, "views": [],
                "reason": "missing VIEW chunk"}
    if not row.length or row.length % 24:
        return {"status": "unparsed", "countByLength": None, "views": [],
                "reason": "VIEW is not a nonempty array of six-float rectangles"}
    count = row.length // 24
    out = []
    for index in range(count):
        left, right, top, bottom, width, height = struct.unpack_from("<6f", data, row.payload + index * 24)
        if not all(math.isfinite(v) for v in (left, right, top, bottom, width, height)):
            reason = "VIEW contains a non-finite value"
        elif not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
            reason = "VIEW atlas rectangle is empty, reversed or outside normalized bounds"
        elif width <= 0 or height <= 0:
            reason = "VIEW dimensions are not positive"
        else:
            out.append({"ordinal": index, "left": left, "right": right, "top": top, "bottom": bottom,
                        "width": width, "height": height})
            continue
        # Do not publish a valid-looking prefix of an invalid array.
        return {"status": "unparsed", "countByLength": count, "views": [], "reason": reason}
    return {"status": "parsed", "countByLength": count, "views": out, "reason": None}


def parse_imposter_set(data: bytes) -> dict:
    outer = chunks(data, 0, len(data))
    if len(outer) != 1 or outer[0].tag != "IMPS":
        raise ImposterFormatError("expected exactly one nested IMPS chunk")
    root = outer[0]
    children = chunks(data, root.payload, root.end)
    atlas = only(children, "BTXT", required=False)
    entries = only(children, "IMPO")
    assert entries is not None
    if entries.length < 4:
        raise ImposterFormatError("IMPO has no complete record count")
    count = struct.unpack_from("<I", data, entries.payload)[0]
    if count > (entries.length - 4) // 8:
        raise ImposterFormatError("IMPO count exceeds its available chunk headers")
    records = chunks(data, entries.payload + 4, entries.end)
    if len(records) != count or any(record.tag != "IMPT" for record in records):
        raise ImposterFormatError("IMPO count or record tags disagree with its framed records")
    out = []
    for ordinal, record in enumerate(records):
        fields = chunks(data, record.payload, record.end)
        mesh = only(fields, "IMSH")
        label = only(fields, "CIMP", required=False)
        views = only(fields, "VIEW", required=False)
        assert mesh is not None
        if mesh.length != 4:
            raise ImposterFormatError("IMSH is not one resource id")
        label_text = None
        label_status = "missing"
        unread = []
        if label is not None:
            if label.length < 68:
                label_status = "truncated"
                unread.append(span(label, "CIMP"))
            else:
                buffer = data[label.payload + 4:label.payload + 68]
                terminator = buffer.find(b"\0")
                if terminator < 0:
                    label_status = "unterminated"
                    unread.append({"field": "CIMP/label", "offset": label.payload + 4, "length": 64})
                else:
                    label_text = buffer[:terminator].decode("latin-1")
                    label_status = "empty" if not label_text else "terminated-latin1"
                unread.append({"field": "CIMP/prefix", "offset": label.payload, "length": 4})
                if label.length > 68:
                    unread.append({"field": "CIMP/tail", "offset": label.payload + 68, "length": label.length - 68})
        unread.extend(span(row, row.tag) for row in fields if row.tag not in {"CIMP", "IMSH", "VIEW"})
        metadata = view_metadata(data, views)
        if views is not None and metadata["status"] != "parsed":
            unread.append(span(views, "VIEW"))
        out.append({"ordinal": ordinal, "offset": record.offset, "length": record.end - record.offset,
                    "meshResourceId": struct.unpack_from("<i", data, mesh.payload)[0],
                    "storedLabel": label_text, "labelStatus": label_status, "viewMetadata": metadata,
                    "uninterpreted": unread})
    return {"records": out, "atlas": None if atlas is None else
            {"offset": atlas.payload, "length": atlas.length},
            "uninterpreted": [span(row, row.tag) for row in children if row.tag not in {"BTXT", "IMPO"}]}
