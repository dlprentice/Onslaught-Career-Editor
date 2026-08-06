#!/usr/bin/env python3
"""Focused falsification tests for exact-body and native-canary accounting."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import re_coverage_ledger as ledger


class FunctionPopulationDateTests(unittest.TestCase):
    def test_canonical_dated_table_keeps_its_published_date(self) -> None:
        self.assertIn("2026-07-27", ledger.function_population_date(ledger.DEFAULT_NAMES))

    def test_disposable_full_inventory_does_not_inherit_the_canonical_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supplied = Path(temporary) / "after-functions.tsv"
            supplied.write_text("address\tname\tbodyMin\tbodyMax\n", encoding="utf-8")
            value = ledger.function_population_date(supplied)
            self.assertTrue(value.startswith("UNKNOWN"), value)
            self.assertNotIn("2026-07-27", value)


class FakeSpecimen:
    image_base = 0x00400000
    text_lo = 0x1000
    text_hi = 0x1020

    def __init__(self) -> None:
        self.data = bytes(range(0x20))

    def bytes_at_rva(self, rva: int, size: int) -> bytes:
        start = rva - self.text_lo
        return self.data[start : start + size]


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_graph(root: Path, spec: FakeSpecimen) -> tuple[Path, list[dict]]:
    rows = [
        (0x00401000, "First", 1, 0x00401000, 0x00401002),
        (0x00401000, "First", 2, 0x00401004, 0x00401006),
        (0x00401008, "Second", 1, 0x00401008, 0x0040100B),
    ]
    body = root / "body-ranges.tsv"
    lines = [
        f"# schema={ledger.PARITY_GRAPH_TSV_SCHEMA}",
        f"# executableMd5={hashlib.md5(spec.data, usedforsecurity=False).hexdigest()}",
        f"# imageBase=0x{spec.image_base:08x}",
        (
            "functionAddress\tfunctionName\trangeOrdinal\trangeMin\trangeMax\t"
            "rangeEndExclusive\trangeBytes\trangeSha256"
        ),
    ]
    for entry, name, ordinal, lo, hi in rows:
        payload = spec.bytes_at_rva(lo - spec.image_base, hi - lo)
        lines.append(
            f"0x{entry:08x}\t{name}\t{ordinal}\t0x{lo:08x}\t0x{hi - 1:08x}\t"
            f"0x{hi:08x}\t{hi - lo}\t{_sha256(payload)}"
        )
    body.write_text("\n".join(lines) + "\n", encoding="utf-8")

    receipt = root / "parity-graph.ready.json"
    receipt.write_text(
        json.dumps(
            {
                "schemaVersion": ledger.PARITY_GRAPH_RECEIPT_SCHEMA,
                "program": {
                    "executableMd5": hashlib.md5(
                        spec.data, usedforsecurity=False
                    ).hexdigest(),
                    "imageBase": f"0x{spec.image_base:08x}",
                },
                "bodyRanges": {
                    "file": body.name,
                    "bytes": body.stat().st_size,
                    "sha256": ledger.sha256_of(body),
                    "functionCount": 2,
                    "rangeCount": 3,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    names = [
        {"va": 0x00401000, "name": "First"},
        {"va": 0x00401008, "name": "Second"},
    ]
    return receipt, names


class ExactBodyGraphTests(unittest.TestCase):
    def test_observed_native_entry_does_not_imply_a_runtime_contract(self) -> None:
        self.assertEqual("U0_NONE", ledger.evidence_proxy_tier("FUN", 0, 0))
        self.assertEqual("U1_NAMED_ONLY", ledger.evidence_proxy_tier("NAMED", 0, 0))

    def test_name_table_loader_accepts_full_inventory_column_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "inventory.tsv"
            path.write_text(
                "address\tname\tfqname\tnameSource\tbodyBytes\tbodyMin\tbodyMax\n"
                "0x00401000\tFirst\tFirst\tDEFAULT\t4\t0x00401000\t0x00401003\n",
                encoding="utf-8",
            )
            rows, headers = ledger.load_name_table(path)

        self.assertEqual([], headers)
        self.assertEqual(
            {
                "va": 0x00401000,
                "name": "First",
                "hullLoVa": 0x00401000,
                "hullHiVa": 0x00401003,
            },
            rows[0],
        )

    def test_fragmented_bodies_are_authenticated_and_counted_exactly(self) -> None:
        spec = FakeSpecimen()
        with tempfile.TemporaryDirectory() as temporary:
            receipt, names = write_graph(Path(temporary), spec)
            graph = ledger.load_exact_body_graph(receipt, spec, names)

        self.assertEqual(2, graph["functionCount"])
        self.assertEqual(3, graph["rangeCount"])
        self.assertEqual(7, graph["unionBytes"])
        self.assertEqual([(0x1000, 0x1002), (0x1004, 0x1006)], graph["byEntryVa"][0x00401000])
        self.assertEqual(0, graph["nameMismatchCount"])

    def test_a_changed_body_file_is_rejected_by_the_ready_receipt(self) -> None:
        spec = FakeSpecimen()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt, names = write_graph(root, spec)
            body = root / "body-ranges.tsv"
            body.write_text(body.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(ledger.LedgerInputError, "byte count"):
                ledger.load_exact_body_graph(receipt, spec, names)

    def test_specimen_bytes_are_checked_for_every_fragment(self) -> None:
        spec = FakeSpecimen()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt, names = write_graph(root, spec)
            changed = bytearray(spec.data)
            changed[4] ^= 0xFF
            spec.data = bytes(changed)
            record = json.loads(receipt.read_text(encoding="utf-8"))
            changed_md5 = hashlib.md5(spec.data, usedforsecurity=False).hexdigest()
            record["program"]["executableMd5"] = changed_md5
            body = root / "body-ranges.tsv"
            text = body.read_text(encoding="utf-8")
            old_md5 = text.split("# executableMd5=", 1)[1].splitlines()[0]
            body.write_text(text.replace(old_md5, changed_md5, 1), encoding="utf-8")
            record["bodyRanges"]["bytes"] = body.stat().st_size
            record["bodyRanges"]["sha256"] = ledger.sha256_of(body)
            receipt.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ledger.LedgerInputError, "body-range bytes"):
                ledger.load_exact_body_graph(receipt, spec, names)

    def test_name_table_and_body_export_must_cover_the_same_entries(self) -> None:
        spec = FakeSpecimen()
        with tempfile.TemporaryDirectory() as temporary:
            receipt, names = write_graph(Path(temporary), spec)
            names.pop()
            with self.assertRaisesRegex(ledger.LedgerInputError, "populations differ"):
                ledger.load_exact_body_graph(receipt, spec, names)


class NativeCanaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = [
            {"coverageSha256": "b" * 64},
            {"coverageSha256": "a" * 64},
        ]
        self.digest = ledger.coverage_set_sha256(self.sources)
        self.native_stamp = {"sha256": "c" * 64}

    def test_coverage_set_identity_is_order_independent(self) -> None:
        self.assertEqual(self.digest, ledger.coverage_set_sha256(list(reversed(self.sources))))

    def test_no_canary_means_no_universal_expected_count(self) -> None:
        result = ledger.native_canary_result(None, self.digest, self.native_stamp, 64, 55)
        self.assertEqual("NOT_CONFIGURED", result["status"])

    def test_matching_input_bound_canary_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "canary.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": ledger.NATIVE_CANARY_SCHEMA,
                        "coverageSetSha256": self.digest,
                        "nativeRegistrySha256": self.native_stamp["sha256"],
                        "expected": {
                            "handlerFirstByteObserved": 64,
                            "handlerFirstByteObservedExcludingContradicted": 55,
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = ledger.native_canary_result(
                path, self.digest, self.native_stamp, 64, 55
            )
        self.assertEqual("PASS", result["status"])

    def test_canary_for_a_different_coverage_set_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "canary.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": ledger.NATIVE_CANARY_SCHEMA,
                        "coverageSetSha256": "0" * 64,
                        "nativeRegistrySha256": self.native_stamp["sha256"],
                        "expected": {
                            "handlerFirstByteObserved": 64,
                            "handlerFirstByteObservedExcludingContradicted": 55,
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ledger.LedgerInputError, "different coverage"):
                ledger.native_canary_result(path, self.digest, self.native_stamp, 64, 55)

    def test_wrong_count_fails_instead_of_becoming_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "canary.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": ledger.NATIVE_CANARY_SCHEMA,
                        "coverageSetSha256": self.digest,
                        "nativeRegistrySha256": self.native_stamp["sha256"],
                        "expected": {
                            "handlerFirstByteObserved": 60,
                            "handlerFirstByteObservedExcludingContradicted": 59,
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ledger.LedgerInputError, "canary failed"):
                ledger.native_canary_result(path, self.digest, self.native_stamp, 64, 55)


if __name__ == "__main__":
    raise SystemExit(0 if unittest.main(verbosity=2, exit=False).result.wasSuccessful() else 1)
