#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks for tools/msl_compile.py and the judging half of tools/msl_gate.py on authored sources (no game bytes).

Each expected instruction list is worked out by hand from the shapes the shipped scripts show (the retail gate, tools/msl_gate.py, is what
compares the compiler with the game's own compiled scripts); the point here is that the compiler keeps those shapes, refuses what it
cannot place, and writes records the world-body encoder accepts."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import msl_compile as mc
import msl_gate as gate
import world_resources_decode as wrd
import world_resources_encode as wre


def compile_text(source: str, includes: dict | None = None, **options) -> dict:
    files = includes or {}

    def read(path: str) -> str:
        key = path.replace("\\", "/").lower()
        if key not in files:
            raise mc.MissingInclude(path)
        return files[key]

    return mc.compile_script("t", source, read, **options)


def listing(record: dict) -> list[str]:
    """The instructions with symbols shown by value (a constant) or name, and a call as Name/arguments (+used)."""
    symbols = record["code"]["symbols"]
    out = []
    for op, attr in record["code"]["instructions"]:
        name = mc.OPCODES[op][3:]
        if name in ("PUSH", "POP", "GETTOP"):
            symbol = symbols[attr]
            out.append(f"{name} {repr(symbol['value']) if symbol['name'].startswith('const') else symbol['name']}")
        elif name == "CALL":
            out.append(f"CALL {wrd.SCRIPT_NATIVES[attr & 0xFF][0]}/{(attr >> 8) & 0xFF}{' +used' if attr & mc.USED else ''}")
        elif name in ("JMP", "JMPFALSE", "JMPNE"):
            out.append(f"{name} {attr}")
        else:
            out.append(name)
    return out


def symbol_table(record: dict) -> list[tuple]:
    return [(s["name"], s["dataType"], s["value"], s["symbolType"]) for s in record["code"]["symbols"]]


class Shapes(unittest.TestCase):
    def test_vars_and_a_call_statement(self):
        record = compile_text("vars\n\tthing player;\nend_vars\ninit()\n{\n\tPause(1);\n}\n")
        self.assertEqual(listing(record), ["RETURN", "PUSH 1", "CALL Pause/1", "REMOVE_TOP", "RETURN"])
        self.assertEqual(record["code"]["eventPCs"], [1] + [-1] * 12)
        self.assertEqual(record["code"]["tail"], [0, 1])
        self.assertEqual(record["code"]["nextSymbolIndex"], 4)
        self.assertEqual(symbol_table(record), [("player", 0, None, 1), ("init", 0, None, 3), ("Pause", 0, None, 5), ("const data0", 1, 1, 5)])
        self.assertEqual(record["trailer"], "656e645f736372697074")

    def test_a_script_without_vars_has_a_zero_trailing_word_and_no_initialiser_block(self):
        record = compile_text("init()\n{\n\tDie();\n}\n")
        self.assertEqual(listing(record), ["CALL Die/0", "REMOVE_TOP", "RETURN"])
        self.assertEqual(record["code"]["tail"], [0, 0])
        self.assertEqual(record["code"]["eventPCs"][0], 0)

    def test_vars_initialisers_and_the_older_attributes_block(self):
        a = compile_text("vars\n\tint n = 4;\n\tfloat f = 1.5;\nend_vars\n")
        b = compile_text("attributes\n\tint n = 4;\n\tfloat f = 1.5;\nend_attributes\n")
        self.assertEqual(listing(a), ["PUSH 4", "POP n", "PUSH 1.5", "POP f", "RETURN"])
        self.assertEqual(a, b)
        self.assertEqual(symbol_table(a), [("n", 0, None, 1), ("const data0", 1, 4, 1), ("f", 0, None, 2), ("const data1", 2, 1.5, 2)])
        self.assertEqual(listing(compile_text("vars\nend_vars\n")), ["RETURN"])  # an empty block still ends in a return
        self.assertEqual(compile_text("vars\nend_vars\n")["code"]["tail"], [0, 1])

    def test_a_call_that_is_a_whole_statement_drops_its_result_and_any_other_use_keeps_it(self):
        record = compile_text("vars\n\tthing t;\nend_vars\ninit()\n{\n\tt = GetThingRef(\"x\");\n\tAttack(GetThingRef(\"y\"));\n\tif (GetHealth() < 5)\n\t{\n\t}\n}\n")
        self.assertEqual(listing(record)[1:], [
            "PUSH 'x'", "CALL GetThingRef/1 +used", "GETTOP t", "REMOVE_TOP",
            "PUSH 'y'", "CALL GetThingRef/1 +used", "CALL Attack/1", "REMOVE_TOP",
            "CALL GetHealth/0 +used", "PUSH 5", "LESS_THAN", "JMPFALSE 13", "LABEL", "RETURN"])

    def test_a_member_call_pushes_its_target_then_a_pointer_and_counts_only_its_own_arguments(self):
        record = compile_text("vars\n\tthing u;\nend_vars\ninit()\n{\n\tu.Die();\n\tGetComponent(3).Shutdown();\n\tu.IsA(2);\n}\n")
        self.assertEqual(listing(record)[1:], [
            "PUSH u", "POINTER", "CALL Die/0", "REMOVE_TOP",
            "PUSH 3", "CALL GetComponent/1 +used", "POINTER", "CALL Shutdown/0", "REMOVE_TOP",
            "PUSH u", "POINTER", "PUSH 2", "CALL IsA/1", "REMOVE_TOP", "RETURN"])

    def test_a_call_attribute_is_native_and_argument_count_with_bit_16_when_the_result_is_used(self):
        record = compile_text("init()\n{\n\tRand(Rand(1));\n}\n")
        calls = [attr for op, attr in record["code"]["instructions"] if mc.OPCODES[op] == "OP_CALL"]
        rand = [name for name, _types in wrd.SCRIPT_NATIVES].index("Rand")
        self.assertEqual(calls, [rand | (1 << 8) | 0x10000, rand | (1 << 8)])
        self.assertEqual(mc.USED, 0x10000)

    def test_an_assignment_is_an_expression_that_leaves_its_value(self):
        record = compile_text("vars\n\tbool v;\nend_vars\ninit()\n{\n\tif (v = TRUE)\n\t{\n\t}\n\tv = FALSE;\n}\n")
        self.assertEqual(listing(record)[1:], ["PUSH 1", "GETTOP v", "JMPFALSE 4", "LABEL", "PUSH 0", "GETTOP v", "REMOVE_TOP", "RETURN"])
        self.assertEqual([s[1] for s in symbol_table(record)][2:], [4, 4])  # TRUE and FALSE are boolean constants

    def test_if_else_if_else(self):
        source = ("init()\n{\n\tif (GetHealth() < 5)\n\t{\n\t\tDie();\n\t}\n\telse if (GetHealth() < 9)\n\t{\n\t\tShutdown();\n\t}\n"
                  "\telse\n\t{\n\t\tActivate();\n\t}\n}\n")
        self.assertEqual(listing(compile_text(source)), [
            "CALL GetHealth/0 +used", "PUSH 5", "LESS_THAN", "JMPFALSE 7", "CALL Die/0", "REMOVE_TOP", "JMP 19",
            "LABEL", "CALL GetHealth/0 +used", "PUSH 9", "LESS_THAN", "JMPFALSE 15", "CALL Shutdown/0", "REMOVE_TOP", "JMP 18",
            "LABEL", "CALL Activate/0", "REMOVE_TOP", "LABEL", "LABEL", "RETURN"])

    def test_while_jumps_back_to_the_condition(self):
        record = compile_text("init()\n{\n\twhile (GetHealth() > 1)\n\t{\n\t\tPause(1);\n\t}\n}\n")
        self.assertEqual(listing(record), [
            "CALL GetHealth/0 +used", "PUSH 1", "GREAT_THAN", "JMPFALSE 8", "PUSH 1", "CALL Pause/1", "REMOVE_TOP", "JMP 0", "LABEL", "RETURN"])

    def test_for_reads_its_step_before_the_body_and_runs_it_after(self):
        record = compile_text("vars\n\tint n;\nend_vars\ninit()\n{\n\tfor (n = 0; n < 3; n = n + 1)\n\t{\n\t\tPause(2);\n\t}\n}\n")
        self.assertEqual(listing(record)[1:], [
            "PUSH 0", "GETTOP n", "REMOVE_TOP",
            "PUSH n", "PUSH 3", "LESS_THAN", "JMPFALSE 17",
            "PUSH 2", "CALL Pause/1", "REMOVE_TOP",
            "PUSH n", "PUSH 1", "PLUS", "GETTOP n", "REMOVE_TOP", "JMP 4", "LABEL", "RETURN"])
        # the step's constant (1) is numbered before the body's (2)
        self.assertEqual([s[2] for s in symbol_table(record) if s[0].startswith("const")], [0, 3, 1, 2])

    def test_for_needs_all_three_parts(self):
        for header in ("for (; n < 3; n = n + 1)", "for (n = 0; ; n = n + 1)", "for (n = 0; n < 3; )"):
            with self.assertRaisesRegex(mc.CompileError, "first statement, a condition and a step"):
                compile_text("vars\n\tint n;\nend_vars\ninit()\n{\n\t" + header + "\n\t{\n\t}\n}\n")

    def test_switch_compares_each_case_and_drops_the_value_at_the_end(self):
        source = "vars\n\tint n;\nend_vars\ninit()\n{\n\tswitch (n)\n\t{\n\t\tcase 1:\n\t\t{\n\t\t\tDie();\n\t\t}\n\t\tcase 2:\n\t\t{\n\t\t\tShutdown();\n\t\t}\n\t}\n}\n"
        self.assertEqual(listing(compile_text(source))[1:], [
            "PUSH n", "PUSH 1", "CMP", "REMOVE_TOP", "JMPNE 9", "CALL Die/0", "REMOVE_TOP", "JMP 18", "LABEL",
            "PUSH 2", "CMP", "REMOVE_TOP", "JMPNE 17", "CALL Shutdown/0", "REMOVE_TOP", "JMP 18", "LABEL", "LABEL", "REMOVE_TOP", "RETURN"])

    def test_do_once_blocks_clear_a_flag_and_their_symbols_come_last(self):
        record = compile_text("init()\n{\n\tdo_once\n\t{\n\t\tDie();\n\t}\n\tdo_once\n\t{\n\t\tShutdown();\n\t}\n}\n", do_once_start=5)
        self.assertEqual(listing(record), [
            "PUSH do-once-5", "JMPFALSE 6", "PUSH do-once-6", "POP do-once-5", "CALL Die/0", "REMOVE_TOP", "LABEL",
            "PUSH do-once-7", "JMPFALSE 13", "PUSH do-once-8", "POP do-once-7", "CALL Shutdown/0", "REMOVE_TOP", "LABEL", "RETURN"])
        self.assertEqual(symbol_table(record)[3:], [("do-once-5", 4, 1, 0), ("do-once-6", 4, 0, 0), ("do-once-7", 4, 1, 0), ("do-once-8", 4, 0, 0)])
        self.assertEqual(record["code"]["nextSymbolIndex"], 7)

    def test_an_event_handler_guards_its_body_and_names_the_first_equal_string(self):
        source = "init()\n{\n\tPostEvent(\"go\");\n}\nevent(\"go\")\n{\n\tDie();\n}\nevent(\"stop\")\n{\n\tDie();\n}\n"
        record = compile_text(source)
        self.assertEqual(listing(record), [
            "PUSH 'go'", "CALL PostEvent/1", "REMOVE_TOP", "RETURN",
            "JMPFALSE 7", "CALL Die/0", "REMOVE_TOP", "LABEL", "RETURN",
            "JMPFALSE 12", "CALL Die/0", "REMOVE_TOP", "LABEL", "RETURN"])
        self.assertEqual(record["code"]["eventFunctions"], [{"entryPC": 4, "params": [2]}, {"entryPC": 9, "params": [5]}])

    def test_a_hit_handler_pops_its_parameter_and_a_misnamed_handler_is_compiled_but_never_entered(self):
        notes: list[mc.Note] = []
        record = compile_text("vars\n\tthing other;\nend_vars\nhit(other)\n{\n\tDie();\n}\ndies()\n{\n\tDie();\n}\n", notes=notes)
        self.assertEqual(listing(record), ["RETURN", "POP other", "CALL Die/0", "REMOVE_TOP", "RETURN", "CALL Die/0", "REMOVE_TOP", "RETURN"])
        self.assertEqual(record["code"]["eventPCs"], [-1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1])
        self.assertEqual([(n.kind, n.line) for n in notes], [("handler", 7)])
        self.assertIn("dies()", notes[0].text)

    def test_numbers_are_single_constants_and_floats_are_float32(self):
        record = compile_text("init()\n{\n\tPause(-2.5);\n\tPause(0.24);\n\tPause(1.5f);\n\tRand(-7);\n\tSetVulnerable(FALSE);\n}\n")
        constants = [(s[1], s[2]) for s in symbol_table(record) if s[0].startswith("const")]
        self.assertEqual(constants, [(2, -2.5), (2, 0.23999999463558197), (2, 1.5), (1, -7), (4, 0)])

    def test_integers_must_fit_32_bits_and_strings_one_byte_characters(self):
        with self.assertRaisesRegex(mc.CompileError, "does not fit in 32 bits"):
            compile_text("init()\n{\n\tRand(2147483648);\n}\n")
        self.assertEqual(symbol_table(compile_text("init()\n{\n\tRand(-2147483648);\n}\n"))[-1][2], -2147483648)
        with self.assertRaisesRegex(mc.CompileError, "single-byte characters"):
            compile_text("init()\n{\n\tPrint(\"\u2603\");\n}\n")

    def test_symbol_lines_count_newlines_only_and_headers_keep_the_numbering(self):
        source = "#include data\\a.msl\r\n#define LIMIT 3\nvars\r\n\tint n = LIMIT;\nend_vars\r\ninit()\r\n{\r\n\tPause(LIMIT);\n}\n"
        record = compile_text(source, {"data/a.msl": "#define BASE 9\n"})
        lines = {name: line for name, _t, _v, line in symbol_table(record)}
        self.assertEqual(lines["n"], 3)
        self.assertEqual(lines["init"], 5)
        self.assertEqual(lines["Pause"], 7)
        self.assertEqual([(s[2], s[3]) for s in symbol_table(record) if s[0].startswith("const")], [(3, 3), (3, 7)])

    def test_the_counters_belong_to_the_session(self):
        record = compile_text("init()\n{\n\tPause(1);\n\tPause(2);\n}\n", const_start=40)
        self.assertEqual([s[0] for s in symbol_table(record) if s[0].startswith("const")], ["const data40", "const data41"])
        self.assertEqual(mc.const_start_of(record), 40)
        self.assertEqual(mc.do_once_start_of(compile_text("init()\n{\n\tdo_once\n\t{\n\t}\n}\n", do_once_start=12)), 12)
        self.assertEqual(mc.const_start_of(compile_text("init()\n{\n}\n")), 0)

    def test_a_name_from_a_missing_header_can_be_given_by_the_caller(self):
        source = "init()\n{\n\tPause(MYSTERY);\n}\n"
        with self.assertRaisesRegex(mc.CompileError, "neither a variable of this script nor a name an included file defines"):
            compile_text(source)
        seen = []

        def resolve(name, index):
            seen.append((name, index))
            return ("int", 7)

        record = compile_text(source, resolve=resolve)
        self.assertEqual(seen, [("MYSTERY", 2)])
        self.assertEqual(symbol_table(record)[2], ("const data0", 1, 7, 2))


class Grouping(unittest.TestCase):
    VARS = "vars\n\tbool a;\n\tbool b;\n\tbool c;\n\tbool d;\n\tbool r;\nend_vars\ninit()\n{\n\t%s\n}\n"

    def compile_expression(self, text: str, notes=None) -> list[str]:
        return listing(compile_text(self.VARS % text, notes=notes))[1:-1]

    def test_and_and_equality_share_a_rank_and_group_left_to_right(self):
        notes: list[mc.Note] = []
        self.assertEqual(self.compile_expression("r = a && b == c;", notes),
                         ["PUSH a", "PUSH b", "AND", "PUSH c", "CMPB", "GETTOP r", "REMOVE_TOP"])
        self.assertEqual([(n.kind, n.text) for n in notes], [("grouping", "a && b == c is grouped ((a && b) == c)")])
        self.assertEqual(self.compile_expression("r = a == b && c == d;"),
                         ["PUSH a", "PUSH b", "CMPB", "PUSH c", "AND", "PUSH d", "CMPB", "GETTOP r", "REMOVE_TOP"])

    def test_arithmetic_binds_tighter_than_the_comparisons(self):
        self.assertEqual(self.compile_expression("r = a < b / 2;"),
                         ["PUSH a", "PUSH b", "PUSH 2", "DIVIDE", "LESS_THAN", "GETTOP r", "REMOVE_TOP"])
        self.assertEqual(self.compile_expression("r = a - 1 <= b;"),
                         ["PUSH a", "PUSH 1", "MINUS", "PUSH b", "LESS_EQ_THAN", "GETTOP r", "REMOVE_TOP"])
        self.assertEqual(self.compile_expression("r = a + 1 == b * 2;"),
                         ["PUSH a", "PUSH 1", "PLUS", "PUSH b", "PUSH 2", "MULTIPLY", "CMPB", "GETTOP r", "REMOVE_TOP"])

    def test_repeating_one_operator_groups_left_to_right(self):
        self.assertEqual(self.compile_expression("r = a || b || c;"),
                         ["PUSH a", "PUSH b", "OR", "PUSH c", "OR", "GETTOP r", "REMOVE_TOP"])
        self.assertEqual(self.compile_expression("r = a - 1 - 2;"),
                         ["PUSH a", "PUSH 1", "MINUS", "PUSH 2", "MINUS", "GETTOP r", "REMOVE_TOP"])

    def test_parentheses_say_what_the_compiler_will_not_guess(self):
        self.assertEqual(self.compile_expression("r = a || (b && c);"),
                         ["PUSH a", "PUSH b", "PUSH c", "AND", "OR", "GETTOP r", "REMOVE_TOP"])
        self.assertEqual(self.compile_expression("r = a + (b * 2);"),
                         ["PUSH a", "PUSH b", "PUSH 2", "MULTIPLY", "PLUS", "GETTOP r", "REMOVE_TOP"])

    def test_a_mix_the_shipped_scripts_do_not_settle_is_refused_naming_both_operators(self):
        for text, first, second in (("a || b && c", "||", "&&"), ("a + b * 2", "+", "*"), ("a + b - 1", "+", "-"), ("a * 2 / b", "*", "/"),
                                    ("a < b && c", "&&", "<"), ("a == b < c", "==", "<"), ("a != b && c", "!=", "&&"),
                                    ("a < b <= c", "<", "<="), ("a && b || c", "&&", "||"), ("a + 1 && b", "&&", "+")):
            with self.subTest(text):
                with self.assertRaises(mc.CompileError) as caught:
                    self.compile_expression(f"r = {text};")
                message = str(caught.exception)
                self.assertIn("mixed without parentheses", message)
                self.assertIn(repr(first), message)
                self.assertIn(repr(second), message)


class Refusals(unittest.TestCase):
    def refuse(self, body: str, message: str, vars_block: str = "vars\n\tint n;\n\tthing t;\nend_vars\n") -> None:
        with self.assertRaisesRegex(mc.CompileError, message):
            compile_text(f"{vars_block}init()\n{{\n\t{body}\n}}\n")

    def test_what_is_not_the_games_is_refused(self):
        self.refuse("Frobnicate(1);", "is not a function the game provides")
        self.refuse("Pause();", r"Pause takes 1 argument\(s\), not 0")
        self.refuse("Die(1);", r"Die takes 0 argument\(s\), not 1")
        self.refuse("m = 1;", "'m' is not a variable of this script")
        self.refuse("Pause(m);", "neither a variable of this script nor a name an included file defines")
        self.refuse("Pause(1)", "expected ';'")
        self.refuse("Pause(\"open);", "a string must end on the line it starts")
        self.refuse("Pause(1); /* x */", "no /\\* \\*/ comments")
        self.refuse("Pause(1) @;", "unexpected character '@'")
        self.refuse("n = ;", "cannot compile an expression starting ';'")

    def test_structure_errors(self):
        with self.assertRaisesRegex(mc.CompileError, "the init handler is written twice"):
            compile_text("init()\n{\n}\ninit()\n{\n}\n")
        with self.assertRaisesRegex(mc.CompileError, "unknown type 'text'"):
            compile_text("vars\n\ttext s;\nend_vars\n")
        with self.assertRaisesRegex(mc.CompileError, "an event handler is named by a string"):
            compile_text("event(go)\n{\n}\n")
        with self.assertRaisesRegex(mc.CompileError, "the source ends"):
            compile_text("init()\n{\n\tDie();\n")
        with self.assertRaisesRegex(mc.CompileError, "is not a variable of this script"):
            compile_text("hit(other)\n{\n}\n")

    def test_a_variable_declared_twice_is_one_variable_with_a_note(self):
        notes: list[mc.Note] = []
        record = compile_text("vars\n\tint n;\n\tfloat n;\nend_vars\n", notes=notes)
        self.assertEqual(len(record["code"]["symbols"]), 1)
        self.assertEqual([(n.kind, n.line) for n in notes], [("declaration", 2)])

    def test_errors_carry_the_line(self):
        with self.assertRaises(mc.CompileError) as caught:
            compile_text("init()\n{\n\tDie();\n\tPause();\n}\n")
        self.assertEqual(caught.exception.line, 3)
        self.assertTrue(str(caught.exception).startswith("line 4: "))


class Headers(unittest.TestCase):
    def test_includes_resolve_in_any_case_inside_the_game_folder_only(self):
        with tempfile.TemporaryDirectory() as folder:
            game = Path(folder, "game")
            (game / "Data" / "Inc").mkdir(parents=True)
            (game / "Data" / "Inc" / "Defs.MSL").write_text("#define LIMIT 3\n#define TWICE LIMIT\n", encoding="latin-1")
            (game.parent / "outside.msl").write_text("#define X 1\n", encoding="latin-1")
            read = mc.includes_from(game)
            record = mc.compile_script("t", "#include data\\inc\\defs.msl\ninit()\n{\n\tPause(TWICE);\n}\n", read)
            self.assertEqual([s[2] for s in symbol_table(record) if s[0].startswith("const")], [3])
            with self.assertRaises(mc.MissingInclude) as caught:
                mc.compile_script("t", "#include data\\inc\\nothing.msl\n", read)
            self.assertEqual(caught.exception.path, "data\\inc\\nothing.msl")
            with self.assertRaisesRegex(mc.CompileError, "cannot climb out of the game folder"):
                mc.compile_script("t", "#include ..\\outside.msl\n", read)
            with self.assertRaises(mc.CompileError):
                mc.compile_script("t", "#include data\\inc\n", read)  # a folder is not a header

    def test_a_define_is_replaced_by_its_tokens_and_keeps_the_line_of_its_use(self):
        record = compile_text("#define PAIR 1\ninit()\n{\n\tPause(PAIR);\n}\n")
        self.assertEqual(symbol_table(record)[-1], ("const data0", 1, 1, 3))


class Records(unittest.TestCase):
    def test_a_compiled_record_writes_and_reads_back_through_the_world_encoder(self):
        record = compile_text(
            "vars\n\tthing t;\n\tfloat h = 0.5;\nend_vars\ninit()\n{\n\tdo_once\n\t{\n\t\tPostEvent(\"x\");\n\t}\n}\nevent(\"y\")\n{\n\tt = GetThingRef(\"z\");\n}\n",
            do_once_start=3)
        writer = wre.Writer()
        wre.write_code(writer, record["code"])
        back = wre.read_code(wrd.Reader(writer.bytes()))
        self.assertEqual(mc.first_difference({"name": "t", "trailer": record["trailer"], "code": back}, record), None)

    def test_first_difference_names_the_field(self):
        a = compile_text("init()\n{\n\tPause(1);\n}\n")
        b = compile_text("init()\n{\n\tPause(2);\n}\n")
        self.assertIsNone(mc.first_difference(a, a))
        self.assertTrue(mc.first_difference(a, b).startswith("symbols[2]"))
        c = compile_text("init()\n{\n\tPause(1);\n\tPause(1);\n}\n")
        self.assertTrue(mc.first_difference(a, c).startswith("instructions"))


class Judging(unittest.TestCase):
    """tools/msl_gate.py's per-script verdicts, on an authored game folder."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.game = Path(self.folder.name)
        (self.game / "data" / "MissionScripts" / "Level123").mkdir(parents=True)
        (self.game / "data" / "MissionScripts" / "onsldef.msl").write_text("#define FIVE 5\n", encoding="latin-1")
        self.read = mc.includes_from(self.game)

    def write(self, name: str, source: str) -> str:
        (self.game / "data" / "MissionScripts" / "Level123" / f"{name}.MSL").write_text(source, encoding="latin-1", newline="")
        return source

    def shipped(self, name: str, source: str) -> dict:
        return mc.compile_script(name, source, self.read, const_start=70)

    def test_exact(self):
        source = self.write("Thing", "#include data\\MissionScripts\\onsldef.msl\ninit()\n{\n\tPause(FIVE);\n}\n")
        self.assertEqual(gate.judge(self.game, self.read, 123, self.shipped("Thing", source)), ("exact", ""))

    def test_different(self):
        self.write("Thing", "init()\n{\n\tPause(5);\n}\n")
        status, detail = gate.judge(self.game, self.read, 123, self.shipped("Thing", "init()\n{\n\tPause(6);\n}\n"))
        self.assertEqual(status, "different")
        self.assertTrue(detail.startswith("symbols[2]"), detail)

    def test_no_source(self):
        status, detail = gate.judge(self.game, self.read, 123, self.shipped("Other", "init()\n{\n}\n"))
        self.assertEqual(status, "no source")
        self.assertIn("Other.msl", detail)

    def test_a_missing_header_is_bound_from_the_shipped_constants(self):
        self.write("Thing", "#include data\\gone\\text.stf\ninit()\n{\n\tPause(MYSTERY);\n}\n")
        shipped = self.shipped("Thing", "// (gone)\ninit()\n{\n\tPause(9);\n}\n")
        self.assertEqual(gate.judge(self.game, self.read, 123, shipped), ("exact, assisted", ""))
        # the binding is only as good as the rest: a different shape still shows
        other = self.shipped("Thing", "// (gone)\ninit()\n{\n\tPause(9);\n\tPause(9);\n}\n")
        self.assertEqual(gate.judge(self.game, self.read, 123, other)[0], "different")

    def test_a_refusal_is_reported(self):
        self.write("Thing", "init()\n{\n\tPause();\n}\n")
        status, detail = gate.judge(self.game, self.read, 123, self.shipped("Thing", "init()\n{\n\tPause(1);\n}\n"))
        self.assertEqual(status, "refused")
        self.assertIn("takes 1 argument", detail)

    def test_the_pinned_stale_sources_are_named_scripts_with_a_reason(self):
        self.assertEqual(len(gate.STALE_SOURCES), 7)
        for (level, name), reason in gate.STALE_SOURCES.items():
            self.assertIsInstance(level, int)
            self.assertTrue(name and len(reason) > 20)


if __name__ == "__main__":
    unittest.main()
