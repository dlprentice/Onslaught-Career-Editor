# Depth4 Lane 09 Risk Register

Generated: 2026-03-04
Scope synthesized from: `subagents/depth1/*`, `subagents/depth2/*`, `subagents/depth3/*`.

## Severity Totals

| Severity | Count |
|---|---:|
| Critical | 4 |
| High | 6 |
| Medium | 4 |
| Low | 1 |

## Register

| Risk ID | Severity | Risk | Blockers | Assumptions | Confidence | Mitigation | Owner | Evidence |
|---|---|---|---|---|---|---|---|---|
| RR-001 | Critical | Public release can accidentally ship high-risk/private families (`game/**`, `media/**`, `scratch/**`, state/orchestration artifacts). | No enforced allowlist/denylist gate yet; release-readiness cards are still `todo`. | Public release packaging may be attempted from current tree. | Very High (0.97) | Execute lane07 inventory/allowlist/denylist/policy cards and enforce denylist in packaging dry-runs before release. | main-agent | `depth1/lane09`, `depth2/lane07`, `depth3/lane07` |
| RR-002 | Critical | Canonical semantics drift on `defaultoptions.bea` write behavior (conditional vs unconditional) can drive incorrect implementation and user guidance. | Multi-file wording fixes pending across docs, app copy, and code comments. | Team uses canonical docs/UI text as behavioral authority. | High (0.93) | Apply L9 semantic/UI cards and run cross-file grep verification on `DAT_0082b5b0 == 0` + load/save sync wording. | main-agent | `depth2/lane09`, `depth3/lane09` |
| RR-003 | Critical | `documentation-standards` skill drift can reintroduce invalid anchors (`CLAUDE.md`) and legacy offset framing. | Skill file outside repo remains stale; no automatic drift guard for skill content. | Agents will continue using this skill during documentation work. | High (0.94) | Apply SD-01..SD-05 updates and add periodic skill drift checks against repo-canonical rules. | main-agent | `depth1/lane08`, `depth2/lane03`, `depth3/lane03` |
| RR-004 | Critical | Safety-critical regressions can ship undetected due missing P0 tests (read-only CLI contracts, options-file safety guard, C# binary patch path). | Missing test files/suites; C# binary patch path lacks parity-grade regression coverage. | Ongoing changes will continue touching CLI/patch flows. | High (0.92) | Implement P0 test cards first and make them gating checks in validation commands. | main-agent | `depth1/lane03`, `depth2/lane08`, `depth3/lane08` |
| RR-005 | High | GUI behavior parity drift persists (config in-place policy mismatch, nested status mismatch, duplicated Python analyzer options section). | Parity fix cards are planned but not implemented; C# GUI action tests sparse. | Cross-stack behavior parity remains a project requirement. | High (0.90) | Execute L4-C01/C02/C05/C06 first, then lock behavior with new GUI tests. | main-agent | `depth2/lane04`, `depth3/lane04` |
| RR-006 | High | CLI contract drift remains (Python missing `--version`; validation/error-stage output differences). | `patcher.py` parser and validation ordering changes not yet applied. | Users/tooling rely on consistent cross-stack CLI behavior. | High (0.89) | Implement CLI-01..CLI-04 and enforce marker-based parity tests for analyze/compare/error paths. | main-agent | `depth2/lane05`, `depth3/lane05` |
| RR-007 | High | Binary patch governance gap: no explicit stable vs experimental taxonomy or hash-profile-aware targeting in active tooling. | Requires owner signoff for taxonomy and policy for unknown hashes/variants. | Binary patch workflows remain user-facing in both GUI stacks and scripts. | High (0.91) | Implement BP-S-001/S-002/S-004 before expanding patch surface area. | main-agent | `depth1/lane04`, `depth2/lane06`, `depth3/lane06` |
| RR-008 | High | Experimental patch proposals (28-region widescreen/code-cave, extra startup gates, binary cardid bypass) have high blast radius and incomplete mapping confidence. | Additional byte targets and safe decision points are not fully mapped/validated. | Experimental tracks may be requested after stable lane completion. | Medium (0.58) | Keep experimental lanes opt-in only, require full backup + per-site byte manifests + staged QA matrix before apply. | main-agent | `depth2/lane06`, `depth3/lane06` |
| RR-009 | High | Modernization rollout can drift or regress due `defaultoptions.bea` rewrite side effects and no broad GPU/driver compatibility matrix. | No implemented drift detector/reapply policy; no fixed compatibility matrix in runbook. | Wrapper/profile modernization stages will proceed. | Medium-High (0.84) | Enforce Stage 0-2 guardrails first: profile drift checks, baseline reapply policy, and minimal NVIDIA/AMD/Intel matrix before deeper changes. | main-agent | `depth2/lane10` |
| RR-010 | High | Doc contradictions can mis-prioritize work (for example stale roadmap parity status and stale validation commands). | Multiple docs require synchronized edits; no automatic parity lint in place. | Contributors use roadmap/checklists as execution authority. | High (0.90) | Apply lane01 fix cards and add docs parity lint tests from lane08 P2 cards. | main-agent | `depth2/lane01`, `depth3/lane01`, `depth3/lane08` |
| RR-011 | Medium | RE execution-state ambiguity (`deep-validation-status` closed vs pending mutation backlog/state) can mislead triage and planning. | State/backlog/status are split across multiple files with different scopes. | Readers may consume one status source without cross-checking others. | High (0.87) | Add explicit cross-reference note and a single reconciled status summary in the canonical roadmap/process docs. | main-agent | `depth1/lane07`, `depth1/lane05` |
| RR-012 | Medium | Submodule public-release suitability is unresolved (URL target, accessibility, licensing/provenance). | No completed submodule policy check/retarget decision for release profile. | Public branch may retain `.gitmodules` and reference gitlinks. | Medium-High (0.83) | Run POL-04 decisions; retarget to intended public upstreams or exclude for public profile. | main-agent | `depth1/lane10`, `depth1/lane09`, `depth2/lane07` |
| RR-013 | Medium | Validation execution can stall on environments lacking GUI test prerequisites (`dotnet`, `pytest`, `PyQt6`, interactive desktop). | Bootstrap prerequisites are not consistently enforced/documented per environment. | Future lanes may run in similarly under-provisioned environments. | High (0.88) | Implement L4-C09 prerequisites/runbook hardening and preflight checks before parity validation passes. | main-agent | `depth2/lane04`, `depth3/lane04` |
| RR-014 | Medium | Binary patch restore/operator confusion risk from mixed backup suffix conventions (`.original.backup` vs `.backup`). | Legacy scripts still use alternate suffix and separate restore expectations. | Operators will use both app and script flows interchangeably. | High (0.86) | Normalize suffix handling or support dual-suffix restore with explicit warnings and migration guidance. | main-agent | `depth1/lane04`, `depth2/lane06` |
| RR-015 | Low | Lore mirror parity checks can raise false-positive drift from intentional path-depth link normalization. | Allowed exception rule is not codified in parity tooling/docs as a formal invariant. | Mirror parity checks continue to run in future maintenance passes. | High (0.91) | Keep deterministic one-file exception (`lore/_index.md`) and codify allowed rewrite rule to suppress noise. | main-agent | `depth1/lane06`, `depth2/lane02`, `depth3/lane02` |

## Immediate Blocker Set

| Blocker ID | Blocking Scope | Severity | Owner | Fastest Mitigation |
|---|---|---|---|---|
| B-01 | No enforceable public release gate (allowlist/denylist/policy cards not executed) | Critical | main-agent | Run `INV/ALW/DEN/POL` cards and freeze a deterministic release profile. |
| B-02 | P0 test gaps for safety and binary patch regressions | Critical | main-agent | Implement lane08 P0 cards and add them to required validation commands. |
| B-03 | Cross-file semantics wording drift on `.bes/.bea` sync behavior | Critical | main-agent | Apply lane09 semantic/UI card replacements and run regex verification. |
| B-04 | Skill guidance drift in `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md` | Critical | main-agent | Apply lane03 skill fix cards and re-run drift scan. |
