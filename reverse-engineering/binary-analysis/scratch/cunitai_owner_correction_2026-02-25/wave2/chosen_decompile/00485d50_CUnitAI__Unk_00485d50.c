/* address: 0x00485d50 */
/* name: CUnitAI__Unk_00485d50 */
/* signature: void __fastcall CUnitAI__Unk_00485d50(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00485d50(int param_1)

{
  int extraout_EAX;
  int iVar1;
  int extraout_EAX_00;
  void *pvVar2;
  int extraout_EAX_01;
  short *psVar3;
  float fVar4;
  int unaff_EDI;
  float10 fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  short *psVar10;
  float fVar11;
  int iVar12;
  int *piVar13;
  int fade_out;
  short *local_18;
  short *local_14;
  longlong local_10;
  int local_8 [2];

  CUnitAI__Unk_00482090();
  CMonitor__Unk_0040dc90(*(int *)(param_1 + 0x50));
  if (0 < extraout_EAX) {
    if ((DAT_008aa530 != 0) && ((DAT_008aa530 == 1 || ((DAT_008aa530 == 2 && (DAT_008aa534 != 0)))))
       ) {
      iVar1 = CGame__Unk_004725d0(0x8a9a98);
      if ((iVar1 == 0) ||
         (fVar6 = _DAT_008aa4fc - _DAT_005dbb74,
         *(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c) != 1)) {
        fVar6 = (_DAT_008aa4fc - _DAT_005dbb74) - _DAT_0067a62c;
      }
      local_10 = CONCAT44(local_10._4_4_,fVar6);
      RenderState_Set(0x13,5);
      RenderState_Set(0x14,6);
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      fVar6 = (float)(short *)local_10;
      CVBufTexture__DrawSpriteEx
                (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe90,(float)(short *)local_10,0.001,
                 *(void **)(param_1 + 0x130),0,0,1.0,0.0,9.223372e+18,1.0,1.0,0.0,1.0,0.0,1.0);
      RenderState_Set(0x13,2);
      RenderState_Set(0x14,2);
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      CVBufTexture__DrawSpriteEx
                (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe90,fVar6,0.001,
                 *(void **)(param_1 + 0x134),0,0,1.0,0.0,-3.3961514e+38,1.0,1.0,0.0,1.0,0.0,1.0);
      CGeneralVolume__Unk_0040c590(*(int *)(param_1 + 0x50));
      if (extraout_EAX_00 == 0) {
        pvVar2 = *(void **)(param_1 + 0x140);
      }
      else if (extraout_EAX_00 == 1) {
        pvVar2 = *(void **)(param_1 + 0x13c);
      }
      else if (extraout_EAX_00 == 2) {
        pvVar2 = *(void **)(param_1 + 0x138);
      }
      else {
        pvVar2 = (void *)0x0;
      }
      fVar5 = (float10)fsin((float10)DAT_00672fd0 * (float10)_DAT_005d85bc);
      local_10 = (longlong)ROUND((fVar5 + (float10)_DAT_005d8568) * (float10)_DAT_005db4ec);
      fVar4 = (float)((int)(short *)local_10 * -0x10000 + -0x80c0d1);
      if (pvVar2 == (void *)0x0) {
        CVBufTexture__DrawSpriteEx
                  (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe90,fVar6,0.001,
                   *(void **)(param_1 + 0x140),0,0,1.0,0.0,fVar4,1.0,1.0,0.0,1.0,0.0,1.0);
        CVBufTexture__DrawSpriteEx
                  (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe90,fVar6,0.001,
                   *(void **)(param_1 + 0x13c),0,0,1.0,0.0,fVar4,1.0,1.0,0.0,1.0,0.0,1.0);
        pvVar2 = *(void **)(param_1 + 0x138);
      }
      CVBufTexture__DrawSpriteEx
                (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe90,fVar6,0.001,pvVar2,0,0,1.0,0.0,fVar4,
                 1.0,1.0,0.0,1.0,0.0,1.0);
    }
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    local_14 = (short *)((DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x584)) *
                        _DAT_005d85d8);
    CGeneralVolume__Unk_0040c550(*(int *)(param_1 + 0x50));
    if (extraout_EAX_01 != 0) {
      iVar1 = CGame__Unk_004725d0(0x8a9a98);
      if ((iVar1 == 0) ||
         (fVar6 = _DAT_008aa4fc - _DAT_005d8ba4,
         *(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c) != 1)) {
        fVar6 = (_DAT_008aa4fc - _DAT_005d8ba4) - _DAT_0067a62c;
      }
      iVar12 = 0;
      local_10 = CONCAT44(local_10._4_4_,fVar6);
      fVar11 = 1.4013e-45;
      pvVar2 = (void *)(_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe8c);
      fVar9 = -NAN;
      fVar8 = 0.6;
      fVar7 = 0.6;
      fVar4 = 0.008;
      iVar1 = extraout_EAX_01;
      psVar3 = local_14;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar1,psVar3,fVar11,iVar12,unaff_EDI);
    }
    iVar1 = CGame__Unk_004725d0(0x8a9a98);
    if ((iVar1 != 0) &&
       (iVar1 = CGame__Unk_004725f0(&DAT_008a9a98,
                                    *(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c),
                                    unaff_EDI), -1 < iVar1)) {
      fVar6 = *(float *)(param_1 + 0x14) - _DAT_005db3a0;
      if (*(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c) != 1) {
        fVar6 = fVar6 - _DAT_0067a62c;
      }
      local_10 = CONCAT44(local_10._4_4_,fVar6);
      sprintf((char *)&local_14,(char *)&PTR_PTR_0062d34c);
      psVar3 = Text__AsciiToWideScratch((char *)&local_14);
      pvVar2 = (void *)(*(float *)(param_1 + 8) + _DAT_005dbe88);
      iVar1 = 0;
      fVar11 = 1.4013e-45;
      psVar10 = (short *)0x40800000;
      fVar9 = -1.7146522e+38;
      fVar8 = 0.8;
      fVar7 = 0.8;
      fVar4 = 0.008;
      fVar6 = (float)(short *)local_10;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,(int)psVar3,psVar10,fVar11,iVar1,unaff_EDI);
    }
  }
  if (DAT_008a9ac0 < 4) {
    local_18 = (short *)0x4479c000;
    iVar1 = *(int *)(*(int *)(param_1 + 0x50) + 0x2b8);
    if (*(int *)(iVar1 + 0x28) != 0) {
      psVar3 = *(short **)(param_1 + 0xb4);
      piVar13 = local_8;
      pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar2,psVar3,piVar13);
      iVar12 = *(int *)(param_1 + 0xb4);
      fade_out = 0;
      fVar11 = 1.4013e-45;
      local_18 = (short *)((DAT_00672fd0 - *(float *)(iVar1 + 0x30)) * _DAT_005d8cc0);
      fVar9 = -NAN;
      fVar8 = 1.0;
      fVar6 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_005dbe84;
      fVar7 = 1.0;
      fVar4 = 0.008;
      pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                       (float)local_8[0] * _DAT_005d85ec);
      psVar3 = local_18;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar12,psVar3,fVar11,fade_out,unaff_EDI);
    }
    local_14 = (short *)0x4479c000;
    if ((_DAT_005d85d4 < (float)local_18) || ((float)local_18 < _DAT_005d856c)) {
      CUnitAI_Unk_0044c720__Wrapper_0040dda0(*(void **)(param_1 + 0x50));
      psVar3 = *(short **)(param_1 + 0xb8);
      piVar13 = local_8;
      local_14 = (short *)((DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x2e8)) *
                          _DAT_005d8cc0);
      pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar2,psVar3,piVar13);
      iVar1 = *(int *)(param_1 + 0xb8);
      iVar12 = 0;
      fVar11 = 1.4013e-45;
      fVar6 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_005dbe84;
      fVar9 = -NAN;
      fVar8 = 1.0;
      fVar7 = 1.0;
      fVar4 = 0.008;
      pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                       (float)local_8[0] * _DAT_005d85ec);
      psVar3 = local_14;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar1,psVar3,fVar11,iVar12,unaff_EDI);
    }
    if (((_DAT_005d85d4 < (float)local_18) || ((float)local_18 < _DAT_005d856c)) &&
       ((_DAT_005d85d4 < (float)local_14 || ((float)local_14 < _DAT_005d856c)))) {
      psVar3 = *(short **)(param_1 + 0xbc);
      piVar13 = local_8;
      local_10 = CONCAT44(local_10._4_4_,
                          (DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x30c)) *
                          _DAT_005d8cc0);
      pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar2,psVar3,piVar13);
      iVar1 = *(int *)(param_1 + 0xbc);
      iVar12 = 0;
      fVar11 = 1.4013e-45;
      fVar6 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_005dbe84;
      fVar9 = -2.3526881e+38;
      fVar8 = 1.0;
      fVar7 = 1.0;
      fVar4 = 0.008;
      pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                       (float)local_8[0] * _DAT_005d85ec);
      psVar3 = (short *)local_10;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar1,psVar3,fVar11,iVar12,unaff_EDI);
    }
    psVar3 = *(short **)(param_1 + 0xc4);
    piVar13 = local_8;
    psVar10 = (short *)((DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x2e0)) *
                       _DAT_005d8cc0);
    pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar2,psVar3,piVar13);
    iVar1 = *(int *)(param_1 + 0xc4);
    iVar12 = 0;
    fVar11 = 1.4013e-45;
    fVar6 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_005db4d0;
    fVar9 = -NAN;
    fVar8 = 1.0;
    fVar7 = 1.0;
    fVar4 = 0.008;
    pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                     (float)local_8[0] * _DAT_005d85ec);
    psVar3 = psVar10;
    CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__DrawTextDynamic
              (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar1,psVar3,fVar11,iVar12,unaff_EDI);
    local_18 = (short *)0x4479c000;
    if ((_DAT_005d85d4 < (float)psVar10) || ((float)psVar10 < _DAT_005d856c)) {
      psVar3 = *(short **)(param_1 + 200);
      piVar13 = local_8;
      local_18 = (short *)((DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x2e4)) *
                          _DAT_005d8cc0);
      pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar2,psVar3,piVar13);
      iVar1 = *(int *)(param_1 + 200);
      iVar12 = 0;
      fVar11 = 1.4013e-45;
      fVar6 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_005db4d0;
      fVar9 = -2.3526881e+38;
      fVar8 = 1.0;
      fVar7 = 1.0;
      fVar4 = 0.008;
      pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                       (float)local_8[0] * _DAT_005d85ec);
      psVar3 = local_18;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar1,psVar3,fVar11,iVar12,unaff_EDI);
    }
    local_14 = (short *)0x4479c000;
    if (((_DAT_005d85d4 < (float)psVar10) || ((float)psVar10 < _DAT_005d856c)) &&
       ((_DAT_005d85d4 < (float)local_18 || ((float)local_18 < _DAT_005d856c)))) {
      psVar3 = *(short **)(param_1 + 0xc0);
      piVar13 = local_8;
      local_14 = (short *)((DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x308)) *
                          _DAT_005d8cc0);
      pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar2,psVar3,piVar13);
      iVar1 = *(int *)(param_1 + 0xc0);
      iVar12 = 0;
      fVar11 = 1.4013e-45;
      fVar6 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_005db4d0;
      fVar9 = -NAN;
      fVar8 = 1.0;
      fVar7 = 1.0;
      fVar4 = 0.008;
      pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                       (float)local_8[0] * _DAT_005d85ec);
      psVar3 = local_14;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar1,psVar3,fVar11,iVar12,unaff_EDI);
    }
    local_10._0_4_ = (short *)0x4479c000;
    if (((_DAT_005d85d4 < (float)psVar10) || ((float)psVar10 < _DAT_005d856c)) &&
       (((_DAT_005d85d4 < (float)local_18 || ((float)local_18 < _DAT_005d856c)) &&
        ((_DAT_005d85d4 < (float)local_14 || ((float)local_14 < _DAT_005d856c)))))) {
      psVar3 = *(short **)(param_1 + 0xcc);
      piVar13 = local_8;
      local_10._0_4_ =
           (short *)((DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x608)) * _DAT_005d8cc0);
      pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar2,psVar3,piVar13);
      iVar1 = *(int *)(param_1 + 0xcc);
      iVar12 = 0;
      fVar11 = 1.4013e-45;
      fVar6 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_005db4d0;
      fVar9 = -NAN;
      fVar8 = 1.0;
      fVar7 = 1.0;
      fVar4 = 0.008;
      pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                       (float)local_8[0] * _DAT_005d85ec);
      psVar3 = (short *)local_10;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar1,psVar3,fVar11,iVar12,unaff_EDI);
    }
    if (((((_DAT_005d85d4 < (float)psVar10) || ((float)psVar10 < _DAT_005d856c)) &&
         ((_DAT_005d85d4 < (float)local_18 || ((float)local_18 < _DAT_005d856c)))) &&
        ((_DAT_005d85d4 < (float)local_14 || ((float)local_14 < _DAT_005d856c)))) &&
       ((_DAT_005d85d4 < (float)(short *)local_10 || ((float)(short *)local_10 < _DAT_005d856c)))) {
      psVar3 = *(short **)(param_1 + 0xd0);
      piVar13 = local_8;
      local_10 = CONCAT44(local_10._4_4_,
                          (DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x60c)) *
                          _DAT_005d8cc0);
      pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar2,psVar3,piVar13);
      iVar1 = *(int *)(param_1 + 0xd0);
      iVar12 = 0;
      fVar11 = 1.4013e-45;
      fVar6 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_005db4d0;
      fVar9 = -NAN;
      fVar8 = 1.0;
      fVar7 = 1.0;
      fVar4 = 0.008;
      pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                       (float)local_8[0] * _DAT_005d85ec);
      psVar3 = (short *)local_10;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar2,fVar6,fVar4,fVar7,fVar8,fVar9,iVar1,psVar3,fVar11,iVar12,unaff_EDI);
    }
    DAT_009c68ac = 0;
    DAT_009c690d = 1;
  }
  return;
}
