# Driving Onslaught Toolkit headlessly

- **Status:** live contract for the headless adapter.
- **Evidence:** MEASURED — every envelope and exit code below was produced by running the
  command against this build on 2026-08-01 and pasting its output back in. The
  "what is not here" list was produced by enumerating the verb tree against the GUI's
  pages, not from recollection. The `lore` verbs joined on 2026-08-23 and the `media`
  verbs joined the same day; their envelopes and exit codes below were produced the
  same way, against this build.
- **Last updated:** 2026-08-23
- **Summary:** the envelope, the exit codes, the whole verb surface, and one session
  that works start to finish.

`OnslaughtCareerEditor.Cli` is a maintainer/agent adapter over the same AppCore services
the WinUI app calls. It is not a second product lane and is not shipped in the release
ZIP — it exists so that anything the GUI can do can also be done, scripted, and asserted
on by something that is not a person sitting at the machine.

```bash
dotnet run --project ./OnslaughtCareerEditor.Cli/OnslaughtCareerEditor.Cli.csproj -- --help
```

## The envelope

Pass `--json` to any verb and stdout becomes exactly one JSON document and nothing else.
No banner, no progress, no warning text — a caller parsing stdout never has to skip
anything.

```json
{
  "ok": true,
  "command": "version",
  "exitCode": 0,
  "warnings": [],
  "data": {
    "version": "1.0.0.0",
    "usingFallbackPatchCatalog": false,
    "safeCopyProfileCatalogVersion": "safe-copy-profiles.v1",
    "safeCopyRoot": "…\\OnslaughtCareerEditor\\GameProfiles",
    "patchBenchRoot": "…\\OnslaughtCareerEditor\\PatchBench"
  }
}
```

A refusal has the same shape with `error` in place of `data`:

```json
{
  "ok": false,
  "command": "copy.delete",
  "exitCode": 1,
  "warnings": [],
  "error": {
    "kind": "usage",
    "message": "Safe copy not found: …\\GameProfiles\\nope",
    "details": []
  }
}
```

`command` is the dotted verb path, so a caller can route on it. `warnings` collects
non-fatal caveats that would otherwise go to stderr — in JSON mode they are inside the
document, because a warning printed outside it is invisible to the caller who most needs
it. `error.kind` mirrors the exit code, so reading only the JSON is enough.

## Exit codes

Three, and the distinction between 1 and 2 is the useful one.

| Code | Meaning | `error.kind` |
|---|---|---|
| 0 | It worked. | — |
| 1 | The invocation was wrong, or a guard refused. Nothing was attempted. | `usage` |
| 2 | It ran, and the answer is no. | `data` |

Verified just now against this build:

```
version           -> 0     it worked
copy delete nope  -> 1     no such copy; nothing was attempted
trainer read      -> 2     ran fine, no mission running, so nothing to read
config detect     -> 0     found an installation
```

**2 is not failure.** `trainer read` with no game running, `saves analyze` on a file that
is not a save, and `patch verify` on bytes that do not match are all working commands
returning a verdict. A caller that treats non-zero as broken will retry things that are
already answered.

## The verbs

| Group | Verbs |
|---|---|
| `config` | `show`, `set-game-dir <path>`, `detect` |
| `saves` | `list`, `analyze <file>`, `compare <l> <r>`, `patch <in> <out>` |
| `goodies` | `list <file>`, `set <in> <out>` |
| `options` | `show <file>`, `edit <in> <out>` |
| `copy` | `list`, `create`, `launch <id>`, `stop <id>`, `saves [id]`, `rescue <id>`, `delete <id>` |
| `patch` | `list`, `stage <src>`, `plan <t>`, `verify <t>`, `apply <t> <ids>`, `restore <t>` |
| `patch install` | `status`, `backup`, `apply --yes`, `restore` |
| `process` | `list`, `stop <pid>` |
| `trainer` | `status`, `read`, `set`, `hold`, `music` |
| `lore` | `search <query>`, `show <document>` |
| `media` | `list [audio\|video]` |

`lore` reads the packaged Lore library — the same
[`LoreBrowserService`](OnslaughtCareerEditor.AppCore/LoreBrowserService.cs) +
`LoreSearchService` pair the GUI reader uses, with nothing written anywhere. By default
the library is the one discovered from the tool's own location (the repository's tracked
corpus in a dev checkout); pass `--root <dir>` to point at a folder containing `lore/`,
`lore-book/`, or a `lore-pack`. Search is whole-word and returns snippets in index
document order; an empty result set is exit 0 with `hitCount: 0`, not an error.
`lore show` resolves only members of the loaded index: an indexed absolute key, an indexed
relative/display key, or a `lore-pack://` key when a pack is present. A filesystem path
that merely exists but is absent from that index is not read; it returns exit 2 like any
other key that names no indexed document.

Measured against this build:

```
lore search aquila --json        -> 0     17 documents searched, 29 hits, ordered snippets
lore show lore/characters.md     -> 0     159 text lines: title, 7-entry outline, body; stderr empty
lore show lore/no-such-doc.md    -> 2     ran fine; that key names no indexed document
lore search                      -> 1     usage error: "A search query is required."
```

`media list` reads the game's audio/video catalog — the same
[`MediaCatalogService`](OnslaughtCareerEditor.AppCore/MediaCatalogService.cs) snapshot the
GUI Media page draws, with mission names joined from the game's own language file and
voice-line transcripts from its text table. Nothing is written anywhere and no audio or
video bytes are ever emitted. The game folder resolves the way `saves list` resolves it:
the configured game directory, then auto-detection; pass `--game-dir <dir>` to override
for one invocation. A directory that is not an installation (no `BEA.exe` + `data`) is
exit 2, a verdict about the data rather than a bad call.

Measured against this build:

```
media list --game-dir <dir> --json   -> 0     both sections: counts, groups, transcripts
media list audio --game-dir <dir> --json
                                     -> 0     the audio section only, video absent
media list --game-dir <dir>          -> 0     text mode: grouped banner, no paths printed
media list --game-dir ./empty        -> 2     ran fine; that directory is not an installation
```

In JSON each item carries its name, group/section, sort order, duration label, game-relative
file label, and transcript when the game's text table carries one — never an absolute path.
Text output is a quiet grouped listing that names media, not file locations.

```json
{
  "audioCount": 3,
  "audio": [
    {
      "name": "512_TATIANA_NEW_1",
      "groupName": "Mission 512",
      "groupSortOrder": 512,
      "durationLabel": "",
      "file": "data/sounds/english/MessageBox/512_TATIANA_NEW_1.ogg",
      "transcript": "Hawk, Billy! What are you two doing?"
    }
  ]
}
```

Two roots exist and are never the same place: `copy` works under `GameProfiles`, whole
playable game folders; `patch` works under `PatchBench`, `BEA.exe`-only working copies.

`patch install` is the one group that touches the game you actually installed. It cannot
write until `AuthorizeInstalledGameWrite` has put a verified `BEA.exe.original.backup`
and its `.sha256` beside the target — so the backup is a precondition of the call
succeeding, not a step a caller has to remember.

## A session that works

Copy-paste, in order. Roughly seven seconds for the copy on a 0.65 GB install.

```bash
CLI="dotnet run --project ./OnslaughtCareerEditor.Cli/OnslaughtCareerEditor.Cli.csproj --"

$CLI config detect --json                       # find the installation
$CLI copy create --name agent-demo --json       # a playable copy, patched windowed
$CLI copy list --json                           # id, size, careers inside, running
$CLI copy launch agent-demo --json              # start it, register the lease
$CLI trainer status --json                      # is it attachable yet
$CLI trainer read --json                        # exit 2 until a mission is running
$CLI trainer hold --life 100 --for 30 --json    # a single write is overwritten in a blink
$CLI copy stop agent-demo --json
$CLI copy saves agent-demo --json               # what a delete would take with it
$CLI copy delete agent-demo --force --keep-saves-in ./kept --json
```

The last line is the shape worth copying: `--force` agrees to remove several gigabytes of
copied game files, and it is deliberately *not* an answer to "and lose the careers played
inside it". Those are separate questions, so `copy delete` refuses while careers are
present unless told either `--keep-saves-in <dir>` or `--discard-saves`.

## What is not here

The GUI can do these and the CLI cannot, as of 2026-08-23. Listed because a gap nobody
wrote down is a gap nobody closes:

- **Cheats** — composing a cheat-named save copy. No verb.
- **Trainer hotkeys and music playback** — `trainer music --out <file>` renders the tune
  to disk; playing it is the app's job.

## Rules that bind a headless caller

- The pristine specimen (`74154bfa…`) is read, never written. It is the measurement
  baseline for every byte finding in this repository.
- Career saves are never destroyed as a side effect. `copy delete` enforces this and so
  must anything built on top.
- Never synthesize a `.bes`. Start from a real save and preserve length, reserved fields
  and unknown bytes.

Full contributor rules are in [`AGENTS.md`](AGENTS.md); the gates are in
[`VALIDATION.md`](VALIDATION.md) and [`package.json`](package.json).
