# Summary

What changed, why, and which user or contributor problem it solves.

## Scope

Lane (check exactly one):

- [ ] WinUI app
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

- [ ] The installed game folder and original `BEA.exe` were not mutated.
- [ ] No proprietary game assets, copied executables, arbitrary saves/options,
      screenshots, frame captures, raw debugger logs, secrets, or raw/bulky
      generated proof payloads, unredacted private paths, or machine identifiers
      were added to the branch or pasted into this PR. Compact non-secret
      summaries remain allowed when useful.
- [ ] Patch/write workflows still target copied files or app-owned roots.
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

State baton update: name updated files, or write `read-only/no state edit`.

Installed game / original `BEA.exe` mutation: none

Copied-profile/runtime proof belongs under validation and the boundary check;
it is never an exception to the `none` answer above.

Remaining risks or follow-ups:
