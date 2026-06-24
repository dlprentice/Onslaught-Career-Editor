/* address: 0x005ab9c0 */
/* name: CTexture__Helper_005ab9c0 */
/* signature: void __stdcall CTexture__Helper_005ab9c0(void * param_1) */


void CTexture__Helper_005ab9c0(void *param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  int unaff_EBX;
  int iVar5;
  int *piVar6;

  puVar2 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x50);
  *(undefined4 **)((int)param_1 + 0x1ac) = puVar2;
  *puVar2 = &LAB_005ab950;
  if (unaff_EBX != 0) {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 4;
    (*(code *)*puVar1)(param_1);
  }
  if (*(int *)(*(int *)((int)param_1 + 0x1c8) + 8) == 0) {
    iVar3 = *(int *)((int)param_1 + 0x140);
  }
  else {
    if (*(int *)((int)param_1 + 0x140) < 2) {
      puVar1 = *(undefined4 **)param_1;
      puVar1[5] = 0x2f;
      (*(code *)*puVar1)(param_1);
    }
    CTexture__BuildComponentPlaneRowPointers();
    iVar3 = *(int *)((int)param_1 + 0x140) + 2;
  }
  iVar5 = 0;
  if (0 < *(int *)((int)param_1 + 0x24)) {
    piVar6 = (int *)(*(int *)((int)param_1 + 0xdc) + 0x24);
    puVar2 = puVar2 + 2;
    do {
      uVar4 = (**(code **)(*(int *)((int)param_1 + 4) + 8))
                        (param_1,1,piVar6[-2] * *piVar6,
                         ((piVar6[-6] * *piVar6) / *(int *)((int)param_1 + 0x140)) * iVar3);
      *puVar2 = uVar4;
      iVar5 = iVar5 + 1;
      puVar2 = puVar2 + 1;
      piVar6 = piVar6 + 0x15;
    } while (iVar5 < *(int *)((int)param_1 + 0x24));
  }
  return;
}
