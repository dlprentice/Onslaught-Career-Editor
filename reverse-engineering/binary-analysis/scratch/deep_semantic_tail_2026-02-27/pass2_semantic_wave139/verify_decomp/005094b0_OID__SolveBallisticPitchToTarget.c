/* address: 0x005094b0 */
/* name: OID__SolveBallisticPitchToTarget */
/* signature: double __thiscall OID__SolveBallisticPitchToTarget(void * this, int param_1, float param_2, float param_3, float param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall
OID__SolveBallisticPitchToTarget(void *this,int param_1,float param_2,float param_3,float param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float10 fVar8;
  float10 fVar9;
  float10 fVar10;
  float10 fVar11;
  float10 fVar12;
  float10 extraout_ST0;
  float local_3c;
  float fStack_30;
  float local_20;
  float local_1c;
  float local_18;
  int local_14;
  float local_8;

  piVar1 = *(int **)((int)this + 8);
  local_20 = (float)piVar1[7];
  local_1c = (float)piVar1[8];
  local_18 = (float)piVar1[9];
  local_14 = piVar1[10];
  if (*(int *)((int)this + 0x98) != 0) {
    (**(code **)(*piVar1 + 0x1c4))(&local_20);
  }
  fVar4 = (float)param_1 - local_20;
  fVar5 = param_2 - local_1c;
  iVar2 = *(int *)((int)this + 0xa0);
  local_3c = -0.7853982;
  local_8 = param_3 - local_18;
  iVar3 = *(int *)(iVar2 + 0x18);
  if (((*(float *)(iVar3 + 0x3c) * _DAT_005d8c6c != _DAT_005d856c) && (*(int *)(iVar3 + 0x50) == 0))
     && (*(int *)(iVar3 + 0x6c) == 0)) {
    fStack_30 = 99999.0;
    fVar6 = *(float *)(iVar3 + 0x2c) * _DAT_005d8584;
    fVar7 = *(float *)(iVar3 + 0x3c) * _DAT_005d8c6c;
    fVar8 = (float10)*(float *)(iVar2 + 0x80);
    if (*(float *)(iVar2 + 0x80) < *(float *)(iVar2 + 0x7c)) {
      fVar9 = (float10)fVar7 * (float10)(param_3 - *(float *)(*(int *)((int)this + 8) + 0x24));
      do {
        fVar10 = (float10)fsin(fVar8);
        fVar10 = fVar10 * (float10)fVar6;
        fVar11 = fVar10 * fVar10 + fVar9 + fVar9;
        if ((float10)_DAT_005d856c < fVar11) {
          fVar12 = (float10)fcos(fVar8);
          fVar10 = fVar12 * (float10)fVar6 * ((SQRT(fVar11) - fVar10) / (float10)fVar7);
          if (((float10)_DAT_005d856c < fVar10) &&
             (fVar10 = ABS(fVar10 - (float10)SQRT(fVar5 * fVar5 + fVar4 * fVar4)),
             fVar10 < (float10)fStack_30)) {
            fStack_30 = (float)fVar10;
            local_3c = (float)fVar8;
          }
        }
        fVar8 = fVar8 + (float10)_DAT_005d8cb8;
      } while (fVar8 < (float10)*(float *)(iVar2 + 0x7c));
    }
    return (double)local_3c;
  }
  if (SQRT(fVar5 * fVar5 + local_8 * local_8 + fVar4 * fVar4) <= _DAT_005d856c) {
    return (double)_DAT_005d856c;
  }
  OID__Helper_0055dcb0();
  return (double)extraout_ST0;
}
