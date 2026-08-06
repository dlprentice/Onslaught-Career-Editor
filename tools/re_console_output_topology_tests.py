#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused can-fail tests for :mod:`re_console_output_topology`."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/re_console_output_topology.py"
SPEC = importlib.util.spec_from_file_location("re_console_output_topology", TOOL)
assert SPEC is not None and SPEC.loader is not None
topology = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(topology)
SPECIMEN = ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
PARITY = ROOT / "local-lab/ghidra-recursive-campaign-2026-08-02/observed40-evidence"
RTTI = ROOT / "local-lab/rtti-strict-census-2026-08-03/strict-census-v2-replay-ready"
BUNDLE = ROOT / "local-lab/console-output-topology-v2-ready"


def synthetic_bundle(root: Path, *, owner: bytes | None = None, ready: bytes | None = None) -> Path:
    bundle = root / "bundle"
    (bundle / "inputs").mkdir(parents=True)
    for name in topology.INPUT_NAMES:
        (bundle / name).write_bytes(b"")
    for name in topology.OUTPUT_NAMES:
        (bundle / name).write_bytes(b"")
    (bundle / "console-output-topology-owner.py").write_bytes(TOOL.read_bytes() if owner is None else owner)
    (bundle / "READY.json").write_bytes(topology.canonical_json({}) if ready is None else ready)
    return bundle


def real_inputs() -> dict[str, bytes]:
    return topology.load_external_inputs(PARITY, RTTI)


class ConsoleOutputTopologyTests(unittest.TestCase):
    def test_rel32_candidate_scan_is_overlapping_and_target_exact(self) -> None:
        start = 0x1000
        target = 0x2000
        data = bytearray(b"\x90" * 20)
        data[2] = 0xE8
        struct.pack_into("<i", data, 3, target - (start + 2 + 5))
        data[10] = 0xE8
        struct.pack_into("<i", data, 11, 0x3000 - (start + 10 + 5))
        self.assertEqual([0x1002], topology.rel32_sites(bytes(data), start, target, 0xE8))

    def test_embedded_rel32_opcode_is_not_an_instruction_boundary(self) -> None:
        start = 0x1000
        target = 0x2000
        data = bytearray(b"\x68\x00\x00\x00\x00\xc3")
        data[1] = 0xE8
        struct.pack_into("<i", data, 2, target - (start + 1 + 5))
        self.assertEqual([0x1001], topology.rel32_sites(bytes(data), start, target, 0xE8))
        pe = {
            "sections": [{
                "name": ".text", "va": start, "virtualBytes": len(data),
                "rawBytes": len(data), "rawOffset": 0,
            }]
        }
        owner = {
            "functionAddress": "0x00001000",
            "rangeMin": "0x00001000",
            "rangeEndExclusive": "0x00001006",
        }
        with self.assertRaisesRegex(topology.TopologyError, "not a sequentially decoded transfer"):
            topology.validate_mapped_transfer(
                bytes(data), pe, 0x1001, topology.X86_INS_CALL, target, owner, {}
            )

    def test_real_derivation_reconciles_calls_jumps_graph_and_vtables(self) -> None:
        if not SPECIMEN.is_file() or not PARITY.is_dir() or not RTTI.is_dir():
            self.skipTest("local pristine or pinned graph evidence is absent")
        calls, slots, _json_bytes, result = topology.derive(SPECIMEN, real_inputs())
        self.assertEqual(380, result["counts"]["printfDirectCalls"])
        self.assertEqual(377, result["counts"]["printfMappedCalls"])
        self.assertEqual(3, result["counts"]["printfResidualCalls"])
        self.assertEqual(291, result["counts"]["foldedStubRel32Calls"])
        self.assertEqual(10, result["counts"]["foldedStubTailJumps"])
        self.assertEqual(299, result["counts"]["foldedStubMappedTransfers"])
        self.assertEqual(2, result["counts"]["foldedStubResidualTailJumps"])
        self.assertEqual(22, result["counts"]["foldedStubRttiVtableSlots"])
        self.assertEqual(323, result["counts"]["foldedStubTotalReferences"])
        self.assertEqual(684, len(calls.decode("utf-8").splitlines()))  # header + 683 rows
        self.assertEqual(23, len(slots.decode("utf-8").splitlines()))  # header + 22 rows
        self.assertEqual(1, result["bodies"]["sharedRetStubBody"]["bytes"])
        self.assertEqual(16, result["sharedRetAlignmentSpan"]["bytes"])
        self.assertEqual("0x00441823", result["coupling"]["printf"]["ringUpdateVa"])
        self.assertEqual(["0x00441767", "0x00441774"], result["sharedRetStub"]["printfSubsetSites"])
        self.assertEqual("UNRESOLVED_SHARED_RET_STUB", result["sharedRetStub"]["semanticCallee"])

    def test_body_mutation_fails_after_identity_is_separately_bypassed(self) -> None:
        if not SPECIMEN.is_file() or not PARITY.is_dir() or not RTTI.is_dir():
            self.skipTest("local pristine or pinned graph evidence is absent")
        data = bytearray(SPECIMEN.read_bytes())
        data[0x41740] ^= 1
        with self.assertRaisesRegex(topology.TopologyError, "printf body hash differs"):
            topology.derive_bytes(bytes(data), real_inputs())

    def test_graph_input_mutation_fails_closed(self) -> None:
        if not PARITY.is_dir() or not RTTI.is_dir():
            self.skipTest("pinned graph evidence is absent")
        inputs = real_inputs()
        inputs["inputs/ghidra-direct-calls.tsv"] += b"mutation"
        with self.assertRaisesRegex(topology.TopologyError, "frozen input hash differs"):
            topology.validate_frozen_inputs(inputs)

    def test_structural_attacks_need_no_local_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            owner_attack = synthetic_bundle(root / "owner", owner=TOOL.read_bytes() + b"# mutation\n")
            with self.assertRaisesRegex(topology.TopologyError, "frozen owner differs"):
                topology.verify(owner_attack, root / "unused")
            directory_attack = synthetic_bundle(root / "directory")
            (directory_attack / "extra").mkdir()
            with self.assertRaisesRegex(topology.TopologyError, "bundle members differ"):
                topology.validate_bundle_tree(directory_attack)
            input_attack = synthetic_bundle(root / "input")
            (input_attack / "inputs/extra").write_bytes(b"")
            with self.assertRaisesRegex(topology.TopologyError, "bundle input members differ"):
                topology.validate_bundle_tree(input_attack)
            canonical_attack = synthetic_bundle(root / "canonical", ready=b"{}")
            with self.assertRaisesRegex(topology.TopologyError, "not canonical JSON"):
                topology.verify(canonical_attack, root / "unused")

    @unittest.skipUnless(os.name == "nt" and hasattr(Path, "is_junction"), "Windows junctions unavailable")
    def test_cli_rejects_terminal_root_junction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = synthetic_bundle(root / "target")
            junction = root / "junction"
            created = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(target)], capture_output=True, text=True, check=False)
            if created.returncode != 0 or not junction.is_junction():
                self.skipTest("could not create junction")
            try:
                result = subprocess.run([sys.executable, "-B", str(TOOL), "verify", "--bundle", str(junction), "--specimen", str(root / "unused")], capture_output=True, text=True, check=False)
                self.assertEqual(2, result.returncode)
                self.assertIn("reparse point", result.stderr)
            finally:
                os.rmdir(junction)

    def test_build_verifies_before_atomic_publication(self) -> None:
        inputs = {name: name.encode("ascii") for name in topology.INPUT_NAMES}
        outputs = {name: name.encode("ascii") for name in topology.OUTPUT_NAMES}
        outputs["console-output-topology-owner.py"] = TOOL.read_bytes()
        result = {"counts": {}}
        original_write = Path.write_bytes

        def poisoned_write(path: Path, data: bytes) -> int:
            if path.name == "direct-transfer-sites.tsv":
                data += b"poison"
            return original_write(path, data)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            specimen = root / "specimen"
            specimen.write_bytes(b"fixture")
            out = root / "published"
            with (
                mock.patch.object(topology, "load_external_inputs", return_value=inputs),
                mock.patch.object(topology, "output_bytes", return_value=(outputs, result)),
                mock.patch.object(Path, "write_bytes", poisoned_write),
                self.assertRaisesRegex(topology.TopologyError, "derived output differs"),
            ):
                topology.build(specimen, root / "parity", root / "rtti", out)
            self.assertFalse(out.exists())
            self.assertEqual([], list(root.glob(".published-*")))

    def test_frozen_ready_replays_when_present(self) -> None:
        if not SPECIMEN.is_file() or not BUNDLE.is_dir():
            self.skipTest("local READY evidence is absent")
        result = topology.verify(BUNDLE, SPECIMEN)
        self.assertEqual(topology.STATUS, result["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
