# FEPLanguageTest.cpp - Function Analysis

## Overview

**Class:** `CFEPLanguageTest` (RTTI: `.?AVCFEPLanguageTest@@` in type descriptor at `0x00629b48`)

This is a developer/debug FrontEnd page that renders a "LANGUAGE TEST" UI showing translation table fields (source file, string id, source text, translated text, sample).

Note:
- This page was previously mis-attributed as `CFEPMultiplayerStart` due to a vtable-address mix-up. Corrected 2026-02-13 via RTTI CompleteObjectLocator inspection.

## Identified Functions

| Address | Name | Role | Notes |
|---------|------|------|------|
| `0x0051bfa0` | `CFEPLanguageTest__Init` | vtable | Zeroes fields at `this+0x08/+0x10/+0x14/+0x18`, returns `1` |
| `0x0051bfc0` | `CFEPLanguageTest__Shutdown` | vtable | Releases sample at `this+0x14` (if any), clears `this+0x18` |
| `0x0051c090` | `CFEPLanguageTest__ButtonPressed` | vtable | Handles nav/back/scroll buttons and analog scroll |
| `0x0051ae50` | `CFEPLanguageTest__RenderPreCommon` | vtable | Thin wrapper around `FUN_004679e0` (fixed color `0x3fffffff`) |
| `0x0051c280` | `CFEPLanguageTest__Render` | vtable | Renders the language test table and current selection |
| `0x0051bfe0` | `CFEPLanguageTest__PlaySound` | helper | Builds `messagebox/<lang>.wav` and plays sample for current row |

## Vtable Analysis (0x005db7e0)

RTTI CompleteObjectLocator:
- `0x005db7dc` -> `0x006136f0`
- `0x006136f0 + 0x0c` -> type descriptor `0x00629b48` (`.?AVCFEPLanguageTest@@`)

Primary vtable at `0x005db7e0`:

| Slot | Address | Function | Notes |
|------|---------|----------|-------|
| 0 | `0x0051bfa0` | `CFEPLanguageTest__Init` | Returns `1` |
| 1 | `0x0051bfc0` | `CFEPLanguageTest__Shutdown` | Clears `this+0x14/+0x18` |
| 2 | `0x00452b60` | (inherited) | (no function object mapping here) |
| 3 | `0x0051c090` | `CFEPLanguageTest__ButtonPressed` | Button handler |
| 4 | `0x0051ae50` | `CFEPLanguageTest__RenderPreCommon` | Pre-common render |
| 5 | `0x0051c280` | `CFEPLanguageTest__Render` | Main render |
| 6 | `0x00464b10` | (inherited) | Sets `*(this+0x04) = now + 2.0` |
| 7 | `0x004014c0` | (inherited) | No function object currently |
| 8 | `0x00459990` | (inherited) | No function object currently |

## Notes

- The `ButtonPressed` handler uses button codes like `0x2a/0x2b` (nav), `0x2c` (play sample), `0x2e` (back), and `0x26/0x27` (analog scroll).
- `Render` draws column labels (String, Source File, String ID, Source Text, Translated, Sample) and displays current selection from `TEXT_DB`-related globals.
