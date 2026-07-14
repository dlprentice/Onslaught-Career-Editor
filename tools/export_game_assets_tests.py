#!/usr/bin/env python3
"""Contract tests for path-free AYA export-outcome production."""

from __future__ import annotations

import copy
import hashlib
import unittest

import aya_archive_inventory as aya_observation
import export_game_assets as exporter


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64


def observation() -> dict[str, object]:
    observed = {
        "archiveOrdinal": "archive-0001",
        "chunkObservations": [
            {
                "bodyCandidateObservations": [],
                "chunkOrdinal": "chunk-0001",
                "declaredLength": 3,
                "payloadSha256": SHA_B,
                "tagAscii": "TEXT",
                "tagHex": "54455854",
            },
            {
                "bodyCandidateObservations": [
                    {
                        "boundaryRule": "cmsh-to-next-pmsh-pms2-or-mesh-end",
                        "candidateOrdinal": "body-candidate-0001",
                        "evidenceKind": "candidate-only",
                        "length": 4,
                        "sha256": SHA_C,
                        "tagAscii": "CMSH",
                        "tagHex": "434d5348",
                    }
                ],
                "chunkOrdinal": "chunk-0002",
                "declaredLength": 4,
                "payloadSha256": SHA_C,
                "tagAscii": "MESH",
                "tagHex": "4d455348",
            },
        ],
        "extension": ".aya",
        "inflatedLength": 23,
        "memberCount": 1,
        "observationStatus": "observed",
        "rejectionCategory": None,
        "sourceIdentity": {"length": 17, "sha256": SHA_A},
    }
    second = copy.deepcopy(observed)
    second["archiveOrdinal"] = "archive-0002"
    second["extension"] = "other"
    second["sourceIdentity"] = {"length": 18, "sha256": SHA_D}
    return aya_observation._observation_report([second, observed])


def target(chunk: int | None = None, *, archive: int = 1) -> dict[str, object]:
    source_identities = {
        1: {"length": 17, "sha256": SHA_A},
        2: {"length": 18, "sha256": SHA_D},
    }
    value: dict[str, object] = {
        "sourceOrdinal": f"archive-{archive:04d}",
        "sourceIdentity": source_identities[archive],
        "chunkIdentity": None,
    }
    if chunk == 1:
        value["chunkIdentity"] = {
            "chunkOrdinal": "chunk-0001",
            "declaredLength": 3,
            "payloadSha256": SHA_B,
        }
    elif chunk == 2:
        value["chunkIdentity"] = {
            "chunkOrdinal": "chunk-0002",
            "declaredLength": 4,
            "payloadSha256": SHA_C,
        }
    return value


def terminal(
    expected: dict[str, object],
    *,
    status: str = "exported",
    reason: str | None = None,
    output_kind: str = "png",
    digest_status: str = "verified",
    digest: str | None = SHA_D,
    dependencies: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        **copy.deepcopy(expected),
        "dependencies": dependencies or [],
        "deterministicOutputDigest": digest,
        "deterministicOutputStatus": digest_status,
        "exportStatus": status,
        "outputKind": output_kind,
        "reason": reason,
    }


def manifest(
    lane: str,
    expected: list[dict[str, object]],
    records: list[dict[str, object]],
    universe: str,
) -> dict[str, object]:
    return {
        "expectedRecords": expected,
        "lane": lane,
        "records": records,
        "schemaVersion": "onslaught.aya-export-lane-manifest.v1",
        "sourceUniverseId": universe,
    }


def complete_outcomes(source: dict[str, object]) -> dict[str, object]:
    lane_records = [
        ("looseTextures", target(1), "png"),
        ("looseMeshes", target(2), "fbx"),
        ("embeddedMeshes", target(), "obj"),
        ("embeddedMeshes", target(archive=2), "materialReport"),
        ("language", target(1, archive=2), "languageCorpus"),
        ("video", target(2, archive=2), "videoManifest"),
        ("catalog", target(archive=2), "assetCatalog"),
    ]
    manifests = [
        manifest(
            lane,
            [expected],
            [terminal(expected, output_kind=output_kind)],
            source["sourceUniverseId"],
        )
        for lane, expected, output_kind in lane_records
    ]
    return exporter.produce_export_outcomes(source, manifests)


class ExportOutcomeProducerTests(unittest.TestCase):
    def test_reconciles_complete_corpus_without_parsing_private_payloads(self) -> None:
        source = observation()
        outcomes = complete_outcomes(source)

        first = exporter.produce_corpus_reconciliation(source, outcomes)
        second = exporter.produce_corpus_reconciliation(
            copy.deepcopy(source), copy.deepcopy(outcomes)
        )

        self.assertEqual(
            exporter.render_corpus_reconciliation(first),
            exporter.render_corpus_reconciliation(second),
        )
        self.assertEqual("onslaught.aya-corpus-reconciliation.v1", first["schemaVersion"])
        self.assertEqual("complete", first["observedSurfaceCoverageStatus"])
        self.assertEqual("terminal-outcome-surface-reconciliation", first["evidenceScope"])
        self.assertEqual(64, len(first["sourceObservationSha256"]))
        self.assertEqual(list(exporter.RECONCILIATION_NONCLAIMS), first["nonClaims"])
        self.assertEqual(
            hashlib.sha256(aya_observation.render_observation_records(source)).hexdigest(),
            first["sourceObservationSha256"],
        )
        self.assertEqual(
            hashlib.sha256(exporter.render_export_outcomes(outcomes)).hexdigest(),
            first["exportOutcomeSha256"],
        )
        self.assertEqual(2, first["observedArchiveCount"])
        self.assertEqual([".aya", "other"], first["observedExtensions"])
        self.assertEqual(
            [
                {"tagAscii": "MESH", "tagHex": "4d455348"},
                {"tagAscii": "TEXT", "tagHex": "54455854"},
            ],
            first["observedTags"],
        )
        self.assertEqual(sorted(exporter.EXPORT_LANES), first["coveredLanes"])
        self.assertEqual(
            sorted(exporter.OUTPUT_KINDS - {"none"}),
            first["coveredOutputKinds"],
        )
        self.assertEqual(
            {"exported": 7},
            first["terminalStatusCounts"],
        )
        encoded = exporter.render_corpus_reconciliation(first).decode("ascii")
        self.assertNotIn("\\", encoded)
        self.assertNotIn("/", encoded)

    def test_reconciliation_rejects_incomplete_or_tampered_outcomes(self) -> None:
        source = observation()
        complete = complete_outcomes(source)
        cases: list[tuple[str, str, dict[str, object]]] = []

        missing_archive = copy.deepcopy(complete)
        missing_archive["exportRecords"] = [
            row
            for row in missing_archive["exportRecords"]
            if row["sourceOrdinal"] != "archive-0002"
        ]
        cases.append(("archive", "archive coverage", missing_archive))

        missing_tag = copy.deepcopy(complete)
        missing_tag["exportRecords"] = [
            row
            for row in missing_tag["exportRecords"]
            if {tag["tagAscii"] for tag in row["observedTags"]} == {"TEXT"}
        ]
        cases.append(("tag", "tag coverage", missing_tag))

        missing_lane = copy.deepcopy(complete)
        missing_lane["exportRecords"] = [
            row for row in missing_lane["exportRecords"] if row["lane"] != "video"
        ]
        cases.append(("lane", "lane coverage", missing_lane))

        missing_output = copy.deepcopy(complete)
        missing_output["exportRecords"] = [
            row for row in missing_output["exportRecords"] if row["outputKind"] != "materialReport"
        ]
        cases.append(("output", "output-family coverage", missing_output))

        tampered_observation = copy.deepcopy(complete)
        tampered_observation["exportRecords"][0]["observedExtensions"] = [".private"]
        cases.append(("observed fields", "observation fields disagree", tampered_observation))

        reversed_records = copy.deepcopy(complete)
        reversed_records["exportRecords"].reverse()
        cases.append(("canonical order", "canonical order", reversed_records))

        for label, error_pattern, outcomes in cases:
            with self.subTest(label=label):
                with self.assertRaisesRegex(exporter.ExportOutcomeError, error_pattern):
                    exporter.produce_corpus_reconciliation(source, outcomes)

    def test_reconciliation_rejects_semantic_loopholes_and_malformed_summary(self) -> None:
        source = observation()
        complete = complete_outcomes(source)

        incompatible_lane = copy.deepcopy(complete)
        png = next(row for row in incompatible_lane["exportRecords"] if row["outputKind"] == "png")
        png["lane"] = "catalog"
        incompatible_lane["exportRecords"].sort(key=exporter._canonical_bytes)
        with self.assertRaisesRegex(exporter.ExportOutcomeError, "lane/output kind"):
            exporter.produce_corpus_reconciliation(source, incompatible_lane)

        unsupported = copy.deepcopy(complete)
        for record in unsupported["exportRecords"]:
            record["deterministicOutputDigest"] = None
            record["deterministicOutputStatus"] = "notApplicable"
            record["exportStatus"] = "knownUnsupported"
            record["reason"] = "unsupportedOutputKind"
        unsupported["exportRecords"].sort(key=exporter._canonical_bytes)
        with self.assertRaisesRegex(exporter.ExportOutcomeError, "verified output-family"):
            exporter.produce_corpus_reconciliation(source, unsupported)

        rejected_source = copy.deepcopy(source)
        rejected = rejected_source["archiveRecords"][1]
        rejected["chunkObservations"] = []
        rejected["inflatedLength"] = None
        rejected["memberCount"] = None
        rejected["observationStatus"] = "rejected"
        rejected["rejectionCategory"] = "empty_archive"
        rejected_source = aya_observation._observation_report(
            rejected_source["archiveRecords"]
        )
        rejected_target = {
            "sourceOrdinal": "archive-0001",
            "sourceIdentity": {"length": 18, "sha256": SHA_D},
            "chunkIdentity": None,
        }
        with self.assertRaisesRegex(
            exporter.ExportOutcomeError, "rejected source cannot carry output"
        ):
            exporter.produce_export_outcomes(
                rejected_source,
                [
                    manifest(
                        "catalog",
                        [rejected_target],
                        [terminal(rejected_target, output_kind="assetCatalog")],
                        rejected_source["sourceUniverseId"],
                    )
                ],
            )

        summary = exporter.produce_corpus_reconciliation(source, complete)
        malformed_summaries = []
        malformed_extension = copy.deepcopy(summary)
        malformed_extension["observedExtensions"] = [1]
        malformed_summaries.append(malformed_extension)
        contradictory_status = copy.deepcopy(summary)
        contradictory_status["terminalStatusCounts"] = {"knownUnsupported": 7}
        malformed_summaries.append(contradictory_status)
        mismatched_tag = copy.deepcopy(summary)
        mismatched_tag["observedTags"][0]["tagHex"] = "00000000"
        mismatched_tag["observedTags"].sort(key=exporter._canonical_bytes)
        malformed_summaries.append(mismatched_tag)
        impossible_archive_count = copy.deepcopy(summary)
        impossible_archive_count["observedArchiveCount"] = 8
        malformed_summaries.append(impossible_archive_count)
        for malformed_summary in malformed_summaries:
            with self.subTest(malformed_summary=malformed_summary):
                with self.assertRaises(exporter.ExportOutcomeError):
                    exporter.render_corpus_reconciliation(malformed_summary)

        no_tags = copy.deepcopy(source)
        for archive in no_tags["archiveRecords"]:
            archive["chunkObservations"] = []
            archive["inflatedLength"] = 0
        no_tags = aya_observation._observation_report(no_tags["archiveRecords"])
        source_targets = [
            ("looseTextures", target(), "png"),
            ("looseMeshes", target(), "fbx"),
            ("embeddedMeshes", target(), "obj"),
            ("embeddedMeshes", target(archive=2), "materialReport"),
            ("language", target(archive=2), "languageCorpus"),
            ("video", target(archive=2), "videoManifest"),
            ("catalog", target(archive=2), "assetCatalog"),
        ]
        no_tag_outcomes = exporter.produce_export_outcomes(
            no_tags,
            [
                manifest(
                    lane,
                    [expected],
                    [terminal(expected, output_kind=output_kind)],
                    no_tags["sourceUniverseId"],
                )
                for lane, expected, output_kind in source_targets
            ],
        )
        with self.assertRaisesRegex(exporter.ExportOutcomeError, "no tag surfaces"):
            exporter.produce_corpus_reconciliation(no_tags, no_tag_outcomes)

        empty = aya_observation._observation_report([])
        empty_outcomes = exporter.produce_export_outcomes(empty, [])
        with self.assertRaisesRegex(exporter.ExportOutcomeError, "empty observation universe"):
            exporter.produce_corpus_reconciliation(empty, empty_outcomes)

    def test_produces_canonical_path_free_records_and_preserves_observations(self) -> None:
        source = observation()
        source_target = target()
        mesh_target = target(2)
        dependencies = [
            {
                "dependencyType": "source",
                "identity": {"length": 17, "sha256": SHA_A},
                "status": "resolved",
            },
            {
                "dependencyType": "texture",
                "identity": {"length": 3, "sha256": SHA_B},
                "status": "missing",
            },
        ]
        manifests = [
            manifest(
                "embeddedMeshes",
                [mesh_target],
                [
                    terminal(
                        mesh_target,
                        output_kind="obj",
                        dependencies=dependencies,
                    )
                ],
                source["sourceUniverseId"],
            ),
            manifest(
                "catalog",
                [source_target],
                [terminal(source_target, output_kind="assetCatalog")],
                source["sourceUniverseId"],
            ),
        ]

        first = exporter.produce_export_outcomes(source, manifests)
        second = exporter.produce_export_outcomes(source, list(reversed(manifests)))

        self.assertEqual(
            exporter.render_export_outcomes(first),
            exporter.render_export_outcomes(second),
        )
        self.assertEqual("onslaught.aya-export-outcome.v1", first["schemaVersion"])
        self.assertEqual(source["sourceUniverseId"], first["sourceUniverseId"])
        mesh = next(row for row in first["exportRecords"] if row["lane"] == "embeddedMeshes")
        self.assertEqual([".aya"], mesh["observedExtensions"])
        self.assertEqual(
            [{"tagAscii": "MESH", "tagHex": "4d455348"}],
            mesh["observedTags"],
        )
        self.assertEqual(
            ["archiveObserved", "chunkObserved", "meshBodyCandidateObserved"],
            mesh["observedFeatureFlags"],
        )
        encoded = exporter.render_export_outcomes(first).decode("ascii")
        self.assertNotIn("\\", encoded)
        self.assertNotIn("/", encoded)

    def test_accepts_every_closed_terminal_status(self) -> None:
        source = observation()
        statuses = [
            ("exported", None, "png", "verified", SHA_D),
            ("knownUnsupported", "unsupportedFeature", "none", "notApplicable", None),
            ("rejected", "exportFailed", "fbx", "failed", None),
            ("notAttempted", "notRequested", "none", "notApplicable", None),
            ("notApplicable", "laneNotApplicable", "none", "notApplicable", None),
        ]
        manifests = []
        for lane, terminal_status in zip(exporter.EXPORT_LANES[:5], statuses, strict=True):
            expected = target(1)
            manifests.append(
                manifest(
                    lane,
                    [expected],
                    [
                        terminal(
                            expected,
                            status=terminal_status[0],
                            reason=terminal_status[1],
                            output_kind=terminal_status[2],
                            digest_status=terminal_status[3],
                            digest=terminal_status[4],
                        )
                    ],
                    source["sourceUniverseId"],
                )
            )

        result = exporter.produce_export_outcomes(source, manifests)

        self.assertEqual(set(exporter.EXPORT_STATUSES), {row["exportStatus"] for row in result["exportRecords"]})

    def test_rejects_missing_duplicate_and_ambiguous_terminal_records(self) -> None:
        source = observation()
        expected = target(1)
        cases = [
            manifest("catalog", [expected], [], source["sourceUniverseId"]),
            manifest(
                "catalog",
                [expected],
                [terminal(expected), terminal(expected)],
                source["sourceUniverseId"],
            ),
            manifest(
                "catalog",
                [expected, copy.deepcopy(expected)],
                [terminal(expected)],
                source["sourceUniverseId"],
            ),
        ]
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(exporter.ExportOutcomeError):
                    exporter.produce_export_outcomes(source, [value])

    def test_rejects_foreign_universe_and_foreign_source_or_chunk_identity(self) -> None:
        source = observation()
        expected = target(1)
        foreign_source = copy.deepcopy(expected)
        foreign_source["sourceIdentity"]["sha256"] = SHA_D
        foreign_chunk = copy.deepcopy(expected)
        foreign_chunk["chunkIdentity"]["payloadSha256"] = SHA_D
        cases = [
            manifest("catalog", [expected], [terminal(expected)], SHA_D),
            manifest(
                "catalog",
                [foreign_source],
                [terminal(foreign_source)],
                source["sourceUniverseId"],
            ),
            manifest(
                "catalog",
                [foreign_chunk],
                [terminal(foreign_chunk)],
                source["sourceUniverseId"],
            ),
        ]
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(exporter.ExportOutcomeError):
                    exporter.produce_export_outcomes(source, [value])

    def test_rejects_path_private_name_and_open_vocabulary_leakage(self) -> None:
        source = observation()
        expected = target()
        base = manifest(
            "catalog",
            [expected],
            [terminal(expected, output_kind="assetCatalog")],
            source["sourceUniverseId"],
        )
        cases: list[dict[str, object]] = []
        with_path = copy.deepcopy(base)
        with_path["records"][0]["input"] = r"C:\private\named-source.aya"
        cases.append(with_path)
        with_name = copy.deepcopy(base)
        with_name["records"][0]["privateName"] = "named-source.aya"
        cases.append(with_name)
        open_output = copy.deepcopy(base)
        open_output["records"][0]["outputKind"] = "privateCustomFormat"
        cases.append(open_output)
        open_dependency = copy.deepcopy(base)
        open_dependency["records"][0]["dependencies"] = [
            {
                "dependencyType": "privatePlugin",
                "identity": {"length": 1, "sha256": SHA_A},
                "status": "resolved",
            }
        ]
        cases.append(open_dependency)
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(exporter.ExportOutcomeError):
                    exporter.produce_export_outcomes(source, [value])

    def test_rejects_invalid_status_reason_dependency_and_digest_combinations(self) -> None:
        source = observation()
        expected = target()
        records = [
            terminal(expected, status="partial"),
            terminal(expected, reason="privateFailure"),
            terminal(expected, status="exported", digest_status="failed", digest=None),
            terminal(expected, status="rejected", reason="exportFailed", digest_status="verified"),
            terminal(
                expected,
                dependencies=[
                    {
                        "dependencyType": "source",
                        "identity": {"length": 17, "sha256": SHA_A},
                        "status": "maybe",
                    }
                ],
            ),
        ]
        for record in records:
            value = manifest(
                "catalog", [expected], [record], source["sourceUniverseId"]
            )
            with self.subTest(record=record):
                with self.assertRaises(exporter.ExportOutcomeError):
                    exporter.produce_export_outcomes(source, [value])

    def test_rejects_unaccepted_observation_and_manifest_versions(self) -> None:
        source = observation()
        expected = target()
        bad_observation = copy.deepcopy(source)
        bad_observation["schemaVersion"] = "onslaught.aya-archive-observation.v2"
        with self.assertRaises(exporter.ExportOutcomeError):
            exporter.produce_export_outcomes(bad_observation, [])

        bad_manifest = manifest(
            "catalog",
            [expected],
            [terminal(expected, output_kind="assetCatalog")],
            source["sourceUniverseId"],
        )
        bad_manifest["schemaVersion"] = "onslaught.aya-export-lane-manifest.v2"
        with self.assertRaises(exporter.ExportOutcomeError):
            exporter.produce_export_outcomes(source, [bad_manifest])

    def test_rejects_reversed_reordinaled_recomputed_unequal_observation_records(self) -> None:
        source = observation()
        reordered = copy.deepcopy(source)
        reordered["archiveRecords"].reverse()
        for ordinal, record in enumerate(reordered["archiveRecords"], 1):
            record["archiveOrdinal"] = f"archive-{ordinal:04d}"
        reordered["sourceUniverseId"] = aya_observation._source_universe_id(
            reordered["archiveRecords"]
        )

        with self.assertRaises(exporter.ExportOutcomeError):
            exporter.produce_export_outcomes(reordered, [])


if __name__ == "__main__":
    unittest.main()
