/* address: 0x005a1e5b */
/* name: CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b */
/* signature: int CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b(void)

{
  undefined8 uVar1;
  undefined8 uVar2;
  int unaff_EBX;
  uint uVar3;
  uint uVar4;
  undefined8 *puVar5;
  void *unaff_EDI;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
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

  uVar3 = -(uint)(10 < in_stack_00000018) & in_stack_00000018 & 0xfffffffc;
  uVar4 = uVar3 >> 2;
  if (uVar4 != 0) {
    CFastVB__BroadcastMatrix4x4ToSIMDLanes(&local_110,in_stack_00000014,unaff_EDI);
    puVar5 = in_stack_00000004;
    for (; uVar4 != 0; uVar4 = uVar4 - 1) {
      uVar1 = *(undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 2);
      fVar6 = (float)*in_stack_0000000c;
      fVar7 = (float)((ulonglong)*in_stack_0000000c >> 0x20);
      fVar8 = (float)*(undefined8 *)((int)in_stack_0000000c + in_stack_00000010);
      fVar9 = (float)((ulonglong)*(undefined8 *)((int)in_stack_0000000c + in_stack_00000010) >> 0x20
                     );
      uVar2 = *(undefined8 *)(in_stack_00000010 * 3 + (int)in_stack_0000000c);
      fVar10 = (float)uVar1;
      fVar11 = (float)((ulonglong)uVar1 >> 0x20);
      fVar12 = (float)uVar2;
      fVar13 = (float)((ulonglong)uVar2 >> 0x20);
      *puVar5 = CONCAT44(fVar6 * local_100 + fVar7 * local_c0 + local_40,
                         fVar6 * local_110 + fVar7 * local_d0 + local_50);
      puVar5[0x10] = CONCAT44(fVar6 * local_e0 + fVar7 * local_a0 + local_20,
                              fVar6 * local_f0 + fVar7 * local_b0 + local_30);
      *(ulonglong *)((int)puVar5 + in_stack_00000008) =
           CONCAT44(fVar8 * fStack_fc + fVar9 * fStack_bc + fStack_3c,
                    fVar8 * fStack_10c + fVar9 * fStack_cc + fStack_4c);
      *(ulonglong *)(in_stack_00000008 + 8 + (int)puVar5) =
           CONCAT44(fVar8 * fStack_dc + fVar9 * fStack_9c + fStack_1c,
                    fVar8 * fStack_ec + fVar9 * fStack_ac + fStack_2c);
      *(ulonglong *)((int)puVar5 + in_stack_00000008 * 2) =
           CONCAT44(fVar10 * fStack_f8 + fVar11 * fStack_b8 + fStack_38,
                    fVar10 * fStack_108 + fVar11 * fStack_c8 + fStack_48);
      *(ulonglong *)((int)puVar5 + in_stack_00000008 * 2 + 8) =
           CONCAT44(fVar10 * fStack_d8 + fVar11 * fStack_98 + fStack_18,
                    fVar10 * fStack_e8 + fVar11 * fStack_a8 + fStack_28);
      *(ulonglong *)(in_stack_00000008 * 3 + (int)puVar5) =
           CONCAT44(fVar12 * fStack_f4 + fVar13 * fStack_b4 + fStack_34,
                    fVar12 * fStack_104 + fVar13 * fStack_c4 + fStack_44);
      *(ulonglong *)(in_stack_00000008 * 3 + 8 + (int)puVar5) =
           CONCAT44(fVar12 * fStack_d4 + fVar13 * fStack_94 + fStack_14,
                    fVar12 * fStack_e4 + fVar13 * fStack_a4 + fStack_24);
      in_stack_0000000c = (undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 4);
      puVar5 = (undefined8 *)((int)puVar5 + in_stack_00000008 * 4);
    }
  }
  if (in_stack_00000018 != uVar3) {
    do {
      CFastVB__DispatchIndirect_00656f30();
      unaff_EBX = unaff_EBX + -1;
    } while (unaff_EBX != 0);
  }
  return (int)in_stack_00000004;
}
