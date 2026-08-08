#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Own the one-shot live Ghidra promotion of the five target-lock contracts.

This owner is deliberately specimen-, project-, proof-, tool-, and cohort-
specific. ``prepare`` is read-only and creates two disjoint, reopened PRE
copies. ``promote`` can spawn one fixed semantic mutator exactly once, then
classifies and reads the project back in separate processes and creates two
disjoint reopened POST copies. ``recover-status`` only observes; it never
restores or retries.
"""

from __future__ import annotations

import argparse
import base64
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from ctypes import wintypes
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Mapping, Sequence


TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
OWNER_ROOT = REPO / "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2"
LIVE_PROJECT = Path(r"C:\Users\david\Ghidra\Projects")
PROJECT_NAME = "BEA"
PROGRAM_NAME = "BEA.exe"
MUTEX_NAME = "Local\\OnslaughtToolkit.BEA.Ghidra.LivePromotion.v1"

SCHEMA = "bea.re.ghidra-target-lock-semantic-live-promotion.v1"
PREPARED_SCHEMA = "bea.re.ghidra-target-lock-semantic-live-prepared.v1"
OBSERVATION_SCHEMA = "bea.re.ghidra-target-lock-semantic-live-observation.v1"
ATTEMPT_SCHEMA = "bea.re.ghidra-target-lock-semantic-live-attempt.v1"
RECOVERY_SCHEMA = "bea.re.ghidra-target-lock-semantic-live-recovery.v1"
LAUNCH_GATE_SCHEMA = "bea.re.ghidra-target-lock-semantic-live-launch-gate.v1"
PROCESS_CONTEXT_SCHEMA = "bea.re.ghidra-target-lock-process-context.v1"
EXECUTION_BUNDLE_SCHEMA = "bea.re.ghidra-target-lock-execution-bundle.v1"
EXECUTION_BUNDLE_SEAL_SCHEMA = "bea.re.ghidra-target-lock-execution-bundle-seal.v1"
EXTERNAL_LAUNCHER_SHA256_ENV = "BEA_TARGET_LOCK_REVIEWED_LAUNCHER_SHA256"

CAMPAIGN = REPO / "local-lab/ghidra-target-lock-semantic-promotion-20260803-v1"
PLAN = CAMPAIGN / "lock-five-semantic-plan-v3.candidate.tsv"
EVIDENCE = CAMPAIGN / "lock-five-semantic-evidence-v1.candidate.tsv"
SCRIPT_SOURCE_BUNDLE_MANIFEST = CAMPAIGN / "ghidra-script-source-bundle-v1.tsv"
SEMANTIC_TOOL = TOOLS / "GhidraApplyTargetLockCorrections.java"
INVENTORY_TOOL = TOOLS / "ExportFullFunctionInventory.java"
BACKUP_TOOL = TOOLS / "ghidra_project_backup.py"
OWNER_TESTS = TOOLS / "ghidra_target_lock_semantic_live_promotion_tests.py"
LAUNCHER = TOOLS / "ghidra_target_lock_semantic_live_launcher.py"
PROCESS_HELPER = TOOLS / "ghidra_function_envelope_proof.py"
# Repinned 2026-08-07: canary/poison TSV re-point to byte-verified
# formal-function-envelope-canary-20260803-v3/inputs (eight-way review
# adjudication; same change as the atomic14 owner). Not tampering.
PROCESS_HELPER_SHA256 = "fdf80237d642db1a2d92213048424f06a4fb0ae614f8e7db6c3bd39210e707a5"

PROOF_ROOT = REPO / "local-lab/ghidra-target-lock-semantic-proof-20260804-v2-r5"
PROOF_OWNER = TOOLS / "ghidra_target_lock_semantic_proof.py"
PROOF_TESTS = TOOLS / "ghidra_target_lock_semantic_proof_tests.py"
PROOF_READY = PROOF_ROOT / "proof.ready.json"
PROOF_CORE = PROOF_ROOT / "proof.core.json"
PROOF_SUBJECT = PROOF_ROOT / "refuter-subject.json"
PROOF_REFUTER = PROOF_ROOT / "refuter.json"

BASELINE_PROJECT = CAMPAIGN / "scratch/replica-b"
BASELINE_FILE_COUNT = 19
BASELINE_TOTAL_BYTES = 186_387_333
BASELINE_FILESET_SHA256 = "309ba7f6fcf6a0d8ecdbd2803c0d7a1279a3d3027b7ee219efbbb0312e1143ab"

PLAN_SHA256 = "f6556238580a8d54b95e5603cd41e70313cebe7a9c92dff45687db7d21bc73c9"
EVIDENCE_SHA256 = "16c07f34feb374067ea19a9019da1f1a648778338d905928e989eced506e7ebc"
SCRIPT_SOURCE_BUNDLE_MANIFEST_SHA256 = (
    "e544317c7f63c25814db407fd23f99489154797d87a1ed5b5237262cbf14466d"
)
SCRIPT_SOURCE_BUNDLE = (
    34, 379_861, "e544317c7f63c25814db407fd23f99489154797d87a1ed5b5237262cbf14466d"
)
SEMANTIC_TOOL_SHA256 = "d3ab355408a70f66032f9a671c846ccf63d154fcd703d1ce20ee7a66396d4485"
INVENTORY_TOOL_SHA256 = "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"
# Repinned 2026-08-07: exFAT hard-link fallback + BOM-free probe sentinel
# fixes (tools/ghidra_project_backup.py 4f60e0c6, verified end-to-end on the
# F:\ pre/post-pilot backups). Adjudicated by the eight-way review. Not
# tampering.
BACKUP_TOOL_SHA256 = "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58"
OWNER_TESTS_SHA256 = "30c844ef27c694d2a44319d1812b2b998203716707a0bb658a87070745552188"
REVIEWED_TEST_COUNT = 67

# Repinned 2026-08-07: Opus effort default made fail-closed
# ('medium' unless review_id == 'opus-max') per the standing pin. Adjudicated
# by the eight-way review. Not tampering.
PROOF_OWNER_SHA256 = "753eadcb4f807a30d75c4cab50dca902528d22b581af9c15d987ccb11cce536d"
PROOF_TESTS_SHA256 = "029f2fad9d37038707ad3d626d3907df85837ca37ae90b698f78265dd331cace"
PROOF_READY_SHA256 = "f7c4220bdf5dfa6040bad23b11d3253ddeecea47f86b6ee238a28a4280987968"
PROOF_CORE_SHA256 = "c981402649f3e41fe0fd039329953958451cea6d75c7d9594a593bb2db4ec782"
PROOF_SUBJECT_SHA256 = "6c7ac187a086e3f5db9e1166ef05e55596358cf8130d4ee5e3189592b650c7d9"
PROOF_REFUTER_SHA256 = "0e8ff14be0f97516d8cea5282f329ec2967417a2f9e506917be00e13272646cb"

PRE_FUNCTIONS_SHA256 = "e7ffc76b6073cf9f96c057ded436e24958596d9d14162e89f3e2d1007b620950"
PRE_PROGRAM_SHA256 = "050c1a9bfd6b421077cb5ea0f6f715edde6b0eac8f8cb65ad4c2294945366ac2"
POST_FUNCTIONS_SHA256 = "f9a06dcdb0ac7510b8bfbf9d655dcf3935a24da603dbc9d3e00f0095fc36af7b"
POST_PROGRAM_SHA256 = "0ec642e8e7fbcdedd06c8d679934b4194a290f70d3435ab08ea07fede4ff943a"
DRY_OUTPUT_SHA256 = "753217a36ecaa2c817d74a9bf3bc0f86b98ae2604238ed9d873a5f40c61ab644"
APPLY_OUTPUT_SHA256 = "e583d6077425f02da8b34234f6e172ec89db56c39200dc992122a42f1ff90123"
READBACK_OUTPUT_SHA256 = "047a800a821be18ba10eb7cc325ee8d724cccba49049e4270f01e2f761329b7d"

GUARD_TOOL = TOOLS / "ghidra_global_init515_live_promotion.py"
GUARD_TOOL_SHA256 = "a1adf103f4c18487553970c62a21f01ea5cfa49c8039b3f299042ff6fc9e8747"
GUARD_DEPENDENCIES = {
    TOOLS / "ghidra_function_batch_proof.py":
        "f76a3e74bd618ef824b0185ce7bebf7476387381e8ace991af72c38560741afa",
    PROCESS_HELPER: PROCESS_HELPER_SHA256,
    TOOLS / "ghidra_global_init_full520_proof.py":
        "2fea029379aaf81df072907a87e142f03e4c1d261d19325933b18823b4fef972",
    TOOLS / "ghidra_promotion_scratch_proof.py":
        "895405aea9da78f72901250c7edb4e042ec28fadf6fbf9409d83097f8dd228be",
    TOOLS / "re_crt_function_strata.py":
        "620d2e09b2d73273ed4815e6dd1d6c0b7c54a3f824aa1b93bd69520119802ab7",
    TOOLS / "re_rtti_vtables.py":
        "90071f2536e6f511d647b47fda7d323110374fd6c57b15e5360adaa0fd717d1d",
}

HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)
HEADLESS_SHA256 = "dd7b9d17d32ed70a71df82a43a21cdaed6c4ce67064e30f8642c149f81c2ae07"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-21.0.9.10-hotspot\bin\java.exe")
JAVA_SHA256 = "5f6248f9c0f32b38ffaba813819bf3331536a48c7ddc45b18e73acd15a6cf7ef"
PYTHON = Path(r"C:\Users\david\AppData\Local\Python\pythoncore-3.14-64\python.exe")
PYTHON_SHA256 = "fda7026477256845afab371e354c4d512896665f1761939cb5887d0a9dec257a"

TOOLCHAIN_MANIFEST_ROOT = (
    REPO / "local-lab/formal-global-init515-proof-20260803-v4/inputs/toolchain"
)
GHIDRA_DISTRIBUTION_MANIFEST = TOOLCHAIN_MANIFEST_ROOT / "ghidra-files.tsv"
JDK_DISTRIBUTION_MANIFEST = TOOLCHAIN_MANIFEST_ROOT / "jdk-files.tsv"
PYTHON_DISTRIBUTION_MANIFEST = TOOLCHAIN_MANIFEST_ROOT / "python-files.tsv"
GHIDRA_DISTRIBUTION = (
    5226, 914_252_158, "5e80e03104d22011ff89429d39d2a83d7e5e56dae6e7e6b0fa2d4c08e674500c"
)
JDK_DISTRIBUTION = (
    490, 343_604_705, "af26450b182c8d085ed3efcae7bb3068f1e002b53f2db2f4111910cb455b39bf"
)
PYTHON_DISTRIBUTION = (
    11_683, 533_160_307, "e43602c0684213f4fb9e1f1c8de2d38cef55345e9ab7a6b061a0e34b1b131d7e"
)

ACTIVE_LAUNCH_GATE: dict[str, object] | None = None

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
DELETE_ACCESS = 0x00010000
READ_CONTROL = 0x00020000
FILE_LIST_DIRECTORY = 0x00000001
FILE_SHARE_READ = 0x00000001
OPEN_EXISTING = 3
CREATE_NEW = 1
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
TOKEN_QUERY = 0x0008
TOKEN_USER = 1
DACL_SECURITY_INFORMATION = 0x00000004
PROTECTED_DACL_SECURITY_INFORMATION = 0x80000000
SDDL_REVISION_1 = 1
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

JOB_CHILD_SOURCE = """\
import base64,json,subprocess,sys
try:
    argv=json.loads(base64.urlsafe_b64decode(sys.argv[1].encode('ascii')).decode('utf-8'))
    if not isinstance(argv,list) or not argv or any(not isinstance(v,str) or not v for v in argv):
        raise ValueError('job child argv must be a nonempty string list')
    if sys.stdin.buffer.read(1)!=b'G':
        raise ValueError('job child launch gate was not released')
    raise SystemExit(subprocess.Popen(argv,stdin=subprocess.DEVNULL).wait())
except (ValueError,UnicodeError,json.JSONDecodeError,OSError,subprocess.SubprocessError) as exc:
    print(f'JOB_CHILD_ERROR: {exc}',file=sys.stderr)
    raise SystemExit(125)
"""


class PromotionError(ValueError):
    """A fail-closed target-lock live-owner refusal."""


class ProjectState(StrEnum):
    PRE = "PRE"
    POST = "POST"
    UNKNOWN = "UNKNOWN"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PromotionError(message)


def exact_file(path: Path, expected: str, label: str) -> Path:
    require(path.is_file() and not path.is_symlink(), f"{label} is absent or unsafe: {path}")
    require(path.stat().st_nlink == 1, f"{label} is hard-linked: {path}")
    require(sha256_file(path) == expected, f"{label} SHA-256 differs: {path}")
    return path.resolve()


# Pin imported executable Python before import.
exact_file(GUARD_TOOL, GUARD_TOOL_SHA256, "live guard")
for _path, _digest in GUARD_DEPENDENCIES.items():
    exact_file(_path, _digest, f"live guard dependency {_path.name}")
exact_file(BACKUP_TOOL, BACKUP_TOOL_SHA256, "backup dependency")
exact_file(PROOF_OWNER, PROOF_OWNER_SHA256, "target-lock proof owner")
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import ghidra_global_init515_live_promotion as guard  # noqa: E402
import ghidra_target_lock_semantic_proof as formal  # noqa: E402

guard.MUTEX_NAME = MUTEX_NAME

EXACT_RUNTIME_MODULE_HASHES = {
    "ghidra_global_init515_live_promotion": GUARD_TOOL_SHA256,
    "ghidra_function_batch_proof": GUARD_DEPENDENCIES[
        TOOLS / "ghidra_function_batch_proof.py"
    ],
    "ghidra_function_envelope_proof": GUARD_DEPENDENCIES[
        TOOLS / "ghidra_function_envelope_proof.py"
    ],
    "ghidra_global_init_full520_proof": GUARD_DEPENDENCIES[
        TOOLS / "ghidra_global_init_full520_proof.py"
    ],
    "ghidra_project_backup": BACKUP_TOOL_SHA256,
    "ghidra_promotion_scratch_proof": GUARD_DEPENDENCIES[
        TOOLS / "ghidra_promotion_scratch_proof.py"
    ],
    "ghidra_target_lock_semantic_proof": PROOF_OWNER_SHA256,
    "re_crt_function_strata": GUARD_DEPENDENCIES[TOOLS / "re_crt_function_strata.py"],
    "re_rtti_vtables": GUARD_DEPENDENCIES[TOOLS / "re_rtti_vtables.py"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def owner_stamp() -> dict[str, object]:
    path = Path(__file__).resolve()
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def expected_launcher_runtime() -> dict[str, object]:
    manifest = exact_file(
        PYTHON_DISTRIBUTION_MANIFEST,
        PYTHON_DISTRIBUTION[2],
        "launcher Python distribution manifest",
    )
    return {
        "pythonDistribution": {
            "root": str(PYTHON.parent.resolve()),
            "fileCount": PYTHON_DISTRIBUTION[0],
            "totalBytes": PYTHON_DISTRIBUTION[1],
            "fileSetSha256": PYTHON_DISTRIBUTION[2],
            "manifest": {
                "path": str(manifest),
                "bytes": manifest.stat().st_size,
                "sha256": PYTHON_DISTRIBUTION[2],
            },
        }
    }


def install_launch_gate(value: Mapping[str, object]) -> None:
    """Install the external launcher's exact, process-local reviewed-byte gate."""
    global ACTIVE_LAUNCH_GATE
    require(ACTIVE_LAUNCH_GATE is None, "launch gate is already installed")
    require(set(value) == {
        "schema", "launcher", "externalReviewedLauncherSha256",
        "reviewedOwnerSha256", "reviewedTestsSha256", "reviewedTests",
        "launcherRuntime",
    }, "launch-gate fields differ")
    require(value.get("schema") == LAUNCH_GATE_SCHEMA, "launch-gate schema differs")
    launcher = value.get("launcher")
    require(isinstance(launcher, dict), "launch-gate launcher stamp is absent")
    require(set(launcher) == {"path", "bytes", "sha256"}, "launch-gate launcher stamp differs")
    launcher_path = Path(str(launcher.get("path")))
    require(
        launcher_path.resolve() == TOOLS / "ghidra_target_lock_semantic_live_launcher.py",
        "launch-gate launcher path differs",
    )
    exact_file(launcher_path, str(launcher.get("sha256")), "external live launcher")
    require(launcher_path.stat().st_size == launcher.get("bytes"),
            "launch-gate launcher byte count differs")
    external_launcher_sha256 = value.get("externalReviewedLauncherSha256")
    require(
        isinstance(external_launcher_sha256, str)
        and re.fullmatch(r"[0-9a-f]{64}", external_launcher_sha256) is not None,
        "external reviewed-launcher SHA-256 is malformed",
    )
    require(external_launcher_sha256 == launcher.get("sha256"),
            "external reviewed-launcher SHA-256 differs from launcher stamp")
    require(os.environ.get(EXTERNAL_LAUNCHER_SHA256_ENV) == external_launcher_sha256,
            "external reviewed-launcher environment gate differs")
    require(value.get("reviewedOwnerSha256") == owner_stamp()["sha256"],
            "launch gate does not bind the running owner")
    require(value.get("reviewedTestsSha256") == OWNER_TESTS_SHA256,
            "launch gate does not bind the reviewed tests")
    exact_file(OWNER_TESTS, OWNER_TESTS_SHA256, "reviewed live-owner tests")
    reviewed_tests = value.get("reviewedTests")
    require(
        isinstance(reviewed_tests, dict)
        and set(reviewed_tests) == {"count", "status"}
        and reviewed_tests.get("status") == "PASSED"
        and reviewed_tests.get("count") == REVIEWED_TEST_COUNT,
        "reviewed live-owner test result differs",
    )
    require(value.get("launcherRuntime") == expected_launcher_runtime(),
            "launch gate does not bind the verified Python distribution")
    require(globals().get("__exact_source_sha256__") == owner_stamp()["sha256"],
            "running owner was not compiled from the reviewed source bytes")
    for module_name, digest in EXACT_RUNTIME_MODULE_HASHES.items():
        module = sys.modules.get(module_name)
        require(module is not None, f"exact-source runtime module is absent: {module_name}")
        require(getattr(module, "__exact_source_sha256__", None) == digest,
                f"runtime module was not compiled from reviewed source: {module_name}")
    ACTIVE_LAUNCH_GATE = json.loads(json.dumps(value))


def require_launch_gate() -> dict[str, object]:
    require(ACTIVE_LAUNCH_GATE is not None, "external reviewed-byte launch gate is absent")
    gate = json.loads(json.dumps(ACTIVE_LAUNCH_GATE))
    require(set(gate) == {
        "schema", "launcher", "externalReviewedLauncherSha256",
        "reviewedOwnerSha256", "reviewedTestsSha256", "reviewedTests",
        "launcherRuntime",
    }, "active launch-gate fields differ")
    require(gate.get("schema") == LAUNCH_GATE_SCHEMA, "active launch-gate schema differs")
    require(gate.get("reviewedOwnerSha256") == owner_stamp()["sha256"],
            "running owner drifted from launch gate")
    require(gate.get("reviewedTestsSha256") == OWNER_TESTS_SHA256,
            "reviewed live-owner test hash drifted")
    require(gate.get("reviewedTests") == {
        "count": REVIEWED_TEST_COUNT, "status": "PASSED",
    }, "reviewed live-owner test result drifted")
    require(gate.get("launcherRuntime") == expected_launcher_runtime(),
            "verified launcher runtime drifted")
    launcher = gate.get("launcher")
    require(isinstance(launcher, dict), "launch-gate launcher stamp is absent")
    require(set(launcher) == {"path", "bytes", "sha256"},
            "active launch-gate launcher stamp differs")
    launcher_path = Path(str(launcher.get("path")))
    require(
        launcher_path.resolve() == TOOLS / "ghidra_target_lock_semantic_live_launcher.py",
        "active launch-gate launcher path differs",
    )
    exact_file(launcher_path, str(launcher.get("sha256")), "external live launcher")
    require(launcher_path.stat().st_size == launcher.get("bytes"),
            "active launch-gate launcher byte count differs")
    require(
        gate.get("externalReviewedLauncherSha256") == launcher.get("sha256")
        and os.environ.get(EXTERNAL_LAUNCHER_SHA256_ENV)
        == gate.get("externalReviewedLauncherSha256"),
        "external reviewed-launcher gate drifted",
    )
    require(globals().get("__exact_source_sha256__") == owner_stamp()["sha256"],
            "running owner is no longer exact-source bound")
    for module_name, digest in EXACT_RUNTIME_MODULE_HASHES.items():
        module = sys.modules.get(module_name)
        require(
            module is not None and getattr(module, "__exact_source_sha256__", None) == digest,
            f"runtime exact-source binding drifted: {module_name}",
        )
    exact_file(OWNER_TESTS, str(gate.get("reviewedTestsSha256")), "reviewed live-owner tests")
    return gate


def validate_timestamp(value: object, label: str) -> None:
    try:
        formal.parse_timestamp(value, label)
    except ValueError as exc:
        raise PromotionError(str(exc)) from exc


def validate_quiescence(value: object, label: str, *, fileset: str) -> None:
    require(isinstance(value, dict), f"{label} is absent")
    require(set(value) == {
        "checkedAtUtc", "javaProcesses", "nativeLockAbsent",
        "exclusiveFilesProbed", "projectFileSetSha256",
    }, f"{label} fields differ")
    validate_timestamp(value.get("checkedAtUtc"), f"{label} timestamp")
    require(value.get("javaProcesses") == [], f"{label} Java state differs")
    require(value.get("nativeLockAbsent") is True, f"{label} native-lock state differs")
    require(value.get("exclusiveFilesProbed") == BASELINE_FILE_COUNT,
            f"{label} exclusive-file count differs")
    require(value.get("projectFileSetSha256") == fileset,
             f"{label} project fileset differs")


def verify_runtime_distributions(
    *, include_ghidra: bool = False, include_jdk: bool = False,
    include_python: bool = False,
) -> dict[str, object]:
    requested = {
        "ghidra": include_ghidra,
        "jdk": include_jdk,
        "python": include_python,
    }
    require(any(requested.values()), "runtime distribution verification has no subject")
    specs = {
        "ghidra": (
            HEADLESS.parent.parent, GHIDRA_DISTRIBUTION_MANIFEST, GHIDRA_DISTRIBUTION,
        ),
        "jdk": (JAVA.parent.parent, JDK_DISTRIBUTION_MANIFEST, JDK_DISTRIBUTION),
        "python": (PYTHON.parent, PYTHON_DISTRIBUTION_MANIFEST, PYTHON_DISTRIBUTION),
    }
    verified: dict[str, object] = {}
    try:
        for label in ("ghidra", "jdk", "python"):
            if not requested[label]:
                continue
            root, manifest, expected = specs[label]
            exact_file(manifest, expected[2], f"{label} distribution manifest")
            value = guard.envelope.verify_distribution(
                root, manifest, expected, label.capitalize()
            )
            value["manifest"] = {
                "path": str(manifest.resolve()),
                "bytes": manifest.stat().st_size,
                "sha256": expected[2],
            }
            verified[label] = value
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    require(set(verified) == {key for key, enabled in requested.items() if enabled},
            "runtime distribution verification is incomplete")
    return verified


def verify_ghidra_script_source_bundle() -> dict[str, object]:
    manifest = exact_file(
        SCRIPT_SOURCE_BUNDLE_MANIFEST,
        SCRIPT_SOURCE_BUNDLE_MANIFEST_SHA256,
        "Ghidra script source-bundle manifest",
    )
    try:
        expected_rows = guard.envelope.parse_distribution_manifest(manifest)
        actual_rows = guard.envelope.tree_rows(
            TOOLS, include=lambda path: path.suffix.casefold() == ".java"
        )
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    count, total_bytes, digest = SCRIPT_SOURCE_BUNDLE
    require(
        len(expected_rows) == count
        and sum(row[1] for row in expected_rows) == total_bytes
        and guard.envelope.rows_digest(expected_rows) == digest,
        "frozen Ghidra script source-bundle manifest identity differs",
    )
    require(actual_rows == expected_rows,
            "Ghidra script source bundle differs from the frozen manifest")
    forbidden: list[str] = []
    try:
        for path in sorted(TOOLS.rglob("*")):
            relative = path.relative_to(TOOLS).as_posix()
            parts = {part.casefold() for part in path.relative_to(TOOLS).parts}
            name = path.name.casefold()
            if (
                "meta-inf" in parts
                or "osgi-inf" in parts
                or path.suffix.casefold() in {".class", ".jar", ".bnd", ".mf"}
                or name in {
                    "bnd.bnd", "generatedactivator.java", "module-info.java",
                    "package-info.java",
                }
            ):
                forbidden.append(relative)
    except OSError as exc:
        raise PromotionError(str(exc)) from exc
    require(not forbidden,
            "Ghidra script source bundle contains activation inputs: " + ", ".join(forbidden))
    return {
        "root": str(TOOLS.resolve()),
        "fileCount": count,
        "totalBytes": total_bytes,
        "fileSetSha256": digest,
        "manifest": {
            "path": str(manifest),
            "bytes": manifest.stat().st_size,
            "sha256": SCRIPT_SOURCE_BUNDLE_MANIFEST_SHA256,
        },
        "activationInputsAbsent": True,
    }


def repository_relative(path: Path, label: str) -> str:
    try:
        relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    except (OSError, ValueError) as exc:
        raise PromotionError(f"{label} escapes the repository") from exc
    require(relative and ":" not in relative and ".." not in Path(relative).parts,
            f"{label} is not one canonical repository-relative path")
    return relative


def live_apply_bundle_sources() -> dict[str, tuple[Path, int, str]]:
    formal.validate_plan(PLAN)
    graph = formal.ArtifactGraph(REPO)
    formal.validate_evidence(EVIDENCE, REPO, graph)
    sources: dict[str, tuple[Path, int, str]] = {}

    def add(relative: str, source: Path, size: int, digest: str) -> None:
        require(relative not in sources, f"execution-bundle source repeats: {relative}")
        require(source.is_file() and not source.is_symlink(),
                f"execution-bundle source is absent or unsafe: {source}")
        require(source.stat().st_size == size and sha256_file(source) == digest,
                f"execution-bundle source differs: {relative}")
        sources[relative] = (source.resolve(), size, digest)

    add(repository_relative(SEMANTIC_TOOL, "semantic mutator"),
        SEMANTIC_TOOL, SEMANTIC_TOOL.stat().st_size, SEMANTIC_TOOL_SHA256)
    add(repository_relative(PLAN, "semantic plan"),
        PLAN, PLAN.stat().st_size, PLAN_SHA256)
    add(repository_relative(EVIDENCE, "semantic evidence"),
        EVIDENCE, EVIDENCE.stat().st_size, EVIDENCE_SHA256)
    for item in graph.items():
        relative = str(item["path"])
        add(relative, REPO / Path(relative), int(item["bytes"]), str(item["sha256"]))
    require(len(sources) == 30, "execution-bundle source count differs")
    return dict(sorted(sources.items()))


def live_apply_bundle_paths(bundle_root: Path) -> dict[str, Path]:
    root = bundle_root.resolve()
    return {
        "root": root,
        "semanticTool": root / Path(repository_relative(SEMANTIC_TOOL, "semantic mutator")),
        "plan": root / Path(repository_relative(PLAN, "semantic plan")),
        "evidence": root / Path(repository_relative(EVIDENCE, "semantic evidence")),
    }


def verify_live_apply_bundle(bundle_root: Path) -> dict[str, object]:
    try:
        root = guard.envelope.require_plain_directory(
            bundle_root, "live-apply execution bundle"
        )
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    paths = live_apply_bundle_paths(root)
    exact_file(paths["semanticTool"], SEMANTIC_TOOL_SHA256,
               "staged semantic mutator")
    exact_file(paths["plan"], PLAN_SHA256, "staged semantic plan")
    exact_file(paths["evidence"], EVIDENCE_SHA256, "staged semantic evidence")
    formal.validate_plan(paths["plan"])
    graph = formal.ArtifactGraph(root)
    formal.validate_evidence(paths["evidence"], root, graph)
    expected: dict[str, tuple[int, str]] = {
        repository_relative(SEMANTIC_TOOL, "semantic mutator"):
            (paths["semanticTool"].stat().st_size, SEMANTIC_TOOL_SHA256),
        repository_relative(PLAN, "semantic plan"):
            (paths["plan"].stat().st_size, PLAN_SHA256),
        repository_relative(EVIDENCE, "semantic evidence"):
            (paths["evidence"].stat().st_size, EVIDENCE_SHA256),
    }
    for item in graph.items():
        relative = str(item["path"])
        stamp = (int(item["bytes"]), str(item["sha256"]))
        require(expected.get(relative, stamp) == stamp,
                f"execution-bundle stamp conflicts: {relative}")
        expected[relative] = stamp
    expected_rows = sorted(
        (relative, size, digest) for relative, (size, digest) in expected.items()
    )
    try:
        actual_rows = guard.envelope.tree_rows(root)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    require(actual_rows == expected_rows,
            "live-apply execution bundle differs from its exact closure")
    forbidden: list[str] = []
    java_sources: list[str] = []
    for relative, _, _ in actual_rows:
        path = root / Path(relative)
        require(path.stat().st_nlink == 1,
                f"execution-bundle file is hard-linked: {relative}")
        parts = {part.casefold() for part in Path(relative).parts}
        name = Path(relative).name.casefold()
        suffix = Path(relative).suffix.casefold()
        if suffix == ".java":
            java_sources.append(relative)
        if (
            "meta-inf" in parts
            or "osgi-inf" in parts
            or suffix in {".class", ".jar", ".bnd", ".mf"}
            or name in {
                "bnd.bnd", "generatedactivator.java", "module-info.java",
                "package-info.java",
            }
        ):
            forbidden.append(relative)
    require(java_sources == [repository_relative(SEMANTIC_TOOL, "semantic mutator")],
            "execution bundle contains an unexpected Java source")
    require(not forbidden,
            "execution bundle contains activation inputs: " + ", ".join(forbidden))
    script_rows = [row for row in actual_rows if row[0] == java_sources[0]]
    return {
        "schema": EXECUTION_BUNDLE_SCHEMA,
        "root": str(root),
        "fileCount": len(actual_rows),
        "totalBytes": sum(row[1] for row in actual_rows),
        "fileSetSha256": guard.envelope.rows_digest(actual_rows),
        "files": [
            {"path": relative, "bytes": size, "sha256": digest}
            for relative, size, digest in actual_rows
        ],
        "semanticTool": spawn_file_stamp(
            paths["semanticTool"], SEMANTIC_TOOL_SHA256, "staged semantic mutator"
        ),
        "plan": spawn_file_stamp(paths["plan"], PLAN_SHA256, "staged semantic plan"),
        "evidence": spawn_file_stamp(
            paths["evidence"], EVIDENCE_SHA256, "staged semantic evidence"
        ),
        "scriptSourceBundle": {
            "root": str(paths["semanticTool"].parent.resolve()),
            "fileCount": 1,
            "totalBytes": script_rows[0][1],
            "fileSetSha256": guard.envelope.rows_digest(
                [(Path(script_rows[0][0]).name, script_rows[0][1], script_rows[0][2])]
            ),
            "activationInputsAbsent": True,
        },
    }


def create_live_apply_bundle(promotion_root: Path) -> dict[str, object]:
    bundle_root = promotion_root / "execution-bundle/repo"
    require(not os.path.lexists(bundle_root),
            "live-apply execution bundle already exists")
    sources = live_apply_bundle_sources()
    for relative, (source, _, _) in sources.items():
        try:
            guard.write_bytes_new(bundle_root / Path(relative), source.read_bytes())
        except (ValueError, OSError) as exc:
            raise PromotionError(str(exc)) from exc
    return verify_live_apply_bundle(bundle_root)


def spawn_file_stamp(path: Path, digest: str, label: str) -> dict[str, object]:
    checked = exact_file(path, digest, label)
    return {
        "path": str(checked),
        "bytes": checked.stat().st_size,
        "sha256": digest,
    }


def verify_spawn_material(argv: Sequence[str]) -> dict[str, object]:
    values = list(argv)
    proof_marker_present = any(
        isinstance(value, str)
        and value in {str(LAUNCHER), str(PROOF_OWNER), "_proof-verify"}
        for value in values
    )
    proof_argv_exact = (
        len(values) == 8
        and values[:5] == [str(PYTHON), "-I", "-B", "-S", "-X"]
        and isinstance(values[5], str)
        and values[5].startswith("pycache_prefix=")
        and values[6:] == [str(LAUNCHER), "_proof-verify"]
    )
    if proof_argv_exact:
        pycache_text = values[5].removeprefix("pycache_prefix=")
        proof_argv_exact = (
            bool(pycache_text)
            and Path(pycache_text).is_absolute()
            and Path(pycache_text).name == "proof-verifier-pycache-disabled"
        )
    if proof_marker_present:
        require(proof_argv_exact, "proof-verifier child grammar differs")
    include_headless = any(
        str(HEADLESS).casefold() in str(value).casefold() for value in argv
    )
    inputs: dict[str, object] = {
        "jobChild": {
            "kind": "inline-python-c",
            "bytes": len(JOB_CHILD_SOURCE.encode("utf-8")),
            "sha256": hashlib.sha256(JOB_CHILD_SOURCE.encode("utf-8")).hexdigest(),
        }
    }
    script_source_bundle: dict[str, object] | None = None
    execution_bundle: dict[str, object] | None = None
    if proof_argv_exact:
        launcher_sha256 = os.environ.get(EXTERNAL_LAUNCHER_SHA256_ENV, "")
        require(re.fullmatch(r"[0-9a-f]{64}", launcher_sha256) is not None,
                "proof-verifier launcher SHA-256 is absent or malformed")
        inputs.update({
            "childEntrypoint": spawn_file_stamp(
                LAUNCHER, launcher_sha256, "proof-verifier launcher entrypoint"
            ),
            "proofOwner": spawn_file_stamp(
                PROOF_OWNER, PROOF_OWNER_SHA256, "proof-verifier exact owner"
            ),
            "proofReady": spawn_file_stamp(
                PROOF_READY, PROOF_READY_SHA256, "proof-verifier READY input"
            ),
        })
    elif include_headless:
        arguments = parse_headless_batch_argv(argv)
        require(arguments.count("-scriptPath") == 1 and arguments.count("-postScript") == 1,
                "Headless spawn script grammar differs")
        script_path_index = arguments.index("-scriptPath") + 1
        script_index = arguments.index("-postScript") + 1
        require(script_path_index < len(arguments) and script_index < len(arguments),
                "Headless spawn script arguments are truncated")
        script_root = Path(arguments[script_path_index]).resolve()
        script = arguments[script_index]
        child = script_root / script
        if script == SEMANTIC_TOOL.name:
            require(script_index + 7 < len(arguments),
                    "semantic Headless arguments are truncated")
            plan = Path(arguments[script_index + 1]).resolve()
            evidence = Path(arguments[script_index + 3]).resolve()
            inputs.update({
                "childEntrypoint": spawn_file_stamp(
                    child, SEMANTIC_TOOL_SHA256, "semantic child entrypoint"
                ),
                "semanticPlan": spawn_file_stamp(plan, PLAN_SHA256, "semantic plan input"),
                "semanticEvidence": spawn_file_stamp(
                    evidence, EVIDENCE_SHA256, "semantic evidence input"
                ),
            })
            if script_root == TOOLS.resolve():
                require(plan == PLAN.resolve() and evidence == EVIDENCE.resolve(),
                        "repository semantic inputs differ")
                script_source_bundle = verify_ghidra_script_source_bundle()
            else:
                execution_bundle = verify_live_apply_bundle(script_root.parent)
                paths = live_apply_bundle_paths(script_root.parent)
                require(
                    child == paths["semanticTool"]
                    and plan == paths["plan"]
                    and evidence == paths["evidence"],
                    "staged semantic paths differ from the execution bundle",
                )
                script_source_bundle = dict(execution_bundle["scriptSourceBundle"])
        elif script == INVENTORY_TOOL.name:
            inputs["childEntrypoint"] = spawn_file_stamp(
                child, INVENTORY_TOOL_SHA256, "inventory child entrypoint"
            )
            require(script_root == INVENTORY_TOOL.parent.resolve(),
                    "inventory script path differs")
            script_source_bundle = verify_ghidra_script_source_bundle()
        else:
            raise PromotionError("Headless spawn lacks one supported child entrypoint")
    elif str(BACKUP_TOOL) in argv:
        inputs["childEntrypoint"] = spawn_file_stamp(
            BACKUP_TOOL, BACKUP_TOOL_SHA256, "backup child entrypoint"
        )
    else:
        raise PromotionError("Python spawn lacks one supported child entrypoint")
    result = {"inputs": inputs}
    if script_source_bundle is not None:
        result["scriptSourceBundle"] = script_source_bundle
    if execution_bundle is not None:
        result["executionBundle"] = execution_bundle
    return result


def verify_spawn_runtime(argv: Sequence[str]) -> dict[str, object]:
    include_headless = any(
        str(HEADLESS).casefold() in str(value).casefold() for value in argv
    )
    distributions = verify_runtime_distributions(
        include_ghidra=include_headless,
        include_jdk=include_headless,
        include_python=True,
    )
    return {
        "distributions": distributions,
        **verify_spawn_material(argv),
    }


def checked_live_apply_spawn(
    promotion_root: Path,
    intent_path: Path,
    intent_sha256: str,
    expected_attempt: Mapping[str, object],
    actual_argv: list[str],
    actual_cwd: Path,
    actual_environment: dict[str, str],
    state: dict[str, object],
    delegate: Callable[
        [list[str], Path, dict[str, str]], tuple[object, int]
    ],
) -> tuple[object, int]:
    """Rebind volatile apply inputs at the actual contained-process spawn edge."""
    require(
        state == {
            "callbackCalls": 0,
            "delegateCalls": 0,
            "preSpawnQuiescence": None,
        },
        "live apply checked-spawn state differs",
    )
    state["callbackCalls"] = 1
    frozen_attempt = require_frozen_json(
        intent_path, intent_sha256, expected_attempt, "live apply intent"
    )
    require(frozen_attempt.get("argv") == actual_argv,
            "live apply argv differs from the frozen intent")

    runtime = frozen_attempt.get("runtimeBoundary")
    require(isinstance(runtime, dict),
            "live apply intent runtime boundary is absent")
    require(set(runtime) == {
        "distributions", "inputs", "scriptSourceBundle", "executionBundle",
        "processContext",
    }, "live apply intent runtime-boundary fields differ")
    execution_bundle = runtime.get("executionBundle")
    require(isinstance(execution_bundle, dict),
            "live apply intent execution bundle is absent")
    bundle_root = Path(str(execution_bundle.get("root", "")))
    bundle_seal = frozen_attempt.get("executionBundleSeal")
    require(isinstance(bundle_seal, dict),
            "live apply intent execution-bundle seal is absent")
    live_preimage = frozen_attempt.get("livePreimage")
    require(isinstance(live_preimage, dict),
            "live apply intent PRE image is absent")
    pre_fileset = live_preimage.get("fileSetSha256")
    require(
        isinstance(pre_fileset, str)
        and re.fullmatch(r"[0-9a-f]{64}", pre_fileset) is not None,
        "live apply intent PRE fileset is malformed",
    )

    actual_runtime = {
        **verify_spawn_runtime(actual_argv),
        "processContext": process_context_boundary(
            promotion_root,
            "live-apply",
            actual_cwd,
            actual_environment,
        ),
    }
    require(actual_runtime == runtime,
            "live apply spawn-edge boundary changed")
    verify_live_apply_bundle_seal(bundle_root, bundle_seal)
    quiescence = guard.assert_quiescent(LIVE_PROJECT)
    validate_quiescence(
        quiescence, "live apply pre-spawn quiescence", fileset=pre_fileset
    )
    state["preSpawnQuiescence"] = json.loads(json.dumps(quiescence))
    state["delegateCalls"] = 1
    return delegate(actual_argv, actual_cwd, actual_environment)


def relative_stamp(path: Path, root: Path) -> dict[str, object]:
    try:
        return guard.relative_stamp(path, root)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def validate_stamp(value: object, root: Path, label: str) -> Path:
    try:
        return guard.validate_relative_stamp(value, root, label)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def validate_exact_stamp(
    value: object, root: Path, expected: Path, label: str
) -> Path:
    path = validate_stamp(value, root, label)
    require(path == expected.resolve(), f"{label} path differs")
    return path


def write_json_new(path: Path, value: object) -> None:
    try:
        guard.write_json_new(path, value)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def require_frozen_json(
    path: Path,
    digest: str,
    expected: Mapping[str, object],
    label: str,
) -> dict[str, object]:
    exact_file(path, digest, label)
    value = formal.read_json(path, label, canonical=True)
    require(value == expected, f"{label} changed")
    return value


def _windows_security_api() -> tuple[object, object]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel32.LocalFree.restype = wintypes.HLOCAL
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    ]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    advapi32.OpenProcessToken.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)
    ]
    advapi32.OpenProcessToken.restype = wintypes.BOOL
    advapi32.GetTokenInformation.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    advapi32.GetTokenInformation.restype = wintypes.BOOL
    advapi32.ConvertSidToStringSidW.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)
    ]
    advapi32.ConvertSidToStringSidW.restype = wintypes.BOOL
    advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(wintypes.DWORD),
    ]
    advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = wintypes.BOOL
    advapi32.SetFileSecurityW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_void_p
    ]
    advapi32.SetFileSecurityW.restype = wintypes.BOOL
    return kernel32, advapi32


def current_user_sid() -> str:
    kernel32, advapi32 = _windows_security_api()
    token = wintypes.HANDLE()
    if not advapi32.OpenProcessToken(
        kernel32.GetCurrentProcess(), TOKEN_QUERY, ctypes.byref(token)
    ):
        raise PromotionError(
            f"cannot open current process token: {ctypes.get_last_error()}"
        )
    try:
        size = wintypes.DWORD()
        advapi32.GetTokenInformation(token, TOKEN_USER, None, 0, ctypes.byref(size))
        require(size.value > 0, "current process token user is absent")
        buffer = ctypes.create_string_buffer(size.value)
        if not advapi32.GetTokenInformation(
            token, TOKEN_USER, buffer, size, ctypes.byref(size)
        ):
            raise PromotionError(
                f"cannot read current process token user: {ctypes.get_last_error()}"
            )
        sid_pointer = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
        text = wintypes.LPWSTR()
        if not advapi32.ConvertSidToStringSidW(sid_pointer, ctypes.byref(text)):
            raise PromotionError(
                f"cannot stringify current process SID: {ctypes.get_last_error()}"
            )
        try:
            sid = str(text.value)
        finally:
            kernel32.LocalFree(text)
    finally:
        kernel32.CloseHandle(token)
    require(re.fullmatch(r"S-\d(?:-\d+)+", sid) is not None,
            "current process SID is malformed")
    return sid


def set_protected_dacl(path: Path, sid: str, *, readonly: bool) -> None:
    kernel32, advapi32 = _windows_security_api()
    user_access = "GRGX" if readonly else "FA"
    sddl = f"D:P(A;;{user_access};;;{sid})(A;;FA;;;SY)"
    descriptor = ctypes.c_void_p()
    size = wintypes.DWORD()
    if not advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
        sddl, SDDL_REVISION_1, ctypes.byref(descriptor), ctypes.byref(size)
    ):
        raise PromotionError(
            f"cannot build protected DACL: {ctypes.get_last_error()}"
        )
    try:
        if not advapi32.SetFileSecurityW(
            str(path),
            DACL_SECURITY_INFORMATION | PROTECTED_DACL_SECURITY_INFORMATION,
            descriptor,
        ):
            raise PromotionError(
                f"cannot seal execution-bundle path: {path}: {ctypes.get_last_error()}"
            )
    finally:
        kernel32.LocalFree(descriptor)


def open_sealed_read_handle(path: Path, *, directory: bool) -> int:
    kernel32, _ = _windows_security_api()
    access = FILE_LIST_DIRECTORY | READ_CONTROL if directory else GENERIC_READ
    flags = FILE_FLAG_OPEN_REPARSE_POINT | (
        FILE_FLAG_BACKUP_SEMANTICS if directory else FILE_ATTRIBUTE_NORMAL
    )
    handle = kernel32.CreateFileW(
        str(path), access, FILE_SHARE_READ, None, OPEN_EXISTING, flags, None
    )
    if handle == INVALID_HANDLE_VALUE:
        raise PromotionError(
            f"cannot acquire sealed read lease: {path}: {ctypes.get_last_error()}"
        )
    return int(handle)


def close_sealed_handles(handles: Sequence[int]) -> None:
    kernel32, _ = _windows_security_api()
    failures: list[int] = []
    for handle in reversed(handles):
        if handle and not kernel32.CloseHandle(wintypes.HANDLE(handle)):
            failures.append(ctypes.get_last_error())
    require(not failures, f"cannot close sealed read leases: {failures}")


def probe_sealed_bundle(bundle_root: Path) -> dict[str, object]:
    paths = live_apply_bundle_paths(bundle_root)
    script_root = paths["semanticTool"].parent
    sibling = script_root / f".seal-create-probe-{uuid.uuid4().hex}.java"
    require(not os.path.lexists(sibling), "bundle seal probe path already exists")
    kernel32, _ = _windows_security_api()
    create = kernel32.CreateFileW(
        str(sibling), GENERIC_WRITE, 0, None, CREATE_NEW,
        FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    create_blocked = create == INVALID_HANDLE_VALUE
    if not create_blocked:
        kernel32.CloseHandle(create)
        try:
            sibling.unlink()
        except OSError:
            pass
    overwrite = kernel32.CreateFileW(
        str(paths["semanticTool"]), GENERIC_WRITE, FILE_SHARE_READ, None,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    overwrite_blocked = overwrite == INVALID_HANDLE_VALUE
    if not overwrite_blocked:
        kernel32.CloseHandle(overwrite)
    delete = kernel32.CreateFileW(
        str(paths["semanticTool"]), DELETE_ACCESS, FILE_SHARE_READ, None,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    delete_blocked = delete == INVALID_HANDLE_VALUE
    if not delete_blocked:
        kernel32.CloseHandle(delete)
    require(create_blocked and overwrite_blocked and delete_blocked,
            "execution-bundle namespace or files remain writable")
    return {
        "createSibling": "BLOCKED",
        "overwriteFile": "BLOCKED",
        "deleteOrRenameFile": "BLOCKED",
    }


def execution_bundle_directories(root: Path, files: Sequence[Path]) -> list[Path]:
    directories = {root}
    for file in files:
        cursor = file.parent
        while True:
            require(cursor == root or root in cursor.parents,
                    "execution-bundle file escapes its root")
            directories.add(cursor)
            if cursor == root:
                break
            cursor = cursor.parent
    return sorted(
        directories,
        key=lambda path: (len(path.parts), str(path).casefold()),
        reverse=True,
    )


def seal_live_apply_bundle(bundle_root: Path) -> dict[str, object]:
    boundary = verify_live_apply_bundle(bundle_root)
    root = Path(str(boundary["root"]))
    sid = current_user_sid()
    files = [root / Path(str(row["path"])) for row in boundary["files"]]
    directories = execution_bundle_directories(root, files)
    sealed: list[Path] = []
    handles: list[int] = []
    try:
        for path in [*files, *directories]:
            set_protected_dacl(path, sid, readonly=True)
            sealed.append(path)
        for path in directories:
            handles.append(open_sealed_read_handle(path, directory=True))
        for path in files:
            handles.append(open_sealed_read_handle(path, directory=False))
        require(verify_live_apply_bundle(root) == boundary,
                "execution bundle changed while being sealed")
        probes = probe_sealed_bundle(root)
    except BaseException:
        if handles:
            close_sealed_handles(handles)
        for path in sealed:
            try:
                set_protected_dacl(path, sid, readonly=False)
            except BaseException:
                pass
        raise
    record = {
        "schema": EXECUTION_BUNDLE_SEAL_SCHEMA,
        "root": str(root),
        "currentUserSid": sid,
        "policy": "protected-current-user-rx-system-full",
        "fileLeases": len(files),
        "directoryLeases": len(directories),
        "writeProbes": probes,
        "trustedHostRequired": True,
    }
    return {"record": record, "handles": handles}


def verify_live_apply_bundle_seal(
    bundle_root: Path, expected: Mapping[str, object]
) -> dict[str, object]:
    boundary = verify_live_apply_bundle(bundle_root)
    root = Path(str(boundary["root"]))
    file_count = int(boundary["fileCount"])
    files = [root / Path(str(row["path"])) for row in boundary["files"]]
    directories = execution_bundle_directories(root, files)
    actual = {
        "schema": EXECUTION_BUNDLE_SEAL_SCHEMA,
        "root": str(root),
        "currentUserSid": current_user_sid(),
        "policy": "protected-current-user-rx-system-full",
        "fileLeases": file_count,
        "directoryLeases": len(directories),
        "writeProbes": probe_sealed_bundle(root),
        "trustedHostRequired": True,
    }
    require(dict(expected) == actual, "execution-bundle seal differs")
    return actual


def seal_exact_file(path: Path, digest: str, label: str) -> int:
    checked = exact_file(path, digest, label)
    sid = current_user_sid()
    set_protected_dacl(checked, sid, readonly=True)
    handle = open_sealed_read_handle(checked, directory=False)
    try:
        exact_file(checked, digest, label)
        kernel32, _ = _windows_security_api()
        for access in (GENERIC_WRITE, DELETE_ACCESS):
            probe = kernel32.CreateFileW(
                str(checked), access, FILE_SHARE_READ, None, OPEN_EXISTING,
                FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, None,
            )
            require(probe == INVALID_HANDLE_VALUE, f"{label} remains writable")
            if probe != INVALID_HANDLE_VALUE:
                kernel32.CloseHandle(probe)
    except BaseException:
        close_sealed_handles([handle])
        try:
            set_protected_dacl(checked, sid, readonly=False)
        except BaseException:
            pass
        raise
    return handle


def spawn_inline_contained_process(
    argv: list[str], cwd: Path, environment: dict[str, str]
) -> tuple[subprocess.Popen, int]:
    encoded = base64.urlsafe_b64encode(
        json.dumps(argv, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    helper = [str(PYTHON), "-I", "-B", "-c", JOB_CHILD_SOURCE, encoded]
    process = subprocess.Popen(
        helper,
        cwd=cwd,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=guard.envelope.CREATE_NO_WINDOW,
    )
    job = guard.envelope._create_kill_on_close_job()
    try:
        guard.envelope._assign_process_to_job(job, process)
        assert process.stdin is not None
        process.stdin.write(b"G")
        process.stdin.flush()
        process.stdin.close()
        process.stdin = None
        return process, job
    except BaseException:
        try:
            guard.envelope._close_handle(job)
        finally:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        raise


def preflight() -> dict[str, object]:
    require(os.name == "nt", "target-lock live promotion is Windows-only")
    require(not ctypes.windll.shell32.IsUserAnAdmin(), "target-lock live promotion must run non-elevated")
    fixed = (
        (PLAN, PLAN_SHA256, "semantic plan"),
        (EVIDENCE, EVIDENCE_SHA256, "semantic evidence"),
        (SCRIPT_SOURCE_BUNDLE_MANIFEST, SCRIPT_SOURCE_BUNDLE_MANIFEST_SHA256,
         "Ghidra script source-bundle manifest"),
        (SEMANTIC_TOOL, SEMANTIC_TOOL_SHA256, "semantic mutator"),
        (INVENTORY_TOOL, INVENTORY_TOOL_SHA256, "inventory tool"),
        (BACKUP_TOOL, BACKUP_TOOL_SHA256, "backup tool"),
        (OWNER_TESTS, OWNER_TESTS_SHA256, "live-owner tests"),
        (PROOF_OWNER, PROOF_OWNER_SHA256, "proof owner"),
        (PROOF_TESTS, PROOF_TESTS_SHA256, "proof owner tests"),
        (PROOF_READY, PROOF_READY_SHA256, "proof READY"),
        (PROOF_CORE, PROOF_CORE_SHA256, "proof core"),
        (PROOF_SUBJECT, PROOF_SUBJECT_SHA256, "proof subject"),
        (PROOF_REFUTER, PROOF_REFUTER_SHA256, "proof refuter"),
        (GUARD_TOOL, GUARD_TOOL_SHA256, "live guard"),
        (HEADLESS, HEADLESS_SHA256, "analyzeHeadless"),
        (JAVA, JAVA_SHA256, "Java"),
        (PYTHON, PYTHON_SHA256, "Python"),
        (GHIDRA_DISTRIBUTION_MANIFEST, GHIDRA_DISTRIBUTION[2],
         "Ghidra distribution manifest"),
        (JDK_DISTRIBUTION_MANIFEST, JDK_DISTRIBUTION[2],
         "JDK distribution manifest"),
        (PYTHON_DISTRIBUTION_MANIFEST, PYTHON_DISTRIBUTION[2],
         "Python distribution manifest"),
    )
    for path, digest, label in fixed:
        exact_file(path, digest, label)
    for path, digest in GUARD_DEPENDENCIES.items():
        exact_file(path, digest, f"live guard dependency {path.name}")
    distributions = verify_runtime_distributions(
        include_ghidra=True, include_jdk=True, include_python=True
    )
    script_source_bundle = verify_ghidra_script_source_bundle()
    ready = formal.verify_ready(PROOF_READY)
    require(ready.get("status") == "READY", "target-lock proof is not READY")
    require(ready.get("semanticNamesAuthorized") is True, "semantic names are not authorized")
    require(ready.get("liveMutationAuthorized") is False, "proof improperly claims live authority")
    baseline = guard.project_snapshot(BASELINE_PROJECT)
    require(
        baseline.get("fileCount") == BASELINE_FILE_COUNT
        and baseline.get("totalBytes") == BASELINE_TOTAL_BYTES
        and baseline.get("fileSetSha256") == BASELINE_FILESET_SHA256,
        "frozen PRE project identity differs",
    )
    return {
        "proofReady": {"path": str(PROOF_READY), "sha256": PROOF_READY_SHA256},
        "proofOwner": {"path": str(PROOF_OWNER), "sha256": PROOF_OWNER_SHA256},
        "semanticTool": {"path": str(SEMANTIC_TOOL), "sha256": SEMANTIC_TOOL_SHA256},
        "plan": {"path": str(PLAN), "sha256": PLAN_SHA256},
        "evidence": {"path": str(EVIDENCE), "sha256": EVIDENCE_SHA256, "rows": 96},
        "baseline": {
            "path": str(BASELINE_PROJECT.resolve()),
            "fileCount": BASELINE_FILE_COUNT,
            "totalBytes": BASELINE_TOTAL_BYTES,
            "fileSetSha256": BASELINE_FILESET_SHA256,
        },
        "program": formal.PROGRAM_IDENTITY,
        "addresses": list(formal.ADDRESSES),
        "runtimeDistributions": distributions,
        "scriptSourceBundle": script_source_bundle,
    }


def environment_for(root: Path) -> tuple[dict[str, str], Path]:
    try:
        environment, cwd = guard.environment_for(root, SimpleNamespace(java=JAVA))
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    expected = expected_process_environment(root)
    environment[EXTERNAL_LAUNCHER_SHA256_ENV] = expected[
        EXTERNAL_LAUNCHER_SHA256_ENV
    ]
    require(environment == expected,
            "fresh process environment differs from the expected boundary")
    return environment, cwd


def canonical_process_context_root(root: Path, run_id: str) -> Path:
    canonical_run_root(root, run_id)
    try:
        contexts = guard.envelope.require_plain_existing_ancestors(
            root / "process-contexts", "process-context root"
        )
        context = guard.envelope.require_plain_existing_ancestors(
            contexts / run_id, "process runtime context"
        )
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    require(context.parent == contexts, "process runtime context escapes its owner")
    return context


def process_context_preflight_path(root: Path, run_id: str) -> Path:
    context = canonical_process_context_root(root, run_id)
    return context.parent / f"{run_id}.preflight.json"


def process_context_boundary(
    root: Path,
    run_id: str,
    cwd: Path,
    environment: Mapping[str, str],
) -> dict[str, object]:
    context = canonical_process_context_root(root, run_id)
    try:
        context = guard.envelope.require_plain_directory(
            context, "process runtime context"
        )
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    require_canonical_process_context(context, cwd, environment)
    try:
        rows = guard.envelope.tree_rows(context)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    java_home = (
        context
        / "runtime-home/roaming/ghidra/ghidra_12.1.2_PUBLIC/java_home.save"
    )
    expected_bytes = f"{JAVA.parent.parent.resolve()}\r\n".encode()
    require(java_home.is_file() and not java_home.is_symlink(),
            "process runtime java_home.save is absent or unsafe")
    require(java_home.stat().st_nlink == 1,
            "process runtime java_home.save is hard-linked")
    expected_rows = [(
        java_home.relative_to(context).as_posix(),
        len(expected_bytes),
        hashlib.sha256(expected_bytes).hexdigest(),
    )]
    require(rows == expected_rows,
            "process runtime context was not pristine before execution")
    return {
        "schema": PROCESS_CONTEXT_SCHEMA,
        "runId": run_id,
        "root": str(context),
        "cwd": str(cwd.resolve()),
        "environment": dict(environment),
        "fileCount": 1,
        "totalBytes": len(expected_bytes),
        "fileSetSha256": guard.envelope.rows_digest(rows),
        "files": [
            {"path": relative, "bytes": size, "sha256": digest}
            for relative, size, digest in rows
        ],
        "compiledClassCount": 0,
    }


def create_fresh_process_context(
    root: Path, run_id: str
) -> tuple[dict[str, str], Path, dict[str, object]]:
    context = canonical_process_context_root(root, run_id)
    preflight_path = process_context_preflight_path(root, run_id)
    require(not os.path.lexists(context),
            f"process runtime context already exists: {context}")
    require(not os.path.lexists(preflight_path),
            f"process runtime preflight already exists: {preflight_path}")
    try:
        guard.envelope.ensure_plain_directory(context, "fresh process runtime context")
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    environment, cwd = environment_for(context)
    boundary = process_context_boundary(root, run_id, cwd, environment)
    write_json_new(preflight_path, boundary)
    frozen = formal.read_json(preflight_path, "process runtime preflight", canonical=True)
    require(frozen == boundary, "process runtime preflight differs")
    return environment, cwd, boundary


def load_process_context_preflight(
    root: Path, run_id: str
) -> dict[str, object]:
    path = process_context_preflight_path(root, run_id)
    require(path.is_file() and not path.is_symlink(),
            f"process runtime preflight is absent or unsafe: {path}")
    require(path.stat().st_nlink == 1,
            f"process runtime preflight is hard-linked: {path}")
    value = formal.read_json(path, "process runtime preflight", canonical=True)
    context = canonical_process_context_root(root, run_id)
    expected_environment = expected_process_environment(context)
    expected_cwd = context / "work"
    require(value.get("schema") == PROCESS_CONTEXT_SCHEMA,
            "process runtime preflight schema differs")
    require(value.get("runId") == run_id and value.get("root") == str(context),
            "process runtime preflight identity differs")
    require(value.get("cwd") == str(expected_cwd.resolve()),
            "process runtime preflight working directory differs")
    require(value.get("environment") == expected_environment,
            "process runtime preflight environment differs")
    require(value.get("fileCount") == 1 and value.get("compiledClassCount") == 0,
            "process runtime preflight file counts differ")
    expected_bytes = f"{JAVA.parent.parent.resolve()}\r\n".encode()
    expected_files = [{
        "path": "runtime-home/roaming/ghidra/ghidra_12.1.2_PUBLIC/java_home.save",
        "bytes": len(expected_bytes),
        "sha256": hashlib.sha256(expected_bytes).hexdigest(),
    }]
    require(value.get("files") == expected_files,
            "process runtime preflight files differ")
    expected_rows = [
        (row["path"], row["bytes"], row["sha256"]) for row in expected_files
    ]
    require(
        value.get("totalBytes") == len(expected_bytes)
        and value.get("fileSetSha256") == guard.envelope.rows_digest(expected_rows),
        "process runtime preflight digest differs",
    )
    return value


def canonical_run_root(root: Path, run_id: str) -> Path:
    require(
        isinstance(run_id, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", run_id) is not None,
        "process run id is not one safe path component",
    )
    require(root.is_absolute(), "process owner root is not absolute")
    try:
        owner_root = guard.envelope.require_plain_directory(root, "process owner root")
        runs_root = guard.envelope.require_plain_existing_ancestors(
            owner_root / "runs", "process runs root"
        )
        run_root = guard.envelope.require_plain_existing_ancestors(
            runs_root / run_id, "process run root"
        )
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    require(run_root.parent == runs_root, "process run root escapes the owner runs root")
    return run_root


def expected_process_environment(root: Path) -> dict[str, str]:
    try:
        expected = guard.envelope.expected_sanitized_environment(root, JAVA)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    expected["BEA_REPO_ROOT"] = str(REPO.resolve())
    launcher_sha256 = os.environ.get(EXTERNAL_LAUNCHER_SHA256_ENV, "")
    require(re.fullmatch(r"[0-9a-f]{64}", launcher_sha256) is not None,
            "reviewed launcher hash is absent from the child environment boundary")
    exact_file(LAUNCHER, launcher_sha256, "reviewed child launcher")
    if ACTIVE_LAUNCH_GATE is not None:
        require(
            ACTIVE_LAUNCH_GATE.get("externalReviewedLauncherSha256") == launcher_sha256,
            "child launcher hash differs from the installed launch gate",
        )
    expected[EXTERNAL_LAUNCHER_SHA256_ENV] = launcher_sha256
    return expected


def require_canonical_process_context(
    root: Path, cwd: Path, environment: Mapping[str, str]
) -> None:
    require(root.is_absolute(), "process owner root is not absolute")
    try:
        owner_root = guard.envelope.require_plain_directory(root, "process owner root")
        expected_cwd = guard.envelope.require_plain_directory(
            owner_root / "work", "process work directory"
        )
        actual_cwd = guard.envelope.require_plain_directory(cwd, "process working directory")
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    require(actual_cwd == expected_cwd, "process working directory differs")
    require(
        type(environment) is dict and environment == expected_process_environment(owner_root),
        "process environment differs from the exact sanitized environment",
    )


def parse_headless_batch_argv(argv: Sequence[str]) -> list[str]:
    require(
        len(argv) == 5
        and Path(argv[0]).resolve() == Path(r"C:\Windows\System32\cmd.exe")
        and list(argv[1:4]) == ["/d", "/s", "/c"]
        and argv[4].startswith("call "),
        "Ghidra Headless process envelope differs",
    )
    command_line = argv[4][len("call "):]
    argc = ctypes.c_int()
    shell32 = ctypes.windll.shell32
    kernel32 = ctypes.windll.kernel32
    shell32.CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
    shell32.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    parsed = shell32.CommandLineToArgvW(command_line, ctypes.byref(argc))
    require(bool(parsed), "cannot parse Ghidra Headless command line")
    try:
        tokens = [parsed[index] for index in range(argc.value)]
    finally:
        kernel32.LocalFree(ctypes.cast(parsed, ctypes.c_void_p))
    require(tokens and Path(tokens[0]).resolve() == HEADLESS.resolve(),
            "Ghidra Headless executable differs")
    try:
        canonical = batch_argv(tokens[1:])
    except (ValueError, OSError) as exc:
        raise PromotionError(f"Ghidra Headless serialization is unsafe: {exc}") from exc
    require(list(argv) == canonical, "Ghidra Headless serialization is noncanonical")
    return tokens[1:]


def require_canonical_readonly_headless(arguments: Sequence[str]) -> None:
    require(len(arguments) >= 10, "read-only Ghidra Headless arguments are truncated")
    require(
        list(arguments[1:9]) == [
            PROJECT_NAME, "-process", PROGRAM_NAME, "-readOnly", "-noanalysis",
            "-scriptPath", str(TOOLS), "-postScript",
        ],
        "read-only Ghidra Headless option grammar differs",
    )
    script = arguments[9]
    if script == SEMANTIC_TOOL.name:
        require(
            len(arguments) == 17
            and list(arguments[10:14]) == [
                str(PLAN), PLAN_SHA256, str(EVIDENCE), EVIDENCE_SHA256,
            ]
            and arguments[16] in {"dry", "readback"},
            "read-only semantic Headless grammar differs",
        )
    elif script == INVENTORY_TOOL.name:
        require(len(arguments) == 12, "read-only inventory Headless grammar differs")
    else:
        raise PromotionError(f"generic runner refuses unsupported Headless script: {script}")


def require_canonical_nonmutating_process(
    root: Path, run_id: str, argv: Sequence[str]
) -> None:
    if any(str(HEADLESS).casefold() in str(value).casefold() for value in argv):
        arguments = parse_headless_batch_argv(argv)
        require_canonical_readonly_headless(arguments)
        run_root = canonical_run_root(root, run_id)
        if arguments[9] == SEMANTIC_TOOL.name:
            require(
                list(arguments[14:16]) == [
                    str(run_root / "observations.tsv"),
                    str(run_root / "observations.ready.json"),
                ],
                "read-only semantic output paths differ from the run root",
            )
        else:
            require(
                list(arguments[10:12]) == [
                    str(run_root / "functions.tsv"), str(run_root / "program.tsv"),
                ],
                "read-only inventory output paths differ from the run root",
            )
        return
    if list(argv) == proof_verify_argv(root):
        canonical_run_root(root, run_id)
        return
    require(
        len(argv) == 9
        and list(argv[:5]) == [str(PYTHON), "-I", "-B", str(BACKUP_TOOL), "copy"]
        and list(argv[7:]) == ["--project-name", PROJECT_NAME]
        and Path(argv[5]).is_absolute()
        and Path(argv[6]).is_absolute(),
        "generic process runner refuses unsupported process grammar",
    )
    canonical_run_root(root, run_id)
    try:
        backups_root = guard.envelope.require_plain_existing_ancestors(
            root / "backups", "backup destination root"
        )
        destination = guard.envelope.require_plain_existing_ancestors(
            Path(argv[6]), "backup destination"
        )
        relative = destination.relative_to(backups_root)
    except (ValueError, OSError) as exc:
        raise PromotionError("backup destination escapes the owner backup root") from exc
    require(relative.parts and all(":" not in part for part in relative.parts),
            "backup destination is not a safe owner-root descendant")


def run_process(
    root: Path,
    run_id: str,
    argv: list[str],
    cwd: Path,
    environment: dict[str, str],
    *,
    timeout: int = 600,
) -> tuple[dict[str, object], str]:
    require_canonical_nonmutating_process(root, run_id, argv)
    require_canonical_process_context(root, cwd, environment)
    verify_spawn_runtime(argv)
    child_environment, child_cwd, context = create_fresh_process_context(root, run_id)
    require(
        process_context_boundary(root, run_id, child_cwd, child_environment) == context,
        "process runtime context changed before execution",
    )
    try:
        return guard.run_contained(
            session_root=root,
            run_id=run_id,
            argv=argv,
            cwd=child_cwd,
            environment=child_environment,
            timeout_seconds=timeout,
        )
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def require_clean_process(process: Mapping[str, object], text: str, label: str) -> None:
    try:
        guard.require_success(process, label)
    except ValueError as exc:
        raise PromotionError(str(exc)) from exc
    require("REPORT SCRIPT ERROR" not in text, f"{label} reported a script error")
    require("unexpected_final_commit=true" not in text, f"{label} reported unexpected final commit")
    require("persistence_tainted=true" not in text, f"{label} reported persistence taint")


def batch_argv(arguments: list[str]) -> list[str]:
    return guard.envelope.windows_batch_argv(HEADLESS, arguments)


def proof_pycache_prefix(root: Path) -> Path:
    path = (root / "runtime/proof-verifier-pycache-disabled").resolve()
    require(not os.path.lexists(path), f"proof-verifier pycache prefix exists: {path}")
    return path


def proof_verify_argv(root: Path) -> list[str]:
    prefix = proof_pycache_prefix(root)
    return [
        str(PYTHON), "-I", "-B", "-S", "-X", f"pycache_prefix={prefix}",
        str(LAUNCHER), "_proof-verify",
    ]


def run_proof_verifier(
    root: Path, run_id: str, cwd: Path, environment: dict[str, str]
) -> dict[str, object]:
    process, text = run_process(
        root, run_id, proof_verify_argv(root), cwd, environment, timeout=900
    )
    require_clean_process(process, text, run_id)
    expected = (
        f"READY_VERIFIED status=READY sha256={PROOF_READY_SHA256} "
        "live_mutation_authorized=false"
    )
    require(text.strip() == expected, f"{run_id} proof-verifier output differs")
    return {"process": process["receipt"], "output": expected}


def semantic_argv(project: Path, output: Path, ready: Path, mode: str) -> list[str]:
    require(mode in {"dry", "readback"}, f"unsupported read-only semantic mode: {mode}")
    arguments = [str(project.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME]
    arguments.append("-readOnly")
    arguments.extend([
        "-noanalysis", "-scriptPath", str(TOOLS), "-postScript", SEMANTIC_TOOL.name,
        str(PLAN), PLAN_SHA256, str(EVIDENCE), EVIDENCE_SHA256,
        str(output), str(ready), mode,
    ])
    return batch_argv(arguments)


def fixed_apply_argv(
    project: Path,
    output: Path,
    ready: Path,
    *,
    semantic_tool: Path = SEMANTIC_TOOL,
    plan: Path = PLAN,
    evidence: Path = EVIDENCE,
) -> list[str]:
    arguments = [
        str(project.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME,
        "-noanalysis", "-scriptPath", str(semantic_tool.parent.resolve()),
        "-postScript", semantic_tool.name,
        str(plan.resolve()), PLAN_SHA256, str(evidence.resolve()), EVIDENCE_SHA256,
        str(output), str(ready), "apply",
    ]
    return batch_argv(arguments)


def inventory_argv(project: Path, functions: Path, program: Path) -> list[str]:
    return batch_argv([
        str(project.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME,
        "-readOnly", "-noanalysis", "-scriptPath", str(INVENTORY_TOOL.parent),
        "-postScript", INVENTORY_TOOL.name, str(functions), str(program),
    ])


def run_semantic(
    project: Path,
    root: Path,
    run_id: str,
    mode: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    require(mode in {"dry", "readback"},
            "run_semantic is read-only; apply is owned only by promote")
    run_root = root / "runs" / run_id
    output = run_root / "observations.tsv"
    ready = run_root / "observations.ready.json"
    argv = semantic_argv(project, output, ready, mode)
    process, text = run_process(root, run_id, argv, cwd, environment, timeout=900)
    require_clean_process(process, text, run_id)
    require(output.is_file() and ready.is_file(), f"{run_id} semantic outputs are absent")
    expected_hash = {
        "dry": DRY_OUTPUT_SHA256,
        "readback": READBACK_OUTPUT_SHA256,
    }[mode]
    require(sha256_file(output) == expected_hash, f"{run_id} semantic TSV differs")
    rows = formal.validate_observations(output, mode)
    formal.validate_java_ready(
        ready,
        output,
        mode=mode,
        semantic_tool=SEMANTIC_TOOL,
        plan=PLAN,
        evidence=EVIDENCE,
    )
    log = root / process["log"]["path"]
    formal.require_success_log(log, mode, SEMANTIC_TOOL)
    return {
        "mode": mode,
        "output": relative_stamp(output, root),
        "ready": relative_stamp(ready, root),
        "process": process["receipt"],
        "normalizedRows": formal.normalized_observations(rows),
    }


def run_inventory(
    project: Path,
    root: Path,
    run_id: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    run_root = root / "runs" / run_id
    functions = run_root / "functions.tsv"
    program = run_root / "program.tsv"
    argv = inventory_argv(project, functions, program)
    process, text = run_process(root, run_id, argv, cwd, environment, timeout=900)
    require_clean_process(process, text, run_id)
    require("INVENTORY_OK" in text, f"{run_id} inventory marker is absent")
    require(functions.is_file() and program.is_file(), f"{run_id} inventory outputs are absent")
    return {
        "functions": relative_stamp(functions, root),
        "program": relative_stamp(program, root),
        "process": process["receipt"],
    }


def inventory_paths(value: Mapping[str, object], root: Path, label: str) -> dict[str, Path]:
    return {
        "functions": validate_stamp(value.get("functions"), root, f"{label} functions"),
        "program": validate_stamp(value.get("program"), root, f"{label} program"),
    }


def classify_inventory(value: Mapping[str, object], root: Path, label: str) -> ProjectState:
    paths = inventory_paths(value, root, label)
    pair = (sha256_file(paths["functions"]), sha256_file(paths["program"]))
    if pair == (PRE_FUNCTIONS_SHA256, PRE_PROGRAM_SHA256):
        formal.validate_inventory_pair(
            paths["functions"], paths["program"], PRE_FUNCTIONS_SHA256, PRE_PROGRAM_SHA256
        )
        return ProjectState.PRE
    if pair == (POST_FUNCTIONS_SHA256, POST_PROGRAM_SHA256):
        formal.validate_inventory_pair(
            paths["functions"], paths["program"], POST_FUNCTIONS_SHA256, POST_PROGRAM_SHA256
        )
        return ProjectState.POST
    return ProjectState.UNKNOWN


def observe_pre(
    project: Path,
    root: Path,
    label: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    guard.assert_quiescent(project)
    before = guard.project_snapshot(project)
    semantic = run_semantic(project, root, f"{label}-dry", "dry", cwd, environment)
    inventory = run_inventory(project, root, f"{label}-inventory", cwd, environment)
    require(classify_inventory(inventory, root, label) == ProjectState.PRE, f"{label} is not exact PRE")
    after = guard.project_snapshot(project)
    require(guard.same_project_snapshot(before, after), f"{label} changed during read-only observation")
    guard.assert_quiescent(project)
    return {
        "schema": OBSERVATION_SCHEMA,
        "state": ProjectState.PRE,
        "projectRoot": str(project.resolve()),
        "rawBefore": before,
        "rawAfter": after,
        "semantic": semantic,
        "inventory": inventory,
    }


def observe_post(
    project: Path,
    root: Path,
    label: str,
    cwd: Path,
    environment: dict[str, str],
    *,
    pre_inventory: Mapping[str, object],
    pre_root: Path,
    apply_semantic: Mapping[str, object] | None = None,
) -> dict[str, object]:
    guard.assert_quiescent(project)
    before = guard.project_snapshot(project)
    semantic = run_semantic(project, root, f"{label}-readback", "readback", cwd, environment)
    inventory = run_inventory(project, root, f"{label}-inventory", cwd, environment)
    require(classify_inventory(inventory, root, label) == ProjectState.POST, f"{label} is not exact POST")
    pre = inventory_paths(pre_inventory, pre_root, f"{label} PRE reference")
    post = inventory_paths(inventory, root, f"{label} POST")
    delta = formal.validate_inventory_delta(
        pre["functions"], pre["program"], post["functions"], post["program"],
        formal.validate_plan(PLAN),
    )
    if apply_semantic is not None:
        require(
            semantic.get("normalizedRows") == apply_semantic.get("normalizedRows"),
            f"{label} apply/readback semantic rows differ",
        )
    after = guard.project_snapshot(project)
    require(guard.same_project_snapshot(before, after), f"{label} changed during read-only observation")
    guard.assert_quiescent(project)
    return {
        "schema": OBSERVATION_SCHEMA,
        "state": ProjectState.POST,
        "projectRoot": str(project.resolve()),
        "rawBefore": before,
        "rawAfter": after,
        "semantic": semantic,
        "inventory": inventory,
        "delta": delta,
    }


def run_copy(
    root: Path,
    run_id: str,
    source: Path,
    destination: Path,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    require(not destination.exists(), f"{run_id} destination already exists")
    argv = [
        str(PYTHON), "-I", "-B", str(BACKUP_TOOL), "copy",
        str(source.resolve()), str(destination.resolve()), "--project-name", PROJECT_NAME,
    ]
    process, text = run_process(root, run_id, argv, cwd, environment, timeout=300)
    require_clean_process(process, text, run_id)
    require("HashDiffCount=0" in text, f"{run_id} copy verification marker is absent")
    manifest = destination / "backup_manifest.json"
    require(manifest.is_file(), f"{run_id} backup manifest is absent")
    return {"process": process["receipt"], "manifest": relative_stamp(manifest, root)}


def copy_and_drill(
    root: Path,
    label: str,
    source: Path,
    backup_root: Path,
    restore_root: Path,
    state: ProjectState,
    cwd: Path,
    environment: dict[str, str],
    *,
    pre_inventory: Mapping[str, object] | None = None,
    pre_root: Path | None = None,
) -> dict[str, object]:
    guard.assert_quiescent(source)
    source_before = guard.project_snapshot(source)
    backup_copy = run_copy(root, f"{label}-backup-copy", source, backup_root, cwd, environment)
    backup_snapshot = guard.project_snapshot(backup_root)
    require(guard.same_project_snapshot(source_before, backup_snapshot), f"{label} backup bytes differ")
    guard.require_disjoint_project_files(source, backup_root)
    if state == ProjectState.PRE:
        backup_observation = observe_pre(
            backup_root, root, f"{label}-backup", cwd, environment
        )
    else:
        require(pre_inventory is not None and pre_root is not None, f"{label} PRE reference is absent")
        backup_observation = observe_post(
            backup_root,
            root,
            f"{label}-backup",
            cwd,
            environment,
            pre_inventory=pre_inventory,
            pre_root=pre_root,
        )

    restore_copy = run_copy(
        root, f"{label}-restore-copy", backup_root, restore_root, cwd, environment
    )
    restore_snapshot = guard.project_snapshot(restore_root)
    require(
        guard.same_project_snapshot(source_before, restore_snapshot),
        f"{label} restore-drill bytes differ",
    )
    guard.require_disjoint_project_files(source, restore_root)
    guard.require_disjoint_project_files(backup_root, restore_root)
    if state == ProjectState.PRE:
        restore_observation = observe_pre(
            restore_root, root, f"{label}-restore", cwd, environment
        )
    else:
        restore_observation = observe_post(
            restore_root,
            root,
            f"{label}-restore",
            cwd,
            environment,
            pre_inventory=pre_inventory,
            pre_root=pre_root,
        )
    source_after = guard.project_snapshot(source)
    require(
        guard.same_project_snapshot(source_before, source_after),
        f"{label} source changed during backup drill",
    )
    return {
        "state": state,
        "sourceRoot": str(source.resolve()),
        "backupRoot": str(backup_root.resolve()),
        "restoreRoot": str(restore_root.resolve()),
        "sourceSnapshot": source_before,
        "backupSnapshot": backup_snapshot,
        "restoreSnapshot": restore_snapshot,
        "backupCopy": backup_copy,
        "restoreCopy": restore_copy,
        "backupObservation": backup_observation,
        "restoreObservation": restore_observation,
    }


def validate_process_stamp(value: object, root: Path, label: str) -> dict[str, object]:
    try:
        receipt = guard.validate_process_receipt(value, root, label)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc
    run_id = receipt.get("id")
    require(isinstance(run_id, str), f"{label} process id is absent")
    context = load_process_context_preflight(root, run_id)
    require(receipt.get("cwd") == context.get("cwd"),
            f"{label} process working directory differs from its fresh context")
    require(receipt.get("environment") == context.get("environment"),
            f"{label} process environment differs from its fresh context")
    return receipt


def validate_proof_verification(value: object, root: Path, label: str) -> None:
    require(isinstance(value, dict), f"{label} is absent")
    expected = (
        f"READY_VERIFIED status=READY sha256={PROOF_READY_SHA256} "
        "live_mutation_authorized=false"
    )
    require(value.get("output") == expected, f"{label} output differs")
    process = validate_process_stamp(value.get("process"), root, f"{label} process")
    require(process.get("argv") == proof_verify_argv(root), f"{label} argv differs")
    log = root / process["log"]["path"]
    require(log.read_text(encoding="utf-8").strip() == expected, f"{label} log differs")


def validate_semantic_payload(
    value: object,
    root: Path,
    label: str,
    *,
    project: Path,
    mode: str,
    semantic_tool: Path = SEMANTIC_TOOL,
    plan: Path = PLAN,
    evidence: Path = EVIDENCE,
) -> dict[str, object]:
    require(isinstance(value, dict), f"{label} is absent")
    require(value.get("mode") == mode, f"{label} mode differs")
    output = validate_stamp(value.get("output"), root, f"{label} output")
    ready = validate_stamp(value.get("ready"), root, f"{label} READY")
    expected_hash = {
        "dry": DRY_OUTPUT_SHA256,
        "apply": APPLY_OUTPUT_SHA256,
        "readback": READBACK_OUTPUT_SHA256,
    }[mode]
    require(sha256_file(output) == expected_hash, f"{label} output hash differs")
    rows = formal.validate_observations(output, mode)
    formal.validate_java_ready(
        ready,
        output,
        mode=mode,
        semantic_tool=semantic_tool,
        plan=plan,
        evidence=evidence,
    )
    process = validate_process_stamp(value.get("process"), root, f"{label} process")
    expected_argv = (
        fixed_apply_argv(
            project,
            output,
            ready,
            semantic_tool=semantic_tool,
            plan=plan,
            evidence=evidence,
        )
        if mode == "apply"
        else semantic_argv(project, output, ready, mode)
    )
    require(process.get("argv") == expected_argv, f"{label} argv differs")
    formal.require_success_log(root / process["log"]["path"], mode, semantic_tool)
    normalized = formal.normalized_observations(rows)
    require(value.get("normalizedRows") == normalized, f"{label} normalized rows differ")
    return {"output": output, "ready": ready, "process": process, "normalizedRows": normalized}


def validate_inventory_payload(
    value: object,
    root: Path,
    label: str,
    *,
    project: Path,
) -> tuple[dict[str, Path], ProjectState]:
    require(isinstance(value, dict), f"{label} is absent")
    paths = inventory_paths(value, root, label)
    process = validate_process_stamp(value.get("process"), root, f"{label} process")
    require(
        process.get("argv") == inventory_argv(project, paths["functions"], paths["program"]),
        f"{label} argv differs",
    )
    text = (root / process["log"]["path"]).read_text(encoding="utf-8")
    require("INVENTORY_OK" in text and "REPORT SCRIPT ERROR" not in text, f"{label} log differs")
    return paths, classify_inventory(value, root, label)


def validate_observation(
    value: object,
    root: Path,
    label: str,
    *,
    project: Path,
    state: ProjectState,
    pre_inventory: Mapping[str, object] | None = None,
    pre_root: Path | None = None,
    check_current: bool = True,
) -> dict[str, object]:
    require(isinstance(value, dict), f"{label} is absent")
    require(value.get("schema") == OBSERVATION_SCHEMA, f"{label} schema differs")
    require(value.get("state") == state, f"{label} state differs")
    require(value.get("projectRoot") == str(project.resolve()), f"{label} project root differs")
    before = value.get("rawBefore")
    after = value.get("rawAfter")
    require(isinstance(before, dict) and isinstance(after, dict), f"{label} raw snapshots are absent")
    require(before.get("root") == str(project.resolve()), f"{label} raw-before root differs")
    require(after.get("root") == str(project.resolve()), f"{label} raw-after root differs")
    require(guard.same_project_snapshot(before, after), f"{label} raw snapshots differ")
    if check_current:
        require(
            guard.same_project_snapshot(after, guard.project_snapshot(project)),
            f"{label} project bytes no longer match",
        )
    mode = "dry" if state == ProjectState.PRE else "readback"
    semantic = validate_semantic_payload(
        value.get("semantic"), root, f"{label} semantic", project=project, mode=mode
    )
    inventory_paths_value, inventory_state = validate_inventory_payload(
        value.get("inventory"), root, f"{label} inventory", project=project
    )
    require(inventory_state == state, f"{label} inventory state differs")
    if state == ProjectState.POST:
        require(pre_inventory is not None and pre_root is not None, f"{label} PRE reference is absent")
        pre = inventory_paths(pre_inventory, pre_root, f"{label} PRE reference")
        delta = formal.validate_inventory_delta(
            pre["functions"],
            pre["program"],
            inventory_paths_value["functions"],
            inventory_paths_value["program"],
            formal.validate_plan(PLAN),
        )
        require(value.get("delta") == delta, f"{label} inventory delta differs")
    return {"semantic": semantic, "inventory": inventory_paths_value}


def validate_copy_payload(
    value: object,
    root: Path,
    label: str,
    *,
    state: ProjectState,
    pre_inventory: Mapping[str, object] | None = None,
    pre_root: Path | None = None,
) -> None:
    require(isinstance(value, dict), f"{label} is absent")
    require(value.get("state") == state, f"{label} state differs")
    source = Path(str(value.get("sourceRoot")))
    backup = Path(str(value.get("backupRoot")))
    restore = Path(str(value.get("restoreRoot")))
    require(len({str(source.resolve()), str(backup.resolve()), str(restore.resolve())}) == 3,
            f"{label} roots are not disjoint")
    source_snapshot = value.get("sourceSnapshot")
    require(isinstance(source_snapshot, dict), f"{label} source snapshot is absent")
    backup_snapshot = guard.validate_project_snapshot(value.get("backupSnapshot"), backup, f"{label} backup")
    restore_snapshot = guard.validate_project_snapshot(value.get("restoreSnapshot"), restore, f"{label} restore")
    require(guard.same_project_snapshot(source_snapshot, backup_snapshot), f"{label} backup differs")
    require(guard.same_project_snapshot(source_snapshot, restore_snapshot), f"{label} restore differs")
    guard.require_disjoint_project_files(source, backup)
    guard.require_disjoint_project_files(source, restore)
    guard.require_disjoint_project_files(backup, restore)
    for copy_key, copy_source, copy_destination in (
        ("backupCopy", source, backup),
        ("restoreCopy", backup, restore),
    ):
        copy_value = value.get(copy_key)
        require(isinstance(copy_value, dict), f"{label} {copy_key} is absent")
        validate_stamp(copy_value.get("manifest"), root, f"{label} {copy_key} manifest")
        process = validate_process_stamp(copy_value.get("process"), root, f"{label} {copy_key} process")
        expected = [
            str(PYTHON), "-I", "-B", str(BACKUP_TOOL), "copy",
            str(copy_source.resolve()), str(copy_destination.resolve()),
            "--project-name", PROJECT_NAME,
        ]
        require(process.get("argv") == expected, f"{label} {copy_key} argv differs")
    validate_observation(
        value.get("backupObservation"),
        root,
        f"{label} backup observation",
        project=backup,
        state=state,
        pre_inventory=pre_inventory,
        pre_root=pre_root,
    )
    validate_observation(
        value.get("restoreObservation"),
        root,
        f"{label} restore observation",
        project=restore,
        state=state,
        pre_inventory=pre_inventory,
        pre_root=pre_root,
    )


def validate_mutation_census(
    owner_root: Path, *, expected: int, preparation_only: bool = False
) -> None:
    mutators: list[tuple[Path, list[object]]] = []
    for receipt_path in owner_root.rglob("run.json"):
        if preparation_only and "promotion" in receipt_path.relative_to(owner_root).parts:
            continue
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        argv = receipt.get("argv")
        require(isinstance(argv, list), f"process argv is malformed: {receipt_path}")
        if not any(str(HEADLESS).casefold() in str(value).casefold() for value in argv):
            continue
        try:
            require_canonical_readonly_headless(parse_headless_batch_argv(argv))
            continue
        except PromotionError:
            pass
        mutators.append((receipt_path, argv))
    require(len(mutators) == expected, f"mutating-process census differs from {expected}")
    if expected:
        receipt_path, argv = mutators[0]
        require(
            receipt_path == owner_root / "promotion/runs/live-apply/run.json",
            "mutating-process receipt path differs",
        )
        intent = formal.read_json(
            owner_root / "promotion/attempt.started.json",
            "mutation-census apply intent",
            canonical=True,
        )
        require(argv == intent.get("argv"),
                "mutating-process argv differs from immutable apply intent")


def prepare(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    launch_gate = require_launch_gate()
    with guard.acquire_mutex() as lease:
        require(not owner_root.exists(), f"live preparation root already exists: {owner_root}")
        owner_root.mkdir()
        require(owner_root.is_dir() and not owner_root.is_symlink(),
                "live preparation root claim is unsafe")
        authority = preflight()
        first_quiescence = guard.assert_quiescent(LIVE_PROJECT)
        environment, cwd = environment_for(owner_root)
        verifier = run_proof_verifier(owner_root, "proof-verify", cwd, environment)
        baseline = guard.project_snapshot(BASELINE_PROJECT)
        live_before = guard.project_snapshot(LIVE_PROJECT)
        require(guard.same_project_snapshot(baseline, live_before),
                "maintainer project differs from the frozen target-lock PRE project")
        initial = observe_pre(LIVE_PROJECT, owner_root, "live-pre-initial", cwd, environment)
        backup = copy_and_drill(
            owner_root,
            "pre-live",
            LIVE_PROJECT,
            owner_root / "backups/pre-live",
            owner_root / "backups/pre-live-restore-drill",
            ProjectState.PRE,
            cwd,
            environment,
        )
        final = observe_pre(LIVE_PROJECT, owner_root, "live-pre-final", cwd, environment)
        require(guard.same_project_snapshot(live_before, final["rawAfter"]),
                "maintainer PRE project changed during preparation")
        final_quiescence = guard.assert_quiescent(LIVE_PROJECT)
        ready = {
            "schema": PREPARED_SCHEMA,
            "status": "READY",
            "preparedAtUtc": utc_now(),
            "owner": owner_stamp(),
            "launchGate": launch_gate,
            "mutex": {"name": lease.name, "abandoned": lease.abandoned},
            "authority": authority,
            "proofVerification": verifier,
            "firstQuiescence": first_quiescence,
            "finalQuiescence": final_quiescence,
            "livePreimage": live_before,
            "initialObservation": initial,
            "finalObservation": final,
            "preBackup": backup,
            "policies": {
                "preparationMutationSpawns": 0,
                "promotionMutationSpawnLimit": 1,
                "retryAuthorized": False,
                "automaticRestoreAuthorized": False,
                "trackedSnapshotRefreshAuthorized": False,
            },
        }
        path = owner_root / "prepared.ready.json"
        write_json_new(path, ready)
        validate_mutation_census(owner_root, expected=0, preparation_only=True)
        frozen = formal.read_json(path, "new prepared READY", canonical=True)
        require(frozen == ready, "frozen prepared READY differs")
        load_prepared(owner_root)
        return {**ready, "ready": str(path), "readySha256": sha256_file(path)}


def load_prepared(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    launch_gate = require_launch_gate()
    path = owner_root / "prepared.ready.json"
    require(path.is_file() and not path.is_symlink(), f"prepared READY is absent or unsafe: {path}")
    require(path.stat().st_nlink == 1, f"prepared READY is hard-linked: {path}")
    path = path.resolve()
    ready = formal.read_json(path, "prepared READY", canonical=True)
    require(set(ready) == {
        "schema", "status", "preparedAtUtc", "owner", "launchGate", "mutex",
        "authority", "proofVerification", "firstQuiescence", "finalQuiescence",
        "livePreimage", "initialObservation", "finalObservation", "preBackup", "policies",
    }, "prepared READY fields differ")
    require(ready.get("schema") == PREPARED_SCHEMA and ready.get("status") == "READY",
            "prepared READY identity differs")
    validate_timestamp(ready.get("preparedAtUtc"), "prepared READY timestamp")
    require(ready.get("owner") == owner_stamp(), "prepared owner identity differs")
    require(ready.get("launchGate") == launch_gate, "prepared launch gate differs")
    require(ready.get("mutex") == {"name": MUTEX_NAME, "abandoned": False},
            "prepared mutex identity differs")
    require(ready.get("authority") == preflight(), "prepared authority differs")
    validate_quiescence(
        ready.get("firstQuiescence"), "prepared first quiescence",
        fileset=BASELINE_FILESET_SHA256,
    )
    validate_quiescence(
        ready.get("finalQuiescence"), "prepared final quiescence",
        fileset=BASELINE_FILESET_SHA256,
    )
    validate_proof_verification(ready.get("proofVerification"), owner_root, "prepared proof verification")
    initial = ready.get("initialObservation")
    final = ready.get("finalObservation")
    validate_observation(
        initial, owner_root, "prepared initial", project=LIVE_PROJECT,
        state=ProjectState.PRE, check_current=False,
    )
    validate_observation(
        final, owner_root, "prepared final", project=LIVE_PROJECT,
        state=ProjectState.PRE, check_current=False,
    )
    validate_copy_payload(ready.get("preBackup"), owner_root, "prepared PRE backup", state=ProjectState.PRE)
    baseline = guard.project_snapshot(BASELINE_PROJECT)
    require(guard.same_project_snapshot(ready.get("livePreimage", {}), baseline),
            "prepared live preimage differs from frozen PRE")
    require(initial["rawAfter"] == ready["livePreimage"] and final["rawAfter"] == ready["livePreimage"],
            "prepared observations differ from live preimage")
    policies = ready.get("policies")
    require(policies == {
        "preparationMutationSpawns": 0,
        "promotionMutationSpawnLimit": 1,
        "retryAuthorized": False,
        "automaticRestoreAuthorized": False,
        "trackedSnapshotRefreshAuthorized": False,
    }, "prepared policies differ")
    validate_mutation_census(owner_root, expected=0, preparation_only=True)
    return ready


def classify_project(
    project: Path,
    root: Path,
    run_id: str,
    cwd: Path,
    environment: dict[str, str],
) -> tuple[ProjectState, dict[str, object]]:
    guard.assert_quiescent(project)
    before = guard.project_snapshot(project)
    inventory = run_inventory(project, root, run_id, cwd, environment)
    state = classify_inventory(inventory, root, run_id)
    after = guard.project_snapshot(project)
    require(guard.same_project_snapshot(before, after),
            f"{run_id} changed the project during classification")
    guard.assert_quiescent(project)
    return state, {
        "schema": OBSERVATION_SCHEMA,
        "state": state,
        "projectRoot": str(project.resolve()),
        "rawBefore": before,
        "rawAfter": after,
        "inventory": inventory,
    }


def validate_classification(
    value: object,
    root: Path,
    label: str,
    *,
    project: Path,
    state: ProjectState,
    check_current: bool = True,
) -> dict[str, Path]:
    require(isinstance(value, dict), f"{label} is absent")
    require(value.get("schema") == OBSERVATION_SCHEMA, f"{label} schema differs")
    require(value.get("state") == state, f"{label} state differs")
    require(value.get("projectRoot") == str(project.resolve()), f"{label} project root differs")
    before = value.get("rawBefore")
    after = value.get("rawAfter")
    require(isinstance(before, dict) and isinstance(after, dict), f"{label} raw snapshots are absent")
    require(guard.same_project_snapshot(before, after), f"{label} raw snapshots differ")
    if check_current:
        require(guard.same_project_snapshot(after, guard.project_snapshot(project)),
                f"{label} project bytes no longer match")
    paths, classified = validate_inventory_payload(
        value.get("inventory"), root, f"{label} inventory", project=project
    )
    require(classified == state, f"{label} reproduced state differs")
    return paths


def validate_apply_protocol(
    process: Mapping[str, object],
    text: str,
    output: Path,
    ready: Path,
    promotion_root: Path,
    *,
    semantic_tool: Path,
    plan: Path,
    evidence: Path,
) -> tuple[dict[str, object] | None, list[str]]:
    reasons: list[str] = []
    semantic: dict[str, object] | None = None
    try:
        require_clean_process(process, text, "live apply")
        require(process.get("argv") == fixed_apply_argv(
            LIVE_PROJECT,
            output,
            ready,
            semantic_tool=semantic_tool,
            plan=plan,
            evidence=evidence,
        ),
                "live apply argv differs from fixed mutator")
        require(output.is_file() and ready.is_file(), "live apply artifacts are absent")
        require(sha256_file(output) == APPLY_OUTPUT_SHA256, "live apply TSV differs")
        rows = formal.validate_observations(output, "apply")
        formal.validate_java_ready(
            ready,
            output,
            mode="apply",
            semantic_tool=semantic_tool,
            plan=plan,
            evidence=evidence,
        )
        formal.require_success_log(
            promotion_root / process["log"]["path"], "apply", semantic_tool
        )
        semantic = {
            "mode": "apply",
            "output": relative_stamp(output, promotion_root),
            "ready": relative_stamp(ready, promotion_root),
            "process": process["receipt"],
            "normalizedRows": formal.normalized_observations(rows),
        }
    except (PromotionError, ValueError, OSError) as exc:
        reasons.append(str(exc))
    return semantic, reasons


def promote(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    launch_gate = require_launch_gate()
    promotion_root = owner_root / "promotion"
    with guard.acquire_mutex() as lease:
        require(not promotion_root.exists(),
                "promotion attempt already exists; use recover-status")
        preflight()
        prepared = load_prepared(owner_root)
        guard.assert_quiescent(LIVE_PROJECT)
        current = guard.project_snapshot(LIVE_PROJECT)
        require(guard.same_project_snapshot(prepared["livePreimage"], current),
                "live project differs from the prepared PRE bytes")
        promotion_root.mkdir()
        require(promotion_root.is_dir() and not promotion_root.is_symlink(),
                "promotion root claim is unsafe")
        environment, cwd = environment_for(promotion_root)
        verifier = run_proof_verifier(promotion_root, "proof-verify", cwd, environment)
        live_pre = observe_pre(
            LIVE_PROJECT, promotion_root, "live-immediate-pre", cwd, environment
        )
        require(guard.same_project_snapshot(prepared["livePreimage"], live_pre["rawAfter"]),
                "live project differs after immediate PRE observation")
        pre_backup = prepared["preBackup"]
        pre_backup_recheck = observe_pre(
            Path(pre_backup["backupRoot"]), promotion_root,
            "pre-backup-recheck", cwd, environment,
        )
        pre_restore_recheck = observe_pre(
            Path(pre_backup["restoreRoot"]), promotion_root,
            "pre-restore-recheck", cwd, environment,
        )
        bundle_boundary = create_live_apply_bundle(promotion_root)
        bundle_root = Path(str(bundle_boundary["root"]))
        bundle_paths = live_apply_bundle_paths(bundle_root)
        bundle_lease = seal_live_apply_bundle(bundle_root)
        bundle_seal = dict(bundle_lease["record"])
        apply_root = promotion_root / "runs/live-apply"
        output = apply_root / "observations.tsv"
        java_ready = apply_root / "observations.ready.json"
        argv = fixed_apply_argv(
            LIVE_PROJECT,
            output,
            java_ready,
            semantic_tool=bundle_paths["semanticTool"],
            plan=bundle_paths["plan"],
            evidence=bundle_paths["evidence"],
        )
        apply_environment, apply_cwd, apply_context = create_fresh_process_context(
            promotion_root, "live-apply"
        )
        apply_runtime = {
            **verify_spawn_runtime(argv),
            "processContext": apply_context,
        }
        attempt = {
            "schema": ATTEMPT_SCHEMA,
            "startedAtUtc": utc_now(),
            "owner": owner_stamp(),
            "launchGate": launch_gate,
            "preparedReady": relative_stamp(owner_root / "prepared.ready.json", owner_root),
            "proofReady": {"path": str(PROOF_READY), "sha256": PROOF_READY_SHA256},
            "livePreimage": prepared["livePreimage"],
            "liveImmediatePre": live_pre,
            "preBackupRecheck": pre_backup_recheck,
            "preRestoreRecheck": pre_restore_recheck,
            "argv": argv,
            "runtimeBoundary": apply_runtime,
            "executionBundleSeal": bundle_seal,
            "mutationSpawnLimit": 1,
            "retryAuthorized": False,
            "automaticRestoreAuthorized": False,
            "mutex": {"name": lease.name, "abandoned": lease.abandoned},
        }
        intent_path = promotion_root / "attempt.started.json"
        write_json_new(intent_path, attempt)
        intent_sha256 = sha256_file(intent_path)
        intent_stamp = relative_stamp(intent_path, promotion_root)
        require(intent_stamp.get("sha256") == intent_sha256,
                "live apply intent stamp differs")
        frozen_attempt = require_frozen_json(
            intent_path, intent_sha256, attempt, "live apply intent"
        )
        frozen_argv = frozen_attempt.get("argv")
        frozen_runtime = frozen_attempt.get("runtimeBoundary")
        require(isinstance(frozen_argv, list) and all(
            isinstance(value, str) for value in frozen_argv
        ), "frozen live apply argv differs")
        require(isinstance(frozen_runtime, dict),
                "frozen live apply runtime boundary differs")
        require(
            {
                **verify_spawn_runtime(frozen_argv),
                "processContext": process_context_boundary(
                    promotion_root, "live-apply", apply_cwd, apply_environment
                ),
            } == frozen_runtime,
            "live apply runtime boundary changed before spawn",
        )
        verify_live_apply_bundle_seal(bundle_root, bundle_seal)
        intent_handle = seal_exact_file(
            intent_path, intent_sha256, "live apply intent"
        )
        checked_spawn_state: dict[str, object] = {
            "callbackCalls": 0,
            "delegateCalls": 0,
            "preSpawnQuiescence": None,
        }

        def checked_spawn(
            actual_argv: list[str],
            actual_cwd: Path,
            actual_environment: dict[str, str],
        ) -> tuple[object, int]:
            return checked_live_apply_spawn(
                promotion_root,
                intent_path,
                intent_sha256,
                frozen_attempt,
                actual_argv,
                actual_cwd,
                actual_environment,
                checked_spawn_state,
                spawn_inline_contained_process,
            )

        try:
            try:
                process, text = guard.run_contained(
                    session_root=promotion_root,
                    run_id="live-apply",
                    argv=list(frozen_argv),
                    cwd=apply_cwd,
                    environment=apply_environment,
                    timeout_seconds=900,
                    spawn=checked_spawn,
                )
            except (ValueError, OSError) as exc:
                raise PromotionError(str(exc)) from exc
            require_frozen_json(
                intent_path,
                intent_sha256,
                frozen_attempt,
                "live apply intent after spawn",
            )
            require(verify_live_apply_bundle(bundle_root) == bundle_boundary,
                    "execution bundle changed during live apply")
            verify_live_apply_bundle_seal(bundle_root, bundle_seal)
            apply_semantic, protocol_reasons = validate_apply_protocol(
                process,
                text,
                output,
                java_ready,
                promotion_root,
                semantic_tool=bundle_paths["semanticTool"],
                plan=bundle_paths["plan"],
                evidence=bundle_paths["evidence"],
            )
        finally:
            close_sealed_handles([
                intent_handle,
                *list(bundle_lease["handles"]),
            ])
        if checked_spawn_state.get("callbackCalls") != 1:
            protocol_reasons.append("live apply checked-spawn callback count differs")
        if checked_spawn_state.get("delegateCalls") != 1:
            protocol_reasons.append("live apply checked-spawn delegate count differs")
        if not isinstance(checked_spawn_state.get("preSpawnQuiescence"), dict):
            protocol_reasons.append("live apply pre-spawn quiescence is absent")

        state = ProjectState.UNKNOWN
        classification: dict[str, object] | None = None
        classification_error = ""
        try:
            state, classification = classify_project(
                LIVE_PROJECT, promotion_root, "live-post-classify", cwd, environment
            )
        except (PromotionError, ValueError, OSError) as exc:
            classification_error = str(exc)

        pre_inventory = prepared["finalObservation"]["inventory"]
        post_observation: dict[str, object] | None = None
        post_error = ""
        if state == ProjectState.POST:
            try:
                post_observation = observe_post(
                    LIVE_PROJECT,
                    promotion_root,
                    "live-post",
                    cwd,
                    environment,
                    pre_inventory=pre_inventory,
                    pre_root=owner_root,
                    apply_semantic=apply_semantic,
                )
                require(
                    classification is not None
                    and post_observation["rawAfter"] == classification["rawAfter"],
                    "full POST observation differs from initial classification",
                )
            except (PromotionError, ValueError, OSError) as exc:
                post_error = str(exc)
        elif state == ProjectState.PRE:
            try:
                observe_pre(
                    LIVE_PROJECT, promotion_root, "live-still-pre", cwd, environment
                )
            except (PromotionError, ValueError, OSError) as exc:
                post_error = str(exc)

        post_backup: dict[str, object] | None = None
        post_backup_error = ""
        if state == ProjectState.POST and post_observation is not None:
            try:
                post_backup = copy_and_drill(
                    promotion_root,
                    "post-live",
                    LIVE_PROJECT,
                    promotion_root / "backups/post-live",
                    promotion_root / "backups/post-live-restore-drill",
                    ProjectState.POST,
                    cwd,
                    environment,
                    pre_inventory=pre_inventory,
                    pre_root=owner_root,
                )
            except (PromotionError, ValueError, OSError) as exc:
                post_backup_error = str(exc)

        protocol = {
            "status": "COMPLETE" if not protocol_reasons else "PARTIAL",
            "reasons": protocol_reasons,
            "semantic": apply_semantic,
        }
        publish = bool(
            state == ProjectState.POST
            and protocol["status"] == "COMPLETE"
            and classification is not None
            and not classification_error
            and post_observation is not None
            and not post_error
            and post_backup is not None
            and not post_backup_error
        )
        result = {
            "schema": SCHEMA,
            "completedAtUtc": utc_now(),
            "state": state,
            "owner": owner_stamp(),
            "launchGate": launch_gate,
            "proofVerification": verifier,
            "attempt": intent_stamp,
            "preSpawnQuiescence": checked_spawn_state["preSpawnQuiescence"],
            "process": process["receipt"],
            "protocol": protocol,
            "classification": classification,
            "classificationError": classification_error,
            "postObservation": post_observation,
            "postObservationError": post_error,
            "postBackup": post_backup,
            "postBackupError": post_backup_error,
            "mutationSpawns": 1,
            "retryAuthorized": False,
            "automaticRestorePerformed": False,
            "trackedSnapshotRefreshed": False,
            "campaignPublicationAuthorized": publish,
        }
        if publish:
            validate_promotion_payload(result, owner_root)
        result_path = promotion_root / "promotion.result.json"
        write_json_new(result_path, result)
        if publish:
            frozen = formal.read_json(result_path, "new promotion result", canonical=True)
            require(frozen == result, "frozen promotion result differs")
            validate_promotion_payload(frozen, owner_root)
            ready_payload = {
                **frozen,
                "status": "READY",
                "result": relative_stamp(result_path, promotion_root),
            }
            ready_path = promotion_root / "promotion.ready.json"
            write_json_new(ready_path, ready_payload)
            verified = verify_artifacts(owner_root)
            require(verified.get("status") == "READY", "new promotion READY did not verify")
            result["ready"] = str(ready_path)
            result["readySha256"] = sha256_file(ready_path)
        return result


def validate_promotion_payload(value: object, owner_root: Path) -> dict[str, object]:
    require(isinstance(value, dict), "promotion result is absent")
    launch_gate = require_launch_gate()
    prepared = load_prepared(owner_root)
    promotion_root = owner_root / "promotion"
    require(set(value) == {
        "schema", "completedAtUtc", "state", "owner", "launchGate",
        "proofVerification", "attempt", "preSpawnQuiescence", "process",
        "protocol", "classification",
        "classificationError", "postObservation", "postObservationError",
        "postBackup", "postBackupError", "mutationSpawns", "retryAuthorized",
        "automaticRestorePerformed", "trackedSnapshotRefreshed",
        "campaignPublicationAuthorized",
    }, "promotion result fields differ")
    require(value.get("schema") == SCHEMA, "promotion result schema differs")
    validate_timestamp(value.get("completedAtUtc"), "promotion completion timestamp")
    require(value.get("state") == ProjectState.POST, "promotion result state differs")
    require(value.get("owner") == owner_stamp(), "promotion result owner differs")
    require(value.get("launchGate") == launch_gate, "promotion launch gate differs")
    require(value.get("mutationSpawns") == 1 and value.get("retryAuthorized") is False,
            "promotion mutation policy differs")
    require(value.get("automaticRestorePerformed") is False,
            "promotion restore policy differs")
    require(value.get("trackedSnapshotRefreshed") is False,
            "promotion improperly claims tracked-snapshot refresh")
    require(value.get("campaignPublicationAuthorized") is True,
            "promotion does not authorize campaign publication")
    for field in ("classificationError", "postObservationError", "postBackupError"):
        require(value.get(field) == "", f"promotion retains {field}")
    validate_proof_verification(
        value.get("proofVerification"), promotion_root, "promotion proof verification"
    )
    attempt_path = validate_exact_stamp(
        value.get("attempt"), promotion_root,
        promotion_root / "attempt.started.json", "apply intent",
    )
    attempt = formal.read_json(attempt_path, "apply intent", canonical=True)
    require(set(attempt) == {
        "schema", "startedAtUtc", "owner", "launchGate", "preparedReady",
        "proofReady", "livePreimage", "liveImmediatePre", "preBackupRecheck",
        "preRestoreRecheck", "argv", "runtimeBoundary", "executionBundleSeal",
        "mutationSpawnLimit", "retryAuthorized", "automaticRestoreAuthorized", "mutex",
    }, "apply-intent fields differ")
    require(attempt.get("schema") == ATTEMPT_SCHEMA, "apply-intent schema differs")
    validate_timestamp(attempt.get("startedAtUtc"), "apply-intent timestamp")
    require(attempt.get("owner") == owner_stamp(), "apply-intent owner differs")
    require(attempt.get("launchGate") == launch_gate, "apply-intent launch gate differs")
    require(attempt.get("proofReady") == {"path": str(PROOF_READY), "sha256": PROOF_READY_SHA256},
            "apply-intent proof differs")
    require(attempt.get("mutationSpawnLimit") == 1 and attempt.get("retryAuthorized") is False,
            "apply-intent mutation policy differs")
    require(attempt.get("automaticRestoreAuthorized") is False,
            "apply-intent restore policy differs")
    require(
        attempt.get("runtimeBoundary") == {
            **verify_spawn_runtime(attempt.get("argv", [])),
            "processContext": load_process_context_preflight(
                promotion_root, "live-apply"
            ),
        },
        "apply-intent runtime boundary differs",
    )
    runtime_boundary = attempt.get("runtimeBoundary")
    require(isinstance(runtime_boundary, dict),
            "apply-intent runtime boundary is absent")
    execution_bundle = runtime_boundary.get("executionBundle")
    require(isinstance(execution_bundle, dict),
            "apply-intent execution bundle is absent")
    bundle_root = Path(str(execution_bundle.get("root", "")))
    verify_live_apply_bundle_seal(
        bundle_root, attempt.get("executionBundleSeal", {})
    )
    bundle_paths = live_apply_bundle_paths(bundle_root)
    validate_exact_stamp(
        attempt.get("preparedReady"), owner_root,
        owner_root / "prepared.ready.json", "apply-intent prepared READY",
    )
    require(attempt.get("mutex") == {"name": MUTEX_NAME, "abandoned": False},
            "apply-intent mutex differs")
    validate_observation(
        attempt.get("liveImmediatePre"), promotion_root, "apply-intent live PRE",
        project=LIVE_PROJECT, state=ProjectState.PRE, check_current=False,
    )
    pre_backup = prepared["preBackup"]
    validate_observation(
        attempt.get("preBackupRecheck"), promotion_root, "apply-intent backup PRE",
        project=Path(pre_backup["backupRoot"]), state=ProjectState.PRE,
    )
    validate_observation(
        attempt.get("preRestoreRecheck"), promotion_root, "apply-intent restore PRE",
        project=Path(pre_backup["restoreRoot"]), state=ProjectState.PRE,
    )
    require(attempt.get("livePreimage") == prepared["livePreimage"],
            "apply-intent PRE differs from preparation")
    validate_quiescence(
        value.get("preSpawnQuiescence"),
        "published live apply pre-spawn quiescence",
        fileset=str(prepared["livePreimage"]["fileSetSha256"]),
    )

    protocol = value.get("protocol")
    require(isinstance(protocol, dict) and protocol.get("status") == "COMPLETE",
            "promotion protocol is incomplete")
    require(set(protocol) == {"status", "reasons", "semantic"},
            "promotion protocol fields differ")
    require(protocol.get("reasons") == [], "promotion protocol retains failure reasons")
    semantic_value = protocol.get("semantic")
    semantic = validate_semantic_payload(
        semantic_value,
        promotion_root,
        "published apply",
        project=LIVE_PROJECT,
        mode="apply",
        semantic_tool=bundle_paths["semanticTool"],
        plan=bundle_paths["plan"],
        evidence=bundle_paths["evidence"],
    )
    process = validate_process_stamp(value.get("process"), promotion_root, "published apply process")
    require(process == semantic["process"], "published apply process differs from semantic receipt")
    require(attempt.get("argv") == process.get("argv"), "apply process differs from immutable intent")

    classification = value.get("classification")
    validate_classification(
        classification,
        promotion_root,
        "published POST classification",
        project=LIVE_PROJECT,
        state=ProjectState.POST,
    )
    post = value.get("postObservation")
    post_validated = validate_observation(
        post,
        promotion_root,
        "published live POST",
        project=LIVE_PROJECT,
        state=ProjectState.POST,
        pre_inventory=prepared["finalObservation"]["inventory"],
        pre_root=owner_root,
    )
    require(post["rawAfter"] == classification["rawAfter"],
            "published POST differs from classification")
    require(
        post_validated["semantic"]["normalizedRows"] == semantic["normalizedRows"],
        "published apply/readback semantic rows differ",
    )
    backup = value.get("postBackup")
    validate_copy_payload(
        backup,
        promotion_root,
        "published POST backup",
        state=ProjectState.POST,
        pre_inventory=prepared["finalObservation"]["inventory"],
        pre_root=owner_root,
    )
    require(backup["sourceSnapshot"] == post["rawAfter"],
            "published POST backup source differs from live POST")
    validate_mutation_census(owner_root, expected=1)
    return {
        "state": ProjectState.POST,
        "functions": 8124,
        "changedFunctions": list(formal.ADDRESSES),
        "proofReadySha256": PROOF_READY_SHA256,
    }


def recover_status(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    launch_gate = require_launch_gate()
    require((owner_root / "prepared.ready.json").is_file(), "prepared READY is absent")
    recovery_root = owner_root / "recoveries" / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    )
    guard.envelope.ensure_plain_directory(recovery_root, "target-lock recovery root")
    state = ProjectState.UNKNOWN
    observation: dict[str, object] | None = None
    error = ""
    mutex: dict[str, object] = {"name": MUTEX_NAME, "abandoned": None}
    try:
        with guard.acquire_mutex(allow_abandoned=True) as lease:
            mutex = {"name": lease.name, "abandoned": lease.abandoned}
            preflight()
            prepared = load_prepared(owner_root)
            environment, cwd = environment_for(recovery_root)
            state, classification = classify_project(
                LIVE_PROJECT, recovery_root, "live-recovery-classify", cwd, environment
            )
            if state == ProjectState.PRE:
                observation = observe_pre(
                    LIVE_PROJECT, recovery_root, "live-recovery-pre", cwd, environment
                )
            elif state == ProjectState.POST:
                observation = observe_post(
                    LIVE_PROJECT,
                    recovery_root,
                    "live-recovery-post",
                    cwd,
                    environment,
                    pre_inventory=prepared["finalObservation"]["inventory"],
                    pre_root=owner_root,
                )
            else:
                observation = classification
    except (PromotionError, ValueError, OSError) as exc:
        error = str(exc)
        state = ProjectState.UNKNOWN
    receipt = {
        "schema": RECOVERY_SCHEMA,
        "observedAtUtc": utc_now(),
        "state": state,
        "launchGate": launch_gate,
        "mutex": mutex,
        "observation": observation,
        "observationError": error,
        "mutationSpawns": 0,
        "retryAuthorized": False,
        "automaticRestorePerformed": False,
        "backupCreated": False,
    }
    path = recovery_root / "recovery.ready.json"
    write_json_new(path, receipt)
    return {**receipt, "ready": str(path), "readySha256": sha256_file(path)}


def verify_artifacts(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    require_launch_gate()
    prepared = load_prepared(owner_root)
    promotion_root = owner_root / "promotion"
    ready_path = promotion_root / "promotion.ready.json"
    if not ready_path.is_file():
        if promotion_root.exists():
            raise PromotionError(
                "promotion was attempted but has no READY; use recover-status and do not retry"
            )
        guard.assert_quiescent(LIVE_PROJECT)
        current = guard.project_snapshot(LIVE_PROJECT)
        require(guard.same_project_snapshot(current, prepared["livePreimage"]),
                "live project differs from prepared PRE bytes")
        return {
            "status": "PREPARED",
            "preparedAtUtc": prepared["preparedAtUtc"],
            "livePreimageVerified": True,
            "liveMutationAuthorized": False,
        }
    require(not ready_path.is_symlink() and ready_path.stat().st_nlink == 1,
            "promotion READY is unsafe")
    ready = formal.read_json(ready_path, "promotion READY", canonical=True)
    require(ready.get("status") == "READY", "promotion READY status differs")
    result_path = validate_exact_stamp(
        ready.get("result"), promotion_root,
        promotion_root / "promotion.result.json", "promotion result",
    )
    result = formal.read_json(result_path, "promotion result", canonical=True)
    expected = {**result, "status": "READY", "result": ready.get("result")}
    require(ready == expected, "promotion READY differs from frozen result")
    summary = validate_promotion_payload(result, owner_root)
    return {
        **summary,
        "status": "READY",
        "promotionReadySha256": sha256_file(ready_path),
        "campaignPublicationAuthorized": True,
        "liveMutationAuthorized": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("prepare", "promote", "recover-status", "verify")
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare()
        elif args.command == "promote":
            result = promote()
        elif args.command == "recover-status":
            result = recover_status()
        else:
            result = verify_artifacts()
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
        if args.command == "promote" and result.get("campaignPublicationAuthorized") is not True:
            return 10
        return 0
    except (PromotionError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "REFUSED", "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
