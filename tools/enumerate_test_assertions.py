#!/usr/bin/env python3
"""Enumerate what the UI test suite actually asserts on.

This exists because the suite's headline number was misleading. "415 static UI tests,
green" was being read as product coverage, while a large share of those assertions are
substring matches against source text read off disk - and ten of them match against the
source of OTHER TEST FILES, which cannot tell you anything about the product at all.

Three categories, and only the first is coverage:

  product-behaviour   asserts on values the product computes
  product-source-lint asserts that product source contains some text. Legitimate for an
                      architectural constraint that has no other expression - "this handler
                      must go through the guarded writer" - and worthless for anything a
                      real assertion could cover.
  harness-lint        asserts that a TEST file contains some text. Never product coverage.
                      Some of these encode real project rules (no global synthetic input in
                      a harness), so they are worth keeping - under a name that says what
                      they are.

Run:  py -3 tools/enumerate_test_assertions.py
      py -3 tools/enumerate_test_assertions.py --check     (non-zero if harness lint is
                                                            outside the declared suite)
      py -3 tools/enumerate_test_assertions.py --self-test

The --check mode is the guard: harness-lint tests must live in a class whose name ends
with HarnessLintTests, so nobody has to guess which side of the line a test is on.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys


TEST_ROOT = "OnslaughtCareerEditor.UiTests"
HARNESS_LINT_SUFFIX = "HarnessLintTests"

_METHOD = re.compile(r"public\s+(?:async\s+)?(?:void|Task)\s+(\w+)\s*\(")
_CLASS = re.compile(r"\bclass\s+(\w+)")
_FILE_REF = re.compile(r'"([A-Za-z0-9_.\\/-]+\.(?:cs|xaml|md|json|py|tsv|csv))"')
_CONTAINS = re.compile(r"Does\.(?:Contain|Not\.Contain)|Assert\.Contains|Assert\.DoesNotContain")


def repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for candidate in [here.parent.parent, *here.parents]:
        if (candidate / "package.json").is_file():
            return candidate
    raise SystemExit("Could not find the repository root.")


class Finding:
    __slots__ = ("file", "cls", "test", "reads_tests", "reads_product", "contains")

    def __init__(self, file: str, cls: str, test: str) -> None:
        self.file = file
        self.cls = cls
        self.test = test
        self.reads_tests: set[str] = set()
        self.reads_product: set[str] = set()
        self.contains = 0

    @property
    def category(self) -> str:
        if self.reads_tests:
            return "harness-lint"
        if self.reads_product:
            return "product-source-lint"
        return "product-behaviour"


def scan(root: pathlib.Path) -> tuple[list[Finding], collections.Counter]:
    findings: list[Finding] = []
    contains_by_file: collections.Counter = collections.Counter()

    test_dir = root / TEST_ROOT
    for path in sorted(test_dir.glob("*.cs")):
        text = path.read_text(encoding="utf-8", errors="replace")
        current_class = ""
        current: Finding | None = None

        for line in text.splitlines():
            class_match = _CLASS.search(line)
            if class_match:
                current_class = class_match.group(1)

            method_match = _METHOD.search(line)
            if method_match:
                current = Finding(path.name, current_class, method_match.group(1))
                findings.append(current)

            if _CONTAINS.search(line):
                contains_by_file[path.name] += 1
                if current is not None:
                    current.contains += 1

            if current is None:
                continue

            for ref in _FILE_REF.findall(line):
                leaf = ref.replace("\\", "/").rsplit("/", 1)[-1]
                if leaf.endswith("Tests.cs"):
                    current.reads_tests.add(leaf)
                elif leaf.endswith((".cs", ".xaml")):
                    current.reads_product.add(leaf)

    return findings, contains_by_file


def misplaced(findings: list[Finding]) -> list[Finding]:
    """Harness lint living outside a suite whose name declares it."""
    return [
        f
        for f in findings
        if f.category == "harness-lint" and not f.cls.endswith(HARNESS_LINT_SUFFIX)
    ]


def report(findings: list[Finding], contains_by_file: collections.Counter) -> None:
    buckets: collections.Counter = collections.Counter(f.category for f in findings)
    total = sum(buckets.values())

    print("=" * 78)
    print("WHAT THE UI TEST SUITE ASSERTS ON")
    print("=" * 78)
    for name in ("product-behaviour", "product-source-lint", "harness-lint"):
        count = buckets.get(name, 0)
        share = (count / total * 100) if total else 0
        print(f"  {count:5}  {share:5.1f}%  {name}")
    print(f"  {total:5}  100.0%  total test methods")

    harness = [f for f in findings if f.category == "harness-lint"]
    if harness:
        print()
        print("HARNESS LINT - asserts on a TEST file, never product coverage")
        for f in sorted(harness, key=lambda f: (f.file, f.test)):
            flag = "" if f.cls.endswith(HARNESS_LINT_SUFFIX) else "   << outside the declared suite"
            print(f"  {f.file}::{f.test}{flag}")
            print(f"      reads: {', '.join(sorted(f.reads_tests))}")

    print()
    print("SUBSTRING ASSERTIONS PER FILE")
    for name, count in contains_by_file.most_common():
        print(f"  {count:5}  {name}")
    print(f"  {sum(contains_by_file.values()):5}  total across {len(contains_by_file)} files")


def self_test() -> int:
    """The classifier's own rules, checked on synthetic input rather than on the repo."""
    import tempfile

    cases = [
        ("reads a test file", 'File.ReadAllText("WinUiFooSmokeTests.cs");', "harness-lint"),
        ("reads product source", 'ReadRepoFile("HomePage.xaml.cs");', "product-source-lint"),
        ("reads product markup", 'ReadRepoFile("SavesPage.xaml");', "product-source-lint"),
        ("asserts on a value", "Assert.That(Compute(), Is.EqualTo(3));", "product-behaviour"),
    ]

    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "package.json").write_text("{}", encoding="utf-8")
        test_dir = root / TEST_ROOT
        test_dir.mkdir(parents=True)

        for index, (label, body, expected) in enumerate(cases):
            (test_dir / f"Case{index}Tests.cs").write_text(
                f"class Case{index}Tests {{ public void T{index}() {{ {body} }} }}",
                encoding="utf-8",
            )

        findings, _ = scan(root)
        by_test = {f.test: f for f in findings}
        for index, (label, _body, expected) in enumerate(cases):
            actual = by_test[f"T{index}"].category
            ok = actual == expected
            failures += 0 if ok else 1
            print(f"  {'PASS' if ok else 'FAIL'}  {label}: {actual}")

    print("SELF-TEST PASS" if failures == 0 else f"SELF-TEST FAIL ({failures})")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if harness lint sits outside its declared suite.")
    parser.add_argument("--self-test", action="store_true", help="Check the classifier against synthetic input.")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    root = repo_root()
    findings, contains_by_file = scan(root)

    if args.check:
        stray = misplaced(findings)
        if stray:
            print("FAIL: harness lint outside a *" + HARNESS_LINT_SUFFIX + " suite:")
            for f in stray:
                print(f"  {f.file}::{f.cls}.{f.test}")
            print()
            print("These assert on the text of other TEST files. They are not product coverage,")
            print("and counting them as such is how a suite's headline number stops meaning")
            print("anything. Move them, or make them assert on the product.")
            return 1

        print("PASS: every harness-lint test lives in a suite that says so.")
        return 0

    report(findings, contains_by_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
