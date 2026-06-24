/* address: 0x004fd7e0 */
/* name: CUnit__Unk_004fd7e0 */
/* signature: int __fastcall CUnit__Unk_004fd7e0(int param_1) */


int __fastcall CUnit__Unk_004fd7e0(int param_1)

{
  int *piVar1;
  bool bVar2;
  int iVar3;
  undefined3 extraout_var;
  int iVar4;

  piVar1 = *(int **)(param_1 + 0x18c);
  if (piVar1 == (int *)0x0) {
    iVar4 = 0;
  }
  else {
    iVar4 = *piVar1;
  }
  while( true ) {
    if (iVar4 == 0) {
      return 1;
    }
    iVar3 = CSpawnerThng__IsSpawnComplete();
    if ((iVar3 == 0) ||
       (bVar2 = CSpawnerThng__Unk_004e4420(iVar4), CONCAT31(extraout_var,bVar2) != 0)) break;
    piVar1 = (int *)piVar1[1];
    if (piVar1 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar1;
    }
  }
  return 0;
}
