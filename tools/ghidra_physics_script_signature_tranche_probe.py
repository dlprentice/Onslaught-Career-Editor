#!/usr/bin/env python3
"""Validate the saved Ghidra PhysicsScript signature/comment tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "physics-script-wave330" / "current"

COMMON_TAGS = ["static-reaudit", "physics-script-wave330", "physics-script", "signature-hardened"]
RETAIL_TAGS = COMMON_TAGS + ["retail-binary-evidence"]

TARGETS = {
    "0x0042e880": {
        "name": "CPhysicsScript__Create",
        "signature": "void __cdecl CPhysicsScript__Create(void)",
        "comment": ["g_pPhysicsScript", "0x10", "object type 0x18", "CSPtrSet/list", "remain unproven"],
        "tags": RETAIL_TAGS + ["manager-lifecycle"],
    },
    "0x0042e8f0": {
        "name": "CPhysicsScript__Destroy",
        "signature": "void __cdecl CPhysicsScript__Destroy(void)",
        "comment": ["vtable slot 0", "delete flag 1", "OID__FreeObject", "remain unproven"],
        "tags": RETAIL_TAGS + ["manager-lifecycle"],
    },
    "0x0042e950": {
        "name": "CPhysicsScript__Load",
        "signature": "bool __cdecl CPhysicsScript__Load(void * memBuffer)",
        "comment": ["0x12", "until -1", "CreateStatement", "slot +0xc", "skips bytes", "remain unproven"],
        "tags": RETAIL_TAGS + ["physics-script-load"],
    },
    "0x0042ea60": {
        "name": "CPhysicsScript__Update",
        "signature": "void __cdecl CPhysicsScript__Update(void)",
        "comment": ["g_pPhysicsScript", "slot +0x4", "remain unproven"],
        "tags": RETAIL_TAGS + ["physics-script-update"],
    },
    "0x0042eb90": {
        "name": "CPhysicsScript__CreateStatement",
        "signature": "void * __cdecl CPhysicsScript__CreateStatement(int statementType)",
        "comment": ["1..9", "0x110-byte", "object type ids 0x11..0x19", "returns null", "remain unproven"],
        "tags": RETAIL_TAGS + ["statement-factory"],
    },
}

EXPECTED_XREFS = (
    ("0x0042e880", "CPhysicsScript__Load"),
    ("0x0042e8f0", "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData"),
    ("0x0042e950", "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData"),
    ("0x0042ea60", "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData"),
    ("0x0042eb90", "CPhysicsScript__Load"),
)

DEFAULT_METADATA_FINAL = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_TAGS = BASE / "tags_final.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "physics-script-signature-tranche.json"

OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "fully re'ed", "100% re", "rebuild parity proven")


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


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


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
    tags_path: Path = DEFAULT_TAGS,
    queue_json_path: Path = DEFAULT_QUEUE_JSON,
) -> dict[str, object]:
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    tags_path = resolve(tags_path)
    queue_json_path = resolve(queue_json_path)

    failures: list[str] = []
    for path, label in (
        (metadata_final_path, "metadata_final"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (tags_path, "tags"),
        (queue_json_path, "queue_json"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    metadata_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    tag_rows = read_tsv(tags_path)
    queue_report = read_json(queue_json_path)

    metadata_ok = 0
    decompile_ok = 0
    tag_ok = 0
    for address, expected in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        if not row:
            failures.append(f"metadata missing {address}")
        else:
            if row.get("status") != "OK":
                failures.append(f"metadata status not OK for {address}: {row.get('status')}")
            if row.get("name") != expected["name"]:
                failures.append(f"name mismatch for {address}: {row.get('name')} != {expected['name']}")
            if row.get("signature") != expected["signature"]:
                failures.append(f"signature mismatch for {address}: {row.get('signature')} != {expected['signature']}")
            comment = row.get("comment", "")
            for token in expected["comment"]:
                if not token_present(comment, token):
                    failures.append(f"comment token missing for {address}: {token}")
            if row.get("status") == "OK" and row.get("name") == expected["name"]:
                metadata_ok += 1

        index_row = row_by_address(index_rows, address)
        if not index_row:
            failures.append(f"decompile index missing {address}")
        else:
            if index_row.get("status") != "OK":
                failures.append(f"decompile index status not OK for {address}: {index_row.get('status')}")
            if index_row.get("name") != expected["name"]:
                failures.append(f"decompile name mismatch for {address}: {index_row.get('name')} != {expected['name']}")
            if index_row.get("signature") != expected["signature"]:
                failures.append(f"decompile signature mismatch for {address}: {index_row.get('signature')} != {expected['signature']}")
            text = decompile_text_for(decompile_dir, address)
            for token in expected["comment"]:
                if not token_present(text, token):
                    failures.append(f"decompile comment token missing for {address}: {token}")
            for bad in OVERCLAIM_TOKENS:
                if token_present(text, bad):
                    failures.append(f"overclaim token present for {address}: {bad}")
            if index_row.get("status") == "OK" and text:
                decompile_ok += 1

        tag_row = row_by_address(tag_rows, address)
        if not tag_row:
            failures.append(f"tags missing {address}")
        else:
            tags = parse_tags(tag_row.get("tags", ""))
            for tag in expected["tags"]:
                if tag not in tags:
                    failures.append(f"tag missing for {address}: {tag}")
            if all(tag in tags for tag in expected["tags"]):
                tag_ok += 1

    for target, caller in EXPECTED_XREFS:
        rows = rows_for_address(xref_rows, target, "target_addr")
        if not any(row.get("from_function") == caller for row in rows):
            failures.append(f"expected xref missing: {target} from {caller}")

    if len(instruction_rows) < len(TARGETS):
        failures.append(f"instruction export too small: {len(instruction_rows)}")

    queue_status = queue_report.get("status")
    if queue_status != "PASS":
        failures.append(f"queue status not PASS: {queue_status}")
    total_functions = int(queue_report.get("totalFunctions", 0) or 0)
    if total_functions != 5884:
        failures.append(f"unexpected totalFunctions: {total_functions}")
    commentless = queue_signal(queue_report, "commentlessFunctionCount")
    undefined_signatures = queue_signal(queue_report, "undefinedSignatureCount")
    param_signatures = queue_signal(queue_report, "paramSignatureCount")
    if commentless is None or commentless > 5061:
        failures.append(f"queue commentlessFunctionCount did not improve to <= 5061: {commentless}")
    if undefined_signatures is None or undefined_signatures > 1983:
        failures.append(f"queue undefinedSignatureCount did not improve to <= 1983: {undefined_signatures}")
    if param_signatures is None or param_signatures > 2269:
        failures.append(f"queue paramSignatureCount regressed: {param_signatures}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-physics-script-signature-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "targetCount": len(TARGETS),
        "metadataOk": metadata_ok,
        "decompileOk": decompile_ok,
        "tagOk": tag_ok,
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "queueCommentlessFunctions": commentless,
        "queueUndefinedSignatures": undefined_signatures,
        "queueParamSignatures": param_signatures,
        "inputs": {
            "metadataFinal": relative(metadata_final_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "tags": relative(tags_path),
            "queueJson": relative(queue_json_path),
        },
        "whatIsProven": [
            "The selected CPhysicsScript manager helpers have saved Ghidra signatures, comments, and tags matching the current retail decompile/read-back evidence.",
            "The manager create/destroy/load/update/factory cluster now has command-checkable public-safe read-back evidence.",
            "The CreateStatement factory has bounded evidence for statement type ids 1..9, 0x110-byte allocations, and object type ids 0x11..0x19.",
        ],
        "notProven": [
            "This does not prove runtime physics-script behavior.",
            "This does not prove exact source body identity, complete statement subtype layouts, or every PhysicsScript helper.",
            "This does not launch or patch BEA.exe, mutate assets or saves, or prove rebuild parity.",
        ],
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA_FINAL)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
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
        tags_path=args.tags,
        queue_json_path=args.queue_json,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra PhysicsScript signature tranche probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']}")
        print(f"Metadata OK: {report['metadataOk']}")
        print(f"Decompile OK: {report['decompileOk']}")
        print(f"Tags OK: {report['tagOk']}")
        print(f"Xref rows: {report['xrefRows']}")
        print(f"Instruction rows: {report['instructionRows']}")
        print(f"Queue commentless functions: {report['queueCommentlessFunctions']}")
        print(f"Queue undefined signatures: {report['queueUndefinedSignatures']}")
        print(f"Queue param signatures: {report['queueParamSignatures']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
