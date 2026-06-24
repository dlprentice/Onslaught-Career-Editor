/* address: 0x00490e30 */
/* name: CGame__BuildCellMinMaxHeightTable */
/* signature: void __fastcall CGame__BuildCellMinMaxHeightTable(int param_1) */


void __fastcall CGame__BuildCellMinMaxHeightTable(int param_1)

{
  bool bVar1;
  uint uVar2;
  float *pfVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int local_14;
  uint local_10;
  int local_c;
  float *local_4;

  local_c = 0;
  local_4 = (float *)(param_1 + 0x13dc);
  do {
    iVar4 = 0;
    do {
      uVar6 = 0x7fff;
      local_10 = 0xffff8000;
      local_14 = 0;
      do {
        iVar5 = 0;
        do {
          uVar2 = CWorld__GetHeightSamplePacked16(param_1,iVar5 + iVar4,local_14 + local_c);
          if ((short)uVar2 < (short)uVar6) {
            uVar6 = uVar2;
          }
          bVar1 = (short)local_10 < (short)uVar2;
          if (bVar1) {
            local_10 = uVar2;
          }
          iVar5 = iVar5 + 1;
        } while (iVar5 < 9);
        local_14 = local_14 + 1;
      } while (local_14 < 9);
      iVar4 = iVar4 + 8;
      pfVar3 = local_4 + 2;
      *local_4 = *(float *)(param_1 + 0x102c) * (float)(int)(short)local_10;
      local_4[1] = *(float *)(param_1 + 0x102c) * (float)(int)(short)uVar6;
      local_4 = pfVar3;
    } while (iVar4 < 0x200);
    local_c = local_c + 8;
  } while (local_c < 0x200);
  return;
}
