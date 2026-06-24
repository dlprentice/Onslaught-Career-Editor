/* address: 0x0055fe26 */
/* name: CRT__LockRouteByAddress */
/* signature: void __cdecl CRT__LockRouteByAddress(uint param_1) */


void __cdecl CRT__LockRouteByAddress(uint param_1)

{
  if ((0x6533bf < param_1) && (param_1 < 0x653621)) {
    CDXTexture__Helper_00561179(((int)(param_1 - 0x6533c0) >> 5) + 0x1c);
    return;
  }
  EnterCriticalSection((LPCRITICAL_SECTION)(param_1 + 0x20));
  return;
}
