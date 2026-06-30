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
from pathlib import Path
from urllib.parse import quote, unquote

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
LORE_BOOK_DIR = "lore-book"
LORE_PACK_DIR = "lore-pack"
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
LOCAL_PATH_REDACTIONS = (
    (re.compile(r"https?://(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|127\.\d{1,3}\.\d{1,3}\.\d{1,3}|localhost)(?::\d+)?(?:/[^\s<>()\]]*)?", re.IGNORECASE), "maintainer-local endpoint"),
    (re.compile(r"\bC:\\Users\\david\\source\\Onslaught-Career-Editor-private\\?", re.IGNORECASE), "maintainer-local former private checkout"),
    (re.compile(r"\bC:\\Users\\david\\source\\Onslaught-Career-Editor\\?", re.IGNORECASE), "maintainer-local public checkout"),
    (re.compile(r"\bC:\\Users\\david\\Ghidra\\Projects\\BEA(?:\.gpr|\.rep)?\\?", re.IGNORECASE), "maintainer-local Ghidra BEA project"),
    (re.compile(r"\bC:\\Users\\david\\Ghidra\\?", re.IGNORECASE), "maintainer-local Ghidra root"),
    (re.compile(r"\bG:\\GhidraBackups\\?", re.IGNORECASE), "maintainer-local Ghidra backup root"),
    (re.compile(r"\bG:\\OnslaughtRuntimeProofArchive\\?", re.IGNORECASE), "maintainer-local runtime proof archive"),
    (re.compile(r"\bG:\\", re.IGNORECASE), "maintainer-local external drive"),
    (re.compile(r"\b[A-Z]:\\[^\r\n`<>()\]]+", re.IGNORECASE), "maintainer-local Windows path"),
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
        raise ValueError("Lore pack relativePath is missing")
    if value.strip() != value:
        raise ValueError(f"Lore pack relativePath has unsafe whitespace: {value!r}")
    if "\\" in value:
        raise ValueError(f"Lore pack relativePath uses backslashes: {value!r}")
    if value.startswith("/"):
        raise ValueError(f"Lore pack relativePath is absolute: {value!r}")
    if ":" in value:
        raise ValueError(f"Lore pack relativePath contains a URI or drive marker: {value!r}")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"Lore pack relativePath contains a control character: {value!r}")

    parts = value.split("/")
    if any(part in {"", ".", ".."} or part.strip() != part for part in parts):
        raise ValueError(f"Lore pack relativePath has unsafe path segments: {value!r}")
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
        ["git", "ls-files", "--", f"{LORE_BOOK_DIR}/"],
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
    return sorted(path for path in lore_root.rglob("*") if path.is_file())


def collect_lore_documents(root: Path, lore_root: Path, *, use_git: bool) -> list[Path]:
    candidates = git_lore_files(root, lore_root) if use_git else filesystem_lore_files(lore_root)
    documents: list[Path] = []
    for path in sorted(candidates, key=lambda item: item.relative_to(lore_root).as_posix().lower()):
        relative = path.relative_to(lore_root).as_posix()
        lower_name = path.name.lower()
        suffix = path.suffix.lower()
        if lower_name in DENY_NAMES or suffix in DENY_SUFFIXES:
            raise ValueError(f"hard-payload-like Lore source rejected: {relative}")
        if suffix in PACKABLE_SUFFIXES:
            documents.append(path)
    return documents


def build_lore_pack(root: Path = ROOT, output_dir: Path | None = None, *, use_git: bool = True) -> dict[str, object]:
    lore_root = root / LORE_BOOK_DIR
    if output_dir is None:
        output_dir = root / LORE_PACK_DIR
    if not lore_root.is_dir():
        raise FileNotFoundError(f"missing {lore_root}")

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
        "sourceRoot": LORE_BOOK_DIR,
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
        doc_id = item.get("id")
        if not isinstance(doc_id, str) or not doc_id.strip():
            raise ValueError(f"index document {item_number} is missing id")
        if doc_id in expected:
            raise ValueError(f"duplicate Lore pack document id: {doc_id}")
        relative_path = validate_lore_pack_relative_path(item.get("relativePath"))
        relative_key = relative_path.lower()
        if relative_key in indexed_relative_paths:
            raise ValueError(f"duplicate Lore pack relativePath: {relative_path}")
        indexed_relative_paths.add(relative_key)
        item["relativePath"] = relative_path
        expected[doc_id] = item
    if index.get("documentCount") != len(expected):
        raise ValueError("Lore pack documentCount does not match index rows")

    seen: set[str] = set()
    for line_number, line in enumerate(content_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        doc_id = row.get("id")
        if doc_id not in expected:
            raise ValueError(f"content row {line_number} has unknown id {doc_id!r}")
        if doc_id in seen:
            raise ValueError(f"content row {line_number} duplicates id {doc_id!r}")
        relative_path = validate_lore_pack_relative_path(row.get("relativePath"))
        if relative_path != expected[doc_id].get("relativePath"):
            raise ValueError(f"content row {line_number} relativePath does not match index")
        content = row.get("content")
        if not isinstance(content, str):
            raise ValueError(f"content row {line_number} is missing text content")
        digest = sha256_text(content)
        if digest != row.get("sha256") or digest != expected[doc_id].get("sha256"):
            raise ValueError(f"content row {line_number} hash mismatch")
        seen.add(doc_id)
    missing = sorted(set(expected) - seen)
    if missing:
        raise ValueError("Lore pack content is missing rows: " + ", ".join(missing[:8]))
    return {
        "schema": index["schema"],
        "documentCount": len(seen),
        "indexSha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
        "contentSha256": hashlib.sha256(content_path.read_bytes()).hexdigest(),
    }


class LorePackBuilderTests(unittest.TestCase):
    def test_build_and_check_lore_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            lore = root / LORE_BOOK_DIR
            lore.mkdir()
            (lore / "BOOK.md").write_text("- [Start](Start.md)\n", encoding="utf-8")
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
            self.assertIn("[Rows](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/lore-book/rows.tsv)", content)
            self.assertIn("[Tool](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/tools/helper.py)", content)

    def test_redacts_maintainer_paths_and_private_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            lore = root / LORE_BOOK_DIR
            lore.mkdir()
            (lore / "BOOK.md").write_text(
                "# Book\n\nD:\\Ghidra\\Projects\\BEA.gpr\n\nhttp://172.26.112.1:8193\n",
                encoding="utf-8",
            )

            build_lore_pack(root, root / LORE_PACK_DIR, use_git=False)
            content = (root / LORE_PACK_DIR / CONTENT_FILE_NAME).read_text(encoding="utf-8")

            self.assertNotIn("D:\\", content)
            self.assertNotIn("172.26.112.1", content)
            self.assertIn("maintainer-local Windows path", content)
            self.assertIn("maintainer-local endpoint", content)

    def test_rejects_hard_payload_like_lore_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            lore = root / LORE_BOOK_DIR
            lore.mkdir()
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

    @staticmethod
    def write_lore_pack_fixture(pack_dir: Path, *, relative_path: str, content_relative_path: str | None = None) -> None:
        pack_dir.mkdir(parents=True)
        content = "# Start\n\nSynthetic fixture.\n"
        digest = sha256_text(content)
        row = {
            "id": "doc-000001",
            "relativePath": content_relative_path or relative_path,
            "title": "Start",
            "sha256": digest,
            "byteLength": len(content.encode("utf-8")),
            "content": content,
        }
        index = {
            "schema": SCHEMA,
            "sourceRoot": LORE_BOOK_DIR,
            "documentCount": 1,
            "documents": [
                {
                    "id": "doc-000001",
                    "relativePath": relative_path,
                    "title": "Start",
                    "sha256": digest,
                    "byteLength": len(content.encode("utf-8")),
                    "order": 0,
                }
            ],
        }
        (pack_dir / INDEX_FILE_NAME).write_text(json.dumps(index), encoding="utf-8")
        (pack_dir / CONTENT_FILE_NAME).write_text(json.dumps(row) + "\n", encoding="utf-8")


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
