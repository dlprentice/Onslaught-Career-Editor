/* address: 0x00575fa1 */
/* name: Math__InterpolateVec3ByUV */
/* signature: int Math__InterpolateVec3ByUV(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int Math__InterpolateVec3ByUV(void)

{
  float *in_stack_00000004;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float in_stack_00000014;
  float in_stack_00000018;

  *in_stack_00000004 =
       (*in_stack_00000010 - *in_stack_00000008) * in_stack_00000018 +
       (*in_stack_0000000c - *in_stack_00000008) * in_stack_00000014 + *in_stack_00000008;
  in_stack_00000004[1] =
       (in_stack_00000010[1] - in_stack_00000008[1]) * in_stack_00000018 +
       (in_stack_0000000c[1] - in_stack_00000008[1]) * in_stack_00000014 + in_stack_00000008[1];
  in_stack_00000004[2] =
       (in_stack_00000010[2] - in_stack_00000008[2]) * in_stack_00000018 +
       (in_stack_0000000c[2] - in_stack_00000008[2]) * in_stack_00000014 + in_stack_00000008[2];
  return (int)in_stack_00000004;
}
