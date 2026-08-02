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

# A class-scope helper that resolves to a file, e.g.
#
#     private static string PageXamlPath => Path.Combine(
#         TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml");
#     private static string PageXaml => File.ReadAllText(PageXamlPath);
#
# These sit ABOVE the first test method, which is exactly why the first version of this
# tool could not see them: it attributed a file reference to the most recent method and
# skipped anything appearing before there was one. Hoisting a path into a helper is
# ordinary C#, so whole suites that read product source were counted as product-behaviour.
# The 2026-08-01 measurement reported 7.2% source-reading on that basis and was wrong.
#
# Two passes now: learn the class's helpers first, then attribute a helper's files to any
# test that names it.
# Properties, fields AND methods. A test that calls TrainerElement("...") to pull a node
# out of CheatsPage.xaml is reading product source just as surely as one that touches a
# PageXaml property, and the first version of this pattern only caught the property form
# because it required =>, = or { after the name. The trailing ( is what admits methods.
_HELPER = re.compile(
    r"(?:private|protected|internal|public)\s+static\s+[\w<>?\[\], ]+?\s+(\w+)\s*(?:=>|=|\{|\()")


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


def _helper_body(lines: list[str], name: str) -> str:
    """
    The lines belonging to a class-scope helper, from its declaration to the next
    declaration or test method. Enough to see which other helpers it is built from.
    """
    body: list[str] = []
    inside = False
    for line in lines:
        declaration = _HELPER.search(line)
        if declaration and not _METHOD.search(line):
            if inside:
                break
            inside = declaration.group(1) == name
            if inside:
                body.append(line)
            continue

        if inside:
            if _METHOD.search(line):
                break
            body.append(line)

    return "\n".join(body)


def scan(root: pathlib.Path) -> tuple[list[Finding], collections.Counter]:
    findings: list[Finding] = []
    contains_by_file: collections.Counter = collections.Counter()

    test_dir = root / TEST_ROOT
    for path in sorted(test_dir.glob("*.cs")):
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()

        # Pass one: what the class's own helpers read. A helper's files count for any test
        # that names it, because reading a file through a property is still reading a file.
        helper_files: dict[str, tuple[set[str], set[str]]] = {}
        helper_owner: str | None = None
        for line in lines:
            if _METHOD.search(line):
                helper_owner = None

            helper_match = _HELPER.search(line)
            if helper_match and not _METHOD.search(line):
                helper_owner = helper_match.group(1)
                helper_files.setdefault(helper_owner, (set(), set()))

            if helper_owner is None:
                continue

            tests_read, product_read = helper_files[helper_owner]
            for ref in _FILE_REF.findall(line):
                leaf = ref.replace("\\", "/").rsplit("/", 1)[-1]
                if leaf.endswith("Tests.cs"):
                    tests_read.add(leaf)
                elif leaf.endswith((".cs", ".xaml")):
                    product_read.add(leaf)

        # A helper built from another helper inherits what that one reads: PageXaml reads
        # PageXamlPath, and only the latter names the file. Repeat until nothing new
        # arrives, so a chain of any depth resolves rather than only one link of it.
        changed = True
        while changed:
            changed = False
            for name, (tests_read, product_read) in helper_files.items():
                body = _helper_body(lines, name)
                for other, (other_tests, other_product) in helper_files.items():
                    if other == name or not re.search(rf"\b{re.escape(other)}\b", body):
                        continue
                    if not other_tests <= tests_read or not other_product <= product_read:
                        tests_read |= other_tests
                        product_read |= other_product
                        changed = True

        current_class = ""
        current: Finding | None = None

        for line in lines:
            class_match = _CLASS.search(line)
            if class_match:
                current_class = class_match.group(1)

            method_match = _METHOD.search(line)
            if method_match:
                current = Finding(path.name, current_class, method_match.group(1))
                findings.append(current)

            if current is not None:
                for helper, (tests_read, product_read) in helper_files.items():
                    if re.search(rf"\b{re.escape(helper)}\b", line):
                        current.reads_tests |= tests_read
                        current.reads_product |= product_read

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

    # The shapes that made the 2026-08-01 measurement wrong. Each hoists the file reference
    # out of the test body, which is ordinary C# and was invisible to the first classifier -
    # so suites that read product source all day counted as product-behaviour. The last case
    # is the one that keeps the fix honest: a class CAN have a helper without every test in
    # it inheriting that helper's files.
    hoisted = [
        (
            "path hoisted into a static property",
            [
                '    private static string PagePath => Path.Combine(Root, "CheatsPage.xaml");',
                "    private static string Page => File.ReadAllText(PagePath);",
                '    public void T4() { Assert.That(Page, Does.Contain("x")); }',
            ],
            {"T4": "product-source-lint"},
        ),
        (
            "path reached through a static helper method",
            [
                '    private static XElement Element(string id) => Load("MediaPage.xaml").Find(id);',
                '    public void T5() { Assert.That(Element("a"), Is.Not.Null); }',
            ],
            {"T5": "product-source-lint"},
        ),
        (
            "a test that never names the helper stays behaviour",
            [
                '    private static string PagePath => Path.Combine(Root, "AboutPage.xaml");',
                "    public void T6() { Assert.That(PagePath, Is.Not.Null); }",
                "    public void T7() { Assert.That(Compute(), Is.EqualTo(3)); }",
            ],
            {"T6": "product-source-lint", "T7": "product-behaviour"},
        ),
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

        for index, (label, body_lines, _expected) in enumerate(hoisted):
            source = [f"class Hoisted{index}Tests", "{", *body_lines, "}", ""]
            (test_dir / f"Hoisted{index}Tests.cs").write_text(
                "\n".join(source),
                encoding="utf-8",
            )

        findings, _ = scan(root)
        by_test = {f.test: f for f in findings}
        for index, (label, _body, expected) in enumerate(cases):
            actual = by_test[f"T{index}"].category
            ok = actual == expected
            failures += 0 if ok else 1
            print(f"  {'PASS' if ok else 'FAIL'}  {label}: {actual}")

        for label, _body_lines, expectations in hoisted:
            for test_name, expected in expectations.items():
                actual = by_test[test_name].category if test_name in by_test else "MISSING"
                ok = actual == expected
                failures += 0 if ok else 1
                print(f"  {'PASS' if ok else 'FAIL'}  {label} ({test_name}): {actual}")

    print("SELF-TEST PASS" if failures == 0 else f"SELF-TEST FAIL ({failures})")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if harness lint sits outside its declared suite.")
    parser.add_argument("--self-test", action="store_true", help="Check the classifier against synthetic input.")
    parser.add_argument("--by-class", action="store_true", help="Break the categories down per suite.")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    root = repo_root()
    findings, contains_by_file = scan(root)

    if args.by_class:
        by_class: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        for finding in findings:
            by_class[finding.cls][finding.category] += 1

        print(f"{'suite':52} {'behaviour':>10} {'src-lint':>9} {'harness':>8}")
        print("-" * 82)
        for name in sorted(by_class, key=lambda n: -sum(by_class[n].values())):
            counts = by_class[name]
            print(
                f"{name[:52]:52} {counts['product-behaviour']:>10} "
                f"{counts['product-source-lint']:>9} {counts['harness-lint']:>8}"
            )
        return 0

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
