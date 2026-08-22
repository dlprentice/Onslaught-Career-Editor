# Validation

Status: active — the gate-selection table
Last updated: 2026-08-21 (Core full suite re-measured after the
wt/t_0bace7cd + t_7d9a828d merges and the Blaster explanation:
**862 passed / 1 failed / 863**, 27 m 40 s; the single remaining failure —
the chain tick pin — was then resolved with a tick-pin-only bisect receipt
and re-pinned (`Level100FullChainTests` class filter 5/5). Both former
failures are explained, not re-fitted — see `developer_state.json` →
`_TICK_BISECT_RESOLVED_20260821` and `_CORE_SUITE_20260821`.)
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
| Rebuild Core | `npm run test:rebuild-core` — measured 2026-08-21: **862 passed / 1 failed / 863 total**, **27 m 40 s** (grew from 856 by the wt/t_0bace7cd + t_7d9a828d merges and the Blaster identity-diff work). The one measured failure — `Level100FullChainTests.ChainAutopilot_ReachesWonByInputAlone` — was then RESOLVED with a tick-pin-only bisect (boundary e633b511; receipts `local-lab/chain-tick-bisect-20260821/`) and re-pinned with the measured attribution; class filter 5/5 after. Both former failures are explained (Blaster: observable reconstruction band, commit 87498824; tick: evidenced TargetZone hit()/InJetMode route change) — see `developer_state.json` → `_TICK_BISECT_RESOLVED_20260821`. Historical: 854/2/856 (2026-08-19), 730/730 `a65826fa`, 729/729 `fd5ab355`; neither is a live count. Use the owner-named filter rather than re-running 28 minutes |
| Rebuild client/adapters | `npm run test:rebuild-client` |
| Godot toolchain or native behavior | the matching `test:rebuild-*` command; native smoke only when native behavior changed |
| Frontend page drawing | `rebuild/tools/Capture-Frontend.ps1 -Plan mainmenu`, which now scores the capture against the retail reference and returns `FAIL` on regression. `npm run test:tools` covers the scorer itself |
| Portable ZIP inputs or layout | `npm run release:winui-zip` |
| Tip census claim in docs | Re-read `developer_state.json` → `current_re_authority`, require its literal READY/reducer/authority-receipt pins, and run the named full replay. Historical Gen10 and candidate Gen73 blocks are not current routing |
| Campaign ledger / generation TSVs | The externally pinned frozen bootstrap in `current_re_authority.verify`; a generation number, matching ledgers, self-derived pins, integrity-only success, or candidate reducer is not authority |
| Tracked evidence register or current authority pointer | `py -3 tools/re_evidence_register_export.py --state developer_state.json --check-header-only` for the portable header gate; on the maintainer host, omit `--check-header-only` and use `--check` for literal-pinned full replay plus byte equality |
| C1 PE plate apply | Exact current pack path/bytes/SHA, entity/body identity, pristine-byte validation, and a field-scoped reducer. Independent normal/adversarial review is strongly advised for consequential changes but is not a fixed model matrix; see `reverse-engineering/REVIEW-PROTOCOL.md` |
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
