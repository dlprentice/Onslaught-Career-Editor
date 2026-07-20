#!/usr/bin/env python3
"""Generate the public-safe third-party notice source for the WinUI lane."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release" / "readiness" / "THIRD_PARTY_NOTICES.winui.md"

PROJECTS = [
    ("WinUI product", ROOT / "OnslaughtCareerEditor.WinUI" / "OnslaughtCareerEditor.WinUI.csproj"),
    ("AppCore support", ROOT / "OnslaughtCareerEditor.AppCore" / "OnslaughtCareerEditor.AppCore.csproj"),
    ("C# CLI support", ROOT / "OnslaughtCareerEditor.Cli" / "OnslaughtCareerEditor.Cli.csproj"),
    ("AppCore tests", ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "OnslaughtCareerEditor.AppCore.Tests.csproj"),
    ("WinUI automation tests", ROOT / "OnslaughtCareerEditor.UiTests" / "OnslaughtCareerEditor.UiTests.csproj"),
]


@dataclass
class PackageNotice:
    package_id: str
    version: str
    used_by: set[str] = field(default_factory=set)
    direct_in: set[str] = field(default_factory=set)
    license_signal: str = "not declared in local NuGet metadata"
    project_url: str = ""
    repository_url: str = ""
    copyright: str = ""

    @property
    def lane(self) -> str:
        if any(label in self.used_by for label in ("WinUI product", "AppCore support")):
            return "Product/runtime"
        if any("support" in label.lower() for label in self.used_by):
            return "Support tooling"
        return "Test-only"

    @property
    def posture(self) -> str:
        lower = f"{self.package_id} {self.license_signal}".lower()
        if "lgpl" in lower or "videolan" in lower or "libvlc" in lower:
            return "Ship as separate replaceable libraries with the LGPL license and exact upstream source links."
        if self.package_id.lower().startswith("microsoft."):
            return "Microsoft license/notice terms must be included as applicable."
        if self.lane == "Test-only":
            return "Not expected in product runtime output; keep if test artifacts are distributed."
        return "Include in final notices when redistributed."


def strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_child(element: ET.Element, name: str) -> ET.Element | None:
    for child in element:
        if strip_namespace(child.tag) == name:
            return child
    return None


def child_text(element: ET.Element | None, name: str) -> str:
    if element is None:
        return ""

    child = find_child(element, name)
    return (child.text or "").strip() if child is not None else ""


def child_attr(element: ET.Element | None, name: str, attr: str) -> str:
    if element is None:
        return ""

    child = find_child(element, name)
    return (child.attrib.get(attr) or "").strip() if child is not None else ""


def parse_direct_package_refs(project_path: Path) -> dict[str, str]:
    tree = ET.parse(project_path)
    refs: dict[str, str] = {}
    for element in tree.iter():
        if strip_namespace(element.tag) != "PackageReference":
            continue

        include = element.attrib.get("Include") or element.attrib.get("Update")
        version = element.attrib.get("Version") or child_text(element, "Version")
        if include and version:
            refs[include.lower()] = version
    return refs


def parse_assets_packages(project_path: Path) -> dict[str, str]:
    assets_path = project_path.parent / "obj" / "project.assets.json"
    if not assets_path.exists():
        return {}

    data = json.loads(assets_path.read_text(encoding="utf-8"))
    packages: dict[str, str] = {}
    for key, row in data.get("libraries", {}).items():
        if row.get("type") != "package" or "/" not in key:
            continue

        package_id, version = key.rsplit("/", 1)
        packages[package_id.lower()] = version
    return packages


def global_packages_root() -> Path:
    env_root = os.environ.get("NUGET_PACKAGES")
    if env_root:
        return Path(env_root)

    return Path.home() / ".nuget" / "packages"


def read_nuspec_metadata(package_id: str, version: str) -> dict[str, str]:
    package_root = global_packages_root() / package_id.lower() / version
    nuspecs = sorted(package_root.glob("*.nuspec"))
    if not nuspecs:
        return {}

    tree = ET.parse(nuspecs[0])
    metadata = find_child(tree.getroot(), "metadata")
    if metadata is None:
        return {}

    license_text = child_text(metadata, "license")
    license_type = child_attr(metadata, "license", "type")
    if license_text and license_type:
        license_signal = f"{license_text} ({license_type})"
    elif license_text:
        license_signal = license_text
    else:
        license_signal = child_text(metadata, "licenseUrl")

    return {
        "license_signal": license_signal or "not declared in local NuGet metadata",
        "license_type": license_type,
        "license_value": license_text,
        "project_url": child_text(metadata, "projectUrl"),
        "repository_url": child_attr(metadata, "repository", "url"),
        "repository_commit": child_attr(metadata, "repository", "commit"),
        "copyright": child_text(metadata, "copyright"),
    }


def collect_notices() -> list[PackageNotice]:
    notices: dict[tuple[str, str], PackageNotice] = {}

    for label, project_path in PROJECTS:
        direct_refs = parse_direct_package_refs(project_path)
        packages = parse_assets_packages(project_path) or direct_refs
        for package_key, version in packages.items():
            canonical_id = package_key
            notice = notices.setdefault(
                (canonical_id, version),
                PackageNotice(package_id=canonical_id, version=version),
            )
            notice.used_by.add(label)
            if package_key in direct_refs:
                notice.direct_in.add(label)

    for notice in notices.values():
        metadata = read_nuspec_metadata(notice.package_id, notice.version)
        if metadata:
            notice.license_signal = metadata["license_signal"]
            notice.project_url = metadata["project_url"]
            notice.repository_url = metadata["repository_url"]
            notice.copyright = metadata["copyright"]

    return sorted(notices.values(), key=lambda item: (item.lane, item.package_id.lower(), item.version))


def display_id(package_id: str) -> str:
    # Local NuGet paths are lowercase; keep markdown stable without implying a local path.
    known = {
        "libvlcsharp": "LibVLCSharp",
        "microsoft.windowsappsdk": "Microsoft.WindowsAppSDK",
        "microsoft.web.webview2": "Microsoft.Web.WebView2",
        "naudio": "NAudio",
        "naudio.vorbis": "NAudio.Vorbis",
        "videolan.libvlc.windows": "VideoLAN.LibVLC.Windows",
        "markdig": "Markdig",
        "system.commandline": "System.CommandLine",
        "flaui.core": "FlaUI.Core",
        "flaui.uia3": "FlaUI.UIA3",
        "nunit": "NUnit",
        "xunit": "xunit",
    }
    return known.get(package_id.lower(), package_id)


def sanitize_cell(value: str) -> str:
    value = value.replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()
    return value or "-"


def render_markdown(notices: list[PackageNotice]) -> str:
    lines = [
        "# WinUI Third-Party Notices",
        "",
        "Status: generated release notice source",
        "",
        "This file is generated from the active WinUI product, AppCore/support, CLI/support, and test project dependency graph plus local NuGet package metadata. Public ZIPs pair it with a generated `THIRD_PARTY_LICENSES/` bundle containing applicable package license/notice files and the .NET runtime notices.",
        "",
        "Retail executables, user saves, bulk extracted assets, raw captures, local NuGet cache paths, and local machine paths are intentionally omitted.",
        "",
        "## Binary Release Boundary",
        "",
        "- Generate this file from the final restored/published dependency graph before any public binary release.",
        "- Include applicable package license and notice files in the final installer/ZIP/MSIX output.",
        "- Keep the dynamically loaded LibVLC components replaceable and retain the matching LGPL notice, license, and source links.",
        "- Test-only dependencies are listed for repo transparency; they are not expected in the product runtime output unless test artifacts are distributed.",
        "",
        "## Package Notices",
        "",
        "| Package | Version | Lane | Direct reference | License signal | Copyright | Project/source | Release posture |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- |",
    ]

    for notice in notices:
        project_source = notice.repository_url or notice.project_url
        direct_reference = ", ".join(sorted(notice.direct_in)) if notice.direct_in else "transitive"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{sanitize_cell(display_id(notice.package_id))}`",
                    sanitize_cell(notice.version),
                    sanitize_cell(notice.lane),
                    sanitize_cell(direct_reference),
                    sanitize_cell(notice.license_signal),
                    sanitize_cell(notice.copyright),
                    sanitize_cell(project_source),
                    sanitize_cell(notice.posture),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Required Final Packaging Checks",
            "",
            "1. Publish the exact WinUI binary candidate.",
            "2. Re-run `py -3 tools\\generate_winui_third_party_notices.py --check` after restore/publish so dependency drift is visible.",
            "3. Verify the package contains this notice plus the generated `THIRD_PARTY_LICENSES/` bundle for its actual published dependency graph.",
            "4. Verify `THIRD_PARTY_LICENSES/README.txt` documents the separate LibVLC files, compatible replacement path, LGPL terms, and exact upstream source locations.",
            "5. Keep retail executables, user saves, bulk extraction output, and raw proof artifacts outside the release package.",
            "",
            "## Current Limitations",
            "",
            "- This notice source is generated from restored project assets and local NuGet metadata, not from a signed installer artifact.",
            "- The portable ZIP gate owns the final dependency-license bundle and checks it against the exact published graph.",
            "- These notices record the distribution boundary; they are not legal advice or a rightsholder endorsement.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the generated notice file is stale")
    args = parser.parse_args()

    notices = collect_notices()
    rendered = render_markdown(notices)

    if args.check:
        existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if existing != rendered:
            print(f"{OUTPUT} is stale; run py -3 tools\\generate_winui_third_party_notices.py")
            return 1

        print(f"Third-party notices check: PASS ({len(notices)} packages)")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT} ({len(notices)} packages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
