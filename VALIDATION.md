# Validation

Status: active — the gate-selection table
Last updated: 2026-07-28 (body; the tracked-`.md`-header row was added that
day). Header fields added at the same time under
[`DOCUMENTATION.md`](DOCUMENTATION.md); no other row was re-reviewed.
Summary: choosing the smallest evidence that proves the contract you changed.
[`package.json`](package.json) owns the commands.

Validation is proportional to the contract changed. Root
[`package.json`](package.json) is the command authority; the commands below are
options, not a required sequence.

| Change | Focused evidence |
| --- | --- |
| Documentation or deletion only | `git diff --check`, `npm run test:docs`, and the affected generator/reference check |
| A new or edited tracked `.md` header | `npm run test:doc-headers`, which is also inside `test:docs`. The contract is [`DOCUMENTATION.md`](DOCUMENTATION.md); the backlog of pre-standard documents is `tools/doc_header_backlog.txt` and may only shrink |
| AppCore behavior | `npm run test:appcore` or a narrower `dotnet test --filter` |
| WinUI behavior or copy | `npm run test:ui` or the affected test fixture, then one real-app workflow smoke |
| Save, options, copied-target, or patch safety | `npm run test:safe-copy` plus the owning focused test |
| CLI | `npm run test:cli` and the relevant AppCore test |
| Lore inputs/reader | `npm run test:lore-pack` plus the LoreBrowserService tests |
| Public payload/provenance boundary | `npm run test:safety` |
| Rebuild Core | `npm run test:rebuild-core` |
| Rebuild client/adapters | `npm run test:rebuild-client` |
| Godot toolchain or native behavior | the matching `test:rebuild-*` command; native smoke only when native behavior changed |
| Frontend page drawing | `rebuild/tools/Capture-Frontend.ps1 -Plan mainmenu`, which now scores the capture against the retail reference and returns `FAIL` on regression. `npm run test:tools` covers the scorer itself |
| Portable ZIP inputs or layout | `npm run release:winui-zip` |

Rebuild commands materialize their exact retail inputs to ignored paths from a
detected user installation. Run `npm run prepare:rebuild-assets` explicitly when
only that boundary changed; pass `-- --game-root "<game folder>"` when Steam
auto-detection cannot find a custom location.

`npm test` is the focused default handoff for cross-cutting active-product work:
one WinUI solution build, consequential AppCore write/parser safety contracts,
and the static WinUI accessibility audit. It intentionally does not run broad
UI, rebuild, release packaging, Ghidra, private runtime probes, or historical
repository accounting.

Generated check output belongs under ignored `.artifacts/`, `local-lab/`, or
another explicitly selected local scratch root. Validation output is not source
evidence or release content by itself.

Do not add a new test during cleanup unless implementation behavior changed,
the regression is consequential, and no focused existing check covers it. Do
not fix unrelated failures discovered outside the changed contract.
