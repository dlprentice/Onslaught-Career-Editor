/* address: 0x005099a0 */
/* name: CUnit__Helper_005099a0 */
/* signature: double __thiscall CUnit__Helper_005099a0(void * this, void * param_1, float param_2, float param_3, float param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall
CUnit__Helper_005099a0(void *this,void *param_1,float param_2,float param_3,float param_4)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  int iVar7;
  int extraout_EAX;
  void *unaff_ESI;
  float10 fVar8;
  float10 fVar9;
  float10 fVar10;
  float local_20;
  float local_18;
  undefined1 local_10 [16];

  if ((*(int *)((int)this + 0xa0) == 0) ||
     (iVar7 = *(int *)(*(int *)((int)this + 0xa0) + 0x18), iVar7 == 0)) {
    fVar8 = (float10)_DAT_005d856c;
  }
  else {
    iVar7 = CEngine__CanUseBallisticArcNoLocks(iVar7);
    if (iVar7 == 0) {
      return (double)*(float *)(*(int *)((int)this + 0xa0) + 0x78);
    }
    if ((((float)param_1 == _DAT_005d856c) && (param_2 == _DAT_005d856c)) &&
       (param_3 == _DAT_005d856c)) {
      fVar8 = (float10)_DAT_005d856c;
    }
    else {
      OID__Helper_0044a850(this,(int)local_10,unaff_ESI);
      fVar8 = (float10)param_3 - (float10)*(float *)(extraout_EAX + 8);
    }
    iVar7 = *(int *)((int)this + 0xa0);
    fVar3 = *(float *)(iVar7 + 0x80);
    fVar5 = *(float *)(*(int *)(iVar7 + 0x18) + 0x2c) * _DAT_005d8584;
    fVar6 = *(float *)(*(int *)(iVar7 + 0x18) + 0x3c) * _DAT_005d8c6c;
    fVar4 = *(float *)(iVar7 + 0x7c);
    if (((_DAT_005d8dec < fVar4) && (_DAT_005d8dec < fVar3)) ||
       ((fVar4 < _DAT_005d8dec && (fVar3 < _DAT_005d8dec)))) {
      fVar9 = (float10)fsin((float10)fVar4);
      fVar1 = (float)fVar9;
      fVar8 = fVar8 * (float10)fVar6 + fVar8 * (float10)fVar6;
      fVar9 = (float10)fcos((float10)fVar4);
      fVar4 = (float)((fVar9 * (SQRT(ABS((float10)fVar1 * (float10)fVar1 * (float10)fVar5 *
                                         (float10)fVar5 - fVar8)) - (float10)fVar1 * (float10)fVar5)
                      * (float10)fVar5) / (float10)fVar6);
      fVar9 = (float10)fsin((float10)fVar3);
      fVar10 = (float10)fcos((float10)fVar3);
      fVar8 = (fVar10 * (SQRT(ABS(fVar9 * (float10)(float)fVar9 * (float10)fVar5 * (float10)fVar5 -
                                  fVar8)) - (float10)(float)fVar9 * (float10)fVar5) * (float10)fVar5
              ) / (float10)fVar6;
      if (fVar8 < (float10)fVar4) {
        return (double)fVar4;
      }
    }
    else {
      fVar9 = (float10)fsin((float10)fVar4);
      fVar1 = (float)(fVar9 * (float10)fVar5);
      fVar2 = (float)((float10)fVar6 * fVar8 + (float10)fVar6 * fVar8);
      fVar8 = (float10)fcos((float10)fVar4);
      fVar8 = fVar8 * (float10)fVar5 *
              ((SQRT((float10)fVar1 * (float10)fVar1 + (float10)fVar2) - (float10)fVar1) /
              (float10)fVar6);
      local_20 = (float)fVar8;
      if (fVar8 < (float10)_DAT_005d856c) {
        local_20 = 0.0;
      }
      fVar8 = (float10)fsin((float10)fVar3);
      fVar8 = fVar8 * (float10)fVar5;
      fVar9 = (float10)fcos((float10)fVar3);
      fVar8 = fVar9 * (float10)fVar5 *
              ((SQRT(fVar8 * fVar8 + (float10)fVar2) - fVar8) / (float10)fVar6);
      local_18 = (float)fVar8;
      if (fVar8 < (float10)_DAT_005d856c) {
        local_18 = 0.0;
      }
      fVar8 = (float10)fsin((float10)_DAT_005dfca8);
      fVar8 = fVar8 * (float10)fVar5;
      fVar9 = (float10)fcos((float10)_DAT_005dfca8);
      fVar8 = fVar9 * (float10)fVar5 *
              ((SQRT(fVar8 * fVar8 + (float10)fVar2) - fVar8) / (float10)fVar6);
      param_1 = (void *)(float)fVar8;
      if (fVar8 < (float10)_DAT_005d856c) {
        param_1 = (void *)0x0;
      }
      if (local_20 < local_18) {
        local_20 = local_18;
      }
      fVar8 = (float10)local_20;
      if (fVar8 < (float10)(float)param_1) {
        return (double)(float)param_1;
      }
    }
  }
  return (double)fVar8;
}
