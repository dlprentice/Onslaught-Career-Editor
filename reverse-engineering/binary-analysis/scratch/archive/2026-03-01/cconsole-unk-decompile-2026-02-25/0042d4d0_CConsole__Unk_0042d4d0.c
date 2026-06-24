/* address: 0x0042d4d0 */
/* name: CConsole__Unk_0042d4d0 */
/* signature: int CConsole__Unk_0042d4d0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CConsole__Unk_0042d4d0(void)

{
  int iVar1;
  bool bVar2;

  if ((DAT_0066e950 != (int *)0x0) && (g_bDevModeEnabled == 0)) {
    DAT_0066e8f0 = 0;
    DAT_0066e8f4 = 0;
    DAT_0066e8f8 = 0;
    DAT_0066e8fc = 0;
    _DAT_0066e900 = 0;
    iVar1 = (**(code **)(*DAT_0066e950 + 0x24))(DAT_0066e950,0x14,&DAT_0066e8f0);
    if (iVar1 < 0) {
      iVar1 = (**(code **)(*DAT_0066e950 + 0x1c))(DAT_0066e950);
      if (iVar1 == -0x7ff8ffe2) {
        do {
          iVar1 = (**(code **)(*DAT_0066e950 + 0x1c))(DAT_0066e950);
        } while (iVar1 == -0x7ff8ffe2);
        return 0;
      }
    }
    else {
      if (g_bDevModeEnabled == 0) {
        DAT_0089bda8 = DAT_0089bda8 + DAT_0066e8f0;
        DAT_0089bda4 = DAT_0089bda4 + DAT_0066e8f4;
        DAT_0089be48 = DAT_0089be48 + DAT_0066e8f8;
      }
      bVar2 = (DAT_0066e8fc & 0x80) == 0;
      if (bVar2) {
        DAT_0089bdfc = DAT_0089bdfc | DAT_0089bdf5;
      }
      DAT_0089bdf8 = (uint)!bVar2;
      DAT_0089bdf5 = !bVar2;
      bVar2 = (DAT_0066e8fc & 0x8000) == 0;
      if (bVar2) {
        DAT_0089be2c = DAT_0089be2c | DAT_0089bdf7;
      }
      DAT_0089be28 = (uint)!bVar2;
      DAT_0089bdf7 = !bVar2;
      if ((DAT_0066e8fc & 0x800000) != 0) {
        DAT_0089be10 = 1;
        DAT_0089bdf6 = 1;
        return 0;
      }
      DAT_0089be10 = 0;
      DAT_0089be14 = DAT_0089be14 | DAT_0089bdf6;
      DAT_0089bdf6 = 0;
    }
  }
  return 0;
}
