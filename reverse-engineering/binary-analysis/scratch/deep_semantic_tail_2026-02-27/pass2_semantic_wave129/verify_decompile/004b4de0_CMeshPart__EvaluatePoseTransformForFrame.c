/* address: 0x004b4de0 */
/* name: CMeshPart__EvaluatePoseTransformForFrame */
/* signature: int CMeshPart__EvaluatePoseTransformForFrame(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshPart__EvaluatePoseTransformForFrame(void)

{
  float fVar1;
  float fVar2;
  int *piVar3;
  void *pvVar4;
  float fVar5;
  int iVar6;
  int iVar7;
  float *pfVar8;
  float unaff_EBX;
  float unaff_EBP;
  undefined4 *puVar9;
  void *unaff_EDI;
  undefined4 *puVar10;
  float10 fVar11;
  int *in_stack_00000004;
  int *in_stack_00000008;
  void *in_stack_0000000c;
  float *in_stack_00000010;
  undefined4 *in_stack_00000014;
  int in_stack_00000018;
  float fStack_a4;
  float fStack_9c;
  float fStack_98;
  float fStack_94;
  float fStack_8c;
  float fStack_88;
  float fStack_84;
  float fStack_60;
  float fStack_58;
  float fStack_54;
  float afStack_50 [6];
  undefined4 auStack_38 [14];

  *in_stack_00000010 = DAT_00704de8;
  in_stack_00000010[1] = DAT_00704dec;
  in_stack_00000010[2] = DAT_00704df0;
  in_stack_00000010[3] = DAT_00704df4;
  puVar9 = &DAT_00704db8;
  puVar10 = in_stack_00000014;
  for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar10 = *puVar9;
    puVar9 = puVar9 + 1;
    puVar10 = puVar10 + 1;
  }
  piVar3 = (int *)in_stack_00000004[3];
  iVar6 = (**(code **)(*in_stack_00000004 + 0x24))();
  if ((iVar6 != 0) && (in_stack_0000000c != (void *)0x0)) {
    if ((piVar3 == (int *)0x0) || (DAT_008a9aac < 2)) {
      iVar6 = (**(code **)(*in_stack_00000008 + 0x1c))();
      if (-1 < iVar6) {
        pvVar4 = (void *)(**(code **)(*in_stack_00000008 + 0x70))();
        pfVar8 = &fStack_54;
        fVar5 = (float)(**(code **)(*in_stack_00000008 + 0x1c))();
        fVar11 = (float10)(**(code **)(*in_stack_00000008 + 0x18))();
        CMeshPart__ResolveWrappedFrameIndexAndLerp
                  (in_stack_0000000c,(int)(float)fVar11,fVar5,(float)pfVar8,pvVar4,unaff_EDI);
      }
      iVar6 = CMCMech__Helper_004b0fb0();
    }
    else {
      CMeshPart__RefreshCachedPoseIfStale();
      pfVar8 = (float *)(*(int *)((int)in_stack_0000000c + 0x88) * 0x10 + piVar3[1]);
      *in_stack_00000010 = *pfVar8;
      in_stack_00000010[1] = pfVar8[1];
      in_stack_00000010[2] = pfVar8[2];
      in_stack_00000010[3] = pfVar8[3];
      puVar9 = (undefined4 *)(*(int *)((int)in_stack_0000000c + 0x88) * 0x30 + *piVar3);
      puVar10 = in_stack_00000014;
      for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
        *puVar10 = *puVar9;
        puVar9 = puVar9 + 1;
        puVar10 = puVar10 + 1;
      }
      iVar6 = in_stack_00000018;
      if (in_stack_00000018 == 0) {
        (**(code **)*in_stack_00000008)(afStack_50);
        (**(code **)(*in_stack_00000008 + 4))(&stack0xffffff58);
        fVar5 = *in_stack_00000010;
        fVar1 = *in_stack_00000010;
        fVar2 = in_stack_00000010[1];
        *in_stack_00000010 =
             fStack_a4 * in_stack_00000010[2] +
             unaff_EBP * *in_stack_00000010 + unaff_EBX * in_stack_00000010[1] + fStack_58;
        in_stack_00000010[1] =
             fStack_54 +
             fStack_94 * in_stack_00000010[2] + fStack_98 * in_stack_00000010[1] + fStack_9c * fVar5
        ;
        in_stack_00000010[2] =
             afStack_50[0] +
             fStack_84 * in_stack_00000010[2] + fStack_88 * fVar2 + fStack_8c * fVar1;
        in_stack_00000010[3] = fStack_60;
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        iVar6 = Mat34__SetRows();
        puVar9 = auStack_38;
        for (iVar7 = 0xc; iVar7 != 0; iVar7 = iVar7 + -1) {
          *in_stack_00000014 = *puVar9;
          puVar9 = puVar9 + 1;
          in_stack_00000014 = in_stack_00000014 + 1;
        }
        return iVar6;
      }
    }
  }
  return iVar6;
}
