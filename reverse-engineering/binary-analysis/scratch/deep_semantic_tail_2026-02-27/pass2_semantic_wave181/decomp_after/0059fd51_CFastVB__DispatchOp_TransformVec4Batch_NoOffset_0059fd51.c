/* address: 0x0059fd51 */
/* name: CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51 */
/* signature: int CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51(void)

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
  float local_d0;
  float fStack_cc;
  float fStack_c8;
  float fStack_c4;
  float local_c0;
  float fStack_bc;
  float fStack_b8;
  float fStack_b4;

  uVar3 = -(uint)(0xc < in_stack_00000018) & in_stack_00000018 & 0xfffffffc;
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
      fVar10 = (float)uVar1;
      fVar11 = (float)((ulonglong)uVar1 >> 0x20);
      fVar12 = (float)uVar2;
      fVar13 = (float)((ulonglong)uVar2 >> 0x20);
      *puVar5 = CONCAT44(fVar6 * local_100 + fVar7 * local_c0,fVar6 * local_110 + fVar7 * local_d0);
      *(ulonglong *)((int)puVar5 + in_stack_00000008) =
           CONCAT44(fVar8 * fStack_fc + fVar9 * fStack_bc,fVar8 * fStack_10c + fVar9 * fStack_cc);
      *(ulonglong *)((int)puVar5 + in_stack_00000008 * 2) =
           CONCAT44(fVar10 * fStack_f8 + fVar11 * fStack_b8,fVar10 * fStack_108 + fVar11 * fStack_c8
                   );
      *(ulonglong *)(in_stack_00000008 * 3 + (int)puVar5) =
           CONCAT44(fVar12 * fStack_f4 + fVar13 * fStack_b4,fVar12 * fStack_104 + fVar13 * fStack_c4
                   );
      in_stack_0000000c = (undefined8 *)((int)in_stack_0000000c + in_stack_00000010 * 4);
      puVar5 = (undefined8 *)((int)puVar5 + in_stack_00000008 * 4);
    }
  }
  if (in_stack_00000018 != uVar3) {
    do {
      CFastVB__DispatchIndirect_00656f44();
      unaff_EBX = unaff_EBX + -1;
    } while (unaff_EBX != 0);
  }
  return (int)in_stack_00000004;
}
