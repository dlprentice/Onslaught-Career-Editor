/* address: 0x00569dfe */
/* name: CRT__WideCharToCurrentCodePage_WithLocaleGuard */
/* signature: int __cdecl CRT__WideCharToCurrentCodePage_WithLocaleGuard(int param_1, int param_2) */


int __cdecl CRT__WideCharToCurrentCodePage_WithLocaleGuard(int param_1,int param_2)

{
  int iVar1;
  bool bVar2;

  InterlockedIncrement(&DAT_009d35f0);
  bVar2 = DAT_009d35ec != 0;
  if (bVar2) {
    InterlockedDecrement(&DAT_009d35f0);
    CRT__LockByIndex(0x13);
  }
  iVar1 = CRT__WideCharToCurrentCodePage(param_1,param_2);
  if (bVar2) {
    CRT__UnlockByIndex(0x13);
  }
  else {
    InterlockedDecrement(&DAT_009d35f0);
  }
  return iVar1;
}
