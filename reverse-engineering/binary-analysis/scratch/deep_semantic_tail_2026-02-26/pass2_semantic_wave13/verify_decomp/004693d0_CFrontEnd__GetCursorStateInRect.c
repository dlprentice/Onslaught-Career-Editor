/* address: 0x004693d0 */
/* name: CFrontEnd__GetCursorStateInRect */
/* signature: uint __cdecl CFrontEnd__GetCursorStateInRect(int param_1, int param_2, int param_3, int param_4) */


uint __cdecl CFrontEnd__GetCursorStateInRect(int param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;

  uVar1 = CFrontEnd__IsMouseInputReady(0x675688);
  if (uVar1 != 0) {
    return uVar1 & 0xffffff00;
  }
  uVar1 = CDXEngine__Helper_00523b50((float)param_1,(float)param_2,(float)param_3,(float)param_4);
  return uVar1;
}
