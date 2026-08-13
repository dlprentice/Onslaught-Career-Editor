# Function naming convention: which vocabulary wins

Status: proposed convention, decided by the agent under explicit maintainer delegation
Last updated: 2026-08-12
Evidence: MEASURED — the shipped error strings, script-command registry, argument
arity and callee evidence gathered across this session; UNKNOWN — whether the
maintainer prefers a different house style, which would override this.
Verdict: three tiers, applied per row, with the binary's own words ranked above
the game's script vocabulary and both above description.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Why this document exists

Two frontiers stalled on the same question: when the shipped image offers more
than one name for a function, which one goes into Ghidra? The maintainer was
away and delegated decisions, so the convention is decided here rather than left
blocking. **It is a proposal in force until overridden**, and it authorises no
Ghidra mutation — promotion remains gated.

## The three tiers

**Tier 1 — a shipped string names the C++ function. That name wins.**
This is a recovered symbol, not an inference. The decisive case:
`0x00533B70` and `0x00533EB0` carry the shipped strings
`FATAL ERROR: null thing passed to 'Create3PointPanCamera'` and its four-point
counterpart, while the script registry calls those slots `Goto3PointPanCamera`
and `Goto4PointPanCamera`. The existing `IScript__Create3PointPanCamera` is
**correct and must not be replaced** — adopting the registry string would destroy
a symbol the binary hands over directly.

**Tier 2 — no shipped symbol, but the script-command registry names the slot.
Use the registry command.**
The registry is the game's own vocabulary for that handler, written by the
developers, and it beats any description invented later. Apply it with the
existing `IScript__` prefix, e.g. `IScript__GetRealHealth` for `0x005359D0`.
Record in the function's document that the name is the script-facing command and
not a proven C++ symbol.

**Tier 3 — neither exists. Use a descriptive name the body supports, and label
it descriptive.**
The four refuted HUD names fall here. A Tier 3 name is a working label; it must
be replaceable without ceremony when Tier 1 or 2 evidence appears, and the
document must say it is descriptive so the next reader does not mistake it for
recovered.

## Consequences for the two blocked frontiers

**The five message natives.** Tier 2 applies: no shipped string names them. The
suffixes `WithCallback`, `WithFade` and `WithPriority` are inventions and go;
the registry names replace them. Note that the `PlaySound` stem was defensible —
the queue does reach voice through `CMessageBox__StartVoiceOrFallbackTextReveal`
— so this is a Tier 3 label losing to Tier 2 evidence, not a correction of a
false claim.

| Address | Current | Proposed (Tier 2) |
| --- | --- | --- |
| `0x00537410` | `IScript__PlaySound` | `IScript__AddMessage` |
| `0x00537500` | `IScript__PlaySoundWithCallback` | `IScript__PlayCharMessage` |
| `0x005375F0` | `IScript__PlaySoundWithFade` | `IScript__PlayCharMessageWait` |
| `0x005377E0` | `IScript__PlaySoundWithPriority` | `IScript__PlayPCharMessage` |
| `0x005378E0` | `IScript__PlaySoundWithFadeAndPriority` | `IScript__PlayPCharMessageWait` |

**The four HUD names.** Tier 3 applies, and the honest consequence is that
**renaming should wait**. Target 0 and target 5 are refuted — no controller
involvement, and weapon ammo rather than objective slots — but replacing one
descriptive label with another buys little and risks repeating the mistake. The
better move is to leave the refutation recorded in
`local-lab/pc-hud-static-join-20260812-v1/NOTE.md` and rename only when a body
reading establishes what each actually renders. Deciding the convention does not
oblige using it.

## What this does not authorise

No Ghidra mutation. Promotion of any name above still requires the full gate in
[`../ghidra/README.md`](../ghidra/README.md): identity, off-volume backup with a
proven restore, isolated scratch replicas, rollback probes, separate-process
dry-run/apply/readback, collateral and alias checks, POST backup, and tracked
snapshot refresh on byte equality.
