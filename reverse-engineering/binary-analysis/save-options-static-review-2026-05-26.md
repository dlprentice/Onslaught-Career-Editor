# Save, options and startup compatibility contract

Status: active bounded contract; comprehensive compatibility recheck in progress
Last updated: 2026-09-22
Summary: independently rechecked startup/serialization behavior and explicit remaining save/settings compatibility boundaries.
Evidence: MEASURED — selected pristine instructions and the isolated execution below; inherited subsystem summaries remain subject to recheck.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## September 19 independent recheck

The private `local-data/test-runs/save-startup-20260919/` owner contains selected
complete-body disassembly and `startup_control.py`. The accepted
`startup-run-o3zcj6ov/startup` receipt is
`9639d263d59a96532c7f182d1e0b209f20b4faa90bc9e4acc519c8dd938a45f7`.
Seventeen scenarios execute unchanged original startup, parser, career load,
career reset, binding initialization and options-tail reader bodies. After
startup returns through an intercepted graphics-create failure, the driver
**separately invokes** original Save, SaveWithFlag and the small default-options
writer. Those later calls do not imply that startup itself saves a file.

The input is the real tracked `gold_career_save.bin`, SHA-256
`0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb`;
negative controls modify only private in-memory derivatives. Original fixture
and executable identities are checked before and after execution. Complete
10,004-byte serializer outputs, their guards, selected before/after state and
source-buffer immutability are compared. This is independent execution of retail
code, not a reconstruction serializer testing itself.

| Question | Rechecked result | Evidence boundary |
| --- | --- | --- |
| Which settings file boots? | WinMain reads the CLI-writable name at `0063db18`; `-defaultoptionsname profiles/test.cfg` changes that read. The small writer independently opens the fixed `defaultoptions.bea` literal at `0063fc74`. | Original parser/WinMain/writer executed; file operations intercepted. |
| What rejects a file? | WinMain calls Load only after the requested byte count is read. Load checks the low 16 bits of `[00623e24] + 0x4bc0`; the pristine global is 17, yielding `0x4bd1`. It has no length argument or checksum check. | Missing, empty, short and wrong-version startup cases executed. No claim that the raw loader safely admits arbitrary buffers. |
| Does boot restore a campaign? | WinMain calls Load with flag zero, then calls Blank regardless of open/read/load success. Blank resets authored campaign nodes and progression while preserving volumes and control options. It does not erase the whole career record. | Complete direct reset state compared; final Goodie recomputation intercepted. |
| Are settings copied unchanged? | The tail reader copies some raw dwords, converts six signed integers through float32/x87, normalizes its final two bytes to booleans, and calls preset/language and audio actions. | Actual reader, packed-mode helper and numeric setter executed; downstream actions recorded but intercepted. |
| Is tail `+28` a device ordinal? | No: it packs width, height and a pixel-format class. Matching-current, matching-second, unavailable and empty mode-list cases have distinct results. A nonempty changed-mode lookup clears the packed key's low 16 bits after selecting a match or fallback. | Original lookup executed with explicitly authored mode capabilities, not host GPU enumeration. |
| Does Save only copy bytes? | Save appends the current active binding rows and current tail globals. The tail writer also refreshes packed-mode global `0066061c`. SaveWithFlag first changes live career `+2488` to one. | Both complete outputs compared in all 17 scenarios; no file publication. |
| Does writer return imply durable success? | The small writer ignores both `fwrite` and `fclose` results. Only open failure reaches its logger. | Success, open failure, short-write and close-error return values supplied to unchanged writer code. Actual filesystem effects untested. |

All system, allocator and graphics calls are intercepted. Audio, preset,
language, diagnostics and final Goodie actions remain explicit boundaries.
The Linux child admits only read/write/exit syscalls; a forbidden-call negative
control terminates with SIGSYS. These controls establish neither real desktop
startup nor full save compatibility. Exact commands and intermediate failures
are in [VALIDATION.md](../../VALIDATION.md#original-save-and-startup-controls--september-19).

## Original menu load and next-startup composition

`menu_control.py` in the same private owner passed 20 cases through unchanged
`CFEPLoadGame__DoLoad`, PC storage-info/read, name-conversion, career Load and
default-options writer bodies. Accepted stem `menu-run-47t_hlhy/menu`, receipt
`720608d9374496a1341259191136537c6a903c725a468e1eafb60c8092159211`.
This replaces the earlier static-only status of the normal load/publication edge.

The live career receives the file's data with its two packed counter bytes
normalized, but retains its previous volumes; bindings and selected tail
globals stay unchanged. If the post-page-call low byte at `0082b5b0` is zero,
the original writer receives **every byte of the original read buffer**.
Nonzero higher bytes alone do not suppress the write. File open/write/close
failures do not change the menu caller's success path. Actual page behavior,
latest-world selection, text/audio services and filesystem effects remain
intercepted rather than validated.

`menu_to_startup.py` then feeds the successful case's captured payload unchanged
to the existing original WinMain executable. Receipt
`533c72da0958207b18b1eb5ea20ec378598226a3c0ca5065451d71906f2f3639`,
stem `menu-boot-qssmorvv/chain`. Menu-live volumes remain `0.25/0.75`, whereas
the next startup reads the fixture's `0.6/0.4` bits, applies its bindings and
sensitivity, and resets campaign progress. The handoff assumes successful
storage; it does not prove durable publication, real process restart or audio
playback. The startup driver's later separately invoked serializers/writer are
outside this chain claim.

The PC reader controls also reproduce name narrowing to low bytes, filename
aliasing/truncation for authored wide strings, name-based identity despite
changed device/slot, one close on a short read and two closes on a complete
read. Supplied close errors do not alter full-read success. Upstream keyboard
admission and the actual CRT consequences remain open.

## Control preset recheck

Twenty separate original-code preset controls pass with original table
initialization and authored detected-count/enable flags. The existing
[binding contract](functions/Controller.cpp/ControlBindings.md#independently-rechecked-preset-behavior--september-19)
now replaces the ambiguous "scheme layers" description: the initialized image
has one 16-row preset group plus a joystick fallback table. Scheme 1 copies
matching rows; higher schemes may substitute the first two enabled devices.
With only one enabled device on that path, secondary-slot field0 is cleared
across all 47 runtime rows, including the 31 normally omitted from saves.

Those direct controls are now complemented by the composed loader experiment
below. Missing/duplicate/inactive/early-sentinel controls bound table lookup
behavior, not arbitrary malformed-save admission.

## Original loader, mutable bindings and later serialization

`load_preset_control.py` passed 19 cases through unchanged Load, TailRead,
ApplyPreset and their actual table helpers, followed by original Save/TailWrite.
Accepted stem `load-preset-run-k8m1uqgd/load`, receipt
`2235a9b50f4d537e1ec45c5fabc2c491ca6c73450d59d0608496e2c2fcab8610`.
The driver measures the actual tail-end ESI at the language-call boundary and
compares complete selected state, serializer output and guards.

Only the flag's low byte selects its mode: `0x100` applies bindings and tail;
`1` and `0x101` preserve receiver volumes and skip them. A separate receiver
control confirms that zero-mode audio calls still use canonical CAREER's
absolute volume globals, rather than the selected receiver's copied values.

The binding table is a sequence of 32-byte records terminated by ID `-1`.
Loading chooses each destination using its pre-copy active byte, then replaces
all 32 bytes without validating the incoming active flag or ID. File row IDs
do not select destinations. Altered metadata can affect later sizing/writing;
the ordinary initialized 16-active-row contract is not arbitrary-file validation.

| Private input change | Observed direct same-process result |
| --- | --- |
| First saved row becomes inactive, custom scheme | Size changes `10004 → 9972 → 9940` across two loads of the same input. The second tail starts at `0x269e`, 32 bytes earlier than `0x26be`. |
| First saved ID becomes `-1` | The first load still consumes the ordinary 16 rows. Later table walks stop at the new first sentinel: size becomes 9492 and the next load reads its tail at `0x24be`. |
| First saved row becomes inactive, scheme 1 | Actual preset application restores that row; both loads retain size 10004 and tail start `0x26be`. |
| First saved ID duplicates the next row | Both loads retain the ordinary size and tail start in this tested custom-scheme case. This does not make duplicate IDs equivalent under later preset lookup. |

These are deliberately changed private derivatives of the real fixture.
Repeated direct calls do **not** establish drift across fresh startups, which
run the binding initializer again. Final Save consumes the resulting live table;
it is not fed back into Load in this experiment. Language/audio/latest-world
actions remain intercepted here. No arbitrary malformed-file safety is claimed.

## Original language application and persistence

`language_control.py` then replaces the language hook with original
`CFrontEnd__SetLanguage`, cleanup and `CText__CopyFrom`, keeping the real
Load/TailRead/preset/Save chain. Sixteen cases pass; accepted stem
`language-run-n__ph8sw/language`, receipt
`016b415f9846f13e02fc2c290e5c96c52e01f1af9cc245d30d119cf507fde5dd`.
The five cache slots and one adjacent-state negative control use explicitly
authored headers/buffers. They are not actual loaded language files.

TailRead's unsigned 16-bit selector chooses a cached object through unchecked
`frontend + 0xbf40 + selector * 0x30` arithmetic. The copy frees a nonnull
destination buffer, copies selected header fields, allocates/copies exactly the
source byte count, and rebases two pointers. Destination `+20..+2f` survives;
the old claim that every object field is copied was incorrect. Reapplying the
same selector repeats the free/allocation/copy. Sizes 0, 1, 3, 4, 7 and 17
exercise the dword and trailing-byte copy paths. See the precise
[copy contract](functions/text.cpp/CText__CopyFrom.md).

The active language field is copied from the source header's `+1c`; only after
that operation returns does TailRead store the input selector to `0066305c`.
Save writes the **low word of active header `0083d97c`**, not that mirror.
An authored selector 2/header-language 4 case therefore saves 4; a full header
value `0x12345678` saves `0x5678`. These controls distinguish the two owners,
not legitimate localization configurations. Index 5 and out-of-buffer pointer
controls expose missing bounds checks without establishing supported inputs.

These September 20 controls execute cleanup's null-object path. The subsequent
[nonnull cleanup contract](functions/FrontEnd.cpp/CFrontEnd__SetLanguage.md#nonnull-cleanup-before-text-replacement)
adds 26 direct cleanup/language-change cases: original nested menu destruction,
resource decrements and monitored-pointer invalidation precede text replacement.
Its authored objects, intercepted heap and optional child calls leave complete
UI construction/destruction open; it is not another Load/Save composition.
Allocator/free and audio services remain intercepted here. Fresh static
inspection of `CText__Init` confirms that it sets the language field before
opening or parsing the file, and that its American override/invalid-selector
fallback can select a different filename without changing that field. Thus
neither the input mirror nor header language proves which text actually loaded.
The following controls now establish bounded real-file parsing and lookup;
localized menu acceptance remains open.

## Original language files, lookup and failure handling

`language_file_control.py` passes 19 cases through ten unchanged bodies:
original Init, text/file constructors, file destructor/size/cached Read/Close,
and SetLanguage/null cleanup/CopyFrom. All six preserved language inputs are
identified in `language-file-inputs.json` and parsed from their actual bytes.
Accepted stem `language-file-run-8clnw9rt/file`; receipt
`a3bebcc872a6df436cbbdd01351ea4ab0599c55fa48954ef8d48f1ba46d3aaec`.

Open supplies the explicitly measured final-prefetch file-object shape;
allocation/free, formatting, GetFileSize and CloseHandle results are
intercepted. The original cached reader consumes actual admitted bytes.
Init does not check its returned count: under the declared zero allocation
fill, a 16-byte or empty cached read still reaches loaded state. Unknown
tagged versions also set that flag after an ordinary returning diagnostic,
without replacing prior version/count/pool fields. Neither result is
successful localization. Open failure stops at the real fatal-call site;
the downstream `ExitProcess(1)` chain remains static evidence.

American override and invalid-selector English fallback preserve the original
header's supplied language value. The latter test passes 65535 to Init and
zero to SetLanguage; no out-of-range SetLanguage safety is implied. Legacy/v1/v2
header derivatives establish arithmetic, not valid older resources.

`language_lookup_control.py` imports the exact original parser/active-copy
header and allocation snapshots into three unchanged lookup bodies. Accepted
stem `language-lookup-run-ekd5wuja/lookup`; receipt
`13dff5555778153c3971046d8771c99ddd66c6114332df6dcc9c8c83e102db7b`.
Seventeen cases pass: six complete resource queries and eleven owned controls.
Every one of each file's 2,571 IDs, plus a missing ID, goes through text,
audio-name and adjacent-string selection. All six have unique IDs; expected
pointers, bounded terminated UTF-16 text and ASCII audio names pass. This
is an explicit memory-image handoff, not continuous game execution.

The recheck resolves three important selection rules:

- Text/audio searches use the first matching physical record. A first
  duplicate with audio offset `-1` returns null even if the next duplicate
  has a name. The six original files contain no such duplicates.
- “After” means a displacement in physical records, not another matching ID.
  Its fixed 12-byte stride also differs from ordinary v1 text lookup.
- Missing text returns the pool base after a diagnostic; missing audio
  returns null. After's unsupported-version diagnostic returns null, despite
  its fatal wording. The old note overstated termination.

Controlled adverse offsets/counts/versions expose absent bounds checks; they
are not supported save or language inputs. Actual file opening, refill,
decompression, nonnull cleanup, allocator failure, audio playback, rendering
and full startup/save composition remain open.

## Original volume application and save composition

The former music/sound setter hooks are now independently rechecked and replaced
in a composed experiment. `audio_volume_control.py` executes four original
bodies: music setter, sound setter, camera getter and PC UpdateSound. Twenty-five
scenario/rounding combinations pass once at each of x87 PC53 and PC64, yielding
50 cases. Accepted stem `audio-volume-run-vra1oais/volume`; receipt
`80a944c49b0e54c3ee76cd128d7f314dcd440a935a14dbd1874a4775e85f29a0`.
Manager/event state and 2D COM boundaries are authored; this opens no device.

Music stores the x87-converted configured integer, logs, then preserves the
original float bits in career. It leaves current/target fade values unchanged.
Sound stores its master float, logs, writes career, then recalculates both volume
fields on every linked event. Low-byte playing and signed channel checks select
device updates. The controls cover category differences, tracking, null buffers,
an intercepted SetVolume error, low-volume remapping and sample-rate fallback.
Logger snapshots establish manager-before-career-write ordering.
See the precise [music](cmusic-shared-semantics-2026-08-11.md#september-20-independent-volume-recheck)
and [sound](csoundmanager-shared-semantics-2026-08-11.md#september-20-independent-volumeevent-recheck)
contracts.

`load_audio_control.py` then passes 16 cases through original Load, both
setters, TailRead/preset/language application and later Save. Accepted stem
`load-audio-run-ehbe0h_d/load`; receipt
`3f92794e90da6d0728787ecfe6be39f3e8cd441ab43a1baec5352a962b74a972`.
It retains a playing event with a null device buffer and a nonplaying tracked
event. The fixture's unchanged music/sound bits produce configured music 51
and sound master `0.6000000238418579`. Both event records update before the
tail/preset/language actions. Nonzero low-byte flags preserve live settings and
skip those changes; repeated loads retain the expected serialized bytes.

The entire selected manager/event state, source, guards and serialized capacity
are compared. PC53 nearest is explicitly supplied; the direct controls also
test other rounding directions. Neither is a live post-device FPU observation.
The original fixture and executable remain unchanged.

This Load/audio/Save experiment still intercepts reset and language-bank calls.
The separate controls below now execute their original callers; they have not
yet been folded into this load/serialization composition.

## Original audio reset and language-bank retry behavior

The [reset controls](../../VALIDATION.md#original-audio-reset-and-music-restoration--september-20)
execute nine unchanged bodies in 26 cases. Original shutdown deletes sample
objects, stops/frees music state, handles message voice, and releases/clears
device slots before attempting sound Init. Init admission tests its low return
byte. The outer wrapper continues after a supplied failure return: enabled
music still passes through original selection and changes mode/selection fields,
even though the now-empty playlist produces no play call. This is a controlled
return-value experiment, not an actual device failure.

Original music Init resets current/target volume to 127, derives configured
volume 51 from the preserved fixture, and consumes a playlist supplied by the
owned platform-Init hook. Restoration selects category 2 for Level 100 and
category 4 for the tested Level 110 route; frontend selection uses category 0.
The original selection code falls back to the playlist head if the requested
track is unavailable. Virtual playback, real playlist creation and audible
continuity remain outside the experiment.

Shutdown clears the playlist head but does not itself clear the current-song
pointer at music `+0x10`. The disabled-music and direct-reset controls retain
that pointer after recorded free calls. Free/destructor hooks preserve owned
memory, so this neither proves a valid lifetime nor demonstrates a real dangling
access. The alternate-manager case likewise establishes the final canonical
sample-list traversal without claiming safe sharing after real destruction.

The [bank controls](../../VALIDATION.md#original-language-bank-admission-and-retry--september-20)
execute seven unchanged bodies in 22 cases. Once initialized, Reload obtains the
name from active CText `+0x1c`, builds the bank path, and compares it with the
manager's cached path using original ASCII case-insensitive comparison. Equal
paths return before changing events, samples or buffers. American text-file
selection still maps to the English bank name in this getter.

For a changed path, retail **stores the new path first**, recycles active events
into the free list, stops the canonical buffer slots, deletes the receiver's
samples, cleans memory and calls the canonical bank loader. Resource-build
mode or disabled compressed audio can then skip loading; an intercepted Open
failure instead executes the real buffer destructor. None rolls back the path.
A second identical request skips loading even after either blocking flag is
changed. A different language retries. The cache therefore records the requested
path, not successful audio availability. This is a reproduced original caller
quirk, not a claim that the preserved or installed bank files are missing.

Bank Stop visits 64 ascending slots, retains their pointers and ignores the
supplied result. Device shutdown separately calls Release and clears its slots.
The alternate-manager control uses distinct buffer objects to distinguish the
canonical Stop target and canonical bank path from the receiver's own state.
Its event/sample nodes are deliberately shared and do not model independent
healthy managers. The embedded trace calls target `0040c640`, whose pristine
body is only RET; intercepted trace records are not retail log output.

These tests preserve the selected executable and fixture. They do not execute
successful bank parsing, real device/platform setup, actual allocation/free,
nonnull language cleanup, a complete startup or durable save reopening.
Unchanged full bodies and explicit hooks are pinned in the private receipts;
this tranche changes no Ghidra database or implementation-lane source.

## Original sample decoding and saved quality

The [44 direct sample controls](../../VALIDATION.md#original-sample-decode-and-quality-conversion--september-22)
execute unchanged sample loading `005172a0`, cached Read `00548570`, device-buffer
creation `00517440`, ADPCM decoding `00517fa0` and conversion `00517600`. The
heap and COM methods are explicit recording hooks. Original bank traversal,
outer CreateSample/name lookup, real device behavior and playback are excluded.

Two complete size/payload records come from
`local-lab/safe-copy-bea-pristine/data/sounds/sounds_english_pc.xap`, SHA-256
`658c15e3bab844d65dd3c07c4ac880f16f741c0ea116f48c603449bbd4dda8b7`.
Its 164 record extents reach exact EOF; 106 declared PCM sizes are divisible by
four and 58 have remainder two. None is odd. That is a metadata pass over this
one bank, not execution of all records. Zero-based records 3 and 4, the computer
and energy plant atmosphere samples, are the two actually decoded at each normal
quality value. The executable is the pristine specimen pinned at this document's head.

For the bounded nonnegative byte counts tested, the direct helper requests
`ceil(N/4)` compressed bytes and decodes `floor(N/2)` signed PCM samples with
fresh predictor/index state zero. The high nibble is consumed first. Static
instructions establish the signed predictor, clamped index `0..88`, individual
step shifts and predictor saturation; the two actual records and authored
controls execute that path. State can persist through the decoder's state
pointer, but nibble phase does not; arbitrary odd-sized decode chunks cannot be
assumed equivalent to a single call. Nonzero initial-state/chunk behavior has
not been executed by these controls.

| Quality word | Requested device bytes | Converter writes | Mono format |
| --- | --- | --- | --- |
| `0` | `N` | Direct decoder writes `2 * floor(N/2)` | 44,100 Hz, 16 bit |
| `1` | `ceil(N/2)` | `2 * ceil(N/4)` | 22,050 Hz, 16 bit |
| `2` | `ceil(N/8)` | `floor(N/8)` | 11,025 Hz, 8 bit |
| Other tested values (`3`, `-1`) | `N` | `floor(N/8)` | 11,025 Hz, 8 bit |

Quality 1 averages adjacent mono samples using a signed right shift; an
incomplete four-byte group appends a zero word. It is sample-rate reduction,
not the stereo-to-mono interpretation in the historical W009/A05 review. The
lower-quality path averages complete groups of four samples into unsigned
eight-bit output and discards the incomplete group. These formulas do not
establish safe admission of negative/overflowing lengths.

Record 3 declares 29,490 PCM bytes: quality 1 requests 14,745 but writes 14,746;
quality 2 requests 3,687 but writes 3,686, leaving the last byte unchanged.
Record 4's 29,752-byte size produces exact requested/written sizes at all three
normal qualities. The instrument deliberately supplies oversized guarded
storage. These results do not establish that a real DirectSound buffer permits
those writes, that retail crashes, or what a player hears.

A supplied Create/Lock failure still returns a nonnull sample object without
decoding; Lock failure releases and clears its buffer pointer. A zero payload
read returns null through the sample-destructor boundary. A nonzero short read
is accepted and decoding includes retained allocation filler. The helper also
ignores a short returned lock span, passes the original `N` to Unlock after
conversion, and ignores the supplied Unlock failure. Reuse here means an
explicitly supplied object; outer name selection/list ownership is not tested.
None of these quirks is a recommendation to reproduce unchecked writes in Godot.

Read-only extraction of the current materializer's two literal tables and pure
`_decode_ima_high_nibble_first` function reproduces both entire quality-0 native
outputs byte for byte. This is a focused consumer comparison, not a full asset
materialization run. An authored seven-byte case matches the first six bytes;
the materializer emits a seventh while the original helper leaves it unchanged.
Since all sizes in the selected bank are even, that control does not demonstrate
a defect in its shipped materialized output. The exact source and output hashes
are retained in the private comparison linked from validation.

## Outer sample admission and registration

The [25 outer-call controls](../../VALIDATION.md#original-sample-admission-and-registration--september-22)
add original `004e0890`, ASCII `stricmp`, `strncpy` and the five-byte stub at
`00517290` to the preceding sample pipeline. They use only English-bank record 3;
existing sample objects and list layouts are authored. Formatter, logger,
heap/COM and actual sample destruction remain intercepted.

With a nonnull data stream, `004e0890` calls `005172a0` with the stream, original
music word and selected existing object. With a null stream, it passes the path
buffer intended for `sounds\%s` or `music\%s` to `00517290`; that original stub
returns null. No name search or sample insertion occurs on that path. The
instrument observes the formatter arguments but deliberately emits no path
bytes: neither tested branch reads that destination afterward.

This contradicted the former metadata name `LoadSampleFromBuffer_StubFail` at
`00517290`, and the filename implication of `CreateSampleFromFile` at
`005172a0`. The [protected correction](../ghidra/README.md#sample-loading-metadata--september-22)
now saves `CPCSoundManager__LoadNewSample_StubFail` and
`CPCSoundManager__LoadSampleFromBuffer`, respectively. The caller establishes a
filename-route stub and a working cached-buffer loader. The partial source at
`references/Onslaught` commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`
has the opposite PC implementation availability: `pcsoundmanager.h:58` stubs
the buffer loader, while `pcsoundmanager.cpp:151` implements filename loading.
`SoundManager.cpp:248` also lacks retail's fourth reuse argument. Those source
identities must not be copied onto retail mechanically. The correction also
renames the filename and music parameters, preserving all types, storage and
function bodies. Original-code controls and actual device behavior remain
separate evidence categories.

Separately, the bank call at `00517e89` passes music zero and forwards its own
argument as the reuse argument. Its former `stream_mode` parameter is now named
`reuse_existing`. The existing `char` type occupies one recorded parameter byte
while the callee purges four stack bytes; both measurements remain unchanged.
This caller edge is statically inspected; the complete bank loader has not
executed in these sample controls.

Retail tests only the reuse argument's low byte. Values `1`, `2` and `257`
admit reuse; `0` and `256` do not. The first case-insensitive match in physical
list order wins, including after a nonmatching head and before a duplicate.
Reuse preserves list position. A fresh object prepends to the existing head.
Successful return stores the whole music word, clears language-dependent state,
copies at most 99 name bytes and terminates the 100-byte name field. Left/right
type comes from the **stored** name's case-insensitive `_L`/`_R` suffix, and only
when its length exceeds five. A 100-character input losing its final character
therefore loses the tested suffix classification.

A supplied device-create failure still yields a sample object that the outer
caller inserts. A supplied lock failure on reuse preserves its list position
and returns that object without PCM. Returning null after a zero payload read
invokes the logger boundary instead of insertion. That earlier experiment's
destructor hook retains objects, so its unchanged reused-sample list is not a
retail unlinking result. The following controls replace that boundary with
original destruction under canonical ownership. Whole-bank traversal and
successful playback remain open.

## Original sample destruction and failed loads

The [23 standalone and 11 composed controls](../../VALIDATION.md#original-sample-destruction-and-failed-loads--september-22)
execute the original deleting wrapper, derived/base destructors, matching-event
shutdown, channel stop, owner clearing and reader-list removal. The composed
route additionally executes `004e0890` → `005172a0` → cached Read, with an
authored size word followed by immediate EOF. Objects, ownership lists and
device returns are supplied; heap/COM calls and owner notification record state
without reclaiming or mutating objects.

The deleting wrapper at `00516960` always destroys the sample. Low-byte flag
bit zero controls the final object-free request: `1`/`257` request it and
`0`/`2` do not. Derived destruction at `005168d0` first shuts down matching
events, then frees/clears sample allocation `+0x78` and releases/clears sample
buffer `+0x80`. Base destruction at `004dff30` changes the vtable, repeats the
event traversal and unlinks through canonical manager `00896988`. Head, middle,
tail and singleton cases are exercised; the singleton leaves the head null.
Sample next and size fields are not cleared. Normal SEH-chain restoration is
checked; exception dispatch is not executed.

An event matches through its sample pointer at `+0x0c`. Owner notification
requires flag DWORD `+0x7c` to equal **1** and a nonnull owner. Notification
precedes channel shutdown, clearing the playing byte and owner detachment.
Playing byte zero does not suppress channel stopping; a negative channel skips
that call. For a nonnull primary channel, original `005179b0` requests Stop, primary Release,
primary clear, then secondary Release/clear. **An initially null primary returns
without touching a nonnull secondary.** Supplied return bits do not prevent the
observed stores; this does not establish real COM failure handling.

When registered, owner clearing removes only the first matching reader-list node,
recycles it, decrements the count and leaves the cursor unchanged. Event sample pointers,
links and channel values remain, as do the manager's event head/count/free-list
fields. Duplicate/missing registrations and owner-null orphan registrations are
deliberate boundary fixtures. In the normal supplied chain, derived detachment
clears owners before base traversal: **no base-loop notification was observed**.
Complete body inclusion is not coverage of every callback or device branch.

The composed failure cases establish a consequential ordering: reuse frees old
storage and releases its sample buffer **before** attempting the payload read.
A zero result then frees the temporary allocation, executes the original sample
destructor, unlinks the sample and requests its final free; the outer caller
returns null and invokes the logging boundary. The destructor does not request
those already-cleared sample resources again. This is not transactional
replacement preserving the old sound. Fresh failure constructs a next-null
sample, destroys it without publication and preserves all existing canonical
samples/events. Its base unlink still traverses the existing list and writes
the already-zero final link; unchanged state does not mean no store occurred.
Authored size zero follows the same null-return path even though
the reader's error field remains zero; positive size with immediate EOF sets it.

Separate adverse fixtures show that base unlinking does not require finding
the sample first: an absent sample with a foreign next pointer rewrites the
canonical tail, or the head when empty. These intentionally inconsistent states
do not demonstrate corruption in a healthy retail session. Actual reclamation,
COM lifetime, mutating owner callbacks, repeated destruction, bank traversal,
retail file behavior, audible results and complete startup remain open.

## Original save reload after reinitialization

The [round-trip controls](../../VALIDATION.md#original-load-save-and-reload-controls--september-20)
pass 15 cases through unchanged Load, the settings/preset/language-copy and
volume bodies, and both Save variants. The second Load reads the first native
serializer's buffer directly. Optional original career and binding initializers
run between the two loads; no Python serializer supplies that second input.

With full settings application, the real 10,004-byte gold fixture survives both
serializations exactly, with and without intervening career initialization.
This includes its unknown bytes. Private derivatives distinguish counter
normalization, preset restoration and progress-flag writes. Plain Save retains
a zero progress scalar; SaveWithFlag changes it before copying. When only the
second save sets it, the sole changed byte is file offset `0x248a`.

Load's preservation flag is its **low byte**: `0x100` applies settings and
`0x101` preserves them. When the second Load preserves settings after career
initialization, its output legitimately contains the initializer's sound/music
floats `0.8/0.9`, rather than the fixture's `0.6/0.4`. The two volume words are
the only changed fields between those saves. Audio-manager state remains from
the first load because this second load skips the setters. Preserving live
settings is therefore not equivalent to restoring saved settings or resetting
the audio system.

Six selected snapshots, the full supplied input, both serializer capacities,
guards and ordered boundary observations are checked. Generated output copies
are written with create-new semantics, fsynced and reread on Linux. That checks
these private files, not retail/Windows publication or crash durability. The
career static initializer is not Blank. Audio reset/bank, allocation/free,
diagnostics and latest-world selection remain hooks; language caches and audio
objects are authored. This is bounded original-code compatibility evidence for
one real fixture and named derivatives, not complete startup acceptance.

## Original startup reset including Goodies

The [extended startup controls](../../VALIDATION.md#original-startup-reset-with-goodies--september-20)
replace the former Goodie hook with the unchanged recomputation and its required
helpers. Original descriptor initialization supplies the thresholds; zero-filled
BSS is not an equivalent starting state. WinMain, Load and Blank execute in 17
valid, missing, short, invalid-version and options-tail scenarios.

After Blank, exactly Goodies `0, 1, 8, 14, 33, 36, 41, 42, 43` have state `1`
(instructions available). All other 291 slots are zero; none is unlocked at
state `2` or above. Both badge bookkeeping globals remain zero. Thus the final
reset result is not an entirely zero Goodie array. Complete career comparisons
retain the options, each node's leading word, and unused node/link storage while
rebuilding the 43-node/86-link authored graph and clearing progression.

The recheck also corrects the old name for career `+0`: it holds pending extra
Goodies, not the accumulated new-Goodie count. At `00420230–0042026c`, original
instructions add that pending value and the count delta to global `00662b20`,
then clear the pending field. `00662b24` is the first-Goodie flag. Progression
predicates use canonical CAREER even though Goodie writes use the receiver;
alternate-receiver behavior remains static evidence here.

The reset-time result is executed, not merely predicted from partial source.
It does not validate every unlock rule or the Goodies UI. Positive-ranking CRT
conversion is an unexpected-entry trap in these reset cases; malformed graphs
and alternate receivers are excluded. File, allocator, graphics, audio and
preset/language services retain explicit boundaries. Separate post-startup Save
calls do not imply that WinMain saves settings automatically. No original save,
Ghidra database or implementation-lane source was modified.

## Rechecked static edges awaiting further execution

The PC save reader checks the requested byte count, not trailing EOF; open
failure leaves `out_read` untouched. Its older demo-comparison results remain
inherited evidence, not comparisons rerun here.

## Implementation-consumer findings

The retained `BesFilePatcher.ApplyOptionsTailOverrides` clamps mouse sensitivity
to `0.1..5.0`. Fresh bytes place the image default at `7.0`, and the retail menu
setter at `004cefe0` writes `(index + 1) * 3.0`; the construction bounds yield
`3, 6, ..., 63`. The tail reader preserves the raw sensitivity dword. Therefore
that editor's range is a narrower application policy, not the retail range.
The `OptionsD3DDeviceIndex`/`D3DDeviceIndex` consumer names similarly misdescribe
the packed display-mode key. No companion/rebuild code was changed in this RE pass.

The language decoder preserves physical rows, but its string readers do not
enforce declared pool bounds or termination. Four private in-memory probes
reproduce silent empty/truncated results and text running into the audio-size
field; receipt `language-lookup-consumer-probe.json` is in the same private
owner. Strict rejection would be an offline validation policy, not an imitation
of retail's unchecked pointers. The rebuild materializer's ID dictionary and
corpus exporter's merged matrix select the last duplicate, unlike retail's
first match; original per-language export rows retain ordering. All six measured
files have unique IDs and valid pools, so these are derivative-input limitations,
not demonstrated errors in their current retail outputs.

## Inherited surface and routing

The table below routes earlier work. Items outside the recheck above are not
newly verified merely because they remain documented here.

| Area | Current evidence | Boundary |
| --- | --- | --- |
| Save container | Retail files are `10004` bytes, start with version `0x4BD1`, and store `CCareer` from true-view base `0x0002`. `CCareer__Load`, `CCareer__Save`, and `CCareer__GetSaveSize` own the binary path. | Static ownership does not prove every frontend save-menu path. |
| Career data | The mapped body includes 100 nodes, 200 links, 300 Goodie slots with 233 displayable entries, five packed kill counters from `0x23F6`, and raw float ranks. | In-game presentation and unlock animation remain runtime behavior. |
| Options | Flags begin at `0x249E`, control entries at `0x24BE`, and the options tail is `0x56` bytes. `OptionsTail_Write`/`Read` and the binding helpers own this structure. | Hardware/input behavior needs focused runtime evidence when claimed. |
| Frontend persistence | `CFEPLoadGame__DoLoad`, `CFEPOptions__SaveDefaultOptions`, `CFEPOptions__WriteDefaultOptionsFile`, `CPauseMenu__ResumeGameAndPersistOptions`, and `Platform__AsyncSaveCareer` connect frontend actions to serialization. | Static xrefs do not establish filesystem timing. |
| Product behavior | `BesFilePatcher` validates size/version, refuses in-place output, preserves unknown and reserved regions, supports scoped options copy, and blocks career writes to options-like files unless explicitly overridden. | These guarantees remain protected by focused AppCore/UI tests. |

## Canonical owners

- [Save format](../save-file/save-format.md)
- [Structure layout](../save-file/struct-layouts.md)
- [Career graph](../save-file/career-graph.md)
- [Grade system](../save-file/grade-system.md)
- [Goodies contract](../save-file/goodies-system.md)
- [Kill tracking](../save-file/kill-tracking.md)
- [`CCareer__Load`](functions/Career.cpp/CCareer__Load.md) and [`CCareer__Save`](functions/Career.cpp/CCareer__Save.md)
- [Control bindings](functions/Controller.cpp/ControlBindings.md)
- [`CFEPOptions__WriteDefaultOptionsFile`](functions/FEPOptions.cpp/CFEPOptions__WriteDefaultOptionsFile.md)
- [`CPauseMenu__ResumeGameAndPersistOptions`](functions/PauseMenu.cpp/CPauseMenu__ResumeGameAndPersistOptions.md)
- [`BesFilePatcher.cs`](../../OnslaughtCareerEditor.AppCore/BesFilePatcher.cs)

## Open boundaries

- copied-profile runtime save/load and controller-remap behavior;
- exact source-layout identity for every object field;
- complete Goodies wall/model-viewer behavior;
- rebuild parity.

Contradictory controlled runtime evidence or a reviewed static correction may refine this contract. Historical queue completion and readiness artifacts are not independent authorities.
