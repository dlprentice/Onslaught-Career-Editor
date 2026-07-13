# RE Behavior Contract Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a prioritized public-safe RE behavior-contract roadmap and one camera-relative movement/morph candidate while surgically preventing two reviewed stale Ghidra ownership pairs from being re-applied.

**Architecture:** A versioned JSON contract is the machine-readable source for the candidate and its six evidence compartments. One Python checker validates that contract against the authoritative reviewed correction plan and scans only the two active mixed Java mutators for forbidden address/name/comment pairs while proving unrelated operations remain. A Markdown roadmap explains priority, evidence gaps, observation order, stale-tool closure, and rebuild/nonclaim boundaries.

**Tech Stack:** Markdown, JSON, Python 3 standard library, Ghidra Java source inspected as text, repository npm documentation/safety gates.

## Global Constraints

- Do not edit `package.json`, canonical goal/state, front-door docs, rebuild implementation, WinUI/AppCore, runtime helpers, or proprietary/local payloads.
- Do not run live Ghidra, BEA, CDB, Godot, WinUI, or other native actions.
- Retire only exact stale records for `0x00411630` / `CMonitor__IntegrateMovementAgainstTerrain` and `0x00411aa0` / `CMonitor__ComputeTerrainVelocityScalar`.
- Preserve unrelated operations in both mixed Java helpers and preserve historical read-only evidence.
- Keep Retry 13 unauthorized and off the critical path.

---

### Task 1: Forbidden-Pair Regression And Surgical Mutator Closure

**Files:**
- Create: `tools/re_behavior_contract_guard.py`
- Create: `tools/re_behavior_contract_guard_test.py`
- Modify: `tools/ApplyMovementJetPartSignatureCorrection.java`
- Modify: `tools/ApplyCMonitorMovementAudioAnimationRenderCurrentRiskWave1187.java`

**Interfaces:**
- Consumes: `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json` records.
- Produces: `build_report() -> dict`, CLI `py -3 tools/re_behavior_contract_guard.py --check`, and an exact forbidden-pair regression.

- [ ] **Step 1: Write the failing unit test**

  Add tests that require both authoritative rows to be `confirmed-apply`, require their `currentName` and `correctedName` to match the exact forbidden/accepted names, reject either forbidden name or stale `CMonitor__UpdateMovementTransitionAndEffects` comment token when paired with its address in either active mutator, and require unrelated sentinels to remain: `0x00411a60` plus `0x00412050` in the movement helper and `0x00409950` plus `0x0044e2c0` in the Wave1187 helper.

- [ ] **Step 2: Run the test to verify RED**

  Run: `py -3 -m unittest tools.re_behavior_contract_guard_test -v`

  Expected: FAIL because both mixed Java helpers currently contain the exact forbidden address/name/comment pairs.

- [ ] **Step 3: Implement the checker and remove only the stale Java records**

  Implement standard-library JSON/text validation. Remove the two `applySignature(...)` calls from `ApplyMovementJetPartSignatureCorrection.java` and the two matching `new Target(...)` entries from `ApplyCMonitorMovementAudioAnimationRenderCurrentRiskWave1187.java`; leave all other rows byte-for-byte except unavoidable surrounding whitespace.

- [ ] **Step 4: Run the focused test and checker to verify GREEN**

  Run:

  ```powershell
  py -3 -m unittest tools.re_behavior_contract_guard_test -v
  py -3 tools/re_behavior_contract_guard.py --check
  ```

  Expected: all unit tests pass and checker reports both forbidden pairs absent with all unrelated sentinels present.

### Task 2: Versioned Candidate Contract And Roadmap

**Files:**
- Create: `reverse-engineering/binary-analysis/first-flight-camera-movement-morph-contract-candidate.v1.json`
- Create: `roadmap/re-behavior-contract-roadmap-2026-07-13.md`
- Modify: `tools/re_behavior_contract_guard.py`
- Modify: `tools/re_behavior_contract_guard_test.py`

**Interfaces:**
- Consumes: reviewed correction plan, movement static crosswalk, morph observer design, controller candidate map, mission command-effect contracts, and rebuild provenance.
- Produces: schema `first-flight-camera-movement-morph-contract-candidate.v1`, status `candidate-static-runtime-required`, and a roadmap pointing to the checker command.

- [ ] **Step 1: Extend tests for the missing contract**

  Require top-level provenance and nonclaim fields plus four ordered observation rows: `camera_reference_frame`, `walker_directional_response`, `jet_directional_response`, and `morph_request_result_correlation`. Each row must contain nonempty `sourceHypothesis`, `steamStaticCorroboration`, `copiedRuntimeMeasurement`, `tolerances`, `rebuildRequirement`, and `nonclaims`; runtime measurement must remain `required-not-measured`, tolerances `not-established`, and no row may authorize a rebuild behavior change.

- [ ] **Step 2: Run the test to verify RED**

  Run: `py -3 -m unittest tools.re_behavior_contract_guard_test -v`

  Expected: FAIL because the versioned candidate does not exist.

- [ ] **Step 3: Add the minimum contract and roadmap**

  The JSON records only accepted static topology and the next observation/acceptance schema. The roadmap ranks P0 camera/movement/morph, P1 controls/weapons, P2 mission-facing systems, and P3 presentation; names exact evidence gaps; defines simpler observations before any new complex canary; documents surgical tooling closure; and states Retry 13 is unauthorized.

- [ ] **Step 4: Run focused validation**

  Run:

  ```powershell
  py -3 -m unittest tools.re_behavior_contract_guard_test -v
  py -3 tools/re_behavior_contract_guard.py --check
  Get-Content reverse-engineering/binary-analysis/first-flight-camera-movement-morph-contract-candidate.v1.json -Raw | ConvertFrom-Json | Out-Null
  ```

  Expected: tests/checker pass and PowerShell parses the JSON without error.

### Task 3: Proportional Validation, Review, Commit, Push, And Handoff

**Files:**
- Modify only files already listed in Tasks 1–2 plus this plan if execution tracking is updated.

**Interfaces:**
- Consumes: completed diff and repository validation commands.
- Produces: reviewed green commit, pushed branch, and integration handoff with recommended canonical-state deltas.

- [ ] **Step 1: Run repository gates**

  Run serially:

  ```powershell
  git diff --check
  npm run test:doc-commands
  npm run test:md-links:public-core
  npm run test:hard-payload-safety
  ```

  Expected: each exits zero. Do not substitute `npm test` or a native/full-suite gate for this focused non-native validation set.

- [ ] **Step 2: Run one review envelope**

  Obtain normal/adversarial Codex review and sanitized normal/adversarial Cursor/Grok consults. Resolve every Critical/Important finding; record unavailable lanes exactly if tooling cannot run.

- [ ] **Step 3: Re-run affected focused and repository gates**

  Re-run the checker test, direct checker, `git diff --check`, and every gate affected by review changes. Inspect `git status --short` and the full staged diff before commit.

- [ ] **Step 4: Commit and push the bounded slice**

  Stage only the listed files, commit with `docs(re): add behavior contract roadmap`, push `codex/re-behavior-contracts`, and verify remote divergence is `0 0`.

- [ ] **Step 5: Send the integration handoff**

  Report changed paths, commit/branch, exact validations, review evidence, explicit nonclaims, payload/native-process confirmation, recommended canonical state updates, and the `ADVANCEMENT` classification to the primary coordinator. Do not edit canonical state directly.
