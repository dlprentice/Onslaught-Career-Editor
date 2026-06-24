#!/usr/bin/env python3
"""Validate the Wave398 high-level collision detector Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "collision-hl-wave398" / "current"

COMMON_TAGS = {"static-reaudit", "collision-hl-wave398", "hlcollision", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    instruction_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "instructionTokens": instruction_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00480a30": target(
        "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
        "void __thiscall CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions(void * this, void * collision_component)",
        ["corrects the older CCollisionSeekingRound owner label", "stores collision_component", "neighbor MapWho sectors", "top-layer quad children", "unexpected collision change", "runtime collision behavior", "rebuild parity remain unproven"],
        ["CMapWho__WorldToSector", "CMapWho__IsEntryInBounds", "CCollisionSeekingRound__IterSetHeadFromMapWhoEntry", "CHLCollisionDetector__DispatchCollisionEventForPair"],
        ["MOV dword ptr [EDI + 0x8], EAX", "CALL 0x00492670", "CALL 0x00480e10"],
        ["owner-corrected", "sector-scan", "signature-corrected", "comment-hardened"],
        ["CCollisionSeekingRound__InitWithSound"],
    ),
    "0x00480c90": target(
        "CHLCollisionDetector__HandleCollisionEnter",
        "void __thiscall CHLCollisionDetector__HandleCollisionEnter(void * this, void * candidate_component)",
        ["enter-event callback", "checks counter", "targeting positions", "0x100 collision filter", "scheduled collision context", "runtime collision behavior", "rebuild parity remain unproven"],
        ["DAT_0067a540", "CUnitAI__GetWorldPositionForTargeting", "CHLCollisionDetector__DispatchCollisionEventForPair", "0x100"],
        ["CALL dword ptr [EDX + 0x28]", "RET 0x4"],
        ["enter-callback", "signature-corrected", "comment-hardened"],
        ["CHLCollisionDetector__HandleScheduledCollisionEvent", "CHLCollisionDetector__DispatchCollisionEventForPair"],
    ),
    "0x00480db0": target(
        "CHLCollisionDetector__HandleCollisionExit",
        "void __thiscall CHLCollisionDetector__HandleCollisionExit(void * this, void * candidate_component)",
        ["exit-event callback", "null/self candidates", "mutual collision filters", "collision-changed flag", "runtime collision behavior", "rebuild parity remain unproven"],
        ["CHLCollisionDetector__DispatchCollisionEventForPair", "s_WARNING__Unexpected_collision_ch", "+ 0x10"],
        ["PUSH ESI", "RET 0x4"],
        ["exit-callback", "signature-corrected", "comment-hardened"],
        ["CHLCollisionDetector__ProcessMapWhoCollisionSweep"],
    ),
    "0x00480e10": target(
        "CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions",
        "void __thiscall CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions(void * this, void * mapwho_entry_or_quad_node)",
        ["corrects the older CCollisionSeekingRound owner label", "recursively traverses", "shared MapWho iterator", "candidate collision components", "unexpected collision change", "runtime collision behavior", "rebuild parity remain unproven"],
        ["CCollisionSeekingRound__IterSetHeadFromMapWhoEntry", "CCollisionSeekingRound__GetCollisionComponentOrNull", "CHLCollisionDetector__DispatchCollisionEventForPair"],
        ["CALL 0x00480e10", "CALL 0x00491d80", "RET 0x4"],
        ["owner-corrected", "quad-traversal", "signature-corrected", "comment-hardened"],
        ["CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions", "CHLCollisionDetector__ProcessMapWhoCollisionSweep"],
    ),
    "0x00480ed0": target(
        "CHLCollisionDetector__DispatchCollisionEventForPair",
        "void __thiscall CHLCollisionDetector__DispatchCollisionEventForPair(void * this, void * candidate_component)",
        ["pair dispatcher", "event queue/list appears too large", "targeting positions", "separation distance", "EVENT_MANAGER", "2000", "runtime collision behavior", "rebuild parity remain unproven"],
        ["s_WARNING__Object_colliding_with_t", "CUnitAI__GetWorldPositionForTargeting", "CEventManager__AddEvent_AtTime", "CHLCollisionDetector__HandleCollisionEnter"],
        ["CALL 0x00441740", "FSQRT", "RET 0x4"],
        ["event-dispatch", "signature-corrected", "comment-hardened"],
        ["CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions", "CHLCollisionDetector__HandleCollisionExit"],
    ),
    "0x00481060": target(
        "CHLCollisionDetector__ProcessMapWhoCollisionSweep",
        "void __thiscall CHLCollisionDetector__ProcessMapWhoCollisionSweep(void * this, void * previous_sector, void * current_sector)",
        ["map/who sweep", "previous and current sectors", "neighbor cells", "exit callbacks", "candidate pair collisions", "runtime collision behavior", "rebuild parity remain unproven"],
        ["CHLCollisionDetector__HandleCollisionExit", "CHLCollisionDetector__DispatchCollisionEventForPair", "CCollisionSeekingRound__IterSetHeadFromMapWhoEntry"],
        ["CALL 0x00480db0", "CALL 0x00480e10", "RET 0x8"],
        ["mapwho-sweep", "signature-corrected", "comment-hardened"],
        ["CCollisionSeekingRound__ProcessMapWhoCollisionSweep"],
    ),
    "0x004812d0": target(
        "CHLCollisionDetector__HandleScheduledCollisionEvent",
        "void __thiscall CHLCollisionDetector__HandleScheduledCollisionEvent(void * this, void * event)",
        ["renames the vfunc-style label", "scheduled collision event handler", "event number 2000", "event pointer for reuse", "HandleCollisionEnter", "runtime collision behavior", "rebuild parity remain unproven"],
        ["2000", "+ 0xc", "CHLCollisionDetector__HandleCollisionEnter", "+ 0x10"],
        ["CMP word ptr [ECX + 0x4], 0x7d0", "CALL 0x00480c90", "RET 0x4"],
        ["scheduled-event", "name-corrected", "signature-corrected", "comment-hardened"],
        ["005dbf78"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 3, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 7, "skipped": 0, "renamed": 3, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime collision behavior proven",
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
        for key in ("address", "target_addr", "from_function_addr", "function_entry", "entry_addr"):
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


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "would_rename": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "would_rename": int(match.group(4)),
        "missing": int(match.group(5)),
        "bad": int(match.group(6)),
    }


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    failures: list[str] = []
    metadata_rows = read_tsv(args.metadata)
    tags_rows = read_tsv(args.tags)
    xref_text = read_text(args.xrefs)
    instruction_text = read_text(args.instructions)
    public_note_text = read_text(args.public_note)

    if not metadata_rows:
        failures.append(f"missing or empty metadata: {args.metadata}")
    if not tags_rows:
        failures.append(f"missing or empty tags: {args.tags}")
    if not xref_text:
        failures.append(f"missing or empty xrefs: {args.xrefs}")
    if not instruction_text:
        failures.append(f"missing or empty instructions: {args.instructions}")
    if not public_note_text:
        failures.append(f"missing or empty public note: {args.public_note}")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: expected name {spec['name']}, got {row.get('name')}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: expected signature {spec['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token present in comment: {token!r}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            tags = parse_tags(tag_row.get("tags", ""))
            for tag in spec["tags"]:  # type: ignore[index]
                if str(tag) not in tags:
                    failures.append(f"{address}: missing tag {tag!r}")

        decompile = decompile_text_for(args.decompile_dir, address)
        if not decompile:
            failures.append(f"{address}: missing decompile export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")
        for token in spec["instructionTokens"]:  # type: ignore[index]
            if not token_present(instruction_text, str(token)):
                failures.append(f"{address}: missing instruction token {token!r}")
        for token in spec["xrefTokens"]:  # type: ignore[index]
            if not token_present(xref_text, str(token)):
                failures.append(f"{address}: missing xref token {token!r}")

    for token in (
        "0x00480a30",
        "0x00480c90",
        "0x00480db0",
        "0x00480e10",
        "0x00480ed0",
        "0x00481060",
        "0x004812d0",
        "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
        "CHLCollisionDetector__HandleCollisionEnter",
        "CHLCollisionDetector__HandleCollisionExit",
        "CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions",
        "CHLCollisionDetector__DispatchCollisionEventForPair",
        "CHLCollisionDetector__ProcessMapWhoCollisionSweep",
        "CHLCollisionDetector__HandleScheduledCollisionEvent",
        "does not prove runtime collision behavior",
        "does not prove rebuild parity",
    ):
        if not token_present(public_note_text, token):
            failures.append(f"public note missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        if token_present(public_note_text, token):
            failures.append(f"public note overclaim token present: {token!r}")

    dry_summary = parse_summary(read_text(args.dry_log))
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, got {dry_summary}")
    apply_log_text = read_text(args.apply_log)
    apply_summary = parse_summary(apply_log_text)
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, got {apply_summary}")
    if "REPORT: Save succeeded" not in apply_log_text:
        failures.append("apply log missing REPORT: Save succeeded")

    report = {
        "schema": "ghidra-collision-hl-wave398.v1",
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "targets": len(TARGETS),
        "failures": failures,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
    }
    return report, 0 if not failures else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=BASE / "metadata_after.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--instructions", type=Path, default=BASE / "instructions_after.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after")
    parser.add_argument("--public-note", type=Path, default=ROOT / "release" / "readiness" / "ghidra_collision_hl_wave398_2026-05-14.md")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "collision-hl-wave398.json")
    parser.add_argument("--check", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report, status = validate(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        print(f"status={report['status']} targets={report['targets']} failures={len(report['failures'])} out={args.out}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
