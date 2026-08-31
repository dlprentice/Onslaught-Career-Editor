#!/usr/bin/env python3
"""Focused topology tests for the frozen UnsetObjective proof verifier."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

try:
    import re_mission_native_unsetobjective_reproof as proof
except ModuleNotFoundError:  # supports ``python -m unittest`` from repository root
    from tools import re_mission_native_unsetobjective_reproof as proof


class MissionNativeUnsetObjectiveReproofTests(unittest.TestCase):
    def test_explicit_fresh_restore_is_accepted_as_a_route(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            restored = Path(temporary) / "restored-project"
            restored.mkdir()
            self.assertEqual(
                restored.resolve(),
                proof.restored_project_root(proof.repo_root(), restored),
            )

    def test_active_and_tracked_projects_are_forbidden(self) -> None:
        root = proof.repo_root()
        for relative in (
            proof.ACTIVE_MUTABLE_PROJECT_RELATIVE,
            proof.TRACKED_CHECKPOINT_RELATIVE,
        ):
            with self.subTest(relative=relative):
                with self.assertRaisesRegex(proof.ProofError, "must not consume"):
                    proof.restored_project_root(root, root / relative)

    def test_sealed_package_must_not_be_opened_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "package"
            candidate = package / "tree"
            candidate.mkdir(parents=True)
            with patch.object(proof, "COLD_PACKAGE_PARENT", package):
                with self.assertRaisesRegex(proof.ProofError, "sealed recovery"):
                    proof.restored_project_root(proof.repo_root(), candidate)

    def test_build_command_is_a_frozen_one_shot_refusal(self) -> None:
        output = io.StringIO()
        with redirect_stderr(output):
            result = proof.main(["build"])
        self.assertEqual(2, result)
        self.assertIn("one-shot proof is frozen", output.getvalue())


if __name__ == "__main__":
    unittest.main()
