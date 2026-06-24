#!/usr/bin/env python3
"""Validate the saved AirGuide/AirUnit Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "airguide-airunit-signature-tranche" / "current"

TARGETS = {
    "0x00402150": {
        "name": "CAirGuide__ctor",
        "signatureTokens": ["void *", "__thiscall", "CAirGuide__ctor", "void * this", "void * guideTarget"],
        "commentTokens": ["AirGuide constructor", "CGuide constructor", "2000/0x7d1", "Not concrete class layout"],
        "decompileTokens": ["CGuide__ctor_like_0047e290", "CEventManager__AddEvent_AtTime", "0xbf800000"],
        "instructionTokens": ["CALL", "0x0047e290", "RET", "0x4"],
    },
    "0x00402200": {
        "name": "CAirGuide__scalar_deleting_dtor",
        "signatureTokens": ["void *", "__thiscall", "CAirGuide__scalar_deleting_dtor", "void * this", "byte flags"],
        "commentTokens": ["scalar-deleting destructor", "CAirGuide__ShutdownAndUnlink", "flags&1"],
        "decompileTokens": ["CAirGuide__ShutdownAndUnlink", "OID__FreeObject", "return this"],
        "instructionTokens": ["TEST", "0x1", "RET", "0x4"],
    },
    "0x004026e0": {
        "name": "CAirGuide__HandleEvent",
        "signatureTokens": ["void", "__thiscall", "CAirGuide__HandleEvent", "void * this", "void * event"],
        "commentTokens": ["AirGuide event handler", "Event 2000", "event 0x7d1", "Not runtime AI behavior proof"],
        "decompileTokens": [
            "CAirGuide__UpdateGroundClearanceCache",
            "CAirGuide__AcquireNearestTargetReader",
            "Random__NextLCGAbs",
            "CEventManager__AddEvent_AtTime",
        ],
        "instructionTokens": ["RET", "0x4"],
    },
    "0x004027c0": {
        "name": "CAirGuide__AcquireNearestTargetReader",
        "signatureTokens": ["void", "__fastcall", "CAirGuide__AcquireNearestTargetReader", "void * this"],
        "commentTokens": ["nearest-target reader", "mapwho", "+0x2c", "Not concrete layout"],
        "decompileTokens": [
            "CGenericActiveReader__SetReader",
            "CMapWho__GetFirstEntryWithinRadius",
            "CMapWho__GetNextEntryWithinRadius",
        ],
        "instructionTokens": ["RET"],
    },
    "0x004028e0": {
        "name": "CAirGuide__UpdateGroundClearanceCache",
        "signatureTokens": ["void", "__fastcall", "CAirGuide__UpdateGroundClearanceCache", "void * this"],
        "commentTokens": ["ground-clearance cache", "+0x24/+0x28", "+/-0x14", "+0x20"],
        "decompileTokens": ["ROUND", "CWorld__GetHeightSamplePacked16", "0x14", "+ 0x20"],
        "instructionTokens": ["RET"],
    },
    "0x00402ad0": {
        "name": "CAirUnit__Init",
        "signatureTokens": ["void", "__thiscall", "CAirUnit__Init", "void * this", "void * init"],
        "commentTokens": ["AirUnit init", "CUnit__Init", "+0x3bc", "Trail/Engine"],
        "decompileTokens": [
            "CUnit__Init",
            "s_Trail_00622d14",
            "s_Engine_00622cec",
            "CSPtrSet__AddToTail",
            "CSPtrSet__AddToHead",
        ],
        "instructionTokens": ["RET", "0x4"],
    },
    "0x00402d30": {
        "name": "CAirUnit__dtor_base",
        "signatureTokens": ["void", "__fastcall", "CAirUnit__dtor_base", "void * this"],
        "commentTokens": ["AirUnit destructor-base", "air-unit set", "Trail/Engine", "Not destructor completeness"],
        "decompileTokens": [
            "CSPtrSet__Remove",
            "CUnit__FinalizeLinkedUnitStateAndClear",
            "CParticleManager__RemoveFromGlobalList",
            "OID__FreeObject",
            "VFuncSlot_02_004f95d0",
        ],
        "instructionTokens": ["CALL", "0x004f95d0", "RET"],
    },
}

DEFAULT_RENAME_DRY = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY = BASE / "rename_apply.log"
DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_COMMENTS_DRY = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_OUT = BASE / "airguide-airunit-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime ai behavior proven",
    "exact source identity proven",
    "class layout proven",
    "rebuild parity proven",
]


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_rename_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"applied": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "applied": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def parse_update_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def find_row(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def instruction_text_for(rows: list[dict[str, str]], address: str) -> str:
    wanted = normalize_address(address)
    chunks: list[str] = []
    for row in rows:
        if normalize_address(row.get("target_addr", "")) == wanted:
            chunks.append(
                " ".join(
                    [
                        row.get("instruction_addr", ""),
                        row.get("function_name", ""),
                        row.get("mnemonic", ""),
                        row.get("operands", ""),
                    ]
                )
            )
    return "\n".join(chunks)


def build_report(
    *,
    rename_dry_log_path: Path = DEFAULT_RENAME_DRY,
    rename_apply_log_path: Path = DEFAULT_RENAME_APPLY,
    signature_dry_log_path: Path = DEFAULT_SIGNATURE_DRY,
    signature_apply_log_path: Path = DEFAULT_SIGNATURE_APPLY,
    comments_dry_log_path: Path = DEFAULT_COMMENTS_DRY,
    comments_apply_log_path: Path = DEFAULT_COMMENTS_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    rename_dry_log_path = resolve(rename_dry_log_path)
    rename_apply_log_path = resolve(rename_apply_log_path)
    signature_dry_log_path = resolve(signature_dry_log_path)
    signature_apply_log_path = resolve(signature_apply_log_path)
    comments_dry_log_path = resolve(comments_dry_log_path)
    comments_apply_log_path = resolve(comments_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("rename dry log", rename_dry_log_path),
        ("rename apply log", rename_apply_log_path),
        ("signature dry log", signature_dry_log_path),
        ("signature apply log", signature_apply_log_path),
        ("comment dry log", comments_dry_log_path),
        ("comment apply log", comments_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    rename_dry = parse_rename_summary(read_text(rename_dry_log_path))
    rename_apply = parse_rename_summary(read_text(rename_apply_log_path))
    signature_dry = parse_update_summary(read_text(signature_dry_log_path))
    signature_apply = parse_update_summary(read_text(signature_apply_log_path))
    comments_dry = parse_rename_summary(read_text(comments_dry_log_path))
    comments_apply = parse_rename_summary(read_text(comments_apply_log_path))

    expected_renames = 6
    expected_signatures = len(TARGETS)
    if rename_dry != {"applied": 0, "skipped": expected_renames, "missing": 0, "bad": 0}:
        failures.append(f"unexpected rename dry summary: {rename_dry}")
    if rename_apply != {"applied": expected_renames, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected rename apply summary: {rename_apply}")
    if signature_dry != {"updated": 0, "skipped": expected_signatures, "missing": 0, "bad": 0}:
        failures.append(f"unexpected signature dry summary: {signature_dry}")
    if signature_apply != {"updated": expected_signatures, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected signature apply summary: {signature_apply}")
    if comments_dry != {"applied": 0, "skipped": expected_signatures, "missing": 0, "bad": 0}:
        failures.append(f"unexpected comment dry summary: {comments_dry}")
    if comments_apply != {"applied": expected_signatures, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected comment apply summary: {comments_apply}")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    target_reports: dict[str, dict[str, object]] = {}
    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"missing metadata row for {address}")
            target_reports[address] = {"status": "FAIL", "name": None}
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"metadata name mismatch for {address}: {row.get('name')} != {expected['name']}")

        signature = row.get("signature", "")
        missing_sig = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_sig:
            failures.append(f"signature tokens missing for {address}: {missing_sig}")

        comment = row.get("comment", "")
        missing_comment = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment:
            failures.append(f"comment tokens missing for {address}: {missing_comment}")
        lower_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lower_comment:
                failures.append(f"runtime/source overclaim for {address}: {token}")

        if index_row is None:
            failures.append(f"missing decompile index row for {address}")
        elif index_row.get("name") != expected["name"]:
            failures.append(f"decompile index name mismatch for {address}: {index_row.get('name')}")

        decompile_path = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_path) if decompile_path else ""
        if not decompile_path:
            failures.append(f"missing decompile file for {address}")
        missing_decompile = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile:
            failures.append(f"decompile tokens missing for {address}: {missing_decompile}")

        instruction_text = instruction_text_for(instruction_rows, address)
        missing_instructions = [token for token in expected["instructionTokens"] if not token_present(instruction_text, token)]
        if missing_instructions:
            failures.append(f"instruction tokens missing for {address}: {missing_instructions}")

        target_reports[address] = {
            "status": "OK",
            "name": row.get("name"),
            "signature": signature,
            "comment": comment,
            "decompile": relative(decompile_path) if decompile_path else None,
        }

    required_xrefs = {
        ("0x004027c0", "CAirGuide__HandleEvent"),
        ("0x004028e0", "CAirGuide__HandleEvent"),
        ("0x00402ad0", "CPlane__Init"),
    }
    for target_addr, from_function in required_xrefs:
        found = any(
            normalize_address(row.get("target_addr", "")) == normalize_address(target_addr)
            and row.get("from_function") == from_function
            for row in xref_rows
        )
        if not found:
            failures.append(f"missing expected xref {target_addr} from {from_function}")

    report = {
        "schema": "ghidra-airguide-airunit-signature-tranche/v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "summary": {
            "targets": len(TARGETS),
            "renamedTargets": rename_apply.get("applied", -1),
            "signatureHardenedTargets": signature_apply.get("updated", -1),
            "commentedTargets": comments_apply.get("applied", -1),
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
        },
        "inputs": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "signatureDryLog": relative(signature_dry_log_path),
            "signatureApplyLog": relative(signature_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "targets": target_reports,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero if validation fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Write JSON report here.")
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"AirGuide/AirUnit signature tranche: {report['status']}")
    print(f"Targets: {report['summary']['targets']}")
    print(f"Renamed targets: {report['summary']['renamedTargets']}")
    print(f"Signature-hardened targets: {report['summary']['signatureHardenedTargets']}")
    print(f"Commented targets: {report['summary']['commentedTargets']}")
    print(f"Xref rows: {report['summary']['xrefRows']}")
    print(f"Instruction rows: {report['summary']['instructionRows']}")
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")
    print(f"Wrote {relative(out_path)}")
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
