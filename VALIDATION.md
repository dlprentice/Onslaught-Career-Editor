# Validation

Status: active — the gate-selection table
Last updated: 2026-09-06 (Linux preparation checks and default Windows gate description).
The 2026-08-31 causal Blaster impact identity and ordered World-110
authored-start assignment composition produced a broad non-ferry Core receipt of
1,130 passed / 3 known failed / 1,133 total; PROGRAM P9 moved the forty-run
`Level100FerrySweepFixture` from the default Core command to an explicit sweep.
Runner discovery proves the post-split 942-test population is exactly the
disjoint union of 936 default tests and six ferry tests; the explicit command
passed all six over the unchanged twenty-perturbation, two-arm matrix. Timing
and overload-invalidity details are in the Rebuild Core row.
Header fields under [`DOCUMENTATION.md`](DOCUMENTATION.md).
Summary: choosing the smallest evidence that proves the contract you changed.
[`package.json`](package.json) owns the commands.

Validation is proportional to the contract changed. Root
[`package.json`](package.json) is the command authority; the commands below are
options, not a required sequence.

David selected a Godot companion for Linux and Windows on September 6, replacing
the WinUI development lane. The table still describes existing code and commands;
WinUI and portable-ZIP checks remain reference procedures for that retained source.
They are not queued companion acceptance work. The future Godot companion needs its
own implemented workflows and native platform validation after development resumes.

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
| Rebuild Core | `npm run test:rebuild-core` is the focused cross-host command and excludes only `Level100FerryLandingTests`; use `npm run test:rebuild-ferry-sweep` for that complete explicit oracle. The larger `npm run test:rebuild` aggregate additionally includes Windows-only Godot/capture gates and therefore runs only in the VM. **Current broad default receipt, 2026-08-31, at combined tip `c0e994ef` over causal Blaster commit `b8fca9ea`:** `dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --nologo --no-restore --filter 'FullyQualifiedName!~Level100FerryLandingTests' --logger 'console;verbosity=minimal'` measured **1,130 passed / 3 known failed / 1,133 total / 0 skipped**, **34 m 23 s**. The only failures in that dated run were the Linux-host Windows-message assertions `TapeFileWriteNew_RejectsExtendedNamespaceAliasInsideSuppliedKnownRoot`, `TapeFileWriteNew_RefusesUnsupportedDeviceNamespaceDestinations`, and `TapeFileWriteNew_EvaluatesResolvedIdentityOfExtendedAliasWithDotSegments`; the September 6 focused correction and result below close those failures without claiming a new broad run. The former `BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses` population mismatch now passes through exact internal round identity, and no assignment/start failure appeared. The 2026-08-30 **1,118/4/1,122** receipt remains historical. **PROGRAM P9 historical receipt, 2026-08-23, pre-change HEAD `221d7811`:** the actual runner first discovered 939 tests, including exactly the six ferry facts. After the split and three gate-composition facts, runner discovery proved **942 = 936 default + 6 sweep**, intersection zero, with the all-minus-default and explicit-sweep sets both exactly those six facts. The gate guard was RED 0/3 before script registration and GREEN 3/3 after. The explicit command passed **6/6** over the unchanged **20 perturbations × 2 arms = 40 runs**; VSTest reported **6 m 38 s**, while fleet-loaded wall time was **67 m 39 s**. Its pre-change 112.6 m overloaded run and the 2026-08-21 **862 passed / 1 failed / 863 total** run remain dated history, not current counts |
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
one WinUI solution build, selected AppCore contracts, UI tests excluding
`WinUIRuntime`/`LegacyWpf`, and CLI tests. It does not run native UI runtime,
rebuild, release packaging, Ghidra, private runtime probes, or historical
repository accounting.

New general check output belongs under ignored `local-data/test-runs/` or a
descriptive child of `local-data/`. Preserve existing coupled `.artifacts/` and
specimen-bound `local-lab/` evidence paths. Validation output is not release content
or proof of unrelated runtime behavior.

September 6 repository preparation used the existing focused checks: packet exporter
**21/21**, probe refuter **46/46**, probe author **43 checks with 17 falsifiable guards**,
and host-attestor unit tests **13/13**. The exporter tests use fake headless launchers;
no Ghidra project was opened. The probe author retained the three protected input hashes.
The attestor's help/diagnostic correction did not rerun full campaign verification.
Documentation and public-payload gates passed.

The three Linux namespace-message failures in the August 31 Core receipt were
reproduced on September 6. The tests now expect Linux's earlier absolute-path refusal
and retain their Windows-specific assertions; production `TapeFile` behavior is unchanged.
The complete affected class passed **22/22, zero skipped** using
`dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter FullyQualifiedName~HeadlessApplicationTests`.
Before/after TRX files are in `local-data/test-runs/preparation-20260906/`.
This focused result closes those three failures; it does not replace the dated broad
receipt or establish Windows/Godot runtime acceptance.

Do not add a new test during cleanup unless implementation behavior changed,
the regression is consequential, and no focused existing check covers it. Do
not fix unrelated failures discovered outside the changed contract.
