/* address: 0x0056c684 */
/* name: CRT__ValidateCodePageAgainstLocale */
/* signature: uint __stdcall CRT__ValidateCodePageAgainstLocale(int param_1) */


uint CRT__ValidateCodePageAgainstLocale(int param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  char local_7c [120];

  iVar1 = CTexture__Helper_0056c927((void *)param_1);
  iVar2 = (*DAT_009d0b38)(iVar1,(-(uint)(DAT_009d0b1c != 0) & 0xfffff005) + 0x1002,local_7c,0x78);
  if (iVar2 == 0) {
    DAT_009d0b30 = 0;
    uVar3 = 1;
  }
  else {
    iVar2 = stricmp(DAT_009d0b2c,local_7c);
    if (iVar2 == 0) {
      iVar2 = CRT__IsCodePageSupportedByLocaleMap(iVar1);
      if (iVar2 != 0) {
        DAT_009d0b30 = DAT_009d0b30 | 4;
        DAT_009d0b18 = iVar1;
        DAT_009d0b34 = iVar1;
      }
    }
    uVar3 = ~DAT_009d0b30 >> 2 & 1;
  }
  return uVar3;
}
