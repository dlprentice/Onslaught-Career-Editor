#!/usr/bin/env python3
"""Run and finalize a tool-bound disposable Ghidra boundary-promotion proof.

This owner deliberately stops at scratch-project evidence.  It never accepts a
maintainer project path, never assigns names, and never authorizes a live
promotion.  Every Ghidra run executes evidence-owned script snapshots whose
bytes are measured by the scripts themselves in the resulting logs.
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "bea.re.ghidra-function-promotion-scratch-proof.v4"
READY_SCHEMA = "bea-ghidra-function-promotion.v2"
BACKUP_SCHEMA = "onslaught-ghidra-project-backup.v2"
BOUNDARY_READY_SCHEMA = "bea.re.boundary-targets.v1"
CAMPAIGN_SCHEMA = "bea.re.campaign.v5"
CAMPAIGN_REDUCER_SCHEMA = "bea.re.campaign-reducer.v1"
CAMPAIGN_REDUCER_ENTRY = "_reducer/tools/re_campaign.py"
CAMPAIGN_REDUCER_ID = (
    "3aee494a4c8daccb356e984b88067a0c0b42b8ae89e0d167a4351e3be7cdc74a"
)
CAMPAIGN_REPLAY_SCHEMA = "bea.re.campaign-source-replay.v1"
COVERAGE_READY_SCHEMA = "bea.re.coverage-ledger-ready.v1"
BASE_PROJECT_FILE_SET_SHA256 = (
    "32937f7c749b5ed434f015c458832fb8aebfb023ff7cad31182cef16a1808622"
)
ANALYZE_HEADLESS_SHA256 = (
    "dd7b9d17d32ed70a71df82a43a21cdaed6c4ce67064e30f8642c149f81c2ae07"
)
GHIDRA_APPLICATION_PROPERTIES_SHA256 = (
    "80890f309379ef60ecbb376a95448bd79e874145544ffcfabb5ba1835ac8a2cf"
)
HOST_JAVA_SHA256 = (
    "5f6248f9c0f32b38ffaba813819bf3331536a48c7ddc45b18e73acd15a6cf7ef"
)
GHIDRA_DISTRIBUTION_FILE_COUNT = 5226
GHIDRA_DISTRIBUTION_TOTAL_BYTES = 914252158
GHIDRA_DISTRIBUTION_FILE_SET_SHA256 = (
    "5e80e03104d22011ff89429d39d2a83d7e5e56dae6e7e6b0fa2d4c08e674500c"
)
JDK_DISTRIBUTION_FILE_COUNT = 490
JDK_DISTRIBUTION_TOTAL_BYTES = 343604705
JDK_DISTRIBUTION_FILE_SET_SHA256 = (
    "af26450b182c8d085ed3efcae7bb3068f1e002b53f2db2f4111910cb455b39bf"
)
PYTHON_SHA256 = (
    "fda7026477256845afab371e354c4d512896665f1761939cb5887d0a9dec257a"
)
PYTHON_DISTRIBUTION_FILE_COUNT = 11683
PYTHON_DISTRIBUTION_TOTAL_BYTES = 533160307
PYTHON_DISTRIBUTION_FILE_SET_SHA256 = (
    "e43602c0684213f4fb9e1f1c8de2d38cef55345e9ab7a6b061a0e34b1b131d7e"
)
WINDOWS_SYSTEM_ROOT = Path(r"C:\Windows")
WINDOWS_COMMAND_PROCESSOR_SHA256 = (
    "8dd1ebb0b969370c70a5ee7f7ee347949aa7046aa5e1a33fcd7b1e9415b21fc3"
)
TRUSTED_TOOL_SHA256 = {
    "promotion": "1c3d6820a7f4d06fe3b08601a0878b4a3ec2acfce7390f32e3105756829bafe9",
    "inventory": "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
    "backup": "36969a237eef29fea0daa52fe4a657127bdbbb5091523c9ca7cd92c69566b452",
    "diff": "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460",
}
TRUSTED_TOOL_NAMES = {
    "promotion": "CreateFunctionsFromAddressList.java",
    "inventory": "ExportFullFunctionInventory.java",
    "backup": "ghidra_project_backup.py",
    "diff": "ghidra_inventory_diff.py",
}
BOUNDARY_TARGET_SHA256 = (
    "fe19c8c0214516b5ff61aefd13b9cffb47f2ae91ffd3d1526bb51b561ee9035d"
)
BOUNDARY_TARGET_READY_SHA256 = (
    "22f1a983cf7a9111fb090eb9ef72b1164381cf66ebd799ba60f4b961ba9e8377"
)
BOUNDARY_SOURCE_CAMPAIGN_READY_SHA256 = (
    "5b8a71deea790db29627984e50f03ca71e5b585ab6b0fb283d2cb7a7d6fd5e5d"
)
BOUNDARY_TARGET_COUNT = 40
GHIDRA_SETTINGS_DIRECTORY = "ghidra_12.1.2_PUBLIC"
PYTHON_ISOLATION_FLAGS = ("-I", "-B")
PROGRAM_NAME = "BEA.exe"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
IMAGE_BASE = "0x00400000"
LANGUAGE = "x86:LE:32:default"
COMPILER_SPEC = "windows"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
ERROR_MARKERS = (
    "REPORT SCRIPT ERROR",
    "FUNCTION_PROMOTION_RECEIPT_LOST",
    "FUNCTION_PROMOTION_FAIL",
    "Exception",
)
RUN_IDS = (
    "copy-main",
    "copy-poison",
    "main-baseline",
    "main-dry",
    "guard-undefined",
    "guard-inside-existing",
    "inspect-poison-pre",
    "poison-baseline",
    "poison-wrong-sha",
    "inspect-poison-post",
    "poison-after",
    "inspect-main-preapply",
    "main-apply",
    "main-readback",
    "main-after",
    "diff-main-inventory",
    "inspect-main-postverification",
)
CLAIM_BOUNDARY = (
    "The exact snapshotted promotion tool was observed creating the reviewed function entries on a disposable backup clone.",
    "In the exported function/program view, only the target function rows were added: no semantic names were assigned, every pre-existing function row remained byte-identical, and all non-function-count program metrics remained unchanged.",
    "The poisoned-SHA writable control may rotate raw Ghidra storage, but its full function and program inventories remain byte-identical.",
    "The inventory hashes memory block ranges/selected metadata/bytes, instruction placement and flow, defined-data placement/type/value representation, explicit stored non-function symbols (not derived dynamic labels), references, listing comments within program memory, and function/repeatable comments, but is not a digest of every possible Ghidra record; global data-type archives, options, bookmarks, property maps, and other unexported payloads remain outside this claim.",
    "This scratch proof does not authorize or perform a maintainer-project mutation and does not independently prove every inferred function body range.",
    "This is unsigned machine-local evidence for a trusted, quiescent host: it detects at-rest drift in bound artifacts and exported state, but is not archival, portable, resistant to a concurrent hostile local actor or OS-level interception, or evidence that the proof preceded a historical mutation.",
)
CAMPAIGN_OUTPUTS = (
    "campaign-functions.tsv",
    "campaign-residuals.tsv",
    "campaign-questions.tsv",
    "campaign-scenarios.tsv",
    "campaign-levers.tsv",
    "campaign-contracts.tsv",
    "campaign-adjudications.tsv",
    "campaign-supersessions.tsv",
)


class ProofError(ValueError):
    """Raised when a scratch proof fails closed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def is_reparse_point(path: Path) -> bool:
    info = path.lstat()
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction() or bool(attributes & reparse_flag)


def require_plain_existing_ancestors(path: Path, label: str) -> Path:
    lexical = lexical_absolute(path)
    for component in reversed((lexical, *lexical.parents)):
        if os.path.lexists(component) and is_reparse_point(component):
            raise ProofError(f"{label} contains a symlink, junction, or reparse point: {component}")
    return lexical


def require_plain_file(path: Path, label: str, *, single_link: bool) -> Path:
    path = require_plain_existing_ancestors(path, label)
    if not path.is_file():
        raise ProofError(f"{label} is not a regular file: {path}")
    info = path.stat(follow_symlinks=False)
    if single_link and getattr(info, "st_nlink", 1) != 1:
        raise ProofError(f"{label} is a hardlinked file: {path}")
    return path


def safe_tree_files(
    root: Path, label: str, *, single_link: bool
) -> list[Path]:
    root = require_plain_existing_ancestors(root, label)
    if not root.is_dir():
        raise ProofError(f"{label} is not a directory: {root}")
    files: list[Path] = []
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold())
        except OSError as exc:
            raise ProofError(f"{label} cannot be enumerated: {directory}") from exc
        for entry in entries:
            path = Path(entry.path)
            try:
                info = path.lstat()
            except OSError as exc:
                raise ProofError(f"{label} entry cannot be inspected: {path}") from exc
            attributes = getattr(info, "st_file_attributes", 0)
            reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            if entry.is_symlink() or bool(attributes & reparse_flag):
                raise ProofError(
                    f"{label} contains a symlink, junction, or reparse point: {path}"
                )
            if entry.is_dir(follow_symlinks=False):
                pending.append(path)
            elif entry.is_file(follow_symlinks=False):
                if single_link and getattr(info, "st_nlink", 1) != 1:
                    raise ProofError(f"{label} contains a hardlinked file: {path}")
                files.append(path)
            else:
                raise ProofError(f"{label} contains a non-regular entry: {path}")
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def plain_project_files(project_root: Path, project_name: str) -> tuple[Path, list[Path]]:
    project_root = require_plain_existing_ancestors(project_root, "project root")
    gpr = require_plain_file(
        project_root / f"{project_name}.gpr", "project marker", single_link=True
    )
    rep = require_plain_existing_ancestors(
        project_root / f"{project_name}.rep", "project store"
    )
    files = safe_tree_files(rep, "project store", single_link=True)
    return project_root, [gpr, *files]


def write_new(path: Path, content: bytes) -> None:
    parent = require_plain_existing_ancestors(path.parent, "output parent")
    parent.mkdir(parents=True, exist_ok=True)
    require_plain_existing_ancestors(parent, "output parent")
    path = parent / path.name
    if os.path.lexists(path):
        raise ProofError(f"refusing to overwrite existing output: {path}")
    partial = path.parent / f".{path.name}.partial-{uuid.uuid4().hex}"
    try:
        with partial.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(partial, path)
        except FileExistsError as exc:
            raise ProofError(f"refusing to overwrite existing output: {path}") from exc
        partial.unlink()
        require_plain_file(path, "published output", single_link=True)
    finally:
        partial.unlink(missing_ok=True)


def write_json_new(path: Path, payload: object) -> None:
    write_new(path, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def stamp(path: Path, root: Path) -> dict[str, object]:
    path = require_plain_file(path, "proof artifact", single_link=True)
    root = require_plain_existing_ancestors(root, "proof root")
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ProofError(f"artifact escapes proof root: {path}") from exc
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def external_stamp(path: Path) -> dict[str, object]:
    path = require_plain_file(path, "external tool", single_link=False)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def require_expected_python(path: Path) -> Path:
    path = require_plain_file(path, "Python interpreter", single_link=False)
    current = require_plain_file(
        Path(sys.executable), "current Python interpreter", single_link=False
    )
    if (
        not path.is_file()
        or path != current
        or sha256_file(path) != PYTHON_SHA256
    ):
        raise ProofError("Python interpreter identity is unsupported")
    return path


def require_trusted_tool_source(role: str, source: Path) -> Path:
    source = source.resolve()
    if role not in TRUSTED_TOOL_SHA256:
        raise ProofError(f"unknown trusted tool role: {role}")
    if (
        not source.is_file()
        or source.name != TRUSTED_TOOL_NAMES[role]
        or sha256_file(source) != TRUSTED_TOOL_SHA256[role]
    ):
        raise ProofError(f"{role} source is not the trusted canonical tool")
    return source


def require_authorized_pilot_inputs(
    *,
    target_content: bytes,
    ready_content: bytes,
    requested_sha256: str,
    requested_count: int,
) -> None:
    if (
        requested_sha256 != BOUNDARY_TARGET_SHA256
        or requested_count != BOUNDARY_TARGET_COUNT
        or sha256_bytes(target_content) != BOUNDARY_TARGET_SHA256
        or sha256_bytes(ready_content) != BOUNDARY_TARGET_READY_SHA256
    ):
        raise ProofError("target inputs are not the authorized observed40 pilot")


def require_authorized_source_campaign_ready(path: Path) -> None:
    if (
        not path.is_file()
        or sha256_file(path) != BOUNDARY_SOURCE_CAMPAIGN_READY_SHA256
    ):
        raise ProofError("source campaign READY is not the authorized observed40 pilot")


def require_expected_external_toolchain(
    headless: Path, java: Path | None = None
) -> tuple[Path, Path, Path]:
    headless = require_plain_file(headless, "analyzeHeadless", single_link=False)
    properties = require_plain_file(
        headless.parent.parent / "Ghidra" / "application.properties",
        "Ghidra application properties",
        single_link=False,
    )
    java_raw = str(lexical_absolute(java)) if java is not None else shutil.which("java")
    if not headless.is_file() or not properties.is_file() or not java_raw:
        raise ProofError("required Ghidra/Java toolchain is unavailable")
    java = require_plain_file(Path(java_raw), "host Java", single_link=False)
    if (
        sha256_file(headless) != ANALYZE_HEADLESS_SHA256
        or sha256_file(properties) != GHIDRA_APPLICATION_PROPERTIES_SHA256
        or sha256_file(java) != HOST_JAVA_SHA256
    ):
        raise ProofError("external Ghidra/Java toolchain identity is unsupported")
    return headless, properties, java


def expected_java_home_save_path(proof_root: Path) -> Path:
    return (
        proof_root.resolve()
        / "runtime-home"
        / "roaming"
        / "ghidra"
        / GHIDRA_SETTINGS_DIRECTORY
        / "java_home.save"
    )


def expected_sanitized_environment(proof_root: Path, java: Path) -> dict[str, str]:
    system_root = WINDOWS_SYSTEM_ROOT.resolve()
    system32 = system_root / "System32"
    command_processor = system32 / "cmd.exe"
    if (
        not command_processor.is_file()
        or sha256_file(command_processor) != WINDOWS_COMMAND_PROCESSOR_SHA256
    ):
        raise ProofError("Windows command processor identity is unsupported")
    runtime_root = proof_root.resolve() / "runtime-home"
    profile = runtime_root / "profile"
    roaming = runtime_root / "roaming"
    local = runtime_root / "local"
    temporary = runtime_root / "temp"
    java = java.resolve()
    java_home = java.parent.parent
    return {
        "APPDATA": str(roaming),
        "COMSPEC": str(command_processor),
        "JAVA_HOME": str(java_home),
        "LOCALAPPDATA": str(local),
        "NoDefaultCurrentDirectoryInExePath": "1",
        "PATH": os.pathsep.join((str(java.parent), str(system32), str(system_root))),
        "PATHEXT": ".COM;.EXE;.BAT;.CMD",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
        "SystemRoot": str(system_root),
        "TEMP": str(temporary),
        "TMP": str(temporary),
        "USERPROFILE": str(profile),
        "WINDIR": str(system_root),
    }


def prepare_sanitized_environment(proof_root: Path, java: Path) -> dict[str, str]:
    environment = expected_sanitized_environment(proof_root, java)
    for key in ("USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP"):
        Path(environment[key]).mkdir(parents=True, exist_ok=True)
    java_home_save = expected_java_home_save_path(proof_root)
    write_new(
        java_home_save,
        f"{Path(environment['JAVA_HOME']).resolve()}\r\n".encode("utf-8"),
    )
    return environment


def read_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ProofError(f"{label} is not a JSON object: {path}")
    return value


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def windows_batch_argv(headless: Path, arguments: list[str]) -> list[str]:
    command_processor = require_plain_file(
        WINDOWS_SYSTEM_ROOT / "System32" / "cmd.exe",
        "Windows command processor",
        single_link=False,
    )
    if sha256_file(command_processor) != WINDOWS_COMMAND_PROCESSOR_SHA256:
        raise ProofError("Windows command processor identity is unsupported")
    values = [str(require_plain_file(headless, "analyzeHeadless", single_link=False))]
    values.extend(str(value) for value in arguments)
    for value in values:
        if not value or re.search(r'[\x00\r\n"&|<>^%()!]', value):
            raise ProofError(f"headless argument is unsafe for cmd.exe: {value!r}")
    command = "call " + subprocess.list2cmdline(values)
    return [str(command_processor), "/d", "/s", "/c", command]


def run_process(
    *,
    proof_root: Path,
    run_id: str,
    argv: list[str],
    cwd: Path,
    environment: dict[str, str],
    timeout_seconds: int = 300,
) -> tuple[dict, str]:
    cwd = require_plain_existing_ancestors(cwd, "execution working directory")
    if safe_tree_files(cwd, "execution working directory", single_link=True):
        raise ProofError("execution working directory is not empty")
    run_root = proof_root / "runs" / run_id
    run_root.mkdir(parents=True, exist_ok=False)
    started = utc_now()
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            creationflags=CREATE_NO_WINDOW,
        )
    except subprocess.TimeoutExpired as exc:
        raise ProofError(f"{run_id} timed out after {timeout_seconds} seconds") from exc
    if safe_tree_files(cwd, "execution working directory", single_link=True):
        raise ProofError("execution working directory was modified")
    completed_at = utc_now()
    combined = f"{completed.stdout}\n{completed.stderr}".replace("\r\n", "\n")
    log_path = run_root / "headless.log"
    write_new(log_path, combined.encode("utf-8"))
    result = {
        "id": run_id,
        "startedAtUtc": started,
        "completedAtUtc": completed_at,
        "cwd": str(cwd),
        "argv": argv,
        "environment": environment,
        "exitCode": completed.returncode,
        "log": stamp(log_path, proof_root),
    }
    return result, combined


def finish_run(proof_root: Path, result: dict, **observations: object) -> dict:
    result = {**result, "verdict": "SURVIVED", "observations": observations}
    receipt_path = proof_root / "runs" / str(result["id"]) / "run.json"
    write_json_new(receipt_path, result)
    return {**result, "receipt": stamp(receipt_path, proof_root)}


def require_clean_log(text: str, label: str) -> None:
    if any(marker in text for marker in ERROR_MARKERS):
        raise ProofError(f"{label} log contains a script error marker")


def require_tool_sentinel(text: str, *, prefix: str, tool: Path, tool_stamp: dict) -> None:
    expected = (
        f"{prefix} path={tool.resolve()} bytes={tool_stamp['bytes']} "
        f"sha256={tool_stamp['sha256']}"
    )
    if text.count(expected) != 1:
        raise ProofError(f"log lacks exact measured tool identity: {expected}")


def run_inventory(
    *,
    proof_root: Path,
    run_id: str,
    headless: Path,
    project_root: Path,
    project_name: str,
    tool: Path,
    tool_stamp: dict,
    cwd: Path,
    environment: dict[str, str],
) -> tuple[dict, Path, Path]:
    run_root = proof_root / "runs" / run_id
    functions_path = run_root / "functions.tsv"
    program_path = run_root / "program.tsv"
    headless_arguments = [
        str(project_root.resolve()),
        project_name,
        "-process",
        PROGRAM_NAME,
        "-readOnly",
        "-noanalysis",
        "-scriptPath",
        str(tool.parent.resolve()),
        "-postScript",
        tool.name,
        str(functions_path.resolve()),
        str(program_path.resolve()),
    ]
    argv = windows_batch_argv(headless, headless_arguments)
    before_rows = project_rows_from_disk(project_root, project_name)
    result, text = run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=argv,
        cwd=cwd,
        environment=environment,
    )
    after_rows = project_rows_from_disk(project_root, project_name)
    if after_rows != before_rows:
        raise ProofError(f"{run_id} changed a project opened read-only")
    if result["exitCode"] != 0:
        raise ProofError(f"{run_id} exited {result['exitCode']}")
    require_clean_log(text, run_id)
    require_tool_sentinel(
        text, prefix="INVENTORY_TOOL_OK", tool=tool, tool_stamp=tool_stamp
    )
    expected_open = f"Opening existing project: {project_root.resolve() / project_name}"
    expected_script = f"SCRIPT: {tool.resolve()} (HeadlessAnalyzer)"
    if (
        text.count(expected_open) != 1
        or text.count(expected_script) != 1
        or "REPORT: Processing read-only project file: /BEA.exe" not in text
        or not functions_path.is_file()
        or not program_path.is_file()
    ):
        raise ProofError(f"{run_id} inventory invocation/output is not exact")
    match = re.search(r"INVENTORY_OK functions=(\d+) instructions=(\d+)", text)
    if match is None:
        raise ProofError(f"{run_id} lacks measured inventory counts")
    result = finish_run(
        proof_root,
        result,
        projectRoot=str(project_root.resolve()),
        readOnly=True,
        functionCount=int(match.group(1)),
        instructionCount=int(match.group(2)),
        functions=stamp(functions_path, proof_root),
        program=stamp(program_path, proof_root),
    )
    return result, functions_path, program_path


def reverify_retained_project_inventories(
    *,
    proof_root: Path,
    headless: Path,
    java: Path,
    inventory_tool: Path,
    backup_project: Path,
    main_project: Path,
    poison_project: Path,
) -> None:
    expected = {
        "backup-current": (
            backup_project,
            proof_root / "runs" / "main-baseline" / "functions.tsv",
            proof_root / "runs" / "main-baseline" / "program.tsv",
        ),
        "main-current": (
            main_project,
            proof_root / "runs" / "main-after" / "functions.tsv",
            proof_root / "runs" / "main-after" / "program.tsv",
        ),
        "poison-current": (
            poison_project,
            proof_root / "runs" / "poison-after" / "functions.tsv",
            proof_root / "runs" / "poison-after" / "program.tsv",
        ),
    }
    with tempfile.TemporaryDirectory(prefix="bea-ghidra-current-state-verify-") as temporary:
        verification_root = require_plain_existing_ancestors(
            Path(temporary), "current-state verification root"
        )
        (verification_root / "runs").mkdir()
        verification_cwd = verification_root / "work"
        verification_cwd.mkdir()
        environment = prepare_sanitized_environment(verification_root, java)
        tool_stamp = external_stamp(inventory_tool)
        for run_id, (project, expected_functions, expected_program) in expected.items():
            before_rows = project_rows_from_disk(project, PROGRAM_NAME.removesuffix(".exe"))
            _run, functions, program = run_inventory(
                proof_root=verification_root,
                run_id=run_id,
                headless=headless,
                project_root=project,
                project_name=PROGRAM_NAME.removesuffix(".exe"),
                tool=inventory_tool,
                tool_stamp=tool_stamp,
                cwd=verification_cwd,
                environment=environment,
            )
            after_rows = project_rows_from_disk(project, PROGRAM_NAME.removesuffix(".exe"))
            if after_rows != before_rows:
                raise ProofError(
                    f"retained {run_id} project changed during read-only verification"
                )
            if (
                functions.read_bytes() != expected_functions.read_bytes()
                or program.read_bytes() != expected_program.read_bytes()
            ):
                raise ProofError(
                    f"retained {run_id} project does not match its recorded inventory"
                )


def expected_counts(mode: str, count: int) -> dict[str, int]:
    return {
        "dry": {
            "targets": count,
            "wouldCreate": count,
            "created": 0,
            "alreadyExists": 0,
            "verified": 0,
        },
        "apply": {
            "targets": count,
            "wouldCreate": 0,
            "created": count,
            "alreadyExists": 0,
            "verified": count,
        },
        "readback": {
            "targets": count,
            "wouldCreate": 0,
            "created": 0,
            "alreadyExists": 0,
            "verified": count,
        },
    }[mode]


def validate_ready(
    *,
    ready_path: Path,
    mode: str,
    target_path: Path,
    target_stamp: dict,
    target_count: int,
    semantic_target_sha256: str,
    tool: Path,
    tool_stamp: dict,
    output_path: Path,
    proof_root: Path,
) -> dict:
    ready = read_json(ready_path, f"{mode} READY")
    output_stamp = stamp(output_path, proof_root)
    expected_program = {
        "name": PROGRAM_NAME,
        "executableMd5": PROGRAM_MD5,
        "executableSha256": PROGRAM_SHA256,
        "imageBase": IMAGE_BASE,
        "language": LANGUAGE,
        "compilerSpec": COMPILER_SPEC,
    }
    expected_tool = {
        "path": str(tool.resolve()),
        "bytes": tool_stamp["bytes"],
        "sha256": tool_stamp["sha256"],
    }
    expected_input = {
        "path": str(target_path.resolve()),
        "bytes": target_stamp["bytes"],
        "sha256": target_stamp["sha256"],
        "expectedCount": target_count,
        "semanticTargetSetSha256": semantic_target_sha256,
    }
    expected_output = {
        "path": str(output_path.resolve()),
        "bytes": output_stamp["bytes"],
        "sha256": output_stamp["sha256"],
    }
    counts = ready.get("counts")
    expected_mode_counts = expected_counts(mode, target_count)
    if not isinstance(counts, dict):
        raise ProofError(f"{mode} READY has no counts")
    before = counts.get("programInstructionsBefore")
    after = counts.get("programInstructionsAfter")
    if (
        ready.get("schemaVersion") != READY_SCHEMA
        or ready.get("mode") != mode
        or ready.get("program") != expected_program
        or ready.get("tool") != expected_tool
        or ready.get("input") != expected_input
        or ready.get("output") != expected_output
        or set(counts) != set(expected_mode_counts) | {
            "programInstructionsBefore", "programInstructionsAfter"
        }
        or any(counts.get(key) != value for key, value in expected_mode_counts.items())
        or not isinstance(before, int)
        or before <= 0
        or after != before
        or ready.get("namesAuthorized") is not False
        or ready.get("mutationCommitted") is not (mode == "apply")
        or ready.get("allTargetsVerified") is not (mode in {"apply", "readback"})
    ):
        raise ProofError(f"{mode} READY does not reproduce its invocation and invariants")
    return ready


def run_promotion(
    *,
    proof_root: Path,
    run_id: str,
    headless: Path,
    project_root: Path,
    project_name: str,
    tool: Path,
    tool_stamp: dict,
    target_path: Path,
    target_stamp: dict,
    target_count: int,
    semantic_target_sha256: str,
    mode: str,
    expected_sha256: str,
    cwd: Path,
    environment: dict[str, str],
    expected_error: str | None = None,
) -> tuple[dict, Path | None, Path | None]:
    run_root = proof_root / "runs" / run_id
    output_path = run_root / f"{mode}.tsv"
    ready_path = run_root / f"{mode}.ready.json"
    read_only = mode != "apply" or expected_error is not None and run_id != "poison-wrong-sha"
    headless_arguments = [
        str(project_root.resolve()),
        project_name,
        "-process",
        PROGRAM_NAME,
    ]
    if read_only:
        headless_arguments.append("-readOnly")
    headless_arguments.extend(
        [
            "-noanalysis",
            "-scriptPath",
            str(tool.parent.resolve()),
            "-postScript",
            tool.name,
            str(target_path.resolve()),
            expected_sha256,
            str(target_count),
            str(output_path.resolve()),
            str(ready_path.resolve()),
            mode,
        ]
    )
    argv = windows_batch_argv(headless, headless_arguments)
    before_project_rows = (
        project_rows_from_disk(project_root, project_name)
        if read_only
        else None
    )
    if before_project_rows is None:
        plain_project_files(project_root, project_name)
    result, text = run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=argv,
        cwd=cwd,
        environment=environment,
    )
    if before_project_rows is None:
        plain_project_files(project_root, project_name)
    elif project_rows_from_disk(project_root, project_name) != before_project_rows:
        raise ProofError(f"{run_id} changed a project opened read-only")
    require_tool_sentinel(
        text, prefix="FUNCTION_PROMOTION_TOOL_OK", tool=tool, tool_stamp=tool_stamp
    )
    expected_open = f"Opening existing project: {project_root.resolve() / project_name}"
    expected_script = f"SCRIPT: {tool.resolve()} (HeadlessAnalyzer)"
    if text.count(expected_open) != 1 or text.count(expected_script) != 1:
        raise ProofError(f"{run_id} opened another project/tool")
    if expected_error is not None:
        # AnalyzeHeadless reports a script-level, deliberately handled preflight
        # rejection with exit code zero. A crash or launcher failure can still
        # contain the registered marker, so the marker alone is not a survived
        # negative control.
        if result["exitCode"] != 0:
            raise ProofError(
                f"{run_id} negative control exited {result['exitCode']} instead of cleanly rejecting"
            )
        if run_id == "poison-wrong-sha" and (
            "REPORT: Processing project file: /BEA.exe" not in text
            or "REPORT: Processing read-only project file: /BEA.exe" in text
        ):
            raise ProofError("poisoned-SHA control was not one writable invocation")
        if (
            text.count("REPORT SCRIPT ERROR") != 1
            or text.count(expected_error) != 1
            or "FUNCTION_PROMOTION_PREFLIGHT_OK" in text
            or "FUNCTION_PROMOTION_OK" in text
            or "FUNCTION_PROMOTION_RECEIPT_LOST" in text
            or output_path.exists()
            or ready_path.exists()
        ):
            raise ProofError(f"{run_id} did not fail at the registered preflight boundary")
        result = finish_run(
            proof_root,
            result,
            projectRoot=str(project_root.resolve()),
            readOnly=read_only,
            rejectedBeforePromotionPreflight=True,
            expectedError=expected_error,
            outputTsvAbsent=True,
            outputReadyAbsent=True,
            saveReported="Save succeeded for processed file: /BEA.exe" in text,
        )
        return result, None, None

    if result["exitCode"] != 0:
        raise ProofError(f"{run_id} exited {result['exitCode']}")
    require_clean_log(text, run_id)
    read_only_marker = "REPORT: Processing read-only project file: /BEA.exe"
    writable_marker = "REPORT: Processing project file: /BEA.exe"
    if mode == "apply":
        if writable_marker not in text or read_only_marker in text:
            raise ProofError(f"{run_id} was not one writable apply")
        if text.count("Save succeeded for processed file: /BEA.exe") != 1:
            raise ProofError(f"{run_id} lacks one project-save sentinel")
    elif read_only_marker not in text:
        raise ProofError(f"{run_id} was not read-only")
    ready = validate_ready(
        ready_path=ready_path,
        mode=mode,
        target_path=target_path,
        target_stamp=target_stamp,
        target_count=target_count,
        semantic_target_sha256=semantic_target_sha256,
        tool=tool,
        tool_stamp=tool_stamp,
        output_path=output_path,
        proof_root=proof_root,
    )
    counts = expected_counts(mode, target_count)
    sentinel = (
        f"FUNCTION_PROMOTION_OK mode={mode} targets={target_count} "
        f"would_create={counts['wouldCreate']} created={counts['created']} "
        f"already_exists={counts['alreadyExists']} verified={counts['verified']} "
        f"mutation_committed={'true' if mode == 'apply' else 'false'}"
    )
    if text.count(sentinel) != 1:
        raise ProofError(f"{run_id} lacks its exact success sentinel")
    result = finish_run(
        proof_root,
        result,
        projectRoot=str(project_root.resolve()),
        readOnly=read_only,
        mode=mode,
        tsv=stamp(output_path, proof_root),
        ready=stamp(ready_path, proof_root),
        instructionCount=ready["counts"]["programInstructionsAfter"],
        saveReported="Save succeeded for processed file: /BEA.exe" in text,
    )
    return result, output_path, ready_path


def run_auxiliary(
    *,
    proof_root: Path,
    run_id: str,
    argv: list[str],
    cwd: Path,
    environment: dict[str, str],
) -> dict:
    result, text = run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=argv,
        cwd=cwd,
        environment=environment,
    )
    if result["exitCode"] != 0:
        raise ProofError(f"{run_id} exited {result['exitCode']}: {text[-500:]}")
    return finish_run(proof_root, result)


def manifest_rows(path: Path, *, expected_root: Path) -> list[tuple[str, int, str]]:
    document = read_json(path, "project manifest")
    if (
        set(document) != {"createdAtUtc", "manifest", "schemaVersion"}
        or document.get("schemaVersion") != BACKUP_SCHEMA
    ):
        raise ProofError(f"unsupported project manifest schema: {path}")
    _iso_timestamp(document.get("createdAtUtc"), "project inspection manifest")
    manifest = document.get("manifest")
    if not isinstance(manifest, dict) or set(manifest) != {
        "fileCount", "files", "projectName", "root", "structurallyComplete",
        "totalBytes",
    }:
        raise ProofError(f"project manifest envelope is malformed: {path}")
    expected_root = require_plain_existing_ancestors(
        expected_root, "project inspection root"
    )
    if manifest.get("root") != str(expected_root):
        raise ProofError(f"project manifest names the wrong project root: {path}")
    return _copy_manifest_section(
        {key: value for key, value in manifest.items() if key != "root"},
        "inspection",
    )


def _copy_manifest_section(value: object, label: str) -> list[tuple[str, int, str]]:
    if not isinstance(value, dict) or set(value) != {
        "fileCount", "files", "projectName", "structurallyComplete", "totalBytes"
    }:
        raise ProofError(f"project copy manifest {label} section is malformed")
    files = value.get("files")
    if (
        value.get("projectName") != "BEA"
        or value.get("structurallyComplete") is not True
        or not isinstance(files, list)
        or not files
    ):
        raise ProofError(f"project copy manifest {label} is not a complete BEA project")
    rows: list[tuple[str, int, str]] = []
    for row in files:
        if not isinstance(row, dict) or set(row) != {"relative_path", "size", "sha256"}:
            raise ProofError(f"project copy manifest {label} row is malformed")
        relative = str(row["relative_path"])
        size = row["size"]
        digest = str(row["sha256"])
        candidate = Path(relative)
        if (
            candidate.is_absolute()
            or ".." in candidate.parts
            or not isinstance(size, int)
            or size < 0
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise ProofError(f"project copy manifest {label} row is unsafe")
        rows.append((candidate.as_posix(), size, digest))
    if (
        rows != sorted(rows)
        or len(rows) != len({row[0] for row in rows})
        or value.get("fileCount") != len(rows)
        or value.get("totalBytes") != sum(row[1] for row in rows)
    ):
        raise ProofError(f"project copy manifest {label} accounting is inconsistent")
    return rows


def validate_copy_manifest(
    path: Path,
) -> tuple[list[tuple[str, int, str]], list[tuple[str, int, str]]]:
    document = read_json(path, "project copy manifest")
    if set(document) != {
        "copyComparison", "createdAtUtc", "destination", "readonlyOpen",
        "schemaVersion", "source", "sourceStable",
    } or document.get("schemaVersion") != BACKUP_SCHEMA:
        raise ProofError(f"unsupported project copy manifest schema/fields: {path}")
    _iso_timestamp(document.get("createdAtUtc"), "project copy manifest")
    comparison = document.get("copyComparison")
    expected_comparison = {
        "extra": [],
        "extraCount": 0,
        "hashDiffCount": 0,
        "hashDifferences": [],
        "matches": True,
        "missing": [],
        "missingCount": 0,
        "sizeDiffCount": 0,
        "sizeDifferences": [],
    }
    if (
        document.get("sourceStable") is not True
        or document.get("readonlyOpen") is not None
        or comparison != expected_comparison
    ):
        raise ProofError("project copy manifest does not prove a stable exact copy")
    source = _copy_manifest_section(document.get("source"), "source")
    destination = _copy_manifest_section(document.get("destination"), "destination")
    if source != destination:
        raise ProofError("project copy manifest source/destination differ")
    return source, destination


def copy_rows(path: Path) -> list[tuple[str, int, str]]:
    _source, destination = validate_copy_manifest(path)
    return destination


def canonical_rows_sha(rows: list[tuple[str, int, str]]) -> str:
    content = "".join(f"{sha}\t{size}\t{path}\n" for path, size, sha in sorted(rows))
    return sha256_bytes(content.encode("utf-8"))


def distribution_rows(root: Path) -> list[tuple[str, int, str]]:
    root = require_plain_existing_ancestors(root, "toolchain distribution")
    rows: list[tuple[str, int, str]] = []
    for path in safe_tree_files(
        root, "toolchain distribution", single_link=False
    ):
        rows.append(
            (
                path.relative_to(root).as_posix(),
                path.stat().st_size,
                sha256_file(path),
            )
        )
    return rows


def require_expected_distribution(
    root: Path,
    *,
    label: str,
    expected_count: int,
    expected_total_bytes: int,
    expected_sha256: str,
) -> list[tuple[str, int, str]]:
    rows = distribution_rows(root)
    if (
        len(rows) != expected_count
        or sum(row[1] for row in rows) != expected_total_bytes
        or canonical_rows_sha(rows) != expected_sha256
    ):
        raise ProofError(f"{label} distribution fingerprint is unsupported")
    return rows


def write_distribution_manifest(
    path: Path, rows: list[tuple[str, int, str]]
) -> None:
    content = "".join(
        f"{sha}\t{size}\t{relative}\n" for relative, size, sha in sorted(rows)
    ).encode("utf-8")
    write_new(path, content)


def read_distribution_manifest(path: Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ProofError(f"toolchain manifest is unreadable: {path}") from exc
    for line in lines:
        parts = line.split("\t")
        if len(parts) != 3:
            raise ProofError(f"toolchain manifest row is malformed: {path}")
        digest, size_text, relative = parts
        candidate = Path(relative)
        try:
            size = int(size_text)
        except ValueError as exc:
            raise ProofError(f"toolchain manifest size is malformed: {path}") from exc
        if (
            re.fullmatch(r"[0-9a-f]{64}", digest) is None
            or size < 0
            or not relative
            or candidate.is_absolute()
            or ".." in candidate.parts
            or candidate.as_posix() != relative
        ):
            raise ProofError(f"toolchain manifest row is unsafe: {path}")
        rows.append((relative, size, digest))
    if rows != sorted(rows) or len(rows) != len({row[0] for row in rows}):
        raise ProofError(f"toolchain manifest is unsorted or repeats a path: {path}")
    return rows


def semantic_target_sha(addresses: list[str]) -> str:
    content = "".join(f"{address}\n" for address in sorted(addresses))
    return sha256_bytes(content.encode("ascii"))


def _file_stamp_matches(path: Path, expected: object, label: str) -> dict:
    if not isinstance(expected, dict) or not path.is_file():
        raise ProofError(f"{label} is missing from disk/receipt")
    actual = {
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if (
        actual["bytes"] != expected.get("bytes")
        or actual["sha256"] != expected.get("sha256")
    ):
        raise ProofError(f"{label} has changed")
    return actual


def _resolve_boundary_source(value: object, repo_root: Path) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ProofError("boundary READY has no source campaign path")
    path = Path(value)
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()


def _validate_campaign_reducer_copy(
    source_root: Path,
    campaign_ready: dict,
    *,
    require_exact_tree: bool = False,
) -> None:
    reducer = campaign_ready.get("reducer")
    if not isinstance(reducer, dict) or set(reducer) != {
        "schema", "id", "entry", "files"
    }:
        raise ProofError("boundary source campaign lacks an exact reducer manifest")
    files = reducer.get("files")
    if not isinstance(files, list) or not files:
        raise ProofError("boundary source campaign reducer is empty")
    if (
        reducer.get("schema") != CAMPAIGN_REDUCER_SCHEMA
        or reducer.get("entry") != CAMPAIGN_REDUCER_ENTRY
        or reducer.get("id") != CAMPAIGN_REDUCER_ID
    ):
        raise ProofError("boundary source campaign reducer identity is unsupported")
    canonical_rows = []
    seen: set[str] = set()
    for row in files:
        if not isinstance(row, dict) or set(row) != {"role", "path", "bytes", "sha256"}:
            raise ProofError("boundary source campaign reducer stamp is malformed")
        relative = str(row.get("path", ""))
        if (
            not relative.startswith("_reducer/")
            or relative in seen
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            raise ProofError("boundary source campaign reducer path is unsafe/duplicate")
        seen.add(relative)
        path = source_root / Path(relative)
        if path.is_symlink():
            raise ProofError("boundary source campaign reducer contains a symlink")
        _file_stamp_matches(path, row, f"boundary reducer {relative}")
        canonical_rows.append(row)
    canonical = "".join(
        f"{row['role']}\t{row['sha256']}\t{row['bytes']}\t{row['path']}\n"
        for row in sorted(canonical_rows, key=lambda item: str(item["path"]))
    ).encode("utf-8")
    if sha256_bytes(canonical) != reducer.get("id"):
        raise ProofError("boundary source campaign reducer digest is inconsistent")
    if require_exact_tree:
        reducer_root = source_root / "_reducer"
        actual = {
            path.relative_to(source_root).as_posix()
            for path in reducer_root.rglob("*")
            if path.is_file()
        }
        if any(path.is_symlink() for path in reducer_root.rglob("*")) or actual != seen:
            raise ProofError("boundary source campaign reducer tree is not exact")


def _campaign_snapshot_relative(campaign_ready: dict, repo_root: Path) -> Path:
    source = campaign_ready.get("sourceSnapshot")
    if not isinstance(source, dict):
        raise ProofError("boundary source campaign has no source snapshot")
    raw = source.get("path")
    if not isinstance(raw, str) or not raw.strip():
        raise ProofError("boundary source campaign source snapshot path is missing")
    relative = Path(raw)
    if relative.is_absolute():
        try:
            relative = relative.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ProofError(
                "boundary source campaign source snapshot is outside its repository"
            ) from exc
    if (
        ".." in relative.parts
        or len(relative.parts) < 3
        or tuple(part.casefold() for part in relative.parts[:2])
        != ("local-lab", "re-ledger")
    ):
        raise ProofError("boundary source campaign source snapshot path is unsafe")
    return relative


def copy_snapshot_evidence(source: Path, destination: Path) -> dict:
    ready_path = source / "ledger.ready.json"
    ready = read_json(ready_path, "boundary source coverage READY")
    if set(ready) != {"schema", "generatedAtUtc", "files"} or ready.get(
        "schema"
    ) != COVERAGE_READY_SCHEMA:
        raise ProofError("boundary source coverage READY is unsupported")
    files = ready.get("files")
    if not isinstance(files, dict) or not files:
        raise ProofError("boundary source coverage READY has no files")
    ready_stat = ready_path.stat()
    ready_destination = destination / "ledger.ready.json"
    write_new(ready_destination, ready_path.read_bytes())
    os.utime(
        ready_destination,
        ns=(ready_stat.st_atime_ns, ready_stat.st_mtime_ns),
    )
    for name, spec in files.items():
        relative = Path(str(name))
        if relative.name != str(name) or relative.is_absolute() or ".." in relative.parts:
            raise ProofError("boundary source coverage READY has an unsafe path")
        path = source / relative
        if path.is_symlink():
            raise ProofError("boundary source coverage contains a symlink")
        _file_stamp_matches(path, spec, f"boundary source coverage {name}")
        if not isinstance(spec, dict) or spec.get("path") != name:
            raise ProofError("boundary source coverage READY has a nonportable path")
        source_stat = path.stat()
        copied = destination / relative
        write_new(copied, path.read_bytes())
        os.utime(copied, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
    return ready


def _run_frozen_campaign_verify(
    *,
    source_root: Path,
    authority_root: Path,
    python: Path,
    environment: dict[str, str],
    campaign_ready: dict,
    snapshot_relative: Path,
) -> dict[str, object]:
    python = require_expected_python(python)
    reducer = campaign_ready["reducer"]
    _validate_campaign_reducer_copy(
        source_root, campaign_ready, require_exact_tree=True
    )
    bootstrap = (
        "import runpy,sys;from pathlib import Path;"
        "p=Path(sys.argv[1]).resolve();sys.path.insert(0,str(p.parent));"
        "sys.argv=[str(p),*sys.argv[2:]];runpy.run_path(str(p),run_name='__main__')"
    )
    replay_environment = dict(environment)
    replay_environment["BEA_REPO_ROOT"] = str(authority_root.resolve())
    with tempfile.TemporaryDirectory(prefix="bea-proof-campaign-replay-") as temporary:
        replay_campaign = Path(temporary) / "campaign"
        shutil.copytree(source_root, replay_campaign)
        replay_ready_path = replay_campaign / "campaign.ready.json"
        replay_ready = read_json(replay_ready_path, "campaign replay READY")
        replay_ready["sourceSnapshot"]["path"] = snapshot_relative.as_posix()
        replay_ready_path.write_text(
            json.dumps(replay_ready, indent=2) + "\n", encoding="utf-8"
        )
        entry = (replay_campaign / CAMPAIGN_REDUCER_ENTRY).resolve()
        argv = [
            str(python.resolve()),
            "-I",
            "-B",
            "-c",
            bootstrap,
            str(entry),
            "verify",
            "--campaign",
            str(replay_campaign.resolve()),
        ]
        try:
            completed = subprocess.run(
                argv,
                cwd=authority_root,
                env=replay_environment,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
                creationflags=CREATE_NO_WINDOW,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ProofError("boundary source campaign frozen replay could not run") from exc
        expected_stdout = (
            f"CAMPAIGN_VERIFIED {campaign_ready.get('counts')} "
            f"{replay_campaign.resolve()}"
        )
    stdout = completed.stdout.strip()
    if (
        completed.returncode != 0
        or completed.stderr.strip()
        or stdout != expected_stdout
    ):
        raise ProofError(
            "boundary source campaign frozen replay failed: "
            f"exit={completed.returncode} stdout={stdout[-300:]!r} "
            f"stderr={completed.stderr.strip()[-300:]!r}"
        )
    return {
        "schema": CAMPAIGN_REPLAY_SCHEMA,
        "verdict": "SURVIVED",
        "reducerId": reducer["id"],
        "campaignReadySha256": sha256_file(source_root / "campaign.ready.json"),
        "counts": campaign_ready.get("counts"),
    }


def validate_boundary_target_source(
    *,
    ready_path: Path,
    target_path: Path,
    repo_root: Path,
    source_override: Path | None = None,
    require_exact_reducer_tree: bool = False,
    snapshot_origin_root: Path | None = None,
) -> dict[str, object]:
    ready = read_json(ready_path, "boundary target READY")
    expected_ready_keys = {
        "schema", "generatedAtUtc", "sourceCampaign", "selection", "count",
        "targets", "output",
    }
    if ready.get("schema") != BOUNDARY_READY_SCHEMA or set(ready) != expected_ready_keys:
        raise ProofError("boundary target READY schema/fields are unsupported")
    output = ready.get("output")
    _file_stamp_matches(target_path, output, "boundary target list")
    if not isinstance(output, dict) or output.get("path") != "boundary-targets.txt":
        raise ProofError("boundary target READY names another output")
    addresses = target_path.read_text(encoding="ascii").splitlines()
    targets = ready.get("targets")
    if (
        not isinstance(targets, list)
        or len(addresses) != ready.get("count")
        or len(addresses) != len(targets)
        or len(addresses) != len(set(addresses))
        or any(re.fullmatch(r"0x[0-9a-f]{8}", value) is None for value in addresses)
        or [row.get("address") for row in targets if isinstance(row, dict)] != addresses
    ):
        raise ProofError("boundary target READY does not reproduce its canonical list")
    selection = ready.get("selection")
    if not isinstance(selection, dict) or set(selection) != {
        "questionType", "priority", "requiresElevation", "state", "limit",
        "namesAuthorized",
    }:
        raise ProofError("boundary target selection is malformed")
    limit = selection.get("limit")
    if (
        not isinstance(limit, int)
        or limit < 0
        or selection
        != {
            "questionType": "NATIVE_BOUNDARY",
            "priority": 0,
            "requiresElevation": False,
            "state": "OPEN",
            "limit": limit,
            "namesAuthorized": False,
        }
    ):
        raise ProofError("boundary target selection policy is not exact")

    source = ready.get("sourceCampaign")
    if not isinstance(source, dict) or set(source) != {
        "path", "ready", "coverageSetSha256", "specimen"
    }:
        raise ProofError("boundary target source campaign is malformed")
    source_root = (
        source_override.resolve()
        if source_override is not None
        else _resolve_boundary_source(source.get("path"), repo_root)
    )
    source_ready_path = source_root / "campaign.ready.json"
    _file_stamp_matches(
        source_ready_path, source.get("ready"), "boundary source campaign READY"
    )
    campaign_ready = read_json(source_ready_path, "boundary source campaign READY")
    if campaign_ready.get("schema") != CAMPAIGN_SCHEMA:
        raise ProofError("boundary source campaign is not the frozen v5 contract")
    if (
        campaign_ready.get("generation") != 0
        or campaign_ready.get("parentCampaign") is not None
        or campaign_ready.get("advance") is not None
    ):
        raise ProofError("boundary source campaign must be a self-contained generation zero")
    outputs = campaign_ready.get("outputs")
    if not isinstance(outputs, dict) or set(outputs) != set(CAMPAIGN_OUTPUTS):
        raise ProofError("boundary source campaign output set is incomplete")
    for name in CAMPAIGN_OUTPUTS:
        _file_stamp_matches(
            source_root / name, outputs[name], f"boundary source campaign {name}"
        )
    _validate_campaign_reducer_copy(
        source_root,
        campaign_ready,
        require_exact_tree=require_exact_reducer_tree,
    )
    snapshot = campaign_ready.get("sourceSnapshot")
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("specimen"), dict):
        raise ProofError("boundary source campaign has no specimen identity")
    specimen = snapshot["specimen"]
    if (
        specimen.get("sha256") != PROGRAM_SHA256
        or source.get("coverageSetSha256") != snapshot.get("coverageSetSha256")
        or source.get("specimen") != specimen
    ):
        raise ProofError("boundary source campaign specimen/coverage identity disagrees")

    questions = read_tsv(source_root / "campaign-questions.tsv")
    eligible = [
        row
        for row in questions
        if row.get("state") == "OPEN"
        and row.get("questionType") == "NATIVE_BOUNDARY"
        and row.get("priority") == "0"
        and row.get("requiresElevation", "").casefold() not in {"true", "1", "yes"}
    ]
    eligible.sort(key=lambda row: (-float(row.get("score") or 0), row["questionId"]))
    if limit:
        eligible = eligible[:limit]
    expected_targets = []
    for row in eligible:
        match = re.fullmatch(
            r"CODE_CANDIDATE:([0-9a-fA-F]{64}):VA=(0[xX][0-9a-fA-F]+)",
            row.get("entityKey", ""),
        )
        if match is None or match.group(1).lower() != PROGRAM_SHA256:
            raise ProofError("boundary source question is not specimen-bound CODE_CANDIDATE")
        expected_targets.append(
            {
                "questionId": row["questionId"],
                "entityKey": row["entityKey"],
                "address": f"0x{int(match.group(2), 16):08x}",
                "source": row["source"],
            }
        )
    if targets != expected_targets or addresses != [row["address"] for row in expected_targets]:
        raise ProofError("boundary targets do not reproduce from the source campaign")
    return {
        "ready": ready,
        "addresses": addresses,
        "sourceRoot": source_root,
        "campaignReady": campaign_ready,
        "snapshotRelative": _campaign_snapshot_relative(
            campaign_ready, snapshot_origin_root or repo_root
        ),
    }


def copy_campaign_evidence(
    source_root: Path, destination: Path, campaign_ready: dict
) -> None:
    relative_paths = [Path("campaign.ready.json"), *(Path(name) for name in CAMPAIGN_OUTPUTS)]
    reducer = campaign_ready.get("reducer", {})
    relative_paths.extend(Path(str(row["path"])) for row in reducer.get("files", []))
    for relative in relative_paths:
        if relative.is_absolute() or ".." in relative.parts:
            raise ProofError("boundary source campaign copy path escapes its root")
        source = (source_root / relative).resolve()
        try:
            source.relative_to(source_root.resolve())
        except ValueError as exc:
            raise ProofError("boundary source campaign copy path escapes its root") from exc
        if not source.is_file() or source.is_symlink():
            raise ProofError(f"boundary source campaign file is missing/symlinked: {source}")
        write_new(destination / relative, source.read_bytes())


def inventory_map(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    addresses = [row.get("address", "").lower() for row in rows]
    if any(not address for address in addresses) or len(addresses) != len(set(addresses)):
        raise ProofError(f"inventory has missing or duplicate addresses: {path}")
    return {address: row for address, row in zip(addresses, rows)}


def program_map(path: Path) -> dict[str, str]:
    rows = read_tsv(path)
    if any(set(row) != {"metric", "value"} for row in rows):
        raise ProofError(f"program inventory has malformed columns: {path}")
    metrics = [row["metric"] for row in rows]
    if any(not metric for metric in metrics) or len(metrics) != len(set(metrics)):
        raise ProofError(f"program inventory has missing or duplicate metrics: {path}")
    return {row["metric"]: row["value"] for row in rows}


def snapshot_tool(source: Path, destination: Path) -> dict[str, object]:
    content = source.read_bytes()
    write_new(destination, content)
    return {
        "sourcePath": str(source.resolve()),
        "sourceBytes": len(content),
        "sourceSha256": sha256_bytes(content),
    }


def artifact_set(proof_root: Path) -> dict[str, object]:
    items: list[dict[str, object]] = []
    proof_root = require_plain_existing_ancestors(proof_root, "proof root")
    for path in safe_tree_files(proof_root, "proof tree", single_link=True):
        if path.name == "proof.ready.json":
            continue
        relative = path.relative_to(proof_root)
        if relative.parts[0] in {"main-project", "poison-project"}:
            continue
        items.append(stamp(path, proof_root))
    canonical = "".join(
        f"{item['sha256']}\t{item['bytes']}\t{item['path']}\n" for item in items
    ).encode("utf-8")
    return {
        "canonicalization": "sha256<TAB>bytes<TAB>relative-posix-path<LF>, sorted by path",
        "count": len(items),
        "totalBytes": sum(int(item["bytes"]) for item in items),
        "sha256": sha256_bytes(canonical),
        "items": items,
    }


def project_rows_from_disk(project_root: Path, project_name: str) -> list[tuple[str, int, str]]:
    project_root, paths = plain_project_files(project_root, project_name)
    rows: list[tuple[str, int, str]] = []
    for path in paths:
        rows.append(
            (
                path.relative_to(project_root).as_posix(),
                path.stat().st_size,
                sha256_file(path),
            )
        )
    return rows


def require_expected_base_project(project_root: Path) -> list[tuple[str, int, str]]:
    rows = project_rows_from_disk(project_root, "BEA")
    if canonical_rows_sha(rows) != BASE_PROJECT_FILE_SET_SHA256:
        raise ProofError("scratch proof backup root is not the preregistered base project")
    return rows


def tree_rows_from_disk(root: Path) -> list[tuple[str, int, str]]:
    root = require_plain_existing_ancestors(root, "evidence tree")
    rows = []
    for path in safe_tree_files(root, "evidence tree", single_link=True):
        rows.append(
            (
                path.relative_to(root).as_posix(),
                path.stat().st_size,
                sha256_file(path),
            )
        )
    return rows


def _exact_artifact_stamp(path: Path, proof_root: Path) -> dict[str, object]:
    return stamp(path, proof_root)


def _verify_external_stamp(spec: object, label: str) -> Path:
    if not isinstance(spec, dict) or set(spec) != {"path", "bytes", "sha256"}:
        raise ProofError(f"scratch proof {label} stamp is malformed")
    path = require_plain_file(
        Path(str(spec["path"])), f"scratch proof {label}", single_link=False
    )
    if path.stat().st_size != spec["bytes"] or sha256_file(path) != spec["sha256"]:
        raise ProofError(f"scratch proof {label} bytes have changed")
    return path


def _verify_python_stamp(spec: object) -> Path:
    path = _verify_external_stamp(spec, "Python interpreter")
    if (
        path != require_plain_file(
            Path(sys.executable), "current Python interpreter", single_link=False
        )
        or sha256_file(path) != PYTHON_SHA256
    ):
        raise ProofError("scratch proof Python interpreter is not the trusted executable")
    return require_expected_python(path)


def distribution_receipt(
    *,
    root: Path,
    manifest_path: Path,
    proof_root: Path,
    rows: list[tuple[str, int, str]],
) -> dict[str, object]:
    return {
        "root": str(root.resolve()),
        "manifest": stamp(manifest_path, proof_root),
        "fileCount": len(rows),
        "totalBytes": sum(row[1] for row in rows),
        "fileSetSha256": canonical_rows_sha(rows),
    }


def _verify_distribution_receipt(
    *,
    proof_root: Path,
    spec: object,
    expected_root: Path,
    expected_manifest_relative: str,
    label: str,
    expected_count: int,
    expected_total_bytes: int,
    expected_sha256: str,
) -> list[tuple[str, int, str]]:
    if not isinstance(spec, dict) or set(spec) != {
        "root", "manifest", "fileCount", "totalBytes", "fileSetSha256"
    }:
        raise ProofError(f"scratch proof {label} distribution receipt is malformed")
    expected_root = expected_root.resolve()
    if spec.get("root") != str(expected_root):
        raise ProofError(f"scratch proof {label} distribution root is unsupported")
    manifest_path = proof_root / expected_manifest_relative
    if stamp(manifest_path, proof_root) != spec.get("manifest"):
        raise ProofError(f"scratch proof {label} distribution manifest has changed")
    recorded_rows = read_distribution_manifest(manifest_path)
    if (
        len(recorded_rows) != expected_count
        or sum(row[1] for row in recorded_rows) != expected_total_bytes
        or canonical_rows_sha(recorded_rows) != expected_sha256
        or spec.get("fileCount") != expected_count
        or spec.get("totalBytes") != expected_total_bytes
        or spec.get("fileSetSha256") != expected_sha256
    ):
        raise ProofError(f"scratch proof {label} distribution manifest is unsupported")
    actual_rows = require_expected_distribution(
        expected_root,
        label=label,
        expected_count=expected_count,
        expected_total_bytes=expected_total_bytes,
        expected_sha256=expected_sha256,
    )
    if actual_rows != recorded_rows:
        raise ProofError(f"scratch proof {label} distribution no longer matches its manifest")
    return recorded_rows


def _verify_tool_snapshots(proof_root: Path, receipt: dict) -> dict[str, Path]:
    toolchain = receipt.get("toolchain")
    if not isinstance(toolchain, dict) or set(toolchain) != {
        "snapshots", "analyzeHeadless", "ghidraApplicationProperties",
        "hostJavaObserved", "ghidraDistribution", "jdkDistribution",
        "pythonDistribution", "javaHomeSave", "windowsCommandProcessor",
    }:
        raise ProofError("scratch proof toolchain is malformed")
    snapshots = toolchain.get("snapshots")
    expected_roles = {"runner", "promotion", "inventory", "backup", "diff"}
    if not isinstance(snapshots, dict) or set(snapshots) != expected_roles:
        raise ProofError("scratch proof tool snapshot set is incomplete")
    paths: dict[str, Path] = {}
    for role in sorted(expected_roles):
        item = snapshots[role]
        if not isinstance(item, dict) or set(item) != {
            "sourcePath", "sourceBytes", "sourceSha256", "snapshot"
        }:
            raise ProofError(f"scratch proof {role} snapshot metadata is malformed")
        snapshot_spec = item["snapshot"]
        if not isinstance(snapshot_spec, dict):
            raise ProofError(f"scratch proof {role} snapshot stamp is malformed")
        path = proof_root / str(snapshot_spec.get("path", ""))
        if stamp(path, proof_root) != snapshot_spec:
            raise ProofError(f"scratch proof {role} snapshot has changed")
        if (
            path.stat().st_size != item["sourceBytes"]
            or sha256_file(path) != item["sourceSha256"]
        ):
            raise ProofError(f"scratch proof {role} source/snapshot identity disagrees")
        if role in TRUSTED_TOOL_SHA256:
            require_trusted_tool_source(role, path)
        if role == "runner" and path.name != Path(__file__).name:
            raise ProofError("scratch proof runner snapshot has an unsupported name")
        paths[role] = path
    if sha256_file(Path(__file__).resolve()) != snapshots["runner"]["sourceSha256"]:
        raise ProofError(
            "scratch proof runner differs from this verifier; use its frozen runner or migrate"
        )
    paths["headless"] = _verify_external_stamp(
        toolchain["analyzeHeadless"], "analyzeHeadless"
    )
    paths["ghidra-properties"] = _verify_external_stamp(
        toolchain["ghidraApplicationProperties"], "Ghidra application properties"
    )
    paths["java"] = _verify_external_stamp(
        toolchain["hostJavaObserved"], "host Java"
    )
    paths["cmd"] = _verify_external_stamp(
        toolchain["windowsCommandProcessor"], "Windows command processor"
    )
    expected_headless, expected_properties, expected_java = (
        require_expected_external_toolchain(paths["headless"], paths["java"])
    )
    if (
        paths["headless"] != expected_headless
        or paths["ghidra-properties"] != expected_properties
        or paths["java"] != expected_java
        or paths["cmd"] != (WINDOWS_SYSTEM_ROOT / "System32" / "cmd.exe").resolve()
        or sha256_file(paths["cmd"]) != WINDOWS_COMMAND_PROCESSOR_SHA256
    ):
        raise ProofError("scratch proof external Ghidra/Java identity is unsupported")
    _verify_distribution_receipt(
        proof_root=proof_root,
        spec=toolchain["ghidraDistribution"],
        expected_root=expected_headless.parent.parent,
        expected_manifest_relative="inputs/toolchain/ghidra-files.tsv",
        label="Ghidra",
        expected_count=GHIDRA_DISTRIBUTION_FILE_COUNT,
        expected_total_bytes=GHIDRA_DISTRIBUTION_TOTAL_BYTES,
        expected_sha256=GHIDRA_DISTRIBUTION_FILE_SET_SHA256,
    )
    _verify_distribution_receipt(
        proof_root=proof_root,
        spec=toolchain["jdkDistribution"],
        expected_root=expected_java.parent.parent,
        expected_manifest_relative="inputs/toolchain/jdk-files.tsv",
        label="JDK",
        expected_count=JDK_DISTRIBUTION_FILE_COUNT,
        expected_total_bytes=JDK_DISTRIBUTION_TOTAL_BYTES,
        expected_sha256=JDK_DISTRIBUTION_FILE_SET_SHA256,
    )
    _verify_distribution_receipt(
        proof_root=proof_root,
        spec=toolchain["pythonDistribution"],
        expected_root=Path(sys.base_prefix),
        expected_manifest_relative="inputs/toolchain/python-files.tsv",
        label="Python",
        expected_count=PYTHON_DISTRIBUTION_FILE_COUNT,
        expected_total_bytes=PYTHON_DISTRIBUTION_TOTAL_BYTES,
        expected_sha256=PYTHON_DISTRIBUTION_FILE_SET_SHA256,
    )
    java_home_save = expected_java_home_save_path(proof_root)
    if (
        stamp(java_home_save, proof_root) != toolchain["javaHomeSave"]
        or java_home_save.read_bytes()
        != f"{expected_java.parent.parent.resolve()}\r\n".encode("utf-8")
    ):
        raise ProofError("scratch proof Java selection file is not exact")
    return paths


def _iso_timestamp(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ProofError(f"scratch proof {label} timestamp is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProofError(f"scratch proof {label} timestamp is malformed") from exc
    if parsed.tzinfo is None:
        raise ProofError(f"scratch proof {label} timestamp has no timezone")
    return parsed


def _verify_run_receipts(
    proof_root: Path,
    receipt: dict,
    tools: dict[str, Path],
    target_path: Path,
    addresses: list[str],
) -> dict[str, dict]:
    execution = receipt.get("execution")
    if not isinstance(execution, dict) or set(execution) != {
        "repoRoot", "backupRoot", "backupBaseFileSetSha256", "projectName",
        "python", "environment", "workingDirectory",
    }:
        raise ProofError("scratch proof execution environment is malformed")
    if execution.get("projectName") != PROGRAM_NAME.removesuffix(".exe"):
        raise ProofError("scratch proof project name is unsupported")
    repo_root = require_plain_existing_ancestors(
        Path(str(execution.get("repoRoot", ""))), "execution repository root"
    )
    backup_root = require_plain_existing_ancestors(
        Path(str(execution.get("backupRoot", ""))), "backup input"
    )
    execution_cwd = require_plain_existing_ancestors(
        Path(str(execution.get("workingDirectory", ""))),
        "execution working directory",
    )
    python = _verify_python_stamp(execution.get("python"))
    if (
        not repo_root.is_dir()
        or not backup_root.is_dir()
        or execution_cwd != lexical_absolute(proof_root / "work")
        or not execution_cwd.is_dir()
    ):
        raise ProofError("scratch proof execution/backup root is unavailable")
    if execution.get("backupBaseFileSetSha256") != BASE_PROJECT_FILE_SET_SHA256:
        raise ProofError("scratch proof backup fingerprint is not exact")
    require_expected_base_project(backup_root)
    run_specs = receipt.get("runs")
    expected_paths = [f"runs/{run_id}/run.json" for run_id in RUN_IDS]
    if (
        not isinstance(run_specs, list)
        or [item.get("path") for item in run_specs if isinstance(item, dict)]
        != expected_paths
    ):
        raise ProofError("scratch proof does not contain the exact ordered 17-run set")

    main_project = lexical_absolute(proof_root / "main-project")
    poison_project = lexical_absolute(proof_root / "poison-project")
    target_sha = sha256_file(target_path)
    count = len(addresses)
    tools_dir = (proof_root / "tools").resolve()
    expected_environment = expected_sanitized_environment(proof_root, tools["java"])
    if execution.get("environment") != expected_environment:
        raise ProofError("scratch proof execution environment is not exactly sanitized")
    isolated_python = [str(python), *PYTHON_ISOLATION_FLAGS]

    def inventory_argv(run_id: str, project: Path) -> list[str]:
        root = proof_root / "runs" / run_id
        arguments = [
            str(project), "BEA", "-process", PROGRAM_NAME,
            "-readOnly", "-noanalysis", "-scriptPath", str(tools_dir),
            "-postScript", tools["inventory"].name,
            str((root / "functions.tsv").resolve()),
            str((root / "program.tsv").resolve()),
        ]
        return windows_batch_argv(tools["headless"], arguments)

    def promotion_argv(
        run_id: str,
        project: Path,
        input_path: Path,
        expected_sha: str,
        expected_count: int,
        mode: str,
        read_only: bool,
    ) -> list[str]:
        root = proof_root / "runs" / run_id
        arguments = [str(project), "BEA", "-process", PROGRAM_NAME]
        if read_only:
            arguments.append("-readOnly")
        arguments.extend(
            [
                "-noanalysis", "-scriptPath", str(tools_dir), "-postScript",
                tools["promotion"].name, str(input_path.resolve()), expected_sha,
                str(expected_count), str((root / f"{mode}.tsv").resolve()),
                str((root / f"{mode}.ready.json").resolve()), mode,
            ]
        )
        return windows_batch_argv(tools["headless"], arguments)

    wrong_sha = ("0" if target_sha[0] != "0" else "1") + target_sha[1:]
    guard_undefined = proof_root / "inputs" / "guard-undefined.txt"
    guard_inside = proof_root / "inputs" / "guard-inside-existing.txt"
    undefined_address = guard_undefined.read_text(encoding="ascii").strip()
    inside_address = guard_inside.read_text(encoding="ascii").strip()
    inside_error_pattern = re.compile(
        rf"^target lies inside existing function: {re.escape(inside_address)} containing=0x[0-9a-f]{{8}}$"
    )
    expected_argv: dict[str, list[str]] = {
        "copy-main": [
            *isolated_python, str(tools["backup"]), "copy", str(backup_root),
            str(main_project), "--project-name", "BEA",
        ],
        "copy-poison": [
            *isolated_python, str(tools["backup"]), "copy", str(backup_root),
            str(poison_project), "--project-name", "BEA",
        ],
        "main-baseline": inventory_argv("main-baseline", main_project),
        "main-dry": promotion_argv(
            "main-dry", main_project, target_path, target_sha, count, "dry", True
        ),
        "guard-undefined": promotion_argv(
            "guard-undefined", main_project, guard_undefined,
            sha256_file(guard_undefined), 1, "dry", True,
        ),
        "guard-inside-existing": promotion_argv(
            "guard-inside-existing", main_project, guard_inside,
            sha256_file(guard_inside), 1, "dry", True
        ),
        "inspect-poison-pre": [
            *isolated_python, str(tools["backup"]), "inspect", str(poison_project),
            "--project-name", "BEA", "--output",
            str((proof_root / "runs" / "poison-pre-manifest.json").resolve()),
        ],
        "poison-baseline": inventory_argv("poison-baseline", poison_project),
        "poison-wrong-sha": promotion_argv(
            "poison-wrong-sha", poison_project, target_path, wrong_sha, count,
            "apply", False,
        ),
        "inspect-poison-post": [
            *isolated_python, str(tools["backup"]), "inspect", str(poison_project),
            "--project-name", "BEA", "--output",
            str((proof_root / "runs" / "poison-post-manifest.json").resolve()),
        ],
        "poison-after": inventory_argv("poison-after", poison_project),
        "inspect-main-preapply": [
            *isolated_python, str(tools["backup"]), "inspect", str(main_project),
            "--project-name", "BEA", "--output",
            str((proof_root / "runs" / "main-preapply-manifest.json").resolve()),
        ],
        "main-apply": promotion_argv(
            "main-apply", main_project, target_path, target_sha, count, "apply", False
        ),
        "main-readback": promotion_argv(
            "main-readback", main_project, target_path, target_sha, count,
            "readback", True,
        ),
        "main-after": inventory_argv("main-after", main_project),
        "diff-main-inventory": [
            *isolated_python, str(tools["diff"]),
            str((proof_root / "runs/main-baseline/functions.tsv").resolve()),
            str((proof_root / "runs/main-after/functions.tsv").resolve()),
            "--json",
            str((proof_root / "runs/main-after/inventory-diff.json").resolve()),
            "--sample-created", str(count),
        ],
        "inspect-main-postverification": [
            *isolated_python, str(tools["backup"]), "inspect", str(main_project),
            "--project-name", "BEA", "--output",
            str((proof_root / "runs/main-postverification-manifest.json").resolve()),
        ],
    }

    runs: dict[str, dict] = {}
    previous_completed: datetime | None = None
    base_keys = {
        "id", "startedAtUtc", "completedAtUtc", "cwd", "argv", "exitCode",
        "environment", "log", "verdict", "observations",
    }
    auxiliary = {
        "copy-main", "copy-poison", "inspect-poison-pre", "inspect-poison-post",
        "inspect-main-preapply", "diff-main-inventory",
        "inspect-main-postverification",
    }
    inventories = {
        "main-baseline": main_project,
        "poison-baseline": poison_project,
        "poison-after": poison_project,
        "main-after": main_project,
    }
    successful_promotions = {
        "main-dry": (main_project, "dry", True, False),
        "main-apply": (main_project, "apply", False, True),
        "main-readback": (main_project, "readback", True, False),
    }
    for run_id, run_spec in zip(RUN_IDS, run_specs):
        run_path = proof_root / str(run_spec["path"])
        if stamp(run_path, proof_root) != run_spec:
            raise ProofError(f"scratch proof run receipt has changed: {run_id}")
        run = read_json(run_path, f"scratch proof run {run_id}")
        if (
            set(run) != base_keys
            or run.get("id") != run_id
            or run.get("cwd") != str(execution_cwd)
            or run.get("argv") != expected_argv[run_id]
            or run.get("environment") != expected_environment
            or run.get("exitCode") != 0
            or run.get("verdict") != "SURVIVED"
            or not isinstance(run.get("observations"), dict)
        ):
            raise ProofError(f"scratch proof run envelope is not exact: {run_id}")
        started = _iso_timestamp(run.get("startedAtUtc"), f"{run_id} start")
        completed = _iso_timestamp(run.get("completedAtUtc"), f"{run_id} completion")
        if completed < started or (previous_completed is not None and started < previous_completed):
            raise ProofError("scratch proof run chronology is not monotonic")
        previous_completed = completed
        log_spec = run.get("log")
        log_path = proof_root / str(log_spec.get("path", ""))
        if stamp(log_path, proof_root) != log_spec:
            raise ProofError(f"scratch proof run log has changed: {run_id}")
        log = log_path.read_text(encoding="utf-8")
        if run_id in inventories or run_id in successful_promotions or run_id in {
            "guard-undefined", "guard-inside-existing", "poison-wrong-sha"
        }:
            ghidra_root = tools["headless"].parent.parent.as_posix()
            launcher_marker = (
                f"Using log config file: jar:file:/{ghidra_root}/Ghidra/"
                "Framework/Generic/lib/Generic.jar!"
            )
            if log.count(launcher_marker) != 1:
                raise ProofError(
                    f"scratch proof log is not bound to the stamped Ghidra launcher: {run_id}"
                )
            expected_log_root = (
                Path(expected_environment["APPDATA"])
                / "ghidra"
                / GHIDRA_SETTINGS_DIRECTORY
            )
            expected_log_marker = f"Using log file: {expected_log_root / 'application.log'}"
            if log.count(expected_log_marker) != 1:
                raise ProofError(
                    f"scratch proof log is not bound to the isolated Ghidra profile: {run_id}"
                )

        expected_observations: dict[str, object]
        if run_id in auxiliary:
            if any(marker in log for marker in ERROR_MARKERS):
                raise ProofError(f"scratch proof auxiliary log has an error: {run_id}")
            expected_observations = {}
        elif run_id in inventories:
            project = inventories[run_id]
            functions = proof_root / f"runs/{run_id}/functions.tsv"
            program = proof_root / f"runs/{run_id}/program.tsv"
            function_rows = inventory_map(functions)
            program_values = program_map(program)
            require_clean_log(log, run_id)
            require_tool_sentinel(
                log,
                prefix="INVENTORY_TOOL_OK",
                tool=tools["inventory"],
                tool_stamp=stamp(tools["inventory"], proof_root),
            )
            sentinel = (
                f"INVENTORY_OK functions={len(function_rows)} "
                f"instructions={int(program_values['instructions'])}"
            )
            if log.count(sentinel) != 1:
                raise ProofError(f"scratch proof inventory sentinel is absent: {run_id}")
            expected_observations = {
                "projectRoot": str(project),
                "readOnly": True,
                "functionCount": len(function_rows),
                "instructionCount": int(program_values["instructions"]),
                "functions": stamp(functions, proof_root),
                "program": stamp(program, proof_root),
            }
        elif run_id in successful_promotions:
            project, mode, read_only, save_reported = successful_promotions[run_id]
            tsv = proof_root / f"runs/{run_id}/{mode}.tsv"
            ready = proof_root / f"runs/{run_id}/{mode}.ready.json"
            ready_value = validate_ready(
                ready_path=ready,
                mode=mode,
                target_path=target_path,
                target_stamp=stamp(target_path, proof_root),
                target_count=count,
                semantic_target_sha256=semantic_target_sha(addresses),
                tool=tools["promotion"],
                tool_stamp=stamp(tools["promotion"], proof_root),
                output_path=tsv,
                proof_root=proof_root,
            )
            require_clean_log(log, run_id)
            require_tool_sentinel(
                log,
                prefix="FUNCTION_PROMOTION_TOOL_OK",
                tool=tools["promotion"],
                tool_stamp=stamp(tools["promotion"], proof_root),
            )
            counts = expected_counts(mode, count)
            sentinel = (
                f"FUNCTION_PROMOTION_OK mode={mode} targets={count} "
                f"would_create={counts['wouldCreate']} created={counts['created']} "
                f"already_exists={counts['alreadyExists']} verified={counts['verified']} "
                f"mutation_committed={'true' if mode == 'apply' else 'false'}"
            )
            if log.count(sentinel) != 1:
                raise ProofError(f"scratch proof promotion sentinel is absent: {run_id}")
            expected_observations = {
                "projectRoot": str(project),
                "readOnly": read_only,
                "mode": mode,
                "tsv": stamp(tsv, proof_root),
                "ready": stamp(ready, proof_root),
                "instructionCount": ready_value["counts"]["programInstructionsAfter"],
                "saveReported": save_reported,
            }
        else:
            input_path = guard_undefined if run_id == "guard-undefined" else (
                guard_inside if run_id == "guard-inside-existing" else target_path
            )
            project = poison_project if run_id == "poison-wrong-sha" else main_project
            expected_error = (
                "target has no defined instruction"
                if run_id == "guard-undefined"
                else None
            )
            observed_error = str(run["observations"].get("expectedError", ""))
            if run_id == "guard-inside-existing":
                if inside_error_pattern.fullmatch(observed_error) is None:
                    raise ProofError("inside-existing control error is not exact")
                expected_error = observed_error
            elif run_id == "poison-wrong-sha":
                expected_error = (
                    f"address-list sha256 mismatch expected={wrong_sha} actual={target_sha}"
                )
            assert expected_error is not None
            output = proof_root / f"runs/{run_id}/{'apply' if run_id == 'poison-wrong-sha' else 'dry'}.tsv"
            ready_output = proof_root / f"runs/{run_id}/{'apply' if run_id == 'poison-wrong-sha' else 'dry'}.ready.json"
            if (
                log.count("REPORT SCRIPT ERROR") != 1
                or log.count(expected_error) != 1
                or "FUNCTION_PROMOTION_PREFLIGHT_OK" in log
                or "FUNCTION_PROMOTION_OK" in log
                or "FUNCTION_PROMOTION_RECEIPT_LOST" in log
                or output.exists()
                or ready_output.exists()
            ):
                raise ProofError(f"scratch proof negative control did not cleanly reject: {run_id}")
            expected_observations = {
                "projectRoot": str(project),
                "readOnly": run_id != "poison-wrong-sha",
                "rejectedBeforePromotionPreflight": True,
                "expectedError": expected_error,
                "outputTsvAbsent": True,
                "outputReadyAbsent": True,
                "saveReported": run_id == "poison-wrong-sha",
            }
        if run["observations"] != expected_observations:
            raise ProofError(f"scratch proof run observations are not reproduced: {run_id}")
        runs[run_id] = run
    return runs


def verify_ready_receipt(ready_path: Path) -> dict:
    ready_path = require_plain_file(
        ready_path, "scratch proof READY", single_link=True
    )
    proof_root = ready_path.parent
    receipt = read_json(ready_path, "scratch proof READY")
    expected_top_keys = {
        "schema", "finalizedAtUtc", "verdict", "claimBoundary", "execution",
        "program", "targets", "targetSourceCampaign", "toolchain", "projects",
        "runs", "checks", "artifacts",
    }
    if (
        receipt.get("schema") != SCHEMA
        or receipt.get("verdict") != "SURVIVED"
        or set(receipt) != expected_top_keys
    ):
        raise ProofError("scratch proof READY schema/verdict is unsupported")
    _iso_timestamp(receipt.get("finalizedAtUtc"), "proof finalization")
    if receipt.get("claimBoundary") != list(CLAIM_BOUNDARY):
        raise ProofError("scratch proof claim boundary is not exact")
    expected_program = {
        "name": PROGRAM_NAME,
        "md5": PROGRAM_MD5,
        "sha256": PROGRAM_SHA256,
        "imageBase": IMAGE_BASE,
        "language": LANGUAGE,
        "compilerSpec": COMPILER_SPEC,
    }
    if receipt.get("program") != expected_program:
        raise ProofError("scratch proof program identity is not exact")
    expected_artifacts = receipt.get("artifacts")
    if not isinstance(expected_artifacts, dict) or artifact_set(proof_root) != expected_artifacts:
        raise ProofError("scratch proof artifact set has changed")

    tools = _verify_tool_snapshots(proof_root, receipt)
    execution = receipt.get("execution")
    if not isinstance(execution, dict) or set(execution) != {
        "repoRoot", "backupRoot", "backupBaseFileSetSha256", "projectName",
        "python", "environment", "workingDirectory",
    }:
        raise ProofError("scratch proof execution environment is malformed")
    python = _verify_python_stamp(execution.get("python"))
    expected_environment = expected_sanitized_environment(proof_root, tools["java"])
    if execution.get("environment") != expected_environment:
        raise ProofError("scratch proof execution environment is not exactly sanitized")

    targets = receipt.get("targets")
    if not isinstance(targets, dict) or set(targets) != {
        "list", "ready", "count", "semanticTargetSetSha256", "namesAuthorized"
    }:
        raise ProofError("scratch proof target envelope is malformed")
    target_path = proof_root / "inputs" / "boundary-targets.txt"
    target_ready_path = proof_root / "inputs" / "boundary-targets.ready.json"
    if (
        stamp(target_path, proof_root) != targets.get("list")
        or stamp(target_ready_path, proof_root) != targets.get("ready")
        or targets.get("namesAuthorized") is not False
        or sha256_file(target_path) != BOUNDARY_TARGET_SHA256
        or sha256_file(target_ready_path) != BOUNDARY_TARGET_READY_SHA256
        or targets.get("count") != BOUNDARY_TARGET_COUNT
    ):
        raise ProofError("scratch proof target artifacts/policy have changed")
    require_authorized_pilot_inputs(
        target_content=target_path.read_bytes(),
        ready_content=target_ready_path.read_bytes(),
        requested_sha256=str(targets["list"]["sha256"]),
        requested_count=int(targets["count"]),
    )
    addresses = target_path.read_text(encoding="ascii").splitlines()
    if (
        len(addresses) != targets.get("count")
        or len(addresses) != len(set(addresses))
        or any(re.fullmatch(r"0x[0-9a-f]{8}", address) is None for address in addresses)
        or semantic_target_sha(addresses) != targets.get("semanticTargetSetSha256")
    ):
        raise ProofError("scratch proof target cohort is not canonical")
    source_campaign = receipt.get("targetSourceCampaign")
    if not isinstance(source_campaign, dict) or set(source_campaign) != {
        "root", "ready", "fileCount", "fileSetSha256", "snapshotRoot",
        "snapshotReady", "snapshotFileCount", "snapshotFileSetSha256", "replay",
    }:
        raise ProofError("scratch proof target source campaign is malformed")
    if source_campaign.get("root") != "inputs/source-campaign":
        raise ProofError("scratch proof target source campaign root is not self-contained")
    source_campaign_root = proof_root / "inputs" / "source-campaign"
    require_authorized_source_campaign_ready(
        source_campaign_root / "campaign.ready.json"
    )
    source_rows = tree_rows_from_disk(source_campaign_root)
    if (
        source_campaign.get("fileCount") != len(source_rows)
        or source_campaign.get("fileSetSha256") != canonical_rows_sha(source_rows)
        or stamp(source_campaign_root / "campaign.ready.json", proof_root)
        != source_campaign.get("ready")
        or sha256_file(source_campaign_root / "campaign.ready.json")
        != BOUNDARY_SOURCE_CAMPAIGN_READY_SHA256
    ):
        raise ProofError("scratch proof target source campaign bytes have changed")
    snapshot_root_value = source_campaign.get("snapshotRoot")
    if not isinstance(snapshot_root_value, str):
        raise ProofError("scratch proof target source snapshot root is malformed")
    snapshot_relative = Path(snapshot_root_value)
    if snapshot_relative.is_absolute() or ".." in snapshot_relative.parts:
        raise ProofError("scratch proof target source snapshot root is unsafe")
    source_snapshot_root = proof_root / snapshot_relative
    snapshot_rows = tree_rows_from_disk(source_snapshot_root)
    if (
        source_campaign.get("snapshotFileCount") != len(snapshot_rows)
        or source_campaign.get("snapshotFileSetSha256")
        != canonical_rows_sha(snapshot_rows)
        or stamp(source_snapshot_root / "ledger.ready.json", proof_root)
        != source_campaign.get("snapshotReady")
    ):
        raise ProofError("scratch proof target source snapshot bytes have changed")
    validated_target = validate_boundary_target_source(
        ready_path=target_ready_path,
        target_path=target_path,
        repo_root=proof_root,
        source_override=source_campaign_root,
        require_exact_reducer_tree=True,
        snapshot_origin_root=Path(str(execution["repoRoot"])),
    )
    if (
        validated_target["addresses"] != addresses
        or validated_target["snapshotRelative"].as_posix()
        != snapshot_relative.as_posix()
    ):
        raise ProofError("scratch proof target source does not reproduce the cohort")
    replay_path = proof_root / "inputs" / "source-campaign-replay.json"
    if stamp(replay_path, proof_root) != source_campaign.get("replay"):
        raise ProofError("scratch proof target source campaign replay has changed")
    recorded_replay = read_json(replay_path, "scratch proof target campaign replay")
    actual_replay = _run_frozen_campaign_verify(
        source_root=source_campaign_root,
        authority_root=proof_root,
        python=python,
        environment=expected_environment,
        campaign_ready=validated_target["campaignReady"],
        snapshot_relative=validated_target["snapshotRelative"],
    )
    if recorded_replay != actual_replay:
        raise ProofError("scratch proof target source campaign replay does not reproduce")

    projects = receipt.get("projects")
    if not isinstance(projects, dict) or set(projects) != {
        "mainScratch", "poisonControl"
    }:
        raise ProofError("scratch proof READY has no project evidence")
    main_project = lexical_absolute(proof_root / "main-project")
    poison_project = lexical_absolute(proof_root / "poison-project")
    main = projects["mainScratch"]
    poison = projects["poisonControl"]
    if not isinstance(main, dict) or set(main) != {
        "root", "copyManifest", "preapplyManifest", "postverificationManifest",
        "baseFileSetSha256", "finalFileSetSha256",
    }:
        raise ProofError("scratch proof main project envelope is malformed")
    if not isinstance(poison, dict) or set(poison) != {
        "root", "copyManifest", "preManifest", "postManifest",
        "baseFileSetSha256", "finalFileSetSha256", "rawProjectChanged",
        "saveReported", "semanticInventoryStable",
    }:
        raise ProofError("scratch proof poison project envelope is malformed")
    if main.get("root") != str(main_project) or poison.get("root") != str(poison_project):
        raise ProofError("scratch proof project roots do not point inside this proof")

    project_artifacts = {
        "main-copy": (main_project / "backup_manifest.json", main["copyManifest"]),
        "main-pre": (
            proof_root / "runs/main-preapply-manifest.json",
            main["preapplyManifest"],
        ),
        "main-post": (
            proof_root / "runs/main-postverification-manifest.json",
            main["postverificationManifest"],
        ),
        "poison-copy": (
            poison_project / "backup_manifest.json", poison["copyManifest"]
        ),
        "poison-pre": (
            proof_root / "runs/poison-pre-manifest.json", poison["preManifest"]
        ),
        "poison-post": (
            proof_root / "runs/poison-post-manifest.json", poison["postManifest"]
        ),
    }
    for label, (path, spec) in project_artifacts.items():
        if stamp(path, proof_root) != spec:
            raise ProofError(f"scratch proof project artifact has changed: {label}")
    main_source_rows, base_rows = validate_copy_manifest(
        project_artifacts["main-copy"][0]
    )
    poison_source_rows, poison_base_rows = validate_copy_manifest(
        project_artifacts["poison-copy"][0]
    )
    backup_project = require_plain_existing_ancestors(
        Path(str(execution["backupRoot"])), "backup input"
    )
    backup_rows = require_expected_base_project(backup_project)
    if (
        base_rows != poison_base_rows
        or main_source_rows != base_rows
        or poison_source_rows != base_rows
        or backup_rows != base_rows
        or canonical_rows_sha(base_rows) != BASE_PROJECT_FILE_SET_SHA256
    ):
        raise ProofError("scratch proof project clones have different bases")
    main_pre_rows = manifest_rows(
        project_artifacts["main-pre"][0], expected_root=main_project
    )
    poison_pre_rows = manifest_rows(
        project_artifacts["poison-pre"][0], expected_root=poison_project
    )
    main_post_rows = manifest_rows(
        project_artifacts["main-post"][0], expected_root=main_project
    )
    poison_post_rows = manifest_rows(
        project_artifacts["poison-post"][0], expected_root=poison_project
    )
    if main_pre_rows != base_rows or poison_pre_rows != base_rows:
        raise ProofError("scratch proof projects differ from their base before mutation")
    if project_rows_from_disk(main_project, "BEA") != main_post_rows:
        raise ProofError("scratch proof main project bytes differ from final manifest")
    if project_rows_from_disk(poison_project, "BEA") != poison_post_rows:
        raise ProofError("scratch proof poison project bytes differ from final manifest")

    runs = _verify_run_receipts(proof_root, receipt, tools, target_path, addresses)

    baseline_functions = proof_root / "runs/main-baseline/functions.tsv"
    baseline_program = proof_root / "runs/main-baseline/program.tsv"
    after_functions = proof_root / "runs/main-after/functions.tsv"
    after_program = proof_root / "runs/main-after/program.tsv"
    poison_before_functions = proof_root / "runs/poison-baseline/functions.tsv"
    poison_before_program = proof_root / "runs/poison-baseline/program.tsv"
    poison_after_functions = proof_root / "runs/poison-after/functions.tsv"
    poison_after_program = proof_root / "runs/poison-after/program.tsv"
    dry_tsv = proof_root / "runs/main-dry/dry.tsv"
    apply_tsv = proof_root / "runs/main-apply/apply.tsv"
    readback_tsv = proof_root / "runs/main-readback/readback.tsv"
    diff_path = proof_root / "runs/main-after/inventory-diff.json"

    if (
        baseline_functions.read_bytes() != poison_before_functions.read_bytes()
        or baseline_program.read_bytes() != poison_before_program.read_bytes()
    ):
        raise ProofError("scratch proof clone baselines are not byte-identical")
    if (
        sha256_file(poison_before_functions) != sha256_file(poison_after_functions)
        or sha256_file(poison_before_program) != sha256_file(poison_after_program)
    ):
        raise ProofError("scratch proof poisoned-SHA control changed semantic inventory")
    before_rows = inventory_map(baseline_functions)
    after_rows = inventory_map(after_functions)
    target_set = set(addresses)
    created = set(after_rows) - set(before_rows)
    destroyed = set(before_rows) - set(after_rows)
    existing_changes = sum(
        before_rows[address] != after_rows[address]
        for address in set(before_rows) & set(after_rows)
    )
    if created != target_set or destroyed or existing_changes:
        raise ProofError("scratch proof main inventory delta exceeds the target cohort")
    apply_rows = inventory_map(apply_tsv)
    readback_rows = inventory_map(readback_tsv)
    if set(apply_rows) != target_set or set(readback_rows) != target_set:
        raise ProofError("scratch proof apply/readback ledgers differ from target set")
    metadata_fields = (
        "name", "nameSource", "bodyBytes", "bodyMin", "bodyMax", "bodyRanges",
        "instrCount",
    )
    for address in addresses:
        if (
            apply_rows[address].get("status") != "created"
            or readback_rows[address].get("status") != "verified"
            or apply_rows[address].get("nameSource") != "DEFAULT"
        ):
            raise ProofError(f"scratch proof target status/name source is wrong: {address}")
        for field in metadata_fields:
            if not (
                apply_rows[address].get(field)
                == readback_rows[address].get(field)
                == after_rows[address].get(field)
            ):
                raise ProofError(f"scratch proof target metadata differs: {address} {field}")
    dry_rows = read_tsv(dry_tsv)
    dry_exact = (
        [row.get("address", "").lower() for row in dry_rows] == addresses
        and {row.get("status") for row in dry_rows} == {"would_create"}
    )
    if not dry_exact:
        raise ProofError("scratch proof dry ledger does not reproduce the target sequence")

    before_program = program_map(baseline_program)
    after_program_values = program_map(after_program)
    expected_program_identity = {
        "programName": PROGRAM_NAME,
        "executableMD5": PROGRAM_MD5,
        "executableSHA256": PROGRAM_SHA256,
        "imageBase": IMAGE_BASE,
        "language": LANGUAGE,
        "compilerSpec": COMPILER_SPEC,
    }
    if any(
        before_program.get(metric) != value
        for metric, value in expected_program_identity.items()
    ):
        raise ProofError("scratch proof baseline inventory program identity is not exact")
    if set(before_program) != set(after_program_values):
        raise ProofError("scratch proof program metric set changed")
    for metric, before_value in before_program.items():
        after_value = after_program_values[metric]
        if metric == "functions":
            if int(after_value) - int(before_value) != len(addresses):
                raise ProofError("scratch proof function count delta is wrong")
        elif before_value != after_value:
            raise ProofError(f"scratch proof program metric changed: {metric}")
    baseline_instruction_count = int(before_program["instructions"])
    after_instruction_count = int(after_program_values["instructions"])
    expected_run_instruction_counts = {
        "main-dry": baseline_instruction_count,
        "main-apply": after_instruction_count,
        "main-readback": after_instruction_count,
    }
    for run_id, expected_instruction_count in expected_run_instruction_counts.items():
        if runs[run_id]["observations"]["instructionCount"] != expected_instruction_count:
            raise ProofError(
                f"scratch proof {run_id} READY instruction count is not inventory-bound"
            )
    diff = read_json(diff_path, "scratch proof inventory diff")
    diff_counts = diff.get("counts")
    expected_diff_counts = {
        "before": len(before_rows),
        "after": len(after_rows),
        "created": len(addresses),
        "destroyed": 0,
        "boundsChanged": 0,
        "namesChanged": 0,
        "signaturesChanged": 0,
        "instrCountChanged": 0,
    }
    if not isinstance(diff_counts, dict) or any(
        diff_counts.get(key) != value for key, value in expected_diff_counts.items()
    ):
        raise ProofError("scratch proof inventory diff exceeds boundary creation")
    if {row.get("address") for row in diff.get("created", [])} != target_set:
        raise ProofError("scratch proof inventory diff created sample is not the target set")

    inside_address = int(
        (proof_root / "inputs/guard-inside-existing.txt").read_text().strip(), 16
    )
    containing_rows = [
        row
        for row in before_rows.values()
        if int(row["bodyMin"], 16) <= inside_address <= int(row["bodyMax"], 16)
    ]
    inside_error = runs["guard-inside-existing"]["observations"]["expectedError"]
    containing_match = re.search(r"containing=(0x[0-9a-f]{8})$", inside_error)
    if (
        len(containing_rows) != 1
        or containing_match is None
        or containing_match.group(1) != containing_rows[0]["address"].lower()
    ):
        raise ProofError("inside-existing negative control names the wrong containing body")

    poison_raw_changed = poison_post_rows != base_rows
    derived_projects = {
        "mainScratch": {
            "root": str(main_project),
            "copyManifest": stamp(project_artifacts["main-copy"][0], proof_root),
            "preapplyManifest": stamp(project_artifacts["main-pre"][0], proof_root),
            "postverificationManifest": stamp(
                project_artifacts["main-post"][0], proof_root
            ),
            "baseFileSetSha256": canonical_rows_sha(base_rows),
            "finalFileSetSha256": canonical_rows_sha(main_post_rows),
        },
        "poisonControl": {
            "root": str(poison_project),
            "copyManifest": stamp(project_artifacts["poison-copy"][0], proof_root),
            "preManifest": stamp(project_artifacts["poison-pre"][0], proof_root),
            "postManifest": stamp(project_artifacts["poison-post"][0], proof_root),
            "baseFileSetSha256": canonical_rows_sha(base_rows),
            "finalFileSetSha256": canonical_rows_sha(poison_post_rows),
            "rawProjectChanged": poison_raw_changed,
            "saveReported": runs["poison-wrong-sha"]["observations"]["saveReported"],
            "semanticInventoryStable": True,
        },
    }
    if projects != derived_projects:
        raise ProofError("scratch proof project claims do not reproduce from artifacts")
    derived_checks = {
        "dryExactTargetSequence": dry_exact,
        "applyCreatedExactTargetSet": created == target_set,
        "readbackMatchesApplyMetadata": True,
        "instructionCountBefore": int(before_program["instructions"]),
        "instructionCountAfter": int(after_program_values["instructions"]),
        "functionsBefore": len(before_rows),
        "functionsAfter": len(after_rows),
        "existingFunctionFieldChanges": existing_changes,
        "destroyedFunctions": len(destroyed),
        "poisonedShaRejectedWithoutOutputs": True,
        "poisonedShaSemanticInventoryStable": True,
        "poisonedShaRawProjectChanged": poison_raw_changed,
        "undefinedInstructionControl": "SURVIVED",
        "insideExistingFunctionControl": "SURVIVED",
    }
    if receipt.get("checks") != derived_checks:
        raise ProofError("scratch proof checks do not reproduce from raw artifacts")
    reverify_retained_project_inventories(
        proof_root=proof_root,
        headless=tools["headless"],
        java=tools["java"],
        inventory_tool=tools["inventory"],
        backup_project=backup_project,
        main_project=main_project,
        poison_project=poison_project,
    )
    return {**receipt, "ready": external_stamp(ready_path)}


def run(args: argparse.Namespace) -> dict:
    repo_root = Path(__file__).resolve().parent.parent
    proof_root = require_plain_existing_ancestors(args.out, "proof output")
    local_lab = (repo_root / "local-lab").resolve()
    try:
        proof_root.relative_to(local_lab)
    except ValueError as exc:
        raise ProofError("proof output must be under the ignored local-lab scope") from exc
    if proof_root.exists():
        raise ProofError(f"proof output already exists: {proof_root}")
    if os.name == "nt" and ctypes.windll.shell32.IsUserAnAdmin():
        raise ProofError("scratch proof must run non-elevated")
    backup_root = require_plain_existing_ancestors(args.backup_root, "backup input")
    try:
        backup_root.relative_to(local_lab)
    except ValueError as exc:
        raise ProofError("backup input must be under the ignored local-lab scope") from exc
    require_expected_base_project(backup_root)
    headless, application_properties, host_java = require_expected_external_toolchain(
        args.headless
    )
    args.headless = headless
    python = require_expected_python(Path(sys.executable))
    sources = {
        "runner": Path(__file__).resolve(),
        "promotion": args.promotion_tool.resolve(),
        "inventory": args.inventory_tool.resolve(),
        "backup": args.backup_tool.resolve(),
        "diff": args.diff_tool.resolve(),
    }
    for role, source in sources.items():
        if not source.is_file():
            raise ProofError(f"{role} source is missing: {source}")
        if role in TRUSTED_TOOL_SHA256:
            require_trusted_tool_source(role, source)
    target_content = args.targets.read_bytes()
    if args.target_ready is None:
        raise ProofError("a verified boundary-target READY receipt is required")
    ready_content = args.target_ready.read_bytes()
    require_authorized_pilot_inputs(
        target_content=target_content,
        ready_content=ready_content,
        requested_sha256=args.expected_target_sha256,
        requested_count=args.expected_count,
    )
    ghidra_root = headless.parent.parent
    jdk_root = host_java.parent.parent
    python_root = Path(sys.base_prefix).resolve()
    ghidra_distribution_rows = require_expected_distribution(
        ghidra_root,
        label="Ghidra",
        expected_count=GHIDRA_DISTRIBUTION_FILE_COUNT,
        expected_total_bytes=GHIDRA_DISTRIBUTION_TOTAL_BYTES,
        expected_sha256=GHIDRA_DISTRIBUTION_FILE_SET_SHA256,
    )
    jdk_distribution_rows = require_expected_distribution(
        jdk_root,
        label="JDK",
        expected_count=JDK_DISTRIBUTION_FILE_COUNT,
        expected_total_bytes=JDK_DISTRIBUTION_TOTAL_BYTES,
        expected_sha256=JDK_DISTRIBUTION_FILE_SET_SHA256,
    )
    python_distribution_rows = require_expected_distribution(
        python_root,
        label="Python",
        expected_count=PYTHON_DISTRIBUTION_FILE_COUNT,
        expected_total_bytes=PYTHON_DISTRIBUTION_TOTAL_BYTES,
        expected_sha256=PYTHON_DISTRIBUTION_FILE_SET_SHA256,
    )
    proof_root.mkdir(parents=True)
    (proof_root / "tools").mkdir()
    (proof_root / "inputs").mkdir()
    (proof_root / "runs").mkdir()
    execution_cwd = proof_root / "work"
    execution_cwd.mkdir()
    execution_environment = prepare_sanitized_environment(proof_root, host_java)
    toolchain_manifest_root = proof_root / "inputs" / "toolchain"
    toolchain_manifest_root.mkdir()
    ghidra_manifest_path = toolchain_manifest_root / "ghidra-files.tsv"
    jdk_manifest_path = toolchain_manifest_root / "jdk-files.tsv"
    python_manifest_path = toolchain_manifest_root / "python-files.tsv"
    write_distribution_manifest(ghidra_manifest_path, ghidra_distribution_rows)
    write_distribution_manifest(jdk_manifest_path, jdk_distribution_rows)
    write_distribution_manifest(python_manifest_path, python_distribution_rows)
    ghidra_distribution = distribution_receipt(
        root=ghidra_root,
        manifest_path=ghidra_manifest_path,
        proof_root=proof_root,
        rows=ghidra_distribution_rows,
    )
    jdk_distribution = distribution_receipt(
        root=jdk_root,
        manifest_path=jdk_manifest_path,
        proof_root=proof_root,
        rows=jdk_distribution_rows,
    )
    python_distribution = distribution_receipt(
        root=python_root,
        manifest_path=python_manifest_path,
        proof_root=proof_root,
        rows=python_distribution_rows,
    )

    snapshots: dict[str, dict[str, object]] = {}
    for role, source in sources.items():
        if not source.is_file():
            raise ProofError(f"{role} source is missing: {source}")
        destination = proof_root / "tools" / source.name
        snapshots[role] = snapshot_tool(source, destination)
        snapshots[role]["snapshot"] = stamp(destination, proof_root)

    promotion_tool = proof_root / str(snapshots["promotion"]["snapshot"]["path"])
    inventory_tool = proof_root / str(snapshots["inventory"]["snapshot"]["path"])
    backup_tool = proof_root / str(snapshots["backup"]["snapshot"]["path"])
    diff_tool = proof_root / str(snapshots["diff"]["snapshot"]["path"])
    promotion_stamp = stamp(promotion_tool, proof_root)
    inventory_stamp = stamp(inventory_tool, proof_root)

    target_path = proof_root / "inputs" / "boundary-targets.txt"
    write_new(target_path, target_content)
    target_stamp = stamp(target_path, proof_root)
    addresses = target_content.decode("ascii").splitlines()
    if (
        len(addresses) != args.expected_count
        or len(addresses) != len(set(addresses))
        or any(re.fullmatch(r"0x[0-9a-f]{8}", address) is None for address in addresses)
    ):
        raise ProofError("target list is not the exact unique canonical cohort")
    semantic_sha = semantic_target_sha(addresses)
    target_ready_path = proof_root / "inputs" / "boundary-targets.ready.json"
    write_new(target_ready_path, ready_content)
    target_ready_stamp = stamp(target_ready_path, proof_root)
    target_validation = validate_boundary_target_source(
        ready_path=target_ready_path,
        target_path=target_path,
        repo_root=repo_root,
    )
    authoritative_source_ready = (
        Path(target_validation["sourceRoot"]) / "campaign.ready.json"
    )
    require_authorized_source_campaign_ready(authoritative_source_ready)
    if target_validation["addresses"] != addresses:
        raise ProofError("preregistered target list differs from its boundary READY")
    source_campaign_copy = proof_root / "inputs" / "source-campaign"
    copy_campaign_evidence(
        Path(target_validation["sourceRoot"]),
        source_campaign_copy,
        target_validation["campaignReady"],
    )
    snapshot_relative = target_validation["snapshotRelative"]
    source_snapshot = (repo_root / snapshot_relative).resolve()
    try:
        source_snapshot.relative_to((repo_root / "local-lab" / "re-ledger").resolve())
    except ValueError as exc:
        raise ProofError("boundary source coverage snapshot escapes local-lab/re-ledger") from exc
    source_snapshot_copy = proof_root / snapshot_relative
    copy_snapshot_evidence(source_snapshot, source_snapshot_copy)
    copied_target_validation = validate_boundary_target_source(
        ready_path=target_ready_path,
        target_path=target_path,
        repo_root=proof_root,
        source_override=source_campaign_copy,
        require_exact_reducer_tree=True,
        snapshot_origin_root=repo_root,
    )
    require_authorized_source_campaign_ready(source_campaign_copy / "campaign.ready.json")
    if copied_target_validation["addresses"] != addresses:
        raise ProofError("copied source campaign does not reproduce the target cohort")
    campaign_replay = _run_frozen_campaign_verify(
        source_root=source_campaign_copy,
        authority_root=proof_root,
        python=python,
        environment=execution_environment,
        campaign_ready=copied_target_validation["campaignReady"],
        snapshot_relative=copied_target_validation["snapshotRelative"],
    )
    campaign_replay_path = proof_root / "inputs" / "source-campaign-replay.json"
    write_new(
        campaign_replay_path,
        (json.dumps(campaign_replay, indent=2) + "\n").encode("utf-8"),
    )

    guard_inputs = {
        "guard-undefined": (args.undefined_address, "target has no defined instruction"),
        "guard-inside-existing": (
            args.inside_address,
            f"target lies inside existing function: {args.inside_address} containing={args.containing_address}",
        ),
    }
    guard_paths: dict[str, tuple[Path, str]] = {}
    for run_id, (address, expected_error) in guard_inputs.items():
        path = proof_root / "inputs" / f"{run_id}.txt"
        write_new(path, f"{address}\n".encode("ascii"))
        guard_paths[run_id] = (path, expected_error)

    actions: list[dict] = []
    main_project = proof_root / "main-project"
    poison_project = proof_root / "poison-project"
    for run_id, project in (("copy-main", main_project), ("copy-poison", poison_project)):
        action = run_auxiliary(
            proof_root=proof_root,
            run_id=run_id,
            argv=[
                str(python),
                *PYTHON_ISOLATION_FLAGS,
                str(backup_tool),
                "copy",
                str(args.backup_root.resolve()),
                str(project),
                "--project-name",
                args.project_name,
            ],
            cwd=execution_cwd,
            environment=execution_environment,
        )
        actions.append(action)

    baseline, baseline_functions, baseline_program = run_inventory(
        proof_root=proof_root,
        run_id="main-baseline",
        headless=args.headless,
        project_root=main_project,
        project_name=args.project_name,
        tool=inventory_tool,
        tool_stamp=inventory_stamp,
            cwd=execution_cwd,
        environment=execution_environment,
    )
    actions.append(baseline)
    dry, dry_tsv, _dry_ready = run_promotion(
        proof_root=proof_root,
        run_id="main-dry",
        headless=args.headless,
        project_root=main_project,
        project_name=args.project_name,
        tool=promotion_tool,
        tool_stamp=promotion_stamp,
        target_path=target_path,
        target_stamp=target_stamp,
        target_count=args.expected_count,
        semantic_target_sha256=semantic_sha,
        mode="dry",
        expected_sha256=args.expected_target_sha256,
            cwd=execution_cwd,
        environment=execution_environment,
    )
    actions.append(dry)
    for run_id, (guard_path, expected_error) in guard_paths.items():
        guard_stamp = stamp(guard_path, proof_root)
        action, _unused_tsv, _unused_ready = run_promotion(
            proof_root=proof_root,
            run_id=run_id,
            headless=args.headless,
            project_root=main_project,
            project_name=args.project_name,
            tool=promotion_tool,
            tool_stamp=promotion_stamp,
            target_path=guard_path,
            target_stamp=guard_stamp,
            target_count=1,
            semantic_target_sha256=semantic_target_sha([guard_path.read_text().strip()]),
            mode="dry",
            expected_sha256=str(guard_stamp["sha256"]),
            cwd=execution_cwd,
            environment=execution_environment,
            expected_error=expected_error,
        )
        actions.append(action)

    poison_pre_manifest = proof_root / "runs" / "poison-pre-manifest.json"
    actions.append(
        run_auxiliary(
            proof_root=proof_root,
            run_id="inspect-poison-pre",
            argv=[
                str(python),
                *PYTHON_ISOLATION_FLAGS,
                str(backup_tool),
                "inspect",
                str(poison_project),
                "--project-name",
                args.project_name,
                "--output",
                str(poison_pre_manifest),
            ],
            cwd=execution_cwd,
            environment=execution_environment,
        )
    )
    poison_baseline, poison_before_functions, poison_before_program = run_inventory(
        proof_root=proof_root,
        run_id="poison-baseline",
        headless=args.headless,
        project_root=poison_project,
        project_name=args.project_name,
        tool=inventory_tool,
        tool_stamp=inventory_stamp,
            cwd=execution_cwd,
        environment=execution_environment,
    )
    actions.append(poison_baseline)
    wrong_sha = ("0" if args.expected_target_sha256[0] != "0" else "1") + args.expected_target_sha256[1:]
    poison, _poison_tsv, _poison_ready = run_promotion(
        proof_root=proof_root,
        run_id="poison-wrong-sha",
        headless=args.headless,
        project_root=poison_project,
        project_name=args.project_name,
        tool=promotion_tool,
        tool_stamp=promotion_stamp,
        target_path=target_path,
        target_stamp=target_stamp,
        target_count=args.expected_count,
        semantic_target_sha256=semantic_sha,
        mode="apply",
        expected_sha256=wrong_sha,
            cwd=execution_cwd,
        environment=execution_environment,
        expected_error=(
            f"address-list sha256 mismatch expected={wrong_sha} "
            f"actual={args.expected_target_sha256}"
        ),
    )
    actions.append(poison)
    poison_post_manifest = proof_root / "runs" / "poison-post-manifest.json"
    actions.append(
        run_auxiliary(
            proof_root=proof_root,
            run_id="inspect-poison-post",
            argv=[
                str(python),
                *PYTHON_ISOLATION_FLAGS,
                str(backup_tool),
                "inspect",
                str(poison_project),
                "--project-name",
                args.project_name,
                "--output",
                str(poison_post_manifest),
            ],
            cwd=execution_cwd,
            environment=execution_environment,
        )
    )
    poison_after, poison_after_functions, poison_after_program = run_inventory(
        proof_root=proof_root,
        run_id="poison-after",
        headless=args.headless,
        project_root=poison_project,
        project_name=args.project_name,
        tool=inventory_tool,
        tool_stamp=inventory_stamp,
            cwd=execution_cwd,
        environment=execution_environment,
    )
    actions.append(poison_after)

    main_pre_manifest = proof_root / "runs" / "main-preapply-manifest.json"
    actions.append(
        run_auxiliary(
            proof_root=proof_root,
            run_id="inspect-main-preapply",
            argv=[
                str(python),
                *PYTHON_ISOLATION_FLAGS,
                str(backup_tool),
                "inspect",
                str(main_project),
                "--project-name",
                args.project_name,
                "--output",
                str(main_pre_manifest),
            ],
            cwd=execution_cwd,
            environment=execution_environment,
        )
    )
    apply, apply_tsv, _apply_ready = run_promotion(
        proof_root=proof_root,
        run_id="main-apply",
        headless=args.headless,
        project_root=main_project,
        project_name=args.project_name,
        tool=promotion_tool,
        tool_stamp=promotion_stamp,
        target_path=target_path,
        target_stamp=target_stamp,
        target_count=args.expected_count,
        semantic_target_sha256=semantic_sha,
        mode="apply",
        expected_sha256=args.expected_target_sha256,
            cwd=execution_cwd,
        environment=execution_environment,
    )
    actions.append(apply)
    readback, readback_tsv, _readback_ready = run_promotion(
        proof_root=proof_root,
        run_id="main-readback",
        headless=args.headless,
        project_root=main_project,
        project_name=args.project_name,
        tool=promotion_tool,
        tool_stamp=promotion_stamp,
        target_path=target_path,
        target_stamp=target_stamp,
        target_count=args.expected_count,
        semantic_target_sha256=semantic_sha,
        mode="readback",
        expected_sha256=args.expected_target_sha256,
            cwd=execution_cwd,
        environment=execution_environment,
    )
    actions.append(readback)
    after, after_functions, after_program = run_inventory(
        proof_root=proof_root,
        run_id="main-after",
        headless=args.headless,
        project_root=main_project,
        project_name=args.project_name,
        tool=inventory_tool,
        tool_stamp=inventory_stamp,
            cwd=execution_cwd,
        environment=execution_environment,
    )
    actions.append(after)
    diff_path = proof_root / "runs" / "main-after" / "inventory-diff.json"
    actions.append(
        run_auxiliary(
            proof_root=proof_root,
            run_id="diff-main-inventory",
            argv=[
                str(python),
                *PYTHON_ISOLATION_FLAGS,
                str(diff_tool),
                str(baseline_functions),
                str(after_functions),
                "--json",
                str(diff_path),
                "--sample-created",
                str(args.expected_count),
            ],
            cwd=execution_cwd,
            environment=execution_environment,
        )
    )
    main_post_manifest = proof_root / "runs" / "main-postverification-manifest.json"
    actions.append(
        run_auxiliary(
            proof_root=proof_root,
            run_id="inspect-main-postverification",
            argv=[
                str(python),
                *PYTHON_ISOLATION_FLAGS,
                str(backup_tool),
                "inspect",
                str(main_project),
                "--project-name",
                args.project_name,
                "--output",
                str(main_post_manifest),
            ],
            cwd=execution_cwd,
            environment=execution_environment,
        )
    )

    base_rows = copy_rows(main_project / "backup_manifest.json")
    if base_rows != copy_rows(poison_project / "backup_manifest.json"):
        raise ProofError("main and poison projects were not cloned from the same backup")
    if (
        manifest_rows(main_pre_manifest, expected_root=main_project) != base_rows
        or manifest_rows(poison_pre_manifest, expected_root=poison_project) != base_rows
    ):
        raise ProofError("immediate preapply projects differ from the verified backup clone")
    poison_post_rows = manifest_rows(
        poison_post_manifest, expected_root=poison_project
    )
    main_post_rows = manifest_rows(main_post_manifest, expected_root=main_project)
    poison_raw_changed = poison_post_rows != base_rows
    if sha256_file(poison_before_functions) != sha256_file(poison_after_functions):
        raise ProofError("poisoned-SHA control changed the function inventory")
    if sha256_file(poison_before_program) != sha256_file(poison_after_program):
        raise ProofError("poisoned-SHA control changed the program inventory")

    before_rows = inventory_map(baseline_functions)
    after_rows = inventory_map(after_functions)
    created = set(after_rows) - set(before_rows)
    destroyed = set(before_rows) - set(after_rows)
    target_set = set(addresses)
    if created != target_set or destroyed or len(created) != args.expected_count:
        raise ProofError("main inventory did not create exactly the target cohort")
    if any(before_rows[address] != after_rows[address] for address in set(before_rows) & set(after_rows)):
        raise ProofError("main promotion changed an existing function inventory row")
    apply_rows = inventory_map(apply_tsv)
    readback_rows = inventory_map(readback_tsv)
    if set(apply_rows) != target_set or set(readback_rows) != target_set:
        raise ProofError("apply/readback ledgers do not contain the exact target set")
    metadata_fields = (
        "name", "nameSource", "bodyBytes", "bodyMin", "bodyMax", "bodyRanges", "instrCount"
    )
    for address in addresses:
        if apply_rows[address].get("status") != "created":
            raise ProofError(f"apply status mismatch at {address}")
        if readback_rows[address].get("status") != "verified":
            raise ProofError(f"readback status mismatch at {address}")
        for field in metadata_fields:
            if (
                apply_rows[address].get(field) != readback_rows[address].get(field)
                or apply_rows[address].get(field) != after_rows[address].get(field)
            ):
                raise ProofError(f"apply/readback/inventory mismatch at {address} field {field}")
    dry_rows = read_tsv(dry_tsv)
    if (
        [row.get("address", "").lower() for row in dry_rows] != addresses
        or {row.get("status") for row in dry_rows} != {"would_create"}
    ):
        raise ProofError("dry run did not classify every target as would_create")

    before_program_values = program_map(baseline_program)
    after_program_values = program_map(after_program)
    if set(before_program_values) != set(after_program_values):
        raise ProofError("program inventory metric keys changed")
    for metric, before_value in before_program_values.items():
        after_value = after_program_values[metric]
        if metric == "functions":
            if int(after_value) - int(before_value) != args.expected_count:
                raise ProofError("program function count did not advance by the target count")
        elif before_value != after_value:
            raise ProofError(f"program metric changed: {metric}")
    diff = read_json(diff_path, "main inventory diff")
    diff_counts = diff.get("counts")
    if not isinstance(diff_counts, dict) or any(
        diff_counts.get(key) != expected
        for key, expected in {
            "before": len(before_rows),
            "after": len(after_rows),
            "created": args.expected_count,
            "destroyed": 0,
            "boundsChanged": 0,
            "namesChanged": 0,
            "signaturesChanged": 0,
            "instrCountChanged": 0,
        }.items()
    ):
        raise ProofError("inventory diff exceeds the authorized boundary creation")

    for role, source in sources.items():
        expected_sha = str(snapshots[role]["sourceSha256"])
        if sha256_file(source) != expected_sha:
            raise ProofError(f"{role} source changed while the proof was running")
    if main_post_rows == base_rows:
        raise ProofError("successful apply did not change scratch project storage")

    source_campaign_rows = tree_rows_from_disk(source_campaign_copy)
    source_snapshot_rows = tree_rows_from_disk(source_snapshot_copy)
    receipt = {
        "schema": SCHEMA,
        "finalizedAtUtc": utc_now(),
        "verdict": "SURVIVED",
        "claimBoundary": list(CLAIM_BOUNDARY),
        "execution": {
            "repoRoot": str(repo_root),
            "backupRoot": str(backup_root),
            "backupBaseFileSetSha256": BASE_PROJECT_FILE_SET_SHA256,
            "projectName": args.project_name,
            "python": external_stamp(python),
            "environment": execution_environment,
            "workingDirectory": str(execution_cwd.resolve()),
        },
        "program": {
            "name": PROGRAM_NAME,
            "md5": PROGRAM_MD5,
            "sha256": PROGRAM_SHA256,
            "imageBase": IMAGE_BASE,
            "language": LANGUAGE,
            "compilerSpec": COMPILER_SPEC,
        },
        "targets": {
            "list": target_stamp,
            "ready": target_ready_stamp,
            "count": args.expected_count,
            "semanticTargetSetSha256": semantic_sha,
            "namesAuthorized": False,
        },
        "targetSourceCampaign": {
            "root": "inputs/source-campaign",
            "ready": stamp(
                source_campaign_copy / "campaign.ready.json", proof_root
            ),
            "fileCount": len(source_campaign_rows),
            "fileSetSha256": canonical_rows_sha(source_campaign_rows),
            "snapshotRoot": snapshot_relative.as_posix(),
            "snapshotReady": stamp(
                source_snapshot_copy / "ledger.ready.json", proof_root
            ),
            "snapshotFileCount": len(source_snapshot_rows),
            "snapshotFileSetSha256": canonical_rows_sha(source_snapshot_rows),
            "replay": stamp(campaign_replay_path, proof_root),
        },
        "toolchain": {
            "snapshots": snapshots,
            "analyzeHeadless": external_stamp(args.headless),
            "ghidraApplicationProperties": external_stamp(application_properties),
            "hostJavaObserved": external_stamp(host_java),
            "windowsCommandProcessor": external_stamp(
                (WINDOWS_SYSTEM_ROOT / "System32" / "cmd.exe").resolve()
            ),
            "ghidraDistribution": ghidra_distribution,
            "jdkDistribution": jdk_distribution,
            "pythonDistribution": python_distribution,
            "javaHomeSave": stamp(expected_java_home_save_path(proof_root), proof_root),
        },
        "projects": {
            "mainScratch": {
                "root": str(main_project),
                "copyManifest": stamp(main_project / "backup_manifest.json", proof_root),
                "preapplyManifest": stamp(main_pre_manifest, proof_root),
                "postverificationManifest": stamp(main_post_manifest, proof_root),
                "baseFileSetSha256": canonical_rows_sha(base_rows),
                "finalFileSetSha256": canonical_rows_sha(main_post_rows),
            },
            "poisonControl": {
                "root": str(poison_project),
                "copyManifest": stamp(poison_project / "backup_manifest.json", proof_root),
                "preManifest": stamp(poison_pre_manifest, proof_root),
                "postManifest": stamp(poison_post_manifest, proof_root),
                "baseFileSetSha256": canonical_rows_sha(base_rows),
                "finalFileSetSha256": canonical_rows_sha(poison_post_rows),
                "rawProjectChanged": poison_raw_changed,
                "saveReported": poison["observations"]["saveReported"],
                "semanticInventoryStable": True,
            },
        },
        "runs": [action["receipt"] for action in actions],
        "checks": {
            "dryExactTargetSequence": True,
            "applyCreatedExactTargetSet": True,
            "readbackMatchesApplyMetadata": True,
            "instructionCountBefore": int(before_program_values["instructions"]),
            "instructionCountAfter": int(after_program_values["instructions"]),
            "functionsBefore": len(before_rows),
            "functionsAfter": len(after_rows),
            "existingFunctionFieldChanges": 0,
            "destroyedFunctions": 0,
            "poisonedShaRejectedWithoutOutputs": True,
            "poisonedShaSemanticInventoryStable": True,
            "poisonedShaRawProjectChanged": poison_raw_changed,
            "undefinedInstructionControl": "SURVIVED",
            "insideExistingFunctionControl": "SURVIVED",
        },
    }
    receipt["artifacts"] = artifact_set(proof_root)
    ready_path = proof_root / "proof.ready.json"
    write_json_new(ready_path, receipt)
    reproduced = read_json(ready_path, "scratch proof READY")
    if reproduced != receipt:
        raise ProofError("scratch proof READY did not reproduce after publication")
    return verify_ready_receipt(ready_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-ready", type=Path)
    parser.add_argument("--backup-root", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--target-ready", type=Path)
    parser.add_argument("--expected-target-sha256")
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--headless", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--project-name", default="BEA")
    parser.add_argument(
        "--promotion-tool",
        type=Path,
        default=Path(__file__).resolve().parent / "CreateFunctionsFromAddressList.java",
    )
    parser.add_argument(
        "--inventory-tool",
        type=Path,
        default=Path(__file__).resolve().parent / "ExportFullFunctionInventory.java",
    )
    parser.add_argument(
        "--backup-tool",
        type=Path,
        default=Path(__file__).resolve().parent / "ghidra_project_backup.py",
    )
    parser.add_argument(
        "--diff-tool",
        type=Path,
        default=Path(__file__).resolve().parent / "ghidra_inventory_diff.py",
    )
    parser.add_argument("--undefined-address", default="0x005d7fff")
    parser.add_argument("--inside-address", default="0x004f9a91")
    parser.add_argument("--containing-address", default="0x004f9a90")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.verify_ready is not None:
        try:
            receipt = verify_ready_receipt(args.verify_ready)
        except (OSError, ProofError, UnicodeError, ValueError) as exc:
            print(f"REFUSED: {exc}")
            return 1
        print(
            "GHIDRA_SCRATCH_PROOF_VERIFIED "
            f"count={receipt['targets']['count']} "
            f"before={receipt['checks']['functionsBefore']} "
            f"after={receipt['checks']['functionsAfter']} "
            f"readySha256={receipt['ready']['sha256']}"
        )
        return 0
    required = {
        "--backup-root": args.backup_root,
        "--targets": args.targets,
        "--expected-target-sha256": args.expected_target_sha256,
        "--expected-count": args.expected_count,
        "--headless": args.headless,
        "--out": args.out,
    }
    missing = [name for name, value in required.items() if value is None]
    if missing:
        print(f"REFUSED: run mode requires {', '.join(missing)}")
        return 1
    if re.fullmatch(r"[0-9a-f]{64}", args.expected_target_sha256) is None:
        print("REFUSED: expected target SHA-256 must be 64 lowercase hexadecimal characters")
        return 1
    if args.expected_count <= 0:
        print("REFUSED: expected count must be positive")
        return 1
    try:
        receipt = run(args)
    except (OSError, ProofError, UnicodeError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 1
    print(
        "GHIDRA_SCRATCH_PROOF_SURVIVED "
        f"count={receipt['targets']['count']} "
        f"before={receipt['checks']['functionsBefore']} "
        f"after={receipt['checks']['functionsAfter']} "
        f"readySha256={receipt['ready']['sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
