/* address: 0x0055fea7 */
/* name: CRT__UnlockRouteByIndex */
/* signature: void __cdecl CRT__UnlockRouteByIndex(int param_1, int param_2) */


void __cdecl CRT__UnlockRouteByIndex(int param_1,int param_2)

{
  if (param_1 < 0x14) {
    CTexture__Helper_005611da(param_1 + 0x1c);
    return;
  }
  LeaveCriticalSection((LPCRITICAL_SECTION)(param_2 + 0x20));
  return;
}
