/* address: 0x004b5e80 */
/* name: CSphere__RenderPartsWithOrientation */
/* signature: int CSphere__RenderPartsWithOrientation(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CSphere__RenderPartsWithOrientation(void)

{
  int *piVar1;
  float *pfVar2;
  int iVar3;
  void *this;
  undefined4 *extraout_EAX;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  float unaff_retaddr;
  float in_stack_00000004;
  float in_stack_00000008;
  int in_stack_00000038;
  undefined4 in_stack_0000003c;
  undefined4 in_stack_00000040;
  uint in_stack_00000044;
  int *in_stack_00000048;
  int in_stack_0000004c;
  undefined1 *puVar8;
  undefined1 *rhs_basis;
  int iStack_94;
  undefined1 auStack_8c [4];
  float fStack_88;
  float fStack_84;
  float fStack_80;
  float afStack_7c [2];
  undefined1 auStack_74 [8];
  undefined4 auStack_6c [3];
  undefined1 local_60 [36];
  undefined1 auStack_3c [4];
  undefined1 auStack_38 [48];
  undefined1 auStack_8 [4];
  float fStack_4;

  piVar1 = *(int **)(in_stack_0000004c + 0xc);
  iVar3 = in_stack_0000004c;
  if (piVar1 != (int *)0x0) {
    pfVar2 = (float *)(**(code **)(*in_stack_00000048 + 4))(local_60);
    fStack_84 = unaff_retaddr * *pfVar2 +
                in_stack_00000004 * pfVar2[1] + in_stack_00000008 * pfVar2[2];
    fStack_80 = unaff_retaddr * pfVar2[4] +
                in_stack_00000004 * pfVar2[5] + in_stack_00000008 * pfVar2[6];
    afStack_7c[0] =
         unaff_retaddr * pfVar2[8] + in_stack_00000004 * pfVar2[9] + in_stack_00000008 * pfVar2[10];
    pfVar2 = (float *)(**(code **)*in_stack_00000048)(auStack_74);
    fStack_4 = fStack_88 + *pfVar2;
    rhs_basis = auStack_38;
    (**(code **)(*in_stack_00000048 + 4))();
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Mat34__SetRows();
    iVar3 = 0;
    puVar6 = auStack_6c;
    puVar7 = &stack0x00000008;
    for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
      *puVar7 = *puVar6;
      puVar6 = puVar6 + 1;
      puVar7 = puVar7 + 1;
    }
    iVar4 = 0;
    if (0 < *(int *)(in_stack_00000038 + 0x15c)) {
      iStack_94 = 0;
      do {
        if (*(int *)(piVar1[3] + iVar4 * 4) != -1) {
          puVar8 = auStack_8;
          puVar6 = (undefined4 *)(*piVar1 + iStack_94);
          puVar7 = auStack_6c;
          for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
            *puVar7 = *puVar6;
            puVar6 = puVar6 + 1;
            puVar7 = puVar7 + 1;
          }
          pfVar2 = afStack_7c;
          CSquadNormal__TransformVec3ByOrientationMatrix
                    (&stack0x00000008,auStack_8c,&stack0xffffff5c,pfVar2);
          Vec3__Add(this,pfVar2,puVar8,rhs_basis);
          CMCBuggy__MultiplyMat34Basis(&stack0x00000008,auStack_3c,auStack_6c,rhs_basis);
          iVar3 = piVar1[2];
          puVar6 = extraout_EAX;
          puVar7 = auStack_6c;
          for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
            *puVar7 = *puVar6;
            puVar6 = puVar6 + 1;
            puVar7 = puVar7 + 1;
          }
          CMeshRenderer__RenderMesh
                    (&stack0xffffff5c,auStack_6c,
                     *(undefined4 *)
                      (*(int *)(in_stack_00000038 + 0x160) + *(int *)(piVar1[3] + iVar4 * 4) * 4),
                     in_stack_0000003c,in_stack_00000040,0,
                     *(uint *)(iVar3 + iVar4 * 4) | in_stack_00000044);
        }
        iStack_94 = iStack_94 + 0x30;
        iVar4 = iVar4 + 1;
        iVar3 = *(int *)(in_stack_00000038 + 0x15c);
      } while (iVar4 < iVar3);
    }
  }
  return iVar3;
}
