# Validation

Status: active — the gate-selection table
Last updated: 2026-08-06 (RE rows added; app/rebuild rows not re-reviewed).
Header fields under [`DOCUMENTATION.md`](DOCUMENTATION.md).
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
| Tip census claim in docs | Re-read `developer_state.json` → `complete_re_tip_20260805` (and FINAL-3WAY-DELTA if named); do not trust Gen10 prose in DELTA/PARITY_LAB as live tip |
| Campaign ledger / generation TSVs | Frozen generation `re_campaign.py verify` (or the owning tool for that plate); tip campaigns may REFUSE without reducer — expected |
| C1 PE plate apply | Mutual packSha256 on DISPOSITION/SUMMARY/FORMAL-PACK; standing **six-way** after last hygiene (Grok subagent N+A, DeepSeek Flash max N+A, Opus medium N+A); **direct DeepSeek session carve-out**: native OpenCode subagent N+A satisfies the reviewer bar, external CLIs on request (see AGENTS.md); peBodySha256 dual-pin to specimen |
| C2_BOUNDED_RUNTIME claim | Entity-scoped controlled runtime + can-fail refuter; refuse PE-only bulk C2 |
| Ghidra mutation | `reverse-engineering/ghidra/README.md` promotion gate + explicit operator authorization; default **not authorized** |

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
