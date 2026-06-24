/* address: 0x0056d25e */
/* name: CRT__MessageBoxA_WithActivePopupFallback */
/* signature: int __cdecl CRT__MessageBoxA_WithActivePopupFallback(int param_1, int param_2, int param_3) */


int __cdecl CRT__MessageBoxA_WithActivePopupFallback(int param_1,int param_2,int param_3)

{
  HMODULE hModule;
  int iVar1;

  iVar1 = 0;
  if (DAT_009d0bfc == (FARPROC)0x0) {
    hModule = LoadLibraryA("user32.dll");
    if (hModule != (HMODULE)0x0) {
      DAT_009d0bfc = GetProcAddress(hModule,"MessageBoxA");
      if (DAT_009d0bfc != (FARPROC)0x0) {
        DAT_009d0c00 = GetProcAddress(hModule,"GetActiveWindow");
        DAT_009d0c04 = GetProcAddress(hModule,"GetLastActivePopup");
        goto LAB_0056d2ad;
      }
    }
    iVar1 = 0;
  }
  else {
LAB_0056d2ad:
    if (DAT_009d0c00 != (FARPROC)0x0) {
      iVar1 = (*DAT_009d0c00)();
      if ((iVar1 != 0) && (DAT_009d0c04 != (FARPROC)0x0)) {
        iVar1 = (*DAT_009d0c04)(iVar1);
      }
    }
    iVar1 = (*DAT_009d0bfc)(iVar1,param_1,param_2,param_3);
  }
  return iVar1;
}
