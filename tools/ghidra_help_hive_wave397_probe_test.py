#!/usr/bin/env python3
"""Self-tests for ghidra_help_hive_wave397_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_help_hive_wave397_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(
    root: Path,
    *,
    old_owner_name: bool = False,
    missing_created_boundary: bool = False,
    overclaim: bool = False,
) -> argparse.Namespace:
    metadata = root / "metadata.tsv"
    tags = root / "tags.tsv"
    decompile_dir = root / "decompile"
    xrefs = root / "xrefs.tsv"
    instructions = root / "instructions.tsv"
    public_note = root / "note.md"
    dry_log = root / "dry.log"
    apply_log = root / "apply.log"
    out = root / "out.json"

    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tags_lines = ["address\tname\ttags\tstatus"]
    all_instruction_tokens: list[str] = []
    all_xref_tokens: list[str] = []
    for address, spec in probe.TARGETS.items():
        if missing_created_boundary and address == "0x0047fad0":
            metadata_lines.append(f"{address}\t<none>\t<none>\t\tMISSING")
            tags_lines.append(f"{address}\t\t\tMISSING")
            continue
        name = str(spec["name"])
        if old_owner_name and address == "0x0047fb50":
            name = "CExplosionInitThing__RenderOverlayMarkerTextWithDistanceFade"
        comment = " ".join(str(token) for token in spec["commentTokens"])  # type: ignore[index]
        if overclaim and address == "0x004804c0":
            comment += " runtime proof"
        metadata_lines.append(f"{address}\t{name}\t{spec['signature']}\t{comment}\tOK")
        tags_lines.append(f"{address}\t{name}\t{';'.join(spec['tags'])}\tOK")
        decompile_tokens = [str(token) for token in spec["decompileTokens"]]  # type: ignore[index]
        instruction_tokens = [str(token) for token in spec["instructionTokens"]]  # type: ignore[index]
        xref_tokens = [str(token) for token in spec["xrefTokens"]]  # type: ignore[index]
        all_instruction_tokens.extend(instruction_tokens)
        all_xref_tokens.extend(xref_tokens)
        write(decompile_dir / f"{address[2:]}_{name}.c", "\n".join(decompile_tokens) + "\n")

    write(metadata, "\n".join(metadata_lines) + "\n")
    write(tags, "\n".join(tags_lines) + "\n")
    write(xrefs, "\n".join(["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"] + all_xref_tokens) + "\n")
    write(instructions, "\n".join(all_instruction_tokens) + "\n")
    note = "\n".join(
        [
            "# Wave397",
            "0x0047fab0 0x0047fad0 0x0047fb00 0x0047fb50 0x0047fe30 0x004804c0",
            "CHelpTextDisplay__ctor CHelpTextDisplay__scalar_deleting_dtor",
            "CHelpTextDisplay__QueueMessageWithTimestamp CHelpTextDisplay__RenderQueuedMessages",
            "CHiveBoss__Init CHiveBoss__SetVar",
            "does not prove runtime HelpText behavior",
            "does not prove runtime HiveBoss behavior",
            "does not prove rebuild parity",
        ]
    )
    if overclaim:
        note += "\nruntime proof\n"
    write(public_note, note + "\n")
    write(dry_log, "SUMMARY updated=0 skipped=5 created=0 would_create=1 renamed=0 would_rename=4 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=6 skipped=0 created=1 would_create=0 renamed=4 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n")

    return argparse.Namespace(
        metadata=metadata,
        tags=tags,
        xrefs=xrefs,
        instructions=instructions,
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


def test_old_helptext_owner_name_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), old_owner_name=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x0047fb50" in failure and "expected name" in failure for failure in report["failures"])


def test_missing_created_boundary_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), missing_created_boundary=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x0047fad0" in failure and "expected name" in failure for failure in report["failures"])


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), overclaim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_old_helptext_owner_name_fails()
    test_missing_created_boundary_fails()
    test_runtime_overclaim_fails()
    print("PASS ghidra_help_hive_wave397_probe_test: 4/4")
