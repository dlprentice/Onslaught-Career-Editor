#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/game_tables_decode.py on authored files (no game bytes): the battle engine configurations as
CBattleEngineData::Load reads each version, the list order its lookups walk, and the sound effect table as
CEffect::LoadSFXFile reads its lines, with the chains it builds."""
from __future__ import annotations

import struct
import unittest
from pathlib import Path

import game_tables_decode as gt
import xap_bank_walk_tests as xap_fixtures


def cstr(text: str) -> bytes:
    return text.encode("latin-1") + b"\0"


def f32s(*values: float) -> bytes:
    return struct.pack(f"<{len(values)}f", *values)


def config(version: int = 12, *, name: str = "Standard", walker=("Walker Gun",), jet=("Jet Gun",),
           primary: str = "Main Gun", aug: str = "Main Gun Aug", explosion: str = "Big Bang",
           cockpit: str = "cockpit2b.msh", language: int = 2, life: float = 25.0, early_weapons=("j1", "j2", "w1", "w2",
                                                                                                    "w3")) -> bytes:
    """One record in CBattleEngineData::Load's order for its version."""
    out = struct.pack("<i", version) + f32s(life, 100.0, 1.0, 0.015, 30.0, 0.9, 0.5, 2.0, 3.0)
    if version < 8:
        out += f32s(7.0, 7.0, 7.0)
    if version <= 4:
        out += b"".join(cstr(w) for w in early_weapons)
    out += cstr(name)
    if version <= 4:
        out += f32s(8.0, 8.0, 8.0, 8.0)
    if version > 1:
        out += f32s(0.5)
    if version > 2:
        out += f32s(0.25)
    if version > 3:
        out += cstr(explosion)
    if version > 4:
        out += struct.pack("<i", len(walker)) + b"".join(cstr(w) for w in walker)
        out += struct.pack("<i", len(jet)) + b"".join(cstr(w) for w in jet)
        for n in range(6):
            out += struct.pack("<i", n % 2) + f32s(float(10 * n))
    if version > 5:
        out += f32s(0.3)
    if version > 6:
        out += f32s(0.6, 0.7)
    if version > 7:
        out += f32s(0.005, 0.02, 0.03)
    if version > 8:
        out += cstr(aug)
    if version > 9:
        out += cstr(primary)
    if version > 10:
        out += cstr(cockpit)
    if version > 11:
        out += struct.pack("<i", language)
    return out


def configs(*records: bytes) -> bytes:
    return struct.pack("<i", len(records)) + b"".join(records)


class ConfigurationTests(unittest.TestCase):
    def test_a_version_12_record_reads_every_field_in_the_loaders_order(self) -> None:
        record = config(walker=("A", "B"), jet=("C",))
        [c] = gt.parse_battle_engine_configurations(configs(record))["records"]
        self.assertEqual((c["version"], c["name"], c["length"], c["offset"]), (12, "Standard", len(record), 4))
        self.assertEqual((c["life"]["value"], c["groundTurnRate"]["value"], c["stealth"]["value"]), (25.0, 3.0, 0.25))
        self.assertEqual((c["walkerWeapons"], c["jetWeapons"]), (["A", "B"], ["C"]))
        self.assertEqual((c["primaryWeapon"], c["augWeapon"], c["explosion"], c["cockpit"], c["languageName"]),
                         ("Main Gun", "Main Gun Aug", "Big Bang", "cockpit2b.msh", 2))
        self.assertEqual([(s["heat"], s["value"]["value"]) for s in c["stores"]],
                         [(False, 0.0), (True, 10.0), (False, 20.0), (True, 30.0), (False, 40.0), (True, 50.0)])
        self.assertEqual((c["minAirVelocity"]["value"], c["loopEnergyCost"]["value"], c["defaulted"]),
                         (struct.unpack("<f", f32s(0.3))[0], struct.unpack("<f", f32s(0.03))[0], []))

    def test_each_record_joins_the_front_so_a_name_finds_its_last_record(self) -> None:
        parsed = gt.parse_battle_engine_configurations(configs(
            config(name="Racer"), config(name="Standard", life=1.0), config(name="Standard", life=2.0)))
        records = parsed["records"]
        self.assertEqual([r["listPosition"] for r in records], [2, 1, 0])
        self.assertEqual(gt.find_configuration(records, "Standard")["index"], 2)
        self.assertIsNone(gt.find_configuration(records, "standard"))  # strcmp: case counts
        self.assertEqual(gt.find_configuration(records, "Racer\0junk")["index"], 0)
        found, matched = gt.world_configuration(records, "Paladin")
        self.assertEqual((found["index"], matched), (2, False))  # GetConfiguration(0): the front, the last record
        self.assertEqual(gt.world_configuration(records, "Racer")[0]["index"], 0)
        self.assertEqual(gt.world_configuration([], "Racer"), (None, False))

    def test_early_versions_take_the_loaders_defaults(self) -> None:
        [c] = gt.parse_battle_engine_configurations(configs(config(4)))["records"]
        self.assertEqual((c["jetWeapons"], c["walkerWeapons"]), (["j2", "j1"], ["w3", "w2", "w1"]))  # each added at the front
        self.assertEqual((c["explosion"], c["cockpit"], c["languageName"], c["stores"]),
                         ("Big Bang", gt.BE_DEFAULT_COCKPIT, 1, None))  # version 4 reads its explosion
        self.assertEqual(c["defaulted"], ["minAirVelocity", "maxAirVelocity", "minAirEnergyCost", "maxAirEnergyCost",
                                          "cockpit", "languageName"])
        [v3] = gt.parse_battle_engine_configurations(configs(config(3)))["records"]
        self.assertEqual((v3["explosion"], v3["defaulted"][0]), (gt.BE_DEFAULT_EXPLOSION, "explosion"))
        [v1] = gt.parse_battle_engine_configurations(configs(config(1)))["records"]
        self.assertEqual((v1["shieldEfficiency"], v1["stealth"]), (None, None))
        [v9] = gt.parse_battle_engine_configurations(configs(config(9)))["records"]
        self.assertEqual((v9["augWeapon"], v9["primaryWeapon"], v9["cockpit"]), ("Main Gun Aug", None,
                                                                                gt.BE_DEFAULT_COCKPIT))
        [v10] = gt.parse_battle_engine_configurations(configs(config(10)))["records"]
        self.assertEqual((v10["primaryWeapon"], v10["cockpit"], v10["languageName"]),
                         ("Main Gun", gt.BE_DEFAULT_COCKPIT, 1))
        [v11] = gt.parse_battle_engine_configurations(configs(config(11, language=4)))["records"]
        self.assertEqual((v11["cockpit"], v11["languageName"], v11["defaulted"]), ("cockpit2b.msh", 1, ["languageName"]))
        [v7] = gt.parse_battle_engine_configurations(configs(config(7)))["records"]
        self.assertEqual((v7["maxWalkVelocity"]["value"] is not None, v7["minAirEnergyCost"]), (True, None))

    def test_a_value_that_is_not_finite_keeps_its_bits(self) -> None:
        record = bytearray(config())
        record[4:8] = struct.pack("<I", 0x7FC00001)
        [c] = gt.parse_battle_engine_configurations(configs(bytes(record)))["records"]
        self.assertEqual(c["life"], {"value": None, "bits": 0x7FC00001})

    def test_input_the_loader_would_misread_is_refused(self) -> None:
        good = configs(config())
        for broken, why in ((good + b"\0", "a byte left over"), (good[:-1], "truncated"),
                            (configs(config(name="x" * 256)), "a name the 256-byte buffer cannot hold"),
                            (struct.pack("<i", -1), "a negative count"),
                            (configs(config(walker=())).replace(struct.pack("<i", 1) + cstr("Jet Gun"),
                                                                struct.pack("<i", -1) + cstr("Jet Gun"), 1),
                             "a negative weapon count")):
            with self.assertRaises(gt.DecodeError, msg=why):
                gt.parse_battle_engine_configurations(broken)
        self.assertEqual(gt.parse_battle_engine_configurations(configs(config(name="x" * 255)))["records"][0]["name"],
                         "x" * 255)


def sfx(effects: list[tuple], *, version: int = 103, newline: str = "\n", comments: bool = True) -> bytes:
    lines = ["# authored table", str(version), str(len(effects))]
    for n, (name, sample, volume, looping, language) in enumerate(effects):
        if comments:
            lines.append(f"# effect {n}")
        lines += [name, sample, "", str(volume), "0", "5"]
        if version >= 101:
            lines.append("1" if looping else "0")
        if version >= 103:
            lines.append("1" if language else "0")
        lines.append("")
    return (newline.join(lines) + newline).encode("latin-1")


def write_tables(game: Path, *, sfx_data: bytes | None = None, config_data: bytes | None = None) -> None:
    """The configurations, the effect table and one sample bank an authored game folder needs for the gate."""
    (game / "data" / "sounds").mkdir(parents=True, exist_ok=True)
    (game / "data" / "battle engine configurations.dat").write_bytes(configs(config()) if config_data is None
                                                                       else config_data)
    (game / "data" / "sounds" / "sounds.sfx").write_bytes(
        sfx([("Engine", "Units\\engine", 30, True, False)]) if sfx_data is None else sfx_data)
    (game / "data" / "sounds" / "sounds_english_pc.xap").write_bytes(xap_fixtures.bank([("Units\\engine", 4, bytes(1))]))


class SoundEffectTests(unittest.TestCase):
    def test_each_effect_reads_its_lines_and_comment_lines_are_skipped(self) -> None:
        data = sfx([("Engine", "Units\\engine", 30, True, False), ("Hello", "Speech\\hello", 80, False, True)])
        d = gt.parse_sfx(data)
        self.assertEqual((d["version"], d["count"], d["names"], d["chained"], d["trailingBytes"]), (103, 2, 2, 0, 0))
        first, second = d["effects"]
        self.assertEqual((first["name"], first["sample"], first["lowpassSample"], first["volume"], first["falloff"],
                          first["pitchVariance"], first["looping"], first["languageDependent"]),
                         ("Engine", "Units\\engine", "", 30, 0, 5, True, False))
        self.assertEqual((second["looping"], second["languageDependent"], second["line"]), (False, True, 15))
        self.assertEqual(data[first["offset"]:first["offset"] + first["length"]].split(b"\n")[0], b"Engine")
        self.assertEqual(d["bytesRead"], len(data))

    def test_crlf_lines_read_as_lf_lines(self) -> None:
        effects = [("Engine", "Units\\engine", 30, True, False)]
        lf, crlf = gt.parse_sfx(sfx(effects)), gt.parse_sfx(sfx(effects, newline="\r\n"))
        strip = lambda d: [{k: v for k, v in e.items() if k not in ("offset", "length", "sha256")} for e in d["effects"]]
        self.assertEqual(strip(lf), strip(crlf))

    def test_a_line_is_read_as_readstring_and_readline_read_it(self) -> None:
        self.assertEqual(gt.read_line(b"abc\nd", 0), ("abc", 4, False))
        self.assertEqual(gt.read_line(b"abc\r\n", 0), ("abc", 5, False))
        self.assertEqual(gt.read_line(b"abc", 0), ("ab", 3, True))  # no LF at the end: the strip eats the "c"
        self.assertEqual(gt.read_line(b"", 0), (None, 0, True))
        long = b"x" * 300 + b"\n"
        self.assertEqual(gt.read_line(long, 0), ("x" * 254, 255, False))  # 255 bytes, no LF: one char stripped
        self.assertEqual(gt.read_line(b"x" * 255, 0)[2], False)  # exactly 255 left: the loop ends by its count
        self.assertEqual(gt.read_line(b"ab\0cd\n", 0), ("a", 6, False))  # strlen stops at the NUL

    def test_older_versions_leave_out_their_flags(self) -> None:
        old = gt.parse_sfx(sfx([("A", "s", 10, True, True)], version=100))["effects"][0]
        self.assertEqual((old["looping"], old["languageDependent"]), (False, False))
        mid = gt.parse_sfx(sfx([("A", "s", 10, True, True)], version=101))["effects"][0]
        self.assertEqual((mid["looping"], mid["languageDependent"]), (True, False))

    def test_effects_of_one_name_form_a_chain(self) -> None:
        d = gt.parse_sfx(sfx([("Shot", "a", 1, 0, 0), ("Other", "b", 1, 0, 0), ("shot", "c", 1, 0, 0),
                              ("SHOT", "d", 1, 0, 0), ("\xc9", "e", 1, 0, 0), ("\xe9", "f", 1, 0, 0)]))
        rows = [(e["head"], e["variant"], e["variants"]) for e in d["effects"]]
        self.assertEqual(rows, [(0, 0, 3), (1, 0, 1), (0, 1, 3), (0, 2, 3), (4, 0, 1), (5, 0, 1)])
        self.assertEqual((d["names"], d["chained"]), (4, 2))  # stricmp folds ASCII letters only

    def test_lookup_keys_follow_the_loader(self) -> None:
        self.assertEqual(gt.effect_lookup_key("Impact\\\\Wood"), b"impact\\wood")  # doubled backslashes made single
        self.assertEqual(gt.stricmp_key("Hud\\Beep\0tail"), b"hud\\beep")
        self.assertEqual([gt.atoi(t) for t in (" 12abc", "-3", "x", "+7", "")], [12, -3, 0, 7, 0])

    def test_input_the_loader_would_misread_is_refused(self) -> None:
        good = sfx([("Engine", "Units\\engine", 30, True, False)])
        for broken, why in ((sfx([("A", "s", 1, 0, 0)], version=104), "a newer version"),
                            (sfx([("x" * 64, "s", 1, 0, 0)]), "a name that overflows its 64-byte field"),
                            (good.rsplit(b"\n", 2)[0] + b"\n", "the file ends before the comment line"),
                            (b"103\n1\n", "nothing left for the first effect")):
            with self.assertRaises(gt.DecodeError, msg=why):
                gt.parse_sfx(broken)
        self.assertEqual(gt.parse_sfx(sfx([("x" * 63, "s", 1, 0, 0)]))["effects"][0]["name"], "x" * 63)
        self.assertEqual(gt.parse_sfx(good + b"# a trailing comment\n")["trailingBytes"], 21)


if __name__ == "__main__":
    unittest.main()
