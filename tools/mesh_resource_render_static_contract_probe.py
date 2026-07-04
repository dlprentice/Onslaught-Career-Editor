#!/usr/bin/env python3
"""Validate the mesh/resource/render static contract surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "mesh_resource_render_static_contract_wave1104_2026-06-04.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"


DEEP_TOKENS = (
    "Mesh / Resource / Render Static Contract",
    "mesh-resource-render-static-contract-wave1104",
    "texture-render-static-review-wave904",
    "mesh-motion-world-particle-static-review-wave905",
    "0x004499d0 CEngine__Init",
    "0x00449dc0 CEngine__LoadAllNamedMeshes",
    "0x0046e460 CGame__Render",
    "0x0053e220 CDXEngine__PreRender",
    "0x0053e2e0 CDXEngine__Render",
    "0x0053ecc0 CDXEngine__PostRender",
    "0x00513af0 D3DStateCache__SetSlotMode4or5",
    "0x00551920 CRenderQueue__BeginFrame",
    "0x005528b0 CRenderQueue__RenderAll",
    "0x00553960 CRenderQueue__RenderMultipassLayerA",
    "0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle",
    "0x004a5020 CMesh__Init",
    "0x004a5970 CMesh__LoadByNameWithStatus",
    "0x004a5b70 CMesh__Load",
    "0x004aa6e0 CMesh__FindOrCreate",
    "0x004aab90 CMesh__Deserialize",
    "DAT_00704ad8",
    "DAT_00704adc",
    "data\\Meshes",
    "data\\resources\\meshes\\m_%s.aya",
    "0x004ae860 CMeshPart__AllocateGeometry",
    "0x004af470 CMeshPart__LoadVerticesAndTriangles",
    "0x004afbb0 CMeshPart__LoadVerticesWithBones",
    "0x004b27a0 CMeshPart__LoadFromStream",
    "0x004b31f0 CMeshPart__OptimizePolygons",
    "resfile_cmeshpartsize",
    "0x13c",
    "0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
    "0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    "0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit",
    "CDXTexture__LoadTextureFromFile_Core",
    "CFastVB__RenderTriangleStripImmediate",
    "CVBufTexture__DrawSpriteEx",
    "847/847",
    "213/213",
    "139/139",
    "352/352",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260526-101300_post_wave904_texture_render_static_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-155838_post_wave1093_cengine_core_bootstrap_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-163255_post_wave1094_cdxengine_frame_render_spine_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-174618_post_wave1096_crenderqueue_core_multipass_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified",
    "6410/6410 = 100.00%",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "Runtime texture decode pixels",
    "Runtime mesh loading",
    "Native textured/animated WinUI rendering",
    "Rebuild parity",
)

OVERCLAIM_TOKENS = (
    "runtime render correctness proven",
    "runtime mesh loading proven",
    "native textured/animated winui rendering proven",
    "rebuild parity proven",
    "exact object layouts proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_deep_surface(path: Path, label: str, failures: list[str]) -> None:
    text = read_text(path)
    for token in DEEP_TOKENS:
        require(contains_token(text, token), f"{label} missing token: {token}", failures)
    for bad in OVERCLAIM_TOKENS:
        require(bad not in text.lower(), f"{label} overclaim token present: {bad}", failures)


def check_navigation(failures: list[str]) -> None:
    docs = {
        "mapped-systems.md": read_text(MAPPED_SYSTEMS),
        "_index.md": read_text(INDEX),
        "RE-INDEX.md": read_text(RE_INDEX),
        "static-reaudit-campaign.md": read_text(CAMPAIGN),
    }
    state_docs = {
        "developer_agent_state.json": read_text(DEVELOPER_STATE),
        "documentation_agent_state.json": read_text(DOCUMENTATION_STATE),
        "re_orchestrator_state.json": read_text(RE_STATE),
    }
    for name, text in docs.items():
        require("mesh-resource-render-static-contract.md" in text, f"{name} missing contract link token", failures)
        require("mesh-resource-render-static-contract-wave1104" in text, f"{name} missing Wave1104 tag", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"{name} overclaim token present: {bad}", failures)
    for name, text in state_docs.items():
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"{name} overclaim token present: {bad}", failures)

    mapped = docs["mapped-systems.md"]
    require("Mesh/resource/render static contract" in mapped, "mapped systems missing contract row/summary", failures)
    require("runtime render correctness" in mapped, "mapped systems missing runtime render boundary", failures)

    campaign = docs["static-reaudit-campaign.md"]
    require(
        "Current continuation: Wave1104" in campaign or "Prior continuation: Wave1104" in campaign,
        "campaign missing Wave1104 current/prior continuation anchor",
        failures,
    )
    require("Prior continuation: Wave1103" in campaign, "campaign missing Wave1103 demotion", failures)


def check_mirror(failures: list[str]) -> None:
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "mesh/resource/render contract lore mirror mismatch", failures)


def check_package_script(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    expected = r"py -3 tools\mesh_resource_render_static_contract_probe.py --check"
    require(scripts.get("test:mesh-resource-render-static-contract") == expected, "missing package mesh/resource/render contract script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_deep_surface(CONTRACT, "contract", failures)
    check_deep_surface(READINESS, "readiness", failures)
    check_navigation(failures)
    check_mirror(failures)
    check_package_script(failures)

    if failures:
        print("Mesh/resource/render static contract probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Mesh/resource/render static contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
