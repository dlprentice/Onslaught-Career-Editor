/* address: 0x005a249d */
/* name: CFastVB__Helper_005a249d */
/* signature: int CFastVB__Helper_005a249d(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Helper_005a249d(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  undefined8 uVar5;
  float fVar6;
  float fVar7;
  int iVar8;
  uint uVar9;
  void *unaff_EDI;
  undefined8 *puVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  undefined8 *in_stack_00000004;
  int in_stack_00000008;
  undefined8 *in_stack_0000000c;
  int in_stack_00000010;
  void *in_stack_00000014;
  uint in_stack_00000018;
  float local_110;
  float fStack_10c;
  float fStack_108;
  float fStack_104;
  float local_100;
  float fStack_fc;
  float fStack_f8;
  float fStack_f4;
  float local_f0;
  float fStack_ec;
  float fStack_e8;
  float fStack_e4;
  float local_d0;
  float fStack_cc;
  float fStack_c8;
  float fStack_c4;
  float local_c0;
  float fStack_bc;
  float fStack_b8;
  float fStack_b4;
  float local_b0;
  float fStack_ac;
  float fStack_a8;
  float fStack_a4;
  float local_90;
  float fStack_8c;
  float fStack_88;
  float fStack_84;
  float local_80;
  float fStack_7c;
  float fStack_78;
  float fStack_74;
  float local_70;
  float fStack_6c;
  float fStack_68;
  float fStack_64;

  uVar9 = -(uint)(10 < in_stack_00000018) & in_stack_00000018 & 0xfffffffc;
  iVar8 = in_stack_00000018 - uVar9;
  uVar9 = uVar9 >> 2;
  puVar10 = in_stack_00000004;
  if (uVar9 != 0) {
    CFastVB__BroadcastMatrix4x4ToSIMDLanes(&local_110,in_stack_00000014,unaff_EDI);
    for (; uVar9 != 0; uVar9 = uVar9 - 1) {
      fVar6 = (float)*in_stack_0000000c;
      fVar14 = (float)((ulonglong)*in_stack_0000000c >> 0x20);
      uVar5 = *(undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 2);
      fVar7 = (float)uVar5;
      fVar11 = (float)((ulonglong)uVar5 >> 0x20);
      fVar12 = (float)*(undefined8 *)((int)in_stack_0000000c + in_stack_00000010);
      fVar13 = (float)((ulonglong)*(undefined8 *)((int)in_stack_0000000c + in_stack_00000010) >>
                      0x20);
      uVar5 = *(undefined8 *)(in_stack_00000010 * 3 + (int)in_stack_0000000c);
      fVar15 = (float)uVar5;
      fVar16 = (float)((ulonglong)uVar5 >> 0x20);
      fVar1 = *(float *)(in_stack_00000010 * 3 + 8 + (int)in_stack_0000000c);
      fVar2 = *(float *)((int)in_stack_0000000c + in_stack_00000010 * 2 + 8);
      fVar3 = *(float *)(in_stack_00000010 + 8 + (int)in_stack_0000000c);
      fVar4 = *(float *)(in_stack_0000000c + 0xc);
      *puVar10 = CONCAT44(fVar6 * local_100 + fVar14 * local_c0 + fVar4 * local_80,
                          fVar6 * local_110 + fVar14 * local_d0 + fVar4 * local_90);
      *(ulonglong *)((int)puVar10 + in_stack_00000008) =
           CONCAT44(fVar12 * fStack_fc + fVar13 * fStack_bc + fVar3 * fStack_7c,
                    fVar12 * fStack_10c + fVar13 * fStack_cc + fVar3 * fStack_8c);
      *(float *)(puVar10 + 0xc) = fVar6 * local_f0 + fVar14 * local_b0 + fVar4 * local_70;
      *(float *)(in_stack_00000008 + 8 + (int)puVar10) =
           fVar12 * fStack_ec + fVar13 * fStack_ac + fVar3 * fStack_6c;
      *(ulonglong *)((int)puVar10 + in_stack_00000008 * 2) =
           CONCAT44(fVar7 * fStack_f8 + fVar11 * fStack_b8 + fVar2 * fStack_78,
                    fVar7 * fStack_108 + fVar11 * fStack_c8 + fVar2 * fStack_88);
      *(ulonglong *)(in_stack_00000008 * 3 + (int)puVar10) =
           CONCAT44(fVar15 * fStack_f4 + fVar16 * fStack_b4 + fVar1 * fStack_74,
                    fVar15 * fStack_104 + fVar16 * fStack_c4 + fVar1 * fStack_84);
      *(float *)((int)puVar10 + in_stack_00000008 * 2 + 8) =
           fVar7 * fStack_e8 + fVar11 * fStack_a8 + fVar2 * fStack_68;
      *(float *)(in_stack_00000008 * 3 + 8 + (int)puVar10) =
           fVar15 * fStack_e4 + fVar16 * fStack_a4 + fVar1 * fStack_64;
      in_stack_0000000c = (undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 4);
      puVar10 = (undefined8 *)((int)puVar10 + in_stack_00000008 * 4);
    }
  }
  for (; iVar8 != 0; iVar8 = iVar8 + -1) {
    CFastVB__Helper_005a16b1(puVar10,in_stack_0000000c,in_stack_00000014);
    in_stack_0000000c = (undefined8 *)((int)in_stack_0000000c + in_stack_00000010);
    puVar10 = (undefined8 *)((int)puVar10 + in_stack_00000008);
  }
  return (int)in_stack_00000004;
}
