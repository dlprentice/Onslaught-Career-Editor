/* address: 0x004145d0 */
/* name: CGeneralVolume__GetCurrentEntryPayload */
/* signature: int __fastcall CGeneralVolume__GetCurrentEntryPayload(void * param_1) */


int __fastcall CGeneralVolume__GetCurrentEntryPayload(void *param_1)

{
  int iVar1;

  iVar1 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
  if (iVar1 != 0) {
    return **(int **)(iVar1 + 0xa4);
  }
  return 0;
}
