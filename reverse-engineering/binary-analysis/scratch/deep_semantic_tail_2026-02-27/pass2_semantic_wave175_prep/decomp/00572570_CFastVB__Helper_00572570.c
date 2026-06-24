/* address: 0x00572570 */
/* name: CFastVB__Helper_00572570 */
/* signature: double __stdcall CFastVB__Helper_00572570(int param_1) */


double CFastVB__Helper_00572570(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int local_4;

  iVar4 = 0;
  piVar5 = *(int **)(param_1 + 4);
  local_4 = 0;
  if (piVar5 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *(int *)(param_1 + 8) - (int)piVar5 >> 2;
  }
  iVar6 = iVar2;
  if (0 < iVar2) {
    do {
      iVar1 = *piVar5;
      if (*(int *)(iVar1 + 0x10) == 0) {
        iVar3 = 0;
      }
      else {
        iVar3 = *(int *)(iVar1 + 0x14) - *(int *)(iVar1 + 0x10) >> 2;
      }
      piVar5 = piVar5 + 1;
      iVar4 = iVar4 + (iVar3 - *(int *)(iVar1 + 0x28));
      iVar6 = iVar6 + -1;
      local_4 = iVar4;
    } while (iVar6 != 0);
  }
  return (double)local_4 / (double)iVar2;
}
