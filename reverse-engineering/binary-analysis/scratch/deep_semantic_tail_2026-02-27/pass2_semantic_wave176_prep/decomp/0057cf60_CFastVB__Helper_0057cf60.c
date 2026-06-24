/* address: 0x0057cf60 */
/* name: CFastVB__Helper_0057cf60 */
/* signature: int __fastcall CFastVB__Helper_0057cf60(void * param_1) */


int __fastcall CFastVB__Helper_0057cf60(void *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;
  int iStack_2c;
  uint local_14;
  undefined4 *local_10;
  uint local_c;
  undefined4 *local_8;

  iVar4 = *(int *)param_1;
  if (((*(uint *)(iVar4 + 0x1044) | *(uint *)(iVar4 + 0x1040) | *(uint *)(iVar4 + 0x1038) |
       *(uint *)(iVar4 + 0x103c)) & 3) != 0) {
    return -0x7fffbffb;
  }
  iVar1 = *(int *)((int)param_1 + 4);
  if (((*(uint *)(iVar1 + 0x1044) | *(uint *)(iVar1 + 0x1040) | *(uint *)(iVar1 + 0x1038) |
       *(uint *)(iVar1 + 0x103c)) & 3) == 0) {
    iVar2 = *(int *)(iVar1 + 4);
    if (iVar2 == 0x31545844) {
      iStack_2c = 8;
    }
    else {
      if ((((iVar2 != 0x32545844) && (iVar2 != 0x33545844)) && (iVar2 != 0x34545844)) &&
         (iVar2 != 0x35545844)) goto LAB_0057cfc3;
      iStack_2c = 0x10;
    }
    uVar3 = *(uint *)(iVar1 + 0x1060);
    local_10 = (undefined4 *)
               ((*(uint *)(iVar1 + 0x103c) >> 2) * *(int *)(iVar1 + 0x1058) +
                *(int *)(iVar1 + 0x105c) * *(int *)(iVar1 + 0x1048) +
                (*(uint *)(iVar1 + 0x1038) >> 2) * iStack_2c + *(int *)(iVar1 + 0x20));
    local_14 = 0;
    puVar7 = (undefined4 *)
             ((*(uint *)(iVar4 + 0x103c) >> 2) * *(int *)(iVar4 + 0x1058) +
              *(int *)(iVar4 + 0x105c) * *(int *)(iVar4 + 0x1048) +
              (*(uint *)(iVar4 + 0x1038) >> 2) * iStack_2c + *(int *)(iVar4 + 0x20));
    if (*(int *)(iVar1 + 0x1068) != 0) {
      uVar5 = *(uint *)(iVar1 + 0x1064);
      do {
        local_c = 0;
        puVar6 = local_10;
        local_8 = puVar7;
        if (uVar5 != 0) {
          do {
            local_c = local_c + 4;
            puVar8 = local_8;
            puVar9 = puVar6;
            for (uVar5 = (uVar3 >> 2) * iStack_2c >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
              *puVar9 = *puVar8;
              puVar8 = puVar8 + 1;
              puVar9 = puVar9 + 1;
            }
            for (iVar4 = 0; iVar4 != 0; iVar4 = iVar4 + -1) {
              *(undefined1 *)puVar9 = *(undefined1 *)puVar8;
              puVar8 = (undefined4 *)((int)puVar8 + 1);
              puVar9 = (undefined4 *)((int)puVar9 + 1);
            }
            puVar6 = (undefined4 *)((int)puVar6 + *(int *)(*(int *)((int)param_1 + 4) + 0x1058));
            uVar5 = *(uint *)(*(int *)((int)param_1 + 4) + 0x1064);
            local_8 = (undefined4 *)((int)local_8 + *(int *)(*(int *)param_1 + 0x1058));
          } while (local_c < uVar5);
        }
        local_10 = (undefined4 *)((int)local_10 + *(int *)(*(int *)((int)param_1 + 4) + 0x105c));
        puVar7 = (undefined4 *)((int)puVar7 + *(int *)(*(int *)param_1 + 0x105c));
        local_14 = local_14 + 1;
      } while (local_14 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1068));
    }
    iVar4 = 0;
  }
  else {
LAB_0057cfc3:
    iVar4 = -0x7fffbffb;
  }
  return iVar4;
}
