#!/usr/bin/env python3
"""Validate Wave467 CFrontEnd render/static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave467-frontend-render-current"
COMMON_TAGS = {"static-reaudit", "cfrontend-render-wave467", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 15,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 2,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 15,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 2,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 15,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004662a0": target(
        "CFrontEnd__Init",
        "int __thiscall CFrontEnd__Init(void * this, int entry, int in_loaded_system)",
        ["Wave467 correction", "CFrontEnd::Init", "loading ranges", "page table wiring"],
        ["frontend", "source-bridge", "initialization", "signature-corrected", "comment-hardened"],
        ["CConsole__SetLoadingRange", "CFrontEnd__LoadSharedResources", "CFrontEnd__SetPage", "CText__Init"],
    ),
    "0x00466990": target(
        "CFrontEnd__NumControllersPresent",
        "int __thiscall CFrontEnd__NumControllersPresent(void * this)",
        ["Wave467 correction", "returns fixed value 2", "source-adjacent"],
        ["frontend", "controllers", "source-bridge", "signature-corrected", "comment-hardened"],
        ["return 2"],
    ),
    "0x00466de0": target(
        "CFrontEnd__DrawLine",
        "void __thiscall CFrontEnd__DrawLine(void * this, float sx, float sy, float ex, float ey, uint argb, float width, float depth, float percent)",
        ["Wave467 correction", "CFrontEnd::DrawLine", "level-link surface"],
        ["frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"],
        ["CDXSurf__RenderSurface", "percent", "width"],
    ),
    "0x00466e70": target(
        "CFrontEnd__DrawBox",
        "void __thiscall CFrontEnd__DrawBox(void * this, float tlx, float tly, float brx, float bry, uint argb, float width, float depth)",
        ["Wave467 correction", "CFrontEnd::DrawBox", "four line-sprite draws"],
        ["frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"],
        ["CDXSurf__RenderSurface", "tlx", "brx"],
    ),
    "0x00467010": target(
        "CFrontEnd__DrawPanel",
        "void __thiscall CFrontEnd__DrawPanel(void * this, float tlx, float tly, float brx, float bry, float depth, uint argb)",
        ["Wave467 correction", "CFrontEnd::DrawPanel", "clamps texture addressing"],
        ["frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"],
        ["D3DStateCache__SetState114Raw", "CDXSurf__RenderSurface", "argb"],
    ),
    "0x004670b0": target(
        "CFrontEnd__DrawBarGraph",
        "void __thiscall CFrontEnd__DrawBarGraph(void * this, float tlx, float tly, float brx, float bry, float num, float max, float depth, uint border_argb, uint back_argb, uint fore_argb)",
        ["Wave467 correction", "CFrontEnd::DrawBarGraph", "background and nonzero filled bar"],
        ["frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"],
        ["CDXSurf__RenderSurface", "num", "max"],
    ),
    "0x004679e0": target(
        "CFrontEnd__RenderPreCommonFade",
        "void __stdcall CFrontEnd__RenderPreCommonFade(float transition, uint argb, int destination_page)",
        ["Wave467 correction", "transition-derived alpha", "full-window"],
        ["frontend", "pre-common-render", "fade", "signature-corrected", "comment-hardened"],
        ["CFrontEnd__RenderVideoQuadScaledToWindow", "transition", "argb"],
    ),
    "0x00467ae0": target(
        "CFrontEnd__DrawBar",
        "void __thiscall CFrontEnd__DrawBar(void * this, float sx, float sy, float depth, int segment_count, uint argb, float scale)",
        ["Wave467 correction", "CFrontEnd::DrawBar", "segment_count + 2 sprites"],
        ["frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"],
        ["CDXSurf__RenderSurface", "segment_count", "scale"],
    ),
    "0x004681c0": target(
        "CFrontEnd__EnableAdditiveAlpha",
        "void __thiscall CFrontEnd__EnableAdditiveAlpha(void * this)",
        ["Wave467 correction", "CFrontEnd::EnableAdditiveAlpha", "source and destination blend"],
        ["frontend", "render-state", "source-bridge", "signature-corrected", "comment-hardened"],
        ["RenderState_Set(0x13,2)", "RenderState_Set(0x14,2)"],
    ),
    "0x004681e0": target(
        "CFrontEnd__EnableModulateAlpha",
        "void __thiscall CFrontEnd__EnableModulateAlpha(void * this)",
        ["Wave467 correction", "CFrontEnd::EnableModulateAlpha", "source-alpha"],
        ["frontend", "render-state", "source-bridge", "signature-corrected", "comment-hardened"],
        ["RenderState_Set(0x13,5)", "RenderState_Set(0x14,6)"],
    ),
    "0x004684d0": target(
        "CFrontEnd__Run",
        "int __thiscall CFrontEnd__Run(void * this, int entry, int in_loaded_system)",
        ["Wave467 correction", "CFrontEnd::Run", "process/render loop"],
        ["frontend", "main-loop", "source-bridge", "signature-corrected", "comment-hardened"],
        ["CFrontEnd__Init", "CFrontEnd__Process", "CFrontEnd__Render"],
    ),
    "0x004685a0": target(
        "CFrontEnd__UpdateCamera",
        "void __thiscall CFrontEnd__UpdateCamera(void * this)",
        ["Wave467 correction", "CFrontEnd::UpdateCamera", "CDXEngine path"],
        ["frontend", "camera", "source-bridge", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CEngine__GetViewMatrixFromCamera", "CDXEngine__SetViewAndProjection"],
    ),
    "0x004685f0": target(
        "CFrontEnd__RenderStart",
        "int __thiscall CFrontEnd__RenderStart(void * this)",
        ["Wave467 correction", "CFrontEnd::RenderStart", "CDXFrontEnd::RenderStart"],
        ["frontend", "render-start", "vtable-slot", "source-bridge", "name-corrected", "signature-corrected", "comment-hardened"],
        ["PLATFORM__BeginScene", "CDXEngine__SetProjectionMatrix", "CDXEngine__ApplyPendingRenderState"],
    ),
    "0x00468730": target(
        "CFrontEnd__GetShadowOffsetX",
        "float __thiscall CFrontEnd__GetShadowOffsetX(void * this)",
        ["Wave467 correction", "shadow X offset", "sin"],
        ["frontend", "shadow-offset", "source-bridge", "signature-corrected", "comment-hardened"],
        ["fsin", "_DAT_008a9570"],
    ),
    "0x00468750": target(
        "CFrontEnd__GetShadowOffsetY",
        "float __thiscall CFrontEnd__GetShadowOffsetY(void * this)",
        ["Wave467 correction", "shadow Y offset", "cos"],
        ["frontend", "shadow-offset", "source-bridge", "signature-corrected", "comment-hardened"],
        ["fcos", "_DAT_008a9570"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004662a0", "0x004684ef", "CFrontEnd__Run"),
    ("0x00466990", "0x0051f617", "CFEPOptions__ProcessInput"),
    ("0x00466990", "0x004621fe", "CFEPMain__GetActionCount"),
    ("0x00466de0", "0x00461724", "CFEPLevelSelect__Render"),
    ("0x00466e70", "0x0044d858", "CFrontEnd__RenderAndProcessModalPanel"),
    ("0x00467010", "0x005212b7", "CFEPVirtualKeyboard__DrawPanel"),
    ("0x004670b0", "0x0044d978", "CFrontEnd__RenderAndProcessModalPanel"),
    ("0x00467ae0", "0x0051c347", "CFEPLanguageTest__Render"),
    ("0x004681c0", "0x0046435d", "CFEPMain__Render"),
    ("0x004681e0", "0x004643f4", "CFEPMain__Render"),
    ("0x004684d0", "0x004f03c0", "CLTShell__RunFrontEndAndGameLoop"),
    ("0x004685a0", "0x00450866", "CFEPBEConfig__Render"),
    ("0x004685f0", "0x00540fa6", "CDXFrontEnd__VFunc_06_00540f70"),
    ("0x004685f0", "0x005db774", "<no_function>"),
    ("0x00468730", "0x0046388f", "CFEPMain__Render"),
    ("0x00468750", "0x00463d3b", "CFEPMain__Render"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime rendering proven",
    "exact layout proven",
    "source identity proven",
    "fully re'ed",
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


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
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


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"updated=\d+.*bad=\d+", text)
    if not match:
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(0))}


def check_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    actual = parse_summary(read_text(path))
    if not actual:
        failures.append(f"{path.name}: missing SUMMARY")
        return
    for key, value in expected.items():
        if actual.get(key) != value:
            failures.append(f"{path.name}: expected {key}={value}, got {actual.get(key)}")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_metadata.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"post_metadata.tsv: missing {address}")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    seen: dict[str, set[str]] = {}
    for row in rows:
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        seen.setdefault(row.get("address", ""), set()).update(tags)
    for address, expected in TARGETS.items():
        actual = seen.get(normalize_address(address), set())
        for tag in expected["tags"]:
            if tag not in actual:
                failures.append(f"{address}: missing tag {tag}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"post-decomp: missing {address}")
            continue
        for token in expected["decompileTokens"]:
            if not token_present(text, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    actual = {
        (row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", ""))
        for row in rows
    }
    for edge in EXPECTED_XREF_EDGES:
        normalized = (normalize_address(edge[0]), normalize_address(edge[1]), edge[2])
        if normalized not in actual:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


def check_instruction_rows(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    if len(rows) < 200:
        failures.append(f"post_instructions.tsv: expected broad context rows, got {len(rows)}")
    target_rows = {
        row.get("target_addr", "")
        for row in rows
        if row.get("role") == "TARGET"
    }
    for address in TARGETS:
        if normalize_address(address) not in target_rows:
            failures.append(f"post_instructions.tsv: missing target instruction for {address}")


def run_checks(base: Path) -> list[str]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_instruction_rows(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    failures = run_checks(args.base)
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print(f"PASS Wave467 CFrontEnd render checks for {len(TARGETS)} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
