# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for tools/ttd_coverage_index.py (PROGRAM P5).

The real corpus lives read-only on G:; these tests never touch it.  They build
synthetic receipt trees in a temp directory, exercise every fail-closed branch,
and prove build/query are deterministic and idempotent.
"""

from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "ttd_coverage_index.py"

_spec = importlib.util.spec_from_file_location("ttd_coverage_index", TOOL_PATH)
ttd_coverage_index = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(ttd_coverage_index)

BASE = 0x400000
MODULE_SIZE = 0x200000
SCHEMA_RECEIPT = ttd_coverage_index.SCHEMA_RECEIPT


def _hex(value: int) -> str:
    return hex(value)


def metadata_row(base: int = BASE) -> dict:
    return {
        "schema": SCHEMA_RECEIPT,
        "kind": "metadata",
        "trace": f"G:\\fake\\trace-{base:x}.run",
        "module_requested": "BEA.exe",
        "module_name": "C:\\fake\\BEA.exe",
        "module_base": _hex(base),
        "module_size": _hex(MODULE_SIZE),
        "module_timestamp": "0x3ED21313",
        "module_checksum": "0x0",
        "upstream_commit": "1b0b2f336f959c1caadcd51bb2c82149a9bce2d5",
        "api_package": "Microsoft.TimeTravelDebugging.Apis/0.9.5",
    }


def summary_row(covered_bytes: int, **overrides: object) -> dict:
    row = {
        "schema": SCHEMA_RECEIPT,
        "kind": "summary",
        "covered_bytes": _hex(covered_bytes),
        "counters_quarantined": False,
        "replay_complete": True,
        "marker_assertions_passed": True,
        "collector_checks_passed": True,
        "stop_reason": "Process",
    }
    row.update(overrides)
    return row


def range_row(index: int, va_start: int, va_end: int,
              base: int = BASE) -> dict:
    return {
        "schema": SCHEMA_RECEIPT,
        "kind": "range",
        "index": index,
        "rva_start": _hex(va_start - base),
        "rva_end_exclusive": _hex(va_end - base),
        "va_start": _hex(va_start),
        "va_end_exclusive": _hex(va_end),
        "byte_count": va_end - va_start,
    }


def assertion_row(va: int, observed: bool, base: int = BASE) -> dict:
    return {
        "schema": SCHEMA_RECEIPT,
        "kind": "assertion",
        "expectation": "hit" if observed else "miss",
        "rva": _hex(va - base),
        "va": _hex(va),
        "observed": observed,
        "pass": True,
    }


def gap_summary_row(**overrides: object) -> dict:
    row = {
        "schema": SCHEMA_RECEIPT,
        "kind": "gap-summary",
        "total": "0",
    }
    for field in (*ttd_coverage_index.GAP_BUCKET_FIELDS,
                  *ttd_coverage_index.GAP_EVENT_FIELDS):
        row[field] = "0"
    row.update(overrides)
    return row


class ReceiptTree:
    """Builds a temp tree of synthetic coverage.jsonl receipts."""

    def __init__(self, root: pathlib.Path) -> None:
        self.root = root

    def write(self, trace_name: str, rows: list[dict],
              auto_contract: bool = True) -> pathlib.Path:
        directory = self.root / trace_name
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "coverage.jsonl"
        prepared = [dict(row) for row in rows]
        if auto_contract and not any(
            row.get("kind") == "gap-summary" for row in prepared
        ):
            insertion = next(
                (index for index, row in enumerate(prepared)
                 if row.get("kind") == "summary"),
                len(prepared),
            )
            prepared.insert(insertion, gap_summary_row())
        if auto_contract and not any(
            row.get("kind") == "assertion" for row in prepared
        ):
            metadata = next(
                (row for row in prepared if row.get("kind") == "metadata"), None
            )
            ranges = [row for row in prepared if row.get("kind") == "range"]
            if metadata is not None and ranges:
                base = int(metadata["module_base"], 16)
                size = int(metadata["module_size"], 16)
                hit_va = int(ranges[0]["va_start"], 16)
                miss_va = base + size - 1
                if any(int(row["va_start"], 16) <= miss_va
                       < int(row["va_end_exclusive"], 16) for row in ranges):
                    raise AssertionError("synthetic miss control is covered")
                insertion = next(
                    (index for index, row in enumerate(prepared)
                     if row.get("kind") in ("gap-summary", "summary")),
                    len(prepared),
                )
                prepared[insertion:insertion] = [
                    assertion_row(hit_va, True, base),
                    assertion_row(miss_va, False, base),
                ]
        range_count = sum(row.get("kind") == "range" for row in prepared)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            for row in prepared:
                if row.get("kind") == "summary":
                    row.setdefault("range_count", range_count)
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
        return path

    @staticmethod
    def good_trace(trace_name: str = "level-a") -> list[dict]:
        return [
            metadata_row(),
            range_row(0, 0x401000, 0x401034),
            range_row(1, 0x404F90, 0x405000),
            assertion_row(0x4F9A90 - 0x400000 + 0x400000, False),  # placeholder
        ]


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="ttd-cov-"))
        self.tree = ReceiptTree(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def index_for(self, *traces: str) -> dict:
        return ttd_coverage_index.build_index(str(self.tmp))

    def test_build_over_a_well_formed_tree_succeeds_and_hashes(self) -> None:
        self.tree.write("level-a", [
            metadata_row(),
            range_row(0, 0x401000, 0x401034),
            range_row(1, 0x404F90, 0x405000),
            assertion_row(0x401010, True),
            assertion_row(0x401034, False),
            summary_row(0x34 + 0x70),
        ])
        payload = ttd_coverage_index.build_index(str(self.tmp))
        self.assertEqual(payload["receipt_count"], 1)
        self.assertEqual(payload["union_covered_bytes"], 0x34 + 0x70)
        self.assertEqual(len(payload["receipt_set_sha256"]), 64)
        trace = payload["traces"][0]
        self.assertEqual(trace["name"], "level-a")
        self.assertEqual(trace["covered_bytes"], 0x34 + 0x70)
        self.assertTrue(pathlib.Path(
            self.tmp / "level-a" / "coverage.jsonl").exists())

    def test_build_is_idempotent_and_byte_stable(self) -> None:
        rows = [
            metadata_row(),
            range_row(0, 0x401000, 0x401034),
            summary_row(0x34),
        ]
        self.tree.write("level-b", rows)
        first = ttd_coverage_index.dump_json(
            ttd_coverage_index.build_index(str(self.tmp)))
        second = ttd_coverage_index.dump_json(
            ttd_coverage_index.build_index(str(self.tmp)))
        self.assertEqual(first, second)

    def test_empty_root_fails_closed(self) -> None:
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_unreadable_subtree_fails_closed_instead_of_vanishing(self) -> None:
        denied = self.tmp / "denied"

        def unreadable_walk(_root: str, onerror=None):
            assert onerror is not None
            onerror(PermissionError(13, "permission denied", str(denied)))
            return iter(())

        with mock.patch.object(ttd_coverage_index.os, "walk", unreadable_walk):
            with self.assertRaisesRegex(
                ttd_coverage_index.StructuralError,
                "unreadable receipt subtree",
            ):
                ttd_coverage_index.collect_receipt_paths(str(self.tmp))

    def test_duplicate_range_rows_fail_closed(self) -> None:
        self.tree.write("level-c", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            range_row(1, 0x401000, 0x401004),
            summary_row(8),
        ])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_overlapping_range_rows_fail_closed(self) -> None:
        self.tree.write("level-c2", [
            metadata_row(),
            range_row(0, 0x401000, 0x401010),
            range_row(1, 0x401008, 0x401018),
            summary_row(0x18),
        ])
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "overlapping range rows"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_summary_disagreement_fails_closed(self) -> None:
        self.tree.write("level-d", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(999),
        ])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_summary_range_count_disagreement_fails_closed(self) -> None:
        self.tree.write("level-d2", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(4, range_count=2),
        ])
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "range_count 2"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_range_va_rva_delta_disagreement_fails_closed(self) -> None:
        bad = range_row(0, 0x401000, 0x401004)
        bad["rva_start"] = "0x2000"
        bad["rva_end_exclusive"] = "0x2004"
        self.tree.write("level-d3", [metadata_row(), bad, summary_row(4)])
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "VA/RVA delta"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_out_of_domain_range_fails_closed(self) -> None:
        self.tree.write("level-e", [
            metadata_row(),
            range_row(0, BASE + MODULE_SIZE, BASE + MODULE_SIZE + 16),
            summary_row(16),
        ])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_unknown_kind_fails_closed(self) -> None:
        self.tree.write("level-f", [
            metadata_row(),
            {"schema": SCHEMA_RECEIPT, "kind": "mystery"},
            summary_row(0),
        ])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_wrong_schema_fails_closed(self) -> None:
        bad = metadata_row()
        bad["schema"] = "bea.ttd.exec-coverage.v2"
        self.tree.write("level-g", [bad, summary_row(0)])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_missing_gap_summary_fails_closed(self) -> None:
        rows = [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            assertion_row(0x401000, True),
            assertion_row(0x5FFFFF, False),
            summary_row(4),
        ]
        self.tree.write("level-g1", rows, auto_contract=False)
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "no gap-summary row"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_duplicate_gap_summary_fails_closed(self) -> None:
        self.tree.write("level-g2", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            gap_summary_row(),
            gap_summary_row(),
            summary_row(4),
        ])
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "duplicate gap-summary row"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_malformed_gap_summary_fails_closed(self) -> None:
        malformed = gap_summary_row()
        malformed.pop("event_KernelCall")
        self.tree.write("level-g3", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            malformed,
            summary_row(4),
        ])
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "malformed gap-summary fields"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_contradictory_gap_accounting_fails_closed(self) -> None:
        contradictory = gap_summary_row(total="1")
        self.tree.write("level-g4", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            contradictory,
            summary_row(4),
        ])
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "contradictory accounting"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_invalid_json_line_fails_closed(self) -> None:
        directory = self.tmp / "level-h"
        directory.mkdir()
        with open(directory / "coverage.jsonl", "w", encoding="utf-8") as handle:
            handle.write("{not json}\n")
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_missing_metadata_or_summary_fails_closed(self) -> None:
        self.tree.write("level-i", [metadata_row(), range_row(0, 0x401000, 0x401004)])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))
        self.tree.write("level-j", [range_row(0, 0x401000, 0x401004)])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_duplicate_trace_names_fail_closed(self) -> None:
        rows = [metadata_row(), range_row(0, 0x401000, 0x401004), summary_row(4)]
        ReceiptTree(self.tmp / "outer").write("level-k", rows)
        self.tree.write("level-k", rows)
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "duplicate trace names"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_divergent_module_bases_fail_closed_at_identity_gate(self) -> None:
        shifted_base = 0x500000
        shifted = metadata_row(base=shifted_base)
        self.tree.write("level-l", [
            metadata_row(), range_row(0, 0x401000, 0x401004), summary_row(4),
        ])
        self.tree.write("level-m", [
            shifted,
            range_row(0, 0x501000, 0x501004, base=shifted_base),
            summary_row(4),
        ])
        with self.assertRaisesRegex(
            ttd_coverage_index.StructuralError,
            "divergent module identity.*module_base",
        ):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_divergent_module_size_fails_closed_at_identity_gate(self) -> None:
        different_size = metadata_row()
        different_size["module_size"] = _hex(MODULE_SIZE + 0x1000)
        rows = [range_row(0, 0x401000, 0x401004), summary_row(4)]
        self.tree.write("level-l2", [metadata_row(), *rows])
        self.tree.write("level-m2", [different_size, *rows])
        with self.assertRaisesRegex(
            ttd_coverage_index.StructuralError,
            "divergent module identity.*module_size",
        ):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_quarantined_counters_are_recorded_not_hidden(self) -> None:
        # Two retained 521 takes carry counters_quarantined=true. Their range
        # rows are structurally sound, so the receipt builds with the
        # quarantine recorded verbatim in the index -- visible, never silent.
        self.tree.write("level-n4", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(4, counters_quarantined=True),
        ])
        payload = ttd_coverage_index.build_index(str(self.tmp))
        self.assertEqual(payload["traces_with_quarantined_counters"], ["level-n4"])
        self.assertTrue(payload["traces"][0]["counters_quarantined"])

    def test_timer_stopped_thread_class_is_accepted(self) -> None:
        # The level-opening corpus stops on a timer: replay ends on a Thread
        # event and the collector's terminal checks read false. That measured,
        # adjudicated trace class must build, not fail.
        self.tree.write("level-n2", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(4, replay_complete=False,
                        collector_checks_passed=False, stop_reason="Thread"),
        ])
        payload = ttd_coverage_index.build_index(str(self.tmp))
        self.assertEqual(payload["receipt_count"], 1)

    def test_replay_complete_with_non_process_stop_fails_closed(self) -> None:
        self.tree.write("level-n3", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(4, stop_reason="Thread"),
        ])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_process_stop_with_failed_collector_checks_fails_closed(self) -> None:
        self.tree.write("level-n5", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(4, collector_checks_passed=False),
        ])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_failed_marker_assertions_fail_closed(self) -> None:
        self.tree.write("level-o", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(4, marker_assertions_passed=False),
        ])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_assertion_contradicting_ranges_fails_closed(self) -> None:
        self.tree.write("level-p", [
            metadata_row(),
            range_row(0, 0x401000, 0x401034),
            assertion_row(0x401034, True),
            summary_row(0x34),
        ])
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_agreeing_assertions_pass(self) -> None:
        self.tree.write("level-q", [
            metadata_row(),
            range_row(0, 0x401000, 0x401034),
            assertion_row(0x401010, True),
            assertion_row(0x401034, False),
            summary_row(0x34),
        ])
        payload = ttd_coverage_index.build_index(str(self.tmp))
        self.assertEqual(payload["receipt_count"], 1)

    def test_missing_required_miss_control_fails_closed(self) -> None:
        self.tree.write("level-q2", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            assertion_row(0x401000, True),
            summary_row(4),
        ])
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "required assertion controls differ"):
            ttd_coverage_index.build_index(str(self.tmp))

    def test_divergent_required_controls_across_receipts_fail_closed(self) -> None:
        self.tree.write("level-q3", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            assertion_row(0x401000, True),
            assertion_row(0x5FFFFF, False),
            summary_row(4),
        ])
        self.tree.write("level-q4", [
            metadata_row(),
            range_row(0, 0x401010, 0x401014),
            assertion_row(0x401010, True),
            assertion_row(0x5FFFFF, False),
            summary_row(4),
        ])
        with self.assertRaisesRegex(
            ttd_coverage_index.StructuralError,
            "divergent required assertion controls across receipts",
        ):
            ttd_coverage_index.build_index(str(self.tmp))


class QueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="ttd-q-"))
        self.index_path = self.tmp / "index.json"
        tree = ReceiptTree(self.tmp)
        tree.write("level-hit", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            range_row(1, 0x407060, 0x40713E),
            range_row(2, 0x4F9A90, 0x4F9AC0),
            summary_row(4 + 0xDE + 0x30),
        ])
        tree.write("level-clean", [
            metadata_row(),
            range_row(0, 0x401000, 0x401034),
            summary_row(0x34),
        ])
        payload = ttd_coverage_index.build_index(str(self.tmp))
        with open(self.index_path, "w", encoding="utf-8") as handle:
            handle.write(ttd_coverage_index.dump_json(payload))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def tampered_index(self, name: str, mutate, rebind: bool = True) -> pathlib.Path:
        with open(self.index_path, encoding="utf-8") as handle:
            payload = json.load(handle)
        mutate(payload)
        if rebind:
            payload["content_sha256"] = (
                ttd_coverage_index._index_content_sha256(payload)
            )
        path = self.tmp / name
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        return path

    def test_membership_positive_miss_and_union(self) -> None:
        result = ttd_coverage_index.run_query(str(self.index_path),
                                              ["0x407060", "0x401010"], [], [])
        by_address = {e["address"]: e for e in result["addresses"]}
        self.assertEqual(by_address[hex(0x407060)]["traces"], ["level-hit"])
        self.assertEqual(by_address[hex(0x401010)]["traces"],
                         ["level-clean"])
        # A bare membership query carries no controls; "pass" reflects them.
        self.assertTrue(result["pass"])

    def test_must_hit_control_passes_when_hit(self) -> None:
        result = ttd_coverage_index.run_query(str(self.index_path),
                                              ["0x407060"], ["0x407060"], [])
        self.assertTrue(result["pass"])

    def test_must_hit_control_fails_when_absent(self) -> None:
        result = ttd_coverage_index.run_query(str(self.index_path),
                                              ["0x407060"], ["0x672FD0"], [])
        self.assertFalse(result["pass"])
        self.assertEqual(result["controls"][0]["control"], "must_hit")

    def test_must_miss_control_passes_when_absent_everywhere(self) -> None:
        result = ttd_coverage_index.run_query(str(self.index_path),
                                              ["0x672FD0"], [], ["0x672FD0"])
        self.assertTrue(result["pass"])

    def test_must_miss_control_fails_when_actually_covered(self) -> None:
        result = ttd_coverage_index.run_query(str(self.index_path),
                                              ["0x407060"], [], ["0x407060"])
        self.assertFalse(result["pass"])

    def test_rva_query_matches_va_query(self) -> None:
        via_va = ttd_coverage_index.run_query(str(self.index_path),
                                              ["0x407134"], [], [])
        self.assertEqual(via_va["addresses"][0]["traces"], ["level-hit"])

    def test_query_input_hash_is_stable_and_binds_controls(self) -> None:
        first = ttd_coverage_index.run_query(
            str(self.index_path), ["0x407060"], ["0x407060"], [])
        second = ttd_coverage_index.run_query(
            str(self.index_path), ["0x407060"], ["0x407060"], [])
        changed = ttd_coverage_index.run_query(
            str(self.index_path), ["0x407060"], [], ["0x407060"])
        self.assertEqual(first["query_input_sha256"],
                         second["query_input_sha256"])
        self.assertNotEqual(first["query_input_sha256"],
                            changed["query_input_sha256"])
        self.assertEqual(first["query_input"], {
            "addresses": ["0x407060"],
            "expect_hit": ["0x407060"],
            "expect_miss": [],
        })

    def test_tampered_module_identity_fails_content_binding(self) -> None:
        path = self.tampered_index(
            "module-tamper.json",
            lambda payload: payload["module"].__setitem__("module_size", "0x300000"),
            rebind=False,
        )
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "content_sha256 mismatch"):
            ttd_coverage_index.load_index(str(path))

    def test_duplicate_tampered_trace_name_fails_semantic_readback(self) -> None:
        path = self.tampered_index(
            "name-tamper.json",
            lambda payload: payload["traces"][1].__setitem__(
                "name", payload["traces"][0]["name"]),
        )
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "duplicate trace names"):
            ttd_coverage_index.load_index(str(path))

    def test_tampered_interval_type_fails_semantic_readback(self) -> None:
        path = self.tampered_index(
            "type-tamper.json",
            lambda payload: payload["traces"][0]["intervals"][0].__setitem__(0, 7),
        )
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "expected hex-string"):
            ttd_coverage_index.load_index(str(path))

    def test_tampered_interval_order_fails_semantic_readback(self) -> None:
        path = self.tampered_index(
            "order-tamper.json",
            lambda payload: payload["traces"][1]["intervals"].reverse(),
        )
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "unsorted or overlapping"):
            ttd_coverage_index.load_index(str(path))

    def test_tampered_receipt_hash_fails_manifest_readback(self) -> None:
        path = self.tampered_index(
            "receipt-hash-tamper.json",
            lambda payload: payload["traces"][0].__setitem__("sha256", "0" * 64),
        )
        with self.assertRaisesRegex(ttd_coverage_index.StructuralError,
                                    "receipt_set_sha256 mismatch"):
            ttd_coverage_index.load_index(str(path))

    def test_bad_address_token_fails_closed(self) -> None:
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index._split_addresses("0xZZZ")

    def test_missing_index_file_fails_closed(self) -> None:
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.load_index(str(self.tmp / "nope.json"))

    def test_non_index_document_fails_closed(self) -> None:
        path = self.tmp / "wrong.json"
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"schema": "something.else.v1"}, handle)
        with self.assertRaises(ttd_coverage_index.StructuralError):
            ttd_coverage_index.load_index(str(path))

    def tampered_rebound_receipt(
        self, receipt_value: str, name: str
    ) -> pathlib.Path:
        """Re-bind one trace's receipt to an impossible path.

        Mirrors the independent RED reproducer on tip 7408b7d2 end to end:
        change one trace ``receipt``, re-sort traces, and recompute BOTH
        ``receipt_set_sha256`` and the canonical ``content_sha256``, so a
        rejection can only come from deep path validation -- not from stale
        hashes or manifest binding.
        """
        with open(self.index_path, encoding="utf-8") as handle:
            payload = json.load(handle)
        payload["traces"][0]["receipt"] = receipt_value
        payload["traces"] = sorted(payload["traces"], key=lambda t: t["receipt"])
        manifest = hashlib.sha256()
        for trace in payload["traces"]:
            manifest.update(trace["receipt"].encode("utf-8"))
            manifest.update(b"\n")
            manifest.update(trace["sha256"].encode("ascii"))
            manifest.update(b"\n")
        payload["receipt_set_sha256"] = manifest.hexdigest()
        payload.pop("content_sha256", None)
        payload["content_sha256"] = (
            ttd_coverage_index._index_content_sha256(payload)
        )
        path = self.tmp / name
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        return path

    def test_rebound_drive_absolute_receipt_fails_at_path_branch(self) -> None:
        # RED reproducer 1/2 (rejected P5 tip 7408b7d2 accepted this index).
        path = self.tampered_rebound_receipt(
            "C:/evil/coverage.jsonl", "rebind-drive-absolute.json"
        )
        with self.assertRaisesRegex(
            ttd_coverage_index.StructuralError,
            r"noncanonical receipt path 'C:/evil/coverage\.jsonl'",
        ):
            ttd_coverage_index.load_index(str(path))

    def test_rebound_wrong_basename_receipt_fails_at_path_branch(self) -> None:
        # RED reproducer 2/2 (rejected P5 tip 7408b7d2 accepted this index).
        path = self.tampered_rebound_receipt(
            "level-clean/not-coverage.txt", "rebind-wrong-basename.json"
        )
        with self.assertRaisesRegex(
            ttd_coverage_index.StructuralError,
            "does not name coverage.jsonl",
        ):
            ttd_coverage_index.load_index(str(path))

    def test_canonical_receipt_path_shape_matrix(self) -> None:
        context = "shape-matrix"
        accept = [
            "level-a/coverage.jsonl",
            "a/b/c/deep/coverage.jsonl",
            "level-a.b-c/coverage.jsonl",
            # A receipt directly in the root is relative, normalized, and
            # names the right file: canonical, though no real corpus emits it.
            "coverage.jsonl",
        ]
        for value in accept:
            self.assertEqual(
                ttd_coverage_index._canonical_receipt_path(value, context),
                value,
                f"canonical form must be accepted: {value!r}",
            )
        rejects = {
            # Windows drive-absolute / drive-relative / alternate-stream colon
            # syntax in every shape.
            "C:/evil/coverage.jsonl": "colon",
            "c:\\evil\\coverage.jsonl": "backslash",
            "C:evil/coverage.jsonl": "colon",
            "G:/bea-ttd/level-a/coverage.jsonl": "colon",
            "stream/coverage.jsonl:ads": "colon",
            # UNC / POSIX rooted.
            "//host/share/coverage.jsonl": ("rooted", "empty"),
            "//./pipe/coverage.jsonl": "rooted",
            "/coverage.jsonl": "rooted",
            "/level-a/coverage.jsonl": "rooted",
            # Separators and normalization.
            "level-a\\coverage.jsonl": "backslash",
            "level-a//coverage.jsonl": "empty",
            "./coverage.jsonl": "empty",
            "level-a/./coverage.jsonl": "'.'",
            "level-a/../level-b/coverage.jsonl": "'..'",
            "../escape/coverage.jsonl": "'..'",
            "level-a/coverage.jsonl/": "empty",
            # Basename contract: every stored receipt names coverage.jsonl.
            "level-clean/not-coverage.txt": "does not name coverage.jsonl",
            "level-a/coverage.json": "does not name coverage.jsonl",
            "": "invalid receipt path",
        }
        for value, fragment in rejects.items():
            with self.assertRaisesRegex(
                ttd_coverage_index.StructuralError,
                re.escape(fragment)
                if isinstance(fragment, str) else "|".join(fragment),
                msg=f"must reject {value!r}",
            ):
                ttd_coverage_index._canonical_receipt_path(value, context)
        for bad_type in (None, 7, ["level-a/coverage.jsonl"],
                         b"level-a/coverage.jsonl"):
            with self.assertRaisesRegex(
                ttd_coverage_index.StructuralError,
                "invalid receipt path",
                msg=f"must reject non-string {bad_type!r}",
            ):
                ttd_coverage_index._canonical_receipt_path(bad_type, context)

    def test_build_over_nested_tree_emits_and_accepts_canonical_paths(self) \
            -> None:
        tree = ReceiptTree(self.tmp / "outer")
        rows = [metadata_row(), range_row(0, 0x401000, 0x401004),
                summary_row(4)]
        tree.write("level-inner/nested", rows)
        payload = ttd_coverage_index.build_index(str(self.tmp / "outer"))
        receipts = [trace["receipt"] for trace in payload["traces"]]
        self.assertEqual(receipts, ["level-inner/nested/coverage.jsonl"])
        index_path = self.tmp / "nested-index.json"
        with open(index_path, "w", encoding="utf-8") as handle:
            handle.write(ttd_coverage_index.dump_json(payload))
        # Round-trip: what build emits is exactly what load accepts.
        ttd_coverage_index.load_index(str(index_path))



class CommandLineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="ttd-cli-"))
        self.tree = ReceiptTree(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run_tool(self, *argv: str) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(TOOL_PATH), *argv]
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def test_cli_build_then_query_round_trip_with_controls(self) -> None:
        self.tree.write("level-x", [
            metadata_row(),
            range_row(0, 0x407060, 0x407064),
            range_row(1, 0x4F9A90, 0x4F9A94),
            summary_row(8),
        ])
        index_path = os.path.join(self.tmp, "..", "shared-index.json")
        built = self._run_tool("build", "--root", str(self.tmp),
                               "--out", str(index_path))
        self.assertEqual(built.returncode, 0, built.stderr)
        queried = self._run_tool(
            "query", "--index", str(index_path),
            "--rva", "0x7060,0xF9A90,0x272FD0",
            "--expect-hit", "0x004f9a90",
            "--expect-miss", "0x00672fd0",
        )
        self.assertEqual(queried.returncode, 0, queried.stderr)
        payload = json.loads(queried.stdout)
        traces_by_address = {e["address"]: e["traces"] for e in payload["addresses"]}
        self.assertEqual(traces_by_address[hex(0x407060)], ["level-x"])
        self.assertEqual(traces_by_address[hex(0x4F9A90)], ["level-x"])
        self.assertEqual(traces_by_address[hex(0x672FD0)], [])
        self.assertTrue(payload["pass"])
        with open(index_path, encoding="utf-8") as handle:
            self.assertEqual(payload["index_receipt_set_sha256"],
                             json.load(handle)["receipt_set_sha256"])

    def test_cli_query_exit_one_on_violated_must_hit(self) -> None:
        self.tree.write("level-y", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(4),
        ])
        index_path = self.tmp / "i.json"
        self.assertEqual(
            self._run_tool("build", "--root", str(self.tmp),
                           "--out", str(index_path)).returncode, 0)
        violated = self._run_tool("query", "--index", str(index_path),
                                  "--va", "0x401008",
                                  "--expect-hit", "0x401008")
        self.assertEqual(violated.returncode, 1)
        self.assertFalse(json.loads(violated.stdout)["pass"])

    def test_cli_rva_query_matches_cli_va_query(self) -> None:
        self.tree.write("level-rva", [
            metadata_row(),
            range_row(0, 0x401000, 0x401004),
            summary_row(4),
        ])
        index_path = self.tmp / "rva-index.json"
        built = self._run_tool("build", "--root", str(self.tmp),
                               "--out", str(index_path))
        self.assertEqual(built.returncode, 0, built.stderr)
        va_result = self._run_tool("query", "--index", str(index_path),
                                   "--va", "0x401000")
        rva_result = self._run_tool("query", "--index", str(index_path),
                                    "--rva", "0x1000")
        self.assertEqual(va_result.returncode, 0, va_result.stderr)
        self.assertEqual(rva_result.returncode, 0, rva_result.stderr)
        va_entry = json.loads(va_result.stdout)["addresses"][0]
        rva_entry = json.loads(rva_result.stdout)["addresses"][0]
        self.assertEqual(va_entry, rva_entry)
        self.assertEqual(va_entry["address"], "0x401000")
        self.assertEqual(va_entry["traces"], ["level-rva"])

    def test_cli_build_exit_two_on_broken_receipt(self) -> None:
        directory = self.tmp / "level-z"
        directory.mkdir()
        with open(directory / "coverage.jsonl", "w", encoding="utf-8") as handle:
            handle.write("]\n")
        broken = self._run_tool("build", "--root", str(self.tmp))
        self.assertEqual(broken.returncode, 2)
        self.assertIn("FAIL CLOSED", broken.stderr)


if __name__ == "__main__":
    unittest.main()
