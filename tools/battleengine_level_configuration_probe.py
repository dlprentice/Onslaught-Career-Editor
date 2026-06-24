#!/usr/bin/env python3
"""Probe level resource configuration hints without mutating game files.

This probe reads a retail ``*_res_PC.aya`` level resource archive from the
local game install, inflates it in memory, and inspects the world-resource
chunk for Battle Engine configuration names. It writes only a derived summary
under ``subagents/`` and never copies or modifies the source archive.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from aya_archive_inventory import inflate_aya, parse_chunk_stream, parse_top_level_chunks  # noqa: E402

DEFAULT_GAME_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")
DEFAULT_LEVEL = 710
EXPECTED_CONFIG_NAMES = ("Standard", "Sniper", "Laser", "Blaster")
EXPECTED_BASE_WORLD_CONFIG = "Sniper"
EXPECTED_SCRIPT_NAME = "Level710script"
SOURCE_SCRIPT = ROOT / "game" / "data" / "MissionScripts" / "level710" / "Level710script.msl"
OUT = ROOT / "subagents" / "battleengine-level-configuration" / "current" / "battleengine-level-configuration.json"

SCRIPT_TOKENS = (
    'if(player.GetConfiguration() == "Sniper")',
    "PlayCharMessageWait(P_TATIANA, _710_CLOAK, 0.0);",
    "AddHelpMessage(_710_J_CLOAK);",
    'Print("Cloak with',
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize(text: str) -> str:
    return "".join(text.split())


def resolve_game_root(value: str | None) -> tuple[Path, str]:
    if value:
        return Path(value), "argument"
    env_value = os.environ.get("BEA_GAME_ROOT")
    if env_value:
        return Path(env_value), "BEA_GAME_ROOT"
    return DEFAULT_GAME_ROOT, "default-common-steam-path"


def chunk_payload(raw: bytes, chunk_offset: int, chunk_size: int) -> bytes:
    start = chunk_offset + 8
    return raw[start : start + chunk_size]


def read_u16(payload: bytes, offset: int) -> int:
    if offset + 2 > len(payload):
        raise ValueError(f"truncated u16 at offset {offset}")
    return int.from_bytes(payload[offset : offset + 2], "little", signed=False)


def read_i32(payload: bytes, offset: int) -> int:
    if offset + 4 > len(payload):
        raise ValueError(f"truncated i32 at offset {offset}")
    return int.from_bytes(payload[offset : offset + 4], "little", signed=True)


def parse_length_prefixed_config_table(payload: bytes, offset: int) -> tuple[list[str], int]:
    count = read_i32(payload, offset)
    cursor = offset + 4
    names: list[str] = []
    if count < 0 or count > 20:
        raise ValueError(f"unexpected Battle Engine configuration count {count} at offset {offset}")

    for _ in range(count):
        if cursor >= len(payload):
            raise ValueError(f"truncated configuration length at offset {cursor}")
        length = payload[cursor]
        cursor += 1
        if cursor + length > len(payload):
            raise ValueError(f"truncated configuration name at offset {cursor}")
        names.append(payload[cursor : cursor + length].decode("ascii", errors="replace"))
        cursor += length

    return names, cursor


def parse_world_header_config_table(payload: bytes) -> dict[str, object]:
    """Parse the BattleEngineConfigurations table loaded by CWorld__LoadWorldHeader.

    The layout is based on read-only Ghidra decompilation of
    CWorld__LoadWorldHeader: CWorld__LoadWorld reads a u16 world version,
    then the header reads three i32 values, then calls
    BattleEngineConfigurations__Load/Skip. For header versions greater than
    one, three trailing i32 values follow the config table; for versions
    greater than two, one additional i32 follows.
    """

    world_version = read_u16(payload, 0)
    header_version = read_i32(payload, 2)
    raw_header_dwords = [read_i32(payload, 6), read_i32(payload, 10)]
    config_offset = 14
    names, cursor = parse_length_prefixed_config_table(payload, config_offset)
    post_config_dwords: list[int] = []
    if header_version > 1:
        for _ in range(3):
            post_config_dwords.append(read_i32(payload, cursor))
            cursor += 4
    if header_version > 2:
        post_config_dwords.append(read_i32(payload, cursor))
        cursor += 4

    return {
        "worldVersion": world_version,
        "headerVersion": header_version,
        "rawHeaderDwords": raw_header_dwords,
        "battleEngineConfigurationOffset": config_offset,
        "battleEngineConfigurations": names,
        "postConfigDwords": post_config_dwords,
        "nextOffsetAfterHeader": cursor,
    }


def ascii_hits(payload: bytes, names: tuple[str, ...]) -> dict[str, list[int]]:
    hits: dict[str, list[int]] = {}
    for name in names:
        marker = name.encode("ascii")
        offsets: list[int] = []
        start = 0
        while True:
            pos = payload.find(marker, start)
            if pos < 0:
                break
            offsets.append(pos)
            start = pos + 1
        hits[name] = offsets
    return hits


def c_strings_near_names(payload: bytes, names: tuple[str, ...]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for name, offsets in ascii_hits(payload, names).items():
        for offset in offsets:
            before = payload.rfind(b"\x00", 0, offset)
            after = payload.find(b"\x00", offset)
            start = before + 1 if before >= 0 else offset
            end = after if after >= 0 else min(len(payload), offset + len(name))
            value = payload[start:end].decode("ascii", errors="replace")
            records.append({"name": name, "offset": offset, "string": value})
    return sorted(records, key=lambda item: int(item["offset"]))


def source_token_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    normalized_lines = [normalize(line) for line in lines]
    return {
        token: [
            index + 1
            for index, line in enumerate(normalized_lines)
            if normalize(token) in line
        ]
        for token in tokens
    }


def parse_wres(raw: bytes) -> dict[str, object]:
    top = parse_top_level_chunks(raw)
    top_by_tag = {chunk.tag: chunk for chunk in top}
    if "WRES" not in top_by_tag:
        raise ValueError("level resource has no WRES chunk")

    wres = top_by_tag["WRES"]
    wres_payload = chunk_payload(raw, wres.offset, wres.size)
    wres_children = parse_chunk_stream(wres_payload, base_offset=wres.offset + 8)
    if len(wres_children) != 1 or wres_children[0].tag != "WRLD":
        raise ValueError("WRES payload does not contain the expected single WRLD child")

    wrld = wres_children[0]
    wrld_payload = chunk_payload(raw, wrld.offset, wrld.size)
    wrld_children = parse_chunk_stream(wrld_payload, base_offset=wrld.offset + 8)
    child_records: list[dict[str, object]] = []
    payloads: dict[str, bytes] = {}
    for child in wrld_children:
        payload = chunk_payload(raw, child.offset, child.size)
        payloads[child.tag] = payload
        child_records.append(
            {
                "tag": child.tag,
                "size": child.size,
                "offsetHex": f"0x{child.offset:x}",
                "payloadOffsetHex": f"0x{child.offset + 8:x}",
            }
        )

    wdat = payloads.get("WDAT", b"")
    wdat_values: dict[str, int] = {}
    if len(wdat) >= 8:
        wdat_values = {
            "worldDataVersion": int.from_bytes(wdat[0:4], "little", signed=True),
            "levelNumber": int.from_bytes(wdat[4:8], "little", signed=True),
        }

    return {
        "topLevelTags": [chunk.tag for chunk in top],
        "wresSize": wres.size,
        "wrldSize": wrld.size,
        "wrldChildren": child_records,
        "wdat": wdat_values,
        "bswdHeader": parse_world_header_config_table(payloads.get("BSWD", b"")),
        "rlwdHeader": parse_world_header_config_table(payloads.get("RLWD", b"")),
        "bswdConfigHits": c_strings_near_names(payloads.get("BSWD", b""), EXPECTED_CONFIG_NAMES),
        "rlwdConfigHits": c_strings_near_names(payloads.get("RLWD", b""), EXPECTED_CONFIG_NAMES),
        "rlwdScriptHits": c_strings_near_names(payloads.get("RLWD", b""), (EXPECTED_SCRIPT_NAME,)),
    }


def build_report(game_root: Path, game_root_source: str, level: int, require_game_root: bool) -> dict[str, object]:
    relative_resource = Path("data") / "Resources" / f"{level}_res_PC.aya"
    resource_path = game_root / relative_resource
    token_hits = source_token_hits(SOURCE_SCRIPT, SCRIPT_TOKENS)
    failures: list[str] = []

    if not resource_path.is_file():
        status = "blocked" if require_game_root else "skipped"
        return {
            "schema": "battleengine-level-configuration.v1",
            "status": status,
            "level": level,
            "gameRootSource": game_root_source,
            "resourceRelativePath": relative_resource.as_posix(),
            "reason": "Battle Engine level resource archive is not available on this machine.",
            "scriptSource": relative(SOURCE_SCRIPT),
            "scriptTokenLineHits": token_hits,
            "failures": [f"missing resource archive: {relative_resource.as_posix()}"] if require_game_root else [],
        }

    raw = inflate_aya(resource_path)
    parsed = parse_wres(raw)

    bswd_names = {str(hit["name"]) for hit in parsed["bswdConfigHits"]}
    bswd_header_names = [str(name) for name in parsed["bswdHeader"]["battleEngineConfigurations"]]
    rlwd_header_names = [str(name) for name in parsed["rlwdHeader"]["battleEngineConfigurations"]]
    rlwd_all_names = [str(hit["name"]) for hit in parsed["rlwdConfigHits"]]
    rlwd_table_names = rlwd_all_names[: len(EXPECTED_CONFIG_NAMES)]
    script_names = {str(hit["name"]) for hit in parsed["rlwdScriptHits"]}
    if parsed["wdat"].get("levelNumber") != level:
        failures.append(f"WDAT level number mismatch: {parsed['wdat']!r}")
    if EXPECTED_BASE_WORLD_CONFIG not in bswd_names:
        failures.append(f"BSWD did not expose {EXPECTED_BASE_WORLD_CONFIG!r}: {sorted(bswd_names)!r}")
    if bswd_header_names != [EXPECTED_BASE_WORLD_CONFIG]:
        failures.append(f"BSWD header configuration table mismatch: {bswd_header_names!r}")
    if tuple(rlwd_header_names) != EXPECTED_CONFIG_NAMES:
        failures.append(f"RLWD header configuration table mismatch: {rlwd_header_names!r}")
    if tuple(rlwd_table_names) != EXPECTED_CONFIG_NAMES:
        failures.append(f"RLWD configuration table mismatch: {rlwd_all_names!r}")
    if EXPECTED_SCRIPT_NAME not in script_names:
        failures.append(f"RLWD did not expose {EXPECTED_SCRIPT_NAME!r}: {sorted(script_names)!r}")
    for token, lines in token_hits.items():
        if not lines:
            failures.append(f"missing Level710 script token: {token}")

    return {
        "schema": "battleengine-level-configuration.v1",
        "status": "pass" if not failures else "blocked",
        "level": level,
        "gameRootSource": game_root_source,
        "resourceRelativePath": relative_resource.as_posix(),
        "rawSize": len(raw),
        "scriptSource": relative(SOURCE_SCRIPT),
        "scriptTokenLineHits": token_hits,
        "wres": parsed,
        "rlwdConfigurationTable": rlwd_table_names,
        "failures": failures,
        "whatIsProven": [
            "The local read-only level 710 resource archive inflates and contains WRES/WRLD world data.",
            "WDAT identifies the resource as level 710.",
            "The base-world header BattleEngineConfigurations table contains only Sniper.",
            "The runtime-level header BattleEngineConfigurations table contains Standard/Sniper/Laser/Blaster.",
            "The runtime-level world data contains the Level710script reference.",
            "The tracked mission script gates cloak tutorial text on player.GetConfiguration() == \"Sniper\".",
        ],
        "notProven": [
            "Any alternate per-unit serialized numeric configuration-id offset beyond the initial-spawn string-resolution path.",
            "A runtime transition into Sniper in the retail executable.",
            "Runtime cloak activation.",
            "Firing while cloaked.",
        ],
    }


def write_report(report: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", help="Battle Engine Aquila install root. Defaults to BEA_GAME_ROOT or the common Steam path.")
    parser.add_argument("--level", type=int, default=DEFAULT_LEVEL)
    parser.add_argument("--json-out", default=str(OUT))
    parser.add_argument("--check", action="store_true", help="Fail when expected local evidence is absent or mismatched.")
    parser.add_argument("--require-game-root", action="store_true", help="Treat a missing game install as failure instead of skip.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    game_root, source = resolve_game_root(args.game_root)
    report = build_report(game_root, source, args.level, args.require_game_root)
    write_report(report, Path(args.json_out))

    print("BattleEngine level configuration probe")
    print(f"Status: {report['status']}")
    print(f"Level: {report['level']}")
    print(f"Resource: {report['resourceRelativePath']}")
    if "wres" in report:
        wres = report["wres"]
        print(f"WDAT: {wres['wdat']}")
        print("BSWD header configuration table:", ", ".join(wres["bswdHeader"]["battleEngineConfigurations"]) or "(none)")
        print("RLWD header configuration table:", ", ".join(wres["rlwdHeader"]["battleEngineConfigurations"]) or "(none)")
        print("BSWD configuration hits:", ", ".join(hit["name"] for hit in wres["bswdConfigHits"]) or "(none)")
        print("RLWD configuration table:", ", ".join(report["rlwdConfigurationTable"]) or "(none)")
        print("RLWD all configuration-name hits:", ", ".join(hit["name"] for hit in wres["rlwdConfigHits"]) or "(none)")
    for failure in report.get("failures", []):
        print(f"FAIL: {failure}")

    if args.check and report["status"] == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
