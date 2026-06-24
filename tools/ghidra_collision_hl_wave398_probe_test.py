#!/usr/bin/env python3
"""Self-tests for ghidra_collision_hl_wave398_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_collision_hl_wave398_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(
    root: Path,
    *,
    stale_owner_name: bool = False,
    stale_param_signature: bool = False,
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
    all_xref_tokens: list[str] = []
    all_instruction_tokens: list[str] = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        if stale_owner_name and address == "0x00480a30":
            name = "CCollisionSeekingRound__ScanNeighborSectorsAndDispatchCollisions"
        signature = str(spec["signature"])
        if stale_param_signature and address == "0x00481060":
            signature = (
                "void __thiscall CHLCollisionDetector__ProcessMapWhoCollisionSweep"
                "(void * this, void * param_1, void * param_2, void * param_3)"
            )
        comment = " ".join(str(token) for token in spec["commentTokens"])  # type: ignore[index]
        if overclaim and address == "0x004812d0":
            comment += " runtime proof"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK")
        tags_lines.append(f"{address}\t{name}\t{';'.join(spec['tags'])}\tOK")
        write(
            decompile_dir / f"{address[2:]}_{name}.c",
            "\n".join(str(token) for token in spec["decompileTokens"]) + "\n",  # type: ignore[index]
        )
        all_xref_tokens.extend(str(token) for token in spec["xrefTokens"])  # type: ignore[index]
        all_instruction_tokens.extend(str(token) for token in spec["instructionTokens"])  # type: ignore[index]

    write(metadata, "\n".join(metadata_lines) + "\n")
    write(tags, "\n".join(tags_lines) + "\n")
    write(xrefs, "\n".join(["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"] + all_xref_tokens) + "\n")
    write(instructions, "\n".join(all_instruction_tokens) + "\n")
    note = "\n".join(
        [
            "# Wave398",
            "0x00480a30 0x00480c90 0x00480db0 0x00480e10 0x00480ed0 0x00481060 0x004812d0",
            "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
            "CHLCollisionDetector__HandleCollisionEnter CHLCollisionDetector__HandleCollisionExit",
            "CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions",
            "CHLCollisionDetector__DispatchCollisionEventForPair",
            "CHLCollisionDetector__ProcessMapWhoCollisionSweep",
            "CHLCollisionDetector__HandleScheduledCollisionEvent",
            "does not prove runtime collision behavior",
            "does not prove rebuild parity",
        ]
    )
    if overclaim:
        note += "\nruntime proof\n"
    write(public_note, note + "\n")
    write(dry_log, "SUMMARY updated=0 skipped=7 renamed=0 would_rename=3 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=7 skipped=0 renamed=3 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n")

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


def test_stale_owner_name_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), stale_owner_name=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x00480a30" in failure and "expected name" in failure for failure in report["failures"])


def test_stale_param_signature_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), stale_param_signature=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x00481060" in failure and "expected signature" in failure for failure in report["failures"])


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), overclaim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_stale_owner_name_fails()
    test_stale_param_signature_fails()
    test_runtime_overclaim_fails()
    print("PASS ghidra_collision_hl_wave398_probe_test: 4/4")
