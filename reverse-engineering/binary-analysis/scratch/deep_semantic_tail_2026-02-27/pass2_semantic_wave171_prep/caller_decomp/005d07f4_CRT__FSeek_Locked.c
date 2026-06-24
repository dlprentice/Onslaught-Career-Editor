/* address: 0x005d07f4 */
/* name: CRT__FSeek_Locked */
/* signature: int __cdecl CRT__FSeek_Locked(uint param_1, int param_2, int param_3) */


int __cdecl CRT__FSeek_Locked(uint param_1,int param_2,int param_3)

{
  int iVar1;

  CRT__LockRouteByAddress(param_1);
  iVar1 = CDXTexture__Helper_005d0820((void *)param_1,param_2,param_3);
  CRT__UnlockRouteByAddress(param_1);
  return iVar1;
}
