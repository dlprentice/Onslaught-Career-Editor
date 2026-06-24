/* address: 0x00409f20 */
/* name: CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90 */
/* signature: void __fastcall CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90(int param_1) */


void __fastcall CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90(int param_1)

{
  short sVar1;

  *(undefined4 *)(param_1 + 0x588) = 0;
  sVar1 = (short)*(undefined4 *)(param_1 + 0x2a0);
  *(short *)(param_1 + 0x2b4) = sVar1;
  if (sVar1 == 0) {
    *(short *)(param_1 + 0x2b4) = (short)*(undefined4 *)(param_1 + 0x2b0);
  }
  if (*(int *)(param_1 + 0x260) == 2) {
    CGeneralVolume__Unk_00413cc0(*(int *)(param_1 + 0x578));
    return;
  }
  if (*(int *)(param_1 + 0x260) == 3) {
    CEngine_Unk_00506010__Wrapper_00411b90(*(void **)(param_1 + 0x57c));
    return;
  }
  return;
}
