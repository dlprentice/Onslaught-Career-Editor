#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The battle engine configurations and the sound effect table, decoded in their loaders' order (no I/O, no retail
bytes kept). Each decoder follows the game function it names (the public decompilation, onslaught-decomp src/, cited
by function and never quoted) and refuses input that function would misread or that it does not consume exactly.

- data/battle engine configurations.dat: UPhysicsManager::Reload opens it and UBattleEngineDataManager::Load reads a
  record count, then each record with CBattleEngineData::Load (every field by the record's version; the walker and
  jet weapon lists are appended in file order from version 5 on). Each record joins the front of the manager's list,
  so a name finds the last record of that name (GetConfiguration's strcmp from the front) and index 0 is the last
  record: the configuration UBattleEngineConfigurations::GetConfiguration falls back on for a world header's name that
  matches nothing.
- data/sounds/sounds.sfx: CSoundManager::Init has CEffect::LoadSFXFile read it as text lines (CDXMemBuffer::ReadString:
  up to 255 bytes through a LF, a CR before it dropped; CEffect::ReadLine skips lines starting with '#' and drops each
  line's last character, the LF). A version and an effect count, then per effect its name, sample, low-pass sample,
  volume, falloff and pitch variance, a looping flag (version 101 on), a language flag (version 103 on) and a comment
  line. Each effect joins the front of CEffect's list; one whose name (stricmp) equals an effect already on the list is
  appended to that effect's chain instead, so the list keeps one effect per name and CSoundManager::PlayEffect picks
  one of a chain at random.

Pure functions over bytes; tools/content_catalog.py joins their results to the rest of the catalogue.
"""
from __future__ import annotations

import hashlib
import math
import struct

DECOMP = "onslaught-decomp"


def cite(source: str, function: str, va: str) -> str:
    return f"{DECOMP} src/{source} {function} @{va}"


L_BE_RELOAD = cite("WorldPhysicsManager.cpp", "UPhysicsManager::Reload (opens data\\battle engine configurations.dat)",
                   "0x00510800")
L_BE_LOAD = cite("BattleEngineDataManager.cpp", "CBattleEngineData::Load", "0x0040f980")
L_BE_MANAGER = cite("BattleEngineDataManager.h", "UBattleEngineDataManager::Load and GetConfiguration (each record "
                    "joins the front of sData; a name finds the first strcmp match from the front)", "inline")
L_BE_WORLD = cite("BattleEngineConfigurations.cpp", "UBattleEngineConfigurations::Load and GetConfiguration (a world "
                  "header's names; one that matches nothing falls back on GetConfiguration(0))", "0x0040f180, 0x0040f2f0")
L_BE_DESCRIPTION = cite("FEPBEConfig.cpp", "CFEPBEConfig::GetConfigDescription", "0x0044eb30")
L_BE_COCKPIT = cite("Cockpit.cpp", "CCockpit::CCockpit (a CRTMesh named by the configuration's cockpit)", "0x004244b0")
L_BE_WEAPONS = (cite("BattleEngineWalkerPart.cpp", "the walker part's weapon set-up (UPhysicsManager::SpawnWeapon by "
                     "name: the walker weapons, the primary and the aug weapon)", "n/a") + "; "
                + cite("BattleEngineJetPart.cpp", "the jet part's weapon set-up (the jet weapons)", "n/a"))
L_BE_EXPLOSION = cite("BattleEngine.cpp", "CBattleEngine::Explode (UPhysicsManager::SpawnExplosion and GetExplosion by "
                      "name)", "0x0040e098")
L_SFX_INIT = cite("SoundManager.cpp", "CSoundManager::Init (data\\sounds\\sounds.sfx)", "0x004e00d0")
L_SFX_LOAD = cite("SoundManager.cpp", "CEffect::LoadSFXFile", "0x004e2530")
L_SFX_LINE = cite("DXMemBuffer.cpp", "CDXMemBuffer::ReadString", "0x00548820") + "; CEffect::ReadLine"
L_SFX_FIND = cite("SoundManager.cpp", "CEffect::GetEffectByName (stricmp over the list, doubled backslashes in the "
                  "asked name made single)", "0x004e2a90")
L_SFX_PLAY = cite("SoundManager.cpp", "CSoundManager::PlayEffect (a random effect of the chain plays its sample with "
                  "PlayNamedSample)", "0x004e1940")
L_SFX_PRECACHE = cite("SoundManager.cpp", "CEffect::PrecacheAll (the sample and the low-pass sample)", "n/a")
L_SAMPLE = cite("SoundManager.cpp", "CSoundManager::GetSample (stricmp over the samples the language's XAP bank "
                "loaded)", "0x004e0a00")

BE_STORES = 6                                   # kBattleEngineStores (BattleEngineDataManager.h)
BE_BUFFER = 256                                 # CBattleEngineData::Load's char temp[256]
BE_LEADING = ("life", "energy", "groundEnergyIncrease", "maxAirEnergyCost", "minTransformEnergy", "maxAirVelocity",
              "groundVelocity", "airTurnRate", "groundTurnRate")
# CFEPBEConfig::GetConfigDescription: the record's mLanguageName (1..5) chooses the description's text id.
BE_DESCRIPTION_TEXT = {1: 0x97D47D6B, 2: 0xE3FCBF7C, 3: 0x3025018D, 4: 0x7C4D439E, 5: 0xC87585AF}
BE_DEFAULT_EXPLOSION = "Animated Explosion Emitter 2"  # CBattleEngineData::Load before version 4
BE_DEFAULT_COCKPIT = "cockpit2.msh"                    # before version 11
SFX_VERSION_MAX = 103                           # LoadSFXFile asserts the version is at most 103
SFX_FIELD = 64                                  # CEffect::mName, mSample, mLowpassSample: char[64]
SFX_READ = 255                                  # ReadString(line, 256) reads at most 255 bytes


class DecodeError(ValueError):
    pass


def number(raw: bytes) -> dict:
    """A stored float32: its value when finite (else null) and its bits."""
    value = struct.unpack("<f", raw)[0]
    return {"value": value if math.isfinite(value) else None, "bits": struct.unpack("<I", raw)[0]}


class Reader:
    def __init__(self, data: bytes):
        self.data, self.pos = data, 0

    def take(self, n: int) -> bytes:
        if n < 0 or self.pos + n > len(self.data):
            raise DecodeError(f"read of {n} bytes at {self.pos} passes the end ({len(self.data)})")
        out = self.data[self.pos:self.pos + n]
        self.pos += n
        return out

    def i32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]

    def f32(self) -> dict:
        return number(self.take(4))

    def cstring(self, what: str) -> str:
        """The do/while byte loop into temp[256]: up to and including a NUL that must come within the buffer."""
        end = self.data.find(b"\0", self.pos, min(len(self.data), self.pos + BE_BUFFER))
        if end < 0:
            raise DecodeError(f"{what} at {self.pos} has no NUL within the loader's {BE_BUFFER}-byte buffer")
        text = self.data[self.pos:end].decode("latin-1")
        self.pos = end + 1
        return text


def parse_battle_engine_configurations(data: bytes) -> dict:
    """UBattleEngineDataManager::Load: a record count, then CBattleEngineData::Load per record, in the loader's order.
    Values default as the loader sets them when the record's version leaves them out (marked in defaulted)."""
    r = Reader(data)
    count = r.i32()
    if not 0 <= count <= 1 << 16:
        raise DecodeError(f"implausible configuration count {count}")
    records = []
    for index in range(count):
        at = r.pos
        version = r.i32()
        rec: dict = {"index": index, "offset": at, "version": version, "defaulted": []}
        for field in BE_LEADING:
            rec[field] = r.f32()
        if version < 8:
            r.take(12)  # three floats it no longer uses
        walker, jet = [], []
        if version <= 4:
            # two jet weapons, then three walker weapons, each added at the front of its list
            for target in (jet, jet, walker, walker, walker):
                target.insert(0, r.cstring("an early-version weapon name"))
        rec["name"] = r.cstring("the configuration name")
        if version <= 4:
            r.take(16)  # four floats it no longer uses
        rec["shieldEfficiency"] = r.f32() if version > 1 else None
        rec["stealth"] = r.f32() if version > 2 else None
        if version > 3:
            rec["explosion"] = r.cstring("the explosion name")
        else:
            rec["explosion"] = BE_DEFAULT_EXPLOSION
            rec["defaulted"].append("explosion")
        stores = None
        if version > 4:
            for target in (walker, jet):
                n = r.i32()
                if not 0 <= n <= 1 << 12:
                    raise DecodeError(f"configuration {index} has an implausible weapon count {n}")
                for _ in range(n):
                    target.append(r.cstring("a weapon name"))
            stores = []
            for _ in range(BE_STORES):
                heat = r.i32()
                stores.append({"heat": heat != 0, "heatWord": heat, "value": r.f32()})
        rec["walkerWeapons"], rec["jetWeapons"], rec["stores"] = walker, jet, stores
        rec["minAirVelocity"] = r.f32() if version > 5 else None
        rec["maxWalkVelocity"], rec["walkFriction"] = (r.f32(), r.f32()) if version > 6 else (None, None)
        if version > 7:
            rec["minAirEnergyCost"], rec["rollEnergyCost"], rec["loopEnergyCost"] = r.f32(), r.f32(), r.f32()
        else:
            # before version 8 the loader sets these (and overwrites the stored maximum air velocity and energy cost)
            rec["minAirEnergyCost"], rec["rollEnergyCost"], rec["loopEnergyCost"] = None, None, None
            rec["defaulted"] += ["minAirVelocity", "maxAirVelocity", "minAirEnergyCost", "maxAirEnergyCost"]
        rec["augWeapon"] = r.cstring("the aug weapon name") if version > 8 else None
        rec["primaryWeapon"] = r.cstring("the primary weapon name") if version > 9 else None
        if version > 10:
            rec["cockpit"] = r.cstring("the cockpit name")
        else:
            rec["cockpit"] = BE_DEFAULT_COCKPIT
            rec["defaulted"].append("cockpit")
        if version > 11:
            rec["languageName"] = r.i32()
        else:
            rec["languageName"] = 1
            rec["defaulted"].append("languageName")
        rec["length"] = r.pos - at
        rec["sha256"] = hashlib.sha256(data[at:r.pos]).hexdigest()
        records.append(rec)
    if r.pos != len(data):
        raise DecodeError(f"the configurations have {len(data) - r.pos} unread bytes")
    for rec in records:
        rec["listPosition"] = count - 1 - rec["index"]  # sData.Add puts each record at the front
    return {"count": count, "records": records}


def find_configuration(records: list[dict], name: str) -> dict | None:
    """UBattleEngineDataManager::GetConfiguration(name): the first strcmp match from the front of the list, which is
    the last record of that name in the file."""
    key = name.split("\0", 1)[0]
    return next((rec for rec in reversed(records) if rec["name"] == key), None)


def world_configuration(records: list[dict], name: str) -> tuple[dict | None, bool]:
    """UBattleEngineConfigurations::GetConfiguration for a world header's name: (record, found). A name that matches
    nothing gets GetConfiguration(0), the front of the list: the last record in the file."""
    found = find_configuration(records, name)
    if found is not None:
        return found, True
    return (records[-1] if records else None), False


def read_line(data: bytes, pos: int) -> tuple[str | None, int, bool]:
    """One CDXMemBuffer::ReadString(line, 256) and ReadLine's strip of the last character: (line, next position,
    end of file reached). At the end of the data the read stops without a LF, and the strip then eats a real
    character; with nothing read at all the line is None (the loader would write before its buffer)."""
    end = min(len(data), pos + SFX_READ)
    lf = data.find(b"\n", pos, end)
    if lf >= 0:
        raw = bytearray(data[pos:lf + 1])
        nxt, eof = lf + 1, False
    else:
        # the loop stops after 255 bytes, or sets mEOF when it reaches the end of the data before that
        raw = bytearray(data[pos:end])
        nxt, eof = end, len(data) - pos < SFX_READ
    if len(raw) > 1 and raw[-1] == 0x0A and raw[-2] == 0x0D:
        raw[-2:] = b"\n"
    text = bytes(raw).split(b"\0", 1)[0]
    if not text:
        return None, nxt, eof
    return text[:-1].decode("latin-1"), nxt, eof


def parse_sfx(data: bytes) -> dict:
    """CEffect::LoadSFXFile over the file's bytes: the version, the count and each effect's lines, then the chains."""
    pos, eof, lines_read, last_line, line_start = 0, False, 0, 0, 0

    def next_line(what: str) -> str:
        nonlocal pos, eof, lines_read, last_line, line_start
        line = "#"
        while line.startswith("#"):
            if eof:
                raise DecodeError(f"the file ends before {what} (ReadLine would hand back its last line again)")
            last_line, line_start = data.count(b"\n", 0, pos) + 1, pos
            line, pos, eof = read_line(data, pos)
            lines_read += 1
            if line is None:
                raise DecodeError(f"nothing left to read for {what} (ReadLine would write before its buffer)")
        return line

    def field(line: str, what: str) -> str:
        if len(line.encode("latin-1")) >= SFX_FIELD:
            raise DecodeError(f"{what} {line!r} does not fit CEffect's {SFX_FIELD}-byte field")
        return line

    version = atoi(next_line("the version"))
    if version > SFX_VERSION_MAX:
        raise DecodeError(f"version {version}: LoadSFXFile supports {SFX_VERSION_MAX} and older")
    count = atoi(next_line("the effect count"))
    effects = []
    for index in range(max(count, 0)):
        what = f"effect {index}"
        name = field(next_line(what + "'s name"), "a name")
        e = {"index": index, "line": last_line, "offset": line_start, "name": name,
             "sample": field(next_line(what + "'s sample"), "a sample"),
             "lowpassSample": field(next_line(what + "'s low-pass sample"), "a low-pass sample"),
             "volume": atoi(next_line(what + "'s volume")), "falloff": atoi(next_line(what + "'s falloff")),
             "pitchVariance": atoi(next_line(what + "'s pitch variance"))}
        e["looping"] = next_line(what + "'s looping flag").startswith("1") if version >= 101 else False
        e["languageDependent"] = next_line(what + "'s language flag").startswith("1") if version >= 103 else False
        next_line(what + "'s comment line")
        e["length"] = pos - e["offset"]
        e["sha256"] = hashlib.sha256(data[e["offset"]:pos]).hexdigest()
        effects.append(e)
    # the chains: an effect whose name equals one already on the list joins the end of that effect's chain
    heads: dict[bytes, dict] = {}
    for e in effects:
        key = stricmp_key(e["name"])
        head = heads.get(key)
        if head is None:
            heads[key] = e
            e["head"], e["variant"] = e["index"], 0
        else:
            e["head"] = head["index"]
            e["variant"] = sum(1 for other in effects[:e["index"]] if other.get("head") == head["index"])
    for e in effects:
        e["variants"] = sum(1 for other in effects if other["head"] == e["head"])
    return {"version": version, "count": count, "effects": effects, "linesRead": lines_read,
            "bytesRead": pos, "trailingBytes": len(data) - pos, "names": len(heads),
            "chained": sum(1 for e in effects if e["variant"] > 0)}


def atoi(text: str) -> int:
    """C atoi: leading whitespace, an optional sign, the digits that follow; 0 when there are none (32-bit wrap)."""
    s = text.lstrip(" \t\n\v\f\r")
    sign, i = 1, 0
    if s[:1] in ("+", "-"):
        sign, i = (-1 if s[0] == "-" else 1), 1
    j = i
    while j < len(s) and s[j].isdigit() and s[j] in "0123456789":
        j += 1
    value = sign * int(s[i:j]) if j > i else 0
    return (value + (1 << 31)) % (1 << 32) - (1 << 31)


def stricmp_key(text: str) -> bytes:
    """The C runtime's stricmp folds ASCII letters only: the key is the bytes up to a NUL, A-Z made a-z."""
    return text.split("\0", 1)[0].encode("latin-1").lower()


def effect_lookup_key(name: str) -> bytes:
    """CEffect::GetEffectByName's comparison key for an asked name: doubled backslashes made single, then stricmp."""
    out, prev = [], False
    for ch in name.split("\0", 1)[0]:
        if ch == "\\":
            if not prev:
                out.append(ch)
            prev = True
        else:
            out.append(ch)
            prev = False
    return stricmp_key("".join(out))
