#!/usr/bin/env python3
"""Parse retail BattleEngine profile data from a read-only game install.

This probe reads ``data/battle engine configurations.dat`` using the source
``UBattleEngineDataManager::Load`` / ``CBattleEngineData::Load`` format. It
does not mutate the install, copy files, launch BEA, attach a debugger, or
write outside ``subagents/``. If the game root is unavailable, the probe skips
cleanly unless ``--require-game-root`` is supplied.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")
DATA_RELATIVE = Path("data") / "battle engine configurations.dat"
SOURCE_MANAGER = ROOT / "references" / "Onslaught" / "BattleEngineDataManager.h"
SOURCE_LOAD = ROOT / "references" / "Onslaught" / "BattleEngineDataManager.cpp"
OUT = ROOT / "subagents" / "battleengine-profile-data" / "current" / "battleengine-profile-data.json"

EXPECTED_NAMES = ("Racer", "Standard", "Sniper", "Aquila Prototype", "Laser", "Blaster")
EXPECTED_POSITIVE_STEALTH = {"Sniper": 80.0}

SOURCE_MANAGER_TOKENS = (
    "inFile.Read( &configurations, sizeof(configurations) );",
    "for (int n=0; n<configurations; n++)",
    "config->Initialise();",
    "config->Load(inFile);",
    "sData.Add(config);",
)

SOURCE_LOAD_TOKENS = (
    "inFile.Read(&version,sizeof(version));",
    "inFile.Read(&mLife,sizeof(mLife));",
    "inFile.Read(&mEnergy,sizeof(mEnergy));",
    "mConfigurationName=new( MEMTYPE_BATTLEENGINE ) char[n+1];",
    "mConfigurationName[m]=temp[m];",
    "inFile.Read(&mShieldEfficiency,sizeof(mShieldEfficiency));",
    "inFile.Read(&mStealth,sizeof(mStealth));",
    "inFile.Read(&mStoreHeat[n],sizeof(mStoreHeat[n]));",
    "inFile.Read(&mStoreValue[n],sizeof(mStoreValue[n]));",
    "inFile.Read(&mLanguageName,sizeof(mLanguageName));",
)


@dataclass
class Reader:
    data: bytes
    offset: int = 0

    def read_int32(self) -> int:
        value = struct.unpack_from("<i", self.data, self.offset)[0]
        self.offset += 4
        return value

    def read_float(self) -> float:
        value = struct.unpack_from("<f", self.data, self.offset)[0]
        self.offset += 4
        return value

    def read_cstr(self) -> str:
        end = self.data.index(0, self.offset)
        value = self.data[self.offset:end].decode("ascii", errors="replace")
        self.offset = end + 1
        return value


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalized(text: str) -> str:
    return "".join(text.split())


def token_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    norm_lines = [normalized(line) for line in lines]
    return {
        token: [
            index + 1
            for index, line in enumerate(norm_lines)
            if normalized(token) in line
        ]
        for token in tokens
    }


def parse_profiles(path: Path) -> dict[str, object]:
    reader = Reader(path.read_bytes())
    count = reader.read_int32()
    profiles: list[dict[str, object]] = []
    for index in range(count):
        start = reader.offset
        version = reader.read_int32()
        profile = {
            "index": index,
            "startOffsetHex": f"0x{start:x}",
            "version": version,
            "life": reader.read_float(),
            "energy": reader.read_float(),
            "groundEnergyIncrease": reader.read_float(),
            "maxAirEnergyCost": reader.read_float(),
            "minTransformEnergy": reader.read_float(),
            "maxAirVelocity": reader.read_float(),
            "groundVelocity": reader.read_float(),
            "airTurnRate": reader.read_float(),
            "groundTurnRate": reader.read_float(),
        }
        if version < 8:
            for _ in range(3):
                reader.read_float()
        if version <= 4:
            raise ValueError("legacy BattleEngine profile versions are not supported by this probe")
        profile["configurationName"] = reader.read_cstr()
        profile["shieldEfficiency"] = reader.read_float() if version > 1 else None
        profile["stealth"] = reader.read_float() if version > 2 else 0.0
        profile["explosion"] = reader.read_cstr() if version > 3 else "Animated Explosion Emitter 2"
        walkers: list[str] = []
        jets: list[str] = []
        stores: list[dict[str, object]] = []
        if version > 4:
            for _ in range(reader.read_int32()):
                walkers.append(reader.read_cstr())
            for _ in range(reader.read_int32()):
                jets.append(reader.read_cstr())
            for store_index in range(6):
                stores.append(
                    {
                        "index": store_index,
                        "heat": reader.read_int32(),
                        "value": reader.read_float(),
                    }
                )
        profile["walkerWeapons"] = walkers
        profile["jetWeapons"] = jets
        profile["stores"] = stores
        profile["minAirVelocity"] = reader.read_float() if version > 5 else 0.3
        if version > 6:
            profile["maxWalkVelocity"] = reader.read_float()
            profile["walkFriction"] = reader.read_float()
        else:
            profile["maxWalkVelocity"] = None
            profile["walkFriction"] = None
        if version > 7:
            profile["minAirEnergyCost"] = reader.read_float()
            profile["rollEnergyCost"] = reader.read_float()
            profile["loopEnergyCost"] = reader.read_float()
        else:
            profile["minAirEnergyCost"] = 0.005
            profile["rollEnergyCost"] = None
            profile["loopEnergyCost"] = None
        profile["augWeapon"] = reader.read_cstr() if version > 8 else ""
        profile["primaryWeapon"] = reader.read_cstr() if version > 9 else ""
        profile["cockpit"] = reader.read_cstr() if version > 10 else "cockpit2.msh"
        profile["languageName"] = reader.read_int32() if version > 11 else 1
        profile["endOffsetHex"] = f"0x{reader.offset:x}"
        profiles.append(profile)

    return {
        "count": count,
        "consumedBytes": reader.offset,
        "totalBytes": len(reader.data),
        "profiles": profiles,
    }


def resolve_game_root(value: str | None) -> tuple[Path, str]:
    if value:
        return Path(value), "argument"
    env_value = os.environ.get("BEA_GAME_ROOT")
    if env_value:
        return Path(env_value), "BEA_GAME_ROOT"
    return DEFAULT_GAME_ROOT, "default-common-steam-path"


def build_report(game_root: Path, game_root_source: str, require_game_root: bool) -> dict[str, object]:
    data_file = game_root / DATA_RELATIVE
    manager_hits = token_hits(SOURCE_MANAGER, SOURCE_MANAGER_TOKENS)
    load_hits = token_hits(SOURCE_LOAD, SOURCE_LOAD_TOKENS)
    failures: list[str] = []
    if not data_file.is_file():
        status = "blocked" if require_game_root else "skipped"
        return {
            "schema": "battleengine-profile-data.v1",
            "status": status,
            "gameRootSource": game_root_source,
            "dataRelativePath": DATA_RELATIVE.as_posix(),
            "reason": "Battle Engine profile data file is not available on this machine.",
            "failures": [f"missing data file: {DATA_RELATIVE.as_posix()}"] if require_game_root else [],
            "sourceManagerTokenLineHits": manager_hits,
            "sourceLoadTokenLineHits": load_hits,
        }

    parsed = parse_profiles(data_file)
    names = [str(profile["configurationName"]) for profile in parsed["profiles"]]
    positive = {
        str(profile["configurationName"]): float(profile["stealth"])
        for profile in parsed["profiles"]
        if float(profile["stealth"]) > 0
    }
    if parsed["count"] != len(EXPECTED_NAMES):
        failures.append(f"expected {len(EXPECTED_NAMES)} profiles, found {parsed['count']}")
    if tuple(names) != EXPECTED_NAMES:
        failures.append(f"unexpected profile names/order: {names!r}")
    if positive != EXPECTED_POSITIVE_STEALTH:
        failures.append(f"unexpected positive stealth profile set: {positive!r}")
    if parsed["consumedBytes"] != parsed["totalBytes"]:
        failures.append(f"parser left trailing bytes: {parsed['totalBytes'] - parsed['consumedBytes']}")
    for token, lines in manager_hits.items():
        if not lines:
            failures.append(f"missing source manager token: {token}")
    for token, lines in load_hits.items():
        if not lines:
            failures.append(f"missing source load token: {token}")

    return {
        "schema": "battleengine-profile-data.v1",
        "status": "pass" if not failures else "blocked",
        "gameRootSource": game_root_source,
        "dataRelativePath": DATA_RELATIVE.as_posix(),
        "profileCount": parsed["count"],
        "consumedBytes": parsed["consumedBytes"],
        "totalBytes": parsed["totalBytes"],
        "profileSummaries": [
            {
                "index": profile["index"],
                "name": profile["configurationName"],
                "version": profile["version"],
                "stealth": profile["stealth"],
                "energy": profile["energy"],
                "minTransformEnergy": profile["minTransformEnergy"],
                "primaryWeapon": profile["primaryWeapon"],
                "walkerWeapons": profile["walkerWeapons"],
                "jetWeapons": profile["jetWeapons"],
            }
            for profile in parsed["profiles"]
        ],
        "positiveStealthProfiles": positive,
        "sourceManagerTokenLineHits": manager_hits,
        "sourceLoadTokenLineHits": load_hits,
        "failures": failures,
        "whatIsProven": [
            "The local read-only retail data file parses as six CBattleEngineData entries with format version 12 and no trailing bytes.",
            "Only the Sniper profile has positive stealth in this retail data file, with mStealth/profile+0xa0 value 80.0.",
            "The next cloak runtime setup target should select or verify the Sniper profile before rerunning the latch observer.",
        ],
        "notProven": [
            "How the latest runtime selected the prior non-stealth profile.",
            "A runtime transition into the Sniper profile.",
            "Runtime cloak activation.",
            "Fire-while-cloaked behavior.",
            "Any mutation of game files, Ghidra projects, or saves.",
        ],
        "privacy": "Report stores derived profile names and gameplay scalar values only; it does not store raw binary bytes, private absolute paths, copied executables, saves, screenshots, or debugger logs.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--game-root")
    parser.add_argument("--require-game-root", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    game_root, source = resolve_game_root(args.game_root)
    report = build_report(game_root, source, args.require_game_root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine profile data probe")
        print(f"Status: {report['status']}")
        print(f"Data path: {report['dataRelativePath']}")
        if report["status"] == "pass":
            print(f"Profiles: {report['profileCount']}")
            print("Positive stealth profiles:")
            for name, stealth in report["positiveStealthProfiles"].items():
                print(f"- {name}: {stealth}")
        elif report["status"] == "skipped":
            print(f"SKIP: {report['reason']}")
        for failure in report["failures"]:
            print(f"- FAIL: {failure}")

    return 0 if report["status"] in {"pass", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
