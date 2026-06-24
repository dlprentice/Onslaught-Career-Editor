#!/usr/bin/env python3
"""Self-tests for the ComponentBasedOn copy helper signature probe."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_component_based_copy_signature_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ComponentBasedCopySignatureProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_signature: bool = False,
        missing_comment: bool = False,
        missing_tag: bool = False,
        missing_xref: bool = False,
        missing_instruction_token: bool = False,
        missing_decompile_token: bool = False,
    ) -> dict[str, Path]:
        probe = load_module()
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        tags = root / "tags_final.tsv"

        expected = probe.TARGET
        signature = " ".join(expected["signature"])
        if stale_signature:
            signature = "void __thiscall CComponentBasedOn__CopyFrom(void * this, int param_1, int param_2)"
        comment = "; ".join(expected["comment"])
        if missing_comment:
            comment = "short stale comment"
        metadata.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            f"{probe.ADDRESS}\t{expected['name']}\t{signature}\t{comment}\tOK\n",
            encoding="utf-8",
        )
        index.write_text(
            "address\tname\tsignature\tstatus\n"
            f"{probe.ADDRESS}\t{expected['name']}\t{signature}\tOK\n",
            encoding="utf-8",
        )
        decompile_tokens = list(probe.DECOMPILE_TOKENS)
        if missing_decompile_token:
            decompile_tokens = decompile_tokens[:-1]
        (decompile_dir / f"{probe.ADDRESS[2:]}_{expected['name']}.c").write_text(
            f"/* fixture */\nvoid __thiscall {expected['name']}(void *this, void *sourceComponent) {{\n  "
            + ";\n  ".join(decompile_tokens)
            + ";\n}\n",
            encoding="utf-8",
        )

        xref_rows = list(probe.EXPECTED_XREFS)
        if missing_xref:
            xref_rows = [probe.EXPECTED_XREFS[1]]
        while len(xref_rows) < probe.MIN_XREF_ROWS:
            next_caller = probe.EXPECTED_XREFS[len(xref_rows) % len(probe.EXPECTED_XREFS)]
            xref_rows.append(probe.EXPECTED_XREFS[1] if missing_xref else next_caller)
        xrefs.write_text(
            "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
            + "\n".join(
                f"{probe.ADDRESS}\t{expected['name']}\t{probe.ADDRESS}\t{probe.ADDRESS}\t{caller}\tUNCONDITIONAL_CALL"
                for caller in xref_rows
            )
            + "\n",
            encoding="utf-8",
        )

        instruction_tokens = list(probe.INSTRUCTION_TOKENS)
        if missing_instruction_token:
            instruction_tokens = instruction_tokens[1:]
        instructions.write_text(
            "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
            + "\n".join(
                f"{probe.ADDRESS}\t{probe.ADDRESS}\tTARGET\t{idx}\t{probe.ADDRESS}\t{probe.ADDRESS}\t{expected['name']}\tMOV\t{token}\t90\tFALL_THROUGH"
                for idx, token in enumerate(instruction_tokens)
            )
            + "\n",
            encoding="utf-8",
        )

        final_tags = list(expected["tags"])
        if missing_tag:
            final_tags = final_tags[1:]
        tags.write_text(
            "address\tname\ttags\tstatus\n"
            f"{probe.ADDRESS}\t{expected['name']}\t{';'.join(final_tags)}\tOK\n",
            encoding="utf-8",
        )
        return {
            "metadata_final_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "tags_path": tags,
        }

    def test_accepts_component_based_copy_fixture(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["target"]["address"], probe.ADDRESS)

    def test_rejects_stale_signature_missing_comment_and_tag(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(
                **self.write_fixture(Path(tmp), stale_signature=True, missing_comment=True, missing_tag=True)
            )
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature token missing" in failure for failure in report["failures"]))
        self.assertTrue(any("comment token missing" in failure for failure in report["failures"]))
        self.assertTrue(any("tag missing" in failure for failure in report["failures"]))

    def test_rejects_missing_xref_instruction_and_decompile_tokens(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(
                **self.write_fixture(
                    Path(tmp),
                    missing_xref=True,
                    missing_instruction_token=True,
                    missing_decompile_token=True,
                )
            )
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("expected xref missing" in failure for failure in report["failures"]))
        self.assertTrue(any("instruction token missing" in failure for failure in report["failures"]))
        self.assertTrue(any("decompile token missing" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
