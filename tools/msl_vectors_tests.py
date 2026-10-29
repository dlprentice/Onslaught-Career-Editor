#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks for tools/msl_vectors.py: the committed C# vectors are what the generator writes, a few vectors are worked out here by hand (not
by the reference they come from), and the set covers every instruction the compiler writes and every operator it reads."""
from __future__ import annotations

import re
import unittest

import msl_compile as mc
import msl_vectors as gen
import world_resources_decode as wrd


def named(name: str) -> dict:
    return next(item for item in gen.vectors() if item["name"] == name)


class Vectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = gen.vectors()
        cls.results = {item["name"]: gen.compile_vector(item) for item in cls.items}

    def test_the_committed_c_sharp_file_is_what_the_generator_writes(self) -> None:
        self.assertEqual(gen.OUTPUT.read_text(encoding="utf-8"), gen.render())

    def test_names_are_unique_and_every_vector_says_why(self) -> None:
        names = [item["name"] for item in self.items]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(item["why"].strip() for item in self.items))
        self.assertGreaterEqual(len(names), 100)

    def test_compiling_twice_gives_the_same_answer(self) -> None:
        for item in self.items:
            self.assertEqual(gen.compile_vector(item), self.results[item["name"]], item["name"])

    def test_a_vars_block_and_a_call_worked_out_by_hand(self) -> None:
        pause = [name for name, _types in wrd.SCRIPT_NATIVES].index("Pause")
        op = {name: index for index, name in enumerate(wrd.OPCODES)}
        expected = [
            "name t",
            f"instruction 0 OP_RETURN -1", f"instruction 1 OP_PUSH 3", f"instruction 2 OP_CALL {pause | (1 << 8)}", "instruction 3 OP_REMOVE_TOP -1",
            "instruction 4 OP_RETURN -1",
        ]
        expected += [f"eventPC 0 1"] + [f"eventPC {n} -1" for n in range(1, 13)]
        expected += ["symbol 0 player 0 - 1 1", "symbol 1 init 0 - 3 1", "symbol 2 Pause 0 - 5 1", "symbol 3 const data0 1 1 5 1",
                     "nextSymbolIndex 4", "tail 0 1"]
        self.assertEqual(self.results["vars-and-a-call"]["dump"], expected)
        self.assertEqual(op["OP_RETURN"], 23)
        self.assertEqual(bytes.fromhex(mc.TRAILER), b"end_script")  # the trailer is not in the dump: every vector compiles to this one

    def test_a_float_constant_is_shown_as_its_float32_bits_and_a_string_as_its_bytes(self) -> None:
        dump = self.results["vars-initialisers"]["dump"]
        self.assertIn("symbol 1 const data0 1 4 1 1", dump)
        self.assertIn("symbol 3 const data1 2 f:3fc00000 2 1", dump)  # 1.5
        string = self.results["string-latin-1"]["dump"]
        self.assertIn("symbol 2 const data0 3 s:636166e920ff 2 1", string)  # "caf\xe9 \xff" as Latin-1 bytes

    def test_refusals_carry_the_reference_message_word_for_word(self) -> None:
        self.assertEqual(self.results["refused-0"], {"error": "line 7: 'Frobnicate' is not a function the game provides", "errorKind": "error",
                                                     "errorLine": 6, "errorPath": ""})
        self.assertEqual(self.results["missing-include"], {"error": "the included file data\\nothing.msl is not in the game folder", "errorKind": "missingInclude",
                                                           "errorLine": -1, "errorPath": "data\\nothing.msl"})
        self.assertEqual(self.results["handler-twice"]["error"], "line 4: the init handler is written twice")
        self.assertEqual(self.results["mixed-operators-0"]["error"].split(": ", 1)[1],
                         "'||' and '&&' are mixed without parentheses: the shipped scripts never leave their grouping to the game's compiler, "
                         "so put parentheses around the part you mean first")
        self.assertIn("'\\x01'", self.results["refused-21"]["error"])  # a control character is shown escaped, as Python's repr shows it
        self.assertIn("'\\xa0'", self.results["refused-20"]["error"])
        self.assertIn("'\"it\\'s\"'", self.results["refused-10"]["error"])  # a token holding both quotes: single quotes, the apostrophe escaped

    def test_the_vectors_write_every_instruction_the_compiler_can_and_use_every_operator(self) -> None:
        written = set()
        for result in self.results.values():
            for line in result.get("dump", []):
                if line.startswith("instruction "):
                    written.add(line.split()[2])
        self.assertEqual(written, set(wrd.OPCODES) - {"OP_NOP", "OP_CALLLOCAL", "OP_PUSHPC"})  # the three the compiler never writes
        text = "\n".join(item["source"] for item in self.items)
        for operator in gen.OPERATORS:
            self.assertIn(f" {operator} ", text, operator)
        kinds = {re.fullmatch(r"symbol \d+ (.+) (\d+) (\S+) (\d+) (\d+)", line).group(2)
                 for result in self.results.values() for line in result.get("dump", []) if line.startswith("symbol ")}
        self.assertEqual(kinds, {"0", "1", "2", "3", "4"})  # names, ints, floats, strings, booleans: what a source can write

    def test_both_kinds_of_answer_and_every_note_kind_are_there(self) -> None:
        self.assertGreater(sum("dump" in result for result in self.results.values()), 50)
        self.assertGreater(sum("error" in result for result in self.results.values()), 40)
        notes = {note.split(" ", 2)[1] for result in self.results.values() for note in result.get("notes", [])}
        self.assertEqual(notes, {"grouping", "handler", "declaration"})

    def test_the_depth_limits_are_on_both_sides_of_the_reference_limit(self) -> None:
        self.assertIn("dump", self.results["blocks-at-the-limit"])
        self.assertIn("nested more than 100 deep", self.results["blocks-past-the-limit"]["error"])
        self.assertIn("dump", self.results["parentheses-at-the-limit"])
        self.assertIn("nested more than", self.results["parentheses-one-past"]["error"])

    def test_the_repr_and_grouping_tables_are_the_references(self) -> None:
        text = gen.render()
        self.assertEqual(len(re.findall(r"^        \(\"[^\"]*\", \"[^\"]*\", -?[01]\),$", text, re.M)), len(gen.OPERATORS) ** 2)
        answers = {(outer, inner): mc.Compiler.binds_tighter(outer, inner) for outer in gen.OPERATORS for inner in gen.OPERATORS}
        self.assertEqual(answers[("&&", "==")], False)
        self.assertEqual(answers[("<", "+")], True)
        self.assertEqual(answers[("+", "<")], False)
        self.assertIsNone(answers[("||", "&&")])
        self.assertEqual(mc.FIXED_EVENTS, wrd.SCRIPT_EVENT_NAMES)

    def test_the_file_quotes_no_game_bytes(self) -> None:
        text = gen.OUTPUT.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("// SPDX-License-Identifier: GPL-3.0-only\n"))
        self.assertNotIn("\r", text)
        self.assertIn("#nullable enable", text)


if __name__ == "__main__":
    unittest.main()
