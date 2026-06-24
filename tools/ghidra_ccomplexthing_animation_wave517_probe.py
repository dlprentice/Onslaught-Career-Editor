#!/usr/bin/env python3
"""Validate Wave517 CComplexThing / CAnimation static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave517-ccomplexthing-tail-004f3e10"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ccomplexthing_animation_wave517_2026-05-17.md"

COMMON_TAGS = {
    "ccomplexthing-animation-wave517",
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime animation behavior proven",
    "runtime script behavior proven",
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
    "0x004046d0": target(
        "CAnimation__ctor",
        "void * __thiscall CAnimation__ctor(void * this, void * owner_thing)",
        ("CAnimation constructor", "not a CAtmospheric constructor", "owner_thing", "+0x20", "event 3000"),
        {"animation", "constructor", "owner-correction", "source-parity"},
        ("void * __thiscall", "owner_thing", "CEventManager__AddEvent_AtTime", "3000"),
    ),
    "0x00404790": target(
        "CAnimation__Process",
        "void __fastcall CAnimation__Process(void * this)",
        ("CAnimation process/update", "not an atmospheric blend-state helper", "FinishedPlayingCurrentAnimation", "CThing__GetRenderThingFrameIncrement"),
        {"animation", "owner-correction", "process", "source-parity"},
        ("void __fastcall", "CThing__GetRenderThingFrameIncrement", "+ 0xec", "0x3f800000"),
    ),
    "0x00404860": target(
        "CAnimation__SetAnimMode",
        "bool __thiscall CAnimation__SetAnimMode(void * this, int anim_mode, int reset_frame, int force_looped)",
        ("CAnimation::SetAnimMode", "not atmospheric trail configuration", "RET 0x0c", "out real-index"),
        {"animation", "mode", "owner-correction", "source-parity"},
        ("bool __thiscall", "anim_mode", "reset_frame", "force_looped", "CThing__GetRenderThingFrameIncrement"),
    ),
    "0x004048c0": target(
        "CAnimation__GetRenderFrame",
        "double __fastcall CAnimation__GetRenderFrame(void * this)",
        ("CAnimation render-frame accessor", "not an atmospheric blend accessor", "0x008a9e44", "x87 float"),
        {"animation", "frame", "owner-correction", "source-parity"},
        ("double __fastcall", "DAT_008a9e44", "+ 8", "+ 0xc"),
    ),
    "0x004f3c80": target(
        "CThing__GetRenderThingFrameIncrement",
        "double __thiscall CThing__GetRenderThingFrameIncrement(void * this, int anim_mode, int * out_real_index)",
        ("CThing::GetRenderThingFrameIncrement", "not an atmospheric sampler", "this+0x30", "out_real_index"),
        {"animation", "cthing", "owner-correction", "render", "source-parity"},
        ("double __thiscall", "anim_mode", "out_real_index", "+ 0x30", "+ 0x38"),
    ),
    "0x004f3e10": target(
        "CComplexThing__ctor_base",
        "void * __fastcall CComplexThing__ctor_base(void * this)",
        ("CComplexThing constructor", "+0x3c", "+0x6c/+0x70/+0x74/+0x78", "returns this"),
        {"ccomplexthing", "constructor", "source-parity"},
        ("void * __fastcall", "CMapWhoEntry__Invalidate", "DAT_0083da30", "+ 0x6c"),
    ),
    "0x004f3ee0": target(
        "CComplexThing__scalar_deleting_dtor",
        "void * __thiscall CComplexThing__scalar_deleting_dtor(void * this, byte delete_flags)",
        ("scalar deleting destructor", "delete_flags", "CComplexThing__dtor_base", "CDXMemoryManager__Free"),
        {"ccomplexthing", "destructor", "vtable-slot-1"},
        ("void * __thiscall", "delete_flags", "CComplexThing__dtor_base", "CDXMemoryManager__Free"),
    ),
    "0x004f3f00": target(
        "CComplexThing__dtor_base",
        "void __fastcall CComplexThing__dtor_base(void * this)",
        ("destructor-base", "+0x74", "+0x6c", "+0x70", "CThing destructor-base"),
        {"ccomplexthing", "destructor", "source-parity"},
        ("void __fastcall", "+ 0x74", "+ 0x6c", "CMapWhoEntry__RemoveFromMap", "CMonitor__Shutdown"),
    ),
    "0x004f3fd0": target(
        "CComplexThing__Init",
        "void __thiscall CComplexThing__Init(void * this, void * init)",
        ("CComplexThing::Init", "CComplexThing__SetName", "CComplexThing__SetScript", "this+0x3c", "CThing__Init"),
        {"ccomplexthing", "init", "source-parity"},
        ("void __thiscall", "CComplexThing__SetScript", "+ 0x3c", "CThing__Init"),
    ),
    "0x004f4120": target(
        "CComplexThing__SetName",
        "void __thiscall CComplexThing__SetName(void * this, char * name)",
        ("CComplexThing::SetName", "not a base CThing helper", "0x00855130", "this+0x78"),
        {"ccomplexthing", "name", "owner-correction", "source-parity"},
        ("char * name", "DAT_00855130", "CDXMemoryManager__Free", "_strncpy"),
    ),
    "0x004f41b0": target(
        "CComplexThing__Shutdown",
        "void __fastcall CComplexThing__Shutdown(void * this)",
        ("CComplexThing shutdown", "this+0x78", "objective/list", "monitor state"),
        {"ccomplexthing", "shutdown", "source-parity", "vtable-slot"},
        ("void __fastcall", "DAT_00855130", "DAT_00855140", "CMonitor__Shutdown_Core"),
    ),
    "0x004f4230": target(
        "CComplexThing__SetScript",
        "void __thiscall CComplexThing__SetScript(void * this, char * script_name)",
        ("CComplexThing::SetScript", "not a CThing sound helper", "+0x74", "INIT_SCRIPT", "0x7d1"),
        {"ccomplexthing", "mission-script", "owner-correction", "source-parity"},
        ("script_name", "CWorld__CloneScriptObjectCodeByName", "OID__AllocObject(0x3c,0x18", "0x7d1"),
    ),
    "0x004f43d0": target(
        "CComplexThing__AddShutdownEvent",
        "void __fastcall CComplexThing__AddShutdownEvent(void * this)",
        ("shutdown-event", "mission script", "+0x74", "base shutdown-event path"),
        {"ccomplexthing", "mission-script", "shutdown", "source-parity"},
        ("void __fastcall", "IScript__CallEventId3_OrReset", "+ 0x74", "2000"),
    ),
    "0x004f4430": target(
        "CComplexThing__StartDieProcess",
        "int __fastcall CComplexThing__StartDieProcess(void * this)",
        ("death-process hook", "StartDieProcess", "+0x74", "StartedDying"),
        {"ccomplexthing", "death", "mission-script", "source-parity"},
        ("int __fastcall", "+ 0x38", "IScript__CallEventId5_OrReset", "return 1"),
    ),
    "0x004f4480": target(
        "CComplexThing__Hit",
        "void __thiscall CComplexThing__Hit(void * this, void * other_thing, void * collision_report)",
        ("mission-script hit callback", "other_thing", "collision_report", "+0x74"),
        {"ccomplexthing", "collision", "hit", "mission-script", "source-parity"},
        ("void __thiscall", "other_thing", "collision_report", "IScript__CreateThingRefWithSquad"),
    ),
    "0x004f44a0": target(
        "CComplexThing__SetAnimMode",
        "bool __thiscall CComplexThing__SetAnimMode(void * this, int anim_mode, int reset_frame, int force_looped)",
        ("CComplexThing::SetAnimMode", "not CThing trail setup", "0x24-byte CAnimation", "CAnimation__SetAnimMode"),
        {"animation", "ccomplexthing", "mode", "owner-correction", "source-parity"},
        ("bool __thiscall", "OID__AllocObject(0x24,5", "CAnimation__ctor", "CAnimation__SetAnimMode"),
    ),
    "0x004f45a0": target(
        "CComplexThing__FinishedPlayingCurrentAnimation",
        "int __fastcall CComplexThing__FinishedPlayingCurrentAnimation(void * this)",
        ("FinishedPlayingCurrentAnimation", "not a CUnit saved-script resume helper", "+0x74", "returns TRUE"),
        {"animation", "ccomplexthing", "mission-script", "owner-correction", "source-parity"},
        ("int __fastcall", "+ 0x74", "return 1"),
    ),
    "0x004f45e0": target(
        "CComplexThing__SetVar",
        "void __stdcall CComplexThing__SetVar(void * var_name, void * data)",
        ("CComplexThing::SetVar", "not an explosion-init helper", "RET 0x8", "unknown variable"),
        {"ccomplexthing", "mission-script", "owner-correction", "source-parity", "warning"},
        ("void CComplexThing__SetVar", "var_name", "CConsole__Printf", "s_Warning__Uknown_var"),
    ),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave517_dry.log": "SUMMARY updated=0 skipped=18 renamed=0 would_rename=13 missing=0 bad=0",
    "apply_wave517_apply.log": "SUMMARY updated=18 skipped=0 renamed=13 would_rename=0 missing=0 bad=0",
    "apply_wave517_verify_dry.log": "SUMMARY updated=0 skipped=18 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "Wave517",
    "18",
    "CAnimation__ctor",
    "CComplexThing__SetScript",
    "CComplexThing__SetAnimMode",
    "runtime animation behavior",
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


def validate_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    wanted = {
        ("0x004046d0", "0x004f44eb", "CComplexThing__SetAnimMode", "UNCONDITIONAL_CALL"),
        ("0x00404860", "0x004f4511", "CComplexThing__SetAnimMode", "UNCONDITIONAL_CALL"),
        ("0x004f3c80", "0x00404885", "CAnimation__SetAnimMode", "UNCONDITIONAL_CALL"),
        ("0x004f3c80", "0x0040480b", "CAnimation__Process", "UNCONDITIONAL_CALL"),
        ("0x004f3ee0", "0x005df788", "<no_function>", "DATA"),
        ("0x004f3f00", "0x004f3ee3", "CComplexThing__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("0x004f4230", "0x004f3ff8", "CComplexThing__Init", "UNCONDITIONAL_CALL"),
    }
    got = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in rows
    }
    missing = wanted - got
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


def validate_counts(base: Path) -> None:
    require(len(read_tsv(base / "post_metadata.tsv")) == 18, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 18, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 415, "post xref row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) >= 5200, "post instruction export unexpectedly small")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 18, "post decompile index row count mismatch")
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
    validate_xrefs(base)
    validate_counts(base)
    validate_logs(base)
    validate_public_note()
    print(f"PASS wave517 CComplexThing/CAnimation evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
