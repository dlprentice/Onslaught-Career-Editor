/* address: 0x00414610 */
/* name: CGeneralVolume__GetCurrentEntryFieldA4_38 */
/* signature: int __fastcall CGeneralVolume__GetCurrentEntryFieldA4_38(void * param_1) */


int __fastcall CGeneralVolume__GetCurrentEntryFieldA4_38(void *param_1)

{
  int iVar1;

  iVar1 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
  if (iVar1 != 0) {
    return *(int *)(*(int *)(iVar1 + 0xa4) + 0x38);
  }
  return 0;
}
