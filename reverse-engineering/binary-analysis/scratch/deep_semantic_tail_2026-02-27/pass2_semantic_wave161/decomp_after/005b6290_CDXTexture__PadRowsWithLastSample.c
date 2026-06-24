/* address: 0x005b6290 */
/* name: CDXTexture__PadRowsWithLastSample */
/* signature: void __stdcall CDXTexture__PadRowsWithLastSample(int param_1, int param_2, int param_3, int param_4) */


void CDXTexture__PadRowsWithLastSample(int param_1,int param_2,int param_3,int param_4)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  undefined4 *puVar5;

  uVar3 = param_4 - param_3;
  if ((0 < (int)uVar3) && (iVar4 = 0, 0 < param_2)) {
    do {
      puVar5 = (undefined4 *)(*(int *)(param_1 + iVar4 * 4) + param_3);
      uVar1 = *(undefined1 *)((int)puVar5 + -1);
      for (uVar2 = uVar3 >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
        *puVar5 = CONCAT22(CONCAT11(uVar1,uVar1),CONCAT11(uVar1,uVar1));
        puVar5 = puVar5 + 1;
      }
      for (uVar2 = uVar3 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
        *(undefined1 *)puVar5 = uVar1;
        puVar5 = (undefined4 *)((int)puVar5 + 1);
      }
      iVar4 = iVar4 + 1;
    } while (iVar4 < param_2);
  }
  return;
}
