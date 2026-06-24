#!/usr/bin/env python3
"""Policy-based docs sync checker.

Modes:
- strict_mirror: canonical tree must match mirror tree for selected glob
- mirror_with_normalization: selected canonical/mirror file pairs must match
- curated: curated files must exist and include explicit canonical-hint pointers
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class Finding:
    kind: str
    message: str


def _norm_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    return data.replace(b"\r\n", b"\n")


def _load_policy(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_rel_paths(root: Path, glob: str, exclude_prefixes: List[str] | None = None) -> Dict[str, Path]:
    out: Dict[str, Path] = {}
    exclude_prefixes = exclude_prefixes or []
    for p in root.glob(glob):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(rel.startswith(prefix) for prefix in exclude_prefixes):
            continue
        out[rel] = p
    return out


def _run_strict_mirror(repo_root: Path, rules: List[Dict]) -> List[Finding]:
    findings: List[Finding] = []
    for rule in rules:
        name = rule.get("name", "strict_mirror_rule")
        canon_root = repo_root / rule["canonical_root"]
        mirror_root = repo_root / rule["mirror_root"]
        glob_pat = rule.get("glob", "**/*")
        exclude_prefixes = rule.get("exclude_prefixes", [])

        if not canon_root.is_dir():
            findings.append(Finding("error", f"[{name}] missing canonical root: {canon_root}"))
            continue
        if not mirror_root.is_dir():
            findings.append(Finding("error", f"[{name}] missing mirror root: {mirror_root}"))
            continue

        canon = _collect_rel_paths(canon_root, glob_pat, exclude_prefixes)
        mirror = _collect_rel_paths(mirror_root, glob_pat, exclude_prefixes)

        for rel, canon_path in sorted(canon.items()):
            mirror_path = mirror.get(rel)
            if mirror_path is None:
                findings.append(Finding("error", f"[{name}] missing in mirror: {rel}"))
                continue
            if _norm_bytes(canon_path) != _norm_bytes(mirror_path):
                findings.append(Finding("error", f"[{name}] content drift: {rel}"))

        for rel in sorted(mirror.keys()):
            if rel not in canon:
                findings.append(Finding("error", f"[{name}] extra in mirror: {rel}"))

    return findings


def _run_normalized_pairs(repo_root: Path, pairs: List[Dict]) -> List[Finding]:
    findings: List[Finding] = []
    for pair in pairs:
        name = pair.get("name", "pair")
        c = repo_root / pair["canonical"]
        m = repo_root / pair["mirror"]
        if not c.is_file():
            findings.append(Finding("error", f"[{name}] missing canonical file: {c.as_posix()}"))
            continue
        if not m.is_file():
            findings.append(Finding("error", f"[{name}] missing mirror file: {m.as_posix()}"))
            continue
        if _norm_bytes(c) != _norm_bytes(m):
            findings.append(Finding("error", f"[{name}] canonical/mirror mismatch"))

    return findings


def _run_curated(repo_root: Path, curated: List[Dict]) -> List[Finding]:
    findings: List[Finding] = []
    for item in curated:
        path = repo_root / item["path"]
        hint = item.get("canonical_hint")
        if not path.is_file():
            findings.append(Finding("error", f"[curated] missing file: {path.as_posix()}"))
            continue
        if hint:
            text = path.read_text(encoding="utf-8", errors="replace")
            if hint not in text:
                findings.append(
                    Finding("error", f"[curated] canonical hint missing in {item['path']}: {hint}")
                )

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate docs sync policy")
    ap.add_argument(
        "--policy",
        default="tools/docsync_policy.json",
        help="Policy JSON path relative to repo root",
    )
    ap.add_argument(
        "--json-out",
        default="",
        help="Optional output JSON report path relative to repo root",
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    policy_path = repo_root / args.policy
    if not policy_path.is_file():
        print(f"ERROR: missing policy file: {policy_path.as_posix()}")
        return 2

    policy = _load_policy(policy_path)
    findings: List[Finding] = []
    findings.extend(_run_strict_mirror(repo_root, policy.get("strict_mirror", [])))
    findings.extend(_run_normalized_pairs(repo_root, policy.get("mirror_with_normalization", [])))
    findings.extend(_run_curated(repo_root, policy.get("curated", [])))

    errors = [f for f in findings if f.kind == "error"]
    status = "PASS" if not errors else "FAIL"

    report = {
        "status": status,
        "errors": [f.message for f in errors],
        "error_count": len(errors),
    }

    if args.json_out:
        out_path = repo_root / args.json_out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Docsync policy check: {status}")
    if errors:
        for err in errors[:200]:
            print(f"- {err.message}")
        if len(errors) > 200:
            print(f"- ... ({len(errors) - 200} more)")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
