/* address: 0x00599258 */
/* name: CFastVB__ComputeNodeSpanAndStride */
/* signature: int __stdcall CFastVB__ComputeNodeSpanAndStride(int param_1, void * param_2, void * param_3) */


int CFastVB__ComputeNodeSpanAndStride(int param_1,void *param_2,void *param_3)

{
  int iVar1;
  uint uVar2;
  void *pvVar3;
  int iVar4;
  uint *puVar5;
  uint *puVar6;

  puVar6 = param_2;
  iVar4 = param_1;
  puVar5 = param_3;
  if (param_3 == (void *)0x0) {
    puVar5 = (uint *)&param_1;
  }
  iVar1 = *(int *)(param_1 + 4);
  if (iVar1 == 8) {
    iVar4 = *(int *)(param_1 + 0x10);
    puVar6 = puVar5;
    if ((iVar4 == 1) || (iVar4 == 0)) {
      *(undefined4 *)param_2 = 1;
      uVar2 = *(uint *)(param_1 + 0x1c);
    }
    else {
      if (iVar4 != 2) {
        return -0x7fffbffb;
      }
      *(undefined4 *)param_2 = *(undefined4 *)(param_1 + 0x1c);
      uVar2 = *(uint *)(param_1 + 0x18);
    }
  }
  else {
    if (iVar1 != 7) {
      if (iVar1 != 1) {
        return -0x7fffbffb;
      }
      *(undefined4 *)param_2 = 0;
      *puVar5 = 0;
      do {
        iVar1 = CFastVB__ComputeNodeSpanAndStride
                          (*(int *)(*(int *)(*(int *)(iVar4 + 8) + 0x18) + 0x20),&param_3,&param_2);
        if (iVar1 < 0) {
          return iVar1;
        }
        *puVar6 = *puVar6 + (int)param_3;
        pvVar3 = (void *)*puVar5;
        if ((void *)*puVar5 < param_2) {
          pvVar3 = param_2;
        }
        *puVar5 = (uint)pvVar3;
        iVar4 = *(int *)(iVar4 + 0xc);
      } while (iVar4 != 0);
      return 0;
    }
    iVar1 = CFastVB__ComputeNodeSpanAndStride(*(int *)(param_1 + 0x10),param_2,puVar5);
    if (iVar1 < 0) {
      return iVar1;
    }
    uVar2 = *(int *)(iVar4 + 0x14) * *puVar6;
  }
  *puVar6 = uVar2;
  return 0;
}
