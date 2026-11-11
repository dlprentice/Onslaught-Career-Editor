#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""A particle set file (data\\ParticleSets\\*.par) walked as the game's reader takes it: line by line, value by value.

The grammar is onslaught-godot's reader's (rebuild/OnslaughtRebuild.Parity/Particles/ there; copies are in
tools/godot_reader_fixtures/): TokenArchive.cs gives each token's value
shape and how a line is split, ParticleSet.cs (ReadData) the file's order, and ParticleDescriptors.cs the tokens each
descriptor type's Load takes. particle_set_walk_tests.py checks the tables below against that C#, so the two cannot
drift apart unnoticed.

The reader ignores most of its own failures (reverse-engineering/binary-analysis/tokenarchive-semantics-2026-08-11.md:
a missing or malformed number keeps the previous value, an unknown line is skipped). The walk is stricter, so that a
walk that closes has read every value as written. It refuses (ParticleSetError, with a reason that holds no file text)
  - a line out of ReadData's order, a token the reader does not know, a number its descriptor's type does not read;
  - a number that is not a whole %i or %f conversion of its word, a missing value or name, and words not separated by
    single spaces where the reader counts its own offsets;
  - a descriptor type the factory does not make, a name used twice (ignoring case, as Create compares) or longer than
    the 49 characters a descriptor keeps, more than a timeline's ten entries, a sprite texture size SetUV does not take;
  - a name slot no field takes (HandleRelocation would write through an unset pointer), a slot index outside the
    reader's 10,000-entry workspace, and a line longer than the reader's 999-byte line buffer;
  - a signature or file version other than the shipped one, the only ones the reader is known to read;
  - a control byte in a line, or a file that ends before its last descriptor's separator.
The words after a direct number, which the reader never looks at, come back as skipped spans. The walk ends after the
last descriptor's separator line; the reader never reaches what follows, so the caller decides what it is.
"""
from __future__ import annotations

import collections
import math
import re
import struct

SIGNATURE = "ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd"  # reverse-engineering/asset-formats/particle-par.md
FILE_VERSION = 1.0
SEPARATOR = "*" * 65
LINE_BUFFER = 999  # ReadNextToken reads at most this many bytes of a line
NAME_LIMIT = 49  # CParticleSet::Create keeps this many characters of a descriptor's name
WORKSPACE = 10_000  # the deferred-reference workspace's slots
TIMELINE_ENTRIES = 10

# Value shapes, in TokenArchive.ReadToken's arms. Every other token but the two markers is a float with an optional
# function name after it (the default arm).
INT = frozenset((
    "Num_Particle_Descriptors", "Particle_Descriptor_Type", "Gravity", "Bounce", "Fade_Col", "Blend_Mode",
    "Texture_Number", "Axis_Aligned", "Anim_Type", "End_Frame", "Texture_Size", "Random_Start_Frame", "2D", "Life",
    "Transmit_Life", "Transmit_FoR", "Interpolated_Emission", "Pass_Num_Particles", "Probability_0", "Probability_1",
    "Probability_2", "Probability_3", "Use_End", "Use_Transition", "Num_Entries", "Time", "Type", "Ring_Axis",
    "Hemisphere", "Num_Particles", "Hollow", "Num_Points", "Taper_Start", "Width_With_Life", "Fade_Point",
    "Use_Segment_Length", "Manual_Wiggle_Enabled", "Flat", "Param_Function", "Clip", "Value_Type", "Offset_Gameturn",
    "Auto_Centre", "Cylinder_NumPtsAxial", "Cylinder_NumPtsRadial", "Sphere_NumPtsAx", "Sphere_NumPtsRad"))
FLOAT = frozenset((
    "File_Version", "Final_Radius", "Anim_Speed", "Velocity_Damp", "Life_Pct", "Velocity_Randomness",
    "Transition_Point", "RandomSX", "RandomSY", "RandomSZ", "Width", "Start_Width", "Wiggle_Factor", "Disperse_Rate",
    "SegmentLength", "Yaw", "Pitch", "Roll", "Angular_Momentum"))
STRING = frozenset(("Particle_Descriptor_Name", "Texture", "Mesh"))
REFERENCE = frozenset((
    "Modifier", "Colour_Range", "Particle_Descriptor", "Shape", "Mover", "Particle_Descriptor_0", "Particle_Descriptor_1",
    "Particle_Descriptor_2", "Particle_Descriptor_3", "Yaw_Function", "Pitch_Function", "Roll_Function",
    "Impact_Spawnee", "Initial", "Death", "Colour_Range2"))
FLOAT_REFERENCE = frozenset((
    "Radius", "Length", "Emit_Per_Turn", "Initial_Velocity_X", "Initial_Velocity_Y", "Initial_Velocity_Z",
    "Transmit_Velocity", "Outward_Velocity", "Start_Red", "Start_Green", "Start_Blue", "End_Red", "End_Green",
    "End_Blue", "Transition_Red", "Transition_Green", "Transition_Blue", "Wiggle_Length", "Yaw_Length", "GravityPC",
    "Param_A", "Param_B", "Param_C", "Param_D", "Gameturn_Scale", "Tile_U", "Tile_V", "Scroll_U", "Scroll_V",
    "Cylinder_Radius", "Cylinder_Radius2", "Cylinder_Length", "Sphere_RadiusTime", "Sphere_Latitude_Start",
    "Sphere_Latitude_End", "Sphere_Longitude_Start", "Sphere_Longitude_End"))
TOKENS = INT | FLOAT | STRING | REFERENCE | FLOAT_REFERENCE | {SEPARATOR}

# What each descriptor type's Load takes (EParticleDescriptorType order). A float the Emitter's Load passes to
# SetFloatRef (Velocity_Randomness) binds the stale slot the reader's integer output still holds.
TYPES = {
    1: ("SimpleSprite", frozenset((
        "Radius", "Final_Radius", "Life", "Life_Pct", "Gravity", "Bounce", "Fade_Col", "Texture", "Modifier",
        "Colour_Range", "Blend_Mode", "Texture_Number", "Texture_Size", "Axis_Aligned", "Velocity_Damp", "Length", "2D",
        "Anim_Type", "End_Frame", "Anim_Speed", "Random_Start_Frame"))),
    2: ("Emitter", frozenset((
        "Emit_Per_Turn", "Life", "Particle_Descriptor", "Initial_Velocity_X", "Initial_Velocity_Y", "Initial_Velocity_Z",
        "Velocity_Randomness", "Transmit_Life", "Transmit_FoR", "Transmit_Velocity", "Interpolated_Emission", "Shape",
        "Pass_Num_Particles", "Outward_Velocity", "Mover"))),
    3: ("Modifier", frozenset()),
    4: ("Selector", frozenset((
        "Particle_Descriptor_0", "Particle_Descriptor_1", "Particle_Descriptor_2", "Particle_Descriptor_3",
        "Probability_0", "Probability_1", "Probability_2", "Probability_3"))),
    5: ("ColourRange", frozenset((
        "Start_Red", "Start_Green", "Start_Blue", "End_Red", "End_Green", "End_Blue", "Transition_Red",
        "Transition_Green", "Transition_Blue", "Use_End", "Use_Transition", "Transition_Point"))),
    6: ("Timeline", frozenset(("Num_Entries", "Particle_Descriptor", "Time", "Transmit_FoR"))),
    7: ("Shape", frozenset((
        "Type", "Ring_Axis", "Hemisphere", "Num_Particles", "Radius", "Hollow", "RandomSX", "RandomSY", "RandomSZ"))),
    8: ("Trail", frozenset((
        "Texture", "Blend_Mode", "Texture_Number", "Width", "Start_Width", "Num_Points", "Colour_Range", "Wiggle_Factor",
        "Disperse_Rate", "Gravity", "Life", "Taper_Start", "Width_With_Life", "Type", "Impact_Spawnee", "Transmit_FoR",
        "Fade_Point", "Use_Segment_Length", "SegmentLength", "Manual_Wiggle_Enabled", "Wiggle_Length", "Yaw_Length",
        "Flat"))),
    9: ("Mover", frozenset((
        "GravityPC", "Yaw", "Pitch", "Roll", "Yaw_Function", "Pitch_Function", "Roll_Function"))),
    10: ("Function", frozenset((
        "Param_A", "Param_B", "Param_C", "Param_D", "Param_Function", "Clip", "Value_Type", "Gameturn_Scale",
        "Offset_Gameturn"))),
    11: ("Mesh", frozenset((
        "Life", "Gravity", "Bounce", "Angular_Momentum", "Transmit_FoR", "Auto_Centre", "Mesh", "Impact_Spawnee"))),
    12: ("FoR", frozenset(("Death", "Initial", "Mover"))),
    13: ("PMesh", frozenset((
        "Type", "Life", "Blend_Mode", "Texture", "Colour_Range", "Colour_Range2", "Tile_U", "Tile_V", "Scroll_U",
        "Scroll_V", "Cylinder_NumPtsAxial", "Cylinder_NumPtsRadial", "Cylinder_Radius", "Cylinder_Radius2",
        "Cylinder_Length", "Sphere_NumPtsAx", "Sphere_NumPtsRad", "Sphere_RadiusTime", "Sphere_Latitude_Start",
        "Sphere_Latitude_End", "Sphere_Longitude_Start", "Sphere_Longitude_End"))),
}
STALE_SLOT_FLOATS = frozenset(("Velocity_Randomness",))
TIMELINE_COUNTED = ("Particle_Descriptor", "Time", "Transmit_FoR")
SPRITE_TEXTURE_SIZES = range(5)  # SetUV's tile counts 16 >> size

_FLOAT_WORD = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
_INT32 = range(-2 ** 31, 2 ** 31)


class ParticleSetError(ValueError):
    """The file does not hold the particle set grammar as the reader takes it; the reason holds no file text."""


def scan_i(word: str) -> int:
    """sscanf's %i over a whole word: decimal, 0x hexadecimal or 0 octal, with a sign; refused unless every character
    belongs to the conversion and the value fits an int."""
    body = word[1:] if word[:1] in ("+", "-") else word
    if body[:2] in ("0x", "0X"):
        digits, radix = body[2:], 16
    elif body[:1] == "0" and len(body) > 1:
        digits, radix = body[1:], 8
    else:
        digits, radix = body, 10
    if not digits or any(char not in _DIGITS[radix] for char in digits):
        raise ParticleSetError("a value that is not a whole %i number")
    value = int(digits, radix) * (-1 if word[:1] == "-" else 1)
    if value not in _INT32:
        raise ParticleSetError("a whole number outside an int")
    return value


_DIGITS = {8: frozenset("01234567"), 10: frozenset("0123456789"), 16: frozenset("0123456789abcdefABCDEF")}


def scan_f(word: str) -> float:
    """sscanf's %f over a whole word, as a 32-bit float: refused unless the word is all one plain decimal that stays
    finite."""
    if not _FLOAT_WORD.fullmatch(word):
        raise ParticleSetError("a value that is not a whole %f number")
    try:
        value = struct.unpack("<f", struct.pack("<f", float(word)))[0]
    except OverflowError:
        value = math.inf
    if not math.isfinite(value):
        raise ParticleSetError("a decimal outside a float")
    return value


def fold(name: str) -> str:
    """The C runtime's _stricmp folding: A..Z to lower case, nothing else."""
    return name.translate(_FOLD)


_FOLD = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def lines_of(data: bytes) -> list[tuple[int, int, str]]:
    """(start, end including the terminator, text) for each line. ReadLine drops the line feed and keeps a carriage
    return, which counts against the line buffer; the text, as the rebuild reads it, has neither."""
    out, position = [], 0
    while position < len(data):
        stop = data.find(b"\n", position)
        end = len(data) if stop < 0 else stop + 1
        raw = data[position:end - 1] if stop >= 0 else data[position:end]
        if len(raw) > LINE_BUFFER:
            raise ParticleSetError("a line longer than the reader's line buffer")
        body = raw[:-1] if raw.endswith(b"\r") else raw
        if any(value < 32 or value == 127 for value in body):
            raise ParticleSetError("a control byte in a line")
        out.append((position, end, body.decode("latin-1")))
        position = end
    return out


class _Line:
    """One line as ReadToken splits it: the token, then the value or name the token's shape takes."""

    def __init__(self, start: int, text: str):
        self.start, self.text = start, text
        self.token, self.space, self.after = text.partition(" ")

    def first_word(self) -> str:
        """The reader's second word, which must follow the token after one space."""
        if not self.space or not self.after.strip(" "):
            raise ParticleSetError(f"{self.token}: a missing value")
        if self.after.startswith(" "):
            raise ParticleSetError(f"{self.token}: words not separated by single spaces")
        return self.after.partition(" ")[0]

    def number(self) -> tuple[str, int | None]:
        """A direct number's word and where the words the reader never reads begin (None when there are none)."""
        word = self.first_word()
        if len(self.after) == len(word):
            return word, None
        return word, self.start + len(self.token) + 1 + len(word)

    def sole_number(self) -> str:
        word, skipped_at = self.number()
        if skipped_at is not None:
            raise ParticleSetError(f"{self.token}: words after its value")
        return word

    def name(self) -> str:
        """Everything after the token and one space (the reader's own offset); refused when the reader would see no
        second word."""
        if not self.space or not self.after.strip(" "):
            raise ParticleSetError(f"{self.token}: a missing name")
        return self.after

    def float_and_name(self) -> tuple[str, str]:
        """The default arm: a float, then an optional name after one more space (the reader's own offsets)."""
        word = self.first_word()
        return word, self.after[len(word) + 1:]


def walk(data: bytes) -> dict:
    """Walk one particle set file; returns where the walk ends, the skipped spans and counts (no names or values)."""
    lines = lines_of(data)
    cursor = 0

    def take(expected: str | None = None) -> _Line:
        nonlocal cursor
        if cursor >= len(lines):
            raise ParticleSetError("the file ends before its last descriptor's separator")
        start, _end, text = lines[cursor]
        cursor += 1
        line = _Line(start, text)
        if expected is not None and line.token != expected:
            raise ParticleSetError(f"{expected} is not where ReadData reads it")
        return line

    header = take()
    if header.text != SIGNATURE:
        raise ParticleSetError("the first line is not the shipped particle set signature")
    if scan_f(take("File_Version").sole_number()) != FILE_VERSION:
        raise ParticleSetError("the file version is not the shipped one")
    count = scan_i(take("Num_Particle_Descriptors").sole_number())
    if count < 0:
        raise ParticleSetError("a negative descriptor count")

    names: list[str] = []  # the archive's name slots, in reading order
    fixups: dict[int, str] = {}  # slot -> the field that takes it (a later bind replaces an earlier one)
    descriptors: dict[str, int] = {}
    skipped: list[tuple[int, int]] = []
    types: collections.Counter = collections.Counter()
    rebinds = 0
    for number in range(count):
        kind = scan_i(take("Particle_Descriptor_Type").sole_number())
        if kind not in TYPES:
            raise ParticleSetError("a descriptor type the factory does not make")
        name = take("Particle_Descriptor_Name").name()
        if len(name) > NAME_LIMIT:
            raise ParticleSetError("a descriptor name longer than a descriptor keeps")
        if fold(name) in descriptors:
            raise ParticleSetError("a descriptor name used twice")
        descriptors[fold(name)] = number
        type_name, takes = TYPES[kind]
        types[type_name] += 1
        ival = 0  # ReadUntilSeparator's integer output, kept across the Load's lines
        timeline = collections.Counter()
        texture_size = 2
        while True:
            line = take()
            token = line.token
            if token == SEPARATOR:
                if line.text != SEPARATOR:
                    raise ParticleSetError("words after a separator")
                break
            if token not in TOKENS:
                raise ParticleSetError("a token the reader does not know")
            if token in INT or token in FLOAT:
                word, skipped_at = line.number()
                if token in INT:
                    ival = value = scan_i(word)
                else:
                    value = scan_f(word)
                if skipped_at is not None:
                    skipped.append((skipped_at, len(line.text) - (skipped_at - line.start)))
                if token not in takes:
                    raise ParticleSetError(f"{token}: a value a {type_name} does not read")
                if token in STALE_SLOT_FLOATS:
                    if ival not in range(WORKSPACE):
                        raise ParticleSetError(f"{token}: binds a slot outside the reader's workspace")
                    rebinds += ival in fixups
                    fixups[ival] = f"{type_name}.{token}"
                if type_name == "Timeline" and token in TIMELINE_COUNTED:
                    timeline[token] += 1
                    if timeline[token] > TIMELINE_ENTRIES:
                        raise ParticleSetError(f"{token}: more than a timeline's entries")
                if type_name == "SimpleSprite" and token == "Texture_Size":
                    texture_size = value
            elif token in STRING:
                line.name()
                if token not in takes:
                    raise ParticleSetError(f"{token}: a name a {type_name} does not read")
            else:
                if token in REFERENCE:
                    names.append(line.name())
                else:
                    word, rest = line.float_and_name()
                    scan_f(word)
                    names.append(rest)
                ival = len(names) - 1
                if len(names) > WORKSPACE:
                    raise ParticleSetError("more name slots than the reader's workspace")
                if token in takes:
                    fixups[ival] = f"{type_name}.{token}"
                    if type_name == "Timeline" and token in TIMELINE_COUNTED:
                        timeline[token] += 1
                        if timeline[token] > TIMELINE_ENTRIES:
                            raise ParticleSetError(f"{token}: more than a timeline's entries")
        if type_name == "SimpleSprite" and texture_size not in SPRITE_TEXTURE_SIZES:
            raise ParticleSetError("a sprite texture size SetUV does not take")
    for slot in range(len(names)):
        if slot not in fixups:
            raise ParticleSetError("a name slot no field takes (the reader would write through an unset pointer)")
    outcome: collections.Counter = collections.Counter()
    for name in names:
        outcome["empty" if not name else "resolved" if fold(name) in descriptors else
                "NONE" if name == "NONE" else "unmatched"] += 1
    end = lines[cursor - 1][1]
    return {"end": end, "skipped": skipped, "lines": cursor, "descriptors": count, "types": dict(sorted(types.items())),
            "nameSlots": len(names), "slotRebinds": rebinds, "references": dict(sorted(outcome.items())),
            "linesAfterTheWalk": len(lines) - cursor}
