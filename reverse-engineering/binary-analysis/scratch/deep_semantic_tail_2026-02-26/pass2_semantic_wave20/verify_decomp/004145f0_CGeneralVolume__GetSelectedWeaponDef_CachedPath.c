/* address: 0x004145f0 */
/* name: CGeneralVolume__GetSelectedWeaponDef_CachedPath */
/* signature: int __fastcall CGeneralVolume__GetSelectedWeaponDef_CachedPath(void * param_1) */


int __fastcall CGeneralVolume__GetSelectedWeaponDef_CachedPath(void *param_1)

{
  int iVar1;

  iVar1 = CGeneralVolume__Unk_00414030(param_1);
  if (iVar1 != 0) {
    return *(int *)(*(int *)(iVar1 + 0xa4) + 4);
  }
  return 0;
}
