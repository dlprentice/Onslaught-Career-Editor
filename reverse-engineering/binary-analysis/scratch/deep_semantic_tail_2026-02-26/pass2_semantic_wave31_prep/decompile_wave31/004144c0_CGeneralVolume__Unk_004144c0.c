/* address: 0x004144c0 */
/* name: CGeneralVolume__Unk_004144c0 */
/* signature: int __fastcall CGeneralVolume__Unk_004144c0(void * param_1) */


int __fastcall CGeneralVolume__Unk_004144c0(void *param_1)

{
  int iVar1;

  iVar1 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
  if (iVar1 != 0) {
    return *(int *)(*(int *)((int)param_1 + 0x20) + 0x55c +
                   *(int *)(*(int *)(iVar1 + 0xa4) + 0x24) * 4);
  }
  return 0;
}
