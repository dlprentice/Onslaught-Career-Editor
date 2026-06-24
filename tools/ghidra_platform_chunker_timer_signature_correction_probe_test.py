#!/usr/bin/env python3
"""Self-tests for the Platform/CFrameTimer/CChunkReader correction probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_platform_chunker_timer_signature_correction_probe.py"

BEFORE_NAMES = {
    "0x00423510": "CCylinder__AcquireNearestTargetReader",
    "0x00423650": "PCPlatform__ReadPerformanceFrequency",
    "0x00423680": "PCPlatform__InitTimerFromPerfCounter",
    "0x00423720": "Platform__UpdateHighResTimerDeltaAndScale",
    "0x004237d0": "CChunker__Create",
    "0x00423840": "CChunkerStream__DestroyOwnedChunkerIfPresent",
    "0x00423870": "CResourceAccumulator__ResetChunkerSlotAndAssignSource",
    "0x004238c0": "CChunkerStream__OpenReadAndGetChunker",
    "0x00423900": "CChunkerStream__CloseDXMemBuffer_Status0OrMinus1",
    "0x00423910": "CMeshPart__ReadHeaderPairAndResetByteCount",
    "0x00423960": "CMeshPart__ReadBlockAndAccumulateByteCount",
    "0x00423990": "CChunkerStream__SkipRemainingChunkBytes",
    "0x004239b0": "CWorld__GetSubstateField_12C",
    "0x004239f0": "CUnitAI__InitDefaults_AutoConfigTestPath",
    "0x005158f0": "Platform__FinalizeAsyncSaveCareer",
    "0x00515950": "PtrFloatAt4__GetOrOne",
    "0x00547d70": "CChunker__CChunker",
    "0x00547d90": "CChunker__Destructor",
    "0x00547ec0": "DXMemBuffer__OpenRead",
    "0x005482d0": "DXMemBuffer__Skip",
    "0x00548570": "DXMemBuffer__ReadBytes",
    "0x00548c00": "DXMemBuffer__Close",
}


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PlatformChunkerTimerSignatureCorrectionProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_final_name: bool = False,
        bad_queue_metric: bool = False,
    ) -> dict[str, Path]:
        probe = load_module()
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        before = root / "metadata_before_final_targets.tsv"
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        queue = root / "static-reaudit-queue.json"

        before_rows = []
        final_rows = []
        index_rows = []
        for address, expected in probe.TARGETS.items():
            before_name = BEFORE_NAMES[address]
            before_rows.append((address, before_name, f"undefined {before_name}(void)", "", "OK"))
            final_name = "CChunker__Create" if stale_final_name and address == "0x004237d0" else expected["name"]
            final_signature = expected["signature"].replace(expected["name"], final_name)
            comment = "; ".join(expected["comment"])
            final_rows.append((address, final_name, final_signature, comment, "OK"))
            index_rows.append((address, final_name, final_signature, "OK"))
            (decompile_dir / f"{address[2:]}_{final_name}.c").write_text(
                f"/* {comment} */\n{final_signature} {{}}\n",
                encoding="utf-8",
            )

        before.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row) for row in before_rows)
            + "\n",
            encoding="utf-8",
        )
        metadata.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row) for row in final_rows)
            + "\n",
            encoding="utf-8",
        )
        index.write_text(
            "address\tname\tsignature\tstatus\n"
            + "\n".join("\t".join(row) for row in index_rows)
            + "\n",
            encoding="utf-8",
        )
        xrefs.write_text(
            "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
            + "\n".join(
                f"{address[2:]}\t{expected['name']}\t005e0000\t<none>\t<no_function>\tDATA"
                for _i in range(49)
                for address, expected in probe.TARGETS.items()
            )
            + "\n",
            encoding="utf-8",
        )
        instructions.write_text(
            "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
            + "\n".join(
                f"{address}\t{address}\tTARGET\t{i}\t{address}\t{address}\t{expected['name']}\tMOV\tEAX, EAX\t00\tFALL_THROUGH"
                for i in range(49)
                for address, expected in probe.TARGETS.items()
            )
            + "\n",
            encoding="utf-8",
        )
        queue.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "totalFunctions": 5876,
                    "qualitySignals": {
                        "commentlessFunctionCount": 5172 if bad_queue_metric else 5171,
                        "undefinedSignatureCount": 2023,
                        "paramSignatureCount": 2319,
                        "uncertainOwnerNameCount": 0,
                        "helperAddressNameCount": 0,
                        "wrapperAddressNameCount": 0,
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "metadata_before_path": before,
            "metadata_final_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "queue_json_path": queue,
        }

    def test_accepts_platform_chunker_timer_readback(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp))
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["signatureCorrectedTargets"], 22)
        self.assertEqual(report["renamedTargets"], 20)
        self.assertEqual(report["queueCommentlessFunctions"], 5171)

    def test_rejects_stale_final_name(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), stale_final_name=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("CChunker__Create" in failure for failure in report["failures"]))

    def test_rejects_queue_metric_drift(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), bad_queue_metric=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("commentlessFunctionCount" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
