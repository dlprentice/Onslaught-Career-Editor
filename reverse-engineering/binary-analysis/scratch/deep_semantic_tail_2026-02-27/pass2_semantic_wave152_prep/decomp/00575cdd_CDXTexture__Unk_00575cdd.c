/* address: 0x00575cdd */
/* name: CDXTexture__Unk_00575cdd */
/* signature: int CDXTexture__Unk_00575cdd(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_00575cdd(void)

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
  return (int)in_stack_00000004;
}
