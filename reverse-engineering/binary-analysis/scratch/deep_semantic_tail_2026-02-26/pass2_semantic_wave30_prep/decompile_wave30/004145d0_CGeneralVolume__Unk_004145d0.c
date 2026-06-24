/* address: 0x004145d0 */
/* name: CGeneralVolume__Unk_004145d0 */
/* signature: int __fastcall CGeneralVolume__Unk_004145d0(void * param_1) */


int __fastcall CGeneralVolume__Unk_004145d0(void *param_1)

{
  int iVar1;

  iVar1 = CGeneralVolume__Unk_00414030(param_1);
  if (iVar1 != 0) {
    return **(int **)(iVar1 + 0xa4);
  }
  return 0;
}
