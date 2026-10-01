# HUD / frontend overlay static contract

Status: bounded retail static evidence; not visual proof
Last updated: 2026-10-01 (BE configuration input gate and light colors; earlier bounded rechecks retained)
Summary: specimen-bound frontend input, color and coordinate corrections; complete function matches and isolated calculations remain distinct from player acceptance.
Evidence: MEASURED — October 1 native compass and font fragments, isolated menu runs and full-section/relocation matches, plus September 30 font and scale-menu readback; August HUD claims were not reverified in this pass.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## BE configuration down-arrow gate — October 1

In `CFEPBEConfig::Render` (`0x004505b0`), the down-arrow rectangle call at
`0x00451835` occurs only after the counter/flash predicate admits it. The
predicate at `0x004517f4` converts the counter using the current x87 control
word, forms the signed remainder modulo 64, and admits a result below 50 or
a positive down-flash value. The earlier reconstruction called the handler
before that predicate. The up-arrow handler remains unconditional.

The lead reproduced 256 finite authored cases of this predicate/call fragment,
with explicit exits before rendering and an authored callback returning false.
The old draft makes 44 extra calls; corrected traces and all five arguments agree
with retail. Missing input, unexpected exits, stack/canary, register and x87
violations are rejected. This does not execute the real callback, mouse handling
or complete Render; callback state changes and player interaction remain open.

The same source correction restores the three RGB light triples using vector
scaling by `0.6f`. All nine compiled arguments now equal retail's float bits;
the earlier literals were one ULP lower. A fresh lead compile matches the frozen
corrected object and preserves all other callable sections in that object.
Full Render remains unmatched. A future whole-caller falsifier should cover the
counter boundary and flash states while observing actual handler side effects.

Private lead evidence under
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/geometry-gate-resume-20261001/`:
`frontend-gate-root-replay/receipt.json` and `trail-frontend-device-root-readback.json`.

## Compass coordinate association — October 1

The original argument fragment at `0x00485ccc`–`0x00485d37` in `CHud::RenderWeaponPanel`
(`0x004858d0`) adds the fixed offsets before the heading displacement: Y is
`((ny - 128) + 48) + dy`; X adds 17, then 48, then `dx` to its base coordinate.
The former reconstruction let VC6 add `dy` before 48 and `dx` before 48. Explicitly grouping
the fixed coordinates restores these instruction associations.

The lead recompiled the correction and reproduced 6,171 native fragment cases using finite authored
states and explicit round-nearest x87 PC24/53/64. All 15 outgoing draw-argument words agree after
the correction; the former expression differs in 146 PC24 cases. For `ny=96`, `dx=float(0.1)`,
`dy=float(-0.1)` and zero X offsets, retail/corrected Y is `0x417e6666`; the old Y is
`0x417e6668`. Stack movement/canaries, nonvolatile registers, x87 stack/control word and absence
of nonprecision exceptions were checked. The old expression supplies a consequential negative control.

This does not execute upstream sine/cosine, `GetBottom`, a draw call or the game. The caller's live
precision and visible consequences are unmeasured. The whole function remains unmatched; its opposite
order of X-global reads, cosine materialization and other scheduling differences remain open. All
55 exact functions in the affected three-object check survive, and all 37 other HUD callable sections
and their relocations are unchanged.

Private reproduction: `bea-decomp/.worktrees/codex-resume-frontend-20261001/local-data/`
`frontend-resume-20261001/native-coordinate.py --out NEW_OUTPUT`, with frozen inputs in `coordinate/`
and lead results in `coordinate/root-reproduction-v01/`. The lead verified the frozen retail fragment
and constants against the specimen and both candidate objects against fresh local compilation.
The next falsifier is a complete caller invocation spanning trigonometry and the actual device state.

## Loading-screen text selection — October 1

At `0x0042cd4b`–`0x0042cd67`, the loading-screen renderer reads the byte at
`0x0066e8c0`. Zero selects text ID `0x003848a7`; any nonzero byte selects
`0x07dea02c`. The authored text-name table identifies these as `IG_LOADING2`
and `FETX_PRESS_START`. The private reconstruction had mistyped the second ID
as `0x07dae02c` and now uses the retail value.

All six inspected version-three language tables contain the correct ID at record
327 and loading ID at record 1897; none contains the mistyped ID. English resolves
them to “Press START button” and “Loading...”. The original lookup `0x004f2580`
logs an absent ID and returns the start of its text pool (`0x004f25d2`–`0x004f25f0`),
which contains `**Undefined String**` in these files. This is the pool prefix, not
the first indexed record. Retail's loader computes that pool as file base plus
`16 + 12 * count` for these version-three files (`0x004f2401`–`0x004f2408`).

The lead executed the original and fresh before/after selection fragments for all
256 flag values with two register/carry seeds. The old version differs in 510 of
512 cases; the corrected version agrees throughout. Eighteen separate calls to the
actual original lookup, using the three IDs and six real tables, reproduce the
selected strings and missing-ID logging. Only logging is a recording substitute;
it checks its arguments and clobbers caller-saved registers. The source lookup was
also freshly compiled and matches its complete section and relocations. Stack,
callee-saved registers and unchanged input data were checked.

This establishes the selection and lookup behavior, not a complete renderer run.
The caller first requires bottom text enabled and a valid font. Mode 3 then replaces
the selected pointer with PC text ID `0xdc` (`0x0042cd72`–`0x0042cd83`), so the
incorrect placeholder need not be drawn in that mode. Actual loading-route
reachability, drawing and visual acceptance remain open. A useful falsifier is a
controls-pause loading state with bottom text enabled, a valid font and mode other
than 3, observing the ID and resulting text.

Private lead evidence is
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/loading-text-root-20261001/`:
`readback.json`, `selection-v02/assets.json` (individual file hashes and offsets),
and `selection-v02/receipt.json` (SHA-256
`0de97f1e4632611013781ed37ba904b105ee6a1d7616508d7f95d942261ee3df`).
The correction changes two instruction bytes, retaining 61 exact console controls,
all 147 target relocations and all 318 other object sections. The full loading-screen
renderer remains unmatched. No game, Godot, font or graphics device was run.

## Goodies text preserves fractional Y — September 30

The Goodies renderer at `0x0045e0d0` passes text flags `0x10` at `0x0045fe3d` to
the font wrapper `0x00540640`. That wrapper forwards the flags to `0x00540010`.
At `0x0054018c`, bit `0x10` selects the path that skips flooring the Y coordinate;
with the bit clear, `0x0054019e` calls the CRT floor routine `0x0055dfe7`. The
private reconstruction previously omitted the flags argument and therefore requested
the default rounding. Its call now passes `0x10`. The complete Goodies renderer
remains unmatched, so this correction does not close the rest of that body.

The lead reproduced 18 bounded original-code cases: two wrapper argument-forwarding
cases and eight finite Y values with the flag both clear and set. For example, clear
flags turn `-0.25` into `-1.0`, whereas `0x10` preserves `-0.25`. The tests execute
the original rounding slice and its actual CRT floor/control-word helpers, check
the exit point, floor-call count, stack and FPU state, and use FPU control word
`0x037f`. They do not execute drawing or a complete font call. Private evidence:
`bea-decomp/.worktrees/codex-frontend-20260930/local-data/frontend-matching-20260930/font_flag_probe.py`
(SHA-256 `dfb50f617d38a8b83a94dc4ba56ac47c1eadd9e65db71ef27be35b5bded7cb4f`);
the lead's reproduced receipt is
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/frontend-matching-20260930/font-flag-probe.json`
(SHA-256 `f34c1d4ccee9ea7a2aa557f801fc1d841d8849d6e4c5c5409667d850f76159d2`).

For reconstruction, preserve the fractional Y path at this call site. No retail or
Godot frame was inspected, and no visible jitter or general font parity is claimed.
A useful presentation falsifier is the same Goodies text at a known fractional Y
position with this bit toggled, keeping the viewport and font inputs fixed.

## Generic scale-menu rendering — September 30

`0x004a37c0` reads the current value at `+0x24`, committed value at `+0x28`, and step count at `+0x2c`.
For a step below both values it selects `0xff00a000`; below neither it keeps `0xff505050`.
A step below only one value enters the time-dependent blend (`0x004a394c`–`0x004a3974`). The
non-selected-item path first copies committed to current and calls the value-change hook
(`0x004a37e2` onward); selection and commit state therefore matter to whether the blend is reachable.

Within the blend, the retail alpha computation multiplies two complementary factors separately by
the **float32** 255.0 constant, then adds them (`0x004a39a7`, `0x004a39af`, `0x004a39b5`). Preserve that
operation structure; factoring the products or substituting a double-width constant did not reproduce
the compiled instructions. The private reconstruction now matches the complete 848-byte section
(843-byte body plus alignment) and all 42 relocations. Lead reproduction retained every earlier match
in the affected objects and full integrated score; receipts are
`bea-decomp/build/menu-render-root-check-20260930.txt` and
`bea-decomp/build/root-score-menu-namedmesh-20260930.log`.

This gives the rebuild a precise generic current-versus-committed rendering contract. It does not
establish a visible defect in its currently live-applied options bars, whose values may already be
committed each change. No fresh game or Godot rendering was inspected. A useful presentation falsifier
is a genuinely deferred bar with differing current/committed values, sampled at known platform times;
player-visible colors and timing remain runtime acceptance work.

## Options-list title return — October 1

At the options-list renderer `0x004a4810`, DeferredRender returns at `0x004a4c53`.
The load at `0x004a4c57` saves `this+4` (the title pointer) into EDI before the
confirmation query and button-action callbacks. Both return paths (`0x004a4c91`
and `0x004a4cbc`) return that saved pointer. The reconstruction previously reread
the field after those calls; it now snapshots it at the retail boundary.

The lead reproduced 27 isolated x86 integer-tail runs: nine scenarios on each of
the original, previous and corrected tails. Explicit callback substitutions either
leave the title unchanged or replace it during confirmation/action handling. Six
changing-dependency cases distinguish the old reread; the corrected result agrees
with retail in every case. Callback receivers, arguments, ordering, final memory,
stack balance and canaries agree. Earlier rendering, floating-point calculations
and real callback implementations are excluded; their code is not executed by the
probe. This demonstrates the consequence of the ordering under intervention, not
that a live retail callback changes or invalidates the title.

That snapshot-only correction left the renderer unmatched; the subsequent complete
match below supersedes that state. All 18 prior exact controls and 22 other callable
sections/relocation destinations were preserved. Lead private evidence is
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/menu-title-root-20261001/`,
particularly `root-readback.json` and `tail/receipt.json` (SHA-256
`fa3b7e716f5a129c655e69ebfa96b6d0eeeef01eba70de58b2ec31701aae381e`).
For implementation, preserve the snapshot boundary. The cheapest remaining
reachability check traces actual confirmation/action implementations and their
title ownership; no player-visible menu defect is claimed from this probe alone.

### Complete renderer and failed text measurement

The subsequent source correction matches all 1,216 section bytes and 41 relocations
(1,207-byte retail body plus nine padding bytes). A natural panel-sizing helper
restores the width scan's First/Next calls at `0x004a48d2` and `0x004a48ea` while
the height scans remain inline. Giving its first `SIZE` a width-only scope and the
later title `SIZE` a caller scope restores retail stack reuse. A named title X
restores argument scheduling. The earlier title snapshot remains in place.

The frame correction has a concrete boundary consequence. Actual GetTextExtent
at `0x00540680` returns false without writing output when text is null. The panel
caller ignores that result; its first `SIZE` aliases an earlier height-sum scratch
word. The old reconstruction used a different unwritten slot. With an authored
80-high, 20-wide item and zero-initialized stack, retail and the corrected source
supply panel `(x,y,width,height) = (267,178,106,123)`; the earlier source supplied
`(300,178,40,123)`.

The lead reproduced 36 isolated prefix runs: twelve states on each of retail,
snapshot-only source and corrected source. Five of six null-title states distinguish
the old source; every corrected state agrees. Real GetTextExtent and pointer-set
instructions execute, with explicit font lookup, clearing and item-dimension
substitutions. The probe stops before drawing. Valid-title controls use an empty
UTF-16 string and a ready font; live null-title reachability remains unproved.
This emitted-code match is not a portable C++ guarantee for reading uninitialized
storage. Trace actual loaded text and confirmation-menu construction to settle
whether normal play can reach the failed-measurement state.

Private lead evidence:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/menu-frame-root-20261001/readback.json`;
prefix receipt SHA-256
`69c4eb25a6380871a16d5ea4520ab4baadae023dd3cecf60c9192b7c80c88b87`.
All 18 previous exact controls and 22 other callable bodies/relocation targets remain
intact. This closes the compiled renderer mismatch, not player or visual acceptance.

## Text measurement admission and rounding — October 1

The retail text-measurement routine `0x00540680` rejects null text or null output
before accessing font fields (`0x0054068a`–`0x0054069a`), returning false without
writing `SIZE`. Empty non-null text instead succeeds with width zero and one row's
height. Newline resets row width and adds a row height, then still measures the
remapped newline glyph (`0x00540754`–`0x0054078f`); carriage return skips glyph
measurement. Width and height conversions at `0x005407ff` and `0x0054080d` use
`FISTP qword`, then copy the low 32 bits. They honor the current x87 rounding mode;
a language cast that always truncates is not a general replacement.

The lead freshly compiled the reconstruction and reproduced 1,032 native i386
comparisons, using actual byte-matched character-map initialization and remapping
bodies at `0x00465c10` and `0x00465cf0`. Return values, dimensions, exception flags,
input/map memory, ABI and x87 state agree in the authored ready-font cases.
These cover 43 fixtures, PC24/53/64, all four rounding modes and two stack fills.
Three numerical/branch mutations are detected in 144, 24 and 726 cases respectively;
missing remapper and excluded texture initialization refuse execution.

The full measurement routine remains unmatched (448-byte section, 433-byte retail
body, 87 differing positions); all 14 existing object controls are preserved.
The cases do not establish behavior for arbitrary remappers, aliases, malformed
strings, nonfinite coordinates or actual font assets. Missing texture enters
initialization, which was excluded rather than modeled as a false return.
GDI/D3D initialization, live rounding state and visual text acceptance remain open.
Private lead receipt:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/font-extent-root-20261001/native-v2/receipt.json`,
SHA-256 `5887039c1a011a199c4e8b112e4b817fabf3a72be2380fc5bd3fd77f3d58fa63`.

## Font glyph stream and V-inset rounding — October 1

DrawTextScaled `0x00540010` writes corners top-left, top-right, bottom-right,
bottom-left with their respective UVs (`0x0054047e`–`0x005405b9`). The former
reconstruction cyclically shifted that stream to bottom-left, top-left, top-right,
bottom-right. The actual FastVB index loop at `0x0051a5d7`–`0x0051a5f3` uses
`0,1,2 / 2,3,0`; correcting the corner order therefore also restores the selected
diagonal. Because UVs moved with the corners, this was not a demonstrated flipped
glyph. No visible difference is claimed for an affine textured rectangle.

The lead reproduced 468 native glyph-loop states with actual map initialization
and remapping helpers. Explicit loop-entry adapters supply corresponding local
values for each compiled frame. The old source differs in 404 cases; the corner
correction reduces this to 32. A half-pixel mutation differs in all 468 cases and
a missing remapper refuses execution. Input/map memory, output guards, vertex and
colour cursors, final XY and x87 state are checked.

Those remaining differences exposed a separate precision boundary: retail stores the
last V coordinate as float32 at `0x00540311` and reloads it at `0x0054032d` before
calculating glyph height. The earlier candidate retained extended precision. An authored
case with unit UV coordinates, V inset `2^-25`, texture height one and starting
Y `.5` produces bottom Y zero in retail versus `-2^-25` in the candidate at
PC53/64 nearest. Nonzero inset reachability is unproved; this is a conditional
numerical defect, not an observed on-screen displacement.

A subsequent source correction gives the local vertex writer references to the
stored UV endpoints and copies their four-byte representations into its existing
fields. Stock VC6 restores the early float32 store/reload without adding calls or
output destinations; all 19 direct call targets retain their order. Fresh lead
execution gives zero differences in the same 468 finite cases. A causal control
removes only that rounding from the original instructions while retaining the
stored UV: its complete normalized outputs reproduce the earlier candidate in
all 468 cases, including the same 32 discrepancies.

Retail uses mixed integer and x87 UV transport; this representation-copy helper
is a reconstruction, not the proven original spelling or identical instruction
sequence. The complete candidate remains unmatched (1,552-byte section versus
1,581-byte retail body). All 14 previous exact object controls and 17 other
callable sections/relocation destinations remain intact. Prefix and viewport conversion,
flooring, buffer locking, device submission, arbitrary aliases/nonfinite inputs
and actual rendering were excluded. NaN payloads and unmasked exceptions are
also untested. The retained V-inset witness now passes; a live follow-up must
first establish the actual inset and FPU state at the caller.

Private lead owner:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/font-loop-root-20261001/`.
`readback-copy-v2.json` binds the fresh final source/object; the reproduced
`native-copy-v1/receipt.json` has SHA-256
`3155f770439a1c1f120e84b3032879ca372a66ab032a67e4237a4ace9086023a`.
The earlier `native-v1/` preserves the corner-only result.

## Message construction and Goodies requirement text — October 1

The radio-message constructor `0x004b71e0` now matches all 288 section bytes,
including its 16 relocations (277-byte retail body). Selecting the first speaker's
portrait through the frame member already assigned zero restores the observed
late table load. A different flat-storage source form yields the same exact body,
so the result proves compiled behavior rather than unique original source text.
The table read still precedes its clear; these checks do not establish prior
allocation contents or what later rendering observes. All 35 previous exact
address/symbol pairs and 44 other callable sections are preserved.

The Goodies requirement-text builder `0x0045a940` also matches its full 736-byte
section and 60 relocations (726-byte body). Both text lookups call `0x004f2580`;
using the existing direct PC lookup removes a forwarding wrapper without changing
the targets. The separate Goodies renderer remains unmatched. Lead private owners
in `bea-decomp/.worktrees/codex-equiv-20260930/local-data/` are
`messagebox-ctor-root-20261001/` and `goodies-match-root-20261001/`, each with a
fresh compiled `final-readback.json`. These checks do not establish visual or
audio acceptance.

## Retained August HUD map

The analyzed retail specimen maps `CHud` as a lifecycle, component-slot,
per-viewpoint overlay, battleline, and active-component render subsystem.

| Area | Representative static anchors |
| --- | --- |
| Lifecycle | `CHud__Init`, `CHud__Reset`, `CHud__LoadTextures`, `CHud__PostLoadProcess`, `CHud__ShutDown` |
| Component slots | `CHud__SetHudComponent`, `CHud__SwitchInOverlay`, `CHud__RenderOverlay`, `CHudComponent__RequestDestroy` |
| Viewpoint overlay | `CHud__RenderOverlayForViewpoint`, `CHud__RenderTargetIndicatorOverlay`, `CHud__RenderWorldTargetSprites`, `CHud__RenderTargetMarkers3D` |
| Objectives and weapons | `CHud__RenderObjectiveStatusPanel`, `CHud__RenderObjectiveSlotFillPanel`, `CHud__RenderSegmentedMeterBar` |
| Radar and status | `CHud__RenderTacticalRadarContacts`, `CHud__RenderControllerSlotStatusPanel`, `HudOverlay__DrawSpriteQuad` |
| Battleline/messages | `CHud__RenderBattleline`, `CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices`, `CMessageBox__RenderOverlay` |

High-level static calls connect game init/reset/load/shutdown to the HUD
lifecycle; cutscene start/stop/update to component selection; and
`CDXEngine__PostRender` to `CHud__Render`, battleline rendering,
`CHud__RenderOverlay`, and `CHud__SwitchInOverlay`, in that order. The three
corrected method identities and their bounded proof are owned by
[`hud-source-identity-correction-2026-08-12.md`](hud-source-identity-correction-2026-08-12.md).

Observed field-role hypotheses include active/pending component slots at
`this+0x1fc` / `this+0x200`, an initialized flag at `this+0x5c`, active
target/viewpoint context around `this+0x50..0x58`, and texture references around
`this+0x154..0x168`. These are not final class-layout names.

MissionScript command-name/handler evidence for HUD and variable operations is
owned by [`missionscript-iscript-static-contract.md`](missionscript-iscript-static-contract.md).
It does not prove visible flashing, variable display, or command effects.

This map supports reconstruction planning and scoped runtime questions. It does
not prove runtime ordering, visible HUD output, exact concrete layouts,
source-body identity, patch behavior, visual fidelity, or rebuild parity.
