#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
Repo-wide OFFLINE markdown link check.

Goal: catch broken *local* links (relative paths) and broken heading anchors early.

Notes:
- External links (http/https/mailto/etc.) are ignored.
- An anchor (`file.md#heading` or `#heading`) is checked against the headings of the
  Markdown file it names, by GitHub's slug rule (lower case, punctuation dropped, spaces
  to hyphens, a repeated heading numbered -1, -2) and against `id=` / `name=` attributes
  of raw HTML. Line anchors (`#L12`) and anchors into files that are not Markdown are not
  checked. Setext headings (underlined with === or ---) are not read as anchors.
- This is best-effort and intentionally conservative.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[1]

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ATX_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
HTML_ANCHOR_RE = re.compile(r"""<[^>]*?\b(?:id|name)\s*=\s*["']([^"']+)["']""", re.I)
LINE_ANCHOR_RE = re.compile(r"^L\d+(?:C\d+)?(?:-L\d+(?:C\d+)?)?$")
PUBLIC_CORE_MARKDOWN = (
    "README.MD",
    "GOAL.md",
    "PROGRAM.md",
    "PROJECT-INDEX.md",
    "CURRENT_CAPABILITIES.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "VALIDATION.md",
    "lore/_index.md",
    "reverse-engineering/RE-INDEX.md",
    "rebuild/README.md",
    "rebuild/PROVENANCE.md",
)


def utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_markdown_name(name: str) -> bool:
    """Markdown by extension, in any case: README.MD was once skipped because of its case."""
    return name.lower().endswith(".md")


def iter_filesystem_markdown_files() -> List[Path]:
    files: List[Path] = []
    for p in REPO_ROOT.rglob("*"):
        if not p.is_file() or not is_markdown_name(p.name) or not include_markdown_path(p):
            continue
        files.append(p)
    files.sort(key=lambda x: x.as_posix())
    return files


def include_markdown_path(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    if rel.startswith(".git/"):
        return False
    if rel.startswith(".venv/"):
        return False
    if rel.startswith(".pytest_cache/"):
        return False
    if rel.startswith("node_modules/"):
        return False
    if rel.startswith("release/artifacts/"):
        return False
    if rel.startswith(".artifacts/"):
        return False
    if rel.startswith("wave_"):
        return False
    if "/bin/" in rel or "/obj/" in rel:
        return False
    return True


def iter_markdown_files(scope: str = "all") -> List[Path]:
    if scope == "public-core":
        return sorted(
            [REPO_ROOT / rel for rel in PUBLIC_CORE_MARKDOWN if (REPO_ROOT / rel).is_file()],
            key=lambda x: x.as_posix(),
        )

    try:
        result = subprocess.run(
            ["git", "ls-files", "--", ":(icase)*.md"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        files = [REPO_ROOT / line for line in result.stdout.splitlines() if line.strip()]
        files = [p for p in files if p.is_file() and is_markdown_name(p.name) and include_markdown_path(p)]
        files.sort(key=lambda x: x.as_posix())
        if files:
            return files
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return iter_filesystem_markdown_files()


def strip_fenced_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def inline_code_ranges(text: str) -> List[Tuple[int, int]]:
    """Ranges whose apparent ``[label](target)`` syntax is literal code."""
    return [(match.start(), match.end()) for match in re.finditer(r"`[^`\n]*`", text)]


def inside_any_range(position: int, ranges: List[Tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in ranges)


def is_external_target(t: str) -> bool:
    t_l = t.lower()
    if t_l.startswith("#"):
        return True
    if t_l.startswith("http://") or t_l.startswith("https://"):
        return True
    if t_l.startswith("mailto:") or t_l.startswith("tel:"):
        return True
    if "://" in t_l:
        return True
    return False


def normalize_target(t: str) -> str:
    t = t.strip()
    # strip optional surrounding <>
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1].strip()
    # drop anchor
    if "#" in t:
        t = t.split("#", 1)[0]
    # drop query
    if "?" in t:
        t = t.split("?", 1)[0]
    return t.strip()


def resolve_local_target(md_path: Path, target: str, root: Path = REPO_ROOT) -> Path:
    # Repo-root absolute links like "/reverse-engineering/..." are treated as repo-root relative.
    if target.startswith("/"):
        return (root / target.lstrip("/")).resolve()
    return (md_path.parent / target).resolve()


def heading_text(markdown: str) -> str:
    """The text of a heading as it renders: images and links to their text, HTML tags, code ticks and emphasis marks dropped."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", markdown)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("`", "").replace("*", "").replace("~~", "")
    return re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)


def slugify(markdown: str) -> str:
    """GitHub's heading slug: lower case; letters, marks, numbers, '-' and '_' kept; every space a hyphen; the rest dropped."""
    text = heading_text(markdown).strip().lower()
    kept = [ch for ch in text if ch in " -_" or unicodedata.category(ch)[0] in "LMN"]
    return "".join(kept).replace(" ", "-")


def anchors_in(text: str) -> Set[str]:
    """Every anchor a Markdown document offers: its ATX headings' slugs (a repeated one numbered -1, -2, ...) and raw-HTML ids."""
    scan = strip_fenced_code(text)
    anchors: Set[str] = set(HTML_ANCHOR_RE.findall(scan))
    seen: Dict[str, int] = {}
    for line in scan.splitlines():
        match = ATX_HEADING_RE.match(line)
        if not match or not match.group(2).strip():
            continue
        base = slugify(match.group(2))
        slug, n = base, 0
        while slug in anchors or slug in seen:
            n += 1
            slug = f"{base}-{n}"
        seen[slug] = 1
        anchors.add(slug)
    return anchors


def fragment_of(raw_target: str) -> str:
    """The percent-decoded fragment of a link target (up to a title or a query), or ''."""
    _, hash_mark, rest = raw_target.partition("#")
    if not hash_mark or not rest.split():
        return ""
    return unquote(rest.split()[0].split("?", 1)[0])


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def check_links(md_files: List[Path], root: Path) -> Tuple[List[Dict[str, Any]], int]:
    """(broken links and anchors, links checked) over the given Markdown files; local targets resolve against root."""
    broken: List[Dict[str, Any]] = []
    total_links = 0
    anchor_cache: Dict[Path, Set[str]] = {}

    def anchors_of(path: Path) -> Set[str]:
        if path not in anchor_cache:
            anchor_cache[path] = {a.lower() for a in anchors_in(read_text(path))}
        return anchor_cache[path]

    for p in md_files:
        rel = p.relative_to(root).as_posix()
        scan = strip_fenced_code(read_text(p))
        code_ranges = inline_code_ranges(scan)
        for m in LINK_RE.finditer(scan):
            # Keep links whose *label* uses backticks, such as
            # [`texture.cpp`](path), but ignore link-like text wholly inside a
            # code span, such as `vtable[0](1)`.
            if inside_any_range(m.start(), code_ranges):
                continue
            raw_target = m.group(1).strip()
            fragment = fragment_of(raw_target)
            if raw_target.startswith("#"):
                total_links += 1
                if fragment and not LINE_ANCHOR_RE.match(fragment) and fragment.lower() not in anchors_of(p):
                    broken.append({"path": rel, "target": "#" + fragment, "resolved": os.fspath(p), "kind": "anchor"})
                continue
            if is_external_target(raw_target):
                continue
            target = normalize_target(raw_target)
            if not target:
                continue
            total_links += 1
            resolved = resolve_local_target(p, target, root)
            if not resolved.exists():
                broken.append({"path": rel, "target": target, "resolved": os.fspath(resolved), "kind": "path"})
            elif fragment and not LINE_ANCHOR_RE.match(fragment) and resolved.is_file() and is_markdown_name(resolved.name):
                if fragment.lower() not in anchors_of(resolved):
                    broken.append({"path": rel, "target": f"{target}#{fragment}", "resolved": os.fspath(resolved), "kind": "anchor"})
    return broken, total_links


def self_test() -> int:
    cases = [("README.MD", True), ("notes.md", True), ("Guide.Md", True), ("page.mdx", False), ("md", False)]
    failures = [name for name, expected in cases if is_markdown_name(name) != expected]
    tracked = [p.relative_to(REPO_ROOT).as_posix() for p in iter_markdown_files("all")]
    if (REPO_ROOT / "README.MD").is_file() and "README.MD" not in tracked:
        failures.append("README.MD is not scanned")
    slugs = [
        ("Hello World", "hello-world"), ("What's new?", "whats-new"), ("A `code` heading", "a-code-heading"),
        ("[A link](https://example.com/x) text", "a-link-text"), ("**Bold** and *italic*", "bold-and-italic"),
        ("C# notes", "c-notes"), ("1. Numbered", "1-numbered"), ("Under_score kept", "under_score-kept"),
        ("_Emphasised_ words", "emphasised-words"), ("Two  spaces", "two--spaces"), ("Ünïcode ok", "ünïcode-ok"),
        ("Native main menu / (draft)", "native-main-menu--draft"), ("<b>Tags</b> go", "tags-go"), ("Dashes - and – dashes", "dashes---and--dashes"),
        ("Re\u0301sume\u0301", "re\u0301sume\u0301"), ("Trailing <i>tag</i> ", "trailing-tag"), ("![Alt text](img.png) after", "alt-text-after"),
        ("[Ref][1] text", "ref-text"), ("snake_case_name", "snake_case_name"),
    ]
    failures += [f"slug of {text!r}: {slugify(text)!r}, expected {want!r}" for text, want in slugs if slugify(text) != want]
    doc = ("# Title\n\n## Same\n\n### Same\n\n## Same\n\n```\n# Not a heading\n```\n\n    # indented code\n\n#### Closed ####\n\n<a id=\"raw-id\"></a>\n\n"
           "####### Seven hashes\n\n#NoSpace\n\n## \n\n<a name='old-name'></a> <A NAME=\"Upper-Name\"></A>\n")
    expected = {"title", "same", "same-1", "same-2", "closed", "raw-id", "old-name", "Upper-Name"}
    if anchors_in(doc) != expected:
        failures.append(f"anchors_in: {sorted(anchors_in(doc))}, expected {sorted(expected)}")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.md").write_text(
            "# A\n\n## Local heading\n\n[ok](b.md#target-heading) [ok2](b.md#Target-Heading) [ok3](#local-heading) [ok4](b.md)\n"
            "[bad](b.md#missing-heading) [bad2](#nope) [bad3](missing.md#x) [line](b.md#L12) [code](notes.txt#anything) [web](https://x.test/a#b)\n"
            "[enc](b.md#target%2Dheading) [title](b.md#target-heading \"a title\") `[inline](b.md#not-checked)`\n\n```\n[fenced](b.md#not-checked)\n```\n"
            "[ok5](#Local-Heading) [up](b.md#upper-name) [l1](b.md#L12C3) [l2](b.md#L12-L20) [l3](b.md#L12C3-L20C9) [q](b.md#target-heading?plain=1)\n"
            "[e](b.md#) [e2](#) [qp](b.md?plain=1) [ang](<b.md>) [root](/b.md) [dir](dir.md#x) `x`[after](b.md#bad-after)\n"
            "an odd ` tick\n[odd](b.md#odd-tick-missing)\nanother ` tick\n",
            encoding="utf-8")
        (root / "b.md").write_text("# B\n\n## Target heading\n\n<A NAME=\"Upper-Name\"></A>\n", encoding="utf-8")
        (root / "dir.md").mkdir()
        (root / "notes.txt").write_text("text", encoding="utf-8")
        broken, total = check_links([root / "a.md", root / "b.md"], root)
        got = sorted((item["target"], item["kind"]) for item in broken)
        want = sorted([("b.md#missing-heading", "anchor"), ("#nope", "anchor"), ("missing.md", "path"),
                       ("b.md#bad-after", "anchor"), ("b.md#odd-tick-missing", "anchor")])
        if got != want:
            failures.append(f"check_links found {got}, expected {want}")
        if total != 25:
            failures.append(f"check_links counted {total} links, expected 25")
    print("md_link_check self-test: " + ("PASS" if not failures else f"FAIL {failures}"))
    return 0 if not failures else 1


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return self_test()
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-dir",
        default=".artifacts/md-link-check",
        help="Output dir (workspace-relative)",
    )
    ap.add_argument("--date", default=_dt.date.today().isoformat(), help="Date stamp (YYYY-MM-DD)")
    ap.add_argument(
        "--scope",
        choices=("all", "public-core"),
        default="all",
        help="Markdown file scope to scan.",
    )
    ap.add_argument(
        "--check-only",
        action="store_true",
        help="Validate without writing markdown/json report artifacts.",
    )
    args = ap.parse_args()

    md_files = iter_markdown_files(args.scope)
    broken, total_links = check_links(md_files, REPO_ROOT)

    payload: Dict[str, Any] = {
        "generated_utc": utc_now_iso(),
        "scope": args.scope,
        "files_scanned": len(md_files),
        "total_local_links_checked": total_links,
        "broken_links": broken,
        "broken_count": len(broken),
    }

    out_json: Path | None = None
    if not args.check_only:
        out_dir = (REPO_ROOT / args.out_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_json = out_dir / f"md-link-check-{args.date}.json"
        out_md = out_dir / f"md-link-check-{args.date}.md"
        out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

        lines: List[str] = []
        lines.append(f"# Markdown Link Check ({args.date})")
        lines.append("")
        lines.append(f"- Files scanned: `{len(md_files)}`")
        lines.append(f"- Local links checked: `{total_links}`")
        lines.append(f"- Broken links and anchors: `{len(broken)}`")
        # State the bound. A report that prints "0 broken" without naming the set
        # it scanned reads as a repo-wide result; it is not one. Gitignored trees
        # (notably local-lab/, ~470 markdown files) are structurally invisible
        # here, so this report must never be cited as evidence that their links
        # resolve. Added 2026-07-28.
        if args.scope == "public-core":
            scope_note = (
                "an explicit list of public-core documents only. Every other "
                "markdown file in the repository is **not** scanned"
            )
        else:
            scope_note = (
                "**git-tracked markdown only** (`git ls-files '*.md'`). Gitignored "
                "trees are structurally invisible to this check — including "
                "`local-lab/` — and `include_markdown_path()` additionally drops "
                "`.git/`, `.venv/`, `.pytest_cache/`, `node_modules/`, "
                "`release/artifacts/`, `.artifacts/`, `wave_*`, and any `/bin/` or "
                "`/obj/` path. A `0` above is a result about that set, not about "
                "the repository"
            )
        lines.append(f"- Scope: `{args.scope}` — {scope_note}.")
        lines.append("")
        if broken:
            lines.append("## Broken Links (Top 200)")
            lines.append("")
            for item in broken[:200]:
                lines.append(f"- `{item['path']}` -> `{item['target']}` ({item['kind']}; resolved `{item['resolved']}`)")
            if len(broken) > 200:
                lines.append(f"- ... (see `{out_json.relative_to(REPO_ROOT).as_posix()}`)")
        else:
            lines.append("No broken local links or anchors detected.")

        out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(out_md.relative_to(REPO_ROOT).as_posix())
        print(out_json.relative_to(REPO_ROOT).as_posix())

    print(f"Markdown files scanned: {len(md_files)}")
    print(f"Local links checked: {total_links}")
    if broken:
        for item in broken[:25]:
            print(f"- {item['path']} -> {item['target']}")
        if len(broken) > 25:
            print(f"- ... ({len(broken) - 25} more)")
        print(f"Markdown link check: FAIL ({len(broken)} broken local links)" + (f"; {sum(1 for b in broken if b['kind'] == 'anchor')} of them anchors" if any(b["kind"] == "anchor" for b in broken) else ""))
        return 1
    print("Markdown link check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
