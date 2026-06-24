/* address: 0x004bdff0 */
/* name: CWorld__Helper_004bdff0 */
/* signature: void CWorld__Helper_004bdff0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWorld__Helper_004bdff0(void)

{
  int iVar1;
  int local_4;

  DXMemBuffer__ReadBytes(&local_4,4);
  if (local_4 == 1) {
    iVar1 = 0x8000;
    do {
      DXMemBuffer__ReadBytes(&stack0x00000004,1);
      iVar1 = iVar1 + -1;
    } while (iVar1 != 0);
  }
  else if (local_4 == 2) {
    iVar1 = 0x2000;
    do {
      DXMemBuffer__ReadBytes(&stack0x00000004,1);
      iVar1 = iVar1 + -1;
    } while (iVar1 != 0);
    return;
  }
  return;
}
