/* address: 0x00562ab1 */
/* name: CRT__MapFpStatusToErrorCode */
/* signature: int __cdecl CRT__MapFpStatusToErrorCode(int param_1) */


int __cdecl CRT__MapFpStatusToErrorCode(int param_1)

{
  int *piVar1;
  int iVar2;

  iVar2 = 0;
  piVar1 = &DAT_00653768;
  do {
    if (*piVar1 == param_1) {
      return *(int *)(iVar2 * 8 + 0x65376c);
    }
    piVar1 = piVar1 + 2;
    iVar2 = iVar2 + 1;
  } while ((int)piVar1 < 0x653840);
  return 0;
}
