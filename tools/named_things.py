#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""A source-modelled registry of named things (WORLD.mNamedThings) and predicted lookups after a level loads.

A mission script finds a thing by name (GetThingRef, Teleport and PlayCutscene in IScript.cpp), and a cutscene the
thing it follows (CCutscene::Start), through CWorld::FindThingByName, which walks WORLD.mNamedThings. This module works
out, from a level's decoded world bodies (tools/world_resources_decode.py:parse_world_body), which things join that
list, in which order, and so which thing a name would find if initialization succeeds. These are predictions from the
public decompilation (onslaught-decomp src/), cited by function and never quoted, not runtime observations:

- Joining. CComplexThing::Init (thing.cpp @0x004f3fd0) calls CComplexThing::SetName (@0x004f4120), which adds the thing
  to WORLD.mNamedThings when its init's name is not empty. The list's Add (GenericSPtrSet::Add, SPtrSet.cpp
  @0x004e5a80) puts the new node at the front, and FindThingByName (world.cpp @0x0050af70) walks from the front and
  returns the first thing whose name is strcmp-equal: the thing named most recently.
- Which things. Every thing class CWorld::LoadWorld makes reaches CComplexThing::Init through its Init's
  SUPERTYPE::Init, except CTree and CWaypoint, which derive from CThing (tree.h, waypoint.h): CThing::Init
  (@0x004f34a0) names nothing, so a named tree or waypoint is never found by name.
- When. CWorld::LoadWorld (@0x0050b9c0) reads every thing record first and initialises the things afterwards, in the
  order of their things[] slots ("start the things"); a record that took no slot is never initialised. The real world
  loads its base world (CWorld::Load(base_level, TRUE)) right after reading its own scripts, so every base-world thing
  joins the list before any thing of the real world.
- The base world keeps a slot only when CCareer::DoesBaseThingExist(level, slot) (Career.cpp @0x0041bb20) and not
  (dies_on != -1 and CCareer::IsWorldLater(level, dies_on) @0x0041bbb0); otherwise the thing is deleted without being
  initialised. The career decides: a blank career keeps every base thing (CCareerNode::Blank @0x0041b740), multiplayer
  and a world the career does not list keep it, and the career's 288 bits (BASE_THINGS_EXISTS_SIZE) cover slots 0-287.
  dies_on[] is written by the records that read a dies-on world (units, buildings, squads, features, hazards) at the
  slot about to be filled, so a slot taken by any other record keeps whatever the last record that failed to take it
  wrote (the array starts at -1).
- Squads. A unit or building record (UPhysicsManager::GetUnitData: the first unit definition of that name) whose
  behaviour has a squad (UPhysicsManager::SpawnSquad @0x0050f4b0: UB_MECH and UB_INFANTRY make a CRelaxedSquad, the
  behaviours SpawnSquad lists make none, every other one a CNormalSquad) becomes a squad of one marked as the unit's
  (mUnknown84): CSquad::Init (squad.cpp @0x004e5e70) gives the record's name to the member unit it spawns and clears its
  own. A squad record's CSquad::Init gives the name to each of its `amount` member units, in order, and clears its own,
  unless the squad is a CNormalSquad (Unknown83 answers 0; CRelaxedSquad's answers 2) and the record does not attach
  scripts to units: then the squad keeps the name and its members have none. A unit whose behaviour is UB_JEEP takes a
  slot but UPhysicsManager::SpawnThing (@0x0050df80) makes nothing for it, so LoadWorld would initialise a null thing.
- At run time. IScript::SetName (@0x00535c70) renames the thing that runs the script (an empty name takes it off the
  list); spawners, SpawnThing, SpawnEscapePod, a unit's components and the start's battle engine make things whose inits
  carry no name; a thing that shuts down leaves the list (CComplexThing::Shutdown @0x004f41b0). Those changes depend
  on play, so a name's answer here is the one right after loading.

Pure functions over decoded world bodies; tools/content_catalog.py joins their results to the catalogue, and
tools/content_catalog_gate.py runs them over an installed game.
"""
from __future__ import annotations

from typing import Callable, Iterable

DECOMP = "onslaught-decomp"


def cite(source: str, function: str, va: str) -> str:
    return f"{DECOMP} src/{source} {function} @{va}"


L_SETNAME = cite("thing.cpp", "CComplexThing::Init -> CComplexThing::SetName", "0x004f3fd0, 0x004f4120")
L_ADD = cite("SPtrSet.cpp", "GenericSPtrSet::Add (a new node goes to the front)", "0x004e5a80")
L_FIND = cite("world.cpp", "CWorld::FindThingByName (the first strcmp match from the front)", "0x0050af70")
L_LOADWORLD = cite("world.cpp", "CWorld::LoadWorld (records first, then Init in slot order; the base world loads "
                   "inside the real world's load, after its scripts)", "0x0050b9c0")
L_THING_INIT = cite("thing.cpp", "CThing::Init (names nothing; CTree and CWaypoint derive from CThing)", "0x004f34a0")
L_BASE_KEEP = (cite("Career.cpp", "CCareer::DoesBaseThingExist", "0x0041bb20") + "; "
               + cite("Career.cpp", "CCareer::IsWorldLater", "0x0041bbb0"))
L_SQUAD_INIT = cite("squad.cpp", "CSquad::Init (the name goes to the member units or stays with the squad)",
                    "0x004e5e70")
L_SPAWNSQUAD = cite("WorldPhysicsManager.cpp", "UPhysicsManager::SpawnSquad", "0x0050f4b0")
L_SPAWNUNIT = cite("WorldPhysicsManager.cpp", "UPhysicsManager::SpawnThing", "0x0050df80")
L_SCRIPT_SETNAME = cite("MissionScript/IScript.cpp", "IScript::SetName (renames the script's own thing)", "0x00535c70")
L_NATIVES = cite("MissionScript/IScript.cpp", "IScript::GetThingRef / Teleport / PlayCutscene -> WORLD.FindThingByName",
                 "0x005367c0, 0x005369b0, 0x00535890")

OID_TREE, OID_WAYPOINT = 7, 18                  # CTree, CWaypoint: CThing, not CComplexThing
NOT_COMPLEX = frozenset({OID_TREE, OID_WAYPOINT})
OID_UNIT, OID_BUILDING, OID_SQUAD = 8, 25, 28
READS_DIES_ON = frozenset({8, 25, 28, 35, 39})  # unit, building, squad, feature, hazard (LoadWorld's arms)
# EUnitBehaviour (WorldPhysicsManager.h) as UPhysicsManager::SpawnSquad sorts it.
UB_MECH, UB_INFANTRY, UB_JEEP = 0, 3, 11
RELAXED_SQUAD = frozenset({UB_MECH, UB_INFANTRY})
NO_SQUAD = frozenset({4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25})
CAREER_BASE_BITS = 288                           # BASE_THINGS_EXISTS_SIZE (Career.h)
# A tool limit, not a claim about the game. Refuse before expanding a malformed or unusually large authored squad.
MAX_NAMED_REGISTRY_ENTRIES = 10_000


class RegistryLimitError(ValueError):
    """The source-modelled registry exceeds this tool's expansion limit; no partial registry is returned."""


def squad_class(behaviour: int | None) -> str | None:
    """The squad UPhysicsManager::SpawnSquad makes for a unit behaviour: "relaxed", "normal" or None."""
    if behaviour is None or behaviour in NO_SQUAD:
        return None
    return "relaxed" if behaviour in RELAXED_SQUAD else "normal"


def first_behaviours(unit_definitions: Iterable[dict]) -> dict[str, int]:
    """Unit name -> behaviour of the first definition of that name (UPhysicsManager::Reload appends the units in file
    order and GetUnitData returns the first strcmp match). Rows are {"definition", "factorySelector"}."""
    out: dict[str, int] = {}
    for row in unit_definitions:
        out.setdefault(row["definition"], row["factorySelector"])
    return out


def strcmp_key(text: str) -> str:
    """A C string compares up to its first NUL; a stored thing name has none, a script string literal might."""
    return text.split("\0", 1)[0]


def effective_dies_on(things: list[dict]) -> dict[int, int]:
    """Thing ordinal -> the dies_on[] value at its slot when the start loop reads it (slotted records only)."""
    dies_on: dict[int, int] = {}
    out: dict[int, int] = {}
    slot = 0
    for t in things:
        if t["oid"] in READS_DIES_ON:
            dies_on[slot] = t["diesOn"]
        if t["slot"] is not None:
            if t["slot"] != slot:
                raise ValueError(f"thing {t['ordinal']} has slot {t['slot']} where LoadWorld would give {slot}")
            out[t["ordinal"]] = dies_on.get(slot, -1)
            slot += 1
    return out


def thing_outcome(t: dict, behaviours: dict[str, int]) -> dict:
    """What CWorld::LoadWorld and the thing's Init do with a named record: which objects join the list, and why not."""
    oid, init = t["oid"], t["init"]
    if t["slot"] is None:
        return {"joins": 0, "object": None, "reason": "no-slot",
                "rule": "the record took no things[] slot (its definition was not found, SpawnThing made nothing, or "
                        "it is a start in a base world), so it is never initialised"}
    if oid in NOT_COMPLEX:
        return {"joins": 0, "object": None, "reason": "not-a-complex-thing",
                "rule": "CTree and CWaypoint derive from CThing, whose Init names nothing"}
    if oid in (OID_UNIT, OID_BUILDING):
        behaviour = behaviours.get(t["definition"])
        squad = squad_class(behaviour)
        if squad is not None:
            return {"joins": 1, "object": "squad-member", "squad": squad,
                    "rule": "the unit's behaviour has a squad: LoadWorld makes a squad of one marked as the unit's, "
                            "and CSquad::Init gives the name to the member unit and clears the squad's"}
        if behaviour == UB_JEEP:
            return {"joins": 0, "object": None, "reason": "no-object",
                    "rule": "UB_JEEP: UPhysicsManager::SpawnThing makes nothing, yet the record takes a slot, so "
                            "LoadWorld would initialise a null thing"}
        return {"joins": 1, "object": "thing", "rule": "the unit's own Init reaches CComplexThing::Init"}
    if oid == OID_SQUAD:
        squad = squad_class(behaviours.get(t["definition"]))
        amount = max(init["squad"]["amount"], 0)
        attach = bool(init["attachScriptsToUnits"])  # None (version 45 and older) is the constructor's FALSE
        if squad == "normal" and not attach:
            return {"joins": 1, "object": "squad", "squad": squad,
                    "rule": "a CNormalSquad that does not attach scripts to units keeps its name; its members have "
                            "none"}
        return {"joins": amount, "object": "squad-members", "squad": squad, "members": amount,
                "rule": ("a CRelaxedSquad" if squad == "relaxed" else "a CNormalSquad that attaches scripts to units")
                + " gives the name to each of its members and clears its own"}
    return {"joins": 1, "object": "thing", "rule": "its Init reaches CComplexThing::Init"}


def build_registry(worlds: dict[str, dict], behaviours: dict[str, int]) -> dict:
    """Model LoadWorld's list: the base world's (BSWD) joins in slot order, then the real world's (RLWD).

    worlds holds decoded bodies keyed "BSWD"/"RLWD" (either may be absent). Returns {"entries": [...] in joining
    order, "outcomes": {(tag, ordinal): outcome}} for every named record. A base-world entry is conditional: it joins
    only if the career keeps its slot (careerBit) and its dies-on world (diesOn, -1 for none) is not before the level.
    """
    entries: list[dict] = []
    outcomes: dict[tuple[str, int], dict] = {}
    for tag in ("BSWD", "RLWD"):
        world = worlds.get(tag)
        if not world:
            continue
        things = world["things"]
        dies = effective_dies_on(things)  # also checks that the slots are LoadWorld's: in record order, from 0
        # slots rise with the record order, so record order is the start loop's order
        for t in things:
            if not t["init"]["name"]:
                continue
            outcome = thing_outcome(t, behaviours)
            outcome["world"], outcome["ordinal"], outcome["slot"] = tag, t["ordinal"], t["slot"]
            if tag == "BSWD" and t["slot"] is not None:
                outcome["keep"] = {"careerBit": t["slot"], "careerBitInRange": t["slot"] < CAREER_BASE_BITS,
                                   "diesOn": dies[t["ordinal"]]}
            outcome["orders"] = []
            members = outcome["object"] in ("squad-member", "squad-members")
            if outcome["joins"] > MAX_NAMED_REGISTRY_ENTRIES - len(entries):
                raise RegistryLimitError(f"{tag} thing {t['ordinal']}: named registry exceeds the tool limit of "
                                         f"{MAX_NAMED_REGISTRY_ENTRIES} entries")
            for member in range(outcome["joins"]):
                entry = {"order": len(entries), "name": t["init"]["name"], "world": tag, "ordinal": t["ordinal"],
                         "slot": t["slot"], "oid": t["oid"], "kind": t["kind"], "object": outcome["object"],
                         "member": member if members else None, "conditional": tag == "BSWD"}
                if tag == "BSWD":
                    entry["keep"] = outcome["keep"]
                outcome["orders"].append(entry["order"])
                entries.append(entry)
            outcomes[(tag, t["ordinal"])] = outcome
    return {"entries": entries, "outcomes": outcomes}


def find(entries: list[dict], name: str) -> dict:
    """What FindThingByName returns for name right after loading, given the registry's entries in joining order.

    status: "resolved" (the most recent entry of that name is a real-world one, so every career gets it),
    "career-dependent" (every entry of that name is a base-world one: the first the career kept, in candidate order,
    or nothing), "unresolved" (no entry has that name). candidates lists the entries of that name most recent first,
    the order FindThingByName meets them; for "resolved" the ones after the first are shadowed while it stays named.
    """
    key = strcmp_key(name)
    candidates = [e for e in reversed(entries) if e["name"] == key]
    if not candidates:
        return {"status": "unresolved", "entry": None, "candidates": []}
    status = "career-dependent" if candidates[0]["conditional"] else "resolved"
    return {"status": status, "entry": candidates[0], "candidates": candidates}


def find_by_walk(entries: list[dict], name: str, kept: Callable[[dict], bool] = lambda e: True) -> dict | None:
    """The same answer computed the loader's way, for cross-checking find(): build the list with front insertion
    (GenericSPtrSet::Add), then walk it from the front comparing C strings (CWorld::FindThingByName)."""
    linked: list[dict] = []
    for entry in entries:
        if kept(entry):
            linked.insert(0, entry)
    wanted = strcmp_key(name).encode("latin-1")
    for entry in linked:
        if entry["name"].encode("latin-1") == wanted:
            return entry
    return None


def runtime_names(calls: Iterable[dict]) -> list[dict]:
    """Literal SetName calls in one script's analysed calls (world_resources_decode.analyse_script): the names that
    script gives its own thing at run time. An empty name takes the thing off the list."""
    out = []
    for c in calls:
        if c["native"] != "SetName" or not c["args"]:
            continue
        arg = c["args"][0]
        out.append({"pc": c["pc"], "name": arg["value"] if arg is not None and isinstance(arg["value"], str) else None})
    return out
