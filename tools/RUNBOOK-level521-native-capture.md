Status: blocked historical runbook — do not execute on the Omarchy host.
Last updated: 2026-08-31 (Linux migration routing; historical measurements and
commands retained as provenance, no current capture owner designated).
Evidence: MEASURED — the reachability table in the appendix is read from the
shipped `data/MissionScripts/level521` scripts (`ResearchCentre.msl:28`,
`LevelScript.msl:81`, `hive.msl:351`/`:474`, verified independently in the main
loop), and the "opening fires none of the 17" claim is measured against the
historical level-521 coverage index at
`G:\bea-ttd\q-campaign-coverage-v1\`. That drive-letter path records where the
Windows campaign ran; it is not current routing. INFERRED — the per-native
timings after the cascade and the "13 of 17 in ten minutes" yield, which depend
on whether `Pause(n)` is wall-clock or frame-driven under TTD; that is
unmeasured and is why take 2 was sized at 300 s rather than tight.
Summary: preserved instructions and evidence for a historical level-521 TTD
session. Copied-game execution and TTD recording are Windows-only. The isolated
Windows VM is staged but not activated, and no guest-owned trace destination
has completed qualification.

# Historical runbook: capture the level-521 script natives

> [!WARNING]
> **CURRENT ROUTE: BLOCKED.** Do not run these commands on Omarchy, reinterpret
> `G:` as a Linux path, or create a replacement destination by analogy. Live
> copied-game execution and TTD recording wait for activation of the isolated
> Windows VM, its own checkout and copied specimen, and an explicitly supplied,
> validated guest `TraceRoot`. The procedure below remains verbatim enough to
> preserve what was measured on Windows; it is not an executable current
> front door. Offline reading and analysis of already-recorded evidence remain
> valid where their inputs are available.

> **CORRECTION 2026-08-02, MEASURED — READ BEFORE SIZING ANY TAKE.**
> **TTD slows the game about 62×.** A 301-second recording of this level
> captured **97 simulation ticks = 4.85 seconds of game time**. Measured four
> independent ways (UpdateAutoAim 97, GetInterpolatedAutoAimPos 98,
> CHiveBossGuide::VFunc_3 97, Walker+Jet Move 95+2=97), with retail's own clock
> confirming 20 Hz (`mLastDamageTime` steps by exactly 0.05 s). Evidence:
> `local-lab/TTD-COMBAT-TRACES-2026-08-02.md`.
>
> **Every duration in this runbook was written in RECORDED seconds and is
> therefore wildly optimistic about what it captures.** The real conversion:
>
> | you record | you capture |
> | --- | --- |
> | 60 s | ~1 s of game time |
> | 300 s | ~5 s of game time |
> | ~62 min, ~164 GiB | 60 s of game time |
>
> **Consequences for how to run this session.** The one-shot triggers below are
> still worth catching, because a trigger is an instant, not a duration — but
> anything described here as "wait and watch" does not work: the boss cascade's
> ~60 s of scripted `Pause` calls would need roughly an hour of recording and
> would blow the 32 GiB cap first. `PlayAnimationWait` was recorded as a miss in
> the 2026-08-02 session and that is NOT an anomaly — the take was ~5 s of game
> time and the animation fires 25–60 s in.
>
> **What actually works:** start recording IMMEDIATELY before the instant you
> care about, keep takes SHORT, and take many of them. Sizing by wall clock is
> the mistake; size by the number of game ticks you need.

## 1. Why this session exists

Fifty-one of the 144 MissionScript natives are written into the shipped mission
scripts but were never seen executing in any of the sixty-six recorded level
openings. **Level 521's own scripts author seventeen of them — more than any
other single level.**

The seventeen: `Die`, `GetGoodieState`, `GetMapHeight`, `GetX`, `GetY`, `GetZ`,
`LevelLostString`, `LevelWon`, `PlayAnimationWait`, `ResetSegmentHealth`,
`SetGoalPoint`, `SetGoodieState`, `SetSegmentVulnerable`, `SetZ`,
`ShutdownVariable`, `SpawnParticle`, `UnsetObjective`.

**Starting the level does not reach a single one of them.** The 181-second
level-521 opening covered seventeen natives, and not one was on this list — the
scripts that run at level start (`Setup.msl`, `LevelScript.msl`'s `init()`, the
hive's `init()`) call an entirely different set. Every one of the seventeen sits
behind a player action. That is what this session is for.

The good news is that the actions are few. **One kill — the Muspell Research
Station — cascades into twelve of the seventeen within about a minute**, with no
further input required beyond staying alive to watch.

## 2. What you must do in the game, and what each action buys

| # | Player action | Natives it reaches | Confidence |
|---|---|---|---|
| A | Destroy **any one** turret (or the research station) | `UnsetObjective` | High |
| B | Destroy **all eight** turrets (5 Gun + 3 Cannon) | `ShutdownVariable` | High |
| C | Destroy the **Muspell Research Station** | `GetX`, `GetY`, `GetZ`, `SpawnParticle` (instant); `ResetSegmentHealth`, `SetSegmentVulnerable`, `Die` (about 8 s later); `GetMapHeight`, `SetZ`, `SetGoalPoint` (about 10 s later); `PlayAnimationWait` (about 25–60 s later) | High |
| D | **Kill the hive boss** | `LevelWon`; and `GetGoodieState` / `SetGoodieState` if you have also killed 25 or more Gnats | Low — see §7 |
| E | **Lose the level** (let the Marshall die, or let your ground force drop below 3 units) | `LevelLostString` | High that it works; mutually exclusive with D |

Steps A and B are the level's first objective and you will do them anyway.
Step C is the trigger that matters. Steps D and E are terminal and are honestly
out of reach of a ten-minute session — plan for **13 of 17** and treat the last
four as a separate, longer run.

**Free with the same window.** Step C also executes nine natives that the corpus
has seen only one to three times each — `CreatePosition`, `SpawnThing`,
`Damage`, `Rand`, `IsA`, `GetDistToObj`, `PlayAnimation`, `SetAllegiance`,
`Activate`. Two of them (`Damage`, `IsA`) need one extra deliberate act: **fly
your battle engine into the hive boss** so it touches you. The analysis step
reports these separately.

## 3. Historical prerequisites (not currently satisfiable)

The following bullets describe the retired Windows session. They do not
describe the present Omarchy host or an activated guest:

- **No save and no career unlock is needed.** The game accepts `-level N` on the
  command line and goes straight into that mission; the sixty-six-level campaign
  recorded level 521 exactly this way. The helper launches
  `BEA.exe -skipfmv -level 521` for you. (`-skipfmv` skips the FMV; a
  click-to-start prompt may still appear.) See
  [`reverse-engineering/quick-reference/cli-parameters.md`](../reverse-engineering/quick-reference/cli-parameters.md).
- **The historical session used one elevated PowerShell 7 window for the whole
  session.** TTD recording needs an elevated token and that Windows machine had no
  `TTDService`. From an elevated window there is no prompt at all between takes.
  From a normal window the helper still works, and launches the game
  unelevated — but raises one UAC prompt per take.
- **The historical `G:` capture owner needed room.** Budget was about 2 GB per
  recorded minute; a full session was roughly 12 GB. `G:` is retired topology,
  not a destination to reuse.
- **Nothing else BEA-shaped may be running.** The helper refuses to continue if a
  BEA that is not the copied target is up.

## 4. Historical session procedure (blocked; do not execute now)

These commands document the measured Windows procedure. They remain blocked
until the VM and an explicit guest `TraceRoot` are activated and this runbook is
requalified against them.

1. **Start take 1 and launch the game.** From the repository root:

   ```powershell
   pwsh -File tools\Record-Level521Session.ps1 -Take 1 -Seconds 60 -MaxFileMB 4096
   ```

   It launches the copied target at level 521, prints the plan, and waits. Write
   down the session stamp it prints (for example `20260731-1830`); every later
   take and the analysis step use it.

2. **Play at full speed** — nothing is being recorded yet. Destroy seven of the
   eight turrets. Leave the eighth alive and get into position on it.

3. **Press Enter in the PowerShell window.** Approve the UAC prompt if you get
   one, go back to the game, then destroy the eighth turret. The game becomes a
   slideshow while recording; that is expected. It runs 60 seconds and then
   speeds back up, leaving the game running.

   *Reaches: `UnsetObjective`, `ShutdownVariable`.*

4. **Play at full speed again.** Get to the Muspell Research Station, line up a
   shot that will kill it, and hold.

5. **Start take 2 from the same window** (substitute your own stamp):

   ```powershell
   pwsh -File tools\Record-Level521Session.ps1 -SessionStamp 20260731-1830 -Take 2 -Seconds 300
   ```

   Press Enter, then **destroy the research station**.

6. **Now do almost nothing for the rest of the take.** The boss sequence is
   entirely script-driven. Stay alive, keep the boss on screen, and — once it has
   lifted off — **fly into it once** to trigger the contact-damage handler. Do not
   quit, do not let your ground force be wiped, and do not let the level end.

   *Reaches the other ten of the twelve, plus the second-observation set.*

7. **When the take ends, the game is still running.** Either stop here or, if you
   want to attempt the hive-boss kill, run take 3 with a longer window and go for
   it. Otherwise quit the game normally.

## 5. When to attach, and why after the level has loaded

Attach **after** the level is loaded and running, immediately before each trigger
action — never at launch.

Two reasons, both measured. First, none of the seventeen natives fires during
loading or the opening minutes; a trace that starts at launch spends its whole
budget on code the corpus already covers 40% of. Second, TTD instruments every
instruction, so a game launched under it is unplayable — and these natives need
you to *play*. Attaching is what lets you cross the level at full speed and pay
the slowdown only across the sixty seconds that matter.

## 6. How long to record, and why not longer

Recording costs about **34 MB/s** — the level-521 opening wrote 5.71 GiB in 181
seconds. So:

| Take | Duration | Trace size |
|---|---|---|
| 1 (last turret) | 60 s | about 2 GB |
| 2 (research station + boss cascade) | 300 s | about 10 GB |

Take 2 is deliberately about five times the script-side length of the cascade.
The scripts' own `Pause()` calls add up to roughly one minute, but **how long
those Pause calls take in wall-clock while TTD is slowing the game has not been
measured** — that is the single biggest uncertainty in this plan, and the wide
window is how it is absorbed. If the analysis comes back with everything except
`PlayAnimationWait`, the take was too short; rerun take 2 at `-Seconds 600
-MaxFileMB 32768`.

Do not simply record the whole session in one long take. The recorder's hard
ceiling is 32 GiB — about sixteen minutes — and a trace that hits the cap while
the game is still running is reported `max-file-aborted` and is incomplete. The
helper refuses any `-Seconds`/`-MaxFileMB` pair that would land within 10% of the
cap.

## 7. Why the last four are probably out of reach

`LevelWon`, `GetGoodieState` and `SetGoodieState` all sit inside the *Hive Dies*
handler, so they need the hive boss actually killed — a boss fight with 27
vulnerable segments, respawning Gnats and Arachnadrones, and a hard lose
condition if your ground force drops below three units. The two goodie natives
additionally need **25 or more Gnats killed** first, and gnats arrive four at a
time roughly every twenty seconds. Ten minutes is not that fight.

`LevelLostString` needs you to *lose* — cheapest by letting the Marshall be
destroyed — and it cannot be combined with `LevelWon` in one run.

Plan the session for thirteen. Treat the remaining four as a separate,
play-to-completion capture, which is a different instrument shape anyway.

## 8. Historical verification procedure

The historical session used this command from a normal (unelevated) Windows
window. It is preserved for provenance, not offered as a current route:

```powershell
pwsh -File tools\Test-Level521NativeCoverage.ps1 -TracePattern 'level521-native-20260731-1830-take*'
```

It runs the landed coverage collector over every take and prints a checklist:

```
  [x] UnsetObjective        0x00535EE0  any turret, or the research station, dies
  [x] ShutdownVariable      0x00536330  ALL EIGHT turrets destroyed
  [ ] GetX                  0x00534B80  research station destroyed (boss start, t+0s)
  ...
  13 of 17 covered.
```

Budget about four minutes per 6 GB trace. It needs no elevation and it never
writes inside a trace directory.

**Read the checklist, not the runner's status lines.** The coverage runner can
label a perfectly valid trace `failed` when the replay ends on an adjudicated
Thread stop (task #155) — eight of the sixty-six corpus levels were mislabelled
that way and every one was valid. This script ignores the runner's log and
decides from each per-trace receipt instead, so its `OK` / `UNUSABLE` lines are
the ones to trust.

## 9. Historical destinations (not current routing)

All `G:` paths below are literal receipt provenance from the retired Windows
layout. A future activated guest must receive a separately validated, explicit
`TraceRoot`; none is designated here.

| What | Historical Windows location |
|---|---|
| Traces | `G:\bea-ttd\level521-native-<stamp>-take<N>\` |
| Recorder receipt (the truth about a take) | `…-take<N>\receipt.json` |
| Coverage output | `G:\bea-ttd\q-level521-native-<stamp>-take\` |
| Coverage receipt per take | `…\<trace name>\receipt.json` |

A healthy take has `guestOutcome: "alive-at-stop"` — the game was still running
when the timer stopped tracing, which is exactly what an attach capture should
look like. Anything else deserves a read before you trust the trace.

## 10. If something goes wrong

| Symptom | What it means |
|---|---|
| `Trace output already exists` | That take number is used. Move to the next `-Take`, or start a new session stamp. |
| `A BEA.exe that is NOT the copied target is running` | The Steam copy is up. Close it — it is a deliberately patched binary and is never a specimen. |
| `guestOutcome: max-file-aborted` | The cap was hit while the game was still running. Incomplete. Re-take with a bigger `-MaxFileMB`. |
| `guestOutcome: exited-error` | The game died. Most often the working directory was wrong; the helper pins it, so read the receipt's `guestFatalError`. |
| Everything hit except `PlayAnimationWait` | Take 2 was too short. Re-take at `-Seconds 600 -MaxFileMB 32768`. |
| Nothing at all hit in take 2 | The research station probably did not die inside the window. Check the level's objective feed before re-taking. |

## 11. Reading the result honestly

A covered entry byte proves those bytes executed inside the recorded window. It
does **not** prove the named native is what ran — a shared or short handler body
can be entered from elsewhere. A miss is non-observation inside this window,
never absence from the game.

---

## Appendix — where these claims come from

You do not need this to run the session. It is here so the plan can be checked
rather than believed.

Every line below was read from the shipped scripts under
`data/MissionScripts/level521/` of the copied pristine target. Handler addresses
come from the 144-row native registry decoded from `BEA.exe.original.backup`
(sha256 `74154bfa…`); `Test-Level521NativeCoverage.ps1` re-verifies them against
that registry at run time and refuses to score if they disagree.

| Native | Authored at | Containing block |
|---|---|---|
| `UnsetObjective` | `Turret.msl:28`, `ResearchCentre.msl:27`, `hive.msl:73` | `died()` |
| `ShutdownVariable` | `LevelScript.msl:72` | `event("Turret Destroyed")`, guarded `numTurrets == 0` |
| `GetX` / `GetY` / `GetZ` | `hive.msl:354` (+ `167`, `252`, `275` for `GetZ`) | `event("Start Hive Boss")`, first statement |
| `SpawnParticle` | `hive.msl:355`, `469` | `event("Start Hive Boss")` |
| `ResetSegmentHealth` | `hive.msl:388–443` (27 calls) | `event("Start Hive Boss")`, after `Pause(4.0)` |
| `SetSegmentVulnerable` | `hive.msl:389–444` (27 calls) | same, interleaved |
| `Die` | `hive.msl:459`, `arachnid.msl:30`, `gnat.msl:25` | `event("Start Hive Boss")`; `event("All Hive Children Die")` |
| `GetMapHeight` | `hive.msl:167,170,252,255,275,279` | `event("State Hive Lift Off")` and the rise/fall loops |
| `SetZ` | `hive.msl:170,255,279` | same loops |
| `SetGoalPoint` | `hive.msl:171,256,280`, `HiveMovement.msl:49` | same loops |
| `PlayAnimationWait` | `hive.msl:87,111,134,156,195` | `event("State Release Gnats")` / `("State Release Spiders")` |
| `LevelWon` | `LevelScript.msl:104` | `event("Hive Dies")` |
| `GetGoodieState` | `LevelScript.msl:100` | `event("Hive Dies")`, guarded `deadGnats >= 25 && …` |
| `SetGoodieState` | `LevelScript.msl:102` | same `if` body |
| `LevelLostString` | `LevelScript.msl:42`, `54`, `110` | `init()` watchdog loop; `event("Marshall Destroyed")` |

**None of these sits in an `init()` block**, which is why starting the level
reaches none of them. The chain that step C sets off is
`ResearchCentre.msl:28` → `LevelScript.msl:81` → `hive.msl:351` →
`hive.msl:474` → *State Release Gnats*.

**The hive script is already live at level start.** `Teleport` and
`SetAllSegmentsVulnerable` are authored nowhere in level 521 except `hive.msl:57`
and `:59`, and the opening covered both — so the boss object exists and its
`init()` ran. It simply never activates.

Four things are **not** verified and could change the plan:

- **`blah.msl` looks like it auto-starts the boss and does not.** `blah.msl:23-24`
  is `Pause(10); PostEvent("Start Hive Boss");`. If it were bound to a live thing
  the boss would start ten seconds into every level open — but the 181-second
  opening covered none of `GetX`, `GetY`, `GetZ`, `SpawnParticle`,
  `ResetSegmentHealth`, `SetSegmentVulnerable` or `Die`, and fifty-four segment
  calls would have been unmissable. Do not size the session as if the boss starts
  by itself.
- **`&&` short-circuiting is unchecked.** If the MissionScript VM does not
  short-circuit, `GetGoodieState` fires on any boss kill and the 25-Gnat
  requirement is unnecessary. The plan assumes the conservative case.
- **`Pause()` under TTD is unmeasured** — see §6.
- **`HiveMovement.msl` may not be bound.** Nothing calls
  `SetScript("HiveMovement")`, so its `GetDistToObj` may never fire.
  `SetGoalPoint` is reached regardless via `hive.msl:171`.
