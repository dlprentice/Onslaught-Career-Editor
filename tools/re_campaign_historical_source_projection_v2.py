#!/usr/bin/env python3
"""Replay frozen campaigns under exact, reviewed historical source inputs.

Generation 24 is immutable, but two later rebuild improvements legitimately
changed source files that older campaign overlays identity-pin.  This launcher
keeps those layers separate: it first proves the exact current source and its
focused tests, then projects only the historical bytes into the frozen
verifier's read path.  It never writes projected bytes to the checkout and
never changes a campaign, proof, reducer, or Ghidra project.
"""

from __future__ import annotations

import argparse
import builtins
import contextlib
import difflib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

SCHEMA = "bea.re.campaign-historical-source-projection-audit.v2"
OLD_OWNER_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-replay-audit-20260812-v1/historical_source_projection.py"
)
OLD_OWNER_BYTES = 17_579
OLD_OWNER_SHA256 = (
    "e16faa93d2820f7c5a57d135dea1bcfec9818c683f2cca4057b9c43155673aec"
)

ACTOR_HISTORICAL_COMMIT = "e7aa7548fe99ff7866f57955624968b097375e20"
ACTOR_RUNTIME_RELATIVE = Path(
    "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs"
)
ACTOR_RUNTIME_HISTORICAL_BYTES = 31_466
ACTOR_RUNTIME_HISTORICAL_SHA256 = (
    "7942536b60d3bab2d0e534f2030fa74b4329b3bf9c2c19324e244c91aa33597b"
)
ACTOR_RUNTIME_CURRENT_BYTES = 32_010
ACTOR_RUNTIME_CURRENT_SHA256 = (
    "8f8692250e70eea6bea0702dfd56d1c3c90ad17dd8dffd65acf639cec4ba6197"
)
ACTOR_TEST_RELATIVE = Path(
    "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs"
)
ACTOR_TEST_HISTORICAL_SOURCE_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-23-cround-handle-event-arm-effects-v1/_reducer/"
    "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs"
)
ACTOR_TEST_HISTORICAL_BYTES = 17_883
ACTOR_TEST_HISTORICAL_SHA256 = (
    "2232bde202407035adc81317058b5594ad69e038d0889e8fb2762058d7e7529c"
)
ACTOR_TEST_CURRENT_BYTES = 17_484
ACTOR_TEST_CURRENT_SHA256 = (
    "cb64be81481a0d6712a13d7f7a16449974d38ba047617444b6f96c9d024c2bfc"
)
SIMULATION_TEST_RELATIVE = Path(
    "rebuild/OnslaughtRebuild.Core.Tests/SimulationTests.cs"
)
SIMULATION_TEST_CURRENT_BYTES = 77_231
SIMULATION_TEST_CURRENT_SHA256 = (
    "bbb31414efe6c36e7fd8ba52eafb4135995671863e91b0a59062874c2c40dd06"
)
CURRENT_FOCUSED_FILTER = (
    "FullyQualifiedName~Level100PlayerDamageTests|"
    "FullyQualifiedName~Level100ActorWeaponTests|"
    "FullyQualifiedName~SimulationTests."
    "PlayerProjectilesConsumeReleasedScatterInRetailDrawOrder"
)
PROOF_AUTHOR_BYTES = 41_785
PROOF_AUTHOR_SHA256 = (
    "8e8c22d3dbb31c7464ad47c211a5179d773aabd9dd665aa4960ee7aa7a0b47e9"
)
PROOF_READY_BYTES = 2_529
PROOF_READY_SHA256 = (
    "ffb2e0b8692ddada364a829d52a158841e5d800742c49bd2a1710b2af135869a"
)


class ProjectionError(RuntimeError):
    """The current-source, historical-input, or replay gate did not hold."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProjectionError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, root: Path) -> dict[str, Any]:
    resolved = path.resolve()
    try:
        display = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        display = os.fspath(resolved)
    return {
        "path": display,
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def _load_old_owner(root: Path) -> ModuleType:
    owner = root / OLD_OWNER_RELATIVE
    require(owner.is_file(), "historical Generation 12 projection owner is missing")
    info = owner.lstat()
    require(
        not owner.is_symlink()
        and not (getattr(info, "st_file_attributes", 0) & 0x400)
        and info.st_nlink == 1
        and (info.st_size, sha256_file(owner))
        == (OLD_OWNER_BYTES, OLD_OWNER_SHA256),
        "historical Generation 12 projection owner identity differs",
    )
    spec = importlib.util.spec_from_file_location(
        "_bea_historical_source_projection_v1", owner
    )
    require(spec is not None and spec.loader is not None, "cannot load v1 owner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exact_bytes(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> bytes:
    require(path.is_file(), f"{label} is missing")
    data = path.read_bytes()
    require(
        (len(data), sha256_bytes(data)) == (expected_bytes, expected_sha256),
        f"{label} identity differs",
    )
    return data


def validate_actor_continuity(
    root: Path, old_owner: ModuleType
) -> tuple[dict[Path, bytes], dict[str, Any]]:
    historical_runtime = old_owner.git_blob(
        root, ACTOR_HISTORICAL_COMMIT, ACTOR_RUNTIME_RELATIVE
    )
    require(
        (len(historical_runtime), sha256_bytes(historical_runtime))
        == (ACTOR_RUNTIME_HISTORICAL_BYTES, ACTOR_RUNTIME_HISTORICAL_SHA256),
        "historical actor-weapon runtime Git blob differs",
    )
    current_runtime = _exact_bytes(
        root / ACTOR_RUNTIME_RELATIVE,
        ACTOR_RUNTIME_CURRENT_BYTES,
        ACTOR_RUNTIME_CURRENT_SHA256,
        "current actor-weapon runtime",
    )

    historical_test_path = root / ACTOR_TEST_HISTORICAL_SOURCE_RELATIVE
    historical_test = _exact_bytes(
        historical_test_path,
        ACTOR_TEST_HISTORICAL_BYTES,
        ACTOR_TEST_HISTORICAL_SHA256,
        "retained historical actor-weapon test input",
    )
    current_test = _exact_bytes(
        root / ACTOR_TEST_RELATIVE,
        ACTOR_TEST_CURRENT_BYTES,
        ACTOR_TEST_CURRENT_SHA256,
        "current actor-weapon test",
    )
    require(
        historical_test.replace(b"\r\n", b"\n") == current_test,
        "historical actor-weapon test does not normalize to current Git bytes",
    )
    require(
        historical_test.count(b"\r\n") == 399
        and historical_test.count(b"\n") == 415,
        "historical actor-weapon mixed-EOL census differs",
    )
    _exact_bytes(
        root / SIMULATION_TEST_RELATIVE,
        SIMULATION_TEST_CURRENT_BYTES,
        SIMULATION_TEST_CURRENT_SHA256,
        "current simulation scatter test owner",
    )

    old_lines = historical_runtime.decode("utf-8").splitlines(keepends=True)
    new_lines = current_runtime.decode("utf-8").splitlines(keepends=True)
    opcodes = difflib.SequenceMatcher(None, old_lines, new_lines).get_opcodes()
    inserted = sum(
        j2 - j1
        for tag, _i1, _i2, j1, j2 in opcodes
        if tag in {"insert", "replace"}
    )
    deleted = sum(
        i2 - i1
        for tag, i1, i2, _j1, _j2 in opcodes
        if tag in {"delete", "replace"}
    )
    retained = sum(i2 - i1 for tag, i1, i2, _j1, _j2 in opcodes if tag == "equal")
    require(
        (inserted, deleted, retained, len(old_lines), len(new_lines))
        == (19, 6, 751, 757, 770),
        "reviewed actor-weapon helper-extraction line relationship differs",
    )

    return (
        {
            ACTOR_RUNTIME_RELATIVE: historical_runtime,
            ACTOR_TEST_RELATIVE: historical_test,
        },
        {
            "historicalCommit": ACTOR_HISTORICAL_COMMIT,
            "historicalRuntime": {
                "path": ACTOR_RUNTIME_RELATIVE.as_posix(),
                "bytes": len(historical_runtime),
                "sha256": sha256_bytes(historical_runtime),
            },
            "currentRuntime": stamp(root / ACTOR_RUNTIME_RELATIVE, root),
            "runtimeRelationship": {
                "classification": "EXACT_REVIEWED_HELPER_EXTRACTION",
                "insertedLines": inserted,
                "deletedLines": deleted,
                "historicalLinesRetained": retained,
                "behaviorEquivalenceClaimedByDiffAlone": False,
            },
            "historicalTest": stamp(historical_test_path, root),
            "currentTest": stamp(root / ACTOR_TEST_RELATIVE, root),
            "testRelationship": {
                "classification": "MIXED_EOL_SNAPSHOT_NORMALIZES_TO_GIT_BYTES",
                "crlfLineEndings": historical_test.count(b"\r\n"),
                "totalLineEndings": historical_test.count(b"\n"),
                "normalizedByteIdentical": True,
            },
            "currentSimulationScatterTest": stamp(
                root / SIMULATION_TEST_RELATIVE, root
            ),
        },
    )


def _run(
    arguments: list[str], *, cwd: Path, timeout: int
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def validate_current(root: Path, old_owner: ModuleType) -> dict[str, Any]:
    completed = _run(
        [
            "dotnet",
            "test",
            "rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj",
            "--filter",
            CURRENT_FOCUSED_FILTER,
            "--no-restore",
            "--nologo",
        ],
        cwd=root,
        timeout=300,
    )
    output = completed.stdout + completed.stderr
    require(completed.returncode == 0, "current focused rebuild suite failed")
    match = re.search(
        r"Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)",
        output,
    )
    require(match is not None, "current focused rebuild census is absent")
    failed, passed, skipped, total = map(int, match.groups())
    require(
        (failed, passed, skipped, total) == (0, 30, 0, 30),
        "current focused rebuild census differs",
    )
    proof_author = root / old_owner.PROOF_AUTHOR_RELATIVE
    proof_ready = root / old_owner.PROOF_ROOT_RELATIVE / "proof.ready.json"
    _exact_bytes(
        proof_author,
        PROOF_AUTHOR_BYTES,
        PROOF_AUTHOR_SHA256,
        "frozen player-damage proof author",
    )
    _exact_bytes(
        proof_ready,
        PROOF_READY_BYTES,
        PROOF_READY_SHA256,
        "frozen player-damage proof receipt",
    )
    current_player_test = root / old_owner.TEST_RELATIVE
    require(
        sha256_file(current_player_test) != old_owner.HISTORICAL_TEST_SHA256,
        "current player-damage test unexpectedly equals the historical input",
    )
    return {
        "focusedRebuild": {
            "exitCode": completed.returncode,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": total,
            "filter": CURRENT_FOCUSED_FILTER,
            "stdoutSha256": sha256_bytes(completed.stdout.encode("utf-8")),
            "stderrSha256": sha256_bytes(completed.stderr.encode("utf-8")),
        },
        "frozenPlayerDamageProof": {
            "author": stamp(proof_author, root),
            "receipt": stamp(proof_ready, root),
            "expectsHistoricalTestSha256": old_owner.HISTORICAL_TEST_SHA256,
            "currentTestSha256": sha256_file(current_player_test),
            "currentIdentityRejectedByExactInputGate": True,
        },
    }


def is_bootstrap_invocation(arguments: object) -> tuple[list[str], int] | None:
    if not isinstance(arguments, (list, tuple)):
        return None
    values = [os.fspath(value) for value in arguments]
    for index, value in enumerate(values):
        if value.replace("\\", "/").lower().endswith(
            "/re_campaign_frozen_bootstrap.py"
        ):
            return values, index
    return None


def replay_with_projections(
    root: Path,
    projections: dict[Path, bytes],
    campaign: Path,
    mode: str,
    expected_ready_sha256: str,
    expected_reducer_id: str,
    old_owner: ModuleType,
) -> tuple[int, str, str]:
    bootstrap_path = root / old_owner.BOOTSTRAP_RELATIVE
    require(
        (bootstrap_path.stat().st_size, sha256_file(bootstrap_path))
        == (old_owner.BOOTSTRAP_BYTES, old_owner.BOOTSTRAP_SHA256),
        "frozen bootstrap identity differs",
    )
    resolved = {
        os.path.normcase(os.fspath((root / relative).resolve())): data
        for relative, data in projections.items()
    }
    original_path_open = pathlib.Path.open
    original_path_stat = pathlib.Path.stat
    original_builtin_open = builtins.open
    original_subprocess_run = subprocess.run

    def projected_data(path: os.PathLike[str] | str) -> bytes | None:
        key = os.path.normcase(os.path.abspath(os.fspath(path)))
        return resolved.get(key)

    def projected_open(
        self: pathlib.Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ):
        data = projected_data(self)
        if data is None:
            return original_path_open(
                self, mode, buffering, encoding, errors, newline
            )
        if any(flag in mode for flag in "wax+"):
            raise OSError("historical source projection is read-only")
        if "b" in mode:
            return io.BytesIO(data)
        return io.StringIO(
            data.decode(encoding or "utf-8", errors or "strict"), newline=newline
        )

    def projected_stat(
        self: pathlib.Path, *, follow_symlinks: bool = True
    ) -> os.stat_result:
        value = original_path_stat(self, follow_symlinks=follow_symlinks)
        data = projected_data(self)
        if data is None:
            return value
        fields = list(value)
        fields[6] = len(data)
        return os.stat_result(fields)

    def projected_builtin_open(
        file: int | os.PathLike[str] | str,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
        closefd: bool = True,
        opener: Any = None,
    ):
        data = None if isinstance(file, int) else projected_data(file)
        if data is None:
            return original_builtin_open(
                file, mode, buffering, encoding, errors, newline, closefd, opener
            )
        if any(flag in mode for flag in "wax+"):
            raise OSError("historical source projection is read-only")
        if "b" in mode:
            return io.BytesIO(data)
        return io.StringIO(
            data.decode(encoding or "utf-8", errors or "strict"), newline=newline
        )

    wrapper_path = Path(__file__).resolve()

    def projected_subprocess_run(
        arguments: object, *args: object, **kwargs: object
    ):
        detected = is_bootstrap_invocation(arguments)
        if detected is None:
            return original_subprocess_run(arguments, *args, **kwargs)
        values, index = detected
        replacement = [
            sys.executable,
            "-I",
            "-B",
            os.fspath(wrapper_path),
            *values[index + 1 :],
        ]
        return original_subprocess_run(replacement, *args, **kwargs)

    environment_start = os.environ.copy()
    cwd_start = Path.cwd()
    pathlib.Path.open = projected_open
    pathlib.Path.stat = projected_stat
    builtins.open = projected_builtin_open
    try:
        os.environ["BEA_REPO_ROOT"] = os.fspath(root)
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        os.chdir(root)
        spec = importlib.util.spec_from_file_location(
            "_bea_historical_source_projection_v2_bootstrap", bootstrap_path
        )
        require(spec is not None and spec.loader is not None, "cannot load bootstrap")
        bootstrap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bootstrap)
        bootstrap.ORIGINAL_SUBPROCESS_RUN = projected_subprocess_run
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = bootstrap.main(
                [
                    "--campaign",
                    os.fspath(campaign),
                    "--mode",
                    mode,
                    "--expected-ready-sha256",
                    expected_ready_sha256,
                    "--expected-reducer-id",
                    expected_reducer_id,
                ]
            )
        return exit_code, stdout.getvalue(), stderr.getvalue()
    finally:
        builtins.open = original_builtin_open
        pathlib.Path.open = original_path_open
        pathlib.Path.stat = original_path_stat
        os.chdir(cwd_start)
        os.environ.clear()
        os.environ.update(environment_start)


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    require(not path.exists(), f"refusing existing audit receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{path.name}.", dir=path.parent))
    try:
        staged = stage / path.name
        staged.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(staged, path)
    finally:
        try:
            stage.rmdir()
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--mode", choices=("full", "integrity"), default="full")
    parser.add_argument("--expected-ready-sha256", required=True)
    parser.add_argument("--expected-reducer-id", required=True)
    parser.add_argument("--check-current", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)
    try:
        configured = os.environ.get("BEA_REPO_ROOT")
        root = Path(configured).resolve() if configured else Path.cwd().resolve()
        require((root / ".git").exists(), "BEA repository root is not selected")
        campaign = args.campaign
        if not campaign.is_absolute():
            campaign = root / campaign
        campaign = campaign.resolve()
        ready_path = campaign / "campaign.ready.json"
        require(ready_path.is_file(), "campaign READY is missing")
        require(
            sha256_file(ready_path) == args.expected_ready_sha256.lower(),
            "campaign READY differs from the external pin",
        )
        ready = json.loads(ready_path.read_text(encoding="utf-8"))
        require(
            ready.get("reducer", {}).get("id") == args.expected_reducer_id,
            "campaign reducer differs from the external pin",
        )

        old_owner = _load_old_owner(root)
        try:
            historical_player_test, player_continuity = (
                old_owner.validate_continuity(root)
            )
            actor_projections, actor_continuity = validate_actor_continuity(
                root, old_owner
            )
        except old_owner.AuditError as exc:
            raise ProjectionError(str(exc)) from exc
        projections = {
            old_owner.TEST_RELATIVE: historical_player_test,
            **actor_projections,
        }
        current_validation = None
        if args.check_current:
            current_validation = validate_current(root, old_owner)

        before = {
            relative.as_posix(): (root / relative).read_bytes()
            for relative in projections
        }
        exit_code, stdout, stderr = replay_with_projections(
            root,
            projections,
            campaign,
            args.mode,
            args.expected_ready_sha256.lower(),
            args.expected_reducer_id,
            old_owner,
        )
        after = {
            relative.as_posix(): (root / relative).read_bytes()
            for relative in projections
        }
        require(before == after, "current source input changed during replay")
        marker = (
            "CAMPAIGN_VERIFIED"
            if args.mode == "full"
            else "FROZEN_CAMPAIGN_INTEGRITY_VERIFIED"
        )
        require(
            exit_code == 0 and marker in stdout,
            "projected frozen campaign replay failed: "
            f"exit={exit_code} stdout={stdout[-1200:]!r} stderr={stderr[-1200:]!r}",
        )

        receipt = {
            "schema": SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "verdict": "PASS",
            "instrument": stamp(Path(__file__), root),
            "generation12ProjectionOwner": stamp(root / OLD_OWNER_RELATIVE, root),
            "continuity": {
                "playerDamage": player_continuity,
                "actorWeapon": actor_continuity,
            },
            "currentValidation": current_validation,
            "projection": {
                "kind": "IN_MEMORY_READ_ONLY_THREE_FILE",
                "paths": [relative.as_posix() for relative in projections],
                "writesToCheckout": False,
                "frozenArtifactsChanged": False,
            },
            "campaign": {
                "root": os.fspath(campaign),
                "generation": ready.get("generation"),
                "mode": args.mode.upper(),
                "ready": stamp(ready_path, root),
                "reducerId": args.expected_reducer_id,
            },
            "result": {
                "exitCode": exit_code,
                "stdoutSha256": sha256_bytes(stdout.encode("utf-8")),
                "stderrSha256": sha256_bytes(stderr.encode("utf-8")),
                "marker": stdout.strip().splitlines()[-1],
            },
            "limitations": [
                "This proves the frozen campaign only under its exact historical source inputs; it does not repin or reinterpret Generation 24.",
                "Current rebuild behavior is checked only when --check-current is selected and only by the named focused suites.",
                "No executable, Ghidra project, runtime trace, or retail asset is mutated or reinterpreted by this projection.",
            ],
        }
        if args.receipt:
            receipt_path = args.receipt
            if not receipt_path.is_absolute():
                receipt_path = root / receipt_path
            write_receipt(receipt_path.resolve(), receipt)
        if stdout:
            print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)
        print(
            "HISTORICAL_SOURCE_PROJECTION_V2_PASS "
            f"generation={ready.get('generation')} mode={args.mode} "
            f"projected={len(projections)}"
        )
        return 0
    except (
        ProjectionError,
        OSError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"HISTORICAL_SOURCE_PROJECTION_V2_BLOCKED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
