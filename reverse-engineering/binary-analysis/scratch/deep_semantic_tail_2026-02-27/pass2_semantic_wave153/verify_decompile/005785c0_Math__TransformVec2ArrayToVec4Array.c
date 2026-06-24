/* address: 0x005785c0 */
/* name: Math__TransformVec2ArrayToVec4Array */
/* signature: int Math__TransformVec2ArrayToVec4Array(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int Math__TransformVec2ArrayToVec4Array(void)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float *pfVar18;
  float *in_stack_00000004;
  int in_stack_00000008;
  float *in_stack_0000000c;
  int in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;

  pfVar18 = in_stack_00000004;
  for (; in_stack_00000018 != 0; in_stack_00000018 = in_stack_00000018 + -1) {
    pfVar1 = in_stack_0000000c + 1;
    fVar2 = *in_stack_0000000c;
    fVar3 = in_stack_00000014[1];
    fVar4 = *in_stack_0000000c;
    fVar5 = in_stack_00000014[5];
    fVar6 = in_stack_0000000c[1];
    fVar7 = in_stack_00000014[0xd];
    fVar8 = in_stack_00000014[2];
    fVar9 = *in_stack_0000000c;
    fVar10 = in_stack_00000014[6];
    fVar11 = in_stack_0000000c[1];
    fVar12 = in_stack_00000014[0xe];
    fVar13 = *in_stack_0000000c;
    fVar14 = in_stack_00000014[3];
    fVar15 = in_stack_0000000c[1];
    in_stack_0000000c = (float *)((int)in_stack_0000000c + in_stack_00000010);
    fVar16 = in_stack_00000014[7];
    fVar17 = in_stack_00000014[0xf];
    *pfVar18 = fVar2 * *in_stack_00000014 + in_stack_00000014[4] * *pfVar1 + in_stack_00000014[0xc];
    pfVar18[1] = fVar5 * fVar6 + fVar3 * fVar4 + fVar7;
    pfVar18[2] = fVar10 * fVar11 + fVar8 * fVar9 + fVar12;
    pfVar18[3] = fVar15 * fVar16 + fVar13 * fVar14 + fVar17;
    pfVar18 = (float *)((int)pfVar18 + in_stack_00000008);
  }
  return (int)in_stack_00000004;
}
