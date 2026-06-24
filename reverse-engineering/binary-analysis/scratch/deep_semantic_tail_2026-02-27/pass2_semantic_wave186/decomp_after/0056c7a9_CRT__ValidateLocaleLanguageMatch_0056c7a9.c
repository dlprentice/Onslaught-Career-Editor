/* address: 0x0056c7a9 */
/* name: CRT__ValidateLocaleLanguageMatch_0056c7a9 */
/* signature: int __cdecl CRT__ValidateLocaleLanguageMatch_0056c7a9(int param_1, int param_2) */


int __cdecl CRT__ValidateLocaleLanguageMatch_0056c7a9(int param_1,int param_2)

{
  int iVar1;
  size_t sVar2;
  size_t sVar3;
  undefined1 local_7c [120];

  iVar1 = (*DAT_009d0b38)((ushort)param_1 & 0x3ff | 0x400,1,local_7c,0x78);
  if (iVar1 == 0) {
    return 0;
  }
  iVar1 = CRT__ParseHexLocaleIdString_0056c927(local_7c);
  if ((param_1 != iVar1) && (param_2 != 0)) {
    sVar2 = CRT__CountAlphaPrefix_0056c960(DAT_009d0b28);
    sVar3 = _strlen(DAT_009d0b28);
    if (sVar2 == sVar3) {
      return 0;
    }
  }
  return 1;
}
