from __future__ import annotations

import hashlib
import json
import os
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import re_rtti_vtables as rtti


IMAGE_BASE = 0x00400000
TEXT_VA = 0x00401000
RDATA_VA = 0x00402000
DATA_VA = 0x00403000


def _put_u32(data: bytearray, file_offset: int, value: int) -> None:
    struct.pack_into("<I", data, file_offset, value & 0xFFFFFFFF)


def _pe_fixture() -> bytearray:
    data = bytearray(0xC00)
    # Keep unowned fixture bytes nonzero so they cannot accidentally resemble a
    # zero-signature CompleteObjectLocator during aligned candidate scanning.
    data[0x600:0xC00] = b"\xCC" * 0x600
    data[:2] = b"MZ"
    pe = 0x80
    _put_u32(data, 0x3C, pe)
    data[pe:pe + 4] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, pe + 4, 0x14C, 3, 0, 0, 0, 0xE0, 0x010F)
    optional = pe + 24
    struct.pack_into("<H", data, optional, 0x10B)
    _put_u32(data, optional + 28, IMAGE_BASE)
    sections = optional + 0xE0
    specs = [
        (b".text", 0x200, 0x1000, 0x200, 0x400, 0x60000020),
        (b".rdata", 0x400, 0x2000, 0x400, 0x600, 0x40000040),
        (b".data", 0x200, 0x3000, 0x200, 0xA00, 0xC0000040),
    ]
    for index, (name, virtual_size, rva, raw_size, raw_offset, characteristics) in enumerate(specs):
        offset = sections + index * 40
        data[offset:offset + len(name)] = name
        struct.pack_into("<IIII", data, offset + 8, virtual_size, rva, raw_size, raw_offset)
        _put_u32(data, offset + 36, characteristics)
    data[0x400] = 0xC3
    data[0x410] = 0xC3
    data[0x420] = 0xC3
    return data


def _file_offset(va: int) -> int:
    if TEXT_VA <= va < TEXT_VA + 0x200:
        return 0x400 + va - TEXT_VA
    if RDATA_VA <= va < RDATA_VA + 0x400:
        return 0x600 + va - RDATA_VA
    if DATA_VA <= va < DATA_VA + 0x200:
        return 0xA00 + va - DATA_VA
    raise AssertionError(f"unmapped fixture VA: {va:#x}")


def _put_va_u32(data: bytearray, va: int, value: int) -> None:
    _put_u32(data, _file_offset(va), value)


def _put_type(data: bytearray, va: int, name: str) -> None:
    raw = f".?AV{name}@@\0".encode("ascii")
    offset = _file_offset(va)
    data[offset:offset + 8] = b"\0" * 8
    data[offset + 8:offset + 8 + len(raw)] = raw


def _put_bcd(data: bytearray, va: int, type_va: int, descendants: int, mdisp: int = 0) -> None:
    struct.pack_into(
        "<IIiiiI",
        data,
        _file_offset(va),
        type_va,
        descendants,
        mdisp,
        -1,
        0,
        0,
    )


def _put_chd(data: bytearray, va: int, attributes: int, bases: list[int], array_va: int) -> None:
    for index, base in enumerate(bases):
        _put_va_u32(data, array_va + index * 4, base)
    struct.pack_into("<IIII", data, _file_offset(va), 0, attributes, len(bases), array_va)


def _put_col(data: bytearray, va: int, type_va: int, hierarchy_va: int) -> None:
    struct.pack_into("<IIIII", data, _file_offset(va), 0, 0, 0, type_va, hierarchy_va)


def _simple_fixture() -> bytearray:
    data = _pe_fixture()
    base_type = RDATA_VA + 0x000
    derived_type = RDATA_VA + 0x020
    base_bcd = RDATA_VA + 0x080
    derived_bcd = RDATA_VA + 0x098
    base_array = RDATA_VA + 0x0C0
    derived_array = RDATA_VA + 0x0C8
    base_chd = RDATA_VA + 0x0E0
    derived_chd = RDATA_VA + 0x0F0
    base_col = RDATA_VA + 0x110
    derived_col = RDATA_VA + 0x130

    _put_type(data, base_type, "Base")
    _put_type(data, derived_type, "Derived")
    _put_bcd(data, base_bcd, base_type, 0)
    _put_bcd(data, derived_bcd, derived_type, 1)
    _put_chd(data, base_chd, 0, [base_bcd], base_array)
    _put_chd(data, derived_chd, 0, [derived_bcd, base_bcd], derived_array)
    _put_col(data, base_col, base_type, base_chd)
    _put_col(data, derived_col, derived_type, derived_chd)

    _put_va_u32(data, RDATA_VA + 0x160, base_col)
    _put_va_u32(data, RDATA_VA + 0x164, TEXT_VA)
    _put_va_u32(data, RDATA_VA + 0x168, 0)
    _put_va_u32(data, RDATA_VA + 0x170, derived_col)
    _put_va_u32(data, RDATA_VA + 0x174, TEXT_VA + 0x10)
    _put_va_u32(data, RDATA_VA + 0x178, 0)

    # A valid COL address embedded in non-vtable payload.  The next dword is
    # deliberately mapped data rather than an executable function pointer.
    _put_va_u32(data, DATA_VA, derived_col)
    _put_va_u32(data, DATA_VA + 4, 0x00740072)
    return data


def _nested_fixture() -> bytearray:
    data = _pe_fixture()
    names = ["Derived", "Middle", "Base", "Interface"]
    type_vas = [RDATA_VA + index * 0x20 for index in range(4)]
    bcd_vas = [RDATA_VA + 0x080 + index * 0x18 for index in range(4)]
    descendants = [3, 1, 0, 0]
    for name, type_va in zip(names, type_vas):
        _put_type(data, type_va, name)
    for bcd_va, type_va, count in zip(bcd_vas, type_vas, descendants):
        _put_bcd(data, bcd_va, type_va, count)
    array_va = RDATA_VA + 0x100
    hierarchy_va = RDATA_VA + 0x120
    col_va = RDATA_VA + 0x140
    _put_chd(data, hierarchy_va, 1, bcd_vas, array_va)
    _put_col(data, col_va, type_vas[0], hierarchy_va)
    _put_va_u32(data, RDATA_VA + 0x180, col_va)
    _put_va_u32(data, RDATA_VA + 0x184, TEXT_VA + 0x20)
    _put_va_u32(data, RDATA_VA + 0x188, 0)
    return data


def _fixture_policy(data: bytes) -> rtti.ProofPolicy:
    census = rtti.parse_rtti(data)
    return rtti.ProofPolicy(
        specimen_sha256=hashlib.sha256(data).hexdigest(),
        specimen_bytes=len(data),
        expected_counts=census.counts(),
        expected_rejected_refs=frozenset(
            (row.reference_va, row.col_va) for row in census.rejected_references
        ),
        required_edges=frozenset({("Derived", "Base")}),
    )


def _ready_fixture(root: Path) -> tuple[Path, Path, rtti.ProofPolicy]:
    specimen_bytes = bytes(_simple_fixture())
    specimen = root / "specimen.bin"
    specimen.write_bytes(specimen_bytes)
    policy = _fixture_policy(specimen_bytes)
    bundle = root / "bundle"
    rtti.write_ready_bundle(bundle, specimen, policy)
    return bundle, specimen, policy


def _load_ready(bundle: Path) -> dict[str, object]:
    return json.loads((bundle / "READY.json").read_text(encoding="utf-8"))


def _write_ready(bundle: Path, ready: dict[str, object]) -> None:
    (bundle / "READY.json").write_bytes(rtti._canonical_json_bytes(ready))


def _restamp_artifact(bundle: Path, name: str, ready: dict[str, object]) -> None:
    content = (bundle / Path(name)).read_bytes()
    artifacts = ready["artifacts"]
    assert isinstance(artifacts, dict)
    receipt = artifacts[name]
    assert isinstance(receipt, dict)
    receipt["bytes"] = len(content)
    receipt["sha256"] = hashlib.sha256(content).hexdigest()


def _mutate_tsv_cell(bundle: Path, name: str, column: int, value: str) -> None:
    path = bundle / name
    lines = path.read_text(encoding="utf-8").splitlines()
    fields = lines[1].split("\t")
    fields[column] = value
    lines[1] = "\t".join(fields)
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


class StrictRttiTests(unittest.TestCase):
    def test_false_col_reference_is_not_a_vtable(self) -> None:
        census = rtti.parse_rtti(bytes(_simple_fixture()))
        self.assertEqual(2, len(census.type_descriptors))
        self.assertEqual(2, len(census.cols))
        self.assertEqual(2, len(census.vtables))
        self.assertEqual(1, len(census.rejected_references))
        rejected = census.rejected_references[0]
        self.assertEqual(DATA_VA, rejected.reference_va)
        self.assertEqual("FIRST_SLOT_NOT_TEXT", rejected.reason)
        self.assertEqual(2, len(census.slots))
        self.assertEqual(2, census.counts()["distinctFunctionTargets"])

    def test_poisoned_real_first_slot_is_rejected(self) -> None:
        data = _simple_fixture()
        _put_va_u32(data, RDATA_VA + 0x174, 0x00690074)
        census = rtti.parse_rtti(bytes(data))
        self.assertEqual(1, len(census.vtables))
        self.assertEqual(2, len(census.rejected_references))
        self.assertEqual(
            {RDATA_VA + 0x170, DATA_VA},
            {row.reference_va for row in census.rejected_references},
        )

    def test_poisoned_subtree_size_rejects_col_chain(self) -> None:
        data = _simple_fixture()
        # The derived hierarchy declares two rows, so its root must contain one.
        _put_va_u32(data, RDATA_VA + 0x098 + 4, 0)
        census = rtti.parse_rtti(bytes(data))
        self.assertEqual(1, len(census.cols))
        self.assertEqual(1, len(census.hierarchies))
        self.assertEqual(1, len(census.rejected_col_candidates))
        self.assertIn("root subtree is not exact", census.rejected_col_candidates[0].reason)

    def test_poisoned_base_pointer_rejects_col_chain(self) -> None:
        data = _simple_fixture()
        _put_va_u32(data, RDATA_VA + 0x0C8 + 4, 0xDEADBEEF)
        census = rtti.parse_rtti(bytes(data))
        self.assertEqual(1, len(census.cols))
        self.assertEqual(1, len(census.rejected_col_candidates))
        self.assertIn("invalid base-class descriptor pointer", census.rejected_col_candidates[0].reason)

    def test_preorder_recovers_direct_not_transitive_edges(self) -> None:
        census = rtti.parse_rtti(bytes(_nested_fixture()))
        self.assertEqual(
            {
                ("Derived", "Middle"),
                ("Middle", "Base"),
                ("Derived", "Interface"),
            },
            set(census.direct_edges),
        )
        self.assertNotIn(("Derived", "Base"), census.direct_edges)

    def test_non_pristine_fixture_cannot_cross_publication_gate(self) -> None:
        census = rtti.parse_rtti(bytes(_simple_fixture()))
        with self.assertRaisesRegex(rtti.EvidenceError, "not the pristine specimen"):
            rtti.validate_pristine_census(census)

    def test_ready_replays_specimen_and_frozen_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle, specimen, policy = _ready_fixture(root)
            receipt = rtti.verify_ready_bundle(bundle, specimen, policy)
            self.assertEqual(str(specimen.resolve()), receipt["specimen"]["path"])
            self.assertEqual(
                Path(rtti.__file__).read_bytes(),
                (bundle / rtti.OWNER_ARTIFACT).read_bytes(),
            )
            self.assertFalse(list(root.glob(".bundle.stage-*")))

    def test_publication_failure_cleans_stage_and_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            specimen_bytes = bytes(_simple_fixture())
            specimen = root / "specimen.bin"
            specimen.write_bytes(specimen_bytes)
            policy = _fixture_policy(specimen_bytes)
            target = root / "bundle"
            with mock.patch.object(
                rtti,
                "verify_ready_bundle",
                side_effect=rtti.EvidenceError("injected verifier failure"),
            ):
                with self.assertRaisesRegex(rtti.EvidenceError, "injected verifier failure"):
                    rtti.write_ready_bundle(target, specimen, policy)
            self.assertFalse(target.exists())
            self.assertFalse(list(root.glob(".bundle.stage-*")))

    def test_self_restamped_artifact_and_canonicality_poisons_fail(self) -> None:
        poisons = (
            ("edge row", "direct-edges.tsv", lambda bundle: _mutate_tsv_cell(
                bundle, "direct-edges.tsv", 1, "PoisonBase")),
            ("hierarchy row", "hierarchies.tsv", lambda bundle: _mutate_tsv_cell(
                bundle, "hierarchies.tsv", 1, "PoisonRoot")),
            ("vtable row", "vtables.tsv", lambda bundle: _mutate_tsv_cell(
                bundle, "vtables.tsv", 3, "0x00401020")),
            ("rejected row", "rejected-col-references.tsv", lambda bundle: _mutate_tsv_cell(
                bundle, "rejected-col-references.tsv", 3, "0x00401020")),
            ("reordered header", "vtables.tsv", self._poison_reordered_header),
            ("trailing blank", "vtables.tsv", self._poison_trailing_blank),
        )
        for label, artifact, mutate in poisons:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                bundle, specimen, policy = _ready_fixture(Path(temporary))
                ready = _load_ready(bundle)
                mutate(bundle)
                _restamp_artifact(bundle, artifact, ready)
                _write_ready(bundle, ready)
                with self.assertRaises(rtti.EvidenceError):
                    rtti.verify_ready_bundle(bundle, specimen, policy)

    @staticmethod
    def _poison_reordered_header(bundle: Path) -> None:
        path = bundle / "vtables.tsv"
        lines = path.read_text(encoding="utf-8").splitlines()
        columns = lines[0].split("\t")
        columns[0], columns[1] = columns[1], columns[0]
        lines[0] = "\t".join(columns)
        path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

    @staticmethod
    def _poison_trailing_blank(bundle: Path) -> None:
        path = bundle / "vtables.tsv"
        path.write_bytes(path.read_bytes() + b"\n")

    def test_extra_missing_and_symlink_bundle_entries_fail(self) -> None:
        with self.subTest(label="extra"), tempfile.TemporaryDirectory() as temporary:
            bundle, specimen, policy = _ready_fixture(Path(temporary))
            extra = bundle / "extra.txt"
            extra.write_bytes(b"extra\n")
            ready = _load_ready(bundle)
            artifacts = ready["artifacts"]
            assert isinstance(artifacts, dict)
            artifacts["extra.txt"] = {
                "bytes": extra.stat().st_size,
                "dataRows": None,
                "sha256": hashlib.sha256(extra.read_bytes()).hexdigest(),
            }
            _write_ready(bundle, ready)
            with self.assertRaisesRegex(rtti.EvidenceError, "bundle tree mismatch"):
                rtti.verify_ready_bundle(bundle, specimen, policy)

        with self.subTest(label="missing"), tempfile.TemporaryDirectory() as temporary:
            bundle, specimen, policy = _ready_fixture(Path(temporary))
            (bundle / "direct-edges.tsv").unlink()
            ready = _load_ready(bundle)
            artifacts = ready["artifacts"]
            assert isinstance(artifacts, dict)
            del artifacts["direct-edges.tsv"]
            _write_ready(bundle, ready)
            with self.assertRaisesRegex(rtti.EvidenceError, "bundle tree mismatch"):
                rtti.verify_ready_bundle(bundle, specimen, policy)

        with self.subTest(label="symlink"), tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle, specimen, policy = _ready_fixture(root)
            artifact = bundle / "vtables.tsv"
            outside = root / "outside-vtables.tsv"
            outside.write_bytes(artifact.read_bytes())
            artifact.unlink()
            os.symlink(outside, artifact)
            with self.assertRaisesRegex(rtti.EvidenceError, "symlink/reparse"):
                rtti.verify_ready_bundle(bundle, specimen, policy)

    def test_self_restamped_producer_specimen_and_count_drift_fail(self) -> None:
        with self.subTest(label="producer"), tempfile.TemporaryDirectory() as temporary:
            bundle, specimen, policy = _ready_fixture(Path(temporary))
            owner = bundle / rtti.OWNER_ARTIFACT
            owner.write_bytes(owner.read_bytes() + b"\n# drift\n")
            ready = _load_ready(bundle)
            _restamp_artifact(bundle, rtti.OWNER_ARTIFACT, ready)
            producer = ready["producer"]
            assert isinstance(producer, dict)
            producer["sha256"] = hashlib.sha256(owner.read_bytes()).hexdigest()
            _write_ready(bundle, ready)
            with self.assertRaisesRegex(rtti.EvidenceError, "frozen owner"):
                rtti.verify_ready_bundle(bundle, specimen, policy)

        with self.subTest(label="specimen"), tempfile.TemporaryDirectory() as temporary:
            bundle, specimen, policy = _ready_fixture(Path(temporary))
            specimen.write_bytes(specimen.read_bytes() + b"\0")
            ready = _load_ready(bundle)
            identity = ready["specimen"]
            assert isinstance(identity, dict)
            identity["bytes"] = specimen.stat().st_size
            identity["sha256"] = hashlib.sha256(specimen.read_bytes()).hexdigest()
            _write_ready(bundle, ready)
            with self.assertRaisesRegex(rtti.EvidenceError, "specimen path/bytes/hash"):
                rtti.verify_ready_bundle(bundle, specimen, policy)

        with self.subTest(label="specimen path"), tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle, specimen, policy = _ready_fixture(root)
            alias = root / "same-bytes-other-path.bin"
            alias.write_bytes(specimen.read_bytes())
            ready = _load_ready(bundle)
            identity = ready["specimen"]
            assert isinstance(identity, dict)
            identity["path"] = str(alias.resolve())
            _write_ready(bundle, ready)
            with self.assertRaisesRegex(rtti.EvidenceError, "verifier-bound path"):
                rtti.verify_ready_bundle(bundle, specimen, policy)

        with self.subTest(label="counts"), tempfile.TemporaryDirectory() as temporary:
            bundle, specimen, policy = _ready_fixture(Path(temporary))
            census_path = bundle / "census.json"
            census = json.loads(census_path.read_text(encoding="utf-8"))
            census["counts"]["vtableSlots"] += 1
            census_path.write_bytes(rtti._canonical_json_bytes(census))
            ready = _load_ready(bundle)
            ready["counts"]["vtableSlots"] += 1
            _restamp_artifact(bundle, "census.json", ready)
            _write_ready(bundle, ready)
            with self.assertRaises(rtti.EvidenceError):
                rtti.verify_ready_bundle(bundle, specimen, policy)


if __name__ == "__main__":
    unittest.main()
