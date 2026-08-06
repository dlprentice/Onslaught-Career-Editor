"""Recover strict MSVC RTTI hierarchies and vtable slots from pristine BEA.exe.

The evidence chain is entirely specimen-byte based:

    TypeDescriptor -> RTTICompleteObjectLocator -> ClassHierarchyDescriptor
                   -> BaseClassArray / BaseClassDescriptor tree
    [vtable - 4] -> validated COL; vtable[0] -> executable .text

Merely finding a dword equal to a valid COL is not enough.  The retail image has
nine such values in unrelated .data/.rsrc payloads.  A strict vtable reference
must be followed by at least one .text function pointer.  Hierarchy structures
are also accepted only when their descriptor pointers and preorder subtree
sizes form one exact, closed tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import struct
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
READY_SCHEMA = "bea-rtti-strict-census-ready.v2"
CENSUS_SCHEMA = "bea-rtti-strict-census.v1"

# This tool accepts only the exact pristine specimen, so an unexpected census
# is a failed proof boundary rather than a reason to silently publish drift.
EXPECTED_PRISTINE_CENSUS = {
    "baseClassDescriptors": 674,
    "classHierarchyDescriptors": 656,
    "classesWithVtable": 656,
    "colPointerReferences": 733,
    "completeObjectLocators": 724,
    "directDerivedBaseEdges": 616,
    "distinctFunctionTargets": 2127,
    "hierarchyRows": 1930,
    "rejectedColPointerReferences": 9,
    "strictVtables": 724,
    "typeDescriptors": 667,
    "vtableSlots": 11777,
}

EXPECTED_REJECTED_REFS = {
    (0x00642F04, 0x00610050),
    (0x00647CBC, 0x00610050),
    (0x00648BA8, 0x00610050),
    (0x0065A41C, 0x00610000),
    (0x0065C360, 0x00610000),
    (0x009D68A4, 0x00610050),
    (0x009D6AD4, 0x00610050),
    (0x009D6B64, 0x00610050),
    (0x009D6D88, 0x00610050),
}


@dataclass(frozen=True)
class ProofPolicy:
    specimen_sha256: str
    specimen_bytes: int
    expected_counts: dict[str, int]
    expected_rejected_refs: frozenset[tuple[int, int]]
    required_edges: frozenset[tuple[str, str]] = frozenset()
    forbidden_edges: frozenset[tuple[str, str]] = frozenset()


PRISTINE_POLICY = ProofPolicy(
    specimen_sha256=PRISTINE_SHA256,
    specimen_bytes=2506752,
    expected_counts=EXPECTED_PRISTINE_CENSUS,
    expected_rejected_refs=frozenset(EXPECTED_REJECTED_REFS),
    required_edges=frozenset({("CActor", "CComplexThing")}),
    forbidden_edges=frozenset({("CActor", "IRenderableThing")}),
)


class EvidenceError(ValueError):
    """A candidate or receipt violates a byte-level evidence invariant."""


@dataclass(frozen=True)
class Section:
    name: str
    va: int
    virtual_size: int
    raw_offset: int
    raw_size: int
    characteristics: int


class PEImage:
    def __init__(self, data: bytes):
        self.data = data
        if len(data) < 0x40 or data[:2] != b"MZ":
            raise EvidenceError("not a DOS/PE image")
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if pe + 24 > len(data) or data[pe:pe + 4] != b"PE\0\0":
            raise EvidenceError("missing PE signature")
        number_of_sections = struct.unpack_from("<H", data, pe + 6)[0]
        optional_size = struct.unpack_from("<H", data, pe + 20)[0]
        optional = pe + 24
        if optional + optional_size > len(data):
            raise EvidenceError("truncated PE optional header")
        if struct.unpack_from("<H", data, optional)[0] != 0x10B:
            raise EvidenceError("only PE32 RTTI is supported")
        self.image_base = struct.unpack_from("<I", data, optional + 28)[0]
        section_table = optional + optional_size
        if section_table + number_of_sections * 40 > len(data):
            raise EvidenceError("truncated PE section table")
        sections: list[Section] = []
        for index in range(number_of_sections):
            raw = data[section_table + index * 40:section_table + (index + 1) * 40]
            name = raw[:8].rstrip(b"\0").decode("ascii", errors="strict")
            virtual_size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", raw, 8)
            characteristics = struct.unpack_from("<I", raw, 36)[0]
            if raw_offset + raw_size > len(data):
                raise EvidenceError(f"section {name} extends past the file")
            sections.append(Section(
                name=name,
                va=self.image_base + rva,
                virtual_size=virtual_size,
                raw_offset=raw_offset,
                raw_size=raw_size,
                characteristics=characteristics,
            ))
        self.sections = tuple(sections)
        matches = [section for section in self.sections if section.name == ".text"]
        if len(matches) != 1:
            raise EvidenceError("expected exactly one .text section")
        self.text = matches[0]
        self.text_start = self.text.va
        self.text_end = self.text.va + self.text.virtual_size

    def file_to_va(self, file_offset: int) -> int | None:
        for section in self.sections:
            if section.raw_offset <= file_offset < section.raw_offset + section.raw_size:
                return section.va + file_offset - section.raw_offset
        return None

    def va_to_file(self, va: int, size: int = 1) -> int | None:
        if size < 0:
            return None
        for section in self.sections:
            delta = va - section.va
            if 0 <= delta and delta + size <= section.raw_size:
                file_offset = section.raw_offset + delta
                if file_offset + size <= len(self.data):
                    return file_offset
        return None

    def section_for_va(self, va: int) -> Section | None:
        for section in self.sections:
            if section.va <= va < section.va + max(section.virtual_size, section.raw_size):
                return section
        return None

    def u32(self, va: int) -> int:
        file_offset = self.va_to_file(va, 4)
        if file_offset is None:
            raise EvidenceError(f"unmapped dword at 0x{va:08x}")
        return struct.unpack_from("<I", self.data, file_offset)[0]

    def i32(self, va: int) -> int:
        file_offset = self.va_to_file(va, 4)
        if file_offset is None:
            raise EvidenceError(f"unmapped dword at 0x{va:08x}")
        return struct.unpack_from("<i", self.data, file_offset)[0]

    def aligned_dwords(self) -> Iterable[tuple[int, int, Section]]:
        for section in self.sections:
            blob = self.data[section.raw_offset:section.raw_offset + section.raw_size]
            for offset in range(0, len(blob) - 3, 4):
                yield section.va + offset, struct.unpack_from("<I", blob, offset)[0], section


@dataclass(frozen=True)
class TypeDescriptor:
    va: int
    name: str


@dataclass(frozen=True)
class BaseClassDescriptor:
    va: int
    type_descriptor_va: int
    class_name: str
    num_contained_bases: int
    mdisp: int
    pdisp: int
    vdisp: int
    attributes: int


@dataclass(frozen=True)
class HierarchyRow:
    index: int
    descriptor: BaseClassDescriptor
    parent_index: int | None


@dataclass(frozen=True)
class ClassHierarchy:
    va: int
    root_type_descriptor_va: int
    root_class: str
    attributes: int
    base_array_va: int
    rows: tuple[HierarchyRow, ...]


@dataclass(frozen=True)
class CompleteObjectLocator:
    va: int
    offset: int
    cd_offset: int
    type_descriptor_va: int
    class_name: str
    hierarchy_va: int


@dataclass(frozen=True)
class Vtable:
    va: int
    col_va: int
    class_name: str


@dataclass(frozen=True)
class VtableSlot:
    class_name: str
    vtable_va: int
    slot: int
    function_va: int


@dataclass(frozen=True)
class RejectedReference:
    reference_va: int
    col_va: int
    class_name: str
    following_value: int | None
    section_name: str
    reason: str


@dataclass(frozen=True)
class RejectedColCandidate:
    va: int
    class_name: str
    hierarchy_va: int
    reason: str


@dataclass(frozen=True)
class RttiCensus:
    specimen_sha256: str
    type_descriptors: dict[int, TypeDescriptor]
    hierarchies: dict[int, ClassHierarchy]
    base_class_descriptors: dict[int, BaseClassDescriptor]
    cols: dict[int, CompleteObjectLocator]
    vtables: dict[int, Vtable]
    slots: tuple[VtableSlot, ...]
    rejected_references: tuple[RejectedReference, ...]
    rejected_col_candidates: tuple[RejectedColCandidate, ...]
    direct_edges: dict[tuple[str, str], tuple[int, ...]]

    def counts(self) -> dict[str, int]:
        return {
            "baseClassDescriptors": len(self.base_class_descriptors),
            "classHierarchyDescriptors": len(self.hierarchies),
            "classesWithVtable": len({v.class_name for v in self.vtables.values()}),
            "colPointerReferences": len(self.vtables) + len(self.rejected_references),
            "completeObjectLocators": len(self.cols),
            "directDerivedBaseEdges": len(self.direct_edges),
            "distinctFunctionTargets": len({slot.function_va for slot in self.slots}),
            "hierarchyRows": sum(len(hierarchy.rows) for hierarchy in self.hierarchies.values()),
            "rejectedColPointerReferences": len(self.rejected_references),
            "strictVtables": len(self.vtables),
            "typeDescriptors": len(self.type_descriptors),
            "vtableSlots": len(self.slots),
        }


def _parse_type_descriptors(image: PEImage) -> dict[int, TypeDescriptor]:
    result: dict[int, TypeDescriptor] = {}
    pattern = rb"\.\?A[VU]([A-Za-z0-9_@?$]+)@@"
    for match in re.finditer(pattern, image.data):
        if match.end() >= len(image.data) or image.data[match.end()] != 0:
            continue
        name_va = image.file_to_va(match.start())
        if name_va is None or image.va_to_file(name_va - 8, 8) is None:
            continue
        descriptor_va = name_va - 8
        if descriptor_va % 4:
            continue
        result[descriptor_va] = TypeDescriptor(
            va=descriptor_va,
            name=match.group(1).decode("ascii", errors="strict"),
        )
    return result


def _parse_base_descriptor(
    image: PEImage,
    va: int,
    type_descriptors: dict[int, TypeDescriptor],
    hierarchy_size: int,
) -> BaseClassDescriptor:
    if va % 4 or image.va_to_file(va, 24) is None:
        raise EvidenceError(f"invalid base-class descriptor pointer 0x{va:08x}")
    type_descriptor_va = image.u32(va)
    if type_descriptor_va not in type_descriptors:
        raise EvidenceError(f"base-class descriptor 0x{va:08x} has unknown type")
    num_contained = image.u32(va + 4)
    if num_contained >= hierarchy_size:
        raise EvidenceError(f"base-class descriptor 0x{va:08x} subtree overflows hierarchy")
    attributes = image.u32(va + 20)
    if attributes & ~0x3F:
        raise EvidenceError(f"base-class descriptor 0x{va:08x} has unknown attributes")
    return BaseClassDescriptor(
        va=va,
        type_descriptor_va=type_descriptor_va,
        class_name=type_descriptors[type_descriptor_va].name,
        num_contained_bases=num_contained,
        mdisp=image.i32(va + 8),
        pdisp=image.i32(va + 12),
        vdisp=image.i32(va + 16),
        attributes=attributes,
    )


def _parse_hierarchy(
    image: PEImage,
    va: int,
    expected_root_type: int,
    type_descriptors: dict[int, TypeDescriptor],
) -> ClassHierarchy:
    if va % 4 or image.va_to_file(va, 16) is None:
        raise EvidenceError(f"invalid class-hierarchy pointer 0x{va:08x}")
    signature = image.u32(va)
    attributes = image.u32(va + 4)
    row_count = image.u32(va + 8)
    base_array_va = image.u32(va + 12)
    if signature != 0:
        raise EvidenceError(f"class hierarchy 0x{va:08x} has nonzero signature")
    if attributes & ~0x7:
        raise EvidenceError(f"class hierarchy 0x{va:08x} has unknown attributes")
    if not 1 <= row_count <= 4096:
        raise EvidenceError(f"class hierarchy 0x{va:08x} has invalid row count")
    if base_array_va % 4 or image.va_to_file(base_array_va, row_count * 4) is None:
        raise EvidenceError(f"class hierarchy 0x{va:08x} has invalid base array")

    descriptors = tuple(
        _parse_base_descriptor(
            image,
            image.u32(base_array_va + index * 4),
            type_descriptors,
            row_count,
        )
        for index in range(row_count)
    )
    if descriptors[0].type_descriptor_va != expected_root_type:
        raise EvidenceError(f"class hierarchy 0x{va:08x} root type disagrees with COL")
    if descriptors[0].num_contained_bases != row_count - 1:
        raise EvidenceError(f"class hierarchy 0x{va:08x} root subtree is not exact")

    parents: list[int | None] = [None] * row_count

    def consume(index: int, limit: int) -> int:
        end = index + descriptors[index].num_contained_bases + 1
        if end > limit:
            raise EvidenceError(f"class hierarchy 0x{va:08x} subtree crosses its parent")
        child = index + 1
        while child < end:
            parents[child] = index
            child = consume(child, end)
        if child != end:
            raise EvidenceError(f"class hierarchy 0x{va:08x} subtree does not close")
        return end

    if consume(0, row_count) != row_count:
        raise EvidenceError(f"class hierarchy 0x{va:08x} has trailing rows")
    rows = tuple(
        HierarchyRow(index=index, descriptor=descriptor, parent_index=parents[index])
        for index, descriptor in enumerate(descriptors)
    )
    return ClassHierarchy(
        va=va,
        root_type_descriptor_va=expected_root_type,
        root_class=type_descriptors[expected_root_type].name,
        attributes=attributes,
        base_array_va=base_array_va,
        rows=rows,
    )


def parse_rtti(data: bytes) -> RttiCensus:
    image = PEImage(data)
    type_descriptors = _parse_type_descriptors(image)
    hierarchies: dict[int, ClassHierarchy] = {}
    base_descriptors: dict[int, BaseClassDescriptor] = {}
    cols: dict[int, CompleteObjectLocator] = {}
    rejected_cols: list[RejectedColCandidate] = []
    hierarchy_cache: dict[tuple[int, int], ClassHierarchy | EvidenceError] = {}

    for candidate_va, signature, _section in image.aligned_dwords():
        if signature != 0 or image.va_to_file(candidate_va, 20) is None:
            continue
        type_descriptor_va = image.u32(candidate_va + 12)
        if type_descriptor_va not in type_descriptors:
            continue
        hierarchy_va = image.u32(candidate_va + 16)
        cache_key = (hierarchy_va, type_descriptor_va)
        parsed = hierarchy_cache.get(cache_key)
        if parsed is None:
            try:
                parsed = _parse_hierarchy(image, hierarchy_va, type_descriptor_va, type_descriptors)
            except EvidenceError as exc:
                parsed = exc
            hierarchy_cache[cache_key] = parsed
        if isinstance(parsed, EvidenceError):
            rejected_cols.append(RejectedColCandidate(
                va=candidate_va,
                class_name=type_descriptors[type_descriptor_va].name,
                hierarchy_va=hierarchy_va,
                reason=str(parsed),
            ))
            continue
        prior = hierarchies.get(hierarchy_va)
        if prior is not None and prior != parsed:
            raise EvidenceError(f"class hierarchy 0x{hierarchy_va:08x} has conflicting parses")
        hierarchies[hierarchy_va] = parsed
        for row in parsed.rows:
            old = base_descriptors.get(row.descriptor.va)
            if old is not None and old != row.descriptor:
                raise EvidenceError(f"base descriptor 0x{row.descriptor.va:08x} is inconsistent")
            base_descriptors[row.descriptor.va] = row.descriptor
        cols[candidate_va] = CompleteObjectLocator(
            va=candidate_va,
            offset=image.u32(candidate_va + 4),
            cd_offset=image.u32(candidate_va + 8),
            type_descriptor_va=type_descriptor_va,
            class_name=type_descriptors[type_descriptor_va].name,
            hierarchy_va=hierarchy_va,
        )

    vtables: dict[int, Vtable] = {}
    rejected_refs: list[RejectedReference] = []
    for reference_va, value, section in image.aligned_dwords():
        col = cols.get(value)
        if col is None:
            continue
        following_va = reference_va + 4
        try:
            following = image.u32(following_va)
        except EvidenceError:
            following = None
        if following is None or not image.text_start <= following < image.text_end:
            rejected_refs.append(RejectedReference(
                reference_va=reference_va,
                col_va=col.va,
                class_name=col.class_name,
                following_value=following,
                section_name=section.name,
                reason="FIRST_SLOT_NOT_TEXT",
            ))
            continue
        vtables[following_va] = Vtable(
            va=following_va,
            col_va=col.va,
            class_name=col.class_name,
        )

    slots: list[VtableSlot] = []
    for vtable_va, vtable in sorted(vtables.items()):
        slot = 0
        while slot <= 4096:
            slot_va = vtable_va + slot * 4
            try:
                function_va = image.u32(slot_va)
            except EvidenceError:
                break
            if not image.text_start <= function_va < image.text_end:
                break
            slots.append(VtableSlot(
                class_name=vtable.class_name,
                vtable_va=vtable_va,
                slot=slot,
                function_va=function_va,
            ))
            slot += 1
        if slot == 0:
            raise EvidenceError(f"strict vtable 0x{vtable_va:08x} has no slots")
        if slot > 4096:
            raise EvidenceError(f"vtable 0x{vtable_va:08x} exceeds slot safety bound")

    edge_evidence: dict[tuple[str, str], set[int]] = defaultdict(set)
    for hierarchy in hierarchies.values():
        for row in hierarchy.rows:
            if row.parent_index is None:
                continue
            parent = hierarchy.rows[row.parent_index].descriptor.class_name
            edge_evidence[(parent, row.descriptor.class_name)].add(hierarchy.va)

    return RttiCensus(
        specimen_sha256=hashlib.sha256(data).hexdigest(),
        type_descriptors=type_descriptors,
        hierarchies=hierarchies,
        base_class_descriptors=base_descriptors,
        cols=cols,
        vtables=vtables,
        slots=tuple(slots),
        rejected_references=tuple(sorted(rejected_refs, key=lambda item: item.reference_va)),
        rejected_col_candidates=tuple(sorted(rejected_cols, key=lambda item: item.va)),
        direct_edges={key: tuple(sorted(values)) for key, values in sorted(edge_evidence.items())},
    )


def validate_census(census: RttiCensus, policy: ProofPolicy) -> None:
    if census.specimen_sha256 != policy.specimen_sha256:
        raise EvidenceError("not the pristine specimen")
    counts = census.counts()
    if counts != policy.expected_counts:
        raise EvidenceError(
            "pristine RTTI census drift: "
            + json.dumps({"expected": policy.expected_counts, "observed": counts}, sort_keys=True)
        )
    rejected = {(row.reference_va, row.col_va) for row in census.rejected_references}
    if rejected != policy.expected_rejected_refs:
        raise EvidenceError("rejected COL-reference set does not match the reproduced specimen set")
    if census.rejected_col_candidates:
        raise EvidenceError("pristine specimen contains structurally rejected COL candidates")
    missing = policy.required_edges - census.direct_edges.keys()
    if missing:
        raise EvidenceError(f"missing required direct hierarchy edges: {sorted(missing)}")
    forbidden = policy.forbidden_edges & census.direct_edges.keys()
    if forbidden:
        raise EvidenceError(f"transitive hierarchy edges were misclassified as direct: {sorted(forbidden)}")


def validate_pristine_census(census: RttiCensus) -> None:
    validate_census(census, PRISTINE_POLICY)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _tsv_text(header: list[str], rows: Iterable[Iterable[object]]) -> str:
    lines = ["\t".join(header)]
    for row in rows:
        lines.append("\t".join(str(value) for value in row))
    return "\n".join(lines) + "\n"


def vtables_tsv(census: RttiCensus) -> str:
    return _tsv_text(
        ["class", "vtable_va", "slot", "function_va"],
        (
            (row.class_name, f"0x{row.vtable_va:08x}", row.slot, f"0x{row.function_va:08x}")
            for row in census.slots
        ),
    )


def hierarchies_tsv(census: RttiCensus) -> str:
    rows = []
    for hierarchy in sorted(census.hierarchies.values(), key=lambda value: value.va):
        for row in hierarchy.rows:
            parent_name = ""
            if row.parent_index is not None:
                parent_name = hierarchy.rows[row.parent_index].descriptor.class_name
            descriptor = row.descriptor
            rows.append((
                f"0x{hierarchy.va:08x}",
                hierarchy.root_class,
                row.index,
                f"0x{descriptor.va:08x}",
                descriptor.class_name,
                descriptor.num_contained_bases,
                descriptor.mdisp,
                descriptor.pdisp,
                descriptor.vdisp,
                f"0x{descriptor.attributes:x}",
                "" if row.parent_index is None else row.parent_index,
                parent_name,
            ))
    return _tsv_text(
        [
            "chd_va", "root_class", "row_index", "bcd_va", "class", "num_contained_bases",
            "mdisp", "pdisp", "vdisp", "attributes", "parent_index", "parent_class",
        ],
        rows,
    )


def direct_edges_tsv(census: RttiCensus) -> str:
    return _tsv_text(
        ["derived_class", "direct_base_class", "evidence_chd_count", "example_chd_va"],
        (
            (derived, base, len(chds), f"0x{chds[0]:08x}")
            for (derived, base), chds in sorted(census.direct_edges.items())
        ),
    )


def rejected_references_tsv(census: RttiCensus) -> str:
    return _tsv_text(
        ["reference_va", "col_va", "class", "following_value", "section", "reason"],
        (
            (
                f"0x{row.reference_va:08x}",
                f"0x{row.col_va:08x}",
                row.class_name,
                "" if row.following_value is None else f"0x{row.following_value:08x}",
                row.section_name,
                row.reason,
            )
            for row in census.rejected_references
        ),
    )


def census_json(census: RttiCensus) -> str:
    payload = {
        "schema": CENSUS_SCHEMA,
        "specimenSha256": census.specimen_sha256,
        "counts": census.counts(),
        "rejectedColReferences": [
            {
                "referenceVa": f"0x{row.reference_va:08x}",
                "colVa": f"0x{row.col_va:08x}",
                "class": row.class_name,
                "followingValue": None if row.following_value is None else f"0x{row.following_value:08x}",
                "section": row.section_name,
                "reason": row.reason,
            }
            for row in census.rejected_references
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


OWNER_ARTIFACT = "owner/re_rtti_vtables.py"
EVIDENCE_ARTIFACTS = (
    "census.json",
    "direct-edges.tsv",
    "hierarchies.tsv",
    "rejected-col-references.tsv",
    "vtables.tsv",
)
EXPECTED_BUNDLE_FILES = frozenset({"READY.json", OWNER_ARTIFACT, *EVIDENCE_ARTIFACTS})
EXPECTED_BUNDLE_DIRS = frozenset({"owner"})


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _is_reparse(info: os.stat_result) -> bool:
    attributes = getattr(info, "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _canonical_plain_path(path: Path, *, directory: bool) -> Path:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    try:
        for part in absolute.parts[1:]:
            current /= part
            info = os.lstat(current)
            if stat.S_ISLNK(info.st_mode) or _is_reparse(info):
                raise EvidenceError(f"path contains a symlink/reparse point: {current}")
        final = os.lstat(absolute)
    except OSError as exc:
        raise EvidenceError(f"path is not an existing plain object: {absolute}: {exc}") from exc
    expected_mode = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected_mode(final.st_mode):
        kind = "directory" if directory else "file"
        raise EvidenceError(f"path is not a plain {kind}: {absolute}")
    resolved = absolute.resolve(strict=True)
    if resolved != absolute:
        raise EvidenceError(f"path is not canonical: {absolute}")
    return resolved


def _canonical_plain_file(path: Path) -> Path:
    return _canonical_plain_path(path, directory=False)


def _canonical_plain_directory(path: Path) -> Path:
    return _canonical_plain_path(path, directory=True)


def _expected_artifact_bytes(census: RttiCensus, owner_bytes: bytes) -> dict[str, bytes]:
    return {
        "census.json": census_json(census).encode("utf-8"),
        "direct-edges.tsv": direct_edges_tsv(census).encode("utf-8"),
        "hierarchies.tsv": hierarchies_tsv(census).encode("utf-8"),
        OWNER_ARTIFACT: owner_bytes,
        "rejected-col-references.tsv": rejected_references_tsv(census).encode("utf-8"),
        "vtables.tsv": vtables_tsv(census).encode("utf-8"),
    }


def _artifact_rows(census: RttiCensus) -> dict[str, int | None]:
    return {
        "census.json": None,
        "direct-edges.tsv": len(census.direct_edges),
        "hierarchies.tsv": census.counts()["hierarchyRows"],
        OWNER_ARTIFACT: None,
        "rejected-col-references.tsv": len(census.rejected_references),
        "vtables.tsv": len(census.slots),
    }


def _ready_payload(
    specimen_path: Path,
    census: RttiCensus,
    artifact_bytes: dict[str, bytes],
    policy: ProofPolicy,
) -> dict[str, object]:
    rows = _artifact_rows(census)
    artifacts = {
        name: {
            "bytes": len(content),
            "dataRows": rows[name],
            "sha256": _sha256_bytes(content),
        }
        for name, content in sorted(artifact_bytes.items())
    }
    return {
        "artifacts": artifacts,
        "counts": census.counts(),
        "producer": {
            "path": OWNER_ARTIFACT,
            "sha256": _sha256_bytes(artifact_bytes[OWNER_ARTIFACT]),
        },
        "schema": READY_SCHEMA,
        "specimen": {
            "bytes": policy.specimen_bytes,
            "path": str(specimen_path),
            "sha256": policy.specimen_sha256,
        },
        "status": "READY",
    }


def _assert_exact_bundle_tree(directory: Path) -> Path:
    root = _canonical_plain_directory(directory)
    files: set[str] = set()
    directories: set[str] = set()

    def walk(path: Path) -> None:
        with os.scandir(path) as entries:
            for entry in entries:
                info = entry.stat(follow_symlinks=False)
                relative = (path / entry.name).relative_to(root).as_posix()
                if entry.is_symlink() or stat.S_ISLNK(info.st_mode) or _is_reparse(info):
                    raise EvidenceError(f"bundle contains a symlink/reparse point: {relative}")
                if stat.S_ISDIR(info.st_mode):
                    directories.add(relative)
                    walk(path / entry.name)
                elif stat.S_ISREG(info.st_mode):
                    files.add(relative)
                else:
                    raise EvidenceError(f"bundle contains a non-plain entry: {relative}")

    walk(root)
    if files != EXPECTED_BUNDLE_FILES or directories != EXPECTED_BUNDLE_DIRS:
        raise EvidenceError(
            "bundle tree mismatch: "
            + json.dumps({
                "expectedFiles": sorted(EXPECTED_BUNDLE_FILES),
                "observedFiles": sorted(files),
                "expectedDirs": sorted(EXPECTED_BUNDLE_DIRS),
                "observedDirs": sorted(directories),
            }, sort_keys=True)
        )
    return root


def _write_new_file(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)


def _clean_stage(stage: Path, parent: Path, prefix: str) -> None:
    if not stage.exists():
        return
    if stage.parent != parent or not stage.name.startswith(prefix):
        raise EvidenceError(f"refusing to clean unexpected staging path: {stage}")
    shutil.rmtree(stage)


def write_ready_bundle(
    directory: Path,
    specimen_path: Path,
    policy: ProofPolicy = PRISTINE_POLICY,
) -> Path:
    target = Path(os.path.abspath(directory))
    if target.exists() or target.is_symlink():
        raise EvidenceError(f"READY output already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    parent = _canonical_plain_directory(target.parent)
    specimen = _canonical_plain_file(specimen_path)
    specimen_bytes = specimen.read_bytes()
    if len(specimen_bytes) != policy.specimen_bytes or _sha256_bytes(specimen_bytes) != policy.specimen_sha256:
        raise EvidenceError("bound specimen bytes/hash mismatch")
    census = parse_rtti(specimen_bytes)
    validate_census(census, policy)
    owner_path = _canonical_plain_file(Path(__file__))
    owner_bytes = owner_path.read_bytes()
    artifacts = _expected_artifact_bytes(census, owner_bytes)
    stage_prefix = f".{target.name}.stage-"
    stage = Path(tempfile.mkdtemp(prefix=stage_prefix, dir=parent))
    try:
        for name, content in artifacts.items():
            _write_new_file(stage / Path(name), content)
        ready = _ready_payload(specimen, census, artifacts, policy)
        _write_new_file(stage / "READY.json", _canonical_json_bytes(ready))
        verify_ready_bundle(stage, specimen, policy)
        if target.exists() or target.is_symlink():
            raise EvidenceError(f"READY target appeared during publication: {target}")
        os.rename(stage, target)
    except BaseException:
        _clean_stage(stage, parent, stage_prefix)
        raise
    return target / "READY.json"


def verify_ready_bundle(
    directory: Path,
    specimen_path: Path,
    policy: ProofPolicy = PRISTINE_POLICY,
) -> dict[str, object]:
    root = _assert_exact_bundle_tree(directory)
    expected_specimen = _canonical_plain_file(specimen_path)
    ready_bytes = (root / "READY.json").read_bytes()
    try:
        ready = json.loads(ready_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"cannot decode READY receipt: {exc}") from exc
    if not isinstance(ready, dict) or set(ready) != {
        "artifacts", "counts", "producer", "schema", "specimen", "status",
    }:
        raise EvidenceError("READY top-level schema mismatch")
    if ready.get("schema") != READY_SCHEMA or ready.get("status") != "READY":
        raise EvidenceError("invalid READY schema or status")
    specimen_receipt = ready.get("specimen")
    if not isinstance(specimen_receipt, dict) or set(specimen_receipt) != {"bytes", "path", "sha256"}:
        raise EvidenceError("READY specimen schema mismatch")
    recorded_path = specimen_receipt.get("path")
    if not isinstance(recorded_path, str) or not Path(recorded_path).is_absolute():
        raise EvidenceError("READY specimen path is not exact/absolute")
    specimen = _canonical_plain_file(Path(recorded_path))
    if str(specimen) != recorded_path:
        raise EvidenceError("READY specimen path is not canonical")
    if specimen != expected_specimen:
        raise EvidenceError("READY specimen path differs from the verifier-bound path")
    specimen_bytes = specimen.read_bytes()
    specimen_identity = {
        "bytes": len(specimen_bytes),
        "path": str(specimen),
        "sha256": _sha256_bytes(specimen_bytes),
    }
    expected_identity = {
        "bytes": policy.specimen_bytes,
        "path": str(specimen),
        "sha256": policy.specimen_sha256,
    }
    if specimen_receipt != specimen_identity or specimen_identity != expected_identity:
        raise EvidenceError("READY specimen path/bytes/hash mismatch")

    running_owner = _canonical_plain_file(Path(__file__)).read_bytes()
    frozen_owner = (root / OWNER_ARTIFACT).read_bytes()
    if frozen_owner != running_owner:
        raise EvidenceError("running verifier differs from frozen owner")
    census = parse_rtti(specimen_bytes)
    validate_census(census, policy)
    expected_artifacts = _expected_artifact_bytes(census, running_owner)
    artifact_receipts = ready.get("artifacts")
    if not isinstance(artifact_receipts, dict) or set(artifact_receipts) != set(expected_artifacts):
        raise EvidenceError("READY artifact schema mismatch")
    expected_rows = _artifact_rows(census)
    for name, expected_content in expected_artifacts.items():
        actual_content = (root / Path(name)).read_bytes()
        if actual_content != expected_content:
            raise EvidenceError(f"artifact does not byte-replay from the bound specimen: {name}")
        expected_receipt = {
            "bytes": len(expected_content),
            "dataRows": expected_rows[name],
            "sha256": _sha256_bytes(expected_content),
        }
        if artifact_receipts[name] != expected_receipt:
            raise EvidenceError(f"artifact receipt mismatch: {name}")
    expected_ready = _ready_payload(specimen, census, expected_artifacts, policy)
    if ready != expected_ready or ready_bytes != _canonical_json_bytes(expected_ready):
        raise EvidenceError("READY receipt is not the exact canonical replay receipt")
    return ready


def _print_counts(counts: dict[str, int]) -> None:
    labels = [
        ("type descriptors", "typeDescriptors"),
        ("complete object locators", "completeObjectLocators"),
        ("class hierarchy descriptors", "classHierarchyDescriptors"),
        ("base class descriptors", "baseClassDescriptors"),
        ("hierarchy rows", "hierarchyRows"),
        ("direct derived/base edges", "directDerivedBaseEdges"),
        ("COL pointer references", "colPointerReferences"),
        ("strict vtables", "strictVtables"),
        ("rejected COL references", "rejectedColPointerReferences"),
        ("vtable slots resolved", "vtableSlots"),
        ("distinct function targets", "distinctFunctionTargets"),
        ("classes with a vtable", "classesWithVtable"),
    ]
    for label, key in labels:
        print(f"{label:<29}: {counts[key]}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--verify-ready", type=Path)
    parser.add_argument("--out-tsv", type=Path, help="strict vtable-slot mapping")
    parser.add_argument("--out-hierarchy-tsv", type=Path)
    parser.add_argument("--out-edges-tsv", type=Path)
    parser.add_argument("--out-rejected-tsv", type=Path)
    parser.add_argument("--out-summary-json", type=Path)
    parser.add_argument("--ready-dir", type=Path)
    parser.add_argument("--inventory", type=Path, help="functions-all.tsv, to report overlap")
    args = parser.parse_args(argv)

    try:
        if args.verify_ready:
            verify_ready_bundle(args.verify_ready, args.binary)
            print(f"READY VERIFIED: {args.verify_ready}")
            return 0
        assert args.binary is not None
        data = args.binary.read_bytes()
        census = parse_rtti(data)
        validate_pristine_census(census)
        _print_counts(census.counts())

        if args.inventory:
            inventory = {}
            with args.inventory.open(encoding="utf-8") as handle:
                next(handle, None)
                for line in handle:
                    fields = line.rstrip("\n").split("\t")
                    if len(fields) >= 2 and fields[0].startswith("0x"):
                        inventory[int(fields[0], 16)] = fields[1]
            distinct_functions = {slot.function_va for slot in census.slots}
            known = sum(function in inventory for function in distinct_functions)
            agree = 0
            disagree = []
            classes_by_function: dict[int, set[str]] = defaultdict(set)
            for slot in census.slots:
                classes_by_function[slot.function_va].add(slot.class_name)
            for function in sorted(distinct_functions):
                if function not in inventory:
                    continue
                current = inventory[function]
                classes = classes_by_function[function]
                if any(current.startswith(class_name + "__") for class_name in classes):
                    agree += 1
                else:
                    disagree.append((function, current, sorted(classes)[:2]))
            print()
            print(f"of those, already in the inventory : {known}")
            print(f"  current name matches RTTI class  : {agree}")
            print(f"  current name DISAGREES with RTTI : {len(disagree)}")
            print(f"  not in inventory at all          : {len(distinct_functions) - known}")
            print("\nsample disagreements (RTTI is the stronger evidence):")
            for function, current, classes in disagree[:12]:
                print(f"  {function:#010x}  now={current[:44]:<44} rtti={classes}")

        outputs = [
            (args.out_tsv, vtables_tsv(census)),
            (args.out_hierarchy_tsv, hierarchies_tsv(census)),
            (args.out_edges_tsv, direct_edges_tsv(census)),
            (args.out_rejected_tsv, rejected_references_tsv(census)),
            (args.out_summary_json, census_json(census)),
        ]
        for path, content in outputs:
            if path:
                _write_text(path, content)
                print(f"wrote: {path}")
        if args.ready_dir:
            print(f"READY: {write_ready_bundle(args.ready_dir, args.binary)}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
