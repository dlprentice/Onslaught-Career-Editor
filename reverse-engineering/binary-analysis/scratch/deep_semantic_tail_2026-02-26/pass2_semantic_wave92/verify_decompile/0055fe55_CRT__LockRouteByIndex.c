/* address: 0x0055fe55 */
/* name: CRT__LockRouteByIndex */
/* signature: void __cdecl CRT__LockRouteByIndex(int param_1, int param_2) */


void __cdecl CRT__LockRouteByIndex(int param_1,int param_2)

{
  if (param_1 < 0x14) {
    CDXTexture__Helper_00561179(param_1 + 0x1c);
    return;
  }
  EnterCriticalSection((LPCRITICAL_SECTION)(param_2 + 0x20));
  return;
}
