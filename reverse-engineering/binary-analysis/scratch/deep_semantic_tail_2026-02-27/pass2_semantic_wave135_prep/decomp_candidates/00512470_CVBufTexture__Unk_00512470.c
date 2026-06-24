/* address: 0x00512470 */
/* name: CVBufTexture__Unk_00512470 */
/* signature: void __fastcall CVBufTexture__Unk_00512470(int param_1) */


void __fastcall CVBufTexture__Unk_00512470(int param_1)

{
  int iVar1;
  undefined4 *puVar2;

  puVar2 = (undefined4 *)(param_1 + 0x332e4);
  for (iVar1 = 0x40; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  return;
}
