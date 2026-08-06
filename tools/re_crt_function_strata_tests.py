#!/usr/bin/env python3
"""Focused tests for the CRT 520 function-envelope stratifier."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from capstone import Cs, CS_ARCH_X86, CS_MODE_32

TOOLS_DIRECTORY = Path(__file__).resolve().parent
if str(TOOLS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIRECTORY))

try:
    import re_crt_function_strata as strata
except ModuleNotFoundError:
    from tools import re_crt_function_strata as strata


def decode(raw: bytes, address: int = 0x1000):
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    return list(decoder.disasm(raw, address))


def target(
    entry: int,
    kind: str,
    shape: str,
    tail: int | None = None,
) -> strata.Target:
    return strata.Target(
        entry=entry,
        end=entry + 1,
        body_sha256="0" * 64,
        instruction_count=1,
        cohort="initializer",
        terminal_kind=kind,
        tail_target=tail,
        shape_key=shape,
        residual_entity_key=f"R-{entry}",
        question_id=f"Q-{entry}",
        contract_id=f"C-{entry}",
        lineage_kinds="FIXTURE",
    )


class CrtFunctionStrataTests(unittest.TestCase):
    def test_terminal_classifier_distinguishes_all_three_kinds(self) -> None:
        self.assertEqual(
            ("RET_TERMINATED", None),
            strata.classify(decode(b"\xc3"), b"\xc3", 0x1000),
        )
        thunk = b"\xe9\x0b\x00\x00\x00"
        self.assertEqual(
            ("DIRECT_JMP_THUNK", 0x1010),
            strata.classify(decode(thunk), thunk, 0x1000),
        )
        cleanup = b"\xb9\x78\x56\x34\x12\xe9\xf6\x0f\x00\x00"
        self.assertEqual(
            ("ECX_LOAD_TAIL_JUMP", 0x2000),
            strata.classify(decode(cleanup), cleanup, 0x1000),
        )

    def test_terminal_classifier_refuses_an_unmodelled_tail_jump(self) -> None:
        raw = b"\x90\xe9\xfa\x0f\x00\x00"
        with self.assertRaises(strata.StrataError):
            strata.classify(decode(raw), raw, 0x1000)

    def test_pilot_keeps_every_nonret_and_one_of_each_ret_shape(self) -> None:
        rows = []
        address = 0x1000
        for index in range(65):
            rows.append(target(address, "ECX_LOAD_TAIL_JUMP", "tail", 0x5000))
            address += 0x10
        for index in range(2):
            rows.append(target(address, "DIRECT_JMP_THUNK", "thunk", 0x6000 + index * 0x10))
            address += 0x10
        for index in range(29):
            rows.append(target(address, "RET_TERMINATED", f"ret-{index}"))
            address += 0x10
            rows.append(target(address, "RET_TERMINATED", f"ret-{index}"))
            address += 0x10
        selected = strata.select_pilot(rows, graph_minimum=())
        self.assertEqual(96, len(selected))
        self.assertTrue(all(row.entry in selected for row in rows[:67]))
        for index in range(67, len(rows), 2):
            self.assertIn(rows[index].entry, selected)
            self.assertNotIn(rows[index + 1].entry, selected)

    def test_manifest_binds_function_kind_and_thunk_target(self) -> None:
        thunk = target(0x1000, "DIRECT_JMP_THUNK", "thunk", 0x1010)
        cleanup = target(0x2000, "ECX_LOAD_TAIL_JUMP", "tail", 0x3000)
        cleanup = strata.Target(
            **{**cleanup.__dict__, "internal_branch_targets": (0x2008, 0x200C)}
        )
        data = strata.manifest_bytes([thunk, cleanup], "PILOT")
        lines = data.decode().splitlines()
        self.assertEqual(strata.envelope.MANIFEST_HEADER, lines[0])
        first = lines[1].split("\t")
        second = lines[2].split("\t")
        self.assertEqual(["true", "0x00001010"], first[6:8])
        self.assertEqual(["false", ""], second[6:8])
        self.assertEqual("0x00002008;0x0000200c", second[8])
        self.assertEqual("PILOT_DIRECT_JMP_THUNK", first[-1])
        self.assertEqual("PILOT_ECX_LOAD_TAIL_JUMP", second[-1])

    def test_tsv_parser_refuses_shifted_and_noncanonical_rows(self) -> None:
        columns = ("a", "b")
        self.assertEqual(
            [{"a": "1", "b": "2"}],
            strata.parse_tsv(b"a\tb\n1\t2\n", columns, "fixture"),
        )
        for poison in (b"a\tb\r\n1\t2\r\n", b"a\tb\n1\n", b"a\tb\n1\t2\n\n"):
            with self.subTest(poison=poison):
                with self.assertRaises(strata.StrataError):
                    strata.parse_tsv(poison, columns, "fixture")

    def test_boundary_ready_must_remain_blocked(self) -> None:
        value = {
            "schema": "bea.re.crt-text-residual-boundary-targets.v2",
            "count": 520,
            "bytes": 58157,
            "selection": {
                "batchAuthorized": False,
                "canaryAdjudication": "REFUTED_ORIGINAL_ONE_RESIDUAL_BODY",
            },
            "outputs": {
                "boundary-targets.tsv": {"sha256": strata.BOUNDARY_TSV_SHA256}
            },
        }
        strata.validate_boundary_ready(json.dumps(value).encode())
        value["selection"]["batchAuthorized"] = True
        with self.assertRaises(strata.StrataError):
            strata.validate_boundary_ready(json.dumps(value).encode())

    def test_duplicate_json_keys_are_refused(self) -> None:
        with self.assertRaises(strata.StrataError):
            strata.parse_json(b'{"a":1,"a":2}', "fixture")

    def test_expected_ready_binds_owner_dependencies_and_outputs(self) -> None:
        summary = {
            "inputs": {"x": {"sha256": "1" * 64}},
            "counts": {"fullTargets": 520},
            "selection": {"livePromotionAuthorized": False},
        }
        ready = strata.expected_ready(
            b"owner", {"dependency.py": b"dependency"}, {"out.tsv": b"x\n"}, summary
        )
        self.assertEqual(strata.READY_SCHEMA, ready["schema"])
        self.assertEqual(strata.sha256_bytes(b"owner"), ready["ownerSha256"])
        self.assertFalse(ready["selection"]["livePromotionAuthorized"])

    def test_real_bound_corpus_reproduces_exact_strata_when_present(self) -> None:
        repo = Path(strata.__file__).resolve().parents[1]
        paths = strata.default_paths(repo)
        base = repo / "local-lab/formal-function-envelope-canary-20260803-v3/inputs/base-functions.tsv"
        required = [*paths.values(), base]
        if not all(path.is_file() for path in required):
            self.skipTest("maintainer-local bound corpus is absent")
        boundary = strata.parse_tsv(
            paths["boundaryTsv"].read_bytes(), strata.BOUNDARY_COLUMNS, "boundary"
        )
        details = strata.parse_tsv(
            paths["details"].read_bytes(), strata.DETAIL_COLUMNS, "details"
        )
        targets = strata.derive_targets(
            paths["specimen"].read_bytes(),
            boundary,
            details,
            strata.base_function_info(base.read_bytes()),
        )
        self.assertEqual(520, len(targets))
        selected = strata.select_pilot(targets)
        self.assertEqual(98, len(selected))
        self.assertTrue(set(strata.GRAPH_AWARE_MINIMUM).issubset(selected))
        self.assertEqual(strata.EXPECTED_INTERNAL_BRANCH_TARGETS, {
            row.entry: row.internal_branch_targets
            for row in targets if row.internal_branch_targets
        })
        self.assertEqual(strata.EXPECTED_TRUE_THUNKS, {
            row.entry: row.tail_target for row in targets if row.expected_is_thunk
        })


if __name__ == "__main__":
    unittest.main(verbosity=2)
