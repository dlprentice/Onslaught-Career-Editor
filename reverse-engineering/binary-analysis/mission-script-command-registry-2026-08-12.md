# The Mission script-command registry, recovered from shipped data

Status: active, bounded static registry recovery
Last updated: 2026-08-12
Evidence: MEASURED — abstract interpretation of the stores in
`ScriptCommandRegistry__InitBuiltins` against the pristine specimen,
reconstructing the record array at `0x0064CE20` and reading its name/handler
pairs, joined to the current tracked Ghidra name projection; UNKNOWN — every
handler signature, argument contract, side effect and runtime behaviour, none of
which this recovery addresses.
Verdict: 144 script commands are paired with handler addresses by the game's own
data. 110 handlers resolve to known function entries and 54 of those functions
still carry default names, so the registry supplies a shipped-data name for 54
currently unnamed functions. No name was promoted to Ghidra.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Prior art — corrected 2026-08-12, this recovery was less novel than first written

**This document originally presented the registry as a new recovery. That was
wrong, and the error was mine.** The registry was already tracked:

- [`ghidra-functions.md`](../ghidra-functions.md) carries
  **Appendix A: complete 144-entry MissionScript native registry**, with 144
  numbered rows already naming `GetRealHealth`, `GetInitialHealth`,
  `SpawnersEmpty`, `EnableWeapon` and `SetSpeed`.
- [`functions/IScript.cpp.md`](functions/IScript.cpp.md) already states that
  `ScriptCommandRegistry__InitBuiltins` initialises 144 contiguous `0x40`-byte
  descriptor slots at base `0x0064CE20`, already binds the `Pause` row to
  `0x00537C70` from direct stores, and already declines to promote that name.

I checked `local-lab/msl/natives.json` for prior art and found it, but did not
check the tracked corpus before writing — even though `ghidra-functions.md` is on
the required intake reading list. Commit messages `14787909` and `43fb041a`
overstate novelty for the same reason.

What this document still contributes, and what the earlier work did not have:

- the handler pointers **resolved against the current name table**, which is what
  identifies the 54 slots whose handlers still carry default names;
- the refutation and alignment checks below;
- the 23-row adjudication, which finds that five handlers documented as
  `IScript__PlaySound*` in `functions/IScript.cpp.md` queue messages and play no
  sound.

Read the structure section below as reproduction and extension of tracked
evidence, not as first recovery.

## Structure

`ScriptCommandRegistry__InitBuiltins @ 0x0052FF30` (13,429 bytes) populates a
record array at `0x0064CE20` using `mov [absolute], reg` and
`mov [absolute], imm` stores, holding shared constants in registers across long
runs. Interpreting those stores abstractly — tracking `mov reg, imm`,
`xor reg, reg`, and clearing on `call` — reconstructs the table with **zero
stores left on an untracked register**.

| Property | Value |
| --- | --- |
| Record stride | `0x40` |
| Command-name pointer | record `+0x00` |
| Handler function pointer | record `+0x30` |
| Records recovered | 144, terminating cleanly at index 144 |
| Handlers resolving to a known function entry | 110 |
| Handlers on still-default `FUN_` names | 54 |
| Handlers on the shared no-op | 1 |

The 144 count independently matches the 144-slot native table reached from the
opposite direction by the compiled-script work, which indexes this table with a
`CALL` operand masked to `& 0xff`.

## Two independent channels agree on three names

The same day, the
[PC-native source-coordinate instrument](pc-native-source-coordinates-2026-08-12.md)
singled out `0x005359D0`, `0x00535A30` and `0x00535A90` as unnamed functions
carrying exact `IScript.cpp` coordinates at lines 1158, 1173 and 1188. The
registry assigns those same three handlers the commands `GetRealHealth`,
`GetInitialHealth` and `SpawnersEmpty`.

Unlike the PC/Xbox coordinate pair — which share a signal and must not be cited
as mutual corroboration — these two channels are genuinely independent: one reads
debug-allocator arguments, the other reads a registrar's stores.

## Refutation, and why the 54 names are not cleared for promotion

Three checks were run before any promotion was contemplated.

**Independent implementation — passed, 143/143.** A prior lane's read of the same
table, by a different author and method, agrees on every index/name pair. It
shares this recovery's source so it is not independent evidence, but it validates
the stride and name-offset arithmetic.

**Table alignment — passed.** This is the check able to detect a wrong base or
stride. Commands `GetX`, `GetY`, `GetZ` occupy consecutive indices 57, 58, 59 and
land in exact order on `IScript__GetVectorX`, `IScript__GetVectorY`,
`IScript__GetVectorZ`; `SetX`, `SetY`, `SetZ` occupy 60, 61, 62. An off-by-N
stride or wrong base would scatter or reverse those families. It does neither.

**Agreement with pre-existing names — 55 testable, 32 agree, 23 disagree.** Most
of the 23 are cases where the existing Ghidra name is a descriptive placeholder
and the registry supplies the game's actual command:
`IScript__SetThingValueViaVFunc198_FromArg` is registered as `EnableWeapon`,
`IScript__CheckValueInRange` as `IsNumberBetween`, `IScript__GetVectorLength` as
`Magnitude`. Superseding those is what this registry is for. That count therefore
does not by itself indicate an extraction error — but it does mean **23 existing
names require per-row adjudication before anything is promoted**, because each is
either a name the registry should supersede or a sign that one of the two is
wrong.

The sharpest is `GetVariable` against `IScript__GetWorldTextSlotTimerValue`. The
same `WorldTextSlotTimerValue` reading is the heaviest callee of the HUD route's
target 0, so if the script-facing name is really `GetVariable`, either that
reading is too specific or the underlying world routine is a generic slot
accessor serving both. Unresolved.

**Posture: the recovered pairing is validated; the naming promotion is not
cleared.** It waits on those adjudications and on the full Ghidra gate.

## The 23 adjudications, resolved

They fall into three classes, and only one is a rename candidate.

**Class 1 — the existing name is the real C++ identity; do not rename (2).**
Indices 114 and 115 are registered `Goto3PointPanCamera` and
`Goto4PointPanCamera`, while Ghidra calls them `IScript__Create3PointPanCamera`
and `IScript__Create4PointPanCamera`. Their bodies carry the shipped strings
`FATAL ERROR: null thing passed to 'Create3PointPanCamera'` and its 4-point
counterpart. The game's own error text names the C++ function `Create…`; the
registry names the script command `Goto…`. Both are right about different things,
and adopting the registry string here would destroy a shipped-symbol identity.
This proves from the binary — not from caution — that a registry string is a
script-facing command name rather than a C++ symbol.

> **Class 2 CORRECTED 2026-08-12, later the same day — my claim was too strong.**
> This section originally asserted that these five handlers "play no sound". That
> is **false**, and one more level of call-graph would have shown it. The queued
> message does reach audio:
> `Insert…SortedAndMaybeAdvance` → `CMessageBox__VFunc_0_004B81D0` →
> `CMessageBox__StartVoiceOrFallbackTextReveal` → `CText__GetAudioNameById` and
> `CBinkOpenThread__StartAsync`. A message carries a voice line and the message
> box starts it when the queue advances, so `PlaySound` is a defensible
> description of the **effect**.
>
> What survives is narrower and still worth fixing: the **suffixes are wrong**.
> `WithCallback`, `WithFade` and `WithPriority` name mechanisms that are not
> there. The registry's actual distinctions are `AddMessage` versus
> `PlayCharMessage` versus `PlayPCharMessage`, and plain versus `Wait` — and the
> `Wait` variants are the two that schedule through
> `CEventManager__GetNextFreeEvent` and `CScheduledEvent__Set`, which is exactly
> the behaviour `WithFade` was invented to describe.
>
> Read the paragraph below as evidence about the immediate call layer only.
> `CUnit__ApplyDamage` and `CUnit__TriggerEffect` also insert queued messages, so
> the queue is not script-only.

**Class 2 — the existing name's suffix is wrong about mechanism (5).** Five
handlers named `IScript__PlaySound*` call no sound routine directly. Their
callees are
`CText__GetStringById`, `CMessage__ctor_base` and
`CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`: they build a localized
message and queue it. The two `…Wait` variants add
`CEventManager__GetNextFreeEvent` and `CScheduledEvent__Set`.

| Idx | Registry command | Current Ghidra name |
| ---: | --- | --- |
| 17 | `AddMessage` | `IScript__PlaySound` |
| 28 | `PlayCharMessage` | `IScript__PlaySoundWithCallback` |
| 36 | `PlayCharMessageWait` | `IScript__PlaySoundWithFade` |
| 90 | `PlayPCharMessage` | `IScript__PlaySoundWithPriority` |
| 91 | `PlayPCharMessageWait` | `IScript__PlaySoundWithFadeAndPriority` |

`WithCallback`, `WithFade` and `WithPriority` describe a mechanism that is not in
these bodies. This is a defect in the canonical database of the same class the
HUD source-identity correction fixed, and it holds independently of whether the
registry names are adopted.

**Class 3 — descriptive placeholder the registry supersedes (16).** `GetX/GetY/
GetZ` over `GetVectorX/Y/Z`, `Magnitude` over `GetVectorLength`,
`IsNumberBetween` over `CheckValueInRange`, `EnableWeapon`/`DisableWeapon` over
`SetThingValueViaVFunc198/19C_FromArg`, and similar. `GetVariable` wraps
`CWorld__GetWorldTextSlotTimerValue`, so only the wrapper is at issue and the
callee keeps its name.

Consequently a blanket adoption of all 54 registry names would have been wrong.
Promotion must be per-row and must keep the two naming systems distinct.

## A named dormant capability

Exactly one handler is the shared no-op, and its command is **`SetSpeed`**. The
mission language can call it, and this build accepts the call and does nothing.
The cheapest falsifier is a mission script that calls `SetSpeed` and observes no
effect.

## Boundary

A registry string is the **script-facing command name for that slot**. It is not
a recovered C++ symbol, and mapping it onto the existing `IScript__<Command>`
convention would be a well-supported naming choice rather than a proven identity.
This recovery establishes no handler signature, argument contract, write set,
failure behaviour or runtime semantics; the Generation 15/16/19 work on `SetPos`
and `UnsetObjective` shows what a real contract for one of these costs.

34 of the 144 handlers did not resolve to a known function entry, and whether
those are unrecovered boundaries or non-entry targets is untested here.

**No Ghidra mutation was made and none is authorised by this report.** Promoting
any of these names requires the full gate in
[`reverse-engineering/ghidra/README.md`](../ghidra/README.md). The mechanical
owner and its receipts are machine-local under
`local-lab/mission-native-registry-20260812-v1/`; the recovered pairing is
[`mission-script-command-registry-2026-08-12.tsv`](mission-script-command-registry-2026-08-12.tsv).
