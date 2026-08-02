# Lore errata

- **Status:** live. The record of what lore documents used to say wrongly, why it was
  wrong, and what settled it. Moved out of the articles themselves on 2026-08-01.
- **Evidence:** SOURCE — each entry cites the evidence that corrected it. The
  superseded text is quoted here verbatim; it is not quoted anywhere a reader goes.
- **Last updated:** 2026-08-01
- **Summary:** corrections lifted out of the shipped lore corpus, plus the questions
  they left open.

## Why this file exists

The lore corpus corrects itself in public, which is right, and it was doing it *in the
article*. A reader opening Community Preservation met this before any prose:

> **CORRECTED 2026-07-28.** This section previously read, in full:
> > **Modding limitations**: Main config file is encrypted. Limited traditional
> > modding potential.

Reprinting the wrong sentence to announce that it was wrong doubles the number of times
a reader meets it, and the second printing is the one in bold. The correction discipline
is worth keeping; the reader is the wrong audience for it.

**The standing rule, from here on:** shipped prose states the current best account, with
its date and evidence link. It never reprints its own former wrong text, and it never
contains a shell command. Both go here.

This is not a graveyard. Several entries below carry live open questions, and those are
the reason to read it.

---

## Corrections

### `community-preservation.md` — "the main config file is encrypted"

**Superseded 2026-07-28.** The Modding Surface section previously read, in full:

> **Modding limitations**: Main config file is encrypted. Limited traditional modding
> potential.

Both sentences were false, and the second followed from the first.

- `cardid.txt` (18 KB) is plain text with a documented grammar —
  [modding-reference.md](../game-assets/modding-reference.md).
- `defaultoptions.bea` (10,004 bytes) is a plain little-endian options snapshot written
  through `fopen`/`fwrite`/`fclose` with no crypt step —
  [game-folder-analysis.md](../game-assets/game-folder-analysis.md).

### `game-overview.md` — the `Maladim` cheat's effect

**Superseded 2026-07-28.** The cell previously read *"Cheat-gated runtime behavior;
visible gameplay effect is inconsistent in testing"*. Live-confirmed since: with
`Maladim` in the save name, the cheat-gated line appears in Controller Options as
`God OFF` / `God ON`, and while on, normal combat damage stops sticking. Already-lost
hull is not restored by toggling it back on —
[cheat-codes.md](../game-mechanics/cheat-codes.md).

### `technical-deep-dive.md` — the display resolution

**Superseded 2026-07-28.** The row previously read *"Hardcoded to 640x480, assumed
GeForce 3 card"*. MEASURED: `CD3DApplication__Init` sets 640x480 as the default
*creation* size only, `CD3DApplication__BuildDeviceList` enumerates adapter/device/mode
support, and `-res W H` overrides it down to a 640x480 minimum. The pinned GPL source
selects 640x480 out of an enumerated mode list too, so it is a default there as well.
GeForce 3 came from the post-mortem's dev-hardware inventory, not from a stated minimum
spec.

### `team-roster.md` — the date of the GPL source drop

**Superseded 2026-07-28.** The entry previously read *"(GPL-3.0, April 2025)"*. The drop
is **staged**, and dating it to April 2025 understated it by roughly 3.4x and misdated
the gameplay code this project ports from. MEASURED from the pinned repository's own git
history: `2025-04-10` published LICENSE, README and 30 platform, memory and controller
files (`0fa6b19` +2, `f4ca46d` +30); `2025-12-12` added 76 more including the
`BattleEngine*` gameplay code (`24939a6` +72, `ac5eff7` +2, `a073df7` +2). The pinned
checkout is **108 files at `5352a81` (2025-12-12)**, and 2 + 30 + 72 + 2 + 2 = 108
exactly. Commits after that point on `origin/main` add and then remove tooling and
dotfiles, not source, and are not in the pinned checkout.

### `_index.md` and `reference-materials.md` — hand-maintained date footers

**Superseded 2026-07-28.** Both files carried a footer stating a "last updated" date
that was false about its own file — `_index.md` claimed 2026-03-05 against a real last
content change of 2026-07-16 (`ca9fe1c7`); `reference-materials.md` claimed December
2025 against 2026-07-11 (`5a7bacec`). Hand-maintained footers drift because nothing
re-reads them. Both footers are gone; git holds the dates, and the header block holds
the maintained one.

---

## Open questions

These are live. They are the reason this file is worth opening.

### The spliced sentence in the GDM post-mortem quotation

`development-history.md` carries a post-mortem quotation whose opening sentence is
truncated to `[…]` because it could not be verified. The archived source PDF is a
maintainer-local path and is absent from this machine, so nobody has read the original
line.

**Do not reconstruct it.** This is the same standard that removed 33 invented cutscene
titles: a plausible sentence nobody can source is worse than a visible gap. It stays
truncated until someone reads the archived PDF.

### Whether the fiction shelf is first-party text

`characters.md` claims to be "drawn from the game's own character bios and briefings",
and `battle-engine-tech.md` says its Kiralova memo is "reproduced as authored". Neither
has ever been checked against the game.

This is now cheap to settle. The game's own text table holds ~2,571 developer-written
strings, and `OnslaughtCareerEditor.AppCore/GameTextCatalog.cs` decodes it from any
installation. One run, diffed against the bios and the memo, answers whether the fiction
shelf is first-party text or a transcription from an archived website — and determines
what a campaign document may quote.

**Until it runs, the in-universe fiction text is edit-frozen.** "Reproduced as authored"
is the same principle as never synthesizing a `.bes` save: if it is authored text, it is
not ours to tighten.

### The PC port developer's surname

Recorded in [attribution.md](attribution.md), not here — the lead, why it is weaker than
it looks, and what would settle it.
