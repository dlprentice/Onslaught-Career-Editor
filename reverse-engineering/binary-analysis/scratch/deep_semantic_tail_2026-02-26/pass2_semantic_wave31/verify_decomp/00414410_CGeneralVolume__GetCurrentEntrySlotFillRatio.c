/* address: 0x00414410 */
/* name: CGeneralVolume__GetCurrentEntrySlotFillRatio */
/* signature: double __fastcall CGeneralVolume__GetCurrentEntrySlotFillRatio(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CGeneralVolume__GetCurrentEntrySlotFillRatio(void *param_1)

{
  float fVar1;
  int iVar2;

  iVar2 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
  if (iVar2 == 0) {
    fVar1 = 0.0;
  }
  else {
    iVar2 = *(int *)(*(int *)(iVar2 + 0xa4) + 0x24);
    fVar1 = *(float *)(*(int *)((int)param_1 + 0x20) + 0x52c + iVar2 * 4) /
            *(float *)(*(int *)(*(int *)((int)param_1 + 0x20) + 0x4b0) + 0x88 + iVar2 * 4);
    if (_DAT_005d8568 < fVar1) {
      return (double)_DAT_005d8568;
    }
  }
  return (double)fVar1;
}
