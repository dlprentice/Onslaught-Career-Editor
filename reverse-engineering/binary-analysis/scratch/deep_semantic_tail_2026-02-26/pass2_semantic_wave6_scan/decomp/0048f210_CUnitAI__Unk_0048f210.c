/* address: 0x0048f210 */
/* name: CUnitAI__Unk_0048f210 */
/* signature: void __fastcall CUnitAI__Unk_0048f210(int param_1) */


void __fastcall CUnitAI__Unk_0048f210(int param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  float *local_18;
  uint local_14;
  float local_10;
  int local_c;
  int local_8;
  float local_4;

  CVBuffer__Lock(&local_18);
  uVar2 = *(uint *)(param_1 + 0x30);
  local_8 = *(int *)(param_1 + 0x44) + 1;
  local_10 = (float)uVar2;
  iVar3 = local_8;
  if (local_8 != 0) {
    do {
      local_c = iVar3;
      local_10 = (float)(int)uVar2;
      uVar4 = *(uint *)(param_1 + 0x2c);
      iVar3 = local_8;
      do {
        *local_18 = (float)(int)uVar4;
        local_18[1] = local_10;
        local_4 = DAT_006fbdf4;
        local_14 = uVar4;
        uVar1 = CWorld__Helper_0047ea20(0x6fadc8,uVar4,uVar2);
        local_18[2] = (float)(int)(short)uVar1 * local_4;
        local_18[3] = *local_18;
        local_18[4] = local_18[1];
        local_18 = local_18 + 5;
        uVar4 = uVar4 + *(int *)(param_1 + 0x34);
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
      uVar2 = uVar2 + *(int *)(param_1 + 0x34);
      iVar3 = local_c + -1;
    } while (local_c + -1 != 0);
    local_c = 0;
    local_14 = uVar4;
    local_10 = (float)uVar2;
  }
  CVBuffer__Unlock();
  *(undefined4 *)(param_1 + 0x40) = 1;
  return;
}
