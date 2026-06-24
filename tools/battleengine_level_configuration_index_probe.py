#!/usr/bin/env python3
"""Index Battle Engine configuration tables across local level resources.

This probe reads the user's local Battle Engine Aquila install as read-only
source material. It inflates numeric ``*_res_PC.aya`` archives in memory,
parses ``WRES -> WRLD`` world-resource headers, and records only derived
configuration-name tables under ``subagents/``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from aya_archive_inventory import inflate_aya, parse_chunk_stream, parse_top_level_chunks  # noqa: E402
from battleengine_level_configuration_probe import (  # noqa: E402
    chunk_payload,
    parse_world_header_config_table,
    resolve_game_root,
)

OUT = ROOT / "subagents" / "battleengine-level-configuration-index" / "current" / "battleengine-level-configuration-index.json"
EXPECTED_BASE_SNIPER_LEVELS = [710, 720, 731, 732]
RESOURCE_NAME_RE = re.compile(r"^(\d+)_res_PC\.aya$", re.IGNORECASE)


def parse_level_resource(resource_path: Path, resources_root: Path) -> dict[str, object] | None:
    match = RESOURCE_NAME_RE.match(resource_path.name)
    if not match:
        return None

    level_from_name = int(match.group(1))
    raw = inflate_aya(resource_path)
    top = parse_top_level_chunks(raw)
    wres = next((chunk for chunk in top if chunk.tag == "WRES"), None)
    if wres is None:
        return None

    wres_payload = chunk_payload(raw, wres.offset, wres.size)
    wres_children = parse_chunk_stream(wres_payload, base_offset=wres.offset + 8)
    wrld = next((chunk for chunk in wres_children if chunk.tag == "WRLD"), None)
    if wrld is None:
        return None

    wrld_payload = chunk_payload(raw, wrld.offset, wrld.size)
    wrld_children = parse_chunk_stream(wrld_payload, base_offset=wrld.offset + 8)
    payloads = {child.tag: chunk_payload(raw, child.offset, child.size) for child in wrld_children}

    wdat = payloads.get("WDAT", b"")
    wdat_values: dict[str, int] = {}
    if len(wdat) >= 8:
        wdat_values = {
            "worldDataVersion": int.from_bytes(wdat[0:4], "little", signed=True),
            "levelNumber": int.from_bytes(wdat[4:8], "little", signed=True),
        }

    bswd_header = parse_world_header_config_table(payloads["BSWD"]) if "BSWD" in payloads else None
    rlwd_header = parse_world_header_config_table(payloads["RLWD"]) if "RLWD" in payloads else None
    bswd_configs = list(bswd_header["battleEngineConfigurations"]) if bswd_header else []
    rlwd_configs = list(rlwd_header["battleEngineConfigurations"]) if rlwd_header else []
    if not bswd_configs and not rlwd_configs:
        return None

    return {
        "level": level_from_name,
        "resourceRelativePath": resource_path.relative_to(resources_root.parent.parent).as_posix(),
        "wdat": wdat_values,
        "bswdConfigurations": bswd_configs,
        "rlwdConfigurations": rlwd_configs,
        "bswdHeaderVersion": bswd_header["headerVersion"] if bswd_header else None,
        "rlwdHeaderVersion": rlwd_header["headerVersion"] if rlwd_header else None,
        "hasBaseSniper": "Sniper" in bswd_configs,
        "hasRuntimeSniperTable": "Sniper" in rlwd_configs,
    }


def build_report(game_root: Path, game_root_source: str, require_game_root: bool) -> dict[str, object]:
    resources_root = game_root / "data" / "Resources"
    if not resources_root.is_dir():
        status = "blocked" if require_game_root else "skipped"
        return {
            "schema": "battleengine-level-configuration-index.v1",
            "status": status,
            "gameRootSource": game_root_source,
            "reason": "Battle Engine resource directory is not available on this machine.",
            "resourceRootRelativePath": "data/Resources",
            "failures": ["missing resource directory: data/Resources"] if require_game_root else [],
        }

    records: list[dict[str, object]] = []
    parse_errors: list[dict[str, str]] = []
    for resource_path in sorted(resources_root.glob("*_res_PC.aya")):
        if not RESOURCE_NAME_RE.match(resource_path.name):
            continue
        try:
            record = parse_level_resource(resource_path, resources_root)
            if record is not None:
                records.append(record)
        except Exception as exc:  # pragma: no cover - corpus diagnostics
            parse_errors.append({"resource": resource_path.name, "error": str(exc)})

    base_sniper_levels = [int(record["level"]) for record in records if record["hasBaseSniper"]]
    runtime_sniper_levels = [int(record["level"]) for record in records if record["hasRuntimeSniperTable"]]
    by_base_config: dict[str, list[int]] = {}
    for record in records:
        for name in record["bswdConfigurations"]:
            by_base_config.setdefault(str(name), []).append(int(record["level"]))

    failures: list[str] = []
    if parse_errors:
        failures.append(f"parse errors: {parse_errors!r}")
    if base_sniper_levels != EXPECTED_BASE_SNIPER_LEVELS:
        failures.append(f"base Sniper level mismatch: {base_sniper_levels!r}")
    if 710 not in runtime_sniper_levels:
        failures.append("level 710 missing from runtime Sniper table levels")

    return {
        "schema": "battleengine-level-configuration-index.v1",
        "status": "pass" if not failures else "blocked",
        "gameRootSource": game_root_source,
        "resourceRootRelativePath": "data/Resources",
        "levelRecordCount": len(records),
        "baseSniperLevels": base_sniper_levels,
        "runtimeSniperTableLevels": runtime_sniper_levels,
        "baseConfigurationsByName": dict(sorted(by_base_config.items())),
        "records": records,
        "parseErrors": parse_errors,
        "failures": failures,
        "whatIsProven": [
            "The local numeric level resource corpus can be inflated and scanned for WRES/WRLD BattleEngineConfigurations tables.",
            "Only levels 710, 720, 731, and 732 have Sniper in the base-world configuration table on this install.",
            "Several later levels include Sniper in the runtime-level configuration table, but not necessarily as the base initial configuration.",
        ],
        "notProven": [
            "Runtime selection of any configuration in a managed BEA process.",
            "Cloak activation.",
            "Fire-while-cloaked behavior.",
        ],
    }


def write_report(report: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", help="Battle Engine Aquila install root. Defaults to BEA_GAME_ROOT or the common Steam path.")
    parser.add_argument("--json-out", default=str(OUT))
    parser.add_argument("--check", action="store_true", help="Fail when expected local evidence is absent or mismatched.")
    parser.add_argument("--require-game-root", action="store_true", help="Treat a missing game install as failure instead of skip.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    game_root, source = resolve_game_root(args.game_root)
    report = build_report(game_root, source, args.require_game_root)
    write_report(report, Path(args.json_out))

    print("BattleEngine level configuration index probe")
    print(f"Status: {report['status']}")
    print(f"Resource root: {report['resourceRootRelativePath']}")
    if "levelRecordCount" in report:
        print(f"Levels with configuration tables: {report['levelRecordCount']}")
        print("Base Sniper levels:", ", ".join(str(level) for level in report["baseSniperLevels"]) or "(none)")
        print("Runtime Sniper table levels:", ", ".join(str(level) for level in report["runtimeSniperTableLevels"]) or "(none)")
    for failure in report.get("failures", []):
        print(f"FAIL: {failure}")

    if args.check and report["status"] == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
