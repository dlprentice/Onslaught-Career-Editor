/* address: 0x00593d0b */
/* name: CFastVB__Helper_00593d0b */
/* signature: void __stdcall CFastVB__Helper_00593d0b(void * param_1, void * param_2) */


void CFastVB__Helper_00593d0b(void *param_1,void *param_2)

{
  undefined1 uVar1;
  int iVar2;
  undefined1 *puVar3;

  if (*(char *)((int)param_1 + 9) == '\x10') {
    puVar3 = param_2;
    for (iVar2 = (uint)*(byte *)((int)param_1 + 10) * *(int *)param_1; iVar2 != 0;
        iVar2 = iVar2 + -1) {
      uVar1 = *(undefined1 *)param_2;
      param_2 = (void *)((int)param_2 + 2);
      *puVar3 = uVar1;
      puVar3 = puVar3 + 1;
    }
    *(undefined1 *)((int)param_1 + 9) = 8;
    *(byte *)((int)param_1 + 0xb) = *(byte *)((int)param_1 + 10) << 3;
    *(uint *)((int)param_1 + 4) = (uint)*(byte *)((int)param_1 + 10) * *(int *)param_1;
  }
  return;
}
