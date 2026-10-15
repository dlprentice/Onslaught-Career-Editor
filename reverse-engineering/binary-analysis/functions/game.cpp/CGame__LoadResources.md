# CGame__LoadResources

> Address: `0x0046cd30`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:624` (`CGame::LoadResources`)
| Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: One-off per-level resource load driven entirely through the
console loading screen (`ecx = 0x00663498` on every call). It sets the
loading range, optionally reads a resource file, then walks
texture-default/mesh-status/particle-set initialization against the
loading bar, finishing with physics definition-reference resolution.
The two float-range pairs encode the released loading-bar choreography:
30–65 while reading resources, then 30–75 during status polling.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famA/LoadResources.txt`), raw byte reads (body
hash), and name-table resolution. No `FUN_*` milled; no Core owner
invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046cd30`–`0x0046cde3` inclusive, **180 bytes**, SHA-256
`ace53e77e785bd5265ca6d88854991c82c48e9b8e35c2f2c2cd197d85b07468b`.
9 direct `E8`, zero decoded `E9`. Caller convention: `this` in `ecx`
(ignored by every callee here — no `[esi]` dereference exists in the
body); two stack parameters read at `[esp+0x10]` (flag) and
`[esp+0xc]` (inLoadedSounds) — at the sole call site these cells are
the caller's saved-`ebp`/saved-`ebx` slots, so the effective values
are `(level_number, 0)`; see
[`CGame__RunLevel.md`](CGame__RunLevel.md) step 6. Returns nonzero via
`ret 8`.
Boundary: twelve `nop` (`0x0046cde4`–`0x0046cdef`) then
`CGame__LoadLevel` at `0x0046cdf0`.

Sequence:

1. `CConsole__SetLoading(1, 1, 1)` (`0x0042bbc0`; stdcall `ret 0xc`
   tail verified this wake).
2. `CConsole__RenderLoadingScreen(0, 0)` (`0x0042c810`).
3. `esi = [esp+0x10]`; if nonzero → `SetLoadingRange(50.0f, 65.0f)`,
   else `SetLoadingRange(30.0f, 0.0f)` (float constants `0x42820000`,
   `0x42480000`, `0x41f00000`; the zero lower bound is the
   not-yet-started arm).
4. If global `[0x00662dd4] == 0`:
   `CResourceAccumulator__ReadResourceFile(inLoadedSounds)`
   (`0x004d7200`) — the only file read in the body.
5. Second range pair: `SetLoadingRange(75.0f, 50.0f)` when `esi`
   nonzero, else `SetLoadingRange(30.0f, 50.0f)` (`0x42960000`).
6. Status polling loop against the bar:
   `CTexture__InitDefaultTextureResourcesAndStatus(inLoadedSounds)`
   (`0x004f29c0`), then
   `CMesh__StatusLoadingMeshResources(inLoadedSounds)` (`0x004a53f0`),
   then `CParticleSet__LoadParticleSetFile(0)` with `ecx = 0x0082b400`
   (`0x004cda60`). Zero return → early `ret 8` (failure); nonzero →
   `CWorldPhysicsManager__ResolveLoadedDefinitionReferences`
   (`0x00510520`), `eax = 1`, `ret 8`.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `0x00663498` | global `CConsole` (all seven console calls) | `0x0046cd38` et al. |
| `0x00662dd4` | read-resource gate (0 = must read) | `0x0046cd75` |
| `0x0082b400` | particle-set owner passed to `LoadParticleSetFile` | `0x0046cdc2` |
| `0x41f00000 / 0x42480000 / 0x42820000 / 0x42960000` | 30.0f / 50.0f / 65.0f / 75.0f range constants | `0x0046cd58`–`0x0046cda4` |

## Callers

Whole-`.text` rel32 scan: **one** inbound `E8` — `0x0046e303` in
`CGame__RunLevel`, inside the one-off resource block (see
[`CGame__RunLevel.md`](CGame__RunLevel.md)). Zero `E9`. The
`(level_number, 0)` effective argument pair at that site selects the
50–65 / 75–50 arms; the 30-based arms belong to other callers' shapes
retained by the compiler from source paths the shell does not take.

## Pinned-source status

`references/Onslaught/game.cpp:624` is the source twin ("level resource
bundle accumulation … loading-range progression based on
`inLoadedSounds`"). The bytes agree and add: the exact four range
pairs, the `0x00662dd4` gate around `ReadResourceFile`, the three-callee
status walk order (textures → meshes → particles), and the physics
resolve tail. Divergence from the older note's claim "called from
`CGame__RunLevel` before one-off and restart-loop resource setup": the
call sits **inside** the one-off block between `InitRestartLoop` and
the restart loop, and it is never repeated on restart — corrected this
wake.

## Rebuild mapping

No Core owner yet models a retail-style staged loader; the campaign-flow
owner (`rebuild/OnslaughtRebuild.Core/RetailWorldCatalog.cs`,
`RetailCampaignFlowTests`) owns admission but not resource staging.
When a load-sequencing owner lands, this body maps to
"one-off stage: ranges + optional ReadResourceFile + status walk +
physics resolve", with the caller-side choreography owned by the
RunLevel driver note. Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046cd30`–`0x0046cde3` is not
  `ace53e77…7468b`, or the body does not end `85 c0 75 03 c2 08 00`.
- The range immediates are anything but the four recorded floats, or
  `SetLoadingRange` resolves anywhere but `0x0042cf40`.
- A second inbound rel32 to `0x0046cd30` appears.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body
  disassembly (`local-lab/famA/LoadResources.txt`), raw byte reads
  (body hash; float constants), whole-`.text` rel32 xref scan
  (`local-lab/famA_xrefs.py`), name-table resolution
  (`tools/xref_targets.py`: all nine targets named functions).
- Corroboration (not duplicated): [`CGame__RunLevel.md`](CGame__RunLevel.md)
  pins the caller-side choreography; `CConsole` call identities match
  the console singleton usage pinned across `game.cpp` notes.
