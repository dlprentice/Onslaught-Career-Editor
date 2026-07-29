# The installed Battle Engine Aquila corpus has a complete aggregate map, but not atom-level semantics

Status: active reconnaissance baseline for one current live-installation snapshot
Date: 2026-07-28
Verdict: **The current installation has a complete aggregate census and full-file
SHA-256 pass for the snapshot identified below, plus structural surveys of its
major container, media, script, localization, executable, and configuration
families. The repository has deep, evidence-backed understanding of
saves/options, the executable, frontend, Aquila, and the Level 100 opening
slice, but it does not yet have atom-level semantic coverage of all 5,515
installed files. This document is the measured map from which that work must
proceed; it is not the unpublished per-file ledger and is not a claim that the
remaining semantics are solved.**
Evidence: MEASURED — read-only recursive enumeration of the requested
installation, logical-byte rollups, SHA-256 of all 5,515 files, a canonical
manifest digest, aggregate extension/naming-family analysis, bounded framing or
metadata probes across every AYA/Ogg/VID/localization file, and direct inspection
of current repository parsers, consumers, evidence documents, and tests. Corpus
measurements, measured repository state, source-backed ownership, and
inferences are distinguished below.

---

## Scope, specimen boundary, and safety

The retail tree surveyed here is:

`C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila`

The project tree against which it was cross-walked is:

`C:\Users\david\source\Onslaught-Career-Editor`

This was a reconnaissance pass, not a game modification pass.

- The installation was never written to.
- The game and helper executables were not launched.
- No retail assets, extracted payloads, raw logs, or binary dumps were added to
  the repository.
- Parsers operated in memory or emitted only console summaries.
- `ffprobe` was used read-only for Bink and Ogg metadata.
- The initial duplicate pass hashed every possible duplicate candidate. Final
  verification then SHA-256 hashed all 5,515 files.
- Repository coverage was judged from the current working tree. That tree
  already contains unrelated, pre-existing modifications, so current-worktree
  observations are not automatically claims about committed `HEAD`.

The requested folder is not a proven Steam-depot snapshot. It contains a
documented locally patched `BEA.exe`, the repo-designated unpatched baseline
backup beside it, generated options and hardware-diagnostic state, nine local
save files, and project-oriented proof artifacts. Measurements in this document
therefore describe the **current live tree**. They must not be promoted to “the
canonical Steam manifest” without a separate Steam-depot reconciliation.

The final full-file observation completed at
`2026-07-28T22:56:08-04:00` (`2026-07-29T02:56:08Z`). Its canonical manifest
digest is:

`3d8aa45fb6792b605b5a29915e4256c5d2afecede92aef6ce8780fea6a10212d`

That digest was computed over every file, sorted by relative path using ordinal
case-sensitive ordering, with one UTF-8-without-BOM row per file. Relative
paths use Windows `\` separators and have no leading `.\`:

```text
relative-path<TAB>byte-length<TAB>lowercase-sha256<LF>
```

The digest makes the measured snapshot distinguishable without publishing
local save names or a redistributable retail-file manifest.

The pass did not use a filesystem snapshot, so it is technically non-atomic.
A final recensus at `2026-07-28T23:11:59-04:00` still found
5,515 files, 133 directories, and 702,659,189 bytes, and the newest file
last-write time remained `2026-07-28T14:39:10.4211069Z`. No concurrent mutation
was observed. A future recensus should still run against a quiescent read-only
copy.

This report is the specimen-bounded narrative census for the measured
installation snapshot. It does not replace the installed files, the mechanical
hash census, or narrower format findings as primary evidence. The game-assets
index routes to it; the older
`reverse-engineering\game-assets\game-folder-analysis.md` remains historical
orientation.

### Evidence vocabulary used below

| Label | Meaning in this document |
| --- | --- |
| **Measured installed corpus** | Read directly from the current installed files or a complete corpus pass. |
| **Measured repository state** | A parser, consumer, document, test, or dirty-worktree condition was directly inspected. Its existence does not by itself establish retail behavior. |
| **Source-backed** | Established by the pinned GPL reference source; useful for ownership and intent, but not alone proof of released Steam behavior. |
| **Bounded** | Exact for named/hash-gated specimens or a selected reconstruction slice, not a general format-completeness claim. |
| **Inventory-only** | Framing, names, hashes, tags, sizes, or counts are known; payload semantics are not complete. |
| **Inferred** | A plausible interpretation of measurements that still needs static or controlled-runtime proof. |
| **Unknown** | Not established; the document states what remains to be done. |

## Executive shape of the installation

| Measurement | Exact result |
| --- | ---: |
| Files | 5,515 |
| Directories below the install root | 133 |
| Logical bytes | 702,659,189 |
| MiB, rounded | 670.11 |
| GiB, rounded | 0.654402 |
| Reparse points | 0 |
| Empty directories | 0 |
| Zero-byte files | 175 |
| Distinct file extensions | 24 |
| Distinct SHA-256 values in the final full-file pass | 5,096 |

`data` owns 5,464 files and 692,713,321 bytes: 99.08% of the files and
98.58% of the bytes. Video is the largest byte owner; Ogg audio is the largest
file-count owner; AYA is the central installed resource-container family.

The directory shape is:

```text
Battle Engine Aquila/
├── 12 root files: executables, codec DLLs, options, installer/config logs
├── data/
│   ├── 4 direct binary/raw tables
│   ├── language/                  6 localization tables
│   ├── MissionScripts/          95 numbered level trees + text/
│   ├── Music/                   10 Ogg tracks
│   ├── ParticleSets/             3 text particle-set files
│   ├── resources/
│   │   ├── 301 root AYA archives
│   │   ├── dxtntextures/       800 wrapped DDS textures
│   │   ├── meshes/             213 wrapped CMSH meshes
│   │   └── textures/            47 wrapped uncompressed DDS textures
│   ├── sounds/
│   │   ├── 5 localized XAP banks + sounds.sfx
│   │   └── 3,047 localized MessageBox Ogg files
│   ├── textures/                 1 loose TGA
│   └── video/                    6 root + 28 briefings + 32 cutscenes
├── Manuals/                     30 localized Word-export files/assets
└── savegames/                    9 local 10,004-byte saves
```

### Exact top-level ownership

| Owner | Direct shape | Recursive files | Recursive directories | Logical bytes |
| --- | --- | ---: | ---: | ---: |
| Install root | 3 directories + 12 files | 5,515 | 133 | 702,659,189 |
| `data` | 8 directories + 4 files | 5,464 | 119 | 692,713,321 |
| `Manuals` | 6 directories | 30 | 11 | 2,784,625 |
| `savegames` | 9 files | 9 | 0 | 90,036 |

### Exact `data` ownership

| Path | Direct shape | Recursive files | Recursive logical bytes |
| --- | --- | ---: | ---: |
| `data` loose files | 4 files | 4 | 190,092 |
| `data\language` | 6 files | 6 | 1,766,076 |
| `data\MissionScripts` | 1 file + 96 child directories | 960 | 1,477,863 |
| `data\Music` | 10 files | 10 | 38,822,467 |
| `data\ParticleSets` | 3 files | 3 | 717,361 |
| `data\resources` | 301 files + 3 child directories | 1,361 | 151,859,739 |
| `data\sounds` | 6 files + 5 language directories | 3,053 | 143,982,599 |
| `data\textures` | 1 file | 1 | 786,476 |
| `data\video` | 6 files + 2 child directories | 66 | 353,110,648 |

### Complete non-level directory census

The table below covers the install root and every directory except the 96
MissionScripts children. Those 95 numbered leaves and `text` are recorded in
the MissionScripts section. Together the two tables account for all 133
directories below the root.

| Directory | Direct dirs | Direct files | Direct bytes | Recursive dirs | Recursive files | Recursive bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `.` | 3 | 12 | 7,071,207 | 133 | 5,515 | 702,659,189 |
| `data` | 8 | 4 | 190,092 | 119 | 5,464 | 692,713,321 |
| `data\language` | 0 | 6 | 1,766,076 | 0 | 6 | 1,766,076 |
| `data\MissionScripts` | 96 | 1 | 5,075 | 96 | 960 | 1,477,863 |
| `data\Music` | 0 | 10 | 38,822,467 | 0 | 10 | 38,822,467 |
| `data\ParticleSets` | 0 | 3 | 717,361 | 0 | 3 | 717,361 |
| `data\resources` | 3 | 301 | 86,646,042 | 3 | 1,361 | 151,859,739 |
| `data\resources\dxtntextures` | 0 | 800 | 43,268,019 | 0 | 800 | 43,268,019 |
| `data\resources\meshes` | 0 | 213 | 16,734,865 | 0 | 213 | 16,734,865 |
| `data\resources\textures` | 0 | 47 | 5,210,813 | 0 | 47 | 5,210,813 |
| `data\sounds` | 5 | 6 | 27,846,461 | 10 | 3,053 | 143,982,599 |
| `data\sounds\english` | 1 | 0 | 0 | 1 | 619 | 21,677,154 |
| `data\sounds\english\MessageBox` | 0 | 619 | 21,677,154 | 0 | 619 | 21,677,154 |
| `data\sounds\french` | 1 | 0 | 0 | 1 | 607 | 21,378,761 |
| `data\sounds\french\MessageBox` | 0 | 607 | 21,378,761 | 0 | 607 | 21,378,761 |
| `data\sounds\german` | 1 | 0 | 0 | 1 | 607 | 25,001,119 |
| `data\sounds\german\MessageBox` | 0 | 607 | 25,001,119 | 0 | 607 | 25,001,119 |
| `data\sounds\italian` | 1 | 0 | 0 | 1 | 607 | 23,496,399 |
| `data\sounds\italian\MessageBox` | 0 | 607 | 23,496,399 | 0 | 607 | 23,496,399 |
| `data\sounds\spanish` | 1 | 0 | 0 | 1 | 607 | 24,582,705 |
| `data\sounds\spanish\MessageBox` | 0 | 607 | 24,582,705 | 0 | 607 | 24,582,705 |
| `data\textures` | 0 | 1 | 786,476 | 0 | 1 | 786,476 |
| `data\video` | 2 | 6 | 33,388,480 | 2 | 66 | 353,110,648 |
| `data\video\briefings` | 0 | 28 | 78,936,704 | 0 | 28 | 78,936,704 |
| `data\video\cutscenes` | 0 | 32 | 240,785,464 | 0 | 32 | 240,785,464 |
| `Manuals` | 6 | 0 | 0 | 11 | 30 | 2,784,625 |
| `Manuals\English` | 1 | 1 | 35,282 | 1 | 9 | 1,347,616 |
| `Manuals\English\English_files` | 0 | 8 | 1,312,334 | 0 | 8 | 1,312,334 |
| `Manuals\French` | 1 | 1 | 31,275 | 1 | 4 | 159,107 |
| `Manuals\French\French_files` | 0 | 3 | 127,832 | 0 | 3 | 127,832 |
| `Manuals\German` | 1 | 1 | 32,417 | 1 | 4 | 152,465 |
| `Manuals\German\German_files` | 0 | 3 | 120,048 | 0 | 3 | 120,048 |
| `Manuals\Italian` | 1 | 1 | 32,787 | 1 | 4 | 182,284 |
| `Manuals\Italian\Italian_files` | 0 | 3 | 149,497 | 0 | 3 | 149,497 |
| `Manuals\Spanish` | 1 | 1 | 31,211 | 1 | 4 | 166,478 |
| `Manuals\Spanish\Spanish_files` | 0 | 3 | 135,267 | 0 | 3 | 135,267 |
| `Manuals\Images` | 0 | 5 | 776,675 | 0 | 5 | 776,675 |
| `savegames` | 0 | 9 | 90,036 | 0 | 9 | 90,036 |

### Exact extension distribution

Extensions were case-folded for this table. There are no extensionless files.

| Extension | Files | Logical bytes | Principal owner |
| --- | ---: | ---: | --- |
| `.ogg` | 3,057 | 154,958,605 | Music and localized voice |
| `.aya` | 1,361 | 151,859,739 | Levels, goodies, textures, meshes |
| `.msl` | 733 | 890,726 | Mission source scripts |
| `.txt` | 132 | 103,114 | Mission support, card DB, runtime history |
| `.stf` | 96 | 506,089 | Text-symbol source and zero-byte files |
| `.vid` | 66 | 353,110,648 | Bink videos |
| `.jpg` | 11 | 278,039 | Manual assets |
| `.bes` | 9 | 90,036 | Local saves |
| `.dat` | 9 | 1,947,976 | Four distinct binary-format families |
| `.png` | 8 | 2,338,155 | Manual assets |
| `.xap` | 5 | 27,832,792 | Localized sound-effect sample banks |
| `.xml` | 5 | 1,847 | Word-export manual support |
| `.htm` | 5 | 162,972 | Localized manuals |
| `.dll` | 4 | 1,463,635 | Bink, Ogg, Vorbis, zlib |
| `.par` | 3 | 717,361 | Particle definitions |
| `.bea` | 2 | 20,008 | Options/save-envelope files |
| `.exe` | 2 | 2,543,616 | Game and message helper |
| `.backup` | 1 | 2,506,752 | Repo-baseline unpatched game executable |
| `.h` | 1 | 1,044 | Generated text-symbol header |
| `.log` | 1 | 514,086 | Legacy installer log |
| `.mso` | 1 | 3,612 | Word-edit metadata |
| `.raw` | 1 | 8,192 | Headerless-looking byte payload; HUD role is static/repo evidence |
| `.sfx` | 1 | 13,669 | Sound-effect catalog |
| `.tga` | 1 | 786,476 | Startup splash |

The extension is not a format guarantee. In particular:

- `.dat` spans localization, world headers, Battle Engine configurations, and
  the physics statement stream.
- `.aya` is an outer zlib-member wrapper whose inflated owner can be a level
  resource stream, DDS, or CMSH.
- `.bea` and `.bes` share the same 10,004-byte save/options envelope.
- The five nonempty `.stf` files are text, not binary.

### File-size shape

| Logical-size bucket | Files | Bytes |
| --- | ---: | ---: |
| 0 bytes | 175 | 0 |
| 1–63 bytes | 6 | 340 |
| 64–255 bytes | 253 | 38,937 |
| 256–1,023 bytes | 618 | 419,272 |
| 1,024–4,095 bytes | 372 | 724,901 |
| 4,096–16,383 bytes | 391 | 4,349,853 |
| 16,384–65,535 bytes | 2,962 | 106,273,930 |
| 65,536–262,143 bytes | 551 | 60,813,026 |
| 262,144–1,048,575 bytes | 56 | 29,247,564 |
| 1,048,576–4,194,303 bytes | 97 | 205,823,600 |
| 4,194,304–16,777,215 bytes | 31 | 222,393,242 |
| At least 16,777,216 bytes | 3 | 72,574,524 |

Nearest-rank percentiles give a median of 28,328 bytes, P90 of 83,261, P95 of
153,831, and P99 of 2,827,282. The largest file is
`data\video\cutscenes\01.vid` at
32,067,000 bytes. The next largest are `OpeningFMV.vid` at 20,306,776 and
`cutscenes\06.vid` at 20,200,748.

### Filesystem naming observations

| Measurement | Result |
| --- | ---: |
| Maximum relative-path length | 93 characters |
| Maximum filename-component length | 65 characters |
| Files whose relative path contains a space | 139 |
| Files whose relative path contains `%` | 761 |
| Files whose relative path contains parentheses | 857 |
| Files with uppercase extension spelling | 1 |
| Files with non-ASCII names | 0 |

The percent signs are predominantly flattened source-style texture paths. Mixed
case occurs in both directory and asset names; any Linux/case-sensitive tooling
must use the installed spelling rather than normalize paths.

### Exact duplicate-content shape

Complete length grouping produced 1,301 possible duplicate candidates.
SHA-256 hashing of all candidates found the groups below; the later full-file
hash pass reproduced the same 5,096 distinct-content result:

| Measurement | Result |
| --- | ---: |
| Exact duplicate groups | 196 |
| Files participating in duplicate groups | 615 |
| Nonzero duplicate groups | 195 |
| Files in nonzero duplicate groups | 440 |
| Redundant nonzero logical bytes beyond one retained copy | 1,684,284 |

Breakdown:

| Family | Duplicate groups | Participating files | Redundant bytes |
| --- | ---: | ---: | ---: |
| AYA | 9 | 20 | 772,860 |
| PNG | 1 | 2 | 666,200 |
| MSL | 172 | 389 | 220,601 |
| TXT | 11 | 25 | 14,557 |
| BEA + BES | 1 | 2 | 10,004 |
| STF | 1 | 2 | 62 |
| Zero-byte STF + TXT | 1 | 175 | 0 |

Notable exact identities include:

- a 666,200-byte English manual PNG duplicated in shared `Manuals\Images`;
- the level 411/412 imposter textures at 214,187 bytes each;
- four 68,327-byte reflection textures with one shared payload;
- the 123,417-byte `ca_mu_craft05` and `ca_mu_early_forces` AYA payloads;
- level 523/524 imposter textures at 89,015 bytes;
- level 856/858 imposter textures at 75,856 bytes;
- reused mission scripts;
- one current options file byte-identical to one local save.

There are no exact duplicate Ogg or Bink files.

The low 1.61 MiB nonzero redundancy is important: repeated naming and parallel
language/level organization do not mean the corpus is mostly duplicate data.

### Timestamp and local-state shape

Exactly 5,502 files share the 2026-01-26 UTC last-write-date cohort; their exact
times are not all identical. Thirteen files have later dates: the patched
executable, two options files, nine saves, and `setuphistory.txt`. Visible
later/local additions include the executable backup, proof options, proof/test
saves, populated saves, and machine-specific hardware diagnostics. A shared
date is a useful cohort measurement, not sufficient provenance by itself.

This separation gives the project three specimen classes:

1. the legacy installed-content cohort;
2. the repo-designated unpatched executable baseline retained beside the game;
3. current user/project/runtime state.

Future corpus ledgers must record that provenance per file instead of treating
the directory as one homogeneous retail artifact.

## Root executables, libraries, logs, and configuration

### Root file ledger

| File | Bytes | SHA-256 | Measured role/state |
| --- | ---: | --- | --- |
| `BEA.exe` | 2,506,752 | `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918` | Current documented four-site/28-byte local patch specimen |
| `BEA.exe.original.backup` | 2,506,752 | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` | Repo-designated unpatched executable baseline |
| `Message.exe` | 36,864 | `9985c14692093a56b2e59d9f5ab4605a15dec3b30579d3c5c8bed08325cc01b7` | Standalone message-box helper |
| `binkw32.dll` | 375,808 | `2d0ae23a6175dc7b635c402a5e7e9542e923c0d1c376a8c5ef876ca0d5959d23` | Bink codec library |
| `ogg.dll` | 49,152 | `308540dbd488f3bceca2dbadefe02cf29d10a27c4ac096bb3da053e3e0b923ea` | Ogg container library |
| `vorbis.dll` | 974,848 | `b4fa55cfe7547ade0a2d5b800ef085ce20cdd71f61898d2461ea61eb0241812b` | Vorbis decoder library |
| `zlib.dll` | 63,827 | `9929233274cd1c33395036717dda8da45d5a3a3c880a4aeff6deabac3407ecc2` | zlib 1.1.4-era library |
| `cardid.txt` | 18,524 | `9855bf65364050d13243acd346a5865ca92ca6843599067a617acf99fece064f` | GPU/driver compatibility rule database |
| `defaultoptions.bea` | 10,004 | `6ffcd7b639c236f329e0349a0b5fc1159c6900872171488570b7cbfa19397f04` | Current runtime options envelope |
| `proof_defaultoptions.bea` | 10,004 | `7f86551c118c1b5efedb7aa8c768c3442800a02774add1532096407b4cdbdba7` | Local proof/options specimen |
| `INSTALL.LOG` | 514,086 | `e13c84efe10e24e32a682cff9538748a87f7e75ff6d3bd1d9f7fb05299b12766` | Legacy Ghost Installer log |
| `setuphistory.txt` | 4,586 | `d1ce368be0e4c05ec92819554084c3c7eae576a9c8202520d8e3e3555ca224a8` | Current-machine graphics/audio diagnostic |

### `BEA.exe`

Both game executables are 32-bit x86 Windows GUI PE images with the same
PE/COFF `TimeDateStamp` value (2003-05-26T13:13:55Z), four sections, and no
ASLR, NX, relocation table, debug directory, overlay, embedded manifest, or
Authenticode signature. Their hashes and byte delta agree exactly with the
repository's specimen baseline:
the live executable is the known 28-byte patch, and the backup is its
repo-designated unpatched baseline. This does not independently establish a
Steam-depot hash.

The measured import surface includes:

- 112 `KERNEL32`, 37 `USER32`, 16 `GDI32`, 5 `ADVAPI32`, and 10 `WINMM`
  imports;
- DirectSound ordinal imports;
- `AVIStreamWrite`;
- 12 Bink APIs;
- zlib compression/decompression;
- 11 Ogg and 13 Vorbis APIs;
- version APIs;
- Direct3D 9 creation;
- DirectInput 8 creation.

`setuphistory.txt` prints “Direct3DCreate8” while the executable statically
imports Direct3D 9 and has no static Direct3D 8 import. The wording is therefore
inconsistent/stale-looking and cannot establish D3D8 use; this pass did not
exclude a dynamically loaded wrapper or recover the exact logging call path.

The PE resources contain:

- Select Device dialog 144, reached by the sole direct `DialogBoxParamA` xref
  found in this scan;
- used menu 141 and accelerator 113;
- Direct3D sample/about dialog 143;
- substantial Model Viewer 166, Cutscene Editor 167, and Cutscene Settings 171
  controls.

The reference source's `DEV_VERSION` gates and the missing retail command-line
switches make dialogs 143/166/167/171 likely development-resource residue, but
that classification is source-backed/inferred. Their indirect reachability was
not excluded. They are not demonstrated retail features.

Measured command-line literals include:

`-forcewindowed`, `-skipfmv`, `-nosound`, `-showdebugtrace`,
`-soundbuffers`, `-nomusic`, `-autoconfigtest`, `-landscape0`,
`-landscape1`, `-landscape2`, `-traceconsole`, `-dxtntextures`,
`-32bittextures`, `-res`, `-playabledemo`, `-findbadwater`, `-timeout`,
`-findgoodwater`, `-backbuffer2`, `-cardid`, `-level`,
`-defaultoptionsname`, `-e3`, `-getversion`, and `-testeur`.

The current per-function command-line analysis, against unpatched hash prefix
`74154bfa`, establishes statically and by runtime verification that unpatched
retail requires `-testeur` before `-forcewindowed`. The quick reference and the
function page's older bottom note are stale where they show `-forcewindowed`
alone. The current live executable has a separate documented force-windowed
patch, so commands for the patched and unpatched specimens must not be mixed.

The executable RE program is deep but not complete. The historical
6,411-function body pass covered 1,539,953 of the baseline image's 1,929,117
`.text` bytes (79.8268%). This pass did not recompute interval coverage for the
newer 7,555-row inventory, so current `.text` coverage is **UNKNOWN**. Neither
metric proves that every recovered function's semantics or every released
behavior is understood.

### `Message.exe`

Static inspection establishes a narrow protocol:

1. scan the command line for three tilde separators;
2. copy the first delimited field after the first separator as the caption;
3. copy the second field as the message text;
4. show a Win32 message box with those two strings and type `0x11000`.

A practical shape is therefore `<ignored>~caption~text~`. The helper uses fixed
400-byte buffers without bounds checks and silently returns unless all three
delimiters occur. It contains no resources, manifest, or debug data.

No literal or direct reference to `Message.exe` was found in the repo-baseline
unpatched `BEA.exe`. Whether another launcher invokes it, or whether it is
orphaned installer-era support, remains unknown.

### Codec/compression DLLs

| DLL | Measured detail | Repository coverage |
| --- | --- | --- |
| `binkw32.dll` | RAD 1.5v-era markers, 85 exports, retained PDB path | Role/import/pass-through known; no internal RE |
| `ogg.dll` | 44 exports | Role/import/pass-through known; no internal RE |
| `vorbis.dll` | 35 exports; Xiph.Org libVorbis I 20020717 marker | Role/import/pass-through known; no internal RE |
| `zlib.dll` | GNUWin32 zlib 1.1.4 markers, 68 exports | Used by AYA; internals not RE'd |

All four are unsigned and have no embedded manifest. The AppCore full-install
copy path treats them as required/pass-through dependencies. Copy support is
not semantic understanding or compatibility proof.

### `cardid.txt`

This is an ASCII, CRLF-delimited hardware compatibility database:

| Measurement | Result |
| --- | ---: |
| Lines | 721 |
| Active nonblank/noncomment lines | 567 |
| Comment lines | 10 |
| Blank lines | 144 |
| `Vendor` rows | 14 |
| `Device` rows | 189 |
| `Driver` rows | 33 |
| Case-folded `Tweak`-family rows | 300 |
| `TweakF` rows | 4 |
| `Opt` rows | 25 |
| `Version` rows | 1 |
| `*End` terminators | 1 |

Its header identifies a 26/5/3 Battle Engine Aquila version and notes ancestry
from a StarTopia/Mucky Foot database. Vendors include SiS, ATI, 3Dlabs, 3dfx,
Matrox, nVidia, PowerVR, S3, Intel, and a `Vendor:0000 Unknown` record. The 300
Tweak-family rows comprise 299 literal `Tweak` spellings and one `TWeak`
case variant.

The currently logged Intel adapter `8086:4688` is absent from the 2003 device
table.
Repository tooling can append/restore presets, and the parser's broad syntax is
known, but exact directive precedence, signed driver-range behavior, unknown
device fallback, and the runtime effect of every tweak remain incomplete.

### `INSTALL.LOG`

This is a legacy Ghost Installer record for an original
`C:\Program Files\Battle Engine Aquila` target and old Windows XP shortcut
locations. It contains 5,502 `CopyFiles` entries.

Reconciliation against the current tree found:

- every listed copied file present except one English manual `Thumbs.db`;
- a listed shared `Uninstall.exe` absent;
- 14 current extra paths: the installer log, the unpatched executable backup,
  two options files, runtime history, and nine saves; the listed `BEA.exe` path
  is present but its current bytes are locally patched;
- no `.bea` file in the installer copy list.

The last point supports runtime generation of `defaultoptions.bea`. The log is
useful provenance evidence, but it should not be treated as a modern Steam
depot manifest.

### `setuphistory.txt`

This is runtime diagnostic output, not a static game configuration contract. It
records the current machine's Intel adapter/driver, display modes,
depth/texture/multisample capability tests, selected HAL path, DirectSound
enumeration, caps, and voice count.

Its current-machine values must not be used as universal game defaults. No
tracked parser/schema consumer was found; the file remains potential runtime
evidence rather than an owned format. This specimen is a successful diagnostic
run ending with the selected sound method, 12 voices, and `Done`; it has no
fatal/crash tail.

## Saves and options

There are eleven files in the shared options/save envelope family: two `.bea`
files and nine `.bes` files. Every one is exactly 10,004 bytes and begins with
version word `0x4BD1`.

| Measurement | Result |
| --- | ---: |
| Envelope files | 11 |
| Distinct hashes | 10 |
| Options files | 2 |
| Save files | 9 |
| Saves exactly matching an options file | 1 |

The current `defaultoptions.bea` is byte-identical to one local test save and
has the same displayed timestamp second, although their high-resolution
last-write times differ by about one millisecond. That is an observed content
identity; no copy mechanism is inferred from it.

The current options decoder establishes 16 entries plus a tail beginning at
file offset `0x26BE`. Current `defaultoptions.bea` includes, among other values,
input scheme 1, language 0, sensitivity 12, mesh distance 70, LOD bias 0.3,
scale 2, table 40, 4:3 shape, MSAA 8, and landscape setting 2. The proof options
specimen differs in several graphics defaults.

This is the repository's strongest complete-file family:

- AppCore has bounded parsers and mutation planners;
- changes start from a real baseline;
- unknown bytes are preserved;
- career, goodies, options, and selected version/bounds/layout-preservation
  contracts are tested;
- synthesis from scratch is intentionally prohibited.

“Strongest” still does not mean every byte is named. The correct contract is
baseline-preserving mutation of demonstrated fields.

Local save names and payload contents are intentionally not reproduced here.
They are user/project state, not redistributable retail evidence.

## `data` root: four structurally distinct installed files

| File | Bytes | SHA-256 | Current understanding |
| --- | ---: | --- | --- |
| `battle engine configurations.dat` | 1,514 | `58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a` | Six source-order Battle Engine profiles; no reusable round-trip parser |
| `default physics.dat` | 175,603 | `e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14` | Entire outer statement stream framed; many value semantics partial |
| `Dial.raw` | 8,192 | `2c57b657b92cd8bd73ca8c8986e8ce60aaffb065fdde09940053a2dd6d59671c` | Exact HUD input retained; full frame/palette format unknown |
| `worldheaders.dat` | 4,783 | `34f2f45027a165fedde0e306b61fbabf64332724ced1e7a763103248fea07524` | Byte-exact parser/re-encoder; four fields still unnamed |

These files must never be routed through one generic `.dat` parser.

### `worldheaders.dat`

The existing fail-closed parser consumes and reproduces the file byte-exactly:

- file version 1;
- 97 records;
- every record version 3;
- a world ID;
- a list of Battle Engine configuration names;
- four trailing integers whose semantics remain explicitly unknown.

Configuration-list distribution:

| Configuration list | Records |
| --- | ---: |
| Standard, Laser, Blaster | 30 |
| Standard, Sniper, Laser, Blaster | 23 |
| Empty | 15 |
| Standard | 10 |
| Racer | 5 |
| Laser | 4 |
| Aquila Prototype | 4 |
| Blaster | 3 |
| Blaster, Laser, Sniper, Standard | 1 |
| Paladin Prototype | 1 |
| Sniper | 1 |

The ordered `Blaster, Laser, Sniper, Standard` row belongs to world ID 0;
`Paladin Prototype` belongs to world ID 1.

The four trailing-field tuple has ten observed combinations. Naming those
fields without further source/static/runtime evidence would be speculation.

### `battle engine configurations.dat`

A source-order reader consumes all 1,514 bytes and finds six version-12
profiles:

| Profile | Life | Energy | `mGroundVelocity` | `mMaxAirVelocity` | Shield | Stealth | Primary weapon | Cockpit file |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Racer | 15 | 8 | 5.0 | 1.0 | 98 | 0 | Mech Twin Vulcan Cannon | `cockpit2.msh` |
| Standard | 25 | 8 | 5.0 | 0.9 | 98 | 0 | Pulse Cannon Pod | `cockpit2.msh` |
| Sniper | 25 | 8 | 5.0 | 0.9 | 90 | 80 | Rail Gun | `cockpit2b.msh` |
| Aquila Prototype | 20 | 8 | 5.0 | 0.9 | 98 | 0 | Pulse Cannon Pod | `cockpit2.msh` |
| Laser | 25 | 8 | 4.5 | 0.9 | 98 | 0 | Stream Laser Pod | `cockpit2b.msh` |
| Blaster | 25 | 8 | 4.5 | 0.9 | 98 | 0 | Pulse Cannon Pod | `cockpit2b.msh` |

Common measured values include `mGroundEnergyIncrease` 0.05,
`mMinTransformEnergy` 1, air turn speed 2, minimum air velocity 0.3, maximum
walk velocity 0.15, friction 0.7, and shared explosion identity
`BE Explosion`. Air-energy costs, secondary weapon/store arrays, cockpit
identities, language IDs, and other record fields are also present in the
source-order read.

Selected Aquila Prototype constants are embedded in deterministic Core code,
but the repository does not yet own:

- a standalone general parser;
- a byte-exact re-encoder;
- an unknown-field preservation model;
- complete runtime profile-selection semantics.

One `worldheaders.dat` record—world 001—names `Paladin Prototype`, but that
configuration is absent from the six records in this file. Whether it is
hard-coded elsewhere, an alternate/fallback profile, or intentionally
invalid/test content is unknown.

### `default physics.dat`

A full shallow framing pass consumes all 175,603 bytes:

| Statement family | Type ID | Statements |
| --- | ---: | ---: |
| Unit | 1 | 160 |
| Weapon | 2 | 139 |
| WeaponMode | 3 | 145 |
| Round | 4 | 91 |
| Spawner | 5 | 38 |
| Explosion | 6 | 118 |
| Component | 7 | 39 |
| Feature | 8 | 43 |
| Hazard | 9 | 4 |
| **Total** |  | **777** |

Additional exact shape:

- header value 18;
- 6,803 field/value nodes;
- 185 unique type/field pairs;
- 73,796 payload bytes;
- 3,912 four-byte nodes;
- 1,872 printable NUL-terminated string nodes containing 739 distinct strings;
- 639 string-node occurrences, 220 unique, cross-reference statement names;
- a terminating `-1`, with no trailing unconsumed bytes.

Unique observed identity counts are 54 Unit, 14 Weapon, 32 WeaponMode, 33 Round,
10 Spawner, 14 Explosion, 20 Component, 5 Feature, and 3 Hazard IDs.

This proves complete **outer framing and census**, not complete value semantics.
Round, WeaponMode, Weapon, and Explosion have deeper existing RE. Unit,
Spawner, Component, Feature, Hazard, damage rules, and many value IDs still
need a schema/behavior ledger and focused evidence.

### `Dial.raw`

Measured shape:

- 8,192 bytes;
- no identified header;
- only byte values `0`, `2`, `4`, `5`, and `6`;
- exact retained hash in the rebuild;
- the released HUD path identifies frame zero as the compass north treatment.

Because 8,192 bytes also permits several plausible dimensions/encodings, size
alone does not prove a 64×64 16-bit texture or any other layout. The remaining
frames, palette/lookup behavior, orientation, and exact byte-sprite composition
are unknown. The current rebuild is an exact bounded consumer, not a general
RAW decoder.

## AYA: the central resource wrapper

### Complete outer-wrapper result

Every one of the 1,361 AYA files parses as repeated:

```text
u32 compressed_length
zlib_member[compressed_length]
```

No file failed this framing pass.

| Owner | Files | Zlib members | AYA file bytes | Zlib payload bytes | Inflated bytes | Inflated/file ratio | Inflated owner/magic |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Root resource archives | 301 | 485 | 86,646,042 | 86,644,102 | 231,846,299 | 2.676× | `LVLR`-family resource streams |
| `dxtntextures` | 800 | 951 | 43,268,019 | 43,264,215 | 232,320,792 | 5.369× | DDS |
| `meshes` | 213 | 222 | 16,734,865 | 16,733,977 | 44,175,802 | 2.640× | CMSH |
| `textures` | 47 | 67 | 5,210,813 | 5,210,545 | 28,750,036 | 5.517× | DDS |
| **Total** | **1,361** | **1,725** | **151,859,739** | **151,852,839** | **537,092,929** | **3.537×** | |

The 6,900-byte difference between AYA file bytes and zlib payload bytes is
exactly 1,725 four-byte member-length prefixes.

Member-count distribution:

| Members per AYA | Files |
| ---: | ---: |
| 1 | 1,115 |
| 2 | 180 |
| 3 | 25 |
| 4 | 30 |
| 5 | 11 |

There are 364 full 1 MiB inflated members. This is evidence of the wrapper's
chunking behavior, not a semantic boundary.

### Root archive families

The 301 root archives divide exactly into:

- 66 numeric `NNN_res_PC.aya` level archives;
- 232 contiguous `goodie_0_res_PC.aya` through
  `goodie_231_res_PC.aya`, with no gap;
- `base_res_PC.aya`;
- `Frontend_res_PC.aya`;
- `Loading_res_PC.aya`.

The bounded top-level chunk walk found 23,884 chunks:

| Tag | Count | Current status |
| --- | ---: | --- |
| `TEXT` | 18,857 | Named/inventoried; payload semantics incomplete |
| `MESH` | 3,492 | Named/inventoried; selected bodies can be carved/exported |
| `AYAD` | 301 | Structural vocabulary |
| `LVLR` | 301 | Root resource owner |
| `TARG` | 301 | Structural vocabulary |
| `GDIE` | 232 | Goodie archive owner; selected fields cross-walked |
| `ERES` | 66 | Numeric-level vocabulary |
| `IMPS` | 66 | Numeric-level vocabulary |
| `LNDS` | 66 | Numeric-level vocabulary |
| `SSHD` | 66 | Numeric-level vocabulary; Level 100 deeply parsed |
| `SURF` | 66 | Numeric-level vocabulary |
| `WRES` | 66 | Numeric-level vocabulary; Level 100 deeply parsed |
| `DMKR` | 1 | Level 100 bounded schema/consumer |
| `PLAT` | 1 | Inventory/specialized evidence |
| `PMIB` | 1 | Inventory/specialized evidence |
| `VSDS` | 1 | Inventory/specialized evidence |

Tag recognition is not payload-schema completeness. The repository's newer
static contract correctly treats this as vocabulary. Any older heading that
calls it a “complete tag catalog” must not be read as “every payload field is
understood.”

The 232 Goodie archives each contain the four outer chunks `LVLR`, `TARG`,
`AYAD`, and `GDIE`. Their filename indices align with the save Goodies slots;
slot 232 maps to cutscene 33 without a corresponding archive. Structure and
save-state ownership are strong, while controlled runtime proof is still narrow.

### Wrapped DXT textures

All 800 `dxtntextures` files inflate to DDS-marked payloads whose bounded header
walk recovered dimensions, pixel format/FourCC, and mip-count fields without an
error:

| Actual DDS FourCC | Files |
| --- | ---: |
| DXT2 | 588 |
| DXT1 | 212 |

Most common dimensions:

| Dimensions | Files |
| --- | ---: |
| 512×512 | 206 |
| 1024×1024 | 152 |
| 128×128 | 143 |
| 64×64 | 101 |
| 256×256 | 84 |
| 32×32 | 35 |
| 1024×512 | 19 |

Mip-count field distribution:

| Mip count | Files |
| ---: | ---: |
| 0 | 547 |
| 10 | 105 |
| 9 | 57 |
| 8 | 39 |
| 7 | 32 |
| 6 | 14 |
| 11 | 4 |
| 5 | 2 |

The filename's format-looking suffix is not the actual stored DDS format.
Examples from the complete corpus:

- 311 names ending in an `A8R8G8B8` source/create suffix store DXT2;
- all 242 common `A1R5G5B5`-suffixed wrapped textures store DXT2;
- 116 common `X8R8G8B8`-suffixed files store DXT1.

Names flatten source paths using `%`: 761 installed paths contain `%`, and 857
contain parentheses. The maximum filename component is 65 characters; 25
texture names hit that exact length and several visibly lose part of their
format-looking suffix. A source-tool filename cap is a strong **inference**, not
yet a proven runtime rule.

The current C# export harness attempts the full two-directory texture corpus.
The Godot runtime loader is intentionally narrower: selected DXT1, DXT2, and
RGBA envelopes with expected dimensions. Successful export means the bounded
extractor handled a specimen; it does not prove correct assignment, color,
lighting, alpha semantics, or rendered fidelity.

### Wrapped uncompressed textures

All 47 files in `resources\textures` inflate to DDS-marked uncompressed payloads
whose bounded headers were read without an error:

| Pixel-mask family | Files |
| --- | ---: |
| 16-bit A1R5G5B5-shaped masks | 38 |
| 32-bit A8R8G8B8-shaped masks | 9 |

Thirty-eight are level imposter textures; the other nine cover fonts and small
frontend/system/HUD assets. Several paired-level files are exact duplicates.

### Wrapped meshes

All 213 individually stored mesh AYA files inflate and pass the bounded
CMSH/chunk walk. The inflated corpus contains 5,494 observed chunks:

| Tag | Count |
| --- | ---: |
| `MESP` | 3,774 |
| `MSHT` | 887 |
| `BBOX` | 213 |
| `CMSH` | 213 |
| `CMST` | 213 |
| `CEMT` | 126 |
| `CAMD` | 61 |
| `PMS2` | 7 |

Names expose broad naming families—Battle Engines, vehicles, buildings,
characters/bosses, cockpits, vegetation, effects, and components—but filename
semantics are not a substitute for structural or runtime proof.

The repository owns a substantial bounded CMSH parser/export path with
fail-closed handling of hierarchy, references, materials, truncation, topology,
and unsupported bones. Embedded bodies carved from level archives remain
explicitly “candidate-only.” General animation, skinning, every topology, and a
full scene/dependency importer remain unsolved. The dedicated Aquila loader is
exact by design and explicitly not a general AYA/CMSH importer.

## MissionScripts

### Complete directory universe

There are 95 numeric level directories plus `MissionScripts\text`. Exact
numeric IDs:

```text
000, 001, 002, 003, 004, 005, 007, 008, 009, 010, 011, 012, 013, 018,
020, 021, 022, 023, 025, 026, 030, 100, 105, 110, 200, 201, 211, 212,
221, 222, 231, 232, 300, 301, 311, 312, 321, 322, 331, 332, 400, 411,
412, 421, 422, 431, 432, 500, 511, 512, 520, 521, 522, 523, 524, 530,
600, 611, 612, 621, 622, 700, 710, 720, 731, 732, 741, 742, 800, 850,
851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864,
865, 866, 888, 900, 901, 902, 903, 904, 905, 956, 958
```

Ninety directory names use lowercase `level`; five use capitalized `Level`:
010, 011, 020, 400, and 511. Exact case must be retained in any corpus ledger
or cross-platform tooling.

Counts by hundred band:

| Band | Directories |
| --- | ---: |
| 0xx | 21 |
| 1xx | 3 |
| 2xx | 8 |
| 3xx | 8 |
| 4xx | 7 |
| 5xx | 9 |
| 6xx | 5 |
| 7xx | 7 |
| 8xx | 19 |
| 9xx | 8 |

### Exact file and lexical shape

The 960-file tree consists of:

- 733 nonempty `.msl` scripts, including root `onsldef.msl`;
- 130 `.txt` files, 84 empty;
- 96 `.stf` files, 91 empty;
- one `textlist.h`.

The 733 MSL files contain:

| Measurement | Result |
| --- | ---: |
| Lines | 41,758 |
| Nonblank lines | 36,735 |
| Comment-only lines | 8,453 |
| CRLF files | 728 |
| LF-only files | 5 |
| Distinct case-folded basenames | 290 |
| Distinct content hashes | 516 |
| Duplicate-content groups | 172 |
| Files in duplicate-content groups | 389 |

Naming/role families include 41 `LevelScript.msl` files, 25
`LevelNNNscript.msl` files, `onsldef.msl`, and 666 entity/support scripts.

A lexical—not semantic—pass found:

- 991 `event("...")` declarations;
- 369 distinct event literals;
- 585 `init`, 233 `died`, 141 `started_dying`, and 134 `hit` declarations;
- 123 callable identifiers;
- 1,687 active `#include` directives across 713 scripts;
- 139 `#define` directives.

Sixteen active includes reference absent paths: eleven point to an
`extra2\jim\text.stf` family and five to an `alex\text.stf` family. They occur
across levels 512, 600, 741, 742, 888, and the 901–905 LapMonitor scripts.
Therefore the installed loose source tree is not self-contained for clean
recompilation.

That does **not** prove retail ignores the loose scripts. Runtime precedence
between loose MSL/source files and packed mission representation is still
unresolved. The repository has only one tightly controlled Level 100 compiled
command mutation as released-runtime proof; it has no general compiler,
interpreter, or repacker.

### Zero-byte and text-source findings

All 175 zero-byte files in the install are under MissionScripts:

- 91 `text.stf`;
- 64 `Global.txt`;
- 20 `English.txt`.

The five nonempty STF files begin with text-source markers; none is a binary STF
container. The older blanket description “STF is binary” is false for this
corpus.

`MissionScripts\text` contains six files:

- current `text.stf`;
- two “Copy” variants;
- `english.txt`;
- `global.txt`;
- `textlist.h`.

File content establishes that this is generated/demo-era residue rather than
merely suggestive naming:

- `Copy (2) of text.stf` has 2,537 defines and is an exact name/ID subset of
  current `text.stf`; the current file adds 34;
- `Copy of text.stf` has 2,446 shared names, no negative IDs, and every numeric
  ID differs from current, making it an older mapping state;
- `textlist.h` says it was automatically generated by `TextConvert.cpp` and
  contains only 16 sequential IDs;
- adjacent `global.txt` identifies an `Onslaught Demo` / `Cpt Zedd` state.

The exact build/date and whether retail ever reads the residue remain unknown.
Current `text.stf`, not the copied variants, is the table that bijects with the
installed localization IDs.

### Per-level direct file/byte census

This compact ledger covers every numbered MissionScripts directory:

```text
000=1/0       001=1/0       002=1/0       003=12/9491   004=4/1810
005=1/0       007=1/0       008=1/0       009=1/0       010=5/2042
011=1/0       012=1/0       013=1/0       018=1/0       020=8/3994
021=4/1696    022=13/13184  023=1/0       025=1/0       026=1/0
030=1/0       100=28/37524  105=1/0       110=16/13454
200=17/19443  201=16/18177  211=16/14351  212=16/14364
221=14/15728  222=15/16335  231=14/19935  232=15/20435
300=11/13728  301=1/0       311=16/16188  312=17/18822
321=16/17691  322=16/19215  331=7/8281    332=7/8278
400=19/24607  411=13/12956  412=13/13061  421=10/8732
422=10/9754   431=7/6456    432=8/7030
500=27/28599  511=12/8956   512=14/15148  520=1/62
521=16/25028  522=17/25449  523=13/10890  524=13/10900
530=18/20469  600=15/16360  611=17/18794  612=17/24329
621=11/8788   622=11/10245  700=11/9339   710=7/6838
720=12/12457  731=21/18567  732=22/21055  741=20/21471
742=22/23265  800=10/8007   850=8/5325    851=9/5337
852=7/2162    853=12/14207  854=6/2164    855=8/3896
856=4/4002    857=2/554     858=4/4002    859=6/7515
860=14/18209  861=9/5337    862=8/3896    863=14/18195
864=8/5326    865=12/14207  866=6/7515    888=6/1876
900=1/0       901=14/12802  902=14/12622  903=15/13212
904=14/12802  905=17/16357  956=4/4002    958=4/4002
```

Each value is `direct-file-count/direct-logical-bytes`.

The remaining MissionScripts child is
`text=6/521486`; unlike the numbered directories it contains the global text
symbol/source family described above.

## Cross-system world and level universe

The game does not have one single “level list.” At least five installed index
spaces overlap:

1. 95 loose MissionScripts directories;
2. 66 numeric level-resource AYA archives;
3. 97 world-header records;
4. 28 briefing videos;
5. career/goodie/cutscene indices.

The 66 numeric resource archives are:

```text
100, 110, 200, 201, 211, 212, 221, 222, 231, 232, 300, 311, 312, 321,
322, 331, 332, 400, 411, 412, 421, 422, 431, 432, 500, 511, 512, 521,
522, 523, 524, 600, 611, 612, 621, 622, 700, 710, 720, 731, 732, 741,
742, 800, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861,
862, 863, 864, 865, 866, 901, 902, 903, 904, 905
```

Every numeric resource ID has a same-number MissionScripts directory.
Twenty-nine script IDs have no numeric resource archive:

```text
000, 001, 002, 003, 004, 005, 007, 008, 009, 010, 011, 012, 013, 018,
020, 021, 022, 023, 025, 026, 030, 105, 301, 520, 530, 888, 900, 956,
958
```

The world-header set differs again:

- header record but no MissionScripts directory: 950, 951, 952, 960, 961;
- MissionScripts directory but no header record: 022, 956, 958;
- numeric resource archive but no header record: none.

The 31 header-record IDs with no numeric resource archive are:

```text
000, 001, 002, 003, 004, 005, 007, 008, 009, 010, 011, 012, 013, 018,
020, 021, 023, 025, 026, 030, 105, 301, 520, 530, 888, 900, 950, 951,
952, 960, 961
```

The measured ID-set relation is:

```text
numeric-resource IDs ⊂ world-header IDs
numeric-resource IDs ⊂ MissionScripts IDs
world-header IDs and MissionScripts IDs overlap,
but neither set contains the other
```

Shared IDs establish a numbering relationship, not runtime ownership. This pass
does not yet explain the exceptional IDs. Likely roles such as tutorial
source, alternate configuration, test map, frontend state, or unused content
must be proven per ID rather than guessed from number bands.

### Briefing and cutscene number spaces

Briefing video IDs:

```text
100, 110, 200, 211, 221, 231, 300, 311, 321, 331, 400, 411, 421, 431,
500, 511, 512, 521, 523, 600, 611, 621, 700, 710, 720, 731, 741, 800
```

All 28 are numeric resource IDs. They do not cover every campaign/variant
resource ID.

Cutscenes are numbered 01 through 31 plus 33. Number 32 is absent. Existing
Goodies work maps cutscene 33 to save slot 232, which explains why that terminal
slot can exist without `goodie_232_res_PC.aya`; the rest of the media/career
relationship still needs a complete mechanical crosswalk.

## Localization

### Complete DAT corpus result

All six files parse as version-3 language tables:

| Language table | Bytes | Nonempty text records | SHA-256 |
| --- | ---: | ---: | --- |
| `american.dat` | 279,819 | 2,103 | `f08695cc8a06b1060e0eb18ea4d8994492693704e022c329d6266901a3e1db1f` |
| `english.dat` | 279,933 | 2,103 | `789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a` |
| `french.dat` | 300,067 | 2,101 | `1151d60309dea484b303eaf269553fc7b883caa7232817f0d51654415239b328` |
| `german.dat` | 308,567 | 2,103 | `69d4f148ba412e721da5a2cfe55f8cbd4cc3f6eeb940f6a2258d400355866e68` |
| `italian.dat` | 303,027 | 2,103 | `6c3f83d1e690a34c7e38b2c6f77d1cdda46c664c4f2a584ae82540c1d7e015c7` |
| `spanish.dat` | 294,663 | 2,101 | `630d0d8cdeea6ecb79cdf6dca20ca8563c2a684cd44aa8ba51ae916d0de5c5c2` |

Every table has:

- little-endian 32-bit magic `0xFFFFFFBB` (disk bytes `BB FF FF FF`);
- version 3;
- 2,571 records;
- 2,571 unique IDs;
- the same ID ordering;
- 607 audio-bearing entries;
- 607 unique audio identifiers;
- identical ID-to-audio-identifier mappings across all six tables.

The mapping equality does not mean byte-identical serialization: American and
English have byte-identical audio pools; Italian and Spanish have another
byte-identical pool; French and German each use a distinct pool ordering.

American and English agree in 2,430 records and differ in 141. French uniquely
blanks `GOODIE_TEXT_66_WEAPONRY` and `GOODIE_TEXT_74_TITLE`; Spanish uniquely
blanks `TO_GO_BACK` and `TO_SCROLL`. The exact strings matter for localization
fidelity, but their full copyrighted corpus is not reproduced here.

### `text.stf` bijection and a current parser bug

Current `MissionScripts\text\text.stf` contains exactly:

- 2,571 `#define` rows;
- 2,571 unique names;
- 2,571 unique numeric IDs;
- 151 negative decimal IDs.

After signed-to-unsigned 32-bit normalization, the STF IDs biject exactly with
all 2,571 DAT IDs.

The current general decoder has a concrete correctness bug:

```python
_STF_DEFINE_RE = re.compile(r"^#define\s+(\S+)\s+(\d+)\s*$")
```

The unsigned-only expression silently omits all 151 negative STF definitions.
That is why the earlier mapping result was only 2,420 of 2,571. The general
corpus exporter inherits the bug. The rebuild materializer independently uses
`-?\d+` and normalizes signed IDs correctly.

This is an observed present-tool gap, not a hypothetical future concern. It
must be fixed and tested before the general localization exporter can claim a
complete name mapping.

### Language/audio crosswalk

French, German, Italian, and Spanish each have exactly 607 MessageBox Ogg stems,
case-fold matching the 607 audio identifiers in the DAT tables with no missing
or extra file. Exact-case behavior differs materially:

| Directory | Case-only mismatches among 607 referenced stems |
| --- | ---: |
| English | 607 |
| French | 0 |
| German | 0 |
| Italian | 12 |
| Spanish | 601 |

English has all 607 table-referenced stems plus 12 additional loose files:

```text
400_beach_held
720_half_2
health_critical_10
health_critical_20
health_critical_30
health_low_10
health_low_20
health_low_30
under_attack_10
under_attack_20
under_attack_30
under_attack_40
```

There is no separate American voice directory. Whether American table selection
intentionally shares English voice assets is highly likely but remains a
runtime/source ownership question until the selection path is cited.

The repository owns a robust general DAT-layout parser, but its STF-name corpus
export is incomplete until the signed-ID bug is fixed. Rebuild consumption is a
hash-pinned English subset. One current materializer comment/assertion says
`data\language` holds “exactly five” DAT sets even though six files are
installed. That filesystem claim is false; the nearby `NUM_LANGUAGES 5` and five
selector flags may still correctly describe a five-choice runtime UI if
American is a regional replacement for English. Filesystem cardinality does
not settle selector cardinality.

## Audio

### Ogg corpus

All 3,057 Ogg files begin with `OggS` and expose readable Vorbis identification
headers and terminal granule metadata. The pass did not decode every packet or
validate every page CRC. The complete metadata-duration pass found:

| Owner | Files | Bytes | Channels/rate | Duration |
| --- | ---: | ---: | --- | ---: |
| Music | 10 | 38,822,467 | Stereo, 44.1 kHz | 43.946 min |
| English MessageBox | 619 | 21,677,154 | Mono, 44.1 kHz | 32.827 min |
| French MessageBox | 607 | 21,378,761 | Mono, 44.1 kHz | 32.650 min |
| German MessageBox | 607 | 25,001,119 | Mono, 44.1 kHz | 36.254 min |
| Italian MessageBox | 607 | 23,496,399 | Mono, 44.1 kHz | 32.610 min |
| Spanish MessageBox | 607 | 24,582,705 | Mono, 44.1 kHz | 35.626 min |
| **Total** | **3,057** | **154,958,605** | | **3.565 h** |

Music nominal bitrate is about 128 kbit/s. Voice nominal bitrate is about
80 kbit/s. No two Ogg files are byte-identical.

AppCore catalogs music and English MessageBox Ogg files and can safely stage
music replacements into copied profiles. The rebuild retains the exact English
Level 100 subset plus selected music. It does not yet own the complete
mission/speaker/cue/state graph for all languages.

### XAP sample banks

The five localized banks are:

| Bank | Bank file bytes | Records | Approx. decoded duration | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| English | 5,396,113 | 164 | 4.070 min | `658c15e3bab844d65dd3c07c4ac880f16f741c0ea116f48c603449bbd4dda8b7` |
| French | 5,565,621 | 164 | 4.198 min | `6921596b5576e1883546f62a2928836c664e5a03a6f9fd334219f32e3c0b671c` |
| German | 5,631,771 | 164 | 4.248 min | `5fd87181b165ad0eebfde7f547e093c54bf3c3cb16878b255bb2e84c9013f99e` |
| Italian | 5,640,591 | 164 | 4.255 min | `be311012e0628b057e744b7951bdc93d699cc3fb1951edae1def15a950cd8063` |
| Spanish | 5,598,696 | 164 | 4.223 min | `e88c95536eb3299ed64529acab098a681d647df842336ba2e3db60cbc40a5dbf` |

Every bank begins `PCXP` and contains 164 `PSMP` records in the same name/order
space. Existing English-bank code establishes the high-nibble-first IMA-style
decode used by selected records. The decoded-duration estimates assume the
observed 44.1 kHz mono 16-bit target shape.

Cross-language comparison:

- 134 of 164 record payloads are byte-identical in all five banks;
- exactly 30 records differ;
- those 30 form the localized HUD voice group;
- all record names and positions align.

Name-family counts:

| Family | Records |
| --- | ---: |
| Impact | 38 |
| HUD | 30 |
| Weapons | 29 |
| Battle Engine | 26 |
| Vehicles | 17 |
| Atmospheres | 15 |
| Front End | 3 |
| `Hit1`–`Hit6` | 6 |

The current rebuild parser verifies and consumes the English bank and selected
records only. This pass establishes common framing across all five installed
banks, but a reusable five-bank decoder and semantic cue graph do not yet
exist.

### `sounds.sfx`

This is plain text, not a binary sample bank:

- SHA-256
  `7b8448d0038449062dbaba16e3205f45c6df1be5e9f580cd456aa67c7b31c96c`;
- file header version 103;
- 170 declared records, indices 0–169;
- 167 distinct descriptions;
- 164 distinct sample references across 170 occurrences;
- five source-named value fields per record: volume, falloff, pitch variance,
  looping, and language dependence;
- 55 records with comments.

Every one of the 164 unique sample references maps to one XAP record. Every XAP
record is referenced. Six sample references are reused twice.

This proves the catalog-to-bank relationship. Stuart's
`CEffect::LoadSFXFile` establishes the five field names above and the following
comment field for its source lineage. Runtime consumer/selection laws,
malformed-input outcomes, playback behavior, and a reusable byte-preserving
decoder remain open. Selected Level 100 rows have deeper ownership.

## Video

All 66 `.vid` files start with Bink magic and pass `ffprobe`:

| Owner | Files | Bytes | Duration |
| --- | ---: | ---: | ---: |
| `data\video` root | 6 | 33,388,480 | 3.77 min |
| `briefings` | 28 | 78,936,704 | 13.20 min |
| `cutscenes` | 32 | 240,785,464 | 15.38 min |
| **Total** | **66** | **353,110,648** | **32.358 min** |

Video-shape distribution:

| Video shape | Files |
| --- | ---: |
| 480×300 at 25 fps | 36 |
| 201×149 at 25 fps | 28 |
| 128×128 at 30 fps | 1 |
| 640×480 at 24 fps | 1 |

Every 201×149 file is a silent briefing. The cutscenes divide into:

- 23 files with five RDFT audio streams;
- 8 files with one RDFT audio stream;
- cutscene 02 with five DCT audio streams.

Five embedded audio streams strongly align with the five European language
lanes, but the language-to-stream ordering is still a hypothesis until proved
by decoding/selection behavior.

The six root videos are:

```text
FEBack128
gill_m_on_a_fork
LTLogo
OpeningFMV
TWIMTBP_GefFX_640x480_Audio
UsTheMovie
```

`FEBack128` and `gill_m_on_a_fork` are silent; the other four have one audio
stream. No Bink file is byte-identical to another.

The repository's manifest tool recursively hashes and classifies every `.vid`;
AppCore presents a media catalog; the rebuild decodes a bounded frontend/intro
selection. A manifest is not a decoder, several friendly catalog labels are
project-authored rather than installed-file evidence, and the current
reconstruction does not decode the Bink audio corpus.

## Particle systems

All three `.par` files are plain text beginning with the Lost Toys particle
editor signature and version 1.0:

| File | Bytes | Lines | Descriptors | Distinct leading keys/tokens | SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- |
| `Frontend.par` | 28,702 | 1,125 | 65 | 105 | `01a4c73d7cfc666b4a367736fabd1d91bf3459ed1c538b6ca77f70c069cf8bc6` |
| `MainSet.par` | 685,194 | 25,931 | 1,405 | 123 | `a51fe4419b55e1af132e31c6b3cd8133c937745d8f4ab691eb5a0d81017ded06` |
| `ModelViewer.par` | 3,465 | 130 | 9 | 64 | `32d85d1f0400f46a45078d49c695967cde60ed572053059fd6246227162115a9` |
| **Total** | **717,361** | **27,186** | **1,479** | | |

All declared descriptor counts match the parsed names, and all 1,479 names are
unique. Type distribution:

| Type | Descriptors |
| ---: | ---: |
| 1 | 405 |
| 2 | 338 |
| 4 | 40 |
| 5 | 97 |
| 6 | 258 |
| 7 | 77 |
| 8 | 100 |
| 9 | 14 |
| 10 | 46 |
| 11 | 13 |
| 12 | 24 |
| 13 | 67 |

This is a complete textual framing/name/type census, not a complete particle
simulation/render schema. A few `MainSet.par` Level 100 effects have static
notes. `Frontend.par` and `ModelViewer.par` are otherwise nearly untouched.

At the frozen survey base `6882e916`, a half-finished particle parser/resolver
and its tests were present only as recovery-tree edits. They were later
adjudicated as unconsumed scaffold and removed. Historical code must not be
reported as an active owner.

## Loose startup texture

`data\textures\splash.tga` is exactly:

- SHA-256
  `ede2de33fb12219bae679fa4f9167109c937c5c15283ae9a448d848c0c7e9a56`;
- uncompressed TGA image type 2;
- 512×512;
- 24 bits per pixel;
- 18-byte header;
- 786,432 bytes of pixel data;
- 26-byte `TRUEVISION-XFILE` trailer;
- 786,476 bytes total.

The rebuild has a bounded startup consumer for this exact asset. There is no
need for a broader loose-TGA family parser because this is the only installed
file in that directory, but startup timing, draw state, and video sequencing
still require retail-behavior evidence separately from successful decoding.

## Manuals

The manual tree has 30 files and 2,784,625 bytes:

| Owner | Files | Bytes |
| --- | ---: | ---: |
| English | 9 | 1,347,616 |
| French | 4 | 159,107 |
| German | 4 | 152,465 |
| Italian | 4 | 182,284 |
| Spanish | 4 | 166,478 |
| Shared `Images` | 5 | 776,675 |

Each language has one Word-export HTML manual. English also retains Office edit
metadata and extra images; the other languages have a smaller support folder.
The HTML pages contain only local references—no scripts, objects, or external
URLs.

| Manual | `href`/`src` references | H1–H6 tags | `p` tags |
| --- | ---: | ---: | ---: |
| English | 6 | 67 | 148 |
| French | 6 | 55 | 144 |
| German | 6 | 55 | 143 |
| Italian | 6 | 55 | 144 |
| Spanish | 6 | 54 | 149 |

These are lexical tag/attribute counts, not semantic-section counts. English,
German, and Italian each contain one empty paragraph tag. Each page also has
one CSS `background-image` reference excluded from the six `href`/`src` count,
so each has seven local resource references in total.

All visible display assets resolve. French, German, Italian, and Spanish each
reference a missing language-local `editdata.mso`, which is Office editing
metadata rather than a demonstrated display dependency. English resolves that
file and also duplicates one shared 666,200-byte PNG exactly.

The repository previously had only a dated directory description for Manuals.
It still has no semantic extraction, topic crosswalk, reusable owned link
checker, or use of the manuals as a systematic design/control/lore evidence
source. This pass performed only the bounded local-reference check above.

## Repository-relative coverage

### Shape of the current project corpus

Before adding this requested report, the Git index contained 1,577 tracked
paths at frozen base
`6882e916dbcb52b8f601208a8b51b5a2435a7040`:

| Top-level owner | Tracked paths |
| --- | ---: |
| `reverse-engineering` | 1,035 |
| `rebuild` | 169 |
| `tools` | 129 |
| WinUI, AppCore, CLI, and their tests | 184 |
| Other root/lore/release/support paths | 60 |

Dominant tracked extensions are 1,048 Markdown, 287 C#, 76 Python, 29 JSON,
28 Java, and 24 PowerShell files. This explains an important asymmetry: the
project has a large evidence/documentation surface, but a much smaller set of
general-purpose retail format consumers. These are dated survey counts, not a
live repository dashboard.

At survey time, relevant coverage-owning files were modified in the
pre-existing working tree,
including `package.json`, `reverse-engineering\RE-INDEX.md`,
`rebuild\README.md`, `rebuild\PROVENANCE.md`,
`rebuild\tools\materialize_retail_assets.py`, and the Level 100 README.
`rebuild\tools\materialize_retail_assets_tests.py` was then untracked, and the
particle owner/test files described below were deleted later. Counts labelled
“current materializer” describe that dated survey snapshot, not current
`HEAD`.

### Primary repository entry points inspected

| Path | Why it matters to this crosswalk |
| --- | --- |
| [reverse-engineering/RE-INDEX.md](reverse-engineering/RE-INDEX.md) | Evidence policy and front door to the executable/data RE corpus |
| [reverse-engineering/game-assets/_index.md](reverse-engineering/game-assets/_index.md) | Asset-format ownership and generated/local-boundary guidance |
| [reverse-engineering/game-assets/game-folder-analysis.md](reverse-engineering/game-assets/game-folder-analysis.md) | Older install census compared against this pass |
| [reverse-engineering/game-assets/aya-asset-format.md](reverse-engineering/game-assets/aya-asset-format.md) | AYA framing and historical tag knowledge |
| [reverse-engineering/game-assets/aya-resource-tag-family-static-contract.md](reverse-engineering/game-assets/aya-resource-tag-family-static-contract.md) | Newer boundary between tag vocabulary and payload schemas |
| [reverse-engineering/save-file/_index.md](reverse-engineering/save-file/_index.md) | Save/options layout, evidence, and mutation constraints |
| [tools/aya_archive_inventory.py](tools/aya_archive_inventory.py) | Fail-closed archive/member/chunk inventory |
| [tools/aya_corpus_chunk_inventory.py](tools/aya_corpus_chunk_inventory.py) | Corpus-level AYA framing/tag census |
| [tools/language_dat_decode.py](tools/language_dat_decode.py) | General localization parser, including the signed-STF bug found here |
| [tools/export_language_corpus.py](tools/export_language_corpus.py) | Six-table corpus exporter that inherits the STF mapping |
| [tools/worldheaders_decode.py](tools/worldheaders_decode.py) | Byte-exact world-header parser/re-encoder |
| [tools/BeaAssetExportHarness/Program.cs](tools/BeaAssetExportHarness/Program.cs) | Broad texture/mesh export harness over the reference extractor |
| [OnslaughtCareerEditor.AppCore/GameProfilePreflightService.cs](OnslaughtCareerEditor.AppCore/GameProfilePreflightService.cs) | Full-install detection and safe copied-profile materialization |
| [OnslaughtCareerEditor.AppCore/MediaCatalogService.cs](OnslaughtCareerEditor.AppCore/MediaCatalogService.cs) | Music, English voice, and video catalog surface |
| [rebuild/tools/materialize_retail_assets.py](rebuild/tools/materialize_retail_assets.py) | Exact ignored retail-input/output manifest for the bounded rebuild slice |
| [rebuild/README.md](rebuild/README.md) | Current opening-slice and validation boundary |
| [rebuild/PROVENANCE.md](rebuild/PROVENANCE.md) | Evidence/provenance ledger for reconstructed consumers |
| [rebuild/OnslaughtRebuild.Godot/Assets/Level100/README.md](rebuild/OnslaughtRebuild.Godot/Assets/Level100/README.md) | Deep Level 100 asset/schema/render boundary |
| [rebuild/OnslaughtRebuild.Godot/CuratedAyaTextureLoader.cs](rebuild/OnslaughtRebuild.Godot/CuratedAyaTextureLoader.cs) | Bounded runtime texture envelopes |
| [rebuild/OnslaughtRebuild.Godot/RetailAquilaWalkerAsset.cs](rebuild/OnslaughtRebuild.Godot/RetailAquilaWalkerAsset.cs) | Exact Aquila asset loader, explicitly not a general mesh importer |

### Coverage labels

| Coverage | Meaning |
| --- | --- |
| **Implemented** | Reusable parser/consumer with focused evidence; unknown fields may still remain. |
| **Bounded** | Exact, tested support for named/hash-gated specimens or a selected slice. |
| **Inventory** | Names, framing, tags, hashes, dimensions, or counts only. |
| **Absent** | No substantive owner beyond a dated description or pass-through copy. |

### Root-family crosswalk

| Installed family | Grade | Current owner and boundary |
| --- | --- | --- |
| `BEA.exe` | **Bounded** | Deep Ghidra corpus, binary findings, runtime labs, patch engine; specimen-specific and not semantic completeness |
| `Message.exe` | **Inventory** | Protocol recovered in this pass; invocation/reachability unproved |
| Codec DLLs | **Inventory** | Import/export/role and safe-copy owners; no internal compatibility RE |
| `.bea` / `.bes` | **Implemented** | AppCore baseline-preserving save/options services and focused tests |
| `cardid.txt` | **Bounded** | Syntax/preset tooling and startup purpose; complete grammar/effects missing |
| `setuphistory.txt` | **Inventory** | Current-machine diagnostic measured; no tracked parser/schema owner |
| `INSTALL.LOG` | **Inventory** | Installer provenance/negative evidence, not modeled manifest |
| `Manuals` | **Inventory** | This pass adds structural/link inventory; semantic use absent |
| Curated playable safe copy | **Implemented** | AppCore copies recursive `data`, game EXE, default options, four required DLLs, and optional card/save/app-ID inputs; it intentionally omits Message.exe, Manuals, logs, proof options, and the backup |

### `data` family crosswalk

| Installed family | Grade | Exact boundary |
| --- | --- | --- |
| Loose MSL/TXT/STF | **Bounded** | Lexical/source docs; no general compiler/interpreter/repacker or loose-selection proof |
| Root AYA archives | **Inventory** | Full wrapper/tag census; Level 100/base deep; other levels mostly structural |
| Goodie AYA | **Bounded** | 232 archive/index relation; runtime proof narrow |
| Wrapped textures | **Bounded** | Full wrapper/header observations and an export harness; curated runtime consumer only, with no corpus-wide render-fidelity claim |
| Individually stored/embedded CMSH | **Bounded** | Static meshes and selected hierarchy/materials; animation/skinning/general scene incomplete |
| `language\*.dat` | **Implemented** | All six DAT layouts parse; general STF-name export bug; rebuild English subset |
| MessageBox Ogg | **Inventory** | Framing/identification/granule metadata read; full decode and cue/speaker/mission graph missing |
| XAP | **Bounded** | English selected decode plus all-bank framing/alignment; general five-bank owner absent |
| `sounds.sfx` | **Bounded** | Complete catalog-bank relation and source-named value fields; runtime selection/playback and reusable decoder remain open |
| Music | **Bounded** | AppCore catalog/replacement plus selected rebuild tracks; complete state/crossfade graph missing |
| Video | **Bounded** | Tracked manifest owns path/family/size/SHA/magic; this snapshot adds ephemeral ffprobe metadata; selected frontend decode, but rebuild Bink-audio decoding/assignment is absent |
| Particle `.par` | **Inventory** | Full text/name/type census; current active parser absent; simulation/render semantics missing |
| `default physics.dat` | **Bounded** | All statements/nodes shallow-framed; many type/value laws incomplete |
| Battle Engine config DAT | **Inventory** | Six profiles read in source order; no reusable round trip |
| `worldheaders.dat` | **Implemented** | Byte-exact 97-record round trip; four fields unknown |
| `Dial.raw` | **Bounded** | Hash/size/frame-zero use; general layout unknown |
| `splash.tga` | **Bounded** | Single exact startup image |

### Exact current rebuild materializer boundary

The current materializer states its intended scope: known frontend, Level 100,
and Aquila inputs. A read-only count of its current input/planning tables
produced the following **non-additive** counts:

| Input/planning table | Count |
| --- | ---: |
| Direct assets | 147 |
| Frontend assets | 33 |
| Packed Level 100 script objects | 25 |
| MAPT sources | 5 |
| Water textures | 5 |
| Explicit mesh conversions | 3 |
| Sound rows | 44 |
| Unique sound output destinations | 41 |
| Intro-sequence clips | 3 |

Its output accounting is separate:

| Output group | Count |
| --- | ---: |
| Fixed outputs | 258 |
| Static-world outputs | 66 |
| **Total expected outputs** | **324** |

Direct-source composition includes:

- 82 `dxtntextures` AYA;
- 6 mesh AYA;
- 2 `resources\textures` AYA;
- 51 English MessageBox Ogg files;
- 1 music Ogg;
- 3 MissionScripts text files;
- 1 English DAT;
- `Dial.raw`.

Frontend adds 30 more DXT texture AYA, 2 resource textures, and 1 music file.

This is an exact and substantial reconstruction slice. It is not equivalent to
coverage of 5,515 retail files, 66 numeric worlds, all 232 Goodies, or the full
media/localization corpus.

### The Level 100 island

`100_res_PC.aya`, selected `base_res_PC.aya` content, Aquila, frontend, and
Level 100 scripts/audio have the deepest data-to-rebuild chain. Existing owners
cover selected:

- HFLD/CHFD/HFDT terrain;
- five MAPT levels;
- 4,096 MMAP rows;
- lighting;
- 30 static shadows;
- 1,481 pine marker stamps;
- WRES placements;
- sky/water/static meshes;
- Battle Engine geometry/textures;
- HUD composition;
- mission event/audio/text subsets.

This work remains bounded. Steep-slope behavior, terrain damage, full scene
population, all mission behavior, dynamic battleline interior, exact particle
rendering, and whole-scene parity are explicit gaps.

### What existing test code and documented gates are intended to prove

Direct inspection shows tests/contracts intended to cover:

- parser bounds and malformed input;
- candidate-only treatment of carved CMSH;
- AYA inventory/export accounting;
- bounded CMSH hierarchy/material/topology contracts;
- bounded materializer/cache inputs and output accounting;
- `worldheaders.dat` byte-exact round trip;
- deterministic Core/client/native smoke state when those gates are run;
- save/options preservation.

This research pass ran the documentation-header gate, not the product/rebuild
suite or native smoke. At the frozen survey point, package commands and some
referenced tests were modified or untracked. Test existence therefore did
**not** establish a current green run, and even a green run would not prove:

- successful semantic parse of every AYA payload;
- complete support for every mesh/texture variant;
- runtime use of loose MissionScripts;
- full media cue ownership;
- final visual parity;
- whole-directory understanding.

The native smoke has no screenshot parity machinery, and visual scoring can
correctly return `UNSCORED`. A green suite must not be cited as an atom-level
corpus-completeness result.

## Corrections to older folder documentation

The December 2025 `game-folder-analysis.md` is useful historical orientation,
but its “complete” wording and several values do not describe this live tree.

| Older statement | Current measured result |
| --- | --- |
| 97 MissionScripts directories | 96 children: 95 numbered levels + `text` |
| MissionScripts about 4.1 MB | 1,477,863 logical bytes |
| 29 briefing files | 28 |
| 33 cutscene files | 32; number 32 absent |
| Empty savegames directory | 9 current local saves |
| `OnslaughtException.txt` present | Absent |
| `steam_appid.txt` present | Absent |
| STF described as binary | 91 empty; 5 nonempty text-source STF files |
| Approximate 680/673 MB corpus figures | 702,659,189 exact bytes / 670.11 MiB rounded |

Some differences may reflect an earlier install or a different local state, not
simple author error. The correct action is to date/specimen-label each census,
not silently replace one timeless-looking number with another.

Additional authority conflicts found:

1. an older AYA page's “complete tag catalog” wording conflicts with the newer,
   correct statement that tags are vocabulary, not complete payload schemas;
2. one current materializer filesystem assertion says five while six DATs are
   installed; the possibly separate five-choice runtime selector remains
   unresolved;
3. the general language tool drops 151 signed STF IDs;
4. the current per-function command-line result proves the `-testeur` guard,
   while the quick reference and an older bottom note remain stale;
5. historical particle parser references conflicted with its later-adjudicated
   removal from the recovery tree;
6. executable claims can silently switch between patched and unpatched
   specimens unless the hash is named.

## What is now settled

This pass settles the following existence and shape claims for the current live
installation:

- a complete traversal accounted for all 5,515 files and 133 directories in
  aggregate, and full-file hashes are anchored by the canonical manifest digest;
- all 1,361 AYA files decompressed through repeated length-prefixed zlib framing
  without an error;
- all 847 wrapped texture payloads exposed bounded, readable DDS headers;
- all 213 individually stored mesh AYA payloads passed the bounded CMSH/chunk
  walk;
- all 3,057 Ogg files exposed readable Vorbis identification and granule
  metadata, from which duration/rate were measured;
- all 66 videos were recognized by ffprobe as Bink with measured
  resolution/rate/audio-stream metadata;
- all six language DATs share one 2,571-record ID order and 607 audio IDs;
- every language voice directory has been case-fold reconciled to the DAT audio
  names, with exact-case differences quantified;
- every XAP bank has the same 164-record name/order space;
- every SFX sample reference maps to an XAP record and vice versa;
- all particle files are text and all declared descriptors were counted;
- all 95 MissionScripts level trees and 66 numeric resource worlds are known;
- world-header, mission, resource, briefing, and cutscene ID differences are
  explicitly enumerated;
- the current executable patched/unpatched identities match the repo baseline;
- legacy last-write-date cohort versus current local state is distinguishable;
- the exact rebuild materializer slice at frozen base `6882e916` is quantified.

## What is not settled

The following remain load-bearing unknowns:

1. the field-level schema and behavior of most AYA payload tags outside the
   Level 100/base/frontend slice;
2. a complete dependency graph from every world/archive object to mesh,
   texture, script, physics, sound, localization, and video;
3. packed mission bytecode/object representation and the runtime precedence of
   packed versus loose source, plus exact case folding, path normalization,
   filename truncation/collision, and resource-search precedence;
4. complete semantics for all nine physics statement families and their value
   IDs;
5. round-trip ownership of Battle Engine configurations;
6. the `Paladin Prototype` world-header reference absent from the six profile
   records;
7. the four trailing world-header fields;
8. unnamed/unknown bytes and tail semantics in the otherwise strongly owned
   save/options envelope;
9. the complete `Dial.raw` frame/palette/layout;
10. runtime consumer, selection, malformed-input, and playback semantics for
    the source-named `sounds.sfx` fields;
11. the full particle simulation/render laws for all descriptor types;
12. animation, skinning, and unsupported CMSH topology;
13. Bink audio decoding and language-stream ordering;
14. the total audio/music/video selection and playback-state graph;
15. American-versus-English runtime policy;
16. exact modern-GPU `cardid` fallback and directive precedence;
17. reachability of embedded development dialogs;
18. whether/how anything invokes `Message.exe`;
19. a complete manual-to-control/lore/mechanics evidence crosswalk;
20. semantics of every recovered executable function and the remaining
    uncovered executable code/data.

## Atom-level research program

The next phase should be discrete and ledger-driven. “Understand everything”
must become countable contracts rather than a continuous confidence score.

### Phase 1 — immutable specimen ledger

Create an ignored local ledger with one row per installed **file**:

- exact relative path and case;
- provenance class;
- size;
- SHA-256;
- timestamps;
- extension;
- measured magic/owner;
- duplicate-group ID;
- parser result;
- linked project owner;
- evidence grade;
- unresolved questions.

Completion bar: 5,515 of 5,515 file rows populated, with no “unseen” file. A
separate directory view must reproduce all 133 directory rows and the aggregate
numbers in this document exactly.

### Phase 2 — AYA semantic coverage ledger

For every AYA member and root chunk, record:

- archive/member offsets and inflated ranges;
- tag tree;
- exact known schema fields;
- opaque byte ranges;
- references to other assets;
- accepted/rejected parser path;
- round-trip status;
- runtime/static/source evidence.

Completion bar: every observed tag instance classified as exact schema,
partial schema, opaque, unsupported, or external-extractor-only. No tag may be
called solved merely because its four-character name is known.

### Phase 3 — world graph

Mechanically join:

- 97 world headers;
- 95 loose mission directories;
- 66 numeric resource archives;
- compiled mission objects;
- 28 briefings;
- 32 cutscenes;
- six Battle Engine profiles;
- career/save progression;
- 232 Goodie archives plus slot 232;
- localization IDs and audio/video cues.

Completion bar: every exceptional/missing/variant ID has a demonstrated role or
an explicit UNKNOWN record with the cheapest test that would settle it.

### Phase 4 — mission language and VM

First fix the signed-STF parser gap. Then:

- resolve or provenance-label the 16 absent include targets;
- map every loose script/object to packed representation;
- recover instruction/operand schemas;
- build a disassembler before considering a compiler;
- prove loose/packed selection and precedence in copied-runtime tests;
- recover case folding, `%` path flattening, the apparent 65-character naming
  cap/collision behavior, and resource search order;
- preserve exact case and source encoding.

Completion bar: every packed mission object can be framed/disassembled without
unclassified bytes, and every source/packed relationship has an evidence grade.

### Phase 5 — standalone structured formats

Build bounded, fail-closed, round-trip-capable owners for:

- Battle Engine configurations;
- the remaining physics fields/families;
- `sounds.sfx`;
- all three particle sets;
- `Dial.raw`;
- remaining unnamed save/options bytes and tail semantics, while retaining the
  baseline-preserving/no-synthesis contract;
- unresolved world-header fields where evidence permits.

Completion bar: byte-exact re-encode for understood envelopes, explicit opaque
retention where semantics remain unknown, and focused tests for every
consequential field.

### Phase 6 — complete media/localization graph

- correct signed STF name handling;
- parse/decode all five XAP banks;
- map every SFX and Ogg cue to scripts/UI/actors;
- map all Bink streams and language selection;
- recover music state, transitions, and crossfades;
- map subtitles, speakers, mission events, Goodies, and videos;
- use decoded media only in ignored local overlays.

Completion bar: all 3,057 Ogg files, 164 shared XAP record identities, 820
physical XAP bank-record instances, 170 SFX rows, 66 Bink files, and 15,426
localization record instances have an owner or explicit unknown.

### Phase 7 — root and documentation residue

- prove `Message.exe` invocation or orphan status;
- inventory and compare every DLL export/version against expected ABI use;
- finish the `cardid` grammar and modern-card fallback;
- model runtime/install log event families;
- mine manuals as localized evidence while preserving copyright/provenance;
- adjudicate embedded development-resource reachability.

Completion bar: no root/manual file remains “role guessed from filename.”

### Phase 8 — rebuild expansion

Only widen reconstruction consumption after a family has:

1. a named retail specimen/hash;
2. a bounded schema;
3. explicit provenance;
4. a deterministic consumer boundary;
5. a focused falsifying test;
6. runtime or rendered evidence where parity is claimed.

The current Level 100/frontend/Aquila slice should remain exact and narrow while
new islands are promoted one demonstrated family at a time.

## Recommended first concrete expedition

The highest-leverage next expedition is the **cross-world AYA and mission
ledger**, not a second broad narrative survey. It should:

1. regenerate the ignored 5,515-row specimen census when the installation
   changes;
2. correct and test the 151 signed STF mappings;
3. run the archive/member/tag walker over all 1,361 AYA files;
4. join all 66 numeric worlds to their loose scripts, world headers, briefings,
   imposter textures, and configuration lists;
5. select one non-Level-100 world with a different tag/terrain/mission shape;
6. pair its constructive schema work with an independent read-only adversarial
   review;
7. promote only the smallest general parser improvements that survive that
   comparison.

That sequence advances the specimen map without broadening the rebuild on
unproved semantics.

## Measurement notes

- Observation environment: Windows, PowerShell 7.6.4, Python 3.14.2,
  ffprobe/FFmpeg 8.1.2, Git 2.55.0.windows.3, Node 24.18.0, npm 11.17.0.
- The filesystem census used literal-path recursive enumeration equivalent to
  `Get-ChildItem -LiteralPath <install> -Force -Recurse`; no glob supplied the
  corpus boundary.
- File counts include hidden files and use literal-path recursion.
- Directory counts exclude the install root itself.
- Sizes are logical file lengths, not filesystem allocation size.
- Extension grouping is case-insensitive.
- Hashes are SHA-256.
- Initial duplicate detection grouped exact lengths and hashed every repeated
  length group; final verification hashed every file.
- The snapshot digest uses ordinal case-sensitive relative-path order and the
  exact UTF-8 row format printed near the top. It intentionally excludes
  timestamps and file contents themselves; each content hash is included.
- AYA framing was checked without extracting retail payloads to tracked paths.
- DDS/CMSH ownership refers to inflated magic/structure, not filename suffix.
- Ogg duration comes from stream granule positions/identification metadata.
- Video duration, dimensions, frame rate, and stream codecs come from read-only
  `ffprobe`.
- Script statistics are lexical unless explicitly described as a parser or
  runtime result.
- Filename-derived roles are never upgraded above inference without independent
  evidence.
- Current working-tree code counts and materializer tables may include
  pre-existing uncommitted work; they are dated observations.
- Several aggregate/lexical probes were ephemeral read-only PowerShell or
  Python invocations and emitted console summaries only. The canonical digest
  makes the content snapshot repeatable, but the future ignored 5,515-row
  ledger remains necessary for per-file auditability.
