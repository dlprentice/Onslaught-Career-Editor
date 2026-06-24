/* address: 0x0040c3a0 */
/* name: CExplosionInitThing__GetCurrentEntrySlotFlag_544 */
/* signature: void __fastcall CExplosionInitThing__GetCurrentEntrySlotFlag_544(int param_1) */


void __fastcall CExplosionInitThing__GetCurrentEntrySlotFlag_544(int param_1)

{
  if (*(int *)(param_1 + 0x260) != 3) {
    CCockpit__GetCurrentEntryFlag_544(*(void **)(param_1 + 0x578));
    return;
  }
  CGeneralVolume__EntryIterator_GetSlotFlag_544(*(void **)(param_1 + 0x57c));
  return;
}
