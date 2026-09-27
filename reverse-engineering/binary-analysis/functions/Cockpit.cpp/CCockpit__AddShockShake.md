# CCockpit__AddShockShake

Status: active, bounded instruction and original-code contract
Last updated: 2026-09-26
Summary: one float argument, four CRT random draws and an unclamped fourth component; the saved integer parameter has been corrected.
Evidence: MEASURED — complete pristine body, caller and 41-case composed original-code experiment; no full-game/rendered acceptance.
Source File: no cockpit implementation in pinned GPL source; caller `references/Onslaught/BattleEngine.cpp:1112` at commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` | Binary: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004247a0`

## Identity and interface correction

Complete body `[0x004247a0,0x0042491a)`, 378 bytes, SHA-256
`5a7885d9a3ee6f5ac76dc8bc1f8a6760f39bc3f406b43c33a1c3e25cb872d98b`.
The September 26 label audit replaced the false CGeneralVolume owner with
`CCockpit__AddShockShake`. Its former `int randomRange` parameter was wrong:
`FDIV` at `0x004247a9` reads entry stack +4 as binary32. The caller at
`0x00407a1d–0x00407a22` pushes the engine's already-clamped float bits.
The interface is `void __thiscall(this, float amount)`, one explicit argument
and `RET 4`. The [promoted ABI cohort](../../../ghidra/README.md#re-audit-cockpit-shake-abi--september-26)
preserves the stack slot, automatic receiver, void return, locals and body.
Independent readback and restored Archive A POST recovery passed; no extra
parameter was introduced.

## Body-derived behavior

For the positive finite inputs admitted by the engine caller:

- Store `d = float32(128 / amount)` and `h = float32(amount × 0.5)`.
- Three CRT rand draws replace `+0x90/+0x94/+0x98` with
  `float32((draw % 128) / d − h)`.
- A fourth draw replaces `+0x9c` with `float32((draw % 32) / d − h)`. The `+0xa0` clear at `0x0042484c`
  precedes that fourth component store at `0x0042486c`.
- Clamp **only the first three** components to ±binary32 `0.01`.
  The fourth remains unclamped. All components are replacements, not additions.

This routine has no copy of the engine's threshold/clamp. Its argument is
bounded by that caller; direct invalid/zero/unordered calls were not executed.
The pinned source drop contains no cockpit body, so the numerical contract
comes from retail instructions, not presumed source equivalence.

CRT rand `[0x0055dbfe,0x0055dc20)` is 34 bytes, SHA-256
`d617aecff4c221d4523adb768f37b1c95cf7205dd9e2f0a4bb30dc5e1b5821ee`.
It obtains thread data through `0x00560b93`, updates DWORD `+0x14` as
`seed = seed × 214013 + 2531011 (mod 2^32)`, then returns
`(seed >> 16) & 0x7fff`. This is separate from the engine's gameplay RNG.

## Executed evidence and limits

The [shared Damage experiment](../BattleEngine.cpp/CBattleEngine__Damage.md)
runs the complete unchanged engine/cockpit/game-RNG/CRT-rand bodies. Its
thread-data provider is an explicit authored substitute, not Windows TLS.
With CRT seed 1, four provider entries produce draws
`41, 18467, 6334, 26500` and final seed `0xe7847115`.
For amount `0.25`, the fourth component is exactly `-0.1171875`, disproving
an all-components ±0.01 clamp. The first three are binary32 `-0.01`,
binary32 `-0.01` and exact `-0.00390625`. Null cockpit and rejected engine-shake
cases preserve that CRT seed, while accepted engine shakes advance their own
seed independently.

Private receipt: `local-data/test-runs/re-audit-20260926/battleengine-damage/run-iekrvvq7/damage.json`,
SHA-256 `f6a2aab65ef85d1558332a3a3605845cd786a7c1c8949149dac52e9b2a6c130d`.
Names of the fields, their downstream units, complete cockpit layout and the
rendered effect remain open. A consumer-composed execution followed by a
controlled copied-retail capture is the remaining falsifier. No physical
screen/input, Godot or full-game process was used for these checks.
