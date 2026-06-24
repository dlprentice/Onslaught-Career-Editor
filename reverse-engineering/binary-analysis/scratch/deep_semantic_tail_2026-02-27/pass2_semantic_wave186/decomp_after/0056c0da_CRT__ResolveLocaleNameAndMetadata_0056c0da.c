/* address: 0x0056c0da */
/* name: CRT__ResolveLocaleNameAndMetadata_0056c0da */
/* signature: int __cdecl CRT__ResolveLocaleNameAndMetadata_0056c0da(void * param_1, void * param_2, int param_3) */


int __cdecl CRT__ResolveLocaleNameAndMetadata_0056c0da(void *param_1,void *param_2,int param_3)

{
  int iVar1;
  uint extraout_EAX;
  BOOL BVar2;

  if (DAT_009d0b38 == (code *)0x0) {
    iVar1 = CRT__IsWindowsNtPlatform();
    if (iVar1 == 0) {
      DAT_009d0b38 = CRT__GetLocaleInfoACompatFallback;
    }
    else {
      DAT_009d0b38 = GetLocaleInfoA_exref;
    }
  }
  if (param_1 != (void *)0x0) {
    DAT_009d0b28 = param_1;
    if (*(char *)param_1 != '\0') {
      CRT__LocaleAliasBinarySearchRemap_0056c257(0x656780,0x40,&DAT_009d0b28);
    }
    DAT_009d0b2c = (char *)((int)param_1 + 0x40);
    if ((DAT_009d0b2c != (char *)0x0) && (*DAT_009d0b2c != '\0')) {
      CRT__LocaleAliasBinarySearchRemap_0056c257(0x6566c8,0x16,&DAT_009d0b2c);
    }
    DAT_009d0b30 = 0;
    if ((DAT_009d0b28 != (char *)0x0) && (*DAT_009d0b28 != '\0')) {
      if ((DAT_009d0b2c == (char *)0x0) || (*DAT_009d0b2c == '\0')) {
        CRT__FindLocaleForLanguageOnly_0056c53a();
      }
      else {
        CRT__FindLocaleForLanguageAndCountry_0056c2af();
      }
      goto LAB_0056c197;
    }
    if ((DAT_009d0b2c != (char *)0x0) && (*DAT_009d0b2c != '\0')) {
      CRT__FindLocaleForCountryOnly_0056c64d();
      goto LAB_0056c197;
    }
  }
  CRT__InitLocaleDefaults();
LAB_0056c197:
  if ((((DAT_009d0b30 == 0) ||
       (CRT__ResolveLocaleCodePageToken((void *)((int)param_1 + 0x80)), extraout_EAX == 0)) ||
      (BVar2 = IsValidCodePage(extraout_EAX & 0xffff), BVar2 == 0)) ||
     (BVar2 = IsValidLocale(DAT_009d0b18,1), BVar2 == 0)) {
    return 0;
  }
  if (param_2 != (void *)0x0) {
    *(undefined2 *)param_2 = (undefined2)DAT_009d0b18;
    *(undefined2 *)((int)param_2 + 2) = (undefined2)DAT_009d0b34;
    *(short *)((int)param_2 + 4) = (short)extraout_EAX;
  }
  if (param_3 != 0) {
    iVar1 = (*DAT_009d0b38)(DAT_009d0b18,0x1001,param_3,0x40);
    if (iVar1 == 0) {
      return 0;
    }
    iVar1 = (*DAT_009d0b38)(DAT_009d0b34,0x1002,param_3 + 0x40,0x40);
    if (iVar1 == 0) {
      return 0;
    }
    CTexture__Helper_0056e0bf(extraout_EAX,param_3 + 0x80,10);
  }
  return 1;
}
