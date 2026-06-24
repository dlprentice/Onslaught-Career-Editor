/* address: 0x005a40c0 */
/* name: CFastVB__Helper_005a40c0 */
/* signature: int CFastVB__Helper_005a40c0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Helper_005a40c0(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  bool bVar4;
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
  float fVar18;
  float fVar19;
  float fVar20;
  float *pfVar21;
  int iVar22;
  float *in_stack_00000004;
  int in_stack_00000008;
  float *in_stack_0000000c;
  int in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;

  if (0 < in_stack_00000018) {
    fVar5 = *in_stack_00000014;
    fVar6 = in_stack_00000014[1];
    fVar7 = in_stack_00000014[2];
    fVar8 = in_stack_00000014[3];
    fVar9 = in_stack_00000014[4];
    fVar10 = in_stack_00000014[5];
    fVar11 = in_stack_00000014[6];
    fVar12 = in_stack_00000014[7];
    fVar13 = in_stack_00000014[8];
    fVar14 = in_stack_00000014[9];
    fVar15 = in_stack_00000014[10];
    fVar16 = in_stack_00000014[0xb];
    fVar17 = in_stack_00000014[0xc];
    fVar18 = in_stack_00000014[0xd];
    fVar19 = in_stack_00000014[0xe];
    fVar20 = in_stack_00000014[0xf];
    pfVar21 = in_stack_00000004;
    do {
      fVar1 = *in_stack_0000000c;
      fVar2 = in_stack_0000000c[1];
      fVar3 = in_stack_0000000c[2];
      in_stack_0000000c = (float *)(in_stack_00000010 + (int)in_stack_0000000c);
      *pfVar21 = fVar1 * fVar5 + fVar2 * fVar9 + fVar3 * fVar13 + fVar17;
      pfVar21[1] = fVar1 * fVar6 + fVar2 * fVar10 + fVar3 * fVar14 + fVar18;
      pfVar21[2] = fVar1 * fVar7 + fVar2 * fVar11 + fVar3 * fVar15 + fVar19;
      pfVar21[3] = fVar1 * fVar8 + fVar2 * fVar12 + fVar3 * fVar16 + fVar20;
      pfVar21 = (float *)(in_stack_00000008 + (int)pfVar21);
      iVar22 = in_stack_00000018 + -1;
      bVar4 = 0 < in_stack_00000018;
      in_stack_00000018 = iVar22;
    } while (iVar22 != 0 && bVar4);
  }
  return (int)in_stack_00000004;
}
