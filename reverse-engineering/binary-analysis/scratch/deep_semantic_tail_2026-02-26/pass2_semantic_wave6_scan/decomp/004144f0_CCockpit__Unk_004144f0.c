/* address: 0x004144f0 */
/* name: CCockpit__Unk_004144f0 */
/* signature: int __fastcall CCockpit__Unk_004144f0(void * param_1) */


int __fastcall CCockpit__Unk_004144f0(void *param_1)

{
  int iVar1;

  iVar1 = CGeneralVolume__Unk_00414030(param_1);
  if (iVar1 != 0) {
    return *(int *)(*(int *)((int)param_1 + 0x20) + 0x544 +
                   *(int *)(*(int *)(iVar1 + 0xa4) + 0x24) * 4);
  }
  return 0;
}
