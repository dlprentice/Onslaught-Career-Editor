/* address: 0x005a1fe9 */
/* name: CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9 */
/* signature: int CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9(void)

{
  undefined8 uVar1;
  undefined8 uVar2;
  int unaff_EBX;
  uint uVar3;
  uint uVar4;
  void *unaff_EDI;
  undefined8 *puVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar13;
  float fVar14;
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
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
  float local_a0;
  float fStack_9c;
  float fStack_98;
  float fStack_94;
  float local_50;
  float fStack_4c;
  float fStack_48;
  float fStack_44;
  float local_40;
  float fStack_3c;
  float fStack_38;
  float fStack_34;
  float local_20;
  float fStack_1c;
  float fStack_18;
  float fStack_14;

  uVar3 = -(uint)(10 < in_stack_00000018) & in_stack_00000018 & 0xfffffffc;
  uVar4 = uVar3 >> 2;
  if (uVar4 != 0) {
    CFastVB__BroadcastMatrix4x4ToSIMDLanes(&local_110,in_stack_00000014,unaff_EDI);
    puVar5 = in_stack_00000004;
    for (; uVar4 != 0; uVar4 = uVar4 - 1) {
      fVar6 = (float)*in_stack_0000000c;
      fVar7 = (float)((ulonglong)*in_stack_0000000c >> 0x20);
      fVar8 = (float)*(undefined8 *)((int)in_stack_0000000c + in_stack_00000010);
      fVar9 = (float)((ulonglong)*(undefined8 *)((int)in_stack_0000000c + in_stack_00000010) >> 0x20
                     );
      uVar1 = *(undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 2);
      uVar2 = *(undefined8 *)(in_stack_00000010 * 3 + (int)in_stack_0000000c);
      fVar16 = (float)uVar1;
      fVar17 = (float)((ulonglong)uVar1 >> 0x20);
      fVar18 = (float)uVar2;
      fVar19 = (float)((ulonglong)uVar2 >> 0x20);
      auVar11._0_4_ = fVar6 * local_e0 + fVar7 * local_a0;
      auVar11._4_4_ = fVar8 * fStack_dc + fVar9 * fStack_9c;
      auVar11._8_4_ = fVar16 * fStack_d8 + fVar17 * fStack_98;
      auVar11._12_4_ = fVar18 * fStack_d4 + fVar19 * fStack_94;
      auVar12._4_4_ = auVar11._4_4_ + fStack_1c;
      auVar12._0_4_ = auVar11._0_4_ + local_20;
      auVar12._8_4_ = auVar11._8_4_ + fStack_18;
      auVar12._12_4_ = auVar11._12_4_ + fStack_14;
      auVar12 = rcpps(auVar11,auVar12);
      fVar10 = auVar12._0_4_;
      fVar13 = auVar12._4_4_;
      fVar14 = auVar12._8_4_;
      fVar15 = auVar12._12_4_;
      fVar10 = (fVar10 + fVar10) - fVar10 * (auVar11._0_4_ + local_20) * fVar10;
      fVar13 = (fVar13 + fVar13) - fVar13 * (auVar11._4_4_ + fStack_1c) * fVar13;
      fVar14 = (fVar14 + fVar14) - fVar14 * (auVar11._8_4_ + fStack_18) * fVar14;
      fVar15 = (fVar15 + fVar15) - fVar15 * (auVar11._12_4_ + fStack_14) * fVar15;
      *puVar5 = CONCAT44((fVar6 * local_100 + fVar7 * local_c0 + local_40) * fVar10,
                         (fVar6 * local_110 + fVar7 * local_d0 + local_50) * fVar10);
      *(ulonglong *)((int)puVar5 + in_stack_00000008) =
           CONCAT44((fVar8 * fStack_fc + fVar9 * fStack_bc + fStack_3c) * fVar13,
                    (fVar8 * fStack_10c + fVar9 * fStack_cc + fStack_4c) * fVar13);
      *(ulonglong *)((int)puVar5 + in_stack_00000008 * 2) =
           CONCAT44((fVar16 * fStack_f8 + fVar17 * fStack_b8 + fStack_38) * fVar14,
                    (fVar16 * fStack_108 + fVar17 * fStack_c8 + fStack_48) * fVar14);
      *(ulonglong *)(in_stack_00000008 * 3 + (int)puVar5) =
           CONCAT44((fVar18 * fStack_f4 + fVar19 * fStack_b4 + fStack_34) * fVar15,
                    (fVar18 * fStack_104 + fVar19 * fStack_c4 + fStack_44) * fVar15);
      in_stack_0000000c = (undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 4);
      puVar5 = (undefined8 *)((int)puVar5 + in_stack_00000008 * 4);
    }
  }
  if (in_stack_00000018 != uVar3) {
    do {
      CFastVB__DispatchIndirect_00656f54();
      unaff_EBX = unaff_EBX + -1;
    } while (unaff_EBX != 0);
  }
  return (int)in_stack_00000004;
}
