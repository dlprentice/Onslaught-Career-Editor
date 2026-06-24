/* address: 0x00469430 */
/* name: CFEPDirectory__Helper_00469430 */
/* signature: uint __cdecl CFEPDirectory__Helper_00469430(int param_1, int param_2, int param_3, int param_4) */


uint __cdecl CFEPDirectory__Helper_00469430(int param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;

  uVar1 = CFrontEnd__IsMouseInputReady(0x675688);
  if (uVar1 != 0) {
    return uVar1 & 0xffffff00;
  }
  uVar1 = CVBufTexture__Unk_00523d40((float)param_1,(float)param_2,(float)param_3,(float)param_4);
  return uVar1;
}
