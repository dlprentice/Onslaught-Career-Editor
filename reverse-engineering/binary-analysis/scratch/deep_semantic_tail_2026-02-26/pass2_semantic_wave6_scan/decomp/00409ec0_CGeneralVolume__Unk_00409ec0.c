/* address: 0x00409ec0 */
/* name: CGeneralVolume__Unk_00409ec0 */
/* signature: void __fastcall CGeneralVolume__Unk_00409ec0(void * param_1) */


void __fastcall CGeneralVolume__Unk_00409ec0(void *param_1)

{
  int iVar1;

  iVar1 = (**(code **)(*(int *)param_1 + 0x1d4))();
  if ((iVar1 != 0) && (*(int *)(*(int *)(iVar1 + 0xa4) + 0x34) == 1)) {
    *(undefined4 *)((int)param_1 + 0x2cc) = 0x3ecccccd;
  }
  return;
}
