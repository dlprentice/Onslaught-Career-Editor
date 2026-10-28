#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Decoders for the level payloads of a Battle Engine Aquila PC resource archive (no I/O, no retail bytes kept).

Each decoder follows the read order of the game function it names (the public decompilation, onslaught-decomp
src/) and refuses input that does not consume exactly:

- the world bodies inside WRES/WRLD (BSWD, RLWD): CWorld::LoadWorld with CWorld::LoadHeader, CWorld::LoadScripts
  (the compiled mission scripts: CMissionScriptObjectCode, CSymbolTable, CEventFunction), CEngine::LoadAllNamedMeshes,
  every thing record (SpawnInitThing's class and its Load), the trees, CInfluenceMap::Load/Skip,
  CWaypointManager::Load, the timings and the occupancy grids;
- ERES: CEngine::Deserialize (CMapTex::Deserialize x N_MAPMIPS, CMap::Deserialize, CHeightField::Load,
  CMixerMap::Init);
- SURF: CDXSurf::Deserialize; SSHD: CStaticShadows::DeserializeAll; LNDS is skipped by the PC loader.

Pure functions over bytes; tools/content_catalog.py joins their results to the rest of the catalogue.
"""
from __future__ import annotations

import hashlib
import math
import struct

DECOMP = "onslaught-decomp"


def cite(source: str, function: str, va: str) -> str:
    return f"{DECOMP} src/{source} {function} @{va}"


L_LOADWORLD = cite("world.cpp", "CWorld::LoadWorld", "0x0050b9c0")
L_LOADHEADER = cite("world.cpp", "CWorld::LoadHeader", "0x0050d4c0")
L_LOADSCRIPTS = cite("world.cpp", "CWorld::LoadScripts", "0x0050ac70")
L_COPYSCRIPT = cite("world.cpp", "CWorld::GetCopyOfScript", "0x0050abc0")
L_SETSCRIPT = cite("thing.cpp", "CComplexThing::SetScript", "0x004f4230")
L_OBJECTCODE = cite("MissionScript/ScriptObjectCode.cpp", "CMissionScriptObjectCode::CMissionScriptObjectCode(file)",
                    "0x00538ec0")
L_SPAWNMESHES = cite("MissionScript/ScriptObjectCode.cpp", "CMissionScriptObjectCode::LoadSpawnedMeshes", "0x005392a0")
L_SYMTAB = cite("MissionScript/Symtab.cpp", "CSymbolTable::CSymbolTable(file)", "0x00539770")
L_INSTR = cite("MissionScript/AsmInstruction.cpp", "CAsmInstruction::Spawn", "0x0052d3d0")
L_CALL = cite("MissionScript/AsmInstruction.cpp", "CInstructionOP_CALL::Execute", "0x0052ea40")
L_PUSH = cite("MissionScript/AsmInstruction.cpp", "CInstructionOP_PUSH::Execute / OP_POP / OP_GETTOP", "0x0052e2c0")
L_NATIVES = cite("MissionScript/IScript.cpp", "gScriptFunctions", "0x0064ce20")
L_EVENTFN = cite("MissionScript/EventFunction.cpp", "CEventFunction::CEventFunction(code, file)", "0x0052fa70")
L_NAMEDMESHES = cite("engine.cpp", "CEngine::LoadAllNamedMeshes", "0x00449dc0")
L_ADDNAMEDMESH = cite("engine.cpp", "CEngine::AddNewGlobalNamedMesh", "n/a")
L_NAMEDMESH_INIT = cite("NamedMesh.cpp", "CNamedMesh::Init", "0x004bbcd0")
L_SPAWNINIT = cite("InitThing.cpp", "SpawnInitThing", "0x0048c650")
L_INITLOAD = cite("InitThing.h", "CInitThing::Load (and the subclasses' Load)", "0x0040e280")
L_SPAWNTHING = cite("oids.cpp", "SpawnThing", "0x004bf090")
L_INFLUENCE = cite("InfluenceMap.cpp", "CInfluenceMap::Load / CInfluenceMap::Skip", "n/a")
L_WAYPOINTS = cite("WaypointManager.cpp", "CWaypointManager::Load -> CWaypointPath::Load", "0x00505ae0")
L_FINDNEAREST = cite("WaypointManager.cpp", "CWaypointManager::FindNearest", "0x00505c30")
L_OCCUPANCY = cite("NavigationMap.cpp", "COccupancyGrid::Load / SkipLegacy / SkipHeader", "0x004be050")
L_BECONFIGS = cite("BattleEngineConfigurations.cpp", "UBattleEngineConfigurations::Load", "0x0040f180")
L_ENGINE = cite("engine.cpp", "CEngine::Deserialize", "0x0044a6e0")
L_MAPTEX = cite("maptex.cpp", "CMapTex::Deserialize", "0x004916c0")
L_MAP = cite("Map.cpp", "CMap::Deserialize", "0x00491060")
L_HEIGHTFIELD = cite("HeightField.cpp", "CHeightField::Load", "0x0047f750")
L_MIXERMAP = cite("mixermap.cpp", "CMixerMap::Init -> SMixerSlot::Init", "0x005232b0")
L_SURF = cite("DXSurf.cpp", "CDXSurf::Deserialize -> SSurfStrip::Create", "0x00556490")
L_SHADOWS = cite("StaticShadows.cpp", "CStaticShadows::DeserializeAll -> CStaticShadow::Deserialize", "0x004ee8a0")
L_TEXTGET = cite("text.cpp", "CText::GetString (TEXT.GetString)", "n/a")
L_FINDTHING = cite("world.cpp", "CWorld::FindThingByName", "0x0050af70")

# Object ids (oids.h, NamedMesh.h, oids.cpp's local enum).
OID_NAMES = {3: "battle-engine", 7: "tree", 8: "unit", 10: "radar", 11: "named-mesh", 15: "start", 16: "rocket",
             17: "building-named-mesh", 18: "waypoint", 19: "spawner", 21: "shell", 25: "building", 26: "cutscene",
             27: "level-script", 28: "squad", 29: "animal", 31: "debris", 33: "wall", 35: "feature",
             36: "sphere-trigger", 37: "safe-side", 38: "wingman-start", 39: "hazard", 41: "spawn-point",
             43: "escape-pod"}
SPAWNTHING_MAKES = frozenset({3, 7, 10, 11, 15, 16, 17, 18, 19, 21, 25, 26, 27, 29, 31, 36, 37, 38, 41, 43})
OID_UNIT, OID_BUILDING, OID_SQUAD, OID_FEATURE, OID_HAZARD, OID_START = 8, 25, 28, 35, 39, 15
# SpawnInitThing's class per id (the default is CInitThing).
INIT_CLASS = {8: "unit", 25: "unit", 28: "squad", 19: "spawner", 26: "cutscene", 15: "start", 41: "start", 7: "tree",
              33: "wall", 35: "feature", 39: "hazard", 36: "sphere-trigger"}

# gScriptFunctions (IScript.cpp): each native's name and argument types in CALL-index order
# (i int, f float, s string, b bool, t thing, p position, * any).
SCRIPT_NATIVES = (
    ("FollowWaypoint", "si"), ("FollowWaypointWait", "s"), ("SetSpeed", "f"), ("SpawnThing", "ssis"), ("Pause", "f"),
    ("PostEvent", "s"), ("Rand", "i"), ("IsFriendly", ""), ("LevelLost", ""), ("LevelWon", ""), ("PlaySample", "s"),
    ("Print", "*"), ("Exists", "t"), ("Die", ""), ("GetThingRef", "t"), ("Activate", ""), ("PrintText", "i"),
    ("AddMessage", "if"), ("GetHealth", ""), ("SetTimer", "f"), ("GetDistToObj", "t"), ("GetPlayer", "i"),
    ("SetVisible", "b"), ("SetObjective", ""), ("SetAIState", "i"), ("IsA", "i"), ("Teleport", "s"),
    ("PlayCutscene", "s"), ("PlayCharMessage", "iif"), ("Deactivate", ""), ("UnsetObjective", ""),
    ("IsObjective", ""), ("SetVulnerable", "b"), ("NumContained", "s"), ("HighlightHudPart", "i"),
    ("UnHighlightHudPart", "i"), ("PlayCharMessageWait", "iif"), ("GetWeaponAmmo", ""), ("GetWeaponName", ""),
    ("GetWeaponCharge", ""), ("GetNumUnits", "ii"), ("SetAllegiance", "i"), ("SetWindVector", "fff"),
    ("SetRainDensity", "f"), ("SetSnowDensity", "f"), ("SetLightningDensity", "f"), ("SetHealth", "f"),
    ("GetRatioBattleLineNodes", "i"), ("SetScript", "s"), ("GetPos", ""), ("SpawnParticle", "sp"),
    ("SetSegmentHealth", "sf"), ("SetAllSegmentsHealth", "f"), ("PlayAnimation", "sbb"),
    ("PlayAnimationWait", "sbb"), ("GetMapHeight", "p"), ("GetWaterHeight", ""), ("GetX", "p"), ("GetY", "p"),
    ("GetZ", "p"), ("SetX", "pf"), ("SetY", "pf"), ("SetZ", "pf"), ("SetGoalPoint", "p"), ("GetSafePos", ""),
    ("GetComponent", "i"), ("CreatePosition", "fff"), ("GetFloatRand", ""), ("SetVar", "s*"), ("Damage", "f"),
    ("GameTime", ""), ("IsEnemy", ""), ("Land", ""), ("SpawnersEmpty", ""), ("Dive", ""), ("Surface", ""),
    ("InitVariable", "ii"), ("SetVariable", "iff"), ("ShutdownVariable", "i"), ("Shutdown", ""), ("GetEnergy", ""),
    ("GetVariable", "f"), ("Retreat", ""), ("PrimaryObjectiveComplete", "ii"), ("SecondaryObjectiveComplete", "ii"),
    ("AddScore", "i"), ("Attack", "t"), ("PrimaryObjectiveFailed", "ii"), ("SecondaryObjectiveFailed", "ii"),
    ("GetAngle", "t"), ("PlayPCharMessage", "iifi"), ("PlayPCharMessageWait", "iifi"), ("GetInitialHealth", ""),
    ("SpawnersInUse", ""), ("SetSpawnScript", "s"), ("Stop", ""), ("Deploy", ""), ("Undeploy", ""),
    ("EnableWeapon", "s"), ("DisableWeapon", "s"), ("EnableFlightMode", ""), ("DisableFlightMode", ""),
    ("GetSquad", ""), ("GetTarget", ""), ("Normalise", "p"), ("Magnitude", "p"), ("LevelLostString", "i"),
    ("IsFiring", ""), ("IsNumberBetween", "fff"), ("SetSegmentVulnerable", "sb"), ("SetAllSegmentsVulnerable", "b"),
    ("GetRealHealth", ""), ("SwitchMessagesOn", ""), ("SwitchMessagesOff", ""), ("Goto3PointPanCamera", "tpppf"),
    ("Goto4PointPanCamera", "tppppf"), ("GotoPlayerCamera", ""), ("GetConfiguration", ""), ("AddHelpMessage", "i"),
    ("SetGoodieState", "ii"), ("GetGoodieState", "i"), ("MPDeclarePlayerWon", "i"), ("MPDeclareGameDrawn", ""),
    ("SetSlot", "ib"), ("GetSlot", "i"), ("InJetMode", ""), ("SetPlayerLives", "ii"), ("Launch", "p"),
    ("HalfDestroy", ""), ("SetVelocity", "p"), ("TriggerHitEffect", "f"), ("GetNumber", ""), ("SpawnEscapePod", ""),
    ("SetSlotSave", "ib"), ("ResetSegmentHealth", "sf"), ("SetPos", "p"), ("SetLockable", "b"),
    ("ToggleCockpit", ""), ("SetStealth", "f"), ("TeleportOrientation", "fff"), ("EnableSpawner", "s"),
    ("DisableSpawner", "s"), ("SetName", "s"), ("IsOverWater", ""),
)
# What a native does with an argument, from its handler in IScript.cpp (function, argument index -> role).
ARG_ROLES = {
    # TEXT.GetString(args[n]) / TEXT_DB.GetString (CGame::DeclareLevelLost)
    ("PrintText", 0): "text", ("AddMessage", 0): "text", ("PlayCharMessage", 0): "text-speaker",
    ("PlayCharMessage", 1): "text", ("PlayCharMessageWait", 0): "text-speaker", ("PlayCharMessageWait", 1): "text",
    ("PlayPCharMessage", 0): "text-speaker", ("PlayPCharMessage", 1): "text",
    ("PlayPCharMessageWait", 0): "text-speaker", ("PlayPCharMessageWait", 1): "text", ("LevelLostString", 0): "text",
    # UPhysicsManager::GetUnitData(type) and SpawnThingByName(type); the script by name (SetScript); the emitter
    ("SpawnThing", 0): "unit", ("SpawnThing", 1): "emitter", ("SpawnThing", 3): "script",
    ("SetScript", 0): "script", ("SetSpawnScript", 0): "script",
    # CWaypointManager::FindNearest(name)
    ("FollowWaypoint", 0): "waypoint-path", ("FollowWaypointWait", 0): "waypoint-path",
    # WORLD.FindThingByName(name)
    ("GetThingRef", 0): "thing-name", ("Teleport", 0): "thing-name", ("PlayCutscene", 0): "thing-name",
    ("PostEvent", 0): "event", ("PlaySample", 0): "sample", ("SpawnParticle", 0): "effect",
    ("EnableSpawner", 0): "spawner", ("DisableSpawner", 0): "spawner",
    ("PrimaryObjectiveComplete", 0): "objective-number", ("SecondaryObjectiveComplete", 0): "objective-number",
    ("PrimaryObjectiveFailed", 0): "objective-number", ("SecondaryObjectiveFailed", 0): "objective-number",
}
OBJECTIVE_NATIVES = frozenset({"SetObjective", "UnsetObjective", "IsObjective", "PrimaryObjectiveComplete",
                               "SecondaryObjectiveComplete", "PrimaryObjectiveFailed", "SecondaryObjectiveFailed"})
OPCODES = ("OP_NOP", "OP_PLUS", "OP_MINUS", "OP_MULTIPLY", "OP_DIVIDE", "OP_PUSH", "OP_POP", "OP_OR", "OP_AND",
           "OP_GREAT_THAN", "OP_LESS_THAN", "OP_GREAT_EQ_THAN", "OP_LESS_EQ_THAN", "OP_LABEL", "OP_REMOVE_TOP",
           "OP_CMP", "OP_CMPB", "OP_CMPNEB", "OP_JMPNE", "OP_JMPFALSE", "OP_JMP", "OP_GETTOP", "OP_POINTER",
           "OP_RETURN", "OP_CALL", "OP_CALLLOCAL", "OP_PUSHPC")
OP_PUSH, OP_POP, OP_GETTOP, OP_CALL = 5, 6, 21, 24
DT_NAMES = {1: "int", 2: "float", 3: "string", 4: "bool", 5: "thing", 6: "position"}
NUM_SCRIPT_EVENTS = 13
LIMIT = 1 << 20  # a count above this is framing damage, not data


class DecodeError(ValueError):
    pass


class Reader:
    def __init__(self, data: bytes, pos: int = 0, end: int | None = None):
        self.data, self.pos, self.end = data, pos, len(data) if end is None else end

    def take(self, n: int) -> bytes:
        if n < 0 or self.pos + n > self.end:
            raise DecodeError(f"read of {n} bytes at {self.pos} passes the end ({self.end})")
        out = self.data[self.pos:self.pos + n]
        self.pos += n
        return out

    def unpack(self, fmt: str):
        return struct.unpack("<" + fmt, self.take(struct.calcsize("<" + fmt)))

    def i32(self) -> int:
        return self.unpack("i")[0]

    def f32(self) -> float:
        return self.unpack("f")[0]

    def count(self, fmt: str = "i") -> int:
        value = self.unpack(fmt)[0]
        if not 0 <= value <= LIMIT:
            raise DecodeError(f"implausible count {value} at {self.pos}")
        return value

    def cstring(self) -> str:
        """A string read byte by byte up to and including its NUL (CInitThing::Load's do/while)."""
        end = self.data.find(b"\0", self.pos, self.end)
        if end < 0 or end - self.pos > 255:
            raise DecodeError(f"unterminated string at {self.pos}")
        text = self.data[self.pos:end].decode("latin-1")
        self.pos = end + 1
        return text

    def lstring(self, fmt: str = "b") -> str:
        """A length-prefixed string (signed char length unless fmt says otherwise)."""
        n = self.unpack(fmt)[0]
        if n < 0:
            raise DecodeError(f"negative string length at {self.pos}")
        return self.take(n).decode("latin-1")

    def chunk_header(self) -> tuple[str, int]:
        """CChunkReader::GetNext: a tag and a size, read in place (the payload follows; nothing is skipped)."""
        tag, size = self.unpack("4sI")
        return tag.decode("latin-1"), size


def finite(values) -> bool:
    return all(math.isfinite(v) for v in values)


# ---------------------------------------------------------------------------------------------- mission scripts
def read_script_value(r: Reader, dtype: int):
    if dtype in (1, 5):
        return r.i32()
    if dtype == 2:
        return r.f32()
    if dtype == 3:
        return r.lstring("i")
    if dtype == 4:
        return r.i32() != 0
    if dtype == 6:
        return list(r.unpack("3f"))
    raise DecodeError(f"unknown script data type {dtype}")


def read_object_code(r: Reader) -> dict:
    """CMissionScriptObjectCode(file): instructions, event PCs, symbol table, event functions, two trailing words."""
    instructions = []
    for _ in range(r.count()):
        opcode, attr = r.unpack("ii")
        if not 0 <= opcode < len(OPCODES):
            raise DecodeError(f"unknown script opcode {opcode}")
        instructions.append((opcode, attr))
    event_pcs = list(r.unpack(f"{NUM_SCRIPT_EVENTS}i"))
    symbols = []
    for _ in range(r.count()):
        name = r.lstring("i")
        dtype = r.i32()
        value = read_script_value(r, dtype) if dtype else None
        sym_type, index, flag = r.unpack("iii")
        symbols.append({"name": name, "dataType": DT_NAMES.get(dtype) if dtype else None, "value": value,
                        "symbolType": sym_type, "index": index, "flag": flag})
    next_index = r.i32()
    functions = []
    for _ in range(r.count()):
        entry = r.i32()
        params = [r.i32() for _ in range(r.count())]
        names = []
        for p in params:
            if not 0 <= p < len(symbols) or symbols[p]["dataType"] != "string":
                raise DecodeError("event function parameter is not a string symbol")
            names.append(symbols[p]["value"])
        functions.append({"entryPC": entry, "events": names})
    tail = list(r.unpack("ii"))
    return {"instructions": instructions, "eventPCs": event_pcs, "symbols": symbols, "nextSymbolIndex": next_index,
            "eventFunctions": functions, "tail": tail}


def analyse_script(code: dict) -> dict:
    """Native calls and their literal arguments.

    A CALL's arguments are the values its n preceding instructions pushed when each is an OP_PUSH (the rule
    CMissionScriptObjectCode::LoadSpawnedMeshes applies to SpawnThing's first argument). A pushed symbol counts as a
    literal only if it holds a stored value and no OP_POP or OP_GETTOP in the script writes it (the only writes to a
    symbol's value in the VM).
    """
    instructions, symbols = code["instructions"], code["symbols"]
    written = {attr for op, attr in instructions if op in (OP_POP, OP_GETTOP)}

    def literal(i: int):
        op, attr = instructions[i]
        if op != OP_PUSH or not 0 <= attr < len(symbols) or attr in written:
            return None
        sym = symbols[attr]
        return None if sym["value"] is None else (sym["dataType"], sym["value"])

    calls = []
    for i, (op, attr) in enumerate(instructions):
        if op != OP_CALL:
            continue
        index, nargs = attr & 0xFF, (attr >> 8) & 0xFF
        if index >= len(SCRIPT_NATIVES):
            raise DecodeError(f"CALL names native {index}, beyond the table")
        name, types = SCRIPT_NATIVES[index]
        args = []
        for k in range(nargs):
            j = i - nargs + k
            lit = literal(j) if j >= 0 else None
            args.append(None if lit is None else {"type": lit[0], "value": lit[1]})
        calls.append({"pc": i, "native": name, "nativeIndex": index, "args": args, "declaredArgs": len(types)})
    events = sorted({e for f in code["eventFunctions"] for e in f["events"]})
    return {"calls": calls, "postedEvents": sorted({c["args"][0]["value"] for c in calls
                                                    if c["native"] == "PostEvent" and c["args"] and c["args"][0]},
                                                   key=str),
            "handledEvents": events,
            "fixedEventHandlers": sum(1 for pc in code["eventPCs"] if pc != -1)}


def literal_args(calls: list[dict], role: str) -> list[dict]:
    """Every (call, argument) whose ARG_ROLES role is role: [{native, pc, argument, value}] (value None = not literal)."""
    out = []
    for c in calls:
        for k, arg in enumerate(c["args"]):
            if ARG_ROLES.get((c["native"], k)) == role:
                out.append({"native": c["native"], "pc": c["pc"], "argument": k,
                            "value": None if arg is None else arg["value"]})
    return out


# ------------------------------------------------------------------------------------------------- world bodies
def read_init(r: Reader, version: int, cls: str) -> dict:
    """CInitThing::Load for version 43..50 (LoadWorld refuses others), then the subclass's fields."""
    if not 43 <= version <= 50:
        raise DecodeError(f"world version {version} outside 43..50")
    pos = list(r.unpack("3f"))
    yaw_pitch_roll = list(r.unpack("3f"))
    mesh_no, allegiance, target = r.unpack("iii")
    init = {"position": pos, "orientation": yaw_pitch_roll, "meshNumber": mesh_no, "allegiance": allegiance,
            "target": target, "script": r.cstring(), "name": r.cstring(), "spawnScript": r.cstring()}
    init["active"] = r.i32()
    init["attachScriptsToUnits"] = r.i32() if version > 45 else None
    if not finite(pos + yaw_pitch_roll):
        raise DecodeError("non-finite placement")
    if cls == "spawner":
        amount, delay, squad_delay, initial_delay, squad_size = r.unpack("ifffi")
        init["spawner"] = {"amount": amount, "delay": delay, "squadDelay": squad_delay, "initialDelay": initial_delay,
                           "squadSize": squad_size, "spawnUnit": r.cstring(),
                           "spawnerSpawnScript": r.cstring() if version > 43 else None}
    elif cls == "squad":
        init["squad"] = {"amount": r.i32(), "mode": r.i32()}
    elif cls == "cutscene":
        init["cutscene"] = {"file": r.cstring(), "linkTo": r.cstring()}
    elif cls == "start":
        init["start"] = {"planeMode": r.i32(), "playerNumber": r.i32()}
    elif cls == "tree":
        init["tree"] = {"treeType": r.cstring()}
    elif cls == "wall":
        init["wall"] = {"length": r.f32(), "life": r.f32(), "wallType": r.cstring()}
    elif cls == "sphere-trigger":
        init["sphereTrigger"] = {"radius": r.f32()}
    return init


def parse_world_body(body: bytes, physics: dict, *, base: bool) -> dict:
    """CWorld::LoadWorld over one world body (BSWD loads with base TRUE, RLWD with base FALSE).

    physics holds the definition names UPhysicsManager knows ("units", "features", "hazards": sets of exact names,
    strcmp) and "squadless" (unit names whose behaviour makes SpawnSquad return NULL), which decide whether a thing
    takes a slot in LoadWorld's things[] array: CWaypointPath::Load indexes that array, not the file's records.
    """
    r = Reader(body)
    version = r.unpack("H")[0]
    if not 43 <= version <= 50:
        raise DecodeError(f"world version {version} outside 43..50")
    hversion, unused1, unused2 = r.unpack("iii")
    configs = [r.lstring() for _ in range(r.count())]
    header = {"headerVersion": hversion, "battleEngineConfigurations": configs, "worldType": None}
    if hversion >= 2:
        r.unpack("iii")
    if hversion >= 3:
        header["worldType"] = r.i32()
    base_level = r.i32()
    scripts = []
    for ordinal in range(r.count()):
        at = r.pos
        name = r.lstring("i")
        code = read_object_code(r)
        r.take(10)
        scripts.append({"ordinal": ordinal, "offset": at, "name": name, "code": code,
                        "sha256": hashlib.sha256(body[at:r.pos]).hexdigest(), "length": r.pos - at})
    map_number = r.i32()
    named_meshes = [r.lstring("B") for _ in range(r.count())]
    things, slot = [], 0
    for ordinal in range(r.count("H")):
        at = r.pos
        oid = r.i32()
        kind = OID_NAMES.get(oid, f"oid-{oid}")
        cls = INIT_CLASS.get(oid, "base")
        row = {"ordinal": ordinal, "offset": at, "oid": oid, "kind": kind}
        if oid in (OID_UNIT, OID_BUILDING):
            row["init"] = read_init(r, version, "base")
            row["definition"] = r.lstring()
            row["diesOn"] = r.i32()
            takes = row["definition"] in physics["units"]
        elif oid == OID_SQUAD:
            row["init"] = read_init(r, version, "squad")
            row["definition"] = r.lstring()
            row["diesOn"] = r.i32()
            takes = row["definition"] in physics["units"] and row["definition"] not in physics["squadless"]
        elif oid in (OID_FEATURE, OID_HAZARD):
            row["init"] = read_init(r, version, "base")
            row["definition"] = r.lstring()
            row["diesOn"] = r.i32()
            takes = row["definition"] in physics["features" if oid == OID_FEATURE else "hazards"]
        elif oid == OID_START:
            row["init"] = read_init(r, version, "start")
            takes = not base
        elif oid in SPAWNTHING_MAKES:
            row["init"] = read_init(r, version, cls)
            takes = True
        else:
            raise DecodeError(f"thing {ordinal} has object id {oid}, which SpawnThing does not make (its record "
                              "would not be read)")
        row["slot"] = slot if takes else None
        if takes:
            slot += 1
        row["length"] = r.pos - at
        things.append(row)
    tree_groups = []
    for _ in range(r.count("h")):
        y0, x0, y1, x1 = r.unpack("4f")
        count = r.i32()
        tree_groups.append({"rect": [x0, y0, x1, y1], "count": count, "treeType": r.lstring(), "seed": r.i32()})
    tree_types = []
    for _ in range(r.count()):
        name = r.lstring()
        positions = [r.unpack("ffi") for _ in range(r.count())]
        tree_types.append({"name": name, "count": len(positions)})
    influence_version = r.unpack("H")[0]
    nodes = r.count()
    r.take(nodes * (12 if influence_version == 0 else 16))
    links = r.count()
    r.take(links * (8 if influence_version == 0 else 12))
    if influence_version not in (0, 1):
        raise DecodeError(f"influence map version {influence_version}")
    by_slot = {t["slot"]: t for t in things if t["slot"] is not None}
    paths = []
    for ordinal in range(r.count("h")):
        at = r.pos
        name = r.lstring()
        members = []
        for _ in range(r.count()):
            index = r.unpack("h")[0]
            thing = by_slot.get(index) if index >= 0 else None
            members.append({"slot": index, "thingOrdinal": thing["ordinal"] if thing else None,
                            "isWaypoint": bool(thing and thing["oid"] == 18)})
        paths.append({"ordinal": ordinal, "offset": at, "name": name, "members": members})
    timings = dict(zip(("oldF", "oldG", "oldH", "preRun", "pan", "sGrade", "dGrade", "timeLimit", "fullScoreTime",
                        "percentageScoreTime", "scorePercentage"), r.unpack("fffffiiffff")))
    if 45 <= version < 48:
        r.unpack("iiiff")
    grids = []
    if version >= 47:
        for _ in range(3):
            gv = r.i32()
            r.take({1: 0x8000, 2: 0x2000}.get(gv, 0))
            grids.append(gv)
        if version < 50:
            r.unpack("5i")
    start_time = r.f32() if version >= 49 else None
    if r.pos != len(body):
        raise DecodeError(f"world body has {len(body) - r.pos} unread bytes")
    return {"version": version, "header": header, "baseLevel": base_level, "mapNumber": map_number,
            "scripts": scripts, "namedMeshes": named_meshes, "things": things,
            "treeGroups": len(tree_groups), "treesInGroups": sum(g["count"] for g in tree_groups),
            "treeTypes": tree_types, "influenceMap": {"version": influence_version, "nodes": nodes, "links": links},
            "waypointPaths": paths, "timings": timings, "occupancyGridVersions": grids, "levelStartTime": start_time,
            "slotsCounted": slot}


# -------------------------------------------------------------------------------------------------------- ERES
MAPTEX_FMT = "<IiIhxxiii6i6i"  # CMapTex (0x4c bytes): mData, mUnknown04, mUnknown08, mSet, mTexSize, mNum, mSize, ...
HEIGHTFIELD_SIZE = 0x13DC
HF_TILES, HF_SAMPLES = 64, 9
MIXER_MAP_SLOTS, MIXER_MAP_SIZE, MIXER_SLOT_SIZE = 0x1000, 0x40000, 0x14


def parse_eres(payload: bytes) -> dict:
    r = Reader(payload)
    tag, _size = r.chunk_header()
    if tag != "ENGN":
        raise DecodeError(f"ERES starts with {tag!r}, CEngine::Deserialize asserts ENGN")
    count = r.i32()
    if count != 7:
        raise DecodeError(f"{count} mixer mips (N_MAPMIPS is 7)")
    mips = []
    for i in range(count):
        r.chunk_header()
        r.chunk_header()
        fields = struct.unpack(MAPTEX_FMT, r.take(0x4C))
        data_ptr, _u04, extra_ptr, mset, tex_size, num, size = fields[:7]
        data_sha = None
        if data_ptr:
            r.chunk_header()
            data_sha = hashlib.sha256(r.take(num * tex_size)).hexdigest()
        if extra_ptr:
            r.chunk_header()
            r.take(num * 1024)
        mips.append({"mip": i, "set": mset, "size": size, "textures": num, "textureBytes": tex_size,
                     "minAlpha": list(fields[7:13]), "maxAlpha": list(fields[13:19]), "pixelSha256": data_sha,
                     "hasExtraTable": bool(extra_ptr)})
    r.chunk_header()
    map_number = r.i32()
    r.chunk_header()
    r.chunk_header()
    hf = r.take(HEIGHTFIELD_SIZE)
    r.chunk_header()
    samples = r.take(HF_TILES * HF_TILES * HF_SAMPLES * HF_SAMPLES * 2)
    heights = struct.unpack(f"<{len(samples) // 2}h", samples)
    u8 = lambda o: hf[o]
    f32 = lambda o: struct.unpack_from("<f", hf, o)[0]
    i32 = lambda o: struct.unpack_from("<i", hf, o)[0]
    hfp = 0x1078
    heightfield = {
        "tiles": [HF_TILES, HF_TILES], "samplesPerTile": [HF_SAMPLES, HF_SAMPLES],
        "sampleCount": len(heights), "sampleMin": min(heights), "sampleMax": max(heights),
        "samplesSha256": hashlib.sha256(samples).hexdigest(),
        "heightScale": f32(0x102C), "waterLevel": f32(0x1034), "gridShift": [i32(0x1038), i32(0x103C)],
        "fog": i32(hfp + 0x00) & 0xFFFFFFFF, "sun": i32(hfp + 0x04) & 0xFFFFFFFF,
        "antiSun": i32(hfp + 0x08) & 0xFFFFFFFF, "ambient": i32(hfp + 0x14) & 0xFFFFFFFF,
        "fogDensity": f32(hfp + 0x20), "visibleSun": bool(u8(hfp + 0x28)),
        "sunPosition": [f32(hfp + 0x2C), f32(hfp + 0x30), f32(hfp + 0x34)],
        # CMap::Deserialize's arguments: SetKempyCube(mHFP+0x18), LoadMixers(+0x1030), LoadMixerTexture(mHFP+0x1c),
        # SetWater(mHFP+0x1d)
        "skyCube": u8(hfp + 0x18), "mixerSet": u8(0x1030), "detailMixer": u8(hfp + 0x1C), "water": u8(hfp + 0x1D),
    }
    r.chunk_header()
    slots_with_data, entries = 0, 0
    for _ in range(MIXER_MAP_SLOTS):
        r.chunk_header()
        r.chunk_header()
        slot = r.take(MIXER_SLOT_SIZE)
        n, data_ptr = struct.unpack_from("<iI", slot, 0)
        if data_ptr:
            r.chunk_header()
            r.take(n * 81)
            slots_with_data += 1
            entries += n
    r.chunk_header()
    mixer_map = r.take(MIXER_MAP_SIZE)
    if r.pos != len(payload):
        raise DecodeError(f"ERES has {len(payload) - r.pos} unread bytes")
    return {"mixerMips": mips, "mapNumber": map_number, "heightField": heightfield,
            "mixerMap": {"slots": MIXER_MAP_SLOTS, "slotsWithData": slots_with_data, "slotEntries": entries,
                         "mapBytes": len(mixer_map), "mapSha256": hashlib.sha256(mixer_map).hexdigest()}}


def parse_surf(payload: bytes) -> dict:
    """CDXSurf::Deserialize: a strip count, then per strip a count and (count + 1) steps of three XYZ vertices."""
    if len(payload) < 8:
        return {"strips": 0, "vertices": 0, "empty": True}
    r = Reader(payload)
    r.chunk_header()
    strips = []
    for _ in range(r.count()):
        r.chunk_header()
        n = r.count()
        r.take((n + 1) * 3 * 12)
        strips.append(n)
    if r.pos != len(payload):
        raise DecodeError(f"SURF has {len(payload) - r.pos} unread bytes")
    return {"strips": len(strips), "steps": sum(n + 1 for n in strips), "vertices": sum((n + 1) * 3 for n in strips),
            "empty": False}


def parse_sshd(payload: bytes) -> dict:
    """CStaticShadows::DeserializeAll: count shadows, each with its rectangle, thing number and part maps."""
    r = Reader(payload)
    r.chunk_header()
    r.chunk_header()
    count = r.count()
    r.chunk_header()
    maps = shadowed = cells = 0
    for _ in range(count):
        r.chunk_header()
        _x, _y, _w, _h, num_maps, _thing = r.unpack("6i")
        if not 0 <= num_maps <= LIMIT:
            raise DecodeError("implausible shadow map count")
        for _ in range(num_maps):
            r.chunk_header()
            _mx, _my, mw, mh, is_shadowed = r.unpack("5i")
            maps += 1
            if is_shadowed:
                shadowed += 1
                r.chunk_header()
                for _ in range(mw * mh):
                    if r.i32() == 1:
                        r.take(0x200)
                        cells += 1
    if r.pos != len(payload):
        raise DecodeError(f"SSHD has {len(payload) - r.pos} unread bytes")
    return {"shadows": count, "partMaps": maps, "shadowedMaps": shadowed, "cells": cells}
