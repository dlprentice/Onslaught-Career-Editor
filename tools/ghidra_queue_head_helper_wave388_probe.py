#!/usr/bin/env python3
"""Validate the Wave388 queue-head helper Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue-head-helper-wave388" / "current"

COMMON_TAGS = {"static-reaudit", "queue-head-helper-wave388", "retail-binary-evidence"}


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
    "0x004098c0": target(
        "CLine__VFunc_01_004098c0",
        "int __thiscall CLine__VFunc_01_004098c0(void * this, void * arg0, void * arg1, void * dispatch_target, void * arg3)",
        [
            "Wave388 queue-head helper correction",
            "CLine vtable-slot wrapper",
            "forwards the ECX receiver plus four stack arguments to dispatch_target vfunc +0x10",
            "Exact argument types, dispatch target class, source identity, runtime behavior, and rebuild parity remain unproven",
        ],
        ["(*", "+ 0x10", "return"],
        ["cline", "vtable-wrapper", "signature-hardened", "comment-hardened"],
        ["DATA"],
    ),
    "0x00409e60": target(
        "CGeneralVolume__ToDoubleIdentity",
        "double __stdcall CGeneralVolume__ToDoubleIdentity(float input_value)",
        [
            "Wave388 queue-head helper comment",
            "x87 identity-style float-to-double helper",
            "constant - (constant - input_value)",
            "Exact source purpose, control behavior, runtime behavior, and rebuild parity remain unproven",
        ],
        ["_DAT_005d8568", "input_value"],
        ["general-volume", "x87", "input-axis", "comment-hardened"],
        ["CBattleEngineJetPart__Turn", "CGeneralVolume__ApplyYawInputByWeaponClass"],
    ),
    "0x0040d320": target(
        "Mat34__MultiplyBasisToOut",
        "void * __thiscall Mat34__MultiplyBasisToOut(void * this, void * out_basis, void * rhs_basis)",
        [
            "Wave388 owner/signature correction",
            "owner-neutral Mat34-style 3x3 basis multiply",
            "ECX is lhs_basis",
            "function returns out_basis in EAX",
            "old CMCBuggy-only owner label too narrow",
            "Concrete matrix layout, exact source identity, locals/types, runtime behavior, and rebuild parity remain unproven",
        ],
        ["out_basis", "rhs_basis"],
        ["mat34", "matrix-basis", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["CBattleEngine__BuildInterpolatedWorldTransform", "CMeshPart__ApplyRootTransformRecursive", "CMonitor__UpdateTrackedRenderPair"],
    ),
    "0x00414010": target(
        "CMonitor__ClearCurrentTrackedEntryFlag60",
        "void __thiscall CMonitor__ClearCurrentTrackedEntryFlag60(void * this)",
        [
            "Wave388 queue-head helper correction",
            "calls CBattleEngineWalkerPart__GetCurrentWeapon",
            "clears field +0x60",
            "Callers include CMonitor__Process, CBattleEngine__Morph, and CBattleEngine__AugmentWeapon",
            "Exact owner boundary, tracked-entry layout, runtime weapon behavior, and rebuild parity remain unproven",
        ],
        ["CBattleEngineWalkerPart__GetCurrentWeapon", "+ 0x60"],
        ["monitor", "weapon-entry", "signature-hardened", "comment-hardened"],
        ["CMonitor__Process", "CBattleEngine__Morph", "CBattleEngine__AugmentWeapon"],
    ),
    "0x0041ad10": target(
        "Vec3__AddInPlace",
        "void __thiscall Vec3__AddInPlace(void * this, void * add_vec3)",
        [
            "Wave388 owner/signature correction",
            "owner-neutral Vec3 in-place add helper",
            "the one stack argument is add_vec3",
            "old CMCTentacle-only owner label too narrow",
            "Concrete vector layout, exact source identity, locals/types, runtime behavior, and rebuild parity remain unproven",
        ],
        ["add_vec3", "+ 8"],
        ["vec3", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["CMeshPart__EvaluateAnimatedTransformCore", "CMCBuggy__UpdateWheel", "CPDSimpleSprite__ProcessAndRenderSpriteList"],
    ),
}

INSTRUCTION_EVIDENCE = [
    ("0x004098c0", "0x004098d9", "CALL", "dword ptr [EDX + 0x10]", "ff 52 10"),
    ("0x004098c0", "0x004098dd", "RET", "0x10", "c2 10 00"),
    ("0x00409e60", "0x00409e60", "FLD", "float ptr [0x005d8568]", "d9 05 68 85 5d 00"),
    ("0x00409e60", "0x00409e6a", "FSUBR", "float ptr [0x005d8568]", "d8 2d 68 85 5d 00"),
    ("0x00409e60", "0x00409e70", "RET", "0x4", "c2 04 00"),
    ("0x0040d320", "0x0040d323", "MOV", "EAX, dword ptr [ESP + 0x38]", "8b 44 24 38"),
    ("0x0040d320", "0x0040d409", "MOV", "EAX, dword ptr [ESP + 0x34]", "8b 44 24 34"),
    ("0x0040d320", "0x0040d46d", "RET", "0x8", "c2 08 00"),
    ("0x00414010", "0x00414010", "CALL", "0x00414030", "e8 1b 00 00 00"),
    ("0x00414010", "0x00414019", "MOV", "dword ptr [EAX + 0x60], 0x0", "c7 40 60 00 00 00 00"),
    ("0x0041ad10", "0x0041ad10", "MOV", "EAX, dword ptr [ESP + 0x4]", "8b 44 24 04"),
    ("0x0041ad10", "0x0041ad2c", "RET", "0x4", "c2 04 00"),
]

CALLSITE_EVIDENCE = [
    ("0x0040dbe6", "0x0040dbdd", "PUSH", "ECX"),
    ("0x0040dbe6", "0x0040dbde", "PUSH", "EDX"),
    ("0x0040dbe6", "0x0040dbdf", "LEA", "ECX, [ESP + 0x11c]"),
    ("0x0040dbe6", "0x0040dbe6", "CALL", "0x0040d320"),
    ("0x004b09b3", "0x004b09af", "PUSH", "EAX"),
    ("0x004b09b3", "0x004b09b0", "PUSH", "ECX"),
    ("0x004b09b3", "0x004b09b3", "CALL", "0x0040d320"),
    ("0x004b57dc", "0x004b57d4", "PUSH", "ECX"),
    ("0x004b57dc", "0x004b57dc", "CALL", "0x0041ad10"),
    ("0x004940d7", "0x004940d3", "PUSH", "ECX"),
    ("0x004940d7", "0x004940d7", "CALL", "0x0041ad10"),
]

EXPECTED_DRY = {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 5, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

DEFAULT_DRY = BASE / "queue_head_helper_wave388_dry.log"
DEFAULT_APPLY = BASE / "queue_head_helper_wave388_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_after"
DEFAULT_XREFS = BASE / "xrefs_after.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_after.tsv"
DEFAULT_CALLSITES = BASE / "callsite_instructions.tsv"
DEFAULT_TAGS = BASE / "tags_after.tsv"
DEFAULT_OUT = BASE / "queue-head-helper-wave388.json"

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime proof",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
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
        for key in ("address", "target_addr", "instruction_addr", "function_entry", "target_raw", "from_addr"):
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


def rows_for_address(rows: list[dict[str, str]], address: str, key: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


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


def instruction_hit(rows: list[dict[str, str]], target: str, instruction_addr: str, mnemonic: str, operands: str, bytes_: str) -> bool:
    target_norm = normalize_address(target)
    instruction_norm = normalize_address(instruction_addr)
    return any(
        (
            normalize_address(row.get("target_addr", "")) == target_norm
            or normalize_address(row.get("function_entry", "")) == target_norm
        )
        and normalize_address(row.get("instruction_addr", "")) == instruction_norm
        and row.get("mnemonic", "") == mnemonic
        and row.get("operands", "") == operands
        and row.get("bytes", "") == bytes_
        for row in rows
    )


def callsite_hit(rows: list[dict[str, str]], target: str, instruction_addr: str, mnemonic: str, operands: str) -> bool:
    target_norm = normalize_address(target)
    instruction_norm = normalize_address(instruction_addr)
    return any(
        normalize_address(row.get("target_addr", "")) == target_norm
        and normalize_address(row.get("instruction_addr", "")) == instruction_norm
        and row.get("mnemonic", "") == mnemonic
        and row.get("operands", "") == operands
        for row in rows
    )


def build_report(
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    callsites_path: Path = DEFAULT_CALLSITES,
    tags_path: Path = DEFAULT_TAGS,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    callsites_path = resolve(callsites_path)
    tags_path = resolve(tags_path)

    dry_log = read_text(dry_log_path)
    apply_log = read_text(apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    callsite_rows = read_tsv(callsites_path)
    tag_rows = read_tsv(tags_path)

    failures: list[str] = []
    dry_summary = parse_summary(dry_log)
    apply_summary = parse_summary(apply_log)
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: {dry_summary} != {EXPECTED_DRY}")
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: {apply_summary} != {EXPECTED_APPLY}")
    if "REPORT: Save succeeded" not in apply_log:
        failures.append("apply log missing REPORT: Save succeeded")

    commented = 0
    signature_hardened = 0
    xref_hits = 0
    for address, expected in TARGETS.items():
        metadata = row_by_address(metadata_rows, address)
        if metadata is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if metadata.get("name") != expected["name"]:
            failures.append(f"{address}: name mismatch {metadata.get('name')} != {expected['name']}")
        if metadata.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature mismatch {metadata.get('signature')} != {expected['signature']}")
        else:
            signature_hardened += 1
        comment = metadata.get("comment", "")
        for token in expected["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: comment overclaim token {token!r}")
        if comment:
            commented += 1

        decompile_text = decompile_text_for(decompile_dir, address)
        if not decompile_text:
            failures.append(f"{address}: missing decompile output")
        for token in expected["decompileTokens"]:
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")

        tags = parse_tags((row_by_address(tag_rows, address) or {}).get("tags", ""))
        for tag in expected["tags"]:
            if tag not in tags:
                failures.append(f"{address}: missing tag {tag!r}")

        target_xrefs = rows_for_address(xref_rows, address, "target_addr")
        for token in expected["xrefTokens"]:
            if any(token_present(" ".join(row.values()), str(token)) for row in target_xrefs):
                xref_hits += 1
            else:
                failures.append(f"{address}: missing xref token {token!r}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        if instruction_hit(instruction_rows, target_addr, instruction_addr, mnemonic, operands, bytes_):
            instruction_hits += 1
        else:
            failures.append(
                f"{target_addr}: missing instruction evidence at {instruction_addr} {mnemonic} {operands} {bytes_}"
            )

    callsite_hits = 0
    for target_addr, instruction_addr, mnemonic, operands in CALLSITE_EVIDENCE:
        if callsite_hit(callsite_rows, target_addr, instruction_addr, mnemonic, operands):
            callsite_hits += 1
        else:
            failures.append(f"{target_addr}: missing callsite evidence at {instruction_addr} {mnemonic} {operands}")

    report: dict[str, object] = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "targetCount": len(TARGETS),
        "commentedTargets": commented,
        "signatureHardenedTargets": signature_hardened,
        "xrefEvidenceHits": xref_hits,
        "instructionEvidenceHits": instruction_hits,
        "callsiteEvidenceHits": callsite_hits,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "callsites": relative(callsites_path),
            "tags": relative(tags_path),
        },
        "failures": failures,
        "notProven": [
            "Runtime behavior is not proven.",
            "Exact Stuart-source method identity is not proven.",
            "Concrete CLine, CGeneralVolume, CMonitor, Vec3, and Mat34 layouts remain unproven.",
            "Local variable names and structure types are not fully recovered.",
            "BEA.exe was not launched or patched.",
            "Rebuild parity is not proven.",
        ],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail with non-zero status if validation fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--callsites", type=Path, default=DEFAULT_CALLSITES)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    args = parser.parse_args()

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        callsites_path=args.callsites,
        tags_path=args.tags,
    )
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"status={report['status']} targets={report['targetCount']} "
        f"commented={report['commentedTargets']} signature_hardened={report['signatureHardenedTargets']} "
        f"xref_hits={report['xrefEvidenceHits']} instruction_hits={report['instructionEvidenceHits']} "
        f"callsite_hits={report['callsiteEvidenceHits']}"
    )
    print(f"wrote={relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
