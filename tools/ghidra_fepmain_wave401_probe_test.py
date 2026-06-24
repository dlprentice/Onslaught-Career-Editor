#!/usr/bin/env python3
"""Self-tests for ghidra_fepmain_wave401_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_fepmain_wave401_probe as probe


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
        if stale_signature and address == "0x004621d0":
            signature = "int __cdecl CFEPMain__GetMenuType(void * this)"
        comment = " ".join(str(token) for token in spec["commentTokens"])  # type: ignore[index]
        if source_overclaim and address == "0x004623e0":
            comment += " source identity proven"
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
        "# Wave401",
        "0x004621b0 0x004621d0 0x004621e0 0x00462250 0x004623e0 0x00462640",
        "0x00462b70 0x00462c90 0x00462d40 0x004644d0 0x00464520",
        "CFEPMain__Init CFEPMain__GetMenuType CFEPMain__GetActionCount CFEPMain__ButtonPressed",
        "CFEPMain__DoAction CFEPMain__Process CFEPMain__RenderPreCommon CFEPMain__Update",
        "CFEPMain__Render CFEPMain__TransitionNotification CFEPMain__ActiveNotification",
        "0x005dbae4",
        "0x005dbaf0 starts with CFEPMain__ButtonPressed",
        "0x005dbb00 points to CFEPMain__ActiveNotification",
        "FEPMain.cpp is absent from the current Stuart source snapshot",
        "does not prove runtime frontend behavior",
        "does not prove exact source identity",
        "does not prove rebuild parity",
    ]
    if stale_vtable_note:
        note_lines = [line.replace("0x005dbae4", "0x005dbaf0") for line in note_lines]
        note_lines.append("0x005dbaf0 starts with CFEPMain__Process")
    if source_overclaim:
        note_lines.append("source identity proven")
    write(public_note, "\n".join(note_lines) + "\n")
    write(dry_log, "SUMMARY updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=11 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n")

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
        assert any("0x004621d0" in failure and "expected signature" in failure for failure in report["failures"])


def test_stale_vtable_note_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), stale_vtable_note=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("public note overclaim token" in failure for failure in report["failures"])


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
    print("PASS ghidra_fepmain_wave401_probe_test: 4/4")
