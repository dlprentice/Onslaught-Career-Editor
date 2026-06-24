/* address: 0x00564e9e */
/* name: CRT__CloseFd_NoLock */
/* signature: int __cdecl CRT__CloseFd_NoLock(uint param_1) */


int __cdecl CRT__CloseFd_NoLock(uint param_1)

{
  int iVar1;
  int iVar2;
  HANDLE hObject;
  BOOL BVar3;
  DWORD DVar4;

  iVar1 = CDXTexture__Helper_0056b212(param_1);
  if (iVar1 != -1) {
    if ((param_1 == 1) || (param_1 == 2)) {
      iVar1 = CDXTexture__Helper_0056b212(2);
      iVar2 = CDXTexture__Helper_0056b212(1);
      if (iVar2 == iVar1) goto LAB_00564eec;
    }
    hObject = (HANDLE)CDXTexture__Helper_0056b212(param_1);
    BVar3 = CloseHandle(hObject);
    if (BVar3 == 0) {
      DVar4 = GetLastError();
      goto LAB_00564eee;
    }
  }
LAB_00564eec:
  DVar4 = 0;
LAB_00564eee:
  CRT__FreeOsHandle(param_1);
  *(undefined1 *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + (param_1 & 0x1f) * 0x24) = 0;
  if (DVar4 == 0) {
    iVar1 = 0;
  }
  else {
    CTexture__Helper_00567a35(DVar4);
    iVar1 = -1;
  }
  return iVar1;
}
