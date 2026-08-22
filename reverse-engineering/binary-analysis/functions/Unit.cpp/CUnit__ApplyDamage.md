# CUnit__ApplyDamage

> Address: `0x004f9a90`

Status: active static function note — byte contract supersedes the Wave835
static read-back summary in place (see Prior-art corrections)
Last updated: 2026-08-22
Source File: none — `Unit.cpp` has no source body in `references/Onslaught/`
(checked 2026-08-22); only `thing.h:176`'s virtual declaration and
`Player.cpp:273-277` survive | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the shared CUnit damage boundary — slot-40
`Damage(float, CThing*, BOOL applyShields, int meshPartIndex)`. Cooldown
gate, allegiance/flag early-outs, AI-state damage scaling, nexus/weakpoint
mesh-name gates, segment-controller dispatch, shield-before-life ordering,
heal clamp to profile max, Tara/Billy bark tables with a %3 selector and
three once-per-state latches. 2,586 bytes; every claim below re-read from
the pristine specimen this wake.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
verified before reading) with capstone whole-body disassembly, raw byte
reads (body hash; float/string constant resolution; image-wide imm32 and
whole-.text rel32 censuses), caller-window disassembly, and cross-checks
against [`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md),
[`../BattleEngine.cpp/CBattleEngine__Damage.md`](../BattleEngine.cpp/CBattleEngine__Damage.md),
and pinned `references/Onslaught/BattleEngine.cpp:2127-2180` /
`thing.h:176` as architecture only. Corrections recorded below. No
`FUN_*` milled; no Core owner changed.

> Address: `0x004f9a90`

## Headline finding

The Wave835 read-back's four callsite addresses are confirmed exactly
(`0x004037be`, `0x00417a16`, `0x0048006d`, `0x004898b0`) and its field-role
sketch is confirmed in outline — but its "scales positive damage by
profile/state fields" sentence hides three separately gated multipliers,
its "repairs health-like `this+0xf8` for non-positive damage" arm is
actually a heal-clamp against profile max `[profile+0xc0]` that also runs
on the death path, and the body carries an entire measured Tara/Billy
bark subsystem the Wave835 note reduced to "queues damage text". This note
pins all of it at byte level.

## Contract (byte-exact)

Body `0x004f9a90`–`0x004fa4a9` inclusive through the complete
`ret 0x10` at `0x004fa4a7`, **2,586 bytes**, SHA-256
`c00c805fc86ad1f52e6ab7d8fc739c456983914319ad99870d49c88b8733f859`.
SEH frame (`0x005d55b4` handler), `sub esp, 0x90`, saves ebx/ebp/esi/edi.
**17 `E8`, 7 `E9`** (all short forward jumps inside the body; zero
out-of-body `E9`). Signature confirmed: `thiscall`, four stack dwords,
`ret 0x10`.

Argument map (from the caller windows and body reads):

| Arg | Meaning | Anchor |
| --- | --- | --- |
| `ecx` | `this` = CUnit receiver | `mov esi, ecx` `0x004f9ab5` |
| stack +0xac (arg1) | `float amount` | `fld [esp+0xb0]` after pushes `0x004f9b22` |
| stack +0xb0 (arg2) | `CThing* source` | `ebx` via `mov ebx, [esp+0xac]` `0x004f9aad`; deref `[ebx+0xec]`, `[ebx+0x34]` flags |
| stack +0xb4 (arg3) | `BOOL applyShields` (1 = shields on) | gate at `0x004f9df8..0x004f9e01` |
| stack +0xb8 (arg4) | `int meshPartIndex` (-1 = none) | `ebp` via `cmp ebp,-1` `0x004f9b7e` |

## Stage law (byte-exact)

1. **Damage-cooldown reset gate** (`0x004f9abc`–`0x004f9ae2`): if
   `[this+0x148]` live **and** source `[src+0x34]` bit 2 clear **and**
   `[src+0xec]` live **and** `[src+0xec]+0x34` bit 4 set → call
   `CUnit__ResetDamageCooldownTimer` `0x004e6660(this=unit, src)`. That
   callee is 21 bytes, SHA-256
   `2f0568d877c62bd654adaef35fe8954ca23f24f286642dcf56aa6492c1c79b8`,
   and stores `[0x00672fd0] + 5.0f` into `[unit+0x88]` (`ret 4`).
   Exactly one inbound `E8` image-wide (the site above); zero imm32.
   The cooldown *consumer* is not in this body — honest unknown.
2. **Reentrancy guard** (`0x004f9ae2`–`0x004f9b06`): if unit `[esi+0x2c]`
   bit 4 set **and** source `[ebx+0x34]` dword bit `0x1000000` set **and**
   `[[esi+0x164]+0x124] != 0` → exit to epilogue without damaging.
3. **AI-state damage scaling** (`0x004f9b07`–`0x004f9b2f`): when
   `[unit+0x244] ∈ {3, 4, 5}`, multiply amount by `[unit+0x164]->[+0x160]`.
   The AI-state field is the same `[+0x244]` the deploy helpers test
   (`CWarspite__TransitionToUndeploying` writes it; W008 B04).
4. **Positive gate** (`0x004f9b36`): `amount <= 0.0f` jumps to the late
   repair block (stage 9). Only positive amounts damage.
5. **Profile live gate** (`0x004f9b4e`): `[unit+0x15c] == 0` → epilogue
   (dead unit refuses further processing).
6. **Shutdown-bit guard** (`0x004f9b5c`–`0x004f9b71`): if `[unit+0x228]`
   nonzero and source dword bit `0x1000000` set → epilogue.
7. **Nexus / weakpoint mesh-part gates** (`0x004f9b71`–`0x004f9dc8`):
   - With source flag bit `0x1000000` set: walk the unit's part-name list
     `[[unit+0x30] vtable+0x24() -> +0x15c count / +0x160 array]`, each
     entry `stricmp(entry+0xdc)` vs `"nexus"` (`0x00633af4`) until match;
     then line-test `0x0050b030(0x00855090, ...)` from source pos
     `[src+0x1c]` toward the hit position built through
     `CMCMech__BuildInterpolatedPoseAndAnchor` `0x004b0fb0`;
     `CLine__ctor_copy` `0x004098e0` seeds `-1.0f`/vptr `0x005d8bfc`;
     miss (`edi == -1`) or wrong-part mismatch → epilogue.
   - Without that flag: if `meshPartIndex >= 0`, resolve part name at
     `[part-array][index]+0xdc`; `stricmp` vs `"nexus"` equal → epilogue
     (named part is immune unless the flag path above already passed).
   - Weakpoint: if `[unit+0x22c]` live and the resolved part name equals
     `"weakpoint"` (`0x00633ae8`), multiply amount by **5.0f**
     (`0x005d85d8`) at `0x004f9db4`.
8. **Segment dispatch** (`0x004f9dc8`–`0x004f9de1`): if `[unit+0x178]`
   (segments controller) live → tail-call
   `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`
   `0x00444030(controller, meshPartIndex, amount, src)` and jump straight
   to the epilogue — the shield/life code below does **not** run for
   segmented units. Matches
   [`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)'s
   controller-dispatch row and CUnit__ApplyDamage forwarding row.
9. **Shields before life** (`0x004f9de6`–`0x004f9e61`): first
   `vtable[+0x1ac](amount)` hook. If `applyShields != 0`:
   - shield `[esi+0x100] >= amount` → subtract full amount from shields,
     done (life untouched);
   - else shields < amount → subtract shields from amount, store shields 0,
     continue to life with remainder.
   Then life `[esi+0xf8] -= remaining`, storing the remainder.
10. **Death lane** (`0x004f9e74`–`0x004f9edd`): remainder `< 0.0f`
    (`test ah,1` on x87 status, i.e. CF set = below) **and** unit
    `[esi+0x2c]` bit 4 clear:
    - kill credit: source `[src+0x34]` bit 2 set, `[src+0xec]` live,
      `[src+0xec]+0x34` bit 3 set → `[[src+0xec]+0x574] += 1` at `+0x30`.
      Architecture sibling: pinned source
      `Player.cpp:273-277 KilledEnemyThing` five-type increment.
    - if `[[unit+0x164]+0x11c] == 0`: call `vtable[+0xc8]()`, then
      `vtable[+0x11c](amount, src)`;
    - clear `[unit+0x1f0] = 0`.
11. **Heal clamp / non-positive repair** (`0x004f9edd`–`0x004f9fa0`):
    reached by the stage-4 jump (amount <= 0), or fall-through when no
    death. If shields `[esi+0x100] < 2.0f` (`0x005d8ba0`) and profile
    `[unit+0x164]` live and life `[esi+0xf8] < [profile+0xc0]` and
    life `>= 0.0f`: if `-[amount] >= [profile+0xc0] - life` →
    life `[esi+0xf8] = [profile+0xc0]` exactly; else
    `life -= amount` (negative amount heals). This is the repair arm the
    Wave835 note called "repairs health-like this+0xf8".
12. **Bark latches** (`0x004f9fa0`–`0x004fa42a`): three independent arms;
    arm k fires only when latch `[unit+0x234 + 4k] == 0`, sets it to 1,
    and emits one text id chosen by `(Random__NextLCGAbs([0x008a9d9c]) % 3)`
    plus which of `"Tara Fighter"` (`0x00633b98`) / `"Billy Fighter"`
    (`0x00633b88`) the profile name `[profile+0xb0]` equals (default ids
    otherwise). Thresholds against life `[esi+0xf8]`:
    - severe: `life < 0.25f * [profile+0xc0]` (`0x005d858c`), latch
      `+0x23c`, also clears the other two latches back to 1-armed state
      (stores 1 at `+0x238`/`+0x234`);
    - moderate: `life < 0.5f * max` (`0x005d85ec`), latch `+0x238`,
      clears `+0x234`;
    - light: `life < 1.0f * max` (bare compare), latch `+0x234`.
13. **Damage text** (`0x004fa42a`–`0x004fa48a`): if global `[0x008a9d84]`
    live and the bark arm produced a string (`ebp != 0`): alloc 0x3c bytes
    (`CDXMemoryManager__Alloc 0x005490e0`, Unit.cpp debug path
    `0x00633b6c`, line token `0x44d`), build `CMessage` via
    `CMessage__ctor_base 0x004b6e50` with the unit, the string, color id
    `CText__GetStringById 0x004f2580` result, and queue through
    `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance 0x004b7ca0`.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x88]` | damage-cooldown expiry time | `0x004e6660` callee |
| `[this+0x2c]` byte bit 4 | DYING-style shutdown bit (gate + death-lane guard) | `0x004f9aea`, `0x004f9e81` |
| `[this+0xf8]` | life | store `0x004f9e6e` |
| `[this+0x100]` | shields | stores `0x004f9e24`, `0x004f9e50` |
| `[this+0x148]` | damage-cooldown reader link (live test) | `0x004f9abc` |
| `[this+0x15c]` | profile-live gate | `0x004f9b4e` |
| `[this+0x164]` | profile pointer | throughout |
| `[profile+0xb0]` | profile name char* (Tara/Billy compare) | `0x004fa00b` |
| `[profile+0xc0]` | maximum life (heal clamp + bark thresholds) | `0x004f9f41`, `0x004fa1d4` |
| `[profile+0x160]` | AI-state damage multiplier | `0x004f9b29` |
| `[profile+0x11c]` | death-callback gate | `0x004f9eb2` |
| `[unit+0x178]` | segments controller (dispatch, then return) | `0x004f9dc8` |
| `[unit+0x228]` | shutdown-guard field | `0x004f9b5c` |
| `[unit+0x22c]` | weakpoint-enable field | `0x004f9d79` |
| `[unit+0x234/+0x238/+0x23c]` | bark latches light/moderate/severe | stores `0x004fa41d`, `0x004fa2f0`, `0x004fa1bd` |
| `[unit+0x244]` | AI deploy state ({3,4,5} scale arm) | `0x004f9b07` |
| `[src+0x34]` bits `0x1000000` / `2` / `4` | flag paths (nexus bypass / kill credit / cooldown reset) | `0x004f9aee`, `0x004f9e87`, `0x004f9ac6` |
| `[src+0xec]` | source owner link (cooldown reset + kill credit) | `0x004f9acc`, `0x004f9e8d` |
| `[owner+0x574]+0x30` | kill counter dword incremented on death | `0x004f9ea3` |

Field names above are functional roles read off this body plus its callees;
the retail symbol names remain unproven and nothing here renames a saved
Ghidra symbol.

## Callers (all four inbound `E8` image-wide)

| Site | Caller (name-table identity) | Shape |
| --- | --- | --- |
| `0x004037be` | `CAirUnit__ApplyDamageAndResolveSlot19Vector_004037a0` | forwards its four args unchanged, then compares life to 0 |
| `0x00417a16` | `CBuilding__VFunc_40_004179a0` | pure forwarder; skips when `[this+0x178]` live or `[this+0x2c]` bit 4 set — matches the rebuild's PROVENANCE account of the prison-building slot 40 |
| `0x0048006d` | `CHiveBoss__ForwardApplyDamageUnlessFlag01000000_00480050` | skips when `[src+0x34] & 0x1000000`; passes `eax` twice (source reused as mesh arg slot per caller window) |
| `0x004898b0` | `CInfantryUnit__VFunc40_HandleCollisionDamageReaction` | collision-damage reaction passing computed args |

Caller names are the current name-table identities; the table's own
`_004037a0`-style suffixes are part of the saved symbol. Plus **19
DATA/vtable slots**: `0x005dd828`, `0x005dfa38`, `0x005dfddc`,
`0x005e002c`, `0x005e027c`, `0x005e0724`, `0x005e0980`, `0x005e0bd0`,
`0x005e1080`, `0x005e1530`, `0x005e1c24`, `0x005e232c`, `0x005e257c`,
`0x005e2a1c`, `0x005e3114`, `0x005e3374`, `0x005e3de0`, `0x005e403c`,
`0x005e4298` — the slot-40 `Damage` implementations across the shared-CUnit
class family (Wave835's list reproduced exactly).

## Pinned-source status

Absent. No `Unit.cpp` in the drop; `thing.h:176` declares the slot-40
virtual `Damage(float, CThing*, BOOL, int)` matching `ret 0x10` arity.
`BattleEngine.cpp:2127 CBattleEngine::Damage` and `Player.cpp:273-277
KilledEnemyThing` are the architecture siblings (shield-efficiency order,
kill-type increments) — cited as shape only, not byte proof.

## Prior-art corrections recorded by this note

Supersedes the corresponding sentences of the Wave835 read-back above (that
note's four-callsite proof and field-offset sketch stand unchanged):

- "**Scales** positive damage by profile/state fields": actually three
  separate gates — AI-state `{3,4,5}` × `[profile+0x160]`, weakpoint ×5.0,
  and the heal-clamp arm that can rewrite life upward to `[profile+0xc0]`.
- "Applies shield-like `this+0x100` **before** life-like `this+0xf8`":
  confirmed exact, including the insufficient-shield remainder path.
- "Queues profile/Tara/Billy damage text": actually three threshold latches
  (`+0x234/+0x238/+0x23c`) with a `%3` random selector over
  `Random__NextLCGAbs([0x008a9d9c])` and per-profile name tables; the
  Wave835 sentence names none of the mechanism.
- Related-functions row said `0x00444030` is reached "when `this+0x178`
  exists" — confirmed, but this note adds that the call is terminal for the
  function (the shield/life/bark stages never run on segmented receivers).

## Rebuild mapping

No Core owner changes this wake; the existing consumers stay bounded:

- `rebuild/OnslaughtRebuild.Core/Level100Destruction.cs` keeps its two
  proved whole-body calls and aggregate Warehouse path; this body confirms
  segmented receivers never reach the shared life/shield arithmetic, which
  is why the Warehouse consumes only its observed aggregate outcome.
- `rebuild/OnslaughtRebuild.Core/Level100PlayerDamage.cs` implements the
  player-side sibling (`CBattleEngine::Damage`), not this CUnit boundary;
  no change.
- No shipped Level 100 contact part is named `nexus` or `weakpoint`
  (checked across `OnslaughtRebuild.Core.Assets.Level100.*` this wake), so
  the mesh-name gates have no Level 100 consumer; focused tests correctly
  deferred until an owner needs them.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x004f9a90`–`0x004fa4a9` is not
  `c00c805f…33f859`, or the final instruction is anything but
  `c2 10 00` at `0x004fa4a7`.
- A fifth rel32 inbound to `0x004f9a90` appears, or any of the 19 imm32
  sites disappears.
- The weakpoint multiplier at `0x004f9db4` stops being `fmul [0x005d85d8]`
  with `0x005d85d8` = `00 00 a0 40` (5.0f).
- The cooldown callee at `0x004e6660` stops hashing
  `2f0568d8…c79b8` or storing `[0x00672fd0] + 5.0f` (`0x005d85d8`).
- `"nexus"` / `"weakpoint"` stop sitting at `.rdata 0x00633af4` /
  `0x00633ae8`.

## Receipts

- 2026-08-22 — pristine specimen
  (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, main tree),
  SHA-256 verified before reading. Tools: capstone whole-body disassembly
  (`local-lab/unitdmg/measure.py`), raw byte reads (body hashes; constant
  resolution `local-lab/unitdmg/consts.py`), whole-.text rel32 scan +
  image-wide imm32 census (`local-lab/unitdmg/xrefs.py`,
  `cooldown_xref.py`, `bit4.py`), caller-window disassembly
  (`callers.py`), PROVENANCE window-hash reproduction
  (`crosscheck.py`).
- Cross-references (same wake):
  [`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md),
  [`../IScript.cpp/IScript__SetSegmentHealth.md`](../IScript.cpp/IScript__SetSegmentHealth.md)
  (controller layout `+4`/`+8`/`+0xc`/`+0x18`),
  [`../BattleEngine.cpp/CBattleEngine__Damage.md`](../BattleEngine.cpp/CBattleEngine__Damage.md)
  (slot-40 sibling envelope),
  `rebuild/PROVENANCE.md` (terminal-threshold window hash reproduced).
