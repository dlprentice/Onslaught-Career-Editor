# Security And Private Data Reporting

Status: active disclosure guidance

Onslaught Toolkit handles save files, local game paths, copied executables, and
generated asset output. Reports should expose only what is needed to reproduce
the defect.

## Consequential safety contracts

- Save and options edits start from an existing file, preserve unknown bytes,
  stage a sibling output, replace atomically, and verify committed bytes.
- The installed game and original `BEA.exe` are read-only. AppCore patches only
  a verified technical copy or an app-created safe game copy, maintains a
  verified full-file backup, and stops only a process it launched and identified.
- AppCore rejects in-place, hardlink, reparse-routed, reserved-device,
  alternate-stream, network/device, wrong-type, and installed-game-tree output
  destinations.
- Generated catalogs use bundle-relative paths. Catalog readers reject rooted,
  escaping, reparse, hardlink, network, device, and game-tree declarations and
  verify source identities and hashes before reading.
- Export tools require an explicit output root separate from retail input and
  tracked source. They publish staged output rather than modifying input.
- The optional Godot developer toolchain is pinned by manifest and hashes. Its
  per-user cache is integrity-checked, not a sandbox against another process
  running as the same Windows user.

These contracts protect data and filesystem integrity. They do not establish
format completeness, patch gameplay effects, asset fidelity, or rebuild parity.

## Report privately

Use the maintainer channel provided with your collaboration invitation for:

- leaked secrets, credentials, private paths, or machine identifiers;
- unsafe mutation of an installed game, original executable, save, or options
  file;
- copied-profile patching that can escape its selected/app-owned root;
- launcher behavior that can stop a process it did not start;
- raw debugger/runtime captures, full Ghidra projects, or unreviewed bulk game
  payloads that should not be posted in a public issue.

In the first report, include the affected path and commit, the command or user
action, high-level reproduction steps, and the smallest redacted evidence. Do
not paste secrets, executable/save bytes, machine-local paths, or raw captures.

If no private channel has been arranged, open a public issue titled `Private
report needed` with a one-sentence category such as `possible unsafe patch
path`. Wait for a private route before adding sensitive detail.

## Public reports

Source-code bugs, documentation defects, redacted validation failures, feature
requests, and already-tracked evidence summaries are normally safe to discuss
publicly. Do not attach full local retail payloads.

## License and asset boundary

The root MIT license covers the toolkit code and documentation. `rebuild/` and
`references/Onslaught` are separately GPL-licensed; file-level and third-party
notices remain applicable.

Retail game files and converted copies remain user-supplied local inputs and
must not be committed, attached to reports, or included in packages. The
repository licenses grant no rights in the retail executable, game assets,
trademarks, or third-party components. The canonical reviewed Ghidra project,
pinned reference submodules, and narrow documented save fixture are explicit
repository exceptions with separate provenance and terms.
