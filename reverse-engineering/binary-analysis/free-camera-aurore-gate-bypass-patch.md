# Free-camera Aurore-gate bypass

Status: experimental copied-profile patch with bounded static and runtime evidence.

The patch catalog is the byte-definition authority. This note records why the rows exist and what has actually been observed.

## Toggle gate

`CGame__ReceiveButtonAction` at `0x0046F7E0` gates `BUTTON_TOGGLE_FREE_CAMERA` behind `IsCheatActive(4)`.

| Item | Value |
| --- | --- |
| Patch id | `free_camera_aurore_gate_bypass` |
| Gate branch VA / file offset | `0x0046F83C` / `0x06F83C` |
| Clean bytes | `0F 84 58 02 00 00` |
| Patched bytes | `90 90 90 90 90 90` |

In a controlled copied-profile comparison, the clean branch received button `1` from scoped `F` input but did not enter `CGame__ToggleFreeCameraOn`. The patched branch received two scoped `F` inputs, entered the toggle, set the free-camera pointer on the first transition, and restored the original camera on the second. This establishes the gate effect in that context, not general camera safety.

## Keyboard companion rows

Eight mutually exclusive experimental variants redirect the same function prologue at VA `0x0041A980` / file offset `0x01A980` to a cave at VA `0x005A3A15` / file offset `0x1A3A15`. The cave is clean `CC` padding in the pinned Steam specimen; the earlier candidate at `0x005A3955` was rejected because it overlaps community widescreen/FOV cave space.

| Variant | Input button | Camera button | Observed scoped hits |
| --- | ---: | ---: | ---: |
| forward | `31` | `38` | 20 |
| backward | `32` | `39` | 21 |
| strafe left | `29` | `40` | 32 |
| strafe right | `30` | `41` | 31 |
| yaw left | `25` | `36` | 33 |
| yaw right | `27` | `37` | 32 |
| pitch up | `26` | `34` | 31 |
| pitch down | `28` | `35` | 33 |

Each accepted copied-runtime observation read back the full hook and cave bytes, saw the mapped post-cave button and camera handler in the scoped `Q` window, and saw position or orientation deltas appropriate to that variant. Adjacent wait windows did not show the source-button cave path or interpolation deltas. These are bounded one-key observations; they do not establish a complete control scheme.

Separate `O` diagnostics with the forward variant did not reach the expected pause-button query or pause/unpause dispatch. The pause mapping therefore remains a separate patch and evidence surface.

## Boundary

The evidence covers toggle on/off and one controlled movement or orientation path per companion row. It does not prove arbitrary key reachability, analog input, control feel, broad gameplay safety, rendering parity, online behavior, or rebuild parity. Every row remains experimental, mutually constrained by the catalog, and valid only for app-owned copied executables. Never apply it to the installed game or the original clean backup.
