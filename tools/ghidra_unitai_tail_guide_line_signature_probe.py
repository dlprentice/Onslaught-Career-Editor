#!/usr/bin/env python3
"""Validate the saved UnitAI tail / guide-line Ghidra signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/unitai-tail-guide-line-wave359/current")
OUTPUT_NAME = "unitai-tail-guide-line-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "unitai-tail-guide-line-wave359",
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
    "0x00447b10": target(
        "CUnitAI__PlayWingUnfoldedAnimationAndSetState5",
        "void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void * unitAI)",
        ["resolves wingunfolded", "+0x27c", "state 5", "occupancy grid", "remain unproven"],
        ["s_wingunfolded_00628ab0", "FindAnimationIndex", "CWorld__RemoveUnitFromOccupancyGrid_Thunk"],
        ["unitai", "door-wing", "animation"],
    ),
    "0x00447b60": target(
        "CUnitAI__HasReachedCachedAnchorPoint",
        "int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)",
        ["cached anchor", "+0x290", "+0x280/+0x284", "distance threshold", "remain unproven"],
        ["+ 0x290", "+ 0x280", "SQRT"],
        ["unitai", "door-wing", "cached-anchor"],
    ),
    "0x00447bb0": target(
        "CUnitAI__GetOrGenerateCachedAnchorPoint",
        "void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)",
        ["cached anchor", "RET 0x4", "outAnchorPoint", "+0x280/+0x28c", "remain unproven"],
        ["CUnitAI__IsCachedAnchorPointValid", "outAnchorPoint", "+ 0x280", "+ 0x28c"],
        ["unitai", "door-wing", "cached-anchor"],
    ),
    "0x00447d50": target(
        "CUnitAI__IsCachedAnchorPointValid",
        "int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)",
        ["cached anchor", "CMapWho", "collision", "occupancy bitmask", "remain unproven"],
        ["CMapWho__GetFirstEntryWithinRadius", "CMapWho__GetNextEntryWithinRadius", "+ 0x27c"],
        ["unitai", "door-wing", "cached-anchor", "collision"],
    ),
    "0x00447fa0": target(
        "CUnitAI__AdvanceDoorWingAnimationState",
        "int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void * unitAI)",
        ["door-wing animation", "dooropening", "doorclosing", "wingfolded", "remain unproven"],
        ["s_dooropening_00628a98", "s_doorclosing_00628a8c", "s_wingunfolded_00628ab0"],
        ["unitai", "door-wing", "animation-state"],
    ),
    "0x00448110": target(
        "CUnitAI__SetDoorWingState6",
        "void __fastcall CUnitAI__SetDoorWingState6(void * unitAI)",
        ["state +0x27c", "to 6", "remain unproven"],
        ["+ 0x27c", "return"],
        ["unitai", "door-wing", "state-transition"],
    ),
    "0x00448120": target(
        "CUnitAI__SetDoorWingState7AndMirrorYawOffset",
        "void __fastcall CUnitAI__SetDoorWingState7AndMirrorYawOffset(void * unitAI)",
        ["state +0x27c", "to 7", "mirrors yaw/offset field +0x2a4", "remain unproven"],
        ["+ 0x27c", "+ 0x2a4", "_DAT_005d8568"],
        ["unitai", "door-wing", "state-transition"],
    ),
    "0x00448170": target(
        "CDropship__TraceGroundAndSpawnThrusterDust",
        "void __stdcall CDropship__TraceGroundAndSpawnThrusterDust(void * effectPoint, void * transformMatrix)",
        ["previously mislabeled", "thruster dust", "static heightfield", "RET 0x8", "remain unproven"],
        ["CStaticShadows__TraceSegmentAgainstHeightfield", "CParticleManager__CreateEffect", "CLine__ScalarDeletingDestructor"],
        ["dropship", "thruster", "heightfield", "particle-effect"],
    ),
    "0x0047e290": target(
        "CGuide__ctor_base",
        "void * __thiscall CGuide__ctor_base(void * this, void * guideOwner)",
        ["CGuide base constructor", "RET 0x4", "base vtable", "guideOwner", "remain unproven"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dbdc4", "guideOwner", "return this"],
        ["guide", "constructor", "base-ctor"],
    ),
    "0x00415d70": target(
        "CBoatGuide__ctor",
        "void * __thiscall CBoatGuide__ctor(void * this, void * guideOwner)",
        ["CBoatGuide constructor", "CGuide__ctor_base", "0x005d8d5c", "CBoat__Init", "remain unproven"],
        ["CGuide__ctor_base", "PTR_SharedVFunc__NoOpOneArg_004014c0_005d8d5c", "return this"],
        ["boat-guide", "guide", "constructor"],
    ),
}

XREF_EVIDENCE = [
    ("0x00447b10", "0x005e1fb8", "DATA"),
    ("0x00447b60", "0x0044866d", "UNCONDITIONAL_CALL"),
    ("0x00447bb0", "0x00448690", "UNCONDITIONAL_CALL"),
    ("0x00447d50", "0x00447a57", "UNCONDITIONAL_CALL"),
    ("0x00447fa0", "0x005e1ec4", "DATA"),
    ("0x00448110", "0x004486dc", "UNCONDITIONAL_CALL"),
    ("0x00448120", "0x00448737", "UNCONDITIONAL_CALL"),
    ("0x00448170", "0x004472b2", "UNCONDITIONAL_CALL"),
    ("0x00448170", "0x004473f9", "UNCONDITIONAL_CALL"),
    ("0x0047e290", "0x00446ee0", "UNCONDITIONAL_CALL"),
    ("0x00415d70", "0x00414f22", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00447b10", "0x00447b29", "CALL", "0x004aa630"),
    ("0x00447b60", "0x00447b60", "MOV", "+ 0x290"),
    ("0x00447bb0", "0x00447d3e", "RET", "0x4"),
    ("0x00447d50", "0x00447d8d", "CALL", "0x00491ea0"),
    ("0x00447fa0", "0x00447fc7", "CALL", "0x004aa630"),
    ("0x00448110", "0x00448110", "MOV", "+ 0x27c"),
    ("0x00448120", "0x00448136", "FSTP", "+ 0x2a4"),
    ("0x00448170", "0x0044835c", "RET", "0x8"),
    ("0x0047e290", "0x0047e2c8", "RET", "0x4"),
    ("0x00415d70", "0x00415d78", "CALL", "0x0047e290"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3"]
STALE_NAME_TOKENS = [
    "CLine__ctor_like_00448170",
    "CGuide__ctor_like_0047e290",
]
ALLOWED_DECOMPILE_STALE_TOKENS = {
    "0x00448170": {"CLine__ctor_like_00448170"},
}
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
    dry_log_path = dry_log_path or root / "unitai_tail_guide_line_signature_dry.log"
    apply_log_path = apply_log_path or root / "unitai_tail_guide_line_signature_apply.log"
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
            allowed_tokens = ALLOWED_DECOMPILE_STALE_TOKENS.get(address, set())
            if token in decompile and token != spec["name"] and token not in allowed_tokens:
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
