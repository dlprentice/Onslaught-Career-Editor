/* address: 0x0040c3a0 */
/* name: CGeneralVolume__Unk_0040c3a0 */
/* signature: void __fastcall CGeneralVolume__Unk_0040c3a0(int param_1) */


void __fastcall CGeneralVolume__Unk_0040c3a0(int param_1)

{
  if (*(int *)(param_1 + 0x260) != 3) {
    CCockpit__Unk_004144f0(*(void **)(param_1 + 0x578));
    return;
  }
  CGeneralVolume__Unk_00412310(*(void **)(param_1 + 0x57c));
  return;
}
