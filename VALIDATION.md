# Validation

Validation is proportional to the contract changed. Root
[`package.json`](package.json) is the command authority; the commands below are
options, not a required sequence.

| Change | Focused evidence |
| --- | --- |
| Documentation or deletion only | `git diff --check`, `npm run test:docs`, and the affected generator/reference check |
| AppCore behavior | `npm run test:appcore` or a narrower `dotnet test --filter` |
| WinUI behavior or copy | `npm run test:ui` or the affected test fixture, then one real-app workflow smoke |
| Save, options, copied-target, or patch safety | `npm run test:safe-copy` plus the owning focused test |
| CLI | `npm run test:cli` and the relevant AppCore test |
| Lore inputs/reader | `npm run test:lore-pack` plus the LoreBrowserService tests |
| Public payload/provenance boundary | `npm run test:safety` |
| Rebuild Core | `npm run test:rebuild-core` |
| Rebuild client/adapters | `npm run test:rebuild-client` |
| Godot toolchain or native behavior | the matching `test:rebuild-*` command; native smoke only when native behavior changed |
| Portable ZIP inputs or layout | `npm run release:winui-zip` |

`npm test` is the focused default handoff for cross-cutting active-product work:
one WinUI solution build, AppCore/UI tests from that build, and deterministic
rebuild Core tests. It intentionally does not run release packaging, native
Godot, Ghidra, private runtime probes, or historical repository accounting.

Generated check output belongs under ignored `.artifacts/`, `local-lab/`, or
another explicitly selected local scratch root. Validation output is not source
evidence or release content by itself.

Do not add a new test during cleanup unless implementation behavior changed,
the regression is consequential, and no focused existing check covers it. Do
not fix unrelated failures discovered outside the changed contract.
