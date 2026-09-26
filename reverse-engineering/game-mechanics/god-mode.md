# God mode

Status: active contract
Last updated: 2026-09-26 (rewritten by the RE audit: the saved per-player flags at file 0x2496 and 0x249A)
Summary: god mode is per-player state saved in the career at file offsets 0x2496 (player 1)
and 0x249A (player 2). The player loads it when it is built and applies it to its Battle
Engine; the Maladim cheat only adds the pause-menu item that shows and toggles player 1's flag.
Evidence: MEASURED — pristine instructions and the tracked gold save; SOURCE — `Player.cpp`,
`Career.cpp`/`Career.h`, `BattleEngine.cpp`, `BattleEngineJetPart.cpp`, `PCGame.cpp`; runtime
notes from 2026-03-15 and 2026-03-29 on a patched-for-windowed Windows install, with no
archived capture. The effect of a saved flag without the cheat name is static only.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; gold save
`tests_shared/fixtures/gold_career_save.bin`.

An earlier version of this page said the Steam build had reused these words for invert-Y
settings and that god mode was not persisted. Both claims were wrong; Git keeps that version.

## Where the flags live

- `CCareer::mIsGod[2]` (`Career.h:204`) sits at career `+0x2494` and `+0x2498`, which are
  file offsets `0x2496` (player 1) and `0x249A` (player 2). In memory they are `0x00662ab4`
  and `0x00662ab8` (the career object is at `0x00660620`).
- `CCareer::Blank` clears both (`0x0041b8cd`, `0x0041b8d3`; `Career.cpp:229`). `CCareer::Load`
  copies the whole `0x92f`-dword block, flags included (`0x00421236-0x00421243`).
- The Steam career block is 8 bytes longer than the source's (`0x24BC` against `0x24B4`)
  because the invert-Y array grew from two entries to four (`+0x249C`-`+0x24A8`). `mIsGod`
  was not moved or reused. The field table is in [save-format.md](../save-file/save-format.md).

## What the flags do

- **Player construction.** `CPlayer::CPlayer` loads its flag from
  `[0x00662ab0 + 4 × number]` (numbers are 1-based) into `+0x20` (`0x004d27f3-0x004d27fe`),
  as `Player.cpp:33` (`mIsGod = CAREER.GetIsGod(mNumber-1)`).
- **Battle Engine assignment.** When `+0x20` is nonzero, `AssignBattleEngine` calls the
  Battle Engine's `SetVulnerable(0)` (vtable `+0xe0`, `0x00405e30`: `+0x15C` = argument) and
  `SetInfinateEnergy(1)` (vtable `+0x154`, `0x00405f20`: `+0x160` = argument, then `+0xFC`
  = the configuration's `+0x20`) (`0x004d30a1-0x004d30ba`). The Battle Engine vtable is
  `0x005d89c4`.
- **`CPlayer::SetIsGod`** (`0x004d3020`, `Player.cpp:221-243`) stores the player's `+0x20`
  and the career word, then, if the player has a Battle Engine (`+0x1c`): for a value of 1,
  `SetVulnerable(0)` and `SetInfinateEnergy(1)`; otherwise `SetVulnerable(1)` and
  `SetInfinateEnergy(0)`. A nonzero value also increments the player's `+0x3c`
  (`IncStat(PS_CHEATED)`, `Player.cpp:240`; `0x004d3070`).
- **Damage.** `CBattleEngine::Damage` (`0x0040A890`) restores the life, shields and energy it
  snapshotted in its prologue when `+0x15C` (`mVulnerable`) is 0, as `BattleEngine.cpp:2234`:

  ```
  +0x035a  8b 86 5c 01 00 00    mov   eax, [esi+0x15C]      ; mVulnerable
  +0x0360  85 c0                test  eax, eax
  +0x036e  75 1e                jnz   +0x1e                 ; non-zero -> damage stands
  +0x0370  8b 54 24 04          mov   edx, [esp+0x04]       ; life,    from the prologue
  +0x0374  8b 44 24 08          mov   eax, [esp+0x08]       ; shields, from the prologue
  +0x0378  8b 4c 24 0c          mov   ecx, [esp+0x0C]       ; energy,  from the prologue
  +0x037c  89 96 f8 00 00 00    mov   [esi+0x0F8], edx      ; life restored
  +0x0382  89 86 00 01 00 00    mov   [esi+0x100], eax      ; shields restored
  +0x0388  89 8e fc 00 00 00    mov   [esi+0x0FC], ecx      ; energy restored
  ```

  It undoes each hit taken while the flag is 0; it does not heal damage taken earlier. (The
  listing leaves out a harmless `fadd`/`fstp` of `+0x604` between these instructions.)
- **Energy.** The jet part skips its energy drain while `+0x160` is nonzero
  (`0x00410ca2`, `BattleEngineJetPart.cpp:313`), so god mode also gives infinite energy.
- **The cheat statistic.** The source's only reader of `PS_CHEATED` is the PC statistics
  line "CHEATER!" (`PCGame.cpp:170-174`); that string is not in the retail image, so the
  statistic has no known effect in retail.

## What gates it

- **Cheat names.** `IsCheatActive` (`0x00465490`) XORs the table at `0x00629464`
  (`0x100` bytes per entry) with the key `HELP ME!!` (`0x00629a64`): 0 `MALLOY`, 1 `TURKEY`,
  2 `V3R5IOF`, 3 `Maladim`, 4 `Aurore`, 5 `latête`. It searches the save name
  (`FromWCHAR`) for the entry with a case-sensitive `strstr` (`0x0055ea80`), so the name
  may contain it anywhere. A nonzero `[0x00662df4]` or byte `[0x00679ec1]` turns every
  cheat on.
- **Pause menu.** `IsCheatActive(3)` decides whether the god item exists
  (`0x004ce314-0x004ce322`). Its label follows player 1's flag (`cmp [0x00662ab4],1`,
  `0x004ce328`: God ON or God OFF). Pressing it calls `SetIsGod` on player 1
  (`[0x008a9d3c]`, `0x004d0b19-0x004d0b55`). Pause virtual 6 re-applies the flag through
  `SetIsGod` (`0x004d1132-0x004d114a`).
- **Debug button.** `CGame::ReceiveButtonAction` case 0 (`BUTTON_TOGGLE_GOD_MODE`,
  `Controller.h:91`; jump table `0x0046faa4` → `0x0046f7fa`) toggles `SetIsGod` for all
  four players. The handler survives in retail; no default PC binding row maps action 0.
- **The saved flag needs no cheat.** Nothing on the construction or assignment path tests
  a cheat, so a save whose `0x2496` is nonzero makes player 1's Battle Engine invulnerable
  whatever the save is named. This is static; see the open questions.

## Runtime notes (2026-03-15 and 2026-03-29)

Observed on a Windows install patched for windowed play, without an archived capture:
- `Maladim` in the save name exposed `God OFF` / `God ON` under **Controller Options** in
  the pause menu, and toggling it changed the label.
- With `God ON`, normal combat damage no longer depleted the shields.
- Turning `God ON` again after losing shields refilled a bar at once; hull already lost
  stayed lost.

The toggle path writes energy (`+0xFC`, through `SetInfinateEnergy`) and nothing on it
writes `+0x100` (shields) or `+0xF8` (life), so which bar refilled is open.

## The internal source build

The pinned source uses different cheat names (`FEPSaveGame.cpp`): `105770Y2` (all goodies),
`!EVAH!` (all levels), `V3R5ION` (version display) and `B4K42` (god mode available).
`IsCheatActive` there also returns true on a PS2 development kit (`FEPSaveGame.cpp:556-559`).
The persistence path is the same as retail's.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| Whether a saved flag alone makes the Battle Engine invulnerable | Set `0x2496` = 1 in a copy of a save not named Maladim, start a level, and read `CBattleEngine+0x15C` (expect 0) |
| Which bar refilled when the toggle was turned on again | Log `+0xF8`, `+0xFC` and `+0x100` across one toggle in a copied runtime |
| Whether water and other hazards bypass the restore | Log `Damage` calls and `+0xF8` while a god-mode Battle Engine enters deep water |
