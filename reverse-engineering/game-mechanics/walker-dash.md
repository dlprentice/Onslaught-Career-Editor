# Walker dash: the retail timing window

Status: active static contract for the rebuild's walker movement
Last updated: 2026-09-27 (complete directional bodies rechecked; slow-movement asymmetry added; earlier frame calculations retain their assumptions)
Summary: a walker dash needs the opposite hard press to have started more than half of
`mDashTime` and less than `mDashTime` before (0.1 to 0.2 s). The pinned source has only the
0.2 s bound. The frame calculation assumes float32 event times and x87 single precision. At 20 event
frames per second it always admits an opposite press 3 frames earlier and never one 1 frame
earlier; one 2 or 4 frames earlier passes only on some frames, decided by rounding.
Evidence: MEASURED — instruction reads of the pristine specimen; SOURCE —
`BattleEngineWalkerPart.cpp`; COMPUTED — the frame table below, from the byte-level predicate.
The audit's research pass found the extra bound; the RE lane re-derived it from the bytes.
There is no runtime capture of a dash, and this pass has not measured the runtime
x87 control word.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## The four gestures

`CPlayer::ReceiveButtonAction` calls one walker-part function per stick direction with the
stick value (`Player.cpp:421-441`). Each function works in two steps:

1. When the stick crosses `mDashStart` in its own direction, it records the event time.
2. When the stick crosses `mDashEnd`, it dashes if the opposite direction's recorded time is
   inside the window.

The event time is copied as a raw float32 dword from `0x00672fd0` (`EVENT_MANAGER` time).

| Function | Body | Call site | Records its time in | Window reads | Source window line |
| --- | --- | --- | --- | --- | --- |
| `Forward` | `0x00412d80-0x00412f66` | `0x004d3317` | `+0x34` (`0x00412de7`) | `+0x38` (`0x00412e1f`) | 140 |
| `Backward` | `0x00412f70-0x00413156` | `0x004d332c` | `+0x38` (`0x00412fd5`) | `+0x34` (`0x00413009`) | 186 |
| `StrafeLeft` | `0x00413160-0x0041335f` | `0x004d3341` | `+0x30` (`0x004131cb`) | `+0x2c` (`0x00413203`) | 236 |
| `StrafeRight` | `0x00413360-0x004135c1` | `0x004d3366` | `+0x2c` (`0x004133c9`) | `+0x30` (`0x004133fd`) | 290 |

The tuning statics keep the source's initial values (`BattleEngineWalkerPart.cpp:30-35`). In
the pristine `.data` they are:

| Static | Address | Value |
| --- | --- | --- |
| `mDashTime` | `0x006236ac` | 0.2f |
| `mDashStart` | `0x006236b0` | 0.9f |
| `mDashEnd` | `0x006236b4` | 0.8f |
| `mDashLength` | `0x006236b8` | 15 |
| `mDashFriction` | `0x006236bc` | 5 |
| `mDashVelocity` | `0x006236c0` | 25.0f |

## The window

All four functions compile the window the same way. In `StrafeLeft`:

```
0x00413203  fld   [esi+0x2c]          ; last = opposite hard-press time
0x00413206  fld   [0x00672fd0]        ; now
0x0041320c  fsub  [0x006236ac]        ; now - mDashTime
0x00413212  fld   st(1)
0x00413214  fcompp                    ; last against now - mDashTime
0x0041321b  jne   0x004132c8          ; last <= now - mDashTime: no dash
0x00413221  fld   [0x006236ac]
0x00413227  fmul  [0x005d85ec]        ; 0.5f
0x0041322d  fsubr [0x00672fd0]        ; now - 0.5 * mDashTime
0x00413233  fxch  st(1)
0x00413235  fcompp
0x0041323c  je    0x004132ca          ; last >= now - 0.5 * mDashTime: no dash
```

The same pair of tests appears in the other three functions:

| Function | First test | Second test |
| --- | --- | --- |
| `Forward` | `0x00412e1f-0x00412e37` | `0x00412e3d-0x00412e58` |
| `Backward` | `0x00413009-0x00413021` | `0x00413027-0x00413042` |
| `StrafeRight` | `0x004133fd-0x00413415` | `0x0041341b-0x00413436` |

So a dash needs:

    now - mDashTime  <  last  <  now - 0.5 * mDashTime

The source has only the left inequality (`if (mLastStartHard…Time > (EVENT_MANAGER.GetTime() -
mDashTime))`, lines 140, 186, 236 and 290). The right inequality is retail-only.

**Precision assumption.** With x87 single precision, the two differences are rounded to
float32 before the comparison. The retail control word at input dispatch has not been
captured; the expected precision below is an inference from device setup. Direct3D sets
the x87 to single precision on `CreateDevice` unless `D3DCREATE_FPU_PRESERVE` (`0x2`) is passed.
Retail never passes it:

- The device is created at `0x0052b2d6` (`IDirect3D9` vtable `+0x40`). Its flags are
  `[esi+0xc]`, optionally ORed with `0x100`.
- The behaviour table the device enumeration builds (`0x00529c21`, `0x00529cf8`,
  `0x00529dd2`, `0x00529ea9`) holds only `0x50`, `0x40`, `0x80` and `0x20`. None of them has
  bit `0x2`.
- The source adds `FPU_PRESERVE` only under `_DEBUG` (`d3dapp.cpp:338-340`).

The event time itself is `fl32(frame × 0.05f)` (`CEventManager.cpp.md`, `0x0044b600`) and does
not depend on the precision mode: the product fits in 48 bits, so it is rounded once. As a C#
predicate, with explicit casts to keep each difference in float32:

```csharp
static float EventTime(int frame) => (float)(frame * (double)0.05f);
static bool DashWindow(int nowFrame, int lastFrame)
{
    float now = EventTime(nowFrame), last = EventTime(lastFrame);
    return last > (float)(now - 0.2f) && last < (float)(now - 0.1f);   // 0.5f * 0.2f == 0.1f
}
```

## What that means per frame

Let `k` be the number of event frames between the opposite hard press and the dash press. This
counts one input sample per event frame.

| `k` | Retail, single precision | Pinned source | Rebuild on 2026-09-26 (`Simulation.cs:2366`, `hardMoveTick > tick - 4`) |
| --- | --- | --- | --- |
| 0, 1 | never | always | always (k = 1) |
| 2 | some frames: 10.5 % of the first 10 minutes, 12.1 % of the first hour; the first are 3, 6, 9, 21 and 42 | always | always |
| 3 | always | always | always |
| 4 | some frames: 22.3 % of the first 10 minutes, 6.1 % of the first hour; the first are 5, 7, 25, 28 and 30 | the same frames as retail | never |
| 5+ | never | never | never |

The numbers are computed by applying the predicate to every frame `n` (the dash press) with
`last = EventTime(n - k)`:

```python
import numpy as np
f32 = np.float32
n = np.arange(72000); t = (n * np.float64(f32(0.05))).astype(f32)
def dash(k):
    now = t[k:].astype(np.float64); last = t[:-k]
    return (last > (now - np.float64(f32(0.2))).astype(f32)) & \
           (last < (now - np.float64(f32(0.1))).astype(f32))
```

If the difference were not rounded (extended precision), k = 2 would pass on 46 % of the first
hour and k = 4 on 62 %. The precision mode decides only those two rows.

## Roll on a strafe dash

The two strafe dashes are asymmetric, as in the source:

- `StrafeLeft` stores `mRollvel = +0.08` (`mov [edx+0x27c], 0x3da3d70a` at `0x004132b4`;
  source line 246, `mRollvel=+DASH_BOOST_ROLL`).
- `StrafeRight` subtracts: `fld [eax+0x27c]; fsub [0x005d8ccc] (0.08f); fstp [eax+0x27c]` at
  `0x004134ae-0x004134ba` (line 300).

The September 26 review reported this in the rebuild (`Simulation.cs:2349-2359`);
that implementation was not rerun by the September 27 RE pass.

## September 27 complete-body recheck

All four complete bodies and the Player caller were freshly decoded from the
pristine specimen above. They retain the two-sided timing window and asymmetric
roll writes. Constructor `00412bc0` binds the six `g_dash_*` registrations, while
the main initializer calls it at `00404faa` and stores its result at main `+0x578`.
This establishes the walker receiver independently of the saved names.

The three bodies Forward, Backward and StrafeLeft test main `+0x588` and multiply
all final movement-vector components by float `0.25` when nonzero. Their scaling
blocks start at `00412f22`, `00413112` and `0041331b`. The complete StrafeRight body
has **no corresponding flag read or scaling**; it reaches AddVelocity at
`004135b8` directly after forming the vector. This agrees with pinned source
lines 310–313: that branch changes the earlier scalar after constructing `move`,
then submits the unchanged vector. Preserve the asymmetry in a faithful rebuild.

Body SHA-256 values, in table order above:
`a1700e98ef7cac1fb13a7a2542e144dc2a0f2016d6a9f2670a91ca56c38312d2`,
`09f9c5709ff76e8956626a77c120dd906efb4e22aef93934b4efcbaabd75296e`,
`f73bf900aff3f6b19d141656b8432f72a385d3fc58b2e7c3cd2305058deaf206`,
`9872c30a8763e6aef8c5975c0055e934fe7ec4afeaab61e94da468ad9e1d918e`.
Private bodies/constants and complete caller witnesses are in
`local-data/test-runs/re-audit-20260926/walker/identity-leads-v2.json` and
`callers-v1.json`. The packet's candidate labels alone are not identity proof.
These are static findings, not a new dash/input experiment. The earlier frame
percentages were not recomputed by this pass.

## Rotation and pitch use the yaw-right binding

Fresh complete-body inspection also identifies `00413660` and `004136e0` as
the source's Rotate and Pitch (`BattleEngineWalkerPart.cpp:347–355`), called
through the walker receiver at `004d337b` and `004d3390`. Their stack arguments
are consumed as floating-point operands, not converted from integers.

Both read the category at `0x008892f8 + 0x0c + 0x0c * (playerNumber - 1)`.
This is the selected player's slot in the **yaw-right action binding**, not
a weapon class. Initializer `00514233` supplies action 27 and default category
13 to receiver `008892f8`; `0042d271` stores the category at `+0x0c`.
The separate binding writer `004565f7` confirms the 12-byte slot stride.
Player construction stores its incoming number at `004d27b6`; assignment
publishes the player through the engine's `+0x574` monitored reference.

Categories 11 and 12 select float bits `3fd9999a` (approximately 1.7); every
other category selects `3f800000` (1.0). The input mapper's table at `0042e340`
sends categories 11/12 to `0042e04b`, which consumes mouse coordinates written
by the `0x200` message handler at `00523548/0052355c`. Categories 13/14 reach
that coordinate path through an extra gate, but **do not** select the 1.7
multiplier. Exact retail enum symbols are absent from the pinned header.
Pitch also reads this same yaw-right record; substituting its own pitch binding
would change the retail rule. The partial source lacks the multiplier.
The resulting writes are yaw velocity at main `+0x278` and pitch velocity at
main `+0x280`, rather than direct orientation-angle changes. The action and
category numbers in this section are decimal.

Root independently decoded and checked all nine bodies in the private
`local-data/test-runs/re-audit-20260926/walker/control-binding-bodies-v1.json`
packet, SHA-256
`43f43da67b4e7073634c3de610a4b1aa61ec2c475451607c1d52c929fc43e9f5`.
This establishes static ownership and selection, not the category chosen by
current user settings or actual input sensitivity in a running game.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| Whether the game thread runs at single precision during play | In a copied runtime, break at `0x00413235` and read the x87 control word: precision bits 8-9 should be `00` |
| Whether one input sample reaches the walker per event frame | Count `CPlayer::ReceiveButtonAction` calls per `CEventManager::AdvanceTime` in a copied runtime, holding the stick steady; more than one per frame adds a `k = 0` case, which retail rejects |
| Whether a dash two frames after the opposite press follows the frame table | A two-frame left-right flick ending on a frame the table admits (for example frame 21) and on one it rejects (frame 20), with the walker's `+0x44` dash count logged |
| Effect of slow movement on all four directions | Run the original directional bodies on copies with identical finite inputs, yaw and velocity, toggling main `+0x588`; intercept AddVelocity and compare submitted vectors |
| Effect of the yaw-right binding category on rotation and pitch | Execute both original bodies on copied valid receivers with identical finite input, varying that binding between categories 11, 12, 13 and 14; compare the yaw/pitch velocity writes while preserving x87 state |
