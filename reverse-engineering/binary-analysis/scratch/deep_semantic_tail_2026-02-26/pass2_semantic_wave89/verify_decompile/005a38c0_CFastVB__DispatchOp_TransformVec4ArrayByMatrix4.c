/* address: 0x005a38c0 */
/* name: CFastVB__DispatchOp_TransformVec4ArrayByMatrix4 */
/* signature: int CFastVB__DispatchOp_TransformVec4ArrayByMatrix4(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_TransformVec4ArrayByMatrix4(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  bool bVar5;
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
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float *pfVar22;
  int iVar23;
  float *in_stack_00000004;
  int in_stack_00000008;
  float *in_stack_0000000c;
  int in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;

  if (0 < in_stack_00000018) {
    fVar6 = *in_stack_00000014;
    fVar7 = in_stack_00000014[1];
    fVar8 = in_stack_00000014[2];
    fVar9 = in_stack_00000014[3];
    fVar10 = in_stack_00000014[4];
    fVar11 = in_stack_00000014[5];
    fVar12 = in_stack_00000014[6];
    fVar13 = in_stack_00000014[7];
    fVar14 = in_stack_00000014[8];
    fVar15 = in_stack_00000014[9];
    fVar16 = in_stack_00000014[10];
    fVar17 = in_stack_00000014[0xb];
    fVar18 = in_stack_00000014[0xc];
    fVar19 = in_stack_00000014[0xd];
    fVar20 = in_stack_00000014[0xe];
    fVar21 = in_stack_00000014[0xf];
    pfVar22 = in_stack_00000004;
    do {
      fVar1 = *in_stack_0000000c;
      fVar2 = in_stack_0000000c[1];
      fVar3 = in_stack_0000000c[2];
      fVar4 = in_stack_0000000c[3];
      in_stack_0000000c = (float *)(in_stack_00000010 + (int)in_stack_0000000c);
      *pfVar22 = fVar1 * fVar6 + fVar2 * fVar10 + fVar3 * fVar14 + fVar4 * fVar18;
      pfVar22[1] = fVar1 * fVar7 + fVar2 * fVar11 + fVar3 * fVar15 + fVar4 * fVar19;
      pfVar22[2] = fVar1 * fVar8 + fVar2 * fVar12 + fVar3 * fVar16 + fVar4 * fVar20;
      pfVar22[3] = fVar1 * fVar9 + fVar2 * fVar13 + fVar3 * fVar17 + fVar4 * fVar21;
      pfVar22 = (float *)(in_stack_00000008 + (int)pfVar22);
      iVar23 = in_stack_00000018 + -1;
      bVar5 = 0 < in_stack_00000018;
      in_stack_00000018 = iVar23;
    } while (iVar23 != 0 && bVar5);
  }
  return (int)in_stack_00000004;
}
