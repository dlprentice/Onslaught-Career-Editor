# Source-first expansion W5 — engine, render, platform, and shell contract

Status: complete — 136-definition source-first wave receipt awaiting independent review
Date: 2026-08-22
Summary: every omitted definition in the exact W5 ten-file set is recorded with its pinned source line/signature, source algorithm and side effects, PC target selection, bounded retail disposition, falsifier, and current rebuild disposition. The canonical 1,149-row crosswalk and its report remain unchanged for the later sole-writer reducer.
Evidence: SOURCE + MEASURED — pinned source lines define the source contracts; tracked Generation-32 catalogs, promoted semantic tables, and W008/W009 static plates bound the retail analogs and deltas. This wave performed no new byte or runtime measurement.
Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, 2,506,752 bytes; cited through tracked predecessor evidence only and not opened or written by this wave.

## Authority and boundary

This receipt is derived first from Stuart Gillam's pinned source at
`references/Onslaught@5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.
Retail correspondence is bounded by the current tracked name table and static
closure, the promoted shell table, the W008/W009 primary/adversarial plates,
and the corrected 1,149-row crosswalk at base commit
`784367bd43f9ec13125521b00fe0c8352670ffdd`.

The retail specimen identity remains `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
2,506,752 bytes. This wave did not open or write the specimen, mutate Ghidra,
write a retail binary, or add a retail payload. Static evidence proves only the
identity, ABI, and body role it names. A source analogy is not retail equality.

The row authority is [`definitions.tsv`](definitions.tsv). Its stable key is
`(source_file, source_line, function, signature)`; repeated labels and
preprocessor alternatives are not collapsed. [`RETAIL-DELTA.tsv`](RETAIL-DELTA.tsv)
separates source agreement, divergence, unresolved retail identity, source-only
bodies, and definitions outside the selected PC target. The validator
[`validate.py`](validate.py) checks exact source-line readback, counts, hashes,
VA uniqueness, and zero collisions with the corrected base.

## Corpus hygiene and reuse preflight

Before extending the tracked W5 root, this wave read the workstation routing
index, `local-lab/CORPUS-HYGIENE-2026-08-22.md`, and the shared expansion
`EXECUTION.md`. It searched tracked owners and
`local-lab/INDEX-CATALOG-2026-08-17.md` by the engine/render/platform/shell
subsystem, representative stable keys, all nine populated VAs, the shared-plan
hashes, and the inventory/crosswalk tool names.

The August 17 catalog predates this August 22 expansion plan and contains no
exact W5 stable-key or shared-partition-hash owner. Its one relevant historical
hit is an explicitly unverified `0x00513820` COLOROP/state-shadow claim. This
wave does not inherit that claim: the current tracked W009 plates and tracked
`ghidra-functions.md` correction own the D3D9 API role. No generic inventory,
PS2 crosswalk, new local-lab root, or new retail measurement was created.

Every one of the 136 definition rows is classified `EXTENDED`: the stable key
and readiness came from the shared partition, then this wave added source
algorithm/side-effect readback, target selection, bounded retail/rebuild
disposition, and a falsifier. None is counted as a new measurement. The receipt
records definition reuse as `REUSED 0 / EXTENDED 136 / NEW_MEASUREMENT 0` and
artifact reuse as `REUSED 13 / EXTENDED 6 / NEW_MEASUREMENT 0`.

| Reused predecessor | SHA-256 |
| --- | --- |
| `local-lab/.../source-first-expansion/PLAN.md` | `604d5db76ecc9811b55321c5ec443f346c9be32515b6d8ed526142622d7ec393` |
| `local-lab/.../source-first-expansion/EXECUTION.md` | `12a0f72ea2b1606ee673824ee801586cefe815e0aa899d2fe55073e7c4509f18` |
| `local-lab/.../source-first-expansion/manifest.json` | `6f58de995a27a0088749f40e06907969d3213872b40d1bf0bb450afda1fd216e` |
| `local-lab/.../source-first-expansion/partition.tsv` | `bc36791975f43d5da6b584727df3eb7d29402e18c550dd3d96e01bba0c301fde` |
| `reverse-engineering/source-crosswalk/crosswalk.tsv` | `e37f13b37e9ce9d712174e35b86fc1f7ebcfc693fe9957448a8f39ff03829479` |
| `ghidra-function-name-table-2026-08-17.tsv` | `4590dff93f4ee85c5a5c3450139b2e696118646af3401f6eb9719dc4237d3213` |
| `function-c1-closure-2026-08-11.tsv` | `cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974` |
| `pcltshell-vtable-semantics-2026-08-11.tsv` | `c1510d9baa0d6a633bf0d9514b7fc9ce3a5eb32070e1643181467ae2cffe7d1b` |
| `W008/adversarial/B15.md` | `a57fb6c7d35eefc4384f7faf56cb79aee77d0c9897d1c4aefe0f3ea770e3e7fd` |
| `W009/primary/A01.md` | `bc1727dfb86d7f9f9aecf27a487e04796bfcf0986ace61cc82970578b9cb68b7` |
| `W009/primary/A02.md` | `59524647a4f21496ad8a3f1247aecd2354b02119115796b61cbe2eee809abba8` |
| `W009/primary/A04.md` | `70ebd87bd8905e7202dd439b3386739023573d95e8c6729237dece1a8911ed61` |
| `stuart-source-synthesis.md` | `62c53e7e266b774c0d1ebe5c433203b9be08a972b911964ab3423fdbb86b417f` |

Generation-32's current name table/static closure and the shared
partition/manifest are reused as inputs; no parallel catalog replaces them.
No files were moved, deleted, retired, or quarantine-staged. H retirement and
all generic PS2 work remain outside this wave.

## Exact denominator

| Source file | Definitions | Selected source role |
| --- | ---: | --- |
| `d3dapp.h` | 11 | Non-editor D3D application base |
| `DXEngine.cpp` | 1 | One Xbox-only local FVF definition |
| `DXEngine.h` | 6 | Active `_DIRECTX` engine accessors/stubs |
| `EditorD3DApp.h` | 11 | `EDITORBUILD2` alternate base |
| `engine.h` | 39 | Common engine state, viewport, and resource access |
| `ltshell.cpp` | 1 | PC shell constructor |
| `ltshell.h` | 40 | PC shell state/input/device wrappers |
| `PCEngine.h` | 11 | Legacy `CPCEngine` alternate, not the active `_DIRECTX` owner |
| `PCPlatform.h` | 8 | PC platform state/font accessors |
| `ResourceAccumulator.h` | 8 | Runtime resource identifiers/targets/handles |
| **Total** | **136** | Exact W5 set |

The planning partition began at 0 exact, 1 named analog, 118 source-only, 7
ambiguous, and 10 external-proof definitions. The source-first/target-selection
and bounded-alias recheck ends at:

| Retail classification | Rows | Meaning |
| --- | ---: | --- |
| `SOURCE_ANALOG` | 9 | Precise retail VA and bounded role; no source-body equality claim |
| `NOT_IN_RETAIL` | 23 | Exact alternate target definition not selected by the PC retail player |
| `NO_MATCH_FOUND` | 104 | Empty VA after the named authority/alias search; not binary absence |
| **Total** | **136** | No duplicate stable keys or populated-VA collisions |

There are zero `SOURCE_EXACT` rows. None of these newly admitted definitions has
an explicit promoted same-source-body authority strong enough for that class.

## Target-selection contract

The source contains parallel framework and engine families; file presence alone
does not establish retail membership.

- `PCLTShell` derives from `CD3DApplication` unless `EDITORBUILD2` selects
  `CEditorD3DApp` ([`ltshell.h:52-56`](../../../../references/Onslaught/ltshell.h#L52-L56)).
  The 11 editor-base definitions are therefore `NOT_IN_RETAIL` for the retail
  player target, not negative name searches.
- `_DIRECTX` selects `CDXEngine`; `CPCEngine` is not selected by the active
  `ENGINE` declaration ([`engine.h:229-232`](../../../../references/Onslaught/engine.h#L229-L232)).
  All 11 `PCEngine.h` rows are recorded as `NOT_IN_RETAIL`, including its internal
  PC/Xbox `GetSky` alternatives.
- `DXEngine.cpp:1166 Vert::FVF` is inside the `TARGET == XBOX` block beginning at
  [`DXEngine.cpp:1124`](../../../../references/Onslaught/DXEngine.cpp#L1124), so
  the PC row is `NOT_IN_RETAIL` even though `DXEngine` as a whole is shared.
- `ltshell.h:201-205` has parallel `LT_DEBUG` and non-`LT_DEBUG` `ForceRS`/
  `ForceTS` definitions. This wave does not guess the Steam build flag. The two
  debug rows remain unresolved and empty-VA; the non-debug rows receive bounded
  retail analogs because the retail raw-setter bodies establish that role.

This follows the source-synthesis warning that `d3dapp.*` and
`EditorD3DApp.*` are mutually selected framework bases and that one guarded
region must not classify an entire source unit
([`stuart-source-synthesis.md:2212-2219`](../../../source-code/stuart-source-synthesis.md#L2212-L2219)).

## Source architecture and algorithms

### D3D framework lifecycle

`CD3DApplication` owns adapter/device selection, window/device handles,
presentation parameters, backbuffer description, timing, and the overridable
scene lifecycle ([`d3dapp.h:101-188`](../../../../references/Onslaught/d3dapp.h#L101-L188)).
The nine omitted lifecycle definitions in this header are deliberate `S_OK`
stubs. They are defaults, not evidence that the retail `PCLTShell` overrides do
nothing. The promoted shell table independently identifies retail
`InitDeviceObjects`, `RestoreDeviceObjects`, `InvalidateDeviceObjects`,
`DeleteDeviceObjects`, and `FinalCleanup` as nontrivial selected overrides
([`pcltshell-vtable-semantics-2026-08-11.tsv`](../../../binary-analysis/pcltshell-vtable-semantics-2026-08-11.tsv)).

`GetHWnd` is a direct handle read. `ForceToWindow` calls
`ToggleFullscreen` only when `m_bWindowed` is false
([`d3dapp.h:199-204`](../../../../references/Onslaught/d3dapp.h#L199-L204)).
The tracked retail `CD3DApplication__ForceWindowed` body is not equated to that
small helper merely because the names are close.

### Engine state and viewports

The common engine fixes `VIEWPOINTS` to 2, seeds source defaults of near `0.1`
and far `256.0`, and stores per-viewpoint camera/player/viewport arrays plus a
by-value current viewport ([`engine.h:13-16`](../../../../references/Onslaught/engine.h#L13-L16),
[`engine.h:66-104`](../../../../references/Onslaught/engine.h#L66-L104)). The
omitted definitions expose four kinds of law:

1. reference-counting mesh access (`GetDefaultMesh`, `GetGlobalMesh`);
2. current/per-viewpoint camera, player, viewport, near/far, and viewport-count
   access ([`engine.h:116-154`](../../../../references/Onslaught/engine.h#L116-L154));
3. debug/particle/HUD mode toggles and texture/light/landscape access;
4. thin landscape damage delegates, where removal passes `-size` back through
   `AddDamage` ([`engine.h:179-182`](../../../../references/Onslaught/engine.h#L179-L182)).

These inline laws are source-visible and recorded exactly, but most have no
separately identifiable retail body: inlining/folding remains a live
falsifier. The active `CDXEngine` adds screen-capture bounds, outline/opaque
textures, and an intentional no-op `SetDefaultMaterial`
([`DXEngine.h:49-83`](../../../../references/Onslaught/DXEngine.h#L49-L83)).
That source no-op must not be confused with the separate
`ReallySetDefaultMaterial` path.

### PC shell state cache and input edges

`PCLTShell` is the D3D/window/input adapter. It owns four joypads, held and
one-shot key tables, mouse state, DirectInput pointers, device-object lists,
render-state/texture-stage mirrors, current textures, and the last vertex shader
([`ltshell.h:48-118`](../../../../references/Onslaught/ltshell.h#L48-L118)).
The source constructor nulls per-pad pointers and states, enables rumble and the
depth buffer, selects fullscreen, clears the joypad count, and leaves texture
compression enabled ([`ltshell.cpp:774-795`](../../../../references/Onslaught/ltshell.cpp#L774-L795)).
W008 confirms the corresponding retail base/vtable/field-clear/title-copy
shape without proving byte equality
([`W008/adversarial/B15.md:164-171`](../../../binary-analysis/ghidra-fullpass-findings/W008/adversarial/B15.md#L164-L171)).

The source's cached setters dispatch only on a value change; force setters write
unconditionally; `SRS_Ret` caches only a successful HRESULT
([`ltshell.h:175-220`](../../../../references/Onslaught/ltshell.h#L175-L220)).
Retail keeps the caching architecture but moved from D3D8 member calls to D3D9
helpers/global mirrors. That API/cache-layout change is recorded as
`SOURCE_DIVERGES`, not normalized away.

Input has two distinct laws:

- `xKeyOn` reads the held-key byte;
- `xKeyOnce` reads and clears the one-shot byte
  ([`ltshell.h:290-292`](../../../../references/Onslaught/ltshell.h#L290-L292)).

W009 proves the corresponding retail held read and consume-and-clear bodies at
`0x00515970` and `0x00515980`
([`W009/primary/A04.md:30-54`](../../../binary-analysis/ghidra-fullpass-findings/W009/primary/A04.md#L30-L54)).
The joystick helpers separately encode rising, held, and falling edges by
comparing old/current button bytes
([`ltshell.h:306-319`](../../../../references/Onslaught/ltshell.h#L306-L319));
their standalone retail identity remains unresolved.

### Platform and resource access

`CPCPlatform` owns timer/frequency scale, a GeForce3 flag, measured memory size,
and six font pointers. The omitted definitions are direct flag/size/font
accessors ([`PCPlatform.h:101-150`](../../../../references/Onslaught/PCPlatform.h#L101-L150)).
`CPlatform__Font @ 0x00515A70` is not assigned to the no-argument `Font()` row:
the retail function takes a font id and selects four slots, so its ABI/body
contradicts this direct default-font accessor
([`W009/primary/A04.md:95-106`](../../../binary-analysis/ghidra-fullpass-findings/W009/primary/A04.md#L95-L106)).

`CResourceAccumulator` uses fixed 100-mesh/1,000-texture arrays, a post-increment
resource id, target platform/level fields, static file handles/name, last-loaded
level, and an output page writer
([`ResourceAccumulator.h:11-31`](../../../../references/Onslaught/ResourceAccumulator.h#L11-L31),
[`ResourceAccumulator.h:62-108`](../../../../references/Onslaught/ResourceAccumulator.h#L62-L108)).
The similarly named retail
`CResourceAccumulator__GetResourceFilename @ 0x004D6F70` is a three-argument
path builder, not the header's zero-argument static char-pointer accessor; the
row remains an evidence-backed bounded no-match rather than taking the name hit.

## Nine bounded analogs

| Stable source identity | Retail target | Strongest bounded statement |
| --- | --- | --- |
| `ltshell.cpp:774 PCLTShell::PCLTShell` | `0x00512670 PCLTShell__ctor` | Base/vtable/clears/title shape agrees; no byte-equality claim |
| `ltshell.h:175 PCLTShell::SRS` | `0x00513BC0 RenderState_Set` | Cached render-state role; D3D8→D3D9 divergence |
| `ltshell.h:190 PCLTShell::STS` | `0x00513820 D3DStateCache__SetStateCached` | Cached texture-stage role; D3D8→D3D9 divergence |
| `ltshell.h:204 PCLTShell::ForceRS` | `0x00513C20 RenderState_SetRaw` | Selected release raw render-state role |
| `ltshell.h:205 PCLTShell::ForceTS` | `0x00513870 D3DStateCache__SetStateRaw` | Selected release raw texture-stage role |
| `ltshell.h:221 PCLTShell::D3D_SetTexture` | `0x00513A50` | Cached SetTexture role; tracked current name is known false |
| `ltshell.h:222 PCLTShell::D3D_SetVertexShader` | `0x00513E90 CEngine__SetVertexShaderHandleCached` | Duplicate-handle suppression only |
| `ltshell.h:291 PCLTShell::xKeyOn` | `0x00515970 PlatformInput__GetKeyOn` | Held-byte read agrees statically |
| `ltshell.h:292 PCLTShell::xKeyOnce` | `0x00515980 PlatformInput__ConsumeKeyOnce` | Read-and-clear agrees statically |

The 0x00513A50 row deliberately cites the measured role rather than promoting
its known-false live label; [`ghidra-functions.md:1613-1618`](../../../ghidra-functions.md#L1613-L1618)
is the tracked correction owner.

## Negative and ambiguity controls

- Empty VA means no supported line/signature-specific join under the current
  instruments. It never means the body is absent from the binary.
- Shared labels do not collapse definitions. The LT_DEBUG/release force setters,
  the old PC/Xbox `GetSky` alternatives, and the no-argument/typed `Font`
  overloads stay line-distinct.
- A current name hit is rejected when ABI/body differs. The resource filename,
  default font, shell window dimensions, and base `ForceToWindow` rows carry the
  rejected candidate in the receipt rather than silently taking it.
- Populated VAs are unique within W5 and do not collide with any populated VA in
  the corrected base. Candidate aliases already owned by a base row remain
  empty-VA here.
- Every negative row names a falsifier: a precise body/ABI/vtable/caller witness
  or controlled runtime observation can replace the bounded no-match later.

## Validation contract

Run from the repository root:

```powershell
py -3 reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/validate.py
npm run test:docs
git diff --check
```

The later canonical reducer, not this wave, owns edits to
`reverse-engineering/source-crosswalk/crosswalk.tsv` and its canonical
`REPORT.md`.
