/* address: 0x004b4ba0 */
/* name: CMeshPart__PopulatePoseCacheRecursive */
/* signature: int CMeshPart__PopulatePoseCacheRecursive(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshPart__PopulatePoseCacheRecursive(void)

{
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  int *in_ECX;
  int iVar4;
  undefined4 *puVar5;
  undefined4 in_stack_00000004;
  undefined4 in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;
  int in_stack_00000044;
  undefined4 in_stack_00000048;
  undefined4 in_stack_0000004c;
  undefined4 in_stack_00000050;
  undefined4 auStack_54 [9];
  undefined4 uStack_30;
  undefined4 *puStack_28;
  undefined1 *puStack_24;
  undefined4 uStack_20;
  int **ppiStack_1c;
  undefined4 *puStack_18;
  int *local_4;

  iVar2 = in_stack_00000044;
  puStack_18 = &stack0x00000050;
  ppiStack_1c = &local_4;
  puStack_24 = &stack0x00000014;
  puStack_28 = &stack0x00000004;
  uStack_30 = 0x4b4bd2;
  local_4 = in_ECX;
  CMeshPart__EvaluateAnimatedTransformCore();
  piVar1 = (int *)(in_stack_00000044 + 0x88);
  in_stack_00000044 = 0;
  puVar3 = (undefined4 *)&stack0x00000014;
  puVar5 = (undefined4 *)(*piVar1 * 0x30 + *in_ECX);
  for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar5 = *puVar3;
    puVar3 = puVar3 + 1;
    puVar5 = puVar5 + 1;
  }
  puVar3 = (undefined4 *)(*(int *)(iVar2 + 0x88) * 0x10 + in_ECX[1]);
  *puVar3 = in_stack_00000004;
  puVar3[1] = in_stack_00000008;
  puVar3[2] = in_stack_0000000c;
  puVar3[3] = in_stack_00000010;
  *(int *)(in_ECX[3] + *(int *)(iVar2 + 0x88) * 4) = local_4[0x22];
  *(undefined4 *)(in_ECX[2] + *(int *)(iVar2 + 0x88) * 4) = in_stack_00000050;
  iVar4 = *(int *)(iVar2 + 0x90);
  if (0 < iVar4) {
    do {
      puStack_18 = (undefined4 *)in_stack_00000050;
      ppiStack_1c = (int **)in_stack_0000004c;
      uStack_20 = in_stack_00000048;
      puStack_24 = *(undefined1 **)(*(int *)(iVar2 + 0x94) + in_stack_00000044 * 4);
      puVar3 = (undefined4 *)&stack0x00000014;
      puVar5 = auStack_54;
      for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
        *puVar5 = *puVar3;
        puVar3 = puVar3 + 1;
        puVar5 = puVar5 + 1;
      }
      CMeshPart__PopulatePoseCacheRecursive();
      iVar4 = in_stack_00000044 + 1;
      in_stack_00000044 = iVar4;
    } while (iVar4 < *(int *)(iVar2 + 0x90));
  }
  return iVar4;
}
