#!/usr/bin/env python3
"""Validate the saved CEngine render/resource Ghidra signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/engine-render-resource-wave361/current")
OUTPUT_NAME = "engine-render-resource-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "engine-render-resource-wave361",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0044a1c0": target(
        "CEngine__UpdatePos",
        "void __thiscall CEngine__UpdatePos(void * this, void * camera)",
        ["UpdatePos", "RET 0x4", "+0x4a8", "+0x4ac", "CDXLandscape__SetTileData", "remain unproven"],
        ["CDXLandscape__SetTileData", "+ 0x4a8", "+ 0x4ac", "camera"],
        ["engine", "landscape", "render-position"],
    ),
    "0x0044a1f0": target(
        "CEngine__LoadMixers",
        "void __thiscall CEngine__LoadMixers(void * this, int set)",
        ["LoadMixers", "RET 0x4", "+0x49c", "0x100", "copied mixer levels", "remain unproven"],
        ["CMapTex__LoadMixerTextureSet", "0x100", "+ 0x49c", "CMapTex__CopyFromOther"],
        ["engine", "map-textures", "resource-load"],
    ),
    "0x0044a2a0": target(
        "CEngine__SetKempyCube",
        "void __thiscall CEngine__SetKempyCube(void * this, int number)",
        ["SetKempyCube", "RET 0x4", "+0x498", "KempyCube", "remain unproven"],
        ["CDXEngine__InitKempyCubeResources", "+ 0x498", "number"],
        ["engine", "kempy-cube", "resource-select"],
    ),
    "0x0044a2c0": target(
        "CEngine__SetWater",
        "void __thiscall CEngine__SetWater(void * this, int number)",
        ["SetWater", "RET 0x4", "+0x14", "CWaterRenderSystem__ReloadTextures", "remain unproven"],
        ["CWaterRenderSystem__ReloadTextures", "+ 0x14", "number"],
        ["engine", "water", "resource-select"],
    ),
}

XREF_EVIDENCE = [
    ("0x0044a1c0", "0x0046f029", "UNCONDITIONAL_CALL"),
    ("0x0044a1f0", "0x00491116", "UNCONDITIONAL_CALL"),
    ("0x0044a2a0", "0x004910f2", "UNCONDITIONAL_CALL"),
    ("0x0044a2c0", "0x00491138", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x0044a1c0", "0x0044a1de", "RET", "0x4"),
    ("0x0044a1f0", "0x0044a1ff", "MOV", "+ 0x49c"),
    ("0x0044a2a0", "0x0044a2a4", "MOV", "+ 0x498"),
    ("0x0044a2c0", "0x0044a2c4", "MOV", "+ 0x14"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3"]
STALE_NAME_TOKENS = [
    "CResourceAccumulator__LoadAndCopyMixerTextureSet",
    "CResourceAccumulator__InitKempyCubeResources",
    "CResourceAccumulator__ReloadWaterRenderTextures",
]
OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "layout proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    match = re.search(r"targets=(\d+)\s+updated=(\d+)\s+skipped=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if not match:
        return {}
    return {
        "targets": int(match.group(1)),
        "updated": int(match.group(2)),
        "skipped": int(match.group(3)),
        "failed": int(match.group(4)),
        "dry": match.group(5) == "true",
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def decompile_for(decompile_dir: Path, address: str) -> str:
    matches = sorted(decompile_dir.glob(f"{norm_addr(address)[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "engine_render_resource_signature_dry.log"
    apply_log_path = apply_log_path or root / "engine_render_resource_signature_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    metadata = row_by_addr(read_tsv(metadata_path))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)

    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"targets": expected_count, "updated": 0, "skipped": expected_count, "failed": 0, "dry": True}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"targets": expected_count, "updated": expected_count, "skipped": 0, "failed": 0, "dry": False}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    stale_name_hits = 0
    stale_signature_hits = 0
    overclaim_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        name = row.get("name", "")
        signature = row.get("signature", "")
        if name != spec["name"]:
            failures.append(f"{address} name mismatch: {name} != {spec['name']}")
        if signature != spec["signature"]:
            failures.append(f"{address} signature mismatch: {signature} != {spec['signature']}")
        for token in STALE_SIGNATURE_TOKENS:
            if token in signature:
                stale_signature_hits += 1
                failures.append(f"{address} stale signature token present: {token}")
        for token in STALE_NAME_TOKENS:
            if token in name and token != spec["name"]:
                stale_name_hits += 1
                failures.append(f"{address} stale name token present: {token}")

        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment.lower():
                overclaim_hits += 1
                failures.append(f"{address} comment overclaim token: {token}")

        tag_row = tags.get(address)
        if not tag_row:
            failures.append(f"{address} tag row missing")
        else:
            observed_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
            expected_tags = COMMON_TAGS | set(spec["tags"])  # type: ignore[arg-type]
            missing_tags = sorted(expected_tags - observed_tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {missing_tags}")

        decompile = decompile_for(decompile_dir, address)
        if not decompile:
            failures.append(f"{address} decompile missing")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address} decompile missing token: {token}")
        for token in STALE_NAME_TOKENS:
            if token in decompile and token != spec["name"]:
                stale_name_hits += 1
                failures.append(f"{address} stale decompile token present: {token}")

    xref_hits = 0
    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target_addr} <- {from_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operands_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target_addr=target_addr, instruction_addr=instruction_addr, mnemonic=mnemonic, operands_token=operands_token: (
                norm_addr(row.get("function_entry")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instruction_addr)
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operands_token)
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target_addr} {instruction_addr} {mnemonic} {operands_token}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": expected_count,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleNameHits": stale_name_hits,
            "staleSignatureHits": stale_signature_hits,
            "overclaimHits": overclaim_hits,
        },
        "inputs": {
            "root": root.as_posix(),
            "dryLog": dry_log_path.as_posix(),
            "applyLog": apply_log_path.as_posix(),
            "metadata": metadata_path.as_posix(),
            "tags": tags_path.as_posix(),
            "xrefs": xrefs_path.as_posix(),
            "instructions": instructions_path.as_posix(),
            "decompileDir": decompile_dir.as_posix(),
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    report = build_report(root=args.root)
    out_path = args.out or args.root / OUTPUT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = report["summary"]
    print(f"Status: {report['status']}")
    print(f"Targets: {summary['targets']}")
    print(f"Xref evidence hits: {summary['xrefEvidenceHits']}")
    print(f"Instruction evidence hits: {summary['instructionEvidenceHits']}")
    print(f"Stale name hits: {summary['staleNameHits']}")
    print(f"Stale signature hits: {summary['staleSignatureHits']}")
    print(f"Overclaim hits: {summary['overclaimHits']}")
    for failure in report["failures"]:
        print(f"- {failure}")

    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
