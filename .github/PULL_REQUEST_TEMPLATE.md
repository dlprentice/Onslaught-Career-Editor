# Summary

What changed, why, and which user or contributor problem it solves.

## Scope

Areas affected:

- [ ] Godot toolkit companion / retained toolkit source
- [ ] AppCore / CLI
- [ ] RE-informed rebuild
- [ ] Patch / mod safety
- [ ] Runtime tooling
- [ ] Docs
- [ ] RE / Lore docs
- [ ] Public/release boundary

Main paths changed:

Out of scope:

## Validation

Validation run (exact local commands and results):

Validation intentionally skipped (relevant commands and reason):

## Safety And Claims

- [ ] Validation used disposable copies and preserved pristine inputs.
- [ ] No proprietary game assets, copied executables, arbitrary saves/options,
      bulk frame captures, raw debugger logs, secrets, or raw/bulky
      generated proof payloads, unredacted private paths, or machine identifiers
      were added to the branch or pasted into this PR. Compact non-secret
      summaries and screenshots registered under the attribution policy remain allowed.
- [ ] Writes preserve unknown save bytes and enforce the selected target. Installed-game
      patching requires an informed choice and a verified recovery backup before writing.
- [ ] Runtime, online, gameplay, visual, RE-semantic, and rebuild claims do not
      exceed the evidence in this PR.
- [ ] No hosted CI/release automation or public release action was added.

Private/public boundary check (write `none` or name affected paths/artifacts):

- Hard payloads:
- Release-manifest entries:
- Copied-game proof summaries:
- Local evidence (redacted paths or compact non-secret summaries only; no raw
  proof bundles):

## State And Risks

Documentation state update — name the docs this change puts out of date and
whether they were updated (for example `CURRENT_CAPABILITIES.md`, the affected
`README`, an evidence document), or write `read-only/no doc state edit`.

Product write behavior changed (selected targets, backup/refusal behavior), or `none`:

Remaining risks or follow-ups:
