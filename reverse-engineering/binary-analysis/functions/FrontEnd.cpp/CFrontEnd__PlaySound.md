# CFrontEnd__PlaySound

> Address: `0x00468770` | Source: `references/Onslaught/FrontEnd.cpp` | Line: ~1603

## Summary

Plays standard frontend UI sounds (move/select/back).

Source-parity with:

```cpp
void CFrontEnd::PlaySound(EFrontEndSound sound)
```

Retail `BEA.exe` appears to implement this as a small helper that takes only the `sound` id (no `this` usage).

## Signature

```c
void CFrontEnd__PlaySound(int sound);
```

## Sound IDs

| `sound` | Name String |
|---------|-------------|
| 0 | `"Front End Move"` |
| 1 | `"Front End Select"` |
| 2 | `"Front End Back"` |
| other | `""` (no sound) |

## Notes

- Internally resolves an effect by name (via `SOUND.GetEffectByName`) and plays it (via `SOUND.PlayEffect`).
- This helper is called from many FEP page handlers.

