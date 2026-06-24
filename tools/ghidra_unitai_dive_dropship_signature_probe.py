#!/usr/bin/env python3
"""Validate the saved UnitAI/DiveBomber/Dropship signature correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/unitai-dive-dropship-wave358/current")
OUTPUT_NAME = "unitai-dive-dropship-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "unitai-dive-dropship-wave358",
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
    "0x00445380": target(
        "CDiveBomberAI__scalar_deleting_dtor",
        "void * __thiscall CDiveBomberAI__scalar_deleting_dtor(void * this, int flags)",
        ["scalar-deleting destructor", "CDiveBomberAI", "OID__FreeObject", "remain unproven"],
        ["CDiveBomberAI__dtor_base", "OID__FreeObject", "return this"],
        ["divebomber-ai", "destructor", "scalar-deleting-dtor"],
    ),
    "0x004453a0": target(
        "CDiveBomberAI__dtor_base",
        "void __fastcall CDiveBomberAI__dtor_base(void * this)",
        ["destructor-base", "CDiveBomberAI", "CSPtrSet__Remove", "CMonitor__Shutdown", "remain unproven"],
        ["CSPtrSet__Remove", "CMonitor__Shutdown"],
        ["divebomber-ai", "destructor", "monitor-cleanup"],
    ),
    "0x00445440": target(
        "CDiveBomberGuide__scalar_deleting_dtor",
        "void * __thiscall CDiveBomberGuide__scalar_deleting_dtor(void * this, int flags)",
        ["scalar-deleting destructor", "CDiveBomberGuide", "OID__FreeObject", "remain unproven"],
        ["CDiveBomberGuide__dtor_base", "OID__FreeObject", "return this"],
        ["divebomber-guide", "destructor", "scalar-deleting-dtor"],
    ),
    "0x00445460": target(
        "CDiveBomberGuide__dtor_base",
        "void __fastcall CDiveBomberGuide__dtor_base(void * this)",
        ["destructor-base", "CDiveBomberGuide", "+0x2c", "CMonitor__Shutdown", "remain unproven"],
        ["CSPtrSet__Remove", "CMonitor__Shutdown"],
        ["divebomber-guide", "destructor", "monitor-cleanup"],
    ),
    "0x00445570": target(
        "CUnitAI__PlayOpenAnimationIfState1Or3",
        "void __fastcall CUnitAI__PlayOpenAnimationIfState1Or3(void * unitAI)",
        ["open animation", "+0x280", "states 1 or 3", "vfunc +0xf0", "remain unproven"],
        ["FindAnimationIndex", "+ 0x280", "+ 0xf0"],
        ["unitai", "door-wing", "animation"],
    ),
    "0x004455c0": target(
        "CUnitAI__PlayCloseAnimationIfState0Or2",
        "void __fastcall CUnitAI__PlayCloseAnimationIfState0Or2(void * unitAI)",
        ["close animation", "+0x280", "states 0 or 2", "vfunc +0xf0", "remain unproven"],
        ["s_close_006289e4", "FindAnimationIndex", "+ 0x280"],
        ["unitai", "door-wing", "animation"],
    ),
    "0x00445610": target(
        "CUnitAI__AdvanceOpenCloseShootAnimationState",
        "int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void * unitAI)",
        ["door-wing state helper", "+0x280", "shoot/close/open-style animation names", "remain unproven"],
        ["s_shoot_006289ec", "s_close_006289e4", "+ 0x280"],
        ["unitai", "door-wing", "animation-state"],
    ),
    "0x00445ad0": target(
        "CUnitAI__UpdateDoorWingEngagement_CloseRange",
        "double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)",
        ["close-range", "+0x68", "+0x70", "open/close animation helpers", "remain unproven"],
        ["CUnitAI__PlayOpenAnimationIfState1Or3", "CUnitAI__PlayCloseAnimationIfState0Or2", "+ 0x68"],
        ["unitai", "door-wing", "engagement"],
    ),
    "0x00445f40": target(
        "CUnitAI__UpdateDoorWingEngagement_MidRange",
        "double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)",
        ["mid-range", "+0x6c", "attached target/weapon context", "vfunc +0xf4", "remain unproven"],
        ["CUnitAI__CallAttachedNodeVFunc14IfPresent", "+ 0x6c", "+ 0xf4"],
        ["unitai", "door-wing", "engagement"],
    ),
    "0x00446150": target(
        "CUnitAI__UpdateDoorWingEngagement_LongRange",
        "double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)",
        ["long-range", "+0x68", "+0x70", "EnterDoorWingOpenTrackingState", "remain unproven"],
        ["CUnitAI__EnterDoorWingOpenTrackingState", "CUnitAI__PlayCloseAnimationIfState0Or2", "+ 0x68"],
        ["unitai", "door-wing", "engagement"],
    ),
    "0x00446400": target(
        "CUnitAI__EnterDoorWingOpenTrackingState",
        "void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)",
        ["enters open tracking", "+0x68", "+0x70", "CUnitAI__PlayOpenAnimationIfState1Or3", "remain unproven"],
        ["CUnitAI__PlayOpenAnimationIfState1Or3", "+ 0x68", "+ 0x70"],
        ["unitai", "door-wing", "state-transition"],
    ),
    "0x00446d70": target(
        "CDropship__Init",
        "void __thiscall CDropship__Init(void * this, void * initThing)",
        ["CDropship init", "wingflat", "doorclosed", "Thruster Dust Effect", "remain unproven"],
        ["s_wingflat_00628a74", "s_doorclosed_00628a80", "CMCDropship__Ctor", "s_Thruster_Dust_Effect_00628a3c"],
        ["dropship", "init", "thruster"],
    ),
    "0x00447040": target(
        "CDropshipAI__scalar_deleting_dtor",
        "void * __thiscall CDropshipAI__scalar_deleting_dtor(void * this, int flags)",
        ["scalar-deleting destructor", "CDropshipAI", "OID__FreeObject", "remain unproven"],
        ["CDropshipAI__dtor_base", "OID__FreeObject", "return this"],
        ["dropship-ai", "destructor", "scalar-deleting-dtor"],
    ),
    "0x00447060": target(
        "CDropshipAI__dtor_base",
        "void __fastcall CDropshipAI__dtor_base(void * this)",
        ["destructor-base", "CDropshipAI", "CSPtrSet__Remove", "CMonitor__Shutdown", "remain unproven"],
        ["CSPtrSet__Remove", "CMonitor__Shutdown"],
        ["dropship-ai", "destructor", "monitor-cleanup"],
    ),
    "0x00447100": target(
        "CDropship__dtor_base",
        "void __fastcall CDropship__dtor_base(void * this)",
        ["destructor-base", "CDropship", "occupancy grid", "CAirUnit__dtor_base", "remain unproven"],
        ["CWorld__RemoveUnitFromOccupancyGrid_Thunk", "CAirUnit__dtor_base"],
        ["dropship", "destructor", "airunit"],
    ),
    "0x00447120": target(
        "CDropship__ProcessDoorThrustersAndChildUnits",
        "void __fastcall CDropship__ProcessDoorThrustersAndChildUnits(void * this)",
        ["CDropship vtable", "dooropening", "doorclosing", "thruster", "child-unit linked lists", "remain unproven"],
        ["s_dooropening_00628a98", "s_doorclosing_00628a8c", "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight"],
        ["dropship", "door-state", "thruster", "child-units"],
    ),
    "0x00447a40": target(
        "CUnitAI__SetDoorWingState2AndClampYawDelta",
        "void __fastcall CUnitAI__SetDoorWingState2AndClampYawDelta(void * unitAI)",
        ["state +0x27c to 2", "+0x2a0", "cached anchor", "remain unproven"],
        ["CUnitAI__IsCachedAnchorPointValid", "+ 0x27c", "+ 0x2a0"],
        ["unitai", "door-wing", "state-transition"],
    ),
    "0x00447ac0": target(
        "CUnitAI__PlayWingFoldedAnimationAndSetState3",
        "void __fastcall CUnitAI__PlayWingFoldedAnimationAndSetState3(void * unitAI)",
        ["wingfolded animation", "+0x27c", "+0x290", "occupancy/shadow state", "remain unproven"],
        ["s_wingfolded_00628aa4", "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk", "FindAnimationIndex"],
        ["unitai", "door-wing", "animation"],
    ),
}


XREF_EVIDENCE = [
    ("0x00445380", "0x005db1b0", "DATA"),
    ("0x00445440", "0x005db184", "DATA"),
    ("0x00445610", "0x005e1328", "DATA"),
    ("0x00446d70", "0x005e1dfc", "DATA"),
    ("0x00447040", "0x005db1f8", "DATA"),
    ("0x00447100", "0x005e1de0", "DATA"),
    ("0x00447120", "0x005e1ee0", "DATA"),
    ("0x00447a40", "0x005e1fb0", "DATA"),
    ("0x00447ac0", "0x005e1fb4", "DATA"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00445380", "0x0044539d", "RET", "0x4"),
    ("0x004453a0", "0x0044542a", "CALL", "0x004bac40"),
    ("0x00445440", "0x0044545d", "RET", "0x4"),
    ("0x00445460", "0x004454a8", "CALL", "0x004bac40"),
    ("0x00445570", "0x004455ab", "CALL", "[EDI + 0xf0]"),
    ("0x004455c0", "0x004455fa", "CALL", "[EDI + 0xf0]"),
    ("0x00445610", "0x00445667", "CALL", "[EDI + 0xf0]"),
    ("0x00445ad0", "0x00445d84", "CALL", "0x00445570"),
    ("0x00445f40", "0x004460d8", "CALL", "[EDX + 0xf4]"),
    ("0x00446150", "0x004463b6", "CALL", "0x00446400"),
    ("0x00446400", "0x00446445", "CALL", "0x00445570"),
    ("0x00446d70", "0x00446e96", "CALL", "0x00496090"),
    ("0x00447040", "0x0044705d", "RET", "0x4"),
    ("0x00447060", "0x004470ea", "CALL", "0x004bac40"),
    ("0x00447100", "0x00447110", "CALL", "0x00402d30"),
    ("0x00447120", "0x004478a3", "CALL", "0x00402dd0"),
    ("0x00447a40", "0x00447a57", "CALL", "0x00447d50"),
    ("0x00447ac0", "0x00447af8", "CALL", "0x004aa630"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3"]
STALE_NAME_TOKENS = [
    "CUnitAI__ctor_like_004453a0",
    "CUnitAI__ctor_like_00447060",
    "VFunc_01_00445380",
    "VFunc_01_00445440",
    "VFunc_01_00447040",
    "VFuncSlot_1c_00447120",
]
EXTERNAL_STALE_REFERENCE_TOKENS = [
    "CGuide__ctor_like_0047e290",
    "CLine__ctor_like_00448170",
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


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def decompile_for(decompile_dir: Path, address: str, name: str) -> str:
    exact = decompile_dir / f"{address[2:]}_{name}.c"
    if exact.exists():
        return read_text(exact)
    matches = sorted(decompile_dir.glob(f"{address[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


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
    dry_log_path = dry_log_path or root / "unitai_dive_dropship_signature_dry.log"
    apply_log_path = apply_log_path or root / "unitai_dive_dropship_signature_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    expected_count = len(TARGETS)
    if dry_summary != {"targets": expected_count, "updated": 0, "skipped": expected_count, "failed": 0, "dry": True}:
        failures.append(f"dry summary mismatch: {dry_summary}")
    if apply_summary != {"targets": expected_count, "updated": expected_count, "skipped": 0, "failed": 0, "dry": False}:
        failures.append(f"apply summary mismatch: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)

    stale_name_hits = 0
    stale_signature_hits = 0
    external_stale_reference_hits = 0
    overclaim_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is {row.get('status')}")
        name = row.get("name", "")
        if name != spec["name"]:
            failures.append(f"{address} name mismatch: {name} != {spec['name']}")
        signature = row.get("signature", "")
        if signature != spec["signature"]:
            failures.append(f"{address} signature mismatch: {signature} != {spec['signature']}")
        for token in STALE_SIGNATURE_TOKENS:
            if token in signature:
                stale_signature_hits += 1
                failures.append(f"{address} stale signature token present: {token}")
        for token in STALE_NAME_TOKENS:
            if token in name:
                stale_name_hits += 1
                failures.append(f"{address} stale name token present: {token}")

        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if str(token) not in comment:
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment:
                overclaim_hits += 1
                failures.append(f"{address} comment overclaim token present: {token}")

        tag_row = tags.get(address)
        tag_text = tag_row.get("tags", "") if tag_row else ""
        for tag in sorted(COMMON_TAGS | set(spec["tags"])):  # type: ignore[arg-type]
            if tag not in tag_text:
                failures.append(f"{address} tag missing: {tag}")

        decompile = decompile_for(decompile_dir, address, str(spec["name"]))
        if not decompile:
            failures.append(f"{address} decompile missing")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if str(token) not in decompile:
                failures.append(f"{address} decompile missing token: {token}")
        for token in STALE_NAME_TOKENS:
            if token in decompile and token not in str(spec["name"]):
                stale_name_hits += 1
                failures.append(f"{address} stale decompile token present: {token}")
        for token in EXTERNAL_STALE_REFERENCE_TOKENS:
            if token in decompile:
                external_stale_reference_hits += 1

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
            failures.append(f"xref evidence missing: {target_addr} from {from_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target_addr=target_addr, instr_addr=instr_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instr_addr)
                and row.get("mnemonic") == mnemonic
                and str(operand_token) in row.get("operands", "")
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"instruction evidence missing: {target_addr} {instr_addr} {mnemonic} {operand_token}")

    report = {
        "schema": "ghidra-unitai-dive-dropship-signature.v1",
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": expected_count,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleNameHits": stale_name_hits,
            "staleSignatureHits": stale_signature_hits,
            "externalStaleReferenceHits": external_stale_reference_hits,
            "overclaimHits": overclaim_hits,
        },
        "inputs": {
            "dryLog": dry_log_path.as_posix(),
            "applyLog": apply_log_path.as_posix(),
            "metadata": metadata_path.as_posix(),
            "tags": tags_path.as_posix(),
            "xrefs": xrefs_path.as_posix(),
            "instructions": instructions_path.as_posix(),
            "decompileDir": decompile_dir.as_posix(),
        },
        "failures": failures,
        "notProven": [
            "This does not prove exact Stuart-source method identity.",
            "This does not prove concrete UnitAI, DiveBomber, Dropship, guide, or component layouts.",
            "This does not prove runtime AI, door, wing, thruster, child-unit, BEA launch, patching, or rebuild behavior.",
        ],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="return non-zero if validation fails")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(root=args.root)
    out = args.root / OUTPUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print("Ghidra UnitAI/DiveBomber/Dropship signature tranche probe")
        print(f"Status: {report['status']}")
        print(f"Output: {out.as_posix()}")
        print(f"Targets: {summary['targets']}")
        print(f"Xref evidence hits: {summary['xrefEvidenceHits']}")
        print(f"Instruction evidence hits: {summary['instructionEvidenceHits']}")
        print(f"Stale name hits: {summary['staleNameHits']}")
        print(f"Stale signature hits: {summary['staleSignatureHits']}")
        print(f"External stale reference hits: {summary['externalStaleReferenceHits']}")
        print(f"Overclaim hits: {summary['overclaimHits']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
