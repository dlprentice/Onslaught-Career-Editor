/* address: 0x005b44c0 */
/* name: CDXTexture__WriteEncodedBlockWithRestartControl */
/* signature: int __stdcall CDXTexture__WriteEncodedBlockWithRestartControl(int param_1, int param_2) */


int CDXTexture__WriteEncodedBlockWithRestartControl(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  int iVar5;

  uVar1 = (*(undefined4 **)(param_1 + 0x18))[1];
  iVar2 = *(int *)(param_1 + 0x174);
  iVar5 = *(int *)(param_1 + 200);
  uVar3 = *(undefined4 *)(param_1 + 0x150);
  *(undefined4 *)(iVar2 + 0x10) = **(undefined4 **)(param_1 + 0x18);
  *(undefined4 *)(iVar2 + 0x14) = uVar1;
  if ((iVar5 != 0) && (*(int *)(iVar2 + 0x44) == 0)) {
    CDXTexture__EmitRestartMarkerAndReset(*(int *)(iVar2 + 0x48));
  }
  if (0 < *(int *)(param_1 + 0x118)) {
    iVar5 = 0;
    do {
      CDXTexture__Helper_005b3ec0((int)(**(short **)(param_2 + iVar5 * 4) >> ((byte)uVar3 & 0x1f)));
      iVar5 = iVar5 + 1;
    } while (iVar5 < *(int *)(param_1 + 0x118));
  }
  puVar4 = *(undefined4 **)(param_1 + 0x18);
  iVar5 = *(int *)(param_1 + 200);
  uVar1 = *(undefined4 *)(iVar2 + 0x14);
  *puVar4 = *(undefined4 *)(iVar2 + 0x10);
  puVar4[1] = uVar1;
  if (iVar5 != 0) {
    if (*(int *)(iVar2 + 0x44) == 0) {
      *(int *)(iVar2 + 0x44) = iVar5;
      *(uint *)(iVar2 + 0x48) = *(int *)(iVar2 + 0x48) + 1U & 7;
    }
    *(int *)(iVar2 + 0x44) = *(int *)(iVar2 + 0x44) + -1;
  }
  return 1;
}
