/* address: 0x004815c0 */
/* name: CHud__Unk_004815c0 */
/* signature: void __fastcall CHud__Unk_004815c0(int param_1) */


void __fastcall CHud__Unk_004815c0(int param_1)

{
  undefined4 *puVar1;
  int iVar2;

  puVar1 = (undefined4 *)(param_1 + 0x34);
  for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar1 = 1;
    puVar1 = puVar1 + 1;
  }
  puVar1 = (undefined4 *)(param_1 + 0x68);
  iVar2 = 4;
  do {
    puVar1[-1] = 0xc1200000;
    *puVar1 = 0;
    puVar1 = puVar1 + 3;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  *(undefined4 *)(param_1 + 0x94) = 0;
  *(undefined4 *)(param_1 + 0xa4) = 0xc61c4000;
  *(undefined4 *)(param_1 + 0xa8) = 0xc61c4000;
  *(undefined4 *)(param_1 + 0x98) = 0;
  *(undefined4 *)(param_1 + 0xac) = 0;
  puVar1 = (undefined4 *)(param_1 + 0xe4);
  iVar2 = 4;
  do {
    puVar1[-4] = 0x3f800000;
    *puVar1 = 0x3f800000;
    puVar1[4] = 0;
    puVar1[0x2b] = 0;
    puVar1[0x35] = 0;
    puVar1[0x42] = 0;
    puVar1[0x3e] = 0;
    puVar1 = puVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}
