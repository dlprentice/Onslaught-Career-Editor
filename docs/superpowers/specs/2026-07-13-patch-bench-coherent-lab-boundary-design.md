# Patch Bench Coherent Lab Boundary Design

**Status:** Approved by the primary coordination task on 2026-07-13

## Goal

Finish the Normal-versus-Lab information boundary on Patch Bench so a first-time
player can create, inspect, launch, and stop an ordinary safe game copy without
sorting through researcher controls, while preservationists and modders retain
the existing specialist tools and stable automation contracts.

## Chosen Structure

Use one dedicated, full-width `PatchBenchLabExpander` after the normal safe-copy
surface. It is collapsed by default and contains purpose-grouped subexpanders;
it is not the existing flat page moved one click deeper.

The normal surface keeps only:

- the required Compatibility base and the optional PATCHED marker and Goodies
  wall preview;
- source selection, optional save-copy choice, readiness, and both Create
  actions;
- copied-profile summary and receipt;
- Play copied game, Stop copied game, and their player-readable status;
- the ordinary local split-screen preset/action and the truthful statement that
  online play is unavailable.

The normal surface does not expose raw launch arguments, copied-options control
experiments, online proof/artifact tools, music replacement tools, or
BEA.exe-only diagnostics.

## Lab Groups

The outer Lab retains the existing purpose and safety copy, profile catalog
status, and preset details. Its subexpanders are collapsed by default and group
existing controls by job:

1. **Patch recipes and executable experiments** — retained legacy recipes,
   visual experiments, dynamic patch rows, row details, and the existing reset
   and clear actions. Existing recipe IDs and patch-key semantics remain intact.
2. **Launch and control diagnostics** — raw launch flags, optional level,
   controller configuration A/B choices, mouse sensitivity choices, control
   diagnostics, texture-RAM input, and the exact launch-plan preview. The normal
   local split-screen action remains outside Lab; its underlying exact flags and
   level controls remain inspectable here.
3. **Online research** — technical readiness details and existing artifact
   loaders. This group remains explicitly research-only and does not imply
   online readiness.
4. **Music experiments** — the create-time copied-track preset plus the existing
   post-create stage/restore workflow. Copy distinguishes creation input from
   later operations.
5. **BEA.exe-only diagnostics** — the existing app-owned executable-copy
   workflow, unchanged and explicitly separate from Safe Game Copy.

All existing controls preserve their `x:Name`, automation ID, accessible name,
event handler, selection values, and state behavior. New group containers and
the new Lab status receive stable automation IDs.

## Hidden-State Guard

Collapsing Lab does not clear active choices. An always-visible
`PatchBenchLabSelectionStatus` near normal Create prevents a hidden specialist
choice from silently affecting the next copy.

The status and the Create confirmation summarize only active settings that can
affect the **next copied profile**:

- selected optional or experimental executable patch rows beyond the required
  Compatibility base;
- active launch modifiers, including raw flags, level, controller
  configuration, and texture-RAM input;
- copied-options control changes such as the mouse-look sensitivity choice;
- the selected create-time copied-track music preset.

The empty state says that no Lab creation settings are active. Non-empty states
use short category labels and counts rather than raw offsets or proof IDs. The
status is a polite live region so preset, reset, clear, checkbox, combo-box, and
text-input changes remain perceivable.

These operations are never counted as creation inputs:

- online proof/artifact viewing or loading;
- post-create music staging or restore;
- BEA.exe-only inspect, apply, restore, or related diagnostics.

They remain separately labeled and report through their existing dedicated
statuses. The copied-profile receipt remains the authoritative post-create
record.

## State And Confirmation

One pure formatter/model builds the creation-input summary from current patch,
launch, copied-options, and create-time music state. `UpdateControlState` uses
it for `PatchBenchLabSelectionStatus`. Every selection path already routed
through control-state refresh must continue to do so; text inputs that do not
must be wired to refresh without changing their meaning.

Both Create buttons retain the existing readiness gate. Immediately before the
existing safe-copy confirmation is shown, the page re-reads current controls
and includes the same creation-input summary. The confirmation still states
source, destination, disk scope, and installed-game boundary. Cancellation
performs no copy or game action.

Reset-to-Compatibility, Clear optional mods, profile presets, dynamic patch-row
changes, launch presets, and page initialization must all yield a truthful
status. Required `resolution_gate` and `force_windowed` rows remain checked,
disabled, and excluded from the Lab-active count because they are the ordinary
base.

## Test And Native Acceptance

TDD covers:

- XAML ancestry proving representative specialist controls are descendants of
  `PatchBenchLabExpander` while representative normal controls are not;
- the pure creation-input formatter for empty, singular, plural, and mixed
  categories, including exclusion of required base rows and non-creation
  operations;
- reset, clear, preset, and input-update paths refreshing the status;
- both Create pre-confirmation paths using a freshly computed summary;
- unchanged safe-copy readiness, patch planning, preflight, and copied-target
  safety behavior.

After a fresh build and an exclusive desktop lease, hands-off native UIA must
prove: Lab starts collapsed; normal Create/readiness/receipt/play/stop/local
split-screen controls remain reachable; specialist controls are not reachable
until Lab and their group expanders are opened; representative stable IDs are
then reachable; one non-mutating Lab creation selection survives collapse and
appears in the visible status; no Create, Play, stage, restore, patch, copy, or
game action occurs. Native screenshots at normal and 760px widths must show a
clear normal journey and intentional disabled/collapsed states. Pre/post process
census must be zero for Toolkit test hosts, BEA, and CDB.

## Boundaries And Nonclaims

This slice changes WinUI information architecture, creation-input disclosure,
and tests only. It does not change AppCore patch injection, catalog recipe IDs,
patch bytes, receipts, safe-copy mutation semantics, launch semantics, music
mutation semantics, online readiness, Asset Library/exporter/bootstrap,
runtime/Ghidra evidence, installed game files, the original `BEA.exe`, canonical
goal/state, release assets, or integration-owned observer docsync drift.

It does not claim better gameplay, widescreen parity, controller feel, online
play, exhaustive Goodies behavior, or safety of experimental recipes beyond
their existing evidence.
