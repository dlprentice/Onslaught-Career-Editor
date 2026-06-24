/* address: 0x00446150 */
/* name: CUnitAI__UpdateDoorWingEngagement_LongRange */
/* signature: double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void *param_1)

{
  int *piVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  uint uVar5;
  int iVar6;
  float10 fVar7;
  float fVar8;
  float fStack_3c;
  float fStack_34;
  float local_30;
  float fStack_2c;
  float fStack_24;
  float fStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_10;
  float fStack_c;

  Random__NextLCGAbs(DAT_008a9d9c);
  if (*(int *)((int)param_1 + 0xc) != 0) {
    (**(code **)(*(int *)param_1 + 0xc))();
  }
  if (*(int **)((int)param_1 + 0xc) == (int *)0x0) {
    *(undefined4 *)((int)param_1 + 0x68) = 0;
    iVar6 = (**(code **)(*(int *)param_1 + 0x14))();
    if (iVar6 != 0) {
      return (double)_DAT_005d856c;
    }
    iVar6 = CUnitAI__Helper_004fda10(*(int *)((int)param_1 + 8));
    if (iVar6 == 0) {
      (**(code **)(**(int **)((int)param_1 + 8) + 0x100))();
    }
  }
  else {
    (**(code **)(**(int **)((int)param_1 + 0xc) + 0x168))(&local_30);
    iVar6 = *(int *)((int)param_1 + 8);
    fStack_24 = fStack_34 - *(float *)(iVar6 + 0x1c);
    fStack_20 = local_30 - *(float *)(iVar6 + 0x20);
    fStack_1c = fStack_2c - *(float *)(iVar6 + 0x24);
    fVar7 = (float10)(**(code **)(**(int **)((int)param_1 + 0xc) + 0x40))();
    fVar8 = (float)fVar7;
    if (((*(uint *)(*(int *)((int)param_1 + 0xc) + 0x34) & 0x80000) != 0) &&
       (piVar1 = *(int **)(*(int *)((int)param_1 + 0xc) + 0x26c), piVar1 != (int *)0x0)) {
      fVar7 = (float10)(**(code **)(*piVar1 + 0x40))();
      fVar8 = (float)fVar7;
    }
    fVar4 = fStack_20 * fStack_20;
    fVar2 = fStack_1c * fStack_1c;
    fVar3 = fStack_24 * fStack_24;
    fVar7 = (float10)(**(code **)(**(int **)((int)param_1 + 8) + 0x40))();
    fVar8 = (float)(((float10)SQRT(fVar3 + fVar2 + fVar4) - fVar7) - (float10)fVar8);
    if (*(int *)((int)param_1 + 0x68) == 0) {
      piVar1 = *(int **)((int)param_1 + 8);
      fStack_10 = (float)piVar1[0x14] * _DAT_005d85d0;
      fStack_c = -((float)piVar1[0x18] * _DAT_005d85d0);
      fStack_24 = (float)piVar1[0x10] * _DAT_005d85d0 + (float)piVar1[7];
      fStack_20 = fStack_10 + (float)piVar1[8];
      fStack_1c = fStack_c + (float)piVar1[9];
      (**(code **)(*piVar1 + 0xf4))(fStack_24,fStack_20,fStack_1c,fStack_18,0);
      if (*(float *)((int)param_1 + 0x70) < fVar8) {
        CUnitAI__EnterDoorWingOpenTrackingState((int)param_1);
        return (double)fStack_3c;
      }
    }
    else {
      CUnitAI__Helper_004fcec0();
      if (fVar8 < *(float *)((int)param_1 + 0x70)) {
        *(undefined4 *)((int)param_1 + 0x68) = 0;
        uVar5 = Random__NextLCGAbs(DAT_008a9d9c);
        uVar5 = uVar5 & 0x8000ffff;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xffff0000) + 1;
        }
        *(float *)((int)param_1 + 0x70) = (float)(int)uVar5 * _DAT_005db1ec + _DAT_005d857c;
        CUnitAI__PlayCloseAnimationIfState0Or2(*(void **)((int)param_1 + 8));
        piVar1 = *(int **)((int)param_1 + 8);
        fStack_10 = (float)piVar1[0x14] * _DAT_005d85d0;
        fStack_c = -((float)piVar1[0x18] * _DAT_005d85d0);
        fStack_24 = (float)piVar1[0x10] * _DAT_005d85d0 + (float)piVar1[7];
        fStack_20 = fStack_10 + (float)piVar1[8];
        fStack_1c = fStack_c + (float)piVar1[9];
        (**(code **)(*piVar1 + 0xf4))(fStack_24,fStack_20,fStack_1c,fStack_18,0);
        return (double)fStack_18;
      }
    }
  }
  return (double)fStack_3c;
}
