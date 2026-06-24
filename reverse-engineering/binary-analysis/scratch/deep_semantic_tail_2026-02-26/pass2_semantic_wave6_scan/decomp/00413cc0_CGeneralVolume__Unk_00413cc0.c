/* address: 0x00413cc0 */
/* name: CGeneralVolume__Unk_00413cc0 */
/* signature: void __fastcall CGeneralVolume__Unk_00413cc0(int param_1) */


void __fastcall CGeneralVolume__Unk_00413cc0(int param_1)

{
  void *pvVar1;

  *(undefined4 *)(*(int *)(param_1 + 0x20) + 0x588) = 0;
  pvVar1 = (void *)CGeneralVolume__Unk_00414030((void *)param_1);
  if ((pvVar1 != (void *)0x0) && (*(int *)((int)pvVar1 + 0x9c) != 0)) {
    CGeneralVolume__Helper_00506010(pvVar1);
    return;
  }
  return;
}
