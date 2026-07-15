# Home Native Visual Focus Harness Design

Status: unattended maintainer-approved design
Date: 2026-07-14

## Goal

Turn the integrated Home newcomer hierarchy into a repeatable native WinUI
acceptance gate. The gate must launch only the repository-built Toolkit, bind
the exact process and top-level window, prove first-run arrival focus reaches
the visible setup action, validate normal and compact rendered layouts, and
publish complete ignored/local evidence without a human judging screenshots.

This slice verifies Toolkit behavior only. It does not launch Battle Engine
Aquila, touch an installed game, enable Host/Join, or authorize a release.

## Baseline Evidence And Root Cause

The integrated explicit smoke already owns receipt-bound FlaUI capture and
Home focus diagnostics. A fresh build at `15f17b3c` succeeded with zero
warnings. Two fresh native runs produced the same boundary result:

- the true first-run setup action received global UIA focus;
- the app emitted a `ContentFocused` / `FocusVerified=true` diagnostic for the
  setup action;
- its receipt-bound first-run image passed the existing header, marker, HWND,
  identity, and pixel-activity checks; and
- the later ready-state launch ended with global UIA and final XAML focus on
  `HomeOpenPatchBenchButton`, but the policy had already stopped with
  `UserFocusPreserved` after observing a transient non-target focus.

The failing assertion therefore confuses the mechanism that established focus
with the native end state being verified. The current diagnostic serializes
only the final XAML focus ID for every earlier sample, so it cannot name the
transient element that caused the policy stop. Changing focus policy from that
evidence would be speculative.

## Selected Approach

Keep Home focus behavior unchanged and harden the existing native smoke into a
named acceptance harness:

1. Record the XAML focused AutomationId and input epoch at each policy
   diagnostic sample, rather than stamping every line with the final focus.
2. Require first-run acceptance to have both global UIA focus on
   `HomeSetupActionButton` and a receipt-bound app diagnostic for the same run,
   PID, input epoch, and final XAML target.
3. Permit the ready state to prove its user-visible end state independently of
   whether the policy actively focused it or preserved an already-established
   focus. The evidence records the diagnostic outcome instead of relabeling it.
4. Capture first-run and ready Home at 1100x900 and 760x820. Every capture must
   retain exact process/start/executable/product-assembly/HWND identity, stable
   UIA marker bounds, Toolkit header pixels, marker-region activity, and no
   horizontal overflow at compact width.
5. Expose a test-only, window-scoped UIA endpoint containing the current XAML
   focus and input epoch. Cross-check it against the global focused UIA node,
   the expected element found below the exact launch HWND, and the full
   process/start/hash/HWND receipt immediately before and after every shutter.
6. Use a unique staging root below
   `local-lab/winui-home-native-visual-focus/`. Store isolated app data,
   diagnostics, synthetic ready-state fixture, captures, and one manifest in
   that staging root. Complete and flush the canonical manifest inside staging,
   then publish with one sibling directory rename only after every check passes;
   delete the partial root on failure.
7. Route the package command through a fail-closed runner. It rebuilds WinUI,
   requires an exact one-test/one-pass/no-skip TRX, one fresh accepted manifest,
   full artifact reconciliation, and a zero relevant-process census. Both build
   and test pin Debug/win-x64. A unique invocation token and runner-captured
   post-build executable/DLL hashes bind the child test plus the only accepted
   or partial directories that invocation may roll back. The command is
   separate from ordinary non-native WinUI tests and release gates.

## Evidence Contract

The schema-3 local manifest is complete only when it contains exactly four capture
receipts and two focus receipts. A capture receipt includes file hash, requested
bounds, PID/start time, executable path/hash, loaded product assembly path/hash,
main HWND, UIA HWND, HWND owner PID, visual marker bounds, and owner-bound focus
and input endpoints on both sides of the shutter. A focus receipt includes
state, expected and actually observed AutomationIds, run ID, full launch
identity, diagnostic stage/outcome, focus-verification flag, sampled and final
XAML focus, plus an unchanged endpoint input epoch.

Acceptance fails closed when:

- the executable is not the repository Debug `win-x64` build;
- process, module, hash, HWND, or owner identity changes;
- the expected action is missing, disabled, offscreen, clipped, or outside the
  captured HWND;
- global UIA and app-side XAML disagree about the accepted focus target;
- the input epoch changes;
- the layout never stabilizes, compact Home scrolls horizontally, capture
  pixels do not meet opaque frame/header/marker coverage, or a screenshot
  hashes differently after staging;
- the filtered native command executes zero, skips, or runs more than the one
  intended test; or
- any expected receipt/capture is missing, a stale manifest is reused, a
  partial directory remains, or the relevant-process census is nonzero.

Screenshots remain ignored local evidence. The tracked result is the harness,
its deterministic non-native regressions, the named command, and an honest
baton statement describing the exact native run.

## Rejected Approaches

### Screenshot hash goldens

Rejected because raster hashes change with benign Windows rendering details
and cannot prove the focused element or process identity. The harness hashes
each produced capture for staging integrity but validates semantics through
UIA bounds and bounded pixel signatures.

### Change Home focus policy to force the ready target

Rejected at this stage because the fresh failure already ended on the correct
visible target and the existing diagnostics do not identify the transient
focus that caused `UserFocusPreserved`. Per-sample instrumentation comes first;
product behavior changes require a separate failing behavioral contract.

### Add a second desktop automation stack

Rejected because FlaUI, app-side XAML diagnostics, and receipt-bound capture
already cover the required native boundaries. A new driver would duplicate
launch, identity, cleanup, and evidence code.

## Verification

The smallest proof set is:

- focused non-native Home policy/product-lane tests;
- receipt-bound visual-capture tests;
- the new named native Home visual-focus command;
- the primary WinUI lane before handoff;
- documentation command/link checks for command authority changes;
- hard-payload safety and `git diff --check`; and
- zero Toolkit/testhost/vstest/BEA/CDB/WinDbg census after native execution.

Native acceptance is claimed only for the exact repository build and states
exercised by the passing harness. It is not retail-game or release evidence.
