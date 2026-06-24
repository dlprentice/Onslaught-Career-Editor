/* address: 0x00560520 */
/* name: CRT__ValidateCatchHandlersForThrow */
/* signature: int CRT__ValidateCatchHandlersForThrow(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__ValidateCatchHandlersForThrow(void)

{
  int iVar1;
  int *piVar2;
  int in_stack_00000014;
  int in_stack_00000018;
  int in_stack_0000001c;
  uint local_c;
  uint local_8;

  iVar1 = CTexture__Helper_00560b93();
  if ((*(int *)(iVar1 + 0x68) != 0) && (iVar1 = CRT__CallExceptionTranslator(), iVar1 != 0)) {
    return iVar1;
  }
  piVar2 = (int *)CRT__GetRangeOfTryBlocksForState
                            (in_stack_00000014,in_stack_0000001c,in_stack_00000018,&local_8,&local_c
                            );
  for (; local_8 < local_c; local_8 = local_8 + 1) {
    if (((*piVar2 <= in_stack_00000018) && (in_stack_00000018 <= piVar2[1])) &&
       ((iVar1 = *(int *)(piVar2[3] * 0x10 + piVar2[4] + -0xc), iVar1 == 0 ||
        (*(char *)(iVar1 + 8) == '\0')))) {
      CRT__SehUnwindAndResumeSearch();
    }
    piVar2 = piVar2 + 5;
  }
  return local_8;
}
