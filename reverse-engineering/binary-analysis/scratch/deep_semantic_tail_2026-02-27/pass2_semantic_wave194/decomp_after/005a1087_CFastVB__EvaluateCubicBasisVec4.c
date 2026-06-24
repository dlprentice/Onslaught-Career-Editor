/* address: 0x005a1087 */
/* name: CFastVB__EvaluateCubicBasisVec4 */
/* signature: int CFastVB__EvaluateCubicBasisVec4(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__EvaluateCubicBasisVec4(void)

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
  float fVar16;
  float *in_stack_00000004;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float *in_stack_00000014;
  float in_stack_00000018;

  fVar15 = in_stack_00000018 * in_stack_00000018;
  fVar16 = in_stack_00000018 * fVar15;
  fVar11 = in_stack_00000018 * _DAT_0065e5e0 + _DAT_0065e5f0 + fVar15 * _DAT_0065e5d0 +
           fVar16 * _DAT_0065e5c0;
  fVar12 = in_stack_00000018 * fRam0065e5e4 + fRam0065e5f4 + fVar15 * fRam0065e5d4 +
           fVar16 * fRam0065e5c4;
  fVar13 = in_stack_00000018 * fRam0065e5e8 + fRam0065e5f8 + fVar15 * fRam0065e5d8 +
           fVar16 * fRam0065e5c8;
  fVar14 = in_stack_00000018 * fRam0065e5ec + fRam0065e5fc + fVar15 * fRam0065e5dc +
           fVar16 * fRam0065e5cc;
  fVar15 = in_stack_00000008[1];
  fVar16 = in_stack_00000008[2];
  fVar1 = in_stack_00000008[3];
  fVar2 = in_stack_0000000c[1];
  fVar3 = in_stack_0000000c[2];
  fVar4 = in_stack_0000000c[3];
  fVar5 = in_stack_00000010[1];
  fVar6 = in_stack_00000010[2];
  fVar7 = in_stack_00000010[3];
  fVar8 = in_stack_00000014[1];
  fVar9 = in_stack_00000014[2];
  fVar10 = in_stack_00000014[3];
  *in_stack_00000004 =
       *in_stack_00000008 * fVar11 + *in_stack_0000000c * fVar12 + *in_stack_00000010 * fVar13 +
       *in_stack_00000014 * fVar14;
  in_stack_00000004[1] = fVar15 * fVar11 + fVar2 * fVar12 + fVar5 * fVar13 + fVar8 * fVar14;
  in_stack_00000004[2] = fVar16 * fVar11 + fVar3 * fVar12 + fVar6 * fVar13 + fVar9 * fVar14;
  in_stack_00000004[3] = fVar1 * fVar11 + fVar4 * fVar12 + fVar7 * fVar13 + fVar10 * fVar14;
  return (int)in_stack_00000004;
}
