#!/usr/bin/env python3
"""Build the short-path offline Lore content pack for the WinUI ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
LORE_BOOK_DIR = "lore-book"
CANONICAL_LORE_DIR = "lore"
LORE_PACK_DIR = "lore-pack"
LORE_SOURCE_NAME = "canonical-lore"
INDEX_FILE_NAME = "onslaught-lore.v1.index.json"
CONTENT_FILE_NAME = "onslaught-lore.v1.jsonl"
SCHEMA = "onslaught-lore-pack.v1"
GITHUB_SOURCE_BLOB_BASE = "https://github.com/dlprentice/Onslaught-Career-Editor/blob/main"
GITHUB_SOURCE_SEARCH_BASE = "https://github.com/dlprentice/Onslaught-Career-Editor/search"
MARKDOWN_LINK_REGEX = re.compile(r"(?P<prefix>\[[^\]]+\]\()(?P<target>[^)]+)(?P<suffix>\))")
MARKDOWN_SUFFIXES = {".md", ".txt"}
SOURCE_DATA_SUFFIXES = {".c", ".csv", ".json", ".jsonl", ".tsv"}
PACKABLE_SUFFIXES = MARKDOWN_SUFFIXES
DENY_SUFFIXES = {
    ".aya",
    ".bea",
    ".bes",
    ".bik",
    ".bytes",
    ".dds",
    ".dmp",
    ".etl",
    ".fbx",
    ".gbf",
    ".gdt",
    ".gpr",
    ".gzf",
    ".mp3",
    ".mp4",
    ".raw",
    ".trx",
    ".vid",
    ".wav",
}
DENY_NAMES = {
    "bea.exe",
    "bea.exe.original.backup",
    "defaultoptions.bea",
}
TITLE_REGEX = re.compile(r"^\s*#\s+(?P<title>.+?)\s*$", re.MULTILINE)
DOCUMENT_ID_REGEX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
LOCAL_PATH_REDACTIONS = (
    (re.compile(r"https?://(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|127\.\d{1,3}\.\d{1,3}\.\d{1,3}|localhost)(?::\d+)?(?:/[^\s<>()\]]*)?", re.IGNORECASE), "maintainer-local endpoint"),
    (re.compile(r"\bC:\\Users\\[^\\]+\\source\\Onslaught-Career-Editor-private(?:\\{1,2}[^\r\n`<>()\]]*)?", re.IGNORECASE), "maintainer-local former private checkout"),
    (re.compile(r"\bC:\\Users\\[^\\]+\\source\\Onslaught-Career-Editor(?:\\{1,2}[^\r\n`<>()\]]*)?", re.IGNORECASE), "maintainer-local public checkout"),
    (re.compile(r"\bC:\\Users\\[^\\]+\\Ghidra\\Projects\\BEA(?:\.gpr|\.rep)?\\?", re.IGNORECASE), "maintainer-local Ghidra BEA project"),
    (re.compile(r"\bC:\\Users\\[^\\]+\\Ghidra\\?", re.IGNORECASE), "maintainer-local Ghidra root"),
    (re.compile(r"\b[A-Z]:\\{1,2}GhidraBackups(?:\\{1,2}[^\r\n`<>()\]]*)?", re.IGNORECASE), "maintainer-local Ghidra backup root"),
    (re.compile(r"\b[A-Z]:\\{1,2}OnslaughtRuntimeProofArchive(?:\\{1,2}[^\r\n`<>()\]]*)?", re.IGNORECASE), "maintainer-local runtime proof archive"),
    (re.compile(r"\b[A-Z]:\\[^\r\n`<>()\]]+", re.IGNORECASE), "maintainer-local Windows path"),
    (re.compile(r"\b[A-Z]:\\", re.IGNORECASE), "maintainer-local external drive"),
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def title_for(relative_path: str, content: str) -> str:
    match = TITLE_REGEX.search(content)
    if match:
        return match.group("title").strip()
    return Path(relative_path).stem.replace("-", " ").replace("_", " ").strip() or relative_path


def code_fence_for(content: str) -> str:
    fence = "```"
    while fence in content:
        fence += "`"
    return fence


def language_for(path: Path) -> str:
    return {
        ".c": "c",
        ".csv": "csv",
        ".json": "json",
        ".jsonl": "json",
        ".tsv": "tsv",
    }.get(path.suffix.lower(), "text")


def pack_content_for_path(relative_path: str, path: Path, content: str) -> str:
    if path.suffix.lower() in MARKDOWN_SUFFIXES:
        return content

    title = title_for(relative_path, content)
    fence = code_fence_for(content)
    language = language_for(path)
    return f"# {title}\n\nSource file: `{relative_path}`\n\n{fence}{language}\n{content.rstrip()}\n{fence}\n"


def sanitize_pack_content(content: str) -> str:
    sanitized = content
    for pattern, replacement in LOCAL_PATH_REDACTIONS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def split_link_target(target: str) -> tuple[str, str]:
    path_part, separator, anchor = target.partition("#")
    return unquote(path_part), f"#{anchor}" if separator else ""


def is_external_link(target: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target))


def normalize_lore_relative(path: Path) -> str:
    return path.as_posix().lstrip("./")


def validate_lore_pack_relative_path(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Lore pack relativePath is invalid")
    if value.strip() != value:
        raise ValueError("Lore pack relativePath is invalid")
    if "\\" in value:
        raise ValueError("Lore pack relativePath is invalid")
    if value.startswith("/"):
        raise ValueError("Lore pack relativePath is invalid")
    if ":" in value:
        raise ValueError("Lore pack relativePath is invalid")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError("Lore pack relativePath is invalid")

    parts = value.split("/")
    if any(part in {"", ".", ".."} or part.strip() != part for part in parts):
        raise ValueError("Lore pack relativePath is invalid")
    return value


def validate_lore_pack_document_id(value: object) -> str:
    if not isinstance(value, str) or value.strip() != value or not DOCUMENT_ID_REGEX.fullmatch(value):
        raise ValueError("Lore pack document id is invalid")
    return value


def resolve_source_candidate(root: Path, lore_root: Path, source_relative: str, path_part: str) -> Path:
    normalized = path_part.replace("\\", "/")
    if normalized.startswith("/"):
        return root / normalized.lstrip("/")
    return (lore_root / source_relative).parent / normalized


def resolve_existing_candidate(candidate: Path) -> Path | None:
    if candidate.is_file():
        return candidate.resolve()

    if candidate.is_dir():
        for child_name in ("_index.md", "README.md", "index.md"):
            child = candidate / child_name
            if child.is_file():
                return child.resolve()
        return None

    base_without_extension = candidate.with_suffix("") if candidate.suffix else candidate
    candidates = (
        candidate,
        candidate.with_suffix(".md"),
        candidate.with_suffix(".html"),
        candidate.with_suffix(".htm"),
        base_without_extension.with_suffix(".md"),
        base_without_extension.with_suffix(".html"),
        base_without_extension.with_suffix(".htm"),
    )
    for item in candidates:
        if item.is_file():
            return item.resolve()
    return None


def is_relative_to(path: Path, ancestor: Path) -> bool:
    try:
        path.relative_to(ancestor)
        return True
    except ValueError:
        return False


def rewrite_pack_links(
    root: Path,
    lore_root: Path,
    source_relative: str,
    content: str,
    packable_relative_paths: set[str],
) -> str:
    root_resolved = root.resolve()
    lore_root_resolved = lore_root.resolve()

    def replace(match: re.Match[str]) -> str:
        target = match.group("target").strip()
        path_part, anchor = split_link_target(target)
        if not path_part or path_part.startswith("#", 0) or is_external_link(path_part):
            return match.group(0)

        candidate = resolve_source_candidate(root_resolved, lore_root_resolved, source_relative, path_part)
        resolved = resolve_existing_candidate(candidate)
        if resolved is not None and is_relative_to(resolved, lore_root_resolved):
            lore_relative = normalize_lore_relative(resolved.relative_to(lore_root_resolved))
            if lore_relative.lower() in packable_relative_paths:
                return match.group(0)

        if resolved is not None and is_relative_to(resolved, root_resolved):
            repo_relative = resolved.relative_to(root_resolved).as_posix()
            github_url = f"{GITHUB_SOURCE_BLOB_BASE}/{quote(repo_relative, safe='/')}{anchor}"
            return f"{match.group('prefix')}{github_url}{match.group('suffix')}"

        query = quote(path_part.strip("/"), safe="/")
        github_url = f"{GITHUB_SOURCE_SEARCH_BASE}?q={query}"
        return f"{match.group('prefix')}{github_url}{match.group('suffix')}"

    return MARKDOWN_LINK_REGEX.sub(replace, content)


def git_lore_files(root: Path, lore_root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "--", LORE_BOOK_DIR, CANONICAL_LORE_DIR],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git ls-files failed")
    files: list[Path] = []
    for raw in completed.stdout.splitlines():
        path = (root / raw).resolve()
        try:
            path.relative_to(lore_root.resolve())
        except ValueError:
            continue
        if path.is_file():
            files.append(path)
    return files


def filesystem_lore_files(lore_root: Path) -> list[Path]:
    candidates: list[Path] = []
    lore_book_root = lore_root / LORE_BOOK_DIR
    if lore_book_root.is_dir():
        candidates.extend(path for path in lore_book_root.iterdir() if path.is_file())
    canonical_root = lore_root / CANONICAL_LORE_DIR
    if canonical_root.is_dir():
        candidates.extend(path for path in canonical_root.rglob("*") if path.is_file())
    return sorted(candidates)


def collect_lore_documents(root: Path, lore_root: Path, *, use_git: bool) -> list[Path]:
    candidates = git_lore_files(root, lore_root) if use_git else filesystem_lore_files(lore_root)
    documents: list[Path] = []
    for path in sorted(candidates, key=lambda item: item.relative_to(lore_root).as_posix().lower()):
        relative = path.relative_to(lore_root).as_posix()
        relative_parts = PurePosixPath(relative).parts
        if not relative_parts or relative_parts[0] not in {LORE_BOOK_DIR, CANONICAL_LORE_DIR}:
            continue
        lower_name = path.name.lower()
        suffix = path.suffix.lower()
        if lower_name in DENY_NAMES or suffix in DENY_SUFFIXES:
            raise ValueError(f"hard-payload-like Lore source rejected: {relative}")
        if relative_parts[0] == LORE_BOOK_DIR and relative != f"{LORE_BOOK_DIR}/BOOK.md":
            raise ValueError("lore-book contains obsolete mirrored content")
        if suffix in PACKABLE_SUFFIXES:
            documents.append(path)
    return documents


def build_lore_pack(root: Path = ROOT, output_dir: Path | None = None, *, use_git: bool = True) -> dict[str, object]:
    lore_root = root
    if output_dir is None:
        output_dir = root / LORE_PACK_DIR
    if not (root / LORE_BOOK_DIR / "BOOK.md").is_file():
        raise FileNotFoundError("missing Lore entry guide")

    documents = collect_lore_documents(root, lore_root, use_git=use_git)
    if not documents:
        raise RuntimeError("no Lore text documents found")
    packable_relative_paths = {
        validate_lore_pack_relative_path(normalize_lore_relative(path.relative_to(lore_root))).lower()
        for path in documents
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    index_documents: list[dict[str, object]] = []
    content_lines: list[str] = []

    for order, source in enumerate(documents):
        relative_path = validate_lore_pack_relative_path(source.relative_to(lore_root).as_posix())
        raw_content = sanitize_pack_content(source.read_text(encoding="utf-8", errors="replace"))
        if source.suffix.lower() in MARKDOWN_SUFFIXES:
            raw_content = rewrite_pack_links(root, lore_root, relative_path, raw_content, packable_relative_paths)
        content = pack_content_for_path(relative_path, source, raw_content)
        digest = sha256_text(content)
        doc_id = f"doc-{order + 1:06d}"
        row = {
            "id": doc_id,
            "relativePath": relative_path,
            "title": title_for(relative_path, content),
            "sha256": digest,
            "byteLength": len(content.encode("utf-8")),
            "content": content,
        }
        index_documents.append({key: row[key] for key in ("id", "relativePath", "title", "sha256", "byteLength")} | {"order": order})
        content_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))

    index = {
        "schema": SCHEMA,
        "sourceRoot": LORE_SOURCE_NAME,
        "documentCount": len(index_documents),
        "documents": index_documents,
    }
    index_path = output_dir / INDEX_FILE_NAME
    content_path = output_dir / CONTENT_FILE_NAME
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    content_path.write_text("\n".join(content_lines) + "\n", encoding="utf-8", newline="\n")
    return {
        "schema": SCHEMA,
        "documentCount": len(index_documents),
        "indexPath": str(index_path),
        "contentPath": str(content_path),
        "contentSha256": hashlib.sha256(content_path.read_bytes()).hexdigest(),
        "indexSha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
    }


def check_lore_pack(pack_dir: Path) -> dict[str, object]:
    index_path = pack_dir / INDEX_FILE_NAME
    content_path = pack_dir / CONTENT_FILE_NAME
    if not index_path.is_file() or not content_path.is_file():
        raise FileNotFoundError("Lore pack index or content file is missing")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index.get("schema") != SCHEMA:
        raise ValueError("Lore pack schema mismatch")
    expected: dict[str, dict[str, object]] = {}
    indexed_relative_paths: set[str] = set()
    for item_number, item in enumerate(index.get("documents", []), start=1):
        if not isinstance(item, dict):
            raise ValueError(f"index document {item_number} is not an object")
        doc_id = validate_lore_pack_document_id(item.get("id"))
        doc_key = doc_id.lower()
        if doc_key in expected:
            raise ValueError("duplicate document id")
        relative_path = validate_lore_pack_relative_path(item.get("relativePath"))
        relative_key = relative_path.lower()
        if relative_key in indexed_relative_paths:
            raise ValueError("duplicate Lore pack relativePath")
        indexed_relative_paths.add(relative_key)
        item["relativePath"] = relative_path
        expected[doc_key] = item
    if index.get("documentCount") != len(expected):
        raise ValueError("Lore pack documentCount does not match index rows")

    seen: set[str] = set()
    for line_number, line in enumerate(content_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"content row {line_number} is not an object")
        allowed_keys = {"id", "relativePath", "title", "sha256", "byteLength", "content"}
        if set(row) - allowed_keys:
            raise ValueError(f"content row {line_number} has unexpected keys")
        doc_id = validate_lore_pack_document_id(row.get("id"))
        doc_key = doc_id.lower()
        if doc_key not in expected:
            raise ValueError(f"content row {line_number} does not match index")
        if doc_key in seen:
            raise ValueError(f"content row {line_number} duplicates id")
        relative_path = validate_lore_pack_relative_path(row.get("relativePath"))
        expected_row = expected[doc_key]
        if relative_path != expected_row.get("relativePath"):
            raise ValueError(f"content row {line_number} relativePath does not match index")
        content = row.get("content")
        if not isinstance(content, str):
            raise ValueError(f"content row {line_number} is missing text content")
        byte_length = len(content.encode("utf-8"))
        if row.get("byteLength") != byte_length or expected_row.get("byteLength") != byte_length:
            raise ValueError(f"content row {line_number} byteLength mismatch")
        digest = sha256_text(content)
        if digest != row.get("sha256") or digest != expected_row.get("sha256"):
            raise ValueError(f"content row {line_number} hash mismatch")
        if has_unresolved_pack_links(relative_path, content, indexed_relative_paths):
            raise ValueError(f"content row {line_number} has unresolved packed links")
        seen.add(doc_key)
    missing = sorted(set(expected) - seen)
    if missing:
        raise ValueError("Lore pack content is missing rows")
    return {
        "schema": index["schema"],
        "documentCount": len(seen),
        "indexSha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
        "contentSha256": hashlib.sha256(content_path.read_bytes()).hexdigest(),
    }


def has_unresolved_pack_links(source_relative_path: str, content: str, available_paths: set[str]) -> bool:
    for match in MARKDOWN_LINK_REGEX.finditer(content):
        target = match.group("target").strip()
        path_part, _ = split_link_target(target)
        if not path_part or path_part.startswith("#") or is_external_link(path_part):
            continue
        if resolve_pack_link_candidate(source_relative_path, path_part, available_paths) is None:
            return True
    return False


def resolve_pack_link_candidate(source_relative_path: str, target: str, available_paths: set[str]) -> str | None:
    normalized_target = target.replace("\\", "/")
    if normalized_target.startswith("/"):
        candidate = normalize_pack_link_path(normalized_target.lstrip("/"))
    else:
        source_parent = PurePosixPath(source_relative_path).parent.as_posix()
        prefix = "" if source_parent == "." else f"{source_parent}/"
        candidate = normalize_pack_link_path(f"{prefix}{normalized_target}")
    if candidate is None:
        return None

    candidate_path = PurePosixPath(candidate)
    candidate_without_suffix = str(candidate_path.with_suffix("")) if candidate_path.suffix else candidate
    candidates = (
        candidate,
        f"{candidate}.md",
        f"{candidate}.html",
        f"{candidate}/_index.md",
        f"{candidate}/README.md",
        f"{candidate}/index.md",
        f"{candidate_without_suffix}.md",
        f"{candidate_without_suffix}.html",
        f"{candidate_without_suffix}.htm",
    )
    for item in candidates:
        normalized = normalize_pack_link_path(item)
        if normalized is not None and normalized.lower() in available_paths:
            return normalized
    return None


def normalize_pack_link_path(value: str) -> str | None:
    parts: list[str] = []
    for part in value.replace("\\", "/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


class LorePackBuilderTests(unittest.TestCase):
    def test_build_and_check_lore_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            lore_book = root / LORE_BOOK_DIR
            lore_book.mkdir()
            lore = root / CANONICAL_LORE_DIR
            lore.mkdir()
            (lore_book / "BOOK.md").write_text("- [Start](../lore/Start.md)\n", encoding="utf-8")
            (lore / "Start.md").write_text("# Start\n\n[Rows](rows.tsv)\n[Tool](../tools/helper.py)", encoding="utf-8")
            (lore / "rows.tsv").write_text("id\tvalue\n1\tAquila\n", encoding="utf-8")
            (lore / "logic.c").write_text("int main(void) { return 0; }\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools" / "helper.py").write_text("print('helper')\n", encoding="utf-8")

            report = build_lore_pack(root, root / LORE_PACK_DIR, use_git=False)
            checked = check_lore_pack(root / LORE_PACK_DIR)
            content = (root / LORE_PACK_DIR / CONTENT_FILE_NAME).read_text(encoding="utf-8")

            self.assertEqual(report["documentCount"], 2)
            self.assertEqual(checked["documentCount"], 2)
            self.assertNotIn("```tsv", content)
            self.assertNotIn("```c", content)
            self.assertIn("[Rows](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/lore/rows.tsv)", content)
            self.assertIn("[Tool](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/tools/helper.py)", content)

    def test_redacts_maintainer_paths_and_private_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            lore = root / LORE_BOOK_DIR
            lore.mkdir()
            (lore / "BOOK.md").write_text(
                "# Book\n\n"
                "C:\\Users\\operator\\Ghidra\\Projects\\BEA.gpr\n\n"
                "C:\\Users\\operator\\source\\Onslaught-Career-Editor-private\\hidden\\proof-note.md\n\n"
                "C:\\Users\\operator\\source\\Onslaught-Career-Editor\\local\\state-note.md\n\n"
                "http://172.26.112.1:8193\n",
                encoding="utf-8",
            )

            build_lore_pack(root, root / LORE_PACK_DIR, use_git=False)
            content = (root / LORE_PACK_DIR / CONTENT_FILE_NAME).read_text(encoding="utf-8")

            self.assertNotIn("C:\\Users\\operator", content)
            self.assertNotIn("proof-note", content)
            self.assertNotIn("state-note", content)
            self.assertNotIn("172.26.112.1", content)
            self.assertIn("maintainer-local Ghidra BEA project", content)
            self.assertIn("maintainer-local former private checkout", content)
            self.assertIn("maintainer-local public checkout", content)
            self.assertIn("maintainer-local endpoint", content)

    def test_redacts_non_user_profile_drive_root_path_families_without_tail_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            lore = root / LORE_BOOK_DIR
            lore.mkdir()
            (lore / "BOOK.md").write_text(
                "# Book\n\n"
                "G:\\GhidraBackups\\synthetic-redaction-fixture\\synthetic-manifest.txt\n\n"
                "F:\\OnslaughtRuntimeProofArchive\\synthetic-redaction-fixture\\synthetic-capture.txt\n",
                encoding="utf-8",
            )

            build_lore_pack(root, root / LORE_PACK_DIR, use_git=False)
            content = (root / LORE_PACK_DIR / CONTENT_FILE_NAME).read_text(encoding="utf-8")

            self.assertIn("maintainer-local Ghidra backup root", content)
            self.assertIn("maintainer-local runtime proof archive", content)
            self.assertNotIn("synthetic-redaction-fixture", content)
            self.assertNotIn("synthetic-manifest", content)
            self.assertNotIn("synthetic-capture", content)

    def test_rejects_hard_payload_like_lore_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            lore = root / LORE_BOOK_DIR
            lore.mkdir()
            (lore / "BOOK.md").write_text("# Book\n", encoding="utf-8")
            (lore / "BEA.exe").write_bytes(b"no")

            with self.assertRaises(ValueError):
                build_lore_pack(root, root / LORE_PACK_DIR, use_git=False)

    def test_rejects_unsafe_lore_pack_relative_paths(self) -> None:
        unsafe_paths = (
            "",
            " ",
            "Start.md ",
            "../secret.md",
            "chapter/../secret.md",
            "chapter/./intro.md",
            "/absolute.md",
            "C:/local.md",
            "C:\\local.md",
            "\\\\server\\share\\doc.md",
            "chapter//intro.md",
            "chapter/intro.md/",
            "chapter\tintro.md",
            "chapter:alternate.md",
        )

        for relative_path in unsafe_paths:
            with self.subTest(relative_path=relative_path):
                with self.assertRaises(ValueError):
                    validate_lore_pack_relative_path(relative_path)

        self.assertEqual(validate_lore_pack_relative_path("chapter/intro.md"), "chapter/intro.md")
        self.assertEqual(validate_lore_pack_relative_path("deep/nested/doc.txt"), "deep/nested/doc.txt")
        self.assertEqual(validate_lore_pack_relative_path("file-with-dashes.md"), "file-with-dashes.md")

    def test_check_rejects_unsafe_lore_pack_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            self.write_lore_pack_fixture(pack_dir, relative_path="../secret.md")

            with self.assertRaises(ValueError):
                check_lore_pack(pack_dir)

    def test_check_rejects_lore_pack_relative_path_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            self.write_lore_pack_fixture(pack_dir, relative_path="Start.md", content_relative_path="Other.md")

            with self.assertRaises(ValueError):
                check_lore_pack(pack_dir)

    def test_check_rejects_invalid_document_id_without_echoing_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            self.write_lore_pack_fixture(pack_dir, relative_path="Start.md", doc_id="doc/path/SecretLeakProbe")

            with self.assertRaises(ValueError) as error:
                check_lore_pack(pack_dir)

            self.assertIn("document id", str(error.exception))
            self.assertNotIn("doc/path/SecretLeakProbe", str(error.exception))
            self.assertNotIn("SecretLeakProbe", str(error.exception))

    def test_check_rejects_case_variant_duplicate_document_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            content = "# Start\n\nSynthetic fixture.\n"
            digest = sha256_text(content)
            self.write_lore_pack_fixture(
                pack_dir,
                relative_path="Start.md",
                extra_index_documents=[
                    {
                        "id": "DOC-000001",
                        "relativePath": "Other.md",
                        "title": "Other",
                        "sha256": digest,
                        "byteLength": len(content.encode("utf-8")),
                        "order": 1,
                    }
                ],
                extra_content_rows=[
                    {
                        "id": "DOC-000001",
                        "relativePath": "Other.md",
                        "title": "Other",
                        "sha256": digest,
                        "byteLength": len(content.encode("utf-8")),
                        "content": content,
                    }
                ],
            )

            with self.assertRaises(ValueError) as error:
                check_lore_pack(pack_dir)

            self.assertIn("duplicate document id", str(error.exception))
            self.assertNotIn("DOC-000001", str(error.exception))

    def test_check_accepts_case_variant_content_document_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            self.write_lore_pack_fixture(pack_dir, relative_path="Start.md", content_doc_id="DOC-000001")

            checked = check_lore_pack(pack_dir)

            self.assertEqual(checked["documentCount"], 1)

    def test_check_rejects_byte_length_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            self.write_lore_pack_fixture(pack_dir, relative_path="Start.md", byte_length_delta=1)

            with self.assertRaises(ValueError) as error:
                check_lore_pack(pack_dir)

            self.assertIn("byteLength", str(error.exception))

    def test_check_rejects_above_root_packed_link_without_echoing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            self.write_lore_pack_fixture(
                pack_dir,
                relative_path="Start.md",
                content="# Start\n\n[Deep](../SecretLeakProbe.md)\n",
            )

            with self.assertRaises(ValueError) as error:
                check_lore_pack(pack_dir)

            self.assertIn("packed links", str(error.exception))
            self.assertNotIn("../SecretLeakProbe.md", str(error.exception))
            self.assertNotIn("SecretLeakProbe", str(error.exception))

    def test_check_accepts_encoded_in_root_dot_segment_packed_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            content = "# Start\n\n[Other](%2e%2e/Other.md)\n"
            other_content = "# Other\n\nSynthetic fixture.\n"
            other_digest = sha256_text(other_content)
            self.write_lore_pack_fixture(
                pack_dir,
                relative_path="folder/Start.md",
                content=content,
                extra_index_documents=[
                    {
                        "id": "doc-000002",
                        "relativePath": "Other.md",
                        "title": "Other",
                        "sha256": other_digest,
                        "byteLength": len(other_content.encode("utf-8")),
                        "order": 1,
                    }
                ],
                extra_content_rows=[
                    {
                        "id": "doc-000002",
                        "relativePath": "Other.md",
                        "title": "Other",
                        "sha256": other_digest,
                        "byteLength": len(other_content.encode("utf-8")),
                        "content": other_content,
                    }
                ],
            )

            checked = check_lore_pack(pack_dir)

            self.assertEqual(checked["documentCount"], 2)

    def test_check_rejects_encoded_above_root_packed_link_without_echoing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            self.write_lore_pack_fixture(
                pack_dir,
                relative_path="Start.md",
                content="# Start\n\n[Deep](%2e%2e/SecretLeakProbe.md)\n",
            )

            with self.assertRaises(ValueError) as error:
                check_lore_pack(pack_dir)

            self.assertIn("packed links", str(error.exception))
            self.assertNotIn("%2e%2e/SecretLeakProbe.md", str(error.exception))
            self.assertNotIn("SecretLeakProbe", str(error.exception))

    def test_check_rejects_unsafe_lore_pack_relative_path_without_echoing_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            pack_dir = Path(temp_root) / LORE_PACK_DIR
            self.write_lore_pack_fixture(pack_dir, relative_path="../SecretLeakProbe.md")

            with self.assertRaises(ValueError) as error:
                check_lore_pack(pack_dir)

            self.assertIn("relativePath", str(error.exception))
            self.assertNotIn("../SecretLeakProbe.md", str(error.exception))
            self.assertNotIn("SecretLeakProbe", str(error.exception))

    @staticmethod
    def write_lore_pack_fixture(
        pack_dir: Path,
        *,
        relative_path: str,
        content_relative_path: str | None = None,
        doc_id: str = "doc-000001",
        content_doc_id: str | None = None,
        content: str = "# Start\n\nSynthetic fixture.\n",
        byte_length_delta: int = 0,
        extra_index_documents: list[dict[str, object]] | None = None,
        extra_content_rows: list[dict[str, object]] | None = None,
    ) -> None:
        pack_dir.mkdir(parents=True)
        digest = sha256_text(content)
        byte_length = len(content.encode("utf-8")) + byte_length_delta
        row = {
            "id": content_doc_id or doc_id,
            "relativePath": content_relative_path or relative_path,
            "title": "Start",
            "sha256": digest,
            "byteLength": byte_length,
            "content": content,
        }
        documents: list[dict[str, object]] = [
            {
                "id": doc_id,
                "relativePath": relative_path,
                "title": "Start",
                "sha256": digest,
                "byteLength": byte_length,
                "order": 0,
            }
        ]
        if extra_index_documents:
            documents.extend(extra_index_documents)
        rows: list[dict[str, object]] = [row]
        if extra_content_rows:
            rows.extend(extra_content_rows)
        index = {
            "schema": SCHEMA,
            "sourceRoot": LORE_SOURCE_NAME,
            "documentCount": len(documents),
            "documents": documents,
        }
        (pack_dir / INDEX_FILE_NAME).write_text(json.dumps(index), encoding="utf-8")
        (pack_dir / CONTENT_FILE_NAME).write_text("".join(json.dumps(item) + "\n" for item in rows), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or check the WinUI offline Lore content pack.")
    parser.add_argument("--self-test", action="store_true", help="run focused unit tests")
    parser.add_argument("--build", action="store_true", help="build the pack")
    parser.add_argument("--check", action="store_true", help="check an existing pack")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(LorePackBuilderTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1

    root = args.root.resolve()
    out_dir = args.out_dir.resolve() if args.out_dir else root / LORE_PACK_DIR
    if args.build:
        report = build_lore_pack(root, out_dir, use_git=root == ROOT)
    elif args.check:
        report = check_lore_pack(out_dir)
    else:
        parser.error("expected --self-test, --build, or --check")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Lore pack {report['schema']}: {report['documentCount']} document(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
