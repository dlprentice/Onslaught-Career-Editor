# Validation

Status: active — the gate-selection table
Last updated: 2026-08-23 (PROGRAM P9 moved the forty-run
`Level100FerrySweepFixture` from the default Core command to an explicit sweep.
Runner discovery proves the post-split 942-test population is exactly the
disjoint union of 936 default tests and six ferry tests; the explicit command
passed all six over the unchanged twenty-perturbation, two-arm matrix. Timing
and overload-invalidity details are in the Rebuild Core row.)
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
| Rebuild Core | `npm run test:rebuild-core` is the default and excludes only `Level100FerryLandingTests`; use `npm run test:rebuild-ferry-sweep` for that complete explicit oracle. `npm run test:rebuild` chains both before the client/adaptor checks. **PROGRAM P9 receipt, 2026-08-23, pre-change HEAD `221d7811`:** the actual runner first discovered 939 tests, including exactly the six ferry facts. After the split and three gate-composition facts, runner discovery proved **942 = 936 default + 6 sweep**, intersection zero, with the default-minus-all and explicit-sweep sets both exactly those six facts. The gate guard was RED 0/3 before script registration and GREEN 3/3 after. The explicit command passed **6/6** over the unchanged **20 perturbations × 2 arms = 40 runs**; VSTest reported **6 m 38 s**, while fleet-loaded wall time was **67 m 39 s**. Do not compare that wall time with the historical idle suite: an owned pre-change full run was terminated at **112.6 m**, with only harness startup in its log and CPU samples of 449–521%, and classified `OVERLOADED_INVALID_NO_COUNT` because eight sibling lanes and campaign replays made it 4.07× the prior timing. No post-split full timing is claimed until a comparable idle window. The last comparable full-suite measurement remains 2026-08-21: **862 passed / 1 failed / 863 total**, **27 m 40 s**; that chain tick-pin failure was subsequently resolved and its class filter passed 5/5 (see `developer_state.json` → `_TICK_BISECT_RESOLVED_20260821`) |
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
