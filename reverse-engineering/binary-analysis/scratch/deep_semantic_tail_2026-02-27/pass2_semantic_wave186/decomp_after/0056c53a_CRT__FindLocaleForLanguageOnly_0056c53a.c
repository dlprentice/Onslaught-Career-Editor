/* address: 0x0056c53a */
/* name: CRT__FindLocaleForLanguageOnly_0056c53a */
/* signature: void CRT__FindLocaleForLanguageOnly_0056c53a(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__FindLocaleForLanguageOnly_0056c53a(void)

{
  size_t sVar1;

  sVar1 = _strlen(DAT_009d0b28);
  DAT_009d0b24 = (uint)(sVar1 == 3);
  if (sVar1 == 3) {
    DAT_009d0b20 = 2;
  }
  else {
    DAT_009d0b20 = CRT__CountAlphaPrefix_0056c960(DAT_009d0b28);
  }
  EnumSystemLocalesA(CRT__EnumLocalesCallback_MatchLanguageOnly_0056c590,1);
  if ((DAT_009d0b30 & 4) == 0) {
    DAT_009d0b30 = 0;
  }
  return;
}
