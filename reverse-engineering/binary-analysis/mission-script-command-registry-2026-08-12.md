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
>
> **WITHDRAWN, same day — the refinement below is wrong; read this first.**
> The paragraph beneath claims `[vtable+0x30]` carries a parameter that
> `PlayPCharMessage` takes from the script and the others fix at ten. That is a
> misreading. `[vtable+0x30]` is a **no-argument getter on a boxed script value**:
> `PlayCharMessage` does `mov ecx,[esi]; mov eax,[ecx]; call [eax+0x30]` at
> `0x00537539` and again at `0x0053754E` for `[esi+4]`, unboxing each script
> argument before passing it to `CText__GetStringById`; `[esi+8]` uses a different
> getter at `[vtable+0x34]`. The `push 0xa` is a literal argument to
> `CMessage__ctor_base` itself.
>
> The error was method, not arithmetic: I printed the eleven instructions
> preceding the constructor call and read them as that call's argument setup, when
> they spanned several unrelated calls. **Do not attribute pushes to a call
> without checking where the preceding call boundaries are.**
>
> So `WithPriority` is **not** rehabilitated — it is back to unsupported, along
> with `WithCallback`, and `WithFade` remains wrong. What actually distinguishes
> the five is still unestablished, and identifying it needs the
> `CMessage__ctor_base` signature rather than any inference from call windows.
>
> **Superseded refinement, retained so the reasoning chain is visible:**
> Comparing the argument setup at each `CMessage__ctor_base` call site:
> `AddMessage` passes a fixed global `0x0089C328` where the two `…CharMessage`
> forms pass a script-supplied value, so `AddMessage` is the fixed-source form.
> More usefully, the virtual at `[vtable+0x30]` that builds the message text takes
> a parameter which `AddMessage` and `PlayCharMessage` **hardcode to `0xA`** and
> which `PlayPCharMessage` takes **from the script**. So the `P` prefix marks a
> script-supplied value for something the others fix at ten — and *priority* is a
> natural reading of that, which means `IScript__PlaySoundWithPriority` may be
> **accurate about the mechanism** even though the registry calls the command
> `PlayPCharMessage`.
>
> Status of the five suffixes on current evidence: `WithFade` is **wrong** — the
> two variants it names are the `Wait` forms that schedule through
> `CEventManager__GetNextFreeEvent`. `WithCallback` remains **unsupported** —
> nothing in `PlayCharMessage` registers a callback. `WithPriority` is
> **plausibly right**. That is a smaller correction than the one this section
> originally claimed, and the parameter at `[vtable+0x30]` should be identified
> before any of the five is renamed.

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

### `CMessage__ctor_base` recovered — and it settles the voice question

`0x004B6E50`, 191 bytes, `ret 0x1c` — **seven stack arguments** plus `this`.
Each is stored to a fixed field, and two are decisive:

| Arg slot | Stored to | Role |
| --- | --- | --- |
| `[esp+0x24]` | `this+0x18` | — |
| `[esp+0x28]` | `this+0x0C` | **the wide message text** — also passed to `WcsLen` |
| `[esp+0x2C]` | `this+0x10` | — |
| `[esp+0x30]` | `this+0x20` | — |
| `[esp+0x34]` | — | **optional audio reader**: if non-zero, `CGenericActiveReader__SetReader` runs and `this+0x38` is set to 1 |
| `[esp+0x38]` | `this+0x28` | — |
| `[esp+0x3C]` | `this+0x2C` | — |

Two facts follow, and unlike the three withdrawn readings above these rest on
stores rather than on inferred call windows:

1. **A message carries an optional voice stream directly.** Argument five is a
   reader handle; when supplied, the constructor installs it and raises a
   has-voice flag at `this+0x38`. This is the concrete mechanism behind the
   corrected Class 2 note — the audio is attached at construction, not looked up
   later.
2. **Display duration is computed from text length.**
   `this+0x14 = WcsLen(text) * [0x005DC6AC] + [0x005D8604]` — a linear reveal
   time. Those two shipped floats are the cheapest next measurement.

Mapping which slots each native fills was then attempted with call boundaries
honoured — each intervening `call` consuming its own callee-popped pushes, named
callees giving an exact count from their `ret imm`. It reaches **three of the
seven** before hitting an indirect virtual call whose consumption cannot be
resolved, and stops there rather than guessing:

| Native | Ctor args 1–3 |
| --- | --- |
| `AddMessage` | **`0x0089C328`**, `ebx`, `eax` |
| `PlayCharMessage` | `ebx`, `ebp`, `eax` |
| `PlayPCharMessage` | `ebx`, `ebp`, `eax` |
| `PlayCharMessageWait` | `ecx`, `eax`, `eax` |
| `PlayPCharMessageWait` | `ecx`, `eax`, `eax` |

Three things follow. `AddMessage` alone passes a **fixed global** as argument
one where every `…CharMessage` form passes a register — the clearest structural
distinction found so far. The plain and `Wait` forms have visibly different
argument shapes. And **`Char` and `PChar` are indistinguishable across all three
resolved arguments**, which independently supports withdrawing `WithPriority`:
whatever separates them lies in arguments four to seven, unreached.

That partial map was the state until the indirect targets were resolved rather
than assumed. Reading the boxed-value vtables directly:

| Vtable | Installs in IScript.cpp | Slot `+0x30` | Arity |
| --- | ---: | --- | --- |
| `0x005E4EA4` | 15× | `CFloatDataType__VFunc_12_0052F290` | `ret 0` |
| `0x005E4D50` | 12× | `SharedVFunc__ReturnZero_00405930` | `ret 0` |
| `0x005E4B4C` | 8× | `SharedVFunc__ReturnZero_00405930` | `ret 0` |
| `0x005E4DF8` | 7× | `SharedVFunc__ReturnZero_00405930` | `ret 0` |
| `0x005E4AF8` | 5× | `SharedVFunc__ReturnField04_0052F540` | `ret 0` |

**Every one takes zero stack arguments**, so the indirect `call [reg+0x30]` that
halted the walk consumes nothing and the backward scan can safely pass it. The
blocker was arity, and the arity is zero — established by reading the vtables
rather than by assuming, which is what the earlier withdrawal required.

It also identifies the boxed type: vtable `0x005E4EA4` is **`CFloatDataType`**,
and it is the vtable the three characterized health natives install at `+0x00` of
their allocated 0x18-byte return box. So `GetRealHealth`, `GetInitialHealth` and
`SpawnersEmpty` return a **boxed float**, and `+0x30`/`+0x34` are its
zero-argument accessors — consistent with health being a float and with
`SpawnersEmpty` returning a float-encoded boolean.

Completing the seven-slot map per native is now unobstructed and is the next
step; renaming still waits on it.

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
