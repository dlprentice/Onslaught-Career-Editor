# Security And Private Data Reporting

Status: active disclosure guidance
Last updated: 2026-06-22

This project handles local game paths, copied executable profiles, save/options files, patch manifests, runtime evidence summaries, and future online-play research. Keep reports minimal and do not paste proprietary or private material into public issues, PR text, or app release docs.

## User Data Safety

Save and options editing writes to a separate output file and refuses in-place patching. Executable patching applies only to app-owned safe copies or technical BEA.exe-only copies; the installed Steam game folder and original `BEA.exe` stay read-only.

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

The MIT license in this repository applies only to original project code, docs, metadata, and public-safe tooling. Battle Engine Aquila, its trademarks, executable, media, manuals, save files, screenshots, extracted assets, and third-party runtime components are not licensed by this repository.

Contributors must use a legally obtained local copy of the game and must not submit proprietary game content.
