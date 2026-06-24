/* address: 0x005a519e */
/* name: CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e */
/* signature: int CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e(void)

{
  undefined4 unaff_ESI;
  undefined4 extraout_MM0_Da;
  undefined4 extraout_MM0_Da_00;
  undefined4 extraout_MM0_Da_01;
  undefined4 extraout_MM0_Da_02;
  undefined8 uVar1;
  ulonglong extraout_MM0;
  ulonglong extraout_MM0_00;
  ulonglong extraout_MM0_01;
  ulonglong extraout_MM0_02;
  ulonglong extraout_MM0_03;
  ulonglong extraout_MM0_04;
  undefined8 uVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  ulonglong uVar5;
  ulonglong uVar6;
  undefined8 uVar7;
  ulonglong uVar8;
  undefined8 uVar9;
  ulonglong uVar10;
  undefined8 uVar11;
  ulonglong uVar12;
  ulonglong uVar13;
  undefined8 uVar14;
  undefined8 *in_stack_00000004;
  undefined8 *in_stack_00000008;
  ulonglong *in_stack_0000000c;
  ulonglong *in_stack_00000010;
  ulonglong *in_stack_00000014;
  ulonglong *in_stack_00000018;
  ulonglong *in_stack_0000001c;
  ulonglong local_a8;
  ulonglong local_a0;
  ulonglong local_88;
  ulonglong local_80;
  ulonglong local_78;
  ulonglong local_70;
  undefined4 local_20;

  local_a8 = *in_stack_00000010;
  local_a0 = in_stack_00000010[1];
  uVar6 = *in_stack_00000014;
  uVar13 = in_stack_00000014[1];
  uVar1 = PackedFloatingADD(local_a8,uVar6);
  uVar2 = PackedFloatingADD(local_a0,uVar13);
  uVar4 = PackedFloatingSUB(local_a8,uVar6);
  uVar1 = PackedFloatingMUL(uVar1,uVar1);
  uVar7 = PackedFloatingSUB(local_a0,uVar13);
  uVar2 = PackedFloatingMUL(uVar2,uVar2);
  uVar4 = PackedFloatingMUL(uVar4,uVar4);
  uVar7 = PackedFloatingMUL(uVar7,uVar7);
  uVar1 = PackedFloatingADD(uVar1,uVar2);
  uVar4 = PackedFloatingADD(uVar4,uVar7);
  local_88 = *in_stack_00000018;
  local_80 = in_stack_00000018[1];
  uVar9 = PackedFloatingADD(uVar6,local_88);
  uVar11 = PackedFloatingADD(uVar13,local_80);
  uVar2 = PackedFloatingSUB(uVar6,local_88);
  uVar7 = PackedFloatingSUB(uVar13,local_80);
  uVar9 = PackedFloatingMUL(uVar9,uVar9);
  uVar11 = PackedFloatingMUL(uVar11,uVar11);
  uVar2 = PackedFloatingMUL(uVar2,uVar2);
  uVar7 = PackedFloatingMUL(uVar7,uVar7);
  uVar9 = PackedFloatingADD(uVar9,uVar11);
  uVar2 = PackedFloatingADD(uVar2,uVar7);
  uVar1 = PackedFloatingAccumulate(uVar1,uVar9);
  uVar2 = PackedFloatingAccumulate(uVar4,uVar2);
  uVar1 = PackedFloatingCompareGT(uVar2,uVar1);
  uVar5 = packsswb(uVar1,uVar1);
  if ((uVar5 & 1) != 0) {
    local_a8 = DAT_005ef128 ^ *in_stack_00000010;
    local_a0 = DAT_005ef128 ^ in_stack_00000010[1];
  }
  if ((uVar5 & 0x10000) != 0) {
    local_88 = DAT_005ef128 ^ *in_stack_00000018;
    local_80 = DAT_005ef128 ^ in_stack_00000018[1];
  }
  local_78 = *in_stack_0000001c;
  uVar5 = in_stack_0000001c[1];
  uVar4 = PackedFloatingADD(local_88,local_78);
  uVar7 = PackedFloatingADD(local_80,uVar5);
  uVar1 = PackedFloatingSUB(local_88,local_78);
  uVar2 = PackedFloatingSUB(local_80,uVar5);
  uVar4 = PackedFloatingMUL(uVar4,uVar4);
  uVar7 = PackedFloatingMUL(uVar7,uVar7);
  uVar1 = PackedFloatingMUL(uVar1,uVar1);
  uVar2 = PackedFloatingMUL(uVar2,uVar2);
  uVar4 = PackedFloatingADD(uVar4,uVar7);
  uVar1 = PackedFloatingADD(uVar1,uVar2);
  uVar2 = PackedFloatingAccumulate(uVar4,uVar4);
  uVar1 = PackedFloatingAccumulate(uVar1,uVar1);
  uVar8 = PackedFloatingCompareGT(uVar1,uVar2);
  local_70 = uVar5;
  if ((uVar8 & 1) != 0) {
    local_78 = DAT_005ef128 ^ *in_stack_0000001c;
    local_70 = DAT_005ef128 ^ in_stack_0000001c[1];
  }
  uVar1 = PackedFloatingMUL(uVar6,uVar6);
  uVar2 = PackedFloatingMUL(uVar13,uVar13);
  uVar1 = PackedFloatingADD(uVar1,uVar2);
  uVar1 = PackedFloatingAccumulate(uVar1,uVar1);
  uVar2 = FloatingReciprocalAprox(uVar5,uVar1);
  uVar5 = PackedFloatingCompareGT(uVar1,_PTR_DAT_005ef170);
  uVar1 = PackedFloatingReciprocalIter1(uVar1,uVar2);
  uVar1 = PackedFloatingReciprocalIter2(uVar1,uVar2);
  uVar2 = PackedFloatingMUL((uVar6 ^ _DAT_005ef1d0) & uVar5,uVar1);
  uVar9 = PackedFloatingMUL((uVar13 ^ _DAT_005ef118) & uVar5,uVar1);
  uVar8 = CONCAT44((int)local_a8,(int)(local_a8 >> 0x20));
  uVar10 = CONCAT44((int)local_a0,(int)(local_a0 >> 0x20));
  uVar5 = PackedFloatingMUL(local_a8,uVar9);
  uVar1 = PackedFloatingMUL(local_a0,uVar2);
  uVar7 = PackedFloatingMUL(uVar10 ^ _DAT_005ef118,uVar2);
  uVar4 = PackedFloatingMUL(uVar8,uVar9);
  uVar1 = PackedFloatingADD(uVar5 ^ _DAT_005ef118,uVar1);
  uVar4 = PackedFloatingSUB(uVar4,uVar7);
  uVar14 = PackedFloatingMUL(uVar10,uVar9);
  uVar4 = PackedFloatingAccumulate(uVar4,uVar1);
  uVar11 = PackedFloatingMUL(uVar8 ^ _DAT_005ef118,uVar2);
  uVar1 = PackedFloatingMUL(local_a8,uVar2);
  uVar7 = PackedFloatingMUL(local_a0 ^ _DAT_005ef118,uVar9);
  uVar11 = PackedFloatingADD(uVar11,uVar14);
  uVar1 = PackedFloatingSUB(uVar7,uVar1);
  uVar8 = PackedFloatingAccumulate(uVar11,uVar1);
  uVar10 = CONCAT44((int)local_88,(int)(local_88 >> 0x20));
  uVar12 = CONCAT44((int)local_80,(int)(local_80 >> 0x20));
  uVar5 = PackedFloatingMUL(local_88,uVar9);
  uVar1 = PackedFloatingMUL(local_80,uVar2);
  uVar11 = PackedFloatingMUL(uVar12 ^ _DAT_005ef118,uVar2);
  uVar7 = PackedFloatingMUL(uVar10,uVar9);
  uVar1 = PackedFloatingADD(uVar5 ^ _DAT_005ef118,uVar1);
  uVar7 = PackedFloatingSUB(uVar7,uVar11);
  uVar14 = PackedFloatingMUL(uVar12,uVar9);
  uVar7 = PackedFloatingAccumulate(uVar7,uVar1);
  uVar11 = PackedFloatingMUL(uVar10 ^ _DAT_005ef118,uVar2);
  uVar1 = PackedFloatingMUL(local_88,uVar2);
  uVar2 = PackedFloatingMUL(local_80 ^ _DAT_005ef118,uVar9);
  uVar9 = PackedFloatingADD(uVar11,uVar14);
  uVar1 = PackedFloatingSUB(uVar2,uVar1);
  uVar5 = PackedFloatingAccumulate(uVar9,uVar1);
  uVar3 = (undefined4)(uVar8 >> 0x20);
  uVar2 = PackedFloatingCompareGE(CONCAT44(uVar3,uVar3),_DAT_005ef188);
  uVar1 = uVar7;
  if ((int)uVar2 == 0) {
    CFastVB__FastAcosApprox_Scalar();
    CFastVB__Helper_005b8da0();
    uVar2 = PackedFloatingCompareGE(extraout_MM0 & _DAT_005ef140,DAT_005ef148);
    if ((int)uVar2 != 0) {
      uVar1 = FloatingReciprocalAprox(uVar1,extraout_MM0);
      uVar2 = PackedFloatingReciprocalIter1(extraout_MM0,uVar1);
      uVar2 = PackedFloatingReciprocalIter2(uVar2,uVar1);
      uVar2 = PackedFloatingMUL(CONCAT44(extraout_MM0_Da,extraout_MM0_Da),uVar2);
      uVar4 = PackedFloatingMUL(uVar4,uVar2);
      uVar8 = PackedFloatingMUL(uVar8,uVar2);
    }
  }
  uVar8 = uVar8 & _DAT_005ef150;
  uVar3 = (undefined4)(uVar5 >> 0x20);
  uVar2 = PackedFloatingCompareGE(CONCAT44(uVar3,uVar3),_DAT_005ef188);
  if ((int)uVar2 == 0) {
    CFastVB__FastAcosApprox_Scalar();
    CFastVB__Helper_005b8da0();
    uVar2 = PackedFloatingCompareGE(extraout_MM0_00 & _DAT_005ef140,DAT_005ef148);
    if ((int)uVar2 != 0) {
      uVar2 = FloatingReciprocalAprox(uVar1,extraout_MM0_00);
      uVar1 = PackedFloatingReciprocalIter1(extraout_MM0_00,uVar2);
      uVar1 = PackedFloatingReciprocalIter2(uVar1,uVar2);
      uVar1 = PackedFloatingMUL(CONCAT44(extraout_MM0_Da_00,extraout_MM0_Da_00),uVar1);
      uVar7 = PackedFloatingMUL(uVar7,uVar1);
      uVar5 = PackedFloatingMUL(uVar5,uVar1);
    }
  }
  uVar1 = PackedFloatingADD(uVar4,uVar7);
  uVar2 = PackedFloatingADD(uVar8,uVar5 & _DAT_005ef150);
  uVar1 = PackedFloatingMUL(uVar1,_DAT_005f4350);
  uVar8 = PackedFloatingMUL(uVar2,_DAT_005f4350);
  uVar2 = PackedFloatingMUL(uVar1,uVar1);
  uVar4 = PackedFloatingMUL(uVar8 & 0xffffffff,uVar8 & 0xffffffff);
  uVar2 = PackedFloatingADD(uVar2,uVar4);
  uVar2 = PackedFloatingAccumulate(uVar2,uVar2);
  uVar4 = PackedFloatingReciprocalSQRAprox(uVar4,uVar2);
  uVar7 = PackedFloatingMUL(uVar4,uVar4);
  uVar7 = PackedFloatingReciprocalSQRIter1(uVar7,uVar2);
  uVar4 = PackedFloatingReciprocalIter2(uVar7,uVar4);
  PackedFloatingMUL(uVar2,uVar4);
  CFastVB__FastTrigPairApprox_Scalar();
  uVar5 = PackedFloatingCompareGE(extraout_MM0_01 & _DAT_005ef138,DAT_005ef148);
  uVar3 = (undefined4)(extraout_MM0_01 >> 0x20);
  uVar2 = PackedFloatingMUL(CONCAT44(uVar3,uVar3),CONCAT44(unaff_ESI,(int)uVar4));
  local_20 = (undefined4)uVar8;
  if ((uVar5 & 0x100000000) != 0) {
    uVar2 = CONCAT44((int)uVar2,(int)uVar2);
    uVar4 = PackedFloatingMUL(uVar8 & 0xffffffff,uVar2);
    local_20 = (undefined4)uVar4;
    uVar1 = PackedFloatingMUL(uVar1,uVar2);
  }
  uVar8 = CONCAT44((int)extraout_MM0_01,local_20);
  uVar10 = CONCAT44((int)uVar1,(int)((ulonglong)uVar1 >> 0x20));
  uVar12 = CONCAT44(local_20,(int)extraout_MM0_01);
  uVar5 = PackedFloatingMUL(uVar1,uVar13);
  uVar2 = PackedFloatingMUL(uVar8,uVar6);
  uVar7 = PackedFloatingMUL(uVar12 ^ _DAT_005ef118,uVar6);
  uVar4 = PackedFloatingMUL(uVar10,uVar13);
  uVar2 = PackedFloatingADD(uVar5 ^ _DAT_005ef118,uVar2);
  uVar4 = PackedFloatingSUB(uVar4,uVar7);
  uVar9 = PackedFloatingMUL(uVar12,uVar13);
  uVar4 = PackedFloatingAccumulate(uVar4,uVar2);
  uVar7 = PackedFloatingMUL(uVar10 ^ _DAT_005ef118,uVar6);
  uVar8 = uVar8 ^ _DAT_005ef118;
  uVar1 = PackedFloatingMUL(uVar1,uVar6);
  *in_stack_00000004 = uVar4;
  uVar2 = PackedFloatingMUL(uVar8,uVar13);
  uVar7 = PackedFloatingADD(uVar7,uVar9);
  uVar1 = PackedFloatingSUB(uVar2,uVar1);
  uVar1 = PackedFloatingAccumulate(uVar7,uVar1);
  in_stack_00000004[1] = uVar1;
  uVar1 = PackedFloatingMUL(local_88,local_88);
  uVar2 = PackedFloatingMUL(local_80,local_80);
  uVar1 = PackedFloatingADD(uVar1,uVar2);
  uVar1 = PackedFloatingAccumulate(uVar1,uVar1);
  uVar2 = FloatingReciprocalAprox(uVar4,uVar1);
  uVar5 = PackedFloatingCompareGT(uVar1,_PTR_DAT_005ef170);
  uVar1 = PackedFloatingReciprocalIter1(uVar1,uVar2);
  uVar1 = PackedFloatingReciprocalIter2(uVar1,uVar2);
  uVar2 = PackedFloatingMUL((local_88 ^ _DAT_005ef1d0) & uVar5,uVar1);
  uVar9 = PackedFloatingMUL((local_80 ^ _DAT_005ef118) & uVar5,uVar1);
  uVar8 = CONCAT44((int)uVar6,(int)(uVar6 >> 0x20));
  uVar10 = CONCAT44((int)uVar13,(int)(uVar13 >> 0x20));
  uVar5 = PackedFloatingMUL(uVar6,uVar9);
  uVar1 = PackedFloatingMUL(uVar13,uVar2);
  uVar7 = PackedFloatingMUL(uVar10 ^ _DAT_005ef118,uVar2);
  uVar4 = PackedFloatingMUL(uVar8,uVar9);
  uVar1 = PackedFloatingADD(uVar5 ^ _DAT_005ef118,uVar1);
  uVar4 = PackedFloatingSUB(uVar4,uVar7);
  uVar14 = PackedFloatingMUL(uVar10,uVar9);
  uVar4 = PackedFloatingAccumulate(uVar4,uVar1);
  uVar11 = PackedFloatingMUL(uVar8 ^ _DAT_005ef118,uVar2);
  uVar1 = PackedFloatingMUL(uVar6,uVar2);
  uVar7 = PackedFloatingMUL(uVar13 ^ _DAT_005ef118,uVar9);
  uVar11 = PackedFloatingADD(uVar11,uVar14);
  uVar1 = PackedFloatingSUB(uVar7,uVar1);
  uVar13 = PackedFloatingAccumulate(uVar11,uVar1);
  uVar5 = CONCAT44((int)local_78,(int)(local_78 >> 0x20));
  uVar8 = CONCAT44((int)local_70,(int)(local_70 >> 0x20));
  uVar6 = PackedFloatingMUL(local_78,uVar9);
  uVar1 = PackedFloatingMUL(local_70,uVar2);
  uVar11 = PackedFloatingMUL(uVar8 ^ _DAT_005ef118,uVar2);
  uVar7 = PackedFloatingMUL(uVar5,uVar9);
  uVar1 = PackedFloatingADD(uVar6 ^ _DAT_005ef118,uVar1);
  uVar7 = PackedFloatingSUB(uVar7,uVar11);
  uVar14 = PackedFloatingMUL(uVar8,uVar9);
  uVar7 = PackedFloatingAccumulate(uVar7,uVar1);
  uVar11 = PackedFloatingMUL(uVar5 ^ _DAT_005ef118,uVar2);
  uVar1 = PackedFloatingMUL(local_78,uVar2);
  uVar2 = PackedFloatingMUL(local_70 ^ _DAT_005ef118,uVar9);
  uVar9 = PackedFloatingADD(uVar11,uVar14);
  uVar1 = PackedFloatingSUB(uVar2,uVar1);
  uVar6 = PackedFloatingAccumulate(uVar9,uVar1);
  uVar3 = (undefined4)(uVar13 >> 0x20);
  uVar2 = PackedFloatingCompareGE(CONCAT44(uVar3,uVar3),_DAT_005ef188);
  uVar1 = uVar7;
  if ((int)uVar2 == 0) {
    CFastVB__FastAcosApprox_Scalar();
    CFastVB__Helper_005b8da0();
    uVar2 = PackedFloatingCompareGE(extraout_MM0_02 & _DAT_005ef140,DAT_005ef148);
    if ((int)uVar2 != 0) {
      uVar1 = FloatingReciprocalAprox(uVar1,extraout_MM0_02);
      uVar2 = PackedFloatingReciprocalIter1(extraout_MM0_02,uVar1);
      uVar2 = PackedFloatingReciprocalIter2(uVar2,uVar1);
      uVar2 = PackedFloatingMUL(CONCAT44(extraout_MM0_Da_01,extraout_MM0_Da_01),uVar2);
      uVar4 = PackedFloatingMUL(uVar4,uVar2);
      uVar13 = PackedFloatingMUL(uVar13,uVar2);
    }
  }
  uVar13 = uVar13 & _DAT_005ef150;
  uVar3 = (undefined4)(uVar6 >> 0x20);
  uVar2 = PackedFloatingCompareGE(CONCAT44(uVar3,uVar3),_DAT_005ef188);
  if ((int)uVar2 == 0) {
    CFastVB__FastAcosApprox_Scalar();
    CFastVB__Helper_005b8da0();
    uVar2 = PackedFloatingCompareGE(extraout_MM0_03 & _DAT_005ef140,DAT_005ef148);
    if ((int)uVar2 != 0) {
      uVar2 = FloatingReciprocalAprox(uVar1,extraout_MM0_03);
      uVar1 = PackedFloatingReciprocalIter1(extraout_MM0_03,uVar2);
      uVar1 = PackedFloatingReciprocalIter2(uVar1,uVar2);
      uVar1 = PackedFloatingMUL(CONCAT44(extraout_MM0_Da_02,extraout_MM0_Da_02),uVar1);
      uVar7 = PackedFloatingMUL(uVar7,uVar1);
      uVar6 = PackedFloatingMUL(uVar6,uVar1);
    }
  }
  uVar1 = PackedFloatingADD(uVar4,uVar7);
  uVar2 = PackedFloatingADD(uVar13,uVar6 & _DAT_005ef150);
  uVar1 = PackedFloatingMUL(uVar1,_DAT_005f4350);
  uVar13 = PackedFloatingMUL(uVar2,_DAT_005f4350);
  uVar2 = PackedFloatingMUL(uVar1,uVar1);
  uVar4 = PackedFloatingMUL(uVar13 & 0xffffffff,uVar13 & 0xffffffff);
  uVar2 = PackedFloatingADD(uVar2,uVar4);
  uVar2 = PackedFloatingAccumulate(uVar2,uVar2);
  uVar4 = PackedFloatingReciprocalSQRAprox(uVar4,uVar2);
  uVar7 = PackedFloatingMUL(uVar4,uVar4);
  uVar7 = PackedFloatingReciprocalSQRIter1(uVar7,uVar2);
  uVar4 = PackedFloatingReciprocalIter2(uVar7,uVar4);
  PackedFloatingMUL(uVar2,uVar4);
  CFastVB__FastTrigPairApprox_Scalar();
  uVar6 = PackedFloatingCompareGE(extraout_MM0_04 & _DAT_005ef138,DAT_005ef148);
  uVar3 = (undefined4)(extraout_MM0_04 >> 0x20);
  uVar2 = PackedFloatingMUL(CONCAT44(uVar3,uVar3),CONCAT44(unaff_ESI,(int)uVar4));
  local_20 = (undefined4)uVar13;
  if ((uVar6 & 0x100000000) != 0) {
    uVar2 = CONCAT44((int)uVar2,(int)uVar2);
    uVar4 = PackedFloatingMUL(uVar13 & 0xffffffff,uVar2);
    local_20 = (undefined4)uVar4;
    uVar1 = PackedFloatingMUL(uVar1,uVar2);
  }
  uVar13 = CONCAT44((int)extraout_MM0_04,local_20);
  uVar5 = CONCAT44((int)uVar1,(int)((ulonglong)uVar1 >> 0x20));
  uVar8 = CONCAT44(local_20,(int)extraout_MM0_04);
  uVar6 = PackedFloatingMUL(uVar1,local_80);
  uVar2 = PackedFloatingMUL(uVar13,local_88);
  uVar7 = PackedFloatingMUL(uVar8 ^ _DAT_005ef118,local_88);
  uVar4 = PackedFloatingMUL(uVar5,local_80);
  uVar2 = PackedFloatingADD(uVar6 ^ _DAT_005ef118,uVar2);
  uVar4 = PackedFloatingSUB(uVar4,uVar7);
  uVar7 = PackedFloatingMUL(uVar8,local_80);
  uVar2 = PackedFloatingAccumulate(uVar4,uVar2);
  uVar4 = PackedFloatingMUL(uVar5 ^ _DAT_005ef118,local_88);
  uVar13 = uVar13 ^ _DAT_005ef118;
  uVar1 = PackedFloatingMUL(uVar1,local_88);
  *in_stack_00000008 = uVar2;
  uVar2 = PackedFloatingMUL(uVar13,local_80);
  uVar4 = PackedFloatingADD(uVar4,uVar7);
  uVar1 = PackedFloatingSUB(uVar2,uVar1);
  uVar1 = PackedFloatingAccumulate(uVar4,uVar1);
  in_stack_00000008[1] = uVar1;
  *in_stack_0000000c = local_88;
  in_stack_0000000c[1] = local_80;
  FastExitMediaState();
  return (int)in_stack_0000000c;
}
