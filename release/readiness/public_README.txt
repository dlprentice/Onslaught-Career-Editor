# Onslaught Toolkit Source Candidate

This directory is a curated, self-contained source candidate generated from the
public Onslaught Toolkit repository. It contains the active WinUI 3 toolkit,
shared correctness libraries, tests, selected public documentation and Lore,
and the GPL-licensed RE-informed rebuild foundation. It is not the complete
project-history checkout and it is not a downloadable app ZIP.

Check `EXPORT_PROVENANCE.json` for the source commit and allowlist identity. A
fresh candidate is intentionally a plain directory rather than a Git checkout.
Run the inventory command below before building so generated output cannot be
mistaken for source-package content.

## Included

- `OnslaughtCareerEditor.WinUI/`: primary Windows toolkit UI.
- `OnslaughtCareerEditor.AppCore/`: save, options, patch, media, catalog, and
  safe-copy correctness logic.
- `OnslaughtCareerEditor.Cli/`: supported C# analysis and patch-planning CLI.
- `rebuild/`: GPL-3.0-or-later, RE-informed original-code deterministic Core,
  tests, and headless replay verifier.
- `reverse-engineering/`, `roadmap/`, `lore/`, and `lore-book/`: selected
  public-safe reference material.

The package does not contain Battle Engine Aquila executables, game archives,
media, arbitrary saves/options, extracted assets, copied game profiles,
screenshots, raw debugger logs, full Ghidra databases, secrets, or build output.
Use a legally obtained local game installation for game-aware toolkit workflows.

## Prerequisites

- Windows 10 or 11 for the WinUI app and native UI tests.
- .NET 10 SDK for the toolkit, plus .NET 8 SDK/runtime for the rebuild.
- Node.js 24.x with npm `>=11.12 <12`.
- Python 3 through the Windows `py` launcher for package checks.

No `npm install` is required for the active WinUI/AppCore/rebuild path.

## Verify And Run

From this directory:

```powershell
npm run test:public-candidate-inventory
npm run test:public-allowlist
npm test
npm run dev
```

`npm test` builds WinUI and runs AppCore, WinUI, and rebuild tests. `npm run
dev` launches the WinUI toolkit. The inventory and allowlist commands are for a
fresh candidate; run both before build/test output is created. They intentionally
reject generated binaries rather than hiding them.

Run the deterministic rebuild directly with:

```powershell
npm run test:rebuild-core
npm run run:rebuild-headless -- --repeat 100
```

The rebuild requires no retail game payload. It is an early deterministic
vertical slice, not gameplay, visual, or rebuild parity and not a strict
clean-room implementation.

## Package Sign-Off

<!-- public-package-commands:start -->
```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:winui-notices
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:rebuild-core
```
<!-- public-package-commands:end -->

For a materialized candidate, the `test:public-allowlist` line above is the
pre-build boundary gate already shown under Verify And Run. Do not rerun it
against `bin/obj` output. Use a new candidate when payload cleanliness must be
re-proven; do not weaken or bypass the scan.

## Documentation

- [Current capabilities](CURRENT_CAPABILITIES.md)
- [Contributor guide](CONTRIBUTING.md)
- [Collaboration and review](COLLABORATION.md)
- [Security and content boundary](SECURITY.md)
- [Rebuild overview](rebuild/README.md)
- [Reverse-engineering index](reverse-engineering/RE-INDEX.md)
- [Roadmap index](roadmap/ROADMAP-INDEX.md)
- [Lore index](lore/_index.md)
- [Public sign-off commands](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md)
- [Release posture](README.RELEASE.md)

## Safety And License

Never patch the installed game or original `BEA.exe`. Executable mutation uses
copied targets and app-owned safe-copy roots. Online Host/Join, signing,
installer/MSIX/Store trust, retail-content redistribution, and parity claims
remain outside this candidate.

The toolkit source is MIT-licensed under [LICENSE](LICENSE). The `rebuild/`
subtree is separately GPL-3.0-or-later under [rebuild/LICENSE](rebuild/LICENSE).
Battle Engine Aquila and its proprietary content are not licensed by this
project.
