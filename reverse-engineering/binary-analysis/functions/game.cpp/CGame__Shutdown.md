# CGame__Shutdown

> Address: `0x0046c990`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:414` (`CGame::Shutdown`) |
Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: One-off level-system shutdown — the inverse of the
`Init`/resource block, run by `RunLevel` only after the restart loop
finally exits (through the `[vtable+8]` virtual teardown this body's
caller chain uses; see caller note). This wake pins its released
ordering from bytes: music stop → HUD/interface shutdown → particle
sets → DX particle textures → static shadows → imposter globals →
render-state reset → engine/map shutdown → memory merge toggle +
cleanup → mesh/texture/waypoint frees → outro FMV → console status +
list clear.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famA/Shutdown.txt`), raw byte reads (body
hash), whole-`.text` rel32 xref scan, and name-table resolution. No
`FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046c990`–`0x0046ca6b` inclusive through the final `c3`,
**220 bytes**, SHA-256
`a2e3b4e7b380794d87ae4602c347d3ef2fe5be229549a3e634ee56abb6d02858`.
22 direct `E8`, zero decoded `E9`. `this` in `ecx`; returns void.
Boundary: single `nop` at `0x0046ca6c`–`0x0046ca6f` is four `90`
bytes (`0x0046ca6c`–`0x0046ca6f`), then `CGame__ShutdownRestartLoop`
at `0x0046ca70`.

Released order:

1. `CMusic__Stop` on `0x00889a48` (`0x004bb490`).
2. `CHud__ShutDown` on `0x008aa4e8` (`0x00481b00`);
   `CGameInterface__Shutdown` on `0x00679fa8` (`0x00472a50`).
3. `CParticleManager__DestroyParticleSetList` (`0x004cbff0`);
   `DXParticleTexture__DestroyAll` (`0x0054fee0`).
4. Static shadows / imposters:
   `CStaticShadows__ClearAllShadowEntries` (`0x004ebd10`);
   `CDXImposter__ShutdownAll` (`0x00542990`);
   `CEngine__SetRenderStateCached` (`0x00513a50`).
5. Engine/map: `CDXEngine__Shutdown` (`0x0053d3e0`);
   `CHeightField__ShutdownAndDestroyMixerMap` on `0x006fadc8`
   (`0x00490f40`).
6. Memory: `CMemoryHeap__SetMerge(0)` then `SetMerge(1)` around
   `MEM_MANAGER__Cleanup` (`0x004a1ea0`, `0x00549270`) — the merge
   toggle brackets the cleanup exactly as the Wave1003 read-back
   recorded.
7. Mesh/texture/waypoint frees:
   `CMesh__FreeUnusedAndReportLeaks` (`0x004a5430`);
   `CTexture__FreeLevelResources` (`0x004f2b40`);
   `CSPtrSet__ClearAnyDynamicCreatedNodes` (`0x004e5990`);
   `CWaypoint__CleanupEndLevelVBufTextures` (`0x00501360`).
8. Outro: `CGame__RunOutroFMV(this)` (`0x0046d9f0`).
9. Console: `CConsole__StatusDone` (`0x0042b800`);
   `CConsole__ClearCommandAndVariableLists` (`0x0042af20`). Return.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `0x008aa4e8` | global `CHud` | `0x0046c99c` region |
| `0x00889a48` | global `CMusic` | `0x0046c997` region |
| `0x00679fa8` | global game-interface owner | `0x0046c9b1` region |
| `0x006fadc8` | height-field owner | `0x0046ca09` region |
| memory-heap merge toggle | bracket around `MEM_MANAGER__Cleanup` | `0x0046c9f0`–`0x0046ca38` |

(The exact per-call addresses are in the committed disassembly listing
`local-lab/famA/Shutdown.txt`; this table records the load-bearing
singletons.)

## Callers

Whole-`.text` rel32 scan for `0x0046c990`: **zero** inbound `E8`, zero
`E9`. The one-off shutdown is reached only as a virtual call —
`CGame__RunLevel` performs `mov edx, [esi]; call [edx+8]` at
`0x0046e432`/`0x0046e436` after `Init` failure and at common exit,
which is the vtable slot whose retail value targets this body. The
DATA references at `0x005dbbbc`/`0x005e50a4` recorded by Wave1003 are
that vtable slot's image copies. This corrects the older note's
"called from both…" framing: no direct rel32 caller exists.

## Pinned-source status

`references/Onslaught/game.cpp:414` is the source twin ("one-off level
system shutdown; releases HUD/interface/particles/shadows/engine/map/
mesh/texture resources, runs the PC outro path, clears console
registrations"). The bytes agree and add the exact order above plus
the two-step `SetMerge` bracket. The Wave1003 boundary recovery that
created this function object remains the boundary authority.

## Rebuild mapping

No Core owner models a retail-style one-off teardown. When one lands,
the order above is the contract; most load-bearing for parity: engine
shutdown before mesh/texture frees, the merge-bracketed cleanup, and
the outro FMV before console teardown. Focused test deferred until
that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046c990`–`0x0046ca6b` is not
  `a2e3b4e7…02858`, or the body does not end with
  `CConsole__ClearCommandAndVariableLists` followed by pops and `c3`.
- A direct inbound rel32 to `0x0046c990` appears anywhere in `.text`.
- The merge toggle is anything but `(0) … (1)` around
  `MEM_MANAGER__Cleanup`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body
  disassembly (`local-lab/famA/Shutdown.txt`), raw byte reads (body
  hash), whole-`.text` rel32 xref scan (`local-lab/famA_xrefs.py`),
  name-table resolution (`tools/xref_targets.py`).
- Corroboration (not duplicated): Wave1003 boundary evidence recorded
  in this note's prior revision and in
  [`../../ghidra-full-reaudit-closeout-2026-07-13.md`](../../ghidra-full-reaudit-closeout-2026-07-13.md)-adjacent
  material;
  [`../../cgame-level-lifecycle-semantics-2026-08-11.md`](../../cgame-level-lifecycle-semantics-2026-08-11.md)
  bounds the demo twin.
