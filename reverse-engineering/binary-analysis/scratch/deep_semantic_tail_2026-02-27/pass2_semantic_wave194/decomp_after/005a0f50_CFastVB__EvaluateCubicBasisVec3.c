/* address: 0x005a0f50 */
/* name: CFastVB__EvaluateCubicBasisVec3 */
/* signature: int CFastVB__EvaluateCubicBasisVec3(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__EvaluateCubicBasisVec3(void)

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
  fVar3 = in_stack_00000018 * _DAT_0065e5e0 + _DAT_0065e5f0 + fVar7 * _DAT_0065e5d0 +
          fVar8 * _DAT_0065e5c0;
  fVar4 = in_stack_00000018 * fRam0065e5e4 + fRam0065e5f4 + fVar7 * fRam0065e5d4 +
          fVar8 * fRam0065e5c4;
  fVar5 = in_stack_00000018 * fRam0065e5e8 + fRam0065e5f8 + fVar7 * fRam0065e5d8 +
          fVar8 * fRam0065e5c8;
  fVar6 = in_stack_00000018 * fRam0065e5ec + fRam0065e5fc + fVar7 * fRam0065e5dc +
          fVar8 * fRam0065e5cc;
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
