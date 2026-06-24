#!/usr/bin/env python3
"""Validate Wave515 tentacle / AI static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave515-tentacle-ai-004f0760"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_tentacle_ai_wave515_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "tentacle-ai-wave515",
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime tentacle behavior proven",
    "runtime ai behavior proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004f0760": target(
        "CTentacle__CreateTentacleGuide",
        "void __fastcall CTentacle__CreateTentacleGuide(void * this)",
        ("CTentacle guide factory", "0x005e4170", "0xec-byte", "CMCTentacle__Constructor", "this+0x70"),
        {"factory", "guide", "motion-controller", "tentacle"},
        ("void __fastcall", "OID__AllocObject(0xec,0x1b", "CMCTentacle__Constructor", "+ 0x70"),
    ),
    "0x004f07e0": target(
        "CTentacle__CreateTentacleAI",
        "void __fastcall CTentacle__CreateTentacleAI(void * this)",
        ("CTentacle AI factory", "0x005e4174", "0x20-byte", "CGuide__ctor_base", "this+0x208"),
        {"ai", "factory", "guide", "tentacle"},
        ("void __fastcall", "OID__AllocObject(0x20,0x17", "CGuide__ctor_base", "+ 0x208"),
    ),
    "0x004f0860": target(
        "CTentacle__CreateWarspiteAI",
        "void __thiscall CTentacle__CreateWarspiteAI(void * this, void * init_context)",
        ("Warspite-style AI factory", "0x005e4178", "RET 0x4", "CWarspite__Init", "this+0x13c"),
        {"ai", "factory", "tentacle", "warspite"},
        ("void __thiscall", "init_context", "OID__AllocObject(0x60,0x17", "CWarspite__Init", "+ 0x13c"),
    ),
    "0x004f08f0": target(
        "CTentacleAI__scalar_deleting_dtor",
        "void * __thiscall CTentacleAI__scalar_deleting_dtor(void * this, byte delete_flags)",
        ("scalar deleting destructor", "0x005df49c", "adjacent destructor-base helper", "delete_flags", "RET 0x4"),
        {"ai", "destructor", "tentacle", "vtable-slot-1"},
        ("void * __thiscall", "delete_flags", "CTentacleAI__dtor_base", "CDXMemoryManager__Free"),
    ),
    "0x004f0910": target(
        "CTentacleAI__dtor_base",
        "void __fastcall CTentacleAI__dtor_base(void * this)",
        ("destructor-base", "CTentacleAI__scalar_deleting_dtor", "CUnitAI-style", "+0x28", "CMonitor__Shutdown"),
        {"ai", "base-cleanup", "destructor", "tentacle"},
        ("void __fastcall", "PTR_LAB_005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown"),
    ),
    "0x004f0c50": target(
        "CMCTentacle__BuildOrientationMatrixFromEuler",
        "void __thiscall CMCTentacle__BuildOrientationMatrixFromEuler(void * this, void * out_matrix)",
        ("orientation-matrix builder", "CMCTentacle__UpdateSpline", "RET 0x4", "Mat34__MultiplyBasisToOut", "12 dwords"),
        {"matrix", "motion-controller", "spline", "tentacle"},
        ("void __thiscall", "out_matrix", "CSquadNormal__BuildOrientationMatrixFromEuler", "Mat34__MultiplyBasisToOut", "iVar6 = 0xc"),
    ),
    "0x004f1220": target(
        "CUnit__GetSpeedScaleByFlag30C",
        "double __fastcall CUnit__GetSpeedScaleByFlag30C(void * this)",
        ("speed-scale selector", "this+0x30c", "0x005dbe34", "0x005df464"),
        {"flag", "movement", "speed-scale", "unit"},
        ("double __fastcall", "+ 0x30c", "_DAT_005dbe34", "_DAT_005df464"),
    ),
}

EXPECTED_XREFS = {
    ("0x004f0760", "0x005e4170", "<no_function>", "DATA"),
    ("0x004f07e0", "0x005e4174", "<no_function>", "DATA"),
    ("0x004f0860", "0x005e4178", "<no_function>", "DATA"),
    ("0x004f08f0", "0x005df49c", "<no_function>", "DATA"),
    ("0x004f0910", "0x004f08f3", "CTentacleAI__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("0x004f0c50", "0x0049dd79", "CMCTentacle__UpdateSpline", "UNCONDITIONAL_CALL"),
    ("0x004f1220", "0x004f1483", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004f1220", "0x004f1697", "<no_function>", "UNCONDITIONAL_CALL"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave515_dry.log": "SUMMARY updated=0 skipped=7 renamed=0 would_rename=2 missing=0 bad=0",
    "apply_wave515_apply.log": "SUMMARY updated=7 skipped=0 renamed=2 would_rename=0 missing=0 bad=0",
    "apply_wave515_verify_dry.log": "SUMMARY updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "Wave515",
    "7",
    "CTentacle__CreateTentacleGuide",
    "CTentacleAI__scalar_deleting_dtor",
    "CMCTentacle__BuildOrientationMatrixFromEuler",
    "CUnit__GetSpeedScaleByFlag30C",
    "runtime tentacle behavior",
    "rebuild parity",
)


def normalize_addr(address: str) -> str:
    address = (address or "").strip().lower()
    if not address or address.startswith("<"):
        return address
    body = address[2:] if address.startswith("0x") else address
    return f"0x{int(body, 16):08x}"


def compact_text(value: str) -> str:
    return " ".join((value or "").replace("\t", " ").replace("\r", " ").replace("\n", " ").split())


def compact_token(value: str) -> str:
    return "".join(compact_text(value).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact_token(token) in compact_token(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr"):
            if key in row and row[key]:
                row[key] = normalize_addr(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def find_decomp_file(decomp_dir: Path, address: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    return candidates[0]


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str]:
    wanted = normalize_addr(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    raise AssertionError(f"missing row for {address}")


def validate_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        require(row["status"] == "OK", f"{address} status mismatch: {row['status']}")
        require(row["name"] == expected["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        comment = compact_text(row["comment"])
        for token in expected["comment_tokens"]:
            require(token_present(comment, str(token)), f"{address} comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            require(not token_present(comment, token), f"{address} comment contains overclaim token {token!r}")


def validate_tags(base: Path) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        tags = {tag.strip() for tag in row["tags"].replace(",", ";").split(";") if tag.strip()}
        missing = expected["tags"] - tags
        require(not missing, f"{address} missing tags: {sorted(missing)}")


def validate_decompile(base: Path) -> None:
    decomp_dir = base / "post_decomp"
    require(decomp_dir.exists(), f"missing decompile dir: {decomp_dir}")
    for address, expected in TARGETS.items():
        text = find_decomp_file(decomp_dir, address).read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token_present(text, str(token)), f"{address} decompile missing token {token!r}")


def validate_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    got = {
        (
            row["target_addr"],
            row["from_addr"],
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    missing = EXPECTED_XREFS - got
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


def validate_counts(base: Path) -> None:
    require(len(read_tsv(base / "post_metadata.tsv")) == 7, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 7, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 8, "post xref row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) >= 3000, "post instruction export unexpectedly small")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 7, "post decompile index row count mismatch")
    for row in decomp_index:
        require(row["status"] == "OK", f"decompile failed for {row.get('address')}")


def validate_logs(base: Path) -> None:
    for name, expected in EXPECTED_LOG_SUMMARIES.items():
        path = base / name
        require(path.exists(), f"missing mutation log: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        require(expected in text, f"{name} missing summary {expected!r}")
        require("LockException" not in text, f"{name} contains LockException")
        require("BADNAME:" not in text and "MISSING:" not in text, f"{name} contains failed mutation row")


def validate_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token in text, f"public note missing token {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base
    validate_metadata(base)
    validate_tags(base)
    validate_decompile(base)
    validate_xrefs(base)
    validate_counts(base)
    validate_logs(base)
    validate_public_note()
    print(f"PASS wave515 tentacle AI evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
