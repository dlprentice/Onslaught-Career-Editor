#!/usr/bin/env python3
"""Validate the saved CEngine render-tail Ghidra signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/engine-render-tail-wave362/current")
OUTPUT_NAME = "engine-render-tail-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "engine-render-tail-wave362",
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
    "0x0044a2d0": target(
        "CEngine__SetupLights",
        "void CEngine__SetupLights(void)",
        ["SetupLights", "sun vector", "Atmospherics", "render-light matrices", "remain unproven"],
        ["Atmospherics__NotifyAll", "CEngine__UpdateViewVector", "DAT_009c68ad", "DAT_009c6910"],
        ["engine", "lighting", "render-state"],
    ),
    "0x0044a5f0": target(
        "Vec3__AssignXYZ",
        "void __thiscall Vec3__AssignXYZ(void * this, float x, float y, float z)",
        ["RET 0xc", "stack float/dword arguments", "vector helper", "remain unproven"],
        ["*(float *)this = x", "*(float *)((int)this + 4) = y", "*(float *)((int)this + 8) = z"],
        ["math", "vector"],
    ),
    "0x0044a610": target(
        "CEngine__TrackBurstEventFromPreset",
        "void __thiscall CEngine__TrackBurstEventFromPreset(void * this, int burstArg0, int burstArg1, int burstArg2)",
        ["RET 0xc", "+0x470", "+0x18", "TrackBurstEventIfNearby", "remain unproven"],
        ["CEngine__TrackBurstEventIfNearby", "+ 0x470", "+ 0x18"],
        ["engine", "projectile-burst"],
    ),
    "0x0044a640": target(
        "CDXEngine__SetOverlaySlotVisibilityByPlayerView",
        "void __thiscall CDXEngine__SetOverlaySlotVisibilityByPlayerView(void * this, int playerView)",
        ["RET 0x4", "+0x18", "overlay", "playerView", "remain unproven"],
        ["CDXEngine__SetOverlaySlotsEnabledForActiveViews", "+ 0x18", "playerView"],
        ["dx-engine", "overlay", "render-state"],
    ),
    "0x0044a650": target(
        "CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite",
        "void CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite(void)",
        ["RenderState_Set", "0x1b", "0x13", "0x14", "0xe", "remain unproven"],
        ["RenderState_Set", "0x1b", "0x13", "0x14", "0xe"],
        ["dx-engine", "render-state", "alpha"],
    ),
    "0x0044a690": target(
        "RenderState__Set0x89_Zero",
        "void RenderState__Set0x89_Zero(void)",
        ["RenderState_Set", "0x89", "0", "remain unproven"],
        ["RenderState_Set", "0x89", "0"],
        ["render-state"],
    ),
    "0x0044a6b0": target(
        "CDXEngine__ApplyNavMapConsoleToggle_Thunk",
        "int __thiscall CDXEngine__ApplyNavMapConsoleToggle_Thunk(void * this, int arg0, int arg1, int arg2, int arg3, int arg4)",
        ["RET 0x14", "+0x10", "navmap", "console", "remain unproven"],
        ["CDXEngine__InvalidateLandscapeTilesAndPatchSlots", "+ 0x10"],
        ["dx-engine", "navmap", "console"],
    ),
    "0x0044a6e0": target(
        "CEngine__Deserialize",
        "void __thiscall CEngine__Deserialize(void * this, void * chunkReader)",
        ["Deserialize", "RET 0x4", "+0x49c", "map-texture array", "remain unproven"],
        ["CChunkReader__GetNext", "CChunkReader__Read", "CMapTex__Deserialize", "+ 0x49c"],
        ["engine", "resource-deserialize", "map-textures"],
    ),
}

XREF_EVIDENCE = [
    ("0x0044a2d0", "0x0053e5b8", "UNCONDITIONAL_CALL"),
    ("0x0044a5f0", "0x0044a3ae", "UNCONDITIONAL_CALL"),
    ("0x0044a610", "0x00507677", "UNCONDITIONAL_CALL"),
    ("0x0044a640", "0x0053e234", "UNCONDITIONAL_CALL"),
    ("0x0044a650", "0x0053e8e2", "UNCONDITIONAL_CALL"),
    ("0x0044a690", "0x00492960", "UNCONDITIONAL_CALL"),
    ("0x0044a6b0", "0x0046c13f", "UNCONDITIONAL_CALL"),
    ("0x0044a6e0", "0x004d768d", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x0044a2d0", "0x0044a38e", "CALL", "0x005524a0"),
    ("0x0044a5f0", "0x0044a604", "RET", "0xc"),
    ("0x0044a610", "0x0044a62e", "RET", "0xc"),
    ("0x0044a640", "0x0044a64d", "RET", "0x4"),
    ("0x0044a650", "0x0044a688", "RET", ""),
    ("0x0044a690", "0x0044a6a1", "RET", ""),
    ("0x0044a6b0", "0x0044a6d1", "RET", "0x14"),
    ("0x0044a6e0", "0x0044a737", "RET", "0x4"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3", "param_4"]
STALE_NAME_TOKENS = [
    "CDXEngine__UpdateAtmosphericsAndLightMatrices",
    "CResourceAccumulator__DeserializeMapTexListAndLoadMap",
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
    dry_log_path = dry_log_path or root / "engine_render_tail_signature_dry.log"
    apply_log_path = apply_log_path or root / "engine_render_tail_signature_apply.log"
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

        tag_text = tags.get(address, {}).get("tags", "")
        expected_tags = COMMON_TAGS | set(spec["tags"])  # type: ignore[arg-type]
        for tag in expected_tags:
            if tag not in tag_text:
                failures.append(f"{address} missing tag: {tag}")

        decompile = decompile_for(decompile_dir, address)
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address} decompile missing token: {token}")

    xref_hits = 0
    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        found = any_row(
            xrefs,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("ref_type") == ref_type
            ),
        )
        if found:
            xref_hits += 1
        else:
            failures.append(f"xref evidence missing: {target_addr} <- {from_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        found = any_row(
            instructions,
            lambda row, target_addr=target_addr, instr_addr=instr_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instr_addr)
                and row.get("mnemonic") == mnemonic
                and (not operand_token or token_present(row.get("operands", ""), operand_token))
            ),
        )
        if found:
            instruction_hits += 1
        else:
            failures.append(f"instruction evidence missing: {target_addr} {instr_addr} {mnemonic} {operand_token}")

    report: dict[str, object] = {
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": expected_count,
            "metadataRows": len(metadata),
            "tagRows": len(tags),
            "xrefRows": len(xrefs),
            "instructionRows": len(instructions),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleNameHits": stale_name_hits,
            "staleSignatureHits": stale_signature_hits,
            "overclaimHits": overclaim_hits,
        },
        "failures": failures,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    output_path = args.json or (args.root / OUTPUT_NAME)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    summary = report["summary"]  # type: ignore[assignment]
    print(f"Targets: {summary['targets']}")
    print(f"Xref evidence hits: {summary['xrefEvidenceHits']}")
    print(f"Instruction evidence hits: {summary['instructionEvidenceHits']}")
    print(f"Stale name hits: {summary['staleNameHits']}")
    print(f"Stale signature hits: {summary['staleSignatureHits']}")
    print(f"Overclaim hits: {summary['overclaimHits']}")

    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:  # type: ignore[index]
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
