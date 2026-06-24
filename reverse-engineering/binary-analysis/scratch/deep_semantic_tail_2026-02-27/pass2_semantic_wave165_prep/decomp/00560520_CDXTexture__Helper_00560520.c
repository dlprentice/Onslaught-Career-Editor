/* address: 0x00560520 */
/* name: CDXTexture__Helper_00560520 */
/* signature: int CDXTexture__Helper_00560520(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Helper_00560520(void)

{
  int iVar1;
  int *piVar2;
  int in_stack_00000014;
  int in_stack_00000018;
  int in_stack_0000001c;
  uint local_c;
  uint local_8;

  iVar1 = CTexture__Helper_00560b93();
  if ((*(int *)(iVar1 + 0x68) != 0) && (iVar1 = CDXTexture__Helper_0055d7e0(), iVar1 != 0)) {
    return iVar1;
  }
  piVar2 = (int *)CDXTexture__Helper_0055d90b
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
