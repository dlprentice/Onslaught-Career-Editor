# Audio and music header source contract

Status: bounded source-first expansion receipt
Last updated: 2026-08-22
Evidence: SOURCE — the pinned three-header family and shared expansion partition; MEASURED — pristine-PC name/closure, Generation-32, semantic-table, and exact-body receipts; INFERRED — rebuild dispositions only; UNKNOWN — unselected emitted accessors, audible parity, and the standalone `CEffect` destructor identity.
Specimen: pristine PC retail `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; never the patched installed executable.
Verdict: all 23 omitted audio/music header definitions now have source contracts, bounded retail dispositions, explicit falsifiers, and rebuild routing without editing the canonical crosswalk.
Scope: the 23 omitted stable definitions in `Music.h`, `pcsoundmanager.h`, and `SoundManager.h` at pinned source commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.

## Authority and boundary

This receipt starts from Stuart Gillam's pinned source, then uses the pristine PC retail semantic tables only to classify released agreement, divergence, or unresolved identity. The retail specimen is `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`. Source analogy is not retail equality. A named deleting-destructor wrapper is not silently promoted to the standalone source destructor, and a bounded `NO_MATCH_FOUND` means only that the current instruments selected no supported target.

The exact source files and hashes are:

- `references/Onslaught/Music.h` — `8715ff13802163367e2e6009c1a14124cb8cf7d76de5135a3fa2548a449ad27a`
- `references/Onslaught/pcsoundmanager.h` — `ed7770ae596f1ec9f348fc4e3b29852d5f20ea76fa73f0078de6170963bc361c`
- `references/Onslaught/SoundManager.h` — `c1710946f0e62a09b5788462e2754f239d8c5de1cbd29f6d938483514838cdad`

`definitions.tsv` is the row-level contract and `RETAIL-DELTA.tsv` is the source/retail adjudication ledger.

## Reuse preflight

No new binary measurement, G: corpus access, generic crosswalk, or PS2 work was performed. The wave searched tracked owners and `local-lab/INDEX-CATALOG-2026-08-17.md` by audio/music subsystem, all 23 stable keys, both selected VAs, the plan/catalog hashes, and the responsible catalog tools. It reused rather than rediscovered:

- the durable `source-first-expansion/PLAN.md`, `partition.tsv`, `sample.tsv`, and `manifest.json` predecessors (hashes are pinned in `RECEIPT.json`);
- current Generation-32 `campaign.ready.json` (`08ed8964…e73f`), tracked `EVIDENCE-REGISTER.tsv`, and generated `contract-schema/coverage.json` for current catalog disposition;
- the current 8,329-row name projection, 8,136-row closure, four promoted audio/music semantic tables, W007 destructor review, and existing source synthesis;
- the current `Level100Audio`/catalog/tests/provenance owners plus the historical `LEVEL100-AUDIO-PARITY-2026-07-26.md` and `AUDIO-PARITY-LAWS-2026-07-27.md` routes identified by the local catalog.

All 23 rows are `EXTENDED`: their stable identities and readiness existed in the shared partition, while this wave adds source algorithms, retail delta statuses, falsifiers, and rebuild dispositions. `NEW_MEASUREMENT` is zero.

## Source architecture

The headers split audio into shared policy and a selected platform backend:

```text
CMusicMenu / CSoundManagerDebugMenu   source debug surfaces
CMusic                                playlist, selection, fade and shared volume state
  -> virtual Device* interface        platform boundary
  -> CPCMusic on TARGET == PC         selected elsewhere by Music.h:109-112

CEffect -> CSample -> CSoundEvent -> CSoundManager
                                  -> CPCSoundManager on TARGET == PC
```

`Music.h:48-106` keeps playlist and transition policy in `CMusic`: play type, playing flag, linked songs, queued/current song, target/set/current integer volume, selection, and initialization state. Its platform interface is the virtual block at `Music.h:90-102`. `SoundManager.h:43-91` owns named effect recipes and the global chained-effect list; `SoundManager.h:124-158` defines each live event's owner, channel, tracking, category, loop, fade, pitch, spatial, completion, and pause state; and `SoundManager.h:173-277` owns logical event/sample roots, category volumes, listener state, and the 256-event policy implemented in `SoundManager.cpp`. `pcsoundmanager.h:42-86` supplies the PC DirectSound adapter selected by `SoundManager.h:280-283`.

## The 23 omitted definitions

### Shared music accessors and hooks (6)

- `Music.h:32 CMusicMenu::GetName` writes the literal `Music` to the caller buffer; `Music.h:34 GetShowSubmenus` returns true. These are debug-menu behavior, not playback policy.
- `Music.h:68 CMusic::GetVolume` exposes `mSetVolume / 127.0f`; `Music.h:69 GetCurrentVolume` exposes the mutable fade/device value `mVolume`. The source therefore distinguishes configured and current integer volume.
- `Music.h:78 DeviceWarnOfStop` is an empty notification hook.
- `Music.h:102 DeviceUpdateStatus` is a non-pure empty default virtual. The retail CPCMusic vtable report independently identifies slot 8 as the inherited one-byte no-op shared by 228 placements, but it does not assign a unique body/VA to this source key (`cpcmusic-vtable-semantics-2026-08-11.md:59-60`).

The surrounding released music policy is materially stronger than these accessors: retail preserves integer current/target/set state, five-point fade steps, selection replay, and the assignment-to-random source bug, while changing directory extension to Ogg and changing normalized option conversion to `round(volume * 127)` (`cmusic-shared-semantics-2026-08-11.md:38-86`). Those are family deltas, not invented VAs for the six header keys.

### PC sound backend accessors/stubs (2)

- `pcsoundmanager.h:58 CPCSoundManager::LoadSampleFromBuffer` always asserts unimplemented and returns null. Retail `0x00517290` is an exact five-byte/two-instruction two-argument null stub (`cpcsoundmanager-backend-semantics-2026-08-11.tsv:7`). Production compressed sample loading enters a separate retail extension at `0x005172A0`; the stub is not the production loader.
- `pcsoundmanager.h:75 GetAvailableChannels` returns `MAX_SOUND_BUFFERS`, defined as 32 at line 20. Released `DeviceInit` instead clears 64 physical slots and derives the active voice count from device capabilities; `FindFreeChannel` scans that active count (`cpcsoundmanager-backend-semantics-2026-08-11.md:41-59`). No exact accessor body is selected, so the source/release capacity contract diverges while the stable key remains `NO_MATCH_FOUND` rather than receiving a guessed VA.

### Effect-list lifetime (1)

`SoundManager.h:53-70 CEffect::~dtor` first deletes `mChainedEffect`, then walks the static `mFirstEffect` list and unlinks `this` either by changing the predecessor's `mNextEffect` or replacing the head. The named retail body at `0x004E0820` is a scalar-deleting wrapper that contains the chain delete/unlink shape and conditionally frees the allocation (`W007/adversarial/B05.md:56-63`). It is a bounded `SOURCE_ANALOG`, not the standalone source destructor identity.

### Shared sound debug/accessor surface (14)

- `SoundManager.h:164` copies `Sound manager`; line 166 returns true. Both belong to the source debug menu.
- Lines 222 and 224 return the active logical-event count and list head. Retail independently recovers those fields at manager `+0x08` and `+0x0C`, plus the 256-event pool (`csoundmanager-shared-semantics-2026-08-11.md:56-68`), without selecting these exact accessors.
- Lines 231, 233, and 235 read the sample-list head, read initialization state, and replace the sample-list head. They are simple state accessors, not sample creation/deletion policy.
- Line 237 returns global sound master volume. Lines 240-244 read/write game and menu category volumes. The source's line-243 getter is deliberately recorded verbatim: `GetMenuSoundsMasterVolume` returns `mGameSoundsMasterVolume`, while its setter writes `mMenuSoundsMasterVolume`. Whether Steam inherited, fixed, or bypassed that wrong-field read remains unresolved.
- Lines 247-248 return the radio- and HUD-message category volumes.

The current name table and C1 closure contain no supported same-owner/leaf targets for these 21 source-only keys. The negative search included the promoted `CMusic`, `CPCMusic`, `CSoundManager`, and `CPCSoundManager` semantic tables; only the exact LoadSampleFromBuffer stub and the bounded CEffect deleting wrapper receive VAs.

## Retail classification result

| Classification | Count | Meaning |
| --- | ---: | --- |
| `SOURCE_EXACT` | 1 | `pcsoundmanager.h:58` exact retail null stub at `0x00517290`. |
| `SOURCE_ANALOG` | 1 | `SoundManager.h:53` bounded scalar-deleting wrapper at `0x004E0820`; not standalone destructor identity. |
| `NO_MATCH_FOUND` | 21 | Current instruments select no supported exact/analog target; this is not binary absence. |

The 23 stable keys are unique. Their two populated VAs are distinct and present in both the 8,329-row current name table and the 8,136-row C1 closure. Canonical `source-crosswalk/crosswalk.tsv` is not edited by this wave.

## Cheapest falsifiers

1. Recover CPCMusic vtable slot 8's exact target VA and body placement; this can upgrade the `DeviceUpdateStatus` key without changing its semantic no-op result.
2. Trace the released callers/inlining of `GetAvailableChannels`; determine whether the retail path returns 64, the capability-derived count, or no standalone value.
3. Isolate a non-deleting `CEffect` destructor body or prove the scalar wrapper is the sole emitted form before any exact promotion.
4. Trace the menu-category getter's retail field read before porting or rejecting the source wrong-field behavior.
5. For each remaining accessor, an owner-qualified body or caller inline with matching field/ABI is sufficient; name similarity alone is not.
