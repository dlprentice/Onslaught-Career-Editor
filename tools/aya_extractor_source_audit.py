#!/usr/bin/env python3
"""Deterministic source/history contract audit for the pinned AYAResourceExtractor fork."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable

SCHEMA = "onslaught.aya-resource-extractor-source-audit.v1"
EXTRACTOR_PIN = "53b10b083b59cfd7e72849c15bec8b608eaf8a23"
UPSTREAM_PIN = "4e04952a200e29040a68fc8648e835f9a7d608d1"
ONSLAUGHT_PIN = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"
CLASSIFICATIONS = frozenset(
    {
        "EXTRACTOR_ONLY",
        "CURRENTLY_CORROBORATED",
        "CURRENT_TOOL_STRONGER",
        "CONTRADICTED",
        "EXPORT_CONVENTION_ONLY",
        "UNKNOWN",
    }
)

HANDWRITTEN_CSHARP = (
    "Code/AyaResourceExtractor/AyaFileUncompressor.cs",
    "Code/AyaResourceExtractor/AyaModel.cs",
    "Code/AyaResourceExtractor/AyaModelExtractor.cs",
    "Code/AyaResourceExtractor/AyaModelImporter.cs",
    "Code/AyaResourceExtractor/AyaTextureExtractor.cs",
    "Code/AyaResourceExtractor/FbxModelExporter.cs",
    "Code/AyaResourceExtractor/Log.cs",
    "Code/AyaResourceExtractor/MainForm.cs",
    "Code/AyaResourceExtractor/Program.cs",
)
GENERATED_CSHARP = (
    "Code/AyaResourceExtractor/MainForm.Designer.cs",
    "Code/AyaResourceExtractor/Properties/Settings.Designer.cs",
)
NATIVE_GLUE = (
    "Code/DDSTextureUncompress/DDSTextureUncompress.cpp",
    "Code/ZLibWrapper/UnCompressFile.cpp",
)
PROJECT_SUPPORT = (
    "Code/AyaResourceExtractor/AYAResourceExtractor - Backup (1).csproj",
    "Code/AyaResourceExtractor/AYAResourceExtractor - Backup.csproj",
    "Code/AyaResourceExtractor/AYAResourceExtractor.csproj",
    "Code/AyaResourceExtractor/AYAResourceExtractor.sln",
    "Code/AyaResourceExtractor/MainForm.resx",
    "Code/AyaResourceExtractor/Properties/Settings.settings",
    "Code/AyaResourceExtractor/Properties/launchSettings.json",
    "Code/DDSTextureUncompress/DDSTextureUncompress.vcxproj",
    "Code/DDSTextureUncompress/DDSTextureUncompress.vcxproj.filters",
    "Code/ZLibWrapper/ZLibWrapper.vcxproj",
    "Code/ZLibWrapper/ZLibWrapper.vcxproj.filters",
)
DDS_THIRD_PARTY = (
    "Code/DDSTextureUncompress/DDSReader.cpp",
    "Code/DDSTextureUncompress/DDSreader.h",
)
TOP_LEVEL = ("BoxWithTextures.fbx", "LICENSE.txt", "README.md")
REPOSITORY_SUPPORT = (".gitattributes", ".gitignore")

EXPECTED_FUNCTIONS: dict[str, tuple[str, ...]] = {
    "Code/AyaResourceExtractor/AyaFileUncompressor.cs": ("Uncompress",),
    "Code/AyaResourceExtractor/AyaModel.cs": ("MultiplyWithVector",),
    "Code/AyaResourceExtractor/AyaModelExtractor.cs": ("ExtractModel",),
    "Code/AyaResourceExtractor/AyaModelImporter.cs": (
        "Import",
        "ReadString",
        "ReadUint",
        "ReadUshort",
        "ReadFloat",
        "ReadVector",
        "ReadVector3",
        "ReadMatrix",
        "ReadVertex",
        "ReadTag",
        "ReadTextures",
        "ReadTexture",
        "LogVector",
        "ReadModelPart",
        "ReadVertexBuffer",
    ),
    "Code/AyaResourceExtractor/AyaTextureExtractor.cs": ("ExtractorTexture",),
    "Code/AyaResourceExtractor/FbxModelExporter.cs": (
        "Export",
        "GenerateTriListIndicesFromTriStrip",
    ),
    "Code/AyaResourceExtractor/Log.cs": ("UpdateTextBox", "Clear", "Error", "AddMessage"),
    "Code/AyaResourceExtractor/MainForm.cs": (
        "MainForm",
        "ExtractFile",
        "ExtractIndividualAyaFileButton_Click",
        "ClearLogButton_Click",
        "ExtractAllButton_Click",
        "EnableExtractionButtons",
        "ExtractAll",
        "SetRootPathButton_Click",
        "SetOutputPathButton_Click",
        "StopExtractingButton_Click",
    ),
    "Code/AyaResourceExtractor/Program.cs": ("Main",),
    "Code/AyaResourceExtractor/MainForm.Designer.cs": ("Dispose", "InitializeComponent"),
    "Code/AyaResourceExtractor/Properties/Settings.Designer.cs": (),
    "Code/DDSTextureUncompress/DDSTextureUncompress.cpp": ("Uncompress",),
    "Code/ZLibWrapper/UnCompressFile.cpp": ("Uncompress",),
}

REQUIRED_CLAIMS = frozenset(
    {
        *(f"AYA-{index:03d}" for index in range(1, 11)),
        *(f"CMSH-{index:03d}" for index in range(1, 43)),
        *(f"GEO-{index:03d}" for index in range(1, 23)),
        *(f"FBX-{index:03d}" for index in range(1, 5)),
        *(f"TEX-{index:03d}" for index in range(1, 8)),
        *(f"LIM-{index:03d}" for index in range(1, 5)),
        *(f"UI-{index:03d}" for index in range(1, 4)),
    }
)

_DECLARATION = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|readonly|virtual|override|sealed|async|unsafe|extern|new)\s+)*"
    r"(?:[A-Za-z_][\w<>,.\[\]?]*\s+)?(?P<name>[A-Za-z_]\w*)\s*\([^;]*\)\s*$"
)
_NON_FUNCTION_WORDS = frozenset({"if", "for", "foreach", "while", "switch", "catch", "lock", "using", "return"})
_LINE_REFERENCE = re.compile(r"^(?P<path>.+):L(?P<first>[1-9]\d*)(?:-L?(?P<last>[1-9]\d*))?$")
FORMAT_TOKENS = (
    "CMSH", "CMST", "MSHT", "TEXB", "MESP", "CMSP", "CHLD", "PRNT", "NMIC",
    "BBOX", "CCUS", "CAMD", "VHFM", "HORI", "HPOS", "HFOV", "BONE", "BONW", "BONS",
    "PBKT", "CPOS", "CORI", "REFR", "PMVB", "CMVB", "MMPT", "IBUF",
    "VBUF", "TEXR",
)
THEMATIC_TOKENS = (
    "CChunkReader",
    "meshtex\\\\",
    "meshtex%",
    "dxtntextures",
    "D3DPT_TRIANGLESTRIP",
    "D3DFVF_",
    "A1R5G5B5",
    "A8R8G8B8",
)


class AuditError(ValueError):
    pass


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _decode_text(data: bytes) -> str | None:
    if b"\0" in data[:4096]:
        return None
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def _git_blobs(
    repo: Path, revision: str, relatives: Iterable[str]
) -> dict[str, tuple[str, bytes]]:
    requested = tuple(relatives)
    completed = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        check=True,
        input="".join(f"{revision}:{relative}\n" for relative in requested).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = completed.stdout
    cursor = 0
    blobs: dict[str, tuple[str, bytes]] = {}
    for relative in requested:
        header_end = output.find(b"\n", cursor)
        if header_end < 0:
            raise AuditError(f"truncated Git blob header for {revision}:{relative}")
        header = output[cursor:header_end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise AuditError(f"Git blob unavailable for {revision}:{relative}")
        object_id = header[0].decode("ascii")
        size = int(header[2])
        data_start = header_end + 1
        data_end = data_start + size
        data = output[data_start:data_end]
        if len(data) != size or output[data_end:data_end + 1] != b"\n":
            raise AuditError(f"truncated Git blob body for {revision}:{relative}")
        if _git_blob_sha1(data) != object_id:
            raise AuditError(f"Git blob identity mismatch for {revision}:{relative}")
        blobs[relative] = (object_id, data)
        cursor = data_end + 1
    if cursor != len(output):
        raise AuditError(f"unexpected trailing Git blob data for {revision}")
    return blobs


def _git_blob(repo: Path, revision: str, relative: str) -> tuple[str, bytes]:
    return _git_blobs(repo, revision, (relative,))[relative]


def _inventory_blob(relative: str, object_id: str, data: bytes) -> dict[str, object]:
    text = _decode_text(data)
    return {
        "path": relative,
        "bytes": len(data),
        "physicalLines": None if text is None else len(text.splitlines()),
        "gitBlobSha1": object_id,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _inventory_file(extractor_root: Path, relative: str, revision: str = "HEAD") -> dict[str, object]:
    object_id, data = _git_blob(extractor_root, revision, relative)
    return _inventory_blob(relative, object_id, data)


def _scan_function_blob(relative: str, data: bytes) -> list[dict[str, object]]:
    text = _decode_text(data)
    if text is None:
        raise AuditError(f"first-party source is not text: {relative}")
    declarations: list[dict[str, object]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = _DECLARATION.match(line)
        if match is None:
            continue
        name = match.group("name")
        if name in _NON_FUNCTION_WORDS:
            continue
        declarations.append({"name": name, "line": line_number})
    expected = list(EXPECTED_FUNCTIONS[relative])
    actual = [str(item["name"]) for item in declarations]
    if actual != expected:
        raise AuditError(f"function denominator drift for {relative}: expected {expected!r}, got {actual!r}")
    return declarations


def _scan_functions(extractor_root: Path, relative: str, revision: str = "HEAD") -> list[dict[str, object]]:
    _, data = _git_blob(extractor_root, revision, relative)
    return _scan_function_blob(relative, data)


def _glob_files(root: Path, directory: str, revision: str = "HEAD") -> tuple[str, ...]:
    return tuple(
        filter(None, _git(root, "ls-tree", "-r", "--name-only", revision, "--", directory).splitlines())
    )


def _validate_line_reference(repo_root: Path, value: str) -> None:
    match = _LINE_REFERENCE.match(value)
    if match is None:
        if ":sha256=" in value:
            path_text, digest = value.rsplit(":sha256=", 1)
            path = repo_root / path_text
            if not path.is_file() or len(digest) != 64 or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise AuditError(f"invalid hash reference: {value}")
            return
        raise AuditError(f"reference lacks checked line range or hash: {value}")
    path = repo_root / match.group("path")
    if not path.is_file():
        raise AuditError(f"missing referenced file: {value}")
    text = _decode_text(path.read_bytes())
    if text is None:
        raise AuditError(f"line reference points at binary: {value}")
    total = len(text.splitlines())
    first = int(match.group("first"))
    last = int(match.group("last") or first)
    if first > last or last > total:
        raise AuditError(f"out-of-range line reference: {value} (file has {total})")


def _read_contract(repo_root: Path, contract_path: Path) -> tuple[list[dict[str, str]], dict[str, int]]:
    with contract_path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        expected_fields = (
            "claim_id",
            "area",
            "extractor_claim",
            "extractor_source",
            "classification",
            "current_evidence",
            "comparison",
            "priority_follow_up",
        )
        if tuple(reader.fieldnames or ()) != expected_fields:
            raise AuditError("contract columns drifted")
        rows = list(reader)
    if not rows:
        raise AuditError("contract is empty")
    ids = [row["claim_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise AuditError("duplicate contract claim id")
    actual_ids = frozenset(ids)
    if actual_ids != REQUIRED_CLAIMS:
        missing = sorted(REQUIRED_CLAIMS - actual_ids)
        extra = sorted(actual_ids - REQUIRED_CLAIMS)
        raise AuditError(f"contract denominator drift: missing={missing}, extra={extra}")
    for row in rows:
        if any(value == "" for value in row.values()):
            raise AuditError(f"blank contract field: {row['claim_id']}")
        if row["classification"] not in CLASSIFICATIONS:
            raise AuditError(f"unclassified contract row: {row['claim_id']}")
        for field in ("extractor_source", "current_evidence"):
            for reference in row[field].split(";"):
                _validate_line_reference(repo_root, reference)
    counts = Counter(row["classification"] for row in rows)
    return rows, {key: counts.get(key, 0) for key in sorted(CLASSIFICATIONS)}


def _token_hits(
    repo: Path,
    tokens: Iterable[str],
    *,
    words: bool,
    revision: str = "HEAD",
) -> dict[str, list[dict[str, object]]]:
    patterns = {
        token: re.compile(
            rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])" if words else re.escape(token)
        )
        for token in tokens
    }
    hits: dict[str, list[dict[str, object]]] = {token: [] for token in tokens}
    tracked = tuple(filter(None, _git(repo, "ls-tree", "-r", "--name-only", revision).splitlines()))
    blobs = _git_blobs(repo, revision, tracked)
    for relative in tracked:
        _, data = blobs[relative]
        text = _decode_text(data)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for token, pattern in patterns.items():
                if pattern.search(line):
                    hits[token].append({"path": relative, "line": line_number})
    return hits


def build_report(repo_root: Path, contract_path: Path) -> dict[str, object]:
    repo_root = repo_root.resolve()
    extractor_root = repo_root / "references" / "AYAResourceExtractor"
    onslaught_root = repo_root / "references" / "Onslaught"
    if _git(extractor_root, "rev-parse", "HEAD") != EXTRACTOR_PIN:
        raise AuditError("AYAResourceExtractor pin mismatch")
    _git(extractor_root, "cat-file", "-e", f"{UPSTREAM_PIN}^{{commit}}")
    if _git(onslaught_root, "rev-parse", "HEAD") != ONSLAUGHT_PIN:
        raise AuditError("Onslaught pin mismatch")
    if len(FORMAT_TOKENS) != len(set(FORMAT_TOKENS)):
        raise AuditError("format token denominator contains duplicates")

    categories: dict[str, tuple[str, ...]] = {
        "firstPartyHandwrittenCSharp": HANDWRITTEN_CSHARP,
        "firstPartyGeneratedCSharp": GENERATED_CSHARP,
        "firstPartyNativeGlue": NATIVE_GLUE,
        "firstPartyProjectSupport": PROJECT_SUPPORT,
        "thirdPartyDdsReaderFreeImage": DDS_THIRD_PARTY,
        "thirdPartyFbxHamishMilne": _glob_files(extractor_root, "Code/Fbx", EXTRACTOR_PIN),
        "thirdPartyZlib": _glob_files(extractor_root, "Code/ZLib", EXTRACTOR_PIN),
        "templateAndTopLevel": TOP_LEVEL,
        "repositorySupport": REPOSITORY_SUPPORT,
    }
    assigned = [path for values in categories.values() for path in values]
    if len(assigned) != len(set(assigned)):
        raise AuditError("inventory categories overlap")
    tracked = tuple(
        filter(None, _git(extractor_root, "ls-tree", "-r", "--name-only", EXTRACTOR_PIN).splitlines())
    )
    if set(assigned) != set(tracked):
        raise AuditError(
            f"tracked inventory mismatch: missing={sorted(set(tracked) - set(assigned))}, "
            f"extra={sorted(set(assigned) - set(tracked))}"
        )
    extractor_blobs = _git_blobs(extractor_root, EXTRACTOR_PIN, tracked)

    inventory: dict[str, object] = {}
    for category, files in categories.items():
        records = [
            _inventory_blob(path, *extractor_blobs[path])
            for path in files
        ]
        inventory[category] = {
            "fileCount": len(records),
            "physicalLines": sum(int(item["physicalLines"] or 0) for item in records),
            "files": records,
        }

    functions: list[dict[str, object]] = []
    for relative in (*HANDWRITTEN_CSHARP, *GENERATED_CSHARP, *NATIVE_GLUE):
        for declaration in _scan_function_blob(relative, extractor_blobs[relative][1]):
            functions.append({"path": relative, **declaration})

    rows, classification_counts = _read_contract(repo_root, contract_path.resolve())
    return {
        "schemaVersion": SCHEMA,
        "extractorPin": EXTRACTOR_PIN,
        "upstreamPin": UPSTREAM_PIN,
        "forkDelta": [
            {
                "commit": EXTRACTOR_PIN,
                "path": "Code/DDSTextureUncompress/DDSTextureUncompress.cpp",
                "role": "rectangular DDS copy-bounds fix only",
            }
        ],
        "onslaughtComparison": {
            "pin": ONSLAUGHT_PIN,
            "formatTokenCount": len(FORMAT_TOKENS),
            "formatTokenHits": _token_hits(
                onslaught_root, FORMAT_TOKENS, words=True, revision=ONSLAUGHT_PIN
            ),
            "thematicTokenHits": _token_hits(
                onslaught_root, THEMATIC_TOKENS, words=False, revision=ONSLAUGHT_PIN
            ),
        },
        "trackedFileCount": len(tracked),
        "inventory": inventory,
        "firstPartyRoutineDenominator": {
            "count": len(functions),
            "routines": functions,
        },
        "contract": {
            "rowCount": len(rows),
            "classificationCounts": classification_counts,
            "claimIds": sorted(row["claim_id"] for row in rows),
            "unclassifiedRows": 0,
        },
    }


def render_report(report: dict[str, object]) -> bytes:
    return (
        json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    ).encode("ascii")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument(
        "--contract",
        type=Path,
        default=default_root / "reverse-engineering" / "source-code" / "aya-resource-extractor-contract.tsv",
    )
    parser.add_argument("--out", type=Path)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    try:
        rendered = render_report(build_report(args.repo_root, args.contract))
    except (AuditError, OSError, subprocess.CalledProcessError) as error:
        print(f"audit rejected: {error}", file=sys.stderr)
        return 2
    if args.out is None:
        sys.stdout.buffer.write(rendered)
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
