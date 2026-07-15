# Single-Root Campaign Operating Foundation Implementation Plan

> **For agentic workers:** Execute this plan in the active root task. Subagents
> and consults are review advisers unless root explicitly assigns a bounded,
> non-overlapping write set.

**Goal:** Replace the legacy lease-first campaign foundation with a durable
single-root default, standing campaign authority, optional concurrency overlay,
and accurate blocker semantics without disturbing the in-progress M2.3 work.

**Architecture:** `goal.policy.md` owns the normal root operating and authority
model. `coordination/` becomes a conditional overlay for deliberately
concurrent writers or shared-resource waves. The canonical slash-goal document
stores the maintainer's unchanged long-horizon objective and delegates
authority detail to policy. A deterministic Python test treats these documents
as one contract and rejects drift back to mandatory root leases.

**Tech Stack:** Markdown policy and state, Python 3 standard-library `unittest`,
existing repository documentation and payload-safety gates.

## Global Constraints

- Preserve every unrelated and pre-existing M2.3 change in the dirty worktree.
- Do not edit or stage the unrelated `terminals/` directory.
- Do not launch BEA, attach a debugger, read or mutate runtime memory, open or
  mutate live Ghidra, publish a release, or perform an external action during
  this foundation-only slice.
- Keep the installed Steam game and original `BEA.exe` immutable.
- Keep the durable user goal text unchanged.
- Do not claim that clearing the authority blocker completes the shield live
  measurement or the reconstruction campaign.
- Do not add the focused policy test to `package.json`; that file already has
  unrelated in-progress M2.3 changes, and the policy test is a narrow handoff
  gate rather than a frequent contributor command.

---

### Task 1: Policy Consistency Harness

**Files:**
- Create: `tools/campaign_operating_foundation_test.py`

**Contract:** The active policy stack declares single-root default operation,
standing campaign authority, optional coordination, retained immutable/payload
boundaries, fresh spending/destructive authority, durable non-time-boxed goal
text, and no active shield lease blocker.

- [ ] **Step 1: Write failing contract tests**

  Add standard-library tests that read the active documents and require:

  - `goal.policy.md` to name the single-root default and standing/fresh
    authority boundaries;
  - copied-runtime observation and mutation, live Ghidra mutation,
    commit/push, release/publication, external action, and normal cleanup to be
    standing-authorized;
  - spending and genuinely destructive operations to require fresh authority;
  - installed Steam/original `BEA.exe` immutability and proprietary evidence
    containment;
  - `coordination/README.md` and its contracts to activate only for explicit
    concurrency rather than every campaign slice;
  - the canonical slash goal to contain the approved durable objective and no
    `STOP_LOCAL` time-box machinery; and
  - `goal.md` to retain M2.3 while no longer carrying an active missing-runtime-
    lease blocker.

- [ ] **Step 2: Run RED**

  ```powershell
  py -3 tools\campaign_operating_foundation_test.py
  ```

  Expected: FAIL against the legacy policy because it requires structured
  runtime batons and coordinated leases, the slash goal is time-boxed, and the
  shield authority blocker is active.

### Task 2: Root Policy And Durable Goal

**Files:**
- Modify: `goal.policy.md`
- Modify: `roadmap/goals/full-rebuild-campaign-slash-goal.md`

- [ ] **Step 1: Rewrite the normal operating model**

  Make root the default owner of implementation, integration, validation,
  state, version control, and acceptance. Make subagents/consults bounded and
  need-shaped. State that shared resources are serialized with identity and
  cleanup receipts, not approval-bearing leases.

- [ ] **Step 2: Encode the authority matrix**

  Record the approved standing authority and the two fresh-authorization
  classes. Retain immutable installed-game/original-executable, hard-payload,
  evidence, Host/Join, and force-push boundaries. Explain that release
  authority does not imply readiness or require a release.

- [ ] **Step 3: Canonicalize the unchanged durable goal**

  Replace the obsolete time-boxed marathon block with the exact maintainer-
  approved objective. Add only surrounding invocation and authority-routing
  notes; do not alter the objective itself.

### Task 3: Optional Coordination Overlay

**Files:**
- Modify: `coordination/README.md`
- Modify: `coordination/WORKSTREAM_CONTRACT.md`
- Modify: `coordination/RESOURCE_LEASES.md`
- Modify: `coordination/REPORT_CONTRACT.md`
- Modify: `coordination/AUTOMATION_STORAGE_GHIDRA_POSTURE.md`
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Scope coordination conditionally**

  State that root activates the overlay only for concurrent writers,
  independent acceptance lanes, recurring automation, or collision-prone
  shared-resource waves. Normal root work does not need a coordinator,
  isolated worktree, lease record, worker report, or separate integration
  owner.

- [ ] **Step 2: Convert leases into resource claims**

  Preserve one-owner-at-a-time collision safety, unknown-process protection,
  and cleanup verification. Clarify that root's local active-operation record
  is sufficient in single-root mode and no lease grants or withholds authority.

- [ ] **Step 3: Make reviews proportionate**

  Keep independent review available for risk, uncertainty, public claims,
  releases, destructive actions, or broad changes. Remove fixed role-count and
  mandatory external-consult ceremony from normal campaign slices. Reviews
  advise; root accepts.

- [ ] **Step 4: Preserve automation and Ghidra safety**

  Keep standing high-throughput automations stopped unless deliberately
  restarted. Replace coordinator-led wording with root-led operation and
  structured-baton permission gates with the standing/fresh authority model.
  Retain complete Ghidra backup, dry-run, read-back, rollback, and stop-on-first-
  mismatch rules.

### Task 4: Campaign And Baton Reconciliation

**Files:**
- Modify: `goal.campaign.md`
- Modify: `goal.md`

- [ ] **Step 1: Align campaign rules**

  Add the single-root default to operating rules. Change M2.2 from authority-
  blocked to live-pair ready/pending under standing authority without claiming
  an attempt or value.

- [ ] **Step 2: Resolve only the procedural blocker**

  Replace the active skipped shield blocker with a compact resolved record that
  says the old lease requirement was superseded. Add a foundation advancement
  ledger row, retain `M2.3-target-acquisition-static-contract` as Current Slice,
  and leave a resume note that the existing M2.3 worktree changes were
  preserved.

- [ ] **Step 3: Run GREEN**

  ```powershell
  py -3 tools\campaign_operating_foundation_test.py
  ```

  Expected: all policy consistency tests pass.

### Task 5: Verification, Review, And Publication

**Files:**
- Modify only files already listed and the implementation plan if review finds
  a plan defect.

- [ ] **Step 1: Run proportional gates**

  ```powershell
  py -3 -m py_compile tools\campaign_operating_foundation_test.py
  py -3 tools\campaign_operating_foundation_test.py
  & "$env:APPDATA\npm\npm.cmd" run test:doc-commands
  & "$env:APPDATA\npm\npm.cmd" run test:md-links:public-core
  & "$env:APPDATA\npm\npm.cmd" run test:hard-payload-safety
  & "$env:APPDATA\npm\npm.cmd" run test:repo-hygiene
  git diff --check
  ```

  Skip full `npm test`, WinUI, Godot, runtime-tooling, and BEA gates because the
  slice changes operating policy only.

- [ ] **Step 2: Review the exact foundation diff**

  Obtain bounded normal and adversarial review focused on hidden authority
  expansion, lingering mandatory-lease wording, target ambiguity, destructive
  cleanup, release readiness, payload safety, blocker semantics, and accidental
  disturbance of M2.3 work. Resolve material findings and rerun affected gates.

- [ ] **Step 3: Commit only owned paths**

  Stage the plan, policy test, policy/coordination/contributor/campaign/slash-
  goal docs, and `goal.md`. Do not stage any M2.3 path or `terminals/`. Confirm
  the exact cached diff before committing.

- [ ] **Step 4: Align the baton tip and push**

  If necessary, make one docs-only tip-alignment commit for `goal.md`, rerun the
  focused policy test and diff check, and push `main` without force. Confirm
  `main` and `origin/main` match while the unrelated M2.3 work remains present
  and unstaged.

- [ ] **Step 5: Stop after the foundation rewrite**

  Report the tip, exact validation, changed paths, resolved blocker, retained
  M2.3 Current Slice, immutable installed game/original executable, and no
  runtime/release/external action. Do not resume the reconstruction goal until
  the user does so.
