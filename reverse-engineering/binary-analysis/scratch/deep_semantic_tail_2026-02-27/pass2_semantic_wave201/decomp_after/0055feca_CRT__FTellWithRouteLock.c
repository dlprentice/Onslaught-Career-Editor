/* address: 0x0055feca */
/* name: CRT__FTellWithRouteLock */
/* signature: int __cdecl CRT__FTellWithRouteLock(uint param_1) */


int __cdecl CRT__FTellWithRouteLock(uint param_1)

{
  int iVar1;

  CRT__LockRouteByAddress(param_1);
  iVar1 = CRT__FTellAdjusted((void *)param_1);
  CRT__UnlockRouteByAddress(param_1);
  return iVar1;
}
