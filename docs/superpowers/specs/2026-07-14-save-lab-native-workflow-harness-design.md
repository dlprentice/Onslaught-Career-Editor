# Save Lab Native Workflow Harness Design

Status: unattended maintainer-approved design
Date: 2026-07-14

## Goal

Turn the existing Save Editor first-use journey and Game Options editor into one
repeatable native WinUI acceptance gate. The gate must launch only the exact
repository build, use deterministic public-safe inputs, exercise both workflows
through UI Automation, validate their important normal and compact states from
receipt-bound pixels, and publish complete ignored/local evidence without a
human judging screenshots.

This is Toolkit workflow evidence only. It does not launch Battle Engine
Aquila, inspect or mutate an installed game, synthesize a new career-save
baseline, open Explorer or a browser, enable Host/Join, or authorize a release.

## Existing Foundation And RID Root-Cause Finding

The current explicit Save Editor smoke already copies the tracked immutable
`tests_shared/fixtures/gold_career_save.bin`, starts with no selected changes,
writes a separate app-owned output, preserves its input, and uses receipt-bound
normal/760 captures. The current Game Options tests separately cover controller
guidance and a private copied-options write. Neither path has the Home gate's
exact-build runner, invocation-bound manifest, exact one-test TRX, atomic
publication, or final process census. Game Options also cannot run unattended
without a private options input.

A fresh Debug/win-x64 focused baseline passed 32 tests and failed seven
source-inspection tests consistently. Their computed source paths contained the
test project twice because `TestFixturePaths.RepoRoot` and one local duplicate
climb a fixed four parents. RID output inserts a `win-x64` directory, while the
working Home harness discovers the first ancestor containing `package.json`
plus both WinUI projects. The exact RID-pinned Save gate therefore requires the
same marker-based repository-root contract; loosening the build/test command
would hide the defect.

## Selected Architecture

Use a separate Save Lab gate and preserve Home as an independently attributable
surface. Reuse the existing receipt-bound app identity/capture adapter, extract
only generic native-runner and Toolkit-pixel helpers that both gates can own,
and keep Save Lab's workflow schema and validation surface-specific.

The gate runs one explicit native test containing two isolated app launches:

1. **Save Editor first use.** Copy the tracked gold fixture into the unique
   staging root, verify SHA-256
   `0C17E47DB9D666E9B26EF88D43D0A25E7CBFBF4F88C8005CC748965050E506FB`,
   and launch directly on Save Editor
   with isolated app data and empty game-discovery candidates. Set the copied
   input through UIA, require the app-owned suggested output, empty preset,
   disabled write action, collapsed-but-reachable advanced controls, and the
   first-use status. Capture that ready state at 1100x900 and 760x820. Select
   only Goodies, invoke the write through UIA, verify a distinct valid output,
   unchanged input bytes, current-plan completion, and enabled reveal action
   without invoking Explorer. Capture the completion state at both sizes.
2. **Game Options.** Materialize a deterministic 10,004-byte `.bea` buffer in
   staging with only little-endian version word `0x4BD1` initialized. Its
   SHA-256 must be
   `A922C6BCA412DB45AED3FCCBE926B6383C039CCF3778C4558D299D1D3C466D99`.
   Launch directly on Game Options with separate isolated app data and empty
   discovery candidates. Capture the modern-controller guidance at both sizes without
   invoking its browser action. Load the synthetic input through UIA, require
   an app-owned distinct output and disabled write action until an override is
   selected, set controller config P1 to `1`, and invoke the write. Verify the
   input hash is unchanged, the output is valid and distinct, the reloaded
   snapshot reports P1 `1`, and the UI reports success without exposing local
   paths. Capture the completion region at both sizes.

The eight exact capture names are:

- `save-ready-normal.png` and `save-ready-760.png`;
- `save-complete-normal.png` and `save-complete-760.png`;
- `options-guidance-normal.png` and `options-guidance-760.png`; and
- `options-complete-normal.png` and `options-complete-760.png`.

Normal means an exact 1100x900 HWND and compact means an exact 760x820 HWND.
Each phase uses stable named UIA markers. Compact capture must realize the
named region through the exact Save Editor or Game Options scroll host, keep
all required markers inside the HWND, and reject horizontal overflow.

## Identity, Interaction, And Visual Contract

Before either launch, the child test hashes the exact adjacent repository
Debug/win-x64 executable and product DLL and compares them with runner-provided
post-build hashes. Each launch receipt then binds PID, UTC start time, live
image path/hash, loaded product DLL path/hash, main HWND, UIA HWND, and HWND
owner PID. Every capture revalidates the full receipt before and after the
shutter.

The harness uses UIA Value, Toggle, ExpandCollapse, Scroll, ScrollItem,
Selection, Focus, and Invoke patterns only. It does not synthesize keyboard or
pointer input. Before each shutter it focuses a phase-specific element, samples
the global UIA focused node under the exact launch HWND, and records the focused
AutomationId, owner PID, HWND, and bounds on both sides of the capture. This
proves deterministic Toolkit focus ownership for capture; it is not an
arrival-focus policy claim.

Toolkit images must be fully opaque at sampled points, have meaningful
luminance/color coverage, contain the rendered blue Toolkit header, reject the
known Codex Desktop signature, and show activity within every required marker
rectangle. Raster hashes protect staged artifact integrity; they are not
cross-machine visual goldens. If the native gate proves compact clipping or
horizontal overflow, the slice may make only the smallest responsive SavesPage
layout correction, guarded by a failing static/native regression and rerun of
both Save Lab and Home native gates.

## Evidence And Publication Contract

One runner invocation creates one sibling partial directory under
`local-lab/winui-save-lab-native-workflow/`. Fixture copies, isolated app data,
outputs, captures, and a schema-1 manifest remain below that directory. The
manifest contains:

- the 32-character invocation ID and fixed UIA-only interaction mode;
- exactly eight capture receipts with workflow, phase, dimensions, SHA-256,
  marker bounds, full launch identity, and owner-bound focus observations;
- exactly two workflow receipts with relative input/output paths and hashes,
  input-preservation result, output validation/readback, and full launch
  identity; acceptance independently reparses the retained output bytes to
  require all 233 displayable Goodies in OLD state and controller config P1
  equal to `1`; and
- the tracked fixture hash plus the deterministic synthetic-options recipe.

All artifact paths in the manifest are relative, normalized, and confined to
the staging root. The child writes and flushes the canonical manifest inside
staging, reopens and validates it, and then publishes with one same-volume
sibling directory rename. On child failure it leaves the caller-owned partial
directory intact. The outer runner may remove only accepted or partial evidence
bearing its exact invocation ID, and only when later TRX, manifest, artifact,
or cleanup validation fails.

The outer runner:

1. requires a zero Toolkit/testhost/vstest/BEA/debugger census and no stale
   partial Save Lab directory;
2. builds the repository WinUI project as Debug/win-x64;
3. records executable and product-DLL hashes and passes them plus a unique
   invocation token to the one filtered native test;
4. requires an exact one-total, one-executed, one-passed, zero-skipped/failed
   TRX for that method;
5. independently reconciles the schema, identities, artifact paths/hashes,
   PNG dimensions, fixture hash, synthetic recipe, workflow mappings, and
   exact capture set; and
6. shuts down build servers, removes its runner scratch root, and requires
   zero relevant processes even when the test or cleanup fails. If an exact
   WinUI launch from the validated manifest survives, it revalidates
   PID/start/path, performs bounded forced cleanup, recenses, and still fails
   the gate because remediation was required.

Both ignored roots must be their exact repository `local-lab` children; any
reparse-point root or owned child fails before writes or recursive cleanup.
Each exact WinUI launch revalidates PID/start/path before bounded graceful close
and again before process-tree kill, propagating failure if exit is not observed.
An unreceipted survivor is reported but never mutated.

## Shared Harness Boundary

Extract small generic helpers from the accepted Home runner for exact
TRX parsing, hashing, PNG dimensions, process census, owned process-tree
termination, build-server shutdown, and cleanup-error accumulation. Home keeps
its own manifest validator and owned-path rules; Save Lab receives its own.
Existing Home unit and named native gates must remain green after extraction.

Name the generic C# Toolkit pixel checks independently of Home while Home
retains a compatibility wrapper. Workflow actions, marker
sets, artifact semantics, and manifest acceptance remain Save Lab-specific.

## Rejected Approaches

### Add more captures to the broad visual smoke

Rejected because that smoke accepts optional/skipped execution, uses dated
output directories, does not reconcile a manifest, and cannot bind a complete
workflow result to the captured exact build.

### Fold Save Lab into the Home native gate

Rejected because Home arrival-focus and Save/options mutation workflows have
different inputs, assertions, evidence schemas, and failure owners. One large
gate would make regressions harder to attribute and would require rerunning
unrelated UI behavior.

### Require a private `defaultoptions.bea`

Rejected because it prevents unattended fresh-clone verification and risks
confusing Toolkit behavior with retail-input evidence. The deterministic
synthetic buffer exercises only the already-tested AppCore parser/editor
contract and carries no retail-behavior claim.

### Pixel-perfect screenshot goldens

Rejected because Windows raster details can vary without changing the product
contract. Semantic UIA markers, exact bounds, focus ownership, meaningful
rendered activity, and per-run integrity hashes provide the bounded evidence.

## Verification

The smallest complete proof set is:

- RID-pinned repository-root regressions;
- shared runner and visual-helper unit tests;
- focused Save journey, receipt, artifact, and manifest acceptance tests;
- the existing Home runner unit tests and named Home native gate after shared
  extraction;
- the new named Save Lab native workflow gate;
- the primary WinUI lane before handoff;
- command inventory, docs/mirror/link checks, generated-output and hard-payload
  safety, repo hygiene, and `git diff --check`; and
- a final zero relevant-process census.

Acceptance is limited to the exact repository build, deterministic inputs,
workflow phases, and window sizes exercised by the harness. It is not proof of
retail options semantics, every save mutation, general accessibility, release
fitness, or visual parity.
