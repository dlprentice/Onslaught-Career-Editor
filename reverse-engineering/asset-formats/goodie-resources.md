# Goodie resources: what each Goodie shows (PC)

Status: active format contract — complete PC Goodie archive layout and Goodie-to-content mapping
Date: 2026-10-16
Verdict: all 232 installed Goodie archives parse to their exact final byte. In each, the number matches the
file name and the type matches the game's number rule. Every texture and mesh they name resolves to exactly one
installed file: 312 texture references and 45 mesh references, 248 distinct files. The archives hold no pixels or
geometry of their own; they name files on the game's existing texture and mesh shelves. Video and level Goodies
carry nothing, and the game picks their cutscene or level from the Goodie number.
Evidence: SOURCE + MEASURED. The layout and the rules were verified against the matched reader in the private
byte-matching decompilation:
- `CFEPGoodies::StartLoadingGoody`, `0x0045c9f0`, and `CFEPGoodies::LoadingGoodyPoll`, `0x0045cc10`;
- `CFEPGoodies::Deserialise`, `0x0045c870`, and `CFEPGoodies::Process`, `0x0045d7e0`;
- `CResourceAccumulator::GetFileName`, `0x004d6f70`;
- `CDXTexture::Deserialize`, `0x00559be0`, `CDXTexture::LoadFrame`, `0x00557300`, and
  `CDXTexture::FormatToString`, `0x00557a00`;
- `CMesh::Deserialize`, `0x004aab90`;
- `MakeCutsceneName`, `0x0046d810`, and `CDXFMV::Play`, `0x0053f190`.

The archives were walked with [`tools/goodie_resource_walk.py`](../../tools/goodie_resource_walk.py). The companion's
separate C# reader resolves every archive the same way: both print the content digest
`f4ddfbbe3c2df24b734efaeb4e5d1228538dcbb36b055380c11c01c723015a5e`, a SHA-256 over one
"number type item | item" line per archive.
Specimen: retail addresses cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`. The corpus is the installed
`data/resources/goodie_NN_res_PC.aya`, 232 files; their manifest digest (SHA-256 over `name sha256` lines in
Goodie order) is `8833322f88bffc00bdad27941026510a055a2af1ba13d40d7da9fad67842b207`.

The Goodies gallery unlocks pictures, models, videos and race levels. Which Goodies a career has unlocked is
career data; [`../save-file/`](../save-file/) covers it. This page covers what an unlocked Goodie shows when you
open it.

## Which file is read

The gallery's grid position gives the Goodie number (`get_goodie_number`, `0x0045cb80`; the grid table is in its
[function note](../binary-analysis/functions/FEPGoodies.cpp/get_goodie_number.md)). When a Goodie is opened, the
game decides its type from the number (the rule below).

Only image and model Goodies read an archive. The game loads resource id `-1000 - N`, which
`GetFileName` turns into `data\Resources\goodie_NN_res_PC.aya`: the number has at least two digits, so the first
ten are `goodie_00` to `goodie_09`. The load runs in the background (`LoadingGoodyPoll`), and the archive's
`GDIE` chunk reaches `CFEPGoodies::Deserialise` through the ordinary resource dispatcher
([lvlr-archive.md](lvlr-archive.md)).

Video and level Goodies are started from their number alone. Their archives exist (Goodies 66–70, 75, 77 and
201–231) but are never read. Goodie 232 is a video and has no archive.

## Archive layout

An archive is an AYA envelope ([aya-container.md](aya-container.md)) around a tagged stream of nested chunks. Each
chunk has a four-character tag, a little-endian `u32` payload size, then the payload. Each nested chunk lies wholly
inside its parent. Every installed archive is:

| Chunk | Payload |
| --- | --- |
| `LVLR`, `TARG`, `AYAD` | The usual resource prefix ([lvlr-archive.md](lvlr-archive.md)) |
| `GDIE` | Exactly one `GDAT` chunk; nothing follows `GDIE` |
| `GDAT` | `i32` Goodie number, `i32` type, then the type's content |

| Type | Meaning | Content after the two integers |
| ---: | --- | --- |
| 0 | Image | One texture reference (`DXTX`) |
| 1 | Model | `MDAT` (an `i32` count), then that many `TXTR` chunks each wrapping one `DXTX`, then `MESH` |
| 2 | Video | Nothing |
| 3 | Level | Nothing |

The reader reads the number but does not check it against the file name, and it sets the type from the file
after setting it from the number rule. In every installed archive the two agree.

For a model, the first texture is the backdrop drawn behind it: `goodies\goodies_F_Bakgrnd.tga` for 23 models,
`goodies\goodies_M_Bakgrnd.tga` for 22. The rest are the model's own textures, each named once.

### Texture reference

`DXTX` holds `CTEX`, a 344-byte image of the game's texture object, then one `TFRM` chunk per frame. Each `TFRM`
holds an `i32` mip-level count. The game copies the record over a new texture object, keeping only that object's
own links. The fields that matter here:

| Offset | Size | Field |
| ---: | ---: | --- |
| 8 | 128 | Name, NUL-terminated, for example `goodies\ca_f_characters\ca_fc_hawk.tga` |
| 172 | 4 | Width (`i32`) |
| 176 | 2 | Height (`i16`) |
| 312 | 4 | Frame count (`i32`, 1 to 16) |
| 324 | 4 | Requested format (`i32`, the list below) |
| 340 | 1 | Compressible flag |

Pointer-sized fields hold stale values from the writing run and are not read back. Goodies load their textures
"not from resources". For each frame, the game therefore loads the pixels from the texture shelf by name
(`LoadFrame`), never from the archive:

1. Replace every `\` in the name with `%`.
2. Append `(frame)` and the requested format's name. The names, by value 0 to 10, are `UNKNOWN`, `A1R5G5B5`,
   `A4R4G4B4`, `X8R8G8B8`, `A8R8G8B8`, `R5G6B5`, `DXT1`, `DXT2`, `DXT4`, `V8U8` and `Q8W8V8U8`.
3. Look in a folder:
   - with the game's DXTn-texture option on and the texture compressible, `data\resources\dxtntextures\`;
   - otherwise `data\resources\textures\`, with `mustbe_` before the name if the texture is not compressible;
   - when that file is missing and the texture is compressible, the game tries `dxtntextures` next.
4. The part after the folder (name, frame, format and `.aya`) may be at most 65 characters. If it would be
   longer, the game keeps its first 61 characters and appends `.aya`.

All 312 installed references are single-frame and compressible, and each resolves in `dxtntextures` with its exact
spelling. None has a twin in `textures/`, so the DXTn option does not change which file is read. The format in the
file name is the one requested, not necessarily the one stored; [dds-texture.md](dds-texture.md) covers the
stored DDS.

### Mesh reference

`MESH` holds `PMSH`, which holds `PMS2`: a 309-byte reference.

| Offset | Size | Field |
| ---: | ---: | --- |
| 0 | 300 | Mesh name, NUL-terminated, for example `f_be1.msh` |
| 300 | 4 | Runtime id (`i32`; 10002–10012 in the installed archives) |
| 304 | 4 | Optional flag (`i32`); when 1, a game that does not want the mesh skips it. It is 0 in every installed archive. |
| 308 | 1 | Keep-buckets flag |

The game opens `data\resources\meshes\m_<name>.aya` and reads the mesh from there
([cmsh-mesh.md](cmsh-mesh.md)). The 45 model Goodies name 42 distinct meshes, all installed.

## Videos

A video Goodie plays `data\video\<name>.vid` (Bink video) full-screen:

| Goodie | Video |
| --- | --- |
| 75 | `GILL_M_on_a_fork` |
| 77 | `UsTheMovie` |
| 201–231 | `cutscenes\NN`, where NN is the Goodie number minus 200, two digits |
| 232 | `cutscenes\33` |

The game's file names are matched without regard to case, as on Windows: Goodie 75 asks for `GILL_M_on_a_fork`, and
the install holds `gill_m_on_a_fork.vid`. A reader on a case-sensitive file system must match the same way. For a
cutscene, `MakeCutsceneName` falls back to `cutscenes\NN_small` when `NN.vid` is missing. Every installed
cutscene from 01 to 31, and 33, is present. Goodies 209, 212–216, 228 and 231 play without localisation. The
other cutscene Goodies pass the player's language to the video opener; how the opener uses it is an open
question. Goodies 75 and 77 are not localised.

## Race levels

Goodies 66–70 start race levels 901–905 in order.

## Type by number

The type rule, as the PC writer applied it and as `StartLoadingGoody` repeats it:

| Goodie numbers | Type |
| --- | --- |
| 0–7, 12, 13, 24, 33–35, 58–65, 71–74, 78–200 | Image |
| 8–11, 14–23, 25–32, 36–57, 76 | Model |
| 75, 77, 201 and above | Video |
| 66–70 | Level |

The installed archives split into 149 images, 45 models, 33 videos and 5 levels. Goodies 71–73 are image archives
the gallery grid never shows ([get_goodie_number](../binary-analysis/functions/FEPGoodies.cpp/get_goodie_number.md)).

## Source lineage

The pinned GPL source's writer (`CFEPGoodies::Serialise`) cuts an image into strips of at most 512 rows and
embeds them. The PC archives instead hold one reference to a whole texture, and the retail reader reads exactly
one. The installed files and the matched reader are the authority here.

## Open questions

- What does the video opener do with the language for a localised cutscene: choose an audio track inside the
  `.vid`, or something else? The cheapest falsifier is to play one localised cutscene with two language settings
  and compare its audio.
- Is any archive for a video or level Goodie read on any path? The reader skips them on the gallery path traced
  here.
