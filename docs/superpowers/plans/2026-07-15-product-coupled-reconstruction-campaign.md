# Product-Coupled Reconstruction Campaign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the research-led campaign authority with the approved
three-outcome, consumer-bound product strategy while preserving the paused M2.3
worktree and all safety boundaries.

**Architecture:** The canonical slash goal states the unattended long-horizon
objective. `goal.policy.md` owns durable operating semantics, `goal.campaign.md`
owns the product portfolio and milestone picker, and `goal.md` remains the
paused mutable baton. Public front doors explain the WinUI/reconstruction/retail
relationship, while one focused Python test prevents those authorities from
drifting back toward research-as-outcome.

**Tech Stack:** Markdown, JSON, Python 3 `unittest`, Git.

## Global Constraints

- Keep the reconstruction campaign paused; do not execute M2.3 or P1/P2 tests.
- Preserve all existing M2.3 tracked and untracked changes byte-for-byte unless
  a strategy-owned file must overlap.
- Do not edit or stage the already-dirty `package.json` or `VALIDATION.md`.
- Keep the installed game and original `BEA.exe` immutable.
- Do not launch BEA, mutate Ghidra, extract assets, modify WinUI/rebuild code,
  publish a release, or enable Host/Join.
- Use `apply_patch` for source edits and stage only the exact strategy paths.
- Proprietary payloads, runtime evidence, screenshots, and local asset output
  remain ignored/local.

---

### Task 1: Add the product-strategy regression guard

**Files:**
- Create: `tools/product_coupled_campaign_strategy_test.py`
- Reference: `docs/superpowers/specs/2026-07-15-product-coupled-reconstruction-campaign-design.md`

**Interfaces:**
- Consumes: canonical goal/policy/campaign/baton and public front-door text.
- Produces: `python -m unittest`-style direct gate with no generated output.

- [ ] **Step 1: Write the failing test against the legacy authorities**

The test must define the exact approved durable goal and assert:

```python
class ProductCoupledCampaignStrategyTests(unittest.TestCase):
    def test_canonical_goal_matches_approved_product_coupled_text(self): ...
    def test_policy_owns_three_shipping_outcomes_and_consumer_debt(self): ...
    def test_campaign_prioritizes_consumers_not_research_counts(self): ...
    def test_paused_baton_preserves_m23_and_names_its_consumer(self): ...
    def test_public_front_doors_connect_winui_rebuild_and_retail(self): ...
    def test_state_batons_use_current_pins_and_product_focus(self): ...
    def test_strategy_does_not_relabel_current_rebuild_strict_clean_room(self): ...
```

It must reject the stale Onslaught/AYA pins `792545b996365f383781c666d145ea6cbda83f3a`
and `6f3df296201ecc62bc09c39f7a93d8a4fb2f1638`, research/proof counts as a
primary outcome, a second consecutive consumerless research slice, a landed
contract-only product milestone, loss of WinUI community releases, and loss of
the original-game multiplayer epic.

- [ ] **Step 2: Run the test to verify RED**

Run:

```powershell
py -3 tools\product_coupled_campaign_strategy_test.py
```

Expected: failures because the canonical slash goal and active campaign files
still use the pre-product-coupling strategy.

- [ ] **Step 3: Keep the gate deterministic and source-only**

The test may read tracked text/JSON only. It must not write output, invoke Git
network operations, inspect runtime payloads, or launch any application.

### Task 2: Install the canonical goal and durable policy

**Files:**
- Modify: `roadmap/goals/full-rebuild-campaign-slash-goal.md`
- Modify: `goal.policy.md`

**Interfaces:**
- Consumes: approved design and exact durable goal text.
- Produces: canonical unattended objective and stable operating contract.

- [ ] **Step 1: Replace the slash goal with the approved exact text**

Use the block under `## Durable Goal Text` in the design without semantic
shortening. Preserve the immutable installed-game boundary, local payload
boundary, Host/Join evidence gate, spending/destructive authority boundary,
unattended behavior, and campaign continuation semantics.

- [ ] **Step 2: Rewrite policy around the three outcomes**

Policy must define:

```text
WinUI Community
Playable Reconstruction
Retail Enhancement
```

It must state that RE/source/runtime/lore/assets/docs/harnesses are supporting
inputs; every slice records primary outcome, user outcome, evidence question,
consumer, acceptance, non-claims, and next link; no second consecutive
research-only slice is selected without an exact dependency; and absent such a
dependency every two accepted slices contain a user-observable result.

- [ ] **Step 3: Preserve authority and safety without reintroducing ceremony**

Retain the single-root default, standing copied-runtime/Ghidra/Git/release
authority, fresh spending/destructive authority, copy identity, Ghidra backup
hard stop, process ownership, optional coordination overlay, and blocker
semantics. Do not add leases or a separate runtime baton as permission gates.

- [ ] **Step 4: Run the focused test**

Expected: canonical-goal and policy tests pass; campaign/baton/front-door/state
tests remain RED.

### Task 3: Rewrite the product portfolio and paused baton

**Files:**
- Modify: `goal.campaign.md`
- Modify: `goal.md`
- Modify: `docs/superpowers/specs/2026-07-15-product-coupled-reconstruction-campaign-design.md`

**Interfaces:**
- Consumes: three-outcome policy and preserved M2.3 packet.
- Produces: product milestone map, next-slice picker, and resume-ready paused
  baton.

- [ ] **Step 1: Replace lane-led milestones with product increments**

Campaign must include:

```text
P0 Product integration foundation
P1 Playable reconstruction verticals
P2 Community WinUI integration and releases
P3 Retail enhancements and mods
P4 Original-game multiplayer epic
P5 Retail asset/mission import
P6 Community knowledge supporting outcomes
```

Retain the compact accepted retail scalar ledger as evidence prerequisites,
not product milestones. Record current First Flight, WinUI, and patch catalog
truth honestly.

- [ ] **Step 2: Install the consumer-first next picker**

Order unsafe shipped correction, actionable evidence debt, playable vertical,
high-value retail enhancement/multiplayer experiment, WinUI integration,
asset/mission import, then product-coupled community knowledge. Include the
two-slice visible-result rule and no shallow quota work.

- [ ] **Step 3: Leave goal.md paused and M2.3 preserved**

Use:

```text
Status: PAUSED (awaiting user goal resume)
Current Slice: M2.3-target-acquisition-static-contract
Primary outcome: Playable Reconstruction
Consumer: deterministic target/lock behavior in OnslaughtRebuild.Core, after
runtime-required behavior is measured
```

Record M2.3 as the narrow dangerous-misinterpretation exception, not a landed
targeting product. Queue shield-to-Core/Godot as the next user-observable
increment and WinUI Reconstruction as the following community integration.

- [ ] **Step 4: Mark the design accepted/implemented only after all gates pass**

Change its status at closeout, not before verification.

### Task 4: Connect the public product front doors and canonical state

**Files:**
- Modify: `README.MD`
- Modify: `CURRENT_CAPABILITIES.md`
- Modify: `rebuild/README.md`
- Modify: `developer_agent_state.json`
- Modify: `documentation_agent_state.json`
- Modify: `re_orchestrator_state.json`

**Interfaces:**
- Consumes: product policy and actual current component capabilities.
- Produces: community-facing relationship and concise current state.

- [ ] **Step 1: Clarify the public product relationship**

README and CURRENT_CAPABILITIES must say WinUI is the community front door,
the reconstruction is a first-class playable companion, and retail
enhancements are a deliberate product outcome. Do not claim that WinUI already
manages First Flight or that the rebuild is retail-complete.

- [ ] **Step 2: Clarify the rebuild relationship**

`rebuild/README.md` must say the component is separate by architecture and
license but not unrelated by product strategy. It is intended to be discovered,
configured, launched, and supplied local user-owned assets through future WinUI
workflows. Preserve Core/Client/Godot boundaries and GPL provenance.

- [ ] **Step 3: Refresh current state without growing history**

Replace current focus/next steps with the paused product-coupled baton. Correct
Onslaught to `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` and AYA to
`53b10b083b59cfd7e72849c15bec8b608eaf8a23`. Preserve useful unrelated verified
truth and blockers.

- [ ] **Step 4: Parse changed JSON and run the focused test**

Run:

```powershell
py -3 -c "import json,pathlib; [json.loads(pathlib.Path(p).read_text(encoding='utf-8')) for p in ('developer_agent_state.json','documentation_agent_state.json','re_orchestrator_state.json')]"
py -3 tools\product_coupled_campaign_strategy_test.py
```

Expected: JSON parse PASS and all focused tests PASS.

### Task 5: Verify, review, integrate, and hand back the new goal

**Files:**
- All strategy-owned files above only.

**Interfaces:**
- Consumes: complete strategy diff.
- Produces: reviewed commits on `main`, synchronized origin, exact resume goal.

- [ ] **Step 1: Run proportional local gates**

```powershell
py -3 -m py_compile tools\product_coupled_campaign_strategy_test.py
py -3 tools\product_coupled_campaign_strategy_test.py
py -3 -c "import json,pathlib; [json.loads(pathlib.Path(p).read_text(encoding='utf-8')) for p in ('developer_agent_state.json','documentation_agent_state.json','re_orchestrator_state.json')]"
git diff --check
C:\Users\david\AppData\Roaming\npm\npm.cmd run test:doc-commands
C:\Users\david\AppData\Roaming\npm\npm.cmd run test:md-links:public-core
C:\Users\david\AppData\Roaming\npm\npm.cmd run test:hard-payload-safety
```

Do not run full `npm test`, native WinUI/Godot, BEA, or the M2.3 contract gate.

- [ ] **Step 2: Complete one bounded review envelope**

Run normal/adversarial Codex review and sanitized normal/adversarial
Cursor/Grok consults against the strategy summary and non-secret selected
diff. Resolve concrete product-coupling, authority, licensing-boundary, stale
state, and anti-wheel-spinning defects. Do not recursively review routine fixes.

- [ ] **Step 3: Stage only the exact strategy allowlist**

Verify cached names and `git diff --cached --check`; ensure all M2.3 paths and
`terminals/` remain unstaged.

- [ ] **Step 4: Commit and push**

Use a strategy implementation commit, then a narrow `goal.md` tip-alignment
commit if needed. Push `main` without force and verify `main...origin/main` is
`0 0`.

- [ ] **Step 5: Return the exact new goal prompt**

Quote the canonical slash goal verbatim so the maintainer can resume it in the
goal system. Confirm the campaign and P1/P2 experiment remained paused, the
installed game/original executable were untouched, and no release occurred.
