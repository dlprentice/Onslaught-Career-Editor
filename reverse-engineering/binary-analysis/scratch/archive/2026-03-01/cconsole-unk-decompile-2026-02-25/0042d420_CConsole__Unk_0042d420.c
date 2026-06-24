/* address: 0x0042d420 */
/* name: CConsole__Unk_0042d420 */
/* signature: int CConsole__Unk_0042d420(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CConsole__Unk_0042d420(void)

{
  int iVar1;

  if (DAT_0066e950 != (int *)0x0) {
    DAT_0066e8f0 = 0;
    DAT_0066e8f4 = 0;
    DAT_0066e8f8 = 0;
    DAT_0066e8fc = 0;
    _DAT_0066e900 = 0;
    iVar1 = (**(code **)(*DAT_0066e950 + 0x24))(DAT_0066e950,0x14,&DAT_0066e8f0);
    if (iVar1 < 0) {
      iVar1 = (**(code **)(*DAT_0066e950 + 0x1c))(DAT_0066e950);
      while (iVar1 == -0x7ff8ffe2) {
        iVar1 = (**(code **)(*DAT_0066e950 + 0x1c))(DAT_0066e950);
      }
      return -1;
    }
    if (g_bDevModeEnabled == 0) {
      DAT_0089bda8 = DAT_0089bda8 + DAT_0066e8f0;
      DAT_0089bda4 = DAT_0089bda4 + DAT_0066e8f4;
      DAT_0089be48 = DAT_0089be48 + DAT_0066e8f8;
    }
  }
  return 0;
}
