#!/usr/bin/env python3
"""Measure advisory WinUI page hardening metrics.

The metrics are locators for agentic UI hardening work. They are not a
product-quality score and not a release gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "OnslaughtCareerEditor.WinUI"
PAGES_ROOT = APP_ROOT / "Pages"
UITESTS_ROOT = ROOT / "OnslaughtCareerEditor.UiTests"
PLAN = ROOT / "roadmap" / "winui-agentic-ui-hardening-plan.md"
PACKAGE_JSON = ROOT / "package.json"
SNAPSHOT_TEST = UITESTS_ROOT / "WinUiAgenticSnapshotSmokeTests.cs"
DEFAULT_REPORT_DIR = ROOT / "subagents" / "winui-agentic-ui-hardening-metrics" / "current"

SCHEMA = "winui-agentic-ui-hardening-metrics.v1"

HANDLER_METHOD_RE = re.compile(
    r"\b(?:private|protected|public|internal)\s+"
    r"(?:async\s+)?(?:void|Task)\s+"
    r"[A-Za-z_]\w*_(?:Click|Tapped|SelectionChanged|TextChanged|Loaded|Checked|Unchecked|"
    r"ValueChanged|ItemClick|DoubleTapped|PointerPressed|PointerReleased|KeyDown|KeyUp|"
    r"GotFocus|LostFocus)\s*\("
)
ASYNC_VOID_RE = re.compile(r"\basync\s+void\b")
DIRECT_UI_WRITE_RE = re.compile(
    r"\b[A-Za-z_]\w*\.(?:Text|Content|ItemsSource|Visibility|IsEnabled|IsChecked|"
    r"SelectedIndex|SelectedItem|Header|Source)\s*="
)
XAML_EVENT_RE = re.compile(
    r"\b(?:Click|Tapped|SelectionChanged|TextChanged|Loaded|Checked|Unchecked|ValueChanged|"
    r"ItemClick|DoubleTapped|PointerPressed|PointerReleased|KeyDown|KeyUp|GotFocus|LostFocus)="
)
AUTOMATION_ID_RE = re.compile(r"AutomationProperties\.AutomationId\s*=")


@dataclass(frozen=True)
class PageMetrics:
    page: str
    xaml: str
    codeBehindFiles: list[str]
    logicalCodeBehindLines: int
    routedHandlerMethods: int
    asyncVoidHandlers: int
    directUiWrites: int
    xamlEventAttributes: int
    automationIds: int
    hasViewModel: bool
    advisoryScore: int


def relative(path: Path, root: Path = ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def logical_lines(text: str) -> int:
    count = 0
    in_block = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if in_block:
            if "*/" in line:
                in_block = False
            continue
        if line.startswith("/*"):
            if "*/" not in line:
                in_block = True
            continue
        if line.startswith("//") or line.startswith("*"):
            continue
        count += 1
    return count


def page_code_files(page_xaml: Path) -> list[Path]:
    page_name = page_xaml.stem
    candidates = [page_xaml.with_suffix(".xaml.cs")]
    candidates.extend(sorted(page_xaml.parent.glob(f"{page_name}.*.cs")))
    files: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        if not path.is_file() or path in seen:
            continue
        seen.add(path)
        files.append(path)
    return files


def has_view_model(app_root: Path, page_name: str) -> bool:
    view_model_name = f"{page_name}ViewModel.cs"
    return any(path.name == view_model_name for path in app_root.rglob("*.cs"))


def measure_pages(root: Path = ROOT) -> list[PageMetrics]:
    app_root = root / "OnslaughtCareerEditor.WinUI"
    pages_root = app_root / "Pages"
    pages: list[PageMetrics] = []
    for page_xaml in sorted(pages_root.glob("*Page.xaml")):
        page_name = page_xaml.stem
        xaml_text = read_text(page_xaml)
        code_files = page_code_files(page_xaml)
        code_texts = [read_text(path) for path in code_files]
        logical_line_count = sum(logical_lines(text) for text in code_texts)
        handler_count = sum(len(HANDLER_METHOD_RE.findall(text)) for text in code_texts)
        async_void_count = sum(len(ASYNC_VOID_RE.findall(text)) for text in code_texts)
        direct_ui_write_count = sum(len(DIRECT_UI_WRITE_RE.findall(text)) for text in code_texts)
        xaml_event_count = len(XAML_EVENT_RE.findall(xaml_text))
        automation_id_count = len(AUTOMATION_ID_RE.findall(xaml_text))
        view_model = has_view_model(app_root, page_name)
        score = (
            logical_line_count
            + direct_ui_write_count * 3
            + handler_count * 5
            + async_void_count * 12
            + xaml_event_count * 2
        )
        pages.append(
            PageMetrics(
                page=page_name,
                xaml=relative(page_xaml, root),
                codeBehindFiles=[relative(path, root) for path in code_files],
                logicalCodeBehindLines=logical_line_count,
                routedHandlerMethods=handler_count,
                asyncVoidHandlers=async_void_count,
                directUiWrites=direct_ui_write_count,
                xamlEventAttributes=xaml_event_count,
                automationIds=automation_id_count,
                hasViewModel=view_model,
                advisoryScore=score,
            )
        )
    return pages


def build_report(root: Path = ROOT) -> dict[str, object]:
    pages = measure_pages(root)
    totals = {
        "winuiPagesMeasured": len(pages),
        "logicalCodeBehindLines": sum(page.logicalCodeBehindLines for page in pages),
        "routedHandlerMethods": sum(page.routedHandlerMethods for page in pages),
        "asyncVoidHandlers": sum(page.asyncVoidHandlers for page in pages),
        "directUiWrites": sum(page.directUiWrites for page in pages),
        "xamlEventAttributes": sum(page.xamlEventAttributes for page in pages),
        "automationIds": sum(page.automationIds for page in pages),
        "pagesWithViewModelFiles": sum(1 for page in pages if page.hasViewModel),
    }
    top_candidates = sorted(pages, key=lambda page: page.advisoryScore, reverse=True)[:5]
    return {
        "schema": SCHEMA,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "totals": totals,
        "pages": [asdict(page) for page in pages],
        "topAdvisoryRefactorCandidates": [asdict(page) for page in top_candidates],
        "interpretation": [
            "Advisory source metrics only; this is not a product-quality score.",
            "Counts locate code-behind-heavy WinUI pages for bounded ViewModel and page-decomposition work.",
            "Future improvements should keep automation IDs and visible behavior stable.",
        ],
    }


def check_repo(report: dict[str, object]) -> list[str]:
    failures: list[str] = []
    totals = report["totals"]
    if totals["winuiPagesMeasured"] < 5:
        failures.append("expected at least five WinUI pages to be measured")
    if totals["automationIds"] <= 0:
        failures.append("expected WinUI pages to expose automation IDs")
    if not PLAN.is_file():
        failures.append(f"missing plan: {relative(PLAN)}")
    else:
        plan_text = read_text(PLAN)
        for token in (
            "npm run test:winui-agentic-ui-hardening-metrics",
            "npm run report:winui-agentic-ui-hardening-metrics",
            "subagents/winui-agentic-ui-hardening-metrics/current/metrics.json",
        ):
            if token not in plan_text:
                failures.append(f"plan missing token: {token}")
    if not SNAPSHOT_TEST.is_file():
        failures.append(f"missing snapshot test: {relative(SNAPSHOT_TEST)}")
    if not PACKAGE_JSON.is_file():
        failures.append(f"missing package manifest: {relative(PACKAGE_JSON)}")
    else:
        package = json.loads(read_text(PACKAGE_JSON))
        scripts = package.get("scripts", {})
        for script in (
            "test:winui-agentic-ui-hardening-metrics",
            "report:winui-agentic-ui-hardening-metrics",
        ):
            if "tools\\winui_agentic_ui_hardening_metrics.py" not in scripts.get(script, ""):
                failures.append(f"package script missing metrics tool: {script}")
    return failures


def render_markdown(report: dict[str, object]) -> str:
    totals = report["totals"]
    lines = [
        "# WinUI Agentic UI Hardening Metrics",
        "",
        f"Schema: `{report['schema']}`",
        f"Generated: `{report['generatedAt']}`",
        "",
        "## Totals",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| WinUI pages measured | {totals['winuiPagesMeasured']} |",
        f"| Logical code-behind lines | {totals['logicalCodeBehindLines']} |",
        f"| Routed handler methods | {totals['routedHandlerMethods']} |",
        f"| `async void` handlers | {totals['asyncVoidHandlers']} |",
        f"| Direct UI writes | {totals['directUiWrites']} |",
        f"| XAML event attributes | {totals['xamlEventAttributes']} |",
        f"| Automation IDs | {totals['automationIds']} |",
        f"| Pages with ViewModel files | {totals['pagesWithViewModelFiles']} |",
        "",
        "## Top Advisory Refactor Candidates",
        "",
        "| Rank | Page | Score | Code lines | Handlers | Direct UI writes |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for index, page in enumerate(report["topAdvisoryRefactorCandidates"], start=1):
        lines.append(
            f"| {index} | `{page['page']}` | {page['advisoryScore']} | "
            f"{page['logicalCodeBehindLines']} | {page['routedHandlerMethods']} | "
            f"{page['directUiWrites']} |"
        )
    lines.extend(
        [
            "",
            "These metrics are advisory locators only. They do not prove UI redesign, "
            "runtime behavior, release readiness, or migration need.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: dict[str, object], out_dir: Path = DEFAULT_REPORT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out_dir / "metrics.md").write_text(render_markdown(report), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pages = root / "OnslaughtCareerEditor.WinUI" / "Pages"
        pages.mkdir(parents=True)
        (pages / "SamplePage.xaml").write_text(
            '<Page x:Class="Demo.SamplePage">\n'
            '  <Button AutomationProperties.AutomationId="SampleButton" Click="SampleButton_Click" />\n'
            "</Page>\n",
            encoding="utf-8",
        )
        (pages / "SamplePage.xaml.cs").write_text(
            "namespace Demo;\n"
            "public sealed partial class SamplePage\n"
            "{\n"
            "    private async void SampleButton_Click(object sender, object e)\n"
            "    {\n"
            "        StatusTextBlock.Text = \"Done\";\n"
            "    }\n"
            "}\n",
            encoding="utf-8",
        )
        report = build_report(root)
        totals = report["totals"]
        assert totals["winuiPagesMeasured"] == 1
        assert totals["automationIds"] == 1
        assert totals["xamlEventAttributes"] == 1
        assert totals["routedHandlerMethods"] == 1
        assert totals["asyncVoidHandlers"] == 1
        assert totals["directUiWrites"] == 1
        assert report["topAdvisoryRefactorCandidates"][0]["page"] == "SamplePage"
    print("WinUI agentic UI hardening metrics self-test: PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if not args.check:
        parser.error("expected --check or --self-test")

    report = build_report(ROOT)
    failures = check_repo(report)
    if failures:
        report["status"] = "FAIL"
    if args.write_report:
        write_report(report)

    print(f"WinUI agentic UI hardening metrics: {report['status']}")
    totals = report["totals"]
    print(
        "Totals: "
        f"pages={totals['winuiPagesMeasured']} "
        f"codeLines={totals['logicalCodeBehindLines']} "
        f"handlers={totals['routedHandlerMethods']} "
        f"asyncVoid={totals['asyncVoidHandlers']} "
        f"directUiWrites={totals['directUiWrites']} "
        f"automationIds={totals['automationIds']}"
    )
    if args.write_report:
        print(f"Report: {relative(DEFAULT_REPORT_DIR / 'metrics.json')}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
