#!/usr/bin/env python3
"""Self-tests for ghidra_hud_overlay_helpers_wave411_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_hud_overlay_helpers_wave411_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=9 created=0 would_create=0 renamed=0 would_rename=9 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=9 skipped=0 created=0 would_create=0 renamed=9 would_rename=0 missing=0 bad=0\n",
    )
    write(
        base / "metadata_after.tsv",
        "address\tname\tsignature\tcomment\tstatus\n"
        "0x00483530\tCHud__RenderControllerSlotStatusPanel\tvoid __thiscall CHud__RenderControllerSlotStatusPanel(void * this)\t"
        "Wave411 owner/signature correction: CHud overlay helper for the controller slot status panel, called from CHud__RenderOverlayForViewpoint. It animates HUD fields +0x68/+0x94/+0x98/+0xac, calls CHud__RenderSegmentedMeterBar, formats timer/status text, and draws it with CDXFont. Static retail evidence only; exact source body identity, concrete CHud layout, runtime HUD behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00484340\tCHud__RenderTargetMarkers3D\tvoid __thiscall CHud__RenderTargetMarkers3D(void * this)\t"
        "Wave411 owner/signature correction: CHud overlay helper for 3D target marker sprites, called from CHud__RenderOverlayForViewpoint. It uses CHud fields +0x50/+0x54/+0x58, applies overlay sprite state, reads CBattleEngine__GetInterpolatedAutoAimPos, and draws target marker textures. Static retail evidence only; exact source body identity, concrete CHud/BattleEngine layout, runtime HUD behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00484c50\tCHud__RenderTacticalRadarContacts\tvoid __thiscall CHud__RenderTacticalRadarContacts(void * this)\t"
        "Wave411 owner/signature correction: CHud tactical radar overlay helper called from CHud__RenderOverlayForViewpoint. It partitions visible units into temporary pointer sets, projects nearby contacts using the active BattleEngine orientation, selects marker textures through CHud__SelectMarkerTextureIndexByUnitFlags, draws markers through HudOverlay__DrawSpriteQuad, and clears temporary sets. Static retail evidence only; exact source body identity, concrete unit/radar semantics, runtime HUD behavior, and rebuild parity remain unproven.\tOK\n"
        "0x004857e0\tHudOverlay__DrawSpriteQuad\tvoid __cdecl HudOverlay__DrawSpriteQuad(float x, float y, void * texture, float argb_tint_bits)\t"
        "Wave411 signature/comment correction: owner-neutral HUD overlay sprite helper called repeatedly by CHud__RenderTacticalRadarContacts. It forwards x/y, texture, and argb_tint_bits to CVBufTexture__DrawSpriteEx with fixed depth 0.011 and fixed sprite sizing parameters. Static retail evidence only; exact tint semantics remain unproven.\tOK\n"
        "0x00485830\tCHud__SelectMarkerTextureIndexByUnitFlags\tint __thiscall CHud__SelectMarkerTextureIndexByUnitFlags(void * this, void * unit)\t"
        "Wave411 owner/signature correction: CHud tactical marker texture selector with one stack argument (unit; RET 0x4). It reads unit flags at +0x34 and returns one of CHud texture slots +0x1a0/+0x1a4/+0x1a8. Static retail evidence only; exact unit layout, texture semantics, and runtime HUD behavior remain unproven.\tOK\n"
        "0x004858d0\tCHud__RenderObjectiveProgressGaugeAndHeadingNeedle\tvoid __thiscall CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(void * this)\t"
        "Wave411 owner/signature correction: CHud overlay helper for the objective progress gauge and heading needle, called from CHud__RenderOverlayForViewpoint. It applies overlay render state, draws gauge sprites, reads CBattleEngine__GetWeaponCharge, and rotates a heading needle from CBattleEngine__GetInterpolatedEulerOrientation. Static retail evidence only; exact source body identity, concrete CHud/BattleEngine layout, runtime HUD behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00485d50\tCHud__RenderObjectiveStatusPanel\tvoid __thiscall CHud__RenderObjectiveStatusPanel(void * this)\t"
        "Wave411 owner/signature correction: CHud overlay helper for objective and weapon status panel, called from CHud__RenderOverlayForViewpoint. It checks CBattleEngine__CountFlag9CBySelectionMode, chooses weapon icons/names through CBattleEngine__GetWeaponIconName and CBattleEngine__GetWeaponName, handles multiplayer lives via CGame__GetPlayerLives, and draws objective text lines. Static retail evidence only; exact source body identity, concrete text-slot semantics, runtime HUD behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00486940\tCHud__RenderObjectiveSlotFillPanel\tvoid __thiscall CHud__RenderObjectiveSlotFillPanel(void * this)\t"
        "Wave411 owner/signature correction: CHud overlay helper for weapon energy/ammo slot fill panel, called from CHud__RenderOverlayForViewpoint. It branches on CBattleEngine__IsEnergyWeapon, reads CBattleEngine__GetWeaponAmmoPercentage, CBattleEngine__IsWeaponOverheated, and CBattleEngine__GetWeaponAmmoCount, then draws fill sprites or ammo text. Static retail evidence only; exact source body identity, concrete ammo semantics, runtime HUD behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00486e00\tCHud__RenderWorldTargetSprites\tvoid __thiscall CHud__RenderWorldTargetSprites(void * this)\t"
        "Wave411 owner/signature correction: CHud overlay helper for world-space target and lock sprites, called from CHud__RenderOverlayForViewpoint. It uses CHud fields +0x50/+0x54/+0x58, applies overlay state, projects target/lock info, reads CLockInfo__GetLockPercentage, and uses CUnitAI__GetWorldPositionForTargeting for unit markers. Static retail evidence only; exact source body identity, concrete list layouts, runtime HUD behavior, and rebuild parity remain unproven.\tOK\n",
    )
    common = "static-reaudit;hud-overlay-helpers-wave411;retail-binary-evidence;"
    write(
        base / "tags_after.tsv",
        "address\tname\ttags\tstatus\n"
        f"00483530\tCHud__RenderControllerSlotStatusPanel\t{common}hud;overlay;controller-status;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"00484340\tCHud__RenderTargetMarkers3D\t{common}hud;overlay;target-markers;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"00484c50\tCHud__RenderTacticalRadarContacts\t{common}hud;overlay;tactical-radar;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"004857e0\tHudOverlay__DrawSpriteQuad\t{common}hud;overlay;sprite-helper;signature-hardened;comment-hardened\tOK\n"
        f"00485830\tCHud__SelectMarkerTextureIndexByUnitFlags\t{common}hud;overlay;marker-texture;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"004858d0\tCHud__RenderObjectiveProgressGaugeAndHeadingNeedle\t{common}hud;overlay;objective;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"00485d50\tCHud__RenderObjectiveStatusPanel\t{common}hud;overlay;objective;weapon-status;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"00486940\tCHud__RenderObjectiveSlotFillPanel\t{common}hud;overlay;objective;weapon-status;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"00486e00\tCHud__RenderWorldTargetSprites\t{common}hud;overlay;world-targets;owner-corrected;signature-hardened;comment-hardened\tOK\n",
    )
    write(
        base / "xrefs_after.tsv",
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "00483530\tCHud__RenderControllerSlotStatusPanel\t00487b8a\t004879e0\tCHud__RenderOverlayForViewpoint\tUNCONDITIONAL_CALL\n"
        "00484340\tCHud__RenderTargetMarkers3D\t00487b91\t004879e0\tCHud__RenderOverlayForViewpoint\tUNCONDITIONAL_CALL\n"
        "00484c50\tCHud__RenderTacticalRadarContacts\t00487bb2\t004879e0\tCHud__RenderOverlayForViewpoint\tUNCONDITIONAL_CALL\n"
        "004858d0\tCHud__RenderObjectiveProgressGaugeAndHeadingNeedle\t00487b98\t004879e0\tCHud__RenderOverlayForViewpoint\tUNCONDITIONAL_CALL\n"
        "00485d50\tCHud__RenderObjectiveStatusPanel\t00487b9f\t004879e0\tCHud__RenderOverlayForViewpoint\tUNCONDITIONAL_CALL\n"
        "00486940\tCHud__RenderObjectiveSlotFillPanel\t00487ba6\t004879e0\tCHud__RenderOverlayForViewpoint\tUNCONDITIONAL_CALL\n"
        "00486e00\tCHud__RenderWorldTargetSprites\t00487b6b\t004879e0\tCHud__RenderOverlayForViewpoint\tUNCONDITIONAL_CALL\n"
        + "".join(
            f"004857e0\tHudOverlay__DrawSpriteQuad\t00485{i}00\t00484c50\tCHud__RenderTacticalRadarContacts\tUNCONDITIONAL_CALL\n"
            for i in range(7)
        )
        + "".join(
            f"00485830\tCHud__SelectMarkerTextureIndexByUnitFlags\t00484{i}18\t00484c50\tCHud__RenderTacticalRadarContacts\tUNCONDITIONAL_CALL\n"
            for i in range(4)
        ),
    )
    decompiles = {
        "00483530_CHud__RenderControllerSlotStatusPanel.c": "void CHud__RenderControllerSlotStatusPanel(void * this) { CPlatform__Font(); CDXFont__DrawTextDynamic(); CHud__RenderSegmentedMeterBar(this,0,0,0,0,0); GetSlotTimerValueByMode(); }",
        "00484340_CHud__RenderTargetMarkers3D.c": "void CHud__RenderTargetMarkers3D(void * this) { HudRenderState__ApplyOverlaySpriteState(); CDXBattleLine__RenderWorldSpaceOverlay(); CBattleEngine__GetInterpolatedAutoAimPos(); CVBufTexture__DrawSpriteEx(); }",
        "00484c50_CHud__RenderTacticalRadarContacts.c": "void CHud__RenderTacticalRadarContacts(void * this) { HudRenderState__ApplyOverlaySpriteState(); CGame__IsMultiplayer(); CBattleEngine__GetInterpolatedEulerOrientation(); CHud__SelectMarkerTextureIndexByUnitFlags(this, unit); HudOverlay__DrawSpriteQuad(x,y,texture,argb); CSPtrSet__Clear(); }",
        "004857e0_HudOverlay__DrawSpriteQuad.c": "void HudOverlay__DrawSpriteQuad(float x,float y,void * texture,float argb_tint_bits) { CVBufTexture__DrawSpriteEx(x,y,0.011,texture,4,0,1.0,0.0,argb_tint_bits,1.0,1.0,0.0,1.0,0.0,1.0); }",
        "00485830_CHud__SelectMarkerTextureIndexByUnitFlags.c": "int CHud__SelectMarkerTextureIndexByUnitFlags(void * this, void * unit) { *(uint *)((int)unit + 0x34); return *(int *)((int)this + 0x1a0) + *(int *)((int)this + 0x1a4) + *(int *)((int)this + 0x1a8); }",
        "004858d0_CHud__RenderObjectiveProgressGaugeAndHeadingNeedle.c": "void CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(void * this) { HudRenderState__ApplyOverlaySpriteState(); CBattleEngine__GetWeaponCharge(); CBattleEngine__GetInterpolatedEulerOrientation(); CVBufTexture__DrawSpriteEx(); }",
        "00485d50_CHud__RenderObjectiveStatusPanel.c": "void CHud__RenderObjectiveStatusPanel(void * this) { HudRenderState__ApplyOverlaySpriteState(); CBattleEngine__CountFlag9CBySelectionMode(); CBattleEngine__GetWeaponIconName(); CBattleEngine__GetWeaponName(); CGame__GetPlayerLives(); CDXFont__DrawTextDynamic(); }",
        "00486940_CHud__RenderObjectiveSlotFillPanel.c": "void CHud__RenderObjectiveSlotFillPanel(void * this) { HudRenderState__ApplyOverlaySpriteState(); CBattleEngine__IsEnergyWeapon(); CBattleEngine__GetWeaponAmmoPercentage(); CBattleEngine__IsWeaponOverheated(); CBattleEngine__GetWeaponAmmoCount(); }",
        "00486e00_CHud__RenderWorldTargetSprites.c": "void CHud__RenderWorldTargetSprites(void * this) { HudRenderState__ApplyOverlaySpriteState(); CUnitAI__GetWorldPositionForTargeting(); CLockInfo__GetLockPercentage(); CVBufTexture__DrawSpriteEx(); CDXEngine__PushTransformState(); }",
    }
    for name, text in decompiles.items():
        write(base / "decompile_after" / name, text)
    write(
        base / "caller_decompile_after" / "004879e0_CHud__RenderOverlayForViewpoint.c",
        "void CHud__RenderOverlayForViewpoint(void * this) { CHud__RenderWorldTargetSprites(this); CHud__RenderControllerSlotStatusPanel(this); CHud__RenderTargetMarkers3D(this); CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(this); CHud__RenderObjectiveStatusPanel(this); CHud__RenderObjectiveSlotFillPanel(this); CHud__RenderTacticalRadarContacts(this); }",
    )


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_signature_regression_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        bad = "int __thiscall CHud__SelectMarkerTextureIndexByUnitFlags(void * this, void * unit, int param_2)"
        text = text.replace("int __thiscall CHud__SelectMarkerTextureIndexByUnitFlags(void * this, void * unit)", bad)
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("0x00485830 signature expected" in failure for failure in failures)


def main() -> int:
    tests = [test_good_fixture_passes, test_signature_regression_fails]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
