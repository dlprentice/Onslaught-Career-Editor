/* address: 0x00486940 */
/* name: CUnitAI__Unk_00486940 */
/* signature: void __fastcall CUnitAI__Unk_00486940(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00486940(int param_1)

{
  int extraout_EAX;
  int iVar1;
  int extraout_EAX_00;
  short *color;
  void *pvVar2;
  int unaff_ESI;
  double dVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float scale_y;
  short *psVar8;
  float transition;
  int *out_extent_xy;
  int iVar9;
  float local_1c [2];
  float fStack_14;
  undefined8 local_10;
  int aiStack_8 [2];

  CUnitAI__Unk_00482090();
  local_10 = (ulonglong)local_10._4_4_ << 0x20;
  local_1c[0] = 1.0;
  CGeneralVolume__Unk_0040c480(*(int *)(param_1 + 0x50));
  if (extraout_EAX != 0) {
    iVar1 = CGame__Unk_004725d0(0x8a9a98);
    if (iVar1 == 0) {
      fStack_14 = (_DAT_008aa4fc - _DAT_005dbe80) - _DAT_0067a62c;
    }
    else if (*(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c) == 1) {
      fStack_14 = _DAT_008aa4fc + _DAT_005db540;
    }
    else {
      fStack_14 = _DAT_008aa4f4 + _DAT_005d9638;
      local_10 = CONCAT44(local_10._4_4_,0x3f800000);
      local_1c[0] = 0.0;
    }
    if ((DAT_008aa530 != 0) && ((DAT_008aa530 == 1 || ((DAT_008aa530 == 2 && (DAT_008aa534 != 0)))))
       ) {
      RenderState_Set(0x13,5);
      RenderState_Set(0x14,6);
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      fVar5 = local_1c[0];
      fVar6 = (float)local_10;
      CVBufTexture__DrawSpriteEx
                ((((_DAT_008aa4f8 - _DAT_005dbe98) + _DAT_005dbe7c) - _DAT_005dbe34) - _DAT_0067a628
                 ,fStack_14,0.001,*(void **)(param_1 + 0x128),2,2,1.0,0.0,0.5,1.0,1.0,0.0,1.0,
                 (float)local_10,local_1c[0]);
      dVar3 = CGeneralVolume__Unk_0040c3c0(*(void **)(param_1 + 0x50));
      local_1c[0] = (float)dVar3;
      fVar4 = _DAT_005d8568 - local_1c[0];
      local_10._0_4_ = (float)(longlong)ROUND(local_1c[0] * _DAT_005d8c70 + fVar4 * _DAT_005dbc4c);
      iVar1 = (int)(float)local_10 * 0x100;
      local_10._0_4_ = (float)(longlong)ROUND(fVar4 * _DAT_005d8c70 + local_1c[0] * _DAT_005db3c0);
      iVar1 = iVar1 + (int)(float)local_10;
      local_10 = (longlong)ROUND(fVar4 * _DAT_005db3c0 + local_1c[0] * _DAT_005db3c0);
      iVar1 = iVar1 * 0x100 + (int)(float)local_10;
      CGeneralVolume__Unk_0040c3a0(*(int *)(param_1 + 0x50));
      fVar4 = fStack_14;
      if (extraout_EAX_00 == 0) {
        *(undefined4 *)(param_1 + 0x1ec + *(int *)(param_1 + 0x58) * 4) = 0x3f4ccccd;
      }
      else {
        iVar9 = *(int *)(param_1 + 0x58);
        if (*(float *)(param_1 + 0x1dc + iVar9 * 4) == *(float *)(param_1 + 0x1ec + iVar9 * 4)) {
          if (*(int *)(param_1 + 0x1ec + iVar9 * 4) == 0x3f4ccccd) {
            *(undefined4 *)(param_1 + 0x1ec + iVar9 * 4) = 0x3dcccccd;
          }
          else {
            *(undefined4 *)(param_1 + 0x1ec + iVar9 * 4) = 0x3f4ccccd;
          }
        }
      }
      iVar9 = *(int *)(param_1 + 0x58);
      fVar7 = DAT_008a9e20 * _DAT_005d85c0 + *(float *)(param_1 + 0x1dc + iVar9 * 4);
      if (*(float *)(param_1 + 0x1ec + iVar9 * 4) <= fVar7) {
        fVar7 = *(float *)(param_1 + 0x1dc + iVar9 * 4) - DAT_008a9e20 * _DAT_005d85c0;
        if (fVar7 <= *(float *)(param_1 + 0x1ec + iVar9 * 4)) {
          *(undefined4 *)(param_1 + 0x1dc + iVar9 * 4) =
               *(undefined4 *)(param_1 + 0x1ec + iVar9 * 4);
        }
        else {
          *(float *)(param_1 + 0x1dc + iVar9 * 4) = fVar7;
        }
      }
      else {
        *(float *)(param_1 + 0x1dc + iVar9 * 4) = fVar7;
      }
      local_10 = (longlong)
                 ROUND(*(float *)(param_1 + 0x1dc + *(int *)(param_1 + 0x58) * 4) * _DAT_005d9644);
      CVBufTexture__DrawSpriteEx
                ((((_DAT_008aa4f8 - _DAT_005dbe98) + _DAT_005dbe7c) - _DAT_005dbe34) - _DAT_0067a628
                 ,fStack_14,0.001,*(void **)(param_1 + 0x128),2,2,local_1c[0],0.0,
                 (float)(iVar1 + (int)(float)local_10 * -0x1000000),1.0,1.0,0.0,1.0,fVar6,fVar5);
      RenderState_Set(0x13,2);
      RenderState_Set(0x14,2);
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      CVBufTexture__DrawSpriteEx
                ((((_DAT_008aa4f8 - _DAT_005dbe98) + _DAT_005dbe7c) - _DAT_005dbe34) - _DAT_0067a628
                 ,fVar4,0.001,*(void **)(param_1 + 0x124),2,2,1.0,0.0,-NAN,1.0,1.0,0.0,1.0,fVar6,
                 fVar5);
    }
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    return;
  }
  iVar1 = CGame__Unk_004725d0(0x8a9a98);
  if (iVar1 == 0) {
    iVar1 = PLATFORM__GetWindowHeight();
    fStack_14 = ((float)iVar1 - _DAT_0067a62c) - _DAT_005d8c20;
    local_10._0_4_ = (float)iVar1;
  }
  else if (*(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c) == 1) {
    iVar1 = PLATFORM__GetWindowHeight();
    fStack_14 = (float)iVar1 * _DAT_005d85ec - _DAT_005d9640;
    local_10._0_4_ = (float)iVar1;
  }
  else {
    iVar1 = PLATFORM__GetWindowHeight();
    fStack_14 = (float)iVar1 * _DAT_005d85ec + _DAT_005db540;
    local_10._0_4_ = (float)iVar1;
  }
  CGeneralVolume__Unk_0040c460(*(int *)(param_1 + 0x50));
  sprintf((char *)local_1c,&DAT_006245cc);
  color = Text__AsciiToWideScratch((char *)local_1c);
  out_extent_xy = aiStack_8;
  psVar8 = color;
  pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__GetTextExtent(pvVar2,psVar8,out_extent_xy);
  iVar9 = 0;
  transition = 1.4013e-45;
  psVar8 = (short *)0x40a00000;
  scale_y = -2.3526914e+38;
  fVar7 = 1.0;
  fVar6 = 1.0;
  fVar5 = 0.008;
  fVar4 = fStack_14;
  iVar1 = PLATFORM__GetWindowWidth();
  local_10 = CONCAT44(local_10._4_4_,iVar1);
  pvVar2 = (void *)((((float)iVar1 - _DAT_0067a628) - _DAT_005dbe94) -
                   (float)aiStack_8[0] * _DAT_005d85ec);
  CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__DrawTextDynamic
            (pvVar2,fVar4,fVar5,fVar6,fVar7,scale_y,(int)color,psVar8,transition,iVar9,unaff_ESI);
  return;
}
