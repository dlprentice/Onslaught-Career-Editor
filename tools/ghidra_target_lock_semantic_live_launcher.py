#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Launch only exact-source, independently reviewed target-lock owner bytes."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.abc
import importlib.util
import io
import os
from pathlib import Path
import re
import subprocess
import sys
import types
from typing import Mapping, Sequence
import unittest


TOOLS = Path(__file__).resolve().parent
OWNER = TOOLS / "ghidra_target_lock_semantic_live_promotion.py"
TESTS = TOOLS / "ghidra_target_lock_semantic_live_promotion_tests.py"
REVIEWER_HOME = Path(r"C:\Users\david")
PYTHON = Path(r"C:\Users\david\AppData\Local\Python\pythoncore-3.14-64\python.exe")
PYTHON_DISTRIBUTION_MANIFEST = (
    TOOLS.parent
    / "local-lab/formal-global-init515-proof-20260803-v4/inputs/toolchain/python-files.tsv"
)
EXTERNAL_SHA256_ENV = "BEA_TARGET_LOCK_REVIEWED_LAUNCHER_SHA256"
PROOF_READY = (
    TOOLS.parent
    / "local-lab/ghidra-target-lock-semantic-proof-20260804-v2-r5/proof.ready.json"
)
PROOF_READY_SHA256 = "f7c4220bdf5dfa6040bad23b11d3253ddeecea47f86b6ee238a28a4280987968"

OWNER_SHA256 = "35ce980cf09cfa2f9af5f8d931705951a9dca50db6712069ed08fcd5f96c6911"
TESTS_SHA256 = "30c844ef27c694d2a44319d1812b2b998203716707a0bb658a87070745552188"
PYTHON_SHA256 = "fda7026477256845afab371e354c4d512896665f1761939cb5887d0a9dec257a"
PYTHON_DISTRIBUTION = (
    11_683, 533_160_307, "e43602c0684213f4fb9e1f1c8de2d38cef55345e9ab7a6b061a0e34b1b131d7e"
)
EXPECTED_TEST_COUNT = 67
CAPSTONE_PACKAGE = PYTHON.parent / "Lib/site-packages/capstone"
CAPSTONE_INIT = CAPSTONE_PACKAGE / "__init__.py"
CAPSTONE_X86 = CAPSTONE_PACKAGE / "x86.py"
CAPSTONE_DLL = CAPSTONE_PACKAGE / "lib/capstone.dll"
CAPSTONE_INIT_SHA256 = "94571d1314355e261aff0ddfc94985fe8761232ddff6874181fd21efa9fab47f"
CAPSTONE_X86_SHA256 = "08cbb0a02ff152bcf1fbd7c4f8850b3ade38c25b9f0a6a9b900a55ee75e87c67"
CAPSTONE_DLL_SHA256 = "76958e18380023a68fd1714fa2e01c594cc6db1955a07ad6937b66e66dc5d6c3"
FORBIDDEN_DEPENDENCY_ENVIRONMENT = ("LIBCAPSTONE_PATH",)
ACTIVE_EXACT_SOURCE_FINDER: object | None = None

EXACT_SOURCE_MODULES: dict[str, tuple[Path, str]] = {
    "ghidra_target_lock_semantic_live_promotion": (OWNER, OWNER_SHA256),
    "ghidra_global_init515_live_promotion": (
        TOOLS / "ghidra_global_init515_live_promotion.py",
        "a1adf103f4c18487553970c62a21f01ea5cfa49c8039b3f299042ff6fc9e8747",
    ),
    "ghidra_function_batch_proof": (
        TOOLS / "ghidra_function_batch_proof.py",
        "f76a3e74bd618ef824b0185ce7bebf7476387381e8ace991af72c38560741afa",
    ),
    "ghidra_function_envelope_proof": (
        TOOLS / "ghidra_function_envelope_proof.py",
        "e20d619c39dd0f2037523b4577860b6640ed76b0be058472834a587192b305e8",
    ),
    "ghidra_global_init_full520_proof": (
        TOOLS / "ghidra_global_init_full520_proof.py",
        "2fea029379aaf81df072907a87e142f03e4c1d261d19325933b18823b4fef972",
    ),
    "ghidra_project_backup": (
        TOOLS / "ghidra_project_backup.py",
        "36969a237eef29fea0daa52fe4a657127bdbbb5091523c9ca7cd92c69566b452",
    ),
    "ghidra_promotion_scratch_proof": (
        TOOLS / "ghidra_promotion_scratch_proof.py",
        "895405aea9da78f72901250c7edb4e042ec28fadf6fbf9409d83097f8dd228be",
    ),
    "ghidra_target_lock_semantic_proof": (
        TOOLS / "ghidra_target_lock_semantic_proof.py",
        "08bf49f38bfe89224197e28d31c8f7514d690b55f2cb2cdfa4f7fdbb3bc964dd",
    ),
    "re_crt_function_strata": (
        TOOLS / "re_crt_function_strata.py",
        "620d2e09b2d73273ed4815e6dd1d6c0b7c54a3f824aa1b93bd69520119802ab7",
    ),
    "re_rtti_vtables": (
        TOOLS / "re_rtti_vtables.py",
        "90071f2536e6f511d647b47fda7d323110374fd6c57b15e5360adaa0fd717d1d",
    ),
}


class LaunchError(ValueError):
    """The reviewed launcher, source graph, or test boundary differs."""


class FrozenImportPath(list[str]):
    """Read-only import roots; exact modules may harmlessly request TOOLS."""

    def __init__(self, values: Sequence[str], ignored_tools: Path) -> None:
        super().__init__(values)
        self._ignored_tools = ignored_tools.resolve()

    def _is_ignored_tools(self, value: object) -> bool:
        try:
            return Path(os.fspath(value)).resolve() == self._ignored_tools
        except (TypeError, ValueError, OSError):
            return False

    def _reject(self) -> None:
        raise LaunchError("reviewed import path is immutable")

    def insert(self, index: int, value: str) -> None:
        (index,)
        if self._is_ignored_tools(value):
            return
        self._reject()

    def append(self, value: str) -> None:
        if self._is_ignored_tools(value):
            return
        self._reject()

    def extend(self, values: Sequence[str]) -> None:
        if all(self._is_ignored_tools(value) for value in values):
            return
        self._reject()

    def __setitem__(self, key: object, value: object) -> None:
        (key, value)
        self._reject()

    def __delitem__(self, key: object) -> None:
        (key,)
        self._reject()

    def __iadd__(self, values: Sequence[str]) -> "FrozenImportPath":
        self.extend(values)
        return self

    def __imul__(self, value: int) -> "FrozenImportPath":
        (value,)
        self._reject()
        return self

    def clear(self) -> None:
        self._reject()

    def pop(self, index: int = -1) -> str:
        (index,)
        self._reject()
        raise AssertionError("unreachable")

    def remove(self, value: str) -> None:
        (value,)
        self._reject()

    def reverse(self) -> None:
        self._reject()

    def sort(self, *args: object, **kwargs: object) -> None:
        (args, kwargs)
        self._reject()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_file(path: Path, digest: str, label: str) -> Path:
    if not path.is_file() or path.is_symlink() or path.stat().st_nlink != 1:
        raise LaunchError(f"{label} is absent or unsafe: {path}")
    if sha256_file(path) != digest:
        raise LaunchError(f"{label} SHA-256 differs: {path}")
    return path.resolve()


def is_reparse_point(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction() or bool(attributes & 0x400)


def require_reviewer_home() -> Path:
    home = REVIEWER_HOME.resolve()
    if home != REVIEWER_HOME or not home.is_dir() or is_reparse_point(home):
        raise LaunchError(f"reviewer home is absent or unsafe: {REVIEWER_HOME}")
    for relative in (Path(".grok/bin/grok.exe"), Path(".local/bin/claude.exe")):
        current = home
        for part in relative.parts[:-1]:
            current /= part
            if not current.is_dir() or is_reparse_point(current):
                raise LaunchError(f"reviewer executable parent is absent or unsafe: {current}")
        executable = current / relative.name
        if (
            not executable.is_file()
            or is_reparse_point(executable)
            or executable.stat().st_nlink != 1
        ):
            raise LaunchError(f"reviewer executable is absent or unsafe: {executable}")
    return home


def canonical_distribution_bytes(rows: list[tuple[str, int, str]]) -> bytes:
    return b"".join(
        f"{digest}\t{size}\t{relative}\n".encode("utf-8")
        for relative, size, digest in sorted(rows)
    )


def parse_distribution_manifest(path: Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    prior = ""
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split("\t")
        if len(fields) != 3 or re.fullmatch(r"[0-9a-f]{64}", fields[0]) is None:
            raise LaunchError(f"malformed Python distribution manifest line {number}")
        try:
            size = int(fields[1])
        except ValueError as exc:
            raise LaunchError(
                f"malformed Python distribution manifest size at line {number}"
            ) from exc
        relative = fields[2]
        if size < 0 or not relative or relative <= prior or "\\" in relative:
            raise LaunchError(f"noncanonical Python distribution row at line {number}")
        rows.append((relative, size, fields[0]))
        prior = relative
    if sha256_bytes(canonical_distribution_bytes(rows)) != sha256_file(path):
        raise LaunchError("Python distribution manifest is not self-canonical")
    return rows


def distribution_tree_rows(root: Path) -> list[tuple[str, int, str]]:
    if not root.is_dir() or is_reparse_point(root):
        raise LaunchError(f"Python distribution root is absent or unsafe: {root}")
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if is_reparse_point(path):
            raise LaunchError(f"Python distribution contains a reparse point: {path}")
        if not path.is_file():
            continue
        rows.append(
            (path.relative_to(root).as_posix(), path.stat().st_size, sha256_file(path))
        )
    return rows


def verify_python_distribution() -> dict[str, object]:
    manifest = exact_file(
        PYTHON_DISTRIBUTION_MANIFEST,
        PYTHON_DISTRIBUTION[2],
        "reviewed Python distribution manifest",
    )
    expected = parse_distribution_manifest(manifest)
    count, total_bytes, digest = PYTHON_DISTRIBUTION
    if (
        len(expected) != count
        or sum(row[1] for row in expected) != total_bytes
        or sha256_bytes(canonical_distribution_bytes(expected)) != digest
    ):
        raise LaunchError("reviewed Python distribution manifest identity differs")
    if distribution_tree_rows(PYTHON.parent) != expected:
        raise LaunchError("running Python distribution differs from its frozen manifest")
    return {
        "root": str(PYTHON.parent.resolve()),
        "fileCount": count,
        "totalBytes": total_bytes,
        "fileSetSha256": digest,
        "manifest": {
            "path": str(manifest),
            "bytes": manifest.stat().st_size,
            "sha256": digest,
        },
    }


def expected_no_site_import_path() -> tuple[str, ...]:
    root = PYTHON.parent.resolve()
    return (
        str(root / "python314.zip"),
        str(root / "DLLs"),
        str(root / "Lib"),
        str(root),
    )


def reviewed_import_path() -> tuple[str, ...]:
    return (*expected_no_site_import_path(), str((PYTHON.parent / "Lib/site-packages").resolve()))


def install_reviewed_import_path() -> dict[str, object]:
    expected = reviewed_import_path()
    if isinstance(sys.path, FrozenImportPath):
        if tuple(sys.path) != expected:
            raise LaunchError("reviewed import path drifted")
        return {"roots": list(expected), "toolsSearchable": False}
    if tuple(sys.path) != expected_no_site_import_path():
        raise LaunchError("Python no-site import roots differ")
    site_packages = Path(expected[-1])
    if (
        not site_packages.is_dir()
        or is_reparse_point(site_packages)
        or site_packages.stat().st_nlink != 1
    ):
        raise LaunchError("reviewed site-packages root is absent or unsafe")
    sys.path = FrozenImportPath(expected, TOOLS)
    return {"roots": list(expected), "toolsSearchable": False}


def require_reviewed_import_path() -> None:
    if not isinstance(sys.path, FrozenImportPath) or tuple(sys.path) != reviewed_import_path():
        raise LaunchError("reviewed import path is absent or drifted")
    if any(Path(entry).resolve() == TOOLS.resolve() for entry in sys.path):
        raise LaunchError("repository tools directory became import-searchable")
    if (
        ACTIVE_EXACT_SOURCE_FINDER is not None
        and (not sys.meta_path or sys.meta_path[0] is not ACTIVE_EXACT_SOURCE_FINDER)
    ):
        raise LaunchError("exact-source finder is absent or no longer first")


def require_dependency_environment() -> None:
    present = sorted(name for name in FORBIDDEN_DEPENDENCY_ENVIRONMENT if name in os.environ)
    if present:
        raise LaunchError(f"forbidden dependency environment is present: {present}")


def loaded_windows_module_path(handle: int) -> Path:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32]
    kernel32.GetModuleFileNameW.restype = ctypes.c_uint32
    buffer = ctypes.create_unicode_buffer(32768)
    length = kernel32.GetModuleFileNameW(ctypes.c_void_p(handle), buffer, len(buffer))
    if length == 0 or length >= len(buffer):
        raise LaunchError(
            f"cannot resolve loaded dependency module; Win32 error {ctypes.get_last_error()}"
        )
    return Path(buffer.value).resolve()


_CAPSTONE_BINDING: dict[str, object] | None = None


def require_capstone_binding() -> dict[str, object]:
    global _CAPSTONE_BINDING
    require_reviewed_import_path()
    require_dependency_environment()
    init = exact_file(CAPSTONE_INIT, CAPSTONE_INIT_SHA256, "reviewed Capstone package")
    x86 = exact_file(CAPSTONE_X86, CAPSTONE_X86_SHA256, "reviewed Capstone x86 module")
    native = exact_file(CAPSTONE_DLL, CAPSTONE_DLL_SHA256, "reviewed Capstone native library")
    if _CAPSTONE_BINDING is None and any(
        name == "capstone" or name.startswith("capstone.") for name in sys.modules
    ):
        raise LaunchError("Capstone was preloaded before its reviewed dependency gate")
    capstone = importlib.import_module("capstone")
    capstone_x86 = importlib.import_module("capstone.x86")
    loaded_native = loaded_windows_module_path(int(capstone._cs._handle))
    if (
        Path(capstone.__file__).resolve() != init
        or Path(capstone_x86.__file__).resolve() != x86
        or Path(str(capstone._cs._name)).resolve() != native
        or loaded_native != native
        or tuple(Path(value).resolve() for value in capstone.__path__) != (CAPSTONE_PACKAGE.resolve(),)
    ):
        raise LaunchError("loaded Capstone Python or native identity differs")
    binding = {
        "package": {"path": str(init), "bytes": init.stat().st_size, "sha256": CAPSTONE_INIT_SHA256},
        "x86": {"path": str(x86), "bytes": x86.stat().st_size, "sha256": CAPSTONE_X86_SHA256},
        "native": {
            "path": str(native),
            "bytes": native.stat().st_size,
            "sha256": CAPSTONE_DLL_SHA256,
        },
    }
    if _CAPSTONE_BINDING is not None and binding != _CAPSTONE_BINDING:
        raise LaunchError("reviewed Capstone binding drifted")
    _CAPSTONE_BINDING = binding
    require_reviewed_import_path()
    return dict(binding)


def read_exact_source(path: Path, digest: str, label: str) -> bytes:
    checked = exact_file(path, digest, label)
    with checked.open("rb") as stream:
        before = os.fstat(stream.fileno())
        content = stream.read()
        after = os.fstat(stream.fileno())
    current = checked.stat()
    if not os.path.samestat(before, after) or not os.path.samestat(after, current):
        raise LaunchError(f"{label} identity changed while held open: {checked}")
    if len(content) != after.st_size or sha256_bytes(content) != digest:
        raise LaunchError(f"{label} bytes changed while held open: {checked}")
    return content


class ExactSourceLoader(importlib.abc.Loader):
    def __init__(self, name: str, path: Path, digest: str) -> None:
        self.name = name
        self.path = path
        self.digest = digest

    def create_module(self, spec: object) -> None:
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        require_reviewed_import_path()
        content = read_exact_source(self.path, self.digest, f"exact-source module {self.name}")
        module.__file__ = str(self.path.resolve())
        module.__exact_source_path__ = str(self.path.resolve())
        module.__exact_source_sha256__ = self.digest
        code = compile(content, str(self.path.resolve()), "exec", dont_inherit=True)
        exec(code, module.__dict__)
        require_reviewed_import_path()


class ExactSourceFinder(importlib.abc.MetaPathFinder):
    def __init__(self, modules: Mapping[str, tuple[Path, str]]) -> None:
        self.modules = dict(modules)

    def find_spec(
        self,
        fullname: str,
        path: object = None,
        target: object = None,
    ) -> object:
        entry = self.modules.get(fullname)
        if entry is None:
            return None
        source, digest = entry
        loader = ExactSourceLoader(fullname, source, digest)
        return importlib.util.spec_from_loader(fullname, loader, origin=str(source.resolve()))


def require_runtime_boundary() -> tuple[str, dict[str, object]]:
    if not sys.flags.isolated or not sys.dont_write_bytecode or not sys.flags.no_site:
        raise LaunchError("launcher requires Python -I -B -S")
    reviewed = os.environ.get(EXTERNAL_SHA256_ENV, "")
    if re.fullmatch(r"[0-9a-f]{64}", reviewed) is None:
        raise LaunchError("external reviewed-launcher SHA-256 is absent or malformed")
    exact_file(Path(__file__).resolve(), reviewed, "externally reviewed live launcher")
    exact_file(PYTHON, PYTHON_SHA256, "reviewed Python runtime")
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise LaunchError("running Python path differs from reviewed runtime")
    distribution = verify_python_distribution()
    install_reviewed_import_path()
    require_capstone_binding()
    return reviewed, distribution


def reject_preloaded_exact_modules(modules: Mapping[str, tuple[Path, str]]) -> None:
    loaded = sorted(name for name in modules if name in sys.modules)
    if loaded:
        raise LaunchError(f"exact-source module was preloaded or shadowed: {loaded}")


def load_reviewed_owner() -> object:
    global ACTIVE_EXACT_SOURCE_FINDER
    exact_file(OWNER, OWNER_SHA256, "reviewed live owner")
    exact_file(TESTS, TESTS_SHA256, "reviewed live-owner tests")
    require_capstone_binding()
    reject_preloaded_exact_modules(EXACT_SOURCE_MODULES)
    if ACTIVE_EXACT_SOURCE_FINDER is not None:
        raise LaunchError("exact-source finder was already installed")
    finder = ExactSourceFinder(EXACT_SOURCE_MODULES)
    ACTIVE_EXACT_SOURCE_FINDER = finder
    sys.meta_path.insert(0, finder)
    require_reviewed_import_path()
    owner = importlib.import_module("ghidra_target_lock_semantic_live_promotion")
    if getattr(owner, "__exact_source_sha256__", None) != OWNER_SHA256:
        raise LaunchError("live owner was not executed from reviewed source bytes")
    require_reviewed_import_path()
    require_capstone_binding()
    return owner


def run_reviewed_tests_in_process() -> int:
    owner = load_reviewed_owner()
    sys.modules["ghidra_target_lock_semantic_live_launcher"] = sys.modules[__name__]
    content = read_exact_source(TESTS, TESTS_SHA256, "reviewed live-owner tests")
    module = types.ModuleType("ghidra_target_lock_semantic_live_promotion_reviewed_tests")
    module.__file__ = str(TESTS.resolve())
    module.__exact_source_sha256__ = TESTS_SHA256
    exec(compile(content, str(TESTS.resolve()), "exec", dont_inherit=True), module.__dict__)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    if not result.wasSuccessful() or result.testsRun != EXPECTED_TEST_COUNT:
        print(stream.getvalue(), file=sys.stderr, end="")
        print(
            f"REFUSED: reviewed test result differs: ran={result.testsRun} "
            f"expected={EXPECTED_TEST_COUNT}",
            file=sys.stderr,
        )
        return 3
    print(f"REVIEWED_OWNER_TESTS_OK count={result.testsRun}")
    return 0


def run_reviewed_proof_verifier_in_process() -> int:
    owner = load_reviewed_owner()
    proof = owner.formal
    expected_proof_path, expected_proof_sha256 = EXACT_SOURCE_MODULES[
        "ghidra_target_lock_semantic_proof"
    ]
    if (
        Path(getattr(proof, "__exact_source_path__", "")).resolve()
        != expected_proof_path.resolve()
        or getattr(proof, "__exact_source_sha256__", None) != expected_proof_sha256
    ):
        raise LaunchError("proof verifier was not executed from reviewed source bytes")
    if Path(owner.PROOF_READY).resolve() != PROOF_READY.resolve():
        raise LaunchError("reviewed owner proof READY path differs")
    exact_file(PROOF_READY, PROOF_READY_SHA256, "proof-verifier READY input")
    prior_argv = sys.argv
    reviewer_home = require_reviewer_home()
    prior_userprofile = os.environ.get("USERPROFILE")
    try:
        # The contained child deliberately has an isolated USERPROFILE.  The
        # frozen proof verifier must nevertheless re-hash the exact reviewer
        # executables named by its already-recorded review receipts.  Restore
        # only USERPROFILE while the exact reviewed proof module runs; every
        # other child-environment boundary remains isolated and unchanged.
        os.environ["USERPROFILE"] = str(reviewer_home)
        sys.argv = [str(expected_proof_path), "verify-ready", str(PROOF_READY)]
        return int(proof.main())
    finally:
        if prior_userprofile is None:
            os.environ.pop("USERPROFILE", None)
        else:
            os.environ["USERPROFILE"] = prior_userprofile
        sys.argv = prior_argv


def run_reviewed_tests_subprocess(reviewed_launcher_sha256: str) -> dict[str, object]:
    environment = dict(os.environ)
    environment[EXTERNAL_SHA256_ENV] = reviewed_launcher_sha256
    process = subprocess.run(
        [
            str(PYTHON), "-I", "-B", "-S",
            str(Path(__file__).resolve()), "_reviewed-tests",
        ],
        cwd=str(TOOLS),
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    expected = f"REVIEWED_OWNER_TESTS_OK count={EXPECTED_TEST_COUNT}"
    if process.returncode != 0 or process.stdout.strip() != expected or process.stderr:
        raise LaunchError(
            "reviewed live-owner tests failed: "
            f"exit={process.returncode} stdout={process.stdout!r} stderr={process.stderr!r}"
        )
    return {"count": EXPECTED_TEST_COUNT, "status": "PASSED"}


def install_reviewed_owner(
    reviewed_launcher_sha256: str,
    reviewed_tests: Mapping[str, object],
    python_distribution: Mapping[str, object],
) -> object:
    owner = load_reviewed_owner()
    launcher = Path(__file__).resolve()
    owner.install_launch_gate({
        "schema": owner.LAUNCH_GATE_SCHEMA,
        "launcher": {
            "path": str(launcher),
            "bytes": launcher.stat().st_size,
            "sha256": reviewed_launcher_sha256,
        },
        "externalReviewedLauncherSha256": reviewed_launcher_sha256,
        "reviewedOwnerSha256": OWNER_SHA256,
        "reviewedTestsSha256": TESTS_SHA256,
        "reviewedTests": dict(reviewed_tests),
        "launcherRuntime": {"pythonDistribution": dict(python_distribution)},
    })
    return owner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "prepare", "promote", "recover-status", "verify",
            "_reviewed-tests", "_proof-verify",
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        reviewed_launcher_sha256, python_distribution = require_runtime_boundary()
        if args.command == "_reviewed-tests":
            return run_reviewed_tests_in_process()
        if args.command == "_proof-verify":
            return run_reviewed_proof_verifier_in_process()
        reviewed_tests = run_reviewed_tests_subprocess(reviewed_launcher_sha256)
        owner = install_reviewed_owner(
            reviewed_launcher_sha256, reviewed_tests, python_distribution
        )
    except (LaunchError, OSError, subprocess.SubprocessError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    return int(owner.main([args.command]))


if __name__ == "__main__":
    raise SystemExit(main())
