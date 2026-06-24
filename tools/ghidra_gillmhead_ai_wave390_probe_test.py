#!/usr/bin/env python3
"""Self-tests for ghidra_gillmhead_ai_wave390_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_gillmhead_ai_wave390_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, overclaim: bool = False) -> argparse.Namespace:
    metadata = root / "metadata.tsv"
    tags = root / "tags.tsv"
    decompile_dir = root / "decompile"
    vtable_types = root / "vtable_types.tsv"
    vtable_slots = root / "vtable_slots.tsv"
    pointer_table = root / "pointer_table.tsv"
    xrefs = root / "xrefs.tsv"
    dry_log = root / "dry.log"
    apply_log = root / "apply.log"
    out = root / "out.json"

    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tags_lines = ["address\tname\ttags\tstatus"]
    for idx, (addr, spec) in enumerate(probe.TARGETS.items()):
        comment_tokens = list(spec["commentTokens"])  # type: ignore[index]
        if overclaim and idx == 0:
            comment_tokens.append("runtime proof")
        comment = " ".join(str(token) for token in comment_tokens)
        metadata_lines.append(f"{addr}\t{spec['name']}\t{spec['signature']}\t{comment}\tOK")
        tags_lines.append(f"{addr}\t{spec['name']}\t{';'.join(spec['tags'])}\tOK")
        decompile = "\n".join(str(token) for token in spec["decompileTokens"])  # type: ignore[index]
        write(decompile_dir / f"{addr[2:]}_{spec['name']}.c", decompile)

    write(metadata, "\n".join(metadata_lines) + "\n")
    write(tags, "\n".join(tags_lines) + "\n")
    write(
        vtable_types,
        "\n".join(
            [
                "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name",
                "005dbcec\t005dbce8\t00614068\t0x0\t0\t0\t0x0\t0x0\t.?AVCGillMHeadAI@@\tCGillMHeadAI",
                "005d8d1c\t005d8d18\t0060c850\t0x0\t0\t0\t0x0\t0x0\t.?AVCUnitAI@@\tCUnitAI",
            ]
        )
        + "\n",
    )
    write(
        vtable_slots,
        "\n".join(
            [
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus",
                "005dbcec\t1\t005dbcf0\t0x0047a7f0\t0047a7f0\t0047a7f0\tCGillMHeadAI__ScalarDeletingDestructor\t0047a7f0\tCGillMHeadAI__ScalarDeletingDestructor\tOK",
                "005dbcec\t3\t005dbcf8\t0x0047afc0\t0047afc0\t0047afc0\tCGillMHeadAI__UpdateAimTransformAndTargetReader\t0047afc0\tCGillMHeadAI__UpdateAimTransformAndTargetReader\tOK",
                "005dbcec\t4\t005dbcfc\t0x0047b090\t0047b090\t0047b090\tCGillMHeadAI__UpdateTargetBallisticArcFlags\t0047b090\tCGillMHeadAI__UpdateTargetBallisticArcFlags\tOK",
            ]
        )
        + "\n",
    )
    write(
        pointer_table,
        "\n".join(
            [
                "slot\tentry_addr\tptr\tptr_name\tptr_signature",
                "3\t005e42e4\t0047a900\tCGillMHeadAI__AdvanceOpenAttackCloseState\tint __fastcall CGillMHeadAI__AdvanceOpenAttackCloseState(void * this)",
                "30\t005e4350\t0047a8b0\tCGillMHeadAI__TryTransitionIdleToOpen\tint __fastcall CGillMHeadAI__TryTransitionIdleToOpen(void * this)",
                "63\t005e43d4\t0047a760\tCGillMHead__CreateGillMHeadAIComponent\tvoid __thiscall CGillMHead__CreateGillMHeadAIComponent(void * this, void * init_data)",
            ]
        )
        + "\n",
    )
    write(
        xrefs,
        "\n".join(
            [
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type",
                "004d0ff0\tCPauseMenu__InitPauseSession\t0046fb70\t0046fb00\tCGame__Pause\tUNCONDITIONAL_CALL",
                "004d10b0\tCPauseMenu__DeactivatePauseSession\t0046faf9\t0046fae0\tCGame__UnPause\tUNCONDITIONAL_CALL",
                "004f4560\tSharedUnitAnimation__PlayAnimationByNameIfPresent\t0040a678\t0040a580\tCBattleEngine__Morph\tUNCONDITIONAL_CALL",
                "004f4560\tSharedUnitAnimation__PlayAnimationByNameIfPresent\t0047a8ef\t0047a8b0\tCGillMHeadAI__TryTransitionIdleToOpen\tUNCONDITIONAL_CALL",
                "004f4530\tSharedUnitAnimation__FindAnimationIndexOrZero\t0047a920\t0047a900\tCGillMHeadAI__AdvanceOpenAttackCloseState\tUNCONDITIONAL_CALL",
            ]
        )
        + "\n",
    )
    write(dry_log, "SUMMARY updated=0 skipped=11 renamed=0 would_rename=10 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=11 skipped=0 renamed=10 would_rename=0 missing=0 bad=0\n")

    return argparse.Namespace(
        metadata=metadata,
        tags=tags,
        decompile_dir=decompile_dir,
        vtable_types=vtable_types,
        vtable_slots=vtable_slots,
        pointer_table=pointer_table,
        xrefs=xrefs,
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


def test_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), overclaim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_overclaim_fails()
    print("PASS ghidra_gillmhead_ai_wave390_probe_test: 2/2")
