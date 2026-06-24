#!/usr/bin/env python3
"""Validate Wave465 PauseMenu tail static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave465-pausemenu-tail-current"
COMMON_TAGS = {"static-reaudit", "pausemenu-tail-wave465", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 10,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 6,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 10,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 6,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 10,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


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
    "0x004d01c0": target(
        "CMenuItem__RestoreCompactVTable",
        "void __fastcall CMenuItem__RestoreCompactVTable(void * menu_item)",
        ["Wave465 correction", "vtable-reset", "PTR_CMenuItem__scalar_deleting_dtor_005db440"],
        ["menu-item", "vtable-reset", "name-corrected", "signature-corrected", "comment-hardened"],
        ["PTR_CMenuItem__scalar_deleting_dtor_005db440"],
    ),
    "0x004d0290": target(
        "CControllerBackMenuItem__RenderBindingCapacityWarning",
        "void __thiscall CControllerBackMenuItem__RenderBindingCapacityWarning(void * this, float x, float y, int render_flags)",
        ["Wave465 correction", "Controls__FindFirstFreeBindingSlot", "0xe8/0xe9", "CMenuItem__RenderWithColor"],
        ["menu-item", "controller-back", "render", "name-corrected", "signature-corrected", "comment-hardened"],
        ["Controls__FindFirstFreeBindingSlot", "Localization__GetStringById", "CMenuItem__RenderWithColor"],
    ),
    "0x004d0490": target(
        "CMenuItem__shared_compact_scalar_deleting_dtor",
        "void * __thiscall CMenuItem__shared_compact_scalar_deleting_dtor(void * this, int flags)",
        ["Wave465 correction", "scalar-deleting destructor", "CMenuItem__RestoreCompactVTable", "flags bit 0"],
        ["menu-item", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CMenuItem__RestoreCompactVTable", "CDXMemoryManager__Free", "flags & 1"],
    ),
    "0x004d04b0": target(
        "CPauseMenu__scalar_deleting_dtor",
        "void * __thiscall CPauseMenu__scalar_deleting_dtor(void * this, int flags)",
        ["Wave465 correction", "CPauseMenu__dtor_base", "flags bit 0"],
        ["pause-menu", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CPauseMenu__dtor_base", "CDXMemoryManager__Free", "flags & 1"],
    ),
    "0x004d0510": target(
        "CPauseMenu__LoadPauseTextures",
        "void __fastcall CPauseMenu__LoadPauseTextures(void * pause_menu)",
        ["Wave465 correction", "pause_circle01/02", "FrontEnd_v2/FE_Blank.tga"],
        ["pause-menu", "texture-load", "signature-corrected", "comment-hardened"],
        ["CMenuItemRange__LoadTexture", "pause_circle01", "FrontEnd_v2_FE_Blank_tga"],
    ),
    "0x004d05e0": target(
        "CPauseMenu__dtor_base",
        "void __fastcall CPauseMenu__dtor_base(void * pause_menu)",
        ["Wave465 correction", "CMonitor__Shutdown", "pause textures"],
        ["pause-menu", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Clear", "CHud__DecrementCounter9C", "CMonitor__Shutdown"],
    ),
    "0x004d06e0": target(
        "CPauseMenu__ResumeGameAndPersistOptions",
        "void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void * pause_menu)",
        ["Wave465 correction", "unpauses the game", "defaultoptions.bea", "serializes the current career/options buffer"],
        ["pause-menu", "options-persist", "signature-corrected", "comment-hardened"],
        ["CGame__UnPause", "CCareer__Save", "CFEPOptions__WriteDefaultOptionsFile"],
    ),
    "0x004d0810": target(
        "CPauseMenu__ButtonPressed",
        "void __thiscall CPauseMenu__ButtonPressed(void * this, void * menu_item, int button_context)",
        ["Wave465 correction", "binding-prompt construction", "CEngine__SetOptionValueAndNotifyTarget", "frontend sound feedback"],
        ["pause-menu", "button-dispatch", "signature-corrected", "comment-hardened"],
        ["CPauseMenu__ResumeGameAndPersistOptions", "CGameMenu__InitBase", "CPauseMenu__InitBindingPromptAction", "CFrontEnd__PlaySound"],
    ),
    "0x004d0db0": target(
        "CPauseMenu__InitBindingPromptAction",
        "void * __thiscall CPauseMenu__InitBindingPromptAction(void * this, void * menu_item, void * pause_menu, int action_id)",
        ["Wave465 correction", "CPauseMenu__InitAndSetActiveReader", "RET 0x0c", "three stack arguments"],
        ["pause-menu", "binding-prompt", "signature-corrected", "comment-hardened"],
        ["CPauseMenu__InitAndSetActiveReader", "action_id", "menu_item"],
    ),
    "0x004d0e40": target(
        "CGameMenu__InitBase",
        "void __fastcall CGameMenu__InitBase(void * game_menu)",
        ["Wave465 correction", "PTR_SharedVFunc__NoOpOneArg_004014c0_005dc72c", "CMenuItemRangeVariant"],
        ["game-menu", "constructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc72c", "+ 4"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004d01c0", "0x004d0493", "CMenuItem__shared_compact_scalar_deleting_dtor"),
    ("0x004d0290", "0x005de604", "<no_function>"),
    ("0x004d0490", "0x005dc578", "<no_function>"),
    ("0x004d04b0", "0x005de700", "<no_function>"),
    ("0x004d0510", "0x0046e3b2", "CGame__RunLevel"),
    ("0x004d05e0", "0x004d04b3", "CPauseMenu__scalar_deleting_dtor"),
    ("0x004d06e0", "0x004d0c8a", "CPauseMenu__ButtonPressed"),
    ("0x004d0810", "0x004d1665", "CPauseMenu__VFunc_03_004d15d0"),
    ("0x004d0db0", "0x004d09fe", "CPauseMenu__ButtonPressed"),
    ("0x004d0e40", "0x004d0917", "CPauseMenu__ButtonPressed"),
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
    parser.add_argument("--base", type=Path, default=BASE, help="Wave465 artifact directory")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
