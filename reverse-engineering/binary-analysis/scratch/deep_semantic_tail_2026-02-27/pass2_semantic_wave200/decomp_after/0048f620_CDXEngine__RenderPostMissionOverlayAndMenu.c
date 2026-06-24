/* address: 0x0048f620 */
/* name: CDXEngine__RenderPostMissionOverlayAndMenu */
/* signature: void CDXEngine__RenderPostMissionOverlayAndMenu(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXEngine__RenderPostMissionOverlayAndMenu(void)

{
  bool bVar1;
  int iVar2;
  short *psVar3;
  void *pvVar4;
  int iVar5;
  short *psVar6;
  int *piVar7;
  uint uVar8;
  int *extraout_ECX;
  double dVar9;
  int iStack00000004;
  float fStack00000008;
  int iStack0000000c;
  undefined4 uStack00000010;
  int iStack00000014;
  longlong lStack00000018;
  int *piStack00000020;
  float fStack00000024;
  int in_stack_0000002c;
  undefined1 *puVar10;
  float fVar11;
  int *piVar12;

  CRT__AllocaProbe();
  if (_DAT_005d856c < (float)extraout_ECX[3]) {
    piStack00000020 = extraout_ECX;
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    DAT_009c68ac = 0;
    DAT_009c690d = 1;
    DAT_009c68ad = 0;
    DAT_009c6910 = 1;
    D3DStateCache__SetState114Raw(0,1,3);
    D3DStateCache__SetState114Raw(0,2,3);
    D3DStateCache__SetMipFilterPoint(0);
    D3DStateCache__SetState114Raw(0,6,2);
    D3DStateCache__SetState114Raw(0,5,2);
    RenderState_Set(0x17,4);
    D3DStateCache__SetStateCached(0,2,2);
    D3DStateCache__SetStateCached(0,3,0);
    D3DStateCache__SetStateCached(0,1,4);
    RenderState_Set(0xf,1);
    RenderState_Set(0x18,8);
    RenderState_Set(0x1b,1);
    RenderState_Set(0xe,0);
    RenderState_Set(7,0);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    if (extraout_ECX[2] != 0) {
      RenderState_Set(0x17,8);
      D3DStateCache__SetStateCached(0,1,4);
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      CVBufTexture__DrawSpriteEx
                (0.0,0.0,0.01,(void *)extraout_ECX[4],0,0,1.0,0.0,-2.2509804,40.0,30.0,0.0,1.0,0.0,
                 1.0);
    }
    dVar9 = PtrFloatAt4__GetOrOne(&DAT_0088a0a8);
    fStack00000024 = _DAT_005db538 / (float)dVar9;
    DAT_009c68ac = 0;
    DAT_009c690d = 1;
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    RenderState_Set(0x17,8);
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    D3DStateCache__SetState114Raw(0,6,2);
    D3DStateCache__SetStateCached(0,2,2);
    D3DStateCache__SetStateCached(0,3,0);
    D3DStateCache__SetStateCached(0,1,4);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    _iStack0000000c = (longlong)ROUND((float)extraout_ECX[3] * _DAT_005dc22c);
    lStack00000018 = (longlong)ROUND((float)extraout_ECX[3] * _DAT_005dc228);
    CExplosionInitThing__CheckValueRange_852_899(0x8a9a98);
    CMessageLog__RenderPanelFrame();
    D3DStateCache__SetStateCached(0,1,4);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    RenderState_Set(0x17,4);
    if (piStack00000020[2] == 0) {
      piStack00000020[3] = (int)((float)piStack00000020[3] - fStack00000024 * _DAT_005d85c0);
      return;
    }
    if (_DAT_005d8568 <= (float)piStack00000020[3]) {
      iVar2 = CFrontEnd__ResolveLevelNameTextIdByCode(DAT_008a9ac8);
      iStack0000000c = iVar2;
      iVar2 = CExplosionInitThing__CheckValueRange_852_899(0x8a9a98);
      if (iVar2 == 0) {
        iVar2 = 0;
        do {
          psVar3 = CText__GetStringByIdAfter(&g_Text,iStack0000000c,iVar2);
          piVar7 = &stack0x0000002c;
          psVar6 = psVar3;
          pvVar4 = CPlatform__Font(&DAT_0088a0a8,1);
          CDXFont__GetTextExtent(pvVar4,psVar6,piVar7);
          fVar11 = 525.0;
          puVar10 = &stack0x00000234;
          CPlatform__Font(&DAT_0088a0a8,1);
          iVar5 = CFEPLanguageTest__Helper_00465a20(puVar10,psVar3,fVar11);
          if (0 < iVar5) {
            psVar6 = (short *)&stack0x00000234;
            do {
              piVar7 = (int *)&stack0x00000024;
              psVar3 = psVar6;
              pvVar4 = CPlatform__Font(&DAT_0088a0a8,1);
              CDXFont__GetTextExtent(pvVar4,psVar3,piVar7);
              CPlatform__Font(&DAT_0088a0a8,1);
              CDXEngine__DrawTextScaledWithShadow();
              psVar6 = psVar6 + 100;
              iVar5 = iVar5 + -1;
            } while (iVar5 != 0);
          }
          iVar2 = iVar2 + 1;
        } while (iVar2 < 9);
      }
      psVar6 = CText__GetStringById(&g_Text,-0xbdec041);
      CUnitAI__Helper_0055e64e(&stack0x00000034,psVar6);
      fVar11 = 179.0;
      iVar2 = CExplosionInitThing__CheckValueRange_852_899(0x8a9a98);
      if (iVar2 != 0) {
        fVar11 = 100.0;
      }
      iVar2 = 0;
      bVar1 = false;
      piVar7 = &DAT_008a9ae4;
      iVar5 = 10;
      do {
        if (*piVar7 != 0) {
          bVar1 = true;
        }
        piVar7 = piVar7 + 2;
        iVar5 = iVar5 + -1;
      } while (iVar5 != 0);
      if (bVar1) {
        CPlatform__Font(&DAT_0088a0a8,1);
        CDXEngine__DrawTextScaledWithShadow();
      }
      fStack00000024 = fVar11 + _DAT_005d8bc0;
      iStack00000014 = 0;
      fStack00000008 = 1.0;
      if ((DAT_008a9ac8 == 0x263) && (g_LanguageIndex == 2)) {
        fStack00000008 = 0.97;
      }
      iStack00000004 = 0;
      do {
        piVar7 = &DAT_008a9ae4;
        iStack0000000c = 10;
        fVar11 = fStack00000024;
        do {
          if (*piVar7 != 0) {
            psVar6 = CText__GetStringById(&g_Text,piVar7[1]);
            piVar12 = &stack0x0000002c;
            pvVar4 = CPlatform__Font(&DAT_0088a0a8,1);
            CDXFont__GetTextExtent(pvVar4,psVar6,piVar12);
            if (iVar2 < in_stack_0000002c) {
              iStack00000014 = in_stack_0000002c;
              iVar2 = in_stack_0000002c;
            }
            if (iStack00000004 == 0) {
              if (fStack00000008 < _DAT_005d8cc4) goto LAB_0048fbff;
LAB_0048fce0:
              CPlatform__Font(&DAT_0088a0a8,1);
              CDXEngine__DrawTextScaledWithShadow();
            }
            else {
              lStack00000018._2_6_ = (uint6)((ulonglong)lStack00000018 >> 0x10) & 0xffffffff0000;
              lStack00000018 = CONCAT62(lStack00000018._2_6_,0x2510);
              if (*piVar7 == 1) {
                lStack00000018 = CONCAT62(lStack00000018._2_6_,0x250c);
              }
              if (_DAT_005d8cc4 <= fStack00000008) goto LAB_0048fce0;
LAB_0048fbff:
              CPlatform__Font(&DAT_0088a0a8,1);
              CDXFont__DrawTextScaled();
            }
            fVar11 = fStack00000008 * _DAT_005d8bc0 + fVar11;
          }
          piVar7 = piVar7 + 2;
          iStack0000000c = iStack0000000c + -1;
        } while (iStack0000000c != 0);
        iStack00000004 = iStack00000004 + 1;
      } while (iStack00000004 < 2);
      fVar11 = fVar11 + _DAT_005d8bc0;
      bVar1 = false;
      piVar7 = &DAT_008a9b34;
      iVar2 = 10;
      do {
        if (*piVar7 != 0) {
          bVar1 = true;
        }
        piVar7 = piVar7 + 2;
        iVar2 = iVar2 + -1;
      } while (iVar2 != 0);
      if (bVar1) {
        psVar6 = CText__GetStringById(&g_Text,-0x3b504359);
        CUnitAI__Helper_0055e64e(&stack0x00000034,psVar6);
        CPlatform__Font(&DAT_0088a0a8,1);
        CDXEngine__DrawTextScaledWithShadow();
        fStack00000024 = fVar11 + _DAT_005d8bc0;
        iVar2 = 0;
        iStack00000004 = 0;
        iStack00000014 = 0;
        do {
          piVar7 = &DAT_008a9b34;
          iStack0000000c = 10;
          do {
            if (*piVar7 != 0) {
              psVar6 = CText__GetStringById(&g_Text,piVar7[1]);
              piVar12 = &stack0x0000002c;
              pvVar4 = CPlatform__Font(&DAT_0088a0a8,1);
              CDXFont__GetTextExtent(pvVar4,psVar6,piVar12);
              if (iVar2 < in_stack_0000002c) {
                iStack00000014 = in_stack_0000002c;
                iVar2 = in_stack_0000002c;
              }
              if (iStack00000004 != 0) {
                lStack00000018._2_6_ = (uint6)((ulonglong)lStack00000018 >> 0x10) & 0xffffffff0000;
                lStack00000018 = CONCAT62(lStack00000018._2_6_,0x2510);
                if (*piVar7 == 1) {
                  lStack00000018 = CONCAT62(lStack00000018._2_6_,0x250c);
                }
              }
              CPlatform__Font(&DAT_0088a0a8,1);
              CDXEngine__DrawTextScaledWithShadow();
            }
            piVar7 = piVar7 + 2;
            iStack0000000c = iStack0000000c + -1;
          } while (iStack0000000c != 0);
          iStack00000004 = iStack00000004 + 1;
        } while (iStack00000004 < 2);
      }
      iStack0000000c = 0;
      if (DAT_0089be28 != 0) {
        DAT_0089be28 = 0;
        (**(code **)(*piStack00000020 + 0xc))();
      }
      if (DAT_00807418 != (void *)0x0) {
        CVBufTexture__DrawSpriteEx
                  (24.0,454.0,0.001,DAT_00807418,4,0,1.0,3.1415927,-NAN,1.0,1.0,0.0,1.0,0.0,1.0);
      }
      uVar8 = Input__GetClickStateInRect(0.0,400.0,200.0,480.0);
      if ((char)uVar8 != '\0') {
        (**(code **)(*piStack00000020 + 0xc))();
      }
      CDXEngine__Helper_00523a70();
    }
    else {
      fVar11 = fStack00000024 * _DAT_005d85c0 + (float)piStack00000020[3];
      piStack00000020[3] = (int)fVar11;
      if (_DAT_005d8568 < fVar11) {
        piStack00000020[3] = 0x3f800000;
        return;
      }
    }
  }
  return;
}
