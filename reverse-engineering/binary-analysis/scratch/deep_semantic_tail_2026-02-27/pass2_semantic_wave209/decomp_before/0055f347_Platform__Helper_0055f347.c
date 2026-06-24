/* address: 0x0055f347 */
/* name: Platform__Helper_0055f347 */
/* signature: int __cdecl Platform__Helper_0055f347(int param_1) */


int __cdecl Platform__Helper_0055f347(int param_1)

{
  BOOL BVar1;
  uint uVar2;

  BVar1 = CreateDirectoryA((LPCSTR)param_1,(LPSECURITY_ATTRIBUTES)0x0);
  if (BVar1 == 0) {
    uVar2 = GetLastError();
  }
  else {
    uVar2 = 0;
  }
  if (uVar2 != 0) {
    CRT__SetErrnoAndDosErrnoFromWinError_00567a35(uVar2);
    return -1;
  }
  return 0;
}
