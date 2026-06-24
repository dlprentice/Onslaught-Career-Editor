/* address: 0x00560b2c */
/* name: CTexture__Unk_00560b2c */
/* signature: int CTexture__Unk_00560b2c(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_00560b2c(void)

{
  DWORD *lpTlsValue;
  BOOL BVar1;
  DWORD DVar2;

  CTexture__Unk_00561150();
  DAT_00653650 = TlsAlloc();
  if (DAT_00653650 != 0xffffffff) {
    lpTlsValue = (DWORD *)CTexture__Helper_005689b8(1,0x74);
    if (lpTlsValue != (DWORD *)0x0) {
      BVar1 = TlsSetValue(DAT_00653650,lpTlsValue);
      if (BVar1 != 0) {
        CTexture__Unk_00560b80((int)lpTlsValue);
        DVar2 = GetCurrentThreadId();
        lpTlsValue[1] = 0xffffffff;
        *lpTlsValue = DVar2;
        return 1;
      }
    }
  }
  return 0;
}
