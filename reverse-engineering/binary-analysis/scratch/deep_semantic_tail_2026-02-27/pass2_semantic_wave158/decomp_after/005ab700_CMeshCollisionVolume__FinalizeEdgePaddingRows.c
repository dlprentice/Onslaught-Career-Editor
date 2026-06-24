/* address: 0x005ab700 */
/* name: CMeshCollisionVolume__FinalizeEdgePaddingRows */
/* signature: void CMeshCollisionVolume__FinalizeEdgePaddingRows(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CMeshCollisionVolume__FinalizeEdgePaddingRows(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int in_EAX;
  int iVar6;
  undefined4 *puVar7;
  uint uVar8;
  int *piVar9;
  int iVar10;
  uint uVar11;

  iVar2 = *(int *)(in_EAX + 0x1ac);
  iVar3 = *(int *)(in_EAX + 0x24);
  iVar10 = 0;
  if (0 < iVar3) {
    iVar4 = *(int *)(in_EAX + 0x140);
    iVar5 = *(int *)(iVar2 + 0x40);
    piVar9 = (int *)(*(int *)(in_EAX + 0xdc) + 0xc);
    do {
      uVar8 = piVar9[6] * *piVar9;
      iVar6 = (int)uVar8 / iVar4;
      uVar11 = (uint)piVar9[8] % uVar8;
      if ((uint)piVar9[8] % uVar8 == 0) {
        uVar11 = uVar8;
      }
      if (iVar10 == 0) {
        *(int *)(iVar2 + 0x48) = (int)(uVar11 - 1) / iVar6 + 1;
      }
      iVar6 = iVar6 * 2;
      if (0 < iVar6) {
        puVar1 = (undefined4 *)
                 (*(int *)(*(int *)(iVar2 + 0x38 + iVar5 * 4) + iVar10 * 4) + uVar11 * 4);
        puVar7 = puVar1;
        do {
          *puVar7 = puVar1[-1];
          puVar7 = puVar7 + 1;
          iVar6 = iVar6 + -1;
        } while (iVar6 != 0);
      }
      iVar10 = iVar10 + 1;
      piVar9 = piVar9 + 0x15;
    } while (iVar10 < iVar3);
  }
  return;
}
