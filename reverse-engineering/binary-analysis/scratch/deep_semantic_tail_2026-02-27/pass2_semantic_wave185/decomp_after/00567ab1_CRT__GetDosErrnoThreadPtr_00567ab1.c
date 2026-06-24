/* address: 0x00567ab1 */
/* name: CRT__GetDosErrnoThreadPtr_00567ab1 */
/* signature: int CRT__GetDosErrnoThreadPtr_00567ab1(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__GetDosErrnoThreadPtr_00567ab1(void)

{
  int iVar1;

  iVar1 = CRT__GetOrInitThreadLocalRecord();
  return iVar1 + 0xc;
}
