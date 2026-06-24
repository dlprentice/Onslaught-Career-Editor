/* address: 0x004858d0 */
/* name: CUnitAI__Unk_004858d0 */
/* signature: void __fastcall CUnitAI__Unk_004858d0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_004858d0(int param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;
  float *extraout_EAX;
  void *unaff_EDI;
  float10 fVar4;
  float10 fVar5;
  double dVar6;
  float local_c;
  float local_8;

  CUnitAI__Unk_00482090();
  RenderState_Set(0x17,8);
  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  iVar3 = CGame__Unk_004725d0(0x8a9a98);
  if ((iVar3 == 0) ||
     (fVar1 = _DAT_008aa4fc + _DAT_005d8bc0,
     *(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c) != 1)) {
    fVar1 = (_DAT_008aa4fc + _DAT_005d8bc0) - _DAT_0067a62c;
  }
  CVBufTexture__DrawSpriteEx
            (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbdfc,fVar1,0.001,*(void **)(param_1 + 0x14c),2
             ,0,1.0,0.0,1.5845632e+29,1.0,1.0,0.0,1.0,0.0,1.0);
  if ((DAT_008aa52c != 0) && ((DAT_008aa52c == 1 || ((DAT_008aa52c == 2 && (DAT_008aa534 != 0))))))
  {
    RenderState_Set(0x13,2);
    RenderState_Set(0x14,2);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    CVBufTexture__DrawSpriteEx
              (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbdfc,fVar1,0.001,*(void **)(param_1 + 0x118)
               ,2,0,1.0,0.0,-3.1843154e+38,1.0,1.0,0.0,1.0,0.0,1.0);
  }
  if ((DAT_008aa530 != 0) && ((DAT_008aa530 == 1 || ((DAT_008aa530 == 2 && (DAT_008aa534 != 0))))))
  {
    iVar3 = CGame__Unk_004725d0(0x8a9a98);
    if ((iVar3 == 0) ||
       (fVar1 = _DAT_008aa4fc - _DAT_005dbe80,
       *(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c) != 1)) {
      fVar1 = (_DAT_008aa4fc - _DAT_005dbe80) - _DAT_0067a62c;
    }
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    CVBufTexture__DrawSpriteEx
              (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe7c,fVar1,0.001,*(void **)(param_1 + 0x128)
               ,2,0,1.0,0.0,0.5,1.0,1.0,0.0,1.0,0.0,1.0);
    dVar6 = CGeneralVolume__Unk_0040c4a0(*(int *)(param_1 + 0x50));
    CVBufTexture__DrawSpriteEx
              (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe7c,fVar1,0.001,*(void **)(param_1 + 0x128)
               ,2,1,(float)dVar6,0.0,3.4027845e+38,1.0,1.0,0.0,1.0,0.0,1.0);
    RenderState_Set(0x13,2);
    RenderState_Set(0x14,2);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    CVBufTexture__DrawSpriteEx
              (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbe7c,fVar1,0.001,*(void **)(param_1 + 0x124)
               ,2,0,1.0,0.0,-NAN,1.0,1.0,0.0,1.0,0.0,1.0);
  }
  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  CGeneralVolume__Unk_0040d660(*(void **)(param_1 + 0x50),(int)&local_c,unaff_EDI);
  fVar1 = *extraout_EAX;
  fVar4 = (float10)fsin((float10)fVar1);
  fVar5 = (float10)fcos((float10)fVar1);
  local_c = (float)(fVar4 * (float10)_DAT_005db540);
  local_8 = (float)fVar5 * _DAT_005dbe78;
  RenderState_Set(0x17,8);
  RenderState_Set(7,0);
  iVar3 = CGame__Unk_004725d0(0x8a9a98);
  if ((iVar3 == 0) ||
     (fVar2 = _DAT_008aa4fc + _DAT_005d8bc0,
     *(int *)(*(int *)(*(int *)(param_1 + 0x50) + 0x574) + 0x2c) != 1)) {
    fVar2 = (_DAT_008aa4fc + _DAT_005d8bc0) - _DAT_0067a62c;
  }
  CVBufTexture__DrawSpriteEx
            (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbdfc + _DAT_005db4e4 + local_c,
             (fVar2 - _DAT_005d95b8) + _DAT_005db4e4 + local_8,0.001,*(void **)(param_1 + 0x148),4,0
             ,1.0,fVar1,-2.9708244e+38,1.0,1.0,0.0,1.0,0.0,1.0);
  return;
}
