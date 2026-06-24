/* address: 0x0056c2af */
/* name: CRT__FindLocaleForLanguageAndCountry_0056c2af */
/* signature: void CRT__FindLocaleForLanguageAndCountry_0056c2af(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__FindLocaleForLanguageAndCountry_0056c2af(void)

{
  size_t sVar1;

  sVar1 = _strlen(DAT_009d0b28);
  DAT_009d0b24 = (uint)(sVar1 == 3);
  sVar1 = _strlen(DAT_009d0b2c);
  DAT_009d0b1c = (uint)(sVar1 == 3);
  DAT_009d0b18 = 0;
  if (DAT_009d0b24 == 0) {
    DAT_009d0b20 = CRT__CountAlphaPrefix_0056c960(DAT_009d0b28);
  }
  else {
    DAT_009d0b20 = 2;
  }
  EnumSystemLocalesA(CRT__EnumLocalesCallback_MatchLanguageCountry_0056c336,1);
  if ((((DAT_009d0b30 & 0x100) == 0) || ((DAT_009d0b30 & 0x200) == 0)) || ((DAT_009d0b30 & 7) == 0))
  {
    DAT_009d0b30 = 0;
  }
  return;
}
