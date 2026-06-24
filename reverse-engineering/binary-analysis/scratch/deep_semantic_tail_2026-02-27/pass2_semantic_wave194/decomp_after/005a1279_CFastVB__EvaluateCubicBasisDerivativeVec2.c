/* address: 0x005a1279 */
/* name: CFastVB__EvaluateCubicBasisDerivativeVec2 */
/* signature: int CFastVB__EvaluateCubicBasisDerivativeVec2(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__EvaluateCubicBasisDerivativeVec2(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  undefined8 *in_stack_00000004;
  undefined8 *in_stack_00000008;
  undefined8 *in_stack_0000000c;
  undefined8 *in_stack_00000010;
  undefined8 *in_stack_00000014;
  float in_stack_00000018;

  fVar4 = in_stack_00000018 * in_stack_00000018;
  fVar5 = in_stack_00000018 * fVar4;
  fVar1 = in_stack_00000018 * _DAT_0065e5a0 + _DAT_0065e5b0 + fVar4 * _DAT_0065e590 +
          fVar5 * _DAT_0065e580;
  fVar2 = in_stack_00000018 * fRam0065e5a4 + fVar4 * fRam0065e594 + fVar5 * fRam0065e584;
  fVar3 = in_stack_00000018 * fRam0065e5a8 + fVar4 * fRam0065e598 + fVar5 * fRam0065e588;
  fVar4 = in_stack_00000018 * fRam0065e5ac + fVar4 * fRam0065e59c + fVar5 * fRam0065e58c;
  *in_stack_00000004 =
       CONCAT44((float)((ulonglong)*in_stack_00000008 >> 0x20) * fVar1 +
                (float)((ulonglong)*in_stack_00000010 >> 0x20) * fVar3 +
                (float)((ulonglong)*in_stack_0000000c >> 0x20) * fVar2 +
                (float)((ulonglong)*in_stack_00000014 >> 0x20) * fVar4,
                (float)*in_stack_00000008 * fVar1 + (float)*in_stack_00000010 * fVar3 +
                (float)*in_stack_0000000c * fVar2 + (float)*in_stack_00000014 * fVar4);
  return (int)in_stack_00000004;
}
