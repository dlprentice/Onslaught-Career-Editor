/* address: 0x0057e0c3 */
/* name: CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy */
/* signature: int __fastcall CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy(void * param_1) */


int __fastcall CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy(void *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  int *piVar8;
  undefined4 *puVar9;
  int *piVar10;
  undefined4 *puVar11;
  bool bVar12;
  uint local_c;
  uint local_8;

  iVar1 = *(int *)((int)param_1 + 4);
  iVar5 = *(int *)param_1;
  if (*(int *)(iVar1 + 4) != *(int *)(iVar5 + 4)) {
    return -0x7fffbffb;
  }
  if ((((*(int *)(iVar5 + 0x18) == 0) && (*(int *)(iVar1 + 0x1060) == *(int *)(iVar5 + 0x1060))) &&
      (*(int *)(iVar1 + 0x1064) == *(int *)(iVar5 + 0x1064))) &&
     ((*(int *)(iVar1 + 0x1068) == *(int *)(iVar5 + 0x1068) &&
      (*(int *)(iVar1 + 0x10) == *(int *)(iVar5 + 0x10))))) {
    if (*(int *)(iVar1 + 0xc) == 0) {
      iVar1 = CDXTexture__CopyDxtBlockRegion(param_1);
      return iVar1;
    }
    if (*(int *)(iVar1 + 0x1c) != 0) {
      if ((int *)(iVar1 + 0x38) != (int *)(iVar5 + 0x38)) {
        iVar2 = 0x100;
        bVar12 = true;
        piVar8 = (int *)(iVar1 + 0x38);
        piVar10 = (int *)(iVar5 + 0x38);
        do {
          if (iVar2 == 0) break;
          iVar2 = iVar2 + -1;
          bVar12 = *piVar8 == *piVar10;
          piVar8 = piVar8 + 1;
          piVar10 = piVar10 + 1;
        } while (bVar12);
        if (!bVar12) goto LAB_0057e1f6;
      }
    }
    *(undefined4 *)(iVar1 + 0x10) = 0;
    *(undefined4 *)(*(int *)param_1 + 0x10) = 0;
    iVar1 = *(int *)((int)param_1 + 4);
    local_8 = 0;
    if (*(int *)(iVar1 + 0x1068) != 0) {
      iVar5 = *(int *)param_1;
      uVar4 = *(uint *)(iVar1 + 0x1064);
      do {
        puVar6 = (undefined4 *)(*(int *)(iVar1 + 0x105c) * local_8 + *(int *)(iVar1 + 0x20));
        puVar7 = (undefined4 *)(*(int *)(iVar5 + 0x105c) * local_8 + *(int *)(iVar5 + 0x20));
        local_c = 0;
        if (uVar4 != 0) {
          do {
            uVar4 = *(uint *)(iVar1 + 0x106c);
            puVar9 = puVar7;
            puVar11 = puVar6;
            for (uVar3 = uVar4 >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
              *puVar11 = *puVar9;
              puVar9 = puVar9 + 1;
              puVar11 = puVar11 + 1;
            }
            for (uVar4 = uVar4 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
              *(undefined1 *)puVar11 = *(undefined1 *)puVar9;
              puVar9 = (undefined4 *)((int)puVar9 + 1);
              puVar11 = (undefined4 *)((int)puVar11 + 1);
            }
            iVar1 = *(int *)((int)param_1 + 4);
            iVar5 = *(int *)param_1;
            puVar6 = (undefined4 *)((int)puVar6 + *(int *)(iVar1 + 0x1058));
            puVar7 = (undefined4 *)((int)puVar7 + *(int *)(iVar5 + 0x1058));
            local_c = local_c + 1;
            uVar4 = *(uint *)(iVar1 + 0x1064);
          } while (local_c < uVar4);
        }
        local_8 = local_8 + 1;
        iVar1 = *(int *)((int)param_1 + 4);
      } while (local_8 < *(uint *)(iVar1 + 0x1068));
    }
    iVar1 = 0;
  }
  else {
LAB_0057e1f6:
    iVar1 = -0x7fffbffb;
  }
  return iVar1;
}
