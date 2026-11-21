#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Read imposter identities, CDXImposter header fields, atlas size and view rectangles without guessing unknown bytes.

The caller supplies the payload of a top-level IMPS archive chunk. The nested
IMPS/DATA, IMPS/BTXT and IMPS/IMPO/IMPT framing, IMSH resource id and CIMP
CDXImposter layout (sizeof == 0x4C: mName[32] at +0x04, mUnknown30 at +0x30,
mAlt at +0x34, mUnknown38 at +0x38, mViews at +0x40, mNumFrames at +0x44,
mAnimated at +0x48) follow onslaught-decomp src/imposter.h and
src/DXImposter.cpp (CDXImposter::DeserializeAll @0x00543d90). VIEW consists of
six-float rectangles as read by content_inventory.views_hold and the rebuild
materializer, with expected count mViews * mNumFrames.

All offsets address the supplied payload. Serialized pointers (mNext, mMesh,
mFrames) and mUnknown28 remain named uninterpreted spans; neither their values
nor original payload bytes are returned. This reader does not read files, write
output, decode atlas pixels or claim runtime use.
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


CIMP_SIZE = 0x4C  # sizeof(CDXImposter) (onslaught-decomp src/imposter.h)
CIMP_NAME_OFFSET = 0x04
CIMP_NAME_SIZE = 0x20  # char mName[0x20]


def parse_imposter_set(data: bytes) -> dict:
    outer = chunks(data, 0, len(data))
    if len(outer) != 1 or outer[0].tag != "IMPS":
        raise ImposterFormatError("expected exactly one nested IMPS chunk")
    root = outer[0]
    children = chunks(data, root.payload, root.end)
    data_chunk = only(children, "DATA", required=False)
    atlas = only(children, "BTXT", required=False)
    entries = only(children, "IMPO")
    assert entries is not None
    atlas_size = None
    set_unread = []
    if data_chunk is not None:
        if data_chunk.length == 8:
            width, height = struct.unpack_from("<2i", data, data_chunk.payload)
            if width > 0 and height > 0:
                atlas_size = {"width": width, "height": height}
            else:
                set_unread.append(span(data_chunk, "DATA"))
        else:
            set_unread.append(span(data_chunk, "DATA"))
    set_unread.extend(span(row, row.tag) for row in children if row.tag not in {"DATA", "BTXT", "IMPO"})
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
        cimp_fields = None
        unread = []
        if label is not None:
            if label.length < CIMP_NAME_OFFSET + CIMP_NAME_SIZE:
                label_status = "truncated"
                unread.append(span(label, "CIMP"))
            else:
                buffer = data[label.payload + CIMP_NAME_OFFSET:label.payload + CIMP_NAME_OFFSET + CIMP_NAME_SIZE]
                terminator = buffer.find(b"\0")
                if terminator < 0:
                    label_status = "unterminated"
                    unread.append({"field": "CIMP/label", "offset": label.payload + CIMP_NAME_OFFSET,
                                   "length": CIMP_NAME_SIZE})
                else:
                    label_text = buffer[:terminator].decode("latin-1")
                    label_status = "empty" if not label_text else "terminated-latin1"
                unread.append({"field": "CIMP/mNext", "offset": label.payload, "length": 4})
                if label.length >= CIMP_SIZE:
                    unread.append({"field": "CIMP/mMesh", "offset": label.payload + 0x24, "length": 4})
                    unread.append({"field": "CIMP/mUnknown28", "offset": label.payload + 0x28, "length": 8})
                    unk30, alt, unk38 = struct.unpack_from("<3i", data, label.payload + 0x30)
                    unread.append({"field": "CIMP/mFrames", "offset": label.payload + 0x3C, "length": 4})
                    view_count, num_frames, animated = struct.unpack_from("<3i", data, label.payload + 0x40)
                    cimp_fields = {"unknown30": unk30, "alt": bool(alt), "unknown38": unk38,
                                   "views": view_count, "numFrames": num_frames, "animated": bool(animated)}
                    if label.length > CIMP_SIZE:
                        unread.append({"field": "CIMP/tail", "offset": label.payload + CIMP_SIZE,
                                       "length": label.length - CIMP_SIZE})
                else:
                    unread.append({"field": "CIMP/tail", "offset": label.payload + CIMP_NAME_OFFSET + CIMP_NAME_SIZE,
                                   "length": label.length - (CIMP_NAME_OFFSET + CIMP_NAME_SIZE)})
        unread.extend(span(row, row.tag) for row in fields if row.tag not in {"CIMP", "IMSH", "VIEW"})
        metadata = view_metadata(data, views)
        if views is not None and metadata["status"] != "parsed":
            unread.append(span(views, "VIEW"))
        view_count_matches = None
        if cimp_fields is not None and cimp_fields["views"] > 0 and cimp_fields["numFrames"] > 0:
            expected_views = cimp_fields["views"] * cimp_fields["numFrames"]
            if metadata["countByLength"] is not None:
                view_count_matches = metadata["countByLength"] == expected_views
        out.append({"ordinal": ordinal, "offset": record.offset, "length": record.end - record.offset,
                    "meshResourceId": struct.unpack_from("<i", data, mesh.payload)[0],
                    "storedLabel": label_text, "labelStatus": label_status, "cimpFields": cimp_fields,
                    "viewCountMatchesCimp": view_count_matches, "viewMetadata": metadata,
                    "uninterpreted": unread})
    return {"records": out, "atlasSize": atlas_size, "atlas": None if atlas is None else
            {"offset": atlas.payload, "length": atlas.length},
            "uninterpreted": set_unread}
