# Tools Surface Map

Status: public-safe orientation note
Last updated: 2026-06-23

`tools/` in a public candidate is a curated subset for release checks, public
source-package validators, and AppCore/WinUI smoke helpers. The private
maintainer tree has many more RE/runtime proof scripts; those are intentionally
absent from public candidates unless rewritten as public-safe support tooling.
Do not treat every private-tree script name mentioned in historical docs as a
public PR gate or user-facing workflow.

## Public Package Gates

The public candidate root `package.json` is the command authority for external
contributors. Start with:

- `npm run test:doc-commands`
- `npm run test:md-links`
- `npm run test:public-allowlist`
- `npm run test:repo-hygiene`
- `npm run test:winui-primary-lane`
- `npm run test:winui-safe-copy-preflight`
- `npm run test:winui-patch-engine-safety`

Use `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` for the full public
candidate sequence.

## Source Export Helpers

Private maintainers use `tools/export_curated_release_tree.py` to materialize a
public-safe source candidate from the generated allowlist. The export writes
`EXPORT_PROVENANCE.json` in the destination and validates the fresh payload
before returning.

## Evidence And Maintainer Helpers

Many private-tree scripts validate bounded evidence, but they are not normal
public gates unless the public `package.json` calls them and the curated export
includes them. Live copied-game launches, CDB/Ghidra work, second-host
networking proof, private asset output, and runtime proof roots remain
maintainer-controlled workflows with separate authorization and safety
boundaries.

For bulky live copied-game proof runs, prefer an explicit private artifact root
outside the public candidate and keep local machine-specific paths in private
state. Raw runtime artifacts can contain local paths, copied-profile paths,
screenshots, CDB logs, and other private proof material; do not paste them into
public readiness notes or public PRs. Publish only redacted summaries and
machine-checkable public-safe counters.

Defender posture: live runtime helpers are maintainer-only and arm-gated. They
may compile a local runner, launch a copied executable, attach CDB, capture
frames, and send scoped input by design. Prefer tracked scripts, narrow
arguments, and one reviewed external proof root instead of inline shell byte
dumps or broad ad hoc scans.
