/* address: 0x00579b39 */
/* name: CFastVB__Helper_00579b39 */
/* signature: int __stdcall CFastVB__Helper_00579b39(void * param_1, uint param_2, void * param_3) */


int CFastVB__Helper_00579b39(void *param_1,uint param_2,void *param_3)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  byte *pbVar5;
  byte *pbVar6;
  bool bVar7;
  uint local_8;

  uVar4 = 0;
  if (param_1 == (void *)0x0) {
    iVar2 = -0x7789f794;
  }
  else {
    local_8 = 0x26;
    do {
      uVar3 = local_8 + uVar4 >> 1;
      pbVar5 = *(byte **)(&UNK_005e9340 + uVar3 * 0xc);
      pbVar6 = param_1;
      do {
        bVar1 = *pbVar5;
        bVar7 = bVar1 < *pbVar6;
        if (bVar1 != *pbVar6) {
LAB_00579b87:
          iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
          goto LAB_00579b8c;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar5[1];
        bVar7 = bVar1 < pbVar6[1];
        if (bVar1 != pbVar6[1]) goto LAB_00579b87;
        pbVar5 = pbVar5 + 2;
        pbVar6 = pbVar6 + 2;
      } while (bVar1 != 0);
      iVar2 = 0;
LAB_00579b8c:
      if (iVar2 == 0) {
        iVar2 = uVar3 * 0xc;
        if ((*(uint *)(&UNK_005e9348 + iVar2) & param_2) == param_2) {
          if (param_3 != (void *)0x0) {
            *(undefined4 *)param_3 = *(undefined4 *)(&UNK_005e9340 + iVar2);
            *(undefined4 *)((int)param_3 + 4) = *(undefined4 *)(&UNK_005e9344 + iVar2);
            *(undefined4 *)((int)param_3 + 8) = *(undefined4 *)(&UNK_005e9348 + iVar2);
          }
          return 0;
        }
        break;
      }
      if (iVar2 < 0) {
        uVar4 = uVar3 + 1;
        uVar3 = local_8;
      }
      local_8 = uVar3;
    } while (uVar4 < local_8);
    iVar2 = -0x7fffbffb;
  }
  return iVar2;
}
