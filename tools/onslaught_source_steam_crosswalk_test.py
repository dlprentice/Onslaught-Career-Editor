#!/usr/bin/env python3
"""Focused normal and adversarial tests for the source/Steam crosswalk."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import subprocess
import tempfile
import unittest
import zlib
from shutil import copyfile
from pathlib import Path

import onslaught_source_steam_crosswalk as crosswalk


PIN = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"


def layer(status: str, **values: object) -> dict[str, object]:
    return {"status": status, **values}


def evidence(token: str, file: str = "reverse-engineering/binary-analysis/static.md") -> dict[str, object]:
    return {
        "file": file,
        "lineStart": 1,
        "lineEnd": 1,
        "requiredTokens": [token],
    }


def row(
    row_id: str,
    *,
    source_status: str = "hypothesis-only",
    steam_status: str = "accepted-bounded-static",
    runtime_status: str = "required-not-measured",
    dependencies: list[str] | None = None,
) -> dict[str, object]:
    address = 0x00400000 + (zlib.crc32(row_id.encode("utf-8")) % 0x100000)
    if runtime_status == "required-not-measured":
        runtime = layer(runtime_status, evidence=[])
    elif runtime_status == "accepted-input-state-handoff-only":
        runtime = layer(
            runtime_status,
            measurementClass="input-state-handoff",
            evidence=[evidence(f"STEAM_{row_id}")],
        )
    else:
        runtime = layer(
            runtime_status,
            measurementClass="scalar-behavior",
            evidence=[evidence(f"STEAM_{row_id}")],
        )
    dependencies = dependencies or []
    return {
        "id": row_id,
        "claim": "bounded test claim",
        "claimClass": "test-static-claim",
        "sourceHypothesis": layer(
            source_status,
            file="references/Onslaught/Test.cpp",
            symbol=f"Source::{row_id}",
            lineStart=1,
            lineEnd=3,
            requiredTokens=[f"TOKEN_{row_id}"],
        ),
        "steamStatic": layer(
            steam_status,
            address=f"0x{address:08x}",
            symbol=f"Steam__{row_id}",
            evidence=[evidence(f"STEAM_{row_id}")],
        ),
        "archiveObservation": layer("not-applicable", evidence=[]),
        "copiedRuntimeMeasurement": runtime,
        "rebuildContract": layer("blocked-until-runtime-accepted", evidence=[]),
        "requirements": copy.deepcopy(crosswalk.REQUIREMENTS),
        "dependencies": dependencies,
        "requiredDependencies": list(dependencies),
        "declaredReadiness": {
            "staticCrosswalkReady": True,
            "runtimeMeasurementReady": False,
            "rebuildContractReady": False,
            "identityReady": False,
        },
        "nonclaims": ["No runtime or rebuild behavior is established."],
    }


def document(rows: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "schemaVersion": crosswalk.SCHEMA_VERSION,
        "sourceRevision": PIN,
        "evidenceLayers": list(crosswalk.EVIDENCE_LAYERS),
        "rows": rows or [row("alpha")],
    }


class FixtureRepo:
    def __init__(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)
        source = self.root / "references" / "Onslaught" / "Test.cpp"
        source.parent.mkdir(parents=True)
        source.write_text(
            "\n".join(
                [
                    "TOKEN_alpha TOKEN_beta TOKEN_gamma",
                    "TOKEN_resource TOKEN_walker",
                    "source fixture end",
                ]
            ),
            encoding="utf-8",
        )
        static = self.root / "reverse-engineering" / "binary-analysis" / "static.md"
        static.parent.mkdir(parents=True)
        static.write_text(
            " ".join(
                [
                    "STEAM_alpha",
                    "STEAM_beta",
                    "STEAM_gamma",
                    "STEAM_resource",
                    "STEAM_walker",
                ]
            ),
            encoding="utf-8",
        )
        rebuild = self.root / "rebuild" / "contract.md"
        rebuild.parent.mkdir(parents=True)
        rebuild.write_text("REBUILD_alpha", encoding="utf-8")

    def close(self) -> None:
        self._temp.cleanup()


class CrosswalkValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = FixtureRepo()

    def tearDown(self) -> None:
        self.repo.close()

    def validate(self, value: object) -> dict[str, object]:
        return crosswalk._validate_test_document(value, self.repo.root)

    def assert_invalid(self, value: object, message: str) -> None:
        with self.assertRaisesRegex(crosswalk.CrosswalkValidationError, message):
            self.validate(value)

    def test_valid_row_computes_static_only_readiness(self) -> None:
        report = self.validate(document())
        self.assertEqual("pass", report["status"])
        self.assertEqual(
            {
                "staticCrosswalkReady": True,
                "runtimeMeasurementReady": False,
                "rebuildContractReady": False,
                "identityReady": False,
            },
            report["rows"][0]["computedReadiness"],
        )

    def test_coordinated_document_pin_drift_fails_closed(self) -> None:
        value = document()
        value["sourceRevision"] = "0" * 40
        self.assert_invalid(value, "source revision mismatch")

    def test_non_git_source_root_revision_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError, "source revision is unavailable"
        ):
            crosswalk._git_revision(self.repo.root / "references" / "Onslaught")

    def test_dirty_tracked_source_root_revision_fails_closed(self) -> None:
        source_root = self.repo.root / "references" / "Onslaught"
        for command in (
            ["git", "init", "--quiet"],
            ["git", "config", "user.email", "fixture@example.invalid"],
            ["git", "config", "user.name", "Fixture"],
            ["git", "add", "Test.cpp"],
            ["git", "commit", "--quiet", "-m", "fixture"],
        ):
            subprocess.run(command, cwd=source_root, check=True)
        with (source_root / "Test.cpp").open("a", encoding="utf-8") as stream:
            stream.write("\nDIRTY_TRACKED_SOURCE")
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError,
            "source working tree is not clean",
        ):
            crosswalk._git_revision(source_root)

    def test_malformed_root_fails_cleanly(self) -> None:
        self.assert_invalid([], "document root must be an object")

    def test_absent_source_file_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["sourceHypothesis"]["file"] = "references/Onslaught/Missing.cpp"
        self.assert_invalid(value, "source file is absent")

    def test_missing_source_token_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["sourceHypothesis"]["requiredTokens"] = ["NOT_PRESENT"]
        self.assert_invalid(value, "source token is absent")

    def test_invalid_source_range_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["sourceHypothesis"]["lineStart"] = 4
        self.assert_invalid(value, "source range")

    def test_boolean_source_range_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["sourceHypothesis"]["lineStart"] = True
        self.assert_invalid(value, "lineStart must be an integer")

    def test_missing_steam_address_fails_closed(self) -> None:
        value = document()
        del value["rows"][0]["steamStatic"]["address"]
        self.assert_invalid(value, "Steam address")

    def test_missing_static_evidence_token_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["steamStatic"]["evidence"][0]["requiredTokens"] = ["MISSING"]
        self.assert_invalid(value, "steamStatic evidence token is absent")

    def test_unbounded_static_evidence_fails_closed(self) -> None:
        value = document()
        del value["rows"][0]["steamStatic"]["evidence"][0]["lineStart"]
        self.assert_invalid(value, "unknown field|lineStart")

    def test_crosswalk_cannot_self_attest_steam_evidence(self) -> None:
        value = document()
        value["rows"][0]["steamStatic"]["evidence"][0]["file"] = (
            "reverse-engineering/source-code/onslaught-source-steam-crosswalk.v1.json"
        )
        self.assert_invalid(value, "unsupported evidence path")

    def test_steam_evidence_cannot_traverse_out_of_layer_directory(self) -> None:
        escaped = self.repo.root / "outside-evidence.txt"
        escaped.write_text("STEAM_alpha", encoding="utf-8")
        value = document()
        value["rows"][0]["steamStatic"]["evidence"][0]["file"] = (
            "reverse-engineering/binary-analysis/../../outside-evidence.txt"
        )
        self.assert_invalid(value, "unsupported evidence path")

    def test_supporting_anchor_must_appear_in_bounded_evidence(self) -> None:
        value = document()
        value["rows"][0]["steamStatic"]["supportingAnchors"] = [
            "0x00401000 Invented__Anchor"
        ]
        self.assert_invalid(value, "supporting anchor is absent from bounded evidence")

    def test_duplicate_address_even_same_pair_fails_closed(self) -> None:
        alpha = row("alpha")
        beta = row("beta")
        beta["steamStatic"]["address"] = alpha["steamStatic"]["address"]
        beta["steamStatic"]["symbol"] = alpha["steamStatic"]["symbol"]
        self.assert_invalid(document([alpha, beta]), "duplicate or conflicting Steam address")

    def test_duplicate_steam_symbol_case_insensitive_fails_closed(self) -> None:
        alpha = row("alpha")
        beta = row("beta")
        beta["steamStatic"]["symbol"] = alpha["steamStatic"]["symbol"].upper()
        self.assert_invalid(document([alpha, beta]), "duplicate Steam symbol")

    def test_ambiguous_address_list_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["steamStatic"]["addressCandidates"] = ["0x00401000"]
        self.assert_invalid(value, "ambiguous Steam address")

    def test_mixed_evidence_vocabulary_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["sourceHypothesis"]["status"] = "accepted-bounded-static"
        self.assert_invalid(value, "unsupported sourceHypothesis status")

    def test_mixed_layer_fields_fail_closed(self) -> None:
        value = document()
        value["rows"][0]["archiveObservation"]["address"] = "0x00401000"
        self.assert_invalid(value, "unknown field address")

    def test_source_only_row_cannot_declare_static_ready(self) -> None:
        value = document()
        value["rows"][0]["steamStatic"] = layer("required-not-established", evidence=[])
        self.assert_invalid(value, "declared readiness does not match computed readiness")

    def test_input_handoff_cannot_promote_scalar_runtime_measurement(self) -> None:
        value = document([row("alpha", runtime_status="accepted-input-state-handoff-only")])
        value["rows"][0]["declaredReadiness"]["runtimeMeasurementReady"] = True
        self.assert_invalid(value, "declared readiness does not match computed readiness")

    def test_accepted_runtime_requires_evidence(self) -> None:
        value = document([row("alpha", runtime_status="accepted-copied-runtime-measurement")])
        value["rows"][0]["copiedRuntimeMeasurement"]["evidence"] = []
        self.assert_invalid(value, "accepted status requires evidence")

    def test_accepted_rebuild_requires_evidence(self) -> None:
        value = document([row("alpha", runtime_status="accepted-copied-runtime-measurement")])
        value["rows"][0]["rebuildContract"] = layer(
            "accepted-rebuild-contract",
            contractClass="accepted-public-behavior-contract",
            evidence=[],
        )
        self.assert_invalid(value, "accepted status requires evidence")

    def test_valid_runtime_and_rebuild_evidence_compute_readiness(self) -> None:
        value = document([row("alpha", runtime_status="accepted-copied-runtime-measurement")])
        value["rows"][0]["rebuildContract"] = layer(
            "accepted-rebuild-contract",
            contractClass="accepted-public-behavior-contract",
            evidence=[evidence("REBUILD_alpha", "rebuild/contract.md")],
        )
        value["rows"][0]["declaredReadiness"]["runtimeMeasurementReady"] = True
        value["rows"][0]["declaredReadiness"]["rebuildContractReady"] = True
        report = self.validate(value)
        self.assertTrue(report["rows"][0]["computedReadiness"]["rebuildContractReady"])

    def test_identity_requires_typed_nonempty_runtime_evidence(self) -> None:
        value = document([row("alpha", runtime_status="accepted-copied-runtime-measurement")])
        item = value["rows"][0]
        item["claimClass"] = "exact-player-resource-identity"
        item["copiedRuntimeMeasurement"]["measurementClass"] = "exact-resource-identity"
        item["declaredReadiness"]["runtimeMeasurementReady"] = True
        item["declaredReadiness"]["identityReady"] = True
        report = self.validate(value)
        self.assertTrue(report["rows"][0]["computedReadiness"]["identityReady"])

    def test_free_form_identity_assertion_fails_closed(self) -> None:
        value = document([row("alpha", runtime_status="accepted-copied-runtime-measurement")])
        value["rows"][0]["copiedRuntimeMeasurement"]["identityObserved"] = True
        self.assert_invalid(value, "unknown field identityObserved")

    def test_archive_name_lead_cannot_promote_identity(self) -> None:
        value = document()
        item = value["rows"][0]
        item["archiveObservation"] = layer(
            "reported-local-name-structure-lead",
            evidence=[],
            resourceName="fixture.aya",
            partCount=1,
            parentChildEdgeCount=0,
            referenceCount=0,
            boneCount=0,
        )
        item["declaredReadiness"]["identityReady"] = True
        self.assert_invalid(value, "declared readiness does not match computed readiness")

    def test_missing_dependency_fails_closed(self) -> None:
        self.assert_invalid(document([row("alpha", dependencies=["missing"])]), "unknown dependency")

    def test_required_dependency_cannot_be_omitted(self) -> None:
        value = document([row("alpha")])
        value["rows"][0]["requiredDependencies"] = ["beta"]
        self.assert_invalid(value, "required dependency is absent")

    def test_runtime_readiness_cannot_bypass_unready_dependency(self) -> None:
        dependency = row("beta")
        dependent = row(
            "alpha",
            runtime_status="accepted-copied-runtime-measurement",
            dependencies=["beta"],
        )
        dependent["declaredReadiness"]["runtimeMeasurementReady"] = True
        self.assert_invalid(
            document([dependent, dependency]),
            "declared readiness does not match computed readiness",
        )

    def test_dependency_cycle_fails_with_cycle_path(self) -> None:
        value = document(
            [row("alpha", dependencies=["beta"]), row("beta", dependencies=["alpha"])]
        )
        self.assert_invalid(value, r"dependency cycle: alpha -> beta -> alpha")

    def test_incomplete_readiness_requirement_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["requirements"]["staticCrosswalk"] = ["sourceHypothesis"]
        self.assert_invalid(value, "incomplete or unsupported readiness requirements")

    def test_declared_readiness_requires_real_booleans(self) -> None:
        value = document()
        value["rows"][0]["declaredReadiness"]["identityReady"] = 0
        self.assert_invalid(value, "declared readiness does not match computed readiness")

    def test_absolute_path_in_any_text_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["claim"] = r"C:\private\proof.log"
        self.assert_invalid(value, "private or absolute path")

    def test_private_field_alias_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["copiedRuntimeMeasurement"]["artifactPath"] = "redacted"
        self.assert_invalid(value, "forbidden private/runtime field")

    def test_unknown_evidence_layer_fails_closed(self) -> None:
        value = document()
        value["rows"][0]["retailTruth"] = layer("accepted", evidence=[])
        self.assert_invalid(value, "unknown field retailTruth")

    def test_general_registry_cannot_promote_exact_identity(self) -> None:
        resource = row("resource")
        resource["claimClass"] = "general-resource-registry"
        identity = row("walker", dependencies=["resource"])
        identity["claimClass"] = "exact-player-resource-identity"
        identity["steamStatic"] = layer("required-not-established", evidence=[])
        identity["declaredReadiness"]["identityReady"] = True
        self.assert_invalid(document([resource, identity]), "general registry evidence cannot promote exact identity")

    def test_validation_does_not_mutate_document(self) -> None:
        value = document()
        before = copy.deepcopy(value)
        self.validate(value)
        self.assertEqual(before, value)


class ProductionFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.fixture_path = (
            cls.root
            / "reverse-engineering"
            / "source-code"
            / "onslaught-source-steam-crosswalk.v1.json"
        )
        cls.value = json.loads(cls.fixture_path.read_text(encoding="utf-8"))
        source_root_text = os.environ.get("ONSLAUGHT_SOURCE_ROOT")
        if source_root_text is None:
            raise AssertionError("ONSLAUGHT_SOURCE_ROOT is required for production validation")
        cls.source_root = Path(source_root_text)

    def validate(self, value: object | None = None) -> dict[str, object]:
        return crosswalk.validate_document(
            self.value if value is None else value,
            self.root,
            source_root=self.source_root,
        )

    def test_explicit_uninitialized_source_root_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source_root = Path(temporary_directory) / "references" / "Onslaught"
            with self.assertRaisesRegex(
                crosswalk.CrosswalkValidationError, "source revision is unavailable"
            ):
                crosswalk.validate_document(
                    self.value,
                    self.root,
                    source_root=source_root,
                )

    def test_production_fixture_has_exact_rows_and_bounded_readiness(self) -> None:
        report = self.validate()
        self.assertNotIn(str(self.source_root), json.dumps(report))
        self.assertEqual(crosswalk.PRODUCTION_ORDER, [item["id"] for item in report["rows"]])
        by_id = {item["id"]: item["computedReadiness"] for item in report["rows"]}
        self.assertFalse(by_id["battleengine_primary_mesh_role"]["staticCrosswalkReady"])
        for row_id in crosswalk.PRODUCTION_ORDER:
            self.assertFalse(by_id[row_id]["identityReady"])
            self.assertFalse(by_id[row_id]["runtimeMeasurementReady"])
            self.assertFalse(by_id[row_id]["rebuildContractReady"])
        for row_id in crosswalk.PRODUCTION_ORDER[1:]:
            self.assertTrue(by_id[row_id]["staticCrosswalkReady"])

    def test_production_profile_rejects_missing_row(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"].pop()
        with self.assertRaisesRegex(crosswalk.CrosswalkValidationError, "exact eight row ids"):
            self.validate(value)

    def test_production_profile_rejects_r1_static_promotion(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"][0]["steamStatic"]["status"] = "accepted-bounded-static"
        value["rows"][0]["declaredReadiness"]["staticCrosswalkReady"] = True
        with self.assertRaisesRegex(crosswalk.CrosswalkValidationError, "production Steam anchor/status mismatch"):
            self.validate(value)

    def test_production_profile_rejects_source_token_drift(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"][0]["sourceHypothesis"]["requiredTokens"] = [
            "m_be1.msh",
            "f_be1.msh",
        ]
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError, "production source tokens mismatch"
        ):
            self.validate(value)

    def test_production_profile_rejects_static_evidence_range_drift(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"][1]["steamStatic"]["evidence"][0]["lineStart"] = 3
        value["rows"][1]["steamStatic"]["evidence"][0]["lineEnd"] = 17
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError, "production Steam evidence mismatch"
        ):
            self.validate(value)

    def test_production_profile_rejects_claim_or_nonclaim_drift(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"][5]["claim"] = (
            "The released game behavior is proven equivalent to the source."
        )
        value["rows"][5]["nonclaims"] = ["No remaining uncertainty."]
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError,
            "production claim/nonclaim text mismatch",
        ):
            self.validate(value)

    def test_production_profile_rejects_supporting_anchor_drift(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"][2]["steamStatic"]["supportingAnchors"].append(
            "0x00400000 Invented__Anchor"
        )
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError,
            "supporting anchor is absent from bounded evidence",
        ):
            self.validate(value)

    def test_production_profile_rejects_w1_runtime_promotion(self) -> None:
        value = copy.deepcopy(self.value)
        runtime = value["rows"][4]["copiedRuntimeMeasurement"]
        runtime["status"] = "accepted-copied-runtime-measurement"
        runtime["measurementClass"] = "scalar-behavior"
        with self.assertRaisesRegex(crosswalk.CrosswalkValidationError, "production runtime status mismatch"):
            self.validate(value)

    def test_production_profile_rejects_w2_runtime_promotion(self) -> None:
        value = copy.deepcopy(self.value)
        runtime = value["rows"][5]["copiedRuntimeMeasurement"]
        runtime["status"] = "accepted-copied-runtime-measurement"
        runtime["measurementClass"] = "scalar-behavior"
        runtime["evidence"] = copy.deepcopy(
            value["rows"][4]["copiedRuntimeMeasurement"]["evidence"]
        )
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError, "production runtime status mismatch"
        ):
            self.validate(value)

    def test_production_profile_rejects_dependency_removal(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"][5]["dependencies"] = []
        value["rows"][5]["requiredDependencies"] = []
        with self.assertRaisesRegex(crosswalk.CrosswalkValidationError, "production dependency mismatch"):
            self.validate(value)

    def test_production_profile_rejects_archive_count_drift(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"][0]["archiveObservation"]["partCount"] = 64
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError,
            "production archive observation mismatch",
        ):
            self.validate(value)

    def test_production_profile_rejects_archive_field_or_evidence_drift(self) -> None:
        value = copy.deepcopy(self.value)
        value["rows"][3]["archiveObservation"]["internalName"] = "invented.msh"
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError,
            "production archive observation mismatch",
        ):
            self.validate(value)

    def test_public_validator_rejects_coordinated_document_pin_drift(self) -> None:
        value = copy.deepcopy(self.value)
        value["sourceRevision"] = "0" * 40
        with self.assertRaisesRegex(
            crosswalk.CrosswalkValidationError, "source revision mismatch"
        ):
            self.validate(value)

    def test_public_validator_rejects_dirty_tracked_evidence_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            evidence_root = Path(temp)
            evidence_paths = {
                item["file"]
                for row_value in self.value["rows"]
                for layer_name in crosswalk.EVIDENCE_LAYERS[1:]
                for item in row_value[layer_name].get("evidence", [])
            }
            for relative in evidence_paths:
                destination = evidence_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                copyfile(self.root / relative, destination)
            for command in (
                ["git", "init", "--quiet"],
                ["git", "config", "user.email", "fixture@example.invalid"],
                ["git", "config", "user.name", "Fixture"],
                ["git", "add", "."],
                ["git", "commit", "--quiet", "-m", "evidence fixture"],
            ):
                subprocess.run(command, cwd=evidence_root, check=True)
            dirty = evidence_root / sorted(evidence_paths)[0]
            with dirty.open("a", encoding="utf-8") as stream:
                stream.write("\nDIRTY_TRACKED_EVIDENCE")
            with self.assertRaisesRegex(
                crosswalk.CrosswalkValidationError,
                "repository evidence working tree is not clean",
            ):
                crosswalk.validate_document(
                    self.value,
                    evidence_root,
                    source_root=self.source_root,
                )

    def test_public_validator_rejects_clean_tracked_symlink_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            evidence_root = Path(temp)
            evidence_paths = {
                item["file"]
                for row_value in self.value["rows"]
                for layer_name in crosswalk.EVIDENCE_LAYERS[1:]
                for item in row_value[layer_name].get("evidence", [])
            }
            for relative in evidence_paths:
                destination = evidence_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                copyfile(self.root / relative, destination)
            for command in (
                ["git", "init", "--quiet"],
                ["git", "config", "user.email", "fixture@example.invalid"],
                ["git", "config", "user.name", "Fixture"],
                ["git", "add", "."],
                ["git", "commit", "--quiet", "-m", "evidence fixture"],
            ):
                subprocess.run(command, cwd=evidence_root, check=True)

            relative = sorted(evidence_paths)[0]
            link_path = evidence_root / relative
            target = link_path.with_name("mutable-untracked-evidence.md")
            copyfile(link_path, target)
            link_target = target.name
            blob = subprocess.run(
                ["git", "hash-object", "-w", "--stdin"],
                cwd=evidence_root,
                input=link_target,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            subprocess.run(
                [
                    "git",
                    "update-index",
                    "--add",
                    "--cacheinfo",
                    f"120000,{blob},{relative}",
                ],
                cwd=evidence_root,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "--quiet", "-m", "tracked evidence symlink"],
                cwd=evidence_root,
                check=True,
            )
            link_path.unlink()
            try:
                link_path.symlink_to(link_target)
            except OSError:
                link_path.write_text(link_target, encoding="utf-8")

            with self.assertRaisesRegex(
                crosswalk.CrosswalkValidationError,
                "repository evidence path is not a regular blob",
            ):
                crosswalk.validate_document(
                    self.value,
                    evidence_root,
                    source_root=self.source_root,
                )

    def test_malformed_cli_root_has_controlled_path_free_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp) / "bad.json"
            bad.write_text("[]", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = crosswalk.main(
                    [
                        str(bad),
                        "--repo-root",
                        str(self.root),
                        "--source-root",
                        str(self.source_root),
                    ]
                )
            self.assertEqual(1, code)
            self.assertEqual("FAIL: document root must be an object", stderr.getvalue().strip())
            self.assertNotIn(str(self.source_root), stderr.getvalue())

    def test_missing_cli_input_has_controlled_path_free_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "private-missing-crosswalk.json"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = crosswalk.main(
                    [
                        str(missing),
                        "--repo-root",
                        str(self.root),
                        "--source-root",
                        str(self.source_root),
                    ]
                )
            self.assertEqual(1, code)
            self.assertEqual("FAIL: crosswalk file is unavailable", stderr.getvalue().strip())
            self.assertNotIn(str(missing), stderr.getvalue())

    def test_malformed_cli_json_has_controlled_path_free_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            malformed = Path(temp) / "private-malformed-crosswalk.json"
            malformed.write_text("{", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = crosswalk.main(
                    [
                        str(malformed),
                        "--repo-root",
                        str(self.root),
                        "--source-root",
                        str(self.source_root),
                    ]
                )
            self.assertEqual(1, code)
            self.assertEqual("FAIL: crosswalk JSON is malformed", stderr.getvalue().strip())
            self.assertNotIn(str(malformed), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
