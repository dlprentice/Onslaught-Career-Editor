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
from unittest import mock


TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "re_campaign_gen32_host_attestation.py"
SPEC = importlib.util.spec_from_file_location("gen32_host_attestation", SCRIPT)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import bootstrap
    raise RuntimeError(f"cannot import {SCRIPT}")
host = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = host
SPEC.loader.exec_module(host)

REPO = Path("/home/xsniper80/Projects/game-dev/Onslaught-Career-Editor")
LAB = REPO / "local-lab"
CAMPAIGN = LAB / host.GEN32_RELATIVE
AUTHORITY = LAB / host.GEN32_AUTHORITY_RELATIVE
ATTESTATION_ROOT = Path("/home/xsniper80/Projects/game-dev/Onslaught-Career-Editor/local-data/host-attestations")


def directory_fingerprint(root: Path) -> tuple[tuple[str, int, int, int], ...]:
    return tuple(
        (entry.name, info.st_mode, info.st_size, info.st_mtime_ns)
        for entry in sorted(root.iterdir(), key=lambda value: value.name)
        for info in (entry.lstat(),)
    )


def command(
    *,
    mode: str = "full",
    ready_sha: str = host.GEN32_READY_SHA256,
    attestation_root: Path = ATTESTATION_ROOT,
) -> list[str]:
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
        "--attestation-root",
        os.fspath(attestation_root),
    ]


class Gen32HostAttestationUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="gen32-host-unit-")
        root = Path(self.temporary.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        self.lab = self.repo / "local-lab"
        self.lab.mkdir()
        self.retired_lab = root / "retired-projectdata-local-lab"
        self.machine_route_patches = (
            mock.patch.object(host, "CANONICAL_REPO_ROOT", self.repo),
            mock.patch.object(host, "CANONICAL_LAB_ROOT", self.lab),
            mock.patch.object(
                host,
                "RETIRED_PROJECTDATA_LAB_ROOT",
                self.retired_lab,
            ),
        )
        for patcher in self.machine_route_patches:
            patcher.start()
        (self.repo / "reverse-engineering").mkdir()
        (self.repo / "reverse-engineering" / "tracked.tsv").write_text("tracked\n")
        (self.lab / "proof").mkdir()
        (self.lab / "proof" / "ready.json").write_text("{}\n")
        self.paths = host.HostPaths(self.repo, self.lab)

    def tearDown(self) -> None:
        for patcher in reversed(self.machine_route_patches):
            patcher.stop()
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

    def test_lab_root_must_be_the_plain_repo_local_directory(self) -> None:
        external = Path(self.temporary.name) / "external-lab"
        external.mkdir()
        with self.assertRaisesRegex(
            host.AttestationError,
            "not the canonical plain repository-local directory",
        ):
            host.HostPaths(self.repo, external)

        second_repo = Path(self.temporary.name) / "second-repo"
        second_repo.mkdir()
        (second_repo / "local-lab").symlink_to(external, target_is_directory=True)
        with (
            mock.patch.object(host, "CANONICAL_REPO_ROOT", second_repo),
            mock.patch.object(
                host,
                "CANONICAL_LAB_ROOT",
                second_repo / "local-lab",
            ),
            self.assertRaisesRegex(host.AttestationError, "traverses a symlink"),
        ):
            host.HostPaths(second_repo, second_repo / "local-lab")

    def test_machine_authority_rejects_alternate_repo_and_retired_lab_twin(self) -> None:
        alternate_repo = Path(self.temporary.name) / "alternate-repo"
        alternate_lab = alternate_repo / "local-lab"
        alternate_lab.mkdir(parents=True)
        with self.assertRaisesRegex(
            host.AttestationError,
            "not the exact current machine authority",
        ):
            host.HostPaths(alternate_repo, alternate_lab)

        self.retired_lab.mkdir()
        with self.assertRaisesRegex(host.AttestationError, "must remain absent"):
            host.HostPaths(self.repo, self.lab)
        self.retired_lab.rmdir()
        self.retired_lab.symlink_to(self.lab, target_is_directory=True)
        with self.assertRaisesRegex(host.AttestationError, "must remain absent"):
            host.HostPaths(self.repo, self.lab)

    def test_durable_output_owner_is_explicit_and_never_derived_from_lab(self) -> None:
        self.assertEqual(host.HOST_ATTESTATIONS_ROOT, ATTESTATION_ROOT)
        expected = ATTESTATION_ROOT / "unit-test-never-written.json"
        self.assertEqual(
            host._authorized_attestation_path(expected, ATTESTATION_ROOT),
            expected,
        )
        implicit_repo_output = self.lab.parent / "host-attestations" / expected.name
        with self.assertRaisesRegex(
            host.AttestationError,
            "explicit ProjectData route",
        ):
            host._authorized_attestation_path(
                implicit_repo_output,
                self.lab.parent / "host-attestations",
            )
        with self.assertRaisesRegex(
            host.AttestationError,
            "must be directly below",
        ):
            host._authorized_attestation_path(
                ATTESTATION_ROOT / "nested" / expected.name,
                ATTESTATION_ROOT,
            )
        with self.assertRaisesRegex(host.AttestationError, "contains traversal"):
            host._authorized_attestation_path(
                ATTESTATION_ROOT / "nested" / ".." / expected.name,
                ATTESTATION_ROOT,
            )
        with self.assertRaisesRegex(host.AttestationError, "contains traversal"):
            host._authorized_attestation_root(
                ATTESTATION_ROOT / "nested" / "..",
            )

    def test_durable_writer_is_atomic_and_refuses_existing_or_linked_owners(self) -> None:
        output_root = Path(self.temporary.name) / "projectdata" / "host-attestations"
        output_root.mkdir(parents=True)
        output = output_root / "attestation.json"
        value = {"schema": "unit", "verdict": "VERIFIED"}
        payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
        with mock.patch.object(host, "HOST_ATTESTATIONS_ROOT", output_root):
            digest = host._write_new_attestation(output, value, output_root)
            self.assertEqual(digest, host.hashlib.sha256(payload).hexdigest())
            self.assertEqual(output.read_bytes(), payload)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(host.AttestationError, "refusing existing"):
                host._write_new_attestation(output, value, output_root)

            linked_output = output_root / "linked.json"
            linked_output.symlink_to(output_root / "absent-target.json")
            with self.assertRaisesRegex(host.AttestationError, "refusing existing"):
                host._write_new_attestation(linked_output, value, output_root)

        real_root = Path(self.temporary.name) / "real-attestation-root"
        real_root.mkdir()
        linked_root = Path(self.temporary.name) / "linked-attestation-root"
        linked_root.symlink_to(real_root, target_is_directory=True)
        with mock.patch.object(host, "HOST_ATTESTATIONS_ROOT", linked_root):
            with self.assertRaisesRegex(host.AttestationError, "traverses a symlink"):
                host._write_new_attestation(
                    linked_root / "attestation.json",
                    value,
                    linked_root,
                )

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
        with (
            mock.patch.object(host, "CANONICAL_REPO_ROOT", REPO),
            mock.patch.object(host, "CANONICAL_LAB_ROOT", LAB),
            mock.patch.object(
                host,
                "RETIRED_PROJECTDATA_LAB_ROOT",
                Path("/home/xsniper80/ProjectData/Onslaught/local-lab"),
            ),
        ):
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

    def test_foreign_attestation_root_blocks_before_frozen_import(self) -> None:
        completed = subprocess.run(
            command(
                mode="integrity",
                attestation_root=self.repo / "host-attestations",
            ),
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(completed.returncode, 10)
        self.assertIn("explicit ProjectData route", completed.stderr)
        self.assertNotIn("CAMPAIGN_HOST_INTEGRITY_VERIFIED", completed.stdout)

    def test_integrity_mode_never_prints_or_writes_full_replay_authority(self) -> None:
        before = directory_fingerprint(ATTESTATION_ROOT)
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
        self.assertEqual(before, directory_fingerprint(ATTESTATION_ROOT))

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
        attestation_before = directory_fingerprint(ATTESTATION_ROOT)
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
        self.assertEqual(
            attestation_before,
            directory_fingerprint(ATTESTATION_ROOT),
        )


if __name__ == "__main__":
    unittest.main()
