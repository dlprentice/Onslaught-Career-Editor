/* address: 0x00575dc9 */
/* name: CFastVB__HermiteInterpolateVec3 */
/* signature: int CFastVB__HermiteInterpolateVec3(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__HermiteInterpolateVec3(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float *in_stack_00000004;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float *in_stack_00000014;
  float in_stack_00000018;

  fVar1 = in_stack_00000018 * in_stack_00000018;
  fVar2 = in_stack_00000018 * fVar1;
  fVar5 = ((fVar2 + fVar2) - fVar1 * _DAT_005e9318) + _DAT_005e6a34;
  fVar3 = (fVar2 - (fVar1 + fVar1)) + in_stack_00000018;
  fVar4 = fVar1 * _DAT_005e9318 - (fVar2 + fVar2);
  fVar2 = fVar2 - fVar1;
  *in_stack_00000004 =
       fVar2 * *in_stack_00000014 +
       fVar4 * *in_stack_00000010 + fVar3 * *in_stack_0000000c + fVar5 * *in_stack_00000008;
  in_stack_00000004[1] =
       fVar5 * in_stack_00000008[1] +
       fVar3 * in_stack_0000000c[1] + fVar4 * in_stack_00000010[1] + fVar2 * in_stack_00000014[1];
  in_stack_00000004[2] =
       fVar5 * in_stack_00000008[2] +
       fVar3 * in_stack_0000000c[2] + fVar4 * in_stack_00000010[2] + fVar2 * in_stack_00000014[2];
  return (int)in_stack_00000004;
}
