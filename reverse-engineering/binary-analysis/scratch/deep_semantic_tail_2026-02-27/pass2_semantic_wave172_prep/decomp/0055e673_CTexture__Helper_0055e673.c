/* address: 0x0055e673 */
/* name: CTexture__Helper_0055e673 */
/* signature: int __cdecl CTexture__Helper_0055e673(int param_1) */


int __cdecl CTexture__Helper_0055e673(int param_1)

{
  bool bVar1;

  if (DAT_009d0998 == 0) {
    if ((0x60 < param_1) && (param_1 < 0x7b)) {
      return param_1 + -0x20;
    }
  }
  else {
    InterlockedIncrement(&DAT_009d35f0);
    bVar1 = DAT_009d35ec != 0;
    if (bVar1) {
      InterlockedDecrement(&DAT_009d35f0);
      CRT__LockByIndex(0x13);
    }
    param_1 = CFastVB__Helper_0055e6e2(param_1);
    if (bVar1) {
      CTexture__Helper_005611da(0x13);
    }
    else {
      InterlockedDecrement(&DAT_009d35f0);
    }
  }
  return param_1;
}
