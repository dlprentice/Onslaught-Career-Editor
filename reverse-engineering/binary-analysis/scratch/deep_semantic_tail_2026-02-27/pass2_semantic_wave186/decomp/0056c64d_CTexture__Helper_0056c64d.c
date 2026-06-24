/* address: 0x0056c64d */
/* name: CTexture__Helper_0056c64d */
/* signature: void CTexture__Helper_0056c64d(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__Helper_0056c64d(void)

{
  size_t sVar1;

  sVar1 = _strlen(DAT_009d0b2c);
  DAT_009d0b1c = (uint)(sVar1 == 3);
  EnumSystemLocalesA(CRT__ValidateCodePageAgainstLocale,1);
  if ((DAT_009d0b30 & 4) == 0) {
    DAT_009d0b30 = 0;
  }
  return;
}
