#!/usr/bin/env python3
"""Tests for the actor/complex-thing signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_actor_complex_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


TARGETS = {
    "0x004011e0": (
        "CActor__Init",
        "void __thiscall CActor__Init(void * this, void * init)",
        "Actor source-parity rename/signature. Sets last-ground/water/object timestamps, copies velocity/old position/orientation from init, delegates to CComplexThing__Init, and schedules first move event. Not runtime proof or concrete class layout.",
    ),
    "0x004013d0": (
        "CActor__dtor_base",
        "void __fastcall CActor__dtor_base(void * this)",
        "Actor destructor-base correction. Resets Actor vtable pointers and delegates to CComplexThing__dtor_base. Not constructor evidence or destructor side-effect completeness proof.",
    ),
    "0x004015c0": (
        "CActor__scalar_deleting_dtor",
        "void * __thiscall CActor__scalar_deleting_dtor(void * this, byte flags)",
        "Actor scalar-deleting destructor. Calls CActor__dtor_base, conditionally frees when flags&1, and returns this. Not allocator ownership proof.",
    ),
    "0x004015e0": (
        "CActor__Move",
        "void __fastcall CActor__Move(void * this)",
        "Actor source-parity rename/signature. Matches CActor::Move-style timestamp, old transform copy, velocity integration, ground/water response, and map-entry update. Not runtime movement claim.",
    ),
    "0x004019b0": (
        "CActor__TeleportOrientation",
        "void __thiscall CActor__TeleportOrientation(void * this, void * orientation)",
        "Actor source-parity rename/signature. Copies orientation into old-orientation storage then delegates to CComplexThing__TeleportOrientation. Not FMatrix layout claim.",
    ),
    "0x004019e0": (
        "CActor__HandleEvent",
        "void __thiscall CActor__HandleEvent(void * this, void * event)",
        "Actor source-parity rename/signature. Handles MOVE 3000 and LF_MOVE 0xbb9, reschedules movement, and delegates other events to CComplexThing__HandleEvent. Not runtime scheduler claim.",
    ),
    "0x004f3ee0": (
        "CComplexThing__scalar_deleting_dtor",
        "void * __thiscall CComplexThing__scalar_deleting_dtor(void * this, byte flags)",
        "ComplexThing scalar-deleting destructor. Calls CComplexThing__dtor_base, conditionally frees when flags&1, and returns this. Not allocator ownership proof.",
    ),
    "0x004f3f00": (
        "CComplexThing__dtor_base",
        "void __fastcall CComplexThing__dtor_base(void * this)",
        "ComplexThing destructor-base correction. Tears down script/animation/motion/mapwho/monitor-owned state and resets base vtables. Not constructor evidence.",
    ),
    "0x004f3fd0": (
        "CComplexThing__Init",
        "void __thiscall CComplexThing__Init(void * this, void * init)",
        "ComplexThing source-parity rename/signature. Sets sound, orientation from init, then delegates to CThing__Init. Not concrete init-struct layout proof.",
    ),
    "0x004f4300": (
        "CComplexThing__HandleEvent",
        "void __thiscall CComplexThing__HandleEvent(void * this, void * event)",
        "ComplexThing source-parity rename/signature. Handles shutdown/init-script/ready-script events and delegates other events. Not runtime script proof.",
    ),
    "0x004f4460": (
        "CComplexThing__TeleportOrientation",
        "void __thiscall CComplexThing__TeleportOrientation(void * this, void * orientation)",
        "ComplexThing source-parity rename/signature. Copies 12 dwords of orientation data into current orientation storage. Not FMatrix layout proof.",
    ),
}


def write_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs_readback.tsv"
    instructions = root / "instructions_readback.tsv"
    decompile.mkdir()

    rename_dry.write_text("--- SUMMARY ---\napplied=0 skipped=11 missing=0 bad=0\n", encoding="utf-8")
    rename_apply.write_text("--- SUMMARY ---\napplied=11 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=11 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=11 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=11 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=11 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    metadata_rows = []
    index_rows = []
    for address, (name, signature, comment) in TARGETS.items():
        if stale_signature and address == "0x004015e0":
            signature = "void __fastcall CActor__Move(int param_1)"
        if overclaim and address == "0x004019e0":
            comment = comment.replace("Not runtime scheduler claim", "Runtime behavior proven")
        metadata_rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name} MOVE 3000 0xbb9 CComplexThing__HandleEvent CComplexThing__Init "
            "CActor__dtor_base OID__FreeObject CComplexThing__dtor_base CThing__Init "
            "CMapWhoEntry__UpdatePosition CEventManager__AddEvent_AtTime DAT_00672fd0 "
            "0xc2c80000 CStaticShadows__SampleShadowHeightBilinear return this "
            "CComplexThing__TeleportOrientation CMapWhoEntry__RemoveFromMap CMonitor__Shutdown "
            "CThing__SetSound CThing__VFunc_09_004f34a0 IScript__CallEvent0AndRegisterNestedListeners "
            "0xc + 0x3c",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "004011e0\tCActor__Init\t004f8b38\t004f86d0\tCUnit__Init\tUNCONDITIONAL_CALL\n"
        + "004019e0\tCActor__HandleEvent\t005d844c\t<none>\t<no_function>\tDATA\n"
        + "004f4300\tCComplexThing__HandleEvent\t004019ff\t004019e0\tCActor__HandleEvent\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x004011e0\t0x004011e0\tTARGET\t0\t0x004013c2\t0x004011e0\tCActor__Init\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004013d0\t0x004013d0\tTARGET\t0\t0x004013d0\t0x004013d0\tCActor__dtor_base\tMOV\tdword ptr [ECX], 0x5d844c\tc7 01 4c 84 5d 00\tFALL_THROUGH\n"
        + "0x004013d0\t0x004013d0\tTARGET\t1\t0x004013dd\t0x004013d0\tCActor__dtor_base\tJMP\t0x004f3f00\te9 1e 2b 0f 00\tUNCONDITIONAL_JUMP\n"
        + "0x004015c0\t0x004015c0\tTARGET\t0\t0x004015dd\t0x004015c0\tCActor__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004015e0\t0x004015e0\tTARGET\t0\t0x0040189c\t0x004015e0\tCActor__Move\tRET\t\tc3\tTERMINATOR\n"
        + "0x004019b0\t0x004019b0\tTARGET\t0\t0x004019c6\t0x004019b0\tCActor__TeleportOrientation\tMOVSD.REP\tES:EDI, ESI\ta5\tFALL_THROUGH\n"
        + "0x004019b0\t0x004019b0\tTARGET\t1\t0x004019d1\t0x004019b0\tCActor__TeleportOrientation\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004019e0\t0x004019e0\tTARGET\t0\t0x00401b4c\t0x004019e0\tCActor__HandleEvent\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004f3ee0\t0x004f3ee0\tTARGET\t0\t0x004f3efd\t0x004f3ee0\tCComplexThing__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004f3f00\t0x004f3f00\tTARGET\t0\t0x004f3fc6\t0x004f3f00\tCComplexThing__dtor_base\tRET\t\tc3\tTERMINATOR\n"
        + "0x004f3fd0\t0x004f3fd0\tTARGET\t0\t0x004f410e\t0x004f3fd0\tCComplexThing__Init\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004f4300\t0x004f4300\tTARGET\t0\t0x004f433e\t0x004f4300\tCComplexThing__HandleEvent\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004f4460\t0x004f4460\tTARGET\t0\t0x004f446e\t0x004f4460\tCComplexThing__TeleportOrientation\tMOVSD.REP\tES:EDI, ESI\ta5\tFALL_THROUGH\n"
        + "0x004f4460\t0x004f4460\tTARGET\t1\t0x004f4472\t0x004f4460\tCComplexThing__TeleportOrientation\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
        encoding="utf-8",
    )
    return {
        "rename_dry": rename_dry,
        "rename_apply": rename_apply,
        "signature_dry": signature_dry,
        "signature_apply": signature_apply,
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class ActorComplexSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_saved_actor_complex_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["renamedTargets"], 11)
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 11)

    def test_fails_for_stale_signature_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_signature=True, overclaim=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
