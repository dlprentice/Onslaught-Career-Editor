#!/usr/bin/env python3
"""Validate Wave589 CDXBattleLine Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave589-battleline-core-0053a050"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_battleline_core_wave589_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BATTLELINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXBattleLine.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave589_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "battleline-core-wave589",
    "retail-binary-evidence",
    "battleline",
    "dx-render",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x0053a050": (
        "CDXBattleLine__Constructor",
        "void __thiscall CDXBattleLine__Constructor(void * this, int origin_x, int origin_y)",
        {"constructor", "ret-8", "hud-field-block", "vtable-005e4f64"},
        ("RET 0x8", "0x005e4f64", "128x1 or 128x128"),
    ),
    "0x0053a120": (
        "CDXBattleLine__scalar_deleting_dtor",
        "void * __thiscall CDXBattleLine__scalar_deleting_dtor(void * this, byte delete_flags)",
        {"scalar-deleting-dtor", "vtable-slot", "ret-4"},
        ("vtable slot 0x005e4f64[0]", "delete_flags bit 0", "returns this"),
    ),
    "0x0053a140": (
        "CDXBattleLine__DestructorThunk",
        "void __fastcall CDXBattleLine__DestructorThunk(void * this)",
        {"destructor-thunk", "jmp-thunk", "base-cdxsurf-dtor", "renamed"},
        ("one-instruction JMP thunk", "0x00556d90", "stale duplicate CDXSurf__dtor label"),
    ),
    "0x0053a150": (
        "CDXBattleLine__LoadTextures",
        "void __fastcall CDXBattleLine__LoadTextures(void * this)",
        {"load-textures", "hud-textures", "dynamic-vbuffer", "ecx-only"},
        ("hud\\\\marker.tga", "hud\\\\V2\\\\BattleEngineMarker.tga", "this+0x78"),
    ),
    "0x0053a280": (
        "CDXBattleLine__Setup",
        "int __fastcall CDXBattleLine__Setup(void * this)",
        {"setup", "post-load", "build-mesh", "ecx-only"},
        ("CHud__PostLoadProcess", "this+0x24", "returns 1"),
    ),
    "0x0053a390": (
        "CDXBattleLine__UpdateHeightmap",
        "void __fastcall CDXBattleLine__UpdateHeightmap(void * this)",
        {"heightmap", "terrain-sampling", "ecx-only"},
        ("BuildMesh", "raw 0x0053a010 trampoline", "short intensity values"),
    ),
    "0x0053a5e0": (
        "CDXBattleLine__BuildMesh",
        "void __fastcall CDXBattleLine__BuildMesh(void * this)",
        {"build-mesh", "triangulate-work-object", "vertex-index-buffer", "ecx-only"},
        ("0x18-byte Triangulate work object", "this+0x1c/+0x20", "vertex/index buffers"),
    ),
    "0x0053a930": (
        "CDXBattleLine__InitMipLevels",
        "void __fastcall CDXBattleLine__InitMipLevels(void * this)",
        {"mip-levels", "texture-gradient", "ecx-only"},
        ("constructor", "raw 0x0053a010 trampoline", "short gradient bands"),
    ),
    "0x0053aa40": (
        "CDXBattleLine__UpdateVertexBuffer",
        "void __thiscall CDXBattleLine__UpdateVertexBuffer(void * this, float hud_y, int use_unit_marker_offsets)",
        {"update-vertex-buffer", "ret-8", "marker-vertices"},
        ("RET 0x8", "CDXBattleLine__Render callsites", "this+0x70"),
    ),
    "0x0053ab40": (
        "CDXBattleLine__SetupVertex",
        "void __cdecl CDXBattleLine__SetupVertex(float * out_vertex, float screen_base_y, float screen_offset_x, float screen_offset_y, float * source_xy, float intensity, char mode)",
        {"setup-vertex", "cdecl", "marker-vertex-record"},
        ("push seven arguments", "add ESP,0x1c", "0x20-byte marker vertex"),
    ),
    "0x0053abe0": (
        "CDXBattleLine__Render",
        "void __fastcall CDXBattleLine__Render(void * this)",
        {"render", "hud-battleline", "multi-pass", "ecx-only"},
        ("CHud__RenderBattleline", "updates marker vertices", "RenderTriOverlayPass"),
    ),
    "0x0053b470": (
        "CDXBattleLine__RenderTriOverlayPass",
        "void __fastcall CDXBattleLine__RenderTriOverlayPass(void * this)",
        {"overlay-pass", "dynamic-vbuffer", "ecx-only"},
        ("unlocks the dynamic overlay buffer", "this+0x0c", "this+0x60"),
    ),
    "0x0053b5f0": (
        "CDXBattleLine__AppendOverlayVertex",
        "void __thiscall CDXBattleLine__AppendOverlayVertex(void * this, float world_x, float world_y, uint color_rgb)",
        {"append-overlay-vertex", "ret-0xc", "dynamic-vbuffer", "color-rgb"},
        ("RET 0xc", "0xffff00/0xff0808", "0x14-byte overlay vertex"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully re'ed",
    "fully reverse-engineered",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value.startswith("<"):
        return value
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "logs" / "wave589_apply_dry.log",
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave589_apply.log",
        {"updated": 13, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave589_apply_final_dry.log",
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_post_exports(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post" / "metadata.tsv")
    tags = read_tsv(BASE / "post" / "tags.tsv")
    if len(metadata) != 13:
        failures.append(f"metadata row count mismatch: {len(metadata)}")
    if len(tags) != 13:
        failures.append(f"tag row count mismatch: {len(tags)}")

    for address, (name, signature, extra_tags, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post metadata")
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        if row["status"] != "OK":
            failures.append(f"{address} metadata status mismatch: {row['status']}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post tags")
            continue
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        expected_tags = COMMON_TAGS | extra_tags
        missing = expected_tags - actual_tags
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "xrefs.tsv": row_count(BASE / "post" / "xrefs.tsv"),
        "instructions.tsv": row_count(BASE / "post" / "instructions.tsv"),
        "decompile/index.tsv": row_count(BASE / "post" / "decompile" / "index.tsv"),
        "vtables.tsv": row_count(BASE / "post" / "vtables.tsv"),
        "callsite_instructions.tsv": row_count(BASE / "post" / "callsite_instructions.tsv"),
        "append_instructions.tsv": row_count(BASE / "post" / "append_instructions.tsv"),
    }
    if expected_counts["xrefs.tsv"] != 18:
        failures.append("post xref row count mismatch")
    if expected_counts["instructions.tsv"] != 2405:
        failures.append("post instruction row count mismatch")
    if expected_counts["decompile/index.tsv"] != 13:
        failures.append("post decompile row count mismatch")
    if expected_counts["vtables.tsv"] != 64:
        failures.append("post vtable row count mismatch")
    if expected_counts["callsite_instructions.tsv"] != 270:
        failures.append("post callsite instruction row count mismatch")
    if expected_counts["append_instructions.tsv"] != 181:
        failures.append("post append instruction row count mismatch")


def check_xrefs(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post" / "xrefs.tsv")
    actual = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    expected = {
        ("0x0053a050", "CDXBattleLine__Constructor", "0x004814f9", "0x00481450", "CHud__Init", "UNCONDITIONAL_CALL"),
        ("0x0053a120", "CDXBattleLine__scalar_deleting_dtor", "0x005e4f64", "<none>", "<no_function>", "DATA"),
        ("0x0053a140", "CDXBattleLine__DestructorThunk", "0x0053a123", "0x0053a120", "CDXBattleLine__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("0x0053a150", "CDXBattleLine__LoadTextures", "0x00481ae2", "0x00481650", "CHud__LoadTextures", "UNCONDITIONAL_CALL"),
        ("0x0053a280", "CDXBattleLine__Setup", "0x00481af3", "0x00481af0", "CHud__PostLoadProcess", "UNCONDITIONAL_CALL"),
        ("0x0053aa40", "CDXBattleLine__UpdateVertexBuffer", "0x0053ac67", "0x0053abe0", "CDXBattleLine__Render", "UNCONDITIONAL_CALL"),
        ("0x0053aa40", "CDXBattleLine__UpdateVertexBuffer", "0x0053b0e9", "0x0053abe0", "CDXBattleLine__Render", "UNCONDITIONAL_CALL"),
        ("0x0053ab40", "CDXBattleLine__SetupVertex", "0x0053aa94", "0x0053aa40", "CDXBattleLine__UpdateVertexBuffer", "UNCONDITIONAL_CALL"),
        ("0x0053ab40", "CDXBattleLine__SetupVertex", "0x0053aaf8", "0x0053aa40", "CDXBattleLine__UpdateVertexBuffer", "UNCONDITIONAL_CALL"),
        ("0x0053abe0", "CDXBattleLine__Render", "0x00488079", "0x00487d10", "CHud__RenderBattleline", "UNCONDITIONAL_CALL"),
        ("0x0053b470", "CDXBattleLine__RenderTriOverlayPass", "0x0053b276", "0x0053abe0", "CDXBattleLine__Render", "UNCONDITIONAL_CALL"),
        ("0x0053b5f0", "CDXBattleLine__AppendOverlayVertex", "0x00414ce2", "0x00414cb0", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices", "UNCONDITIONAL_CALL"),
        ("0x0053b5f0", "CDXBattleLine__AppendOverlayVertex", "0x00414d35", "0x00414cb0", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices", "UNCONDITIONAL_CALL"),
    }
    missing = expected - actual
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")


def check_instructions_and_vtable(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post" / "instructions.tsv")
    instructions = {
        (normalize_address(row["instruction_addr"]), row["mnemonic"], row["operands"])
        for row in rows
    }
    expected_instructions = {
        ("0x0053a115", "RET", "0x8"),
        ("0x0053a13d", "RET", "0x4"),
        ("0x0053a140", "JMP", "0x00556d90"),
        ("0x0053a100", "CALL", "0x0053a930"),
        ("0x0053a295", "CALL", "0x0053a5e0"),
        ("0x0053a60b", "CALL", "0x0053a390"),
        ("0x0053aa94", "CALL", "0x0053ab40"),
        ("0x0053aaf8", "CALL", "0x0053ab40"),
        ("0x0053ab30", "RET", "0x8"),
        ("0x0053b276", "CALL", "0x0053b470"),
    }
    missing = expected_instructions - instructions
    if missing:
        failures.append(f"missing expected instructions: {sorted(missing)}")

    callsite_rows = read_tsv_rows(BASE / "post" / "callsite_instructions.tsv")
    callsite_instr = {
        (normalize_address(row["instruction_addr"]), row["mnemonic"], row["operands"])
        for row in callsite_rows
    }
    expected_callsite = {
        ("0x004814e8", "PUSH", "0xe"),
        ("0x004814ea", "PUSH", "-0x7"),
        ("0x004814ec", "MOV", "ECX, EAX"),
        ("0x00414cd9", "PUSH", "0xffff00"),
        ("0x00414d2c", "PUSH", "0xff0808"),
    }
    missing = expected_callsite - callsite_instr
    if missing:
        failures.append(f"missing expected callsite instructions: {sorted(missing)}")

    append_rows = read_tsv_rows(BASE / "post" / "append_instructions.tsv")
    append_instr = {
        (normalize_address(row["instruction_addr"]), row["mnemonic"], row["operands"])
        for row in append_rows
    }
    if ("0x0053b803", "RET", "0xc") not in append_instr:
        failures.append("missing AppendOverlayVertex RET 0xc")

    vtables = read_tsv_rows(BASE / "post" / "vtables.tsv")
    slot0 = next((row for row in vtables if row["vtable"] == "005e4f64" and row["slot_index"] == "0"), None)
    if slot0 is None:
        failures.append("missing vtable slot 0")
    elif slot0["function_entry"] != "0053a120" or slot0["function_name"] != "CDXBattleLine__scalar_deleting_dtor":
        failures.append(f"vtable slot 0 mismatch: {slot0}")
    slot1 = next((row for row in vtables if row["vtable"] == "005e4f64" and row["slot_index"] == "1"), None)
    if slot1 is None or slot1["status"] != "NO_FUNCTION_AT_POINTER":
        failures.append("expected slot 1 to remain NO_FUNCTION_AT_POINTER")


def check_queue_and_docs(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    quality = queue["qualitySignals"]
    expected = {
        "commentlessFunctionCount": 3074,
        "undefinedSignatureCount": 1347,
        "paramSignatureCount": 1114,
    }
    for key, expected_value in expected.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x0053b900" or head["name"] != "CClouds__ctor_like_0053b900":
        failures.append(f"unexpected queue head: {head}")

    for label, path, tokens in (
        ("public note", PUBLIC_NOTE, ("Wave589", "CDXBattleLine", "0x0053b900", "DiffCount=0")),
        ("function index", FUNCTION_INDEX, ("DXBattleLine.cpp", "Wave589")),
        ("battleline doc", BATTLELINE_DOC, ("Wave589", "CDXBattleLine__DestructorThunk", "AppendOverlayVertex")),
        ("ghidra reference", GHIDRA_REFERENCE, ("Wave589", "CDXBattleLine__Constructor")),
        ("campaign", CAMPAIGN, ("Wave 589", "CDXBattleLine core/render", "3019")),
        ("backlog", BACKLOG, ("Wave589", "battleline-core-wave589")),
    ):
        text = read_text(path)
        require_tokens(label, text, tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    ledger_text = read_text(LEDGER)
    require_tokens("ledger", ledger_text, ("Wave589", "0x0053a050", "CDXBattleLine__AppendOverlayVertex"), failures)
    attempt_text = read_text(ATTEMPT_LOG)
    require_tokens("attempt log", attempt_text, ("wave589", "ApplyBattleLineCoreWave589.java", "updated=13"), failures)


def check_backup(failures: list[str]) -> None:
    summary = json.loads(read_text(BACKUP_SUMMARY))
    expected = {
        "FileCount": 19,
        "TotalBytes": 160926599,
        "MissingCount": 0,
        "ExtraCount": 0,
        "DiffCount": 0,
        "ManifestHash": "af1567751e713aaac69b5115e81bef5c3821f60b7d92fe27c6ac58173b1b1ee6",
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            failures.append(f"backup {key} mismatch: {summary.get(key)} != {expected_value}")
    if "BEA_20260519-114822_post_wave589_battleline_core_verified" not in summary.get("BackupPath", ""):
        failures.append(f"unexpected backup path: {summary.get('BackupPath')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    try:
        check_logs(failures)
        check_post_exports(failures)
        check_xrefs(failures)
        check_instructions_and_vtable(failures)
        check_queue_and_docs(failures)
        check_backup(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{exc.__class__.__name__}: {exc}")

    if failures:
        print("Wave589 CDXBattleLine core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave589 CDXBattleLine core probe: PASS")
    print("Verified 13 metadata/tag rows, xrefs, instruction evidence, queue counts, docs, logs, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
