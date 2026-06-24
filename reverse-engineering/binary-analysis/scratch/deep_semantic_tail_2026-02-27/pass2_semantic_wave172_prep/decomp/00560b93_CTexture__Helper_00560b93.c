/* address: 0x00560b93 */
/* name: CTexture__Helper_00560b93 */
/* signature: int CTexture__Helper_00560b93(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_00560b93(void)

{
  DWORD dwErrCode;
  DWORD *lpTlsValue;
  BOOL BVar1;
  DWORD DVar2;

  dwErrCode = GetLastError();
  lpTlsValue = TlsGetValue(DAT_00653650);
  if (lpTlsValue == (DWORD *)0x0) {
    lpTlsValue = (DWORD *)CTexture__Helper_005689b8(1,0x74);
    if (lpTlsValue != (DWORD *)0x0) {
      BVar1 = TlsSetValue(DAT_00653650,lpTlsValue);
      if (BVar1 != 0) {
        CTexture__InitializeThreadLocalRecordDefaults((int)lpTlsValue);
        DVar2 = GetCurrentThreadId();
        lpTlsValue[1] = 0xffffffff;
        *lpTlsValue = DVar2;
        goto LAB_00560bee;
      }
    }
    __amsg_exit(0x10);
  }
LAB_00560bee:
  SetLastError(dwErrCode);
  return (int)lpTlsValue;
}
