/* address: 0x004a52b0 */
/* name: CMesh__ClearAllUsageMarkers */
/* signature: void CMesh__ClearAllUsageMarkers(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CMesh__ClearAllUsageMarkers(void)

{
  int iVar1;

  for (iVar1 = DAT_00704ad8; iVar1 != 0; iVar1 = *(int *)(iVar1 + 0x158)) {
    *(undefined4 *)(iVar1 + 0x170) = 0;
  }
  CLTShell__Helper_004a52d0();
  return;
}
