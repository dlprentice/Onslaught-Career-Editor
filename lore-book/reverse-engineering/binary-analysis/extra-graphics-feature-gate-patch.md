# Extra Graphics Feature Gate Patch

## Summary

Retail `BEA.exe` registers the tweak `GEFORCE_FX_POWER` with a default value of `0`.
When modern GPUs do not match `cardid.txt` vendor/device rules, that default can leave the
"extra graphical features" path unavailable.

A deterministic file patch can change the default to `1` directly in `BEA.exe`.

## Patch

- Target binary: retail Steam `BEA.exe`
- SHA256 (known target): `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- VA: `0x004CDD40`
- File offset: `0x0CDD40`
- Original bytes: `6A 00` (`push 0`)
- Patched bytes: `6A 01` (`push 1`)

## Related Patch: Ignore cardid.txt Overrides

To ignore `cardid.txt` vendor/device matching and always use executable defaults:

- VA: `0x0052AF3F`
- File offset: `0x12AF3F`
- Original bytes: `E8 9C D7 FF FF` (`call 0x005286E0`)
- Patched bytes: `90 90 90 90 90` (NOP ×5)

This bypasses the startup call into `CD3DApplication__LoadCardIdAndApplyVendorTweaks`.

## Why This Location

Disassembly at `0x004CDD40` shows tweak registration for string `GEFORCE_FX_POWER`
(string VA `0x00631174`) through `CD3DApplication` tweak-registration path (`0x00528AA0`).
The immediate `push` value becomes the default stored for that tweak object.

So:

- `push 0` => default disabled
- `push 1` => default enabled

This changes default behavior without requiring `cardid.txt` vendor/device matching.

## Related Retail Flow

- `CD3DApplication__LoadCardIdAndApplyVendorTweaks` at `0x005286E0` reads `cardid.txt`
  and applies named tweak overrides when vendor/device/version checks pass.
- Keeping that flow intact while changing only the default avoids broad side effects from
  bypassing card/vendor checks globally.

## Baseline Tweak Defaults (Retail Registration Sites)

The key graphics-related tweak defaults are registered in code and already default to enabled-friendly values in retail:

- `LANDSCAPE_LIGHTING` at `0x00544692`: `push 1`
- `EXTRA_GEFORCE_FX_FEATURES` at `0x0054FB62`: `push 1`
- `GEFORCE_PARTICLE_FOG` at `0x0054FB92`: `push 1`
- `SRT_ENABLE` at `0x00551E92`: `push 1`
- `DISABLE_SNOW` at `0x00554F52`: `push 0` (snow not forcibly disabled)

The outlier relevant to feature gating is `GEFORCE_FX_POWER` at `0x004CDD40`, which defaults to `0` unless patched.

## Scope / Side Effects

- Intended effect: extra graphics feature gate defaults to enabled.
- If the cardid-load bypass patch is not applied, `cardid.txt` still can override tweak values when a matching rule applies.
- Rollback: restore `BEA.exe.original.backup` or write back `6A 00` at `0x0CDD40`.
