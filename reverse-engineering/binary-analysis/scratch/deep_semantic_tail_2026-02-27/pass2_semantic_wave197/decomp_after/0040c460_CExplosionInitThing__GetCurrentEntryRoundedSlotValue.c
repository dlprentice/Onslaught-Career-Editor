/* address: 0x0040c460 */
/* name: CExplosionInitThing__GetCurrentEntryRoundedSlotValue */
/* signature: void __fastcall CExplosionInitThing__GetCurrentEntryRoundedSlotValue(int param_1) */


void __fastcall CExplosionInitThing__GetCurrentEntryRoundedSlotValue(int param_1)

{
  if (*(int *)(param_1 + 0x260) != 3) {
    CGeneralVolume__GetCurrentEntryRoundedSlotValue(*(void **)(param_1 + 0x578));
    return;
  }
  ROUND__Wrapper_00412240(*(void **)(param_1 + 0x57c));
  return;
}
