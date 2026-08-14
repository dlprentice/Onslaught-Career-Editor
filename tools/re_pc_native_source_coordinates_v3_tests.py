#!/usr/bin/env python3
"""Focused regression and can-fail tests for the PC coordinate dataflow miner."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import struct
import sys
import tempfile
import unittest

from capstone import CS_ARCH_X86, CS_MODE_32, Cs

import re_pc_native_source_coordinates_v3 as scanner


BASE = 0x00401000
FUNCTION_VA = 0x0040F590
PATH_VA = 0x00623674
PATH = r"C:\dev\ONSLAUGHT2\BattleEngineDataManager.cpp"
ALLOCATOR = 0x005490E0
SENTINEL = 0x00662B2C
ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN_TOOL = ROOT / "tools" / "re_pc_native_source_coordinates.py"
FROZEN_COORDINATES = (
    ROOT
    / "reverse-engineering"
    / "binary-analysis"
    / "pc-native-source-coordinates-2026-08-12.tsv"
)
PROVISIONAL_COORDINATES = (
    ROOT
    / "reverse-engineering"
    / "binary-analysis"
    / "pc-native-source-coordinates-stack-stable-2026-08-13.tsv"
)
PROJECTION = (
    ROOT
    / "reverse-engineering"
    / "binary-analysis"
    / "ghidra-function-name-table-2026-08-13.tsv"
)


def push_immediate(value: int) -> bytes:
    if 0 <= value <= 0x7F:
        return b"\x6A" + bytes((value,))
    return b"\x68" + struct.pack("<I", value & 0xFFFFFFFF)


def relative_call(call_at: int, target: int = ALLOCATOR) -> bytes:
    return b"\xE8" + struct.pack("<i", target - (call_at + 5))


def finish_call(prefix: bytes, target: int = ALLOCATOR) -> bytes:
    call_at = BASE + len(prefix)
    return prefix + relative_call(call_at, target)


def make_push_sequence(
    line: int,
    gap: bytes = b"",
    *,
    path_va: int = PATH_VA,
    before_call: bytes = b"",
    consumer: int = ALLOCATOR,
) -> bytes:
    prefix = (
        push_immediate(line)
        + gap
        + push_immediate(path_va)
        + push_immediate(0x15)
        + push_immediate(9)
        + b"\xB9\xF0\x3D\x9C\x00"
        + before_call
    )
    return finish_call(prefix, consumer)


def make_register_sequence(line: int, path_va: int = PATH_VA) -> bytes:
    prefix = (
        b"\xBA" + struct.pack("<I", line)
        + b"\x52"
        + b"\xB8" + struct.pack("<I", path_va)
        + b"\x50"
        + push_immediate(0x15)
        + push_immediate(9)
        + b"\xB9\xF0\x3D\x9C\x00"
    )
    return finish_call(prefix)


def make_derived_path_sequence(line: int) -> bytes:
    prefix = (
        b"\xB8" + struct.pack("<I", PATH_VA - 4)
        + b"\x83\xC0\x04"
        + push_immediate(line)
        + b"\x50"
        + push_immediate(0x15)
        + push_immediate(9)
        + b"\xB9\xF0\x3D\x9C\x00"
    )
    return finish_call(prefix)


def make_esp_relative_sequence(line: int, path_va: int = PATH_VA) -> bytes:
    prefix = (
        b"\x83\xEC\x10"
        + b"\xC7\x44\x24\x0C" + struct.pack("<I", line)
        + b"\xC7\x44\x24\x08" + struct.pack("<I", path_va)
        + b"\xC7\x44\x24\x04" + struct.pack("<I", 0x15)
        + b"\xC7\x04\x24" + struct.pack("<I", 9)
        + b"\xB9\xF0\x3D\x9C\x00"
    )
    return finish_call(prefix)


def decode(code: bytes) -> list:
    disassembler = Cs(CS_ARCH_X86, CS_MODE_32)
    disassembler.detail = True
    return list(disassembler.disasm(code, BASE))


def scan(code: bytes, paths: dict[int, str] | None = None):
    return scanner.scan_decoded_function(
        decode(code),
        paths if paths is not None else {PATH_VA: PATH},
        FUNCTION_VA,
        "CBattleEngineData__Initialise",
    )


def header_and_first_row(path: pathlib.Path) -> bytes:
    lines = path.read_bytes().splitlines(keepends=True)
    if len(lines) < 2:
        raise AssertionError(f"expected a header and data row in {path}")
    return b"".join(lines[:2])


class SourceCoordinateScannerTests(unittest.TestCase):
    def test_adjacent_pair_remains_accepted(self) -> None:
        hits, rejections, references = scan(make_push_sequence(36))

        self.assertEqual(1, len(hits))
        self.assertEqual([], rejections)
        self.assertEqual([(BASE + 2, PATH, "push:IMMEDIATE")], references)
        self.assertEqual("ADJACENT", hits[0].pairing_mode)
        self.assertEqual("PUSH_IMMEDIATE", hits[0].argument_mode)
        self.assertEqual(0, hits[0].intervening_instructions)

    def test_known_lines_survive_stack_stable_scheduling(self) -> None:
        cases = {
            32: bytes.fromhex("8B E9"),
            35: bytes.fromhex("F2 AE F7 D1 2B F9"),
            64: bytes.fromhex("F2 AE F7 D1 2B F9"),
        }
        for line, gap in cases.items():
            with self.subTest(line=line):
                hits, rejections, _references = scan(make_push_sequence(line, gap))
                self.assertEqual([], rejections)
                self.assertEqual(1, len(hits))
                self.assertEqual(line, hits[0].source_line)
                self.assertEqual("STACK_STABLE_GAP", hits[0].pairing_mode)

    def test_register_carried_arguments_are_resolved(self) -> None:
        hits, rejections, _references = scan(make_register_sequence(64))

        self.assertEqual([], rejections)
        self.assertEqual(1, len(hits))
        self.assertEqual("REGISTER_OR_STACK_CARRIED", hits[0].argument_mode)
        self.assertEqual(BASE, hits[0].line_origin_at)
        self.assertGreater(hits[0].line_argument_at, hits[0].line_origin_at)

    def test_derived_register_path_is_resolved(self) -> None:
        hits, rejections, references = scan(make_derived_path_sequence(64))

        self.assertEqual([], rejections)
        self.assertEqual(1, len(hits))
        self.assertEqual(PATH_VA, hits[0].source_path_va)
        self.assertEqual([], references)

    def test_esp_relative_argument_plate_is_resolved(self) -> None:
        hits, rejections, _references = scan(make_esp_relative_sequence(64))

        self.assertEqual([], rejections)
        self.assertEqual(1, len(hits))
        self.assertEqual("ESP_RELATIVE", hits[0].argument_mode)
        self.assertEqual("DATAFLOW_ESP_RELATIVE", hits[0].pairing_mode)

    def test_esp_relative_stack_hole_is_rejected(self) -> None:
        prefix = (
            b"\x83\xEC\x10"
            + b"\xC7\x44\x24\x0C" + struct.pack("<I", 64)
            + b"\xC7\x44\x24\x08" + struct.pack("<I", PATH_VA)
            # [esp+4], the allocation-type slot, is deliberately unassigned.
            + b"\xC7\x04\x24" + struct.pack("<I", 9)
            + b"\xB9\xF0\x3D\x9C\x00"
        )
        hits, rejections, _references = scan(finish_call(prefix))

        self.assertEqual([], hits)
        self.assertEqual(1, len(rejections))
        self.assertIn("four exact arguments", rejections[0].reason)

    def test_surplus_push_does_not_shift_argument_plate(self) -> None:
        hits, rejections, _references = scan(
            make_push_sequence(64, before_call=push_immediate(0x1234))
        )

        self.assertEqual([], hits)
        self.assertEqual(1, len(rejections))
        self.assertIn("source-path argument", rejections[0].reason)

    def test_pointer_into_path_is_a_negative_control(self) -> None:
        hits, rejections, _references = scan(
            make_push_sequence(64, path_va=PATH_VA + 1)
        )

        self.assertEqual([], hits)
        self.assertEqual(1, len(rejections))
        self.assertIn("not a NUL-terminated", rejections[0].reason)

    def test_uninitialised_sentinel_is_a_negative_control(self) -> None:
        hits, rejections, _references = scan(
            make_push_sequence(64, path_va=SENTINEL)
        )

        self.assertEqual([], hits)
        self.assertEqual(1, len(rejections))
        self.assertIn("not a NUL-terminated", rejections[0].reason)

    def test_path_slot_overwrite_rejects_misleading_literal(self) -> None:
        overwrite = b"\xC7\x44\x24\x08" + struct.pack("<I", PATH_VA + 1)
        hits, rejections, references = scan(
            make_push_sequence(64, before_call=overwrite)
        )

        self.assertEqual([], hits)
        self.assertEqual(1, len(rejections))
        self.assertEqual(1, len(references))

    def test_cfg_predecessor_carries_line_to_joined_path_plate(self) -> None:
        code = (
            push_immediate(64)
            + b"\xEB\x00"
            + push_immediate(PATH_VA)
            + push_immediate(0x15)
            + push_immediate(9)
            + b"\xB9\xF0\x3D\x9C\x00"
        )
        hits, rejections, _references = scan(finish_call(code))

        self.assertEqual([], rejections)
        self.assertEqual(1, len(hits))
        self.assertEqual("DATAFLOW_CFG_PREDECESSOR", hits[0].pairing_mode)

    def test_cfg_join_preserves_two_exact_predecessor_lines(self) -> None:
        prefix = (
            b"\x85\xC0"          # test eax,eax
            + b"\x75\x04"       # jne alternate line
            + push_immediate(32)
            + b"\xEB\x02"       # jmp joined path push
            + push_immediate(35)
            + push_immediate(PATH_VA)
            + push_immediate(0x15)
            + push_immediate(9)
            + b"\xB9\xF0\x3D\x9C\x00"
        )
        hits, rejections, references = scan(finish_call(prefix))

        self.assertEqual([], rejections)
        self.assertEqual({32, 35}, {hit.source_line for hit in hits})
        self.assertEqual(2, len(hits))
        self.assertEqual(1, len(references))

    def test_unproved_consumer_is_not_a_candidate(self) -> None:
        hits, rejections, _references = scan(
            make_push_sequence(64, consumer=ALLOCATOR + 0x10)
        )

        self.assertEqual([], hits)
        self.assertEqual([], rejections)

    def test_path_index_handles_printable_prefix_bytes(self) -> None:
        encoded = PATH.encode("ascii")
        data = b"\x00Y?" + encoded + b"\x00tail"

        discovered = scanner.discover_source_path_offsets(data)
        legacy = [
            match.group().decode("ascii")
            for match in scanner.LEGACY_PRINTABLE_RUN_RE.finditer(data)
            if scanner.SOURCE_PATH_TEXT_RE.fullmatch(match.group().decode("ascii"))
        ]
        self.assertEqual({3: PATH}, discovered)
        self.assertEqual([], legacy)

    def test_render_and_immutable_output_check_are_deterministic(self) -> None:
        hits, _rejections, _references = scan(make_push_sequence(64))
        first = scanner.render_candidate_tsv(hits)
        second = scanner.render_candidate_tsv(hits)
        self.assertEqual(first, second)

        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory)
            payload = {"candidate-manifest.tsv": first}
            scanner.publish_or_check(output, payload, check=False)
            scanner.publish_or_check(output, payload, check=True)
            (output / "candidate-manifest.tsv").write_bytes(first + b"corrupt")
            with self.assertRaises(scanner.CoordinateScanError):
                scanner.publish_or_check(output, payload, check=True)

    def test_frozen_owner_identity_and_name_reconciliation(self) -> None:
        frozen_tool = FROZEN_TOOL.read_bytes()
        self.assertEqual(5_529, len(frozen_tool))
        self.assertEqual(
            "98d62226eedcd4c93ebb0aec52d6557007850d9d8b80cfc1210608729b4ba4c6",
            hashlib.sha256(frozen_tool).hexdigest(),
        )

        rows, _keys = scanner.load_coordinate_keys(
            FROZEN_COORDINATES,
            scanner.BASELINE_COORDINATE_PIN,
        )
        projection = {row.va: row.name for row in scanner.load_projection(PROJECTION)}
        addresses = {int(row["functionVa"], 16) for row in rows}
        stored_real_names = {
            int(row["functionVa"], 16)
            for row in rows
            if scanner.is_real_name(row["functionName"])
        }
        current_real_names = {
            address
            for address in addresses
            if scanner.is_real_name(projection[address])
        }

        self.assertEqual(1_559, len(rows))
        self.assertEqual(827, len(addresses))
        self.assertEqual(323, len(stored_real_names))
        self.assertEqual(347, len(current_real_names))

    def test_reviewed_intermediate_identity_and_anchor_rows(self) -> None:
        rows, _keys = scanner.load_coordinate_keys(
            PROVISIONAL_COORDINATES,
            scanner.PROVISIONAL_COORDINATE_PIN,
        )
        self.assertEqual(1_840, len(rows))
        self.assertEqual(993, len({row["functionVa"] for row in rows}))

        anchors = {
            row["sourceLine"]: row
            for row in rows
            if row["sourcePath"]
            == r"C:\dev\ONSLAUGHT2\BattleEngineDataManager.cpp"
            and row["functionVa"] == "0x0040F590"
            and row["sourceLine"] in {"32", "35", "64"}
        }
        expected = {
            "32": ("0x0040F594", "0x0040F598", "1", "0x0040F5A6"),
            "35": ("0x0040F5BD", "0x0040F5C5", "3", "0x0040F5E5"),
            "64": ("0x0040F781", "0x0040F789", "3", "0x0040F7A9"),
        }
        self.assertEqual(set(expected), set(anchors))
        for line, values in expected.items():
            with self.subTest(line=line):
                row = anchors[line]
                self.assertEqual(
                    values,
                    (
                        row["pushLineAt"],
                        row["pushPathAt"],
                        row["interveningInstructions"],
                        row["consumerAt"],
                    ),
                )
                self.assertEqual("STACK_STABLE_GAP", row["pairingMode"])
                self.assertEqual("0x005490E0", row["consumerVa"])
                self.assertEqual("CDXMemoryManager__Alloc", row["consumerName"])

    def test_baseline_header_plus_one_row_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            truncated = pathlib.Path(directory) / "baseline.tsv"
            truncated.write_bytes(header_and_first_row(FROZEN_COORDINATES))
            with self.assertRaises(scanner.CoordinateScanError):
                scanner.load_coordinate_keys(
                    truncated,
                    scanner.BASELINE_COORDINATE_PIN,
                )

    def test_provisional_header_plus_one_row_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            truncated = pathlib.Path(directory) / "provisional.tsv"
            truncated.write_bytes(header_and_first_row(PROVISIONAL_COORDINATES))
            with self.assertRaises(scanner.CoordinateScanError):
                scanner.load_coordinate_keys(
                    truncated,
                    scanner.PROVISIONAL_COORDINATE_PIN,
                )


def prove_can_fail() -> int:
    mutations = {}
    overwrite = b"\xC7\x44\x24\x08" + struct.pack("<I", PATH_VA + 1)
    mutations["path argument overwrite"] = not scan(
        make_push_sequence(64, before_call=overwrite)
    )[0]
    mutations["pointer into source string"] = not scan(
        make_push_sequence(64, path_va=PATH_VA + 1)
    )[0]
    mutations["unproved consumer"] = not scan(
        make_push_sequence(64, consumer=ALLOCATOR + 0x10)
    )[0]
    with tempfile.TemporaryDirectory() as directory:
        temporary = pathlib.Path(directory)
        for name, source, pin in (
            (
                "truncated frozen coordinate owner",
                FROZEN_COORDINATES,
                scanner.BASELINE_COORDINATE_PIN,
            ),
            (
                "truncated reviewed intermediate",
                PROVISIONAL_COORDINATES,
                scanner.PROVISIONAL_COORDINATE_PIN,
            ),
        ):
            truncated = temporary / f"{name.replace(' ', '-')}.tsv"
            truncated.write_bytes(header_and_first_row(source))
            try:
                scanner.load_coordinate_keys(truncated, pin)
            except scanner.CoordinateScanError:
                mutations[name] = True
            else:
                mutations[name] = False

    missed = [name for name, detected in mutations.items() if not detected]
    for name, detected in mutations.items():
        print(f"{'DETECTED' if detected else 'SURVIVED'}: {name}")
    print(f"{len(mutations) - len(missed)}/{len(mutations)} mutations detected")
    return 1 if missed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prove-can-fail", action="store_true")
    arguments, remaining = parser.parse_known_args()
    if arguments.prove_can_fail:
        return prove_can_fail()
    result = unittest.main(
        argv=[sys.argv[0], *remaining],
        exit=False,
        verbosity=2,
    ).result
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
