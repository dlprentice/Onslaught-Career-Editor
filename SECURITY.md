# Security And Private Data Reporting

Status: active disclosure guidance
Last updated: 2026-07-11

This project handles local game paths, copied executable profiles, save/options files, patch manifests, runtime evidence summaries, and future online-play research. Keep reports minimal and do not paste proprietary or private material into public issues, PR text, or app release docs.

## User Data Safety

Save and options editing calculates its app-owned default path without creating directories and refuses in-place, hardlink, reparse-routed, reserved-device, wrong-type, device/network, alternate-stream, and installed-game-tree destinations. The guarded writer resolves DOS drive aliases to physical local paths, holds physical ancestor and source-file identities, stages and flushes a sibling file, atomically replaces the selected output, and verifies the staged and committed identities and bytes. Generated safe-copy control editing requires a capability minted after profile/manifest validation for the canonical app-owned `GameProfiles` root. Executable patching applies only to app-owned safe copies or technical BEA.exe-only copies; AppCore publishes backup, checksum, patched, and restored bytes through verified same-directory staging and can recover a damaged copied executable from a verified full-file backup. The installed Steam game folder and original `BEA.exe` stay read-only. Standalone Python patch scripts remain lab helpers and do not carry the AppCore atomic-publication guarantee.

Generated asset catalogs use one canonical `<bundle>/asset_catalog/catalog.json`
layout with bundle-root-relative paths. AppCore rejects game-tree, network,
device, alternate-stream, reparse, hardlink, rooted, and escaping declarations;
pins the catalog root, catalog, and source identities plus content hashes; and
reads or copies through held no-follow directory and file handles. First package
publication is assembled under a sibling staging root and moved into a vacant
final name only after its payload and sidecars are complete. Existing packages
are accepted only when payloads remain byte-identical, and every importer,
preview, scene, mesh, manifest, and sidecar output uses the same guarded atomic
writer. Failure cleanup does not traverse directory links. These boundaries
protect local filesystem integrity; they do not license or publish extracted
game assets.

Generated-asset tools apply the same boundary before AppCore consumes a
catalog. Python producers hold source inputs and publish flushed temporary
handles by identity. The C# AYA harness produces FBX/PNG bytes in memory, keeps
each final staged identity exclusively held against concurrent write/delete,
requires an exact generated tree, and publishes by copying from held handles
into native atomic replacements. Contested or identity-ambiguous staging
entries are left for inspection instead of being deleted by path. Multi-file
asset export remains a sequence of atomic files, not a batch transaction.
Empty writable output directories are protected by transient delete-on-close
entries installed while a strict no-write-share directory handle is held. This
prevents in-place reparse conversion during publication while preserving normal
child creation/rename behavior; the guard is released only after another held
entry keeps the directory nonempty.

The optional First Flight source client uses a fixed tracked Godot manifest,
exact archive/tree hashes, reparse-path rejection, a setup lock, and held
read-only file handles through restore/build/run. Its per-user developer cache
is integrity-hardened, not a sandbox: the project does not claim isolation from
another malicious process already running with the same Windows-user authority.

The optional local mesh workflow pins its repository root to the script
checkout, rejects network/device/reparse/hardlink paths, and confines output to
the ignored `local-lab/rebuild-godot/` workspace. Guarded copies hold a no-follow
single-link source identity against write/delete, stage and hash locally, then
verify the final identity, link count, size, and hash after atomic rename. This
closes avoidable path-reopen and unchecked-final-state gaps; it does not claim a
sandbox against a hostile process running as the same Windows user.
Bootstrap places both verified role files in one content-addressed generation
and publishes only the manifest atomically after both succeed. A failure between
role copies can leave an ignored unreferenced file, but cannot alter the active
manifest or its referenced generation.

New generated files are content-quarantined before their first write: they are
made POSIX-delete-pending, must have zero links while bytes are written and
flushed, and regain a name only after content is final. A hostile process under
the same Windows user can still copy or add a hardlink to already-final bytes in
the disposition-clear/commit window, just as it can immediately after a normal
publish. That alias makes commit fail but may retain the final bytes at the new
attacker-created path. The project does not claim confidentiality or namespace
containment against that same-user post-final-byte action; it does claim that
the operation will not write through a pre-existing source/game identity or
accept the added alias as a valid commit.

## What To Report Privately

Use the maintainer channel provided with your collaboration invitation for any
suspected issue involving:

- leaked secrets, tokens, credentials, unnecessary local user paths, or machine identifiers
- bundled or pasted Battle Engine Aquila executable bytes, media, manuals,
  saves, screenshots, frame captures, extracted assets, or raw runtime proof
- unsafe mutation of the installed Steam game folder or original `BEA.exe`
- copied-profile patching that can escape the app-owned safe-copy folder
- launcher/process-control behavior that can stop the wrong process
- future online-session, matchmaking, relay, invitation, identity, replay, or input-routing weaknesses

Do not include raw secrets, game binaries, saves, screenshots, frame dumps, or extracted assets in the first report. Include only the affected path, commit, command, high-level reproduction steps, and the smallest non-proprietary evidence needed to triage.

If no private channel has been arranged for you, do not improvise one in a
public thread. Open a public issue with only the title `Private report needed`
and a one-sentence category such as `possible asset leak` or `possible unsafe
patch path`. Do not include sensitive details until a maintainer provides a
private route.

## What Can Be Public

It is normally fine to discuss:

- source-code bugs in public-safe project code
- documentation wording issues that do not reveal private paths or assets
- failed local validation commands with private paths redacted
- feature requests for the WinUI app, patch catalog, or public-safe tooling
- compact historical proof summaries already tracked in this repo, as long as
  they do not include raw game/media/save payloads, secrets, raw captures, or
  full debugger/Ghidra databases

## License Boundary

The root MIT license applies only to original toolkit code, docs, metadata, and
public-safe tooling. `rebuild/` and the `references/Onslaught` submodule are
separately GPL-licensed; the root license does not relicense them. The active
rebuild is explicitly RE-informed. See `rebuild/PROVENANCE.md` for the source
and clean-room boundaries.

Battle Engine Aquila, its trademarks, executable, media, manuals, save files,
screenshots, extracted assets, and third-party runtime components are not
licensed by this repository.

Contributors must use a legally obtained local copy of the game and must not submit proprietary game content.
