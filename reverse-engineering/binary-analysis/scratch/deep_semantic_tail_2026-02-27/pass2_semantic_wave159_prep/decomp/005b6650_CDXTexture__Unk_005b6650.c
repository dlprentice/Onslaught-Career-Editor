/* address: 0x005b6650 */
/* name: CDXTexture__Unk_005b6650 */
/* signature: void __fastcall CDXTexture__Unk_005b6650(void * param_1, int param_2, int param_3) */


void __fastcall CDXTexture__Unk_005b6650(void *param_1,int param_2,int param_3)

{
  int iVar1;
  int in_EAX;
  byte *pbVar2;
  int iVar3;
  int iVar4;
  undefined1 *puVar5;
  uint uVar6;
  int local_18;
  int local_10;

  iVar4 = *(int *)(param_2 + 0x1c) << 3;
  CDXTexture__Helper_005b6290
            ((int)param_1,*(int *)(in_EAX + 0xf4),*(int *)(in_EAX + 0x1c),
             *(int *)(param_2 + 0x1c) * 0x10);
  iVar1 = *(int *)(param_2 + 0xc);
  local_10 = 0;
  if (0 < iVar1) {
    do {
      puVar5 = *(undefined1 **)(param_3 + local_10 * 4);
      pbVar2 = *(byte **)param_1;
      uVar6 = 1;
      if (iVar4 != 0) {
        iVar3 = *(int *)((int)param_1 + 4) - (int)pbVar2;
        local_18 = iVar4;
        do {
          *puVar5 = (char)((int)((uint)*pbVar2 +
                                pbVar2[1] + uVar6 + (uint)pbVar2[iVar3 + 1] + (uint)pbVar2[iVar3])
                          >> 2);
          puVar5 = puVar5 + 1;
          uVar6 = uVar6 ^ 3;
          pbVar2 = pbVar2 + 2;
          local_18 = local_18 + -1;
        } while (local_18 != 0);
      }
      param_1 = (void *)((int)param_1 + 8);
      local_10 = local_10 + 1;
    } while (local_10 < iVar1);
  }
  return;
}
