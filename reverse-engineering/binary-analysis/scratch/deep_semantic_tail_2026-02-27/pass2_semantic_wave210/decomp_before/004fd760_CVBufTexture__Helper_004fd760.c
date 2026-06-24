/* address: 0x004fd760 */
/* name: CVBufTexture__Helper_004fd760 */
/* signature: int __fastcall CVBufTexture__Helper_004fd760(int param_1) */


int __fastcall CVBufTexture__Helper_004fd760(int param_1)

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
    iVar2 = CUnit__Helper_0050a290(iVar2);
    if (iVar2 != 0) break;
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
