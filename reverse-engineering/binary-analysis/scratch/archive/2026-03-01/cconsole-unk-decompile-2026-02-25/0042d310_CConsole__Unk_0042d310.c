/* address: 0x0042d310 */
/* name: CConsole__Unk_0042d310 */
/* signature: int CConsole__Unk_0042d310(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CConsole__Unk_0042d310(void)

{
  int iVar1;

  iVar1 = (**(code **)(*DAT_00889028 + 0xc))(DAT_00889028,&DAT_0060c0bc,&DAT_0066e950,0);
  if (-1 < iVar1) {
    iVar1 = (**(code **)(*DAT_0066e950 + 0x2c))(DAT_0066e950,&DAT_0060be3c);
    if (-1 < iVar1) {
      (**(code **)(*DAT_0066e950 + 0x34))(DAT_0066e950,DAT_00888a44,5);
      DAT_0066e8f0 = 0;
      DAT_0066e8f4 = 0;
      DAT_0066e8f8 = 0;
      DAT_0066e8fc = 0;
      _DAT_0066e900 = 0;
      CProfiler__ResetAll();
      iVar1 = PLATFORM__GetWindowWidth();
      DAT_0089bda8 = iVar1 >> 1;
      iVar1 = PLATFORM__GetWindowHeight();
      DAT_0089bda4 = iVar1 >> 1;
      CVBufTexture__Unk_005234d0(1);
      iVar1 = 0;
    }
  }
  return iVar1;
}
