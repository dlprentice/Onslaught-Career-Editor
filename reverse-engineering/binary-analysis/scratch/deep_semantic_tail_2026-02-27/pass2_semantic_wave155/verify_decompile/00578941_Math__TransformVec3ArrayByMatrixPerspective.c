/* address: 0x00578941 */
/* name: Math__TransformVec3ArrayByMatrixPerspective */
/* signature: int Math__TransformVec3ArrayByMatrixPerspective(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int Math__TransformVec3ArrayByMatrixPerspective(void)

{
  float fVar1;
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
  int iVar16;
  float *extraout_ECX;
  int extraout_EDX;
  float *pfVar17;
  float *in_stack_00000004;
  int in_stack_00000008;
  float *in_stack_0000000c;
  int in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;

  pfVar17 = in_stack_00000004;
  for (; in_stack_00000018 != 0; in_stack_00000018 = in_stack_00000018 + -1) {
    fVar1 = in_stack_00000014[1];
    fVar2 = *in_stack_0000000c;
    fVar3 = in_stack_00000014[5];
    fVar4 = in_stack_0000000c[1];
    fVar5 = in_stack_00000014[9];
    fVar6 = in_stack_0000000c[2];
    fVar7 = in_stack_00000014[0xd];
    fVar8 = in_stack_0000000c[2];
    fVar9 = in_stack_00000014[10];
    fVar10 = *in_stack_0000000c;
    fVar11 = in_stack_00000014[2];
    fVar12 = in_stack_0000000c[1];
    fVar13 = in_stack_00000014[6];
    fVar14 = in_stack_00000014[0xe];
    fVar15 = in_stack_00000014[0xb] * in_stack_0000000c[2] +
             in_stack_00000014[7] * in_stack_0000000c[1] + in_stack_00000014[3] * *in_stack_0000000c
             + in_stack_00000014[0xf];
    *pfVar17 = *in_stack_0000000c * *in_stack_00000014 +
               in_stack_00000014[8] * in_stack_0000000c[2] +
               in_stack_00000014[4] * in_stack_0000000c[1] + in_stack_00000014[0xc];
    pfVar17[1] = fVar5 * fVar6 + fVar3 * fVar4 + fVar1 * fVar2 + fVar7;
    pfVar17[2] = fVar12 * fVar13 + fVar10 * fVar11 + fVar8 * fVar9 + fVar14;
    iVar16 = Math__IsFloatDiffOutsideTolerance(fVar15,1.0);
    if (iVar16 == 0) {
      fVar15 = 1.0 / fVar15;
      *pfVar17 = fVar15 * *pfVar17;
      pfVar17[1] = fVar15 * pfVar17[1];
      pfVar17[2] = fVar15 * pfVar17[2];
    }
    in_stack_0000000c = (float *)(extraout_EDX + in_stack_00000010);
    pfVar17 = (float *)((int)pfVar17 + in_stack_00000008);
    in_stack_00000014 = extraout_ECX;
  }
  return (int)in_stack_00000004;
}
