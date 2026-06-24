/* address: 0x00428110 */
/* name: CUnitAI__Unk_00428110 */
/* signature: void __fastcall CUnitAI__Unk_00428110(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00428110(void *param_1)

{
  byte bVar1;
  int *piVar2;
  float fVar3;
  int iVar4;
  void *pvVar5;
  int iVar6;
  int *piVar7;
  uint uVar8;
  byte *pbVar9;
  void *unaff_EDI;
  bool bVar10;
  float10 fVar11;
  char *pcVar12;
  undefined **ppuStack_3d8;
  undefined1 auStack_3d4 [8];
  float fStack_3cc;
  undefined1 auStack_3c4 [140];
  undefined4 uStack_338;
  int iStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;

  if (((*(byte *)((int)param_1 + 0x2c) & 4) != 0) &&
     (*(int *)(*(int *)((int)param_1 + 0x164) + 0x198) != 0)) {
    fVar3 = *(float *)((int)param_1 + 0x118) - _DAT_005d85f8;
    *(undefined4 *)((int)param_1 + 0x130) = 0x3ba3d70a;
    *(float *)((int)param_1 + 0x124) = fVar3;
    fVar11 = (float10)(**(code **)(*(int *)param_1 + 0xb4))();
    *(float *)((int)param_1 + 0x84) = (float)(fVar11 + (float10)*(float *)((int)param_1 + 0x84));
    fVar11 = (float10)(**(code **)(*(int *)param_1 + 0x124))();
    *(float *)((int)param_1 + 0x7c) = (float)(fVar11 * (float10)*(float *)((int)param_1 + 0x7c));
    *(float *)((int)param_1 + 0x80) = (float)(fVar11 * (float10)*(float *)((int)param_1 + 0x80));
    *(float *)((int)param_1 + 0x84) = (float)(fVar11 * (float10)*(float *)((int)param_1 + 0x84));
    iVar4 = HeightDelta__Below025_D0((int)param_1);
    if (iVar4 != 0) {
      *(float *)((int)param_1 + 0x7c) = *(float *)((int)param_1 + 0x7c) * _DAT_005d8b9c;
      *(float *)((int)param_1 + 0x80) = *(float *)((int)param_1 + 0x80) * _DAT_005d8b9c;
      *(float *)((int)param_1 + 0x84) = *(float *)((int)param_1 + 0x84) * _DAT_005d8b9c;
      *(undefined4 *)((int)param_1 + 0x130) = 0;
    }
    iVar4 = 2;
    do {
      (**(code **)(*(int *)param_1 + 0x17c))();
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    if (*(float *)((int)param_1 + 0xf8) < -*(float *)(*(int *)((int)param_1 + 0x164) + 0xc0)) {
      CExplosionInitThing__ctor_like_004fd230(param_1);
      (**(code **)(*(int *)param_1 + 0x38))();
    }
  }
  if ((*(int *)((int)param_1 + 0x214) == 0) || (*(int *)(*(int *)((int)param_1 + 0x13c) + 0xc) == 0)
     ) {
    if ((*(float *)((int)param_1 + 0x268) + _DAT_005d8ba0 < DAT_00672fd0) &&
       ((*(int *)((int)param_1 + 0x264) != 1 && (*(int *)((int)param_1 + 0x264) != 2)))) {
      pcVar12 = s_Deactivated_006248c8;
      pvVar5 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
      iVar4 = FindAnimationIndex(pvVar5,(int)pcVar12,unaff_EDI);
      if (iVar4 != -1) {
        (**(code **)(*(int *)param_1 + 0xf0))(iVar4,1,0);
        *(undefined4 *)((int)param_1 + 0x264) = 2;
      }
    }
  }
  else {
    if ((*(int *)((int)param_1 + 0x264) != 0) && (*(int *)((int)param_1 + 0x264) != 3)) {
      pcVar12 = s_Activate_00623e14;
      pvVar5 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
      iVar4 = FindAnimationIndex(pvVar5,(int)pcVar12,unaff_EDI);
      if (iVar4 != -1) {
        (**(code **)(*(int *)param_1 + 0xf0))(iVar4,1,0);
        *(undefined4 *)((int)param_1 + 0x264) = 3;
      }
    }
    if (*(int *)(*(int *)((int)param_1 + 0x13c) + 0xc) != 0) {
      *(float *)((int)param_1 + 0x268) = DAT_00672fd0;
    }
  }
  if (*(int *)((int)param_1 + 700) != 0) {
    CInfluenceMap__Init();
    ppuStack_3d8 = &PTR_VFuncSlot_00_0040e1b0_005d8c80;
    iStack_1c = 0;
    uStack_18 = 0;
    uStack_14 = 0;
    uStack_10 = 0;
    uStack_c = 0;
    uStack_4 = 0;
    uStack_8 = 0;
    CUnit__UpdateTransform(1,1,auStack_3d4,auStack_3c4);
    uStack_338 = *(undefined4 *)((int)param_1 + 0x138);
    iVar4 = 0;
    piVar7 = (int *)*DAT_008553f8;
    DAT_008553f8[2] = (int)piVar7;
    if (piVar7 == (int *)0x0) {
      iVar6 = 0;
    }
    else {
      iVar6 = *piVar7;
    }
    while (iVar6 != 0) {
      pbVar9 = *(byte **)(iVar6 + 0x30);
      pcVar12 = s_Gill_M_Claw_Hit_006248b8;
      do {
        bVar1 = *pcVar12;
        bVar10 = bVar1 < *pbVar9;
        if (bVar1 != *pbVar9) {
LAB_0042839a:
          iVar6 = (1 - (uint)bVar10) - (uint)(bVar10 != 0);
          goto LAB_0042839f;
        }
        if (bVar1 == 0) break;
        bVar1 = pcVar12[1];
        bVar10 = bVar1 < pbVar9[1];
        if (bVar1 != pbVar9[1]) goto LAB_0042839a;
        pcVar12 = pcVar12 + 2;
        pbVar9 = pbVar9 + 2;
      } while (bVar1 != 0);
      iVar6 = 0;
LAB_0042839f:
      if (iVar6 == 0) goto LAB_004283c4;
      iVar4 = iVar4 + 1;
      piVar7 = *(int **)(DAT_008553f8[2] + 4);
      DAT_008553f8[2] = (int)piVar7;
      if (piVar7 == (int *)0x0) {
        iVar6 = 0;
      }
      else {
        iVar6 = *piVar7;
      }
    }
    iVar4 = -1;
LAB_004283c4:
    piVar7 = (int *)CWorldPhysicsManager__CreatePickup(iVar4);
    if (piVar7 != (int *)0x0) {
      piVar2 = (int *)*DAT_008553f8;
      DAT_008553f8[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        iStack_1c = 0;
      }
      else {
        iStack_1c = *piVar2;
      }
      while (iStack_1c != 0) {
        pbVar9 = *(byte **)(iStack_1c + 0x30);
        pcVar12 = s_Gill_M_Claw_Hit_006248b8;
        do {
          bVar1 = *pcVar12;
          bVar10 = bVar1 < *pbVar9;
          if (bVar1 != *pbVar9) {
LAB_0042842f:
            iVar4 = (1 - (uint)bVar10) - (uint)(bVar10 != 0);
            goto LAB_00428434;
          }
          if (bVar1 == 0) break;
          bVar1 = pcVar12[1];
          bVar10 = bVar1 < pbVar9[1];
          if (bVar1 != pbVar9[1]) goto LAB_0042842f;
          pcVar12 = pcVar12 + 2;
          pbVar9 = pbVar9 + 2;
        } while (bVar1 != 0);
        iVar4 = 0;
LAB_00428434:
        if (iVar4 == 0) goto LAB_00428461;
        piVar2 = *(int **)(DAT_008553f8[2] + 4);
        DAT_008553f8[2] = (int)piVar2;
        if (piVar2 == (int *)0x0) {
          iStack_1c = 0;
        }
        else {
          iStack_1c = *piVar2;
        }
      }
      iStack_1c = 0;
LAB_00428461:
      uStack_18 = 0;
      if (DAT_006fbdfc < fStack_3cc) {
        fStack_3cc = DAT_006fbdfc;
      }
      (**(code **)(*piVar7 + 0x24))(&ppuStack_3d8);
    }
  }
  CUnit__Unk_004fa8d0(param_1);
  uVar8 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar8 = uVar8 & 0x8000ffff;
  if ((int)uVar8 < 0) {
    uVar8 = (uVar8 - 1 | 0xffff0000) + 1;
  }
  if (_DAT_005d8bb0 < (float)(int)uVar8 * _DAT_005d8d54) {
    CUnitAI__RefreshCachedComponentTransform((int)param_1);
  }
  return;
}
