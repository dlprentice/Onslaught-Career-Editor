#!/usr/bin/env python3
"""Self-tests for ghidra_goodies_wave395_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_goodies_wave395_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(
    root: Path,
    *,
    missing_tag: bool = False,
    overclaim: bool = False,
    stale_comment: bool = False,
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
        comment_tokens = list(spec["commentTokens"])  # type: ignore[index]
        comment = " ".join(str(token) for token in comment_tokens)
        if stale_comment and address == "0x0045cde0":
            comment = "old placeholder comment"
        if overclaim and address == "0x0045c870":
            comment += " runtime proof"
        metadata_lines.append(f"{address}\t{spec['name']}\t{spec['signature']}\t{comment}\tOK")

        tag_values = list(spec["tags"])  # type: ignore[index]
        if missing_tag and address == "0x0045cb80":
            tag_values = [tag for tag in tag_values if tag != "goodie-grid"]
        tags_lines.append(f"{address}\t{spec['name']}\t{';'.join(tag_values)}\tOK")

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
    note = "\n".join(
        [
            "# Wave395",
            "0x0045ac30 0x0045c770 0x0045c870 0x0045c9f0 0x0045cb80 0x0045cc10 0x0045cd10 0x0045cde0",
            "does not prove runtime Goodies behavior",
            "does not prove hidden Goodies 71-73 reachability",
            "does not prove rebuild parity",
        ]
    )
    if overclaim:
        note += "\nruntime proof\n"
    write(public_note, note + "\n")
    write(dry_log, "SUMMARY updated=0 skipped=8 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=8 skipped=0 missing=0 bad=0\nREPORT: Save succeeded\n")

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


def test_missing_grid_tag_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), missing_tag=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x0045cb80" in failure and "goodie-grid" in failure for failure in report["failures"])


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), overclaim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


def test_stale_comment_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), stale_comment=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x0045cde0" in failure and "missing comment token" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_missing_grid_tag_fails()
    test_runtime_overclaim_fails()
    test_stale_comment_fails()
    print("PASS ghidra_goodies_wave395_probe_test: 4/4")
