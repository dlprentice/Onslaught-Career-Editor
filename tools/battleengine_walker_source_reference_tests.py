from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import battleengine_walker_source_reference as model


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def synthetic_repository(root: Path) -> None:
    _write(root / ".git/modules/references/Onslaught/HEAD", model.SOURCE_REVISION + "\n")
    rows = []
    for row_id, tokens in model.REQUIRED_ROWS.items():
        runtime_status = "accepted-input-state-handoff-only" if row_id == "player_forward_route" else "required-not-measured"
        row = {
            "id": row_id,
            "sourceHypothesis": {"status": "hypothesis-only", "requiredTokens": list(tokens)},
            "copiedRuntimeMeasurement": {"status": runtime_status},
            "rebuildContract": {"status": "blocked-until-runtime-accepted"},
        }
        if row_id in model.STEAM_ROW_CONTRACTS:
            status, address, symbol = model.STEAM_ROW_CONTRACTS[row_id]
            row["steamStatic"] = {"status": status, "address": address, "symbol": symbol}
        rows.append(row)
    _write(root / model.SOURCE_CROSSWALK, json.dumps({"sourceRevision": model.SOURCE_REVISION, "rows": rows}))
    for relative, tokens in model.SOURCE_TOKEN_CONTRACTS.items():
        _write(root / relative, "\n".join(tokens))
    for relative, tokens in model.STEAM_EVIDENCE_TOKEN_CONTRACTS.items():
        _write(root / relative, "\n".join(tokens))


class SourceReferenceTests(unittest.TestCase):
    def test_default_repo_root_resolves_from_handoff_or_integrated_tool(self) -> None:
        self.assertEqual(Path.cwd().resolve(), model._parse_args([]).repo_root.resolve())

    def test_integrated_repository_uses_real_hardened_crosswalk_validator(self) -> None:
        manifest = model.validate_repository_evidence(Path.cwd())
        self.assertEqual("required-not-measured", manifest["copiedRuntimeMeasurement"][0]["status"])
        self.assertFalse(manifest["rebuildContract"][0]["authorizedBehaviorChange"])

    def validate_synthetic_repository(self, root: Path) -> dict[str, object]:
        with mock.patch.object(
            model.crosswalk_validator,
            "validate_document",
            return_value={"status": "validated"},
        ) as validate_document:
            result = model.validate_repository_evidence(root)
        validate_document.assert_called_once()
        document, repo_root = validate_document.call_args.args
        self.assertEqual(root.resolve(), repo_root)
        self.assertEqual(model.SOURCE_REVISION, document["sourceRevision"])
        return result

    def test_repository_evidence_requires_exact_pin_rows_and_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_repository(root)
            self.assertEqual(model.evidence_manifest(), self.validate_synthetic_repository(root))

            path = root / model.SOURCE_CROSSWALK
            data = json.loads(path.read_text(encoding="utf-8"))
            data["sourceRevision"] = "0" * 40
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(model.ModelError, "source pin mismatch"):
                self.validate_synthetic_repository(root)

    def test_repository_evidence_rejects_missing_token_and_promoted_row(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_repository(root)
            (root / model.SOURCE_FILE).write_text("IsOnGround\n", encoding="utf-8")
            with self.assertRaisesRegex(model.ModelError, "missing pinned source tokens"):
                self.validate_synthetic_repository(root)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_repository(root)
            path = root / model.SOURCE_CROSSWALK
            data = json.loads(path.read_text(encoding="utf-8"))
            data["rows"][1]["sourceHypothesis"]["status"] = "confirmed"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(model.ModelError, "promotion"):
                self.validate_synthetic_repository(root)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_repository(root)
            path = root / model.SOURCE_CROSSWALK
            data = json.loads(path.read_text(encoding="utf-8"))
            walker = next(row for row in data["rows"] if row["id"] == "walker_forward")
            walker["copiedRuntimeMeasurement"]["status"] = "accepted-input-state-handoff-only"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(model.ModelError, "runtime status mismatch"):
                self.validate_synthetic_repository(root)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_repository(root)
            path = root / next(iter(model.STEAM_EVIDENCE_TOKEN_CONTRACTS))
            path.write_text("0x004081c0\n", encoding="utf-8")
            with self.assertRaisesRegex(model.ModelError, "missing tracked Steam evidence tokens"):
                self.validate_synthetic_repository(root)

    def test_repository_evidence_rejects_reordered_walker_move_control_flow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_repository(root)
            path = root / model.SOURCE_FILE
            text = path.read_text(encoding="utf-8")
            first, second = model.SOURCE_ORDER_CONTRACTS[model.SOURCE_FILE][:2]
            text = text.replace(first, "__SECOND__").replace(second, first).replace("__SECOND__", second)
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(model.ModelError, "source control-flow order"):
                self.validate_synthetic_repository(root)

    def test_hardened_crosswalk_rejection_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_repository(root)
            with mock.patch.object(
                model.crosswalk_validator,
                "validate_document",
                side_effect=model.crosswalk_validator.CrosswalkValidationError("bad crosswalk"),
            ):
                with self.assertRaisesRegex(model.ModelError, "hardened crosswalk validation failed"):
                    model.validate_repository_evidence(root)

    def test_walker_specific_checks_run_after_hardened_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_repository(root)

            def invalidate_after_validation(*_args: object, **_kwargs: object) -> dict[str, str]:
                (root / model.SOURCE_FILE).write_text("invalid after hardened validation\n", encoding="utf-8")
                return {"status": "validated"}

            with mock.patch.object(
                model.crosswalk_validator,
                "validate_document",
                side_effect=invalidate_after_validation,
            ):
                with self.assertRaisesRegex(model.ModelError, "missing pinned source tokens"):
                    model.validate_repository_evidence(root)

    def test_manifest_separates_all_evidence_layers_and_rejects_promotion(self) -> None:
        manifest = model.evidence_manifest()
        self.assertEqual(
            {
                "sourceHypothesis",
                "steamStatic",
                "archiveObservation",
                "copiedRuntimeMeasurement",
                "rebuildContract",
                "unresolvedDifferences",
            },
            set(manifest),
        )
        self.assertEqual(
            ["0x004081c0", "0x00412ad0", "0x00412d80", "0x00413760"],
            [row["address"] for row in manifest["steamStatic"]],
        )
        self.assertTrue(all(row["status"] == "accepted-bounded-static" for row in manifest["steamStatic"]))
        steam_rows = {row["address"]: row for row in manifest["steamStatic"]}
        identity_claim = "retail address/symbol identity under BattleEngineWalkerPart"
        self.assertEqual(identity_claim, steam_rows["0x00412d80"]["claim"])
        self.assertEqual(identity_claim, steam_rows["0x00413760"]["claim"])
        unresolved_shape = manifest["unresolvedDifferences"][0]
        self.assertFalse(unresolved_shape["retailControlFlowShapeEstablished"])
        self.assertFalse(unresolved_shape["retailNamedConfigBindingsEstablished"])
        self.assertFalse(unresolved_shape["retailConstantsEstablished"])
        self.assertFalse(unresolved_shape["runtimeBehaviorEstablished"])
        self.assertIsNone(manifest["unresolvedDifferences"][1]["values"])
        self.assertFalse(manifest["rebuildContract"][0]["authorizedBehaviorChange"])
        self.assertEqual("blocked-until-runtime-accepted", manifest["rebuildContract"][0]["status"])
        self.assertEqual("required-not-measured", manifest["copiedRuntimeMeasurement"][0]["status"])
        gate = manifest["copiedRuntimeMeasurement"][0]["requiredFutureAcceptanceGate"]
        self.assertFalse(gate["satisfied"])
        self.assertFalse(gate["publicationAuthorized"])
        self.assertEqual("battleengine-walker-forward-scalar-response.v2", gate["schemaVersion"])
        self.assertEqual("two-accepted-fresh-attempts", gate["requiredStatus"])
        self.assertEqual(2, gate["attemptCount"])
        self.assertTrue(gate["thirdAttemptForbidden"])
        self.assertEqual(["receiptSha256", "runDigest"], gate["distinctIdentityFields"])
        self.assertEqual(
            ["receiptRevalidated", "foregroundMaintained", "keyUpConfirmed", "cleanupConfirmed"],
            gate["requiredIntegrity"],
        )
        for fixture in model.generated_fixtures():
            events = model.execute_fixture(fixture)["events"]
            walker_events = [
                event
                for event in events
                if event["call"] in {"CBattleEngineWalkerPart::Forward", "CBattleEngineWalkerPart::Move"}
            ]
            self.assertTrue(walker_events)
            self.assertTrue(all(event["evidence"] == "sourceHypothesis" for event in walker_events))

        promoted = model.evidence_manifest()
        promoted["copiedRuntimeMeasurement"][0]["status"] = "accepted"
        with self.assertRaisesRegex(model.ModelError, "promotion|mutation"):
            model.validate_evidence_manifest(promoted)

    def test_generated_catalog_covers_every_declared_branch(self) -> None:
        report = model.execute_catalog()
        self.assertEqual(sorted(model.BRANCH_IDS), report["branchCoverage"])
        self.assertEqual(7, len(report["fixtures"]))
        self.assertFalse(report["retailValuesResolved"])
        self.assertEqual(model.FUTURE_CORE_CONSUMER, report["futureConsumer"])

    def test_call_order_and_side_effect_order_are_explicit(self) -> None:
        report = model.execute_fixture(model.generated_fixtures()[0])
        self.assertEqual(
            [
                "CPlayer::ReceiveButtonAction",
                "CBattleEngineWalkerPart::Forward",
                "CBattleEngine::Move",
                "CBattleEngineWalkerPart::Move",
                "CBattleEngineWalkerPart::UpdateWalkCycle",
            ],
            report["calls"],
        )
        sequences = [event["sequence"] for event in report["events"]]
        self.assertEqual(list(range(len(sequences))), sequences)
        actions = [event["action"] for event in report["events"]]
        self.assertLess(actions.index("add-symbolic-velocity"), actions.index("dispatch-walker-part"))
        self.assertLess(actions.index("copy-energy-to-shields"), actions.index("apply-symbolic-friction"))
        self.assertLess(actions.index("apply-symbolic-friction"), actions.index("advance-symbolic-cycle"))

    def test_exact_sampler_fields_and_no_measured_values_are_emitted(self) -> None:
        report = model.execute_catalog()
        self.assertEqual(
            [
                "steadySpeed",
                "baselineB95Speed",
                "baselineEndpointDisplacement",
                "responseThreshold",
                "responseLatencyMs",
                "releaseLatencyMs",
                "steadySlope",
                "normalizedResponse",
                "velocityHoldToBaselineRatio",
            ],
            report["measurementFieldPartition"]["scalarMeasurableNow"],
        )
        self.assertEqual(
            ["actorBasis", "actorRelativeDirection", "groundedState", "terrainState", "dashState", "walkCycle", "energy", "shield"],
            report["measurementFieldPartition"]["requiresFutureProbe"],
        )
        self.assertEqual(
            list(model.SOURCE_SHAPED_FIXTURE_INPUTS),
            report["measurementFieldPartition"]["sourceShapedFixtureInputs"],
        )
        rendered = model.render_report(report).decode("utf-8")
        self.assertNotIn('"retailValuesResolved": true', rendered)
        self.assertIn('"status": "required-not-measured"', rendered)
        self.assertIn('"futureConsumer": "deterministic-core-walker-forward"', rendered)
        self.assertEqual(
            {
                "contractFile": "rebuild/OnslaughtRebuild.Core/WalkerForwardResponseContract.cs",
                "contractType": "WalkerForwardResponseContract",
                "integrationFile": "rebuild/OnslaughtRebuild.Core/Simulation.cs",
                "integrationType": "Simulation",
                "contractTests": "rebuild/OnslaughtRebuild.Core.Tests/WalkerForwardResponseContractTests.cs",
                "integrationTests": "rebuild/OnslaughtRebuild.Core.Tests/SimulationTests.cs",
                "contractTestCases": [
                    "AcceptsTwoAttemptEnvelope",
                    "RejectsMissingOrOutOfRangeEnvelope",
                ],
                "integrationTestCases": [
                    "WalkerForward_UsesAcceptedResponseContractDeterministically",
                    "WalkerForward_ReplayHashIsStable",
                ],
                "constantsFile": "rebuild/OnslaughtRebuild.Core/SimulationConstants.cs",
                "constantsType": "SimulationConstants",
                "candidateConstantsMember": "WalkerSpeedPerTick",
                "translationContract": {
                    "status": "blocked-until-coordinate-scale-tick-and-quantization-policy-accepted",
                    "measurementUnit": "retail-world-coordinate-units-per-second",
                    "coreUnit": "integer-core-units-per-tick",
                    "coreTickRateMember": "SimulationConstants.TicksPerSecond",
                    "requiredFields": [
                        "coreUnitsPerRetailWorldCoordinateUnit",
                        "speedEnvelopeSelectionRule",
                        "responseCurveToTickRule",
                        "releaseLatencyToTickRule",
                        "roundingMode",
                        "maximumQuantizationErrorCoreUnits",
                        "overflowBounds",
                    ],
                    "satisfied": False,
                },
                "replayTests": "rebuild/OnslaughtRebuild.Core.Tests/ReplayTests.cs",
                "replayTestCase": "FirstFlightReplay_IsDeterministicAndMatchesGoldenHash",
                "scenarioFile": "rebuild/scenarios/first-flight.v1.json",
                "headlessFile": "rebuild/OnslaughtRebuild.Headless/HeadlessApplication.cs",
                "headlessType": "HeadlessApplication",
                "headlessTests": "rebuild/OnslaughtRebuild.Core.Tests/HeadlessApplicationTests.cs",
                "headlessTestCase": "TapeGolden_IsCheckedAndVerified",
                "targetSetStatus": "open-blocked-translation-contract-incomplete",
            },
            report["futureCoreTargets"],
        )
        for constant in model.UNRESOLVED_CONSTANTS:
            self.assertIn(constant, rendered)

    def test_symbolic_forward_and_move_preserve_unresolved_constants(self) -> None:
        report = model.execute_fixture(model.generated_fixtures()[3])
        state = report["finalSymbolicState"]
        forward_velocity = next(event for event in report["events"] if event["action"] == "add-symbolic-velocity")
        self.assertIn("unresolvedSlowMovementFactor", forward_velocity["details"]["velocity"])
        self.assertIn("unresolvedDashVelocityMultiplier", forward_velocity["details"]["velocity"])
        self.assertEqual("unresolvedEnergyMaximum", state["energy"])
        self.assertIn("unresolvedDashLength", state["dash_count"])
        self.assertIn("unresolvedTwoPiSpan", state["walk_cycle"])
        self.assertIn("forward.trigger_dash", report["branches"])
        self.assertIn("move.speed_clamp", report["branches"])
        self.assertIn("walk.y_axis", report["branches"])
        self.assertIn("walk.upper_wrap", report["branches"])
        dash_miss = model.execute_fixture(model.generated_fixtures()[4])
        miss_event = next(event for event in dash_miss["events"] if event["action"] == "evaluate-reverse-start-window")
        self.assertFalse(miss_event["details"]["result"])

    def test_speed_clamp_preserves_source_short_circuit_order(self) -> None:
        within = model.execute_fixture(model.generated_fixtures()[0])
        actions = [event["action"] for event in within["events"]]
        self.assertIn("evaluate-horizontal-speed", actions)
        self.assertNotIn("evaluate-dash-friction-threshold", actions)
        self.assertNotIn("move.dash_clamp_gate_open", within["branches"])
        self.assertNotIn("move.dash_clamp_gate_closed", within["branches"])

        exceeds = model.execute_fixture(model.generated_fixtures()[-1])
        actions = [event["action"] for event in exceeds["events"]]
        self.assertLess(
            actions.index("evaluate-horizontal-speed"),
            actions.index("evaluate-dash-friction-threshold"),
        )

    def test_early_return_water_slide_and_idle_paths_are_modeled(self) -> None:
        airborne = model.execute_fixture(model.generated_fixtures()[1])
        self.assertIn("forward.airborne_return", airborne["branches"])
        self.assertIn("move.water", airborne["branches"])
        self.assertIn("move.no_walk_cycle", airborne["branches"])
        self.assertNotIn("add-symbolic-velocity", [event["action"] for event in airborne["events"]])

        dash_active = model.execute_fixture(model.generated_fixtures()[2])
        self.assertIn("forward.dash_active_return", dash_active["branches"])
        self.assertIn("move.slide", dash_active["branches"])
        self.assertIn("move.dash_decrement", dash_active["branches"])

    def test_two_water_checks_are_independent_and_ordered(self) -> None:
        base = model.generated_fixtures()[0]
        for outcomes in ((False, False), (False, True), (True, False), (True, True)):
            with self.subTest(outcomes=outcomes):
                fixture = replace(
                    base,
                    fixture_id=f"water-{int(outcomes[0])}-{int(outcomes[1])}",
                    move=replace(
                        base.move,
                        going_into_water_checks=outcomes,
                        should_slide=False,
                    ),
                )
                report = model.execute_fixture(fixture)
                checks = [
                    event for event in report["events"]
                    if event["action"] == "evaluate-going-into-water"
                ]
                self.assertEqual([1, 2], [event["details"]["occurrence"] for event in checks])
                self.assertEqual(list(outcomes), [event["details"]["result"] for event in checks])
                self.assertEqual(not outcomes[1], "move.friction" in report["branches"])
                self.assertEqual(
                    outcomes[0],
                    "zero-horizontal-velocity" in [event["action"] for event in report["events"]],
                )

    def test_serialized_fixture_state_accounts_for_every_trace_control(self) -> None:
        base = model.generated_fixtures()[0]
        report = model.execute_fixture(base)

        def leaf_paths(value: object, prefix: str = "") -> set[str]:
            if isinstance(value, dict):
                return {
                    path
                    for key, item in value.items()
                    for path in leaf_paths(item, f"{prefix}.{key}" if prefix else key)
                }
            return {prefix}

        self.assertEqual(
            set(model.SOURCE_SHAPED_FIXTURE_INPUTS),
            leaf_paths(report["initialInputsAndState"]),
        )
        changed = replace(
            base,
            move=replace(
                base.move,
                current_weapon_present=False,
                player_present=False,
                shields_recharging_before_move=False,
            ),
        )
        changed_report = model.execute_fixture(changed)
        self.assertNotEqual(
            report["initialInputsAndState"],
            changed_report["initialInputsAndState"],
        )
        self.assertNotEqual(report["branches"], changed_report["branches"])

    def test_invalid_and_nondeterministic_branch_fixtures_fail_closed(self) -> None:
        base = model.generated_fixtures()[0]
        cases = (
            (replace(base, fixture_id=r"C:\private\fixture"), "private path"),
            (replace(base, dash_count=-1), "dash count"),
            (replace(base, move=replace(base.move, going_into_water_checks=(False,))), "water checks"),
            (replace(base, move=replace(base.move, going_into_water_checks=(False, 1))), "water checks"),
            (replace(base, battleengine_state="jet"), "walker-path state"),
            (replace(base, grounded_at_forward=False, forward=model.ForwardBranches(True, False, False)), "unreachable Forward"),
            (replace(base, forward=model.ForwardBranches(False, False, True)), "dash-window"),
            (replace(base, move=replace(base.move, going_into_water_checks=(True, True), should_slide=True)), "slide"),
            (replace(base, move=replace(base.move, recent_ground=False, recharge_exceeds_capacity=True)), "energy-cap"),
            (
                replace(
                    base,
                    move=replace(
                        base.move,
                        going_into_water_checks=(False, True),
                        horizontal_speed_exceeds_max=True,
                        dash_below_friction_threshold=True,
                    ),
                ),
                "unreachable speed-clamp",
            ),
            (
                replace(
                    base,
                    move=replace(
                        base.move,
                        going_into_water_checks=(True, False),
                        horizontal_speed_exceeds_max=True,
                        dash_below_friction_threshold=True,
                    ),
                ),
                "unreachable speed-clamp",
            ),
            (
                replace(base, move=replace(base.move, dash_below_friction_threshold=True)),
                "dead dash-friction",
            ),
            (replace(base, walk_cycle=None), "walk-cycle"),
            (
                replace(
                    base,
                    walk_cycle=model.WalkCycleBranches(True, True, True),
                ),
                "impossible walk-cycle wrap",
            ),
        )
        for fixture, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(model.ModelError, message):
                model.execute_fixture(fixture)

    def test_rendering_is_path_free_canonical_and_deterministic(self) -> None:
        report = model.execute_catalog()
        first = model.render_report(report)
        second = model.render_report(model.execute_catalog())
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertEqual(hashlib.sha256(first).hexdigest(), hashlib.sha256(second).hexdigest())
        rendered = first.decode("utf-8")
        self.assertNotIn(str(Path.cwd()), rendered)
        self.assertNotRegex(rendered, r"[A-Za-z]:[\\/]")

        leaked = dict(report)
        leaked["leak"] = r"C:\Users\private\capture.log"
        with self.assertRaisesRegex(model.ModelError, "private path"):
            model.render_report(leaked)
        for absolute in (
            r"\\server\share\private.log",
            r"\\?\C:\private.log",
            r"\\.\pipe\private",
            "/dev/null",
            "/proc/self/maps",
            "/etc/passwd",
            "/var/log/private.log",
            "/root/.ssh/config",
            "file:///private.log",
        ):
            with self.subTest(absolute=absolute), self.assertRaisesRegex(model.ModelError, "private path"):
                model.render_report({"leak": absolute})

        promoted = model.execute_fixture(model.generated_fixtures()[0])
        promoted["futureCoreTargets"]["translationContract"]["satisfied"] = True
        with self.assertRaisesRegex(model.ModelError, "Core target|translation"):
            model.render_report(promoted)

        promoted_catalog = model.execute_catalog()
        promoted_catalog["fixtures"][0]["futureCoreTargets"]["targetSetStatus"] = "closed"
        with self.assertRaisesRegex(model.ModelError, "Core target|translation"):
            model.render_report(promoted_catalog)

        promoted_event = model.execute_fixture(model.generated_fixtures()[0])
        forward_event = next(
            event for event in promoted_event["events"]
            if event["call"] == "CBattleEngineWalkerPart::Forward"
        )
        forward_event["evidence"] = "steamStatic"
        promoted_event["finalSymbolicState"]["velocity"] = "123.0"
        with self.assertRaisesRegex(model.ModelError, "canonical|mutation"):
            model.render_report(promoted_event)

        promoted_catalog_event = model.execute_catalog()
        promoted_catalog_event["fixtures"][0]["events"][0]["evidence"] = "steamStatic"
        with self.assertRaisesRegex(model.ModelError, "canonical|mutation"):
            model.render_report(promoted_catalog_event)

    def test_custom_manifest_cannot_authorize_rebuild_behavior(self) -> None:
        promoted = model.evidence_manifest()
        promoted["rebuildContract"][0]["authorizedBehaviorChange"] = True
        with self.assertRaisesRegex(model.ModelError, "promotion|mutation|authorization"):
            model.execute_fixture(model.generated_fixtures()[0], manifest=promoted)

    def test_future_core_targets_are_fresh_and_nested_tampering_is_rejected(self) -> None:
        first = model.execute_fixture(model.generated_fixtures()[0])
        tampered = first["futureCoreTargets"]
        tampered["translationContract"]["satisfied"] = True
        tampered["targetSetStatus"] = "closed"
        with self.assertRaisesRegex(model.ModelError, "Core target|translation"):
            model.validate_future_core_targets(tampered)

        report = model.execute_fixture(model.generated_fixtures()[0])
        self.assertFalse(report["futureCoreTargets"]["translationContract"]["satisfied"])
        self.assertEqual(
            "open-blocked-translation-contract-incomplete",
            report["futureCoreTargets"]["targetSetStatus"],
        )


if __name__ == "__main__":
    unittest.main()
