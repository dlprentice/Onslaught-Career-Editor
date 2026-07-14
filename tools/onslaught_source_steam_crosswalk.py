#!/usr/bin/env python3
"""Fail-closed validator for the bounded Onslaught source/Steam crosswalk."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path, PureWindowsPath
from typing import Any


SCHEMA_VERSION = "onslaught-source-steam-crosswalk.v1"
EXPECTED_SOURCE_REVISION = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"
SOURCE_PREFIX = "references/Onslaught/"
CROSSWALK_NAME = "onslaught-source-steam-crosswalk.v1.json"
EVIDENCE_LAYERS = [
    "sourceHypothesis",
    "steamStatic",
    "archiveObservation",
    "copiedRuntimeMeasurement",
    "rebuildContract",
]
TOP_KEYS = {"schemaVersion", "sourceRevision", "evidenceLayers", "rows"}
ROW_KEYS = {
    "id",
    "claim",
    "claimClass",
    *EVIDENCE_LAYERS,
    "requirements",
    "dependencies",
    "requiredDependencies",
    "declaredReadiness",
    "nonclaims",
}
READINESS_KEYS = {
    "staticCrosswalkReady",
    "runtimeMeasurementReady",
    "rebuildContractReady",
    "identityReady",
}
REQUIREMENTS = {
    "staticCrosswalk": ["sourceHypothesis", "steamStatic"],
    "runtimeMeasurement": ["staticCrosswalk", "copiedRuntimeMeasurement"],
    "rebuildContract": ["runtimeMeasurement", "rebuildContract"],
}
LAYER_STATUSES = {
    "sourceHypothesis": {"hypothesis-only"},
    "steamStatic": {
        "accepted-bounded-static",
        "partial-bounded-static",
        "required-not-established",
    },
    "archiveObservation": {"not-applicable", "reported-local-name-structure-lead"},
    "copiedRuntimeMeasurement": {
        "required-not-measured",
        "accepted-input-state-handoff-only",
        "accepted-copied-runtime-measurement",
    },
    "rebuildContract": {"blocked-until-runtime-accepted", "accepted-rebuild-contract"},
}
SOURCE_KEYS = {"status", "file", "symbol", "lineStart", "lineEnd", "requiredTokens"}
STEAM_KEYS = {
    "status",
    "address",
    "symbol",
    "evidence",
    "addressCandidates",
    "supportingAnchors",
}
ARCHIVE_KEYS = {
    "status",
    "evidence",
    "resourceName",
    "internalName",
    "partCount",
    "parentChildEdgeCount",
    "referenceCount",
    "boneCount",
}
RUNTIME_KEYS = {"status", "evidence", "measurementClass"}
REBUILD_KEYS = {"status", "evidence", "contractClass"}
EVIDENCE_ITEM_KEYS = {"file", "lineStart", "lineEnd", "requiredTokens"}
FORBIDDEN_KEY_PARTS = {
    "pid",
    "pointer",
    "machinepath",
    "processpath",
    "executablepath",
    "modulebase",
    "artifactpath",
    "logpath",
}
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{8}$")
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
PRIVATE_PATH_RE = re.compile(
    r"(?i)(?:(?<![a-z])[a-z]:(?!:)|\\\\|//\?/|~[\\/]|\$home(?:[\\/]|$)|%userprofile%(?:[\\/]|$))"
)


PRODUCTION_ORDER = [
    "battleengine_primary_mesh_role",
    "battleengine_render_object_init",
    "mesh_registry_load",
    "mesh_pose_hierarchy",
    "player_forward_route",
    "walker_forward",
    "walker_move",
    "walker_walk_cycle",
]
PRODUCTION_ROWS: dict[str, dict[str, Any]] = {
    "battleengine_primary_mesh_role": {
        "claimClass": "exact-player-resource-identity",
        "source": ("references/Onslaught/BattleEngine.cpp", "CBattleEngine::Init", 144, 167),
        "steam": ("partial-bounded-static", "0x00404dd0", "CBattleEngine__Init"),
        "archive": "reported-local-name-structure-lead",
        "runtime": "required-not-measured",
        "rebuild": "blocked-until-runtime-accepted",
        "dependencies": [],
    },
    "battleengine_render_object_init": {
        "claimClass": "render-resource-handoff",
        "source": ("references/Onslaught/BattleEngine.cpp", "CBattleEngine::Init", 146, 159),
        "steam": ("accepted-bounded-static", "0x004176c0", "CThing__InitRenderThingFromInitMeshName"),
        "archive": "not-applicable",
        "runtime": "required-not-measured",
        "rebuild": "blocked-until-runtime-accepted",
        "dependencies": [],
    },
    "mesh_registry_load": {
        "claimClass": "general-resource-registry",
        "source": ("references/Onslaught/engine.cpp", "CEngine::LoadAllNamedMeshes/CEngine::AddNewGlobalNamedMesh", 229, 279),
        "steam": ("accepted-bounded-static", "0x004a5970", "CMesh__LoadByNameWithStatus"),
        "archive": "not-applicable",
        "runtime": "required-not-measured",
        "rebuild": "blocked-until-runtime-accepted",
        "dependencies": [],
    },
    "mesh_pose_hierarchy": {
        "claimClass": "mesh-pose-hierarchy-contract",
        "source": ("references/Onslaught/thing.cpp", "CThing::GetTopPos", 472, 489),
        "steam": ("accepted-bounded-static", "0x004b4ba0", "CMeshPart__PopulatePoseCacheRecursive"),
        "archive": "reported-local-name-structure-lead",
        "runtime": "required-not-measured",
        "rebuild": "blocked-until-runtime-accepted",
        "dependencies": ["mesh_registry_load"],
    },
    "player_forward_route": {
        "claimClass": "input-to-walker-state-handoff",
        "source": ("references/Onslaught/Player.cpp", "CPlayer::ReceiveButtonAction", 415, 423),
        "steam": ("accepted-bounded-static", "0x004d3110", "CPlayer__ReceiveButtonAction"),
        "archive": "not-applicable",
        "runtime": "accepted-input-state-handoff-only",
        "rebuild": "blocked-until-runtime-accepted",
        "dependencies": [],
    },
    "walker_forward": {
        "claimClass": "walker-movement-static-candidate",
        "source": ("references/Onslaught/BattleEngineWalkerPart.cpp", "CBattleEngineWalkerPart::Forward", 119, 165),
        "steam": ("accepted-bounded-static", "0x00412d80", "CBattleEngineWalkerPart__Forward"),
        "archive": "not-applicable",
        "runtime": "required-not-measured",
        "rebuild": "blocked-until-runtime-accepted",
        "dependencies": ["player_forward_route"],
    },
    "walker_move": {
        "claimClass": "walker-movement-static-candidate",
        "source": ("references/Onslaught/BattleEngineWalkerPart.cpp", "CBattleEngineWalkerPart::Move", 361, 439),
        "steam": ("accepted-bounded-static", "0x00413760", "CBattleEngineWalkerPart__Move"),
        "archive": "not-applicable",
        "runtime": "required-not-measured",
        "rebuild": "blocked-until-runtime-accepted",
        "dependencies": ["walker_forward"],
    },
    "walker_walk_cycle": {
        "claimClass": "walker-animation-static-candidate",
        "source": ("references/Onslaught/BattleEngineWalkerPart.cpp", "CBattleEngineWalkerPart::UpdateWalkCycle", 38, 58),
        "steam": ("accepted-bounded-static", "0x00412ad0", "CBattleEngineWalkerPart__UpdateWalkCycle"),
        "archive": "not-applicable",
        "runtime": "required-not-measured",
        "rebuild": "blocked-until-runtime-accepted",
        "dependencies": ["walker_move"],
    },
}
PRODUCTION_SOURCE_TOKENS = {
    "battleengine_primary_mesh_role": ["m_be1.msh", "f_be1.msh", "SpawnRenderThing"],
    "battleengine_render_object_init": ["CRenderData", "RTID_CRTMesh", "mRenderThing->Init"],
    "mesh_registry_load": ["Loading named meshes", "AddNewGlobalNamedMesh", "CMESH::GetMesh(name)"],
    "mesh_pose_hierarchy": [
        "mesh->GetPart(0)->mOffsetPos",
        "mesh->GetPart(0)->mOrientation",
        "GetRenderOrientation",
    ],
    "player_forward_route": [
        "BATTLE_ENGINE_STATE_WALKER",
        "BUTTON_MECH_FORWARD",
        "GetWalkerPart()->Forward(val)",
    ],
    "walker_forward": ["IsOnGround", "mDoingDashCount", "mMainPart->AddVelocity(move)"],
    "walker_move": ["mGroundEnergyIncrease", "mWalkFriction", "mMaxWalkVelocity", "UpdateWalkCycle"],
    "walker_walk_cycle": [
        "ori.TransposeInPlace",
        "rel_vel.X*2.5f",
        "rel_vel.Y*3.0f",
        "PI_M2",
    ],
}
PRODUCTION_STEAM_EVIDENCE = {
    "battleengine_primary_mesh_role": [
        {
            "file": "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Init.md",
            "lineStart": 1,
            "lineEnd": 18,
            "requiredTokens": ["0x00404dd0", "m_be1.msh", "f_be1.msh"],
        }
    ],
    "battleengine_render_object_init": [
        {
            "file": "reverse-engineering/binary-analysis/wave1216-render-resource-texture-hud-tail-current-risk-review.md",
            "lineStart": 17,
            "lineEnd": 17,
            "requiredTokens": [
                "0x004176c0",
                "CThing__InitRenderThingFromInitMeshName",
                "Render-thing init bridge from init mesh name",
            ],
        }
    ],
    "mesh_registry_load": [
        {
            "file": "reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md",
            "lineStart": 116,
            "lineEnd": 123,
            "requiredTokens": [
                "0x004a5970 CMesh__LoadByNameWithStatus",
                "0x004aa6e0 CMesh__FindOrCreate",
                "0x004aab90 CMesh__Deserialize",
                "DAT_00704ad8",
                "data\\Meshes\\",
            ],
        }
    ],
    "mesh_pose_hierarchy": [
        {
            "file": "reverse-engineering/binary-analysis/functions/MeshPart.cpp/_index.md",
            "lineStart": 51,
            "lineEnd": 51,
            "requiredTokens": [
                "0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive",
                "recurses through child count/table",
                "+0x90/+0x94",
            ],
        }
    ],
    "player_forward_route": [
        {
            "file": "reverse-engineering/binary-analysis/functions/Player.cpp/_index.md",
            "lineStart": 35,
            "lineEnd": 38,
            "requiredTokens": [
                "0x004d3110",
                "CPlayer__ReceiveButtonAction",
                "walker part `+0x578` dispatch",
            ],
        }
    ],
    "walker_forward": [
        {
            "file": "reverse-engineering/binary-analysis/functions/BattleEngineWalkerPart.cpp/_index.md",
            "lineStart": 28,
            "lineEnd": 28,
            "requiredTokens": ["0x00412d80", "CBattleEngineWalkerPart__Forward"],
        }
    ],
    "walker_move": [
        {
            "file": "reverse-engineering/binary-analysis/functions/BattleEngineWalkerPart.cpp/_index.md",
            "lineStart": 34,
            "lineEnd": 34,
            "requiredTokens": ["0x00413760", "CBattleEngineWalkerPart__Move"],
        }
    ],
    "walker_walk_cycle": [
        {
            "file": "reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md",
            "lineStart": 53,
            "lineEnd": 65,
            "requiredTokens": [
                "0x00412ad0 CBattleEngineWalkerPart__UpdateWalkCycle",
                "larger-magnitude X/Y component",
                "runtime pending",
            ],
        }
    ],
}
PRODUCTION_RUNTIME_EVIDENCE = {
    "player_forward_route": [
        {
            "file": "reverse-engineering/binary-analysis/local-multiplayer-static-runtime-contract.md",
            "lineStart": 239,
            "lineEnd": 247,
            "requiredTokens": [
                "accepted claim remains input-to-state-store handoff",
                "not visible movement causality",
            ],
        }
    ]
}
PRODUCTION_CLAIM_TEXT_SHA256 = (
    "d058c8b7202bd5f5c7e2eddcfeac6978902aa84e49a5818fee9409eb0f7f2d97"
)
PRODUCTION_SUPPORTING_ANCHORS = {
    "mesh_registry_load": [
        "0x004a5b70 CMesh__Load",
        "0x004aa6e0 CMesh__FindOrCreate",
        "0x004aab90 CMesh__Deserialize",
        "DAT_00704ad8",
    ]
}
PRODUCTION_ARCHIVE_LAYERS = {
    "battleengine_primary_mesh_role": {
        "status": "reported-local-name-structure-lead",
        "evidence": [],
        "resourceName": "m_f_be1.msh.aya",
        "internalName": "f_be1.msh",
        "partCount": 63,
        "parentChildEdgeCount": 62,
        "referenceCount": 15,
        "boneCount": 0,
    },
    "mesh_pose_hierarchy": {
        "status": "reported-local-name-structure-lead",
        "evidence": [],
        "resourceName": "m_f_be1.msh.aya",
        "partCount": 63,
        "parentChildEdgeCount": 62,
        "referenceCount": 15,
        "boneCount": 0,
    },
}
for _production_row_id in PRODUCTION_ORDER:
    PRODUCTION_ARCHIVE_LAYERS.setdefault(
        _production_row_id, {"status": "not-applicable", "evidence": []}
    )


class CrosswalkValidationError(ValueError):
    """Raised when evidence cannot support the declared crosswalk."""


def _fail(message: str) -> None:
    raise CrosswalkValidationError(message)


def _normalized_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def _looks_private_path(text: str) -> bool:
    return (
        bool(PRIVATE_PATH_RE.search(text))
        or Path(text).is_absolute()
        or PureWindowsPath(text).is_absolute()
    )


def _check_privacy(value: Any, key: str | None = None) -> None:
    if key is not None:
        normalized = _normalized_key(key)
        if any(part in normalized for part in FORBIDDEN_KEY_PARTS):
            _fail(f"forbidden private/runtime field: {key}")
    if isinstance(value, dict):
        for child_key, child in value.items():
            _check_privacy(child, str(child_key))
    elif isinstance(value, list):
        for child in value:
            _check_privacy(child, key)
    elif isinstance(value, str) and _looks_private_path(value):
        _fail("private or absolute path is forbidden")


def _require_exact_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(value) - allowed
    if unknown:
        _fail(f"{label}: unknown field {sorted(unknown)[0]}")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be a non-empty string")
    return value


def _require_string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        _fail(f"{label} must be a string list")
    if nonempty and not value:
        _fail(f"{label} must be non-empty")
    if len(value) != len(set(value)):
        _fail(f"{label} contains duplicates")
    return value


def _require_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        _fail(f"{label} must be an integer >= {minimum}")
    return value


def _safe_file(root: Path, relative: str, label: str) -> Path:
    if _looks_private_path(relative):
        _fail("private or absolute path is forbidden")
    root = Path(root).absolute()
    relative_path = Path(relative)
    if any(part in {"", ".", ".."} for part in relative_path.parts):
        _fail("private or absolute path is forbidden")
    candidate = root
    components = [root, *(root.joinpath(*relative_path.parts[:index]) for index in range(1, len(relative_path.parts) + 1))]
    for index, component in enumerate(components):
        try:
            metadata = os.lstat(component)
        except OSError:
            _fail(f"{label} file is absent: {relative}")
        is_reparse = bool(
            getattr(metadata, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        )
        if stat.S_ISLNK(metadata.st_mode) or is_reparse:
            _fail(f"{label} path contains a reparse component")
        if index < len(components) - 1 and not stat.S_ISDIR(metadata.st_mode):
            _fail(f"{label} file is absent: {relative}")
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        _fail("private or absolute path is forbidden")
    if not stat.S_ISREG(os.lstat(candidate).st_mode):
        _fail(f"{label} file is absent: {relative}")
    return candidate


def _bounded_tokens(path: Path, start: Any, end: Any, tokens: Any, label: str) -> str:
    start = _require_int(start, f"{label} lineStart", minimum=1)
    end = _require_int(end, f"{label} lineEnd", minimum=1)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if end < start or end > len(lines):
        _fail(f"{label} range is invalid")
    required = _require_string_list(tokens, f"{label} requiredTokens", nonempty=True)
    bounded = "\n".join(lines[start - 1 : end])
    for token in required:
        if token not in bounded:
            _fail(f"{label} token is absent: {token}")
    return bounded


def _source_file(source_root: Path, relative: str) -> Path:
    normalized = relative.replace("\\", "/")
    if not normalized.startswith(SOURCE_PREFIX):
        _fail(f"source file must be below {SOURCE_PREFIX}")
    return _safe_file(source_root, normalized[len(SOURCE_PREFIX) :], "source")


def _validate_source(row_id: str, layer: dict[str, Any], source_root: Path) -> None:
    _require_exact_keys(layer, SOURCE_KEYS, f"{row_id}.sourceHypothesis")
    if layer.get("status") != "hypothesis-only":
        _fail(f"unsupported sourceHypothesis status: {layer.get('status')}")
    relative = _require_string(layer.get("file"), f"{row_id} source file")
    _require_string(layer.get("symbol"), f"{row_id} source symbol")
    path = _source_file(source_root, relative)
    _bounded_tokens(
        path,
        layer.get("lineStart"),
        layer.get("lineEnd"),
        layer.get("requiredTokens"),
        "source",
    )


def _allowed_evidence_path(relative: str, layer_name: str, repo_root: Path) -> bool:
    normalized = relative.replace("\\", "/")
    roots = {
        "steamStatic": "reverse-engineering/binary-analysis",
        "copiedRuntimeMeasurement": "reverse-engineering/binary-analysis",
        "archiveObservation": "reverse-engineering/game-assets",
        "rebuildContract": "rebuild",
    }[layer_name]
    if _looks_private_path(normalized) or Path(normalized).name == CROSSWALK_NAME:
        return False
    candidate = (repo_root / normalized).resolve()
    allowed_root = (repo_root / roots).resolve()
    try:
        candidate.relative_to(allowed_root)
    except ValueError:
        return False
    return True


def _validate_evidence(
    row_id: str,
    evidence: Any,
    repo_root: Path,
    layer_name: str,
    *,
    nonempty: bool,
) -> list[str]:
    if not isinstance(evidence, list):
        _fail(f"{row_id}.{layer_name}.evidence must be a list")
    if nonempty and not evidence:
        _fail(f"{row_id}.{layer_name} accepted status requires evidence")
    bounded_texts: list[str] = []
    for item in evidence:
        if not isinstance(item, dict):
            _fail(f"{row_id}.{layer_name}: malformed evidence item")
        _require_exact_keys(item, EVIDENCE_ITEM_KEYS, f"{row_id}.{layer_name}.evidence")
        relative = _require_string(item.get("file"), f"{row_id}.{layer_name} evidence file")
        if not _allowed_evidence_path(relative, layer_name, repo_root):
            _fail(f"{row_id}.{layer_name}: unsupported evidence path")
        path = _safe_file(repo_root, relative, f"{layer_name} evidence")
        bounded_texts.append(
            _bounded_tokens(
                path,
                item.get("lineStart"),
                item.get("lineEnd"),
                item.get("requiredTokens"),
                f"{layer_name} evidence",
            )
        )
    return bounded_texts


def _validate_steam(
    row_id: str,
    layer: dict[str, Any],
    repo_root: Path,
    addresses: set[str],
    symbols: set[str],
) -> bool:
    _require_exact_keys(layer, STEAM_KEYS, f"{row_id}.steamStatic")
    status = layer.get("status")
    if status not in LAYER_STATUSES["steamStatic"]:
        _fail(f"unsupported steamStatic status: {status}")
    candidates = layer.get("addressCandidates")
    if candidates not in (None, []):
        _fail(f"{row_id}: ambiguous Steam address")
    if status == "required-not-established":
        if set(layer) != {"status", "evidence"} or layer.get("evidence") != []:
            _fail(f"{row_id}: unestablished Steam layer carries promotion fields")
        return False
    address = _require_string(layer.get("address"), f"{row_id} Steam address").lower()
    symbol = _require_string(layer.get("symbol"), f"{row_id} Steam symbol")
    if not ADDRESS_RE.fullmatch(address):
        _fail(f"{row_id}: Steam address is malformed")
    normalized_symbol = symbol.casefold()
    if address in addresses:
        _fail(f"duplicate or conflicting Steam address: {address}")
    if normalized_symbol in symbols:
        _fail(f"duplicate Steam symbol: {symbol}")
    addresses.add(address)
    symbols.add(normalized_symbol)
    anchors: list[str] = []
    if "supportingAnchors" in layer:
        anchors = _require_string_list(
            layer["supportingAnchors"], f"{row_id} supportingAnchors", nonempty=True
        )
    bounded_evidence = _validate_evidence(
        row_id, layer.get("evidence"), repo_root, "steamStatic", nonempty=True
    )
    bounded_text = "\n".join(bounded_evidence)
    for anchor in anchors:
        if anchor not in bounded_text:
            _fail(f"{row_id}: supporting anchor is absent from bounded evidence")
    return status == "accepted-bounded-static"


def _validate_archive(row_id: str, layer: dict[str, Any], repo_root: Path) -> None:
    _require_exact_keys(layer, ARCHIVE_KEYS, f"{row_id}.archiveObservation")
    status = layer.get("status")
    if status not in LAYER_STATUSES["archiveObservation"]:
        _fail(f"unsupported archiveObservation status: {status}")
    if status == "not-applicable":
        if set(layer) != {"status", "evidence"} or layer.get("evidence") != []:
            _fail(f"{row_id}: not-applicable archive layer carries observation fields")
        return
    _require_string(layer.get("resourceName"), f"{row_id} archive resourceName")
    for name in ("partCount", "parentChildEdgeCount", "referenceCount", "boneCount"):
        _require_int(layer.get(name), f"{row_id} archive {name}")
    if "internalName" in layer:
        _require_string(layer["internalName"], f"{row_id} archive internalName")
    _validate_evidence(row_id, layer.get("evidence"), repo_root, "archiveObservation", nonempty=False)


def _validate_runtime(row_id: str, layer: dict[str, Any], repo_root: Path) -> tuple[bool, bool]:
    _require_exact_keys(layer, RUNTIME_KEYS, f"{row_id}.copiedRuntimeMeasurement")
    status = layer.get("status")
    if status not in LAYER_STATUSES["copiedRuntimeMeasurement"]:
        _fail(f"unsupported copiedRuntimeMeasurement status: {status}")
    if status == "required-not-measured":
        if set(layer) != {"status", "evidence"} or layer.get("evidence") != []:
            _fail(f"{row_id}: unmeasured runtime layer carries promotion fields")
        return False, False
    measurement_class = _require_string(
        layer.get("measurementClass"), f"{row_id} runtime measurementClass"
    )
    allowed = (
        {"input-state-handoff"}
        if status == "accepted-input-state-handoff-only"
        else {"scalar-behavior", "exact-resource-identity"}
    )
    if measurement_class not in allowed:
        _fail(f"{row_id}: unsupported runtime measurementClass")
    has_evidence = bool(_validate_evidence(
        row_id,
        layer.get("evidence"),
        repo_root,
        "copiedRuntimeMeasurement",
        nonempty=True,
    ))
    runtime_ready = status == "accepted-copied-runtime-measurement" and has_evidence
    return runtime_ready, runtime_ready and measurement_class == "exact-resource-identity"


def _validate_rebuild(row_id: str, layer: dict[str, Any], repo_root: Path) -> bool:
    _require_exact_keys(layer, REBUILD_KEYS, f"{row_id}.rebuildContract")
    status = layer.get("status")
    if status not in LAYER_STATUSES["rebuildContract"]:
        _fail(f"unsupported rebuildContract status: {status}")
    if status == "blocked-until-runtime-accepted":
        if set(layer) != {"status", "evidence"} or layer.get("evidence") != []:
            _fail(f"{row_id}: blocked rebuild layer carries promotion fields")
        return False
    if layer.get("contractClass") != "accepted-public-behavior-contract":
        _fail(f"{row_id}: unsupported rebuild contractClass")
    return bool(_validate_evidence(
        row_id, layer.get("evidence"), repo_root, "rebuildContract", nonempty=True
    ))


def _validate_production_profile(rows: list[dict[str, Any]]) -> None:
    ids = [row["id"] for row in rows]
    if ids != PRODUCTION_ORDER:
        _fail("production profile requires the exact eight row ids and order")
    claim_text = [
        {"id": row["id"], "claim": row["claim"], "nonclaims": row["nonclaims"]}
        for row in rows
    ]
    claim_text_sha256 = hashlib.sha256(
        json.dumps(
            claim_text,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()
    if claim_text_sha256 != PRODUCTION_CLAIM_TEXT_SHA256:
        _fail("production claim/nonclaim text mismatch")
    for row in rows:
        row_id = row["id"]
        expected = PRODUCTION_ROWS[row_id]
        source = row["sourceHypothesis"]
        steam = row["steamStatic"]
        actual_source = (
            source["file"],
            source["symbol"],
            source["lineStart"],
            source["lineEnd"],
        )
        actual_steam = (steam["status"], steam["address"], steam["symbol"])
        dependencies = row.get("dependencies", [])
        required = row.get("requiredDependencies", [])
        if row["claimClass"] != expected["claimClass"]:
            _fail(f"{row_id}: production claimClass mismatch")
        if actual_source != expected["source"]:
            _fail(f"{row_id}: production source anchor mismatch")
        if source["requiredTokens"] != PRODUCTION_SOURCE_TOKENS[row_id]:
            _fail(f"{row_id}: production source tokens mismatch")
        if actual_steam != expected["steam"]:
            _fail(f"{row_id}: production Steam anchor/status mismatch")
        if steam["evidence"] != PRODUCTION_STEAM_EVIDENCE[row_id]:
            _fail(f"{row_id}: production Steam evidence mismatch")
        if steam.get("supportingAnchors", []) != PRODUCTION_SUPPORTING_ANCHORS.get(
            row_id, []
        ):
            _fail(f"{row_id}: production supporting anchors mismatch")
        if row["archiveObservation"]["status"] != expected["archive"]:
            _fail(f"{row_id}: production archive status mismatch")
        if row["copiedRuntimeMeasurement"]["status"] != expected["runtime"]:
            _fail(f"{row_id}: production runtime status mismatch")
        expected_runtime_evidence = PRODUCTION_RUNTIME_EVIDENCE.get(row_id, [])
        if row["copiedRuntimeMeasurement"]["evidence"] != expected_runtime_evidence:
            _fail(f"{row_id}: production runtime evidence mismatch")
        if row["rebuildContract"]["status"] != expected["rebuild"]:
            _fail(f"{row_id}: production rebuild status mismatch")
        if dependencies != expected["dependencies"]:
            _fail(f"{row_id}: production dependency mismatch")
        if required != expected["dependencies"]:
            _fail(f"{row_id}: production required dependency mismatch")
        if row["archiveObservation"] != PRODUCTION_ARCHIVE_LAYERS[row_id]:
            _fail(f"{row_id}: production archive observation mismatch")


def _validate_core(
    value: Any,
    repo_root: Path,
    source_root: Path,
    observed_source_revision: str,
    *,
    production_profile: bool,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("document root must be an object")
    document = copy.deepcopy(value)
    repo_root = Path(repo_root).resolve()
    source_root = Path(source_root).resolve()
    _check_privacy(document)
    _require_exact_keys(document, TOP_KEYS, "document")
    if document.get("schemaVersion") != SCHEMA_VERSION:
        _fail("unsupported schema version")
    if (
        document.get("sourceRevision") != EXPECTED_SOURCE_REVISION
        or observed_source_revision != EXPECTED_SOURCE_REVISION
    ):
        _fail("source revision mismatch")
    if document.get("evidenceLayers") != EVIDENCE_LAYERS:
        _fail("unsupported or mixed evidence vocabulary")
    rows = document.get("rows")
    if not isinstance(rows, list) or not rows:
        _fail("rows must be a non-empty list")

    by_id: dict[str, dict[str, Any]] = {}
    addresses: set[str] = set()
    symbols: set[str] = set()
    layer_ready: dict[str, dict[str, bool]] = {}
    for row in rows:
        if not isinstance(row, dict):
            _fail("malformed row")
        _require_exact_keys(row, ROW_KEYS, "row")
        row_id = _require_string(row.get("id"), "row id")
        if not ID_RE.fullmatch(row_id) or row_id in by_id:
            _fail(f"duplicate or malformed row id: {row_id}")
        _require_string(row.get("claim"), f"{row_id} claim")
        _require_string(row.get("claimClass"), f"{row_id} claimClass")
        _require_string_list(row.get("nonclaims"), f"{row_id} nonclaims", nonempty=True)
        by_id[row_id] = row
        for layer_name in EVIDENCE_LAYERS:
            layer = row.get(layer_name)
            if not isinstance(layer, dict):
                _fail(f"{row_id}: missing evidence layer {layer_name}")
            if layer.get("status") not in LAYER_STATUSES[layer_name]:
                _fail(f"unsupported {layer_name} status: {layer.get('status')}")
        _validate_source(row_id, row["sourceHypothesis"], source_root)
        steam_ready = _validate_steam(row_id, row["steamStatic"], repo_root, addresses, symbols)
        _validate_archive(row_id, row["archiveObservation"], repo_root)
        runtime_ready, identity_evidence_ready = _validate_runtime(
            row_id, row["copiedRuntimeMeasurement"], repo_root
        )
        rebuild_ready = _validate_rebuild(row_id, row["rebuildContract"], repo_root)
        if row.get("requirements") != REQUIREMENTS:
            _fail(f"{row_id}: incomplete or unsupported readiness requirements")
        layer_ready[row_id] = {
            "sourceHypothesis": True,
            "steamStatic": steam_ready,
            "copiedRuntimeMeasurement": runtime_ready,
            "rebuildContract": rebuild_ready,
            "identityEvidence": identity_evidence_ready,
        }

    if production_profile:
        _validate_production_profile(rows)

    for row_id, row in by_id.items():
        dependencies = _require_string_list(row.get("dependencies", []), f"{row_id} dependencies")
        required = _require_string_list(
            row.get("requiredDependencies", []), f"{row_id} requiredDependencies"
        )
        for dependency in required:
            if dependency not in dependencies:
                _fail(f"{row_id}: required dependency is absent: {dependency}")
        for dependency in dependencies:
            if dependency not in by_id:
                _fail(f"{row_id}: unknown dependency: {dependency}")

    visiting: list[str] = []
    visited: set[str] = set()

    def visit(row_id: str) -> None:
        if row_id in visiting:
            start = visiting.index(row_id)
            _fail("dependency cycle: " + " -> ".join(visiting[start:] + [row_id]))
        if row_id in visited:
            return
        visiting.append(row_id)
        for dependency in by_id[row_id].get("dependencies", []):
            visit(dependency)
        visiting.pop()
        visited.add(row_id)

    for row_id in by_id:
        visit(row_id)

    computed: dict[str, dict[str, bool]] = {}

    def compute(row_id: str) -> dict[str, bool]:
        if row_id in computed:
            return computed[row_id]
        row = by_id[row_id]
        dependencies = [compute(item) for item in row.get("dependencies", [])]
        layers = layer_ready[row_id]
        static_ready = layers["sourceHypothesis"] and layers["steamStatic"] and all(
            item["staticCrosswalkReady"] for item in dependencies
        )
        runtime_ready = static_ready and layers["copiedRuntimeMeasurement"] and all(
            item["runtimeMeasurementReady"] for item in dependencies
        )
        rebuild_ready = runtime_ready and layers["rebuildContract"] and all(
            item["rebuildContractReady"] for item in dependencies
        )
        identity_ready = (
            runtime_ready
            and row["claimClass"] == "exact-player-resource-identity"
            and layers["identityEvidence"]
        )
        declared = row.get("declaredReadiness")
        if (
            row["claimClass"] == "exact-player-resource-identity"
            and not layers["steamStatic"]
            and isinstance(declared, dict)
            and declared.get("identityReady") is True
            and any(
                by_id[item]["claimClass"] == "general-resource-registry"
                for item in row.get("dependencies", [])
            )
        ):
            _fail("general registry evidence cannot promote exact identity")
        readiness = {
            "staticCrosswalkReady": static_ready,
            "runtimeMeasurementReady": runtime_ready,
            "rebuildContractReady": rebuild_ready,
            "identityReady": identity_ready,
        }
        if (
            not isinstance(declared, dict)
            or set(declared) != READINESS_KEYS
            or any(type(value) is not bool for value in declared.values())
            or declared != readiness
        ):
            _fail(f"{row_id}: declared readiness does not match computed readiness")
        computed[row_id] = readiness
        return readiness

    report_rows = [
        {"id": row_id, "computedReadiness": compute(row_id)} for row_id in by_id
    ]
    return {
        "status": "pass",
        "sourceRevision": EXPECTED_SOURCE_REVISION,
        "rows": report_rows,
    }


def _require_regular_git_blobs(
    root: Path,
    paths: list[str],
    *,
    unavailable_message: str,
    invalid_mode_message: str,
) -> None:
    if not paths:
        return
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--stage",
                "--",
                *paths,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        _fail(unavailable_message)
    if result.returncode != 0:
        _fail(unavailable_message)
    entries: dict[str, tuple[str, str]] = {}
    for line in result.stdout.splitlines():
        try:
            metadata, relative = line.split("\t", 1)
            mode, _object_id, stage = metadata.split()
        except ValueError:
            _fail(unavailable_message)
        if relative in entries:
            _fail(invalid_mode_message)
        entries[relative] = (mode, stage)
    if set(entries) != set(paths):
        _fail(unavailable_message)
    if any(
        stage != "0" or mode not in {"100644", "100755"}
        for mode, stage in entries.values()
    ):
        _fail(invalid_mode_message)


def _git_revision(source_root: Path, source_paths: list[str] | None = None) -> str:
    source_root = Path(source_root).resolve()
    if not source_root.is_dir() or not (source_root / ".git").exists():
        _fail("source revision is unavailable")
    try:
        top = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
        revision = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        status = subprocess.run(
            [
                "git",
                "-C",
                str(source_root),
                "status",
                "--porcelain=v1",
                "--untracked-files=no",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        _fail("source revision is unavailable")
    if (
        top.returncode != 0
        or revision.returncode != 0
        or status.returncode != 0
        or Path(top.stdout.strip()).resolve() != source_root
    ):
        _fail("source revision is unavailable")
    if status.stdout.strip():
        _fail("source working tree is not clean")
    _require_regular_git_blobs(
        source_root,
        source_paths or [],
        unavailable_message="source revision is unavailable",
        invalid_mode_message="source path is not a regular blob",
    )
    return revision.stdout.strip()


def _production_evidence_paths(value: dict[str, Any]) -> list[str]:
    paths = {
        item["file"].replace("\\", "/")
        for row in value["rows"]
        for layer_name in EVIDENCE_LAYERS[1:]
        for item in row[layer_name].get("evidence", [])
    }
    return sorted(paths)


def _declared_source_paths(value: Any) -> list[str]:
    if not isinstance(value, dict) or not isinstance(value.get("rows"), list):
        return []
    paths: set[str] = set()
    for row in value["rows"]:
        if not isinstance(row, dict):
            continue
        layer = row.get("sourceHypothesis")
        if not isinstance(layer, dict):
            continue
        relative = layer.get("file")
        if isinstance(relative, str) and relative.startswith(SOURCE_PREFIX):
            paths.add(relative[len(SOURCE_PREFIX) :].replace("\\", "/"))
    return sorted(paths)


def _declared_evidence_paths(value: Any) -> list[str]:
    if not isinstance(value, dict) or not isinstance(value.get("rows"), list):
        return []
    paths: set[str] = set()
    for row in value["rows"]:
        if not isinstance(row, dict):
            continue
        for layer_name in EVIDENCE_LAYERS[1:]:
            layer = row.get(layer_name)
            if not isinstance(layer, dict) or not isinstance(layer.get("evidence"), list):
                continue
            for item in layer["evidence"]:
                if isinstance(item, dict) and isinstance(item.get("file"), str):
                    paths.add(item["file"].replace("\\", "/"))
    return sorted(paths)


def _git_evidence_revision(repo_root: Path, evidence_paths: list[str]) -> str:
    repo_root = Path(repo_root).resolve()
    if not evidence_paths:
        _fail("repository evidence set is empty")
    try:
        top = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
        revision = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        status = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "status",
                "--porcelain=v1",
                "--untracked-files=no",
                "--",
                *evidence_paths,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        _fail("repository evidence revision is unavailable")
    if (
        top.returncode != 0
        or revision.returncode != 0
        or status.returncode != 0
        or Path(top.stdout.strip()).resolve() != repo_root
    ):
        _fail("repository evidence revision is unavailable")
    if status.stdout.strip():
        _fail("repository evidence working tree is not clean")
    _require_regular_git_blobs(
        repo_root,
        evidence_paths,
        unavailable_message="repository evidence revision is unavailable",
        invalid_mode_message="repository evidence path is not a regular blob",
    )
    return revision.stdout.strip()


def validate_document(
    value: Any,
    repo_root: Path,
    *,
    source_root: Path | None = None,
) -> dict[str, Any]:
    """Validate the exact production profile against a real pinned Git source root."""

    repo_root = Path(repo_root).resolve()
    source_root = (
        Path(source_root).resolve()
        if source_root is not None
        else (repo_root / "references" / "Onslaught").resolve()
    )
    source_paths = _declared_source_paths(value)
    evidence_paths = _declared_evidence_paths(value)
    observed_source = _git_revision(source_root, source_paths)
    observed_evidence = (
        _git_evidence_revision(repo_root, evidence_paths) if evidence_paths else None
    )
    report = _validate_core(
        value,
        repo_root,
        source_root,
        observed_source,
        production_profile=True,
    )
    if observed_evidence is None:
        evidence_paths = _production_evidence_paths(value)
        observed_evidence = _git_evidence_revision(repo_root, evidence_paths)
    if _git_evidence_revision(repo_root, evidence_paths) != observed_evidence:
        _fail("repository evidence revision changed during validation")
    if _git_revision(source_root, source_paths) != observed_source:
        _fail("source revision changed during validation")
    return report


def _validate_test_document(value: Any, repo_root: Path) -> dict[str, Any]:
    """Exercise generic schema rules against generated source-shaped fixtures."""

    repo_root = Path(repo_root).resolve()
    return _validate_core(
        value,
        repo_root,
        repo_root / "references" / "Onslaught",
        EXPECTED_SOURCE_REVISION,
        production_profile=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("crosswalk", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.crosswalk.read_text(encoding="utf-8"))
        report = validate_document(value, args.repo_root, source_root=args.source_root)
    except OSError:
        print("FAIL: crosswalk file is unavailable", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("FAIL: crosswalk JSON is malformed", file=sys.stderr)
        return 1
    except CrosswalkValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
