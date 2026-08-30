#!/usr/bin/env python3
"""Focused tests for the Generation-32 Linux host attestor."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "re_campaign_gen32_host_attestation.py"
SPEC = importlib.util.spec_from_file_location("gen32_host_attestation", SCRIPT)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import bootstrap
    raise RuntimeError(f"cannot import {SCRIPT}")
host = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = host
SPEC.loader.exec_module(host)

REPO = TOOLS.parent
LAB = Path("/home/xsniper80/ProjectData/Onslaught/local-lab")
CAMPAIGN = LAB / host.GEN32_RELATIVE
AUTHORITY = LAB / host.GEN32_AUTHORITY_RELATIVE


def command(*, mode: str = "full", ready_sha: str = host.GEN32_READY_SHA256) -> list[str]:
    return [
        sys.executable,
        "-I",
        "-B",
        os.fspath(SCRIPT),
        "--campaign",
        os.fspath(CAMPAIGN),
        "--repo-root",
        os.fspath(REPO),
        "--lab-root",
        os.fspath(LAB),
        "--authority",
        os.fspath(AUTHORITY),
        "--expected-ready-sha256",
        ready_sha,
        "--expected-reducer-id",
        host.GEN32_REDUCER_ID,
        "--expected-authority-sha256",
        host.GEN32_AUTHORITY_SHA256,
        "--mode",
        mode,
    ]


class Gen32HostAttestationUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="gen32-host-unit-")
        root = Path(self.temporary.name)
        self.repo = root / "repo"
        self.lab = root / "lab"
        self.repo.mkdir()
        self.lab.mkdir()
        (self.repo / "reverse-engineering").mkdir()
        (self.repo / "reverse-engineering" / "tracked.tsv").write_text("tracked\n")
        (self.lab / "proof").mkdir()
        (self.lab / "proof" / "ready.json").write_text("{}\n")
        self.paths = host.HostPaths(self.repo, self.lab)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_exact_legacy_relative_and_physical_forms_bind_to_authorized_roots(self) -> None:
        logical_lab = host.WINDOWS_REPO_PREFIX + "local-lab\\proof\\ready.json"
        logical_repo = host.WINDOWS_REPO_PREFIX + "reverse-engineering\\tracked.tsv"
        self.assertEqual(
            self.paths.resolve(logical_lab),
            self.lab / "proof" / "ready.json",
        )
        self.assertEqual(
            self.paths.resolve("local-lab\\proof\\ready.json"),
            self.lab / "proof" / "ready.json",
        )
        self.assertEqual(
            self.paths.resolve(logical_repo),
            self.repo / "reverse-engineering" / "tracked.tsv",
        )
        self.assertEqual(
            self.paths.resolve(self.lab / "proof" / "ready.json"),
            self.lab / "proof" / "ready.json",
        )

    def test_foreign_unc_traversal_mixed_and_same_suffix_paths_are_rejected(self) -> None:
        rejected = (
            r"D:\local-lab\proof\ready.json",
            r"C:local-lab\proof\ready.json",
            r"\\server\share\ready.json",
            host.WINDOWS_REPO_PREFIX + r"local-lab\..\proof\ready.json",
            host.WINDOWS_REPO_PREFIX + r"local-lab/proof/ready.json",
            "/tmp/proof/ready.json",
            r"local-lab\proof/ready.json",
        )
        for raw in rejected:
            with self.subTest(raw=raw), self.assertRaises(host.AttestationError):
                self.paths.resolve(raw)

    def test_symlink_and_hardlink_controls_fail_closed(self) -> None:
        (self.lab / "linked-proof").symlink_to(self.lab / "proof", target_is_directory=True)
        with self.assertRaises(host.AttestationError):
            self.paths.resolve("local-lab/linked-proof/ready.json")
        first = self.lab / "proof" / "ready.json"
        second = self.lab / "proof" / "hardlink.json"
        os.link(first, second)
        with self.assertRaises(host.AttestationError):
            host._require_plain_file(first, "hardlinked pin")
        router = host.BuilderRoutingRoot(self.paths, {"local-lab/proof/ready.json"})
        with self.assertRaises(host.AttestationError):
            router / "local-lab/proof/ready.json"

    def test_builder_router_admits_only_closure_and_sealed_receipt_sources(self) -> None:
        closure = self.repo / Path(host.CLOSURE_RELATIVE)
        closure.parent.mkdir(parents=True)
        closure.write_text("closure\n")
        source = "local-lab/proof/ready.json"
        router = host.BuilderRoutingRoot(self.paths, {source})
        self.assertEqual(router / host.CLOSURE_RELATIVE, closure)
        self.assertEqual(router / source, self.lab / "proof" / "ready.json")
        with self.assertRaises(host.AttestationError):
            router / "local-lab/proof/unsealed.json"

    def test_schema_normalization_is_exactly_leaf_allowlisted(self) -> None:
        receipt = json.loads((CAMPAIGN / "campaign.ready.json").read_text())
        campaign_api = SimpleNamespace(
            GENERATION32_STATIC_RECEIPT_RESEAT_ADVANCE_KIND=(
                "GENERATION32_STATIC_RECEIPT_RESEAT"
            ),
            GENERATION32_STATIC_RECEIPT_RESEAT_ADVANCE_SCHEMA=(
                "bea.re.generation32-static-receipt-reseat-advance.v1"
            ),
        )
        real_paths = host.HostPaths(REPO, LAB)
        source = receipt["sourceSnapshot"]
        source["untrustedExtra"] = {"path": r"D:\must-remain-logical"}
        normalized_source = host._normalized_campaign_field(
            real_paths, campaign_api, "sourceSnapshot", source
        )
        self.assertEqual(
            normalized_source["parityGraph"]["program"]["executablePath"],
            source["parityGraph"]["program"]["executablePath"],
        )
        self.assertEqual(
            normalized_source["untrustedExtra"]["path"],
            r"D:\must-remain-logical",
        )
        normalized_advance = host._normalized_campaign_field(
            real_paths, campaign_api, "advance", receipt["advance"]
        )
        self.assertEqual(
            normalized_advance["sealedClosure"]["path"],
            host.CLOSURE_RELATIVE,
        )
        self.assertEqual(
            normalized_advance["rows"][0]["receiptSources"],
            receipt["advance"]["rows"][0]["receiptSources"],
        )
        self.assertTrue(Path(normalized_advance["snapshot"]["path"]).is_absolute())

    def test_wrong_external_pin_blocks_before_frozen_import(self) -> None:
        completed = subprocess.run(
            command(mode="integrity", ready_sha="0" * 64),
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(completed.returncode, 10)
        self.assertIn("GEN32_LINUX_HOST_ATTESTATION_BLOCKED", completed.stderr)
        self.assertNotIn("CAMPAIGN_HOST_REPLAY_VERIFIED", completed.stdout)

    def test_integrity_mode_never_prints_or_writes_full_replay_authority(self) -> None:
        completed = subprocess.run(
            command(mode="integrity"),
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("CAMPAIGN_HOST_INTEGRITY_VERIFIED", completed.stdout)
        self.assertNotIn("CAMPAIGN_HOST_REPLAY_VERIFIED", completed.stdout)

    def test_preloaded_manifest_module_is_rejected(self) -> None:
        receipt = {
            "reducer": {
                "files": [
                    {"path": "_reducer/tools/synthetic_owned_module.py"},
                ]
            }
        }
        sentinel = object()
        sys.modules["synthetic_owned_module"] = sentinel
        try:
            with self.assertRaises(host.AttestationError):
                host._reject_preloaded_manifest_modules(receipt)
        finally:
            del sys.modules["synthetic_owned_module"]


class Gen32HostAttestationIntegrationTests(unittest.TestCase):
    def test_real_gen32_full_replay_verifies_without_mutating_critical_inputs(self) -> None:
        receipt = json.loads((CAMPAIGN / "campaign.ready.json").read_text())
        paths = host.HostPaths(REPO, LAB)
        selected = host._critical_inputs(
            paths,
            CAMPAIGN,
            LAB / host.GEN32_REPLICA_RELATIVE,
            AUTHORITY,
            receipt,
            REPO / host.BOOTSTRAP_RELATIVE,
        )
        before = host._critical_fingerprint(selected)
        completed = subprocess.run(
            command(),
            text=True,
            capture_output=True,
            check=False,
            timeout=900,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("CAMPAIGN_HOST_REPLAY_VERIFIED", completed.stdout)
        self.assertNotIn("CAMPAIGN_VERIFIED", completed.stdout)
        self.assertNotIn("ATTESTATION_BLOCKED", completed.stderr)
        after = host._critical_fingerprint(selected)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
