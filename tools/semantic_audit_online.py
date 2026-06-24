#!/usr/bin/env python3
"""
Repo-wide ONLINE doc audit against a live GhidraMCP HTTP instance.

This is intentionally read-only (HTTP GET only) so it can be run safely even
when Ghidra MCP mutations are unstable.

What it checks (best-effort):
- For function-entry mapping contexts in markdown files, verify that the
  documented address resolves to a function in Ghidra and that the name matches.
- For function docs that explicitly state an address/signature in the header,
  verify those fields against Ghidra function metadata.

What it does NOT do:
- Full semantic equivalence of prose behavior descriptions (manual review).

Usage:
  python3 tools/semantic_audit_online.py --base http://172.26.112.1:8193
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]

# Only treat these as "code VAs" for lookup. (BEA.exe base 0x00400000)
CODE_ADDR_MIN = 0x00400000
CODE_ADDR_MAX = 0x00600000

# Known "orphans": addresses we expect may legitimately be missing as functions
# (function-object creation can fail or require manual UI intervention).
KNOWN_ORPHAN_ADDRS = {
    # Orphan camera blocks
    0x00419D40,
    0x00419D70,
    0x00419D90,
    0x00419DC0,
    0x00419DE0,
    # FE multiplayer-start holes
    0x0051BFA0,
    0x0051C090,
    0x0051AE50,
    0x0051C280,
    # Orphan console callbacks (InitRestartLoop command callbacks)
    0x0046BE10,
    0x0046BE80,
    0x0046BEA0,
    0x0046BED0,
    0x0046BEF0,
    0x0046C0B0,
    0x0046C120,
    0x0046C150,
    0x0046C180,
    0x0046C200,
    # HUD vtable holes
    0x004DE6B0,
    0x004DE7D0,
}


ADDR_RE = re.compile(r"0x[0-9a-fA-F]{8}")
MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iter_markdown_files() -> List[Path]:
    files: List[Path] = []
    for base in [
        REPO_ROOT,
    ]:
        for p in base.rglob("*.md"):
            # ignore vendored deps / build outputs if any
            rel = p.relative_to(REPO_ROOT).as_posix()
            if rel.startswith(".git/"):
                continue
            if rel.startswith(".venv/"):
                continue
            if rel.startswith(".pytest_cache/"):
                continue
            if rel.startswith("node_modules/"):
                continue
            # Generated agent-output / scratch folders are not part of canonical docs.
            if rel.startswith("wave_"):
                continue
            if "/bin/" in rel or "/obj/" in rel:
                continue
            if rel.startswith("reverse-engineering/binary-analysis/semantic-audit"):
                continue
            if rel.startswith("lore-book/reverse-engineering/binary-analysis/semantic-audit"):
                continue
            files.append(p)
    # stable order
    files.sort(key=lambda x: x.as_posix())
    return files


def md_inline_to_text(s: str) -> str:
    """
    Remove the most common markdown wrappers used in tables.
    Keeps this intentionally simple.
    """
    s = s.strip()
    # unwrap links: [text](path)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    # strip emphasis markers
    s = s.replace("**", "").replace("*", "")
    # strip backticks (after link/emphasis unwrapping too)
    while s.startswith("`") and s.endswith("`") and len(s) >= 2:
        s = s[1:-1].strip()
    return s.strip()


def parse_hex_addr(token: str) -> Optional[int]:
    token = token.strip()
    if not token.startswith("0x"):
        return None
    try:
        v = int(token, 16)
    except ValueError:
        return None
    if v < CODE_ADDR_MIN or v > CODE_ADDR_MAX:
        return None
    return v


@dataclasses.dataclass(frozen=True)
class HeadingCtx:
    level: int
    text: str


@dataclasses.dataclass(frozen=True)
class Expectation:
    addr: int
    expected_name: str
    expected_sig: Optional[str]
    source: str  # "table" | "header"
    context: str  # heading breadcrumb for debugging


def breadcrumb(headings: List[HeadingCtx]) -> str:
    if not headings:
        return ""
    return " / ".join(h.text for h in headings[-3:])


def is_negative_context(ctx: str) -> bool:
    ctx_l = ctx.lower()
    negative_keywords = [
        "callers",
        "called by",
        "called functions",
        "calls",
        "cross-references",
        "xrefs",
        "references",
        "related functions",
        "related files",
        "related",
        "patch",
        "patched",
        "original",
        "file offset",
        "byte",
        "vtable",
        "exception",
        "handler",
        "globals",
        "strings",
        "offsets",
        "members",
        "class layout",
    ]
    return any(k in ctx_l for k in negative_keywords)


def is_positive_context(ctx: str) -> bool:
    ctx_l = ctx.lower()
    positive_keywords = [
        "functions",
        "function map",
        "function mappings",
        "function index",
        "key functions",
        "function addresses",
    ]
    return any(k in ctx_l for k in positive_keywords)


def should_treat_table_as_function_map(
    rel_path: str, headings: List[HeadingCtx], header_cols: List[str]
) -> bool:
    ctx = breadcrumb(headings)
    if is_negative_context(ctx):
        return False

    header_l = [c.lower() for c in header_cols]
    if "address" not in header_l and "va" not in header_l:
        return False
    if "function" not in header_l and "name" not in header_l:
        return False

    banned_header_tokens = [
        "context",
        "line",
        "line#",
        "read/write",
        "caller",
        "callee",
        "jump",
        "offset",
        "index",
        "file offset",
        "original",
        "patched",
        "string",
        "usage",
        "region",
        "bytes",
    ]
    if any(any(bt in c for bt in banned_header_tokens) for c in header_l):
        return False

    # Boost for known index files.
    if rel_path.endswith("/_index.md") and ("/reverse-engineering/binary-analysis/functions/" in "/" + rel_path):
        if is_positive_context(ctx) or "functions" in ctx.lower():
            return True

    if is_positive_context(ctx):
        return True

    # Conservative default: allow only if file itself is an index-ish doc.
    if rel_path in (
        "reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md",
        "reverse-engineering/binary-analysis/README.md",
        "reverse-engineering/binary-analysis/executable-analysis.md",
        "reverse-engineering/binary-analysis/functions/_index.md",
    ):
        return True

    return False


def extract_expectations_from_markdown(rel_path: str, text: str) -> List[Expectation]:
    expectations: List[Expectation] = []
    lines = text.splitlines()
    headings: List[HeadingCtx] = []
    h1_title: Optional[str] = None

    # Header-style expectations (common function-doc template)
    # Look for "**Address:** `0x...`" and "**Signature:** `...`".
    #
    # Note: Many docs format labels as "**Address:**" (bold). That yields text
    # like "Address:** `0x...`" so we must tolerate "*" immediately after ":".
    header_addr: Optional[int] = None
    header_sig: Optional[str] = None
    for i, line in enumerate(lines[:60]):  # header is near the top
        m = MD_HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if level == 1 and h1_title is None:
                h1_title = title
            continue

        if header_addr is None:
            m = re.search(r"Address:\s*(?:\*+\s*)?`?(0x[0-9a-fA-F]{8})`?", line)
            if m:
                header_addr = parse_hex_addr(m.group(1))
                continue
        if header_sig is None:
            m = re.search(r"Signature:\s*(?:\*+\s*)?`?([^`]+?)`?\s*$", line)
            if m:
                header_sig = m.group(1).strip()
                continue

    if header_addr is not None:
        # Only apply header expectations to per-function docs, not general prose docs.
        is_function_doc = (
            "/reverse-engineering/binary-analysis/functions/" in ("/" + rel_path)
            and not rel_path.endswith("/_index.md")
        )
        title_txt = md_inline_to_text(h1_title or "")
        # Prevent headings like "Related Functions" from becoming an expected name.
        looks_like_fn = ("__" in title_txt) or title_txt.startswith("FUN_") or ("::" in title_txt)
        if is_function_doc and title_txt and looks_like_fn:
            expectations.append(
                Expectation(
                    addr=header_addr,
                    expected_name=title_txt,
                    expected_sig=header_sig,
                    source="header",
                    context=title_txt,
                )
            )

    # Table-style expectations
    i = 0
    while i < len(lines):
        line = lines[i]
        hm = MD_HEADING_RE.match(line)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2).strip()
            # pop headings >= level
            while headings and headings[-1].level >= level:
                headings.pop()
            headings.append(HeadingCtx(level=level, text=title))
            i += 1
            continue

        # Detect a markdown table header row.
        if line.strip().startswith("|") and "|" in line:
            # Need a separator row next.
            if i + 1 < len(lines) and re.match(r"^\s*\|?\s*[-: ]+\|", lines[i + 1]):
                header_cells = [md_inline_to_text(c) for c in line.strip().strip("|").split("|")]
                header_cells = [c.strip() for c in header_cells]
                if should_treat_table_as_function_map(rel_path, headings, header_cells):
                    # Parse rows until table ends.
                    j = i + 2
                    while j < len(lines) and lines[j].strip().startswith("|"):
                        row_cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                        if len(row_cells) < 2:
                            j += 1
                            continue
                        addr_token = md_inline_to_text(row_cells[0])
                        addr = parse_hex_addr(addr_token)
                        if addr is None:
                            j += 1
                            continue

                        # Find name column index.
                        name_idx = None
                        for k, hc in enumerate(header_cells):
                            if hc.lower() in ("function", "name"):
                                name_idx = k
                                break
                        if name_idx is None or name_idx >= len(row_cells):
                            j += 1
                            continue
                        # Some indexes intentionally list inline blocks / non-function labels.
                        row_text = " | ".join(md_inline_to_text(c) for c in row_cells).lower()
                        if "not a function" in row_text:
                            j += 1
                            continue
                        expected_name = md_inline_to_text(row_cells[name_idx])
                        if not expected_name:
                            j += 1
                            continue
                        # Strip trailing "(...)" notes used as annotations in tables.
                        m_note = re.match(r"^(.*?)(?:\s*\(([^)]+)\))\s*$", expected_name)
                        if m_note:
                            note = m_note.group(2).strip()
                            if note.upper() == "TODO" or note.startswith("FUN_"):
                                expected_name = m_note.group(1).strip()
                        # If the "name" is a placeholder (e.g. "(inline)"), do not treat as a function entry.
                        if expected_name.startswith("(") and expected_name.endswith(")"):
                            j += 1
                            continue

                        expectations.append(
                            Expectation(
                                addr=addr,
                                expected_name=expected_name,
                                expected_sig=None,
                                source="table",
                                context=breadcrumb(headings),
                            )
                        )
                        j += 1

                # Skip past table regardless.
                # Consume until non-table line.
                k = i + 2
                while k < len(lines) and lines[k].strip().startswith("|"):
                    k += 1
                i = k
                continue

        i += 1

    return expectations


def http_get_json(url: str, timeout_s: int) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read()
    return json.loads(raw.decode("utf-8", errors="replace"))


def fetch_function_info(base: str, addr: int, timeout_s: int) -> Optional[Dict[str, Any]]:
    url = f"{base.rstrip('/')}/functions/0x{addr:08x}"
    try:
        j = http_get_json(url, timeout_s=timeout_s)
    except urllib.error.HTTPError as e:
        # 404 / 500 etc
        _ = e
        return None
    except urllib.error.URLError as e:
        raise RuntimeError(f"HTTP connection failed for {url}: {e}") from e

    if not j.get("success"):
        return None
    return j.get("result")


def normalize_expected_name(expected: str) -> str:
    # Expectations should already be unwrapped, but normalize defensively.
    return md_inline_to_text(expected).strip()


def acceptable_name_match(expected: str, actual: str) -> bool:
    expected_n = normalize_expected_name(expected)
    # Placeholder labels used in docs to indicate non-entry/callsite/etc.
    if expected_n.startswith("(") and expected_n.endswith(")"):
        return True
    if expected_n.lower() in {"unknown", "(unknown)"}:
        return True

    if expected_n == actual:
        return True

    # Allow a pure style mapping: CCareer::Save -> CCareer__Save
    if "::" in expected_n and expected_n.replace("::", "__") == actual:
        return True

    return False


def normalize_sig(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def normalize_type_tokens(s: str) -> str:
    # Normalize whitespace and pointer/reference spacing for comparison.
    s = normalize_sig(s)
    # Remove spaces around pointer/reference tokens so "char *" == "char*" etc.
    s = re.sub(r"\s*([*&])\s*", r"\1", s)
    return s


def split_params(param_blob: str) -> List[str]:
    # Best-effort split on commas, ignoring nested parentheses/brackets.
    params: List[str] = []
    cur: List[str] = []
    depth_paren = 0
    depth_brack = 0
    for ch in param_blob:
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren = max(0, depth_paren - 1)
        elif ch == "[":
            depth_brack += 1
        elif ch == "]":
            depth_brack = max(0, depth_brack - 1)
        if ch == "," and depth_paren == 0 and depth_brack == 0:
            params.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    tail = "".join(cur).strip()
    if tail:
        params.append(tail)
    return params


def param_type_only(p: str) -> str:
    p = normalize_sig(p)
    if not p:
        return ""
    # Drop default value, if present.
    p = re.sub(r"\s*=\s*.+$", "", p).strip()
    if p == "...":
        return "..."

    # If it looks like a function pointer type, keep as-is (hard to strip name safely).
    if "(" in p or ")" in p:
        return normalize_type_tokens(p)

    # Strip trailing identifier assumed to be the parameter name.
    m = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", p)
    if m and p != m.group(1):
        p = p[: m.start(1)].rstrip()
    return normalize_type_tokens(p)


def signature_skeleton(sig: str) -> str:
    s = normalize_sig(sig)
    # Remove common calling convention markers.
    s = re.sub(r"\b__(thiscall|fastcall|stdcall|cdecl)\b", "", s)
    s = normalize_sig(s)
    if "(" not in s or ")" not in s:
        return normalize_type_tokens(s)

    prefix, rest = s.split("(", 1)
    params_blob = rest.rsplit(")", 1)[0]

    prefix = prefix.strip()
    # Prefix is "<ret> <name>" (usually); keep only return type.
    parts = prefix.split()
    ret = " ".join(parts[:-1]).strip() if len(parts) >= 2 else prefix
    ret = normalize_type_tokens(ret)

    params = [param_type_only(p) for p in split_params(params_blob)]
    params = [p for p in params if p]
    if params == ["void"]:
        params = []
    return f"{ret}({','.join(params)})"


def acceptable_sig_match(expected: str, actual: str) -> bool:
    return signature_skeleton(expected) == signature_skeleton(actual)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("GHYDRA_HTTP_BASE", "http://172.26.112.1:8193"))
    ap.add_argument("--timeout", type=int, default=10, help="HTTP timeout per GET in seconds")
    ap.add_argument(
        "--out-dir",
        default="reverse-engineering/binary-analysis",
        help="Output dir (workspace-relative)",
    )
    ap.add_argument("--date", default=_dt.date.today().isoformat(), help="Date stamp (YYYY-MM-DD)")
    args = ap.parse_args()

    base: str = args.base
    timeout_s: int = args.timeout
    out_dir = (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    md_files = iter_markdown_files()

    # First pass: extract expectations.
    file_rows: List[Dict[str, Any]] = []
    unique_addrs: Dict[int, None] = {}
    for p in md_files:
        rel = p.relative_to(REPO_ROOT).as_posix()
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="latin-1")

        exps = extract_expectations_from_markdown(rel, text)
        addrs = sorted({e.addr for e in exps})
        for a in addrs:
            unique_addrs[a] = None

        file_rows.append(
            {
                "path": rel,
                "status": "skip" if not exps else "pending",
                "code_addrs": [f"0x{a:08x}" for a in addrs],
                "expectations": [dataclasses.asdict(e) for e in exps],
                "mismatches": [],
            }
        )

    # Second pass: fetch unique function infos once.
    addr_info: Dict[int, Optional[Dict[str, Any]]] = {}
    for addr in unique_addrs.keys():
        addr_info[addr] = fetch_function_info(base, addr, timeout_s=timeout_s)

    reason_counts = {"missing_function": 0, "name_mismatch": 0, "sig_mismatch": 0, "expected_missing_orphan": 0}

    files_pass = 0
    files_pass_with_orphans = 0
    files_fail = 0
    files_skip = 0

    for row in file_rows:
        if row["status"] == "skip":
            files_skip += 1
            continue

        mismatches: List[Dict[str, Any]] = []
        for e in row["expectations"]:
            addr = int(e["addr"])
            expected_name = e["expected_name"]
            expected_sig = e.get("expected_sig")

            actual = addr_info.get(addr)
            if actual is None:
                if addr in KNOWN_ORPHAN_ADDRS:
                    reason_counts["expected_missing_orphan"] += 1
                    mismatches.append(
                        {
                            "reason": "expected_missing_orphan",
                            "addr": f"0x{addr:08x}",
                            "expected": {"expected_name": expected_name, "expected_sig": expected_sig, "source": e["source"], "context": e["context"]},
                            "actual": None,
                        }
                    )
                else:
                    reason_counts["missing_function"] += 1
                    mismatches.append(
                        {
                            "reason": "missing_function",
                            "addr": f"0x{addr:08x}",
                            "expected": {"expected_name": expected_name, "expected_sig": expected_sig, "source": e["source"], "context": e["context"]},
                            "actual": None,
                        }
                    )
                continue

            actual_name = actual.get("name") or ""
            actual_sig = actual.get("signature")

            if expected_name and actual_name and not acceptable_name_match(expected_name, actual_name):
                reason_counts["name_mismatch"] += 1
                mismatches.append(
                    {
                        "reason": "name_mismatch",
                        "addr": f"0x{addr:08x}",
                        "expected": {"expected_name": expected_name, "expected_sig": expected_sig, "source": e["source"], "context": e["context"]},
                        "actual": {"name": actual_name, "signature": actual_sig},
                    }
                )
            elif expected_sig and actual_sig and not acceptable_sig_match(expected_sig, actual_sig):
                reason_counts["sig_mismatch"] += 1
                mismatches.append(
                    {
                        "reason": "sig_mismatch",
                        "addr": f"0x{addr:08x}",
                        "expected": {"expected_name": expected_name, "expected_sig": expected_sig, "source": e["source"], "context": e["context"]},
                        "actual": {"name": actual_name, "signature": actual_sig},
                    }
                )

        row["mismatches"] = mismatches
        if not mismatches:
            row["status"] = "pass"
            files_pass += 1
        elif all(mm.get("reason") == "expected_missing_orphan" for mm in mismatches):
            row["status"] = "pass_with_orphans"
            files_pass_with_orphans += 1
        else:
            row["status"] = "fail"
            files_fail += 1

    payload = {
        "generated_utc": utc_now_iso(),
        "base": base,
        "files_total": len(file_rows),
        "files_pass": files_pass,
        "files_pass_with_orphans": files_pass_with_orphans,
        "files_fail": files_fail,
        "files_skip": files_skip,
        "reason_counts": reason_counts,
        "unique_code_addrs": sorted([f"0x{a:08x}" for a in unique_addrs.keys()]),
        "instances_current": None,  # informational only; discovered externally
        "files": file_rows,
    }

    out_json = out_dir / f"semantic-audit-online-pass-{args.date}.json"
    out_md = out_dir / f"semantic-audit-online-{args.date}.md"

    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    # Markdown summary
    lines: List[str] = []
    lines.append(f"# Online Semantic Audit ({args.date})")
    lines.append("")
    lines.append(f"- HTTP base: `{base}`")
    lines.append(f"- Files scanned: `{len(file_rows)}`")
    lines.append(f"- Unique code addresses checked (0x00400000-0x00600000): `{len(unique_addrs)}`")
    lines.append(
        f"- Result: `{files_pass}` pass, `{files_pass_with_orphans}` pass_with_orphans, `{files_fail}` fail, `{files_skip}` skip"
    )
    lines.append("")
    lines.append("## Mismatch Counts")
    lines.append("")
    for k in ["missing_function", "name_mismatch", "sig_mismatch", "expected_missing_orphan"]:
        lines.append(f"- `{k}`: `{reason_counts[k]}`")
    lines.append("")
    lines.append("## Failures (Top 50)")
    lines.append("")
    shown = 0
    for row in file_rows:
        if row["status"] != "fail":
            continue
        for mm in row["mismatches"]:
            if shown >= 50:
                break
            exp = mm.get("expected", {})
            actual = mm.get("actual")
            lines.append(
                f"- `{row['path']}`: `{mm['reason']}` at `{mm['addr']}` "
                f"(expected `{exp.get('expected_name')}`, actual `{(actual or {}).get('name')}`)"
            )
            shown += 1
        if shown >= 50:
            break
    if files_fail and shown < sum(len(r["mismatches"]) for r in file_rows if r["status"] == "fail"):
        lines.append(f"- ... (see `{out_json.relative_to(REPO_ROOT).as_posix()}`)")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(out_md.relative_to(REPO_ROOT).as_posix())
    print(out_json.relative_to(REPO_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
