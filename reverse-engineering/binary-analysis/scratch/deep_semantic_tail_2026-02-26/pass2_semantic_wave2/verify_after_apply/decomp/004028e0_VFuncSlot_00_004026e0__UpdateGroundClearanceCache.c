/* address: 0x004028e0 */
/* name: VFuncSlot_00_004026e0__UpdateGroundClearanceCache */
/* signature: void __fastcall VFuncSlot_00_004026e0__UpdateGroundClearanceCache(int param_1) */


void __fastcall VFuncSlot_00_004026e0__UpdateGroundClearanceCache(int param_1)

{
  uint uVar1;
  float fVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  int local_8;

  iVar3 = *(int *)(param_1 + 0x18);
  local_8 = (int)(longlong)ROUND(*(float *)(iVar3 + 0x1c));
  iVar7 = local_8;
  if ((local_8 != *(int *)(param_1 + 0x24)) ||
     (local_8 = (int)(longlong)ROUND(*(float *)(iVar3 + 0x20)), local_8 != *(int *)(param_1 + 0x28))
     ) {
    *(int *)(param_1 + 0x24) = iVar7;
    local_8 = (int)(longlong)ROUND(*(float *)(iVar3 + 0x20));
    *(int *)(param_1 + 0x28) = local_8;
    fVar2 = *(float *)(iVar3 + 0x24);
    fVar5 = -DAT_006fbdfc;
    *(undefined4 *)(param_1 + 0x20) = 0x497423f0;
    local_8 = (int)(longlong)ROUND(*(float *)(iVar3 + 0x1c));
    iVar7 = local_8;
    local_8 = (int)(longlong)ROUND(*(float *)(iVar3 + 0x20));
    uVar9 = local_8 - 0x14;
    if ((int)uVar9 <= local_8 + 0x14) {
      uVar1 = iVar7 - 0x14;
      uVar6 = uVar1;
      fVar4 = DAT_006fbdf4;
      do {
        for (; DAT_006fbdf4 = fVar4, (int)uVar6 <= iVar7 + 0x14; uVar6 = uVar6 + 5) {
          uVar8 = CWorld__Helper_0047ea20(0x6fadc8,uVar6,uVar9);
          fVar4 = -((float)(int)(short)uVar8 * fVar4);
          if (fVar4 < fVar5) {
            fVar4 = fVar5;
          }
          fVar4 = -fVar2 - fVar4;
          if (fVar4 < *(float *)(param_1 + 0x20)) {
            *(float *)(param_1 + 0x20) = fVar4;
          }
          fVar4 = DAT_006fbdf4;
        }
        uVar9 = uVar9 + 5;
        uVar6 = uVar1;
      } while ((int)uVar9 <= local_8 + 0x14);
    }
  }
  return;
}
