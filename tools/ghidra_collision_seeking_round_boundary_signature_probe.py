#!/usr/bin/env python3
"""Validate the saved Ghidra CollisionSeekingRound boundary/signature wave."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "collision-seeking-wave322" / "current"

TARGETS = {
    "0x00425a10": {
        "name": "CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags",
        "signature": "bool __thiscall CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags(void * this, void * candidateRound)",
        "comment": ["infantry-bloke", "CBattleEngine__IsWeaponModeCompatibleWithMountState", "runtime collision behavior", "remain unproven"],
    },
    "0x00425b50": {
        "name": "CCollisionSeekingRound__InitCollisionLineAndSound",
        "signature": "void __thiscall CCollisionSeekingRound__InitCollisionLineAndSound(void * this, void * roundConfig)",
        "comment": ["Recovered function-boundary", "CLine-style helper", "InitWithSound", "runtime projectile behavior", "remain unproven"],
        "created": True,
    },
    "0x00425c60": {
        "name": "CCollisionSeekingRound__FilterCollisionCandidateByTrajectory",
        "signature": "bool __thiscall CCollisionSeekingRound__FilterCollisionCandidateByTrajectory(void * this, void * candidateRound)",
        "comment": ["Recovered function-boundary", "CheckCollisionFlags", "same-owner", "trajectory", "remain unproven"],
        "created": True,
    },
    "0x00425e30": {
        "name": "CCollisionSeekingRound__UpdatePrimarySeekerLeadVector",
        "signature": "void * __fastcall CCollisionSeekingRound__UpdatePrimarySeekerLeadVector(void * this)",
        "comment": ["Recovered function-boundary", "primary seeker", "lead vector", "+0x38", "remain unproven"],
        "created": True,
    },
    "0x00426150": {
        "name": "CCollisionSeekingRound__Init",
        "signature": "void __thiscall CCollisionSeekingRound__Init(void * this, void * roundConfig)",
        "comment": ["primary CLine-style seeker", "collisionseekingthing.cpp", "0x39", "rebuild parity", "remain unproven"],
    },
    "0x00426300": {
        "name": "CMeshCollisionVolume__ScalarDeletingDestructor_00426300",
        "signature": "void * __thiscall CMeshCollisionVolume__ScalarDeletingDestructor_00426300(void * this, int deleteFlags)",
        "comment": ["scalar-deleting destructor", "CMeshCollisionVolume", "delete flag", "exact helper subtype", "remain unproven"],
    },
    "0x00426340": {
        "name": "CLine__ScalarDeletingDestructor_00426340",
        "signature": "void * __thiscall CLine__ScalarDeletingDestructor_00426340(void * this, int deleteFlags)",
        "comment": ["scalar-deleting destructor", "CLine-style collision helper", "BattleEngine helper lines", "remain unproven"],
    },
    "0x00426360": {
        "name": "CLine__SetBaseVtable_00426360",
        "signature": "void __fastcall CLine__SetBaseVtable_00426360(void * this)",
        "comment": ["vtable reset", "broader than CollisionSeekingRound", "previous CollisionSeekingRound-specific name", "remain unproven"],
    },
    "0x00426370": {
        "name": "CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset",
        "signature": "void __thiscall CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset(void * this, void * newSeeker)",
        "comment": ["Recovered function-boundary", "replaces the primary seeker", "owner-relative offset", "remain unproven"],
        "created": True,
    },
    "0x004263f0": {
        "name": "CCollisionSeekingRound__Destructor",
        "signature": "void __fastcall CCollisionSeekingRound__Destructor(void * this)",
        "comment": ["destructor body", "primary and secondary helper", "CMonitor__Shutdown", "remain unproven"],
    },
    "0x00426460": {
        "name": "CCollisionSeekingRound__ScalarDeletingDestructor",
        "signature": "void * __thiscall CCollisionSeekingRound__ScalarDeletingDestructor(void * this, int deleteFlags)",
        "comment": ["scalar-deleting destructor", "delete flag", "runtime destruction behavior", "remain unproven"],
    },
    "0x00426480": {
        "name": "CCollisionSeekingRound__SetCollisionMask",
        "signature": "void __thiscall CCollisionSeekingRound__SetCollisionMask(void * this, int collisionMask)",
        "comment": ["collision mask", "+0x10", "0x100", "runtime collision filtering", "remain unproven"],
    },
    "0x004264a0": {
        "name": "CCollisionSeekingRound__ResolveRoundCollisionResponse",
        "signature": "void __thiscall CCollisionSeekingRound__ResolveRoundCollisionResponse(void * this, void * otherRound)",
        "comment": ["Recovered function-boundary", "delayed-ready flag 0x400", "collision-priority", "response callbacks", "remain unproven"],
        "created": True,
    },
    "0x00426900": {
        "name": "CCollisionSeekingRound__CheckCollisionFlags",
        "signature": "bool __thiscall CCollisionSeekingRound__CheckCollisionFlags(void * this, void * candidateRound)",
        "comment": ["candidate owner's thing flags", "+0x34", "collision mask", "+0x10", "remain unproven"],
    },
    "0x00426920": {
        "name": "CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance",
        "signature": "int __thiscall CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance(void * this, void * packedCell)",
        "comment": ["Recovered function-boundary", "Chebyshev-style distance", "packed candidate coordinates", "remain unproven"],
        "created": True,
    },
    "0x004269b0": {
        "name": "CCollisionSeekingRound__InitWithSound",
        "signature": "void __thiscall CCollisionSeekingRound__InitWithSound(void * this, void * roundConfig)",
        "comment": ["InitWithSound", "3000ms", "EVENT_MANAGER", "neighbor sectors", "remain unproven"],
    },
    "0x00426a00": {
        "name": "CCollisionSeekingRound__ProcessMapWhoCollisionSweep",
        "signature": "void __thiscall CCollisionSeekingRound__ProcessMapWhoCollisionSweep(void * this, void * startOrContext, void * endOrContext)",
        "comment": ["Recovered function-boundary", "this+0x24", "CHLCollisionDetector__ProcessMapWhoCollisionSweep", "remain unproven"],
        "created": True,
    },
    "0x00426a20": {
        "name": "CCollisionSeekingRound__MarkDelayedCollisionReady",
        "signature": "void __thiscall CCollisionSeekingRound__MarkDelayedCollisionReady(void * this, void * event)",
        "comment": ["Recovered function-boundary", "3000ms", "flag 0x400", "InitWithSound", "remain unproven"],
        "created": True,
    },
    "0x00426a40": {
        "name": "CCollisionSeekingRound__CreateEffect",
        "signature": "void __thiscall CCollisionSeekingRound__CreateEffect(void * this, void * roundConfig)",
        "comment": ["CreateEffect", "CLine-style trace helper", "best target hit", "rebuild parity", "remain unproven"],
    },
}

DEFAULT_METADATA_FINAL = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_CREATE_APPLY = BASE / "function_create_apply.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "collision-seeking-round-boundary-signature-correction.json"

OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "fully re'ed", "100% re")


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


def read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "function_entry", "target_raw"):
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


def queue_signal(report: dict[str, object], name: str) -> int | None:
    signals = report.get("qualitySignals", {})
    if isinstance(signals, dict) and isinstance(signals.get(name), int):
        return int(signals[name])
    return None


def build_report(
    *,
    metadata_final_path: Path = DEFAULT_METADATA_FINAL,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    create_apply_path: Path = DEFAULT_CREATE_APPLY,
    queue_json_path: Path = DEFAULT_QUEUE_JSON,
) -> dict[str, object]:
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    create_apply_path = resolve(create_apply_path)
    queue_json_path = resolve(queue_json_path)

    failures: list[str] = []
    for path, label in (
        (metadata_final_path, "metadata_final"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (create_apply_path, "function_create_apply"),
        (queue_json_path, "queue_json"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    final_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    create_rows = read_tsv(create_apply_path)
    queue = read_json(queue_json_path)

    created_expected = {addr for addr, expected in TARGETS.items() if expected.get("created")}
    created_actual = {
        normalize_address(row.get("address", ""))
        for row in create_rows
        if row.get("status") in {"created", "renamed_existing", "already_exists"}
    }
    missing_created = sorted(created_expected - created_actual)
    if missing_created:
        failures.append(f"created target read-back missing: {', '.join(missing_created)}")
    if any(row.get("status") == "failed" for row in create_rows):
        failures.append("function creation TSV contains failed rows")

    target_summaries: list[dict[str, object]] = []
    stale_params = 0
    for address, expected in TARGETS.items():
        final = row_by_address(final_rows, address)
        index = row_by_address(index_rows, address)
        decompile_text = decompile_text_for(decompile_dir, address)
        xrefs = rows_for_address(xref_rows, address, "target_addr")
        instructions = rows_for_address(instruction_rows, address, "target_addr")

        name = str(expected["name"])
        signature = str(expected["signature"])
        if final is None:
            failures.append(f"{address} missing from final metadata")
        else:
            if final.get("name") != name:
                failures.append(f"{address} final name mismatch: {final.get('name', '')} != {name}")
            if final.get("signature") != signature:
                failures.append(f"{name} signature mismatch: {final.get('signature', '')} != {signature}")
            if "param_" in final.get("signature", ""):
                stale_params += 1
                failures.append(f"{name} final signature still has param_N placeholder: {final.get('signature', '')}")
            comment = final.get("comment", "")
            for token in expected["comment"]:
                if not token_present(comment, str(token)):
                    failures.append(f"{name} comment missing token: {token}")
            lowered_comment = comment.lower()
            for token in OVERCLAIM_TOKENS:
                if token in lowered_comment:
                    failures.append(f"{name} comment overclaim token: {token}")

        if index is None:
            failures.append(f"{address} missing from decompile index")
        elif index.get("signature") != signature:
            failures.append(f"{name} decompile index signature mismatch: {index.get('signature', '')}")
        if not token_present(decompile_text, signature):
            failures.append(f"{name} decompile text did not include final signature")
        if len(xrefs) == 0:
            failures.append(f"{name} has no xref rows")
        if len(instructions) == 0:
            failures.append(f"{name} has no instruction rows")

        target_summaries.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "xrefRows": len(xrefs),
                "instructionRows": len(instructions),
            }
        )

    if queue.get("status") != "PASS":
        failures.append(f"queue status is not PASS: {queue.get('status')}")
    total_functions = queue.get("totalFunctions")
    if not isinstance(total_functions, int) or total_functions < 5884:
        failures.append(f"totalFunctions below expected recovered-boundary floor: {total_functions}")

    return {
        "schema": "ghidra-collision-seeking-round-boundary-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "inputs": {
            "metadataFinal": relative(metadata_final_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "functionCreateApply": relative(create_apply_path),
            "queue": relative(queue_json_path),
        },
        "targetCount": len(TARGETS),
        "createdBoundaryTargets": len(created_expected),
        "createdBoundaryReadBackTargets": len(created_actual & created_expected),
        "staleParamSignatures": stale_params,
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "queueTotalFunctions": total_functions,
        "queueCommentlessFunctions": queue_signal(queue, "commentlessFunctionCount"),
        "queueUndefinedSignatures": queue_signal(queue, "undefinedSignatureCount"),
        "queueParamSignatures": queue_signal(queue, "paramSignatureCount"),
        "targets": target_summaries,
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project now has function objects for eight previously missing CollisionSeekingRound-adjacent boundaries.",
            "The saved Ghidra project has hardened names, signatures, and comments for nineteen CollisionSeekingRound, CLine-helper, CMeshCollisionVolume-helper, and infantry-bloke collision helpers.",
            "The previous CollisionSeekingRound-specific name for the tiny CLine-style vtable reset helper was narrowed to a CLine-style helper because xrefs are broader than CollisionSeekingRound.",
        ],
        "notProven": [
            "This does not prove runtime projectile, collision, sound, event, or effect behavior.",
            "This does not prove exact source method names for vtable slots where Stuart source body identity is still absent or ambiguous.",
            "This does not prove concrete layouts, tags, locals, type names, or rebuild parity.",
            "This does not mutate or run BEA.exe.",
        ],
        "privacy": "Report stores repo-relative paths, public addresses, names, signatures, aggregate counts, and public-safe summaries only; raw decompile/read-back files remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA_FINAL)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--function-create-apply", type=Path, default=DEFAULT_CREATE_APPLY)
    parser.add_argument("--queue-json", type=Path, default=DEFAULT_QUEUE_JSON)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(
        metadata_final_path=args.metadata_final,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        create_apply_path=args.function_create_apply,
        queue_json_path=args.queue_json,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra CollisionSeekingRound boundary/signature probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']}")
        print(f"Created boundary read-back: {report['createdBoundaryReadBackTargets']}/{report['createdBoundaryTargets']}")
        print(f"Queue total functions: {report['queueTotalFunctions']}")
        print(f"Queue undefined signatures: {report['queueUndefinedSignatures']}")
        print(f"Queue param signatures: {report['queueParamSignatures']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
