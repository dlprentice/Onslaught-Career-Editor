/* address: 0x005a1002 */
/* name: CFastVB__EvaluateCubicBasisVec2 */
/* signature: int CFastVB__EvaluateCubicBasisVec2(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__EvaluateCubicBasisVec2(void)

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
  fVar1 = in_stack_00000018 * _DAT_0065e5e0 + _DAT_0065e5f0 + fVar4 * _DAT_0065e5d0 +
          fVar5 * _DAT_0065e5c0;
  fVar2 = in_stack_00000018 * fRam0065e5e4 + fRam0065e5f4 + fVar4 * fRam0065e5d4 +
          fVar5 * fRam0065e5c4;
  fVar3 = in_stack_00000018 * fRam0065e5e8 + fRam0065e5f8 + fVar4 * fRam0065e5d8 +
          fVar5 * fRam0065e5c8;
  fVar4 = in_stack_00000018 * fRam0065e5ec + fRam0065e5fc + fVar4 * fRam0065e5dc +
          fVar5 * fRam0065e5cc;
  *in_stack_00000004 =
       CONCAT44((float)((ulonglong)*in_stack_00000008 >> 0x20) * fVar1 +
                (float)((ulonglong)*in_stack_00000010 >> 0x20) * fVar3 +
                (float)((ulonglong)*in_stack_0000000c >> 0x20) * fVar2 +
                (float)((ulonglong)*in_stack_00000014 >> 0x20) * fVar4,
                (float)*in_stack_00000008 * fVar1 + (float)*in_stack_00000010 * fVar3 +
                (float)*in_stack_0000000c * fVar2 + (float)*in_stack_00000014 * fVar4);
  return (int)in_stack_00000004;
}
