#!/usr/bin/env python3
"""Self-tests for ghidra_hud_battleline_tail_wave412_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_hud_battleline_tail_wave412_probe as probe


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
        "0x00487d10\tCHud__RenderBattleline\tvoid __thiscall CHud__RenderBattleline(void * this, void * viewport)\t"
        "Wave412 owner/signature correction: source-aligned CHud::RenderBattleline(viewport) candidate called from CDXEngine__PostRender with HUD singleton 0x8aa4e8 and one viewport stack argument. The body copies the viewport rectangle into CHud scratch fields, draws battleline/message-box sprites, invokes CDXEngine__RenderBattleLinePulseSprites, and dispatches CDXBattleLine influence-overlay population/render when the influence map is non-empty. Static retail/source-alignment evidence only; exact source body identity, concrete CHud/BattleLine layout, runtime HUD behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488090\tCHud__RenderActiveHudComponentPass\tvoid __thiscall CHud__RenderActiveHudComponentPass(void * this)\t"
        "Wave412 owner/signature correction: CHud active component render pass called from CDXEngine__PostRender with HUD singleton 0x8aa4e8. The body checks CHud active component slot +0x1fc, applies alpha-sprite render state, calls CHudComponent__RenderPass, destroys/clears the component when its +0x64 done flag is set, and restores render state. Static retail evidence only; exact source method identity, concrete CHud/component layout, runtime overlay behavior, and rebuild parity remain unproven.\tOK\n"
        "0x004881e0\tCHud__ResolveOverlaySlotRenderMode\tint __thiscall CHud__ResolveOverlaySlotRenderMode(void * this, int slot_index)\t"
        "Wave412 owner/signature correction: CHud overlay slot render-mode helper reached by CDXBattleLine__RenderWorldSpaceOverlay, CDXCompass__Render, and CVBufTexture__UpdateDynamicOverlayTexture with HUD singleton 0x8aa4e8 and one slot_index stack argument. It reads CHud slot state at +0x34 + slot_index*4 and returns 0, 1, or CHud field +0x4c when the slot state is 2. Static retail evidence only; exact slot semantics, concrete CHud layout, runtime render behavior, and rebuild parity remain unproven.\tOK\n",
    )
    common = "static-reaudit;hud-battleline-tail-wave412;retail-binary-evidence;"
    write(
        base / "tags_after.tsv",
        "address\tname\ttags\tstatus\n"
        f"00487d10\tCHud__RenderBattleline\t{common}hud;battleline;source-parity;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"00488090\tCHud__RenderActiveHudComponentPass\t{common}hud;overlay;hud-component;owner-corrected;signature-hardened;comment-hardened\tOK\n"
        f"004881e0\tCHud__ResolveOverlaySlotRenderMode\t{common}hud;overlay;render-mode;owner-corrected;signature-hardened;comment-hardened\tOK\n",
    )
    write(
        base / "xrefs_after.tsv",
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "00487d10\tCHud__RenderBattleline\t0053ed79\t0053ecc0\tCDXEngine__PostRender\tUNCONDITIONAL_CALL\n"
        "00488090\tCHud__RenderActiveHudComponentPass\t0053ef26\t0053ecc0\tCDXEngine__PostRender\tUNCONDITIONAL_CALL\n"
        "004881e0\tCHud__ResolveOverlaySlotRenderMode\t0053d0f3\t0053cd30\tCDXBattleLine__RenderWorldSpaceOverlay\tUNCONDITIONAL_CALL\n"
        "004881e0\tCHud__ResolveOverlaySlotRenderMode\t004276b3\t00427210\tCDXCompass__Render\tUNCONDITIONAL_CALL\n"
        "004881e0\tCHud__ResolveOverlaySlotRenderMode\t004276d4\t00427210\tCDXCompass__Render\tUNCONDITIONAL_CALL\n"
        "004881e0\tCHud__ResolveOverlaySlotRenderMode\t0053c7d4\t0053c510\tCVBufTexture__UpdateDynamicOverlayTexture\tUNCONDITIONAL_CALL\n"
        "004881e0\tCHud__ResolveOverlaySlotRenderMode\t0053c7fa\t0053c510\tCVBufTexture__UpdateDynamicOverlayTexture\tUNCONDITIONAL_CALL\n"
        "004881e0\tCHud__ResolveOverlaySlotRenderMode\t0053ca01\t0053c510\tCVBufTexture__UpdateDynamicOverlayTexture\tUNCONDITIONAL_CALL\n"
        "004881e0\tCHud__ResolveOverlaySlotRenderMode\t0053ca20\t0053c510\tCVBufTexture__UpdateDynamicOverlayTexture\tUNCONDITIONAL_CALL\n",
    )
    write(
        base / "decompile_after" / "00487d10_CHud__RenderBattleline.c",
        "void CHud__RenderBattleline(void * this, void * viewport) { HudRenderState__ApplyOverlaySpriteState(); CDXEngine__RenderMessageBoxOverlay(); CDXEngine__RenderBattleLinePulseSprites(); CInfluenceMapManager__IsEmpty(); CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices(); CDXBattleLine__Render(); }",
    )
    write(
        base / "decompile_after" / "00488090_CHud__RenderActiveHudComponentPass.c",
        "void CHud__RenderActiveHudComponentPass(void * this) { CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite(); CHudComponent__RenderPass(*(void **)((int)this + 0x1fc)); *(char *)(component + 0x64); *(undefined4 *)((int)this + 0x1fc) = 0; }",
    )
    write(
        base / "decompile_after" / "004881e0_CHud__ResolveOverlaySlotRenderMode.c",
        "int CHud__ResolveOverlaySlotRenderMode(void * this, int slot_index) { int mode = *(int *)((int)this + slot_index * 4 + 0x34); if (mode == 1) return 1; if (mode == 2) return *(int *)((int)this + 0x4c); return 0; }",
    )
    write(
        base / "callsite_instructions_after.tsv",
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x0053ed79\t0x0053ed79\tBEFORE\t-2\t0x0053ed73\t0x0053ecc0\tCDXEngine__PostRender\tPUSH\tESI\t56\tFALL_THROUGH\n"
        "0x0053ed79\t0x0053ed79\tBEFORE\t-1\t0x0053ed74\t0x0053ecc0\tCDXEngine__PostRender\tMOV\tECX, 0x8aa4e8\tb9 e8 a4 8a 00\tFALL_THROUGH\n"
        "0x0053ed79\t0x0053ed79\tTARGET\t0\t0x0053ed79\t0x0053ecc0\tCDXEngine__PostRender\tCALL\t0x00487d10\te8 92 8f f4 ff\tUNCONDITIONAL_CALL\n"
        "0x0053ef26\t0x0053ef26\tBEFORE\t-1\t0x0053ef09\t0x0053ecc0\tCDXEngine__PostRender\tMOV\tECX, 0x8aa4e8\tb9 e8 a4 8a 00\tFALL_THROUGH\n"
        "0x0053ef26\t0x0053ef26\tTARGET\t0\t0x0053ef26\t0x0053ecc0\tCDXEngine__PostRender\tCALL\t0x00488090\te8 65 91 f4 ff\tUNCONDITIONAL_CALL\n",
    )
    write(
        base / "vbuf_blend_callsite_instructions_after.tsv",
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x0053d0f3\t0x0053d0f3\tBEFORE\t-2\t0x0053d0ec\t0x0053cd30\tCDXBattleLine__RenderWorldSpaceOverlay\tPUSH\t0x2\t6a 02\tFALL_THROUGH\n"
        "0x0053d0f3\t0x0053d0f3\tBEFORE\t-1\t0x0053d0ee\t0x0053cd30\tCDXBattleLine__RenderWorldSpaceOverlay\tMOV\tECX, 0x8aa4e8\tb9 e8 a4 8a 00\tFALL_THROUGH\n"
        "0x0053d0f3\t0x0053d0f3\tTARGET\t0\t0x0053d0f3\t0x0053cd30\tCDXBattleLine__RenderWorldSpaceOverlay\tCALL\t0x004881e0\te8 e8 b0 f4 ff\tUNCONDITIONAL_CALL\n"
        "0x004276b3\t0x004276b3\tBEFORE\t-2\t0x004276ad\t0x00427210\tCDXCompass__Render\tPUSH\tEBP\t55\tFALL_THROUGH\n"
        "0x004276b3\t0x004276b3\tBEFORE\t-1\t0x004276ae\t0x00427210\tCDXCompass__Render\tMOV\tECX, 0x8aa4e8\tb9 e8 a4 8a 00\tFALL_THROUGH\n"
        "0x004276b3\t0x004276b3\tTARGET\t0\t0x004276b3\t0x00427210\tCDXCompass__Render\tCALL\t0x004881e0\te8 28 0b 06 00\tUNCONDITIONAL_CALL\n"
        "0x0053c7d4\t0x0053c7d4\tBEFORE\t-2\t0x0053c7bb\t0x0053c510\tCVBufTexture__UpdateDynamicOverlayTexture\tPUSH\t0x0\t6a 00\tFALL_THROUGH\n"
        "0x0053c7d4\t0x0053c7d4\tBEFORE\t-1\t0x0053c7cf\t0x0053c510\tCVBufTexture__UpdateDynamicOverlayTexture\tMOV\tECX, 0x8aa4e8\tb9 e8 a4 8a 00\tFALL_THROUGH\n"
        "0x0053c7d4\t0x0053c7d4\tTARGET\t0\t0x0053c7d4\t0x0053c510\tCVBufTexture__UpdateDynamicOverlayTexture\tCALL\t0x004881e0\te8 07 ba f4 ff\tUNCONDITIONAL_CALL\n",
    )


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_owner_signature_regression_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CHud__RenderBattleline", "CDXEngine__RenderBattleLineAndInfluenceOverlay")
        text = text.replace(
            "int __thiscall CHud__ResolveOverlaySlotRenderMode(void * this, int slot_index)",
            "int __thiscall CVBufTexture__ResolveBlendModeSelector(void * this, int param_1, int param_2)",
        )
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("0x00487d10 name expected" in failure for failure in failures)
        assert any("0x004881e0 signature expected" in failure for failure in failures)


def main() -> int:
    tests = [test_good_fixture_passes, test_owner_signature_regression_fails]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
