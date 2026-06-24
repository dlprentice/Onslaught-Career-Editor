#!/usr/bin/env python3
"""Self-tests for ghidra_fepmultiplayerstart_subobj_wave399_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_fepmultiplayerstart_subobj_wave399_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> argparse.Namespace:
    metadata = root / "metadata.tsv"
    tags = root / "tags.tsv"
    decompile_dir = root / "decompile"
    xrefs = root / "xrefs.tsv"
    instructions = root / "instructions.tsv"
    vtable_slots = root / "vtable_slots.tsv"
    public_note = root / "note.md"
    dry_log = root / "dry.log"
    apply_log = root / "apply.log"
    out = root / "out.json"

    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tags_lines = ["address\tname\ttags\tstatus"]
    xref_tokens: list[str] = []
    instruction_tokens: list[str] = []
    vtable_lines = [
        "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus"
    ]
    for address, spec in probe.TARGETS.items():
        signature = str(spec["signature"])
        if stale_signature and address == "0x00459e50":
            signature = (
                "void __stdcall CFEPMultiplayerStart__SubObj8848__RenderPreCommon"
                "(void * this, float transition)"
            )
        comment = " ".join(str(token) for token in spec["commentTokens"])  # type: ignore[index]
        if overclaim and address == "0x00459ee0":
            comment += " runtime proof"
        metadata_lines.append(f"{address}\t{spec['name']}\t{signature}\t{comment}\tOK")
        tags_lines.append(f"{address}\t{spec['name']}\t{';'.join(spec['tags'])}\tOK")
        write(
            decompile_dir / f"{address[2:]}_{spec['name']}.c",
            "\n".join(str(token) for token in spec["decompileTokens"]) + "\n",  # type: ignore[index]
        )
        xref_tokens.extend(str(token) for token in spec["xrefTokens"])  # type: ignore[index]
        instruction_tokens.extend(str(token) for token in spec["instructionTokens"])  # type: ignore[index]

    for slot, address in probe.EXPECTED_VTABLE_SLOTS.items():
        spec = probe.TARGETS[address]
        vtable_lines.append(
            f"005db4fc\t{slot}\t005db4fc\t{address}\t{address[2:]}\t{address[2:]}\t{spec['name']}\t{address[2:]}\t{spec['name']}\tOK"
        )

    write(metadata, "\n".join(metadata_lines) + "\n")
    write(tags, "\n".join(tags_lines) + "\n")
    write(xrefs, "\n".join(["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"] + xref_tokens) + "\n")
    write(instructions, "\n".join(instruction_tokens) + "\n")
    write(vtable_slots, "\n".join(vtable_lines) + "\n")
    note = "\n".join(
        [
            "# Wave399",
            "0x00459810 0x00459920 0x004599a0 0x00459a60 0x00459aa0 0x00459b00 0x00459c10 0x00459e50 0x00459ee0",
            "CFEPMultiplayerStart__SubObj8848__RenderPreCommon",
            "does not prove runtime multiplayer behavior",
            "does not prove exact source identity",
            "does not prove rebuild parity",
        ]
    )
    if overclaim:
        note += "\nruntime proof\n"
    write(public_note, note + "\n")
    write(dry_log, "SUMMARY updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n")

    return argparse.Namespace(
        metadata=metadata,
        tags=tags,
        xrefs=xrefs,
        instructions=instructions,
        vtable_slots=vtable_slots,
        decompile_dir=decompile_dir,
        public_note=public_note,
        dry_log=dry_log,
        apply_log=apply_log,
        out=out,
    )


def test_happy_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report, status = probe.validate(build_fixture(Path(tmp)))
        assert status == 0, report["failures"]
        assert report["status"] == "PASS"


def test_stale_render_precommon_signature_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report, status = probe.validate(build_fixture(Path(tmp), stale_signature=True))
        assert status == 1
        assert any("0x00459e50" in failure and "expected signature" in failure for failure in report["failures"])


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report, status = probe.validate(build_fixture(Path(tmp), overclaim=True))
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_stale_render_precommon_signature_fails()
    test_runtime_overclaim_fails()
    print("PASS ghidra_fepmultiplayerstart_subobj_wave399_probe_test: 3/3")
