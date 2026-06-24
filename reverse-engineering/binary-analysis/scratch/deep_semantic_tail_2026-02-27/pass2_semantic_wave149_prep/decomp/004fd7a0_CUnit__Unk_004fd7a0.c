/* address: 0x004fd7a0 */
/* name: CUnit__Unk_004fd7a0 */
/* signature: int __fastcall CUnit__Unk_004fd7a0(int param_1) */


int __fastcall CUnit__Unk_004fd7a0(int param_1)

{
  int *piVar1;
  bool bVar2;
  undefined3 extraout_var;
  int iVar3;

  piVar1 = *(int **)(param_1 + 0x18c);
  if (piVar1 == (int *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *piVar1;
  }
  while( true ) {
    if (iVar3 == 0) {
      return 0;
    }
    bVar2 = CUnit__Helper_004e4420(iVar3);
    if (CONCAT31(extraout_var,bVar2) != 0) break;
    piVar1 = (int *)piVar1[1];
    if (piVar1 == (int *)0x0) {
      iVar3 = 0;
    }
    else {
      iVar3 = *piVar1;
    }
  }
  return 1;
}
