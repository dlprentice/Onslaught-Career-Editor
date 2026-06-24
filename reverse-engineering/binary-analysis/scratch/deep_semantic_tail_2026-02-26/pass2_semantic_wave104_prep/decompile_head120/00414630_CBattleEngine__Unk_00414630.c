/* address: 0x00414630 */
/* name: CBattleEngine__Unk_00414630 */
/* signature: int __fastcall CBattleEngine__Unk_00414630(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CBattleEngine__Unk_00414630(void *param_1)

{
  int iVar1;
  int iVar2;

  iVar2 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
  if ((iVar2 != 0) && (*(int *)(iVar2 + 0x9c) != 0)) {
    iVar1 = *(int *)((int)param_1 + 0x20);
    iVar2 = *(int *)(*(int *)(iVar2 + 0xa4) + 0x24);
    if (*(int *)(iVar1 + 0x55c + iVar2 * 4) == 0) {
      if (_DAT_005d856c < *(float *)(iVar1 + 0x52c + iVar2 * 4)) {
        return 1;
      }
    }
    else if ((*(float *)(iVar1 + 0x52c + iVar2 * 4) <
              *(float *)(*(int *)(iVar1 + 0x4b0) + 0x88 + iVar2 * 4)) &&
            (*(int *)(iVar1 + 0x544 + iVar2 * 4) == 0)) {
      return 1;
    }
  }
  return 0;
}
