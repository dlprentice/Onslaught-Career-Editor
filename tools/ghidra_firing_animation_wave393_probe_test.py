#!/usr/bin/env python3
"""Self-tests for ghidra_firing_animation_wave393_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_firing_animation_wave393_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, overclaim: bool = False, clear_claim: bool = False) -> argparse.Namespace:
    metadata = root / "metadata.tsv"
    tags = root / "tags.tsv"
    decompile_dir = root / "decompile"
    xrefs = root / "xrefs.tsv"
    vtable_slots = root / "vtable_slots.tsv"
    instructions = root / "instructions.tsv"
    public_note = root / "note.md"
    dry_log = root / "dry.log"
    apply_log = root / "apply.log"
    out = root / "out.json"

    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tags_lines = ["address\tname\ttags\tstatus"]
    decompile_tokens: list[str] = []
    instruction_tokens: list[str] = []
    for idx, (address, spec) in enumerate(probe.TARGETS.items()):
        comment_tokens = list(spec["commentTokens"])  # type: ignore[index]
        if overclaim and idx == 0:
            comment_tokens.append("runtime proof")
        if clear_claim and address == "0x0047d670":
            comment_tokens.append("clears both slots")
        comment = " ".join(str(token) for token in comment_tokens)
        metadata_lines.append(f"{address}\t{spec['name']}\t{spec['signature']}\t{comment}\tOK")
        tags_lines.append(f"{address}\t{spec['name']}\t{';'.join(spec['tags'])}\tOK")
        decompile_tokens.extend(str(token) for token in spec["decompileTokens"])  # type: ignore[index]
        instruction_tokens.extend(str(token) for token in spec["instructionTokens"])  # type: ignore[index]
        write(decompile_dir / f"{address[2:]}_{spec['name']}.c", "\n".join(str(token) for token in spec["decompileTokens"]))  # type: ignore[index]

    write(metadata, "\n".join(metadata_lines) + "\n")
    write(tags, "\n".join(tags_lines) + "\n")
    write(
        xrefs,
        "\n".join(
            [
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type",
                "0047d3b0\tCMonitor__TryQueuePrefireAnimation\t005e2ad4\t<none>\t<no_function>\tDATA",
                "0047d420\tCUnitAI__QueueFiringOrPostfireAnimation\t005e2ad8\t<none>\t<no_function>\tDATA",
                "0047d670\tCUnitAI__FreeOwnedObjects_10_18\t005d2c59\t005d2c53\tUnwind@005d2c53\tUNCONDITIONAL_CALL",
            ]
        )
        + "\n",
    )
    write(
        vtable_slots,
        "\n".join(
            [
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus",
                "005e297c\t86\t005e2ad4\t0x0047d3b0\t0047d3b0\t0047d3b0\tCMonitor__TryQueuePrefireAnimation\t0047d3b0\tCMonitor__TryQueuePrefireAnimation\tOK",
                "005e297c\t87\t005e2ad8\t0x0047d420\t0047d420\t0047d420\tCUnitAI__QueueFiringOrPostfireAnimation\t0047d420\tCUnitAI__QueueFiringOrPostfireAnimation\tOK",
            ]
        )
        + "\n",
    )
    write(instructions, "\n".join(instruction_tokens + decompile_tokens) + "\n")
    note_text = "\n".join(
        [
            "# Wave393",
            "0x0047d3b0 0x0047d420 0x0047d670",
            "CGroundVehicle vtable slots 86 and 87",
            "does not claim slot clearing",
            "does not prove runtime animation behavior",
            "does not prove rebuild parity",
        ]
    )
    if overclaim:
        note_text += "\nruntime proof\n"
    write(public_note, note_text + "\n")
    write(dry_log, "SUMMARY updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=3 skipped=0 renamed=0 would_rename=0 missing=0 bad=0\n")

    return argparse.Namespace(
        metadata=metadata,
        tags=tags,
        xrefs=xrefs,
        vtable_slots=vtable_slots,
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


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), overclaim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


def test_cleanup_clear_claim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), clear_claim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("clears both slots" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_runtime_overclaim_fails()
    test_cleanup_clear_claim_fails()
    print("PASS ghidra_firing_animation_wave393_probe_test: 3/3")
