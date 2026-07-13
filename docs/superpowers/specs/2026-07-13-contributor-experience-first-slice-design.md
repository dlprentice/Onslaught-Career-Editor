# Contributor Experience First Slice: Audit And Design

Status: proposed bounded cleanup
Date: 2026-07-13

## Purpose

Make the public contribution path easier to understand without rewriting shared
front doors, deleting historical evidence, or treating the repository's large
research surface as ordinary contributor ceremony. This document is both the
requested initial audit and the design for the first cleanup slice so the audit
does not create a second planning chain.

## Scope And Boundaries

The first slice may change only this audit and the three existing GitHub
templates:

- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`

It does not change `README.MD`, `CONTRIBUTING.md`, `COLLABORATION.md`,
`AGENTS.md`, root `package.json`, generated indexes, canonical state batons,
product code, patch bytes, rebuild code, Lore or RE claims, release workflows,
or repository contents outside those paths. It adds no hosted validation or
automation.

## Contributor Journey Audit

### 1. Arrival And Orientation

The public repository has a credible primary route:

1. `README.MD` explains the product, current lanes, quick start, and safety
   boundary.
2. `CONTRIBUTING.md` asks a contributor to run `npm test`, launch the WinUI app,
   choose one lane, and use focused validation.
3. `VALIDATION.md` supplies the measured change-class matrix.
4. `COLLABORATION.md` supplies the handoff fields.

The problem is not missing guidance. The same setup, lane, command, safety, and
handoff facts are repeated across `README.MD`, `CONTRIBUTING.md`, `AGENTS.md`,
`COLLABORATION.md`, and release guidance. The documents are mostly current, but
the repetition increases drift risk and makes it unclear which detail belongs
to which audience.

### 2. Choosing Work And Commands

Root `package.json` contains 1,512 scripts. `VALIDATION.md` correctly classifies
1,087 Ghidra/wave commands as historical proof and 98 commands as runtime proof,
while the normal `npm test` profile reaches only 12 commands transitively. That
is a strong safety and ergonomics improvement.

The remaining discovery gap is human-facing: contributors are told that
`package.json` is command authority, but browsing 1,512 names is not useful and
the machine-readable inventory is JSON intended for analysis rather than a
short command menu. The current measured `npm test` closeout is about 210
seconds, so it is a meaningful baseline rather than an instant preflight.
Focused commands are documented, but repeated command blocks across several
front doors can still drift.

### 3. Opening An Issue Or Pull Request

The templates are concise and preserve important payload, mutation, evidence,
and release boundaries. They are nevertheless behind the current contributor
taxonomy:

- the pull-request lane line omits the rebuild and runtime-tooling lanes;
- both issue templates omit those lanes as well;
- the pull-request template compresses several required handoff facts instead
  of mirroring the explicit `COLLABORATION.md` fields;
- there is no filled, concrete example of a good pull request, only prose and
  blank template prompts.

The missing example is a follow-up, not a reason to enlarge the first slice.
Aligning the existing templates first removes the direct workflow mismatch.

## Repository Clutter Map

The current tracked tree is intentionally broad, but its scale makes ownership
classification essential:

| Surface | Measured size | Classification | Cleanup posture |
| --- | ---: | --- | --- |
| `reverse-engineering/` | 13,395 files | Canonical research/evidence | Keep; improve generated routing before structural cleanup |
| `tools/` | 2,647 files | Active and historical tooling | Keep; route through `tools/README.md` and validation profiles |
| `release/` | 1,712 files | Current policy plus dated evidence | Classify current versus historical before moves |
| `lore-book/` | 1,143 files | Protected/generated projections | Never hand-delete; change canonical inputs and owning generators |
| Markdown indexes | 368 files | 181 canonical RE, 184 Lore-book projections, 3 other | Treat canonical and projected copies as one generated family |
| `subagents/` | 104 tracked files | Mixed compact reports and historical snapshots | Preserve unique conclusions; classify generated/raw-looking families before pruning |
| `wave_online_audit*` | 8 files | Historical audit evidence | Candidate for archive routing, not immediate deletion |

The highest-value clutter candidates are not safe first deletions:

- `setuphistory.txt` is a machine-specific Direct3D capability log at repository
  root and is excluded from release profiles.
- `MCP_DEBUGGING_OPTIONS.md` and `MCP_LIMITATIONS.md` are private maintainer
  workstation notes at repository root and are release-excluded.
- `onslaught_codex_directive.md` is explicitly superseded operator provenance
  but remains a root-level file.
- tracked `subagents/` snapshots and the two `wave_online_audit` roots are
  historical material in contributor-visible locations.

Those paths are referenced by release classification, hygiene checks, tools,
or historical docs. A later cleanup must first record the canonical owner,
active consumers, unique evidence, replacement location, and exact rollback.
No file in those families is deleted or moved by the first slice.

## Stale And Duplicate Front Doors

Ranked by contributor impact:

1. **GitHub templates:** current workflow entry points with an outdated lane
   list and incomplete handoff-field parity. This is the first slice.
2. **`CONTRIBUTING.md` static-RE status:** it still says a prior Ghidra snapshot
   is under deep review, while current goal evidence records the completed
   full-reaudit closeout. This requires integration-owned front-door
   reconciliation.
3. **Root setup and command duplication:** `README.MD`, `CONTRIBUTING.md`,
   `AGENTS.md`, and `COLLABORATION.md` repeat prerequisites, lane commands, and
   safety rules. The facts are generally aligned, but future work should make
   one human workflow authoritative and let other documents route to it.
4. **Release guidance chain:** `README.RELEASE.md`,
   `RELEASE_SCOPE_AND_TEST_COMMANDS.md`, and
   `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` overlap on prerequisites,
   release shape, safety, and gates. The public sign-off guide is the clearest
   command authority; the other two should eventually narrow to release notes
   and scope.
5. **Private maintainer notes at root:** `MCP_LIMITATIONS.md` points to an
   `AGENTS.md` section named `Context Reset / Compaction Resume Checklist` that
   no longer exists. Its root placement also makes a private workstation note
   look like contributor startup material.

## Validation Pain Points

- `npm test` is a useful common baseline but takes minutes, so a first-time
  contributor can interpret it as the only acceptable edit loop even though
  focused gates exist.
- `npm run` exposes 1,512 scripts without a short human-facing command index.
- command blocks are repeated across active docs, increasing synchronization
  cost and stale-copy risk.
- the all-tree payload and hygiene gates take multiple minutes and are
  intentionally unsuitable for every small contribution; this distinction is
  documented but easy to miss in copied command lists.
- `npm run test:md-links` writes ignored output, while the minor-doc
  `test:md-links:public-core` check is non-writing; contributors need the
  change-class matrix to understand that distinction.

The first slice does not add another command alias. A later command-discovery
slice should generate one short contributor menu from the validated profile
inventory rather than maintain another handwritten list.

## Considered Approaches

### A. Templates First — Selected

Align the three GitHub templates with the current lane taxonomy and the public
handoff contract. This removes a live mismatch, has a small write set, does not
compete with integration-owned root docs, and has a one-commit rollback.

### B. Rewrite Shared Front Doors First

This could reduce duplication sooner, but it overlaps integration-owned files
and active campaign truth. It would mix information architecture with current
RE, release, and product reconciliation, making review and rollback harder.

### C. Delete Or Move Clutter First

This would produce the most visible file-count reduction, but several
candidates are protected projections or inputs to release and hygiene checks.
Without consumer and preservation proof, deletion would optimize appearance at
the cost of evidence and reproducibility.

## First Slice Design

The pull-request template will:

- present the current lane choices: WinUI, AppCore/CLI, RE-informed rebuild,
  patch/mod safety, runtime tooling, docs, RE/Lore, and public/release boundary;
- ask for exact validation commands and results;
- ask separately for relevant validation intentionally skipped;
- preserve the existing payload, copied-target, evidence-class, and no-hosted-
  automation checkboxes;
- expose the `COLLABORATION.md` handoff fields for private/public boundary,
  state disposition, installed game/original `BEA.exe` mutation, and remaining
  risks.

The issue templates will use the same current area vocabulary where relevant,
retain the existing public-safe reproduction/problem prompts, and keep the
explicit `SECURITY.md` route for private data, proprietary content, security,
or online-session concerns. They will not request attachments or raw proof.

## Verification

The proportional gate set is:

```powershell
git diff --check
npm run test:doc-commands
npm run test:md-links:public-core
```

A focused PowerShell assertion will also confirm that all three templates
contain the intended lane and boundary terms. Whole-tree hygiene, public
allowlist, product builds, native WinUI/Godot, game, debugger, Ghidra, and
release gates are intentionally skipped because the slice changes only public
Markdown workflow templates and this design document.

The final diff receives one normal and one adversarial Codex review plus serial
sanitized normal and adversarial Cursor/Grok consultation. Reviewers are
read-only and do not own acceptance.

## Preservation And Rollback

No historical or generated file is removed. The preimage is the current
`82bbc2c0` version of the three templates. Rollback is a revert of the bounded
template commit and removal or archival of this design artifact if the
information-architecture decision is rejected. No state migration, generated
index regeneration, package mutation, game/runtime action, or release action
is involved.

## Follow-Up Order

After this slice is accepted, the next useful work is:

1. generate a short contributor command menu from validation-profile truth;
2. reconcile the stale Ghidra sentence and reduce root-guide duplication with
   the integration owner;
3. classify root maintainer notes, tracked subagent reports, and wave audit
   roots with explicit consumers and preservation destinations;
4. classify canonical versus generated indexes before removing generated
   noise.

Each follow-up is a separate evidence-backed cleanup, not a prerequisite chain
for ordinary contributions.
