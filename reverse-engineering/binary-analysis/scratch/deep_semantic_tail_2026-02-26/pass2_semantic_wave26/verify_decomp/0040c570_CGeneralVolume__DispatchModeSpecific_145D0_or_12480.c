/* address: 0x0040c570 */
/* name: CGeneralVolume__DispatchModeSpecific_145D0_or_12480 */
/* signature: void __fastcall CGeneralVolume__DispatchModeSpecific_145D0_or_12480(int param_1) */


void __fastcall CGeneralVolume__DispatchModeSpecific_145D0_or_12480(int param_1)

{
  if (*(int *)(param_1 + 0x260) != 3) {
    CGeneralVolume__Unk_004145d0(*(void **)(param_1 + 0x578));
    return;
  }
  CGeneralVolume__Unk_00412480(*(void **)(param_1 + 0x57c));
  return;
}
