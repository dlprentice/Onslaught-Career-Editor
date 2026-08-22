# Patch-surface census — maximal patchable sites (static, pristine-only)

Status: active — static census, Phase 2 runtime probes are a separate card
Last updated: 2026-08-22
Summary: first cut `t_7b48b14a` plus successor `t_14fcbbed` expansion.
Evidence: MEASURED — every non-unknown TSV `original_bytes` compared to the
named specimen at write time; PE section table re-parsed; first-cut BSS
god-flag row retracted.
Specimen: `local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(2,506,752 bytes).
Machine-readable companion: [`patch-surface-rows.tsv`](patch-surface-rows.tsv)
(one row per candidate site; columns `va, offset, original_bytes, patched_bytes,
effect, confidence, evidence_path, risk, cheapest_verification`).
PE mapping owner: [`../reverse-engineering/binary-analysis/patch-surface/PE-MAPPING.md`](../reverse-engineering/binary-analysis/patch-surface/PE-MAPPING.md).

## Authority and method

- Every byte below was re-read for this census from the pristine specimen
  `local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`,
  SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
  (2,506,752 bytes), hash-verified at read time. The Steam install is
  deliberately patched and is never byte authority.
- PE section table parsed directly from the specimen (re-parsed 2026-08-22):
  `.text` VA `0x401000` rawsize `0x1D7000`, `.rdata` `0x5D8000/0x4A000`,
  `.data` VA `0x622000` **VirtualSize `0x3B2614`** / SizeOfRawData `0x3F000`,
  `.rsrc` `0x9D5000`. File-backed `.data` ends at `0x00661000`. VAs from
  `0x00661000` through `.data` virtual end `0x009D4614` are **BSS** — the
  loader zero-fills them. Naive `VA − 0x400000` in that band lands in
  `.rsrc` raw or past EOF and is **not** the runtime global. See
  `reverse-engineering/binary-analysis/patch-surface/PE-MAPPING.md`.
- TSV `original_bytes` for every non-`unknown-*` row were compared to the
  specimen in the `t_14fcbbed` writer and refused on mismatch.
- Confidence vocabulary: MEASURED (byte + behavior evidence),
  STATIC_ONLY (byte evidence verified here; behavior inferred from pinned
  source or prior bounded observations), SPECULATIVE (site plausible,
  semantics unproven).
- This catalog is additive to, and does not modify,
  `patches/catalog/patches.v2.json` (29 rows) — the product catalog with its
  own contract (`patches/CATALOG_CONTRACT.md`). Nothing here is product
  eligibility; Phase 2 runtime probes are a separate card.

## Coverage map

| # | System | Section | Notes |
|---|--------|---------|------|
| 1 | Mission timers | [§1](#1-mission-timers) | won-imm corrected to `0x0046F33D` |
| 2 | Instant win / lose | [§2](#2-instant-win--lose) | debug arms still SPECULATIVE |
| 3 | AI freeze (named tick call sites) | [§3](#3-ai-freeze-named-tick-call-sites) | per-unit think still absent |
| 4 | Physics constants | [§4](#4-physics-constants) | + friction rungs, COfG, zoom, water line |
| 5 | Player resources & damage | [§5](#5-player-resources--damage) | Damage/water gates now pinned; BSS god-flag retracted |
| 6 | Weapons (fire gate, charge cap) | [§6](#6-weapons-fire-gate-charge-cap) | + FireWeapon/ChargeWeapon siblings |
| 7 | Cheat flags | [§7](#7-cheat-flags) | + Maladim / latete call sites |
| 8 | Debug leftovers (console) | [§8](#8-debug-leftovers-console) | reachability still unpinned |
| 9 | Already-cataloged adjacent rows (pointer only) | [§9](#9-already-cataloged-adjacent-rows-pointer-only) | — |
| 10 | Explicit non-surfaces | [§10](#10-explicit-non-surfaces) | BSS list expanded |
| 11 | End-of-level ranking | [§11](#11-end-of-level-ranking) | FillOut stores |
| 12 | Career graph / goodies / kills | [§12](#12-career-graph--goodies--kills) | Update / SetSlot / GRADE |
| 13 | Flight / script enable | [§13](#13-flight--script-enable) | DisableFlight NOP, AddScore, SetVulnerable |
| 14 | Input / analogue | [§14](#14-input--analogue) | 0.001f scale |
| 15 | Collision / camera knobs | [§15](#15-collision--camera-knobs) | COfG, movie zoom |
| 16 | Script objective / pause flags | [§16](#16-script-objective--pause-flags) | or/and +0x2c, stop-flag |

---

## 1. Mission timers

### 1.1 Lost countdown — `CGame::DeclareLevelLost` store

| field | value |
|---|---|
| VA | `0x0046F4A8` (offset `0x0006F4A8`) |
| original | `c7 43 48 00 00 00 40` = `mov [ebx+0x48], 0x40000000` (2.0f) |
| candidate patches | bytes 3..6 → any IEEE-754 float, e.g. `00 00 00 00` (0.0f instant menu return), `00 00 A0 40` (5.0f source parity) |

Measured divergence from Stuart source (`game.cpp:75`
`GAME_COUNT_WHEN_LOST_OR_DRAW 5.0f`): retail ships **2.0f**. Recorded in
`rebuild/PARITY.md` known divergences with mutation-killed rebuild owner
`RetailGameEndCountdown.LostTicks` (test
`TutorialBroken_StartsTheTwoSecondLostCountdown`). The countdown value lands
in `CGame+0x48`; the main loop's quit wait consumes it.

Confidence: **MEASURED**. Risk: low — single-instruction immediate.
Cheapest verification: copied-launch Broke-Tutorial loss; time from death to
failure menu.

Sibling context (same function): `0x0046F49E` area also stores state 4 and
lost-reason via `c7 43 28 04 00 00 00` (`mov [ebx+0x28], 4`) — the state word
itself is another candidate but is consumed by many branches; not row-tracked.

### 1.2 Won countdown — `CGame::DeclareLevelWon` store

| field | value |
|---|---|
| VA | `0x0046F33D` (offset `0x0006F33D`) — imm32 of `mov [ebx+0x48], 5.0f` |
| instruction start | `0x0046F338`: `8b cb c7 43 48 00 00 a0 40` = `mov ecx,ebx; mov [ebx+0x48], 0x40A00000` (5.0f) |
| candidate patches | imm32 at `0x0046F33D` → e.g. `00 00 00 00` (0.0f instant handoff) |

Byte correction, two layers. `rebuild/PARITY.md` cites `0x0046F338` for this
store. First-cut `t_7b48b14a` moved the claim to `0x0046F33B`, but that
address is the `ModRM` byte (`43`) of `c7 43 48`. Re-read 2026-08-22:
`8b cb` at `0x0046F338`, `c7 43 48` at `0x0046F33A`, **imm32 `00 00 a0 40`
at `0x0046F33D`**. The TSV row follows the imm32. This lane does not edit
`rebuild/**`; PARITY stays as the rebuild owner left it. The PARITY *value*
(5.0f, `cmp eax,0x2E5/0x2E6` miss arm) is still correct.

Confidence: **MEASURED** (bytes + pinned countdown consumer). Risk: low.
Cheapest verification: copied Level 100 win; time from win overlay to
frontend handoff.

### 1.3 Simulation clock rate — `CLOCK_TICK`

| field | value |
|---|---|
| VA | `0x005D8578` (offset `0x001D8578`) |
| original | `cd cc 4c 3d` = 0.05f |
| candidate patches | e.g. `9a 99 19 3d` (0.038f ≈ faster world clock), `00 00 00 3f` (0.5f slow-motion) |

Consumed by `CEventManager::Update` at `0x0044B5E6`
(`fmul dword [0x005D8578]`; body byte-verified in
`reverse-engineering/binary-analysis/functions/CEventManager.cpp.md`,
which closes `time = frame × 0.05f`). Neighbour `0x005D857C` = 20.0f
(`GAME_FR`) is the reciprocal display constant — patching one without the
other desyncs anything reading both. Measured refcount of the 0.05f dword
address in the image: 48 references — this constant is shared; expect broad
side effects (event scheduling, physics tick, script waits all key off the
event-manager time law).

Confidence: **STATIC_ONLY** (byte + consumer identified; whole-game effect
unprobed). Risk: high — global time base.
Cheapest verification: copied launch with a scripted event timer visible.

---

## 2. Instant win / lose

### 2.1 Console `Win` command — `con_win`

| field | value |
|---|---|
| VA | `0x0046C186` (offset `0x0006C186`) |
| original | `03 7F` = `jg short` (skip unless `g_GameState == PLAYING(3)`) |
| candidate patch | `EB 7F` (`jmp`) → command always proceeds |

Function head `0x0046C180`: `83 3D C0 9A 8A 00 03` =
`cmp dword [0x008A9AC0], 3`. Body then pushes `(0,0)` and calls
`0x0046FB00` (win flow). Registered as console command `Win`
("Win this level") in `CGame::InitRestartLoop` per
`reverse-engineering/binary-analysis/functions/game.cpp/con_win.md`.
Requires an open console route to invoke; see §10 note on the dev-gate.

Confidence: **STATIC_ONLY**. Risk: low. Cheapest verification: console `Win`
outside PLAYING in a copied build.

### 2.2 Console `Lose` command — `con_lose` call site

| field | value |
|---|---|
| VA | `0x0046C209` (offset `0x0006C209`) |
| original | `e8 22 32 00 00` = `call CGame::DeclareLevelLost` |
| candidate patch | `90 90 90 90 90` → console lose becomes no-op (harden) |

Body `0x0046C200`: `6a 00 6a 00 b9 98 9a 8a 00` = push 0, push 0,
`mov ecx, 0x008A9AC0` (g_GameState singleton), then the call. Sibling of
`con_win`; named owner `con_lose [0x46c200..0x46c20e)`.

Confidence: **STATIC_ONLY**. Risk: low. Cheapest verification: console
invocation path in a copied build.

### 2.3 Scripted win — `IScript__LevelWon` call site

| field | value |
|---|---|
| VA | `0x005381E5` (offset `0x001381E5`) |
| original | `e8 06 71 f3 ff` = `call CGame::DeclareLevelWon` |
| candidate patch | NOP×5 → mission scripts cannot trigger the win transition |

This is the **only** direct call to `DeclareLevelWon` in the whole image
(measured rel32 scan over all of `.text`). All scripted wins route through
this one native. Owner `IScript__LevelWon [0x5381e0..0x5381ec)`; registry
record cited as `0x64D060` in the function note, though that region reads
file-zero (runtime-populated; see §10.3).

Confidence: **STATIC_ONLY** (call-site uniqueness measured; effect follows
from the pinned transition owner). Risk: medium — levels whose completion
depends on scripted wins become unwinnable. Cheapest verification: Level 100
script beat that posts the win event.

### 2.4 Scripted lose — `IScript__LevelLost` call site

| field | value |
|---|---|
| VA | `0x005381A9` (offset `0x001381A9`) |
| original | `e8 82 72 f3 ff` = `call CGame::DeclareLevelLost` |
| candidate patch | NOP×5 → scripts cannot force a loss |

Owner `IScript__LevelLost [0x5381a0..0x5381b0)`.

Confidence: **STATIC_ONLY**. Risk: low-medium (removes fail states some
levels author). Cheapest verification: a level whose script calls LevelLost.

### 2.5 Scripted lose-with-string — `IScript__LevelLostString` call site

| field | value |
|---|---|
| VA | `0x005381D3` (offset `0x001381D3`) |
| original | `e8 58 72 f3 ff` = `call CGame::DeclareLevelLost` |
| candidate patch | NOP×5 |

Owner `IScript__LevelLostString [0x5381c0..0x5381da)`. Same shape as §2.4;
separate native (index 106 record `0x64E8A0` per the function note).

Confidence: **STATIC_ONLY**. Risk: low-medium. Cheapest verification: same
as §2.4.

### 2.6 Debug-button win — `BUTTON_WIN_LEVEL` arm

| field | value |
|---|---|
| VA | `0x0046F945` (offset `0x0006F945`) |
| original / patch | jump-table dispatch target inside `CGame::ReceiveButtonAction`; score-randomize + win flow per `functions/game.cpp/CGame__ReceiveButtonAction.md` button map |

No single-byte form is claimed: the arm is entered through the button
dispatch switch. Reaching it requires the debug-button path (see §10.1).
Recorded as surface identification only.

Confidence: **SPECULATIVE** (arm mapped; invocation reachability in retail
unproven). Risk: n/a until a concrete byte plan exists. Cheapest
verification: prove how button IDs reach `ReceiveButtonAction` in retail.

### 2.7 Debug-button lose — `BUTTON_LOOSE_LEVEL` arm

Same posture as §2.6 at dispatch target `0x0046FA39`; ends in the
`call DeclareLevelLost` measured at `0x0046FA7C`.

Confidence: **SPECULATIVE**. Cheapest verification: same as §2.6.

### 2.8 Complete-all-objectives — `BUTTON_COMPLETE_ALL_OBJECTIVES` arm

Dispatch target `0x0046F9F3`; prints "Completing all Objectives" and writes
the objective state arrays (button-map note). The objective-array writes are
the interesting patchable stores for objective-counter cheats, but they are
inside a large arm without a pinned instruction-level map yet — left as an
open row rather than guessed bytes.

Confidence: **SPECULATIVE**. Cheapest verification: pin the store
instructions in that arm against the specimen.

Related predicate rows already carried elsewhere: the secondary-objective
ranking clamp lives in `FillOutEndLevelData` (see §9) and the
`CCareerNode` complete/link laws are in PARITY.md — those govern what a *win
is worth*, not whether it fires.

---

## 3. AI freeze (named tick call sites)

The card asks for freeze = NOP the tick call sites, named. Whole-image
rel32 scans give exactly one direct caller each for the simulation heartbeat
owners (each count MEASURED here):

### 3.1 `CGame::MainLoop` call site

| field | value |
|---|---|
| VA | `0x0046E0E0` (offset `0x0006E0E0`) |
| original | `e8 fb 0d 00 00` = `call CGame::MainLoop` |
| patch | NOP×5 → per-attempt frame loop never runs |

Sole direct caller: `CGame::RestartLoopRunLevel [0x46dc30..0x46e22a)`
(owner `0x0046DC30`). Freezes everything: rendering loop, input processing,
simulation, timers — the level hangs at its entry state. This is the total
freeze primitive.

Confidence: **STATIC_ONLY** (uniqueness + owner measured; hang behavior
follows from the pinned loop structure in
`functions/game.cpp/CGame__RestartLoopRunLevel.md`). Risk: high — soft-lock
by design. Cheapest verification: copied launch, observe no-frame progress.

### 3.2 `CEventManager::AdvanceTime` call site

| field | value |
|---|---|
| VA | `0x0046EB5D` (offset `0x0006EB5D`) |
| original | `e8 9e ca fd ff` = `call CEventManager::AdvanceTime` |
| patch | NOP×5 → world/event time stops advancing |

Sole direct caller: `CGame::Update [0x46e910..0x46ee75)` (owner
`0x0046E910`). `AdvanceTime [0x44b600..0x44b63a)` advances
`mTime += frame × 0.05f` and rotates the ring buffer without flushing.
Freezing time stalls every scheduled event (respawns, script waits, timed
objectives) while rendering and input continue.

Confidence: **STATIC_ONLY**. Risk: high (also gates UI timing that flows
through the same manager). Cheapest verification: copied build; observe a
timed event never firing.

### 3.3 `CEventManager::Flush` call site in gameplay update

| field | value |
|---|---|
| VA | `0x0046EBCE` (offset `0x0006EBCE`) |
| original | `e8 6d ca fd ff` = `call CEventManager::Flush` |
| patch | NOP×5 → due events accumulate but never dispatch |

Second direct caller of `Flush` (the first is `Update`'s own tail at
`0x0044B5F6`, which is the AdvanceTime+Flush pairing documented in
`functions/CEventManager.cpp.md`). Caller: `CGame::Update`. Difference vs
§3.2: time still advances (so `mTime`-based displays move) but nothing
dispatches.

Confidence: **STATIC_ONLY**. Risk: high. Cheapest verification: same harness
as §3.2, watching the event queue grow.

### 3.4 Frontend event pump — `CFrontEnd__Process` Update call site

| field | value |
|---|---|
| VA | `0x0046BFE` → exact site `0x00466BFE` (offset `0x00066BFE`) |
| original | `e8 bd 49 fe ff` = `call CEventManager::Update` |
| patch | NOP×5 → frontend menus lose their scheduled-event pump |

Caller: `CFrontEnd__Process [0x466ba0..0x466ddd)`. Included for completeness;
freezing it affects menus, not battlefield AI.

Confidence: **STATIC_ONLY**. Risk: medium (menu breakage). Cheapest
verification: frontend idle animation / music sequencing behavior.

### 3.5 Unit-level damage entry — `CUnit::ApplyDamage` call sites

| field | value |
|---|---|
| VAs | `0x004037BE`, `0x00417A16`, `0x0048006D`, `0x004898B0` |
| original | `e8 cd 62 0f 00` / `e8 75 20 0e 00` / `e8 1e 9a 07 00` / `e8 db 01 07 00` |
| patch | NOP×5 each → those four unit families stop taking routed damage |

Exactly four direct callers (MEASURED):
`CAirUnit__ApplyDamageAndResolveSlot19Vector_004037a0`,
`CBuilding__VFunc_40_004179a0`,
`CHiveBoss__ForwardApplyDamageUnlessFlag01000000_00480050`,
`CInfantryUnit__VFunc39_HandleCollisionDamageReaction`. Note the asymmetry:
NOPing these does **not** shield walkers/sentinels/etc., whose damage arrives
via vtable slot 40 dispatch (indirect, outside an E8/E9 scan) — a full
"units invulnerable" cheat needs the slot-40 body approach (§5.2), not these
four sites.

Confidence: **STATIC_ONLY** (per-family effect). Risk: medium.
Cheapest verification: shoot one building family member in a copied build.

---

## 4. Physics constants

All rows in this section patch the float operand itself (4 bytes). Shared
constant risk is quantified per row by measured dword-address refcount.

### 4.1 Gravity, walker/morph index — `CBattleEngine::Gravity`

| field | value |
|---|---|
| VA | `0x005D8BAC` (offset `0x001D8BAC`) |
| original | `6f 12 03 3b` = 0.002f |
| candidate patches | e.g. `00 00 00 00` (float), `00 00 80 3F` (1.0f moon-less), reduced values for low-grav |

Jump-table law fully pinned in `rebuild/PARITY.md` (row
`CBattleEngine::Gravity`): tables at `0x00407520` / `0x00407530`; **index 0**
(`MORPHING_INTO_WALKER`, `BattleEngine.h:32`) takes the `fld [0x005D8BAC]`
arm at `0x00407508`; other states take 0.01f (`0x005D8574`). Refcount of the
0.002f address: **exactly 1 reference** (measured) — this float is private to
gravity. Cleanest gravity knob in the binary, but note it tunes the morph
state, not normal walking (walker falls under the shared 0.01f at `0x005D8574`,
which IS heavily shared — do not patch `0x005D8574` for gravity; see §1.3's
refcount note).

Confidence: **MEASURED** for identity/semantics (PARITY mutation-killed);
**STATIC_ONLY** for any new patched value's feel. Risk: low-medium.
Cheapest verification: morph mid-air in a copied build; compare descent.

### 4.2 Jet friction slow-flight gate — 1.5f threshold

| field | value |
|---|---|
| VA | `0x005D8BD8` (offset `0x001D8BD8`) |
| original | `00 00 c0 3f` = 1.5f |
| candidate patches | lower → easier slow-flight hover band; raise → tighter |

Pinned law: `CBattleEngineJetPart::GetFriction` compares against this at
`0x00411B39` (`fcomp` + `test ah,1`), interpolating between ladder constants
below the gate (`0x005D8CC4`=0.99f, `0x005D8B9C`=0.98f, `0x005D8568`=1.0f,
`0x005D8CC0`=3.0f — all individually patchable too, listed once here rather
than four near-duplicate rows; their addresses carry the same evidence).
Refcount of the 1.5f address: 28 references — SHARED; patching the float may
touch unrelated consumers. Safer targeted form: patch the `fcomp` operand
reference at `0x00411B3B` (4-byte rel-free disp32 `d8 1d d8 8b 5d 00` →
point at a private constant) — recorded as the verification suggestion, not a
separate row.

Confidence: **MEASURED** (law), STATIC_ONLY (any new value). Risk: medium
(shared). Cheapest verification: jet hover stability in a copied build.

### 4.3 Walker water-entry margin — 0.3f selector

| field | value |
|---|---|
| VA | `0x005D8CB4` (offset `0x001D8CB4`) |
| original | `9a 99 99 3e` = 0.3f |
| candidate patches | raise → BE treats shallower water as deep (arms water entry sooner) |

Pinned law: `CBattleEngineWalkerPart::GoingIntoWater` arm selector at
`0x00413ABF` (`fcomp [0x005D8CB4]` on unrounded height; instruction bytes at
`0x413AB8`: `… df e0 f6 c4 41 75 65 …` — the parity row's inclusive-selector
finding). Refcount: 38 references — SHARED.

Confidence: **MEASURED** (law). Risk: medium (shared). Cheapest verification:
walk into progressively deeper water in a copied build.

### 4.4 Jet auto-level manoeuvre threshold — (0.1f)²

| field | value |
|---|---|
| VA | `0x005D8C60` (offset `0x001D8C60`) |
| original | `0b d7 23 3c` = float(0.1f)² ≈ 0.010000001 |
| candidate patches | raise → auto-level engages at higher ground speed |

Pinned law: `CBattleEngineJetPart::AutoLevel` gate `fcomp [0x005D8C60]` at
`0x0041293A` (PARITY row; the classic trap is writing plain 0.01f =
`0ad7233c`, a *different* constant). Refcount: 5 references.

Confidence: **MEASURED** (law). Risk: medium-low. Cheapest verification:
auto-level engagement speed on takeoff.

### 4.5 Weapon charge ceiling — 400.0f

| field | value |
|---|---|
| VA | `0x005DB358` (offset `0x001DB358`) |
| original | `00 00 c8 43` = 400.0f |
| candidate patches | raise → charge keeps accumulating past the cap; lower → faster saturation |

Consumer (byte-read here): `CWeapon__AdvanceChargeProgressIfAnySlotAssigned`
loads `[weapon+0x60]` then `d8 1d 58 b3 5d 00` = `fcomp dword [0x005DB358]`
at `0x0044B640`? No — at `0x00506916` inside `0x005068F0`
(`506910: d9 41 60 | d8 1d 58 b3 5d 00 | df e0 | f6 c4 01 | 74 09`),
i.e. add-if-below-cap exactly as the PARITY charge row describes. Other
referencing sites (measured): `0x450E1D`, `0x451EF2`, `0x4EA67A`, `0x51BB1F`
— five total; treat as shared.

Confidence: **MEASURED** (consumer + PARITY row with mutation kill).
Risk: medium. Cheapest verification: hold charge on Pulse Cannon Pod; watch
charge readout pass previous cap.

### 4.6 Battle Engine max velocity — 35.0f

| field | value |
|---|---|
| VA | `0x005D8BA4` (offset `0x001D8BA4`) |
| original | `00 00 0c 42` = 35.0f |
| candidate patches | raise/lower top speed |

Getter `CBattleEngine::GetMaxVelocity 0x00405EF0` is `d9 05 a4 8b 5d 00 c3`
(`fld [0x005D8BA4]; ret`) — vtable slot 15, SOURCE_INLINE ("returns the
source-declared 35.0f", `cbattleengine-vtable-semantics-2026-08-11.tsv`).
Refcount of the constant address: 6 references (`0x405EF2`,
`0x41660E`, `0x445FDD`, `0x452E58`, `0x486098`, `0x4860AB`) — partially
shared; the getter itself is the proven BE consumer.

Confidence: **STATIC_ONLY** (getter proven; downstream use = velocity clamp
per class contract). Risk: medium-low. Cheapest verification: jet top-speed
run in a copied build.

### 4.7 Event-time divisor pair — GAME_FR 20.0f

| field | value |
|---|---|
| VA | `0x005D857C` (offset `0x001D857C`) |
| original | `00 00 a0 41` = 20.0f |
| candidate patches | must move in lockstep with §1.3 CLOCK_TICK (reciprocal) |

Refcount 74 references — the most-shared constant in this census. Listed to
warn against touching it casually and to pair it with §1.3 if a deliberate
global timescale change is ever attempted.

Confidence: **STATIC_ONLY**. Risk: very high. Cheapest verification: none
cheap — leave alone unless §1.3 changes.

---

## 5. Player resources & damage

### 5.1 God-mode data flag — RETRACTED (BSS)

First-cut rowed `g_bGodModeEnabled` `0x00662AB4` as `00 00 00 00` →
`01 00 00 00`. PE re-parse: that VA is `.data` BSS (`delta 0x40AB4` ≥
raw `0x3F000`). The zeros previously read at file `0x262AB4` are `.rsrc`,
not the flag. File-patching them would corrupt resources and would not
enable god mode. TSV row removed. Runtime path remains the Maladim /
pause-menu toggle plus the now-pinned Damage restore (§5.2).

### 5.2 Damage restoration branch — `CBattleEngine::Damage` mVulnerable check

| field | value |
|---|---|
| function | `0x0040A890` (917 bytes; vtable primary:40) |
| load | `0x0040ABEA`: `8b 86 5c 01 00 00` `mov eax,[esi+0x15C]` |
| test | `0x0040ABF0`: `85 c0` (FPU `fadd`/`fstp` of `[esi+0x604]` follows; flags preserved) |
| jcc | `0x0040ABFE`: `75 1e` `jnz` → skip restore when mVulnerable ≠ 0 |
| restore | `mov` life/shields/energy from the prologue snapshot back to `+0xF8/+0x100/+0xFC` |

Pinned 2026-08-22 against the specimen; matches
`reverse-engineering/game-mechanics/god-mode.md` (the note skipped the
intervening FPU pair). Polarity: zero is invulnerable.

Candidate patches (2-byte jcc):

- `75 1e` → `90 90` — always restore = file-expressible god
- `75 1e` → `EB 1e` — never restore = harden against the flag

Setter sibling: `CUnit::SetVulnerable` `0x00405E30` is
`mov eax,[esp+4]; mov [ecx+0x15C],eax; ret 4` with **zero** direct `E8`
callers (vtable only). `8b 44 24 04` → `33 c0 90 90` forces every
indirect call to write FALSE.

Confidence: **MEASURED** for the jcc identity (god-mode.md live combat
effect + exact bytes). STATIC_ONLY for a file-patched jcc's feel versus
the pause-menu toggle. Risk: low-medium.

### 5.3 Water-death exception — `DeclareInWater` gate

| field | value |
|---|---|
| function | `0x00408150` (97 bytes, SOURCE_BODY) |
| water compare | `fcomp [0x005D8BF0]` (`cd cc 4c be` = −0.2f, 6 refs) then `test ah,0x41` |
| altitude jcc | `0x00408189`: `75 1d` skip death if not below the line |
| mVulnerable | `0x0040818B`: `mov eax,[esi+0x15C]` / `test` / `0x00408193`: `75 09` → death if vulnerable |
| conjunct | `0x00408195`: `mov eax,[0x00662DD0]` (BSS — **not** `0x00662DF4`) / `0x0040819C`: `75 0a` survive if that flag ≠ 0 |
| death | `call [edx+0xC8]` |

Source law (battle-system.md): survive only if `mVulnerable==FALSE` **and**
developer mode. Retail conjunct is the BSS dword at `0x00662DD0` (10
address refs). That flag cannot be file-patched.

Candidate patches:

- `75 0a` → `EB 0a` at `0x0040819C` — once invulnerable, skip the BSS
  conjunct (god survives water)
- `75 1d` → `EB 1d` at `0x00408189` — never take the death call
- −0.2f at `0x005D8BF0` → `00 00 00 00` moves the water line (shared)

Confidence: **STATIC_ONLY** (bytes + source polarity; no copied-runtime
water probe on this card). Risk: medium.

### 5.4 Energy drain scalars (shipped data, not code)

| field | value |
|---|---|
| location | `data/battle engine configurations.dat`, SHA-256 `58722b12…` (1,514 bytes), record 3 "Aquila Prototype" @`0x2d2` |
| values | `mGroundEnergyIncrease 0.05`, `mMinAirEnergyCost 0.005`, `mMaxAirEnergyCost 0.012` (jet drain measured −0.5625…−0.4713 u/s, pair energy-p02) |

These live in shipped data files, NOT the exe — outside this card's
exe-bytes scope, listed because the card names energy explicitly and the
exe-side drain code paths (`SetInfinateEnergy 0x00405F20` stores the flag +
refills from configuration; jet thrust drain interpolates min/max cost) are
pinned enough to know a code-side "no drain" patch would sit in
`JetPart::Move/Thrust` bodies that are mapped but not byte-pinned for this
purpose. See
`game-mechanics/jet-energy-drain-retail-to-core-translation-policy.md` and
`energy-retail-to-core-translation-policy.md`.

Confidence: **SPECULATIVE** as exe rows; the data-file route is the cheap
one. Next instrument: pin the drain `fsub` sites in `JetPart::Move`.

### 5.5 Shield efficiency — configuration-carried

`mShieldEfficiency` (damage→shield multiplier, battle-system.md) is loaded
from the same configurations data (§5.4 posture). Exe side, the Damage body
consumes it; no standalone exe constant is pinned. Not row-tracked beyond
this note — same next instrument as §5.2.

### 5.6 Kill counters — save-side plus one exe clamp

Career kill counters (`CCareer+0x23F4/+0x23F8`, load-clamp ±64) remain
primarily a save-lab surface. The exe clamp's `xor eax,eax` at
`0x00421274` is now TSV-rowed as a hardening/widen option (NOP keeps
out-of-range counters). See §12.6.

### 5.7 Infinite-energy flag — `SetInfinateEnergy` and a drain skip

`CBattleEngine::SetInfinateEnergy` `0x00405F20` (28 B, SOURCE_INLINE,
**zero** direct `E8` callers — vtable slot 85):

```
8b 44 24 04             mov eax, [esp+4]
8b 91 b0 04 00 00       mov edx, [ecx+0x4B0]    ; config
89 81 60 01 00 00       mov [ecx+0x160], eax    ; mInfinateEnergy
d9 42 20                fld [edx+0x20]
d9 99 fc 00 00 00       fstp [ecx+0x0FC]        ; refill energy
c2 04 00                ret 4
```

`8b 44 24 04` → `33 c0 40 90` (eax=1) makes every indirect call enable
the flag and still refill.

Drain skip at `0x004137E0` (walker-range body):
`mov eax,[ecx+0x160]; test eax,eax; 0x004137E8: 75 4e` — `jnz` skips the
following drain arm. `75 4e` → `EB 4e` is file-expressible infinite
energy without the flag. A jet-range sibling at `0x00410CA2`
(`cmp [ecx+0x160],ebp / jnz`) is **not** rowed: polarity depends on
whatever `ebp` holds.

Confidence: **STATIC_ONLY**. Risk: medium. Jet `Move/Thrust` fsub sites
remain a named next instrument (data-file min/max costs stay the cheap
authored route).

---

## 6. Weapons (fire gate, charge cap)

(Charge cap float itself is §4.5.)

### 6.1 Walker weapon active gate

| field | value |
|---|---|
| VA | `0x00414644` (the `je`; test sits at `0x00414642`) |
| original | `74 5f` |
| candidate patch | `EB 5F`: fire proceeds with no active weapon selected |

Law pinned in PARITY (`CBattleEngineWalkerPart::CanWeaponFire`,
gate `mov ecx,[eax+0x9c]` at `0x0041463C`, jet body lacks the displacement).
Sibling `[+0x9c]==0` early-outs now rowed:

| site | VA | original | note |
|---|---|---|---|
| FireWeapon | `0x00413CDE` | `74 07` | after `mov ecx,[eax+0x9c]; test ecx,ecx` |
| ChargeWeapon | `0x00413D10` | `74 52` | after `mov eax,[esi+0x9c]; test eax,eax` |

`GetCurrentWeapon` `0x0040C380` is a mode-3 jet/walker part selector, **not**
an `[+0x9c]` test — first-cut's sibling list over-claimed that body. A
complete "always able to fire" cheat is the three `je`s above.

Confidence: **MEASURED** (identity), STATIC_ONLY (behavioral consequence).
Risk: low-medium (fires with undefined current weapon — could crash on null
weapon record; that is exactly what the je guards). Cheapest verification:
copied build, attempt fire with no weapon selected.

### 6.2 Charge-reload strictness

| field | value |
|---|---|
| function | `TargetProfileContext__CanProceedByTargetRangeGate 0x0050A080` (34 bytes) |
| law | `ReadyToCharge` blocks charge increment until engine time strictly greater than fire-stamped `now + CWeaponReloadTime` (PARITY: `test ah,0x41`) |

The strictness test bytes sit inside this tiny gate; the reload-time source
per-weapon is data (`Mech Pulse Cannon Charged` 0.1 s etc.). Patching the
strict `>` to `>=` buys one 20 Hz sample — negligible; patching reload time
belongs to weapon data files. Recorded as understood-and-declined: no
worthwhile exe byte here. Kept in the TSV as an explicit declined row so the
census shows the decision.

Confidence: **STATIC_ONLY** (declined). Risk: n/a.

---

## 7. Cheat flags

Full mechanism authority: `game-mechanics/cheat-codes.md` (XOR key
"HELP ME!!" @`0x00629A64`, table @`0x00629464`, strstr-on-save-name,
call-site map). All five IsCheatActive call sites byte-verified here:

| call site VA | index | cheat | original bytes |
|---|---|---|---|
| `0x0045D7F4` | 0 | MALLOY (goodies) | `e8 97 7c 00 00` (+ `f7 d8 1b c0` tail) |
| `0x0045D80B` | 5 | lat\xEAte (goodie gating bypass) | `e8 80 7c 00 00` |
| `0x00461A6F` | 1 | TURKEY (all levels) | `e8 1c 3a 00 00` |
| `0x0046F835` | 4 | Aurore (free camera) | `e8 56 5c ff ff` |
| `0x004CE31B` | 3 | Maladim (god UI) | `e8 70 71 f9 ff` |

### 7.1 Force all cheats — `IsCheatActive` early-exit JNZ

| field | value |
|---|---|
| VA | `0x004654A0` (offset `0x000654A0`) |
| original | `75 7A` = `jnz short +0x7a` (skip to strstr path when neither dev-mode nor all-cheats flag set) |
| candidate patch | `EB 7A` = unconditional `jmp` → every caller takes the TRUE early-exit |

Effect boundary already proven by the Dec 2025 investigation: this yields the
TURKEY-like subset only, because goodies-menu/god-toggle/frontend flows also
check `g_bAllCheatesEnabled` directly (§10.2 BSS — cannot file-patch). The
historical "data flag" idea is dead; this code patch is the maximal
file-expressible version.

Confidence: **MEASURED** (bytes; partial-effect claim carries the Dec 2025
runtime observation). Risk: medium. Cheapest verification: campaign level
select shows all missions in a copied build.

### 7.2–7.6 Per-site cheat forcing

Each call-site row above can be NOP'd (×5) to disable that specific cheat
check (hardening) or forced (`B8 01 00 00 00` mov eax,1 replacing the call…
not recommended — the MALLOY site's tail `f7 d8 1b c0`
(`neg eax; sbb eax,eax`) builds the boolean from the return value, so
return-value forcing needs care per site). One representative row is tracked
(TURKEY site, the cleanest: pure call → test → jcc consumer) rather than five
near-duplicates:

| field | value |
|---|---|
| VA | `0x00461A6F` |
| original | `e8 1c 3a 00 00` |
| candidate patch | `B8 01 00 00 00` = `mov eax,1` (force cheat-active) |

Confidence: **STATIC_ONLY** (consumer shape verified for TURKEY site; the
other four sites need the same per-site consumer read before forcing).
Risk: medium.

### 7.3 latete site

`0x0045D80B`: `e8 80 7c 00 00` followed by the same `f7 d8 1b c0` tail as
MALLOY. TSV rows `B8 01 00 00 00` as a candidate; do **not** productize
without a consumer re-read (the tail inverts/extends the boolean). MALLOY
itself stays pointer-only (§9) because the product catalog already owns
`0x0045D7F4`.

### 7.7 God-flag UI gate — Maladim site

| field | value |
|---|---|
| VA | `0x004CE31B` |
| original | `e8 70 71 f9 ff` |
| consumer | `85 c0` / `0f 84 86 00 00 00` (jz skip the Controller Options God line) |
| candidate | `B8 01 00 00 00` — God OFF/ON appears on a normal-named save |

No `neg/sbb` tail here — clean force. Does **not** by itself write
`mVulnerable`; it only unhides the toggle that the Dec 2025 / Mar 2026
tests already showed changes combat damage.

Confidence: **STATIC_ONLY**. Risk: low.

---

## 8. Debug leftovers (console)

### 8.1 Console command registration

`CGame::InitRestartLoop 0x0046C430` registers `Win`/"Win this level"
(name ptr `0x0062BE84`, desc `0x0062BE88`) and (sibling) `Lose` — the
registration stores themselves are patchable strings/pointer pairs (rename,
hide, or repoint commands). Surface noted; individual string edits are
trivial cosmetic rows not itemized.

### 8.2 Dev-mode gate posture

The console/debug-button layer (§2.6–2.8) is reachable in principle through
`ReceiveButtonAction` button IDs 0–14, but the retail invocation route
(how a controller event carries a debug button ID) is not pinned. Until that
route is proven, the honest statement is: console commands exist and are
registered; the retail path to drive them is UNKNOWN_WITH_FALSIFIER
(falsifier: trace a `ReceiveButtonAction` call with button≥11 in a controlled
runtime — Phase 2).

Confidence: **SPECULATIVE** (reachability). This bounds §§2.6–2.8.

---

## 9. Already-cataloged adjacent rows (pointer only)

These live in `patches/catalog/patches.v2.json` (product-owned, contract-
gated) and are listed here ONLY so the census's coverage claim is honest —
they are not re-rowed:

- Goodies gallery display unlock `0x0045D7F4` (overlaps cheat site §7! The
  product row patches the same address with a 9-byte sequence — dependency/
  conflict awareness required if any §7 row were ever productized);
- Free-camera Aurore gate bypass `0x0046F83C` (6-byte NOP just after §7's
  Aurore call site);
- Pause-key default row `0x005144CD`;
- Frontend clear-screen presets, widescreen/windowed/graphics rows,
  free-camera cave/hook family.

## 10. Explicit non-surfaces

### 10.1 Debug-button reachability

See §8.2 — the door exists, the handle is unpinned.

### 10.2 BSS globals (cannot be file-patched)

`.data` VirtualSize `0x3B2614` vs SizeOfRawData `0x3F000`: file-backed
`.data` ends at `0x00661000`. Everything from there to virtual end
`0x009D4614` is BSS. A flat `VA − 0x400000` in that band hits `.rsrc`
raw (from file `0x261000`) or EOF — that is how first-cut mis-rowed
`g_bGodModeEnabled`.

Confirmed BSS (not file-patchable):

| VA | label |
|---|---|
| `0x00662AB4` | `g_bGodModeEnabled` (1 address ref) |
| `0x00662DD0` | water-death conjunct (10 refs) |
| `0x00662DF4` | claimed `g_bDevModeEnabled`; file-flat bytes are UTF-16 `scen` in `.rsrc` (39 refs) |
| `0x00679EC1` | `g_bAllCheatsEnabled` |
| `0x00672E20` | FillOut ranking destination |
| `0x0089C800` | script pause stop-flag |
| `0x008A9AC0` | `g_GameState` |

Any "patch" of those file offsets is a no-op or resource corruption.

### 10.3 Runtime-populated data despite a file address

The IScript native registry records cited at `0x0064D020`/`0x0064D060`/
`0x0064E8A0` read **file-zero** (verified here) — populated at runtime.
Patching those file bytes does nothing. (Their citations remain valid as
*runtime* registry documentation.)

### 10.4 Unit AI "think" loops

No distinct per-unit AI tick function surfaced in the evidence corpus — unit
behavior runs through the CThing/CActor virtual update chain dispatched from
the MainLoop/AdvanceTime heartbeats (§3). The maximal freeze primitives ARE
§3.1–§3.3; finer granularity (per-squad aggression) would require pinning the
virtual dispatch bodies, which is Phase-2-scale RE beyond this census.
Named honestly as a coverage limit, not silently omitted.

### 10.5 Spawn tables and caps

Unit spawn composition comes from authored level data (`100_res_PC.aya`
etc.), not exe tables — the exe-side lever is the FillOut/objective surface
(§2) plus data-file editing (different lane). The 35-base-things census
(`[0x0085515C]`=35 on first play) is measurement, not a patch point.
No exe spawn-table rows exist to write; stated to close the card's coverage
ask honestly.

---

## 11. End-of-level ranking

`CGame::FillOutEndLevelData` `0x0046D470` (920 B). Sole direct `E8` caller
measured at `0x0046E1CB` (`RestartLoopRunLevel`). Ranking dword is written
to BSS `0x00672E20` — patch the **stores**, not the destination.

### 11.1 Score-time arm

| site | VA | original | role |
|---|---|---|---|
| below-D `jl` | `0x0046D724` | `7c 4c` | taken when fistp'd score < D |
| store 0 | `0x0046D772` | `c7 05 20 2e 67 00 00 00 00 00` | ranking = 0 |
| store 0.001 | `0x0046D791` | `c7 05 20 2e 67 00 6f 12 83 3a` | exact-D band |
| store 1.0 | `0x0046D709` | `c7 05 20 2e 67 00 00 00 80 3f` | S-score equality (already 1.0; not re-rowed) |

PARITY mutation-kills the below-D / exact-D law. Candidate: NOP the `jl`,
or rewrite the 0 / 0.001 stores to `00 00 80 3f` (force S).

Confidence: **MEASURED**. Risk: medium (changes career grade / goodie
unlocks via §12.4).

### 11.2 Secondary ranking clamp

After the arm, a nonzero secondary count runs
`CEndLevelData__IsAllSecondaryObjectivesComplete` `0x004496E0`. Compare
constants `0x005D8C40` (0.4f, **31 refs**, also GetRadius SP) and
`0x005D8BB8` (0.6f, 21 refs) are shared — do not patch those floats.
The **stores** are private immediates:

- floor `0x0046D7D9`: `c7 05 20 2e 67 00 cd cc cc 3e` (0.4f)
- ceil `0x0046D7F7`: `c7 05 20 2e 67 00 9a 99 19 3f` (0.6f)

Level 100 authors zero secondaries so this clamp does not run there.

Confidence: **MEASURED** (FillOut note + specimen). Risk: low-medium.

### 11.3 TF_DYING snapshot

`0x0046D4D1`: `test byte [eax+0x2c],4` / `0x0046D4D5`: `75 08` skips the
store-1 when the base-thing is dying. NOP the `jne` to keep dying
base-things as present. PARITY already mutation-kills the store-0 path.

Confidence: **STATIC_ONLY**. Risk: medium.

---

## 12. Career graph / goodies / kills

### 12.1 `CCareer::Update` Won-only gate

`0x0041BD00`: `mov eax,[0x00672E1C]` / `cmp eax,5` at `0x0041BD06` /
`jnz` at **`0x0041BD0C`** (`0f 85 c7 00 00 00`) after `push edi; mov esi,ecx`.
Lost is 4; the jnz skips the 32-dword copy. NOP the jnz to apply the
update on Lost as well. Sole direct caller: `0x00466315`.

Confidence: **MEASURED**. Risk: high (Lost can complete career nodes).

### 12.2 `CCareer::SetSlot` 256-bit guard

`0x004214EB`: `cmp eax,0x100` / `jge`. Store backing is 1024 bits.
`3d 00 01 00 00` → `3d 00 04 00 00`. Sole `E8`: `0x00533945`
(`IScript::SetSlotSave`).

Confidence: **MEASURED**. Risk: low.

### 12.3 `UpdateThingsKilled` world-100 skip

`cmp eax,0x64` at `0x0041C188`; **`je` at `0x0041C18E`**
(`0f 84 a6 00 00 00`). NOP to accumulate Level 100 kills into career.

Confidence: **MEASURED**. Risk: low-medium.

### 12.4 `UpdateGoodieStates` GRADE thresholds

Re-read: `0x0041DE68` `6a 43` (`'C'`), `0x0041EA4F` `6a 42` (`'B'`),
`0x0041F70E` `6a 41` (`'A'`). Pushing `'E'` (`6a 45`) loosens each band
to any completed letter. Incomplete GRADE still writes `'E'` at
`0x00421499` (`b0 45`) — do not confuse that store with these thresholds.

Confidence: **STATIC_ONLY**. Risk: medium (unlocks goodies 78/121/164 on
an E-grade win).

### 12.5 `ConfirmedKill` allegiance gate

32-byte body `0x0040A560`. `cmp dword [eax+0x138],1` then `0x0040A56B`
`75 10` skips `0x004D30D0`. NOP the jnz to count every allegiance.
One inbound `E8` at `0x0040A578` (already inside this body).

Confidence: **STATIC_ONLY**. Risk: medium.

### 12.6 Load clamp `xor eax,eax`

`0x0042126A` `cmp eax,-0x40` / `0x0042126F` `cmp eax,0x40` /
`0x00421274` `33 c0`. NOP the xor to keep out-of-range counters.

Confidence: **STATIC_ONLY**. Risk: low.

---

## 13. Flight / script enable

### 13.1 `DisableFlightMode` store

`0x0040DCC0`: `mov eax,[ecx+0x260]; mov [ecx+0x58c],0; cmp eax,3; …`.
Store at `0x0040DCC6` (`c7 81 8c 05 00 00 00 00 00 00`). Sole `E8`:
`0x00535099` (`IScript::DisableFlightMode`). NOP the store: scripts
cannot clear the flight flag. Twin enable store `0x0040DCB0` already
writes 1 — the lever is the disable / the wrapper gate.

Confidence: **MEASURED** (PARITY Level 100 flight flag). Risk: medium.

### 13.2 `IScript::EnableFlightMode` type-bit gate

`0x00535070`: `mov ecx,[ecx+0x10]; test [ecx+0x34],8; 0x00535077: 74 05`
skips `call 0x0040DCB0`. NOP the `jz` to enable flight on things that
lack bit 3.

Confidence: **STATIC_ONLY**. Risk: medium.

### 13.3 `IScript::AddScore`

`0x005343CB`: `01 05 8c 9b 8a 00` = `add [0x008A9B8C],eax` (`CGame+0xf4`).
Zero direct `E8` (native registry). NOP: scripts cannot increment mScore.

Confidence: **MEASURED**. Risk: low.

### 13.4 `IScript::SetVulnerable`

Ghidra `NO_FUNCTION` at `0x00535F70` is stale — 32-byte native is live:
get bool, `and eax,0xff` at **`0x00535F82`**, `call [edi+0xE0]`.
`25 ff 00 00 00` → `33 c0 90 90 90` forces every scripted call to pass
FALSE (invulnerable). Distinct from player god (§5.2).

Confidence: **STATIC_ONLY**. Risk: medium.

---

## 14. Input / analogue

`CPCController::GetAnalogueLeftX` `fild` at `0x0051465E` then
`fmul [0x005DC6E4]` at `0x00514660`. Dword `6f 12 83 3a` = 0.001f.
`0.36f` occurs **zero** times (source dead-zone never shipped). Seven
refs of the constant: `0x004B865B`, `0x004B8763`, `0x004D63A3`,
`0x00514662` (LeftX), `0x00514693` (sibling axis), `0x005146C3`
(sibling axis), `0x00515A63`. Patching the float scales all seven.

Confidence: **MEASURED** (PARITY analogue law). Risk: medium.

Mouse-look helper `0x00407540` early-outs on BSS `[0x00662DF4]` — not a
file surface. Product pause-key / free-camera rows stay in §9.

---

## 15. Collision / camera knobs

### 15.1 `COfGHeight`

Getter `0x0040DFA0`: `d9 05 78 8c 5d 00 c3` = `fld [0x005D8C78]; ret`.
Dword `33 33 f3 3f` = 1.9f. **Sole ref** — clean chassis knob.

Confidence: **STATIC_ONLY** (vtable SOURCE_BODY; feel unprobed). Risk:
low-medium.

### 15.2 Movie-camera zoom

`CMovieCamera::GetZoom` `fmul [0x005D9338]` at `0x0041A681` then
`fmul [0x005D85EC]` (0.5f, **409 refs** — do not touch). `0x005D9338` =
`61 0b 36 3c` = 1/90, **sole ref**. Example: 1/45 doubles FOV.

Confidence: **MEASURED**. Risk: low.

### 4.8 leftover / 15.3 friction rungs

First-cut named the ladder constants without TSV rows. Now rowed:

| VA | value | refs |
|---|---|---|
| `0x005D8CC4` | 0.99f | 11 |
| `0x005D8B9C` | 0.98f | 5 |
| `0x005D8568` | 1.0f | **941 — do not patch** |
| `0x005D8CC0` | 3.0f | 54 — not rowed |
| `0x005D8574` | 0.01f walker gravity | 70 — still not a gravity knob |

Hostile-env 5.0f `0x005D85D8` has 65 refs — listed only as a warning.
GetRadius SP 0.4f shares `0x005D8C40` with the ranking compare (31 refs).

---

## 16. Script objective / pause flags

### 16.1 Objective bit on the thing

Callee `0x004F3970`. `0x004F398E`: `80 4e 2c 20` `or [esi+0x2c],0x20`.
`0x004F39A5`: `80 66 2c df` `and [esi+0x2c],0xdf`. PARITY Level 100
`SetObjective` / `UnsetObjective`. NOP either side.

Confidence: **MEASURED**. Risk: medium / low-medium.

### 16.2 Script pause stop-flag

`IScript::Pause` `0x00537D55` and `PlayCharMessageWait` `0x005376F9` both
`mov dword [0x0089C800],1`. Destination is BSS; the **stores** are in
`.text`. NOP at `0x00537D55` is rowed (Pause). Twin at `0x005376F9` is
the same 10-byte store — not duplicated. Raising that flag is how
wait-natives stop the VM; NOPing it can desync authored scripts.

Confidence: **STATIC_ONLY**. Risk: high.

---

## Verification protocol (for any row promoted to Phase 2)

1. Copy, never in-place: safe-copy through the app; pristine specimen stays
   read-only; installed game untouched.
2. Byte preconditions: verify original bytes at offset before apply (the
   AppCore engine already refuses mismatches for catalog rows). TSV
   `original_bytes` for this census were specimen-compared at write time.
3. One row per probe; screenshot-or-timer evidence; revert via full-file
   backup restore.
4. A row graduates STATIC_ONLY → MEASURED only with the named cheapest
   verification observed on the copied binary.
5. Never file-patch a VA whose section map is BSS (see PE-MAPPING.md).

## Row inventory

TSV: **70 data rows** (68 unique VAs). First-cut 34 minus retracted BSS
god-flag, plus pinned Damage/water/energy, fire-gate siblings, Maladim /
latete, FillOut / career / flight / analogue / COfG / zoom / friction /
objective / pause.

Confidence histogram: **MEASURED 22 / STATIC_ONLY 45 / SPECULATIVE 3**.

First-cut corrections landed here, not in `rebuild/**`:

- won-countdown imm is `0x0046F33D`, not `0x0046F33B` (ModRM) or `0x0046F338`
- lost-countdown file offset is `0x0006F4A8`, not `0x000F4A8`
- building ApplyDamage offset is `0x00017A16`, not `0x0007A16`
- `g_bGodModeEnabled` is BSS; first-cut file row retracted
- water conjunct is `[0x00662DD0]`, not `0x00662DF4`

Coverage limits that stay honest: no per-unit AI tick, no exe spawn
tables, debug-button retail invocation unpinned, jet energy `fsub` sites
unpinned, IScript natives beyond the rowed set not exhausted.
