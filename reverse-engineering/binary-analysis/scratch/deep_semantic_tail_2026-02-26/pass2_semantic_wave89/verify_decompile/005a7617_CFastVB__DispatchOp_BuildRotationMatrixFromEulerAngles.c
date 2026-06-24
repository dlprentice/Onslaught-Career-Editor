/* address: 0x005a7617 */
/* name: CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles */
/* signature: void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles(void * param_1, int param_2, int param_3) */


void CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles(void *param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  undefined8 extraout_MM0;
  undefined8 extraout_MM0_00;
  undefined8 extraout_MM0_01;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  ulonglong uVar5;
  undefined4 uVar8;
  undefined8 uVar6;
  ulonglong uVar7;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined4 uVar11;
  undefined8 uVar12;
  undefined8 in_stack_00000010;

  PackedFloatingMUL(DAT_005ef190,in_stack_00000010);
  PackedFloatingMUL(DAT_005ef190,CONCAT44(param_3,param_2));
  CFastVB__Unk_005b8ca0();
  CFastVB__Unk_005b8ca0();
  CFastVB__Unk_005b8ca0();
  uVar1 = (undefined4)extraout_MM0_01;
  uVar8 = (undefined4)((ulonglong)extraout_MM0_01 >> 0x20);
  uVar4 = CONCAT44((int)extraout_MM0_00,(int)extraout_MM0_00);
  uVar11 = (undefined4)((ulonglong)extraout_MM0_00 >> 0x20);
  uVar9 = CONCAT44(uVar11,uVar11);
  uVar2 = PackedFloatingMUL(CONCAT44(uVar1,uVar1) ^ DAT_005ef120,uVar9);
  uVar3 = PackedFloatingMUL(CONCAT44(uVar1,uVar1),uVar4);
  uVar6 = PackedFloatingMUL(CONCAT44(uVar8,uVar8),uVar4);
  uVar9 = PackedFloatingMUL(CONCAT44(uVar8,uVar8) ^ DAT_005ef120 >> 0x20,uVar9);
  uVar12 = CONCAT44((int)extraout_MM0,(int)((ulonglong)extraout_MM0 >> 0x20));
  uVar2 = PackedFloatingMUL(uVar2,extraout_MM0);
  uVar4 = PackedFloatingMUL(uVar3,uVar12);
  uVar3 = PackedFloatingMUL(uVar6,uVar12);
  uVar6 = PackedFloatingMUL(uVar9,extraout_MM0);
  uVar2 = PackedFloatingADD(uVar2,uVar3);
  uVar6 = PackedFloatingADD(uVar4,uVar6);
  uVar4 = PackedFloatingADD(uVar2,uVar2);
  uVar3 = PackedFloatingADD(uVar6,uVar6);
  uVar1 = (undefined4)((ulonglong)uVar2 >> 0x20);
  uVar8 = (undefined4)((ulonglong)uVar6 >> 0x20);
  uVar12 = CONCAT44(uVar8,uVar8);
  uVar9 = PackedFloatingMUL(uVar2,uVar4);
  uVar2 = CONCAT44((int)uVar4,(int)uVar3);
  uVar10 = PackedFloatingMUL(uVar4,uVar12);
  uVar6 = PackedFloatingMUL(CONCAT44((int)uVar6,(int)uVar6),uVar2);
  uVar4 = PackedFloatingMUL(uVar2,CONCAT44(uVar1,uVar1));
  uVar2 = PackedFloatingMUL(uVar2,uVar12);
  uVar3 = CONCAT44((int)((ulonglong)uVar6 >> 0x20),(int)((ulonglong)uVar4 >> 0x20));
  *(undefined8 *)((int)param_1 + 0x30) = 0;
  uVar12 = PackedFloatingADD(CONCAT44((int)uVar6,(int)uVar6),uVar9);
  uVar6 = PackedFloatingAccumulate(uVar9,uVar9);
  uVar2 = CONCAT44((int)((ulonglong)uVar10 >> 0x20),(int)uVar2);
  uVar5 = PackedFloatingSUBR(uVar6,CONCAT44(DAT_005ef104,DAT_005ef100));
  uVar9 = PackedFloatingSUBR(uVar12,CONCAT44(DAT_005ef104,DAT_005ef100));
  uVar6 = PackedFloatingADD(uVar3,uVar2);
  *(ulonglong *)((int)param_1 + 0x28) = uVar5 & 0xffffffff;
  uVar7 = PackedFloatingSUB(uVar3,uVar2);
  uVar5 = PackedFloatingADD(uVar4,uVar10);
  uVar2 = PackedFloatingSUB(uVar4,uVar10);
  *(ulonglong *)((int)param_1 + 0x18) = uVar5 & 0xffffffff;
  uVar5 = (ulonglong)DAT_005ef100;
  *(ulonglong *)((int)param_1 + 8) = uVar7 >> 0x20;
  *(ulonglong *)((int)param_1 + 0x10) = CONCAT44((int)uVar9,(int)uVar7);
  *(ulonglong *)param_1 = CONCAT44((int)uVar6,(int)((ulonglong)uVar9 >> 0x20));
  *(ulonglong *)((int)param_1 + 0x20) = CONCAT44((int)uVar2,(int)((ulonglong)uVar6 >> 0x20));
  *(ulonglong *)((int)param_1 + 0x38) = uVar5 << 0x20;
  FastExitMediaState();
  return;
}
