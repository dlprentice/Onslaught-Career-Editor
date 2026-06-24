#!/usr/bin/env python3
"""Self-tests for ghidra_hud_overlay_wave410_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_hud_overlay_wave410_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=3 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0\n",
    )
    write(
        base / "metadata_after.tsv",
        "address\tname\tsignature\tcomment\tstatus\n"
        "0x00487bc0\tCHud__RenderOverlay\tvoid __thiscall CHud__RenderOverlay(void * this)\t"
        "Wave410 owner/signature correction: source/retail alignment for CHud::RenderOverlay, called from CDXEngine__PostRender with HUD singleton 0x8aa4e8 where source calls HUD.RenderOverlay. Runtime HUD overlay behavior and rebuild parity remain unproven.\tOK\n"
        "0x004879e0\tCHud__RenderOverlayForViewpoint\tvoid __thiscall CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float param_3)\t"
        "Wave410 owner/signature correction: per-viewpoint CHud overlay renderer clips the overlay marker rectangle, stores CHud fields +0x50/+0x54/+0x58, target-indicator and tactical radar overlay helpers. Runtime HUD overlay behavior and rebuild parity remain unproven.\tOK\n"
        "0x00482590\tCHud__RenderTargetIndicatorOverlay\tvoid __thiscall CHud__RenderTargetIndicatorOverlay(void * this)\t"
        "Wave410 owner/signature/comment correction: CHud target indicator overlay helper called from CHud__RenderOverlayForViewpoint, uses active/last target reader, CHud texture +0x168, and Thunderhead mesh-specific miniature path. Runtime HUD behavior and rebuild parity remain unproven.\tOK\n",
    )
    common = "static-reaudit;hud-overlay-wave410;retail-binary-evidence;"
    write(
        base / "tags_after.tsv",
        "address\tname\ttags\tstatus\n"
        f"00487bc0\tCHud__RenderOverlay\t{common}hud;overlay;source-parity;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"004879e0\tCHud__RenderOverlayForViewpoint\t{common}hud;overlay;viewpoint;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"00482590\tCHud__RenderTargetIndicatorOverlay\t{common}hud;overlay;target-indicator;owner-corrected;signature-hardened;comment-hardened\tOK\n",
    )
    write(
        base / "xrefs_after.tsv",
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "00487bc0\tCHud__RenderOverlay\t0053ed01\t0053ecc0\tCDXEngine__PostRender\tUNCONDITIONAL_CALL\n"
        "004879e0\tCHud__RenderOverlayForViewpoint\t00487c57\t00487bc0\tCHud__RenderOverlay\tUNCONDITIONAL_CALL\n"
        "00482590\tCHud__RenderTargetIndicatorOverlay\t00487b72\t004879e0\tCHud__RenderOverlayForViewpoint\tUNCONDITIONAL_CALL\n",
    )
    write(
        base / "decompile_after" / "00487bc0_CHud__RenderOverlay.c",
        "void CHud__RenderOverlay(void * this) { CGame__GetCamera(); CHud__RenderOverlayForViewpoint(this,pvVar1,number,0.0); RenderState_Set(0xe,1); D3DStateCache__SetMipFilterLinear(0); }",
    )
    write(
        base / "decompile_after" / "004879e0_CHud__RenderOverlayForViewpoint.c",
        "void CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float param_3) { CEngine__SelectViewpoint(); HudRenderState__ApplyOverlaySpriteState(); CHud__RenderTargetIndicatorOverlay((int)this); CExplosionInitThing__RenderObjectiveStatusPanel((int)this); CExplosionInitThing__RenderTacticalRadarContacts((int)this); }",
    )
    write(
        base / "decompile_after" / "00482590_CHud__RenderTargetIndicatorOverlay.c",
        "void CHud__RenderTargetIndicatorOverlay(void * this) { CGenericActiveReader__SetReader(); CVBufTexture__DrawSpriteEx(); s_m_thunderhead_msh_0062d304; D3DDevice__SetViewport(); CSphere__RenderAnimatedRecursive(); CSphere__GetRootSubtreeHealthIfAnyActive(0); }",
    )
    write(
        base / "outer_caller_decompile_after" / "0053ecc0_CDXEngine__PostRender.c",
        "void CDXEngine__PostRender(void * this) { CHud__RenderOverlay(&DAT_008aa4e8); CHud__PromotePendingHudComponent(&DAT_008aa4e8); }",
    )


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_missing_target_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        (base / "metadata_after.tsv").write_text(text.replace("CHud__RenderTargetIndicatorOverlay", "BadName", 1), encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("0x00482590 name expected CHud__RenderTargetIndicatorOverlay" in failure for failure in failures)


def main() -> int:
    tests = [test_good_fixture_passes, test_missing_target_fails]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
