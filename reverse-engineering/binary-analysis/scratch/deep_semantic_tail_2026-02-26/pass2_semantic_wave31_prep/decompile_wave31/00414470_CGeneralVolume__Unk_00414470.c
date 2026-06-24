/* address: 0x00414470 */
/* name: CGeneralVolume__Unk_00414470 */
/* signature: int __fastcall CGeneralVolume__Unk_00414470(void * param_1) */


int __fastcall CGeneralVolume__Unk_00414470(void *param_1)

{
  int iVar1;
  undefined4 local_8;

  iVar1 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
  if (iVar1 != 0) {
    iVar1 = *(int *)(*(int *)(iVar1 + 0xa4) + 0x24);
    if (*(int *)(*(int *)((int)param_1 + 0x20) + 0x55c + iVar1 * 4) == 0) {
      local_8 = (int)(longlong)ROUND(*(float *)(*(int *)((int)param_1 + 0x20) + 0x52c + iVar1 * 4));
      return local_8;
    }
  }
  return 0;
}
