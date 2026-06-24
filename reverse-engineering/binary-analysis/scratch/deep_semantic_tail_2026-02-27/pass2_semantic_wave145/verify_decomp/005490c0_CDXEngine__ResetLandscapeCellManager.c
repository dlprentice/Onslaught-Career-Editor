/* address: 0x005490c0 */
/* name: CDXEngine__ResetLandscapeCellManager */
/* signature: void __fastcall CDXEngine__ResetLandscapeCellManager(int param_1) */


void __fastcall CDXEngine__ResetLandscapeCellManager(int param_1)

{
  DAT_009c6334 = 0;
  CMemoryManager__UnlinkAndReleaseMutex((void *)(param_1 + 0x214));
  return;
}
