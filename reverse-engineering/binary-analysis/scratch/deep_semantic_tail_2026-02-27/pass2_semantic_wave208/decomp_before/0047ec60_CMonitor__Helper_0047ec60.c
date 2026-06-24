/* address: 0x0047ec60 */
/* name: CMonitor__Helper_0047ec60 */
/* signature: float * __fastcall CMonitor__Helper_0047ec60(int param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

float * __fastcall CMonitor__Helper_0047ec60(int param_1,void *param_2,void *param_3)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  float fVar5;
  uint uVar6;
  int iVar7;
  double dVar8;
  double dVar9;
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 local_18;
  undefined4 local_4;

  dVar8 = CRT__RoundDoubleWithFpuChecks((double)*(float *)param_3);
  local_20 = (uint)(longlong)ROUND((float)dVar8);
  uVar2 = local_20;
  dVar9 = CRT__RoundDoubleWithFpuChecks((double)*(float *)((int)param_3 + 4));
  local_20 = (uint)(longlong)ROUND((float)dVar9);
  if (((((int)uVar2 < 0) || (0x1ff < (int)(uVar2 + 1))) || ((int)local_20 < 0)) ||
     (0x1ff < (int)(local_20 + 1))) {
    *(undefined4 *)param_2 = 0;
    *(undefined4 *)((int)param_2 + 4) = 0;
    *(undefined4 *)((int)param_2 + 8) = 0x3f800000;
    return param_2;
  }
  uVar6 = uVar2 & 0x80000007;
  if ((int)uVar6 < 0) {
    uVar6 = (uVar6 - 1 | 0xfffffff8) + 1;
  }
  uVar4 = local_20 & 0x80000007;
  if ((int)uVar4 < 0) {
    uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
  }
  iVar1 = *(int *)(param_1 + 0x1028) +
          (((int)(uVar2 + ((int)uVar2 >> 0x1f & 7U)) >> 3) * 0x40 +
          ((int)(local_20 + ((int)local_20 >> 0x1f & 7U)) >> 3)) * 0xa2;
  iVar3 = uVar6 + uVar4 * 8;
  if (_DAT_005d8568 <
      (*(float *)param_3 - (float)dVar8) + (*(float *)((int)param_3 + 4) - (float)dVar9)) {
    iVar3 = uVar4 + iVar3;
    iVar7 = (int)*(short *)(iVar1 + 0x14 + iVar3 * 2);
    fVar5 = (float)(*(short *)(iVar1 + (uVar6 + (uVar4 + 1) * 9) * 2) - iVar7) *
            *(float *)(param_1 + 0x102c) * _DAT_005d8be0;
    uStack_1c = (float)(*(short *)(iVar1 + 2 + iVar3 * 2) - iVar7) * *(float *)(param_1 + 0x102c) *
                _DAT_005d8be0;
    local_18 = SQRT(fVar5 * fVar5 + uStack_1c * uStack_1c + _DAT_005d8568);
    if (local_18 != _DAT_005d856c) {
      local_18 = _DAT_005d8568 / local_18;
      fVar5 = fVar5 * local_18;
      uStack_1c = uStack_1c * local_18;
      local_18 = local_18 * -1.0;
      goto LAB_0047ee02;
    }
  }
  else {
    iVar3 = iVar3 + uVar4;
    iVar7 = (int)*(short *)(iVar1 + iVar3 * 2);
    fVar5 = (float)(*(short *)(iVar1 + 2 + iVar3 * 2) - iVar7) * *(float *)(param_1 + 0x102c);
    uStack_1c = (float)(*(short *)(iVar1 + (uVar6 + (uVar4 + 1) * 9) * 2) - iVar7) *
                *(float *)(param_1 + 0x102c);
    local_18 = SQRT(fVar5 * fVar5 + uStack_1c * uStack_1c + _DAT_005d8568);
    if (local_18 != _DAT_005d856c) {
      local_18 = _DAT_005d8568 / local_18;
      fVar5 = fVar5 * local_18;
      uStack_1c = uStack_1c * local_18;
      local_18 = local_18 * -1.0;
      goto LAB_0047ee02;
    }
  }
  local_18 = -1.0;
LAB_0047ee02:
  *(float *)param_2 = fVar5;
  *(float *)((int)param_2 + 4) = uStack_1c;
  *(float *)((int)param_2 + 8) = local_18;
  *(undefined4 *)((int)param_2 + 0xc) = local_4;
  return param_2;
}
