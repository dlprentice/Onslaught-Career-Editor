# Home Native Visual Focus Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Produce one unattended, receipt-bound native WinUI gate for Home first-run focus and normal/compact visual acceptance.

**Architecture:** Extend the existing explicit Home FlaUI smoke rather than adding another automation framework. App-side diagnostics expose per-sample and current endpoint focus/input observations; the smoke stages isolated state and four semantically validated HWND captures under ignored `local-lab`, materializes fully identity-linked focus/capture receipts, and publishes one complete schema-3 manifest with a single directory rename. A fail-closed Python runner rebuilds the app, invokes only this explicit native scenario, verifies exact TRX/artifact counts, and requires a zero relevant-process census.

**Tech Stack:** C# 13 / .NET 10, WinUI 3, NUnit 4, FlaUI UIA3, `System.Drawing`, JSON, npm command routing.

## Global Constraints

- Do not launch BEA, read live game memory, send game input, or touch an
  installed game/original `BEA.exe`.
- Launch only the repository Debug `win-x64` WinUI executable built by the
  focused command.
- Keep screenshots, isolated app data, diagnostics, and generated manifests
  ignored/local.
- Preserve user-focus behavior; this slice instruments and verifies it but does
  not force a new focus policy.
- Publish no partial evidence root and leave no owned Toolkit/test processes.
- Preserve the unrelated untracked `terminals/` directory.

---

### Task 1: Lock The Harness Contract In Non-Native Tests

**Files:**
- Modify: `OnslaughtCareerEditor.UiTests/HomeArrivalFocusPolicyTests.cs`
- Modify: `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`
- Add: `OnslaughtCareerEditor.UiTests/HomeFocusEvidenceAcceptanceTests.cs`
- Add: `OnslaughtCareerEditor.UiTests/HomeVisualEvidenceAcceptanceTests.cs`

- [x] Add source-contract assertions for per-sample focused AutomationId and
  input epoch, a unique `local-lab/winui-home-native-visual-focus` staging root,
  four captures, two focus receipts, repository-build enforcement, and the
  focused package command.
- [x] Run the focused tests and record RED because the harness does not yet
  expose those fields or command.

### Task 2: Add Per-Sample Native Diagnostics

**Files:**
- Modify: `OnslaughtCareerEditor.WinUI/MainWindow.xaml.cs`
- Modify: `OnslaughtCareerEditor.UiTests/HomeArrivalFocusPolicyTests.cs`

- [x] Wrap each `HomeArrivalFocusDiagnostic` at report time with the current
  XAML focused AutomationId and input epoch.
- [x] Serialize the sampled fields alongside the existing run/PID/generation
  and policy fields without changing policy decisions.
- [x] Run the focused policy tests GREEN.

### Task 3: Harden And Complete The Native Acceptance Artifact

**Files:**
- Modify: `OnslaughtCareerEditor.UiTests/WinUiHomeNavigationSmokeTests.cs`
- Modify: `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`
- Add: `OnslaughtCareerEditor.UiTests/HomeFocusEvidenceAcceptance.cs`
- Add: `OnslaughtCareerEditor.UiTests/HomeVisualEvidenceAcceptance.cs`

- [x] Stage a unique run under ignored `local-lab`; put per-state app data and
  the synthetic ready fixture inside the partial root.
- [x] Require the exact repository-built executable and retain the existing
  process/start/hash/module/HWND receipt checks.
- [x] Return structured focus receipts from global UIA plus current-run XAML
  diagnostics, require an unchanged input epoch, and preserve the actual policy
  outcome.
- [x] Capture first-run normal/compact and ready normal/compact states. Validate
  visibility, ordering, stable markers, rendered pixels, compact overflow, and
  focus after capture.
- [x] Publish exactly four capture receipts and two focus receipts only after
  all hashes and schema fields revalidate; remove partial output on failure.
- [x] Run focused non-native tests GREEN.

### Task 4: Add Command Authority And Run Native Acceptance

**Files:**
- Modify: `package.json`
- Modify: `CONTRIBUTING.md`
- Modify: `VALIDATION.md`
- Add: `tools/run_winui_home_native_visual_focus.py`
- Add: `tools/run_winui_home_native_visual_focus_test.py`

- [x] Add `test:winui-home-native-visual-focus`: rebuild WinUI, then run only
  the explicit native Home acceptance test.
- [x] Document this as an opt-in native evidence gate, separate from normal UI
  tests and release signoff.
- [x] Run the named command. If it fails, use its sampled diagnostic and partial
  cleanup evidence to fix only the proven harness or product defect, then rerun.
- [x] Inspect the accepted manifest and images programmatically; do not rely on
  human screenshot approval.

### Task 5: Review, Handoff, And Campaign Advance

**Files:**
- Modify: `goal.md`
- Modify: `goal.campaign.md`
- Modify only truthful current capability/state mirrors affected by the native
  result.

- [ ] Run focused visual-capture tests, the primary WinUI lane, docs/link checks,
  hard-payload safety, `git diff --check`, and a final relevant-process census.
- [ ] Complete one normal/adversarial Codex review and one normal/adversarial
  sanitized Cursor consult for this substantive objective; resolve material
  findings.
- [ ] Record the exact native acceptance scope and non-claims, advance to the
  next actionable campaign slice, commit, and push green. No release or tag.
