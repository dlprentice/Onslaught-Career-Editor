/* address: 0x005954a0 */
/* name: CTexture__ReadDecodeInputBytes */
/* signature: void __stdcall CTexture__ReadDecodeInputBytes(void * param_1, int param_2, uint param_3) */


void CTexture__ReadDecodeInputBytes(void *param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  void *pvVar4;
  uint uVar5;
  uint uVar6;
  void **ppvVar7;

  pvVar4 = param_1;
  iVar1 = *(int *)((int)param_1 + 0x14);
  if (iVar1 != 0x65) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x14;
    puVar2[6] = iVar1;
    (*(code *)*puVar2)(param_1);
  }
  if (*(uint *)((int)pvVar4 + 0x20) <= *(uint *)((int)pvVar4 + 0xe8)) {
    iVar1 = *(int *)pvVar4;
    *(undefined4 *)(iVar1 + 0x14) = 0x7b;
    (**(code **)(iVar1 + 4))(pvVar4,0xffffffff);
  }
  puVar2 = *(undefined4 **)((int)pvVar4 + 8);
  if (puVar2 != (undefined4 *)0x0) {
    uVar3 = *(undefined4 *)((int)pvVar4 + 0x20);
    puVar2[1] = *(undefined4 *)((int)pvVar4 + 0xe8);
    puVar2[2] = uVar3;
    (*(code *)*puVar2)(pvVar4);
  }
  if (*(int *)(*(int *)((int)pvVar4 + 0x154) + 0xc) != 0) {
    (**(code **)(*(int *)((int)pvVar4 + 0x154) + 4))(pvVar4);
  }
  uVar5 = *(int *)((int)pvVar4 + 0x20) - *(int *)((int)pvVar4 + 0xe8);
  uVar6 = param_3;
  if (uVar5 < param_3) {
    uVar6 = uVar5;
  }
  ppvVar7 = &param_1;
  param_1 = (void *)0x0;
  (**(code **)(*(int *)((int)pvVar4 + 0x158) + 4))(pvVar4,param_2,ppvVar7,uVar6);
  *(int *)((int)pvVar4 + 0xe8) = *(int *)((int)pvVar4 + 0xe8) + (int)ppvVar7;
  return;
}
