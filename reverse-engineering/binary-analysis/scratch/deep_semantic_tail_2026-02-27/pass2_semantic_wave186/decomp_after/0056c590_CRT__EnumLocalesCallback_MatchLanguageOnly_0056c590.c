/* address: 0x0056c590 */
/* name: CRT__EnumLocalesCallback_MatchLanguageOnly_0056c590 */
/* signature: uint __stdcall CRT__EnumLocalesCallback_MatchLanguageOnly_0056c590(int param_1) */


uint CRT__EnumLocalesCallback_MatchLanguageOnly_0056c590(int param_1)

{
  int iVar1;
  int iVar2;
  char local_7c [120];

  iVar1 = CRT__ParseHexLocaleIdString_0056c927((void *)param_1);
  iVar2 = (*DAT_009d0b38)(iVar1,(-(uint)(DAT_009d0b24 != 0) & 0xfffff002) + 0x1001,local_7c,0x78);
  if (iVar2 == 0) {
    DAT_009d0b30 = 0;
    return 1;
  }
  iVar2 = stricmp(DAT_009d0b28,local_7c);
  if (iVar2 == 0) {
    if (DAT_009d0b24 == 0) {
      iVar2 = 1;
      goto LAB_0056c61c;
    }
  }
  else {
    if (((DAT_009d0b24 != 0) || (DAT_009d0b20 == (void *)0x0)) ||
       (iVar2 = CMCBuggy__Helper_0056e170(DAT_009d0b28,local_7c,DAT_009d0b20), iVar2 != 0))
    goto LAB_0056c63b;
    iVar2 = 0;
LAB_0056c61c:
    iVar2 = CRT__ValidateLocaleLanguageMatch_0056c7a9(iVar1,iVar2);
    if (iVar2 == 0) goto LAB_0056c63b;
  }
  DAT_009d0b30 = DAT_009d0b30 | 4;
  DAT_009d0b18 = iVar1;
  DAT_009d0b34 = iVar1;
LAB_0056c63b:
  return ~DAT_009d0b30 >> 2 & 1;
}
