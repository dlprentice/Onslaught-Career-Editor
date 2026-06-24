/* address: 0x0055fe55 */
/* name: CFastVB__Unk_0055fe55 */
/* signature: void __cdecl CFastVB__Unk_0055fe55(int param_1, int param_2) */


void __cdecl CFastVB__Unk_0055fe55(int param_1,int param_2)

{
  if (param_1 < 0x14) {
    CDXTexture__Helper_00561179(param_1 + 0x1c);
    return;
  }
  EnterCriticalSection((LPCRITICAL_SECTION)(param_2 + 0x20));
  return;
}
