/* address: 0x00414610 */
/* name: CMonitor__Unk_00414610 */
/* signature: int __fastcall CMonitor__Unk_00414610(void * param_1) */


int __fastcall CMonitor__Unk_00414610(void *param_1)

{
  int iVar1;

  iVar1 = CGeneralVolume__Unk_00414030(param_1);
  if (iVar1 != 0) {
    return *(int *)(*(int *)(iVar1 + 0xa4) + 0x38);
  }
  return 0;
}
