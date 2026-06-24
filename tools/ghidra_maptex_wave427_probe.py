#!/usr/bin/env python3
"""Validate the Wave427 CMapTex saved-Ghidra correction."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave427-maptex" / "current"

COMMON_TAGS = {"static-reaudit", "maptex-wave427", "terrain-texture", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00491180": target(
        "CMapTex__Reset",
        "void __fastcall CMapTex__Reset(void * this)",
        ["RET with no stack cleanup", "+0x0c", "+0x00/+0x08", "OID__FreeObject", "maptex.cpp is absent", "runtime terrain texture behavior", "rebuild parity remain unproven"],
        ["0xffff", "OID__FreeObject", "this + 8"],
        ["reset", "lifecycle", "signature-corrected", "comment-hardened"],
        ["CEngine__Shutdown", "CEngine__Init"],
    ),
    "0x004911c0": target(
        "CMapTex__LoadTexture",
        "int __thiscall CMapTex__LoadTexture(void * this, char * texture_path, int texture_width, int texture_index)",
        ["RET 0xc", "CTGALoader", "texture_path", "texture_width", "texture_index", "height/alpha channel", "maptex.cpp is absent", "runtime terrain texture behavior", "rebuild parity remain unproven"],
        ["CTGALoader", "texture_width", "texture_index", "0x1c", "0x34"],
        ["tga-loader", "height-channel", "signature-corrected", "comment-hardened"],
        ["CMapTex__LoadMixerTextureSet"],
    ),
    "0x00491340": target(
        "CMapTex__DownsampleTexture",
        "void __thiscall CMapTex__DownsampleTexture(void * this, void * dest_buffer, void * src_buffer)",
        ["RET 0x8", "dest_buffer", "src_buffer", "2x2", "signed averaging for the fourth channel", "maptex.cpp is absent", "runtime terrain texture behavior", "rebuild parity remain unproven"],
        ["dest_buffer", "src_buffer", "0x18", ">> 2"],
        ["downsample", "signature-corrected", "comment-hardened"],
        ["CMapTex__CopyFromOther"],
    ),
    "0x004914b0": target(
        "CMapTex__LoadMixerTextureSet",
        "int __thiscall CMapTex__LoadMixerTextureSet(void * this, int set_id, int texture_count, int texture_width)",
        ["RET 0xc", "set_id", "texture_count", "texture_width", "mixer TGA path", "maptex.cpp is absent", "runtime terrain texture behavior", "rebuild parity remain unproven"],
        ["mixers", "CMapTex__LoadTexture", "0x97"],
        ["mixer-texture-set", "signature-corrected", "comment-hardened"],
        ["CEngine__LoadMixers"],
    ),
    "0x004915d0": target(
        "CMapTex__CopyFromOther",
        "void __thiscall CMapTex__CopyFromOther(void * this, void * source_map_tex)",
        ["RET 0x4", "source_map_tex", "copies set/count/min/max", "halves the width", "CMapTex__DownsampleTexture", "maptex.cpp is absent", "runtime terrain texture behavior", "rebuild parity remain unproven"],
        ["source_map_tex", "CMapTex__DownsampleTexture", "0xaf"],
        ["copied-mixer-lod", "signature-corrected", "comment-hardened"],
        ["CEngine__LoadMixers"],
    ),
    "0x004916c0": target(
        "CMapTex__Deserialize",
        "void __thiscall CMapTex__Deserialize(void * this, void * chunk_reader, int texture_index)",
        ["RET 0x8", "chunk_reader", "texture_index is callsite/RET-proven", "not consumed in current decompile", "count << 0xc", "maptex.cpp is absent", "runtime terrain texture behavior", "rebuild parity remain unproven"],
        ["chunk_reader", "0x4c", "0x17c", "0x19a", "0xc"],
        ["chunk-deserialize", "signature-corrected", "comment-hardened"],
        ["CEngine__Deserialize"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 6, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

INSTRUCTION_RETURNS = {
    "0x00491180": ("RET", ""),
    "0x004911c0": ("RET", "0xc"),
    "0x00491340": ("RET", "0x8"),
    "0x004914b0": ("RET", "0xc"),
    "0x004915d0": ("RET", "0x4"),
    "0x004916c0": ("RET", "0x8"),
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime terrain behavior proven",
    "runtime terrain texture behavior proven",
    "runtime mixer behavior proven",
    "source identity proven",
    "concrete layout proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
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


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


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


def rows_by_address(rows: list[dict[str, str]], address: str, key: str = "target_addr") -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "decompile_after"
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return "\n".join(read_text(path) for path in matches)


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def compare_summary(failures: list[str], label: str, path: Path, expected: dict[str, int]) -> None:
    actual = parse_summary(path)
    if actual is None:
        failures.append(f"{label}: missing SUMMARY")
    elif actual != expected:
        failures.append(f"{label}: summary mismatch {actual} != {expected}")


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    instructions = read_tsv(base / "instructions_after.tsv")

    if metadata:
        compare_summary(failures, "dry", base / "apply_dry.log", EXPECTED_DRY)
        compare_summary(failures, "apply", base / "apply_apply.log", EXPECTED_APPLY)
    else:
        failures.append("metadata_after.tsv: missing or empty")

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        expected_name = str(expected["name"])
        expected_signature = str(expected["signature"])
        if row.get("name") != expected_name:
            failures.append(f"{address}: name mismatch {row.get('name')} != {expected_name}")
        if row.get("signature") != expected_signature:
            failures.append(f"{address}: signature mismatch {row.get('signature')} != {expected_signature}")

        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[assignment]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tags row")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing = expected_tags - actual_tags
            if missing:
                failures.append(f"{address}: missing tags {sorted(missing)}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing decompile_after text")
        else:
            for token in expected["decompileTokens"]:  # type: ignore[assignment]
                if not token_present(decompile, str(token)):
                    failures.append(f"{address}: missing decompile token {token!r}")
            for token in OVERCLAIM_TOKENS:
                if token_present(decompile, token):
                    failures.append(f"{address}: decompile overclaim token {token!r}")

        xref_rows = rows_by_address(xrefs, address)
        if not xref_rows:
            failures.append(f"{address}: missing xrefs")
        else:
            combined = "\n".join(" ".join(row.values()) for row in xref_rows)
            for token in expected["xrefTokens"]:  # type: ignore[assignment]
                if not token_present(combined, str(token)):
                    failures.append(f"{address}: missing xref token {token!r}")

        mnemonic, operand = INSTRUCTION_RETURNS[address]
        insn_rows = rows_by_address(instructions, address)
        if not any(row.get("mnemonic") == mnemonic and (not operand or row.get("operands") == operand) for row in insn_rows):
            failures.append(f"{address}: missing instruction terminator {mnemonic} {operand}".rstrip())

    return failures


def build_result(base: Path, failures: list[str]) -> dict[str, object]:
    return {
        "schema": "ghidra-maptex-wave427.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base": str(base.relative_to(ROOT)) if base.is_relative_to(ROOT) else str(base),
        "status": "PASS" if not failures else "FAIL",
        "target_count": len(TARGETS),
        "classification": "maptex-mixer-texture-signature-and-comment-correction" if not failures else "maptex-correction-incomplete",
        "not_proven": [
            "runtime terrain texture behavior",
            "runtime mixer loading behavior",
            "concrete CMapTex layout",
            "source-complete identity because maptex.cpp is absent from the current Stuart snapshot",
            "rebuild parity",
        ],
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--out", type=Path, default=BASE / "maptex-wave427.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    result = build_result(args.base, failures)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        print("FAIL ghidra_maptex_wave427_probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS ghidra_maptex_wave427_probe")
    if args.check:
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
