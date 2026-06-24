/* address: 0x00578794 */
/* name: Math__TransformVec2ArrayByMatrixLinear */
/* signature: int Math__TransformVec2ArrayByMatrixLinear(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int Math__TransformVec2ArrayByMatrixLinear(void)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float *pfVar7;
  float *in_stack_00000004;
  int in_stack_00000008;
  float *in_stack_0000000c;
  int in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;

  pfVar7 = in_stack_00000004;
  for (; in_stack_00000018 != 0; in_stack_00000018 = in_stack_00000018 + -1) {
    pfVar1 = in_stack_0000000c + 1;
    fVar2 = *in_stack_0000000c;
    fVar3 = in_stack_00000014[1];
    fVar4 = *in_stack_0000000c;
    fVar5 = in_stack_00000014[5];
    fVar6 = in_stack_0000000c[1];
    in_stack_0000000c = (float *)((int)in_stack_0000000c + in_stack_00000010);
    *in_stack_00000004 = fVar2 * *in_stack_00000014 + in_stack_00000014[4] * *pfVar1;
    in_stack_00000004[1] = fVar5 * fVar6 + fVar3 * fVar4;
    in_stack_00000004 = (float *)((int)in_stack_00000004 + in_stack_00000008);
  }
  return (int)pfVar7;
}
