#!/usr/bin/env python3
"""Self-tests for ghidra_fepdemo_wave402_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_fepdemo_wave402_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(
    root: Path,
    *,
    stale_signature: bool = False,
    stale_vtable_note: bool = False,
    source_overclaim: bool = False,
) -> argparse.Namespace:
    metadata = root / "metadata.tsv"
    tags = root / "tags.tsv"
    decompile_dir = root / "decompile"
    xrefs = root / "xrefs.tsv"
    instructions = root / "instructions.tsv"
    vtables = root / "vtables.tsv"
    public_note = root / "note.md"
    dry_log = root / "dry.log"
    apply_log = root / "apply.log"
    out = root / "out.json"

    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tags_lines = ["address\tname\ttags\tstatus"]
    all_instruction_tokens: list[str] = []
    all_xref_tokens: list[str] = []

    for address, spec in probe.TARGETS.items():
        signature = str(spec["signature"])
        if stale_signature and address == "0x00457ec0":
            signature = "int __cdecl CFEPDemoMain__GetMenuType(void * this)"
        comment = " ".join(str(token) for token in spec["commentTokens"])  # type: ignore[index]
        if source_overclaim and address == "0x00457ee0":
            comment += " exact source identity proven"
        metadata_lines.append(f"{address}\t{spec['name']}\t{signature}\t{comment}\tOK")
        tags_lines.append(f"{address}\t{spec['name']}\t{';'.join(spec['tags'])}\tOK")

        decompile_tokens = [str(token) for token in spec["decompileTokens"]]  # type: ignore[index]
        instruction_tokens = [str(token) for token in spec["instructionTokens"]]  # type: ignore[index]
        xref_tokens = [str(token) for token in spec["xrefTokens"]]  # type: ignore[index]
        all_instruction_tokens.extend(instruction_tokens)
        all_xref_tokens.extend(xref_tokens)
        write(decompile_dir / f"{address[2:]}_{spec['name']}.c", "\n".join(decompile_tokens) + "\n")

    write(metadata, "\n".join(metadata_lines) + "\n")
    write(tags, "\n".join(tags_lines) + "\n")
    write(xrefs, "\n".join(["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"] + all_xref_tokens) + "\n")
    write(instructions, "\n".join(all_instruction_tokens) + "\n")
    write(vtables, "\n".join(probe.EXPECTED_VTABLE_TOKENS) + "\n")

    note_lines = [
        "# Wave402",
        "0x00457ec0 0x00457ed0 0x00457ee0 0x00457f20",
        "CFEPDemoMain__GetMenuType CFEPDemoMain__GetActionCount CFEPDemoMain__DoAction CFEPDemoMain__Update",
        "0x005db7c0",
        "0x005e4a78 is an extra data-table xref to CFEPDemoMain__GetMenuType",
        "FEPDemoMain source file was not found in the current Stuart source snapshot",
        "does not prove runtime frontend behavior",
        "does not prove exact source identity",
        "does not prove rebuild parity",
    ]
    if stale_vtable_note:
        note_lines = [line.replace("0x005db7c0", "0x005db7cc") for line in note_lines]
    if source_overclaim:
        note_lines.append("source identity proven")
    write(public_note, "\n".join(note_lines) + "\n")
    write(dry_log, "SUMMARY updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=4 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n")

    return argparse.Namespace(
        metadata=metadata,
        tags=tags,
        xrefs=xrefs,
        instructions=instructions,
        vtables=vtables,
        decompile_dir=decompile_dir,
        public_note=public_note,
        dry_log=dry_log,
        apply_log=apply_log,
        out=out,
    )


def test_happy_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp))
        report, status = probe.validate(args)
        assert status == 0, report["failures"]
        assert report["status"] == "PASS"


def test_stale_signature_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), stale_signature=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x00457ec0" in failure and "expected signature" in failure for failure in report["failures"])


def test_stale_vtable_note_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), stale_vtable_note=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("public note missing token" in failure for failure in report["failures"])


def test_source_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), source_overclaim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_stale_signature_fails()
    test_stale_vtable_note_fails()
    test_source_overclaim_fails()
    print("PASS ghidra_fepdemo_wave402_probe_test: 4/4")
