/* address: 0x004145a0 */
/* name: CGeneralVolume__Unk_004145a0 */
/* signature: short * __fastcall CGeneralVolume__Unk_004145a0(void * param_1) */


short * __fastcall CGeneralVolume__Unk_004145a0(void *param_1)

{
  int iVar1;
  short *psVar2;

  iVar1 = CGeneralVolume__Unk_00414030(param_1);
  if (iVar1 != 0) {
    psVar2 = CText__GetStringById(&g_Text,*(int *)(*(int *)(iVar1 + 0xa4) + 0x3c));
    return psVar2;
  }
  return (short *)0x0;
}
