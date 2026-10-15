# `CUnit` primary virtual interface: demo/retail semantic crosswalk

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — strict retail/demo RTTI and vtables, gapless decoded
function bodies, direct callers, constants, and dataflow; SOURCE — pinned
`CThing` and `CBattleEngine` declarations and implementations; UNKNOWN — the
historical names explicitly left open in the TSV.
Verdict: the 64-target `CUnit` owner block is independently stable across the
PC demo and retail builds, and 21 inherited or added virtual meanings now have
source- or source-callsite names. The remaining slots retain behavioral names
instead of guessed historical symbols.
Specimen: pristine Steam `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`

## Result

Strict RTTI pairs retail `CUnit` primary vtable `0x005DF998` with demo
`0x005E0998`. Their complete-object locators are `0x00617050` and
`0x00618050`; the structural key is
`dd6dba0aad78846cc82ff20a1a30e59f807ce37a7da8c7e77bb5fc8c9584199c`.
The primary table retains inherited slots 0–70 and adds 46 `CUnit` slots,
71–116. Those 46 entries resolve to 42 distinct retail code targets because
MSVC folded several identical no-op/constant bodies.

Across the broader virtual-target census, `semantic_owner=CUnit` selects 64
distinct targets containing 16,492 retail body bytes and 5,087 decoded
instructions. Forty targets have 447 raw-different instructions in the demo,
but every one of the 64 pairs has zero differences after encoded
address/displacement normalization. This is independent build corroboration
of their instruction, branch, register, and literal shape—not proof that the
demo and retail exercised every path identically.

The complete 46-slot result is machine-readable in
[`cunit-primary-vtable-semantics-2026-08-11.tsv`](cunit-primary-vtable-semantics-2026-08-11.tsv).
That 8,562-byte table has SHA-256
`b3ac3554e9db634b6ddeec1d48c60f2d2098338afd628d7b5b1e5b6b2b8dd802`.
The full 2,127-target comparison remains in
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Source-named joins

The following names no longer depend on field-offset prose or a decompiler
guess:

| Slot | Retail target | Recovered meaning | Joining evidence |
| ---: | --- | --- | --- |
| 15 | `0x004F84B0` | `CUnit::GetMaxVelocity` | Pinned `CThing` virtual order; body returns exact `0.2f` |
| 43 | `0x00417610` | `CUnit::GetSoundMaterial` | Pinned inherited slot; body returns unit-data field `+0xE4` |
| 46 | `0x004FDC90` | `CUnit::ObeyGravity` | Pinned inherited slot; body tests the retained unit mode |
| 47 | `0x00417620` | `CUnit::BounceFactor` | Pinned inherited slot; body returns unit-data field `+0x154` |
| 53 | `0x00405E50` | `CUnit::GetAIState` | Pinned inherited slot; body returns field `+0x210` |
| 54 | `0x004FDCB0` | `CUnit::SetAIState` | Pinned inherited slot; body stores the state and clears the target reader when required |
| 55 | `0x004FDC20` | `CUnit::AccumulateScore` | Pinned inherited slot and spawn/count accounting body |
| 56 | `0x00405E30` | `CUnit::SetVulnerable` | Pinned inherited slot; exact field `+0x15C` setter |
| 57 | `0x00405E40` | `CUnit::GetVulnerable` | Pinned inherited slot; exact field `+0x15C` getter |
| 58 | `0x004F9220` | `CUnit::IncreaseThingCounter` | Pinned inherited slot and nested-init traversal |
| 75 | `0x004FC3C0` | `CUnit::GetLaunchPosition` | `CBattleEngine` slot-75 override `0x0040C990` matches pinned source signature and body |
| 79 | `0x004175C0` | `CUnit::GetThreat` | `CBattleEngine` override `0x0040E8E0` matches the source terrain-height/`2.0f`/`5.0f` law |
| 80 | `0x004175D0` | `CUnit::GetImportance` | `CBattleEngine` override `0x0040E910` matches the source on-ground/not-on-object law |
| 81 | `0x004175E0` | `CUnit::GetCurrentTarget` | `CBattleEngine` override `0x004071B0` occupies the exact pinned source slot |
| 85 | `0x00417600` | `CUnit::SetInfinateEnergy` | Pinned source spelling; `0x00405F20` stores the flag and refills Battle Engine energy |
| 90 | `0x004FD4D0` | `CUnit::GetTargetablePos` | Both pinned auto-aim routines call slot 90 with an output vector; the body selects its cached target point or centre position |
| 91 | `0x004BFC60` | `CUnit::GetStealth` | Pinned lock/auto-aim source uses this slot in `1.0f - stealth/100.0f`; Battle Engine override `0x00405F50` returns its stealth field |
| 102 | `0x004FE2B0` | `CUnit::EnableWeapon` | Battle Engine override `0x0040DC30` forwards the name to walker and jet parts exactly as pinned source |
| 103 | `0x004FE310` | `CUnit::DisableWeapon` | Battle Engine override `0x0040DC60` forwards the name to walker and jet parts exactly as pinned source |
| 104 | `0x00417630` | `CUnit::CanBeLocked` | Battle Engine override `0x0040E7D0` exactly reproduces source stealth, jet-loop/roll, and walker-special gates |
| 105 | `0x004014A0` | `CUnit::OnScanner` | Pinned `HandleAutoAim` halves range only when this slot returns false |

The old current label `CUnit__SelectTarget` at `0x004FD4D0` is therefore
incorrect: the ABI and both source callsites establish `GetTargetablePos`.
Likewise, the anonymous field getters at `0x004175C0`, `0x004175D0`,
`0x004175E0`, `0x00417600`, and `0x00417630` now have class-interface
meanings rather than mere offsets.

## Why several addresses must not receive one global semantic name

MSVC identical-code folding reuses the same target for unrelated virtual
contracts. For example, `0x004BFC60` is the zero-float implementation of
`CUnit::GetStealth` at slot 91, but other classes and other slots also point at
that body. Similarly, `0x004014A0` implements `CUnit::OnScanner` at slot 105
and multiple unrelated constant-true virtuals elsewhere. The semantic truth
therefore belongs to `(class, primary-vtable, slot)`, not to the code address
alone. Renaming either shared address globally to the CUnit meaning would make
other classes less correct.

This also explains a misleading decompiler rendering in
`CBattleEngine::HandleAutoAim`: the call at `0x0040BBBC` uses weapon virtual
slot 71 (`CanPredict` in the pinned source), not CUnit slot 71. Register tracing
shows `ESI` holds the current weapon from Battle Engine slot 117. Treating all
`+0x11C` calls as one class interface would have assigned an impossible
zero-argument meaning to CUnit's `RET 8` stub.

## Boundary and next use

The absent `Unit.h`/`Unit.cpp` means a body-stable demo twin cannot supply
historical names by itself. Slots marked `OPEN_NAME` or `STATIC_DESCRIPTIVE`
remain bounded behavior contracts. They are not promoted to invented source
symbols, and this report does not claim runtime coverage or rebuild parity.

The useful next step is recursive: use the recovered slot meanings to name
their subclass overrides and callers, then use those named call chains to
resolve the remaining deploy, spawn, support, and movement slots. This avoids
both extremes—leaving the functions as anonymous offsets and pretending a
plausible name is proof.
