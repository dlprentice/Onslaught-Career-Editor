/* address: 0x0048f180 */
/* name: CUnitAI__Unk_0048f180 */
/* signature: void __fastcall CUnitAI__Unk_0048f180(int param_1) */


void __fastcall CUnitAI__Unk_0048f180(int param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 *puVar3;

  *(undefined4 *)(param_1 + 0x2c) = 1;
  if (*(undefined4 **)(param_1 + 0x40) != (undefined4 *)0x0) {
    uVar1 = *(int *)(param_1 + 0x44) << 1;
    puVar3 = *(undefined4 **)(param_1 + 0x40);
    for (uVar2 = uVar1 >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
      *puVar3 = 0xffffffff;
      puVar3 = puVar3 + 1;
    }
    for (uVar1 = uVar1 & 3; uVar1 != 0; uVar1 = uVar1 - 1) {
      *(undefined1 *)puVar3 = 0xff;
      puVar3 = (undefined4 *)((int)puVar3 + 1);
    }
    return;
  }
  CLandscapeTexture__UpdateTileRange(0,0,0x3f,0x3f);
  return;
}
