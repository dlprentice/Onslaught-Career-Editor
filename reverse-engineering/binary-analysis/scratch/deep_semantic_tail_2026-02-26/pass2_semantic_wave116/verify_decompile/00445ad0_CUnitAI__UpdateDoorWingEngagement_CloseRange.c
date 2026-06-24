/* address: 0x00445ad0 */
/* name: CUnitAI__UpdateDoorWingEngagement_CloseRange */
/* signature: double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void *param_1)

{
  float fVar1;
  int iVar2;
  float fVar3;
  float fVar4;
  uint uVar5;
  int *piVar6;
  undefined4 *extraout_EAX;
  void *pvVar7;
  undefined4 *extraout_EAX_00;
  int iVar8;
  float10 fVar9;
  void *pvVar10;
  float *pfVar11;
  float fVar12;
  float fStack_3c;
  float fStack_34;
  float fStack_30;
  float fStack_2c;
  undefined4 uStack_28;
  float fStack_24;
  float local_20;
  float fStack_1c;
  undefined1 auStack_14 [20];

  Random__NextLCGAbs(DAT_008a9d9c);
  if ((*(int *)((int)param_1 + 0xc) != 0) && (*(int *)((int)param_1 + 0x68) != 0)) {
    (**(code **)(*(int *)param_1 + 0xc))();
  }
  if (*(int **)((int)param_1 + 0xc) == (int *)0x0) {
    *(undefined4 *)((int)param_1 + 0x68) = 0;
    iVar8 = (**(code **)(*(int *)param_1 + 0x14))();
    if (iVar8 != 0) {
      return (double)_DAT_005d856c;
    }
    iVar8 = CUnitAI__Helper_004fda10(*(int *)((int)param_1 + 8));
    if (iVar8 == 0) {
      (**(code **)(**(int **)((int)param_1 + 8) + 0x100))();
    }
  }
  else {
    pfVar11 = &local_20;
    (**(code **)(**(int **)((int)param_1 + 0xc) + 0x168))();
    fVar9 = (float10)(**(code **)(**(int **)((int)param_1 + 0xc) + 0x40))();
    fVar12 = (float)fVar9;
    if (((*(uint *)(*(int *)((int)param_1 + 0xc) + 0x34) & 0x80000) != 0) &&
       (piVar6 = *(int **)(*(int *)((int)param_1 + 0xc) + 0x26c), piVar6 != (int *)0x0)) {
      fVar9 = (float10)(**(code **)(*piVar6 + 0x40))();
      fVar12 = (float)fVar9;
    }
    piVar6 = *(int **)((int)param_1 + 8);
    fVar1 = fStack_24 - (float)piVar6[7];
    fVar4 = local_20 - (float)piVar6[8];
    fVar3 = fStack_1c - (float)piVar6[9];
    fVar9 = (float10)(**(code **)(*piVar6 + 0x40))();
    piVar6 = *(int **)((int)param_1 + 8);
    fVar1 = (float)(((float10)SQRT(fVar1 * fVar1 + fVar4 * fVar4 + fVar3 * fVar3) - fVar9) -
                   (float10)fVar12);
    fVar3 = fStack_24 - (float)piVar6[7];
    fVar4 = local_20 - (float)piVar6[8];
    fVar9 = (float10)(**(code **)(*piVar6 + 0x40))();
    fVar9 = ((float10)SQRT(fVar3 * fVar3 + fVar4 * fVar4) - fVar9) - (float10)fVar12;
    if (*(int *)((int)param_1 + 100) == 0) {
      if ((_DAT_005d9768 < fVar1) && ((float10)_DAT_005d8610 < fVar9)) {
        iVar8 = *(int *)((int)param_1 + 0xc);
        pvVar10 = (void *)0x0;
        *(undefined4 *)((int)param_1 + 100) = 1;
        iVar2 = **(int **)((int)param_1 + 8);
        pvVar7 = (void *)Vec3__SetXYZ();
        CMeshCollisionVolume__Helper_0040d120((void *)(iVar8 + 0x1c),&fStack_34,pvVar7,pvVar10);
        (**(code **)(iVar2 + 0xf4))
                  (*extraout_EAX_00,extraout_EAX_00[1],extraout_EAX_00[2],extraout_EAX_00[3]);
        return (double)(float)pfVar11;
      }
      Vec3__SetXYZ();
      fVar12 = SQRT(fStack_30 * fStack_30 + fStack_2c * fStack_2c + fStack_34 * fStack_34);
      if (fVar12 != _DAT_005d856c) {
        fVar12 = _DAT_005d8568 / fVar12;
        fStack_34 = fStack_34 * fVar12;
        fStack_30 = fStack_30 * fVar12;
        fStack_2c = fStack_2c * fVar12;
      }
      fStack_34 = fStack_34 * _DAT_005db1e8;
      piVar6 = *(int **)((int)param_1 + 8);
      fStack_30 = fStack_30 * _DAT_005db1e8;
      fStack_2c = fStack_2c * _DAT_005db1e8;
      iVar8 = *piVar6;
LAB_00445ca8:
      Vec3__Add(piVar6 + 7,auStack_14,&fStack_34,(void *)0x0);
      (**(code **)(iVar8 + 0xf4))(*extraout_EAX,extraout_EAX[1],extraout_EAX[2],extraout_EAX[3]);
      return (double)(float)pfVar11;
    }
    if (_DAT_005d85d4 <= fVar1) {
      if ((float10)_DAT_005d857c < fVar9) {
        fStack_34 = fStack_24;
        fStack_30 = local_20;
        fStack_2c = fStack_1c - _DAT_005db1e4;
        (**(code **)(**(int **)((int)param_1 + 8) + 0xf4))(fStack_24,local_20,fStack_2c,uStack_28,0)
        ;
        return (double)(float)pfVar11;
      }
      if (*(int *)((int)param_1 + 0x68) == 0) {
        *(undefined4 *)((int)param_1 + 0x68) = 1;
        uVar5 = Random__NextLCGAbs(DAT_008a9d9c);
        uVar5 = uVar5 & 0x8000ffff;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xffff0000) + 1;
        }
        *(float *)((int)param_1 + 0x70) = (float)(int)uVar5 * _DAT_005db1e0 + _DAT_005d85d4;
        CUnitAI__PlayOpenAnimationIfState1Or3(*(void **)((int)param_1 + 8));
      }
      if (*(int *)((int)param_1 + 0xc) != 0) {
        CUnitAI__Helper_004fcec0();
        return (double)fStack_3c;
      }
    }
    else {
      *(undefined4 *)((int)param_1 + 0x68) = 0;
      uVar5 = Random__NextLCGAbs(DAT_008a9d9c);
      uVar5 = uVar5 & 0x8000ffff;
      if ((int)uVar5 < 0) {
        uVar5 = (uVar5 - 1 | 0xffff0000) + 1;
      }
      *(float *)((int)param_1 + 0x70) = (float)(int)uVar5 * _DAT_005db1ec + _DAT_005d857c;
      CUnitAI__PlayCloseAnimationIfState0Or2(*(void **)((int)param_1 + 8));
      *(undefined4 *)((int)param_1 + 100) = 0;
      if (*(int *)((int)param_1 + 0xc) != 0) {
        CMeshCollisionVolume__Helper_0040d120
                  ((void *)(*(int *)((int)param_1 + 8) + 0x1c),&fStack_34,
                   (void *)(*(int *)((int)param_1 + 0xc) + 0x1c),pfVar11);
        SQRT__Wrapper_00406d50(&fStack_34);
        fStack_34 = fStack_34 * _DAT_005db1e8;
        piVar6 = *(int **)((int)param_1 + 8);
        fStack_30 = fStack_30 * _DAT_005db1e8;
        fStack_2c = fStack_2c * _DAT_005db1e8;
        iVar8 = *piVar6;
        goto LAB_00445ca8;
      }
    }
  }
  return (double)fStack_3c;
}
