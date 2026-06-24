/* address: 0x0059bae0 */
/* name: CDXTexture__Unk_0059bae0 */
/* signature: int __stdcall CDXTexture__Unk_0059bae0(void * param_1, int param_2, uint param_3) */


int CDXTexture__Unk_0059bae0(void *param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *extraout_EAX;
  undefined4 *extraout_EAX_00;
  undefined4 *puVar4;
  int iVar5;
  uint uVar6;

  iVar1 = *(int *)((int)param_1 + 4);
  if (0x3b9ac9f0 < param_3) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x36;
    puVar2[6] = 1;
    (*(code *)*puVar2)(param_1);
  }
  if ((param_3 & 7) != 0) {
    param_3 = param_3 + (8 - (param_3 & 7));
  }
  if ((param_2 < 0) || (1 < param_2)) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0xe;
    puVar2[6] = param_2;
    (*(code *)*puVar2)(param_1);
  }
  puVar3 = *(undefined4 **)(iVar1 + 0x34 + param_2 * 4);
  puVar2 = (undefined4 *)0x0;
  while (puVar4 = puVar3, puVar4 != (undefined4 *)0x0) {
    if (param_3 <= (uint)puVar4[2]) goto LAB_0059bbf3;
    puVar2 = puVar4;
    puVar3 = (undefined4 *)*puVar4;
  }
  iVar5 = param_3 + 0x10;
  if (puVar2 == (undefined4 *)0x0) {
    uVar6 = *(uint *)(&DAT_005f37e4 + param_2 * 4);
  }
  else {
    uVar6 = *(uint *)(&DAT_005f37ec + param_2 * 4);
  }
  if (1000000000U - iVar5 < uVar6) {
    uVar6 = 1000000000U - iVar5;
  }
  CDXTexture__Unk_005b1c00((int)param_1,uVar6 + iVar5);
  puVar4 = extraout_EAX;
  while (puVar4 == (undefined4 *)0x0) {
    uVar6 = uVar6 >> 1;
    if (uVar6 < 0x32) {
      puVar3 = *(undefined4 **)param_1;
      puVar3[5] = 0x36;
      puVar3[6] = 2;
      (*(code *)*puVar3)(param_1);
    }
    CDXTexture__Unk_005b1c00((int)param_1,uVar6 + iVar5);
    puVar4 = extraout_EAX_00;
  }
  *(uint *)(iVar1 + 0x4c) = *(int *)(iVar1 + 0x4c) + uVar6 + iVar5;
  *puVar4 = 0;
  puVar4[1] = 0;
  puVar4[2] = uVar6 + param_3;
  if (puVar2 == (undefined4 *)0x0) {
    *(undefined4 **)(iVar1 + 0x34 + param_2 * 4) = puVar4;
  }
  else {
    *puVar2 = puVar4;
  }
LAB_0059bbf3:
  iVar1 = puVar4[1];
  puVar4[1] = iVar1 + param_3;
  puVar4[2] = puVar4[2] - param_3;
  return iVar1 + 0x10 + (int)puVar4;
}
