#!/usr/bin/env python3
"""Validate Wave516 CThing core static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave516-cthing-core-004f33e0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cthing_core_wave516_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "cthing-core-wave516",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime behavior proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004f33e0": target(
        "CThing__ctor_base",
        "void * __fastcall CThing__ctor_base(void * this)",
        ("CThing constructor", "CMapWhoEntry", "+0x30/+0x38", "0x0083da30"),
        {"constructor", "cthing", "source-parity"},
        ("void * __fastcall", "CMapWhoEntry__Invalidate", "DAT_0083da30"),
    ),
    "0x004f3480": target(
        "CThing__scalar_deleting_dtor",
        "void * __thiscall CThing__scalar_deleting_dtor(void * this, byte delete_flags)",
        ("scalar deleting destructor", "delete_flags", "CThing__dtor_base", "CDXMemoryManager__Free"),
        {"cthing", "destructor", "vtable-slot-1"},
        ("void * __thiscall", "delete_flags", "CThing__dtor_base", "CDXMemoryManager__Free"),
    ),
    "0x004f34a0": target(
        "CThing__Init",
        "void __thiscall CThing__Init(void * this, void * init)",
        ("CThing::Init-style", "RET 0x4", "map-who", "collision-seeking"),
        {"cthing", "init", "map-who", "source-parity"},
        ("void __thiscall", "CMapWhoEntry__SetPosition", "+ 0x8c", "CSPtrSet__AddToHead"),
    ),
    "0x004f35d0": target(
        "CThing__InitRenderThing",
        "void __fastcall CThing__InitRenderThing(void * this)",
        ("render-object initialization", "+0x20", "this+0x30"),
        {"cthing", "init", "render", "vtable-slot"},
        ("void __fastcall", "CResourceDescriptorTable__InstantiateChain", "+ 0x30"),
    ),
    "0x004f3600": target(
        "CThing__Shutdown",
        "void __fastcall CThing__Shutdown(void * this)",
        ("shutdown path", "world thing set", "big-things", "scalar-deleting destructor"),
        {"cthing", "shutdown", "source-parity", "world-list"},
        ("void __fastcall", "CMonitor__Shutdown_Core", "+ 4"),
    ),
    "0x004f3640": target(
        "CThing__dtor_base",
        "void __fastcall CThing__dtor_base(void * this)",
        ("destructor-base", "+0x38", "+0x30", "map-who entry"),
        {"cthing", "destructor", "source-parity"},
        ("void __fastcall", "CMapWhoEntry__RemoveFromMap", "CMonitor__Shutdown"),
    ),
    "0x004f36d0": target(
        "CThing__Render",
        "void __thiscall CThing__Render(void * this, uint render_flags)",
        ("render_flags", "flag 0x20", "TF_DONT_RENDER", "debug cuboid"),
        {"cthing", "render", "source-parity", "vtable-slot"},
        ("void __thiscall", "render_flags", "CThing__DrawDebugCuboid"),
    ),
    "0x004f3710": target(
        "CThing__RenderImposter",
        "void __fastcall CThing__RenderImposter(void * this)",
        ("imposter-render", "this+0x30", "TF_DONT_RENDER"),
        {"cthing", "imposter", "render", "vtable-slot"},
        ("void __fastcall", "+ 0x30", "+ 0xc"),
    ),
    "0x004f3730": target(
        "CThing__HandleEvent",
        "void __thiscall CThing__HandleEvent(void * this, void * event)",
        ("event dispatcher", "2000", "0x7d2", "StartDieProcess"),
        {"cthing", "event", "source-parity", "vtable-slot"},
        ("void __thiscall", "event", "0x7d2"),
    ),
    "0x004f37c0": target(
        "CThing__DrawDebugCuboid",
        "void __fastcall CThing__DrawDebugCuboid(void * this)",
        ("debug-volume", "identity matrix", "green outer box", "white radius box"),
        {"cthing", "debug-render", "source-parity"},
        ("void __fastcall", "CThing__RenderDebugVolumeOverlay", "0xff00ff00", "0xffffffff"),
    ),
    "0x004f3940": target(
        "CThing__GetBoundingRadius",
        "double __fastcall CThing__GetBoundingRadius(void * this)",
        ("bounding-radius", "+0x24 radius", "GetRadius", "x87 float return"),
        {"bounds", "cthing", "render", "source-parity"},
        ("double __fastcall", "+ 0x24", "+ 0x40"),
    ),
    "0x004f3970": target(
        "CThing__SetObjective",
        "void __thiscall CThing__SetObjective(void * this, int enabled)",
        ("enabled", "0x00855140", "flag 0x20"),
        {"cthing", "objective", "source-parity", "world-list"},
        ("void __thiscall", "enabled", "0x20"),
    ),
    "0x004f39b0": target(
        "CThing__UpdatePosition",
        "void __fastcall CThing__UpdatePosition(void * this)",
        ("owner correction", "not a CUnit debug-trace helper", "this+0x30"),
        {"cthing", "owner-correction", "position", "source-parity"},
        ("void __fastcall", "+ 0x30"),
    ),
    "0x004f39c0": target(
        "CThing__InitCollisionSeekingThing",
        "void __thiscall CThing__InitCollisionSeekingThing(void * this, void * init_collision)",
        ("InitCollisionSeekingThing", "0x38-byte", "thing.cpp line 0x136", "mesh collision type 2 to 1"),
        {"collision", "cthing", "owner-correction", "source-parity"},
        ("void __thiscall", "init_collision", "OID__AllocObject(0x38,0xb", "CConsole__Printf"),
    ),
    "0x004f3a50": target(
        "CCSPersistentThing__scalar_deleting_dtor",
        "void * __thiscall CCSPersistentThing__scalar_deleting_dtor(void * this, byte delete_flags)",
        ("CCSPersistentThing scalar deleting destructor", "delete_flags", "CCSPersistentThing__dtor_base"),
        {"collision", "destructor", "persistent-collision"},
        ("void * __thiscall", "delete_flags", "CCSPersistentThing__dtor_base"),
    ),
    "0x004f3a70": target(
        "CCSPersistentThing__dtor_base",
        "void __fastcall CCSPersistentThing__dtor_base(void * this)",
        ("destructor-base", "this+0x24", "CCollisionSeekingRound__Destructor"),
        {"collision", "destructor", "persistent-collision"},
        ("void __fastcall", "CMonitor__Shutdown", "CCollisionSeekingRound__Destructor"),
    ),
    "0x004f3ac0": target(
        "CThing__GetCentrePos",
        "void __thiscall CThing__GetCentrePos(void * this, void * out_pos)",
        ("owner correction", "GetCentrePos", "out_pos", "targeting"),
        {"cthing", "owner-correction", "position", "source-parity", "targeting"},
        ("void __thiscall", "out_pos", "+ 0x1c"),
    ),
    "0x004f3c50": target(
        "CThing__StickToGround",
        "void __fastcall CThing__StickToGround(void * this)",
        ("StickToGround", "terrain/ground height", "render position"),
        {"cthing", "ground", "position", "source-parity"},
        ("void __fastcall", "CStaticShadows__SampleShadowHeightBilinear", "+ 0x24"),
    ),
    "0x004f3cb0": target(
        "CThing__MoveTo",
        "void __thiscall CThing__MoveTo(void * this, void * pos)",
        ("MoveTo", "RET 0x4", "pos", "this+0x1c"),
        {"cthing", "movement", "position", "source-parity"},
        ("void __thiscall", "pos", "+ 0x1c"),
    ),
    "0x004f3ce0": target(
        "CThing__Teleport",
        "void __thiscall CThing__Teleport(void * this, void * pos)",
        ("Teleport", "RET 0x4", "MoveTo-style virtual slot", "+0x4c"),
        {"cthing", "movement", "position", "source-parity"},
        ("void __thiscall", "pos", "+ 0x4c"),
    ),
    "0x004f3d10": target(
        "CThing__GetPersistentCollisionSeekingThing",
        "void * __fastcall CThing__GetPersistentCollisionSeekingThing(void * this)",
        ("GetCSPT-style", "this+0x38", "persistent collision-seeking"),
        {"collision", "cthing", "owner-correction", "source-parity"},
        ("void * __fastcall", "+ 0x38", "+ 0x10"),
    ),
    "0x004f3de0": target(
        "CThing__IsOverWater",
        "int __fastcall CThing__IsOverWater(void * this)",
        ("water/ground relation", "0x006fbdfc", "terrain/ground height"),
        {"cthing", "source-parity", "terrain", "water"},
        ("int __fastcall", "DAT_006fbdfc", "+ 0x1c"),
    ),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave516_dry.log": "SUMMARY updated=0 skipped=22 renamed=0 would_rename=15 missing=0 bad=0",
    "apply_wave516_apply.log": "SUMMARY updated=22 skipped=0 renamed=15 would_rename=0 missing=0 bad=0",
    "apply_wave516_verify_dry.log": "SUMMARY updated=0 skipped=22 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "Wave516",
    "22",
    "CThing__ctor_base",
    "CThing__InitCollisionSeekingThing",
    "CThing__GetPersistentCollisionSeekingThing",
    "2433",
    "1403",
    "runtime object lifecycle behavior",
    "rebuild parity",
)


def normalize_addr(address: str) -> str:
    address = (address or "").strip().lower()
    if not address or address.startswith("<"):
        return address
    body = address[2:] if address.startswith("0x") else address
    return f"0x{int(body, 16):08x}"


def compact_text(value: str) -> str:
    return " ".join((value or "").replace("\t", " ").replace("\r", " ").replace("\n", " ").split())


def compact_token(value: str) -> str:
    return "".join(compact_text(value).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact_token(token) in compact_token(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr"):
            if key in row and row[key]:
                row[key] = normalize_addr(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def find_decomp_file(decomp_dir: Path, address: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    return candidates[0]


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str]:
    wanted = normalize_addr(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    raise AssertionError(f"missing row for {address}")


def validate_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        require(row["status"] == "OK", f"{address} status mismatch: {row['status']}")
        require(row["name"] == expected["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        comment = compact_text(row["comment"])
        for token in expected["comment_tokens"]:
            require(token_present(comment, str(token)), f"{address} comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            require(not token_present(comment, token), f"{address} comment contains overclaim token {token!r}")


def validate_tags(base: Path) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        tags = {tag.strip() for tag in row["tags"].replace(",", ";").split(";") if tag.strip()}
        missing = expected["tags"] - tags
        require(not missing, f"{address} missing tags: {sorted(missing)}")


def validate_decompile(base: Path) -> None:
    decomp_dir = base / "post_decomp"
    require(decomp_dir.exists(), f"missing decompile dir: {decomp_dir}")
    for address, expected in TARGETS.items():
        text = find_decomp_file(decomp_dir, address).read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token_present(text, str(token)), f"{address} decompile missing token {token!r}")


def validate_counts(base: Path) -> None:
    require(len(read_tsv(base / "post_metadata.tsv")) == 22, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 22, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 416, "post xref row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) >= 4800, "post instruction export unexpectedly small")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 22, "post decompile index row count mismatch")
    for row in decomp_index:
        require(row["status"] == "OK", f"decompile failed for {row.get('address')}")


def validate_logs(base: Path) -> None:
    for name, expected in EXPECTED_LOG_SUMMARIES.items():
        path = base / name
        require(path.exists(), f"missing mutation log: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        require(expected in text, f"{name} missing summary {expected!r}")
        require("LockException" not in text, f"{name} contains LockException")
        require("BADNAME:" not in text and "MISSING:" not in text, f"{name} contains failed mutation row")


def validate_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token in text, f"public note missing token {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base
    validate_metadata(base)
    validate_tags(base)
    validate_decompile(base)
    validate_counts(base)
    validate_logs(base)
    validate_public_note()
    print(f"PASS wave516 CThing core evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
