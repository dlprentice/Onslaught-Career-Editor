/* address: 0x00590e10 */
/* name: CDXTexture__Helper_00590e10 */
/* signature: int __stdcall CDXTexture__Helper_00590e10(void * param_1, int param_2, int param_3) */


int CDXTexture__Helper_00590e10(void *param_1,int param_2,int param_3)

{
  int iVar1;
  undefined4 *puVar2;
  uint uVar3;
  void *pvVar4;
  void **ppvVar5;

  pvVar4 = param_1;
  iVar1 = *(int *)((int)param_1 + 0x14);
  if (iVar1 != 0xcd) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x14;
    puVar2[6] = iVar1;
    (*(code *)*puVar2)(param_1);
  }
  uVar3 = *(uint *)((int)pvVar4 + 0x74);
  if (uVar3 <= *(uint *)((int)pvVar4 + 0x8c)) {
    iVar1 = *(int *)pvVar4;
    *(undefined4 *)(iVar1 + 0x14) = 0x7b;
    (**(code **)(iVar1 + 4))(pvVar4,0xffffffff);
    return 0;
  }
  puVar2 = *(undefined4 **)((int)pvVar4 + 8);
  if (puVar2 != (undefined4 *)0x0) {
    puVar2[1] = *(uint *)((int)pvVar4 + 0x8c);
    puVar2[2] = uVar3;
    (*(code *)*puVar2)(pvVar4);
  }
  ppvVar5 = &param_1;
  param_1 = (void *)0x0;
  (**(code **)(*(int *)((int)pvVar4 + 0x1ac) + 4))(pvVar4,param_2,ppvVar5,param_3);
  *(int *)((int)pvVar4 + 0x8c) = *(int *)((int)pvVar4 + 0x8c) + (int)ppvVar5;
  return (int)ppvVar5;
}
