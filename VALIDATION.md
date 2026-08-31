# Validation

Status: active — the gate-selection table
Last updated: 2026-08-31 (World-110 all-40 serialized seed admission raised
the broad non-ferry Core truth to 1,118 passed / 4 known failed / 1,122 total;
PROGRAM P9 moved the forty-run
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

Run host-appropriate gates. Omarchy is authoritative for documentation,
safety, reverse engineering, retail materialization, and the
Core/Client/headless rebuild. `npm test`, `npm run dev`, the full AppCore suite,
WinUI, CLI, the full `test:rebuild` aggregate, and controlled Godot
build/launch/smoke/capture require the isolated Windows VM after activation.
Linux static behavior is not native Windows or Godot evidence. Root scripts use
`python` and forward-slash paths; Windows-only commands also fail fast before
attempting their toolchain.
The 2026-08-30 Linux measurement of the otherwise buildable AppCore lane was
**1,575 passed / 26 failed / 1,601 total**; the failures depend on Windows path,
process, and media behavior, so the root full-suite command is guarded rather
than misreported as a Linux gate.

| Change | Focused evidence |
| --- | --- |
| Documentation or deletion only | `git diff --check`, `npm run test:docs`, and the affected generator/reference check |
| A new or edited tracked `.md` header | `npm run test:doc-headers`, which is also inside `test:docs`. The contract is [`DOCUMENTATION.md`](DOCUMENTATION.md); the backlog of pre-standard documents is `tools/doc_header_backlog.txt` and may only shrink |
| AppCore behavior | In the Windows VM, `npm run test:appcore`; a deliberately selected platform-neutral fixture may run directly on Linux, but is not the full gate |
| WinUI behavior or copy | In the Windows VM, `npm run test:ui` or the affected test fixture, then one real-app workflow smoke |
| Save, options, copied-target, or patch safety | On Linux, only a deliberately selected platform-neutral AppCore fixture; in the Windows VM, `npm run test:safe-copy` also covers the UI regression half |
| CLI | In the Windows VM, `npm run test:cli` and the relevant AppCore test |
| Lore inputs/reader | `npm run test:lore-pack` is portable; run the LoreBrowserService/AppCore fixture in the Windows VM unless that exact fixture has been demonstrated platform-neutral |
| Public payload/provenance boundary | `npm run test:safety` |
| Rebuild Core | `npm run test:rebuild-core` is the focused cross-host command and excludes only `Level100FerryLandingTests`; use `npm run test:rebuild-ferry-sweep` for that complete explicit oracle. The larger `npm run test:rebuild` aggregate additionally includes Windows-only Godot/capture gates and therefore runs only in the VM. **Current broad default receipt, 2026-08-30, after the World-110 all-40 serialized seed admission:** `dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --nologo --no-restore --filter 'FullyQualifiedName!~Level100FerryLandingTests' --logger 'console;verbosity=minimal'` measured **1,118 passed / 4 known failed / 1,122 total / 0 skipped**, **35 m 43 s**. Three failures are the known Linux-host Windows-message assertions `TapeFileWriteNew_RejectsExtendedNamespaceAliasInsideSuppliedKnownRoot`, `TapeFileWriteNew_RefusesUnsupportedDeviceNamespaceDestinations`, and `TapeFileWriteNew_EvaluatesResolvedIdentityOfExtendedAliasWithDotSegments`; the fourth is the pre-existing `BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses` observable mismatch (actual 81 against 109–117). **PROGRAM P9 historical receipt, 2026-08-23, pre-change HEAD `221d7811`:** the actual runner first discovered 939 tests, including exactly the six ferry facts. After the split and three gate-composition facts, runner discovery proved **942 = 936 default + 6 sweep**, intersection zero, with the all-minus-default and explicit-sweep sets both exactly those six facts. The gate guard was RED 0/3 before script registration and GREEN 3/3 after. The explicit command passed **6/6** over the unchanged **20 perturbations × 2 arms = 40 runs**; VSTest reported **6 m 38 s**, while fleet-loaded wall time was **67 m 39 s**. Its pre-change 112.6 m overloaded run and the 2026-08-21 **862 passed / 1 failed / 863 total** run remain dated history, not current counts |
| Rebuild client/adapters | `npm run test:rebuild-client` |
| Godot toolchain or native behavior | In the Windows VM, the matching `test:rebuild-*` command; native smoke only when native behavior changed. Linux Godot source/static work is not native runtime evidence |
| Frontend page drawing | In the Windows VM, `pwsh -NoLogo -NoProfile -File ./rebuild/tools/Capture-Frontend.ps1 -Plan mainmenu`, which scores the capture against the retail reference and returns `FAIL` on regression. The scorer's portable tests are only one subset of `npm run test:tools` |
| Portable ZIP inputs or layout | In the Windows VM, `npm run release:winui-zip` |
| Tip census claim in docs | Re-read `developer_state.json` → `current_re_authority`, require its literal READY/reducer/authority-receipt pins, and run the named full replay. Historical Gen10 and candidate Gen73 blocks are not current routing |
| Campaign ledger / generation TSVs | The externally pinned frozen bootstrap in `current_re_authority.verify`; a generation number, matching ledgers, self-derived pins, integrity-only success, or candidate reducer is not authority |
| Tracked evidence register or current authority pointer | `python ./tools/re_evidence_register_export.py --state developer_state.json --check-header-only` for the portable header gate; on the maintainer host, omit `--check-header-only` and use `--check` for literal-pinned full replay plus byte equality |
| C1 PE plate apply | Exact current pack path/bytes/SHA, entity/body identity, pristine-byte validation, and a field-scoped reducer. Independent normal/adversarial review is strongly advised for consequential changes but is not a fixed model matrix; see `reverse-engineering/REVIEW-PROTOCOL.md` |
| C2_BOUNDED_RUNTIME claim | Entity-scoped controlled runtime + can-fail refuter; refuse PE-only bulk C2 |
| Ghidra mutation | `reverse-engineering/ghidra/README.md` promotion gate + explicit operator authorization; default **not authorized** |

Rebuild commands materialize their exact retail inputs to ignored paths. On
Linux the root command selects canonical `local-lab/rebuild-godot`, but a fresh
materialization requires `-- --game-root "/absolute/game/root"`; Windows retains
Steam discovery. Run `npm run prepare:rebuild-assets` explicitly when only that
boundary changed.

Inside the Windows VM, `npm test` is the focused default handoff for
cross-cutting active-product work:
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
