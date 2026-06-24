/* address: 0x0059c3f0 */
/* name: CDXTexture__ReleaseDecodeBankLists */
/* signature: void __stdcall CDXTexture__ReleaseDecodeBankLists(void * param_1, int param_2) */


void CDXTexture__ReleaseDecodeBankLists(void *param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;

  iVar1 = *(int *)((int)param_1 + 4);
  if ((param_2 < 0) || (1 < param_2)) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0xe;
    puVar2[6] = param_2;
    (*(code *)*puVar2)(param_1);
  }
  if (param_2 == 1) {
    for (iVar3 = *(int *)(iVar1 + 0x44); iVar3 != 0; iVar3 = *(int *)(iVar3 + 0x2c)) {
      if (*(int *)(iVar3 + 0x28) != 0) {
        *(undefined4 *)(iVar3 + 0x28) = 0;
        (**(code **)(iVar3 + 0x38))(param_1,iVar3 + 0x30);
      }
    }
    iVar3 = *(int *)(iVar1 + 0x48);
    *(undefined4 *)(iVar1 + 0x44) = 0;
    for (; iVar3 != 0; iVar3 = *(int *)(iVar3 + 0x2c)) {
      if (*(int *)(iVar3 + 0x28) != 0) {
        *(undefined4 *)(iVar3 + 0x28) = 0;
        (**(code **)(iVar3 + 0x38))(param_1,iVar3 + 0x30);
      }
    }
    *(undefined4 *)(iVar1 + 0x48) = 0;
  }
  puVar2 = *(undefined4 **)(iVar1 + 0x3c + param_2 * 4);
  *(undefined4 *)(iVar1 + 0x3c + param_2 * 4) = 0;
  while (puVar2 != (undefined4 *)0x0) {
    iVar3 = puVar2[2];
    iVar4 = puVar2[1];
    puVar5 = (undefined4 *)*puVar2;
    CDXTexture__Helper_005b1c30((int)param_1,(int)puVar2);
    *(int *)(iVar1 + 0x4c) = *(int *)(iVar1 + 0x4c) - (iVar3 + 0x10 + iVar4);
    puVar2 = puVar5;
  }
  puVar2 = *(undefined4 **)(iVar1 + 0x34 + param_2 * 4);
  *(undefined4 *)(iVar1 + 0x34 + param_2 * 4) = 0;
  while (puVar2 != (undefined4 *)0x0) {
    iVar3 = puVar2[2];
    iVar4 = puVar2[1];
    puVar5 = (undefined4 *)*puVar2;
    CDXTexture__Helper_005b1c30((int)param_1,(int)puVar2);
    *(int *)(iVar1 + 0x4c) = *(int *)(iVar1 + 0x4c) - (iVar3 + 0x10 + iVar4);
    puVar2 = puVar5;
  }
  return;
}
