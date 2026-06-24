#!/usr/bin/env python3
"""Self-tests for ghidra_hud_head_wave400_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_hud_head_wave400_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(
    root: Path,
    *,
    stale_overlay_owner: bool = False,
    stale_signature: bool = False,
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
        name = str(spec["name"])
        if stale_overlay_owner and address == "0x00482090":
            name = "CExplosionInitThing__SetupOverlayMarkerRenderState"
        signature = str(spec["signature"])
        if stale_signature and address == "0x00481450":
            signature = "undefined CHud__Init(void)"
        comment = " ".join(str(token) for token in spec["commentTokens"])  # type: ignore[index]
        if overclaim and address == "0x00482210":
            comment += " runtime proof"

        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK")
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
            "# Wave400",
            "0x00481400 0x00481450 0x004815c0 0x00481650 0x00481af0 0x00481b00",
            "0x00481f40 0x00482050 0x00482090 0x004821b0 0x004821e0 0x00482210",
            "CHud__ctor_base CHud__Init CHud__Reset CHud__LoadTextures",
            "CHud__PostLoadProcess CHud__ShutDown CHud__SetHudComponent",
            "CHud__PromotePendingHudComponent HudRenderState__ApplyOverlaySpriteState",
            "CDXCompass__ApplyRenderStateModulate CDXCompass__ApplyRenderStateAdditive",
            "CHud__RenderSegmentedMeterBar",
            "does not prove runtime HUD behavior",
            "does not prove concrete CHud layout",
            "does not prove rebuild parity",
        ]
    )
    if overclaim:
        note += "\nruntime proof\n"
    write(public_note, note + "\n")
    write(dry_log, "SUMMARY updated=0 skipped=12 created=0 would_create=0 renamed=0 would_rename=4 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=12 skipped=0 created=0 would_create=0 renamed=4 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n")

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


def test_stale_overlay_owner_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), stale_overlay_owner=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x00482090" in failure and "expected name" in failure for failure in report["failures"])


def test_stale_signature_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), stale_signature=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("0x00481450" in failure and "expected signature" in failure for failure in report["failures"])


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), overclaim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_stale_overlay_owner_fails()
    test_stale_signature_fails()
    test_runtime_overclaim_fails()
    print("PASS ghidra_hud_head_wave400_probe_test: 4/4")
