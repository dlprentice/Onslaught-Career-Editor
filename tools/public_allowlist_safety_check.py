#!/usr/bin/env python3
"""Validate public-candidate allowlist safety beyond manifest freshness.

This check is path-aware. Root `media/**` is private, and archived app
families under `archive/**` are not part of the WinUI-first public candidate.
"""

from __future__ import annotations

import argparse
import ast
import html
import json
import re
import sys
import tempfile
import unicodedata
from functools import lru_cache
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "release" / "readiness" / "public_candidate_allowlist.tsv"
PRIVATE_TEXT_PAYLOAD_GUARD = ROOT / "release" / "readiness" / "private_public_payload_text_guard_patterns.json"

REQUIRED_PUBLIC_ROWS = {
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    "CONTRIBUTING.md",
    "COLLABORATION.md",
    "README.MD",
    "README.RELEASE.md",
    "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
    "SECURITY.md",
    "tools/README.md",
    "lore-book/BOOK.md",
    "lore-book/Start-Here.md",
    "lore-book/lore/_index.md",
    "lore/_index.md",
    "release/readiness/PUBLIC_SIGNOFF_COMMANDS.md",
    "release/readiness/public_AGENTS.md",
    "release/readiness/public_CURRENT_CAPABILITIES.txt",
    "release/readiness/public_gitignore.txt",
    "release/readiness/public_package.json",
    "release/readiness/public_RE_INDEX.txt",
    "release/readiness/public_quick_reference_index.txt",
    "release/readiness/public_ROADMAP_INDEX.txt",
    "release/readiness/public_mod_patch_runtime_rebuild_register.txt",
    "release/readiness/public_lore_book_mod_patch_runtime_rebuild_register.txt",
    "release/readiness/public_lore_index.txt",
    "release/readiness/public_lore_book_BOOK.txt",
    "release/readiness/public_lore_book_Start-Here.txt",
    "release/readiness/public_lore_book_lore_index.txt",
    "release/readiness/public_msl_scripting.txt",
    "reverse-engineering/RE-INDEX.md",
    "reverse-engineering/public-assets-and-modding.md",
    "reverse-engineering/public-save-options.md",
    "reverse-engineering/public-static-contracts.md",
    "reverse-engineering/game-assets/msl-scripting.md",
    "roadmap/ROADMAP-INDEX.md",
    "roadmap/public-roadmap.md",
}
MATERIALIZED_PUBLIC_SOURCES = {
    ".gitignore": "release/readiness/public_gitignore.txt",
    "AGENTS.md": "release/readiness/public_AGENTS.md",
    "CURRENT_CAPABILITIES.md": "release/readiness/public_CURRENT_CAPABILITIES.txt",
    "lore-book/BOOK.md": "release/readiness/public_lore_book_BOOK.txt",
    "lore-book/Start-Here.md": "release/readiness/public_lore_book_Start-Here.txt",
    "lore-book/lore/_index.md": "release/readiness/public_lore_book_lore_index.txt",
    "lore/_index.md": "release/readiness/public_lore_index.txt",
    "reverse-engineering/RE-INDEX.md": "release/readiness/public_RE_INDEX.txt",
    "reverse-engineering/game-assets/msl-scripting.md": "release/readiness/public_msl_scripting.txt",
    "reverse-engineering/quick-reference/_index.md": "release/readiness/public_quick_reference_index.txt",
    "roadmap/ROADMAP-INDEX.md": "release/readiness/public_ROADMAP_INDEX.txt",
    "roadmap/winui-ui-ux-redesign-radar.md": "release/readiness/public_winui_ui_ux_redesign_radar.txt",
    "roadmap/mod-patch-runtime-rebuild-register.md": "release/readiness/public_mod_patch_runtime_rebuild_register.txt",
    "lore-book/roadmap/mod-patch-runtime-rebuild-register.md": "release/readiness/public_lore_book_mod_patch_runtime_rebuild_register.txt",
    "package.json": "release/readiness/public_package.json",
}

ALLOWED_PUBLIC_SUBAGENT_ROOTS = {
    "md-link-check",
}

ROOT_DENY_PREFIXES = (
    ".github/workflows/",
    ".codex/",
    "archive/",
    "game/",
    "media/",
    "save-attempts/",
    "GameProfiles/",
    "PatchBench/",
    "subagents/",
    "release/artifacts/",
    "release/out/",
    "discord_channel_dumps/",
    "wave_online_audit/",
    "wave_online_audit2/",
    "reverse-engineering/binary-analysis/scratch/",
    "lore-book/reverse-engineering/binary-analysis/scratch/",
)
CONTAIN_DENY = (
    "GameProfiles/",
    "PatchBench/",
    "release/readiness/private_runtime_evidence/",
)
EXACT_DENY = {
    "AGENTS.md",
    "USER_SANITY_CHECK.md",
    "onslaught_codex_directive.md",
    "MCP_DEBUGGING_OPTIONS.md",
    "MCP_LIMITATIONS.md",
    "developer_agent_state.json",
    "documentation_agent_state.json",
    "re_orchestrator_state.json",
    "goal.md",
    "goal.policy.md",
    "release/readiness/private_public_payload_text_guard_patterns.json",
}
EXACT_FILE_DENY = {
    "onslaught-profile-manifest.json",
    "onslaught-control-options-manifest.json",
    "onslaught-music-replacement-manifest.json",
}
DENY_SUFFIXES = (
    ".aya",
    ".bea",
    ".bes",
    ".bik",
    ".bin",
    ".dds",
    ".dll",
    ".exe",
    ".fbx",
    ".gzf",
    ".mp3",
    ".mp4",
    ".ogg",
    ".trx",
    ".vid",
    ".wav",
)

TEXT_SUFFIXES = {
    ".cjs",
    ".cs",
    ".css",
    ".html",
    ".java",
    ".json",
    ".jsonc",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
    ".tsv",
    ".txt",
    ".xml",
    ".xaml",
    ".yml",
    ".yaml",
}

PUBLIC_EVIDENCE_FIELD_SUFFIXES = {
    ".html",
    ".json",
    ".jsonc",
    ".md",
    ".tsv",
    ".txt",
    ".xaml",
    ".xml",
    ".yml",
    ".yaml",
}

TEXT_PATTERNS = (
    (
        "private-rfc1918-ipv4-address",
        re.compile(
            r"\b(?:10\.(?:25[0-5]|2[0-4]\d|1?\d?\d)\.(?:25[0-5]|2[0-4]\d|1?\d?\d)\.(?:25[0-5]|2[0-4]\d|1?\d?\d)|172\.(?:1[6-9]|2\d|3[01])\.(?:25[0-5]|2[0-4]\d|1?\d?\d)\.(?:25[0-5]|2[0-4]\d|1?\d?\d)|192\.168\.(?:25[0-5]|2[0-4]\d|1?\d?\d)\.(?:25[0-5]|2[0-4]\d|1?\d?\d))\b"
        ),
    ),
    ("absolute-user-path", re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s`'\"<>)]+")),
    ("wsl-user-path", re.compile(r"/mnt/[a-z]/Users/[^\\/\s`'\"<>)]+", re.IGNORECASE)),
    ("file-url-user-path", re.compile(r"file:/+[A-Za-z]:/Users/[^\\/\s`'\"<>)]+", re.IGNORECASE)),
    (
        "private-repo-name-or-url",
        re.compile(
            r"\b(?:"
            + re.escape("Onslaught-Career-Editor-" + "private")
            + r"|github\.com/dlprentice/"
            + re.escape("Onslaught-Career-Editor-" + "private")
            + r")\b",
            re.IGNORECASE,
        ),
    ),
    ("sandbox-attachment-path", re.compile("sandbox:" + r"/mnt/data/", re.IGNORECASE)),
    (
        "ignored-runtime-artifact-path",
        re.compile(
            r"subagents[\\/](?:winui-safe-copy-live-runtime|winui-visual-qa)[\\/][A-Za-z0-9._-]+[\\/]",
            re.IGNORECASE,
        ),
    ),
    (
        "ignored-runtime-artifact-path-expression",
        re.compile(
            r"(?:\b(?:joinpath|artifact)\(\s*['\"]subagents['\"]\s*,\s*['\"](?:winui-safe-copy-live-runtime|winui-visual-qa)['\"]|ROOT\s*/\s*['\"]subagents['\"]\s*/\s*['\"](?:winui-safe-copy-live-runtime|winui-visual-qa)['\"])",
            re.IGNORECASE,
        ),
    ),
    (
        "private-runtime-helper-import",
        re.compile(
            r"^\s*(?:import|from)\s+winui_safe_copy_online_host_authority_(?:runtime|n_slot_runtime|secure_n_slot_runtime|state_authority)",
            re.IGNORECASE | re.MULTILINE,
        ),
    ),
    ("restricted-corpus-proof-taxonomy", re.compile(r"\b" + "private" + r"[- ]" + "corpus" + r"\b", re.IGNORECASE)),
    ("runtime-capture-artifact-path", re.compile("capture/" + "safe-copy-frame", re.IGNORECASE)),
    ("runtime-smoke-artifact-name", re.compile(re.escape("live-safe-copy-runtime-" + "smoke.json"), re.IGNORECASE)),
    (
        "runtime-process-or-window-id",
        re.compile(r"\b(?:live process|foreground process id|main-window handle)\b[^\n]{0,40}`?(?:0x[0-9a-f]+|\d{3,})`?", re.IGNORECASE),
    ),
    ("runtime-frame-sha", re.compile(r"\b(?:frame|last-frame|title/menu frame)\b[^\n]{0,80}\bSHA-256\b", re.IGNORECASE)),
    (
        "local-ghidra-backup-root",
        re.compile(r"\b[A-Za-z]:[\\/]+GhidraBackups[\\/][^\s`'\"<>)\]]*", re.IGNORECASE),
    ),
    (
        "local-runtime-proof-archive-root",
        re.compile(
            r"\b[A-Za-z]:[\\/]+[A-Za-z0-9._ -]*RuntimeProofArchive(?:[\\/][^\s`'\"<>)\]]*)?",
            re.IGNORECASE,
        ),
    ),
    (
        "embedded-base64-data-url",
        re.compile(r"data:[a-z0-9.+-]+/[a-z0-9.+-]+;base64,[a-z0-9+/=\r\n]{80,}", re.IGNORECASE),
    ),
)

CONCRETE_SUBAGENT_ROOT_PATTERN = re.compile(
    r"\bsubagents[\\/]+([A-Za-z0-9._-]+)(?=$|[\\/`\s'\"<>)\],.;:])",
    re.IGNORECASE,
)
CONCRETE_SUBAGENT_SCAN_PREFIXES = (
    "CURRENT_CAPABILITIES.md",
    "README",
    "CONTRIBUTING",
    "COLLABORATION",
    "SECURITY",
    "RELEASE_SCOPE",
    "lore/",
    "lore-book/",
    "patches/catalog/",
    "release/readiness/",
    "reverse-engineering/",
    "roadmap/",
    "tools/",
)
CONCRETE_SUBAGENT_SCAN_EXEMPT_PATHS = {
    "tools/public_allowlist_safety_check.py",
    "tools/repo_text_hygiene_check.py",
    "tools/repo_text_hygiene_check_test.py",
}

PACKAGE_SCRIPT_PATH_PATTERN = re.compile(
    r"(?:^|[;&|()\s\"'])((?:\.?[\\/]+)?tools[\\/][A-Za-z0-9._+\-\\/]+?\.(?:py|ps1|sh|cjs|mjs|js))(?=$|[;&|()\s\"'])",
    re.IGNORECASE,
)

PUBLIC_EVIDENCE_FIELD_PATTERNS = (
    (
        "runtime-process-id-field",
        re.compile(
            r"\b(?:targetProcessId|cdbProcessId|processId|process-id|cdb process id)\b\s*[:=]\s*`?\d{3,}`?",
            re.IGNORECASE,
        ),
    ),
    (
        "runtime-cdb-log-path-field",
        re.compile(
            r"\b(?:cdbLogPath|cdb log path)\b\s*[:=]\s*`?[^`'\"<>\r\n]+?\.log\b",
            re.IGNORECASE,
        ),
    ),
)

PUBLIC_PATCH_SURFACE_PRIVATE_REF_PREFIXES = (
    "CURRENT_CAPABILITIES.md",
    "OnslaughtCareerEditor.AppCore/",
    "OnslaughtCareerEditor.AppCore.Tests/",
    "OnslaughtCareerEditor.WinUI/",
    "OnslaughtCareerEditor.UiTests/",
    "patches/README.md",
    "patches/catalog/",
    "release/readiness/public_CURRENT_CAPABILITIES.txt",
    "release/readiness/public_mod_patch_runtime_rebuild_register.txt",
    "release/readiness/public_lore_book_mod_patch_runtime_rebuild_register.txt",
    "release/readiness/public_package.json",
    "roadmap/mod-patch-runtime-rebuild-register.md",
    "lore-book/roadmap/mod-patch-runtime-rebuild-register.md",
)
PUBLIC_PATCH_SURFACE_PRIVATE_REF_PATTERNS = (
    ("private-readiness-note-reference", re.compile(r"release/readiness/" + r"winui_[A-Za-z0-9._-]+\.md", re.IGNORECASE)),
    ("private-readiness-label-reference", re.compile(r"\bReadiness:\s*" + r"winui_[A-Za-z0-9._-]+\.md", re.IGNORECASE)),
    ("historical-private-binary-name", re.compile(r"\b(?:" + r"BEA_" + r"Widescreen\.exe|BEA\.exe\.gzf" + r")\b", re.IGNORECASE)),
    ("historical-private-binary-section", re.compile(r"\b" + r"Historical " + r"private binaries" + r"\b", re.IGNORECASE)),
)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def load_allowlist(path: Path) -> list[tuple[str, str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)

    rows: list[tuple[str, str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if line_number == 1 and cols[:3] == ["path", "class", "reason"]:
            continue
        if len(cols) < 3:
            rows.append((f"<line {line_number}>", "MALFORMED", line))
            continue
        rows.append((normalize_path(cols[0]), cols[1], cols[2]))
    return rows


def is_text_candidate(path: str) -> bool:
    return Path(path).suffix.lower() in TEXT_SUFFIXES


def is_public_evidence_field_candidate(path: str) -> bool:
    return Path(path).suffix.lower() in PUBLIC_EVIDENCE_FIELD_SUFFIXES


def check_allowlist_rows(rows: list[tuple[str, str, str]]) -> list[str]:
    errors: list[str] = []
    row_paths = {path for path, _cls, _reason in rows}
    for required_path in sorted(REQUIRED_PUBLIC_ROWS):
        if required_path not in row_paths:
            errors.append(f"required public payload missing from public allowlist: {required_path}")
    for path, cls, reason in rows:
        lower = path.lower()
        if path.startswith(ROOT_DENY_PREFIXES):
            errors.append(f"deny root family in public allowlist: {path}")
        if any(part in path for part in CONTAIN_DENY):
            errors.append(f"private evidence path in public allowlist: {path}")
        if path in EXACT_DENY:
            errors.append(f"operator/state path in public allowlist: {path}")
        if Path(path).name in EXACT_FILE_DENY:
            errors.append(f"generated runtime manifest in public allowlist: {path}")
        if lower.endswith(DENY_SUFFIXES):
            errors.append(f"binary/save payload suffix in public allowlist: {path}")
        if cls != "R0_ALLOW":
            errors.append(f"non-R0 public allowlist row: {path} => {cls}:{reason}")
    return errors


def find_text_payload_errors(path: str, text: str, require_private_text_guard: bool = False) -> list[str]:
    errors: list[str] = []
    for candidate_text in iter_payload_text_views(text):
        for label, pattern in TEXT_PATTERNS:
            match = pattern.search(candidate_text)
            if match:
                snippet = match.group(0)
                if len(snippet) > 120:
                    snippet = snippet[:117] + "..."
                errors.append(f"{label} in {path}: {snippet}")
                break
        for label, pattern in load_private_text_payload_patterns(require_private_text_guard):
            match = pattern.search(candidate_text)
            if match:
                snippet = match.group(0)
                if len(snippet) > 120:
                    snippet = snippet[:117] + "..."
                errors.append(f"{label} in {path}: {snippet}")
                break
        if should_scan_concrete_subagent_roots(path):
            errors.extend(find_concrete_subagent_root_errors(path, candidate_text))
        if should_scan_public_patch_surface_private_refs(path):
            for label, pattern in PUBLIC_PATCH_SURFACE_PRIVATE_REF_PATTERNS:
                match = pattern.search(candidate_text)
                if match:
                    snippet = match.group(0)
                    if len(snippet) > 120:
                        snippet = snippet[:117] + "..."
                    errors.append(f"{label} in {path}: {snippet}")
                    break
        if is_public_evidence_field_candidate(path):
            for label, pattern in PUBLIC_EVIDENCE_FIELD_PATTERNS:
                match = pattern.search(candidate_text)
                if match:
                    snippet = match.group(0)
                    if len(snippet) > 120:
                        snippet = snippet[:117] + "..."
                    errors.append(f"{label} in {path}: {snippet}")
                    break
    return errors


@lru_cache(maxsize=1)
def load_private_text_payload_guard_config(require_private_text_guard: bool = False) -> dict[str, object]:
    if not PRIVATE_TEXT_PAYLOAD_GUARD.is_file():
        if require_private_text_guard:
            raise FileNotFoundError(f"missing required private text payload guard config: {PRIVATE_TEXT_PAYLOAD_GUARD}")
        return {"patterns": [], "positiveTests": [], "negativeTests": []}
    try:
        data = json.loads(PRIVATE_TEXT_PAYLOAD_GUARD.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"private text payload guard config parse error: {exc.lineno}:{exc.colno}") from exc
    if not isinstance(data, dict):
        raise ValueError("private text payload guard config must be a JSON object")
    return data


@lru_cache(maxsize=1)
def load_private_text_payload_patterns(
    require_private_text_guard: bool = False,
) -> tuple[tuple[str, re.Pattern[str]], ...]:
    data = load_private_text_payload_guard_config(require_private_text_guard)
    patterns = data.get("patterns", [])
    if not isinstance(patterns, list):
        raise ValueError("private text payload guard patterns must be a list")

    compiled: list[tuple[str, re.Pattern[str]]] = []
    for index, row in enumerate(patterns):
        if not isinstance(row, dict):
            raise ValueError(f"private text payload guard pattern #{index} must be an object")
        label = row.get("label")
        pattern = row.get("pattern")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"private text payload guard pattern #{index} missing label")
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError(f"private text payload guard pattern {label} missing pattern")
        compiled.append((label, re.compile(pattern, re.IGNORECASE)))
    return tuple(compiled)


def should_scan_concrete_subagent_roots(path: str) -> bool:
    if path in CONCRETE_SUBAGENT_SCAN_EXEMPT_PATHS:
        return False
    return path.startswith(CONCRETE_SUBAGENT_SCAN_PREFIXES)


def should_scan_public_patch_surface_private_refs(path: str) -> bool:
    return path.startswith(PUBLIC_PATCH_SURFACE_PRIVATE_REF_PREFIXES)


def find_concrete_subagent_root_errors(path: str, text: str) -> list[str]:
    errors: list[str] = []
    for match in CONCRETE_SUBAGENT_ROOT_PATTERN.finditer(text):
        root = match.group(1).rstrip(".,;:")
        if root in {"", "."}:
            continue
        if root in ALLOWED_PUBLIC_SUBAGENT_ROOTS:
            continue
        snippet = match.group(0)
        if len(snippet) > 120:
            snippet = snippet[:117] + "..."
        errors.append(f"ignored-subagent-evidence-root in {path}: {snippet}")
        break
    return errors


def iter_payload_text_views(text: str) -> list[str]:
    views = [text]
    if "\\" in text:
        normalized = text.replace("\\\\", "\\")
        if normalized != text:
            views.append(normalized)

    decoded = decode_json_strings(text)
    if decoded and decoded not in views:
        views.append(decoded)

    expanded: list[str] = []
    for view in views:
        candidates = [view]
        if "&" in view:
            candidates.append(html.unescape(view))
        if "\\" in view:
            candidates.append(decode_backslash_escapes(view))
        for candidate in candidates:
            if candidate and candidate not in expanded:
                expanded.append(candidate)

    final: list[str] = []
    for view in expanded:
        if view and view not in final:
            final.append(view)
        if needs_unicode_normalization(view):
            normalized_view = normalize_payload_text_view(view)
            if normalized_view and normalized_view not in final:
                final.append(normalized_view)
    return final


BACKSLASH_ESCAPE_PATTERN = re.compile(r"\\(?:u([0-9a-fA-F]{4})|U([0-9a-fA-F]{8})|x([0-9a-fA-F]{2})|([nrt]))")
ZERO_WIDTH_CHARS = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\u2060",
    "\ufeff",
}


def decode_backslash_escapes(text: str) -> str:
    def replacement(match: re.Match[str]) -> str:
        simple_escape = match.group(4)
        if simple_escape is not None:
            return " "
        value = next(group for group in match.groups() if group is not None)
        try:
            return chr(int(value, 16))
        except ValueError:
            return match.group(0)

    return BACKSLASH_ESCAPE_PATTERN.sub(replacement, text)


def normalize_payload_text_view(text: str) -> str:
    without_zero_width = "".join(char for char in text if char not in ZERO_WIDTH_CHARS)
    return unicodedata.normalize("NFKC", without_zero_width)


def needs_unicode_normalization(text: str) -> bool:
    return any(ord(char) > 127 or char in ZERO_WIDTH_CHARS for char in text)


def decode_json_strings(text: str) -> str | None:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None

    values: list[str] = []

    def collect(value: object) -> None:
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, dict):
            for item in value.values():
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(parsed)
    return "\n".join(values)


def check_text_payloads(
    rows: list[tuple[str, str, str]],
    payload_root: Path = ROOT,
    require_private_text_guard: bool = False,
) -> list[str]:
    errors: list[str] = []
    for path, _cls, _reason in rows:
        if not is_text_candidate(path):
            continue
        full_path = public_payload_source_path(path, payload_root)
        if not full_path.is_file():
            errors.append(f"allowlisted file missing from working tree: {path}")
            continue
        text = full_path.read_text(encoding="utf-8", errors="replace")
        errors.extend(find_text_payload_errors(path, text, require_private_text_guard))
    return errors


def public_payload_source_path(path: str, payload_root: Path = ROOT) -> Path:
    materialized_source = MATERIALIZED_PUBLIC_SOURCES.get(path)
    if materialized_source:
        template = payload_root / materialized_source
        if template.is_file():
            return template
    return payload_root / path


def iter_python_imports(path: str, text: str, root: Path = ROOT) -> list[str]:
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        return [f"<syntax-error:{exc.lineno or 0}>"]

    path_bindings = collect_static_path_bindings(tree, root, path)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    imports.append(alias.name)
                    imports.append(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level != 0:
                imports.append("<relative-import>")
                continue
            if not node.module:
                continue
            imports.append(node.module)
            imports.append(node.module.split(".", 1)[0])
            for alias in node.names:
                if alias.name != "*":
                    imports.append(f"{node.module}.{alias.name}")
        elif isinstance(node, ast.Call):
            dynamic_name = get_dynamic_import_name(node, path_bindings, root)
            if dynamic_name:
                imports.append(dynamic_name)
                if not dynamic_name.startswith("<"):
                    imports.append(dynamic_name.split(".", 1)[0])
    return sorted(set(imports))


def collect_static_path_bindings(tree: ast.AST, root: Path, source_path: str) -> dict[str, Path]:
    bindings: dict[str, Path] = {}
    current_file = root / source_path
    for node in getattr(tree, "body", []):
        if not isinstance(node, ast.Assign):
            continue
        value = eval_static_path_expr(node.value, bindings, root, current_file)
        if value is None:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                bindings[target.id] = value
    return bindings


def eval_static_path_expr(node: ast.AST, bindings: dict[str, Path], root: Path, current_file: Path) -> Path | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return Path(node.value)
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            return current_file
        return bindings.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = eval_static_path_expr(node.left, bindings, root, current_file)
        right_path = eval_static_path_expr(node.right, bindings, root, current_file)
        if left is None or right_path is None:
            return None
        return left / right_path
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "Path" and len(node.args) == 1:
            return eval_static_path_expr(node.args[0], bindings, root, current_file)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "resolve":
            value = eval_static_path_expr(node.func.value, bindings, root, current_file)
            return value.resolve() if value is not None else None
    if isinstance(node, ast.Attribute):
        value = eval_static_path_expr(node.value, bindings, root, current_file)
        if value is None:
            return None
        if node.attr == "parent":
            return value.parent
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and node.value.attr == "parents":
        value = eval_static_path_expr(node.value.value, bindings, root, current_file)
        if value is None:
            return None
        index_node = node.slice
        if isinstance(index_node, ast.Constant) and isinstance(index_node.value, int):
            try:
                return value.parents[index_node.value]
            except IndexError:
                return None
    return None


def repo_relative_dynamic_path(value: Path, root: Path) -> str | None:
    if not value.is_absolute():
        value = root / value
    try:
        return value.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def get_dynamic_import_name(node: ast.Call, path_bindings: dict[str, Path], root: Path) -> str | None:
    function_name = ""
    if isinstance(node.func, ast.Name):
        function_name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        function_name = node.func.attr

    dynamic_import_functions = {
        "__import__",
        "import_module",
        "run_module",
        "spec_from_file_location",
    }
    if function_name not in dynamic_import_functions or not node.args:
        return None
    if function_name == "spec_from_file_location":
        if len(node.args) < 2:
            return "<dynamic-import>"
        dynamic_path = eval_static_path_expr(node.args[1], path_bindings, root, root)
        if dynamic_path is None:
            return "<dynamic-import>"
        repo_path = repo_relative_dynamic_path(dynamic_path, root)
        if repo_path and repo_path.endswith(".py"):
            return f"<path:{repo_path}>"
        return "<dynamic-import>"
    first_arg = node.args[0]
    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
        return first_arg.value
    return "<dynamic-import>"


def resolve_local_python_import(import_name: str, root: Path) -> str | None:
    if import_name in {"<relative-import>", "<dynamic-import>"}:
        return import_name
    if import_name.startswith("<path:") and import_name.endswith(">"):
        return import_name.removeprefix("<path:").removesuffix(">")
    module_parts = [part for part in import_name.split(".") if part]
    if not module_parts:
        return None
    module_path = Path(*module_parts)
    candidates = [
        root / "tools" / f"{import_name}.py",
        root / "tools" / module_path.with_suffix(".py"),
        root / f"{import_name}.py",
        root / module_path.with_suffix(".py"),
        root / module_path / "__init__.py",
    ]
    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate.relative_to(root).as_posix()
        except OSError:
            continue
    return None


def check_python_import_closure(rows: list[tuple[str, str, str]], root: Path = ROOT) -> list[str]:
    public_paths = {path for path, cls, _reason in rows if cls == "R0_ALLOW"}
    errors: list[str] = []
    for path, cls, _reason in rows:
        if cls != "R0_ALLOW" or not path.endswith(".py"):
            continue
        full_path = root / path
        if not full_path.is_file():
            continue
        text = full_path.read_text(encoding="utf-8", errors="replace")
        for import_name in iter_python_imports(path, text, root):
            if import_name.startswith("<syntax-error:"):
                errors.append(f"python import parse error in {path}: {import_name}")
                continue
            dependency = resolve_local_python_import(import_name, root)
            if dependency in {"<relative-import>", "<dynamic-import>"}:
                errors.append(f"{path} uses unresolved public-candidate import: {import_name}")
                continue
            if dependency is None or dependency == path:
                continue
            if dependency not in public_paths:
                errors.append(f"{path} imports non-public local dependency: {dependency}")
    return errors


def check_public_package_script_closure(rows: list[tuple[str, str, str]], root: Path = ROOT) -> list[str]:
    public_paths = {path for path, cls, _reason in rows if cls == "R0_ALLOW"}
    errors: list[str] = []
    for path, cls, _reason in rows:
        if cls != "R0_ALLOW" or Path(path).name not in {"package.json", "public_package.json"}:
            continue
        full_path = root / path
        if not full_path.is_file():
            continue
        try:
            package = json.loads(full_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"public package script closure parse error in {path}: {exc.lineno}:{exc.colno}")
            continue
        scripts = package.get("scripts", {})
        if not isinstance(scripts, dict):
            continue
        for script_name, command in sorted(scripts.items()):
            if not isinstance(command, str):
                continue
            if "--allow-current-user-cert-trust" in command:
                errors.append(f"{path} script {script_name} exposes public trust-store mutation flag")
            for dependency in iter_script_tool_paths(command):
                if dependency not in public_paths:
                    errors.append(f"{path} script {script_name} references non-public local tool: {dependency}")
    return errors


def iter_script_tool_paths(command: str) -> list[str]:
    paths: list[str] = []
    for view in iter_payload_text_views(command):
        for match in PACKAGE_SCRIPT_PATH_PATTERN.finditer(view):
            paths.append(normalize_path(match.group(1)).removeprefix("./"))
    return sorted(set(paths))


def run_self_test(require_private_text_guard: bool = False) -> int:
    def j(*parts: str) -> str:
        return "".join(parts)

    cases = [
        (
            "windows ignored runtime artifact path",
            j(r"py -3 tools\checker.py subagents", "\\", "winui-safe-copy-live-runtime", r"\focus1\proof.json"),
            "ignored-runtime-artifact-path",
        ),
        (
            "forward ignored runtime artifact path",
            j("py -3 tools/checker.py subagents/", "winui-visual-qa", "/focus1/proof.json"),
            "ignored-runtime-artifact-path",
        ),
        (
            "json escaped ignored runtime artifact path",
            j(r'{"script":"py -3 tools\\checker.py subagents\\', "winui-safe-copy-live-runtime", r'\\focus1\\proof.json"}'),
            "ignored-runtime-artifact-path",
        ),
        (
            "split ignored runtime artifact path expression",
            j('ROOT / "subagents" / "', "winui-safe-copy-live-runtime", '" / stamp'),
            "ignored-runtime-artifact-path-expression",
        ),
        (
            "joinpath ignored runtime artifact path expression",
            j('artifact("subagents", "', "winui-safe-copy-live-runtime", '", "focus1", runtime_artifact_name)'),
            "ignored-runtime-artifact-path-expression",
        ),
        (
            "private runtime checker import",
            j("import ", "winui_safe_copy_online_host_authority_", "runtime_executor_check as executor"),
            "private-runtime-helper-import",
        ),
        (
            "private LAN literal",
            j("Bound private host ", "192.168.", "1.100 during a local proof."),
            "private-rfc1918-ipv4-address",
        ),
        (
            "runtime smoke artifact filename",
            j("Collected ", "live-safe-copy-runtime-", "smoke.json from a private copied-game run."),
            "runtime-smoke-artifact-name",
        ),
        (
            "runtime process id",
            j("Observed foreground ", "process id `", "12345", "` during the private smoke."),
            "runtime-process-or-window-id",
        ),
        (
            "runtime processId field",
            j("processId: ", "12345"),
            "runtime-process-id-field",
        ),
        (
            "runtime process-id field",
            j("process-id: ", "12345"),
            "runtime-process-id-field",
        ),
        (
            "runtime cdb process id field",
            j("cdb process id: ", "12345"),
            "runtime-process-id-field",
        ),
        (
            "runtime targetProcessId field",
            j("targetProcessId: ", "12345"),
            "runtime-process-id-field",
        ),
        (
            "runtime cdbProcessId field",
            j("cdbProcessId: ", "12345"),
            "runtime-process-id-field",
        ),
        (
            "runtime cdbLogPath field",
            r"cdbLogPath: C:\tmp\cdb.log",
            "runtime-cdb-log-path-field",
        ),
        (
            "runtime CDB log path field",
            r"CDB log path: C:\tmp\cdb.log",
            "runtime-cdb-log-path-field",
        ),
        (
            "local Ghidra backup root",
            r"Verified backup root " + "G:" + r"\Ghidra" + "Backups" + r"\BEA_20260607_verified",
            "local-ghidra-backup-root",
        ),
        (
            "wsl private user path",
            j("/mnt/c/Users/", "operator", "/source/Onslaught-Career-Editor-", "private"),
            "wsl-user-path",
        ),
        (
            "private repository name",
            j("https://github.com/dlprentice/Onslaught-Career-Editor-", "private", "/pull/1"),
            "private-repo-name-or-url",
        ),
        (
            "temporary local Ghidra backup root",
            r"Temporary backup root " + "D:" + r"\Ghidra" + "Backups" + r"\BEA_20260621_verified",
            "local-ghidra-backup-root",
        ),
        (
            "local runtime proof archive root",
            r"Archive root " + "R:" + r"\ExampleRuntimeProofArchive" + r"\runtime-proof-set",
            "local-runtime-proof-archive-root",
        ),
        (
            "generic ignored subagent evidence root",
            j(r"See subagents", "\\", r"goodies-input-observer-runtime-2026-05-08\proof.json for the private proof."),
            "ignored-subagent-evidence-root",
        ),
    ]
    failures: list[str] = []
    for name, text, expected_label in cases:
        synthetic_path = "release/readiness/synthetic.md" if expected_label == "ignored-subagent-evidence-root" else "synthetic.md"
        errors = find_text_payload_errors(synthetic_path, text, require_private_text_guard)
        if not any(error.startswith(expected_label) for error in errors):
            failures.append(f"{name}: expected {expected_label}, got {errors or 'no errors'}")
    allowed_subagent_errors = find_text_payload_errors(
        "release/readiness/synthetic.md",
        "The markdown-link checker writes ignored reports under subagents/md-link-check.",
        require_private_text_guard,
    )
    if any(error.startswith("ignored-subagent-evidence-root") for error in allowed_subagent_errors):
        failures.append(f"allowed subagent root guard: expected md-link-check to pass, got {allowed_subagent_errors}")
    guard_config = load_private_text_payload_guard_config(require_private_text_guard)
    private_guard_patterns_present = bool(guard_config.get("patterns"))
    for row in guard_config.get("positiveTests", []):
        if not isinstance(row, dict):
            failures.append(f"private text payload guard positive test: expected object, got {row!r}")
            continue
        name = row.get("name")
        text = row.get("text")
        expected_label = row.get("expectedLabel")
        if not isinstance(name, str) or not isinstance(text, str) or not isinstance(expected_label, str):
            failures.append(f"private text payload guard positive test malformed: {row!r}")
            continue
        errors = find_text_payload_errors("release/readiness/synthetic.md", text, require_private_text_guard)
        if not any(error.startswith(expected_label) for error in errors):
            failures.append(f"{name}: expected {expected_label}, got {errors or 'no errors'}")
    for row in guard_config.get("negativeTests", []):
        if not isinstance(row, dict):
            failures.append(f"private text payload guard negative test: expected object, got {row!r}")
            continue
        name = row.get("name")
        text = row.get("text")
        if not isinstance(name, str) or not isinstance(text, str):
            failures.append(f"private text payload guard negative test malformed: {row!r}")
            continue
        errors = find_text_payload_errors("release/readiness/synthetic.md", text, require_private_text_guard)
        private_errors = [error for error in errors if error.startswith("private-")]
        if private_errors:
            failures.append(f"{name}: expected no private text payload guard error, got {private_errors}")

    with tempfile.TemporaryDirectory() as tmp:
        temp_root = Path(tmp)
        tools_dir = temp_root / "tools"
        tools_dir.mkdir()
        (tools_dir / "public_tool.py").write_text("import private_helper\n", encoding="utf-8")
        (tools_dir / "public_dynamic.py").write_text(
            "import importlib\nimportlib.import_module('private_helper')\n",
            encoding="utf-8",
        )
        (tools_dir / "public_spec.py").write_text(
            "import importlib.util\n"
            "from pathlib import Path\n"
            "ROOT = Path(__file__).resolve().parents[1]\n"
            "MODULE_PATH = ROOT / 'tools' / 'private_helper.py'\n"
            "importlib.util.spec_from_file_location('private_helper', MODULE_PATH)\n",
            encoding="utf-8",
        )
        (tools_dir / "public_relative.py").write_text("from . import private_helper\n", encoding="utf-8")
        (tools_dir / "private_helper.py").write_text("VALUE = 1\n", encoding="utf-8")
        package_dir = temp_root / "package"
        package_dir.mkdir()
        (package_dir / "public_dotted.py").write_text("from package import private_helper\n", encoding="utf-8")
        (package_dir / "private_helper.py").write_text("VALUE = 1\n", encoding="utf-8")
        closure_errors = check_python_import_closure(
            [
                ("tools/public_tool.py", "R0_ALLOW", "default"),
                ("tools/public_dynamic.py", "R0_ALLOW", "default"),
                ("tools/public_spec.py", "R0_ALLOW", "default"),
                ("tools/public_relative.py", "R0_ALLOW", "default"),
                ("package/public_dotted.py", "R0_ALLOW", "default"),
            ],
            temp_root,
        )
        if not any("imports non-public local dependency: tools/private_helper.py" in error for error in closure_errors):
            failures.append(f"python import closure: expected private helper failure, got {closure_errors or 'no errors'}")
        if not any("package/public_dotted.py imports non-public local dependency: package/private_helper.py" in error for error in closure_errors):
            failures.append(f"python dotted import closure: expected package helper failure, got {closure_errors or 'no errors'}")
        if not any("tools/public_dynamic.py imports non-public local dependency: tools/private_helper.py" in error for error in closure_errors):
            failures.append(f"python dynamic import closure: expected dynamic helper failure, got {closure_errors or 'no errors'}")
        if not any("tools/public_spec.py imports non-public local dependency: tools/private_helper.py" in error for error in closure_errors):
            failures.append(f"python spec import closure: expected dynamic file helper failure, got {closure_errors or 'no errors'}")
        if not any("tools/public_relative.py uses unresolved public-candidate import: <relative-import>" in error for error in closure_errors):
            failures.append(f"python relative import closure: expected fail-closed relative import, got {closure_errors or 'no errors'}")
        try:
            resolve_local_python_import("x." + ("y" * 320), temp_root)
        except OSError as exc:
            failures.append(f"python long import closure: expected long synthetic path to be ignored, got {exc!r}")
        (temp_root / "package.json").write_text(
            json.dumps(
                {
                    "scripts": {
                        "public-tool": r"py -3 tools\public_tool.py",
                        "private-tool": r"py -3 tools\private_helper.py",
                        "trusted-install": r"py -3 tools\public_tool.py --allow-current-user-cert-trust",
                    }
                }
            ),
            encoding="utf-8",
        )
        package_errors = check_public_package_script_closure(
            [
                ("package.json", "R0_ALLOW", "default"),
                ("tools/public_tool.py", "R0_ALLOW", "default"),
            ],
            temp_root,
        )
        if not any("package.json script private-tool references non-public local tool: tools/private_helper.py" in error for error in package_errors):
            failures.append(f"package script closure: expected private helper failure, got {package_errors or 'no errors'}")
        if not any("package.json script trusted-install exposes public trust-store mutation flag" in error for error in package_errors):
            failures.append(f"package script trust flag guard: expected trusted install failure, got {package_errors or 'no errors'}")
        required_errors = check_allowlist_rows(
            [
                ("README.MD", "R0_ALLOW", "default"),
                ("README.RELEASE.md", "R0_ALLOW", "default"),
                ("RELEASE_SCOPE_AND_TEST_COMMANDS.md", "R0_ALLOW", "default"),
                ("release/readiness/public_package.json", "R0_ALLOW", "default"),
            ]
        )
        if not any("required public payload missing from public allowlist: CONTRIBUTING.md" in error for error in required_errors):
            failures.append(f"required public payload guard: expected CONTRIBUTING.md failure, got {required_errors or 'no errors'}")
        if not any("required public payload missing from public allowlist: SECURITY.md" in error for error in required_errors):
            failures.append(f"required public payload guard: expected SECURITY.md failure, got {required_errors or 'no errors'}")
        private_goal_errors = check_allowlist_rows(
            [
                ("goal.policy.md", "R0_ALLOW", "default"),
                ("goal.md", "R0_ALLOW", "default"),
            ]
        )
        if not any("operator/state path in public allowlist: goal.policy.md" in error for error in private_goal_errors):
            failures.append(f"goal policy deny guard: expected goal.policy.md failure, got {private_goal_errors or 'no errors'}")
        guard_config_rel = PRIVATE_TEXT_PAYLOAD_GUARD.relative_to(ROOT).as_posix()
        guard_config_errors = check_allowlist_rows([(guard_config_rel, "R0_ALLOW", "default")])
        if not any(f"operator/state path in public allowlist: {guard_config_rel}" in error for error in guard_config_errors):
            failures.append(
                f"private text payload guard config deny guard: expected {guard_config_rel} failure, "
                f"got {guard_config_errors or 'no errors'}"
            )
        suffix_errors = check_allowlist_rows(
            [
                ("tests_shared/fixtures/gold_career_save.bin", "R0_ALLOW", "default"),
                ("tools/ExampleProbe.java", "R0_ALLOW", "default"),
            ]
        )
        if not any("binary/save payload suffix in public allowlist: tests_shared/fixtures/gold_career_save.bin" in error for error in suffix_errors):
            failures.append(f"binary suffix guard: expected .bin failure, got {suffix_errors or 'no errors'}")
        if not is_text_candidate("tools/ExampleProbe.java"):
            failures.append("java text candidate guard: expected .java to be scanned as text")

    if private_guard_patterns_present:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            materialized_template = temp_root / MATERIALIZED_PUBLIC_SOURCES["AGENTS.md"]
            materialized_template.parent.mkdir(parents=True, exist_ok=True)
            materialized_template.write_text(j("Use ", "Gr", "ok", " Build", " for release review.\n"), encoding="utf-8")
            materialized_errors = check_text_payloads(
                [("AGENTS.md", "R0_ALLOW", "default")],
                temp_root,
                require_private_text_guard,
            )
            expected_materialized_label = j("private-consult-topology-", "gr", "ok", "-build")
            if not any(error.startswith(expected_materialized_label) for error in materialized_errors):
                failures.append(
                    f"materialized private topology guard: expected AGENTS.md template failure, "
                    f"got {materialized_errors or 'no errors'}"
                )

    if failures:
        print("Public allowlist safety self-test: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Public allowlist safety self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public allowlist safety")
    parser.add_argument(
        "--allowlist",
        default=str(ALLOWLIST.relative_to(ROOT)),
        help="Allowlist TSV path relative to repo root",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in pattern tests")
    parser.add_argument(
        "--payload-root",
        default=str(ROOT),
        help="Root containing the public payload to scan; defaults to this repo root.",
    )
    parser.add_argument(
        "--require-private-text-guard",
        action="store_true",
        help="Fail if the private text-payload guard config is unavailable.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test(args.require_private_text_guard)

    payload_root = Path(args.payload_root).resolve()
    rows = load_allowlist(payload_root / args.allowlist)
    errors = check_allowlist_rows(rows)
    errors.extend(check_text_payloads(rows, payload_root, args.require_private_text_guard))
    errors.extend(check_python_import_closure(rows))
    errors.extend(check_public_package_script_closure(rows))

    if errors:
        print("Public allowlist safety check: FAIL")
        for error in errors[:200]:
            print(f"- {error}")
        if len(errors) > 200:
            print(f"- ... ({len(errors) - 200} more)")
        return 1

    print("Public allowlist safety check: PASS")
    print(f"Rows checked: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
