# Patch-surface census — maximal patchable sites (static, pristine-only)

Status: active — static census, Phase 2 runtime probes are a separate card
Last updated: 2026-08-22
Summary: first cut `t_7b48b14a`, then `t_14fcbbed`, `t_17fa180d` (jet drain /
debug-button door / IScript mutators), then `t_120c3e1b` (config+0x8/+0xc
named; IScript getters / camera / weather / message natives), then
`t_94b70425` (remaining Initialise slots named; leftover IScript
position / script / HUD / PlayCutscene one-instruction rows).
Evidence: MEASURED — every non-unknown TSV `original_bytes` compared to the
named specimen at write time; PE section table re-parsed; first-cut BSS
god-flag row retracted. `t_17fa180d` re-read JetPart::Move, SendButtonAction,
and the 144-native handler heads. `t_120c3e1b` re-read those TSV bytes again
and the getter / camera / weather / message heads plus
`CBattleEngineData::Initialise` / `LoadFromMemBuffer` from the same specimen.
`t_94b70425` re-read those TSV bytes again and the leftover IScript heads
plus the rest of Initialise / the versioned Load walks.
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
- TSV `original_bytes` for every non-`unknown-*` / non-`none-*` row were
  compared to the specimen in the `t_14fcbbed` writer, again in the
  `t_17fa180d` writer, again in the `t_120c3e1b` writer, and again in the
  `t_94b70425` writer and refused on mismatch.
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
| 2 | Instant win / lose | [§2](#2-instant-win--lose) | WIN/LOSE BSS conjunct now pinned; mapping IDs still BSS |
| 3 | AI freeze (named tick call sites) | [§3](#3-ai-freeze-named-tick-call-sites) | per-unit think still absent; SetAIState is a poke |
| 4 | Physics constants | [§4](#4-physics-constants) | + friction rungs, COfG, zoom, water line |
| 5 | Player resources & damage | [§5](#5-player-resources--damage) | Jet drain `fsubr` now pinned |
| 6 | Weapons (fire gate, charge cap) | [§6](#6-weapons-fire-gate-charge-cap) | + FireWeapon/ChargeWeapon siblings |
| 7 | Cheat flags | [§7](#7-cheat-flags) | + Maladim / latete call sites |
| 8 | Debug leftovers (console) | [§8](#8-debug-leftovers-console) | SendButtonAction door pinned; key→id still BSS |
| 9 | Already-cataloged adjacent rows (pointer only) | [§9](#9-already-cataloged-adjacent-rows-pointer-only) | — |
| 10 | Explicit non-surfaces | [§10](#10-explicit-non-surfaces) | BSS list expanded |
| 11 | End-of-level ranking | [§11](#11-end-of-level-ranking) | FillOut stores |
| 12 | Career graph / goodies / kills | [§12](#12-career-graph--goodies--kills) | Update / SetSlot / GRADE |
| 13 | Flight / script enable | [§13](#13-flight--script-enable) | DisableFlight NOP, AddScore, SetVulnerable |
| 14 | Input / analogue | [§14](#14-input--analogue) | 0.001f scale |
| 15 | Collision / camera knobs | [§15](#15-collision--camera-knobs) | COfG, movie zoom |
| 16 | Script objective / pause flags | [§16](#16-script-objective--pause-flags) | or/and +0x2c, stop-flag + Wait twins |
| 17 | IScript mutators (beyond the first-cut set) | [§17](#17-iscript-mutators-beyond-the-first-cut-set) | + Launch / Teleport / SetPos / SetScript / segment / variables / PostEvent |
| 18 | IScript getters / predicates | [§18](#18-iscript-getters--predicates) | + GetNumber / GetSquad / GetTarget / Spawners* / IsA |
| 19 | IScript camera | [§19](#19-iscript-camera) | GotoPlayer / ToggleCockpit / disable 3-/4-point pan |
| 20 | Weather | [§20](#20-weather) | Rain/snow/lightning fstp + init stores; wind X |
| 21 | IScript messages / wait | [§21](#21-iscript-messages--wait) | Wait-flag twins; SwitchMessages; PlayChar insert; PlayCutscene call |
| 22 | HUD highlight | [§22](#22-hud-highlight) | Highlight/UnHighlight stores; dest is BSS |

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
| jump-table slot | `[11]` at `0x0046FAD0` = `45 f9 46 00` → `0x0046F945` |
| arm head | `0x0046F945`: `83 3d d0 2d 66 00 01` `cmp dword [0x00662DD0], 1` |
| jcc | `0x0046F94C`: `0f 85 48 01 00 00` `jne` → skip the whole arm |
| candidate | NOP×6 the jne — WIN proceeds without the BSS flag |

Jump table at `0x0046FAA4` (15 dwords) was re-read 2026-08-22 and matches
`CGame__ReceiveButtonAction.md` exactly. The WIN arm is **not** an unknown
target: it first requires `[0x00662DD0]==1` (the same BSS conjunct as
water-death, §5.3 / §10.2). That flag cannot be file-patched; the **jcc**
can. After the conjunct the arm randomizes `mScore` in
`[mDGradeScore, mSGradeScore)` and falls into the win flow.

Getting button id 11 into this function is a separate door (§8.3). No
file-backed mapping row emitting ids 0–14 was found; the 47-row table at
`0x008892DC` is BSS.

Confidence: **STATIC_ONLY** (bytes + jump table + BSS conjunct). Risk:
medium (still needs a mapping that emits 11). Cheapest verification: a
copied build whose mapping emits 11, with the BSS flag left 0.

### 2.7 Debug-button lose — `BUTTON_LOOSE_LEVEL` arm

| field | value |
|---|---|
| jump-table slot | `[12]` at `0x0046FAD4` = `39 fa 46 00` → `0x0046FA39` |
| arm head | same `cmp dword [0x00662DD0], 1` |
| jcc | `0x0046FA40`: `75 58` `jnz` skip |
| extra | `cmp [esi+0x28], 3` / `jl` skip — still requires PLAYING-or-later |

Candidate: `75 58` → `EB 58` skips only the BSS conjunct (state gate
remains). Ends in `DeclareLevelLost` at `0x0046FA7C`.

Confidence: **STATIC_ONLY**. Same mapping-id caveat as §2.6.

### 2.8 Complete-all-objectives — `BUTTON_COMPLETE_ALL_OBJECTIVES` arm

| field | value |
|---|---|
| jump-table slot | `[14]` at `0x0046FADC` = `f3 f9 46 00` → `0x0046F9F3` |
| head | `push 0x0062C1DC` / `call CConsole::Printf` ("Completing all Objectives") |
| store seed | `0x0046FA0F`: `bd 01 00 00 00` `mov ebp, 1` |
| stores | loop of 10: `mov [eax], ebp` / `mov [eax+4], edx` (`edx=10`) at `this+0x4c` |

No BSS conjunct on this arm. Candidate: `mov ebp, 1` → `mov ebp, 0`
makes the ten primary-array stores write 0. The first-cut "stores unpinned"
hole is closed.

Confidence: **STATIC_ONLY**. Same mapping-id caveat (button 14).

Related predicate rows already carried elsewhere: the secondary-objective
ranking clamp lives in `FillOutEndLevelData` (see §9) and the
`CCareerNode` complete/link laws are in PARITY.md — those govern what a *win
is worth*, not whether it fires. Scripted complete/fail stores are §17.7.

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
exe-bytes scope, listed because the card names energy explicitly. The
exe drain path is now pinned in §5.8; the data-file min/max costs remain
the cheap authored route for a *value* change.

Confidence: data-file route is the cheap one; exe `fsub` is no longer
the next instrument.

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
energy without the flag. The jet sibling is no longer "ebp-unknown":
see §5.8.

Confidence: **STATIC_ONLY**. Risk: medium.

### 5.8 Jet energy drain — `CBattleEngineJetPart::Move`

Body `0x00410C50`–`0x004114CA` (2171 B, SHA-256 `0de35d19…7484`) re-read
from the named specimen. Prologue `xor ebp, ebp` at `0x00410C5A` — `ebp`
is **0** for the whole Move. That closes the first-cut refusal of
`0x00410CA2`.

| site | VA | bytes | role |
|---|---|---|---|
| flag test | `0x00410CA2` | `39 a9 60 01 00 00` | `cmp [ecx+0x160], ebp` (`ecx` = `[ebx+0x18]` = BE) |
| skip drain | `0x00410CA8` | `75 50` | `jnz` → `0x00410CFA` when `mInfinateEnergy != 0` |
| zero-energy skip | `0x00410CBB` | `75 3d` | `jnz` after `fcomp [0x005D856C]` (0.0f) |
| lerp | `0x00410CBD`… | `fld [config+0xc]` / `fld [config+0x8]` / `fsub st(1)` / `fmul [ebx+0x20]` / `fadd st(1)` | `config = [BE+0x4B0]`; `[JetPart+0x20]` is the interpolant |
| store | `0x00410CD0` | `d8 a9 fc 00 00 00` `fsubr [ecx+0xfc]` then `fstp [ecx+0xfc]` | `energy := energy − lerp` |
| floor | `0x00410CF4` | `89 a9 fc 00 00 00` | `mov [ecx+0xfc], ebp` when the post-drain compare is `< 0` |

`[config+0x8]` is **`mMaxAirEnergyCost`**. `[config+0xc]` is
**`mMinAirEnergyCost`**. `CBattleEngineData::Initialise` `0x0040F590`
writes the Stuart-source defaults there (`0x0040F824`
`mov [ebp+0xc], 0x3dcccccd` = 0.1f; `0x0040F82B`
`mov [ebp+8], 0x3e99999a` = 0.3f). The same function writes the rest
of the constructor map below. `LoadFromMemBuffer` `0x0040F980` does
**not** call Initialise — it frees via `0x0040F890` then reads the
dat. Shipped profiles therefore overwrite these immediates. Do **not**
TSV-row the Initialise stores as value cheats; the cheap value route
is still the dat (§5.4). The names are the point of this cut.

| offset | Initialise store | value | name | Load |
|---|---|---|---|---|
| `+0x00` | `0x0040F835` `00 00 f0 40` | 7.5f | `mMaxAirVelocity` | unversioned prefix |
| `+0x04` | `0x0040F83C` `00 00 a0 40` | 5.0f | `mMinAirVelocity` | Initialise-named; versioned walk not re-opened |
| `+0x08` | `0x0040F82B` `9a 99 99 3e` | 0.3f | `mMaxAirEnergyCost` | unversioned prefix |
| `+0x0c` | `0x0040F824` `cd cc cc 3d` | 0.1f | `mMinAirEnergyCost` | format `> 7` (prior cut) |
| `+0x10` | `0x0040F843` `00 00 80 40` | 4.0f | `mGroundVelocity` | unversioned prefix |
| `+0x14` | `0x0040F84A` `00 00 00 40` | 2.0f | `mAirTurnRate` | unversioned prefix |
| `+0x18` | `0x0040F851` `00 00 c0 3f` | 1.5f | `mGroundTurnRate` | unversioned prefix |
| `+0x1c` | `0x0040F80F` `00 00 a0 41` | 20.0f | `mLife` | unversioned prefix |
| `+0x20` | `0x0040F816` `00 00 20 40` | 2.5f | `mEnergy` | unversioned prefix |
| `+0x24` | `0x0040F858` `00 00 b4 42` | 90.0f | `mShieldEfficiency` | format `> 1` at `0x0040FD0D` |
| `+0x28` | `0x0040F81D` `0a d7 23 3c` | 0.01f | `mGroundEnergyIncrease` | unversioned prefix |
| `+0x2c` | `0x0040F832` from eax=1.0f | 1.0f | `mMinTransformEnergy` | unversioned prefix |
| `+0x30` | `0x0040F85F` `66 66 66 3f` | 0.9f | `mWalkFriction` | Initialise-named |
| `+0x34` | `0x0040F866` `9a 99 19 3e` | 0.15f | `mMaxWalkVelocity` | Initialise-named |
| `+0x38` | `0x0040F86D` from eax=1.0f | 1.0f | `mRollEnergyCost` | Initialise-named |
| `+0x3c` | `0x0040F870` from eax=1.0f | 1.0f | `mLoopEnergyCost` | Initialise-named |
| `+0x70`.. | store-heat loop `0x0040F74E` | 0 | `mStoreHeat[0..5]` | — |
| `+0x88` | loop `0x0040F751` `00 00 7a 44` | 1000.0f | `mStoreValue[0..5]` | — |
| `+0xa0` | `0x0040F87D` from ebx=0 | 0 | `mStealth` | format `> 2` at `0x0040FD21` |
| `+0xa4` | `0x0040F873` | 1 | `mLanguageName` | — |
| `+0xa8` | earlier alloc | `"Standard"` | `mConfigurationName` | format `> 4` string at `0x0040FCA9` |

The layout candidate that starts `mLife` at `+0x1c` is still right;
`+0x00..+0x18` sit *before* `mLife`. Format `< 8` still falls back to
`mov [ebp+0xc], 0x3ba3d70a` (0.005f) and `mov [ebp+8], 0x3c75c28f`
(0.015f). The lerp identity is: cost =
`mMinAirEnergyCost + [JetPart+0x20] * (mMaxAirEnergyCost − mMinAirEnergyCost)`.
The shipped 0.005 / 0.012 values remain the data-file route for a
*value* change (§5.4); the exe lerp operands are now named.

A later `fsub` at `0x00410E3A` interpolates `[cfg+0]` / `[cfg+4]` into a
direction/speed helper (`fsqrt` of a 3-vector). That is **not** an energy
store.

Candidates:

- `75 50` → `EB 50` at `0x00410CA8` — always skip the drain (file-expressible
  infinite jet energy; no flag required)
- NOP the 12-byte `fsubr`+`fstp` at `0x00410CD0` — energy is never written
  even if the flag test is taken

Confidence: **STATIC_ONLY** (bytes + `ebp==0` + store identity). Risk:
medium. Cheapest verification: copied jet; energy HUD under thrust.

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

First-cut left the retail route to `ReceiveButtonAction` unpinned. It is
now pinned; the remaining hole is the **key → button-id** binding, not
the door.

### 8.3 How a debug button id reaches `CGame::ReceiveButtonAction`

Sole `.text` `E8` to `0x0046F7E0`: `0x0042E59D` inside
`CController::SendButtonAction` `0x0042E4D0` (312 B,
`controller-shared-semantics-2026-08-11.md`). `CPlayer::ReceiveButtonAction`
`0x004D3110` has **zero** direct `E8`/`E9` (vtable only) and handles
`BUTTON_PAUSE` (56), not ids 0–14.

Inside `SendButtonAction`, after the three virtual-button words are ORed:

| site | bytes | law |
|---|---|---|
| `0x0042E581` | `83 fb 10` | `cmp ebx, 0x10` |
| `0x0042E584` | `7d 36` | `jge` → ordinary (player) path. Ids **0–15** stay on the CGame path |
| `0x0042E58A` | `ff 52 14` | `call [edi+0x14]` on the current target |
| `0x0042E58F` | `74 17` | `je` skip CGame if that vfunc returns 0 |
| `0x0042E59D` | `e8 3e 12 04 00` | `call CGame::ReceiveButtonAction` (`this=0x008A9A98`) |

DoMappings' 13 call sites all push the **runtime** action id from the
current 32-byte mapping row (`[row+0x04]`), except the dual-Shift site
at `0x0042E31E` which pushes immediate `0x2D`
(`BUTTON_FRONTEND_CHEAT`) — not a debug id. The 47-row table base
`0x008892D8` / view `0x008892DC` is BSS (§10.2). No file-backed
template for those 47 action ids was found in this slice.

Candidates (both high-consequence):

- `7d 36` → `90 90` — **every** action id, including fire/morph, is
  offered to CGame's 0–14 switch. Recorded so the door is named, not
  as a product cheat.
- `74 17` → `90 90` — still require id `< 16`, but call CGame even when
  the target vfunc+0x14 returns 0.

Confidence: **STATIC_ONLY**. The code path is pinned. Whether any of the
47 retail rows emits ids 0–14 is still a runtime / initializer question
(prior diagnostics never saw V-key god fire `ReceiveButtonAction`).

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

See §8.3 — the door and the `<16` gate are pinned. The handle (a mapping
row that emits ids 0–14) is still BSS. WIN/LOSE also require
`[0x00662DD0]==1` (§2.6–2.7).

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
| `0x008A9A98` | `CGame` singleton (`SetPlayerLives` `this`; RBA `this`) |
| `0x008A9ADC` | primary-objective array (script Complete/Failed) |
| `0x008A9B2C` | secondary-objective array |
| `0x00662560` | `SetGoodieState` dword table |
| `0x00662564` | `GetGoodieState` view of the same table (one-based) |
| `0x008892D8` / `0x008892DC` | 47-row mapping table (action id at `+0x04`) |
| `0x008A9D3C` | player-camera / `GetPlayer` slot table |
| `0x008A9D84` | MessageBox singleton (`SwitchMessages*`) |
| `0x008A9D90` | `AddHelpMessage` singleton |
| `0x00672FD0` | `GameTime` source |
| `0x006FBDFC` | `GetWaterHeight` source |
| `0x008AA51C` | `HighlightHudPart` dword table |
| `0x008A9D9C` | `Rand` / `GetFloatRand` RNG object |
| `0x006FADC8` | `GetMapHeight` world |
| `0x008551C0` / `0x00855228` | `GetNumUnits` allegiance tables |
| `0x00855090` | `InitVariable` / `PlayCutscene` lookup `this` |
| `0x00672FC8` | `PostEvent` / `Shutdown` event-manager `this` |

Any "patch" of those file offsets is a no-op or resource corruption.

### 10.3 Runtime-populated data despite a file address

The IScript native registry records cited at `0x0064D020`/`0x0064D060`/
`0x0064E8A0` read **file-zero** (verified here) — populated at runtime.
Patching those file bytes does nothing. (Their citations remain valid as
*runtime* registry documentation.)

### 10.4 Unit AI "think" loops

No distinct per-unit AI tick function surfaced. Unit behavior runs
through the CThing/CActor virtual update chain dispatched from the
MainLoop/AdvanceTime heartbeats (§3). `IScript::SetAIState` (`0x005361A0`)
is a one-shot `call [thing.vtable+0xd8]` with a script int — a poke, not
a tick. The maximal freeze primitives remain §3.1–§3.3. Named honestly
as a coverage limit.

### 10.5 Spawn tables and caps

Unit spawn composition comes from authored level data (`100_res_PC.aya`
etc.), not exe tables. `IScript::SpawnThing` `0x00536CD0` is a large
native (unboxes four script args, then a long world-spawn body) — not a
table. `IScript::SetSpeed` is a 3-byte `ret 0xc` no-op (§17.9). The
35-base-things census (`[0x0085515C]`=35 on first play) is measurement,
not a patch point. No exe spawn-table rows exist to write.

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

`IScript::Pause` `0x00537D55`, `PlayCharMessageWait` `0x005376F9`,
`PlayPCharMessageWait` `0x005379F5`, and `PlayAnimationWait`
`0x0053531C` all `mov dword [0x0089C800],1` (four sites, MEASURED
needle scan). Destination is BSS; the **stores** are in `.text`.
NOP at `0x00537D55` was already rowed (Pause). This cut rows the
three Wait twins. Raising that flag is how wait-natives stop the
VM; NOPing it can desync authored scripts.

Confidence: **STATIC_ONLY**. Risk: high.

---

## 17. IScript mutators (beyond the first-cut set)

The 144-entry registry
(`ghidra-functions.md` Appendix A, base `0x0064CE20`, stride `0x40`)
is name/handler evidence. First-cut rowed LevelWon/Lost/LostString,
Enable/DisableFlight, AddScore, SetVulnerable, Pause, SetObjective,
and SetSlotSave's callee. `t_17fa180d` pinned the other
**state-writing** natives that have a one-instruction file lever.
This cut adds the leftover mutators below and opens §18–§21 for
getters, camera, weather, and message/wait helpers.

Most mutators share a type-bit gate: `test byte [thing+0x34], 0x10` /
`je skip`. NOP the `je` to run the write on things that lack bit 4.
`EnableFlightMode` already uses bit 3 (`test …, 8`) the same way (§13.2).

### 17.1 Die / HalfDestroy

`IScript::Die` `0x00535CD0` (40 B): `AddEvent_AtTime(0x7d2, [this+0x10],
NEXT_FRAME)` — `START_DIE_PROCESS` on the attached thing. Sole useful
lever is the call at `0x00535CF2` (`e8 79 56 f1 ff`). NOP×5: scripts
cannot schedule death. Zero inbound `E8` (native 13).

`IScript::HalfDestroy` `0x00534370`: type-bit then `call 0x004F9430`
(sole image `E8` of that helper). `0x00534377` `74 05` → `EB 05` never
calls.

### 17.2 Health / segment health / segment vulnerable

`SetHealth` `0x00535C10`: type-bit `je` at **`0x00535C18`** (`74 27`),
then `vtable+0x34` unbox, `fmul [[thing+0x164]+0xc0]`, `fstp [thing+0xf8]`.
NOP the `je` to write the life-like float without bit 4.

`SetAllSegmentsHealth` `0x00535500`: same type-bit at `0x00535508`
(`74 20`), then `call 0x00444580` on `[thing+0x178]`.

`SetAllSegmentsVulnerable` `0x00534390`: type-bit, unbox bool,
`and eax, 0xff` at **`0x005343AF`**, `call 0x00444620`. Same force-FALSE
shape as `SetVulnerable` (§13.4): `25 ff 00 00 00` → `33 c0 90 90 90`.

### 17.3 Enable / Disable weapon

Twins, 38 B each. Type-bit `je` then `vtable+0x38` (int unbox) then
`call [thing.vtable+0x198]` / `+0x19c`.

| native | je VA | original |
|---|---|---|
| EnableWeapon | `0x00534FBA` | `74 19` |
| DisableWeapon | `0x00534FEA` | `74 19` |

### 17.4 Enable / Disable spawner

Same type-bit; helpers `0x004FE390` / `0x004FE3F0` are **sole** `E8`
callers from these natives.

| native | je VA | original |
|---|---|---|
| EnableSpawner | `0x0053501A` | `74 14` |
| DisableSpawner | `0x0053504A` | `74 14` |

This is the exe-side on/off for an already-placed spawner. It is **not**
an exe spawn table (§10.5).

### 17.5 SetAllegiance / SetStealth

| native | je VA | original | tail |
|---|---|---|---|
| SetAllegiance | `0x0053556A` | `74 14` | `call 0x004FD830` (3 image `E8`) |
| SetStealth | `0x0053553A` | `74 1c` | `vtable+0x34` float then `call [+0x1c8]` |

### 17.6 SetPlayerLives

`0x005338A0` unboxes two ints and `call 0x00472620`
(`CGame::SetPlayerLives`, sole `E8`) with `this=0x008A9A98`. The callee
writes `[this+0x290]` when arg0==1 and `[this+0x294]` when arg0==2.
Destinations are BSS; NOP the call at `0x005338BD`.

### 17.7 Objective complete / fail stores

Four 41-byte twins. Unbox two ints; `lea eax, [eax*8 + base]`;
`mov [eax+4], edi`; `mov dword [eax], imm`.

| native | store VA | original | base |
|---|---|---|---|
| PrimaryObjectiveComplete | `0x00534402` | `c7 00 01 00 00 00` | `0x008A9ADC` |
| SecondaryObjectiveComplete | `0x00534432` | same | `0x008A9B2C` |
| PrimaryObjectiveFailed | `0x00534462` | `c7 00 02 00 00 00` | `0x008A9ADC` |
| SecondaryObjectiveFailed | `0x00534492` | same | `0x008A9B2C` |

NOP a complete-store to ignore script completion. Rewrite a fail-store
`02` → `01` to record a scripted fail as complete. Destinations are BSS.

### 17.8 SetGoodieState

`0x00533A70`: unbox two ints, `mov [eax*4 + 0x00662560], edi` at
`0x00533A87` (`89 3c 85 60 25 66 00`). Destination is BSS. NOP the
store: scripts cannot write goodie state. Index convention stays with
`missionscript-iscript-static-contract.md` (one-based script index).

### 17.9 SetSpeed — declined no-op

Handler `0x00453AC0` is `c2 0c 00` (`ret 0xc`) plus nops. Registry
index 2. The existing Ghidra name `SharedVFunc__NoOp_Ret0C` is the
honest identity. There is no speed immediate to patch. Rowed as
understood-and-declined so the 144-native census does not re-open it.

### 17.10 Activate / Deactivate / SetVisible

| native | site | original | role |
|---|---|---|---|
| Activate | `0x00535D55` | `ff 50 58` | `call [eax+0x58]` |
| Deactivate | `0x00535D65` | `ff 50 5c` | `call [eax+0x5c]` |
| SetVisible | `0x00535EB3` | `75 0c` | after `cmp al, 1`: jne → hide (`+0x84`); NOP → always show (`+0x80`) |

### 17.11 SetAIState — poke, not a tick

`0x005361A0` unboxes an int and `call [thing.vtable+0xd8]` at
`0x005361B8`. NOP the 6-byte call: scripts cannot poke AI state. This
does **not** freeze per-unit think (§10.4).

### 17.12 Land / Dive / Surface / Retreat / Deploy / Undeploy

Type-bit then a vfunc or a named helper. NOP the `je` to run the
command without the type test.

| native | je VA | original | tail |
|---|---|---|---|
| Land | `0x005361D7` | `74 08` | `call [eax+0x174]` |
| Dive | `0x005361FA` | `74 05` | `call 0x004EF000` (bit `0x10000000`) |
| Surface | `0x0053621A` | `74 05` | `call 0x004EF050` (same bit) |
| Retreat | `0x00535D37` | `74 08` | `call [eax+0x190]` |
| Deploy | `0x00534F77` | `74 05` | `call 0x004FDE30` |
| Undeploy | `0x00534F97` | `74 05` | `call 0x004FDE70` |

### 17.13 MPDeclarePlayerWon / MPDeclareGameDrawn

`MPDeclarePlayerWon` `0x00533A40` unboxes an int and
`call 0x0046F360` at `0x00533A51` with `this=0x008A9A98`
(`CGame`). `MPDeclareGameDrawn` `0x00533A60` is
`mov ecx, 0x008A9A98; call 0x0046F3E0` at `0x00533A65`.
NOP either call. Destinations inside those helpers are BSS.

### 17.14 SetLockable

`0x00533950`: type-bit `je` at `0x00533958`, then
`[thing+0x164]` must be non-null, unbox bool,
`and eax, 0xff` at **`0x0053396F`**, store
`[config+0x114]`. Same force-FALSE shape as
`SetVulnerable`: `25 ff 00 00 00` → `33 c0 90 90 90`.

### 17.15 SetTimer

`0x005358E0` unboxes a float and
`AddEvent_AtTime(0x7d2, this, delay)` via
`call 0x0044B2D0` at `0x00535908`. NOP×5: scripts
cannot schedule the IScript timer (HandleMessage 2002).

### 17.16 Damage / SetName

`IScript::Damage` `0x005348C0`: unbox float, then
`call [thing.vtable+0xa0]` at `0x005348E3` (`ff 97 a0 00 00 00`).
NOP×6.

`IScript::SetName` `0x00535C70`: unbox string, then
`call [thing.vtable+0xa8]` at `0x00535C88`. NOP×6.

### 17.17 SetVelocity / Attack type-bit

| native | je VA | original | tail |
|---|---|---|---|
| SetVelocity | `0x0053434B` | `74 1a` | `call [thing.vtable+0x70]` |
| Attack | `0x00535FD2` | `74 47` | target must also have bit 4 (or the `0x20000000` alt) |

### 17.18 Launch / TriggerHitEffect

`Launch` `0x005344A0`: type-bit `je` at **`0x005344AD`** (`74 46`), then
`[thing+0x164]` must be non-null and `[config+0xe0]==0x18`, then
`call 0x004D36C0` at `0x005344F0`. NOP the `je` to try without bit 4
(the config test still runs). NOP the call to stop scripted launches.

`TriggerHitEffect` `0x00536CA0`: type-bit `je` at `0x00536CAA`
(`74 1f`), unbox float, `call [thing.vtable+0x1ac]` at `0x00536CC5`.

### 17.19 SetPos / Teleport / SetGoalPoint / Stop

All four write a position through a vfunc. Destinations are the
thing, not a file global.

| native | site | original | role |
|---|---|---|---|
| SetPos | `0x00536C90` | `ff 52 50` | `call [edx+0x50]` |
| Teleport | `0x00536A2B` | `ff 50 50` | same vfunc after a type-6 / name lookup |
| SetGoalPoint | `0x00534F1C` | `ff 97 f4 00 00 00` | `call [edi+0xf4]` |
| Stop | `0x00534F57` | `ff 90 f4 00 00 00` | same `+0xf4` with the thing's current `+0x1c` pose |

`TeleportOrientation` multiplies three unboxed angles by
`[0x005DC7B0]` = π/180 (8 refs). That float is shared — not rowed.

### 17.20 SetScript / SetSpawnScript

`SetScript` `0x00535C50` unboxes a string and `call 0x004F4230` at
`0x00535C62`. `SetSpawnScript` `0x00535CA0` unboxes and
`call [thing.vtable+0xfc]` at `0x00535CB8`. NOP either: scripts
cannot rebind the attached / spawn script.

### 17.21 Segment health / vulnerable

Twins of §17.2. Type-bit then `[thing+0x178]` must be non-null.

| native | je VA | original | tail |
|---|---|---|---|
| SetSegmentHealth | `0x00535488` | `74 2d` | `call 0x00444450` |
| ResetSegmentHealth | `0x005354C8` | `74 2d` | `call 0x004444B0` |
| SetSegmentVulnerable | `0x00534308` | `74 2f` | `and eax,0xff` at `0x00534325` then `call 0x004445B0` |

Force-FALSE on the bool: `25 ff 00 00 00` → `33 c0 90 90 90`.

### 17.22 PlayAnimation / SpawnParticle

`PlayAnimation` `0x00535160`: `mov ecx,[thing+0x30]; test ecx,ecx;`
`0x0053516C` `74 51` skips the whole play. `74 51` → `EB 51` is a
safe disable (never look up / dispatch). NOP of that `je` would
run the helper with a null controller — not rowed.

`SpawnParticle` `0x00536B70` looks up by name via `0x004CD7A0`.
`0x00536B9C` `75 1b` proceeds on a hit. `75 1b` → `EB 1b` always
takes the error return.

`SpawnEscapePod` `0x005371E0` is 556 B (construct + vslot). No
one-instruction lever is claimed. `FollowWaypoint*` is a large
lookup + pose write; declined this cut.

### 17.23 SetVar / world variables / Shutdown / PostEvent

| native | site | original | role |
|---|---|---|---|
| SetVar | `0x00534901` | `ff 92 f8 00 00 00` | `call [edx+0xf8]` |
| InitVariable | `0x0053624D` | `e8 4e 74 fd ff` | `call 0x0050D6A0` (`this=0x00855090`, BSS) |
| SetVariable | `0x0053628F` | `e8 8c 74 fd ff` | `call 0x0050D720` |
| ShutdownVariable | `0x00536341` | `e8 5a 74 fd ff` | `call 0x0050D7A0` |
| Shutdown | `0x00535D22` | `e8 49 56 f1 ff` | `AddEvent(0x7d0)` via `0x0044B370` |
| PostEvent | `0x00538459` | `e8 12 2f f1 ff` | same helper, same event id |

`0x00855090` / `0x00672FC8` are BSS; patch the calls.

Confidence for §17.18–§17.23: **STATIC_ONLY**. Risk: medium
(type-bit drops) / high for Shutdown (authored teardown).

Confidence for §17: **STATIC_ONLY** (handler heads + type-bit pattern +
specimen bytes). Risk: medium for mutators that drop a type-bit guard
(null-record / wrong-vtable crash is exactly what the `je` prevents).

---

## 18. IScript getters / predicates

Getters box a float (`vtable 0x005E4EA4`) or a bool
(`vtable 0x005E4D50`) and return. The useful file levers are
(a) the type-bit `je` that skips the load, (b) the boxed-float
**init dword** that becomes the return when the helper is skipped,
and (c) the `setne` / false-arm `jcc` that builds a bool.

### 18.1 GetHealth / GetRealHealth / GetInitialHealth

`GetHealth` `0x00535920`: `mov [esp], 0` at `0x00535924`, type-bit
`je` at `0x00535930` (`74 09`), else `call 0x004F99F0` (fld
`[thing+0xf8]` or a segment helper) and `fstp [esp]`. Pair:

- init `00 00 00 00` → `00 00 80 3f` (1.0f)
- `74 09` → `EB 09` (never call the helper)

Scripts then always see full health. NOP the `je` instead to run
the helper without bit 4.

`GetRealHealth` `0x005359D0` / `GetInitialHealth` `0x00535A30`
are the same shape (helpers `0x004F9A40` and `vtable+0x138`).
Type-bit `je`s at `0x005359E0` / `0x00535A40` are rowed.

### 18.2 GetEnergy

`0x00535BB0`: type-bit `je` at `0x00535BC0` (`74 0a`); taken path
copies `[thing+0xfc]` (the same energy dword JetPart::Move
drains, §5.8). Same init+skip pair as GetHealth.

### 18.3 GetWeaponAmmo / GetWeaponCharge

Bit **3** (`test [thing+0x34], 8`) — the BE/flight bit, not bit 4.
`je`s at `0x00535620` / `0x00535760`. Helpers `0x0040C3C0` /
`0x0040C4A0`.

### 18.4 GetConfiguration

Bit 3 `je` at `0x005357CE` (`74 6e`), then
`ecx = [thing+0x4B0]; ecx = [ecx+0xa8]` — the profile name
pointer. This is independent proof that `[BE+0x4B0]` is the
`CBattleEngineData` used in §5.8 (`+0xa8` =
`mConfigurationName`, Initialise's first store).

### 18.5 IsObjective / Exists

`IsObjective` `0x00535EF0`: `call [thing.vtable+0x68]`; `je` at
`0x00535EFA` (`74 3a`) takes the box-FALSE arm. NOP → always
TRUE.

`Exists` `0x00536920`: `call [arg.vtable+0x40]`; `jne` at
`0x0053692D` (`75 3a`) takes the box-TRUE arm. `75 3a` →
`EB 3a` → always TRUE.

### 18.6 IsFiring / InJetMode / IsOverWater

All three `xor esi,esi`, optionally set esi from a helper, then
`setne cl` into the boxed bool.

| native | setne VA | helper |
|---|---|---|
| IsFiring | `0x00535B8B` | type-bit then `0x004FD760` |
| InJetMode | `0x00538132` | bit 3 then `0x00408120` |
| IsOverWater | `0x00538183` | `0x004F3DE0` (no type-bit) |

`0f 95 c1` → `b1 01 90` (`mov cl, 1`).

`0x00408120` is **not** a plain IsJet: `cmp [BE+0x260], 2` then
a `GameTime − [BE+0xcc] < 0.5f` conjunct (`0x005D85EC` = 0.5f).
The native boxes TRUE iff that helper returns **0**. The `setne`
patch ignores the helper. Do not advertise it as "force jet
physics".

### 18.7 GetSlot

`0x005339A0` unboxes an int, `call 0x0046D410`
(`CGame::GetSlot`, `this=0x008A9A98`), `setne al` at
`0x005339F7`. `0f 95 c0` → `b0 01 90`. Sibling of §12.2.

### 18.8 IsFriendly / IsEnemy

Both test type bit 4 then `[thing+0x138]` (same allegiance
dword as `ConfirmedKill`, §12.5). Friendly is `== 0`; Enemy is
`== 1`. NOP the type-bit `je` and/or the allegiance `jne` to
force the TRUE arm.

`GetPlayer` (`0x005363E0`) indexes BSS `[eax*4+0x008A9D3C]`
— no file row. `GetGoodieState` loads BSS
`[index*4+0x00662564]` (one-based; same table as §17.8).
`GetWaterHeight` flds BSS `0x006FBDFC`. `GameTime` flds BSS
`0x00672FD0`. Those four stay honest non-surfaces.

### 18.9 GetNumber / GetSquad / GetTarget / GetWeaponName

| native | je VA | original | note |
|---|---|---|---|
| GetNumber | `0x0053598D` | `74 06` | bit `0x80000`; else `[thing+0x270]` |
| GetSquad | `0x005365E5` | `74 06` | bit 4; else `[thing+0x148]` |
| GetTarget | `0x005366E4` | `74 0a` | bit 4; else `vfunc+0x144` |
| GetWeaponName | `0x0053568E` | `74 6e` | bit 3 (BE), then `0x0040C570` |

### 18.10 GetSafePos / GetComponent

`GetSafePos` `0x005350B0`: type-bit `je` at `0x005350D7`
(`74 1a`) skips `vfunc+0x1b8` and boxes the zeroed stack
vector. NOP to run the helper without bit 4.

`GetComponent` `0x005349B0`: type-bit `je` at `0x005349D9`
(`74 19`) skips `0x004FD8D0` and logs. NOP to look up
anyway.

`GetMapHeight` flds through BSS `0x006FADC8` — no file row.
`GetX`/`GetY`/`GetZ` unbox a vector and return one
component; no one-instruction cheat.

### 18.11 SpawnersEmpty / SpawnersInUse

Same shape as IsFiring: type-bit, helper, `setne cl`.

| native | je VA | setne VA | helper |
|---|---|---|---|
| SpawnersEmpty | `0x00535A9A` | `0x00535ACB` | `0x004FD7E0` |
| SpawnersInUse | `0x00535AFA` | `0x00535B2B` | `0x004FD7A0` |

`0f 95 c1` → `b1 01 90`. `GetNumUnits` indexes BSS
`[ebx*4+0x008551C0]` / `+0x00855228` — no file row.

### 18.12 IsA

`0x00536350` unboxes an int mask, `test [thing+0x34], eax`,
`je` at **`0x00536365`** (`74 3a`) takes the box-FALSE arm.
NOP → always TRUE.

`Rand` / `GetFloatRand` load BSS `[0x008A9D9C]` then an LCG.
The `[0,1)` scale at `0x005D8D54` (`1/65536`, **46 refs**) is
shared — not rowed.

Confidence for §18.9–§18.12: **STATIC_ONLY**.

Confidence for §18: **STATIC_ONLY**. Risk: medium for type-bit
drops; low-medium for bool forces.

---

## 19. IScript camera

### 19.1 GotoPlayerCamera

11-byte native `0x005342B0`: `mov ecx, [0x008A9D3C]; call 0x004D2A50`.
The singleton is BSS; NOP the call at `0x005342B6`. Callee
switches on `[this+0x28]` (1 → `0x004D28C0`, 2 → `0x004D29C0`).

### 19.2 ToggleCockpit

`0x00533980`: `[0x008A9D3C]` then `[eax+0x1c]` then
`call 0x0040E840` at `0x00533990`. Callee toggles
`[cockpit+0x12c]` via `sete`. NOP the call.

### 19.3 Disable scripted pans

`Goto3PointPanCamera` `0x00533B70` / `Goto4PointPanCamera`
`0x00533EB0` early-out if the unboxed thing-ref is null
(`jne` at `0x00533B9C` / `0x00533EDC`, both `75 24`, to the
constructor). NOP the `jne`: every call takes the error return
and never builds the pan. Bodies after that are large
(matrix / duration) and are not further rowed.

---

## 20. Weather

Destinations `0x00660188` (lightning), `0x0066018C` (snow),
`0x00660190` (rain), `0x00660198..A4` (wind) sit in
**file-backed** `.data` (before `0x00661000`) but ship as 0.0f
and are **zeroed again** by the weather-init block at
`0x00404A20` (`c7 05 … 00 00 00 00` at `0x00404A43` /
`4D` / `57`). File-patching those dwords is a no-op after
init. Patch the **init stores** or the IScript `fstp`s.

### 20.1 IScript density stores

Each native is 17 bytes: unbox float (`vtable+0x34`), `fstp`
the dest, `ret 0xc`.

| native | fstp VA | dest |
|---|---|---|
| SetRainDensity | `0x0053836B` | `0x00660190` |
| SetSnowDensity | `0x0053838B` | `0x0066018C` |
| SetLightningDensity | `0x005383AB` | `0x00660188` |

NOP the 6-byte `fstp`. Scripts cannot change that density.

### 20.2 Init defaults

`0x00404A43` / `4D` / `57`: rewrite the imm32 `00 00 00 00` →
`00 00 80 3f` (1.0f) for a startup rain/snow/lightning world.
IScript can still overwrite unless §20.1 is also applied. The
same addresses are later pushed as cvar/registration args
(`0x00404B1A` etc.) — do not confuse those pushes with stores.

### 20.3 SetWindVector

`0x00538300` unboxes four floats and writes
`[0x00660198..A4]`. First store `0x0053833B`
(`a3 98 01 66 00`) is rowed. Siblings
`0x00538348` / `4E` / `54` are the other three components.

Confidence for §20: **STATIC_ONLY**. Risk: low / medium
(init-1.0 changes the default look).

---

## 21. IScript messages / wait

### 21.1 Wait-flag twins

See §16.2. This cut rows `PlayCharMessageWait` `0x005376F9`,
`PlayPCharMessageWait` `0x005379F5`, and `PlayAnimationWait`
`0x0053531C`. Same 10-byte store as Pause. High desync risk.

### 21.2 SwitchMessagesOn / Off

17-byte twins. `[0x008A9D84]` (MessageBox singleton, BSS);
`je` skip if null; `call 0x004B7B60` (On, writes
`[this+0x2c0]=1`) / `0x004B7B70` (Off, writes 0). NOP the
call at `0x005342CA` / `0x005342EA`.

### 21.3 PlayCharMessage insert

`PlayCharMessage` `0x00537500` builds a `CMessage` (`ctor`
`0x004B6E50` at `0x005375BC`, arg7 hardcoded `0xA` per
`mission-script-command-registry-2026-08-12.md`) then
`call 0x004B7CA0` at `0x005375D2`
(`InsertQueuedMessageSortedAndMaybeAdvance`). NOP the insert:
the line is constructed and not queued. The two `Wait` forms
and `PlayPChar*` are the same insert family; one
representative is rowed.

### 21.4 PlaySample

`0x005381F0` pushes a stack of volume/id immediates (including
`0x3f800000` = 1.0f and `0x3f333333` = 0.7f) and
`call 0x004E0A90` at `0x00538226`. NOP the call.

### 21.5 AddHelpMessage

`0x00533B30`: `[0x008A9D90]` (BSS); unbox; `cmp eax, 0x2321c8`
then `jne` skip. `call 0x0047FB00` at `0x00533B5D` is the
push. NOP the call.

`Print` / `PrintText` / `AddMessage` stay pointer-only (debug
console / fixed-source queue).

### 21.6 PlayCutscene

`0x00535890` unboxes a string, looks up via `0x0050AF70`
(`this=0x00855090`, BSS), then `test [obj+0x34], 0x10000`.
`je` at **`0x005358B4`** (`74 0b`) skips
`call 0x0043F340` at `0x005358B8`. NOP the `je` to call
even without the cutscene bit. NOP the call: scripts cannot
start a cutscene. The lookup table is runtime; this is the
file lever the prior cut left pointer-only.

Confidence for §21: **STATIC_ONLY**. Risk: high for wait-flag
NOPs; medium for dropping queued lines / cutscenes.

---

## 22. HUD highlight

`HighlightHudPart` `0x00535E60` and `UnHighlightHudPart`
`0x00535E80` are 22-byte twins. Unbox int, then an unchecked
`mov [eax*4 + 0x008AA51C], imm`. Destination is BSS
(2 address refs — only these two stores). Patch the stores.

| native | store VA | original |
|---|---|---|
| HighlightHudPart | `0x00535E6B` | `c7 04 85 1c a5 8a 00 02 00 00 00` (imm 2) |
| UnHighlightHudPart | `0x00535E8B` | same form, imm 1 |

NOP the 11-byte store: that native becomes a no-op. Rewrite
imm `02` → `01` to make Highlight behave like UnHighlight.
The bound on `eax` is still open (static-contract note);
an out-of-range index writes past the table.

Confidence: **STATIC_ONLY**. Risk: low-medium.

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

TSV: **184 data rows** (182 unique VAs). `t_120c3e1b` 147 plus 37
from this cut (HUD / PlayCutscene / leftover IScript
position-script-segment-variable-getter rows). Every
non-unknown `original_bytes` was re-read from the named
specimen (`145` prior compared, `0` mismatch, then `37` new).

Confidence histogram: **MEASURED 22 / STATIC_ONLY 162 / SPECULATIVE 0**.

First-cut corrections landed here, not in `rebuild/**`:

- won-countdown imm is `0x0046F33D`, not `0x0046F33B` (ModRM) or `0x0046F338`
- lost-countdown file offset is `0x0006F4A8`, not `0x000F4A8`
- building ApplyDamage offset is `0x00017A16`, not `0x0007A16`
- `g_bGodModeEnabled` is BSS; first-cut file row retracted
- water conjunct is `[0x00662DD0]`, not `0x00662DF4`
- jet `0x00410CA2` polarity is `ebp==0` (xor at `0x00410C5A`); first-cut left it unrowed
- WIN/LOSE arms start with `cmp [0x00662DD0], 1`, not an unknown jump target

Coverage limits that stay honest: no per-unit AI tick (SetAIState is a
poke), no exe spawn tables (SpawnThing is a native; SetSpeed is a no-op),
debug-button **key → id** still BSS (the SendButtonAction door is pinned).
Initialise now names the remaining constructor slots (`mLife` /
`mEnergy` / velocities / turn rates / shield / stealth / store
loop); shipped dats still overwrite them. Getters/camera/weather/message
already had one-instruction rows; this cut adds HUD stores,
PlayCutscene, Teleport/SetPos, SetScript, segment twins, world
variables, and leftover predicates. `GetPlayer` / `GetGoodieState` /
`GetWaterHeight` / `GameTime` remain BSS-sourced. Print/PrintText/
AddMessage are still pointer-only. `Rand`/`GetFloatRand`/`GetMapHeight`/
`GetNumUnits` are BSS-sourced.
