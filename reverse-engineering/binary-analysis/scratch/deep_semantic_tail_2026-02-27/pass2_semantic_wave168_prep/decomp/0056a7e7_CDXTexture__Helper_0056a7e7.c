/* address: 0x0056a7e7 */
/* name: CDXTexture__Helper_0056a7e7 */
/* signature: int __cdecl CDXTexture__Helper_0056a7e7(int param_1, int param_2) */


int __cdecl CDXTexture__Helper_0056a7e7(int param_1,int param_2)

{
  DWORD DVar1;
  undefined4 *puVar2;

  DVar1 = GetFileAttributesA((LPCSTR)param_1);
  if (DVar1 == 0xffffffff) {
    DVar1 = GetLastError();
    CTexture__Helper_00567a35(DVar1);
  }
  else {
    if (((DVar1 & 1) == 0) || ((param_2 & 2U) == 0)) {
      return 0;
    }
    puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar2 = 0xd;
    puVar2 = (undefined4 *)CTexture__Helper_00567ab1();
    *puVar2 = 5;
  }
  return -1;
}
