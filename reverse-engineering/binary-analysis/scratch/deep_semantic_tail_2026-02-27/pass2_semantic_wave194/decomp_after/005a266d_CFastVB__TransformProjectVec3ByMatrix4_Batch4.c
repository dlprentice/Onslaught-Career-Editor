/* address: 0x005a266d */
/* name: CFastVB__TransformProjectVec3ByMatrix4_Batch4 */
/* signature: int CFastVB__TransformProjectVec3ByMatrix4_Batch4(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__TransformProjectVec3ByMatrix4_Batch4(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  undefined8 uVar5;
  float fVar6;
  int iVar7;
  uint uVar8;
  void *unaff_EDI;
  undefined8 *puVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar20;
  float fVar21;
  undefined1 auVar18 [16];
  undefined1 auVar19 [16];
  float fVar22;
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
  float local_e0;
  float fStack_dc;
  float fStack_d8;
  float fStack_d4;
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
  float local_a0;
  float fStack_9c;
  float fStack_98;
  float fStack_94;
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
  float local_60;
  float fStack_5c;
  float fStack_58;
  float fStack_54;
  float local_50;
  float fStack_4c;
  float fStack_48;
  float fStack_44;
  float local_40;
  float fStack_3c;
  float fStack_38;
  float fStack_34;
  float local_30;
  float fStack_2c;
  float fStack_28;
  float fStack_24;
  float local_20;
  float fStack_1c;
  float fStack_18;
  float fStack_14;

  uVar8 = -(uint)(10 < in_stack_00000018) & in_stack_00000018 & 0xfffffffc;
  iVar7 = in_stack_00000018 - uVar8;
  uVar8 = uVar8 >> 2;
  puVar9 = in_stack_00000004;
  if (uVar8 != 0) {
    CFastVB__BroadcastMatrix4x4ToSIMDLanes(&local_110,in_stack_00000014,unaff_EDI);
    for (; uVar8 != 0; uVar8 = uVar8 - 1) {
      fVar14 = (float)((ulonglong)*in_stack_0000000c >> 0x20);
      fVar6 = (float)*in_stack_0000000c;
      uVar5 = *(undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 2);
      fVar10 = (float)uVar5;
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
      auVar18._0_4_ = fVar6 * local_e0 + fVar14 * local_a0 + fVar4 * local_60;
      auVar18._4_4_ = fVar12 * fStack_dc + fVar13 * fStack_9c + fVar3 * fStack_5c;
      auVar18._8_4_ = fVar10 * fStack_d8 + fVar11 * fStack_98 + fVar2 * fStack_58;
      auVar18._12_4_ = fVar15 * fStack_d4 + fVar16 * fStack_94 + fVar1 * fStack_54;
      auVar19._4_4_ = auVar18._4_4_ + fStack_1c;
      auVar19._0_4_ = auVar18._0_4_ + local_20;
      auVar19._8_4_ = auVar18._8_4_ + fStack_18;
      auVar19._12_4_ = auVar18._12_4_ + fStack_14;
      auVar19 = rcpps(auVar18,auVar19);
      fVar17 = auVar19._0_4_;
      fVar20 = auVar19._4_4_;
      fVar21 = auVar19._8_4_;
      fVar22 = auVar19._12_4_;
      fVar17 = (fVar17 + fVar17) - fVar17 * (auVar18._0_4_ + local_20) * fVar17;
      fVar20 = (fVar20 + fVar20) - fVar20 * (auVar18._4_4_ + fStack_1c) * fVar20;
      fVar21 = (fVar21 + fVar21) - fVar21 * (auVar18._8_4_ + fStack_18) * fVar21;
      fVar22 = (fVar22 + fVar22) - fVar22 * (auVar18._12_4_ + fStack_14) * fVar22;
      *puVar9 = CONCAT44((fVar6 * local_100 + fVar14 * local_c0 + fVar4 * local_80 + local_40) *
                         fVar17,(fVar6 * local_110 + fVar14 * local_d0 + fVar4 * local_90 + local_50
                                ) * fVar17);
      *(ulonglong *)((int)puVar9 + in_stack_00000008) =
           CONCAT44((fVar12 * fStack_fc + fVar13 * fStack_bc + fVar3 * fStack_7c + fStack_3c) *
                    fVar20,(fVar12 * fStack_10c + fVar13 * fStack_cc + fVar3 * fStack_8c + fStack_4c
                           ) * fVar20);
      *(float *)(puVar9 + 0xc) =
           (fVar6 * local_f0 + fVar14 * local_b0 + fVar4 * local_70 + local_30) * fVar17;
      *(float *)(in_stack_00000008 + 8 + (int)puVar9) =
           (fVar12 * fStack_ec + fVar13 * fStack_ac + fVar3 * fStack_6c + fStack_2c) * fVar20;
      *(ulonglong *)((int)puVar9 + in_stack_00000008 * 2) =
           CONCAT44((fVar10 * fStack_f8 + fVar11 * fStack_b8 + fVar2 * fStack_78 + fStack_38) *
                    fVar21,(fVar10 * fStack_108 + fVar11 * fStack_c8 + fVar2 * fStack_88 + fStack_48
                           ) * fVar21);
      *(ulonglong *)(in_stack_00000008 * 3 + (int)puVar9) =
           CONCAT44((fVar15 * fStack_f4 + fVar16 * fStack_b4 + fVar1 * fStack_74 + fStack_34) *
                    fVar22,(fVar15 * fStack_104 + fVar16 * fStack_c4 + fVar1 * fStack_84 + fStack_44
                           ) * fVar22);
      *(float *)((int)puVar9 + in_stack_00000008 * 2 + 8) =
           (fVar10 * fStack_e8 + fVar11 * fStack_a8 + fVar2 * fStack_68 + fStack_28) * fVar21;
      *(float *)(in_stack_00000008 * 3 + 8 + (int)puVar9) =
           (fVar15 * fStack_e4 + fVar16 * fStack_a4 + fVar1 * fStack_64 + fStack_24) * fVar22;
      in_stack_0000000c = (undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 4);
      puVar9 = (undefined8 *)((int)puVar9 + in_stack_00000008 * 4);
    }
  }
  for (; iVar7 != 0; iVar7 = iVar7 + -1) {
    CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786
              (puVar9,in_stack_0000000c,in_stack_00000014);
    in_stack_0000000c = (undefined8 *)((int)in_stack_0000000c + in_stack_00000010);
    puVar9 = (undefined8 *)((int)puVar9 + in_stack_00000008);
  }
  return (int)in_stack_00000004;
}
