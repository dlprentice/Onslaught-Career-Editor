import csv
from collections import Counter
import json
import tempfile
import unittest
from pathlib import Path

import ghidra_reviewed_correction_plan as plan


class ReviewedCorrectionPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_json(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def write_decisions(self, rows: list[dict]) -> Path:
        path = self.root / "decisions.jsonl"
        path.write_text(
            "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows),
            encoding="utf-8",
        )
        return path

    def write_snapshot(self, rows: list[dict], name: str = "snapshot.tsv") -> Path:
        path = self.root / name
        fields = ["address", "name", "signature", "comment", "status", "prototype_key"]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow({**row, "status": "OK"})
        return path

    @staticmethod
    def verify_fixture(public: Path, post: Path, expected_snapshot_count: int = 3) -> dict:
        return plan._verify_post_state_data(
            json.loads(public.read_text(encoding="utf-8")),
            plan.load_snapshot(post),
            expected_snapshot_count=expected_snapshot_count,
        )

    @staticmethod
    def cursor_record(address: str, current: str, corrected: str) -> dict:
        return {
            "address": address,
            "changeClass": "comment-only",
            "correctedComment": corrected,
            "correctedFields": ["comment"],
            "correctedName": "Function_" + address[-2:],
            "currentComment": current,
            "currentName": "Function_" + address[-2:],
            "docFindings": [],
            "evidence": ["final-decompile"],
            "rationale": "Original manifest rationale.",
        }

    @staticmethod
    def targeted_comment_record(address: str, current: str, corrected: str, supersedes: bool = False) -> dict:
        row = {
            "address": address,
            "correctedComment": corrected,
            "correctedFields": ["comment"],
            "correctedName": "Function_" + address[-2:],
            "currentName": "Function_" + address[-2:],
            "currentPrototypeKey": "proto-comment",
            "currentSignature": "void Function(void)",
            "docFindings": [],
            "evidence": ["final-instructions"],
            "phase": "recovered-conflicts",
            "rationale": "Targeted manifest rationale.",
            "signatureChangeClass": None,
        }
        if supersedes:
            row["supersedesCursorDeltaRecord"] = True
        return row

    @staticmethod
    def structured_record(address: str) -> dict:
        return {
            "address": address,
            "confidence": "high-static",
            "correctedComment": "Correct structured comment.",
            "correctedFields": ["signature", "comment"],
            "correctedName": "StructuredFunction",
            "correctedSignature": "bool __thiscall StructuredFunction(void * this, int value)",
            "currentName": "StructuredFunction",
            "currentPrototypeKey": "proto-before",
            "currentSignature": "bool __thiscall StructuredFunction(void * this)",
            "docFindings": [],
            "evidence": ["final-instructions"],
            "phase": "runtime-critical",
            "rationale": "Structured manifest rationale.",
            "signatureChangeClass": "structured-prototype-change",
            "sourceAlignment": "partial",
        }

    def fixture(self) -> tuple[Path, Path, Path, Path]:
        cursor = self.write_json(
            "cursor.json",
            {
                "schemaVersion": "onslaught-ghidra-full-reaudit-corrections.v1",
                "recordCount": 2,
                "prototypeOrBoundaryMutationAuthorized": False,
                "records": [
                    self.cursor_record("0x00400010", "Old A", "New A"),
                    self.cursor_record("0x00400020", "Old overlap", "Wrong overlap"),
                ],
            },
        )
        targeted = self.write_json(
            "targeted.json",
            {
                "schemaVersion": "onslaught-ghidra-targeted-revalidation-corrections.v2",
                "recordCount": 2,
                "prototypeOrBoundaryMutationAuthorized": False,
                "supersedingCursorDeltaOverlapAddresses": ["0x00400020"],
                "supersedingCursorDeltaOverlapCount": 1,
                "records": [
                    self.targeted_comment_record("0x00400020", "Old overlap", "New overlap", True),
                    self.structured_record("0x0050b9c0"),
                ],
            },
        )
        decisions = self.write_decisions(
            [
                {
                    "address": "0x00400010",
                    "classification": "confirmed-apply",
                    "rationale": "Fresh body confirms A.",
                    "freshEvidence": ["live-decompile", "live-instructions"],
                },
                {
                    "address": "0x00400020",
                    "classification": "disputed-needs-research",
                    "rationale": "Fresh body does not settle overlap.",
                    "freshEvidence": ["live-decompile"],
                },
                {
                    "address": "0x0050b9c0",
                    "classification": "confirmed-apply",
                    "rationale": "RET and stack reads confirm the prototype.",
                    "freshEvidence": ["live-decompile", "live-instructions"],
                    "expectedCorrectedPrototypeKey": "proto-after",
                },
            ]
        )
        snapshot = self.write_snapshot(
            [
                {
                    "address": "0x00400010",
                    "name": "Function_10",
                    "signature": "void Function(void)",
                    "comment": "Old A",
                    "prototype_key": "proto-comment",
                },
                {
                    "address": "0x00400020",
                    "name": "Function_20",
                    "signature": "void Function(void)",
                    "comment": "Old overlap",
                    "prototype_key": "proto-comment",
                },
                {
                    "address": "0x0050b9c0",
                    "name": "StructuredFunction",
                    "signature": "bool __thiscall StructuredFunction(void * this)",
                    "comment": "Old structured comment.",
                    "prototype_key": "proto-before",
                },
            ]
        )
        return cursor, targeted, decisions, snapshot

    def build(self) -> tuple[dict, Path, Path]:
        cursor, targeted, decisions, snapshot = self.fixture()
        public = self.root / "public.json"
        apply_tsv = self.root / "apply.tsv"
        result = plan.build_plan(cursor, targeted, decisions, snapshot, public, apply_tsv)
        return result, public, apply_tsv

    def test_builds_exact_classification_manifest_and_confirmed_only_apply_plan(self) -> None:
        result, public, apply_tsv = self.build()

        self.assertEqual(3, result["reviewedAddressCount"])
        self.assertEqual(
            {"confirmed-apply": 2, "disputed-needs-research": 1},
            result["classificationCounts"],
        )
        self.assertEqual(2, result["applyRecordCount"])
        self.assertEqual(result, json.loads(public.read_text(encoding="utf-8")))
        with apply_tsv.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(["0x00400010", "0x0050b9c0"], [row["address"] for row in rows])
        self.assertTrue(all(row["classification"] == "confirmed-apply" for row in rows))
        self.assertEqual("proto-after", rows[1]["expected_corrected_prototype_key"])
        self.assertEqual(result["applyPlanSha256"], plan.sha256_file(apply_tsv))

    def test_targeted_superseding_record_wins_independent_of_source_order(self) -> None:
        result, _, _ = self.build()
        overlap = next(row for row in result["records"] if row["address"] == "0x00400020")
        self.assertEqual("targeted", overlap["sourceManifest"])
        self.assertEqual("New overlap", overlap["correctedComment"])

    def test_rejects_duplicate_decisions(self) -> None:
        cursor, targeted, decisions, snapshot = self.fixture()
        rows = [json.loads(line) for line in decisions.read_text(encoding="utf-8").splitlines()]
        decisions.write_text(json.dumps(rows[0]) + "\n" + json.dumps(rows[0]) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate decision address"):
            plan.build_plan(cursor, targeted, decisions, snapshot, self.root / "out.json", self.root / "out.tsv")

    def test_rejects_missing_decision(self) -> None:
        cursor, targeted, decisions, snapshot = self.fixture()
        rows = [json.loads(line) for line in decisions.read_text(encoding="utf-8").splitlines()]
        decisions.write_text("".join(json.dumps(row) + "\n" for row in rows[:-1]), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "decision addresses"):
            plan.build_plan(cursor, targeted, decisions, snapshot, self.root / "out.json", self.root / "out.tsv")

    def test_rejects_live_precondition_mismatch(self) -> None:
        cursor, targeted, decisions, snapshot = self.fixture()
        text = snapshot.read_text(encoding="utf-8").replace("Old A", "Drifted A")
        snapshot.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "live precondition mismatch.*0x00400010.*comment"):
            plan.build_plan(cursor, targeted, decisions, snapshot, self.root / "out.json", self.root / "out.tsv")

    def test_rejects_unmarked_overlap(self) -> None:
        cursor, targeted, decisions, snapshot = self.fixture()
        data = json.loads(targeted.read_text(encoding="utf-8"))
        data["records"][0].pop("supersedesCursorDeltaRecord")
        targeted.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate correction address"):
            plan.build_plan(cursor, targeted, decisions, snapshot, self.root / "out.json", self.root / "out.tsv")

    def test_rejects_unexpected_source_schema_or_embedded_mutation_authority(self) -> None:
        cursor, targeted, decisions, snapshot = self.fixture()
        cursor_data = json.loads(cursor.read_text(encoding="utf-8"))
        cursor_data["schemaVersion"] = "unexpected.cursor.schema"
        cursor.write_text(json.dumps(cursor_data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unexpected manifest schema"):
            plan.build_plan(
                cursor,
                targeted,
                decisions,
                snapshot,
                self.root / "out.json",
                self.root / "out.tsv",
            )

        cursor_data["schemaVersion"] = "onslaught-ghidra-full-reaudit-corrections.v1"
        cursor.write_text(json.dumps(cursor_data), encoding="utf-8")
        targeted_data = json.loads(targeted.read_text(encoding="utf-8"))
        targeted_data["prototypeOrBoundaryMutationAuthorized"] = True
        targeted.write_text(json.dumps(targeted_data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "must not authorize prototype or boundary mutation"):
            plan.build_plan(
                cursor,
                targeted,
                decisions,
                snapshot,
                self.root / "out.json",
                self.root / "out.tsv",
            )

    def test_rejects_confirmed_structured_signature_without_expected_prototype_key(self) -> None:
        cursor, targeted, decisions, snapshot = self.fixture()
        rows = [json.loads(line) for line in decisions.read_text(encoding="utf-8").splitlines()]
        rows[2].pop("expectedCorrectedPrototypeKey")
        decisions.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "expectedCorrectedPrototypeKey"):
            plan.build_plan(cursor, targeted, decisions, snapshot, self.root / "out.json", self.root / "out.tsv")

    def test_rejects_structured_signature_outside_leased_address(self) -> None:
        cursor, targeted, decisions, snapshot = self.fixture()
        targeted.write_text(
            targeted.read_text(encoding="utf-8").replace("0x0050b9c0", "0x00400030"),
            encoding="utf-8",
        )
        decisions.write_text(
            decisions.read_text(encoding="utf-8").replace("0x0050b9c0", "0x00400030"),
            encoding="utf-8",
        )
        snapshot.write_text(
            snapshot.read_text(encoding="utf-8").replace("0x0050b9c0", "0x00400030"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "structured signature address is not leased"):
            plan.build_plan(
                cursor,
                targeted,
                decisions,
                snapshot,
                self.root / "out.json",
                self.root / "out.tsv",
            )

    def test_escape_unescape_round_trip_preserves_literal_escape_sequences(self) -> None:
        value = "literal \\t \\n \\r \\\\ plus\tactual\ncontrols\r"
        self.assertEqual(value, plan.unescape(plan.escape(value)))

    def test_verify_post_state_rejects_empty_unknown_duplicate_and_counter_drift(self) -> None:
        result, public, _ = self.build()
        post = self.write_snapshot([], "empty-post.tsv")

        public.write_text(
            json.dumps({"schemaVersion": "onslaught-ghidra-reviewed-correction-plan.v1"}),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "non-empty records"):
            self.verify_fixture(public, post)

        public.write_text(json.dumps(result), encoding="utf-8")
        unknown = json.loads(public.read_text(encoding="utf-8"))
        unknown["records"][0]["classification"] = "invented-classification"
        public.write_text(json.dumps(unknown), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid classification"):
            self.verify_fixture(public, post)

        duplicate = json.loads(json.dumps(result))
        duplicate["records"].append(dict(duplicate["records"][0]))
        duplicate["reviewedAddressCount"] += 1
        public.write_text(json.dumps(duplicate), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate reviewed address"):
            self.verify_fixture(public, post)

        drifted = json.loads(json.dumps(result))
        drifted["applyRecordCount"] = 1
        public.write_text(json.dumps(drifted), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "applyRecordCount mismatch"):
            self.verify_fixture(public, post)

    def test_verify_reenforces_signature_lease_and_rendering_only_prototype_key(self) -> None:
        result, public, _ = self.build()
        post = self.write_snapshot([], "post.tsv")

        escaped = json.loads(json.dumps(result))
        escaped_record = escaped["records"][0]
        escaped_record["correctedFields"].append("signature")
        escaped_record["signatureChangeClass"] = "structured-prototype-change"
        public.write_text(json.dumps(escaped), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "structured signature address is not leased"):
            self.verify_fixture(public, post)

        rendering = json.loads(json.dumps(result))
        rendering_record = rendering["records"][0]
        rendering_record["correctedFields"].append("signature")
        rendering_record["signatureChangeClass"] = "name-and-parameter-rendering-only"
        rendering_record["expectedCorrectedPrototypeKey"] = "different-prototype"
        public.write_text(json.dumps(rendering), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "rendering-only signature changes prototype key"):
            self.verify_fixture(public, post)

    def test_dedicated_verify_rejects_substituted_plan_and_fixture_checks_full_count(self) -> None:
        _, public, _ = self.build()
        post = self.write_snapshot([], "post.tsv")

        with self.assertRaisesRegex(ValueError, "reviewed plan SHA-256 mismatch"):
            plan.verify_post_state(public, post)
        with self.assertRaisesRegex(ValueError, "snapshot address count mismatch"):
            self.verify_fixture(public, post, expected_snapshot_count=6411)

    def test_verify_post_state_requires_confirmed_after_and_nonconfirmed_before(self) -> None:
        result, public, _ = self.build()
        post = self.write_snapshot(
            [
                {
                    "address": "0x00400010",
                    "name": "Function_10",
                    "signature": "void Function(void)",
                    "comment": "New A",
                    "prototype_key": "proto-comment",
                },
                {
                    "address": "0x00400020",
                    "name": "Function_20",
                    "signature": "void Function(void)",
                    "comment": "Old overlap",
                    "prototype_key": "proto-comment",
                },
                {
                    "address": "0x0050b9c0",
                    "name": "StructuredFunction",
                    "signature": "bool __thiscall StructuredFunction(void * this, int value)",
                    "comment": "Correct structured comment.",
                    "prototype_key": "proto-after",
                },
            ],
            "post.tsv",
        )
        verified = self.verify_fixture(public, post)
        self.assertEqual(3, verified["verifiedAddressCount"])
        self.assertEqual(2, verified["confirmedAppliedCount"])
        self.assertEqual(1, verified["nonAppliedUnchangedCount"])
        self.assertEqual([], verified["mismatches"])

        post.write_text(post.read_text(encoding="utf-8").replace("New A", "Wrong A"), encoding="utf-8")
        failed = self.verify_fixture(public, post)
        self.assertEqual(1, len(failed["mismatches"]))
        self.assertEqual("0x00400010", failed["mismatches"][0]["address"])

    def test_verify_rejected_row_must_remain_at_before_state(self) -> None:
        result, public, _ = self.build()
        rejected = json.loads(json.dumps(result))
        rejected["records"][1]["classification"] = "rejected-manifest-error"
        rejected["classificationCounts"] = {
            "confirmed-apply": 2,
            "rejected-manifest-error": 1,
        }
        public.write_text(json.dumps(rejected), encoding="utf-8")
        post = self.write_snapshot(
            [
                {
                    "address": "0x00400010",
                    "name": "Function_10",
                    "signature": "void Function(void)",
                    "comment": "New A",
                    "prototype_key": "proto-comment",
                },
                {
                    "address": "0x00400020",
                    "name": "Function_20",
                    "signature": "void Function(void)",
                    "comment": "Mutated rejected row",
                    "prototype_key": "proto-comment",
                },
                {
                    "address": "0x0050b9c0",
                    "name": "StructuredFunction",
                    "signature": "bool __thiscall StructuredFunction(void * this, int value)",
                    "comment": "Correct structured comment.",
                    "prototype_key": "proto-after",
                },
            ],
            "rejected-post.tsv",
        )

        failed = self.verify_fixture(public, post)

        self.assertEqual(1, len(failed["mismatches"]))
        self.assertEqual("0x00400020", failed["mismatches"][0]["address"])
        self.assertEqual("comment", failed["mismatches"][0]["field"])

    def test_apply_plan_contract_rejects_substitution_and_malformed_rows(self) -> None:
        _, _, apply_tsv = self.build()

        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            plan.validate_apply_plan(
                apply_tsv,
                expected_sha256="0" * 64,
                expected_count=2,
            )

        original = apply_tsv.read_text(encoding="utf-8")

        def reject(mutated: str, pattern: str, count: int = 2) -> None:
            apply_tsv.write_text(mutated, encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(ValueError, pattern):
                plan.validate_apply_plan(
                    apply_tsv,
                    expected_sha256=plan.sha256_file(apply_tsv),
                    expected_count=count,
                )
            apply_tsv.write_text(original, encoding="utf-8", newline="\n")

        reject(original.replace("confirmed-apply", "rejected-manifest-error", 1), "non-confirmed")
        reject(original, "row count mismatch", count=3)
        rows = original.splitlines()
        reject(original.replace("address\tclassification", "addr\tclassification", 1), "header mismatch")
        reject("\n".join([rows[0], rows[1], rows[1], rows[2]]) + "\n", "duplicate")
        reject("\n".join([rows[0], "", rows[1], rows[2]]) + "\n", "blank apply-plan row")
        reject("\n".join([rows[0], rows[1] + "\textra", rows[2]]) + "\n", "column count")
        reject(original.replace("0x0050b9c0", "0x00400030"), "structured apply-plan address is not leased")
        reject(original.replace("0x00400010", "0x004dac90"), "rejected manifest address")
        rendering_row = rows[1].split("\t")
        rendering_row[2] = "comment,signature"
        rendering_row[10] = "name-and-parameter-rendering-only"
        rendering_row[11] = "different-prototype"
        reject(
            "\n".join([rows[0], "\t".join(rendering_row), rows[2]]) + "\n",
            "rendering-only apply-plan row changes prototype key",
        )

    def test_real_reviewed_artifacts_are_locked_to_the_accepted_91_of_92_set(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        analysis = repo / "reverse-engineering" / "binary-analysis"
        decisions_path = analysis / "ghidra-reviewed-correction-decisions-2026-07-13.jsonl"
        public_plan_path = analysis / "ghidra-reviewed-correction-plan-2026-07-13.json"
        cursor_manifest = analysis / "ghidra-full-reaudit-corrections-2026-07-13.json"
        targeted_manifest = analysis / "ghidra-targeted-revalidation-corrections-2026-07-13.json"

        decisions = [
            json.loads(line)
            for line in decisions_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        public_plan = json.loads(public_plan_path.read_text(encoding="utf-8"))
        records = public_plan["records"]
        self.assertEqual(records, plan.validate_reviewed_plan_manifest(public_plan))

        self.assertEqual(
            "312ee274791c4d9a0167305846f482a12cd8f153adc44ee7f7f27279cc48c8ce",
            plan.sha256_file(public_plan_path),
        )
        self.assertEqual(
            "cff10b8ab16a8b8c5169c9c47fc9435b29a4b8ac8bf2159785125b292be9e84e",
            plan.sha256_file(decisions_path),
        )

        decision_addresses = [row["address"] for row in decisions]
        record_addresses = [row["address"] for row in records]
        self.assertEqual(92, len(decision_addresses))
        self.assertEqual(92, len(set(decision_addresses)))
        self.assertEqual(set(decision_addresses), set(record_addresses))
        self.assertEqual(
            Counter({"confirmed-apply": 91, "rejected-manifest-error": 1}),
            Counter(row["classification"] for row in decisions),
        )
        self.assertEqual(
            {"confirmed-apply": 91, "rejected-manifest-error": 1},
            public_plan["classificationCounts"],
        )
        self.assertEqual(91, public_plan["applyRecordCount"])
        self.assertEqual(
            "a2a5f4210f060d1ce1ecc8f7d11ef041954b7c6951860b3026a32dd857bf2148",
            public_plan["applyPlanSha256"],
        )
        self.assertEqual(92, plan.EXPECTED_REVIEWED_ADDRESS_COUNT)
        self.assertEqual(91, plan.EXPECTED_APPLY_RECORD_COUNT)
        self.assertEqual(6411, plan.EXPECTED_POST_SNAPSHOT_COUNT)

        truncated_post = self.write_snapshot([], "truncated-real-post.tsv")
        with self.assertRaisesRegex(ValueError, "snapshot address count mismatch"):
            plan.verify_post_state(public_plan_path, truncated_post)

        confirmed = [row for row in records if row["classification"] == "confirmed-apply"]
        fields = Counter(field for row in confirmed for field in row["correctedFields"])
        self.assertEqual(Counter({"comment": 88, "name": 26, "signature": 9}), fields)
        signature_classes = Counter(
            row["signatureChangeClass"]
            for row in confirmed
            if "signature" in row["correctedFields"]
        )
        self.assertEqual(
            Counter({"name-and-parameter-rendering-only": 8, "structured-prototype-change": 1}),
            signature_classes,
        )
        structured = [
            row
            for row in confirmed
            if row.get("signatureChangeClass") == "structured-prototype-change"
        ]
        self.assertEqual(["0x0050b9c0"], [row["address"] for row in structured])
        rejected = [row for row in records if row["classification"] == "rejected-manifest-error"]
        self.assertEqual(["0x004dac90"], [row["address"] for row in rejected])

        source_manifests = public_plan["sourceManifestSha256"]
        self.assertEqual(plan.sha256_file(cursor_manifest), source_manifests["cursor"])
        self.assertEqual(plan.sha256_file(targeted_manifest), source_manifests["targeted"])


if __name__ == "__main__":
    unittest.main()
