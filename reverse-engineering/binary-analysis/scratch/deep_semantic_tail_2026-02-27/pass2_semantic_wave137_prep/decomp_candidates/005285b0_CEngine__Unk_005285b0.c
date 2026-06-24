/* address: 0x005285b0 */
/* name: CEngine__Unk_005285b0 */
/* signature: void CEngine__Unk_005285b0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CEngine__Unk_005285b0(void)

{
  if (DAT_0089bec8 != (int *)0x0) {
    (**(code **)(*DAT_0089bec8 + 0x48))(DAT_0089bec8);
    ResetEvent(DAT_0089bec4);
    ResetEvent(DAT_0089bec0);
    ResetEvent(CEngine__Unk_00528540);
  }
  return;
}
