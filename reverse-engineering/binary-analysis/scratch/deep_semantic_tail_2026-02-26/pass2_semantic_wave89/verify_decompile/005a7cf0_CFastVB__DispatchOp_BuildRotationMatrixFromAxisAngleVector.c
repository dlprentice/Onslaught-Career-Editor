/* address: 0x005a7cf0 */
/* name: CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector */
/* signature: void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector(void * param_1, void * param_2) */


void CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector(void *param_1,void *param_2)

{
  undefined8 extraout_MM0;
  undefined8 uVar1;
  undefined8 uVar2;
  ulonglong uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  ulonglong uVar7;
  undefined8 uVar8;
  undefined4 uVar9;
  undefined8 local_20;
  uint local_18;

  local_20 = *(undefined8 *)param_2;
  local_18 = *(uint *)((int)param_2 + 8);
  CFastVB__Helper_005a9a5f(&local_20,&local_20);
  CFastVB__Unk_005b8ca0();
  uVar1 = PackedFloatingSUBR(extraout_MM0,CONCAT44(DAT_005ef104,DAT_005ef100));
  uVar9 = (undefined4)((ulonglong)extraout_MM0 >> 0x20);
  uVar3 = (ulonglong)local_18;
  uVar4 = PackedFloatingMUL(CONCAT44(local_18,local_18),local_20);
  uVar1 = CONCAT44((int)uVar1,(int)uVar1);
  uVar2 = PackedFloatingMUL(CONCAT44(local_18,(int)((ulonglong)local_20 >> 0x20)),local_20);
  uVar8 = CONCAT44((int)extraout_MM0,(int)extraout_MM0);
  uVar2 = PackedFloatingMUL(uVar2,uVar1);
  uVar4 = PackedFloatingMUL(uVar4,uVar1);
  uVar5 = PackedFloatingMUL(local_20,local_20);
  uVar6 = PackedFloatingMUL(uVar3,uVar3);
  uVar5 = PackedFloatingMUL(uVar5,uVar1);
  uVar1 = PackedFloatingMUL(uVar6,uVar1);
  uVar5 = PackedFloatingADD(uVar5,uVar8);
  uVar7 = PackedFloatingADD(uVar1,uVar8);
  uVar1 = CONCAT44(uVar9,uVar9);
  uVar8 = PackedFloatingMUL(local_20,uVar1);
  uVar1 = PackedFloatingMUL(uVar3,uVar1);
  *(undefined8 *)((int)param_1 + 0x30) = 0;
  uVar6 = CONCAT44((int)uVar8,(int)uVar1);
  uVar9 = (undefined4)((ulonglong)uVar8 >> 0x20);
  uVar8 = CONCAT44(uVar9,uVar9);
  *(ulonglong *)((int)param_1 + 0x28) = uVar7 & 0xffffffff;
  uVar1 = PackedFloatingSUB(uVar2,uVar6);
  uVar7 = PackedFloatingADD(uVar2,uVar6);
  uVar3 = PackedFloatingSUB(uVar4,uVar8);
  *(ulonglong *)param_1 = CONCAT44((int)uVar7,(int)uVar5);
  *(ulonglong *)((int)param_1 + 8) = uVar3 & 0xffffffff;
  uVar3 = (ulonglong)DAT_005ef104;
  uVar8 = PackedFloatingADD(CONCAT44((int)uVar4,(int)uVar4),uVar8);
  *(ulonglong *)((int)param_1 + 0x18) = uVar7 >> 0x20;
  *(ulonglong *)((int)param_1 + 0x38) = uVar3 << 0x20;
  *(ulonglong *)((int)param_1 + 0x20) =
       CONCAT44((int)((ulonglong)uVar1 >> 0x20),(int)((ulonglong)uVar8 >> 0x20));
  *(ulonglong *)((int)param_1 + 0x10) = CONCAT44((int)((ulonglong)uVar5 >> 0x20),(int)uVar1);
  FastExitMediaState();
  return;
}
