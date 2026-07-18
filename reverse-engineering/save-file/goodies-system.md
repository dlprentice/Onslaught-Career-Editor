# Goodies save and unlock contract

This document owns the public format boundary and the evidence needed to interpret the product. Exact unlock descriptions are implemented once in [`GoodieUnlockRequirementService.cs`](../../OnslaughtCareerEditor.AppCore/GoodieUnlockRequirementService.cs), backed by the pinned source references [`Career.cpp`](../../references/Onslaught/Career.cpp) and [`FEPGoodies.cpp`](../../references/Onslaught/FEPGoodies.cpp).

## Save layout

`CCareer` stores 300 four-byte Goodie states. The retail save view used by AppCore is:

```text
offset(index) = 0x1F46 + index * 4
displayable indices = 0..232
reserved indices = 233..299
storage end = 0x23F6 (exclusive)
```

| Dword | Meaning | UI state |
| ---: | --- | --- |
| `0` | unknown | Locked |
| `1` | instructions available | Locked with hint |
| `2` | newly unlocked | Gold badge |
| `3` | previously viewed | Blue badge |

Steam `CFEPGoodies__Render` (`0x0045E0D0`) confirms that states `0` and `1`
both keep the dark interior. State `0` uses the gray tight ring; state `1` uses
the pale/white tight ring and can display the unlock hint. Neither ring is the
cursor. Selection is a separate animation that expands the selected ring to
`1.25x` and rotates it by up to 45 degrees. State `2` renders gold and state `3`
renders blue. Stuart's `FEPGoodies.cpp` has the same state switch. Horizontal
wall panning changes projected screen position, not the cursor coordinate used
by `get_goodie_number`.

AppCore accepts only a real `10004`-byte, version-`0x4BD1` baseline, refuses in-place Goodie patching, limits writes to displayable indices, and preserves unselected and reserved bytes. [`BesFilePatcher.cs`](../../OnslaughtCareerEditor.AppCore/BesFilePatcher.cs) and its focused tests are the implementation authority for this contract.

MissionScript handlers use one-based indices:

```text
script index = save index + 1
save offset = 0x1F46 + (script index - 1) * 4
```

Script index `0` is invalid and would underflow the Goodie array.

## Unlock ownership

The product's source-backed rules cover:

- sequential character bios at indices `0..7`;
- campaign, kill-count, boss, and race unlocks through index `70`;
- three source-backed image Goodies at `71..73`;
- S-rank developer items at `74..77`;
- C-, B-, and A-grade concept-art bands at `78..200`;
- cutscene-driven FMV entries at `201..232`;
- reserved-byte guidance at `233..299`.

Mission scripts unlock save indices `50`, `52`, and `67..70`. FMVs are set by game cutscene handlers rather than `CCareer__UpdateGoodieStates`; save index `232` maps to cutscene `33` because cutscene `32` is absent.

The source table label for Goodie `66` suggests A grades, but the recomputation path counts 26 C-or-better campaign grades. The recomputation behavior is the current authority unless controlled retail runtime evidence establishes a divergence.

## Resource and wall evidence

The checked PC install contains 232 matching Goodie archives for 233 displayable save slots. Parsed `GDAT` families were:

| Kind | Interpreted family | Count |
| ---: | --- | ---: |
| `0` | texture/artwork | 149 |
| `1` | model/gallery | 45 |
| `2` | video/cutscene | 33 |
| `3` | level/metadata | 5 |

Every parsed archive's embedded Goodie index matched its filename index. Save index `232` is the only displayable slot without a matching `goodie_232_res_PC.aya` in that corpus.

Goodies `71..73` have source data-table entries, unlock/instruction hooks, and shipped texture-only archives (`ca_be_final01`, `ca_be_final02`, and `ca_bea_battle_pic`). A controlled copied-profile observation of ordinary top-row navigation returned `66, 67, 68, 69, 70, 74`, not `71..73`. The WinUI catalog may preview those shipped artwork resources, but hidden or indirect in-game wall reachability remains unproven.

## Bounded retail consumption

Stuart's in-house PC source establishes the four-byte state shape and state meanings, but its frontend implementation and addresses do not define the console-derived Steam release. The checked Steam executable owns the offsets used here: `CCareer__Load` copies the serialized career from file offset `0x0002`, the retail Goodie array begins at file offset `0x1F46`, and `CFEPGoodies` maps wall coordinate `(2,0)` to save index `2`.

A controlled WinUI/AppCore A/B used disposable copies of one real `10004`-byte, version-`0x4BD1` career save. The control retained Goodie `2 = 0`; the edited output set its dword at `0x1F4E` to `2`. The output differed only at byte `0x1F4E` (`00` to `02`); all other bytes, including reserved indices `233..299`, matched, and the source hash was unchanged. Same-file output and a new output inside the installed game tree were both rejected without creating or changing a file.

Both app-owned game copies had the same verified copied `BEA.exe`. Before any Goodies-wall interaction, automated retail selection of the sole staged save exposed runtime states `1,0,0` for Goodies `1..3` in the control and `1,2,0` at the same addresses in the edited arm. With the live `CFEPGoodies` object at its checked retail vtable and cursor `(2,0)`, the edited cell was gold and exposed `Unlocked! Col. Chuck Kramer`; opening it changed the live state from `2` to `3`, turned the cell blue, and displayed the Kramer image. The control target remained dark at raw state `0`. Process memory before selection, the live cursor, the retail mapper, the label, and the automatic state transition establish the identity; ring appearance alone does not. The Steam load flow also rewrote the copy's `defaultoptions.bea` as an exact mirror of the selected save buffer before wall interaction, independently confirming which buffer it consumed. The staged save and mirror remained byte-identical to the edited output after the live `2`-to-`3` transition, so persistence of the viewed state was not established.

The tested save was named `Maladim`, which makes retail cheat index `3`
available for the unrelated God-mode menu option. Fresh Steam decompilation shows
that `CFEPGoodies__Process` checks only indices `0` (`MALLOY`) and `5`
(`latête`), so that name did not activate an all-Goodies display override. This
establishes causality for Goodie `2` load, wall display, and live state
transition only; it is not a generic no-cheat runtime baseline.

## Corrected offset boundary

The former aligned-view note that treated `0x22D4` as `mCareerInProgress` was wrong:

```text
Goodie 228 = 0x1F46 + 228 * 4 = 0x22D6
mCareerInProgress = file offset 0x248A
```

Writing a progress flag at `0x22D4` corrupts the neighboring Goodie dword. AppCore uses the true view and must preserve this correction.

## Claim boundary

Source tables and static retail evidence establish layout and likely unlock ownership. Copied-save tests establish broad byte preservation, and the bounded retail A/B above establishes Goodie `2` load, wall display, and live transition from new to old. It does not establish disk persistence after that transition, every runtime wall path, retail/source identity for every rule, or rebuild parity. No game payload, private artifact path, or installed-game mutation belongs in this repository.
