#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_tokenarchive_dispatch_reproof.py"
SPEC = importlib.util.spec_from_file_location("re_tokenarchive_dispatch_reproof", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


class TokenArchiveDispatchReproofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ready_path = ROOT / owner.EVIDENCE_RELATIVE / owner.READY_NAME
        if not cls.ready_path.is_file():
            raise AssertionError(f"required TokenArchive proof is missing: {cls.ready_path}")
        cls.saved = json.loads(cls.ready_path.read_text(encoding="utf-8"))
        cls.image = (
            ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
        ).read_bytes()
        cls.instructions = owner.read_tsv(
            ROOT / owner.EVIDENCE_RELATIVE / "ghidra-readonly/instructions.tsv"
        )
        cls.xrefs = owner.read_tsv(
            ROOT / owner.EVIDENCE_RELATIVE / "ghidra-readonly/xrefs.tsv"
        )
        cls.functions = owner.read_tsv(
            ROOT
            / "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/"
            "runs-v2/live-post-inventory/functions.tsv"
        )

    def test_exact_saved_proof_rederives(self) -> None:
        owner.validate_saved(self.saved, ROOT)
        self.assertEqual("PASS", self.saved["verdict"])
        self.assertEqual("TERMINAL_DATA", self.saved["adjudication"]["terminalState"])
        self.assertEqual(owner.PARENT_READY_SHA256, self.saved["parent"]["readySha256"])
        self.assertEqual(
            [3, 28, 125, 15],
            [row["bytes"] for row in self.saved["partition"]["partition"]],
        )
        self.assertEqual(171, sum(row["bytes"] for row in self.saved["partition"]["partition"]))

    def test_receipt_claim_and_parent_tampers_are_refused(self) -> None:
        mutations = (
            ("classification", lambda value: value["adjudication"].update(classification="CODE")),
            ("semantic promotion", lambda value: value["adjudication"].update(semanticPromotionApplied=True)),
            ("pointer target", lambda value: value["partition"]["dispatchTargets"].__setitem__(0, "0x004f5abc")),
            ("index population", lambda value: value["partition"]["indexValueCounts"].update({"6": 15})),
            ("parent", lambda value: value["parent"].update(readySha256="0" * 64)),
            ("historical claim", lambda value: value["historicalDisposition"].update(disposition="READMITTED")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                poisoned = copy.deepcopy(self.saved)
                mutate(poisoned)
                with self.assertRaisesRegex(owner.ProofError, "proof content differs"):
                    owner.validate_saved(poisoned, ROOT)

    def test_pristine_partition_poisons_are_refused(self) -> None:
        attacks = (
            ("alignmentPrefix", owner.START),
            ("pointerTable", owner.PREFIX_END),
            ("indexTable", owner.POINTER_END),
            ("alignmentSuffix", owner.INDEX_END),
            ("consumer", owner.CONSUMER_START + 2),
        )
        for expected, va in attacks:
            with self.subTest(span=expected):
                poisoned = bytearray(self.image)
                offset = owner.pe_offset(poisoned, va)
                poisoned[offset] ^= 1
                # The enclosing 171-byte digest is intentionally checked first;
                # every subspan poison must therefore fail no later than that
                # whole-residual identity gate.
                with self.assertRaisesRegex(owner.ProofError, "bytes differ"):
                    owner.validate_pristine(bytes(poisoned), require_whole_image=False)

    def test_ghidra_reference_and_instruction_poisons_are_refused(self) -> None:
        cases: list[tuple[str, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], str]] = []

        missing_pointer_ref = copy.deepcopy(self.xrefs)
        missing_pointer_ref = [
            row
            for row in missing_pointer_ref
            if not (
                row["target_addr"] == "004f5ac8"
                and row["from_addr"] == "004f584d"
                and row["ref_type"] == "DATA"
            )
        ]
        cases.append(("pointer xref", self.instructions, missing_pointer_ref, self.functions, "pointer-table reference"))

        wrong_target_owner = copy.deepcopy(self.instructions)
        target = next(
            row
            for row in wrong_target_owner
            if row["target_addr"] == "0x004f587e" and row["role"] == "TARGET"
        )
        target["function_entry"] = "0x004f5b70"
        cases.append(("target owner", wrong_target_owner, self.xrefs, self.functions, "dispatch target leaves"))

        defined_table = copy.deepcopy(self.instructions)
        missing = next(
            row
            for row in defined_table
            if row["target_addr"] == "0x004f5ae4" and row["role"] == "MISSING"
        )
        missing["role"] = "TARGET"
        cases.append(("defined table", defined_table, self.xrefs, self.functions, "unexpectedly defines"))

        wrong_consumer = copy.deepcopy(self.instructions)
        consumer = next(
            row
            for row in wrong_consumer
            if row["target_addr"] == "0x004f5847" and row["role"] == "TARGET"
        )
        consumer["operands"] = "CL, byte ptr [EAX + 0x4f5ae5]"
        cases.append(("consumer operand", wrong_consumer, self.xrefs, self.functions, "instruction differs"))

        for label, instructions, xrefs, functions, message in cases:
            with self.subTest(label=label):
                with self.assertRaisesRegex(owner.ProofError, message):
                    owner.validate_ghidra_rows(instructions, xrefs, functions)

    def test_police_reopen_is_preserved_not_laundered(self) -> None:
        history = owner.validate_police_history(ROOT)
        self.assertEqual("REFUTED_BY_POLICE_SMALL_TABLE_BULK_INDEX", history["disposition"])
        self.assertEqual(
            "EXACT_125_BYTE_INDEX_LENGTH_AND_CONSUMER_BOUND_PLUS_GHIDRA_XREFS",
            history["newProofDifference"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
