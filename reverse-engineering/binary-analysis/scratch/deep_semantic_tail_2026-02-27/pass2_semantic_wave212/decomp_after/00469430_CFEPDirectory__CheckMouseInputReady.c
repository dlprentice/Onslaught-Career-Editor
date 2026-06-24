/* address: 0x00469430 */
/* name: CFEPDirectory__CheckMouseInputReady */
/* signature: uint __cdecl CFEPDirectory__CheckMouseInputReady(int param_1, int param_2, int param_3, int param_4) */


uint __cdecl CFEPDirectory__CheckMouseInputReady(int param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;

  uVar1 = CFrontEnd__IsMouseInputReady(0x675688);
  if (uVar1 != 0) {
    return uVar1 & 0xffffff00;
  }
  uVar1 = Input__GetCursorStateInRectAndConsume
                    ((float)param_1,(float)param_2,(float)param_3,(float)param_4);
  return uVar1;
}
