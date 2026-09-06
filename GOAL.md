# The goal

Status: standing maintainer objective; not complete; feature execution on hold
Last updated: 2026-09-05
Summary: the three outcomes, acceptance criteria, evidence rules, and full retail RE mandate.

This is the maintainer's statement of what is wanted. Measurements can correct
implementation claims; they cannot narrow or mark this objective complete.
Execution history remains in Git and the existing evidence owners.

## The objectives

1. Fully reverse Battle Engine Aquila's retail release: functions, contracts,
   data, systems, patch points, and dormant capabilities, so it can be understood,
   preserved, patched, and modded with evidence.
2. Rebuild it in Godot at 1:1 behavioral and experiential parity, beginning with
   the complete released startup → splash/intro → menus → loading → Level 100
   tutorial and completion path.
3. Ship a polished WinUI 3 preservation toolkit for careers, saves, safe copies,
   patching, media, and other proven capabilities, with no known data-loss path.

These outcomes are coequal. RE supplies behavior to the rebuild and toolkit;
their missing capabilities expose the next retail questions. A task's focus
does not demote either of the other outcomes.

### The rebuild property, and the test that stands in for it

A human starting a cold first career must get the released experience. The
acceptance proxy is an agent driving Level 100 to `Won` using only player input,
without posting mission events. An autopilot exploiting behavior a player cannot
reproduce does not pass. Pixel similarity and a winning run alone do not prove
the full experience, including sound, timing, controls, and a responsive world.

## The evidence partition

- Use the pinned, partial GPL source for the systems it contains, including
  player-vehicle physics/flight, frontend flow, career, camera, and sound.
  Cite file and line; override it only for measured retail divergence or an
  explicitly documented architectural difference.
- Read authored content directly from shipped data: mission scripts, world and
  vehicle definitions, physics, textures, video, and language tables.
- Recover missing behavior from retail bytes and controlled observations:
  HUD/cockpit, battleline, messages, unit AI, weapons, script VM, and math conventions.

Every behavior claim needs a capture, byte comparison, focused test, or pinned
source reference. Decompiler output, a name, one observed call, or a model report
alone is insufficient. Admit RE claims only after specimen-bound, two-witness validation
and local reproduction of their load-bearing conclusions; validate actual receipts and
controls, not metadata labels. Keep structural discovery, static semantics, runtime
contracts, and rebuild parity separate; no single completion percentage spans them.
Reconstruction defaults must be retail defaults, not capture-rig or user settings.

## Current directive

The full retail RE mandate remains: account for every admitted function, newly
discovered boundary, and mapped or unmapped `.text` range, including unexecuted
residuals. Each needs an evidence-graded terminal classification or an explicit
open question, cheapest falsifier, and next instrument. Recover boundaries,
ownership, signatures, globals, fields, algorithms, constants, units, ordering,
and failure behavior; progress relevant contracts toward `REBUILD_READY`.
Keep every nonterminal entity reachable and map retail entities to rebuild owners,
implementations, and parity tests. Never count `UNSCORED` evidence as success.

The storage-consolidation hold remains in force: no new RE campaign, rebuild
feature, WinUI/CLI feature, or semantic Ghidra mutation until David resumes that
work. Authorized routing repair, read-only audit, checksum validation, and repository
organization may proceed. Completing storage work does not silently lift the hold.
See [the program](PROGRAM.md) for the durable backlog and acceptance gates.

When resumed, select → preregister → measure → refute → advance. Prioritize
blocked contracts, call chains, patch/mod value, and playable slices. Mine surviving
evidence first; raw TTD recordings have been retired, so historical capture claims
do not imply replay availability. Use the smallest controlled safe-copy experiment
for an unanswered question, with positive, negative, adverse, and replication
controls. Reuse existing instruments; build a new one only for a demonstrated gap.
Prefer one instrument that measures a class of questions over repeated manual fitting;
build it first when existing tools cannot provide that measurement.
After two attempts at the same noise floor, change instrument or rotate frontier.
Preserve candidate supersession and rejected claims without repeatedly redoing closed work.

## Authority and safeguards

`developer_state.json` → `current_re_authority` is the sole live campaign selector:
generation, parent, READY/reducer pins, grades, verification command, and next-valid
generation belong there. Use its literal verify command for campaign verification.
Historical generations, projection oracles, and the DeepSeek verdict index are not
alternative authorities. [Ghidra's owner](reverse-engineering/ghidra/README.md)
plus fresh inspection governs database identity and structural state.

- Never write the pristine measurement specimen. Bind byte findings to its hash.
- Installed-game writes require the owner's informed choice and a verified backup
  before writing. Never label an already modified file as the original.
- Never destroy saves as a side effect. Use real save baselines and preserve length,
  reserved fields, and unknown bytes; do not synthesize `.bes` saves.
- Keep `OnslaughtRebuild.Core` deterministic and independent of presentation,
  filesystem, clock, process, network, and GPU APIs.
- Ghidra promotion requires the owning procedure: exact identity, recoverable
  off-volume backup, isolated rehearsal, independent refutation, dry run, apply,
  separate readback, non-target comparison, POST backup, and byte-verified checkpoint
  refresh. The hold still applies; access alone does not authorize mutation.
- Preserve unique evidence and unrelated changes. Follow [AGENTS.md](AGENTS.md)
  for current storage, publication, and scoped cleanup rules; retired Windows
  quarantine scripts and deleted Recovery paths are not operational routes.

## Where the goal currently stands

Not met. [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) owns measured behavior;
`developer_state.json` owns resumable state; [VALIDATION.md](VALIDATION.md) owns
validation routes and known limitations. A milestone, pilot, structural closure,
or successful promotion does not complete the mandate while an actionable function,
residual, contract, rebuild mapping, or discovery-instrument frontier remains open.
