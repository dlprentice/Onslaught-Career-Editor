#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/particle_set_walk.py on authored particle sets (no game bytes): what the walk reads, every reason it
refuses, and its tables against the rebuild's reader they were taken from, so the two cannot drift apart unnoticed."""
from __future__ import annotations

import random
import re
import unittest
from pathlib import Path

import particle_set_walk as psw

ROOT = Path(__file__).resolve().parents[1]
PARTICLES = ROOT / "rebuild" / "OnslaughtRebuild.Parity" / "Particles"
SEMANTICS = ROOT / "reverse-engineering" / "binary-analysis" / "tokenarchive-semantics-2026-08-11.md"
SEP = psw.SEPARATOR


def particle_set(*descriptors: tuple[int, str, list[str]], count: int | None = None, head: list[str] | None = None,
                 tail: str = "", newline: str = "\r\n") -> bytes:
    """A particle set file: the signature, version and count, then each descriptor's type, name, lines and separator."""
    lines = head if head is not None else [psw.SIGNATURE, "File_Version 1.000000",
                                           f"Num_Particle_Descriptors {len(descriptors) if count is None else count}"]
    for kind, name, body in descriptors:
        lines += [f"Particle_Descriptor_Type {kind}", f"Particle_Descriptor_Name {name}", *body, SEP]
    return (newline.join(lines) + newline + tail).encode("latin-1")


SPRITE = (1, "Spark", ["Radius 0.5 NONE", "Life 40", "Blend_Mode 1", r"Texture C:\dev\Onslaught2\data\textures\spark.tga",
                       "Colour_Range Fire", "Texture_Size 3"])
COLOURS = (5, "Fire", ["Start_Red 255.0 NONE", "End_Red 10", "Use_End 1", "Transition_Point 0.5"])
EMITTER = (2, "Smoke", ["Emit_Per_Turn 2.5 Wobble", "Particle_Descriptor spark", "Velocity_Randomness 0.1 NONE",
                        "Initial_Velocity_Z -0.25 NONE", "Shape NONE"])
WOBBLE = (10, "Wobble", ["Param_A 1.0 NONE", "Param_Function 2", "Gameturn_Scale 20.0"])


def walk(*descriptors, **options) -> dict:
    return psw.walk(particle_set(*descriptors, **options))


class WalkTests(unittest.TestCase):
    def test_a_set_is_read_value_by_value_to_its_end(self):
        data = particle_set(SPRITE, COLOURS, EMITTER, WOBBLE)
        result = psw.walk(data)
        self.assertEqual(result["end"], len(data))
        self.assertEqual(result["descriptors"], 4)
        self.assertEqual(result["types"], {"ColourRange": 1, "Emitter": 1, "Function": 1, "SimpleSprite": 1})
        # Radius, Colour_Range, Start_Red, End_Red, Emit_Per_Turn, Particle_Descriptor, Initial_Velocity_Z, Shape,
        # Param_A and Gameturn_Scale take one name slot each; a name resolves ignoring case, NONE and none find nothing.
        self.assertEqual(result["nameSlots"], 10)
        self.assertEqual(result["references"], {"NONE": 5, "empty": 2, "resolved": 3})
        self.assertEqual(result["linesAfterTheWalk"], 0)

    def test_the_words_after_a_direct_number_are_skipped_spans(self):
        data = particle_set(EMITTER, WOBBLE)
        result = psw.walk(data)
        start = data.index(b"Velocity_Randomness 0.1") + len(b"Velocity_Randomness 0.1")
        self.assertEqual(result["skipped"], [(start, len(b" NONE"))])

    def test_velocity_randomness_rebinds_the_stale_slot(self):
        # Its float arm leaves the integer output as the Particle_Descriptor line's slot, which the Emitter binds again.
        self.assertEqual(walk(EMITTER, WOBBLE)["slotRebinds"], 1)
        fresh = (2, "Puff", ["Velocity_Randomness 0.1"])
        self.assertEqual(walk(fresh)["slotRebinds"], 0)  # slot 0 does not exist yet; nothing is rebound
        with self.assertRaisesRegex(psw.ParticleSetError, "outside the reader's workspace"):
            walk((2, "Puff", ["Life 20000", "Velocity_Randomness 0.1"]))

    def test_lines_after_the_last_descriptor_are_left_to_the_caller(self):
        data = particle_set(COLOURS, tail="Life 3\r\n")
        result = psw.walk(data)
        self.assertEqual((result["linesAfterTheWalk"], len(data) - result["end"]), (1, len(b"Life 3\r\n")))

    def test_line_feeds_alone_read_the_same(self):
        self.assertEqual(walk(SPRITE, COLOURS, newline="\n")["nameSlots"], 4)

    def test_numbers_follow_the_reader_s_conversions(self):
        self.assertEqual([psw.scan_i(word) for word in ("40", "+5", "-3", "010", "0x1F", "0")], [40, 5, -3, 8, 31, 0])
        for word in ("08", "4x", "0x", "", "-", "2147483648", "1.0"):
            with self.subTest(word=word), self.assertRaises(psw.ParticleSetError):
                psw.scan_i(word)
        self.assertEqual([psw.scan_f(word) for word in ("1.5", ".5", "-2.", "1e3", "7")], [1.5, 0.5, -2.0, 1000.0, 7.0])
        for word in ("1e+", "nan", "inf", "+.", "1e39", "0x10", "1,5"):
            with self.subTest(word=word), self.assertRaises(psw.ParticleSetError):
                psw.scan_f(word)


class RefusalTests(unittest.TestCase):
    def refuses(self, reason: str, data: bytes) -> None:
        with self.assertRaisesRegex(psw.ParticleSetError, reason):
            psw.walk(data)

    def test_garbage_values_are_refused(self):
        self.refuses("not a whole %f number", particle_set((1, "Spark", ["Radius 0.5x NONE"])))
        self.refuses("not a whole %i number", particle_set((1, "Spark", ["Life forty"])))
        self.refuses("a missing value", particle_set((1, "Spark", ["Life"])))
        self.refuses("a missing name", particle_set((1, "Spark", ["Colour_Range "])))
        self.refuses("single spaces", particle_set((1, "Spark", ["Radius  0.5"])))

    def test_shuffled_lines_are_refused(self):
        lines = particle_set(SPRITE, COLOURS, EMITTER, WOBBLE).decode("latin-1").split("\r\n")[1:-1]
        shuffler = random.Random(20261103)
        for _ in range(20):
            shuffler.shuffle(lines)
            with self.assertRaises(psw.ParticleSetError):
                psw.walk("\r\n".join([psw.SIGNATURE] + lines + [""]).encode("latin-1"))

    def test_the_file_s_own_lines_are_where_read_data_reads_them(self):
        self.refuses("not the shipped particle set signature", particle_set(head=["ParticleSystemEd_File_", "x"]))
        self.refuses("not the shipped one", particle_set(head=[psw.SIGNATURE, "File_Version 2.0",
                                                               "Num_Particle_Descriptors 0"]))
        self.refuses("File_Version is not where", particle_set(head=[psw.SIGNATURE, "Num_Particle_Descriptors 0"]))
        self.refuses("words after its value", particle_set(head=[psw.SIGNATURE, "File_Version 1.0",
                                                                 "Num_Particle_Descriptors 0 x"]))
        self.refuses("a negative descriptor count", particle_set(head=[psw.SIGNATURE, "File_Version 1.0",
                                                                       "Num_Particle_Descriptors -1"]))
        self.refuses("Particle_Descriptor_Name is not where",
                     particle_set(head=[psw.SIGNATURE, "File_Version 1.0", "Num_Particle_Descriptors 1",
                                        "Particle_Descriptor_Type 1", "Life 3"]))

    def test_a_count_that_does_not_close_is_refused(self):
        self.refuses("ends before its last descriptor's separator", particle_set(COLOURS, count=2))
        self.refuses("ends before its last descriptor's separator",
                     particle_set(head=[psw.SIGNATURE, "File_Version 1.0", "Num_Particle_Descriptors 1",
                                        "Particle_Descriptor_Type 5", "Particle_Descriptor_Name Fire", "Use_End 1"]))

    def test_tokens_are_the_reader_s_and_the_descriptor_s(self):
        self.refuses("a token the reader does not know", particle_set((1, "Spark", ["Sparkle 1"])))
        self.refuses("a token the reader does not know", particle_set((1, "Spark", [""])))
        self.refuses("Probability_0: a value a SimpleSprite does not read", particle_set((1, "Spark", ["Probability_0 5"])))
        self.refuses("Mesh: a name a SimpleSprite does not read", particle_set((1, "Spark", ["Mesh rock.msh"])))
        # A name a descriptor does not take leaves its slot without a field: the reader would write through nothing.
        self.refuses("a name slot no field takes", particle_set((1, "Spark", ["Emit_Per_Turn 2.0 NONE"])))
        self.refuses("words after a separator", particle_set(head=[psw.SIGNATURE, "File_Version 1.0",
                                                                   "Num_Particle_Descriptors 1",
                                                                   "Particle_Descriptor_Type 3",
                                                                   "Particle_Descriptor_Name M", SEP + " x"]))

    def test_descriptors_the_factory_and_create_refuse(self):
        self.refuses("a descriptor type the factory does not make", particle_set((14, "Odd", [])))
        self.refuses("a descriptor type the factory does not make", particle_set((0, "Odd", [])))
        self.refuses("a descriptor name used twice", particle_set(COLOURS, (3, "FIRE", [])))
        self.refuses("longer than a descriptor keeps", particle_set((3, "n" * (psw.NAME_LIMIT + 1), [])))
        walk((3, "n" * psw.NAME_LIMIT, []))

    def test_loads_that_would_overrun_or_throw_are_refused(self):
        self.refuses("Time: more than a timeline's entries", particle_set((6, "T", ["Time 1"] * 11)))
        self.refuses("Particle_Descriptor: more than a timeline's entries",
                     particle_set((6, "T", ["Particle_Descriptor NONE"] * 11)))
        walk((6, "T", ["Num_Entries 10"] + ["Time 1", "Particle_Descriptor NONE", "Transmit_FoR 0"] * 10))
        self.refuses("a sprite texture size SetUV does not take", particle_set((1, "Spark", ["Texture_Size 5"])))
        self.refuses("a sprite texture size SetUV does not take", particle_set((1, "Spark", ["Texture_Size -1"])))

    def test_lines_the_reader_s_buffer_cannot_hold_are_refused(self):
        self.refuses("longer than the reader's line buffer",
                     particle_set((1, "Spark", ["Texture " + "t" * psw.LINE_BUFFER])))
        self.refuses("a control byte", particle_set((1, "Spark", ["Life\t40"])))
        self.refuses("a control byte", particle_set((1, "Spark", ["Life 40\r"])))

    def test_more_slots_than_the_workspace_are_refused(self):
        self.refuses("more name slots than the reader's workspace",
                     particle_set((1, "Spark", ["Colour_Range NONE"] * (psw.WORKSPACE + 1))))


def enum_members(source: str, name: str) -> list[str]:
    body = re.search(rf"public enum {name}\s*\{{(.*?)\}}", source, re.S).group(1)
    return [m.split("=")[0].strip() for m in body.replace("\n", " ").split(",") if m.strip()]


def switch_cases(body: str, order: list[str]) -> dict[str, str]:
    """Every Pst label of a switch body (with C# range patterns expanded in enum order) and the text of its arm."""
    arms: dict[str, str] = {}
    pieces = re.split(r"\n\s*(case\s[^:]*?:|default:)", body)
    for label, arm in zip(pieces[1::2], pieces[2::2]):
        span = re.fullmatch(r"case >= Pst\.(\w+) and <= Pst\.(\w+):", label)
        names = order[order.index(span.group(1)):order.index(span.group(2)) + 1] if span else re.findall(r"Pst\.(\w+)", label)
        for name in names:
            arms[name] = arm
    return arms


class TablesTests(unittest.TestCase):
    """The walk's tables are the rebuild's: TokenArchive.cs, ParticleSet.cs and ParticleDescriptors.cs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.archive = (PARTICLES / "TokenArchive.cs").read_text(encoding="utf-8")
        cls.descriptors = (PARTICLES / "ParticleDescriptors.cs").read_text(encoding="utf-8")
        cls.set_source = (PARTICLES / "ParticleSet.cs").read_text(encoding="utf-8")
        cls.order = [m for m in enum_members(cls.archive, "Pst") if m != "None"]
        names = re.search(r"Names =\s*\[(.*?)\];", cls.archive, re.S).group(1)
        cls.names = re.findall(r'"((?:[^"\\]|\\.)*)"', names)
        cls.token = dict(zip(cls.order, cls.names))

    def test_the_tokens_are_the_reader_s(self):
        self.assertEqual(len(self.order), len(self.names))
        self.assertEqual(set(self.names[1:]), psw.TOKENS)
        self.assertEqual(self.token["Separator"], psw.SEPARATOR)
        self.assertIn('HeaderPrefix = "ParticleSystemEd_File_"', self.archive)
        self.assertTrue(psw.SIGNATURE.startswith("ParticleSystemEd_File_"))

    def test_the_value_shapes_are_read_token_s_arms(self):
        body = re.search(r"switch \(token\)\s*\{(.*?)\n    \}\n", self.archive, re.S).group(1)
        arms = switch_cases(body, self.order)
        shapes: dict[str, set[str]] = {"int": set(), "float": set(), "string": set(), "reference": set(), "marker": set()}
        for member, arm in arms.items():
            if "ScanI" in arm:
                shapes["int"].add(self.token[member])
            elif "_names.Add(afterToken)" in arm:
                shapes["reference"].add(self.token[member])
            elif "sval = afterToken" in arm:
                shapes["string"].add(self.token[member])
            elif "ScanF" in arm:
                shapes["float"].add(self.token[member])
            elif "return true" in arm and member != "None":
                shapes["marker"].add(self.token[member])
        self.assertEqual(shapes["int"], psw.INT)
        self.assertEqual(shapes["float"], psw.FLOAT)
        self.assertEqual(shapes["string"], psw.STRING)
        self.assertEqual(shapes["reference"], psw.REFERENCE)
        self.assertEqual(shapes["marker"], {"", psw.SEPARATOR})
        listed = {self.token[member] for member in arms if member != "None"}
        self.assertEqual(set(self.names) - listed, psw.FLOAT_REFERENCE)  # the default arm
        self.assertIn("ival = _names.Count", body.split("default:")[1])

    def test_each_descriptor_type_takes_what_its_load_reads(self):
        kinds = enum_members(self.descriptors, "PdType")
        classes = re.findall(r"public sealed partial class Pd(\w+) : ParticleDescriptor\s*\{(.*?)\n\}", self.descriptors, re.S)
        self.assertEqual(len(classes), len(psw.TYPES))
        stale = set()
        for _class_name, body in classes:
            kind = re.search(r"PdType Type => PdType\.(\w+);", body).group(1)
            load = body[body.index("public override void Load"):]
            arms = switch_cases(load, self.order)
            name, takes = psw.TYPES[kinds.index(kind)]
            self.assertEqual(name, kind)
            self.assertEqual({self.token[member] for member in arms}, takes, kind)
            stale |= {self.token[m] for m, arm in arms.items() if "SetFloatRef" in arm and self.token[m] in psw.FLOAT}
            if kind == "Timeline":
                counted = {self.token[m] for m, arm in arms.items() if "++]" in arm}
                self.assertEqual(counted, set(psw.TIMELINE_COUNTED))
                self.assertIn(f"Enumerable.Range(0, {psw.TIMELINE_ENTRIES})", body)
            if kind == "SimpleSprite":
                sizes = [int(size) for size in re.findall(r"\n\s*(\d+) => \(\d+, \d+\),", body)]
                self.assertEqual(sizes, list(psw.SPRITE_TEXTURE_SIZES))
        self.assertEqual(stale, set(psw.STALE_SLOT_FLOATS))

    def test_the_limits_are_the_reader_s(self):
        self.assertIn(f"name.Length > {psw.NAME_LIMIT} ? name[..{psw.NAME_LIMIT}]", self.set_source)
        semantics = SEMANTICS.read_text(encoding="utf-8")
        self.assertIn(f"at most {psw.LINE_BUFFER} bytes", semantics)
        self.assertIn(f"{psw.WORKSPACE:,} destination pointers", semantics)


if __name__ == "__main__":
    unittest.main()
