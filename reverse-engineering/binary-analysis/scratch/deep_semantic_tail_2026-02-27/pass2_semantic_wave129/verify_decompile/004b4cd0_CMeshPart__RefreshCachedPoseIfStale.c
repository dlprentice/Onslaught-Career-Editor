/* address: 0x004b4cd0 */
/* name: CMeshPart__RefreshCachedPoseIfStale */
/* signature: int CMeshPart__RefreshCachedPoseIfStale(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshPart__RefreshCachedPoseIfStale(void)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int in_ECX;
  undefined4 *puVar5;
  undefined4 *puVar6;
  float10 fVar7;
  int in_stack_00000004;
  int *in_stack_00000008;
  int in_stack_00000010;
  undefined4 auStack_54 [12];
  undefined4 uStack_24;
  undefined4 uStack_18;

  piVar2 = in_stack_00000008;
  iVar1 = DAT_008a9aac;
  if (DAT_008a9aac == *(int *)(in_ECX + 0x14)) {
    return 0;
  }
  if ((DAT_008a9aac < *(int *)(in_ECX + 0x14) + 0x1e) && (in_stack_00000010 == 0)) {
    return 0;
  }
  uStack_18 = 0x4b4d16;
  piVar3 = (int *)(**(code **)(*in_stack_00000008 + 0x70))();
  iVar4 = *in_stack_00000008;
  in_stack_00000008 = (int *)0x0;
  uStack_18 = 0x4b4d2b;
  iVar4 = (**(code **)(iVar4 + 0x1c))();
  *(undefined4 *)(in_ECX + 0x14) = 0xffffd8f1;
  if (((*(int *)(in_stack_00000004 + 0x14) != 0) && (-1 < iVar4)) &&
     (iVar4 = *(int *)(in_stack_00000004 + 0x18) + iVar4 * 0x24, iVar4 != 0)) {
    uStack_18 = 0x4b4d55;
    fVar7 = (float10)(**(code **)(*piVar2 + 0x18))();
    in_stack_00000008 =
         (int *)(float)((float10)*(int *)(iVar4 + 0x1c) * fVar7 + (float10)*(int *)(iVar4 + 0x14));
  }
  if (piVar3 != (int *)0x0) {
    uStack_18 = 0x4b4d72;
    (**(code **)(*piVar3 + 0x20))();
  }
  uStack_18 = 0;
  uStack_24 = **(undefined4 **)(in_stack_00000004 + 0x160);
  puVar5 = &DAT_00704db8;
  puVar6 = auStack_54;
  for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar6 = *puVar5;
    puVar5 = puVar5 + 1;
    puVar6 = puVar6 + 1;
  }
  CMeshPart__PopulatePoseCacheRecursive();
  *(int *)(in_ECX + 0x14) = iVar1;
  *(int **)(in_ECX + 0x18) = in_stack_00000008;
  return 1;
}
