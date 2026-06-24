/* address: 0x0055f783 */
/* name: Win32__FindCloseWithErrno */
/* signature: int __cdecl Win32__FindCloseWithErrno(int param_1) */


int __cdecl Win32__FindCloseWithErrno(int param_1)

{
  BOOL BVar1;
  undefined4 *puVar2;

  BVar1 = FindClose((HANDLE)param_1);
  if (BVar1 == 0) {
    puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar2 = 0x16;
    return -1;
  }
  return 0;
}
