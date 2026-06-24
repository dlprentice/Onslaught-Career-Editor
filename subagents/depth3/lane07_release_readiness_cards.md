# Lane 07 Release Readiness Task Cards (Deterministic)

## Scope
This card set converts `R0-R4` release-risk classification into deterministic release-readiness tasks for:
- path-family inventory
- allowlist candidates
- denylist candidates
- policy checks

Source of truth for classification: `subagents/depth2/lane07_release_risk_classification.md`.

## Deterministic Rules
1. Risk class mapping is fixed:
`R0=include`, `R1=include-with-review`, `R2=conditional`, `R3=exclude-default`, `R4=hard-exclude`.
2. A path family can only move from candidate to approved if its card-specific acceptance criteria are fully satisfied.
3. If any policy check for an `R2` family fails, that family resolves to denylist candidate for this release cycle.
4. `R3` and `R4` families are denylist candidates by default without exception handling in this card deck.

## Card Status Values
- `todo`
- `in_progress`
- `pass`
- `fail`
- `blocked`

---

## Inventory Cards

### Card INV-01: Build Path-Family Inventory
- Status: `todo`
- Objective: Produce a complete inventory row for every classified path family.
- Inputs:
`subagents/depth2/lane07_release_risk_classification.md`
- Procedure:
1. Enumerate every row from the "Path-Family Classification Matrix".
2. Record one inventory row per path family with fields:
`path_family`, `risk_class`, `primary_risk_vectors`, `candidate_public_posture`, `candidate_private_posture`.
3. Verify no duplicate `path_family` keys.
- Acceptance Criteria:
1. Inventory row count equals matrix row count.
2. Every row has non-empty `risk_class`.
3. No duplicate path-family key.
- Output:
Inventory table in this section marked `pass` only when all criteria hold.

### Card INV-02: Risk Coverage Check
- Status: `todo`
- Objective: Confirm every risk class (`R0-R4`) has at least one represented path family.
- Inputs:
Inventory from `INV-01`.
- Procedure:
1. Count families per risk class.
2. Compare observed classes to required set `{R0,R1,R2,R3,R4}`.
- Acceptance Criteria:
1. All five classes are present.
2. Counts are explicit and non-zero for each present class.
- Output:
Risk coverage summary with class counts.

### Card INV-03: High-Priority Family Presence Check
- Status: `todo`
- Objective: Ensure immediate-attention risk families are present and classified.
- Required families:
`game/**`, `reverse-engineering/binary-analysis/scratch/**`, `media/**` high-risk families, `save-attempts/**`, `discord_channel_dumps/**`.
- Inputs:
Inventory from `INV-01`.
- Procedure:
1. Verify each required family exists in inventory.
2. Verify each required family class is `R3` or `R4`.
- Acceptance Criteria:
1. All required families found.
2. No required family classified below `R3`.
- Output:
Presence/assertion checklist for required families.

---

## Allowlist Candidate Cards

### Card ALW-01: Seed Deterministic Allowlist Candidates from R0
- Status: `todo`
- Objective: Build initial allowlist candidate set from `R0`.
- Inputs:
Inventory from `INV-01`.
- Procedure:
1. Select all rows where `risk_class=R0`.
2. Emit these families as allowlist candidates with reason `R0 default include`.
- Acceptance Criteria:
1. Candidate set equals exact set of `R0` families, no extras.
2. Each candidate has reason text.
- Output:
Allowlist candidate table (R0 seed).

### Card ALW-02: Add Review-Required Candidates from R1
- Status: `todo`
- Objective: Add `R1` families as review-gated allowlist candidates.
- Inputs:
Inventory from `INV-01`.
- Procedure:
1. Select all `R1` families.
2. Mark each with required check `content sanity review`.
- Acceptance Criteria:
1. Every `R1` family appears exactly once in candidate table.
2. Each row includes `review_required=true`.
- Output:
Allowlist candidate table (R1 review-gated).

### Card ALW-03: Stage Conditional Candidates from R2
- Status: `todo`
- Objective: Stage `R2` families as conditional allowlist candidates pending policy checks.
- Inputs:
Inventory from `INV-01`.
- Procedure:
1. Select all `R2` families.
2. Attach required checks:
`provenance`, `derivative-content`, `endpoint-privacy`, `submodule` (if applicable), `payload`.
3. Default decision for each row is `pending`.
- Acceptance Criteria:
1. All `R2` families are represented.
2. Every row includes at least one required policy check.
3. No row defaults to `approved`.
- Output:
Allowlist candidate table (R2 pending).

### Card ALW-04: Approve Allowlist Candidates Deterministically
- Status: `todo`
- Objective: Produce final allowlist approval decisions using only class rules plus policy-check outcomes.
- Inputs:
`ALW-01`, `ALW-02`, `ALW-03`, `POL-01..POL-05`.
- Procedure:
1. Auto-approve all `R0` rows.
2. Approve `R1` rows only if review check passes.
3. Approve `R2` rows only if all required policy checks pass.
4. Reject any row with failed or missing required checks.
- Acceptance Criteria:
1. Final approved set contains no `R3` or `R4`.
2. Every approved `R2` row has all required checks marked `pass`.
3. Every rejected row includes deterministic reason code.
- Output:
Final allowlist decision table with reason codes.

---

## Denylist Candidate Cards

### Card DEN-01: Baseline Denylist from R3 and R4
- Status: `todo`
- Objective: Build baseline denylist candidates from high-risk classes.
- Inputs:
Inventory from `INV-01`.
- Procedure:
1. Select all rows where `risk_class in {R3,R4}`.
2. Mark `deny_reason` as `class_default_exclude`.
- Acceptance Criteria:
1. Denylist includes every `R3` and `R4` family exactly once.
2. No `R0` family is included.
- Output:
Baseline denylist candidate table.

### Card DEN-02: Add Pattern-Based Operational Denylist Families
- Status: `todo`
- Objective: Ensure operational residue patterns are denylisted.
- Required patterns:
`*_state.json`, `*_state.json.tmp`, `bin/**`, `obj/**`, `.venv/**`, `__pycache__/**`, `.tmp_*/**`.
- Inputs:
Classification denylist baseline and matrix.
- Procedure:
1. Verify each required pattern appears in denylist candidate coverage.
2. Add missing required patterns with reason `operational_residue`.
- Acceptance Criteria:
1. All required patterns are present.
2. Every required pattern has deny reason.
- Output:
Pattern denylist candidate table.

### Card DEN-03: Hard-Exclude Family Assertion
- Status: `todo`
- Objective: Assert all `R4` families are hard-exclude candidates.
- Inputs:
Inventory from `INV-01`.
- Procedure:
1. Filter `R4` families.
2. Mark each as `hard_exclude=true`.
- Acceptance Criteria:
1. Every `R4` row has `hard_exclude=true`.
2. No `R4` row appears in final allowlist output.
- Output:
Hard-exclude assertion table.

### Card DEN-04: Resolve Failed Conditional Candidates to Denylist
- Status: `todo`
- Objective: Deterministically move failed `R2` candidates to denylist.
- Inputs:
`ALW-03`, `POL-01..POL-05`.
- Procedure:
1. Select `R2` rows with any failed required policy check.
2. Add to denylist with reason code `r2_gate_failed`.
- Acceptance Criteria:
1. Every failed `R2` candidate appears in denylist.
2. Reason code includes failed check identifiers.
- Output:
Denylist addendum for failed conditional candidates.

---

## Policy Check Cards (for R2 and Review-Gated Families)

### Card POL-01: Provenance Check
- Status: `todo`
- Objective: Validate publishability provenance for each conditional family.
- Applicable families:
All `R2`, plus any `R1` row requiring provenance sanity.
- Procedure:
1. Confirm each family has a documented ownership/provenance statement.
2. Mark result `pass/fail`.
- Acceptance Criteria:
1. No applicable row left without decision.
2. Failures include `provenance_missing` or `permission_unclear`.
- Output:
Per-family provenance decision table.

### Card POL-02: Derivative-Content Check
- Status: `todo`
- Objective: Enforce summary-over-raw policy for reverse-engineering-heavy families.
- Applicable families:
`reverse-engineering/source-code/**`, `reverse-engineering/game-assets/**`, `reverse-engineering/binary-analysis/functions/**`, other `R2` derivative families.
- Procedure:
1. Check whether content is curated summary vs raw bulk derivative output.
2. Mark `pass` only for curated summary posture.
- Acceptance Criteria:
1. Raw bulk derivative families cannot pass.
2. Each failure has reason `raw_derivative_bulk`.
- Output:
Derivative-content decision table.

### Card POL-03: Endpoint and Privacy Check
- Status: `todo`
- Objective: Ensure no private endpoint/path/personal data leakage in candidate families.
- Applicable families:
All `R2`, plus `R1` where private metadata risk exists.
- Procedure:
1. Scan for machine-local absolute paths, private URLs, and personal identifiers.
2. Mark `pass` when none found.
- Acceptance Criteria:
1. No applicable row remains unchecked.
2. Failures include concrete finding type:
`private_url`, `machine_path`, or `personal_data`.
- Output:
Endpoint/privacy finding table.

### Card POL-04: Submodule Target and License Check
- Status: `todo`
- Objective: Validate submodule references used by conditional candidates.
- Applicable families:
`.gitmodules`, `references/Onslaught`, `references/AYAResourceExtractor`.
- Procedure:
1. Confirm targets are intended and publicly reachable for release context.
2. Confirm license compatibility is documented.
- Acceptance Criteria:
1. Each applicable row has `target_ok` and `license_ok` booleans.
2. Any false value yields failed policy check.
- Output:
Submodule policy decision table.

### Card POL-05: Artifact Payload Check
- Status: `todo`
- Objective: Ensure conditional script/media/patch families do not include proprietary binary payloads.
- Applicable families:
`tools/**`, `patches/**`, `media/generated-art/**`, other `R2` payload-carrying families.
- Procedure:
1. Verify each family payload is source-only or explicitly publishable.
2. Flag unknown binary blobs as fail.
- Acceptance Criteria:
1. Every applicable row has payload classification.
2. Unknown or proprietary payloads fail with reason `payload_not_publishable`.
- Output:
Artifact payload decision table.

---

## Deterministic Candidate Inventories (Seeded from Classification)

### Allowlist Candidates (Initial)
| Family | Seed Class | Initial Decision Rule |
|---|---|---|
| Core C# app files (`Program.cs`, `BesFilePatcher.cs`, `App*.cs`, `MainWindow*.xaml*`, `Views/**`, project/solution files) | R0 | candidate_allow |
| Python implementation (`patcher.py`, `onslaught/**`, `onslaught_explorer.py`) | R0 | candidate_allow |
| Test suites (`OnslaughtCareerEditor.UiTests/**`, `tests_pyqt/**`) | R0 | candidate_allow |
| Root docs (`README.MD`, `LICENSE`, selected root `.md`) | R1 | candidate_allow_review |
| `roadmap/**` | R1 | candidate_allow_review |
| `lore/**` | R1 | candidate_allow_review |
| `lore-book/**` | R1 | candidate_allow_review |
| `reverse-engineering/save-file/**` | R1 | candidate_allow_review |
| `reverse-engineering/game-mechanics/**` | R1 | candidate_allow_review |
| `reverse-engineering/project-meta/**` | R1 | candidate_allow_review |
| `reverse-engineering/source-code/**` | R2 | candidate_conditional |
| `reverse-engineering/game-assets/**` | R2 | candidate_conditional |
| `reverse-engineering/binary-analysis/functions/**` | R2 | candidate_conditional |
| `reverse-engineering/binary-analysis` curated top-level docs/artifacts | R2 | candidate_conditional |
| `references/*` gitlinks and `.gitmodules` | R2 | candidate_conditional |
| `tools/**`, `patches/**`, `media/generated-art/**` | R2 | candidate_conditional |

### Denylist Candidates (Initial)
| Family | Seed Class | Initial Decision Rule |
|---|---|---|
| `reverse-engineering/binary-analysis/*.jsonl` + tracking state artifacts | R3 | candidate_deny |
| `media/patches/**` (unverified provenance) | R3 | candidate_deny |
| `save-attempts/**` | R3 | candidate_deny |
| `subagents/**` | R3 | candidate_deny |
| `wave_online_audit*/**` | R3 | candidate_deny |
| generated/runtime residue (`*_state.json`, `*_state.json.tmp`, `bin/**`, `obj/**`, `.venv/**`, `__pycache__/**`, `.tmp_*/**`) | R3 | candidate_deny |
| `game/**` | R4 | candidate_hard_deny |
| `BEA_Widescreen.exe`, `BEA.exe.gzf` | R4 | candidate_hard_deny |
| copyrighted media families (`media/packaging/**`, `media/publications/**`, `media/wallpapers/**`, `media/portraits/**`, `media/flash/**`) | R4 | candidate_hard_deny |
| `reverse-engineering/binary-analysis/scratch/**` | R4 | candidate_hard_deny |
| `discord_channel_dumps/**` | R4 | candidate_hard_deny |

---

## Release-Readiness Completion Gate
Mark lane readiness as `pass` only if all are true:
1. `INV-01..INV-03` are `pass`.
2. `ALW-04` is `pass`.
3. `DEN-01..DEN-04` are `pass`.
4. `POL-01..POL-05` are `pass` for all applicable families.
5. Final allowlist contains only rows with deterministic approval paths and no unresolved policy failures.

If any condition fails, lane readiness is `fail` with blocking card IDs listed.
