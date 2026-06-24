/* address: 0x004d11d0 */
/* name: CEngine__RenderOverlayAndMenuTransitions */
/* signature: uint __fastcall CEngine__RenderOverlayAndMenuTransitions(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __fastcall CEngine__RenderOverlayAndMenuTransitions(int param_1)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  float fStack_14;
  int iStack_10;
  uint uStack_8;

  iVar3 = *DAT_0082b48c;
  uVar2 = (**(code **)(iVar3 + 0x3c))();
  (**(code **)(iVar3 + 0x38))(uVar2);
  iVar3 = CRTMesh__GetQualityLevel();
  if (iVar3 == 0) {
    uVar2 = 0;
    iVar3 = *DAT_0082b488;
  }
  else {
    if (iVar3 == 1) {
      (**(code **)(*DAT_0082b488 + 0x38))(1);
      goto LAB_004d1229;
    }
    if (iVar3 != 2) goto LAB_004d1229;
    uVar2 = 2;
    iVar3 = *DAT_0082b488;
  }
  (**(code **)(iVar3 + 0x38))(uVar2);
LAB_004d1229:
  if (*(int *)(param_1 + 0x10) == 0) {
    bVar1 = *(float *)(param_1 + 0x30) < _DAT_005d856c;
    *(undefined4 *)(param_1 + 0x34) = 0;
    if (bVar1) {
      return 0;
    }
    fVar4 = PLATFORM__GetSysTimeFloat();
    if (_DAT_005d8c40 < fVar4 - *(float *)(param_1 + 0x30)) {
      return 0;
    }
  }
  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  DAT_009c68ad = 0;
  DAT_009c6910 = 1;
  D3DStateCache__SetState114Raw(0,1,3);
  D3DStateCache__SetState114Raw(0,2,3);
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
  if (*(int *)(param_1 + 0x10) == 0) {
    fVar4 = *(float *)(param_1 + 0x30) + _DAT_005d8c40;
    fVar5 = PLATFORM__GetSysTimeFloat();
    fVar4 = fVar4 - fVar5;
  }
  else {
    fVar4 = PLATFORM__GetSysTimeFloat();
    fVar4 = fVar4 - *(float *)(param_1 + 0x28);
  }
  iStack_10 = (int)(longlong)ROUND(fVar4 * _DAT_005db34c);
  if (0xc0 < iStack_10) {
    iStack_10 = 0xc0;
  }
  if (*(int *)(param_1 + 0x48) != 0) {
    iStack_10 = 0xc0;
  }
  RenderState_Set(0x17,8);
  if ((DAT_0082b4e8 == '\0') && ((*(int *)(param_1 + 0x10) != 0 || (*(int *)(param_1 + 0x48) == 0)))
     ) {
    CVBufTexture__DrawSpriteEx
              (-10.0,-10.0,0.01,DAT_0082b490,0,0,1.0,0.0,(float)(iStack_10 * 0x1000000 + 0x101010),
               50.0,40.0,0.0,1.0,0.0,1.0);
  }
  if (*(float *)(param_1 + 0x34) == _DAT_005d856c) {
    fVar5 = PLATFORM__GetSysTimeFloat();
    *(float *)(param_1 + 0x34) = fVar5;
  }
  if (*(int *)(param_1 + 0x10) != 0) {
    fVar4 = PLATFORM__GetSysTimeFloat();
    fVar4 = fVar4 - *(float *)(param_1 + 0x2c);
  }
  RenderState_Set(0x17,4);
  fVar5 = 1.2;
  fStack_14 = 0.0;
  if (_DAT_005d8604 <= fVar4) {
    fStack_14 = fVar4;
    if (_DAT_005d8c40 < fVar4) {
      fStack_14 = _DAT_005d8c40;
    }
    fStack_14 = fStack_14 - _DAT_005d8604;
  }
  else {
    fVar5 = fVar4 * _DAT_005db564 * _DAT_005dc240 + _DAT_005d85c0;
  }
  if ((DAT_0082b4e8 == '\0') && (*(int *)(param_1 + 0x24) == 0)) {
    CVBufTexture__DrawSpriteEx
              (320.0,240.0,0.004,*(void **)(param_1 + 0x40),4,0,1.0,-fStack_14,-NAN,fVar5,fVar5,0.0,
               1.0,0.0,1.0);
    CVBufTexture__DrawSpriteEx
              (320.0,240.0,0.004,*(void **)(param_1 + 0x44),4,0,1.0,fStack_14,-NAN,fVar5,fVar5,0.0,
               1.0,0.0,1.0);
  }
  if (_DAT_005d8c40 < fVar4) {
    iVar3 = param_1;
    CUnit__Unk_004e5c90((void *)(param_1 + 0x14),*(void **)(param_1 + 0x24),param_1);
    uStack_8 = CMenuItemRange__Render(iVar3);
    if (*(int *)(param_1 + 8) != 0) {
      CMenuItemRange__Render(param_1);
    }
    if (*(int *)(param_1 + 0x3c) != 0) {
      CMenuItemRange__Render(param_1);
    }
  }
  RenderState_Set(0xe,1);
  RenderState_Set(7,1);
  if ((DAT_0082b4e8 == '\0') && (iStack_10 == 0xc0)) {
    CDXEngine__Helper_00523a70();
  }
  return -(uint)(*(int *)(param_1 + 0x24) != 0) & uStack_8;
}
