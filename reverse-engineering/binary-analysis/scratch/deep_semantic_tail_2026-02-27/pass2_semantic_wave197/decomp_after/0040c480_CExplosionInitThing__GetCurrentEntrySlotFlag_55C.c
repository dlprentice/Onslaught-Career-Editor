/* address: 0x0040c480 */
/* name: CExplosionInitThing__GetCurrentEntrySlotFlag_55C */
/* signature: void __fastcall CExplosionInitThing__GetCurrentEntrySlotFlag_55C(int param_1) */


void __fastcall CExplosionInitThing__GetCurrentEntrySlotFlag_55C(int param_1)

{
  if (*(int *)(param_1 + 0x260) != 3) {
    CGeneralVolume__GetCurrentEntrySlotFlag_55C(*(void **)(param_1 + 0x578));
    return;
  }
  CGeneralVolume__EntryIterator_GetSlotFlag_55C(*(void **)(param_1 + 0x57c));
  return;
}
