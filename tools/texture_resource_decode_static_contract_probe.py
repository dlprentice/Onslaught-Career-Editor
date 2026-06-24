#!/usr/bin/env python3
"""Validate the static texture/resource/decode contract anchors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

TOKENS = (
    "Texture Resource Decode Static Contract",
    "wave1163-texture-node-tree-inflate-huffman-current-risk-review",
    "564/1179 = 47.84%",
    "17 CFastVB/CTexture/CDXTexture current-risk rows",
    "Archive/resource ingress",
    "Texture lookup/lifetime",
    "Serialized parser/node-tree",
    "Decode setup",
    "Codec fronts",
    "JPEG entropy/Huffman",
    "Zlib/inflate/Huffman",
    "Texel conversion/upload",
    "Render-facing handoff",
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
    "JPEG Huffman separate from inflate Huffman",
    "no runtime texture decode proof",
    "no rebuild parity",
)

OVERCLAIMS = (
    "runtime texture decode behavior proven",
    "runtime jpeg behavior proven",
    "runtime inflate behavior proven",
    "exact layout proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    text = read_text(CONTRACT)
    mirror = read_text(CONTRACT_MIRROR)
    if text != mirror:
        failures.append("texture contract mirror mismatch")
    for token in TOKENS:
        if token not in text:
            failures.append(f"missing token: {token}")
    lowered = text.lower()
    for token in OVERCLAIMS:
        if token in lowered:
            failures.append(f"overclaim token: {token}")

    scripts = json.loads(read_text(PACKAGE_JSON)).get("scripts", {})
    expected = r"py -3 tools\texture_resource_decode_static_contract_probe.py --check"
    if scripts.get("test:texture-resource-decode-static-contract") != expected:
        failures.append("missing package script")

    if failures:
        print("Texture resource decode static contract probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture resource decode static contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
