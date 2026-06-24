#!/usr/bin/env python3
"""Validate the saved CEngine / viewpoint Ghidra signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/engine-viewpoint-wave360/current")
OUTPUT_NAME = "engine-viewpoint-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "engine-viewpoint-wave360",
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
    "0x00449820": target(
        "CEngine__ctor",
        "void __fastcall CEngine__ctor(void * engine)",
        ["constructor", "vtable", "near/far clip", "+0x4a8", "remain unproven"],
        ["0x3dcccccd", "0x43800000", "+ 0x4a8"],
        ["engine", "constructor", "viewpoint"],
    ),
    "0x00449890": target(
        "CEngine__Shutdown",
        "void __fastcall CEngine__Shutdown(void * engine)",
        ["shutdown", "screen effects", "shadow/tree", "map texture/HUD texture resources", "remain unproven"],
        ["CScreenFx__ReleaseZoomTextures", "CDXShadows__Destructor", "CDXTrees__Reset", "CEngine__TrimVbIbPoolCapacitiesPow2"],
        ["engine", "shutdown", "resource-lifecycle"],
    ),
    "0x004499d0": target(
        "CEngine__Init",
        "int __fastcall CEngine__Init(void * engine)",
        ["init", "cg_renderlandscape", "gamut", "map texture", "landscape", "returns 1/0", "remain unproven"],
        ["s_cg_renderlandscape_00628b9c", "CGamut__Init", "CDXLandscape__Init", "CScreenFx__InitZoomEffectCvar"],
        ["engine", "init", "resource-lifecycle"],
    ),
    "0x00449d50": target(
        "CEngine__InitResources",
        "void __fastcall CEngine__InitResources(void * engine)",
        ["resource init", "hilight.tga", "hiteffect.tga", "cloak.tga", "cloud-shadow", "remain unproven"],
        ["CScreenFx__LoadZoomTextures", "s_hilight_tga_00628cb0", "s_cloak_tga_00628c94", "CDXLandscape__LoadCloudShadowTexture"],
        ["engine", "init-resources", "textures"],
    ),
    "0x00449dc0": target(
        "CEngine__LoadAllNamedMeshes",
        "void __thiscall CEngine__LoadAllNamedMeshes(void * this, void * dataFile)",
        ["LoadAllNamedMeshes", "RET 0x4", "Loading named meshes", "CMesh__FindOrCreate", "remain unproven"],
        ["s_Loading_named_meshes_00628cbc", "CDXMemBuffer__Read", "CMesh__FindOrCreate", "CConsole__StatusDone"],
        ["engine", "named-meshes", "world-load"],
    ),
    "0x00449ef0": target(
        "CEngine__GetViewMatrixFromCamera",
        "void __thiscall CEngine__GetViewMatrixFromCamera(void * this, void * camera, void * outViewMatrix)",
        ["GetViewMatrixFromCamera", "RET 0x8", "camera", "outViewMatrix", "pitch basis", "remain unproven"],
        ["camera", "outViewMatrix", "fcos", "fsin", "CMCBuggy__MultiplyMat34Basis"],
        ["engine", "viewpoint", "camera-matrix"],
    ),
    "0x0044a020": target(
        "CEngine__SetViewpoint",
        "void __thiscall CEngine__SetViewpoint(void * this, int viewpoint, void * camera, void * viewport, void * player)",
        ["SetViewpoint", "RET 0x10", "viewport", "player", "CInterpolatedCamera", "remain unproven"],
        ["viewpoint", "camera", "viewport", "player", "CInterpolatedCamera"],
        ["engine", "viewpoint", "camera"],
    ),
    "0x0044a0d0": target(
        "CEngine__SelectViewpoint",
        "void __thiscall CEngine__SelectViewpoint(void * this, int viewpoint)",
        ["SelectViewpoint", "RET 0x4", "+0x4ac", "D3DDevice__SetViewport", "remain unproven"],
        ["viewpoint", "+ 0x4ac", "D3DDevice__SetViewport"],
        ["engine", "viewpoint", "viewport"],
    ),
    "0x0044a110": target(
        "CEngine__ResetPos",
        "void __thiscall CEngine__ResetPos(void * this, int x, int y)",
        ["ResetPos", "RET 0x8", "mLandscape", "x/y", "remain unproven"],
        ["x", "y", "+ 0x10", "CDXLandscape__ResetWrapper"],
        ["engine", "landscape", "position-reset"],
    ),
    "0x0044a130": target(
        "CEngine__InitDamageSystem",
        "void __fastcall CEngine__InitDamageSystem(void * engine)",
        ["InitDamageSystem", "tree-shadow", "damage stamp", "LockCurrentDamage", "remain unproven"],
        ["CDamage__ResetDamageTables", "CTree__ComputeLodBucket", "CDXEngine__ApplyLandscapeDamageStamp", "CDXLandscape__Reset"],
        ["engine", "landscape", "damage-system"],
    ),
}

XREF_EVIDENCE = [
    ("0x00449820", "0x0053d345", "UNCONDITIONAL_CALL"),
    ("0x00449890", "0x0053d3e4", "UNCONDITIONAL_CALL"),
    ("0x004499d0", "0x0053d5f3", "UNCONDITIONAL_CALL"),
    ("0x00449d50", "0x0053d6d3", "UNCONDITIONAL_CALL"),
    ("0x00449dc0", "0x0050bc34", "UNCONDITIONAL_CALL"),
    ("0x00449ef0", "0x0053e360", "UNCONDITIONAL_CALL"),
    ("0x0044a020", "0x0046e680", "UNCONDITIONAL_CALL"),
    ("0x0044a0d0", "0x0053e320", "UNCONDITIONAL_CALL"),
    ("0x0044a110", "0x0043f4a1", "UNCONDITIONAL_CALL"),
    ("0x0044a130", "0x0046ddf0", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00449820", "0x0044982f", "MOV", "0x3dcccccd"),
    ("0x00449890", "0x0044989a", "CALL", "0x00551d40"),
    ("0x004499d0", "0x00449a19", "MOV", "0x663498"),
    ("0x00449d50", "0x00449d76", "CALL", "0x004f27f0"),
    ("0x00449dc0", "0x00449ede", "RET", "0x4"),
    ("0x00449ef0", "0x0044a010", "RET", "0x8"),
    ("0x0044a020", "0x0044a0bc", "RET", "0x10"),
    ("0x0044a0d0", "0x0044a102", "RET", "0x4"),
    ("0x0044a110", "0x0044a122", "RET", "0x8"),
    ("0x0044a130", "0x0044a1a9", "CALL", "0x00545070"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3"]
STALE_NAME_TOKENS = [
    "CEngine__ctor_like_00449820",
    "VFuncSlot_00_00449890",
    "CEngine__VFunc_02_00449d50",
    "CWorld__LoadNamedMeshCacheFromBuffer",
    "CFrontEnd__BuildCameraBasisFromYaw",
    "CCutscene__ResetLandscape",
    "CGame__RebuildLandscapeDamageStamps",
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
    dry_log_path = dry_log_path or root / "engine_viewpoint_signature_dry.log"
    apply_log_path = apply_log_path or root / "engine_viewpoint_signature_apply.log"
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
