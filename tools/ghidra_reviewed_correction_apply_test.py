import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "GhidraApplyReviewedCorrections.java"


class ReviewedCorrectionApplyScriptTests(unittest.TestCase):
    def source(self) -> str:
        self.assertTrue(SCRIPT.is_file(), "reviewed-correction Ghidra script must exist")
        return SCRIPT.read_text(encoding="utf-8")

    def test_hash_binds_plan_and_rejects_nonconfirmed_rows(self) -> None:
        source = self.source()
        for token in (
            "MessageDigest.getInstance(\"SHA-256\")",
            "EXPECTED_APPLY_PLAN_SHA256",
            "a2a5f4210f060d1ce1ecc8f7d11ef041954b7c6951860b3026a32dd857bf2148",
            "PLAN_HASH_OK",
            "confirmed-apply",
            "duplicate address",
        ):
            self.assertIn(token, source)

    def test_binds_program_identity_and_exact_reviewed_target_count(self) -> None:
        source = self.source()
        for token in (
            "EXPECTED_PROGRAM_NAME",
            "BEA.exe",
            "EXPECTED_PROGRAM_MD5",
            "3b456964020070efe696d2cc09464a55",
            "currentProgram.getExecutableMD5()",
            "EXPECTED_TARGET_COUNT",
            "91",
            "PROGRAM_ID_OK",
        ):
            self.assertIn(token, source)

    def test_preflights_every_row_before_first_mutation(self) -> None:
        source = self.source()
        preflight = source.index("preflightAll(targets)")
        mutation = source.index("applyTarget(target)", preflight)
        self.assertLess(preflight, mutation)
        self.assertIn("PREFLIGHT_OK", source)

    def test_serializes_transactions_and_reads_back_each_field(self) -> None:
        source = self.source()
        for token in (
            "startTransaction",
            "endTransaction(transactionId, commit)",
            "READBACK_FIELD_OK",
            "READBACK_ROW_OK",
            "APPLY_ABORT",
        ):
            self.assertIn(token, source)

    def test_only_allows_rendering_signatures_and_the_leased_world_prototype(self) -> None:
        source = self.source()
        for token in (
            "name-and-parameter-rendering-only",
            "structured-prototype-change",
            "0x0050b9c0",
            "DYNAMIC_STORAGE_ALL_PARAMS",
            "new ParameterImpl(\"mem_buffer\"",
            "new ParameterImpl(\"is_base_world\"",
            "new ParameterImpl(\"initialize_world_state\"",
        ):
            self.assertIn(token, source)

    def test_does_not_enumerate_or_mutate_outside_plan_addresses(self) -> None:
        source = self.source()
        self.assertNotIn("getFunctions(", source)
        self.assertNotIn("getFunctionIterator", source)
        self.assertIn("functionAtEntry(target.address)", source)


if __name__ == "__main__":
    unittest.main()
