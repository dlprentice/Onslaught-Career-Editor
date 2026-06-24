/* address: 0x005a112c */
/* name: CFastVB__DispatchOp_CubicBlendVec3_005a112c */
/* signature: int CFastVB__DispatchOp_CubicBlendVec3_005a112c(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_CubicBlendVec3_005a112c(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  undefined8 *in_stack_00000004;
  undefined8 *in_stack_00000008;
  undefined8 *in_stack_0000000c;
  undefined8 *in_stack_00000010;
  undefined8 *in_stack_00000014;
  float in_stack_00000018;

  fVar7 = in_stack_00000018 * in_stack_00000018;
  fVar8 = in_stack_00000018 * fVar7;
  fVar3 = in_stack_00000018 * _DAT_0065e5a0 + _DAT_0065e5b0 + fVar7 * _DAT_0065e590 +
          fVar8 * _DAT_0065e580;
  fVar4 = in_stack_00000018 * fRam0065e5a4 + fVar7 * fRam0065e594 + fVar8 * fRam0065e584;
  fVar5 = in_stack_00000018 * fRam0065e5a8 + fVar7 * fRam0065e598 + fVar8 * fRam0065e588;
  fVar6 = in_stack_00000018 * fRam0065e5ac + fVar7 * fRam0065e59c + fVar8 * fRam0065e58c;
  fVar7 = *(float *)(in_stack_00000008 + 1);
  fVar8 = *(float *)(in_stack_0000000c + 1);
  fVar1 = *(float *)(in_stack_00000010 + 1);
  fVar2 = *(float *)(in_stack_00000014 + 1);
  *in_stack_00000004 =
       CONCAT44((float)((ulonglong)*in_stack_00000008 >> 0x20) * fVar3 +
                (float)((ulonglong)*in_stack_0000000c >> 0x20) * fVar4 +
                (float)((ulonglong)*in_stack_00000010 >> 0x20) * fVar5 +
                (float)((ulonglong)*in_stack_00000014 >> 0x20) * fVar6,
                (float)*in_stack_00000008 * fVar3 + (float)*in_stack_0000000c * fVar4 +
                (float)*in_stack_00000010 * fVar5 + (float)*in_stack_00000014 * fVar6);
  *(float *)(in_stack_00000004 + 1) = fVar7 * fVar3 + fVar8 * fVar4 + fVar1 * fVar5 + fVar2 * fVar6;
  return (int)in_stack_00000004;
}
