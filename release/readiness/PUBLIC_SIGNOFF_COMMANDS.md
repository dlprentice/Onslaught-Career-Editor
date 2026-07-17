# Public sign-off commands

Use only the commands that match the candidate. A source check does not publish
or authorize a release.

## Source and product

```powershell
npm run test:product
npm run test:cli
npm run test:docs
npm run test:safety
npm run test:notices
```

Add `npm run test:rebuild` only when the release claim or source candidate
includes rebuild changes. It is the broad non-native rebuild gate; native Godot
acceptance remains a separate check for engine setup, rendering, input, launch,
or clean-exit changes.

## Portable WinUI ZIP

```powershell
npm run release:winui-zip
```

This is the candidate-shape gate. It verifies the ignored local publish/ZIP,
generated canonical Lore pack, content exclusions, extracted launch, Home/Lore
navigation, and owned-process cleanup. It does not sign, install, upload, tag,
announce, or publish anything.

For a documentation-only change, `git diff --check` and `npm run test:docs` are
sufficient unless a release input, notice, payload boundary, or command above
also changed.
