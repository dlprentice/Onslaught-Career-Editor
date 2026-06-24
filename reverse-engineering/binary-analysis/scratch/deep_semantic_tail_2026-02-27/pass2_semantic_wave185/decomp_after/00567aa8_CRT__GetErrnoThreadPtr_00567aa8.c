/* address: 0x00567aa8 */
/* name: CRT__GetErrnoThreadPtr_00567aa8 */
/* signature: int CRT__GetErrnoThreadPtr_00567aa8(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__GetErrnoThreadPtr_00567aa8(void)

{
  int iVar1;

  iVar1 = CRT__GetOrInitThreadLocalRecord();
  return iVar1 + 8;
}
