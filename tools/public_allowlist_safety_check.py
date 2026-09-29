#!/usr/bin/env python3
"""Hard-payload safety check for the public-primary repo.

The public repository is now the working repository. This check rejects exact
local retail-materialization owners, copied game/runtime payload roots, build
outputs, and obvious secret files. File extensions alone do not establish
provenance, so ordinary project-authored or separately provided asset formats
remain reviewable. This is intentionally not a portable-app ZIP manifest; the
WinUI package has its own stricter payload boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
SELF_REL = "tools/public_allowlist_safety_check.py"

DENY_ROOTS = (
    ".vs/",
    "GameProfiles/",
    "Ghidra/",
    "PatchBench/",
    "game/",
    "ghidra-local/",
    "local-game/",
    "local-ghidra/",
    "local-lab/",
    "local-media/",
    "local-rom-input/",
    "local-proofs/",
    "local-saves/",
    "mcps/",
    "media/",
    "save-attempts/",
)

DENY_CONTAINS = (
    "/bin/",
    "/obj/",
    "/TestResults/",
    "/__pycache__/",
    ".rep/",
    "/.rep/",
    "/secrets/",
    "/credentials/",
    "/.codex/auth/",
    "/.codex/cache/",
    "/.codex/logs/",
    "/.codex/sessions/",
    "/.codex/tmp/",
)

DENY_EXACT = {
}

ALLOW_EXACT_SHA256 = {
    "references/AYAResourceExtractor/BoxWithTextures.fbx": "37526ffde1d48016fa8a2a05c5dfeb3cd0a30a8ab402ccce60a7f44addf8eed2",
    "tests_shared/fixtures/gold_career_save.bin": "0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb",
}

ALLOW_EXACT = set(ALLOW_EXACT_SHA256)

REVIEWED_GHIDRA_ROOT = "reverse-engineering/ghidra/"
REVIEWED_GHIDRA_SUFFIXES = {".bak", ".dat", ".gbf", ".prp"}

RETAIL_MATERIALIZED_ROOTS = (
    "rebuild/OnslaughtRebuild.Core/Assets/Level100/",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/",
)
RETAIL_MATERIALIZED_METADATA = {
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/README.md",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/README.md",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/README.md",
}

ALLOW_CDB_SCRIPT_PREFIXES: tuple[str, ...] = ()

DENY_OPERATIONAL_SUFFIXES = (
    ".7z",
    ".appx",
    ".appxbundle",
    ".bak",
    ".bea",
    ".bes",
    ".bik",
    ".cab",
    ".cue",
    ".crt",
    ".db",
    ".dll",
    ".dmp",
    ".etl",
    ".exe",
    ".gbf",
    ".gdt",
    ".gpr",
    ".gz",
    ".gzf",
    ".img",
    ".iso",
    ".key",
    ".log",
    ".mso",
    ".msi",
    ".msix",
    ".msixbundle",
    ".pem",
    ".pfx",
    ".pdb",
    ".pyo",
    ".pyc",
    ".raw",
    ".rar",
    ".sav",
    ".sqlite",
    ".tar",
    ".trx",
    ".vid",
    ".zip",
)

MAX_UNREVIEWED_FILE_BYTES = 5 * 1024 * 1024
MAGIC_SCAN_BYTES = 4096

TEXT_SUFFIXES = {
    ".cmd",
    ".cs",
    ".css",
    ".html",
    ".java",
    ".json",
    ".jsonl",
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

TEXT_DENY_PATTERNS = (
    ("deny-private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("deny-openai-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("deny-github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("deny-github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("deny-aws-access-key", re.compile(r"\bA(?:KIA|SIA)[A-Z0-9]{16}\b")),
    ("deny-stripe-key", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{20,}\b")),
    ("deny-cloudflare-token", re.compile(r"\b(?:CF_API_TOKEN|CLOUDFLARE_API_TOKEN)\s*[:=]\s*[A-Za-z0-9_-]{20,}\b")),
    ("deny-huggingface-token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
    ("deny-sentry-dsn", re.compile(r"https://[A-Fa-f0-9]{16,}@[A-Za-z0-9.-]+/\d+")),
    ("deny-npm-token", re.compile(r"\bnpm_[A-Za-z0-9]{20,}\b")),
    ("deny-supabase-jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b")),
    ("deny-discord-token", re.compile(r"\b(?:mfa\.)?[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,}\b")),
)

TEXT_ALLOW_EXACT = {
    "tools/public_allowlist_safety_check.py",
}

PAYLOAD_TEXT_ALLOW_EXACT: set[str] = set()

# Exact reviewed text, not an extension/root exemption. The first manifest
# contains ten canonical UTF-8 comments (7,696 decoded bytes); the BBOX manifest
# contains two (1,575 bytes); bounds comments contain four (2,114 bytes).
# Segment-controller ownership contains eight analytic comments (4,705 bytes).
# Weapon-provider semantics contains ten analytic comments (8,032 bytes).
# UnitAI initializer/event arguments contain two/four analytic comments
# (2,226/3,536 decoded bytes).
# UnitAI exit contract contains two analytic comments (3,509 decoded bytes).
# Aim-provider semantics contains eight analytic comments (7,662 decoded bytes).
# Asin-helper semantics contains four analytic comments (4,607 decoded bytes).
# Renderer arguments/shared return-4 contain four/two analytic comments
# (3,846/1,101 decoded bytes).
# All were decoded/reviewed without control, secret or payload findings.
# Encoding preserves exact PRE/POST text;
# changing any byte removes the long-Base64 allowance. All other checks remain.
# Debug-log metadata: ten analytic comments (7,419 decoded bytes), with the
# same exact-content requirement and all other payload/secret checks retained.
# Sample loading/parameters: four comments each (3,673/4,227 decoded bytes),
# reviewed as authored analysis; the same exact-content boundary applies.
# RE-audit labels: ten current and ten proposed comments (4,708/6,733 decoded
# bytes), reviewed as authored analysis; the same exact-content boundary applies.
# Second RE-audit label cohort: seventeen current and eighteen proposed comments
# (9,370/12,711 decoded bytes), reviewed the same way.
# RE-audit D3DX library names: 987 current comments (the working project's prior
# analytic comments, 577,447 decoded bytes) and 1,139 generated evidence comments
# (library symbol, member, byte ranges and relocation counts; 1,086,765 bytes).
# No library or program bytes are encoded; reviewed the same way.
# RE-audit C runtime library names: 343 current comments (prior analytic comments,
# 150,337 decoded bytes) and 370 generated evidence comments (304,438 bytes; WinMain's
# keeps its earlier note as a marked lead). Reviewed the same way.
# Third RE-audit label cohort: eight current/eight proposed analytic comments
# (4,178/7,871 decoded bytes), reviewed with the same exact-content boundary.
# NvTriStrip identity cohort: 71 current/72 proposed analytic comments
# (38,389/80,580 decoded bytes), reviewed with the same exact-content boundary.
# Verified library comments: 191 current/191 proposed authored comments
# (133,185/175,548 decoded bytes); identifiers/provenance, no program/library bytes.
# Keyboard-query ABI: four current/four proposed analytic comments
# (1,754/8,036 decoded bytes); authored findings and marked historical leads only.
# Startup identities: four current/four proposed analytic comments
# (2,296/8,381 decoded bytes); authored findings and marked historical leads only.
# Damage/shake comments: two current/two proposed analytic comments
# (1,530/7,102 decoded bytes); authored findings and superseded historical leads.
# Cockpit float ABI: one current/one proposed analytic comment
# (848/3,262 decoded bytes); authored argument/arithmetic evidence and limits.
# Thing virtual identities: 172 current/205 proposed analytic comments
# (109,294/332,698 decoded bytes); source/RTTI proofs and marked historical leads.
# Verified Thing virtual identities: 65 current/65 proposed analytic comments
# (36,186/109,949 decoded bytes); static identity evidence and qualified older leads.
# Header interface identities: 14 current/16 proposed analytic comments
# (11,474/36,028 decoded bytes); bounded source/RTTI/body evidence and old leads.
# Controller/Engine verified identities: 14 current/14 proposed authored comments
# (6,132/30,168 decoded bytes); source/RTTI/body evidence and marked older leads.
# Compiler deleting-entry identities: 33 old/33 proposed authored comments
# (12,430/94,572 decoded bytes); bounded identity/normal-flow proofs and historical leads.
# Verified compiler deleting entries: 80 old/80 proposed authored comments
# (29,285/234,452 decoded bytes); static identity proofs and marked historical leads.
# Frontend page identities: 19 old/23 proposed authored comments
# (11,493/71,741 decoded bytes); common-interface evidence and marked historical leads.
# Verified frontend pages: 74 old/74 proposed authored comments
# (34,497/228,505 decoded bytes); bounded interface identities and marked older leads.
# Frontend callback ABI:3 old/3 proposed authored comments (8,037/12,358 decoded bytes);
# bounded receiver/stack transport and source divergences, preserving old notes as leads.
# Class-name getters:35 old/62 proposed authored comments (25,637/128,998 decoded bytes);
# bounded source-call/RTTI/literal identity, with prior notes and ABI tags historical.
# Memory-buffer identities:5 old/5 authored comments (3,387/10,512 decoded bytes);
# source/retail differences, bounded native runs and preserved fallible older notes.
# Event listeners:9 old/16 authored comments (4,457/32,127 decoded bytes);
# guarded dispatch and RTTI identity only; old notes/types remain fallible leads.
# Memory-buffer ABI:8 old/8 authored comments (9,110/15,708 decoded bytes);
# source/transport witnesses and explicitly retained fallible earlier notes.
# Resource-reader identities:5 old/5 authored comments (2,574/7,497 decoded bytes);
# bounded source/caller identities, divergences and preserved fallible older notes.
# Chunk-reader ABI:6 old/6 authored comments (2,109/9,691 decoded bytes);
# source/body/member transport and bounded original-code evidence, with old leads.
# Bounded-switch identities:5 old/6 authored comments (5,294/14,848 bytes);
# inherited interface proof, preserved uncertainty tags and older fallible leads.
# Verified switch methods:17 old/17 authored comments (8,345/37,760 bytes);
# static interface identities only; every older note remains a fallible lead.
# Camera position identities:5 old/9 authored comments (4,900/18,515 bytes);
# result-pointer/local-interface proof; old notes and nonexclusive contexts preserved.
# Camera copy returns:5 old/6 authored comments (7,752/16,421 bytes);
# physical EAX result corrections only; original notes/types retained with limits.
# Device lifecycle:25 old/31 authored comments (14,378/74,759 bytes);
# exact typed-list interface roles; old notes retained as fallible leads.
# Startup shell: five old/eight authored comments (4,373/13,298 bytes);
# partial virtual-slot witnesses and exact registration body; earlier notes retained.
# GetBPP: one old/authored comment (433/2,253 bytes); caller/source identity
# and bounded physical interface; old note retained as a fallible lead.
# Frontend argument interfaces: 22 old/22 authored comments (69,297/101,160 bytes);
# ordered local transport with return uncertainty and fallible old notes retained.
# WndProc: one new authored 2,084-byte comment; no prior plate note; opaque SDK types.
# Cleanup bodies:43 old/new authored comments (16,761/102,111 bytes); retained notes are leads.
# CPostEventData: 1,955 old / 3,950 authored comment bytes; short inherited opcode witness retained as a lead.
# Console menu: seven old notes/12 authored comments (6,842/31,807 bytes); old notes remain leads.
# Console kept names: nine old/new notes (5,027/24,150 bytes); only bounded role evidence is verified.
# Vertex menu: one old/new note (3,310/5,060 bytes); parameter-only ABI evidence.
# Music: eight old notes/ten authored comments (5,848/21,782 bytes); old notes remain leads.
# Thing gameplay: 47 old notes/60 authored comments (34,328/154,819 bytes); old notes remain leads.
# Thing gameplay ABI: 32 old/authored notes (83,744/128,922 bytes); old notes remain leads.
# Music verified: eight old/authored notes (3,624/17,063 bytes); old notes remain leads.
# GenericSPtrSet forwarder: one old/authored note (616/1,964 bytes); old note retained as a lead.
# GenericSPtrSet identities: fourteen old/authored notes (4,707/26,635 bytes); old notes retained as leads.
# GenericSPtrSet ABI: eight old/authored notes (14,732/24,562 bytes); old notes remain leads.
# Sound verified: 41 old/authored notes (23,740/86,153 bytes); old notes remain leads.
# Sound ABI: ten old/authored notes (21,154/35,742 bytes); old notes remain leads.
# Sound source identities: two old/authored notes (1,155/5,191 bytes); old notes remain leads.
# Walker verified: 25 old/authored notes (7,504/50,256 bytes); old notes remain leads.
# Walker helpers: eleven old/authored notes (5,388/24,918 bytes); old notes remain leads.
# Weapon icons: two old/authored notes (1,078/4,249 bytes); old notes remain leads.
# Jet verified: 14 old/authored notes (5,775/28,878 bytes); old notes remain leads.
# Jet/main helpers: nine old/authored notes (3,476/17,801 bytes); old notes remain leads.
# Jet ChargeWeapon: one old/authored note (3,229/4,680 bytes); old notes remain leads.
# Allocator verified: 27 old/authored notes (13,760/62,108 bytes); old notes remain leads.
# Allocator interfaces: three verified/authored notes (7,745/12,012 bytes); the verified notes are kept.
# Decomp names: 75 old/authored notes (40,476/109,654 bytes); old notes remain leads.
# Decomp names, batch 2: 44 old/authored notes (23,292/63,912 bytes); old notes remain leads.
REVIEWED_ENCODED_COMMENTS_SHA256 = {
    "tools/cohort-specs/decomp-names-2-20260929.manifest.tsv":
        "f415dd868a2948f9df8c352d894be674eed47ce016c9893529f55a34e1fb41bf",
    "tools/cohort-specs/decomp-names-20260929.manifest.tsv":
        "73f50978847462c0050ad1b0921fc3d15ff4858975b80f59e6f1df27395617e2",
    "tools/cohort-specs/memory-abi-20260928.manifest.tsv":
        "89ef1d3f2b1b2db6654a6c2d247a8d460a9e0a2d4f48aa29ca375bfbd5097fd2",
    "tools/cohort-specs/memory-verified-20260927.manifest.tsv":
        "fd355d74bbb544b136d19485cdc1a14d0ca3deed4c895283e898a22863ef6cef",
    "tools/cohort-specs/jet-charge-abi-20260927.manifest.tsv":
        "4be7541e2f5ef278c2bf8f260020cc19f1ac488b7bc6a6398ea32aceb1b549ac",
    "tools/cohort-specs/jet-helper-identities-20260927.manifest.tsv":
        "5ca9339b2cedd9214ba31397d4b44b9a3fc34b93323a4ca0e7f1025f54381b7a",
    "tools/cohort-specs/jet-verified-20260927.manifest.tsv":
        "2cbf3ba4fe7ea7023977311a8f5c179b845f85e76e898645799b3b5f053e2d25",
    "tools/cohort-specs/weapon-icon-identities-20260927.manifest.tsv":
        "437dd948f5dba051b30a61ca50db25a4063f5e94f41beaad3471dae2154a7d35",
    "tools/cohort-specs/walker-helper-identities-20260927.manifest.tsv":
        "b97d29f562aee82b5663ad6cc3199e6a80739bab256974b96cd44cc852e0d6d5",
    "tools/cohort-specs/walker-verified-20260927.manifest.tsv":
        "bfb0f0ce0f3d92453faafcd86993f626b539ef6bc04090529ba5ca23eb07b805",
    "tools/cohort-specs/sound-source-identities-20260927.manifest.tsv":
        "d8ea10c9e14801f33c0d56261b124154dee2f15096b97010895c92a709f76543",
    "tools/cohort-specs/sound-abi-20260927.manifest.tsv":
        "ecac955001c06643e3392b2e7fe94627c31326f3e9c6930894bb6e56dcbf8b2e",
    "tools/cohort-specs/sound-verified-20260927.manifest.tsv":
        "f614617973c1c4153486fbe5b787327732ffd69ddfba8880edd3dafcd111bcac",
    "tools/cohort-specs/sptrset-abi-20260927.manifest.tsv":
        "fe76eb6dd2320aca12ae8567c97ad6f177cfa872d568e77c3e22564ffe300b17",
    "tools/cohort-specs/sptrset-identities-20260927.manifest.tsv":
        "9ce5e7d3871208383f3d85397bbf7ca40bb3f315e756dc33484d4ac7908f22ed",
    "tools/cohort-specs/sptrset-forwarder-20260927.manifest.tsv":
        "c908006dda77b5af235ee112124212708f9d91813b7d5465cabcb05c6e843e55",
    "tools/cohort-specs/music-verified-20260927.manifest.tsv":
        "33cc495d11569cabeb256bfa24ac436ab1f963ece1cc86e6401b8abc4c31e608",
    "tools/cohort-specs/thing-gameplay-abi-20260927.manifest.tsv":
        "bc7232579531bb63bfd424661bf26d5fb44cde1277b08c2dffa6b092d3c81c72",
    "tools/cohort-specs/thing-gameplay-identities-20260927.manifest.tsv":
        "43ea56ebd707ad49e5da1383de8bcf6ce65c82f3b24742973db7a8c6d31ee058",
    "tools/cohort-specs/music-identities-20260927.manifest.tsv":
        "cca35b9b460735c991414dc4f1725a77bf6c8be2335455c2f0bda8a6ad8df559",
    "tools/cohort-specs/vertex-menu-abi-20260927.manifest.tsv":
        "a2f578d0ee7418cf0698d3640fcc43949e4bb10b982610fc93e72fe49a827511",
    "tools/cohort-specs/console-menu-verified-20260927.manifest.tsv":
        "08720aacef957006395d1217896e2eec5a162b62d5d162d4964fbf4cbeb32062",
    "tools/cohort-specs/console-menu-identities-20260927.manifest.tsv":
        "ab9cf380e888890a2c8e10deb447c6f19fe380126e89903458d06c89866ea64e",
    "tools/cohort-specs/postevent-cleanup-20260927.manifest.tsv":
        "999d6e415a432c3e7f5a0858f5e297f5472e57d43936041b0712eaf01141383a",
    "tools/cohort-specs/cleanup-body-verified-20260927.manifest.tsv":
        "e28925f18b6a2c2c85e8f7c7ab7726127fca13d3a1180938923096fdc2204a6d",
    "tools/cohort-specs/window-callback-abi-20260927.manifest.tsv":
        "55a506c425543cbbfc41ef95f7e948f25bbede5400cdb1b45fd2ed36d33b501c",
    "tools/cohort-specs/frontend-argument-abi-20260927.manifest.tsv":
        "7956c0b2795768913f74dd6848b64415bdb4685bd7a0d3ff412083c2e25d3ddd",
    "tools/cohort-specs/getbpp-abi-20260927.manifest.tsv":
        "168042f8d46217c420461ac7322d4142bc503781d3ed9a86f3e93441117af315",
    "tools/cohort-specs/startup-shell-20260927.manifest.tsv":
        "0b866f3285c25906cb39855caaa8e22dff7b1c543050bad29202e3b017c3f9c8",
    "tools/cohort-specs/device-lifecycle-20260927.manifest.tsv":
        "29f00b2042d7a788e7885a508c989c1152c02c399fd459c1349b42feda5eed65",
    "tools/cohort-specs/camera-copy-abi-20260927.manifest.tsv":
        "5010dcb91729ed39dcb7f9c02f6b61a0ddd86e7b9c41af4e8ca365c1d7a5e597",
    "tools/cohort-specs/camera-position-20260927.manifest.tsv":
        "0736cd5bb2eaa88a3e8e41e1a70286cb0ef59c90cbcd108902e31806d00be9d4",
    "tools/cohort-specs/switch-verified-20260927.manifest.tsv":
        "529ac81fb09106db0b9a69c099f7d87b9cd425b161fd058b7bbf9428625453e7",
    "tools/cohort-specs/switch-identities-20260927.manifest.tsv":
        "c4eb0001c3d166da84ea6cf0c74fe710d3e3dce8e309bc7fa6d9794afda2cac5",
    "tools/cohort-specs/reader-abi-20260927.manifest.tsv":
        "d6f4df28fd21be4faa9a0c47912b05669e8898037ba924cd90060104f52e9d4f",
    "tools/cohort-specs/resource-reader-identities-20260927.manifest.tsv":
        "63760c8e48b9d0611ca942d4273c32fb69801ec31552a92568d6849e662c449a",
    "tools/cohort-specs/membuffer-abi-20260927.manifest.tsv":
        "1b0de953ff8b525d9d406f1c8547c2e3b6df9410ff3c924b7fc07311a110fbd5",
    "tools/cohort-specs/listener-identities-20260927.manifest.tsv":
        "b55491e7c0deb84bdf7eb9bf0b82b8f99e69744915be8679626443652b5a783d",
    "tools/cohort-specs/membuffer-identities-20260927.manifest.tsv":
        "9a8ae4e68f37841be77ba4c8bb770a8baae901e3df2a52087e5188dcfe915366",
    "tools/cohort-specs/class-name-identities-20260927.manifest.tsv":
        "3b4cb6df7686b0b1261a1dcfed796ae51cdba72ae469d4e3bbbe211d174533bb",
    "tools/cohort-specs/frontend-callback-abi-20260927.manifest.tsv":
        "5b46095bcba7ae7883cbfee2a010750a031b1e84bf43b3833e3d85bf3ed2bc1d",
    "tools/cohort-specs/frontend-page-verified-20260927.manifest.tsv":
        "7f632659a7037581523e8223b47628e15cede7bd29a8c9e8b9005a07916cbbfb",
    "tools/cohort-specs/frontend-page-identities-20260927.manifest.tsv":
        "3f2c77b5f7bd530395bee5fb46c48ea7877f569e23ee9331ec8311e329491310",
    "tools/cohort-specs/compiler-destructor-verified-20260927.manifest.tsv":
        "eba36e6b528be7fa11cfc6996c8f162263628d8591ec9634c0295c39080af12f",
    "tools/cohort-specs/compiler-destructor-identities-20260927.manifest.tsv":
        "5586a02c772122a4eb2003bc189b03566feb8d7c53eff8334033b6816fc294bf",
    "tools/cohort-specs/controller-engine-verified-20260927.manifest.tsv":
        "9d5a41056274491e780de80a73f775e9b9a55406ecf35c8651d3e5f51d307c86",
    "tools/cohort-specs/header-interface-identities-20260926.manifest.tsv":
        "1d69f0b76974d06ece27b6270e779bf991296ff3bd699af6a29da4c6ee42fc8a",
    "tools/cohort-specs/thing-virtual-verified-20260926.manifest.tsv":
        "0223080a54241030cd083172a94ebd77f09585a22e603b2ea3b788c4cdb6ce88",
    "tools/cohort-specs/thing-virtual-identities-20260926.manifest.tsv":
        "a493b499e16ed804cd5ca4209c5e31b9f7654c090598820a2bdc26972a29b3df",
    "tools/cohort-specs/cockpit-shake-abi-20260926.manifest.tsv":
        "fb211b8eb5f13776511572f4b2aa7e724b55a4f3e8c9d34427ca1aa38e5acf5e",
    "tools/cohort-specs/damage-shake-comments-20260926.manifest.tsv":
        "c04f79f0d66c800bfd8fdeb2dbea74eb849c5dd3e86969e14dfe71dee18fa9e3",
    "tools/cohort-specs/startup-identities-20260926.manifest.tsv":
        "12fc2b6c96e0dee69e8c10d3e3039abe30f797675e5ad458f727e5f5acd82936",
    "tools/cohort-specs/input-key-abi-20260926.manifest.tsv":
        "47dec4ac21fb1c416cb5520a34d21732f30018cd26c5417fd2193e024114a875",
    "tools/cohort-specs/library-verified-20260926.manifest.tsv":
        "b9b307b6fc50cf53a65676f82c41da1919a0f7e65e8504047c4e91b9fcda6495",
    "tools/cohort-specs/library-nvtristrip-20260926.manifest.tsv":
        "183c67901469967fe26220a1d3701925911e05d71aef55d23482de39bb96540d",
    "tools/cohort-specs/label-audit-3-20260926.manifest.tsv":
        "438b81bf3d28799f59b8190d0ff3f34d20bed7cddb729aea424590e4e4ce50bc",
    "tools/cohort-specs/library-crt-20260926.manifest.tsv":
        "b1292f792373f16b2e3cc8bd80e8abeed191cf90decbef6fb6d47cec7eb67b63",
    "tools/cohort-specs/library-d3dx-20260926.manifest.tsv":
        "382eb1d2406f0e83b0dd36f6342b67f65805a245de6b43e588882ade3234387e",
    "tools/cohort-specs/label-audit-2-20260926.manifest.tsv":
        "a08aedbd280a23db7596a4e43e1c49efebfa189e6199fef3f26b58c51486d4e1",
    "tools/cohort-specs/label-audit-20260926.manifest.tsv":
        "fcb3d147351b5fc3696c03e302529c7809d75f88e2bf3ddc1e80d018d616c40f",
    "tools/cohort-specs/audio-sample-loading.manifest.tsv":
        "18a636d7b1c654a7b680d4ea7505e737e3438b81955de5f9979e7d21ff545d0b",
    "tools/cohort-specs/audio-sample-parameters.manifest.tsv":
        "ebed1bf4c675eb4684aea0609e3f6ba05af2b373224e393c766254b2a4f38ed7",
    "tools/cohort-specs/cli-initializer-ownership.manifest.tsv":
        "7159872b1d29231f1c89d6fc74bf5944035e463348defec60cb26b9fb0fd893a",
    "tools/cohort-specs/debug-log-metadata.manifest.tsv":
        "6c9dd2b0a8d2b2ac44a093232f1f7770bcc16d6174100854ba6f6fed9fc93b17",
    "tools/cohort-specs/render-registry-arguments.manifest.tsv":
        "35aa28c32dec8183e92d441afb9287e5204c98420b2de12a6cb5c93d2af4e121",
    "tools/cohort-specs/shared-return4-leaf.manifest.tsv":
        "28d6914d29e3111fbc5acd967588ffb3a0440d4e8e55b0b746e1cc0480c296bd",
    "tools/cohort-specs/asin-helper-semantics.manifest.tsv":
        "e3a8567675054accd4045b91a623f0b291b23a7b56b40b220464d7160f99fe1e",
    "tools/cohort-specs/aim-provider-semantics.manifest.tsv":
        "9efc2b4a31c908219384576963d9cb79c89f2d3767e74a9fb2735214777284c6",
    "tools/cohort-specs/unit-ai-exit-contract.manifest.tsv":
        "3cf43cd18e2c7ad0ed62613e649642feaad0ad19e53a29d9b2c4df609fa9cf71",
    "tools/cohort-specs/unit-ai-initializer.manifest.tsv":
        "d68d041e02f0d0cfe0d6453723a5a29af08913387648650292590b8a3ed2b1d8",
    "tools/cohort-specs/unit-ai-event-arguments.manifest.tsv":
        "e2f73dd9b98e160c28700ec70ec6a2c1399a1cb4f011128aabf0d878503a4ec0",
    "tools/cohort-specs/weapon-provider-semantics.manifest.tsv":
        "a686f08b85288db2e43cca9f82ba5b9d91a048e7c2d50b6ca0f4b32fd7b0a804",
    "tools/cohort-specs/air-contact-shutdown.manifest.tsv":
        "d97fee5bddfd289cda7f9d2be43d6b388043f688205bc27303f961235ee73da4",
    "tools/cohort-specs/segment-controller-ownership.manifest.tsv":
        "467f5235b71bfd301407b4c806aaec66a31dbe120551ba9bb9a1061886ee3585",
    "tools/cohort-specs/bounds-contract-comments.manifest.tsv":
        "b74cdb6a1ed2dff28b2a4946bbfc4453bada7a0afa6c625982c8cd618bbb479c",
    "tools/cohort-specs/first-training-semantic-corrections.manifest.tsv":
        "b8b1999ee60f6ff9ece0466eba783d93891f47b7272c72ec27b71718adf6feaf",
    "tools/cohort-specs/mesh-bounding-box-metadata.manifest.tsv":
        "3ab12852fe992be1789eb1f24f57cf0052d6b3706286f22bdf057a1aef485749",
}

CDB_PROMPT_RE = re.compile(r"(?m)^\s*\d+:\d+>\s+")
REGISTER_DUMP_RE = re.compile(
    r"(?im)\b(?:eax|ebx|ecx|edx|esi|edi|eip|esp|rax|rbx|rcx|rdx|rsi|rdi|rip|rsp)=[0-9a-f`]{4,}\b"
)
STACK_TRACE_RE = re.compile(r"(?im)^\s*(?:ChildEBP|Child-SP|RetAddr)\s+")
DATA_IMAGE_RE = re.compile(r"data:image/(?:png|jpeg|jpg|gif|webp|bmp);base64,", re.IGNORECASE)
EMBEDDED_PNG_RE = re.compile(r"(?:\\x89PNG|iVBORw0KGgo)", re.IGNORECASE)
EMBEDDED_JPEG_RE = re.compile(r"(?:\\xff\\xd8\\xff|/9j/4AAQSkZJRgABAQ)", re.IGNORECASE)
BASE64_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/=]{512,}(?![A-Za-z0-9+/=])")

MAGIC_DENY_SIGNATURES = (
    ("deny-magic-executable", b"MZ"),
    ("deny-magic-zip-archive", b"PK\x03\x04"),
    ("deny-magic-7z-archive", b"7z\xbc\xaf\x27\x1c"),
    ("deny-magic-rar-archive", b"Rar!\x1a\x07"),
    ("deny-magic-msi-ole-package", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"),
    ("deny-magic-cab-archive", b"MSCF"),
    ("deny-magic-pdb-symbols", b"Microsoft C/C++"),
    ("deny-magic-bink-video", b"BIK"),
    ("deny-magic-sqlite-db", b"SQLite format 3\x00"),
)

@dataclass(frozen=True)
class Finding:
    path: str
    label: str
    detail: str


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def public_candidate_files(root: Path, *, include_submodules: bool = False) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git executable was not found for public candidate enumeration") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr)
        raise RuntimeError(f"git ls-files failed for public candidate enumeration: {stderr.strip()}") from exc
    paths = [
        path
        for item in result.stdout.decode("utf-8", errors="replace").split("\0")
        if (path := normalize(item)) and (root / path).exists()
    ]
    if include_submodules:
        paths.extend(submodule_candidate_files(root))
    return sorted(set(paths))


def payload_root_files(root: Path) -> list[str]:
    if not root.is_dir():
        raise RuntimeError(f"payload root is not a directory: {root}")

    paths: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise RuntimeError(f"payload root enumeration escaped root: {path}") from exc
        if relative.startswith(".git/"):
            continue
        paths.append(normalize(relative))
    return sorted(set(paths))


def submodule_paths(root: Path) -> list[str]:
    gitmodules = root / ".gitmodules"
    if not gitmodules.is_file():
        return []
    try:
        result = subprocess.run(
            ["git", "config", "--file", str(gitmodules), "--get-regexp", r"^submodule\..*\.path$"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git executable was not found for .gitmodules parsing") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f".gitmodules could not be parsed: {exc.stderr.strip()}") from exc
    paths: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            paths.append(normalize(parts[1].strip()))
    return sorted(paths)


def submodule_candidate_files(root: Path) -> list[str]:
    paths: list[str] = []
    for submodule_path in submodule_paths(root):
        full_path = root / submodule_path
        if not full_path.is_dir():
            continue
        try:
            result = subprocess.run(
                ["git", "ls-files", "-z"],
                cwd=full_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(f"git executable was not found while scanning submodule {submodule_path}") from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr)
            raise RuntimeError(f"submodule {submodule_path} could not be scanned: {stderr.strip()}") from exc
        for item in result.stdout.decode("utf-8", errors="replace").split("\0"):
            if not item:
                continue
            paths.append(f"{submodule_path}/{normalize(item)}")
    return sorted(paths)


def submodule_scan_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        paths = submodule_paths(root)
    except RuntimeError as exc:
        return [Finding(".gitmodules", "deny-unreadable-submodule-map", str(exc))]
    for submodule_path in paths:
        full_path = root / submodule_path
        if not full_path.is_dir():
            findings.append(Finding(submodule_path, "deny-missing-submodule-scan", "declared submodule directory is absent"))
            continue
        try:
            subprocess.run(
                ["git", "ls-files", "-z"],
                cwd=full_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            findings.append(Finding(submodule_path, "deny-unreadable-submodule-scan", str(exc)))
    return findings


def is_text_file(path: str) -> bool:
    return Path(path).suffix.lower() in TEXT_SUFFIXES


def is_text_candidate(path: str) -> bool:
    """Compatibility helper used by release accounting scripts."""
    return is_text_file(path)


def is_reviewed_payload(path: str) -> bool:
    if path == f"{REVIEWED_GHIDRA_ROOT}BEA.gpr":
        return True
    if not path.startswith(f"{REVIEWED_GHIDRA_ROOT}BEA.rep/"):
        return False
    return Path(path).suffix.lower() in REVIEWED_GHIDRA_SUFFIXES or Path(path).name == "projectState"


def path_findings(path: str) -> list[Finding]:
    if path in ALLOW_EXACT or is_reviewed_payload(path):
        return []
    findings: list[Finding] = []
    lower = path.lower()
    name = Path(path).name.lower()
    if lower.startswith(".codex/"):
        findings.append(Finding(path, "deny-codex-runtime-subtree", path))
    if path in DENY_EXACT:
        findings.append(Finding(path, "deny-exact", path))
    if name == ".env" or name.startswith(".env."):
        findings.append(Finding(path, "deny-env-file", name))
    if lower.startswith(tuple(prefix.lower() for prefix in DENY_ROOTS)):
        findings.append(Finding(path, "deny-root", path.split("/", 1)[0]))
    if (
        lower.startswith(tuple(prefix.lower() for prefix in RETAIL_MATERIALIZED_ROOTS))
        and lower not in {item.lower() for item in RETAIL_MATERIALIZED_METADATA}
    ):
        findings.append(Finding(path, "deny-materialized-retail-output", path))
    if any(token.lower() in lower for token in DENY_CONTAINS):
        findings.append(Finding(path, "deny-generated-or-private-path", path))
    if lower.endswith(".cdb.txt") and not any(lower.startswith(prefix.lower()) for prefix in ALLOW_CDB_SCRIPT_PREFIXES):
        findings.append(Finding(path, "deny-raw-cdb-text-transcript", ".cdb.txt"))
    if lower.endswith(".txt") and "cdb" in name and "log" in name:
        findings.append(Finding(path, "deny-raw-cdb-text-transcript", name))
    if lower.endswith(DENY_OPERATIONAL_SUFFIXES):
        findings.append(Finding(path, "deny-operational-payload-suffix", Path(path).suffix.lower()))
    return findings


def size_findings(root: Path, path: str) -> list[Finding]:
    full_path = root / path
    if full_path.is_dir():
        return []
    try:
        size = full_path.stat().st_size
    except OSError as exc:
        return [Finding(path, "stat-error", str(exc))]
    if path in ALLOW_EXACT_SHA256 or is_reviewed_payload(path):
        return []
    if size > MAX_UNREVIEWED_FILE_BYTES:
        return [Finding(path, "deny-large-unreviewed-file", str(size))]
    return []


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def exact_allow_hash_findings(root: Path, path: str) -> list[Finding]:
    expected = ALLOW_EXACT_SHA256.get(path)
    if expected is None:
        return []
    full_path = root / path
    try:
        actual = sha256_file(full_path)
    except OSError as exc:
        return [Finding(path, "exact-allow-hash-read-error", str(exc))]
    if actual.lower() != expected.lower():
        return [Finding(path, "exact-allow-hash-mismatch", actual)]
    return []


def magic_findings(root: Path, path: str) -> list[Finding]:
    if path in ALLOW_EXACT_SHA256 or is_text_file(path) or is_reviewed_payload(path):
        return []
    full_path = root / path
    if full_path.is_dir():
        return []
    try:
        prefix = full_path.read_bytes()[:MAGIC_SCAN_BYTES]
    except OSError as exc:
        return [Finding(path, "read-error", str(exc))]
    findings: list[Finding] = []
    for label, signature in MAGIC_DENY_SIGNATURES:
        offset = prefix.find(signature)
        if offset >= 0:
            findings.append(Finding(path, label, f"offset={offset} signature={signature.hex()}"))
            break
    return findings


def text_binary_findings(root: Path, path: str) -> list[Finding]:
    if path == SELF_REL or path in TEXT_ALLOW_EXACT or not is_text_file(path):
        return []
    full_path = root / path
    try:
        prefix = full_path.read_bytes()[:MAGIC_SCAN_BYTES]
    except OSError as exc:
        return [Finding(path, "read-error", str(exc))]
    if b"\x00" in prefix:
        return [Finding(path, "deny-nul-byte-in-text-file", "NUL byte")]
    control_count = sum(1 for byte in prefix if byte < 32 and byte not in {9, 10, 13})
    if prefix and control_count / len(prefix) > 0.05:
        return [Finding(path, "deny-control-byte-heavy-text-file", f"{control_count}/{len(prefix)}")]
    return []


def content_signature_findings(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    if path in PAYLOAD_TEXT_ALLOW_EXACT:
        return findings
    cdb_prompt_count = len(CDB_PROMPT_RE.findall(text))
    register_count = len(REGISTER_DUMP_RE.findall(text))
    stack_trace_count = len(STACK_TRACE_RE.findall(text))
    if cdb_prompt_count >= 3 or (cdb_prompt_count >= 1 and (register_count >= 4 or stack_trace_count >= 1)):
        findings.append(
            Finding(
                path,
                "deny-raw-debugger-transcript-content",
                f"cdbPrompts={cdb_prompt_count} registerRows={register_count} stackRows={stack_trace_count}",
            )
        )
    if DATA_IMAGE_RE.search(text):
        findings.append(Finding(path, "deny-data-image-url", "data:image/*;base64"))
    if EMBEDDED_PNG_RE.search(text):
        findings.append(Finding(path, "deny-embedded-png-header", "png header/base64 marker"))
    if EMBEDDED_JPEG_RE.search(text):
        findings.append(Finding(path, "deny-embedded-jpeg-header", "jpeg header/base64 marker"))
    if (REVIEWED_ENCODED_COMMENTS_SHA256.get(path) ==
            hashlib.sha256(text.encode("utf-8")).hexdigest()):
        return findings
    for match in BASE64_TOKEN_RE.finditer(text):
        token = match.group(0)
        if "0x" in token.lower():
            continue
        if "+" not in token and "/" not in token and "=" not in token:
            continue
        snippet = token[:117] + "..." if len(token) > 120 else token
        findings.append(Finding(path, "deny-large-base64-blob", snippet))
        break
    return findings


def text_findings(root: Path, path: str) -> list[Finding]:
    if path == SELF_REL or path in TEXT_ALLOW_EXACT:
        return []
    if not is_text_file(path):
        return []
    full_path = root / path
    try:
        text = full_path.read_bytes().decode("utf-8", errors="replace")
    except OSError as exc:
        return [Finding(path, "read-error", str(exc))]

    findings: list[Finding] = []
    for label, pattern in TEXT_DENY_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group(0).replace("\n", "\\n")
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            findings.append(Finding(path, label, snippet))
    findings.extend(content_signature_findings(path, text))
    return findings


def find_text_payload_errors(path: str, text: str, require_private_text_guard: bool = False) -> list[str]:
    """Compatibility helper used by release accounting scripts."""
    if path == SELF_REL or path in TEXT_ALLOW_EXACT:
        return []
    if not is_text_candidate(path):
        return []

    errors: list[str] = []
    for label, pattern in TEXT_DENY_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group(0).replace("\n", "\\n")
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            errors.append(f"{label} in {path}: {snippet}")
    for finding in content_signature_findings(path, text):
        errors.append(f"{finding.label} in {path}: {finding.detail}")
    return errors


def check_repo(root: Path, *, include_submodules: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    try:
        paths = public_candidate_files(root, include_submodules=include_submodules)
    except RuntimeError as exc:
        return [Finding(".", "deny-public-candidate-enumeration-failed", str(exc))]
    if not paths:
        return [Finding(".", "deny-empty-public-candidate-set", "git candidate enumeration returned zero files")]
    if include_submodules:
        findings.extend(submodule_scan_findings(root))
    for path in paths:
        findings.extend(path_findings(path))
        findings.extend(exact_allow_hash_findings(root, path))
        findings.extend(size_findings(root, path))
        findings.extend(magic_findings(root, path))
        findings.extend(text_binary_findings(root, path))
        findings.extend(text_findings(root, path))
    return findings


def check_payload_root(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        paths = payload_root_files(root)
    except RuntimeError as exc:
        return [Finding(".", "deny-public-candidate-enumeration-failed", str(exc))]
    if not paths:
        return [Finding(".", "deny-empty-public-candidate-set", "payload-root enumeration returned zero files")]
    for path in paths:
        findings.extend(path_findings(path))
        findings.extend(exact_allow_hash_findings(root, path))
        findings.extend(size_findings(root, path))
        findings.extend(magic_findings(root, path))
        findings.extend(text_binary_findings(root, path))
        findings.extend(text_findings(root, path))
    return findings


def run_self_test() -> int:
    # A reviewed encoding allows only the exact path/content. Secret scanning
    # still runs on that same file; no general TSV or Base64 exemption exists.
    with tempfile.TemporaryDirectory() as tmp:
        import base64
        root = Path(tmp)
        path = "reviewed-comments.tsv"
        value = base64.b64encode(("Reviewed text only. " * 64).encode()).decode() + "\n"
        REVIEWED_ENCODED_COMMENTS_SHA256[path] = hashlib.sha256(value.encode()).hexdigest()
        try:
            (root / path).write_text(value, encoding="utf-8")
            if text_findings(root, path):
                print("Public payload safety self-test: FAIL - exact reviewed comments rejected")
                return 1
            for candidate_path, candidate_text in (
                (path, value + "changed\n"),
                (path, value.replace("\n", "\r\n")),
                ("unreviewed.tsv", value),
            ):
                (root / candidate_path).write_bytes(candidate_text.encode())
                if not any(f.label == "deny-large-base64-blob" for f in text_findings(root, candidate_path)):
                    print("Public payload safety self-test: FAIL - encoded comment guard widened")
                    return 1
            secret_text = value + "ghp" + "_" + "testfixturevalue000000000000\n"
            REVIEWED_ENCODED_COMMENTS_SHA256[path] = hashlib.sha256(secret_text.encode()).hexdigest()
            (root / path).write_text(secret_text, encoding="utf-8")
            if not any(f.label == "deny-github-token" for f in text_findings(root, path)):
                print("Public payload safety self-test: FAIL - reviewed comments bypassed secret check")
                return 1
        finally:
            del REVIEWED_ENCODED_COMMENTS_SHA256[path]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        openai_fixture = "sk" + "-" + "not-a-real-fixture-value"
        generic_secret_fixture = "sk" + "-" + "thisfixturehasenoughcharacters000000"
        github_fixture = "ghp" + "_" + "thisfixturehasenoughcharacters000000"
        stripe_fixture = "sk" + "_" + "live" + "_" + "thisfixturehasenoughcharacters000000"
        hf_fixture = "hf" + "_" + "thisfixturehasenoughcharacters000000"
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        (root / "game").mkdir()
        (root / "game" / "BEA.exe").write_bytes(b"not ok")
        (root / "media").mkdir()
        (root / "media" / "music.ogg").write_bytes(b"not ok")
        (root / "save-attempts").mkdir()
        (root / "save-attempts" / "slot.bes").write_bytes(b"not ok")
        (root / "local-rom-input").mkdir()
        (root / "local-rom-input" / "payload.txt").write_text("local-only payload root\n", encoding="utf-8")
        (root / "project-assets").mkdir()
        (root / "project-assets" / "frame.webp").write_bytes(b"RIFF\x00\x00\x00\x00WEBP")
        (root / "project-assets" / "theme.ogg").write_bytes(b"OggS\x00project audio")
        (root / "project-assets" / "effect.wav").write_bytes(b"RIFF\x00\x00\x00\x00WAVE")
        (root / "project-assets" / "model.obj").write_text("project-authored model\n", encoding="utf-8")
        (root / "project-assets" / "mesh.aya").write_bytes(b"project-authored mesh")
        (root / "project-assets" / "data.bin").write_bytes(b"project-authored data")
        (root / "installer.msix").write_bytes(b"not ok")
        (root / "symbols.pdb").write_bytes(b"Microsoft C/C++ MSF 7.00\r\n\x1aDS\0\0\0")
        (root / "package.msi").write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1not ok")
        (root / "cabinet.cab").write_bytes(b"MSCFnot ok")
        (root / "archive.7z").write_bytes(b"not ok")
        (root / "slot.sav").write_bytes(b"not ok")
        materialized_payloads = (
            "rebuild/OnslaughtRebuild.Core/Assets/Level100/retail-chunk.bin",
            "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/retail-model.obj",
            "rebuild/OnslaughtRebuild.Godot/Assets/Hud/retail-hud.aya",
            "rebuild/OnslaughtRebuild.Godot/Assets/Level100/retail-terrain.bin",
        )
        for materialized_payload in materialized_payloads:
            target = root / materialized_payload
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"local retail materialization")
        (root / "rebuild" / "OnslaughtRebuild.Godot" / "Assets" / "Level100" / "README.md").write_text(
            "# Materialization owner\n",
            encoding="utf-8",
        )
        (root / "manual.pdf").write_bytes(b"%PDF-project documentation")
        (root / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\nproject screenshot")
        (root / "disguised-note.md").write_bytes(b"\x89PNG\r\n\x1a\nnot ok")
        (root / "padded-disguised-note.md").write_bytes((b"x" * 40) + b"\x89PNG\r\n\x1a\nnot ok")
        (root / "nul-note.md").write_bytes(b"text before\x00payload")
        (root / "manual.html").write_text("<html>not ok</html>\n", encoding="utf-8")
        (root / "manual.xml").write_text("<xml>not ok</xml>\n", encoding="utf-8")
        (root / "local.rep").mkdir()
        (root / "local.rep" / "project.db").write_bytes(b"not ok")
        canonical_ghidra = root / "reverse-engineering" / "ghidra" / "BEA.rep" / "idata"
        canonical_ghidra.mkdir(parents=True)
        (canonical_ghidra / "database.gbf").write_bytes(b"reviewed canonical database fixture")
        (root / "reverse-engineering" / "ghidra" / "BEA.exe").write_bytes(b"not reviewed")
        (root / ".codex" / "custom").mkdir(parents=True)
        (root / ".codex" / "custom" / "instructions.md").write_text("not public\n", encoding="utf-8")
        (root / ".codex" / "sessions").mkdir(parents=True)
        (root / ".codex" / "sessions" / "session.jsonl").write_text("not ok\n", encoding="utf-8")
        (root / "archive" / "electron-workbench" / "packages" / "ui").mkdir(parents=True)
        (root / "archive" / "electron-workbench" / "packages" / "ui" / "index.html").write_text("<div>allowed app shell</div>\n", encoding="utf-8")
        (root / "references" / "AYAResourceExtractor").mkdir(parents=True)
        (root / "references" / "AYAResourceExtractor" / "BoxWithTextures.fbx").write_bytes(b"allowed non-BEA extractor fixture")
        (root / "big.md").write_bytes(b"x" * (MAX_UNREVIEWED_FILE_BYTES + 1))
        (root / "tests_shared" / "fixtures").mkdir(parents=True)
        (root / "tests_shared" / "fixtures" / "gold_career_save.bin").write_bytes(b"allowed regression fixture")
        (root / ".env").write_text(f"OPENAI_API_KEY={openai_fixture}\n", encoding="utf-8")
        (root / "docs.md").write_text("Raw RE notes may mention local paths and field names.\n", encoding="utf-8")
        (root / "token-note.md").write_text(
            f"Accidental token example {generic_secret_fixture}\n",
            encoding="utf-8",
        )
        (root / "inline-image.md").write_text(
            "Accidental inline image data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB\n",
            encoding="utf-8",
        )
        (root / "blob-note.md").write_text(
            "Accidental blob " + ("A" * 260) + "/" + ("B" * 260) + "\n",
            encoding="utf-8",
        )
        (root / "raw-debugger-summary.md").write_text(
            "0:000> r\n"
            "eax=00000001 ebx=00000002 ecx=00000003 edx=00000004 esi=00000005 edi=00000006 eip=00401000 esp=0019ff00\n",
            encoding="utf-8",
        )
        (root / "raw-debugger-events.jsonl").write_text(
            '{"line":"0:000> r eax=00000001 ebx=00000002 ecx=00000003 edx=00000004 eip=00401000"}\n',
            encoding="utf-8",
        )
        (root / "subagents" / "runtime").mkdir(parents=True)
        (root / "subagents" / "runtime" / "raw-session.cdb.txt").write_text(
            "0:000> g\nraw debugger transcript fixture\n",
            encoding="utf-8",
        )
        (root / "release" / "readiness").mkdir(parents=True)
        (root / "release" / "readiness" / "session-cdb-log.txt").write_text(
            "raw cdb log fixture\n",
            encoding="utf-8",
        )
        (root / "tools" / "runtime-probes").mkdir(parents=True)
        (root / "tools" / "runtime-probes" / "allowed-observer.cdb.txt").write_text(
            ".echo command script fixture\nvertarget\ng\n",
            encoding="utf-8",
        )
        (root / "github-token-note.md").write_text(
            f"Accidental token example {github_fixture}\n",
            encoding="utf-8",
        )
        (root / "stripe-token-note.md").write_text(
            f"Accidental token example {stripe_fixture}\n",
            encoding="utf-8",
        )
        (root / "hf-token-note.md").write_text(
            f"Accidental token example {hf_fixture}\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root)
        labels = {finding.label for finding in findings}
        required = {
            "deny-root",
            "deny-codex-runtime-subtree",
            "deny-generated-or-private-path",
            "deny-operational-payload-suffix",
            "deny-materialized-retail-output",
            "deny-env-file",
            "deny-large-unreviewed-file",
            "deny-magic-pdb-symbols",
            "deny-magic-msi-ole-package",
            "deny-magic-cab-archive",
            "deny-nul-byte-in-text-file",
            "deny-data-image-url",
            "deny-embedded-png-header",
            "deny-raw-debugger-transcript-content",
            "exact-allow-hash-mismatch",
            "deny-openai-key",
            "deny-github-token",
            "deny-stripe-key",
            "deny-huggingface-token",
            "deny-raw-cdb-text-transcript",
        }
        missing = sorted(required - labels)
        if missing:
            print("Public payload safety self-test: FAIL")
            print(f"- missing expected labels: {', '.join(missing)}")
            print(f"- findings: {findings!r}")
            return 1
        if any(finding.path == "tests_shared/fixtures/gold_career_save.bin" for finding in findings):
            if not any(
                finding.path == "tests_shared/fixtures/gold_career_save.bin" and finding.label == "exact-allow-hash-mismatch"
                for finding in findings
            ):
                print("Public payload safety self-test: FAIL")
                print("- gold fixture exception was rejected for a reason other than hash mismatch")
                print(f"- findings: {findings!r}")
                return 1
        if any(finding.path == "references/AYAResourceExtractor/BoxWithTextures.fbx" for finding in findings):
            if not any(
                finding.path == "references/AYAResourceExtractor/BoxWithTextures.fbx"
                and finding.label == "exact-allow-hash-mismatch"
                for finding in findings
            ):
                print("Public payload safety self-test: FAIL")
                print("- AYAResourceExtractor fixture fbx was rejected for a reason other than hash mismatch")
                print(f"- findings: {findings!r}")
                return 1
        for denied_payload in materialized_payloads:
            if not any(finding.path == denied_payload for finding in findings):
                print("Public payload safety self-test: FAIL")
                print(f"- local retail-materialization output was not rejected: {denied_payload}")
                print(f"- findings: {findings!r}")
                return 1
        allowed_project_files = (
            "project-assets/frame.webp",
            "project-assets/theme.ogg",
            "project-assets/effect.wav",
            "project-assets/model.obj",
            "project-assets/mesh.aya",
            "project-assets/data.bin",
            "manual.pdf",
            "screenshot.png",
            "manual.html",
            "manual.xml",
            "rebuild/OnslaughtRebuild.Godot/Assets/Level100/README.md",
        )
        unexpected_project_findings = [
            finding for finding in findings if finding.path in allowed_project_files
        ]
        if unexpected_project_findings:
            print("Public payload safety self-test: FAIL")
            print("- legitimate authored/document asset formats were rejected")
            print(f"- findings: {unexpected_project_findings!r}")
            return 1
        if not any(finding.path == "tools/runtime-probes/allowed-observer.cdb.txt" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- tracked CDB command scripts were not rejected")
            print(f"- findings: {findings!r}")
            return 1
        canonical_findings = [
            finding
            for finding in findings
            if finding.path.startswith("reverse-engineering/ghidra/")
            and finding.path != "reverse-engineering/ghidra/BEA.exe"
        ]
        if canonical_findings:
            print("Public payload safety self-test: FAIL")
            print("- canonical Ghidra project owner was rejected")
            print(f"- findings: {findings!r}")
            return 1
        if not any(finding.path == "reverse-engineering/ghidra/BEA.exe" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- standalone executable inside the Ghidra owner was not rejected")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        (root / "Game").mkdir()
        (root / "Game" / "payload.txt").write_text("case variant root\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root)
        if not any(finding.label == "deny-root" and finding.path == "Game/payload.txt" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- case-variant game root was not rejected")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        non_repo = Path(tmp)
        findings = check_repo(non_repo)
        if not any(finding.label == "deny-public-candidate-enumeration-failed" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- non-git root did not fail closed")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        payload_root = Path(tmp)
        (payload_root / "README.MD").write_text("# OK\n", encoding="utf-8")
        (payload_root / "game").mkdir()
        (payload_root / "game" / "BEA.exe").write_bytes(b"not ok")
        findings = check_payload_root(payload_root)
        if not any(finding.label == "deny-root" and finding.path == "game/BEA.exe" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- payload-root mode did not reject game root")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / ".gitmodules").write_text("[submodule \"broken\"\n\tpath = broken\n", encoding="utf-8")
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root, include_submodules=True)
        if not any(finding.label == "deny-public-candidate-enumeration-failed" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- malformed .gitmodules did not fail closed")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / ".gitmodules").write_text(
            '[submodule "missing"]\n\tpath = references/missing\n\turl = ../missing.git\n',
            encoding="utf-8",
        )
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root, include_submodules=True)
        if not any(
            finding.label == "deny-missing-submodule-scan"
            and finding.path == "references/missing"
            for finding in findings
        ):
            print("Public payload safety self-test: FAIL")
            print("- missing declared submodule did not fail closed")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        submodule = root / "references" / "payload-fixture"
        submodule.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=submodule, check=True)
        (submodule / "game").mkdir()
        (submodule / "game" / "BEA.exe").write_bytes(b"not ok")
        subprocess.run(["git", "add", "."], cwd=submodule, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Payload Fixture",
                "-c",
                "user.email=payload-fixture@example.invalid",
                "commit",
                "-q",
                "-m",
                "payload fixture",
            ],
            cwd=submodule,
            check=True,
        )
        (root / ".gitmodules").write_text(
            '[submodule "payload-fixture"]\n'
            "\tpath = references/payload-fixture\n"
            "\turl = ../payload-fixture.git\n",
            encoding="utf-8",
        )
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        subprocess.run(
            ["git", "-c", "advice.addEmbeddedRepo=false", "add", "."],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        findings = check_repo(root, include_submodules=True)
        if not any(
            finding.path == "references/payload-fixture/game/BEA.exe"
            for finding in findings
        ):
            print("Public payload safety self-test: FAIL")
            print("- initialized submodule hard payload was not rejected")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "game").mkdir()
        (root / "game" / "BEA.exe").write_bytes(b"root payload")
        submodule = root / "references" / "clean-fixture"
        submodule.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=submodule, check=True)
        (submodule / "README.MD").write_text("# Clean fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=submodule, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Clean Fixture",
                "-c",
                "user.email=clean-fixture@example.invalid",
                "commit",
                "-q",
                "-m",
                "clean fixture",
            ],
            cwd=submodule,
            check=True,
        )
        (root / ".gitmodules").write_text(
            '[submodule "clean-fixture"]\n'
            "\tpath = references/clean-fixture\n"
            "\turl = ../clean-fixture.git\n",
            encoding="utf-8",
        )
        (root / "README.MD").write_text("# Root fixture\n", encoding="utf-8")
        subprocess.run(
            ["git", "-c", "advice.addEmbeddedRepo=false", "add", "."],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        root_findings = set(check_repo(root))
        combined_findings = set(check_repo(root, include_submodules=True))
        if not root_findings or not root_findings.issubset(combined_findings):
            print("Public payload safety self-test: FAIL")
            print("- root findings changed when submodule scanning was enabled")
            print(f"- root findings: {sorted(root_findings, key=lambda item: item.path)!r}")
            print(f"- combined findings: {sorted(combined_findings, key=lambda item: item.path)!r}")
            return 1
    print("Public payload safety self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run built-in fixture tests.")
    parser.add_argument("--include-submodules", action="store_true", help="Also scan initialized submodule tracked files with parent hard-payload rules.")
    parser.add_argument("--require-private-text-guard", action="store_true", help="Accepted for compatibility; denylist text guards are built in.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--payload-root", type=Path, help="Scan an already materialized non-git payload/export tree by walking files under this root.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = (args.payload_root or args.repo_root).resolve()
    findings = check_payload_root(root) if args.payload_root else check_repo(root, include_submodules=args.include_submodules)
    if findings:
        print("Public payload safety check: FAIL")
        for finding in findings[:200]:
            print(f"- {finding.path}: {finding.label}: {finding.detail}")
        if len(findings) > 200:
            print(f"- ... ({len(findings) - 200} more)")
        return 1

    print("Public payload safety check: PASS")
    count = len(payload_root_files(root)) if args.payload_root else len(public_candidate_files(root, include_submodules=args.include_submodules))
    print(f"Public candidate files checked: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
