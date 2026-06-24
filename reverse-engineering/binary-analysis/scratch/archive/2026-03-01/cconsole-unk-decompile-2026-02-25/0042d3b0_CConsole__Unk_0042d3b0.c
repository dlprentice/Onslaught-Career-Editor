/* address: 0x0042d3b0 */
/* name: CConsole__Unk_0042d3b0 */
/* signature: int CConsole__Unk_0042d3b0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CConsole__Unk_0042d3b0(void)

{
  BOOL BVar1;
  tagPOINT local_8;

  if (DAT_0066e950 != (int *)0x0) {
    (**(code **)(*DAT_0066e950 + 0x20))(DAT_0066e950);
    CVBufTexture__Unk_005234d0(0);
    if (DAT_0066e950 != (int *)0x0) {
      (**(code **)(*DAT_0066e950 + 8))(DAT_0066e950);
      DAT_0066e950 = (int *)0x0;
    }
  }
  if (g_bDevModeEnabled == 0) {
    BVar1 = GetCursorPos(&local_8);
    if (BVar1 != 0) {
      DAT_0089bda8 = local_8.x;
      DAT_0089bda4 = local_8.y;
    }
  }
  CProfiler__ResetAll();
  return 0;
}
