/* address: 0x005ab4d0 */
/* name: CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh */
/* signature: void __fastcall CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh(int param_1) */


void __fastcall CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int *piVar6;
  undefined4 *puVar7;
  int *piVar8;
  undefined4 *puVar9;
  undefined4 *puVar10;
  int iVar11;
  int *local_20;
  int local_18;
  int local_10;

  iVar11 = *(int *)(param_1 + 0x1ac);
  iVar1 = *(int *)(param_1 + 0x140);
  local_10 = *(int *)(param_1 + 0x24);
  if (0 < local_10) {
    piVar6 = *(int **)(iVar11 + 0x3c);
    local_20 = (int *)(iVar11 + 8);
    piVar8 = (int *)(*(int *)(param_1 + 0xdc) + 0xc);
    iVar11 = *(int *)(iVar11 + 0x38) - (int)piVar6;
    do {
      iVar5 = (piVar8[6] * *piVar8) / iVar1;
      puVar2 = *(undefined4 **)(iVar11 + (int)piVar6);
      puVar7 = (undefined4 *)*piVar6;
      iVar3 = *local_20;
      local_18 = (iVar1 + 2) * iVar5;
      if (0 < local_18) {
        puVar9 = puVar7;
        do {
          uVar4 = *(undefined4 *)((int)puVar9 + (iVar3 - (int)puVar7));
          *(undefined4 *)(((int)puVar2 - (int)puVar7) + (int)puVar9) = uVar4;
          *puVar9 = uVar4;
          puVar9 = puVar9 + 1;
          local_18 = local_18 + -1;
        } while (local_18 != 0);
      }
      if (0 < iVar5 * 2) {
        puVar9 = puVar7 + iVar5 * iVar1;
        puVar10 = (undefined4 *)(iVar3 + (iVar1 + -2) * iVar5 * 4);
        local_18 = iVar5 * 2;
        do {
          *(undefined4 *)(((int)puVar7 - iVar3) + (int)puVar10) =
               *(undefined4 *)((int)puVar9 + (iVar3 - (int)puVar7));
          *puVar9 = *puVar10;
          puVar10 = puVar10 + 1;
          puVar9 = puVar9 + 1;
          local_18 = local_18 + -1;
        } while (local_18 != 0);
      }
      if (0 < iVar5) {
        puVar7 = puVar2 + -iVar5;
        do {
          *puVar7 = *puVar2;
          puVar7 = puVar7 + 1;
          iVar5 = iVar5 + -1;
        } while (iVar5 != 0);
      }
      piVar6 = piVar6 + 1;
      local_20 = local_20 + 1;
      piVar8 = piVar8 + 0x15;
      local_10 = local_10 + -1;
    } while (local_10 != 0);
  }
  return;
}
