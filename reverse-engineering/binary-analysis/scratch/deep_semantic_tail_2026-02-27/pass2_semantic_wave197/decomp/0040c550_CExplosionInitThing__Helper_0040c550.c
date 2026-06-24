/* address: 0x0040c550 */
/* name: CExplosionInitThing__Helper_0040c550 */
/* signature: void __fastcall CExplosionInitThing__Helper_0040c550(int param_1) */


void __fastcall CExplosionInitThing__Helper_0040c550(int param_1)

{
  if (*(int *)(param_1 + 0x260) != 3) {
    CGeneralVolume__GetCurrentEntryDisplayString(*(void **)(param_1 + 0x578));
    return;
  }
  CText_GetStringById__Wrapper_00412420(*(void **)(param_1 + 0x57c));
  return;
}
