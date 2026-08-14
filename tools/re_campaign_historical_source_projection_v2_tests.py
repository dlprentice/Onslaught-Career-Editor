#!/usr/bin/env python3
"""Focused tests for the current Generation 24 historical-input projection."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


TOOL_PATH = Path(__file__).resolve().with_name(
    "re_campaign_historical_source_projection_v2.py"
)
TOOL_SPEC = importlib.util.spec_from_file_location(
    "_bea_re_campaign_historical_source_projection_v2", TOOL_PATH
)
if TOOL_SPEC is None or TOOL_SPEC.loader is None:
    raise RuntimeError("cannot load historical source projection v2")
projection = importlib.util.module_from_spec(TOOL_SPEC)
TOOL_SPEC.loader.exec_module(projection)


TOOL_BYTES = 23_336
TOOL_SHA256 = (
    "4e57dd93e26d4706a4b49e3c6f11909a0abf57c43f061838c70896baf9ca8946"
)
GEN24_CAMPAIGN = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-24-current-8280-reseed-e7aa-v1"
)
GEN24_READY_SHA256 = (
    "29ac9d91136c88a651fe5bc2202ca14d9c3a8dc7bd733e1cb7396c4c32a39e86"
)
GEN24_REDUCER_ID = (
    "6cf37430cf7ddace01088aa21a8732943e027f621b54fdf52c9be002dd284582"
)
REPARSE_ATTRIBUTE = 0x400


class HistoricalSourceProjectionV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parent.parent
        cls.tool = Path(projection.__file__).resolve()

    def test_tool_and_continuity_inputs_are_exact(self) -> None:
        data = self.tool.read_bytes()
        self.assertEqual(TOOL_BYTES, len(data))
        self.assertEqual(TOOL_SHA256, hashlib.sha256(data).hexdigest())

        old_owner = projection._load_old_owner(self.repo)
        historical_player, player = old_owner.validate_continuity(self.repo)
        actor_projection, actor = projection.validate_actor_continuity(
            self.repo, old_owner
        )
        self.assertEqual(old_owner.HISTORICAL_TEST_SHA256,
                         hashlib.sha256(historical_player).hexdigest())
        self.assertEqual(
            projection.ACTOR_RUNTIME_HISTORICAL_SHA256,
            hashlib.sha256(
                actor_projection[projection.ACTOR_RUNTIME_RELATIVE]
            ).hexdigest(),
        )
        self.assertEqual(
            projection.ACTOR_TEST_HISTORICAL_SHA256,
            hashlib.sha256(
                actor_projection[projection.ACTOR_TEST_RELATIVE]
            ).hexdigest(),
        )
        self.assertTrue(player["relationship"]["historicalLinesRetainedInOrder"])
        self.assertEqual(
            "EXACT_REVIEWED_HELPER_EXTRACTION",
            actor["runtimeRelationship"]["classification"],
        )
        self.assertTrue(actor["testRelationship"]["normalizedByteIdentical"])

    def test_current_runtime_identity_drift_is_rejected(self) -> None:
        old_owner = projection._load_old_owner(self.repo)
        with patch.object(
            projection, "ACTOR_RUNTIME_CURRENT_SHA256", "0" * 64
        ):
            with self.assertRaisesRegex(
                projection.ProjectionError,
                "current actor-weapon runtime identity differs",
            ):
                projection.validate_actor_continuity(self.repo, old_owner)

    def test_bootstrap_detection_is_path_separator_independent(self) -> None:
        detected = projection.is_bootstrap_invocation(
            [
                sys.executable,
                "-I",
                "-B",
                r"C:\proof\tools\re_campaign_frozen_bootstrap.py",
                "--mode",
                "full",
            ]
        )
        self.assertIsNotNone(detected)
        assert detected is not None
        self.assertEqual(3, detected[1])
        self.assertIsNone(
            projection.is_bootstrap_invocation(
                [sys.executable, "tools/re_campaign.py", "verify"]
            )
        )

    def test_current_focused_rebuild_contracts_pass(self) -> None:
        old_owner = projection._load_old_owner(self.repo)
        result = projection.validate_current(self.repo, old_owner)
        self.assertEqual(30, result["focusedRebuild"]["passed"])
        self.assertEqual(0, result["focusedRebuild"]["failed"])
        self.assertTrue(
            result["frozenPlayerDamageProof"][
                "currentIdentityRejectedByExactInputGate"
            ]
        )

    def test_full_generation24_replay_when_evidence_is_local(self) -> None:
        campaign = self.repo / GEN24_CAMPAIGN
        if not (campaign / "campaign.ready.json").is_file():
            self.skipTest("retained Generation 24 evidence is unavailable")
        local_lab = self.repo / "local-lab"
        stat = local_lab.lstat()
        if local_lab.is_symlink() or (
            getattr(stat, "st_file_attributes", 0) & REPARSE_ATTRIBUTE
        ):
            self.skipTest("retained evidence is exposed through a reparse point")

        environment = os.environ.copy()
        cwd = Path.cwd()
        output = io.StringIO()
        try:
            os.environ["BEA_REPO_ROOT"] = os.fspath(self.repo)
            os.chdir(self.repo)
            with contextlib.redirect_stdout(output):
                exit_code = projection.main(
                    [
                        "--campaign",
                        os.fspath(GEN24_CAMPAIGN),
                        "--mode",
                        "full",
                        "--expected-ready-sha256",
                        GEN24_READY_SHA256,
                        "--expected-reducer-id",
                        GEN24_REDUCER_ID,
                    ]
                )
        finally:
            os.chdir(cwd)
            os.environ.clear()
            os.environ.update(environment)
        self.assertEqual(0, exit_code)
        self.assertIn("CAMPAIGN_VERIFIED", output.getvalue())
        self.assertIn("projected=3", output.getvalue())


if __name__ == "__main__":
    unittest.main()
