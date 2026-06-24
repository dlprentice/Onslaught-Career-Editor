/* address: 0x0055fe78 */
/* name: CDXTexture__Unk_0055fe78 */
/* signature: void __cdecl CDXTexture__Unk_0055fe78(uint param_1) */


void __cdecl CDXTexture__Unk_0055fe78(uint param_1)

{
  if ((0x6533bf < param_1) && (param_1 < 0x653621)) {
    CTexture__Helper_005611da(((int)(param_1 - 0x6533c0) >> 5) + 0x1c);
    return;
  }
  LeaveCriticalSection((LPCRITICAL_SECTION)(param_1 + 0x20));
  return;
}
