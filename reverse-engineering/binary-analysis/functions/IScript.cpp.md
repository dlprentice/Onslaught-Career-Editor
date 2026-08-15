# IScript mission-scripting interface

Status: active static function map

The retail IScript handlers bridge MissionScript commands to cameras, audio,
object references, vectors, objectives, career slot bits, and Goodie state.
Current corrected metadata is owned by the
[reviewed correction plan](../ghidra-reviewed-correction-plan-2026-07-13.json).

`0x0052ff30 ScriptCommandRegistry__InitBuiltins` initializes 144 contiguous
`0x40`-byte descriptor slots. An older generated schema, now retained only in
Git history, mistook record zero's handler field for the table base and cannot
decide an exact row or binding. The current exact 144-row registry is the
[MissionScript appendix in `../../ghidra-functions.md`](../../ghidra-functions.md#appendix-a-complete-144-entry-missionscript-native-registry);
direct stores in the pristine image decide the `Pause` row below.

## Name corrections — 2026-07-28 and 2026-08-13

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](_index.md#the-name-corrections-of-2026-07-28).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x00535560` | `IScript__SetThingRefViaCUnitHelper4FD830_FromArg`; later `IScript__SetFactionForHierarchy_FromArg` | `IScript__SetAllegiance` | shipped Tier-2 registry vocabulary; underlying hierarchy/faction mechanism retained |
| `0x005362a0` | `IScript__GetTextWidth`; later `IScript__GetWorldTextSlotTimerValue` | `IScript__GetVariable` | shipped Tier-2 registry vocabulary is broader than the measured world-text-slot timer wrapper |

Where a row's **suffix** moved rather than only its class prefix, the behavioural
text beside it in this note was written for the old name. This sweep corrected
names against the export and re-derived no behaviour, so read any such gloss as
unverified against the new name until it is re-measured.

---

## Functions (46 listed)

| Address | Name | Purpose |
|---------|------|---------|
| 0x005333b0 | IScript__Constructor | Construct the 0x3c-byte mission-script object for `CComplexThing__SetScript` |
| 0x00533430 | IScript__ScalarDeletingDestructor | Scalar deleting destructor wrapper (`flags&1` frees `this`) |
| 0x00533450 | IScript__Destructor | Tear down the script object, listener/state set, and monitor base |
| 0x00533500 | IScript__CallEvent0AndRegisterNestedListeners | Dispatch event id 0 and register nested `CScriptEventNB` listeners |
| 0x005335a0 | IScript__CallEventId6_OrReset | Dispatch event id 6 or reset when the script VM is shutting down |
| 0x005335d0 | IScript__CreateThingRef | Create a reference to a game object |
| 0x00533660 | IScript__CallEventId5_OrReset | Dispatch event id 5 from destruction/cleanup-adjacent paths or reset |
| 0x00533690 | IScript__CreateThingRefWithSquad | Create thing ref with CRelaxedSquad initialization |
| 0x005337e0 | IScript__CallEventId3_OrReset | Dispatch event id 3 from shutdown/deploy-adjacent paths or reset |
| 0x00533840 | IScript__RestoreSavedStateAndGotoInstruction | Restore a saved script state and resume at the saved instruction cursor |
| 0x005338a0 | IScript__SetPlayerLives | Set per-player lives counters (`SetPlayerLives(player_index,lives)`) |
| 0x005338d0 | IScript__SetSlot | Set a slot bit in the runtime script bitset only (`SetSlot(slot,val)`) |
| 0x00533900 | IScript__SetSlotSave | Set a slot bit and persist it into career save data (`SetSlotSave(slot,val)`) |
| 0x005339a0 | IScript__GetSlotBitValue | Get career slot bit value (tech unlocks) |
| 0x00533a70 | IScript__SetGoodieState | Set `g_Career_mGoodies[index-1]` state (1-based index in scripts) |
| 0x00533aa0 | IScript__GetGoodieState | Get `g_Career_mGoodies[index-1]` state (cutscene/kill goodies) |
| 0x00533b70 | IScript__Create3PointPanCamera | Create camera pan with 3 control points |
| 0x00533eb0 | IScript__Create4PointPanCamera | Create camera pan with 4 control points |
| 0x005345d0 | IScript__Magnitude | Registry `Magnitude`; measured vector-length wrapper |
| 0x005347b0 | IScript__IsNumberBetween | Registry `IsNumberBetween`; measured range check |
| 0x005348c0 | IScript__Damage | Registry `Damage`; measured forwarder that hands its float argument to the runtime receiver's damage virtual (`vtable +0xa0`) with a non-null source, `applyShields=1`, and `meshPart=-1` |
| 0x00534b80 | IScript__GetX | Registry `GetX`; measured vector-component wrapper |
| 0x00534c10 | IScript__GetY | Registry `GetY`; measured vector-component wrapper |
| 0x00534ca0 | IScript__GetZ | Registry `GetZ`; measured vector-component wrapper |
| 0x00534fb0 | IScript__EnableWeapon | Registry supplies weapon scope; body visibly dispatches the supplied value through vtable slot `+0x198` |
| 0x00534fe0 | IScript__DisableWeapon | Registry supplies weapon scope; body visibly dispatches the supplied value through vtable slot `+0x19c` |
| 0x00535010 | IScript__EnableSpawner | Registry supplies spawner scope; body uses the enable-by-name engine helper |
| 0x00535040 | IScript__DisableSpawner | Registry supplies spawner scope; body uses the disable-by-name engine helper |
| 0x00535530 | IScript__SetStealth | Registry supplies stealth meaning; body visibly dispatches the supplied float through vtable slot `+0x1c8` |
| 0x00535560 | IScript__SetAllegiance | Registry vocabulary over the measured `CUnit__SetFactionForHierarchy` path |
| 0x00535670 | IScript__GetWeaponName | Registry supplies weapon scope; body calls the battle-engine weapon-physics-name path |
| 0x005357b0 | IScript__GetConfiguration | Registry vocabulary over the measured current thing-type/configuration string path |
| 0x005362a0 | IScript__GetVariable | Registry name is broader; measured implementation wraps `CWorld__GetWorldTextSlotTimerValue` |
| 0x005363e0 | IScript__GetPlayerBattleEngine | Get player's battle engine reference |
| 0x00537410 | IScript__AddMessage | Build and queue a localized `CMessage`; queued advancement can reach voice playback |
| 0x00537500 | IScript__PlayCharMessage | Build and queue a localized character message; the measured body/call layer registers no callback |
| 0x005375f0 | IScript__PlayCharMessageWait | Build and queue a localized character message and schedule its wait event; no fade axis was found |
| 0x005377e0 | IScript__PlayPCharMessage | Build and queue a localized character message with caller-varied argument 7, the measured `P` axis |
| 0x005378e0 | IScript__PlayPCharMessageWait | Build and queue the `P`-axis character message and schedule its wait event; no fade axis was found |
| 0x00537c40 | IScript__PrintText | `PrintText(text_id)`: resolve text id through `CText__GetStringById` and print it through `CConsole__Printf("%w", ...)` |
| 0x00537c70 | IScript__Pause | Mission native `Pause(seconds)`: save the current execution and schedule its continuation for current time plus the float argument |
| 0x00537fd0 | IScript__IsFriendly | Return whether the current script context is friendly (`IsFriendly()`) |
| 0x005381a0 | IScript__LevelLost | Declare the current level LOST (`LevelLost()`) |
| 0x005381c0 | IScript__LevelLostString | Declare the current level LOST with a text id (`LevelLostString(message_id)`) |
| 0x005381e0 | IScript__LevelWon | Declare the current level WON (`LevelWon()`) |
| 0x005383c0 | IScript__PostEvent | Registry `PostEvent`; measured implementation allocates/schedules event ID `2000` for `NEXT_FRAME` (`-1.0f`) |
| 0x0052ff30 | ScriptCommandRegistry__InitBuiltins | Wave864 built-in command descriptor registry initializer; 144 contiguous 0x40-byte records |

### `Pause` vertical contract

The shipped registry is runtime-populated, so its descriptor slots are zero in
the file image. Direct stores from `ScriptCommandRegistry__InitBuiltins`
establish row 4 at base `0x0064CE20`, stride `0x40`, with the string `Pause` and
handler `0x00537C70`. The saved Ghidra name is now `IScript__Pause`, promoted
as Tier-2 registry vocabulary rather than an original C++ symbol.

The pristine handler body reads argument zero through the script value's float
getter, clones the active `CEventFunction` execution state, appends it to the
set at `IScript+0x28`, schedules event `0x7D1` for
`DAT_00672FD0 + seconds`, sets `DAT_0089C800` to 1, and returns with the fixed
three-argument script-command ABI. This is a timed MissionScript continuation,
not `CGame__Pause` or the in-game menu.

Level 100 contains 35 authored `Pause` calls across 10 `.msl` files.
`TargetZone1.msl` supplies the focused law used by the reconstruction:
`Pause(0.5)` separates setting the zone reached from unsetting/deactivating it
and posting the firing-range event. The copied-runtime trace
`G:\bea-ttd\play-level100\play-level100.run`, SHA-256
`03599CEA7459810F601174A6713EBF17CF12DFE88D593D7F87FD5B94C564E40E`,
observed one call at `0x00537C70`; current v5 symbolic and numeric
`TTD.Calls` both returned 1. The positive control
`CWorldPhysicsManager__CreateThingByType` returned 33/33. Query result:
`local-lab/pause-native-count-v1/result.json`, SHA-256
`9B642820D73EA40BEA8CCB9808D0B1EFB33F57B898857300010DD30CBF4BB7F2`.

An independent state query on that same trace sought the first call's exact
entry and return positions. At entry, `DAT_0089C800` was zero and the
`IScript+0x28` continuation-set head/tail were both null. At return,
`DAT_0089C800` was one and both head/tail pointed to the new
`0x03F90098` continuation, with count one. The return address was inside
`CInstructionOP_CALL::ExecuteCall`. Result SHA-256:
`72D18ADF013BC82AB1C6365AB621AD118ED2C18125E04EB788DF2BFD01710C77`.
The state query did not independently decode the float argument or scheduled
due time; those parts remain joined by the pristine body, the authored
`Pause(0.5)` instruction, and the focused reconstruction test rather than
being overstated as direct trace observations.

The rebuild already owns the same engine-neutral behavior in
`Level100MissionTiming.PauseTicks` and the two compiled-script execution
contexts. Its focused `TargetZone1` test retains the raw `0.5f` argument bits,
proves no continuation through ticks 1–14, and proves resumption at tick 15.

### `Damage` vertical contract

Recorded 2026-08-15. The registry descriptor is row 69, which the shared base
`0x0064CE20` and stride `0x40` place at `0x0064DF60` — the same address the
independent registry table in [`ghidra-functions.md`](../../ghidra-functions.md)
lists for shipped name `Damage` and handler `0x005348C0`. The saved Ghidra name
is `IScript__Damage` over the body `0x005348C0`–`0x005348ED`, promoted as Tier-2
registry vocabulary rather than an original C++ symbol.

**The wrapper owns no damage law.** Its indirect call at `0x005348E3` dispatches
through the *runtime* receiver's `vtable +0xA0`. On the forced Level 100 pilot
the receiver's vtable `0x005E24DC` resolved that slot to `CUnit__ApplyDamage`
at `0x004F9A90`, receiving the amount unchanged plus a non-null source,
`applyShields = 1`, and `meshPart = -1`. This refuted the preregistered rival
that the wrapper hardcodes `CBattleEngine::Damage` at `0x0040A890`; the two
`Damage` entities remain distinct, and which law runs is a property of the
receiver, not of this function.

The measured life transition is a plain float32 subtract with **no clamp at
zero**: `0x3BA3D70B - 0x447A0000 = 0xC479FFAE`
(`0.005000000353902578 - 1000.0 = -999.9949951171875`), reproduced exactly in
IEEE-754 single precision. Shields stayed `0.0 -> 0.0` at `applyShields = 1`, so
that arm proves only that zero shields absorb nothing. Evidence:
`local-lab/damage-chain-pilot-2026-08-02/runtime-contract.json` and its 7.25
holdout (`0x40E80000`), campaign contract `C-8c445f1e27de9913`.

**Shipped authored callers — six sites in four levels.** The pilot recorded that
it established no natural issue path. The released `.msl` corpus does contain
authored calls to this native, though never in Level 100:

| Site | Form | Amount |
| --- | --- | --- |
| `level500\Submarine.msl:83` | bare self-receiver | `health`, set to `GetHealth() / 6` |
| `level500\Submarine.msl:87` | bare self-receiver | integer literal `100` |
| `level521\hive.msl:339` | `other_thing.Damage(...)` | float literal `0.25` |
| `level522\hive.msl:339` | `other_thing.Damage(...)` | float literal `0.25` |
| `level530\hive.msl:292` | `other_thing.Damage(...)` | float literal `0.25` |
| `level720\Prison.msl:37` | bare self-receiver | `orig_health / 2` |

`level521\hive.msl` and `level522\hive.msl` are byte-identical
(SHA-256 `0f636d9d0aff7fa21cbd8659267f105dee6b7bcd861ebd5d930d1d43cd45ebfa`,
13,433 bytes); `level530\hive.msl` is
`7d11ccf69a85419efbcea3181f224b0392c16e6b1dfff6035bccbb860e36e15b`,
`level500\Submarine.msl` is
`ebc6e7c50b0a345ba5305abd8f0a21265532a6efc9733469b88a6af606810051`, and
`level720\Prison.msl` is
`df4467e893bfca24cbefea8d93bcfa8de3fa45243b49ee605e2f65f9d3389c52`, all read
from the pristine safe copy.

**The level 521 hive script is proved live, and this native is proved not to
fire at level start.** Corrected 2026-08-15: an earlier draft of this section
called attachment unverified because no `SetScript("hive")` exists anywhere in
the corpus. The retained level-521 opening settles it. Reading the exec-coverage
index
`G:\bea-ttd\q-campaign-coverage-v1\level-opening-3m-v1-level521\coverage.jsonl`
(7,077 executed ranges over the pristine module at base `0x400000`):

| Handler | Covered in the 181 s opening |
| --- | --- |
| `IScript__Teleport` `0x005369B0` | **yes**, range `0x005369B0-0x005369E1` |
| `IScript__Damage` `0x005348C0` | no |
| `CUnit__ApplyDamage` `0x004F9A90` | no |
| `CBattleEngine::Damage` `0x0040A890` | no |

`Teleport` is authored in the whole of level 521 exactly once, at
`hive.msl:57` — the only other occurrence, `:54`, is commented out — so its
execution proves `hive.msl`'s `init()` ran and the boss object is live. The
script is attached; it simply never activates at start. The same index shows
this native and both damage laws absent, which is a measured negative rather
than an absence of looking: the contact handler is gated behind
`allowed_to_damage` and a player collision that the opening never performs.
This matches
[`tools/RUNBOOK-level521-native-capture.md`](../../../tools/RUNBOOK-level521-native-capture.md),
which already targets `Damage` as one of the natives reachable only by flying
the battle engine into the boss.

Two facts follow from the authored content itself. The amount **shares units
with `GetHealth`** — three of the six sites derive it from a `GetHealth()`
return — and `Prison.msl` then polls `GetHealth()` in a `while` loop until it
falls to `orig_health / 2`, so shipped content *depends* on the plain decrement
that the measured bits confirm. The three hive sites are a contact handler
gated by `allowed_to_damage` with `Pause(0.5)`, whose shipped comment reads
"damage them every 0.5 secs", against an explicit
`IsA(THING_TYPE_BATTLE_ENGINE)` receiver. Submarine.msl also brackets its call
in `SetVulnerable(TRUE)` / `(FALSE)`, the same idiom the authored pilot used.

**Both damage laws are the same vtable slot, read from the specimen.** Slot
`+0xA0` is slot 40, and the pristine image resolves it for each receiver class
directly:

| Receiver vtable | File offset | Slot `+0xA0` target |
| --- | --- | --- |
| `CBattleEngine` `0x005D89C4` | `0x001D8A64` | `0x0040A890` `CBattleEngine::Damage` |
| measured `CCannon` receiver `0x005E24DC` | `0x001E257C` | `0x004F9A90` `CUnit__ApplyDamage` |

So the single indirect call at `0x005348E3` provably reaches the player damage
law for a battle-engine receiver and the unit law for a unit receiver. The
three hive sites gate on `IsA(THING_TYPE_BATTLE_ENGINE)` before calling, which
makes them *authored* callers of `CBattleEngine::Damage @ 0x0040A890` — the same
entity that already carries its own `C2_BOUNDED_RUNTIME` contract and rebuild
owner. This is a static specimen read joining three existing contracts; it is
neither a runtime observation of those calls nor proof that they execute.

**Level 100 does not reach this native.** Decoding all 25 hash-pinned Level 100
script objects yields 366 native calls across 40 distinct commands, and 69 is
not among them. Reaching this path in Level 100 is therefore a property of the
released VM, not of released Level 100 content. Two independent decoders — a
scratch Python reader and the rebuild's own `Level100MissionProgram` parser —
agree on both totals.

The rebuild owns the forwarding half in
`Level100ActorScriptRuntime.InvokeDamageNative`, which preserves the authored
float32 bits exactly, widens an integer literal rather than rejecting it, emits
a typed `Damage` command boundary, and mutates no actor state. Parity tests:
`Level100MissionTests.MissionNativeDamage_ForwardsTheAuthoredFloat32AmountUnchanged`
and `MissionNativeDamage_IsIssuedByNoShippedLevel100Program`. The receiving law
stays with its existing owners — `Level100Destruction` for the `CUnit` arm,
already pinned to `0xC479FFAE` by
`Level100DestructionContactTests.ApplyDamageTraceVectorPreservesExactOverkillBits`,
and `Level100PlayerDamage` for the battle-engine arm.

**A natural call is already in the retained corpus — corrected 2026-08-15.** An
earlier draft of this section claimed no retained trace reaches a shipped call
site. That was wrong, and re-querying all 66 level-opening coverage indexes
disproves it:

| Handler | Levels covering it, of 66 |
| --- | ---: |
| `IScript__Damage` `0x005348C0` | **1** — `level720` |
| `CUnit__ApplyDamage` `0x004F9A90` | 18 — incl. `level720` |
| `CBattleEngine::Damage` `0x0040A890` | 3 — `level731`, `level732`, `level854` |

Level 720 is exactly where `Prison.msl:37` sits, and that call needs **no player
action**: `init()` runs `HalfDestroy(); Pause(3.0); PostEvent("Health Check")`,
and the handler calls `Damage(orig_health / 2)` — well inside a 181 s opening.
The same trace covers `CUnit__ApplyDamage`, which is what `+0xA0` should resolve
to for a prison-building receiver, so this is a natural-path corroboration of
the receiver-selection rule rather than a forced one. The trace is
`G:\bea-ttd\level-opening-3m-v1-level720`, and querying a retained trace needs
no elevation.

The hive contact remains unobserved, but it is now the *harder* of two natural
paths rather than the only one, and `Prison.msl` exercises the bare
self-receiver form with a `GetHealth()`-derived amount.

Open: the source argument's identity, whether the compiler emits Integer or
Float for `Damage(100)`, positive-shield absorption, and death/cleanup ordering
remain unmeasured.

Next instrument, cheapest first:

1. **Query the retained level 720 trace.** It already contains a natural call
   and needs no elevation, no gameplay, and no new capture. Read the entry
   arguments, `ECX`, the receiver vtable, and the resolved `+0xA0` target with
   the existing `tools/Invoke-TtdCallContextV2.ps1`. This is the measurement
   that should have been run before any of the wording above was written.
2. **A battle-engine receiver.** Level 720's receiver is a prison building, so
   it tests the `CUnit` arm. `level731`, `level732`, and `level854` cover
   `CBattleEngine::Damage`, so check whether any of those reaches it *through*
   `0x005348C0` before authoring anything.
3. **The hive contact, only if 1 and 2 leave it open.** It is expensive for a
   measured reason: TTD runs this game about **62× slow** — a 301 s recording
   captured 97 simulation ticks, or 4.85 s of game time
   (`local-lab/TTD-COMBAT-TRACES-2026-08-02.md`) — and reaching the contact
   needs eight turrets, the research station, boss lift-off, then a collision.
   `tools/Test-Level521NativeCoverage.ps1` already scores such a take, and
   unattended recording would need `TTD.exe -installservice` once.

## Key Patterns

### Object Allocation Pattern
All functions use `OID__AllocObject` to create script result objects:
```c
puVar = OID__AllocObject(8, 0x18, "IScript.cpp", lineNumber);
if (puVar != NULL) {
    *puVar = vtable;        // Set vtable pointer
    puVar[1] = returnValue; // Set return value
}
```

### Camera Creation (3/4-Point Pan)
The camera functions create CBSpline objects for smooth camera movement:
- Transform world-space coordinates using thing's local matrix
- Create CSPtrSet lists of control points
- Allocate CBSpline with 3 points and initialize camera path

### Vector Operations
Simple extraction of X/Y/Z components from 12-byte vector structure:
- X at offset 0
- Y at offset 4
- Z at offset 8
- Length uses SQRT(x*x + y*y + z*z)

### Sound System Integration
Sound functions integrate with the sound manager:
- Use `FUN_004f2580` to convert sound enum to resource
- Support priority levels (0-10)
- Support fade effects with 0x3d4ccccd (0.05f) fade rate
- Event ID 0x7d1 (2001) for sound fade event

## Related Global Variables

| Address | Purpose |
|---------|---------|
| 0x0089c7f0 | Script system disabled flag |
| 0x008a9ac0 | Game state (4 = exiting) |
| 0x0089c528 | Last created script object |
| 0x008a9d84 | Sound manager initialized flag |
| 0x008a9d3c | Player array base |
| 0x0089c590 | Sound manager instance |

## VTables Referenced

| Address | Class |
|---------|-------|
| 0x005e4af8 | Script integer/thing ref result |
| 0x005e4b4c | Script thing ref with squad |
| 0x005e4d50 | Script boolean result |
| 0x005e4df8 | Script thing ref (final) |
| 0x005e4ea4 | Script float result |
| 0x005e4f1c | Sound fade state |
| 0x005e4f34 | Scheduled event |

## Error Strings

| Address | String | Function |
|---------|--------|----------|
| 0x0064fa9c | "FATAL ERROR: null thing passed to 'Create3PointPanCamera'" | IScript__Create3PointPanCamera |
| 0x0064fad8 | "FATAL ERROR: null thing passed to 'Create4PointPanCamera'" | IScript__Create4PointPanCamera |
| 0x0064fc3c | "Fatal error: Player %d has no battle engine!!!" | IScript__GetPlayerBattleEngine |
| 0x0064fc6c | "Warning: sorry no player %d returning 1" | IScript__GetPlayerBattleEngine |
| 0x0064fd30 | "_unknown_" | IScript__PlaySound (default sound name) |
| 0x0064fd3c | "SHIT this should never happen" | IScript__PlaySoundWithFade (error case) |

## Calling Convention

Wave578 split the IScript object/event helpers from the later interpreter command handlers. The lifecycle and event helpers at `0x005333b0..0x00533840` are normal retail thiscall-style helpers: `ECX=this`; constructor cleanup is `RET 0x8`; scalar-deleting and thing-ref helpers use `RET 0x4`; register-only event/reset helpers have no stack cleanup. CreateThingRef helpers are IScript thiscall helpers with RET 0x4, not the fixed three-stack-argument script-command ABI.

Later IScript command handlers are called by the MissionScript interpreter using a fixed **3-argument stack ABI** (most return with `ret 0x0c`, i.e. callee pops 12 bytes).

Observed (Steam `BEA.exe`):
- `arg0`: pointers to script argument objects (handlers call virtual getters on these objects)
- `arg1`: often unused (sometimes a state/flags value)
- `arg2`: out-result pointer for commands that return a value (e.g. `IScript__GetSlotBitValue` writes `*out`)

Virtual getters on argument objects (common offsets):
- vtable+`0x30`: integer getter (e.g. `LevelLostString(message_id)`)
- vtable+`0x34`: float getter
- vtable+`0x3c`: byte/bool-like getter (seen in `IScript__SetSlot`)
- vtable+`0x44`: vector getter

Note: many handlers ignore `arg1/arg2` (e.g. `IScript__LevelLost`), so Ghidra may infer fewer parameters even though the call ABI is fixed.

## Integration with CGame Slot Bits

Slot-bit persistence is script-driven:
- `GetSlot(...)` returns `CGame__GetSlot(slot)` (`0x0046d410`) from the runtime slot-bitset at `CGame + 0x308`.
- `SetSlot(slot,val)` calls `CGame__SetSlot(slot,val)` (`0x0046d3a0`) on the runtime slot-bitset (persists into CCareer on LevelWon via END_LEVEL_DATA copy).
- `SetSlotSave(slot,val)` calls `CGame__SetSlot(slot,val)` (`0x0046d3a0`) and also persists the same flag into the career save bitmap via `CCareer__SetSlot(&CAREER, slot, val)` (`0x004214e0`).


Goodie state manipulation is also script-driven:
- `GetGoodieState(index)` returns `g_Career_mGoodies[index-1]` as a scalar result.
- `SetGoodieState(index, state)` updates `g_Career_mGoodies[index-1]` in-place (scripts use 1-based indices).
- Retail state values are `0..3` (`GOODIE_UNKNOWN/INSTRUCTIONS/NEW/OLD`); see [`reverse-engineering/save-file/goodies-system.md`](../../save-file/goodies-system.md).
- Save-file mapping: goodie array starts at file offset `0x1F46`, so script index `N` maps to `0x1F46 + (N-1)*4`.


## Notes

1. **Exception Handling**: All functions set up SEH (Structured Exception Handling) frames with Unwind handlers
2. **Memory Safety**: Functions check for NULL allocations before dereferencing
3. **Squad System**: Some thing refs automatically initialize CRelaxedSquad for AI control
4. **Matrix Operations**: Camera functions perform full 3x3 matrix multiplication for coordinate transformation

## Claim boundary

These entries are static instruction, xref, string, and decompile findings.
They do not prove complete mission-corpus coverage, runtime command behavior,
exact VM/datatype layouts, installed-game patch safety, gameplay outcomes, or
rebuild parity. Save offsets and Goodie state remain owned by the save-format
contracts rather than this function map.
