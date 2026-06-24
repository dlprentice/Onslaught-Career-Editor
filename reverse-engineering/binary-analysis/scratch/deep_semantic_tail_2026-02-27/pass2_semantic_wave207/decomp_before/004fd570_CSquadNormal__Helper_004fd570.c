/* address: 0x004fd570 */
/* name: CSquadNormal__Helper_004fd570 */
/* signature: int __fastcall CSquadNormal__Helper_004fd570(int param_1) */


int __fastcall CSquadNormal__Helper_004fd570(int param_1)

{
  int *piVar1;
  int iVar2;

  piVar1 = *(int **)(param_1 + 0x17c);
  if (piVar1 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1;
  }
  while( true ) {
    if (iVar2 == 0) {
      return 0;
    }
    if (*(int *)(iVar2 + 0x94) != 0) break;
    piVar1 = (int *)piVar1[1];
    if (piVar1 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar1;
    }
  }
  return 1;
}
