/* address: 0x0055fe26 */
/* name: CFastVB__Unk_0055fe26 */
/* signature: void __cdecl CFastVB__Unk_0055fe26(uint param_1) */


void __cdecl CFastVB__Unk_0055fe26(uint param_1)

{
  if ((0x6533bf < param_1) && (param_1 < 0x653621)) {
    CDXTexture__Helper_00561179(((int)(param_1 - 0x6533c0) >> 5) + 0x1c);
    return;
  }
  EnterCriticalSection((LPCRITICAL_SECTION)(param_1 + 0x20));
  return;
}
