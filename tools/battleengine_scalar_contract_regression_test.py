#!/usr/bin/env python3
"""Tests for landed scalar contract regression checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import battleengine_scalar_contract_regression as reg


class LandedContractRegressionTests(unittest.TestCase):
    def test_real_walker_and_jet_contracts_pass(self) -> None:
        reports = reg.validate_all_landed_contracts()
        self.assertEqual(2, len(reports))
        schemas = {row["schemaVersion"] for row in reports}
        self.assertIn("battleengine-walker-forward-scalar-response.v2", schemas)
        self.assertIn("battleengine-jet-forward-scalar-response.v1", schemas)
        for row in reports:
            speeds = row["steadySpeeds"]
            self.assertEqual(2, len(speeds))
            self.assertTrue(all(speed > 0 for speed in speeds))

    def test_cli_main_passes_on_real_contracts(self) -> None:
        code = reg.main([])
        self.assertEqual(0, code)

    def test_rejects_broken_envelope(self) -> None:
        good = json.loads(reg.CONTRACTS[0].read_text(encoding="utf-8"))
        good["envelope"]["steadySpeed"] = {"lower": 10.0, "upper": 11.0}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(json.dumps(good), encoding="utf-8")
            with self.assertRaisesRegex(reg.ContractRegressionError, "outside envelope"):
                reg.validate_landed_scalar_contract(path)


if __name__ == "__main__":
    unittest.main()
