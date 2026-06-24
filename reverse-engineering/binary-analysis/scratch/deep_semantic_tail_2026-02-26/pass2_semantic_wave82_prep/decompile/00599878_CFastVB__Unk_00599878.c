/* address: 0x00599878 */
/* name: CFastVB__Unk_00599878 */
/* signature: int __fastcall CFastVB__Unk_00599878(int param_1) */


int __fastcall CFastVB__Unk_00599878(int param_1)

{
  void *extraout_EAX;
  undefined4 *puVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int *piVar5;
  uint local_c;

  CFastVB__Helper_00426fd0(0x60);
  if (extraout_EAX == (void *)0x0) {
    puVar1 = (undefined4 *)0x0;
  }
  else {
    puVar1 = (undefined4 *)CFastVB__Unk_005997a5(extraout_EAX);
  }
  if (puVar1 == (undefined4 *)0x0) {
    return 0;
  }
  puVar3 = (undefined4 *)(param_1 + 0x10);
  puVar4 = puVar1 + 4;
  for (iVar2 = 8; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar4 = *puVar3;
    puVar3 = puVar3 + 1;
    puVar4 = puVar4 + 1;
  }
  puVar1[0xc] = *(undefined4 *)(param_1 + 0x30);
  puVar1[0xd] = *(undefined4 *)(param_1 + 0x34);
  puVar1[0xe] = *(undefined4 *)(param_1 + 0x38);
  puVar1[0x15] = *(undefined4 *)(param_1 + 0x54);
  puVar1[0x16] = *(undefined4 *)(param_1 + 0x58);
  if (*(int **)(param_1 + 0x3c) == (int *)0x0) {
LAB_005998f4:
    if (*(int **)(param_1 + 0x40) != (int *)0x0) {
      iVar2 = (**(code **)(**(int **)(param_1 + 0x40) + 8))();
      puVar1[0x10] = iVar2;
      if (iVar2 == 0) goto LAB_005998e8;
    }
    local_c = 0;
    piVar5 = (int *)(param_1 + 0x44);
    do {
      if ((int *)*piVar5 != (int *)0x0) {
        iVar2 = (**(code **)(*(int *)*piVar5 + 8))();
        *(int *)(((int)puVar1 - param_1) + (int)piVar5) = iVar2;
        if (iVar2 == 0) goto LAB_005998e8;
      }
      local_c = local_c + 1;
      piVar5 = piVar5 + 1;
    } while (local_c < 4);
  }
  else {
    iVar2 = (**(code **)(**(int **)(param_1 + 0x3c) + 8))();
    puVar1[0xf] = iVar2;
    if (iVar2 != 0) goto LAB_005998f4;
LAB_005998e8:
    (**(code **)*puVar1)(1);
    puVar1 = (undefined4 *)0x0;
  }
  return (int)puVar1;
}
