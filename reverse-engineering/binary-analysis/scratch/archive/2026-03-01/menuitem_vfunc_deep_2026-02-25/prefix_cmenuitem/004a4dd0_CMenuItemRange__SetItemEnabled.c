/* address: 0x004a4dd0 */
/* name: CMenuItemRange__SetItemEnabled */
/* signature: undefined CMenuItemRange__SetItemEnabled(void) */


void __thiscall CMenuItemRange__SetItemEnabled(int param_1,int param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;

  piVar1 = *(int **)(param_1 + 8);
  *(int **)(param_1 + 0x10) = piVar1;
  if (piVar1 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1;
  }
  while (iVar2 != 0) {
    if (*(int *)(iVar2 + 8) == param_2) {
      *(undefined4 *)(iVar2 + 0x10) = param_3;
    }
    piVar1 = *(int **)(*(int *)(param_1 + 0x10) + 4);
    *(int **)(param_1 + 0x10) = piVar1;
    if (piVar1 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar1;
    }
  }
  return;
}
