#!/usr/bin/env python3
"""Validate the Wave383 CGamut Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/gamut-wave383/current")
OUTPUT_NAME = "gamut-wave383.json"

COMMON_TAGS = {
    "static-reaudit",
    "gamut-wave383",
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
    "0x004741b0": target(
        "CGamut__Init",
        "void * __thiscall CGamut__Init(void * this, int init_arg)",
        [
            "Signature/comment hardening",
            "64-cell CGamut grid",
            "0x2000 height buffer",
            "0x1000 visibility buffer",
            "cg_gamutlocked",
            "exact init_arg semantics, source body, runtime culling behavior, and rebuild parity remain unproven",
        ],
        [
            "CGamut__Init",
            "s_C__dev_ONSLAUGHT2_gcgamut_cpp_0062c968",
            "s_cg_gamutlocked_0062c918",
            "s_cg_showgamut_0062c8e0",
            "s_cg_renderimposters_0062c8cc",
        ],
        ["gamut", "frustum-culling", "rendering", "signature-hardened", "comment-hardened"],
    ),
    "0x00474260": target(
        "CGamut__Destroy",
        "void __fastcall CGamut__Destroy(void * this)",
        [
            "Signature/comment hardening",
            "frees the CGamut height buffer",
            "CGamut visibility buffer",
            "clears both slots",
            "runtime shutdown behavior and rebuild parity remain unproven",
        ],
        ["CGamut__Destroy", "OID__FreeObject", "+ 0xc", "+ 0x10"],
        ["gamut", "frustum-culling", "rendering", "destructor", "signature-hardened", "comment-hardened"],
    ),
    "0x004742a0": target(
        "CGamut__ComputePlanes",
        "void __thiscall CGamut__ComputePlanes(void * this, float * frustum_corners)",
        [
            "Signature/comment hardening",
            "takes the caller-built frustum corner buffer",
            "normalizes four frustum-edge plane vectors",
            "writes per-cell signed height ranges",
            "exact source body, local names, data layout, runtime culling behavior, and rebuild parity remain unproven",
        ],
        ["CGamut__ComputePlanes", "frustum_corners", "SQRT", "local_158", "local_164", "local_168", "local_13c"],
        ["gamut", "frustum-culling", "rendering", "plane-rasterization", "signature-hardened", "comment-hardened"],
    ),
    "0x00476a20": target(
        "CGamut__Calculate",
        "void __thiscall CGamut__Calculate(void * this, float * view_matrix, float depth, float width_scale, float height_scale, float * camera_pos)",
        [
            "Signature/comment hardening",
            "CDXEngine::Render callsite supplies",
            "skips recalculation when cg_gamutlocked is set",
            "calls CGamut__ComputePlanes",
            "fills the 64x64 visibility buffer",
            "exact argument semantics, visual runtime behavior, and rebuild parity remain unproven",
        ],
        ["CGamut__Calculate", "DAT_0067a070", "CGamut__ComputePlanes", "view_matrix", "camera_pos", "0x40"],
        ["gamut", "frustum-culling", "rendering", "visibility-grid", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x004741b0", "0x00449acb", "CEngine__Init", "UNCONDITIONAL_CALL"),
    ("0x00474260", "0x004498c1", "CEngine__Shutdown", "UNCONDITIONAL_CALL"),
    ("0x004742a0", "0x00476f81", "CGamut__Calculate", "UNCONDITIONAL_CALL"),
    ("0x00476a20", "0x0053e471", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x004741b0", "0x004741b5", "PUSH", "0x62c968", "68 68 c9 62 00"),
    ("0x004741b0", "0x004741bc", "PUSH", "0x2000", "68 00 20 00 00"),
    ("0x004741b0", "0x004741ef", "CALL", "0x005490e0", "e8 ec 4e 0d 00"),
    ("0x00474260", "0x00474270", "CALL", "0x00549220", "e8 ab 4f 0d 00"),
    ("0x00474260", "0x00474289", "CALL", "0x00549220", "e8 92 4f 0d 00"),
    ("0x004742a0", "0x004742a6", "MOV", "EAX, dword ptr [ESP + 0x16c]", "8b 84 24 6c 01 00 00"),
    ("0x00476a20", "0x00476a20", "MOV", "AL, [0x0067a070]", "a0 70 a0 67 00"),
    ("0x00476a20", "0x00476a39", "MOV", "EAX, dword ptr [ESP + 0xdc]", "8b 84 24 dc 00 00 00"),
]

CALLSITE_EVIDENCE = [
    ("0x00449acb", "PUSH", "0x20"),
    ("0x00449acb", "MOV", "ECX, EAX"),
    ("0x00449acb", "CALL", "0x004741b0"),
    ("0x004498c1", "MOV", "ECX, EDI"),
    ("0x004498c1", "CALL", "0x00474260"),
    ("0x00476f81", "LEA", "EAX, [ESP + 0x80]"),
    ("0x00476f81", "MOV", "ECX, ESI"),
    ("0x00476f81", "PUSH", "EAX"),
    ("0x00476f81", "CALL", "0x004742a0"),
    ("0x0053e471", "MOV", "ECX, dword ptr [EBP + 0x470]"),
    ("0x0053e471", "FSTP", "float ptr [ESP]"),
    ("0x0053e471", "PUSH", "ESI"),
    ("0x0053e471", "PUSH", "0x45000000"),
    ("0x0053e471", "PUSH", "EAX"),
    ("0x0053e471", "CALL", "0x00476a20"),
]

STALE_TOKENS = [
    "undefined CGamut__Init(void)",
    "undefined CGamut__Destroy(void)",
    "undefined CGamut__ComputePlanes(void)",
    "undefined CGamut__Calculate(void)",
    "int param_1",
    "float *param_2",
    "float param_3",
    "float param_4",
    "float param_5",
    "float *param_6",
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime proof",
    "rebuild parity proven",
    "exact source identity proven",
    "complete source identity",
]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key, value in list(row.items()):
            row[key] = unescape_tsv(value or "")
    return rows


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def has_summary(text: str, *, updated: int, skipped: int, renamed: int, would_rename: int) -> bool:
    pattern = (
        rf"SUMMARY:\s+updated={updated}\s+skipped={skipped}\s+renamed={renamed}\s+"
        rf"would_rename={would_rename}\s+missing=0\s+bad=0"
    )
    return re.search(pattern, text) is not None


def decompile_text_for(decompile_dir: Path, address: str) -> str:
    prefix = normalize_address(address)[2:]
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in decompile_dir.glob(f"{prefix}_*.c")
    )


def evidence_hit(
    rows: list[dict[str, str]],
    *,
    target: str,
    instruction_addr: str,
    mnemonic: str,
    operands: str,
    bytes_: str,
) -> bool:
    expected_target = normalize_address(target)
    expected_instruction = normalize_address(instruction_addr)
    return any(
        normalize_address(row.get("target_addr", "")) == expected_target
        and normalize_address(row.get("instruction_addr", "")) == expected_instruction
        and row.get("mnemonic") == mnemonic
        and row.get("operands") == operands
        and row.get("bytes") == bytes_
        for row in rows
    )


def callsite_hit(rows: list[dict[str, str]], *, target: str, mnemonic: str, operands: str) -> bool:
    expected_target = normalize_address(target)
    return any(
        normalize_address(row.get("target_addr", "")) == expected_target
        and row.get("mnemonic") == mnemonic
        and row.get("operands") == operands
        for row in rows
    )


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    callsite_instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "gamut_wave383_dry.log"
    apply_log_path = apply_log_path or root / "gamut_wave383_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    callsite_instructions_path = callsite_instructions_path or root / "callsite_instructions_wave383.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)

    if not has_summary(dry_text, updated=0, skipped=len(TARGETS), renamed=0, would_rename=0):
        failures.append(f"dry-run summary missing/dirty: {relative(dry_log_path)}")
    if not has_summary(apply_text, updated=len(TARGETS), skipped=0, renamed=0, would_rename=0):
        failures.append(f"apply summary missing/dirty: {relative(apply_log_path)}")
    if "REPORT: Save succeeded" not in apply_text:
        failures.append(f"apply log missing save success: {relative(apply_log_path)}")

    metadata_rows = {
        normalize_address(row.get("address", "")): row
        for row in read_tsv(metadata_path)
        if row.get("address")
    }
    tag_rows = {
        normalize_address(row.get("address", "")): row
        for row in read_tsv(tags_path)
        if row.get("address")
    }

    for address, spec in TARGETS.items():
        metadata = metadata_rows.get(address)
        if metadata is None:
            failures.append(f"{address} missing metadata")
            continue
        if metadata.get("status") != "OK":
            failures.append(f"{address} metadata status not OK: {metadata.get('status')}")
        if metadata.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {metadata.get('name')} != {spec['name']}")
        if metadata.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {metadata.get('signature')} != {spec['signature']}")
        comment = metadata.get("comment", "")
        for token in spec["commentTokens"]:
            if str(token) not in comment:
                failures.append(f"{address} missing comment token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment:
                failures.append(f"{address} comment overclaim token present: {token}")

        tag_row = tag_rows.get(address)
        if tag_row is None:
            failures.append(f"{address} missing tags")
        else:
            tags = set(filter(None, tag_row.get("tags", "").split(";")))
            missing_tags = sorted((COMMON_TAGS | set(spec["tags"])) - tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {', '.join(missing_tags)}")

        decompile_text = decompile_text_for(Path(decompile_dir), address)
        if not decompile_text:
            failures.append(f"{address} missing decompile text")
        for token in spec["decompileTokens"]:
            if str(token) not in decompile_text:
                failures.append(f"{address} missing decompile token: {token}")
        for token in STALE_TOKENS:
            if token in decompile_text:
                failures.append(f"{address} stale decompile token present: {token}")

    xrefs = read_tsv(xrefs_path)
    xref_hits = 0
    for target_addr, from_addr, from_function, ref_type in XREF_EVIDENCE:
        expected_target = normalize_address(target_addr)
        expected_from = normalize_address(from_addr)
        hit = any(
            normalize_address(row.get("target_addr", "")) == expected_target
            and normalize_address(row.get("from_addr", "")) == expected_from
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
            for row in xrefs
        )
        if hit:
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target_addr} <- {from_addr} {from_function} {ref_type}")

    instructions = read_tsv(instructions_path)
    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        if evidence_hit(
            instructions,
            target=target_addr,
            instruction_addr=instruction_addr,
            mnemonic=mnemonic,
            operands=operands,
            bytes_=bytes_,
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target_addr} {instruction_addr} {mnemonic} {operands}")

    callsite_instructions = read_tsv(callsite_instructions_path)
    callsite_hits = 0
    for target_addr, mnemonic, operands in CALLSITE_EVIDENCE:
        if callsite_hit(callsite_instructions, target=target_addr, mnemonic=mnemonic, operands=operands):
            callsite_hits += 1
        else:
            failures.append(f"missing callsite evidence: {target_addr} {mnemonic} {operands}")

    return {
        "schema": "ghidra-gamut-wave383/v1",
        "status": "PASS" if not failures else "FAIL",
        "root": relative(root),
        "summary": {
            "targets": len(TARGETS),
            "metadataRows": len(metadata_rows),
            "tagRows": len(tag_rows),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "callsiteEvidenceHits": callsite_hits,
        },
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    output_path = args.out or args.root / OUTPUT_NAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"status={report['status']}")
    print(f"targets={report['summary']['targets']}")
    print(f"xrefEvidenceHits={report['summary']['xrefEvidenceHits']}")
    print(f"instructionEvidenceHits={report['summary']['instructionEvidenceHits']}")
    print(f"callsiteEvidenceHits={report['summary']['callsiteEvidenceHits']}")
    print(f"wrote={relative(output_path)}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
