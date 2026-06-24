/* address: 0x00445f40 */
/* name: CUnitAI__Unk_00445f40 */
/* signature: double __fastcall CUnitAI__Unk_00445f40(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CUnitAI__Unk_00445f40(void *param_1)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  float10 fVar4;
  float fVar5;
  float fStack_28;
  float local_24;
  float local_20;
  float fStack_1c;
  undefined4 uStack_18;
  float local_10;
  float local_c;

  uVar2 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar2 = uVar2 & 0x8000ffff;
  if ((int)uVar2 < 0) {
    uVar2 = (uVar2 - 1 | 0xffff0000) + 1;
  }
  local_24 = (float)(int)uVar2 * _DAT_005d85f0 + _DAT_005d85ec;
  if (*(int *)((int)param_1 + 0xc) != 0) {
    fVar4 = (float10)(**(code **)(*(int *)param_1 + 0xc))();
    local_24 = (float)fVar4;
  }
  piVar1 = *(int **)((int)param_1 + 0xc);
  if (piVar1 == (int *)0x0) {
    iVar3 = (**(code **)(*(int *)param_1 + 0x14))();
    if (iVar3 != 0) {
      return (double)_DAT_005d856c;
    }
    (**(code **)(**(int **)((int)param_1 + 8) + 0x100))();
    return (double)local_24;
  }
  iVar3 = *(int *)((int)param_1 + 8);
  local_10 = (float)piVar1[7] - *(float *)(iVar3 + 0x1c);
  local_c = (float)piVar1[8] - *(float *)(iVar3 + 0x20);
  local_20 = *(float *)(iVar3 + 0x114);
  fStack_1c = *(float *)(iVar3 + 0x118);
  uStack_18 = *(undefined4 *)(iVar3 + 0x11c);
  fVar5 = SQRT(local_10 * local_10 + local_c * local_c);
  if (fVar5 <= _DAT_005d8ba4) {
    if (_DAT_005d85d8 < fVar5) {
      fVar4 = (float10)fpatan((float10)local_10,(float10)local_c);
      fStack_28 = (float)-fVar4;
      if (((float10)_DAT_005d85c8 <= -fVar4) || (local_20 <= _DAT_005d85e4)) {
        fVar5 = local_20;
        if ((_DAT_005d85e4 < fStack_28) && (local_20 < _DAT_005d85c8)) {
          fVar5 = local_20 + _DAT_005d85e0;
        }
      }
      else {
        fVar5 = local_20 - _DAT_005d85e0;
      }
      if (_DAT_005d85e4 < ABS(fStack_28 - fVar5)) {
        *(undefined4 *)((int)param_1 + 0x6c) = 0;
      }
    }
  }
  else {
    *(undefined4 *)((int)param_1 + 0x6c) = 1;
  }
  (**(code **)(*piVar1 + 0x168))(&local_20);
  fVar5 = fStack_1c - _DAT_005db1e4;
  fStack_1c = fVar5;
  if (*(int *)((int)param_1 + 0x6c) != 0) {
    (**(code **)(**(int **)((int)param_1 + 8) + 0xf4))(local_24,local_20,fVar5,uStack_18,0);
    return (double)fVar5;
  }
  CUnitAI__Helper_004fce40();
  return (double)fStack_28;
}
