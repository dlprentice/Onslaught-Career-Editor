/* address: 0x00512fc0 */
/* name: CVBufTexture__Unk_00512fc0 */
/* signature: void __fastcall CVBufTexture__Unk_00512fc0(int param_1) */


void __fastcall CVBufTexture__Unk_00512fc0(int param_1)

{
  undefined1 *puVar1;

  puVar1 = (undefined1 *)(param_1 + 0x331e4);
  do {
    puVar1[-0x100] = 0;
    *puVar1 = 0;
    puVar1[0x100] = 0;
    puVar1 = puVar1 + 1;
  } while (puVar1 + (-0x331e4 - param_1) < (undefined1 *)0x100);
  return;
}
