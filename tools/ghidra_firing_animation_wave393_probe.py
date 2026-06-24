#!/usr/bin/env python3
"""Validate the Wave393 firing-animation Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "firing-animation-wave393" / "current"

COMMON_TAGS = {"static-reaudit", "firing-animation-wave393", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    instruction_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "instructionTokens": instruction_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0047d3b0": target(
        "CMonitor__TryQueuePrefireAnimation",
        "int __fastcall CMonitor__TryQueuePrefireAnimation(void * this)",
        [
            "CGroundVehicle vtable 0x005e297c slot 86",
            "CUnit__UpdateDeployStateAndChargeEffects",
            "prefire",
            "vfunc +0xf0",
            "runtime behavior",
            "rebuild parity remain unproven",
        ],
        [
            "CUnit__UpdateDeployStateAndChargeEffects",
            "s_prefire_0062cb60",
            "FindAnimationIndex",
            "+ 0xf0",
        ],
        ["0x62cb60", "0xf0", "004aa630"],
        ["cgroundvehicle", "animation", "prefire", "signature-hardened", "comment-hardened"],
    ),
    "0x0047d420": target(
        "CUnitAI__QueueFiringOrPostfireAnimation",
        "void __fastcall CUnitAI__QueueFiringOrPostfireAnimation(void * this)",
        [
            "CGroundVehicle vtable 0x005e297c slot 87",
            "CUnitAI__FinalizeSpawnAndAdvanceState",
            "firing",
            "postfire",
            "vfunc +0xf0",
            "runtime behavior",
            "rebuild parity remain unproven",
        ],
        [
            "CUnitAI__FinalizeSpawnAndAdvanceState",
            "s_firing_0062cb68",
            "s_postfire_0062cb70",
            "FindAnimationIndex",
            "+ 0xf0",
        ],
        ["0x62cb68", "0x62cb70", "0xf0", "004aa630"],
        ["cgroundvehicle", "animation", "firing", "postfire", "signature-hardened", "comment-hardened"],
    ),
    "0x0047d670": target(
        "CUnitAI__FreeOwnedObjects_10_18",
        "void __fastcall CUnitAI__FreeOwnedObjects_10_18(void * this)",
        [
            "unwind-target cleanup helper",
            "+0x18",
            "+0x10",
            "no slot-clear stores",
            "runtime behavior",
            "rebuild parity remain unproven",
        ],
        [
            "OID__FreeObject",
            "+ 0x18",
            "+ 0x10",
        ],
        ["[ESI + 0x18]", "[ESI + 0x10]", "00549220"],
        ["cleanup", "owned-object-cleanup", "signature-hardened", "comment-hardened"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 3, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 3, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime proof",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
    "clears +0x10",
    "clears +0x18",
    "clears both slots",
)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


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
        for key in (
            "address",
            "target_addr",
            "vtable",
            "slot_addr",
            "pointer_addr",
            "function_entry",
            "entry_addr",
            "from_function_addr",
        ):
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


def vtable_slot_hit(rows: list[dict[str, str]], vtable: str, slot: str, function_name: str) -> bool:
    for row in rows:
        if normalize_address(row.get("vtable", "")) != normalize_address(vtable):
            continue
        if row.get("slot_index") != slot:
            continue
        if row.get("function_name") == function_name:
            return True
    return False


def xref_hit(rows: list[dict[str, str]], target: str, from_function: str | None = None, ref_type: str | None = None) -> bool:
    wanted = normalize_address(target)
    for row in rows:
        if normalize_address(row.get("target_addr", "")) != wanted:
            continue
        if from_function is not None and row.get("from_function") != from_function:
            continue
        if ref_type is not None and row.get("ref_type") != ref_type:
            continue
        return True
    return False


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    metadata = read_tsv(resolve(args.metadata))
    tags = read_tsv(resolve(args.tags))
    xrefs = read_tsv(resolve(args.xrefs))
    vtable_slots = read_tsv(resolve(args.vtable_slots))
    instructions_text = read_text(resolve(args.instructions))
    decompile_dir = resolve(args.decompile_dir)
    public_note = read_text(resolve(args.public_note))
    dry_log = read_text(resolve(args.dry_log))
    apply_log = read_text(resolve(args.apply_log))

    failures: list[str] = []
    target_reports: dict[str, dict[str, object]] = {}

    if not metadata:
        failures.append(f"missing metadata TSV: {relative(resolve(args.metadata))}")
    if not tags:
        failures.append(f"missing tags TSV: {relative(resolve(args.tags))}")
    if not xrefs:
        failures.append(f"missing xrefs TSV: {relative(resolve(args.xrefs))}")
    if not vtable_slots:
        failures.append(f"missing vtable slots TSV: {relative(resolve(args.vtable_slots))}")
    if not instructions_text:
        failures.append(f"missing instructions TSV: {relative(resolve(args.instructions))}")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        tag_row = row_by_address(tags, address)
        decompile = decompile_text_for(decompile_dir, address)
        target_failures: list[str] = []

        if row is None:
            target_failures.append("metadata row missing")
        else:
            if row.get("name") != spec["name"]:
                target_failures.append(f"name {row.get('name')!r} != {spec['name']!r}")
            if row.get("signature") != spec["signature"]:
                target_failures.append(f"signature {row.get('signature')!r} != {spec['signature']!r}")
            comment = row.get("comment", "")
            for token in spec["commentTokens"]:  # type: ignore[index]
                if not token_present(comment, str(token)):
                    target_failures.append(f"comment missing token {token!r}")
            for token in OVERCLAIM_TOKENS:
                if token_present(comment, token):
                    target_failures.append(f"comment overclaim token present {token!r}")

        if tag_row is None:
            target_failures.append("tag row missing")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            expected_tags = set(spec["tags"])  # type: ignore[arg-type]
            missing_tags = sorted(expected_tags - actual_tags)
            if missing_tags:
                target_failures.append(f"tags missing {missing_tags}")

        if not decompile:
            target_failures.append("decompile file missing")
        else:
            for token in spec["decompileTokens"]:  # type: ignore[index]
                if not token_present(decompile, str(token)):
                    target_failures.append(f"decompile missing token {token!r}")

        for token in spec["instructionTokens"]:  # type: ignore[index]
            if not token_present(instructions_text, str(token)):
                target_failures.append(f"instructions missing token {token!r}")

        target_reports[address] = {
            "name": spec["name"],
            "failures": target_failures,
        }
        failures.extend(f"{address}: {failure}" for failure in target_failures)

    if not vtable_slot_hit(vtable_slots, "0x005e297c", "86", "CMonitor__TryQueuePrefireAnimation"):
        failures.append("missing CGroundVehicle vtable slot 86 -> CMonitor__TryQueuePrefireAnimation")
    if not vtable_slot_hit(vtable_slots, "0x005e297c", "87", "CUnitAI__QueueFiringOrPostfireAnimation"):
        failures.append("missing CGroundVehicle vtable slot 87 -> CUnitAI__QueueFiringOrPostfireAnimation")

    if not xref_hit(xrefs, "0x0047d3b0", ref_type="DATA"):
        failures.append("missing DATA xref to 0x0047d3b0")
    if not xref_hit(xrefs, "0x0047d420", ref_type="DATA"):
        failures.append("missing DATA xref to 0x0047d420")
    if not xref_hit(xrefs, "0x0047d670", from_function="Unwind@005d2c53", ref_type="UNCONDITIONAL_CALL"):
        failures.append("missing unwind xref to cleanup helper")

    if public_note:
        required_note_tokens = [
            "0x0047d3b0",
            "0x0047d420",
            "0x0047d670",
            "CGroundVehicle vtable slots 86 and 87",
            "does not claim slot clearing",
            "does not prove runtime animation behavior",
            "does not prove rebuild parity",
        ]
        for token in required_note_tokens:
            if not token_present(public_note, token):
                failures.append(f"public note missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(public_note, token):
                failures.append(f"public note overclaim token present {token!r}")

    dry_summary = parse_summary(dry_log)
    apply_summary = parse_summary(apply_log)
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: {dry_summary} != {EXPECTED_DRY}")
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: {apply_summary} != {EXPECTED_APPLY}")

    report: dict[str, object] = {
        "schema": "ghidra.firingAnimationWave393.v1",
        "generatedUtc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "base": relative(BASE),
        "targets": target_reports,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "failures": failures,
    }
    return report, 0 if not failures else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=BASE / "metadata_after.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--vtable-slots", type=Path, default=BASE / "vtable_slots_after.tsv")
    parser.add_argument("--instructions", type=Path, default=BASE / "instructions_after.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply.log")
    parser.add_argument(
        "--public-note",
        type=Path,
        default=ROOT / "release" / "readiness" / "ghidra_firing_animation_wave393_2026-05-14.md",
    )
    parser.add_argument("--out", type=Path, default=BASE / "firing-animation-wave393.json")
    parser.add_argument("--check", action="store_true", help="Exit non-zero on validation failure.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report, status = validate(args)
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "status={status} targets={targets} failures={failures} out={out}".format(
            status=report["status"],
            targets=len(TARGETS),
            failures=len(report["failures"]),  # type: ignore[arg-type]
            out=relative(out_path),
        )
    )
    if report["failures"]:
        for failure in report["failures"]:  # type: ignore[union-attr]
            print(f"FAIL: {failure}")
    return status if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
