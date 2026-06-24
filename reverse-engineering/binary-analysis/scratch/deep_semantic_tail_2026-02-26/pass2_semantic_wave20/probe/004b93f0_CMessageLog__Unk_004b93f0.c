/* address: 0x004b93f0 */
/* name: CMessageLog__Unk_004b93f0 */
/* signature: void __fastcall CMessageLog__Unk_004b93f0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMessageLog__Unk_004b93f0(void *param_1)

{
  float10 fVar1;
  float fVar2;
  float p2;
  bool bVar3;
  bool bVar4;
  short *psVar5;
  void *pvVar6;
  int iVar7;
  uint uVar8;
  void *pvVar9;
  float10 fVar10;
  float10 fVar11;
  double dVar12;
  float fVar13;
  int *piVar14;
  int local_1c;
  int local_10;
  int local_8 [2];

  pvVar9 = (void *)0x0;
  if (*(int *)((int)param_1 + 0x28) != 0) {
    *(undefined4 *)((int)param_1 + 0x34) = 0;
    CExplosionInitThing__Helper_00482090();
    RenderState_Set(0x17,8);
    D3DStateCache__SetStateCached(0,1,4);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    CVBufTexture__DrawSpriteEx
              (0.0,0.0,0.01,*(void **)((int)param_1 + 0xc),0,0,1.0,0.0,-2.2509804,40.0,30.0,0.0,1.0,
               0.0,1.0);
    CVBufTexture__DrawSpriteEx
              (100.0,100.0,0.01,*(void **)((int)param_1 + 0x10),0,0,1.0,0.0,0.0,1.0,1.0,0.0,1.0,0.0,
               1.0);
    D3DStateCache__SetStateCached(0,1,4);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    psVar5 = CText__GetStringById(&g_Text,0x1f08cea);
    piVar14 = local_8;
    pvVar6 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar6,psVar5,piVar14);
    CPlatform__Font(&DAT_0088a0a8,0);
    CDXEngine__Helper_004659a0();
    if (*(int *)((int)param_1 + 0x24) == 0) {
      psVar5 = CText__GetStringById(&g_Text,0x2a9338);
      CMessageLog__Unk_004b9010();
      piVar14 = local_8;
      pvVar6 = CPlatform__Font(&DAT_0088a0a8,1);
      CDXFont__GetTextExtent(pvVar6,psVar5,piVar14);
      CPlatform__Font(&DAT_0088a0a8,1);
      CDXEngine__Helper_004659a0();
    }
    D3DStateCache__SetState114Raw(0,6,1);
    D3DStateCache__SetState114Raw(0,5,1);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    local_10 = (int)(longlong)ROUND(_DAT_005db4d0 - *(float *)((int)param_1 + 0x2c));
    local_1c = local_10;
    if ((0 < *(int *)((int)param_1 + 0x38)) && (0 < *(int *)((int)param_1 + 0x38))) {
      do {
        CUnit__Unk_004e5c90((void *)((int)param_1 + 0x18),pvVar9,0x42c80000);
        iVar7 = CMessageLog__Unk_004b9a80();
        local_10 = local_10 + (-8 - iVar7);
        pvVar9 = (void *)((int)pvVar9 + 1);
        local_1c = local_10;
      } while ((int)pvVar9 < *(int *)((int)param_1 + 0x38));
    }
    piVar14 = *(int **)((int)param_1 + 0x18);
    bVar3 = false;
    bVar4 = false;
    *(int **)((int)param_1 + 0x20) = piVar14;
    local_10 = local_1c;
    if (piVar14 == (int *)0x0) {
      iVar7 = 0;
    }
    else {
      iVar7 = *piVar14;
    }
    while (iVar7 != 0) {
      iVar7 = CMessageLog__Unk_004b9a80();
      if (local_1c < 0x33) {
        bVar3 = true;
      }
      if (_DAT_005dc760 <= (float)local_1c) {
        bVar4 = true;
      }
      if ((0x32 < local_1c) && (local_1c < 0x15e)) {
        CMessageLog__Unk_004b9a80();
        local_10 = iVar7 + local_1c;
      }
      local_1c = local_1c + 8 + iVar7;
      piVar14 = *(int **)(*(int *)((int)param_1 + 0x20) + 4);
      *(int **)((int)param_1 + 0x20) = piVar14;
      if (piVar14 == (int *)0x0) {
        iVar7 = 0;
      }
      else {
        iVar7 = *piVar14;
      }
    }
    dVar12 = PtrFloatAt4__GetOrOne(&DAT_0088a0a8);
    fVar13 = (*(float *)((int)param_1 + 0x30) - *(float *)((int)param_1 + 0x2c)) * _DAT_005dc758 *
             (_DAT_005db538 / (float)dVar12) + *(float *)((int)param_1 + 0x2c);
    *(float *)((int)param_1 + 0x2c) = fVar13;
    if (ABS(fVar13 - *(float *)((int)param_1 + 0x30)) < (float)_DAT_005d87e0) {
      *(undefined4 *)((int)param_1 + 0x2c) = 0;
      *(undefined4 *)((int)param_1 + 0x30) = 0;
      if (*(int *)((int)param_1 + 0x38) != *(int *)((int)param_1 + 0x3c)) {
        *(int *)((int)param_1 + 0x38) = *(int *)((int)param_1 + 0x3c);
      }
    }
    D3DStateCache__SetState114Raw(0,6,2);
    D3DStateCache__SetState114Raw(0,5,2);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    fVar13 = PLATFORM__GetSysTimeFloat();
    fVar10 = (float10)fcos((float10)fVar13 * (float10)_DAT_005dc750);
    fVar1 = (float10)_DAT_005d8578;
    fVar13 = PLATFORM__GetSysTimeFloat();
    fVar11 = (float10)fcos((float10)fVar13 * (float10)_DAT_005dc750);
    fVar13 = (float)(fVar11 * (float10)_DAT_005d85d8);
    fVar2 = _DAT_005d8600 - (float)(fVar10 * fVar1);
    if (bVar3) {
      p2 = fVar13 + _DAT_005dc74c;
      CVBufTexture__DrawSpriteEx
                (320.0,p2,0.001,DAT_00807418,4,0,1.0,-1.5707964,-NAN,fVar2 * _DAT_005d85ec,fVar2,0.0
                 ,1.0,0.0,1.0);
      uVar8 = Input__GetClickStateInRect(304.0,p2 - _DAT_005d8bc0,336.0,fVar13 + _DAT_005dc748);
      if ((char)uVar8 != '\0') {
        (**(code **)(*(int *)param_1 + 0xc))(0,0x2a,0x3f800000);
      }
    }
    if (bVar4) {
      fVar13 = (float)(local_10 + 0x10) - fVar13;
      CVBufTexture__DrawSpriteEx
                (320.0,fVar13,0.001,DAT_00807418,4,0,1.0,1.5707964,-NAN,fVar2 * _DAT_005d85ec,fVar2,
                 0.0,1.0,0.0,1.0);
      fVar2 = fVar13 + _DAT_005d8bc0;
      *(undefined4 *)((int)param_1 + 0x34) = 1;
      uVar8 = Input__GetClickStateInRect(304.0,fVar13 - _DAT_005d8bc0,336.0,fVar2);
      if ((char)uVar8 != '\0') {
        (**(code **)(*(int *)param_1 + 0xc))(0,0x2b,0x3f800000);
      }
    }
    CVBufTexture__DrawSpriteEx
              (24.0,454.0,0.001,DAT_00807418,4,0,1.0,3.1415927,-NAN,1.0,1.0,0.0,1.0,0.0,1.0);
    uVar8 = Input__GetClickStateInRect(0.0,400.0,200.0,480.0);
    if ((char)uVar8 != '\0') {
      (**(code **)(*(int *)param_1 + 0xc))(0,0x2e,0x3f800000);
    }
    if (DAT_0089be28 != 0) {
      DAT_0089be28 = 0;
      (**(code **)(*(int *)param_1 + 0xc))(0,0x2e,0x3f800000);
    }
    CDXEngine__Helper_00523a70();
  }
  return;
}
