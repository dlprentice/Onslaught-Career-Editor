#!/usr/bin/env python3
"""Validate Wave463 particle manager / particle set static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave463-particle-manager-current"
COMMON_TAGS = {"static-reaudit", "particle-manager-wave463", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 17,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 17,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = EXPECTED_DRY.copy()


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004cae50": target(
        "CParticle__Destroy",
        "void __fastcall CParticle__Destroy(void * particle)",
        ["Wave463 correction", "+0x88 resource block", "vfunc +0x38", "owner handle at +0x58"],
        ["particle-node", "resource-free", "signature-corrected", "comment-hardened"],
        ["CDXMemoryManager__Free", "CEngine__RemoveNodeFromActiveList", "+ 0x88"],
    ),
    "0x004caed0": target(
        "CParticleManager__SetParticleResource",
        "bool __thiscall CParticleManager__SetParticleResource(void * this, int resource_size)",
        ["Wave463 correction", "particle +0x88", "OID__AllocObject", "resource_size"],
        ["particle-resource", "allocation", "signature-corrected", "comment-hardened"],
        ["OID__AllocObject", "0xc2", "+ 0x88"],
    ),
    "0x004caf60": target(
        "CParticleManager__CleanupHandles",
        "void __cdecl CParticleManager__CleanupHandles(void)",
        ["Wave463 correction", "DAT_0082b3e4", "+0xb4", "+0xa4"],
        ["effect-handle", "cleanup", "signature-corrected", "comment-hardened"],
        ["DAT_0082b3e4", "+ 0xb4", "CDXMemoryManager__Free"],
    ),
    "0x004cb0e0": target(
        "CParticleManager__Init",
        "void * __fastcall CParticleManager__Init(void * manager)",
        ["Wave463 correction", "0x200-entry particle pool", "0xd8-byte particle nodes", "DAT_0082b3ec"],
        ["particle-pool", "manager-init", "signature-corrected", "comment-hardened"],
        ["0x1b004", "0xd8", "DAT_0082b3ec"],
    ),
    "0x004cb1b0": target(
        "CParticleManager__Shutdown",
        "void __fastcall CParticleManager__Shutdown(void * manager)",
        ["Wave463 correction", "0xd8-byte particle array", "callback cleanup", "DAT_0082b3ec"],
        ["particle-pool", "manager-shutdown", "signature-corrected", "comment-hardened"],
        ["CDXLandscape__DestroyArrayWithCallback", "CDXMemoryManager__Free", "DAT_0082b3ec"],
    ),
    "0x004cb210": target(
        "CParticleManager__Update",
        "int __thiscall CParticleManager__Update(void * this, float delta_time, int update_context)",
        ["Wave463 correction", "clears handle activity/backlinks", "prunes dead particles", "CParticleManager__CleanupHandles"],
        ["manager-update", "particle-update", "signature-corrected", "comment-hardened"],
        ["CParticleManager__UpdateParticles", "CParticleManager__PruneDeadParticles", "CParticleManager__CleanupHandles"],
    ),
    "0x004cb300": target(
        "CParticleManager__InterpolatePositions",
        "void __cdecl CParticleManager__InterpolatePositions(void)",
        ["Wave463 correction", "DAT_0082b3e8", "10000.0 sentinel", "DAT_008a9e44"],
        ["effect-handle", "interpolation", "signature-corrected", "comment-hardened"],
        ["DAT_0082b3e8", "DAT_008a9e44", "10000.0"],
    ),
    "0x004cb3d0": target(
        "CParticleManager__CreateEffect",
        "void __stdcall CParticleManager__CreateEffect(void * manager, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)",
        ["Wave463 correction", "0xb8 effect handle", "DAT_0082b3e4", "looping/high-priority handle flags"],
        ["effect-create", "effect-handle", "signature-corrected", "comment-hardened"],
        ["CParticleManager__AllocateParticle", "0xb8", "DAT_0082b3e4"],
    ),
    "0x004cb5c0": target(
        "CParticleManager__AllocateParticle",
        "void * __thiscall CParticleManager__AllocateParticle(void * this, void * particle_set, int force_allocate)",
        ["Wave463 correction", "free list", "LOD skip thresholds", "vfunc +0x24"],
        ["particle-pool", "lod-threshold", "signature-corrected", "comment-hardened"],
        ["CGame__IsMultiplayer", "DAT_0082b3e0", "0x200"],
    ),
    "0x004cb920": target(
        "CParticleManager__UpdateParticleAndRecycleIfDead",
        "void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle, int unused_context)",
        ["Wave463 correction", "attached handle activity/backlink", "vfunc +0x28", "recycles dead particles"],
        ["particle-update", "particle-recycle", "signature-corrected", "comment-hardened"],
        ["Vec3__SetXYZ", "+ 0x58", "CParticle__Destroy"],
    ),
    "0x004cba30": target(
        "CParticleManager__ProjectPointToTerrainWithRadiusClamp",
        "int __stdcall CParticleManager__ProjectPointToTerrainWithRadiusClamp(void * world_pos, float radius, void * out_pos)",
        ["Wave463 correction", "static-shadow terrain height", "out_pos.z", "height - radius"],
        ["terrain-projection", "shadow-height", "signature-corrected", "comment-hardened"],
        ["CStaticShadows__SampleShadowHeightBilinear", "return 1", "return 0"],
    ),
    "0x004cba90": target(
        "CParticleManager__ComputeMinCameraDistanceSqForParticle",
        "double __stdcall CParticleManager__ComputeMinCameraDistanceSqForParticle(void * particle)",
        ["Wave463 correction", "camera-distance-squared", "camera 0/1 in multiplayer", "+0x58"],
        ["camera-distance", "particle-lod", "signature-corrected", "comment-hardened"],
        ["CGame__GetCamera", "1e+07", "+ 0x58"],
    ),
    "0x004cbca0": target(
        "CParticleManager__UpdateParticles",
        "void __cdecl CParticleManager__UpdateParticles(void * active_head)",
        ["Wave463 correction", "active particle list", "vfunc +0x54", "DAT_009c63fc"],
        ["particle-update", "active-list", "signature-corrected", "comment-hardened"],
        ["DAT_009c63fc", "+ 0x58", "+ 0x60"],
    ),
    "0x004cbe30": target(
        "CParticleManager__PruneDeadParticles",
        "int __fastcall CParticleManager__PruneDeadParticles(void * manager)",
        ["Wave463 correction", "manager +0x1c", "death-flagged particles", "free list at manager +0x8"],
        ["particle-prune", "particle-recycle", "signature-corrected", "comment-hardened"],
        ["CParticle__Destroy", "+ 0x68", "+ 0x6c"],
    ),
    "0x004cbff0": target(
        "CParticleManager__DestroyParticleList",
        "void __fastcall CParticleManager__DestroyParticleList(void * list_head_ptr)",
        ["Wave463 correction", "head-linked particle list", "vfunc slot 0", "delete flag 1"],
        ["particle-list", "destructor", "signature-corrected", "comment-hardened"],
        ["(**(code **)*", "(1)", "puVar2[0xe]"],
    ),
    "0x004cc020": target(
        "CParticleSet__CreateByType",
        "void * __thiscall CParticleSet__CreateByType(void * this, char * set_name, int type_id, void * context)",
        ["Wave463 correction", "sorted name lookup", "type id", "DAT_0082b450"],
        ["particle-set", "factory", "signature-corrected", "comment-hardened"],
        ["OID__AllocObject", "stricmp", "PTR_VFuncSlot_00_004ccb40"],
    ),
    "0x004cc850": target(
        "CParticleSet__Init",
        "void __fastcall CParticleSet__Init(void * particle_set)",
        ["Wave463 correction", "+0x3c", "+0x54", "base particle-set vtable"],
        ["particle-set", "initializer", "signature-corrected", "comment-hardened"],
        ["PTR_LAB_005ddad4", "+ 0x3c", "+ 0x54"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004cae50", "0x0046cc82", "CGame__ShutdownRestartLoop"),
    ("0x004caed0", "0x004c3665", "CEngine__ConfigureParticleBurstForDistance"),
    ("0x004caf60", "0x0046ccb7", "CGame__ShutdownRestartLoop"),
    ("0x004cb0e0", "0x004cb644", "CParticleManager__AllocateParticle"),
    ("0x004cb1b0", "0x0046ccc8", "CGame__ShutdownRestartLoop"),
    ("0x004cb210", "0x00466c0f", "CFrontEnd__Process"),
    ("0x004cb300", "0x0053e8ab", "CDXEngine__Render"),
    ("0x004cb3d0", "0x0053eb6a", "CDXEngine__Render"),
    ("0x004cb5c0", "0x004cb402", "CParticleManager__CreateEffect"),
    ("0x004cb920", "0x004c207e", "<no_function>"),
    ("0x004cba30", "0x004c5114", "<no_function>"),
    ("0x004cba90", "0x004c0a65", "<no_function>"),
    ("0x004cbca0", "0x004cb28a", "CParticleManager__Update"),
    ("0x004cbe30", "0x004cb2c8", "CParticleManager__Update"),
    ("0x004cbff0", "0x00469237", "CFrontEnd__ReleaseParticleHudWaypointResources"),
    ("0x004cc020", "0x004cd97d", "CParticleSet__LoadFromArchive"),
    ("0x004cc850", "0x004cc0c7", "CParticleSet__CreateByType"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime rendering proven",
    "exact layout proven",
    "source identity proven",
    "fully re'ed",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"updated=\d+.*bad=\d+", text)
    if not match:
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(0))}


def check_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    actual = parse_summary(read_text(path))
    if not actual:
        failures.append(f"{path.name}: missing SUMMARY")
        return
    for key, value in expected.items():
        if actual.get(key) != value:
            failures.append(f"{path.name}: expected {key}={value}, got {actual.get(key)}")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_metadata.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"post_metadata.tsv: missing {address}")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    seen: dict[str, set[str]] = {}
    for row in rows:
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        seen.setdefault(row.get("address", ""), set()).update(tags)
    for address, expected in TARGETS.items():
        actual = seen.get(normalize_address(address), set())
        for tag in expected["tags"]:
            if tag not in actual:
                failures.append(f"{address}: missing tag {tag}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {(row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post decompile export")
            continue
        for token in expected["decompileTokens"]:
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    return ("FAIL" if failures else "PASS", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Accepted for npm-script consistency")
    parser.add_argument("--base", type=Path, default=BASE, help="Wave463 artifact directory")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
