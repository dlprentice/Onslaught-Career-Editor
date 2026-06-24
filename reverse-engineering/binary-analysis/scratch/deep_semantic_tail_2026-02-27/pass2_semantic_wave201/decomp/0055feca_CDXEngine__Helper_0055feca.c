/* address: 0x0055feca */
/* name: CDXEngine__Helper_0055feca */
/* signature: int __cdecl CDXEngine__Helper_0055feca(uint param_1) */


int __cdecl CDXEngine__Helper_0055feca(uint param_1)

{
  int iVar1;

  CRT__LockRouteByAddress(param_1);
  iVar1 = CRT__FTellAdjusted((void *)param_1);
  CRT__UnlockRouteByAddress(param_1);
  return iVar1;
}
