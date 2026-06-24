/* address: 0x005b8060 */
/* name: CDXTexture__Unk_005b8060 */
/* signature: void __stdcall CDXTexture__Unk_005b8060(int param_1) */


void CDXTexture__Unk_005b8060(int param_1)

{
  int iVar1;

  iVar1 = *(int *)(param_1 + 0x164);
  *(undefined4 *)(*(int *)(param_1 + 0x154) + 0xc) = 0;
  (**(code **)(iVar1 + 4))(param_1);
  (**(code **)(*(int *)(param_1 + 0x164) + 8))(param_1);
  return;
}
