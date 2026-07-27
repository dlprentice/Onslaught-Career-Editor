#!/usr/bin/env python3
"""
Repo-wide OFFLINE markdown REACHABILITY check.

`tools/md_link_check.py` answers "does every link resolve?". It does not answer
"can a reader who starts at the front door ever arrive at this document?".

A tracked document that nothing links to is invisible in practice: it is found
only by accident, by `git ls-files`, or by a lucky grep. This project has
already been bitten by it -- a root-level policy document sat referenced from
nowhere for weeks and was acted on by nobody. This gate builds the reachability graph from the
documented entry points and reports what cannot be reached.

Design notes:
- Roots default to the files a new session is actually told to read:
  `CLAUDE.md`, `AGENTS.md`, `README.MD`.
- A link to a directory counts as reaching that directory's `_index.md` or
  `README.md`, because that is how the repository is browsed.
- Non-markdown link targets are followed only as far as recording them; they
  cannot themselves contain links.
- A file is classified `browse-reachable` rather than `orphan` when some
  ancestor directory (other than the repository root) already contains a
  reachable document. A reader who was sent into `binary-analysis/functions/`
  and told to "browse the directory tree" will find its children; that is a
  weaker guarantee than a link, but it is not invisibility. The repository root
  is deliberately excluded: a stray top-level `.md` is exactly the case this
  gate exists to catch.

Exit code is 0 unless `--fail-on-orphans` is passed.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Set

REPO_ROOT = Path(__file__).resolve().parents[1]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# Bare relative paths inside backticks, e.g. `reverse-engineering/RE-INDEX.md`.
BACKTICK_PATH_RE = re.compile(r"`([^`\n]*?\.md)`", re.IGNORECASE)

DEFAULT_ROOTS = ("CLAUDE.md", "AGENTS.md", "README.MD")

INDEX_BASENAMES = ("_index.md", "README.md", "readme.md", "index.md")

EXCLUDE_PREFIXES = (
    ".git/",
    ".venv/",
    ".pytest_cache/",
    "node_modules/",
    "release/artifacts/",
    ".artifacts/",
    "wave_",
)


def utc_now_iso() -> str:
    return (
        _dt.datetime.now(tz=_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def include_markdown_path(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    for pfx in EXCLUDE_PREFIXES:
        if rel.startswith(pfx):
            return False
    if "/bin/" in rel or "/obj/" in rel:
        return False
    return True


def tracked_markdown_files() -> List[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.md", "*.MD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        files = [REPO_ROOT / line for line in result.stdout.splitlines() if line.strip()]
        files = [p for p in files if p.is_file() and include_markdown_path(p)]
        if files:
            return sorted(set(files), key=lambda x: x.as_posix())
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return sorted(
        (p for p in REPO_ROOT.rglob("*.md") if include_markdown_path(p)),
        key=lambda x: x.as_posix(),
    )


def strip_fenced_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def is_external_target(t: str) -> bool:
    t_l = t.lower()
    return (
        t_l.startswith("#")
        or t_l.startswith("http://")
        or t_l.startswith("https://")
        or t_l.startswith("mailto:")
        or t_l.startswith("tel:")
        or "://" in t_l
    )


def normalize_target(t: str) -> str:
    t = t.strip()
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1].strip()
    for sep in ("#", "?"):
        if sep in t:
            t = t.split(sep, 1)[0]
    return t.strip()


def resolve_local_target(md_path: Path, target: str) -> Path:
    if target.startswith("/"):
        return (REPO_ROOT / target.lstrip("/")).resolve()
    return (md_path.parent / target).resolve()


def outgoing_markdown_targets(md_path: Path, follow_backticks: bool) -> Set[Path]:
    try:
        text = md_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = md_path.read_text(encoding="latin-1")

    body = strip_fenced_code(text)
    raw_targets: List[str] = [m.group(1) for m in LINK_RE.finditer(body)]
    if follow_backticks:
        raw_targets.extend(m.group(1) for m in BACKTICK_PATH_RE.finditer(body))

    out: Set[Path] = set()
    for raw in raw_targets:
        raw = raw.strip()
        if is_external_target(raw):
            continue
        target = normalize_target(raw)
        if not target:
            continue
        resolved = resolve_local_target(md_path, target)
        if resolved.is_dir():
            for base in INDEX_BASENAMES:
                cand = resolved / base
                if cand.is_file():
                    out.add(cand.resolve())
            continue
        if resolved.is_file() and resolved.suffix.lower() == ".md":
            out.add(resolved)
    return out


def rel(p: Path) -> str:
    try:
        return p.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        action="append",
        default=None,
        help="Entry-point markdown file, repo-relative. Repeatable. "
        f"Default: {', '.join(DEFAULT_ROOTS)}",
    )
    ap.add_argument(
        "--follow-backticks",
        action="store_true",
        help="Also treat `path/to/doc.md` in backticks as an edge. Many documents "
        "in this repository name their neighbours this way instead of linking.",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    ap.add_argument(
        "--fail-on-orphans",
        action="store_true",
        help="Exit 1 when any file is classified `orphan`.",
    )
    args = ap.parse_args()

    root_rels = tuple(args.root) if args.root else DEFAULT_ROOTS
    roots: List[Path] = []
    missing_roots: List[str] = []
    for r in root_rels:
        p = (REPO_ROOT / r).resolve()
        if p.is_file():
            roots.append(p)
        else:
            missing_roots.append(r)

    all_md = tracked_markdown_files()
    all_set = {p.resolve() for p in all_md}

    reachable: Set[Path] = set()
    queue: deque[Path] = deque()
    for r in roots:
        if r not in reachable:
            reachable.add(r)
            queue.append(r)

    while queue:
        cur = queue.popleft()
        for nxt in outgoing_markdown_targets(cur, args.follow_backticks):
            if nxt in reachable:
                continue
            reachable.add(nxt)
            queue.append(nxt)

    # Directories that a reader can already be standing in, having followed a
    # link. The repository root is excluded on purpose (see module docstring).
    reachable_dirs = {p.parent for p in reachable if p.parent != REPO_ROOT}

    def browse_covered(p: Path) -> bool:
        for anc in p.parents:
            if anc == REPO_ROOT:
                return False
            if anc in reachable_dirs:
                return True
        return False

    orphans: List[str] = []
    browse_reachable: List[str] = []
    for p in sorted(all_set, key=lambda x: x.as_posix()):
        if p in reachable:
            continue
        if browse_covered(p):
            browse_reachable.append(rel(p))
        else:
            orphans.append(rel(p))

    # Untracked-but-present markdown that IS linked from tracked docs is a
    # separate hazard: the link resolves locally and breaks in a fresh clone.
    tracked_rels = {rel(p) for p in all_set}
    reachable_untracked = sorted(
        rel(p) for p in reachable if rel(p) not in tracked_rels
    )

    payload: Dict[str, Any] = {
        "generated_utc": utc_now_iso(),
        "roots": list(root_rels),
        "missing_roots": missing_roots,
        "follow_backticks": bool(args.follow_backticks),
        "tracked_markdown_files": len(all_set),
        "reachable_count": len(reachable & all_set),
        "orphan_count": len(orphans),
        "orphans": orphans,
        "browse_reachable": browse_reachable,
        "reachable_but_untracked": reachable_untracked,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Roots: {', '.join(root_rels)}")
        if missing_roots:
            print(f"MISSING ROOTS: {', '.join(missing_roots)}")
        print(f"Tracked markdown files: {len(all_set)}")
        print(f"Reachable from roots:   {len(reachable & all_set)}")
        print(f"Browse-reachable only:  {len(browse_reachable)}")
        print(f"Orphans:                {len(orphans)}")
        if browse_reachable:
            by_dir: Dict[str, int] = {}
            for r in browse_reachable:
                by_dir[r.rsplit("/", 1)[0] if "/" in r else "."] = (
                    by_dir.get(r.rsplit("/", 1)[0] if "/" in r else ".", 0) + 1
                )
            print("  Link-unreachable but browse-covered, by directory (top 15):")
            for d, n in sorted(by_dir.items(), key=lambda kv: -kv[1])[:15]:
                print(f"    {n:5d}  {d}/")
        if reachable_untracked:
            print(f"Linked but UNTRACKED (breaks in a fresh clone): {len(reachable_untracked)}")
            for r in reachable_untracked[:25]:
                print(f"  ! {r}")
        for o in orphans:
            print(f"  - {o}")

    if args.fail_on_orphans and orphans:
        if not args.json:
            print("Markdown reachability check: FAIL")
        return 1
    if not args.json:
        print("Markdown reachability check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
