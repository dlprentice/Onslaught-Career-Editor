# PatchBench Primitive Projection Contract

Status: active design note
Last updated: 2026-06-29

This note defines the boundary required before extracting safe-copy receipt and
source-summary presentation helpers from `BinaryPatchesPage`. It is a design
contract only. It does not move AppCore receipt construction, file I/O, launch
planning, process control, patch catalog behavior, or online-readiness behavior.

## Goal

Future PatchBench presentation helpers may format already-safe display state.
They must not become a second owner of safe-copy behavior, source validation,
patch semantics, launch authority, or runtime proof claims.

The primitive projection rule is:

```text
BinaryPatchesPage projects facts -> AppCore owns receipt truth -> PatchBench
helpers format primitive display state.
```

## Allowed Helper Inputs

Presentation helpers may receive only display-safe primitives or tiny records
made from those primitives:

- `string` values that are already safe for display, such as a headline, label,
  bullet text, launch modifier summary, patch display list, or safe-copy folder
  leaf name.
- `bool` values that the page already computed, such as copied-savegame status,
  tracked-process status, source-ready status, or content-stale status.
- `int` or count values that are already safe to show, such as files copied.
- Small WinUI-local enums that describe display state only, such as source
  selection kind or catalog source kind.
- Lists of safe strings or safe label/value rows.

For a receipt helper, the projected state should be a WinUI-local primitive
record, not an AppCore DTO. A suitable shape is:

```csharp
internal sealed record PatchBenchSafeCopyReceiptTextState(
    string Headline,
    IReadOnlyList<PatchBenchReceiptLineTextState> Lines,
    IReadOnlyList<string> IncludedChanges,
    IReadOnlyList<string> StillNotIncluded);

internal sealed record PatchBenchReceiptLineTextState(string Label, string Value);
```

For a later source-summary helper, the projected state should use page-computed
values such as:

- source kind: not set, unsupported name, `BEA.exe`, or
  `BEA.exe.original.backup`
- source file exists: yes/no, computed by the page
- optional parent folder leaf name only
- working-copy readiness: yes/no, computed by the page
- catalog source kind, version label, and optional short hash prefix projected
  by the page

## BinaryPatchesPage Ownership

`BinaryPatchesPage` must keep:

- reading UI controls and assigning UI control text
- `File.Exists`, `Directory.Exists`, `Path.*`, source path parsing, source path
  persistence, browse/config loading, and folder leaf extraction
- `IsBattleEngineExecutableSourcePath`, `IsUsableWorkingCopy`, safe-copy content
  signatures, selected-key matching, and copied-profile freshness decisions
- calls to `GameProfilePreflightService.PrepareWindowedCompatibilityProfile`
  and `GameProfilePreflightService.BuildPrepareReceipt`
- mapping `GameProfilePrepareReceipt` into WinUI-local primitive projection
  records
- `BuildPatchDisplayList`, hidden patch display fallback, profile matching,
  and catalog static reads
- confirmation text, operation-log assignment, `AppStatusService` status
  updates, busy state, and enablement state
- launch option tuples, launch argument construction, launch-plan validation,
  launch preview, launch/stop process control, and managed-process state
- music staging/restoration state and service calls
- online-readiness service calls, artifact loading, and Host/Join gating

If the current receipt backstop that adds the Host/Join boundary when missing is
retained, it should stay explicit in the page projection layer or be proven
unnecessary by AppCore tests. It should not be hidden inside a generic text
formatter.

## AppCore Ownership

AppCore must keep:

- safe-copy correctness, source-root validation, destination validation, copy
  planning, patch verification, and manifest semantics
- `GameProfilePrepareReceipt` construction and receipt semantics
- included-change and still-not-included decisions
- path redaction inside receipt facts, such as safe-copy folder and manifest
  file-name display
- control-options matching, music-muted limit injection, installed-game
  mutation boundaries, Host/Join limits, and no-parity non-claims
- launch-plan construction and safe-copy runtime services

WinUI helpers may lay out the AppCore receipt after the page has projected it;
they must not recreate or reinterpret AppCore receipt truth.

## Forbidden Helper Ownership

PatchBench presentation helpers must never own or reference:

- raw source, target, executable, manifest, profile-root, proof-root, or local
  campaign paths
- raw manifests, raw local storage manifests, content signatures, proof IDs,
  proof artifact IDs, or private proof paths
- `GameProfilePrepareResult`, `GameProfileLaunchPlan`,
  `GameProfilePrepareOptions`, `GameProfileControlOptionsRequest`, or service
  result types that carry behavior or paths
- `GameProfilePreflightService.BuildPrepareReceipt` or any AppCore receipt
  construction
- `File.*`, `Directory.*`, `Path.*`, `Process`, `Task`, `async`, or `await`
- patch engine APIs, patch catalog validation, profile preset matching, hidden
  patch expansion, or `BinaryPatchPlanBuilder` static reads
- launch argument normalization, launch-plan parsing, copied-profile launch,
  copied-profile stop, or process registry behavior
- Host/Join enablement, online-ready wording, public matchmaking, runtime proof,
  gameplay proof, music playback proof, release packaging, or release claims

Helpers should not sanitize by denylist. Raw sensitive values should not cross
the helper boundary in the first place.

## Leak Prevention Rules

Projection into helper state must happen before formatting:

- Convert absolute paths to approved display forms before calling helpers.
  Normal allowed forms are leaf names, safe-copy folder names, file names, or
  explicitly safe relative paths within a copied safe game.
- Do not pass drive roots, user folders, app config roots, manifest paths,
  proof roots, raw JSON, raw command previews, source roots, target roots, or
  normalized source signatures.
- Do not pass proof IDs or profile proof-status fields into player-facing
  helpers. If diagnostics need a proof label, keep that in an explicit
  diagnostics surface.
- Do not let helpers decide readiness. They may only describe readiness that
  the page or AppCore already computed.
- Keep player copy and bench/diagnostic copy separate. Source/catalog strings
  that mention schema, SHA-256, byte verification, or proof classes belong in
  diagnostics unless a later UI decision explicitly keeps them visible.

## First Future Extraction

The first future helper should be a narrow receipt text formatter, not a source
summary helper and not a broad `PatchBenchSafeCopyOutcomeText` expansion.

Recommended order:

1. In `BinaryPatchesPage`, keep `GameProfilePreflightService.BuildPrepareReceipt`
   and map the returned receipt into a WinUI primitive receipt text state.
2. Move only the text layout currently represented by `BuildSafeCopyReceiptText`
   into a new receipt text helper.
3. Keep Host/Join boundary completeness explicit in AppCore or in the page
   projection layer.
4. Add focused tests before or with the extraction.

Source-summary extraction should wait until its own primitive state is defined.
It has more leakage risk because the current methods touch raw paths,
`File.Exists`, and catalog statics.

## Boundary Tests

Before implementation, add or extend tests that prove:

- PatchBench helpers remain behavior-free and contain no `File.`, `Directory.`,
  `Path.`, `Process`, AppCore services, patch engines, launch builders, online
  services, or release/package wording.
- The receipt formatter does not reference `GameProfilePrepareReceipt`,
  `GameProfilePrepareResult`, launch plans, manifest paths, patch catalogs, or
  raw paths.
- `BinaryPatchesPage` still calls `GameProfilePreflightService.BuildPrepareReceipt`
  and still owns the mapping from AppCore receipt DTO to primitive WinUI text
  state.
- Receipt text renders the headline, label/value rows, `Included changes`,
  `Still not included`, bullet formatting, and Host/Join boundary exactly once.
- AppCore receipt tests continue to reject full local paths, raw source roots,
  proof-promotion wording, and unsafe non-claim omissions.
- Source-summary helper tests, when that extraction happens, cover empty source,
  unsupported file name, ready `BEA.exe`, ready backup-named executable, missing
  file, working-copy ready/not-ready, and catalog source states without passing
  raw paths.
- Output guards reject drive roots, absolute path separators, manifest path
  fragments, local proof path language, raw proof IDs, and online-ready or
  Host/Join action wording in helper output.

## Explicit Non-Goals

This contract does not authorize:

- moving AppCore receipt construction into WinUI
- changing safe-copy creation, source validation, file copying, patching,
  manifests, byte verification, or profile catalog behavior
- changing launch arguments, launch plans, launch previews, process start/stop,
  or managed-process restoration
- enabling Host/Join, online play, matchmaking, online-ready copy, or online
  action controls
- claiming runtime proof, music audible-output proof, gameplay proof, visual
  parity, release readiness, rebuild parity, or no-noticeable-difference parity
- broad `BinaryPatchesPage` splitting, ViewModel migration, or release work
- adding hard payloads, local paths, raw manifests, copied executables, game
  files, screenshots, frame dumps, raw CDB logs, secrets, or build output
