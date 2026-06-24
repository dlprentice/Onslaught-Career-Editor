/* address: 0x00569124 */
/* name: CTexture__Helper_00569124 */
/* signature: int CTexture__Helper_00569124(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_00569124(void)

{
  char cVar1;
  WCHAR WVar2;
  WCHAR *pWVar3;
  WCHAR *pWVar4;
  int iVar5;
  size_t _Size;
  LPSTR lpMultiByteStr;
  char *pcVar6;
  void *pvVar8;
  LPWCH lpWideCharStr;
  LPCH pCVar9;
  LPSTR local_8;
  char *pcVar7;

  lpWideCharStr = (LPWCH)0x0;
  pCVar9 = (LPCH)0x0;
  if (DAT_009d0ac8 == 0) {
    lpWideCharStr = GetEnvironmentStringsW();
    if (lpWideCharStr != (LPWCH)0x0) {
      DAT_009d0ac8 = 1;
LAB_0056917b:
      if ((lpWideCharStr == (LPWCH)0x0) &&
         (lpWideCharStr = GetEnvironmentStringsW(), lpWideCharStr == (LPWCH)0x0)) {
        return 0;
      }
      WVar2 = *lpWideCharStr;
      pWVar4 = lpWideCharStr;
      while (WVar2 != L'\0') {
        do {
          pWVar3 = pWVar4;
          pWVar4 = pWVar3 + 1;
        } while (*pWVar4 != L'\0');
        pWVar4 = pWVar3 + 2;
        WVar2 = *pWVar4;
      }
      iVar5 = ((int)pWVar4 - (int)lpWideCharStr >> 1) + 1;
      _Size = WideCharToMultiByte(0,0,lpWideCharStr,iVar5,(LPSTR)0x0,0,(LPCSTR)0x0,(LPBOOL)0x0);
      local_8 = (LPSTR)0x0;
      if (((_Size != 0) && (lpMultiByteStr = _malloc(_Size), lpMultiByteStr != (LPSTR)0x0)) &&
         (iVar5 = WideCharToMultiByte(0,0,lpWideCharStr,iVar5,lpMultiByteStr,_Size,(LPCSTR)0x0,
                                      (LPBOOL)0x0), local_8 = lpMultiByteStr, iVar5 == 0)) {
        CRT__FreeBase((int)lpMultiByteStr);
        local_8 = (LPSTR)0x0;
      }
      FreeEnvironmentStringsW(lpWideCharStr);
      return (int)local_8;
    }
    pCVar9 = GetEnvironmentStrings();
    if (pCVar9 == (LPCH)0x0) {
      return 0;
    }
    DAT_009d0ac8 = 2;
  }
  else {
    if (DAT_009d0ac8 == 1) goto LAB_0056917b;
    if (DAT_009d0ac8 != 2) {
      return 0;
    }
  }
  if ((pCVar9 == (LPCH)0x0) && (pCVar9 = GetEnvironmentStrings(), pCVar9 == (LPCH)0x0)) {
    return 0;
  }
  cVar1 = *pCVar9;
  pcVar6 = pCVar9;
  while (cVar1 != '\0') {
    do {
      pcVar7 = pcVar6;
      pcVar6 = pcVar7 + 1;
    } while (*pcVar6 != '\0');
    pcVar6 = pcVar7 + 2;
    cVar1 = *pcVar6;
  }
  pvVar8 = _malloc((size_t)(pcVar6 + (1 - (int)pCVar9)));
  if (pvVar8 == (void *)0x0) {
    pvVar8 = (void *)0x0;
  }
  else {
    CTexture__Helper_00567700(pvVar8,pCVar9,(uint)(pcVar6 + (1 - (int)pCVar9)));
  }
  FreeEnvironmentStringsA(pCVar9);
  return (int)pvVar8;
}
