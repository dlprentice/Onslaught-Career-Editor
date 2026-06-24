/* address: 0x005786c0 */
/* name: CDXTexture__Unk_005786c0 */
/* signature: int CDXTexture__Unk_005786c0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_005786c0(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  int iVar7;
  float *extraout_ECX;
  int extraout_EDX;
  float *pfVar8;
  float *in_stack_00000004;
  int in_stack_00000008;
  float *in_stack_0000000c;
  int in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;

  pfVar8 = in_stack_00000004;
  for (; in_stack_00000018 != 0; in_stack_00000018 = in_stack_00000018 + -1) {
    fVar1 = in_stack_00000014[1];
    fVar2 = *in_stack_0000000c;
    fVar3 = in_stack_00000014[5];
    fVar4 = in_stack_0000000c[1];
    fVar5 = in_stack_00000014[0xd];
    fVar6 = in_stack_00000014[7] * in_stack_0000000c[1] + in_stack_00000014[3] * *in_stack_0000000c
            + in_stack_00000014[0xf];
    *pfVar8 = *in_stack_0000000c * *in_stack_00000014 + in_stack_00000014[4] * in_stack_0000000c[1]
              + in_stack_00000014[0xc];
    pfVar8[1] = fVar3 * fVar4 + fVar1 * fVar2 + fVar5;
    iVar7 = Math__IsFloatDiffOutsideTolerance(fVar6,1.0);
    if (iVar7 == 0) {
      fVar6 = 1.0 / fVar6;
      *pfVar8 = fVar6 * *pfVar8;
      pfVar8[1] = fVar6 * pfVar8[1];
    }
    in_stack_0000000c = (float *)(extraout_EDX + in_stack_00000010);
    pfVar8 = (float *)((int)pfVar8 + in_stack_00000008);
    in_stack_00000014 = extraout_ECX;
  }
  return (int)in_stack_00000004;
}
