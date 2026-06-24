/* address: 0x005b61e0 */
/* name: CDXTexture__Helper_005b61e0 */
/* signature: void __stdcall CDXTexture__Helper_005b61e0(void * param_1, int param_2) */


void CDXTexture__Helper_005b61e0(void *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;
  int *piVar6;

  if (param_2 != 0) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 4;
    (*(code *)*puVar3)(param_1);
  }
  puVar3 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x40);
  iVar1 = *(int *)(*(int *)((int)param_1 + 0x16c) + 8);
  *(undefined4 **)((int)param_1 + 0x15c) = puVar3;
  *puVar3 = &LAB_005b5c30;
  if (iVar1 == 0) {
    iVar1 = *(int *)((int)param_1 + 0x3c);
    iVar2 = *(int *)((int)param_1 + 0x44);
    iVar5 = 0;
    puVar3[1] = &LAB_005b5c80;
    if (0 < iVar1) {
      piVar6 = (int *)(iVar2 + 8);
      puVar3 = puVar3 + 2;
      do {
        uVar4 = (**(code **)(*(int *)((int)param_1 + 4) + 8))
                          (param_1,1,(piVar6[5] * *(int *)((int)param_1 + 0xf0) * 8) / *piVar6,
                           *(undefined4 *)((int)param_1 + 0xf4));
        *puVar3 = uVar4;
        iVar5 = iVar5 + 1;
        puVar3 = puVar3 + 1;
        piVar6 = piVar6 + 0x15;
      } while (iVar5 < *(int *)((int)param_1 + 0x3c));
    }
    return;
  }
  puVar3[1] = &LAB_005b5e90;
  CDXTexture__Helper_005b60a0((int)param_1);
  return;
}
