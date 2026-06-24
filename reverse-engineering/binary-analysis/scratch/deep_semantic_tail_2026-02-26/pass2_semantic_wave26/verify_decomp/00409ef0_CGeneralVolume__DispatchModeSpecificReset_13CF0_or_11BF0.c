/* address: 0x00409ef0 */
/* name: CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0 */
/* signature: void __fastcall CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0(int param_1) */


void __fastcall CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0(int param_1)

{
  if (*(int *)(param_1 + 0x260) == 2) {
    CGeneralVolume__Unk_00413cf0(*(int *)(param_1 + 0x578));
    return;
  }
  if (*(int *)(param_1 + 0x260) == 3) {
    CEngine_Unk_0050a080__Wrapper_00411bf0(*(void **)(param_1 + 0x57c));
    return;
  }
  return;
}
