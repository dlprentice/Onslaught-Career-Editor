#!/usr/bin/env python3
"""Validate the saved Wave364 early high-signal Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/early-high-signal-wave364/current")
OUTPUT_NAME = "early-high-signal-correction.json"

COMMON_TAGS = {
    "static-reaudit",
    "early-high-signal-wave364",
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
    "0x00440b70": target(
        "CDamage__ctor_clear_head_and_init_flag",
        "void __fastcall CDamage__ctor_clear_head_and_init_flag(void * damage)",
        ["owner correction", "damage-object head", "+0x1588c", "CDamage__Init", "remain unproven"],
        ["*(undefined4 *)damage = 0", "+ 0x1588c"],
        ["damage-system", "owner-corrected"],
    ),
    "0x00441490": target(
        "CDXEngine__UpdateWrappedThingPositionsAndDistance",
        "void __cdecl CDXEngine__UpdateWrappedThingPositionsAndDistance(float camera_x, float camera_y, float camera_z)",
        ["CDXEngine__Render", "wraps positions", "+0x80", "mapwho position", "remain unproven"],
        ["camera_x", "camera_y", "camera_z", "CStaticShadows__SampleShadowHeightBilinear", "CMapWhoEntry__UpdatePosition"],
        ["dx-engine", "world-wrap", "signature-hardened"],
    ),
    "0x004416e0": target(
        "CConsole__ResetStatusHistoryBuffer",
        "void __fastcall CConsole__ResetStatusHistoryBuffer(void * console)",
        ["owner correction", "30 0x50-byte text slots", "+0x9e4", "+0x9e8", "remain unproven"],
        ["0x1e", "+ 0x9e4", "+ 0x9e8", "DAT_00662dd0"],
        ["console", "status-history", "owner-corrected"],
    ),
    "0x004419e0": target(
        "CConsole__RenderStatusHistoryOverlay",
        "void __fastcall CConsole__RenderStatusHistoryOverlay(void * console)",
        ["owner correction", "draws up to six recent ring-buffer lines", "Text__AsciiToWideScratch", "CDXFont__DrawText", "remain unproven"],
        ["Text__AsciiToWideScratch", "CDXFont__DrawText", "iVar5 < 6"],
        ["console", "status-history", "owner-corrected"],
    ),
    "0x00441e50": target(
        "CDebugMarkers__Shutdown",
        "void __fastcall CDebugMarkers__Shutdown(void * * head_ref)",
        ["owner correction", "global marker head passed by reference", "OID__FreeObject", "CGame__ShutdownRestartLoop", "remain unproven"],
        ["OID__FreeObject", "DAT_0066ffb0", "*head_ref"],
        ["debug-marker", "owner-corrected"],
    ),
    "0x00441ea0": target(
        "CDebugMarkers__Render",
        "void __fastcall CDebugMarkers__Render(void * debug_markers)",
        ["owner correction", "DEBUGMARKERS.Render", "default mesh texture", "renders debug volume", "remain unproven"],
        ["CThing__RenderDebugVolumeOverlay", "CDXFont__DrawText", "s_meshtex_default_tga_00625498"],
        ["debug-marker", "render", "owner-corrected"],
    ),
    "0x004422d0": target(
        "CDebugMarker__ctor",
        "void * __fastcall CDebugMarker__ctor(void * this)",
        ["owner correction", "global DAT_0066ffb0 marker list head", "default size/transform values", "+0x98", "remain unproven"],
        ["DAT_0066ffb0", "+ 0x98", "return this"],
        ["debug-marker", "constructor", "owner-corrected"],
    ),
    "0x00442380": target(
        "CDebugMarker__UnlinkFromGlobalList",
        "void __fastcall CDebugMarker__UnlinkFromGlobalList(void * this)",
        ["owner correction", "unlink", "global DAT_0066ffb0 singly-linked marker list", "OID__FreeObject", "remain unproven"],
        ["DAT_0066ffb0", "*(int *)this"],
        ["debug-marker", "unlink", "owner-corrected"],
    ),
}

XREF_EVIDENCE = [
    ("0x00440b70", "0x005446c5", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00441490", "0x0053e56c", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
    ("0x004416e0", "0x004efb65", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
    ("0x004416e0", "0x004efb6f", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
    ("0x004419e0", "0x0047182c", "FrontendUpdate_CheatChecks", "UNCONDITIONAL_CALL"),
    ("0x00441e50", "0x0046cbe4", "CGame__ShutdownRestartLoop", "UNCONDITIONAL_CALL"),
    ("0x00441ea0", "0x0053e826", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
    ("0x004422d0", "0x004e1ca2", "CSoundManager__UpdateStatus", "UNCONDITIONAL_CALL"),
    ("0x00442380", "0x004e2b5f", "CSoundManager__ReleaseSoundEventNode", "UNCONDITIONAL_CALL"),
    ("0x00442380", "0x004e1dcd", "CSoundManager__UpdateStatus", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00440b70", "0x00440b78", "MOV", "[EAX + 0x1588c]"),
    ("0x00441490", "0x004414e4", "FSTP", "[ESI + 0x80]"),
    ("0x004416e0", "0x0044170b", "MOV", "[ECX + 0x9e8]"),
    ("0x004419e0", "0x00441ade", "CALL", "0x00540640"),
    ("0x00441e50", "0x00441e86", "CALL", "0x00549220"),
    ("0x00441ea0", "0x00441f4d", "CALL", "dword ptr [EDX]"),
    ("0x004422d0", "0x004422dd", "MOV", "[0x0066ffb0]"),
    ("0x00442380", "0x0044238b", "MOV", "[0x0066ffb0]"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3"]
STALE_NAME_TOKENS = [
    "CUnitAI__ResetPrimaryAndTailSentinels",
    "CUnit__ResetPerSlotCooldownTables",
    "FrontendUpdate_CheatChecks__RenderCheatStatusText",
    "CGame__FreeObjectIfPresent",
    "CDXEngine__RenderWorldDebugTextBillboards",
    "CSoundManager__SoundEventNode__Ctor",
    "CSoundManager__SoundEventNode__UnlinkFromGlobalList",
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


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path, *, unescape_comment: bool = False) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if unescape_comment:
        for row in rows:
            row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


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
    dry_log_path = dry_log_path or root / "early_high_signal_correction_dry.log"
    apply_log_path = apply_log_path or root / "early_high_signal_correction_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
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
            if token in name and name != spec["name"]:
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
                failures.append(f"{address} tag missing: {tag}")

        decompile_text = decompile_for(decompile_dir, address)
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address} decompile missing token: {token}")

    xref_hits = 0
    for target_addr, from_addr, from_name, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target_addr=target_addr, from_addr=from_addr, from_name=from_name, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == target_addr
                and norm_addr(row.get("from_addr")) == from_addr
                and from_name in row.get("from_function", "")
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"xref evidence missing: {target_addr} from {from_addr} {from_name} {ref_type}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target_addr=target_addr, instruction_addr=instruction_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == target_addr
                and norm_addr(row.get("instruction_addr")) == instruction_addr
                and row.get("mnemonic") == mnemonic
                and operand_token in row.get("operands", "")
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"instruction evidence missing: {target_addr} {instruction_addr} {mnemonic} {operand_token}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-early-high-signal-correction.v1",
        "status": status,
        "classification": "owner-name-signature-comment-corrections" if status == "PASS" else "blocked",
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
        "targets": [{"address": address, "name": spec["name"]} for address, spec in TARGETS.items()],
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project has corrected owner/name/signature/comment/tag state for the selected Wave364 functions.",
            "The read-back evidence separates console status-history helpers from frontend cheat checks and separates debug markers from sound events.",
            "The damage helper at 0x00440b70 is no longer recorded as a CUnitAI helper in saved metadata.",
        ],
        "notProven": [
            "This does not prove runtime behavior, final concrete layouts, local variable recovery, or rebuild parity.",
            "This does not create new function boundaries for adjacent no-function debug-marker helpers.",
            "This does not complete the broader static re-audit queue or make the 20% proxy a milestone.",
        ],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero when the report fails.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    out_path = args.out or args.root / OUTPUT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Status: {report['status']}")
    print(json.dumps(report["summary"], sort_keys=True))
    print(f"Wrote: {out_path}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
