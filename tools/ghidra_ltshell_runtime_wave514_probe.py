#!/usr/bin/env python3
"""Validate Wave514 CLTShell runtime static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave514-ltshell-runtime-004efb10"
)
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ltshell_runtime_wave514_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "ltshell-runtime-wave514",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime launch behavior proven",
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
    "0x004efb10": target(
        "CLTShell__InitializeRuntimeAndLoadCoreResources",
        "int __fastcall CLTShell__InitializeRuntimeAndLoadCoreResources(void * level_request_slot)",
        ("runtime initialization", "WinMain", "DAT_00896ca4", "pointer sets", "reloads default physics"),
        {"ltshell", "resource-loading", "runtime-init", "startup"},
        ("int __fastcall", "level_request_slot", "CSPtrSet__Initialise", "PCPlatform__Init", "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData"),
    ),
    "0x004f00e0": target(
        "CLTShell__ShutdownRuntimeAndReleaseResources",
        "void __cdecl CLTShell__ShutdownRuntimeAndReleaseResources(void)",
        ("runtime shutdown", "resource-release", "WinMain", "music/sound", "pointer-set resources"),
        {"ltshell", "resource-lifecycle", "runtime-shutdown"},
        ("void __cdecl", "CWorldPhysicsManager__ClearAndFreeAllDefinitionLists", "CTexture__ClearOut", "CSPtrSet__Shutdown"),
    ),
    "0x004f0200": target(
        "CLTShell__RunStressTestLevelLoop",
        "void __stdcall CLTShell__RunStressTestLevelLoop(int stress_test_count)",
        ("stress-test level loop", "DAT_00663058", "DAT_00632b04", "CGame__RunLevel", "memory/debug deltas"),
        {"level-loop", "ltshell", "memory-debug", "stress-test"},
        ("void __stdcall", "stress_test_count", "DAT_00632b04", "CFrontEnd__Run", "CGame__RunLevel"),
    ),
    "0x004f0330": target(
        "CLTShell__RunFrontEndAndGameLoop",
        "int __fastcall CLTShell__RunFrontEndAndGameLoop(void * level_request_slot)",
        ("frontend/game loop", "DAT_00896ca4", "CLTShell__RunStressTestLevelLoop", "CFrontEnd__Run", "CGame__RunLevel"),
        {"frontend-loop", "game-loop", "level-launch", "ltshell"},
        ("int __fastcall", "level_request_slot", "CLTShell__RunStressTestLevelLoop", "CFrontEnd__Run", "CGame__RunLevel"),
    ),
}

EXPECTED_XREFS = {
    ("0x004efb10", "0x005123c3", "CLTShell__WinMain", "UNCONDITIONAL_CALL"),
    ("0x004f00e0", "0x0051241a", "CLTShell__WinMain", "UNCONDITIONAL_CALL"),
    ("0x004f0200", "0x004f0342", "CLTShell__RunFrontEndAndGameLoop", "UNCONDITIONAL_CALL"),
    ("0x004f0200", "0x004f03e5", "CLTShell__RunFrontEndAndGameLoop", "UNCONDITIONAL_CALL"),
    ("0x004f0330", "0x00512410", "CLTShell__WinMain", "UNCONDITIONAL_CALL"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave514_dry.log": "SUMMARY updated=0 skipped=4 missing=0 bad=0",
    "apply_wave514_apply.log": "SUMMARY updated=4 skipped=0 missing=0 bad=0",
    "apply_wave514_verify_dry.log": "SUMMARY updated=0 skipped=4 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "Wave514",
    "4",
    "CLTShell__InitializeRuntimeAndLoadCoreResources",
    "CLTShell__ShutdownRuntimeAndReleaseResources",
    "CLTShell__RunStressTestLevelLoop",
    "CLTShell__RunFrontEndAndGameLoop",
    "runtime launch behavior",
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
    got = {
        (
            row["target_addr"],
            row["from_addr"],
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    missing = EXPECTED_XREFS - got
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


def validate_counts(base: Path) -> None:
    require(len(read_tsv(base / "post_metadata.tsv")) == 4, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 4, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 5, "post xref row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) >= 1000, "post instruction export unexpectedly small")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 4, "post decompile index row count mismatch")
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
    print(f"PASS wave514 LTShell runtime evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
