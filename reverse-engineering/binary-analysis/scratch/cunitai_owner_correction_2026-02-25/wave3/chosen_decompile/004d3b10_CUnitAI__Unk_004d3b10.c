/* address: 0x004d3b10 */
/* name: CUnitAI__Unk_004d3b10 */
/* signature: int CUnitAI__Unk_004d3b10(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnitAI__Unk_004d3b10(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;
  float *in_stack_00000014;
  float *in_stack_00000018;

  fVar1 = in_stack_00000004 + in_stack_0000000c;
  if ((fVar1 < *in_stack_00000014) && (fVar1 < *in_stack_00000018)) {
    return 0;
  }
  if ((*in_stack_00000014 < in_stack_00000004) && (*in_stack_00000018 < in_stack_00000004)) {
    return 0;
  }
  fVar2 = in_stack_00000008 + in_stack_00000010;
  if ((fVar2 < in_stack_00000014[1]) && (fVar2 < in_stack_00000018[1])) {
    return 0;
  }
  if ((in_stack_00000014[1] < in_stack_00000008) && (in_stack_00000018[1] < in_stack_00000008)) {
    return 0;
  }
  fVar3 = *in_stack_00000018 - *in_stack_00000014;
  fVar4 = in_stack_00000018[1] - in_stack_00000014[1];
  if (fVar3 != (float)_DAT_005d87b0) {
    fVar6 = (in_stack_00000004 - *in_stack_00000014) * (fVar4 / fVar3) + in_stack_00000014[1];
    fVar5 = (fVar1 - *in_stack_00000014) * (fVar4 / fVar3) + in_stack_00000014[1];
    if ((fVar2 <= fVar6) && (fVar2 <= fVar5)) {
      return 0;
    }
    if ((fVar6 < in_stack_00000008) && (fVar5 < in_stack_00000008)) {
      return 0;
    }
  }
  if (fVar4 != (float)_DAT_005d87b0) {
    fVar5 = (in_stack_00000008 - in_stack_00000014[1]) * (fVar3 / fVar4) + *in_stack_00000014;
    fVar2 = (fVar2 - in_stack_00000014[1]) * (fVar3 / fVar4) + *in_stack_00000014;
    if ((fVar1 <= fVar5) && (fVar1 <= fVar2)) {
      return 0;
    }
    if ((fVar5 < in_stack_00000004) && (fVar2 < in_stack_00000004)) {
      return 0;
    }
  }
  return 1;
}
