#!/usr/bin/env python3
"""Validate the saved Ghidra DXCompass signature/comment correction wave."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "dxcompass-wave323" / "current"

TARGETS = {
    "0x00426fd0": {
        "name": "OID__AllocObject_DefaultTag_00662b2c",
        "signature": "void * __cdecl OID__AllocObject_DefaultTag_00662b2c(int sizeBytes)",
        "comment": ["allocator wrapper", "OID__AllocObject", "not DXCompass-specific", "remain unproven"],
    },
    "0x004270e0": {
        "name": "CDXCompass__InitMarkerArrays",
        "signature": "void __fastcall CDXCompass__InitMarkerArrays(void * this)",
        "comment": ["two 30-slot", "this+0x3c24", "CDXCompass__Init", "remain unproven"],
    },
    "0x00427110": {
        "name": "CDXCompass__LoadTextures",
        "signature": "void __fastcall CDXCompass__LoadTextures(void * this)",
        "comment": ["ThreatFlash", "DamageFlash", "BarLine", "CompassObjectiveMarker", "remain unproven"],
    },
    "0x00427190": {
        "name": "CDXCompass__DestroyTextures",
        "signature": "void __fastcall CDXCompass__DestroyTextures(void * this)",
        "comment": ["texture references", "texture+8", "CHud__ShutDown", "remain unproven"],
    },
    "0x00427200": {
        "name": "CDXCompass__Reset",
        "signature": "void __fastcall CDXCompass__Reset(void * this)",
        "comment": ["this+0x3c10", "CHud reset", "runtime HUD behavior", "remain unproven"],
    },
    "0x00427210": {
        "name": "CDXCompass__Render",
        "signature": "void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)",
        "comment": ["CDXBattleLine__RenderWorldSpaceOverlay", "battle-engine/render context", "tracked X/Y getters", "remain unproven"],
    },
    "0x0053be40": {
        "name": "CDXCompass__Init",
        "signature": "void __fastcall CDXCompass__Init(void * this)",
        "comment": ["CByteSprite", "GPU caps", "CVBuffers", "ring geometry", "remain unproven"],
    },
    "0x0053c1d0": {
        "name": "CDXCompass__BuildRingGeometry",
        "signature": "void __cdecl CDXCompass__BuildRingGeometry(void * vertices, int textureWidth, int textureHeight, int segmentCount, int thicknessPercent, float uvScale)",
        "comment": ["vertex strip", "texture width/height", "segment count", "outer and inner rings", "remain unproven"],
    },
}

DEFAULT_METADATA_FINAL = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "dxcompass-signature-correction.json"

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
    queue_json_path: Path = DEFAULT_QUEUE_JSON,
) -> dict[str, object]:
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    queue_json_path = resolve(queue_json_path)

    failures: list[str] = []
    for path, label in (
        (metadata_final_path, "metadata_final"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (queue_json_path, "queue_json"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    final_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    queue = read_json(queue_json_path)

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
        failures.append(f"totalFunctions below expected floor: {total_functions}")

    commentless = queue_signal(queue, "commentlessFunctionCount")
    undefined = queue_signal(queue, "undefinedSignatureCount")
    param_signatures = queue_signal(queue, "paramSignatureCount")
    if commentless is not None and commentless > 5133:
        failures.append(f"commentlessFunctionCount did not drop to expected ceiling: {commentless}")
    if undefined is not None and undefined > 1997:
        failures.append(f"undefinedSignatureCount did not drop to expected ceiling: {undefined}")
    if param_signatures is not None and param_signatures > 2306:
        failures.append(f"paramSignatureCount did not drop to expected ceiling: {param_signatures}")

    return {
        "schema": "ghidra-dxcompass-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "inputs": {
            "metadataFinal": relative(metadata_final_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "queue": relative(queue_json_path),
        },
        "targetCount": len(TARGETS),
        "staleParamSignatures": stale_params,
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "queueTotalFunctions": total_functions,
        "queueCommentlessFunctions": commentless,
        "queueUndefinedSignatures": undefined,
        "queueParamSignatures": param_signatures,
        "targets": target_summaries,
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project now has hardened signatures and comments for eight DXCompass-adjacent render/resource helpers.",
            "CDXCompass render is modeled as a thiscall with the compass object in ECX and an explicit battle-engine/render-context stack argument.",
            "CDXCompass ring geometry is modeled as a plain helper taking locked vertices and ring geometry parameters, not as a class method.",
        ],
        "notProven": [
            "This does not prove runtime HUD rendering behavior or visual parity.",
            "This does not prove exact source-body identity because DXCompass.cpp is not present in the available Stuart source snapshot.",
            "This does not prove concrete layouts, tags, locals, or rebuild parity.",
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
        queue_json_path=args.queue_json,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra DXCompass signature correction probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']}")
        print(f"Queue total functions: {report['queueTotalFunctions']}")
        print(f"Queue commentless functions: {report['queueCommentlessFunctions']}")
        print(f"Queue undefined signatures: {report['queueUndefinedSignatures']}")
        print(f"Queue param signatures: {report['queueParamSignatures']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
