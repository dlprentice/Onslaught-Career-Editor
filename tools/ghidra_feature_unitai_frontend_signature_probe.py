#!/usr/bin/env python3
"""Validate the Wave368 feature/unit-AI/frontend Ghidra signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/feature-unitai-frontend-wave368/current")
OUTPUT_NAME = "feature-unitai-frontend-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "feature-unitai-frontend-wave368",
    "retail-binary-evidence",
}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004480c0": target(
        "CUnitAI__CanContinueDoorWingTransition",
        "bool __fastcall CUnitAI__CanContinueDoorWingTransition(void * unitAi)",
        ["door/wing transition", "+0x294", "spawned children", "ballistic arc", "remain unproven"],
        ["unitai", "transition-gate", "signature-hardened"],
    ),
    "0x0044ca30": target(
        "CFeature__Init",
        "void __thiscall CFeature__Init(void * this, void * init)",
        ["name/signature correction", "CActor__Init", "occupancy grid", "random sample", "remain unproven"],
        ["feature", "init", "name-corrected", "signature-hardened"],
    ),
    "0x0044cbe0": target(
        "CFeature__ShutdownAndRemoveFromWorld",
        "void __fastcall CFeature__ShutdownAndRemoveFromWorld(void * feature)",
        ["name/signature correction", "KillSamplesForThing", "RemoveUnitFromOccupancyGrid", "UpdateVisibility", "remain unproven"],
        ["feature", "shutdown", "name-corrected", "signature-hardened"],
    ),
    "0x0044cd20": target(
        "CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200",
        "void __thiscall CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200(void * this, float delta, int unused1, int unused2, int unused3)",
        ["RET 0x10", "delta", "+0xe0", "vfunc +0xc8", "remain unproven"],
        ["unitai", "engagement-metric", "signature-hardened"],
    ),
    "0x0044cee0": target(
        "CFeature__MaybeSpawnRandomPickupFromData",
        "void __fastcall CFeature__MaybeSpawnRandomPickupFromData(void * feature)",
        ["name/signature correction", "+0xe4", "CreatePickup", "randomized pickup", "owner inferred", "remain unproven"],
        ["feature", "pickup-spawn", "name-corrected", "signature-hardened"],
    ),
    "0x0044d1f0": target(
        "CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4",
        "void __fastcall CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4(void * unitAi)",
        ["SetStateTimestampCCToNow", "flag bit 4", "vfunc +0x38", "remain unproven"],
        ["unitai", "state-dispatch", "signature-hardened"],
    ),
    "0x0044d210": target(
        "CUnitAI__RenderWithStaticShadowVisibilityUpdate",
        "void __thiscall CUnitAI__RenderWithStaticShadowVisibilityUpdate(void * this, int render_context)",
        ["RET 0x4", "static shadow visibility", "CThing__Render", "remain unproven"],
        ["unitai", "render", "signature-hardened"],
    ),
    "0x0044d6f0": target(
        "CFrontEnd__RenderAndProcessModalPanel",
        "void __fastcall CFrontEnd__RenderAndProcessModalPanel(void * frontend)",
        ["modal panel", "+0x1f8c", "DrawPanel", "HandleModalPanelButton", "remain unproven"],
        ["frontend", "modal-panel", "signature-hardened"],
    ),
    "0x0044dd60": target(
        "CFrontEnd__HandleModalPanelButton",
        "void __thiscall CFrontEnd__HandleModalPanelButton(void * this, int button, int context)",
        ["RET 0x8", "button", "0x2a", "0x2b", "0x2c", "remain unproven"],
        ["frontend", "modal-panel", "button-handler", "signature-hardened"],
    ),
    "0x0044dea0": target(
        "CFrontEnd__IsMouseInputReady",
        "bool __fastcall CFrontEnd__IsMouseInputReady(void * frontend)",
        ["mouse input ready", "+0x1f8c", "+0x1f98", "remain unproven"],
        ["frontend", "mouse-input", "signature-hardened"],
    ),
    "0x0044e2c0": target(
        "CMonitor__CheckSVFAnimationAndAdvanceState",
        "int __fastcall CMonitor__CheckSVFAnimationAndAdvanceState(void * monitor)",
        ["SVF", "FindAnimationIndex", "vfunc +0x38", "remain unproven"],
        ["monitor", "animation-gate", "signature-hardened"],
    ),
    "0x0044e300": target(
        "PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300",
        "void __fastcall PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300(void * object)",
        ["owner-neutral rename", "+0x164", "attached frame", "CreatePickup", "remain unproven"],
        ["pickup-spawn", "owner-deferred", "name-corrected", "signature-hardened"],
    ),
}

VTABLE_EXPECTED = {
    2: ("0x0044cbe0", "CFeature__ShutdownAndRemoveFromWorld"),
    9: ("0x0044ca30", "CFeature__Init"),
    4: ("0x0044d210", "CUnitAI__RenderWithStaticShadowVisibilityUpdate"),
    8: ("0x0044cd20", "CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200"),
    7: ("0x0044d1f0", "CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4"),
    3: ("0x0044e2c0", "CMonitor__CheckSVFAnimationAndAdvanceState"),
}

INSTRUCTION_EVIDENCE = [
    ("0x0044ca30", "0x0044cbd6", "RET", "0x4"),
    ("0x0044cbe0", "0x0044cc08", "CALL", "0x004f41b0"),
    ("0x0044cd20", "0x0044cd36", "FSUB", "float ptr [ESP + 0x8]"),
    ("0x0044cd20", "0x0044cd7d", "RET", "0x10"),
    ("0x0044cee0", "0x0044cec8", "CALL", "dword ptr [EDX + 0x24]"),
    ("0x0044d210", "0x0044d22d", "RET", "0x4"),
    ("0x0044dd60", "0x0044ddf1", "RET", "0x8"),
    ("0x0044e2c0", "0x0044e2d7", "CALL", "0x004aa630"),
    ("0x0044e300", "0x0044e30d", "CMP", "dword ptr [EDI + 0x164]"),
]

XREF_EVIDENCE = [
    ("0x0044ca30", "005e4604", "DATA"),
    ("0x0044cbe0", "005e45e8", "DATA"),
    ("0x0044cee0", "0044ccf1", "UNCONDITIONAL_CALL"),
    ("0x0044d6f0", "00468433", "UNCONDITIONAL_CALL"),
    ("0x0044dd60", "0044d82c", "UNCONDITIONAL_CALL"),
    ("0x0044dea0", "004693d5", "UNCONDITIONAL_CALL"),
    ("0x0044e300", "0044e28e", "UNCONDITIONAL_CALL"),
]

STALE_SIGNATURE_TOKENS = ["param_1", "param_2", "param_3", "unaff_"]
STALE_NAME_TOKENS = [
    "CFeature__VFunc_09_0044ca30",
    "CFeature__VFunc_02_0044cbe0",
    "CExplosionInitThing__ctor_like_0044cee0",
    "CExplosionInitThing__ctor_like_0044e300",
]
OVERCLAIM_TOKENS = [
    "fully re'ed",
    "100% re",
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
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
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if not match:
        return {}
    return {
        "targets": int(match.group(1)),
        "changed_or_would_change": int(match.group(2)),
        "failed": int(match.group(3)),
        "dry": match.group(4) == "true",
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    vtable_path: Path | None = None,
    instructions_path: Path | None = None,
    xrefs_path: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "feature_unitai_frontend_signature_dry.log"
    apply_log_path = apply_log_path or root / "feature_unitai_frontend_signature_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"

    failures: list[str] = []
    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    vtable_rows = read_tsv(vtable_path)
    instruction_rows = read_tsv(instructions_path)
    xref_rows = read_tsv(xrefs_path)
    expected_count = len(TARGETS)

    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": True}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": False}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    stale_name_hits = 0
    stale_signature_hits = 0
    overclaim_hits = 0
    vtable_hits = 0
    instruction_hits = 0
    xref_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if row is None:
            failures.append(f"missing metadata for {address}")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"name mismatch for {address}: {row.get('name')} != {spec['name']}")
        signature = row.get("signature", "")
        if signature != spec["signature"]:
            failures.append(f"signature mismatch for {address}: {signature} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"missing comment token for {address}: {token}")
        for token in STALE_NAME_TOKENS:
            if token_present(row.get("name", ""), token):
                stale_name_hits += 1
                failures.append(f"stale name token for {address}: {token}")
        for token in STALE_SIGNATURE_TOKENS:
            if token_present(signature, token):
                stale_signature_hits += 1
                failures.append(f"stale signature token for {address}: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                overclaim_hits += 1
                failures.append(f"overclaim token for {address}: {token}")

        tag_row = tags.get(norm_addr(address))
        if tag_row is None:
            failures.append(f"missing tags for {address}")
        else:
            tag_set = set(filter(None, re.split(r"[;,]\s*", tag_row.get("tags", ""))))
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing = sorted(expected_tags - tag_set)
            if missing:
                failures.append(f"missing tags for {address}: {missing}")

    for slot_index, (expected_addr, expected_name) in VTABLE_EXPECTED.items():
        hit = any_row(
            vtable_rows,
            lambda row, slot_index=slot_index, expected_addr=expected_addr, expected_name=expected_name: (
                row.get("slot_index") == str(slot_index)
                and norm_addr(row.get("pointer_addr")) == norm_addr(expected_addr)
                and norm_addr(row.get("function_entry")) == norm_addr(expected_addr)
                and row.get("function_name") == expected_name
                and row.get("status") == "OK"
            ),
        )
        if hit:
            vtable_hits += 1
        else:
            failures.append(f"missing vtable read-back for slot {slot_index}: {expected_addr} {expected_name}")

    for target_addr, instr_addr, mnemonic, operands in INSTRUCTION_EVIDENCE:
        hit = any_row(
            instruction_rows,
            lambda row, target_addr=target_addr, instr_addr=instr_addr, mnemonic=mnemonic, operands=operands: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instr_addr)
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operands)
            ),
        )
        if hit:
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target_addr} {instr_addr} {mnemonic} {operands}")

    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        hit = any_row(
            xref_rows,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("ref_type") == ref_type
            ),
        )
        if hit:
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target_addr} <- {from_addr} {ref_type}")

    status = "PASS" if not failures else "FAIL"
    return {
        "status": status,
        "root": str(root),
        "summary": {
            "targets": expected_count,
            "metadataRows": len(metadata),
            "vtableEvidenceHits": vtable_hits,
            "instructionEvidenceHits": instruction_hits,
            "xrefEvidenceHits": xref_hits,
            "staleNameHits": stale_name_hits,
            "staleSignatureHits": stale_signature_hits,
            "overclaimHits": overclaim_hits,
        },
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    output_path = args.json or args.root / OUTPUT_NAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"status={report['status']} targets={report['summary']['targets']} "
        f"metadata={report['summary']['metadataRows']} output={output_path}"
    )
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
