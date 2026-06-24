/* address: 0x00472f10 */
/* name: CDXEngine__Helper_00472f10 */
/* signature: void __fastcall CDXEngine__Helper_00472f10(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXEngine__Helper_00472f10(void *param_1)

{
  longlong lVar1;
  short sVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  short *psVar6;
  void *pvVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  char *text_ascii;
  void *unaff_ESI;
  float fVar11;
  float fVar12;
  float fVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  uint uVar16;
  undefined4 uVar17;
  undefined4 uVar18;
  undefined4 uVar19;
  uint local_9c;
  undefined8 local_90;
  float local_88;
  char local_81;
  short local_80 [64];

  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  if (*(char *)((int)param_1 + 0x14) == '\0') {
    iVar9 = *(int *)((int)param_1 + 0x10) + -0x10;
    *(int *)((int)param_1 + 0x10) = iVar9;
    if (iVar9 < 0) {
      *(undefined4 *)((int)param_1 + 0x10) = 0;
    }
LAB_00472f59:
    iVar9 = *(int *)((int)param_1 + 0x10);
  }
  else {
    iVar9 = *(int *)((int)param_1 + 0x10) + 0x10;
    *(int *)((int)param_1 + 0x10) = iVar9;
    if (0xff < iVar9) {
      *(undefined4 *)((int)param_1 + 0x10) = 0xff;
      goto LAB_00472f59;
    }
  }
  if (iVar9 != 0xff) {
    piVar3 = CGame__GetCamera(&DAT_008a9a98,0);
    (**(code **)(*piVar3 + 0x1c))();
  }
  local_88 = *(float *)((int)param_1 + 0x10);
  if (local_88 != 0.0) {
    local_90 = (longlong)ROUND((float)(int)local_88 * _DAT_005d8bc4);
    uVar10 = (int)local_90 << 0x18 | 0xffffff;
    if (*(int *)((int)param_1 + 0xc) != 0) {
      DAT_009c68ac = 0;
      DAT_009c690d = 1;
      iVar9 = *(int *)(*(int *)((int)param_1 + 0xc) + 0xac);
      iVar4 = PLATFORM__GetWindowWidth();
      sVar2 = *(short *)(*(int *)((int)param_1 + 0xc) + 0xb0);
      iVar5 = PLATFORM__GetWindowHeight();
      fVar11 = (float)(iVar5 / 2 - (int)sVar2 / 2);
      local_88 = (float)(iVar4 / 2 - iVar9 / 2);
      CDXSurf__RenderSurface
                (local_88,fVar11,0x3a83126f,*(undefined4 *)((int)param_1 + 0xc),uVar10,0x3f800000,
                 0x3f800000,0,0,0x3f800000,0);
      text_ascii = s_Movement_0062c65c;
      iVar9 = 0;
      do {
        piVar3 = (int *)&local_90;
        psVar6 = Text__AsciiToWideScratch(text_ascii);
        pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
        CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
        uVar18 = 0;
        uVar17 = 0;
        local_90 = CONCAT44(local_90._4_4_ / 2,(int)local_90 / 2);
        if (*(int *)((int)&DAT_0062c854 + iVar9) == 0) {
          psVar6 = Text__AsciiToWideScratch(text_ascii);
          iVar4 = *(int *)((int)&DAT_0062c838 + iVar9);
          fVar12 = ((float)*(int *)((int)&DAT_0062c81c + iVar9) + local_88) - (float)(int)local_90;
        }
        else {
          psVar6 = Text__AsciiToWideScratch(text_ascii);
          iVar4 = *(int *)((int)&DAT_0062c838 + iVar9);
          fVar12 = (float)*(int *)((int)&DAT_0062c81c + iVar9) + local_88;
        }
        fVar13 = (float)iVar4 + fVar11;
        uVar15 = 0x3f000000;
        uVar14 = 0x3f000000;
        uVar19 = 0x3dcccccd;
        uVar16 = uVar10;
        CPlatform__Font(&DAT_0088a0a8,0);
        CDXFont__DrawTextScaled(fVar12,fVar13,uVar19,uVar14,uVar15,uVar16,psVar6,uVar17,uVar18);
        text_ascii = text_ascii + 0x40;
        iVar9 = iVar9 + 4;
      } while ((int)text_ascii < 0x62c81c);
    }
  }
  if (*(char *)((int)param_1 + 0x1c) == '\0') {
    iVar9 = *(int *)((int)param_1 + 0x18) + -0x20;
    *(int *)((int)param_1 + 0x18) = iVar9;
    if (iVar9 < 0) {
      *(undefined4 *)((int)param_1 + 0x18) = 0;
    }
  }
  else {
    iVar9 = *(int *)((int)param_1 + 0x18) + 0x20;
    *(int *)((int)param_1 + 0x18) = iVar9;
    if (0xff < iVar9) {
      *(undefined4 *)((int)param_1 + 0x18) = 0xff;
    }
  }
  local_81 = '\0';
  if (((*(int *)((int)param_1 + 0x44) == 1) && (*(int *)((int)param_1 + 0x18) != 0)) &&
     (DAT_008aa468 == 0)) {
    DAT_00679b40 = 1;
    lVar1 = (longlong)ROUND((float)*(int *)((int)param_1 + 0x18) * _DAT_005d8bc4);
    local_90._0_4_ = (int)lVar1;
    iVar9 = (int)local_90;
    local_88 = (float)_DAT_0089ce1c + (float)DAT_0089ce14 * _DAT_005d85ec;
    if (0xa0 < (int)local_90) {
      local_90._0_4_ = 0xa0;
    }
    if (*(char *)((int)param_1 + 0x24) != '\0') {
      uVar10 = (int)local_90 << 0x18;
      local_90 = lVar1;
      CVBufTexture__DrawSpriteEx
                (local_88,((float)DAT_0089ce18 - (float)DAT_0089ce18 * _DAT_005d85ec) +
                          _DAT_005d85d4,0.001,*(void **)((int)param_1 + 8),4,0,1.0,0.0,
                 (float)(uVar10 | 0x505050),0.34,0.8,0.0,1.0,0.0,1.0);
      lVar1 = local_90;
    }
    local_90 = lVar1;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    iVar4 = (*(int *)((int)param_1 + 0x28) - (*(int *)((int)pvVar7 + 0x54) * 5) / 2) + 0xf0;
    psVar6 = CText__GetStringById(&g_Text,0x130ed7);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if (*(char *)((int)param_1 + 0x24) != '\0') {
      uVar19 = 0x3f800000;
      uVar18 = 0;
      psVar6 = local_80;
      uVar17 = 0;
      fVar11 = (float)iVar4;
      uVar10 = iVar9 << 0x18 | 0x505050;
      fVar12 = _DAT_005db3e8 - (float)((int)local_90 / 2);
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawText(fVar12,fVar11,uVar10,psVar6,uVar17,uVar18,uVar19);
    }
    iVar4 = iVar4 + local_90._4_4_;
    if (*(int *)((int)param_1 + 0x20) == 0) {
      fVar11 = PLATFORM__GetSysTimeFloat();
      local_9c = (uint)(longlong)ROUND(fVar11 * _DAT_005dbc44 * _DAT_005db020);
      local_9c = local_9c & 0x800000ff;
      if ((int)local_9c < 0) {
        local_9c = (local_9c - 1 | 0xffffff00) + 1;
      }
      uVar10 = (int)(local_9c - 0x80) >> 0x1f;
      iVar5 = (local_9c - 0x80 ^ uVar10) - uVar10;
      uVar10 = ((int)(iVar5 + (iVar5 >> 0x1f & 3U)) >> 2) * 0x101 + (iVar9 << 0x18 | 0x400000U) +
               iVar5 * 0x10000;
    }
    else if (*(int *)((int)param_1 + 0x2c) == 1) {
      uVar10 = iVar9 << 0x18 | 0xf0f0f0;
    }
    else {
      uVar10 = iVar9 << 0x18 | 0x202020;
    }
    psVar6 = CText__GetStringById(&g_Text,0x41d6e9);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x2c) != 0) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      uVar19 = 0x3f800000;
      uVar18 = 0;
      psVar6 = local_80;
      uVar17 = 0;
      fVar11 = (float)iVar4;
      fVar12 = _DAT_005db3e8 - (float)((int)local_90 / 2);
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawText(fVar12,fVar11,uVar10,psVar6,uVar17,uVar18,uVar19);
    }
    if (*(int *)((int)param_1 + 0x20) == 1) {
      PLATFORM__GetSysTimeFloat();
    }
    psVar6 = CText__GetStringById(&g_Text,0x1f08cea);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x30) != 0) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      CPlatform__Font(&DAT_0088a0a8,0);
      CUnitAI__Unk_004659a0();
    }
    if (*(int *)((int)param_1 + 0x20) == 2) {
      PLATFORM__GetSysTimeFloat();
    }
    psVar6 = CText__GetStringById(&g_Text,0x3fc4f9);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x34) != 0) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      CPlatform__Font(&DAT_0088a0a8,0);
      CUnitAI__Unk_004659a0();
    }
    iVar9 = iVar4 + 0x48;
    if (*(int *)((int)param_1 + 0x20) == 3) {
      PLATFORM__GetSysTimeFloat();
    }
    psVar6 = CText__GetStringById(&g_Text,0xcada9);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x38) == 1) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      fVar11 = (float)iVar9;
      local_88 = fVar11;
      iVar5 = CVBufTexture__Unk_00523b50
                        (_DAT_005db3e8 - (float)((int)local_90 / 2),fVar11,
                         (float)((int)local_90 / 2) + _DAT_005db3e8,(float)(local_90._4_4_ + iVar9))
      ;
      if ((char)iVar5 != '\0') {
        *(undefined4 *)((int)param_1 + 0x20) = 3;
      }
      uVar10 = CVBufTexture__Unk_00523cc0
                         (_DAT_005db3e8 - (float)((int)local_90 / 2),fVar11,
                          (float)((int)local_90 / 2) + _DAT_005db3e8,(float)(local_90._4_4_ + iVar9)
                         );
      if ((char)uVar10 != '\0') {
        *(undefined4 *)((int)param_1 + 0x20) = 3;
        local_81 = '\x01';
      }
      CPlatform__Font(&DAT_0088a0a8,0);
      CUnitAI__Unk_004659a0();
    }
    iVar4 = iVar4 + 0x60;
    if (*(int *)((int)param_1 + 0x20) == 4) {
      PLATFORM__GetSysTimeFloat();
    }
    psVar6 = CText__GetStringById(&g_Text,0x7a211);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x3c) == 1) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      fVar11 = (float)iVar4;
      local_88 = fVar11;
      iVar9 = CVBufTexture__Unk_00523b50
                        (_DAT_005db3e8 - (float)((int)local_90 / 2),fVar11,
                         (float)((int)local_90 / 2) + _DAT_005db3e8,(float)(local_90._4_4_ + iVar4))
      ;
      if ((char)iVar9 != '\0') {
        *(undefined4 *)((int)param_1 + 0x20) = 4;
      }
      uVar10 = CVBufTexture__Unk_00523cc0
                         (_DAT_005db3e8 - (float)((int)local_90 / 2),fVar11,
                          (float)((int)local_90 / 2) + _DAT_005db3e8,(float)(local_90._4_4_ + iVar4)
                         );
      if ((char)uVar10 != '\0') {
        *(undefined4 *)((int)param_1 + 0x20) = 4;
        local_81 = '\x01';
      }
      CPlatform__Font(&DAT_0088a0a8,0);
      CUnitAI__Unk_004659a0();
    }
    if (*(int *)((int)param_1 + 0x20) == 5) {
      PLATFORM__GetSysTimeFloat();
    }
    psVar6 = CText__GetStringById(&g_Text,0x265233);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x40) != 0) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      CPlatform__Font(&DAT_0088a0a8,0);
      CUnitAI__Unk_004659a0();
    }
    CVBufTexture__Unk_00523a70();
    DAT_00679b40 = 0;
  }
  if (((*(int *)((int)param_1 + 0x44) == 2) && (*(int *)((int)param_1 + 0x18) != 0)) &&
     (DAT_008aa468 == 0)) {
    lVar1 = (longlong)ROUND((float)*(int *)((int)param_1 + 0x18) * _DAT_005d8bc4);
    local_90._0_4_ = (int)lVar1;
    iVar9 = (int)local_90;
    local_88 = (float)_DAT_0089ce1c + (float)DAT_0089ce14 * _DAT_005d85ec;
    if (0xa0 < (int)local_90) {
      local_90._0_4_ = 0xa0;
    }
    if (*(char *)((int)param_1 + 0x24) != '\0') {
      uVar10 = (int)local_90 << 0x18;
      local_90 = lVar1;
      CVBufTexture__DrawSpriteEx
                (local_88,((float)DAT_0089ce18 - (float)DAT_0089ce18 * _DAT_005d85ec) -
                          _DAT_005d85cc,0.001,*(void **)((int)param_1 + 8),4,0,1.0,0.0,
                 (float)(uVar10 | 0x505050),0.34,0.6,0.0,1.0,0.0,1.0);
      lVar1 = local_90;
    }
    local_90 = lVar1;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    iVar4 = *(int *)((int)pvVar7 + 0x54);
    iVar8 = PLATFORM__GetWindowHeight();
    iVar5 = *(int *)((int)param_1 + 0x28);
    psVar6 = CText__GetStringById(&g_Text,0x265233);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if (*(char *)((int)param_1 + 0x24) != '\0') {
      fVar11 = (float)((iVar8 / 2 - (iVar4 * 5) / 2) + iVar5);
      uVar19 = 0x3f800000;
      uVar18 = 0;
      psVar6 = local_80;
      uVar17 = 0;
      uVar10 = iVar9 << 0x18 | 0x505050;
      iVar9 = PLATFORM__GetWindowWidth();
      fVar12 = (float)(iVar9 / 2) - (float)((int)local_90 / 2);
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawText(fVar12,fVar11,uVar10,psVar6,uVar17,uVar18,uVar19);
    }
    if (*(int *)((int)param_1 + 0x20) == 0) {
      PLATFORM__GetSysTimeFloat();
    }
    if (*(int *)(DAT_008a9d3c + 0x20) == 0) {
      psVar6 = CText__GetStringById(&g_Text,0x226f16);
    }
    else {
      psVar6 = CText__GetStringById(&g_Text,0x148fe9);
    }
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x2c) != 0) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      PLATFORM__GetWindowWidth();
      CPlatform__Font(&DAT_0088a0a8,0);
      CUnitAI__Unk_004659a0();
    }
    if (*(int *)((int)param_1 + 0x20) == 1) {
      PLATFORM__GetSysTimeFloat();
    }
    if (DAT_008a9ab8 == 1) {
      psVar6 = CText__GetStringById(&g_Text,0x20df719);
    }
    else {
      psVar6 = CText__GetStringById(&g_Text,0x3ba2e96);
    }
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x34) != 0) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      PLATFORM__GetWindowWidth();
      CPlatform__Font(&DAT_0088a0a8,0);
      CUnitAI__Unk_004659a0();
    }
    if (*(int *)((int)param_1 + 0x20) == 2) {
      PLATFORM__GetSysTimeFloat();
    }
    psVar6 = CText__GetStringById(&g_Text,0x6f9da);
    CTexture__Unk_0055e64e(local_80,psVar6);
    piVar3 = (int *)&local_90;
    psVar6 = local_80;
    pvVar7 = CPlatform__Font(&DAT_0088a0a8,1);
    CDXFont__GetTextExtent(pvVar7,psVar6,piVar3);
    if ((*(int *)((int)param_1 + 0x38) == 1) || (*(char *)((int)param_1 + 0x24) == '\x01')) {
      PLATFORM__GetWindowWidth();
      CPlatform__Font(&DAT_0088a0a8,0);
      CUnitAI__Unk_004659a0();
    }
  }
  if (local_81 == '\0') {
    DAT_009c68ac = 1;
    DAT_009c690d = 1;
    return;
  }
  pvVar7 = CGame__GetController(&DAT_008a9a98,0);
  if (pvVar7 != (void *)0x0) {
    pvVar7 = CGame__GetController(&DAT_008a9a98,0);
    pvVar7 = CController__GetToControl(pvVar7);
    if (pvVar7 == param_1) {
      iVar9 = 0;
      goto LAB_00474097;
    }
  }
  pvVar7 = CGame__GetController(&DAT_008a9a98,1);
  if (pvVar7 == (void *)0x0) {
    DAT_009c68ac = 1;
    DAT_009c690d = 1;
    return;
  }
  pvVar7 = CGame__GetController(&DAT_008a9a98,1);
  pvVar7 = CController__GetToControl(pvVar7);
  if (pvVar7 != param_1) {
    DAT_009c68ac = 1;
    DAT_009c690d = 1;
    return;
  }
  iVar9 = 1;
LAB_00474097:
  pvVar7 = CGame__GetController(&DAT_008a9a98,iVar9);
  CUnitAI__Unk_00472b40(param_1,(int)pvVar7,unaff_ESI);
  DAT_009c68ac = 1;
  DAT_009c690d = 1;
  return;
}
