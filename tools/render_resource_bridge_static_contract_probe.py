#!/usr/bin/env python3
"""Validate the render-resource bridge static contract.

This checker consumes only tracked public Markdown and package metadata. It
does not inspect ignored payload overlays, private manifests, raw proof bundles,
copied executables, live Ghidra state, runtime logs, auth/session/cache data, or
secrets. It validates that the bridge remains source/static planning context
and does not become runtime, GPU, visual, importer, generated-output, or rebuild
proof.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "render-resource-bridge-static-contract.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "render-resource-bridge-static-contract.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BINARY_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
AYA_TAG_CONTRACT = ROOT / "reverse-engineering" / "game-assets" / "aya-resource-tag-family-static-contract.md"
ENGINE_SYSTEM = ROOT / "reverse-engineering" / "source-code" / "core" / "engine-system.md"
MESH_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
TEXTURE_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
DXMESH_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
DXTEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
CHAIN_MAP = ROOT / "roadmap" / "rebuild-front-door-chain-map.md"
PACKAGE_JSON = ROOT / "package.json"

PLAN_NAME = "render-resource-bridge-static-contract.md"
SCOPE = "render-resource-bridge-static-contract"
ALIAS = "render-resource-bridge-static-contract"
PACKAGE_SCRIPT = "test:render-resource-bridge-static-contract"
PACKAGE_COMMAND = r"py -3 tools\render_resource_bridge_static_contract_probe.py --check"
BRIDGE_ITEMS = ("`MESH` loader vocabulary", "`TEXT` loader vocabulary", "Material/texture sidecar metadata", "Render-loop handoff")

REQUIRED_PLAN_TOKENS = (
    "Status: source/static public-safe bridge contract, not runtime or visual proof",
    f"Scope: `{SCOPE}`",
    "how should the tracked AYA loader vocabulary for `MESH` and `TEXT` be routed",
    "use `MESH` and `TEXT` only as bridge vocabulary",
    "The current proof class is Tier C source engine architecture plus Tier B retail/static",
    "Tier C source engine architecture",
    "Tier B retail/static render and decode docs",
    "Tier A runtime/GPU/visual proof",
    "Not used in this slice.",
    "Device behavior, rendered frames, texture pixels, animation/skinning",
    "Higher authority still required",
    "`CMesh`, `CMeshPart`, `CDXMeshVB`, and `CMeshRenderer`",
    "`CTexture` and `CDXTexture`",
    "`CEngine`, `CDXEngine`, `CRenderQueue`, `CFastVB`, and `CVBufTexture`",
    "This checker-backed slice may read only tracked public Markdown and package",
    "launch BEA",
    "attach CDB",
    "mutate Ghidra",
    "patch an executable",
    "mutate an installed game",
    "run an extractor",
    "execute an importer",
    "generate asset payloads",
    "claim runtime parser behavior",
    "runtime texture decode behavior",
    "GPU upload",
    "texture pixels",
    "runtime mesh loading",
    "animation/skinning",
    "material appearance",
    "shader behavior",
    "visual output",
    "renderer behavior",
    "rebuild parity",
    "runtime parity",
    "no-noticeable-difference",
    "add AppCore, WinUI, CLI, Godot, renderer implementation, release",
    "binary-analysis indexes link this contract",
    "without changing active rebuild proof scope",
    "No runtime proof, extractor run",
    "importer execution, generated asset output, renderer implementation",
    "product exposure, or release action",
)

REQUIRED_PLAN_LINK_PATHS = (
    "reverse-engineering/game-assets/aya-resource-tag-family-static-contract.md",
    "reverse-engineering/source-code/core/engine-system.md",
    "reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md",
    "reverse-engineering/binary-analysis/texture-resource-decode-static-contract.md",
    "reverse-engineering/binary-analysis/functions/DXMeshVB.cpp/_index.md",
    "reverse-engineering/binary-analysis/functions/DXTexture.cpp/_index.md",
    "roadmap/rebuild-front-door-chain-map.md",
)

ANCHOR_TOKENS = {
    AYA_TAG_CONTRACT: (
        "`MESH`",
        "`TEXT`",
        "public-safe loader-contract vocabulary only",
        "Higher authority still required",
    ),
    ENGINE_SYSTEM: (
        "DirectX 8",
        "Render Pipeline",
        "All rendering state is runtime-only",
    ),
    MESH_CONTRACT: (
        "Mesh / Resource / Render Static Contract",
        "CMesh__Deserialize",
        "CDXMeshVB",
        "CMeshRenderer__RenderMesh",
        "Runtime texture decode pixels or GPU upload results",
        "Rebuild parity",
    ),
    TEXTURE_CONTRACT: (
        "Texture Resource Decode Static Contract",
        "Archive/resource ingress",
        "Render-facing handoff",
        "Runtime texture pixels and GPU upload behavior",
    ),
    DXMESH_INDEX: (
        "CDXMeshVB__Load",
        "CMeshRenderer__RenderMeshWithLayerPasses",
        "Runtime Direct3D behavior",
    ),
    DXTEXTURE_INDEX: (
        "CDXTexture__LoadTextureFromFile",
        "CDXTexture__Deserialize",
        "Runtime texture output behavior",
    ),
    BINARY_INDEX: (
        PLAN_NAME,
        ALIAS,
        "source/static bridge contract",
        "not runtime proof",
    ),
    LORE_BINARY_INDEX: (
        PLAN_NAME,
        ALIAS,
        "source/static bridge contract",
        "not runtime proof",
    ),
    CHAIN_MAP: (
        PLAN_NAME,
        ALIAS,
        "render-resource bridge side guard",
        "source/static bridge vocabulary",
        "does not change the active rebuild proof scope",
    ),
}

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)/(?:home|mnt|var|opt|tmp|users?)/"), "machine-local absolute path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)(?<![A-Za-z0-9-])(?:local-)?game[\\/]"), "private game mirror path"),
    (re.compile(r"(?i)(?<![A-Za-z0-9-])(?:local-)?media[\\/]"), "private media path"),
    (re.compile(r"(?i)save-attempts[\\/]"), "private save path"),
    (re.compile(r"(?i)(?:local-)?proofs?[\\/]"), "private proof path"),
    (re.compile(r"(?i)(?:local-ghidra|ghidra-local)[\\/]"), "private Ghidra path"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framebytelength"), "private frame locator field"),
    (re.compile(r"(?i)password|token=|secret="), "secret-like marker"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"\b[a-fA-F0-9]{40}\b"), "raw digest-like value"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime parser behavior proven",
    "runtime texture decode behavior proven",
    "gpu upload proven",
    "texture pixels proven",
    "runtime mesh loading proven",
    "animation proof complete",
    "skinning proof complete",
    "material appearance proven",
    "shader behavior proven",
    "visual output proven",
    "renderer behavior proven",
    "visual proof complete",
    "runtime proof complete",
    "generated asset output complete",
    "extractor run complete",
    "importer execution complete",
    "real importer executed",
    "rebuild parity proven",
    "runtime parity proven",
    "no-noticeable-difference parity proven",
    "appcore support added",
    "winui support added",
    "cli support added",
    "godot renderer implemented",
    "release action authorized",
    "product exposure approved",
)

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")


class RenderBridgeContractError(ValueError):
    """Raised when the render bridge contract violates its boundary."""


def read_text(path: Path) -> str:
    if not path.is_file():
        raise RenderBridgeContractError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8-sig")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RenderBridgeContractError(message)


def normalize_repo_path(path: Path) -> str:
    return path.relative_to(ROOT.resolve()).as_posix()


@lru_cache(maxsize=1)
def tracked_markdown_paths() -> frozenset[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.md"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RenderBridgeContractError("failed to enumerate public Markdown files with git ls-files") from exc
    paths = frozenset(path for path in result.stdout.decode("utf-8", errors="replace").split("\0") if path)
    require(paths, "git ls-files returned no public Markdown files")
    return paths


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_token(text: str, token: str) -> bool:
    return token in text or token in compact(text)


def check_public_safety(text: str, label: str) -> None:
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{label} leaks forbidden public category: {category}")
    lower = text.lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{label} contains forbidden overclaim phrase: {phrase}")


def local_markdown_links(text: str) -> list[str]:
    links: list[str] = []
    for match in LINK_PATTERN.finditer(text):
        target = unquote(match.group(1).strip())
        if target.startswith("#"):
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
            continue
        links.append(target)
    return links


def resolve_link(source_path: Path, raw_target: str, label: str) -> Path:
    clean_target = raw_target.split("#", 1)[0]
    require(clean_target != "", f"{label} has empty local link target")
    require("\\" not in clean_target, f"{label} uses backslash link target: {raw_target}")
    if clean_target.startswith("/"):
        resolved = (ROOT / clean_target.lstrip("/")).resolve()
    else:
        target_path = Path(clean_target)
        require(not target_path.is_absolute(), f"{label} uses absolute local link target: {raw_target}")
        resolved = (source_path.parent / target_path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RenderBridgeContractError(f"{label} resolves outside repo: {raw_target}") from exc
    return resolved


def check_links_resolve(text: str, source_path: Path) -> None:
    label = str(source_path.relative_to(ROOT))
    links = local_markdown_links(text)
    require(links, f"{label} has no local Markdown links to validate")
    tracked_markdown = tracked_markdown_paths()
    resolved_relatives: list[str] = []
    for raw_target in links:
        resolved = resolve_link(source_path, raw_target, label)
        relative = normalize_repo_path(resolved)
        resolved_relatives.append(relative)
        require(relative.endswith(".md"), f"{label} local link target is not Markdown: {raw_target}")
        require(relative in tracked_markdown, f"{label} local link target is not public Markdown: {raw_target}")
        require(resolved.is_file(), f"{label} Markdown link does not resolve: {raw_target}")
    for required_path in REQUIRED_PLAN_LINK_PATHS:
        require(required_path in resolved_relatives, f"{label} missing required resolved link target: {required_path}")


def check_plan_text(text: str, label: str) -> None:
    check_public_safety(text, label)
    for token in REQUIRED_PLAN_TOKENS:
        require(contains_token(text, token), f"{label} missing required token: {token}")
    for item in BRIDGE_ITEMS:
        require(f"| {item} |" in text, f"{label} missing bridge row: {item}")
    require(text.count("| Tier C source engine architecture |") == 1, f"{label} missing Tier C table row")
    require(text.count("| Tier B retail/static render and decode docs |") == 1, f"{label} missing Tier B table row")
    require(text.count("| Tier A runtime/GPU/visual proof | Not used in this slice. |") == 1, f"{label} missing Tier A non-use row")
    require(text.count("| Bridge item | Static route allowed | Higher authority still required |") == 1, f"{label} bridge table header count mismatch")


def check_anchor_tokens() -> None:
    for path, tokens in ANCHOR_TOKENS.items():
        text = read_text(path)
        label = str(path.relative_to(ROOT))
        for token in tokens:
            require(contains_token(text, token), f"{label} missing anchor token: {token}")


def check_package_script() -> None:
    try:
        package = json.loads(read_text(PACKAGE_JSON))
    except json.JSONDecodeError as exc:
        raise RenderBridgeContractError(f"invalid JSON: {PACKAGE_JSON.relative_to(ROOT)}: {exc}") from exc
    scripts = package.get("scripts")
    require(isinstance(scripts, dict), "package.json scripts must be an object")
    require(scripts.get(PACKAGE_SCRIPT) == PACKAGE_COMMAND, f"package.json missing {PACKAGE_SCRIPT}")


def run_check() -> None:
    require(PLAN.read_bytes() == LORE_PLAN.read_bytes(), "render bridge contract copies differ byte-for-byte")
    for path in (PLAN, LORE_PLAN):
        text = read_text(path)
        check_plan_text(text, str(path.relative_to(ROOT)))
        check_links_resolve(text, path)
    check_anchor_tokens()
    check_package_script()


def run_self_test() -> None:
    check_public_safety(
        "Source/static render bridge only; no runtime proof and no visual output.",
        "self-test clean boundary",
    )
    for bad_text, label in (
        ("runtime texture decode behavior proven", "positive runtime texture proof"),
        ("GPU upload proven", "positive GPU proof"),
        ("visual output proven", "positive visual proof"),
        ("importer execution complete", "positive importer execution"),
        ("generated asset output complete", "positive generated output"),
        ("rebuild parity proven", "positive rebuild parity"),
        (r"C:\\Users\\example\\private\\file.txt", "raw Windows path"),
        ("/home/example/private/file.txt", "raw Unix path"),
        ("a" * 64, "raw digest-like value"),
    ):
        try:
            check_public_safety(bad_text, label)
        except RenderBridgeContractError:
            pass
        else:
            raise RenderBridgeContractError(f"self-test failed to catch {label}")

    try:
        check_plan_text("not enough context", "self-test incomplete plan")
    except RenderBridgeContractError:
        pass
    else:
        raise RenderBridgeContractError("self-test failed to catch incomplete plan")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate tracked render-resource bridge static contract")
    parser.add_argument("--self-test", action="store_true", help="run internal negative guard tests")
    args = parser.parse_args()

    if not args.check and not args.self_test:
        parser.error("choose --check and/or --self-test")

    try:
        if args.self_test:
            run_self_test()
        if args.check:
            run_check()
    except RenderBridgeContractError as exc:
        print("Render resource bridge static contract probe: FAIL")
        print(f"- {exc}")
        return 1

    print("Render resource bridge static contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
