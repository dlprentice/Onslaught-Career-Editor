#!/usr/bin/env python3
"""Validate Wave499 OptionsTail static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave499-options-tail-00420b10"

COMMON_TAGS = {"static-reaudit", "options-tail-wave499", "retail-binary-evidence"}


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
    "0x00420b10": target(
        "OptionsTail_Write",
        "byte * __stdcall OptionsTail_Write(byte * tail)",
        (
            "Wave499 signature/comment/tag hardening",
            "fixed 0x56-byte options tail snapshot",
            "CCareer__Save",
            "CCareer__SaveWithFlag",
            "D3DDeviceProfileTable__GetAdapterRecord",
            "D3DDeviceProfile__PackDeviceIndexKey",
            "tail+0x08/+0x0a",
            "tail+0x54/+0x55",
            "returns tail+0x56",
            "runtime option persistence behavior",
            "rebuild parity remain unproven",
        ),
        {"save-options", "options-tail", "tail-0x56", "defaultoptions", "signature-corrected", "comment-hardened"},
        (
            "D3DDeviceProfileTable__GetAdapterRecord",
            "D3DDeviceProfile__PackDeviceIndexKey",
            "g_ControlSchemeIndex",
            "g_LanguageIndex",
            "g_LandscapeDetailLevel2",
            "g_LandscapeDetailLevel1",
            "return tail + 0x56",
        ),
    ),
    "0x00420d70": target(
        "OptionsTail_Read",
        "byte * __stdcall OptionsTail_Read(byte * tail)",
        (
            "Wave499 signature/comment/tag hardening",
            "fixed 0x56-byte options tail snapshot",
            "CCareer__Load",
            "Controls__ApplyPreset",
            "CFrontEnd__SetLanguage",
            "CDXEngine__SetGlobalTintColorOpaque(0xf6)",
            "Audio__ReinitializeSoundAndRestoreMusic(1)",
            "CSoundManager__ReloadLanguageSampleBank",
            "tail+0x54/+0x55",
            "returns tail+0x56",
            "runtime option persistence behavior",
            "rebuild parity remain unproven",
        ),
        {"save-options", "options-tail", "tail-0x56", "defaultoptions", "signature-corrected", "comment-hardened"},
        (
            "Controls__ApplyPreset",
            "CFrontEnd__SetLanguage",
            "CDXEngine__SetGlobalTintColorOpaque(0xf6)",
            "Audio__ReinitializeSoundAndRestoreMusic(1)",
            "CSoundManager__ReloadLanguageSampleBank",
            "return tail + 0x56",
        ),
    ),
}

XREF_EXPECTATIONS = (
    ("0x00420b10", "0x004213ab", "CCareer__Save", "UNCONDITIONAL_CALL"),
    ("0x00420b10", "0x00421425", "CCareer__SaveWithFlag", "UNCONDITIONAL_CALL"),
    ("0x00420d70", "0x0042133c", "CCareer__Load", "UNCONDITIONAL_CALL"),
)

EXPECTED_LOG_SUMMARIES = {
    "apply_options_tail_wave499_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_options_tail_wave499_apply.log": {
        "updated": 2,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_options_tail_wave499_final_verify_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

OVERCLAIM_TOKENS = (
    "runtime option persistence behavior proven",
    "runtime behavior proven",
    "exact tail struct proven",
    "rebuild parity proven",
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


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing TSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def read_text(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def require_token(text: str, token: str, label: str) -> None:
    if not token_present(text, token):
        raise AssertionError(f"{label} missing token: {token}")


def decompile_text(base: Path, address: str, expected_name: str) -> str:
    stem = normalize_address(address)[2:]
    decomp_dir = base / "post-decomp"
    preferred = sorted(decomp_dir.glob(f"{stem}_{expected_name}*.c"))
    candidates = preferred or sorted(decomp_dir.glob(f"{stem}_*.c"))
    if not candidates:
        raise AssertionError(f"missing post-decompile for {address}")
    return read_text(candidates[0])


def check_metadata(base: Path) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(base / "post_metadata.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row is None:
            raise AssertionError(f"missing metadata row for {address}")
        if row["status"] != "OK":
            raise AssertionError(f"{address} metadata status {row['status']}")
        if row["name"] != spec["name"]:
            raise AssertionError(f"{address} name {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            raise AssertionError(f"{address} signature {row['signature']} != {spec['signature']}")
        comment = row["comment"]
        for token in spec["comment_tokens"]:
            require_token(comment, str(token), f"{address} comment")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                raise AssertionError(f"{address} overclaim token present: {token}")


def check_tags(base: Path) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(base / "post_tags.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row is None:
            raise AssertionError(f"missing tag row for {address}")
        tags = {tag for tag in row["tags"].split(";") if tag}
        missing = sorted(spec["tags"] - tags)
        if missing:
            raise AssertionError(f"{address} missing tags: {missing}")


def check_decompiles(base: Path) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text(base, address, str(spec["name"]))
        for token in spec["decompile_tokens"]:
            require_token(text, str(token), f"{address} decompile")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    for target, from_addr, from_function, ref_type in XREF_EXPECTATIONS:
        found = any(
            row["target_addr"] == normalize_address(target)
            and row["from_addr"] == normalize_address(from_addr)
            and row["from_function"] == from_function
            and row["ref_type"] == ref_type
            for row in rows
        )
        if not found:
            raise AssertionError(f"missing xref {target} from {from_addr} {from_function} {ref_type}")


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"SUMMARY:?\s+(.+)", text)
    if not match:
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(1))}


def check_logs(base: Path) -> None:
    for name, expected in EXPECTED_LOG_SUMMARIES.items():
        text = read_text(base / name)
        if "REPORT: Save succeeded" not in text:
            raise AssertionError(f"{name} missing save success")
        actual = parse_summary(text)
        if not actual:
            raise AssertionError(f"{name} missing SUMMARY line")
        for key, expected_value in expected.items():
            actual_value = actual.get(key)
            if actual_value != expected_value:
                raise AssertionError(f"{name} {key} {actual_value} != {expected_value}")


def check(args: argparse.Namespace) -> int:
    base = Path(args.base).resolve()
    check_metadata(base)
    check_tags(base)
    check_decompiles(base)
    check_xrefs(base)
    check_logs(base)
    print(f"Wave499 OptionsTail probe PASS ({len(TARGETS)} targets)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=str(DEFAULT_BASE))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("use --check")
    return check(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
