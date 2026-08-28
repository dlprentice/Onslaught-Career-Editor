# CFEPDebriefing__Render

Status: active reproduced static contract; runtime/pixel equivalence remains open
Last updated: 2026-08-27
Source File: `C:\dev\ONSLAUGHT2\FEPDebriefing.cpp` (embedded by the shipped image; absent from the pinned Stuart drop) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Pristine PC address: `0x00456DD0`
> Exact body: `0x00456DD0..0x00457CED` (3,870 bytes, 1,076 instructions)
> Body SHA-256: `2ce0bc8ee64da806aad4c272b1242063616df5f513393c55789a9f76c5e19e91`
> Source path embedded by retail: `FEPDebriefing.cpp`; that file is absent from the pinned Stuart drop

## Evidence boundary

This is a reproduced static contract from pristine PC
`BEA.exe.original.backup` (SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
The exact raw body was independently extracted and decoded. Stuart's
`EndLevelData.h`, `game.h`, `Career.cpp`, and `FrontEnd.cpp` corroborate
the named data bridge and frontend order, but the missing source body prevents a
source-equivalence claim. Static evidence proves the branches, reads, calls, and
submitted constants below; it does not substitute for a settled retail capture.

## Inputs read

| Address | Field/use |
| --- | --- |
| `0x00672D78 + i*8`, `i=0..9` | primary objective status dwords |
| `0x00672DC8 + i*8`, `i=0..9` | secondary objective status dwords |
| `0x00672E18` | `mWorldFinished`; level-name lookup and world-500 branch |
| `0x00672E1C` | `mFinalState` |
| `0x00672E20` | `mRanking`; victory-only grade conversion |

The two loops read exactly ten entries at stride eight and only the first dword
of each objective record. This body never reads `mThingsKilled`; the released
debriefing page has no kill table in this render path.

## Settled text contract

- Final state `4` draws **Defeat** in `0xFFFF3F1F`.
- Final state `5` draws **Victory** in `0xFF3FFF2F`.
- Every other state draws **Aborted** in `0xFF3F3F3F`.
- Mission/objective labels use `0xFFFFAF3F`; level and grade label use white.
- For each objective group, zero is ignored. All ten zero hides the row. If at
  least one entry is nonzero, the row is **Complete** only when every nonzero
  entry is exactly `1`; any other nonzero value makes it **Incomplete**.
- One exact exception exists: world `500` plus final state `5` forces the
  primary row visible and Complete regardless of all ten primary words.
  Secondary objectives have no override.
- Grade label/art is present only for final state `5`.
  `CCareer::GetGradeFromRanking(0x00672E20)` selects S explicitly and A-E
  through the contiguous shared-resource table.

English text comes from `english.dat` SHA-256
`789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a`:
`DEBRIEFING`, `Mission Status`, `Victory`, `Defeat`, `Aborted`,
`Primary Objectives`, `Secondary Objectives`, `Complete`, `Incomplete`,
and `Grade:`. English joins the first three labels to their values with
`": "`; French uses `" : "`.

## Settled geometry and assets

At transition `1.0`:

- the level name begins at `(130,149)`;
- mission status is at y `184`;
- primary objectives are at y `210` when visible;
- secondary objectives are at y `226` after a visible primary, otherwise
  y `210`;
- the value column begins at x `130 + max(label extents) + 20`;
- `Grade:` begins at `(130,295)`;
- the grade frame body is centred at `(320,310)`, scale `1.25`; its shadow
  is at `(325,320)`, scale `1.3125`;
- grade art is centred at `(320,310)`, scale `1.0`; its shadow is at
  `(323,313)`;
- `FE_metal_ring_trans_from_levsel2` is centred at `(285,225)`, scale
  `1.6`;
- `FEPShared::RenderSelectionBrackets` is a recovered-name misnomer here: it
  draws four `FE_Forseti_Writing_large` surfaces at x `86`, scale `0.5`,
  180 pixels apart. The first y is
  `90 - fmod(frontend_counter * 0.3, 180)`.

Shared-resource bindings recovered from
`CFrontEnd::LoadSharedResources @ 0x004687E0`:

| Address | Surface |
| --- | --- |
| `0x0089D7B8` | `GlareAlpha` (dynamic delayed glint only) |
| `0x0089D7C0` | `RankingS` |
| `0x0089D7C4..0x0089D7D4` | `RankingA` through `RankingE` |
| `0x0089D7F0` | `FE_Forseti_Writing_large` |
| `0x0089D810` | `FE_metal_ring_trans_from_levsel2` |
| `0x0089D8A0` | `FE_BEA_title_symbol_bracket01` |

`CFEPDebriefing::RenderPreCommon @ 0x00456D40` calls
`CFrontEnd::RenderPreCommonFade`, which calls the common frontend video-quad
path. It does not draw the Mission Briefing rock background. Exact debriefing
underlay phase/tint remains capture-open.

## Input and sibling state

When settled and mouse input is ready, Render registers the entire
`0,0,640,480` rectangle as button `0x2C`. `ButtonPressed @ 0x004568A0`
also accepts `0x2E`, but page exit is gated on `this+0x08 > 0.5f`;
`0x2D` only arms a delayed time field. Ordinary PC retail then selects page
`7` (Level Select) with transition `30`, plays sound `1`, and clears all
100 link handles. Playable-demo mode takes a different result-sentinel path.

`TransitionNotification @ 0x00457CF0` consumes the career new-goodie count
(ordinary retail only) and first-goodie Boolean after `CCareer::Update`.
`Process @ 0x00456930` uses those values for transient particle/message
effects. They are not a rendered list of goodies.

## Promoted reconstruction boundary

`RetailDebriefingProjection` reproduces the final-state, objective, world-500,
grade, and goodie-latch projection. The Godot page consumes the exact ring and
A-E/S grade files and implements the measured settled content, geometry, and
submitted colors. It deliberately does not claim the entry/exit interpolation,
`this+8 > 0.5` input delay, goodie particle/message sequence, grade reveal
timing, glare animation, writing-scroll clock, retail mode-8 Z-function versus
Canvas draw-order equivalence, or capture-level pixel parity.

The current Level 100 reconstruction feeds the canned pre-score-time
`ForLevel100Won()` ranking of `1.0`, so its displayed S proves the page path,
not the still-unjoined live Level 100 score/time result.

## Cheapest remaining falsifiers

1. Capture a pristine settled world-100 debrief and compare font baselines,
   common-underlay phase/tint, blend state, and asset placement.
2. Probe copied retail around the `this+8 == 0.5` boundary and goodie counts
   `0,1,99,100`.
3. Force copied world 500 to Won with zero/failing primary words to visibly
   reproduce the forced-Complete branch.
4. Join a natural Level 100 run's live score/time stores into
   `END_LEVEL_DATA.mRanking` before treating its grade as experience parity.

Primary decompile:
`local-lab/ghidra-fullpass-2026-07-23/exports/W004/decompile/00456dd0_CFEPDebriefing__Render.c`
(SHA-256
`266ed5d831611cf1d67648d7c13af24c23be347f2103033d215a7777d4746524`).
