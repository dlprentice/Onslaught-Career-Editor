/* address: 0x0040c590 */
/* name: CExplosionInitThing__GetCurrentEntryFieldA4_38 */
/* signature: void __fastcall CExplosionInitThing__GetCurrentEntryFieldA4_38(int param_1) */


void __fastcall CExplosionInitThing__GetCurrentEntryFieldA4_38(int param_1)

{
  if (*(int *)(param_1 + 0x260) != 3) {
    CGeneralVolume__GetCurrentEntryFieldA4_38(*(void **)(param_1 + 0x578));
    return;
  }
  CGeneralVolume__EntryIterator_GetIndexedEntryFieldA4_38(*(void **)(param_1 + 0x57c));
  return;
}
