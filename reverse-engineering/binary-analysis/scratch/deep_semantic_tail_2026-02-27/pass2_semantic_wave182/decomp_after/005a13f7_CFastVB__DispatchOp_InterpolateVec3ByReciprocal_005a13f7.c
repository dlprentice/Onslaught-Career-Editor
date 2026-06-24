/* address: 0x005a13f7 */
/* name: CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7 */
/* signature: int CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7(void)

{
  float fVar1;
  float fVar2;
  undefined1 auVar3 [16];
  float fVar6;
  float fVar7;
  undefined1 auVar4 [16];
  undefined1 auVar5 [16];
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float in_XMM6_Dc;
  float in_XMM6_Dd;
  undefined8 *in_stack_00000004;
  float *in_stack_00000008;
  undefined8 *in_stack_0000000c;
  undefined8 *in_stack_00000010;

  fVar12 = in_stack_00000008[3];
  fVar1 = *(float *)(in_stack_0000000c + 1);
  fVar2 = *(float *)(in_stack_00000010 + 1);
  fVar8 = (float)*in_stack_0000000c;
  fVar9 = (float)((ulonglong)*in_stack_0000000c >> 0x20);
  fVar14 = fVar9 * in_stack_00000008[1];
  fVar10 = (float)*in_stack_00000010;
  fVar6 = *in_stack_00000008 * fVar10;
  fVar11 = (float)((ulonglong)*in_stack_00000010 >> 0x20);
  fVar7 = in_stack_00000008[1] * fVar11;
  fVar13 = fVar12 * 0.0 + fVar14;
  auVar5._0_4_ = in_stack_00000008[2] * fVar2 + fVar6;
  auVar5._4_4_ = fVar12 * 0.0 + fVar7;
  auVar5._8_4_ = fVar6 + in_XMM6_Dc;
  auVar5._12_4_ = fVar7 + in_XMM6_Dd;
  fVar6 = fVar1 * in_stack_00000008[2] + fVar8 * *in_stack_00000008 + fVar14;
  auVar4._4_12_ = auVar5._4_12_;
  auVar4._0_4_ = auVar5._0_4_ + fVar7;
  fVar7 = fVar6 - auVar4._0_4_;
  if (fVar7 == _DAT_009d2ffc) {
    in_stack_00000004 = (undefined8 *)0x0;
  }
  else {
    auVar3._4_4_ = fVar14;
    auVar3._0_4_ = fVar7;
    auVar3._8_4_ = fVar13;
    auVar3._12_4_ = fVar13;
    auVar5 = rcpss(auVar4,auVar3);
    fVar13 = auVar5._0_4_;
    fVar12 = (fVar6 + fVar12) * ((fVar13 + fVar13) - fVar7 * fVar13 * fVar13);
    *in_stack_00000004 =
         CONCAT44(fVar9 + fVar12 * (fVar11 - fVar9),fVar8 + fVar12 * (fVar10 - fVar8));
    *(float *)(in_stack_00000004 + 1) = fVar1 + fVar12 * (fVar2 - fVar1);
  }
  return (int)in_stack_00000004;
}
