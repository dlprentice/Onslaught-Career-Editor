#!/usr/bin/env python3
"""Validate the texture/resource/decode static contract ledger.

This checker consumes only tracked public Markdown, JSON, and package metadata.
It does not inspect ignored payload overlays, private manifests, raw proof
bundles, copied executables, live Ghidra state, runtime logs, auth/session/cache
data, or secrets. It validates that the texture/resource/decode surface remains
a static routing ledger and does not become runtime decode, GPU, visual,
extractor, generated-output, or rebuild proof.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract-ledger.v1.json"
LEDGER_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract-ledger.v1.json"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MEASUREMENT_REGISTER_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
RENDER_BRIDGE = ROOT / "reverse-engineering" / "binary-analysis" / "render-resource-bridge-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

PACKAGE_SCRIPT = "test:texture-resource-decode-static-contract"
PACKAGE_COMMAND = r"py -3 tools\texture_resource_decode_static_contract_probe.py --check"
SCOPE = "texture-resource-decode-static-contract-ledger"
LEDGER_STATUS = "texture-resource-decode-static-contract-ledger-complete-static-routing-not-runtime-proof"
SOURCE_EVIDENCE = {
    "staticContract": "reverse-engineering/binary-analysis/texture-resource-decode-static-contract.md",
    "renderBridgeContract": "reverse-engineering/binary-analysis/render-resource-bridge-static-contract.md",
    "measurementRegister": "reverse-engineering/binary-analysis/static-reaudit-measurement-register.md",
    "publicSafety": "tracked static contract and routing metadata only; no raw payload bytes, sample chunks, exact local roots, private artifact locators, or runtime observations",
}

LANES = (
    "archive-resource-ingress",
    "texture-lookup-lifetime",
    "serialized-parser-node-tree",
    "decode-setup",
    "codec-fronts",
    "jpeg-entropy-huffman",
    "zlib-inflate-huffman",
    "texel-conversion-upload",
    "render-facing-handoff",
)

HISTORICAL_WAVES = ("Wave1163", "Wave1216")

ANCHOR_FUNCTIONS = (
    "CTexture__NodePayloadRecordCtor",
    "CFastVB__NodeType9__ctor",
    "CDXTexture__NodeType13__ctor",
    "CDXTexture__RegisterSerializedChunk",
    "CFastVB__AreNodeTreesCompatible",
    "CFastVB__SelectBestNodeTreeMatch",
    "CTexture__LoadDefaultHuffmanTables",
    "CDXTexture__InflateStream_ProcessZlibState",
    "CDXTexture__BuildInflateHuffmanTable",
    "CDXTexture__FlushEntropyBitWriter",
)

FALSE_GUARDS = (
    "runtimeExecution",
    "beLaunch",
    "debuggerAttachment",
    "ghidraMutation",
    "freshGhidraExport",
    "executablePatching",
    "extractorExecution",
    "importerExecution",
    "generatedAssetOutput",
    "productUiWired",
    "runtimeParserBehaviorProven",
    "runtimeTextureDecodeBehaviorProven",
    "runtimeJpegBehaviorProven",
    "runtimeInflateBehaviorProven",
    "gpuUploadProven",
    "texturePixelsProven",
    "visualOutputProven",
    "exactLayoutProven",
    "rebuildImplementation",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "runtimeDecodeRows",
    "runtimeTexturePixelRows",
    "gpuUploadRows",
    "visualProofRows",
    "freshGhidraExportRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "extractorRunRows",
    "importerRunRows",
    "generatedAssetRows",
    "beProcessesAfterLedger",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\\\\[^\\/\s]+\\[^\\/\s]+"), "UNC/private network path"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "legacy private backup root"),
    (re.compile(r"(?i)/(?:home|mnt|var|opt|tmp|users?)/"), "machine-local absolute path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)(?<![A-Za-z0-9-])(?:local-game|private-game)[\\/]"), "private game mirror path"),
    (re.compile(r"(?i)(?<![A-Za-z0-9-])(?:local-media|private-media)[\\/]"), "private media path"),
    (re.compile(r"(?i)save-attempts[\\/]"), "private save path"),
    (re.compile(r"(?i)(?:local-proof|local-proofs|private-proof|private-proofs)[\\/]"), "private proof path"),
    (re.compile(r"(?i)(?:local-ghidra|ghidra-local)[\\/]"), "private Ghidra path"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framebytelength"), "private frame locator field"),
    (re.compile(r"(?i)password|token=|secret="), "secret-like marker"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"\b[a-fA-F0-9]{40}\b"), "raw digest-like value"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime texture decode behavior proven",
    "runtime jpeg behavior proven",
    "runtime inflate behavior proven",
    "runtime parser behavior proven",
    "gpu upload proven",
    "texture pixels proven",
    "visual output proven",
    "exact layout proven",
    "exact source-body identity proven",
    "extractor run complete",
    "importer execution complete",
    "generated asset output complete",
    "appcore support added",
    "winui support added",
    "cli support added",
    "product exposure approved",
    "rebuild implementation complete",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


class TextureContractError(ValueError):
    """Raised when the texture/resource/decode ledger violates its boundary."""


def read_text(path: Path) -> str:
    if not path.is_file():
        raise TextureContractError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise TextureContractError(f"invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TextureContractError(message)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_token(text: str, token: str) -> bool:
    return token in text or token in compact(text)


def check_public_safety(text: str, label: str, *, allow_digests: bool = False) -> None:
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        if allow_digests and category == "raw digest-like value":
            continue
        require(pattern.search(text) is None, f"{label} leaks forbidden public category: {category}")
    lower = text.lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{label} contains forbidden overclaim phrase: {phrase}")


def check_package_script() -> None:
    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts")
    require(isinstance(scripts, dict), "package.json scripts must be an object")
    require(scripts.get(PACKAGE_SCRIPT) == PACKAGE_COMMAND, f"package.json missing {PACKAGE_SCRIPT}")


def check_contract_text() -> None:
    require(CONTRACT.read_bytes() == CONTRACT_MIRROR.read_bytes(), "texture contract Markdown mirror mismatch")
    text = read_text(CONTRACT)
    mirror = read_text(CONTRACT_MIRROR)
    for label, body in (
        (str(CONTRACT.relative_to(ROOT)), text),
        (str(CONTRACT_MIRROR.relative_to(ROOT)), mirror),
    ):
        check_public_safety(body, label)
        for token in (
            "Texture Resource Decode Static Contract",
            "Historical Wave1216 and Wave1163 anchors",
            "Wave1220 static closeout acceptance",
            "active current-risk focused accounting is `1179/1179 = 100.00%`",
            "Current machine-readable companion",
            "texture-resource-decode-static-contract-ledger.v1.json",
            "latestGhidraBackupClass=verified-static-backup-redacted",
            "Archive/resource ingress",
            "Texture lookup/lifetime",
            "Serialized parser/node-tree",
            "Decode setup",
            "Codec fronts",
            "JPEG entropy/Huffman",
            "Zlib/inflate/Huffman",
            "Texel conversion/upload",
            "Render-facing handoff",
            "JPEG Huffman separate from inflate Huffman",
            "no runtime texture decode proof",
            "no rebuild parity",
        ):
            require(contains_token(body, token), f"{label} missing required token: {token}")
        for lane in LANES:
            require(lane in body, f"{label} missing ledger lane id: {lane}")
        for function_name in ANCHOR_FUNCTIONS:
            require(function_name in body, f"{label} missing anchor function: {function_name}")


def check_ledger() -> None:
    require(LEDGER.read_bytes() == LEDGER_MIRROR.read_bytes(), "texture contract ledger mirror mismatch")
    ledger = read_json(LEDGER)
    mirror = read_json(LEDGER_MIRROR)
    require(ledger == mirror, "texture contract ledger JSON mirror mismatch")
    for path in (LEDGER, LEDGER_MIRROR):
        check_public_safety(read_text(path), str(path.relative_to(ROOT)))

    require(ledger["schemaVersion"] == "texture-resource-decode-static-contract-ledger.v1", "schema version mismatch")
    require(ledger["status"] == "PASS", "ledger status mismatch")
    require(ledger["ledgerStatus"] == LEDGER_STATUS, "ledger status token mismatch")
    require(ledger["scope"] == SCOPE, "scope mismatch")
    require(ledger["proofClass"] == "Tier B static routing ledger; not runtime proof", "proof class mismatch")
    require(ledger["sourceEvidence"] == SOURCE_EVIDENCE, "source evidence mismatch")

    static = ledger["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch")
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch")
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch")
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch")
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch")
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch")
    require(static["currentRiskAuthority"] == "reverse-engineering/binary-analysis/static-reaudit-measurement-register.md", "current-risk authority mismatch")

    historical = ledger["historicalAnchors"]
    require([row["wave"] for row in historical] == list(HISTORICAL_WAVES), "historical wave order mismatch")
    for row in historical:
        require(row["status"] == "provenance-only", f"{row['wave']} must be provenance-only")
        require(row["backupClass"] == "historical-verified-backup-redacted", f"{row['wave']} backup class mismatch")
        require(row["activeCurrentTruth"] is False, f"{row['wave']} must not be active current truth")

    lanes = ledger["subsystemLanes"]
    require([row["id"] for row in lanes] == list(LANES), "subsystem lane order mismatch")
    for row in lanes:
        require("claim" in row and "boundary" in row, f"lane missing claim/boundary: {row.get('id')}")
        require("runtime" in row["boundary"].lower() or "exact" in row["boundary"].lower(), f"lane boundary too weak: {row['id']}")

    anchors = ledger["anchorFunctions"]
    require(anchors == list(ANCHOR_FUNCTIONS), "anchor function list mismatch")
    require(ledger["boundarySplits"]["jpegHuffmanSeparateFromInflateHuffman"] is True, "Huffman boundary mismatch")
    require("runtime decompression behavior" in ledger["boundarySplits"]["requiresLaterProof"], "boundary split missing later proof")

    guard = ledger["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch")
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch")
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"guard must be false: {key}")
    for key in ZERO_COUNTERS:
        require(guard["zeroCounters"][key] == 0, f"counter must be zero: {key}")

    public = ledger["publicSafety"]
    require(public["rawBytesEmitted"] is False, "raw bytes guard mismatch")
    require(public["sampleChunksEmitted"] is False, "sample chunks guard mismatch")
    require(public["rawHashValuesEmitted"] is False, "raw hash guard mismatch")
    require(public["absolutePrivatePathsEmitted"] is False, "absolute private path guard mismatch")
    require(public["privateArtifactLocatorsEmitted"] is False, "private artifact locator guard mismatch")
    require(public["publicLeakCheck"] == "PASS", "public leak check mismatch")

    claims = ledger["claimBoundary"]
    require("public-safe texture/resource/decode static routing ledger" in claims["proves"], "claim boundary missing positive scope")
    for token in (
        "runtime parser behavior",
        "runtime texture decode behavior",
        "runtime JPEG behavior",
        "runtime inflate/decompression behavior",
        "runtime texture pixels",
        "GPU upload behavior",
        "exact concrete layouts",
        "exact source-body identity",
        "extractor execution",
        "importer execution",
        "generated asset output",
        "AppCore support",
        "WinUI support",
        "CLI support",
        "product exposure",
        "BEA patching behavior",
        "visual QA",
        "gameplay outcomes",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in claims["doesNotProve"], f"claim boundary missing non-claim: {token}")


def check_source_anchors() -> None:
    require(MEASUREMENT_REGISTER.read_bytes() == MEASUREMENT_REGISTER_MIRROR.read_bytes(), "measurement register mirror mismatch")
    require(MAPPED_SYSTEMS.read_bytes() == MAPPED_SYSTEMS_MIRROR.read_bytes(), "mapped systems mirror mismatch")
    for path in (MEASUREMENT_REGISTER, MEASUREMENT_REGISTER_MIRROR):
        measurement = read_text(path)
        check_public_safety(measurement, str(path.relative_to(ROOT)), allow_digests=True)
        require("Wave1220 static closeout acceptance" in measurement, f"{path.relative_to(ROOT)} missing Wave1220 closeout authority")
        require("1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence" in measurement, f"{path.relative_to(ROOT)} missing current-risk authority")
    for path in (MAPPED_SYSTEMS, MAPPED_SYSTEMS_MIRROR):
        mapped = read_text(path)
        check_public_safety(mapped, str(path.relative_to(ROOT)), allow_digests=True)
        require("texture-resource-decode-static-contract.md" in mapped, f"{path.relative_to(ROOT)} missing texture contract link")
        require("texture-resource-decode-static-contract-ledger.v1.json" in mapped, f"{path.relative_to(ROOT)} missing texture ledger link")
        require("Wave1220 static closeout acceptance" in mapped, f"{path.relative_to(ROOT)} missing Wave1220 closeout authority")
    bridge = read_text(RENDER_BRIDGE)
    check_public_safety(bridge, str(RENDER_BRIDGE.relative_to(ROOT)), allow_digests=True)
    require("texture-resource-decode-static-contract.md" in bridge, "render bridge missing texture contract link")
    require("Runtime texture pixels and GPU upload behavior" in read_text(CONTRACT), "texture contract missing runtime texture boundary")


def run_check() -> None:
    check_contract_text()
    check_ledger()
    check_source_anchors()
    check_package_script()


def run_self_test() -> None:
    check_public_safety(
        "Static texture routing ledger only; no runtime proof, no exact layouts, no generated output.",
        "self-test clean boundary",
    )
    for bad_text, label in (
        ("runtime texture decode behavior proven", "positive runtime texture proof"),
        ("runtime JPEG behavior proven", "positive JPEG proof"),
        ("runtime inflate behavior proven", "positive inflate proof"),
        ("GPU upload proven", "positive GPU proof"),
        ("exact layout proven", "positive exact layout proof"),
        ("generated asset output complete", "positive generated output"),
        ("extractor run complete", "positive extractor run"),
        ("rebuild parity proven", "positive rebuild parity"),
        ("C:" + "\\Users\\example\\private\\file.txt", "raw Windows path"),
        ("\\\\server\\share\\private.txt", "raw UNC path"),
        ("X:" + "\\PrivateBackups\\example", "machine-local absolute path"),
        ("G" + ":" + "\\GhidraBackups\\example", "legacy private backup root"),
        ("local-game\\payload.bin", "private game mirror path"),
        ("local-media\\capture.bin", "private media path"),
        ("private-proofs\\capture.bin", "private proof path"),
        ("/home/example/private/file.txt", "raw Unix path"),
        ("a" * 64, "raw digest-like value"),
    ):
        try:
            check_public_safety(bad_text, label)
        except TextureContractError:
            pass
        else:
            raise TextureContractError(f"self-test failed to catch {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate tracked texture/resource/decode static contract ledger")
    parser.add_argument("--self-test", action="store_true", help="run internal negative guard tests")
    args = parser.parse_args()

    if not args.check and not args.self_test:
        parser.error("choose --check and/or --self-test")

    try:
        if args.self_test:
            run_self_test()
        if args.check:
            run_check()
    except TextureContractError as exc:
        print("Texture resource decode static contract probe: FAIL")
        print(f"- {exc}")
        return 1

    print("Texture resource decode static contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
