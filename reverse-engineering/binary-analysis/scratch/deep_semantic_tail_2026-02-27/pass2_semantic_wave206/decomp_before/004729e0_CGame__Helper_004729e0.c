/* address: 0x004729e0 */
/* name: CGame__Helper_004729e0 */
/* signature: void __fastcall CGame__Helper_004729e0(int param_1) */


void __fastcall CGame__Helper_004729e0(int param_1)

{
  int iVar1;
  undefined4 *puVar2;

  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined1 *)(param_1 + 0x14) = 0;
  *(undefined4 *)(param_1 + 0x18) = 0;
  *(undefined1 *)(param_1 + 0x1c) = 0;
  *(undefined4 *)(param_1 + 0x20) = 0;
  *(undefined1 *)(param_1 + 0x24) = 1;
  *(undefined4 *)(param_1 + 0x28) = 0;
  *(undefined4 *)(param_1 + 0x44) = 1;
  puVar2 = (undefined4 *)(param_1 + 0x2c);
  for (iVar1 = 6; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 1;
    puVar2 = puVar2 + 1;
  }
  return;
}
