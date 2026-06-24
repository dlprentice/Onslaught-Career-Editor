/* address: 0x005aba90 */
/* name: CDXTexture__Unk_005aba90 */
/* signature: void __fastcall CDXTexture__Unk_005aba90(int param_1) */


void __fastcall CDXTexture__Unk_005aba90(int param_1)

{
  int iVar1;
  undefined4 uVar2;

  iVar1 = *(int *)(param_1 + 0x1b0);
  uVar2 = 1;
  if (*(int *)(param_1 + 0x14c) < 2) {
    if (*(uint *)(param_1 + 0x98) < *(int *)(param_1 + 0x144) - 1U) {
      *(undefined4 *)(iVar1 + 0x1c) = *(undefined4 *)(*(int *)(param_1 + 0x150) + 0xc);
      *(undefined4 *)(iVar1 + 0x14) = 0;
      *(undefined4 *)(iVar1 + 0x18) = 0;
      return;
    }
    uVar2 = *(undefined4 *)(*(int *)(param_1 + 0x150) + 0x48);
  }
  *(undefined4 *)(iVar1 + 0x1c) = uVar2;
  *(undefined4 *)(iVar1 + 0x14) = 0;
  *(undefined4 *)(iVar1 + 0x18) = 0;
  return;
}
