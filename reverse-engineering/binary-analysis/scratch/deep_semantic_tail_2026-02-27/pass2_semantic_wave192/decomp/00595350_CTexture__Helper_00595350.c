/* address: 0x00595350 */
/* name: CTexture__Helper_00595350 */
/* signature: void __stdcall CTexture__Helper_00595350(void * param_1) */


void CTexture__Helper_00595350(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;

  iVar2 = *(int *)((int)param_1 + 0x14);
  if ((iVar2 == 0x65) || (iVar2 == 0x66)) {
    if (*(uint *)((int)param_1 + 0xe8) < *(uint *)((int)param_1 + 0x20)) {
      puVar1 = *(undefined4 **)param_1;
      puVar1[5] = 0x43;
      (*(code *)*puVar1)(param_1);
    }
    (**(code **)(*(int *)((int)param_1 + 0x154) + 8))(param_1);
  }
  else if (iVar2 != 0x67) {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 0x14;
    puVar1[6] = iVar2;
    (*(code *)*puVar1)(param_1);
  }
  puVar1 = *(undefined4 **)((int)param_1 + 0x154);
  iVar2 = puVar1[4];
  while (iVar2 == 0) {
    (*(code *)*puVar1)(param_1);
    uVar3 = *(uint *)((int)param_1 + 0xf8);
    uVar4 = 0;
    if (uVar3 != 0) {
      do {
        puVar1 = *(undefined4 **)((int)param_1 + 8);
        if (puVar1 != (undefined4 *)0x0) {
          puVar1[1] = uVar4;
          puVar1[2] = uVar3;
          (*(code *)*puVar1)(param_1);
        }
        iVar2 = (**(code **)(*(int *)((int)param_1 + 0x160) + 4))(param_1,0);
        if (iVar2 == 0) {
          puVar1 = *(undefined4 **)param_1;
          puVar1[5] = 0x18;
          (*(code *)*puVar1)(param_1);
        }
        uVar3 = *(uint *)((int)param_1 + 0xf8);
        uVar4 = uVar4 + 1;
      } while (uVar4 < uVar3);
    }
    (**(code **)(*(int *)((int)param_1 + 0x154) + 8))(param_1);
    puVar1 = *(undefined4 **)((int)param_1 + 0x154);
    iVar2 = puVar1[4];
  }
  (**(code **)(*(int *)((int)param_1 + 0x164) + 0xc))(param_1);
  (**(code **)(*(int *)((int)param_1 + 0x18) + 0x10))(param_1);
  CDXTexture__PumpDecodeAllocatorAndSetStage((int)param_1);
  return;
}
