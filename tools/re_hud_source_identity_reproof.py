#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove three CHud source identities from exact PC retail/source ordering.

This proof is static and read-only.  It binds the pristine retail bodies, the
current verified 8,136-function Ghidra inventory, exact instruction exports,
and two supplied source variants.  It proves source-method identity and call
ordering only; it does not prove visible rendering, runtime branch behavior,
field names, or reconstruction parity.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import struct
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "bea.re.hud-source-identity-reproof.v1"
CLAIM = "PC_RETAIL_CHUD_RENDER_OVERLAY_SWITCHINOVERLAY_SOURCE_IDENTITIES"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EVIDENCE_RELATIVE = Path("local-lab/hud-source-identity-reproof-20260812-v1")
READY_NAME = "proof.ready.json"

INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup":
        (2_506_752, SPECIMEN_SHA256),
    "references/Onslaught/PCEngine.cpp":
        (26_325, "aaa017eda83eaf36ae2eb5d5b47fad2a6b4cb3af09e56538b078d7b771c3a369"),
    "references/Onslaught/DXEngine.cpp":
        (44_268, "1d6764e491716a50364c32bacd34d1c69bc2970f51448277695520fa6a48c425"),
    "local-lab/ghidra-fullpass-2026-07-23/exports/W005/instructions.tsv":
        (4_689_887, "8696f71f93bf7220386d7325f990d05b8173d4e5f06ae0e1ff368b700a8db275"),
    "local-lab/ghidra-fullpass-2026-07-23/exports/W010/instructions.tsv":
        (4_867_985, "c08848d95182d657e71bd6221224577bf68646b78f7ba883da8476bfdbe3e59e"),
    "local-lab/ghidra-cround-handle-event-arm-effects-live-promotion-20260812-v1/"
    "runs/live-post-inventory/functions.tsv":
        (7_059_971, "356001a1910712b65e80886281c8536ba59b3e26d440c87bdd5a5fc0a92642b4"),
    "local-lab/ghidra-cround-handle-event-arm-effects-live-promotion-20260812-v1/"
    "runs/live-post-inventory/program.tsv":
        (1_267, "790ae35e391077ca7e4f8656ea229ea4ffb16ddf306ed5dcb4b06815498ce8f9"),
    "local-lab/ghidra-cround-handle-event-arm-effects-live-promotion-20260812-v1/"
    "live-promotion-v2.ready.json":
        (5_323, "6009a379eeb5c7506a9c1a30f6312e695b74a0a0779161e86f76c76637fc4811"),
    "local-lab/ghidra-cround-handle-event-arm-effects-live-promotion-20260812-v1/"
    "tracked-snapshot-restore.ready.json":
        (5_971, "d687fc821b0f674e46337c436f67c02a2adc344c5cd5a85b1e83519b21475e5f"),
}

PROGRAM_RELATIVE = next(key for key in INPUTS if key.endswith("/program.tsv"))
FUNCTIONS_RELATIVE = next(key for key in INPUTS if key.endswith("/functions.tsv"))
W005_RELATIVE = next(key for key in INPUTS if key.endswith("W005/instructions.tsv"))
W010_RELATIVE = next(key for key in INPUTS if key.endswith("W010/instructions.tsv"))

TARGETS: dict[str, dict[str, Any]] = {
    "0x00482050": {
        "preName": "CHud__PromotePendingHudComponent",
        "postName": "CHud__SwitchInOverlay",
        "bodyEnd": 0x00482089,
        "bodyBytes": 57,
        "bodySha256": "d05f4babaea82c17acdbe94643e9c56c0d53a59e33d41b465cadd6f9875db308",
        "bodyDigest": "5f371f29ef6faab252bba14db24cf8703be7f33d9d25776d905f758631437393",
        "instructionCount": 17,
        "preSignature": "void __thiscall CHud__PromotePendingHudComponent(void * this)",
        "commentSha256": "fa7bd0edc83b9a48e87b2072aa1d79552882ab938c5b37bf00caadd28664b940",
        "landmarks": (
            ("0x00482053", "MOV", "EAX, dword ptr [ESI + 0x200]"),
            ("0x00482077", "MOV", "dword ptr [ESI + 0x200], 0x0"),
            ("0x00482081", "MOV", "dword ptr [ESI + 0x1fc], ECX"),
        ),
    },
    "0x00487bc0": {
        "preName": "CHud__RenderOverlay",
        "postName": "CHud__Render",
        "bodyEnd": 0x00487D0C,
        "bodyBytes": 332,
        "bodySha256": "57f6ac5df156250ae2358c017615029cb42075dc2e18a5b59f7d6e0c18936f0f",
        "bodyDigest": "bb6d356f43a990204f7206f2543c02a594d3fb7d8867f3658729440c61b7e107",
        "instructionCount": 104,
        "preSignature": "void __thiscall CHud__RenderOverlay(void * this)",
        "commentSha256": "4f9ef7ef145e0a9925969ca004ce09014c6beef709386373e98fa454c82b6e84",
        "landmarks": (
            ("0x00487c01", "MOV", "dword ptr [EBX + 0x4c], ECX"),
            ("0x00487c57", "CALL", "0x004879e0"),
        ),
    },
    "0x00488090": {
        "preName": "CHud__RenderActiveHudComponentPass",
        "postName": "CHud__RenderOverlay",
        "bodyEnd": 0x004881E0,
        "bodyBytes": 336,
        "bodySha256": "690cb02e54cc6246137e3540479af23e9cf0f32dc6b9850eea29406994829925",
        "bodyDigest": "e7b3a684f09adb050926fb343464dee21877ce71287b0007ba8ffd4fe0d9c423",
        "instructionCount": 95,
        "preSignature": "void __thiscall CHud__RenderActiveHudComponentPass(void * this)",
        "commentSha256": "5773aed87c6d43665944f2a775b8612ec8b59c4c04b33b0cbfa65c7d11578929",
        "landmarks": (
            ("0x00488096", "MOV", "EAX, dword ptr [EBP + 0x1fc]"),
            ("0x0048815f", "CALL", "0x004de860"),
            ("0x0048816a", "MOV", "CL, byte ptr [EAX + 0x64]"),
            ("0x00488181", "MOV", "dword ptr [EBP + 0x1fc], 0x0"),
        ),
    },
}

POST_RENDER_CALLS = (
    ("0x0053ed01", "0x00487bc0", "CHud::Render"),
    ("0x0053ed79", "0x00487d10", "CHud::RenderBattleline"),
    ("0x0053ef26", "0x00488090", "CHud::RenderOverlay"),
    ("0x0053ef5e", "0x00482050", "CHud::SwitchInOverlay"),
)


class ProofError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ProofError(message)


def root_path() -> Path:
    configured = os.environ.get("BEA_REPO_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, root: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def exact_inputs(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(INPUTS.items()):
        actual = stamp(root / relative, root)
        require((actual["bytes"], actual["sha256"]) == expected,
                f"input identity differs: {relative}")
        result[relative] = actual
    return result


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def one(rows: Iterable[dict[str, str]], key: str, value: str, label: str) -> dict[str, str]:
    matches = [row for row in rows if row.get(key) == value]
    require(len(matches) == 1, f"{label} census differs")
    return matches[0]


def pe_offset(image: bytes, va: int) -> int:
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    require(image[pe:pe + 4] == b"PE\0\0", "pristine PE signature differs")
    sections = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    optional = pe + 24
    image_base = struct.unpack_from("<I", image, optional + 28)[0]
    rva = va - image_base
    table = optional + optional_size
    for index in range(sections):
        row = table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", image, row + 8)
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_pointer + rva - virtual_address
    raise ProofError(f"VA is not mapped: 0x{va:08x}")


def validate_pristine(image: bytes, *, require_whole_image: bool = True) -> dict[str, Any]:
    if require_whole_image:
        require(len(image) == 2_506_752 and sha256_bytes(image) == SPECIMEN_SHA256,
                "pristine specimen differs")
    bodies: list[dict[str, Any]] = []
    for address, spec in TARGETS.items():
        start = int(address, 16)
        end = int(spec["bodyEnd"])
        offset = pe_offset(image, start)
        body = image[offset:offset + end - start]
        require(len(body) == spec["bodyBytes"], f"body length differs: {address}")
        require(sha256_bytes(body) == spec["bodySha256"], f"body bytes differ: {address}")
        bodies.append({
            "address": address,
            "endExclusiveVa": f"0x{end:08x}",
            "bytes": len(body),
            "sha256": spec["bodySha256"],
        })
    return {"specimenSha256": SPECIMEN_SHA256, "bodies": bodies}


def validate_source_text(pc_text: str, dx_text: str) -> dict[str, Any]:
    pc = pc_text.splitlines()
    dx = dx_text.splitlines()
    expected_pc = {
        846: "HUD.Render();",
        900: "HUD.RenderOverlay();",
        936: "HUD.SwitchInOverlay();",
    }
    expected_dx = {
        1333: "HUD.Render();",
        1354: "HUD.RenderBattleline(viewport);",
        1418: "HUD.RenderOverlay();",
        1457: "HUD.SwitchInOverlay();",
    }
    for line, expected in expected_pc.items():
        require(line <= len(pc) and pc[line - 1].strip() == expected,
                f"PCEngine source line differs: {line}")
    for line, expected in expected_dx.items():
        require(line <= len(dx) and dx[line - 1].strip() == expected,
                f"DXEngine source line differs: {line}")
    require(list(expected_pc) == sorted(expected_pc), "PCEngine call order differs")
    require(list(expected_dx) == sorted(expected_dx), "DXEngine call order differs")
    return {
        "PCEngine.cpp": [{"line": line, "call": call} for line, call in expected_pc.items()],
        "DXEngine.cpp": [{"line": line, "call": call} for line, call in expected_dx.items()],
    }


def instruction_key(row: dict[str, str]) -> tuple[str, str, str]:
    return row.get("instruction_addr", ""), row.get("mnemonic", ""), row.get("operands", "")


def validate_retail_rows(w005: list[dict[str, str]], w010: list[dict[str, str]]) -> dict[str, Any]:
    body_observations: dict[str, list[dict[str, str]]] = {}
    for address, spec in TARGETS.items():
        rows = [row for row in w005 if row.get("function_entry") == address]
        require(len(rows) == spec["instructionCount"], f"instruction count differs: {address}")
        observed = {instruction_key(row) for row in rows}
        landmarks = []
        for landmark in spec["landmarks"]:
            require(landmark in observed, f"retail body landmark differs: {address} {landmark[0]}")
            landmarks.append({"instructionVa": landmark[0], "mnemonic": landmark[1],
                              "operands": landmark[2]})
        body_observations[address] = landmarks

    post = [row for row in w010 if row.get("function_entry") == "0x0053ecc0"]
    call_rows = []
    positions = []
    for instruction, target, source_name in POST_RENDER_CALLS:
        row = one(post, "instruction_addr", instruction, f"PostRender call {instruction}")
        require(row.get("mnemonic") == "CALL" and row.get("operands") == target,
                f"PostRender call target differs: {instruction}")
        positions.append(int(instruction, 16))
        call_rows.append({"instructionVa": instruction, "targetVa": target,
                          "sourceMethod": source_name})
    require(positions == sorted(positions), "retail PostRender call order differs")

    receiver_rows = {
        "0x0053ecfc": "0x8aa4e8",
        "0x0053ed74": "0x8aa4e8",
        "0x0053ef09": "0x8aa4e8",
        "0x0053ef59": "0x8aa4e8",
    }
    for instruction, receiver in receiver_rows.items():
        row = one(post, "instruction_addr", instruction, f"PostRender receiver {instruction}")
        require(row.get("mnemonic") == "MOV" and row.get("operands") == f"ECX, {receiver}",
                f"PostRender receiver differs: {instruction}")
    return {
        "caller": "0x0053ecc0",
        "receiver": "0x008aa4e8",
        "orderedCalls": call_rows,
        "bodyLandmarks": body_observations,
    }


def validate_inventory(functions: list[dict[str, str]], program: list[dict[str, str]]) -> dict[str, Any]:
    metrics = {row["metric"]: row["value"] for row in program}
    require(metrics.get("programName") == "BEA.exe", "Ghidra program name differs")
    require(metrics.get("executableSHA256") == SPECIMEN_SHA256, "Ghidra specimen differs")
    require(metrics.get("functions") == "8136" and metrics.get("instructions") == "549872",
            "Ghidra function/instruction census differs")
    rows = []
    for address, spec in TARGETS.items():
        row = one(functions, "address", address, f"Ghidra target {address}")
        require(row.get("name") == spec["preName"], f"Ghidra PRE name differs: {address}")
        require(row.get("nameSource") == "USER_DEFINED", f"Ghidra name source differs: {address}")
        require(row.get("signature") == spec["preSignature"], f"Ghidra signature differs: {address}")
        require(row.get("bodyBytes") == str(spec["bodyBytes"]), f"Ghidra body size differs: {address}")
        require(row.get("bodyDigest") == spec["bodyDigest"], f"Ghidra body digest differs: {address}")
        require(row.get("instrCount") == str(spec["instructionCount"]),
                f"Ghidra instruction count differs: {address}")
        require(row.get("commentSha256") == spec["commentSha256"],
                f"Ghidra PRE comment differs: {address}")
        rows.append({
            "address": address,
            "preName": spec["preName"],
            "postName": spec["postName"],
            "bodyDigest": spec["bodyDigest"],
            "instructionCount": spec["instructionCount"],
        })
    return {
        "functionCount": 8136,
        "instructionCount": 549872,
        "targets": rows,
    }


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def validate_lineage(root: Path) -> dict[str, Any]:
    lane = root / "local-lab/ghidra-cround-handle-event-arm-effects-live-promotion-20260812-v1"
    promotion = read_json(lane / "live-promotion-v2.ready.json")
    restore = read_json(lane / "tracked-snapshot-restore.ready.json")
    require(promotion.get("verdict") == "READY" and promotion.get("phase") == "LIVE_PROMOTED",
            "latest live Ghidra promotion is not READY")
    require(promotion.get("result", {}).get("trackedSnapshotMatchesLive") is True,
            "tracked/live Ghidra equality is not proven")
    require(restore.get("readonlyOpen", {}).get("opened") is True,
            "tracked Ghidra restore did not open")
    require(restore.get("readonlyOpen", {}).get("contentStable") is True,
            "tracked Ghidra restore was not content-stable")
    require(restore.get("copyComparison", {}).get("matches") is True,
            "tracked Ghidra restore copy differs")
    return {
        "livePromotionReadySha256": INPUTS[
            next(key for key in INPUTS if key.endswith("live-promotion-v2.ready.json"))][1],
        "trackedRestoreReadySha256": INPUTS[
            next(key for key in INPUTS if key.endswith("tracked-snapshot-restore.ready.json"))][1],
        "trackedSnapshotMatchesLive": True,
        "trackedRestoreReadOnlyOpen": True,
    }


def build(root: Path, generated_at: str) -> dict[str, Any]:
    datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    inputs = exact_inputs(root)
    image = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    source = validate_source_text(
        (root / "references/Onslaught/PCEngine.cpp").read_text(encoding="utf-8"),
        (root / "references/Onslaught/DXEngine.cpp").read_text(encoding="utf-8"),
    )
    retail = validate_retail_rows(read_tsv(root / W005_RELATIVE), read_tsv(root / W010_RELATIVE))
    inventory = validate_inventory(
        read_tsv(root / FUNCTIONS_RELATIVE), read_tsv(root / PROGRAM_RELATIVE))
    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "verdict": "READY",
        "generatedAtUtc": generated_at,
        "author": stamp(Path(__file__), root),
        "inputs": inputs,
        "lineage": validate_lineage(root),
        "pristine": validate_pristine(image),
        "sourceOrder": source,
        "retailOrder": retail,
        "ghidraPreimage": inventory,
        "adjudication": {
            "confidence": "HIGH_STATIC_SOURCE_IDENTITY",
            "corrections": [
                {"address": address, "from": spec["preName"], "to": spec["postName"]}
                for address, spec in TARGETS.items()
            ],
            "authorizedMutationEnvelope": {
                "functionNames": 3,
                "selfDescribingSignatures": 3,
                "functionComments": 3,
                "staleOrRequiredFunctionTags": 3,
                "functionBoundaries": 0,
                "programBytes": 0,
                "instructions": 0,
                "dataUnits": 0,
                "references": 0,
            },
        },
        "limitations": [
            "The supplied source variants corroborate source-method identity and order; they are not retail source-body proof.",
            "Retail body landmarks establish structural consistency, not every branch or field meaning.",
            "No visible rendering result, runtime output, complete side-effect set, or failure behavior is claimed.",
            "No reconstruction mapping or REBUILD_READY status is authorized.",
            "This receipt alone does not authorize a live Ghidra write; backup, scratch replicas, rollback probes, separate-process readback, and collateral comparison remain required.",
        ],
    }


def json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def publish_new(path: Path, content: bytes) -> None:
    require(not path.exists(), f"refusing to overwrite proof receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".partial",
                                     dir=path.parent, delete=False) as stream:
        partial = Path(stream.name)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(partial, path)
    finally:
        partial.unlink(missing_ok=True)


def validate_saved(saved: dict[str, Any], root: Path) -> None:
    require(saved == build(root, saved.get("generatedAtUtc", "")), "saved proof content differs")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    args = parser.parse_args()
    root = root_path()
    ready = root / EVIDENCE_RELATIVE / READY_NAME
    if args.command == "seal":
        payload = build(root, utc_now())
        publish_new(ready, json_bytes(payload))
        validate_saved(read_json(ready), root)
    else:
        validate_saved(read_json(ready), root)
    print(f"HUD_SOURCE_IDENTITY_REPROOF_READY sha256={sha256_file(ready)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
