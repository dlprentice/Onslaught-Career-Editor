/* address: 0x00414010 */
/* name: CMonitor__Unk_00414010 */
/* signature: void CMonitor__Unk_00414010(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CMonitor__Unk_00414010(void)

{
  int iVar1;
  void *in_ECX;

  iVar1 = CGeneralVolume__Unk_00414030(in_ECX);
  if (iVar1 != 0) {
    *(undefined4 *)(iVar1 + 0x60) = 0;
  }
  return;
}
