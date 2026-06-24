/* address: 0x005695af */
/* name: CRT__ToLower_005695af */
/* signature: int __cdecl CRT__ToLower_005695af(int param_1) */


int __cdecl CRT__ToLower_005695af(int param_1)

{
  void *extraout_ECX;
  uint unaff_EDI;
  bool bVar1;
  void *this;

  if (DAT_009d0998 == 0) {
    if ((0x40 < param_1) && (param_1 < 0x5b)) {
      return param_1 + 0x20;
    }
  }
  else {
    InterlockedIncrement(&DAT_009d35f0);
    bVar1 = DAT_009d35ec != 0;
    this = extraout_ECX;
    if (bVar1) {
      InterlockedDecrement(&DAT_009d35f0);
      this = (void *)0x13;
      CRT__LockByIndex(0x13);
    }
    param_1 = CMCBuggy__Helper_0056961e(this,(void *)param_1,unaff_EDI);
    if (bVar1) {
      CRT__UnlockByIndex(0x13);
    }
    else {
      InterlockedDecrement(&DAT_009d35f0);
    }
  }
  return param_1;
}
