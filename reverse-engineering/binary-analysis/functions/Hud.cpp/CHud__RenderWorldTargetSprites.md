# CHud__RenderWorldTargetSprites

> Address: `0x00486e00`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/BattleEngine.cpp` owns only the
`CLockInfo::GetLockPercentage` callee (lines 3142–3150);
`CHud::RenderWorldTargetSprites` / `RenderOverlayForViewpoint` have
no `Hud.cpp` in `references/Onslaught/` (checked 2026-08-22) | Binary:
BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the lock-HUD path is not `DisplayLock` and not the radar
blob picker. `CHud__Render` (`0x00487bc0`) calls
`CHud__RenderOverlayForViewpoint` (`0x004879e0`) once per viewpoint;
that dispatcher’s **first** overlay after shared sprite state is
`CHud__RenderWorldTargetSprites` (`0x00486e00`). The body walks the
already-pinned BattleEngine lock sets at `this+0x294` then
`this+0x2a4` (hud `+0x50` is that BattleEngine), calls
`CLockInfo__GetLockPercentage` (`0x0040d5b0`) on each live
`CLockInfo`, and draws the `hud\\v3\\hud_lock_on_piece{1,2,3}.tga`
trio while the percentage is `< 1.0` or the
`hud_lock_on_pieces_all` / `hud_target_lockedon_red` pair once it is
not. The percentage formula is byte-identical to Stuart
`CLockInfo::GetLockPercentage`:
`(mTime + GetFrameRenderFraction * CLOCK_TICK − mStart) / (mFinish − mStart)`
clamped at `1.0f`. No `FUN_*` milled; no Core owner invented.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
verified before reading; twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
byte-identical, 2,506,752 B) with `tools/disasm_va.py` (whole
bodies), raw byte reads (body hashes, float constants, LoadTextures
path immediates), and `tools/call_xref_scan.py`.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding (name vs. behavior)

W005 plates describe `RenderWorldTargetSprites` as a “lock-list /
objective-marker walk” and `SelectMarkerTextureIndexByUnitFlags` as
the radar-contact texture picker. Both labels survive this wake,
plus one correction to the implied lock-HUD reading:

- The **lock diamonds** are this function, not
  `CBattleEngine__DisplayLock` (`0x00407310`). DisplayLock is the
  already-pinned “current weapon equals stack arg” predicate; its
  only inbound is `ProjectileBurst__SpawnFromCurrentPreset`
  `0x005074bb`. It never draws.
- `CHud__SelectMarkerTextureIndexByUnitFlags` (`0x00485830`) returns
  one of `hud+0x1a0/0x1a4/0x1a8` =
  `ScannerBlob{Small,Medium,Large}.tga`. Its four inbound `E8`s all
  sit inside `CHud__RenderTacticalRadarContacts`. It is not on the
  lock-list path.
- The **percentage** that chooses in-progress pieces vs the locked-on
  pair is `CLockInfo__GetLockPercentage`. Exactly two image-wide
  rel32 callers, both in this body (`0x00486fd5` on the `+0x294`
  walk, `0x004872b2` on the `+0x2a4` walk).

Siblings already on this branch:
[`CBattleEngine__FireLock.md`](../BattleEngine.cpp/CBattleEngine__FireLock.md)
(writes `mStart` / `mFinish = mStart+0.5f` into the `+0x2a4` set),
[`CBattleEngine__AddProjectile.md`](../BattleEngine.cpp/CBattleEngine__AddProjectile.md)
(`StartLock` appends to `+0x294`),
[`CBattleEngine__LockHit.md`](../BattleEngine.cpp/CBattleEngine__LockHit.md).

## Contract (byte-exact)

### Dispatcher `CHud__RenderOverlayForViewpoint` — `0x004879e0`, 477 bytes

Body `0x004879e0`–`0x00487bbc` inclusive through `ret 0x8`, SHA-256
`59b6a535b636c3b79c12c7c6cf34e55511dc6047e29cf352dab79476812936a9`.
Fourteen `E8`, zero `E9`. Incoming-ECX thiscall; two stack args
(viewpoint*, viewpoint_index). The entry `push ecx` / epilogue
`pop ecx` is local scratch, not a third argument — W005 A01/B01
already flagged that, and the sole inbound at `0x00487c57` inside
`CHud__Render` (`0x00487bc0`–`0x00487d0b`) matches `ret 0x8`.

Early-out (shared epilogue `0x00487bb7`): `ebp = [arg0+0x1c]`; null
or `[ebp+0x2c] & 4` (`TF_DYING`, `thing.h:45`) skips every overlay.

After the clip / window-size setup (callees
`CEngine__SelectViewpoint` `0x0044a0d0`,
`PLATFORM__GetWindowWidth` `0x00515940`,
`PLATFORM__GetWindowHeight` `0x00515b00`; constants
`0x0062ce74 = 0.85f` and `0x005d85ec = 0.5f` used only here — not
re-derived), the body stores hud context and dispatches, in this
order. Context stores first, then the overlay calls:

- `0x00487b30` `[hud+0x50] = ebp` (the viewpoint thing = BattleEngine)
- `0x00487b33` `[hud+0x54] = edi` (selected viewpoint record)
- `0x00487b36` `[hud+0x58] = ebx` (viewpoint index)

| Callee | Current name | Instruction |
| --- | --- | --- |
| `0x00482090` | `HudRenderState__ApplyOverlaySpriteState` | `0x00487b56` |
| `0x00513bc0` | `RenderState_Set` | `0x00487b64` (`push 0; push 0xf`) |
| `0x00486e00` | `CHud__RenderWorldTargetSprites` | `0x00487b6b` (lock-HUD) |
| `0x00482590` | `CHud__RenderTargetIndicatorOverlay` | `0x00487b72` |
| `0x0047fb50` | `CHelpTextDisplay__RenderQueuedMessages` | `0x00487b83` (only if `[0x008a9d90]`) |
| `0x00483530` | `CHud__RoutePanel_T0_00483530` | `0x00487b8a` |
| `0x00484340` | `CHud__RenderTargetMarkers3D` | `0x00487b91` |
| `0x004858d0` | `CHud__RoutePanel_T3_004858d0` | `0x00487b98` |
| `0x00485d50` | `CHud__RoutePanel_T4_00485d50` | `0x00487b9f` |
| `0x00486940` | `CHud__RoutePanel_T5_00486940` | `0x00487ba6` |
| `0x00484c50` | `CHud__RenderTacticalRadarContacts` | `0x00487bb2` (`push 0x42c00000` = `96.0f`) |

HIGH on ABI, `ret 0x8`, the `+0x50/+0x54/+0x58` stores, the
TF_DYING early-out, and this call order. Not claimed: the clip
algebra or the authored names of RoutePanel_T{0,3,4,5}.

### `CHud__RenderWorldTargetSprites` — `0x00486e00`, 3031 bytes

Body `0x00486e00`–`0x004879d6` inclusive through bare `ret`, SHA-256
`60b658929ae75c144054bf6e37423e322af0ae14b6c6adf850c1d2c68b4e3325`.
902 Capstone insns; 48 `E8`, 3 `E9`. Incoming-ECX thiscall; zero
stack args. Sole inbound `E8` is the dispatcher site above. Neighbor
is three `nop` then `CHud__RenderOverlayForViewpoint`.

**Prologue (not the lock walk).** Copies three 16-dword matrices
keyed by `[hud+0x58]`, applies overlay sprite state, ticks
`[hud + viewpoint*4 + 0x1b8]` by `[0x008a9e20] * 0.05f` wrapped at
`2π` (`0x005d85e0`). Those matrices and the wrap are **not** this
proof.

**Acquiring-lock walk (`0x00486f07`).**
`ebx = [hud+0x50] + 0x294`. Inline `CSPtrSet::First()`:
`eax = [ebx]; [ebx+8] = eax; payload = eax ? [eax] : 0`. Empty set
jumps to the fired walk at `0x004871e0`. Else `esi = payload`
(`CLockInfo*`).

Per live node (`0x00486f38`):

1. `CUnit__ApplyRenderPositionDeltaToVector` `0x004fd500` on
   `[esi]` (the lock’s unit) into a local.
2. A viewpoint vfunc pair (`[edi]` / `[edi+4]`) builds a camera-space
   delta. `fcomp [0x005d8580]` (`0.001f`); `test ah, 0x41` / `jne`
   skips the draw (behind / degenerate). Projection algebra is
   **not** claimed.
3. `CDXEngine__PushTransformState` `0x00551300` with `[hud+0x54]`.
4. `mov ecx, esi; call 0x0040d5b0` —
   `CLockInfo__GetLockPercentage`.
5. `fcom [0x005d8568]` (`1.0f`); `test ah, 1` (`C0` = ST0 `< 1.0`);
   `je 0x00487129` is the **completed** arm. So:
   - percentage `< 1.0` → three `CVBufTexture__DrawSpriteEx`
     `0x00555be0` using `[hud+0x1c8]`, `[hud+0x1cc]`, `[hud+0x1d0]`;
   - percentage `>= 1.0` → two `DrawSpriteEx` using `[hud+0x1b0]`
     then `[hud+0x1b4]`.

**Next (`0x004871c3`).** Inline `CSPtrSet::Next()`:
`eax = [[ebx+8]+4]; [ebx+8] = eax; payload = eax ? [eax] : 0`;
nonzero loops to `0x00486f38`.

**Fired-lock walk (`0x004871e0`).**
`ebx = [hud+0x50] + 0x2a4`, same First/Next shape, same
`GetLockPercentage` at `0x004872b2`, same `< 1.0` vs completed
split. The `+0x294` / `+0x2a4` pair is the occupancy FireLock /
StartLock already pinned.

**After both lock walks** the body walks the world unit set
(`[0x00855140]` cursor) and may call `CThing__GetCentrePos`
`0x004f3ac0`. That objective / off-screen marker pass is **not**
this proof.

HIGH on the two set bases, First/Next, both `GetLockPercentage`
sites, the `< 1.0` discriminator, the five hud texture slots, and
the unique inbound. Not claimed: DrawSpriteEx argument packing,
the `0x3c54fdf4` depth immediate, ARGB construction
(`0xffffff` / `0xc8ffffff` / `0x80ff5555` are present as immediates
only), or the third walk.

### `CLockInfo__GetLockPercentage` — `0x0040d5b0`, 51 bytes

Body `0x0040d5b0`–`0x0040d5e2` inclusive through bare `ret`, SHA-256
`aa65f86303098b2e68181ccb4b40e915e98cece8ae5a178a282c40ffc16900f2`.
Zero `E8` / zero `E9`. Incoming-ECX thiscall; zero stack args; ST0
return. Two inbound `E8` (list above). Zero encodings of imm
`b0 d5 40 00` in the image.

```
fld  dword [0x008a9e44]     ; GAME.GetFrameRenderFraction (BSS)
fmul dword [0x005d8578]     ; CLOCK_TICK = 0.05f (thing.h:29)
fadd dword [0x00672fd0]     ; EVENT_MANAGER mTime
fsub dword [ecx+4]          ; minus mStart
fld  dword [ecx+8]          ; mFinish
fsub dword [ecx+4]          ; mFinish - mStart
fdivp st(1), st(0)
fcom dword [0x005d8568]     ; 1.0f
fnstsw ax
test ah, 0x41               ; C0|C3  =>  ST0 <= 1.0
jne  keep                   ; 0x0040d5e2
fstp st(0)
fld  dword [0x005d8568]     ; clamp to 1.0f
keep:
ret
```

Source architecture (not the proof, the match):
`references/Onslaught/BattleEngine.cpp:3142-3150`

```
value = (EVENT_MANAGER.GetTime()
         + GAME.GetFrameRenderFraction()*CLOCK_TICK
         - mStart) / (mFinish - mStart);
if (value > 1.0f) value = 1.0f;
```

Retail has **no** floor at 0. `CLockInfo::Fired`
(`BattleEngine.cpp:3153-3157`) is the already-pinned FireLock
inline: `mStart = mTime; mFinish = mStart + 0.5f`. A just-fired
lock therefore reaches 1.0 after half a second of `mTime` plus the
sub-tick fraction term.

`0x008a9e44` is BSS (not in the 2,506,752-byte image). Existing
notes already treat it as the frame-render fraction
([`player-camera-attach-and-mesh-hfov-2026-07-26.md`](../../player-camera-attach-and-mesh-hfov-2026-07-26.md));
this wake did not re-derive the writer. `0x00672fd0` is the
campaign-closed `mTime`.

HIGH on the 51 bytes, ABI, both inbound sites, the four memory
operands, the `1.0f` clamp polarity, and the source formula match.
Not claimed: the writer of `0x008a9e44`, a floor at 0, or HUD
behavior when `mFinish == mStart` (the `fdivp` is unguarded).

## Lock texture slots (LoadTextures)

`CHud__LoadTextures` `0x00481650`–`0x00481aea` stores each
`0x004f27f0` result into the next slot (MSVC
`call load(A); push B; mov [slotA], eax; call load(B)`). The five
slots this body reads:

| Hud offset | Path VA | Store | String |
| --- | --- | --- | --- |
| `+0x1b0` | `0x0062cf48` | `0x00481a24` | `hud\v3\hud_lock_on_pieces_all.tga` |
| `+0x1b4` | `0x0062cf24` | `0x00481a4d` | `hud\v3\hud_target_lockedon_red.tga` |
| `+0x1c8` | `0x0062cf04` | `0x00481a67` | `hud\v3\hud_lock_on_piece1.tga` |
| `+0x1cc` | `0x0062cee4` | `0x00481a75` | `hud\v3\hud_lock_on_piece2.tga` |
| `+0x1d0` | `0x0062cec4` | `0x00481a9e` | `hud\v3\hud_lock_on_piece3.tga` |

HIGH on the pairing. The Godot HUD README already retains
`target-sighted` and says lock layers “remain absent rather than
being inferred”
(`rebuild/OnslaughtRebuild.Godot/Assets/Hud/README.md`).

## Callers

| Function | Inbound rel32 |
| --- | --- |
| `CHud__RenderOverlayForViewpoint` | 1 — `CHud__Render` `0x00487c57` |
| `CHud__RenderWorldTargetSprites` | 1 — dispatcher `0x00487b6b` |
| `CLockInfo__GetLockPercentage` | 2 — this body `0x00486fd5`, `0x004872b2` |

`CHud__Render` itself has one inbound, `CDXEngine__PostRender`
`0x0053ed01`, matching the 2026-08-12 HUD source-identity
correction (`HUD.Render` first).

## Pinned-source status

`CLockInfo::GetLockPercentage` / `Fired` are in
`references/Onslaught/BattleEngine.cpp:3142-3157`. `CLOCK_TICK`
is `thing.h:29`. No `Hud.cpp` is pinned; dispatcher and
WorldTargetSprites shape authority is the image. No
divergence-from-source on the percentage formula: retail matches
the source expression and the `> 1.0` clamp, and does not add a
floor the source also lacks.

## Field map pinned by these bodies

| Offset | Meaning | Anchor |
| --- | --- | --- |
| hud `+0x50` | BattleEngine* for this viewpoint | store `0x00487b30`; walks add `0x294` / `0x2a4` |
| hud `+0x54` | viewpoint record | store `0x00487b33`; `PushTransformState` |
| hud `+0x58` | viewpoint index | store `0x00487b36` |
| BE `+0x294` | acquiring-lock `CSPtrSet` | walk `0x00486f0a` |
| BE `+0x2a4` | fired-lock `CSPtrSet` | walk `0x004871e3` |
| `CLockInfo+0x04` | `mStart` | getter `0x0040d5c2` |
| `CLockInfo+0x08` | `mFinish` | getter `0x0040d5c5` |
| `0x00672fd0` | `mTime` | getter `0x0040d5bc` |
| `0x008a9e44` | frame-render fraction | getter `0x0040d5b0` |
| `0x005d8578` | `0.05f` = `CLOCK_TICK` | getter `0x0040d5b6` |
| `0x005d8568` | `1.0f` clamp / discriminator | getter + both walks |
| thing `+0x2c` bit 2 | `TF_DYING` early-out | dispatcher `0x004879f4` |

## Rebuild mapping

Nearest reconstruction owner: **none added.** Core has
`SimulationConstants.TicksPerSecond = 20` /
`CLOCK_TICK = 0.05` but no lock-set type and no
`GetLockPercentage`. FireLock’s note already mapped the set move
onto `Simulation.TryFire` as `PARTIAL_CONTRACT` and recorded that
Godot HUD target-lock layers stay absent. This wake adds the
**draw law** those layers would need:

- walk `mLocks` then `mFiredLocks` each overlay pass;
- percentage =
  `(mTime + frameFraction * 0.05 − mStart) / (mFinish − mStart)`,
  clamp at 1, no floor at 0;
- `< 1` draws piece1/2/3; `>= 1` draws pieces_all + lockedon_red;
- do not route lock art through `SelectMarkerTextureIndexByUnitFlags`
  or through `DisplayLock`.

The rebuild-parity lane (`t_d9d4ea2d` on `wt/bea-rebuild-worlds`)
is running; per lane rules no Core / Godot file was edited. The
focused-test step is deferred until that lane (or a HUD owner)
names the arm.

## Cheapest falsifier

Any one of:

- Body SHA-256 mismatch: dispatcher 477 B `59b6a535…12936a9`
  (must end `c2 08 00`); WorldTargetSprites 3031 B
  `60b65892…8b4e3325` (must end `c3`); getter 51 B
  `aa65f863…c16900f2` (must end `c3`).
- `tools/disasm_va.py` on the getter shows a memory operand other
  than `{0x008a9e44, 0x005d8578, 0x00672fd0, [ecx+4], [ecx+8],
  0x005d8568}`, or a clamp test other than `test ah, 0x41`.
- `tools/call_xref_scan.py` on `0x0040d5b0` is not exactly the two
  WorldTargetSprites sites, or on `0x00486e00` is not exactly
  `0x00487b6b`.
- The acquiring walk loses `add ebx, 0x294` or the fired walk
  loses `add ebx, 0x2a4`, or the `< 1.0` arm stops reading
  `hud+0x1c8/1cc/1d0`.
- LoadTextures store `0x00481a24` is no longer preceded by the
  `hud_lock_on_pieces_all.tga` load.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading (2,506,752 B,
  `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`);
  twin
  `local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
  matches. Tools: `tools/disasm_va.py` (getter through `ret`;
  WorldTargetSprites lock walks and Next tails; dispatcher through
  `ret 0x8`; LoadTextures store window), raw byte reads (three body
  hashes; floats `0x005d8568=1.0`, `0x005d8578=0.05`,
  `0x005d85e0=2π`, `0x005d8580=0.001`; `.rdata` HUD path run), and
  `tools/call_xref_scan.py` (counts above). Ghidra was not opened.
- Name-table current symbols (2026-08-17):
  `CHud__RenderWorldTargetSprites` `0x00486e00`–`0x004879d6`,
  `CLockInfo__GetLockPercentage` `0x0040d5b0`–`0x0040d5e2`,
  `CHud__RenderOverlayForViewpoint` `0x004879e0`–`0x00487bbc`,
  `CHud__Render` `0x00487bc0`–`0x00487d0b`.
- W005 A01/B01 remain corroboration for dispatcher `ret 0x8` and
  the WorldTargetSprites “lock-list walk” label; this wake
  re-derived both lock walks and the percentage formula from the
  image, so those contracts are no longer plate-only.
- Does not redo DisplayLock, FireLock, StartLock, LockHit, or
  IScript natives 76–81.
